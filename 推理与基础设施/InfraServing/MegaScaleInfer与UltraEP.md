---
title: "Sparse MoE 服务系统：MegaScale-Infer + UltraEP（≠ MoE 架构通史 / ≠ DeepEP 通信）"
topic: MegaScaleInfer与UltraEP
date: 2026-09-22
lines: [AI Infra, 服务架构]
status: archived
sources:
 - https://arxiv.org/abs/2504.02263
 - https://arxiv.org/abs/2606.04101
arxiv: ["2504.02263", "2606.04101"]
related:
 - "混合专家架构"
 - "NVSHMEM与DeepEP通信"
 - "推理引擎生态"
 - "DeepSeekV3训练与MoE基建"
 - "AI基础设施总览"
 - "PrefillDecode分离与统一服务"
 - "硬件软件协同部署"
 - "MoE路由与负载均衡"
 - "分布式训练并行策略"
note_deepep: "DeepEP 无独立 arXiv 主文；本篇仅作集成/对照接口一句；内核分析见 NVSHMEM与DeepEP通信"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# Sparse MoE 服务系统：MegaScale-Infer + UltraEP（≠ MoE 架构通史 / ≠ DeepEP 通信）

> **主要来源**：[MegaScale-Infer（Zhu, Jiang, Jin 等，ByteDance Seed / PKU）](https://arxiv.org/abs/2504.02263)，v4 2025-07-26；[UltraEP（Wei, Jin, Dai 等，PKU / 小红书 / 上海 AI Lab 等）](https://arxiv.org/abs/2606.04101)，v3 2026-06-18（截至 2026-09-22）
> **研究线**：AI Infra / 服务架构（主）——稀疏 MoE 在服务与训练中如何摆放注意力与专家、如何实时均衡负载；文内吞吐与失衡字段（辅）
> **范围与相邻笔记**：
> - ≠ [[混合专家架构]]：本篇不写路由公式与 MoE 通史，稀疏只当「每个专家分到的 token 变少 → 利用率塌」一句接口。
> - ≠ [[NVSHMEM与DeepEP通信]]：本篇不写 NVSHMEM 与 DeepEP 内核，DeepEP 只出现在对照与集成句里。
> - ≠ [[推理引擎生态]]：本篇不写引擎选型，vLLM、SGLang 等只作评测基线。
>
> **意义**：MoE 的稀疏让专家计算在 decode 时吃不饱、在大专家并行时负载随层和微批剧烈漂移；MegaScale-Infer 用「注意力与专家分机 + 乒乓流水」解决前者，UltraEP 用「门控后按精确负载实时复制热专家」解决后者，两者合起来说明 MoE 的服务成本主要由系统摆放与均衡决定，而不只是模型结构。

**一句话**：MegaScale-Infer 把注意力复制、专家切开、用微批乒乓填空闲；UltraEP 在机架级高带宽域内，按每层每个微批的真实负载当场复制和重路由。

---

## 一、问题背景

**稀疏饿死专家（MegaScale-Infer §1–2）**：decode 主导服务成本。稠密模型增大 batch 就能让 FFN 吃满算力；MoE 在同样 batch 下，每个专家分到的 token 约为 B × topk / 专家数，稀疏度越高专家侧利用率越低；内存与 TBT SLO 又限制了全局 batch。

**历史均衡跟不上（UltraEP §1–3）**：32/64 路专家并行已是百亿到千亿 MoE 的常见配置，专家负载不均会放大为算力掉队、all-to-all 瓶颈和激活内存尖峰。EPLB 类方案按历史负载周期性重排并冗余复制，但训练和 prefill 中热专家随数据域、层、微批剧变，陈旧布局残留失衡。路由侧的辅助损失与 bias 能稳定训练，却不能保证每个微批的实际负载均衡——UltraEP 站在系统侧补这一层。

## 二、脉络：从拆阶段到拆模块

| 节点 | 拆什么 | 来源 |
|---|---|---|
| PD 分离（DistServe 等） | prefill 与 decode 分池 | [[PrefillDecode分离与统一服务]] |
| Infinite-LLM 式拆注意力 | 稠密长上下文把注意力单独拆出；MegaScale-Infer 指出对 MoE 的 token 稀疏帮助有限 | MegaScale-Infer §1–2 |
| MegaScale-Infer（2025） | 层内拆：注意力节点与专家节点分置 | MegaScale-Infer |
| EPLB 类均衡 | 按历史负载周期性复制热专家 | UltraEP §1–3 |
| UltraEP（2026） | 门控后按精确负载逐层、逐微批复制与重路由，依赖机架级 scale-up 域 | UltraEP §4–6 |

## 三、MegaScale-Infer：解耦专家并行

### 3.1 注意力与专家分机

- **注意力节点**：数据并行复制，存权重与 KV。
- **专家节点**：专家并行切分。
- **异构部署**：注意力选带宽与容量性价比高的卡（文例 H20），专家选算力性价比高的卡（文例 L40S）。
- 论文主写 decode；运行时另接 prefill / decode 分簇。

### 3.2 乒乓流水（§4.1）

解耦后一侧计算时另一侧空闲，还要等跨节点结果。做法是把全局 batch 切成 m 个微批，在注意力与专家之间乒乓。成立条件：

1. 注意力与专家每微批耗时接近（T_a ≈ T_e）；
2. 通信能被计算盖住（T_c < max(T_a, T_e)）；
3. m 足够大以填满流水，通常快网 m≥3、慢网 m≥4；论文把搜索上限设为 4，切太碎会伤专家 GEMM。

### 3.3 部署搜索（Alg.1）

枚举两侧的张量并行度、按剖面平衡注意力节点数、再扫 m，在 TBT SLO（文设 150 ms）与 KV 内存约束下最大化单位成本吞吐。

### 3.4 M2N 通信库（§5）

解耦后 all-to-all 变成 M 个注意力 GPU 与 N 个专家 GPU 之间的 M2N。NCCL 点对点在这种模式下中位与尾延迟偏高，于是自写约 4900/5000 行的通信库：去掉多余的 GPU→CPU 拷贝、group 初始化与同步，用 RDMA write with immediate 传数据。相对 NCCL：吞吐 4.2×，中位延迟降 68.2%，尾延迟降 92.9%。

与 DeepEP 的一句对照（§6）：MegaScale-Infer 跨节点通信由 CPU 侧驱动以省 GPU SM，DeepEP 走 GPU–GPU。

### 3.5 结果（§7）

| 项 | 结果（论文口径） |
|---|---|
| 模型 | Mixtral-8×22B、DBRX、Scaled-MoE（约 317B） |
| 负载 | 生产 trace，中位输入 / 输出 571 / 159 token |
| 每 GPU decode 吞吐 | 相对 vLLM / TensorRT-LLM 最高约 2.56× / 1.28×；Scaled-MoE 上 7.11× / 1.90× |
| 异构单位成本 | 相对 H20 上的基线最高约 3.24× / 1.86× |
| 端到端（含 prefill） | 最高约 1.18×，prefill 偏算力，增益淡 |
| 生产 | 作者称已部署，同流量成本降约 1.5–2.0× |

## 四、UltraEP：门控后精确负载均衡

### 4.1 为何需要机架级节点（RSN）

标准集群的 scale-up 多止于 4/8 GPU，跨节点迁移专家状态对关键路径太贵。RSN 把 scale-up 扩到整机架（文称常为 64 块以上 GPU），专家并行组落在高带宽域内，门控后实时均衡才可行；摘要称关键路径上暴露的开销约 0.3 ms。范围限定为训练与 prefill；decode 受内存束缚，算力失衡被稀释，不作主目标。

### 4.2 只复制、不迁移（§4.1）

每个 rank 固定若干主槽与冗余槽；主专家不迁移，冗余槽不带优化器状态，权重与梯度缓冲跨层复用。Qwen3-235B-A22B 例：单个冗余槽每 rank 从 3.3 GB 权重 + 6.6 GB 梯度压到 **36 MB + 72 MB**。反向时副本梯度规约回主专家，保持训练等价。

### 4.3 配额驱动规划（Alg.1）

不再「先放副本、再启发式重路由」，而是直接求每个物理实例的最终负载配额：二分找最小负载阈值（目标系数 β=1.01），贪心把过载 rank 的负载转给余量最大的 rank（单次转移至少 1024 token），再按配额重路由 token。全程在 GPU 上执行，避免主机往返。

### 4.4 复制通信（§6）

专家复制流量稀疏且逐层变化，不是静态集合。用持久核按 tile 流式传权重与梯度；副本数超过 4 的热专家建两级中继树分摊扇出。相对 torch.distributed 与 DeepEP，专家复制加速 3.1–5.5×。token 的 dispatch/combine 仍接 DeepEP（hybrid-ep 分支，v1.2.1+7febc6e）。

### 4.5 结果

| 项 | 结果（论文口径） |
|---|---|
| 规模 | 最多 256 GPU，106B–671B 参数；每机架 64 GPU |
| 贴近理想吞吐 | 训练平均 94.6%，prefill 平均 93.9%，摘要跨设定 94.3% |
| 相对无均衡 | 1.49× |
| 相对框架 | 训练相对 Megatron-LM 1.42×，prefill 相对 SGLang 1.56× |
| 失衡度 | 均衡后 rank 间约 1.01–1.04，无均衡时 1.30–4.01 |
| 均衡方案对比（相对 Megatron 训练增益） | EPLB +20%、LPLB +12%、EPLB+ +29%、UltraEP +42% |
| 生产 | 作者称长期保持在理想值 92% 以上 |

## 五、两篇对照

| 问题 | MegaScale-Infer | UltraEP |
|---|---|---|
| 主场景 | decode 服务与异构成本 | 训练与 prefill |
| 通信对象 | 激活与 token（M↔N） | 专家权重与梯度的复制 |
| 负载策略 | 周期性冗余专家 + 部署搜索 | 门控后逐层、逐微批精确均衡 |
| 硬件假设 | 多节点 IB，可选异构 GPU | 机架级 scale-up 域 |
| 与 DeepEP | 一句 CPU 驱动 vs GPU–GPU 的对照 | token 路径集成，复制带宽对照 |

## 六、意义

- **解耦的粒度在变细**：从 prefill / decode 分池，到层内注意力与专家分机；每次拆分都让两侧按各自瓶颈（带宽或算力）选硬件、定并行度。
- **均衡从统计走向实时**：机架级高带宽域让「看到真实负载再决定复制」变得负担得起，这是 UltraEP 能贴近理想吞吐的前提。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[混合专家架构]] | 那篇讲专家为何稀疏激活，本篇讲稀疏激活在服务与训练系统里造成的利用率与均衡问题 | 路由公式、MoE 史 |
| [[MoE路由与负载均衡]] | 那篇在训练中用辅助损失或无辅助损失偏置压均专家负载；本篇在系统层接手路由之后的问题：UltraEP 在线复制热门专家，把残留的秩间失衡从无均衡时的 1.30–4.01 压到 1.01–1.04，MegaScale-Infer 解耦注意力与专家以抬高专家侧批量 | 路由器设计与均衡损失 |
| [[NVSHMEM与DeepEP通信]] | 那篇剖析的 DeepEP 是 MegaScale-Infer 的对照对象、UltraEP 的 token 通信后端 | NVSHMEM 与 DeepEP 内核 |
| [[DeepSeekV3训练与MoE基建]] | 那篇有 V3 的冗余专家与 all-to-all 安排，本篇的两套系统针对同类问题给出服务侧与训练侧方案 | V3 报告配方 |
| [[分布式训练并行策略]] | 那篇讲专家并行在五种并行中的位置；UltraEP 的训练实验正是 EP64 与 DP、PP 的组合（Table 2），本篇只讲其中专家并行内部的负载均衡，MegaScale-Infer 则是推理侧的专家并行部署 | 并行组合法则与流水线调度 |
| [[PrefillDecode分离与统一服务]] | 那篇讲 prefill / decode 分池，MegaScale-Infer 在此基础上进一步拆开层内的注意力与专家 | PD 分离调度 |
| [[硬件软件协同部署]] | 那篇讲带宽、精度、互联三轴，MegaScale-Infer 按「注意力吃带宽、专家吃算力」选异构卡正是这一逻辑的应用 | 硬件规格 |
| [[推理引擎生态]] | 那篇的 vLLM、SGLang、TensorRT-LLM 在本篇只作基线 | 引擎选型 |
| [[AI基础设施总览]] | 那篇讲专家并行的 all-to-all 可与算力同量级，本篇讲如何在系统层面摊平它 | 基础设施通论 |

