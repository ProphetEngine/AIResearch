---
title: "MTP 训练范式：AdaMTP、MTP-D 与 OCC"
topic: MTP训练范式
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2608.00434
 - https://arxiv.org/abs/2603.23911
 - https://arxiv.org/abs/2605.28184
 - https://arxiv.org/abs/2509.18362
arxiv: ["2608.00434", "2603.23911", "2605.28184", "2509.18362"]
related: ["EntMTP熵引导投机解码", "EAGLE3投机解码", "投机解码原理与发展脉络", "推理引擎生态", "DeepSeekV3训练与MoE基建", "Nemotron3Ultra技术报告深读"]
github_occ: "https://github.com/MarkXCloud/RL-MTP"
github_fastmtp: "https://github.com/Tencent-BAC/FastMTP"
archived: 2026-09-22
---

# MTP 训练范式：AdaMTP、MTP-D 与 OCC

> **主要来源**：[AdaMTP: An Adaptive Training Paradigm for Multi-Token Prediction](https://arxiv.org/abs/2608.00434)；[Self-Distillation for Multi-Token Prediction](https://arxiv.org/abs/2603.23911)；[Joint Training of Multi-Token Prediction in Reinforcement Learning via Optimal Coefficient Calibration](https://arxiv.org/abs/2605.28184)；[FastMTP: Accelerating LLM Inference with Enhanced Multi-Token Prediction](https://arxiv.org/abs/2509.18362)（截至 2026-08-01）。四篇均只有 v1：AdaMTP（Cui 等，2026-08-01）、MTP-D（Zhao 等，腾讯，2026-03-25）、OCC（Wang 等，2026-05-27）、FastMTP（Cai 等，腾讯，2025-09-16）。下文用方法名简称。
> **研究线**：架构思想（主）——监督深度、蒸馏对象、RL 损失系数分别怎样改写 MTP 的训练目标；评测字段（辅）——任务均值、接受率、加速比、AIME avg@32。
> **范围与相邻笔记**：
> - ≠ [[EntMTP熵引导投机解码]]：本篇不写推理期按熵切换草稿树，只写 MTP 头与损失怎样训练。两篇都用到熵，但 AdaMTP 的熵用于切分训练数据与掩码损失，EntMTP 的熵用于在线换树。
> - ≠ [[EAGLE3投机解码]]：本篇不写 EAGLE-3 的训练期测试与多层特征融合，FastMTP 只提到兼容 EAGLE 式递归草稿。
> - ≠ [[投机解码原理与发展脉络]]：本篇不写投机解码的无损证明与方法族谱，「草稿—校验、与主模型同分布」只作接口；引擎选型见 [[推理引擎生态]]。
>
> **意义**：MTP（多 token 预测）原本是挂在主模型上的辅助头，训练时加一点监督，推理时当草稿用。三篇工作分别在 SFT、预训练和 RL 后训练三个阶段指出它的训练目标本身需要设计：固定预测深度会把噪声梯度传回骨干，MTP 头与主头的分布差会限制接受率，RL 中写死的损失系数会先帮后伤。它们让 MTP 从「顺带训一下的加速头」变成需要单独设计的训练目标。

**一句话**：AdaMTP 让辅助头不跨语义边界硬预测，MTP-D 让主头去教 MTP 头并可循环扩头，OCC 让 RL 中的 MTP 系数随梯度相关性在线变化，从而能把 MTP 梯度安全地传回主模型；FastMTP 作为补充，说明单个共享头要按推理时的递归方式来训。

---

## 一、问题背景

MTP 在共享骨干上为每个位置额外预测后面几个 token，可以增加训练信号，推理时又可作为自投机解码的草稿来源（草稿—校验流程与无损性见 [[投机解码原理与发展脉络]]）。三篇论文各自指出一个训练侧痛点：

1. **固定预测深度带来表示干扰**（AdaMTP §3）：语义块内的预测熵近似单调下降，跨块边界时熵突增。固定要求每个位置都预测满 $n$ 个 token，跨边界的监督就是噪声，梯度经共享骨干回传，标准 MTP 的任务均值常低于同设定下的普通下一 token 预测（NTP）。
2. **头间分布差与头数上限**（MTP-D §1）：MTP 头的接受率有限，多头连乘后的累积接受率呈指数下降；多头的交叉熵与主头互相拉扯，工业部署常只挂 1–4 个头。
3. **RL 中只能 detach**（OCC §1）：veRL、slime 等框架文档说明，把 MTP 梯度传回主模型容易严重掉分，默认 detach（切断梯度）；GLM-5、Composer-2、Nemotron-3 Super 等也隔离 MTP，或在 RL 后单独微调。

## 二、脉络

| 节点 | 做法 | 留下的问题 |
|---|---|---|
| Medusa（2024-01） | Medusa-1 冻结主模型（Medusa-2 联合训练），加多个并行解码头做树状草稿 | 草稿头后挂在已训好的主模型上，不随预训练一起学 |
| Gloeckle 等（2024-04） | 预训练时用多个输出头同时预测多个未来 token | 固定预测深度 |
| DeepSeek-V3（2024-12） | 级联 MTP 模块随预训练一起训，推理时可丢弃或改作草稿 | 头数少，损失系数按阶段写死 |
| FastMTP（2025-09） | 单个共享 MTP 头按递归推理方式自蒸馏微调 | 只在后处理阶段改头，不动主模型 |
| MTP-D（2026-03） | 主头向 MTP 头做梯度切断的自蒸馏，循环扩头 | 需要续训 |
| OCC（2026-05） | RL 中按梯度相关性在线校准 MTP 系数 | 依赖小步更新近似 |
| AdaMTP（2026-08） | 按熵分段，动态掩码 MTP 损失 | 阈值按数据集搜索 |

DeepSeek-V3 的 MTP 配置见 [[DeepSeekV3训练与MoE基建]]。

## 三、AdaMTP：按熵分段的自适应监督深度

- **熵分段**（§3.1）：用待微调的基座本身算每个位置的下一 token 熵，相邻位置的熵增超过阈值 $\tau$ 处切组；$\tau$ 按数据集搜索，使平均组长大致等于头数 $n$。
- **自适应深度**：组内 token 只预测到本组末尾，组末的边界 token 改为预测下一整组；第 $j$ 个辅助头只在 $j+1\le d_t$ 时计损失，总损失为 $L_{\mathrm{LM}}+\lambda L_{\mathrm{MTP}}$。
- **两阶段训练**（§3.2）：先冻结骨干与主头、只训辅助头作预热，再用 LoRA 联合训练骨干与各头。默认 $n=4$、$\lambda=0.1$；二阶段数据为 10k 条数学、代码、通用混合样本。
- **推理两种模式**（§3.3）：默认仍按固定深度出草稿、用 Medusa 式树校验，因此加速增益可归因于训练；另有按实时熵增提前停草稿的自适应模式，单样本收益有限，大 batch 下更省校验算力（Fig.4）。

**结果**（Table 1–2）：

| 骨干 | NTP 均值 | 标准 MTP 均值 | AdaMTP 均值 | GSM8K 加速（MTP → AdaMTP） |
|---|---:|---:|---:|---|
| Llama-3.1-8B | 36.32 | 35.90 | **36.85** | 1.65× → **2.12×** |
| Qwen-2.5-7B | 62.92 | 61.60 | **63.19** | — |
| Gemma-3-12B | 45.72 | 44.99 | **46.12** | 2.38× → **2.75×** |

Llama-3.1 的 HumanEval 加速为 1.86× → 2.01×（加速均相对 NTP 的 1.00×）。Qwen 系上所有微调方案都低于基座的 64.95，论文归因于微调语料的分布偏移，而非 MTP 本身。头数扫描（Llama，GSM8K）中，标准 MTP 随 $n$ 增大准确率近单调下降，AdaMTP 始终高于 NTP，$n=4$ 时最高（13.12）。

## 四、MTP-D：主头自蒸馏与循环扩头

- **设定**（§4）：沿用 DeepSeek-V3 的级联 MTP，在 2B 稠密模型与 10B 总参、1B 激活的 MoE 上，用 FineWeb-Edu 350B token 预训练，主实验用 256 张 H20。速度相对 1 头的 DeepSeek 式 MTP 计。
- **梯度切断的 TopN KL**（§3.2）：在原有 MTP 交叉熵之外，加一项让各 MTP 头逼近主头分布的 KL 损失，主头 logits 做 stop-gradient，蒸馏不会反过来拖累主头；只对主头概率最高的 $N=10{,}000$ 个 token 计算（词表约 122,880，全词表 KL 贵且长尾噪声大）。默认前向 KL；$\beta_k$ 单头取 1.0、四头取 0.5。消融（Table 2）：去掉梯度切断，主头均值掉约 1.49 分；$N$ 过小会伤接受率；$\beta_k=1.5$ 时主头损失上升。
- **循环扩头**（§3.3）：把已训好的 $m$ 个头的权重复制，作为下一组 $m$ 个头的初始化后续训，主模型与旧头冻结。不训练、直接循环从 1 头扩到 8 头时，普通 MTP 第 3 头在 AGIEval-en 上的累积接受率只剩 0.6%，MTP-D 仍有 26.70%。续训约 70B token 可扩到 8–16 个头。
- **结果**：2B 稠密、1 头时 AGIEval-en 接受率 85.75 → 88.98；4 头时第 4 头累积接受率 / 接受率 45.47 / 83.77 → 52.96 / 86.46（Table 1）。§4.2：4 头时第 4 头的累积接受率提高 7.5%，对应加速提高 22.9%；相对单头配置，4 头 MTP-D 加速约 107.4%（§4.2）。循环扩头后，相对 1 头最高 +220.4%（摘要），即附录 Table 8 中 4 头循环到 16 头的七项平均 3.204×；循环到 8 头为 3.052×。

## 五、OCC：RL 联合训练中的最优系数校准

**为什么会掉分**（§3.1–3.2）。在 $L$-光滑假设下，带系数 $\lambda$ 的 MTP 更新给每步改进带来的贡献为

$$
\Delta_{\mathrm{MTP}}=\eta\lambda(1-L\eta)\,c-\frac{L\eta^2\lambda^2}{2}\,v^2,\qquad c=\langle g_{\mathrm{RL}},g_{\mathrm{MTP}}\rangle,\ v^2=\lVert g_{\mathrm{MTP}}\rVert^2 .
$$

第一项是 RL 梯度与 MTP 梯度的相关性带来的收益，第二项是 MTP 梯度本身的扰动代价。三种常见做法对应三种结局：

| 做法 | 结局 |
|---|---|
| Detach | $g_{\mathrm{MTP}}$ 对主模型为零，$\Delta=0$，不帮也不伤 |
| MTP 用交叉熵损失 | 与按优势加权的 RL 方向期望相关性约为零，只剩负的二阶项，系统性掉分 |
| MTP 用与 RL 相同的策略损失、固定 $\lambda$ | 早期 $c$ 大，表现上升；后期 $c$ 衰减而 $v^2$ 仍在，先升后降 |

**校准**（§3.4）。闭式最优为 $\lambda^*\propto c/v^2$。小步更新下用 log-prob 变化 $\delta=\log\pi_\theta-\log\pi_{\mathrm{old}}$ 作代理，在线估计 $\hat c_t=\langle\delta_{\mathrm{RL}},\delta_{\mathrm{MTP}}\rangle$、$\hat v_t^2=\lVert\delta_{\mathrm{MTP}}\rVert^2$，取 $\lambda_t=\lambda_+\cdot\hat c_t/(\hat v_t^2+\epsilon)$（默认 $\lambda_+=1.0$、$\epsilon=10^{-8}$）。$\lambda_t$ 早期大，相关性衰减后趋近 0（§4.3）。每步耗时 8.07 秒，与 Detach 的 8.11 秒相当；直接算全模型梯度要 45.06 秒，约慢 5.6 倍（§4.3）。

**结果**（Table 1，avg@32，%）。训练用 DAPO-Math-17k、200 步、128 张 H20、veRL；基座为 MiMo-7B-RL（DAPO 与 GSPO 两种算法）与 GLM-4.5-Air（106B 总参、12B 激活）。

| 设定 | Detach | 交叉熵 | 策略损失 | OCC |
|---|---:|---:|---:|---:|
| MiMo + DAPO | 58.9 | 47.7 | 57.4 | **61.7** |
| MiMo + GSPO | 57.8 | 50.0 | 56.2 | **60.1** |
| GLM-4.5-Air + DAPO | 65.9 | 54.8 | 64.4 | **67.6** |

MiMo + DAPO 的 AIME24：Detach 45.3、交叉熵 16.1、策略损失 38.9、OCC 45.9；AIME25：Detach 36.7、OCC 46.7。固定 $\lambda\in\{0.1,0.2,0.5,1.0\}$ 的策略损失都不及 OCC（Table 2）。

## 六、FastMTP：按推理方式训练单个共享头

OCC 的相关工作点名了 FastMTP。这里只把它作为「训推对齐」的补充，不与前三篇并列为第四种范式。

- **做法**：沿用 DeepSeek-V3 式 MTP 结构，但只用一个共享权重的头递归预测 $K$ 步，省去多个模块的 KV 缓存与调度；冻结主模型，只微调不到 3% 的参数，用自蒸馏数据、按步数指数衰减的损失权重训练；草稿侧用语言感知的高频词表压缩，校验仍用全词表，因此无损。
- **结果**（Table 1，MiMo-7B-RL，七项基准平均）：相对 NTP 加速 2.03×；直接复用原 MTP 头只有 1.21×，论文称相对后者提高 82%；第 1 / 2 / 3 个草稿位的接受率由约 70% / 11% / 2% 提高到 81% / 56% / 36%。

## 七、三种范式对照

| 维度 | AdaMTP | MTP-D | OCC |
|---|---|---|---|
| 训练阶段 | 在预训练模型上用 SFT 加装 MTP | 预训练加续训扩头 | RLVR 后训练 |
| 核心旋钮 | 自适应监督深度 $d_t$ | TopN KL 与权重复制 | 在线系数 $\lambda_t$ |
| 针对的风险 | 跨边界的噪声交叉熵 | 头间分布差、主头被拖累 | 交叉熵的无关扰动、固定系数的先升后降 |
| 熵的作用 | 切分训练数据 | 不涉及 | 不涉及 |
| 与 EntMTP 的关系 | 都用熵，但这里是损失掩码，不是选树 | 提高接受率可服务投机，不调度树 | 联合 RL，不调度树 |

## 八、意义

- **训练目标需要单独设计**：三篇分别表明，固定深度、只用交叉熵、固定系数都不是 MTP 的默认安全选项，换成掩码、蒸馏或在线系数后，主任务和加速可以同时提高。
- **头数与接受率的上限被抬高**：MTP-D 把工业上常见的 1–4 头扩到 8–16 头，FastMTP 把后几个草稿位的接受率提高了数倍。
- **MTP 可以回到 RL 主循环**：OCC 给出不 detach 也不掉分、开销与 detach 相当的做法，为「RL 后再单独补训 MTP」提供了替代。

## 九、局限与待核实

- **结果难横向比较**：三篇的模型、阶段与指标都不同（SFT 任务均值、预训练接受率、RL 的 avg@32），只能各自看相对基线的变化。
- **AdaMTP**：阈值 $\tau$ 需按数据集搜索；Qwen 系上所有微调方案都低于基座，绝对水平受微调语料影响。
- **MTP-D**：「+220.4%」是摘要口径，任务级分解以附录 Table 8 为准，不宜换算成论文没有给出的 tokens/s。
- **OCC**：MiMo + GSPO 一行交叉熵均值印为 50.0，若与各题分数手算均值有出入，以 Table 1 印刷值为准；代理估计依赖小步更新假设。
- **代码**：AdaMTP 与 MTP-D 正文没有给出代码仓库。
- **FastMTP**：词表压缩细节与七项基准的 tokens/s 全表未展开。

## 十、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[EntMTP熵引导投机解码]] | 同一类 MTP 草稿头的两端：本篇改训练损失，那篇在推理期按熵在线切换草稿树、不改训练目标 | 拓扑库、路径价值选树与吞吐主表 |
| [[EAGLE3投机解码]] | FastMTP 兼容 EAGLE 式递归草稿；EAGLE-3 是独立草稿头路线，本篇的方法都让 MTP 头随主模型一起训练或对齐 | 训练期测试、多层特征融合与 SGLang 表 |
| [[投机解码原理与发展脉络]] | 那篇给出草稿—校验与同分布无损的投机解码基线，4.1、4.5 节写 MTP 模块当草稿的一面；本篇的接受率与加速比都在这一框架下计算 | 投机解码证明与方法族谱 |
| [[推理引擎生态]] | 引擎侧：MTP 草稿头在 vLLM、SGLang 等引擎中的接入与选型 | 引擎实现细节 |
| [[DeepSeekV3训练与MoE基建]] | MTP-D 与 FastMTP 都建立在那篇所写的 DeepSeek-V3 级联 MTP 结构上；V3 在预训练中按阶段手设 MTP 损失系数，OCC 讨论的则是 RL 阶段该系数怎样在线设定 | V3 的并行与 MoE 基建 |
| [[Nemotron3Ultra技术报告深读]] | 工业案例：那篇的模型预训练带 2 个共享权重 MTP 头，后训练在 RL 之后另设 MTP Boosting 阶段，与 OCC 所说「工业界隔离 MTP、事后单独训练」一致 | Nemotron 的混合架构与后训练全流程 |

## 十一、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [AdaMTP](https://arxiv.org/abs/2608.00434) §3 | 熵分段、自适应深度与两种推理模式 |
| 2 | [MTP-D](https://arxiv.org/abs/2603.23911) §3 | 梯度切断的 TopN KL 与循环扩头 |
| 3 | [OCC](https://arxiv.org/abs/2605.28184) §3 | 相关—扰动分解与在线系数 |
| 4 | [MarkXCloud/RL-MTP README](https://github.com/MarkXCloud/RL-MTP) | OCC 代码 |
| 5 | [FastMTP](https://arxiv.org/abs/2509.18362)、[Tencent-BAC/FastMTP README](https://github.com/Tencent-BAC/FastMTP) | 共享头递归训练与词表压缩 |
| 6 | [Better & Faster Large Language Models via Multi-token Prediction](https://arxiv.org/abs/2404.19737) | 预训练多 token 预测的起点 |
