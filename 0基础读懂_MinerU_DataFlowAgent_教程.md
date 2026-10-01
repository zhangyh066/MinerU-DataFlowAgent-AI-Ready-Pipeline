# 零基础读懂 MinerU + DataFlowAgent 数据生产线

> 这篇教程面向完全零基础的同学，目标是让你不用会写代码，也能看懂这个项目在做什么、每一步是什么意思、结果怎么看。

---

## 一、一句话总结

这个项目做了一件很简单的事：

> **把一堆 PDF 论文丢给 MinerU 拆成文字 → 用 DataFlowAgent 调用 AI 大模型给每篇论文打分、写摘要 → 最后输出一份质量评估报告。**

你可以把它理解成一个 **"AI 论文筛选流水线"**：

```
PDF 论文文件夹
    ↓
MinerU（拆解员）把 PDF 变成结构化文字
    ↓
convert_mineru_jsons.py（清洗员）把文字整理干净，存成 input.json
    ↓
homework1_final.py（评分员）调用 AI 大模型逐篇评估
    ↓
output_results_batch.json、summary_report_batch.txt（成绩单）
```

---

## 二、MinerU 是什么？

### 2.1 通俗理解

**MinerU** 是一个专门用来 **"读懂 PDF"** 的开源工具。

PDF 文件对人眼友好，但对电脑程序来说是一团乱麻：文字、图片、表格、公式、页眉页脚全混在一起。MinerU 的作用就像 **一个细心的文档拆解员**，它会把 PDF 里的内容：

- 拆成一段段正文
- 识别出表格
- 区分标题、段落、页眉页脚
- 保留阅读顺序

最后输出成一个 **结构化的 JSON 文件**。

### 2.2 JSON 是什么？

你可以把 JSON 理解成 **一种电脑喜欢的"清单格式"**。就像下面这样：

```json
{
  "file_name": "某篇论文.pdf",
  "pages": [
    {
      "page_number": 1,
      "blocks": [
        {"type": "text", "content": "论文标题"},
        {"type": "table", "content": "表格内容"}
      ]
    }
  ]
}
```

每个 `{}` 是一个对象，每个 `[]` 是一个列表。MinerU 的输出就是这种格式，方便后面的程序读取。

### 2.3 在本项目中的作用

在项目文件夹里，你会看到一个 `mineru_outputs/` 文件夹，里面都是 MinerU 处理好的 JSON 文件，例如：

```
mineru_outputs/
├── MinerU_json_Investing in misallocation.pdf_xxx.json
├── MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_xxx.json
└── ...
```

这些文件就是 MinerU 把原始 PDF 论文"拆解"后的结果。文件名里通常带有原始 PDF 的名字和一个随机编号。

---

## 三、DataFlowAgent 是什么？

### 3.1 通俗理解

**DataFlowAgent** 是一个帮助开发者 **"搭流水线"** 的 Python 框架。

所谓"搭流水线"，就是把一系列数据处理步骤串起来：

```
读取数据 → 处理数据 → 调用 AI 模型 → 保存结果
```

DataFlowAgent 提供了很多现成的"积木"，比如：

- `PipelineABC`：流水线的骨架
- `FileStorage`：读写本地文件
- `APILLMServing_request`：调用在线 AI 大模型
- `PromptedGenerator`：把提示词发给大模型并获取回答

### 3.2 为什么要用它？

如果没有 DataFlowAgent，你要自己写很多重复代码：怎么读取 JSON、怎么调用 API、API 超时了怎么办、结果怎么缓存……

DataFlowAgent 把这些麻烦事封装好了，你只需要：

1. 指定输入文件
2. 指定要调用的模型
3. 写一段提示词（告诉 AI 要做什么）
4. 指定输出位置

剩下的它帮你搞定。

### 3.3 在本项目中的作用

在 `homework1_final.py` 中，DataFlowAgent 负责：

1. 读取 `input.json`（已经被清洗好的论文文字）
2. 一篇一篇地调用 **智谱 GLM-4.5-air** 大模型
3. 让 AI 按照固定格式输出：`QUALITY`、`SCORE`、`REASON`、`SUMMARY`
4. 把结果保存到 `output_results_batch.json` 和 `summary_report_batch.txt`

---

## 四、本项目到底在做什么？

### 4.1 整体流程图

```
┌─────────────────────┐
│  原始 PDF 论文文件    │  （外部准备，不在本项目中运行）
└──────────┬──────────┘
           ↓  用 MinerU 处理
┌─────────────────────┐
│  mineru_outputs/    │  ← JSON 文件，每篇论文一个
│  （结构化文本数据）   │
└──────────┬──────────┘
           ↓  运行 convert_mineru_jsons.py
┌─────────────────────┐
│     input.json      │  ← 提取并清洗后的纯文本
│  （论文名字 + 正文）  │
└──────────┬──────────┘
           ↓  运行 homework1_final.py
┌─────────────────────┐
│ output_results_     │  ← 每篇论文的评分、理由、摘要
│   batch.json        │
├─────────────────────┤
│ summary_report_     │  ← 统计报告：多少 YES、多少 NO
│   batch.txt         │
├─────────────────────┤
│   all_summaries.txt │  ← 所有论文摘要合集
└─────────────────────┘
```

