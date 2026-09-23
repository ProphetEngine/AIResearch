---
title: "Latent reasoning：Coconut（Chain of Continuous Thought）"
topic: 潜空间推理Coconut
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2412.06769
arxiv: ["2412.06769"]
related: ["推理时扩展TestTimeScaling", "推理时树搜索ABMCTS", "机制可解释性入门"]
github: "https://github.com/facebookresearch/coconut"
openreview_pdf: "https://openreview.net/pdf?id=KrWSrrYGpT"
补链索引: ["AGCLR 2606.07720（概念瓶颈；不升主项）"]
archived: 2026-09-22
---

# Latent reasoning：Coconut（Chain of Continuous Thought）

> **定位**：连续潜空间推理 **P0**——相对 **[[推理时扩展TestTimeScaling]]**（语言空间 CoT / 采样 / 树搜索式 TTS 通史）补一块独立的 **连续潜空间推理** 切片：FAIR/Meta 的 **Coconut**（*Training Large Language Models to Reason in a Continuous Latent Space*，arXiv **2412.06769v4**）把 **last hidden state** 直接反馈为下一输入嵌入，在连续空间做隐式多路径搜索。
> **攻坚线**：**架构思想（主）**——「continuous thought」回路 + 多阶段课程如何把语言 CoT 内化为潜推理；**评测字段（辅）**——相对 CoT / No-CoT / iCoT / pause 的准确率—生成 token 权衡（GSM8k / ProntoQA / ProsQA）。
> **硬划界**：
> - **≠ [[推理时扩展TestTimeScaling]]**：不写 o1/R1 产品通史、语言 CoT 提示/RL 训练配方；只取「语言空间推理有瓶颈 → 换到连续空间」这一接口。
> - **≠ [[推理时树搜索ABMCTS]] AB-MCTS**：不写外层 **显式 token/答案树** + Thompson sampling；Coconut 的「BFS」是 **潜表示内并行编码多候选**，无外层搜索控制器。
> - **≠ 机制可解释性**：不写 SAE / 电路 / 归因图通史；文中对 latent 的 probe（把 continuous thought 解码成候选概念概率）只作 **行为解释证据**，不升 MI 方法论。
> - **禁止编造**：表数字、阶段数、$c$、epoch、ProsQA 统计一律锚定官方 PDF（2026-09-22 CST）。AGCLR 仅作议程补链点名，本卡不展开。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Hao, Sukhbaatar, Su, Li, Hu, Weston, Tian（FAIR at Meta / UCSD）, *Training Large Language Models to Reason in a Continuous Latent Space* | arXiv:**2412.06769v4** \[cs.CL\] **23 Aug 2026**；页眉 *Last updated: August 25, 2026*；`https://arxiv.org/abs/2412.06769`（**18** 页 letter；3,211,318 bytes） | 一手：范式、课程、ProsQA 潜搜索分析、主表 |
| **镜像** | OpenReview PDF | https://openreview.net/pdf?id=KrWSrrYGpT | 议程备链；本笔记数字以 arXiv 官方 PDF 为准 |
| **代码** | facebookresearch/**coconut** | https://github.com/facebookresearch/coconut（文首页） | 复现入口；本卡不 walkthrough |

**一句话抓手：** 把「推理状态」从 **词 token 序列** 换成 **可微的连续向量回路**——$h_t$ 不经 LM head 解码，直接当下一输入嵌入；再靠 **多阶段课程** 逐步用 $c$ 个 continuous thoughts 顶替语言推理步，让模型在潜空间里 **并行保留多条下一跳**，呈现类似 BFS 的规划行为。

---

## 二、议题边界：连续潜推理，不是语言 CoT / 外层树 / MI 通史

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[推理时扩展TestTimeScaling]] / 语言 CoT** | 「逐步生成中间过程能抬解题率」；CoT 把输出回路回输入、加深有效深度（文引 Feng et al. 作动机） | o1/R1 产品线、RL 长 CoT、采样/共识/打分重排通史 |
| **[[推理时树搜索ABMCTS]] AB-MCTS** | 「规划任务需要宽探索、勿过早钉死一条路径」（抽象对照） | GEN 节点、Thompson sampling、TreeQuest、答案级外层 MCTS |
| **机制可解释性 MI** | 「可对内部表征做 probe / 干预式读出」（文 §4.3 用 softmax 读候选概念） | SAE、电路、归因图、monosemanticity 史线 |

### 2.2 文内立轴：语言空间为何可能不是最优推理介质

文 §1 三点（跟读压缩，非神经科学展开）：

1. **算力均匀分配**：每 token 预算近似相同，但 CoT 里大量 token 只为流畅，关键规划步却极难。
2. **语言约束**：提示「写短 CoT」或 Quiet-STaR 式「关键 token 前多想」仍落在语言空间。
3. **理想形态**：推理时不受语言约束，**必要时再译回语言**。

Coconut 的回答：**删掉 hidden↔token 的映射环，让连续 thought 端到端可微。**

### 2.3 与「显式树搜索」的一句话差

| | 语言/外层树（ToT、AB-MCTS 等） | **Coconut 潜「BFS」** |
|---|---|---|
| 候选存在何处 | 离散 token / 答案节点，外层算法展开 | **同一 continuous thought 向量内叠加多候选** |
| 是否显式搜索控制器 | 有（beam / MCTS / 采样策略） | **无**；从训练目标涌现 |
| 训练信号 | 常需轨迹/奖励或外部分数 | 语言 CoT 课程 + 对剩余文本的 CE |

---

## 三、架构思想：语言模式 ↔ 潜模式回路

### 3.1 记号与核心改动（文 §3）

标准 LM（文记法）：

$$
H_t = \mathrm{Transformer}(E_t),\quad
M(x_{t+1}\mid x_{\le t})=\mathrm{softmax}(W h_t)
$$

其中 $E_t$ 为 token 嵌入序列，$h_t=H_t[t,:]$ 为位置 $t$ 的 last hidden state。

**Coconut：** 在潜模式区间用特殊标记 `<bot>` / `<eot>` 界定；若潜推理在 $i$ 与 $j$ 之间（$x_i=\texttt{<bot>}$, $x_j=\texttt{<eot>}$），则对 $i<t<j$：

- **下一输入不再是 $e(x_t)$，而是上一位置的 $h_{t-1}$**（已过最终 norm，幅值可控）；
- $M(x_{t+1}\mid\cdot)$ 在潜区间 **不定义**（不强制映回词表）；但 $\mathrm{softmax}(W h_t)$ 仍可算，供 §5/§4 探针。

跟读：**CoT = 词→词回路；Coconut = 向量→向量回路，必要时再出语言。**

### 3.2 多阶段课程（Figure 2；灵感自 iCoT / Deng et al. 2024）

问题设定：给定问题，经推理生成答案。训练数据带 **语言 CoT 步骤**。

| 阶段 | 做法 |
|---|---|
| 初始 | 普通语言 CoT SFT |
| 第 $k$ 阶段 | 把 CoT 的 **前 $k$ 个语言推理步** 换成 $k\times c$ 个 continuous thoughts（`<bot>`/`<eot>` 不计入 $c$） |
| 损失 | 对问题与 latent thoughts **mask**；只对 continuous thoughts **之后剩余文本** 做 NLL |
| 优化器 | 阶段切换时 **reset optimizer state**（跟随 Deng et al.） |

关键澄清（文原话级）：目标 **不是** 让 continuous thought **压缩**被删掉的那句语言，而是 **方便预测后续推理**——因此潜表示可以比人类语言更高效。

实现细节（跟读即可，非手册）：若当前阶段排了 $n$ 个 latent thoughts，做 $n+1$ 次前向（每次出一个新 thought，最后一次算剩余文本损失）；可用 KV cache 省重复算，但多次前向的串行性限制并行——文称训练效率仍是开放问题。

### 3.3 推理期何时进出潜模式

- 解题设定下：问题 token 后立刻插 `<bot>`。
- `<eot>` 两种策略：（a）在 latent thoughts 上训二分类器自主结束；（b）**固定长度 padding**。文称两者相当，实验默认 **(b)**。

---

## 四、连续空间为何能「隐式树搜索」（ProsQA）

### 4.1 ProsQA：需要规划的逻辑 QA

文新提 **ProsQA**（Proof with Search Question-Answering）：每题是概念间逻辑关系的 **DAG**，用自然语言陈述；要求找合法路径判定关系。相对 ProntoQA，DAG 带来更多干扰分支，**规划/搜索压力更大**（细节 Appendix A）。

图结构统计（Table 2，均值）：节点 **23.0**、边 **36.0**、最短路径长 **3.8**、最短路径条数 **1.6**。

数据规模（Table 3）：ProsQA train/val/test = **17,886 / 300 / 500**（ProntoQA 9,000/200/800；GSM8k 合成训集约 385,620 / 500 / 1319）。

底座：**预训练 GPT-2**；lr $1\times10^{-4}$，effective batch **128**；ProsQA 最大推理步 6 → 训练阶段数 $N=6$；每阶段 5 epoch，末阶段留到总 **50** epoch；取末阶段验证最佳 checkpoint。

### 4.2 用 `<eot>` 位置插值：同权重、不同潜深度

推理时强制 Coconut 使用 $k\in\{0,\ldots,6\}$ 个 continuous thoughts，再让模型用语言吐出剩余链——**同一套权重**，只改推理期潜步数。度量两套：

1. **最终答案对错**（主指标，亦用于 §5）；
2. **过程类别**：Correct Path / Longer Path / Hallucination / Wrong Target；对只出答案者另计 Correct/Incorrect Label（六类互斥，§4.1）。

Figure 3 定性结论（文述，无另造点估计）：相对语言 CoT 易幻觉不存在边或走向错误目标，**增加 continuous thoughts → 答案准确率与正确过程比例上升，Hallucination / Wrong Target 下降**。

案例（Figure 4）：CoT 卡死末端后幻觉边 *Every yumpus is a rempus*；Coconut $k=1$ 走到无关节点；**$k=2$ 正解**。

### 4.3 探针：latent = 并行多候选 + 非贪心「价值」

做法：在中间 continuous thought 之后 **强制改回语言**，读出下一概念的预测分布（概念概率 = 其内各 token 条件概率之积），视为 **隐式价值函数**。

同一案例（Figure 5）：

- 第一步：「lempus」价值最高（**0.33**），候选含 Alex 的直接孩子；
- 第二步：最高落在「grimpus」的孩子「rorpus」（**0.87**），**并未沿第一步最高的 lempus 贪心走下去**。

文称这类似 **BFS**：连续表示可同时编码多条候选路径，避免语言 CoT 的过早确定性承诺；且该模式不限个例，支撑「更大 $k$ 持续改进」。

Figure 6：第一步 top-1/2/3 累积价值曲线间距大（宽探索）；第二步间距收窄（更聚焦）。Figure 7：节点 **height**（到叶最短距离）越低，对正确/错误节点的价值估计越干净——解释「为何推迟确定性决策有利规划」。

---

## 五、评测字段：三数据集主表与效率权衡

### 5.1 训练配置摘要（§5.1）

| 数据 | $c$ | 阶段设计（压缩） |
|---|---|---|
| **GSM8k** | **2** | 初始 + 3 阶段；再加一阶段仍用 $3\times c$ thoughts 但 **删光剩余语言链**（消化 >3 步长尾）；初始 6 epoch，其后每阶段 3 epoch |
| **ProntoQA / ProsQA** | **1** | 初始 + **6** 阶段（最大步数 6）；末阶段纯 continuous thoughts；每阶段 5 epoch |
| 共性 | — | 标准日程后留在末阶段至 **50** epoch；按验证准确率选 ckpt；推理 latent 步数对齐末阶段；**greedy** |

GSM8k 训练用 Deng et al. (2023) 合成数据（文 §5.1）。

### 5.2 基线与消融

- **CoT / No-CoT**
- **iCoT**（Deng et al. 2024）：逐步删掉链首 token，「内化」后推理直接出答案
- **Pause token**（Goyal et al.）：问答之间插与 Coconut 同数量的 `<pause>`，无推理链监督

Coconut 变体：**w/o curriculum**（直接末阶段）；**w/o thought**（同课程但不加 latent）；**pause as thought**（用 pause 顶替 continuous thought，同课程）。

### 5.3 Table 1 主结果（官方 PDF；Acc. % ±；# Tokens）

| Method | GSM8k Acc / #Tok | ProntoQA Acc / #Tok | ProsQA Acc / #Tok |
|---|---|---|---|
| CoT | 42.9±0.2 / **25.0** | 98.8±0.8 / **92.5** | 77.5±1.9 / **49.4** |
| No-CoT | 16.5±0.5 / 2.2 | 93.8±0.7 / 3.0 | 76.7±1.0 / 8.2 |
| iCoT | 30.0∗ / 2.2 | 99.8±0.3 / 3.0 | 98.2±0.3 / 8.2 |
| Pause Token | 16.4±1.8 / 2.2 | 77.7±21.0 / 3.0 | 75.9±0.7 / 8.2 |
| **Coconut** | **34.1±1.5 / 8.2** | **99.8±0.2 / 9.0** | **97.0±0.3 / 14.2** |
| – w/o curriculum | 14.4±0.8 / 8.2 | 52.4±0.4 / 9.0 | 76.1±0.2 / 14.2 |
| – w/o thought | 21.6±0.5 / 2.3 | 99.9±0.1 / 3.0 | 95.5±1.1 / 8.2 |
| – pause as thought | 24.1±0.7 / 2.2 | 100.0±0.1 / 3.0 | 96.6±0.8 / 8.2 |

∗ iCoT 的 GSM8k 数字来自 Deng et al. (2024)（表注）。

**跟读要点（文 §5.3）：**

1. **链式 latent 提升表达力**：GSM8k 上 Coconut **34.1%** ≫ No-CoT **16.5%**，并超过同策略的 pause-as-thought / w/o-thought；也超过 iCoT 的 30.0%。$c: 0\to1\to2$ 稳步升（Figure 8-II）；$c=3$ 时略降且方差升，末阶段一次塞入三 thoughts 触发 loss spike（Appendix C.1）。
2. **比语言 CoT 更省 token（逻辑任务）**：ProntoQA / ProsQA 上 Coconut **准确率 ≥ CoT 且 #Tokens 显著更少**（9.0 vs 92.5；14.2 vs 49.4）。GSM8k **未超过** CoT 的 42.9%，但 Figure 8-I 显示：相对「逐步内化语言步」的 CoT 变体，用 2 个 continuous thoughts 顶替每步时，**少生成 token 时掉点更缓**——更好准确率—效率权衡。
3. **课程几乎必需**：w/o curriculum ≈ 甚至劣于 No-CoT（GSM8k 14.4）；说明仅靠 QA 梯度 **学不出** 有效 latent 推理，需语言链引导的多阶段课程。
4. **解码探针（Figure 9）**：第一个 continuous thought 解码常对应数学题中的 **中间变量**——支持「潜表示是更密的推理载体」。

### 5.4 墙钟时间（Appendix B，A100，bs=1，秒/题）

| Method | GSM8k | ProntoQA | ProsQA |
|---|---|---|---|
| No-CoT | 0.03 | 0.03 | 0.08 |
| CoT | 0.26 | 0.85 | 0.47 |
| Coconut | **0.09** | **0.11** | **0.15** |

文称墙钟大致与新生成 token 数成正比（与 Table 1 一致）。

### 5.5 更大模型（Appendix C.2，GSM8k，$c=1$）

| Model | no-CoT | Coconut |
|---|---|---|
| Llama 3.2-3B | 26.0 | **31.7** |
| Llama 3-8B | 42.2 | **43.6** |

相对 GPT-2 主实验，增益 **更小**；文猜测大模型语言预训练更重，迁到潜推理更难，并强调需 **面向推理的 latent pretraining** 才可能普遍超过语言 CoT（点名 Geiping et al. 2025、Barrault et al. 2024、Gladstone et al. 2025 为可整合方向——本卡不展开）。

---

## 六、刻意不写 / 开放问题（文内自陈）

- **不写**：完整 iCoT / pause-token / ToT / RAP 复述；ProsQA 构图 Alg.1 逐步伪代码；训练并行优化实现；把 probe 写成 MI 方法论文。
- **开放**：无语言链监督的 latent 学习；训练多次前向的效率；$c$ 更大时的细粒度课程；语言骨架 + 潜空间填槽的混合推理；扩展到预训练尺度。
- **补链（不升主项）**：议程所列 **AGCLR（2606.07720）** 作概念瓶颈相关索引；文末引用的 Zhu et al. 2025a/b（叠加态理论与训练动态）可作后续理论跟读，本卡不展开公式。

---

## 七、可跟读结论（三句）

1. **Coconut = 把 CoT 的「词回路」改成「连续 hidden 回路」**，用 `<bot>`/`<eot>` 切换模式，用多阶段课程把语言步逐步换成 $c$ 个 continuous thoughts。
2. **在 ProsQA 这类需规划的逻辑图上**，潜表示可并行编码多下一跳并推迟承诺，行为上像 **隐式 BFS**——这与 [[推理时树搜索ABMCTS]] 的 **显式外层树** 不是同一层机制。
3. **实证**：逻辑任务上相对 CoT **更高或持平准确率、更少 token / 更短墙钟**；GSM8k 上相对 No-CoT 大涨、相对 CoT 未超越但效率前沿更好；**无课程则几乎失败**。

**本地路径：** 架构/潜空间推理Coconut.md · PDF `https://arxiv.org/abs/2412.06769` · 抽取

## 相关笔记

- [[测试时训练|Test-Time Training]]
- [[潜空间推理Coconut|Coconut]]
- [[审慎对齐与断路器|Deliberative / Circuit Breakers]]
- [[DeepSeekV4技术报告深读|DeepSeek-V4]]

