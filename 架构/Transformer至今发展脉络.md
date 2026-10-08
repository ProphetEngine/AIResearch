---
title: 时间线 · Transformer 至今
topic: Transformer至今发展脉络
date: 2026-10-08
type: timeline
status: active
---

# 时间线 · Transformer 至今

> 本时间线梳理从 2017 年 Transformer 到 2026 年 10 月的主叙事，是本库「史与势」的总入口。细部节点请转入各主题 MOC 与专题时间线；旗舰型号与 System Card 见 [[MOC_模型与技术报告]]。日期口径：论文取 arXiv 首版（v1）日期，官方发布按 UTC 日期，系统卡取封面日期。

## 主叙事（简史）

2017 年，Google 团队提出「只用注意力、去掉循环与卷积」的 Transformer（《Attention Is All You Need》）。序列建模从逐步递推变为高度可并行的自注意力计算，训练吞吐与长程依赖建模同时上台阶，成为此后几乎一切大模型的骨架。

随后路线迅速收敛到 **Decoder-only / 因果语言模型**：GPT 系列把「大规模无监督预训练 + 少量示例即可适应新任务」推到台前。Encoder 路线在理解类任务上仍有价值，但生成式助手、对话与工具调用的主流产品形态由 Decoder-only 占据。

约 2020–2022 年，**规模定律**把「算力—参数—数据」从经验变为可规划的预算问题；数据质量、清洗、多语与代码占比、packing 与长上下文续训，逐渐与「单纯堆参数」同等重要。预训练范式演进为「预训练 → 指令微调 → 偏好/强化学习对齐」的流水线。

架构侧，**稀疏激活（MoE）** 成为「总参数很大、每次只激活一部分」的主路径之一。**长上下文**沿位置编码/注意力变体与系统侧（KV cache、分页注意力、serving）两条线推进。**多模态**从 CLIP 对比对齐，经 Flamingo 与视觉指令微调，走到原生多模态与「看图/听音/看视频再推理」的产品默认能力。

对齐方面，InstructGPT 将 RLHF 做成可复现流水线；Constitutional AI / RLAIF 与 DPO 等偏好优化拓展了后训练工具箱。2024 年秋季起，**推理时计算（test-time scaling）** 成为新主叙事：训练期 RL + 更长思维链 + 推理期算力，换取数学、代码与科学题上的跃迁。

到 2026 年中，闭源与开放权重谱系在统一「快答 + 深度思考 + 路由」、原生多模态、长上下文与 MoE/推理蒸馏上竞赛；**AI Infra**（三维并行、低精度训练、serving、量化与硬件协同）已成为战略变量。2025 年 10 月至 2026 年 10 月的关键节点见下节「近一年节点」。

对本库的读法建议：先沿本页把握总轴，再按主题 MOC 与专题时间线深入，避免只见单篇论文而失去时间轴。

## 近一年节点（2025-10 — 2026-10）

这一年有四条主线。第一，注意力层大规模改成线性注意力、稀疏注意力或压缩注意力与全注意力的混合，百万 token 上下文进入旗舰标配。第二，开放权重旗舰的总参推到 1T 至 3T 级，并公开越来越完整的训练配方。第三，闭源旗舰按能力和访问对象分档发布，安全护栏从拒答外移到分类器、受信访问和分阶段放量。第四，后训练普遍用同策略蒸馏把多个专家模型合成一个。

