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

> **主要来源**：[Model Cards for Model Reporting](https://arxiv.org/abs/1810.03993)（Mitchell 等，FAT* ’19，arXiv v2 2019-01-14）；[Model Cards](https://huggingface.co/docs/hub/en/model-cards)（Hugging Face Hub 文档）；[Annotated Model Card Template](https://huggingface.co/docs/hub/en/model-card-annotated)（Hugging Face Hub 文档）；[Model Card Guidebook](https://huggingface.co/docs/hub/en/model-card-guidebook)（Hugging Face Hub 文档）（截至 2026-08-13）。厂商卡的体裁差异只取相邻深读笔记的目录级描述。
> **研究线**：架构思想（文档体裁与披露字段：模型卡字段从哪里来，系统卡改变了什么）
> **范围与相邻笔记**：
> - ≠ [[SystemCard谱系时间线]]：本篇不写各厂系统卡与技术报告的逐年发布节点，只取体裁发生变化的几处。
> - ≠ [[安全红队与对抗评测]]：本篇不写红队方法谱系，只写红队章节在卡内的位置。
> - ≠ [[评测与排行榜可靠性]]：本篇不写评测协议与去污方法，只提示跨卡横比前要先对齐协议。
> - 本篇不写各厂卡的能力与安全数字、案例正文，这些在第八节分工表所列各篇。
>
> **意义**：模型卡由 Mitchell 等在 2018 年提出，用一至两页的短文档写清已训练模型的用途边界、分群表现与局限；Hugging Face 把它落成「YAML 元数据加 Markdown 正文」的仓库 README。前沿闭源厂商沿用了「卡」这个名字，但 System Card 的骨架已从分群公平报告转向威胁类型、治理框架档位与部署防护，并形成主卡加增补卡、预览版加正式版的系列。读任何一张卡之前，先分清它是哪种体裁、相对哪张前卡、按哪套治理框架判定，才能决定哪些字段可以与别家对照。

## 一、问题背景

Mitchell 等（原文 §1）指出，当时没有标准化的流程来沟通已训练机器学习模型的性能特征；随模型发布的文档即便存在，也很少说明性能、预期用途与潜在陷阱。商用人脸识别等系统中的系统性偏差，往往在部署之后才由受影响的用户暴露出来。作者因此主张发布模型时附上一至两页的短记录，称为模型卡（model cards for model reporting），作为 Datasheets for Datasets 等数据文档的补充：数据文档写训练与测试数据，模型卡写已训练模型的类型、预期用途、性能可能随之变化的因素与性能度量（§1）。目标是让使用者判断模型是否适合自己的情境，作者称之为迈向机器学习「负责任的民主化」的一步（摘要）。

此后模型文档分成两条线。开放权重模型以 Hugging Face 仓库 README 的形式发布模型卡；前沿闭源模型则由厂商发布长篇 PDF 或网页形式的 System Card，同一个「卡」字下的文档在受众、篇幅与骨架上都已分叉。读者对照各厂卡时，需要一份说明：经典模型卡有哪些字段，System Card 在哪些地方偏离了它，哪些字段因此不能直接横比。

## 二、发展脉络

| 时间 | 节点 | 体裁上的变化 |
|---|---|---|
| 2018-10 | Model Cards for Model Reporting 预印本 | 提出随已训练模型发布的短文档，按分群与交叉群组报告评测 |
| 2019-01 | 同文在 FAT* ’19 发表 | 正式版给出九段章节与两个工作示例，成为后来模型卡字段的源头 |
| 2022-12 | Hugging Face 发布卡片创建工具与 Model Card Guidebook（[Model Cards](https://huggingface.co/blog/model-cards) 博文，Ozoani、Gerchick、Mitchell） | 模型卡落成仓库 README，配注释模板与角色分工 |
| 2024-12 | [OpenAI o1 System Card](https://arxiv.org/abs/2412.16720)（arXiv 首版） | 厂商以 System Card 为名发布推理模型的安全与风险评估，可作早期范例 |
| 2025-05 | Claude Sonnet 4 与 Opus 4 系统卡（[Model system cards](https://www.anthropic.com/system-cards) 索引页） | 系统卡把 RSP 评测、智能体安全与对齐评估放进同一卷 |
| 2025-08 | GPT-5 系统卡、Claude Opus 4.1 系统卡附录、Grok 4 模型卡 | 统一系统与路由进入卡的骨架；出现主卡加附录的分层写法；xAI 以八页、几乎只讲安全评测的模型卡发布 |
| 2025-11 至 12 | GPT-5.1 增补、Gemini 3 Pro 模型卡、Claude Opus 4.5 系统卡、GPT-5.2 更新卡 | 增补卡与更新卡成为常态；Google 仍称 Model Card 但并入前沿安全框架（FSF）档位；能力章节回到 Anthropic 的系统卡内 |
| 2026-04 | Grok 4.20 System Card | xAI 同系文档由 Model Card 改称 System Card |
| 2026-06 至 07 | GPT-5.6 预览版与正式版两张系统卡 | 同一型号先后出预览版卡与正式版卡 |
| 2026-08 | Gemini 3.7 Flash 模型卡 | 改按 2026 年 4 月版 FSF 评估，并新增 TCL 一列 |

2025 年以来各节点的细节见第八节分工表所列各篇；按厂商排列的完整节点见 [[SystemCard谱系时间线]]。

## 三、核心思想：Model Card 的经典字段

### 3.1 Mitchell 的九段骨架

原文 §4 说明，这些章节用于提示应当考虑的细节，并不完整、也不穷尽，可按模型、情境与利益相关方裁剪；Figure 1 汇总了全部章节与提示问题。按正文顺序归纳如下。

| Mitchell 节 | 核心披露 | 提示问题要点 |
|---|---|---|
| 4.1 Model Details | 身份与出处 | 开发者或组织、日期、版本及与前版差异、模型类型、更多资源、引用、许可、反馈联系；企业与学术机构披露粒度可不同，不要求泄露私有信息或专有训练技术 |
| 4.2 Intended Use | 该用与不该用 | 主要预期用途、主要预期用户、范围外用途（易被混淆的技术、用户可能误用的相关情境，可推荐更合适的模型） |
| 4.3 Factors | 性能可能随什么变化 | 相关因素与实际评测因素（二者不同时说明原因）；群组（含交叉）、采集仪器、部署环境 |
| 4.4 Metrics | 报什么、为何、有多不确定 | 性能度量、决策阈值、不确定性与变异的估计方法；分类系统报混淆矩阵派生的各类错误率，打分系统报分布与离散程度 |
| 4.5 Evaluation Data | 评在什么数据上 | 数据集、选用动机、预处理；宜包含可供第三方使用的公开数据集，并覆盖典型用例与预期的困难场景 |
| 4.6 Training Data | 训在什么数据上 | 理想情况下与评测数据同样详细；数据专有或受保密协议约束时，至少给出群组分布等基本信息 |
| 4.7 Quantitative Analyses | 分群结果 | 单一因素结果与交叉结果，尽量给置信区间或误差条 |
| 4.8 Ethical Considerations | 开发期的伦理考量 | 敏感数据、是否影响人的生命与福祉、缓解策略、风险与危害、高风险用例；可写外部评审或特定社区测试 |
| 4.9 Caveats and Recommendations | 未覆盖项与建议 | 是否需要进一步测试、评测集未覆盖的群组、理想评测集的特征 |

模型卡与数据文档分工：标注者、标注说明、标注一致性等数据细节应放在随数据集提供的数据文档里（§4.3.1），模型卡引用它们，而不是把数据文档整份并入。

原文 §5 给了两个工作示例：CelebA 上的微笑分类器（图像分类，按年龄与性别的交叉群组报告 FPR、FNR、FDR、FOR）；Perspective API 的 TOXICITY 分类器（文本打分，用合成的 Identity Phrase Templates 测试集，并列 v1 与 v5 两个版本的结果）。后者的结论是模型会随时间剧烈变化，模型卡应随每次新版本发布而更新。

### 3.2 Hugging Face 的落地形态：YAML 元数据加 Markdown 正文

Hub 文档写明，模型卡就是模型仓库里的 `README.md`，应描述模型本身、预期用途与潜在局限（包括 Mitchell 2018 中详述的偏见与伦理考量）、训练参数与实验信息、训练数据集与评测结果；卡由两部分重叠的信息构成：元数据（YAML front matter）与正文描述。

Annotated Model Card Template 把正文组织为与 Mitchell 同源、命名更现代的各块：

| HF 正文块 | 与 Mitchell 的大致对应 |
|---|---|
| Model Details（Model Description、Model Sources） | 4.1 |
| Uses（Direct Use、Downstream Use、Out-of-Scope Use） | 4.2 |
| Bias, Risks, and Limitations；Recommendations | 4.8、4.9，以及 Factors 中的社会技术面 |
| Training Details（Training Data、Preprocessing、Speeds, Sizes, Times） | 4.6，加训练开销 |
| Evaluation（Testing Data, Factors & Metrics；Results；可选 Societal Impact Assessment） | 4.3 至 4.5、4.7 |
| Environmental Impact；Technical Specifications | Mitchell 未单列，属实践扩展 |
| Citation；Model Card Authors；Model Card Contact；How to Get Started with the Model | 4.1 中引用与反馈的工程化 |

Hub 元数据中常见的机读字段用于发现、过滤与页面小部件，不承担安全披露：

- `language`、`license`（及 `license_name`、`license_link`）、`datasets`、`tags`、`library_name`、`pipeline_tag`
- `base_model` 与 `base_model_relation`（adapter、merge、quantized、finetune）
- `new_version`：指向同一模型在 Hub 上的新版本
- 评测结果：最初的元数据规范基于 Papers with Code 的 `model-index`，Hub 解析后在模型页以小部件展示；文档另推出了更简单的评测结果元数据格式
- CO2 排放披露；卡内链接论文页时，Hub 会把 arXiv ID 抽成标签

注释模板还把填卡的人分为三种角色：developer（写代码、跑训练）、sociotechnic（分析技术与社会的长期互动，包括律师、伦理学者、社会学者或权益倡导者）、project organizer（了解模型的整体范围与影响面，能大致填写每一部分，并作为卡片更新的联系人）。这是文档生产的分工，不是模型结构。

### 3.3 小结

模型卡的核心是三件事：写清用途边界，按因素拆分评测，留下可复现的评测痕迹。Mitchell 强调分群与交叉分析；Hugging Face 把同一思想拆成人读的正文与机读的 YAML，并加上许可、基座模型谱系、新版本指针与结构化评测结果等发布层字段。

## 四、关键机制：System Card 相对 Model Card 的偏移

### 4.1 命名与形态

| 维度 | 经典 Model Card（Mitchell、Hub README） | 厂商卡的实践（据相邻深读笔记） |
|---|---|---|
| 篇幅 | Mitchell 主张一至两页的短记录 | Gemini 3 Pro 模型卡 10 页、Grok 4 模型卡 8 页，仍接近短卡；GPT-5、Claude 4、Claude Opus 4.5 的系统卡是分多章的长篇文档 |
| 名称 | Model Card | OpenAI、Anthropic 多用 System Card；Google DeepMind 的 Gemini 3 Pro 仍称 Model Card；xAI 的 Grok 4、4.1 称 Model Card，Grok 4.20 改称 System Card（见 [[Grok4模型卡深读]] 第五节） |
| 文档关系 | 常随权重或仓库一起发布 | 常为独立文档；GPT-5.1、GPT-5.2、Claude Opus 4.1 以附录或更新卡挂在主卡之下，而不是每次全量重写 |
| 版本差分 | Mitchell 要求写明与前版的差异 | Claude Opus 4.5、Opus 4.1 卡带显式变更记录；OpenAI 的更新卡先声明缓解措施与前卡「largely the same」，再报增量（见 [[GPT52SystemCard更新]]） |

前沿闭源厂商的 System Card 更接近部署前的安全与能力治理报告；Hub 上的模型卡更接近可复现的发布元数据加用途说明。二者共享 Mitchell 的「用途、限制、评测」三项，但受众与厚度已经分叉。Gemini 3 Pro 卡开篇称其目的在于提供模型的基本信息，包括已知局限、缓解方法与安全表现，篇幅也接近短卡，但已并入前沿安全框架的档位表（见 [[Gemini3Pro模型卡深读]]）。

### 4.2 章节重心对照（只标结构，不抄数字）

以下为目录级对照，细节与分数一律见对应深读笔记。

| 披露轴 | Mitchell / HF 模型卡 | OpenAI GPT-5 系系统卡 | Anthropic Claude 4、Opus 4.5 系统卡 | Google Gemini 3 Pro 模型卡 | xAI Grok 4 系卡 |
|---|---|---|---|---|---|
| 身份与版本 | Model Details | 引言；型号表（gpt-5-main、gpt-5-thinking 等） | 引言与训练、模型特性；ASL 结论 | 模型信息（依赖、输入输出、架构一句） | 引言；Web 与 API 两种部署，后卡改为 Thinking 与非 Thinking、单智能体与多智能体 |
| 数据与训练 | Training / Evaluation Data | 数据与训练短节，公开句极少 | 训练数据与训练过程叙述；众包工作者一节 | 训练数据集与处理；硬件与软件 | 数据与训练短节 |
| 用途与政策 | Intended Use；Out-of-scope | 产品路由与工具语境下的安全挑战 | Usage Policy；RSP 与 ASL | 分发渠道与预期用途 | RMF，后卡改称 FAIF |
| 内容安全与滥用 | Ethical；Bias / Risks | 违禁内容、越狱、提示注入、谄媚等 | 安全防护与无害性；儿童安全；偏见评测 | 安全政策；内部自动安全评测 | 滥用潜力（拒答、越狱等） |
| 分群公平 | Factors 加 Quantitative Analyses | 有 BBQ 等专节，但不是 Mitchell 式交叉分析主轴 | 政治偏见与歧视性偏见评测 | 以安全表为主，不是交叉分析主轴 | 可疑倾向（含偏见、谄媚等） |
| 能力榜 | 可选 Results 或 `model-index` | 能力多出现在 Preparedness 危险能力一侧，通用榜不是主轴 | Opus 4.5 卡设能力大节，把能力评测写回系统卡 | 能力对照加前沿安全表 | 几乎不报通用能力榜，重双用途 |
| 智能体与工具 | 经典卡几乎未覆盖 | 提示注入、工具与连接器、智能体表面 | 智能体安全；计算机使用；MCP 等 | 产品能力叙述（thinking、Deep Think） | 工具调用能力只在引言；评测按风险行为切分 |
| 治理框架 | Caveats；伦理过程 | Preparedness Framework 档位 | RSP 加 ASL 标准 | Frontier Safety Framework（FSF） | RMF，后卡改称 FAIF |
| 红队与外部评估 | Societal Impact；伦理测试 | 红队与外部评估专章 | 贯穿安全防护、对齐与 RSP 各章 | 人类红队叙述 | 第三方测试叙述（有选择） |
| 对齐深层 | Ethical Considerations | 欺骗、思维链监控等 | 对齐评估；模型福祉评估 | 篇幅相对短 | 可疑倾向 |

**FSF 背景**：Google DeepMind 的 Frontier Safety Framework（FSF）为每个风险域设关键能力档（CCL），并在 CCL 之下设 alert 阈值，提示模型可能正在接近该 CCL。Gemini 3 Pro 模型卡按 2025 年 9 月版评估，各域均未达 CCL，Cybersecurity 已达 alert（见 [[Gemini3Pro模型卡深读]]）；Gemini 3.7 Flash 模型卡改按 2026 年 4 月版评估，并新增 TCL 一列（见 [[Gemini37Flash模型卡深读]]）。框架各版本与 Gemini 的 FSF 报告见 [Frontier safety at Google DeepMind](https://deepmind.google/frontier-safety/)（Google DeepMind 的 FSF 落地页）。四家的治理框架在卡内的位置相同，都是给出风险档位结论的依据：OpenAI 用 Preparedness 档位，Anthropic 用 RSP 与 ASL，Google 用 FSF 的 CCL 与 alert 阈值，xAI 用 RMF（Grok 4.20 卡改称 FAIF）。

### 4.3 相对 Mitchell 的系统性偏移

1. **从分群误差条到威胁类型目录**：前沿系统卡的一级目录常按越狱、提示注入、CBRN、网络安全、智能体、RSP 等组织，而不是按单一群组与交叉群组组织。BBQ 等公平基准仍会出现，但通常是专节，而非整张卡的骨架。
2. **从单个模型到系统**：OpenAI 强调统一系统、路由器、thinking 变体、工具与防护栈；Anthropic 强调混合推理、effort、计算机使用与 ASL。System Card 这个名字与此一致。
3. **从一次发布到系列文档**：主卡之外有附录与更新卡，还有同一型号的预览版卡与正式版卡（见 [[GPT56系统卡深读]]）。引用一张卡时，要同时记下卡的类型与它相对哪张主卡。
4. **名称漂移**：同一厂商同一系列的文档可以从 Model Card 改称 System Card（见 [[Grok4模型卡深读]] 第五节），不能只凭名称判断字段是否完备。
5. **机读层与厂商文档层并行**：开放权重发布仍大量依赖 Hub README 与 YAML，闭源旗舰则以厂商发布的系统卡或模型卡为权威。对照两类模型时，两层都要看。

## 五、常见误读

1. **「System Card 就是加长版 Model Card」**：篇幅变长只是表象，一级目录已从分群报告转向威胁类型、治理框架与可选的能力章节。用 Mitchell 九段去硬套 GPT 或 Claude 的系统卡，会漏掉 Preparedness、RSP 与智能体这几条主轴。
2. **「名称是 Model Card，就没有系统级的治理内容」**：Gemini 3 Pro、Grok 4 都以 Model Card 为名，却含前沿安全档位或 RMF 双用途评测；反过来，Grok 4.20 改称 System Card 也没有因此补上通用能力榜。
3. **「Hub README 把 YAML 填全，就完成了 Mitchell 的交叉分析」**：YAML 服务于发现与小部件，Mitchell §4.7 要求的单一因素与交叉结果仍须在正文或另文给出；`model-index` 里的分数不等于分群公平分析。
4. **「把各厂系统卡的安全表直接纵向比出谁更安全」**：协议、是否移除防护后评测、语言覆盖、自评与外部评估、预览版与正式版都可能不同。Grok 4.1 卡更正了旧卡拒答评测只跑英文的问题；更新卡声明缓解与前卡「largely the same」后只报增量。横比前先对齐评测轴与协议说明。
5. **「只看最新的卡就够了」**：TOXICITY v1 与 v5 的示例和 Anthropic、OpenAI 卡的变更记录都表明，版本之间的差分本身就是证据。阅读时应沿着版本链看：相对哪张前卡、被哪张后卡取代；Hub 上对应的是 `new_version` 字段。
6. **「训练数据一节可以反推完整配比」**：Mitchell §4.6 已承认专有数据可以只给分布层面的信息；多数厂商卡对数据只有高层描述。卡内没有的细节应视为未公开，不能用二手博客补成官方字段。
7. **「早期系统卡与 2025 年以来的旗舰卡字段同构」**：o1 System Card 可作早期范例，体裁同属 System Card，但目录与威胁类型随产品代际扩展。引用时应注明代际，不假设字段一一对应。

## 六、意义

模型卡把「发布模型时说清楚什么」变成一组可对照的字段：用途边界、因素拆分、评测数据与分群结果、伦理与局限。System Card 继承了用途、限制与评测三项，又把治理框架档位、部署防护、智能体表面和版本链变成新的必备内容。对读者而言，本篇提供的是一套读卡的先后顺序：先认体裁与名称，再看相对哪张前卡、按哪套框架判定，最后才看数字；第四节的对照表则说明哪些字段在两类卡之间可以对齐，哪些只能各自阅读。

## 七、局限与待核实

1. **卡是自述文档**：Mitchell 在原文 §6 承认，模型卡的有用性与准确性取决于作者的诚信；短期内模型卡难以标准化到足以防止误导性呈现的程度，应把它视为多种透明工具之一，与第三方算法审计、对抗测试与用户反馈并用。厂商系统卡同样是自评文档，外部评估只在部分章节出现。
2. **Hub 文档是活页**：Hugging Face 的三页文档没有标更新日期，YAML 字段与评测结果格式会随 Hub 演进（文档已注明推出新的评测结果元数据格式），第 3.2 节按本篇所读页面描述。
3. **对照范围有限**：第四节的目录级对照只覆盖表头所列各卡。o1 System Card 只作范例入口，未逐节对照；Claude 4 系统卡没有对应的深读笔记，相关单元格依据其目录；此后各厂新发布的系统卡未逐一并入对照表，按厂商排列的后续节点见 [[SystemCard谱系时间线]]。
4. **框架名称是否对应同一文件**：Grok 4.20 卡正文称 FAIF，但引注条目标题仍为 RMF，二者是否为同一文件改名，卡内未说明（见 [[Grok4模型卡深读]]）。
5. **Gemini 3 Pro 卡的版本**：深读笔记按 PDF 所标「Last Updated: May 2026」计，与官方索引页的更新日不一致；本篇所引的 FSF 版本与 alert 结论以该笔记为准。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT5系统卡深读]] | 作为「统一系统」型 System Card 主卡的样本，用于第四节的体裁对照 | 该卡的安全评测数字与 Preparedness 判定 |
| [[GPT52SystemCard更新]] | 作为挂在主卡下的「更新卡」体裁样本 | 更新卡的差分数字与增补评测 |
| [[GPT56系统卡深读]] | 作为同一型号「预览版卡与正式版卡」并存的样本 | 两张卡的评测与防护内容 |
| [[ClaudeOpus41系统卡附录深读]] | 作为「主卡加附录」分层写法与变更记录的样本 | 附录的评测内容 |
| [[ClaudeOpus45系统卡深读]] | 作为把能力章节写回系统卡、带变更记录的样本 | 该卡的能力、安全与对齐结论 |
| [[Gemini3Pro模型卡深读]] | 作为「名为 Model Card、含前沿安全档位」的短卡样本；FSF 背景放在本篇 | 该卡的能力表与前沿安全表 |
| [[Gemini37Flash模型卡深读]] | 作为只报变化量、指回前代卡的增量卡样本；FSF 背景放在本篇 | 该卡的能力差分与各域档位 |
| [[Grok4模型卡深读]] | 作为同系文档由 Model Card 改称 System Card 的样本；RMF 与 FAIF 在各家框架中的位置放在本篇 | 三张卡的评测结构与数字 |
| [[GPToss模型卡深读]] | 作为开放权重模型以 model card 为名发布的样本 | 该卡的架构与评测内容 |
| [[安全红队与对抗评测]] | 系统卡安全章节背后的红队方法，与第 4.2 节「红队与外部评估」一行对应 | 红队方法谱系 |
| [[评测与排行榜可靠性]] | 跨卡横比前对齐协议的方法依据，对应第五节第 4 条 | 评测协议与去污方法 |
| [[智能体工具与长程任务]] | 卡内「智能体与工具」一行所指的能力面 | 智能体能力本身 |
| [[多语言与跨语种]] | 语种覆盖应写入卡字段；与第五节第 4 条的语言覆盖差异对应 | 多语言模型与评测本身 |
| [[Qwen3技术报告深读]] | 开放权重模型族的技术报告，作为与系统卡、模型卡并列的「技术报告」体裁对照 | 该报告的架构与训练配方 |
| [[思维链可监控性]] | 系统卡里的思维链监控类评测属于第 4.2 节对照表「对齐深层」一行；这类评测的概念与度量方法看那篇 | 可监控性的评测方法与失效路径 |
| [[SystemCard谱系时间线]] | 各厂文档按时间排列的完整节点，第二节只取体裁转折 | 逐年发布节点 |

同属 System Card 系的还有 [[GPT6Astra系统卡深读]]、[[GPT61Sol系统卡短报]]、[[GPT6SolLuna十月版系统卡短报]]、[[ClaudeOpus5系统卡深读]]、[[ClaudeFable与Mythos51]]、[[ClaudeOpus55系统卡短报]]、[[ClaudeSonnet55系统卡短报]]、[[ClaudeHaiku55系统卡短报]]：它们是第四节所述体裁在后续型号上的实例，本篇未逐张并入对照表。全部挂载见 [[MOC_模型与技术报告]]。

## 九、延伸阅读

- Mitchell 等：原文 §4（九段章节与提示问题，Figure 1）、§5（两个工作示例，Figure 2、3）、§6（局限与展望）。
- [Annotated Model Card Template](https://huggingface.co/docs/hub/en/model-card-annotated)：Hub 模型卡逐节填写说明，与第 3.2 节的正文块对应。
- [Model Card Guidebook](https://huggingface.co/docs/hub/en/model-card-guidebook)：Hugging Face 的模型卡指南，回顾 Mitchell 以来的模型文档实践。
- [OpenAI o1 System Card](https://arxiv.org/abs/2412.16720)：早期厂商系统卡的范例，可与第四节的对照表对读。
