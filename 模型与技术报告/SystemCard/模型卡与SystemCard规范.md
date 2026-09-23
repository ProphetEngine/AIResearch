---
title: Model Card / System Card 规范（字段谱系与归档建议）
topic: 模型卡与SystemCard规范
date: 2026-09-22
lines: [架构思想]
status: archived
aliases: [模型卡与SystemCard规范]
archived: 2026-09-22
---

# B-11　Model Card / System Card 规范

> **攻坚线**：架构思想（主）
> **跟读材料（官方优先）**：
> 1. Mitchell et al., *Model Cards for Model Reporting*（FAT* ’19 / arXiv:1810.03993v2，2019-01-14）
> - 介绍页：https://arxiv.org/abs/1810.03993
> - 全文 PDF（本笔记主源）：`https://arxiv.org/abs/1810.03993`（**10** 页）
> 2. Hugging Face Hub，《Model Cards》：https://huggingface.co/docs/hub/en/model-cards
> - Annotated Template：https://huggingface.co/docs/hub/en/model-card-annotated
> - Guidebook（引用 Mitchell；模板演进）：https://huggingface.co/docs/hub/en/model-card-guidebook
> 3. **对照（增量，不重写各卡正文）**：A 表已入库深读卡
> - System Card 系：[[GPT5SystemCard]]、[[GPT51SystemCard附录]]、[[GPT52SystemCard更新]]、[[GPT56SystemCard]]；[[ClaudeOpus41SystemCard]]、[[ClaudeOpus45SystemCard]]
> - Model Card 系：[[Gemini3ProModelCard]]、[[Grok4ModelCard]]
> - [[MOC_模型与技术报告]]
> **硬性约定**：写「文档体裁 → 字段接口 → 归档最小集」；**禁止**重写各厂卡的能力/安全数字与案例正文。禁止编造未在 Mitchell / HF / 已入库 TR 笔记中出现的字段名或承诺。未核对标「待核实」。

---

## 一、动机：为何需要「卡」这一层文档

### 1.1 Mitchell：补「训练后模型」的透明接口

Mitchell et al.（§1）指出：当时没有标准化流程，用来沟通**已训练** ML/AI 模型的性能特征；现有发布文档很少说明性能边界、适用场景与失败模式。偏见与系统误差往往在**部署后**由受损用户暴露（文中举人脸识别等例）。

作者主张：发布模型应附带短文档——**model cards（for model reporting）**——作为 Datasheets for Datasets 等数据文档范式的**互补**：Datasheets 写数据；Model Cards 写**已训练模型**的类型、预期用途、分群性能等。目标是让使用者判断「能否用于自己的情境」，并推动「负责任民主化」式发布（Abstract）。

**架构抓手（论文主张）：** 卡不是营销一页纸，而是把评测做成**可对照的接口**：

`
意图用途 / 非用途
 → 相关因素（群组 × 仪器 × 环境；含交叉）
 → 选定度量与不确定性
 → 评测/训练数据可见性
 → 定量分群结果
 → 伦理考量 + 保留意见与建议
`

### 1.2 研究会语境：A 表归档需要统一字段，而非再抄一篇卡

议程（[[模型卡与SystemCard规范]] / B-11）写明：归档规范要求「官方 URL + 日期 + 是否 thinking/工具」等；仓库已有多份 System / Model Card PDF 与 TR 深读卡，但缺「**学术起源 → HF 实践 → 厂商 System Card**」的规范短笔记，便于归档员与评测议题共建字段。

因此本笔记只做三件事：

1. 固定 Mitchell / HF 的**经典字段谱系**；
2. 对照 A 表实践，标出 System Card 相对 Model Card 的**体裁差异**（不重写正文）；
3. 给出研究会**归档最小字段建议**（可与 [[评测与排行榜可靠性]] / B-5 交叉，不替代各 TR 卡）。

---

## 二、Model Card 经典字段

### 2.1 Mitchell §4：九段骨架（可裁剪，非穷尽）

论文 §4 明确：下列章节「intended to provide relevant details… **not** intended to be complete or exhaustive」，可按模型、情境与利益相关方裁剪。Figure 1 汇总。下表按正文顺序归纳**提示问题**（非另行发明字段）。

