---
title: "GRPO → DAPO / Dr.GRPO 后训练算法族专线"
topic: GRPO与DAPO算法族
date: 2026-09-22
lines: [数学原理, 架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2402.03300
 - https://arxiv.org/abs/2503.14476
 - https://arxiv.org/abs/2503.20783
 - https://arxiv.org/abs/2503.06639
arxiv: ["2402.03300", "2503.14476", "2503.20783", "2503.06639"]
archived: 2026-09-22
---

# GRPO → DAPO / Dr.GRPO 后训练算法族专线

> **定位**：[[GRPO与DAPO算法族]] P0 横切——立 **后训练 RL 算法谱系**（目标函数 / 组相对优势 / 变体），**不**重写 R1 多阶段管线表（见 [[DeepSeekR1推理训练深读]]）。
> **攻坚线**：**数学原理（主）** + **架构思想（辅）**。
> **刻意不写**：R1-Zero→R1 冷启动 / 拒绝采样 / 二次 RL 阶段表；[[对齐脉络RLHF与偏好优化]] RLHF·DPO·CAI 通史；[[推理时扩展TestTimeScaling]] test-time scaling「势」叙事。本篇只串 **GRPO 目标 → DAPO 四技 → Dr.GRPO 去偏**。
> **禁止编造**：公式、超参、消融数字一律取自官方 PDF（2026-09-22 CST）；议程所列 `2503.06639` **不是** Dr.GRPO——Dr.GRPO 出自 `2503.20783`（已补入）；`2503.06639` 作可选 RLVR 动力学对照。

---

## 一、材料元信息与谱系抓手

| 代号 | 标题（封面/页眉） | arXiv / 页眉版本 | 官方 PDF | 页数 | 在谱系中的角色 |
|---|---|---|---|---:|---|
| **GRPO** | DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models | **2402.03300v3** \[cs.CL\] **27 Apr 2024** | `https://arxiv.org/abs/2402.03300` | 30 | **原点**：去 critic、组内相对优势、KL 进损失 |
| **DAPO** | DAPO: An Open-Source LLM Reinforcement Learning System at Scale | **2503.14476v2** \[cs.LG\] **20 May 2025**；文内 Date: March 17, 2025 | `https://arxiv.org/abs/2503.14476` | 16 | **工程变体族**：Clip-Higher / Dynamic Sampling / token-level loss / Overlong Reward Shaping |
| **Dr. GRPO** | Understanding R1-Zero-Like Training: A Critical Perspective | **2503.20783v2** \[cs.LG\] **6 Oct 2025**（COLM 2025） | `https://arxiv.org/abs/2503.20783` | 20 | **去偏改写**：去掉 \|o\| 与 std 归一，称 *GRPO Done Right* |
| **RLVR 动力学（可选）** | Reinforcement Learning with Verifiable Rewards: GRPO’s Effective Loss, Dynamics, and Success Amplification（Youssef Mroueh, IBM） | **2503.06639v4** \[cs.LG\] **20 Oct 2025** | `https://arxiv.org/abs/2503.06639` | 23 | **理论对照**：可验证奖励下 GRPO 有效损失 / PoS 放大；**文中无「Dr. GRPO」命名** |

**一句话谱系：** DeepSeekMath 用 **同题一组 rollout 的均值/标准差** 代替 value baseline（GRPO）→ R1 族大规模采用同构思想（细节见 [[DeepSeekR1推理训练深读]]，此处不表）→ DAPO 针对长 CoT 上的 **熵崩塌、零优势样本、sample-level 损失、截断噪声** 给出可复现四技 → Dr. GRPO 从目标函数证明 GRPO 的 \|o\|/std 项引入长度与难度偏置并给出去偏形式；Mroueh (2503.06639) 在可验证二元奖励下分析 GRPO 迭代放大成功概率。

 · · ·

---

## 二、GRPO（DeepSeekMath §4.1）— 目标与组相对优势

### 2.1 相对 PPO 的架构意图（辅）

据 **Figure 4** 与 §4.1.1：

| | **PPO** | **GRPO** |
|---|---|---|
| Advantage 来源 | GAE + **learned value** $V_\psi$ | **同题组内奖励** 的相对量，**无 value model** |
| KL 放哪 | 常把 per-token KL **加进 reward**（文给式 (2)） | **直接加进目标**，避免搅乱 $\hat A_{i,t}$ |
| 资源 | policy + reward + value（量级相当） | 省去 value；用组分数估 baseline |

原文动机（意译要点，据 §4.1.1）：LLM 场景常 **只在末 token 赋分**，逐 token value 难训准；组相对优势与「同题比较」的 RM 训练形态对齐。

### 2.2 PPO 对照目标（式 1）

$$
J_{\mathrm{PPO}}(\theta)
=
\mathbb{E}_{q\sim P(Q),\, o\sim\pi_{\theta_{\mathrm{old}}}(\cdot\mid q)}
\frac{1}{|o|}
\sum_{t=1}^{|o|}
\min\Big(
r_t(\theta)\,\hat A_t,\;
\mathrm{clip}\big(r_t(\theta),\,1-\varepsilon,\,1+\varepsilon\big)\,\hat A_t
\Big)
$$

其中 $r_t(\theta)=\pi_\theta(o_t\mid q,o_{<t})/\pi_{\theta_{\mathrm{old}}}(o_t\mid q,o_{<t})$；$\hat A_t$ 由 GAE 得（§4.1.1）。

### 2.3 GRPO 目标（式 3；主）

对每个问题 $q$，从 $\pi_{\theta_{\mathrm{old}}}$ 采样一组 $\{o_i\}_{i=1}^{G}$，最大化：

$$
\begin{aligned}
J_{\mathrm{GRPO}}(\theta)
&=
\mathbb{E}_{q\sim P(Q),\,\{o_i\}_{i=1}^{G}\sim\pi_{\theta_{\mathrm{old}}}(\cdot\mid q)}
\Bigg[
\frac{1}{G}\sum_{i=1}^{G}
\frac{1}{|o_i|}\sum_{t=1}^{|o_i|}
\Big(
\min\big(
r_{i,t}(\theta)\,\hat A_{i,t},\;
\mathrm{clip}(r_{i,t}(\theta),1-\varepsilon,1+\varepsilon)\,\hat A_{i,t}
\big)
\beta\, D_{\mathrm{KL}}\!\big(\pi_\theta\|\pi_{\mathrm{ref}}\big)
\Big)
\Bigg]
\end{aligned}
$$

**无偏 KL 估计（式 4，Schulman 2020）：**

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})
=
\frac{\pi_{\mathrm{ref}}(o_{i,t}\mid q,o_{i,<t})}{\pi_\theta(o_{i,t}\mid q,o_{i,<t})}
\log\frac{\pi_{\mathrm{ref}}(o_{i,t}\mid q,o_{i,<t})}{\pi_\theta(o_{i,t}\mid q,o_{i,<t})}
- 1
$$

