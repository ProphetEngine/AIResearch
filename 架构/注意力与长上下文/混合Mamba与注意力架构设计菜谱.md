---
title: "Hybrid Mamba–Attention 混合架构设计菜谱"
topic: 混合Mamba与注意力架构设计菜谱
date: 2026-09-25
lines: [架构思想]
status: archived
sources:
  - https://arxiv.org/abs/2510.04800
arxiv: ["2510.04800"]
related:
  - "线性注意力与状态空间模型谱系"
  - "注意力效率族MQA到MLA"
  - "混合专家架构"
  - "Nemotron3Ultra技术报告深读"
  - "Qwen38Next架构深读"
  - "KimiK3技术报告"
  - "MiniMaxM1技术报告深读"
  - "长上下文与注意力效率时间线"
  - "门控注意力与注意力汇"
retrieval_cutoff: 2026-08-31
timezone: Asia/Shanghai (CST)
boundary: "≠ Nemotron3Ultra技术报告深读 单机 Hybrid+LatentMoE 配方深读；≠ Qwen38Next架构深读 的 GDN/QSA 产品深读"
archived: 2026-09-28
---

# Hybrid Mamba–Attention 混合架构设计菜谱

> **主要来源**：[Hybrid Architectures for Language Models: Systematic Analysis and Design Insights](https://arxiv.org/abs/2510.04800)（Bae、Acun、Lin 等，FAIR at Meta / Meta / KAIST AI，v3 2026-04-21）（截至 2026-08-31）。
> **研究线**：架构思想——注意力与 Mamba 的层间（inter-layer）、层内（intra-layer）混合，块比例与摆放，长上下文中外推与检索的分工。
> **范围与相邻笔记**：
> - ≠ [[线性注意力与状态空间模型谱系]]：那篇写线性注意力与 SSM 的原理和谱系，本篇只写同预算对照给出的混合设计规律。
> - ≠ [[Nemotron3Ultra技术报告深读]]、[[Qwen38Next架构深读]] 等各厂报告：那些写具体产品的混合配方，本篇只写通用的对照实验，各篇关系见第八节分工表。
>
> **意义**：此前各家混合模型的比例与摆放各自选定、不可互比；该文在同一预算下把两种混合方式、多种比例与位置放在一起比较，给出了可复用的设计建议。

## 一、问题背景：为什么要混

| 原语 | 长处 | 短板 |
|---|---|---|
| **Softmax 注意力（Transformer）** | 任意位置精确对齐，检索类任务强 | 计算随序列长度二次增长；KV 缓存随长度增长；超过预训练长度后因位置编码而外推困难（§4.3） |
| **Mamba / SSM（以及滑窗注意力 SWA）** | 计算随长度线性增长；Mamba 缓存大小与序列长度无关 | 偏重局部信息，窗外、远距离的检索差——困惑度好不等于找得到（§4.3） |

主文给的量级（§2）：1B 模型、8K 上下文下，Transformer 每样本 FLOPs 比 Mamba 多约 18%；Mamba 每块参数是注意力块的 2.5 倍（25M 对 10M），缓存却比 Transformer 小 95%（256 MiB 对 13.4 MiB）。

混合的思路：用少量全局注意力保留精确检索，用大量线性原语承担长序列吞吐与长度外推。原理与「固定大小状态对 KV 缓存」的取舍见 [[线性注意力与状态空间模型谱系]]（前置）；本篇只看怎么混。

## 二、发展脉络

| 时间 | 工作 | 贡献 |
|---|---|---|
| 2022-12 | [H3](https://arxiv.org/abs/2212.14052) | 指出 SSM 在回忆前文 token、跨序列比较 token 两项能力上不足；保留两层注意力的 125M H3–注意力混合模型在 OpenWebText 上比 Transformer 低 1.0 PPL（摘要） |
| 2024-03 | [Jamba](https://arxiv.org/abs/2403.19887) | 交错 Transformer 层与 Mamba 层并在部分层加入 MoE，单张 80GB GPU 可放下，长上下文评测到 256K token（摘要） |
| 2024-05 | [Zamba](https://arxiv.org/abs/2405.16712) | 7B，Mamba 主干加一个共享的注意力模块，以很小的参数代价获得注意力的好处（摘要） |
| 2024-06 | [Samba](https://arxiv.org/abs/2406.07522) | 逐层组合 Mamba 与滑窗注意力；3.8B、3.2T token；4K 上微调后可外推到 256K 并在 Passkey Retrieval 上完全召回（摘要） |
| 2024-06 | [An Empirical Study of Mamba-based Language Models](https://arxiv.org/abs/2406.07887) | 8B、同数据对照：纯 SSM 在复制、上下文学习（如 5-shot MMLU、Phonebook）和长上下文推理上落后；43% Mamba-2 + 7% 注意力 + 50% MLP 的混合模型在 12 项标准任务上均超过同规模 Transformer（平均 +2.65）（摘要） |
| 2024-11 | [Hymba](https://arxiv.org/abs/2411.13676) | 混合头并行（层内混合）：注意力头负责高分辨率召回，SSM 头负责上下文摘要；另加可学习的 meta token（摘要） |
| 2025-04 | [Nemotron-H](https://arxiv.org/abs/2504.03624) | 8B 与 56B/47B，把大部分自注意力层换成 Mamba 层，精度与同规模开放 Transformer 相当或更好，推理最快 3 倍（摘要） |
| 2025-07 | [Falcon-H1](https://arxiv.org/abs/2507.22448) | 并行混合（注意力与 SSM 并联），0.5B–34B 多个规模，支持 256K 上下文（摘要） |
| 2025-08 | [Nemotron Nano 2](https://arxiv.org/abs/2508.14444) | 沿用 Nemotron-H 架构（大部分注意力层换成 Mamba-2），面向长推理链；8K 输入、16K 输出场景下吞吐最高 6 倍于同规模模型（摘要） |
| 2025-10 | [Hybrid Architectures for Language Models](https://arxiv.org/abs/2510.04800)（本篇主文，v1） | 同预算下系统比较层间与层内混合、块比例与摆放 |
| 2025-10 | [Kimi Linear](https://arxiv.org/abs/2510.26692) | KDA（细粒度门控的 Gated DeltaNet）与 MLA 逐层混合，官方称首次在公平对比下超过全注意力；1M 上下文下 KV 缓存最多减 75%、解码吞吐最高 6 倍（摘要） |

脉络上，混合先从「SSM 补不上的能力由少量注意力补」（H3）出发，2024 年起在大模型上落地为两条路：整层交错（Jamba、Zamba、Samba、Nemotron-H）与层内并联（Hymba、Falcon-H1）。主文的作用是在同一预算下把这两条路放在一起比较。

## 三、主文概况

| 项 | 内容 |
|---|---|
| 作者 | Sangmin Bae, Bilge Acun, Chien-Yu Lin, Haroun Habeeb, Seungyeon Kim, Liang Luo, Junjie Wang, Carole-Jean Wu |
| 版本 | v1 2025-10-06；v2 2026-03-23；v3 2026-04-21（引用此版，版本差异见第七节） |
| 实验骨架 | 原语按 Llama 3.2 与 Mamba 2 配置；TorchTitan、H200 训练（§4）；主对照为 350M 与 1B，缩放分析 100M–3B；DCLM 约 60B token、预训练上下文 8K；附录 H 另有 16K、32K 预训练结果 |

## 四、两种混法与长文分工

### 4.1 层间混合（inter-layer）

整层二选一：一层是 Transformer 就整层是注意力，否则整层是 Mamba，按比例交错堆叠（§3.1）。实现简单，是现有混合模型的主流做法（文中列举 H3、Zamba、Jamba、Samba、Nemotron nano 2 等）。可调的主要是 Transformer 与 Mamba 的块比，以及 Transformer 放在哪一层。

### 4.2 层内混合（intra-layer）

同一层内按头拆分：一半头走注意力、一半头走 Mamba，再融合输出；整网再在「层内混合块」与纯 Mamba 块之间按比例交错（§3.2）。文中取按头拆分（Hymba、Falcon-H1 一路），并系统比较归一化、可学习标量或门控、相加 / 相减 / 拼接、输出投影等变体（Table 6）。

同设定下，层内混合占据质量与效率的帕累托前沿（§1，Table 2）；即使两支串行执行，用半尺寸 Transformer 的层内混合吞吐也优于层间混合（§4.2）。

### 4.3 长文：外推靠谁、检索靠谁

| 能力 | 主要依靠 | 文中现象（1B、8K 预训练、1:5 块比） |
|---|---|---|
| **长度外推（困惑度）** | Mamba | PG19 逐位置损失：超过 8K 后 SSM 能外推，Transformer 受位置编码拖累；混合模型借 Mamba 保持外推（§4.3）。文中还提出，混合模型中显式位置信息多余，可改用 NoPE 进一步消除 Transformer 一侧的外推限制（§4.3） |
| **上下文内检索（大海捞针）** | 全局注意力，但需与 Mamba 协同 | Transformer 超过 8K 后准确率接近零；SWA 与 Mamba 在窗口与 sink 区域之外、远距离处检索困难；层间、层内混合都能把较强的检索保持到约 1.5 倍预训练长度，外推区间中段的准确率仍会下降（§4.3） |

线性支路负责读得下去、外推不崩，少量全局注意力负责找得到；文中的说法是混合模型克服了两种原语各自的局限，而不是简单继承（§4.3）。

## 五、设计建议对照表

（综合 §4.5–§4.6、Table 4–6；默认 DCLM 约 60B token、8K 上下文、1B 规模。）

| 决策轴 | 层间混合（Transformer / Mamba） | 层内混合（层内混合块 / Mamba） |
|---|---|---|
| **块比** | 质量优先约 1:1（1B：DCLM NLL 2.725 / 准确率 54.0）；兼顾效率约 1:5（同表 2.735 / 53.3），与大模型常用的 1:5、1:7 等低比例一致（Table 5） | 含注意力的块越多质量越好，为效率可多留纯 Mamba 块；主结果用 1:5（2 个层内混合块 + 11 个 Mamba 块）（§4.6，Table 4） |
| **摆放** | 不要把 Transformer 放在最前；放在中间层效果最好。附录 O 的注意力分数显示，前层 Transformer 的注意力过于均匀、全局，作者推测这与 Mamba 的局部偏置冲突（§4.5） | 含注意力的块均匀散开（Scatter）最好；两端也放（Sandwich）大幅掉点（§4.6） |
| **块内维度比** | — | 加大 Transformer 支路维度有利质量，但并行执行时吞吐受注意力支路限制，1:1 维度分配是实用折中（§4.6） |
| **融合方式** | 层即原语本身 | 归一化很关键（两模块输出尺度不同），有了归一化后额外的标量或门控多余；融合用相减（抑制注意力噪声）或拼接最好；最优变体（Group 归一化 + 相减，输出投影一栏取 2）准确率 54.9，高于复现的 Hymba 52.4 与 Falcon-H1 53.6（Table 6） |
| **与 MoE** | 混合只改序列混合模块，FFN 换成 MoE 完全兼容；各架构加 MoE 后 NLL 约降 0.08、few-shot 准确率约升 4 个点（§4.4）。Table 4：层间混合 53.3→56.0 | 同上（层内混合 54.7→56.9） |
| **缩放** | 计算最优线介于 Transformer（每参数约 20 token）与 Mamba（更大模型、更少数据）之间 | 比层间混合略更吃数据（§4.4） |

附录 Q 用可学习的插值权重 α 让模型自己决定层内混合块中两支的比重，结果与手工结论一致：前几层偏向 Mamba，中间层偏向 Transformer；逐 token 看，Transformer 在关键句法边界处激活，Mamba 处理局部的子词依赖（§4.6）。

**速记三条**

1. 要质量：多留注意力（层间 1:1；层内提高混合块占比或 Transformer 维度）。
2. 要吞吐与缓存：压到约 1:5，并让全局注意力落在中段、均匀散开。
3. 长文：Mamba 保外推，注意力保检索；不要指望纯 SSM 或纯滑窗单独完成检索。

## 六、意义

主文的价值在于可比性：Jamba 的 1:7、Nemotron-H 的「大部分层换成 Mamba」等选择原本各自依赖不同的数据与规模，无法互相印证；该文在同一预算、同一套原语下给出了块比、摆放、融合方式的对照，并把「Mamba 保外推、注意力保检索」从经验说法变成了可复现的实验现象。作者称这是对层间与层内混合取舍的首次深入比较（§4.1）。

## 七、局限与待核实

1. **规模**：实验最大到 3B、60B token，作者自己也把更大规模、更长训练下优势是否保持列为待验证问题（§6）。
2. **原语**：只用基础 Transformer 与 Mamba 块；Qwen3-Next、Kimi Linear 等采用的门控注意力、Gated DeltaNet、KDA 等新原语上这些结论是否成立，作者列为开放问题（§6）。
3. **下游任务**：Table 3 中混合模型并非处处领先，例如 GovReport 上层间混合 19.56、低于 Transformer 的 20.55；v3 把三项下游任务匿名为 Task A/B/C，只报相对 Transformer 的差值，无法与外部结果对照。
4. **长文检索**：约 1.5 倍预训练长度的结论来自 1B、8K 的大海捞针测试；更长上下文、更难检索任务未覆盖。
5. **版本差异**：v1（2025-10-06）已有主表（Table 2、4、5、6）与「2.9%」结论；v2（2026-03-23）篇幅大幅扩充，补充训练曲线、下游微调、附录 O 注意力分数可视化、NoPE 讨论与附录 Q 学习式路由等；v3 相对 v2 正文结论不变，主要改动是把下游任务中的 Multi-News、BIGPATENT、NarrativeQA 换成匿名任务并改报相对分数。本篇按 v3 写。
6. **图读数**：Figure 3、4 的曲线与热力图未读数，相关结论只取正文文字。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[线性注意力与状态空间模型谱系]] | 上游前置：线性注意力、SSM、Delta 规则的统一框架与工业混合比例在那篇；本篇只给混合方式的对照实验 | Mamba、Mamba-2 / SSD、DeltaNet 的原理 |
| [[注意力效率族MQA到MLA]] | 并列：两者都为减小 KV 缓存；那篇压缩每层注意力的缓存，本篇减少注意力层的数量，Kimi Linear 把两者结合（KDA 与 MLA 混合） | MQA / GQA / MLA 机制 |
| [[混合专家架构]] | 接口：本篇只验证 FFN 换成 MoE 与混合骨干兼容 | MoE 路由与负载均衡 |
| [[Nemotron3Ultra技术报告深读]] | 下游实例：NVIDIA 把 Mamba–注意力混合与 LatentMoE 用于开放旗舰；本篇是通用对照实验，不替代该产品深读 | Ultra 的 LatentMoE、后训练与量化配方 |
| [[Qwen38Next架构深读]] | 下游实例：Gated DeltaNet 与全局注意力按每 4 层 1 层全注意力混合，属本篇第七节所说的新原语情形，结论能否迁移待验证 | GDN / QSA 产品差分 |
| [[KimiK3技术报告]] | 下游实例：KDA–MLA 混合骨干的旗舰报告 | KDA、AttnRes、LatentMoE 细节 |
| [[MiniMaxM1技术报告深读]] | 下游实例：每 7 个 lightning attention 块接 1 个 softmax 注意力块，与本篇「低注意力比例兼顾效率」的结论同向 | Lightning Attention 实现与 CISPO |
| [[长上下文与注意力效率时间线]] | 时间索引：2024-03（Jamba）与 2025-10（本篇主文、Kimi Linear）两个节点指向本篇 | 其余长上下文节点 |
| [[门控注意力与注意力汇]] | 原语：局限第 2 条列为开放问题的门控注意力，其机制在该篇 | 门控注意力的机制与实验 |

## 九、延伸阅读

- [Hybrid Architectures for Language Models（v3）](https://arxiv.org/abs/2510.04800v3)：§4.5–§4.6 与附录 N、O、P、Q 是设计建议的出处。
- [An Empirical Study of Mamba-based Language Models](https://arxiv.org/abs/2406.07887)：8B 规模的纯 SSM、混合与 Transformer 同数据对照，可与主文的 1B 结论互相印证。
- [Jamba](https://arxiv.org/abs/2403.19887)、[Nemotron-H](https://arxiv.org/abs/2504.03624)：层间混合在大模型上的两个代表。
- [Hymba](https://arxiv.org/abs/2411.13676)、[Falcon-H1](https://arxiv.org/abs/2507.22448)：层内（并联）混合的两个代表，也是主文 Table 6 复现的对照。
