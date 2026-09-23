---
title: "Education tutors：LearnLM 教学法对齐与辅导交互"
topic: LearnLM教育辅导
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - `https://arxiv.org/pdf/2412.16429`；
 - https://arxiv.org/abs/2407.12687
arxiv: ["2412.16429", "2407.12687"]
related: ["MedGemma医学专科", "对齐脉络RLHF与偏好优化", "B11"]
archived: 2026-09-22
---

# Education tutors：LearnLM（教学法对齐 / 辅导交互）

> **定位**：教育辅导主题轴 **可选短卡**——仓库此前无「教学法对齐 / 辅导交互」专科线。主文是 **LearnLM（2412.16429）**：把教育学行为改写成 **pedagogical instruction following（教学法系统指令遵循）**；对照早期评测驱动报告 **2407.12687**（LearnLM-Tutor / Gemini 1.0 微调）。
> **攻坚线**：**架构思想（主）**——不锁死单一教学法定义，而用 System Instructions 条件化辅导行为 + 与 Gemini 后训练共训；**评测字段（辅）**——场景化多轮辅导、教学法量尺、专家偏好。
> **硬划界**：
> - **禁止编造**：场景数、偏好强度、基准名、部署规模一律锚定官方 PDF（2026-09-22 CST）。
> - **禁止写成「AI 家教产品手册 / 替代教师操作指南」**；只记论文主张、管线与评测字段。
> - **不重写** [[对齐脉络RLHF与偏好优化]] RLHF 通史、`B11` Model Card 全文；本卡只取「教学法数据进后训练混合物 / 与 Gemini 对齐的安全评」接口。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文 · LearnLM** | LearnLM Team (Google), *LearnLM: Improving Gemini for Learning* | arXiv:**2412.16429v3** \[cs.CY\]（页眉 **2024-12-19**；`goo.gle/LearnLM-dec24`）；`https://arxiv.org/pdf/2412.16429`；（**35** 页 A4；约 28.7 MB） | 把教育学问题重述为 **pedagogical IF**；SFT + RLHF 共训进 Gemini；专家场景评测 vs GPT-4o / Claude 3.5 Sonnet / Gemini 1.5 Pro |
| **对照 · 早期报告** | Jurenka, Kunesch, McKee, Gillick et al. (Google DeepMind 等), *Towards Responsible Development of Generative AI for Education: An Evaluation-Driven Approach* | arXiv:**2407.12687v4** \[cs.CY\]（页眉 v1 **2024-05-14**；v2 **2025-11-28**）；`https://arxiv.org/abs/2407.12687`（**86** 页 A4；约 6.0 MB） | 参与式研发；**五条高阶教学法原则**；**七套**教育学基准 taxonomy；SFT 出 **LearnLM-Tutor（𝑀4，Gemini 1.0）**；ASU Study Hall / HallMate |

**一句话抓手：** 通用 LLM 默认「给信息」≠「会辅导」——早期报告用 **SFT 把教学法原则灌进 LearnLM-Tutor**；后续 LearnLM 改成 **让教师/开发者用 System Instructions 指定教学法**，并把教育学数据 **混进 Gemini 后训练**，用场景化专家偏好量「像不像好导师」。

---

## 二、议题边界：辅导交互专科，不是通用对齐通史

| 已入库 / 相邻 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[对齐脉络RLHF与偏好优化]]** RLHF / InstructGPT | LearnLM 用 **RM + RLHF** 跟「软」教学法指令；早期报告主路径是 **SFT** | RLHF 公式与偏好学习通史 |
| **B11** Model Card | LearnLM §4.1：安全评与 Gemini 1.5 对齐；早期报告另有教育专用安全数据 | 不替两文代写完整卡 |
| **[[MedGemma医学专科]]** MedGemma | 同属「域专科 + 不可夸大用途」自觉；Appendix C 医学教育可行性 | 临床影像 / clinical-grade |
| **通用 Chatbot「有帮助」** | 两文共识：默认 helpfulness 常与学习冲突（直接给作业答案） | 提示词工程产品清单 |

