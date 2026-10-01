"""BM25 词法检索、RRF 融合与混合检索器。"""

import logging
import math
from dataclasses import dataclass, field

import numpy as np

from .chunking import Chunk
from .text import tokenize

log = logging.getLogger(__name__)


@dataclass
class Hit:
    chunk: Chunk
    score: float
    sources: str = "向量"          # 向量 / 词法 / 图谱 / 组合，如 "向量+词法"
    chunk_id: int = -1             # 在索引中的位置（图谱查询等按 id 定位）


class BM25Index:
    """BM25 关键词检索（jieba 分词，词表共享检索用的停用词过滤）。"""

    def __init__(self, texts, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.n = len(texts)
        self.tf, self.dl = [], []
        self.df = {}
        for t in texts:
            words = tokenize(t)
            counter = {}
            for w in words:
                counter[w] = counter.get(w, 0) + 1
            self.tf.append(counter)
            self.dl.append(max(1, len(words)))
            for w in counter:
                self.df[w] = self.df.get(w, 0) + 1
        self.avgdl = sum(self.dl) / max(1, self.n)

    def search(self, query, k):
        if self.n == 0:
            return []
        scores = np.zeros(self.n, dtype=np.float32)
        for w in set(tokenize(query)):
            df = self.df.get(w)
            if not df:
                continue
            idf = math.log(1 + (self.n - df + 0.5) / (df + 0.5))
            for i in range(self.n):
                f = self.tf[i].get(w)
                if not f:
                    continue
                scores[i] += idf * f * (self.k1 + 1) / (
                    f + self.k1 * (1 - self.b + self.b * self.dl[i] / self.avgdl))
        order = np.argsort(-scores)[:k]
        return [(int(i), float(scores[i])) for i in order if scores[i] > 0]


def rrf_fuse(rank_lists, k=60, top_n=10):
    """
    Reciprocal Rank Fusion：只看排名不看分数。
    候选得分 = 各路 1/(k + 排名) 之和，多路同排的候选叠加得分。
    """
    scores, origin = {}, {}
    for name, lst in rank_lists:
        for rank, idx in enumerate(lst, start=1):
            scores[idx] = scores.get(idx, 0.0) + 1.0 / (k + rank)
            origin.setdefault(idx, []).append(name)
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])[:top_n]
    return [(i, s, "+".join(origin.get(i, []))) for i, s in ranked]


class HybridRetriever:
    """向量 + BM25 混合检索（RRF 融合），可选术语共现图扩展。"""

    def __init__(self, index, config):
        self.index = index
        self.config = config
        self.chunks: list[Chunk] = index.chunks
        self.bm25 = BM25Index(index.ctx_texts)
        self._term_graph = None

    @property
    def term_graph(self):
        if self._term_graph is None:
            from .graph import TermGraph
            self._term_graph = TermGraph.build(self.chunks)
        return self._term_graph

    def _dense_search(self, query, k):
        qv = self.index.embedder.encode([query])[0]
        sims = self.index.matrix @ qv
        order = np.argsort(-sims)[:k]
        return [(int(i), float(sims[i])) for i in order if sims[i] > 0]

    def search(self, query, top_k=None, use_graph=None) -> list[Hit]:
        top_k = top_k or self.config.top_k
        use_graph = self.config.graph_enabled if use_graph is None else use_graph
        n_cand = max(self.config.fuse_candidates, top_k * 3)

        dense_hits = self._dense_search(query, n_cand)
        bm25_hits = self.bm25.search(query, n_cand)

        rank_lists = [("向量", [i for i, _ in dense_hits]),
                      ("词法", [i for i, _ in bm25_hits])]

        # 图谱扩展作为第三路参与 RRF：与向量/词法同为排名信号，量纲一致
        if use_graph:
            graph_rank = self._graph_candidates(query, dense_hits, n_cand)
            if graph_rank:
                rank_lists.append(("图谱", graph_rank))

        fused = rrf_fuse(rank_lists, k=self.config.rrf_k, top_n=n_cand)

        hits = []
        for idx, score, origin in fused[:top_k]:
            hits.append(Hit(chunk=self.chunks[idx], score=score,
                            sources=origin, chunk_id=idx))
        return hits

    def _graph_candidates(self, query, dense_hits, n_cand):
        """术语共现图扩展：把与命中块「逻辑相关但不像」的块作为一路候选。"""
        from .text import extract_terms

        seeds = set(extract_terms(query, 8))
        for i, _ in dense_hits[:3]:
            seeds |= set(self.term_graph.chunk_terms.get(i, []))

        gscore = self.term_graph.expand(seeds)
        if not gscore:
            return []
        ranked = sorted(gscore.items(), key=lambda kv: -kv[1])[:n_cand]
        return [i for i, _ in ranked]

    def subgraph_text(self, hits: list[Hit]) -> str:
        """把命中块之间的术语关联整理成一段话，作为生成时的补充上下文。"""
        lines = []
        for a in range(len(hits)):
            for b in range(a + 1, len(hits)):
                terms_a = set(self.term_graph.chunk_terms.get(hits[a].chunk_id, []))
                terms_b = set(self.term_graph.chunk_terms.get(hits[b].chunk_id, []))
                shared = [t for t in terms_a & terms_b]
                if shared:
                    lines.append(
                        f"- 《{hits[a].chunk.doc_name}》与《{hits[b].chunk.doc_name}》"
                        f"都提到了：{'、'.join(shared[:5])}")
        if not lines:
            return ""
        return "【这些资料之间的关联】\n" + "\n".join(lines)
