---
title: "辅导/教学 Agent 评测：MathTutorBench + TutorBench + TeachArena（≠ LearnLM）"
topic: 辅导教学Agent评测
date: 2026-09-22
lines: [评测字段, 任务设计]
status: archived
sources:
 - https://arxiv.org/abs/2502.18940
 - https://arxiv.org/abs/2510.02663
 - https://arxiv.org/abs/2605.14322
aux:
 - https://github.com/eth-lre/mathtutorbench
 - https://huggingface.co/datasets/tutorbench/tutorbench
arxiv: ["2502.18940", "2510.02663", "2605.14322"]
related: ["LearnLM教育辅导", "合成用户仿真", "评测与排行榜可靠性", "评测污染可靠性鸿沟", "智能体工具与长程任务", "Inspect评测Harness"]
retrieval_cutoff: 2026-09-29
timezone: Asia/Shanghai (CST)
---

# 辅导/教学 Agent 评测：MathTutorBench + TutorBench + TeachArena（≠ LearnLM）

> **主要来源**：[MathTutorBench（Macina et al., ETH Zurich / UKP Darmstadt）](https://arxiv.org/abs/2502.18940)；[TutorBench（Srinivasa et al., Scale AI）](https://arxiv.org/abs/2510.02663)；[TeachArena：*Are Agents Ready to Teach? A Multi-Stage Benchmark for Real-World Teaching Workflows*（Chen et al., HKUST + Qwen Team）](https://arxiv.org/abs/2605.14322)（TeachArena 按 2026-09-29 的 v4 核对，其余截至 2026-09-22）
> **研究线**：评测字段 / 任务设计——辅导 Agent 评什么对象、以什么为证据、怎样自动打分。
> **范围与相邻笔记**：
> - ≠ [[LearnLM教育辅导]]：本篇不写教学法对齐的训练配方（pedagogical IF 共训、SFT/RM/RL 进 Gemini）。
> - ≠ [[合成用户仿真]]：本篇不写 τ-bench / ToolEmu 的用户与工具仿真协议。
> - ≠ [[评测与排行榜可靠性]]：本篇不写污染、路由、thinking 配置等榜单可靠性问题。
> - ≠ [[Inspect评测Harness]]：本篇不写评测运行时的 Task / Solver / Scorer 原语。
>
> **意义**：三篇基准把「会做题」「会辅导」「会在教学系统里把干预做完」拆成三层可自动打分的证据，并显示这三层上的模型排名并不一致——辅导能力不能用解题分或单一总分代替。

**一句话**：MathTutorBench 用教学法偏好奖励模型给开放脚手架打分；TutorBench 用样本专属量尺给多模态辅导打分；TeachArena 把教师判断、多轮辅导与 LMS 动作拆成三面分别审计，暴露出「知道—会教—会做」之间的排名重排。

---

## 一、问题背景

学生把 LLM 当学习助手已很普遍（TutorBench Abstract），但多数基准量的是知识与推理，而不是辅导技能本身。辅导评测有三个与普通问答评测不同的难点：

1. **开放生成没有标准答案**。一句好的教师话语可以有很多写法，词重叠指标（BLEU 等）抓不住「是否泄题、是否在引导学生自己想」；人工评分贵，也无法对未来模型复用（MathTutorBench §1）。
2. **好的辅导常常与通用「有用性」偏好相反**。替学生直接算出答案容易被当作「有用」，在教学法上却剥夺了学生自己推理的机会。MathTutorBench 的奖励模型实验发现，通用奖励模型在「专家 vs 新手教师」判别上只略好于随机。
3. **证据跨越多轮与系统状态**。真正的教学结果体现在学习者自己说出的关键推理、以及教师在学习管理系统（LMS）里留下的成绩、消息和测验上，单轮回答看不到这些（TeachArena §1）。

## 二、脉络

| 时间 | 基准 | 评测对象 | 自动打分方式 | 相对前作补了什么 |
|---|---|---|---|---|
| 2025-02 | MathTutorBench | 数学对话中的教师话语 + 诊断子任务 | 分类指标 + 教学法奖励模型 | 把 Bridge / MathDial 对话与 StepVerify 错误标注整合成七任务，开放生成用小 RM 打分 |
| 2025-10 | TutorBench | 高中 / AP 六科 STEM 的单段辅导回应 | 样本专属量尺 + LLM 评审 | 既有辅导基准多为单科纯文本且接近满分；改为多学科、多模态，并按难度过滤 |
| 2026-05 | TeachArena | 教师判断 / 多轮辅导轨迹 / LMS 工作流 | 匹配验证器（语义、程序、过程、目标状态、产物质量） | 把前两类视为「局部辅导回应」，补上多轮情境与制度动作 |

几条承接关系：

- MathTutorBench 之前的开放评测主要是逐准则二分类（如 MRBench 的 8 条准则），MathTutorBench 认为这种做法稀疏且噪声大，转向成对偏好 RM。
- TeachArena §2 明确把 MathTutorBench、TutorBench 与 LearnLM 的评测归到「局部辅导回应」一侧；其 Stage 1 有 17 题由 MathTutorBench 变换而来（TeachArena §3），两者有构造上的承接。
- TeachArena §2 的 Table 1 还对照了 τ-bench、TheAgentCompany、Toolathlon：这些通用 Agent 基准有工具与状态，但成功标准不问动作是否有教学证据支撑。

## 三、MathTutorBench：拆开「会算」与「会教」

### 3.1 三技能轴与七任务

| 技能轴 | 任务 | 数据来源 |
|---|---|---|
| Math Expertise | Problem Solving；Socratic Questioning | GSM8k |
| Student Understanding | Solution Correctness；Mistake Location；Mistake Correction | StepVerify |
| Pedagogy | Scaffolding Generation（含 hard 长对话变体）；Pedagogical Instruction Following | MathDialBridge（Bridge + MathDial） |

学习科学原则取四条：正确、以脚手架代替给答案、鼓励自我纠正、不让学生过载（MathTutorBench §3.2）。Ped. IF 任务直接复用 LearnLM 的 extended prompt，作为教学法指令遵循的压力测试。

### 3.2 关键机制：教学法偏好奖励模型

开放的教师话语用成对偏好 RM 打分：在教学法偏好对上微调 Qwen2.5-1.5B-Instruct，在 Bridge 独立测试集上判别「专家回应 > 新手回应」的准确率为 **0.84**（MathTutorBench Table 3）。对照组中，加了扩展 prompt 的 LLM 评审仍 **<0.7**，通用 RM 只略好于随机——论文的结论是**通用人类偏好 ≠ 教学法偏好**。

最终指标是 win rate：RM 偏好模型回应胜过教师参考回应的比例。

### 3.3 主要发现（§6.1 与 Table 4）

- **专长不会自动变成教学法**：Qwen2.5-Math-7B 解题 **0.88**，脚手架 win rate 仅 **0.06**。
- **辅导专科模型有偏科**：SocraticLM 脚手架高于基座，但 Solution Correctness 跌到 **0.05**。
- **指令遵循能补一部分**：GPT-4o 的 Ped. IF 为 **0.82**，明显高于其脚手架分 **0.50**；多数开源模型的 IF 增益有限。
- LearnLM-1.5-Pro 各轴较均衡，论文称只有它在 hard 长对话上保持稳定；整体上对话越长分数越低。

## 四、TutorBench：样本专属量尺 + 难度过滤

### 4.1 构造

- **规模**：1,490 个样本，覆盖生物、物理、化学、统计、微积分、计算机六科；其中 828 个附有学生手写或截图作业。
- **样本专属量尺**：每个样本 3–39 条评分准则，全集 15,220 条；准则带权重 {-5, 1, 5}，例如「直接泄露答案」记 -5。
- **难度过滤**：五个强模型作答，至少三个得分 <50% 的样本才保留，使榜单远离饱和。
- **评审**：Claude Sonnet 4 按准则判分；在 250 个样本的三人标注上，评审与多数票的 F1 为 **0.81**。

三类用例对应三种辅导动作：Adaptive Explanation（针对追问暴露的知识缺口再讲解）、Assessment and Feedback（诊断学生的错误推理并给纠正性反馈）、Active Learning Support（给提示而不直接给最终答案）。

### 4.2 结果（Table 1 与 §3.2）

- 最高分 Gemini 2.5 Pro **55.65%**、GPT-5 **55.33%**；前沿模型在「引导、诊断、支持」类技能准则上的通过率都 **<60%**。
- 三类用例均值分别为 47.16% / 51.56% / 54.07%；Claude 系在 Active Learning 上更强，但总分落后于 Gemini / GPT 系。
- OpenAI study mode 得分 **46.94%**，论文归因于回答偏短、主动征询用户输入导致中断等；它是带系统指令的产品形态，不能当作 API 公平对照。

## 五、TeachArena：判断—辅导—行动三面

### 5.1 构造

| 面 | 任务数 | 环境 | 主要验证对象 |
|---|---|---|---|
| Stage 1 教学判断 | 117 | 打包好的证据，冻结检索与工具 | 诊断、先修、形成性评价决策是否有依据 |
| Stage 2 情境辅导 | 100 | 六种画像的受控学习者模拟器，13 个学科 | 每轮策略、整段轨迹、学习者产出 |
| Stage 3 LMS 工作流 | 137 | 合成的 Canvas 风格 LMS | 消息、成绩、测验、材料等持久状态变更 |

合计 354 个审计任务，以 Danielson 框架的六项教师工作能力贯穿（TeachArena §1）。构造采用 insight-first：先定一个教学洞见，再落到证据与匹配的验证器；Stage 3 的每个任务还至少埋一条「能执行但教育上无效」的诱导路径（TeachArena §3）。

### 5.2 结果（TeachArena §4 Table 6 与附录 E）

- **有界判断已偏高**：Stage 1 均值 **0.893**；工作流最高只有 **0.704**（Claude Opus 4.8 的 Stage 3），该模型 Overall 为 **0.803**，排第一。
- **三面排名不一致**：排名相关系数 ρ 在 Stage 2–1 为 **0.24**、Stage 2–3 为 **0.21**、Stage 1–3 为 **0.58**；单个模型最好与最差面的排名差中位数为 **7** 位。典型如 Gemini-2.5-Pro，Stage 2 排第 2，Stage 3 排第 12。
- **两种压力最伤**：面对索要捷径的「策略性浅层学习者」，均值 **0.702** vs 其他画像 **0.757**；6 个长链工作流任务均值 **0.321** vs 其他 Stage 3 任务 **0.559**。论文称两项都只是描述性对比，不指认链长或某个接口为原因。

## 六、三基准的设计差异与教学评测难点

| 维度 | MathTutorBench | TutorBench | TeachArena |
|---|---|---|---|
| 证据单位 | 单轮教师话语 + 诊断子任务 | 单段辅导回应（带多轮上下文） | 判断 / 辅导轨迹 / LMS 状态 |
| 领域与模态 | 中学数学，纯文本 | 六科 STEM，828 张作业图 | 多学科，Stage 3 含材料与幻灯片产物 |
| 打分契约 | 教学法 RM 的成对偏好 | 每样本专属准则 + LLM 评审 | 每任务匹配的多类验证器 |
| 饱和情况 | 解题高、教学法低 | 总分 <56% | Stage 1 高，Stage 3 与长链低 |
| 开放程度 | 代码与数据公开 | 只公开 30 样本预览 | 代码数据在 Hugging Face |

三篇合起来指向的共同难点：

1. **评审本身要懂教学法**：通用 RM 和通用评审会偏好「直接给答案」，所以三篇分别用专门训练的 RM、带负权重的样本准则、以及按洞见设计的验证器来对冲。
2. **不能只报总分**：MathTutorBench 的解题与脚手架、TeachArena 的三面都出现明显背离，总分会把这些背离抹平。
3. **离学习收益还隔一层**：三篇都只量辅导行为，不量学生是否真的学会。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[LearnLM教育辅导]] | LearnLM 是训练侧的教学法对齐工作，本篇是它的评测侧；只取它作为被测模型的成绩与被复用的 Ped. IF prompt | 教学法后训练配方、Gemini 模型卡 |
| [[合成用户仿真]] | TeachArena Stage 2 的学习者模拟器是合成用户思路在教学场景的应用；只取「学习者画像 + 轨迹打分」契约 | τ-bench / ToolEmu 的用户策略与风险仿真 |
| [[评测与排行榜可靠性]] | 评审漂移、只报总分的风险是该篇通用问题在辅导评测里的具体表现 | 榜单可靠性的一般讨论 |
| [[评测污染可靠性鸿沟]] | MathTutorBench 承认 GSM8k 解题已饱和或受污染，只把它作「专长—教学法平衡」指示器；污染本身见该篇 | 污染检测方法 |
| [[Inspect评测Harness]] | 三篇是领域基准，若要统一复跑需要该篇那样的运行时承载 | 评测框架原语 |
| [[智能体工具与长程任务]] | TeachArena Stage 3 是长程工具任务的一个教学领域实例 | 通用工具环与长程任务史 |

