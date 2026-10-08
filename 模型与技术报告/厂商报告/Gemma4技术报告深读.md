---
topic: Gemma4技术报告深读
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
title: Gemma 4 Technical Report 深读
sources:
 - https://arxiv.org/abs/2607.02770
 - https://ai.google.dev/gemma/docs/core
related: ["Gemini25技术报告深读", "端侧小模型", "ZeroQAT量化感知训练", "投机解码原理与发展脉络", "多模态架构脉络", "长上下文位置编码与系统侧", "MedGemma医学专科", "开源与闭源前沿模型谱系"]
archived: 2026-09-22
---

# Gemma 4 Technical Report 深读

> **主要来源**：[Gemma 4 Technical Report](https://arxiv.org/abs/2607.02770)（Gemma Team, Google DeepMind，v2，2026-07-24；首次提交 2026-07-02）；[Gemma 4 开发者概述](https://ai.google.dev/gemma/docs/core)（Last updated 2026-07-08）（截至 2026-07-24）。
> **研究线**：架构思想（主：local/global 注意力与 KV 复用、12B 无编码器架构）；AI Infra（辅：QAT、MTP drafter、TPU 分片表）
> **范围与相邻笔记**：
> - ≠ [[Gemini25技术报告深读]]：Gemma 4 沿用 Gemini 2.5 的 tokenizer 与训练弹性机制，闭源 Gemini 的能力与安全结论在那篇。
> - ≠ [[端侧小模型]]：E2B、E4B 的端侧产品化与其他端侧路线的对照在那篇。
>
> **意义**：Gemma 4 是 Google 以 Apache 2.0 许可放出的开放权重多模态模型族，包含稠密的 E2B、E4B、12B、31B 与 26B-A4B MoE。与闭源 Gemini 不同，报告公开了参数分项、注意力与位置编码配方、量化格式与芯片分片表；架构新点是 12B 去掉独立视觉与音频编码器、直接投影原始图块与音频片段。Arena 文本榜上 31B 是领先的稠密开源模型；Table 5 中 31B 全面超过 Gemma 3 27B。

## 一、问题背景

开放权重模型需要同时具备多模态理解、推理与计算效率。报告指出长上下文会让 KV 缓存的内存急剧膨胀，而 Gemma 4 面向多种端侧硬件，因此把效率放在与能力同等的位置：注意力配方压 KV 缓存，QAT 压参数内存，MTP drafter 提解码速度，12B 去掉独立编码器以减少内存碎片（§1）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-03 | [Gemma](https://arxiv.org/abs/2403.08295) | 基于 Gemini 研究的首代开放权重模型 |
| 2024-07 | [Gemma 2](https://arxiv.org/abs/2408.00118) | 实用尺寸上的开放模型改进 |
| 2025-03 | [Gemma 3](https://arxiv.org/abs/2503.19786) | Gemma 4 沿用的 local/global 注意力比例与预训练、后训练配方 |
| 2025-07 | [Gemini 2.5](https://arxiv.org/abs/2507.06261) | Gemma 4 所用的 tokenizer 与 Slice-Granularity Elasticity |
| 2026-07 | [Gemma 4](https://arxiv.org/abs/2607.02770) | 稠密与 MoE 并存、12B 无编码器、thinking 模式、QAT 与 MTP drafter |

## 三、核心机制：架构（§2）

### 3.1 型号与骨干

Decoder-only Transformer，pre-norm 与 post-norm 并用 RMSNorm，并加 QKNorm。词表 262k，与 Gemini 2.5 同一 SentencePiece tokenizer（拆分数字、保留空白、字节级编码）。

| 型号 | 骨架 | 参数（报告用语） | 编码器（Table 1） |
|---|---|---|---|
| E2B | 稠密，逐层嵌入（PLE，沿用 Gemma 3n） | 2.3B effective，5B total | 音频 305M，视觉 150M |
| E4B | 稠密，PLE | 4.5B effective，8B total | 音频 305M，视觉 150M |
| 12B | 稠密，统一的无编码器架构 | 12B | 无独立编码器 |
| 26B-A4B | MoE | 正文写 3.8B activated、26B total；Table 1 的 Einsums 列写 2,800M (active) | 视觉 550M |
| 31B | 稠密 | 31B | 视觉 550M |

Table 1 另列 MTP drafter 参数：E2B 76M、E4B 77M、12B 400M、26B-A4B 430M、31B 500M。

### 3.2 长上下文与 KV 效率

- **注意力比例**：沿用 Gemma 3，local 滑窗与 global 注意力为 5:1，E2B 为 4:1。
- **位置编码**：global 层用 p-RoPE（p=0.25），local 层用 RoPE；RoPE 频率 global 1M、local 10k。
- **KV 复用**：global 层让 values 等于 keys（E2B、E4B 除外）；报告称这些设计使 global KV 缓存最多减少 37.5%。E2B 与 E4B 另做 KV 缓存共享，比例为 20/35 与 18/42。

### 3.3 视觉与音频编码器（§2.1–§2.2）

- **视觉**：E2B、E4B 用 150M ViT，更大的型号（12B 除外）用 550M ViT，patch 大小均为 16。支持可变宽高比，用轴向 2D-RoPE（非因果注意力）加 2D 绝对位置嵌入；最大 token 数可取 70、140、280、560、1120。编码器在预训练中冻结。
- **音频**：E2B、E4B 用 305M 编码器，基于 USM（两层下采样卷积加十二层 Conformer），以 40ms 为一块、Mel 滤波器组为输入；结构与 Gemma 3n 相近，参数减少 55%（680M 到 305M）。不做向量量化，LLM 直接接收连续表示。

### 3.4 12B 无编码器架构（§2.3）

12B 从零训练，用轻量投影模块替代独立的视觉与音频编码器。视觉侧输入 48×48×3 的 RGB 图块，用一个大矩阵乘（35M 参数）替代 550M 视觉编码器，在最终 LayerNorm 前加 2D 坐标位置嵌入。音频侧整个丢弃 305M 的 Conformer 编码器，把 16kHz 下 40ms 的原始音频切成 640 维向量直接投影进嵌入空间，不再加位置编码。Table 8 显示，没有专用音频编码器的 12B 仍有有竞争力的音频转写与翻译表现。

### 3.5 MoE 26B-A4B

报告只确认 26B-A4B 是 MoE 并给出总参与激活参数；专家数、共享与路由专家划分、top-k 与负载均衡方法均未公开。开发者概述补充：生成时每个 token 只激活 4B 参数，但全部 26B 都须装入内存，内存需求更接近 26B 稠密模型。

## 四、核心机制：效率与基础设施

### 4.1 预训练与算力（§2.4、§2.7，Table 2）

预训练沿用 Gemma 3 的做法；数据含网页、代码、图像与音频（音频仅用于 E2B、E4B 与 12B），截止日期为 2025 年 1 月；过滤基准污染、不安全内容与复述风险。训练 token 总量未给出。

| 型号 | TPU | 芯片数 | Data | Seq | Replica |
|---|---|---:|---:|---:|---:|
| E2B | v6e | 4,096 | 16 | 8 | 32 |
| E4B | v6e | 6,144 | 16 | 16 | 24 |
| 12B | v4 | 12,288 | 16 | 16 | 48 |
| 26B-A4B | v6e | 6,144 | 16 | 16 | 24 |
| 31B | v6e | 10,240 | 16 | 16 | 40 |

大型号用 Slice-Granularity Elasticity，局部故障时以更少的 slice 继续训练，中断延迟从「many minutes」降到「a few seconds」。优化器状态用 ZeRO-3 分片；多 pod 训练按 Pathways 做数据副本归约；编程模型为 JAX 单控制器加 Pathways、GSPMD 与 MegaScale XLA。

### 4.2 QAT 与内存（§2.5，Table 3）

报告针对两种权重表示做 QAT：mobile 量化（逐通道低比特权重，int2 与 int4 混合，激活 int8）与 Q4_0 分块量化。为在 fp16 下稳定推理，每个 block 加一个标量缩放来限制激活范围。

Table 3（纯文本，单位 Gb；+KV 为 32k 上下文下的 int8 KV 缓存）：

| 型号 | bf16 | 量化 | +KV |
|---|---:|---:|---:|
| E2B | 4.6 | 0.8（mobile） | +0.05 |
| E4B | 9.0 | 2.3（mobile） | +0.14 |
| 12B | 24.0 | 7.65（Q4_0） | +0.28 |
| 26B-A4B | 52.0 / 7.6 | 16.2 / 2.8（Q4_0） | +0.28 |
| 31B | 64.0 | 19.2（Q4_0） | +1.10 |

编码器也做 QAT：150M 图像编码器量化到 W8A8 后，前向内存从 400 MB 降到 200 MB，相对 Gemma 3n 在新硬件上延迟降低 44%；音频编码器权重按层簇取 2、4、8 比特，磁盘占用从 Gemma 3n 的 390 MB 降到 87 MB，减少 78%。开发者概述另给含 20% 加载开销的内存表，口径与 Table 3 不同，不能混用。

### 4.3 MTP drafter（§2.6）

与主模型一同训练的小型自回归 MTP 头，用于投机解码。它以主模型上一步的最后一层激活和 token 嵌入为输入，用独立嵌入器与一个 4 层 Transformer 块交叉注意主模型的 KV，因而不需要 MTP 预填充，支持任意草稿长度。该块的模型维度 E2B、E4B 为 256，26B-A4B 与 31B 为 1024，含三层 local、一层 global 注意力。E2B、E4B 的 drafter 把全词表投影换成对 token 簇的 top-k，最终矩阵乘从 d×262,000 降到 d×4096，接受率相近。

### 4.4 指令微调与对话协议（§3，Table 11）

后训练沿用 Gemma 3，主要差别是加入 thinking 模式：模型先输出推理轨迹再回答。数据过滤去掉个人信息、不安全输出、错误自我认同与重复样本，并加入鼓励归因、对冲与拒答的子集以减少幻觉。PT 与 IT 共用 tokenizer，PT 生成以 eos 结束，IT 以回合结束符结束，微调时须加对应的结束符；thinking 开关放在开头的 system 回合，控制符与函数调用格式见 Table 11。

## 五、主要结果（§4）

| 维度 | 报告数字 | 出处 |
|---|---|---|
| Arena 文本榜（as of June 19, 2026） | 31B 为 1451，26B-A4B 为 1438，Gemma 3 27B 为 1366；报告称 31B 是榜上领先的稠密开源模型 | Table 4 |
| 文本与智能体（31B 对 Gemma 3 27B） | MMLU Pro 85.2 对 67.6；AIME 2026 无工具 89.2 对 20.8；LiveCodeBench v6 80.0 对 29.1；GPQA Diamond 84.3 对 42.4；Tau2 retail 86.4 对 6.6 | Table 5 |
| 视觉（31B，1120 视觉 token） | MMMU Pro 76.9，MATH-Vision 85.6，InfographicVQA 92.0；E4B 在全部视觉评测上持平或超过 Gemma 3 27B | Table 6 |
| 音频（对 Gemma 3n 同档） | 翻译相对提升 12%（E2B）与 10%（E4B），转写相对提升 17% 与 12% | Table 7 |
| 长上下文（不开 thinking） | RULER 128k：31B 为 96.4，Gemma 3 27B 为 66.0；LOFT 文本检索 128k：79.5 对 8.6 | Table 9 |

Table 5 中 Gemma 4 为 thinking 模式，Gemma 3 27B 为 non-thinking。报告另称 E2B 以少 10 倍的参数大致追平 Gemma 3 27B。

## 六、意义

Gemma 4 把 Google 的多模态与推理能力落成一套可下载、可复现的权重族，并公开了闭源 Gemini 不给的工程配方：local/global 注意力加 p-RoPE 与 KV 复用，用来控制长上下文的 KV 缓存；mobile 与 Q4_0 两种 QAT 格式，加上同训的 MTP drafter，用来压内存与提解码速度。12B 去掉独立编码器、直接投影原始图块与音频，是多模态架构上值得跟踪的一个开源样本。

## 七、局限与待核实

1. **26B-A4B 激活参数的写法不一**：正文写 3.8B activated，Table 1 Einsums 列写 2,800M (active)，型号名与 Arena 表写 4B；引用时须标明出处。
2. **未公开项**：训练 token 总量、MoE 专家配置、thinking 预算的数值均未给出。
3. **视频**：开发者概述把视频列为输入模态，并写 Audio featured natively on the E2B, E4B and 12B；括注是否同时覆盖视频，页面没有拆开。报告正文只讲文本、图像与音频，视频管线细节待核。
4. **版本差异**：v1 写训练用 TPUv5p 与 TPUv6e，Table 2 中 12B 为 v5p；v2 改为 TPUv4，并增补作者名单。本篇按 v2。
5. **日期不一致**：开发者概述的 Last updated 为 2026-07-08，早于报告 v2；本篇按 v2 日期计截至，概述中的上下文窗口、视频与内存表可能未反映 v2 的修订。
6. **安全**：§5 只给定性结论（各尺寸政策违规极少，各类内容安全相对 Gemma 3 与 3n 明显改进），没有分项数字。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[Gemini25技术报告深读]] | Gemma 4 沿用其 tokenizer 与 Slice-Granularity Elasticity | Gemini 2.5 的架构、能力与安全结论 |
| [[端侧小模型]] | E2B、E4B 的 PLE 与 mobile QAT 是那篇的一个对照点 | 端侧部署与其他端侧路线 |
| [[ZeroQAT量化感知训练]] | 本篇 4.2 的 mobile 量化（int2 + int4 权重、int8 激活）是官方用量化感知训练做好的分发件；那篇是量化感知训练算法本身，用零阶梯度绕开反向传播与直通估计器，大幅降低训练内存。两篇是 QAT 的「产物」与「方法」之分 | QAT 训练算法 |
| [[投机解码原理与发展脉络]] | 与主模型同训的 MTP drafter 及各尺寸规格，是那篇脉络中的一个节点 | 投机解码通史 |
| [[多模态架构脉络]] | 12B 去掉独立编码器、直接投影原始输入的范式 | 多模态融合方式的通史 |
| [[长上下文位置编码与系统侧]] | local/global 注意力、p-RoPE 与 KV 复用的配方 | 长上下文方法的总览 |
| [[MedGemma医学专科]] | 同属 Gemma 家族，那篇是医学专科分支，本篇是通用开放权重族 | 医学专科模型 |
| [[开源与闭源前沿模型谱系]] | Gemma 4 在那篇中作为开放权重模型的一个节点 | 各厂代际坐标 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Gemma 4 arXiv（v2）](https://arxiv.org/abs/2607.02770v2) | §2 架构与效率、Table 1 至 Table 3、Table 11 控制符 |
| 2 | [Gemma 4 开发者概述](https://ai.google.dev/gemma/docs/core) | 上下文窗口、内存表与 QAT 权重下载 |
| 3 | [Gemma 3 Technical Report](https://arxiv.org/abs/2503.19786) | Gemma 4 沿用的 local/global 注意力与训练配方 |