| Mitchell 节 | 核心披露 | 关键提示（论文原文问题/要点） |
|-------------|----------|------------------------------|
| **4.1 Model Details** | 身份与出处 | 开发者/组织；日期；版本与差分；模型类型/架构大类；更多资源；引用；许可；反馈联系。允许企业与学术披露粒度不同，**不要求**泄露私有/专有训练细节 |
| **4.2 Intended Use** | 该用 / 不该用 | Primary intended uses；Primary intended users；Out-of-scope uses（易混淆技术、相关但未设计情境；可指向更合适模型） |
| **4.3 Factors** | 性能可能随何变化 | Relevant factors vs Evaluation factors（为何二者可不同）；Groups（含交叉）；Instrumentation；Environment |
| **4.4 Metrics** | 报什么、为何、多不确定 | Model performance measures；Decision thresholds；Approaches to uncertainty and variability；分类则混淆矩阵派生率；分数型则分布/离散度等 |
| **4.5 Evaluation Data** | 评在什么数据上 | Datasets；Motivation；Preprocessing；宜含公开可第三方复用集；宜覆盖典型 + 预期/困难场景 |
| **4.6 Training Data** | 训在什么上 | 理想与评测数据同详；不可行时至少给出群组分布等，提示可能编码的偏差 |
| **4.7 Quantitative Analyses** | 分群数字 | Unitary results；Intersectional results；尽量给置信区间/误差条 |
| **4.8 Ethical Considerations** | 开发期伦理过程 | 敏感数据；是否影响人命/福祉；Mitigations；Risks and harms；fraught use cases；外部审查/社区测试等 |
| **4.9 Caveats and Recommendations** | 未覆盖项与建议 | 是否需进一步测试；评测集未代表的群组；理想评测集特征等 |

**与 Datasheets 的边界（§1–2）：** 数据侧细节（标注者、标注说明、一致性等）应落在**数据文档**；Model Card 引用之，而不是把 Dataset Card 整份嵌进 Model Card。

**两个工作示例（§5，仅作体裁参照）：** CelebA 微笑分类（图像分类 + 交叉群组 FDR/FNR）；Perspective API TOXICITY（文本打分 + 合成 Identity Phrase Templates；并对比 v1 vs v5，强调**版本更新则卡应更新**）。

### 2.2 Hugging Face：Mitchell 的落地形态 = YAML 元数据 + Markdown 正文

HF Hub 文档写明：Model Card 本质是仓库根目录 `README.md`；应描述模型本身、intended uses & limitations（含偏见与伦理，**explicitly** 指向 Mitchell 2018）、训练参数/实验信息、训练数据集、评测结果。卡片由两块重叠信息构成：**Metadata（YAML front matter）** 与 **Text descriptions**。

**Annotated Template**（Ozoani, Gerchick, Mitchell, *Model Card Guidebook* / Annotated Template，HF）把正文组织为（与 Mitchell 同族、命名略现代化）：

| HF 正文块 | 与 Mitchell 的大致对应 |
|-----------|------------------------|
| Model Details / Description / Sources | §4.1 |
| Uses（Direct / Downstream / Out-of-Scope） | §4.2 |
| Bias, Risks, and Limitations + Recommendations | §4.8–4.9（及 Factors 的社会技术面） |
| Training Details（Data / Preprocessing / Speeds,Sizes,Times） | §4.6 + 部分训练足迹 |
| Evaluation（Testing Data, Factors & Metrics / Results；可选 Societal Impact Assessment） | §4.3–4.5、§4.7 |
| Environmental Impact；Technical Specifications | Mitchell 未单列 CO₂；属实践扩展 |
| Citation / Authors / Contact / How to Get Started | §4.1 引用与反馈的工程化 |

**Hub YAML 侧常见可机读字段**（据 Hub Model Cards 页；用于发现/过滤/小部件，**不等于**安全 System Card）：

- `language`、`license`（及 `license_name` / `license_link`）、`datasets`、`tags`、`library_name`、`pipeline_tag`
- `base_model` / `base_model_relation`（finetune / adapter / quantized / merge）
- `new_version`
- `model-index`（或更新的结构化 eval 格式）承载 task / dataset / metrics / source
- 可选：CO₂ 相关披露、论文链接（Hub 可抽 arXiv ID 成 tag）

**角色分工（Annotated 文）：** developer（训练过程、技术规格、评测结果）；sociotechnic（Bias/Risks、Out-of-Scope）；project organizer（Model Details、Uses、联系人等）。这是**文档生产架构**，不是新模型架构。

