---
title: "Privacy-preserving inference：GPU/CPU TEE 机密计算（信任边界 × CC tax，5）"
topic: TEE机密推理
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2608.26575
 - https://arxiv.org/abs/2606.31408
arxiv: ["2608.26575", "2606.31408"]
related: ["隐私与机器遗忘", "端侧小模型", "硬件软件协同部署", "推理引擎生态", "AI基础设施总览"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# Privacy-preserving inference：GPU/CPU TEE 机密计算

> **定位**：**P1**——仓库缺 **云侧机密推理 / TEE 开销与远程证明** 横切；[[隐私与机器遗忘]] 已写机器遗忘，本篇改写 **data-in-use 机密部署**。锚点两篇可核 PDF：Confidential.ai 的 Blackwell B200 CC 吞吐实测（arXiv **2608.26575**）与 EnclaveX 端到端 CPU+GPU TEE（arXiv **2606.31408**）。
> **攻坚线**：**架构思想（主）**——信任边界（CPU TEE ↔ GPU CC ↔ 应用层）与远程证明链；**评测字段（辅）**——CC tax / 吞吐 / TTFT·TPOT·ITL，以及 attestation 延迟。
> **硬划界（禁止重写）**：
> - **≠ [[隐私与机器遗忘]] unlearning**：擦权重 / forget 集 ≠ 运行时加密隔离；本篇**不写**遗忘算法与 MIA。
> - **≠ [[端侧小模型]] 端侧 SLM 通史**：端侧「数据不离机」是**另一轴**；本篇是 **公有云 / 多租户** 上的机密 VM + cGPU。
> - **≠ [[硬件软件协同部署]] HW–SW 白皮书选型地图**：不写 Blackwell 代际 / FP4 规格通史；只取 **CC 模式边界与开销**。
> - **禁止侧信道利用步骤**：两文威胁模型均声明侧信道**超范围**；本笔记只记「观测被故意关闭」等防御后果，**不写**攻击复现。
> - **禁止编造**：数字、配置、页数一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文 A（开销面）** | Asad & Grunseid (Confidential.ai), *Benchmarking Confidential Computing Performance on NVIDIA Blackwell GPUs* | arXiv:**2608.26575v2** \[cs.DC\] **1 Sep 2026**（文内 **June 2026**）；`https://arxiv.org/abs/2608.26575`（**23** 页 A4；439,825 bytes） | Intel TDX + NVIDIA CC on **8× B200**；配对 CC-on/off；机制归因 + 部署建议 |
| **主文 B（端到端边界）** | Schambach, Le, Arnautov & Fetzer, *EnclaveX: End-to-End Confidential AI with CPU/GPU TEEs* | arXiv:**2606.31408v1** \[cs.CR\] **30 Jun 2026**；`https://arxiv.org/abs/2606.31408`（**8** 页 letter；881,245 bytes） | Intel TDX + **H200** cGPU + SCONE；应用层证明对抗 K8s admin；CVM vs native 开销 |

**一句话抓手：** 云上机密推理要把 **prompt / KV / 权重** 从「宿主机特权方可读」推进到 **硬件根信任**；开销不是一个常数——Blackwell 上配置对时可达 **约 1–3%**，配置错可达 **30–40%**；仅有 CVM 不够时，还要 **应用层 attestation 后再放密钥**（EnclaveX）。

---

## 二、议题边界：云侧机密部署 × 开销面，不是遗忘 / 端侧 / 芯片选型

### 2.1 相对相邻笔记只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[隐私与机器遗忘]]** unlearning | 「事后擦知识」是**另一条**隐私轴；索引一句即可 | forget/retain、OpenUnlearning、MIA 实现 |
| **[[端侧小模型]]** 端侧 SLM | 「数据不出设备」与「云上 TEE」互补，不互换 | MobileLLM / Phi 通史、端侧 QAT |
| **[[硬件软件协同部署]]** HW–SW | Blackwell / H200 **作为 CC 载体**点名 | 白皮书代际、FP4/互联选型地图 |
| **B7 / [[AI基础设施总览]]** | SGLang / vLLM / Triton **仅作测栈**；补丁名作开销杠杆 | 引擎选型通史、PagedAttention 全文 |

### 2.2 两文各自的「不写什么」（跟读）

| 文 | 明确超范围 / 未测 |
|---|---|
| **2608.26575 §1.3** | **不审计**安全性质是否成立；**不测** attestation 与机密 VM 启动开销；**不测**跨节点 RDMA / prefill–decode 分离（§9 只定性） |
| **2606.31408 §3.1** | 威胁模型**显式排除**侧信道；DoS 亦超范围；SCONE 文内仅点名已有缓解（L1 / AEX-Notify 等）——**本笔记不展开利用** |

### 2.3 跟读口诀

`
威胁：CSP / 宿主机 / 特权租户 / 物理接触可读 data-in-use
 ↓
硬件边界：CPU TEE（TDX/SEV-SNP…）+ GPU CC（PCIe / NVLink 加密）
 ↓
证明：远程 attestation 通过 → 再释放会话密钥 / 应用密钥
 ↓
开销 = 通信税（不是算力税）：
 轴1 每步 host 提交 / 同步（可被 CUDA graph + 框架补丁摊薄）
 轴2 加密的跨 GPU 流量（NVLE；软件抹不掉，靠并行度与业务形状压低）
`

---

## 三、架构思想：信任边界与「谁还在 TCB 里」

### 3.1 TEE 三性质（Blackwell 文 §2.1，跟读）

文对本栈 TEE 钉了三点（后续开销测量**默认保证成立**）：

1. **Confidentiality**：客户机内存硬件加密，hypervisor / 宿主 OS **拿不到密钥**。
2. **Integrity**：对内存的篡改（重放 / 破坏 / 重映射）由硬件检测。
3. **Attestation**：启动时装载软件的度量签名，链到厂商根信任；远程方先验后信。

**本栈组合：**

| 层 | 机制 | 保护什么 |
|---|---|---|
| CPU | Intel **TDX** 机密 VM | 客户机内存与运行态相对宿主隔离 |
| GPU | NVIDIA **CC mode** | GPU 机密启动；**PCIe** 与多卡 **NVLink** 加密；权重与 data-in-use 在 GPU 侧 |
| 证明 | TDX quote + NVIDIA GPU attestation report | 链验证通过后，GPU **才释放** CC 会话密钥 |

保护对象（§1.1 / §2.1）：**prompt、生成 token、KV cache、模型权重**——在 CPU、PCIe、GPU 内存、NVLink 上全程加密与完整性保护，使基础设施运营方**可跑工作负载而不能读/改**。

### 3.2 四条加密边界（开销归因名录，§2.2）

Blackwell 文把成本**点名**到边界，避免「一个总慢」：

| 边界 | 机制（文述） | 对推理的含义 |
|---|---|---|
| **PCIe bulk** | H2D/D2H 经驱动 bounce buffer + **AES-GCM**（非内核 SWIOTLB） | 权重加载 / 输入 / sampler 回读有 per-byte + per-call 税；热路径应让权重与 KV **常驻 GPU** |
| **命令通道** | 每次 kernel 提交走加密 **GSP-RPC** | **固定 per-submission** 税（文测约 **+12 µs**/次）；eager 多提交时放大 |
| **NVLE** | Multi-Party Trust NVLink encryption | 跨卡集合通信按字节计税；份额大时**不随 batch 摊薄** |
| **能力损失** | NVSwitch **multicast（cuMulticast）禁用** | 依赖 multicast 的融合核走无 multicast 路径 |

AES 侧：单核 AES-256-GCM 约 **13.9 GB/s** 上限；实测 CC PCIe 路径约 **10 GB/s**（约 72%）；每 GPU 的 SPDM 安全会话在当前实现里**单线程钉核**，故 H2D crypto **不跨宿主线程扩展**——扩展方式是**加 GPU**，不是加宿主线程（§5.1 Table 4）。

### 3.3 EnclaveX：CVM 不够 → 应用层证明后再放秘密（§1 / §3）

**问题（文原动机）：** 仅用机密容器 / CVM + Hopper/H200 cGPU，仍可能把 **K8s admin** 留在应用 TCB 内——admin 可 `kubectl exec` 进机密 VM，等价于 enclave 内 root。

**EnclaveX 防御姿态（只写部署侧）：**

| 组件 | 作用 |
|---|---|
| **CPU TEE** | Intel TDX（兼容叙述含 SEV-SNP / ARM CCA）加密内存隔离 |
| **cGPU** | NVIDIA **H200** 机密 GPU；CVM 内驱动保护 CVM–cGPU IO |
| **SCONE runtime** | 进程级屏蔽执行；目标是更小 TCB、微服务粒度信任 |
| **CAS**（Configuration & Attestation Service） | 自在 TEE 内；管策略、验证明、**通过后再供给密钥** |
| **Guest 内核模块** | 运行时度量 ML 应用；**关闭 Guest 内 memory dump** |

**威胁模型摘要（§3.1，防御侧复述）：** 攻击者可掌控 OS/hypervisor、物理探测内存、K8s 全 API、对网络做 Dolev–Yao 式篡改/重放；**侧信道与 DoS 排除在外**。密钥只在 attestation 成功后交给应用——即便 admin exec 进 VM，也**拿不到**应用层密钥。

**工作流（§3.4 Figure 1，九步压缩）：**

1. 用户定义安全策略并先证明 **CAS**；
2. 策略提交 CAS；起 TDX VM 时带 VM ID 策略扩展；
3–4. 固件/Guest/内核模块度量；驱动侧证明 **cGPU**；
5–6. 向 CAS 提交 VM+GPU 报告 → 发签名密钥、标记已证明（singleton）；
7–8. 度量运行中的 ML 应用 → quote → CAS 验策略 → **下发配置与解密密钥**；
9. 在 CPU+GPU TEE 内跑推理/训练。

实现注记（§4）：Trustee 验 CVM，SCONE Attestation 验应用；内核模块拟开源以支持 SEV-SNP / ARM CCA；应用**无需改代码**即可包进软件 enclave。

### 3.4 两文信任边界对照

| 维度 | Blackwell CC 实测 | EnclaveX |
|---|---|---|
| 硬件代 | **B200** + TDX | **H200** + TDX（+ SCONE） |
| 主问题 | **开销机制**与可达成工作点 | **谁还能读秘密**（含 K8s admin） |
| 证明 | 背景链：TDX quote + GPU report（**未测延迟**） | **测了** native vs 应用层附加延迟 |
| TCB 叙事 | 运营方移出 data-in-use 可读集 | 进一步把 **Guest 特权方** 移出密钥可读集 |

---

## 四、评测字段：CC tax / 吞吐开销（主表跟读）

### 4.1 方法纪律（Blackwell §3）

- **配对对照**：同一物理机、同一盘、同一 GPU；只改 **GPU CC bit + TDX guest 对象**。
- **Host**：Intel Xeon **6767P**（双路）+ **8× B200** NVLink。
- **栈**：Ubuntu 24.04.3；guest 驱动 NVIDIA **595.71.05**；框架含 SGLang **0.5.13** / **cc-fixes**、vLLM **0.21/0.22**、Megatron+TE（训练）。
- **Caveat（§3.3）**：CC 下 CUDA-event 计时与部分 autotuner **不可信**（设计上关闭以防侧信道泄漏）→ 用 `%globaltimer` 或墙钟吞吐；带 submission tracing 的跑**不当**吞吐锚点。

### 4.2 头条 CC tax（Table 2 / §4）

| 工作负载（配置正确） | CC tax（相对非 CC） |
|---|---|
| MoE serving，**4** GPU（TP4），decode-heavy，pinned | **∼1.5%** |
| MoE serving，**8** GPU（TP8），decode-heavy，pinned | **∼3%**（两轮五次中位 **2.8% / 3.6%**） |
| 单卡，full CUDA graphs + 框架补丁 | **<1%** |
| 8 卡训练（bf16） | **10–13%** |

文强调：**30–40%** 类高惩罚来自**可避免配置**（未打补丁 / eager / 短输出 prefill-heavy），**不是**可达成工作点。NVIDIA 白皮书侧有独立「低个位数」报告（文引 [6]）。

**两轴模型（§4 / §7.1）：**

1. **Per-host-operation**：每步提交/同步更贵（加密命令通道 + 强制同步拷贝）→ 固定成本，**随 batch 摊薄**；full graph + 补丁可压到噪声。
2. **Per-NVLink-traffic**：集合通信字节 × 近似常数 NVLE 率 → 由「步内跨卡通信时间份额」决定；份额大时**不摊薄**，是硬件地板。

### 4.3 微观：提交税与图捕获（§5.2）

| 度量 | CC off | CC on | 税 |
|---|---|---|---|
| 单次 kernel submission | 3.45 µs | 15.7 µs | **∼+12 µs（∼3.5×）** |
| 仅 sync | 1.62 µs | 1.67 µs | ∼0 |

合成 decode（约 181 launches/step）：eager **2.41×** → 整步 graph **1.04×**（Table 6）。模型：

$$
\text{CC decode tax} \approx (\#\text{host submissions per step}) \times \sim 12\,\mu\mathrm{s}
$$

vLLM 0.22 / Qwen3.5-9B 单 B200（Table 7）：cudagraph decode **1179 vs 1772 tok/s（1.50×）**；倒推每步约 **2.28 ms** ≈ **185** 次分段提交 × 12 µs——与「按层切 graph」一致。libcrypto CPU 在 decode 仅 **0.5%** → 贵的是 **launch**，不是 bulk 密码运算本身。

### 4.4 NVLE 带宽地板（Table 8，4× B200 同 NUMA）

| 度量 | 相对非 CC |
|---|---|
| D2D Copy Engine | 约 **−11% ∼ −12%** 带宽 |
| D2D SM-based | 约 **−18%** |
| NCCL all_reduce / all_to_all | 约 **−10%** |
| P2P short-write 中位延迟 | **∼4×**（14.5 vs 3.7 µs） |

另：CC 下 PCIe H2D/D2H 约 **15–19×** 慢（例：3.5 vs 51.6 GB/s H2D）——主要伤**加载**；权重/KV 常驻后逐步影响小。

### 4.5 单卡：overlap 一开一关差一个数量级（§6）

| 工况 | 模型 | CC tax |
|---|---|---|
| overlap **关**（Mamba 被迫关） | Nemotron-3-Super-120B-A12B NVFP4 | **∼2%**（Table 9：1.7–2.8%） |
| overlap **开**、出厂 SGLang | Qwen3-8B bf16 | **∼34–39%**（Table 12） |
| graph + **CC 补丁** | Qwen2.5-72B-AWQ | 并发扫 **−0.2%∼+0.6%**；形扫中位 **1.2%**，最差 **6.5%**（Table 14） |

机制（防御后果，非攻击）：CC 强制逐步 D2H token 回读同步 → overlap 调度串行 → GPU 利用率从约 74% 掉到约 57%。补丁核心是 **异步 D2H worker** 把回读移出关键路径。

**VRAM / 能耗（§6.1 / §10）：** 可用显存读数同为 **183 GB**；CC 固定划 **700 MB** 保护 framebuffer（KV 按比例吃满时要记账）。能耗**不升**——变慢时常因空闲更多而功耗更低。

### 4.6 多卡 MoE 生产面（MiniMax-M2.7，§7.5）

生产默认：overlap + piecewise graphs 开；融合 QK-norm、FP8/NVFP4 MoE runner、all-reduce fusion。

| 扫描 | 形状 | CC penalty（文） |
|---|---|---|
| 并发（1024-in / 2048-out） | c1→c128 | 噪声 → 平台约 **5.4%**（Table 17） |
| 序列（c32） | 512/512 → 4k/1k | **7.4% → 3.9%**（Table 18） |
| 长上下文 | 32k-in / 2048-out | **−0.4%**（噪声内，Table 19） |
| 输出长（1024-in, c32） | 256 → 2048 out | **14.4% → 1.1%**（Table 20） |
| **Pinned 典范点** | 1024/2048/c32，TP8 | **∼3%**（2.8–3.6%） |
| 同点 **TP4** | 同上 | **∼1.5%**，吞吐约 TP8 的 **94%** |

**并行杠杆（§7.4）：** 有 attention TP 时，加长输入 → 税升（更多加密 all-reduce）；**无 attention TP**（DP-attn + EP）时，加长输入 → 税降（固定开销被算力摊薄；32k 约 **2%**）。长上下文机密服务宜 **偏 EP/DP，忌过度 TP 切分**。

### 4.7 训练（Table 21）

8 卡 Megatron+TE：dense bf16 TP8 **∼13%**（1.13×）；tuned MoE EP8 **∼11%**；税在加密集合通信。文建议机密 8 卡训练默认 **bf16**（FP8 步更短，集合份额相对放大，税更高）。

### 4.8 EnclaveX 开销字段（H200 + Triton TRT-LLM，§5.1–5.2）

**三模式：** native（非 TDX Guest，GPU 非 CC） / **cvm**（TDX + GPU CC） / **scone**（EnclaveX 改 TDX + GPU CC）。模型：NVIDIA 优化 **Llama-3.1-8B-Instruct FP8**；Triton **25.01** + TensorRT-LLM **0.17.0**；硬件 SuperMicro SYS-322GA-NR + **H200 NVL 141GB**。

| 对比 | 指标 | 文内结果 |
|---|---|---|
| **SCONE vs CVM** | TPS / TBT / TTFT | **无显著开销**（SIM 模式：依赖 CVM 内存保护，不再二次加密内存；RQ1） |
| **CVM vs Native** | TPS | **35.0%–62.8%**，随 batch↑ 下降 |
| | TBT（ITL） | **35.2%–73.9%**，随 batch↑ 下降 |
| | TTFT | **11.2%–38.3%**，随输入长↑ 下降 |
| **Attestation** | native TDX+cGPU | 均值 **1.1611 s**（σ 0.0313；n=100） |
| | 应用层附加（SCONE） | 均值 **0.0147 s** → 合计约 **1.1758 s**，附加约 **+1.27%** |

RQ2 机制（防御侧）：cGPU 模式加密 CVM–cGPU IO（bounce buffer）→ 小 batch/短输入时 IO 税显眼；算力占比升则税降。文指出 TDX-Connect / SEV-IO 等 TEE-I/O 方向 NVIDIA cGPU **尚未支持**（引其 release notes）。

> **读数纪律：** Blackwell 文在 B200 + 打补丁 SGLang 上给出 **1–3%** 可达成点；EnclaveX 在 H200 + Triton 上给出的是 **CVM/CC vs 完全非机密 native** 的 **几十百分点** 面，且 **SCONE 相对 CVM 可忽略**。两表**机代、栈、对照基线不同**，禁止合成「TEE 一律 X%」。

---

## 五、部署建议（只写防御配置杠杆）

### 5.1 摘自 Blackwell §11（可跟读清单）

1. **始终 full CUDA graphs**——压掉 ∼12 µs/submission。
2. **用带 CC 补丁的框架**（异步 D2H worker）；未打补丁单卡常见 **30–40%**，打补丁可 **<1%**。
3. **权重与 KV 常驻 GPU**——避开热路径上的 CC-mode KV offload / CPU expert offload / weight streaming（撞 ∼10 GB/s 加密 PCIe）。
4. **TP 宽度按模型需要 right-size**；机密 MoE 上典范点 TP8∼3% vs TP4∼1.5%（94% 吞吐）；优先 **EP/DP-attention** 减 attention NVLE。
5. **偏 decode-heavy / 更长输出与上下文**——加密 prefill all-reduce 是主税；短 burst prefill-heavy 才到 low teens。
6. **接受残留 NVLink 地板**：配好后多卡 MoE 约 **1.5–3%**，极高并发可近 **∼5%**。
7. **可观测性改宿主侧**：GPU kernel profiling / CUDA event 在 CC 下按设计关闭 → guest CPU 时钟、NVTX、端到端吞吐。

### 5.2 跨节点结构难点（§9，未量化）

- CC guest **不支持** pinned host buffer（仅驱动 bounce buffer）。
- **GPUDirect RDMA 在启用 GPU CC 后直接不可用** → 跨节点要 GPU↔CPU↔CPU↔GPU，且仍走加密 bounce 路径。
- Prefill/decode 分离依赖快速 KV 传输时，集成难度高于非 CC；文**未**给出端到端分离测量。
- 展望：TDISP 等把设备 DMA 直接纳入机密 guest 可信边界后，有望去掉 bounce 绕路——**方向，非实测**。

### 5.3 EnclaveX 部署要点（边界，非攻击）

- 策略与密钥走 **CAS**；先证 CAS，再证 VM+GPU，再证应用，**最后**放解密密钥。
- Guest 关 memory dump；应用层证明把 **K8s admin** 移出密钥 TCB。
- 推理路径上可用 SCONE **SIM** 模式避免相对 CVM 的二次内存加密税（文 RQ1）。

---

## 六、与「通史 / 选型」的刻意留白

- **不写** Intel TDX / AMD SEV / ARM CCA / SGX 产品通史。
- **不写** Hopper→Blackwell 白皮书算力表（→ [[硬件软件协同部署]]）。
- **不写** 侧信道、投机执行利用、cache 攻击步骤（两文排除；观测关闭只记后果）。
- **不写** Bifrost TEE–FHE 混合等附录候选升格（agenda：可补链，不升主清单）。
- **不写** 跨节点 CC 吞吐数字（源文未测）。

---

## 七、可核断言速查

| 断言 | 出处 |
|---|---|
| 配好时 Blackwell 机密推理约 **1–3%**；错配 **30–40%** | 2608.26575 Abstract / §4 |
| 税两轴：host 操作 + NVLE 流量 | §4 / §7.1 |
| 单提交约 **+12 µs**；整步 graph → ∼1.04× | Table 5–6 |
| 单卡 overlap 开未打补丁 **34–39%**；打补丁 **<1%** | Table 12 / 14 |
| MoE TP8 pinned ∼**3%**，TP4 ∼**1.5%**（94% 吞吐） | §7.5 |
| 训练 8 卡 **10–13%** | Table 2 / 21 |
| CC 几乎不伤 GEMM/算力与能耗；VRAM +**700 MB** 固定 | §4 / §10 |
| EnclaveX：SCONE≈CVM；CVM vs native TPS **35–63%** | Fig.2 / RQ1–2 |
| 应用层 attestation 附加 ∼**+1.3%**（相对已有 CVM+cGPU 证明） | RQ3 |
| 侧信道排除；CUDA-event 计时在 CC 下关闭 | EnclaveX §3.1；Blackwell §3.3 / §9 |

---

## 八、本地路径

| 类型 | 路径 |
|---|---|
| 笔记 | 推理与基础设施/TEE机密推理.md |
| PDF | `https://arxiv.org/abs/2608.26575` · `https://arxiv.org/abs/2606.31408` |
| 抽取 | · |

## 相关笔记

- [[检索式注意力|RetrievalAttention]]
- [[TEE机密推理|TEE Confidential Inference]]
- [[模型合并|Model Merging]]
- [[ZeroQAT量化感知训练|ZeroQAT]]
- [[SeamlessM4T语音翻译|SeamlessM4T]]