（文称保证非负。）

### 2.4 组相对优势：Outcome / Process（§4.1.2–4.1.3）

**Outcome supervision（最常用骨架）：**
组奖励 $\mathbf{r}=\{r_1,\ldots,r_G\}$ **减均值、除标准差**；末 token 得归一化奖励后，**该序列全部 token 共享同一优势**：

$$
\hat A_{i,t}
=
\tilde r_i
=
\frac{r_i - \mathrm{mean}(\mathbf{r})}{\mathrm{std}(\mathbf{r})}
$$

**Process supervision：** 逐步 RM 打分，步奖励同样做组内均值/方差归一；token $t$ 的优势为 **后续各步归一化奖励之和** $\hat A_{i,t}=\sum_{\mathrm{index}(j)\ge t}\tilde r_i^{\mathrm{index}(j)}$。

### 2.5 迭代 GRPO（Algorithm 1）与文内超参要点

Algorithm 1 要点（原文步骤）：每外层 iteration 把 $\pi_{\mathrm{ref}}\leftarrow\pi_\theta$；内层 step 更新 $\pi_{\theta_{\mathrm{old}}}$、采样 $G$ 条、算组相对 $\hat A$、做 $\mu$ 次 GRPO 更新；并可 **持续训奖励模型**（含 10% 历史 replay）。

