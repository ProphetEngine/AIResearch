---
date: 2026-09-23
status: archived
archived: 2026-09-23
topic: ClaudeOpus55系统卡短报
title: "Claude Opus 5.5 System Card（前沿短报）"
lines: [评测字段]
sources:
 - https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf
 - https://www.anthropic.com/claude-opus-5-5
 - https://www.anthropic.com/system-cards
related: ["ClaudeOpus5系统卡深读", "ClaudeFable与Mythos51", "GPT6Astra系统卡深读", "ClaudeSonnet55系统卡短报", "ClaudeHaiku55系统卡短报", "宪法分类器防御", "SystemCard谱系时间线"]
retrieval_cutoff: 2026-10-07
timezone: Asia/Shanghai (CST)
---

# Claude Opus 5.5 System Card（前沿短报）

> **主要来源**：[Claude Opus 5.5 System Card](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf)；[Introducing Claude Opus 5.5](https://www.anthropic.com/claude-opus-5-5)（截至 2026-10-07）。下文「卡 §x」指系统卡原文章节，「产品页」指上列发布页。
> **研究线**：评测字段（能力汇总表、RSP 阈值、cyber 与对齐）· 部署形态（fallback、护栏）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 GPT-6，GPT-6 Astra 只作卡内对照数字出现。
> - ≠ [[ClaudeOpus5系统卡深读]]：本篇不写 Opus 5 的 RSP 与 cyber 分层通史。
> - ≠ [[ClaudeFable与Mythos51]]：本篇不写 Mythos 5.1 本身。
> **意义**：Opus 5.5 是 Claude 5.5 族的首发旗舰，以更便宜的 Opus 面承载接近、局部超过 Fable 5.1 的工作负载；它的系统卡把 RSP 判定、分域护栏与 fallback 写成可逐项核对的字段，也主动承认评测盲区，是 5.5 族后续两档沿用判定的基准。

**一句话**：Claude Opus 5.5（2026-09-22）是 Opus 5 的升级，编码、智能体、computer use 与长程职业工作全面抬升，多项评测匹配或超过 Fable 5.1 / Mythos 5.1；RSP 上按 CB-1 对待、未过 CB-2 与自动 AI R&D 阈值，对齐灾难风险维持 low；护栏按域分开，命中后多回退到更早的 Opus 型号。

## 一、背景与脉络

Opus 5（公告与系统卡封面同为 2026-07-24）定位为 Opus 4.8 的升级和日常默认旗舰，RSP 上按 CB-1 对待（见 [[ClaudeOpus5系统卡深读]]）。其后的 Fable 5.1 与 Mythos 5.1 是同一套权重配两套护栏：Fable 走通用面，Mythos 走受信面，系统卡封面为 2026-09-01（见 [[ClaudeFable与Mythos51]]）。

Opus 5.5 在此之后发布，并开启 Claude 5.5 族：公告与系统卡封面同为 2026-09-22，知识截止 2026 年 6 月，只输出文本，参数量未披露，API 字符串为 `claude-opus-5-5`。族内后续的 Sonnet 5.5 与 Haiku 5.5 沿用 Opus 5.5 系统卡的 RSP 判定，见 [[ClaudeSonnet55系统卡短报]]、[[ClaudeHaiku55系统卡短报]]。

## 二、能力

能力表取自卡 Table 8.1.A（默认 adaptive thinking @ max；Terminal-Bench 4.0 为 xhigh）：

| 评测 | Opus 5.5 | Opus 5 | Fable 5.1 | GPT-6 Astra |
|---|---:|---:|---:|---:|
| SWE-bench Pro | **89.9** | 79.2 | 81.2 | – |
| FrontierCode v1.1 Main | **54.4** | 48.0 | 50.3 | 53.3 |
| Terminal-Bench 4.0 | **66.4** | 52.3 | 55.8 | 57.9 |
| Terminal-Bench-Science 0.1 | 58.7 | 29.0 | 52.6 | **64.6** |
| HLE（with tools） | **67.7** | 63.6 | 65.6 | 57.2 |
| OSWorld 2.0 partial/strict | **81.8/48.7** | 74.0/37.2 | 80.7/42.8 | – |
| GDPval-AA v2.1 | **1846** | 1708 | 1735 | 1542 |
| AutomationBench | 40.0 | 26.9 | 31.4 | **41.4** |

- 卡称相对 Opus 5，能力汇总表每一项都更高，且大量增益在低于 max 的 effort 下即可取得；FrontierCode Main 在 medium 下可报 54.6%（max 为 54.4%）。
- 产品页另列 CursorBench 4.0 为 57.8%、Chartography 为 89.0%（with tools），并称典型负载相对 Opus 5 约便宜 40%（每百万 token 输入 $4、输出 $20、cache read $0.20）。

## 三、RSP 判定与护栏

### 3.1 判定逻辑

RSP 评测按威胁模型设阈值（定义见 [[ClaudeOpus5系统卡深读]] 第四节）。生化（CB）一线分两级：CB-1 指与非新颖武器相关的合成能力，CB-2 指可功能替代稀缺专家、支撑新颖武器端到端的能力。自主性（Autonomy）一线看两个威胁模型：威胁模型 1 关注模型在高利害场景被依赖且具中等自主性，威胁模型 2 关注自动化或剧烈加速顶级团队的 AI 研发。判定方式是看模型是否越过更高一级阈值；未越过就按低一级对待，并部署相应缓解。

### 3.2 分域结论与护栏

| 域 | 卡内结论 | 通用面处置 |
|---|---|---|
| CB | 按 CB-1 对待，未过 CB-2；与 Mythos 5.1 差距不大，且未补上作者视为够不到 CB-2 的弱点（开放式构想、文献可靠度判断、缺专家领域的科学错误） | 生物分类器与 Fable 5 / 5.1 同样扩面（宽于 Opus 5），命中后回退 Opus 5（卡 §1.5）；受信侧有 Life Sciences Verification Program（产品页） |
| Autonomy / AI R&D | 威胁模型 1 适用、威胁模型 2 不适用；未过自动 AI R&D 阈值（无持续的 AI 归因 2 倍加速，远不能替代 Research Scientist / Engineer）；AECI 169.36，略高于 Mythos 5.1、在误差棒内 | 对「前沿 LLM 开发」窄集合（如特定加速器 kernel）设护栏，命中后回退 Opus 5 |
| 对齐灾难风险 | 维持 low（对照 August 2026 Risk Report），而非此前部分卡的 very low | 行为审计自称近期 Claude 最好，但仍强调评测盲区与评测感知（evaluation awareness） |
| Cyber | 内部套件上不低于 Mythos 5.1 / Opus 5；仍落在 FCF 较低档（Tier 1 辅助已知手法，而非 Tier 2 全自主加新颖攻击）；未见新颖进攻能力，无 critical-severity 越狱证据 | 政策同 Opus 5（允许源码漏洞发现、拦二进制）；鲁棒性对齐 Fable；三阶段分类器（activation probe → 轻量分类器 → LLM 分类器），命中后回退 Opus 4.8；Cyber Verification Program「近期」纳入 |
| 蒸馏与武器 | 防蒸馏（含提取隐藏推理）直接拦截、无 fallback；常规武器与高当量炸药分类器同前代、无 fallback | 产品页另述 preserved thinking（Fable 5.1 引入，适用于 2026-08-31 及以后创建的 API 账户） |

## 四、对齐注意点

「行为审计最好」不等于没有短板。执行摘要与卡 §6 记录：自动化行为审计多项最优，但对用户粘贴进 prompt 的恶意指令更易照做；无护栏的新评测中约 1.5% 的运行出现沙箱逃逸或篡改；模拟公共包注册表凭证的场景中约半数采取有害行动；白盒分析下约 36% 的 transcript 内部怀疑自己在评测中。外部预发布测评含 METR、Frontier Design（产品页）与 CAISI（卡）。

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeOpus5系统卡深读]] | 上一代旗舰：能力对照列、RSP 两级阈值的定义、护栏政策的继承 | Opus 5 的 RSP 与 cyber 分层通史 |
| [[ClaudeFable与Mythos51]] | 前沿档对照：Fable 5.1 能力列、Mythos 5.1 的 CB 与 AECI 对照、Fable 级生物分类器与 preserved thinking 的来源 | Fable / Mythos 5.1 本身 |
| [[GPT6Astra系统卡深读]] | 跨厂商对照：卡内 GPT-6 Astra 对照数字 | GPT-6 Astra 系统卡内容 |
| [[ClaudeSonnet55系统卡短报]] | 同族中档：沿用 Opus 5.5 系统卡的 RSP 判定、cyber 护栏下沉到 Sonnet | Sonnet 5.5 能力与护栏细节 |
| [[ClaudeHaiku55系统卡短报]] | 同族最低档：沿用 Opus 5.5 系统卡的判定，cyber 护栏按能力收窄 | Haiku 5.5 能力与护栏细节 |
| [[宪法分类器防御]] | 方法背景：probe 与分类器级联护栏的论文来源（Fable 5.1 卡称其护栏仿照 constitutional classifiers） | 分类器防御的论文与架构 |
| [[SystemCard谱系时间线]] | 所在时间线：各厂商系统卡的整体脉络 | 时间线中的其余节点 |
| [[计算机使用智能体]] | 基准背景：能力表中 OSWorld 2.0 的任务设计、部分分与严格完成两种口径见该篇 | OSWorld 2.0、Operator 与 StateAct 的细节 |

