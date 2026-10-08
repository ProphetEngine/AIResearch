---
title: 时间线 · Infra · Serving · 硬件
topic: InfraServing发展时间线
date: 2026-10-08
type: timeline
status: active
---

# 时间线 · Infra · Serving · 硬件

> 本时间线梳理 AI 基础设施的关键转折，主线依次是：训练并行与通信，注意力算子，推理调度与 KV 显存管理，服务架构按阶段和模块拆分，模型侧的量化与端侧小模型，最后是机架级专家并行、FP4 部署和机密推理。贯穿始终的问题是算力、通信、显存和精度四者怎样先拆开、再协同。这一主题的共用背景集中写在本页，专题笔记只写各自的系统增量。日期口径：论文取 arXiv 首版（v1）日期，官方发布按 UTC 日期，系统卡取封面日期。会议论文取会议日期。

## 一、训练并行与通信（2018—2024）

模型超过单卡显存之后，训练首先要回答两个问题：模型和数据怎么切，切开之后怎么通信。这条线先解决「切得开」，即流水线、张量和 ZeRO 各自成形；再解决「组合得好」，即多维并行的配置法则；最后转向长序列与稀疏专家带来的上下文并行和专家并行。

- **2018-11** · GPipe 把一个批切成微批依次灌入流水线，并配合激活重计算，单卡装不下的模型可以按层切到多卡上同步训练（[arXiv:1811.06965](https://arxiv.org/abs/1811.06965)） · [[分布式训练并行策略]]
- **2019-09** · Megatron-LM 在层内切分矩阵乘做张量并行，只需在 PyTorch 中插入少量通信算子，就能把 8.3B 模型扩到 512 张 GPU 上。训练并行从改造框架变成可以复用的模式（[arXiv:1909.08053](https://arxiv.org/abs/1909.08053)） · [[AI基础设施总览]] · [[分布式训练并行策略]]
- **2019-10** · ZeRO 分三个阶段切分优化器状态、梯度和参数，去掉数据并行中每张卡各存一份完整副本的冗余，同样的显存能训练大得多的模型（[arXiv:1910.02054](https://arxiv.org/abs/1910.02054)） · [[分布式训练并行策略]]
- **2020-06** · GShard 把稀疏 MoE 的专家分片到 2048 个 TPU v3 上训练 600B 级模型，专家并行成为继数据、张量、流水线之后的又一个切分维度（[arXiv:2006.16668](https://arxiv.org/abs/2006.16668)） · [[分布式训练并行策略]]
- **2021-04** · Megatron-LM 团队系统研究张量、流水线、数据三维并行的组合（PTD-P），并提出交错式 1F1B 调度，三维并行有了可遵循的配置法则（[arXiv:2104.04473](https://arxiv.org/abs/2104.04473)） · [[分布式训练并行策略]]
- **2023-04** · PyTorch FSDP 把 ZeRO-3 式的全分片数据并行做进框架核心，成为开放社区训练大模型的常用方案（[arXiv:2304.11277](https://arxiv.org/abs/2304.11277)） · [[分布式训练并行策略]]
- **2023-09** · DeepSpeed-Ulysses 按注意力头做 all-to-all，次月的 Ring Attention 让 K/V 按块在设备环上依次传递。序列维度也能切到多卡上，长上下文训练有了两条上下文并行路线（[arXiv:2309.14509](https://arxiv.org/abs/2309.14509)；[arXiv:2310.01889](https://arxiv.org/abs/2310.01889)） · [[分布式训练并行策略]]
- **2023-11** · Zero Bubble Pipeline Parallelism 把反向传播拆成「对输入求梯度」和「对权重求梯度」两部分分别调度，在同步语义下做到流水线零气泡（[arXiv:2401.10241](https://arxiv.org/abs/2401.10241)） · [[分布式训练并行策略]]
- **2024-07** · Llama 3 报告公开张量、上下文、流水线与 FSDP 四维并行的生产配置，以及按网络层级安排各维并行的原则（[arXiv:2407.21783](https://arxiv.org/abs/2407.21783)） · [[分布式训练并行策略]]
- **2024-12** · DeepSeek-V3 用大规模专家并行加 DualPipe 双向流水，训练中不用张量并行，并采用 FP8 混合精度；推理部署方案也一并公开，基础设施设计成为模型竞争力的一部分（[arXiv:2412.19437](https://arxiv.org/abs/2412.19437)） · [[AI基础设施总览]]

## 二、连续批处理、分页显存与推理引擎（2022—2023）

推理侧的难点与训练不同：逐 token 解码时算力利用率低，KV 缓存占满显存，调度和显存管理成为吞吐的瓶颈。

- **2022-07** · Orca（OSDI 2022）把调度粒度从整批请求改为单次迭代：早结束的请求立即返回，新请求随时插入。这就是业界所说的连续批处理，此后成为 LLM 服务的基础（[OSDI 2022 论文页](https://www.usenix.org/conference/osdi22/presentation/yu)） · [[连续批处理与Orca]]
- **2022-11** · 投机解码由小模型起草、大模型并行校验，输出分布不变，大模型的串行步数减少；Chen 等人于 2023-02 独立提出同类方法（[arXiv:2211.17192](https://arxiv.org/abs/2211.17192)；[arXiv:2302.01318](https://arxiv.org/abs/2302.01318)） · [[推理引擎生态]]
- **2023-07** · FlashAttention-2 在 FlashAttention（2022-05）分块计算精确注意力的基础上，改进线程块并行与工作划分，注意力算子的效率接近矩阵乘（[arXiv:2307.08691](https://arxiv.org/abs/2307.08691)） · [[AI基础设施总览]]
- **2023-09** · vLLM 的 PagedAttention 借用操作系统分页，把 KV 缓存按块管理，消除碎片并支持跨请求共享，vLLM 由此成为开源服务引擎的事实基线（[arXiv:2309.06180](https://arxiv.org/abs/2309.06180)） · [[推理引擎生态]]
- **2023-12** · SGLang 用 RadixAttention 自动复用请求间的相同前缀，并把多步调用写成结构化程序执行，引擎优化从单次请求扩展到整个调用程序（[arXiv:2312.07104](https://arxiv.org/abs/2312.07104)） · [[推理引擎生态]] · [[Prompt前缀缓存]]

## 三、拆分服务与压缩模型（2024—2025）

服务规模扩大后，prefill 与 decode、注意力与专家、云端与端侧的资源需求明显分化。系统开始按阶段、按模块拆分；模型侧则用量化、专用内核和小模型降低部署成本。

- **2024-01** · DistServe 把 prefill 与 decode 放进不同的 GPU 池，两阶段不再互相干扰，并以满足延迟目标的有效吞吐（goodput）作为优化目标（[arXiv:2401.09670](https://arxiv.org/abs/2401.09670)） · [[PrefillDecode分离与统一服务]]
- **2024-01** · KVQuant 与次月的 KIVI 把 KV 缓存压到 2—4 比特，同样的显存能放下更长的上下文或更多并发请求（[arXiv:2401.18079](https://arxiv.org/abs/2401.18079)；[arXiv:2402.02750](https://arxiv.org/abs/2402.02750)） · [[KV缓存量化与压缩]]
- **2024-02** · MobileLLM 指出在十亿参数以下，「深而窄」优于「浅而宽」，并配合权重共享，端侧小模型有了专门的架构配方（[arXiv:2402.14905](https://arxiv.org/abs/2402.14905)） · [[端侧小模型]]
- **2024-03** · NVIDIA 发布 Blackwell 平台：FP4 进入数据中心张量核心，NVL72 机架用 NVLink 把 72 张 GPU 连成一个整体。硬件代际开始直接决定低精度部署和大规模专家并行的成本（[NVIDIA 新闻稿](https://nvidianews.nvidia.com/news/nvidia-blackwell-platform-arrives-to-power-a-new-era-of-computing)） · [[硬件软件协同部署]]
- **2024-05** · SpinQuant 用学习得到的旋转矩阵抹平激活离群值，权重和激活都能做低比特训练后量化（[arXiv:2405.16406](https://arxiv.org/abs/2405.16406)） · [[SpinQuant与ARCQuant量化]]
- **2024-10** · ThunderKittens 以 16×16 tile 为基本抽象编写 GPU 内核，用少量代码就能接近厂商库的性能，高性能内核的开发门槛明显下降（[arXiv:2410.20399](https://arxiv.org/abs/2410.20399)） · [[ThunderKittens内核DSL]]
- **2024-12** · Phi-4（14B）以合成数据为主训练，报告主张小模型的能力提升更多依赖数据配方而非规模（[arXiv:2412.08905](https://arxiv.org/abs/2412.08905)） · [[端侧小模型]]
- **2025-02** · DeepSeek 开源 DeepEP，基于 NVSHMEM 由 GPU 端直接发起专家并行的 all-to-all 通信，MoE 的通信开始绕开主机侧的集合通信库自建（[deepseek-ai/DeepEP README](https://github.com/deepseek-ai/DeepEP)） · [[NVSHMEM与DeepEP通信]]
- **2025-04** · MegaScale-Infer 复制注意力模块、切开专家模块，分别部署扩展（解耦专家并行），解决 MoE 解码时专家 GPU 吃不饱的问题（[arXiv:2504.02263](https://arxiv.org/abs/2504.02263)） · [[MegaScaleInfer与UltraEP]]
- **2025-04** · Google 发布第七代 TPU Ironwood，官方称是第一款面向推理的 TPU，专用加速器的设计重心从训练转向推理（[Google 博文](https://blog.google/products/google-cloud/ironwood-tpu-age-of-inference/)） · [[硬件软件协同部署]]
- **2025-08** · TaiChi 不再在「聚合」与「解聚」之间二选一，用能力分化的实例和延迟转移覆盖任意首 token 延迟与单 token 延迟组合下的有效吞吐（[arXiv:2508.01989](https://arxiv.org/abs/2508.01989)） · [[PrefillDecode分离与统一服务]]
- **2025-08** · ZeroQAT 用零阶方法从前向传播估计梯度，去掉反向传播，以接近推理的成本做端到端量化感知训练，手机上也能做 QAT（[arXiv:2509.00031](https://arxiv.org/abs/2509.00031)） · [[ZeroQAT量化感知训练]]
- **2025-09** · SGLang HiCache 把 KV 缓存从 GPU 显存扩展到主机内存和分布式存储三级，统一挂在一棵前缀树上，可复用的前缀容量大幅扩大（[LMSYS 博文](https://www.lmsys.org/blog/2025-09-10-sglang-hicache/)） · [[HiCache层次化KV缓存]]
- **2025-11** · MobileLLM-Pro（1.08B）用隐式位置蒸馏把上下文扩到 128K，并做 4-bit 量化感知训练，端侧基础模型开始具备长上下文能力（[arXiv:2511.06719](https://arxiv.org/abs/2511.06719)） · [[MobileLLM端侧增量]]

## 四、机架级专家并行、FP4 与可信部署（2026）

MoE 旗舰把专家并行推到机架规模，FP4 成为部署的主力精度，云端推理同时面临「数据在使用中」的隐私保护要求。

- **2026-01** · ARCQuant 用增广残差通道补偿 NVFP4 的量化误差，部署量化随硬件精度进入 FP4（[arXiv:2601.07475](https://arxiv.org/abs/2601.07475)） · [[SpinQuant与ARCQuant量化]]
- **2026-02** · Dr. Kernel 用强化学习训练模型生成 Triton 内核，内核编写开始由模型参与（[arXiv:2602.05885](https://arxiv.org/abs/2602.05885)） · [[ThunderKittens内核DSL]]
- **2026-03** · MobileLLM-Flash 以真机延迟为目标做硬件在环的架构搜索，端侧模型设计从参数量导向转向延迟导向（[arXiv:2603.15954](https://arxiv.org/abs/2603.15954)） · [[MobileLLM端侧增量]]
- **2026-06** · UltraEP 在机架级高速互联域内，按门控后的精确负载当场分配配额、复制热点专家，MoE 训练与推理的吞吐逼近完全均衡的理想值（[arXiv:2606.04101](https://arxiv.org/abs/2606.04101)） · [[MegaScaleInfer与UltraEP]]
- **2026-06** · 「Demystifying NVSHMEM」系统剖析对称内存与设备端发起的通信，解释了稀疏专家并行为什么适合在其上自建 dispatch 与 combine（[arXiv:2606.05951](https://arxiv.org/abs/2606.05951)） · [[NVSHMEM与DeepEP通信]]
- **2026-06** · EnclaveX 打通 CPU 与 GPU 的可信执行环境，实现端到端机密推理，并给出远程证明链（[arXiv:2606.31408](https://arxiv.org/abs/2606.31408)） · [[TEE机密推理]]
- **2026-08** · 在 Blackwell B200 上实测机密计算模式的吞吐开销，机密推理从可行性论证进入成本测量（[arXiv:2608.26575](https://arxiv.org/abs/2608.26575)） · [[TEE机密推理]]

## 相关

- [[投机解码发展时间线]]：投机解码的独立时间线，本页只保留 2022-11 一个交汇节点。
- [[长上下文与注意力效率时间线]]：注意力变体与 KV 压缩的架构侧时间线，与本页在分页注意力、前缀缓存和 KV 量化上交汇。
- [[预训练与架构发展时间线]]：预训练架构、MoE 路由与数据侧的时间线；本页第一段的训练并行节点是它的系统侧对应。
- [[分布式训练并行策略]]：本页第一段各训练并行节点的机制说明（五种并行、ZeRO/FSDP、流水线气泡）。
- [[MOC_推理与基础设施]]：推理与基础设施的主题地图，按子主题组织本页各笔记。
- [[Transformer至今发展脉络]]：全库总史，本页细化其中 AI Infra 这一支。

## 局限与待核实

- DeepEP 没有独立论文，2025-02 依据 GitHub 仓库与 DeepSeek 开源周索引页；具体公开日未单独核对。
- arXiv 编号月份与首版日期不一致、按首版记的条目：Zero Bubble Pipeline Parallelism（编号 2401，首版 2023-11-30）、ZeroQAT（编号 2509，首版 2025-08-21）。
- 按首版计的年月可能早于相关笔记材料表所记的修订版或会议版日期。
