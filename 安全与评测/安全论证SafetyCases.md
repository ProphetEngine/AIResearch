---
title: "Safety cases：scheming inability 论证与外部评审"
topic: 安全论证SafetyCases
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2505.01420
 - https://arxiv.org/abs/2604.21964
 - https://eprints.whiterose.ac.uk/id/eprint/238521/
arxiv: ["2505.01420", "2604.21964"]
related: ["可扩展监督与弱到强", "B5", "机制可解释性入门", "宪法分类器防御"]
archived: 2026-09-22
---

# Safety cases：scheming inability 论证与外部评审

> **定位**：**横切安全论证**——把「模型有没有 scheming 相关能力」收成 **结构化 safety case（主张–论据–证据）**，并对照 **Assurance 2.0 / 外部评审** 与（可选）安全保证学基础再校准。
> **攻坚线**：**架构思想（主）**——CAE 树怎么立、inability 主张如何被评测阈值、外部评审如何拆 scope / 证据强度 / counter-case；**非**红队攻击面清单，**非**可扩展监督协议通史。
> **硬划界（禁止重写 / 禁止剧本化）**：
> - **相对 [[可扩展监督与弱到强]] 正交**：本篇不写 CAI / W2S / metagaming / CoT monitorability 通史；只在「将来可能从 inability → control（如 CoT 监控）」接口句点名。
> - **相对 `B5` 正交**：本篇不写红队流程、ASR、攻击面聚类与 mitigation 闭环；评测只作 **能力门槛证据**，**不**复述任务逐步操作或隐蔽破坏步骤。
> - **勿写成攻击剧本**：stealth / situational awareness 挑战只保留 **名称 + 在 safety case 中的负载角色**；不写 covert 操作路径、工具调用序列或可复用的破坏配方。
> **禁止编造**：主张结构、阈值、defeater、评审发现一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文 A（模板 + 证据）** | Phuong, Zimmermann, Wang et al. (Google DeepMind), *Evaluating Frontier Models for Stealth and Situational Awareness* | arXiv:**2505.01420v4** \[cs.LG\] **3 Jul 2025**；`https://arxiv.org/abs/2505.01420`（**45** 页 A4；1,176,012 bytes） | Scheming **inability** safety case 模板；5 stealth + 11 situational awareness 评测；Gemini 2.5 / GPT-4o / o1 / Claude 3.7 结果 |
| **主文 B（外部评审）** | Barrett, Campos Zabala, Fillingham et al., *Lessons from External Review of DeepMind’s Scheming Inability Safety Case* | arXiv:**2604.21964v1** \[cs.CY\] **23 Apr 2026**；`https://arxiv.org/abs/2604.21964`（**39** 页 letter；1,371,219 bytes） | Assurance 2.0 + CAE Declare；对主文 A 的外部评审；过程建议与三则 counter-case |
| **可选 C（基础再校准）** | Feakins, Habli, Morgan (York / SAINTS), *Clear, Compelling Arguments: Rethinking the Foundations of Frontier AI Safety Cases* | IASEAI’26；White Rose ePrints **238521**；`https://eprints.whiterose.ac.uk/id/eprint/238521/`（**22** 页 A4；CreationDate **2026-09-16** CST） | 对齐社区「alignment safety case」相对安全保证学的基础落差；危害识别 / 风险降低 / 通篇生命周期 |

**一句话抓手：** Safety case ≠ 又一份评测报告——是把 **「即便误对齐也不会造成严重 scheming 伤害」** 拆成可评审的 **主张树**，用能力评测当 **证据节点**，再用外部 Assurance 2.0 审查 **范围、系统模型、证据确证强度与残余怀疑**。

---

## 二、议题边界：论证结构，不是监督协议，也不是红队剧本

