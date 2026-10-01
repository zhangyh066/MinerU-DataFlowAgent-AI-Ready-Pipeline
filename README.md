# 基于 MinerU 与 DataFlow-Agent 的 AI-Ready 数据自动化生产线

一条「PDF 文献 → AI-Ready 结构化数据」的自动化处理流水线：用 MinerU 将金融类 PDF 解析为结构化 JSON，再由 DataFlow-Agent 驱动大模型（GLM-4.5-Air）对文献自动评分、分类并生成摘要，最终产出可直接用于下游 AI 应用的高质量语料。

## 处理流程

```
PDF 文献
  │  ① MinerU 解析
  ▼
mineru_outputs/*.json
  │  ② convert_mineru_jsons.py：清洗、抽取正文、去重
  ▼
input.json  ──►  ③ homework1_final.py：DataFlow-Agent + GLM 批量评分/摘要、失败重试
                    │
                    ▼
     output_results_batch.json / all_summaries.txt / summary_report_batch.txt
```

## 功能特性

- **MinerU JSON 批量转换**：兼容 block/span、content_list 等多种 MinerU 导出结构，自动清洗脏字符、按内容指纹去重；
- **大模型批量评估**：五维评分规则（满分 100），自动解析模型输出，质量判定与分数自洽性校验；
- **失败自动重试**：缺结果或解析失败的条目自动重试，报告含失败原因统计；
- **断点续跑缓存**：按文档内容指纹缓存评估结果，重跑只处理新增/变更文档，不重复消耗 API 额度；
- **AI-Ready 语料导出**：一键把高质量文献导出为 JSONL（微调/RAG）与 Markdown；
- **交互式 HTML 报告**：筛选、搜索、排序、图表统计，离线浏览器直接打开；
- **文献语义检索**：基于 TF-IDF（jieba 分词）的本地检索，输入问题返回相关文献片段并注明出处，是 RAG 应用的最小示例；
- **一键流水线**：`run_all.py` 串联转换 → 评估 → 导出 → 报告，新文献放入 `mineru_outputs/` 后增量更新；
- **CSV 导出与关键词词频**：评估结果可导出 Excel 打开的 CSV，报告内置语料高频关键词图。

## 目录结构

```
.
├── convert_mineru_jsons.py   # 步骤二：MinerU JSON → input.json
├── homework1_final.py        # 步骤三：大模型批量评分/摘要 + 失败重试 + 断点续跑
├── export_ai_ready.py        # 拓展：导出 AI-Ready 语料（JSONL / Markdown / CSV）
├── generate_report.py        # 拓展：生成交互式 HTML 评估报告（含关键词词频图）
├── search_papers.py          # 拓展：本地文献语义检索（TF-IDF + jieba 分词）
├── run_all.py                # 拓展：一键运行完整流水线
├── input.json                # 待评估文档列表
├── mineru_outputs/           # MinerU 解析输出的 JSON 文件（15 篇文献）
├── ai_ready_corpus/          # 导出的高质量语料
│   ├── corpus.jsonl
│   ├── corpus_eval.csv
│   └── markdown/
├── report.html               # 交互式评估报告
├── charts/                   # 报告图表 PNG
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

在项目根目录创建 `.env` 文件，填入大模型 API 密钥（`.env` 已被 git 忽略，不会上传）：

```
DF_API_KEY=你的密钥
```

可选环境变量：`MODEL_NAME`（默认 `glm-4.5-air`）、`API_URL`。

## 使用

```bash
# 一键运行完整流水线（新文献放入 mineru_outputs/ 后增量更新）
python run_all.py
python run_all.py --skip-eval   # 不调 API，基于已有结果重建导出与报告

# 分步执行
python convert_mineru_jsons.py                  # 生成/更新 input.json
python homework1_final.py                       # 大模型批量评估
python homework1_final.py --batch-size 5 --sleep 5 --max-retries 2
python homework1_final.py --no-cache            # 忽略缓存全部重评

# 导出 AI-Ready 语料（默认仅导出 YES 文献）
python export_ai_ready.py
python export_ai_ready.py --include-partial --min-score 80
python export_ai_ready.py --formats jsonl md csv

# 生成交互式 HTML 报告（可选同时导出图表 PNG）
python generate_report.py --charts-dir charts

# 本地文献语义检索
python search_papers.py --query "金融科技对银行流动性创造的影响"
python search_papers.py            # 交互模式
```

## 评分规则（总分 100）

| 维度 | 分值 | 说明 |
| --- | --- | --- |
| 方法与识别 | 0–25 | DID、回归、理论模型、因果识别 |
| 可复用信息 | 0–25 | 变量、机制、样本、结果 |
| 金融相关 | 0–20 | 风险、投资、银行、创新、市场机制 |
| 噪声控制 | 0–15 | 无目录、无乱码、无封面、无教学题目 |
| 学术贡献 | 0–15 | 有机制、有假说、有明确贡献 |

判定标准：`score ≥ 80` → **YES**；`60–79` → **PARTIAL**；`< 60` → **NO**。

## 运行结果

对 `mineru_outputs/` 中 15 篇文献（金融科技、银行行为、资产定价等方向）完成批量评估：

- 总文档数 **15**，解析成功率 **100%**
- **YES 13 篇**、PARTIAL 1 篇、NO 1 篇
- 平均分 **84.3**（其中 YES 文献平均 **90.5**），全部摘要见 `all_summaries.txt`

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

评估效果符合预期：正式学术论文全部识别为 YES；行业研究报告因缺少计量方法识别为 PARTIAL；考试练习题被正确判为 NO 并过滤，验证了流水线的质量甄别能力。

## 输出文件

- `output_results_batch.json`：结构化结果，含每篇的 `quality / score / reason / summary`；
- `all_summaries.txt`：全部文献的摘要合集；
- `summary_report_batch.txt`：总数、成功率、失败原因统计与样例预览；
- `ai_ready_corpus/corpus.jsonl`：高质量语料（JSONL，含正文、摘要、元信息），可直接用于微调或 RAG；
- `ai_ready_corpus/corpus_eval.csv`：评估结果表（Excel 可直接打开）；
- `ai_ready_corpus/markdown/`：高质量语料的 Markdown 版本；
- `report.html`：交互式评估报告，浏览器直接打开；
- `charts/`：报告中的统计图表 PNG（质量占比、评分分布、高频关键词）。

## 作者

Yuhui Zhang
