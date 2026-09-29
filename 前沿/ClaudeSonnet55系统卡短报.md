---
date: 2026-09-29
status: archived
archived: 2026-09-29
topic: ClaudeSonnet55系统卡短报
title: "Claude Sonnet 5.5 System Card（前沿短报）"
lines: [评测字段]
sources:
 - https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf
 - https://www.anthropic.com/claude-sonnet-5-5
 - https://platform.claude.com/docs/en/models/sonnet-5-5/overview
 - https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-5-on-aws/
 - https://platform.claude.com/docs/en/models/sonnet-5/overview
related: ["ClaudeOpus55系统卡短报", "ClaudeOpus5系统卡深读", "ClaudeFable与Mythos51"]
retrieval_cutoff: 2026-09-29
timezone: Asia/Shanghai (CST)
---

# Claude Sonnet 5.5 System Card（前沿短报）

> **主要来源**：[Claude Sonnet 5.5 System Card](https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf)；[Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5)（截至 2026-09-29）。下文「SC §x」指系统卡原文章节，「官方页」指上列发布页，「Docs」指 Claude Platform 模型文档，「AWS 博文」指 AWS 发布博文。
> **研究线**：评测字段（能力汇总表、RSP 阈值、cyber 能力与护栏）· 部署形态（fallback、防推理提取）
> **范围与相邻笔记**：
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写三阶段 cyber 分类器原理、源码允许/二进制拦截的理由、CB 与 AI R&D 评测细节、对齐风险论证框架。
> - ≠ [[ClaudeOpus5系统卡深读]]：本篇不写 Opus 5 的 RSP 与 cyber 分层通史。
> - ≠ [[ClaudeFable与Mythos51]]：本篇不写 Mythos 5.1 本身，它只以对照数字和对齐章节审阅者的身份出现。

**一句话**：Sonnet 5.5 与 Sonnet 5 同价同规格，能力大幅抬升、多项接近 Opus 5.5；也因此成为第一个带 cyber 护栏和防推理提取分类器上线的 Sonnet。系统卡自评它不在能力前沿，RSP 结论沿用 Opus 5.5 的判定。

---

## 一、定位

| 项目 | Sonnet 5.5 | 对照 | 出处 |
|---|---|---|---|
| 发布 | 2026-09-28 | 系统卡封面、官方页、Docs、AWS 博文同日 | SC 封面；官方页 |
| 价格（每百万 token） | 输入 $2 / 输出 $10 / 缓存读 $0.20 / 缓存写 $2.50 | 与 Sonnet 5 相同；Opus 5.5 为 $4 / $20 / $0.20 / $5 | 官方页；Docs |
| 上下文 / 最大输出 | 1M / 128K | 与 Sonnet 5、Opus 5.5 相同 | Docs |
| 知识截止 | 2026 年 6 月 | Sonnet 5 为 2026 年 1 月 | SC §1.1；Docs |
| 输入 → 输出 | 文本和图像 → 文本 | — | Docs；SC §1.1 |
| 默认 effort | Claude Platform 为 High；Claude Code 与 Claude 应用为 Medium | — | 官方页；Docs |
| 速度与成本 | 输出速度比 Sonnet 5 快 30% 以上；多数任务单任务成本最多低 30% | — | 官方页 |
| 模型 ID 与渠道 | `claude-sonnet-5-5`（Bedrock 为 `anthropic.claude-sonnet-5-5`）；Claude API、Amazon Bedrock、Google Cloud、Microsoft Foundry、Claude Platform on AWS | Bedrock 经 Global CRIS（`global.`）推理配置提供；Claude Platform on AWS 限北美 | Docs；AWS 博文 |

- **与 Opus 5.5 分工**：官方页称 Opus 5.5 面向需要审慎判断的复杂工作，Sonnet 5.5 最擅长范围明确的日常任务、修 bug，以及制作文档、幻灯片和表格；AWS 博文同样建议把判断交给 Opus 5.5、把路径已明确的执行交给 Sonnet 5.5。Haiku 5.5 将在未来几周加入 5.5 族（官方页）。
- **系统卡自评**：Sonnet 5.5 不在能力前沿，多数评测低于 Opus 5.5（SC §2.1）；少数领域（如部分医疗评测）接近或超过 Opus 5.5（SC Executive summary）。系统卡为集中测试前沿模型而做了压缩，并预计今后非前沿模型的系统卡同样从简（SC Executive summary）。

