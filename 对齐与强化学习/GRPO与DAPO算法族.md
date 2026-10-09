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
related: ["DeepSeekR1推理训练深读", "对齐脉络RLHF与偏好优化", "推理时扩展TestTimeScaling", "RL算力缩放与环境扩展", "AgenticRL景观与能力模块", "奖励黑客与涌现失对齐", "过程奖励模型PRM谱系", "MemoryR1强化学习记忆维护", "StepAudio2语音旗舰", "音视频联合Flamingo"]
archived: 2026-09-22
---

# GRPO → DAPO / Dr.GRPO 后训练算法族专线

> **主要来源**：[DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models](https://arxiv.org/abs/2402.03300)（简称 DeepSeekMath，v3）；[DAPO: An Open-Source LLM Reinforcement Learning System at Scale](https://arxiv.org/abs/2503.14476)（简称 DAPO，v2）；[Understanding R1-Zero-Like Training: A Critical Perspective](https://arxiv.org/abs/2503.20783)（简称 Dr. GRPO 论文，v2，COLM 2025）；[Reinforcement Learning with Verifiable Rewards: GRPO's Effective Loss, Dynamics, and Success Amplification](https://arxiv.org/abs/2503.06639)（简称 Mroueh，v4）（截至 2025-10-20）。
> **研究线**：数学原理（目标函数、优势估计与归一化偏差，主）· 架构思想（去掉价值网络后的训练系统形态，辅）
> **范围与相邻笔记**：
> - ≠ [[DeepSeekR1推理训练深读]]：本篇不写 R1-Zero → R1 的冷启动、拒绝采样与多阶段管线。
> - ≠ [[对齐脉络RLHF与偏好优化]]：本篇不写 RLHF、DPO、CAI 通史；PPO 进入语言模型对齐的背景见该篇。
> - ≠ [[推理时扩展TestTimeScaling]]：本篇不写推理期算力的缩放叙事。
> - ≠ [[RL算力缩放与环境扩展]]：本篇不写 RL 算力曲线与训练环境构建；ScaleRL 对本篇各设计选择（损失聚合、优势归一化、动态采样）的大规模消融见该篇。
>
> **意义**：GRPO 用同题一组采样的相对得分代替价值网络，使大规模可验证奖励 RL 在显存与工程上变得可行，成为 R1 以来推理与智能体 RL 的常用优化器；DAPO 与 Dr. GRPO 把它在长链推理上暴露的熵塌缩、零梯度、长度与难度偏差逐一定位并给出修正，让这条路线可以复现。

**一句话**：DeepSeekMath 用同题一组 rollout 的均值与标准差代替价值基线（GRPO）→ R1 族大规模采用 → DAPO 针对长链推理上的熵塌缩、零优势样本、样本级损失与截断噪声给出四项可复现改动 → Dr. GRPO 指出 GRPO 中按回复长度与组内标准差的归一化会引入偏差，并给出去偏形式；Mroueh 则在二元可验证奖励下分析了 GRPO 为何能放大成功概率。

---

## 一、问题背景

PPO 用学到的价值函数 $V_\psi$ 配合 GAE 估计优势。DeepSeekMath §4.1.1 指出它在大模型上的两个难处：价值网络通常与策略同量级，带来很大的显存与算力负担；而语言模型场景里奖励模型通常只给最后一个 token 打分，逐 token 的价值函数很难训准。

GRPO 的回答是不要价值网络：对同一个问题采样一组回答，用组内得分的相对高低充当基线。这一做法与奖励模型「同题比较」的训练形态一致，也天然适合答案可自动判对错的数学、代码任务。

问题出在规模化之后。DAPO 在 Qwen2.5-32B 上复现 R1-Zero 式训练时，朴素 GRPO 在 AIME 2024 只到 30 分，远低于 DeepSeek-R1-Zero-Qwen-32B 的 47 分；论文称朴素 GRPO 面临熵塌缩、奖励噪声与训练不稳（DAPO §1）。Dr. GRPO 论文则发现 GRPO 会人为拉长回答，尤其是错误回答（Dr. GRPO 论文摘要）。这两篇分别从工程与目标函数两侧修补 GRPO。

## 二、脉络

| 时间 | 节点 | 推进了什么 |
|---|---|---|
| 2017-07 | PPO | 裁剪重要性比率的近端策略优化，后成为 RLHF 的标准优化器 |
| 2022–2023 | RLHF 流水线 | 监督微调 → 奖励模型 → PPO（[[对齐脉络RLHF与偏好优化]]） |
| 2024-02 | GRPO（DeepSeekMath） | 去掉价值网络，组内相对优势；KL 从奖励移进目标 |
| 2025-01 | DeepSeek-R1 | GRPO 配规则奖励的大规模 RL 成为推理模型主路线（[[DeepSeekR1推理训练深读]]） |
| 2025-03 | Mroueh | 在二元可验证奖励下给出 GRPO 的有效损失与成功概率递推 |
| 2025-03 | DAPO | 解耦裁剪、动态采样、token 级损失、超长奖励整形四项改动，并开源系统与数据 |
| 2025-03 | Dr. GRPO | 指出长度偏差与难度偏差，去掉两项归一化 |
| 2025-10 起 | ScaleRL 等 | 在大算力下系统比较损失聚合、优势归一化、动态采样等选择（[[RL算力缩放与环境扩展]]） |

日期为 arXiv 首版日期。

## 三、GRPO：组相对优势（DeepSeekMath §4.1）

### 3.1 相对 PPO 改了什么

| | PPO | GRPO |
|---|---|---|
| 优势来源 | GAE + 学到的价值函数 $V_\psi$ | 同题一组回答的奖励相对量，无价值网络 |
| KL 放在哪 | 常把逐 token KL 加进奖励 | 直接加进目标，避免干扰优势估计 |
| 资源 | 策略、奖励模型、价值模型同量级 | 省去价值模型 |

### 3.2 目标与优势

对每个问题 $q$，从 $\pi_{\theta_{\mathrm{old}}}$ 采样一组回答 $\{o_i\}_{i=1}^{G}$，最大化：

$$
J_{\mathrm{GRPO}}(\theta)=\mathbb{E}\Bigg[\frac{1}{G}\sum_{i=1}^{G}\frac{1}{|o_i|}\sum_{t=1}^{|o_i|}\Big(\min\big(r_{i,t}\hat A_{i,t},\ \mathrm{clip}(r_{i,t},1-\varepsilon,1+\varepsilon)\hat A_{i,t}\big)-\beta\,D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})\Big)\Bigg]
$$

