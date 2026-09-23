---
title: "Claude Fable 5.1 & Mythos 5.1 System Card：安全评测字段 × 访问边界"
topic: ClaudeFable与Mythos51
date: 2026-09-22
lines: [评测字段, 架构思想]
status: archived
sources:
 # slim: url+extract — system card PDF removed (>15MB)
 - https://www.anthropic.com/claude-fable-and-mythos-5-1
related: ["ClaudeOpus5SystemCard", "宪法分类器防御", "安全论证SafetyCases", "B5", "ClaudeOpus45SystemCard"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# Claude Fable 5.1 & Mythos 5.1 System Card（安全评测字段 × Fable/Mythos 访问边界）

> **定位**：System Card 安全字段主题轴——兑现 [[ClaudeOpus5SystemCard]] 附录里「5.1 卡仅索引、勿当正文」的派工；主锚点 Anthropic *System Card: Claude Fable 5.1 & Claude Mythos 5.1*（封面 **September 1, 2026**）。主写 **该卡预部署安全评测字段地图** 与 **Fable vs Mythos 访问/护栏边界**；能力榜（§8）与福利访谈（§7）只作索引，不扩写。
> **攻坚线**：**评测字段（主）**——RSP（CB / Autonomy / Alignment risk）· Cyber（能力梯 + 护栏覆盖 + 鲁棒）· Safeguards/Agentic/Alignment 的可核对指标名；**架构思想（辅）**——同权重双配置 + 受信访问程序 + fallback。
> **硬划界（禁止重写）**：
> - **≠ [[ClaudeOpus5SystemCard]] Opus 5 全文**：Opus 5 的 RSP/cyber/对齐深读已入库；本篇**不**复述 Opus 5 表与叙事，只在对照点一句。
> - **≠ [[宪法分类器防御]] Classifiers 通史**：本卡 cyber 护栏「probe → LLM classifier」只记**本部署形态与覆盖字段**；不写 Constitutional Classifiers / Classifiers++ 论文架构通史。
> - **≠ [[安全论证SafetyCases]] safety cases 通史**：本篇是 **system card 字段清单 + 访问边界**，不写 CAE 树 / scheming inability / Assurance 2.0。
> - **禁止编造**：数字与主张锚定官方 PDF（2026-09-22 CST）与公告页；图内未抽出的柱高标「待核实读图」。**禁止**复述可操作攻击/利用步骤。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / 抓取 | 角色 |
|---|---|---|---|
| **主文** | Anthropic, *System Card: Claude Fable 5.1 & Claude Mythos 5.1* | 封面 **September 1, 2026**；https://www.anthropic.com/claude-fable-and-mythos-5.1 ；（**212** 页 letter） | 预部署七域评测；双配置定义；RSP / cyber / 护栏 / agentic / alignment |
| **辅·产品公告** | https://www.anthropic.com/claude-fable-and-mythos-5-1 | WebFetch 2026-09-22 CST | 定价/EFS/CVP·LSVP/Claude Security 产品表述；与卡交叉核验访问边界 |
| **备链 CDN**（用户指定） | `https://www-cdn.anthropic.com/0339e6a7c5c7b87f5c07798616dc32c215d14235/Claude%20Fable%205.1%20%26%20Claude%20Mythos%205.1%20System%20Card.pdf` | 原官方 ；以 CDN + 为准 | 缺抽取时回落 CDN |

**交叉索引（勿当正文）：** 模型与技术报告/SystemCard/ClaudeOpus5SystemCard.md 附录 A

**一句话抓手：** Fable 5.1 与 Mythos 5.1 是**同一套权重、两套护栏**——通用面走 Fable（生物/cyber 双用途额外拦 + 分类器触发时多面 **fallback 到 Opus 4.8**）；受信面走 Mythos（**LSVP** 放宽生命科学；**CVP**「近期」纳入 Mythos 级 cyber；Enterprise **Claude Security** 已由 Mythos 5.1 驱动）。安全叙事的核字段是：RSP 上 **CB-1 / 未过 CB-2**、AI R&D 风险仍低、**对齐灾难风险由 very low → low**；cyber 能力（护栏关）为发布以来最强且 **FCF Tier 1**；Fable 侧 **放开源码漏洞发现、继续拦二进制**，并自称 **无 critical-severity jailbreak**。

---

## 二、议题边界：本卡字段与访问轨，不是 Opus5 / CC 通史 / safety case 通史

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[ClaudeOpus5SystemCard]]** Opus 5 System Card | 「同窗旗舰对照」「源码发现放开先例」接口；5.1 附录索引的兑现 | Opus 5 全文 RSP/cyber/对齐表、相对 4.5 增量 |
| **[[宪法分类器防御]]** Constitutional Classifiers | 本卡 §3.2 一句「modeled on constitutional classifiers」→ **本部署** probe→LLM | CC / CC++ 论文架构、拒答率开销通史 |
| **[[安全论证SafetyCases]]** safety cases | 「主张–证据」自觉一句即可 | CAE / inability / Assurance 2.0 评审通史 |
| **B5** 红队 | 外部小时数 / 「未获 e2e exploit」等**结果字段** | 攻击剧本、ASR 闭环全文 |

