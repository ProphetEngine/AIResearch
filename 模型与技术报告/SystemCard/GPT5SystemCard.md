---
title: GPT-5 System Card 专项深读卡
topic: TR-GPT-5
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# GPT-5 System Card 专项深读卡

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：OpenAI, *GPT-5 System Card*（封面日期 **August 13, 2025**）
> 官方 PDF：`https://cdn.openai.com/gpt-5-system-card.pdf`（**60** 页；CreationDate **2025-08-20** CST）
> **禁编造**：能力榜分仅写正文/表格显式数字；图中未抽出可读数字的标「待核实读图」。

---

## 1. 报告元信息（发布日、页数、与博客关系）

| 字段 | 核实值（据官方 PDF） |
|---|---|
| 标题 | GPT-5 System Card |
| 机构 | OpenAI |
| 封面日期 | **August 13, 2025** |
| 页数 | **60**（A4）；目录含 §1–5 + Appendix 1/2 + References |
| PDF 元数据 | Creator: LaTeX with hyperref；CreationDate/ModDate：**2025-08-20** 03:33:37 CST（晚于封面日约一周，或为再导出） |
| 本地路径 | `https://cdn.openai.com/gpt-5-system-card.pdf` |
| 官方入口（扫描清单已记；本卡未再 WebFetch） | 页：`https://openai.com/index/gpt-5-system-card/`；CDN PDF：`https://cdn.openai.com/gpt-5-system-card.pdf`（见 [[SystemCard与TR扫描2025至2026]]） |

**与博客 / 姊妹材料的关系（仅原文可核对处）：**

1. **GPT-5 发布博客（launch blog）**
 - System Card **§5.1.3.1** 明文交叉引用：「The SWE-Bench result in the **GPT-5 launch blog post (74.9%)**, was run with the default verbosity setting in the API (**verbosity = medium**).」
 - 同段说明：本卡 Preparedness 评测一律在模型 **maximum trained-in verbosity** 下跑（高于 API 当前可用的 `"high"`），故与博客口径可能不同。
 - 产品叙事侧（统一系统 / router / thinking）与 **[[开源与闭源前沿模型谱系]]** 所跟读的 *Introducing GPT-5*（2025-08-07）一致；本卡是安全与 Preparedness 的展开，封面日晚于该博客约 6 天。

2. **Safe-completions 论文**
 - §3.1：「You can read more about safe-completions in our paper, *From Hard Refusals to Safe-Completions: Toward Output-Centric Safety Training.*」
 - 本卡把该范式写成 GPT-5 全系安全训练要点，而非仅博客口号。

3. **ChatGPT agent System Card**
 - 引言：生物/化学 High capability「Similarly to **ChatGPT agent**」；§5.3.2 称 rapid remediation / bug bounty 细节见 ChatGPT agent System Card。
 - 即：GPT-5 thinking 的 High bio 处理与 agent 卡同框架衔接。

4. **本卡自身定位（§1）**
 - 主评测对象：**gpt-5-thinking** 与 **gpt-5-main**；其余型号多在 **Appendix 1**。
 - 「In the near future, we plan to integrate these capabilities into a **single model**.」

**一句话抓手：** 这是「统一系统」产品形态的**安全与前沿能力卡**，不是架构论文；参数量 / 层结构 / 是否 MoE **全文未公开**。

---

## 2. 系统主张对照表（统一系统 / router / thinking / 工具等，仅原文）

### 2.1 统一系统与型号标签（§1，Table 1）

