"""MinerU RAG 本地试用页：检索问答、引用展开、反馈回流与可选 OTLP 观测。"""

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace

from rag.config import RAGConfig
from rag.observability import RAGObservability
from rag.qa import QAPipeline
from rag.retrieval import HybridRetriever
from rag.store import ChunkIndex

PAGE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MinerU 金融文献知识库试用</title>
<style>
:root{font-family:Inter,"Segoe UI","Microsoft YaHei",sans-serif;color:#172033;background:#f5f7fb}*{box-sizing:border-box}body{margin:0}.wrap{max-width:1050px;margin:0 auto;padding:28px 18px 60px}h1{margin:0 0 8px;font-size:28px}p{line-height:1.65}.muted{color:#687386}.card{background:#fff;border:1px solid #e4e9f1;border-radius:14px;padding:20px;margin:16px 0;box-shadow:0 5px 20px #1b365d0a}textarea{width:100%;min-height:105px;padding:14px;border:1px solid #cbd5e3;border-radius:10px;font:inherit;font-size:16px}button{border:0;border-radius:9px;padding:10px 16px;background:#2255cc;color:white;cursor:pointer;font:inherit}button.secondary{background:#e9eef7;color:#26364d}button:disabled{opacity:.55}#answer{white-space:pre-wrap;line-height:1.75}.source{border-left:4px solid #b9cbe9;padding:10px 12px;margin:10px 0;background:#f8faff}.source b{display:block}.source small{color:#667085}.tasks li{margin:7px 0}.error{color:#b42318}.feedback button{margin-right:8px}select,input{max-width:100%;padding:9px;border:1px solid #cbd5e3;border-radius:8px;font:inherit}select{width:100%;margin:8px 0 12px}#comment{width:100%;min-height:65px}#status{font-size:14px;margin-left:10px}details{margin-top:10px}code{background:#eef2f7;padding:2px 5px;border-radius:4px}</style></head>
<body><main class="wrap">
<h1>金融文献知识库试用</h1>
<p class="muted">检索真实金融论文、展开来源、标记问题。只有本机运行的请求会进入观测日志。</p>
<section class="card"><b>建议试用任务</b><ul class="tasks">
<li>监管沙盒试点如何影响实体企业创新？</li><li>金融科技通过什么机制影响银行风险承担？</li><li>社交媒体情绪能否预测企业并购撤回？（跨语言失败案例）</li><li>这套资料能否证明金融科技一定降低银行风险？（无答案边界）</li></ul></section>
<section class="card"><label for="question"><b>你的问题</b></label><textarea id="question" placeholder="输入一个金融文献问题…">监管沙盒试点如何影响实体企业创新？</textarea>
<div style="margin-top:12px"><button id="ask">检索并回答</button><span id="status"></span></div></section>
<section id="result" class="card" hidden><h2>回答</h2><div id="answer"></div><p id="mode" class="muted"></p><details id="prompt-box" hidden><summary>查看发送给模型的资料与提示词</summary><pre id="prompt" style="white-space:pre-wrap"></pre></details>
<h3>来源与证据</h3><div id="sources"></div>
<div class="feedback"><b>这次回答是否有帮助？</b><div style="margin:10px 0"><button class="secondary" data-rating="up">有帮助</button><button class="secondary" data-rating="down">没有帮助</button><button class="secondary" data-rating="error">回答有误</button></div>
<label for="error-type">错误类型</label><select id="error-type"><option value="">无</option><option value="retrieval">检索不到正确资料</option><option value="citation">引用不支持结论</option><option value="answer">答案本身错误</option><option value="refusal">应该拒答却回答了</option><option value="other">其他</option></select>
<label for="comment">问题说明（可选）</label><textarea id="comment" placeholder="请描述实际结果与预期结果，不要填写个人信息"></textarea><div style="margin-top:10px"><button id="feedback-submit">提交反馈</button><span id="feedback-status"></span></div></div></section>
</main><script>
let traceId = null;
let selectedRating = 'error';
const $ = id => document.getElementById(id);
async function post(url, payload) {
  const response = await fetch(url, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || '请求失败');
  return data;
}
$('ask').onclick = async () => {
  const question = $('question').value.trim();
  if (!question) return;
  $('ask').disabled = true; $('status').textContent = '正在检索与生成…';
  try {
    const data = await post('/api/ask', {question, top_k:5});
    traceId = data.trace_id; $('result').hidden = false;
    $('answer').textContent = data.answer || data.prompt || '没有生成回答';
    $('mode').textContent = data.demo_mode ? '当前为功能演示回答，不代表模型真实效果。' : (data.answer ? '由当前配置的模型生成。' : '当前只展示检索和提示词，未调用模型。');
    $('prompt-box').hidden = !data.prompt; $('prompt').textContent = data.prompt || '';
    $('sources').replaceChildren();
    data.sources.forEach((source, index) => {
      const block = document.createElement('div'); block.className = 'source';
      const title = document.createElement('b'); title.textContent = `[${index+1}] ${source.doc_name}`;
      const meta = document.createElement('small'); meta.textContent = ` ${source.quality || ''} · ${source.sources} · ${source.score}`;
      const text = document.createElement('p'); text.textContent = source.excerpt;
      block.append(title, meta, text); $('sources').append(block);
    });
    $('status').textContent = `完成 · ${data.latency_ms} ms · trace ${traceId}`;
  } catch (error) { $('status').textContent = error.message; $('status').className = 'error'; }
  finally { $('ask').disabled = false; }
};
document.querySelectorAll('[data-rating]').forEach(button => button.onclick = () => {
  selectedRating = button.dataset.rating;
  document.querySelectorAll('[data-rating]').forEach(other => other.style.outline = '');
  button.style.outline = '2px solid #2255cc';
});
$('feedback-submit').onclick = async () => {
  if (!traceId) { $('feedback-status').textContent = '请先完成一次提问'; return; }
  const rating = selectedRating;
  try {
    const data = await post('/api/feedback', {trace_id:traceId, rating, error_type:$('error-type').value, comment:$('comment').value});
    $('feedback-status').textContent = `反馈已记录：${data.feedback_id}`;
  } catch (error) { $('feedback-status').textContent = error.message; }
};
</script></body></html>"""


class DemoLLMClient:
    def __init__(self):
        self.config = SimpleNamespace(llm_model="demo-grounded-client")

    def chat(self, prompt):
        return "这是用于功能验收的演示回答，不是模型生成结果。请以下方论文来源为准，检查检索、引用与反馈流程。"


def make_handler(pipeline, observability, demo, with_llm):
    class Handler(BaseHTTPRequestHandler):
        def _json(self, payload, status=200):
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _payload(self):
            length = int(self.headers.get("Content-Length", "0"))
            if length > 64 * 1024:
                raise ValueError("请求过大")
            return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

        def do_GET(self):
            if self.path == "/api/health":
                self._json({
                    "status": "ok",
                    "chunks": len(pipeline.retriever.chunks),
                    "demo_mode": demo,
                    "llm_enabled": with_llm,
                    "otlp_enabled": bool(observability.otlp_endpoint),
                })
                return
            if self.path not in ("/", "/index.html"):
                self._json({"error": "not found"}, 404)
                return
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            try:
                payload = self._payload()
                if self.path == "/api/ask":
                    question = str(payload.get("question", "")).strip()
                    if not question:
                        self._json({"error": "question 不能为空"}, 400)
                        return
                    if len(question) > 2000:
                        self._json({"error": "question 不能超过 2000 字"}, 400)
                        return
                    client = DemoLLMClient() if demo else None
                    generate = demo or with_llm
                    result = pipeline.ask(
                        question,
                        top_k=payload.get("top_k", 5),
                        with_llm=generate,
                        llm_client=client,
                        observability=observability,
                    )
                    self._json({
                        "trace_id": result.trace_id,
                        "question": result.question,
                        "answer": result.answer,
                        "prompt": result.prompt if not result.answer else None,
                        "sources": result.sources,
                        "demo_mode": demo,
                        "latency_ms": result.latency_ms,
                    })
                elif self.path == "/api/feedback":
                    trace_id = str(payload.get("trace_id", "")).strip()
                    rating = str(payload.get("rating", "")).strip()
                    if not trace_id or rating not in {"up", "down", "error"}:
                        self._json({"error": "trace_id 或 rating 不合法"}, 400)
                        return
                    comment = str(payload.get("comment", ""))[:1000]
                    error_type = str(payload.get("error_type", ""))[:50]
                    feedback_id = observability.feedback(trace_id, rating, error_type, comment)
                    self._json({"success": True, "feedback_id": feedback_id})
                else:
                    self._json({"error": "not found"}, 404)
            except (ValueError, json.JSONDecodeError) as exc:
                self._json({"error": str(exc)}, 400)
            except Exception as exc:
                self._json({"error": str(exc)}, 500)

        def log_message(self, *_):
            pass

    return Handler


def main():
    parser = argparse.ArgumentParser(description="MinerU RAG 本地试用页")
    parser.add_argument("--host", default="127.0.0.1", help="仅监听本机回环地址")
    parser.add_argument("--port", type=int, default=7860)
    parser.add_argument("--demo", action="store_true", help="使用明确标注的演示回答，不调用模型")
    parser.add_argument("--with-llm", action="store_true", help="调用真实模型生成回答")
    parser.add_argument("--no-observe", action="store_true", help="关闭本地 JSONL 和 OTLP 观测")
    parser.add_argument("--otlp", default=None, help="OTLP endpoint，例如 http://127.0.0.1:6006/v1/traces")
    args = parser.parse_args()
    if args.host != "127.0.0.1":
        raise ValueError("试用页仅允许监听 127.0.0.1；如需共享请自行增加鉴权与反向代理")

    config = RAGConfig.from_env()
    index = ChunkIndex(config)
    index.load_or_build()
    retriever = HybridRetriever(index, config)
    pipeline = QAPipeline(retriever)
    observability = RAGObservability(enabled=not args.no_observe, otlp_endpoint=args.otlp)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(pipeline, observability, args.demo, args.with_llm))
    print(f"试用页：http://{args.host}:{args.port} | 文档块 {len(retriever.chunks)} | demo={args.demo}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        observability.shutdown()


if __name__ == "__main__":
    main()
