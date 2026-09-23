---
title: "偏好优化新变体：SafeDPO + RePO（≠ DPO/GRPO/SimPO 主轴）"
topic: SafeDPO与RePO
date: 2026-09-22
lines: [架构思想, 目标函数接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2505.20065 # 1.9M / 40p（主 A）
 - https://arxiv.org/abs/2606.09124 # 4.6M / 33p（主 B）
 - https://arxiv.org/abs/2511.09385 # 608K / 20p（补链，不升主）
arxiv: ["2505.20065", "2606.09124", "2511.09385"]
related:
 - "对齐脉络RLHF与偏好优化"
 - "GRPO与DAPO算法族"
 - "SimPO与ORPO偏好优化"
 - "合成对齐数据Magpie"
 - "宪法分类器防御"
 - "审慎对齐与断路器"
code_promised: null
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 偏好优化新变体：SafeDPO + RePO（≠ DPO / GRPO / SimPO 主轴）

> **定位**：[[SafeDPO与RePO]] **P1 偏好优化横切**——仓库已有 RLHF/DPO 通史（**[[对齐脉络RLHF与偏好优化]]**）、可验证奖励组相对优势族（**[[GRPO与DAPO算法族]]**）、无参考/单阶段/非成对变体族（**[[SimPO与ORPO偏好优化]]**）。本卡立两条**可划界新刀**，禁止写成「又一篇 DPO / SimPO / GRPO」：
> - **SafeDPO**（*Safe Direct Preference Optimization*）：把 **硬安全约束**（不安全响应概率为零）经 cost-augmented reward 与 **安全感知偏好变换 $T$** 收成 DPO 形目标；仅需偏好对 + 二元安全指示，**无需 reward / cost RM、无需在线采样**；额外超参仅安全间隔 $\Delta$。
> - **RePO**（*Regret-based Preference Optimization*）：把人类偏好解释为 **遗憾最小化**（相对最优策略的相对次优性 + 行为策略未来序列前向 KL），而非即时/累积效用最大化；闭式更新兼容直接偏好优化，并给出无行为策略时的 **RePO_det**。
> **攻坚线**：**架构思想 / 目标函数接口（主）**——约束安全变换 vs 反事实遗憾分解；**文内安全—有用性 / 偏好—推理字段（辅）**——PKU-SafeRLHF / XSTest、AlpacaEval2 / Arena-Hard / 数学推理表。
> **硬划界（开篇钉死）**：
> - **≠ [[对齐脉络RLHF与偏好优化]]**：禁止重写 InstructGPT 三阶段、DPO 闭式最优策略证明、CAI 通史。本卡只在对照句点名 DPO 外壳。
> - **≠ [[GRPO与DAPO算法族]]**：禁止写 GRPO→DAPO、Clip-Higher、可验证奖励 RL 配方与组相对基线谱系。RePO 实验虽含数学 verifier 偏好对，贡献是 **遗憾解释**，不是 GRPO 管线。
> - **≠ [[SimPO与ORPO偏好优化]]**：禁止重写 SimPO 平均 log-prob + $\gamma$、ORPO odds ratio、KTO HALO 推导。本卡不把 AMaPO 升主。
> - **≠ [[合成对齐数据Magpie]]**：禁止写 Magpie / ActiveUltraFeedback **合成偏好数据流水线**；本卡消费静态偏好+标签，不造数据。
> - **≠ [[宪法分类器防御]] / [[审慎对齐与断路器]]**：禁止写 Constitutional Classifiers、deliberative circuit breakers 等 **安全产品/护栏机制**；本卡是 **离线偏好目标函数** 变体。
> **补链不升主**：**AMaPO**（自适应 margin，与 SimPO/固定 margin 族过近）→ §八仅索引。
> **禁止编造**：机制、命题编号、表数字一律锚定官方 PDF（2026-09-22 CST）。图内未列表格的精确曲线点标 **待核实读图**。SafeDPO / RePO 文内**未见**作者自发布官方训练仓 URL → 记为 **无承诺仓**（仅数据集 / 基线仓索引）。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主 A** | *SafeDPO: A Simple Approach to Direct Preference Optimization with Enhanced Safety* | arXiv:**2505.20065v2** \[cs.LG\]（**4 Mar 2026**）；ICLR 2026；Kim, Kim, Kim, Lee, Bae*, Jang†§, Lee‡§（LG AI Research） | `https://arxiv.org/abs/2505.20065` | **1.81MB**（1,897,644 B） | **40** | |
| **主 B** | *A Regret Minimization Framework on Preference Learning in Large Language Models* | arXiv:**2606.09124v1** \[cs.AI\]（**8 Jun 2026**）；ICML 2026（PMLR 306）；Kim*, Cho*†, Kim, Kim, Jang‡, Lee‡, Lee‡（SNU / LG AI Research / UNIST / HodooAI） | `https://arxiv.org/abs/2606.09124` | **4.58MB**（4,805,395 B） | **33** | |
| **补链** | *AMaPO: Adaptive Margin-attached Preference Optimization for Language Model Alignment* | arXiv:**2511.09385v2** \[cs.CL\]（**15 Nov 2025**）；AAAI 2026；Deng, Feng, Lei*（川大） | `https://arxiv.org/abs/2511.09385` | **0.59MB**（622,109 B） | **20** | |

| 材料 | 代码 / 数据（文内） |
|---|---|
| SafeDPO | 训练仓：**未见**作者自发布 URL。数据：`PKU-Alignment/PKU-SafeRLHF-30K`；参考起点：`alpaca-7b-reproduced-llama-2`；评判：`beaver-7b-unified-reward` / `beaver-7b-unified-cost` |
| RePO | 训练仓：**未见**作者自发布 URL。基线实现索引：OpenRLHF（DPO/IPO/KTO）、RPO、TDPO 第三方仓（附录） |
| AMaPO（补链） | `https://github.com/Shiroha-Offical/AMaPO`（文首标注；本卡不跟 commit） |

**体积判定（2026-09-22 CST，`ls` / `os.path.getsize`）：**

| 文件 | 体积 | 备注 |
|---|---|---|
| `2505.20065-safedpo.pdf` | **1.81MB** | **官方 HTTPS 外链**（≪10MB） |
| `2606.09124-repo.pdf` | **4.58MB** | **官方 HTTPS 外链**（≪10MB） |
| `2511.09385-amapo.pdf` | **0.59MB** | **官方 HTTPS 外链**（补链；≪10MB） |

**一句话抓手：**
- **SafeDPO**：别再训 cost RM / 多阶段 SafeRLHF——用安全标签 **换序/丢弃** 偏好对，再可选加 $\Delta$ 间隔，把硬约束收成单阶段 DPO。
- **RePO**：别把中间步偏好当成「到目前为止的即时奖励」——按 **负遗憾**（最优相对似然 − 行为策略未来序列 KL）打分，显式吃行为策略与反事实展开。

---

## 二、议题边界：两条新刀 ≠ 已入库偏好主轴

### 2.1 五向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| RLHF / DPO 通史与闭式推导 | 三阶段、隐式奖励 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$ | **[[对齐脉络RLHF与偏好优化]]** | **否** |
| GRPO / DAPO 等组相对 + 可验证奖励 | 在线采样、组内优势、Clip 配方 | **[[GRPO与DAPO算法族]]** | **否** |
| SimPO / ORPO / KTO | 无 ref、单阶段、非成对标签 | **[[SimPO与ORPO偏好优化]]** | **否** |
| Magpie / ActiveUF | 指令/偏好 **数据从哪来** | **[[合成对齐数据Magpie]]** | **否** |
| Constitutional Classifiers / circuit breakers | 推理期护栏 / 产品安全机制 | **[[宪法分类器防御]] / [[审慎对齐与断路器]]** | **否** |
| **SafeDPO** | 偏好对 + **安全指示** → 硬约束等价目标 | **本篇主文 A** | **是** |
| **RePO** | 偏好 = **遗憾/反事实次优性**（非即时效用） | **本篇主文 B** | **是** |
| AMaPO | 实例自适应 margin 改排序梯度 | 补链 §八 | **否（不升主）** |

跟读直觉：[[对齐脉络RLHF与偏好优化]]/[[SimPO与ORPO偏好优化]] 问「**helpful 偏好损失怎么写**」；[[GRPO与DAPO算法族]] 问「**有 verifier 时怎么做在线组相对 RL**」；SafeDPO 问「**已有安全标签时，如何把硬约束塞进离线 DPO 外壳**」；RePO 问「**人类偏好是否应从遗憾而非奖励最大化来建模**」。四者外壳可同为「成对 log-ratio + $\sigma$」，但**贡献旋钮不同**。

### 2.2 双主文自划界（文内）

- **SafeDPO**：对照 SafeRLHF / SACPO / CAN——批评其依赖 **辅助 RM/cost、多阶段或期望代价松弛**；主张直接分析原硬约束式 (6)，经 $T(\mathcal{D})$ 落到式 (11)(12)。Figure 1 明示：相对 DPO 只多蓝项（安全指示）；相对 Safe RLHF 少红项（RM/cost/在线采样）。
- **RePO**：Related work 把 DPO/TDPO/RPO/IPO 放在「奖励最大化视角下的目标修补」；把自己放在 CPL/PPL/KTO 一侧的 **Beyond Reward Maximization**，但贡献是 **KL-正则 MDP 下的遗憾闭式 + 序列前向 KL 估计**，不是 KTO 前景理论重写（KTO 细节 → [[SimPO与ORPO偏好优化]]）。

`
 离线偏好优化外壳（成对 / BT / log-ratio）
 │
 ┌───────────┼───────────────┐
 ▼ ▼ ▼
 DPO/SimPO SafeDPO RePO
 (有用性主轴) (安全硬约束变换) (遗憾最小化)
 [[对齐脉络RLHF与偏好优化]]/[[SimPO与ORPO偏好优化]] 本篇 A 本篇 B
`

---

## 三、站 1：SafeDPO — 硬安全约束 → 安全感知 DPO（2505.20065）

### 3.1 问题设定（§2.2）

安全对齐数据：$(x,y_w,y_l,h_w,h_l)\sim\mathcal{D}$，其中 $h=1\{c(x,y)>0\}$ 为 **不安全** 指示。原硬约束问题（式 6）：

$$
\max_\theta\ \mathbb{E}[r(x,y)-\beta D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})]
\quad\text{s.t.}\quad c(x,y)\le 0\ \forall x,y\sim\pi_\theta.
$$

