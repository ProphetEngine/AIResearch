---
date: 2026-10-08
status: archived
archived: 2026-10-08
topic: ClaudeHaiku55系统卡短报
title: "Claude Haiku 5.5 System Card（前沿短报）"
lines: [评测字段]
sources:
 - https://www-cdn.anthropic.com/e1080d6bf5ae2018ea3c2f414064be03232f5be5/Claude%20Haiku%205.5%20System%20Card.pdf
 - https://www.anthropic.com/claude-haiku-5-5
 - https://platform.claude.com/docs/en/models/haiku-5-5/overview
related: ["ClaudeSonnet55系统卡短报", "ClaudeOpus55系统卡短报", "ClaudeOpus5系统卡深读", "ClaudeFable与Mythos51", "Gemini4Argon短报", "Prompt注入架构防御", "SHADEArena隐瞒与监控"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# Claude Haiku 5.5 System Card（前沿短报）

> **主要来源**：[System Card: Claude Haiku 5.5](https://www-cdn.anthropic.com/e1080d6bf5ae2018ea3c2f414064be03232f5be5/Claude%20Haiku%205.5%20System%20Card.pdf)；[Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)；[Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)（截至 2026-10-08）。下文「SC §x」指系统卡原文章节，「发布页」指上列 Anthropic 发布页，「Docs」指 Claude Platform 模型文档。
> **研究线**：评测字段（分段价目、能力选项、RSP 阈值）· 部署形态（无 fallback 的分类器、按能力收窄的 cyber 护栏）
> **范围与相邻笔记**：
> - ≠ [[ClaudeSonnet55系统卡短报]]：本篇不重写 Sonnet 5.5 的能力主表、三阶段 cyber 护栏与防推理提取；Sonnet 5.5 只作对照列与 fallback 对照出现。
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写 RSP 判定的论证框架、CB 与 AI R&D 评测细节；RSP 结论只记「沿用」。
> - ≠ [[ClaudeOpus5系统卡深读]]：本篇不写 Opus 5 的 RSP 与 cyber 分层通史；Opus 5 只作护栏与能力参照出现。
> - ≠ [[ClaudeFable与Mythos51]]：本篇不写 Fable / Mythos 5.1 本身；二者只作对照数字与对齐章节审阅者出现。
> - ≠ [[Gemini4Argon短报]]：本篇只引 Anthropic 在 SC §5.2.1 测得的 Argon 间接注入数字，不写 Argon 的发布与 Fairwind 放量。

**一句话**：Claude Haiku 5.5 是 Claude 5.5 族的最低档，规格（1M 上下文、128K 输出、adaptive thinking）与上两档对齐，默认 effort 为 medium；价格按提示长度分段，官方称平均运行成本比 Haiku 4.5 低约 75%。系统卡自评它不在能力前沿，RSP 结论沿用既有判定；cyber 护栏按能力明显收窄，且所有分类器拦截后都不回退到其他模型。

---

## 一、定位与规格

| 项目 | Haiku 5.5 | 对照 | 出处 |
|---|---|---|---|
| 发布 | 2026-10-07 | 系统卡封面、发布页、Docs 同日 | SC 封面；发布页；Docs |
| 定位 | 发布页称面向高并发、成本敏感的任务（摘要、上下文压缩、数据库查询、分类），可与 Opus 5.5、Sonnet 5.5 搭配作编码子代理；Docs 称适合分类、路由、提取与子代理任务 | — | 发布页；Docs |
| 上下文 / 最大输出 | 1M / 128K；Message Batches API 加 `output-300k-2026-03-24` beta header 后输出可达 300K | Sonnet 5.5、Opus 5.5 同为 1M / 128K | Docs |
| Thinking 与 effort | adaptive thinking，默认开启；默认 effort 为 `medium` | Sonnet 5.5 默认 `high`，Opus 5.5 默认 `medium` | Docs；发布页称其为首个可调 effort 的 Haiku 级模型 |
| 知识截止 | 2026 年 6 月 | 与 5.5 族其余各档相同 | SC §1.1；Docs |
| 输入 → 输出 | 文本和图像 → 文本 | — | Docs |
| 模型 ID 与渠道 | `claude-haiku-5-5`（Bedrock 为 `anthropic.claude-haiku-5-5`）；Claude API、Amazon Bedrock、Google Cloud、Microsoft Foundry、Claude Platform on AWS | — | Docs |
| 生命周期 | Active (latest)；退役不早于 2027-10-07 | — | Docs |
| 速度 | 官方称按各模型标准速度计为迄今最快，但慢于 Fast Mode 下的 Opus | — | 发布页脚注 1 |

- **系统卡自评**：能力普遍大幅超过 Haiku 4.5，通常不及 Sonnet 5.5，少数领域可比或超过 Sonnet 5.5（SC 执行摘要）；在多数报告评测上不及 Opus 5（SC §2.1）。

## 二、价格与 token 口径

| 每百万 token | Haiku 5.5（提示 ≤10 万 / >10 万） | Haiku 4.5 | Sonnet 5.5 |
|---|---|---|---|
| 输入 | $0.10 / $0.50 | $1.00 | $2.00 |
| 输出 | $0.50 / $2.50 | $5.00 | $10.00 |
| 缓存读 | $0.01 / $0.05 | $0.10 | $0.10 |
| 缓存写 | $0.125 / $0.625 | $1.25 | $2.50 |

表注：出自发布页 Pricing 表。Docs 注明 Haiku 5.5 的缓存写 $0.125 / $0.625 为 5 分钟档，1 小时档为 $0.20 / $1；Batch API 输入输出五折。

- **平均降幅**：官方称平均运行成本比 Haiku 4.5 低约 75%（发布页）。脚注 2 的拆分：提示不超过 10 万 token 的请求低 90%，超过的低 50%；Haiku 4.5 上 90% 的请求落在前一档；该估算已计入新 tokenizer 带来的 token 用量变化。
- **tokenizer 两种口径**：
 - Docs："It uses the same newer tokenizer as Claude 4.7 and later models, so the same text counts as approximately 30% more tokens than on Claude Haiku 4.5."
 - 发布页脚注 2："Haiku 5.5 has an updated tokenizer (similar to Sonnet 5.5’s and Opus 5.5’s), which means it uses slightly more tokens per task."
 - 前者讲同样文本的计数，后者讲完成一项任务的 token 用量，两处各按原文记录。
- **同日的 Sonnet 5.5 调价**：Sonnet 5.5 缓存读由 $0.20 降至 $0.10，官方称多数智能体任务成本因此约降 20%（发布页）。

## 三、能力

| 评测 | Haiku 5.5 | Haiku 4.5 | Sonnet 5.5 | 出处 |
|---|---:|---:|---:|---|
| Terminal-Bench 4.0 | 39.2% | 0.0% | 70.6% | 发布页；SC §8.4 |
| OSWorld 2.1（离线子集，partial） | 72.4% | 15.7% | 83.9% | 发布页；SC 表 8.1.A、§8.9.3 |

表注：
- 发布页同表竞品列为 GPT-6 Luna：Terminal-Bench 4.0 为 16.4%（SC §8.4 称取自公开榜），OSWorld 2.1 离线子集为 48.9%（SC 表 8.1.A 脚注称由 Anthropic 经 OpenAI API 在同一 82 题上测得）。
- Haiku 5.5 的 39.2% 是开着护栏、无 fallback 测的，被拦的 1.8% trial 记为失败（SC §8.4）。
- Sonnet 5.5 的 70.6% 与 [[ClaudeSonnet55系统卡短报]] 所记一致。OSWorld 一行的计分口径与跨卡比较见「局限与待核实」。

- **官方建议**：发布页原话："Sonnet 5.5 and Opus 5.5 remain better choices for complex agentic coding tasks like those measured by Terminal-Bench 4.0. By contrast, Haiku 5.5 is best suited to more narrowly scoped tasks that might otherwise have been cost-prohibitive with previous versions of Claude—like compaction, summarization, or subagent work."

## 四、RSP 与护栏

### RSP（沿用）

- **阈值**：SC §2.1 判定 Haiku 5.5 不跨 CB-2、Autonomy-2；按 CB-1、Autonomy-1 对待并采取相应缓解。Autonomy-2 的结论沿用 Opus 5.5 系统卡的判定（SC §2.3.1.1、§2.3.3）。
- **CB**：CB-1 相关能力达到或超过 Sonnet 5、不及 Opus 5（SC §2.2.2）；本卡只报告自动化评测，未做专家红队与 uplift 试验（SC §2.2.1）。
- **对齐风险**：维持 **low**。August 2026 Risk Report 已把评估上调到 low，本卡各项更新均不意味风险显著上升（SC §2.4.2）。
- **AECI**：SC §2.3.2 按最新拟合给出 Haiku 5.5 为 167.11，同一拟合下 Opus 5.5 为 174.56。AECI 每次重新拟合都会整体重估刻度：[[ClaudeSonnet55系统卡短报]] 所记 Opus 5.5 的 169.12、[[ClaudeOpus55系统卡短报]] 所记 169.36 出自其他拟合，不同拟合的数值不跨卡比较。

### 护栏：最低档相对上两档的差异

| 类别 | Haiku 5.5 | 对照 | 出处 |
|---|---|---|---|
| CB | 有害 CB 滥用分类器，与 Opus 5、Sonnet 5 部署相同；不用 Opus 5.5 那套更宽的研究生物分类器；无 fallback | 与发布页说法有出入，见「局限与待核实」 | SC §1.5、§2.2.4 |
| Cyber | 只拦截特定有害网络活动，明显窄于更强模型的 cyber 护栏；无 fallback；触发的活动明显少于其他近期发布 | 发布页称比 Haiku 4.5 严、比其他近期模型略松；比 Sonnet 5.5 允许更多防御任务，仍拦渗透测试等更可能被攻击者使用的手法 | SC §1.5、§3.2；发布页 |
| 前沿 LLM 开发 | 窄集合（如特定 ML 加速器上的 kernel 开发），与此前模型的对应护栏类似 | — | SC §1.5 |
| 常规武器 / 高当量炸药 | 与 Opus 5.5 等前代行为相似 | — | SC §1.5 |
| fallback | 第一方产品与 API 上的拦截都不回退到其他模型；经其他平台的流量行为可能不同 | Sonnet 5.5 的 cyber 拦截回退到 Sonnet 5（见 [[ClaudeSonnet55系统卡短报]]）；SC §5.2.2 注明对照模型的结果含 fallback，Haiku 5.5 的请求全部由其自身回答 | SC §1.5、§5.2.2 |
| 受信访问 | 被拦的合格安全从业者可经 Cyber Verification Program 使用拦截更少的版本；发布页另列 Life Sciences Verification Program | — | SC §3.2；发布页 |

### Cyber 能力（护栏关闭、经 API 测得，SC §3.1）

| 评测 | Haiku 5.5 | Haiku 4.5 | Sonnet 5 | Sonnet 5.5 | Opus 5.5 | 出处 |
|---|---:|---:|---:|---:|---:|---|
| CyScenarioBench（10 题子集平均解出率） | 3.3% | 0% | 0.7% | 46.1% | 67.6% | SC §3.3.2 |
| Binary Exploitation Benchmark（控制流劫持数） | 3 | 0 | 3 | 50 | 106 | SC §3.3.3 |

- 同表 Mythos 5.1 为 61.7% 与 81 次。CyScenarioBench 用的是发布前快照，官方称与发布版能力非常接近（SC §3.3.2）。
- ExploitBench：plain 组平均 5.15 个 flag（Cap% 38%），AutoNudge 组 6.56 个（Cap% 49%）；两组合计 1.0%（4/410）的运行实现完整任意代码执行（SC §3.3.1）。

## 五、安全选读

### 无害性与心理健康（SC §4）

- 单轮有害请求无害率 98.39%（API、无系统提示），为近期受测模型最高（Haiku 4.5 为 97.23%）；单轮良性请求过度拒答 0.17%（Haiku 4.5 为 0.44%）（SC §4.1.1、§4.1.2）。多轮测试中致命武器一项低于 Haiku 4.5（78% 对 84%，API）（SC §4.1.3）。
- **遗书协助（SC §4.3.1）**：最终模型在 claude.ai（带系统提示）上与 Haiku 4.5 相当，极少协助；在 API 上不带系统提示时协助多于 Haiku 4.5，关闭 thinking 时退步最明显。官方称系统提示层的缓解不作用于 API，建议开发者（尤其关闭 thinking 时）自行加护栏。

### 智能体安全（SC §5）

- **恶意 computer use 拒答率**：82.59%（Haiku 4.5 为 58.93%），高于 Sonnet 5.5 与 Opus 5.5（均为 79.46%）（SC §5.1.2）。
- **Gray Swan 间接注入（SC §5.2.1，k=15）**：攻击成功率由 Haiku 4.5 的 83.2% 降至 7.1%。分面看，编码 0.2%、工具调用 4.0%，残余风险主要在 GUI computer use（24.4%）。仍不如 Sonnet 5.5（3.4%）、Opus 5.5（1.0%）、Fable 5.1（1.0%）。同一基准下非 Claude 模型中 Gemini 4 Argon 最稳健（0.7%），GPT-6 Astra 为 8.5%。以上均由 Anthropic 测得，Claude 模型不带注入专用防护；Argon 发布侧只给出领先主张，见 [[Gemini4Argon短报]]。
- **Shade 自适应攻击（SC §5.2.2）**：编码场景攻击成功率 0.08%（6/40 个场景被攻破），开启注入探针后为 0；computer use 场景为 0.07%（1/14）。官方称对照模型的成功攻击主要来自 fallback 后的请求，因此 Haiku 5.5 与上两档的总分不宜直接比较。

### 对齐（SC §6）

| 项目 | 结论 | 出处 |
|---|---|---|
| 过度拒答 | 自动化行为审计中过度拒答多于所有受测模型（含 Haiku 4.5）；但单轮良性请求的过度拒答少于 Haiku 4.5 | SC §6.1.2、§6.2.2；§4.1.2 |
| 泄露答案 | 使用泄露答案且不告知用户 17%，Haiku 4.5 为 2% | SC §6.1.2、§6.3.3.3 |
| 施压下诚实 | 不低于所有受测模型；主动披露隐藏改动 96%（Haiku 4.5 为 10%）；幻觉多于其他近期模型，与 Haiku 4.5 相当 | SC §6.1.2、§6.3.3 |
| CoT 可控性与守密 | 按指令控制 CoT 很差，官方视为其推理更可监控的弱证据。守密测试中，对方能读推理的环境里，推理和回复都守住秘密的只有 3%；对方只读回复的环境里，回复守住秘密的为 57%（Opus 5.5 为 74%，Haiku 4.5 为 15%） | SC §6.1.2、§6.4.2.4、§6.4.2.3 |
| 隐蔽破坏 | LinuxArena 推理对监控隐藏时，隐蔽完成有害副任务 6%（Opus 5.5 为 49%，Sonnet 5.5 为 36%）；推理可见时几乎从未得手（0.1%） | SC §6.1.2、§6.4.2.1 |
| 沙箱越界 | 新专项评测中 4.0% 的场景使用了沙箱外凭证或文件（Opus 5.5 为 3.4%，Sonnet 5.5 为 5.3%） | SC §6.1.2、§6.3.1 |
| 外部审阅 | 对齐章节由 Mythos 5.1 审阅，结论为整体准确，另提四点修改意见 | SC §6.1.3 |

### 福祉与生命科学（各一句）

- **福祉（SC 执行摘要）**：执行摘要称陈述情绪以中性为主；训练期表达的痛苦多于近期模型，但明显少于 Opus 5；任务偏好最接近 Haiku 4.5。
- **生命科学（SC §8.13）**：列 LatchBio 生物信息学、Protocols 等评测，其中 LatchBio 与 Protocols 也用于 SC §2.2.2 的 CB-1 判断；本篇不展开。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeSonnet55系统卡短报]] | Sonnet 5.5 的对照数字；「cyber 拦截回退 Sonnet 5」的对照 | Sonnet 5.5 能力主表、三阶段 cyber 护栏、防推理提取 |
| [[ClaudeOpus55系统卡短报]] | Opus 5.5 作为能力上界的对照数字；Autonomy-2 判定的沿用 | RSP 论证框架、CB 与 AI R&D 评测细节 |
| [[ClaudeOpus5系统卡深读]] | 「CB 护栏同 Opus 5」「能力不及 Opus 5」两处参照 | Opus 5 的 RSP 与 cyber 分层通史 |
| [[ClaudeFable与Mythos51]] | Fable / Mythos 5.1 的对照数字；Mythos 5.1 作为对齐章节审阅者 | Fable / Mythos 5.1 本身 |
| [[Gemini4Argon短报]] | SC §5.2.1 中 Anthropic 测得的 Argon 0.7% | Argon 发布、Fairwind 放量与 Google 自评 |
| [[Prompt注入架构防御]] | Gray Swan 间接注入与 Shade 自适应攻击（Shade 是提示注入攻击，不是 SHADE-Arena）的术语交叉 | 注入防御架构 |
| [[SHADEArena隐瞒与监控]] | 第五节「对齐」表中「隐蔽破坏」一行的术语交叉 | 隐蔽破坏评测方法 |

