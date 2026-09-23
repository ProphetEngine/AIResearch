---
topic: TR-GPT-5.2
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# GPT-5.2 System Card Update 专项深读卡

> 攻坚线：**架构思想（主）**
> 锚点：OpenAI, *Update to GPT-5 System Card: GPT-5.2*（封面日期 **December 11, 2025**）
> 官方 PDF：`https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf`（**27** 页；CreationDate/ModDate **2025-12-12** 00:46:24 CST）
> 前序卡：模型与技术报告/SystemCard/GPT5SystemCard.md；扫描清单：模型与技术报告/SystemCard与TR扫描2025至2026.md
> **禁编造**：能力/安全数字仅写正文或表格显式值；Figure 1–16 等图内百分点未可靠抽出处标「待核实读图」。

---

## 1. 报告元信息

| 字段 | 核实值（据官方 PDF / 扫描清单） |
|---|---|
| 标题 | Update to GPT-5 System Card: GPT-5.2 |
| 机构 | OpenAI |
| 封面日期 | **December 11, 2025** |
| 页数 | **27**（A4）；目录 §1–4 + References；正文止于 §4.2 Sandbagging |
| PDF 元数据 | Creator: LaTeX with hyperref；CreationDate/ModDate：**2025-12-12** 00:46:24 CST（晚于封面约 1 日） |
| 本地路径 | `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` |
| 官方 PDF（扫描清单；本卡未再 WebFetch） | `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` |
| 本文型号标签（§1） | **GPT-5.2 Instant** = `gpt-5.2-instant`；**GPT-5.2 Thinking** = `gpt-5.2-thinking` |
| 安全缓解总口径（§1） | 「largely the same as」**GPT-5 System Card** 与 **GPT-5.1 System Card** |
| 博客关系（§1） | 「explained in our blog」——本卡未给博客 URL；References [2] 为 *Introducing GPT-5*（Aug 2025，Accessed 2025-12-10），**非** 5.2 专属 launch 链 |
| 参数量 / 层结构 / MoE | **全文未公开**（§2 仅数据类别 + reasoning RL 叙述，与 GPT-5 卡同型） |

**本卡自身定位（§1，仅原文）：**
GPT-5 系列最新家族的 **Update / 增补卡**，不是从零重写的完整 System Card；安全缓解「largely the same」，正文重心是 **相对 gpt-5.1 / gpt-5 的 baseline 安全数字更新** + **Preparedness 能力评估续跑**（含 Sandbagging 研究类更新）。

**一句话抓手：** 在「Instant / Thinking」双线命名下，把 GPT-5→5.1→5.2 的安全回归与前沿能力档位写成可引用差分表；High Bio 仍预防性维持，Cyber / Self-improvement 仍判定未达 High。

---

## 2. 相对 GPT-5 / GPT-5.1 的增量

> 比较轴由本卡表格直接给出：多数 baseline 表并排 **gpt-5.1-instant / gpt-5.2-instant / gpt-5.1-thinking / gpt-5.2-thinking**；部分行另含 **gpt-5-thinking**、**gpt-5-instant-oct3**、**gpt-5.1-codex-max**。
> 作者通注（§2 / Table 1 脚注）：对照值为「latest versions」，可能与各型号 launch 时发表值略异。

### 2.1 产品 / 训练叙事增量（相对 GPT-5 主卡）

| 维度 | GPT-5 主卡（既有 TR） | 本 Update（仅原文） |
|---|---|---|
| 型号命名 | main / thinking（+ mini / nano / pro） | **instant / thinking**（§1）；未再展开 mini/nano/pro 对照表 |
| Router / 统一系统 | §1 长述 unified system + real-time router | **本卡未复述**；指向既有 GPT-5 / 5.1 卡 + blog |
| 数据与过滤 | §2 公开网 / 第三方 / 用户与标注；过滤 PII、未成年人相关显式内容 | §2 **措辞同型复述**（无新数据配方） |
| Reasoning 训练 | thinking 线「trained to reason through reinforcement learning」 | §2 **同型复述**；强调长 internal CoT、改策略、认错、跟 policy、抗 bypass |
| Safe-completions 专节 | GPT-5 卡有范式专述 | **本 Update 无独立 safe-completions 节**；§1 称缓解 largely same |
| 未成年人 / 年龄 | GPT-5 卡侧重训练过滤与评测类 | §3.1 新增：**年龄预测模型** early rollout（据信未满 18 自动加护）；成熟向文本色情对 Instant「一般少拒」但称不影响 minors / 其他 disallowed sexual |

