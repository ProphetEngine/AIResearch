---
title: "分布式集合通信 Demystifying NVSHMEM（DeepEP 案例）"
topic: NVSHMEM与DeepEP通信
date: 2026-09-22
lines: [AI Infra, 架构思想]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2606.05951
 - https://github.com/deepseek-ai/DeepEP # 工程辅：主 README 现为 V2.5（NCCL GIN）
 - https://github.com/deepseek-ai/DeepEP/tree/v1.2.1 # V1（NVSHMEM 后端）README 与性能表
 - https://github.com/deepseek-ai/DeepEP/blob/main/README.md
 - https://github.com/deepseek-ai/DeepEP/commit/b306af06afd412c88e51e71802951606e40b7358
 - https://github.com/deepseek-ai/DeepEP/commit/def865146e95aa9ea223e277c0a8a4c6b81e5ac7
arxiv: ["2606.05951"]
related: ["AI基础设施总览", "混合专家架构", "DeepSeekV3训练与MoE基建", "DeepSeekV4技术报告深读", "MegaScaleInfer与UltraEP", "硬件软件协同部署", "分布式训练并行策略", "MoE路由与负载均衡"]
retrieval_cutoff: 2026-09-30
timezone: Asia/Shanghai (CST)
github_deepep: "https://github.com/deepseek-ai/DeepEP"
note_deepep_arxiv: "DeepEP 无独立 arXiv 主文；主文以 GitHub [33] 引用"
---

# 分布式集合通信 Demystifying NVSHMEM（DeepEP 案例）

