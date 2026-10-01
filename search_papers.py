"""
search_papers.py

基于 TF-IDF 的本地文献语义检索：对评估通过的文献正文分块建立索引，
输入关键词或问题，返回最相关的文献片段并注明出处，是 RAG 应用的最小示例。

有 jieba 时使用中文分词（停用词过滤），否则退化为字符 n-gram，两种模式均可工作。

用法：
    python search_papers.py --query "金融科技对银行流动性创造的影响"
    python search_papers.py --query "流动性创造" --top-k 3
    python search_papers.py                # 进入交互模式，多次查询
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CHUNK_SIZE = 450      # 每块字符数
CHUNK_STRIDE = 350    # 分块步长（相邻块有重叠，保证语义连贯）
TOP_KEYWORDS = 15     # 关键词统计保留的词数

try:
    import jieba
    jieba.setLogLevel(60)  # 关闭初始化日志
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

# 通用中文停用词 + 学术写作高频泛化词（对关键词展示和检索都是噪声）
STOPWORDS = set("""
的 了 和 与 及 或 在 是 对 为 等 中 由 其 该 此 有 无 不 也 都 而 且 但 并 把 被 让 向 从 到 上 下
一个 一些 以及 因此 通过 进行 本文 我们 可以 具有 表示 其中 基于 相关
进一步 结果表明 与此同时 综上所述 也就是说 特别 显然 可能 主要 采用 利用 发现 提出
影响 关系 水平 方面 程度 由于 对于 来说 之一 不仅 而且 如果 虽然 因为 所以
""".split())


def make_console_output_safe():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(errors="replace")
            except Exception:
                pass


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="本地文献语义检索（TF-IDF）")
    parser.add_argument("--query", default=None, help="检索词或问题（缺省进入交互模式）")
    parser.add_argument("--top-k", type=int, default=5, help="返回结果条数（默认：5）")
    parser.add_argument("--input", default=str(BASE_DIR / "output_results_batch.json"),
                        help="评估结果 JSON（默认：./output_results_batch.json）")
    parser.add_argument("--texts", default=str(BASE_DIR / "input.json"),
                        help="原始文档文本 JSON（默认：./input.json）")
    parser.add_argument("--include-all", action="store_true",
                        help="检索全部文献（默认仅检索 QUALITY=YES 的高质量文献）")
    return parser.parse_args(argv)


# ================= 分词与向量化（纯 Python） =================
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9-]{1,}")


def tokenize(text):
    """
    中英文混合分词：
    - 有 jieba：jieba 中文分词 + 西文单词，过滤停用词
    - 无 jieba：退化为字符 bigram + trigram（对中英文均有一定效果）
    """
    text = text.lower()

    if HAS_JIEBA:
        tokens = []
        for w in jieba.lcut(text):
            w = w.strip()
            if len(w) < 2 or w in STOPWORDS:
                continue
            if _CJK_RE.search(w) or _WORD_RE.fullmatch(w):
                tokens.append(w)
        return tokens

    tokens = []
    cjk_chars = [ch for ch in text if _CJK_RE.match(ch)]
    n = len(cjk_chars)
    for i in range(n - 1):
        tokens.append(cjk_chars[i] + cjk_chars[i + 1])
    for i in range(n - 2):
        tokens.append(cjk_chars[i] + cjk_chars[i + 1] + cjk_chars[i + 2])
    tokens.extend(_WORD_RE.findall(text))
    return tokens


class TfidfIndex:
    """极简 TF-IDF 检索索引：chunks = [(doc_idx, chunk_text, vector)]"""

    def __init__(self):
        self.chunks = []
        self.idf = {}
        self.doc_names = []

    def build(self, docs):
        """docs: [(name, text)]"""
        self.doc_names = [name for name, _ in docs]

        raw_chunks = []  # (doc_idx, chunk_text, token列表)
        df = {}
        for doc_idx, (_, text) in enumerate(docs):
            for chunk_text in split_chunks(text):
                tokens = tokenize(chunk_text)
                if not tokens:
                    continue
                raw_chunks.append((doc_idx, chunk_text, tokens))
                for tok in set(tokens):
                    df[tok] = df.get(tok, 0) + 1

        n = len(raw_chunks)
        self.idf = {tok: math.log((1 + n) / (1 + freq)) + 1 for tok, freq in df.items()}

        for doc_idx, chunk_text, tokens in raw_chunks:
            vec = self._vectorize(tokens)
            self.chunks.append((doc_idx, chunk_text, vec))

    def _vectorize(self, tokens):
        tf = {}
        for tok in tokens:
            tf[tok] = tf.get(tok, 0) + 1
        vec = {}
        norm_sq = 0.0
        for tok, count in tf.items():
            weight = (1 + math.log(count)) * self.idf.get(tok, 0)
            vec[tok] = weight
            norm_sq += weight * weight
        norm = math.sqrt(norm_sq) or 1.0
        return vec, norm

    def search(self, query, top_k=5):
        q_tokens = tokenize(query)
        if not q_tokens or not self.chunks:
            return []
        q_vec, q_norm = self._vectorize(q_tokens)

        scored = []
        for doc_idx, chunk_text, (vec, norm) in self.chunks:
            dot = sum(w * vec.get(tok, 0) for tok, w in q_vec.items())
            if dot <= 0:
                continue
            scored.append((dot / (q_norm * norm), doc_idx, chunk_text))

        scored.sort(key=lambda x: -x[0])
        return scored[:top_k]


def split_chunks(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    if not text:
        return []
    chunks = []
    for start in range(0, len(text), CHUNK_STRIDE):
        chunk = text[start:start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
        if start + CHUNK_SIZE >= len(text):
            break
    return chunks


def shorten(text, max_len=160):
    text = text.replace("\n", " ").strip()
    return text if len(text) <= max_len else text[:max_len] + "..."


# ================= 关键词统计（供 generate_report 复用） =================
def top_keywords(docs, top_n=TOP_KEYWORDS):
    """docs: [(name, text)] -> [(词, 权重)]，用于报告中的关键词条形图。"""
    if HAS_JIEBA:
        import jieba.analyse
        text = " ".join(t for _, t in docs)
        pairs = jieba.analyse.extract_tags(text, topK=top_n * 3, withWeight=True)
        return [(w, float(x)) for w, x in pairs if w not in STOPWORDS][:top_n]

    index = TfidfIndex()
    index.build(docs)
    weights = {}
    for _, _, (vec, _) in index.chunks:
        for tok, w in vec.items():
            if len(tok) < 2:  # 过滤单字符噪声
                continue
            weights[tok] = max(weights.get(tok, 0), w)
    return sorted(weights.items(), key=lambda x: -x[1])[:top_n]


# ================= 主流程 =================
def load_docs(args):
    with open(args.input, "r", encoding="utf-8") as f:
        rows = json.load(f)
    with open(args.texts, "r", encoding="utf-8") as f:
        texts = json.load(f)

    by_name = {t.get("file_name"): t.get("text", "") for t in texts}
    docs = []
    for row in rows:
        if not args.include_all and row.get("quality") != "YES":
            continue
        name = row.get("file_name")
        text = by_name.get(name, "")
        if text:
            docs.append((name, text, row))
    return docs


def run_query(index, meta_by_doc, query, top_k):
    hits = index.search(query, top_k=top_k)
    if not hits:
        print("未找到相关内容。")
        return
    for rank, (score, doc_idx, chunk) in enumerate(hits, 1):
        name, _, row = meta_by_doc[doc_idx]
        print(f"\n[{rank}] 相关度 {score:.3f}  |  {name}")
        print(f"    判定 {row.get('quality')} / 评分 {row.get('score')}")
        print(f"    片段: {shorten(chunk)}")


def main(argv=None):
    make_console_output_safe()
    args = parse_args(argv)

    docs = load_docs(args)
    if not docs:
        print("没有可检索的文献（请先运行 homework1_final.py 完成评估）")
        sys.exit(1)

    index = TfidfIndex()
    index.build([(name, text) for name, text, _ in docs])
    meta_by_doc = list(docs)
    print(f"已建立索引：{len(index.doc_names)} 篇文献，{len(index.chunks)} 个文本块")

    if args.query:
        run_query(index, meta_by_doc, args.query, args.top_k)
        return

    print("进入交互模式，输入问题检索文献，输入 q 退出。")
    while True:
        try:
            query = input("\n检索> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if query.lower() in ("q", "quit", "exit"):
            break
        if query:
            run_query(index, meta_by_doc, query, args.top_k)


if __name__ == "__main__":
    main()
