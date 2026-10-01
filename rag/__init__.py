"""RAG 检索与问答子系统。

从 rag_demo 提炼并工程化：语义向量(BGE) + BM25 混合检索 + RRF 融合 +
术语共现图谱扩展 + 可选 LLM 生成 + 命中率评测。

主要模块：
    config     配置（环境变量覆盖）
    text       中文分词 / 停用词 / 术语与关键词抽取
    chunking   面向纯文本的句子级切块（标题边界感知 + 重叠）
    embedding  向量模型（BGE 优先，TF-IDF 兜底）
    store      语料切块与向量索引的构建、持久化与加载
    retrieval  BM25、RRF、混合检索器
    graph      术语共现图与跳扩展
    llm        OpenAI 兼容接口的 LLM 客户端（urllib，零额外依赖）
    qa         检索 -> 组提示词 -> 生成
    evaluate   自动/标注两种命中率评测
    cli        build / query / ask / eval 子命令
"""

__version__ = "1.0.0"