先验工作常松弛为期望代价 $\mathbb{E}[c]\le\hat C$（式 7）。SafeDPO **拒绝**以期望松弛代替硬约束，主张在可解前提下保留「不安全响应支撑为零」。

### 3.2 三步推导（§3.1–3.3）

**（1）Cost-augmented reward → 闭式策略。** 定义 $r_c=r$（安全）或 $-\infty$（不安全），得无约束式 (8)；最优策略

$$
\pi^*(y|x)=\frac{1}{Z(x)}\pi_{\mathrm{ref}}(y|x)\exp\!\big(\tfrac{1}{\beta}r_c(x,y)\big)
\quad\Rightarrow\quad \pi^*(y|x)=0\ \text{若}\ c(x,y)>0.\quad (9)
$$

由此诱导理论偏好分布 $\tilde{\mathcal{D}}$ 与不可观 DPO 形目标式 (10)。

**（2）安全感知变换 $T$（可计算代理）。** 因任意安全响应在 $r_c$ 下优于任意不安全响应：

$$
T(x,y_w,y_l,h_w,h_l)=
\begin{cases}
(x,y_w,y_l) & h_w=0\\
(x,y_l,y_w) & h_w=1,\ h_l=0\\
\emptyset & h_w=h_l=1
\end{cases}
$$

