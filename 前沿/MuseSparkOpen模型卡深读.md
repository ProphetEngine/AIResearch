---
date: 2026-10-16
status: archived
archived: 2026-10-16
topic: MuseSparkOpen模型卡深读
title: "Muse Spark Open 模型卡深读"
lines: [评测字段, 风险框架, 开放权重]
sources:
 - https://research.meta.ai/blog/muse-spark-open
 - https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B
 - https://research.meta.ai/static/muse-spark-open-evaluation-methodology
 - https://dev.meta.ai/models/muse-spark-open
 - https://huggingface.co/blog/meta-muse-spark-open
related: ["MuseWonder模型卡深读", "混合专家架构", "开源与闭源前沿模型谱系", "模型卡与SystemCard规范", "GPToss模型卡深读"]
retrieval_cutoff: 2026-10-15
timezone: Asia/Shanghai (CST)
---

# Muse Spark Open 模型卡深读

> **主要来源**：[Introducing Muse Spark Open, The Most Capable US Open‑Weight Model to Date](https://research.meta.ai/blog/muse-spark-open)；[Muse-Spark-Open-816B-A42B](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B)；[Muse Spark Open Evaluation Methodology](https://research.meta.ai/static/muse-spark-open-evaluation-methodology)；[Muse Spark Open](https://dev.meta.ai/models/muse-spark-open)；[Welcome Muse Spark Open: open-weight frontier multimodal mixture-of-experts model from Meta](https://huggingface.co/blog/meta-muse-spark-open)（截至 2026-10-15）。下文「博文」指 Meta 发布博文，「模型卡」指 Hugging Face 模型页上的 Muse Spark Open Model Card，「方法文档」指评测方法文档，「开发者页」指 Meta 开发者平台的模型页，「HF 博文」指 Hugging Face 的集成介绍。
> **研究线**：评测字段（只与开放权重模型比较，方法文档逐项写明来源与 harness）· 风险框架（Meta Superintelligence Scaling Framework 下的开放权重发布判定）· 开放权重（许可证与本地部署路径）
> **范围与相邻笔记**：
> - ≠ [[MuseWonder模型卡深读]]：本篇不写 Muse Wonder 的 Active Memory、Active Focus 与分领域风险判定，只把它当作同一模型家族闭源一侧的对照。
> - ≠ [[GPToss模型卡深读]]：本篇不写 gpt-oss 的对抗微调评估，只把它当作开放权重安全评估的先例。
> - ≠ [[混合专家架构]]：本篇不写 MoE 的一般原理，只写模型卡公开的配置。
> - 本篇不展开生物与化学评估的内容，不收攻击步骤，不搬分数表。
>
> **意义**：Muse Spark Open 是 Meta 在闭源的 Muse Spark 基础上额外做安全后训练、以开放权重发布的 MoE 模型。模型卡公开了层数、注意力头、专家数与编码器配置，并说明开放权重版本要在「没有系统级护栏」的条件下单独抵御滥用；完整评估报告截至 2026-10-15 尚未发布。

**一句话**：Muse Spark Open 于 2026-10-15 发布权重，816B 总参、42B 激活的原生多模态 MoE（Mixture-of-Experts，混合专家），推理时上下文 1M token，面向编码、智能体与长程任务，按 Muse Model License（含有限商用条款）开放；「迄今最强的美国开放权重模型」是 Meta 的自述。

## 一、问题背景

闭源模型的安全措施有一部分在系统层：服务端的分类器、监控与拒答策略都由厂商掌握。权重一旦开放，下载者可以绕开这些系统层护栏，也可以继续微调模型，厂商只能靠模型本身的行为来抵御滥用。模型卡把这一点写成开放权重版本的设计目标：额外做安全后训练，使模型「作为没有系统护栏的独立模型」也更能抵御滥用；同时仍建议把它部署在带护栏的更大 AI 系统中。

能力一侧，Meta 把它定位为编码与智能体模型：长程任务、复杂软件工程与多步推理（博文）。HF 博文补充，Meta 称它在多文件重构、长时间调试等真实开发者工作流上训练。

## 二、脉络

| 时间 | 节点 | 关系 |
|---|---|---|
| 开发者页所称「8 月」 | Muse Spark | 闭源母型；开发者页称 Muse Spark Open 由 8 月发布的 Muse Spark 派生 |
| HF 博文所称「8 月」 | Muse Glimmer | HF 博文称其为同一系列的小型 dense 模型，与 Muse Spark Open 共用分词器与词表 |
| 2026-10-12 | Muse Wonder / Muse Wonder Full | Meta 闭源一侧的前沿模型，见 [[MuseWonder模型卡深读]] |
| 2026-10-15 | Muse Spark Open | Muse 系列的满尺寸开放权重模型（HF 博文），在 Muse Spark 之上加做安全后训练 |

Meta 的模型家族因此同时有闭源与开放权重两条线；开放权重一侧的 Muse Spark Open 以「去掉系统护栏后模型本身是否稳健」为评估前提。开放权重谱系的整体格局见 [[开源与闭源前沿模型谱系]]。

## 三、架构与规格（模型卡 Model Overview）

| 字段 | 内容 |
|---|---|
| 类型 | MoE Transformer，附感知编码器（Perception Encoder） |
| 参数 | 816B 总参、42B 激活 |
| 语言模型 | 62 层；分组查询注意力（GQA），128 个查询头、16 个 KV 头；注意力块带输出门控与输出归一化，启用 QK 归一化；每层 256 个专家，每个 token 经 top-k 路由选 8 个 |
| 感知编码器 | 1.8B 参数、50 层，每 4 层与最后一层为全注意力，其余为稀疏注意力 |
| 模态 | 输入文本、图像、视频、音频；输出文本 |
| 上下文 | 推理时 1M token |
| 语言 | 训练数据覆盖 100 多种语言 |
| 训练数据 | 公开来源、网络爬取、第三方采购、Meta 产品与服务衍生数据及合成数据；只给类别，不给配比 |
| 未披露 | 训练 token 数、训练算力与硬件、数据配比、预训练与后训练配方 |

HF 博文补充三点结构细节：每个块用可学习的残差门控而非直接相加来合并输入与输出；专家占总参数的绝大部分，每个 token 只算 8 个专家，因此部署要装下全部参数、计算量却接近激活参数规模；音频经独立的音频编码器转成 token，视频与图像共用感知编码器。GQA 让多个查询头共用同一组键值头，HF 博文称这使这一规模的模型的 KV 缓存保持较小。

推理强度分 low、medium、high、xhigh 四档，默认 xhigh，不能关闭推理（模型卡；HF 博文）。对话模板沿用 gpt-oss 引入的通道式格式（HF 博文），推理、工具调用前的说明与最终回答走不同通道；开发者页称单独的说明通道让模型在行动前先陈述意图。

## 四、能力取向与评测方法

模型卡列出七类用途：多步推理、端到端智能体任务、编码智能体、工具使用、多模态推理、合成数据生成、以模型作评审。博文另举两例本地智能体工作流：用 Muse Code 在设备上为开源 Mastodon 客户端提交 iOS 修改，以及端到端操作 DaVinci Resolve 剪辑视频。

方法文档的设计要点如下，分数本身不在本篇复述。

- **只比开放权重**：对比对象全部是开放权重模型（Inkling、Nemotron 3 Ultra、Beam、Mistral Large 4、Qwen3.8-2.4T-A95B、GLM 5.3、Kimi K3），各取可用的最高推理强度；内部运行时用各厂商推荐的采样参数。
- **取分顺序**：所有模型都有官方榜单或基准方结果时用官方来源；否则取内部运行或厂商自报中可比的最高主指标值。Beam 与 Mistral Large 4 当时没有广泛可用的权重，只引其自报数字与 Artificial Analysis 的结果。
- **第三方模型是尽力而为**：方法文档承认智能体工具与系统提示没有针对第三方模型调优，未必反映其最佳表现。
- **harness 不统一**：编码类基准按各模型的首选或自报 harness 取数，Muse Spark Open 用的是 Meta 自家的 Muse Code；OSWorld-Verified 让各模型用各自训练时的坐标格式，不强行统一。同一行内的数字因此并非同一 harness 下的受控对比。
- **多模态只比三家**：不支持原生多模态输入的模型不跑多模态评测，多模态行实际只有 Muse Spark Open、Inkling 与 Kimi K3。
- **安全基准有内部自建**：StrongREJECT v2 是在 StrongREJECT 基础上加入内部整理行为的内部基准，每个行为在越狱策略库、对抗性开发者提示与自适应多轮攻击者等五种条件下受攻击，任一次攻破即计为攻破；FORTRESS 结果取自 Scale 榜单的私有划分。

## 五、开放权重安全与风险判定（模型卡 Safety and Preparedness）

**动机。** 博文称开放权重有其自身的考量，因此 Muse Spark Open 做了额外的安全后训练；模型卡说明目标是让它作为没有系统护栏的独立模型更能抵御滥用。

**四个评估领域。** 模型卡列出：内容安全（有害内容生成与拒答，兼顾回答质量与意识形态平衡）、智能体风险（使用工具或代用户行动时的有害或越权操作，包括编码智能体中的不安全代码执行与破坏性修改）、隐私（处理个人与敏感信息的方式）、Preparedness（按 Meta Superintelligence Scaling Framework 评估化学与生物、网络与失控风险）。

**判定。** 博文称模型按该框架评估了最严重的风险，达到框架要求的发布门槛；模型卡称基于模型评估与剩余风险评估满足发布的安全标准。Muse Spark Open 的模型卡没有给出分领域风险档位；闭源同族的判定写法见 [[MuseWonder模型卡深读]]。

**Preparedness 各领域的结论。**

- **网络安全**：评估设定是自适应攻击者像调用 API 模型那样直接查询模型，不加任何系统级防护；模型卡称在内部基准上拒绝了 99.2% 的越狱，并在同一设定下与 Kimi K3 对比。这一设定对应的正是开放权重的使用方式。
- **化学**：模型卡称模型在化学有害请求上拒答表现强。
- **失控**：用 MASK（受压时是否保持诚实）与 Agentic Misalignment（是否为达成目标采取单方面有害行动）两项评测，模型卡称欺骗或单方面有害行为的倾向低。

**适用范围。** 模型卡写明，这些评估只刻画所发布检查点在测试条件下的表现，不覆盖所有下游配置与用例；下游修改可能削弱安全性，所发布检查点的结果不应被假定适用于修改后的模型。

## 六、许可证与部署生态

**许可证。** Muse Model License 允许免费使用、复制、修改（含微调）、蒸馏、合并与再分发，Meta 不主张对输出的所有权（模型卡页许可证全文）。附加条件有三：使用该模型或其衍生模型的产品须醒目标注「Built with Muse Spark Open」；以「模型即服务」形式向第三方提供模型、且连续 12 个月总收入超过 2000 万美元的被许可方，须通知 Meta 并另签书面协议，内部使用、研究与非模型即服务的商业用途不受此条限制；须遵守附带的使用政策，不面向 18 岁以下用户。博文把这些条款概括为「有限商用条款」。

**部署路径。**

- **云端**：博文列出多家托管推理 API 平台；权重可从 Hugging Face 与几家云厂商的模型库下载，提供 BF16 与 NVFP4 两种格式（模型卡）。
- **推理引擎**：博文列出 SGLang、vLLM、TensorRT-LLM、Hugging Face Transformers、Apple MLX、llama.cpp 与 Unsloth；SGLang 中附带可自动调优的 Helion GPU 内核。
- **本地**：博文称两台 Apple M5 Ultra Mac Studio 经最新版 MLX 可运行完整模型，依据是统一内存能装下全部权重、而每个 token 只需读取激活的一小部分参数。
- **继续训练**：博文建议用 PyTorch 的 TorchTitan 继续微调；HF 博文给出一个只在注意力层上训练 LoRA 适配器、冻结全部专家的示例。

## 七、意义

1. **开放权重的安全评估前提被写明**：模型卡把「没有系统护栏、自适应攻击者直接查询」作为网络评估的设定，并声明结果不适用于下游修改后的模型。这比只报告带护栏系统的拒答率更贴近开放权重的实际风险面。
2. **架构披露**：模型卡公开了层数、注意力头、专家数、路由与编码器配置，可与 [[GPToss模型卡深读]] 等开放权重模型卡对照；闭源同族的披露范围见 [[MuseWonder模型卡深读]]。
3. **评测来源逐项可查**：方法文档逐项说明每个分数取自官方榜单、内部运行还是厂商自报，并承认第三方运行未经调优、harness 不统一。

## 八、局限与争议

- 完整评估报告截至 2026-10-15 尚未发布。博文原句为「Detailed results are in the Muse Spark Open model card, with a full evaluation report available soon.」；目前只有博文、模型卡与方法文档。
- 开放权重的可滥用面：模型卡自己写明下游修改可能削弱安全性；模型卡没有报告针对恶意微调的评估，本篇未见相关材料。
- 「迄今最强的美国开放权重模型」「同级中首个可在桌面运行的模型」都是 Meta 的自述；对比对象、推理强度与 harness 由 Meta 选定，部分数字为厂商自报或内部运行，未经独立复现。
- StrongREJECT v2 等安全基准是内部基准，外部无法复现；模型卡没有分领域风险档位，无法与 Muse Wonder 的判定逐项对照。
- 参数口径两处并列：博文与模型卡写 816B 总参；Hugging Face 模型页侧栏的自动统计显示「Model size 822B params」。两者的统计范围未说明。
- 训练数据只给类别，训练 token 数、算力与配方均未披露。
- 模型卡 Considerations and Limitations 一节列出的已知局限：可能产生不准确、有偏或令人反感的回答；新场景下多步推理仍会出错；并非所有预训练语言都做过评测；量化推理在边缘情况下与全精度略有差异；不面向 18 岁以下用户；很短或低分辨率的视频可能被回答为无法查看。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[MuseWonder模型卡深读]] | 同一模型家族的闭源一侧：两篇可对照阅读 Meta 在闭源与开放权重两种发布形态下的模型卡写法与风险判定 | Muse Wonder 的能力定义、评测口径与分领域判定 |
| [[混合专家架构]] | 原理背景：本篇第三节的专家数、top-k 路由与激活参数以该篇所述 MoE 原理为前提 | MoE 的一般原理与路由设计 |
| [[开源与闭源前沿模型谱系]] | 所在谱系：本篇是开放权重一侧的新节点，可与该篇的开放权重与闭源格局对照 | 各家谱系全表 |
| [[模型卡与SystemCard规范]] | 体裁背景：本篇的模型卡与方法文档分开发布、完整评估报告后发，可对照该篇的字段谱系 | 模型卡与系统卡的字段规范 |
| [[GPToss模型卡深读]] | 先例：该篇是开放权重安全评估的先例，本篇的「无护栏条件下评估」可与之对照 | gpt-oss 的架构、对抗微调与评测 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Muse Spark Open 博文](https://research.meta.ai/blog/muse-spark-open) | 定位、本地部署路径、安全与许可证概述 |
| 2 | [Muse-Spark-Open-816B-A42B 模型页](https://huggingface.co/meta-models/Muse-Spark-Open-816B-A42B) | 模型卡的规格表、Safety and Preparedness 与许可证全文 |
| 3 | [Muse Spark Open Evaluation Methodology](https://research.meta.ai/static/muse-spark-open-evaluation-methodology) | 逐项来源、harness 与安全基准定义 |
| 4 | [Hugging Face 集成介绍](https://huggingface.co/blog/meta-muse-spark-open) | 结构细节、推理强度与部署配方 |
