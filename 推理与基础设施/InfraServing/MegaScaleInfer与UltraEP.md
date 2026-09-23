---
title: "Sparse MoE 服务系统：MegaScale-Infer + UltraEP（≠ MoE 架构通史 / ≠ DeepEP 通信）"
topic: MegaScaleInfer与UltraEP
date: 2026-09-22
lines: [AI Infra, 服务架构]
status: archived
sources:
 - https://arxiv.org/abs/2504.02263 # 1.1M / 24p（主 A）
 - https://arxiv.org/abs/2606.04101 # 2.7M / 15p（主 B）
arxiv: ["2504.02263", "2606.04101"]
related:
 - "混合专家架构"
 - "NVSHMEM与DeepEP通信"
 - "ThunderKittens内核DSL"
 - "推理引擎生态"
 - "DeepSeekV3训练与MoE基建"
 - "AI基础设施总览"
note_deepep: "DeepEP 无独立 arXiv 主文；本卡仅作集成/对照接口一句；禁止虚构 DeepEP paper arXiv 号；内核分析见 NVSHMEM与DeepEP通信"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# Sparse MoE 服务系统：MegaScale-Infer + UltraEP（≠ MoE 架构通史 / ≠ DeepEP 通信）

> **定位**：**P1 Infra / 服务架构**——在 **[[混合专家架构]]** 已立 MoE **架构通史**、**[[NVSHMEM与DeepEP通信]]** 已立 **NVSHMEM 通信基底 + DeepEP 案例**之后，本卡只写 **服务侧如何把注意力与专家解耦、如何在机架级大 EP 上做近最优负载均衡**。两条主轴正交：
> - **MegaScale-Infer**（*Disaggregated Expert Parallelism*）：**注意力节点 ↔ 专家节点**解耦 + ping-pong 微批 + 定制 **M2N** 通信；主战场是 **decode 吞吐 / 单位成本**。
> - **UltraEP**（*exact-load, real-time balancer*）：在 **rack-scale node（RSN）** 上对 **每个 microbatch × 每层**做 **配额驱动复制 + 重路由**；主战场是 **训练 + serving prefill** 的秩级负载与理想吞吐贴近度。
> **攻坚线**：**AI Infra / 服务架构（主）** + **文内吞吐 / 失衡字段（辅）**。
> **硬划界（开篇钉死，禁止滑向通史或通信内核）**：
> - **≠ [[混合专家架构]]**：不写 Switch→Mixtral→V3 路由公式、aux-loss、总参/激活参通史；MoE 稀疏只当「每专家 batch 变稀 → 利用率塌」接口一句。
> - **≠ [[NVSHMEM与DeepEP通信]]**：不写 NVSHMEM 对称堆 / IBGDA / DeepEP V1·V2 内核剖面；**禁止虚构 DeepEP 独立 arXiv 号**；本卡若点 DeepEP，只录「token all-to-all 后端 / 对照一句」。
> - **≠ [[ThunderKittens内核DSL]]**：不写 ThunderKittens tile DSL / 核编程抽象。
> - **≠ B7**：不写 vLLM/SGLang/TRT-LLM 引擎选型通史、PagedAttention、投机解码族；基线名只作评测对照。
> **禁止编造**：倍率、失衡比、硬件表一律锚定官方 PDF（2026-09-22 CST）。
> **二进制**：两篇均 **≪20MB**（见 §一）→ **官方 HTTPS 外链**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A** | Zhu, Jiang, Jin 等（ByteDance Seed / PKU），*MegaScale-Infer: Serving Mixture-of-Experts at Scale with Disaggregated Expert Parallelism* | arXiv:**2504.02263**v4 \[cs.DC\] **26 Jul 2025**；`https://arxiv.org/abs/2504.02263`（**1,143,163** B ≈ **1.1M**；**24** 页 letter） | **解耦 EP 服务**：Attention–Expert 分节点 + ping-pong + M2N |
| **主文 B** | Wei, Jin, Dai 等（PKU / 小红书 / 上海 AI Lab 等），*UltraEP: Unleash MoE Training and Inference on Rack-Scale Nodes with Near-Optimal Load Balancing* | arXiv:**2606.04101**v3 \[cs.DC\] **18 Jun 2026**；`https://arxiv.org/abs/2606.04101`（**2,846,924** B ≈ **2.7M**；**15** 页 letter；CreationDate **2026-06-19 CST**） | **机架级 exact-load 均衡**：配额规划 + RSN tile/relay 通信 |

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2504.02263-megascale-infer.pdf` | **1.1M**（1,143,163 B） | 24 | **官方 HTTPS 外链**（≪20MB） |
| `2606.04101-ultraep.pdf` | **2.7M**（2,846,924 B） | 15 | **官方 HTTPS 外链**（≪20MB） |

**一句话抓手：**
- **MegaScale-Infer**：稀疏 decode 时「整模同节点」会把专家 GEMM 饿死——把 **Attention 复制、Expert 切开**，用 **ping-pong 微批**填空闲，用 **M2N** 扛动态 token 路由。
- **UltraEP**：大 EP 下历史统计的 EPLB 跟不上「层 × 微批 × 域」漂移——在 **RSN 高速域**里用 **门控后精确负载**当场解配额、复制热专家、重路由 token，逼近 force-balanced 理想吞吐。

---

## 二、议题边界：服务解耦 / 机架均衡 ≠ 架构通史 / 通信基底 / 引擎通史

### 2.1 四向对照（跟读）

| 轴 | 动什么 | 粒度 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|---|
| **[[混合专家架构]] MoE 架构通史** | 路由 / 稀疏 / 总参–激活参 | 模型族叙事 | [[混合专家架构]] | **否** |
| **[[NVSHMEM与DeepEP通信]] NVSHMEM·DeepEP** | 设备侧 RMA / EP all-to-all 内核 | 通信库 | [[NVSHMEM与DeepEP通信]] | **否**（仅接口） |
| **[[ThunderKittens内核DSL]] ThunderKittens** | GPU 核 DSL | 编程模型 | [[ThunderKittens内核DSL]] | **否** |
| **B7 推理引擎** | vLLM / SGLang / TRT-LLM 选型 | 引擎生态 | B7 | **否**（名作基线） |
| **MegaScale-Infer** | Attention–FFN **节点解耦** + ping-pong + M2N | **decode 服务实例** | **本篇 A** | **是** |
| **UltraEP** | **exact-load** 复制/重路由（RSN hot-path） | **EP 组 × 层 × 微批** | **本篇 B** | **是** |

跟读直觉：[[混合专家架构]] 问「**模型怎么稀疏**」；[[NVSHMEM与DeepEP通信]] 问「**token 怎么在 GPU 间搬**」；B7 问「**引擎怎么选**」；MegaScale-Infer 问「**注意力与专家要不要分机、怎么流水**」；UltraEP 问「**大 EP 热专家怎么实时摊平**」。

### 2.2 DeepEP 硬约束（防越界）

- UltraEP §7：**token dispatch/combine** 接 **DeepEP**（文标 `hybrid-ep` 分支、`v1.2.1+7febc6e`）；References **\[9\]** 为 **GitHub** `deepseek-ai/DeepEP`，**无独立 arXiv 主文号**。
- MegaScale-Infer §6「Comparison with DeepEP」只给 **一句对照**：己方 **CPU 侧**做跨节点 M2N，DeepEP 走 **GPU–GPU**（无 CPU proxy）——**不**展开 DeepEP 内核 / PTX / L2 占用分析（那是 [[NVSHMEM与DeepEP通信]]）。
- **本卡禁止**：虚构 DeepEP paper arXiv；重写 DeepEP V1/V2 通信路径；把 UltraEP 写成「DeepEP 续篇」。

`
 MoE serving / large-EP 外壳
 │
 ┌──────────────┼──────────────┐
 ▼ ▼ ▼
 [[混合专家架构]] 架构 [[NVSHMEM与DeepEP通信]] 通信 本卡服务系统
 路由/稀疏史 NVSHMEM·DeepEP MegaScale 解耦 + UltraEP 均衡
