---
topic: TR-GPT-5.1
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# GPT-5.1 System Card Addendum 专项深读卡

> 攻坚线：**架构思想（主）**
> 锚点：OpenAI, *GPT-5.1 Instant and GPT-5.1 Thinking System Card Addendum*（封面日期 **November 12, 2025**）
> 官方 PDF：`https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf`（**5** 页；CreationDate/ModDate **2025-11-13** 00:38:05 CST）
> 主卡对照：模型与技术报告/SystemCard/GPT5SystemCard.md（GPT-5 System Card，封面 **2025-08-13**）
> 扫描入口：模型与技术报告/SystemCard与TR扫描2025至2026.md（deploymentsafety / CDN PDF）
> **禁编造**：本 addendum **无能力榜分、无参数量/架构细节**；数字仅取正文/表格显式值；线上 A/B 仅写作者定性结论（wide error bars / low statistical confidence），不臆造百分点。

---

## 1. 元信息

| 字段 | 核实值（据官方 PDF） |
|---|---|
| 标题 | GPT-5.1 Instant and GPT-5.1 Thinking System Card Addendum |
| 机构 | OpenAI |
| 封面日期 | **November 12, 2025** |
| 页数 | **5**（A4）；§1 Introduction → §2 Baseline Model Safety Evaluations → §3 Preparedness Framework → References |
| PDF 元数据 | Creator: LaTeX with hyperref；CreationDate/ModDate：**2025-11-13** 00:38:05 CST（晚于封面约 1 天） |
| 本地路径 | `https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf` |
| 官方入口（扫描清单已记；本卡未再 WebFetch） | 页：`https://deploymentsafety.openai.com/gpt-5-1`；CDN PDF：`https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf`（见 模型与技术报告/SystemCard与TR扫描2025至2026.md） |

**本卡自身定位（§1，仅原文）：**

1. 产品迭代：GPT-5.1 Instant / Thinking 为 GPT-5 的 next iteration；另有 **GPT-5.1 Auto** 继续按查询路由到最适合的模型（多数情况下用户无需选型）。
2. Instant 产品主张（无分数）：「more conversational」；improved instruction following；**adaptive reasoning**（决定何时 think before responding）。
3. Thinking 产品主张（无分数）：「adapts thinking time more precisely to each question」。
4. 安全立场：comprehensive safety mitigations **largely the same** as GPT-5 System Card；本 addendum 提供 **updated baseline safety metrics**。
5. 评测扩展：引用「recent GPT-5 system card addendum on **sensitive conversations**」——基线安全评测扩入 **mental health**（isolated delusions / psychosis / mania 迹象）与 **emotional reliance**（对 ChatGPT 的 unhealthy emotional dependence / attachment）。
6. 内部标签：GPT-5.1 Instant → **gpt-5.1-instant**；GPT-5.1 Thinking → **gpt-5.1-thinking**。

**一句话抓手：** 这是 GPT-5 主卡之后的**短增补安全卡**（5 页），更新 Production / jailbreak / vision 基线分，并续写敏感对话（mental health / emotional reliance）与 Preparedness 档位；**不是**新架构报告，也**不含** SWE 等能力榜。

---

## 2. 相对 GPT-5 System Card 的增量对照

> 对照轴：本 addendum ↔ 模型与技术报告/SystemCard/GPT5SystemCard.md 所据主卡（封面 2025-08-13，60 页）。
> 仅写两边都能锚定的差分；主卡有而本卡未重跑/未复述的项标「本卡未覆盖」。

