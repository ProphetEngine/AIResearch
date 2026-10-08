---
title: "技术报告专项：DeepSeek-V3 报告深读切片"
topic: DeepSeekV3训练与MoE基建
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2412.19437
sources:
 - https://arxiv.org/abs/2412.19437
 - https://github.com/deepseek-ai/DeepSeek-V3
related: ["混合专家架构", "注意力效率族MQA到MLA", "MTP训练范式", "AI基础设施总览", "NVSHMEM与DeepEP通信", "DeepSeekR1推理训练深读", "DeepSeekV32技术报告深读", "DeepSeekV4技术报告深读", "KimiK2技术报告深读", "开源与闭源前沿模型谱系", "分布式训练并行策略", "MoE路由与负载均衡"]
archived: 2026-09-22
---

# 技术报告专项：DeepSeek-V3 报告深读切片

> **主要来源**：[DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437)（DeepSeek-AI，v2，2025-02-18；首次提交 2024-12-27）；[deepseek-ai/DeepSeek-V3 README](https://github.com/deepseek-ai/DeepSeek-V3)（GitHub 仓库说明，活页面，无更新日期）（截至 2026-04-26）。
> **研究线**：架构思想（DeepSeekMoE 路由与无辅助损失均衡、MTP，主）· AI Infra（PP × EP × ZeRO-1、DualPipe、跨节点 all-to-all、FP8 训练，辅）
> **范围与相邻笔记**：
> - ≠ [[混合专家架构]]：本篇不写 Switch → Mixtral → V3 的 MoE 史线。
> - ≠ [[注意力效率族MQA到MLA]]：本篇不写 MLA 的低秩压缩推导，只列 V3 的取值。
> - ≠ [[AI基础设施总览]]：本篇不写 Megatron、FlashAttention、vLLM 等通论。
> - ≠ [[开源与闭源前沿模型谱系]]：本篇不写开闭源代际坐标。
>
> **意义**：V3 用约 2.788M H800 GPU 小时训出 671B 总参、37B 激活的开放权重 MoE，并公开了做到这一点的整套工程：无辅助损失的负载均衡、限节点路由与 DualPipe 让跨节点专家并行的通信几乎全被计算掩盖，报告称首次在这一规模上验证了 FP8 混合精度训练的可行性。此后 R1、V3.2、V4 都在这个底座上演进，其他开放权重 MoE（如 Kimi K2）也以它为参照。

**一句话**：V3 的效率来自三处协同：细粒度专家 + 共享专家 + 偏置式负载均衡让专家更特化而不伤主任务；每 token 最多路由到 4 个节点，配合 DualPipe 把 all-to-all 与流水线通信藏进计算；FP8 用细粒度分块缩放与定期提升到 FP32 累加控制误差。

---

## 一、问题背景

MoE 能把总参数与每 token 计算量解耦，但规模化有三个工程难题。其一，负载均衡：传统做法加辅助损失逼路由均匀，损失太大会伤主任务。其二，通信：细粒度专家分散在很多节点上，跨节点专家并行时计算与通信之比约为 1:1（原文 §3.2），通信直接拖慢训练。其三，精度与显存：在数千卡上用更低精度训练能省算力和显存，但此前没有在这种规模上验证过 FP8 训练的稳定性。

V3 的报告目标是在有限算力（2048 张 H800）上把这三点同时解决，并让训练全程不出现不可恢复的 loss 尖峰、不回滚（摘要）。

## 二、脉络

| 时间 | 节点 | 要点 | 出处 |
|---|---|---|---|
| 2024-01 | DeepSeekMoE | 细粒度专家 + 共享专家隔离 | [DeepSeekMoE](https://arxiv.org/abs/2401.06066) |
| 2024-04 | 多 token 预测（Gloeckle 等） | 一次预测多个未来 token 作为训练目标；V3 的 MTP 引用此线 | [Better & Faster LLMs via Multi-token Prediction](https://arxiv.org/abs/2404.19737) |
| 2024-05 | DeepSeek-V2 | MLA + DeepSeekMoE；V3 沿用其架构与 YaRN 扩窗 | [DeepSeek-V2](https://arxiv.org/abs/2405.04434) |
| 2024-08 | 无辅助损失负载均衡（Wang 等） | 用专家偏置代替辅助损失；V3 在 671B 规模上采用 | [Auxiliary-Loss-Free Load Balancing](https://arxiv.org/abs/2408.15664) |
| 2024-12 | **DeepSeek-V3** | 671B / 37B；MTP；DualPipe；FP8 | 本篇 |
| 2025-01 | DeepSeek-R1 | 以 V3-Base 为底座做推理 RL | [[DeepSeekR1推理训练深读]] |
| 2025-12 | DeepSeek-V3.2 | 架构上只加 DSA 稀疏注意力 | [[DeepSeekV32技术报告深读]] |
| 2026-04 | DeepSeek-V4 preview | CSA + HCA 混合注意力、mHC、Muon；MTP 配置同 V3 | [[DeepSeekV4技术报告深读]] |

## 三、架构与 MoE 机制

**骨架（原文 §4.2）。** 61 层，hidden 7168；注意力为 MLA（128 头，KV 压缩维 512，query 压缩维 1536，解耦 RoPE 每头 64 维）；除前 3 层外 FFN 全换成 MoE，每层 1 个共享专家 + 256 个路由专家（中间维 2048），每 token 激活 8 个路由专家；总参 671B，每 token 激活 37B。

**路由（原文 §2.1.2）。** 亲和分由 V2 的 softmax 改为 $s_{i,t}=\mathrm{Sigmoid}(u_t^\top e_i)$，在选中的 Top-8 上再归一化得到门控。训练与推理都不丢 token。

**无辅助损失均衡。** 每个专家带偏置 $b_i$，只用于**选择**：按 $s_{i,t}+b_i$ 取 Top-K，乘到专家输出上的门控仍来自原始 $s_{i,t}$。每步按整个 batch 统计负载，过载专家 $b_i\leftarrow b_i-\gamma$，欠载 $+\gamma$（前 14.3T token $\gamma=0.001$，最后 500B 为 0）。另加系数极小（$\alpha=0.0001$）的序列级辅助损失，防止单条序列内极端失衡。为什么有效：偏置只改「谁被选」，不进入梯度路径，因而不像辅助损失那样直接与语言建模目标冲突；原文 §4.5 与附录 C 显示这种做法下专家在不同领域上更特化。

**限节点路由。** 每 token 最多发往 4 个节点：先按各节点上最高 $K_r/M$ 个亲和分之和选节点，再在其中选专家。这把跨节点 IB 流量封顶，是后面通信几乎全掩盖的前提。

**MTP（原文 §2.2）。** 深度 $D=1$：主模型预测下一个 token 之外，用一个顺序串接的 MTP 模块再预测一个未来 token，损失 $\mathcal{L}_{\mathrm{MTP}}=\frac{\lambda}{D}\sum_{k=1}^{D}\mathcal{L}^k_{\mathrm{MTP}}$（前 10T token $\lambda=0.3$，其后 0.1）。目的是加密训练信号；推理时可丢弃，也可当投机解码的草稿头。

## 四、Infra：把通信藏进计算

**并行组合（原文 §3.2）。** 自研 HAI-LLM 框架；16 路流水线并行 × 64 路专家并行（跨 8 节点）× ZeRO-1 数据并行；靠显存优化完全不用张量并行。

**DualPipe（原文 §3.2.1）。** 把每对 forward / backward chunk 拆成 attention、all-to-all dispatch、MLP、all-to-all combine，backward 再拆为对输入与对权重两部分（与 ZeroBubble 同思路），然后让一个 chunk 的计算与另一个 chunk 的通信重叠，并从流水线两端同时灌入 micro-batch。代价是参数存两份；收益是在保持算通比时，all-to-all 与流水线通信基本被完全隐藏，气泡也比 1F1B 少（气泡与显存对照见原文 Table 2）。

**跨节点 all-to-all（原文 §3.2.2）。** 节点内 NVLink（160 GB/s）约是跨节点 IB（50 GB/s）的 3.2 倍。token 先经 IB 发到目标节点上同编号的 GPU，再经 NVLink 转发到持有专家的 GPU，两段并行。这样每个节点平均可再选 3.2 个专家而不增加 NVLink 开销，理论上可把路由专家数扩到 13 个而通信成本不变（实际用 8 个）。只用 20 个 SM 就能打满 IB 与 NVLink 带宽。

**显存（原文 §3.2.3）。** 反向时重算全部 RMSNorm 与 MLA 上投影；EMA 参数放 CPU 异步更新；DualPipe 让最浅层与最深层同处一个流水线 rank，MTP 模块与主模型物理共享 embedding 与输出头。

**FP8 混合精度（原文 §3.3）。** 三类 GEMM（前向、对输入的反向、对权重的反向）都用 FP8；embedding、输出头、MoE 门控、归一化与注意力保持 BF16 / FP32，主权重与优化器状态保持高精度。三点控制误差：

| 做法 | 内容 | 为什么需要 |
|---|---|---|
| 细粒度缩放 | 激活按 1×128 tile、权重按 128×128 block 各自缩放，在线取 max-abs | 激活离群值只影响所在小块，不拉低整张量的精度 |
| 提升累加精度 | H800 的 FP8 Tensor Core 累加约只保留 14 位；每 128 个元素把部分和提升到 CUDA Core 的 FP32 累加 | 长内积的累加误差随维度增大 |
| 统一 E4M3 | 所有张量用 E4M3（不在反向改用 E5M2） | 细粒度缩放已解决动态范围，尾数精度更重要 |

小规模验证（约 1T token）中相对 BF16 的 loss 相对误差始终低于 0.25%（附录 B.1）。MoE dispatch 前的激活也量化到 FP8 以省通信，combine 路径保留 BF16。

**推理部署（原文 §3.4）。** prefill 的 MoE 部分用 EP32 并设冗余专家；decode 用 EP320、每 GPU 约 1 个专家，共享专家当作路由专家处理（每 token 视作选 9 个）。完整节点表与冗余策略见原文。

## 五、训练配方与成本

| 阶段 | H800 GPU 小时 | 要点 |
|---|---:|---|
| 预训练 | 2664K | 14.8T token，最大序列 4K；每万亿 token 约 180K GPU 小时（2048 卡上约 3.7 天） |
| 上下文扩展 | 119K | YaRN 两阶段 4K → 32K → 128K，各 1000 步 |
| 后训练 | 5K | SFT 1.5M 条（推理域数据来自内部 R1 系列并经拒绝采样）；RL 用 GRPO，规则奖励 + 模型奖励 |
| 合计 | 2788K | 按 2 美元 / GPU 小时折算约 557.6 万美元，不含此前研究与消融 |

优化器为 AdamW；学习率 2.2×10⁻⁴ 恒定到 10T token 后余弦衰减；batch 在前 469B token 内从 3072 增到 15360；分词器为 128K 词表的字节级 BPE；FIM 比例 0.1。完整调度见原文 §4.2。

## 六、意义

V3 表明，在 2048 张 H800 的集群上，靠算法与系统协同设计也能以较低成本训出与闭源旗舰可比的开放权重模型。可迁移的经验有三条：负载均衡可以只改选择、不改梯度；路由设计要先考虑网络拓扑（限节点）再考虑表达能力；低精度训练的关键在缩放粒度与累加精度，而不在格式本身。报告同时给出了按 GPU 小时与假设租金折算的成本口径，并写明不含前期研究与消融。

## 七、局限与待核实

- 原文 Table 2 中 DualPipe 的气泡公式排版有折行，本篇不转录，引用时以原表为准。
- 推理部署的完整节点表与动态冗余专家策略（原文写在探索中）未收录。
- FP8 与 BF16 的对比曲线（附录 B）、各层专家负载图（附录 C）未逐图数字化。
- 评测分数（MMLU、MATH、SWE-bench 等）不在本篇范围。
- 557.6 万美元按假设租金折算，不是审计账单，也不含前期研究成本。
- arXiv 最新版即 v2（2025-02-18），本篇数字均按 v2。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[混合专家架构]] | V3 是该篇 MoE 史线中「无辅助损失均衡」的大规模实例，本篇给配方与数字 | Switch / Mixtral 史线与思想跳跃 |
| [[注意力效率族MQA到MLA]] | 该篇以 V3 报告 §2.1.1 讲 MLA，本篇只列 V3 的维度取值 | MLA 推导 |
| [[MTP训练范式]] | 该篇把 V3 的级联 MTP 损失当作后续方法的起点 | MTP 方法族 |
| [[AI基础设施总览]] | 该篇摘 DualPipe、FP8 与分阶段部署作 Infra 案例，本篇给细节 | 训练与服务通论 |
| [[NVSHMEM与DeepEP通信]] | 本篇只写 V3 报告中的 all-to-all 设计，内核实现在该篇 | DeepEP 内核与 NVSHMEM |
| [[分布式训练并行策略]] | 本篇第四节的 16 路流水线 × 64 路专家并行 × ZeRO-1 是该篇「MoE 时代的组合案例」之一 | 五种并行各切什么、何时不用张量并行 |
| [[MoE路由与负载均衡]] | 本篇第三节的无辅助损失偏置与限节点路由，在该篇放进从 Switch 到 Quantile Balancing 的路由演进中对照 | 路由与均衡方法的演进 |
| [[DeepSeekR1推理训练深读]] | R1 以 V3-Base 为底座，V3 的 SFT 推理数据又来自 R1 系列 | 推理 RL 配方 |
| [[DeepSeekV32技术报告深读]] | 下一代只改注意力（DSA），其余沿用 V3 | DSA 与混合 RL |
| [[DeepSeekV4技术报告深读]] | V4 继承 DeepSeekMoE 与 MTP，改路由亲和函数并去掉节点约束 | CSA / HCA、mHC、Muon |
| [[KimiK2技术报告深读]] | K2 以 V3 架构为参照，该篇给出两者的配置差分 | K2 与 MuonClip |
| [[开源与闭源前沿模型谱系]] | V3 在开放权重谱系中的位置 | 代际坐标 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [DeepSeek-V3 Technical Report](https://arxiv.org/abs/2412.19437) §2.1–2.2 | 路由、均衡与 MTP |
| 2 | 同上 §3.2–3.3 | DualPipe、all-to-all 与 FP8 |
| 3 | [Auxiliary-Loss-Free Load Balancing](https://arxiv.org/abs/2408.15664) | 偏置式均衡的原始论文 |
| 4 | [[混合专家架构]] | MoE 史线 |
| 5 | [[DeepSeekV4技术报告深读]] | V3 底座的后续演进 |