`

---

## 三、主文 A：MegaScale-Infer（2504.02263）

### 3.1 问题立轴：稀疏把 FFN 从算力密集打回内存密集

§1–2：decode 主导服务成本。稠密模型里，增大 batch 可让 FFN 吃满算力；MoE 同 batch 下每专家 token ≈ `B × topk / #experts`，稀疏升高后专家侧利用率塌（Fig.1）。内存与 TBT SLO 又卡住全局 batch。Infinite-LLM 式「拆注意力」对稠密长上下文有效，但对 MoE 的 top-k 动态路由不够。

**解法名：** *disaggregated expert parallelism*——**Attention 节点**与 **Expert 节点**分置：

- Attention：**数据并行复制**（存权重 + KV）；节点内可 TP（NVLink）。
- Expert：**专家并行**（典型 1–8 GPU/节点持有一个专家）；节点内可 TP。
- 异质部署：注意力偏 **性价比带宽/容量**（文例 H20）；专家偏 **性价比算力**（文例 L40S）。
- 运行时还接 **prefill / decode 分簇**（跟读 DistServe 等）；**本文主写 decode**。

### 3.2 Ping-pong 流水：用微批填「你算我闲」

解耦后单批会出现：一侧算时另一侧空转，外加跨节点等结果。§4.1 把全局 batch 切成 **m 个 micro-batches**，在 Attention ↔ Expert 间 **乒乓**：