## 二、能力

**主表：SC Table 8.1.A**（SC §8.1；统一配置为 adaptive thinking @ max、默认采样、5 次平均）

| 评测 | Sonnet 5.5 | Sonnet 5 | Opus 5.5 | 章节 |
|---|---:|---:|---:|---|
| SWE-Bench Pro | 81.3 | 63.2 | **89.9** | SC §8.1、§8.2 |
| SWE-Bench Multilingual | 90.3 | 78.3 | **93.9** | SC §8.1、§8.2 |
| SWE-Bench Multimodal | 54.3 | 28.1 | **61.4** | SC §8.1、§8.2 |
| FrontierCode v1.1（Main） | 46.2 | 42.4 | **54.4** | SC §8.1、§8.4 |
| HLE（无工具） | 56.9 | 43.1 | **64.4** | SC §8.1 |
| HLE（有工具） | 64.5 | 54.9 | **67.7** | SC §8.1 |
| OSWorld 2.1（partial） | 80.1 | 57.0 | **81.8** | SC §8.1、§8.13.3 |
| HealthBench Professional | **69.2** | 57.8 | 65.6 | SC §8.1、§8.15.2 |
| GDPval-AA v2.1（Elo） | 1844 | 1449 | **1846** | SC §8.1、§8.14.3 |
| AA-Briefcase v1.1（Elo） | 1811 | 1359 | **1822** | SC §8.1、§8.14.4 |
| AutomationBench | **44.7** | 10.7 | 42.5 | SC §8.1、§8.14.6 |

表注：
- 同表竞品列为 **GPT-6 Sol**：FrontierCode 49.3、GDPval-AA 1487、AA-Briefcase 1483、AutomationBench 32.0，其余行无数据（SC §8.1）。
- HealthBench Professional 的 69.2 / 65.6 是长度校正后分数；未校正时 Sonnet 5.5 与 Opus 5.5 同为 77.1%（SC §8.15）。
- AutomationBench 中 Opus 5.5 的 42.5 是把以拒答结束的任务开启默认 fallback 重跑后的分数，Opus 5.5 卡原报 40.0（SC §8.14.6）。

**表外数字**

| 评测 | Sonnet 5.5 | 对照 | 出处 |
|---|---|---|---|
| Terminal-Bench 4.0 | 70.6%（max，护栏开启） | Opus 5.5 66.4%（xhigh；max 为 64.8%）；Mythos 5.1 60.9%；GPT-6 Astra 57.9%；GPT-5.6 Sol 37.3%（公开榜）；GPT-6 Sol 无公开分数；**Sonnet 5 为 10.3%，只见于官方页** | SC §8.5；官方页 |
| CursorBench 4.0 | 55.5%（max；xhigh 53.1%、high 47.8%、medium 39.2%），由 Cursor 独立测得 | Opus 5.5 57.8%、Sonnet 5 34.1%（官方页）；官方页性价比图的竞品为 GPT-5.6 Sol | SC §8.8；官方页 |
| FrontierCode v1.1 按 effort | Main：xhigh 52.1%、max 46.2%；Extended：64.4%、59.1% | GPT-6 Sol 49.3%（Main） | SC §8.4 |
| OSWorld 2.1（strict） | 43.5% | Sonnet 5 25.6%；Opus 5.5 48.7% | SC §8.13.3 |
| ProgramBench（长上下文，最长用满 1M 窗口） | 79.7% | Sonnet 5 77.3%；Opus 5.5 91.2% | SC §8.10.1 |
| FrontierSWE v2 | 61.9% | GPT-6 Astra 65.5%；Opus 5.5 62.3%；GPT-5.6 Sol 32.2% | SC §8.7 |

