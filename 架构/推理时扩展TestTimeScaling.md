---
title: 推理时计算 / test-time scaling / 链式推理前沿
topic: 推理时扩展TestTimeScaling
date: 2026-09-22
lines: [架构思想, 数学原理, AI Infra]
status: archived
archived: 2026-09-22
---

# 8：推理时计算 / test-time scaling / 链式推理前沿

> 攻坚线：**架构思想（主）** + **数学原理（辅）** + **AI Infra（辅）**
> 锚点材料：OpenAI *Introducing OpenAI o1-preview*（2024-09-12）；OpenAI *Learning to reason with LLMs*（2024-09-12）；OpenAI o1 System Card（arXiv:2412.16720，2024-12）；DeepSeek-R1（arXiv:2501.12948，2025-01）

---

## 一、势：为何 2024 下半年起「多想一会儿」成为主叙事

2020–2023 年行业主叙事几乎都在 **train-time scaling**：更大参数、更多 token、更多预训练 FLOPs（Kaplan / Chinchilla 等）。模型一旦训完，单次前向的能力曲线大致固定；想再涨分，主要靠更大预训练或更多 SFT/RLHF 数据。

2024 年 9 月 OpenAI 发布 o1-preview，公开把另一条轴推到台前：

> *「We have found that the performance of o1 consistently improves with more reinforcement learning (train-time compute) and with more time spent thinking (test-time compute).」*
> —— *Learning to reason with LLMs*

也就是说：**同一（或同一系列）模型，在推理期多花算力——生成更长的内部思维链、或对多条候选做选择/投票——准确率可继续平滑上升。** 预训练缩放并未消失，但「推理难题」上出现了可产品化的第二轴。

同期公开证据把「多想一会儿」从口号变成可复述数字：

| 任务 / 设定 | 公开数字（以官方页 / 论文为准） |
|---|---|
| IMO 资格考风格（介绍页） | GPT-4o 约 13%；reasoning 模型约 83%（*Introducing o1-preview*） |
| AIME 2024（Learning to reason） | GPT-4o pass@1 约 12%（1.8/15）；o1 单样本约 74%（11.1/15）；64 样本共识约 83%；用学习到的打分函数对 1000 样本重排约 93% |
| Codeforces（Learning to reason 附录表） | GPT-4o Elo 808（约 11 百分位）；o1 Elo 1673（约 89 百分位） |
| GPQA Diamond | o1 超过招募的 PhD 专家基线（官方表述：首个在该基准上超过这些专家的模型；并不等于「全面超过 PhD」） |

**为何此时成为主叙事（跟读直觉）：**

1. **预训练边际收益变贵**：再堆数量级 train FLOPs 成本陡峭；而推理难题上，把算力挪到「答这一题时多想」往往更划算。
2. **可验证任务刚好喂得动 RL**：竞赛数学、编程、STEM 选择题有明确对错，适合用结果奖励把「长思维」训出来（DeepSeek-R1 把这一点写得更直白）。
3. **产品形态天然是 latency/cost vs quality 旋钮**：思考深度可按请求调节，适合 API 计费与产品分层（见第四节）。
4. **安全叙事也跟着变**：System Card 强调 deliberative alignment——模型在回答前用 CoT「想一遍安全规则」；同时也承认更强推理带来新风险（CBRN / persuasion 等评为 Medium）。

一句话：**「多想一会儿」不是提示词技巧复活，而是把 search / reflection 写进训练目标，并在推理期显式花钱买准确率。**

---

## 二、架构思想：训练期 RL + 长思维链 + 推理期算力

### 2.1 共同骨架（o1 公开叙述 ∩ DeepSeek-R1）

两边公开叙述收敛到同一三角：

`
预训练底座
 ↓
大规模强化学习（鼓励「先想后答」）
 ↓
推理时生成长 Chain-of-Thought（可含自我纠正、换策略、验证）
 ↓
（可选）多采样 / 共识 / 打分重排 → 进一步花 test-time compute
`

OpenAI System Card（§2）原文级表述：

> o1 family *「is trained with reinforcement learning to perform complex reasoning」*；*「o1 thinks before it answers—it can produce a long chain of thought before responding」*；通过训练学会 *refine thinking、try different strategies、recognize mistakes*。

OpenAI 技术博文进一步强调：**大规模 RL 教模型如何用 CoT「productive 地想」**，且 train-time RL 与 test-time thinking 两条轴上性能都平滑改进；该路线的缩放约束「与预训练明显不同」（*Learning to reason*）。