> **主要来源**：[Demystifying NVSHMEM（Ma, Shen, Chen 等，ETH Zürich + NVIDIA）](https://arxiv.org/abs/2606.05951)，v1 2026-06-04，分析对象为 NVSHMEM 3.3.9；[deepseek-ai/DeepEP README](https://github.com/deepseek-ai/DeepEP/blob/main/README.md)（现为 V2.5）；[deepseek-ai/DeepEP v1.2.1 README](https://github.com/deepseek-ai/DeepEP/tree/v1.2.1)（V1，NVSHMEM 后端）（截至 2026-09-30）
> **研究线**：AI Infra（主）——GPU 设备侧发起通信的编程模型与实现；架构思想（辅）——稀疏专家并行为何需要这种通信
> **范围与相邻笔记**：
> - ≠ [[混合专家架构]]：本篇不写 MoE 路由与稀疏史，专家并行只当「专家切分 → 数据依赖的 all-to-all」一句接口。
> - ≠ [[DeepSeekV3训练与MoE基建]] / [[DeepSeekV4技术报告深读]]：本篇不重写报告里的 DualPipe、SM 配额、FP8 配方，只讲通信底层。
> - ≠ [[MegaScaleInfer与UltraEP]]：本篇不写服务系统的部署搜索与负载均衡。
>
> **意义**：MoE 的 dispatch/combine 是由路由结果决定的稀疏 all-to-all，主机发起的集合通信接口难以表达；NVSHMEM 让 GPU kernel 直接读写远端显存，DeepEP 正是在这一能力上自建通信流水，才把专家并行做成了可用的工程件。

**一句话**：NVSHMEM 把多 GPU 显存变成一张「对称堆 + 一侧 put/get/atomic」的地址空间，可在 kernel 内发起；DeepEP V1 只在跨节点关键点薄用 NVSHMEM/IBGDA，其余多段传输和 warp 分工全部自建。

---

## 一、问题背景：主机发起的集合通信不够用

NCCL 是 CUDA 分布式训练与推理的默认集合通信后端，传统接口由主机发起：CPU 把集合操作排进 stream，再调度 NCCL kernel。它对规则、大批量、同步的集合（AllReduce 等）极强，但对三类场景不自然（主文 §I–II）：

- 细粒度点对点通信；
- 只涉及一部分 rank、由数据决定对象的通信；
- 与计算紧耦合的自定义 kernel（稀疏专家并行、不规则图等）。

这些场景里，主机协调的开销和控制粒度成为瓶颈。MoE 的专家并行恰好落在其中：每层每个 token 发往哪些 GPU，要等路由算完才知道。

## 二、脉络：从 OpenSHMEM 到设备发起通信

| 阶段 | 内容 | 来源 |
|---|---|---|
| PGAS / OpenSHMEM | 逻辑共享、物理按 PE（processing element）分区的地址空间；一侧通信，目标方无需配对 recv | 主文 §I–II |
| NVSHMEM | 把 OpenSHMEM 搬到 GPU：通常一进程一 GPU 一 PE，CUDA kernel 内可直接发起 put/get/atomic | 主文 §I–III |
| GPU 发起网络操作 | GDA-KI：kernel 直接发起并控制网卡操作，绕过 CPU 代理；IB 上的实现称 IBGDA | 主文 §I–II |
| DeepEP V1 | DeepSeek 开源的专家并行通信库，跨节点部分建在 NVSHMEM/IBGDA 上；仓库创建于 2025-02-17 | 主文 §VIII；DeepEP 仓库 |
| NCCL 吸收 | NCCL 后续通过 Device API、对称内存、GIN 吸收了部分 NVSHMEM 先发概念，但仍强调 scale-up / scale-out 与 communicator 层级 | 主文 §I–II |
| DeepEP V2 / V2.5 | 2026-04-30 公开 EPv2，后端改为 NCCL GIN；2026-09-29 的 V2.5 完全移除 V1 及其 NVSHMEM 后端 | DeepEP README；仓库提交记录 |

所以 NVSHMEM 与 NCCL 是互补关系：前者偏平坦的远程内存视图，后者偏集合与层级拓扑。

## 三、核心思想：对称堆 + 一侧通信

### 3.1 编程模型（主文 §III）

- **对称对象**：每个 PE 上同类型、同大小、同布局的对象，可被别的 PE 直接 put/get/atomic。
- **Team**：PE 子集的轻量句柄，不像 communicator 那样承载大部分运行时状态；但集合内部资源按 team 绑定，所以同一 team 上不能并发发起多个集合。
- **作用域**：设备侧 API 可按 thread / warp / block 发起；主机侧另有排进 stream 的版本。能放进 kernel 热路径的是 RMA、atomic 和完成/等待原语；堆的分配与 team 创建仍走主机侧。

### 3.2 对称堆的实现（主文 §IV）

用 CUDA 虚拟内存管理在初始化时预留连续虚拟地址，物理页按需提交。每个 PE 的地址区间里，第一段是本地堆，其余段按固定偏移映射可直连的 peer，于是远端地址 = peer 基址 + 对象偏移，kernel 内一次算出。

### 3.3 快路径与慢路径（主文 §V）

- **快路径**：同节点可 P2P 直连的 peer，直接对映射地址做 load/store，走 NVLink。
- **慢路径**：跨节点 peer 走 IBGDA（GPU 直接驱动网卡）或 CPU 代理线程。

设计含义：同一套 API，底层按拓扑分流，调用方不必区分。

### 3.4 设备侧集合（主文 §VI）

集合用对称的同步数组协调；小消息协议有 LL（16B 粒度）与 LL128（128B，适合 NVLink）；算法按规则树选择。关键限制：没有整个 grid 范围的设备集合，多 CTA 协同的集合只能走主机侧排进 stream 的版本。

## 四、微基准要点（主文 §VII，H200 + ConnectX-7 IB）

| 维度 | 结果（主文口径） |
|---|---|
| 节点内带宽 | bulk put 约 313、get 约 141 GB/s；标量 p 约 172、g 不足 9 GB/s |
| 跨节点 IBGDA | bulk put/get 约 48.0 / 48.2 GB/s；标量 p/g 约 15.6 / 1.28 GB/s |
| 延迟 | 节点内约 1.8–2.5 µs；IBGDA 约 9.4–9.7 µs |
| 节点内 AllReduce | stream 版 264 GB/s，接近 NCCL NVLS 的 276；单 block 设备版约 30 |
| 跨节点 AllReduce | NVSHMEM 不足 0.20 GB/s，NCCL 为 180 / 252 GB/s |
| 小消息延迟 | NVSHMEM 3.8–7.1 µs，NCCL ring 4.7–8.9 µs |

结论：bulk、聚合写风格的 RMA 最有效，标量操作更适合作控制与延迟原语；NVSHMEM 的跨节点集合明显弱于 NCCL，它的长处在一侧 RMA 而非集合。

## 五、DeepEP V1 怎么用 NVSHMEM（主文 §VIII）

### 5.1 问题形态

专家并行的 dispatch（token 发往专家所在 GPU）与 combine（结果送回）都是稀疏、由路由决定的 all-to-all，每次的发送量和对象都不同。

### 5.2 高吞吐路径（训练与 prefill）

- **两段式**：先经 RDMA 发到目标节点上「同一本地序号」的 GPU，再经 NVLink 转发给真正托管专家的 GPU；这与 [[DeepSeekV3训练与MoE基建]] 记录的「先 IB 到同 index GPU、再 NVLink 转发」一致。
- **准备**：先交换每个 peer 要收多少 token 的元数据，再分配接收位置。
- **流水**：通道以成对 SM 组织，warp 按角色专门化；每个 peer 一个 RDMA 环形缓冲。
- **NVSHMEM 的用量**：只在跨节点关键点调用 warp 级 IBGDA 非阻塞 put 和非取回原子加（作信用计数）；另按「每节点 8 GPU」的假设建 8 个并行 team。

### 5.3 低延迟路径（decode）

不做 NVLink 转发，直接对全局 team 做 IBGDA put，配合原子计数通知到达，以降低单步延迟。

### 5.4 V1 性能表（DeepEP v1.2.1 README，H800 + CX7）

设定：4096 tokens、hidden 7168、top-4 groups、top-8 experts，dispatch 用 FP8、combine 用 BF16。

| 路径 | 规模 | dispatch / combine |
|---|---|---|
| 节点内 | EP8 | 153 / 158 GB/s（NVLink） |
| 跨节点 | EP16 | 43 / 43 GB/s（RDMA） |
| 跨节点 | EP32 | 58 / 57 GB/s |
| 跨节点 | EP64 | 51 / 50 GB/s |
| 低延迟 | EP8，每批 128 tokens | dispatch 77 µs / 98 GB/s；combine 114 µs / 127 GB/s |

### 5.5 核心结论

DeepEP 并不把工作表达成 NVSHMEM 集合或通用 RMA 全家桶：NVSHMEM 只出现在元数据交换、分块 put、信用原子这些跨节点关键点，上层多段传输和 warp 分工是自建的。主文概括为「薄封装 NVSHMEM/IBGDA + 厚自建流水」。性能方面主文没有复测，§VIII-C 转述了 NVIDIA 自己的 GIN 工作（Hamidouche 等，*GPU-Initiated Networking for NCCL*，2025）：在该工作中，DeepEP 接到 NCCL GIN、并以原 NVSHMEM 版为基线，HT 与 LL 两条路径的 dispatch / combine 性能通常相差约 1–2%。这不是 DeepEP V2 自己的实测。

## 六、DeepEP V2：后端换成 NCCL GIN

主文明说只分析 V1，V2 基于 NCCL GIN、不在其范围内（主文 §VIII）。以下只记 DeepEP 现版 README 能核到的设计变化（[README](https://github.com/deepseek-ai/DeepEP/blob/main/README.md)「News」「New features」「Notes」「Requirements」各节）：

- **后端**：V2 是专家并行的整体重构，通信后端改为轻量的 NCCL GIN，提供设备侧通信 API，并可复用已有的 NCCL communicator；README 要求 NCCL 2.32.3 及以上。
- **统一 buffer**：高吞吐与低延迟两类接口合并为同一个 `EPBuffer`，并为分组专家 GEMM 提供展开布局。
- **资源配置**：通信所用的 SM 数与 QP 数改为解析式估算，不再需要自动调优，也可逐次调用覆盖。
- **规模与模式**：支持更大的 scale-up 与 scale-out 域；hybrid 与 direct 两种模式仍都支持。
- **编译方式**：通信 kernel 改由 DeepJIT 在运行时编译。
- **V2.5**：把原 `ElasticBuffer` 拆为 `EPBuffer`、`EngramBuffer`、`PPBuffer`、`BucketBuffer`；新增冗余专家权重经 NVLink 预取与梯度归并的接口；**完全移除 V1**（含其 API、NVSHMEM 后端与旧文档），NVSHMEM 不再是依赖。
- README 注明 EP 的 dispatch 与 combine 仍需占用 GPU SM，不支持零 SM 的 RDMA EP。

README 没有给出 V2 相对 V1 的性能数字，本篇因此不写倍数。V2 首次公开的提交在 2026-04-30，V2.5 的提交在 2026-09-29（仓库提交记录）。

## 七、意义

- **对编程模型**：专家并行这类数据依赖通信，需要「kernel 内发起、按拓扑分流」的一侧通信；NVSHMEM 提供了这种能力的通用库形态，NCCL 后来也吸收了同类概念。
- **对系统设计**：真正决定性能的是自建流水（两段转发、SM 分工、信用流控），通信库只提供原语；这与 NVIDIA 在 GIN 工作中把 DeepEP 后端换成 NCCL GIN、性能与 NVSHMEM 基线通常相差约 1–2% 的结果相符（主文 §VIII-C 转述；该数出自 NVIDIA 自己的 GIN 工作，不是 DeepEP V2 的实测）。DeepEP V2 随后正式把后端换成了 NCCL GIN（见第六节）。

## 八、局限与待核实

- **DeepEP V1 已从主分支移除**：主 README 写明已完全移除 V1、其 API、NVSHMEM 后端与旧文档，NVSHMEM 不再是依赖；V1 资料只剩 v1.2.1 标签。主文分析的正是 V1。
- **README 未给 V2 相对 V1 的性能数**：第六节只记设计变化；README 早先版本给过的倍数说法现版已删去，本篇不引用。
- **微基准口径**：§VII 数字只对 H200 + CX7 与 NVSHMEM 3.3.9 成立；V1 性能表是 H800，两表不可混比。
- **hybrid 与 direct 模式**：README 只写两种模式仍都支持，未解释两者的具体区别，待核实。
- **拓扑假设**：高吞吐路径按「每节点 8 GPU」建 team，换拓扑需改实现。
- **GIN 对比为转述**：约 1–2% 的差距来自 NVIDIA 自己的 GIN 工作，由主文 §VIII-C 转述，主文没有复测，也不是 DeepEP V2 的实测。
- **相关工作**：Hu 等对 NCCL 做了源码级拆解，Langer 等专讲动态对称堆；本篇未展开。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[AI基础设施总览]] | 总览讲跨节点专家并行的 all-to-all 可与算力同量级，本篇讲这类通信在设备侧怎么实现 | 基础设施通论 |
| [[混合专家架构]] | 那篇讲专家为何稀疏激活，本篇讲稀疏激活带来的 all-to-all 如何落到通信底层 | 路由损失、容量因子、MoE 史 |
| [[MoE路由与负载均衡]] | 那篇的路由决定每个 token 送往哪些专家、跨几个节点，也就决定了本篇 dispatch / combine 的 all-to-all 流量与失衡 | 路由算法与负载均衡损失 |
| [[DeepSeekV3训练与MoE基建]] | 那篇的「IB 到同 index GPU、再 NVLink 转发」正是 DeepEP 高吞吐路径的两段式 | DualPipe、FP8 配方、SM 配额 |
| [[DeepSeekV4技术报告深读]] | 那篇 §四 的专家并行细粒度重叠建在同类 dispatch/combine 之上，本篇讲其下层通信 | V4 的融合管线与 MegaMoE |
| [[MegaScaleInfer与UltraEP]] | 那篇的 M2N 库拿 DeepEP 作对照，UltraEP 集成的是 DeepEP 分支，本篇讲被对照与被集成的这一层 | 部署搜索、热度均衡 |
| [[硬件软件协同部署]] | 那篇讲 NVLink 域与互联代际，本篇讲在这种互联上怎样用设备侧通信走满带宽 | 硬件规格与选型 |
| **[[分布式训练并行策略]]** 训练并行总览 | 专家并行在五种并行中的位置：EP 与 PP、ZeRO 组合时每层两次 all-to-all，是本篇通信需求的来源 | 并行组合法则与流水线调度 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Demystifying NVSHMEM](https://arxiv.org/abs/2606.05951) §II–V | 对称堆、快慢路径的实现 |
| 2 | 同上 §VIII | DeepEP V1 两条路径的拆解 |
| 3 | [DeepEP v1.2.1 标签](https://github.com/deepseek-ai/DeepEP/tree/v1.2.1) | V1 接口与性能表 |
| 4 | [DeepEP README](https://github.com/deepseek-ai/DeepEP/blob/main/README.md) | V2 / V2.5 改用 NCCL GIN 后的设计 |
