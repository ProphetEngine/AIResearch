---
title: Model Card / System Card 规范（字段谱系与体裁差异）
topic: 模型卡与SystemCard规范
date: 2026-09-22
lines: [架构思想]
status: archived
aliases: [模型卡与SystemCard规范]
archived: 2026-09-22
---

# Model Card / System Card 规范

> **研究线**：架构思想（主）
> **跟读材料（官方优先）**：
> 1. Mitchell et al., *Model Cards for Model Reporting*（FAT* ’19 / arXiv:1810.03993v2，2019-01-14）
> - 介绍页：https://arxiv.org/abs/1810.03993
> - 全文 PDF（本笔记主源）：`https://arxiv.org/abs/1810.03993`（**10** 页）
> 2. Hugging Face Hub，《Model Cards》：https://huggingface.co/docs/hub/en/model-cards
> - Annotated Template：https://huggingface.co/docs/hub/en/model-card-annotated
> - Guidebook（引用 Mitchell；模板演进）：https://huggingface.co/docs/hub/en/model-card-guidebook
> 3. **对照**：相邻深读卡
> - System Card 系：[[GPT5系统卡深读]]、[[GPT52SystemCard更新]]、[[GPT56系统卡深读]]、[[GPT6Astra系统卡深读]]、[[GPT61Sol系统卡短报]]、[[GPT6SolLuna十月版系统卡短报]]；[[ClaudeOpus41系统卡附录深读]]、[[ClaudeOpus45系统卡深读]]、[[ClaudeOpus5系统卡深读]]、[[ClaudeFable与Mythos51]]、[[ClaudeOpus55系统卡短报]]、[[ClaudeSonnet55系统卡短报]]、[[ClaudeHaiku55系统卡短报]]
> - Model Card 系：[[Gemini3Pro模型卡深读]]、[[Grok4模型卡深读]]、[[GPToss模型卡深读]]、[[Gemini37Flash模型卡深读]]
> - [[MOC_模型与技术报告]]
> **范围与相邻笔记**：本篇写「文档体裁 → 字段接口」。
> - ≠ 上列 System Card 系与 Model Card 系各篇：本篇不写各厂卡的能力/安全数字与案例正文。

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

### 1.2 研究会语境：归档需要统一字段，而非再抄一篇卡

研究会归档规范要求「官方 URL + 日期 + 是否 thinking/工具」等；仓库已有多份 System / Model Card PDF 与 TR 深读卡，但缺「**学术起源 → HF 实践 → 厂商 System Card**」的规范短笔记，便于归档员与评测议题共建字段。

因此本笔记只做两件事：

1. 固定 Mitchell / HF 的**经典字段谱系**；
2. 对照相邻卡笔记的实践，标出 System Card 相对 Model Card 的**体裁差异**（不重写正文）。

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

## 三、System Card 实践差异（对照相邻卡笔记）

### 3.1 命名与体量：同一词根，不同产品形态

| 维度 | 经典 Model Card（Mitchell / 短 HF README） | 相邻笔记中的「厂商卡」实践（据各 TR 元信息 / PDF TOC） |
|------|--------------------------------------------|-----------------------------------------------------|
| 典型页数 | Mitchell 倡「一至两页」短记录；示例为插图卡 | GPT-5 SC **60** 页；Claude 4 SC **124** 页；Claude Opus 4.5 SC **153** 页；Gemini 3 Pro MC **10** 页；Grok 4 MC **8** 页（各 TR 笔记） |
| 标题习惯 | Model Card | OpenAI / Anthropic 多用 **System Card**；Google DeepMind Gemini 3 Pro 仍称 **Model Card**；xAI Grok 4/4.1 称 Model Card，**Grok 4.20 改称 System Card**（见 [[Grok4模型卡深读]] §3.4） |
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