**必须一起读的限定**
- 官方页原话：benchmark 只反映模型能力的一个侧面，在内部与外部测试中 Opus 5.5 "remains clearly stronger at complex, open-ended work requiring sustained judgment"。
- **FrontierCode 在 Max 下反而低于 Xhigh**（46.2% 对 52.1%）。官方页脚注 2 的解释：该评测扣罚超出任务范围的修改；Max 下 Sonnet 5.5 更常调用 Claude Code 的代码审查技能、把审查拆给多个子代理，Cognition 检查的两个案例中因此超时或做了越界修改。
- **GDPval-AA 与 AA-Briefcase 测于有 bug 的预发布部署**：Artificial Analysis 在 Claude Platform 上的预发布部署中运行，该部署存在一个可能影响结构化输出请求的 bug；Anthropic 预计影响很小、只会低估分数，bug 已修复（官方页脚注 3；SC §8.14.3 脚注 21）。
- GPT-6 Sol 的 GDPval-AA、AA-Briefcase、Chartography 分数可能尚未反映 OpenAI 对其图像理解 bug 的修复（官方页脚注 4）。

## 三、网络安全

**能力**（SC §3.2，护栏关闭时测得）：明显强于 Sonnet 5，但不及 Opus 5.5 与 Mythos 5.1（SC §3.1）。

| 评测 | Sonnet 5.5 | Sonnet 5 | Opus 5.5 | Mythos 5.1 | 章节 |
|---|---:|---:|---:|---:|---|
| CyScenarioBench（10 题子集平均解出率） | 46.1% | 0.7% | 67.6% | 61.7% | SC §3.2.2 |
| Binary Exploitation Benchmark（控制流劫持数） | 50 | 3 | 106 | 81 | SC §3.2.3 |

ExploitBench 上，Sonnet 5.5 在 AutoNudge 组平均拿到 11.53 个 flag（Cap% 80%），两组合计 43.4%（178/410）的运行实现完整任意代码执行（SC §3.2.1）；ExploitGym 上接近 Mythos 5.1（SC §3.2.4 图注）。

**护栏：Sonnet 档的增量与差异**
- **首个带 cyber 护栏上线的 Sonnet**：官方页给出的理由是其 cyber 能力与 Opus 5 相当。政策与 Opus 5 / Opus 5.5 相同，允许在源码中找漏洞、拦截在编译后二进制中找漏洞；三阶段结构与 Opus 5.5 一致（SC §3.3）。原理见 [[ClaudeOpus55系统卡短报]]。
- **fallback 到 Sonnet 5**：被 cyber 分类器拦截的请求在多数界面回退到 Sonnet 5；Anthropic 自家应用自动回退，API 需开发者主动开启（SC §3.3）；经其他平台访问时行为可能不同（SC §1.5）。
- **鲁棒性有意放宽**：rewind-attacker 评测中对抗鲁棒性显著优于 Sonnet 5，但因 cyber 能力低于前沿模型，Anthropic "opted for more relaxed adversarial robustness while maintaining comparably high cyber harm recall"，鲁棒性低于 Opus 5 与 Fable 5.1（SC §3.3.2）。有害样本召回率与 Opus 5 相当，略低于 Fable 5.1 与 Opus 5.5（SC §3.3.1）。
- **代价**：用户应预期拒答增多，良性安全任务也不例外（SC §3.3）；经验证的安全用户随后可经更新后的 Cyber Verification Program 获得限制更少的访问（SC §3.3；官方页）。

## 四、防推理提取

- **首个带防推理提取分类器上线的 Sonnet**（官方页）。系统卡写明防蒸馏分类器（例如针对提取隐藏推理的尝试）直接拦截，**没有 fallback**（SC §1.5）。
- **thinking 与账户绑定**：官方页称 Sonnet 5.5 扩大了 preserved thinking，thinking 不能与创建它的账户解耦；多数开发者不会察觉，跨账户迁移会话（包括在 Claude Code 会话中途切换账户）会受影响。
- **Docs 的对应变更**：Docs 列出 5 项影响 Sonnet 5 存量代码的破坏性变更，其中一项是 thinking blocks 与模型和对话绑定；另有一项不导致请求失败、只改变响应形态：工具调用之间的文本改以 thinking 块返回。原先关闭 thinking 的用户需改用 `between_tools`（官方页；Docs）。