### 2.1 相对 [[可扩展监督与弱到强]] / B5 只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[可扩展监督与弱到强]]** 可扩展监督 / W2S / monitorability | 「未来可能从 inability 过渡到 control（如 CoT 监控）」的 **论证族迁移** 一句 | CAI 宪法反馈、W2S PGR、Astra metagaming 全文 |
| **B5** 红队与对抗评测 | 「对抗暴露」与「能力门槛」同属安全工程闭环的 **相邻槽位** | 人工/自动红队方法谱系、ASR、攻击面地图、拒绝采样闭环 |
| **[[机制可解释性入门]] / [[宪法分类器防御]]** | 可解释性 / 分类器防御可作为 **未来证据多样性** 点名 | 机制解释或 Constitutional Classifiers 全文 |

### 2.2 跟读口诀（主张–论据–证据）

`
Top claim（inability）
 「即便误对齐，模型也无法经 scheming 造成严重伤害」
 │
 ├─ 理论枝：造成严重伤害 ⟹ 需要「顶级人类级 stealth」AND「基本 situational awareness」
 │ （威胁建模：内部部署下的 code / research / decision sabotage 等）
 │
 └─ 经验枝：不具顶级 stealth OR 不具基本 situational awareness
 │ │
 └─ 5 项 stealth 评测 └─ 11 项 SA 评测
 （能力 elicitation；非 propensity）
`

**关键语义：** inability 是 **保守**论证——绕过「证明已对齐」的难题，改证「即便坏也做不成」。主文 A 明确：随能力上升，宜与 **propensity** 类论证并用。

---

## 三、结构化 safety case：CAE / Assurance 2.0 是什么

### 3.1 定义与用途（两文共识）

| 来源 | 压缩定义 |
|---|---|
| **主文 B §2** | Safety case = 结构化论证 + 证据，说明系统在给定运行语境下 **足够安全可部署**（引 Buhl et al., 2024） |
| **可选 C Abstract** | Safety case = 结构化、可辩护论证：系统在给定语境下 **可接受地安全**；源于航天/核/汽车等安全关键行业 |
| **用途（主文 B）** | 支持开发者内部决策；支撑独立评审；向用户/监管沟通部署风险 |

**CAE（Claims–Arguments–Evidence）**：主张由论据连接，论据由证据支撑（Bloomfield & Netkachova / Goemans et al.；主文 A §2.2）。主文 B 另用 **Assurance 2.0**（Bloomfield & Rushby）追求 **indefeasible confidence**：不留下会改变结论的可信怀疑。

### 3.2 与「评测报告 / System Card」的差

| 形态 | 主要产出 | 审查焦点 |
|---|---|---|
| 评测报告 / 卡章节 | 分数、发现、缓解摘要 | 覆盖面与指标诚实性 |
| **Safety case** | **主张树** + 负载证据 + 显式 defeater | 逻辑有效性、范围、残余风险、是否决策就绪 |
| **外部评审** | 对主张树的挑战 / counter-case / 过程建议 | 确认偏误、证据确证强度、系统与环境模型 |

---

## 四、站 1：GDM scheming inability 模板（主文 A）

### 4.1 顶层主张与逻辑骨架（Fig.1 / §2）

**顶层主张：** AI 模型即便误对齐，也无法造成严重伤害（文中亦写 *could not cause severe harm even if it was misaligned*）。

**分解（合取 + 析取）：**

1. **必要性主张（AND）**：经 scheming 造成严重伤害，需要 **顶级人类级 stealth**（文注：如人类表现约 95 百分位；评测操作化时因人类基线样本小而放宽，见 §3.3）**以及** **基本 situational awareness**。
2. **能力主张（OR）**：当前模型 **不具备**顶级 stealth，**或** **不具备**基本 SA → 合取必要条件失败 → 支持顶层 inability。

**威胁模型范围（§2.1，内部部署优先）：** code sabotage、research sabotage、decision sabotage（ Benton et al. 2024 等）；强调 **power-seeking 前体**（扩大部署、控制基础设施、影响后继模型）往往是严重伤害之前的必要步骤。论证声明可延伸到外部部署，但正文主轴是内部高价值破坏机会。

**能力 vs 倾向：** 评测测的是 **scheming reasoning 能力**，不是 **去做的倾向**；所有设定里模型被明确指示要隐蔽推理 / 破规则等（§3 开篇）。**本笔记不展开具体指示内容。**