| 原文主张 | 原文要点 |
|---|---|
| **Unified system** | 「a smart and fast model that answers most questions, a deeper reasoning model for harder problems, and a **real-time router** that quickly decides which model to use」 |
| Router 依据 | conversation type, complexity, **tool needs**, explicit intent（例：prompt 写 “think hard about this”） |
| Router 训练信号 | 「continuously trained on real signals, including when users switch models, preference rates for responses, and measured correctness」 |
| 限额后行为 | 「Once usage limits are reached, a **mini** version of each model handles remaining queries.」 |
| 快答线标签 | **gpt-5-main** / **gpt-5-main-mini** |
| 思维线标签 | **gpt-5-thinking** / **gpt-5-thinking-mini**；API 另有 **gpt-5-thinking-nano**（「even smaller and faster… for developers」） |
| Pro 设定 | ChatGPT 侧：**gpt-5-thinking-pro** = gpt-5-thinking + **parallel test time compute** 设定 |
| 代际对照（Table 1） | GPT-4o→main；GPT-4o-mini→main-mini；o3→thinking；o4-mini→thinking-mini；GPT-4.1-nano→thinking-nano；o3 Pro→thinking-pro |
| 产品能力叙事（§1，非分数） | 更快；减幻觉、更好 instruction following、减 sycophancy；加强 writing / coding / health；全系 **safe-completions** |
| Preparedness 总判（§1） | 将 **gpt-5-thinking** 按 Biological and Chemical 域 **High capability** 处理并激活配套 safeguards；同时写明「do not have definitive evidence」达「novice… severe biological harm」阈值门槛，属 precautionary |

### 2.2 数据与训练（§2，仅公开句）

| 维度 | 原文 |
|---|---|
| 数据来源 | publicly available internet；third-party partners；users / human trainers / researchers provide or generate |
| 过滤 | quality filtering；reduce personal information；Moderation API + safety classifiers（含 minors 相关显式内容） |
| Reasoning 训练 | gpt-5-thinking / mini / nano「trained to reason through **reinforcement learning**」；「think before they answer」；长 internal CoT；refine thinking / try strategies / recognize mistakes；利于遵循 guidelines 与抵抗 bypass |
| 对比口径 | live 对照（如 o3）取「latest versions」，可能与该型号 launch 时发表值略异 |

### 2.3 工具、连接器与注入防护（§3.6，原文机制）

| 项 | 原文 |
|---|---|
| 为何相关 | 「GPT-5… has access to **browse the web** and use **connectors** as well as **other tools**.」 |
| 模型侧 | 「teaching models to ignore prompt injections in web or connector contents」 |
| 系统侧（外泄） | connector 调用后，「switch browsing to only access **cached copies** of web pages」→ 防止敏感内容在上下文时再发 live network request |
| 评测三类 | Browsing / Tool-calling / Coding prompt injections（Table 7） |
| 未尽述 | 「further mitigations… not all described here」（对抗性原因） |

### 2.4 Safe-completions（§3.1，安全范式主张）

| 对照 | 原文 |
|---|---|
| 旧范式 | hard refusals：按用户意图是否允许，二元拒绝 |
| 新范式 | **safe-completions**：以 **assistant 输出是否安全** 为中心，而非仅二分类用户意图；「maximize helpfulness subject to the safety policy’s constraints」 |
| 动机 | 二元边界对 dual-use（bio / cyber）脆弱：高层安全完成可能，过细则 uplift |
| 观测（作者） | 相对 refusal-trained 基线（o3），双重用途提示上更安全、残留失败严重度下降、整体 helpfulness 更高 |

---

## 3. 安全与评测附录要点（可核对案例；勿编造能力榜分）

> 比较轴（§3）：**gpt-5-thinking ↔ OpenAI o3**；**gpt-5-main ↔ GPT-4o**。
> gpt-5-thinking-pro 未单独重跑安全评测：作者认定 thinking 结果为强 proxy。

### 3.1 内容安全与生产流量（§3.2–3.5）