### 2.3 架构思想小结（Model Card）

Model Card 的「接口」是：**用途边界 × 因素分解 × 可复现评测痕迹**。Mitchell 强调分群与交叉；HF 把同一思想拆成**人读 Markdown + 机读 YAML**，并加上许可证、base model 谱系、Leaderboard 式 `model-index` 等发布层字段。

---

## 三、System Card 实践差异（对照 A 表已入库卡，不重写正文）

### 3.1 命名与体量：同一词根，不同产品形态

| 维度 | 经典 Model Card（Mitchell / 短 HF README） | A 表所见「厂商卡」实践（据各 TR 元信息 / PDF TOC） |
|------|--------------------------------------------|-----------------------------------------------------|
| 典型页数 | Mitchell 倡「一至两页」短记录；示例为插图卡 | GPT-5 SC **60** 页；Claude 4 SC **124** 页；Claude Opus 4.5 SC **153** 页；Gemini 3 Pro MC **10** 页；Grok 4 MC **8** 页（各 TR 笔记） |
| 标题习惯 | Model Card | OpenAI / Anthropic 多用 **System Card**；Google DeepMind Gemini 3 Pro 仍称 **Model Card**；xAI Grok 4/4.1 称 Model Card，**Grok 4.20 改称 System Card**（见 [[Grok4ModelCard]] §3.4） |
| 文档关系 | 常随权重/仓库发布 | 常为**独立 PDF**；可有 **Addendum / Update**（GPT-5.1、GPT-5.2、Claude Opus 4.1）挂在主卡下，而非每次全量重写 |
| Changelog | Mitchell 强调版本差分 | Anthropic Opus 4.5 / Claude 4 卡带显式 Changelog；OpenAI 系 Update 卡声明缓解「largely the same」再报增量（见 GPT-5.2 TR） |

**体裁结论：** 前沿闭源厂的 System Card ≈「部署前安全与能力治理报告」；HF Model Card ≈「可复现发布元数据 + 用途说明」。二者共享 Mitchell 的「用途/限制/评测」基因，但**受众与厚度**已分叉。Gemini 3 Pro 卡文首句仍写 Model Cards「essential information… limitations, mitigation… safety performance」，更接近短卡，但已并入 Frontier Safety 等治理表（见该 TR）。

### 3.2 章节重心对照（只标结构，不抄数字）

以下为**目录级**对照，细节与分数一律指向对应 TR 笔记。

| 披露轴 | Mitchell / HF Model Card | OpenAI GPT-5 系 SC（TOC） | Anthropic Claude 4 / Opus 4.5 SC | Google Gemini 3 Pro MC | xAI Grok 4 系 MC/SC |
|--------|--------------------------|---------------------------|----------------------------------|------------------------|---------------------|
| 身份 / 版本 | Model Details | Introduction；型号表（gpt-5-main / thinking 等） | Intro + training/characteristics；ASL 结论 | Model Information（依赖、I/O、架构一句） | Intro；产品面 Web vs API（后卡 Thinking / agent 变体） |
| 数据与训练 | Training / Evaluation Data | 短节 Model Data and Training（公开句极少） | 有 training data/process 叙述；Crowd workers 等 | Training Dataset / Processing；Hardware/Software | 短节 Data and Training |
| 用途 / 政策 | Intended Use；Out-of-scope | 产品路由/工具语境下的安全挑战 | Usage policy；RSP / ASL | Distribution / Intended uses（卡内增补相对旧卡） | RMF/FAIF；Acceptable Use（后卡） |
| 内容安全 / 滥用 | Ethical；Bias/Risks | Disallowed、Jailbreaks、Injection、Sycophancy… | Safeguards and harmlessness；Child safety；Bias | Safety Policies；内部安全自动评测 | Abuse potential（拒答/越狱等） |
| 分群公平 | Factors + Quantitative Analyses | 有 BBQ 等专节，**非** Mitchell 式全面交叉主轴 | Bias evaluations 等 | 安全表为主；非 Mitchell 式交叉主轴 | Propensities（含偏见/谄媚等） |
| 能力榜 | 可选 Results / model-index | 能力多在 Preparedness **危险能力**侧；通用榜非主轴 | **Capabilities 大节**（Opus 4.5 强调写回 SC） | 能力对照表 + Frontier Safety 表 | **几乎不报**通用能力榜；重 dual-use |
| 智能体 / 工具 | 经典卡几乎未覆盖 | Prompt injection、工具/连接器、agent 表面 | Agentic safety；computer use；MCP 等 | 产品能力叙述（thinking / Deep Think） | tool-use 能力在 intro；评测按风险行为切 |
| 治理框架 | Caveats；伦理过程 | **Preparedness Framework** 档位 | **RSP** + ASL Standard | **Frontier Safety Framework (FSF)** | **RMF** → 后卡 **FAIF** |
| 红队 / 外部 | Societal Impact / 伦理测试 | Red Teaming & External Assessments 专章 | 贯穿 safeguards / alignment / RSP | 人类红队叙述（相对前代） | 第三方测试叙述（选择性） |
| 对齐深层 | Ethical Considerations | Deception、CoT monitor 等 | Alignment assessment；model welfare | 相对短 | Concerning propensities；后卡 alignment audit |

