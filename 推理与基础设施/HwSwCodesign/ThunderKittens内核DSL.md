---
title: "GPU Kernel DSL：ThunderKittens（Dr. Kernel 索引）"
topic: ThunderKittens内核DSL
date: 2026-09-22
lines: [AI Infra, 编程模型]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2410.20399
 - https://openreview.net/forum?id=0fJfVOSUra
 - https://proceedings.iclr.cc/paper_files/paper/2025/hash/05dc08730e32441edff52b0fa6caab5f-Abstract-Conference.html
 - https://arxiv.org/abs/2602.05885
arxiv: ["2410.20399", "2602.05885"]
related: ["硬件软件协同部署", "注意力效率族MQA到MLA", "AI基础设施总览", "推理引擎生态", "混合Mamba与注意力架构设计菜谱", "线性注意力与状态空间模型谱系"]
github_tk: "https://github.com/HazyResearch/ThunderKittens"
github_dr_kernel: "https://github.com/hkust-nlp/KernelGYM"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# GPU Kernel DSL：ThunderKittens（Dr. Kernel 索引）

> **主要来源**：[ThunderKittens: Simple, Fast, and Adorable AI Kernels（Spector, Arora, Singhal, Fu, Ré，Stanford）](https://arxiv.org/abs/2410.20399)，会刊版见 [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/05dc08730e32441edff52b0fa6caab5f-Abstract-Conference.html)；索引 [Dr. Kernel](https://arxiv.org/abs/2602.05885)（截至 2026-09-22）
> **研究线**：AI Infra / 编程模型（主）——GPU 核该用什么抽象来写；评测字段（辅）——论文 H100 结果
> **范围与相邻笔记**：
> - ≠ [[硬件软件协同部署]]：本篇不写芯片与机架的代际规格，只写核的编程抽象。
> - ≠ [[注意力效率族MQA到MLA]]：本篇不写注意力算法变体，GQA 只作 TK 实现的一类工作负载。
> - 本篇不是 CUDA 教程，不写核源码与安装步骤；Dr. Kernel 只作索引。
>
> **意义**：ThunderKittens 显示，围绕「喂饱 tensor core」设计的一小套意见化抽象（16×16 tile、异步流水模板、块序控制），就能写出与 CuBLAS、FlashAttention-3 相当的核，并在线性注意力、SSM 等新算子上大幅领先，缩短新架构等待高性能核的时间。

**一句话**：不靠大量嵌套模板，也不靠整套编译器，而是用三层少数抽象把 GPU 的硬件特性默认用对，必要时退回完整 C++。

---

## 一、问题背景：新架构总在等核

TK 开篇的诊断（§1、Abstract）：

1. **核欠账**：新架构层出不穷，GPU 实现常远低于理论峰值。连 softmax 注意力也长期缺核：FlashAttention-2 迁到 H100 有 47% 的性能退化，FlashAttention-3 在 H100 发布两年多之后才出现。
2. **硬件技巧繁多**：warp / block / grid 三级并行、bank conflict、occupancy、L2 复用……
3. **中心事实**：BF16 tensor core 的吞吐约为通用算力的 16 倍（论文对 A100/H100 的叙述），高性能核必须优先喂饱 tensor core、压低其余开销。

问题因此是：一小套意见化抽象，能否既好写又够快？

## 二、脉络：注意力核与核编程路线

| 节点 | 内容 | 来源 |
|---|---|---|
| FlashAttention / FA2 | 把注意力从算力问题改写成显存带宽与占用率问题（IO-aware） | [[AI基础设施总览]] §三 |
| FA2 → H100 | 迁到 H100 性能退化 47%，FA3 两年多后才补上 | TK §1 |
| CUTLASS / CuTe | C++ 嵌入、理论上能写任何核，但模板繁重 | TK §2、Appendix A |
| Triton 等编译器路线 | 接口友好，但难直接用未暴露的专用指令与细粒度异步控制 | TK §2、Appendix A |
| ThunderKittens（ICLR 2025） | 嵌入 C++ 的少数抽象 | TK §3 |
| Dr. Kernel（2026） | 另一条路：用强化学习让 LLM 生成 Triton 核 | Dr. Kernel 摘要 |

## 三、核心思想：三层意见化抽象（TK §3）

抽象按 GPU 层次对齐。

### 3.1 Warp 级：16×16 tile 作为基本类型

- 以 16×16 矩阵 tile 为基元，最大化与 tensor core 的兼容；有寄存器 tile、共享 tile，以及面向 HBM 的四维全局布局描述符（类比 PyTorch 的 batch / head / length / embed）。
- tile 上的算子（mma、exp、cumsum、逐点乘等）接口贴近 PyTorch。
- 共享内存布局只留 3 种 swizzle，按 tile 宽度自动选，用以压低 bank conflict。
- 布局不符（如 mma 要求 A 行主、B 列主）在编译期报错。

设计含义：把「线程拥有哪块数据、用哪种 swizzle」从手工活收成类型系统，默认路径就对准 tensor core。

### 3.2 Block 级：LCSF 异步模板

开发者填 Load / Compute / Store / Finish 四个函数，模板负责：

- **多段流水缓冲**：Table 1 的 GEMM（M=N=K=4096）里，段数 1/2/3/4 对应约 260 / 484 / 683 / 760 TFLOPS；
- **阶段同步**与统一的异步 I/O 接口（同步拷贝、TMA 同一包装）；
- **occupancy 旋钮**：调 load/store 与 compute worker 数量，在「重叠」与「寄存器、共享内存争用」之间扫曲线，不必手写 ping-pong 调度（论文对比 FA3 的手写方式）。

与 Triton 的关键差别：TK 嵌入 CUDA/C++，抽象不够用时可以退回完整 C++。

### 3.3 Grid 级：持久化启动与块序

- **持久化块**：块在 Finish 阶段领下一份工作或预取下一段输入，减少反复启动的流水气泡（Table 2）。
- **块序决定 L2 复用**：Table 3 中同一 GEMM 换块序，982 GB/s·805 TFLOPS 对 3070 GB/s·392 TFLOPS——HBM 流量高反而算力效率低，说明数据复用落在 L2、取决于块的启动顺序。

## 四、H100 结果（TK §4，H100 80GB SXM，CUDA 12.6）

| 工作负载 | 对照 | 结果（论文口径） |
|---|---|---|
| GEMM | CuBLAS | 匹敌；单个约 40 行 device 代码的核 |
| 注意力前向 | FlashAttention-3 | 竞争 |
| 注意力反向 | FlashAttention-3 | 短序列快 40% 以上，长序列约 10% |
| 多项式特征线性注意力 | Flash Linear Attention | 14× |
| 学习特征映射线性注意力 | 同上 | 6.5× |
| 长卷积 | FlashFFTConv | 序列 4096 为 4.7×，1024 为 7.9×；相对 PyTorch FFT 最高约 8.7× |
| Mamba-2 | 此前的 Triton 核 | 3× 以上，论文归因于更易融合复杂算子 |

**NCU 剖面（Table 4）**：反向注意力上 TK 与 FA3 的 tensor core 利用率接近，但共享内存 stall 0.14 对 0.92；论文称 TK 无 bank conflict，而 NCU 对 FA3 报最高约 9.6-way；长卷积的 tensor core 利用率约为 FlashFFTConv 的 4.1×。

## 五、与相近路线的定位

| 路线 | 角色 | TK 的差异主张 |
|---|---|---|
| CUTLASS / CuTe | 同为 C++ 嵌入 | 少模板，默认避免 bank conflict |
| Triton / TVM / XLA | 编译器与高层图 | 留在 CUDA 嵌入层，可直接用专用指令 |
| Dr. Kernel | LLM 经强化学习生成 Triton 核 | 主体不同：TK 是人写 DSL，Dr. Kernel 是模型生成 |

**Dr. Kernel 索引**：问题是 LLM 生成核时的 reward hacking（写了 Triton 核却不调用等）与只优化琐碎子算子；做法是分布式环境 KernelGYM 与多轮强化学习方法 TRLOO，产出 Dr. Kernel-14B。代码见 [KernelGYM](https://github.com/hkust-nlp/KernelGYM)。

## 六、意义

- **抽象层的选择**：在 C++ 嵌入层只做少数意见化抽象，兼顾可写性与对硬件的完全控制，是 CUTLASS 与 Triton 之间的第三种做法。
- **对新架构**：线性注意力、长卷积、Mamba-2 这些新算子过去缺少成熟的核，TK 的倍数级加速说明它们的瓶颈有一部分在实现，而不全在算法。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[硬件软件协同部署]] | 那篇讲 tensor core、互联等硬件规格，本篇讲怎样写核才能用满这些硬件 | 代际与机架规格 |
| [[注意力效率族MQA到MLA]] | 那篇讲注意力存多少 KV 的算法族，本篇把 GQA 当作 TK 实现过的工作负载 | 注意力公式与取舍 |
| [[AI基础设施总览]] | 那篇 §三 讲 FlashAttention-2 的 IO-aware 思路，本篇是其后的核编程抽象 | FlashAttention 原理 |
| [[推理引擎生态]] | 推理引擎会调用定制核，本篇讲这类核的写法 | 引擎选型 |
| [[混合Mamba与注意力架构设计菜谱]] | 那篇讲混合 SSM–注意力的架构设计，本篇的 Mamba-2 与长卷积核是这类架构的底层实现 | 架构配比 |
| [[线性注意力与状态空间模型谱系]] | 那篇讲线性注意力与 SSM 的递归 / 分块形式，并指出分块并行内核是新层落地的前提；本篇的线性注意力与 Mamba-2 核是这类形式的一种实现 | 线性注意力与 SSM 的数学与谱系 |

## 八、局限与待核实

- **硬件范围**：论文只测 H100 + CUDA 12.6；仓库后来的 Blackwell 等支持属工程演进，不能算作论文结论。
- **剖面的适用范围**：「无 bank conflict」只对论文剖析的这些核成立，不是全称命题。
- **「匹敌 CuBLAS」的含义**：指所示矩阵规模上单个短核可竞争，不是替换 cuBLAS 库。
- **可用性叙事**：论文称没有 CUDA 经验的学生也能写出快核，这是叙事，不是可复现的用户实验。
- **Dr. Kernel**：只作索引，KernelBench 数字以原文为准，未深读。

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [ThunderKittens](https://arxiv.org/abs/2410.20399) §3 | 三层抽象的设计 |
| 2 | 同上 §4、Table 4 | H100 结果与 NCU 剖面 |
| 3 | [ThunderKittens 仓库](https://github.com/HazyResearch/ThunderKittens) | 当前支持的硬件与示例 |
| 4 | [Dr. Kernel](https://arxiv.org/abs/2602.05885) | 模型生成核的另一条路 |
