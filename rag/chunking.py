"""面向纯文本的句子级切块（从 rag_demo 提炼，去掉页码概念）。

与滑窗切块相比，这里按「句子累加 + 标题边界优先下刀 + 尾部句子重叠」，
块的语义更完整。每个块附带来源文档与所属标题，检索时组装 contextual chunk。
"""

import re
from dataclasses import dataclass, field

from .text import char_ngrams

# 小标题特征：一、 / （一） / 1. / 1.1 / 第X章/节 开头的短行
HEADING_RE = re.compile(
    r"^\s*((第[一二三四五六七八九十百\d]+[章节部分篇])|"
    r"([一二三四五六七八九十]+、)|"
    r"(（[一二三四五六七八九十\d]+）)|"
    r"(\d+(\.\d+)*[\.、．]?))\s*\S{0,40}$"
)


@dataclass
class Chunk:
    doc_name: str
    text: str
    heading: str = ""
    index: int = 0                      # 在所属文档内的序号（从 1 开始）
    meta: dict = field(default_factory=dict)

    @property
    def ctx_text(self) -> str:
        """contextual chunk：给块补上「来自哪篇文档、哪一节」，提升向量可区分度。"""
        title = re.sub(r"\.json$", "", self.doc_name, flags=re.I)
        head = f"《{title}》"
        if self.heading:
            head += self.heading + " "
        return head + title + "\n" + self.text


def _iter_lines(text):
    """把文本拆成句子行：MinerU 清洗后的文本一行一句，直接按行迭代。"""
    for line in (text or "").splitlines():
        line = line.strip()
        if line:
            yield line


def _carry_tail(buf, overlap):
    """把上一块结尾的几个完整句子挪到下一块开头。"""
    if overlap <= 0:
        return []
    out, total = [], 0
    for sent in reversed(buf):
        if total >= overlap:
            break
        out.insert(0, sent)
        total += len(sent)
    return out


def split_text(text, doc_name, chunk_size=300, overlap=60):
    """
    按句子攒块：一句句往上加，快满就切；
    遇到小标题且当前块已有一定内容时，优先在标题处下刀。
    """
    chunks, buf, buf_len = [], [], 0
    heading = ""

    for sent in _iter_lines(text):
        at_heading = bool(HEADING_RE.match(sent)) and len(sent) <= 45
        if buf and (buf_len + len(sent) > chunk_size
                    or (at_heading and buf_len > chunk_size * 0.4)):
            chunks.append(Chunk(doc_name, "\n".join(buf), heading))
            buf = _carry_tail(buf, overlap)

        if at_heading:
            heading = sent[:30]

        buf.append(sent)
        buf_len = sum(len(s) for s in buf)

    if buf:
        chunks.append(Chunk(doc_name, "\n".join(buf), heading))

    for i, c in enumerate(chunks, 1):
        c.index = i
    return chunks


def best_excerpt(text, query, width=80):
    """在块里找出与问题重合度最高的一小段作为预览。"""
    grams = set(char_ngrams(query))
    if not grams or len(text) <= width:
        return text[:width]
    best_pos, best_hit = 0, -1
    step = max(1, width // 3)
    for i in range(0, max(1, len(text) - 10), step):
        hit = len(grams & set(char_ngrams(text[i:i + width])))
        if hit > best_hit:
            best_hit, best_pos = hit, i
    return text[best_pos:best_pos + width].replace("\n", "")
