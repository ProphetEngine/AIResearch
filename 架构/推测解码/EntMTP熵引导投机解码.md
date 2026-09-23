---
title: "投机解码新变体：EntMTP（熵引导 MTP / 动态草稿树）"
topic: EntMTP熵引导投机解码
date: 2026-09-22
lines: [架构思想, 延迟/接受率字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.27550
arxiv: ["2606.27550"]
related: ["推理引擎生态", "EAGLE3投机解码"]
archived: 2026-09-22
---

# 投机解码新变体：EntMTP（熵引导 MTP / 动态草稿树）

> **定位**：EntMTP **P1 Infra**——在 **B7** 已立投机「草稿—校验」基线、**[[EAGLE3投机解码]]** 已补 **EAGLE-3**（training-time test + 多层特征融合）之后，只写近窗 **EntMTP**（*Entropy Guided Multi-Token Prediction*，arXiv **2606.27550**）：**训练免费**的运行时调度器，按局部可预测性在 **预编译 TopologyBank** 上切换草稿树拓扑。
> **攻坚线**：**架构思想（主）**——离线吞吐 Pareto 前沿 → TopologyBank → 熵/路径价值驱动的 per-step 选树；**延迟 / 接受率字段（辅）**——相对 Hydra / Medusa **默认树** 的 tok/s、ρ、τ（Table 1）。
> **硬划界**：
> - **≠ B7**：不写 Leviathan / Chen / Lookahead 通史与引擎选型全文；「草稿—并行校验、同分布」只当接口一句。
> - **≠ [[EAGLE3投机解码]]**：不重写特征回归解除、多层融合、SGLang 大 batch 表；本文仅借用文中 **EAGLE-2 path value** 作为调度特征定义。
> - **禁止升格**：Hydra / Medusa / Lookahead **不得**写成新主文或谱系课——只作本 PDF 对照列与默认树基线；细节回指 **B7 / [[EAGLE3投机解码]]**。
> **禁止编造**：倍率、tok/s、τ、节点数、阈值、硬件一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息

| 字段 | 核实值（PDF / ） |
|---|---|
| 标题 | *EntMTP: Accelerating LLM Inference with Entropy Guided Multi Token Prediction* |
| 作者 | Carrie Chen（Cornell University；`cc2864@cornell.edu`） |
| arXiv | **2606.27550v1** \[cs.CL\]（**25 Jun 2026**） |
| 官方 PDF | `https://arxiv.org/abs/2606.27550`（**7** 页 letter；1,364,886 bytes；arXiv GenPDF） |
| 抽取 | （同步 ） |
| HTML | https://arxiv.org/html/2606.27550v1（议程备链；数字以官方 PDF 为准） |
| 代码 | 正文 / 摘要 **未给出** GitHub 链接 → 本卡不编造仓址 |

**一句话抓手：** 现有 MTP 头（Medusa / Hydra 路线）推理期锁死 **一张静态草稿树**——验证算力与推测深度不随上下文熵变化；EntMTP **不改**目标权重、**不松** Hydra 式接受条件，只在离线挑好的 **任务特异 Pareto 树** 上做 **O(1) 拓扑切换**，把推测深度对齐到局部可预测性。

---

## 二、议题边界：只写「熵→选树」，不写投机通史 / EAGLE-3

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **B7 投机通史** | 「廉价草稿 + 目标并行校验、边际分布不变」 | Leviathan / Chen 证明、Lookahead、引擎对比全文 |
| **[[EAGLE3投机解码]]** | EAGLE-2 **path value** $V_i$ 可作置信度代理（文 §2.2 / §4） | training-time test、低/中/高融合、SGLang Table 3–4 |
| **文内 Hydra / Medusa** | 默认树 tok/s 与「静态拓扑」诊断 | 独立成篇的 Hydra/Medusa 方法课、头结构设计通史 |

### 2.2 文内立轴：静态树为何与自然语言错位（摘要 / §1）

跟读压缩（非通史）：

1. MTP 头挂在目标 **最终 hidden**，用树状候选做稀疏校验——**自投机**默认路线。
2. 现有基础/开源 MTP **整段生成共用一张树拓扑** → 推测深度与验证算力 **常数**。
3. 自然语言熵不匀：**低熵**区可多步草稿；**高熵**区应保守。
4. 附录 A / Fig.3：接受长度的可预测特征 **随任务变**——ShareGPT 上近期接受历史强（EMA $r=0.49$）；GSM8K / HumanEval 上熵类特征相对更强，但 $|r|\le 0.22$——单拓扑跨分布难 Pareto 最优。

EntMTP 回答：**把任务依赖当信号**——离线建吞吐前沿，在线按状态在前沿上切换。

---

## 三、架构思想：离线前沿 → TopologyBank → 运行时策略

### 3.1 离线两段：接受前沿 → 吞吐前沿（§3）

沿用 Ankner / Cai 的「任务上离线选树」两段，但强调 **吞吐重排** 与 **任务特异**：

| 阶段 | 做法（跟读） |
|---|---|
| **接受前沿** | Algorithm 1：贪心加节点至预算 $B$；对所有一跳增广 $T\cup\{\nu\}$ 做 **一次联合树 self-rollout**，按路径 mask 估 mean accept length；并列打破：更小 child-rank 和、更浅深度 |
| **校准** | 100 prompts / 任务；$T=0.7$；posterior threshold $0.09$；$\alpha=0.3$；256-token rollouts |
| **偏差** | §3.1.1：联合树打分略乐观；Appendix B 用候选树 **自身** proposal / mask / KV 更新做 canonical self-rollout——偏置 $\le\pm 3.3\%$，**前沿拓扑不变** |
| **吞吐前沿** | 对接受前沿端到端测 wall-clock **tok/s**（含 prefill）；丢掉被支配拓扑；**吞吐最大树** → $\mathrm{EntMTP}^*$ 的静态任务最优树 |

Fig.1–2（HumanEval）：深度-4、节点 $\ge 23$ 时深度-4 树主导全局 Pareto；再映射到吞吐空间重排。GSM8K / ShareGPT 同协议见 Appendix C Fig.4–5。

### 3.2 TopologyBank：切换 = O(1) 指针交换（摘要 / §4 Cost）

每个前沿树预编译：

- attention mask
- position offsets
- gather / retrieve indices（文：`generate hydra buffers`）

推理期换树 = **字典指针交换**，无 mask 重建、无 kernel 重编。策略读出标量 $s$：对 $D\le 4$ 做 cumulative product + 一次 `.item()` sync，文称 **每步 $<0.1\,\mathrm{ms}$**。

### 3.3 调度特征：path-value 标量 $s$（§4）

不用另训模块。在校验器最后位置，用 **基座 top-1** $p_0$ 与各 Hydra 头 top-1 $p_d$：

$$
g_d = p_0 \prod_{i=1}^{d} p_i,\qquad
s = \max(p_0, g_1,\ldots,g_D)
$$

文称 $s$ 与期望接受长度单调相关：头链深层质量高时 $s\to 1$，大树才值得付验证成本。摘要亦写可用「EAGLE-2 path value」或「base top-1」等现成特征。

### 3.4 三种训练免费策略（摘要 / §4 Policy）

| 记号 | 行为 |
|---|---|
| $\mathrm{EntMTP}^*$ | **静态**：整段生成固定为该任务吞吐最优树（已优于 published default） |
| $\mathrm{EntMTP}_\tau$ | **二值 + 迟滞**：保守树 $T_-$（小/浅）↔ 激进树 $T_+$（大、depth-4）；$s>\tau_{\mathrm{on}}$ 上切，$s\le\tau_{\mathrm{off}}$ 回切，$\tau_{\mathrm{off}}\le\tau_{\mathrm{on}}$ 抑抖动；默认可 $\tau_{\mathrm{on}}=\tau_{\mathrm{off}}=\tau$ |
| $\mathrm{EntMTP}\text{-}l$ | **阈值阶梯**：把 $s$ 分成 $K$ 段，映射到 $T_1,\ldots,T_K$ |

$\tau$ 在与树搜索 **同一 100-prompt 校准集** 上一维扫描；候选 $\tau\in\{0.001,0.005,0.01,0.02,0.05\}$。

跟读口径：

`
离线：贪心树 → 接受前沿 → self-rollout 去偏 → 吞吐 Pareto → TopologyBank
在线：每步算 s（path value）→ π 选树索引 → O(1) 换 mask/indices → 照常 draft–verify
`

---

## 四、评测设定与无损声明（§5）

| 项 | 文内设定 |
|---|---|
| 基座 | Vicuna-7B v1.3 |
| 草稿/校验栈 | `ankner/hydra-vicuna-7b-v1.3`（Hydra verifier） |
| 硬件 | 单卡 **A100**，FP16 |
| 共享超参 | $T=0.7$；$\epsilon=0.09$；$\alpha=0.3$；max input 1400；max gen 256 |
| 篮子 | 每任务 **100** prompts（seed 123）：HumanEval-val / GSM8K-val / ShareGPT（Vicuna unfiltered） |
| 计时 | 含 prompt **prefill**；一次 warm-up 后排除 JIT/KV 分配 |
| 无损 | 不微调原 LLM、不放松 Hydra 典型接受条件；续写困惑度相对基座 **$\le 0.02$ nats**（§5.1）；相对 Hydra 响应 perplexity **$0.022$ 内**（§1） |

**指标：**

- $\rho$：相对同设定 vanilla AR 的 wall-clock **输出 tok/s** 加速比
- $\tau$：每轮 draft–verify **平均接受长度**（硬件无关，隔离拓扑质量）

摘要另点名 LitBench；**主表 Table 1 仅三任务**（HumanEval / GSM8K / ShareGPT）。LitBench 出现在 Appendix A 特征日志规模（约 320k step rows），**无 Table 1 同行数字** → 本卡不编造 LitBench tok/s。

---

## 五、延迟 / 接受率字段（Table 1 + §6 分解）

### 5.1 Table 1 精读（照录）

| benchmark | method | tok/s | $\rho$ | $\tau$ |
|---|---|---|---|---|
| HumanEval | Vanilla Vicuna | 38.2 | 1.00× | 1.00 |
| | Medusa (default) | 91.2 | 2.38× | 2.87 |
| | Hydra (default) | 109.0 | 2.85× | 3.06 |
| | $\mathrm{EntMTP}^*$ | 123.4 | 3.21× | 3.28 |
| | $\mathrm{EntMTP}_\tau$ | **124.7** | **3.26×** | 3.20 |
| GSM8K | Vanilla | 33.7 | 1.00× | 1.00 |
| | Medusa (default) | 87.4 | 2.59× | 2.51 |
| | Hydra (default) | 102.4 | 2.87× | 2.86 |
| | $\mathrm{EntMTP}^*$ | 109.7 | 3.07× | 3.08 |
| | $\mathrm{EntMTP}_\tau$ | **112.0** | **3.13×** | 3.02 |
| ShareGPT | Vanilla | 35.4 | 1.00× | 1.00 |
| | Medusa (default) | 94.6 | 2.72× | 2.86 |
| | Hydra (default) | 109.0 | 2.89× | 3.06 |
| | $\mathrm{EntMTP}^*$ | 116.9 | 3.42× | 2.97 |
| | $\mathrm{EntMTP}_\tau$ | **117.5** | **3.47×** | 2.99 |

§1 叙述对齐：GSM8K **+9.4%** vs Hydra；HumanEval **+14.0%**（表算 $124.7/109.0-1\approx 14.4\%$，以表 tok/s 为准跟读）；ShareGPT **+7.8%**。摘要区间：**相对 Hydra 约 1.09–1.15×**；相对 Medusa **峰值 $\sim 1.36\times$**（HumanEval：$124.7/91.2\approx 1.37$）。

**batch size = 1**：文称 $\mathrm{EntMTP}_\tau$ 在三任务上同时压过 Hydra、Medusa 默认与 $\mathrm{EntMTP}^*$。

### 5.2 增益从哪来（§6.1，禁止升格 Hydra 方法）

| 贡献块 | 文内分解 |
|---|---|
| **静态 $\mathrm{EntMTP}^*$ vs Hydra default** | **+7.1–13.2%** tok/s；草稿节点 **$\ge 2\times$ 更少**（HumanEval / GSM8K / ShareGPT：**28 / 46 / 30** vs Hydra default **63**）；相对 Medusa default **+7.7–32.4%** |
| 结构 | 多半来自 **更小任务树 → 降每步验证成本**；另 **0–7%** 来自优化拓扑抬高 $\tau$（HumanEval $\tau: 3.06\to 3.28$；ShareGPT 略降 $\tau$ 仍净赚 tok/s） |
| **调度残差 $\mathrm{EntMTP}_\tau$ vs $^*$** | 再 **+0.5–2.1%**；GSM8K 最大（**+2.1%**）——高熵推理步混入保守树，回收验证周期且不损接受长度 |

---

## 六、与 EAGLE-2「动态树」的一句话差（不展开 EAGLE-3）

| | EAGLE-2（文 §2.2 简述） | **EntMTP** |
|---|---|---|
| 动态对象 | 用草稿置信度 **在线展开/剪枝节点**（同一草稿机制内） | 在 **预编译的多张固定拓扑** 间切换 |
| 训练 | 特征级草稿模型（EAGLE 系） | **训练免费**调度；树来自 Hydra 头栈上的离线搜索 |
| 本卡关系 | 只借 **path value** 公式作 $s$ | **不**复述 EAGLE-3 训练期改动（→ [[EAGLE3投机解码]]） |

---

## 七、跟读清单（可复述）

1. **问题** ← MTP 静态树与熵不均匀错位；接受信号还 **任务特异**。
2. **离线** ← 贪心接受前沿 → self-rollout 去偏 → **吞吐 Pareto** → 少而精的树银行。
3. **在线** ← TopologyBank **O(1)** 换树；$s=\max$ path value；$\tau$ 迟滞二值或阶梯。
4. **数字** ← $\mathrm{EntMTP}_\tau$：HumanEval **124.7** tok/s（**3.26×** AR）、GSM8K **112.0**（**3.13×**）、ShareGPT **117.5**（**3.47×**）；相对 Hydra default 约 **+8–14%**。
5. **无损** ← 困惑度贴基座 / Hydra；增益来自 **调度与更小任务树**，非改接受规则。

---

## 八、待核实 / 不写

- 官方代码仓：PDF **未给** → 不编造 URL。
- LitBench **主表 tok/s**：摘要点名，Table 1 无行 → 缺数不补。
- $\mathrm{EntMTP}\text{-}l$ 阶梯的完整 K 路消融表：正文以 $\mathrm{EntMTP}^*$ / $\mathrm{EntMTP}_\tau$ 为主结果。
- 多卡 / 大 batch / 非 Vicuna-7B：超出本 7 页主设定。
- Hydra / Medusa / Lookahead / EAGLE-3 **方法全文** → **B7 / [[EAGLE3投机解码]]**；本卡对照列到此为止。

---

## 九、一句话收束

相对 B7 的投机基线与 [[EAGLE3投机解码]] 的 EAGLE-3 训练增量，EntMTP 可研切片是：**在 Hydra 式 MTP 栈上，用任务吞吐 Pareto + TopologyBank，把「熵/路径价值 → 选哪张预编译草稿树」做成几乎零开销的训练免费调度，从而在不改分布的前提下挤出约 1.1× 相对默认 Hydra 树的 tok/s。**

---

*笔记状态：draft · 攻坚线架构思想 + 延迟/接受率 · PDF 已归档 2026-09-22 CST*

## 相关笔记

- [[DiffusionForcing族|Diffusion Forcing]]
- [[WorfBench工作流基准|WorfBench]]
- [[合成对齐数据Magpie|Magpie / ActiveUltraFeedback]]
- [[EntMTP熵引导投机解码|EntMTP]]
- [[DuoAttention与KVzip|DuoAttention / KVZip]]

