---
date: 2026-10-09
status: archived
archived: 2026-10-09
topic: 低精度训练FP8与FP4
title: "低精度训练FP8与FP4"
lines: [AI Infra, 数学原理]
sources:
  - https://arxiv.org/abs/1710.03740
  - https://arxiv.org/abs/2209.05433
  - https://arxiv.org/abs/2310.10537
  - https://arxiv.org/abs/2310.18313
  - https://arxiv.org/abs/2409.12517
  - https://arxiv.org/abs/2411.04330
  - https://arxiv.org/abs/2412.19437
  - https://arxiv.org/abs/2502.20586
  - https://arxiv.org/abs/2505.14669
  - https://arxiv.org/abs/2505.19115
  - https://arxiv.org/abs/2505.20524
  - https://arxiv.org/abs/2506.13585
  - https://arxiv.org/abs/2509.25149
  - https://arxiv.org/abs/2510.25602
  - https://arxiv.org/abs/2510.26788
  - https://arxiv.org/abs/2604.12374
  - https://arxiv.org/abs/2605.09825
  - https://arxiv.org/abs/2606.15007
  - https://arxiv.org/abs/2606.19348
  - https://arxiv.org/abs/2607.24653
  - https://arxiv.org/abs/2608.30181
  - https://arxiv.org/abs/2610.00053
arxiv: ["1710.03740", "2209.05433", "2310.10537", "2310.18313", "2409.12517", "2411.04330", "2412.19437", "2502.20586", "2505.14669", "2505.19115", "2505.20524", "2506.13585", "2509.25149", "2510.25602", "2510.26788", "2604.12374", "2605.09825", "2606.15007", "2606.19348", "2607.24653", "2608.30181", "2610.00053"]
related: ["分布式训练并行策略", "AI基础设施总览", "DeepSeekV3训练与MoE基建", "SpinQuant与ARCQuant量化", "ZeroQAT量化感知训练", "KV缓存量化与压缩", "硬件软件协同部署", "RL训练系统与异步Rollout", "Nemotron3Ultra技术报告深读", "DeepSeekV4技术报告深读", "KimiK3技术报告", "AXK2技术报告深读", "MiniMaxM1技术报告深读", "优化器与训练稳定性"]
---

# 低精度训练FP8与FP4