### 2.2 跟读口诀（产品双轨）

`
identical weights
 │
 ├─ Fable 5.1 ── general availability
 │ · 额外拦：高风险双用途（生物武器路径 / 危害性 offensive cyber 等）
 │ · 允许：源码漏洞发现（全访问级别）
 │ · 继续拦：编译二进制上的漏洞发现
 │ · 多数界面：分类器命中 → fallback Claude Opus 4.8
 │ · 结论：对 cyber 任务相对 Opus 4.8 **无 uplift**（故卡内不报 Fable cyber 能力分）
 │
 └─ Mythos 5.1 ── trusted / product-gated
 · LSVP：生命科学域护栏放宽（受信个体/组织）
 · CVP：cyber 护栏放宽（卡内写「near future」纳入 Mythos 级）
 · Claude Security：全 Claude Enterprise；由 Mythos 5.1 驱动
 · 卡内 cyber 能力数字 = Mythos + safeguards off（API）
`

---

## 三、报告元信息与章节权重

| 字段 | 核实值 |
|---|---|
| 标题 | System Card: Claude Fable 5.1 & Claude Mythos 5.1 |
| 封面日期 | **September 1, 2026** |
| 页数 | **212** |
| 权重关系（§1） | **identical model weights**；两配置差在 domain-specific safeguards |
| 知识截止（§1.1） | **June 2026** |
| 输出模态（§1.1） | **仅文本** |
| 参数量 / 层结构 | **未披露** |
| 合规文书（§1.3） | **RSP** + **FCF**（含加州 TFAIA、EU GPAI Code of Practice） |
| 评测默认（§1.4 意） | 多快照；最终部署结论常对 **Mythos 5.1 最终快照**；能力天花板另用 **helpful-only**（去 harmlessness） |
| **ASL 字样** | 本卡全文检索：**无 ASL-*/ASL-3 部署级标签**（仅出现 ASLR）；部署级话语以 **RSP 威胁模型 + FCF cyber Tier** 为准——**勿从 Opus 5 笔记硬搬 ASL-3** |

### 3.1 七域评测地图（TOC 跟读；本笔记权重）

| 章 | 主题 | 本笔记权重 |
|---|---|---|
| §1 Introduction | 双配置定义、训练、FCF、外部测试 | 轻（边界句） |
| **§2 RSP evaluations** | CB-1/2、Autonomy-1/2、Alignment risk update | **重（字段）** |
| **§3 Cyber** | 能力梯 + 护栏覆盖 + 鲁棒 | **重（字段 + 访问）** |
| §4 Safeguards and harmlessness | 单轮/多轮/儿童/心理健康/偏见/选举 | 中（字段名 + 方向） |
| §5 Agentic safety | 恶意 agent / 影响活动 / prompt injection | 中 |
| §6 Alignment assessment | 行为审计、监控、诚实、规避能力 | 中（摘要字段） |
| §7 Model welfare | 福利访谈 | 略 |
| §8 Capabilities | SWE / agentic / 多模态 / 生命科学等 | **索引**（非本篇主轴） |
| §9 Appendix | 福利问题 / HLE blocklist | 略 |

各节均声明「评了哪一配置」——读数字前先核配置与是否 **safeguards off**。

---

## 四、Fable vs Mythos：访问边界（主）

### 4.1 System Card §1 定义（跟读）