即：preferred 已安全 → 保留；preferred 不安全且 loser 安全 → **交换**；双不安全 → **丢弃**。在 $T(\mathcal{D})$ 上写标准 DPO：

$$
\mathcal{L}_{\mathrm{SafeDPO}}(\theta)
=-\mathbb{E}_{T(\mathcal{D})}\log\sigma\Big(
\beta\log\frac{\pi_\theta(\tilde y_w|x)}{\pi_{\mathrm{ref}}(\tilde y_w|x)}
-\beta\log\frac{\pi_\theta(\tilde y_l|x)}{\pi_{\mathrm{ref}}(\tilde y_l|x)}
\Big).\quad (11)
$$

**命题 4.3**：对任意 $\theta$，不可观式 (10) **等于** 式 (11)。

**（3）安全间隔 $\Delta\ge 0$（优化动力，不改最优集）。**

$$
\mathcal{L}_{\mathrm{SafeDPO}}(\theta;\Delta)
=-\mathbb{E}_{T(\mathcal{D})}\log\sigma\Big(
\beta\log\frac{\pi_\theta(\tilde y_w|x)}{\pi_{\mathrm{ref}}}
-\beta\log\frac{\pi_\theta(\tilde y_l|x)}{\pi_{\mathrm{ref}}}
-(\tilde h_l-\tilde h_w)\Delta
\Big).\quad (12)
$$

