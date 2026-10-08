---
date: 2026-10-08
status: archived
archived: 2026-10-08
topic: MistralLarge4短报
title: "Mistral Large 4（前沿短报）"
lines: [开源权重, 网安取舍, 异步RL]
sources:
 - https://mistral.ai/news/mistral-large-4/
 - https://docs.mistral.ai/models/mistral-large-4-0
 - https://huggingface.co/mistralai/Mistral-Large-4.0-1T05-A52B
 - https://thenextweb.com/news/mistral-releases-large-4-a-1-trillion-parameter-open-weight-ai-model
related: ["Gemini4Argon短报", "ClaudeOpus55系统卡短报", "GPT6Astra系统卡深读", "AgenticRL景观与能力模块", "MiMoV26智能体强化学习短报", "开源与闭源前沿模型谱系", "Mistral3公告短卡"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# Mistral Large 4（前沿短报）

> **主要来源**：[Introducing Mistral Large 4](https://mistral.ai/news/mistral-large-4/)；[Mistral Large 4 模型文档](https://docs.mistral.ai/models/mistral-large-4-0)；[Mistral-Large-4.0-1T05-A52B](https://huggingface.co/mistralai/Mistral-Large-4.0-1T05-A52B)（截至 2026-10-08）。下文「博文」指 Mistral 发布博文，「文档」指模型文档，「HF 页」指 Hugging Face 预告页。
> **研究线**：前沿模型 · 开源权重 · 网络安全能力与拒答的取舍
> **范围与相邻笔记**：
> - ≠ [[Gemini4Argon短报]]：两者只对照发布路径，不复述 Argon 的能力与 Fairwind 细则。
> - ≠ [[ClaudeOpus55系统卡短报]]、[[GPT6Astra系统卡深读]]：本篇只借用两家的护栏叙事作对照，不复述其系统卡。
> - ≠ [[AgenticRL景观与能力模块]]、[[MiMoV26智能体强化学习短报]]：ML4 只作为异步 RL 基础设施的工业实例，方法论见这两篇。
> - ≠ [[开源与闭源前沿模型谱系]]、[[Mistral3公告短卡]]：本篇不复述开源权重谱系与 Large 3 公告。
> - 本篇不是系统卡短报：ML4 目前没有技术报告，也没有 System Card。
> **意义**：ML4 是欧洲厂商推出的约 1T 总参开源权重模型（权重尚待开放），走「API 预览、放权重前受控红队、月底开放权重」的路径；它把网安能力当作卖点，并批评服务商层面的拒答，与闭源厂商以护栏和受信访问管控网安能力的路线形成对照。

**一句话**：Mistral 于 2026-10-06 以 API 公开预览形式发布 Mistral Large 4（ML4，昵称 Le Chonk），约 1T 总参、52B 激活的原生多模态 MoE；官方称它明显领先美国与欧洲开发的开源权重模型，在 AA Cyber Index 上位列全球前五，权重定于本月底开放。

## 一、背景与发布形态

Mistral 的上一代旗舰 Large 3 于 2025-12-02 发布，为 41B 激活、675B 总参的稀疏 MoE，公告称采用 Apache 2.0（见 [[Mistral3公告短卡]]）。ML4 把总参推到约 1T，发布方式是先开放 API 预览、月底再放权重。

- **当前形态**：API 公开预览，可在 Mistral Studio 试用；文档标 Public Preview · Open · v26.10，发布日期未标具体时刻（博文页头、「Le Chonk」节；文档）。
- **许可**：文档只标「Open」，未给出具体许可条款（文档）。
- **技术文档**：无技术报告、无 System Card；官方称将在放权重时公布架构细节、更多基准和后训练方法（博文「Try it today」「What comes next」节）。

## 二、规格与价格

- **参数**：博文写 1T 总参、52B 激活；文档写 1.05T 总参、52B 激活，与 HF 仓库名中的「1T05」一致；HF 页称每 token 激活 49B，计入 embedding 和输出层为 52B。
- **结构与上下文**：文档称细粒度（granular）MoE、多模态，视觉编码器 1.6B，上下文 1M；1M 上下文与视觉编码器规模只见于文档。
- **价格**（美元 / 百万 token，文档）：输入 $1.36、缓存输入 $0.14、输出 $4.18；限时价为其一半（$0.68 / $0.07 / $2.09），文档没写限时价的截止日期。

## 三、发布路径与权重日期

- **受控红队**：官方称权重开放前先开放 API 预览，同时与 "cybersecurity leaders, vetted partners, and state authorities" 在真实场景中红队测试；这些机构使用同一模型，审核降低（reduced moderation），网安能力扩展（博文「Frontier performance」节）。
- **权重日期三说并存**：博文写 "Weights drop end of this month"，未给具体日期；HF 页写 October 31, 2026（标「Current ETA」，仍可能调整）；The Next Web（2026-10-06）写 October 27。本篇不作判断。
- **与 Argon 对照**：Argon 经 Fairwind 计划向受信网络防御方分阶段放量、模型保持闭源（见 [[Gemini4Argon短报]]）；ML4 先预览、再受控红队，最终公开权重。

## 四、网络安全

- **AA Cyber Index**：在全部模型中排名前五，官方称在中国以外开发的开源权重模型中 "by a wide margin" 领先；博文只给排名，未以文字给出总分（博文「Cybersecurity」节）。
- **单项与竞赛**：指数中「复现开源软件真实漏洞并打补丁」一项得 82%，官方称为所有模型中最高；Cybench（40 道安全竞赛题）为 93%（同节）。官方称 Claude Opus 5.5、GPT-6 Astra 等闭源模型在该单项上接近 0 分，原因是拒绝执行任务；这是 Mistral 的说法，本篇未独立核实。
- **用途与拒答**：官方称内部测试中 ML4 可用于恶意软件分析、漏洞优先级排序和检测规则编写（同节）；同时称其对网安类恶意请求的拒答率高于所有开源模型，口径为 JailbreakBench、StrongREJECT、AgentHarm 中网安提示的平均拒答率（博文「Model Safety」节）。

## 五、代表能力

| 评测 | ML4 | 官方给出的对照 |
|---|---|---|
| DeepSWE v1.1 | 61.7% | — |
| SWE-Atlas-QnA | 59.4% | — |
| Terminal-Bench 4 | 28.3% | — |
| Coding Agent Index（综合） | 49.8% | 领先 DeepSeek V4 Pro 0813 与 Qwen3.8 Max |
| AutomationBench（657 个业务工作流） | 59.9% | 领先 Kimi K3、MiMo-V2.6-Pro、DeepSeek V4 Pro |
| AA-Briefcase（长程知识工作） | 1393 Elo | 领先 DeepSeek V4 Pro |
| Dense 200（视觉定位） | 42% | GPT-6 Astra 41% |

编码类数字出自博文「Agentic coding」节，工作流两项出自「Agentic Workflows」节，Dense 200 出自「Multimodal」节；编码类评测均未公布 harness，对比模型由官方选定。官方另称，在 Surge AI 的编码质量盲评中 ML4 Preview 在五个模型里排第二（3.74，满分 5），仅次于 Claude Opus 5（4.22）。

## 六、安全评测（博文「Model Safety」节）

- Lakera B3 AI Security Benchmark：抵抗 93.3% 的攻击，官方称未见竞品更高。
- KORA Benchmark：1.691（满分 2，对应「Exemplary」），官方称为其测得的开源模型最高分。
- 间接提示注入：官方称已使内部基准饱和。

## 七、训练与 RL 基础设施

- **预训练**：官方称在 Mistral 自有的欧洲数据中心用 3,800 张 NVIDIA Grace Blackwell GPU 从零训练，公开预览也部署在同一设施；训练数据覆盖 160 余种语言，包括欧盟全部官方语言（博文「Forged in Europe. Built for AI sovereignty.」节）。
- **异步 RL**（博文「Reinforcement learning at scale」节，只公开到工程层面）：统一的可组合环境接口，单次训练可混合单轮对话、科学问题求解、安全对齐、事实性和长程工具使用；验证端按任务组合奖励模型、单元测试、LLM 评审和静态检查。自动扩缩的 actor 集群并行生成数万条 rollout、训练异步进行，支持跨多次压缩（compaction）、预算达数百万 token 的长轨迹，同时控制陈旧度（staleness）。
- **规模**：当前约 3k GPU，单次训练每天约产出 330 亿 token，经过滤和掩码后约 160 亿为可训练的补全 token；官方称用新方法减小 off-policy 偏移，但未披露算法。
- **状态**：官方称支撑本次预览的 RL 训练仍在进行，未见饱和迹象（博文「What comes next」节）。

## 八、史与势

- **开源权重前沿**：官方措辞以「美国或欧洲开发」「中国以外」为限，对全球最强开源模型只称 "competitive"（博文「Frontier performance」「Cybersecurity」节）。开源与闭源前沿的整体谱系见 [[开源与闭源前沿模型谱系]]。
- **网安能力与拒答的取舍**：闭源系统卡以护栏、分类器和受信访问管控网安能力（见 [[ClaudeOpus55系统卡短报]]、[[GPT6Astra系统卡深读]]）。Mistral 则称服务商层面的拒答可能阻碍合法的漏洞研究与事件响应，主张让组织 "under their own policies" 运行网安工作（博文「Forged in Europe. Built for AI sovereignty.」节），同时称其对恶意网安提示的拒答率高于开源同类。
- **欧洲主权算力**：官方称提供由 Mistral 端到端运营、"independently of other digital service providers and under European law" 的欧洲部署（博文「Forged in Europe. Built for AI sovereignty.」节），算力仍在扩建（博文「What comes next」节）。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[Mistral3公告短卡]] | 前代：Large 3 的发布日、规模与许可 | Large 3 与 Ministral 3 公告本身 |
| [[开源与闭源前沿模型谱系]] | 所在谱系：开源权重与闭源前沿的整体格局 | 谱系各代模型 |
| [[Gemini4Argon短报]] | 发布路径对照：闭源分阶段放量与开源放权重 | Argon 的能力与 Fairwind 细则 |
| [[ClaudeOpus55系统卡短报]] | 网安治理对照：闭源厂商以护栏与受信访问管控网安能力 | Opus 5.5 系统卡内容 |
| [[GPT6Astra系统卡深读]] | 网安治理对照：同上，OpenAI 一侧 | Astra 系统卡内容 |
| [[AgenticRL景观与能力模块]] | 方法背景：异步 RL 所在的 Agentic RL 研究线 | Agentic RL 能力模块地图 |
| [[MiMoV26智能体强化学习短报]] | 同期工业实例：另一份公开到工程层面的大规模异步 RL 配方 | MiMo-V2.6 的 batch、grader 与 harness 设计 |

## 十、局限与待核实

1. **没有技术报告和系统卡**：架构、更多基准和后训练方法要等权重开放时公布；本篇不作架构推测。
2. **权重日期和许可证未定**：博文写「月底」，HF 页写 10-31（Current ETA），媒体写 10-27；文档许可证只标「Open」，具体条款未公布。
3. **预览期数字**：官方称 RL 训练仍在进行、未见饱和，并预期未来数周至数月有较大提升；现有分数是阶段性结果。
4. **自选对比与 harness**：对比模型由官方选定，编码类评测未公布 harness，不能与其他笔记的分数横比。例如 Gemini 4 Argon 的 DeepSWE v1.1 77.9% 基于 mini-swe harness，与本篇的 61.7% 口径不同。
5. **官方说法未独立核实**：闭源模型「因拒答而近 0」的归因、拒答率「高于所有开源模型」、B3「未见更高」都是官方说法，测试设置未完整公开；82% 是 AA Cyber Index 中一项测试的得分，不是指数总分。
6. **口径并存**：总参 1T / 1.05T、激活 49B / 52B 并存；1M 上下文只见于文档。
7. **媒体与博文不一致**：The Next Web 写约 4,000 张 GPU、Dense 200 两者都是 42%，与博文的 3,800 张、42% 对 41% 不同；本篇以博文为准。

## 十一、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 博文 | Introducing Mistral Large 4 | Mistral，2026-10-06，未标具体时刻 | https://mistral.ai/news/mistral-large-4/ |
| 文档 | Mistral Large 4 模型文档 | Mistral Docs，Public Preview · Open · v26.10 | https://docs.mistral.ai/models/mistral-large-4-0 |
| HF 预告页 | Mistral-Large-4.0-1T05-A52B | Hugging Face，Upcoming；Current ETA October 31, 2026 | https://huggingface.co/mistralai/Mistral-Large-4.0-1T05-A52B |
| 媒体报道 | Europe's Mistral launches Large 4 | The Next Web，2026-10-06；权重日期等媒体说法 | https://thenextweb.com/news/mistral-releases-large-4-a-1-trillion-parameter-open-weight-ai-model |