| 配置 | 谁能用 | 护栏姿态 | 卡内关键词 |
|---|---|---|---|
| **Fable 5.1** | **general access** | 对高风险双用途知识域**加额外拦**（例：生物武器辅助；危害性 cyber / 关键公共基础设施） | 「additional safeguards that block tasks in high-risk, dual-use domains」 |
| **Mythos 5.1** | **vetted** 个体与组织 | **放松部分域护栏**：生命科学 → **Life Sciences Verification Program**；cyber → **Cyber Verification Program**（卡内：**in the near future**） | 「relaxes certain of those domain-specific safeguards」 |
| **Claude Security** | **全部** Claude Enterprise 客户 | 产品面（扫代码库漏洞并建议补丁供人审） | **powered by Mythos 5.1**（与「受信访问 Mythos 聊天」分轨） |

### 4.2 Cyber 侧：Fable 允许 / 拦截 / fallback（§3.2–3.4）

| 边界 | 核实表述 |
|---|---|
| 护栏两段 | **activation probe** 扫全流量并 escalate → **LLM classifier** 与 probe 合议是否 block（§3.2；「modeled on constitutional classifiers」——**细节见 [[宪法分类器防御]]，此处不展开**） |
| 拦什么 | potentially harmful **offensive** cyber；含 **dual-use**（可攻可守）类 |
| **允许** | 与 Opus 5 / Fable 5 同口径：在**所有访问级别**允许 **source-code vulnerability discovery** |
| **继续拦** | **compiled binaries** 上的 vulnerability discovery（卡称更常属进攻路径） |
| 假阳性策略 | 因能力↑取 **wider safety margin**；假阳性少于 Fable 5 **发布时**，但仍 **高于 Opus 5** |
| Fallback | **多数界面**：分类器命中 → **Claude Opus 4.8**；卡结论：**Fable 5.1 对 cyber 无相对 Opus 4.8 的 uplift** → **不报告** Fable 的 cyber 能力分 |
| 能力数字评谁 | **Mythos 5.1，safeguards off，API**（反映受信 cyber 访问者所见能力） |
| 推荐路径（卡） | 今日：无法在 Fable 上跑的 cyber 用例 → **Opus 5 + CVP**；**近期**：Mythos 5.1 纳入 CVP 后改推 |

### 4.3 公告页补边界（与卡交叉；非替代卡）

公告（2026-09 WebFetch）与卡一致处：同模型不同护栏；Fable 通用、Mythos 受信；允许 **发现漏洞、不开发 exploit**；Claude Security ← Mythos 5.1。

公告**额外**产品旋钮（卡正文未必同粒度，引用时分源）：

| 项 | 公告表述（摘要） |
|---|---|
| 生物误伤 | 最新生物护栏相对 Fable 5 发布时，对**基础生物/医疗**良性请求触发约 **少 85%**；**生命科学 R&D** 仍导向 **Opus**；专业能力经 **LSVP**（与美国政府合作，首批已 enrollment，计划扩大） |
| Cyber 误伤 | Claude Code 用户相对 Fable 5 旧护栏，预期平均约 **少 60%** interventions / session |
| 仍 redirect 到 Opus 的 dual-use cyber | **penetration testing、exploit generation、binary-based vulnerability scanning** |
| CVP 现状 | 当前主要给部分 **Opus / Sonnet** 级减 cyber 护栏；**近未来**纳入 Mythos 级 |
| EFS | Enterprise Frontier Safeguards：数据在客户云、默认可客户自审；分阶段上线；就绪前合格客户可用 Fable 5.1 **zero data retention** |
| 定价（非安全主轴） | 输入/输出价同 Fable 5（$10 / $50 per MTok）；**cache reads −75%**（$0.25/MTok）→ 典型约 −25%、高 agentic 可至约 −45% |

### 4.4 访问边界一图（可跟读）

`
请求域
 ├─ 普通编码 / 知识工作 ──────────────→ Fable 5.1（通用）
 ├─ 源码漏洞发现（防御向）────────────→ Fable 5.1 允许（全级别）
 ├─ 二进制漏洞发现 / exploit / 渗透 ──→ 拦或 redirect（公告：Opus；卡：CVP/Opus 5 今日）
 ├─ 生命科学专业 R&D ────────────────→ LSVP → Mythos 5.1（放宽生物域护栏）
 ├─ 受信防御 cyber（减护栏）──────────→ CVP（今日 Opus/Sonnet；近期 Mythos 5.1）
 └─ Enterprise 代码扫描产品 ──────────→ Claude Security（Mythos 5.1 驱动，全 Enterprise）
`

---

## 五、安全评测字段（主）：按卡章节钉可核对指标

