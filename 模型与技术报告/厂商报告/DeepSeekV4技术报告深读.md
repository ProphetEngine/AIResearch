---
title: "DeepSeek-V4 Technical Report 深读"
topic: DeepSeekV4技术报告深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
source_url: https://arxiv.org/abs/2606.19348
arxiv: "2606.19348"
sources:
 - https://arxiv.org/abs/2606.19348
 - https://huggingface.co/collections/deepseek-ai/deepseek-v4
related: ["DeepSeekV3训练与MoE基建", "DeepSeekV32技术报告深读", "DeepSeekV41Flash深读", "分块KV压缩的相位敏感性", "KV缓存量化与压缩", "注意力效率族MQA到MLA", "长上下文位置编码与系统侧", "混合专家架构", "优化器与训练稳定性", "OnPolicy蒸馏OPD范式", "推理引擎生态", "AI基础设施总览", "MoE路由与负载均衡"]
archived: 2026-09-22
---

# DeepSeek-V4 Technical Report 深读

> **主要来源**：[DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence](https://arxiv.org/abs/2606.19348)（DeepSeek-AI，v1，2026-04-26，58 页）；[DeepSeek-V4 权重集合](https://huggingface.co/collections/deepseek-ai/deepseek-v4)（截至 2026-09-28）。
> **研究线**：架构思想（CSA + HCA 混合注意力、mHC、Muon，主）· 评测字段（长上下文与智能体表，辅）
> **范围与相邻笔记**：
> - ≠ [[DeepSeekV3训练与MoE基建]]：本篇不写 MoE 基座、DualPipe 与 FP8 训练配方。
> - ≠ [[DeepSeekV32技术报告深读]]：本篇不写 DSA 两阶段继续训练与 GRPO 稳定化细节。
> - ≠ [[DeepSeekV41Flash深读]]：本篇不写 V4.1-Flash 的 CED、CSA2、主 KV FP4 与 SWA Bounded Replay；本报告自称 preview，对照基线是 V3 / V3.2。
> - ≠ [[KV缓存量化与压缩]]：本篇不写 KV 量化通史，只列 V4 的产品解。
>
> **意义**：V4 把「百万 token 上下文」从可训练推到可规模化服务：在 1M 长度下，V4-Pro 单 token 推理 FLOPs 只有 V3.2 的 27%、KV cache 只有 10%。办法不是单一技巧，而是把注意力改成「先压缩再稀疏」与「重压缩稠密」两种层交错，再配合残差、优化器与 KV 存储结构的整套改动；后训练则用多教师在线蒸馏取代 V3.2 的混合 RL 合并阶段。

**一句话**：V4 系列（Pro 1.6T / 49B 激活，Flash 284B / 13B 激活）原生支持 1M 上下文；CSA 把每 4 个 token 的 KV 压成 1 条再做 top-k 稀疏注意力，HCA 把每 128 个 token 压成 1 条但保持稠密注意力，两者都附一个近邻滑窗；mHC 把加宽的残差流约束在双随机矩阵上以保稳定，主体参数用 Muon 优化。

---

## 一、问题背景

长上下文的成本有两部分：注意力计算随长度增长，KV cache 随长度线性增长并占满显存。V3.2 用 DSA（DeepSeek Sparse Attention，用轻量 indexer 为每个 query 选 top-k 个 token）解决了第一部分，但 KV 仍按每个 token 存一份（[[DeepSeekV32技术报告深读]]）。当目标从 128K 扩到 1M、且要在智能体与多轮场景中复用长前缀时，KV 体积成为部署瓶颈，PagedAttention 那种「所有层同一种页」的缓存假设也不再适用。

V4 报告同时要解决规模化训练的稳定性：模型更深更宽、残差流加宽后容易数值发散，MoE 训练会出现 loss 尖峰。

## 二、脉络

| 时间 | 节点 | 要点 | 出处 |
|---|---|---|---|
| 2024-09（arXiv） | Hyper-Connections（Zhu 等） | 把残差流加宽为 $n$ 路并学习混合矩阵；深层堆叠易不稳 | [Hyper-Connections](https://arxiv.org/abs/2409.19606) |
| 2024-12 | DeepSeek-V3 | MLA + DeepSeekMoE + MTP 基座 | [[DeepSeekV3训练与MoE基建]] |
| 2025-12 | DeepSeek-V3.2 | DSA 稀疏注意力；混合 RL | [[DeepSeekV32技术报告深读]] |
| 2026-04 | **DeepSeek-V4 preview** | CSA + HCA；mHC；Muon；OPD 合并 | 本篇 |
| 2026-09 | DeepSeek-V4.1-Flash | 纯 CSA2 + 主 KV FP4，再压常驻 KV | [[DeepSeekV41Flash深读]] |
| 2026-09 | 分块 KV 压缩的相位敏感性 | 第三方发现 CSA 固定步长带来检索准确率的周期性弱点 | [[分块KV压缩的相位敏感性]] |

## 三、核心机制

### 3.1 混合注意力：CSA + HCA（原文 §2.3）

| | CSA（Compressed Sparse Attention） | HCA（Heavily Compressed Attention） |
|---|---|---|
| 压缩 | 每 $m=4$ 个 token 合成 1 条 KV；每条由 $2m$ 个原始 KV 加权得到，相邻条目重叠 | 每 $m'=128$ 个 token 合成 1 条，不重叠 |
| 注意力 | lightning indexer 选 top-k 条压缩 KV（Flash 512、Pro 1024）后稀疏注意 | 对全部压缩 KV 稠密注意 |
| 共同点 | 选中的压缩条目同时作 K 与 V（shared-KV MQA）；分组输出投影；另附最近 128 个未压缩 token 的滑窗分支，保证块内因果与近邻细节 | 同左 |

为什么这样组合：CSA 保留了较细的粒度，靠稀疏选取控制计算；HCA 粗到可以对全序列稠密注意，提供廉价的全局视野；滑窗补上压缩丢掉的近邻信息。两种层交错堆叠（Flash 前 2 层为纯滑窗，Pro 前 2 层为 HCA）。其余细节：query 与压缩 KV 先做 RMSNorm；只对最后 64 维加 RoPE，输出端用位置 $-i$ 抵消绝对位置；每头一个可学习的 attention sink。

**效率口径。** KV 中 RoPE 维存 BF16、其余存 FP8，体积约减半；indexer 注意力用 FP4。1M 长度下：

| | 单 token FLOPs（相对 V3.2） | KV cache（相对 V3.2） |
|---|---:|---:|
| V4-Pro | 27% | 10% |
| V4-Flash | 10% | 7% |

相对 BF16 的 GQA8（头维 128）基线，1M 设定下 KV 约为其 2%。

### 3.2 mHC：受流形约束的超连接（原文 §2.2）

mHC 由 Xie 等（2026）提出，V4 在各 Transformer 块的残差连接上采用。Hyper-Connections 把残差流扩成 $n_{\mathrm{hc}}\times d$，用矩阵 $B_l$ 在各路之间混合，但层层相乘后范数可能放大。mHC 把 $B_l$ 投影到双随机矩阵集合（行列和均为 1、元素非负），这类矩阵谱范数不超过 1 且对乘法封闭，所以任意多层叠加仍不放大信号；投影用 Sinkhorn-Knopp 迭代 20 次。输入、输出映射经 Sigmoid 保证非负有界。V4 取 $n_{\mathrm{hc}}=4$。

### 3.3 MoE 与优化器（原文 §2.1、§2.4）

- **MoE**：沿用 DeepSeekMoE 与无辅助损失均衡；亲和函数由 Sigmoid 改为 $\sqrt{\mathrm{Softplus}(\cdot)}$；去掉路由的目标节点数约束；前 3 层由稠密 FFN 改为按 token ID 哈希路由的 MoE 层。Flash 为 1 共享 + 256 路由专家，Pro 为 1 共享 + 384 路由专家，均每 token 激活 6 个。MTP 与 V3 相同（深度 1）。
- **Muon**：主体参数用 Muon（对动量做 Newton-Schulz 正交化），embedding、预测头、mHC 的静态偏置与门控、全部 RMSNorm 仍用 AdamW；更新的 RMS 重标定到 0.18 以复用 AdamW 学习率。因 Q / KV 已做 RMSNorm，不需要 QK-Clip。

### 3.4 KV 存储结构（原文 §3.5）

V4 的缓存条目是异构的：CSA 主 KV、CSA indexer、HCA、滑窗 KV，以及尚未凑满一个压缩块的尾部。报告把它们分成两池：经典 KV 池存压缩条目，每块覆盖 $\mathrm{lcm}(m,m')$ 个原始 token；状态池按请求固定分配，存滑窗与未压缩尾部。前缀复用时，压缩 KV 全部落盘；滑窗 KV 体积约为压缩部分的 8 倍，给出三种策略：全量缓存（零重算、写放大大）、周期性存检查点（可调存算比）、不存滑窗而用已缓存的压缩 KV 重放末尾若干 token 重建。

### 3.5 专家并行细粒度重叠与 MegaMoE（原文 §3.1）

专家并行把 MoE 层拆为 Dispatch、Linear-1、Linear-2、Combine 四段，按 wave 调度专家，使通信与计算细粒度重叠，并融合为单核 MegaMoE（开源于 DeepGEMM）；相对非融合基线，一般推理提速 1.50–1.73×，RL rollout 等延迟敏感场景最高 1.96×（原文 §3.1）。

## 四、训练与后训练要点

**预训练（原文 §4）。** 语料超过 32T token（Flash 32T、Pro 33T），中期掺入智能体代码数据并加强长文档；序列长度分阶段 4K → 16K → 64K → 1M，64K 起引入稀疏注意力。两项稳定化：**Anticipatory Routing**（特征用当前参数、路由索引用若干步前的参数，出现尖峰时自动启用，启用期间额外耗时约 20%）与 **SwiGLU Clamping**（线性支路截断到 $[-10,10]$）；作者承认两者的机理尚不清楚。

**后训练（原文 §5）。** 先按领域（数学、代码、智能体、指令等）各自 SFT → GRPO 训出专家，再用多教师在线蒸馏（OPD，学生在自身采样上对齐超过 10 个教师的全词表分布，反向 KL）合并成一个模型，取代 V3.2 的混合 RL 合并阶段。推理档位分 Non-think、Think High、Think Max。工具场景下跨用户轮次保留全部思维，普通对话仍在新消息到来时丢弃旧思维。后训练中对 MoE 专家权重与 indexer 的 QK 路径做 FP4 量化感知训练；另把 index score 由 FP32 降为 BF16，top-k 选择器提速 2×，召回保持 99.7%（原文 §5.2.1）。

## 五、结果要点

| 基准（Base，Table 1） | V3.2-Base | V4-Flash-Base | V4-Pro-Base |
|---|---:|---:|---:|
| MMLU-Pro | 65.5 | 68.3 | 73.5 |
| SimpleQA-Verified | 28.3 | 30.1 | 55.2 |
| LongBench-V2 | 40.2 | 44.7 | 51.5 |

| 基准（V4-Pro-Max，Table 6） | V4-Pro-Max | 对照 |
|---|---:|---|
| MRCR 1M | 83.5 | Opus-4.6 Max 92.9；Gemini-3.1-Pro High 76.3 |
| LiveCodeBench | 93.5 | 表内最高 |
| SWE Verified | 80.6 | Opus-4.6 Max 80.8 |
| HLE | 37.7 | Gemini-3.1-Pro High 44.4 |

作者自述：知识仍落后 Gemini-3.1-Pro，推理约落后前沿闭源 3–6 个月；内部 R&D 编码基准通过率 67%，Opus 4.5 为 70%、Opus 4.6 Thinking 为 80%（Table 8）。

## 六、意义

V4 是「压缩注意力」路线在开放权重旗舰上较完整的一次落地，并把模型结构与 KV 存储、磁盘复用一起设计。它也暴露了这条路线的代价：架构明显变复杂（作者在 §6 说未来要「蒸馏到本质」），固定压缩步长还带来了平均分看不出的检索弱点（[[分块KV压缩的相位敏感性]]）。后训练上，「领域专家 RL + 多教师在线蒸馏合并」成为与 Nemotron 3 Ultra、Kimi K3 共享的配方（[[OnPolicy蒸馏OPD范式]]）。

## 七、局限与待核实

- CSA 与 HCA 的精确层交错比正文未给，需看开源推理代码。
- 「相对 BF16 GQA8 约 2% KV」没有逐字段的字节拆解；1M 以外长度的 FLOPs / KV 曲线只在 Fig 1 图中。
- Table 6 / 7 中部分对照模型因 API 繁忙空缺，跨 scaffold 引用需注明设置；Terminal Bench 2.0 另有 Verified 版约 72.0 的补充句，主表为 67.9。
- 外部模型（GPT-5.4、Gemini-3.1-Pro、Kimi-K2.6、GLM-5.1、Opus-4.6 等）分数为作者对比，本篇未核其独立来源。
- 本报告为 preview；arXiv 最新版即 v1，正式产品与 preview 的差异未见官方文档。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[DeepSeekV3训练与MoE基建]] | V4 继承的 MoE、MTP 基座；本篇只写 V4 的差分 | DualPipe、FP8 配方 |
| [[DeepSeekV32技术报告深读]] | CSA 即「压缩 + DSA」；1M 效率以 V3.2 为基线；OPD 取代其混合 RL 合并 | DSA 继续训练与 GRPO 细节 |
| [[归一化与残差连接设计]] | V4 所用 mHC 属于残差加宽路线，从 HC 到 mHC 的约束及其与 AttnRes、门控残差的对照在那篇 | 归一化位置与残差设计谱系 |
| [[DeepSeekV41Flash深读]] | V4.1-Flash 以 V4-Flash 为基线改为纯 CSA2 并压主 KV | CED、CSA2、FP4 主 KV、Bounded Replay |
| [[分块KV压缩的相位敏感性]] | 该研究以 V4 家族为主要对象，测得 base 检查点随 token 相位的检索差距最大约 40 个百分点 | 现象的机制与理论 |
| [[KV缓存量化与压缩]] | V4 的 KV 混合精度与 indexer FP4 是该通史中的一个产品解 | 量化误差轴与通史 |
| [[注意力效率族MQA到MLA]] | CSA / HCA 的 shared-KV MQA 属该篇的 KV 共享族 | MQA、GQA、MLA 推导 |
| [[长上下文位置编码与系统侧]] | V4 的部分 RoPE 与 1M 分阶段扩窗 | 位置编码通论 |
| [[混合专家架构]] | V4 的 MoE 改动（亲和函数、Hash 路由、去节点约束） | MoE 史线 |
| [[MoE路由与负载均衡]] | 本篇 3.3 节的 Sqrt(Softplus) 亲和分、去掉节点约束与前 3 层哈希路由，是该篇路由演进中的产品级节点 | 路由与均衡方法的演进 |
| [[优化器与训练稳定性]] | V4 主体用 Muon、不需要 QK-Clip；Anticipatory Routing 与 SwiGLU Clamping 是稳定化实例 | 优化器通论 |
| [[OnPolicy蒸馏OPD范式]] | V4 用多教师 OPD 合并领域专家 | OPD 方法族 |
| [[推理引擎生态]] | V4 的异构 KV 打破 PagedAttention 的统一页假设，需要引擎侧两池布局 | 引擎选型 |
| [[AI基础设施总览]] | V4 的专家并行融合核（MegaMoE）与确定性核属该篇的训练与服务基础设施 | Infra 通论 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [DeepSeek-V4](https://arxiv.org/abs/2606.19348) §2.3 与 Fig 3–4 | CSA、HCA 结构 |
| 2 | 同上 §2.2、§2.4 | mHC 与 Muon |
| 3 | 同上 §3.5 | 异构 KV 与磁盘策略 |
| 4 | [Hyper-Connections](https://arxiv.org/abs/2409.19606) | mHC 所约束的原始结构 |
| 5 | [[DeepSeekV41Flash深读]] | V4 之后的 KV 压缩增量 |
