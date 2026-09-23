---
title: "Preference optimization 新变体族：SimPO + ORPO（KTO 索引）"
topic: SimPO与ORPO偏好优化
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2405.14734
 - https://arxiv.org/abs/2403.07691
 - https://arxiv.org/abs/2402.01306
arxiv: ["2405.14734", "2403.07691", "2402.01306"]
related: ["对齐脉络RLHF与偏好优化", "GRPO与DAPO算法族", "过程奖励模型PRM谱系"]
archived: 2026-09-22
---

# Preference optimization 新变体族：SimPO + ORPO（KTO 索引）

> **定位**：[[SimPO与ORPO偏好优化]] P0 横切——补齐 [[对齐脉络RLHF与偏好优化]] 明确**不覆盖**的偏好变体短史：仓库缺 **无参考模型 / 单阶段 / 非成对标签** 三条轴上的可核条目。本篇主写 **SimPO**（长度归一平均 log 概率作隐式奖励 + 目标奖励间隔）与 **ORPO**（SFT NLL + odds ratio 单阶段 monolithic）；**KTO** 仅作谱系索引（二元 desirable/undesirable、HALO 族）。
> **攻坚线**：**架构思想（主）**——目标函数假设与数据形态；**评测字段（辅）**——AlpacaEval / Arena-Hard / MT-Bench 等文内表。
> **硬划界（禁止重写）**：
> - **≠ [[对齐脉络RLHF与偏好优化]]**：不重写 InstructGPT 三阶段 / DPO 闭式推导 / CAI；[[对齐脉络RLHF与偏好优化]] 已声明 IPO/KTO/ORPO 等不在精读范围。
> - **≠ [[GRPO与DAPO算法族]]**：不写 GRPO→DAPO / 可验证奖励 RL / Clip-Higher 等。
> - **≠ [[过程奖励模型PRM谱系]]**：不写 PRM 逐步监督 / Best-of-N 过程分。
> **禁止编造**：公式、超参区间、榜上数字一律取自官方 PDF（2026-09-22 CST）；KTO 只索引主张与损失骨架，不展开实验全表。

---

## 一、材料元信息与谱系抓手

| 代号 | 标题（封面） | arXiv / 页眉版本 | 官方 PDF | 页数 | 在谱系中的角色 |
|---|---|---|---|---:|---|
| **SimPO** | SimPO: Simple Preference Optimization with a Reference-Free Reward（Meng, Xia, Chen） | **2405.14734v3** \[cs.CL\] **1 Nov 2024**；NeurIPS 2024 | `https://arxiv.org/abs/2405.14734` | 32 | **主文 A**：平均 log 概率作隐式奖励；无 $\pi_{\mathrm{ref}}$；BT + 目标间隔 $\gamma$ |
| **ORPO** | ORPO: Monolithic Preference Optimization without Reference Model（Hong, Lee, Thorne；KAIST AI） | **2403.07691v2** \[cs.CL\] **14 Mar 2024** | `https://arxiv.org/abs/2403.07691` | 22 | **主文 B**：SFT NLL + odds ratio；单阶段、无参考模型、无单独偏好对齐相位 |
| **KTO（索引）** | KTO: Model Alignment as Prospect Theoretic Optimization（Ethayarajh et al.） | **2402.01306v5** \[cs.LG\] **8 Sep 2026**；ICML 2024（PMLR 235） | `https://arxiv.org/abs/2402.01306` | 21 | **谱系索引**：非成对二元信号；HALO；直接最大化 generation utility |

**一句话谱系：** DPO 用 $\pi_\theta/\pi_{\mathrm{ref}}$ 对数比作隐式奖励、仍要参考模型与成对偏好 → **ORPO** 把「弱惩罚拒绝 + 强适配接受」并进 **SFT 同一步**（odds ratio，无 ref、无第二阶段）→ **SimPO** 进一步把隐式奖励改成与**解码度量对齐**的长度归一平均 log 概率，并在 BT 里加目标间隔 $\gamma$ → **KTO** 换数据形态：只要「好/坏」二元标签（可把成对拆成 2n），用前景理论风格的 HALO 直接最大化效用（本篇不深读实验）。

