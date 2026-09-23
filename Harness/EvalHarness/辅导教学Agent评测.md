---
title: "辅导/教学 Agent 评测：MathTutorBench + TutorBench + TeachArena（≠ LearnLM）"
topic: 辅导教学Agent评测
date: 2026-09-22
lines: [评测字段, 任务设计]
status: archived
sources:
 - https://arxiv.org/abs/2502.18940 # 5.84MiB / 18p；≪10MB → 官方 HTTPS 外链
 - https://arxiv.org/abs/2510.02663 # 1.91MiB / 18p；≪10MB → 官方 HTTPS 外链
 - https://arxiv.org/abs/2605.14322 # 4.46MiB / 24p；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2502.18940
 - https://arxiv.org/pdf/2502.18940
 - https://arxiv.org/abs/2510.02663
 - https://arxiv.org/pdf/2510.02663
 - https://arxiv.org/abs/2605.14322
 - https://arxiv.org/pdf/2605.14322
 - https://github.com/eth-lre/mathtutorbench
 - https://huggingface.co/datasets/tutorbench/tutorbench
arxiv: ["2502.18940", "2510.02663", "2605.14322"]
related: ["LearnLM教育辅导", "合成用户仿真", "评测与排行榜可靠性", "评测污染可靠性鸿沟", "智能体工具与长程任务"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 辅导 / 教学 Agent 评测：MathTutorBench + TutorBench + TeachArena（≠ LearnLM）

> **定位**：辅导教学评测主题轴——仓库已有 **[[LearnLM教育辅导]]**（LearnLM **教学法对齐 / 模型侧** pedagogical IF）。本卡转问正交空位：**如何评测辅导 / 教学 Agent**。主锚三篇基准：
> - **MathTutorBench**（ETH 等）：开放式数学对话辅导能力（专业知识 × 学生理解 × 教学法生成）+ 轻量 Scaffolding RM。
> - **TutorBench**（Scale AI）：高中 / AP 六科 STEM、多模态、样本专属量尺（rubric）+ LLM-judge；三用例（自适应讲解 / 评估反馈 / 主动学习）。
> - **TeachArena**（HKUST + Qwen）：真实教学工作流三面——教师判断 → 情境多轮辅导 → LMS 端到端动作；354 审计任务。
> **攻坚线**：**评测字段 / 任务设计（主）**——评什么对象、证据单位、自动打分契约；**教学法原则对照（辅）**——仅作与 [[LearnLM教育辅导]] 原则表的接口对照，**不**重写 LearnLM 后训练配方。
> **硬划界（开篇钉死）**：
> - **≠ [[LearnLM教育辅导]]**：禁止写成 **LearnLM 第二张模型卡**。本卡**不**写 pedagogical IF 共训、SFT/RM/RL 进 Gemini、专家场景偏好对齐配方；LearnLM 仅在 MathTutorBench Table 4 / TeachArena 文内对照句 / TutorBench 相关工作中作为**被测或引用对象**出现。
> - **≠ [[合成用户仿真]]**：禁止重写 τ-bench / ToolEmu「合成用户 / 合成工具」仿真评测主轴。TeachArena 虽引用 τ-bench 作 agent 工作流对照，本卡只取 **教学证据 → 决策 → LMS 状态** 契约，不写零售/航空用户仿。
> - **≠ [[评测与排行榜可靠性]]**：禁止写成榜单污染 / thinking 模式 / 路由敏感性通史；三篇分数只作文内协议下的**转述**，不定外部聚合榜。
> - **≠ [[Inspect评测Harness]]**：禁止写成 Inspect Task/Solver/Scorer harness 运行时 API；本卡是 **领域基准任务设计**，不是评测框架原语。
> **禁止编造**：主张、实例数、表数字、RM 准确率、HF commit 一律锚定官方 PDF（2026-09-22 CST）。文内未给完整 HF repo slug / 未列表格的图柱读数 → **标待核实** 或不写。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **锚 1 · MathTutorBench** | Macina, Daheim, Hakimi, Kapur, Gurevych & Sachan, *MathTutorBench: A Benchmark for Measuring Open-ended Pedagogical Capabilities of LLM Tutors* | arXiv:**2502.18940**v2 \[cs.CL\]（页眉 **12 Oct 2025**）；ETH Zurich / UKP Darmstadt / ETH Learning Sciences；`https://arxiv.org/abs/2502.18940`（**5.84MiB**，6,120,260 B；**18** 页） | 数学对话辅导 **七任务 / 三技能轴**；开放生成用 **Scaffolding RM**（Qwen2.5-1.5B 微调，专家>新手 pairwise **0.84**） |
| **锚 2 · TutorBench** | Srinivasa, Che, Zhang et al. (Scale AI), *TutorBench: A Benchmark To Assess Tutoring Capabilities Of Large Language Models* | arXiv:**2510.02663**v1 \[cs.LG\]（页眉 **3 Oct 2025**）；Preprint；`https://arxiv.org/abs/2510.02663`（**1.91MiB**，1,998,643 B；**18** 页） | **1,490** 样本；六科 STEM；**828** 含图；样本专属 rubric（共 **15,220** 条）+ Claude Sonnet 4 judge；顶分 **55.65%** |
| **锚 3 · TeachArena** | Chen, Liu, Sheng, Li, Tu, Deng, Shum, Liu & Qu, *TeachArena: Are Language Agents Ready for Realistic Teaching Work?* | arXiv:**2605.14322**v3 \[cs.AI\]（页眉 **2 Aug 2026**）；HKUST + Qwen Team；`https://arxiv.org/abs/2605.14322`（**4.46MiB**，4,679,430 B；**24** 页） | **354** 审计任务；Stage1 判断 / Stage2 情境辅导 / Stage3 LMS 工作流；17 模型；Overall 顶 **0.803**（Claude Opus 4.8） |

**代码 / 数据（文内明示）：**

| 论文 | 文内入口 |
|---|---|
| MathTutorBench | `https://github.com/eth-lre/mathtutorbench`；数据 CC-BY-4.0（Limitations 段） |
| TutorBench | 样本子集 `https://huggingface.co/datasets/tutorbench/tutorbench`（文内：30 样本预览；**全文「将很快发布」**，2026-09-22 抽取口径） |
| TeachArena | 脚注 2：「All code and data are available on Hugging Face」；Appendix E 钉 commit **`cbd99fcca76b`**；子集名 `stage1_pedagogical_judgment` / `stage0_situated_tutoring` / `stage2_teaching_workflows`。**完整 HF repo slug 文内未印出** → 入库时以 commit 钉为准，slug **待补** |

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2502.18940-mathtutorbench.pdf` | **5.84MiB**（6,120,260 B） | 18 | **官方 HTTPS 外链**（≪10MB；≪80 页） |
| `2510.02663-tutorbench.pdf` | **1.91MiB**（1,998,643 B） | 18 | **官方 HTTPS 外链** |
| `2605.14322-teacharena.pdf` | **4.46MiB**（4,679,430 B） | 24 | **官方 HTTPS 外链** |

**一句话抓手：** 「会做题」≠「会辅导」≠「会在 LMS 里把教学决策做完」——MathTutorBench 用轻量 RM 量开放脚手架；TutorBench 用样本专属量尺打多模态辅导；TeachArena 把教师判断、多轮政策与制度动作拆成可审计三面，并暴露 **knowing–teaching–acting** 排名重排。

---

## 二、议题边界：评测基准族 ≠ 模型对齐配方 / 仿真 harness / 榜通史

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **教学法对齐（模型侧）** | pedagogical IF、SFT/RM/RL 共训进 Gemini、专家场景偏好 | **[[LearnLM教育辅导]] LearnLM** | **否**（禁第二张模型卡） |
| **合成用户 / 工具仿真** | LM 仿用户策略一致性、ToolEmu 风险 | **[[合成用户仿真]]** | **否**（τ-bench 仅 TeachArena 相关工作点名） |
| **榜单可靠性通史** | 污染、路由、thinking 配置 | **[[评测与排行榜可靠性]]** | **否** |
| **开源评测运行时** | Inspect Task/Solver/Scorer/sandbox | **[[Inspect评测Harness]]** | **否** |
| **辅导 / 教学 Agent 评测契约** | 任务对象、证据单位、自动打分、工作流状态 | **本篇三锚** | **是** |

跟读直觉：[[LearnLM教育辅导]] 问「**怎么把教学法行为训进模型**」；本卡问「**训完 / 提示完之后，用什么基准量辅导 Agent 是否真的在教**」。同一教育域，**训练对象 vs 评测对象** 正交。

### 2.2 三锚彼此分工（本卡内部）

`
 辅导/教学评测横切
 │
 ┌─────────────┼─────────────────────────┐
 ▼ ▼ ▼
 MathTutorBench TutorBench TeachArena
 数学对话七任务 六科多模态+样本量尺 判断→辅导→LMS
 开放生成+RM 三用例 ARRw 354 审计任务
 (中学数学) (高中/AP STEM) (教师工作系统)
`

TeachArena Related Work 明确把 MathTutorBench / TutorBench / LearnLM 评测放在「局部辅导响应」一侧，并声称缺「教学系统」整段证据链——本卡承认该定位，**不**因此把前两篇写成过时废纸：它们仍是可跑、可复现的辅导能力切片。

---

## 三、MathTutorBench：数学开放教学法能力（锚 1）

### 3.1 问题与三技能轴

Abstract / §1：现有自动评测常靠词重叠或纯 QA，抓不住「何时不泄答案 / 苏格拉底提问 / 认知参与」；人工评贵且无法对未来模型复用。作者释放 **开源、易跑、整体** 的数学对话辅导基准。

三高阶技能（Figure 1 / §4；对齐 Bommasani 等「Expertise / Student Understanding / Pedagogical Abilities」口径）：

| 技能轴 | 测什么 | 任务数 |
|---|---|---|
| **Math Expertise** | 学科解题能力 | Problem Solving；Socratic Questioning |
| **Student Understanding** | 核验 / 定位 / 纠正学生错误 | Solution Correctness；Mistake Location；Mistake Correction |
| **Pedagogy（Teacher Response Generation）** | 开放脚手架生成 + 教学法指令遵循 | Scaffolding Gen.；Ped. IF；及 hard 变体 |

### 3.2 七任务与数据契约（Table 1）

| 任务 | Dataset | 类型 | 实例数 | 备注 |
|---|---|---|---|---|
| Problem Solving | GSM8k | generation | 1319 | CoT 数值答案准确率（文内承认饱和/污染，作 **专长–教学法平衡指示器**） |
| Socratic Questioning | GSM8k | generation | 1319 | 每步 $s_n$ 至少一引导问 $q_n$；metric **BLEU** |
| Solution Correctness | StepVerify | 平衡二分类 | 2004 | F1 |
| Mistake Location | StepVerify | 多分类 | 2004 | micro F1（首错步） |
| Mistake Correction | StepVerify | generation | 1002 | 条件于含错历史 $H$；avg turns **3.04** |
| Scaffolding Gen. | MathDialBridge | generation | 1150 | avg turns **3.08**；RM win rate |
| Scaffolding [hard] | MathDialBridge[hard] | generation | 327 | avg turns **5.78**；更长对话 |

数据源：问题主来自 **GSM8k**；对话来自 **Bridge**（新手教师片段 + 专家修订）与 **MathDial**（真人教师 × 模拟学生，约 2.9k）合并为 MathDialBridge；错误步标注来自 **StepVerify**。排除 NCTE（多人设）。

### 3.3 学习科学原则（§3.2；辅对照，非 LearnLM 配方）

1:1 多轮、主动学习脚手架。四条原则（文内）：**(a) correctness**；**(b) scaffolding instead of giving away the answer**；**(c) encourage self-correction**；**(d) not overload student**。Ped. IF 任务直接接入 LearnLM **extended** prompt（Jurenka et al. / Team et al. 引用）——本卡只记「**评测侧复用该 prompt 作指令遵循压力测试**」，不展开 [[LearnLM教育辅导]] 共训混合物。

### 3.4 Scaffolding Score：开放生成怎么自动打

开放教师话语无法靠参考句 BLEU。路径：

1. **Criteria-based**：每准则训二分类 $C_i$，求和为离散分（MRBench 8 准则等；文内称稀疏/噪声，整体落后）。
2. **Pairwise RM（主）**：在教学法偏好对上微调小 RM；最终选 **Qwen2.5-1.5B-Instruct** 微调模型，Bridge 独立测集（482 例）上专家>新手准确率 **0.84**（Table 3 最优行：`+ MathDial (8.1k)`）。
3. 对照：LLM-as-a-judge（Llama-3.1-70B / GPT-4o-mini / Prometheus-7b）扩展 prompt 后仍 **<0.7**；RewardBench 通用 RM 仅略好于随机——文内结论：**通用人类偏好 ≠ 教学法偏好**。

Win rate 定义（Table 4 注）：RM 更偏好 **模型响应** 相对 **教师参考响应** 的比率（非「越高越好无条件」；需与「专家>新手」校准实验分开读）。

### 3.5 主结果（Table 4 精选转述）

文内核心发现（§6.1）：

1. **专长不自动变成理解与教学法**：Qwen2.5-Math-7B Problem Solving **0.88**，但 scaff. win rate 仅 **0.06**。
2. **辅导专科模型**：SocraticLM 相对基座在脚手架上有提升，但 Student Understanding 多项崩（Solution Correctness **0.05**）。
3. **LearnLM-1.5-Pro** 在文内被描述为各技能更均衡；长对话（hard）上「Only LearnLM can keep consistent performance」——**仅作文内对照句**，不升为本卡训练主轴。
4. **GPT-4o** Ped. IF **0.82**（相对 scaff. **0.50** 大幅提升），显示强指令遵循；多数开源模型 IF 增益有限或持平。
5. **更长对话更难**：hard 列普遍掉分。

| Model（Table 4） | Prob. | Socratic | Sol.Corr | Mist.Loc | Mist.Corr | scaff. | ped.IF | hard | ped.IF hard |
|---|---|---|---|---|---|---|---|---|---|
| LLaMA3.1-70B-Instruct | 0.91 | 0.29 | 0.71 | 0.56 | 0.19 | 0.63 | 0.70 | 0.49 | 0.49 |
| GPT-4o | 0.90 | 0.48 | 0.67 | 0.37 | 0.84 | 0.50 | 0.82 | 0.46 | 0.70 |
| LearnLM-1.5-Pro | 0.94 | 0.32 | 0.75 | 0.57 | 0.74 | 0.64 | 0.68 | 0.66 | 0.67 |
| Qwen2.5-Math-7B-Instruct | 0.88 | 0.35 | 0.43 | 0.47 | 0.49 | 0.06 | 0.07 | 0.05 | 0.05 |
| Qwen2.5-7B-SocraticLM | 0.73 | 0.32 | 0.05 | 0.39 | 0.23 | 0.39 | 0.39 | 0.28 | 0.28 |

**跟读口诀：** 数学辅导评测要 **拆开**「会算」与「会教」；开放轮次用 **教学法偏好 RM**，不要拿通用 chat RM 顶替。

### 3.6 局限（文内）

不替代学习收益真人实验；中学数学 / 英语对话为主；RM 有 reward hacking 风险；未覆盖所有教学法维度与低参与学生等。

---

## 四、TutorBench：多模态样本量尺辅导评测（锚 2）

### 4.1 问题与规模

Abstract：学生把 LLM 当学习助手已成常态，但多数基准量「高阶知识/推理」，忽略适应、引导、诊断等辅导技能；既有辅导基准常单科、纯文本，且 SOTA 接近满分。

| 字段 | 文内口径 |
|---|---|
| 样本数 | **1,490**（学生人格–导师人格对话） |
| 学段 / 学科 | 高中 / AP；**6** STEM：Biology, Physics, Chemistry, Statistics, Calculus, Computer Science |
| 多模态 | **828** 含学生手写/打印/截图作业图 |
| Rubric | 每样本 **3–39** 条专属准则；全集 **15,220** 条 |
| 难度过滤 | 五模型（Gemini 2.5 Pro / Claude 3.7 Sonnet / Llama 4 Maverick / o3 / DeepSeek-R1）作答；**至少三模型 <50%** 才保留 → 顶分压到 **55.65%** |
| Judge | Claude Sonnet 4；权重 $\{-5,1,5\}$；归一化 $[0,1]$ |
| 人机对齐 | 250 样本 × 每准则 3 人评；LLM-judge vs 多数票 **F1=0.81**（优于中位人类） |

公开：HF 子集 `tutorbench/tutorbench`（文内 30 样本）；**完整集「will be released soon」**（2026-09-22 抽取仍为此口径）。

### 4.2 三用例（§2.1）

| Use case | 交互形态 | 测什么 |
|---|---|---|
| **Adaptive Explanation Generation** | 学生问 → 导师讲解 → 学生追问；模型针对追问中的知识缺口再讲 | 识别误解 + 个性化、聚焦讲解 |
| **Assessment and Feedback** | 学生给出（常含错）推理；模型评估并反馈 | 诊断错误推理 / 误解并纠正性反馈 |
| **Active Learning Support** | 学生卡在半解；模型给 hint/问题 | **不直接给最终答案**；脚手架与 agency |

Figure 1 例：统计题手写半解 +「给 hint 勿泄答案」系统提示；量尺含「直接泄露均值 2.74 → 权重 **-5**」类惩罚项。

### 4.3 量尺标签（细粒度分析用）

每条 rubric 打四类标签（§2.4）：

1. **Evaluation dimensions**：instruction following / style and tone / truthfulness / visual reasoning / visual perception / conciseness and relevance / student level calibration / emotional component
2. **Tutoring skills**：guiding questions / misconceptions / 识别对错步 / 例子类比 / 替代解法 / 定义定理 / step-by-step help
3. **Explicit vs Implicit**
4. **Objective vs Subjective**

Abstract 强调：前沿模型在与「引导、诊断、支持」相关的技能准则上 **通过率均 <60%**。

### 4.4 主结果（Table 1 精选）

最终分 = 各例加权 rubric 通过率 $ARR_w$ 的平均。

| Rank | Model | Text-Only (%) | Multimodal (%) | Overall (%) | CI |
|---|---|---|---|---|---|
| 1 | Gemini 2.5 Pro | 57.05 | 54.53 | **55.65** | ±1.11 |
| 2 | GPT-5 | 57.03 | 53.97 | **55.33** | ±1.02 |
| 3 | o3 Pro | 56.07 | 53.45 | 54.62 | ±1.02 |
| 6 | Claude Opus 4.1 (Thinking) | 51.65 | 50.08 | 50.78 | ±1.05 |
| 11 | Llama 4 Maverick | 39.54 | 40.73 | 40.20 | ±1.00 |
| 12 | GPT-4o | 39.10 | 33.74 | 36.12 | ±0.96 |
| — | gpt-oss-120b | 56.01 | N/A | N/A | ±1.49 |
| — | DeepSeek-R1 | 48.38 | N/A | N/A | ±1.50 |

用例均值（§3.2 文内）：Adaptive **47.16%**；Assessment **51.56%**；Active Learning **54.07%**。**Claude 系在 Active Learning 上明显更强**，但总体仍落后 Gemini/GPT 系（Figure 3 叙事）。

另评 OpenAI **study mode**（网站系统指令产品，非主榜）：**46.94 ± …**；文内归因含回答偏短、主动征求用户输入导致截断、忽略部分量尺——**不作 API 公平对照**。

**跟读口诀：** 未饱和 + 样本专属可核验量尺 + 多模态作业图，才是近窗「辅导能力」压力测试；总榜 <56% 说明空间大。

---

## 五、TeachArena：教学工作系统三面（锚 3）

### 5.1 问题重述

Introduction：教育 Agent 不能停在「答对题 / 调对 API」。需要：

1. **Stage 1 Pedagogical judgment**：从证据推断有依据的教学决策（诊断、先修、形成性评价）。
2. **Stage 2 Situated tutoring**：多轮轨迹上自适应脚手架；理解/迁移以**学习者产出关键推理**为准。
3. **Stage 3 LMS teaching workflows**：把教学决策落实为 Canvas 风格 LMS 中可验证的持久状态变更（消息、成绩、测验、材料）。

Danielson 六教师工作能力贯穿：DIAGNOSE / DESIGN / CREATE / TEACH / COMMUNICATE / EVALUATE。

### 5.2 规模与构造

| Stage | N | 证据 / 环境 | 验证器侧重 |
|---|---|---|---|
| 1 判断 | **117** | 打包证据在桌上；冻结检索/对话/工具 | 语义断言 117；程序化 response anchors 100 |
| 2 情境辅导 | **100** | 受控学习者模拟器（六画像）；13 学科 | turn policy / trajectory / learner outcome（transfer probe 记日志但 **榜权重 0**） |
| 3 LMS 工作流 | **137** | 合成 Canvas-style LMS：**126** 学习者、**432** 选课、**222** 作业记录、**1,058** 测验尝试、**13** 可编辑演示文稿 | Environment 137；semantic 137；process 123；goal state 87；artifact quality 83 |

合计 **354** 审计任务。构造：**insight-first**——先定教学洞见，再落到证据与匹配 verifier；每任务含至少一条「可执行但教育上无效」的引诱路径。

Stage 1 来源拆分（文内）：26 MathDial 变换；**17 MathTutorBench 变换**；22 OER/文献；52 作者证据契约——与本卡锚 1 **有构造血缘，无训练配方复述**。

### 5.3 Stage 2 / 3 压力条件（文内诊断）

| 压力 | 口径 | 数字 |
|---|---|---|
| **Strategic surface learner** | 互动但索要捷径/答案确认 | 15/17 模型在该画像最低；均值 **0.702** vs 其他画像 **0.757**（bootstrap 95% CI gap **0.033–0.078**） |
| **Long-chain workflows** | 跨接口长链 | 6 任务均值 **0.321** vs 其他 Stage3 家族 **0.559**（gap CI **0.170–0.302**） |

### 5.4 主结果（Table 6）

Overall = 三 stage 分数**不加权平均**（任务数不等不影响 headline）。

| # | Model | Stage1 | Stage2 | Stage3 | Overall |
|---|---|---|---|---|---|
| 1 | Claude Opus 4.8 | 0.930 | 0.773 | **0.704** | **0.803** |
| 2 | Claude Opus 4.6 | **0.947** | 0.763 | 0.661 | 0.791 |
| 3 | GPT-5.5-pro | 0.916 | 0.739 | 0.693 | 0.783 |
| 5 | Qwen3.7-Max | 0.914 | 0.766 | 0.580 | 0.753 |
| 12 | Gemini-2.5-pro | 0.867 | **0.769** | 0.477 | 0.704 |
| 14 | Kimi K2.6 | 0.901 | 0.761 | 0.395 | 0.686 |
| 17 | GPT-4.1 | 0.799 | 0.732 | 0.447 | 0.659 |

文内关键统计：Stage1 均值 **0.893**（范围 0.799–0.947）——**有界判断整体偏高**；Stage2–Stage1 Spearman **ρ=0.24**，Stage2–Stage3 **ρ=0.21**，Stage1–Stage3 **ρ=0.58**；模型「最好–最差 stage 排名」中位差 **7** 位。

典型重排：Gemini-2.5-Pro Stage2 第 2（0.769）但 Stage3 第 12（0.477）；GPT-5.5 Stage3 前列、Stage2 靠后。文内点到 LearnLM「教育向行为」与 Gemini Stage2 相对强、但 **禁止归因到专有训练**——本卡同样 **不**据此写 LearnLM 卡。

工作流分数上沿 **0.704**（Claude Opus 4.8 Stage3）——Abstract「workflow scores top out at 0.704」。

**跟读口诀：** 会答「下一步该教什么」≠ 会在多轮里护住 learner agency ≠ 会把干预写进正确 LMS 对象；**必须分 stage 报，禁止只看 Overall**。

### 5.5 与 [[合成用户仿真]] / 通用 Agent 榜的文内自划界

Table 1 定位：τ-bench / TheAgentCompany / Toolathlon 有工具与状态，但成功标准通常 **不问** 动作是否被教学证据 warrant。TeachArena Stage3 显式查 **evidence → decision → action → state** 连续性（错对象、错受众、先宣布后创建、用无关测验等均可本地失败）。

---

## 六、三锚横切对照（评测字段主表）

| 维度 | MathTutorBench | TutorBench | TeachArena |
|---|---|---|---|
| **评测对象** | 单轮/短对话教师话语 + 诊断子任务 | 单段（多轮上下文）辅导响应 | 判断 / 完整辅导轨迹 / LMS 工作流 |
| **领域** | 中学数学 | 高中/AP 六科 STEM | 多学科（STEM 偏重）；真实教师工作 |
| **模态** | 文本 | 文本 + **828** 图 | 文本；Stage3 含材料/幻灯等产物 |
| **自动打分** | 分类指标 + **教学法 RM** | **样本专属 rubric** + LLM-judge | 匹配 verifier（语义+程序+过程+目标态+产物质量） |
| **与 LearnLM 关系** | Ped. IF 复用 extended prompt；Table4 被测 | 相关工作引用 | 相关工作 + Gemini 行为点名；**非训练主文** |
| **饱和度** | 解题高、教学法低（贸易off） | Overall **<56%** | Stage1 高、Stage3/长链低 |
| **开源成熟度** | GitHub 全开 | HF 子集；全文待发 | HF commit 钉住；slug 文内未印 |

教学法原则对照（辅，点到即止 → [[LearnLM教育辅导]]）：

| 原则（跨文常见） | 本卡落点 |
|---|---|
| 不直接给答案 / 主动学习 | MathTutorBench scaff.；TutorBench Active Learning 负权重泄题；TeachArena Stage2 agency |
| 诊断误解 | Mistake Location；Assessment use case；Stage1 诊断家族 |
| 自适应脚手架 | hard 长对话；Adaptive Explanation；Stage2 轨迹政策 |
| 制度落地 | **仅 TeachArena Stage3** |

---

## 七、开放问题与跟读建议

1. **RM / LLM-judge 漂移**：MathTutorBench 已证通用 RM 失效；TutorBench 钉 Claude Sonnet 4——换 judge 家族是否重排？文内未做跨 judge 全表 → 复现时需固定版本。
2. **TutorBench 全文数据**：2026-09-22 抽取仍为「soon」；榜数字以论文 Table 1 为准，勿用 30 样本子集外推。
3. **TeachArena HF slug**：仅有 commit `cbd99fcca76b`；入库脚本需补全 repo 路径后再 `git checkout` 钉死。
4. **学习收益外环**：三文均声明不替代真人学习实验；与 [[LearnLM教育辅导]] 早期报告的课堂/Study Hall 线正交，本卡不并写。
5. **Agent 产品叙事**：勿滑入 [[智能体工具与长程任务]] MCP/长程 System Card；TeachArena 工具面是 **教学状态契约**，不是通用工具环通史。

---

## 八、本卡不写什么（再钉一次）

- LearnLM / Gemini 教育学后训练混合物、安全评与 Model Card 全文 → **[[LearnLM教育辅导]]**
- τ-bench 用户策略 / ToolEmu 对抗仿真协议 → **[[合成用户仿真]]**
- 污染检测、thinking 配置敏感性、第三方聚合榜定论 → **[[评测与排行榜可靠性]]**
- Inspect harness API → **[[Inspect评测Harness]]**
- 「如何做 AI 家教产品 / 替代教师操作手册」

---

## 九、来源与核验

- 官方 PDF：`https://arxiv.org/abs/2502.18940` · `2510.02663-tutorbench.pdf` · `2605.14322-teacharena.pdf`
- *.txt`（2026-09-22 CST）
- arXiv abs/pdf 链接见 YAML `aux`
- 代码/数据入口见 §一表；TeachArena 完整 HF slug **文内未给出** → 不编造