---

## 三、架构思想（主）：从「写死教学法」到「教学法指令遵循」

### 3.1 问题陈述（两文共识）

| 点 | 文内口径 |
|---|---|
| **默认行为错位** | 主文 Abstract：当今 gen AI **默认呈现信息**，而非像人类导师那样 **为学习而互动**。早期报告 §1：模型被训成「有帮助」，学生易直接拿到作业答案，产生 **虚假掌握感**。 |
| **教学法难统一定义** | 主文 §1 访谈结论 **(1)**：年级、学科、语言、文化、产品形态、教育哲学跨度大，理想 AI 导师行为 **甚至可能互相矛盾** → 宜由 **开发者/教师指定**。 |
| **立刻有用的能力** | 主文 §1 **(2)**：底层模型最常被点名的能力是 **按系统指令做互动式导师练习**，且学生试图绕过时仍遵守（例：「不要直接给答案」「保持主题」）。 |
| **逐应用后微调不划算** | 主文 §1 **(3)**：成本、维护、基座快速迭代 → 尽管有缺陷，**prompting 仍可能是 EdTech 指定行为的主路径**。 |

### 3.2 LearnLM 的 reframing：pedagogical instruction following

`
旧路径（早期报告） 新路径（LearnLM 主文）
 选定教学法原则 不承诺单一教学法定义
 → 合成/人工 SFT 对话 → 每条训练/评测样本带「本会话的教学法 System Instruction」
 → 专用 tutor 模型 → 与 Gemini 后训练混合物共训（SFT / RM / RL）
 → 提示调 Gemini 作对照 → 教师/开发者用指令指定行为；学生侧指令不得覆盖系统指令
`

**跟读口诀：** **别把「好导师」焊进权重人格；焊的是「听懂并遵守复杂教学法系统指令」。**

要点（主文 §2）：

1. **System Instructions vs User Instructions**（Gemini 区分）：系统指令优先于用户后续指令——对应「不要泄题」类硬约束。
2. **硬约束 vs 软约束**：例「不要揭示答案」vs「用激励语气」；教育学指令往往 **复杂、细腻、难程序化验证**。
3. **SFT 数据改造**：每段对话以 **不同的、具体的** 教学法系统指令开头；过泛指令会让模型学会 **忽略指令**。
4. **RLHF**：同样按「是否遵循该会话的教学法指令」标偏好 → 训 RM → RL；文内称对细腻、长对话上的指令遵循，**RL 明显比仅 SFT 更有效**。
5. **共训收益（§2.3）**：教育学行为常与「直接给答案」的对话 AI 习惯冲突；用系统指令 **条件化** 后，可与通用推理/多模态/事实性/安全数据并存，减轻遗忘，并便于与 Gemini 配方同步。文内：LearnLM 改进的一部分已进入 **Gemini 2.0**；实验模型可在 **Google AI Studio** 试用。

### 3.3 早期报告管线（对照，勿与主文混为同一模型）

早期报告在 **Gemini 1.0** 上经多代 SFT 得到 **LearnLM-Tutor = 𝑀4**（Table 1）：

| 数据切片 | 作用（文内） |
|---|---|
| Human tutoring | 真人师生聊天；质量不均、含跑题 |
| Gen AI role-play | 师生双角色 + 状态注入；人工过滤编辑 |
| GSM8k dialogue | Socratic 逐步解 → 对话化（dialogue in-painting） |
| Golden conversations | 教师按量尺手写/精修的高质量示范 |
| Safety | 教育学专用安全微调（§9.3） |

文内观察：更「人」的数据偏 **风格**（鼓励、停顿、主动引导）；更「合成」的数据偏 **实质缺口**（纠错等）。**全合成无人工** 或 **未筛选真人聊天** 都不够。

---

## 四、辅导交互：五条原则 × 场景化多轮

### 4.1 五条高阶教学法原则（早期报告 §4.3.1；主文量尺同族）

