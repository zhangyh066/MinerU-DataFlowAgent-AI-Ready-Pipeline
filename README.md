# 基于 MinerU 与 DataFlow-Agent 的 AI-Ready 数据自动化生产线

本项目演示了一条「PDF → AI-Ready 数据」的自动化处理流水线：

1. 用 [MinerU](https://github.com/opendatalab/MinerU) 将金融类 PDF 文献解析为结构化 JSON；
2. `convert_mineru_jsons.py` 批量清洗、抽取正文，合并为 `input.json`；
3. `homework1_final.py` 基于 OpenDataLab [DataFlow-Agent](https://github.com/opendatalab/DataFlow-Agent) 调用大模型（默认智谱 GLM-4.5-Air），按统一的五维评分规则对每篇文献打分、分类并生成摘要，最终输出结构化结果与统计报告。

## 目录结构

```
.
├── convert_mineru_jsons.py   # 步骤一：MinerU JSON → input.json（清洗 + 去重）
├── homework1_final.py        # 步骤二：大模型批量评分/摘要 + 失败重试 + 报告导出
├── input.json                # 步骤一的输出，待评估文档列表
├── mineru_outputs/           # MinerU 解析输出的 JSON 文件
├── output_results_batch.json # 结构化评估结果（每篇：quality/score/reason/summary）
├── all_summaries.txt         # 全部文档的摘要合集
├── summary_report_batch.txt  # 统计报告
└── 0基础读懂_MinerU_DataFlowAgent_教程.md  # 原理解读教程
```

## 环境准备

```bash
pip install -r requirements.txt
```

> ⚠️ **注意包名陷阱**：DataFlow-Agent 的 pip 包名是 `dataflow-agent`（安装后 `import dataflow`）。
> PyPI 上另有一个同名包 `dataflow`，是无关的第三方库，**不要安装**。
> 判断方法：`import dataflow` 后如果存在 `dataflow.serving` / `dataflow.pipeline` 子模块，才是正确的包。

## 配置

在项目根目录创建 `.env` 文件（该文件已被 .gitignore 排除，不会上传）：

```bash
cp .env.example .env
# 然后编辑 .env，填入你的密钥
```

可用环境变量：

| 变量 | 说明 |
| --- | --- |
| `DF_API_KEY` | 必填，大模型 API 密钥（智谱开放平台） |
| `MODEL_NAME` | 可选，覆盖默认模型 `glm-4.5-air` |
| `API_URL` | 可选，覆盖默认的 chat completions 接口地址 |

## 使用

```bash
# 步骤一：把 mineru_outputs/ 下的 MinerU JSON 转成 input.json
python convert_mineru_jsons.py

# 步骤二：运行评估流水线（默认逐条处理、批间等待 15 秒，适配免费额度限流）
python homework1_final.py

# 常用可调参数
python homework1_final.py --batch-size 5      # 每批 5 条（注意 API 限流与额度）
python homework1_final.py --sleep 5           # 缩短批间等待
python homework1_final.py --max-retries 2     # 失败条目最多重试 2 轮
python homework1_final.py --input 其他.json --output 结果.json
```

## 评分规则（总分 100）

| 维度 | 分值 | 说明 |
| --- | --- | --- |
| 方法与识别 | 0–25 | DID、回归、理论模型、因果识别 |
| 可复用信息 | 0–25 | 变量、机制、样本、结果 |
| 金融相关 | 0–20 | 风险、投资、银行、创新、市场机制 |
| 噪声控制 | 0–15 | 无目录、无乱码、无封面、无教学题目 |
| 学术贡献 | 0–15 | 有机制、有假说、有明确贡献 |

判定：`score >= 80` → **YES**；`60–79` → **PARTIAL**；`< 60` → **NO**。
输出时会额外校验模型给出的 QUALITY 与 SCORE 是否自洽，不一致的条目会在结果中标记。

## 输出文件

- `output_results_batch.json`：结构化结果，含 `quality / score / reason / summary` 字段；解析失败的条目保留 `raw_result_preview` 便于排查；
- `all_summaries.txt`：全部文档的摘要合集；
- `summary_report_batch.txt`：总数、成功率、失败原因统计与样例预览。

## 隐私说明

- `.env`（API 密钥）已通过 `.gitignore` 排除，不会进入版本库；
- 仓库中 `mineru_outputs/` 内的文献解析结果仅用于课程演示。