**跟读枢纽（三条轴）：**

| 轴 | DPO（[[对齐脉络RLHF与偏好优化]] 已写） | ORPO | SimPO | KTO（索引） |
|---|---|---|---|---|
| 参考模型 $\pi_{\mathrm{ref}}$ | 要 | **不要** | **不要** | 要（损失里仍有 $\pi_{\mathrm{ref}}$ / KL 参考点） |
| 数据形态 | 成对 $y_w \succ y_l$ | 成对（但与 SFT **同一步**） | 成对 | **非成对**二元 desirable / undesirable |
| 相对 SFT 的阶段 | 常：SFT → 偏好优化 | **monolithic：偏好并进 SFT** | 离线偏好优化（可从 SFT / Instruct 起） | 可跳过 SFT（文称基座够好时） |

---

## 二、问题立轴：为何还要「新变体」

据 SimPO §1–§2.1 与 ORPO §1 / Figure 2：

1. **经典 RLHF**（RM + PPO）多阶段、采样与训不稳定——[[对齐脉络RLHF与偏好优化]] 已覆盖，此处不表。
2. **DPO** 消掉显式 RM，但仍：(a) 训练要 **参考模型**（显存/算力）；(b) 隐式奖励是 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，与推理时「无 ref、按序列似然生成」**不对齐**（SimPO §2.2：训好奖励排序 $\not\Rightarrow$ 平均 log-likelihood 排序）。
3. **ORPO 观察**：纯 SFT 只抬 chosen 的 NLL 时，**rejected 的 log-prob 也会跟着升**（ORPO Figure 3，OPT-350M / HH-RLHF）——缺对「不想要风格」的惩罚，故主张在 SFT 上挂一个 **odds ratio 弱惩罚**，省掉独立偏好相位。
4. **KTO 观察**（索引）：真实世界更常见的是「这条回复好不好」的二元信号，而非成对偏好；若损失有合适归纳偏置，**非成对**也可到 DPO 量级（KTO 摘要 / §1 要点）。

本篇只钉 **无 ref 成对线（ORPO / SimPO）** + **非成对索引（KTO）**；IPO 等仅在 SimPO 对照表里被点名，不单独立节。

---

## 三、站 1：ORPO — 单阶段 monolithic odds ratio（2403.07691）

### 3.1 架构意图（主）

ORPO Figure 2 / 摘要主张：

- **Reference-free**：训练不加载 $\pi_{\mathrm{ref}}$。
- **Monolithic**：不必「SFT 热身 → 再偏好对齐」两阶段；把对比项 **直接挂到 NLL** 上。
- 动机实验（§3，Figure 3）：只对 chosen 做 SFT 时，rejected 的 log-prob **同步上升**；需要显式压低不想要风格。

### 3.2 记号与 odds（§4.1，式 3–5）

长度 $m$ 的序列平均 log 似然（文中写作 $\log P_\theta(y|x)$）：

$$
\log P_\theta(y|x)=\frac{1}{m}\sum_{t=1}^{m}\log P_\theta(y_t\mid x,y_{<t})\qquad (3)
$$

Odds 与 odds ratio：

$$
\mathrm{odds}_\theta(y|x)=\frac{P_\theta(y|x)}{1-P_\theta(y|x)}\qquad (4)
\qquad
\mathrm{OR}_\theta(y_w,y_l)=\frac{\mathrm{odds}_\theta(y_w|x)}{\mathrm{odds}_\theta(y_l|x)}\qquad (5)
$$

直觉（文）：$\mathrm{odds}=k$ 表示「生成 $y$」相对「不生成 $y$」约 $k$ 倍可能；OR 刻画 chosen 相对 rejected 有多「更可能」。

### 3.3 目标（§4.2，式 6–7）

$$
\mathcal{L}_{\mathrm{ORPO}}=\mathbb{E}_{(x,y_w,y_l)}\big[\mathcal{L}_{\mathrm{SFT}}+\lambda\cdot\mathcal{L}_{\mathrm{OR}}\big]\qquad (6)
$$