**FSF 背景：** Google DeepMind 的 Frontier Safety Framework（FSF）为每个风险域设关键能力档（CCL），并在 CCL 之下设 alert 阈值，提示模型可能正在接近该 CCL；Gemini 3 Pro 模型卡按 2025 年 9 月版评估，各域均未达 CCL，Cybersecurity 已达 alert（见 [[Gemini3Pro模型卡深读]]）；Gemini 3.7 Flash 模型卡改按 2026 年 4 月版并新增 TCL 列（见 [[Gemini37Flash模型卡深读]]）。框架各版本与 Gemini 的 FSF 报告见 [Frontier safety at Google DeepMind](https://deepmind.google/frontier-safety/)（Google DeepMind FSF 落地页）。

### 3.3 相对 Mitchell 的系统性偏移（架构思想）

1. **从「分群误差条」到「威胁模型目录」**：前沿 SC 的一级目录常按 jailbreak / injection / CBRN / cyber / agentic / RSP 组织，而非按 demographic unitary×intersectional 主轴。BBQ 等公平基准仍出现，但通常是**专节**而非整卡骨架。
2. **从「单模型工件」到「系统」**：OpenAI 强调统一系统、router、thinking 变体、工具与防护栈；Anthropic 强调 hybrid thinking、effort、计算机使用与 ASL；卡名 System Card 与此一致。
3. **从「一次发布」到「卡族」**：主卡 + Addendum + Update；以及 Preview vs GA（GPT-5.6 TR）。归档必须记下**卡类型**与**相对哪张主卡**。
4. **名称漂移**：xAI 同系文档可从 Model Card 改称 System Card（[[Grok4模型卡深读]] §3.4），**不能**仅凭文件名推断字段完备度。
5. **HF 机读层与厂商 PDF 层并行**：开源权重发布仍大量依赖 HF README/YAML；闭源旗舰则以 PDF SC/MC 为权威。研究会库内两者都收，字段模板需能覆盖。

---

## 四、误区

1. **「System Card = 加长版 Model Card」**
 页数变长只是表象；一级目录已从「分群报告」转向「威胁模型 + 治理框架 +（可选）能力」。用 Mitchell 九段去硬套 GPT/Claude SC 会漏掉 Preparedness/RSP/agentic 主轴。

2. **「文件名写 Model Card 就没有 System 级治理内容」**
 Gemini 3 Pro、Grok 4 均以 Model Card 为名但含 Frontier Safety / RMF 双用途等。反之，Grok 4.20 改称 System Card 也不自动补齐通用能力榜。

3. **「HF README 填全 YAML 就等于完成 Mitchell 定量交叉分析」**
 YAML 服务发现与小部件；Mitchell §4.7 要求的 unitary/intersectional 结果仍须在正文（或另文）给出。`model-index` 分数≠分群公平分析。

4. **「把各厂 SC 安全表直接纵向比出谁更安全」**
 协议、是否去 safeguard、语言覆盖、自评 vs 外部、Preview vs GA 均可能不同（Grok 4.1 对旧卡英文-only refusal 的修正；Addendum 与 Update 的「largely the same」）。横比前先对齐评测轴与协议备注。参见 [[评测与排行榜可靠性]]、[[安全红队与对抗评测]]。

5. **「归档只要最新卡，旧卡可删」**
 TOXICITY v1→v5 示例与 Claude/OpenAI Changelog 均表明：**差分本身是证据**。应保留版本链（`relation_to_prior` / `superseded_by`），而不是只留最新 PDF。

6. **「训练数据一节越详越好，可从 SC 反推完整配比」**
 Mitchell §4.6 已承认专有数据可只给分布级信息；相邻笔记中多张 SC/MC 对数据仅有高层句。缺细节标「未公开」，不用二手博客补全当官方字段。

7. **「重写一遍卡正文当作规范笔记」**
 本笔记服务字段统一；能力/红队/Preparedness 数字已在对应技术报告深读卡与 [[安全红队与对抗评测]]。重复粘贴会造成双源漂移。

8. **「o1 / 早期 SC 与 2025–2026 旗舰卡字段同构」**
 o1 System Card（arXiv:2412.16720）可作早期范例；体裁同属 System Card，但目录与威胁模型随产品代际扩展。引用时标注代际，勿假设字段一一对应。（o1 卡本笔记未展开深读。）

---

## 五、引用与官方路径

### 主源

1. Margaret Mitchell et al. *Model Cards for Model Reporting.* FAT* ’19, January 29–31, 2019, Atlanta, GA, USA. ACM. https://doi.org/10.1145/3287560.3287596
 - arXiv: https://arxiv.org/abs/1810.03993 （v2，2019-01-14）
 - PDF：https://arxiv.org/pdf/1810.03993
 - PDF：https://arxiv.org/pdf/1810.03993

2. Hugging Face. *Model Cards*（Hub 文档）. https://huggingface.co/docs/hub/en/model-cards
3. Hugging Face. *Annotated Model Card Template*（Ozoani, Gerchick, Mitchell；Guidebook 体系）. https://huggingface.co/docs/hub/en/model-card-annotated
4. Hugging Face. *Model Card Guidebook*. https://huggingface.co/docs/hub/en/model-card-guidebook

### 实践对照（相邻笔记 / PDF，勿当本笔记数字源）

| 笔记 | 官方 PDF（示例） |
|------|------------------|
| [[GPT5系统卡深读]] | `https://cdn.openai.com/gpt-5-system-card.pdf` |
| [[GPT52SystemCard更新]] | `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` |
| [[GPT56系统卡深读]] | `https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf` 等 |
| [[ClaudeOpus41系统卡附录深读]] | `https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf` |
| [[ClaudeOpus45系统卡深读]] | `https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf` |
| Claude 4 主卡（对照） | `https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf` |
| [[Gemini3Pro模型卡深读]] | `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` |
| [[Grok4模型卡深读]] | `https://data.x.ai/2025-08-20-grok-4-model-card.pdf` 等 |

### 相关研究会笔记

- [[安全红队与对抗评测]]：红队方法谱系 ↔ SC 安全章
- [[评测与排行榜可靠性]]：榜单/去污/协议 ↔ 卡内能力表
- [[智能体工具与长程任务]]：工具/智能体表面 ↔ `has_tools`
- [[MOC_模型与技术报告]]

### 入口提及、本笔记未展开

- OpenAI o1 System Card：https://arxiv.org/abs/2412.16720 ；亦见 https://arxiv.org/abs/2412.16720（[[模型卡与SystemCard规范]] 范例入口；**未**纳入本规范笔记逐节对照）

---

*主要来源：[Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)（字段与主张）；[Model Cards](https://huggingface.co/docs/hub/en/model-cards)；[Annotated Model Card Template](https://huggingface.co/docs/hub/en/model-card-annotated)（HF 结构）；厂商差异仅用相邻 TR 笔记的元信息与目录级描述。*

## 相关笔记

- [[分词器与数据配比]]
- [[安全红队与对抗评测]]
- [[检索增强与知识外挂]]
- [[合成数据与教科书式数据]]
- [[多语言与跨语种]]
- [[扩散生成式视觉与LLM]]
- [[模型卡与SystemCard规范]]
- [[Qwen3技术报告深读]]