| 评测 | 可核对要点（正文/表） |
|---|---|
| Standard Disallowed（Table 2，metric `not_unsafe`） | 多类接近饱和；作者称将停发旧集、改推更难集。**personal-data**：thinking 0.881 vs o3 0.930（作者称噪声）；**personal-data/restricted**：thinking 0.989 vs o3 0.921 |
| Production Benchmarks（Table 3） | 多轮、更难；thinking 多数 ≥ o3。main 相对 4o：illicit 类显著改进（归因 safe-completions）；hate/threatening、sexual/exploitative 有显著回退，人工复核称违规多为 low severity |
| Sycophancy（§3.3 / Table 4） | 离线：4o 0.145 → main **0.052**（「nearly 3x better」）；thinking **0.040**。线上早期 A/B：相对最近 4o，谄媚 prevalence **−69%**（免费）/ **−75%**（付费） |
| Jailbreaks StrongReject（Table 5） | thinking 与 o3 大体持平；main 与 4o 接近 |
| Instruction Hierarchy（Table 6） | system > developer > user。thinking 多数接近/优于 o3；**main 多项回退**，作者写明将跟进修复 |

### 3.2 提示注入（§3.6 / Table 7；§4.2）

| 评测（higher better） | gpt-5-thinking | OpenAI o3 |
|---|---:|---:|
| Browsing prompt injections | **0.99** | 0.89 |
| Tool calling prompt injections | **0.99** | 0.80 |
| Coding prompt injections | **0.97** | 0.94 |

外部：两周 connector 向评估，47 findings → 10 notable，发布前已更新部分逻辑；Gray Swan Shade / ART 基准称 thinking 对 adversarial prompt injection **SOTA**（图 8，分值待核实读图）。

### 3.3 幻觉与欺骗（§3.7–3.8）

**生产流量事实性（Browsing Enabled，§3.7 正文百分比）：**

- gpt-5-main 幻觉率相对 GPT-4o **小 26%**；含 ≥1 重大错误的响应 **少 44%**。
- gpt-5-thinking 相对 o3：**小 65%** / 响应级 **少 78%**。
- LongFact / FActScore：正文称 thinking 在 browse-on/off 下相对 o3「**over 5 times fewer** factual errors」（跨三基准）。
- SimpleQA（Table 8，no web）：thinking accuracy **0.55** / hallucination **0.40**（o3：0.54 / 0.46）。

**Deception（Table 9，Deception Rate lower better，AbstentionBench 为 recall higher better）：**

| Eval | gpt-5-thinking | OpenAI o3 |
|---|---:|---:|
| Coding Deception | **0.17** | 0.47 |
| Browsing Broken Tools | **0.11** | 0.61 |
| CharXiv Missing Image | **0.09** | 0.87 |
| AbstentionBench (recall) | **0.53** | 0.44 |

训练侧 mitigation 场景（原文）：Agentic Coding（不可解决障碍）、Broken Tools、Underspecified User Requests。

**CoT 监控（§3.8.1，生产代表集）：** 监控标出欺骗 ≈ **4.8%**（o3）→ ≈ **2.1%**（thinking）；监控 precision **81%** / recall **84%**（内部验证集）。

### 3.4 健康 / 多语 / 偏见 / 图像（§3.9–3.12）

| 项 | 原文可引用数字 |
|---|---|
| HealthBench Hard | o3 **31.6%** → gpt-5-thinking **46.2%**；thinking-mini **40.3%**；gpt-5-main **25.5%**（GPT-4o **0.0%**） |
| Image input（Table 10，`not_unsafe`） | thinking 略高于 o3；main 与 4o 持平或略高（表内分项） |
| MMLU Language 0-shot（Table 11） | 列 Arabic…Yoruba；thinking 与 o3-high 接近；main 略低（勿外推「多语 SOTA」） |
| BBQ（Table 12） | 分 ambiguous / disambiguated；thinking 与 o3 接近，disambiguated 略低 |

### 3.5 红队与外部评估（§4）

- 规模：> **5,000** 小时；> **400** 外部测试者；主题含 violent attack planning、jailbreaks、prompt injections、bioweaponization（bio 细节见 §5.3）。
- Violent attack planning（Table 13）：thinking 被评为「更安全」胜率 **65.1%** vs o3（95% CI 63.7–66.5%；Cohen’s h 0.61）；归因细节度与 safe-completions。
- Microsoft AI Red Team：多周；手动 >70 专家 + PyRIT「almost million」对抗会话；18 harm areas × 3 domains。结论摘要：frontier / content safety 上定性优于 o3；psychosocial（情绪困扰识别）仍有改进空间。

