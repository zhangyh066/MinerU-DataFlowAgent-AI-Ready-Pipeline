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


def format_context(hits: list[Hit], query, width=220) -> str:
    blocks = []
    for n, hit in enumerate(hits, 1):
        c = hit.chunk
        meta = c.meta or {}
        label = (f"[{n}] 《{c.doc_name}》"
                 f"{f'（{meta.get("quality")} {meta.get("score")}分）' if meta.get('quality') else ''}"
                 f"{f' 章节：{c.heading}' if c.heading else ''}")
        excerpt = best_excerpt(c.text, query, width)
        blocks.append(f"{label}\n{excerpt}")
    return "\n\n".join(blocks)


class QAPipeline:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

    def ask(self, question, top_k=None, use_graph=None, with_llm=False,
            llm_client=None) -> Answer:
        hits = self.retriever.search(question, top_k=top_k, use_graph=use_graph)

        context = format_context(hits, question)
        subgraph = self.retriever.subgraph_text(hits)
        if subgraph:
            context = context + "\n\n" + subgraph
        prompt = PROMPT_TEMPLATE.format(context=context, question=question)

        answer = None
        if with_llm:
            from .llm import LLMClient
            client = llm_client or LLMClient()
            log.info("调用 %s 生成答案…", client.config.llm_model)
            answer = client.chat(prompt)

        sources = [{
            "doc_name": h.chunk.doc_name,
            "score": round(h.score, 4),
            "sources": h.sources,
            "quality": (h.chunk.meta or {}).get("quality"),
            "excerpt": best_excerpt(h.chunk.text, question, 120),
        } for h in hits]

        return Answer(question=question, hits=hits, prompt=prompt,
                      answer=answer, sources=sources)
