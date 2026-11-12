"""问答流水线：检索 -> 组装带引用的提示词 -> （可选）LLM 生成。"""

import logging
from dataclasses import dataclass, field

from .chunking import best_excerpt
from .retrieval import Hit, HybridRetriever

log = logging.getLogger(__name__)

PROMPT_TEMPLATE = """以下是从资料库中检索到的内容（按相关度排序）：

{context}

请只依据上面的资料回答问题。资料中没有提到的，直接回答“资料中未提及”，不要凭印象补充。
回答时在相关论述后用 [编号] 标注出处。

问题：{question}
"""


@dataclass
class Answer:
    question: str
    hits: list[Hit]
    prompt: str
    answer: str | None = None
    sources: list[dict] = field(default_factory=list)
    trace_id: str | None = None
    latency_ms: int | None = None


def format_context(hits: list[Hit], query, width=220) -> str:
    blocks = []
    for n, hit in enumerate(hits, 1):
        c = hit.chunk
        meta = c.meta or {}
        quality = f"（{meta.get('quality')} {meta.get('score')}分）" if meta.get('quality') else ""
        heading = f" 章节：{c.heading}" if c.heading else ""
        label = f"[{n}] 《{c.doc_name}》{quality}{heading}"
        excerpt = best_excerpt(c.text, query, width)
        blocks.append(f"{label}\n{excerpt}")
    return "\n\n".join(blocks)


class QAPipeline:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    def ask(self, question, top_k=None, use_graph=None, with_llm=False,
            llm_client=None, observability=None) -> Answer:
        import time
        from contextlib import nullcontext

        started = time.perf_counter()
        metadata = {
            "embed_backend": self.retriever.index.embedder.name,
            "use_graph": self.retriever.config.graph_enabled if use_graph is None else use_graph,
            "top_k": top_k or self.retriever.config.top_k,
        }
        manager = observability.trace(question, **metadata) if observability else nullcontext(None)
        with manager as trace:
            retrieval_started = time.perf_counter()
            hits = self.retriever.search(question, top_k=top_k, use_graph=use_graph)
            retrieval_ms = round((time.perf_counter() - retrieval_started) * 1000)

            context = format_context(hits, question)
            subgraph = self.retriever.subgraph_text(hits)
            if subgraph:
                context = context + "\n\n" + subgraph
            prompt = PROMPT_TEMPLATE.format(context=context, question=question)

            sources = [{
                "doc_name": h.chunk.doc_name,
                "score": round(h.score, 4),
                "sources": h.sources,
                "quality": (h.chunk.meta or {}).get("quality"),
                "excerpt": best_excerpt(h.chunk.text, question, 120),
            } for h in hits]
            if trace:
                trace.event(
                    "retrieval",
                    latency_ms=retrieval_ms,
                    source_count=len(sources),
                    documents=[source["doc_name"] for source in sources],
                )

            answer = None
            generation_ms = None
            if with_llm:
                from .llm import LLMClient
                client = llm_client or LLMClient()
                log.info("调用 %s 生成答案…", client.config.llm_model)
                generation_started = time.perf_counter()
                answer = client.chat(prompt)
                generation_ms = round((time.perf_counter() - generation_started) * 1000)

            result = Answer(
                question=question,
                hits=hits,
                prompt=prompt,
                answer=answer,
                sources=sources,
                trace_id=trace.trace_id if trace else None,
                latency_ms=round((time.perf_counter() - started) * 1000),
            )
            if trace:
                trace.event(
                    "answer",
                    with_llm=with_llm,
                    generation_ms=generation_ms,
                    prompt_chars=len(prompt),
                    answer_chars=len(answer or ""),
                    latency_ms=round((time.perf_counter() - started) * 1000),
                )
            return result
