---
date: 2026-10-08
status: archived
archived: 2026-10-08
topic: MoE路由与负载均衡
title: "MoE路由与负载均衡"
lines: [架构思想, AI Infra]
sources:
  - https://arxiv.org/abs/2006.16668
  - https://arxiv.org/abs/2101.03961
  - https://arxiv.org/abs/2202.08906
  - https://arxiv.org/abs/2401.06066
  - https://arxiv.org/abs/2408.15664
  - https://arxiv.org/abs/2202.01169
  - https://arxiv.org/abs/1701.06538
  - https://arxiv.org/abs/2202.09368
  - https://arxiv.org/abs/2501.11873
  - https://arxiv.org/abs/2409.02060
  - https://arxiv.org/abs/2412.19437
related: ["混合专家架构", "DeepSeekV3训练与MoE基建", "NVSHMEM与DeepEP通信", "MegaScaleInfer与UltraEP", "KimiK2技术报告深读", "KimiK3技术报告", "DeepSeekV4技术报告深读", "Nemotron3Ultra技术报告深读", "Qwen3技术报告深读", "规模定律与预训练范式", "分布式训练并行策略"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# MoE路由与负载均衡

> **主要来源**：[GShard: Scaling Giant Models with Conditional Computation and Automatic Sharding](https://arxiv.org/abs/2006.16668)；[Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity](https://arxiv.org/abs/2101.03961)；[ST-MoE: Designing Stable and Transferable Sparse Expert Models](https://arxiv.org/abs/2202.08906)；[DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models](https://arxiv.org/abs/2401.06066)；[Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts](https://arxiv.org/abs/2408.15664)；[Unified Scaling Laws for Routed Language Models](https://arxiv.org/abs/2202.01169)（截至 2026-10-08）。其余来源见第九节。
> **研究线**：架构思想（路由器怎样选专家、怎样保持均衡与特化）· AI Infra（容量、丢 token 与跨设备通信对路由设计的约束）
> **范围与相邻笔记**：
> - ≠ [[混合专家架构]]：本篇不重写 Switch → Mixtral → DeepSeek-V3 的史线与总参/激活参的基本概念，只在其上展开路由与均衡机制。
> - ≠ [[DeepSeekV3训练与MoE基建]]：本篇不列 V3 的 MoE 超参与训练调度，只把无辅助损失均衡作为机制讲清。
> - ≠ [[NVSHMEM与DeepEP通信]]：本篇不写 dispatch/combine 的通信内核实现。
> - ≠ [[MegaScaleInfer与UltraEP]]：本篇不写推理服务中的专家复制与在线负载调度。
> - ≠ [[KimiK3技术报告]] / [[Nemotron3Ultra技术报告深读]]：本篇不写 Quantile Balancing 与 LatentMoE 的产品级细节，只作演进节点引用。
> **意义**：路由与均衡决定 MoE 的名义总参有多少能变成有效容量，也决定专家并行的通信与负载；当代开放权重旗舰普遍采用细粒度 MoE，前提就是这套路由技术成熟。

**一句话**：MoE 的路由器要为每个 token 做一次离散选择——送给哪几个专家、各占多少权重。这个选择必须同时满足三件事：专家负载大致均衡（否则热点专家拖慢整体、冷门专家学不到东西），专家各有所长（否则总参再大也只是冗余），以及跨设备的通信可控。路由技术的十年演进，就是在这三者之间换取舍：从带噪 top-k 加辅助损失、容量因子与丢 token，到细粒度与共享专家、无辅助损失偏置和全局批均衡。

## 一、问题背景：离散选择带来的三个矛盾

1. **均衡与质量的矛盾**。路由器天然会「强者愈强」：被选中多的专家训练得更快，于是更容易被选中。Shazeer 等在 2017 年就描述了这种自我强化的失衡（Sparsely-Gated MoE 论文 §4）。要打破它就得施加均衡约束，但约束本身会干扰主任务的梯度。
2. **特化与冗余的矛盾**。理想的专家应掌握互不重叠的知识；但若每个 token 只能选很少几个大专家，每个专家被迫覆盖多种知识，彼此高度重叠（DeepSeekMoE 摘要）。
3. **动态与静态的矛盾**。路由结果每步都在变，而加速器偏好固定形状的计算，跨设备通信也偏好可预测的流量。早期做法是给每个专家设固定容量，溢出就丢弃，这就把系统约束写进了模型行为。

这些矛盾在稠密模型里不存在，所以 MoE 的大部分工程难度都集中在路由与均衡上。

## 二、发展脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2017-01 | [Sparsely-Gated MoE](https://arxiv.org/abs/1701.06538) | 带噪 top-k 门控；以重要性与负载两类辅助损失对抗自我强化的失衡 |
| 2020-06 | [GShard](https://arxiv.org/abs/2006.16668) | top-2 门控、专家容量、分组本地派发、可微辅助损失，以及按权重概率随机丢弃第二专家 |
| 2021-01 | [Switch Transformers](https://arxiv.org/abs/2101.03961) | 简化为 top-1；容量因子与溢出 token 走残差旁路；辅助损失 $\alpha N\sum_i f_iP_i$ |
| 2021-03 / 06 | [BASE Layers](https://arxiv.org/abs/2103.16716)、[Hash Layers](https://arxiv.org/abs/2106.04426) | 不学路由也能均衡：线性分配求解完全均衡，或按 token 哈希固定分配 |
| 2022-02 | [Expert Choice](https://arxiv.org/abs/2202.09368) | 反过来让专家挑 token，每个专家桶大小固定、天然均衡 |
| 2022-02 | [ST-MoE](https://arxiv.org/abs/2202.08906)、[Unified Scaling Laws](https://arxiv.org/abs/2202.01169) | router z-loss 稳定训练；把参数量与计算量作为两条独立的缩放轴 |
| 2022-11 | [MegaBlocks](https://arxiv.org/abs/2211.15841) | 用块稀疏算子实现不丢 token（dropless）训练 |
| 2024-01 | [DeepSeekMoE](https://arxiv.org/abs/2401.06066)、[Mixtral](https://arxiv.org/abs/2401.04088) | 细粒度切分与共享专家隔离；Mixtral 的路由分析发现专家选择更贴近句法而非主题 |
| 2024-08 | [Loss-Free Balancing](https://arxiv.org/abs/2408.15664) | 在选择前给路由分数加专家偏置并按负载调节，不引入干扰梯度 |
| 2024-09 | [OLMoE](https://arxiv.org/abs/2409.02060) | 全开放的 MoE 消融：不丢 token 的 token 选择优于专家选择；共享专家在其设置下无益 |
| 2024-12 | [DeepSeek-V3](https://arxiv.org/abs/2412.19437) | 671B 规模上以无辅助损失均衡为主、极小序列级损失为辅，训练与推理均不丢 token |
| 2025-01 | [Global-batch LBL](https://arxiv.org/abs/2501.11873) | 在全局批而非微批上计算均衡损失，显著改善领域特化；Qwen3 采用 |
| 2025-07 | [Kimi K2](https://arxiv.org/abs/2507.20534)、[Efficiency Leverage](https://arxiv.org/abs/2507.17702) | 稀疏度（总专家/激活专家）作为缩放变量：K2 取 48；以激活比例与粒度预测 MoE 相对稠密模型的算力优势 |

近一年的产品级演进：DeepSeek-V4 把亲和分改为 Sqrt(Softplus)、去掉目标节点数约束并在前 3 层改用按 token ID 的哈希路由（[[DeepSeekV4技术报告深读]]）；Kimi K3 以 Quantile Balancing 做无辅助损失路由，稀疏度约 56（[[KimiK3技术报告]]）。

## 三、核心机制

### 3.1 路由器：打分、选择、加权

一次路由可拆成三步：

1. **打分**：路由器是一个线性层，给出 token 与每个专家的亲和分。经典做法是 softmax；DeepSeek-V3 改用 sigmoid 后再对选中专家归一化（[[混合专家架构]] 2.3 节）。sigmoid 让各专家的分数互不竞争，便于后续加偏置而不改变门控权重。
2. **选择**：取分数最高的 $k$ 个专家（top-k）。2017 年的门控在 top-k 前加可调高斯噪声，帮助探索与均衡（Sparsely-Gated MoE 论文 §2.1）。
3. **加权**：被选中专家的输出按门控值加权求和，门控值让路由器能通过主任务梯度学习。

$k$ 是质量、计算与通信的折中：Switch 取 1 以降低路由开销与通信，GShard、Mixtral 取 2，细粒度 MoE 通常取 8 或更多。

**谁挑谁**。上述「token 挑专家」之外，还有两类变体：

| 方式 | 做法 | 优点 | 代价 |
|---|---|---|---|
| token 选择（top-k） | 每个 token 选 $k$ 个专家 | 每 token 计算量固定，符合因果 | 负载不均，需要均衡机制 |
| 专家选择（Expert Choice） | 每个专家从批中挑分数最高的若干 token | 桶大小固定、天然均衡，token 可得到可变数量的专家（Expert Choice 论文摘要） | 选择依赖同批中的未来 token，违反语言模型的因果约束，造成信息泄漏（Loss-Free Balancing 论文 §5.2） |
| 固定分配（Hash、BASE） | 按 token ID 哈希，或解线性分配问题 | 无需路由参数或辅助损失 | 分配与内容的关联弱（Hash），或需全局求解（BASE） |

自回归语言模型因此基本回到 token 选择，均衡问题交给损失或偏置解决；OLMoE 的消融也发现不丢 token 的 token 选择优于专家选择（OLMoE 论文 §1）。哈希路由并未消失，DeepSeek-V4 在前 3 层重新采用了它（见 [[DeepSeekV4技术报告深读]]）。

### 3.2 容量因子与丢 token

- **容量**：为了让每个专家的计算形状固定，GShard 与 Switch 给每个专家设上限：容量 = 批内 token 数 / 专家数 × 容量因子。溢出的 token 在该层不经专家计算，直接经残差连接传到下一层（GShard §2.2；Switch 的公式见 [[混合专家架构]] 2.1 节）。
- **取舍**：容量因子大，丢得少但空槽多、浪费算力与通信；容量因子小，计算紧凑但丢得多，被丢的 token 等于少走了一层。论文中的 FLOPs 数字若伴随大量丢 token，实际有效计算并不对齐。
- **不丢 token**：MegaBlocks 指出，固定容量逼使用户在丢 token 与填充浪费之间二选一；它把 MoE 计算改写为块稀疏运算，从而永不丢 token（MegaBlocks 论文摘要）。DeepSeek-V3 也称因均衡有效，训练与推理均不丢 token。当代大模型普遍以「不丢 token + 强均衡」替代「固定容量 + 丢弃」。

### 3.3 负载均衡：从辅助损失到偏置

**辅助损失**。Switch 的均衡损失为 $\alpha N\sum_i f_iP_i$，$f_i$ 是实际分到专家 $i$ 的 token 比例，$P_i$ 是路由概率分给专家 $i$ 的平均值；两者都均匀时取最小。它可微、简单，但有两个问题：

1. **干扰梯度**：系数大了会把主任务梯度拉偏，系数小了又压不住失衡；Loss-Free Balancing 的作者称辅助损失控制法在均衡与性能之间存在两难，未必有完美折中（Loss-Free Balancing 论文摘要、§2.2）。
2. **统计粒度**：框架通常在微批内计算 $f_i$ 再跨并行组平均，而大模型的微批只含很少几条序列，相当于要求每条序列内部都均匀路由——连代码序列也被迫分给所有专家，抑制了特化。改在全局批上同步 $f_i$ 后，预训练困惑度与下游任务都有提升，专家的领域特化也明显增强（Global-batch LBL 论文摘要）。Qwen3 的 MoE 采用了这一做法（Qwen3 技术报告 §2）。

**稳定性**。路由器里有指数运算，对数值误差敏感。ST-MoE 提出 router z-loss，惩罚进入路由器的 logits 的 log-sum-exp 平方，压住过大的 logits，作者称显著改善稳定性且不损质量（ST-MoE 论文 §3）。

**无辅助损失偏置**。Loss-Free Balancing 的思路是把「均衡」从梯度里拿出来：

- 每个专家维护一个偏置 $b_i$，只用于 top-k **选择**（按 $s_i+b_i$ 排序），乘到输出上的门控仍用原始分数 $s_i$；
- 每步按近期负载调节：过载的专家减小 $b_i$，欠载的增大；
- 偏置依据的是历史负载而非当前序列，以免用到未来 token 的信息（Loss-Free Balancing 论文 §3）。

由于不产生干扰梯度，作者称它同时得到更好的性能与更好的均衡（Loss-Free Balancing 论文摘要）。DeepSeek-V3 在 671B 规模采用了它，并保留一个系数极小的序列级损失防止单条序列内的极端失衡（[[DeepSeekV3训练与MoE基建]] 第三节）。Kimi K3 的 Quantile Balancing 是同一方向的变体：按分位数设偏置，用直方图估计全局批分位，推理时冻结偏置（[[KimiK3技术报告]]）。

**随梯度训练的偏置**。另一条路是让偏置本身成为模型参数。MiniMax-M2 也用 sigmoid 门控加每专家偏置，但偏置与模型参数一起经梯度训练，而非按负载规则更新（Loss-Free 一类正是为了不产生干扰梯度才把偏置放在梯度之外）；报告称这同样大幅减少了对辅助损失的依赖（[MiniMax-M2 系列报告](https://arxiv.org/abs/2605.26494) §2.2.1）。

### 3.4 专家粒度与共享专家

- **细粒度切分**：把 $N$ 个专家各切成 $m$ 份、激活数同步放大为 $mK$，计算量不变而组合数暴增。DeepSeekMoE 的例子：16 选 2 只有 120 种组合，切成 64 选 8 则有 4,426,165,368 种（DeepSeekMoE 论文 §3.1）。组合越多，每个专家越能只学一小块知识。
- **共享专家**：再隔离出若干个对所有 token 恒定激活的专家，承担通用知识，让路由专家少做重复劳动（DeepSeekMoE 论文 §3.2）。DeepSeek 系列、Kimi K2（1 个）与 Kimi K3（2 个）都采用。
- **反方证据**：OLMoE 在其设置下发现「1 共享 + 1 路由」略差于「2 路由」，理由是共享专家把每层可能的组合数从 35,960 砍到 4,495，减少了近九成灵活性（OLMoE 论文 §4.1.3）；Qwen3 的 MoE 也去掉了共享专家（Qwen3 技术报告 §2）。共享专家是否有益，取决于专家粒度与规模，尚无定论。
- **稀疏度成为缩放变量**：Kimi K2 定义稀疏度为总专家数/激活专家数，报告称固定激活参数时提高稀疏度能持续降低损失，最终取 48（[[KimiK2技术报告深读]] 3.2 节）。在极端稀疏下，LatentMoE 让路由专家在更窄的潜空间宽度上计算（机制见 [[KimiK3技术报告]]；[[Nemotron3Ultra技术报告深读]] 同样采用）。

### 3.5 路由约束与通信

专家分布在不同设备上时，token 要经 all-to-all 发往专家所在卡并收回，通信量随 $k$、专家分散程度与节点数增长。专家并行本身——专家如何分到各卡、每层两次 all-to-all 从何而来、它与流水线和数据并行怎样组合——见 [[分布式训练并行策略]] 3.5 节；本节只讲路由为控制这部分通信所加的约束：

- **分组本地派发**：GShard 把批均分成若干组，各组独立计算容量与派发（GShard §2.2）。
- **节点受限路由**：DeepSeek-V3 让每个 token 最多发往 4 个节点，先按节点内最高亲和分之和选节点，再在节点内选专家，以保证通信能被计算重叠（[[DeepSeekV3训练与MoE基建]] 第三节）。DeepSeek-V4 去掉了这一约束（[[DeepSeekV4技术报告深读]]）。
- 通信内核与重叠调度见 [[NVSHMEM与DeepEP通信]] 与 [[DeepSeekV3训练与MoE基建]]；推理侧的专家复制与在线均衡见 [[MegaScaleInfer与UltraEP]]。

## 四、路由坍缩与专家特化

- **坍缩的两种形态**：一是负载坍缩，少数专家吃掉大部分 token，名义总参很大而有效专家很少；二是表示坍缩，路由学习使 token 表示向专家中心聚集，Chi 等提出在低维超球面上计算路由分数来缓解（表示坍缩论文摘要）。
- **专家到底学了什么**：Mixtral 在 The Pile 不同子集上统计专家分配，未发现按主题的明显模式，专家选择更贴近句法，尤其在首尾层（Mixtral 报告 §5）。OLMoE 则报告路由在预训练早期就趋于稳定、专家很少共同激活，并呈现领域与词表特化（OLMoE 论文 §1）。两者结论不同，与专家粒度、均衡方式有关：全局批均衡与无辅助损失偏置都被报告能增强特化（Global-batch LBL 论文摘要；DeepSeek-V3 §4.5，见 [[DeepSeekV3训练与MoE基建]] 第三节）。
- **对均衡目标的再认识**：均衡的对象应是「整个语料上的负载」，而不是「每条序列内部的负载」。过严的局部均衡会把本该特化的专家强行平均化。这是近一年从辅助损失转向全局批统计与偏置调节的共同动机。

## 五、缩放规律：MoE 的两条轴

- **参数与计算分离**：Unified Scaling Laws 把路由模型的性能写成参数量与计算量两个变量的函数，并据此定义「有效参数量」，用来比较不同路由方法（Unified Scaling Laws 论文摘要）。
- **激活比例与粒度**：Efficiency Leverage 用 300 多个模型的实验给出 MoE 相对稠密模型算力优势的预测律：主要由专家激活比例与总算力预算决定，二者都服从幂律，专家粒度则存在最优区间；其验证模型 Ling-mini-beta（0.85B 激活）在 1T token 上追平 6.1B 稠密模型，算力省 7 倍以上（Efficiency Leverage 论文摘要）。
- **对设计的含义**：在激活参数固定时继续增加专家数（提高稀疏度）通常还有收益，但收益递减，并受通信与均衡难度制约，Kimi K2 取 48 即是性能与基础设施复杂度的折中（[[KimiK2技术报告深读]]）。规模定律的一般背景见 [[规模定律与预训练范式]]。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[混合专家架构]] | 上游通史，本篇的起点：Switch 容量公式与辅助损失形式、V3 的 sigmoid 门控 | MoE 史线、总参与激活参、Mixtral 开源叙事 |
| [[DeepSeekV3训练与MoE基建]] | 无辅助损失均衡的首个大规模实例：无辅助损失偏置与序列级损失、节点受限路由、不丢 token | V3 超参、$\gamma$ 调度、Infra 表 |
| [[DeepSeekV4技术报告深读]] | 路由演进的产品案例：Sqrt(Softplus) 亲和分、去掉节点约束、前 3 层哈希路由 | V4 其余架构与训练 |
| [[KimiK2技术报告深读]] | 路由演进的产品案例：稀疏度定义与取 48 的理由、1 个共享专家 | K2 的 MuonClip 与 Infra |
| [[KimiK3技术报告]] | 路由演进的产品案例：Quantile Balancing 与 LatentMoE 作为演进节点 | Stable LatentMoE 三件套细节 |
| [[Nemotron3Ultra技术报告深读]] | 路由演进的产品案例：LatentMoE 作为极端稀疏下的结构选择 | Ultra 的整体配方 |
| [[Qwen3技术报告深读]] | 路由演进的产品案例：Qwen3 MoE 不用共享专家、采用全局批均衡 | Qwen3 的思考模式与后训练 |
| [[分布式训练并行策略]] | 下游承载：专家并行承载路由结果，本篇的路由约束为压低其 all-to-all 而设；只取「每层两次 all-to-all、最忙的卡决定整体速度」这一接口 | 专家放置、与 PP/DP 的组合、DualPipe 等调度 |
| [[NVSHMEM与DeepEP通信]] | 下游实现：路由结果决定其 all-to-all 流量 | 通信内核 |
| [[MegaScaleInfer与UltraEP]] | 推理侧对应：专家复制与在线均衡解决服务时的负载不均，与本篇训练侧的均衡对照 | 推理专家复制与调度 |
| [[规模定律与预训练范式]] | 背景：稠密模型规模定律 | Kaplan 与 Chinchilla 本身 |

## 七、意义

- **把「总参大」变成「容量大」**：路由与均衡决定了专家是否各司其职；细粒度、共享专家与全局均衡让同等激活参数下的模型质量明显提升，是当代开放权重旗舰普遍采用细粒度 MoE 的基础。
- **把系统约束从模型行为里剥离**：从「固定容量 + 丢 token」到「不丢 token + 偏置均衡」，模型不再为硬件形状牺牲 token；均衡也从改梯度变成改选择。
- **使稀疏度成为可调的设计变量**：有了稳定的路由与均衡，总专家数、激活数、粒度才能像层数、宽度一样按缩放规律选取。

## 八、局限与待核实

1. **结论依赖规模与设置**：共享专家是否有益（DeepSeekMoE 与 OLMoE、Qwen3 相反）、专家是否按领域特化（Mixtral 与 OLMoE 不同），都是在各自规模、粒度与均衡方式下的结论，不能直接外推。
2. **无辅助损失偏置的验证规模**：Loss-Free Balancing 原文的实验规模为最多 3B 参数、200B token（摘要）；更大规模的证据来自 DeepSeek-V3 等报告的整体结果，而非严格的对照实验。
3. **效率数字的口径**：DeepSeekMoE 的「约 40% 计算追平 LLaMA2 7B」、Efficiency Leverage 的「7 倍以上」都以各自的数据与训练配方为前提。
4. **未展开的方向**：稠密模型升级为 MoE（upcycling）、MoE 的微调与推理时专家剪枝、多模态 MoE 的模态路由、注意力层的 MoE，本篇均未覆盖；条件记忆与查表稀疏另成一条稀疏轴，本篇不写。

## 九、延伸阅读

建议顺序：先读 Switch Transformers 第 2 节建立 top-1、容量与辅助损失的直觉，再读 ST-MoE 第 3 节理解稳定性，然后读 DeepSeekMoE 第 3 节与 Loss-Free Balancing 理解当代主流做法，最后读 Global-batch LBL 与 OLMoE 的路由分析，对照不同的特化证据。

| 文献 | 链接 | 与本篇的关系 |
|---|---|---|
| Outrageously Large Neural Networks（Shazeer et al., 2017） | https://arxiv.org/abs/1701.06538 | 带噪 top-k 门控、失衡的自我强化 |
| GShard（Lepikhin et al., 2020） | https://arxiv.org/abs/2006.16668 | top-2、容量、分组派发、辅助损失 |
| Switch Transformers（Fedus et al., 2021） | https://arxiv.org/abs/2101.03961 | top-1 与容量因子 |
| BASE Layers（Lewis et al., 2021） | https://arxiv.org/abs/2103.16716 | 线性分配实现均衡 |
| Hash Layers（Roller et al., 2021） | https://arxiv.org/abs/2106.04426 | 哈希路由 |
| Mixture-of-Experts with Expert Choice Routing（Zhou et al., 2022） | https://arxiv.org/abs/2202.09368 | 专家选择路由 |
| ST-MoE（Zoph et al., 2022） | https://arxiv.org/abs/2202.08906 | router z-loss 与稳定性 |
| Unified Scaling Laws for Routed Language Models（Clark et al., 2022） | https://arxiv.org/abs/2202.01169 | 路由模型的缩放规律 |
| On the Representation Collapse of Sparse Mixture of Experts（Chi et al., 2022） | https://arxiv.org/abs/2204.09179 | 表示坍缩 |
| MegaBlocks（Gale et al., 2022） | https://arxiv.org/abs/2211.15841 | 不丢 token 的块稀疏实现 |
| DeepSeekMoE（Dai et al., 2024） | https://arxiv.org/abs/2401.06066 | 细粒度与共享专家 |
| Mixtral of Experts（Jiang et al., 2024） | https://arxiv.org/abs/2401.04088 | 路由分析（§5） |
| Auxiliary-Loss-Free Load Balancing（Wang et al., 2024） | https://arxiv.org/abs/2408.15664 | 无辅助损失偏置 |
| OLMoE（Muennighoff et al., 2024） | https://arxiv.org/abs/2409.02060 | 开放消融与特化分析 |
| DeepSeek-V3 Technical Report（2024） | https://arxiv.org/abs/2412.19437 | 无辅助损失均衡的大规模应用 |
| Demons in the Detail（Qiu et al., 2025） | https://arxiv.org/abs/2501.11873 | 全局批均衡损失 |
| Qwen3 Technical Report（2025） | https://arxiv.org/abs/2505.09388 | 无共享专家、全局批均衡 |
| Kimi K2: Open Agentic Intelligence（2025） | https://arxiv.org/abs/2507.20534 | 稀疏度缩放 |
| Towards Greater Leverage（Tian et al., 2025） | https://arxiv.org/abs/2507.17702 | MoE 效率杠杆的缩放律 |
| The MiniMax-M2 Series（2026） | https://arxiv.org/abs/2605.26494 | sigmoid 门控加专家偏置 |
