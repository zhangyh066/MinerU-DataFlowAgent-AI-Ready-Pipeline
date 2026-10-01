"""向量模型抽象：BGE 语义向量优先，TF-IDF 兜底，切换后端时索引自动重建。"""

import logging
import os
from pathlib import Path

import numpy as np

from .text import char_ngrams

log = logging.getLogger(__name__)


def normalize(matrix):
    """行向量归一化，之后点积即余弦相似度。"""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


class BaseEmbedder:
    name = "base"
    # 是否需要先在语料上 fit（TF-IDF 需要，BGE 不需要）
    needs_fit = False

    def fit(self, texts):
        return self

    def encode(self, texts):
        raise NotImplementedError

    def save_state(self, npz_path, extra):
        """把需要持久化的状态写进 npz（子类按需扩展）。"""

    def load_state(self, data):
        """从 npz 读取状态，返回是否成功。"""


class TfidfEmbedder(BaseEmbedder):
    """TF-IDF 稀疏向量：纯本地计算，无需模型，作为 BGE 不可用时的兜底。"""

    name = "tfidf"
    needs_fit = True

    def fit(self, texts):
        df = {}
        for t in texts:
            for g in set(char_ngrams(t)):
                df[g] = df.get(g, 0) + 1
        self.vocab = {g: i for i, g in enumerate(sorted(df))}
        n = len(texts)
        self.idf = np.ones(len(self.vocab), dtype=np.float32)
        for g, i in self.vocab.items():
            self.idf[i] = np.log((1 + n) / (1 + df[g])) + 1
        return self

    def encode(self, texts):
        matrix = np.zeros((len(texts), len(self.vocab)), dtype=np.float32)
        for r, t in enumerate(texts):
            tf = {}
            for g in char_ngrams(t):
                if g in self.vocab:
                    tf[g] = tf.get(g, 0) + 1
            for g, c in tf.items():
                matrix[r, self.vocab[g]] = c * self.idf[self.vocab[g]]
        return normalize(matrix)

    def save_state(self, npz_path, extra):
        vocab = np.array(sorted(self.vocab, key=self.vocab.get))
        np.savez(npz_path, matrix=extra["matrix"], backend=self.name,
                 vocab=vocab, idf=self.idf)

    def load_state(self, data):
        if "vocab" not in data or "idf" not in data:
            return False
        self.vocab = {g: i for i, g in enumerate(data["vocab"].tolist())}
        self.idf = data["idf"]
        return True


class BgeEmbedder(BaseEmbedder):
    """BGE 中文语义向量（sentence-transformers，本地模型目录加载）。"""

    name = "bge"

    def __init__(self, model_dir, model_name):
        # 国内网络下两个必要的开关（下载时才生效）
        os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
        os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise RuntimeError(
                "未安装 sentence-transformers，无法使用 BGE 向量"
            ) from e

        model_dir = Path(model_dir)
        if not (model_dir / "config.json").exists():
            log.info("本地未见模型，首次运行需下载约 100MB：%s", model_name)
            from huggingface_hub import snapshot_download
            # local_dir 直接落地：默认缓存模式在 Windows 非管理员下建不了符号链接
            model_dir.mkdir(parents=True, exist_ok=True)
            snapshot_download(model_name, local_dir=str(model_dir))

        log.info("加载向量模型：%s", model_dir)
        self.model = SentenceTransformer(str(model_dir))

    def encode(self, texts):
        return self.model.encode(
            list(texts), normalize_embeddings=True, show_progress_bar=False)

    def save_state(self, npz_path, extra):
        np.savez(npz_path, matrix=extra["matrix"], backend=self.name)

    def load_state(self, data):
        return True


def create_embedder(backend, model_dir, model_name):
    """按配置创建向量模型；BGE 不可用时自动降级 TF-IDF。"""
    if backend == "tfidf":
        return TfidfEmbedder()
    if backend == "bge":
        try:
            return BgeEmbedder(model_dir, model_name)
        except (RuntimeError, ImportError) as e:
            log.warning("BGE 不可用（%s），自动降级 TF-IDF", e)
            return TfidfEmbedder()
    raise ValueError(f"未知 embedding 后端：{backend}")