| 原则 | 文内压缩含义 |
|---|---|
| **Encourage active learning** | 学习者应讨论、练习、创造地 **操作信息**，而非被动吸收 |
| **Manage cognitive load** | 多模态呈现、结构良好、切成可管理块 |
| **Deepen metacognition** | 「关于思考的思考」，利于跨情境迁移 |
| **Motivate / stimulate curiosity** | 通向自我效能与终身学习 |
| **Adapt to learners’ goals and needs** | 评估现状与目标，并规划弥合差距 |

主文 Figure 5 专家量尺五类与上表对齐：**Manages cognitive load / Inspires active learning / Deepens metacognition / Stimulates curiosity / Adapts to learner**。文内称 LearnLM 在各类上平均最高，尤其在 **激发主动学习、加深元认知、刺激好奇** 上领先较大。

### 4.2 交互设计字段（主文场景模板）

场景不是「随便聊天」，而是可复现的多轮评测模板，典型字段包括：

- **Conversation plan**（学习者角色、具体问题、解题路径、互动方式）
- **Learner persona**（例：不展示步骤、易分心）
- **Initial learner query**
- **System Instructions**（本场景要求的教学法行为）
- **Grounding materials**（作业题、作文、图示等）

收集侧：参与者按场景 **角色扮演学习者**，与 **成对盲测** 的两套导师各聊至少 **10 轮**（至少各 5 个学习者/导师回合），再填体验与对比问卷。

### 4.3 定性主题：什么叫「像辅导」

主文对角色扮演学习者偏好解释做主题编码（Table 1 子样）。更常支持 LearnLM 的主题包括：

- **keeps_on_topic**（拉回主题）
- **challenges_learner**（推动思考而非一味附和）
- **gives_away_answers**（主题标签：相对更少直接泄答案、更走引导步骤；亦有「该给时太吝啬」的反例摘录）

更常支持对照模型的主题包括 **clarity / info_amount / conversation_style**（更清晰、信息量/简洁、语气风格）。跟读：**辅导 ≠ 更啰嗦或更讨好；核心是指令遵循 + 主动学习压力。**

---

## 五、评测字段（辅）：场景专家评 × 七套基准 taxonomy

### 5.1 LearnLM 主评测流水线（主文 §3–4）

| 阶段 | 内容 | 文内规模（以正文为准） |
|---|---|---|
| **场景库** | 三阶段：用例征集 → 模板 → 生成修订 | **49** 个核心学科场景；Appendix C 医学教育可行性 |
| **对话收集** | 教育学专家角色扮演学习者 | §3.2：**𝑁 = 168**（§3 总述另写 186——文内数字不一致，不擅自调和） |
| **教学法评估** | 另一批专家审成对对话 | §3.3：**𝑁 = 228**（§3 总述另写 248） |
| **语料合计** | 多轮对话 + 专家评估 | **2360** 段对话、**58 459** 条消息、**10 192** 次专家评估（平均每对约 3 人） |
| **统计** | 层级贝叶斯回归等 | Appendix B.8 |

**对照时点（文内点名，2024-10-01 前后旗舰）：** LearnLM（文内表：**2024-11-19**）vs GPT-4o（2024-08-06）/ Claude 3.5 Sonnet（2024-06-20）/ Gemini 1.5 Pro-002（2024-09-24）。作者强调 **时点比较**，其后各模型已更新。

**五维对比偏好（Figure 4）：** Better supported learning goal / Better adapted to learner / Better instruction following / More like a very good human tutor / Better pedagogy。

**摘要级平均偏好强度（Abstract，相对 LearnLM）：** **+31%** vs GPT-4o；**+11%** vs Claude 3.5 Sonnet；**+13%** vs 所基于的 Gemini 1.5 Pro。专家在「哪位导师辅导更好」上对 LearnLM 偏好最强。

### 5.2 早期报告：七套基准与 taxonomy（§4.3.2 / Figure 2）

文内称 **seven pedagogical benchmarks**，覆盖定量/定性、自动/人类；Figure 2 用 taxonomy 组织权衡，正文具名展开包括：