仅在（安全,不安全）对上 $(\tilde h_l-\tilde h_w)=1$ 时推大间隔；同安全状态时项为零。**命题 4.4**：任意 $\Delta\ge 0$，式 (11) 与 (12) **共享同一最优解集**。文注 $\Delta=50$ 等过大值会在有限训练中伤 helpfulness（附录 A.4）——跟读时区分「最优集不变」与「有限步动力学」。

**SafeDAA（§3.4）：** 同一 $T$ + $\Delta$ 可挂到一般 DAA（式 5 的凸 $g$）；本文只实例化 DPO。

### 3.3 理论三件套（§4；证明 → 附录 A）

| 结果 | 内容 |
|---|---|
| **假设 4.1** | 每个 $x$ 上参考策略对安全响应集 $Y_s(x)$ 质量 $\ge\delta>0$（可行性） |
| **命题 4.2** | 式 (8) 最优解在惩罚 $C\to\infty$ 时 TV 收敛到硬约束式 (6) |
| **命题 4.3** | $T(\mathcal{D})$ 无偏恢复式 (10) |
| **命题 4.4** | $\Delta$ 不改变全局最优集合 |

### 3.4 实验字段（§5；禁外推未测场景）

**床：** PKU-SafeRLHF-30K（~27k train / 3k test）；共享 SFT 起点（Alpaca-7B reproduced on 同数据）。
**基线：** DPO-HELPFUL / DPO-HARMLESS / **DPO-SAFEBETTER**（仅滤掉 preferred 不安全的对——用于证明「只过滤不够」）/ SafeRLHF (PPO-λ) / SACPO / P-SACPO。
**主协议：** beaver reward/cost；GPT-4 有用/无害；人评（末 100 题 ×5 标注员）。

**模型评判 Figure 2(a) 精确值（附录 Table 17）：**

| Method | Helpfulness (N) | Harmless Ratio (%) | Harmlessness |
|---|---|---|---|
| DPO-HELPFUL | 10.00 | 37.59 | −2.23 |
| DPO-SAFEBETTER | 9.08 | 49.75 | −0.20 |
| SafeRLHF | 4.23 | 88.97 | 3.63 |
| SACPO | 2.80 | 89.60 | 4.34 |
| **SafeDPO** | **4.61** | **96.87** | **5.97** |

**GPT-4 Figure 2(b)（Table 18）：** SafeDPO Helpfulness **8.14**、Harmless Ratio **100%**、Harmlessness **9.92**（同表 SafeRLHF 96.62% / 9.57）。正文强调：GPT 可能把「更安全」误读进「更有用」（附录 C/D）——人评 Table 2 中 SFT helpfulness **0.868** 高于 SafeDPO **0.499**，与 GPT 排序不一致，跟读必记。

**人评 Table 2：** SafeDPO Safety **0.943** vs SafeRLHF **0.932**；Helpfulness 二者接近（0.499 / 0.497）。

**$\Delta$ 扫描（§5.1.3）：** $\Delta\in\{0,2,5,10,20\}$；$\Delta=0$（仅 $T$）已高 harmless ratio；主对比常用 $\Delta=10$。把同一 $\Delta$ 挂到普通 DPO **达不到** SafeDPO 安全水平 → **变换 $T$ 是主因，间隔是加强信号**。

**规模 Table 1（1.5B–13B，同超参）：** Harmless ratio 约 **95.5–97.9%**；13B Helpfulness **7.60**（表内最高）。

