---
date: 2026-09-30
status: archived
archived: 2026-09-30
topic: GPT61Sol系统卡短报
title: "GPT-6.1 Sol System Card（addendum · 前沿短报）"
lines: [评测字段]
sources:
 - https://deploymentsafety.openai.com/gpt-6-1-sol
 - https://openai.com/index/introducing-gpt-6-1-sol
 - https://openai.com/index/devday-2026-recap
 - https://deploymentsafety.openai.com/gpt-6-astra
 - https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925
related: ["GPT6Astra系统卡深读", "GPT56系统卡深读", "GPT6SolLuna十月版系统卡短报", "ClaudeSonnet55系统卡短报", "ClaudeOpus55系统卡短报"]
retrieval_cutoff: 2026-09-29
timezone: Asia/Shanghai (CST)
---

# GPT-6.1 Sol System Card（addendum · 前沿短报）

> **主要来源**：[Addendum to GPT-6 Astra System Card: GPT-6.1 Sol](https://deploymentsafety.openai.com/gpt-6-1-sol)；[Introducing GPT-6.1 Sol](https://openai.com/index/introducing-gpt-6-1-sol)（截至 2026-09-29）。下文「该卡 §x」指 Deployment Safety Hub 上的这份 addendum，「博文」指上列发布页。
> **研究线**：评测字段（能力对照、Preparedness、相对 GPT-6 Sol 与 Astra 的安全增量）· 部署形态（API 价、ChatGPT Work 与 Codex 可用性）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 Astra 护栏栈、评测方法学与 Daybreak/Trusted Access 通史；Preparedness 术语与同款护栏只交叉引用。
> - ≠ [[GPT56系统卡深读]]：本篇不写 5.6 族专史；仅在命名对照（5.6 Sol ≠ 6 Sol）或该卡对照列出现时引用。
> - ≠ [[GPT6SolLuna十月版系统卡短报]]：本篇不写 GPT-6 Sol 与 Luna 此后版本的系统卡。
> - ≠ [[ClaudeSonnet55系统卡短报]]：本篇不写 Anthropic 系统卡。
> - ≠ [[ClaudeOpus55系统卡短报]]：本篇不写 Opus 5.5 系统卡；Opus 5.5 只作为博文已列的跨厂对照出现。
>
> **意义**：GPT-6.1 Sol 是一个价位低于旗舰的模型，却与 GPT-6 Astra 取得相同的 Preparedness 判定（网安 Critical），因此直接套用 Astra 的整套护栏；该卡也延续了 OpenAI 用短增补而非独立长卡记录同代迭代的做法。

**一句话**：GPT-6.1 Sol 是 GPT-6 Sol 的升级，官方称在 agentic coding、computer use 与 professional work 上接近 GPT-6 Astra，标准 API 输入、输出价约为 Astra 的五分之一；文档形态是 Astra System Card 的 addendum，Preparedness 判定与护栏栈都与 Astra 相同。

---

## 一、背景与脉络

GPT-6 家族按能力与价位分档：Astra 是旗舰，Sol 与 Luna 是更快、更便宜的两档，官方称它们建立在 Astra 的进展之上，把 Astra 的大部分长处带进可规模化使用的模型（GPT-6 Sol 与 Luna 社区公告）。Astra 在网安上被判为 Critical 之后，较低价位的模型一旦能力逼近 Astra，就要回答是否也要按 Critical 处理、套用同一套护栏。GPT-6.1 Sol 是这一问题的第一个实例：该卡称它的能力与 Astra 相当，速度与价格更有优势（§1）。它在 DevDay 2026 当天随其他产品线一起发布。

| 日期 | 节点 | 出处 |
|---|---|---|
| 2026-09-03 | GPT-6 Astra System Card 发布 | [Deployment Safety Hub](https://deploymentsafety.openai.com/gpt-6-astra) |
| 2026-09-22 | GPT-6 Sol、GPT-6 Luna 在 ChatGPT Work、Codex 与 API 推出 | [社区公告](https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925) |
| 2026-09-29 | GPT-6.1 Sol 以 Astra 卡 addendum 的形式发布 | 该卡（Hub 标 Published September 29, 2026） |

GPT-6 Sol 与 Luna 此后的版本另有系统卡，见 [[GPT6SolLuna十月版系统卡短报]]，本篇不写。

## 二、定位与价

| 项目 | GPT-6.1 Sol | 对照 | 出处 |
|---|---|---|---|
| 文档身份 | GPT-6 Astra System Card 的 **addendum** | 训练数据与护栏细节指向 Astra 卡 | 该卡 §1、§2 |
| API | `gpt-6.1-sol` | — | 博文 Pricing |
| 标准 API 价（每百万 token） | 输入 **$2** / 输出 **$10** / cached 输入 **$0.10** | Astra：$10 / $50 / $1 cached；Luna：$0.10 / $0.50 / $0.01 | 博文 Pricing；博文对照卡图注 |
| 「约 1/5」口径 | 相对 Astra 的 **标准输入与输出** token 价（$2/$10 对 $10/$50） | **不含** cached：cached 输入 $0.10，相对 GPT-6 Sol cached −50% | 博文 og:description 与 Pricing |
| 可用性 | Plus / Pro / Business / Enterprise / Edu：**ChatGPT Work** 与 **Codex** | **Chat 尚未开放**（原文 *not yet available in Chat*）；Ultrafast「未来几天」上线，Codex 中称最高约 8× 生成速度 | 博文 Pricing |

- **定位口号**（博文）：upgrade to GPT-6 Sol；nearly matches GPT-6 Astra on agentic coding, computer use, and professional work at one-fifth of Astra’s standard input and output token prices。
- **评测环境**（该卡 §1 脚注）：评测在研究环境或经 API 进行，与生产 ChatGPT 可能因 system prompt、可用工具与 effort 等不同而略有差异。

## 三、能力对照

博文对能力多给相对差或成本叙述，未给绝对分的项本篇不补。代表项如下：

- **DeepSWE v1.1**：匹配 GPT-6 Astra；相对 GPT-6 Sol 最佳分 **+6.4 pp**，且在更低 reasoning effort 与成本下（博文 Coding）。
- **OSWorld 2.0**（offline，partial reward；v2026.08.08）：相对 GPT-6 Sol **+7 pp**（max），距 Astra **2.1 pp**（max）（博文 Computer use）。
- **Factuality**（含事实错误的回答占比，low effort）：相对 GPT-6 Sol 由 **11.4%** 降到 **7.7%**；评测集取自用户曾举报过错误的对话，不代表日常流量（博文 Factuality）。
- 博文另在 GDP.pdf、AutomationBench、Terminal-Bench Science 上给出相对 Claude Opus 5.5、GPT-6 Sol 与 Astra 的分差和任务均价对比，结论方向与上面一致：接近 Astra，成本明显更低。

## 四、Preparedness 与安全增量

### Preparedness（该卡 §1、§9）

| 域 | 判定 | 备注 | 出处 |
|---|---|---|---|
| Cybersecurity | **Critical** | 与 Astra 同判定 | 该卡 §1、§9、§9.1.2 |
| Biological and Chemical | **High** | Critical 套件结果未过指示阈 | 该卡 §9、§9.1.1 |
| AI Self-Improvement | **未达 High**（below High） | — | 该卡 §9、§9.1.3 |
| 护栏 | **与 GPT-6 Astra 同一 safeguards stack** | 细节见 [[GPT6Astra系统卡深读]]，本篇不重写 | 该卡 §1、§9、§9.2 |

### 安全与对齐增量（代表项）

| 项 | GPT-6.1 Sol | 对照 | 出处 |
|---|---|---|---|
| Production Benchmarks（challenging prompts） | 八类中 **五类**高于 GPT-6 Sol | — | 该卡 §3.1.1 |
| Broken search（未披露搜索不可用） | **2.08%** | GPT-6 Sol **4.92%** | 该卡 §7.4.2；博文 Deploying safely |
| Codex 内部仿真 severity ≥ 3 旗 | **28**（0.056%） | Astra **27**（0.054%）；GPT-6 Sol **42**，GPT-6.1 Sol 比它少 33% | 该卡 §7.6 |
| CoT controllability（750–1250 tok） | **44.8%** | Astra **60.9%**；GPT-6 Sol **23.2%**；GPT-5.6 Sol **16.1%** | 该卡 §8.1.1 |
| ExploitBench Internal Port（ACE） | **21.5%** | Astra **31.5%**；GPT-6 Sol **5.5%** | 该卡 §9.1.2.2 |

在 Auto-review 评测中，GPT-6.1 Sol 与 Astra、GPT-6 Sol 一样没有尝试绕过监控（该卡 §7.1）。博文 Deploying safely 的摘要是：对齐评测相对 GPT-6 Sol 有实质改进、更接近 Astra；在 broken search 透明度、尊重显式限制、避免 agentic 未授权结果等挑战性评测上失败率低于 Sol。

## 五、意义

- **护栏跟随能力判定，而不跟随价位**：GPT-6.1 Sol 价位远低于 Astra，但网安判定同为 Critical，该卡因此对两者采用同一套护栏（§9）。
- **短增补记录同代迭代**：训练数据、评测方法与护栏都指回 Astra 卡，该卡只报基线安全指标与评测结果的更新（§1、§2）。
- **可监控性逐版本报告**：CoT controllability 在 GPT-6 Sol、GPT-6.1 Sol 与 Astra 之间差别明显（见第四节），该卡对每个版本单独报告（§8.1.1）。

## 六、局限与待核实

- **Chat 未开放**：博文明确 *not yet available in Chat*；当前渠道为 ChatGPT Work、Codex 与 API。
- **addendum 非独立长卡**：训练数据与护栏栈细节依赖 Astra 卡，本篇不展开。
- **能力项多为相对叙述**：DeepSWE、OSWorld 等博文未给 GPT-6.1 Sol 绝对分，本篇不补第三方或自测分。
- **评测环境**：研究环境或 API 与生产 ChatGPT 可能因 prompt、工具与 effort 不同而有差异。
- **博文发布时刻**：抓取到的博文没有文章自身的 time 元素，页内唯一的 2026-09-29T10:00 属于文末 DevDay 2026 Recap 卡片，不能当作 GPT-6.1 Sol 的发布时刻；发布日以该卡 Hub 页的 September 29, 2026 为准。
- **ExploitBench**：该卡提示公开 ExploitBench 的分数可能因历史漏洞暴露而虚高（§9.1.2.1），本篇因此只列 Internal Port。
- **Codex 仿真**：该卡 §7.6 写明它更适合作为内部部署风险信号，不宜直接当作外部部署安全率；本篇所列取自 §7.6 的 49,650 题匹配集，与 [[GPT6Astra系统卡深读]] 所记 Astra 卡自身集合的数字不能直接比。
- **对照列版本**：该卡写明先前模型的对照值可能来自后继版本，与发布时公布的数字可能不同（§2）。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT6Astra系统卡深读]] | 该卡的训练、评测方法与护栏都指回 Astra 卡；本篇只取 Preparedness 术语、同款护栏这一结论与对照列 | Astra 安全通史、CoT 与监控栈机制、变更日志 |
| [[GPT56系统卡深读]] | 「5.6 Sol ≠ 6 Sol」命名澄清；该卡对照列中的 5.6 分数 | 5.6 族专史 |
| [[GPT6SolLuna十月版系统卡短报]] | 同属 GPT-6 家族的后续系统卡；本篇只写 6.1 Sol 这份 addendum | 此后 Sol 与 Luna 版本的推送、判定与数字 |
| [[ClaudeSonnet55系统卡短报]]、[[ClaudeOpus55系统卡短报]] | 博文把 Opus 5.5 列为跨厂对照，本篇只取这一对照语境 | 重做 Sonnet、Opus 正文；RSP 框架 |

## 八、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| System Card addendum | Addendum to GPT-6 Astra System Card: GPT-6.1 Sol | OpenAI Deployment Safety Hub，Published September 29, 2026 | https://deploymentsafety.openai.com/gpt-6-1-sol |
| 官方博文 | Introducing GPT-6.1 Sol | OpenAI，页内 Sep 29, 2026 | https://openai.com/index/introducing-gpt-6-1-sol |
| DevDay 背景 | DevDay 2026 recap | OpenAI，2026-09-29 | https://openai.com/index/devday-2026-recap |
| 家族前序 | Announcing GPT-6 Sol and GPT-6 Luna in the API, Codex and ChatGPT | OpenAI 开发者社区，2026-09-22 | https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925 |
| 相邻深读 | [[GPT6Astra系统卡深读]] | OpenAI Deployment Safety Hub | https://deploymentsafety.openai.com/gpt-6-astra |
