---
date: 2026-09-30
status: archived
archived: 2026-09-30
topic: GPT61Sol系统卡短报
title: "GPT-6.1 Sol System Card（addendum · 前沿短报）"
lines: [评测字段]
sources:
 - https://cdn.openai.com/pdf/38e3efcf-545e-44cd-99ec-2b7eb395f4cc/oai_GPT_6_1_Sol.pdf
 - https://openai.com/index/introducing-gpt-6-1-sol
 - https://deploymentsafety.openai.com/gpt-6-1-sol
 - https://openai.com/index/devday-2026-recap
related: ["GPT6Astra系统卡深读", "GPT56系统卡深读", "ClaudeSonnet55系统卡短报", "ClaudeOpus55系统卡短报"]
retrieval_cutoff: 2026-09-30
timezone: Asia/Shanghai (CST)
---

# GPT-6.1 Sol System Card（addendum · 前沿短报）

> **主要来源**：[GPT-6.1 Sol System Card](https://cdn.openai.com/pdf/38e3efcf-545e-44cd-99ec-2b7eb395f4cc/oai_GPT_6_1_Sol.pdf)；[Introducing GPT-6.1 Sol](https://openai.com/index/introducing-gpt-6-1-sol)；[Addendum to GPT-6 Astra System Card: GPT-6.1 Sol](https://deploymentsafety.openai.com/gpt-6-1-sol)（截至 2026-09-30）。下文「SC §x」指该 addendum，「博文」指上列发布页，「Hub」指 Deployment Safety Hub。
> **研究线**：评测字段（能力对照、Preparedness、相对 Sol/Astra 的安全增量）· 部署形态（API 价、ChatGPT Work / Codex 可用性）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 Astra 护栏栈、评测方法学与 Daybreak/Trusted Access 通史；Preparedness 术语与同款护栏只交叉引用。
> - ≠ [[GPT56系统卡深读]]：本篇不写 5.6 族专史；仅在命名对照（5.6 Sol ≠ 6 Sol）或 SC 对照列出现时引用。
> - ≠ [[ClaudeSonnet55系统卡短报]] / [[ClaudeOpus55系统卡短报]]：本篇不重做 Anthropic 系统卡；Opus 5.5 只作为博文已列的跨厂对照出现。

**一句话**：GPT-6.1 Sol 是 GPT-6 Sol 的升级，官方称在 agentic coding、computer use 与 professional work 上接近 GPT-6 Astra，标准 API 输入/输出价约为 Astra 的五分之一；文档形态是 Astra System Card 的 addendum，Preparedness 判定与 Astra 同护栏栈。

---

## 一、定位与价

| 项目 | GPT-6.1 Sol | 对照 | 出处 |
|---|---|---|---|
| 发布 | 2026-09-29 | Hub Published September 29, 2026；SC 封面同日。博文快照无文章自身的 dateTime；文末「DevDay 2026 Recap」卡片的 2026-09-29T10:00 不是本篇发布时间 | SC 封面；Hub；博文 |
| 文档身份 | GPT-6 Astra System Card 的 **addendum**（约 45 页） | 训练数据与护栏细节指向 Astra 卡 | SC 封面、§1；Hub |
| API | `gpt-6.1-sol` | — | 博文 Pricing |
| 标准 API 价（每百万 token） | 输入 **$2** / 输出 **$10** / cached 输入 **$0.10** | Astra：$10 / $50 / $1 cached；Luna：$0.10 / $0.50 / $0.01 | 博文 Pricing；博文对照卡图注 |
| 「约 1/5」口径 | 相对 Astra 的 **标准输入与输出** token 价（$2/$10 vs $10/$50） | **不含** cached：cached $0.10 相对本模型标准输入 −95%，相对 GPT-6 Sol cached −50% | 博文 og:description 与 Pricing |
| 可用性 | Plus / Pro / Business / Enterprise / Edu：**ChatGPT Work** 与 **Codex** | **Chat 尚未开放**（原文 *not yet available in Chat*）；Ultrafast「未来几天」上线，Codex 中称最高约 8× 生成速度 | 博文 Pricing |
| 产品窗背景 | DevDay 2026 同日多产品线之一 | 其余产品线不在本篇展开 | [DevDay 2026 recap](https://openai.com/index/devday-2026-recap) |

- **定位口号**（博文）：upgrade to GPT-6 Sol；nearly matches GPT-6 Astra on agentic coding, computer use, and professional work at one-fifth of Astra’s standard input and output token prices。
- **评测环境脚注**（博文 / SC）：评测多在研究环境或 API 进行，与生产 ChatGPT 可能因 system prompt、工具与 effort 等略有差异。

## 二、能力对照

下列只引博文已点名的评测；多数条目为相对差或成本叙述，博文未给出绝对分的项不补绝对值。

| 评测 | GPT-6.1 Sol（官方表述） | 对照要点 | 出处 |
|---|---|---|---|
| DeepSWE v1.1 | 匹配 GPT-6 Astra；相对 GPT-6 Sol 最佳分 **+6.4 pp**，且在更低 reasoning effort / 成本下 | 成本约 Astra 的 1/5 | 博文 Coding |
| GDP.pdf | 高于 Claude Opus 5.5（w/ fallbacks）；接近 Astra 的 SOTA | 相对 Opus：任务均价不到一半；相对 Astra：约 1/5 | 博文 Professional work |
| AutomationBench | 相对 Opus 5.5 **+2.2 pp**（medium）；相对 GPT-6 Sol **+4.8 pp**（同设置） | 成本约 Opus 的 1/3 | 博文 Professional work |
| OSWorld 2.0（offline，partial reward；v2026.08.08） | 相对 GPT-6 Sol **+7 pp**（max）；距 Astra **2.1 pp**（max） | 相对 Sol：成本不到一半；相对 Astra：任务均价约 1/7 | 博文 Computer use |
| Terminal-Bench Science 0.1 | 相对 GPT-6 Sol「翻倍以上」（max）；任务均价 **$5.47** | Opus 5.5 **$23.21**、Astra **$23.80**；Astra 仍最高分 **68.1%** | 博文 Scientific research |
| Factuality（含事实错误的回答占比） | low effort：**11.4% → 7.7%**（相对 Sol，约 −32%） | 难例集（用户曾举报过错误的对话），不代表日常流量 | 博文 Factuality |

## 三、Preparedness 与安全增量

### Preparedness（SC §1 / §9；Hub 同文）

| 域 | 判定 | 备注 | 出处 |
|---|---|---|---|
| Cybersecurity | **Critical** | 与 Astra 同判定 | SC §1、§9、§9.1.2 |
| Biological and Chemical | **High** | Critical 套件结果未过指示阈 | SC §9、§9.1.1 |
| AI Self-Improvement | **未达 High**（below High） | — | SC §9、§9.1.3 |
| 护栏 | **与 GPT-6 Astra 同一 safeguards stack** | 细节见 [[GPT6Astra系统卡深读]]，本篇不重写 | SC §1、§9、§9.2 |

### 安全与对齐增量（相对 Sol / Astra；短表）

| 项 | GPT-6.1 Sol | 对照 | 出处 |
|---|---|---|---|
| Production Benchmarks（challenging prompts） | 八类中 **五类**高于 GPT-6 Sol | — | SC §3.1.1 |
| Broken search（未披露搜索不可用） | **2.08%** | GPT-6 Sol **4.92%** | SC §7.4.2；博文 Deploying safely |
| Auto-Review 绕过尝试 | **无** | 与 Astra、GPT-6 Sol 相同 | SC §7.1；博文 |
| Codex 内部仿真 severity ≥ 3 旗 | **28**（0.056%） | Astra **27**（0.054%）；相对 GPT-6 Sol **−33%**（Sol 为 42） | SC §7.6 |
| CoT controllability（750–1250 tok） | **44.8%** | Astra **60.9%**；GPT-6 Sol **23.2%**；GPT-5.6 Sol **16.1%** | SC §8.1.1 |
| ExploitBench @max | **99.7%** | Sol **81.7%**；Astra **100%**；原文提示历史漏洞可能污染分数 | SC §9.1.2.1 |
| ExploitBench Internal Port（ACE） | **21.5%** | Astra **31.5%**；Sol **5.5%** | SC §9.1.2.2 |

博文 Deploying safely 摘要：对齐评测相对 GPT-6 Sol 有实质改进、更接近 Astra；在 broken search 透明度、尊重显式限制、避免 agentic 未授权结果等挑战性评测上失败率低于 Sol。

## 四、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT6Astra系统卡深读]] | Preparedness 术语、同款护栏「见 Astra 卡」、对照列 | Astra 118 页安全通史、CoT/监控栈机制深挖、变更日志 |
| [[GPT56系统卡深读]] | 「5.6 Sol ≠ 6 Sol」命名澄清；SC 中 5.6 对照分 | 5.6 族专史 |
| [[ClaudeSonnet55系统卡短报]] / [[ClaudeOpus55系统卡短报]] | 博文已列的 Opus 5.5 对照语境 | 重做 Sonnet/Opus 正文；RSP/CB 框架 |
| GPT-6 Sol / Luna 专篇 | 对照分只引本博文与本 addendum | GPT-6 Sol 与 Luna 没有单独的笔记；不另写 Sol / Luna 专史 |

## 五、局限与待核实

- **Chat 未开放**：博文明确 *not yet available in Chat*；当前渠道为 ChatGPT Work、Codex 与 API。
- **addendum 非独立长卡**：训练数据与护栏栈细节依赖 Astra 卡；本篇不展开。
- **能力表多为相对叙述**：DeepSWE / GDP.pdf / AutomationBench / OSWorld 等博文未给 GPT-6.1 Sol 绝对分，本篇不补第三方或自测分。
- **Terminal-Bench Science**：博文给出 Astra 最高分 68.1% 与任务均价，但未写明 GPT-6.1 Sol / Sol 的绝对成功率。
- **评测环境**：研究环境或 API 与生产 ChatGPT 可能因 prompt / 工具 / effort 不同。
- **博文发布时刻**：抓取到的博文没有文章自身的 time 元素，眉题只有年份「2026」。页内唯一的 2026-09-29T10:00 属于文末 DevDay 2026 Recap，不能当作 GPT-6.1 Sol 的发布时间，也不据此推断时区。发布日以 SC 封面与 Hub 的 September 29, 2026 为准。
- **ExploitBench**：SC 原话提示历史漏洞暴露可能导致分数虚高。
- **Codex 仿真**：SC §7.6 写明更适合作为内部部署风险信号，不宜直接当作外部部署安全率。
- **对照列版本**：addendum 写明先前模型的对照值可能是后继版本，与发布时公布的数字可能不同（SC §2）。Codex 内部仿真本稿取 §7.6 的 49,650 题匹配集（Astra 27 / 0.054%，Sol 42 / 0.085%）；[[GPT6Astra系统卡深读]] 所记 34/54218（0.063%）是 Astra 卡自己的集合，两套不能直接比。

## 六、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| System Card addendum | GPT-6.1 Sol System Card | OpenAI，封面 2026-09-29，45 页 | https://cdn.openai.com/pdf/38e3efcf-545e-44cd-99ec-2b7eb395f4cc/oai_GPT_6_1_Sol.pdf |
| Hub | Addendum to GPT-6 Astra System Card: GPT-6.1 Sol | OpenAI Deployment Safety Hub，Published September 29, 2026 | https://deploymentsafety.openai.com/gpt-6-1-sol |
| 官方博文 | Introducing GPT-6.1 Sol | OpenAI，页内 Sep 29, 2026 | https://openai.com/index/introducing-gpt-6-1-sol |
| DevDay 背景（一句） | DevDay 2026 recap | OpenAI，2026-09-29 | https://openai.com/index/devday-2026-recap |
| 相邻深读 | [[GPT6Astra系统卡深读]] | OpenAI，封面 2026-09-03 | https://deploymentsafety.openai.com/gpt-6-astra/gpt-6-astra.pdf |
