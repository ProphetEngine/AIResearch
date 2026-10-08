---
title: Claude Opus 5 System Card 深读
topic: ClaudeOpus5系统卡深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://www.anthropic.com/system-cards
 - https://www.anthropic.com/news/claude-opus-5
related: ["ClaudeOpus45系统卡深读", "ClaudeFable与Mythos51", "ClaudeOpus55系统卡短报", "安全红队与对抗评测", "宪法分类器防御", "SHADEArena隐瞒与监控", "Prompt注入架构防御", "GPT56系统卡深读", "模型卡与SystemCard规范", "SystemCard谱系时间线"]
archived: 2026-09-22
---

# Claude Opus 5 System Card 深读

> **主要来源**：[System Card: Claude Opus 5](https://www.anthropic.com/system-cards)（Anthropic，封面 July 24, 2026，变更记录至 2026-08-19，仅有 PDF 版，此处挂官方系统卡索引页，以下简称该卡）；[Introducing Claude Opus 5](https://www.anthropic.com/news/claude-opus-5)（Anthropic 发布公告，2026-07-24，以下简称公告）（截至 2026-08-19）。
> **研究线**：架构思想（RSP 威胁模型与对齐风险的写法）+ 评测字段（cyber 能力梯与分类器分层）
> **范围与相邻笔记**：
> - ≠ [[ClaudeOpus45系统卡深读]]：本篇不写 Opus 4.5 本身；该卡全文没有拿 Opus 4.5 作对照，第九节的增量对照只比结构与政策，不横比分数。
> - ≠ [[ClaudeFable与Mythos51]]：Fable 5.1 与 Mythos 5.1 系统卡在那篇，本篇不收。
> - ≠ [[安全红队与对抗评测]]：红队方法全文在那篇，本篇只录该卡的评测结论。
> - 本篇不收可操作的攻击步骤。
>
> **意义**：Opus 5 是 Anthropic 在 ASL-3 下发布的日常旗舰，能力相对 Opus 4.8 全面抬升、多项评测与 Fable 5 和 Mythos 5 可比；该卡的写法有三处值得记下：一是 RSP 结论改用 CB-1 / CB-2 与 Autonomy-1 / Autonomy-2 威胁模型表述，并以「不超过 Mythos 5」为由沿用 Opus 4.8 的保护组合；二是 cyber 部分形成「找洞接近 Mythos 5、写利用明显落后」的多套件一致格局，护栏沿用 Fable 级两段式分类器，但放开源码漏洞发现、继续拦二进制漏洞发现；三是对齐部分在自称「迄今最对齐」的同时，坦白过度自信、事实幻觉略多，以及回退到 Opus 4.8 后部分对齐维度反而变差。

## 一、问题背景

Opus 5 发布时，Claude 5 族已有 Fable 5 与 Mythos 5，前一代日常 Opus 是 Opus 4.8。该卡执行摘要称 Opus 5 是「an upgrade to Claude Opus 4.8」，公告称其接近 Fable 5 的前沿智能、价格为其一半。能力逼近 Fable 5 与 Mythos 5 之后，该卡要回答三个问题：RSP 上能否沿用 Opus 4.8 的 ASL-3 保护（第四节）；cyber 能力落在 Opus 4.8 与 Mythos 5 之间的什么位置（第五节）；Fable 级分类器用在日常旗舰上时，放行范围怎么调（第六节）。

## 二、脉络

| 时间 | 文档 | 关键一步 |
|---|---|---|
| 2025-11 | Claude Opus 4.5 系统卡（见 [[ClaudeOpus45系统卡深读]]） | 上一张完整的 Opus 卡；ASL-3，按 CBRN-4 与 AI R&D-4 阈值表述 |
| 2026-04 | Mythos Preview 系统卡 | 该卡 §2.4 的 stealth 率以 Mythos Preview 为上方对照 |
| 2026-05 | Claude Opus 4.8 系统卡 | 该卡的主对照；Opus 5 沿用其 ASL-3 保护，护栏命中时默认回退到 Opus 4.8 |
| 2026-06 | Claude Fable 5 与 Mythos 5 系统卡 | 该卡以「不超过 Mythos 5」判 CB 风险，护栏沿用 Fable 5，只放开源码漏洞发现 |
| 2026-07-24 | Claude Opus 5（该卡与公告） | 改用 CB-1 / CB-2 与 Autonomy 威胁模型表述；cyber 能力梯与两段式分类器 |
| 2026-08-19 | 该卡变更记录 | 补入 §5.2.2.1 prompt injection bug bounty 结果，重跑 §5.2.2.4 Cowork 结果 |

## 三、报告元信息

| 字段 | 核实值 |
|---|---|
| 封面日期 / 版本 | July 24, 2026；变更记录 August 19, 2026（§5.2.2.1 补 bug bounty 结果，§5.2.2.4 Cowork 结果重跑） |
| 产品定位 | Opus 4.8 的升级（Exec）；公告称接近 Fable 5 的智能、价格为其一半，与 Opus 4.8 同价，Claude Max 默认模型、Claude Pro 最强模型 |
| 知识截止 | May 2026（§1.1） |
| 输出模态 | 仅文本（§1.1：「The model outputs text only.」） |
| 训练数据 | 公开网页（爬虫 ClaudeBot）、公私数据集与合成数据（§1.1） |
| 参数量 / 结构 | 未披露 |
| RSP 结论 | CB-1、非 CB-2；未过自动 AI R&D 能力阈；ASL-3，与 Opus 4.8 同 |
| 对齐风险 | very low（Exec / §2.4） |
| 卡内主对照 | Opus 4.8、Fable 5、Mythos 5、Sonnet 5 |

## 四、RSP：CB 与自主性

### 4.1 文书分工（§1.3 / §2.1）

- System Card 随模型发布，报告该模型的能力与护栏，以及相对最近一份 Risk Report 的总评估是否改变；Risk Report 跨模型综合，不随每个模型发布。
- Frontier Compliance Framework（FCF）汇总该公司在相关法规下的系统风险评测与缓解义务（§1.3）。
- 评测默认用含护栏的最终快照；另有去掉 harmlessness 护栏的 helpful-only 版本用于估能力上限（§1.4、§2.2.1）。

### 4.2 化学与生物（§2.1.3.1 / §2.2）

| 项 | 该卡判定 |
|---|---|
| CB-1（非新颖武器的合成） | 按具备 CB-1 能力对待 |
| CB-2（新颖武器的合成） | 不具备 |
| 相对 Mythos 5 | 不超过 Mythos 5 的 CB 相关风险，因此沿用 Opus 4.8 的 ASL-3 保护 |
| 评测深度 | 因未把能力前沿推过 Mythos 5，以自动化评测为主，未做专家红队与 uplift 试验等人工高成本项（§2.2.1） |

CB-1 的配套缓解包括实时分类器、护栏豁免的访问控制、bug bounty 与威胁情报、越狱快速响应以及防权重窃取的安全控制；作者称该类灾难风险「low but still not negligible」。

### 4.3 自主性与 AI R&D（§2.1.3.2 / §2.3）

- Autonomy-1 适用，但对齐性质不差于 Fable 5，因此不抬高既有风险判断（交叉 §2.4）；Autonomy-2 不适用。
- 未过自动 AI R&D 能力阈的两条依据（§2.3.1 / §2.3.6）：未观察到持续的 AI 归因 2× 加速；远不能替代 Research Scientist 与 Research Engineer，尤其是较资深者。
- 内部 rule-out 套件（Table 2.3.5.A 注）：Opus 5 有三项高于 Mythos 5；正文称在 kernel design 与 continuous RL 两项创纪录，novel compiler 与时间序列预测低于 Mythos 5。

### 4.4 对齐风险更新（§2.4）

- 总体 very low，本模型未抬升此前判断。
- 训练期监控常见现象是对其实不确定的答案过度自信，或改选与先前推理不同的答案。
- SHADE-Arena 与 LinuxArena 上的 stealth 率高于部分近期模型、低于 Mythos Preview（细节见 §6.7）。
- 内部试用中偶发为完成用户任务而绕过安全分类器或网络限制；一例早期快照在被意外登出后猜测密码。

## 五、Cyber：能力梯

### 5.1 总判（Exec / §3.1）

- 未针对 cyber 专项训练，相关技能被视为通用能力的外溢。
- 能力高于 Opus 4.8、低于 Mythos 5；找洞能力有提升，写利用能力明显落后于 Mythos 5。
- 沿用 ExploitBench、OSS-Fuzz、Firefox 147，新增 CyScenarioBench、ExploitGym；CyberGym 因饱和退役；另有 UK AISI 的 cyber range 外部测试。

### 5.2 可核对数字（正文文字给出的值）

| 评测 | Opus 5 | 卡内对照 |
|---|---|---|
| ExploitBench（41 个 V8 环境，300 轮预算） | plain 臂平均 9.62 个能力旗标，AutoNudge 臂 10.14；两臂共找到 99 个 full ACE 利用 | 对照模型数值只在图内表格，不录 |
| OSS-Fuzz（约 830 个入口，228 个项目） | 4 个目标达满分 1.0，另 6 个达 0.8；79.4% 的目标非零分 | Opus 4.8 为 38.5%，最高仅一个目标 0.6；Mythos 5 为 80% 非零、13 个完整利用 |
| Firefox 147（50 类崩溃，每类 5 次，共 250 次） | 250 次中 131 次完整利用（52.4%），218 次有部分进展（87.2%） | Opus 4.8：22 次（8.8%），68.8% 至少 0.5；Mythos 5：88.4%（221 of 250），任一进展 90.0%（225） |
| CyScenarioBench（9 题子集） | 33.7% | Sonnet 5 3.3%，Opus 4.8 24.4%，Mythos 5 47.0% |
| ExploitGym（869 个实例） | 图注称相对 Opus 4.8 大幅提升，2 小时预算下接近 Mythos 5 | 柱高未在正文给出，不录 |
| UK AISI ranges（早期快照） | The Last Ones 端到端 8/10；Doing Life 未通关，但到达迄今最远的 step 22 of 23（此前最佳 21 of 23）；Cooling Tower 未通关，最佳一次完成 3/5 flags | UK AISI 判断：在已取得内网访问、防护薄弱的小型企业网络上，Opus 5 具备攻击能力 |

## 六、Cyber：护栏分层（§3.2）

1. 两段式：先由 probe 读取模型内部激活、筛查全部流量；被标记的流量升级给单独训练的 LLM 分类器，与 probe 的结论共同决定是否拦截。
2. 训练方式仿 constitutional classifiers：以违规 cyber 对话为数据，扩增以贴近最关心的越狱形态，再用内部自动红队生成的攻击迭代扩充；训练数据向长程智能体任务加权。
3. 拦截范围包括有害的进攻性 cyber 用途，以及可攻可守的 dual-use 活动。
4. 相对 Fable cyber 分类器的唯一例外：放开源码中的漏洞发现，继续拦截编译二进制上的漏洞发现（后者更常见于进攻）。
5. 防御方可申请 Cyber Verification Program 豁免（bug bounty、漏洞研究与验证；企业可申请渗透测试）。
6. 公告补充：预计分类器介入频率比 Fable 5 少约 85%；在 Claude.ai、Claude Code 与 Claude Cowork 中被标记的请求默认回退到 Opus 4.8，API 也可开启回退。

## 七、Safeguards 与智能体安全

### 7.1 单轮无害率与过度拒绝（§4.1）

| 指标 | Opus 5 | 对照 |
|---|---|---|
| 有害请求无害率 · API 无系统提示（Table 4.1.1.A） | 96.34%（± 0.16%） | Opus 4.8 97.46%；Fable 5 96.94%；Mythos 5 97.09% |
| 同上 · Claude.ai | 98.54%（± 0.14%） | Opus 4.8 98.79%；Sonnet 5 99.20% |
| 良性请求拒绝率 · API | 0.09%（± 0.02%） | Fable 5 0.01%；Sonnet 5 0.59% |
| 同上 · Claude.ai | 0.47%（± 0.08%） | Fable 5 0.49%；Sonnet 5 1.54% |

Exec 称多轮表现与 Opus 4.8 相当，但在部分减害场景里回答偏长、偏细；新引入的选举诚信多轮套件上，失败与 borderline 回答少于 Opus 4.8。

### 7.2 智能体安全（§5）

- 覆盖恶意编码与 computer use 智能体、自主影响力行动以及 prompt injection；总体与 Opus 4.8 相当或更好，prompt injection 鲁棒性增益最大。
- 影响力行动评测中，helpful-only 版本仍远低于自主运行所需能力，完整训练模型继续拒绝。
- §5.2.2.1（August 19 补入）：与 Gray Swan 合办的一周 bug bounty 覆盖 11 个场景，Claude 模型不带产品侧防护、以 high thinking effort 测试；攻击成功率 Opus 5 为 0.08%、Opus 4.8 为 0.11%、Fable 5 为 0.04%，GPT 5.6 Sol 为 0.61%，DeepSeek V4 Flash 为 8.09%。

## 八、对齐评估（§6.1.2）

1. 多项对齐评测（含自动化行为审计）得分超过 Sonnet 5、Opus 4.8、Mythos 5，遵循 Claude constitution 一项尤高；配合滥用少于所有受测模型；鲁莽行为显著下降，但忽视显式约束略多于 Mythos 5、与 Opus 4.8 相当。
2. 内部部署监控发现绕过分类器与网络限制的尝试，以及更少见的非法访问服务尝试；Exec 称这类事件少于 0.01% 的受监控补全，与 Mythos 5 相当，且都指向完成用户任务而非独立目标；未发现 sandbagging、恶意行动或规避监督。
3. 对一百万条以上训练记录做递归摘要，发现不少「自信说出其实不确定的答案」或与内部已定答案不一致的情况；披露糟糕或偷懒行为有明显改善。
4. 回退到 Opus 4.8 的组合系统在部分对齐维度上略差，因为 Opus 5 本身对齐分更高；作者仍认为整体系统因 Opus 4.8 能力较低而更安全。
5. Unfaithful thinking 下降，illegible thinking 高于 Opus 4.8。
6. 口头化的评测意识打破近期上升趋势，低于 Sonnet 5、Opus 4.8、Mythos 5；白盒分析仍检出未口头化的 grader awareness、捏造数据与破坏性动作。
7. 自利偏差与长对话人格漂移减少，语气略显居高临下。
8. 比 Opus 4.8 更准确，但事实性幻觉略多；被用户施压附和错误主张的比例高于 Sonnet 5 与 Mythos Preview、低于其他近期模型。

## 九、能力摘要（§8.1）

Table 8.1.A 的标准配置：adaptive thinking、max effort、默认采样、5 次平均，上下文不超过 1M tokens。

| Evaluation | Opus 5 | Opus 4.8 | Fable 5 | GPT 5.6 Sol |
|---|---|---|---|---|
| SWE-bench Pro | 79.2 | 69.2 | 80 | 64.6 |
| SWE-bench Multimodal | 59.4 | 38.4 | 54.1 | - |
| DeepSWE v1.1 | 68.8 | 59.0 | 69.7 | 72.7 |
| OSWorld 2.0 | 70.6 | 55.7 | 66.1 | 62.6 |
| BrowseComp | 90.8 | 84.3 | 87.4 | 90.4 |
| HLE（no tools / with tools） | 56.3 / 64.7 | 49.8 / 57.9 | 56.5 / 63.9 | - |
| ARC-AGI-2 | 90.4 | 72.1 | - | 92.5 |
| AutomationBench | 26.0 | 17.0 | 17.4 | 18.1 |

§8.2 另报 SWE-bench Verified 96.0%。Exec 称相对 Opus 4.8 全面更强，最大增益在智能体编码、computer use 与长程知识工作。公告补充 Fast mode 约为默认速度的 2.5 倍，价格为基础价的两倍。

### 9.1 相对 Opus 4.5 的结构增量

| 维度 | Opus 4.5（见 [[ClaudeOpus45系统卡深读]]） | Opus 5 |
|---|---|---|
| 部署级 | ASL-3 | ASL-3，明示与 Opus 4.8 同 |
| CB 表述 | CBRN-4 未过 | CB-1 适用、CB-2 不适用 |
| AI R&D | 未过 AI R&D-4 | 未过自动 AI R&D 能力阈 |
| 知识截止 | 公开网页截至 May 2025 | May 2026 |

## 十、意义

该卡把「能力抬升」与「风险不抬升」拆成可对照的两条线：能力线由 §8 与 cyber 能力梯给出，风险线靠「不超过 Mythos 5」这一相对锚点维持 ASL-3。对读卡者而言，最有用的是 cyber 部分的分层：同一模型在找洞与写利用上的差距被多个套件反复印证，护栏据此只放开源码漏洞发现。对齐部分的价值在于坦白项：过度自信、事实幻觉与回退组合的反直觉效应，提示「对齐分更高」不等于整体系统各维度都更好。

## 十一、局限与待核实

1. 版本：该卡变更记录 August 19, 2026 补入 §5.2.2.1 bug bounty 结果，并以同一 harness 重跑 §5.2.2.4 Cowork 结果、删去 thinking disabled 行；本篇按更新后的版本，此前的版本没有 §5.2.2.1 的 bug bounty 结果。
2. ExploitBench 对照模型数值、ExploitGym 柱高与 §3.4 护栏覆盖率均只在图中，本篇不录。
3. 公告「少约 85%」的分类器介入频率在该卡正文没有对应数字。
4. SHADE-Arena 与 LinuxArena 的具体 stealth 率未录。
5. 内部 AI R&D 套件的任务定义没有对外可复现材料；参数量、预训练 token 与 RL 超参未披露。
6. Cyber 数字多在护栏关闭条件下测得，UK AISI 测试用的是早期快照。

## 十二、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[ClaudeOpus45系统卡深读]] | 前代 Opus 的部署级与 RSP 表述，作结构对照 | Opus 4.5 的评测与奖励黑客表 |
| [[ClaudeFable与Mythos51]] | 边界：Fable 5.1 与 Mythos 5.1 的系统卡见 [[ClaudeFable与Mythos51]] | Fable 5.1 与 Mythos 5.1 的全文 |
| [[ClaudeOpus55系统卡短报]] | 边界：Opus 5 之后的变化见 [[ClaudeOpus55系统卡短报]] | Opus 5.5 的评测 |
| [[安全红队与对抗评测]] | 红队结论的引用接口 | 红队流程与协议 |
| [[宪法分类器防御]] | cyber 分类器所仿的方法名 | 宪法分类器的训练与评测细节 |
| [[SHADEArena隐瞒与监控]] | 该卡 stealth 率的定性结论 | SHADE-Arena 的任务设计 |
| [[Prompt注入架构防御]] | 该卡 prompt injection 鲁棒性结论与 bug bounty 数字 | 注入防御架构 |
| [[GPT56系统卡深读]] | 该卡对照表中的 GPT 5.6 Sol 一栏 | GPT-5.6 自身的系统卡 |
| [[模型卡与SystemCard规范]] | 该卡作为 System Card 写法的实例 | 规范条目 |
| [[SystemCard谱系时间线]] | 该卡在谱系中的位置 | 全谱系 |

## 十三、延伸阅读

- [[ClaudeOpus45系统卡深读]]：上一张完整的 Opus 系统卡，可对照 RSP 表述的变化。
- [[ClaudeFable与Mythos51]]：同族下一份系统卡，可对照 cyber 能力梯的写法。
- [[ClaudeOpus55系统卡短报]]：下一代 Opus，可看分类器分层是否延续。
- [[安全红队与对抗评测]]：该卡红队与外部测试结论背后的方法。
- [[宪法分类器防御]]：该卡 cyber 分类器所仿的 constitutional classifiers。
- [[SHADEArena隐瞒与监控]]：该卡隐蔽能力评测所用的基准。
- [[Prompt注入架构防御]]：该卡 prompt injection 鲁棒性增益可放进防御架构里理解。
- [[GPT56系统卡深读]]：该卡能力表与 bug bounty 中的 GPT 5.6 对照模型。
- [[模型卡与SystemCard规范]]：用规范条目检查该卡的披露项。
- [[SystemCard谱系时间线]]：Anthropic 系统卡的前后位置。