其中 $r_{i,t}=\pi_\theta(o_{i,t}\mid q,o_{i,<t})/\pi_{\theta_{\mathrm{old}}}(o_{i,t}\mid q,o_{i,<t})$。KL 用一个保证非负的无偏估计（DeepSeekMath 式 4）。

结果监督下，组内奖励减均值、除标准差，整条回答的所有 token 共享同一优势：

$$
\hat A_{i,t}=\frac{r_i-\mathrm{mean}(\mathbf r)}{\mathrm{std}(\mathbf r)}
$$

过程监督时，逐步奖励同样做组内归一化，token 的优势取其后各步归一化奖励之和（§4.1.3）。

### 3.3 原始设定

DeepSeekMath 的迭代 GRPO 每轮把参考策略更新为当前策略，并可持续训练奖励模型（含 10% 历史数据回放）。文内设定：策略学习率 1e-6，KL 系数 0.04，每题采样 64 条（§4.2）。要注意，DeepSeekMath 阶段仍主要用神经奖励模型；规则奖励配长链推理的大规模 RL 是 R1 之后的事。

## 四、DAPO：让 GRPO 在长链推理上稳定（DAPO §2–§4）

### 4.1 相对 GRPO 的两处取舍

- **去掉 KL 项**：长链推理训练中策略本就会显著偏离初始分布，论文认为 RLHF 式「贴住参考策略」没有必要（§2.3）。
- **规则结果奖励**：答案等价为 $+1$，否则 $-1$，以减少奖励模型被钻空子（§2.4）。

### 4.2 四项改动

| 改动 | 针对的现象 | 做法与直觉 |
|---|---|---|
| Clip-Higher（解耦裁剪） | 对称 $\varepsilon=0.2$ 时熵迅速下降，组内回答趋同 | 正优势时，旧概率 0.01 的 token 最多抬到 0.012，旧概率 0.9 的却能到 1.08，探索性 token 难以被抬高。于是只抬上界：$\varepsilon_{\mathrm{low}}=0.2$，$\varepsilon_{\mathrm{high}}=0.28$；下界不动，以免把概率压向 0 |
| Dynamic Sampling（动态采样） | 组内全对或全错时优势为 0、梯度为 0，且全对题的比例随训练上升 | 过采样并过滤准确率为 0 或 1 的题，凑满有效 batch 再更新；论文称这不一定降低训练效率，同步系统里生成时间主要由长尾样本决定，且用动态采样能更快达到同等表现（§3.2、Figure 6） |
| Token-Level Loss（token 级损失） | 样本级平均让长回答里每个 token 的权重被稀释，长样本中的重复与乱码难被惩罚 | 在组内全部 token 上取平均（分母为 $\sum_i\lvert o_i\rvert $），同一模式无论出现在长短回答里都被同等对待；对分数提升不大，但长度增长更健康、训练更稳 |
| Overlong Reward Shaping（超长奖励整形） | 截断样本一律惩罚，会误伤推理正确但过长的回答 | 先对截断样本屏蔽损失；再在最大长度前设缓冲区线性惩罚。设定为期望最大长度 16,384、缓冲 4,096，生成上限 20,480 token |