其中 $\mathcal{L}_{\mathrm{SFT}}$ 为对 **chosen** 的标准因果 LM NLL；相对比项：

$$
\mathcal{L}_{\mathrm{OR}}=-\log\sigma\Big(\log\frac{\mathrm{odds}_\theta(y_w|x)}{\mathrm{odds}_\theta(y_l|x)}\Big)\qquad (7)
$$

**跟读：** $\lambda$ 控制「偏好对比」相对「模仿 chosen」的强度；梯度分析（§4.3 式 8–10）把 $\mathcal{L}_{\mathrm{OR}}$ 拆成惩罚项 $\delta(d)$ 与加权对比 $h(d)$——当 chosen 的 odds 已明显高于 rejected 时 $\delta\to 0$，惩罚自动减弱。

> 注：正文一处笔误把 $y_w$ 写成 “disfavored”；按式 (5)(7) 与全文 chosen/rejected 约定，**$y_w$=favored/chosen，$y_l$=rejected**。SimPO Table 3 对 ORPO 的改写用 $p_\theta=\exp(\frac{1}{|y|}\log\pi_\theta)$，与 ORPO 自用「平均 log 再还原为 $P$」记号同族，跟读以 ORPO 原文式 (3)–(7) 为准。

### 3.4 实验设置与评测字段（辅）

| 字段 | 文内 |
|---|---|
| 缩放对照 | OPT **125M→1.3B**：SFT / PPO / DPO / ORPO（§5.1） |
| 应用尺度 | Phi-2 **2.7B**、Llama-2 **7B**、Mistral **7B**（§6） |
| 数据 | Anthropic **HH-RLHF**；**Binarized UltraFeedback**（滤掉 $y_w=y_l$ 或空） |
| 公开检查点 | **Mistral-ORPO-α / β (7B)**；代码 `https://github.com/xfactlab/orpo` |
| $\lambda$ 举例 | Phi-2：$0.25$；Llama-2 (7B)：$0.2$；Mistral-α：文称 $\lambda=0.1$（§6.1） |

**AlpacaEval（Table 1，摘要数字与表一致）：**

| 模型 | AlpacaEval 1.0 | AlpacaEval 2.0 |
|---|---:|---:|
| Phi-2 + ORPO | 71.80% | 6.35% |
| Llama-2 + ORPO (7B) | 81.26% | 9.44% |
| Mistral-ORPO-α (7B) | 87.92% | **11.33%** |
| Mistral-ORPO-β (7B) | 91.41% | **12.20%** |

摘要另报：Mistral-ORPO 线 **IFEval** instruction-level loose 最高至 **66.19%**（Table 6）；MT-Bench **7.23 / 7.32**（α / β；Figure 4 / 摘要）。Figure 1 叙事：Mistral-ORPO-α&β 在 **单 epoch、仅 UltraFeedback** 设定下超过 Zephyr-β 与 Llama-2-Chat (13B)（以 AlpacaEval 2.0 为准）。

**受控对照（§6.3，Table 2–3）：** 在 HH-RLHF / UltraFeedback 上，同设定下 ORPO 对 SFT/RLHF/DPO 的 win rate 表——跟读时注意这是 **文内 RM / 采样协议** 下的相对胜率，不要与 AlpacaEval 官方榜混读。

---

## 四、站 2：SimPO — 参考无关 + 目标奖励间隔（2405.14734）

### 4.1 架构意图（主）

SimPO §2 两刀：

1. **隐式奖励改写**：不用 DPO 的 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，改用与生成度量一致的 **长度归一平均 log 概率** → **自然去掉 $\pi_{\mathrm{ref}}$**。
2. **BT 加目标间隔 $\gamma>0$**：迫使 $r(x,y_w)-r(x,y_l)\ge\gamma$，拉大 win/lose 间隔（类比分类 margin；IPO 也有间隔思想，但 SimPO 称完整目标不如己，§2.3 / §4.1）。

文内实证动机（§2.2）：DPO 训完后，训练集上仅约 **~50%** 的三元组满足「平均 log-likelihood 排序与奖励排序一致」（Figure 4b）。