### 4.2 每一步详细解释

#### 第 1 步：MinerU 拆解 PDF（已提前完成）

你不需要在本项目中运行 MinerU。项目的 `mineru_outputs/` 文件夹里已经有它处理好的结果了。

#### 第 2 步：提取并清洗文字

**文件：`convert_mineru_jsons.py`**

这个脚本做的事情：

1. 打开 `mineru_outputs/` 里的每一个 JSON 文件
2. 从 JSON 里把正文、表格里的文字拿出来
3. 清洗掉乱码、多余空格、特殊符号等
4. 把结果保存成 `input.json`

`input.json` 的格式大概长这样：

```json
[
  {
    "file_name": "某论文.json",
    "text": "论文的正文内容……"
  },
  {
    "file_name": "另一篇论文.json",
    "text": "另一篇论文的正文内容……"
  }
]
```

#### 第 3 步：AI 评分

**文件：`homework1_final.py`**

这个脚本做的事情：

1. 读取 `input.json` 里的每篇论文
2. 调用 GLM-4.5-air 大模型
3. 给大模型一段"系统提示词"，让它扮演"金融论文质量评估助手"
4. 大模型返回固定格式的结果
5. 解析结果，保存成 JSON 和 TXT 报告

评分规则包括 5 个维度，总分 100：

| 维度 | 满分 | 评估什么 |
|------|------|----------|
| 方法与识别 | 25 | 有没有 DID、回归、理论模型、因果识别 |
| 可复用信息 | 25 | 有没有变量、机制、样本、结果 |
| 金融相关 | 20 | 是不是讲风险、投资、银行、创新、市场机制 |
| 噪声控制 | 15 | 有没有目录、乱码、封面、教学题目 |
| 学术贡献 | 15 | 有没有机制、假说、明确贡献 |

最终按分数判定：

- `score >= 80` → `YES`（高质量论文）
- `60 <= score < 80` → `PARTIAL`（部分可用）
- `score < 60` → `NO`（质量不够）

---

## 五、关键文件速查表

| 文件/文件夹 | 作用 | 是否需要手动改 |
|------------|------|---------------|
| `mineru_outputs/` | 存放 MinerU 处理后的 JSON 文件 | 否，一般是提前准备好的 |
| `convert_mineru_jsons.py` | 从 MinerU JSON 中提取并清洗文本，生成 `input.json` | 否，路径写死了 |
| `input.json` | 清洗后的论文纯文本，作为 AI 评估的输入 | 自动生成 |
| `homework1_final.py` | 调用大模型给论文评分的主程序 | 可以改提示词、模型、批次大小 |
| `.env` | 存放 API 密钥（`DF_API_KEY`） | 需要自己配置 |
| `output_results_batch.json` | 每篇论文的评分结果 | 自动生成 |
| `summary_report_batch.txt` | 统计报告 | 自动生成 |
| `all_summaries.txt` | 所有论文的摘要合集 | 自动生成 |

---

## 六、手把手运行步骤

### 6.1 准备工作

确保你已经：

1. 安装了 Python（建议 3.9 以上）
2. 安装了依赖包：`dataflow`、`python-dotenv` 等
3. 在 `.env` 文件里填写了你的 API Key：

```
DF_API_KEY=你的密钥
```

> 注意：`.env` 文件里已经有一个示例密钥，但这是大模型服务商分配的，如果你要长期跑，建议换成自己的。

### 6.2 第一步：生成 input.json

在终端里运行：

```bash
python convert_mineru_jsons.py
```

运行后你会看到类似输出：

```
[成功] MinerU_json_xxx.json -> 提取 12345 个字符
[成功] MinerU_json_yyy.json -> 提取 23456 个字符
全部完成，共写入 15 条数据
输出文件：input.json
```

如果有的文件提取为空，会显示 `[跳过]`。

### 6.3 第二步：运行 AI 评估

```bash
python homework1_final.py
```

这个脚本会：

1. 一次处理一篇论文（`BATCH_SIZE = 1`）
2. 每篇之间等待 15 秒（`SLEEP_SECONDS = 15`），防止调用 API 太频繁
3. 调用 GLM-4.5-air 大模型
4. 最后输出统计结果

运行过程中你会看到：

```
处理第 1 条...
⏳ 等待 15 秒后开始下一条...
处理第 2 条...
```

处理完所有论文后，终端会显示：

