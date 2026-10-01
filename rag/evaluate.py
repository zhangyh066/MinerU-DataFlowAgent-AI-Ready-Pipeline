"""检索效果评测：自动体检 + 人工标注命中率，输出可写进报告的 Markdown。"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from .retrieval import HybridRetriever

log = logging.getLogger(__name__)


@dataclass
class EvalResult:
    n: int
    top1: int
    top_k: int
    k: int
    misses: list = field(default_factory=list)

    @property
    def hit_rate(self):
        return self.top_k / self.n * 100 if self.n else 0.0


def _hit_rank(hits, expect_source=None, expect_keywords=None):
    """在召回结果里找第一个满足「来源 + 关键词」条件的命中，返回名次（从 1 起）。"""
    for rank, hit in enumerate(hits, 1):
        if expect_source and expect_source not in hit.chunk.doc_name:
            continue
        if expect_keywords and not any(k in hit.chunk.text for k in expect_keywords):
            continue
        return rank
    return None


def auto_eval(retriever: HybridRetriever, sample=20, use_graph=None) -> EvalResult:
    """自动评测：取每块中间一段文字反查自身（下限体检，不等于真实效果）。"""
    chunks = retriever.chunks
    n = min(len(chunks), sample)
    top1 = top_k = 0
    for c in chunks[:n]:
        start = min(len(c.text) // 2, max(0, len(c.text) - 60))
        probe = c.text[start:start + 60]
        hits = retriever.search(probe, top_k=3, use_graph=use_graph)
        rank = _hit_rank(hits, expect_source=c.doc_name,
                         expect_keywords=[probe[10:40]])
        if rank == 1:
            top1 += 1
        if rank and rank <= 3:
            top_k += 1
    return EvalResult(n=n, top1=top1, top_k=top_k, k=3)


def labeled_eval(questions_file, retriever: HybridRetriever, top_k=3,
                 use_graph=None) -> EvalResult:
    """人工标注评测：读评测集 JSON，算真实命中率。"""
    with open(questions_file, encoding="utf-8") as f:
        items = json.load(f)

    top1 = hit_k = 0
    misses = []
    for it in items:
        hits = retriever.search(it["question"], top_k=top_k, use_graph=use_graph)
        rank = _hit_rank(hits, expect_source=it.get("expect_source"),
                         expect_keywords=it.get("expect_keywords"))
        if rank == 1:
            top1 += 1
        if rank and rank <= top_k:
            hit_k += 1
        else:
            got = "、".join(h.chunk.doc_name for h in hits) or "（无召回）"
            misses.append((it["question"], it.get("expect_source", "未指定"), got))
    return EvalResult(n=len(items), top1=top1, top_k=hit_k, k=top_k, misses=misses)


def render_report(auto: EvalResult | None, labeled: EvalResult | None,
                  backend: str, use_graph: bool) -> str:
    lines = [
        "# 检索效果评测报告",
        "",
        f"- 向量后端：`{backend}`",
        f"- 图谱扩展：{'开' if use_graph else '关'}",
        "",
        "## 结论怎么读",
        "",
        "自动评测是「下限体检」（拿块内容反查自身），数字必然偏高，只用于发现管道故障；",
        "人工标注评测才是能写进报告的效果数字。判据：Top-K 内存在来自期望文献且含任一关键词的块。",
    ]
    if auto:
        lines += [
            "",
            "## 自动评测（下限体检）",
            "",
            f"- 抽测块数：{auto.n}",
            f"- Top-1 命中：{auto.top1}/{auto.n}",
            f"- Top-{auto.k} 命中：{auto.top_k}/{auto.n}",
        ]
    if labeled:
        lines += [
            "",
            "## 人工标注评测",
            "",
            f"- 题目数：{labeled.n}",
            f"- Top-1 命中：{labeled.top1}/{labeled.n}",
            f"- Top-{labeled.k} 命中率：**{labeled.hit_rate:.1f}%**（{labeled.top_k}/{labeled.n}）",
        ]
        if labeled.misses:
            lines += ["", "### 未命中题目（比命中率本身更有用）", ""]
            for q, src, got in labeled.misses:
                lines.append(f"- 问题：{q}")
                lines.append(f"  - 期望文献：{src}")
                lines.append(f"  - 实际召回：{got}")
    lines += [
        "",
        "## 报告口径备注",
        "",
        "1. 样本量：见各节题目/块数；小样本下数字波动大，扩大语料后应复测。",
        "2. 题目来源：人工对着原文撰写（见 eval_questions.json）。",
        "3. 判据：文件级宽松判定（Top-K 内存在来自期望文献且含任一关键词的块即算命中）。",
    ]
    return "\n".join(lines) + "\n"


def write_report(path, *args, **kwargs):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_report(*args, **kwargs)
    path.write_text(text, encoding="utf-8")
    return path