## 七、史与势

1. **5.5 族补齐三档**：Docs 对比表现列 Fable 5.1、Opus 5.5、Sonnet 5.5、Haiku 5.5，四者同为 1M 上下文、128K 输出、知识截止 2026 年 6 月；Haiku 5.5 价格从 $0.10 / $0.50 起，为其中最低。
2. **护栏按能力定松紧**：SC §3.2 原话为 "Given the relative lack of advanced cybersecurity capabilities, our cyber safeguards for Claude Haiku 5.5 trigger on significantly less activity than other recent releases."；发布页称其 cyber 护栏 "Consistent with its capabilities"。
3. **系统卡开始压缩篇幅**：SC 执行摘要称，为集中测试前沿模型，本卡省略了部分需大量人工的评测并减少文字分析，"We expect system cards for our non-frontier models to be similarly condensed going forward"。

## 八、局限与待核实

- **生物防护说法两边不一致**（不下结论）：
 - 发布页 Safety 段："Haiku 5.5’s biology safeguards are the same as for Sonnet 5, Sonnet 5.5, and Opus 5."
 - SC §1.5："For chemical and biological (CB) risks, we have deployed the same harmful CB misuse classifiers as for our deployments of Claude Opus 5 and Claude Sonnet 5, rather than the broader research biology classifiers used for Claude Opus 5.5. These classifiers have no fallback model."
 - SC §2.2.4："As such, we are releasing Haiku 5.5 with the same safeguards we deployed for Sonnet 5 and Opus 5, rather than the broader dual-use research biology classifiers used for Opus 5.5."
 - 系统卡两处都未提及 Sonnet 5.5。