必要条件（文式 1–3）：

1. $T_a \approx T_e$（层间依赖少空泡）；
2. $T_c < T_f$，$T_f=\max\{T_a,T_e\}$（通信可被算力盖住）；
3. $m \times T_f \ge 2(T_f+T_c)$ → 常需 **m≥3**（快网）或 **m≥4**（慢网）；文设搜索上限 $N_m=4$（切太碎伤专家 GEMM）。

迭代时延近似（式 4–5）：单微批在 $(T_a+T_e+2T_c)$ 与 $m T_f L$ 之间；全局 $T_{total}=(T_a+T_e+2T_c)+T_f(mL-1)$。

### 3.3 部署搜索与异质：最大化单位成本吞吐

Alg.1 枚举 $t_{pa},t_{pe}$、由剖面系数平衡 $n_a$、再扫 $m$，在 **TBT SLO** 与 KV 内存约束下最大化 **throughput per unit cost**（$t_{puc}$）。复杂度 $O(M^2 N_m)$，$M$ 为单机 GPU 上限（如 {1,2,4,8}）。

SLO：文设 **TBT = 150 ms**。异质表（Table 3）以 L20 归一化标价，对比 L20 / H800 / A800 / H20 / L40S 的容量·带宽·TFLOPS 性价比——跟读时只取「注意力吃带宽、专家吃算力」选型逻辑，不外推未测机型。

### 3.4 M2N 通信库（服务侧定制，≠ DeepEP 内核课）

解耦后 All2All 变成 **M 个注意力 GPU ↔ N 个专家 GPU** 的 **M2N / N2M**。§5 动机：NCCL 点对点在该模式下中位延迟与 **P99** 相对 perftest 基线偏高（Fig.5）。定制库要点（照录主张）：

- 去掉不必要的 **GPU→CPU 拷贝**、**group 初始化**、冗余 **GPU sync**；
- 流模型：CUDA event 等前核 → 阻塞流 → **RDMA write with immediate** → poll CQ → 放行；
- 约 **4900/5000** 行 C++/Python 的 PyTorch 扩展；GPUDirect / GDRCopy；
- 相对 NCCL：摘要称 **4.2×** 吞吐、**68.2%** 更低延迟（§7.3 亦录中位 **68.2%**、尾延迟 **92.9%**、吞吐 **4.2×**）。

**与 DeepEP 一句边界（文 §6）：** MegaScale-Infer 强调跨节点走 **CPU 通信**以省 GPU SM；DeepEP 走 **GPU–GPU**——细节与剖面 **回指 [[NVSHMEM与DeepEP通信]]**，本卡不重写。

专家侧另有基于近期流量的 **冗余专家 / 贪心放置**（§6 Load balance），属服务期热度摊平，**不是** UltraEP 的逐微批 exact-load。

### 3.5 评测字段（照录）

