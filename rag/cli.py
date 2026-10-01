"""rag_cli 子命令实现：build / query / ask / eval。"""

import json
import logging
import sys
from pathlib import Path

from .chunking import best_excerpt
from .config import RAGConfig, BASE_DIR
from .evaluate import auto_eval, labeled_eval, write_report
from .qa import QAPipeline
from .retrieval import HybridRetriever
from .store import ChunkIndex

log = logging.getLogger(__name__)


def _make_retriever(config: RAGConfig, build_if_missing=True):
    index = ChunkIndex(config)
    if build_if_missing:
        index.load_or_build()
    else:
        index.load()
    return HybridRetriever(index, config)


# ---------- build ----------
def cmd_build(args):
    config = RAGConfig.from_env()
    if args.backend:
        config.embed_backend = args.backend
    if args.corpus:
        config.corpus_file = Path(args.corpus)

    index = ChunkIndex(config)
    if index.exists() and not args.force:
        try:
            index.load()
            print(f"索引已存在（{len(index.chunks)} 块，后端 {index.embedder.name}），"
                  f"如需重建请加 --force")
            return 0
        except Exception:
            print("现有索引不可加载，重新构建")

    index.build()
    index.save()
    print(f"[OK] 索引构建完成：{config.index_dir}（{len(index.chunks)} 块）")
    return 0


# ---------- query ----------
def _print_hits(hits, query):
    for rank, hit in enumerate(hits, 1):
        c = hit.chunk
        meta = c.meta or {}
        badge = f"{meta.get('quality')} {meta.get('score')}分" if meta.get("quality") else "-"
        print(f"\n[{rank}] {hit.score:.4f} | 来源:{hit.sources} | 判定:{badge}")
        print(f"    文献: {c.doc_name}"
              + (f"（第{c.index}块，章节:{c.heading}）" if c.heading else f"（第{c.index}块）"))
        print(f"    片段: {best_excerpt(c.text, query)}")


def cmd_query(args):
    config = RAGConfig.from_env()
    config.graph_enabled = not args.no_graph
    retriever = _make_retriever(config)
    hits = retriever.search(args.query, top_k=args.top_k)
    print(f"索引：{len(retriever.chunks)} 块，后端 {retriever.index.embedder.name}，"
          f"图谱扩展：{'开' if config.graph_enabled else '关'}")
    _print_hits(hits, args.query)
    return 0


# ---------- ask ----------
def cmd_ask(args):
    config = RAGConfig.from_env()
    config.graph_enabled = not args.no_graph
    retriever = _make_retriever(config)
    pipeline = QAPipeline(retriever)

    result = pipeline.ask(args.question, top_k=args.top_k, with_llm=args.with_llm)

    if args.with_llm:
        print("\n===== 回答 =====\n")
        print(result.answer or "（未生成答案）")
    else:
        print("（未调用大模型：以下为将发送给 LLM 的提示词，"
              "确认无误后加 --with-llm 真正生成）\n")
        print(result.prompt)

    print("\n===== 引用来源 =====")
    for n, s in enumerate(result.sources, 1):
        print(f"[{n}] {s['doc_name']} | 判定:{s['quality']} "
              f"| 召回方式:{s['sources']} | 融合分:{s['score']}")
    return 0


# ---------- eval ----------
def cmd_eval(args):
    config = RAGConfig.from_env()
    config.graph_enabled = not args.no_graph
    retriever = _make_retriever(config)
    backend = retriever.index.embedder.name

    auto = labeled = None
    if args.auto:
        print("运行自动评测（下限体检）…")
        auto = auto_eval(retriever, sample=args.sample,
                         use_graph=config.graph_enabled)
        print(f"  Top-{auto.k} 命中 {auto.top_k}/{auto.n}")

    if args.questions:
        print(f"运行人工标注评测：{args.questions}")
        labeled = labeled_eval(args.questions, retriever, top_k=args.top_k,
                               use_graph=config.graph_enabled)
        print(f"  Top-{labeled.k} 命中率 {labeled.hit_rate:.1f}%"
              f"（{labeled.top_k}/{labeled.n}）")

    if auto is None and labeled is None:
        print("请指定 --auto 或 --questions <评测集 json>")
        return 1

    out = Path(args.output) if args.output else BASE_DIR / "reports" / "retrieval_eval.md"
    write_report(out, auto, labeled, backend, config.graph_enabled)
    print(f"[OK] 评测报告已写入：{out}")
    return 0


COMMANDS = {
    "build": cmd_build,
    "query": cmd_query,
    "ask": cmd_ask,
    "eval": cmd_eval,
}


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 1
    _setup_logging(args.verbose)
    return args.func(args)


def _build_parser():
    import argparse
    parser = argparse.ArgumentParser(
        prog="rag_cli",
        description="RAG 检索与问答：build 建索引 / query 检索 / ask 问答 / eval 评测")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("build", help="从语料构建检索索引")
    p.add_argument("--corpus", default=None, help="语料 JSONL（默认 ai_ready_corpus/corpus.jsonl）")
    p.add_argument("--backend", choices=["bge", "tfidf"], default=None,
                   help="向量后端（默认 bge，失败自动降级 tfidf）")
    p.add_argument("--force", action="store_true", help="强制重建")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("query", help="检索相关文献片段")
    p.add_argument("--query", required=True, help="检索词或问题")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--no-graph", action="store_true", help="关闭图谱扩展召回")
    p.set_defaults(func=cmd_query)

    p = sub.add_parser("ask", help="检索并生成带引用的回答（默认只组提示词，不调 LLM）")
    p.add_argument("--question", required=True, help="问题")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--no-graph", action="store_true", help="关闭图谱扩展召回")
    p.add_argument("--with-llm", action="store_true", help="真正调用大模型生成")
    p.set_defaults(func=cmd_ask)

    p = sub.add_parser("eval", help="检索命中率评测")
    p.add_argument("--questions", default=None, help="人工标注评测集 JSON")
    p.add_argument("--auto", action="store_true", help="运行自动体检评测")
    p.add_argument("--sample", type=int, default=20, help="自动评测抽样块数")
    p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--no-graph", action="store_true", help="关闭图谱扩展召回")
    p.add_argument("--output", default=None, help="报告输出路径")
    p.set_defaults(func=cmd_eval)

    parser.add_argument("-v", "--verbose", action="store_true", help="输出调试日志")
    return parser


def _setup_logging(verbose):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr)