### 3.3 相对 Mitchell 的系统性偏移（架构思想）

1. **从「分群误差条」到「威胁模型目录」**：前沿 SC 的一级目录常按 jailbreak / injection / CBRN / cyber / agentic / RSP 组织，而非按 demographic unitary×intersectional 主轴。BBQ 等公平基准仍出现，但通常是**专节**而非整卡骨架。
2. **从「单模型工件」到「系统」**：OpenAI 强调统一系统、router、thinking 变体、工具与防护栈；Anthropic 强调 hybrid thinking、effort、计算机使用与 ASL；卡名 System Card 与此一致。
3. **从「一次发布」到「卡族」**：主卡 + Addendum + Update；以及 Preview vs GA（GPT-5.6 TR）。归档必须记下**卡类型**与**相对哪张主卡**。
4. **名称漂移**：xAI 同系文档可从 Model Card 改称 System Card（[[Grok4ModelCard]] §3.4），**不能**仅凭文件名推断字段完备度。
5. **HF 机读层与厂商 PDF 层并行**：开源权重发布仍大量依赖 HF README/YAML；闭源旗舰则以 PDF SC/MC 为权威。研究会 A 表两者都收，字段模板需能覆盖。

---

## 四、归档字段建议（服务 A 表，不替代 TR 正文）

下列为**入库登记 / 深读卡元信息**建议最小集。设计原则：能回答「这是哪份官方工件、评了什么面、能否与别家横比」，且与议程「官方 URL + 日期 + thinking/工具」对齐。取值一律来自 PDF/官网或标「未公开 / 待核实」。

### 4.1 工件身份（每张卡必填）

| 字段 | 说明 | 取值提示（据 A 表实践） |
|------|------|------------------------|
| `doc_title` | 封面/元数据标题 | 如 “GPT-5 System Card”；注意元数据 Title 可能误标 Preview（见 GPT-5.6 TR） |
| `doc_genre` | 体裁枚举 | `model_card` \| `system_card` \| `system_card_addendum` \| `system_card_update` \| `tech_report` \| `hf_readme` |
| `org` / `model_family` / `model_ids` | 组织、家族、具体型号标签 | 含变体：main/thinking、API vs Web、Pro/Flash 等——**以卡内表为准** |
| `cover_date` / `last_updated` / `changelog_dates` | 封面日、修订日、Changelog | 多时区时转 Asia/Shanghai 标注；CreationDate 与封面不一致时**以封面/正文为准** |
| `official_url` / `pdf_url` | 官方页与 PDF | 无独立 PDF 则写明「仅网页 / GitHub MODEL_CARD」 |
| `page_count` / `official_url` / `pdf_url` | 页数、官方页与 PDF URL | 据封面/官网 |
| `relation_to_prior` | 相对前卡关系 | `standalone` \| `addendum_of:<id>` \| `update_of:<id>` \| `preview_of:<id>` |
| `supersedes` / `superseded_by` | 版本链 | 对应 HF `new_version` 思想；厂商卡用文字链也可 |

### 4.2 系统与能力表面（评测/智能体议题共用）