## 八、局限与待核实

- **部署与生产数字为自述**：MegaScale-Infer 的成本降 1.5–2.0×、UltraEP 的长期 92% 以上都来自作者部署段，无第三方复现。
- **硬件前提强**：UltraEP 依赖机架级 scale-up 域，标准 8 卡节点集群上不适用；MegaScale-Infer 的异构结论只对所测机型成立，不外推。
- **场景范围**：MegaScale-Infer 主写 decode，端到端增益只有约 1.18×；UltraEP 不针对 decode。
- **基线时效**：两文的 vLLM、SGLang、TensorRT-LLM 基线版本随时间变化，倍数不宜与其他论文直接比较。
- **DeepEP 版本**：UltraEP 集成的是 DeepEP 的 hybrid-ep 分支（v1.2.1 系），DeepEP 主分支现已改为 V2，集成状态待核实。

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [MegaScale-Infer](https://arxiv.org/abs/2504.02263) §4–5 | 乒乓流水条件与 M2N 库 |
| 2 | 同上 Alg.1、§7 | 部署搜索与异构成本 |
| 3 | [UltraEP](https://arxiv.org/abs/2606.04101) §4 与 Alg.1 | 冗余槽设计与配额规划 |
| 4 | 同上 §6 与评测部分 | 复制通信与评测 |