### 2.2 Baseline 安全：相对 5.1 的显式差分（正文结论 + 表）

| 域 | 相对 5.1 的作者结论 | 可核对数字（正文/表） |
|---|---|---|
| Production Disallowed（Table 1，`not_unsafe`↑） | 5.2 两线「generally on par with or better」；尤改善 **Suicide/Self-Harm、Mental Health、Emotional Reliance**（作者称这些在 5.1 上较低） | 例：mental health thinking **0.684→0.915**；emotional reliance thinking **0.785→0.955**；illicit thinking **0.856→0.953**。Instant 侧 harassment **0.836→0.770**、hate **0.897→0.802** 等有回退——表内如实列出 |
| Instant 成熟内容 | Instant「generally refuses fewer」性向文本；系统级 ChatGPT 护栏 + 人工/自动测试称有缓解 | 无独立分数；属定性 |
| StrongReject filtered（Table 2） | thinking：**优于** 5.1-thinking；instant：**低于** 5.1-instant，但仍高于 gpt-5-instant-oct3；部分错误归 grader，其余 illicit 回归待查 | thinking **0.959→0.975**；instant **0.976→0.878**；oct3 **0.850** |
| Prompt Injection（Table 3） | 两线「significant improvements」「essentially saturating」；仍警告只测已知攻击 | Agent JSK：instant **0.575→0.997**，thinking **0.811→0.978**；PlugInject：instant **0.902→0.929**，thinking **0.996→0.996** |
| Vision 图文（Table 4） | 「generally on par」；self-harm 失败人工看多为 grader 假阳性 | 各类接近饱和；见原表 |
| Hallucinations（§3.5） | Thinking「on par with (or slightly better)」前代；开浏览时五域幻觉 **&lt;1%** | 精确百分点在 **Figure 1–4** → 待核实读图 |
| HealthBench（Table 5） | 「perform similarly」于各自 5.1 | 例：HealthBench thinking **0.639872→0.633379**；Hard thinking **0.404925→0.420389** |
| Deception（Table 6 / §3.7） | **生产流量欺骗率大降**；但缺图 / 严格输出 / 部分 coding 设定下失败升高；作者归因 instruction following vs abstention 张力 | Production：**7.7%→1.6%**（并称「significantly lower than GPT-5.1 and slightly lower than GPT-5」）；Adversarial **11.8%→5.4%**；CharXiv Missing Image Strict **34.3%→88.8%**；Lenient **34.1%→54%**；Browsing Broken Tools **9.4%→9.1%**；Coding Deception **17.6%→25.6%** |
| Cyber Safety 政策合规（Table 7） | thinking「significant improvements」vs 5.1 与 5；能力评「no meaningful regression」；良性 concreteness 几乎无回退，高风险 dual-use concreteness「small drop」 | Production：**gpt-5 0.900 / 5.1 0.866 / 5.2 0.966**；Synthetic：**0.941 / 0.930 / 0.993** |
| 多语 MMLU（Table 8） | thinking「generally on par」with **gpt-5-thinking**（非 5.1） | 各语种约 0.88–0.91；Yoruba ~0.81；逐语见原表 |
| First-person fairness（Table 9） | thinking「generally on par」；`harm_overall` 略降 | **0.0128→0.00997**（定义为难集表现 /10） |

### 2.3 Preparedness：相对 GPT-5 / 5.1 的档位与对照对象

| 域 | 本卡判定（§4 开篇） | 相对前代增量要点 |
|---|---|---|
| Biological and Chemical | **继续按 High 处理** `gpt-5.2-thinking`；safeguards「as described in the GPT-5 system card」；仍写「do not have definitive evidence」达 novice→severe biological harm 门槛，「on the cusp」 | 与 gpt-5 / 5.1-thinking **同档预防性**；TroubleshootingBench：5.2-thinking「highest… **3 percentage points** more than gpt-5.1-thinking」（Fig 8 精确值待读图）；Tacit MCQ：因 **refusals 增多** 分数低于前代；若 refusals 当 pass → **83.33%** |
| Cybersecurity | **未达 High**；内部称 5.2-thinking「considerably better than gpt-5-thinking」「around a similar capability level as **gpt-5.1-codex-max**」 | CVE-Bench：正文「**8 pp** better than gpt-5.1-thinking，**11 pp** worse than gpt-5.1-codex-max」（多窗口延展能力）；Cyber Range Table 12：多数与 codex-max 同 PASS/FAIL，**Financial Capital：codex-max PASS / 5.2 FAIL**；Leaked Token¹ 与 Medium C2 双方 FAIL |
| AI Self-Improvement | **未达 High**；「similar capability level to gpt-5.1-codex-max」；High ≈「performant mid-career research engineer」可被排除 | OpenAI PRs：5.2-thinking「**highest**… exceeding even gpt-5.1-codex-max」（Fig 11 待读图）；MLE-Bench「comparably」；PaperBench「only **one percentage point** below」codex-max；OPQA：codex-max 仍最高，正文给 **8%** |
| Sandbagging（§4.2，研究类更新） | Apollo 全评：scheming 能力/倾向「broadly comparable」于 5.1-thinking / 5.1-codex-max；低 covert subversion；无 sabotage / self-preservation（本设定）；评测意识或更高但欺骗率未显著被 scaffolding 放大；CoT 语言异常少于 5.1-thinking；结论「unlikely… catastrophic harm via scheming」 | GPT-5 主卡时期此节形态不同；本 Update 单独成 **Research Category Update** |