**XSTest 过拒 Table 3（裁判 GPT-5.1）：**

| Method | Over-refusal (%) | Harmless ratio (%) |
|---|---|---|
| DPO-HELPFUL | 0 | 14.5 |
| SafeRLHF | 3.2 | 84.5 |
| SACPO | 2.4 | 86 |
| **SafeDPO** | **12.4** | **100** |

文内自陈：硬约束换来 **完全压制不安全**，但边界良性提示（词面像有害）上更保守——这是目标函数结构 trade-off，不是表外编造。

---

## 四、站 2：RePO — 遗憾最小化偏好学习（2606.09124）

### 4.1 动机：奖励最大化与人类判断的机制错位（§4.1）

文内两刀（配合 Figure 1–3）：

1. **前瞻（prospective）：** 人类对中间推理段的偏好依赖「想象中的未来续写」，不是「到目前为止已实现即时奖励」。奖励最大化把未完成段只按已实现 $r$ 计，会把「暂零奖但通向正确终态」的段判成与失败段无异。
2. **反事实（counterfactual）：** 人类比较「若当初选另一动作会怎样」；实现收益更高的动作未必更接近最优策略。

因此主张：偏好分数应是 **负遗憾**（相对最优的次优性），而非局部效用。

### 4.2 遗憾定义与闭式（§4.2 / §5）

在逐步 KL-正则 RL（式 1）下，定义行为策略 $\mu$ 相对 $\alpha$-最优 $\pi^*$ 的遗憾：

$$
\mathrm{Reg}^\mu_{\pi^*}(q_{<t},o_t)
:= V^{\pi^*}(q_{<t})-Q^\mu(q_{<t},o_t)
= -\alpha\log\frac{\pi^*(o_t|q_{<t})}{\pi_{\mathrm{ref}}(o_t|q_{<t})}
-\bar D_{\mathrm{KL}}(\mu\|\pi^*;q_{<t},o_t)
$$

其中 $\bar D_{\mathrm{KL}}$ 为未来轨迹上的 **折扣序列前向 KL**（定理 5.4）。**引理 5.5**：该分解对 $(\alpha,\pi^*)$-等价奖励类中的状态塑形 $\beta(\cdot)$ **不变**——文称这是相对「奖励最大化需锚定 $\beta$」的结构优势。

直觉拆两项：
- **局部项** $-\alpha\log(\pi^*/\pi_{\mathrm{ref}})$：与 DPO 同族的相对似然；
- **长程项** $\bar D_{\mathrm{KL}}$：惩罚行为策略相对最优的未来偏离（离线/异策略时 DPO 隐式当作 on-policy 会失配；对照 PPL/Cho et al. 2025）。

### 4.3 可实现估计（§6）

精确 $\bar D_{\mathrm{KL}}$ 需从每步重 rollout → 用观察到的 $q^+,q^-$ 作单条 Monte Carlo，有限时域平均化，得经验遗憾分数 $S^{\mathrm{RePO}}$（含 $\mu$ 的 token logprob）。
**RePO_det：** $\mu=\delta_{o_t}$（Dirac 伪标签），无行为策略元数据时仍可训；跨 tokenizer / 跨模型族时更实用。

**引理 6.1（归纳偏置）：** 在 $\epsilon\ge 0$（$\mu$ 更近 $\pi^*$ 而非 $\pi_{\mathrm{ref}}$）且终态 verifier-accepted 时，终态遗憾上界于中间上下文期望遗憾 → **截断成功轨迹会被系统性地判得更差**；文称此偏置使 RePO **无需**像 DPO 那样靠 mask 增广才学到「完整成功 > 截断成功」。

### 4.4 实验字段（§7）

**人类偏好（UltraFeedback 协议合成，~16K 对，保留行为 logprob；Qwen3-1.7B/4B + LoRA）— Table 1 节选：**

