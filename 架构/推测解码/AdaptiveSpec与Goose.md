---
title: "投机解码新轴：AdaptiveSpec + Goose（≠ EAGLE-3）"
topic: AdaptiveSpec与Goose
date: 2026-09-22
lines: [AI Infra, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2609.02897
 - https://arxiv.org/abs/2604.02047
arxiv: ["2609.02897", "2604.02047"]
related: ["EAGLE3投机解码", "EntMTP熵引导投机解码", "推理引擎生态", "投机解码发展时间线"]
---

# 投机解码新轴：AdaptiveSpec + Goose（≠ EAGLE-3）

> **主要来源**：[Margins, Not Windows: Training-Free Per-Step Lossy Speculative Decoding](https://arxiv.org/abs/2609.02897)（AdaptiveSpec，v2）；[Goose: Anisotropic Speculation Trees for Training-Free Speculative Decoding](https://arxiv.org/abs/2604.02047)（v2，COLM 2026）（截至 2026-09-28）。
> **研究线**：AI Infra（投机解码的树形与校验规则，主）· 数学原理（margin 判据、接受率异构下的最优树，辅）
> **范围与相邻笔记**：
> - ≠ [[EAGLE3投机解码]]：本篇不写 training-time test 与多层特征融合；AdaptiveSpec 把 EAGLE-3 当草稿器和静态基线，Goose 与 EAGLE-3 不同类。
> - ≠ [[推理引擎生态]]：本篇不写「草稿—并行校验、分布不变」的基本框架与引擎选型，投机解码共用背景见该篇第三节。
> - ≠ [[EntMTP熵引导投机解码]]：本篇不写在预编译拓扑间切换的调度器。
>
> **意义**：两篇都不训练新草稿头，只改「树怎么长、错配怎么判」：AdaptiveSpec 说明已有草稿器在运行时还能每步调树形、放宽校验；Goose 说明没有草稿头时，把接受率悬殊的两种免费候选源排成不对称的树，本身就能拿到 1.9–4.3× 的无损加速。

**一句话**：投机解码的收益不只取决于草稿模型训得多好，也取决于草稿树的形状与校验规则；AdaptiveSpec 用目标分布的 margin 放行近义错配、按草稿置信每步改树，Goose 用「可靠源作深脊柱、不可靠源作宽枝」的各向异性树替代各向同性树。

---

## 一、问题背景

以 EAGLE-3 为代表的树注意力草稿器，推理时通常固定两件事：校验用**严格 token 匹配**，草稿树形 $(n_{\text{steps}},\text{top-}k,\mathrm{ndt})$ **静态不变**（AdaptiveSpec §1）。前人各放松过一条轴：FLy 用下游窗口判断有损等价，TALON 在固定节点预算内按置信重分配深宽；两者都没进生产级引擎，也没有同时动两条轴（AdaptiveSpec §2）。

另一条线是**无训练**的草稿源：PLD（在上下文里查 n-gram）与 Token Recycling（TR，用转移邻接表）。它们零草稿成本，但已有方法把不同来源的候选当作同质节点排成各向同性的树（Goose）。

## 二、脉络

| 节点 | 内容 | 来源 |
|---|---|---|
| 投机采样 | 廉价草稿 + 目标并行校验，输出分布不变 | [[推理引擎生态]] 第三节 |
| Medusa / Lookahead / PLD | 草稿内置进目标或免模型取候选 | [[推理引擎生态]] 第三节；Goose 相关工作 |
| EAGLE → EAGLE-2 → EAGLE-3 | 特征级草稿、动态树、training-time test | [[EAGLE3投机解码]] |
| FLy、TALON | 窗口式有损校验；固定预算下的置信树形 | AdaptiveSpec 相关工作 |
| AdaptiveSpec（2026） | 在 EAGLE-3 上同时放松校验与树形，落在 SGLang | AdaptiveSpec |
| Goose（2026） | PLD 脊柱 + TR 枝的各向异性树，附最优性命题 | Goose |

## 三、AdaptiveSpec：margin 校验 + 逐步树形

**轴一：margin 有损校验（§3.2）。** 在第一个错配位置 $j$ 读目标分布：

$$
\mathrm{margin}(j)=\frac{p_{\text{target}}(\text{draft}_j)}{p_{\text{target}}(\text{top1}_j)}\in[0,1]
$$

$\mathrm{margin}(j)\ge\kappa$ 时放行该草稿 token，否则拒绝。margin 接近 1 表示目标也几乎会选它；接近 0 表示目标很确定草稿错了。相对 FLy，这只看单个位置，不依赖链长：EAGLE-3 静态树的平均接受长度 τ 只有 2.08–3.27，装不下 FLy 需要的长度为 6 的窗口（附录 G）。v2 所有有损配置统一用 $\kappa=0.2$。

**轴二：DCS 动态树形（§3.3）。** 每步算草稿置信分 $\mathrm{DCS}_t=p_{\text{draft}}(\text{top1}_t)\cdot\mathrm{RAR}_t$，RAR 为滚动接受率（EMA，$\alpha=0.3$），再按除数 $d$ 饱和到 $[0,1]$。树形在 $(3,4,4)\leftrightarrow(7,1,8)$ 之间插值：置信高给深而窄的链，置信低给浅而宽的树；各三元组的总节点数不同，所以弱草稿步真正少算，而不只是重分配。连续五步零接受时回退到起始配置。为保留 SGLang 的 CUDA Graph 加速，启动时为每个可达三元组各捕获一张图，运行时切换。

**结果（v2，§4）。** 三个目标模型（Llama-3.1-8B-Instruct、DeepSeek-R1-Distill-Llama-8B、Qwen3-8B）配公开 EAGLE-3 草稿，测 GSM8K / MATH-500 / HumanEval，greedy、单卡 A100、SGLang。

| 配置（三基准、三模型平均，Table 2） | Speedup | τ | 准确率保留 % |
|---|---|---|---|
| 静态树 × 严格（≈ EAGLE-3） | 1.82× | 2.59 | 100 |
| 动态树 × 严格 | 2.21× | 3.61 | 100 |
| 静态树 × 有损 | 2.10× | 3.78 | 93 |
| 动态树 × 有损（AdaptiveSpec） | **2.42×** | 4.08 | 95 |

论文称相对 EAGLE-3 按目标模型平均提速 16%–45%、峰值 +56%（Llama-3.1-8B HumanEval，2.82× 对 1.81×），准确率平均保留 94%–96%。两条轴各自有效、组合最好，组合配置在每个目标模型上都是最快的。v2 新增 batch size 1–16 的扫描（DeepSeek-R1-8B）：AdaptiveSpec 在每格都领先 EAGLE-3，但两者的加速比都随 batch 增大而下降（如 GSM8K 上从 3.20× 降到 1.67×），论文归因于负载从带宽受限转向算力受限。

## 四、Goose：各向异性脊柱树

**观察（§3）。** 五个模型、五个基准的 greedy 日志里，PLD 候选的接受率中位数约 0.21，TR 约 0.033，两者之比在 2–18 倍之间（中位约 6 倍，Figure 1）。源无关的建树方法（如 Sequoia 式）无法偏向可靠来源。

**理论直觉（§3，Prop. 1–4）。** 用可靠源铺一条深「脊柱」，不可靠源在脊柱各处挂宽枝：期望接受长度有一个由脊柱项、断脊处的续接项与奖励 token 组成的下界；固定预算下最优枝宽随深度递减（部署时用 $1/i$ 近似）；只要可靠源接受率更高，同预算下脊柱树严格优于任一单源的各向同性树，且不劣于单用 PLD 或单用 TR。

**做法（§4）。** 每轮从上次接受的位置出发：按脊柱比例 $r$ 铺 PLD 链，余下预算给根部与脊上的 TR 枝（邻接表改用 bigram）；一次前向加树注意力校验；按纯 token 恒等贪心游走，离开脊柱后不再回到脊柱，因此能在断脊处沿 TR 续接。多长度 n-gram 一致且匹配够长时跳过建树、直接验链；$r$ 随 PLD 接受率在约 0.15–0.50 间自适应。

**结果（Figure 4、Table 1–2）。** Vicuna-7B/13B/33B、Llama-3-8B-Instruct、Qwen3-8B，五个代码与对话基准，greedy、bs=1：

- 相对自回归 1.9–4.3× 无损加速（Llama-3-8B 的 GSM8K 因提示近乎复述，是 7.5× 的离群点，论文单列）。
- 同预算下相对各向同性树，平均接受长度提高 12%–33%（宏平均 +25.4%，Table 1）。
- 消融（Qwen3-8B，Table 2）：去掉一致性旁路、bigram、PLD 脊柱或脊上枝，各损失约 3%–5%。
- 相对 EAGLE-2 墙钟互有胜负（8B 以下常因零草稿成本占优）；论文不声称在 EAGLE 原生对话模板设定下全面胜过 EAGLE-3。

## 五、两篇对照

| 维度 | AdaptiveSpec | Goose |
|---|---|---|
| 草稿源 | 现成 EAGLE-3 草稿模型 | 无训练：PLD + TR |
| 改动的旋钮 | 校验判据 + 每步树形 | 跨来源的树拓扑 |
| 是否无损 | 有损（准确率保留按经验报告） | 无损（greedy 恒等输出） |
| 落地 | SGLang 内实现，多张 CUDA Graph | 论文自有解码循环 |

两者都反对「单一静态树 + 不区分来源的接受模型」。已部署 EAGLE-3 时，AdaptiveSpec 是运行时补丁；没有草稿头可用时，Goose 给出免费候选源的排法。

## 六、意义

投机解码的研究重心正从「训更好的草稿头」扩展到「推理时如何用现有信号塑形草稿树与校验」。AdaptiveSpec 把这类运行时策略做进生产引擎并给出 batch 扩展下的表现；Goose 用可证明的命题说明接受率异构时树必须不对称。两者都可以叠在同一 draft–verify 外壳上，与草稿头训练正交。

## 七、局限与待核实

- AdaptiveSpec 的 margin 规则不在形式意义上保持目标分布，准确率保留是经验报告；只在 EAGLE-3 草稿器上评测，未报扩散式草稿器（论文第 7 节）。
- AdaptiveSpec 引用的是 v2；v1 写的是按目标平均提速 18%–44%、准确率保留「93% 到无损」，Table 2 的静态树 × 有损为 2.20× / 3.99 / 92、组合为 2.44× / 4.10 / 98，且只测 bs=1。
- AdaptiveSpec 的公开代码仓在论文页未见；Goose 的实现是自有循环，未宣称集成进 SGLang 或 vLLM。
- 两篇没有在同一引擎、同一模型上做过头对头比较，本篇不给统一倍率。
- Goose 与 EAGLE-3 的协议敏感对照只记结论句，逐格数字见其附录 D。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[EAGLE3投机解码]] | AdaptiveSpec 的草稿器与静态基线就是 EAGLE-3，那篇讲这个草稿头怎么训，本篇讲它上面的树形与校验怎么在运行时调 | training-time test、多层特征融合 |
| [[EntMTP熵引导投机解码]] | 同为无训练的运行时树形调度：那篇在离线挑好的几张预编译树之间切换，AdaptiveSpec 在一个三元组区间里连续插值 | TopologyBank、path value 选树 |
| [[推理引擎生态]] | 投机解码的共用背景（decode 受带宽束缚、草稿—校验框架）在那篇第三节，本篇直接建立在其上 | 引擎选型、Leviathan / Medusa / Lookahead 正文 |
| [[投机解码发展时间线]] | 本篇两种方法列在该时间线的投机解码族中 | 族谱全表 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [AdaptiveSpec](https://arxiv.org/abs/2609.02897) §3、Table 2–3 | margin 与 DCS 的定义；两轴消融与 batch 扫描 |
| 2 | [Goose](https://arxiv.org/abs/2604.02047) §3–4、Figure 1 | 接受率异构的测量与四个命题；建树与贪心游走 |
| 3 | [[EAGLE3投机解码]] | AdaptiveSpec 所用草稿器的来历 |
| 4 | [[推理引擎生态]] 第三节 | 投机解码的基本框架与 decode 带宽瓶颈 |
