---
title: 时间线 · 旗舰 System Card / TR
topic: SystemCard谱系时间线
date: 2026-10-08
type: timeline
status: active
---

# 时间线 · 旗舰 System Card / TR

> 本时间线按厂商梳理旗舰模型的系统卡（System Card）、模型卡与技术报告。2025 年以来，闭源旗舰公开文档的重心从能力榜单转向风险判定与部署护栏：OpenAI 的 Preparedness 档位从生物化学域的「预防性 High」一路上调到网络安全域的「Critical」；Anthropic 从以 ASL 部署级为核心，转向按 CB 等能力阈值判定，并为分类器护栏配上回退模型（fallback）；Google 则以精简模型卡和受信放量计划取代长篇技术报告。开放权重一侧，技术报告持续公开架构与训练配方，近一年的重心转向长上下文效率与强化学习算力。通史见 [[开源与闭源前沿模型谱系]]，文档字段规范见 [[模型卡与SystemCard规范]]；完整挂载见 [[MOC_模型与技术报告]]，前沿短报见 [[MOC_前沿]]。日期口径：论文取 arXiv 首版（v1）日期，官方发布按 UTC 日期，系统卡取封面日期。

## 背景与规范

- **2018-10** · Model Cards 提出为每个模型附上标准化报告（预期用途、分组评测、局限），是后来模型卡与系统卡的字段源头（[arXiv:1810.03993](https://arxiv.org/abs/1810.03993)） · [[模型卡与SystemCard规范]]
- [[开源与闭源前沿模型谱系]] 给出开源与闭源旗舰的通史坐标；本时间线只排各家文档节点，不重复谱系叙事。

## Anthropic：从 ASL 部署级到分档护栏与回退

Anthropic 依据负责任扩展政策（RSP）发布系统卡。2025 年的卡以 ASL-3 部署级为核心结论；2026 年起，护栏按能力分档，分类器拦截时把请求转给上一代模型，部署形态本身成为系统卡的主要内容。

- **2025-08** · Claude Opus 4.1 系统卡附录：增量发布只做精简安全评测以衔接 RSP，几乎不报能力榜，形成「主卡 + 附录」的分层写法（[发布公告](https://www.anthropic.com/news/claude-opus-4-1)） · [[ClaudeOpus41系统卡附录深读]]
- **2025-11** · Claude Opus 4.5 系统卡：把智能体能力榜与安全、对齐、RSP 评测合为一卷，在 ASL-3 下部署，并坦言排除 AI R&D-4 与 CBRN-4 风险已越来越难（[发布公告](https://www.anthropic.com/news/claude-opus-4-5)） · [[ClaudeOpus45系统卡深读]]
- **2026-07** · Claude Opus 5 系统卡：仍在 ASL-3 下发布，核心增量是「激活探针 → LLM 分类器」的分级网安护栏，放开源码漏洞发现、继续拦截二进制漏洞相关请求（[发布公告](https://www.anthropic.com/news/claude-opus-5)） · [[ClaudeOpus5系统卡深读]]
- **2026-09** · Claude Fable 5.1 与 Mythos 5.1 合卡：同一套权重配两套护栏，通用面（Fable）在分类器触发时回退到 Opus 4.8，受信面（Mythos）通过验证计划向受信用户开放更多生命科学与网安能力（[发布页](https://www.anthropic.com/claude-fable-and-mythos-5-1)） · [[ClaudeFable与Mythos51]]
- **2026-09** · Claude Opus 5.5 系统卡：5.5 族首发，多项评测追平或超过 Mythos 5.1；卡内基本不再使用 ASL 标签，风险按 CB-1 等阈值判定，生物分类器命中时回退到 Opus 5（[发布页](https://www.anthropic.com/claude-opus-5-5)） · [[ClaudeOpus55系统卡短报]]
- **2026-09** · Claude Sonnet 5.5 系统卡：同价同规格下能力接近 Opus 5.5，因此成为首个带网安护栏（拦截后转交 Sonnet 5）和防推理内容提取分类器（拦截后无回退）的 Sonnet（[发布页](https://www.anthropic.com/claude-sonnet-5-5)） · [[ClaudeSonnet55系统卡短报]]
- **2026-10** · Claude Haiku 5.5 系统卡：5.5 族最低档，RSP 结论沿用既有判定，网安护栏按能力明显收窄，且所有分类器拦截后都不再回退到其他模型（[发布页](https://www.anthropic.com/claude-haiku-5-5)） · [[ClaudeHaiku55系统卡短报]]

## OpenAI：Preparedness 档位逐级上调

OpenAI 依 Preparedness Framework 对生物化学、网络安全、AI 自我改进三类风险分档（High / Critical），并以主卡、附录（addendum）与更新卡跟进迭代型号。2026 年起，防护重心从模型拒答外移到分类器、监控与受信访问。

- **2025-08** · gpt-oss 模型卡：OpenAI 自 GPT-2 以来首个正式开放权重的语言模型，Apache 2.0 许可的 MoE 推理模型，推理强度可调（[arXiv:2508.10925](https://arxiv.org/abs/2508.10925)） · [[GPToss模型卡深读]]
- **2025-08** · GPT-5 系统卡：面向「统一系统 + 路由」的产品形态，把 gpt-5-thinking 在生物化学域按 High 能力预防性处理并启用配套防护（[系统卡页](https://openai.com/index/gpt-5-system-card/)） · [[GPT5系统卡深读]]
- **2025-11** · GPT-5.1 系统卡附录：5 页增补，只报安全评测，不给能力分与架构信息（[Hub](https://deploymentsafety.openai.com/gpt-5-1)） · [[GPT5系统卡深读]] 第四节
- **2025-12** · GPT-5.2 更新卡：以差分表记录 GPT-5 → 5.1 → 5.2 的安全变化，生物化学仍预防性判为 High，网安与自我改进仍未达 High（[Hub](https://deploymentsafety.openai.com/gpt-5-2)） · [[GPT52SystemCard更新]]
- **2026-06** · GPT-5.6 预览版系统卡：Sol、Terra、Luna 三型号家族在生物化学与网安两域首次全员判为 High，连较小较快的型号也不例外（[Hub](https://deploymentsafety.openai.com/gpt-5-6-preview)） · [[GPT56系统卡深读]]
- **2026-07** · GPT-5.6 正式版系统卡：安全叙事从模型拒答外移到激活分类器、实时扫描、账户级处置与受信访问（Trusted Access），后续更新又补入 GPT-Red 自动红队的提示注入结果（[Hub](https://deploymentsafety.openai.com/gpt-5-6)） · [[GPT56系统卡深读]]
- **2026-09** · GPT-6 Astra 系统卡：OpenAI 首个在 Preparedness 下判为网安 Critical 并广泛部署的模型；思维链可监控性下降，监控转向全轨迹、激活与动作层面（[Hub](https://deploymentsafety.openai.com/gpt-6-astra)） · [[GPT6Astra系统卡深读]]
- **2026-09** · GPT-6.1 Sol 附录（挂在 Astra 卡下）：以约 Astra 五分之一的 API 价格提供接近的能力，判定网安 Critical、生物化学 High，沿用 Astra 的防护栈（[Hub](https://deploymentsafety.openai.com/gpt-6-1-sol)） · [[GPT61Sol系统卡短报]]
- **2026-10** · GPT-6 Sol 与 Luna 十月版：同一型号开始按月份出版本，十月版进入 ChatGPT 对话、取代 GPT-5.6 对应型号，Preparedness 判定与之一致，系统卡只报安全内容（[Hub](https://deploymentsafety.openai.com/gpt-6-october)） · [[GPT6SolLuna十月版系统卡短报]]

## Google：从长篇技术报告到精简模型卡与受信放量

Google 的闭源 Gemini 线从 2.5 代的长篇技术报告，转为 10 页左右的模型卡，再到旗舰只配评测文件；风险结论统一以前沿安全框架（FSF）的关键能力水平（CCL）表述。开放权重的 Gemma 线单独出技术报告。

- **2025-07** · Gemini 2.5 技术报告（arXiv 首版）：73 页，公开推理、长上下文与智能体能力，安全章只给「未达 CCL」的结论（[arXiv:2507.06261](https://arxiv.org/abs/2507.06261)） · [[Gemini25技术报告深读]]
- **2025-11** · Gemini 3 Pro 模型卡：10 页产品与安全卡，公开稀疏 MoE 加原生多模态的骨架和 FSF 各域「未达 CCL」，不给参数量与训练规模（[发布博文](https://blog.google/products-and-platforms/products/gemini/gemini-3/)） · [[Gemini3Pro模型卡深读]]
- **2026-07** · Gemma 4 技术报告：开放权重族的架构、效率与量化字段，与闭源 Gemini 卡分线公开（[arXiv:2607.02770](https://arxiv.org/abs/2607.02770)） · [[Gemma4技术报告深读]]
- **2026-08** · Gemini 3.7 Flash 模型卡：9 页增量卡，多数字段指向 3.6 Flash 卡；FSF 升级到 2026 年 4 月版，并引入 TCL 与生化、网安「预警」（alert）表述（[模型卡页](https://deepmind.google/models/model-cards/gemini-3-7-flash/)） · [[Gemini37Flash模型卡深读]]
- **2026-09** · Gemini 3.8 Flash：基于 3.7 Flash 的 Gemini 3 族迭代，六周内第三个 Flash 版本；同时发布的 3.8 Flash Cyber 变体只经 Fairwind 计划向受信防御方开放（[官方博文](https://blog.google/innovation-and-ai/models-and-research/gemini-models/3-8-flash-and-3-8-flash-cyber/)、[模型卡](https://deepmind.google/models/model-cards/gemini-3-8-flash/)）
- **2026-09** · Gemini 4 Argon：没有独立的模型卡或系统卡，只配 5 页评测文件，经 Fairwind 计划先向受信网络防御方分阶段放量（[官方博文](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)） · [[Gemini4Argon短报]]

## xAI

- **2025-08** · Grok 4 模型卡：8 页、几乎全是安全评测，以风险管理框架（RMF）三分法加系统提示、输入过滤作为主要缓解，并自报生物双用途知识超过人类专家水平（[模型卡](https://data.x.ai/2025-08-20-grok-4-model-card.pdf)） · [[Grok4模型卡深读]]

## Meta

- **2025-04** · Llama 4 只以博文发布，没有 Llama 1–3 那样的论文式技术报告，也没有独立 PDF 模型卡，开放权重旗舰的文档披露明显收缩（[官方博文](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)） · [[LLaMA开源生态里程碑]]

## Mistral

- **2025-12** · Mistral 3 发布边缘端 Ministral 3 与旗舰 Mistral Large 3，全系 Apache 2.0；配套论文只覆盖 Ministral 3（arXiv 首版 2026-01）（[官方博文](https://mistral.ai/news/mistral-3/)） · [[MistralLarge4短报]]
- **2026-10** · Mistral Large 4：约 1T 总参（权重仓库标 1.05T）、52B 激活的原生多模态 MoE，以 API 公开预览发布，没有技术报告与系统卡，开放权重前先与网安机构做受控红队（[官方博文](https://mistral.ai/news/mistral-large-4/)） · [[MistralLarge4短报]]

## DeepSeek

DeepSeek 的技术报告是开放权重一侧披露最详尽的系列，主线从 MoE 训练基建，经推理强化学习，走到稀疏注意力与长上下文的 KV 压缩。

- **2024-12** · DeepSeek-V3：671B 总参 / 37B 激活的 MoE，公开 FP8 训练、DualPipe 与无辅助损失负载均衡等完整配方（[arXiv:2412.19437](https://arxiv.org/abs/2412.19437)） · [[DeepSeekV3训练与MoE基建]]
- **2025-01** · DeepSeek-R1：公开以 GRPO 加规则奖励训练推理模型的各个阶段，R1-Zero 展示纯强化学习可涌现长链推理（[arXiv:2501.12948](https://arxiv.org/abs/2501.12948)） · [[DeepSeekR1推理训练深读]]
- **2025-12** · DeepSeek-V3.2：架构上唯一的改动是 DeepSeek 稀疏注意力（DSA），再以加码的 GRPO 混合强化学习与大规模合成智能体任务，把推理与工具使用合到一条线上（[arXiv:2512.02556](https://arxiv.org/abs/2512.02556)） · [[DeepSeekV32技术报告深读]]
- **2026-04** · DeepSeek-V4 系列预览报告：V4-Pro（1.6T / 49B 激活）与 V4-Flash（284B / 13B 激活），原生 1M 上下文，以 CSA + HCA 混合注意力压低长文本的计算与 KV 开销（[arXiv:2606.19348](https://arxiv.org/abs/2606.19348)） · [[DeepSeekV4技术报告深读]]
- **2026-09** · DeepSeek-V4.1-Flash：把长程智能体的瓶颈从算力转到 KV 存储，以 CSA2 与 FP4 KV 把常驻显存的全局 KV 压到 V4-Flash 的约四分之一（[arXiv:2609.19969](https://arxiv.org/abs/2609.19969)） · [[DeepSeekV41Flash深读]]

## Qwen

- **2025-05** · Qwen3：把思考与非思考两种模式统一进同一模型，并用思考预算（thinking budget）调节推理算力（[arXiv:2505.09388](https://arxiv.org/abs/2505.09388)） · [[Qwen3技术报告深读]]
- **2026-02** · Qwen3-Coder-Next：在可执行环境反馈上扩展智能体中期训练与强化学习，产出 80B 总参 / 3B 激活的代码专用开放权重模型（[arXiv:2603.00729](https://arxiv.org/abs/2603.00729)） · [[Qwen3CoderNext技术报告深读]]
- **2026-08** · Qwen3.8-Next 架构报告：以门控 DeltaNet 线性注意力混合等设计，用约三分之一的激活参数与约九分之一的训练算力逼近前代 397B-A17B 旗舰（[arXiv:2608.30320](https://arxiv.org/abs/2608.30320)） · [[Qwen38Next架构深读]]

## Moonshot（Kimi）

- **2025-01** · Kimi k1.5：与 DeepSeek-R1 同月公开长上下文强化学习框架，包括部分 rollout 与长度惩罚等做法（[arXiv:2501.12599](https://arxiv.org/abs/2501.12599)） · [[Kimik15技术报告深读]]
- **2025-07** · Kimi K2：1T 总参 / 32B 激活的 MoE，以 MuonClip 优化器稳定 15.5T token 预训练，后训练侧重智能体数据合成与联合强化学习（[arXiv:2507.20534](https://arxiv.org/abs/2507.20534)） · [[KimiK2技术报告深读]]
- **2026-07** · Kimi K3：约 2.8T 总参 / 104B 激活的原生多模态 MoE，采用 KDA 与 MLA 混合注意力，在 1M 上下文上做智能体强化学习，全权重开放（[arXiv:2607.24653](https://arxiv.org/abs/2607.24653)） · [[KimiK3技术报告]]

## 其他开放权重报告

- **2025-06** · MiniMax-M1：混合 MoE 加 Lightning Attention，原生 1M 上下文，以 CISPO 算法在约三周内完成全量强化学习（[arXiv:2506.13585](https://arxiv.org/abs/2506.13585)） · [[MiniMaxM1技术报告深读]]
- **2025-08** · 智谱 GLM-4.5：GLM 系首个 MoE（355B / 32B 激活），先训推理、智能体、通用三类专家模型再统一自蒸馏，同一权重支持思考与非思考模式（[arXiv:2508.06471](https://arxiv.org/abs/2508.06471)） · [[GLM45技术报告深读]]
- **2025-12** · AI2 OLMo 3：走「全开放」路线，公开各阶段数据、中间检查点与代码，而不只是最终权重（[arXiv:2512.13961](https://arxiv.org/abs/2512.13961)） · [[OLMo3全栈开放配方]]
- **2026-06** · NVIDIA Nemotron 3 Ultra：混合 Mamba–Attention 加 LatentMoE，面向智能体推理公开预训练、后训练、量化与推理配方（[arXiv:2606.15007](https://arxiv.org/abs/2606.15007)） · [[Nemotron3Ultra技术报告深读]]
- **2026-08** · 蚂蚁 UI-Venus-2：覆盖移动、网页与桌面的 GUI 智能体基础模型，以轨迹级与样本级可验证信号支撑离线强化学习（[arXiv:2609.00028](https://arxiv.org/abs/2609.00028)） · [[UIVenus2GUI智能体]]
- **2026-08** · SK Telecom A.X K2：韩国主权 AI 背景下从零训练的 688B / 33B 激活 MoE，以较少但偏智能体与软件工程的数据全面超过前代（[arXiv:2608.30181](https://arxiv.org/abs/2608.30181)） · [[AXK2技术报告深读]]
- **2026-09** · 小米 MiMo-V2.6：报告主轴是放大强化学习算力（更大 batch、更多环境与 harness、更多评分器算力），并开源约 7k 个可验证环境（[官方发布页](https://mimo.mi.com/docs/en-US/news/latest/v2-6)） · [[MiMoV26智能体强化学习短报]]

## 相关

- [[安全治理评测发展时间线]]：系统卡中反复出现的宪法分类器、提示注入防御、scheming 与监控评测等方法，其来历在那里按时间展开。
- [[对齐与强化学习发展时间线]]：R1、k1.5、MiMo-V2.6 等报告所用的 GRPO、可验证奖励与 Agentic RL 方法线在那里展开。

## 局限与待核实

- 模型卡同系统卡取封面日期，无封面日期时取官方索引页日期；无报告的模型取官方发布页日期。
- Gemini 4 Argon 官方博文发布时间为 2026-09-30 20:00 UTC，折合上海时间为 2026-10-01，本时间线按页眉日期记作 2026-09。
- Gemini 2.5 技术报告按 arXiv 首版（2025-07-07）记，Google 官方首次发布报告的日期未单独核对，待核实。
- DeepSeek-V4（arXiv 2606.19348）首版为 2026-04-26，UI-Venus-2（arXiv 2609.00028）首版为 2026-08-27，编号月份与首版日期不一致，按 arXiv 首版日期记。
- GPT-5.6 预览版封面为 2026-06-25，Deployment Safety Hub 标注发布于 2026-06-26，两者同月，不影响排序。
- MiMo-V2.6 官方页标注「更新时间 2026-09-22」，具体发布日待核实，此处只记到月。
