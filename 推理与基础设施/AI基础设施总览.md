---
title: AI Infra「势」：训练并行、推理 serving、量化与硬件协同
topic: AI基础设施总览
date: 2026-09-22
lines: [AI Infra, 架构思想]
status: archived
archived: 2026-09-22
---

# 10　AI Infra「势」：训练并行、推理 serving、量化与硬件协同

入口论文 / 报告：

- Shoeybi et al., *Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism* (arXiv:1909.08053；下文称 Megatron 论文)。
- Dao, *FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning* (arXiv:2307.08691；下文称 FA2 论文)；其前身 FlashAttention 记为 Dao et al. [5]（文中引用）。
- Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention* (arXiv:2309.06180；下文称 vLLM / PagedAttention 论文)。
- DeepSeek-AI, *DeepSeek-V3 Technical Report* (arXiv:2412.19437；下文称 V3 报告) **§3 Training Framework / FP8 / Inference**。

本笔记以 **AI Infra** 为主线、**架构思想** 为辅线：跟读「算力—通信—显存—精度」如何被拆开再协同。吞吐与效率数字一律取自原文摘要/正文，不编造未读到的对比表或外推百分比。

---

## 一、为何 Infra 从幕后变战略变量

早期深度学习叙事里，Infra 常被当成「把模型跑起来的工程细节」。当代大模型把三件事同时推到极限之后，Infra 本身成为**能力与成本的一阶变量**：

1. **参数量与优化器状态**：单卡装不下权重与 ADAM 等状态（Megatron §1、§2.3）。
2. **序列长度平方**：注意力 runtime / 显存随 $N$ 二次增长；标准实现还要把 $S=QK^\top$、$P=\mathrm{softmax}(S)$ 物化到 HBM（FA2 §1、§2.2）。
3. **推理侧动态 KV**：自回归 decode 下 KV cache 随请求动态涨缩，占满显存就卡死 batch，吞吐上不去（vLLM §1；13B 模型在 A100 40GB 上 KV 约可占内存布局的 ~30%，权重约 65%——图 1 叙述）。

因此「谁能训更大 / 更长 / 更便宜地服更大并发」，不再只是算法论文的附录，而是与架构选型（稀疏 MoE、MLA、量化）绑死的**系统—硬件联合设计**。跟读抓手可以记成一条链：

> **训练并行（切参数 / 切层 / 切数据）→ 注意力核（IO-aware，少搬 HBM）→ 推理 KV 管理（分页，近零浪费）→ 低精度与网络拓扑协同（FP8、all-to-all、NVLink/IB）**。

Megatron 把「层内张量切分」做成少通信的 PyTorch 原语；FlashAttention 族把注意力从「算力问题」重写为「带宽 / 占用率问题」；PagedAttention 把 OS 虚拟内存思想搬进 serving；DeepSeek-V3 则在 MoE + 跨节点通信已经接近 1:1 算通比时，用 DualPipe、定制 all-to-all 与 FP8 把 Infra 写成可复现的训练报告章节。

---

## 二、训练侧：张量 / 流水线 / 数据并行（Megatron 思想）与专家并行衔接

### 2.1 三种经典并行（背景语言）

Megatron §2.3 把扩展训练收成两条中心范式，并点出层内张量切分与流水线的正交性：

| 范式 | 切什么 | 典型代价 |
|------|--------|----------|
| **数据并行 (DP)** | 样本 / batch | 梯度同步；弱扩展时常近线性，但过大 batch 可能伤收敛（文中转述） |
| **流水线并行 (PP)** | 层组到不同设备 | 流水气泡、激活在设备间传递；GPipe 等需框架/编译器（§1） |
| **张量 / 模型并行 (TP，文中称 intra-layer model parallelism)** | 单层内的矩阵 / 头 | 层内 all-reduce；Megatron 目标是**少同步、保持算力绑定** |

Megatron 强调其方法与流水线**正交且可互补**，且不依赖新编译器：只需在原生 PyTorch 里插入少量通信算子（摘要、§1）。

### 2.2 Megatron 的「列切 + 行切」：把非线性留在分区内

Transformer 一层 = 自注意力 + 两层 MLP。Megatron §3 对 MLP 的 GEMM $Y=\mathrm{GeLU}(XA)$ 给出两种切法：

