---
title: "过程可验证 RL（Lean）：Process-Verified RL + Leanabell-Prover-V2（≠ AlphaProof / ≠ VPS）"
topic: 过程可验证RL与Lean
date: 2026-09-22
lines: [架构思想, 奖励接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.20068
 - https://arxiv.org/abs/2507.08649
aux:
 - https://arxiv.org/abs/2606.20068
 - https://arxiv.org/abs/2507.08649
 - https://github.com/Leanabell-LM/Leanabell-Prover-V2
arxiv: ["2606.20068", "2507.08649"]
related: ["形式化验证与LLM", "可验证过程监督", "过程奖励模型PRM谱系", "GRPO与DAPO算法族", "推理时扩展TestTimeScaling", "对齐与强化学习发展时间线"]
retrieval_cutoff: 2026-08-05
timezone: Asia/Shanghai (CST)
---

# 过程可验证 RL（Lean）：Process-Verified RL + Leanabell-Prover-V2（≠ AlphaProof / ≠ VPS）

> **主要来源**：[Process-Verified Reinforcement Learning for Theorem Proving via Lean](https://arxiv.org/abs/2606.20068)（Kim、Yun，KAIST AI，ICLR 2026，v1 2026-06-18，以下简称 Process-Verified）；[Leanabell-Prover-V2: Verifier-integrated Reasoning for Formal Theorem Proving via Reinforcement Learning](https://arxiv.org/abs/2507.08649)（Ji、Liu、Wang 等，快手 Klear 团队，v1 2025-07-11，以下简称 Leanabell-V2）（截至 2026-08-05）。
> **研究线**：架构思想（主：Lean 的细粒度反馈怎样接进强化学习的信用分配）；奖励接口与评测字段（辅：MiniF2F、ProofNet、ProverBench 上的 pass@k）
> **范围与相邻笔记**：
> - ≠ [[形式化验证与LLM]]：那篇写 AlphaProof 的树搜索、测试时强化学习与 IMO，以及 VeriCoT；本篇只写 Lean 作为训练期反馈来源。
> - ≠ [[可验证过程监督]]：那篇的过程信号来自棋类引擎与医学指南，本篇来自 Lean 的阐述结果与报错。
> - ≠ [[过程奖励模型PRM谱系]]：两文都不训练神经逐步奖励模型。
>
> **意义**：定理证明的强化学习通常只用一个二值信号，整份证明过没过 Lean，可 Lean 实际上会指出哪一步出错、错在哪里。两文把这部分信息用起来，方式不同。Process-Verified 把 Lean 的阐述结果压成 tactic 级奖励：报错之前的 tactic 算局部正确，第一处报错及之后全算错，奖励只打在每个 tactic 的第一个 token 上，再与结果奖励一起进入 GRPO 式目标，STP-Lean 的 MiniF2F pass@64 从 56.7% 升到 59.2%。Leanabell-V2 让模型在长思维链里多次调用 Lean 编译证明片段，读到报错后反思改写，用 DAPO 训练，Kimina 基座的 pass@128 从 67.2% 升到 70.4%，接近基座 pass@1024 的 70.8%。两文说明 Lean 不只是终点的判官，也可以是训练过程中的稠密反馈源；目前增益都在几个百分点，对已经很强的基座收益递减。

## 一、问题背景

可验证奖励强化学习（RLVR）在定理证明上天然合适：Lean 内核接受的证明就是对的。但只用「过或不过」的二值结果，信号稀疏：一份长证明错在最后一步和错在第一步得到同样的零分。学习式过程奖励模型需要逐步标注，而 Lean 证明缺少自然语言思维链，也没有现成的逐步标注数据。另一方面，Lean 的输出本来就是结构化的：证明可以解析成 tactic 序列，阐述器会报告每个 tactic 是否出错、错误信息是什么。

两文各自回答一个问题。Process-Verified 问：能否直接把 Lean 的阐述结果变成 tactic 级的过程奖励，而不另训打分器。Leanabell-V2 问：7B 级证明模型在训练时只能负担 8–32 次采样，评测却常用 pass@1024 级别的大预算，能否让模型在一次生成里借助 Lean 的反馈自己改错。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-05 | [DeepSeek-Prover](https://arxiv.org/abs/2405.14333) | 自动形式化竞赛题，合成大规模 Lean 4 证明数据，整份证明一次生成 |
| 2024-07 | [Lean-STaR](https://arxiv.org/abs/2407.10040) | 在每个 tactic 前插入自然语言思考 |
| 2024-08 | [DeepSeek-Prover-V1.5](https://arxiv.org/abs/2408.08152) | 用证明助手反馈做强化学习（RLPAF），加内在奖励驱动的树搜索 RMaxTS |
| 2025-01 | [STP](https://arxiv.org/abs/2502.00212) | 猜想者与证明者自博弈，缓解正确证明稀少造成的稀疏奖励 |
| 2025-03 | [DAPO](https://arxiv.org/abs/2503.14476) | 开源的大规模强化学习配方，解耦裁剪上下界、动态采样、token 级损失 |
| 2025-04 | [Kimina-Prover Preview](https://arxiv.org/abs/2504.11354) | 从 Qwen2.5-72B 做大规模强化学习，以「形式推理模式」长思维链生成 Lean 证明 |
| 2025-04 | [DeepSeek-Prover-V2](https://arxiv.org/abs/2504.21801) | 子目标分解的冷启动加强化学习，发布 325 题的 ProverBench |
| 2025-07 | Leanabell-V2 | 长思维链内多轮调用 Lean 验证器，读反馈反思改写，DAPO 训练 |
| 2026-06 | Process-Verified | Lean 阐述结果变成 tactic 级奖励，首错传播加首 token 信用 |

## 三、Process-Verified：Lean 作为符号过程预言机

**反馈的形式化**（§3.1）：一份证明按语法树顺序解析成 tactic 序列。整份证明通过时每个 tactic 记 1；未通过时，没有出现在错误日志里的 tactic 记 d1（局部阐述成功但证明未完成），出错的记 d2。作者强调，在依赖类型论下没报错的 tactic 是局部可靠的，即便后续子目标没关上；tactic 级可靠不等于整份证明完整。

**奖励接口**（§4）：

- **首错传播**：第一处报错之后的 tactic 一律记为错误。理由是模型自回归生成，前缀一旦无效，后面无法挽回。
- **优势组合**：结果优势按组内标准化整份证明是否通过，均匀加到该回答的所有 token；过程优势为 tactic 分数减去组内通过率（作难度基线），只加到每个 tactic 的第一个 token（通常是 intro、apply、have 这类关键字）。
- **主实验设定**（§5.1）：d1 = −0.05、d2 = −0.1；从 STP 数据集（326 万份证明）随机取 10k 条训练；Lean REPL 每次 15 秒超时；不用思维链，直接生成完整 Lean 证明。

**主结果**（Table 1，7B，预算为每题采样数）：

| 模型 | 预算 | MiniF2F-test | ProofNet-test |
|---|---:|---:|---:|
| STP-Lean | 32 / 64 | 55.9% / 56.7% | 17.2% / 19.1% |
| STP-Lean + 本法 | 32 / 64 | 57.1% / 59.2% | 18.6% / 19% |
| DeepSeek-Prover-V1.5 + STP | 32 / 64 | 54.9% / 57.2% | 16.8% / 17.7% |
| DeepSeek-Prover-V1.5 + STP + 本法 | 32 / 64 | 56.3% / 57.8% | 17.6% / 18.5% |

- **单信号对比**（Table 2，STP-Lean，MiniF2F pass@64）：结果加 tactic 奖励 59.2%，只用结果奖励的 GRPO 57.9%，只用 tactic 奖励 56.8%。作者指出只用结果奖励时，GRPO 在 DeepSeek 基座的 ProofNet 上没有增益，有时还不如监督基线。
- **信用分配位置**（Table 3）：只打第一个 token 优于打全部 token、最后一个 token 或按熵抽样。
- **奖励策略**（Table 4）：去掉首错传播、去掉难度基线或令 d1 = d2，都会损害稳定性。
- **超时**（§5）：5 秒最差，15 秒总体最好；作者认为较短超时会丢弃过于复杂的证明，偏向短证明策略。
- **与树搜索比**：本法 pass@64 的 59.2% 接近 InternLM2.5-StepProver 树搜索的 58.5%，但两者的预算一个数整份证明采样、一个数搜索扩展次数，表注说明不可直接比较。

## 四、Leanabell-V2：在思维链里调用验证器

**目标**（§2）：没有验证器交互时，优化的是整份证明一次通过的概率；引入反馈后，优化的是依据 Lean 反馈改写后的证明通过的概率，即显式地学习纠错。

**冷启动**（§2.2）：基座证明模型多次采样，Lean 过滤出失败样本，把失败证明和错误日志交给 Claude-3.7-Sonnet 改写，再经 Lean 验证，得到「错误–修正」对，拼成四种场景的长思维链 SFT 数据。证明片段放在 `<code>` 标签里，验证器返回的信息放在 `<interpreter>` 标签里。验证器返回的文本不是模型生成的，SFT 与强化学习时都屏蔽这部分 token 的损失。

**强化学习**（§2.3）：用 DAPO，裁剪下界 0.2、上界 0.28，只保留组内既有成功又有失败的题。奖励只有格式奖励与成败奖励两部分，作者称简单的成败奖励已足够；附录 B 尝试过基于语法树的细粒度奖励，没有得到有利结果。训练题来自 NuminaMath，经 Kimina-Autoformalizer-7B 形式化，按 pass@8 落在 1/8 到 1/2 之间筛题，Kimina 基座用 3.8K 道、DeepSeek 基座用 1.7K 道。

**结果**（Table 1、4、5）：

| 模型 | MiniF2F pass@32 | MiniF2F pass@128 | ProofNet pass@128 | ProverBench pass@128 |
|---|---:|---:|---:|---:|
| Kimina-Prover-Preview-Distill-7B | 63.1% | 67.2% | 11.8% | 34.8% |
| Leanabell-V2（Kimina 基座） | 68.4% | 70.4% | 18.2% | 42.9% |
| DeepSeek-Prover-V2-7B | 75.6% | 76.2% | 25.4% | 50.8% |
| Leanabell-V2（DeepSeek 基座） | 76.6% | 78.2% | 25.2% | 48.7% |

- **与普通强化学习比**（Table 2，pass@32，奖励与优化器配置相同）：Kimina 基座普通强化学习 65.5%、本法 68.4%；DeepSeek 基座普通强化学习没有增益（75.6%），本法 76.6%。
- **多轮调用**（Table 3）：Kimina 基座在第一轮反思后从 64.7% 升到 68.4%，迭代到第三轮为 69.2%；DeepSeek 基座多轮后停在 76.6%。
- **难题**：ProverBench 中的 15 道 AIME 题，DeepSeek 基座版解出 2 道，基座解出 1 道。

## 五、意义

两文把 Lean 的作用从「最后判对错」扩展到训练过程本身，路线互补。Process-Verified 不改变生成形式，把 Lean 已经产生的阐述信息变成 tactic 级的稠密奖励，代价几乎为零，因为两种训练都要调用 Lean REPL，额外的排序与打分开销可忽略。Leanabell-V2 改变生成形式，让验证器进入推理轨迹，模型在一次回答里就能看到报错并改写，用较小的采样预算换来接近大预算的效果。两文的过程信号都来自形式系统本身而不是神经打分器，这与可验证过程监督在棋类、医学领域的思路一致。Leanabell-V2 在语法树细粒度奖励上没有成功，而 Process-Verified 在不用思维链、只奖第一个 token 的设定下把类似的细粒度信号用了起来；两文没有联合实验，不能直接推出两者可以叠加。

## 六、局限与待核实

- **Process-Verified 的增益很小**：作者称 STP-Lean 上 MiniF2F 最多 +2.5 个百分点（pass@64），ProofNet +1.4（pass@32）、pass@64 −0.1；DeepSeek 基座上的提升为「marginal yet consistent」（§5.2）。STP-Lean 的 ProofNet pass@64 与只用结果奖励持平（都是 19%），DeepSeek 基座的 MiniF2F pass@64 与只用 tactic 奖励持平（都是 57.8%）。作者自陈没有和学习式 PRM 比较（Lean 缺少带思维链的逐步标注），模型不生成长思维链，d1、d2 是固定值且对模型和数据集较敏感。文中没有给出代码地址。只有 v1。
- **Leanabell-V2 的收益依赖基座强弱**：对已经很强的 DeepSeek-Prover-V2-7B，ProofNet 与 ProverBench 上略低于基座。作者自陈题目越难，能激活强化学习的题越少（难题集本身小，又按通过率过滤）。多轮调用会在首轮之后追加采样，与基座的 pass@k 不是严格同预算的比较；Table 3 的首轮基线 64.7% 与 Table 1 中基座的 63.1% 口径不同，前者是本模型思维链中第一个代码块的结果。冷启动数据依赖 Claude-3.7-Sonnet。只有 v1。
- **两文不能横比**：基座、生成形式（整份证明与长思维链）、预算和评测集都不同；两文结果均为作者自报。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[形式化验证与LLM]] | 同用 Lean：AlphaProof 只用证明成败与长度做 AlphaZero 式强化学习，本篇把阐述报错接进训练信号 | AlphaProof、VeriCoT 与 IMO |
| [[可验证过程监督]] | 同一思路的另一领域：那篇用引擎与指南规则给中间步骤打分 | 棋类与医学的规则奖励 |
| [[自然语言证明与自验证推理]] | 对照：本篇的奖励来自 Lean 报错，那篇的奖励来自检查自然语言证明的学习式验证器 | 证明验证器的训练与评测 |
| [[过程奖励模型PRM谱系]] | 对照：两文的过程信号来自 Lean，不训练神经逐步打分器 | PRM 的标注与训练 |
| [[GRPO与DAPO算法族]] | Process-Verified 改造 GRPO 式的优势，Leanabell-V2 直接使用 DAPO | 算法配方本身 |
| [[推理时扩展TestTimeScaling]] | Leanabell-V2 的 pass@128 接近基座 pass@1024，相当于把推理时采样预算换成训练期学到的纠错 | 推理时扩展的方法谱系 |
| [[对齐与强化学习发展时间线]] | 时间线的 2025-07、2026-06 两个节点即本篇两文 | 对齐与强化学习通史 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Process-Verified](https://arxiv.org/abs/2606.20068) §3–4 | tactic 级反馈的形式化、首错传播与首 token 信用 |
| 2 | [Process-Verified](https://arxiv.org/abs/2606.20068) Table 2–4 | 单信号、信用位置与奖励策略的消融 |
| 3 | [Leanabell-V2](https://arxiv.org/abs/2507.08649) §2 | 冷启动数据、反馈屏蔽与 DAPO 设定 |
| 4 | [DeepSeek-Prover-V1.5](https://arxiv.org/abs/2408.08152) | 用证明助手反馈做强化学习的前身 |
| 5 | [STP](https://arxiv.org/abs/2502.00212) | Process-Verified 的基座与训练数据来源 |