- **2025-10** · Meta 等系统比较注意力与 Mamba 的层间、层内混合方式，同月 Kimi Linear 以线性注意力与 MLA 按 3:1 混合，官方称首次在公平对比下超过全注意力。混合架构从个案变成可以按配方设计的方案（[arXiv:2510.04800](https://arxiv.org/abs/2510.04800)；[arXiv:2510.26692](https://arxiv.org/abs/2510.26692)） · [[混合Mamba与注意力架构设计菜谱]] · [[长上下文与注意力效率时间线]]
- **2025-10** · 中期训练综述把数据退火、学习率调度和长上下文扩展归为预训练与后训练之间的独立阶段，「预训练 → 后训练」的两段式流水线细化为三段（[arXiv:2510.06826](https://arxiv.org/abs/2510.06826)） · [[中期训练MidTraining范式]]
- **2025-11** · Gemini 3 Pro（11-18）与 Claude Opus 4.5（11-24）相继发布：前者是原生多模态的稀疏 MoE 推理旗舰，提供可选的 Deep Think 模式；后者突出软件工程与工具、电脑使用。闭源旗舰的竞争焦点转到智能体式任务（[Google 博文](https://blog.google/products/gemini/gemini-3/)；[Anthropic 公告](https://www.anthropic.com/news/claude-opus-4-5)） · [[Gemini3Pro模型卡深读]] · [[ClaudeOpus45系统卡深读]]
- **2025-12** · DeepSeek-V3.2（12-02）在 128K 的 V3.1-Terminus 上继续训练，架构上唯一的改动是细粒度稀疏注意力 DSA；Olmo 3（12-15）公开每个阶段的数据、中间检查点和代码。开放权重一侧同时推进可训练稀疏注意力与全栈开放（[arXiv:2512.02556](https://arxiv.org/abs/2512.02556)；[arXiv:2512.13961](https://arxiv.org/abs/2512.13961)） · [[DeepSeekV32技术报告深读]] · [[OLMo3全栈开放配方]]
- **2025-12** · GPT-5.2 系统卡（12-11）在 Instant / Thinking 双线命名下更新安全回归与前沿能力档位，生物风险仍按 High 预防性处理（[OpenAI 系统卡页](https://deploymentsafety.openai.com/gpt-5-2)） · [[GPT52SystemCard更新]]
- **2026-02** · Qwen3-Coder-Next 在可执行环境的反馈上扩展智能体式中期训练与强化学习，以 80B 总参、3B 激活的开放权重面向编码智能体与本地部署（[arXiv:2603.00729](https://arxiv.org/abs/2603.00729)） · [[Qwen3CoderNext技术报告深读]]
- **2026-04** · 同策略蒸馏综述（04-01）把「学生自己采样、教师在这些状态上给信号」整理成一个范式，此后它成为开放旗舰后训练的常用环节（[arXiv:2604.00626](https://arxiv.org/abs/2604.00626)） · [[OnPolicy蒸馏OPD范式]]
- **2026-04** · DeepSeek-V4 预览版（04-26）用 CSA 与 HCA 两种压缩注意力混合，原生支持 1M 上下文，V4-Pro 为 1.6T 总参、49B 激活。分块 KV 压缩进入旗舰架构（[arXiv:2606.19348](https://arxiv.org/abs/2606.19348)） · [[DeepSeekV4技术报告深读]]
- **2026-06** · Nemotron 3 Ultra（06-12）以 550B 总参、55B 激活的 Mamba–注意力混合加 LatentMoE 做开放旗舰，后训练用两轮多教师同策略蒸馏（[arXiv:2606.15007](https://arxiv.org/abs/2606.15007)） · [[Nemotron3Ultra技术报告深读]]
- **2026-06** · GPT-5.6 预览版系统卡（06-26，正式版 07-09）中，Sol、Terra、Luna 三个型号在生物和网络安全上首次全部判为 High，安全措施从模型拒答外移到激活分类器、实时扫描和受信访问（[OpenAI 系统卡页](https://deploymentsafety.openai.com/gpt-5-6)） · [[GPT56系统卡深读]]
- **2026-07** · Gemma 4（arXiv 07-02）以 Apache 2.0 许可放出 E2B 至 31B 的稠密模型和 26B-A4B 的 MoE，并公开参数分项、注意力配方和 QAT、MTP 等效率组件（[arXiv:2607.02770](https://arxiv.org/abs/2607.02770)） · [[Gemma4技术报告深读]]
- **2026-07** · Claude Opus 5（07-24）发布；同月 Kimi K3（arXiv 07-27）以 2.78T 总参、104B 激活的原生多模态 MoE 公开全部权重，注意力采用 KDA 线性注意力混合。开放权重进入 3T 级（[Anthropic 公告](https://www.anthropic.com/news/claude-opus-5)；[arXiv:2607.24653](https://arxiv.org/abs/2607.24653)） · [[ClaudeOpus5系统卡深读]] · [[KimiK3技术报告]]
- **2026-08** · Qwen3.8-Next（08-31）把损失、下游表现、训推成本和训练稳定性当作同一个设计问题，用 Gated DeltaNet 混合与继续预训练期的 QSA 控制长文开销，原文称以约 1/9 的训练 FLOPs 逼近前代 397B-A17B 旗舰（[arXiv:2608.30320](https://arxiv.org/abs/2608.30320)） · [[Qwen38Next架构深读]]
- **2026-09** · Claude Fable 5.1 与 Mythos 5.1 系统卡（09-01）描述「同一套权重、两套护栏」：通用面走 Fable，受信面走 Mythos。GPT-6 Astra（09-03）成为 OpenAI 首个在 Preparedness 框架下达到网络安全 Critical 级并广泛部署的模型。前沿能力开始按访问对象分级开放（[Fable/Mythos 系统卡](https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20%26%20Claude%20Mythos%205.1%20System%20Card.pdf)；[OpenAI 系统卡页](https://deploymentsafety.openai.com/gpt-6-astra)） · [[ClaudeFable与Mythos51]] · [[GPT6Astra系统卡深读]]
- **2026-09** · DeepSeek-V4.1-Flash（arXiv 09-17）从零训练稀疏注意力并把主 KV 压到 FP4；Periodic Weak Spots（09-28）随即发现分块 KV 压缩会让检索准确率随相位周期起伏，DeepSeek-V4 base 在 128K 测试中最多相差 40.2 个百分点。KV 压缩的收益与盲点在同一个月被摆上台面（[arXiv:2609.19969](https://arxiv.org/abs/2609.19969)；[arXiv:2609.36322](https://arxiv.org/abs/2609.36322)） · [[DeepSeekV41Flash深读]] · [[分块KV压缩的相位敏感性]]
- **2026-09** · Claude 5.5 家族的 Opus 5.5（09-22）与 Sonnet 5.5（09-28）发布，网络安全护栏从 Opus 档下放到 Sonnet 档；GPT-6.1 Sol（09-29）以约 Astra 五分之一的 API 价格提供接近 Astra 的智能体能力；Gemini 4 Argon（官方博文 2026-09-30 UTC）没有独立模型卡，经 Fairwind Program 先向受信的网络防御方分阶段放量（[Anthropic Opus 5.5 页](https://www.anthropic.com/claude-opus-5-5)；[Anthropic Sonnet 5.5 页](https://www.anthropic.com/claude-sonnet-5-5)；[OpenAI 系统卡页](https://deploymentsafety.openai.com/gpt-6-1-sol)；[Google 博文](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)） · [[ClaudeOpus55系统卡短报]] · [[ClaudeSonnet55系统卡短报]] · [[GPT61Sol系统卡短报]] · [[Gemini4Argon短报]]
- **2026-10** · Mistral Large 4（10-06）以约 1T 总参（权重仓库标 1.05T）、52B 激活（不含嵌入层约 49B）的原生多模态 MoE 开放 API 预览，权重计划在受控红队后放出；GPT-6 Sol 与 Luna 十月版（10-07）进入 ChatGPT 对话，取代 GPT-5.6 对应型号；Claude Haiku 5.5（10-07）发布。新一代能力继续向日常与低价档位扩散（[Mistral 公告](https://mistral.ai/news/mistral-large-4/)；[OpenAI 系统卡页](https://deploymentsafety.openai.com/gpt-6-october)；[Anthropic Haiku 5.5 页](https://www.anthropic.com/claude-haiku-5-5)） · [[MistralLarge4短报]] · [[GPT6SolLuna十月版系统卡短报]] · [[ClaudeHaiku55系统卡短报]]

## 枢纽节点（通史级）

| 主题 | 通史 / 总览入口 |
| --- | --- |
| Attention / Transformer | [[注意力与Transformer核心思想]] |
| Decoder-only / GPT | [[DecoderOnly与GPT路线]] |
| 规模定律与预训练 | [[规模定律与预训练范式]] |
| MoE / 稀疏激活 | [[混合专家架构]] |
| 长上下文 | [[长上下文位置编码与系统侧]] · 专题 [[长上下文与注意力效率时间线]] |
| 多模态 | [[多模态架构脉络]] · 专题 [[多模态与世界模型发展时间线]] |
| 对齐 | [[对齐脉络RLHF与偏好优化]] · 专题 [[对齐与强化学习发展时间线]] |
| Test-time scaling | [[推理时扩展TestTimeScaling]] |
| 前沿谱系 | [[开源与闭源前沿模型谱系]] · [[SystemCard谱系时间线]] |
| AI Infra | [[AI基础设施总览]] · [[InfraServing发展时间线]] |
| 智能体 | [[智能体工具与长程任务]] · [[智能体工具记忆发展时间线]] |
| RAG | [[检索增强与知识外挂]] · [[RAG发展时间线]] |

## 专题时间线

- [[预训练与架构发展时间线]]
- [[长上下文与注意力效率时间线]]
- [[多模态与世界模型发展时间线]]
- [[智能体工具记忆发展时间线]]
- [[对齐与强化学习发展时间线]]
- [[安全治理评测发展时间线]]
- [[RAG发展时间线]]
- [[InfraServing发展时间线]]
- [[投机解码原理与发展脉络]]（第二节为投机解码脉络表）
- [[SystemCard谱系时间线]]

## 相关

- [[MOC_阅读入口]]：完整十一簇主题图谱，按主题而非时间进入全库。
- [[MOC_发展时间线]]：串联本页与各专题时间线的史线入口。

## 局限与待核实

- arXiv 编号月份与首版日期不一致、按首版记的条目：Qwen3-Coder-Next（编号 2603，首版 2026-02-28）、DeepSeek-V4（编号 2606，首版与 PDF 页眉均为 2026-04-26）。
- Gemma 4 报告页眉日期为 2026-06-19，按 arXiv 首版记为 2026-07；Kimi K3 的官方博文早于 arXiv 首版，两者同在 2026-07。