```
============================================================
【处理结果统计】
============================================================
总文档数：15
成功解析 result 的文档数：15
没有 result 的文档数：0
result 解析失败的文档数：0
QUALITY=YES 的文档数：13
QUALITY=PARTIAL 的文档数：1
QUALITY=NO 的文档数：1
解析成功率：100.0%
```

---

## 七、结果怎么看？

### 7.1 `output_results_batch.json`

这是结构化结果，每篇论文一条记录，例如：

```json
{
  "file_name": "MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_xxx.json",
  "quality": "YES",
  "score": 93,
  "reason": "该论文构建了严谨的理论模型，采用多种实证方法识别中国商业银行超额准备金持有的驱动机制……",
  "summary": "本文研究了中国商业银行超额准备金持有的驱动机制……",
  "parse_ok": true,
  "raw_result_preview": "<think> ... </think>"
}
```

字段含义：

| 字段 | 含义 |
|------|------|
| `file_name` | 原始 JSON 文件名 |
| `quality` | 质量等级：`YES` / `PARTIAL` / `NO` |
| `score` | 0-100 的分数 |
| `reason` | AI 给出的评分理由（一句话） |
| `summary` | AI 生成的 100-200 字摘要 |
| `parse_ok` | 是否成功解析出结构化结果 |
| `raw_result_preview` | AI 原始输出的前 200 字符预览 |

### 7.2 `summary_report_batch.txt`

这是给人类看的统计报告，例如：

```
============================================================
【AI-Ready 数据生产线结果报告】
============================================================
总文档数：15
成功解析 result 的文档数：15
没有 result 的文档数：0
result 解析失败的文档数：0
QUALITY=YES 的文档数：13
QUALITY=PARTIAL 的文档数：1
QUALITY=NO 的文档数：1
解析成功率：100.0%

【样例预览】
------------------------------------------------------------
文件名：MinerU_json_xxx.json
质量：YES
评分：93
理由：……
摘要：……
```

### 7.3 `all_summaries.txt`

这是所有论文摘要的合集，方便你快速浏览全部内容：

```
文件: MinerU_json_xxx.json
质量: YES
评分: 93
理由: ……
摘要: ……
==================================================
```

---

## 八、常见问题

### Q1：MinerU 是怎么把 PDF 变成 JSON 的？

MinerU 通过版面分析、OCR、表格识别等技术，把 PDF 页面拆成一个个"块"（block），每个块标记类型（文本、表格、图片等），然后按阅读顺序排列，输出 JSON。

### Q2：DataFlowAgent 和 LangChain 有什么区别？

两者都是帮助开发者调用大模型的框架，但 DataFlowAgent 更偏重于 **数据流水线** 场景：读取本地文件、批量处理、结果缓存、错误重试等。本项目用它是因为处理的是批量论文评估任务。

### Q3：为什么每次只处理一篇论文？

因为 `BATCH_SIZE = 1`。这样做的原因通常是：

- 大模型对长文本处理能力有限
- 单篇处理更容易调试和重试
- 避免一次性调用消耗太多 token

如果你论文很短，也可以改成 `BATCH_SIZE = 5` 一次处理 5 篇。

### Q4：为什么每篇之间要等 15 秒？

`SLEEP_SECONDS = 15` 是为了 **控制 API 调用频率**，避免被服务商限流。如果你用的是付费高速接口，可以适当调小。

### Q5：`parse_ok = false` 是什么意思？

说明 AI 没有按固定格式输出，程序没法解析出 `QUALITY`、`SCORE`、`REASON`、`SUMMARY`。可能的原因：

- 模型输出了额外的内容
- 提示词格式被模型忽略了
- 网络问题导致输出不完整

可以在 `raw_result_preview` 里看到 AI 到底输出了什么。

### Q6：我想换成其他模型，怎么改？

打开 `homework1_final.py`，找到下面这段代码：

```python
self.llm_serving = APILLMServing_request(
    api_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
    model_name="glm-4.5-air",
    ...
)
```

把 `api_url` 和 `model_name` 改成你要用的模型即可。注意 API Key 也要对应修改。

---

## 九、总结

| 工具/文件 | 角色 | 一句话 |
|----------|------|--------|
| **MinerU** | 文档拆解员 | 把 PDF 变成机器能读的结构化 JSON |
| **convert_mineru_jsons.py** | 清洗员 | 从 JSON 中提取干净文字 |
| **DataFlowAgent** | 流水线框架 | 把"读数据 → 调模型 → 存结果"串起来 |
| **homework1_final.py** | 评分员 | 调用 AI 给论文打分、写摘要 |
| **output_results_batch.json** | 成绩单 | 每篇论文的评分和摘要 |
| **summary_report_batch.txt** | 统计报告 | 整体通过率和样例预览 |

希望这份教程能帮你零基础看懂这个项目！如果还有不清楚的地方，建议从运行 `convert_mineru_jsons.py` 开始，亲眼看看 `input.json` 里长什么样，再跑一遍 `homework1_final.py`，观察输出结果，理解会更深刻。
