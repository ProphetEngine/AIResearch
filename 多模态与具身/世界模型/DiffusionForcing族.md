---
title: "Diffusion Forcing 族：DF → Self Forcing（Causal Forcing 附录）"
topic: DiffusionForcing族
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2407.01392
 - https://arxiv.org/abs/2506.08009
 - https://arxiv.org/abs/2602.02214
arxiv: ["2407.01392", "2506.08009", "2602.02214"]
related: ["扩散语言模型", "视频生成模型脉络", "扩散生成式视觉与LLM", "世界模型与VJEPA", "MatrixGame与Cosmos", "BAGEL统一多模态生成"]
project_df: "https://boyuan.space/diffusion-forcing"
project_sf: "https://self-forcing.github.io/"
project_cf: "https://thu-ml.github.io/CausalForcing.github.io/"
github_cf: "https://github.com/thu-ml/Causal-Forcing"
archived: 2026-09-22
---

# Diffusion Forcing 族：DF → Self Forcing（Causal Forcing 附录）

> **主要来源**：[Diffusion Forcing: Next-token Prediction Meets Full-Sequence Diffusion](https://arxiv.org/abs/2407.01392)（Chen 等，MIT，NeurIPS 2024，v4 2024-12-10）；[Self Forcing: Bridging the Train-Test Gap in Autoregressive Video Diffusion](https://arxiv.org/abs/2506.08009)（Huang 等，Adobe / UT Austin，NeurIPS 2025，v2 2025-11-10）；[Causal Forcing: Autoregressive Diffusion Distillation Done Right for High-Quality Real-Time Interactive Video Generation](https://arxiv.org/abs/2602.02214)（Zhu、Zhao 等，清华 / 生数，ICML 2026，v5 2026-06-01）（截至 2026-09-29）。
> **研究线**：架构思想（主：各 forcing 训练时以什么为条件、训练与推理是否同分布）；评测字段（辅：迷宫规划累计奖励、VBench、吞吐与时延）
> **范围与相邻笔记**：
> - ≠ [[扩散语言模型]]：本篇不写 LLaDA、Dream 的离散掩码扩散，只写连续序列（视频、轨迹）上的高斯噪声级。
> - ≠ [[视频生成模型脉络]]：本篇不写视频生成全线与旗舰系统卡，只跟自回归与扩散杂交的 forcing 一族。
> - ≠ [[世界模型与VJEPA]]：那篇是表征空间里的非生成预测，本篇是像素或潜空间的生成。
>
> **意义**：整段扩散能被引导但只能定长生成，逐帧自回归能流式生成却会把自己的误差越滚越大。Diffusion Forcing 给序列里每个 token 独立的噪声级，把两者合成一个模型；Self Forcing 让模型训练时就基于自己生成的历史继续生成，消除训练与推理的分布差，在单张 H100 上做到 17 FPS、亚秒级时延的流式视频；Causal Forcing 再指出蒸馏时必须用自回归教师。三篇合起来，是今天实时交互视频与世界模型（如 Matrix-Game 3.0）所用蒸馏管线的方法来源。

---

## 一、问题背景

序列生成有两条路。逐 token 预测配 Teacher Forcing（训练时条件是真实前缀）长度可变、能流式输出，但难以按整段目标做引导，连续数据滚出训练长度后容易发散；整段扩散能联合建模并用引导，但是非因果、定长。Diffusion Forcing 的观察是：加噪相当于部分掩码，零噪声等于不掩、满噪声等于全掩，所以可以让每个 token 各取一个噪声级（DF §1、§3）。

到了自回归视频扩散，又出现暴露偏差：训练时的条件是干净真实帧（Teacher Forcing）或各帧独立加噪的帧（Diffusion Forcing），推理时却是模型自己生成的帧，误差逐帧累积。CausVid 用 DF 训练再接 DMD 分布匹配蒸馏，但训练时生成的分布仍不是推理分布（SF §2）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2022-05 | [Diffuser](https://arxiv.org/abs/2205.09991) | 用整段轨迹扩散做规划，靠引导满足目标 |
| 2023-11 | [DMD](https://arxiv.org/abs/2311.18828) | 分布匹配蒸馏，把多步扩散压成一步生成器 |
| 2024-07 | Diffusion Forcing | 每 token 独立噪声级加因果网络，统一逐 token 预测与整段扩散 |
| 2024-12 | [CausVid](https://arxiv.org/abs/2412.07772) | 把双向视频扩散模型蒸馏成少步自回归生成器 |
| 2025-03 | [Wan](https://arxiv.org/abs/2503.20314) | 开源视频生成基座，Wan2.1-T2V-1.3B 是 SF 与 CF 的初始化 |
| 2025-06 | Self Forcing | 训练期自回归展开，用整段视频的分布匹配损失 |
| 2026-02 | Causal Forcing | 指出双向教师破坏帧级单射，改用自回归教师做 ODE 初始化 |
| 2026-04 | Matrix-Game 3.0 | 交互世界模型借 DMD 与 Self Forcing 的思路做多段少步蒸馏（[[MatrixGame与Cosmos]]） |

## 三、方法

### 3.1 Diffusion Forcing（DF §3）

- **训练**：对轨迹的每个时刻独立采样噪声级，因果网络（RNN 或因果 Transformer）共享参数同时去噪各 token。定理 3.1 说明这一过程优化的是所有噪声级组合下序列似然的重加权 ELBO。
- **采样**：用一张噪声日程表规定每步每 token 的目标噪声级。同一模型不重训即可切换用法：让近处先去噪、远处保持高噪声；对已生成的帧加一点小噪声后再作条件，使长序列滚动保持稳定；把未来 token 的奖励梯度回传给过去，做长程引导（Monte Carlo Guidance）。

### 3.2 Self Forcing（SF §3）

- **训练期展开**：每帧以自己已生成的干净前缀为条件去噪，训练也用 KV 缓存，不需要特殊掩码。
- **控制代价**：用少步扩散骨干；每条序列只对随机抽中的一个去噪步开梯度，过去帧的 KV 截断梯度。
- **整段分布匹配**：损失可选 DMD（主结果）、SiD 或 GAN，匹配的是整段生成视频与真实视频的分布。
- **滚动 KV**：只保留最近若干帧的 KV，支持超出训练长度的流式生成。

作者强调 SF 的首要目标是消除暴露偏差，不是单纯为加速而蒸馏。

### 3.3 Causal Forcing（CF §3）

SF 与 CausVid 的蒸馏都是「双向教师 → ODE 蒸馏初始化少步自回归学生 → DMD」。CF 论证 DMD 阶段补不了双向到因果的架构差，问题出在 ODE 初始化：自回归学生要求帧级单射，即固定一个噪声帧，教师的概率流 ODE 只映到唯一的干净帧；双向教师去噪时看得到未来，同一噪声帧可对应多个干净帧，学生只能学到条件期望式的模糊解。CF 的做法是先用 Teacher Forcing 训一个多步自回归教师，再从它做因果 ODE 蒸馏，最后接与 SF 相同的 DMD。作者也比较了训练自回归教师的两种方式，Teacher Forcing 优于 Diffusion Forcing（CF Table 2）。

## 四、结果

| 工作 | 设定 | 结果 |
|---|---|---|
| DF | D4RL Maze2D 单任务平均累计奖励（Table 1） | 141.7，Diffuser 为 119.5 |
| DF | Minecraft、DMLab 视频滚动（§4.1） | 远超训练长度（如 1000 帧）仍稳定，Teacher Forcing 与整段扩散基线很快发散 |
| DF | 真实机器人换位任务（§4） | 成功率 80%，遮挡关键状态后 76% |
| SF | 单张 H100，Wan2.1-1.3B 底座，按块生成（Table 1） | 17.0 FPS、时延 0.69 秒，VBench 总分 84.31；双向 Wan2.1 为 0.78 FPS、103 秒、84.26 |
| SF | 训练成本（§4） | DMD 版本在 64 张 H100 上约 1.5 小时收敛 |
| CF | 同口径（Table 1） | 吞吐与时延与 SF 相同；相对 SF，Dynamic Degree 高 19.3%、VisionReward 高 8.7%、指令遵循高 16.7% |

## 五、意义

DF 把「噪声级」变成可逐 token 控制的软掩码，让一个模型同时具备流式生成与引导能力；SF 表明自回归视频扩散的主要短板是训练与推理不同分布，在训练里模拟推理即可在保持质量的同时实时生成；CF 补上蒸馏管线的理论条件。从世界模型角度看，这一族解决的是「边交互边生成、长时间不崩」的底层问题，交互式世界模型的少步蒸馏直接建立在它之上。

## 六、局限与待核实

- **作者自述**：SF 与 CF 默认只在约 5 秒的注意力窗口上训练，直接外推更长视频仍有训练与推理差距（CF §5）；CF 的 Causal CD 变体仍是基础一致性蒸馏，弱于分数蒸馏；DF 自陈时序预测不是主要应用。
- **同一模型跨论文分数不同**：CF 重新评测时，SF 的 VBench 总分为 83.74、Wan2.1 为 83.37，与 SF 原文自报的 84.31、84.26 不同，两篇的数字不能混用。
- **DF 的规划对比有前提**：Diffuser 需要手写 PD 控制器、忽略其生成的动作才能运行；直接执行 Diffuser 生成的动作时会大幅失败（DF Table 1 图注；该列的具体分数未核到，本篇不列）。
- **SF 相对 Wan2.1 的「约 150 倍」时延加速**是正文叙述（§4），由 103 秒对 0.69 秒得出，属于不同生成方式的对比。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[扩散语言模型]] | 对照：那篇的 block diffusion 与自回归初始化是文本侧的自回归—扩散混合，本篇是连续序列侧 | 离散掩码扩散、文本评测 |
| [[视频生成模型脉络]] | 定位：那篇脉络的 2024-07、2025-06、2026-02 三个节点在本篇展开，是其流式生成一支的方法来源 | 视频生成通史与系统卡 |
| [[扩散生成式视觉与LLM]] | 上游：去噪、引导与 DiT 骨干的来历在那篇 | 图像潜扩散史 |
| [[世界模型与VJEPA]] | 对照：同被称为世界模型，那篇在表征空间做非生成预测，本篇在像素或潜空间生成 | JEPA 目标与探针评测 |
| [[MatrixGame与Cosmos]] | 下游：Matrix-Game 3.0 的多段少步蒸馏借鉴 DMD 与 Self Forcing，并以 Causal Forcing 的理论为由让教师与学生同用双向架构 | 记忆检索与部署加速 |
| [[BAGEL统一多模态生成]] | 下游：BAGEL 交错生成多张图时按 Diffusion Forcing 给各图独立噪声级 | 统一模型架构与评测 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Diffusion Forcing](https://arxiv.org/abs/2407.01392) §3–4 | 训练与采样、定理 3.1、视频与规划实验 |
| 2 | [Self Forcing](https://arxiv.org/abs/2506.08009) Figure 1–2、§3、Table 1–2 | 三种 forcing 的对照、训练期展开、消融 |
| 3 | [Causal Forcing](https://arxiv.org/abs/2602.02214) §3、Figure 3 | 帧级单射与三阶段管线 |
| 4 | [[MatrixGame与Cosmos]] | 这一族在交互世界模型中的落地 |
