---
title: "分布式集合通信 Demystifying NVSHMEM（DeepEP 案例）"
topic: NVSHMEM与DeepEP通信
date: 2026-09-22
lines: [AI Infra, 架构思想]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2606.05951 # 824K / 12p；主文
 - https://github.com/deepseek-ai/DeepEP # 工程辅：README + docs/legacy.md（V1）
arxiv: ["2606.05951"]
related: ["AI基础设施总览", "混合专家架构", "DeepSeekV3训练与MoE基建"]
github_deepep: "https://github.com/deepseek-ai/DeepEP"
note_deepep_arxiv: "DeepEP 无独立 arXiv 主文；主文以 GitHub [33] 引用；禁止虚构 DeepEP paper arXiv 号"
---

# 分布式集合通信 Demystifying NVSHMEM（DeepEP 案例）

> **定位**：**P1 Infra / 通信横切**——立「**GPU 端发起、对称内存、一侧 put/get**」这条与 **NCCL 主机侧集体**互补的通信模型。主文是 Ma / Shen / Chen 等 *Demystifying NVSHMEM*（arXiv:**2606.05951**）；**DeepEP** 仅作主文 §VIII 案例 + GitHub 工程辅读（README / `docs/legacy.md`），**不是**本卡第二篇论文。
> **攻坚线**：**AI Infra（主）**——对称堆、P2P 快路径 / IBGDA 慢路径、设备侧集体与 LL/LL128；**架构思想（辅）**——为何稀疏 EP 的数据依赖 all-to-all 更适合在 NVSHMEM 基底上自建 dispatch/combine，而不是直接套现成集体。
> **硬划界（开篇钉死）**：
> - **≠ [[AI基础设施总览]]**：不写 Megatron TP/PP/DP 通论、FlashAttention、PagedAttention、FP8 训练栈全文；本卡只取「通信库 / 设备侧 RMA」一层。
> - **≠ [[混合专家架构]]**：不写 Switch→Mixtral→V3 的 MoE **路由/稀疏史线**（总参 vs 激活参、aux-loss、$M=4$ 等）；EP 只当「专家切分 → 稀疏 all-to-all」接口一句。
> - **≠ [[DeepSeekV3训练与MoE基建]] / [[DeepSeekV4技术报告深读]] 通信小节全文重写**：不重写 DualPipe 气泡表、20 SM / 3.2 experts/node、dispatch 前 FP8 / combine BF16 等 **报告配方轴**；本卡只跟 NVSHMEM 运行时如何被 DeepEP **调用**，以及 HT/LL 内核如何叠在对称堆与 IBGDA 上。
> **硬约束**：**DeepEP 无独立 arXiv 主文**——引用只写 `github.com/deepseek-ai/DeepEP`（主文 References [33]）；**禁止虚构** DeepEP paper arXiv 号。主文分析对象为 **DeepEP V1（NVSHMEM）**；V2 已切 **NCCL Gin**，本卡只点一句边界，不升主轴。
> **禁止编造**：带宽、延迟、算法名一律锚定官方 PDF（2026-09-22 CST）与公开 README/legacy；未在源出现的对比表不写。
> **入库体积**（`ls -lh`）：主 PDF **824K** ≪ **20MB** → **可入库**；无权重 / 数据集 / 视频。

---

## 一、材料元信息与 PDF 体积

| 角色 | 材料 | 标识 / 路径 | 体积 / 页 | 备注 |
|---|---|---|---|---|
| **主文** | Ma, Shen\*, Chen 等（ETH Zürich + NVIDIA），*Demystifying NVSHMEM: A System-Level Analysis on Symmetric Memory and Device-Initiated Operations in GPU Communication* | arXiv:**2606.05951v1** \[cs.DC\]（**4 Jun 2026**）；`https://arxiv.org/abs/2606.05951` | **824K**（843,450 B）；**12** 页 | 分析目标库版本：**NVSHMEM 3.3.9** |
| **抽取** | | | ~112K 文本 | 跟读用 |
| **工程辅** | DeepSeek-AI，*DeepEP: an efficient expert-parallel communication library* | **仅 GitHub**：https://github.com/deepseek-ai/DeepEP ；Citation bibtex `publisher = {GitHub}` | — | **无独立 arXiv**；主文以 GitHub 引用为 [33] |
| **辅读切片** | DeepEP **V1 legacy**（NVSHMEM 后端） | `docs/legacy.md`（仓内） | — | 与主文 §VIII「聚焦 V1」对齐；主 README 现以 **V2 / NCCL Gin** 为主 |