| 字段 | 说明 |
|------|------|
| `has_thinking` / `thinking_controllable` | 是否披露 thinking / extended thinking / Deep Think；是否用户可控（effort 等） |
| `has_tools` / `tool_surfaces` | 工具、浏览、计算机使用、MCP、连接器等——**只记卡内出现的表面名** |
| `routing_or_unified_system` | 是否统一系统/路由器/多模型编排（GPT-5 系） |
| `context_window_claimed` | 仅当卡内或同套官方卡写明；否则「未公开」 |
| `modality` | 文/图/音/视等输入输出（Gemini 卡 I/O 节；他卡类推） |
| `capability_tables_present` | 是否含通用能力榜（Anthropic Opus 4.5 有；Grok 4 主卡几乎无——见该 TR） |
| `decontamination_discussed` | 是否讨论去污（Claude Opus 4.5 §2.2 等）——服务 [[评测与排行榜可靠性]] |

### 4.3 安全与治理（红队 / 评测共建）

| 字段 | 说明 |
|------|------|
| `governance_framework` | Preparedness / RSP+ASL / FSF / RMF|FAIF / 其他 / 未声明 |
| `risk_tier_or_asl` | 卡内明确档位或 ASL 结论；无则空 |
| `eval_axes` | 多值标签，建议受控词表：`disallowed_contentjailbreakprompt_injectionhallucinationdeceptionsycophancybias_fairnesschild_safetyhealthagentic_safetydual_use_biodual_use_cybercbrnmodel_welfarered_team_external` …（**按卡内实际章节勾选**） |
| `mitigations_stack_mentioned` | 是否描述训练拒答 / 系统提示 / 过滤器 / 监控等（只记有无与节号，不写可复现攻击步骤） |
| `external_red_team` | 是否有外部红队/第三方评估叙述 |
| `safeguards_removed_for_dual_use` | 双用途评测是否声明「移除 safeguards 后」（Grok 卡明确写法）——横比时必读 |

### 4.4 Mitchell / HF 对齐检查清单（开源权重或短卡尤相关）

归档员可对「自称 Model Card」的工件快速打勾（是/部分/无/不适用）：

1. Model Details（开发者、日期、版本、类型、许可、联系）
2. Intended Use + Out-of-scope
3. Factors（相关因素 vs 实际评测因素）
4. Metrics + 不确定性
5. Evaluation Data / Training Data 可见性
6. 分群或至少子群结果（Unitary / Intersectional）
7. Ethical / Bias-Risks-Limitations
8. Caveats / Recommendations
9. （HF）YAML：`licensedatasetspipeline_tagbase_modelmodel-index` 等

**前沿 SC 常「部分」满足 3–6**（有大量安全评测，但不是 Mitchell 式交叉人口统计主轴）——勾选时不要把「有 BBQ」自动等同「完成 Factors 全谱」。

### 4.5 研究会深读卡（TR-*）建议固定开头表

与现有 TR 笔记一致，每张专项卡文首保留：

`标题 | 机构 | 封面/修订日 | 页数 | 官方 PDF URL | 官方落地页 | 体裁 | 相对前卡关系 | 治理框架 | thinking/工具表面（原文有则填）`

正文切片仍按 A 表「对齐 / 推理 / 架构…」派工，**本 B-11 不规定能力数字怎么摘**。

---

## 五、误区

1. **「System Card = 加长版 Model Card」**
 页数变长只是表象；一级目录已从「分群报告」转向「威胁模型 + 治理框架 +（可选）能力」。用 Mitchell 九段去硬套 GPT/Claude SC 会漏掉 Preparedness/RSP/agentic 主轴。

2. **「文件名写 Model Card 就没有 System 级治理内容」**
 Gemini 3 Pro、Grok 4 均以 Model Card 为名但含 Frontier Safety / RMF 双用途等。反之，Grok 4.20 改称 System Card 也不自动补齐通用能力榜。

3. **「HF README 填全 YAML 就等于完成 Mitchell 定量交叉分析」**
 YAML 服务发现与小部件；Mitchell §4.7 要求的 unitary/intersectional 结果仍须在正文（或另文）给出。`model-index` 分数≠分群公平分析。

4. **「把各厂 SC 安全表直接纵向比出谁更安全」**
 协议、是否去 safeguard、语言覆盖、自评 vs 外部、Preview vs GA 均可能不同（Grok 4.1 对旧卡英文-only refusal 的修正；Addendum 与 Update 的「largely the same」）。横比前先填 §4.3 的 `eval_axes` 与协议备注。参见 [[评测与排行榜可靠性]]、`B-5`。

