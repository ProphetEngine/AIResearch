---
title: "Inference-time tree search：AB-MCTS（Adaptive Branching MCTS）"
topic: 推理时树搜索ABMCTS
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2503.04412
arxiv: ["2503.04412"]
related: ["推理时扩展TestTimeScaling", "自适应测试时算力", "过程奖励模型PRM谱系", "形式化验证与LLM", "DeepSeekR1推理训练深读", "MixtureOfAgents与TUMIX", "多智能体辩论", "潜空间推理Coconut"]
blog: "https://sakana.ai/ab-mcts/"
github: "https://github.com/SakanaAI/treequest"
github_arc2: "https://github.com/SakanaAI/ab-mcts-arc2"
archived: 2026-09-22
---

# Inference-time tree search：AB-MCTS（Adaptive Branching MCTS）

> **主要来源**：[Wider or Deeper? Scaling LLM Inference-Time Compute with Adaptive Branching Tree Search](https://arxiv.org/abs/2503.04412)（Inoue 等，Sakana AI，v5，NeurIPS 2025 spotlight）；[SakanaAI/treequest](https://github.com/SakanaAI/treequest)；[Inference-Time Scaling and Collective Intelligence for Frontier AI](https://sakana.ai/ab-mcts/)（2025-07-01 博客）（截至 2025-11-07）。
> **研究线**：架构思想（多答案树搜索中「变宽还是变深」的贝叶斯决策，主）· 评测字段（同预算下对重复采样、固定宽度 MCTS，辅）
> **范围与相邻笔记**：
> - ≠ [[推理时扩展TestTimeScaling]]：本篇不写 o1 / R1 的训练期 RL 与长思维链，只取「推理期多花算力生成多个答案」这一族。
> - ≠ [[过程奖励模型PRM谱系]]：本篇不写过程奖励模型的训练；AB-MCTS 的评分来自可执行的外部反馈。
> - ≠ [[形式化验证与LLM]]：本篇不写证明器内的形式证明搜索。
>
> **意义**：重复采样只会变宽、顺序修订只会变深、标准 MCTS 要事先固定分支数；AB-MCTS 让每个节点按后验在「再采一个新答案」和「继续改进已有答案」之间选择，在不知道任务偏宽还是偏深时也能稳定靠前，并自然扩展到在多个模型之间选生成器。

**一句话**：在有外部反馈分数的任务上，不预先规定每层生几个孩子；每个节点挂一个 GEN 子节点代表「从这里再生成一个新答案」，用 Thompson sampling 在 GEN 与已有孩子之间抽样，搜索树由此自适应地变宽或变深。

---

## 一、问题背景

论文把推理时扩展分三族（§1–2）：训练后的长思维链（o1、R1 等）、奖励引导的逐步搜索（主要用于数学）、多答案生成（同一提示非零温度多次采样再选优）。AB-MCTS 落在第三族。

在编程等能拿到外部反馈的场景，第三族有两种极端：重复采样（Best-of-$n$）只有探索没有利用，顺序修订只沿一条链改。标准 MCTS（如 LATS 的编程配置）兼顾两者，但分支因子是固定超参；而 LLM 对同一提示可以无限采样，分支因子理论上无界，固定它就浪费了这种多样性。

## 二、脉络

| 节点 | 内容 | 来源 |
|---|---|---|
| 重复采样 / Best-of-$n$ | 只变宽：同一提示采 $n$ 次，按启发式选优 | AB-MCTS §2 |
| 顺序修订 | 只变深：带反馈反复改同一答案 | AB-MCTS §2 |
| LATS 等标准 MCTS | 固定分支因子的树搜索 | AB-MCTS §2、§5.2 |
| Progressive Widening | 按访问次数启发式放宽分支，不看已观察奖励 | AB-MCTS 附录 C.4 |
| o1、DeepSeek-R1（2024–2025） | 训练期 RL 出长思维链，另一条推理时扩展路线 | [[推理时扩展TestTimeScaling]] |
| AB-MCTS（2025） | GEN 节点 + Thompson sampling 的自适应分支 | AB-MCTS |
| Multi-LLM AB-MCTS（2025-07） | 再加一维：选哪个模型生成 | AB-MCTS 附录 D；博客 |

## 三、核心机制

**问题设定（§3.1）。** $f_{\text{LLM}}(t_{\text{in}})\to t_{\text{out}}$ 非零温度生成；根节点输入任务提示，非根节点输入历史答案与外部反馈做改进；评分 $r=R(t_{\text{out}})$ 常归一到 $[0,1]$（如公开测例通过率、验证集指标）。节点一生成就能评分，不需要单独 rollout。目标是在有限 LLM 调用次数内找到高分答案。

**骨架（Algorithm 1）。** 每轮加一个新节点：从根往下选择，选中 GEN 就停下，在该父节点上调用 LLM 生成新孩子，再把分数沿树回传。每个节点（含新叶）都挂一个 GEN 子，所以非叶也能再扩，分支因子不再是静态超参。GEN 会动态生成新臂，不是标准多臂赌博机的静态臂集，所以不用 UCT，改用贝叶斯后验 + Thompson sampling：对 GEN 与每个已有孩子各算后验预测、各抽一个分数、取最大。这也便于并行扩展。

**两种变体（§3.3–3.4）。**

| 变体 | 建模 | 特点 |
|---|---|---|
| AB-MCTS-M（混合模型） | 父节点下每个孩子子树为一组的混合效应模型，GEN 是尚无观测的新组，用 MCMC 拟合 | 组间共享统计强度；结果最好但开销大；树形偏深 |
| AB-MCTS-A（节点聚合） | 增加与 GEN 同层的 CONT 节点代表「继续改已有孩子」，共轭先验解析更新 | 轻量；到深度 $d$ 需连续 $d$ 次选 CONT，树形偏宽 |

论文建议（附录 C.5）：重结果质量用 M；选择步要快或任务已知偏广探索（如 ARC-AGI）用 A。先验在一组设定下基本不敏感（附录 A.6）。

**Multi-LLM（附录 D）。** 在宽、深之外再选生成器：对每个模型的历史分数建后验，用 Thompson sampling 选模型；ARC-AGI-2 实验采用「每个父节点挂多个 GEN、每个模型一个」的版本。

## 四、评测要点

设定（§4.1）：LiveCodeBench、CodeContest、ARC-AGI（100 道公开评测题）与三道 MLE-Bench 低复杂度 Kaggle 题；GPT-4o 与 DeepSeek-V3；生成预算即 API 调用上限 128。

| 方法（Table 1，六个设定的平均名次，越小越好） | 平均名次 |
|---|---|
| AB-MCTS-M | **2.3** |
| AB-MCTS-A（Gaussian / Beta） | 2.7 / 2.7 |
| 重复采样 | 3.5 |
| 标准 MCTS | 4.2 |
| 顺序修订 | 5.5 |

- AB-MCTS 三个变体占据平均名次前三，但在 ARC-AGI 上重复采样两个模型都排第一：任务偏广探索时纯变宽仍然强，AB-MCTS 的价值是「不是处处第一，但处处靠前」。
- MLE-Bench 三题的最佳基线各不相同（有的偏深、有的偏宽），AB-MCTS-M 平均名次 1.3 最好（Table 2）。
- 标准 MCTS 对宽度敏感（Table 6）；调好的 Progressive Widening 可接近 AB-MCTS，但对超参敏感且方差大（Table 4）。
- ARC-AGI-2（附录 D、博客；120 题、预算 250，报覆盖率 Pass@k 而非官方 Pass@2）：o4-mini 重复采样 23%，单模型 AB-MCTS 27.5%，o4-mini + Gemini-2.5-Pro + DeepSeek-R1-0528 的 Multi-LLM 版本超过 30%；用简单规则选两个答案的 Pass@2 只有 19.2%。

## 五、意义

AB-MCTS 把「推理时多花算力」从单一的采样数或修订轮数，推进到每个节点上的宽深分配决策，并给出不必调分支因子的实用算法（TreeQuest 已开源）。Multi-LLM 版本说明，不同前沿模型在同一棵树里接力改进，可以解出单个模型解不了的题——这为「模型间协作」提供了一个以外部评分为中心的框架。

## 六、局限与待核实

- 依赖可靠的评分器 $R$；没有公开测例或验证集的任务，搜索信号本身就是瓶颈（§5）。
- 预算按 API 调用次数计，未计真实延迟与评分器开销（附录 C.10）。
- Multi-LLM 上 Pass@k 远高于简单 Pass@2，终答选择仍缺好办法（附录 D.3）。
- 论文提议按累积奖励估计难度、在 M 与 A 之间切换，尚未实现。
- MLE-Bench 只跑了 GPT-4o + AB-MCTS-M、各一次（成本原因）。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[推理时扩展TestTimeScaling]] | 推理时扩展的总背景在那篇；AB-MCTS 属于其中「多答案生成 + 选择」一族，与训练出长思维链的路线互补 | o1 / R1 产品线与训练配方 |
| [[DeepSeekR1推理训练深读]] | R1 论文自述按难度动态分配思考 token，并与多数投票、MCTS 这类外层搜索对照；AB-MCTS 正是外层搜索一侧 | R1 训练管线 |
| [[自适应测试时算力]] | 两者都在固定预算下自适应分配算力：那篇按查询难度分配 token 与样本，AB-MCTS 在单题内分配宽与深 | 难度估计与路由方法 |
| [[潜空间推理Coconut]] | 对照：AB-MCTS 在外层显式展开答案树、用 Thompson sampling 决定加宽还是加深；那篇训练模型在单个连续思维向量里同时保留多个候选，作者称其类似广度优先搜索，没有外层搜索控制器 | 连续思维训练课程与探针 |
| [[过程奖励模型PRM谱系]] | 都用信号引导搜索：PRM 是训练出的逐步判别器，AB-MCTS 用可执行的外部评分；论文把答案选择的缺口列为可用奖励模型补足的方向 | PRM 训练与 ORM / PRM 谱系 |
| [[形式化验证与LLM]] | 「树搜索 + 外部校验」作推理时扩展的另一形态：那里的校验器是证明器内核，这里是测例与验证集 | Lean 证明搜索 |
| [[MixtureOfAgents与TUMIX]]、[[多智能体辩论]] | 都是多模型协作：MoA / 辩论按层聚合或互相批评，Multi-LLM AB-MCTS 用后验在树里选生成器；两者关系 Sakana 博客列为开放问题 | MoA / 辩论的机制与评测 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [AB-MCTS](https://arxiv.org/abs/2503.04412) Figure 1、Algorithm 1 | 三种基线与 AB-MCTS 的宽深对比；GEN 节点 |
| 2 | 同上 §3.3–3.4、附录 C.5 | M 与 A 的回传差异与选用建议 |
| 3 | 同上 Table 1、Figure 4–5 | 平均名次、预算曲线与树形 |
| 4 | [Sakana AI 博客](https://sakana.ai/ab-mcts/)、[ab-mcts-arc2](https://github.com/SakanaAI/ab-mcts-arc2) | Multi-LLM 与 ARC-AGI-2 复现 |
| 5 | [TreeQuest](https://github.com/SakanaAI/treequest) | 开源实现（Apache-2.0）；批量 ask / tell 接口 |