| 维度 | GPT-5 System Card（主卡） | 本 Addendum（5.1） |
|---|---|---|
| 文档角色 | 全量安全 + Preparedness（§1–5 + Appendix） | **基线安全指标更新卡**；声明 mitigations largely same |
| 产品型号 | gpt-5-main / thinking（+ mini/nano/pro）；unified system + real-time router | **gpt-5.1-instant** / **gpt-5.1-thinking**；**GPT-5.1 Auto** 继续路由 |
| 路由叙事 | router：conversation type / complexity / tool needs / explicit intent | Auto「route each query to the model best suited」——**机制细节本卡未展开** |
| Instant/Main 命名 | 主卡快答线为 **gpt-5-main** | 本卡快答线改称 **Instant**；对照表列 **gpt-5-instant-aug15**、**gpt-5-instant-oct3**（主卡未用此标签） |
| Thinking 时间控制 | reasoning RL / think before answer（训练侧描述） | Instant：**adaptive reasoning**（何时 think）；Thinking：**更精确适配 thinking time**——仍无 token/秒数字 |
| 敏感对话评测 | 主卡 §3 无独立 mental health / emotional reliance Production 行（本卡称引入自「GPT-5 update on sensitive conversations」姊妹 addendum） | Table 1 新增 **mental health\***、**emotional reliance\***；并给早期 **online A/B** 定性信号 |
| Disallowed 报告集 | Standard（近饱和）+ Production Benchmarks | **只报 Production Benchmarks**（刻意更难；不代表平均生产流量） |
| StrongReject | 主卡 Table 5（thinking↔o3；main↔4o） | Table 2：5.1 相对 **gpt-5-thinking / gpt-5-instant-aug15/oct3** |
| Vision 图文输入 | 主卡 Table 10（相对 o3/4o） | Table 3：沿用「ChatGPT agent 引入的 image input evaluations」；相对 GPT-5 世代对照 |
| Safe-completions / Instruction Hierarchy / Sycophancy / 幻觉 / 欺骗 / 注入三评测 / 红队规模 | 主卡专节有数字 | **本卡未复测、未复述** |
| Preparedness | Bio/Chem：**High**（precautionary）+ 配套 safeguards；Cyber：**未达** high；Self-improvement：**未达** High | §3：对 GPT-5.1 **继续**按 Bio/Chem **High risk** 处理并继续施相应 safeguards；Cyber 与 AI self-improvement：近终盘「**do not have a plausible chance of reaching a High threshold**」（与 GPT-5 前代一致口径） |
| 架构/参数/训练数据 | 主卡亦未公开参数量；有数据类别 + reasoning RL 句 | **无新增**训练/架构披露 |
| 能力榜（SWE 等） | Preparedness 图 + 引用博客 medium verbosity 74.9% | **全文无能力榜分** |

**跟读结论（架构思想）：** 5.1 在产品面上把「快答线」显式产品化为 **Instant + adaptive reasoning**，把「深思线」强调为 **更精细的 thinking-time 适配**，Auto 继续隐藏选型；安全栈主张「与 GPT-5 主卡大体相同」，增量主要是 **基线表换代对照** 与 **敏感情境（mental health / emotional reliance）离线+早期在线信号**，而非新的安全范式论文。

---

## 3. 安全 / 能力更新要点（仅正文与表）

### 3.1 Production Benchmarks（§2.1 / Table 1）

- 指标：`not_unsafe`（higher better）；故意难；围绕「现有模型尚未理想作答」的案例构建；**error rates 不代表平均生产流量**。
- 作者总评：gpt-5.1-thinking 与 gpt-5.1-instant 相对 GPT-5 前代，在这些特别难的集上 **comparable safety performance**。

**Table 1 可核对数字（Production Benchmarks）：**

| Category | gpt-5-thinking | gpt-5.1-thinking | gpt-5-instant-aug15 | gpt-5-instant-oct3 | gpt-5.1-instant |
|---|---:|---:|---:|---:|---:|
| illicit/non-violent | 0.865 | 0.860 | 0.700 | 0.807 | 0.853 |
| personal data | 0.966 | 1.000 | 0.966 | 1.000 | 1.000 |
| harassment | 0.815 | 0.747 | 0.683 | 0.745 | 0.836 |
| sexual | 0.906 | 0.895 | 0.782 | 0.951 | 0.917 |
| extremism | 1.000 | 1.000 | 0.922 | 0.978 | 0.989 |
| hate | 0.883 | 0.839 | 0.74 | 0.806 | 0.897 |
| violence | 0.946 | 0.930 | 0.829 | 0.953 | 0.938 |
| sexual/minors | 0.953 | 0.901 | 0.862 | 0.961 | 0.957 |
| Illicit/violent | 0.954 | 0.934 | 0.783 | 0.862 | 0.918 |
| self-harm/intent | 0.959 | 0.958 | 0.893 | 0.893 | 0.909 |
| self-harm/instructions | 0.979 | 0.950 | 0.858 | 0.943 | 0.950 |
| mental health* | 0.466 | 0.684 | 0.251 | 0.944 | 0.883 |
| emotional reliance* | 0.812 | 0.785 | 0.688 | 0.986 | 0.945 |

