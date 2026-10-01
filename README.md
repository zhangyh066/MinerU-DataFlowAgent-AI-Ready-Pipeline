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

## 目录结构

```
.
├── convert_mineru_jsons.py   # 步骤二：MinerU JSON → input.json
├── homework1_final.py        # 步骤三：大模型批量评分/摘要 + 失败重试 + 报告导出
├── input.json                # 待评估文档列表
├── mineru_outputs/           # MinerU 解析输出的 JSON 文件（15 篇文献）
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
# 生成/更新 input.json
python convert_mineru_jsons.py

# 运行评估流水线
python homework1_final.py

# 可调参数：批大小、批间等待、失败重试轮数、模型等
python homework1_final.py --batch-size 5 --sleep 5 --max-retries 2
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
- 平均分 **86.5**，全部摘要见 `all_summaries.txt`

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
- `summary_report_batch.txt`：总数、成功率、失败原因统计与样例预览。

## 作者

Yuhui Zhang
