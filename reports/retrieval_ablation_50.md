# 检索效果评测报告

- 向量后端：`bge`
- 图谱扩展：开

## 结论怎么读

自动评测是「下限体检」（拿块内容反查自身），数字必然偏高，只用于发现管道故障；
人工标注评测才是能写进报告的效果数字。判据：Top-K 内存在来自期望文献且含任一关键词的块。

## 检索消融（同一批人工题）

| 方案 | Top-1 | Top-3 | Top-3 命中率 |
| --- | ---: | ---: | ---: |
| 纯向量 | 24/46 | 30/46 | 65.2% |
| 纯 BM25 | 31/46 | 35/46 | 76.1% |
| 向量 + BM25 | 29/46 | 32/46 | 69.6% |
| 向量 + BM25 + 图谱 | 29/46 | 32/46 | 69.6% |

消融只用于观察这批题目上的相对变化；样本量较小时，不把分数差异外推为稳定收益。

## 人工标注评测

- 题目数：46
- Top-1 命中：29/46
- Top-3 命中率：**69.6%**（32/46）

### 未命中题目（比命中率本身更有用）

- 问题：为什么有些企业边际产出低却仍保持高投资？
  - 期望文献：Investing in misallocation
  - 实际召回：MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_并购模式与企业创新_陈爱贞.pdf_6d8c8fd9-be91-494e-b4e4-0e7d15a2dc67.json、MinerU_json_中国市场化利率调控体系改革思考_张成思.pdf_c52090fb-652d-4208-8e94-d61b4176ac40.json
- 问题：高投资低边际产出的企业大约占多大比例？
  - 期望文献：Investing in misallocation
  - 实际召回：MinerU_json_金融科技监管与实体企业创新：来自中国版“监管沙盒”试点的考察_田利辉.pdf_40fd8755-85c1-448d-9473-089fb5652f17.json、MinerU_json_金融科技监管与实体企业创新：来自中国版“监管沙盒”试点的考察_田利辉.pdf_40fd8755-85c1-448d-9473-089fb5652f17.json、MinerU_json_并购模式与企业创新_陈爱贞.pdf_6d8c8fd9-be91-494e-b4e4-0e7d15a2dc67.json
- 问题：消除表面上的资本错配会对总生产率产生什么影响？
  - 期望文献：Investing in misallocation
  - 实际召回：MinerU_json_中国金融科技发展对资本市场信息效率的影响研究_杨松令.pdf_5f5ebfda-4469-4b9a-8012-7148c37874eb.json、MinerU_json_中国金融科技发展对资本市场信息效率的影响研究_杨松令.pdf_5f5ebfda-4469-4b9a-8012-7148c37874eb.json、MinerU_json_金融科技对银行风险的影响研究——基于流动性创造与经营效率的分析_张骏.pdf_78ad6eac-094b-4f89-9636-3d8507ba3936.json
- 问题：负面社交媒体情绪与并购撤回之间有什么关系？
  - 期望文献：COOKSON
  - 实际召回：MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json、MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json、MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json
- 问题：企业开设官方 Twitter 账号后，社交媒体情绪对并购撤回的影响有何变化？
  - 期望文献：COOKSON
  - 实际召回：MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json、MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json、MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json
- 问题：社交媒体影响并购撤回更支持管理者学习机制还是治理机制？
  - 期望文献：COOKSON
  - 实际召回：MinerU_json_基金经理媒体报道与个体投资者行为——来自基金申赎微观大数据的证据_贺佳.pdf_b07245a5-208d-470b-bcb3-48340bb6fe84.json、MinerU_json_并购模式与企业创新_陈爱贞.pdf_6d8c8fd9-be91-494e-b4e4-0e7d15a2dc67.json、MinerU_json_并购模式与企业创新_陈爱贞.pdf_6d8c8fd9-be91-494e-b4e4-0e7d15a2dc67.json
- 问题：活期存款每增长1%会驱动超额准备金增长多少？
  - 期望文献：中国商业银行超额准备金持有的驱动机制研究
  - 实际召回：MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_751b5b2e-4d0d-4443-949d-e149640391a2.json、MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_751b5b2e-4d0d-4443-949d-e149640391a2.json、MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_751b5b2e-4d0d-4443-949d-e149640391a2.json
- 问题：大型银行和中小型银行对短期利率信号的反应有何不同？
  - 期望文献：中国商业银行超额准备金持有的驱动机制研究
  - 实际召回：MinerU_json_金融科技对传统银行行为的影响——基于互联网理财的视角_邱晗.pdf_fd885568-715a-4aa1-91e9-7c0737e21c8c.json、MinerU_json_中国商业银行超额准备金持有的驱动机制研究.pdf_751b5b2e-4d0d-4443-949d-e149640391a2.json、MinerU_json_中国市场化利率调控体系改革思考_张成思.pdf_c52090fb-652d-4208-8e94-d61b4176ac40.json
- 问题：哪篇论文认为外部竞争效应大于技术溢出效应并抑制银行流动性创造？
  - 期望文献：金融科技与银行行为——基于流动性创造视角
  - 实际召回：MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json
- 问题：金融科技通过哪些渠道抑制银行流动性创造？
  - 期望文献：金融科技与银行行为——基于流动性创造视角
  - 实际召回：MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json
- 问题：监管沙盒通过哪些渠道推动企业创新？
  - 期望文献：金融科技监管与实体企业创新
  - 实际召回：MinerU_json_金融科技监管与实体企业创新：来自中国版“监管沙盒”试点的考察_田利辉.pdf_40fd8755-85c1-448d-9473-089fb5652f17.json、MinerU_json_金融科技监管与实体企业创新：来自中国版“监管沙盒”试点的考察_田利辉.pdf_40fd8755-85c1-448d-9473-089fb5652f17.json、MinerU_json_金融科技监管与实体企业创新：来自中国版“监管沙盒”试点的考察_田利辉.pdf_40fd8755-85c1-448d-9473-089fb5652f17.json
- 问题：哪篇论文认为金融科技会抑制银行流动性创造？
  - 期望文献：金融科技与银行行为——基于流动性创造视角
  - 实际召回：MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json、MinerU_json_金融科技与商业银行流动性创造：抑制还是促进_盛天翔.pdf_52c0b6a2-2573-4cbe-b346-bca23af87051.json
- 问题：Which social platforms were used to study merger withdrawals in the COOKSON paper?
  - 期望文献：COOKSON
  - 实际召回：MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json、MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json、MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json
- 问题：What kinds of tweets are most associated with merger withdrawals in the COOKSON study?
  - 期望文献：COOKSON
  - 实际召回：MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json、MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json、MinerU_json_The Journal of Finance - 2025 - COOKSON - Can Social Media Inform Corporate Decisions  Evidence from Merger Withdrawals.pdf_f29548f7-9261-41be-8bfe-0773f6bffb9c.json

## 报告口径备注

1. 样本量：见各节题目/块数；小样本下数字波动大，扩大语料后应复测。
2. 题目来源：人工对着原文撰写（见 eval_questions.json）。
3. 判据：文件级宽松判定（Top-K 内存在来自期望文献且含任一关键词的块即算命中）。