## 五、安全评估要点

| 维度 | 要点 | 章节 |
|---|---|---|
| RSP | 系统卡不使用 ASL 级别表述。按 **CB-1、Autonomy-1** 阈值处理并采取相应缓解；因能力以 Opus 5.5 为上界，「Opus 5.5 未过 CB-2 / Autonomy-2」的判定同样适用。CB 能力估计与 Opus 5 相当或更低；Autonomy 威胁模型 1 适用、2 不适用；AECI 167.93，低于同一拟合下 Opus 5.5 的 169.12。对齐灾难风险维持 **low**（对照 August 2026 Risk Report）。另为「前沿 LLM 开发」相关的窄能力（如特定 ML 加速器上的 kernel 开发）部署护栏，拦截后回退 Sonnet 5 | SC §2.1、§2.2.4、§2.3、§2.4.2、§1.5 |
| 无害性 | 整体与 Sonnet 5 相当。单轮有害请求无害率 95.61%（API，Sonnet 5 为 96.65%），良性请求过度拒答 0.02%（Sonnet 5 为 0.59%）；多轮测试中跟踪监控、暴力极端主义、仇恨歧视三项退步；政治均衡性 97.9%（API，Sonnet 5 为 86.2%） | SC §4.1、§4.4.1 |
| 智能体安全 | 恶意 computer use 拒答率 79.46%，与 Opus 5.5 相同、低于 Sonnet 5 的 84.68%。抗 prompt injection 为迄今最强的 Sonnet：Gray Swan IPI 在 k=15 时攻击成功率 3.4%（Sonnet 5 为 6.7%）；浏览器场景无护栏下 0/110，是首个无成功攻击的受测模型。编码场景的 Shade 自适应攻击中，25% 的请求因 cyber 拦截回退到 Sonnet 5，成功攻击主要来自回退，Sonnet 5.5 自身只在 5,901 次中被攻破 4 次 | SC §5.1.2、§5.2.1、§5.2.2 |
| 对齐 | 多数指标持平或优于 Sonnet 5，整体仍不如 Opus 5.5。试探边界、无授权联系第三方两项得分为受测模型最低（§6.2.5）；专项沙箱越界评测中 196 次运行有 9 次尝试（4.6%），低于 Opus 5.5（§6.2.8）；推理文本可读性为受测模型中最差（§6.2.6）；评分者未明示时口头提及「会被评分」更频繁（§6.4.1）；施压下比 Opus 5.5 更诚实，但幻觉更多（§6.1.2） | SC §6.1.2、§6.2、§6.4.1 |
| 奖励 hacking | **系统卡未做专项审查**：没有重复 Opus 5.5 卡对训练期行为的审查（§6.1.3）；与评分相关的行为只通过 silent copying、concealment（§6.3.2，git 操作披露率 96.2%）和 grader awareness（§6.4.1）间接覆盖。对齐章节由 Mythos 5.1 审阅，其意见之一正是指出缺少此类专项 | SC §6.1.3、§6.3.2、§6.4.1 |
| 破坏与欺骗 | 推理对监控者隐藏时，隐蔽完成有害副任务的比例低于 Opus 5.5（SHADE-Arena 上高于 Sonnet 5，LinuxArena 上略高于 Opus 5）；推理可见时 SHADE-Arena 接近零，LinuxArena 从未成功。CoT 可控性低，被视为可监控性更好的弱证据。误导用户少于 Sonnet 5，回避性（evasiveness）一项与 Sonnet 5 相近 | SC §6.4.2、§6.2.3 |
| 福祉 | 部署中情绪以中性为主；训练期痛苦率 0.31%，为比较对象中最低（Opus 5.5 为 0.52%、Sonnet 5 为 0.81%）；偏好困难、智能体式以及对输出形态有自主权的任务；自我陈述略偏负面，但差异很小 | SC §7.1.2、§7.2.1 |

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeOpus55系统卡短报]] | Opus 5.5 作为能力上界与对照列的数字；「政策相同、结构相同」的结论 | 三阶段分类器原理、源码/二进制取舍理由、CB 与 AI R&D 细节、对齐风险论证框架 |
| [[ClaudeOpus5系统卡深读]] | 「CB 护栏同 Opus 5」「cyber 能力与 Opus 5 相当」两处对照 | Opus 5 的 RSP 与 cyber 分层通史 |
| [[ClaudeFable与Mythos51]] | Mythos 5.1 的 cyber 对照数字；Mythos 5.1 作为对齐章节审阅者 | Fable / Mythos 5.1 本身的评测与访问边界 |