| 块 | 代表内容 |
|---|---|
| **人类 · 无引导** | §5.1 主观学习者反馈（约 45 分钟开放会话，接地 YouTube 学术视频） |
| **人类 · 回合级** | §5.2 教师回合级教学法评分 |
| **人类 · 会话级** | §5.3 会话级教学法 |
| **人类 · 并排** | §5.4 Side-by-side 教师偏好（Figure 1 所称 teacher preferences 之一） |
| **自动 · LME** | §6.1 Language Model Evaluations：按维度拆任务 + critic LLM（可给特权信息，如正确解） |
| **真实部署** | §7 ASU Study Hall：**HallMate** Chrome 扩展；CSE 110；访谈 𝑛=10 等（细节见该节） |
| **定向能力** | §8 evaluative practice、程序性作业反馈等（偏能力切片，服务研发） |

**LME 与五原则的例映射（Table 2）：** Stay on topic；Do not reveal the answer / guide towards the answer / promote active engagement；Identify misconceptions；Positive tone / affect cues；Adapt to learner’s level——文内明确 LME 是 **窄行为 spot check**，不能完整覆盖量尺。

**准确率护栏（早期报告 §4.1）：** 标准教育相关基准上 LearnLM-Tutor **复现** Gemini Pro 量级（例：MMLU **0.72**、MATH **0.33**）；开放接地对话的回合事实性上与 prompt-tuned Gemini 1.0 **无显著差**（Fully verified 约 **96%** vs **93%**，𝑝=0.13）。

### 5.3 安全与局限（两文）

- 主文 §4.1：安全/责任评与 Gemini 1.5 流程对齐，并叠加 **learning-specific model policy**；Model Card 指向 Gemini 1.5 报告附录。
- 早期报告：教育场景额外风险（有害请求上的不当表扬、拟人化等，Table 6–8 一类自动评）。
- 主文 §5 展望：从 **内在** 教学法量尺走向 **外在** 学习成效；量尺原则有学习科学依据，但 **不等价于已证明提分**。
- 角色扮演专家 ≠ 真实学生；早期报告亦强调 WEIRD 参与者局限与统计功效受限。

---

## 六、跟读清单（可核对）

1. **默认 helpful ≠ 教学法**：直接给答案会破坏练习——两文开篇同构。
2. **LearnLM 主创新**是 **pedagogical IF + 共训**，不是又一个「固定苏格拉底人格」。
3. **五原则**（主动学习 / 认知负荷 / 元认知 / 动机好奇 / 适应）是量尺骨架。
4. **评测**靠 **场景 + 系统指令 + grounding + 多轮 + 专家并排**，不是单轮 IQ 题。
5. **数字**：49 场景；偏好 +31%/+11%/+13%；2360 对话 / 10192 评估——写进笔记前再对 PDF。
6. **𝑀4 LearnLM-Tutor（Gemini 1.0 SFT）≠ 主文 LearnLM（Gemini 1.5 Pro 共训）**——称呼相近，代际不同。

---

## 七、待核实 / 不写

| 项 | 状态 |
|---|---|
| §3 总述 𝑁=186/248 与 §3.2–3.3 的 168/228 | **文内不一致**；本卡并列，不编造解释 |
| 「七套基准」的官方一览表全名 | 文内以 taxonomy + 分节给出；**未**在摘要中枚举七个专名 → 不臆造第七项名称 |
| Google AI Studio 上 LearnLM 实验模型 **当前是否仍挂牌** | 以主文主张为准；上线状态随产品变，**待产品页核实** |
| 学习成效 RCT / 长期提分 | 主文明确仍偏内在评测；**本卡不外推** |

## 相关笔记

- [[SHADEArena隐瞒与监控|SHADE-Arena]]
- [[天气气候基础模型|Weather / Climate FM]]
- [[QwenOmni音视频原生|Qwen Omni]]
- [[LearnLM教育辅导|LearnLM]]