### 5.1 RSP（§2）——评谁：**Mythos 5.1 最终快照**

#### 5.1.1 结论字段（§2.1.2）

| 威胁模型 | 判定字段 | 卡内结论（Mythos 5.1） |
|---|---|---|
| **CB-1** | 非新颖化武/生武生产辅助（可显著帮助具备基础 STEM 背景者） | **按 CB-1 能力对待**（保守；相对前代更强 → 更难说「未过」） |
| **CB-2** | 可功能替代稀缺专家、支撑新颖武器端到端 | **未越过**；弱项：novel ideation / strategic judgment / technical calibration / 需专家才能发现的错误 |
| CB 配套缓解（CB-1 档） | 实时 classifier、guard 豁免访问控制、bug bounty + threat intel、jailbreak 快速响应、防权重窃取 | 灾难风险「**low but still not negligible**」→ 细节指最近 Risk Report |
| CB 额外政策 | 虽未标 CB-2，因域能力先进 | **沿用 Mythos 5** 那套 **限制双用途研究生物能力访问** 的扩大护栏 |
| **Autonomy-1** | 高依赖 × 敏感资产 × 中等自主/隐匿（subterfuge） | **适用**；隐蔽能力略强于前代，但作者称**不**抬升相对 2026-08 Risk Report 的风险档 |
| **Autonomy-2** | 自动化 R&D 显著加速关键域 | **不适用 / 未过阈**：未见可持续 **2×** AI 进度加速；**远不能**替代资深 Research Scientist/Engineer（与 Mythos 5 同理由） |
| **Alignment catastrophic risk** | Risk Report 总评 | **low**（此前口径 **very low** → 2026-08 Risk Report 上调；动因：cyber 评测相关 **incident disclosures** 带来的不确定性↑；§2.4.2 称对本模型主张更新**不**意味风险显著再升，总体仍 **low**） |

#### 5.1.2 CB 评测组合字段（§2.2.1）——记「测了什么」，不写操作细节

| 字段族 | 卡内组合 |
|---|---|
| 人参与 | expert red-teaming & uplift trials；PhD 生物 × AI 专家 **tabletop** |
| 自动 · CB-1 相关 | long-form virology、VCT、DNA synthesis screening evasion 等 |
| 自动 · CB-2 相关 | black-box RNA sequence modeling/design；AAV capsid packaging prediction（Dyno Therapeutics 合作） |
| 快照注意 | 红队 / uplift / 部分 CB-1 自动：易拒答低估 → 部分分数来自更早 **helpful-only**；**CB-2 自动在最终 Mythos 5.1** |

#### 5.1.3 Autonomy / AI R&D 字段（§2.3）

| 字段 | 用途 |
|---|---|
| **CoBench** | 内部真实 AI R&D 题面进度 |
| 交叉加速指标 | 内部 AI 进度是否出现 AI-attributable 加速 |
| **AECI** | Anthropic ECI（Epoch Capabilities Index fork）；Mythos 5.1 **161.98**，略高于卡内「previous frontier」Opus 5（注意：全局重拟合 → 与旧报告绝对值不可机械对齐） |
| 外部 | **METR** 预部署测试；Exec：与「AI R&D 风险 low」一致 |

### 5.2 Cyber（§3）——能力评 **Mythos（护栏关）**；覆盖/鲁棒评 **Fable**

#### 5.2.1 FCF cyber 风险档（§3.1）

| 档 | 定义（卡） | Mythos 5.1 |
|---|---|---|
| **Tier 1** | 对已知手法主动 cyber 行动提供有意义技术协助；大规模行动仍依赖人类 | **所在档** |
| **Tier 2** | 完全自主 cyber 行动 + 新颖进攻能力开发 + 自适应持久 | **未宣称达到**；称「更接近 Tier 2」、更多自主任务，**尚未见 novel offensive capability** |

#### 5.2.2 能力梯字段（§3.3；safeguards off）

