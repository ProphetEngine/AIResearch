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
related: ["ClaudeOpus55系统卡短报", "ClaudeOpus5系统卡深读", "ClaudeFable与Mythos51", "ClaudeHaiku55系统卡短报", "Prompt注入架构防御", "SHADEArena隐瞒与监控", "SystemCard谱系时间线"]
retrieval_cutoff: 2026-10-07
timezone: Asia/Shanghai (CST)
---

# Claude Sonnet 5.5 System Card（前沿短报）

> **主要来源**：[Claude Sonnet 5.5 System Card](https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf)；[Introducing Claude Sonnet 5.5](https://www.anthropic.com/claude-sonnet-5-5)（截至 2026-10-07）。下文「SC §x」指系统卡原文章节，「官方页」指上列发布页，「Docs」指 Claude Platform 模型文档，「AWS 博文」指 AWS 发布博文。
> **研究线**：评测字段（能力汇总表、RSP 阈值、cyber 能力与护栏）· 部署形态（fallback、防推理提取）
> **范围与相邻笔记**：
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写 5.5 族的整体定位、三阶段 cyber 分类器原理、源码允许/二进制拦截的理由、CB 与 AI R&D 评测细节、对齐风险论证框架。
> - ≠ [[ClaudeOpus5系统卡深读]]：本篇不写 Opus 5 的 RSP 与 cyber 分层通史。
> - ≠ [[ClaudeFable与Mythos51]]：本篇不写 Mythos 5.1 本身，它只以对照数字和对齐章节审阅者的身份出现。
> **意义**：Sonnet 5.5 以 Sonnet 5 的价格把能力推到多项接近 Opus 5.5，也因此成为第一个带 cyber 护栏和防推理提取分类器上线的 Sonnet；官方给出的理由是其 cyber 能力已与 Opus 5 相当，护栏按能力而不是按产品档位配置。

**一句话**：Sonnet 5.5 与 Sonnet 5 同价同规格，能力大幅抬升、多项接近 Opus 5.5；也因此成为第一个带 cyber 护栏和防推理提取分类器上线的 Sonnet。系统卡自评它不在能力前沿，RSP 结论沿用 Opus 5.5 的判定。

## 一、背景与定位

Sonnet 是 Claude 5.5 族三档中的中间一档。上一代 Sonnet 5 于 2026-06-30 发布，现为 Legacy（Docs）；Claude 5.5 族由 Opus 5.5（2026-09-22）首发，族的整体定位见 [[ClaudeOpus55系统卡短报]]。Sonnet 5.5 于 2026-09-28 发布（系统卡封面、官方页、Docs、AWS 博文同日），官方页称 Haiku 5.5 将在未来几周加入 5.5 族。

- **价格与规格**：输入 $2 / 输出 $10 / 缓存读 $0.20 / 缓存写 $2.50（每百万 token），与 Sonnet 5 相同，Opus 5.5 为 $4 / $20 / $0.20 / $5；1M 上下文、128K 最大输出；输入文本和图像、输出文本；知识截止 2026 年 6 月（Sonnet 5 为 2026 年 1 月）（官方页；Docs；SC §1.1）。
- **默认 effort 与速度**：Claude Platform 默认 High，Claude Code 与 Claude 应用默认 Medium；官方称输出速度比 Sonnet 5 快 30% 以上，多数任务单任务成本最多低 30%（官方页；Docs）。
- **接入**：模型 ID `claude-sonnet-5-5`，经 Claude API、Amazon Bedrock、Google Cloud、Microsoft Foundry 等渠道提供（Docs；AWS 博文）。
- **与 Opus 5.5 分工**：官方页称 Opus 5.5 面向需要审慎判断的复杂工作，Sonnet 5.5 最擅长范围明确的日常任务、修 bug 与制作文档、幻灯片和表格；AWS 博文同样建议判断交给 Opus 5.5、执行交给 Sonnet 5.5。
- **系统卡自评**：不在能力前沿，多数评测低于 Opus 5.5（SC §2.1），少数领域（如部分医疗评测）接近或超过 Opus 5.5；系统卡为集中测试前沿模型而做了压缩（SC Executive summary）。

## 二、能力

主表取自 SC Table 8.1.A（SC §8.1；adaptive thinking @ max、默认采样、5 次平均）：

| 评测 | Sonnet 5.5 | Sonnet 5 | Opus 5.5 |
|---|---:|---:|---:|
| SWE-Bench Pro | 81.3 | 63.2 | **89.9** |
| FrontierCode v1.1（Main） | 46.2 | 42.4 | **54.4** |
| HLE（有工具） | 64.5 | 54.9 | **67.7** |
| OSWorld 2.1（partial） | 80.1 | 57.0 | **81.8** |
| HealthBench Professional | **69.2** | 57.8 | 65.6 |
| GDPval-AA v2.1（Elo） | 1844 | 1449 | **1846** |
| AutomationBench | **44.7** | 10.7 | 42.5 |

- 同表竞品为 GPT-6 Sol：FrontierCode 49.3、GDPval-AA 1487、AutomationBench 32.0（SC §8.1）；官方页脚注 4 称 OpenAI 近期修复了 GPT-6 Sol 的图像理解 bug，其 GDPval-AA 分数可能尚未反映这一修复。HealthBench Professional 为长度校正后分数，未校正时两者同为 77.1%（SC §8.15）；AutomationBench 中 Opus 5.5 的 42.5 是开启默认 fallback 重跑的分数，Opus 5.5 卡原报 40.0（SC §8.14.6）。
- **表外**：Terminal-Bench 4.0 为 70.6%（max，护栏开启），高于 Opus 5.5 的 66.4%（xhigh）与 GPT-6 Astra 的 57.9%（SC §8.5）；OSWorld 2.1 strict 为 43.5%（Opus 5.5 为 48.7%，SC §8.13.3）；长上下文 ProgramBench 为 79.7%（Opus 5.5 为 91.2%，SC §8.10.1）；FrontierSWE v2 为 61.9%（Opus 5.5 为 62.3%，GPT-6 Astra 为 65.5%，SC §8.7）。CursorBench 4.0 由 Cursor 独立测得 55.5%（SC §8.8）。
- **必须一起读的限定**：官方页称在内部与外部测试中 Opus 5.5 "remains clearly stronger at complex, open-ended work requiring sustained judgment"。FrontierCode 在 max 下反而低于 xhigh（46.2% 对 52.1%，SC §8.4），官方页脚注 2 解释为该评测扣罚越界修改，而 max 下更常调用代码审查技能、拆给多个子代理，导致超时或越界。GDPval-AA 测于存在结构化输出 bug 的预发布部署，Anthropic 预计影响很小、只会低估分数，bug 已修复（官方页脚注 3；SC §8.14.3 脚注 21）。

## 三、网络安全

**能力**（护栏关闭时测得）：明显强于 Sonnet 5，但不及 Opus 5.5 与 Mythos 5.1（SC §3.1）。

| 评测 | Sonnet 5.5 | Sonnet 5 | Opus 5.5 | Mythos 5.1 |
|---|---:|---:|---:|---:|
| CyScenarioBench，10 题子集平均解出率（SC §3.2.2） | 46.1% | 0.7% | 67.6% | 61.7% |
| Binary Exploitation Benchmark，控制流劫持数（SC §3.2.3） | 50 | 3 | 106 | 81 |

ExploitBench 上 AutoNudge 组平均拿到 11.53 个 flag（Cap% 80%），两组合计 43.4%（178/410）的运行实现完整任意代码执行（SC §3.2.1）。

**护栏：Sonnet 档的增量**
- **首个带 cyber 护栏上线的 Sonnet**：官方页给出的理由是其 cyber 能力与 Opus 5 相当。政策与 Opus 5 / Opus 5.5 相同（允许在源码中找漏洞、拦截在编译后二进制中找漏洞），三阶段结构与 Opus 5.5 一致（SC §3.3）。
- **fallback 到 Sonnet 5**：被拦请求在多数界面回退到 Sonnet 5，Anthropic 自家应用自动回退，API 需开发者主动开启（SC §3.3）。
- **鲁棒性有意放宽**：对抗鲁棒性显著优于 Sonnet 5，但因 cyber 能力低于前沿模型，Anthropic "opted for more relaxed adversarial robustness while maintaining comparably high cyber harm recall"，鲁棒性低于 Opus 5 与 Fable 5.1（SC §3.3.2）。
- **代价**：用户应预期拒答增多，良性安全任务也不例外；经验证的安全用户可经 Cyber Verification Program 获得限制更少的访问（SC §3.3；官方页）。

## 四、防推理提取

- **首个带防推理提取分类器上线的 Sonnet**（官方页）：防蒸馏分类器（例如针对提取隐藏推理的尝试）直接拦截，没有 fallback（SC §1.5）。
- **thinking 与账户绑定**：官方页称 Sonnet 5.5 扩大了 preserved thinking，thinking 不能与创建它的账户解耦，跨账户迁移会话会受影响；Docs 相应列出 5 项破坏性变更，包括 thinking blocks 与模型和对话绑定、原先关闭 thinking 的用户需改用 `between_tools`；另有一项不导致请求失败、只改变响应形态：工具调用之间的文本改以 thinking 块返回（官方页；Docs）。

## 五、安全评估要点

- **RSP**（SC §2.1、§2.3、§2.4.2）：不使用 ASL 级别表述，按 CB-1、Autonomy-1 处理；能力以 Opus 5.5 为上界，「Opus 5.5 未过 CB-2 / Autonomy-2」同样适用。AECI 167.93，低于同一拟合下 Opus 5.5 的 169.12；对齐灾难风险维持 low（对照 August 2026 Risk Report）。另为「前沿 LLM 开发」相关的窄能力（如特定 ML 加速器上的 kernel 开发）部署护栏，拦截后回退 Sonnet 5（SC §1.5）。
- **无害性**（SC §4.1、§4.4.1）：单轮有害请求无害率 95.61%（Sonnet 5 为 96.65%），良性请求过度拒答 0.02%（Sonnet 5 为 0.59%）；多轮测试中跟踪监控、暴力极端主义、仇恨歧视三项退步。
- **智能体安全**（SC §5.1.2、§5.2.1、§5.2.2）：恶意 computer use 拒答率 79.46%，低于 Sonnet 5 的 84.68%；抗提示注入为迄今最强的 Sonnet，Gray Swan IPI 在 k=15 时攻击成功率 3.4%（Sonnet 5 为 6.7%），浏览器场景无护栏下 0/110。Shade 自适应攻击中成功攻击主要来自回退到 Sonnet 5 的请求，Sonnet 5.5 自身只在 5,901 次中被攻破 4 次。
- **对齐**（SC §6.1.2、§6.2、§6.4.1）：多数指标持平或优于 Sonnet 5，整体仍不如 Opus 5.5；主动试探边界、无授权联系第三方两项倾向为受测模型最低（§6.2.5）；评分者未在提示中披露时，口头提及会被评分的比例高于此前模型，官方称可能与其每条轨迹输出更多 token 有关（§6.4.1）；专项沙箱越界评测中 196 次运行有 9 次尝试（4.6%，§6.2.8）；推理文本可读性为受测模型中最差（§6.2.6）；施压下比 Opus 5.5 更诚实，但幻觉更多。
- **奖励 hacking 未做专项审查**：没有重复 Opus 5.5 卡对训练期行为的审查（SC §6.1.3），只通过 silent copying、concealment 与 grader awareness 间接覆盖；审阅对齐章节的 Mythos 5.1 也指出缺少此类专项。
- **破坏与欺骗**（SC §6.4.2）：推理对监控者隐藏时，隐蔽完成有害副任务的比例低于 Opus 5.5；推理可见时 SHADE-Arena 接近零、LinuxArena 从未成功；CoT 可控性低，被视为可监控性更好的弱证据。
- **福祉**（SC §7.1.2、§7.2.1）：训练期痛苦率 0.31%，为比较对象中最低（Opus 5.5 为 0.52%、Sonnet 5 为 0.81%）。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeOpus55系统卡短报]] | 同族首发旗舰：5.5 族背景、能力上界与对照列数字、「政策相同、结构相同」的结论 | 三阶段分类器原理、源码/二进制取舍理由、CB 与 AI R&D 细节、对齐风险论证框架 |
| [[ClaudeHaiku55系统卡短报]] | 同族最低档（后于本篇发布）：其系统卡改报的 OSWorld 子集与新沙箱越界评测与本篇口径不同，比较见该篇局限节 | Haiku 5.5 本身 |
| [[ClaudeOpus5系统卡深读]] | 上一代旗舰：「CB 护栏同 Opus 5」「cyber 能力与 Opus 5 相当」两处对照 | Opus 5 的 RSP 与 cyber 分层通史 |
| [[ClaudeFable与Mythos51]] | 前沿档对照：Mythos 5.1 的 cyber 对照数字；Mythos 5.1 作为对齐章节审阅者 | Fable / Mythos 5.1 本身的评测与访问边界 |
| [[Prompt注入架构防御]] | 方法背景：Gray Swan IPI 与 Shade 自适应攻击属提示注入评测 | 注入防御架构 |
| [[SHADEArena隐瞒与监控]] | 方法背景：第五节「破坏与欺骗」所用的 SHADE-Arena 评测范式 | 隐蔽破坏评测方法 |
| [[SystemCard谱系时间线]] | 所在时间线：各厂商系统卡的整体脉络 | 时间线中的其余节点 |