1. **按行切 $A$、按列切 $X$**：会得到 $Y=\mathrm{GeLU}(X_1A_1+X_2A_2)$，因 GeLU 非线性，**不能**拆成各分区 GeLU 再加，GeLU 前必须同步。
2. **按列切 $A=[A_1,A_2]$**：各分区独立算 $[Y_1,Y_2]=[\mathrm{GeLU}(XA_1),\mathrm{GeLU}(XA_2)]$，**去掉 GeLU 前的同步点**。第二层 GEMM 再按行切，直接吃 GeLU 输出；第二次 GEMM 后再 all-reduce。

自注意力同理（§3、Figure 3b）：Q/K/V 的 GEMM **列并行**，使每个 attention head 的矩阵乘落在本地 GPU，**做完 self-attention 前不必通信**；输出投影再**行并行**。MLP 与注意力各自「两段 GEMM 融成一组」，一层里前向只需 **2 次 all-reduce**，反向亦 2 次（Figure 4 合计前向+反向共 4 次通信）。

词表很大时，输出 embedding 也按词表维列切；若先 all-gather logits 再算交叉熵，通信量是 $b\times s\times v$。Megatron 把并行 GEMM 输出与交叉熵**融合**，只通信标量损失量级（约 $b\times s$），大幅降通信（§3）。

**架构思想一句**：并行策略的优劣不在「切得细不细」，而在**非线性与归约放在哪一侧**——把可局部分解的算子留在分区内，把不可避免的同步压到最少次数。

### 2.3 原文规模与效率数字（仅报告文中数字）

- 单卡强基线：约 **1.2B** 参数，单块 **NVIDIA V100 32GB**，整应用维持 **39 TeraFLOPs**，约峰值的 **30%**（DGX-2H 配置叙述，摘要 / §1）。
- 扩展：约 **8.3B** 参数，**512 GPU**，**8-way** 模型并行，维持最高约 **15.1 PetaFLOPs**，相对单卡基线 **76%** 扩展效率（摘要、§1、Figure 1）。
- 弱扩展叙事：约 **每 GPU 1B** 参数量级的 8-way 模型并行；再叠 **64-way** 数据并行（Figure 1 说明）。

精度侧：混合精度 + 动态 loss scaling，以利用 V100 Tensor Cores（§4.2）。BERT 类模型上，Megatron 另强调 **LayerNorm 放置**对「变大不掉点」至关重要（摘要、贡献列表）——这是架构细节对 Infra 扩展叙事的反作用。

### 2.4 与专家并行（EP）的衔接：从「切矩阵」到「切专家 + 切网络」

Megatron 原文主战场是稠密 Transformer 的 **TP(+DP)**，尚未展开当代细粒度 MoE 的跨节点 all-to-all。跟读当代时，把并行维度扩成：

- **TP**：仍切注意力 / 稠密线性的大矩阵（通信相对「结构化」：all-reduce）。
- **PP**：切层；气泡与激活驻留是主矛盾。
- **DP / ZeRO**：切优化器状态与梯度。
- **EP**：把不同专家放在不同 GPU/节点；token 经 **dispatch / combine（all-to-all）** 流动——通信量可与算力同量级。

V3 报告给出一条可跟读的「后 Megatron」组合（§3.2）：训练用 **16-way PP + 64-way EP（跨 8 节点）+ ZeRO-1 DP**，并写明通过显存优化 **不使用昂贵的 TP** 即可训 V3。跨节点 EP 下，报告称算通比恶化到约 **1:1**，于是用 **DualPipe** 把单个 forward/backward chunk 拆成 `attention | all-to-all dispatch | MLP | all-to-all combine`（反向再拆 input/weight），双向灌 micro-batch，力图把 all-to-all 与 PP 通信**藏进计算**（§3.2.1、Figure 4–5）。网络侧：节点间 IB、节点内 NVLink；NVLink 带宽叙述为约 **160 GB/s**，约 IB（**50 GB/s**）的 **3.2×**；配合「每 token 最多发往 **4** 个节点」的路由限制，使 IB 与 NVLink 传输重叠（§3.2.2）。

**跟读抓手**：Megatron 解决的是「一层矩阵怎么切才少同步」；MoE 时代的 Infra 还必须回答「专家散落在多机时，**通信能否被算力盖住**」——DualPipe / 定制 all-to-all 是对后者的公开答案，不是对前者的否定。

---

## 三、注意力核：FlashAttention-2 解决什么（IO-aware）

### 3.1 问题重述：标准注意力为何「算得慢」

FA2 §2.2：对 $Q,K,V\in\mathbb{R}^{N\times d}$，标准路径是

1. GEMM 得 $S=QK^\top$ → 写回 HBM；
2. 从 HBM 读 $S$ 做 softmax → 写 $P$；
3. GEMM 得 $O=PV$。

