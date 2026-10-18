---
date: 2026-10-12
status: archived
archived: 2026-10-13
topic: MuseWonder模型卡深读
title: "Muse Wonder 模型卡深读"
lines: [评测字段, 风险框架]
sources:
 - https://research.meta.ai/blog/muse-wonder
 - https://research.meta.ai/static/muse-wonder-model-card
related: ["开源与闭源前沿模型谱系", "GPT6Astra系统卡深读", "ClaudeFable与Mythos51", "ClaudeOpus55系统卡短报", "SystemCard谱系时间线", "MuseSparkOpen模型卡深读"]
retrieval_cutoff: 2026-10-12
timezone: Asia/Shanghai (CST)
---

# Muse Wonder 模型卡深读

> **主要来源**：[Muse Wonder: A Frontier Model For Personal & Professional AI Agents](https://research.meta.ai/blog/muse-wonder)；[Muse Wonder Model Card](https://research.meta.ai/static/muse-wonder-model-card)（截至 2026-10-12）。下文「博文」指上列发布页，「模型卡」指网页版模型卡；博文中「see our report」一句链向的就是这份模型卡。
> **研究线**：评测字段（内部基准与第三方来源分开读）· 风险框架（Meta Superintelligence Scaling Framework 下的判定）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 GPT-6 Astra 的判定与评测，只把它当作模型卡里的对比对象。
> - ≠ [[ClaudeFable与Mythos51]]：本篇不写 Claude Fable 5.1 系统卡的字段。
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写 Claude Opus 5.5 系统卡的字段。
> - 本篇不展开生物与化学评测的各项内容，不收攻击步骤。
>
> **意义**：Muse Wonder 是 Meta 以闭源 API 与产品形态发布的前沿模型，把「个人智能体」拆成 Active Memory 与 Active Focus 两种能力来定义和评测；模型卡按 Meta Superintelligence Scaling Framework 给出分领域风险判定。

**一句话**：Muse Wonder 与 Muse Wonder Full 于 2026-10-12 发布，通过 Meta Model API 与 Muse Code 提供；模型卡给出规格、评测口径和风险判定，截至 2026-10-12，完整安全报告尚未发布。

## 一、问题背景

个人智能体要替用户在消息、日历、私人文档之间行动，单看几个领域的热门基准不足以说明它能否应付各种没见过的组合任务。博文把这种落差概括为「benchmaxxing」与「big model smell」之争：分数相近的两个模型，泛化广度可能差得很远。Muse Wonder 的发布材料围绕三个问题展开：如何定义并测量记忆与持续执行；怎样论证能力能泛化到训练未覆盖的任务；在能代用户行动的前提下，如何判定滥用风险。

## 二、脉络

| 时间 | 节点 | 关系 |
|---|---|---|
| 博文所称「十四个月前」 | Meta 从底层重建 AI 技术栈 | 博文给出的起点 |
| 早于本篇 | Muse Spark | 博文称其提出了「可预测、严谨」的扩展路线；Muse Spark 1.3 是泛化对比的基线 |
| 2026-10-12 | Muse Wonder / Muse Wonder Full | 在 Muse Spark 路线上同时推进预训练与强化学习，在吉瓦级 Prometheus 数据中心训练 |

博文称 Muse Wonder 将来还会用来开发面向 Muse 全体用户的专用模型。两档的可用范围不同：Muse Wonder 当日上 [Meta Model API](https://dev.meta.ai) 与 [Muse Code](https://developer.meta.com/ai/products/muse-code)，Muse Wonder Full 只对 Muse Code 订阅者开放；之后会接入 Muse 产品，先面向订阅者。

## 三、规格（模型卡第 1 节）

| 字段 | 内容 |
|---|---|
| 模态 | 输入文本、图像、视频、音频；输出文本 |
| 上下文 | 推理时 1M tokens |
| 语言 | 多语言训练数据 |
| 未披露 | 参数量、架构、训练算力与数据配比 |

## 四、核心概念：Active Memory 与 Active Focus

- **Active Memory**：跨对话保留与用户有关的重要上下文，并在任务需要时主动检索相关细节。对应的内部基准 MemoryBench 用 64K 到 100K tokens 的多轮长对话，夹入干扰对话以及与目标事实冲突或后来更新它的轮次，由 LLM 评审按加权细则打分。
- **Active Focus**：面对困难目标时持续工作，包括换用其他方法、绕过障碍、根据新信息调整；必要时请用户澄清，执行重要操作前先确认。对应的内部基准 FocusBench 覆盖住房、出行、IT、金融等个人任务，考察跨多次交互处理真实阻碍、适应动态环境的能力；长程持续执行另用 SWE-Marathon 衡量。

编程被博文视为两者的汇合点：要跟踪需求、跨代码库修改、反复测试与修订。两档模型都在多样的长程任务上训练。

## 五、泛化论证（博文「Capabilities That Generalize」）

博文比较 Muse Spark 1.3 与 Muse Wonder Full：每个点对应一个推理强度，横轴是后训练重点任务的综合分（分布内），纵轴是后训练未针对的任务的平均分（分布外）。

- 两个模型随测试时计算增加，分布外分数的提升幅度相近。
- 在相同的分布内水平上，Muse Wonder Full 的分布外表现高于 Muse Spark 1.3 趋势线的预测。
- Meta 的解释是：Muse Wonder 建立在更大、更强的基座模型上，更强的基座让后训练收益更有效地迁移到陌生任务。

博文称这种泛化能力对个人智能体尤其重要，因为它们要应付许多训练时无法预见的目标、工具与约束组合。这一解释是 Meta 的官方解释，分布外任务集的构成没有公开，也未经独立复现。

## 六、评测口径（模型卡第 3 节）

模型卡对评测来源与配置的说明如下：

- **配置**：Muse Wonder 两档都用最高推理强度，对比对象 GPT-6 Astra、Claude Fable 5.1、Claude Opus 5.5 也取最高推理强度。内部受控的编程对比中，所有模型用同一个基准专用 harness；外部编程结果保留报告方所用的 harness 或智能体产品。
- **取分规则**：有可比的第三方或厂商自报结果时用它；否则取内部验证运行、自报分数、官方榜单三者中最高的一个。模型拒答计零分并留在分母里，不剔除（模型卡第 3 节：「Model refusals receive zero credit and remain in the denominator rather than being dropped.」）。
- **竞品运行**：内部跑的竞品结果尽量用通用设置，但模型卡承认提示、工具与运行时未必针对闭源模型调到最优。
- **内部基准多**：PSI（Personal Superintelligence Index）是内部综合指标，由七项评测组成，其中 FocusBench 与 VBT 本身也是内部基准；MemoryBench 同样是内部基准。这些分数无法在外部复现。第三方来源的有 Artificial Analysis（Harvey LAB-AA、AutomationBench-AA、Terminal-Bench 4.0、AA Intelligence Index v4.3）、Vals AI、Surge、Datacurve、Abundant AI 等。
- **SWE-Marathon 不是受控对比**：所有模型的结果都来自 Abundant AI，但其榜单上 GPT-6 Astra 用 Codex、Claude Fable 5.1 用 Claude Code，模型卡明说这一行不是同一 harness 下的受控对比；Muse Wonder Full 这一行是 xhigh 推理强度。
- **混合来源**：HealthBench Pro 中两款 Claude 的结果取自 Anthropic 系统卡；DeepSWE 的结果分别来自 Datacurve、OpenAI 自报和 Anthropic 系统卡。同一行内的数字并非出自同一次运行。

## 七、风险判定与安全（模型卡第 4、5 节）

**判定规则。** 在 Meta Superintelligence Scaling Framework 下，一个模型的部署如果可能实质促成某个被认定为严重的威胁场景，即达到高风险阈值。判定以最强的 Muse Wonder Full 为准，因此覆盖整个模型族。

| 领域 | 未缓解 | 缓解后 |
|---|---|---|
| Chemical & Biological | 不排除达到高风险阈值，因此施加针对性缓解（安全后训练与系统级分类器） | moderate or lower |
| Cybersecurity | moderate or lower | moderate or lower |
| Loss of Control | moderate or lower | moderate or lower |

所有领域缓解后都在 moderate or lower，模型卡据此支持部署决定，并称内部治理流程在部署前审阅了这一评估，开发与部署期间按生命周期权重安全计划保护模型权重。

**网络安全：ExploitGym 的计分说明。** Muse Wonder Full 在 ExploitGym 上拿下 92 个 flag。验证环节用 GPT-cyber 验证器、再由 Gemini 3.1 Pro 独立确认，发现其中只有 21 个利用的是预期漏洞，另外 71 个走的是非预期漏洞。ExploitGym 公开榜单只计预期漏洞的利用，所以与公开榜单可比的数字是 21，而不是表中标星号的 92。读这项分数要以 21 为准。

**失控领域。** 用 MASK（受压时是否保持诚实）与 Agentic Misalignment（是否为达成目标或避免被替换、关停而采取有害行动）两项评测。

**生物与 CBRN。** 结论即上表：未缓解时不排除化学与生物领域达到高风险阈值，缓解后为 moderate or lower。

**部署建议。** 模型卡建议把 Muse Wonder 作为更大 AI 系统的一部分部署，按用例加护栏；在能执行真实动作的智能体场景中，对不可逆操作加人工确认。

## 八、意义

Muse Wonder 的材料意义有二。其一，把「个人超级智能」落到可测的 Active Memory 与 Active Focus，并配上专门的内部基准，给个人智能体评测提供了一种拆法。其二，模型卡把评测口径写得较透：拒答计零分、来源逐项标注、明说哪一行不是受控对比、给 ExploitGym 的原始分加计分注释。这些口径说明比分数本身更有助于判断结果能否横向比较。

## 九、局限与争议

- 完整安全报告尚未发布，博文原句为「A full report with additional safety evaluations will be available soon.」；目前没有独立的系统卡，只有博文与网页版模型卡。
- 泛化论证是 Meta 的官方解释，分布外任务集未公开，未经独立复现；对比曲线只见于图中，具体读数不写入本篇。
- 评测分数由 Meta 汇总，含大量内部基准与混合来源；竞品的内部运行按模型卡所说是尽力而为。
- 模型卡第 6 节列出的已知局限：可能产生不准确、有偏或令人反感的回答；在训练数据覆盖不足的新场景中多步推理仍会出错；视觉与空间推理（尤其 3D 任务）是已知短板；并非所有预训练语言都做过评测；表现随量化、服务配置、提示、工具与智能体 harness 而变；不面向 18 岁以下用户。
- 参数量、架构、训练算力与数据均未披露。
- 模型卡前后口径不一：第 3 节写拒答计零分；第 4 节 CBRN 能力表注写「Refusals dropped prior to scoring」。

## 十、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[开源与闭源前沿模型谱系]] | 本篇是 Meta 在闭源一侧的节点，可与那篇的 Meta 开放权重节点对照阅读 | 各家谱系全表 |
| [[GPT6Astra系统卡深读]] | GPT-6 Astra 是本篇模型卡的对比对象之一，其判定与评测在那篇 | Astra 的字段 |
| [[ClaudeFable与Mythos51]] | Claude Fable 5.1 是本篇模型卡的对比对象之一，其系统卡字段在那篇 | Fable 的字段 |
| [[ClaudeOpus55系统卡短报]] | Claude Opus 5.5 是本篇模型卡的对比对象之一，其系统卡字段在那篇 | Opus 5.5 的字段 |
| [[SystemCard谱系时间线]] | 本篇提供「网页模型卡、完整安全报告后发」这一披露形态，可与那篇的各厂系统卡序列对照 | 各厂系统卡全表 |
| [[MuseSparkOpen模型卡深读]] | 同一模型家族的开放权重一侧：两篇可对照阅读 Meta 在闭源与开放权重两种发布形态下的模型卡写法与风险判定 | Muse Spark Open 的规格、评测方法与许可证 |

## 十一、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Muse Wonder 博文](https://research.meta.ai/blog/muse-wonder) | Active Memory、Active Focus 与泛化对比图 |
| 2 | [Muse Wonder Model Card](https://research.meta.ai/static/muse-wonder-model-card) 第 3 节 | 评测方法与逐项来源 |
| 3 | 同卡第 4、6 节 | 风险判定、ExploitGym 计分注释、已知局限 |