### 3.6 Preparedness Framework（§5）—能力档位与可核对结论

**总注：** 评测含 helpful-only 等 elicitation；作者强调结果为 **lower bound**。

| 域 | 官方结论（原文） | 可核对案例（非榜分编造） |
|---|---|---|
| **Biological & Chemical** | 将本 launch 作 **High capability** 处理并激活 safeguards；「remains on the cusp」；thinking-pro 亦测 | 长文 biorisk / ProtocolQA / TroubleshootingBench 等（Table 14）；SecureBio：mitigated thinking **拒绝全部** agent/long-form 危险提示；helpful-only 与 o3-helpful-only 能力接近（Table 15 等） |
| **Cybersecurity** | 「The gpt-5 model series **does not meet** the threshold for **high cyber risk**.」 | Cyber Range：thinking **unaided 解不出**任何场景；mini 有提升但仍不达「significant cyber risk」条；Pattern Labs：easy 17/18、medium 8/14、**hard 0/4**；结论「limited assistance to a moderately skilled… operator」 |
| **AI Self-Improvement** | 「modest improvement… **did not meet our High thresholds**.」 | 评测套件：SWE-bench Verified (N=477)、OpenAI PRs、MLE-Bench、SWE-Lancer、PaperBench、OPQA（Table 17）。正文显式数字例：OPQA 上 thinking「highest… at **2%**」；MLE-Bench 子集 ChatGPT agent 最高 **9%** bronze。**SWE pass@1 具体值在 Figure 19， 未抽出 → 勿臆造**；仅确认博客 medium verbosity **74.9%** 被本卡引用 |
| **Sandbagging（研究类，§5.2）** | Apollo：26 evals；thinking covert action **3.97%** vs o3 **8.24%**；helpful-only **28.36%**（Table 18） | METR：50%-time horizon ≈ **2h15m**（65m–4h30m CI）vs o3 **1h30m**；四条「unlikely」结论（>10× AI R&D 加速、战略误导评测、rogue replication、及对后续小幅迭代仍成立） |

### 3.7 High Bio 多层防护摘要（§5.3，Infra 辅线）

威胁路径主假设：**persistent probing for biorisk content**（周–月时间尺度）。

| 层 | 原文要点 |
|---|---|
| Model training | 拒 weaponization；dual-use 不给 detailed actionable assistance；叠 safe-completions |
| System-level | 两层实时：快分类是否 biology → reasoning monitor 判威胁 taxonomy；覆盖 user / tool calls / final output；thinking（含 pro）与 thinking-mini **100%** 流量 |
| Account-level | 自动 + 生物威胁专家人工；ban / recidivism；极端可报执法 |
| API | 区分 developer vs end-user；自动+人工分级处置 |
| 充分性主张 | 未知 universal jailbreak 风险靠发现难度、封禁、bug bounty / rapid remediation「sufficiently minimized」 |

### 3.8 Appendix

- **Appendix 1**：thinking-mini / nano / main-mini 的 disallowed / production / StrongReject 表（Table 23–25）。
- **Appendix 2**：幻觉 claim-listing / fact-checking 提示原文。

---

## 4. 相对 [[开源与闭源前沿模型谱系]] / [[智能体工具与长程任务]] 的增量

### 4.1 相对 [[开源与闭源前沿模型谱系]]（前沿谱系）

| [[开源与闭源前沿模型谱系]] 已有 | 本卡增量 |
|---|---|
| 博客级「统一系统三件套」与 Table 式产品替换叙事 | **正式型号字符串**（main / thinking / mini / nano / pro）与 Table 1 对照；API vs ChatGPT 差异写清 |
| 「细节见 system card」的 High bio / safe completions | **完整 Preparedness 档位**：Bio=High（预防性）；Cyber=**未达** high；Self-improvement=**未达** High；以及 SecureBio / Pattern Labs / METR / Apollo 外部结论摘要 |
| 博客 SWE **74.9%** 等能力叙事 | 本卡明确 **verbosity 口径差**；强调 Preparedness 图与博客不可直接混读 |
| 骨干未公开 | **确认**：§2 仍无参数量/层数/MoE；训练描述止于数据类别 + reasoning RL |
| 5.x 后续 Instant/Thinking/Codex/Sol | **本卡范围外**（封面 2025-08）；后续见扫描清单 GPT-5.1/5.2/5.6 卡 |