文内 GRPO 实验设定摘录（§4 训练段）：policy LR **1e-6**；KL 系数 **0.04**；**每题采样 64** outputs（相对后续 R1 的 $G{=}16$ 为 DeepSeekMath 原设定）。

> **边界：** DeepSeekMath 阶段仍大量用 **奖励模型**；可验证规则奖励 + 大规模长 CoT 的叙事在 R1 TR——**勿把本篇写成 R1 管线复述**。

---

## 三、DAPO（Yu et al.）— 在 GRPO 骨架上的四技

### 3.1 问题诊断（相对 naive GRPO）

底座：**Qwen2.5-32B** base；初始 naive GRPO 在 AIME 2024 仅约 **30**（avg@32 口径，Table 1），远低于文中对照的 DeepSeek-R1-Zero-Qwen-32B **47**。文指 naive GRPO 面临：**熵崩塌、奖励噪声、训练不稳** 等（§1）。

**相对 GRPO 的两处显式偏离（§2.3–2.4）：**

1. **去掉 KL 项**：长 CoT 推理训练中策略可显著偏离初始分布，文认为 RLHF 式「贴住 $\pi_{\mathrm{ref}}$」**不必要**（§2.3）。
2. **规则 outcome 奖励**（式 7）：$R=+1$ 若等价正确，否则 $-1$（可验证任务；防 reward hacking）。

GRPO 优势写法（DAPO 式 4 / 9，与 DeepSeekMath outcome 同构）：

$$
\hat A_{i,t}
=
\frac{R_i - \mathrm{mean}(\{R_i\}_{i=1}^{G})}{\mathrm{std}(\{R_i\}_{i=1}^{G})}
$$

文强调：原 GRPO 目标按 **sample-level** 归约——先对序列内 token 取均，再对样本取均（§2.2），与后文 token-level 对照。

### 3.2 DAPO 总目标（式 8）与 Algorithm 1

**Decoupled Clip and Dynamic sAmpling Policy Optimization**：

$$
\begin{aligned}
J_{\mathrm{DAPO}}(\theta)
&=
\mathbb{E}_{(q,a)\sim\mathcal{D},\,\{o_i\}\sim\pi_{\theta_{\mathrm{old}}}}
\Bigg[
\frac{1}{\sum_{i=1}^{G}|o_i|}
\sum_{i=1}^{G}\sum_{t=1}^{|o_i|}
\min\Big(
r_{i,t}(\theta)\,\hat A_{i,t},\;
\mathrm{clip}\big(r_{i,t}(\theta),\,1-\varepsilon_{\mathrm{low}},\,1+\varepsilon_{\mathrm{high}}\big)\,\hat A_{i,t}
\Big)
\Bigg] \\
&\quad\text{s.t.}\quad
0 < \bigl|\{o_i:\ \mathrm{is\_equivalent}(a,o_i)\}\bigr| < G
\end{aligned}
$$

（式 8–9：比率 $r_{i,t}$ 与组标准化 $\hat A$ 同 GRPO；**无** $\beta D_{\mathrm{KL}}$；分母为 **组内总 token 数**——对应 §3.3 的 token-level 归约。版式抽取中分子分母排版嘈杂，以上以 §3.3 散文「按 token 等权、长序列影响更大」与式 (12) 叙述为准。）

Algorithm 1：采样 → 算奖励 → **Dynamic Sampling 过滤进 buffer** → buffer 满 $N$ 后算 $\hat A$ → $\mu$ 次最大化 DAPO 目标。

### 3.3 四技（据原文 §3.1–3.4；主）

#### （1）Clip-Higher（解耦上下 clip）