> **主要来源**：[FP8 Formats for Deep Learning](https://arxiv.org/abs/2209.05433)（简称 FP8 格式论文）；[Microscaling Data Formats for Deep Learning](https://arxiv.org/abs/2310.10537)（简称 MX 论文）；[Scaling FP8 training to trillion-token LLMs](https://arxiv.org/abs/2409.12517)（简称 Fishman 等）；[Pretraining Large Language Models with NVFP4](https://arxiv.org/abs/2509.25149)（简称 NVFP4 论文）；[Nemotron 3 Super](https://arxiv.org/abs/2604.12374)（简称 Nemotron 3 Super 报告）（截至 2026-09-04）。其余来源见第十三节。
> **研究线**：AI Infra（预训练与后训练中矩阵乘、梯度、优化器状态与通信改用 8 位、4 位浮点格式的配方，以及训练格式、发布格式与推理格式的区分）· 数学原理（指数位与尾数位的取舍、块级缩放、随机舍入的无偏性、精度进入缩放律的方式）
> **范围与相邻笔记**：
> - ≠ [[SpinQuant与ARCQuant量化]]：本篇不写推理侧量化，包括训练后对权重与激活做的量化（旋转、残差通道等 PTQ 方法）及其保真评测，只在第九节说明发布格式与训练格式可以不同。
> - ≠ [[KV缓存量化与压缩]]：本篇不写推理时 KV 缓存的量化。
> - ≠ [[ZeroQAT量化感知训练]]：本篇不写 QAT 方法谱系，只记前沿模型在后训练中用低精度 QAT 的做法。
> - ≠ [[硬件软件协同部署]]：本篇不写 GPU 微架构与各代硬件的算力规格。
> - ≠ [[DeepSeekV3训练与MoE基建]]：本篇不复述 DeepSeek-V3 的 FP8 框架全貌，只取它在缩放粒度演进中的位置。
>
> **意义**：16 位混合精度之后，FP8 训练已被广泛采用，FP4 正从论文进入工业预训练与后训练。决定成败的不只是位宽，而是缩放粒度、哪些张量与层保留高精度、舍入方式，以及训练、rollout 与部署三处的数值是否一致。

## 一、问题背景

低精度训练要同时解决两件事：每个数值能表示的范围（由指数位决定）与相邻数值的间隔（由尾数位决定）。位数越少，两者越难兼顾，溢出、下溢与舍入误差都会累积成训练发散。

16 位时代的答案是混合精度。Micikevicius 等提出用半精度存储权重、激活与梯度，同时保留单精度的权重副本累积梯度，用损失缩放保住小幅值梯度，并用半精度乘、单精度累加，论文称这近乎把显存需求减半（混合精度论文摘要）。FP8-LM 论文指出，由于 FP16 的数值范围受限，FP16 与 FP32 的混合方案在大模型上已知不稳定，社区随后普遍改用 BF16 与 FP32 的组合（FP8-LM 论文第 2 节）。

FP8 与 FP4 的动机来自算力与显存。NVFP4 论文称，FP8 训练已被广泛采用，转向 FP4 这类更窄的精度可能进一步提升计算速度与资源利用率，但在这一位宽上，大模型长训练的稳定性、收敛与实现都面临挑战（NVFP4 论文摘要）。本篇按「数制、缩放粒度、FP8 配方、FP4 配方、精度缩放律、后训练、工业落地」的顺序梳理这条线。

## 二、发展脉络

| 时间 | 节点 | 要点 |
|---|---|---|
| 2017-10 | [Mixed Precision Training](https://arxiv.org/abs/1710.03740) | 单精度权重副本、损失缩放、半精度乘单精度累加，奠定混合精度范式 |
| 2022-09 | [FP8 格式论文](https://arxiv.org/abs/2209.05433) | 提出 E4M3 与 E5M2 两种 FP8 编码，推荐权重与激活用 E4M3、梯度用 E5M2 |
| 2023-10 | [MX 论文](https://arxiv.org/abs/2310.10537) | 32 个元素共享一个 E8M0 缩放因子的微缩放格式；6 位格式训练生成式模型与 FP32 持平 |
| 2023-10 | [FP8-LM](https://arxiv.org/abs/2310.18313) | 把 FP8 从矩阵乘扩展到梯度通信、优化器状态与分布式训练 |
| 2024-09 | [Fishman 等](https://arxiv.org/abs/2409.12517) | FP8 训练到 2 万亿 token，发现 SwiGLU 放大离群值导致后期发散 |
| 2024-11 | [Scaling Laws for Precision](https://arxiv.org/abs/2411.04330) | 低精度训练降低「有效参数量」，精度进入缩放律 |
| 2024-12 | [DeepSeek-V3](https://arxiv.org/abs/2412.19437) | 细粒度块级缩放与提升累加精度，在超大规模模型上验证 FP8 预训练 |
| 2025-02 | [Training LLMs with MXFP4](https://arxiv.org/abs/2502.20586)（Tseng 等） | 反向传播用 MXFP4，随机舍入配合随机 Hadamard 变换 |
| 2025-05 | [Quartet](https://arxiv.org/abs/2505.14669) | 所有线性层都用 MXFP4 的端到端训练，并提出低精度缩放律 |
| 2025-05 | [FP4 All the Way](https://arxiv.org/abs/2505.19115) | 权重、激活与梯度都以 FP4 为主的全量化训练，比较块大小、缩放格式与舍入 |
| 2025-05 | [Towards Fully FP8 GEMM LLM Training at Scale](https://arxiv.org/abs/2505.20524) | 改架构让 Transformer 块内所有矩阵乘在前向与反向都用 FP8 |
| 2025-09 | [NVFP4 论文](https://arxiv.org/abs/2509.25149) | 12B 模型用 NVFP4 训练 10 万亿 token，与 FP8 基线可比 |
| 2025-10 | [INT v.s. FP](https://arxiv.org/abs/2510.25602) | 细粒度块缩放下整数格式与浮点格式的比较 |
| 2025-10 | [FP16 论文](https://arxiv.org/abs/2510.26788) | RL 微调中改回 FP16 以消除训推不一致 |
| 2026-04 | [Nemotron 3 Super](https://arxiv.org/abs/2604.12374) | Nemotron 3 系列首个 NVFP4 预训练模型 |
| 2026-04 | [DeepSeek-V4](https://arxiv.org/abs/2606.19348) | 后训练中对 MoE 专家权重做 FP4（MXFP4）QAT |
| 2026-05 | [MXFP4 on Native FP4 Hardware](https://arxiv.org/abs/2605.09825)（Cim 等） | 定位权重梯度量化是 FP4 训练发散的主因 |
| 2026-06 | [Nemotron 3 Ultra](https://arxiv.org/abs/2606.15007) | 550B 总参模型的 NVFP4 预训练 |
| 2026-07 | [Kimi K3](https://arxiv.org/abs/2607.24653) | 后训练全程 MXFP4 权重、MXFP8 激活的 QAT |
| 2026-08 | [A.X K2](https://arxiv.org/abs/2608.30181) | MXFP8 预训练；RL 中训练端与 rollout 端统一为块级 FP8 |
| 2026-09 | [Format-Aware Fusion](https://arxiv.org/abs/2610.00053)（Hu） | FP4 预训练的吞吐瓶颈在缩放计算、打包与布局等周边开销 |

主线分四段：2017 年确立 16 位混合精度；2022 到 2024 年 FP8 从格式定义走到万亿 token 级训练，缩放粒度从整张量收窄到小块；2025 年 FP4 训练配方集中出现，围绕块缩放格式、随机舍入与 Hadamard 变换展开；2026 年 FP4 进入工业预训练与后训练，训练端、rollout 端与部署端的格式一致性成为新问题。

## 三、数制基础

### 3.1 指数位与尾数位

浮点数把位数分给指数与尾数：指数位决定范围，尾数位决定精度。FP16 论文对两种 16 位格式的描述是：FP16 分给指数 5 位、尾数 10 位，精度较高但范围受限，容易溢出与下溢，训练常需损失缩放；BF16 分给指数 8 位，与 FP32 的范围相当，尾数只有 7 位（FP16 论文 §3.1）。

### 3.2 FP8 的两种编码

FP8 格式论文提出 E4M3（4 位指数、3 位尾数）与 E5M2（5 位指数、2 位尾数）两种编码（FP8 格式论文摘要）。两者的分工是：

- **用途**。论文推荐 E4M3 用于权重与激活张量，E5M2 用于梯度张量；有些网络只用其中一种也能训练，但也有网络需要两种都用；这与此前工作中推理和训练前向用 E4M3 变体、反向梯度用 E5M2 变体的发现一致（FP8 格式论文 §3）。
- **特殊值**。E5M2 遵循 IEEE 754 的特殊值约定；E4M3 不表示无穷大，NaN 只保留一个尾数位模式，由此把动态范围多扩展一个 2 的幂，从 17 个 binade 增加到 18 个（FP8 格式论文 §3.1）。
- **规模**。论文的训练实验覆盖最大 175B 参数的语言模型，超参数与 16 位基线保持一致（FP8 格式论文摘要）。

这一分工后来并非定式。DeepSeek-V3 报告称，此前工作在 Fprop 用 E4M3、在 Dgrad 与 Wgrad 用 E5M2，而它对所有张量都用 E4M3 以获得更高精度（DeepSeek-V3 报告 §3.3.2）；A.X K2 报告称其前向与反向都用 E4M3（A.X K2 报告 §3.7）。两者都依赖第四节的细粒度缩放来弥补 E4M3 较窄的范围。

### 3.3 FP4：E2M1

MX 论文与 NVFP4 论文中的 FP4 都是 E2M1（2 位指数、1 位尾数）（MX 论文 Table 1；NVFP4 论文第 2 节）。NVFP4 论文给出 E2M1 与 E4M3 的最大可表示幅值分别为 6 与 448（NVFP4 论文附录 B.1）。NVFP4 论文指出，高精度原值常常超出 FP4 的范围，量化时必须先缩放到可表示范围内（NVFP4 论文第 2 节）；这也是 FP4 配方的重心落在缩放与舍入上的原因。

## 四、缩放粒度：从整张量到小块

### 4.1 张量级缩放

FP8-LM 论文对张量缩放的描述是：在转为 FP8 之前把高精度值乘以缩放因子，使其落入 FP8 格式的可表示范围（FP8-LM 论文第 2 节）。DeepSeek-V3 报告指出，常规做法把输入张量的最大绝对值对齐到 FP8 的最大可表示值，这让低精度训练对激活离群值高度敏感（DeepSeek-V3 报告 §3.3.2）。张量级框架还常用「延迟缩放」，用此前若干迭代的最大绝对值历史推断当前值（DeepSeek-V3 报告 §3.3.2）。Fishman 等指出，长训练后期突然出现的离群值会打破延迟缩放所依赖的跨迭代统计一致性（Fishman 等第 3 节、§4.4）。

### 4.2 块级缩放

缩小共享缩放因子的元素组，单个离群值只影响所在小块。几种代表性做法如下：

| 方案 | 元素格式 | 块大小 | 缩放因子格式 | 出处 |
|---|---|---|---|---|
| 张量级 FP8 | E4M3 / E5M2 | 整张量 | 高精度标量 | FP8-LM 论文第 2 节 |
| DeepSeek-V3 块级 FP8 | E4M3 | 激活按 1 乘 128 的 tile（每 token 每 128 个通道）；权重按 128 乘 128 的 block | 在线计算 | DeepSeek-V3 报告 §3.3.2 |
| MXFP8 | FP8（E4M3 / E5M2） | 32 | E8M0 | MX 论文 Table 1 |
| MXFP6 | FP6（E2M3 / E3M2） | 32 | E8M0 | MX 论文 Table 1 |
| MXFP4 | FP4（E2M1） | 32 | E8M0 | MX 论文 Table 1 |
| MXINT8 | INT8 | 32 | E8M0 | MX 论文 Table 1 |
| NVFP4 | FP4（E2M1） | 16 | 块级 E4M3，另加张量级 FP32 | NVFP4 论文第 2 节 |

几点说明：

- **MX 格式**。MX 论文称所有具体 MX 格式都用 E8M0（一个 8 位指数）作为共享缩放因子的格式，其可表示指数是 FP32 的超集（MX 论文 §2.2）。
- **NVFP4 与 MXFP4 的差别**。NVFP4 论文列出三点：块大小从 32 降到 16，块内动态范围更窄；块缩放因子用 E4M3 而不是 UE8M0，以部分指数范围换取尾数位；再在张量级加一个 FP32 缩放因子（NVFP4 论文第 2 节）。两级缩放先由张量级 FP32 因子把张量整体移到「FP4 乘 FP8」能覆盖的范围，再由块级 E4M3 因子把块内数值移到 FP4 范围（NVFP4 论文第 2 节）。
- **DeepSeek-V3 的累加精度**。除细粒度缩放外，DeepSeek-V3 每隔 128 个元素把部分和提升到 CUDA Core 上做 FP32 累加（DeepSeek-V3 报告 §3.3.2）。完整框架见 [[DeepSeekV3训练与MoE基建]]。

### 4.3 整数还是浮点

INT v.s. FP 论文称，在粗粒度量化下浮点格式占优，到了细粒度块缩放层面比较更复杂：对块大小为 32 的 8 位 MX 格式，MXINT8 在算法精度与硬件效率上都优于对应的浮点格式；在 4 位上，浮点格式（MXFP4、NVFP4）往往有精度优势，但配合 Hadamard 旋转等离群值抑制手段时 NVINT4 可以超过 NVFP4（INT v.s. FP 论文摘要）。论文还提出对称截断方法，用于解决细粒度低比特整数训练中的梯度偏差（INT v.s. FP 论文摘要）。

## 五、FP8 训练配方

### 5.1 从矩阵乘扩展到全流程

FP8-LM 论文指出，当时可用的 Transformer Engine 只在线性层的矩阵乘中用 FP8，权重更新与梯度同步等仍用更高精度（FP8-LM 论文第 2 节）。它提出三级渐进的 FP8 用法，依次纳入 8 位梯度、优化器状态与分布式训练（FP8-LM 论文摘要）。优化器部分的结论是「精度解耦」：梯度统计量可以用低精度，主权重需要高精度；一阶矩可用 FP8，二阶矩需要 16 位；主权重默认用带张量缩放的 FP16（FP8-LM 论文 §2.2）。论文称，在 H100 上训练 GPT-175B 时，其框架让实际显存占用减少 39%，比 BF16 框架 Megatron-LM 快 75%，比 Transformer Engine 快 37%（FP8-LM 论文摘要）。

### 5.2 长训练暴露的离群值

Fishman 等把 FP8 训练推到 2 万亿 token，论文称这比此前的上限增加了 20 倍（Fishman 等摘要）。它们的发现：

- **现象**。在 Llama2 7B 上，FP8 训练在约 200B token 后出现明显的损失发散；离群值只在训练约 200 billion token 之后出现（Fishman 等第 3 节、§4.3）。
- **成因**。论文把发散追溯到 SwiGLU：训练中某些通道里 SwiGLU 两个权重向量的相关性与范数同时增大，产生极端激活；关闭 SwiGLU 输出的量化即可收敛（Fishman 等 §4.3、§4.4）。
- **Smooth-SwiGLU**。对 SwiGLU 的线性支路乘一个缩放因子，在最后一个线性层之后再缩放回来，从而在保留 FP8 加速的同时避免最后一个线性层输入的离群值（Fishman 等 §4.4）。
- **FP8 优化器**。论文称首次把 Adam 的两个矩都量化为 FP8：一阶矩用 E4M3，二阶矩需要动态范围更大的 E5M2（Fishman 等 §5.2）。
- **结果**。在 256 块 Intel Gaudi2 上训练 7B 模型，结果与 BF16 基线相当，吞吐提升最高约 34%（Fishman 等摘要）。

这一结论的意义在于：短训练验证过的 FP8 配方，不能保证在长训练中依然稳定。

### 5.3 块级缩放与全 FP8 矩阵乘

DeepSeek-V3 把细粒度缩放与提升累加精度写进主文，报告称其首次在超大规模模型上验证了 FP8 训练的可行性与有效性，FP8 训练模型相对 BF16 基线的相对损失误差始终低于 0.25%（DeepSeek-V3 报告第 1 节、§3.3）。同期另一条路线是改架构。Hernández-Cano 等称，现有做法要么依赖不够优的细粒度 FP8 内核，要么在注意力投影等敏感部件退回高精度矩阵乘；它们提出的新架构首次让 Transformer 块内所有矩阵乘在前向与反向都用 FP8，并给出预判发散的监控指标（Towards Fully FP8 GEMM 论文摘要）。

### 5.4 MXFP8 预训练

A.X K2 报告是 MXFP8 预训练的一个公开实例（A.X K2 报告 §3.7）：

- 每 32 个连续元素共享一个缩放因子，前向与反向都用 E4M3。
- 主参数与梯度保持 FP32，优化器的指数滑动平均与平方梯度用 BF16，其余符合条件的张量都用 MXFP8。
- 分布式优化器的参数分片直接以 FP8 做 all-gather，并与计算重叠；报告称这既减少通信量，也保证 all-gather 与随后矩阵乘使用同一份低精度权重，有助于 FP8 训练的数值稳定。

## 六、FP4 训练配方

### 6.1 早期探索：MX 格式

MX 论文用 MXFP6_e3m2 同时承担前向与反向，训练 20M 到 1.5B 的类 GPT 模型，超参数沿用 FP32 的设置；论文称这是首次用 6 位权重、激活与梯度把生成式语言模型训练到与 FP32 持平（MX 论文 §4.5）。进一步改用 MXFP4 权重、MXFP6_e3m2 激活与梯度时，论文称模型损失只付出轻微代价，训练配方同样无需修改（MX 论文 §4.5）。

### 6.2 反向传播与全线性层

- **Tseng 等**。论文称，直接用 MXFP4 替代 BF16 训练会显著降低模型质量；其关键是用随机舍入得到无偏梯度估计，再用随机 Hadamard 变换从理论上约束随机舍入的方差，以抑制块级离群值。论文训练了最大 6.7B 参数的 GPT 模型，称相对 BF16 混合精度只有极小退化；配方中超过 1/2 的训练 FLOPs 用 MXFP4，估计反向传播比 FP8 快超过 1.3 倍、比 BF16 快超过 1.7 倍（Tseng 等摘要）。
- **Quartet**。论文以所有主要计算（线性层）都用低精度为目标，选 MXFP4 的原因是论文调研发现，它是当时 Blackwell 上唯一在前向与反向所需布局都有支持的微缩放格式（Quartet 论文摘要、第 3 节）。论文称其 Blackwell 内核让全 FP4 训练成为 FP16 与 FP8 训练的有力替代（Quartet 论文摘要）。

### 6.3 NVFP4 的四件套

FP4 All the Way 系统比较了块大小、缩放格式与舍入方式，结论是 16 个 E2M1 值共享一个 E4M3 缩放因子的 NVFP4 格式效果最好；前向用就近舍入，反向与参数更新用随机舍入；论文还给出一个阈值：当梯度范数低于约 √3 倍的量化噪声时，量化训练的效果变差（FP4 All the Way 论文摘要）。

NVFP4 论文把配方归纳为四条建议（NVFP4 论文第 4 节）：

1. **保留少数敏感线性层的高精度**：约占网络的 15%，多数在网络末端。论文观察到所有线性层都量化为 FP4 时训练发散，末端几层需要比 FP4 更大的动态范围与尾数（NVFP4 论文 §4.1）。
2. **随机 Hadamard 变换**：只作用于权重梯度矩阵乘（Wgrad）的输入，Hadamard 矩阵大小取 16。论文观察到在较小规模上，Hadamard 变换对 Fprop 与 Dgrad 没有可测的收益（NVFP4 论文 §4.2）。
3. **二维缩放**：权重按 16 个输入通道乘 16 个输出通道的二维块缩放，激活与梯度按一维的 16 元素块缩放。动机是反向传播转置张量后，同一张量在前向与反向会得到两种不同的量化表示，违背链式法则（NVFP4 论文 §4.3）。
4. **随机舍入**：梯度用随机舍入，权重与激活用就近舍入。论文称对梯度做随机舍入是 12B 模型收敛的必要条件，对前向张量做随机舍入反而有害（NVFP4 论文 §4.4）。

论文称，这些技巧对较小模型与较短训练未必都需要，但对 12B 模型训练 10T token 而言，去掉任何一项都会让收敛变差（NVFP4 论文第 4 节）。主结果是：12B 模型训练 10 万亿 token，论文称这是迄今公开记录中最长的 4 位精度训练；训练损失与下游准确率与 FP8 基线可比，例如 MMLU-pro 为 62.58%，FP8 预训练为 62.62%（NVFP4 论文摘要）。

格式对比方面，8B 模型训练 1 万亿 token 时，MXFP4 相对 BF16 的相对误差约为 2.5%，NVFP4 为 1.5%；MXFP4 需要多 36% 的 token（1.36T 而不是 1T）才能追平 NVFP4 的损失（NVFP4 论文第 5 节）。论文还建议，在损失最关键的场景，可在训练末段切换到更高精度来缩小差距（NVFP4 论文第 3 节、附录 D）。

### 6.4 发散源头之争：随机性还是结构性误差

Cim 等在 AMD Instinct MI355X 的原生 MXFP4 上做受控实验：在 C4 上完整预训练 Llama 3.1–8B，逐步对 Fprop、Dgrad、Wgrad 启用 FP4，发现量化 Wgrad 是收敛退化的主因；一旦 Wgrad 被量化，随机舍入与随机化 Hadamard 旋转都无法稳定训练，确定性 Hadamard 旋转则能稳定恢复优化（Cim 等摘要）。论文据此认为，FP4 训练的不稳定来自敏感梯度路径上的结构性微缩放误差，而不是随机性不足（Cim 等摘要）。NVFP4 论文的结论相反：其设定是 NVFP4 格式、12B 混合 Mamba-Transformer 模型训练 10 万亿 token，对 Wgrad 输入做随机 Hadamard 变换改善训练，梯度随机舍入是收敛的必要条件（NVFP4 论文第 3 节、§4.2、§4.4）。两者的格式、模型与训练规模都不同，尚无同一设定下的对照，本篇并列呈现，不下结论。

### 6.5 吞吐：周边开销

Hu 指出，FP4 Tensor Core 加速了矩阵乘，但缩放计算、操作数打包、布局构造与为反向保存的状态可能抵消收益（Format-Aware Fusion 论文摘要）。论文的 Llama-3 系 8B 预训练实验跑到 160 billion token，在同一加速器的对照中：

- bfloat16 与 Transformer Engine NVFP4 分别达到 18.8K 与 27.6K tokens/s/GPU，作者最快的自定义路径达到 37.9K。
- 使用行梯度随机舍入与固定符号 32 值 Hadamard 权重梯度预处理的 MXFP4 达到 37.2K tokens/s/GPU（86.3% 的 bfloat16 模型 FLOP 利用率），最终训练损失比 bfloat16 高 2.11%。
- 末端四个块保持 bfloat16 的 Transformer Engine 配方最终损失比 bfloat16 高 0.87%，吞吐为 27.1K tokens/s/GPU。

论文还指出下游排名与训练损失排名不一致（Format-Aware Fusion 论文摘要）。

## 七、精度缩放律

本节只记结论，不展开函数形式。

- **有效参数量**。Kumar 等提出，以较低精度训练会降低模型的「有效参数量」，据此预测低精度训练与训练后量化带来的额外损失；训练侧的缩放律提示，以更低精度训练更大的模型可能是算力最优的；推理侧则发现，模型训练数据越多，训练后量化带来的退化越大，最终使额外的预训练数据变得有害（Scaling Laws for Precision 摘要）。拟合基于超过 465 次预训练，验证规模为最大 1.7B 参数、最多 26B token（Scaling Laws for Precision 摘要）。
- **参数效率与数据效率**。Quartet 为各种量化训练方法拟合缩放律，分离出参数效率与数据效率两个参数；论文发现参数效率与前向压缩误差直接相关，数据效率与梯度估计的偏差相关（Quartet 论文第 1 节）。

两者共同的提示是：低精度训练的代价可以折算成「少了多少参数」或「多要多少数据」，再与吞吐收益权衡；NVFP4 论文中 MXFP4 需多 36% token 才能追平 NVFP4，就是数据效率差异的一个实例（NVFP4 论文第 5 节）。

精度进入缩放律后，参数、数据与精度怎样联合配置，见 [[缩放定律的扩展形态]] 第六节；本节只写与训练配方相关的结论。

## 八、后训练中的低精度

### 8.1 RL 中的精度一致性

RL 的训练端与 rollout 端常用不同的引擎，数值差异会让两边的概率分布分离。本篇只记与精度格式相关的结论，补偿与消除训推不一致的系统做法归 [[RL训练系统与异步Rollout]]。

- **FP16 取代 BF16**。FP16 论文认为 BF16 在预训练中的稳定性是优点，但它的低精度是训推不一致的根源；FP16 有 10 位尾数，论文称其精度是 BF16 的 8 倍；RL 微调时权重与激活的动态范围已在预训练中确定，BF16 的大范围不再关键（FP16 论文 §3.4）。
- **输出头 FP32**。MiniMax-M1 把训推概率差异的主要误差源定位到 LM head 的大幅值激活，将其精度提到 FP32 后，训练与推理概率的相关性从约 0.9x 提高到 0.99x（MiniMax-M1 报告 §3.2）。
- **FP8 下训练端要对齐 rollout 端**。A.X K2 报告称，Blackwell 原生支持 MXFP8，但其 rollout 后端 vLLM 没有一等的 MXFP8 支持，成熟的 MoE FP8 路径面向 Hopper 上的块级 FP8 配方；为让训练与 rollout 使用同一配方，它们端到端统一为块级 FP8，并通过修改过的 Transformer Engine 分支在 Blackwell 上强制使用 FP32 块缩放因子（A.X K2 报告 §4.2）。对照实验中，rollout 固定为块级 FP8，训练端用 MXFP8 时奖励学习先变得不稳定、最终崩溃，加 TIS 也无法阻止；训练端与 rollout 对齐后训练保持稳定（A.X K2 报告 §4.2，Figure 6）。

### 8.2 后训练 QAT：训练即部署

两份 2026 年报告在后训练中用 FP4 做量化感知训练，目的都是部署：

- **DeepSeek-V4**。后训练阶段引入 QAT，对 MoE 专家权重与 CSA indexer 的 QK 路径做 FP4（MXFP4）量化。专家权重的做法是：优化器维护的 FP32 主权重先量化到 FP4，再反量化到 FP8 参与计算；报告称 FP4 到 FP8 的反量化是无损的，因为 E4M3 比 E2M1 多 2 个指数位，只要每个 FP8 量化块（128 乘 128 的 tile）内各 FP4 子块（1 乘 32 的 tile）缩放因子的最大最小比不超过某个阈值，细粒度缩放信息就能被 FP8 的范围完全吸收，整条 QAT 流程因此可以复用现有 FP8 训练框架（DeepSeek-V4 报告 §5.2.1）。反向传播对同一份 FP8 权重求梯度并直接传回 FP32 主权重，相当于直通估计器；推理与 RL rollout 阶段直接使用原生 FP4 权重而不是模拟量化，报告称这保证采样行为与线上部署一致（DeepSeek-V4 报告 §5.2.1）。
- **Kimi K3**。MoE 专家权重量化为 MXFP4、激活用 MXFP8 计算，非专家部件保持更高精度；QAT 覆盖整个后训练阶段（SFT 与 RL），RL 中 rollout 与训练共用同一量化方案，报告称这消除了训推不一致（Kimi K3 报告 §4.1.4）。

这两例说明，后训练 QAT 同时承担两个功能：让模型适应部署格式，以及让 RL 的训练端与 rollout 端在数值上对齐。

## 九、工业落地：训练格式、发布格式与推理格式

同一个模型往往有三种「精度」：训练时矩阵乘用的格式、发布的权重格式、推理服务时的格式。三者可以不同，引用时需分开写。

| 模型 | 训练侧格式 | 发布或部署侧 | 出处 |
|---|---|---|---|
| DeepSeek-V3 | FP8 混合精度预训练（块级缩放，全部张量 E4M3） | 本篇不涉及 | DeepSeek-V3 报告 §3.3 |
| Nemotron 3 Super | NVFP4 预训练，部分层保留 BF16 或 MXFP8 | 另行量化出 FP8（W8A8）与 NVFP4（W4A4）两种部署检查点 | Nemotron 3 Super 报告 §2.2、第 4 节 |
| Nemotron 3 Ultra | NVFP4 预训练，沿用 Super 的配方 | 用训练后量化得到 NVFP4 检查点 | Nemotron 3 Ultra 报告 §2.2、第 4 节 |
| DeepSeek-V4 | 后训练中 MXFP4 QAT（专家权重与 indexer QK 路径） | 路由专家参数使用 FP4 | DeepSeek-V4 报告第 1 节、§5.2.1 |
| Kimi K3 | 后训练全程 MXFP4 权重、MXFP8 激活的 QAT | 与训练同一量化方案 | Kimi K3 报告 §4.1.4 |
| A.X K2 | MXFP8 预训练；RL 阶段训练端为块级 FP8 | 发布块级 FP8（E4M3）检查点，128 乘 128 的权重块、逐 token 动态激活缩放 | A.X K2 报告 §3.7、§4.2 |

几个值得记的工程细节：

- **Nemotron 3 Super 的分层格式**。Table 3 列出：除特别注明外的线性层用 NVFP4；网络最后 15%、潜空间投影、MTP 层、QKV 与注意力投影、嵌入层用 BF16；Mamba 输出投影用 MXFP8，理由是较小规模实验中把这一层量化到 NVFP4 时下溢频繁（Nemotron 3 Super 报告 §2.2）。
- **零值梯度**。Nemotron 3 Super 训练中权重梯度的零值元素增多，到预训练结束时占总参数的 7%；在 Nemotron 3 Nano 上的对照显示，相同 token 量下 NVFP4 预训练产生的零值权重梯度约为 BF16 的 3x，切回 BF16 后恢复到基线水平；报告把来源追到 NVFP4 量化把小幅值梯度下溢为零，并指出二维权重量化块跨越了高幅值与低幅值通道（Nemotron 3 Super 报告 §2.2）。
- **末段提高精度**。Nemotron 3 Super 在 19T token（退火前 1T token）把所有张量提升到 MXFP8，训练到 20.6T token；报告称损失轨迹有改善，但下游任务准确率没有提升，最终模型全程使用 NVFP4 配方（Nemotron 3 Super 报告 §2.2）。NVFP4 论文也建议在损失最关键的场景于训练末段切换到更高精度（见 6.3 节）。两者都在训练末段提高精度，但模型、切换格式与切换时机都不同。
- **梯度累加精度**。Nemotron 3 Ultra 的第一次发散出现在约 8T token，报告将其归因于为把数据并行梯度归约改为 BF16 传输，把输出层的本地梯度累加精度从 FP32 降到 BF16；回滚并恢复完整的 FP32 梯度归约后训练重新稳定（Nemotron 3 Ultra 报告 §2.7）。
- **发布格式与训练格式分离**。A.X K2 训练用 32 元素的 MX 块，发布时改用主流 FP8 推理内核支持的块级格式，报告称模型无需单独的事后量化即可直接以 FP8 服务，同一块级配方也用于 RL rollout（A.X K2 报告 §3.7）。

## 十、意义

1. **对预训练成本**：NVFP4 论文称 FP8 训练已被广泛采用；FP4 预训练已有从 8B 到 550B 总参的公开实例。但各家给出的对照基线不同（NVFP4 论文对 FP8 基线，Nemotron 3 Ultra 对切换到 BF16 的分支），引用「与高精度相当」时要写明对谁。
2. **对配方设计**：缩放粒度是主轴，从整张量到 128 元素块、32 元素块、16 元素块逐步收窄；在其上叠加的保留高精度层、随机舍入、Hadamard 变换、二维权重块等，本质上都在处理离群值、偏差与前反向一致性三类误差。
3. **对稳定性判断**：Fishman 等的后期发散、Nemotron 3 Super 的零值梯度增长都说明，低精度问题可能在长训练后期才出现；短程验证不足以判定配方安全。
4. **对后训练**：RL 让「训练端与 rollout 端的数值一致」成为硬约束，后训练 QAT 把部署格式提前到训练中，这使低精度从单纯的加速手段变成训练正确性的一部分。
5. **对引用**：训练格式、发布格式与推理格式是三件事；把推理侧量化的保真数字当作训练侧结论，是这个领域最常见的误读。

## 十一、局限与待核实

1. **对照基线不一**。FP8-LM 对 BF16 的 Megatron-LM，Fishman 等对 BF16，NVFP4 论文对 FP8，Nemotron 3 Ultra 对切换到 BF16 的分支，Hu 对 bfloat16；各篇数字不能直接横向比较。
2. **随机化手段的结论有冲突**。NVFP4 论文认为随机舍入与随机 Hadamard 变换有益，Cim 等在 MXFP4 与 AMD 硬件上发现两者在 Wgrad 量化后无效、确定性 Hadamard 才有效；两者的格式、模型与训练规模不同，尚无同一设定下的对照。
3. **吞吐数字依赖硬件与内核**。Tseng 等的加速是估计值，Hu 的吞吐来自同一加速器上的对照探测；FP4 相对 FP8 的实际收益随内核实现变化，本篇不做换算。
4. **缩放律的验证规模有限**。Kumar 等的验证规模为最大 1.7B 参数、最多 26B token，外推到万亿 token 级训练需谨慎。
5. **部分工业报告只给结论**。Nemotron 3 Ultra 第二次发散的原因报告标为「Undetermined」；DeepSeek-V4 提到的 FP4 子块缩放因子比值阈值未给出具体数值。
6. **推理侧数字未收**。A.X K2 报告 §6.1 有 NVFP4 相对 FP8 的基座任务保真数字，但那是训练后量化的评测，属推理侧，本篇不收；Qwen3.8-Next 报告中的 FP8 用于推理时残差状态的存储，同样不在本篇范围。
7. **版本**。Quartet 当前为 v4、Cim 等为 v4、NVFP4 论文为 v2、Tseng 等为 v3，本篇按 abs 页当前版本引用；早期版本的数字可能不同。
8. **本篇未覆盖**：INT8 训练、低精度注意力内核、低精度通信压缩算法、非 NVIDIA 与 AMD 硬件上的格式支持。

## 十二、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[分布式训练并行策略]] | 前置：本篇第五节的 FP8 参数 all-gather 与梯度归约精度，都发生在该篇所述的并行切分之上 | 各种并行与 ZeRO/FSDP 的机制 |
| [[AI基础设施总览]] | 上位总览：本篇把总览中低精度一节展开为从 FP16 到 FP4 的训练侧专题 | 训练并行、注意力核与推理 serving 总览 |
| [[DeepSeekV3训练与MoE基建]] | 节点：DeepSeek-V3 的块级缩放在本篇第四节缩放粒度演进中作为一个节点出现 | FP8 框架全貌、通信重叠与成本 |
| [[SpinQuant与ARCQuant量化]] | 对照：两篇都处理离群值，该篇在训练后对权重与激活做旋转与残差补偿，本篇在训练中用 Hadamard 变换与块缩放 | PTQ 方法与结果 |
| [[ZeroQAT量化感知训练]] | 方法背景：本篇第八节的后训练 QAT 属于该篇所述的量化感知训练范式 | QAT 方法谱系与端侧实验 |
| [[KV缓存量化与压缩]] | 边界：KV 缓存量化是推理侧的另一类低精度，与本篇的训练格式无关 | KV 量化方法 |
| [[硬件软件协同部署]] | 硬件背景：本篇第四节的 MX 与 NVFP4 格式依赖该篇所述的硬件代际支持 | 微架构与算力规格 |
| [[RL训练系统与异步Rollout]] | 分工：本篇第八节只写精度格式本身对训推一致性的影响，该篇写补偿与消除不一致的系统做法 | rollout 架构、离策修正 |
| [[Nemotron3Ultra技术报告深读]] | 案例：Nemotron 3 Ultra 是本篇第九节 NVFP4 预训练的实例之一 | 架构、数据与后训练全貌 |
| [[DeepSeekV4技术报告深读]] | 案例：本篇第八节的 FP4 QAT 取自该报告 | 混合注意力、mHC 与后训练流程 |
| [[KimiK3技术报告]] | 案例：本篇第八节的 MXFP4 后训练 QAT 取自该报告 | 架构、RL 与基础设施全貌 |
| [[AXK2技术报告深读]] | 案例：本篇第五节的 MXFP8 预训练与第八节的训练端对齐 rollout 取自该报告 | 模型全貌与部署侧低比特评测 |
| [[MiniMaxM1技术报告深读]] | 案例：本篇第八节的输出头 FP32 取自该报告 | M1 架构与 CISPO |
| [[优化器与训练稳定性]] | 分工：一般的训练稳定性手段归该篇，本篇只写由低精度引起的发散 | 优化器与通用稳定化技巧 |

## 十三、延伸阅读

建议顺序：先读混合精度论文与 FP8 格式论文建立数制概念，再读 MX 论文与 NVFP4 论文第 2 节理解块缩放格式；FP8 配方读 FP8-LM 与 Fishman 等，FP4 配方读 Tseng 等、FP4 All the Way 与 NVFP4 论文第 4 节；最后读 Kumar 等的缩放律与几份工业报告的精度章节。

| 文献 | 链接 | 与本篇的关系 |
|---|---|---|
| Mixed Precision Training（Micikevicius et al., 2017） | https://arxiv.org/abs/1710.03740 | 16 位混合精度范式 |
| FP8 Formats for Deep Learning（Micikevicius et al., 2022） | https://arxiv.org/abs/2209.05433 | E4M3 与 E5M2 的定义与用途 |
| Microscaling Data Formats for Deep Learning（Rouhani et al., 2023） | https://arxiv.org/abs/2310.10537 | MX 格式与 6 位训练 |
| FP8-LM（Peng et al., 2023） | https://arxiv.org/abs/2310.18313 | FP8 梯度、优化器与分布式训练 |
| Scaling FP8 training to trillion-token LLMs（Fishman et al., 2024） | https://arxiv.org/abs/2409.12517 | 长训练离群值、Smooth-SwiGLU、FP8 Adam 矩 |
| Scaling Laws for Precision（Kumar et al., 2024） | https://arxiv.org/abs/2411.04330 | 精度感知缩放律 |
| DeepSeek-V3 Technical Report（DeepSeek-AI, 2024） | https://arxiv.org/abs/2412.19437 | 块级 FP8 与累加精度 |
| Training LLMs with MXFP4（Tseng et al., 2025） | https://arxiv.org/abs/2502.20586 | 随机舍入与随机 Hadamard 变换 |
| Quartet（Castro et al., 2025） | https://arxiv.org/abs/2505.14669 | 全线性层 MXFP4 与低精度缩放律 |
| FP4 All the Way（Chmiel et al., 2025） | https://arxiv.org/abs/2505.19115 | 全量化 FP4 训练的设计空间 |
| Towards Fully FP8 GEMM LLM Training at Scale（Hernández-Cano et al., 2025） | https://arxiv.org/abs/2505.20524 | 改架构实现全 FP8 矩阵乘 |
| MiniMax-M1（MiniMax, 2025） | https://arxiv.org/abs/2506.13585 | 输出头 FP32 |
| Pretraining LLMs with NVFP4（NVIDIA, 2025） | https://arxiv.org/abs/2509.25149 | NVFP4 格式与训练四件套 |
| INT v.s. FP（Chen et al., 2025） | https://arxiv.org/abs/2510.25602 | 细粒度整数与浮点格式对比 |
| Defeating the Training-Inference Mismatch via FP16（Qi et al., 2025） | https://arxiv.org/abs/2510.26788 | RL 中的 FP16 |
| Nemotron 3 Super（NVIDIA, 2026） | https://arxiv.org/abs/2604.12374 | NVFP4 预训练的分层格式与零值梯度 |
| Pretraining LLMs with MXFP4 on Native FP4 Hardware（Cim et al., 2026） | https://arxiv.org/abs/2605.09825 | Wgrad 量化与确定性 Hadamard |
| Nemotron 3 Ultra（NVIDIA, 2026） | https://arxiv.org/abs/2606.15007 | 550B 总参 NVFP4 预训练与梯度累加精度 |
| DeepSeek-V4（DeepSeek-AI, 2026） | https://arxiv.org/abs/2606.19348 | 后训练 FP4 QAT |
| Kimi K3 Technical Report（Kimi Team, 2026） | https://arxiv.org/abs/2607.24653 | MXFP4 后训练 QAT |
| A.X K2 Technical Report（Baek et al., 2026） | https://arxiv.org/abs/2608.30181 | MXFP8 预训练与训练端对齐 rollout |
| Format-Aware Fusion for Fast FP4 Pretraining（Hu, 2026） | https://arxiv.org/abs/2610.00053 | FP4 预训练的周边开销与吞吐 |