### 4.2 从 DPO 背景到 SimPO 目标（§2.1–2.3）

DPO 隐式奖励与目标（式 1–2，仅作对照，推导见 [[对齐脉络RLHF与偏好优化]]）：

$$
r(x,y)=\beta\log\frac{\pi_\theta(y|x)}{\pi_{\mathrm{ref}}(y|x)}+\beta\log Z(x)
\qquad
\mathcal{L}_{\mathrm{DPO}}=-\mathbb{E}\log\sigma\Big(\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\mathrm{ref}}(y_w|x)}-\beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\mathrm{ref}}(y_l|x)}\Big)
$$

平均 log-likelihood 与 SimPO 奖励（式 3–4）：

$$
p_\theta(y|x)=\frac{1}{|y|}\log\pi_\theta(y|x)=\frac{1}{|y|}\sum_i\log\pi_\theta(y_i\mid x,y_{<i})\qquad (3)
$$

$$
r_{\mathrm{SimPO}}(x,y)=\frac{\beta}{|y|}\log\pi_\theta(y|x)\qquad (4)
$$

带间隔的 BT（式 5）→ SimPO 损失（式 6）：

$$
p(y_w\succ y_l|x)=\sigma\big(r(x,y_w)-r(x,y_l)-\gamma\big)\qquad (5)
$$

$$
\mathcal{L}_{\mathrm{SimPO}}(\pi_\theta)=-\mathbb{E}_{(x,y_w,y_l)\sim\mathcal{D}}\log\sigma\Big(
\frac{\beta}{|y_w|}\log\pi_\theta(y_w|x)
\frac{\beta}{|y_l|}\log\pi_\theta(y_l|x)
-\gamma
\Big)\qquad (6)
$$

**跟读抓手：**

- **必须长度归一**：去掉 $1/|y|$ 会偏向「更长但更差」（§2.2 / §4.4）。
- **无显式 KL 项**：文称靠小学习率 + 多样偏好数据 + LLM 抗遗忘，经验上对 ref 的 KL 仍可保持较低（§2.3 / §4.4）——这是经验主张，不是定理。
- 超参经验区间（§3）：**$\beta\in[2.0,2.5]$，$\gamma\in[0.5,1.5]$**（各设定需扫；附录 B）。

### 4.3 实验设定（§3）

| 设定 | 起点 | 偏好数据 |
|---|---|---|
| **Base** | 自训 SFT：Mistral-7B-v0.1 / Llama-3-8B ← **UltraChat-200k** | **UltraFeedback** |
| **Instruct** | 现成 Instruct（Llama-3-8B-Instruct / Mistral-7B-Instruct-v0.2 等） | 文内再生偏好（可用更强 RM；Gemma-2 用 ArmoRM，Appendix J） |
| 四宫格 | Llama-3-Base / Llama-3-Instruct / Mistral-Base / Mistral-Instruct | — |
| 最强报告点 | **Gemma-2-9B-it + SimPO**（Table 1） | 更强 RM 标注 |

对照方法（Table 3）：RRHF、SLiC-HF、DPO、IPO、CPO、**KTO**、**ORPO**、R-DPO 等——同表给出各目标的公式缩写，便于与 §三 / 索引节对照。

### 4.4 评测字段（辅）

评测协议（Table 2）：

| 基准 | #题 | 裁判 / 基线 | 指标 |
|---|---:|---|---|
| AlpacaEval 2 | 805 | GPT-4 Turbo vs GPT-4 Turbo | **LC** win rate + raw WR |
| Arena-Hard | 500 | GPT-4 Turbo vs GPT-4-0314 | WR |
| MT-Bench | 80 | GPT-4 / GPT-4-Preview-1106 | 1–10 均分 |

**四设定主表（Table 4，节选 SimPO vs DPO；LC/WR 为 %）：**