### 2.2 OpenAI o1：公开说了什么、没说什么

**公开确认：**

- **训练范式**：大规模 RL + CoT 推理；安全侧引入 deliberative alignment（让模型在上下文中推理安全规范后再回答）（System Card §1）。
- **推理期行为**：隐藏原始 CoT；ChatGPT 展示的是 **模型生成的 CoT 摘要**（*Learning to reason*「Hiding the Chains of Thought」；System Card §4.3.2）。理由包括：监控潜力、用户体验、竞争因素；并称不宜把合规策略直接训进原始 CoT，以免破坏可监控性假设。
- **产品族**：o1-preview / o1 / o1-mini；o1-mini 更便宜、偏编程（介绍页称比 o1-preview 便宜约 80%）。
- **评测默认**：*Learning to reason* 写明除非另注，对 o1 使用 **maximal test-time compute** 设定。
- **额外 test-time 选择**：IOI 设定下，从大量候选提交中按公开测例、模型生成测例与学习到的打分函数选出 50 份；随机提交约 156 分，选择策略约 213 分；若放宽到每题 10,000 次提交，即使无选择策略也可超过金牌线（约 362 分）（*Learning to reason*）。

**公开未给出 / 应标「待核实」：**

- 具体 RL 算法名（是否 PPO/GRPO 等）、奖励模型结构、训练步数与算力账单。
- 底座是否等于 GPT-4o、MoE/稠密等架构细节。
- 原始 CoT 的完整忠实度（faithfulness）——System Card 明确称 CoT 是否真实反映内部计算仍是开放研究问题。
- 「o1 Pro / 搜索树」等第三方推断：**待核实**，不以本笔记为据。

### 2.3 DeepSeek-R1：更可复述的开源叙事（含蒸馏）

DeepSeek-R1 论文把「纯 RL 激励推理」拆成可跟读的两段产品：

#### （1）DeepSeek-R1-Zero：跳过 SFT，直接 RL

- **底座**：DeepSeek-V3-Base。
- **算法**：Group Relative Policy Optimization（**GRPO**，Shao et al. 2024）——用组内相对优势，**不训 value model**，相对 PPO 省显存与算力（论文 §2.1、附录 A.3）。
- **奖励**：规则奖励 = **准确率奖励 + 格式奖励**（`<think>` / `<answer>` 类标签）；**明确不用**过程/结果神经奖励模型于推理任务，以防大规模 RL 时 reward hacking（§2.2）。
- **模板**：只约束「先推理再作答」的结构，不注入人类解题步骤内容，以便观察自发涌现。
- **涌现现象（Figure 1）**：
 - AIME 2024 pass@1：约 **15.6% → 77.9%**；cons@16 可达约 **86.7%**。
 - 训练过程中 **平均回复长度持续上升**——模型自发用更长思考时间解题。
 - 出现反思、换路、「aha moment」（中间 checkpoint 突然增加 “wait” 等反思用语，Table 2）。

作者论点（§1、§6）：**不一定要大量人类标注的思维轨迹**；关键是难问题 + 可靠 verifier + 足够 RL 算力。人类示范甚至可能限制探索（故 Zero 故意绕过 SFT）。

**代价**：可读性差、中英混杂；偏推理域，写作/开放域 QA 弱 → 引出 R1 多阶段管线。

#### （2）DeepSeek-R1：多阶段对齐 + 可读长 CoT

论文 Figure 2 / §3 管线（公开叙述）：

1. **冷启动 SFT**：少量「会话式、第一人称、可读」长 CoT（产品动机：用户体验；论文也提醒这是工程启发式，不等于模型「真有人类智能」）。
2. **第一阶段 RL**：在可读思维格式上继续用 GRPO；加入 **语言一致性奖励**（目标语言词占比），减轻中英混写。
3. **拒绝采样 + 大规模 SFT**：约 **800k** 样本（约 600k 推理 + 200k 非推理），覆盖数学/代码/STEM/逻辑与写作等。
4. **第二阶段 RL**：规则奖励（推理）+ 模型奖励（helpful / safety）+ 语言一致性；总步数有限，避免对神经奖励的 hacking（附录 B.5）。

**最终公开结果摘录（Table 3 / Table 8 口径）：**

