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
related: ["对齐脉络RLHF与偏好优化", "SafeDPO与RePO", "合成对齐数据Magpie", "GRPO与DAPO算法族", "过程奖励模型PRM谱系"]
archived: 2026-09-22
---

# Preference optimization 新变体族：SimPO + ORPO（KTO 索引）

> **主要来源**：[SimPO: Simple Preference Optimization with a Reference-Free Reward](https://arxiv.org/abs/2405.14734)（Meng、Xia、Chen，简称 SimPO，v3，NeurIPS 2024）；[ORPO: Monolithic Preference Optimization without Reference Model](https://arxiv.org/abs/2403.07691)（Hong、Lee、Thorne，简称 ORPO，v2）；[KTO: Model Alignment as Prospect Theoretic Optimization](https://arxiv.org/abs/2402.01306)（Ethayarajh 等，简称 KTO，v5，ICML 2024，仅作索引）（截至 2026-09-08）。
> **研究线**：架构思想（隐式奖励的写法、是否需要参考模型、数据形态，主）· 评测字段（AlpacaEval、Arena-Hard、MT-Bench，辅）
> **范围与相邻笔记**：
> - ≠ [[对齐脉络RLHF与偏好优化]]：本篇不写 InstructGPT 三阶段、DPO 闭式推导与 CAI；DPO 是本篇所有方法的对照基线，其推导见该篇第 2.3 节与第 3.3 节。
> - ≠ [[GRPO与DAPO算法族]]：本篇不写在线组相对 RL 与可验证奖励。
> - ≠ [[过程奖励模型PRM谱系]]：本篇不写逐步过程奖励。
> - KTO 只写它在族谱中的位置与损失骨架，不展开实验。
>
> **意义**：DPO 之后，偏好优化沿三条轴继续简化：去掉参考模型、把监督微调与偏好对齐并成一步、改用不成对的好坏标签。ORPO、SimPO、KTO 各占一轴，其中 SimPO 用「与解码一致的长度归一化似然」作隐式奖励，以更少的显存在 AlpacaEval 2 与 Arena-Hard 上稳定超过 DPO，成为离线偏好优化的常用强基线。

**一句话**：ORPO 在监督微调损失上加一项几率比惩罚，单阶段完成对齐且不要参考模型；SimPO 把隐式奖励改成长度归一化的平均对数概率并加目标间隔，同样去掉参考模型；KTO 换数据形态，只用「好 / 坏」二元标签。

---

## 一、问题背景

经典 RLHF（奖励模型 + PPO）多阶段、采样昂贵、训练不稳；DPO 去掉了显式奖励模型与在线采样，但仍有两处代价（SimPO §1–§2.2）：

1. **要参考模型**：训练时始终要加载 $\pi_{\mathrm{ref}}$，增加显存与算力。
2. **训练与生成不一致**：DPO 的隐式奖励是 $\beta\log(\pi_\theta/\pi_{\mathrm{ref}})$，而推理时模型按自身的序列似然生成，不看参考模型。论文观察到 DPO 训完后，训练集上只有约 50% 的三元组满足「平均对数似然排序与奖励排序一致」（Figure 4b）。

另外两个观察推动了另外两条轴：
- ORPO 发现，只对被选回答做监督微调时，被拒回答的对数概率也会随之上升（ORPO §3、Figure 3，OPT-350M / HH-RLHF），说明监督微调缺少对「不想要的风格」的惩罚，可以在这一步就顺带做对齐。
- KTO 指出现实中更常见的是「这条回答好不好」的二元信号而不是成对偏好；只要损失有合适的归纳偏置，不成对数据也能达到 DPO 的水平（KTO 摘要、§1）。

## 二、脉络

| 时间 | 节点 | 推进了什么 |
|---|---|---|
| 2022-03 | InstructGPT | 监督微调 → 奖励模型 → PPO 三阶段 |
| 2023-05 | DPO | 把 KL 约束下的 RLHF 改写为偏好对上的分类损失，仍需参考模型（[[对齐脉络RLHF与偏好优化]]） |
| 2024-02 | KTO | 前景理论式效用，只需二元标签 |
| 2024-03 | ORPO | 几率比惩罚并入监督微调，单阶段、无参考模型 |
| 2024-05 | SimPO | 长度归一化平均对数概率作隐式奖励 + 目标间隔，无参考模型 |
| 2025 起 | SafeDPO、AMaPO、RePO 等 | 在 DPO 外壳上分别改安全约束、间隔设计与偏好语义（[[SafeDPO与RePO]]） |

日期为 arXiv 首版日期。

三条轴的对照：

| 轴 | DPO | ORPO | SimPO | KTO |
|---|---|---|---|---|
| 参考模型 | 要 | 不要 | 不要 | 要（损失中仍有 $\pi_{\mathrm{ref}}$ 与 KL 参考点） |
| 数据形态 | 成对 | 成对，与监督微调同一步使用 | 成对 | 不成对的好 / 坏标签 |
| 与监督微调的关系 | 通常先监督微调再偏好优化 | 合为一步 | 离线偏好优化，可从 SFT 或 Instruct 模型起步 | 论文称基座够好时可跳过监督微调 |

## 三、ORPO：单阶段的几率比惩罚（ORPO §4）

记长度为 $m$ 的回答的平均对数似然为 $\log P_\theta(y|x)=\frac1m\sum_t\log P_\theta(y_t\mid x,y_{<t})$，几率 $\mathrm{odds}_\theta(y|x)=P_\theta(y|x)/(1-P_\theta(y|x))$ 表示「生成 $y$」相对「不生成 $y$」的可能性倍数。目标为

$$
\mathcal L_{\mathrm{ORPO}}=\mathbb E\big[\mathcal L_{\mathrm{SFT}}+\lambda\,\mathcal L_{\mathrm{OR}}\big],\qquad
\mathcal L_{\mathrm{OR}}=-\log\sigma\Big(\log\frac{\mathrm{odds}_\theta(y_w|x)}{\mathrm{odds}_\theta(y_l|x)}\Big)
$$

$\mathcal L_{\mathrm{SFT}}$ 是对被选回答的标准负对数似然，$\lambda$ 控制偏好对比相对模仿的强度。梯度分析（§4.3）显示，当被选回答的几率已明显高于被拒回答时，惩罚项自动减弱。

**关键结果**：OPT 125M–1.3B 上对照 SFT、PPO、DPO（§5）；应用到 Phi-2（2.7B）、Llama-2（7B）、Mistral（7B），数据为 HH-RLHF 与 Binarized UltraFeedback（§6）。$\lambda$ 取值：Phi-2 为 0.25，Llama-2 为 0.2，Mistral-ORPO-α 为 0.1。AlpacaEval（Table 1）：

| 模型 | AlpacaEval 1.0 | AlpacaEval 2.0 |
|---|---:|---:|
| Phi-2 + ORPO | 71.80% | 6.35% |
| Llama-2 + ORPO（7B） | 81.26% | 9.44% |
| Mistral-ORPO-α（7B） | 87.92% | 11.33% |
| Mistral-ORPO-β（7B） | 91.41% | 12.20% |

论文另报 IFEval（指令级宽松口径）最高 66.19%，MT-Bench 7.23 / 7.32（α / β，§6.2 与结论）；称 Mistral-ORPO-α 与 β 仅在 UltraFeedback 上训练一个 epoch，就超过 Zephyr-β 与 Llama-2-Chat（13B）（AlpacaEval 2.0，Figure 1）。§6.3 的受控对照（ORPO 对 SFT、RLHF、DPO 的胜率）用的是论文自己的奖励模型与采样协议，不能与 AlpacaEval 榜单混读。代码与模型见 [xfactlab/orpo](https://github.com/xfactlab/orpo)。

## 四、SimPO：与生成一致的隐式奖励（SimPO §2–§4）

两处改动：

1. **隐式奖励改写**：用长度归一化的平均对数概率 $r_{\mathrm{SimPO}}(x,y)=\frac{\beta}{|y|}\log\pi_\theta(y|x)$ 代替 DPO 的对数比。它与生成时的似然度量一致，参考模型也随之消失。
2. **目标间隔 $\gamma>0$**：在 Bradley-Terry 模型里要求胜者奖励至少高出 $\gamma$：

$$
\mathcal L_{\mathrm{SimPO}}=-\mathbb E\log\sigma\Big(\frac{\beta}{|y_w|}\log\pi_\theta(y_w|x)-\frac{\beta}{|y_l|}\log\pi_\theta(y_l|x)-\gamma\Big)
$$

要点：长度归一化不可省，去掉 $1/|y|$ 会偏向更长但更差的回答（§2.2、§4.4）；目标里没有显式 KL 项，论文称靠小学习率、多样的偏好数据与大模型本身的抗遗忘性，对参考模型的 KL 经验上仍能保持较低（§2.3），这是经验主张而非定理。超参经验区间：$\beta$ 在 2.0–2.5，$\gamma$ 在 0.5–1.5（§3）。

**实验设定**：Base 设定从 UltraChat-200k 自训 SFT 起步，用 UltraFeedback 偏好数据；Instruct 设定从现成 Instruct 模型起步，用重新生成的偏好数据；共 Mistral 与 Llama-3 的 Base / Instruct 四组。评测为 AlpacaEval 2（805 题，报长度控制胜率 LC 与原始胜率 WR）、Arena-Hard（500 题）、MT-Bench（80 题）。

**关键结果**（Table 4，LC / WR / Arena-Hard，单位 %）：

| 设定 | DPO | SimPO |
|---|---|---|
| Mistral-Base | 15.1 / 12.5 / 10.4 | 21.5 / 20.8 / 16.6 |
| Mistral-Instruct | 26.8 / 24.9 / 16.3 | 32.1 / 34.8 / 21.0 |
| Llama-3-Base | 18.2 / 15.5 / 15.9 | 22.0 / 20.3 / 23.4 |
| Llama-3-Instruct | 40.3 / 37.9 / 32.6 | 44.7 / 40.5 / 33.8 |

摘要所称「相对 DPO 在 AlpacaEval 2 上最高 +6.4、Arena-Hard 上最高 +7.5」分别对应 Mistral-Base 的 LC（21.5 − 15.1）与 Llama-3-Base 的 Arena-Hard（23.4 − 15.9）。同表中 ORPO 与 KTO 也作为基线出现，例如 Mistral-Base 上 LC 分别为 14.7 与 13.1，Llama-3-Instruct 上为 28.5 与 33.1。

最强报告点是 Gemma-2-9B-it + SimPO（v3 新增，用 ArmoRM 标注偏好）：AlpacaEval 2 LC 72.4%（原模型 51.1%）、Arena-Hard 59.1%，论文称在 Chatbot Arena 10B 以下模型中用户投票排名第一（注明截至 2024-09-16，Table 1、摘要）。代码见 [princeton-nlp/SimPO](https://github.com/princeton-nlp/SimPO)。

## 五、KTO：只用二元标签（索引）

KTO（Kahneman–Tversky Optimization）用前景理论风格的价值函数，在「可取 / 不可取」二元标签上直接最大化生成的效用，而不是最大化成对偏好的对数似然。每个样本只需一个好坏信号，$n$ 条成对偏好可拆成 $2n$ 条 KTO 样本；论文称它在 1B–30B 规模上匹配或超过基于偏好的方法，标签极不平衡时也可用远少的正例，基座够好时可跳过监督微调（摘要、§1）。

损失骨架（§4.1）：以 $r_\theta=\log(\pi_\theta/\pi_{\mathrm{ref}})$ 为隐式奖励，以小批量估计的 $\mathrm{KL}(\pi_\theta\|\pi_{\mathrm{ref}})$ 为参考点 $z_0$，可取样本取 $\lambda_D\sigma(\beta(r_\theta-z_0))$、不可取样本取 $\lambda_U\sigma(\beta(z_0-r_\theta))$ 作为价值，损失为 $\lambda_y$ 减去价值的期望。KTO 还提出 HALO（人类感知损失）族，把 DPO 与离线 PPO 变体都归入其中；KTO 是该族里换了数据假设的一支，不属于「无参考模型」一支。

## 六、三者对照

| | ORPO | SimPO | KTO |
|---|---|---|---|
| 核心形式 | $\mathcal L_{\mathrm{SFT}}+\lambda\mathcal L_{\mathrm{OR}}$ | 长度归一 BT + $\gamma$ | 前景理论式效用，二元标签 |
| 参考模型 | 无 | 无 | 有 |
| 是否含监督微调项 | 有（主项） | 无 | 无（可跳过监督微调） |
| 代表数字 | Mistral-ORPO-β AE2 12.20%，MT-Bench 7.32 | Gemma-2-9B-it-SimPO AE2 LC 72.4%；四组设定相对 DPO 最高 +6.4 / +7.5 | 1B–30B 匹配或超过基于偏好的方法（含 DPO） |
| 适用直觉 | 还没有单独的偏好阶段，想在监督微调时顺带对齐 | 已有成对数据，想去掉参考模型并与解码度量一致 | 只有点赞 / 点踩，或正负样本严重不平衡 |

## 七、意义

三种方法都保留了 DPO「离线、无在线采样」的优点，又各自拿掉一项成本：ORPO 拿掉单独的对齐阶段，SimPO 拿掉参考模型并修正训练与生成的不一致，KTO 拿掉成对标注。SimPO 的结果说明，隐式奖励的写法本身就会显著影响偏好优化效果，长度归一化与目标间隔都是关键设计；它此后常被当作离线偏好优化的强基线，偏好数据研究（如 ActiveUltraFeedback）也把它作为下游消费算法之一。

## 八、局限与待核实

- **跨管线不可直接比**：ORPO 原文的旗舰分数与 SimPO Table 4 中的 ORPO 行来自不同数据、起点模型与超参搜索，不能据此判断谁更强；同管线下的相对排序以 SimPO Table 4 为准。
- **无 KL 的泛化**：SimPO 用经验因素代替显式 KL，在窄领域或小数据上是否仍稳定，论文没有作为定理给出。
- **ORPO 文内不一致**：MT-Bench 分数在 §6.2 与结论中为 7.23 / 7.32，§1 写作 7.24 / 7.32，本篇取 §6.2 的值；正文另有一处把被选回答 $y_w$ 误写为 disfavored，按式 (5)–(7) 与全文约定，$y_w$ 为被选、$y_l$ 为被拒。
- **KTO**：标签不平衡比、参考点 $z_0$ 的估计方式与同数据拆分实验未展开；v5（2026-09-08）与摘要所述结论一致。
- SimPO 的 Gemma-2 结果为 v3 新增，用的是更强的奖励模型标注，与四组主设定的数据口径不同。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[对齐脉络RLHF与偏好优化]] | 上游：DPO 是本篇所有方法的对照基线，其推导与 RLHF 背景是共用背景，在该篇；该篇也把 SimPO、ORPO、KTO 列为后续变体指向本篇 | RLHF、DPO、CAI 通史与推导 |
| [[SafeDPO与RePO]] | 同一 DPO 外壳上的其他改法：AMaPO 的自适应间隔接着 SimPO 的目标间隔轴走，RePO 以 KTO 为主要对照基线 | 安全约束变换、遗憾分解 |
| [[合成对齐数据Magpie]] | 上游数据：SimPO Base 设定所用的 UltraFeedback 与 ActiveUltraFeedback 的选对研究在该篇；ActiveUltraFeedback 把 SimPO 与 IPO 作为下游算法检验数据 | 数据合成与选对流水线 |
| [[GRPO与DAPO算法族]] | 对照：本篇是离线偏好目标，该篇是有验证器时的在线组相对 RL | GRPO、DAPO 配方 |
| [[过程奖励模型PRM谱系]] | 对照：本篇只用整条回答层面的偏好，逐步奖励见该篇 | PRM 数据与模型 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [SimPO](https://arxiv.org/abs/2405.14734) §2、Table 3–4、Figure 4 | 隐式奖励与生成度量的不一致；各目标公式对照；四组设定主表 |
| 2 | [ORPO](https://arxiv.org/abs/2403.07691) Figure 3、§4 | 监督微调抬高被拒回答；几率比目标与梯度 |
| 3 | [KTO](https://arxiv.org/abs/2402.01306) §3–§4 | HALO 定义与 KTO 损失 |
| 4 | [[对齐脉络RLHF与偏好优化]] 第 2.3 节 | DPO 的推导 |
| 5 | [[SafeDPO与RePO]] | DPO 外壳上的安全与遗憾改法 |