**体积判定**：主 PDF **824K < 20MB**，按规矩 **二进制可入库**。DeepEP 为开源仓，不下载整仓权重或二进制工件。

**一句话抓手：**
- **NVSHMEM** = 把 OpenSHMEM/PGAS 的 **对称堆 + 一侧 RMA** 直接暴露给 **CUDA 线程/warp/block**，补 NCCL「主机发起集体」不擅长的细粒度、数据依赖通信。
- **DeepEP V1** = 在 EP 的稀疏 dispatch/combine 上，**仅在跨节点 RDMA 关键点**调用 NVSHMEM（尤其 IBGDA put / atomic），其余流水与 warp 分工自建。
- **V2** = 后端改 NCCL Gin；主文明确「beyond scope」——本卡也不展开。

---

## 二、议题边界：只写「NVSHMEM 怎么实现 + DeepEP 怎么用它」

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[AI基础设施总览]]** AI Infra「势」 | 「算力—通信—显存」链上的 **通信库** 一环；NCCL 作对照基线一句 | Megatron 列/行切、FA2、vLLM 分页、FP8 配方全文 |
| **[[混合专家架构]]** MoE 稀疏史 | EP = 专家分片 → 每层 **数据依赖 all-to-all** | Switch/Mixtral/V3 路由损失、容量因子、总参/激活参通史 |
| **[[DeepSeekV3训练与MoE基建]]** | DualPipe chunk 里「all-to-all dispatch/combine」是 **调度动机**；DeepEP 对齐 group-limited gating 的工程实现 | DualPipe 气泡公式表、训练超参、FP8 块量化细则、报告通信小节全文重写 |
| **[[DeepSeekV4技术报告深读]]** | 同左：不整节搬通信配方 | 同上 |

### 2.2 本卡主轴

`
问题：细粒度 / 不规则 / GPU 内发起的通信，NCCL 主机集体不够用
 ↓
NVSHMEM：对称内存 + 一侧 put/get/atomic + 设备侧集体
 ↓
实现：VMM 对称堆 → P2P 快路径 / IBGDA·proxy 慢路径 → pSync + LL/LL128
 ↓
案例：DeepEP V1 在 HT/LL 两路上把 NVSHMEM 当「跨节点 RDMA 基底」
`

---

## 三、背景：为何需要「设备发起」的 PGAS（主文 §I–II）

### 3.1 NCCL 强项与缺口

- **NCCL** 是 CUDA 分布式 ML 的默认集体后端（PyTorch / Megatron / vLLM 等）；传统接口是 **主机发起**：CPU 入队集体，再调度 NCCL kernel 到 stream。
- 对 **规则、大批量同步集体** 极强；但对 **细粒度点对点**、**数据依赖子集通信**、**与计算紧耦合的自定义核**（stencil、不规则图、稀疏 EP）不够自然——主机协调开销与控制粒度成为瓶颈。

### 3.2 NVSHMEM 补位

- 基于 **OpenSHMEM / PGAS**：逻辑上共享、物理上按 **PE（processing element）** 分区的地址空间。
- 每个 PE 通常对应一进程映一 GPU（≥2.4.1 有限支持多 PE/GPU）。
- 核心原语：**对称对象**（各 PE 同类型/大小/布局）上的 **一侧 put/get、atomic、显式同步**；CUDA kernel 内可直接发起。
- **不是**取代 NCCL，而是互补；主文亦指出 NCCL 后续经 **Device API / 对称内存 / GIN** 吸收了部分 NVSHMEM 先发概念，但抽象不同：NVSHMEM 偏 **平坦远程内存视图**，NCCL 更强调 **scale-up vs scale-out** 与 communicator 层级。

### 3.3 关键术语（跟读词典）