- **现象：** $\varepsilon{=}0.2$ 时熵快速下降，组内回答近乎相同（Fig. 2）。
- **机制直觉（原文数值例）：** $A>0$ 时抬概率，旧概率 $0.01$ vs $0.9$ 的上界分别为 $0.012$ 与 $1.08$——**探索 token 难抬、剥削 token 易抬到极端**。观测到被上 clip 的 token 平均概率 $<0.2$（Fig. 3a）。
- **做法：** $\varepsilon_{\mathrm{low}}$ 与 $\varepsilon_{\mathrm{high}}$ **解耦**；**抬高** $\varepsilon_{\mathrm{high}}$ 给低概率 token 空间；**保持** $\varepsilon_{\mathrm{low}}$（抬高下界会把概率压向 0、塌缩采样空间）。
- **实验设定：** $\varepsilon_{\mathrm{low}}=\mathbf{0.2}$，$\varepsilon_{\mathrm{high}}=\mathbf{0.28}$（§4.1）。

#### （2）Dynamic Sampling

- **现象：** 组内全对（或奖励全同）→ $\hat A{=}0$ → 零梯度；随训练 accuracy=1 的 prompt 比例上升（Fig. 3b），有效 batch 变小、梯度噪声变大。
- **做法：** 过采样并 **过滤 accuracy∈{0,1} 的 prompt**，只保留 $0<\mathrm{acc}<1$（式 11 约束）；凑满有效 batch 再更新。文称采样成本动态，但同步系统中长尾生成占时，整体墙钟甚至更快（Fig. 6）。

#### （3）Token-Level Policy Gradient Loss

- **对照：** GRPO **sample-level**（每条样本等权）→ 长样本内每个 token 对总损失贡献被稀释。
- **危害（原文）：** (i) 高质量长推理难学；(ii) 过长样本中的乱码/重复难被惩罚 → 熵与长度「不健康」上升（Fig. 4）。
- **做法：** 在 **全部生成 token** 上归约（式 12 / 总目标式 8 的 $1/\sum|o_i|$ 形式）；长序列对梯度影响更大；同一模式无论出现在长短回答中被同等激励/抑制。
- **消融口径：** token-level 对 AIME 点数提升不大，但 **稳定性** 与长度增长更健康（§4.2）。

#### （4）Overlong Reward Shaping

- **噪声源：** 达最大长度截断后默认惩罚 → 可能惩罚「推理正确但过长」的轨迹。
- **Overlong Filtering：** 对截断样本 **mask 损失** → 稳定且抬分（Fig. 5）。
- **Soft Overlong Punishment（式 13）：** 设 $L_{\max}$、缓存宽 $L_{\mathrm{cache}}$；在 $(L_{\max}-L_{\mathrm{cache}},\,L_{\max}]$ 内线性惩罚，超过 $L_{\max}$ 为 $-1$；加到规则正确性奖励上。
- **设定：** 期望最大长 **16,384**；soft cache **4,096** → 生成上限 **20,480**（§4.1）。

### 3.4 渐进消融（Table 1，AIME24 avg@32）

| 配置 | AIME24 avg@32 |
|---|---:|
| DeepSeek-R1-Zero-Qwen-32B（文内对照） | **47** |
| Naive GRPO | **30** |
| + Overlong Filtering | **36** |
| + Clip-Higher | **38** |
| + Soft Overlong Punishment | **41** |
| + Token-level Loss | **42** |
| + Dynamic Sampling（**= DAPO**） | **50** |

文称相对 R1-Zero-Qwen-32B，DAPO 在 Qwen2.5-32B 上达 **50**，且约用其 **50% training steps**（Fig. 1 / §4.2）。其他训练超参摘录：AdamW LR **1e-6**（20 rollout warmup）；prompt batch **512**；每 prompt **G=16**；mini-batch **512**（每 rollout 16 次梯度更新）。

数据：答案改造为整数易解析 → **DAPO-Math-17K**（§3.5）。代码：基于 **verl**；项目页 https://dapo-sia.github.io/ 。

---

## 四、Dr. GRPO（Liu et al., 2503.20783）— 去偏形式

> **命名澄清：** 议程可选链 `2503.06639` 为 Mroueh 的 RLVR 动力学分析；**「Dr. GRPO / GRPO Done Right」** 出自 Sea AI Lab 等 *Understanding R1-Zero-Like Training*（**2503.20783**）。二者均讨论 GRPO，但贡献轴不同。