| 项 | 文内 |
|---|---|
| 模型 | Mixtral-8×22B（~141B）、DBRX（~132B）、Scaled-MoE（~317B）；Table 4：experts 8/16/32，top-k 2/4/4 |
| 同质集群 | 8×节点 × 8×80GB Ampere + 200 Gbps IB；基线 **vLLM**、**TensorRT-LLM**（时分 P/D 公平比） |
| 异质 | H20（注意力）+ L40S（专家） |
| 工作负载 | 生产 trace；中位 in/out **571 / 159** token；bf16 |
| Decode / GPU | 相对基线最高约 **2.56× / 1.28×**（Mixtral/DBRX 量级叙述）；Scaled-MoE 上相对 vLLM / TRT-LLM **7.11× / 1.90×** |
| 单位成本 | 异质相对 H20 上基线最高约 **3.24× / 1.86×**；摘要亦写同质 **1.90×**、异质 per-cost **1.86×**；另有 **1.7×** per-cost 叙述 |
| E2E（含 prefill） | 同质最高约 **1.18×**（prefill 算力密集，增益淡） |
| 生产 | 公司服务已部署，同流量成本约降 **1.5–2.0×** |

---

## 四、主文 B：UltraEP（2606.04101）

### 4.1 问题立轴：大 EP + 非平稳热度 → 历史均衡失灵

§1–3：32/64-way EP 已成百亿–千亿 MoE 标配，但专家负载不均会放大为 **算力掉队、token all-to-all 瓶颈、激活内存尖峰**。EPLB 类方案按 **历史负载周期重排 + 冗余复制**；文观察 serving prefill 与训练中热专家随 **域 / 层 / 微批** 剧变，陈旧布局残留失衡（Fig.4–6），极端时甚至恶化。

**算法侧 aux-loss / 路由 bias** 与 **系统侧均衡**互补：前者稳优化与特化，**不能保证**每个 microbatch 的实现负载——UltraEP 站系统侧。

**为何需要 RSN：** 标准集群 scale-up 多止于 4/8 GPU 节点；跨节点迁专家状态对 hot-path 过贵。RSN 把 scale-up 扩到 **整机架（文称常 64+ GPU）**，使 EP 组可落在高带宽域，**门控后实时均衡**才物理可行（Fig.2）。摘要标 hot-path 暴露开销约 **~0.3 ms** 量级。

**范围钉死：** **训练 + serving prefill**；decode 内存束缚下算力失衡被稀释，文不把 decode 作主均衡目标。

### 4.2 布局：只复制、不重排主专家；跨层复用冗余缓冲

§4.1：每 rank 固定 **main slots + redundant slots（$N_{slot}$）**。主实例不可迁移；冗余槽 **无 optimizer state**，权重/梯度缓冲 **跨层复用**——Qwen3-235B-A22B 例：单冗余槽从 **3.3 GB 权重 + 6.6 GB 梯度**压到 **36 MB + 72 MB**/rank（代价是前向关键路径上的逐层物化截止）。

前向（Fig.8）：复用 notify-dispatch 收齐精确负载 → **全设备确定性**解复制+重路由 → 主专家权重分发到副本 → 再 token dispatch。
后向（Fig.9）：按缓存计划重物化冗余权重（可与 Wgrad 重叠）→ MoE 反传后把副本梯度 **reduce 回主专家**（保训练等价）→ 再进入下层。

### 4.3 配额驱动规划（控制面）

把「先放副本、再启发式重路由」改成直接解 **每物理实例最终负载配额 $U$**，再诱导重路由 $Q$（Alg.1）：

1. **阈值二分**：找最小 $\tau$，使各 rank 经复制后负载 ≤ $\tau$（目标系数 $\beta=1.01$）；
2. 探针内贪心：过载 rank 按超额降序、其主专家按 $\lambda_e$ 降序，向 **slack 最大且满足槽位/不重复** 的 rank 转移，单次转移 ≥ $u_{\min}$（文设 **1024**）；
3. **重路由**：先吃本地配额，残余按剩余配额比例分配 + 确定性舍入；token 级用前缀扫描上界查找落地实例。

全程 **GPU 常驻**（单 SM 协作块 + warp 归约），避免 hot-path 主机往返。

### 4.4 RSN 原生通信（数据面，≠ DeepEP 内核课）

§6：均衡流量是 **稀疏、逐层易变** 的专家状态图，不是静态集体。

- **Persistent tile streaming**：权重/梯度切固定 tile，持久核拉任务流；共享内存双缓冲。
- **Chunk-streaming relay**：副本数超过阈值（文设 **4**）的热专家建两级中继树，把扇出摊到空闲发送容量（Fig.10）。