| 设定 | 方法 | AE2 LC | AE2 WR | Arena-Hard WR |
|---|---|---:|---:|---:|
| Mistral-Base | DPO | 15.1 | 12.5 | 10.4 |
| Mistral-Base | **SimPO** | **21.5** | **20.8** | **16.6** |
| Mistral-Instruct | DPO | 26.8 | 24.9 | 16.3 |
| Mistral-Instruct | **SimPO** | **32.1** | **34.8** | **21.0** |
| Llama-3-Base | DPO | 18.2 | 15.5 | 15.9 |
| Llama-3-Base | **SimPO** | **22.0** | **20.3** | **23.4** |
| Llama-3-Instruct | DPO | 40.3 | 37.9 | 32.6 |
| Llama-3-Instruct | **SimPO** | **44.7** | **40.5** | **33.8** |

摘要宣称相对 DPO：**AlpacaEval 2 最高 +6.4**（对上 Mistral-Base LC：21.5−15.1）、**Arena-Hard 最高 +7.5**（对上 Llama-3-Base：23.4−15.9）。同设定下 ORPO / KTO 亦列入 Table 4（例如 Mistral-Base：ORPO LC 14.7、KTO LC 13.1；Llama-3-Instruct：ORPO LC 28.5、KTO LC 33.1）——**同管线下的相对排序以 Table 4 为准**，勿与 ORPO 原文自家榜直接横比。

**Table 1 旗舰点（Gemma-2-9B-it 线）：**

| 模型 | AE2 LC | AE2 WR | 生成长度 |
|---|---:|---:|---:|
| Gemma-2-9B-it-SimPO | **72.4** | 65.9 | 1833 |
| Gemma-2-9B-it | 51.1 | 38.1 | 1571 |
| Llama-3-8B-Instruct-SimPO | 44.7 | 40.5 | 1825 |

摘要另报该 SimPO 检查点 **Arena-Hard WR 59.1%**，并称 Chatbot Arena **\<10B** 用户票排名第 1（文注「As of September 16th, 2024」）。代码：`https://github.com/princeton-nlp/SimPO`。

---

## 五、KTO 谱系索引（2402.01306）— 不展开精读

> **本节约束：** 只回答「它在族谱哪一格」；实验全表、HALO 证明细节 → 留给专篇或回读 PDF。[[对齐脉络RLHF与偏好优化]] 已把 KTO 列为「后续方法、不在精读范围」。

**一句话：** Kahneman–Tversky Optimization——用前景理论价值函数风格的 **HALO**，在 **二元 desirable / undesirable** 标签上直接最大化 generation utility，而不是最大化成对偏好的对数似然。

**数据形态（摘要 / §1）：** 每个 $(x,y)$ 只需「好/坏」信号；可把 $n$ 条 DPO 偏好拆成 $2n$ 条 KTO 样本。文称：极端不平衡下仍可用远少得多的 desirable 例逼近 DPO；基座够好时可 **跳过 SFT** 直上 KTO。

**损失骨架（§4.1，式 8；跟读级）：**

$$
\mathcal{L}_{\mathrm{KTO}}(\pi_\theta,\pi_{\mathrm{ref}})=\mathbb{E}_{x,y\sim\mathcal{D}}[\lambda_y-v(x,y)]
$$

其中 $r_\theta(x,y)=\log\frac{\pi_\theta(y|x)}{\pi_{\mathrm{ref}}(y|x)}$，参考点 $z_0=\mathrm{KL}(\pi_\theta(\cdot|x)\|\pi_{\mathrm{ref}}(\cdot|x))$（微批估计），

$$
v(x,y)=
\begin{cases}
\lambda_D\,\sigma\big(\beta(r_\theta(x,y)-z_0)\big) & y\sim y_{\mathrm{desirable}}|x \\
\lambda_U\,\sigma\big(\beta(z_0-r_\theta(x,y))\big) & y\sim y_{\mathrm{undesirable}}|x
\end{cases}
$$

**与本篇主线交汇：**

| | 相对 SimPO / ORPO |
|---|---|
| 参考模型 | **仍要** $\pi_{\mathrm{ref}}$（与 ORPO/SimPO「无 ref」相反） |
| 成对 vs 非成对 | **非成对**（本篇「数据形态」第三轴） |
| 在 SimPO Table 3/4 | 作为离线偏好基线之一出现；同管线下常低于 SimPO |

