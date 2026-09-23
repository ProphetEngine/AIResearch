---
title: "Multimodal reasoning benchmarks：MMMU → MMMU-Pro"
topic: MMMU多模态推理基准
date: 2026-09-22
lines: [评测字段, 架构思想]
status: archived
sources:
 # slim: url+extract — MMMU / MMMU-Pro arXiv+ACL PDFs removed (>15MB; near-dup pair both dropped)
 - https://arxiv.org/abs/2311.16502
 - https://arxiv.org/abs/2409.02813
 - https://aclanthology.org/2025.acl-long.736/
 - https://mmmu-benchmark.github.io/
 - https://mmmu-benchmark.github.io/#leaderboard
arxiv: ["2311.16502", "2409.02813"]
related: ["多模态架构脉络", "评测与排行榜可靠性", "SelfRAG与CorrectiveRAG", "训练数据污染检测"]
archived: 2026-09-22
---

# Multimodal reasoning benchmarks：MMMU → MMMU-Pro

> **定位**：专家级多学科多模态推理评测 切片——主轴是评测史 **「文本捷径可破解 → 视觉必要」**，不是多模态预训练通史。
> **攻坚线**：**评测字段（主）**——MMMU 规模/学科/模态协议 → MMMU-Pro 三步加固（滤文本可解、扩选项、Vision-only 截图）；**架构思想（辅）**——分数下降对「真多模态理解」的含义（感知→跨模态整合→推理）。
> **硬划界**：
> - **相对 [[多模态架构脉络]]**：本篇 **不**重写 CLIP 对比预训练、Flamingo Perceiver、LLaVA 视觉指令微调全文；只取「多模态产品默认 / 需要可区分能力的评测」接口。
> - **相对 [[评测与排行榜可靠性]]**：本篇 **不**重写污染三分法、thinking 路由、第三方聚合榜元规则全文；只取「分数必须绑定协议」一句，并把 MMMU 族的协议字段写清。
> - **相对 [[SelfRAG与CorrectiveRAG]]**：检索增强评测另槽；本篇不写 Self-RAG/CRAG。
> **禁止编造**：主张与数字锚定官方 PDF（2026-09-22 CST）；live 榜滚动更新，正文以 PDF Table 为准。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文 A（一手）** | Yue et al., *MMMU: A Massive Multi-discipline Multimodal Understanding and Reasoning Benchmark for Expert AGI* | arXiv:**2311.16502v4** \[cs.CL\] **13 Jun 2024**；[abs](https://arxiv.org/abs/2311.16502) · [pdf](https://arxiv.org/pdf/2311.16502)；（**119** 页 letter） | 11.5K 题构造、六学科/30 科、异构图、交错图文；Table 2 文本-only / LMM / 人类专家 |
| **主文 B（一手 · arXiv）** | Yue et al., *MMMU-Pro: A More Robust Multi-discipline Multimodal Understanding Benchmark* | arXiv:**2409.02813v3** \[cs.CL\] **22 May 2025**；[abs](https://arxiv.org/abs/2409.02813) · [pdf](https://arxiv.org/pdf/2409.02813)；（**53** 页 A4） | 三步构造、与 MMMU Val 对照的 ∆、CoT/OCR 消融 |
| **主文 B′（一手 · ACL 相机就绪）** | 同上题名；ACL 2025 Long | https://aclanthology.org/2025.acl-long.736/ · [pdf](https://aclanthology.org/2025.acl-long.736.pdf)；（**53** 页 A4；页码 **15134–15186**） | 与 arXiv v3 同题；本篇数字以 ACL Table 1 / Fig. 1–7 为主核对，arXiv 作 URL 备链 |
| **榜 / 代码入口（文内）** | https://mmmu-benchmark.github.io/ · `#leaderboard` | live 更新；GitHub `MMMU-Benchmark/MMMU` | 只作入口；**不**用未核对手写记忆填当期分数 |

**一句话抓手：**
- **MMMU**：把「Expert AGI 监控」落到 **大学级多学科交错图文题**（11.5K；6 学科 / 30 科 / 183 子领域）；GPT-4V test **55.7%**，文本-only GPT-4 **33.8%**——但后文证明部分题仍可被文本捷径啃。
- **MMMU-Pro**：三步加压后，相对 MMMU Val 的模型掉分约 **16.8–26.9** pp；正式 overall = **Standard(10 opts) 与 Vision 的平均**；Vision 设定逼模型「同时看与读」。

---

## 二、议题边界：专家级多模态推理评测史，不是 CLIP/LLaVA 通史

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[多模态架构脉络]]** 多模态架构脉络 | 「需要评测真正的图文联合理解」的产品/能力动机 | CLIP 双塔、Flamingo gated XAttn、LLaVA 投影+指令数据全文 |
| **[[评测与排行榜可靠性]]** 榜可靠性 | 「一个数字 = 一整套未声明协议」→ 本篇把输入模态/选项数/滤题规则写死 | 污染检测通史、thinking 开关对照表、第三方聚合榜纪律全文 |
| **[[训练数据污染检测]]** 污染检测 | 「公开题会渗入爬取」自觉一句 | 检测方法论 |
| **[[SelfRAG与CorrectiveRAG]]** Self-RAG/CRAG | 同属「评测加固」族的相邻槽 | 检索正确性 / 引用 faithfulness 正文 |

### 2.2 跟读口诀（评测史一条线）

`
日常/常识 VQA、ScienceQA（偏中小学）
 │
 ▼
MMMU（2024）——大学级 × 多学科 × 异构图 × 交错图文
 │ 文本-only 基线仍远低于 LMM，但「无图可答」捷径仍在
 ▼
MMMU-Pro（ACL 2025）
 │ (1) 滤掉强文本 LLM 多数票可解的题
 │ (2) 4 → 10 选项，压缩猜测空间
 │ (3) Vision-only：题干+选项嵌进截图/照片，无显式文本通道
 ▼
「看起来多模态」→「视觉信息不可缺」的更硬观测
`

**关键语义：** 测的是 **专家级学科知识 + 图文联合推理** 是否被测到；**不**测对比预训练配方，也**不**测指令微调数据工程。

---

## 三、MMMU：把 Expert AGI 监控落到可操作的大学级多模态考卷

### 3.1 问题动机（§1，压缩）

- Morris 等 Expert AGI 定义强调广度与深度；作者以 **大学考试** 作为「熟练成人」的可操作代理（类比文本侧 MMLU / AGIEval），并补上 **多模态** 维。
- 既有多模态榜多偏常识/日常感知；ScienceQA 有广度但深度偏中小学。MMMU 目标：**breadth（30 科）+ depth（需学科知识的逐步推理）**。
- 文明确警告：MMMU **不是** Expert AGI 充分检验（无直接映射到「熟练成人第 90 百分位」）；但强表现应是 Expert AGI 的 **必要信号** 之一。

### 3.2 数据集字段（Table 1 / §3）

| 字段 | 文内数字 |
|---|---|
| 总题量 | **11,550**（文称 11.5K） |
| 学科 / 科目 / 子领域 | **6 / 30 / 183** |
| 图像类型 | **30** 种（图、表、化学结构、乐谱、病理、漫画等） |
| 划分 Dev : Val : Test | **150 : 900 : 10,500**（Dev = 每科 5 题 few-shot） |
| 难度 Easy : Med : Hard | **28% : 45% : 27%** |
| 题型 | 选择题 **10,861（94.03%）**；开放题 **689（5.97%）** |
| 图位置 | 问句中有图 **97.52%**；选项中有图 **3.37%**；多图例 **7.39%** |

**四项挑战（Fig. 1）：** ① 覆盖面；② 异构图像；③ **交错图文**；④ 植根学科知识的专家级感知与推理。

**采集纪律（跟读用）：** 50+ 大学生按专业收题；排除难以找到多模态题的学科（如 law / linguistics）；质量控制含词面/URL 去重、格式校对；难度四档后去掉约 10%「very easy」。文提及数据污染担忧，建议选答案不在题面旁立即可得的题——**此为采集自觉，不是完整 decontam 协议**（完整污染方法论见 [[评测与排行榜可靠性]] / [[训练数据污染检测]]）。

### 3.3 评测协议（§4）

- **零样本**为主；无有效答案时：选择题随机补、开放题记错。
- 指标：**micro-averaged accuracy**；用正则从长回答抽最终答案。
- 对照：**Random Choice / Frequent Choice**；**人类**：90 名高年级本科（每科 3 人）做 Val 900 题，可用课本、禁搜网。
- 文本-only：GPT-4、Llama2-7B、FLAN-T5-XXL、Vicuna-13B；另测 **+OCR（MMOCR）** / **+LLaVA-1.5 caption** 是否抬分。

### 3.4 关键结果（Table 2，锚定 PDF）

| 系统 | Val Overall (900) | Test Overall (10,500) |
|---|---|---|
| Random / Frequent | 22.1 / 26.8 | 23.9 / 25.8 |
| Human Expert Worst / Med / Best | **76.2 / 82.6 / 88.6** | — |
| GPT-4V (Playground) | 56.8 | **55.7** |
| GPT-4 Text（无图） | 34.9 | **33.8** |
| FLAN-T5-XXL / +OCR / +Caption | 32.1 / 34.7 / 34.8 | 31.2 / 31.9 / 31.9 |
| Vicuna-13B / +OCR / +Caption | 33.3 / 35.4 / 33.9 | 31.0 / 31.9 / 32.7 |
| 投稿期开源前列（BLIP-2 / LLaVA-1.5 量级） | ~34–36 Val | test 约 **34** |
| 后期作者更新*（表内） | GPT-4o Val **69.1**；Gemini 1.5 Pro **62.2**；Claude 3 Opus **59.4** | — |

\* 表注：带 `*` 为作者提供后续结果；**引用时写清 checkpoint / 日期**，勿与初版 GPT-4V 混写。

**跟读结论（MMMU 自身）：**
1. 相对人类 Best **88.6%**，当时最强 LMM 仍有大缺口。
2. **OCR/Caption 外挂对文本 LLM 抬分有限** → 作者解读为需要更深的图文联合解释（非「把图变成字就够」）。
3. Art & Design / Humanities 相对高；Business / Science / Medicine / Tech 更低（复杂图 + 重推理）。
4. 难度分层（Table 3）：GPT-4V Easy **76.1** → Medium **55.6** → Hard **31.2**；Hard 上优势几乎消失。
5. GPT-4V 150 例错误分布（Fig. 5）：**感知 35% / 缺知识 29% / 推理 26%**（另有拒答、标注等小类）。

**但：文本捷径的伏笔已埋下。** Table 2 里文本-only 整体远低于 LMM，**并不**等于「每道题都视觉必要」——MMMU-Pro 正是针对后一漏洞。

---

## 四、MMMU-Pro：三步把「可被文本啃」压成「必须看」

### 4.1 诊断：两类捷径（§2.1）

作者观察强 MLLM（如 GPT-4o）在原版 MMMU 已很高（文引 Val **69.1%**），追问：分数是真理解，还是捷径？识别两类问题：

| 类型 | 含义 | 文内例（Fig. 2，Llama-3-70B Instruct 无图答对） |
|---|---|---|
| **Text-Only Dependency** | 题与图弱相关 / 图对解题非必要 | 依赖先验知识答「Grange 支持谁」类题 |
| **Shortcut Exploitation** | 对人需要看图，但选项/题干相关让模型靠预训练相关答对 | 噬菌体感染阶段排序：模型承认未见图仍选标准顺序 (A) |

### 4.2 三步构造（Fig. 1 / §2.2）

| 步 | 操作 | 产出 |
|---|---|---|
| **(1) LLM Filtering** | 四强开源文本 LLM（**Llama3-70B-Instruct、Qwen2-72B-Instruct、Yi-1.5-34B-Chat、Mixtral-8×22B-Instruct**）无图答题；每模 **10** 次；单模「可答」= 正确 **>5** 次；若 **≥3/4** 模多数可答 → 剔除 | 从剩余池按 30 科均匀抽 **1800**（每科 60） |
| **(2) Option Augmentation** | 选项 **4 → 10**；GPT-4o 生成、Claude 3.5 过滤、**两轮人工**审；并复核图文相关性，再滤 **70** 题 | **1730** 标准题 |
| **(3) Vision-only** | 人工在模拟显示环境拍照/截图；变背景、字体、字号；**无显式文本通道**（题干+选项都在图里） | 另 **1730** Vision 题；合计 **3,460** |

> 注：部分 PDF 双栏抽取在 Mixtral 行旁出现 `(gpt-4o)` 碎片，属排版串行；四模名单以 Fig. 3 横轴标签为准。

**Fig. 3 主张：** Filtering + 扩选项后，文本-only LLM 准确率显著下降（图示 Original → w/ Filtering → w/ Option Augmentation 三柱）。

### 4.3 评分协议（§3.1）

三种设定：
1. Standard，通常 **4** 选项（对照）；
2. Standard，通常 **10** 选项；
3. **Vision-only**。

**MMMU-Pro overall = 设定 (2) 与 (3) 的平均。** 设定 (1) 与原 MMMU Val 只作对照。Direct / CoT 均测，总表取较高者。

**人类专家：** 未重做全量专家标注；用原 MMMU 人类表现 **近似**（理由：题干难度核心不变；原评测要求写出解题过程；Vision 对人整合图文负担假设相近）。近似后 Human High：10-opt / Vision 约 **85.4%**（相对原 Val 88.6 略降）。

### 4.4 主结果（ACL Table 1，摘关键行）

记 **∆1** = Standard(10) − MMMU(Val)；**∆2** = Vision − MMMU(Val)。

| 模型 | Std 4 | Std 10 | Vision | MMMU Val | ∆1 | ∆2 |
|---|---|---|---|---|---|---|
| GPT-4o (0513) | 64.7 | **54.0** | **49.7** | 69.1 | −15.1 | −19.4 |
| Claude 3.5 Sonnet | 63.7 | 55.0 | 48.0 | 68.3 | −13.3 | −20.3 |
| Gemini 1.5 Pro (0801) | 60.6 | 49.4 | 44.4 | 65.8 | −16.4 | −21.4 |
| Qwen2-VL-72B | 59.3 | 49.2 | 43.3 | 64.5 | −15.3 | −21.2 |
| LLaVA-OneVision-72B | 52.3 | 38.0 | **24.0** | 56.8 | −18.8 | −32.8 |
| VILA-1.5-40B | 46.8 | 35.9 | **14.1** | 51.9 | −16.0 | −37.8 |
| Random (10-opt / Vision) | 24.9 | 12.8 | 12.4 | 22.1 | −9.3 | −9.7 |

**摘要句（与 Abstract 对齐）：** 相对原 MMMU，模型掉分约 **16.8%–26.9%**（文举例：Claude 3.5 **−16.8**、Gemini 1.5 Pro (0801) **−18.9**、VILA-1.5-40B **−26.9**——此处百分比点相对 Val 的综合落差叙述）。扩选项 alone 已让 GPT-4o 从 4-opt **64.7** → 10-opt **54.0**（−10.7）；Vision 再相对 10-opt 降 **4.3**（→49.7）。部分开源在 Vision 上崩塌式下跌（OneVision-72B 10-opt→Vision **−14.0**）。

### 4.5 CoT 与 OCR（§3.3–3.4）

| 旋钮 | 文内结论 |
|---|---|
| **CoT** | 两设定上总体有益，幅度模型相关。例：Claude 3.5 Standard Direct **42.7 → CoT 55.0**；学科上 Tech/Science 增益大（GPT-4o Tech **+14.49**、Science **+8.22**），Art & Design 弱或负（OneVision-72B Art **−17.12**） |
| **显式 OCR prompt** | Vision 上对多数模型 **几乎无显著改变**；OCR Acc 可很高（如 GPT-4o **89.7**）但 Vision Acc 仍低（**44.4** w/ OCR vs **43.6** w/o）→ **「认得字 ≠ 会做题」** |
| **响应长度** | Vision 下 GPT-4o 更短，且更多「Descriptive」、更少「Analytical」（Fig. 8）——作者解读为视觉认知负荷挤压推理链 |

### 4.6 错误分布漂移（§3.6，60 例 GPT-4o Vision）

| 类别 | MMMU（150 例 GPT-4V） | MMMU-Pro Vision（60 例 GPT-4o） |
|---|---|---|
| Reasoning | **26%** | **46%** |
| Perception | **35%** | **27%**（且 OCR Error **0%**） |
| Lack of Knowledge | **29%** | **25%** |

**跟读：** 滤捷径 + 嵌字入图之后，瓶颈从「看不清/缺知识」更推向 **跨模态整合后的推理失败**；纯 OCR 不是主瓶颈。

### 4.7 对训练的提示（§4，只记评测含义，不展开配方）

文建议方向（本篇只作「评测暴露的缺口」索引）：放大 LLM backbone；更强视觉表示（附录 Cambrian 上 DINOv2 在 Pro Vision 优于偏语言监督的 SigLIP：**17.4 vs 16.7**，而 Val 上 SigLIP 略高）；更好的图文融合；推理向 CoT 数据——**此处不展开训练细节，避免滑回 [[多模态架构脉络]]**。

---

## 五、评测史含义：从「有图的考卷」到「视觉通道不可旁路」

### 5.1 一条可记忆的因果链

`
MMMU 抬高学科与图像异构门槛
 → 但仍含「无图可解 / 选项相关可蒙」子集
MMMU-Pro 显式对抗文本捷径
 → 扩选项压缩随机与相关蒙题
 → Vision-only 取消干净文本通道（逼近用户截图习惯）
结果：榜分普降，错误类型更偏推理；OCR 够用仍不够聪明
`

### 5.2 对「架构思想」的最小含义（辅线）

- **外挂 OCR/Caption ≠ 多模态专家推理**（MMMU 已示；Pro 的高 OCR Acc + 低 Vision Acc 再钉死）。
- **输入协议是能力定义的一部分**：同样权重，4-opt / 10-opt / Vision 是三个不同任务。
- **捷径滤题改变排名**（Table 1 箭头）：部分模型 ∆2 排名升降显著（如 VILA Vision 大跌、个别小模型相对位次变化）——引用「谁第一」必须声明设定。

### 5.3 引用分数前的协议核对清单（对接 [[评测与排行榜可靠性]]，不重写其全文）

写笔记或对外引用 MMMU 族分数时，至少能回答：

1. **题集版本**：MMMU Val/Test 还是 MMMU-Pro？Pro 的 Std-4 / Std-10 / Vision / overall？
2. **输入模态**：交错图文分离输入，还是截图一体？有无额外 OCR 文本？
3. **提示协议**：Direct 还是 CoT？是否取二者较高？
4. **模型身份**：名称 + checkpoint/日期（如 GPT-4o **0513**；Gemini 1.5 Pro **0801 vs 0523**）。
5. **人类对照**：Pro 人类是 **近似** 还是新标注？
6. **是否 live 榜**：官网 leaderboard 可能新于 PDF Table——并列注明来源，不静默混用。

---

## 六、常见误区

1. **「MMMU 文本-only 低 ⇒ 每题都视觉必要」** — 错；Pro 正是拆穿子集捷径。
2. **「Pro 掉分 = 模型变差」** — 多为 **评测变严**；应报告 ∆ 与设定。
3. **「Vision 设定在测 OCR」** — 文明示 OCR Acc 高仍可能 Vision Acc 低；测的是 **看+读+学科推理** 的联合。
4. **「用 Pro 分数直接对比未声明 4-opt 的旧 MMMU 截图」** — 协议不可比。
5. **「重写 CLIP/LLaVA 来解释 Pro」** — 越界；训练配方归 [[多模态架构脉络]]，本篇停在评测字段。
6. **「把 [[评测与排行榜可靠性]] 污染/thinking 元规则整章贴进本篇」** — 越界；只保留清单接口。

---

## 七、未写入定论 / 待核实

1. **官网 live leaderboard 当期数字** — 滚动；本笔记不从记忆补表。
2. **Mixtral 过滤行旁 PDF 串行碎片** — 已按 Fig. 3 四模名单采信；若需法律级引用请对官方 PDF 目视该段。
3. **Pro 人类近似的置信区间** — 文称成本原因未重做全量专家评；引用时标明 *approximated*。
4. **与 MathVista / GAIA 等邻榜的系统对齐实验** — 原文 related work 提及差异，本篇不展开横向重跑。

---

## 附录 A：本地文件

| 文件 | 说明 |
|---|---|
| https://arxiv.org/abs/2311.16502 | MMMU v4 |
| https://arxiv.org/abs/2409.02813 | MMMU-Pro arXiv v3 |
| https://aclanthology.org/2025.acl-long.736/ | ACL 2025 Long 相机就绪 |
| `*.txt` | |

## 附录 B：与议程承诺对照

| 议程要求 | 本篇处置 |
|---|---|
| 「文本捷径 → 视觉必要」评测史 | §二口诀 + §四三步 + §五因果链 |
| 禁止重写 CLIP/LLaVA | §二划界；§4.7 只列缺口方向 |
| 勿重写 [[评测与排行榜可靠性]] 榜单元规则全文 | §5.3 仅核对清单 |
| 禁编造 | 数字均挂 Table/节号；live 榜不填 |

---

*草稿状态：draft。修订时优先同步 ACL/PDF changelog 与官网 leaderboard 协议变更。*

## 相关笔记

- [[恶意软件分析评测|Malware Analysis Evals]]
- [[LLM水印|LLM Watermarking]]
- [[持续学习|Continual Learning LLM]]
- [[SelfRAG与CorrectiveRAG|Self-RAG / CRAG]]
- [[MMMU多模态推理基准|MMMU-Pro]]