\*New evaluations，引入自 GPT-5 update on sensitive conversations。

**作者点名的回归 / 改进（§2.1 正文）：**

| 型号 | 相对谁 | 原文结论 |
|---|---|---|
| gpt-5.1-thinking | gpt-5-thinking | **light regressions**：harassment、hateful language、disallowed sexual content；「working on further improvements」 |
| gpt-5.1-instant | gpt-5-instant-aug15 | **outperforms on all** above evaluations |
| gpt-5.1-instant | gpt-5-instant-oct3 | **slightly worse**：disallowed sexual、violent、mental health、emotional reliance |

### 3.2 敏感情境：离线 vs 早期在线（§2.1 续）

- **在线测量定位**：A/B 期间 early signal；undesired responses for sensitive situations **prevalence 极低** + A/B 规模相对小 → **wide error bars**；上线后继续测以决定是否需进一步 mitigations（例：routing to specific safer models）。
- **离线 vs 在线**：在线捕真实部署 prevalence / 用户行为漂移；离线偏「worst case」——通常很长多轮、前几轮植入过去模型的 undesired behavior。

| 主题 | 离线（Production） | 早期 online（作者定性；无百分点） |
|---|---|---|
| Mental health | instant：相对 oct3 **slight regression**，仍优于 aug15；thinking：相对 gpt-5-thinking **improves** | instant / thinking 相对各自前代均 **slight improvement**，但 **low statistical confidence**；将 post-launch 继续调查 |
| Emotional reliance | instant 与 thinking 相对 oct3 / thinking 前代均 **slight regression**；instant 仍优于 aug15 | instant 相对 oct3：**regression**（low confidence），仍优于 aug15；thinking 相对前代：**improvement，high statistical confidence**；承诺继续调查并更新 safeguards |
| Self harm and suicide | （Table 1 有 self-harm/intent、self-harm/instructions 行；作者 online 段另述） | instant 相对 oct3：**neutral**；thinking 相对前代：**improvements**；估计均 **low statistical confidence** |

### 3.3 Jailbreaks — StrongReject（§2.2 / Table 2）

- 方法：学术 StrongReject [1] 的改编——把已知 jailbreak 插入 disallowed 内容样例，再用与 disallowed 相同的 policy graders；metric `not_unsafe`。

| metric | gpt-5-thinking | gpt-5.1-thinking | gpt-5-instant-aug15 | gpt-5-instant-oct3 | gpt-5.1-instant |
|---|---:|---:|---:|---:|---:|
| not_unsafe | 0.974 | 0.967 | 0.683 | 0.850 | 0.976 |

作者结论：gpt-5.1-instant **优于**前代；gpt-5.1-thinking **on par** 前代。

### 3.4 Vision — Image input（§2.3 / Table 3）

- 评测：ChatGPT agent 引入的 image input evaluations；disallowed **combined text + image** → `not_unsafe`。

| Category | gpt-5-thinking | gpt-5.1-thinking | gpt-5-instant-aug15 | gpt-5-instant-oct3 | gpt-5.1-instant |
|---|---:|---:|---:|---:|---:|
| hate | 0.984 | 0.980 | 0.982 | 0.990 | 0.993 |
| extremism | 0.991 | 0.993 | 0.986 | 0.986 | 0.996 |
| illicit | 0.994 | 0.980 | 0.986 | 1.000 | 0.992 |
| attack planning | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 |
| self-harm | 0.976 | 0.936 | 0.983 | 0.975 | 0.960 |
| harms-erotic | 0.990 | 0.990 | 0.994 | 0.999 | 0.999 |

作者结论：instant / thinking **generally on par** 前代；**观测到 gpt-5.1-thinking 在 self-harm + image 上回归**，正在跟进改进。

### 3.5 Preparedness Framework（§3）

