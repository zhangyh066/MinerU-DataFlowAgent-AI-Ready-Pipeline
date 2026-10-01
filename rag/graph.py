"""术语共现图：节点=术语，边=同块共现权重，支持多跳扩展（从 rag_demo 提炼）。"""

import logging
import math

from .text import extract_terms

log = logging.getLogger(__name__)

# 出现块数超过该比例的术语视为泛词，剔除
MAX_TERM_DF = 0.3


class TermGraph:
    def __init__(self):
        self.inv = {}            # 术语 -> {块id: 出现次数}
        self.edges = {}          # 术语 -> {邻居术语: 边权重}
        self.chunk_terms = {}    # 块id -> [术语]

    @classmethod
    def build(cls, chunks, per_chunk_terms=15):
        graph = cls()
        chunk_terms = {}
        for i, c in enumerate(chunks):
            chunk_terms[i] = extract_terms(c.ctx_text, per_chunk_terms)
        graph.chunk_terms = chunk_terms

        n = len(chunks)
        for i, terms in chunk_terms.items():
            for t in terms:
                graph.inv.setdefault(t, {})
                graph.inv[t][i] = graph.inv[t].get(i, 0) + 1

        # 只保留出现在 2~(max_df) 个块之间的术语：单块出现的当不了桥梁，太多块的是泛词
        max_df = max(3, int(n * MAX_TERM_DF))
        graph.inv = {t: m for t, m in graph.inv.items() if 2 <= len(m) <= max_df}

        # 稀有度：越常见的词越不值钱，避免“发展×产业”这类泛词组合淹没真关系
        idf = {t: math.log((1 + n) / (1 + len(m))) for t, m in graph.inv.items()}

        for terms in chunk_terms.values():
            keep = [t for t in terms if t in graph.inv]
            for a in range(len(keep)):
                for b in range(a + 1, len(keep)):
                    t1, t2 = keep[a], keep[b]
                    w = idf[t1] * idf[t2]
                    graph.edges.setdefault(t1, {})
                    graph.edges[t1][t2] = graph.edges[t1].get(t2, 0) + w
                    graph.edges.setdefault(t2, {})
                    graph.edges[t2][t1] = graph.edges[t2].get(t1, 0) + w

        n_edges = sum(len(v) for v in graph.edges.values()) // 2
        log.info("术语共现图：%d 个节点，%d 条边", len(graph.inv), n_edges)
        return graph

    def expand(self, seed_terms, hops=2, decay=0.5, max_terms=40):
        """
        从种子术语出发在图上走 hops 跳，沿途收集术语对应的块得分。
        每多跳一次权重打折一次：隔得越远，关系越弱。
        """
        weights = {t: 1.0 for t in seed_terms if t in self.inv}
        if not weights:
            return {}

        frontier = set(weights)
        for hop in range(hops):
            step = decay ** (hop + 1)
            nxt = {}
            for t in frontier:
                for nb, w in (self.edges.get(t) or {}).items():
                    nxt[nb] = max(nxt.get(nb, 0.0), w * step)
            new_terms = [(t, w) for t, w in nxt.items() if t not in weights]
            if not new_terms:
                break
            new_terms.sort(key=lambda kv: -kv[1])
            frontier = set()
            for t, w in new_terms[:max_terms]:
                weights[t] = w
                frontier.add(t)

        chunk_score = {}
        for t, w in weights.items():
            for i, c in (self.inv.get(t) or {}).items():
                chunk_score[i] = chunk_score.get(i, 0) + w * c
        return chunk_score
