---
title: "HiCache：层次化 KV 缓存（GPU / Host / 分布式存储三级）"
topic: HiCache层次化KV缓存
date: 2026-09-28
lines: [AI Infra, KV 缓存, 服务架构]
status: archived
sources:
  - https://www.lmsys.org/blog/2025-09-10-sglang-hicache/  # 主锚：LMSYS 博客
  - https://docs.sglang.ai/advanced_features/hicache_design.html  # 设计文档
  - https://kvcache-ai.github.io/Mooncake/performance/sglang/sglang-hicache-benchmark-results-v1.html  # 辅助：Mooncake 基准页
  - https://arxiv.org/abs/2312.07104  # 背景：SGLang 论文（RadixAttention）
related:
  - "PrefillDecode分离与统一服务"
  - "Prompt前缀缓存"
  - "推理引擎生态"
  - "KV缓存量化与压缩"
  - "AI基础设施总览"
retrieval_cutoff: 2026-09-28
timezone: Asia/Shanghai (CST)
boundary: "只讲 SGLang HiCache 的三级 KV 缓存层级、写回 / 预取策略及其与 Radix 前缀树的衔接；不写 PD 算力池化调度、不写 API 侧 Prompt Cache 计费、不做引擎选型、不写 KV 量化压缩。"
archived: 2026-09-28
---

# HiCache：层次化 KV 缓存（GPU / Host / 分布式存储三级）

