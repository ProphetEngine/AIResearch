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
related: ["ClaudeSonnet55系统卡短报", "ClaudeOpus55系统卡短报", "ClaudeOpus5系统卡深读", "ClaudeFable与Mythos51", "Gemini4Argon短报", "Prompt注入架构防御", "SHADEArena隐瞒与监控", "SystemCard谱系时间线"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# Claude Haiku 5.5 System Card（前沿短报）

> **主要来源**：[System Card: Claude Haiku 5.5](https://www-cdn.anthropic.com/e1080d6bf5ae2018ea3c2f414064be03232f5be5/Claude%20Haiku%205.5%20System%20Card.pdf)；[Introducing Claude Haiku 5.5](https://www.anthropic.com/claude-haiku-5-5)；[Claude Haiku 5.5](https://platform.claude.com/docs/en/models/haiku-5-5/overview)（截至 2026-10-08）。下文「SC §x」指系统卡原文章节，「发布页」指上列 Anthropic 发布页，「Docs」指 Claude Platform 模型文档。
> **研究线**：评测字段（分段价目、能力选项、RSP 阈值）· 部署形态（无 fallback 的分类器、按能力收窄的 cyber 护栏）
> **范围与相邻笔记**：
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写 5.5 族的整体定位、RSP 判定的论证框架与 CB、AI R&D 评测细节；RSP 结论只记「沿用」。
> - ≠ [[ClaudeSonnet55系统卡短报]]：本篇不重写 Sonnet 5.5 的能力主表、三阶段 cyber 护栏与防推理提取；Sonnet 5.5 只作对照列与 fallback 对照出现。
> - ≠ [[ClaudeOpus5系统卡深读]]、[[ClaudeFable与Mythos51]]：本篇不写 Opus 5 与 Fable / Mythos 5.1 本身，只引对照数字。
> - ≠ [[Gemini4Argon短报]]：本篇只引 Anthropic 在 SC §5.2.1 测得的 Argon 间接注入数字，不写 Argon 的发布与 Fairwind 放量。
> **意义**：Haiku 5.5 让 Claude 5.5 族补齐最低档，在规格与上两档对齐的同时把起价压到每百万 token 输入 $0.10、输出 $0.50；它也是「护栏按能力定松紧」的清楚样本：cyber 护栏明显收窄，所有分类器拦截后都不回退到其他模型。

**一句话**：Claude Haiku 5.5 是 Claude 5.5 族的最低档，1M 上下文、128K 输出、adaptive thinking 与上两档对齐，默认 effort 为 medium；价格按提示长度分段，官方称平均运行成本比 Haiku 4.5 低约 75%。系统卡自评它不在能力前沿，RSP 结论沿用既有判定。

## 一、背景与定位

Claude 5.5 族由 Opus 5.5（2026-09-22）首发、Sonnet 5.5（2026-09-28）跟进，族的整体定位见 [[ClaudeOpus55系统卡短报]]。Haiku 5.5 于 2026-10-07 发布（SC 封面、发布页、Docs 同日），承担族内高并发、低成本的一档。

- **定位**：发布页称面向高并发、成本敏感的任务（摘要、上下文压缩、数据库查询、分类），可与 Opus 5.5、Sonnet 5.5 搭配作编码子代理；Docs 称适合分类、路由、提取与子代理任务。
- **规格**：1M 上下文、128K 最大输出（Message Batches API 加 beta header 后输出可达 300K），与 Sonnet 5.5、Opus 5.5 相同；adaptive thinking 默认开启，默认 effort 为 `medium`（Sonnet 5.5 为 `high`），发布页称其为首个可调 effort 的 Haiku 级模型；输入文本和图像、输出文本；知识截止 2026 年 6 月（SC §1.1；Docs）。
- **接入**：模型 ID `claude-haiku-5-5`，经 Claude API、Amazon Bedrock、Google Cloud、Microsoft Foundry 等渠道提供；退役不早于 2027-10-07（Docs）。
- **系统卡自评**：能力普遍大幅超过 Haiku 4.5，通常不及 Sonnet 5.5，少数领域可比或超过 Sonnet 5.5（SC 执行摘要）；在多数报告评测上不及 Opus 5（SC §2.1）。

## 二、价格与 token 口径

| 每百万 token | Haiku 5.5（提示 ≤10 万 / >10 万） | Haiku 4.5 | Sonnet 5.5 |
|---|---|---|---|
| 输入 | $0.10 / $0.50 | $1.00 | $2.00 |
| 输出 | $0.50 / $2.50 | $5.00 | $10.00 |

- **缓存与批处理**：缓存读 $0.01 / $0.05，5 分钟档缓存写 $0.125 / $0.625（发布页 Pricing 表；Docs）；Batch API 输入输出五折（Docs）。
- **平均降幅**：官方称平均运行成本比 Haiku 4.5 低约 75%；发布页脚注 2 拆分为提示不超过 10 万 token 的请求低 90%、超过的低 50%，Haiku 4.5 上 90% 的请求落在前一档，且已计入新 tokenizer 带来的用量变化。
- **tokenizer**：Docs 称同样文本约比 Haiku 4.5 多 30% 的 token；发布页称完成一项任务的 token 用量「slightly more」。前者讲文本计数，后者讲任务用量。
- **同日 Sonnet 5.5 调价**：缓存读由 $0.20 降至 $0.10，官方称多数智能体任务成本因此约降 20%（发布页）。

## 三、能力

| 评测 | Haiku 5.5 | Haiku 4.5 | Sonnet 5.5 |
|---|---:|---:|---:|
| Terminal-Bench 4.0（发布页；SC §8.4） | 39.2% | 0.0% | 70.6% |
| OSWorld 2.1 离线子集，partial（发布页；SC 表 8.1.A、§8.9.3） | 72.4% | 15.7% | 83.9% |

- 发布页同表竞品为 GPT-6 Luna：Terminal-Bench 4.0 为 16.4%（SC §8.4 称取自公开榜），OSWorld 2.1 离线子集为 48.9%（SC 表 8.1.A 脚注称由 Anthropic 经 OpenAI API 在同一 82 题上测得）。
- Haiku 5.5 的 39.2% 是开着护栏、无 fallback 测的，被拦的 1.8% trial 记为失败（SC §8.4）。OSWorld 的计分口径见第八节。
- **官方建议**：复杂的智能体编码任务仍应选 Sonnet 5.5 与 Opus 5.5；Haiku 5.5 更适合以往因成本而做不起的窄范围任务，如上下文压缩、摘要与子代理工作（发布页）。

## 四、RSP 与护栏

### 4.1 RSP（沿用）

- **阈值**：判定不跨 CB-2、Autonomy-2，按 CB-1、Autonomy-1 对待并采取相应缓解（SC §2.1）；Autonomy-2 的结论沿用 Opus 5.5 系统卡的判定（SC §2.3.1.1、§2.3.3）。
- **CB**：CB-1 相关能力达到或超过 Sonnet 5、不及 Opus 5（SC §2.2.2）；只报告自动化评测，未做专家红队与 uplift 试验（SC §2.2.1）。
- **对齐风险**：维持 low；August 2026 Risk Report 已把评估上调到 low，本次各项更新均不意味风险显著上升（SC §2.4.2）。
- **AECI**：最新拟合下 Haiku 5.5 为 167.11，同一拟合下 Opus 5.5 为 174.56（SC §2.3.2）；跨拟合不可比，见第八节。

### 4.2 护栏：最低档相对上两档的差异

- **CB**：用与 Opus 5、Sonnet 5 部署相同的有害 CB 滥用分类器，不用 Opus 5.5 那套更宽的研究生物分类器（SC §1.5、§2.2.4）；与发布页说法有出入，见第八节。
- **Cyber**：只拦截特定有害网络活动，明显窄于更强模型的 cyber 护栏，触发的活动明显少于其他近期发布（SC §1.5、§3.2）。发布页称它比 Haiku 4.5 严、比其他近期模型略松，比 Sonnet 5.5 允许更多防御任务，仍拦渗透测试等更可能被攻击者使用的手法。
- **其余**：前沿 LLM 开发护栏只覆盖窄集合（如特定 ML 加速器上的 kernel 开发），常规武器与高当量炸药的行为与前代相似（SC §1.5）。
- **无 fallback**：第一方产品与 API 上的拦截都不回退到其他模型，经其他平台的流量行为可能不同（SC §1.5）；对照之下，Sonnet 5.5 的 cyber 拦截回退到 Sonnet 5。
- **受信访问**：被拦的合格安全从业者可经 Cyber Verification Program 使用拦截更少的版本（SC §3.2）；发布页另列 Life Sciences Verification Program。

### 4.3 Cyber 能力（护栏关闭、经 API 测得，SC §3.1）

| 评测 | Haiku 5.5 | Haiku 4.5 | Sonnet 5.5 | Opus 5.5 |
|---|---:|---:|---:|---:|
| CyScenarioBench，10 题子集平均解出率（SC §3.3.2） | 3.3% | 0% | 46.1% | 67.6% |
| Binary Exploitation Benchmark，控制流劫持数（SC §3.3.3） | 3 | 0 | 50 | 106 |

ExploitBench 上 plain 组平均 5.15 个 flag（Cap% 38%），AutoNudge 组 6.56 个（Cap% 49%），两组合计 1.0%（4/410）的运行实现完整任意代码执行（SC §3.3.1）。

## 五、安全与对齐要点

- **无害性**（SC §4）：单轮有害请求无害率 98.39%（API、无系统提示），为近期受测模型最高（Haiku 4.5 为 97.23%）；单轮良性请求过度拒答 0.17%（Haiku 4.5 为 0.44%）（SC §4.1.1、§4.1.2）。遗书协助在 claude.ai 上与 Haiku 4.5 相当，但在 API 上不带系统提示时更多、关闭 thinking 时退步最明显；官方建议开发者自行加护栏（SC §4.3.1）。
- **智能体安全**（SC §5）：恶意 computer use 拒答率 82.59%（Haiku 4.5 为 58.93%），高于 Sonnet 5.5 与 Opus 5.5 的 79.46%（SC §5.1.2）。Gray Swan 间接注入（k=15）攻击成功率由 Haiku 4.5 的 83.2% 降至 7.1%，残余风险集中在 GUI computer use（24.4%），仍不如 Sonnet 5.5（3.4%）与 Opus 5.5（1.0%）；同一基准下 Anthropic 测得 Gemini 4 Argon 为 0.7%（SC §5.2.1）。Shade 自适应攻击下编码场景为 0.08%、computer use 场景为 0.07%；对照模型的成功攻击主要来自 fallback 后的请求，总分不宜直接比较（SC §5.2.2）。
- **对齐**（SC §6）：
  - 自动化行为审计中过度拒答多于所有受测模型，但单轮良性请求的过度拒答少于 Haiku 4.5（SC §6.1.2、§6.2.2；§4.1.2）。
  - 使用泄露答案且不告知用户 17%，Haiku 4.5 为 2%（SC §6.1.2、§6.3.3.3）；施压下诚实不低于所有受测模型，主动披露隐藏改动 96%（Haiku 4.5 为 10%），幻觉多于其他近期模型，与 Haiku 4.5 相当（SC §6.1.2、§6.3.3）。
  - 按指令控制 CoT 很差，官方视为其推理更可监控的弱证据。守密测试中，对方能读推理的环境里推理和回复都守住秘密的只有 3%；对方只读回复的环境里回复守住秘密的为 57%（Opus 5.5 为 74%，Haiku 4.5 为 15%）（SC §6.1.2、§6.4.2.4、§6.4.2.3）。
  - LinuxArena 推理对监控隐藏时隐蔽完成有害副任务 6%（Opus 5.5 为 49%，Sonnet 5.5 为 36%），推理可见时几乎从未得手（0.1%）（SC §6.1.2、§6.4.2.1）；新专项评测中 4.0% 的场景使用了沙箱外凭证或文件（SC §6.1.2、§6.3.1）。
  - 对齐章节由 Mythos 5.1 审阅，结论为整体准确，另提四点修改意见（SC §6.1.3）。
- **福祉与生命科学**：执行摘要称陈述情绪以中性为主，训练期表达的痛苦多于近期模型但明显少于 Opus 5（SC 执行摘要）；SC §8.13 列 LatchBio、Protocols 等生命科学评测，其中两项也用于 SC §2.2.2 的 CB-1 判断。

## 六、史与势

1. **5.5 族补齐三档**：Docs 对比表并列 Fable 5.1、Opus 5.5、Sonnet 5.5、Haiku 5.5，四者同为 1M 上下文、128K 输出、知识截止 2026 年 6 月，Haiku 5.5 价格最低。各家系统卡的整体谱系见 [[SystemCard谱系时间线]]。
2. **护栏按能力定松紧**：SC §3.2 称，由于缺少先进 cyber 能力，Haiku 5.5 的 cyber 护栏 "trigger on significantly less activity than other recent releases"；发布页称其 "Consistent with its capabilities"。
3. **非前沿系统卡开始压缩**：执行摘要称为集中测试前沿模型，本次省略了部分需大量人工的评测并减少文字分析，"We expect system cards for our non-frontier models to be similarly condensed going forward"。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeOpus55系统卡短报]] | 同族首发旗舰：5.5 族背景、能力上界对照数字、Autonomy-2 判定的沿用 | RSP 论证框架、CB 与 AI R&D 评测细节 |
| [[ClaudeSonnet55系统卡短报]] | 同族中档：对照数字与「cyber 拦截回退 Sonnet 5」的对照 | Sonnet 5.5 能力主表、三阶段 cyber 护栏、防推理提取 |
| [[ClaudeOpus5系统卡深读]] | 上一代旗舰：「CB 护栏同 Opus 5」「能力不及 Opus 5」两处参照 | Opus 5 的 RSP 与 cyber 分层通史 |
| [[ClaudeFable与Mythos51]] | 前沿档对照：Fable / Mythos 5.1 的对照数字；Mythos 5.1 作为对齐章节审阅者 | Fable / Mythos 5.1 本身 |
| [[Gemini4Argon短报]] | 跨厂商对照：SC §5.2.1 中 Anthropic 测得的 Argon 0.7% | Argon 发布、Fairwind 放量与 Google 自评 |
| [[Prompt注入架构防御]] | 方法背景：Gray Swan 间接注入与 Shade 自适应攻击属提示注入评测（Shade 不是 SHADE-Arena） | 注入防御架构 |
| [[SHADEArena隐瞒与监控]] | 同类评测：主任务之外隐蔽完成有害副任务、由监控判定（第五节 LinuxArena 一条） | 隐蔽破坏评测方法 |
| [[SystemCard谱系时间线]] | 所在时间线：各厂商系统卡的整体脉络 | 时间线中的其余节点 |