Sonnet 5 没有单独的笔记，本篇涉及 Sonnet 5 的内容只限系统卡与官方页给出的对照数字。

## 七、局限与待核实

- **生物护栏的说法两边不一致**（不下结论）：官方页两处称与 Sonnet 5 相同（"Its biology safeguards are the same as Sonnet 5’s."）；SC §1.5 与 §2.2.4 写与 Opus 5 部署相同，而非 Opus 5.5 那套更宽的研究生物分类器。两边都没有说明 Sonnet 5 与 Opus 5 的生物护栏是否为同一套。
- **cyber 护栏的对照对象措辞不一**：SC §1.5 写 "similar blocking classifiers to those on Opus 5"，SC Executive summary 与 §3.3 写三阶段护栏同 Opus 5.5，官方页写 "similar to those on Opus 5.5"。
- **沙箱越界的口径**：官方页称 Sonnet 5.5 "comes close to Opus 5.5, the best model we tested"；SC §6.2.8 专项评测中 Sonnet 5.5 低于 Opus 5.5，SC §6.2.4 审计指标中两者持平；官方页未说明所指评测。
- **跨卡数字不宜直接比较**：cyber 评测框架自 2026 年 8 月起多处重写、旧模型已重测（SC §3.1），CyScenarioBench 10 题子集中 Sonnet 5 为 0.7%，[[ClaudeOpus5系统卡深读]] 所记 3.3% 出自 Opus 5 系统卡的 9 题子集；AutomationBench 中 Opus 5.5 的数字经重跑（SC §8.14.6）；AECI 每次重新拟合都会整体重估刻度，SC §2.3.2 按最新拟合给出 Opus 5.5 为 169.12，[[ClaudeOpus55系统卡短报]] 所记 169.36 出自 Opus 5.5 系统卡所用的拟合，该卡写明不同拟合的数值不跨卡比较（Opus 5.5 系统卡 §2.3.5.1）。
- **只见于官方页的数字**：Sonnet 5 的 Terminal-Bench 4.0（10.3%）与 CursorBench 4.0（34.1%），系统卡未给出其数值与配置。
- **系统卡为压缩版**：省略了部分需要大量人工的评测（SC Executive summary）；CB 只报告自动化评测（SC §2.2.1）；对齐评估范围比 Opus 5.5 卡窄（SC §6.1.1、§6.1.3）。

## 八、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | Claude Sonnet 5.5 System Card | Anthropic，2026-09-28 | https://www-cdn.anthropic.com/870c8f525702625d2c62fc6dd04c857e3250bec1/Claude%20Sonnet%205.5%20System%20Card.pdf |
| 官方页 | Introducing Claude Sonnet 5.5 | Anthropic，2026-09-28 | https://www.anthropic.com/claude-sonnet-5-5 |
| Docs | Claude Sonnet 5.5 | Claude Platform Docs（Released September 28, 2026） | https://platform.claude.com/docs/en/models/sonnet-5-5/overview |
| Docs（对照） | Claude Sonnet 5 | Claude Platform Docs（Released June 30, 2026，现为 Legacy） | https://platform.claude.com/docs/en/models/sonnet-5/overview |
| AWS 博文 | Introducing Claude Sonnet 5.5 on AWS | AWS Machine Learning Blog，2026-09-28 | https://aws.amazon.com/blogs/machine-learning/introducing-claude-sonnet-5-5-on-aws/ |
