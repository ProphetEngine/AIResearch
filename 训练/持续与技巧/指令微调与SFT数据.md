---
date: 2026-10-12
status: archived
archived: 2026-10-12
topic: 指令微调与SFT数据
title: "指令微调与SFT数据"
lines: [训练方法, 数据策展]
sources:
  - https://arxiv.org/abs/2104.08773
  - https://arxiv.org/abs/2109.01652
  - https://arxiv.org/abs/2110.08207
  - https://arxiv.org/abs/2203.02155
  - https://arxiv.org/abs/2204.07705
  - https://arxiv.org/abs/2210.11416
  - https://arxiv.org/abs/2301.13688
  - https://arxiv.org/abs/2305.11206
  - https://arxiv.org/abs/2305.15717
  - https://arxiv.org/abs/2306.02707
  - https://arxiv.org/abs/2306.04751
  - https://arxiv.org/abs/2307.08701
  - https://arxiv.org/abs/2308.12032
  - https://arxiv.org/abs/2312.01552
  - https://arxiv.org/abs/2312.15685
  - https://arxiv.org/abs/2402.04333
  - https://arxiv.org/abs/2411.15124
  - https://arxiv.org/abs/2501.17161
  - https://arxiv.org/abs/2502.03387
  - https://arxiv.org/abs/2502.04194
  - https://arxiv.org/abs/2506.04178
  - https://arxiv.org/abs/2601.13995
  - https://arxiv.org/abs/2604.10448
  - https://arxiv.org/abs/2605.30857
arxiv: ["2104.08773", "2109.01652", "2110.08207", "2203.02155", "2204.07705", "2210.11416", "2301.13688", "2305.11206", "2305.15717", "2306.02707", "2306.04751", "2307.08701", "2308.12032", "2312.01552", "2312.15685", "2402.04333", "2411.15124", "2501.17161", "2502.03387", "2502.04194", "2506.04178", "2601.13995", "2604.10448", "2605.30857"]
related: ["对齐脉络RLHF与偏好优化", "合成数据与教科书式数据", "合成对齐数据Magpie", "LoRA与参数高效微调", "OnPolicy蒸馏OPD范式", "中期训练MidTraining范式", "RLVR能力边界与熵机制", "DeepSeekR1推理训练深读"]
---

# 指令微调与SFT数据