| Method | Qwen3-1.7B AE2 LC / WR | Arena-Hard WR | Qwen3-4B AE2 LC / WR | Arena-Hard WR |
|---|---|---|---|---|
| DPO | 23.90 / 25.84 | 23.4 | 32.89 / 33.92 | 44.5 |
| KTO | 34.73 / 38.93 | 30.4 | 52.31 / 55.78 | 63.9 |
| **RePO** | **36.61 / 43.66** | 27.1 | **55.08 / 60.12** | 60.1 |
| RePO_det | 34.95 / 41.42 | 26.6 | 51.66 / 55.53 | 59.9 |

跟读：1.7B 上 RePO 相对 DPO 的 AE2 LC **+12.71**；Arena-Hard 上 KTO 有时更高（1.7B: 30.4 vs RePO 27.1；4B: KTO 63.9 vs RePO 60.1）——**勿报成全面碾压**。

**数学推理（Qwen2.5-7B-Math-Instruct 造对，~69K；正确≻错误）— Table 2 节选（Qwen3-1.7B-Base）：**

| Method | GSM8K | MATH | MATH500 | Minerva |
|---|---|---|---|---|
| DPO | 77.33 | 53.44 | 52.80 | 16.91 |
| KTO | 79.68 | 54.42 | 56.60 | 17.28 |
| **RePO** | 80.52 | **54.50** | **57.40** | 20.59 |
| **RePO_det** | **80.74** | **54.84** | 54.40 | **25.74** |

4B 上 RePO_det GSM8K **91.05** 最高；KTO 在 AMC23 等个别榜更高（55.00 vs RePO 42.50）——单榜例外保留。

**无行为策略离线（Table 3，Llama3.1-8B）：** Base 设定 RePO_det GSM8K **62.17** vs KTO 61.56、DPO 44.50；Instruct 设定 MATH/MATH500 上 RePO_det **46.46 / 47.40** 领先，但 GSM8K 上 KTO **84.61** > RePO_det **80.44**。

**样本效率（§7.3 / Table 4 / Figure 5）：** 对成功轨迹 mask 末 {16…80} token 作增广时，DPO 吃增广（Qwen3-1.7B GSM8K 72.55→77.71）；RePO 几乎持平（80.52→80.29），且相对 RePO 诱导分数的 MSE：DPO 0.073→增广后 0.056（更靠近 RePO）。文称遗憾目标 **内化** 了 DPO 需靠数据学的「完整成功偏好」偏置。

---

## 五、双刀对照（本卡主轴）

| | **SafeDPO** | **RePO** |
|---|---|---|
| **改的是什么** | 数据变换 $T$ + 可选 $\Delta$（外壳仍是 DPO） | 偏好分数语义：负遗憾 + 序列 KL |
| **额外监督** | 二元安全指示 $h$ | 行为策略 logprob（或 Dirac 伪标签） |
| **相对 DPO 的理论承诺** | 硬约束最优 / $T$ 无偏 / $\Delta$ 最优集不变 | 奖励塑形不变性；异策略未来偏离显式入账 |
| **主战场** | 安全–有用权衡（PKU-SafeRLHF、XSTest） | 通用偏好榜 + 数学推理（AE2/Arena、GSM8K/MATH） |
| **明确代价** | XSTest 过拒升高（12.4%） | 需估计未来 KL；Arena 等个别榜不总压过 KTO |
| **不回答** | 护栏产品、合成数据、GRPO 在线环 | SimPO 式解码对齐 margin、安全硬约束 |

二者作者群有重叠（LG AI Research / Jang / Lee 线），但问题定义正交：**一个把安全标签焊进约束最优，一个把反馈语义从 reward 换成 regret**——禁止并成「同一方法的两个名字」。

---

## 六、与相邻笔记的禁止清单（验收用）

| 笔记 | 本卡禁止写入的内容 |
|---|---|
| **[[对齐脉络RLHF与偏好优化]]** | InstructGPT 三阶段精读、DPO 最优策略推导全文、CAI |
| **[[GRPO与DAPO算法族]]** | GRPO/DAPO/Clip-Higher、组相对优势公式、RLVR 训练菜谱 |
| **[[SimPO与ORPO偏好优化]]** | SimPO $\frac{\beta}{\|y\|}\log\pi$、ORPO odds ratio、KTO 损失展开 |
| **[[合成对齐数据Magpie]]** | Magpie 无种子合成、ActiveUF bandit 选对 |
| **[[宪法分类器防御]] / [[审慎对齐与断路器]]** | Constitutional Classifiers、deliberative circuit breakers 机制与产品评测 |
| **AMaPO** | 自适应 margin 主文级展开（→ 仅 §八补链） |

