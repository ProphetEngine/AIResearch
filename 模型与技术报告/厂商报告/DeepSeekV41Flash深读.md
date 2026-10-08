---
title: "DeepSeek-V4.1-Flash Technical Report 深读"
topic: DeepSeekV41Flash深读
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2609.19969
sources:
 - https://arxiv.org/abs/2609.19969
 - https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash
arxiv: "2609.19969"
related: ["DeepSeekV4技术报告深读", "DeepSeekV32技术报告深读", "DeepSeekV3训练与MoE基建", "KV缓存量化与压缩", "注意力效率族MQA到MLA", "长上下文位置编码与系统侧", "混合专家架构", "推理引擎生态", "投机解码原理与发展脉络", "ClaudeOpus5系统卡深读"]
archived: 2026-09-22
---

# DeepSeek-V4.1-Flash Technical Report 深读

> **主要来源**：[DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression](https://arxiv.org/abs/2609.19969)；[deepseek-ai/DeepSeek-V4.1-Flash 模型页](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)（仅用于核对型号名）（截至 2026-09-17）。报告只有 arXiv v1；模型页不引事实，不计入截至。
> **研究线**：架构思想（主：Causal Encoder-Decoder、CSA2、FP4 主 KV）；AI Infra（辅：SWA Bounded Replay 与持久化 KV 管理）
> **范围与相邻笔记**：
> - ≠ [[DeepSeekV4技术报告深读]]：CSA 与 HCA 混合注意力、mHC 与 V4 的训练配方在那篇，本篇只写 V4.1-Flash 相对 V4 的改动。
> - ≠ [[DeepSeekV32技术报告深读]]：DSA 的两阶段继续训练在那篇；V4.1-Flash 从零训练稀疏注意力，不做稠密预热。
> - ≠ [[KV缓存量化与压缩]]：KV 量化的通论在那篇，本篇只记 V4.1-Flash 采用的格式。
>
> **意义**：长程智能体让负载以输入为主，部署成本的主要瓶颈变成 prefill 计算与 KV cache 占用的 HBM、SSD 容量和带宽。V4.1-Flash 从三个层面压 KV：架构上用 Causal Encoder-Decoder 让 prefill 只激活 8B 参数（decode 为 16B），用 CSA2 跨层复用 KV 与索引；精度上把主 KV 改为 FP4；部署上用 SWA Bounded Replay 不再持久化滑窗 KV。摘要称常驻 HBM 的全局 KV 为每 token 890 字节，约为 V4-Flash 的 1/4，持久化 KV 约为 V4-Flash 的 1/8（§3.2.1 写为 V4 的 1/8，见局限），而骨干参数 552B（另有 196B Engram 参数），比 V4-Flash 更大、整体表现更好。

## 一、问题背景

长程智能体频繁调用工具，产生大量 prefill 请求；KV cache 未命中时 prefill 计算开销很重，而大 KV cache 持续挤占 HBM、SSD 容量与传输带宽（§1、§2.2）。报告把 V4 理解为以滑窗注意力做局部处理、再加压缩全局上下文的骨干，因此 V4.1-Flash 的思路是简化全局分支、基本保留局部注意力设计（§1）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-05 | [DeepSeek-V2](https://arxiv.org/abs/2405.04434) | MLA 用共享小 latent 压缩每条 KV |
| 2024-05 | [YOCO](https://arxiv.org/abs/2405.05254) | 上半层直接共享下半层生成的 KV，减少 prefill 计算 |
| 2025-12 | [DeepSeek-V3.2](https://arxiv.org/abs/2512.02556) | 轻量 indexer 选 top-k 的稀疏注意力 |
| 2026-04 | [DeepSeek-V4](https://arxiv.org/abs/2606.19348) | CSA 与 HCA 按序列维压缩 KV，mHC 残差 |
| 2026-09 | [DeepSeek-V4.1-Flash](https://arxiv.org/abs/2609.19969) | CED、CSA2 跨层复用、FP4 主 KV、SWA Bounded Replay |

## 三、核心机制

### 3.1 Causal Encoder-Decoder（§2.2）

CED 受 YOCO 启发。40 层骨干的下 20 层作为因果 encoder，上 20 层作为 decoder；decoder 各层的全局 KV 不从本层隐状态生成，而由 encoder 末层隐状态经各层自己的投影得到。prefill 时只需跑前半网络就能拿到上半层的全局 KV，prefill 计算接近减半，复杂度由 O(NL) 降到约 O(NL/2)。

滑窗注意力仍逐层从本层隐状态生成局部 KV，以保留局部计算深度。代价是 decoder 的滑窗 KV 需要额外回放，因此引入 Decoder SWA Bounded Replay：只对 prompt 的最后一个窗口长度的 token 做滑窗计算（见 3.4）。

### 3.2 Compressed Sparse Attention 2（§2.3）

KV 成本可沿三个维度相乘地压缩：条目大小（GQA、MLA）、序列维（V4 的 CSA、HCA 每 m 个 token 压成一条）、层维（层间复用缓存与选择）。CSA2 同时利用三者，并把缓存共享与索引复用解耦。相对 V4 的 CSA，CSA2 去掉了压缩源条目的重叠与绝对位置编码，indexer K 改由主 KV 投影得到；V4 用 CSA 与 HCA 混合，V4.1-Flash 只用 CSA2。

每层静态分配三种模式之一，三种模式都在本层计算 query 与滑窗 KV：

| 模式 | 主 KV 与 indexer K | Top-K 索引 |
|---|---|---|
| Full | 本层生成 | 本层 indexer 新算 |
| Reindex | 复用最近 Full 层的 | 本层 indexer Q 对复用的 K 重新打分，选出新的 Top-K |
| Reuse | 复用最近 Full 层的 | 复用最近 Full 或 Reindex 层的 Top-K，不再计算索引 |

**层次稀疏 indexer**（只用于 decoder，§2.3.2）：decoder 第一个 Full 层对全部可见位置打分，同时按块取最高分选块，组成候选池，例如 2,048 个块各 8 个位置，共 16,384 个候选；后续 Reindex 层只在池内打分。候选池大小固定时，深层 indexer 每个 query 的打分量与上下文长度无关。

**本代配置**（§4.2.1）：前两层只用滑窗注意力；encoder 其余 18 层为 CSA2、压缩率 m = 2，分 3 组、每组 1 个 Full 加 5 个 Reuse；decoder 20 层为 CSA2、m = 1，分 5 组，第一组 1 个 Full 加 3 个 Reuse，其余四组各 1 个 Reindex 加 3 个 Reuse。注意力 top-k 为 512。

### 3.3 FP4 主 KV（§2.4.4）

V4 已用量化感知训练把 indexer 的 Q、K 做成 FP4（OCP MXFP4）。V4.1-Flash 把 QAT 扩到主 KV，目的是省存储而不是加速矩阵乘：缓存值在注意力前先反量化，因此可以用更准的格式而不要求硬件原生支持。格式选 E2M1 加每 16 个通道一个 E4M3 scale，沿用 NVFP4 但去掉第二级全局 scale；报告论证该格式的动态范围远高于缓存值的幅度上界，去掉全局 scale 没有测得精度下降。QAT 在后训练引入，在 RoPE 之后量化；滑窗 KV 对量化敏感，仍用 FP8。相对 V4 的 FP8 主 KV，存储接近减半。

### 3.4 SWA Bounded Replay 与持久化 KV（§3.2）

精确重建滑窗 KV 需要回放「层数 × 窗口长度」个 token，在生产中代价过高。V4 部署中滑窗 KV 占持久化缓存近一半，但它只在会话内分钟级的窗口里被复用，与全局 KV 长尾复用、保留 72 小时以上的策略不匹配。V4.1 的改动：

1. 滑窗 KV 不再进持久化缓存，改放在由每台机器 10% host DRAM 组成的分布式内存池，TTL 只有几分钟；全局 KV 仍在持久化缓存中，保证寿命至少 72 小时。
2. 滑窗 KV 未命中时，用 Encoder SWA Bounded Replay 只回放最近一个窗口长度的 token 来近似重建，而不是「层数 × 窗口长度」个 token。报告称近似重建带来的性能下降可以忽略。

§3.2.1 称同等负载下持久化 KV 降到 V4 的 1/8，来自两个因子相乘：不再存滑窗 KV，体积近乎减半；其中的全局 KV 又压到 V4 的 1/4。

### 3.5 其他组件与训练（§2.4、§4.2、§5）

- **Engram** 条件记忆模块，196B 参数均分在两个模块中。
- **DSpark** 投机解码模块：不像 DeepSeek-V3 的 MTP 那样与骨干联合预训练，而是在预训练之后单独训练。
- **Single-Pass mHC**：改进 V4 的 mHC，配套的 Mega-mHC 内核使激活访存相对原四内核实现减半。
- **MoE**：每层 1 个共享专家加 384 个路由专家。
- **预训练**：45T token 多模态语料；稀疏注意力在 64K 长度上从零训练，不做稠密预热，在 34T token 时扩到 1M；报告称训练中没有不稳定。
- **后训练**：明确没有算法创新，沿用 V4 的 SFT、RL 与在线策略蒸馏（OPD），实质改动都在数据与环境合成管线。

## 四、主要结果

| 维度 | 报告数字 | 出处 |
|---|---|---|
| 基座 | V4.1-Flash-Base 与 V4-Pro-Base 的世界知识、推理与代码能力相当，留出评测提升 5%–10%，只用其 1/3 总参与 1/4 激活参数 | §1 |
| 解码计算 | 上下文从 4K 扩到 1M（256 倍），单 token 解码 FLOPs 只增加 1/4，增幅明显小于 V4-Flash | §1 |
| 推理 | Codeforces 3471，高于 V4-Flash 的 3289 与 V4-Pro 的 3348；GPQA Diamond 90.9% | §5.3 |
| 智能体 | DeepSWE v1.1 为 74.2%（V4-Flash 为 54.4%）；Terminal-Bench 2.1 为 90.6% | §5.3 |
| 推理强度 | effort 从 25 调到 100，八项推理基准平均 Pass@1 从 67.1% 升到 76.3% | §5.3.3 |
| 内核 | 每个 CSA2 Reuse 层 prefill 只需 15 个内核，decode 只需 11 个 | §1 |

## 五、意义

V4.1-Flash 把优化目标从计算量转向 KV 的存储与迁移。CED 处理 prefill 计算，CSA2 与 FP4 处理常驻 HBM 的全局 KV，SWA Bounded Replay 处理持久化层，三者分别对应计算、HBM 与 SSD 三种资源。其中 SWA Bounded Replay 用少量近似重算换掉整类持久化存储，是一种新的存储与计算折中。后训练没有算法创新、能力提升来自数据与环境规模，也说明这一代的增量集中在架构与部署。

## 六、局限与待核实

1. **报告自述的局限**（§6）：新架构带来的鲁棒性边界尚未充分刻画，CSA2 的选择错误与 SWA Bounded Replay 的近似重建可能在未测试的边界情况下导致能力下降；标准基准趋于饱和，在最难的推理与边角任务上与顶尖闭源模型仍有差距。
2. **报告内两处比例不一致**：全局 KV「约为 V4-Flash 的 1/4」在摘要与引言（§1）各写一次；持久化 KV「约为 V4-Flash 的 1/8」在摘要与引言（§1），§3.2.1 则写为 V4 的 1/8，同节的全局 KV 1/4 也以 V4 为对照。两处照录，不调和。
3. **基座对比口径**：「1/3 总参、1/4 激活参数」与「提升 5%–10%」是作者对 V4-Pro-Base 的口径。
4. **自评说法**：引言称可完成超过 95% 的真实任务，是作者主张，未经第三方审计。
5. **图中数字**：各代全局 KV 大小对比与解码 FLOPs 曲线只在图中给出，本篇只用正文给出的倍数，不写由字节数换算的比例。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[DeepSeekV4技术报告深读]] | V4 是 V4.1-Flash 的对照基线：CSA 与 HCA 混合改为纯 CSA2，FP8 主 KV 改为 FP4，持久化滑窗 KV 改为 Bounded Replay | V4 的完整架构与训练配方 |
| [[DeepSeekV32技术报告深读]] | V4.1-Flash 的稀疏注意力从零训练，不再走 V3.2 的稠密预热 | DSA 的继续训练流程 |
| [[DeepSeekV3训练与MoE基建]] | V4.1-Flash 省略了 V3 的 MTP，改用预训练后单独训练的 DSpark | V3 的训练配方 |
| [[KV缓存量化与压缩]] | V4.1-Flash 主 KV 的 FP4 格式选择与量化位置 | KV 量化的通论 |
| [[注意力效率族MQA到MLA]] | CSA2 把 MLA 式条目压缩与序列维、层维压缩组合 | MQA 到 MLA 的演进 |
| [[长上下文位置编码与系统侧]] | 1M 上下文下解码 FLOPs 近乎不随长度增长 | 长上下文的通论 |
| [[混合专家架构]] | 每层 1 个共享专家加 384 个路由专家的配置 | MoE 的通史 |
| [[推理引擎生态]] | 持久化缓存与内存池分层管理全局 KV 和滑窗 KV | 推理引擎的选型 |
| [[投机解码原理与发展脉络]] | DSpark 是 V4.1-Flash 的投机解码模块 | 投机解码算法本身 |
| [[ClaudeOpus5系统卡深读]] | 本篇 Table 3 后训练主表以 Claude Opus 5 为闭源对照之一（§5.3 的智能体结果也点名 Opus-5）；Opus 5 自身的系统卡与安全评测见那篇 | Opus 5 的安全评测 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [DeepSeek-V4.1-Flash arXiv（v1）](https://arxiv.org/abs/2609.19969v1) | §2.2–§2.4 的 CED、CSA2 与 FP4 主 KV，§3.2 的持久化 KV 管理 |
| 2 | [deepseek-ai/DeepSeek-V4.1-Flash 模型页](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash) | 权重 |