> **主要来源**：[Finetuned Language Models Are Zero-Shot Learners](https://arxiv.org/abs/2109.01652)（简称 FLAN）；[Scaling Instruction-Finetuned Language Models](https://arxiv.org/abs/2210.11416)（简称 Flan-PaLM）；[LIMA: Less Is More for Alignment](https://arxiv.org/abs/2305.11206)（简称 LIMA）；[Tulu 3: Pushing Frontiers in Open Language Model Post-Training](https://arxiv.org/abs/2411.15124)（简称 Tulu 3）；[SFT Memorizes, RL Generalizes: A Comparative Study of Foundation Model Post-training](https://arxiv.org/abs/2501.17161)（简称 Chu 等）；[OpenThoughts: Data Recipes for Reasoning Models](https://arxiv.org/abs/2506.04178)（简称 OpenThoughts）（截至 2026-05-29）。其余来源见第十二节。
> **研究线**：训练方法（在「指令—回复」对上做监督微调，怎样把预训练模型变成能按指令作答的模型；它在 RL 主导的后训练中还承担什么角色）· 数据策展（多任务指令集合怎样扩大，「少而精」与「多而全」两种数据观各自成立的条件，SFT 数据按什么信号筛选）
> **范围与相邻笔记**：
> - ≠ [[对齐脉络RLHF与偏好优化]]：本篇不写奖励模型、PPO 与 DPO，InstructGPT 只作为「示范数据 SFT 是 RLHF 第一步」引用。
> - ≠ [[合成数据与教科书式数据]]：本篇不写指令数据的合成方法，只把合成产出当作数据来源。
> - ≠ [[合成对齐数据Magpie]]：本篇不写对齐数据的合成管线。
> - ≠ [[LoRA与参数高效微调]]：本篇不写微调时更新哪些参数。
> - ≠ [[OnPolicy蒸馏OPD范式]]：本篇不写在线策略蒸馏。
> - ≠ [[中期训练MidTraining范式]]：本篇不写中期训练混入指令数据的配方。
> - ≠ [[RLVR能力边界与熵机制]]：本篇不写 RLVR 机制。
> - ≠ [[DeepSeekR1推理训练深读]]：本篇不写具体模型的冷启动配方。
>
> **意义**：指令微调把「按自然语言说明做事」本身当作训练目标，使模型在没见过的任务上也能零样本作答，是此后对话模型与后训练流水线的起点。数据观随后分为两支：LIMA 认为知识几乎都来自预训练，少量精选样本就够；Tulu 3 与 OpenThoughts 则以大规模、可复现的数据管线推进开放模型。数据选择由此成为独立问题，而在以 RL 为主的推理后训练中，SFT 的角色被重新界定为稳定输出格式、为 RL 打底。

## 一、问题背景

**预训练模型不擅长按指令作答**：Ouyang 等指出，把模型做大并不会让它天然更好地遵循用户意图，大模型会生成不真实、有害或无用的输出（InstructGPT 摘要）。GPT-3 式的零样本能力依赖提示写法，T0 的作者把这种能力归因于一个假说：预训练中隐含了多任务学习（T0 摘要）。

**能否显式地教**：既然零样本泛化可能来自隐含的多任务学习，那么把大量有监督任务改写成自然语言指令再训练，能否直接诱导出这种泛化（T0 摘要）？这就是指令微调要回答的问题。

**定义**：指令微调（instruction tuning，也称监督微调 SFT）是在「指令—回复」对上以标准监督损失微调预训练模型。FLAN 的表述是「在一组以指令描述的任务上微调语言模型」（FLAN 摘要）。与继续预训练、中期训练相比，它的数据形态是成对的指令与回复，目标是学会遵循指令，而不是补充知识。在后训练流水线中，它位于偏好优化与 RL 之前。

## 二、发展脉络

| 时间（arXiv v1） | 节点 | 要点 |
|---|---|---|
| 2021-04 | Natural Instructions（Mishra 等） | 61 个任务、人工撰写的指令与 19.3 万个实例；用指令的模型在未见任务上好 19% |
| 2021-09 | FLAN（Wei 等） | 137B 模型、60 余个任务；25 项中 20 项超过零样本 175B GPT-3 |
| 2021-10 | T0（Sanh 等） | 多提示改写的多任务混合，常超过大 16 倍的模型 |
| 2022-03 | InstructGPT（Ouyang 等） | 标注员示范数据上的 SFT 成为 RLHF 的第一步 |
| 2022-04 | Super-NaturalInstructions（Wang 等） | 1,616 个任务、76 种任务类型 |
| 2022-10 | Flan-PaLM / Flan-T5（Chung 等） | 扩到 1.8K 个任务，加入思维链数据 |
| 2023-01 | Flan Collection（Longpre 等） | 任务平衡、混合提示设定的消融 |
| 2023-05 | LIMA（Zhou 等）；模仿的局限（Gudibande 等） | 1,000 条样本与表层对齐假说；模仿模型学到风格而非事实性 |
| 2023-06 | Orca（Mukherjee 等）；How Far Can Camels Go（Wang 等） | 解释轨迹模仿；12 个开放指令数据集的系统比较 |
| 2023-07 至 2024-02 | AlpaGasus、IFD、Deita、LESS | 数据选择成为独立问题 |
| 2023-12 | URIAL（Lin 等） | 不微调、只用上下文示例的对齐 |
| 2024-11 | Tulu 3（Lambert 等） | SFT、DPO、RLVR 全开放配方 |
| 2025-01 至 2025-02 | Chu 等；LIMO（Ye 等）；GRAPE（Zhang 等） | SFT 偏记忆但稳定格式；少量推理示范；按目标模型分布选回复 |
| 2025-06 | OpenThoughts（Guha 等） | 1,000 余次受控实验的推理 SFT 数据管线 |
| 2026-01 至 2026-05 | TAGS、ADG、MADS | 用知识树、回答发散度与模型激活选数据 |

主线：众包与多任务指令化（2021 至 2023 年初），对话式 SFT 与「表层对齐」之争（2023），数据选择成为独立问题（2023 下半年至 2024 年初），全开放后训练配方（2024 年末），推理时代 SFT 的角色重定位与推理数据管线（2025），再到以模型自身信号做数据选择（2026）。

## 三、多任务指令化：从众包指令到 Flan Collection

### 3.1 众包指令与跨任务泛化

Natural Instructions 把构建现有 NLP 数据集时发给众包工人的说明收集起来，映射到统一格式，得到 61 个任务、人工撰写的指令和 19.3 万个输入—输出实例。在已见任务上训练、在其余未见任务上测试，使用指令的模型泛化好 19%，但与估计的上限仍差很远（Natural Instructions 摘要）。

Super-NaturalInstructions 扩到 1,616 个任务、76 种任务类型，指令由专家撰写。在其上训练的 Tk-Instruct 比 InstructGPT 高 9% 以上，而规模小一个数量级；论文还分析了泛化随已见任务数、每个任务的实例数与模型规模的变化（Super-NaturalInstructions 摘要）。

### 3.2 FLAN 与 T0：指令微调的提出

FLAN 以 137B 参数的 LaMDA-PT 为基座，这是一个只做过语言模型预训练、没有为对话微调的 decoder-only 模型（FLAN 原文 §2.4）。它把 60 余个 NLP 任务用自然语言指令模板改写后微调，在未见任务类型上评测：25 项中 20 项超过零样本的 175B GPT-3，在 ANLI、RTE、BoolQ 等任务上还大幅超过少样本 GPT-3。消融显示，微调数据集的数量、模型规模与自然语言指令是成功的关键（FLAN 摘要）。

T0 走的是同一思路的另一条路：为大量有监督数据集各写多条措辞不同的提示，在这个多任务混合上微调编码器—解码器模型（T0 摘要），所有变体由 11B 的 LM 适配版 T5 初始化（T0 原文 §5）。它在若干标准数据集上的零样本表现常超过大 16 倍的模型，在 BIG-bench 子集上超过大 6 倍的模型（T0 摘要）。

**为什么有效**：两篇的共同解释是，模型从「多种任务都以自然语言说明给出」这一形式中学到了读懂说明本身，因此遇到新的说明也能执行。FLAN 的消融与这个解释一致：微调数据集的数量、模型规模与自然语言指令三者都是关键（FLAN 摘要）。

### 3.3 扩大与总结：Flan-PaLM 与 Flan Collection

Chung 等沿三个方向扩大：任务数、模型规模、思维链数据。在 1.8K 个任务上微调的 Flan-PaLM 540B 平均比 PaLM 540B 高 9.4%，五样本 MMLU 达到 75.2%；公开的 Flan-T5 检查点在少样本上能与 PaLM 62B 这样更大的模型相比（Flan-PaLM 摘要）。

Flan Collection 拆解 Flan 2022 的设计决定。论文称，任务平衡与数据增强常被忽视却很关键；尤其是把零样本、少样本与思维链三种提示设定混合训练，会在所有设定上都更强（2% 以上）。它还发现，Flan-T5 作为下游单任务微调的起点，比 T5 收敛更快、更高，因此指令微调过的模型是更省算力的起始检查点（Flan Collection 摘要）。

## 四、对话式 SFT 与模仿

### 4.1 示范数据进入 RLHF

InstructGPT 先收集标注员写的提示与 API 用户提交的提示，由标注员写出期望行为的示范，用监督学习微调 GPT-3，再在此基础上做 RLHF（InstructGPT 摘要）。这一步让 SFT 从「多任务 NLP 改写」转向「开放式对话示范」。三阶段的细节见 [[对齐脉络RLHF与偏好优化]]。

### 4.2 模仿专有模型的局限

2023 年出现了一种廉价做法：用 ChatGPT 等专有模型的输出微调较弱的开源模型，[Alpaca](https://crfm.stanford.edu/2023/03/13/alpaca.html)、Self-Instruct 等是代表（Gudibande 等摘要）。Gudibande 等用 1.5B 到 13B 的基座、0.3M 到 150M token 的模仿数据系统检验这一做法。众包评审起初认为模仿模型的输出能与 ChatGPT 竞争，但针对性的自动评测显示，在模仿数据覆盖不多的任务上，模仿模型几乎没有缩小基座与 ChatGPT 的差距。论文的解释是：模仿模型善于模仿 ChatGPT 的风格，而不是它的事实性，这种差异容易骗过人类评审；更高杠杆的做法是开发更好的基座（Gudibande 等摘要）。

### 4.3 解释轨迹：Orca

Orca 认同「小模型往往只学到风格、学不到推理过程」这一诊断，改用 GPT-4 的解释轨迹、逐步思考过程与复杂指令作为信号，并由 ChatGPT 担任教师助手做渐进学习。13B 的 Orca 在 BBH 上比 Vicuna-13B 高 100% 以上，在 AGIEval 上高 42%，在 BBH 上与 ChatGPT 持平，但仍落后于 GPT-4（Orca 摘要）。

## 五、少而精：表层对齐假说

### 5.1 LIMA

LIMA 用标准监督损失，在 1,000 条精心挑选的提示与回复上微调 65B 的 LLaMa，不做 RL，也不做人类偏好建模。受控人评中，LIMA 的回复在 43% 的情况下与 GPT-4 相当或更优；对 Bard 这一比例为 58%，对经过人类反馈训练的 DaVinci003 为 65%（LIMA 摘要）。注意 43% 是「相当或更优」的合计比例，不是胜率。

论文据此提出**表层对齐假说**：模型的知识与能力几乎全部在预训练中习得，对齐只是教它与用户交互时该用哪一种格式的子分布（LIMA 原文 §2）。如果假说成立，少量样本就足以完成对齐。

### 5.2 URIAL：不微调的对照

URIAL 从另一侧检验这一假说。Lin 等比较基座模型与其对齐版本的 token 分布，发现在大多数位置上两者解码几乎相同，分布偏移主要出现在风格性 token 上，论文称这直接支持了表层对齐假说。在此基础上，URIAL 不做 SFT 也不做 RLHF，只用三个固定的风格示例加一段系统提示做上下文学习，论文报告其表现能达到甚至超过经 SFT 或 SFT 加 RLHF 对齐的模型（URIAL 摘要）。

### 5.3 推理时代的 LIMO

LIMO 把「少而精」搬到数学推理。它以 Qwen2.5-32B-Instruct 为基座（LIMO 原文 §4），从候选题与解答中按质量分取前 800 条组成训练集（LIMO 原文 §3.1.2），只做简单的 SFT，在 AIME24 上达到 63.3%、MATH500 上 95.6%，而此前的微调模型分别为 6.5% 与 59.2%，所用训练数据只有以往方法的 1%（LIMO 摘要）。论文提出「少即是多推理假说」：当领域知识已在预训练中被充分编码时，少量精心设计的认知过程示范就能引出复杂推理；门槛取决于预训练知识是否完整、后训练样本能否充当推理的「认知模板」（LIMO 摘要）。

**成立条件**：LIMA 用 65B 的 LLaMa，LIMO 用已经做过指令微调的 Qwen2.5-32B-Instruct，两篇的结论都明确以「预训练已提供知识」为前提。Gudibande 等的结论与此一致：缺的是基座能力时，靠模仿数据补不上。

## 六、多而全：开放数据与可复现管线

### 6.1 How Far Can Camels Go 与 Tülu

Wang 等在 6.7B 到 65B 的模型上，用 12 个指令数据集（从人工整理的 OpenAssistant 到合成与蒸馏的 Alpaca）分别微调，并从事实知识、推理、多语种、代码与开放式指令跟随几方面系统评测。结论有三：不同数据集能挖掘或增强不同技能，没有一个数据集或组合在所有评测上最好；基于模型与人类偏好的评测反映不出基准评测暴露的能力差异；任一评测上最好的模型平均只达到 ChatGPT 的 87%、GPT-4 的 73%（How Far Can Camels Go 摘要）。

### 6.2 Tulu 3

Tulu 3 以 Llama 3.1 基座为起点，公开全部数据、代码与训练配方，训练算法依次为 SFT、DPO 与 RLVR。论文报告其结果超过 Llama 3.1、Qwen 2.5、Mistral 的 instruct 版本以及 GPT-4o-mini、Claude 3.5-Haiku。它同时提出带开发集与未见评测的多任务评测方案，并对现有开放数据集在这些基准上做了大量去污染（Tulu 3 摘要）。对 SFT 而言，它的意义在于把 SFT 数据当作按核心技能逐项构建、可复现的一环，而不是一次性的数据集。

### 6.3 OpenThoughts

OpenThoughts 面向推理模型的 SFT 数据。其 OpenThoughts2-1M 数据集训练出的 OpenThinker2-32B，是第一个用公开推理数据训练、在 AIME 与 LiveCodeBench 等基准上与 DeepSeek-R1-Distill-32B 相当的模型。随后团队用 1,000 余次受控实验逐步考察数据生成管线的每一步，得到 OpenThoughts3；把管线扩到 1.2M 样本、以 QwQ-32B 作教师，OpenThoughts3-7B 在 AIME 2025 上达到 53%、LiveCodeBench 06/24-01/25 上 51%、GPQA Diamond 上 54%，比 DeepSeek-R1-Distill-Qwen-7B 分别高 15.3、17.2 与 20.5 个百分点（OpenThoughts 摘要）。

**与「少而精」的关系**：两种数据观不是同一问题的正反答案。LIMA、LIMO 在强基座上问「最少需要多少样本才能引出已有能力」；Tulu 3、OpenThoughts 问「怎样系统地构建数据，让开放模型在广泛基准上逼近专有模型」。

## 七、数据选择

数据选择要回答：给定一个大数据池，挑哪些样本来微调。各方法的差别主要在于用什么信号给样本打分。

| 方法 | 信号来源 | 论文报告的结论（各行不可横比） |
|---|---|---|
| AlpaGasus（2023-07） | 强模型（如 ChatGPT）给每条样本打质量分，滤掉低质量样本 | 从 Alpaca 的 52k 条中选出 9k 条，明显优于原版 Alpaca；7B 训练时间从 80 分钟降到 14 分钟 |
| IFD（2023-08） | 指令跟随难度：模型的期望回复与其自身生成能力之间的差距 | 在 Alpaca、WizardLM 上只用 10% 的数据即取得更好的结果 |
| Deita（2023-12） | 复杂度、质量、多样性三个维度组合 | 只用 6K 条 SFT 样本，比基线少 10 倍以上，表现优于或持平当时开源对齐模型 |
| LESS（2024-02） | 与 Adam 优化器适配的低秩梯度相似度，对照目标能力的少量示例 | 选出的 5% 数据常优于全量；小模型选出的数据可用于大模型与其他家族 |
| GRAPE（2025-02） | 对每条指令收集多个模型的回复，取目标模型给出概率最高的一条 | 在 Tulu3 与 Olmo-2 的后训练数据上，用 1/3 的数据、一半的轮数，让 LLaMA3.1-8B 比 Tulu3-SFT 高 3.5% |
| TAGS（2026-01） | 由细粒度标签自底向上聚类出的知识树，度量质量与多样性 | 只用 5% 的数据超过全量模型 5.84% |
| ADG（2026-04） | 同一指令高温多次采样的回答在嵌入空间中的发散程度与形状 | 只用 1 万条选出的样本，在六个基准上稳定优于强选择器 |
| MADS（2026-05） | 推理时模型的神经激活状态，做覆盖式核心集 | 在 52K 条的 Alpaca-GPT4 上，由 Llama-3.2-3B-Instruct 选出 15% 的核心集，微调四个更大基座，平均比全量高 2.5% |

出处依次为各论文摘要。

**信号的演变**：早期信号来自外部，即由强模型给样本打分（AlpaGasus）或按人定义的维度度量（Deita）。此后信号逐渐转向目标模型自身：IFD 看模型自己生成回复的难度，LESS 看样本对模型梯度的影响，GRAPE 看回复是否贴合目标模型的预训练分布，MADS 看模型内部的激活。GRAPE 的出发点是，从其他大模型采样的回复往往在目标模型的分布之外，规模大了会收益递减，甚至损害性能与鲁棒性（GRAPE 摘要）。多样性也从按文本嵌入聚类转向按知识结构（TAGS）、回答分布（ADG）或模型激活（MADS）来度量。TAGS 的作者指出，基于嵌入聚类或语义标签的多样性度量受限于嵌入空间的扁平与标签的粗糙（TAGS 摘要）。

**选数据为什么能胜过全量**：AlpaGasus 发现 Alpaca 的 52k 条中有许多错误或无关的回复，会误导训练（AlpaGasus 摘要）。去掉这类样本、减少与目标模型分布不合的回复，同时保留覆盖面，是这些方法共同的解释。

## 八、SFT 与 RL 的分工

Chu 等用算术卡牌游戏 GeneralPoints 与真实世界导航环境 V-IRL，分别在文本规则变体与视觉变体上比较 SFT 与 RL 的泛化。论文称，RL（尤其以结果为奖励时）能在两类变体上泛化，SFT 则倾向于记住训练数据，难以泛化到分布外；但 SFT 仍然是 RL 有效的前提，因为它稳定了模型的输出格式，使后续 RL 能够取得收益（Chu 等摘要）。

这与本篇其他来源互相印证：LIMA 与 URIAL 把对齐微调的作用主要归于格式与风格，Chu 等则在 RL 流水线中把 SFT 的作用落在「输出格式」上。在现代后训练中，SFT 因此更像是为偏好优化与 RL 准备一个格式稳定、能按指令作答的起点；Tulu 3 的 SFT、DPO、RLVR 顺序即是一例。SFT 与在线策略蒸馏在成本上的对照见 [[OnPolicy蒸馏OPD范式]]，RL 能否扩展能力边界见 [[RLVR能力边界与熵机制]]。

## 九、意义

1. **把「遵循指令」变成可训练的目标**：FLAN 与 T0 证明，以自然语言说明组织的多任务训练能带来零样本泛化，任务数、规模与指令形式是关键变量。
2. **把对齐的重心推回预训练**：LIMA 的表层对齐假说、URIAL 的上下文对齐与 LIMO 的推理示范共同指向一点：在强基座上，SFT 主要决定输出的格式与风格，能力主要来自预训练。
3. **让数据成为后训练的主要研究对象**：从 Flan Collection 的混合消融到 Tulu 3、OpenThoughts 的开放管线，再到以模型自身信号选数据，SFT 研究的重心从「怎样训练」转向「用什么数据训练」。

## 十、局限与争议

1. **数据集与评测之间可比性差**：How Far Can Camels Go 发现，没有一个指令数据集在所有评测上最好，基于偏好的评测与基准评测给出的结论不一致。本篇引用的各方法提升幅度都在各自的数据池、基座与基准上测得，不能横向比较。
2. **两种数据观的结论条件不同**：LIMA、LIMO 在强基座上测，Tulu 3、OpenThoughts 面向广泛基准与可复现的开放配方，不能简单对立。
3. **人评与模仿的偏差**：Gudibande 等指出，模仿模型的风格优势可能骗过人类评审，LIMA 的 43% 也来自人评，且是「相当或更优」的合计比例而不是胜率。
4. **论点而非定论**：「表层对齐假说」「SFT 记忆、RL 泛化」都是论文提出的论点。Chu 等的结论来自 GeneralPoints 与 V-IRL 两类环境，向其他任务推广的程度本篇没有核实。
5. **数据污染**：Tulu 3 对开放数据集做了去污染，其他来源的基准分数在多大程度上受训练数据重叠影响，本篇没有核实。
6. **版本**：Natural Instructions 当前为 v4，FLAN 为 v5，T0 为 v3，Super-NaturalInstructions 为 v3，Flan-PaLM 为 v5，Flan Collection 为 v2，How Far Can Camels Go 为 v2，AlpaGasus 为 v5，IFD 为 v5，Deita 为 v2，LESS 为 v3，Tulu 3 为 v5，Chu 等为 v2，LIMO 为 v3，GRAPE 为 v3，OpenThoughts 为 v2，ADG 为 v2。本篇按 abs 页当前版本引用，早期版本的表述与数字可能不同；LIMO 训练集规模按 v3 写作 800 条。

## 十一、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[对齐脉络RLHF与偏好优化]] | 上游与下游：本篇写的示范数据 SFT 是 InstructGPT 流程的第一步，之后的偏好优化归该篇 | 奖励模型、PPO、DPO |
| [[合成数据与教科书式数据]] | 数据来源：本篇把合成指令数据当作 SFT 的输入，讨论怎样使用与筛选 | 合成方法本身 |
| [[合成对齐数据Magpie]] | 数据来源：同上，本篇第七节的选择方法可作用于这类合成对齐数据 | 合成管线 |
| [[LoRA与参数高效微调]] | 正交：本篇写 SFT 用什么数据，该篇写 SFT 更新哪些参数 | 参数高效方法 |
| [[OnPolicy蒸馏OPD范式]] | 对照：本篇第八节写 SFT 在后训练中的角色，SFT 与 OPD 的成本对照归该篇 | 在线策略蒸馏 |
| [[中期训练MidTraining范式]] | 区分：本篇第一节按数据形态与目标区分指令微调与中期训练 | 中期训练配方 |
| [[RLVR能力边界与熵机制]] | 下游：本篇第八节写 SFT 为 RL 稳定输出格式，RL 能否扩展能力归该篇 | RLVR 机制 |
| [[DeepSeekR1推理训练深读]] | 实例：本篇写推理 SFT 数据的一般做法，具体模型的冷启动配方归该篇 | 冷启动配方 |

## 十二、延伸阅读

建议顺序：先读 FLAN 与 T0 的引言，理解指令微调为何带来零样本泛化；再读 Flan Collection 的消融；然后对照读 LIMA、Gudibande 等与 How Far Can Camels Go，看两种数据观的分歧；接着读 Tulu 3 与 OpenThoughts 了解开放配方；数据选择读 AlpaGasus、LESS 与 GRAPE；最后读 Chu 等，理解 SFT 在 RL 流水线中的角色。

| 文献 | 链接 | 与本篇的关系 |
|---|---|---|
| Cross-Task Generalization via Natural Language Crowdsourcing Instructions（Mishra et al., 2021） | https://arxiv.org/abs/2104.08773 | 众包指令 |
| Finetuned Language Models Are Zero-Shot Learners（Wei et al., 2021） | https://arxiv.org/abs/2109.01652 | 指令微调的提出 |
| Multitask Prompted Training Enables Zero-Shot Task Generalization（Sanh et al., 2021） | https://arxiv.org/abs/2110.08207 | 多提示多任务训练 |
| Training language models to follow instructions with human feedback（Ouyang et al., 2022） | https://arxiv.org/abs/2203.02155 | 示范数据 SFT |
| Super-NaturalInstructions: Generalization via Declarative Instructions on 1600+ NLP Tasks（Wang et al., 2022） | https://arxiv.org/abs/2204.07705 | 大规模指令基准 |
| Scaling Instruction-Finetuned Language Models（Chung et al., 2022） | https://arxiv.org/abs/2210.11416 | 扩大任务数与规模 |
| The Flan Collection: Designing Data and Methods for Effective Instruction Tuning（Longpre et al., 2023） | https://arxiv.org/abs/2301.13688 | 任务混合消融 |
| LIMA: Less Is More for Alignment（Zhou et al., 2023） | https://arxiv.org/abs/2305.11206 | 表层对齐假说 |
| The False Promise of Imitating Proprietary LLMs（Gudibande et al., 2023） | https://arxiv.org/abs/2305.15717 | 模仿的局限 |
| Orca: Progressive Learning from Complex Explanation Traces of GPT-4（Mukherjee et al., 2023） | https://arxiv.org/abs/2306.02707 | 解释轨迹模仿 |
| How Far Can Camels Go? Exploring the State of Instruction Tuning on Open Resources（Wang et al., 2023） | https://arxiv.org/abs/2306.04751 | 开放数据集比较 |
| AlpaGasus: Training A Better Alpaca with Fewer Data（Chen et al., 2023） | https://arxiv.org/abs/2307.08701 | 质量打分选择 |
| From Quantity to Quality: Boosting LLM Performance with Self-Guided Data Selection for Instruction Tuning（Li et al., 2023） | https://arxiv.org/abs/2308.12032 | 指令跟随难度 |
| The Unlocking Spell on Base LLMs: Rethinking Alignment via In-Context Learning（Lin et al., 2023） | https://arxiv.org/abs/2312.01552 | 不微调的对齐 |
| What Makes Good Data for Alignment? A Comprehensive Study of Automatic Data Selection in Instruction Tuning（Liu et al., 2023） | https://arxiv.org/abs/2312.15685 | 复杂度、质量与多样性 |
| LESS: Selecting Influential Data for Targeted Instruction Tuning（Xia et al., 2024） | https://arxiv.org/abs/2402.04333 | 梯度影响选择 |
| Tulu 3: Pushing Frontiers in Open Language Model Post-Training（Lambert et al., 2024） | https://arxiv.org/abs/2411.15124 | 全开放后训练配方 |
| SFT Memorizes, RL Generalizes: A Comparative Study of Foundation Model Post-training（Chu et al., 2025） | https://arxiv.org/abs/2501.17161 | SFT 与 RL 的分工 |
| LIMO: Less is More for Reasoning（Ye et al., 2025） | https://arxiv.org/abs/2502.03387 | 少量推理示范 |
| The Best Instruction-Tuning Data are Those That Fit（Zhang et al., 2025） | https://arxiv.org/abs/2502.04194 | 贴合目标模型分布的选择 |
| OpenThoughts: Data Recipes for Reasoning Models（Guha et al., 2025） | https://arxiv.org/abs/2506.04178 | 推理 SFT 数据管线 |
| From Tags to Trees: Structuring Fine-Grained Knowledge for Controllable Data Selection in LLM Instruction Tuning（Niu et al., 2026） | https://arxiv.org/abs/2601.13995 | 知识树选择 |
| Instruction Data Selection via Answer Divergence（Li et al., 2026） | https://arxiv.org/abs/2604.10448 | 回答发散度选择 |
| MADS: Model-Aware Diverse Core Set Selection for Instruction Tuning（Bai et al., 2026） | https://arxiv.org/abs/2605.30857 | 激活覆盖式核心集 |
