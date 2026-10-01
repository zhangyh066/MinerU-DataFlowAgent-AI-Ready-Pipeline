# 基于 MinerU 与 DataFlow-Agent 的 AI-Ready 数据自动化生产线

**项目周期：2026.03 — 2026.04　|　负责人：Yuhui Zhang**

针对大模型训练中非结构化 PDF 清洗成本高的痛点，本项目主导搭建了「高精解析 + 智能调度」的端到端数据生产线：原始金融文献 PDF 经过解析、清洗、质量评估后，自动转化为带质量分级、可直接供微调 / RAG 使用的高质量数据集，并内置检索问答与效果评测能力，实现从原始文档到 AI-Ready 语料的全流程自动化。

## 核心能力

- **版面解析**：集成 MinerU 攻克双栏排版、跨页表格及密集公式的提取难题，精准剥离页眉页脚噪声，公式高保真转为 LaTeX 代码，表格无损还原为结构化文本；
- **智能编排**：基于 DataFlow-Agent 串联解析结果装载、正则清洗、内容去重、LLM 批量评分与自动摘要等算子，数据在管道中自动流转，配合内容指纹缓存实现增量更新、断点续跑；
- **质量管控**：引入 Prompt 驱动的质量评估智能体，基于大模型按五维规则动态评估文本质量，构建「通过（YES）/ 存疑（PARTIAL）/ 丢弃（NO）」动态路由，自动拦截练习题、目录、封面等低质数据，确保产出语料具备高信噪比；评估原始输出全量留存，质量判定与分数自洽性自动校验；
- **工程化拓展**：一键流水线（`run_all.py`）串联全部环节；AI-Ready 语料一键导出（JSONL / Markdown / CSV）；交互式 HTML 评估报告（筛选、搜索、排序、图表）；RAG 检索问答子系统（BGE 语义向量 + BM25 混合检索 + 术语共现图谱扩展 + 带引用生成 + 命中率评测）。

## 整体架构

```
PDF 文献
  │  ① MinerU 高精解析（双栏/表格/公式，输出结构化 JSON）
  ▼
mineru_outputs/*.json
  │  ② convert_mineru_jsons.py：正则清洗、正文抽取、内容指纹去重
  ▼
input.json
  │  ③ homework1_final.py：DataFlow-Agent 编排 GLM 智能体
  │     五维评分 → YES/PARTIAL/NO 动态路由 → 失败自动重试 → 断点续跑缓存
  ▼
output_results_batch.json ──► ④ export_ai_ready.py：导出 AI-Ready 语料
  │                              （JSONL 微调/RAG · Markdown · CSV）
  ▼
ai_ready_corpus/corpus.jsonl
  │  ⑤ rag_cli.py build：句子级切块 + BGE 向量化 + BM25 + 共现图
  ▼
data/rag_index/ ──► query / ask（混合检索 + 图谱扩展 + 带引用生成）
                   ──► eval（自动体检 + 人工标注命中率评测）
```

## 目录结构

```
.
├── convert_mineru_jsons.py   # ② MinerU JSON → input.json（清洗 + 去重）
├── homework1_final.py        # ③ LLM 批量评分/摘要 + 失败重试 + 断点续跑
├── export_ai_ready.py        # ④ AI-Ready 语料导出（JSONL / Markdown / CSV）
├── generate_report.py        # 交互式 HTML 评估报告（含关键词词频图）
├── rag_cli.py                # RAG 命令行：build / query / ask / eval
├── rag/                      # RAG 检索与问答子系统（包）
├── run_all.py                # 一键运行完整流水线
├── eval_questions.json       # 检索命中率人工标注评测集
├── input.json                # 待评估文档列表
├── mineru_outputs/           # MinerU 解析输出（15 篇金融科技文献）
├── ai_ready_corpus/          # AI-Ready 语料库
│   ├── corpus.jsonl
│   ├── corpus_eval.csv
│   └── markdown/
├── data/rag_index/           # RAG 检索索引（rag_cli.py build 生成）
├── report.html               # 交互式评估报告
├── charts/                   # 报告图表 PNG
├── reports/                  # 检索效果评测报告
├── output_results_batch.json # 结构化评估结果
├── all_summaries.txt         # 全部文献摘要合集
├── summary_report_batch.txt  # 统计报告
└── 0基础读懂_MinerU_DataFlowAgent_教程.md  # 原理解读教程
```

## 环境准备

```bash
pip install -r requirements.txt
```

## 配置

在项目根目录创建 `.env` 文件，填入大模型 API 密钥（`.env` 已被 git 忽略，敏感信息不会入库）：

```
DF_API_KEY=你的密钥
```

可选环境变量：`MODEL_NAME`（默认 `glm-4.5-air`）、`API_URL`、`RAG_LLM_PROVIDER`（设为 `deepseek` 时改用 `DEEPSEEK_API_KEY`）、`RAG_MODEL_DIR`（BGE 模型目录）。

## 使用

```bash
# 一键运行完整流水线（新文献放入 mineru_outputs/ 后增量更新）
python run_all.py
python run_all.py --skip-eval   # 不调 API，基于已有结果重建导出、索引与报告

# 分步执行
python convert_mineru_jsons.py                  # ② 清洗转换
python homework1_final.py                       # ③ LLM 批量评估
python homework1_final.py --batch-size 5 --sleep 5 --max-retries 2
python homework1_final.py --no-cache            # 忽略缓存全部重评
python export_ai_ready.py --include-partial     # ④ 导出语料（可加 --min-score 80）
python generate_report.py --charts-dir charts   # HTML 评估报告

# RAG 检索与问答
python rag_cli.py build                          # 从语料构建持久化检索索引
python rag_cli.py query --query "金融科技对银行流动性创造的影响"
python rag_cli.py ask --question "金融科技通过什么机制影响银行风险承担？"
python rag_cli.py ask --question "..." --with-llm   # 真正调用大模型生成带引用回答
python rag_cli.py eval --auto --questions eval_questions.json   # 检索命中率评测
```

