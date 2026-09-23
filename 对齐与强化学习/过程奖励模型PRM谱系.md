---
title: "Process Reward Models（PRM）谱系：过程监督 → 自动标注 → 用于 TTS/RL"
topic: 过程奖励模型PRM谱系
date: 2026-09-22
lines: [数学原理, 架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2305.20050
 - https://arxiv.org/abs/2312.08935
 - https://arxiv.org/abs/2510.08049
arxiv: ["2305.20050", "2312.08935", "2510.08049"]
related: ["推理时扩展TestTimeScaling", "GRPO与DAPO算法族", "对齐脉络RLHF与偏好优化", "DeepSeekR1推理训练深读"]
archived: 2026-09-22
---

# Process Reward Models（PRM）谱系

> **定位**：[[过程奖励模型PRM谱系]] P0 横切——仓库缺「逐步奖励模型」独立笔记。本篇只立 **PRM 作为逐步奖励枢纽**：连接 **验证（rerank / Best-of-N）**、**test-time scaling**、**过程 RL（dense step reward）**。
> **攻坚线**：**数学原理（主）** + **架构思想（辅）**。
> **谱系三站**：人类过程监督（Lightman et al.）→ 自动过程标注（Math-Shepherd）→ 用法闭环（TTS / process RL；综述作地图）。
> **硬划界（禁止重写）**：
> - **禁止重写** DeepSeek-R1 **阶段表** / 规则奖励通史（→ [[DeepSeekR1推理训练深读]]）。
> - **禁止重写** [[GRPO与DAPO算法族]] **GRPO→DAPO 技巧清单** / 裁剪、动态采样等算法族配方（→ `[[GRPO与DAPO算法族]]-grpo-dapo-algorithm-family`）。
> - **禁止重写** [[推理时扩展TestTimeScaling]] TTS 通史与 o1/R1 产品叙事（→ `[[推理时扩展TestTimeScaling]]-test-time-scaling`）；本篇只补 **PRM 在 TTS 中的打分器角色**。
> - **禁止重写** [[对齐脉络RLHF与偏好优化]] 偏好优化 / ORM 作 preference RM 全文。
> **禁止编造**：数字、损失式、聚合规则一律锚定官方 PDF（2026-09-22 CST）；综述后延工作仅作索引，不外推未核数字。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文 A** | Lightman et al., *Let’s Verify Step by Step* | OpenAI CDN PDF（CreationDate **2023-06-01**）；arXiv **2305.20050**；`https://arxiv.org/abs/2305.20050`（**29** 页 letter；4,498,809 bytes） | 人类逐步标注 → **PRM800K**；MATH 上 PRM ≫ ORM（Best-of-N） |
| **主文 B** | Wang et al., *Math-Shepherd* | arXiv **2312.08935v3** \[cs.AI\] **19 Feb 2024**；`https://arxiv.org/abs/2312.08935`（**15** 页；827,225 bytes） | **无人工标注**的自动过程监督；**验证 + step-by-step PPO** |
| **可选地图** | Zheng et al., *A Survey of Process Reward Models* | arXiv **2510.08049v3** \[cs.CL\] **29 Apr 2026**；`https://arxiv.org/abs/2510.08049`（**17** 页 A4） | data → build → use（TTS / RL）全环综述；GitHub: `despzcm/Survey-of-Process-Reward-Model` |

**一句话抓手：** ORM 只看终答对错；PRM 给**每一步**打分，既可做 **Best-of-N / 搜索** 的验证器，又可做 **逐步 dense reward** 喂 RL——Lightman 用人类标注证明过程监督在难题上显著更强并放出 PRM800K；Math-Shepherd 用「从该步续写能否得到金标答案」自动造逐步标签，打通验证与过程 PPO；后续工作把这条枢纽接到更广的 TTS / 过程 RL 闭环（见综述地图，细节不展开算法族）。

---

## 二、问题立轴：ORM vs PRM（为何要「过程」）

### 2.1 定义对照（三文共识口径）

| | **ORM（Outcome Reward Model）** | **PRM（Process Reward Model）** |
|---|---|---|
| 监督粒度 | 整条解 / 最终答案 | **逐步**（step / 局部前缀） |
| 典型训练 | 用终答自动核对得到 $y_s\in\{0,1\}$，交叉熵（Math-Shepherd Eq.1；Lightman §2.5） | 逐步标签 $y_{s_i}$，逐步交叉熵（Math-Shepherd Eq.2；Lightman §2.6 单 token 分类） |
| 测试时用法 | 取**最终 token** 预测作解分数（Lightman §2.5） | 先得逐步正确概率，再**聚合**成解分数（见 §三.3 / §四.3） |
| 核心优势（论文主张） | 可全自动（有 checker 时）；便宜 | **精确定位错误**；信用分配更易；对齐上更直接奖励「人类认可的推理链」（Lightman §1、§6） |

**前作锚点（只点一句，不展开）：** Uesato et al. (2022) 在小学数学（GSM 域）上发现过程 vs 结果监督**最终表现相近**，但过程监督更省数据。Lightman §1 / §7.1 明确：自家差异在于 **更强基座（GPT-4）+ 更大量人工过程标签 + 更难的 MATH**。

### 2.2 本篇枢纽图（跟读）

`
过程数据（人标 / 自动 / 半自动）
 ↓
 训练 PRM（判别式逐步打分为主；综述另列生成式/隐式）
 ↓
 ┌────┴────┐
 │ │
验证/TTS 过程 RL
Best-of-N step reward → PPO 等
搜索/重排 （算法细节 → [[GRPO与DAPO算法族]]，本篇不抄）
`

综述 Figure 1 同构：**generate process data → train PRMs → use PRMs（TTS or RL）→ better data**。本篇只把枢纽钉死在 **Lightman + Math-Shepherd**；扩展索引见 §六。

---

## 三、站 1：人类过程监督 — *Let’s Verify Step by Step*（2305.20050）

### 3.1 实验边界（刻意不做的事）

Lightman **§2.1 Scope** 写得很硬：

- 固定一个 **generator** 产解；**不**用 RL 去改进 generator。
- 「outcome / process supervision」专指给 **reward model** 的监督，不是给 generator 的 RL 监督。
- 评测：**Best-of-N**——对每题从 generator 均匀采样多解，用 RM 选最高分，按**终答**自动打分，报正确率。

跟读：这篇是在证「**更可靠的逐步 RM**」，不是 R1 那种「用奖励把策略训成会想」的后训练通史。

### 3.2 数据：PRM800K

| 字段 | 论文事实 |
|---|---|
| 来源 | 大模型 generator 在 MATH 上的逐步解；人类逐步标注 |
| 标签 | 每步 **positive / negative / neutral**（界面 Figure 1） |
| 规模 | **800K** step-level labels；覆盖约 **75K** solutions、**12K** problems |
| 评测切分 | 为减过拟合，把 **4.5K** MATH test 题放进训练；正式评测只在剩余 **500** 题子集（后称 MATH500 同源子集） |
| 发布 | 全文放出 **PRM800K** |

**主动学习（active learning）：** 优先给人标「当前最佳 PRM 打分高、但终答错」的 **convincing wrong-answer** 解；迭代重训 PRM；小规模合成监督实验估计约 **2.6×** 数据效率（相对均匀采样；§4.2 / 贡献条 3）。

**只标到第一步错：** §2.6——错误解只监督到**第一个错误步**，使与 ORM 的信息对比公平（两者都揭示「至少有错」；PRM 额外给出位置）；也控制标注成本。

### 3.3 训练与解级聚合

- PRM：在每步**末 token** 预测正确性；标准 LM pipeline 训练；整解一次前向即可得逐步分（§2.6）。
- **解分数（主文默认）：** 各步正确概率的 **乘积**（「每步都正确」的联合概率）。
- Appendix F / Table 4：另试 min vs product、neutral 当正/当负；**最优为 product + neutral=positive → Best-of-1860 上 78.2%**；四种策略差距不大（77.4–78.2）。

### 3.4 大模型结果（MATH 500 子集）

| 方法 | Best-of-1860 % Solved（文内表） |
|---|---|
| Majority voting | **69.6** |
| ORM | **72.4** |
| **PRM** | **78.2** |

Figure 3：随 $N$ 增大，**PRM 与 ORM / majority 的差距拉大**——更适合「砸推理算力搜很多候选」的 TTS 设定。

ORM 基线刻意做强：每题 **100** 条均匀采样、训练集约比 PRM800K **大一个数量级**且无重叠；作者仍声明两训练集不可直接 apples-to-apples（§3）。

### 3.5 小规模合成监督：隔离混淆因素

用 **PRM_large** 当「合成标注员」训小 RM（§4）：在相同采样集上比三种监督——(i) 逐步监督；(ii) 把 PRM_large 压成 outcome；(iii) 纯终答核对。结论：**过程监督在所有数据规模上显著更好**；用 PRM_large 做 outcome 又优于纯终答（能惩罚「歪打正着」）。

### 3.6 OOD 与讨论要点（只录主张）

- Table 1（AP Calc/Chem/Physics、AMC10/12；Best-of-100）：Aggregate **PRM 72.9%** vs ORM 63.8% vs majority 61.3%。
- **Credit assignment（§6.1）：** 难题上多数解都有错，ORM 负标签边际信息低；PRM 标明「前几步对到哪 + 错在哪」。
- **Alignment（§6.2）：** 直接奖励人类认可的 CoT；作者称过程监督带来 **negative alignment tax**（更安全且更强）——**仅限数学域主张，作者自陈外推未知**。

---

## 四、站 2：自动标注 — *Math-Shepherd*（2312.08935）

### 4.1 动机

Lightman / Uesato 式 **人工逐步标注昂贵**，阻碍 PRM 实用化。Math-Shepherd 目标：**零人工逐步标注**造过程数据，并同时验证 **(1) 验证/rerank** 与 **(2) step-by-step PPO**。

### 4.2 自动过程标注：Completion + Estimation

**质量定义（§3.3.1）：** 受 MCTS 启发——一步的好坏 = **从该步出发推出正确终答的潜力**。

**流程（§3.3.2 / Figure 2）：**

1. **Completer**：从中间步 $s_i$ 续写 $N$ 条完整后续，得到答案集 $A=\{a_j\}_{j=1}^N$。
2. **Hard estimation (HE)：** 只要存在 $a_j=a^\*$（金标）则 $y_{s_i}=1$，否则 $0$（Eq.3）。
3. **Soft estimation (SE)：** $y_{s_i}=\frac{1}{N}\sum_j \mathbb{I}(a_j=a^\*)$（Eq.4）。
4. 用逐步交叉熵训 PRM（Eq.2）；文内主实验为方便用 **HE**（两特殊 token：`has potential` / `no potential`）。

**实现量级（§4 Parameter Setting）：** completer = **LLemma-7B**，$N=8$；约 **170k**（GSM8K）/ **270k**（MATH）解用于训 RM；generator/completer 在 MetaMath 上微调。

### 4.3 验证用法

- 解级聚合：**各步分数取 min**（§3.4：「Following Lightman…」——注意 Lightman 主文默认 **product**，Appendix 亦试 min；此处以 Math-Shepherd 明文为准）。
- 可与 self-consistency 结合：按终答分组，组内 RM 分加权再 argmax（Eq.5）。
- 评测：每题 **256** 候选；MATH 验证用与 Lightman 相同的 **MATH500**。

**Table 1 摘录（256 候选验证；RM 基座：GSM8K 用 LLaMA2-70B，MATH 用 LLemma-34B）：**

| Generator（均 MetaMATH 微调） | Verifier | GSM8K | MATH500 |
|---|---|---|---|
| DeepSeek-67B | Self-Consistency | 88.2 | 45.4 |
| | ORM | 92.6 | 45.3 |
| | **Math-Shepherd** | **93.3** | **47.0** |
| | SC + Math-Shepherd | 92.5 | **48.1** |

文内观察：难题 MATH 上 PRM 相对 ORM 优势更明显（呼应 Lightman）；若 RM 已很强，再叠 SC 可能伤 GSM8K（§4.1）。

### 4.4 过程 RL：step-by-step PPO

与「ORM-PPO 只在序列末给奖」对照：Math-Shepherd 的 PPO **在每步结束给奖**（§3.5）。

**Table 2（greedy；RM 为 Mistral-7B 训的 ORM / Shepherd）：**

| 模型 | GSM8K | MATH |
|---|---|---|
| Mistral-7B: MetaMATH | 77.9 | 28.6 |
| + ORM-PPO | 81.8 | 31.3 |
| **+ Math-Shepherd step-by-step PPO** | **84.1** | **33.0** |

**Table 3（RL + 验证互补；256 候选）：**
Mistral-7B + step-by-step PPO 后再用 **SC + Math-Shepherd** → **GSM8K 89.1 / MATH500 43.5**（即摘要「进一步到 89.1% / 43.5%」的出处）。
作者注：PPO 后「仅 RM、无 SC」有时不如 SC——猜想初始 RM 追不上变强后的策略，暗示 **迭代 RL** 潜力（留给未来）。

### 4.5 与 PRM800K 的对照（文内分析，§5.1）

在开放模型 + MetaMATH 分布上，作者称自动数据训的 PRM **优于** 直接用人类 PRM800K（归因：**分布差**——PRM800K 来自 GPT-4 解；以及自动数据 **量约为 PRM800K 的 4 倍**、可扩展）。此为 **Math-Shepherd 文内主张**，不是对 Lightman 主结果的否定。

---

## 五、枢纽：PRM 如何接入 TTS 与过程 RL

> 本节只钉 **接口角色**；TTS 通史 → [[推理时扩展TestTimeScaling]]；GRPO/DAPO 配方 → [[GRPO与DAPO算法族]]；R1 多阶段 → [[DeepSeekR1推理训练深读]]。**禁止把下列写成算法清单重写。**

### 5.1 Test-time scaling / 验证（对 [[推理时扩展TestTimeScaling]] 的补丁）

| 用法 | 论文锚点 | 枢纽含义 |
|---|---|---|
| **Best-of-N / rejection sampling** | Lightman 全文评测范式；Math-Shepherd §3.1 | PRM = 多候选上的 **逐步可靠排序器**；$N$ 越大相对 ORM/投票优势常更明显 |
| **解级分数聚合** | Lightman: **product**（主）；Math-Shepherd: **min** | 实现细节影响榜数，但两文都显示逐步信号可用 |
| **与 majority / SC 组合** | 两文均试；Math-Shepherd Eq.5 | 强 RM 时叠投票未必增益（任务依赖） |
| **搜索 / 剪枝（综述索引）** | Survey §4.1：beam annealing、Generate–Verify–Refine、MCTS 等 | PRM 从静态 reranker → **推理期控制器**；具体系统不在本篇展开 |

跟读一句：**[[推理时扩展TestTimeScaling]] 讲「多花推理算力」；本篇讲这算力砸在候选上时，谁来当逐步裁判——答案经常是 PRM。**

### 5.2 过程 RL（对 [[GRPO与DAPO算法族]] / R1 的补丁）

| 用法 | 论文锚点 | 枢纽含义 |
|---|---|---|
| **Dense step reward** | Math-Shepherd step-by-step PPO | 把稀疏终答奖换成逐步奖，改善信用分配 |
| **信号进目标的方式很关键** | Survey §4.2：求和易 reward hacking → 有工作改 **min-form** 等；另有 advantage 式 progress、熵正则等 | **有 PRM ≠ 会用 PRM**；进损失的形态影响稳定性 |
| **与规则奖励 / 组相对策略** | Survey 提及可与 **GRPO** 等结合（如 PROF 过滤过程–结果不一致样本） | **只交叉引用**：算法旋钮仍在 [[GRPO与DAPO算法族]]；R1 主叙事仍是可验证规则奖，不在此重画阶段表 |

跟读一句：**[[GRPO与DAPO算法族]] 管「怎么更新策略」；本篇管「逐步奖励从哪来、怎么进验证与 RL」。**

---

## 六、可选地图：综述 2510.08049（索引级）

> 仅作导航；后延工作名作索引，**不核其实验数字**。

| 环 | 综述分法 | 本篇已深读锚点 |
|---|---|---|
| **Data** | 人工（PRM800K）/ 自动（Math-Shepherd、OmegaPRM、FOVER…）/ 半自动·主动学习 | Lightman；Math-Shepherd |
| **Build** | Discriminative / Generative / Implicit / 其他架构 | 两主文均为 **判别式逐步打分** |
| **Use** | TTS（rerank → generative verify → search）+ PRM-guided RL | §五 |
| **应用** | 数学、代码、多模态、agent、高风险域等 | 本篇不扩写 |
| **开放挑战（Conclusion）** | 降标注成本且稳住自动监督；跨域泛化；接入 agent 规划/记忆；标准化评测 | 与 Lightman 污染/对齐税、Shepherd 噪声定义相呼应 |

---

## 七、跟读清单（可复述）

1. **ORM 看结局，PRM 看过程**——难题上逐步信用分配更关键（Lightman §6.1）。
2. **Lightman：** 人标 PRM800K + Best-of-N → MATH500 子集 **78.2%**（vs ORM 72.4 / vote 69.6）；主动学习约 **2.6×** 效率；**故意不训 generator RL**。
3. **聚合：** Lightman 主用 **product**；Math-Shepherd 验证用 **min**——读代码时别混。
4. **Math-Shepherd：** 用 completer 从该步续写，HE/SE 估「能否到金标」→ 无人工逐步标；同一 PRM 既做 **256-rerank** 又做 **step-by-step PPO**（Mistral：**77.9→84.1** GSM8K，**28.6→33.0** MATH；再验证到 **89.1 / 43.5**）。
5. **枢纽：** PRM = TTS 的逐步裁判 + 过程 RL 的 dense 奖励源；**不要**在本笔记重写 R1 阶段或 DAPO 技巧表。

---

## 八、未覆盖 / 待核实

| 项 | 状态 |
|---|---|
| Uesato et al. 2022 原文数字表 | 仅经 Lightman/Shepherd 转述；未落盘深读 |
| Lightman generator/ORM 具体 GPT-4 变体与 MathMix 构造细节 | Appendix A 未全文展开进本卡 |
| Math-Shepherd SE vs HE 完整消融曲线 | §5 有分析；本卡只录 HE 主实验设定 |
| 综述中 OmegaPRM / GenPRM / PURE min-form 等 | **仅索引**，数字待各自 PDF |
| 与 R1/GRPO 生产线的具体接线（是否用 PRM、何种聚合） | **各 TR 为准**；本篇不猜测 |

---

## 九、交叉引用

| 笔记 | 关系 |
|---|---|
| `[[推理时扩展TestTimeScaling]]-test-time-scaling` | TTS / Best-of-N 叙事；本篇补 **PRM 打分器** |
| `[[GRPO与DAPO算法族]]-grpo-dapo-algorithm-family` | 策略优化算法族；本篇 **不**抄技巧清单，只承认 PRM 可作奖励输入 |
| [[DeepSeekR1推理训练深读]] | 推理后训练阶段与规则奖；本篇 **不**重画阶段表 |
| `[[对齐脉络RLHF与偏好优化]]-alignment-rlhf-dpo` | 偏好/ORM 对齐主线；本篇是 **逐步过程 RM** 横切 |

## 相关笔记

- [[Gemma4技术报告深读|Gemma 4]]
- [[AXK2技术报告深读|AX-K2]]
- [[UIVenus2GUI智能体|UI-Venus-2]]
- [[宪法分类器防御|Constitutional Classifiers]]
- [[过程奖励模型PRM谱系|Process Reward Models]]

