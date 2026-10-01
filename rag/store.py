"""语料切块与向量索引的构建、持久化与加载。"""

import json
import logging
from datetime import datetime
from pathlib import Path

import numpy as np

from .chunking import Chunk, split_text
from .config import RAGConfig
from .embedding import create_embedder

log = logging.getLogger(__name__)


class IndexNotFoundError(FileNotFoundError):
    pass


class ChunkIndex:
    """
    切块 + 向量的持久化索引。

    磁盘布局（index_dir）：
        chunks.jsonl  每行一个块（doc_name/text/heading/index/meta）
        vectors.npz   向量矩阵 + 后端标识（TF-IDF 另存词表与 idf）
        meta.json     后端、模型、构建时间、块数量
    """

    def __init__(self, config: RAGConfig):
        self.config = config
        self.chunks: list[Chunk] = []
        self.matrix: np.ndarray | None = None
        self.embedder = None

    # ---------- 构建 ----------
    def build(self, corpus_file: Path | None = None):
        corpus_file = Path(corpus_file or self.config.corpus_file)
        if not corpus_file.exists():
            raise FileNotFoundError(
                f"语料文件不存在：{corpus_file}（先运行 export_ai_ready.py 导出）")

        docs = self._load_corpus(corpus_file)
        log.info("语料：%s，共 %d 篇", corpus_file, len(docs))

        chunks = []
        for name, text, meta in docs:
            doc_chunks = split_text(
                text, name,
                chunk_size=self.config.chunk_size,
                overlap=self.config.chunk_overlap,
            )
            for c in doc_chunks:
                c.meta = dict(meta)
            chunks.extend(doc_chunks)
        if not chunks:
            raise ValueError("切块结果为空，请检查语料内容")
        log.info("切块完成：%d 个块（chunk_size=%d, overlap=%d）",
                 len(chunks), self.config.chunk_size, self.config.chunk_overlap)

        self.embedder = create_embedder(
            self.config.embed_backend, self.config.model_dir, self.config.model_name)
        if self.embedder.needs_fit:
            self.embedder.fit([c.ctx_text for c in chunks])
        matrix = self.embedder.encode([c.ctx_text for c in chunks])

        self.chunks, self.matrix = chunks, matrix
        return self

    @staticmethod
    def _load_corpus(corpus_file: Path):
        docs = []
        with open(corpus_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                text = row.get("text", "")
                if not text.strip():
                    continue
                meta = {k: row.get(k) for k in ("quality", "score", "summary", "reason")}
                docs.append((row.get("file_name", "未命名"), text, meta))
        return docs

    # ---------- 持久化 ----------
    def save(self):
        self.config.index_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config.chunks_file, "w", encoding="utf-8") as f:
            for c in self.chunks:
                f.write(json.dumps({
                    "doc_name": c.doc_name,
                    "text": c.text,
                    "heading": c.heading,
                    "index": c.index,
                    "meta": c.meta,
                }, ensure_ascii=False) + "\n")

        self.embedder.save_state(self.config.vectors_file,
                                 {"matrix": self.matrix})

        with open(self.config.meta_file, "w", encoding="utf-8") as f:
            json.dump({
                "backend": self.embedder.name,
                "model": self.config.model_name,
                "n_chunks": len(self.chunks),
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }, f, ensure_ascii=False, indent=2)
        log.info("索引已保存：%s（%d 块，后端 %s）",
                 self.config.index_dir, len(self.chunks), self.embedder.name)

    def exists(self) -> bool:
        return (self.config.chunks_file.exists()
                and self.config.vectors_file.exists()
                and self.config.meta_file.exists())

    def load(self):
        if not self.exists():
            raise IndexNotFoundError(
                f"索引不存在：{self.config.index_dir}（先运行 rag_cli.py build）")

        with open(self.config.meta_file, encoding="utf-8") as f:
            meta = json.load(f)

        self.embedder = create_embedder(
            self.config.embed_backend, self.config.model_dir, self.config.model_name)

        # 后端不一致（换过模型）时强制重建，两种向量空间不能混用
        if meta.get("backend") != self.embedder.name:
            raise IndexNotFoundError(
                f"索引后端({meta.get('backend')})与当前配置({self.embedder.name})不一致，请重建索引")

        data = np.load(self.config.vectors_file, allow_pickle=False)
        if not self.embedder.load_state(data):
            raise IndexNotFoundError("索引向量状态不完整，请重建索引")
        self.matrix = data["matrix"]

        self.chunks = []
        with open(self.config.chunks_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    row = json.loads(line)
                    self.chunks.append(Chunk(
                        doc_name=row["doc_name"], text=row["text"],
                        heading=row.get("heading", ""), index=row.get("index", 0),
                        meta=row.get("meta", {}),
                    ))
        log.info("索引已加载：%d 块（后端 %s）", len(self.chunks), self.embedder.name)
        return self

    def load_or_build(self):
        try:
            return self.load()
        except IndexNotFoundError as e:
            log.info("%s", e)
            return self.build()

    # ---------- 检索辅助 ----------
    @property
    def ctx_texts(self):
        return [c.ctx_text for c in self.chunks]