### 4.1 GRPO 目标中的两项偏置（§3.1）

文重写 GRPO（其式 3）并指出相对「无偏」优势 $\tilde A_{i,t}=R(q,o_i)-\mathrm{mean}(R)$，有效更新被 **std** 与 **\|o_i\|** 再加权（Fig. 4）：

| 偏置 | 来源 | 原文后果 |
|---|---|---|
| **Response-level length bias** | 目标里除以 $\lvert o_i\rvert$（sample-level 均值） | $A>0$（正确）→ 更偏短答；$A<0$（错误）→ **长错误答惩罚更弱** → 偏好拉长错误轨迹 |
| **Question-level difficulty bias** | 优势除以组内 $\mathrm{std}(R)$ | 过易/过难（std 小）的题在更新中 **权重更大**；文对比「batch 级归一」常见，**题级**归一造成难度偏置 |

文另指出：多种开源 PPO 实现也按 response length 做 `masked_mean`，与教科书 PPO 目标（其式 2，对 token 求和、**不**按 \|o\| 归一）不一致（Table 2 / Listing 1）。

文设 $\beta=0$（规则可验证奖励，可不贴 $\pi_{\mathrm{ref}}$；§3 开篇）——与 DAPO「去 KL」同向，但是 **独立论证来源**。

### 4.2 Dr. GRPO 定义（§3.2）

**做法（原文「simply remove」）：**

1. 去掉目标中的 $\lvert o_i\rvert$ 归一（改为用 **常数**如 generation budget / `MAX_TOKENS` 做 masked 归约，Listing 1 绿行）；
2. 去掉优势中的 $\mathrm{std}(\{R\})$ 归一，保留 **减组均值** 的 baseline。

文称：上述修改使估计回到 **Monte Carlo return + 无偏 baseline** 的 PPO 式目标（式 2），算法命名 **Dr. GRPO**（*Done Right*）。

**奖励（其实验最小规则）：** 含正确答案则 $R=1$，否则 $0$（与 DAPO 的 $\pm 1$ 不同，以各文为准）。

### 4.3 实证摘要（仅录原文主张，不外推）

- Fig. 5：相对 GRPO，Dr. GRPO **抑制错误回答长度持续变长**，token 效率更好；奖励仍可上升。
- 最小主义 R1-Zero 配方（摘要）：在 **Qwen2.5-Math-7B** + MATH L3–5 + Qwen-Math template 上用 Dr. GRPO，称 AIME 2024 **43.3%**（7B SOTA 口径，摘要句）。
- 附录消融（Fig. 8 叙述）：去 length 或去 std 均有益；**length 项对响应长度影响更大**。

代码入口（文内）：https://github.com/sail-sg/understand-r1-zero 。

---

## 五、可选理论对照：Mroueh 2503.06639（RLVR + GRPO 动力学）

**不并入「Dr. GRPO」节点。** 摘要级要点（据 Abstract / §1）：

- 在可验证 **二元** 奖励下，GRPO 的 **mean+variance（whitening）** 标定诱导一种 **对比损失**，负样本来自 **上一策略** 的合成 rollout。
- 分析变体轴：奖励归一（仅均值 vs 均值+方差）；正则（mirror 贴 $\pi_{n-1}$ / 贴固定 $\pi_{\mathrm{ref}}$ / 两者兼有）。
- 迭代策略的 **probability of success (PoS)** 服从简单递推，收敛到由参考 PoS 与正则强度决定的不动点，且 **不动点高于参考** → 文称 GRPO **放大**成功概率。

跟读价值：给「组内 whitening 为何像对比学习」一条解析路径；**不**替代 DAPO/Dr.GRPO 的工程改写清单。

---

## 六、算法谱系对照表（只立轴，不写 R1 阶段）