**族谱坐标（跟读一句）：** HALO 把 DPO /（离线）PPO-Clip 等收进「人类感知偏置」损失族（Def. 3.4、Thm 3.5）；KTO 是该族里换数据假设的一支，**不是**「无参考模型」支。

---

## 六、对照总表与选用直觉

| | **ORPO** | **SimPO** | **KTO（索引）** |
|---|---|---|---|
| 核心公式角色 | $\mathcal{L}_{\mathrm{SFT}}+\lambda\mathcal{L}_{\mathrm{OR}}$ | 长度归一 BT + $\gamma$ | HALO 效用 $v$；二元标签 |
| 参考模型 | 无 | 无 | 有 |
| 是否保留 SFT 项 | **有**（主项） | 无（纯偏好目标） | 无（可跳过 SFT 阶段） |
| 典型数据 | 成对偏好（与 SFT 同用 chosen） | 成对偏好 | 非成对好/坏 |
| 文内代表数字 | Mistral-ORPO-β AE2 **12.20%**；MT **7.32** | Gemma-2-9B-it-SimPO AE2 LC **72.4%**；四宫格相对 DPO 最高 +6.4 / +7.5 | 摘要：1B–30B 匹配或超过 DPO（细节不展开） |
| 工程直觉 | 「还没单独偏好阶段、想 SFT 时顺带对齐」 | 「已有成对数据、想去掉 ref、对齐解码度量」 | 「只有点赞/点踩或严重不均衡」 |

**刻意不写：** GRPO/DAPO 组相对优势与可验证奖励（→ [[GRPO与DAPO算法族]]）；PRM 逐步分（→ [[过程奖励模型PRM谱系]]）；DPO 闭式最优策略证明（→ [[对齐脉络RLHF与偏好优化]]）。

---

## 七、可核对出处清单

| 主张 | 出处 |
|---|---|
| SimPO 平均 log-prob 奖励 + $\gamma$；式 (4)(6) | 2405.14734 §2.2–2.3 |
| SimPO vs DPO AE2/Arena 最大增益 6.4 / 7.5；Gemma LC 72.4 / Arena 59.1 | 摘要；Table 1 / Table 4 |
| SimPO $\beta\in[2.0,2.5]$，$\gamma\in[0.5,1.5]$ | §3 |
| ORPO 式 (3)–(7)；SFT 抬高 rejected log-prob | 2403.07691 §3 Figure 3；§4 |
| Mistral-ORPO-α/β：AE2 11.33 / 12.20；MT 7.23 / 7.32；IFEval 至 66.19% | 摘要；Table 1；§6.2 |
| KTO 二元信号；$\mathcal{L}_{\mathrm{KTO}}$ 式 (8)；HALO；ICML 2024 | 2402.01306 摘要 / §1 / §4.1；页眉 PMLR 235 |
| [[对齐脉络RLHF与偏好优化]] 不覆盖 IPO/KTO/ORPO | 对齐与强化学习/对齐脉络RLHF与偏好优化.md 文末范围句 |

---

## 八、开放问题 / 跟读提示

1. **同榜不同管线：** ORPO 原文旗舰分与 SimPO Table 4 里的 ORPO 行不可直接当「谁更强」——数据再生、起点模型、超参扫描不同。
2. **无 KL 的泛化：** SimPO 用经验因素代替显式 KL；换窄域/小数据时是否仍稳，文未当作定理。
3. **KTO 专篇：** 若后续要深读不平衡比、$z_0$ 估计、与 DPO 同数据拆分实验，另开笔记；本篇保持索引厚度。
4. **与在线 RL 族：** PPO/GRPO 等采样—奖励环见 [[对齐脉络RLHF与偏好优化]] / [[GRPO与DAPO算法族]]；本篇只覆盖 **离线偏好目标变体**。

## 相关笔记

- [[推理时树搜索ABMCTS|AB-MCTS]]
- [[SimPO与ORPO偏好优化|SimPO / ORPO]]
- [[VendingBench经营长程评测|Vending-Bench]]