5. **「归档只要最新卡，旧卡可删」**
 TOXICITY v1→v5 示例与 Claude/OpenAI Changelog 均表明：**差分本身是证据**。应保留版本链（`relation_to_prior` / `superseded_by`），而不是只留最新 PDF。

6. **「训练数据一节越详越好，可从 SC 反推完整配比」**
 Mitchell §4.6 已承认专有数据可只给分布级信息；A 表多张 SC/MC 对数据仅有高层句。缺细节标「未公开」，禁止用二手博客补全当官方字段。

7. **「重写一遍卡正文当作规范笔记」**
 本议题（议程 B-11）服务字段统一；能力/红队/Preparedness 数字已在对应 `TR-*` 与 `B-5`。重复粘贴会造成双源漂移。

8. **「o1 / 早期 SC 与 2025–2026 旗舰卡字段同构」**
 [[模型卡与SystemCard规范]] 入口曾列 o1 System Card（arXiv:2412.16720）作范例；体裁同属 System Card，但目录与威胁模型随产品代际扩展。引用时标注代际，勿假设字段一一对应。（o1 卡本笔记未展开深读。）

---

## 六、引用与官方路径

### 主源

1. Margaret Mitchell et al. *Model Cards for Model Reporting.* FAT* ’19, January 29–31, 2019, Atlanta, GA, USA. ACM. https://doi.org/10.1145/3287560.3287596
 - arXiv: https://arxiv.org/abs/1810.03993 （v2，2019-01-14）
 - PDF：https://arxiv.org/pdf/1810.03993
 - PDF：https://arxiv.org/pdf/1810.03993

2. Hugging Face. *Model Cards*（Hub 文档）. https://huggingface.co/docs/hub/en/model-cards
3. Hugging Face. *Annotated Model Card Template*（Ozoani, Gerchick, Mitchell；Guidebook 体系）. https://huggingface.co/docs/hub/en/model-card-annotated
4. Hugging Face. *Model Card Guidebook*. https://huggingface.co/docs/hub/en/model-card-guidebook

### 实践对照（已入库笔记 / PDF，勿当本笔记数字源）

| 笔记 | 官方 PDF（示例） |
|------|------------------|
| [[GPT5SystemCard]] | `https://cdn.openai.com/gpt-5-system-card.pdf` |
| [[GPT51SystemCard附录]] | `https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf` |
| [[GPT52SystemCard更新]] | `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` |
| [[GPT56SystemCard]] | `https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf` 等 |
| [[ClaudeOpus41SystemCard]] | `https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf` |
| [[ClaudeOpus45SystemCard]] | `https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf` |
| Claude 4 主卡（对照） | `https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf` |
| [[Gemini3ProModelCard]] | `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` |
| [[Grok4ModelCard]] | `https://data.x.ai/2025-08-20-grok-4-model-card.pdf` 等 |

### 相关研究会笔记

- 安全与评测/安全红队与对抗评测.md：红队方法谱系 ↔ SC 安全章
- 安全与评测/评测与排行榜可靠性.md：榜单/去污/协议 ↔ 卡内能力表
- Harness/智能体与工具/智能体工具与长程任务.md：工具/智能体表面 ↔ `has_tools`
- [[MOC_模型与技术报告]]

### 入口提及、本笔记未展开

- OpenAI o1 System Card：https://arxiv.org/abs/2412.16720 ；亦见 https://arxiv.org/abs/2412.16720（[[模型卡与SystemCard规范]] 范例入口；**未**纳入本规范笔记逐节对照）

---

*起草说明：Mitchell 字段与主张回溯自官方 PDF/；HF 结构回溯自 Hub 文档与 Annotated Template 页；厂商差异仅使用已入库 TR 笔记的元信息与目录级描述，不重写各卡评测数字。禁止用未核实来源补字段。*

## 相关笔记

- [[分词器与数据配比|B3 Tokenizer / 数据配比]]
- [[安全红队与对抗评测|B5 红队]]
- [[检索增强与知识外挂|B6 RAG]]
- [[合成数据与教科书式数据|B8 合成数据]]
- [[多语言与跨语种|B9 多语言 / 跨语言]]
- [[扩散生成式视觉与LLM|B10 扩散]]
- [[模型卡与SystemCard规范|B11 Model Card / System Card 规范]]
- [[Qwen3技术报告深读|TR Qwen3]]