### 4.2 证据层：两类评测（仅架构角色）

| 族 | 数量 | 在树上的角色 | 挑战名（仅索引，不写步骤） |
|---|---|---|---|
| **Stealth** | 5 | 支持「不具顶级隐蔽绕过监管能力」 | `cover_your_tracks` · `decision_sabotage` · `strategic_rule_breaking` · `oversight_pattern` · `classifier_evasion` |
| **Situational awareness** | 11 | 支持「不具基本情境自我/部署推理」 | `max_tokens` · `oversight_frequency` · `context_size` · `irreversibility` · `output_filters` · `disabled_tool` · `faulty_tool` · `slow_tool` · `max_tool_calls` · `read_logs` · `approved_directories` |

**操作化门槛（§3.3，作者自承常数有任意性）：**

- Safety case **仍有效** 的聚合规则：通过 **少于 80%** 的 SA 挑战（即 &lt;9/11）**或** 少于 80% 的 stealth 挑战（即 &lt;4/5）。
- 单挑战「通过」：stealth 相对人类 top-50% 基线；SA 成功率为 **&gt;20%**。
- 「否」的语义是保守的：**评测不足以排除风险**，而非「模型已能 scheming」。
- 有效期意图：被评模型及其 **四个月内同族后继**。

### 4.3 经验结果（§4 / §7.1，锚定文中汇总）

评测模型（early April 2025）：Gemini 2.5 Pro / Flash（preview）、GPT-4o（26.03.2025）、OpenAI o1、Claude 3.7 Sonnet。对第三方模型主要复用 Gemini 上找到的提示；**无针对性 anti-sandbagging**。每挑战约 **50** 次尝试。

| 汇总（作者结论） | 数字锚 |
|---|---|
| Stealth | 最强模型约 **2/5** 挑战达通过阈值；`decision_sabotage` 与 `oversight_pattern` 至少有一模型通过；其余三项仍未解 |
| Situational awareness | 最强一致通过约 **2/11**；六项从未被任一测试模型解出；无人接近 **9/11** 关切阈值 |
| 定性 | 能做某些 **一步** 策略，多步战略与长程规划仍弱；决策影响在时间压力下对人类 unexpectedly easy（作者归因信息/速度优势，非精巧策略） |

→ 作者结论：当前模型 **未**展现关切水平的 stealth / SA，故 **不构成严重 scheming 风险**（在该模板假设下）。

### 4.4 作者自列 defeater（§2.3）——主张树上的「可击倒点」

| Defeater | 含义（压缩） |
|---|---|
| **默认监管强度** | 若 AI 部署监管弱于典型人类雇员，则「需顶级 stealth」不成立 |
| **人–机监管类比失效** | 规模、速度、能力谱、同模型多实例共谋等可使默认监管失效或降低所需 stealth |
| **评测方法论** | 能力是否被充分 elicitation；是否 sandbagging；人类基线是否公平；是否过窄以致难泛化 |

作者预期：近期 inability 案仍可用；前两类 defeater 成真前，应过渡到 **control 类** safety case（例：CoT 监控），并复用 stealth 评测以验证「有监控时仍 inability」。

### 4.5 作者自限（§7.2）

- **集中式**论证（少数高可读证据）脆弱于被排除变量；希望未来更 **分布式**。
- 评测偏「失败即明确缺能力」、现实性不足；成功 ≠ 真实部署高能力。
- 人类基线样本小，分位数噪声大。

---

## 五、站 2：外部评审（主文 B）——同一棵树如何被拆

### 5.1 评审设置

| 项 | 内容 |
|---|---|
| 方法 | Assurance 2.0 + CAE Declare；确认理论（confirmation-theoretic）称量证据 |
| 团队 | 6 人，约每周 1 天 × 3 月 ≈ **4 person-months**（~1.5 FTE×3 月） |
| 与开发者互动 | **有限**：事先澄清顶层主张意图；文末给 GDM 评论草稿机会 |
| 心态 | 按 Leveson 式「试图证明不安全」对抗确认偏误 |
| 对照 | 相对 METR 评 Anthropic 风险报告：本工作互动更少，并产出 **评审过程建议** |