| 术语 | 含义（主文口径） |
|---|---|
| **P2P（GPU）** | 一 GPU 直接访问另一 GPU 内存（常 NVLink/NVSwitch；可含 MNNVL） |
| **GDRDMA** | NIC 直接读写 GPU 内存（scale-out） |
| **GDA-KI / IBGDA** | GPU kernel **发起并控制** 网络操作、绕过 CPU proxy；IB 上的实现称 **IBGDA** |
| **一侧通信** | 发起方指定源/目的，目标无需匹配 recv（类 MPI RMA，接口更轻） |

---

## 四、编程模型速览：Team、双接口、API 族（§III）

### 4.1 Teams

- Team = PE 子集的轻量句柄（可带拓扑信息）；默认 `NVSHMEM_TEAM_WORLD`。
- **与 MPI/NCCL communicator 不同**：team **不**承载大部分通信运行时状态；集体内部资源（如 `pSync`）按 team 绑定。
- **约束**：同一 PE 上 **不可**对同一 team 并发发起多个集体（内部同步/scratch 单套）。

### 4.2 双接口与命名

| 前缀 | 含义 |
|---|---|
| `nvshmem_` | 标准 OpenSHMEM 风格 API |
| `nvshmemx_` | 扩展（stream 序、warp/block 作用域等） |
| `nvshmemi_` | 内部实现（非公开） |

设备侧按 **作用域**：默认 **thread**；`nvshmemx_` 另有 **`_warp` / `_block`**。主机侧另有 **`_on_stream`**。

### 4.3 API 分组（Table I 压缩）

| 组 | 主机/设备 | 作用 |
|---|---|---|
| Setup / exit | 混合 | init/finalize、bootstrap（MPI 或 unique ID） |
| Memory management | **主机** | `malloc`/`align`/`free`、部分本地 buffer 注册 |
| Team management | 混合（创建偏主机） | 子团队、PE 翻译 |
| One-sided RMA | **双端** | put/get、scalar p/g、strided、非阻塞 |
| Atomics | **双端** | fetch/add/CAS 等 |
| Memory ordering | **双端** | `fence`（同目的序）/ `quiet`（完成可见） |
| Synchronization | 偏设备 | wait/test、基于对称对象/信号 |
| Collectives | **双端** | Barrier、Broadcast、AlltoAll、FCollect、Reduce、ReduceScatter 等 |

**跟读口诀：**能放进 kernel 热路径的是 **RMA + atomic + quiet/wait**；堆布局与 team 创建仍走 **主机集体分配**。

---

## 五、对称内存：VMM 堆与远程地址公式（§IV）

### 5.1 设计要点

- 默认用 CUDA **VMM**：`init` 时 **eager 预留 VA**，物理页 **按需提交**。
- 每 PE 预留连续 VA，长度约 `p2p_npes_ × heap_size_`：第一段本地堆，其余段留给 **P2P 可映射 peer** 的固定偏移映射。
- 非 P2P peer：另表 `peer_heap_base_remote_[]` + 传输层句柄（慢路径）。

### 5.2 分配与增长（Fig.1 五步，意译）

触发堆增长时大致：`cuMemCreate` → `cuMemMap`/`SetAccess` → 注册 P2P → 插入 `mspace` → 注册网络传输；再交换句柄并 barrier。主机侧分配器刻意简单（first-fit、`std::map` 管理空闲块），因分配多发生在初始化。

### 5.3 远程地址（核心公式）

对本地对称指针 `dest_local`，远程地址保持 **堆内偏移不变**：

$$
\texttt{dest\_remote}
=
\texttt{peer\_heap\_base\_p2p\_[remote\_pe]}
+
(\texttt{dest\_local}-\texttt{heap\_base\_})
$$

非 P2P 时换用 `peer_heap_base_remote_[remote_pe]`，并把地址交给传输层。**快路径**上 GPU 可对映射后的 VA 直接 LD/ST；这与主机 `cudaMemcpyAsync` 的 copy-engine 路径要分开理解。

---

## 六、一侧通信：快路径 vs 慢路径（§V）

### 6.1 快路径（P2P 直接访存）

- 主机侧判定：同主机、CUDA peer 可见、`cudaDeviceCanAccessPeer` 等通过后，填充 `peer_heap_base_p2p_[pe]`。
- **设备 RMA**：标量 `p`/`g`、bulk put/get 退化为对公式地址的 store/load 或 threadgroup memcpy。
- **主机 RMA**：走 `cudaMemcpyAsync` 等，基于同一映射。