文称相对主流后端，专家复制加速 **3.1×–5.5×**（对照含 `torch.distributed` 与 **DeepEP**——此处 DeepEP 是 **复制通信对照**，不是本卡分析对象）。

实现：独立运行时约 **9.6K** 行；接入 Megatron-LM / SGLang 各 **<1K**；token 路径接 DeepEP（**仅集成句**）。

### 4.5 评测字段（照录）

| 项 | 文内 |
|---|---|
| 测试床 | 公有云 RSN：每架 **64 GPU**；scale-up 带宽约 scale-out **8–10×**；原型 prefill 1 架、训练 2/4 架，另有多机架生产 |
| 模型 / 并行（Table 2） | GLM4.5-106B EP64-DP2；Qwen3-235B EP64-DP4 / serve EP64；GLM4.7-358B serve EP40；DeepSeek-V3-671B EP64-PP4；$N_{slot}$ 多为 2（358B 为 4） |
| 规模 | 至 **256 GPU**；参数 **106B–671B** |
| 理想贴近 | 训练均 **94.6%**、serving prefill 均 **93.9%** force-balanced ideal；摘要跨设定均 **94.3%** |
| vs 无均衡 | 摘要 **1.49×** |
| vs 框架基线 | 训练均 **1.42×** over Megatron-LM；prefill **1.56×** over SGLang |
| 失衡 | 均衡后秩间约 **1.01–1.04**（摘要；训练段 1.01–1.03）；无均衡口径 **1.30–4.01** |
| 基线族 | Megatron / SGLang；EPLB；LPLB；**EPLB+（exact load + 原启发式）**；Ideal（改路由强制均匀） |
| 训练增益均分 | EPLB / LPLB / EPLB+ / UltraEP 相对 Megatron：**+20% / +12% / +29% / +42%** |
| 生产 | 内部 RefMoE-288B-A16B（EP32）等；长期 **>92%** ideal，并称保持收敛语义 |

---

## 五、交叉对照与跟读清单

| 问题 | MegaScale-Infer | UltraEP |
|---|---|---|
| 主场景 | **Decode 服务**（兼异质成本） | **训练 + Prefill**（RSN 大 EP） |
| 旋钮 | Attention/Expert **分节点**、$m$、异质 GPU、M2N | **$N_{slot}$**、配额 $\tau/\beta$、tile/relay |
| 通信对象 | **激活 / token**（M↔N） | **专家权重·梯度**（复制）+ 既有 token A2A 后端 |
| 负载策略 | 服务期热度冗余（周期）+ 部署搜索 | **门控后 exact-load** 逐层·逐微批 |
| 硬件假设 | 多节点 IB + 可选异质 GPU | **机架级 scale-up 域** |
| 与 DeepEP | 一句 CPU vs GPU–GPU 对照 | token 后端集成；复制带宽对照 |
| 典型数字锚 | 最高 **1.90×**/GPU decode；M2N **4.2×** | **~94%** ideal；失衡 **→~1.01–1.04** |

**建议跟读顺序：** §二划界 → MegaScale Fig.3–4 + Alg.1 + Fig.8/9 吞吐表 → UltraEP Fig.1–2 + Alg.1 + Fig.11/12 → 需要通信基底时回 **[[NVSHMEM与DeepEP通信]]**，需要路由史时回 **[[混合专家架构]]**，需要引擎选型时回 **B7**——**不要**反向把本卡写成其中任一续篇。

**刻意不写（防越界）：** Switch/Mixtral 路由公式重推；NVSHMEM/IBGDA/DeepEP V1·V2 内核；ThunderKittens DSL；vLLM PagedAttention / 投机解码通史；虚构 DeepEP arXiv。

---

## 六、来源与核验

| 字段 | 值 |
|---|---|
| 一手 PDF | `https://arxiv.org/abs/2504.02263`；`https://arxiv.org/abs/2606.04101` |
| 抽取 | `*.txt`（及 ） |
| 核验时刻 | 2026-09-22 CST（`curl` arXiv PDF → → ） |
| DeepEP 引用 | UltraEP Ref.[9] = GitHub；MegaScale 文内对照句；**无独立 arXiv** |
| 禁编造声明 | 未外推未见表硬件倍率；生产「1.5–2.0× / >92% ideal」仅照录作者自述部署段 |