- AIME 2024 pass@1：R1 约 **79.8%**（R1-Zero 约 77.9%）。
- MATH-500 pass@1：约 **97.3%**。
- Codeforces：百分位约 **96.3%**、rating 约 **2029**（Table 3 阶段表）。
- 与 o1-1217 对比表中，AIME pass@1：o1 约 **79.2%**、R1 约 **79.8%**（Table 8；评测协议见附录 D）。

#### （3）蒸馏叙事（论文明确有）

§1 与附录 B.4.3 / Supplementary F：

> 把大模型涌现出的推理模式 **系统性地蒸馏到更小模型**，并以更低能耗开放。

公开蒸馏系列包括（Table 6）：
DeepSeek-R1-Distill-Qwen-{1.5B,7B,14B,32B}、DeepSeek-R1-Distill-Llama-{8B,70B} 等——用约 800k 轨迹对对应基座做 2–3 epoch SFT。
**含义**：长 CoT 能力不必每家都从零跑满规模 RL；**轨迹蒸馏**是第二条扩散路径。

### 2.4 o1 公开叙述 vs R1：对照表

| 维度 | OpenAI o1（公开） | DeepSeek-R1（论文） |
|---|---|---|
| 核心主张 | RL 训出会「想」的模型；test-time 多想可涨分 | 纯 outcome RL 可激励长 CoT；人类示范非必须 |
| 算法细节 | 未公开具体算法 | GRPO + 组相对优势；对比 PPO |
| 奖励 | 未公开配方 | 推理域：规则准确率+格式；后期加 RM |
| 是否先 SFT | 未明确公开 Zero 式路径 | R1-Zero：**无 SFT**；R1：冷启动 + 多阶段 |
| CoT 可见性 | 原始 CoT 隐藏，产品给摘要 | 开源权重侧可看到完整思维格式（部署策略另论） |
| 小模型路径 | o1-mini（官方：更快更便宜，偏代码） | **显式蒸馏系列** + 训练成本表（附录） |
| 安全 | System Card + Preparedness；deliberative alignment | 自述固有安全中等（可比 GPT-4o），需风控系统抬升 |

---

## 三、数学 / 评测直觉：test-time compute 与准确率权衡

> 本节只复述**公开图与表述**；不拟合未给出的闭式定律。

### 3.1 两条「算力轴」（OpenAI 公开图意）

*Learning to reason* 给出概念图：**o1 性能随 train-time compute 与 test-time compute 均平滑上升**。直觉上：

- **Train-time**：RL 步数 ↑ → 更会规划、纠错、换策略。
- **Test-time**：单题思考 token / 采样数 ↑ → 更充分搜索解空间。

评测上常同时看到：

- **pass@1**：单次采样正确率（接近真实「一次回答」体验）。
- **cons@k / majority vote**：k 次采样多数票（显式花更多推理算力）。
- **重排 / 选择策略**：用验证器或学习打分在候选中选优（IOI 例子）。

AIME 2024（*Learning to reason*）是最清晰的公开权衡链：

$$
\underbrace{12\%}_{\text{GPT-4o}}
\;\rightarrow\;
\underbrace{74\%}_{\text{o1 pass@1}}
\;\rightarrow\;
\underbrace{83\%}_{\text{cons@64}}
\;\rightarrow\;
\underbrace{93\%}_{\text{1000 样本 + 学习打分重排}}
$$

每向右一步，都是 **用更多 test-time compute（或更强选择器）换准确率**。

### 3.2 DeepSeek-R1：自适应思考长度 vs 传统多数票

论文对 test-time scaling 的公开比较（Supplementary E，Figure 18 及相关段落）要点：

1. **自适应分配**：在 2024 竞赛数学题集合上，R1 约 **61.8%** Pass@1，平均约 **8,793** thinking tokens；简单题可 <7k，难题可 >18k——**难的多想、易的少想**。
2. **对比非推理模型**：同集上 GPT-4o-0513 约 **24.7%**、平均约 **711** 输出 token（约一个数量级更短）。
3. **多数票补不齐差距**：对 GPT-4o，16 样本多数票提升有限；AIME 2024 上 64 票仅约 **9.3% → 13.4%**，仍远低于 R1 ~79.8% / o1 ~79.2%。原因：独立采样**不会**像长 CoT 那样在单条轨迹内回退与自纠。
4. **长 CoT 仍可再叠加传统方法**：R1 在 AIME 上 Pass@64 ≈ **90.0%** > Pass@1 **79.8%**；majority voting 可再把 R1 推到约 **86.7%**（与 Zero 的 cons@16 叙事一致）。
5. **作者自称相对 MCTS/多数票的差异**：R1「按题目难度动态分配」token，而非固定外层搜索；但仍有 **overthinking**（简单题想太久）问题（§6 Token efficiency）。