## 评分规则（总分 100）

| 维度 | 分值 | 说明 |
| --- | --- | --- |
| 方法与识别 | 0–25 | DID、回归、理论模型、因果识别 |
| 可复用信息 | 0–25 | 变量、机制、样本、结果 |
| 金融相关 | 0–20 | 风险、投资、银行、创新、市场机制 |
| 噪声控制 | 0–15 | 无目录、无乱码、无封面、无教学题目 |
| 学术贡献 | 0–15 | 有机制、有假说、有明确贡献 |

判定标准：`score ≥ 80` → **YES**（进入语料库）；`60–79` → **PARTIAL**；`< 60` → **NO**（动态路由拦截）。输出时自动校验质量判定与分数的自洽性，不一致条目单独标记。

## 运行结果

对 `mineru_outputs/` 中 15 篇文献（金融科技、银行行为、资产定价等方向）完成批量评估：

- 总文档数 **15**，评估解析成功率 **100%**
- **YES 13 篇**、PARTIAL 1 篇、NO 1 篇
- 平均分 **84.3**（其中 YES 文献平均 **90.5**）
- RAG 混合检索人工标注评测 **Top-3 命中率 87.5%**（评测报告见 `reports/retrieval_eval.md`）

| 文献 | 判定 | 分数 |
| --- | :-: | :-: |
| 金融科技与银行行为——基于流动性创造视角（宋科） | YES | 93 |
| 金融科技对银行风险的影响研究——基于流动性创造与经营效率的分析（张骏） | YES | 93 |
| 算法交易的市场影响：稳定与信息效率的双重视角（岳崴） | YES | 93 |
| 中国商业银行超额准备金持有的驱动机制研究 | YES | 93 |
| 基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据（贺佳） | YES | 92 |
| 金融科技监管与实体企业创新：来自中国版"监管沙盒"试点的考察（田利辉） | YES | 92 |
| 并购模式与企业创新（陈爱贞） | YES | 90 |
| 金融科技与商业银行流动性创造：抑制还是促进（盛天翔） | YES | 90 |
| Investing in Misallocation（Kılıç & Tüzel） | YES | 89 |
| 金融科技对传统银行行为的影响——基于互联网理财的视角（邱晗） | YES | 89 |
| 中国市场化利率调控体系改革思考（张成思） | YES | 88 |
| Can Social Media Inform Corporate Decisions? Evidence from Merger Withdrawals（J. of Finance, 2025） | YES | 88 |
| 中国金融科技发展对资本市场信息效率的影响研究（杨松令） | YES | 86 |
| Commonwealth Bank of Australia 股权研究报告（CFA Research Challenge） | PARTIAL | 66 |
| CFA 一级组合管理考前练习题 | NO | 23 |

评估效果符合预期：正式学术论文全部识别为 YES；行业研究报告因缺少计量方法识别为 PARTIAL；考试练习题被正确判为 NO 并路由拦截，验证了质量管控机制的有效性。

## RAG 检索与问答设计要点

- **切块**：按句子累加、小标题边界优先下刀、块间句子重叠；每块向量化为 contextual chunk（块前补《文件名》+ 章节），避免同类套话段落互相混淆；
- **混合检索**：BGE 语义向量（本地模型，sentence-transformers 不可用时自动降级 TF-IDF）与 BM25 词法检索两路召回，RRF 倒数排名融合；术语共现图（jieba 名词性术语 + 稀有度加权）作为第三路信号参与融合，把「内容不像但逻辑相关」的块补召回，命中结果带来源标记（向量/词法/图谱）；
- **生成**：检索结果按相关度组装成带 `[编号]` 引用的提示词，默认只打印提示词，`--with-llm` 才真正调用大模型（默认 GLM，可切 DeepSeek）；附「资料间关联」子图作为多跳上下文；
- **评测**：自动体检（块内容反查自身的下限参考）+ 人工标注评测集（`eval_questions.json`）计算 Top-K 命中率，报告含未命中题目分析；
- **持久化**：索引存于 `data/rag_index/`（向量 + 块元数据 + 后端标识），更换向量后端时自动检测并拒绝混用。

## 输出文件

- `output_results_batch.json`：结构化评估结果，含每篇的 `quality / score / reason / summary`；
- `ai_ready_corpus/corpus.jsonl`：高质量语料（正文、摘要、质量元信息），可直接用于微调或 RAG；
- `ai_ready_corpus/corpus_eval.csv`：评估结果表（Excel 可直接打开）；
- `ai_ready_corpus/markdown/`：高质量语料的 Markdown 版本；
- `report.html`：交互式评估报告，浏览器直接打开；
- `charts/`：质量占比、评分分布、高频关键词图表 PNG；
- `data/rag_index/`：RAG 检索索引（`rag_cli.py build` 生成，`query/ask` 自动加载）；
- `reports/retrieval_eval.md`：检索命中率评测报告；
- `all_summaries.txt` / `summary_report_batch.txt`：摘要合集与统计报告。

## 作者

Yuhui Zhang
