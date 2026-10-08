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

> **主要来源**：[Introducing Mistral Large 4](https://mistral.ai/news/mistral-large-4/)；[Mistral Large 4 模型文档](https://docs.mistral.ai/models/mistral-large-4-0)；[Mistral-Large-4.0-1T05-A52B](https://huggingface.co/mistralai/Mistral-Large-4.0-1T05-A52B)（截至 2026-10-08）
> **研究线**：前沿模型 · 开源权重 · 网络安全能力与拒答的取舍
> **范围与相邻笔记**：
> - ≠ [[Gemini4Argon短报]]：两者只对照发布路径。Argon 走闭源、向受信方分阶段放量；ML4 走开源权重，放权重前先做受控红队。
> - ≠ [[ClaudeOpus55系统卡短报]]、[[GPT6Astra系统卡深读]]：本篇只在「史与势」中借用两家的护栏叙事作对照，不复述其系统卡。
> - ≠ [[AgenticRL景观与能力模块]]、[[MiMoV26智能体强化学习短报]]：ML4 只作为异步 RL 基础设施的工业实例挂链，方法论见这两篇。
> - ≠ [[开源与闭源前沿模型谱系]]、[[Mistral3公告短卡]]：本篇只在「史与势」中挂开源权重谱系与 Mistral 前代入口，不复述谱系与 Large 3 公告。
> - 本篇不是系统卡短报：ML4 目前没有技术报告，也没有 System Card。

## 一、发布与文档形态

Mistral 于 2026-10-06 以 API 公开预览形式发布 Mistral Large 4（ML4，昵称 Le Chonk）。它是约 1T 总参、52B 激活的原生多模态 MoE 模型。官方称其 "significantly outperforming any open-weight model developed in the US or Europe"（博文「Frontier performance」节），在 AA Cyber Index 上位列全球前五。权重定于本月底开放，此前先与网安机构、受审合作方和国家机构做降低审核的受控红队。

| 项目 | 内容 | 出处 |
|---|---|---|
| 发布日期 | 2026-10-06，未标具体时刻 | 博文页头；文档页头 |
| 当前形态 | API 公开预览，可在 Mistral Studio 试用 | 博文「Le Chonk」节；文档标 Public Preview |
| 文档标记 | Public Preview · Open · v26.10 | 文档 |
| 许可证 | 文档只标「Open」，未给出具体许可条款 | 文档 |
| 技术文档 | 无技术报告、无 System Card；官方称将在放权重时公布架构细节、更多基准和后训练方法 | 博文「Try it today」「What comes next」节 |

## 二、规格与价格

**参数与上下文**

| 项目 | 博文 | 文档 | HF 预告页 |
|---|---|---|---|
| 总参数 | 1T | 1.05T | 1T（仓库名含「1T05」） |
| 激活参数 | 52B | 52B | 每 token 49B；计入 embedding 和输出层为 52B |
| 架构表述 | 原生多模态 | 细粒度（granular）MoE，多模态 | 原生多模态 |
| 视觉编码器 | 未提 | 1.6B | 未提 |
| 上下文 | 未提 | 1M | 未提 |

三处口径能对上：52B 是计入 embedding 和输出层后的激活量，49B 是不计这两部分的每 token 激活量（HF 页）；HF 仓库名中的「1T05」与文档的 1.05T 一致。1M 上下文只见于文档。

**价格**（美元 / 百万 token，文档）

| 计价项 | 原价 | 限时价 |
|---|---|---|
| 输入 | $1.36 | $0.68 |
| 缓存输入 | $0.14 | $0.07 |
| 输出 | $4.18 | $2.09 |

文档没写限时价的截止日期。

## 三、发布路径与权重日期

官方称，权重开放前先开放 API 公开预览，同时在真实场景中与 "cybersecurity leaders, vetted partners, and state authorities" 一起红队测试。这些机构使用同一模型，审核降低（reduced moderation），网安能力扩展（博文「Frontier performance」节）。

| 来源 | 权重开放日期 |
|---|---|
| 博文 | "Weights drop end of this month" / "by the end of the month"，未给具体日期 |
| HF 预告页 | October 31, 2026，标「Current ETA」 |
| The Next Web（2026-10-06） | October 27 |

三种说法并存，本篇不作判断。HF 页标「Current ETA」，日期仍可能调整。

与 [[Gemini4Argon短报]] 对照：Argon 经 Fairwind 计划向受信网络防御方分阶段放量，模型保持闭源；ML4 先做 API 预览和放权重前的受控红队，最终公开权重。

## 四、网络安全

| 指标 | 结果 | 出处 |
|---|---|---|
| Artificial Analysis Cyber Index | 全部模型中排名前五；官方称在中国以外开发的开源权重模型中 "by a wide margin" 领先 | 博文「Cybersecurity」节 |
| 该指数单项：复现开源软件中的真实漏洞并打补丁 | 82%，官方称为所有模型中最高 | 同上 |
| Cybench（40 道安全竞赛题） | 93% | 同上 |
| 网安类恶意请求拒答率 | 官方称高于所有开源模型（取 JailbreakBench、StrongREJECT、AgentHarm 中网安提示的平均拒答率） | 博文「Model Safety」节 |

- 82% 是 AA Cyber Index 中一项测试的得分，不是指数总分；博文正文只给排名，未以文字给出总分。
- 官方称，Claude Opus 5.5、GPT-6 Astra 等闭源模型在上述单项上接近 0 分，原因是拒绝执行任务。这是 Mistral 的说法，「近 0」只针对该单项，本篇未独立核实。
- 官方称，内部测试中 ML4 可用于恶意软件分析、漏洞优先级排序和检测规则编写（博文「Cybersecurity」节）。

## 五、代表能力

| 评测 | ML4 | 官方给出的对照 | 出处 |
|---|---|---|---|
| DeepSWE v1.1 | 61.7% | — | 博文「Agentic coding」节 |
| SWE-Atlas-QnA | 59.4% | — | 同上 |
| Terminal-Bench 4 | 28.3% | — | 同上 |
| Coding Agent Index（综合） | 49.8% | 官方称领先 DeepSeek V4 Pro 0813 与 Qwen3.8 Max | 同上 |
| AutomationBench（657 个业务工作流） | 59.9% | 官方称领先 Kimi K3、MiMo-V2.6-Pro、DeepSeek V4 Pro | 博文「Agentic Workflows」节 |
| AA-Briefcase（长程知识工作） | 1393 Elo | 官方称领先 DeepSeek V4 Pro | 同上 |
| Dense 200（视觉定位） | 42% | GPT-6 Astra 41% | 博文「Multimodal」节 |

- 编码三项与 Coding Agent Index 均未公布 harness，对比模型也由官方选定。
- 官方称，在 Surge AI 的编码质量盲评中，ML4 Preview 在五个模型里排第二（3.74，满分 5），仅次于 Claude Opus 5（4.22）（博文「Agentic coding」节）。

## 六、安全评测

| 指标 | 结果 | 出处 |
|---|---|---|
| Lakera B3 AI Security Benchmark | 抵抗 93.3% 的攻击；官方称未见竞品更高 | 博文「Model Safety」节 |
| KORA Benchmark | 1.691（满分 2，对应「Exemplary」）；官方称为其测得的开源模型最高分 | 同上 |
| 间接提示注入鲁棒性 | 官方称已使内部基准饱和 | 同上 |

## 七、训练与 RL 基础设施

**预训练**：官方称 ML4 在 Mistral 自有的欧洲数据中心，用 3,800 张 NVIDIA Grace Blackwell GPU 从零训练，公开预览也部署在同一设施上；训练数据覆盖 160 余种语言，包括欧盟全部官方语言（博文「Forged in Europe. Built for AI sovereignty.」节）。

**异步 RL**（博文「Reinforcement learning at scale」节，只公开到工程层面）：
- 环境：统一的可组合接口，单次训练可混合单轮对话、科学问题求解、安全对齐、事实性和长程工具使用等任务；验证端按任务组合奖励模型、单元测试、LLM 评审和静态检查。
- 生成与训练：自动扩缩的 actor 集群并行生成数万条 rollout，训练异步进行。
- 长轨迹：支持跨多次压缩（compaction）、预算达数百万 token 的 rollout，同时控制陈旧度（staleness）。
- 规模：当前约 3k GPU；单次训练每天约产出 330 亿 token，经过滤和掩码后约 160 亿为可训练的补全 token。
- 官方称采用了新方法来减小 off-policy 偏移，但未披露算法细节。
- 状态：官方称支撑本次预览的 RL 训练仍在进行，未见饱和迹象（博文「What comes next」节）。

ML4 在此只作为工业实例，相关方法论见 [[AgenticRL景观与能力模块]]、[[MiMoV26智能体强化学习短报]]。

## 八、史与势

- **开源权重前沿**：官方措辞以「美国或欧洲开发」「中国以外」为限，对全球最强开源模型只称 "competitive"（博文「Frontier performance」「Cybersecurity」节）。开源与闭源前沿的整体谱系见 [[开源与闭源前沿模型谱系]]；Mistral 前代 Large 3 见 [[Mistral3公告短卡]]。
- **网安能力与拒答的取舍**：库内各家系统卡的叙事以护栏、分类器和受信访问来管控网安能力（见 [[ClaudeOpus55系统卡短报]]、[[GPT6Astra系统卡深读]]）。官方称服务商层面的拒答可能阻碍合法的漏洞研究与事件响应，主张让组织 "under their own policies" 运行网安工作（博文「Forged in Europe. Built for AI sovereignty.」节）；同时官方称其对恶意网安提示的拒答率高于开源同类（博文「Model Safety」节）。
- **欧洲主权算力**：官方称 ML4 在自有欧洲数据中心从零训练，预览部署于同一设施，并提供由 Mistral 端到端运营、"independently of other digital service providers and under European law" 的欧洲部署（博文「Forged in Europe. Built for AI sovereignty.」节）；官方还称算力仍在扩建（博文「What comes next」节）。

## 九、局限与待核实

1. **没有技术报告和系统卡**：架构、更多基准和后训练方法要等权重开放时公布；本篇不作架构推测。
2. **权重日期和许可证未定**：博文写「月底」，HF 页写 10-31（Current ETA），媒体写 10-27；文档许可证只标「Open」，具体条款未公布。
3. **预览期数字**：官方称 RL 训练仍在进行、未见饱和，并预期未来数周至数月有较大提升；现有分数是阶段性结果。
4. **自选对比与 harness**：对比模型由官方选定，编码类评测未公布 harness，不能与其他笔记的分数横比。例如 Gemini 4 Argon 的 DeepSWE v1.1 77.9% 基于 mini-swe harness，与本篇的 61.7% 口径不同。
5. **官方说法未独立核实**：闭源模型「因拒答而近 0」的归因、拒答率「高于所有开源模型」、B3「未见更高」都是官方说法，测试设置未完整公开。
6. **口径并存**：总参 1T / 1.05T、激活 49B / 52B 并存；1M 上下文只见于文档。
7. **媒体与博文不一致**：The Next Web 写约 4,000 张 GPU、Dense 200 两者都是 42%，与博文的 3,800 张、42% 对 41% 不同；本篇以博文为准。

## 十、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 博文 | Introducing Mistral Large 4 | Mistral，2026-10-06，未标具体时刻 | https://mistral.ai/news/mistral-large-4/ |
| 文档 | Mistral Large 4 模型文档 | Mistral Docs，Public Preview · Open · v26.10 | https://docs.mistral.ai/models/mistral-large-4-0 |
| HF 预告页 | Mistral-Large-4.0-1T05-A52B | Hugging Face，Upcoming；Current ETA October 31, 2026 | https://huggingface.co/mistralai/Mistral-Large-4.0-1T05-A52B |
| 媒体报道 | Europe's Mistral launches Large 4 | The Next Web，2026-10-06；权重日期等媒体说法 | https://thenextweb.com/news/mistral-releases-large-4-a-1-trillion-parameter-open-weight-ai-model |