### 3.3 跟读用的「权衡草图」（非论文公式）

把一次请求的有效算力粗记为：

$$
C_{\text{test}} \;\propto\; L_{\text{think}} \times N_{\text{samples}} \times C_{\text{verify}}
$$

- $L_{\text{think}}$：单条思维链长度（o1/R1 主轴）。
- $N_{\text{samples}}$：并行候选数（pass@k / majority / best-of-N）。
- $C_{\text{verify}}$：外部验证或打分（单测、符号检验、奖励模型）。

公开结果共同暗示：**在可验证域，先把 $L_{\text{think}}$ 训厚，再适度加 $N_{\text{samples}}$，往往比「短答案 × 海量独立投票」更 token 高效。** 精确的 log-linear 斜率、与 train-time 的可兑换率：**OpenAI 博文有定性图，未给可引用闭式系数 → 外推系数标「待核实」。**

### 3.4 评测协议提醒（避免苹果橙）

- R1 附录 D：长输出用非零温度采样再平均成 pass@1；AIME/GPQA 常用 k=64 等。
- o1 博文：默认 maximal test-time；表格同时列 pass@1 与 cons@64。
- **跨文数字不可直接横比**，除非对齐采样数、温度、工具与是否隐藏 CoT。

---

## 四、AI Infra：推理成本、延迟、按思考深度计费

### 4.1 成本结构变了什么

传统 Chat 模型：账单 ≈ 输入 token + **可见**输出 token。

推理模型额外冒出一类 **reasoning / thinking tokens**：

- 占用上下文窗口；
- 通常按 **输出单价**计费；
- API **不一定返回原文**（OpenAI：原始推理不可见，usage 里可见 `reasoning_tokens` 计数——以官方 Reasoning 指南为准）。

因此：**贵的往往不是最终那两段答案，而是中间「想」的那几万 token。** 延迟也从「秒级补全」变成「数秒到数分钟」（o1-preview 发布时官方即提示复杂题可能很慢）。

### 4.2 产品旋钮：思考深度 = 显式 SLO

公开产品逻辑（OpenAI 介绍页 + 后续 Reasoning API 文档族）：

- **选模型**：o1 / o1-mini / 后续 o 系列与带 `reasoning.effort` 的模型——能力、价、延迟不同。
- **调 effort / max tokens**：控制愿花多少思考预算；effort 低 → 更快更便宜；高 → 更强但更贵更慢。
- **路由**：简单问答继续走 GPT-4o 类快模型；竞赛级数学/代码/科学再走推理模型（介绍页亦称多数日常场景近期仍可能是 GPT-4o 更合适）。

**计费含义（架构师视角）：**

1. 单价应按 **「完整 completion = 可见输出 + 隐藏推理」** 建模，否则会系统性低估 3–20×（量级随题而变，需用自有流量校准）。
2. `max_output_tokens` 设太小，可能在**尚未写出可见答案前**就因推理耗尽而 `incomplete`——仍可能产生费用。
3. 批处理 / 缓存对「每题新想一遍」帮助有限；KV cache 随思维变长线性涨，吞吐与尾延迟是新瓶颈。
4. DeepSeek 路线给出另一 Infra 答案：**大模型 RL 出轨迹 → 蒸馏小模型**，把部分 test-time 智能「编译」回更便宜的权重（论文动机句：lower energy cost）。

### 4.3 训练侧 Infra 一瞥（仅 R1 公开数字）

R1 附录 Table 7（按文中假设 H800 租金 \$2/GPU·h）：

| 阶段 | H800 GPU·h（约） |
|---|---|
| R1-Zero | 101K |
| SFT 数据制造 | 5K |
| R1 | 41K |
| **合计** | **147K（文中约 \$294K）** |

并描述解耦的 Rollout（vLLM）/ Inference / Rule-reward / Training 模块、异步隐藏规则奖励延迟、数据 packing 等（附录 B.1）。
**o1 训练账单：未公开 → 待核实。**

### 4.4 系统卡里的「推理算力」安全含义