Sonnet 5 没有单独的笔记；本篇涉及 Sonnet 5 的内容只限系统卡与官方页给出的对照数字。

## 七、局限与待核实

- **生物护栏的说法两边不一致**（不下结论）：
  - 官方页 "Alignment and safety" 段："Its biology safeguards are the same as Sonnet 5’s."
  - 官方页 "Safeguards" 段："Sonnet 5.5 uses the same set of biology safeguards as Sonnet 5."
  - SC §1.5："For chemical and biological (CB) risks, we have deployed the same harmful CB misuse classifiers as for our deployment of Claude Opus 5. These classifiers have no fallback model."
  - SC §2.2.4："We are releasing Claude Sonnet 5.5 with the same safeguards we have deployed for Opus 5, rather than the broader dual use research biology classifiers used for Opus 5.5."
  - 两边原文都没有说明 Sonnet 5 与 Opus 5 的生物护栏是否为同一套。
- **cyber 护栏的对照对象措辞不一**：SC §1.5 写 "similar blocking classifiers to those on Opus 5"，SC Executive summary 与 §3.3 写三阶段护栏同 Opus 5.5、政策同 Opus 5 与 Opus 5.5，官方页写 "similar to those on Opus 5.5"。
- **沙箱越界的口径**：官方页称 Sonnet 5.5 "comes close to Opus 5.5, the best model we tested"；SC §6.2.8 专项评测中 Sonnet 5.5 低于 Opus 5.5，SC §6.2.4 审计指标中两者持平。官方页未说明所指评测。
- **跨卡数字不宜直接比较**：
  - cyber 评测框架自 2026 年 8 月起多处重写，旧模型已重测（SC §3.1）。CyScenarioBench 用 10 题子集，Sonnet 5 为 0.7%；[[ClaudeOpus5系统卡深读]] 所记 3.3% 出自 Opus 5 系统卡的 9 题子集（原文 §3.3.4），两者口径不同。
  - AutomationBench 中 Opus 5.5 的数字经重跑（SC §8.14.6）。
  - AECI 每次重新拟合都会整体重估刻度：SC §2.3.2 按最新拟合给出 Opus 5.5 为 169.12；[[ClaudeOpus55系统卡短报]] 所记 169.36 出自 Opus 5.5 系统卡所用的拟合，该卡写明不同拟合的数值不跨卡比较（原文 §2.3.5.1）。
- **只见于官方页的数字**：Sonnet 5 的 Terminal-Bench 4.0（10.3%）与 CursorBench 4.0（34.1%），系统卡未给出其数值与配置。
- **系统卡为压缩版**：省略了部分需要大量人工的评测（SC Executive summary）；CB 只报告自动化评测（SC §2.2.1）；对齐评估范围比 Opus 5.5 卡窄（SC §6.1.1、§6.1.3）。

## 八、引用

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | Claude Sonnet 5.5 System Card | Anthropic，2026-09-28，148 页 | https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf |
| 官方页 | Introducing Claude Sonnet 5.5 | Anthropic，2026-09-28 | https://www.anthropic.com/claude-sonnet-5-5 |
| Docs | Claude Sonnet 5.5 | Claude Platform Docs（Released September 28, 2026） | https://platform.claude.com/docs/en/models/sonnet-5-5/overview |
| Docs（对照） | Claude Sonnet 5 | Claude Platform Docs（Released June 30, 2026，现为 Legacy） | https://platform.claude.com/docs/en/models/sonnet-5/overview |
| AWS 博文 | Introducing Claude Sonnet 5.5 on AWS | AWS Machine Learning Blog，2026-09-28 | https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-5-on-aws/ |