Clip-Higher 为什么能维持熵，可从熵变化的协方差机制得到解释，见 [[RLVR能力边界与熵机制]] 7.4 节。

### 4.3 渐进消融（Table 1，Qwen2.5-32B，AIME 2024 avg@32）

| 配置 | 分数 |
|---|---:|
| DeepSeek-R1-Zero-Qwen-32B（对照） | 47 |
| 朴素 GRPO | 30 |
| + Overlong Filtering | 36 |
| + Clip-Higher | 38 |
| + Soft Overlong Punishment | 41 |
| + Token-level Loss | 42 |
| + Dynamic Sampling（即 DAPO） | 50 |

论文称 DAPO 以 R1-Zero-Qwen-32B 约 50% 的训练步数超过后者（§4.2、Figure 1）。其他设定：AdamW，学习率 1e-6；prompt batch 512，每题 16 条回答，每个 rollout 步 16 次梯度更新（§4.1）。系统基于 verl，数据集 DAPO-Math-17K 把答案统一改写为整数以便判分（§3.5）。

## 五、Dr. GRPO：去掉两项归一化（Dr. GRPO 论文 §3）

### 5.1 两项偏差

相对 PPO 的标准目标，GRPO 多出两处归一化（§3.1、Figure 4）：

| 偏差 | 来源 | 后果 |
|---|---|---|
| 回答级长度偏差 | 目标里除以 $\lvert o_i\rvert $ | 正确回答（优势为正）越短更新越大，策略偏好短的正确答案；错误回答越长受罚越轻，策略偏好拉长错误答案 |
| 问题级难度偏差 | 优势除以组内 $\mathrm{std}$ | 太易或太难的题（奖励几乎全 1 或全 0，标准差小）在更新中权重更大；常见做法是在整个 batch 上归一化，按题归一化才造成偏差 |

论文还发现 trl、OpenRLHF、verl 等多个开源 PPO 实现的损失同样按回答长度取平均，带入了长度偏差（Table 2、Listing 1）。

### 5.2 做法与结果

做法是直接删去这两项：目标里用常数（如最大生成长度）代替 $|o_i|$，优势只减组均值、不除标准差。这样估计回到「蒙特卡洛收益 + 无偏基线」的 PPO 形式，论文称之为 *GRPO Done Right*（§3.2）。论文全程取 $\beta=0$，理由是规则验证器不存在奖励模型的分布漂移问题（§3 开头），与 DAPO 去 KL 同向但论证独立。实验奖励为答对 1、答错 0。

论文称 Dr. GRPO 抑制了错误回答长度的持续增长、提高了 token 效率，同时保持推理表现（Figure 5）；用它在 MATH 3–5 级题目上训练 Qwen2.5-Math-7B 的极简 R1-Zero 配方，AIME 2024 达到 43.3%（摘要、§1）。附录消融显示两项都有益，其中长度项对回答长度影响更大。

## 六、理论对照：GRPO 为何放大成功概率（Mroueh）

Mroueh 不是 Dr. GRPO，而是另一条理论线。在二元可验证奖励下，GRPO 的均值加方差归一化等价于一种对比损失，负样本来自上一轮策略的采样。论文分析了奖励归一化（只减均值或均值加方差）与 KL 正则（贴上一轮策略、贴固定参考策略或两者兼有）的组合，证明每轮最优策略有显式形式，迭代下的成功概率服从简单递推，收敛到一个由参考策略成功概率与正则强度决定的不动点，且该不动点高于参考值（摘要）。这给出了「组内归一化为何像对比学习」的解析解释，但不替代 DAPO 与 Dr. GRPO 的工程改动。

## 七、三者对照

| 轴 | GRPO | DAPO | Dr. GRPO |
|---|---|---|---|
| 价值网络 | 无，组均值作基线 | 同左 | 同左 |
| 优势标准化 | 减均值、除标准差 | 保留标准差 | 去掉标准差，只减均值 |
| 长度归一 | 样本级 $1/\lvert o_i\rvert $ | token 级 $1/\sum_i\lvert o_i\rvert $，长回答权重大 | 常数归一，去长度偏差 |
| 裁剪 | 对称 $\varepsilon$ | 解耦上下界 | 沿用 PPO 裁剪 |
| KL | 进目标，$\beta>0$（文内 0.04） | 去掉 | $\beta=0$ |
| 采样过滤 | 无 | 过滤全对、全错组 | 非主要贡献 |
| 奖励 | 奖励模型（可含过程奖励） | 规则 $\pm1$ | 规则 $0/1$ |

