---
title: "生成式奖励模型（GenRM）与奖励推理化"
topic: 生成式奖励模型GenRM与奖励推理化
date: 2026-09-25
lines: [架构思想, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2505.02387
 - https://arxiv.org/abs/2504.12328
 - https://arxiv.org/abs/2504.02495
arxiv: ["2505.02387", "2504.12328", "2504.02495"]
related: ["过程奖励模型PRM谱系", "对齐脉络RLHF与偏好优化", "GRPO与DAPO算法族"]
retrieval_cutoff: 2026-09-25
timezone: Asia/Shanghai (CST)
archived: 2026-09-28
---

# 生成式奖励模型（GenRM）与奖励推理化

> **定位**：把「打分器」从**标量黑箱**推进到**可生成的偏好判断**，再推进到**把奖励建模本身当成推理任务**（长链 rubric / principle + 可验证 RL）。本篇只立这条**奖励侧范式跃迁**；以 RM-R1 的 Chain-of-Rubrics 与 DeepSeek-GRM 的推理时扩展为一招锚点。
> **研究线**：**架构思想（主）** + **数学原理（辅）**。
> **三代抓手**：标量 RM → 生成式 critique / LLM-as-judge → **奖励即推理**（含推理时扩展）。
> **范围与相邻笔记**：
> - **≠ [[过程奖励模型PRM谱系]]**：不写逐步过程分、Best-of-N PRM、过程 PPO 通史；本篇打分对象是**整段回复 / 偏好对**，不是「逐步过程标签」。
> - **≠ [[对齐脉络RLHF与偏好优化]]**：不重写标量 RM + PPO / DPO 通史与损失族；只消费「偏好 → 奖励信号」入口。
> - **≠ [[GRPO与DAPO算法族]]**：两文均用 GRPO 作优化器，算法配方不在此展开。
> **安全范围**：不写具体越狱步骤、奖励 hacking payload、可复用攻击模板。

---

## 一、材料元信息

| 材料 | 标识 | 版本与链接 | 角色 |
|---|---|---|---|
| **主文** | Chen, Li, Wang et al., *RM-R1: Reward Modeling as Reasoning* | arXiv:**2505.02387v4** \[cs.CL\] **6 Mar 2026**；ICLR 2026；`https://arxiv.org/abs/2505.02387`；30 页 | 把奖励建模铸成推理任务；**Chain-of-Rubrics（CoR）** + 蒸馏 + RLVR → Reasoning Reward Models（ReasRMs）家族 RM-R1 |
| **辅·总览** | Zhong, Shen, Li et al., *A Comprehensive Survey of Reward Models* | arXiv:**2504.12328v1** \[cs.CL\] **12 Apr 2025**；`https://arxiv.org/abs/2504.12328`；38 页 | RM 分类地图：判别式 / **生成式** / 隐式；粒度上 ORM vs PRM（PRM → 另篇） |
| **辅·推理时扩展** | Liu, Wang, Xu et al. (DeepSeek-AI), *Inference-Time Scaling for Generalist Reward Modeling* | arXiv:**2504.02495v3** \[cs.CL\] **25 Sep 2025**；`https://arxiv.org/abs/2504.02495`；44 页 | **pointwise GRM** + **SPCT**；并行采样投票 / Meta RM，把更多推理算力砸进奖励 |

**开源（主）：** 文称代码与模型 `https://github.com/RM-R1-UIUC/RM-R1`。  
**开源（辅 GRM）：** 文称 Hugging Face / ModelScope 发布 DeepSeek-GRM。

**一句话抓手：** 标量 RM 只吐一个数；普通 GenRM 能写 critique 但仍常「浅想」；RM-R1 / DeepSeek-GRM 把**长推理链**（rubric 或自适应 principle）写进奖励过程，并用可验证对错做 RL——前者重**结构化跟读打分**，后者重**推理时把奖励算力砸大**。

---

## 二、三代对照：标量 → 生成式 critique → 奖励即推理

综述 §2.2.1 把参数化 RM 分成判别式、生成式、隐式；主文 §1 / Figure 2 再把「生成式里要不要长推理」单独抬高一档。跟读对照：

| | **标量 RM（ScalarRM）** | **生成式 critique（普通 GenRM / LLM-as-judge）** | **奖励即推理（ReasRM / GRM+扩展）** |
|---|---|---|---|
| 输出形态 | 分类头 → 标量 $r(x,y)$（综述 Fig.3a–b；主文 ScalarRM） | 保留 LM 解码头，生成自由文本判断 / Yes-No，可再抽 token 概率当分数（综述 Generative Reward；主文 GenRM） | 先生成**长且结构化**的推理（rubric / solution / principle+critique），再给出偏好或 pointwise 分（主文 ReasRM；GRM 文 SPCT） |
| 可解释性 | 黑箱分数；难解释「为何偏好」 | 有文字理由，但主文主张常**浅层、不可靠** | 理由与打分同链；可跟读 rubric / principle |
| 任务感知 | 通常一套头打全域 | 靠提示；细粒度题型差异弱 | **显式分流或自适应原则**（CoR 的 Chat vs Reasoning；SPCT 的自生成 principles） |
| 训练抓手 | BT / 交叉熵等偏好拟合 | 提示、拒绝采样、浅 CoT、SFT 判断 | **高质量推理链蒸馏 / RFT 冷启** + **可验证结果 RL**（主文 GRPO；GRM 文规则奖励 GRPO） |
| 推理时扩展 | 分数方差小，难靠多样本「想更多」变好（GRM 文 §2） | 可多数票，但对细粒度分差弱 | **加长推理链**（主文 Fig.4b）或 **并行多套 principle+critique 再投票 / Meta RM**（GRM 文 §4） |

**跟读：** 三代差的不是「能不能说话」，而是**奖励模型是否被训练成会为打分而推理**，以及推理算力能否在测试时继续换成更好的奖励信号。

---

## 三、RM-R1 一招：Chain-of-Rubrics（跟读机制）

### 3.1 问题立轴

主文问：*Can we cast reward modeling as a reasoning task?*  
动机：偏好判断要推断隐含标准、多准则权衡、模拟后果——需要与「赋分」同场的深度推理；仅标量或浅 critique 不够（§1、Fig.1）。

### 3.2 任务形式（白话）

偏好数据 $(x, y_a, y_b, l)$。生成式 RM $r_\theta$ 输出整段文本判断 $j$（含推理与最终选择 $\hat{l}$），目标是提高 $\hat{l}=l$ 的准确率（Eq.1–3）。不是再加一层标量头，而是**把「写判断」当成策略**。

### 3.3 训练两段（蒸馏 → RL）

1. **推理蒸馏**：从 instruct 基座出发，用 oracle（文中如 o3 / Claude-3.7）为子集样本合成结构化推理迹 $r^{(i)}$，拼上金标偏好得 $y_{\mathrm{trace}}$；最小化 NLL，把「会写奖励推理」灌进模型（§2.2、Eq.4–6）。文称蒸馏集约 **8.7K–9K** 量级。
2. **RLVR / GRPO**：把 $r_\theta(j\mid x,y_a,y_b)$ 当策略，相对蒸馏（或冷启）检查点加 KL；奖励**仅看最终偏好对不对**：$R=+1$（$\hat{l}=l$）否则 $-1$（Eq.7–8）。主文消融：**只做冷启 RL 不够**；蒸馏后再 RL 最强（Table 2、§4.1）。

已具备长推理蒸馏的基座（如 DeepSeek-R1-Distill 系）可**跳过蒸馏**、直接 RLVR（§1）。

### 3.4 一招：CoR 分流 rollout（Fig.3）

推理时系统提示强制先分类型，再走不同打分剧本：

| 类型 | 模型先做什么 | 再做什么 |
|---|---|---|
| **Reasoning**（数学 / 代码 / 多步推理） | 自己解出题，写入 `<solution>` | 对照己解，评两边正确性 / 完整性 / 推理质量 → `<eval>` → `<answer>[[A/B]]</answer>` |
| **Chat**（开放对话、风格、安全等） | **自拟**样本级评分量表 `<rubric>`（含权重与 `<justify>`） | 按量表对照两边 → `<eval>` → 同上最终答案 |

白话：**聊天题先写「这道题该按什么尺子量」；推理题先自己做一遍再当裁判。** 这就是相对「随便写一段 CoT 再选 A/B」的结构化升级。Ablation：rubrics + 题型分类（QC）抬升；再叠加蒸馏得 RM-R1 全配方（Table 2）。

### 3.5 证据口径（不堆榜）

主文报告：在 RewardBench / RM-Bench / RMB 平均上，14B–32B 级 RM-R1 可超过更大开源标量 RM 与 GPT-4o 等，平均最多约 **+4.9%**（摘要）；并强调相对旧式 critique（拒绝采样 + 非结构化 CoT）更接近或超过强 ScalarRM（§3.2）。规模上：更大基座从「推理训练」获益更多；加长推理 token 预算亦抬分（Fig.4）。细节分数表不在此复述。

---

## 四、DeepSeek-GRM 一招：原则自适应 + 推理时砸算力

### 4.1 选型：pointwise 生成式 RM

GRM 文论证：标量难多样本扩展；pairwise 不灵活吃「单条 / 多条」输入。**Pointwise GRM** 用纯语言对任意条回复写 critique，并可抽出各条分数，统一格式、利于并行扩展（§2、Fig.2）。

### 4.2 SPCT：把 principle 从「预处理」改成「生成的一部分」

**Self-Principled Critique Tuning（SPCT）**（§3、Fig.3）：

1. **Rejective FT（冷启）**：多次采样「principle → critique → pointwise 分」；丢掉判错轨迹，也丢掉「全对太易」的题；可选 **hinted sampling**（提示金标最佳项）补难例，但文观察到 hint 可能让 critique 走捷径 → 需要在线 RL。
2. **规则在线 RL（GRPO）**：rollout 自生成 principles + critiques；按能否正确挑出最佳回复给 $+1/-1$（Eq.11）；**不用 format 奖励**，靠更大 KL 稳住格式、抑偏。

跟读：原则不是外挂清单，而是**模型针对本题现写的打分宪法**；RL 同时塑造「写什么原则」与「如何据此 critique」。

### 4.3 推理时扩展：投票 / Meta RM

同一 query+回复上**并行采样** $k$ 套 principle–critique，对 pointwise 分**求和**得到更细粒度的最终奖励（Eq.14）；直觉：每条原则像一个评判视角，视角越多越接近真实偏好分布（§4）。另训 **meta RM**（pointwise 标量）识别哪些采样质量高，引导投票，进一步抬扩展曲线（Fig.1、Table 2 Voting@32 / MetaRM）。文主张：相对纯训时扩规模，**推理时扩展**在通用域奖励上可更划算。

**与 RM-R1 对照一句：** RM-R1 强调**单次结构化长链**（CoR）；DeepSeek-GRM 强调**多样本原则集合 + 投票**，把扩展旋钮拧在采样宽度上。

---

## 五、交叉（仅指针）

- 逐步过程标签、Best-of-N PRM、过程 RL → [[过程奖励模型PRM谱系]]（粒度不同：过程步 vs 整段偏好）。
- 标量 RM + PPO / DPO / CAI 通史 → [[对齐脉络RLHF与偏好优化]]（本篇只替换「奖励怎么产」这一环）。
- GRPO 裁剪 / 组相对基线等算法细节 → [[GRPO与DAPO算法族]]。

---

## 六、小结

| 问题 | 答复 |
|---|---|
| GenRM 相对标量 RM 多了什么？ | 用生成能力产出可检视的判断文本，而非单一分数头。 |
| 「奖励推理化」再多什么？ | 强制/训练出**长且任务感知**的推理（rubric 或 principle），并用可验证对错 RL 加固。 |
| RM-R1 记住哪一招？ | **CoR**：Chat 自拟量表；Reasoning 先自解再裁判；**蒸馏 + RL**，只 RL 不够。 |
| DeepSeek-GRM 记住哪一招？ | **SPCT** 自适应写原则；推理时 **多采样投票 / Meta RM** 把算力换成更细奖励。 |
| 本篇不写什么？ | PRM 逐步谱系、RLHF/DPO 通史、越狱与 reward hacking payload。 |

**文献对齐：** 三代分型锚定综述 §2.2.1 + 主文 §1/Fig.2；CoR / 蒸馏–RL / 消融锚定 RM-R1 §2–§4；SPCT / 投票 / Meta RM 锚定 DeepSeek-GRM §2–§4。未外推未核实验数字。