| 轴 | GRPO（DeepSeekMath） | DAPO | Dr. GRPO | 备注 |
|---|---|---|---|---|
| Critic / value | **无**；组均值作 baseline | 同左 | 同左（MC − mean） | 相对 PPO 的共同出发点 |
| 优势标准化 | $(R-\mathrm{mean})/\mathrm{std}$ | **保留** std | **去掉 std**，留 mean-center | Dr. 指 std → 难度偏置 |
| 序列长度归一 | $\frac{1}{\lvert o_i\rvert}$ sample-level | 改为 **token-level** $\propto 1/\sum\lvert o_i\rvert$（长答权重大） | 用 **常数预算** 归约，去 \|o\| 偏置 | DAPO 与 Dr. 对「长度」处方 **不同向**——以各文问题设定为准，禁强行统一 |
| Clip | 对称 $\varepsilon$ | **解耦** $\varepsilon_{\mathrm{low}},\varepsilon_{\mathrm{high}}$（Clip-Higher） | 沿用 PPO-clip 叙述；重点不在 clip | — |
| KL | 进目标，$\beta>0$（文内例 0.04） | **去掉** | 分析中常 $\beta=0$ | 与长 CoT / 规则奖励叙事一致 |
| 采样过滤 | 无（Algorithm 1 常规 batch） | **Dynamic Sampling** 滤掉全对/全错组 | 未作为主贡献 | — |
| 超长处理 | 未作 DAPO 级 shaping | Filtering + Soft Overlong Punishment | 讨论长度偏置与「越训越长」 | — |
| 奖励 | RM（+ 可 process） | 规则 $\pm 1$ | 规则 $0/1$ | R1 规则奖励细节见 [[DeepSeekR1推理训练深读]] |

**架构思想（辅）一句话：** 三者共享「**同题组 rollout → 相对优势 → 无 value**」；分歧在 **是否信任 std、如何聚合 token 损失、是否用 clip/采样/长度惩罚维持探索与稳定**。

---

## 七、与仓库已有笔记的边界

| 已有 | 本篇关系 |
|---|---|
| [[DeepSeekR1推理训练深读]] §三 GRPO 公式与 Zero/R1 超参 | **交叉引用即可**；**禁止**重画 R1 阶段表 / 奖励式 (4)(8–10) 管线 |
| `[[对齐脉络RLHF与偏好优化]]` RLHF / DPO / CAI | 上游对齐通史；本篇不重写偏好优化 |
| `[[推理时扩展TestTimeScaling]]` test-time scaling | 只交叉「R1 用 GRPO」一句；算法族细节以本篇为准 |

---

## 八、待核实 / 非本 PDF 范围

- DAPO 式 (8) 与式 (12) 在 中排版重叠严重；token-level 归约形式已按 §3.3 散文与「分母为总 token」理解书写——若需印刷级符号，建议对照 PDF 矢量公式再校一次。
- Dr. GRPO 摘要 43.3% AIME 与 Table/Fig 全表数字的逐格核对未在本篇展开。
- verl / OpenRLHF 等实现是否已默认切换 Dr.GRPO 或 DAPO 旗标：**本篇不跟代码默认值**（非论文正文承诺）。
- `2503.06639` 不动点定理的完整推导未抄入（可选深读）。

---

## 九、来源清单

1. Shao et al., 2024. *DeepSeekMath* — arXiv:**2402.03300**；本地 `https://arxiv.org/abs/2402.03300`。
2. Yu et al., 2025. *DAPO* — arXiv:**2503.14476**；本地 `https://arxiv.org/abs/2503.14476`；https://dapo-sia.github.io/ 。
3. Liu et al., 2025. *Understanding R1-Zero-Like Training*（**Dr. GRPO**）— arXiv:**2503.20783**；本地 `https://arxiv.org/abs/2503.20783`。
4. Mroueh, 2025. *RL with Verifiable Rewards: GRPO’s Effective Loss…* — arXiv:**2503.06639**；本地 `https://arxiv.org/abs/2503.06639`（可选动力学）。
5. 交叉：模型与技术报告/厂商报告/DeepSeekR1推理训练深读.md（阶段表权威源，本篇不复制）。

## 相关笔记

- [[GRPO与DAPO算法族|GRPO→DAPO]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[对齐脉络RLHF与偏好优化|对齐]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]