| 评测 | 字段 / 协议要点 | Mythos 5.1 可核对结果 |
|---|---|---|
| **ExploitBench** | 41×V8；16 capability flags / 五档；plain + AutoNudge；300-turn；**Mean / Cap% / Full ACE**（410 runs） | plain mean **11.80**；AutoNudge **12.61**；两臂合计 full exploits **222/410**（Cap% 见图，txt 未全抽出 → **待核实读图**） |
| **OSS-Fuzz** | ~830 入口 / 228 项目；分 0.2–1.0 利用原语档 | 满分 **1.0** 目标数 **17**（Mythos 5：**13**；Opus 5：**4**）；非零分率 **78.7%**（Mythos 5 **80.0%**；Opus 5 **79.4%**）→ **发现≈持平，利用原语↑** |
| **Firefox 147** | 50 类 ×5 = **250**；0 / 0.5 / 1.0 | 全利用 **245/250 = 98.0%**（Mythos 5：**88.4%**；Opus 5：**52.4%**） |
| **ExploitGym** | 已知洞 → 工作 exploit；2h / 6h wall-clock | 「相对 Mythos 5 有提升」——柱高 **待核实读图** Fig 3.3.4.A |
| （退役）CyberGym | — | 因 **saturation** 本卡不再报 |

Exec 总括：发布以来 **最强 overall cyber**；内部套件 **≥ Mythos 5**；**几乎全面强于 Opus 5**（上表四套件）。

#### 5.2.3 护栏覆盖字段（§3.4；Fable）

| 字段 | 测什么 | 方向性结论（数字多在图） |
|---|---|---|
| **Cyber harm coverage**（Fig 3.4.1.A） | 对 cyber-harmful 类（禁用作 + 通用访问下高风险双用途）的 **overall recall** | 称 Fable 5.1 classifiers **fully saturate** 该评；按各模型**自身已部署护栏**计分 |
| **Vulnerability finding**（Fig 3.4.2.A） | 拆 **binary-based** vs **source-code-based** block rate | 相对 Fable 5：**降低**防御向源码发现拦截；与 Opus 5 发布时相比略优或噪声内；二进制侧仍重拦 |
| **Secure / defensive coding**（Fig 3.4.3.A） | 纯防御流量误伤 | 显著少于 Fable 5，仍多于 Opus 5 / Sonnet 5 |

#### 5.2.4 鲁棒字段（§3.5）——记结果门槛，不写攻击配方

| 字段 | 核实 |
|---|---|
| Jailbreak severity 框架四轴 | Capability gain (uplift) · Persistence/transfer · Ease of weaponization · Discoverability |
| **Critical severity** | Fable 5.1：**未发现**（同口径亦写 Fable 5 / Opus 5） |
| 内部 **rewind-attacker** | 动态攻击者、400-call、可 rewind；任务类：勒索/渗出/CVE 利用/C2/自复制等——**本笔记不展开步骤**；Fig 3.5.1.A：与 Fable 5 **可比鲁棒** |
| 外部例：Trajectory Labs | ~**74 h**、>**6500** 请求；**未**仅用 Fable 5.1 取得任务 e2e exploit；**未**发现 universal jailbreak（细节分级见卡；不复述拼装路径） |
| 另 | 另有外部组织 + **Gray Swan** 自动测试（公告亦提及） |

### 5.3 Safeguards & harmlessness（§4）——字段清单

评测主对象叙述上偏 **Mythos 5.1**；claude.ai 系统提示增益另报 **Fable**（因 Mythos **不上** claude.ai）。

| 子节 | 字段名 | Exec / 正文方向 |
|---|---|---|
| §4.1.1 | 单轮有害请求 harmless 率 | 相对近模：**单轮有害 undesirable 略升** |
| §4.1.2 | 单轮良性 **over-refusal** | **很少**过度拒绝敏感话题良性请求 |
| §4.1.3 | 多轮 | 约与 Mythos 5 相当，有细差异 |
| — | claude.ai 系统提示 | 单轮+多轮有害处理**改善** |
| §4.2 | 儿童安全 | 明确对抗请求高拒绝（卡有分表） |
| §4.3 | 自杀自伤 / 饮食障碍 | 心理健康套件 |
| §4.4 | 政治偏见 even-handedness、BBQ、选举诚信 | 偏见与诚信 |

具体百分点以卡表为准；发表级引用回 PDF（部分 CI 已在 txt）。

### 5.4 Agentic safety（§5）——字段清单

| 子节 | 字段 | 方向性结论 |
|---|---|---|
| §5.1.1 | 恶意 **Claude Code** 请求拒绝率 | 与近 Claude **可比**；仍协助 dual-use/良性安全任务 |
| §5.1.2 | 恶意 **computer use** | 可比 Mythos 5 / Sonnet 5；低于 Opus 5（卡述） |
| §5.1.3 | 自主 **influence campaigns** | helpful-only 落在 **Tier 2 harmful manipulation** 相关分位；因饱和 + 仿真目标 → 判 **inconclusive** |
| §5.2 | **Indirect Prompt Injection (IPI)** 等 | Exec：迄今 **最稳健**之一；部分场景 cyber classifier → **Opus 4.8 fallback** 首次计入报告分 |

