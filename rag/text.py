"""中文分词、停用词、术语与关键词抽取（jieba 优先，自动降级）。"""

import re

try:
    import jieba
    import jieba.analyse
    jieba.setLogLevel(60)
    HAS_JIEBA = True
except ImportError:
    HAS_JIEBA = False

_CJK_RE = re.compile(r"[一-鿿]")
_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9-]{1,}")

# 通用中文停用词 + 学术写作高频泛化词
STOPWORDS = set("""
的 了 和 与 及 或 在 是 对 为 等 中 由 其 该 此 有 无 不 也 都 而 且 但 并 把 被 让 向 从 到 上 下
一个 一些 以及 因此 通过 进行 本文 我们 可以 具有 表示 其中 基于 相关
进一步 结果表明 与此同时 综上所述 也就是说 特别 显然 可能 主要 采用 利用 发现 提出
影响 关系 水平 方面 程度 由于 对于 来说 之一 不仅 而且 如果 虽然 因为 所以
如下 所示 上述 本文研究 研究表明
""".split())


def char_ngrams(text, n=2):
    text = re.sub(r"\s+", "", text or "")
    if len(text) < n:
        return [text] if text else []
    return [text[i:i + n] for i in range(len(text) - n + 1)]


def tokenize(text):
    """
    中英文混合分词（用于检索向量与 BM25）：
    - 有 jieba：jieba 分词 + 停用词过滤，保留中文词与西文单词
    - 无 jieba：退化为字符 bigram + trigram
    """
    text = (text or "").lower()

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


def extract_terms(text, topn=15):
    """抽取名词性术语（用于共现图节点）。只留名词性词，避免碎片词当节点。"""
    if HAS_JIEBA:
        return jieba.analyse.extract_tags(
            text or "", topK=topn,
            allowPOS=("n", "nr", "ns", "nt", "nz", "vn", "eng"))
    from collections import Counter
    cnt = Counter(char_ngrams(text))
    return [w for w, _ in cnt.most_common(topn)]


def top_keywords(docs, top_n=15):
    """docs: [(name, text)] -> [(词, 权重)]，用于报告中的关键词条形图。"""
    if HAS_JIEBA:
        text = " ".join(t for _, t in docs)
        pairs = jieba.analyse.extract_tags(text, topK=top_n * 3, withWeight=True)
        return [(w, float(x)) for w, x in pairs if w not in STOPWORDS][:top_n]

    # 无 jieba 的兜底：按字符 bigram 词频
    from collections import Counter
    cnt = Counter()
    for _, t in docs:
        cnt.update(char_ngrams(t))
    total = sum(cnt.values()) or 1
    return [(w, c / total) for w, c in cnt.most_common(top_n) if len(w) >= 2]