### 6.2 慢路径（IBGDA 或 CPU proxy）

- 用于跨节点或不可 P2P 的 peer。
- 传输可插拔：IBRC / IBDEVX、UCX、libfabric 等；IB 上常见 RC QP，IBGDA 另支持 DC。
- **设备侧**：优先 `nvshmemi_ibgda_*`——GPU 直接构造/提交 RDMA；否则写 **pinned proxy 描述符**，由主机 proxy 线程代发。
- **语义**：API 仍是 GPU 发起，但完成可能由 **NIC（IBGDA）** 或 **主机 proxy** 驱动。

**跟读抓手：**DeepEP 跨节点热路径点名的是 **`nvshmemi_ibgda_put_nbi_warp`** 与 **`nvshmemi_ibgda_amo_nonfetch_add`**（§VIII）——正是慢路径里「设备直打 NIC」的那一支。

---

## 七、集体：pSync、LL/LL128、算法选择与 multi-CTA 短板（§VI）

### 7.1 pSync

每 team 一块对称 **persistent synchronization** 区；跨 team 跨 cache line 步幅布局；集体类型用硬编码子偏移；部分操作双缓冲以免次次 barrier。

### 7.2 LL / LL128

对齐 NCCL 思路：小消息把 **数据与到达旗** 打在同一原子写里，减少显式同步。
- **LL**：两数据 + 两旗 → 16B 原子写。
- **LL128**：120B 数据 + 8B 旗 → 128B；依赖 128B 原子存储，**主要安全于 NVLink**，PCIe 等不一般保证。

### 7.3 算法与 multi-CTA

- Table II 汇总 Broadcast / AlltoAll / FCollect / Reduce / ReduceScatter 的多种算法量级（含 NVLS one/two-shot、k-ary 等）；运行时用 **规则树**（能力、类型、scratch、消息阈值）选型，而非解析性能模型。
- 设备集体 API 是 **单 threadgroup** 参与一次调用；**无公开 `_grid`**——跨 CTA 同步更贵，且与「一 team 一套 pSync」冲突。
- 内建 multi-CTA 主要经主机 **`_on_stream`**，且仅部分集体；首次调用时 `team_dups[]` 复制 team。性能上 multi-CTA + NVLS 对 AllReduce **至关重要**（见下节）。

### 7.4 Barrier vs Sync

二者同为 dissemination（深度 $\log_k N$）；**barrier** 额外在进入前做 `quiet` / `__threadfence_system` 等，完成与可见性更强。

---

## 八、微基准摘录（§VII；仅照录）

**平台（文内）：** CoreWeave **H200**（8×H200 SXM5 / 节点，NVLink-4，~900 GB/s 双向/GPU，NVLS）；跨节点 **CX7 IB**，8 NIC/节点；CUDA 13.0.88；**NVSHMEM 3.3.9**。

### 8.1 设备一侧 RMA（Fig.4）

| 场景 | 指标（文内） |
|---|---|
| 节点内 bulk **put** | 峰 **313 GB/s** |
| 节点内 bulk **get** | 峰 **141 GB/s** |
| 节点内 scalar **p** | 峰 **172 GB/s**（多线程独立远程 store 可重叠） |
| 节点内 scalar **g** | **< 9 GB/s**（依赖返回值 → 难深度流水） |
| 跨节点 IBGDA bulk put/get | ~**48.0 / 48.2 GB/s**（逼近单轨 IB 参考） |
| 跨节点 scalar p / g | 峰 **15.6 / 1.28 GB/s** |
| 小消息延迟量级 | 节点内 bulk ~**1.8–2.5 µs**；IBGDA 跨节点 put/get 约 **9.4–9.7 µs**（256B–64KiB） |

文内结论：**bulk / 聚合写风格 RMA** 最有效；标量更宜作延迟/控制原语并批处理。均低于 450 GB/s NVLink 参考——归因于地址翻译、同步、划分与协议开销。

### 8.2 AllReduce（Fig.5）

| 路径 | 节点内算法带宽峰（文内） |
|---|---|
| NVSHMEM **on-stream**（multi-CTA + NVLS） | **264 GB/s** |
| NCCL **NVLS** | **276 GB/s** |
| NVSHMEM **device block**（单 CTA） | 仅 **~30 GB/s** |
| 跨节点 | NVSHMEM 变体 **< 0.20 GB/s**；NCCL ring / NVLS Tree 达 **180 / 252 GB/s** |

