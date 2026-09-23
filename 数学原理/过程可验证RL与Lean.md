---
title: "过程可验证 RL（Lean）：Process-Verified RL + Leanabell-Prover-V2（≠ AlphaProof / ≠ VPS）"
topic: 过程可验证RL与Lean
date: 2026-09-22
lines: [架构思想, 奖励接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.20068 # https://arxiv.org/abs/2606.20068
 - https://arxiv.org/abs/2507.08649 # 0.96MiB / 23p；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2606.20068
 - https://arxiv.org/pdf/2606.20068
 - https://arxiv.org/abs/2507.08649
 - https://arxiv.org/pdf/2507.08649
 - https://github.com/Leanabell-LM/Leanabell-Prover-V2
arxiv: ["2606.20068", "2507.08649"]
related: ["可验证过程监督", "过程奖励模型PRM谱系", "推理时扩展TestTimeScaling", "GRPO与DAPO算法族"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 过程可验证 RL（Lean）：Process-Verified RL + Leanabell-Prover-V2（≠ AlphaProof / ≠ VPS）

> **定位**：[[过程可验证RL与Lean]] **P1 形式化 / 可验证 RL 增量切片**——在 **[[形式化验证与LLM]]** 已立「VeriCoT（Z3）+ AlphaProof（Lean 树搜索 RL / TTRL）」、**[[可验证过程监督]]** 已立「可验证过程监督（VPS / VPRM）」之后，本卡只写 **Lean 细粒度过程反馈直接打进 RL** 的近窗两条：
> - **Process-Verified RL**（*Process-Verified Reinforcement Learning for Theorem Proving via Lean*，arXiv:**2606.20068**v1，页眉 **ICLR 2026** / arXiv 行 **18 Jun 2026**）：把 Lean 阐述 / AST / 错误日志压成 **tactic 级稠密可验证奖励**，注入 GRPO 式目标（first-error propagation + first-token credit）。
> - **Leanabell-Prover-V2**（*Verifier-integrated Reasoning for Formal Theorem Proving via Reinforcement Learning*，arXiv:**2507.08649**v1，页眉 **11 Jul 2025**）：在 long CoT 里 **多轮调用 Lean 4 verifier**，用反馈做反思改写 + DAPO；feedback token masking。
> **攻坚线**：**架构思想 / 奖励接口（主）** + **文内 MiniF2F / ProofNet（及 Leanabell 的 ProverBench）字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[形式化验证与LLM]]**：禁止复述 **AlphaProof IMO / TTRL / 树搜索通史**，禁止重写 VeriCoT→Z3 FOL 校验主文。本卡 **不**写 AlphaZero 式证明搜索、auto-formalization 课程或 IMO 2024 叙事；Lean 只作 **训练期过程奖励宿主**。
> - **≠ [[可验证过程监督]]**：禁止重写 **VPS 结构先验 + 确定性声明核验** 或 **VPRM 医学 RoB 规则逐步分**。本卡信号来自 **Lean 内核/阐述**，不是棋类引擎或 Cochrane 指南决策树。
> - **≠ [[过程奖励模型PRM谱系]]**：禁止重写 Lightman / Math-Shepherd / 学习式 PRM 谱系。两文均 **不训神经逐步 RM**；Process-Verified 明确对照「无外部 PRM」。
> - **≠ [[推理时扩展TestTimeScaling]]**：禁止写成 TTS / o1 / R1 产品通史；pass@k 仅作文内采样预算字段，不串推理时缩放通史。
> - **禁止复述 AlphaProof IMO/TTRL 长文**（议程硬禁）。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。文内未给的超参网格 / 未发表联合实验 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A · Process-Verified RL** | Kim & Yun (KAIST AI), *Process-Verified Reinforcement Learning for Theorem Proving via Lean* | arXiv:**2606.20068v1** \[cs.AI\] **18 Jun 2026**；页眉 *Published as a conference paper at ICLR 2026*；XMP MetadataDate 2026-06-19T00:53:42Z（→ **2026-06-19 08:53 CST**）；CC-BY-4.0；`https://arxiv.org/abs/2606.20068`（**10,407,700 B ≈ 9.93MiB** / **28** 页 letter） | 主锚：Lean = tactic 级过程 oracle → GRPO |
| **主文 B · Leanabell-Prover-V2** | Ji, Liu, Wang♥, Zhang, Yue, Shi, Sun, Zhang, Zhou & Gai (Klear Team, Kuaishou), *Leanabell-Prover-V2: Verifier-integrated Reasoning for Formal Theorem Proving via Reinforcement Learning* | arXiv:**2507.08649v1** \[cs.AI\] **11 Jul 2025**；XMP MetadataDate 2025-07-14T00:50:01Z（→ **2025-07-14 08:50 CST**）；arXiv nonexclusive-distrib 1.0；`https://arxiv.org/abs/2507.08649`（**1,004,898 B ≈ 0.96MiB** / **23** 页 A4） | 主锚：多轮 verifier-integrated CoT + DAPO |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| Process-Verified PDF | `https://arxiv.org/abs/2606.20068` | **9.93MiB** | **28** | 官方 HTTPS 外链（≈9.93MiB） |
| Process-Verified 抽取 | | **98K**（100,318 B） | — | 全文检索 |
| Leanabell-V2 PDF | `https://arxiv.org/abs/2507.08649` | **0.96MiB** | **23** | **官方 HTTPS 外链**（≪10MB） |
| Leanabell-V2 抽取 | | **87K**（88,826 B） | — | 全文检索 |

**代码入口（文内明示，2026-09-22 未做线上可用性核验）：**
- Leanabell-Prover-V2：`https://github.com/Leanabell-LM/Leanabell-Prover-V2`（源码 / 数据 / 模型）
- Process-Verified RL：正文未给独立公开仓链接（以 PDF / 作者页为准；**不编造 URL**）。

**一句话抓手：**
[[形式化验证与LLM]] 回答「形式系统怎么给 LLM 接地」；[[可验证过程监督]] 回答「过程标签怎么从确定性域规则来」；本卡回答「**Lean 的细粒度反馈怎么变成 RL 信用分配**」——Process-Verified 把 **阐述成功 / 首错传播** 压成 tactic 标量打进 GRPO；Leanabell-V2 把 **编译成败日志** 嵌进 long CoT 多轮反思。与「终局二进制 RLVR」和「PRM 神经打分」可硬划界。

---

## 二、议题边界：Lean 过程奖励接口 ≠ 树搜索通史 / ≠ VPS / ≠ PRM / ≠ TTS

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **VeriCoT + AlphaProof** | Z3 FOL 校验；Lean 树搜索 RL / TTRL / IMO | **[[形式化验证与LLM]]** | **否**（禁 AlphaProof 长文；禁 VeriCoT 主文） |
| **VPS + VPRM** | 结构先验 + 确定性声明/规则逐步核验 | **[[可验证过程监督]]** | **否**（禁棋类/GSM8K VPS；禁医学 RoB） |
| **学习式 PRM** | 人类/自动逐步标签 → 神经逐步 RM | **[[过程奖励模型PRM谱系]]** | **否**（禁 PRM800K / Math-Shepherd 通史） |
| **TTS / 长 CoT 产品叙事** | o1 / R1 推理时缩放 | **[[推理时扩展TestTimeScaling]]** | **否**（pass@k 仅作文内字段） |
| **Process-Verified + Leanabell-V2** | Lean tactic/编译反馈 → RL 信用 / 多轮反思 | **本篇** | **是** |

跟读直觉：共享「Lean / 可验证 / 过程」词表，但 **信号宿主与训练接口不同**——AlphaProof 是搜索+终局/长度环境；VPS 是域规则声明核验；PRM 是再训一个打分器；本卡是 **把 Lean 已有的结构化输出接到 RL 目标**。

`
 形式化 / 过程监督近窗
 │
 ┌─────────┼──────────┬────────────┐
 │ │ │ │
 [[形式化验证与LLM]] [[可验证过程监督]] [[过程奖励模型PRM谱系]] [[推理时扩展TestTimeScaling]]
 AlphaProof VPS/VPRM 神经 PRM TTS 通史
 +VeriCoT 域规则核验 逐步打分器 o1/R1
 │ │ │ │
 └─────────┴────┬─────┴────────────┘
 │ 禁止复读
 ▼
 ★ [[过程可验证RL与Lean]] Process-Verified ‖ Leanabell-V2
 tactic 稠密可验证奖励 ‖ 多轮 verifier-integrated CoT
`

### 2.2 两条主轴正交（本卡骨架）

| | **Process-Verified RL** | **Leanabell-Prover-V2** |
|---|---|---|
| 核心不满 | 二进制 outcome RLVR 稀疏；PRM 又要逐步标注且对 Lean 不适用 | 小模型（7B）在小采样预算下难以产高质量 Lean；标准 RL 奖励多样性不足 |
| Lean 用法 | **训练期过程 oracle**：解析 tactic 序列 + 阐述/错误 → $\phi(Y,T)$ | **轨迹内工具**：`<code>` 片段即时编译；失败则 `<interpreter>` 反馈进下一轮 |
| 过程信号粒度 | **tactic 级**（局部类型正确 vs 报错；首错后全否） | **整段 proof / 编译成败**（附录试过 AST 细奖励，文称未获有利结果） |
| 优化器接口 | GRPO 式；$A_{i,t}=A_{\mathrm{outcome}}+1\{t=\mathrm{first}(T)\}\cdot A_{\mathrm{process}}$ | DAPO（clip-higher、token-level loss）；$R_{\mathrm{format}}$ + $R_{\mathrm{success/fail}}$ |
| 生成形态 | **非 CoT 纯 Lean 证明**（whole-proof generation） | **verifier-integrated long CoT**（NL 反思 + Lean 片段） |
| 冷启动 | 直接在 STP / DeepSeek-Prover 上做 RL | Claude-3.7 协助构造 incorrect→corrected 对 + 四场景 SFT；feedback token masking |
| 主评测场 | MiniF2F-Test / ProofNet-Test（STP-Lean、DeepSeek-Prover-V1.5） | MiniF2F-test / ProofNet-test / ProverBench（Kimina / DeepSeek-Prover-V2 7B） |

**交叉一句（文内互指，不外推联合实验）：** Process-Verified Related Work 点名 Ji et al. 2025（即 Leanabell 线）为「少数把细粒度监督写入训练」的工作之一；Leanabell §2.3 写明基于 AST 的精致奖励「have not obtained favorable results」，把「AST → 有效反思奖励」留作开放问题——与 Process-Verified 在 **非 CoT、tactic first-token** 设定下跑通稠密信号形成对照，**不是**同文续作。

---

## 三、Process-Verified RL：Lean 作符号过程 oracle

### 3.1 问题与主张（Abstract / §1 / Contributions）

**主张（压缩）：** RLVR 常只吃 **单一二进制验证**；Lean 却能提供稠密、类型论接地的结构化反馈。本文把 Lean 同时当作 **outcome 与 tactic 级过程 oracle**——证明尝试解析为 tactic 序列，阐述标记局部正确步与 **最早失败步**，再注入 GRPO 式目标。相对 outcome-only，tactic 监督在多数设定上抬升 MiniF2F / ProofNet；且 **无需 NL 引导、无需外部 PRM**。

**三项贡献（§1 原文结构）：**
1. 形式化 Lean 的符号 tactic 反馈 → 可映射到 token 级信用的标量；
2. 将 outcome + tactic 奖励并入 RL（稠密且可验证的信用分配）；
3. 在 MiniF2F / ProofNet 上相对 outcome-only 与 vanilla 基线更稳的增益。

### 3.2 Lean 反馈形式化（§3.1）

证明 $Y$ = AST 排序后的 tactic 序列 $(T_1,\ldots,T_{N(Y)})$。
- $g(Y)\in\{0,1\}$：整证是否过 Lean；
- $\phi(Y,T)\in\{1,d_1,d_2\}$：
 - $g=1$ → 全 1；
 - $g=0$ 且 $T$ 无错误 → $d_1$（局部阐述成功但仍未完成）；
 - $g=0$ 且 $T$ 含错误 → $d_2$。

文强调：**未出现在错误日志中的 tactic = 依赖类型论下局部可靠**，即使后续子目标未关或不构成完整证明——即 **tactic-level soundness ≠ proof-level completeness**。

### 3.3 奖励接口：first-error + first-token（§4）

**First-error propagation：** 令 $j=\min\{i:T_i\text{ 报错}\}$，则 $k\ge j$ 一律当错误（$\phi=d_2$）。因果理由：LLM 自回归，首错后前缀已无效，后续无法「救回」。

**优势组合（主公式）：**
$$
A_{i,t}=A_{\mathrm{outcome},i,t}+\mathbf{1}\{t=\mathrm{first}(T_{i,s(i,t)})\}\cdot A_{\mathrm{process},i,s(i,t)}
$$
- $A_{\mathrm{outcome}}$：组内 $g(Y)$ 标准化，**均匀**加到该响应所有 token；
- $A_{\mathrm{process}}$：$\phi(Y,T)-\mathrm{mean}(g)$（难度基线）；**只打到每个 tactic 的首 token**（通常是 `intro`/`apply`/`have` 等 tactic 关键字）。

主实验：$d_1=-0.05$，$d_2=-0.1$；训练 10k STP 子集；Lean REPL **15s** timeout；非 CoT 提示风格对齐 Xin et al. 2024b。

**消融要点（Table 2–4，STP-Lean）：**
- **Outcome+Tactic > Outcome-only / Tactic-only**（Table 2）：MiniF2F pass@64 **59.2%±0.5** vs Outcome-only **57.9%±0.5** vs Tactic-only **56.8%±0.6**。
- **First token** 优于 all-tokens / last-token / entropy 抽样（Table 3）。
- 去掉 first-error、去掉难度基线、或 $d_1=d_2$ 均伤稳定性（Table 4：Same tactic reward 在 MiniF2F 偶有涨、ProofNet 掉）。

### 3.4 文内评测字段（Process-Verified）

**主表（Table 1，whole-proof 块；7B；预算 = 每题采样 N）：**

| 模型 | Budget | MiniF2F-Test | ProofNet-Test |
|---|---:|---:|---:|
| STP-Lean | 32 / 64 | 55.9%±0.2 / 56.7%±0.2 | 17.2%±0 / 19.1%±0.4 |
| **STP-Lean + Ours** | 32 / 64 | **57.1%±0.8 / 59.2%±0.5** | **18.6%±0.3 / 19%±0.3** |
| DeepSeek-Prover-V1.5 + STP | 32 / 64 | 54.9%±0.7 / 57.2%±0.2 | 16.8%±0.3 / 17.7%±0 |
| **+ STP + Ours** | 32 / 64 | **56.3%±0.6 / 57.8%±0.4** | **17.6%±0.8 / 18.5%±0.3** |

文述：STP-Lean + Ours 相对基线 MiniF2F 最高约 **+2.5%p**（pass@64）；ProofNet pass@32 **+1.4%p**，pass@64 几乎持平（−0.1%p）。相对强树搜索基线（如 InternLM2.5-StepProver 58.5%、DeepSeek+RMaxTS 等）是 **不同算力轴**（whole-proof 采样 vs 搜索扩展），表注已声明不可直接比。

**动态（Fig.2）：** Outcome+Tactic 相对单信号更稳；熵更低但平均证明长度不因「灌水」变长。
**Timeout（Fig.3）：** 5s 最差；**15s** 总体最佳；10–15s 有时优于 30s——文归因于丢弃过复杂证明、偏向短证明策略。

**局限（文 Limitations）：** 未与学习式 PRM 对比（Lean 缺 NL CoT 逐步标注）；模型输出 **无 long CoT**；$d_1,d_2$ 固定且敏感；需要更好的优势估计器与大规模 tactic 级数据。

---

## 四、Leanabell-Prover-V2：多轮 verifier-integrated CoT RL

### 4.1 问题与主张（Abstract / §1）

**主张（压缩）：** 在 Leanabell-V1 之后，V2 主升级是 **用 Lean 4 verifier 反馈做 RL**。Verifier 告知成败与具体错误，使模型对自身推理「自知」并学反射纠错。直接对 **多轮 verifier 交互轨迹** 优化；配合 **feedback token masking** 与简单奖励。相对基线：Kimina-Prover-Preview-Distill-7B MiniF2F pass@128 **+3.2%**（67.2→70.4）；DeepSeek-Prover-V2-7B **+2.0%**（76.2→78.2）（Abstract / Fig.1）。

**动机切片（≠ AlphaProof 搜索叙事）：** 形式推理评测常依赖极大 pass@k（32→1024），而实用 RL rollout 往往只有 8–32；7B 骨干在标准配置下难维持奖励多样性。解法不是加大树搜索（[[形式化验证与LLM]] 轴），而是 **把 verifier 嵌进 long CoT 即时多轮修正**。

### 4.2 方法接口（§2）

**问题形式：** 无 verifier 交互时最大化 $P(y_i=1)$（整证过检）；引入反馈后优化 $P(\hat y_i=1)$，其中 $\hat p_i$ 是依 $o_i$ **改写后**的证明——目标显式变成 **学纠错**。

**Cold-start（§2.2）：**
1. 基线 prover 多样本生成；
2. Lean 过滤；
3. 失败样本 + 错误日志 → Claude-3.7-Sonnet 改写；
4. 再验证 → incorrect–corrected 对。
四场景拼接 long CoT（≈2K+2K+2K+1K 量级，文内约数）；特殊标记 `<code></code>` / `<interpreter></interpreter>`。
**Feedback token masking：** verifier 文本非模型生成 → SFT/RL 均 mask，只学改写/续写侧。

**RL（§2.3）：** DAPO；约束组内 $0<|\{\text{valid}\}|<G$；$\varepsilon_{\mathrm{low}}=0.2$，$\varepsilon_{\mathrm{high}}=0.28$。
**奖励：** $R_{\mathrm{format}}$ 较小（如 0.2）+ $R_{\mathrm{success}}/R_{\mathrm{failed}}$（如 1.0）；文称简单成败奖励足够。附录试 AST 结构化奖励 → **未获有利结果**（开放问题）。
**数据：** NuminaMath → Kimina-Autoformalizer-7B 形式化；按 pass@8 ∈ $[1/8,1/2]$ 筛题 → Kimina 线 **3.8K** / DeepSeek-V2 线 **1.7K** 语句；max len 16K，rollout 24，lr 1e-6。

### 4.3 文内评测字段（Leanabell-V2）

**MiniF2F-test（Table 1；主宣称数字）：**

| 方法 | pass@32 | pass@128 |
|---|---:|---:|
| Kimina-Prover-Preview-Distill-7B | 63.1% | 67.2%（pass@1024: 70.8%） |
| **Leanabell-Prover-V2-KM** | **68.4%** | **70.4%** |
| DeepSeek-Prover-V2-7B (CoT) | 75.6%±0.5% | 76.2%（pass@1024: 79.9%±0.3%） |
| **Leanabell-Prover-V2-DS** | **76.6%** | **78.2%** |

读表：KM 的 pass@128 **70.4%** ≈ 基线 pass@1024 **70.8%**（文称推理效率增益）；DS 在 pass@128 **+2.0%p**。

**RL 消融（Table 2，pass@32）：** Kimina + Vanilla RL **65.5%** vs + Our RL **68.4%**（相对基线 63.1：Vanilla +2.4 vs Ours +5.3）；DeepSeek + Vanilla **无增益（75.6%）**，Ours **76.6%**。

**迭代 verifier 调用（Table 3）：** 首轮反思 KM 64.7→68.4（+3.7），DS 75.4→76.6（+1.2）；KM 迭代至 3 轮可到 **69.2%**；DS 多轮平台。树宽 32-4 对 KM 略涨（68.4→68.8）。

**ProofNet-test（Table 4）：** KM **18.2%** @128 vs 基线 **11.8%**（**+6.4%p**，与引言一致）；DS **25.2%** @128 ≈ 基线 25.4%±0.7（文称可比、无显著提升）。

**ProverBench（Table 5）：** KM All @128 **42.9%**（基线 34.8%，约 +8.1%p）；DS All 略低于基线（48.7 vs 50.8），但 AIME 24&25 **2/15**（基线 1/15）——文称「多解出一套」难题。

**局限（§4）：** 题变难后「可激活」RL 提示变少（题库小 + pass 率过滤）；对已很强的 DeepSeek-Prover-V2-7B，额外 RL 收益递减。

---

## 五、对照小结与可行动取舍

| 决策问题 | 更贴哪条 | 依据（文内） |
|---|---|---|
| 要 **tactic 级稠密、类型论接地** 的信用，且输出是纯 Lean whole-proof | **Process-Verified** | first-error + first-token；Table 2 Outcome+Tactic 优于单信号 |
| 要 **小模型在 CoT 里学会调用 verifier 纠错** | **Leanabell-V2** | 多轮 `<interpreter>`；Table 2 verifier-integrated ≫ vanilla RL |
| 已有强 DS-V2-7B、再榨 hard 题 | 预期 **边际小** | Leanabell 局限段；Process-Verified 在 DS-V1.5 上增益也偏温和 |
| 想上 **神经 PRM / AlphaProof 树搜 / VPS 声明核验** | **不要用本卡当主文** | → [[过程奖励模型PRM谱系]] / [[形式化验证与LLM]] / [[可验证过程监督]] |

**跟读口诀：**
- Process-Verified = **「Lean 阐述日志 → GRPO 的过程优势」**（训练期 oracle，非搜索）。
- Leanabell-V2 = **「Lean 编译服务 → CoT 内多轮工具调用 + DAPO」**（轨迹内反思，过程奖励仍偏 outcome）。
- 二者都 **≠** AlphaProof 的 TTRL/IMO 长文，**≠** VPS 的域规则过程监督，**≠** PRM 神经打分。

---

## 六、来源与核验

| 项 | 值 |
|---|---|
| 主 PDF | `https://arxiv.org/abs/2606.20068`（**10,407,700 B ≈ 9.93MiB** / 28p）；`https://arxiv.org/abs/2507.08649`（**1,004,898 B ≈ 0.96MiB** / 23p） |
| 抽取 | `{process-verified-rl,leanabell-prover-v2}.txt`（及 镜像） |
| 抽取命令 | （2026-09-22 CST） |
| 备注 | **两篇均官方 HTTPS 外链**；Process-Verified 体积偏中 → ****；Leanabell |
| 未核 / 禁写 | AlphaProof IMO/TTRL 通史；VPS/VPRM 主文；PRM 谱系；未公开的 Process-Verified 代码仓；AST 细奖励「应能工作」的外推 |

**变更记录：** 2026-09-22 CST — 初稿 draft：双主锚深读 + 四向划界；表数字锚定本地抽取。
