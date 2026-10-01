"""RAG 子系统配置。所有参数可用环境变量覆盖。"""

import os
from dataclasses import dataclass, field
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# BGE 模型的查找顺序：本地 models/ -> rag_demo 已下载的模型 -> 触发下载到本地 models/
_MODEL_CANDIDATES = [
    BASE_DIR / "models" / "bge-small-zh-v1.5",
    Path(r"D:\workbuddy缓存\2026-09-18-14-27-45\rag_demo\模型\bge-small-zh-v1.5"),
    BASE_DIR / "models" / "bge-small-zh-v1.5",  # 兜底：下载目标位置
]

DEFAULT_MODEL_NAME = "BAAI/bge-small-zh-v1.5"


def resolve_model_dir() -> Path:
    env_dir = os.getenv("RAG_MODEL_DIR")
    if env_dir:
        return Path(env_dir)
    local = find_local_model()
    if local is not None:
        return local
    return _MODEL_CANDIDATES[0]  # 都找不到时：作为下载目标位置


def find_local_model() -> Path | None:
    """返回已存在 config.json 的本地模型目录，没有则返回 None。"""
    for cand in _MODEL_CANDIDATES:
        if (cand / "config.json").exists():
            return cand
    return None


@dataclass
class RAGConfig:
    # 路径
    base_dir: Path = BASE_DIR
    corpus_file: Path = field(default_factory=lambda: BASE_DIR / "ai_ready_corpus" / "corpus.jsonl")
    index_dir: Path = field(default_factory=lambda: BASE_DIR / "data" / "rag_index")

    # 切块
    chunk_size: int = 300
    chunk_overlap: int = 60

    # 检索
    top_k: int = 5
    fuse_candidates: int = 20        # 融合前每路取回的候选数
    rrf_k: int = 60                  # RRF 平滑系数
    graph_weight: float = 0.35       # 图谱扩展得分的加成上限
    graph_enabled: bool = True

    # 向量模型：bge 优先，失败自动退回 tfidf
    embed_backend: str = field(default_factory=lambda: os.getenv("RAG_EMBED_BACKEND", "bge"))
    model_name: str = DEFAULT_MODEL_NAME
    model_dir: Path = field(default_factory=resolve_model_dir)

    # LLM（OpenAI 兼容接口）
    llm_provider: str = field(default_factory=lambda: os.getenv("RAG_LLM_PROVIDER", "glm"))
    llm_model: str = field(default_factory=lambda: os.getenv("RAG_LLM_MODEL", "glm-4.5-air"))
    llm_timeout: int = 120
    llm_retries: int = 2

    @classmethod
    def from_env(cls) -> "RAGConfig":
        cfg = cls()
        if os.getenv("RAG_CORPUS"):
            cfg.corpus_file = Path(os.getenv("RAG_CORPUS"))
        if os.getenv("RAG_INDEX_DIR"):
            cfg.index_dir = Path(os.getenv("RAG_INDEX_DIR"))
        if os.getenv("RAG_TOP_K"):
            cfg.top_k = int(os.getenv("RAG_TOP_K"))
        if os.getenv("RAG_CHUNK_SIZE"):
            cfg.chunk_size = int(os.getenv("RAG_CHUNK_SIZE"))
        if os.getenv("RAG_CHUNK_OVERLAP"):
            cfg.chunk_overlap = int(os.getenv("RAG_CHUNK_OVERLAP"))
        return cfg

    @property
    def chunks_file(self) -> Path:
        return self.index_dir / "chunks.jsonl"

    @property
    def vectors_file(self) -> Path:
        return self.index_dir / "vectors.npz"

    @property
    def meta_file(self) -> Path:
        return self.index_dir / "meta.json"