三者共享「同题组采样 → 相对优势 → 无价值网络」的骨架，分歧在是否信任标准差、怎样聚合 token 损失、用什么手段维持探索与稳定。DAPO 与 Dr. GRPO 对「长度」的处方方向不同，各自对应不同的问题设定，不宜强行统一。

## 八、意义

GRPO 让可验证奖励 RL 摆脱了价值网络的显存与训练难题，使 R1 式大规模推理 RL 能在开源社区复现；DAPO 把复现中缺失的关键细节补齐并公开系统与数据；Dr. GRPO 把「回答越训越长」中的一部分归因于目标函数本身而非能力提升。此后不少工具 RL、记忆 RL、奖励模型训练等工作直接用 GRPO 或 DAPO 作优化器，算法选择的大规模比较则转入 RL 算力缩放研究。

## 九、局限与待核实

- Dr. GRPO 论文摘要中的 43.3% 与正文各表的逐格对应未在本篇展开。
- verl、OpenRLHF 等框架当前是否默认采用 DAPO 或 Dr. GRPO 的设置，属于代码默认值而非论文结论，本篇未跟踪。
- Mroueh 不动点定理的条件与推导未展开，见原文。
- DAPO 与 Dr. GRPO 的结论都来自数学推理任务和 Qwen2.5 系基座；Dr. GRPO 论文本身也指出 Qwen2.5 基座在无模板时已有较强推理能力，可能存在预训练偏置，换基座或任务域时增益是否保持需另核。

## 十、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[DeepSeekR1推理训练深读]] | R1 是 GRPO 配规则奖励规模化的起点，本篇的 DAPO 与 Dr. GRPO 都以复现 R1-Zero 为出发点 | R1 阶段表与奖励设计 |
| [[对齐脉络RLHF与偏好优化]] | 上游：PPO 式 RLHF 是 GRPO 要简化的对象，该篇第 2.4 节把本篇列为 RLHF 之后的优化器分支 | RLHF、DPO、CAI 通史 |
| [[推理时扩展TestTimeScaling]] | 训练期用本篇算法做 RL，推理期再扩展思考长度，是两条并列的算力轴 | 推理时缩放叙事 |
| [[RL算力缩放与环境扩展]] | 下游：ScaleRL 把本篇的损失聚合、优势归一化、动态采样当作消融对象；零方差组被过滤正是环境需要难度自适应的动机之一 | 算力曲线与环境构建 |
| [[AgenticRL景观与能力模块]] | 本篇算法在 Agentic RL 中充当优化器，被搬到多步、部分可观测的长轨迹上 | 能力模块地图 |
| [[MemoryR1强化学习记忆维护]] | 下游实例：意义节所说「记忆 RL」的一例，那篇把本篇的 GRPO（与 PPO 并列）用作记忆管理器和答题智能体的优化器，目标函数不再重述 | 记忆操作、奖励设计与评测 |
| [[奖励黑客与涌现失对齐]] | DAPO 采用规则结果奖励的理由之一是减少奖励被钻空子，该篇把它列为防奖励黑客的设计选择 | 奖励黑客的手法与泛化 |
| [[过程奖励模型PRM谱系]] | GRPO 原文已支持过程监督的优势计算；逐步奖励从哪来见该篇 | PRM 数据与模型 |
| [[StepAudio2语音旗舰]] | 下游实例：Step-Audio 2 的强化学习先做两段 PPO（先用二元奖励控制思考长度，再改用奖励模型打分），最后一段用 GRPO 提升音频感知，是本篇算法用在端到端语音模型后训练上的一例 | 语音模型架构与评测 |
| [[音视频联合Flamingo]] | 下游实例：AV-Flamingo 的推理版先在带时间戳的音视推理链上做 SFT，再用 GRPO 训练，每题采样 5 个回答，奖励由格式、答案准确率与结构化字段重叠组成 | 音视频模型与训练数据 |

## 十一、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [DeepSeekMath](https://arxiv.org/abs/2402.03300) §4.1、Figure 4 | PPO 与 GRPO 的对照与动机 |
| 2 | [DAPO](https://arxiv.org/abs/2503.14476) §3、Table 1；[项目页](https://dapo-sia.github.io/) | 四项改动的现象图与渐进消融 |
| 3 | [Dr. GRPO 论文](https://arxiv.org/abs/2503.20783) §3、Listing 1；[sail-sg/understand-r1-zero](https://github.com/sail-sg/understand-r1-zero) | 两项偏差与开源实现中的长度偏差 |
| 4 | [Mroueh](https://arxiv.org/abs/2503.06639) | 成功概率放大的理论分析 |
| 5 | [PPO](https://arxiv.org/abs/1707.06347) | GRPO 所简化的原算法 |
| 6 | [[RL算力缩放与环境扩展]] | 这些设计选择在大算力下的比较 |