> **主要来源**：[SGLang HiCache 博客（Zhiqiang Xie / LMSYS，2025-09-10）](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/)；[HiCache 设计文档](https://docs.sglang.ai/advanced_features/hicache_design.html)（无发布日期，按 2026-09-28 所见版本）；佐证：[Mooncake 的 HiCache 基准页](https://kvcache-ai.github.io/Mooncake/performance/sglang/sglang-hicache-benchmark-results-v1.html)（截至 2026-09-28）
> **研究线**：AI Infra / KV 缓存——三级各存什么、何时往下写、何时往上取、如何挂在同一棵前缀树上
> **范围与相邻笔记**：
> - ≠ [[PrefillDecode分离与统一服务]]：本篇不写 prefill / decode 算力分池。
> - ≠ [[Prompt前缀缓存]]：本篇不写模块化 Prompt Cache 与商业 API 计费。
> - ≠ [[KV缓存量化与压缩]]：本篇不写 KV 本身的量化压缩。
>
> **意义**：前缀复用的收益原本被 GPU 显存容量封顶；HiCache 把 RadixAttention 的前缀缓存扩到主机内存和分布式存储，用容量换命中率、用命中率换更少的 prefill 重算，让长上下文多轮与 agent 负载的历史 KV 不再被丢弃。

**一句话**：显存装不下的历史 KV 不丢，往下放；同前缀的请求再来时往上取，而不是重算。

---

## 一、问题背景：前缀复用被显存卡住

- RadixAttention 在 GPU 显存里缓存并复用前缀 KV；上下文越长、客户端越多、轮数越多，历史 KV 越多地被驱逐，命中率随之下降（博客 "Why Hierarchical KV Caching Matters"）。
- 未命中就要重算 prefill。博客引用的社区案例：Novita AI 的编码 agent 场景（Qwen3-Coder-480B），对话常超过 25K token、每会话约 8 轮；接入 HiCache + DeepSeek 3FS 后命中率从 40% 升到 80%，会话平均 TTFT 降 56%。

## 二、脉络：从分页 KV 到分层 KV

| 节点 | 解决什么 | 来源 |
|---|---|---|
| PagedAttention（vLLM） | KV 分页存放，放得下、碎片少 | [[推理引擎生态]] |
| RadixAttention（SGLang） | 用前缀树在 GPU 显存内自动跨请求复用 KV | [SGLang 论文](https://arxiv.org/abs/2312.07104) §3；[[推理引擎生态]] |
| Mooncake 等 KV 中心架构 | 把 KV 缓存当作可跨节点存取的资源 | [[PrefillDecode分离与统一服务]] 的交叉引用 |
| HiCache（2025-09） | 把前缀树的命中范围扩到主机内存与存储后端 | 博客 |

借鉴 CPU 三级缓存：GPU 显存当 L1，主机内存当 L2，分布式存储（Mooncake、3FS、NIXL、AIBrix KVCache 等）当 L3（文档 "Why and What is HiCache?"）。

## 三、三级缓存

| 层级 | 介质 | 共享范围 | 存什么 | 主要代价 |
|---|---|---|---|---|
| L1 | GPU 显存 | 单实例私有 | 当前计算需要的 KV 与热前缀；layer-first 布局 | 容量最小 |
| L2 | 主机内存 | 单实例私有，多机内存不能拼成一个 L2 | 从 L1 写下的 KV；可用 page-first 等 I/O 友好布局 | 依赖 CPU–GPU 带宽 |
| L3 | 存储后端（file、mooncake、3FS、nixl、aibrix 等） | 由后端决定，各实例指向同一命名空间时才是集群级共享 | 从 L2 写下的 KV，按页存 | 延迟高且不稳定，需要提前取 |

两点易误解（文档 "Tier Sharing Scope"）：实例 0 产生的 KV 只有到达 L3 后实例 1 才看得到；放大 L2 只是放大各实例自己的缓存，跨实例复用必须配存储后端。

## 四、核心机制：往下写与往上取

### 4.1 往下写（文档 "Data Write-back"）

| 策略 | 何时写到下一层 | 适用 |
|---|---|---|
| write_through | 每次访问立即写 | 带宽充足时收益最大 |
| write_through_selective | 访问次数超过阈值才写，只备份热点 | 想减少 I/O |
| write_back | 上层驱逐时才写 | 慢层容量也吃紧 |

- 总体口径是 prefill 完成后再把新 KV 存入 L2 或 L3。
- L2 → L3 只传 L3 中还没有的数据（去重）。
- MLA 模型各 TP rank 持有相同的完整 KV，只让一个 rank 写回，避免重复存储。

### 4.2 往上取

两段上行路径按延迟特性区别对待（博客 "Versatile control plane"）：

- **L2 → L1 逐层重叠**：prefill 计算第 N 层时加载第 N+1 层的 KV，把传输藏在计算后面。
- **L3 → L2 机会式预取**：L3 命中长度超过阈值（默认 256 token）才触发（文档 "Prefetch from L3"）。

预取何时停有三种策略：best_effort（GPU 可以开始 prefill 就停）、wait_complete（等全部取完）、timeout（超时或完成即停，文档推荐用于生产）。timeout 的时长随待取 token 数线性增长并有上限（默认 base 2 秒、每 1024 token 加 0.1 秒、最多 30 秒）。

## 五、与前缀树的衔接：HiRadixTree

- HiRadixTree 沿用 RadixTree 结构，但每个节点额外记录这段 KV 在哪一层（GPU、CPU、L3 或多层）；博客称它相当于一张「页表」。
- L1/L2 的数据保存精确地址；L3 的元数据不存也不持续同步，访问时实时询问后端，以降低开销。
- 本地匹配只遍历树、不拷数据，返回一个连续前缀：前段在 L1、后段在 L2（文档 "Local Match"）。

所以三级缓存没有另起一套索引：前缀树仍是唯一入口，节点上多了一个「住在哪一层」的标记。

**请求的数据流**：

1. **匹配**：在 HiRadixTree 上找最长前缀，得到 L1 段 + L2 段。
2. **查 L3**：剩余部分向 L3 查询连续命中长度，超过阈值则预取到 L2。
3. **收口**：按预取策略决定等多久；停下后，已取到的部分与 L1/L2 数据合并。
4. **上载**：L2 中的 KV 在 prefill 中逐层重叠加载到 GPU；取不到的部分重算。
5. **写回**：prefill 完成后按写回策略写到 L2、L3。
6. **驱逐**：L1 不足时驱逐旧 KV；write_back 下驱逐正是写下的时机。材料未展开驱逐算法。

多卡时各 rank 的判断须一致：预取前后各用一次 all_reduce(min) 统一 L3 命中数与实际取回长度（文档 "Multi-Rank Synchronization"）。

## 六、工程要点与效果

- **布局**：GPU 保持 layer-first 以兼容计算内核，L2/L3 改用 page-first，同一页的 KV 连续存放、单次传得更多；博客称结合零拷贝，主机内存与存储层之间的传输吞吐最高提升 2×。
- **传输内核**：专为 KV 传输写的 GPU 辅助 I/O 内核，CPU–GPU 传输吞吐最高提升 3×。
- **页大小取舍**：页越大元数据越少、存储 I/O 越高效，但部分匹配时命中率可能下降；长公共前缀适合大页。
- **后端接口**：后端只需实现 get / exist / set 三个操作，调度与同步由中心缓存控制器负责；LMCache 是另一种替代方案。
- **与 PD 分离**：HiCache 可同时在 prefill 与 decode 节点启用，decode 节点的输出也会写回 L3（文档）；博客引用蚂蚁集团在 PD 分离下测 DeepSeek-R1-671B，命中相对完全重算平均降低 84% TTFT。
- **效果**：博客自测在长上下文和多轮对话基准上吞吐最高提升 6×、TTFT 最高降低 80%；Mooncake 基准页显示，轮数增加、KV 超出 L2 容量后，只有 L2 的配置命中率下降、TTFT 上升，接 Mooncake 的配置保持高命中率。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[推理引擎生态]] | 那篇讲 RadixAttention 的前缀复用与选型，本篇讲把这一复用扩到显存之外 | 引擎横向选型 |
| [[PrefillDecode分离与统一服务]] | 那篇讲 prefill / decode 是否分池，本篇讲 KV 放在哪一层，两者可叠加（见第六节） | 分池调度 |
| [[Prompt前缀缓存]] | 那篇讲模块化 Prompt Cache 与云 API 的缓存计费，同样是复用前缀 KV，本篇在引擎内部做 | 计费字段 |
| [[KV缓存量化与压缩]] | 那篇减少每条 KV 的字节数，本篇扩大能存 KV 的空间，两者正交 | 量化方法 |
| [[AI基础设施总览]] | 那篇讲 PagedAttention 等 serving 基础，本篇是其上的存储层级扩展 | serving 通论 |

## 八、局限与待核实

- **来源性质**：主要依据是团队博客与持续更新的设计文档，不是同行评审论文；文档无发布日期，参数默认值可能随版本变化。
- **效果数字多为自测或转引**：6×、80%、56%、84% 来自博客自测或博客引用的社区案例，测试负载与硬件未统一公开，不宜横向比较。
- **驱逐算法未展开**：材料没有给出 L1 / L2 驱逐的具体策略。
- **L3 依赖后端**：跨实例共享、延迟与一致性都取决于所接的存储后端，本篇未比较各后端。
- **与 PD 分离的协同仍在进行**：博客写明这部分设计尚未完成。

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [HiCache 博客](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/) | 动机与总体设计 |
| 2 | [HiCache 设计文档](https://docs.sglang.ai/advanced_features/hicache_design.html) | 写回、预取、多 rank 同步的定义 |
| 3 | [SGLang 论文](https://arxiv.org/abs/2312.07104) §3 | RadixAttention 原始设计 |
| 4 | [Mooncake 基准页](https://kvcache-ai.github.io/Mooncake/performance/sglang/sglang-hicache-benchmark-results-v1.html) | L3 在多轮负载下的作用 |