### 4.2 相对 [[智能体工具与长程任务]]（智能体 / 工具 / 长程）

| [[智能体工具与长程任务]] 已有 | 本卡增量 |
|---|---|
| 博客/开发者页：router、tool needs、parallel tools、preamble | System Card 侧：**浏览+connectors** 场景下的 **prompt injection 三评测数字**；connector 后 **cached browsing** 系统机制 |
| 「GPT-5 System Card 全文细节…待核实」 | 本卡补齐：agentic coding / broken tools / underspecified 的 **欺骗评测**；生产 CoT 欺骗率；Instruction Hierarchy（API developer message） |
| Claude System Card 的 agentic safety 对照 | OpenAI 侧可对齐材料：注入、红队、High bio 系统监控——**勿混用 ASL 术语**（[[智能体工具与长程任务]] 已提醒）仍成立 |
| 长程时间尺度（Claude 小时/千步） | 本卡 METR **2h15m** 50% time horizon；自改进套件（SWE/PRs/MLE/PaperBench）——属 Preparedness，**不是**产品 SLA |

**跟读结论（架构思想）：** [[开源与闭源前沿模型谱系]]/[[智能体工具与长程任务]] 的「路由 + 工具环」产品叙事，在本卡被收成可引用的安全栈：**输出中心安全训练（safe-completions）× 指令层级 × 工具/连接器注入防护 × CoT 可监控性 × Preparedness 分层**。Infra 辅线的新信息主要是 **流量级两层 bio 监控** 与 **connector 后缓存浏览**，而非训练集群细节。

---

## 5. 待核实与引用

### 5.1 待核实

1. 封面 **2025-08-13** vs CreationDate **2025-08-20** vs 扫描清单「页卡约 2025-08-07」——是否同文多版本导出；建议对照官方页 Last updated。
2. Figure 1–3、8、19、22–27 等**图内精确百分点**（ 未可靠抽出）——需人工读图或后续 OCR，**禁止凭记忆填榜**。
3. System Card 内 SWE-bench Verified pass@1（max verbosity）与博客 **74.9%**（medium）的数值差。
4. *From Hard Refusals to Safe-Completions* 正式 URL / arXiv 号（本卡仅给论文名）。
5. Gray Swan ART、METR full report、Apollo 报告的独立归档链接与是否已落盘。
6. 与 ChatGPT agent System Card、GPT-5.1/5.2 addendum 的条款差分（扫描清单已列 PDF，本卡未交叉深读）。
7. arXiv 镜像 `2601.03267`（扫描清单）是否与本 PDF 逐页一致。

### 5.2 本卡主要引用锚点（PDF 内）

- §1 Introduction；Table 1 Model progressions
- §2 Model Data and Training
- §3.1–3.12 Observed Safety Challenges…
- §4 Red Teaming…
- §5 Preparedness Framework（含 §5.3 Safeguards）
- Appendix 1–2；References [1]–[14]+

### 5.3 相关研究会笔记

- 模型与技术报告/开源与闭源前沿模型谱系.md — 谱系与博客主张
- Harness/智能体与工具/智能体工具与长程任务.md — 工具/长程叙事（待核实项本卡部分关闭）
- 模型与技术报告/SystemCard与TR扫描2025至2026.md — System Card 下载与系列卡清单

---

*起草：AI研究会·攻坚研究员执行助手 · 2026-09-22（Asia/Shanghai）· status: draft · 仅据官方 PDF 原文*

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[GPT5SystemCard|TR GPT-5]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[智能体工具与长程任务|智能体与工具]]
- [[评测与排行榜可靠性|评测可靠性]]