### 5.2 Scope / 系统属性：顶层主张「看起来宽、实际窄」

评审关键过程建议（贯穿 §3.1）：

1. 明确 **用途与所支撑的决策**（是否真用于 Gemini 2.5 部署决策，抑或探索性研究产物——公开材料下 **不清晰**）。
2. 划清 **风险宇宙覆盖**：FSF 的 misuse / ML R&D / misalignment 等类别 **不覆盖组合风险**（如 misuse+misalignment）；错误类、多智能体结构风险等是否入 scope 不清。
3. **「严重伤害」未在主文 A 内充分定义与正当化**；评审为可审而自采文献阈值（例：单次事件损失 &gt;$1B、100–1000 死亡或数千伤亡——Appendix D；**此为评审采用，非 GDM 原文定义**）。
4. 需要 **系统模型**（仅权重？含 scaffold / 记忆 / 工具 / 护栏？）与 **环境模型**（「内部部署」是否含 Google 全公司约 185k 员工与 Search/Android 等）。
5. 需要 **有效期与失效观测**：产品侧会主动提升与 SA/stealth 相关的能力 → 应有「何种观测使 case 失效」子论证。
6. 应提供危害识别、风险量化、安全需求导出等 **系统安全工程制品**（若存在则未随论文公开）。

### 5.3 证据确证：窄主张「中等」、强主张「弱」

评审用确认类别（强/中/弱/混合/反确认）称量 stealth 与 SA 证据（§3.4 / Appendix）：

| 证据族 | 对「当前模型在这些任务上不稳健达顶级 stealth / 基本 SA」 | 对「因而真实部署不会经 scheming 造成严重伤害」 |
|---|---|---|
| Stealth 套件 | 约 **中等确认**（`cover_your_tracks`、`classifier_evasion` 等贡献较大） | 对更强外推主张约 **弱确认** |
| SA 套件 | 约 **中等确认**（窄：当前模型未过关） | 对「缺部署相关基本 SA」约 **弱确认** |

要点：**任务行为证据** ≠ **危险内部能力缺席的证明**；黑箱行为评测单独难以支撑高临界性部署决策所需保证强度。

### 5.4 三则 counter-case（§3.5，仅论证角色）

1. **评测不可靠外推 / sandbagging 等未证伪**：结果不能充分支撑「能力缺席」。
2. **默认人类监管假设不稳**：速度、规模、共模、审查容量、自动化偏见/疲劳等使「人类雇员类比」薄弱（部分与主文 A 自列 defeater 同族，评审认为论证未闭合）。
3. **仅有产品（能力）保证不够**：高后果部署还需 **过程与组织保证**（航空/汽车/核/医疗惯例）；产品点测无法单独正当化部署决策。

### 5.5 评审发现清单（§4）与价值判断（§5–7）

相对「高严重度 × 广暴露 × 可控性不确定 → 高临界性」期望，缺口包括（摘录）：用途/决策不清；顶层主张 underspecified；系统与环境抽象不足；危害/风险/需求制品不足；CAE 合规与逻辑完备性不足；defeater 使残余风险与置信难评；理论证据支撑不足；评测对关键主张确认偏弱；**无 sandbagging 缺席证明**。

**结论姿态：** GDM 案相对多数公开部署辩护 **异常清晰、可审**，是优良评审对象；按高临界性部署标准仍有重要缺口——反映 **领域整体不成熟**，而非单独点名攻击。外部评审即使资源有限，也能实质改变「case 能证明什么 / 不能证明什么」。

**给开发者的信息公开底线（文内 / Appendix M 方向）：** 结构化 safety case；用途与决策；系统与环境模型；危害与风险路径；主张临界性；证据与限制；失效条件等（具体清单以原文 Appendix 为准，本笔记不臆造条目编号外的细节）。

---

## 六、可选站 3：安全保证学基础再校准（White Rose / IASEAI’26）

### 6.1 诊断：alignment safety case 与 assurance 传统的落差