当 $N\gg d$（文中典型 $N$ 约 1k–8k，$d$ 约 64–128）时，$S,P$ 是 $O(N^2)$ 中间量，**多数算子受内存带宽限制**；反向还要存 $P$（§2.2）。

GPU 侧不对称层级（§2.1，A100 为例）：**HBM** 约 40–80GB、带宽约 **1.5–2.0 TB/s**；每 SM 上 **SRAM（shared memory）** 约 **192KB**、带宽估计约 **19 TB/s**。FlashAttention 的核心不是近似注意力，而是 **IO-aware**：少碰慢的 HBM，多在快的 SRAM 里算完。

### 3.2 FlashAttention（前身）在做什么

FA2 §2.3 转述 FlashAttention：

- **Tiling**：块状从 HBM 装入 SRAM，对块算注意力，用 **online softmax** 重缩放，最终得到与标准 softmax 相同的 $O$（无近似）。
- **不把 $S,P$ 写回 HBM** → 墙钟约 **2–4×** 于优化基线；显存从二次降到对 $N$ **线性**，反向约 **10–20×** 显存节省（取决于序列长度）。

即便如此，FlashAttention 相对优化 GEMM 仍偏慢：摘要称其仅达理论峰值 FLOPs/s 的约 **25–40%**；正文细化前向约 **30–50%**、反向约 **25–35%**（A100），而优化 GEMM 可达约 **80–90%**（§1）。根因被诊断为 **thread block / warp 之间工作划分不佳** → 低 occupancy，或多余的 shared memory 读写。

### 3.3 FlashAttention-2：三条「更好的并行与划分」

摘要与 §3 的三项改动（跟读时可逐条对照 Algorithm 1）：

1. **减少 non-matmul FLOPs**（§3.1）：GPU 上 matmul（Tensor Core）远快于一般 FLOP。A100 例：FP16/BF16 matmul 理论峰值约 **312 TFLOPs/s**，非 matmul FP32 仅约 **19.5 TFLOPs/s**——约 **16×** 代价差。算法微调 online softmax 更新，使更多时间花在 matmul 上，输出不变。
2. **沿序列维并行**（§1、§3）：除 batch、head 外，对**单个 head** 也按序列长度拆到不同 thread block，提高长序列（常伴随小 batch）时的 occupancy。
3. **block 内 warp 划分**（§1、§3）：减少 warp 间经 shared memory 的通信与读写。

**因果 mask**：按块跳过整块上三角；文中称相对无因果约 **1.7–1.8×**；每行通常只需对约 1 个边界块做 mask（§3.1.1）。

### 3.4 原文速度数字（仅报告文中数字）

- 相对 FlashAttention：约 **2×** 加速（摘要；§3 亦写改进带来约 **2–3×**，以 §4 验证为准）。
- 设备利用率：达理论最大 FLOPs/s 的约 **50–73%**（A100），接近 GEMM 效率（摘要）。
- 端到端训 GPT 风格模型：最高约 **225 TFLOPs/s per A100**（约 **72%** model FLOPs utilization）（摘要、§1、§4 叙述）。

**架构思想一句**：注意力 Infra 的主线不是「换公式」，而是承认 **HBM↔SRAM 的不对称**，用 tiling + 重计算 + 占用率友好的并行，把二次中间态留在片上——这与 Megatron「少通信、保持 compute-bound」是同一哲学在不同层级的投影。

---

## 四、推理 serving：PagedAttention 与量化 / 低精度（衔 DeepSeek-V3 FP8 等公开要点）

### 4.1 为何 serving 卡在 KV，而不是「再加几张卡」

vLLM §1–§3：自回归服务可拆 **prompt（prefill）** 与 **autoregressive generation（decode）**。Prefill 可矩阵并行，相对吃得饱算力；decode 逐步依赖已缓存 K/V，常呈 **memory-bound**，GPU 算力闲置。提吞吐要靠 **batch 多请求**，但 KV 动态增长且长度先验未知。

既有系统常把每条请求的 KV 放在**连续**预留块（按最大长度，如 2048），导致三类浪费（Figure 2–3）：

- **预留未用**（reserved）；
- **内部碎片**（实际长度远短于最大长度）；
- **外部碎片**（不同预留尺寸）。

剖析显示：现有系统 KV 内存中真正存 token 状态的比例可低至约 **20.4%–38.2%**（§1、Figure 2）。复杂解码（并行采样、beam search）本可共享前缀 KV，连续布局也难以做块级共享。