解读（主文）：NVSHMEM 集体优化重心在 **节点内 / MNNVL + NVLS**；跨节点集体不是其当前长板。小消息上设备路径节点内延迟仍可与 NCCL 竞争（约 **3.8–7.1 µs** vs ring **4.7–8.9 µs** 等）。

---

## 九、案例：DeepEP 如何「薄用」NVSHMEM（§VIII + GitHub 辅）

> **再次钉死：**DeepEP **没有**独立 arXiv 主文。下列机制描述以 **2606.05951 §VIII** 为准；带宽表与 API 形态以 GitHub **README / `docs/legacy.md`** 为辅，不编造论文号。

### 9.1 问题形态

- MoE **专家并行（EP）**：每层专家分片到多 GPU；token 经路由 **dispatch** 到专家，算完再 **combine** 回原 rank。
- 两阶段都是 **稀疏、数据依赖的 all-to-all**——现成集体库难以高效表达。
- DeepEP：自定义 dispatch/combine kernel；**跨节点 RDMA 基底**在 V1 上为 **NVSHMEM**。

### 9.2 主文范围：V1 only

- **HT（high-throughput）**：训练 / 大 token，偏带宽。
- **LL（low-latency）**：推理解码，偏层延迟。
- **V2**：README 写明改 **NCCL Gin**、统一 `ElasticBuffer`、更大 EP 域等——主文写明 beyond scope；本卡同样 **不展开 V2 内核**。

### 9.3 HT 路径（训练向；Fig.6）

**两阶段流水：**

1. **跨节点 RDMA**：仅发生在 **同 local index** 的 GPU 之间；
2. **节点内 NVLink**：再转发到真正托管专家的 GPU。

**实现抓手（主文）：**

- 使用 **8 个并行 NVSHMEM world team**（每节点槽位一个）——假设 **每节点恰 8 张可 P2P GPU**（可移植性代价）。
- **notify_dispatch**：先换元数据（每 rank/专家 token 数、前缀矩阵、channel 划分），再 **dispatch/combine** 搬载荷。
- 逻辑 **channel** = 一对 SM，切分 token 片；每 SM **16 warp 特化**（RDMA 侧：7 sender + 1 sender-coordinator + 8 NVLink receiver；配对 SM：8 RDMA→NVLink forwarder + coordinators）。
- 发送：token 放入对称堆上 **per-peer RDMA ring**；coordinator 批量 `nvshmemi_ibgda_put_nbi_warp`，并用 `nvshmemi_ibgda_amo_nonfetch_add` 更新远端 tail。
- **关键结论：**DeepEP **并不**把工作表达成 NVSHMEM 集体或通用 RMA 全家桶；NVSHMEM 只出现在 **跨节点关键点**（元数据交换、chunked put、credit atomic）。上层多段传输与 warp 分工是 DeepEP 自建。

### 9.4 LL 路径（推理向）

- **去掉**节点内 NVLink 转发，跨节点靠 RDMA；同节点可 P2P 则直接本地拷入映射接收缓冲。
- Team：单一 global world + 同槽位 **strided team**（对比 HT 的八平行 world）。
- 结构更简：无 logical channel / 无 HT 式 warp 特化；按 **本地专家** 划分 SM；warp 组绑定专家。
- 热路径 NVSHMEM：**IBGDA put** 送载荷 + **atomic** 发布最终 token 计数。

### 9.5 工程辅：legacy 性能表（GitHub，非 arXiv）

`docs/legacy.md`（V1）公开测试口径（H800 + CX7；对齐 V3/R1 设定）：

**Normal（NVLink+RDMA 转发；4096 tok/batch，7168 hidden，top-4 groups，top-8，FP8 dispatch / BF16 combine）：**

| Type | Dispatch #EP | Bottleneck BW | Combine #EP | Bottleneck BW |
|---|---|---|---|---|
| Intranode | 8 | 153 GB/s (NVLink) | 8 | 158 GB/s (NVLink) |
| Internode | 16 | 43 GB/s (RDMA) | 16 | 43 GB/s (RDMA) |
| Internode | 32 | 58 GB/s (RDMA) | 32 | 57 GB/s (RDMA) |
| Internode | 64 | 51 GB/s (RDMA) | 64 | 50 GB/s (RDMA) |