## 八、局限与待核实

1. **不等于学习收益**：MathTutorBench 结论称目标不是替代测量学习成效的人类研究；TutorBench 未讨论学习成效，只评对预设对话的最终回应（§5）；TeachArena §7 只说未来应连到纵向学习成效。MathTutorBench 限于高中多步数学题、对话不超过 10 轮（Limitations），并提示模型可能针对其教学法奖励模型做 reward hacking（Accessibility and Potential Misuse 段）。
2. **评审漂移未测**：TutorBench 固定 Claude Sonnet 4 作评审，论文未给换评审家族后的全表；复现时需固定评审版本。
3. **TutorBench 完整数据未发布**：截至 2026-09-22 仍只有 Hugging Face 上 30 个样本的预览，榜单数字以论文 Table 1 为准，不宜用子集外推。
4. **TeachArena 数据入口不完整**：论文称代码与数据都在 Hugging Face，附录 D 给出 commit `cbd99fcca76b`，但没有印出完整仓库名。
5. **TeachArena 版本变动**：本篇按 v4（2026-09-29）核对；v4 相对 v3 只把题名从 *TeachArena: Are Language Agents Ready for Realistic Teaching Work?* 改回 v1、v2 用过的现题名，摘要、正文与各表数字逐词一致，0.704 等数字在两版中同样见于 §1 与 §4 Table 6。
6. **LearnLM 的相对表现不宜归因**：TeachArena 点到 Gemini 在 Stage 2 相对强，但论文本身说不宜归因到专有训练（TeachArena §4）。

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [MathTutorBench](https://arxiv.org/abs/2502.18940) §4–§6 | 七任务、教学法 RM 的训练与校准、Table 4 |
| 2 | [MathTutorBench 代码](https://github.com/eth-lre/mathtutorbench) | 任务实现与 RM 用法 |
| 3 | [TutorBench](https://arxiv.org/abs/2510.02663) §2–§3 | 样本专属量尺、难度过滤、三类用例结果 |
| 4 | [TutorBench 样本预览](https://huggingface.co/datasets/tutorbench/tutorbench) | 量尺与样本的实际格式 |
| 5 | [TeachArena](https://arxiv.org/abs/2605.14322) §3–§4 与附录 E | 三面构造、insight-first、Table 6 与排名重排分析 |
