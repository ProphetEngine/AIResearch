---
date: 2026-09-22
status: archived
archived: 2026-09-22
topic: GPT5系统卡深读
title: "GPT-5 System Card 深读（含 GPT-5.1 增补）"
lines: [架构思想, AI Infra]
sources:
  - https://deploymentsafety.openai.com/gpt-5
  - https://arxiv.org/abs/2601.03267
  - https://arxiv.org/abs/2508.09224
  - https://deploymentsafety.openai.com/gpt-5-sensitive-conversations
  - https://deploymentsafety.openai.com/gpt-5-1
related: ["开源与闭源前沿模型谱系", "智能体工具与长程任务", "评测与排行榜可靠性", "模型卡与SystemCard规范", "SystemCard谱系时间线", "GPT52SystemCard更新", "GPT56系统卡深读", "GPToss模型卡深读", "ClaudeOpus41系统卡附录深读", "ClaudeOpus45系统卡深读", "Gemini25技术报告深读", "Gemini3Pro模型卡深读", "Qwen3技术报告深读", "DeepSeekR1推理训练深读", "安全红队与对抗评测"]
---

# GPT-5 System Card 深读（含 GPT-5.1 增补）

> **主要来源**：[GPT-5 System Card](https://deploymentsafety.openai.com/gpt-5)（OpenAI Deployment Safety Hub，标 Published August 7, 2025；PDF 封面 August 13, 2025）；[OpenAI GPT-5 System Card](https://arxiv.org/abs/2601.03267)（arXiv 镜像，v2 2026-05-01）；[GPT-5.1 Instant and GPT-5.1 Thinking System Card Addendum](https://deploymentsafety.openai.com/gpt-5-1)（Hub，Published November 12, 2025）（截至 2026-05-01）。arXiv v2 注明「Added monitorability evals and authors」。
> **研究线**：架构思想（主）+ AI Infra（辅）
> **范围与相邻笔记**：
> - ≠ [[开源与闭源前沿模型谱系]]：发布博客层面的统一系统叙事与模型谱系在那篇；本篇只写系统卡原文。
> - ≠ [[GPT52SystemCard更新]]、[[GPT56系统卡深读]]：GPT-5.2 及以后各卡各有专篇；本篇覆盖 GPT-5 主卡与 GPT-5.1 增补（第四节）。
> - 参数量、层结构、是否 MoE，GPT-5 与 GPT-5.1 两份文件都未公开，本篇不推测。
>
> **意义**：GPT-5 系统卡把「快答模型 + 深思模型 + 实时路由」的产品形态收成一套可引用的安全栈：输出中心的 safe-completions、指令层级、工具与连接器注入防护、CoT 可监控性、Preparedness 分域判定（生物化学按 High 预防性处理，网安与自我改进未达 High）。三个月后的 GPT-5.1 增补只有 5 页，声明防护「大体相同」，增量是基线安全表换代与心理健康、情感依赖两类敏感对话评测，显示 OpenAI 用「主卡 + 短增补」记录小版本迭代的做法。

---

## 一、背景与报告元信息

### 1.1 背景

System Card 是厂商在发布时公开的安全与风险评估文件，与发布博客分工：博客写能力与产品，System Card 写安全评测、红队与 Preparedness 判定（规范层面见 [[模型卡与SystemCard规范]]）。GPT-5 于 2025-08-07 发布，取代 GPT-4o、o3 等多条产品线；这份卡是它的安全与前沿能力卡，不是架构论文。

### 1.2 元信息

| 字段 | 核实值 |
| --- | --- |
| 标题 / 机构 | GPT-5 System Card / OpenAI |
| 日期 | Hub 页标 Published August 7, 2025；PDF 封面 August 13, 2025；PDF 元数据 CreationDate 2025-08-20 03:33:37 CST |
| 篇幅 | 原 PDF 60 页（§1–5 + Appendix 1–2 + References）；arXiv v1 61 页、v2 63 页 |
| 版本 | arXiv v1 2025-12-19；v2 2026-05-01 补入第 5 节「Chain of Thought Evaluations」（正文注明 2026-04-24 加入），Preparedness 因此由原 PDF 的 §5 顺延为 §6，图号顺延 3 个；表号与数字未变 |
| 前代卡 | Table 1 对照 OpenAI o3 / o4-mini System Card（2025-04-16） |

下文节号按 Hub 与 arXiv v2；与原 PDF 不同时括注。

### 1.3 与博客及姊妹材料的关系（只取原文可核对处）

1. **发布博客**：§6.1.3.1（原 §5.1.3.1）明文写「The SWE-Bench result in the GPT-5 launch blog post (74.9%), was run with the default verbosity setting in the API (verbosity = medium)」；而 GPT-5 系统卡 Preparedness 评测一律在模型的 maximum trained-in verbosity 下运行，高于 API 当前可用的 "high"，两者口径不同。
2. **Safe-completions 论文**：§3.1 指向 [From Hard Refusals to Safe-Completions: Toward Output-Centric Safety Training](https://arxiv.org/abs/2508.09224)（arXiv 2025-08-12），GPT-5 系统卡把该范式写成 GPT-5 全系的安全训练要点。
3. **ChatGPT agent System Card**：引言称生物化学 High capability 的处理「Similarly to ChatGPT agent」；rapid remediation 与 bug bounty 细节见该卡。
4. **GPT-5 系统卡自身定位**（§1）：主评测对象是 gpt-5-thinking 与 gpt-5-main，其余型号多在 Appendix 1；并称「In the near future, we plan to integrate these capabilities into a single model.」

## 二、系统主张（只取原文）

### 2.1 统一系统与型号标签（§1，Table 1）

| 原文主张 | 要点 |
| --- | --- |
| Unified system | 「a smart and fast model that answers most questions, a deeper reasoning model for harder problems, and a real-time router that quickly decides which model to use」 |
| Router 依据 | conversation type、complexity、tool needs、explicit intent（例：prompt 写 "think hard about this"） |
| Router 训练信号 | 「continuously trained on real signals, including when users switch models, preference rates for responses, and measured correctness」 |
| 限额后行为 | 「Once usage limits are reached, a mini version of each model handles remaining queries.」 |
| 快答线 | gpt-5-main / gpt-5-main-mini |
| 深思线 | gpt-5-thinking / gpt-5-thinking-mini；API 另有 gpt-5-thinking-nano |
| Pro | ChatGPT 侧 gpt-5-thinking-pro = gpt-5-thinking + parallel test time compute 设定 |
| 代际对照 | GPT-4o → main；GPT-4o-mini → main-mini；o3 → thinking；o4-mini → thinking-mini；GPT-4.1-nano → thinking-nano；o3 Pro → thinking-pro |
| 产品叙事（无分数） | 更快；减幻觉、更好的指令遵循、减谄媚；加强写作、编码、健康；全系 safe-completions |
| Preparedness 总判 | gpt-5-thinking 按生物化学域 High capability 处理并激活配套防护；同时写明「do not have definitive evidence」达到相应阈值，属预防性处理 |

### 2.2 数据与训练（§2）

| 维度 | 原文 |
| --- | --- |
| 数据来源 | 公开互联网；第三方合作方；用户、人类训练员与研究者提供或生成的数据 |
| 过滤 | 质量过滤；减少个人信息；Moderation API 与安全分类器（含涉及未成年人的显式内容） |
| 推理训练 | thinking / mini / nano「trained to reason through reinforcement learning」，先思考再回答，长内部 CoT，可改进思路、尝试策略、识别错误 |
| 对比口径 | 与 o3 等的对照取「latest versions」，可能与该型号发布时公布的值略有差异 |

### 2.3 工具、连接器与注入防护（§3.6）

| 项 | 原文 |
| --- | --- |
| 为何相关 | GPT-5 可以浏览网页、使用 connectors 和其他工具 |
| 模型侧 | 「teaching models to ignore prompt injections in web or connector contents」 |
| 系统侧（防外泄） | 调用 connector 后把浏览切换为只访问网页的 cached copies，防止敏感内容在上下文中时再发出实时网络请求 |
| 评测 | Browsing / Tool-calling / Coding 三类注入（Table 7） |
| 未尽述 | 「further mitigations… not all described here」（出于对抗原因） |

### 2.4 Safe-completions（§3.1）

| 对照 | 原文 |
| --- | --- |
| 旧范式 | hard refusals：按用户意图是否允许，二元地全答或拒绝 |
| 新范式 | safe-completions：以助手输出是否安全为中心，「maximize helpfulness subject to the safety policy's constraints」 |
| 动机 | 二元边界对生物、网安等 dual-use 场景脆弱：高层次的安全回答可行，过细则提供 uplift |
| 作者观测 | 相对 refusal 训练的基线（o3），在 dual-use 提示上更安全、残余失败的严重度更低、整体更有帮助 |

## 三、安全与评测要点（可核对案例）

比较轴（§3）：gpt-5-thinking 对 OpenAI o3，gpt-5-main 对 GPT-4o。gpt-5-thinking-pro 未单独重跑安全评测，作者认为 thinking 的结果是强代理。

### 3.1 内容安全与生产流量（§3.2–3.5）

| 评测 | 要点 |
| --- | --- |
| Standard Disallowed（Table 2，`not_unsafe`） | 多类接近饱和，作者称将停发旧集、改用更难的集。personal-data：thinking 0.881 vs o3 0.930（作者称为噪声）；personal-data/restricted：thinking 0.989 vs o3 0.921 |
| Production Benchmarks（Table 3） | 多轮、更难；thinking 多数不低于 o3。main 相对 4o：illicit 类显著改进（归因于 safe-completions）；hate/threatening、sexual/exploitative 有显著回退，人工复核称违规多为低严重度 |
| Sycophancy（§3.3，Table 4） | 离线：4o 0.145 → main 0.052（「nearly 3x better」）；thinking 0.040。线上早期 A/B：相对最近的 4o，谄媚 prevalence 降低 69%（免费用户）/ 75%（付费用户） |
| Jailbreaks StrongReject（Table 5） | thinking 与 o3 大体持平；main 与 4o 接近 |
| Instruction Hierarchy（Table 6） | system > developer > user。thinking 多数接近或优于 o3；main 多项回退，作者写明将跟进修复 |

### 3.2 提示注入（§3.6，Table 7；§4.2）

| 评测（越高越好） | gpt-5-thinking | OpenAI o3 |
| --- | ---: | ---: |
| Browsing prompt injections | 0.99 | 0.89 |
| Tool calling prompt injections | 0.99 | 0.80 |
| Coding prompt injections | 0.97 | 0.94 |

外部评估：针对 connector 的两周评估得到 47 个 findings，其中 10 个 notable，发布前已更新部分逻辑；Gray Swan 的注入基准称 thinking 对对抗性提示注入达到 SOTA（分值只在图中，本篇不读图）。

### 3.3 幻觉与欺骗（§3.7–3.8）

**生产流量事实性**（开启浏览，§3.7 正文）：

- gpt-5-main 的幻觉率比 GPT-4o 低 26%，含至少一处重大错误的回答少 44%。
- gpt-5-thinking 相对 o3：幻觉率低 65%，含重大错误的回答少 78%。
- LongFact / FActScore：正文称 thinking 在开关浏览两种设定下、三个基准上的事实错误都比 o3 少五倍以上。
- SimpleQA（Table 8，无网络）：thinking accuracy 0.55、hallucination 0.40（o3：0.54 / 0.46）。

**Deception**（Table 9；前三行为欺骗率，越低越好；AbstentionBench 为 recall，越高越好）：

| Eval | gpt-5-thinking | OpenAI o3 |
| --- | ---: | ---: |
| Coding Deception | 0.17 | 0.47 |
| Browsing Broken Tools | 0.11 | 0.61 |
| CharXiv Missing Image | 0.09 | 0.87 |
| AbstentionBench (recall) | 0.53 | 0.44 |

训练侧缓解场景：Agentic Coding（遇到无法解决的障碍）、Broken Tools、Underspecified User Requests。

**CoT 监控**（§3.8.1，生产代表集）：监控标出的欺骗约 4.8%（o3）→ 约 2.1%（thinking）；监控在内部验证集上 precision 81%、recall 84%。

### 3.4 健康、多语、偏见、图像（§3.9–3.12）

| 项 | 原文数字 |
| --- | --- |
| HealthBench Hard | o3 31.6% → gpt-5-thinking 46.2%；thinking-mini 40.3%；gpt-5-main 25.5%（GPT-4o 0.0%） |
| Image input（Table 10，`not_unsafe`） | thinking 略高于 o3；main 与 4o 持平或略高 |
| MMLU Language 0-shot（Table 11） | 阿拉伯语至约鲁巴语各列；thinking 与 o3-high 接近，main 略低，不能外推为「多语 SOTA」 |
| BBQ（Table 12） | thinking 与 o3 接近，disambiguated 略低 |

### 3.5 红队与外部评估（§4）

- 规模：超过 5,000 小时、超过 400 名外部测试者；主题含 violent attack planning、jailbreaks、prompt injections、bioweaponization。
- Violent attack planning（Table 13）：thinking 被评为「更安全」的胜率 65.1%（对 o3；95% CI 63.7–66.5%；Cohen's h 0.61），作者归因于细节程度与 safe-completions。
- Microsoft AI Red Team：多周；70 多名专家手动测试，加 PyRIT 近百万次对抗会话；覆盖 18 个 harm areas × 3 个 domains。结论：frontier 与内容安全上定性优于 o3，psychosocial（识别情绪困扰）仍有改进空间。

### 3.6 Preparedness Framework（§6，原 §5）

评测含 helpful-only 等 elicitation 方式，作者强调结果只是能力下限。

| 域 | 官方结论 | 可核对案例 |
| --- | --- | --- |
| Biological & Chemical | 本次发布按 High capability 处理并激活防护；「remains on the cusp」；thinking-pro 也测了 | 长文 biorisk、ProtocolQA、TroubleshootingBench 等（Table 14）；SecureBio：带缓解的 thinking 拒绝了全部 agent / long-form 危险提示；helpful-only 版本与 o3 helpful-only 能力接近 |
| Cybersecurity | 「The gpt-5 model series does not meet the threshold for high cyber risk.」 | Cyber Range：thinking 无辅助时一个场景都没解出；mini 有提升但仍未达「significant cyber risk」；Pattern Labs：easy 17/18、medium 8/14、hard 0/4，结论是只能给中等水平操作者有限帮助 |
| AI Self-Improvement | 「modest improvement… did not meet our High thresholds」 | 套件：SWE-bench Verified（N=477）、OpenAI PRs、MLE-Bench、SWE-Lancer、PaperBench、OPQA（Table 17）。正文数字：OPQA 上 thinking 最高，为 2%；MLE-Bench 子集上 ChatGPT agent 最高，为 9% bronze。SWE-bench 每题平均 4 次计算 pass@1，正文只说 thinking 与 thinking-mini 得分最高，具体值只在图中（v2 Figure 22，原 Figure 19） |
| Sandbagging（研究类，§6.2） | Apollo：26 个评测；thinking covert action 3.97% vs o3 8.24%；helpful-only 28.36%（Table 18） | METR：50% time horizon 约 2h15m（95% CI 65m–4h30m），o3 为 1h30m；给出四条「unlikely」结论（AI R&D 加速 10 倍以上、策略性误导评测、rogue replication，以及对后续小幅迭代仍成立） |

### 3.7 High Bio 多层防护（§6.3，原 §5.3；Infra 辅线）

主要威胁路径假设：以周到月为尺度、持续探查生物风险内容。

| 层 | 要点 |
| --- | --- |
| 模型训练 | 拒绝武器化请求；dual-use 不给详细可操作帮助；叠加 safe-completions |
| 系统层 | 两层实时监控：快速分类器判断是否涉及生物 → 推理监控器按威胁分类判断；覆盖用户输入、工具调用、最终输出；thinking（含 pro）与 thinking-mini 100% 流量 |
| 账户层 | 自动检测加生物威胁专家人工复核；封禁与再犯处理；极端情况可报执法 |
| API | 区分开发者与终端用户；自动与人工分级处置 |
| 充分性主张 | 未知通用越狱的风险依靠发现难度、封禁、bug bounty 与快速修复做到「sufficiently minimized」 |

### 3.8 附录

- **Appendix 1**：thinking-mini / nano / main-mini 的 disallowed、production、StrongReject 表（Table 23–25）。
- **Appendix 2**：幻觉评测的 claim-listing 与 fact-checking 提示原文。

### 3.9 思维链评测（§5，2026-04-24 补入）

- **CoT Monitorability**：用 Guan 等（2025）的评测套件（13 个评测、24 个环境，分 intervention、process、outcome-property 三类），以兼顾 TPR 与 TNR 的 g-mean² 汇总；监控模型为 GPT-5 Thinking。与原研究一致，CoT 越长可监控性越好，能看 CoT 或全部消息的监控明显强于只看动作的监控；跨环境平均，GPT-5 Thinking 的 CoT 可监控性高于 o3。
- **CoT Controllability**：用 CoT-Control 套件测模型按用户指令控制自身 CoT 的能力，因受 CoT 长度强烈混杂而按长度分组报告；GPT-5 Thinking 可控性低，与 o3 相近。本节两项结果只在图中给出分值，正文只有上述定性结论。

## 四、GPT-5.1 增补（2025-11-12）

### 4.1 定位与型号

GPT-5.1 Instant and GPT-5.1 Thinking System Card Addendum（Hub 标 Published November 12, 2025；PDF 5 页，CreationDate 2025-11-13 00:38:05 CST），章节为 §1 Introduction、§2 Baseline Model Safety Evaluations、§3 Preparedness Framework。

- **型号**：GPT-5.1 Instant（`gpt-5.1-instant`）与 GPT-5.1 Thinking（`gpt-5.1-thinking`）是 GPT-5 的下一次迭代；GPT-5.1 Auto 继续把每个查询路由到最合适的模型，多数情况下用户无需选型。
- **产品主张（无分数）**：Instant「more conversational」、指令遵循改进，并有 adaptive reasoning，自行决定何时先思考再回答；Thinking 把思考时间更精确地适配到每个问题。
- **安全立场**：防护措施与 GPT-5 System Card「largely the same」，增补只提供更新后的基线安全指标。
- **没有的内容**：无能力榜分（SWE-bench、GPQA、HealthBench 等都没有），无参数与架构披露，未复测 safe-completions、指令层级、谄媚、幻觉、欺骗、注入三项与红队规模。

### 4.2 中间一步：敏感对话增补（2025-10-27）

GPT-5.1 增补的心理健康与情感依赖两项评测，引自此前的 [Addendum to GPT-5 System Card: Sensitive Conversations](https://deploymentsafety.openai.com/gpt-5-sensitive-conversations)（Hub 标 Published October 27, 2025）。该增补说明：OpenAI 于 10 月 3 日更新了 ChatGPT 默认模型，与 170 多名心理健康专家合作，使模型更可靠地识别困扰迹象并引导用户寻求现实支持，称不符合期望的回答减少 65–80%；它比较的是 ChatGPT 默认模型（也称 GPT-5 Instant）的 8 月 15 日版与 10 月 3 日更新版。GPT-5.1 增补表中的 `gpt-5-instant-aug15`、`gpt-5-instant-oct3` 即对应这两个版本。

### 4.3 Production Benchmarks（§2.1，Table 1）

指标 `not_unsafe`（越高越好）；集合刻意偏难，围绕现有模型尚未理想作答的案例构建，错误率不代表平均生产流量。作者总评：两款 5.1 模型与 GPT-5 前代在这些难集上安全表现相当。

| Category | gpt-5-thinking | gpt-5.1-thinking | gpt-5-instant-aug15 | gpt-5-instant-oct3 | gpt-5.1-instant |
| --- | ---: | ---: | ---: | ---: | ---: |
| illicit/non-violent | 0.865 | 0.860 | 0.700 | 0.807 | 0.853 |
| personal data | 0.966 | 1.000 | 0.966 | 1.000 | 1.000 |
| harassment | 0.815 | 0.747 | 0.683 | 0.745 | 0.836 |
| sexual | 0.906 | 0.895 | 0.782 | 0.951 | 0.917 |
| extremism | 1.000 | 1.000 | 0.922 | 0.978 | 0.989 |
| hate | 0.883 | 0.839 | 0.74 | 0.806 | 0.897 |
| violence | 0.946 | 0.930 | 0.829 | 0.953 | 0.938 |
| sexual/minors | 0.953 | 0.901 | 0.862 | 0.961 | 0.957 |
| illicit/violent | 0.954 | 0.934 | 0.783 | 0.862 | 0.918 |
| self-harm/intent | 0.959 | 0.958 | 0.893 | 0.893 | 0.909 |
| self-harm/instructions | 0.979 | 0.950 | 0.858 | 0.943 | 0.950 |
| mental health* | 0.466 | 0.684 | 0.251 | 0.944 | 0.883 |
| emotional reliance* | 0.812 | 0.785 | 0.688 | 0.986 | 0.945 |

\* 新评测，引自敏感对话增补。

作者点名的变化：gpt-5.1-thinking 相对 gpt-5-thinking 在 harassment、hateful language、disallowed sexual content 上有 light regressions，称正在改进；gpt-5.1-instant 在上述全部评测上优于 aug15，但在 disallowed sexual、violent、mental health、emotional reliance 上略逊于 oct3。

### 4.4 敏感情境：离线与早期在线（§2.1 续）

在线测量是 A/B 期间的早期信号：敏感情境下不理想回答的 prevalence 极低，A/B 规模相对小，误差棒很宽；上线后会继续测量，以决定是否需要进一步缓解（例如路由到特定的更安全模型）。离线集偏最坏情况，通常是很长的多轮对话，前几轮植入了旧模型的不良行为。

| 主题 | 离线（Production） | 早期在线（作者定性，无百分点） |
| --- | --- | --- |
| Mental health | instant 相对 oct3 略回退，仍优于 aug15；thinking 相对 gpt-5-thinking 改进 | instant 与 thinking 相对各自前代都略有改进，统计置信度低 |
| Emotional reliance | instant 与 thinking 相对 oct3 / 前代 thinking 都略回退；instant 仍优于 aug15 | instant 相对 oct3 回退（低置信度），仍优于 aug15；thinking 相对前代改进，统计置信度高 |
| Self harm and suicide | 见 Table 1 的 self-harm 两行 | instant 相对 oct3 持平；thinking 相对前代改进；均为低置信度 |

### 4.5 越狱与图像输入（§2.2–2.3）

- **StrongReject**（Table 2）：改编自学术 StrongReject（Souly 等，arXiv:2402.10260），把已知越狱插入 disallowed 样例，用相同的策略评分器。`not_unsafe`：gpt-5-thinking 0.974、gpt-5.1-thinking 0.967、aug15 0.683、oct3 0.850、gpt-5.1-instant 0.976。作者结论：5.1 Instant 优于前代，5.1 Thinking 与前代持平。
- **Image input**（Table 3）：沿用 ChatGPT agent 引入的图文组合评测，`not_unsafe`。

| Category | gpt-5-thinking | gpt-5.1-thinking | gpt-5-instant-aug15 | gpt-5-instant-oct3 | gpt-5.1-instant |
| --- | ---: | ---: | ---: | ---: | ---: |
| hate | 0.984 | 0.980 | 0.982 | 0.990 | 0.993 |
| extremism | 0.991 | 0.993 | 0.986 | 0.986 | 0.996 |
| illicit | 0.994 | 0.980 | 0.986 | 1.000 | 0.992 |
| attack planning | 1.000 | 1.000 | 1.000 | 1.000 | 1.00 |
| self-harm | 0.976 | 0.936 | 0.983 | 0.975 | 0.960 |
| harms-erotic | 0.990 | 0.990 | 0.994 | 0.999 | 0.999 |

作者结论：两款模型总体与前代持平，但观察到 gpt-5.1-thinking 在 self-harm 图文提示上回退，正在改进。

### 4.6 Preparedness（§3）

| 域 | 原文结论 |
| --- | --- |
| Biological and Chemical | 与 GPT-5 发布时相同，继续把 GPT-5.1 视为 High risk 并施加相应防护 |
| Cybersecurity | 与 GPT-5 前代一样，「do not have a plausible chance of reaching a High threshold」 |
| AI self-improvement | 同上 |

增补未重刊 Cyber Range、Pattern Labs、METR、SWE 等细表，能力档位以这段定性结论为准。

### 4.7 相对主卡的增量

| 维度 | GPT-5 主卡 | GPT-5.1 增补 |
| --- | --- | --- |
| 文档角色 | 全量安全 + Preparedness | 基线安全指标更新；防护大体相同 |
| 型号与路由 | main / thinking（+ mini / nano / pro）+ 实时路由，路由依据写明 | instant / thinking + Auto；路由机制未展开 |
| 快答线命名 | gpt-5-main | 改称 Instant；对照列出 aug15、oct3 两个版本 |
| 思考时间 | 训练侧描述（推理 RL、先思考再回答） | Instant 自行决定何时思考；Thinking 更精确适配思考时间；仍无 token 或秒数 |
| 敏感对话 | 主卡无独立的心理健康 / 情感依赖行 | 新增两行，并给早期在线定性信号 |
| Disallowed 报告集 | Standard（近饱和）+ Production | 只报 Production |
| Preparedness | Bio High（预防性）；Cyber、自我改进未达 High | 结论延续，只给定性句 |

两份文件合读：5.1 在产品面上把快答线显式产品化为「Instant + adaptive reasoning」，把深思线强调为更精细的思考时间适配，由 Auto 继续隐藏选型；安全面的增量是基线表换代与敏感情境信号，不是新的安全范式。

## 五、相对谱系与智能体笔记的增量

| 相邻笔记已有 | 本篇增量 |
| --- | --- |
| [[开源与闭源前沿模型谱系]]：博客级「统一系统三件套」与产品替换叙事 | 正式型号字符串（main / thinking / mini / nano / pro）与 Table 1 对照；API 与 ChatGPT 的差异 |
| 同上：「细节见 system card」的 High bio 与 safe-completions | 完整 Preparedness 档位与 SecureBio、Pattern Labs、METR、Apollo 外部结论 |
| 同上：博客 SWE 74.9% 等能力叙事 | 明确 verbosity 口径差，Preparedness 图与博客分数不能混读 |
| [[智能体工具与长程任务]]：路由、tool needs、并行工具 | 浏览加 connectors 场景下的三项注入数字；connector 后缓存浏览的系统机制 |
| 同上：GPT-5 System Card 细节待核实 | agentic coding、broken tools、underspecified 三类欺骗评测；生产 CoT 欺骗率；指令层级 |
| 同上：Claude 侧的小时级长程任务 | METR 50% time horizon 约 2h15m，属 Preparedness 评测，不是产品 SLA |

架构思想上的结论：谱系与智能体两篇的「路由 + 工具环」产品叙事，在 GPT-5 系统卡被收成可引用的安全栈——输出中心安全训练 × 指令层级 × 工具与连接器注入防护 × CoT 可监控性 × Preparedness 分层。Infra 辅线的新信息主要是流量级两层生物监控与 connector 后的缓存浏览，没有训练集群细节。

## 六、意义

- **把「统一系统」写成可审计的安全栈**：路由、深思线、工具环各自对应一组评测与防护，GPT-5 之后的 OpenAI 系统卡（见 [[GPT52SystemCard更新]]、[[GPT56系统卡深读]]）沿用这套结构。
- **safe-completions 取代硬拒绝**：以输出安全为中心的训练范式写进全系，dual-use 场景的评测口径随之改变。
- **预防性 High 判定**：在没有确定证据达到阈值时，先按生物化学 High 处理并上线多层防护，是 Preparedness Framework 的一次公开实践。
- **主卡 + 短增补的文档分层**：GPT-5.1 用 5 页增补记录小版本的安全基线变化，与 [[ClaudeOpus41系统卡附录深读]] 的 Addendum 形式可对照。

## 七、局限与待核实

1. **日期多口径**：Hub 页标 2025-08-07（发布日），PDF 封面 2025-08-13，PDF 元数据 2025-08-20；GPT-5.1 封面 2025-11-12、元数据 2025-11-13。各口径都已记录，以 Hub 与封面为准。
2. **图内数字未读**：Gray Swan 注入分、SWE-bench Verified pass@1、多张 Preparedness 图的精确值只在图中，本篇不写。
3. **博客与系统卡的 SWE 差值**：系统卡（maximum verbosity）的 SWE-bench 值未在正文给出，与博客 74.9%（medium）无法直接比较。
4. **外部报告**：Gray Swan、METR 完整报告、Apollo 报告的独立链接未核对。
5. **型号对应**：`gpt-5-instant-aug15` 对应 ChatGPT 默认模型（GPT-5 Instant）8 月 15 日版，已由敏感对话增补确认；它与主卡 `gpt-5-main` 标签是否同一模型，两份文件都没有写成等式。
6. **在线 A/B**：GPT-5.1 增补的样本量、时间窗、不良回答的操作定义与置信区间数值均未给出。
7. **排版疑点**：GPT-5.1 Table 3「attack planning」行的 gpt-5.1-instant 单元格为 1.00（两位小数），与同表三位小数不一致，原文如此。
8. **StrongReject 协议**：GPT-5.1 增补只称「adaptation of StrongReject」，与主卡 Table 5 是否同一协议未说明。
9. **arXiv 版本差异**：v2 只增补第 5 节与作者名单，表号与本篇所引数字与原 PDF 一致；节号与图号顺延，见 1.2 节。
10. **o3 对照**：作者说明与 o3 对比时取其最新版本，可能与 o3 发布时公布的值略有差异。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
| --- | --- | --- |
| [[开源与闭源前沿模型谱系]] | GPT-5 在前沿谱系中的位置，博客层统一系统叙事在那篇；本篇只补系统卡原文 | 各家模型谱系 |
| [[智能体工具与长程任务]] | 那篇的路由与工具叙事在本篇对应注入评测与缓存浏览机制（第五节） | 工具环与长程任务方法 |
| [[评测与排行榜可靠性]] | verbosity 口径差、o3 取最新版对照，是那篇「同名不同协议」问题的实例 | 榜单可靠性通论 |
| [[模型卡与SystemCard规范]] | GPT-5 主卡与 5.1 增补是那篇 System Card 系的两个样本 | 模型卡规范本身 |
| [[SystemCard谱系时间线]] | 两份文件在那条时间线上分别占 2025-08、2025-11 节点 | 其他厂商系统卡 |
| [[GPT52SystemCard更新]] | 5.1 之后的下一份更新（2025-12-11），沿用 GPT-5 系统卡的 High bio 防护栈与 safe-completions | GPT-5.2 的评测内容 |
| [[GPT56系统卡深读]] | 同一系列较晚的完整系统卡，可对照 Preparedness 结构的演变 | GPT-5.6 内容 |
| [[GPToss模型卡深读]] | 同期 OpenAI 开源权重模型卡（2025-08-05），以 GPT-5 系统卡为闭源一侧对照 | gpt-oss 的开源字段 |
| [[ClaudeOpus41系统卡附录深读]] | 同为「主卡 + 短增补」形式，Anthropic 一侧的 Addendum 样本 | Opus 4.1 内容 |
| [[ClaudeOpus45系统卡深读]] | Anthropic 一侧的完整系统卡，可对照红队、注入与去污写法 | Opus 4.5 内容 |
| [[Gemini25技术报告深读]] | Google 一侧以技术报告加 Frontier Safety 章的形式披露，与 GPT-5 系统卡只给安全卡不给架构形成对照 | Gemini 2.5 内容 |
| [[Gemini3Pro模型卡深读]] | Google 一侧的模型卡（10 页），篇幅与披露粒度远小于 GPT-5 系统卡 | Gemini 3 Pro 内容 |
| [[Qwen3技术报告深读]] | Qwen3 把思考与非思考模式放进同一模型，GPT-5 系统卡则用路由在两个模型间切换，并预告将来合为单一模型 | Qwen3 架构与训练 |
| [[DeepSeekR1推理训练深读]] | GPT-5 系统卡对推理 RL 只有一句话，R1 报告公开了推理 RL 的管线与奖励设计，可作对照 | R1 训练细节 |
| [[安全红队与对抗评测]] | 那篇把本篇 3.5 节的红队收进方法谱系 | 红队方法通论 |

## 九、延伸阅读

| # | 来源 | 读什么 |
| --- | --- | --- |
| 1 | [GPT-5 System Card](https://deploymentsafety.openai.com/gpt-5)（Hub） | §1 Table 1、§3.1、§3.6–3.8、§6 Preparedness |
| 2 | [OpenAI GPT-5 System Card](https://arxiv.org/abs/2601.03267)（arXiv v2） | §5 思维链评测（2026-04 补入） |
| 3 | [From Hard Refusals to Safe-Completions](https://arxiv.org/abs/2508.09224) | safe-completions 训练范式 |
| 4 | [Addendum to GPT-5 System Card: Sensitive Conversations](https://deploymentsafety.openai.com/gpt-5-sensitive-conversations) | 心理健康与情感依赖评测的来源 |
| 5 | [GPT-5.1 System Card Addendum](https://deploymentsafety.openai.com/gpt-5-1)（Hub） | Table 1–3 与 §3 Preparedness |