System Card §5.3：o 系列因推理与 **test-time compute** 带来能力跃迁，对 CBRN、persuasion 等维持 Medium 评级并加强缓解（含 deliberative alignment）。
**Infra 推论**：服务端不仅要计量 token，还要计量/限流「危险域上的长思考」，监控对象从最终答案扩展到 **CoT 摘要与行为模式**（§4.3 CoT deception monitoring 为早期探索）。

---

## 五、常见误区与引用

### 5.1 常见误区

1. **「就是 CoT 提示词」**
 错。公开叙事强调 **RL 训练出的长思维策略**；提示「一步步想」既无同等涨分，也不是 o1/R1 的核心。

2. **「test-time scaling = 无限多数票」**
 不完整。R1 公开对比表明：对非推理模型，多数票远不能追上长 CoT；对推理模型，多数票是**互补**而非替代。

3. **「隐藏 CoT = 没有推理」**
 错。OpenAI 仍生成并计费 reasoning tokens，只是不展示原文；产品展示的是摘要。

4. **「R1-Zero 证明完全不需要人类数据」**
 过度解读。Zero 展示的是**推理策略可少依赖人类轨迹**；完整 R1 仍用冷启动、偏好数据与安全数据做对齐。预训练语料本身也含大量人类文本。

5. **「公开了 System Card = 公开了训练配方」**
 否。System Card 主攻安全评测与风险；**算法超参、数据配比、损失细节大多未公开**。R1 相对透明，但仍非逐步复现手册。

6. **「想得越久一定越好」**
 否。存在延迟/费用上限、overthinking、以及错误逻辑路径上「固执地想很久」（R1 §6；o1 亦有 reward hacking 观察）。

7. **把第三方架构传闻当事实**
 凡未出现在 OpenAI/DeepSeek 一级来源的「搜索树层数、隐蔽 MoE、内部代号」等，一律 **待核实**。

### 5.2 一级引用（跟读清单）

1. OpenAI. *Introducing OpenAI o1-preview.* https://openai.com/index/introducing-openai-o1-preview/ （2024-09-12）
2. OpenAI. *Learning to reason with LLMs.* https://openai.com/index/learning-to-reason-with-llms/ （2024-09-12）
3. OpenAI. *OpenAI o1 System Card.* arXiv:2412.16720 / https://arxiv.org/pdf/2412.16720 （2024-12）
4. DeepSeek-AI. *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948 / https://arxiv.org/pdf/2501.12948 （2025-01）
5. OpenAI API. *Reasoning models* 指南（reasoning tokens、effort、计费与上下文；接口随时间更新，引用时核对当前文档）

### 5.3 官方 PDF

- `https://arxiv.org/abs/2412.16720`
- `https://arxiv.org/abs/2501.12948`

### 5.4 待核实清单（禁止当事实传播）

- o1 / o1-pro 内部是否使用显式 MCTS、过程奖励模型、或特定搜索宽度。
- o1 与 GPT-4o 是否同底座、参数量、专家数。
- train-time 与 test-time compute 的**可兑换定量定律**（第三方 log-linear 斜率）。
- 各云厂商「按思考深度」套餐的最新单价与是否对 reasoning tokens 打折（以账单与官方定价页为准）。
- R1 蒸馏小模型在**非数学代码域**的泛化边界与安全对齐是否等同大模型。

---

## 附：一页纸跟读结论

| 问题 | 公开答案 |
|---|---|
| 新轴是什么？ | **Test-time compute**：推理时多想 / 多采样可涨分 |
| 怎么训出来的？ | **大规模 RL 激励长 CoT**（o1 公开叙述；R1 给 GRPO+规则奖励细节） |
| 和提示 CoT 差在哪？ | 策略由优化学出，可含反思与换路；可叠加采样 |
| 开源侧多了什么？ | R1-Zero 无 SFT 路径 + **蒸馏小模型** + 更细 Infra/成本表 |
| 工程代价？ | 延迟↑、reasoning token 费用↑、KV/吞吐压力↑；需要 effort 路由 |
| 安全？ | 推理有助于对齐，也放大危险能力；需新监控与缓解 |

*稿状态：draft · 仅基于上述公开材料 · 2026-09-22*

## 相关笔记

- [[注意力与Transformer核心思想|Attention / Transformer]]
- [[DecoderOnly与GPT路线|Decoder-only / GPT]]
- [[规模定律与预训练范式|规模定律与预训练]]
- [[混合专家架构|MoE / 稀疏激活]]
- [[对齐脉络RLHF与偏好优化|对齐 RLHF / DPO]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿模型谱系]]