---

## 七、跟读清单与误区

**建议跟读顺序：**
1. SafeDPO Figure 1 + §3 $T$/式 (11)(12) + Table 17/18/3；
2. RePO Figure 1–3 + 遗憾分解 + §6 估计器 + Table 1–4；
3. 本卡 §五对照表；AMaPO 只扫 Abstract + 议程「不升主」句。

**常见误区：**
1. 把 SafeDPO 写成「DPO + 安全 RM」——文明确 **无** reward/cost model。
2. 把 DPO-SAFEBETTER 当成 SafeDPO——过滤 ≠ 换序+惩罚不安全。
3. 把 RePO 写成 GRPO/RLVR——RePO 是 **离线偏好目标语义**；数学实验只用 verifier **造偏好对**。
4. 把 RePO 写成 KTO「又一个非 BT」——KTO 是二元标签+前景理论（[[SimPO与ORPO偏好优化]]）；RePO 仍用成对 BT 外壳，改的是 **score=负遗憾**。
5. 只报 RePO 赢的榜、抹掉 Arena-Hard / AMC23 上 KTO 更高的行。
6. 把 AMaPO 当第三主文——与 SimPO margin 轴过近，议程指定补链。
7. 编造 SafeDPO/RePO 官方 GitHub——本地抽取 **未见**；仅 AMaPO 有文首仓。

**开放问题（文内已暗示，本卡不编造答案）：** SafeDPO 数据集单一、≤13B；过拒–安全帕累托如何调 $\Delta$ 以外的机制；RePO 的 $\bar D_{\mathrm{KL}}$ 截断偏差与跨域 tokenizer；遗憾偏置在非 verifier 域是否仍成立。

---

## 八、补链：AMaPO（2511.09385）— 仅索引，不升主

- **一句话：** 统一 margin 框架诊断 DPO 族 **过拟合（已排对仍大梯度）/ 欠拟合（排错梯度不足）**；提出实例自适应 margin（Z-norm + 指数缩放；已排对则 margin→0）。
- **为何不升主：** 与 **[[SimPO与ORPO偏好优化]] SimPO**（固定/目标间隔 $\gamma$）同属「改 margin 提排序准确率」轴；议程明确 **过近 SimPO → 仅补链**。
- **文内指针：** 代码 `https://github.com/Shiroha-Offical/AMaPO`；Table 2 四设定 AE2/MT；相对 SimPO 的排序准确率/OOD 表（Table 4）——细节不展开。
- **与本卡双主的关系：** AMaPO 不引入安全约束，也不改「奖励 vs 遗憾」语义；若后续单独立项，应挂 [[SimPO与ORPO偏好优化]] 延伸而非本卡续篇。

---

| 文件 | `ls` 体积 | 页数 | 备注 |
|---|---|---|---|
| `https://arxiv.org/abs/2505.20065` | 1,897,644 B（**1.81MB**） | 40 | **入库二进制** + 抽取 |
| `https://arxiv.org/abs/2606.09124` | 4,805,395 B（**4.58MB**） | 33 | **入库二进制** + 抽取 |
| `https://arxiv.org/abs/2511.09385` | 622,109 B（**0.59MB**） | 20 | **入库二进制**（补链）+ 抽取 |

{safedpo,repo,amapo}.txt`（并镜像 ）。
笔记路径：`/workspace/AIResearch-drafts/对齐与强化学习/SafeDPO与RePO.md。

**本卡主张锚点（抽查用）：**
- SafeDPO $T$ 三分支与式 (11)(12)；命题 4.3/4.4；Table 17 harmless ratio **96.87%**；XSTest 过拒 **12.4%** / 无害 **100%**。
- RePO 遗憾 = 局部 log-ratio + 序列 $\bar D_{\mathrm{KL}}$；RePO_det；Table 1 Qwen3-1.7B AE2 LC **36.61**；Table 4 mask 增广对 DPO vs RePO 的不对称增益。
- AMaPO 仅 §八；划界五条开篇钉死。
