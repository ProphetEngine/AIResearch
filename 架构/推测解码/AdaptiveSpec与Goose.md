---
title: "投机解码新轴：AdaptiveSpec + Goose（≠ EAGLE-3）"
topic: AdaptiveSpec与Goose
date: 2026-09-22
lines: [AI Infra, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2609.02897 # 550K / 13p
 - https://arxiv.org/abs/2604.02047 # 647K / 29p
arxiv: ["2609.02897", "2604.02047"]
related: ["B7", "Prompt前缀缓存", "NVSHMEM与DeepEP通信", "ThunderKittens内核DSL", "KV缓存量化与压缩", "投机解码发展时间线"]
---

# 投机解码新轴：AdaptiveSpec + Goose（≠ EAGLE-3）

> **定位**：AdaptiveSpec + Goose **P1 Infra**——在 **[[EAGLE3投机解码]]** 已立 EAGLE-3 草稿头增量（training-time test + 多层特征融合）之后，本卡立**两条正交新轴**，禁止写成「又一篇 EAGLE」：
> - **AdaptiveSpec**（*Margins, Not Windows*）：**无训**、逐步自适应；在 **EAGLE-3 草稿器之上**同时动两条旋钮——① **margin 有损校验**（单位置目标概率比，非 FLy 窗口）；② **动态树形**（直接调 `nsteps/top-k/ndt`，非 TALON 固定预算重分配）。落在 **SGLang**。
> - **Goose**（*Anisotropic Speculation Trees*）：**无训**各向异性脊柱树；联合 **PLD 上下文 n-gram**（高接受 spine）与 **TR 转移表**（低接受 branches），证明异构接受率下最优树非各向同性；**不训草稿头**。
> **攻坚线**：**AI Infra / 投机解码拓扑与校验规则（主）** + **数学原理（辅）**（margin、接受异构、脊柱树期望产量下界）。
> **硬划界（开篇钉死，禁止 EAGLE 重写）**：
> - **≠ [[EAGLE3投机解码]]**：不重写 training-time test、特征融合、EAGLE→EAGLE-2→EAGLE-3 谱系与 SGLang 吞吐表正文。AdaptiveSpec **以 EAGLE-3 为草稿器/静态基线**，贡献是 **margin 校验 + 逐步树形**；Goose 文内明示与 EAGLE-3 **跨类（cross-category）**——无神经草稿头，本卡只录对照句，不抄 EAGLE-3 方法。
> - **≠ B7**：不写 vLLM/SGLang/TRT-LLM 选型通史，不写 Leviathan/Chen/Medusa/Lookahead 基线课。
> - **≠ [[Prompt前缀缓存]] / [[NVSHMEM与DeepEP通信]] / [[ThunderKittens内核DSL]]**：不写 Prompt Caching 计费、NVSHMEM/DeepEP、ThunderKittens 内核 DSL。
> - **≠ [[KV缓存量化与压缩]] / [[连续批处理与Orca]]**：不写 KV 量化、Orca 连续批处理。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。
> **二进制**：两篇均 **≪10MB**（见 §一）→ **官方 HTTPS 外链**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A** | Urbán, Kwon, Venieris & Mascolo, *Margins, Not Windows: Training-Free Per-Step Lossy Speculative Decoding* | arXiv:**2609.02897**v1 \[cs.CL\] **3 Jul 2026**；`https://arxiv.org/abs/2609.02897`（**550K**，562,524 B；**13** 页 A4） | **AdaptiveSpec**：margin 有损校验 + DCS 动态树；SGLang；vs EAGLE-3 / TALON\* / FLy\* |
| **主文 B** | Jin, Nguyen & Inoue (JAIST), *Goose: Anisotropic Speculation Trees for Training-Free Speculative Decoding* | arXiv:**2604.02047**v2 \[cs.CL\] **10 Aug 2026**；COLM 2026；`https://arxiv.org/abs/2604.02047`（**647K**，662,064 B；**29** 页 letter） | **Goose**：各向异性脊柱树（PLD spine + TR branches）；无训；vs isotropic / PLD / TR / SuffixDecoding / EAGLE-2 |

**代码（文内明示，本篇不展开实现）：** Goose → `GOOSE_Speculative_Decoding`（摘要页符号链接式标注；完整 URL 以文内仓库为准）。AdaptiveSpec 未在摘要页给出独立 GitHub。

| 文件 | 体积 | 备注 |
|---|---|---|
| `2609.02897-adaptivespec.pdf` | **550K** | **官方 HTTPS 外链**（≪10MB） |
| `2604.02047-goose.pdf` | **647K** | **官方 HTTPS 外链**（≪10MB） |

**一句话抓手：**
- **AdaptiveSpec**：别再死守「严格 token 匹配 + 静态树」——用目标分布的 **margin** 放行近义错配，用草稿置信×滚动接受率 **每步改树深宽与节点数**；两条轴正交、增益可叠加。
- **Goose**：别把 PLD 与 TR 当成同质候选——接受率差中位约 **6×**，最优树应是 **深脊柱（可靠）+ 宽枝（不可靠）** 的各向异性结构，无训即可 1.9–4.3× 无损加速。

---

## 二、议题边界：新轴 ≠ EAGLE-3 方法重写

### 2.1 四向对照（跟读）

| 轴 | 草稿从哪来 | 树/校验怎么动 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|---|
| **EAGLE-3** | 训好的特征/token 草稿头（多层融合 + training-time test） | 固定/半固定树 + 严格匹配（[[EAGLE3投机解码]]） | [[EAGLE3投机解码]] | **否**（禁重写） |
| **AdaptiveSpec** | **沿用 EAGLE-3 草稿器** | **逐步** margin 有损校验 + 直接调 `(nsteps, top-k, ndt)` | **本篇主文 A** | **是** |
| **Goose** | **无训**：PLD n-gram + TR 邻接表 | **各向异性脊柱树**；贪婪游走无损校验 | **本篇主文 B** | **是** |
| 引擎/缓存/内核 | — | 选型、前缀缓存、通信、TK | B7 / [[Prompt前缀缓存]] / [[NVSHMEM与DeepEP通信]] / [[ThunderKittens内核DSL]] / [[KV缓存量化与压缩]] / [[连续批处理与Orca]] | **否** |

跟读直觉：[[EAGLE3投机解码]] 问「**怎么把草稿头训得更吃数据、更长接受**」；AdaptiveSpec 问「**已有草稿器时，校验规则与树形能否每步自适应**」；Goose 问「**没有草稿头时，异构 token 源应排成什么树**」。三者可叠在同一「draft–verify」外壳下，但**贡献旋钮不同**——禁止把后两篇写成 EAGLE 续作。

### 2.2 文内自划界（跟读）

- **AdaptiveSpec**：显式以 EAGLE-3 为 SOTA 自回归草稿器与静态基线；批评 FLy 的 lookahead 窗口在 EAGLE-3 短接受长度（τ≈2.08–3.27）下失效；批评 TALON 只在固定 `ndt` 预算内重分配、未进生产级引擎。本卡只跟这两刀，不抄 EAGLE-3 训练。
- **Goose**：Related work 一句点到 EAGLE-3「直接 token 预测 + 多层融合」后立刻划到 **training-free** 谱系；§5.2 / §6 强调与 EAGLE-3 **cross-category**：不声称在 EAGLE 原生 chat-template 设定下全面压过 EAGLE-3。

`
 投机解码 draft–verify 外壳
 │
 ┌───────────┼───────────┐
 ▼ ▼ ▼
 EAGLE-3 AdaptiveSpec Goose
 (训草稿头) (margin+动态树) (各向异性脊柱)
 [[EAGLE3投机解码]] 本篇 A 本篇 B
`

---

## 三、主文 A：AdaptiveSpec（2609.02897）

### 3.1 问题立轴：两条旋钮被固定死了

摘要 / §1：树注意力草稿器（以 EAGLE-3 为代表）通常锁死——
1. **严格 token 匹配**校验；
2. **静态**草稿树形 `(nsteps, top-k, ndt)`。

先验分头放松：FLy 等用下游窗口做有损等价；TALON 等在固定 token 预算内按置信改深宽。AdaptiveSpec 主张：**无训、逐步、仅用解码已有内部信号**，同时放松两条轴，且总草稿节点数可真收缩（非只重分配）。

### 3.2 轴一：Margin 有损校验（§3.2）

在**第一个错配位置** $j$ 定义：

$$
\mathrm{margin}(j)=\frac{p_{\mathrm{target}}(\mathrm{draft}_j)}{p_{\mathrm{target}}(\mathrm{top1}_j)}\in[0,1]
$$

若 $\mathrm{margin}(j)\ge\kappa$ 则**提升（promote）**该草稿 token，否则拒绝。Margin 近 1 ≈ 目标几乎也选了草稿（语义近邻，较安全）；近 0 ≈ 目标自信草稿错。

**相对 FLy：** 单位置读目标分布，**不依赖**草稿链长 / 窗口 $W$；EAGLE-3 上静态 τ 仅 2.08–3.27（Table 5），装不下 FLy 设计的 $W{=}6$。

### 3.3 轴二：DCS 动态树形（§3.3）

每步 Draft Confidence Score：

$$
\mathrm{DCS}_t = p_{\mathrm{draft}}(\mathrm{top1}_t)\cdot\mathrm{RAR}_t
$$

RAR = 滚动接受率（EMA，$\alpha{=}0.3$）；再经除数 $d$ 饱和到 $[0,1]$。将 $(nsteps, top\text{-}k, ndt)$ 在 **(3,4,4) ↔ (7,1,8)** 间插值：置信 → 深窄链；不确定 → 宽浅树。候选三元组**总节点数不同** → 弱草稿步可真正减负。连续五步零接受则断路器回退起始配置。

**SGLang / CUDA Graph：** 启动时为每个可达三元组预捕获一张图，运行时切换——保留静态形状加速。

### 3.4 主结果与消融（Table 1–2，跟读）

设定：三目标（Llama-3.1-8B-Instruct / DeepSeek-R1-Distill-Llama-8B / Qwen3-8B）× 公开 EAGLE-3 草稿；GSM8K / MATH-500 / HumanEval；greedy、bs=1、单卡 A100、SGLang + SpecForge。加速相对 **vanilla AR**；Rec.% = 相对无损 EAGLE-3 的任务准确率保留。TALON\* / FLy\* 为作者在 SGLang+EAGLE-3 上的复现。

**摘要级数字（文内）：** Combined 相对 EAGLE-3 **峰值 +56%** 吞吐（Llama-3.1-8B HumanEval：2.82× vs 1.81×，Rec. 103%）；按目标平均约 **+18% / +38% / +44%**（Qwen / DeepSeek-R1 / Llama）；准确率保留约 **93%–全无损**。

**Table 2 消融（三基准平均）：**

| 配置 | 平均 Speedup | τ | Rec.% |
|---|---|---|---|
| Static × Strict（≈EAGLE-3） | 1.82× | 2.59 | 100 |
| Dynamic × Strict | 2.21×（+21.4%） | 3.61 | 100 |
| Static × Lossy | 2.20×（+20.9%） | 3.99 | 92 |
| Dynamic × Lossy（Combined） | **2.44×** | 4.10 | **98** |

两轴各自有效、组合最优；$d{=}0.5$ 在 Dynamic-only 搜索中多数格点胜出（Table 3）；$\kappa$ 存在吞吐–恢复权衡，按 (model, bench) 选（Table 4）。

**限制（§7，照录）：** margin 规则**不**在 Leviathan 形式意义上保持目标分布；仅评 bs=1；未报扩散式草稿器（DFlash / DDTree）。

---

## 四、主文 B：Goose（2604.02047）

### 4.1 问题立轴：接受率异构 → 树必须各向异性

训练无关两源：
- **PLD**（Prompt Lookup / 上下文 n-gram）：高接受，宜深链；
- **TR**（Token Recycling / 转移邻接）：低接受，宜宽枝兜底。

文内测量（五模型×五基准 greedy 日志）：$\hat p_s$（spine）中位 **0.21**，$\hat p_t$（transition）中位 **0.033**，比 $\hat p_s/\hat p_t$ 约 **2–18×**（中位 **∼6×**；Figure 1）。Sequoia 式「源无关接受」无法偏置可靠源。

### 4.2 理论要点（§3，跟读不抄证明）

- **Prop.1**：脊柱树期望产量 $E[\tau]$ 下界 = spine 项 + 断脊处 continuation synergy + bonus。
- **Prop.2**：固定分支预算下，最优宽度随深度近似线性递减（根部更宽）。部署用 **1/i 谐波**近似。
- **Prop.3**：$p_s>p_t$ 时，最优分配脊柱树严格优于同预算最优单源 isotropic。
- **Prop.4（非退化）**：任意预算 $B$，脊柱树期望产量 ≥ 单独 PLD 或单独 TR（各拿满 $B$）；无匹配时退化为纯 TR；高置信可 bypass 成纯链。

### 4.3 方法：Build → Verify → Greedy walk（§4）

每周期从上一接受锚点出发：
1. **Build spine tree**：预算 $B$ 按 spine ratio $r$ 铺 PLD 链；剩余按 $\rho$（默认 0.5）分给根枝与脊上枝；邻接表用 **bigram**（相对 TR 原 unigram）；枝递归延伸至深度 $D{=}6$。
2. **Verify**：一次前向 + tree attention；logits 回填邻接表，接受前缀更新 PLD 索引。
3. **Greedy walk**：纯 token 恒等匹配；同节点先查 PLD 子再查 TR 子；一旦离脊不返回——由此发现 **spine continuation**（脊断点处 TR 续走）。

**置信自适应（§4.3）：** 多长度 n-gram `{3,4,5}` 共识 + 长匹配（≥8）→ **bypass**（跳过建树、线性验链）；$r$ 由 PLD 接受率 EMA 在约 0.15–0.50 间调。

### 4.4 主结果（Figure 4 / Table 1–2，跟读）

设定：Vicuna-7B/13B/33B、Llama-3-8B-Instruct、Qwen3-8B；HumanEval / MBPP / ClassEval / GSM8K / MT-Bench；greedy、bs=1；$B{=}60$，$D{=}6$，top-K=10，$\rho{=}0.5$（全设定固定）。7B–13B 单卡 A40；Vicuna-33B 为 2×A100-40GB。

- **无损加速：** 摘要 / Figure 4：**1.9–4.3×** vs AR（Llama-3-8B GSM8K 近复述异常至 7.5× / τ=9.25，文内单列；其余 24 格落在 1.9–4.3×）。
- **vs isotropic 同预算：** Table 1 八设定 **+12–33%** τ（宏均 **+25.4%**；例 L3-8B ClassEval 4.89 vs Iso(3) 3.67，**+33%**）。
- **消融（Table 2，Qwen3-8B）：** 去脊枝 −2.9%；去 bigram −3.7%；去共识 bypass −5.1%；去 PLD 脊 −3.4%；关 spine continuation 另计约 −4.4%。
- **与 EAGLE 族：** vs EAGLE-2 墙钟互有胜负（≤8B 常因零草稿成本占优）；vs EAGLE-3：**不声称原生 chat-template 设定全面胜出**（§5.2 / §6 cross-category）。本卡不展开附录 D.4 逐格表。

---

## 五、两篇并读：同壳异轴

| 维度 | AdaptiveSpec | Goose |
|---|---|---|
| 草稿源 | 现成 **EAGLE-3** 草稿模型 | **无训** PLD + TR |
| 新贡献 | 校验 margin + 逐步树超参 | 跨源各向异性拓扑 + 非退化保证 |
| 损失性 | Combined 轴可有损（Rec. 经验报告） | 主实验 **无损**（greedy 恒等输出） |
| 引擎 | **SGLang** 生产路径（CUDA Graph 多形） | 自研循环（文内算法；未宣称 SGLang 集成） |
| 对 EAGLE-3 | **基线 + 草稿器宿主** | **跨类对照**，非方法续作 |

合读口径：若已部署 EAGLE-3 草稿头 → AdaptiveSpec 是「**校检与树形的运行时补丁**」；若拒绝训头 / 无头可用 → Goose 是「**用异构免费源排成脊柱树**」。二者都反对「单一静态树 + 源盲接受模型」，但**不得**并写成 EAGLE-3 第三代。

---

## 六、与仓库其他卡的接口（只索引）

| 卡 | 本篇取用 / 禁止 |
|---|---|
| **[[EAGLE3投机解码]]** | EAGLE-3 作 AdaptiveSpec 宿主与静态对照一句；**禁止**重写训练与特征融合 |
| **B7** | draft–verify / 树注意力外壳一句；**禁止**引擎选型通史 |
| **[[Prompt前缀缓存]] / [[NVSHMEM与DeepEP通信]] / [[ThunderKittens内核DSL]]** | 无交叉展开 |
| **[[KV缓存量化与压缩]] / [[连续批处理与Orca]]** | 无交叉展开 |

---

## 七、待办 / 缺口

- AdaptiveSpec：公开代码仓未在摘要钉死；多 batch、扩散草稿器（DDTree）文内留白。
- Goose：与 EAGLE-3 的协议敏感对照仅录结论句；完整附录表按需回 §D。
- 二者尚未在同一引擎、同一模型卡上做**头对头**（文内亦无）；合读勿捏造统一倍率。

---

## 八、回报摘要（供父代理）

- **笔记：** `/workspace/AIResearch-drafts/架构/推测解码/AdaptiveSpec与Goose.md
- **PDF：**
 - `https://arxiv.org/abs/2609.02897` — **550K** — **外链引用**
 - `https://arxiv.org/abs/2604.02047` — **647K** — **外链引用**
- **** `{adaptivespec,goose}.txt`
- **核心主张（不编造）：** AdaptiveSpec 无训双轴，相对 EAGLE-3 平均约 +18–44% 吞吐（峰 +56%），准确率保留约 93%–无损；Goose 无训各向异性脊柱树，1.9–4.3× 无损加速，同预算相对 isotropic +12–33% τ。