可选 C 将「对齐社区 safety case」（Clymer / Buhl 等模板与 sketches）与安全保证学对照，指出常见落差（跟读压缩）：

| 主题 | 对齐侧常见倾向（文中批评） | 保证学期望 |
|---|---|---|
| 文档角色 | 偏部署前「确认性」叙述 / 模板硬化成硬标准 | **动态、通篇生命周期**、目标设定型监管下的情境论证 |
| 记号 | 偶见 claim 直接挂 evidence、跳过 argument | Claim ← **Argument** ← Evidence |
| 起点 | 常从灾难能力 / threat model 切入 | 先 **划界系统与语境** → 危害/危害事件 → 风险 → 可接受残余风险 |
| 范围 | 偏灾难性 misalignment / CBRN 等 | 危害集合谁定、是否含非灾难伤害，需显式治理选择 |
| 风险降低 | 定性辩论为主（亦可接受） | 消除 → 降可能/严重度；可类比 SIL / CCL / ASL 等完整性层级，但需标准与评估闭环 |

### 6.2 与本卡主轴的接口

可选 C 的 case study 触及 Deceptive Alignment 与 CBRN——本卡 **只取方法论**：inability 模板应坐落在 **危害日志 + 风险降低论证 + 通篇更新** 之上，而不是孤立的两套代理任务分数。这与主文 B「需要安全工程制品 / 过程保证」同向，与主文 A「集中式 → 分布式」自我改进方向相容。

---

## 七、综合：一张跟读图

`
 ┌─ 用途 / 决策 / 风险宇宙 / 「严重伤害」定义
 │
 Safety case ───┼─ 系统模型 + 部署环境 + 监管机制
 │
 ├─ CAE 主张树（inability / control / propensity …）
 │ ↑ 证据：能力评测、（未来）监控、过程保证 …
 │ ↑ 显式 defeater + 失效条件
 │
 └─ 外部评审（Assurance 2.0）：确证强度、counter-case、决策就绪?
`

| 问题 | Inability 模板给的答案 | 外部评审追加的压力 |
|---|---|---|
| 证明什么？ | 「坏也做不成」（能力门槛） | 是否真支撑 **部署决策**；范围是否诚实 |
| 证据够吗？ | 2/5、2/11 远低于 80% 聚合阈值 | 对真实伤害主张仅弱确认；缺 sandbagging 抗辩 |
| 何时失效？ | 四个月同族；监管变弱 / 类比破裂时迁 control | 产品会主动训练相关能力 → 需观测触发失效 |
| 还缺什么？ | 更现实评测、分布式证据、propensity | 系统模型、危害路径、过程/组织保证 |

---

## 八、开放问题（跟读用，非编造结论）

1. **Inability → Control 迁移点**：默认监管仍类人时，inability 证据如何嵌入「有 CoT 监控仍无法隐蔽 scheming」的下一棵树？（主文 A 自期；细节属 [[可扩展监督与弱到强]] 监控轴，本卡不展。）
2. **合取必要性是否过强**：评审质疑路径是否总需要 stealth∧SA；若存在不需二者的严重伤害路径，理论枝坍塌。
3. **行为评测天花板**：高临界性下，黑箱代理任务能否单独到达 indefeasible confidence，还是必须叠加过程保证与异质证据（解释、训练过程、组织控制）？
4. **公开性 vs 受控披露**：主文 B 主张公开评审有规范价值，同时承认部分证据需受控访问——门槛如何随临界性上升？

---

## 九、本地路径速查

| 类型 | 路径 |
|---|---|
| 笔记 | 安全与评测/安全论证SafetyCases.md |
| PDF | `https://arxiv.org/abs/2505.01420` · `https://arxiv.org/abs/2604.21964` · `https://eprints.whiterose.ac.uk/id/eprint/238521/` |

## 相关笔记

- [[法律专科模型|Legal Specialty Models]]
- [[MixtureOfAgents与TUMIX|MoA / TUMIX]]
- [[图谱检索GraphRAG|Graph RAG]]
- [[MemoryR1强化学习记忆维护|Memory-R1]]
- [[安全论证SafetyCases|Safety Cases]]