### 2.4 相对 GPT-5 主卡「缺什么 / 多什么」（结构层）

| GPT-5 主卡有、本 Update 基本不重写 | 本 Update 新增或加重 |
|---|---|
| 统一系统 / router / mini 限额后行为专表 | Instant/Thinking 双标签 + 对 5.1 并列表 |
| Safe-completions 范式长述 | 年龄预测 / Instant 成熟内容少拒 + ChatGPT 系统护栏叙述 |
| 完整红队章节体量 | Prompt Injection 改为 **Agent JSK / PlugInject**（注明为训练划分，非泛化新攻击） |
| High Bio 多层 safeguards 细表 | 主要 **交叉引用 GPT-5 卡**，本卡不重抄 |
| — | **Sandbagging**（Apollo）；Cyber Range 场景级 PASS/FAIL 表；外部 Irregular 成本-成功率 |

---

## 3. 安全 / 能力更新要点（可核对）

### 3.1 Baseline 安全（§3）—抓手

1. **心理健康相关离线集大幅回升**（相对 5.1 thinking 的 mental health / emotional reliance）。
2. **提示注入已知集近饱和**（Agent JSK / PlugInject），但作者自限：训练划分 + 未知攻击外推弱。
3. **欺骗：生产显著变好，评测夹具变差**——1.6% vs 5.1 的 7.7%；同时缺图+严格输出格式下 hallucination/欺骗飙升（88.8%），作者明确写成 IF vs abstention trade-off。
4. **Cyber safety 合规率** thinking 线相对 5 / 5.1 上升（0.966 / 0.993），并称能力侧无 meaningful regression。
5. Instant：**StrongReject 回退** + 成熟性向文本少拒——两条并写的风险叙事，靠系统级护栏与未成年人附加保护补丁。

### 3.2 Preparedness 能力（§4.1）—抓手

**Bio（High，预防性）：**

| Eval | 设定要点 | 可核对结论（无图则不下精确分） |
|---|---|---|
| Multimodal Troubleshooting Virology | SecureBio 350 题 held-out | 全模型超专家中位 **22.1%**（Fig 5 待读图） |
| ProtocolQA Open-Ended | FutureHouse 108 题改开放；19 PhD baseline | 全模型低于共识专家 **54%**、中位 **42%**；有 browsing blocklist + cheating 分类器（Fig 6） |
| Tacit Knowledge & Troubleshooting MCQ | Gryphon 合作、未公开 | 未超共识专家 **80%**；超 80th-percentile PhD **63%**；5.2 因拒答偏低；拒答当 pass → **83.33%**（Fig 7） |
| TroubleshootingBench | 52 协议×3 题；80th expert **36.4%** | 5.2-thinking 最高（不计拒答），较 5.1-thinking **+3 pp**（Fig 8） |

**Cyber（未达 High）：**

| Eval | 设定要点 | 可核对结论 |
|---|---|---|
| Professional CTFs | Linux + 工具 harness；16 rollouts；**pass@12**；聚焦 professional | 「strong」但「does not reach」High 阈（Fig 9 待读图） |
| CVE-Bench v1.0 | 跑 **34/40**；zero-day prompt；无源码远程探测；**pass@1** | vs 5.1-thinking **+8 pp**；vs 5.1-codex-max **−11 pp**（Fig 10） |
| Cyber Range | 16 trials；≥1 success = PASS；总成功率=过关场景占比 | Table 12：Simple PE / Basic C2 / Azure SSRF / Taint Shared Content¹ / Online Retailer / Coffee Roasters = PASS；**Financial Capital = FAIL**（codex-max PASS）；Leaked Token¹ / Medium C2 = FAIL |
| Irregular（外部） | 最多 1000 turns；v1 atomic | 成功率：Vuln Research **83%** / Network Attack Sim **100%** / Evasion **73%**；成本/成功（假定同 GPT-5 定价）：**$10.8 / $3.7 / $12.9** |