| 域 | 原文结论（可引用） |
|---|---|
| Biological and Chemical | 与 GPT-5 launch 相同：继续将 GPT-5.1 视为 **High risk**，并继续应用 corresponding safeguards |
| Cybersecurity | 近终盘评测：与 GPT-5 前代一样，**do not have a plausible chance of reaching a High threshold** |
| AI self-improvement | 同上：无 plausible chance of High |

> 本卡 **未**重刊主卡中的 Cyber Range / Pattern Labs / METR / SWE 等细表；能力档位结论以本段定性句为准。

### 3.6 「能力」侧：本卡实际写了什么

本 addendum **没有** SWE-bench、GPQA、HealthBench 等能力分数。唯一可记的产品能力主张（§1，非评测）：

- Instant：更 conversational；更好 instruction following；adaptive reasoning（何时 think）。
- Thinking：thinking time 更精确适配问题。
- Auto：继续按查询路由，用户多数无需手选模型。

若需能力榜，应回 GPT-5 主卡 / launch blog，或扫描清单中的后续卡——**勿把本卡当能力源**。

---

## 4. 待核实与引用

### 4.1 待核实

1. 封面 **2025-11-12** vs CreationDate **2025-11-13**——是否同文次日再导出；建议对照 deploymentsafety 页 Last updated。
2. 「GPT-5 system card addendum on **sensitive conversations**」姊妹文：官方页 / 扫描清单是否已收录、mental health / emotional reliance 定义与 grader 细则以哪份为准。
3. **gpt-5-instant-aug15** / **gpt-5-instant-oct3** 与主卡 **gpt-5-main** 的精确对应关系（本卡未写「main = Instant」等式；仅从命名与对照轴推断产品线延续——**勿写死等同**）。
4. Online A/B 的样本量、时间窗、undesired 操作定义、置信区间数值——正文仅给定性（wide error bars / low|high statistical confidence），**无表内百分点**。
5. Table 3「attack planning」gpt-5.1-instant 单元格为 **1.00**（两位）而其行列多为三位——是否排版截断，读图/再抽取确认。
6. StrongReject 改编细节（插入哪些 jailbreak、harm 覆盖面）相对主卡 Table 5 是否同协议——本卡仅称「adaptation of … StrongReject [1]」。
7. 与 GPT-5.2 / 后续 addendum、ChatGPT agent System Card 的条款差分（扫描清单 P1 项；本卡未交叉深读）。
8. CDN 文件名 `5_1_system_card.pdf` 与本地 `gpt-5.1-system-card-addendum.pdf` 是否逐页一致（扫描已记来源；本卡未做哈希对照）。

### 4.2 本卡主要引用锚点（PDF 内）

- §1 Introduction（型号、Auto、与 GPT-5 SC / sensitive-conversations addendum 关系）
- §2.1 Disallowed / Production Benchmarks（Table 1）+ Mental Health / Emotional Reliance / Self Harm online 段
- §2.2 Jailbreaks（Table 2 StrongReject）
- §2.3 Vision（Table 3）
- §3 Preparedness Framework
- References [1] Souly et al., “A strongreject for empty jailbreaks,” arXiv:2402.10260, 2024

### 4.3 相关研究会笔记

- 模型与技术报告/SystemCard/GPT5SystemCard.md — GPT-5 主卡深读（本卡直接增量对象）
- 模型与技术报告/SystemCard与TR扫描2025至2026.md — 系列卡下载与 P1「5.1/5.2 增补卡」排队
- 模型与技术报告/开源与闭源前沿模型谱系.md — 统一系统 / Instant·Thinking 产品谱系
- Harness/智能体与工具/智能体工具与长程任务.md — 工具/路由叙事（本卡未新增注入数字）

---

*起草：AI研究会·攻坚研究员执行助手 · 2026-09-22（Asia/Shanghai）· status: draft · 仅据官方 PDF 原文*

## 相关笔记

### 技术报告专项
- [[GPT5SystemCard|TR GPT-5]]
- [[GPT51SystemCard附录|TR GPT-5.1 Addendum]]
- [[GPT52SystemCard更新|TR GPT-5.2 Update]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[Gemini3ProModelCard|TR Gemini 3 Pro Model Card]]
- [[ClaudeOpus41SystemCard|TR Claude Opus 4.1]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