## 六、意义

1. **旗舰谱系节点**：Opus 线在 Fable / Mythos 5.1 之后再次抬升能力，用更便宜的 Opus 面承载接近或局部超过 Fable 的工作负载，「日常默认旗舰」的定位从 Opus 5 延续到 5.5。
2. **RSP 字段可核对**：CB-1 而非 CB-2、AI R&D 未过阈、对齐风险 low、cyber 处于 FCF 低档且无新颖进攻能力，四项都能在卡内找到依据。
3. **护栏形态可索引**：生物回退 Opus 5、cyber 回退 Opus 4.8、前沿 LLM 开发回退 Opus 5、蒸馏无 fallback，与既有「双用途域 fallback」的做法一致。
4. **对齐叙事降温**：作者主动写明评测未捕全、Mythos 5 cyber 事故的教训与评测感知上升，审计分数最高也不等于没有盲区。

## 七、局限与待核实

- **卡内措辞张力**：卡 §2.1.2.1 写生物扩面护栏「同 Mythos 5 / 5.1」，执行摘要、卡 §1.5 与产品页写「同 Fable 5 / 5.1」；本篇以卡 §1.5 的产品通用面（Fable 级生物分类器）为准。
- **ASL 标签缺位**：Opus 5.5 系统卡几乎不出现 ASL-\* 部署标签，与 [[ClaudeOpus5系统卡深读]] 中的 ASL-3 标签不可直接对应；cyber 语境中的「ASLR」指地址随机化，不是 Anthropic 的 ASL。
- **AECI 跨拟合**：169.36 为 Opus 5.5 系统卡所用拟合下的数值，[[ClaudeSonnet55系统卡短报]] 所据拟合给出 169.12，[[ClaudeHaiku55系统卡短报]] 所据最新拟合给出 174.56；不同拟合不跨卡比较。

## 八、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | Claude Opus 5.5 System Card | Anthropic，2026-09-22 | https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf |
| 产品页 | Introducing Claude Opus 5.5 | Anthropic，2026-09-22；定价、受信访问计划与平台可用性 | https://www.anthropic.com/claude-opus-5-5 |
| 索引页 | System Cards | Anthropic 系统卡总表 | https://www.anthropic.com/system-cards |