### 4.2 PagedAttention：把 OS 分页搬进注意力

思想（§1、§4.1）：把一条序列的 KV 切成固定 token 数的 **block（页）**；逻辑上连续的序列，物理上可非连续。类比：block ≈ page，token ≈ byte，request ≈ process。

注意力按块取 K/V（式 (4)）：内核按 block table 分别取非连续块，乘 query，累加输出（Figure 5）。收益：

1. **近零浪费**：按需分配小块，消除内外碎片叙事下的主浪费；
2. **块级共享**：同请求多序列 / 跨请求可共享物理块（beam、并行采样）；
3. 与 **iteration-level scheduling**、抢占式调度共设计（系统概述 Figure 4）。

**原文吞吐表述**：相对 FasterTransformer、Orca 等，同延迟水平下流行 LLM 吞吐约 **2–4×**；更长序列、更大模型、更复杂解码时更明显（摘要、§1）。跟读时注意：这是论文评估区间，不是「任意部署保证 2–4×」。

### 4.3 量化 / 低精度：训练 FP8 与推理部署（DeepSeek-V3 公开要点）

V3 把「精度」写进 Infra 主文，而不是附录技巧：

**规模与代价（报告摘要 / Table 1）**：总参 **671B**，每 token 激活 **37B**；全流程约 **2.788M H800 GPU hours**（预训练 2664K + 上下文扩展 119K + 后训练 5K）。架构侧复用 **MLA**（降 KV）与 **DeepSeekMoE**（细粒度专家）；Infra 侧宣称首次在极大规模上验证 **FP8 混合精度预训练**可行性。

**FP8 混合精度框架（§3.3）**（公开要点，跟读用）：

- 多数高密度 **GEMM（Fprop / Dgrad / Wgrad）走 FP8**，输出可为 BF16/FP32；相对 BF16，理论算力叙述为约 **翻倍**（§3.3.1）。
- **保留高精度**的模块：embedding、输出头、MoE gating、normalization、**attention**；master weight / 梯度 / 优化器状态更高精度（§3.3.1）。
- **细粒度量化**抗 outlier：激活按 **1×128 tile**（每 token 每 128 channel）缩放；权重按 **128×128 block** 缩放（§3.3.2）。
- **提高累加精度**：H800 上 FP8 Tensor Core 累加有效位宽有限；每隔 $N_C=128$ 元素把部分和 **promote 到 CUDA Core 上做 FP32 累加**（§3.3.2）。
- 全张量采用 **E4M3**（相对部分工作 Fprop 用 E4M3、反向用 E5M2 的混合），依赖细粒度缩放撑动态范围；**在线**按 tile/block 算 max 再量化（§3.3.2）。
- 通信与缓存：MoE dispatch 前激活可 FP8；combine 关键路径保留 BF16；AdamW 一二阶矩可用 BF16（§3.3.3）。
- 验证叙述：在类似 V2-Lite / V2 规模上训约 1T token，相对 BF16 的相对 loss error 持续 **低于 0.25%**（§3.3）。

**推理部署（§3.4）**：prefill 与 decode **分阶段**部署以兼顾 SLO 与吞吐。

| 阶段 | 最小部署单元（报告） | 注意力 | MoE |
|------|----------------------|--------|-----|
| Prefilling | 4 节点 / 32 GPU | TP4 + SP + DP8 | EP32；冗余专家 32 个等 |
| Decoding | 40 节点 / 320 GPU | TP4 + SP + DP80 | EP320；每 GPU 一专家等 |

Prefill 用双 micro-batch 重叠 attention/MoE 与 dispatch/combine；decode 侧 batch/专家较小（常 $\le 256$ token），瓶颈偏访存，可用较少 SM 做 dispatch+MoE+combine，把更多资源留给 attention（§3.4.2）。路由侧另有冗余专家、周期性按在线负载调整等——与训练时的 node-limited routing / 无 token-dropping 叙事一致（架构章 + §3.4）。

**与 PagedAttention 的衔接（思想层，非原文实验）**：PagedAttention 管的是 **KV 布局与碎片**；MLA / GQA 管的是 **每 token KV 体积**；FP8 / 低精度管的是 **算与传的位宽**。三者叠乘才构成当代 serving「势」：同一 GPU、同一延迟预算下，能塞进更大有效 batch。

---

## 五、常见误区与引用

### 5.1 常见误区