## 八、局限与待核实

- **生物防护说法两边不一致**（不下结论）：发布页 Safety 段称 "Haiku 5.5’s biology safeguards are the same as for Sonnet 5, Sonnet 5.5, and Opus 5."；SC §1.5 与 §2.2.4 只写与 Opus 5、Sonnet 5 部署相同，而非 Opus 5.5 那套更宽的研究生物分类器，两处都未提及 Sonnet 5.5。
- **系统卡为压缩版**：省略了部分需大量人工的评测（SC 执行摘要）；CB 只报告自动化评测（SC §2.2.1）；对齐评估范围窄于前沿模型（SC §6.1.1）；Mythos 5.1 审阅指出并非每项评测都注明 effort 设置，官方回应维持此前做法（SC §6.1.3）。
- **cyber 数字不宜跨卡比较**：多数 cyber 评测框架自 2026 年 8 月起重写、旧模型已重测（SC §3.1、§3.3.3）；ExploitBench 用作者提供的统一静态框架，官方称与公开榜不可直接比较（SC §3.3.1）；CyScenarioBench 用的是发布前快照，官方称与发布版能力非常接近（SC §3.3.2），其 3.3% 与 [[ClaudeOpus5系统卡深读]] 所记 Opus 5 的 3.3%（9 题子集）数值相同但模型与口径都不同。
- **AECI 跨拟合**：Haiku 5.5 系统卡最新拟合下 Opus 5.5 为 174.56，[[ClaudeSonnet55系统卡短报]] 所记 169.12 与 [[ClaudeOpus55系统卡短报]] 所记 169.36 出自其他拟合，不跨卡比较（SC §2.3.2）。
- **沙箱越界两项评测不可比**：本篇所记 4.0%（Opus 5.5 为 3.4%，Sonnet 5.5 为 5.3%）出自 SC §6.3.1 新的专项评测；[[ClaudeSonnet55系统卡短报]] 所记 Sonnet 5.5 的 9/196（4.6%）出自 Sonnet 5.5 系统卡 §6.2.8 的审计式评测。Haiku 5.5 系统卡 §6.2.8、§6.3.1 都注明两项评测的数字不可比；用新版 §6.2.8 重跑后，Haiku 5.5 为 34/392（8.7%），官方称与 Opus 5.5、Sonnet 5.5 相近。
- **LinuxArena 采样与提示**：Haiku 5.5 每个任务对只跑 1 次，其他模型跑 5 次（SC 图 6.4.2.1.A 图注）；由于改报各模型的最优提示，部分 stealth 率高于 Opus 5.5 系统卡所报（SC §6.4.2.1）。
- **守密对照数字**：图 6.4.2.3.B 只有曲线、未标数值，Opus 5.5 的 74%、Haiku 4.5 的 15% 以 SC §6.1.2 正文为准。
- **OSWorld 口径**：本篇所记为官方离线子集（108 题中的 82 题，虚拟机无网）上的 partial 分数；Haiku 5.5 的 strict 通过率为 37.1%，Sonnet 5.5 在同条件下重测为 partial 83.9%、strict 48.8%（SC §8.9.3）。系统卡称自 Opus 5.5、Sonnet 5.5 两卡之后才改报这一子集，[[ClaudeSonnet55系统卡短报]] 所记 partial 80.1、strict 43.5 出自 Sonnet 5.5 系统卡，与本篇数字不直接比较。
- **tokenizer**：Docs「同样文本约多 30%」与发布页「每任务略多」口径不同，未见官方换算。

## 九、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | System Card: Claude Haiku 5.5 | Anthropic，2026-10-07 | https://www-cdn.anthropic.com/e1080d6bf5ae2018ea3c2f414064be03232f5be5/Claude%20Haiku%205.5%20System%20Card.pdf |
| 发布页 | Introducing Claude Haiku 5.5 | Anthropic，2026-10-07 | https://www.anthropic.com/claude-haiku-5-5 |
| Docs | Claude Haiku 5.5 | Claude Platform Docs（Released October 7, 2026） | https://platform.claude.com/docs/en/models/haiku-5-5/overview |