**Low-latency（纯 RDMA；128 tok/batch 等生产设定）** 例：EP8 dispatch **77 µs / 98 GB/s**，combine **114 µs / 127 GB/s**；EP 增大时延迟升、带宽降（表见 legacy）。

主 README（V2）另给 SM90/SM100 表，并称相对 V1 **最高约 1.3× 峰性能、最高约 4× 节省 SM**——属 V2/Gin 叙事，**勿与主文 H200 微基准混表**。

### 9.6 与 NCCL GIN 的关系（主文转述，非本卡复测）

主文 **不**重跑对比；转述 GIN 文：DeepEP 接 NCCL GIN 后，HT/LL 的 dispatch/combine 与 NVSHMEM 基线通常差约 **1–2%**，同时留在 NCCL 运行时内做设备发起通信。含义：NVSHMEM 仍是有价值的 **低层一侧 RMA 基底**；生态上 NCCL 正在收窄「设备发起」缺口。

---

## 十、讨论与结论（§IX–X，压缩）

1. **系统定位**：NVSHMEM 在 GPU 通信设计空间占据「设备发起 + 一侧 + 对称内存」点；对称堆、多传输路径、分层运行时把设备 API 接到 NIC/proxy。
2. **已知短板**：内建集体的 **multi-CTA** 支持有限（§VI-D）；跨节点集体相对 NCCL 弱（§VII-C）。
3. **应用启示（DeepEP）**：高性能稀疏 DL 通信往往 = **薄封装 NVSHMEM/IBGDA + 厚自建流水**（ring、warp 特化、两域转发），而不是「调用一次 AlltoAll 了事」。
4. **相关工作边界**：Hu et al. 对 NCCL 的源码级 demystify；Langer et al. 专讲动态对称堆——本主文覆盖更广。

---

## 十一、跟读清单与反幻觉

| 主张 | 锚点 |
|---|---|
| 主文 arXiv / 页数 / 体积 | `2606.05951v1`；12 页；`ls -lh` → **824K** |
| 分析库版本 | NVSHMEM **3.3.9** |
| DeepEP 文献形态 | GitHub only；主文 [33]；**无**独立 arXiv |
| 本卡不写 | [[AI基础设施总览]] 通论；[[混合专家架构]] MoE 史；[[DeepSeekV3训练与MoE基建]] / [[DeepSeekV4技术报告深读]] 通信小节全文；DeepEP V2 内核深读 |
| HT 用 8× world team | §VIII-A；依赖 8 GPU/节点假设 |
| 临界 NVSHMEM 调用 | `nvshmemi_ibgda_put_nbi_warp`、`nvshmemi_ibgda_amo_nonfetch_add` |
| 微基准数字 | §VII / Fig.4–5；上表照录 |
| legacy 带宽表 | `docs/legacy.md`（GitHub），非 arXiv |

**自检三问：**
1. 是否误给 DeepEP 捏造了 arXiv 号？→ 必须否。
2. 是否把 DualPipe / 路由损失写进本卡主文？→ 必须否。
3. 是否把 V2 Gin 性能表与主文 H200 NVSHMEM 微基准混为一谈？→ 必须否。

---

## 十二、回报摘要（给编排用）

- **笔记路径**：`/workspace/AIResearch-drafts/推理与基础设施/InfraServing/NVSHMEM与DeepEP通信.md
- **PDF 路径**：`https://arxiv.org/abs/2606.05951`
- **PDF 体积**：`ls -lh` → **824K**（可入库，≪20MB）
- **抽取**：
- **摘要**：主文系统拆解 NVSHMEM 3.3.9 的对称堆、P2P/IBGDA 一侧路径与设备集体；以 DeepSeek **DeepEP V1**（GitHub，无独立 arXiv）证明「稀疏 EP 只需在跨节点临界点薄用 NVSHMEM」。划界避开 [[AI基础设施总览]] / [[混合专家架构]] / [[DeepSeekV3训练与MoE基建]] · [[DeepSeekV4技术报告深读]] 通信全文。