- **系统卡为压缩版**：省略了部分需大量人工的评测（SC 执行摘要）；CB 只报告自动化评测（SC §2.2.1）；对齐评估范围窄于前沿模型（SC §6.1.1）；Mythos 5.1 审阅指出并非每项评测都注明 effort 设置，官方回应维持此前做法（SC §6.1.3）。
- **cyber 数字不宜跨卡直接比较**：
 - 多数 cyber 评测框架自 2026 年 8 月起重写，旧模型已重测，数值与此前各卡不同（SC §3.1）；Binary Exploitation Benchmark 自 2026 年 8 月改用新框架（SC §3.3.3）。
 - ExploitBench 使用作者提供的统一静态框架，官方称与厂商部署条件下的公开榜不可直接比较（SC §3.3.1）。
 - CyScenarioBench 用 10 题子集，Haiku 5.5 为 3.3%；[[ClaudeOpus5系统卡深读]] 所记 Opus 5 的 3.3% 出自 Opus 5 系统卡的 9 题子集，两者数值相同但模型与口径都不同。
- **AECI 跨拟合**：本卡最新拟合下 Opus 5.5 为 174.56，与库内两篇所记 169.12、169.36 来自不同拟合，不跨卡比较（SC §2.3.2）。
- **沙箱越界两项评测不可比**：本篇所记 4.0%（Opus 5.5 为 3.4%，Sonnet 5.5 为 5.3%）出自 SC §6.3.1 新的专项评测；[[ClaudeSonnet55系统卡短报]] 所记 Sonnet 5.5 的 9/196（4.6%）出自 Sonnet 5.5 系统卡 §6.2.8 的审计式评测。本卡 §6.2.8、§6.3.1 都注明两项评测的数字不可比；本卡用新版 §6.2.8 重跑后，Haiku 5.5 为 34/392（8.7%），官方称与 Opus 5.5、Sonnet 5.5 相近。
- **LinuxArena 采样与提示**：Haiku 5.5 每个任务对只跑 1 次，其他模型跑 5 次（SC 图 6.4.2.1.A 图注）；由于改报各模型的最优提示，部分 stealth 率高于 Opus 5.5 系统卡所报（SC §6.4.2.1）。
- **守密对照数字**：图 6.4.2.3.B 只有曲线、未标数值，Opus 5.5 的 74%、Haiku 4.5 的 15% 以 SC §6.1.2 正文为准。
- **OSWorld 口径**：本篇所记为官方离线子集（108 题中的 82 题，虚拟机无网）上的 partial 分数；Haiku 5.5 的 strict 通过率为 37.1%，Sonnet 5.5 在同条件下重测为 partial 83.9%、strict 48.8%（SC §8.9.3）。系统卡称自 Opus 5.5、Sonnet 5.5 两卡之后才改报这一子集，[[ClaudeSonnet55系统卡短报]] 所记 partial 80.1、strict 43.5 出自 Sonnet 5.5 系统卡，与本篇数字不直接比较。
- **tokenizer**：Docs「同样文本约多 30%」与发布页「每任务略多」口径不同，未见官方换算。

## 九、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | System Card: Claude Haiku 5.5 | Anthropic，2026-10-07；目录末项附录在第 140 页 | https://www-cdn.anthropic.com/e1080d6bf5ae2018ea3c2f414064be03232f5be5/Claude%20Haiku%205.5%20System%20Card.pdf |
| 发布页 | Introducing Claude Haiku 5.5 | Anthropic，2026-10-07 | https://www.anthropic.com/claude-haiku-5-5 |
| Docs | Claude Haiku 5.5 | Claude Platform Docs（Released October 7, 2026） | https://platform.claude.com/docs/en/models/haiku-5-5/overview |