1. **「模型并行 = 流水线」**：Megatron 主贡献是 **层内张量并行**；流水线是正交选项。把 GPipe 与 Megatron 混称「同一种并行」会读错通信形态（all-reduce vs 激活传递 / 气泡）。
2. **「FlashAttention 是近似注意力」**：FA2 明确 **no approximation**，正确性同标准 $\mathrm{softmax}(QK^\top)V$；省的是 HBM 上的 $S,P$，不是数学定义。
3. **「FA2 数字可直接当自家集群 SLA」**：文中 **225 TFLOPs/s、50–73%、2×** 均绑定 A100 / 其实验设置；换精度、头维、是否因果、实现版本都会变。
4. **「vLLM 一定 2–4×」**：该区间是相对 FasterTransformer / Orca 等、在论文工作负载上的结果；连续预分配若已极优化、或瓶颈已在别的子系统，倍率不可外推。
5. **「量化只是推理压缩」**：V3 把 **FP8 预训练**写成主文，并区分哪些算子必须留 BF16/FP32；把「推理 INT8/INT4」与「训练 FP8」混为一谈会漏掉累加精度、tile 缩放、通信路径精度等关键设计。
6. **「有了 EP 就不需要 TP / 反之」**：V3 训练叙事是大 EP + DualPipe **省掉 TP**；其 **推理** prefill 仍用 **TP4**。并行维度随阶段（训 / prefill / decode）切换，不是全局唯一最优。
7. **编造未写明的吞吐**：本笔记禁止把「某博客说的 tokens/s」写进正文；若需更新数字，应回到对应论文表图或官方复现说明。

### 5.2 核心引用

- Shoeybi, M., Patwary, M., Puri, R., LeGresley, P., Casper, J., & Catanzaro, B. (2019/2020). *Megatron-LM: Training Multi-Billion Parameter Language Models Using Model Parallelism*. arXiv:1909.08053. PDF: `https://arxiv.org/abs/1909.08053`
- Dao, T. (2023). *FlashAttention-2: Faster Attention with Better Parallelism and Work Partitioning*. arXiv:2307.08691. PDF: `https://arxiv.org/abs/2307.08691`
- Kwon, W., Li, Z., Zhuang, S., Sheng, Y., Zheng, L., Yu, C. H., Gonzalez, J. E., Zhang, H., & Stoica, I. (2023). *Efficient Memory Management for Large Language Model Serving with PagedAttention*. arXiv:2309.06180. PDF: `https://arxiv.org/abs/2309.06180`
- DeepSeek-AI (2024/2025). *DeepSeek-V3 Technical Report*. arXiv:2412.19437. PDF: `https://arxiv.org/abs/2412.19437`
- 相关背景（本议题引用链）：Huang et al., GPipe；Dao et al., FlashAttention；Vaswani et al., Attention Is All You Need；Lepikhin et al. / Fedus et al. 等 MoE 并行文献（见 V3 / Megatron 参考文献列表）。

### 5.3 待核实 / 延伸

- Megatron 后续开源栈（Megatron-Core、Megatron-LM 新版本）中的 **序列并行、上下文并行、分布式优化器** 等：本笔记以 1909.08053 正文为准，未逐项对照 2024+ 代码默认策略。
- FlashAttention-3 / 更新内核在 Hopper/Blackwell 上的占用率与精度路径：未纳入本次 PDF 精读。
- vLLM 生产版本相对论文的调度器、前缀缓存、多模态 KV：论文保证的是 PagedAttention 思想与当时评测倍率。
- V3 报告中 DualPipe 气泡公式在 Table 2 的排版（PDF 提取有折行）；引用气泡复杂度时建议回看原表而非仅依赖文本提取。
- 硬件建议章（V3 §3.5）对厂商通信 / 低精度原语的诉求：属作者建议，非第三方实测。

---

*笔记状态：draft · 攻坚线 AI Infra（主）+ 架构思想（辅）· 可跟读*

## 相关笔记

### P0
- [[注意力与Transformer核心思想|Attention / Transformer]]
- [[DecoderOnly与GPT路线|Decoder-only / GPT]]
- [[规模定律与预训练范式|规模定律与预训练]]
- [[混合专家架构|MoE / 稀疏激活]]
- [[对齐脉络RLHF与偏好优化|对齐 RLHF / DPO]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿模型谱系]]

### P1
- [[长上下文位置编码与系统侧|长上下文]]
- [[多模态架构脉络|多模态]]
- [[AI基础设施总览|AI Infra]]
- [[注意力效率族MQA到MLA|注意力效率]]
- [[LLaMA开源生态里程碑|LLaMA 生态]]