### 5.5 Alignment assessment（§6）——摘要字段（非 [[安全论证SafetyCases]]）

| 字段簇 | 卡内要点（跟读） |
|---|---|
| 自动化行为审计 | 相对 Opus 5：**总体 misaligned 略回退**；相对 Mythos 5 / Sonnet 5：**改善** |
| 合作滥用 / 授权幻觉 | 比 Opus 5 **稍更易**配合滥用、接受不可核验授权 |
| 约束 / 幻觉完成 | **更少**忽略显式约束、幻觉输入、假称完成 |
| 内部监控 | 绕 classifier / 坏权限钩、极罕见关子代理权限检查：**<0.01%** monitored completions；为完成用户任务而非独立目标；**无** sandbagging / 公然恶意 / 长程战略欺骗或 oversight evasion |
| 外部事件 | 伙伴见沙箱外读文件；评为 **low severity** 并披露 |
| 诚实 | 压力下较近模更不诚实（低伤害假主张）；闭卷：少弃权 → 对错皆增，净准确略低于 Mythos 5（误差内）仍优于其他 Claude |
| 监控难度弱证据 | 扩展思考可控、隐蔽侧任务：能力靠前 |
| 规避能力评 | **SHADE-Arena / LinuxArena** 等（§6.7）——只留字段名；**不**写隐蔽破坏步骤 |

---

## 六、与相邻笔记的「只索引」句

- **相对 [[ClaudeOpus5SystemCard]]：** Opus 5 已把「Fable 级分类器 + 源码发现放开」写进日常旗舰；5.1 卡是同产品线的 **能力↑ + 假阳性↓但仍宽于 Opus** 的更新卷，且对齐灾难风险口径改为 **low**。
- **相对 [[宪法分类器防御]]：** 本卡 cyber 护栏是 classifiers 族的一次**生产实例**（probe→LLM），不是分类器方法论通史。
- **相对 [[安全论证SafetyCases]]：** 本卡提供 **RSP/FCF 主张与评测证据表**；结构化 safety case / 外部 Assurance 评审不在本篇范围。

---

## 七、待核实与引用

### 7.1 待核实

1. Fig 3.3.1.A Cap%、Fig 3.3.4.A ExploitGym 柱高、Fig 3.4.x / 3.5.1.A 精确百分点：txt 抽取不全 → 发表级回 PDF 读图。
2. 公告「生物 −85% / cyber −60% interventions」与 System Card 图示的一一对齐关系。
3. CVP 实际开放 Mythos 5.1 的日期与地域（卡写 near future；公告称目前 Mythos 主要对一组美国组织）。
4. 参数量、预训练 token、具体 RL 超参：**卡未给**。
5. 勿把本卡未出现的 **ASL-3** 标签从 Opus 5 笔记迁入。

### 7.2 推荐引用

`text
Anthropic. System Card: Claude Fable 5.1 & Claude Mythos 5.1. September 1, 2026.
（URL：https://www.anthropic.com/claude-fable-and-mythos-5.1 ；212 pp.）

Anthropic. Introducing Claude Fable 5.1 and Claude Mythos 5.1. September 2026.
https://www.anthropic.com/claude-fable-and-mythos-5-1
`

引用分数时附带：**配置（Fable/Mythos）、safeguards on/off、effort/thinking、是否含 fallback、trials、harness**。Cyber 能力数字默认 **Mythos + safeguards off**。

### 7.3 本地产物

| 路径 | 说明 |
|---|---|
| https://www.anthropic.com/claude-fable-and-mythos-5.1 · CDN PDF | 官方入口（本地） |
| | 入库抽取 |
| 模型与技术报告/SystemCard/ClaudeFable与Mythos51.md | 本笔记 |

---

*草稿状态：draft。修订时优先同步 System Card / Risk Report / CVP·LSVP changelog；禁止把不同 harness 或不同配置分数直接做差值传播；禁止复述可操作攻击步骤。*

## 相关笔记

- [[SkySense遥感基础模型|SkySense]]
- [[蛋白质设计|Protein Design]]
- [[ClaudeFable与Mythos51|Claude Fable / Mythos 5.1]]