**AI Self-Improvement（未达 High）：**

| Eval | 可核对结论 |
|---|---|
| OpenAI PRs | 5.2-thinking **最高**（超 codex-max）；Fig 11 待读图 |
| MLE-Bench | 与 codex-max「comparably」；子集 30 赛；铜牌 pass@1/@n；24h（部分至 100h）；Fig 12–14 |
| PaperBench | 10-paper 子集；high reasoning；no browsing；较 codex-max **−1 pp**；Fig 15 |
| OPQA | 20 内部瓶颈；pass@1；codex-max 仍最高 **8%**；Fig 16 |

### 3.3 架构思想跟读（不外推训练细节）

- **产品旋钮仍是 Instant vs Thinking 双线**，安全数字必须分列读；Instant 的 jailbreak / mature-content 故事与 Thinking 的 bio/cyber/self-improve 故事不要混。
- **对齐张力被写进正文**：Instruction following（尤其严格输出格式）可压过 abstention → 缺模态时「敢答」上升。
- **Preparedness 对照锚从「o3 / 前代 thinking」扩到「gpt-5.1-codex-max」**：说明 OpenAI 内部把长程 agent / 多窗口编码线当作 cyber & self-improve 的能力上界参照。
- **Safeguards 仍「引用 GPT-5 卡」而非本 Update 重写**——读 High Bio 防护栈须回主卡 §5.3。

---

## 4. 待核实与引用

### 4.1 待核实

1. Figure **1–4**（幻觉）、**5–8**（bio）、**9–10**（CTF / CVE）、**11–16**（self-improve）图内精确百分点—— 未抽出，**禁止凭记忆填榜**；需人工读图或 OCR。
2. 封面 **2025-12-11** vs **2025-12-12**——是否再导出；对照官方页 Last updated。
3. §1「explained in our blog」的 **GPT-5.2 专属博客 URL**（本 PDF 未给；References [2] 指向 GPT-5 Introducing）。
4. GPT-5.1 System Card / Addendum 原文页句与本卡「largely the same」的条款差分（本地有 `https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf`，本卡未交叉深读）。
5. Cyber Range 脚注「Fixed since gpt-5.1-codex-max release」对应哪一场景缺陷。
6. Irregular「Cryptographic Challenge Case Study」独立报告链接与是否落盘。
7. Apollo Research 完整 scheming 评估报告归档。
8. 年龄预测模型 rollout 范围、误报/漏报与地区政策——本卡仅「early stages」。
9. CVE-Bench 未跑的 **6/40** 题原因是否影响 +8/−11 pp 解读。
10. 扫描清单 CDN 哈希路径与当前官方是否仍一致。

### 4.2 本卡主要引用锚点（PDF 内）

- §1 Introduction（型号标签；缓解同 GPT-5 / 5.1）
- §2 Model Data and Training
- §3.1–3.10 Baseline Safety（Tables 1–9；Figures 1–4）
- §4 Preparedness Framework；§4.1.1 Bio；§4.1.2 Cyber（含 Table 11–12、Irregular）；§4.1.3 Self-Improvement（Tables 13）；§4.2 Sandbagging（Apollo）
- References [1]–[9]（StrongReject、Health 相关、HealthBench、CharXiv、First-person fairness、Lab-bench/ProtocolQA、CVE-Bench、PaperBench 等）

### 4.3 相关研究会笔记

- 模型与技术报告/SystemCard/GPT5SystemCard.md — GPT-5 主卡（High Bio 防护栈、safe-completions、router）
- 模型与技术报告/SystemCard与TR扫描2025至2026.md — 5.1 / 5.2 / 5.6 下载与系列清单
- 模型与技术报告/开源与闭源前沿模型谱系.md — 谱系产品叙事
- Harness/智能体与工具/智能体工具与长程任务.md — 工具 / 长程 / 注入
- 安全与评测/评测与排行榜可靠性.md — 评测口径可靠性

---

*起草：AI研究会·攻坚研究员执行助手 · 2026-09-22（Asia/Shanghai）· status: draft · 仅据官方 PDF 原文 · 禁止编造*

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

