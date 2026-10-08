---
title: Grok 4 Model Card 专项深读卡
topic: Grok4模型卡深读
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://x.ai/news/grok-4
 - https://x.ai/news/grok-4-1
 - https://docs.x.ai/developers/models # 仅用于核对型号名 grok-4.20
related: ["模型卡与SystemCard规范", "SystemCard谱系时间线", "审慎对齐与断路器", "Prompt注入架构防御", "安全红队与对抗评测", "LLaMA开源生态里程碑", "MistralLarge4短报"]
archived: 2026-09-22
---

# Grok 4 Model Card 专项深读卡

> **主要来源**：[Grok 4 Model Card](https://x.ai/news/grok-4)（xAI，Last updated: August 20, 2025，仅有 PDF 版，此处挂官方 Grok 4 发布页，以下简称该卡）；[Grok 4.1 Model Card](https://x.ai/news/grok-4-1)（xAI，November 17, 2025，仅有 PDF 版，此处挂官方 Grok 4.1 发布页）；Grok 4.20 System Card（xAI，April 7, 2026，仅有 PDF 版，无官方落地页）；[Grok Models & Pricing](https://docs.x.ai/developers/models)（xAI 开发者文档，仅用于核对型号名 grok-4.20）（截至 2026-04-07）。
> **研究线**：架构思想（xAI 如何用风险框架把推理加工具调用模型的风险拆成滥用、倾向与双用途能力，以及系统提示、输入过滤与拒绝训练如何充当主要缓解）
> **范围与相邻笔记**：
> - ≠ [[模型卡与SystemCard规范]]：RMF、FAIF 与 Preparedness、RSP、FSF 的框架对照在那篇，本篇只记 xAI 三张卡的结构与数字。
> - ≠ [[审慎对齐与断路器]]：「让模型对着政策推理再拒绝」的方法在那篇，本篇只记 xAI 的用法。
> - 参数量、层数、训练算力与通用能力榜三张卡均未披露，本篇不补。
>
> **意义**：Grok 4 卡是一份八页、几乎只讲安全评测的模型卡：能力只有一句定性的「state-of-the-art」，安全侧按 RMF 把行为分为滥用潜力、可疑倾向与双用途能力三类，主要缓解是写进系统提示的拒绝政策和基于模型的输入过滤；双用途部分自报生物协议与病毒学知识超过人类专家基线，同时称端到端进攻性 cyber 仍低于人类专业水平。到 4.1 与 4.20，xAI 承认旧卡的拒绝评测只跑了英文；4.20 卡 §1 不再提 RMF，改称按 FAIF 做双用途能力评估，章节改为恶意使用、失控、双用途三章（恶意使用与失控两类风险在 Grok 4 卡 §1 的 RMF 里已有）；拒绝训练改为在推理政策的 rollout 上做 SFT，但通用能力榜始终没有进入卡内。

## 一、问题背景

该卡 §1 称 Grok 4 是 xAI 最新的推理模型，具备高级推理与工具调用能力，在学术与业界基准上达到 state-of-the-art，但不给任何榜分。按 xAI 的 Risk Management Framework（RMF），风险分为 malicious use 与 loss of control 两类，评测对象是三类安全相关行为：abuse potential（§2.1）、concerning propensities（§2.2）、dual-use capabilities（§2.3）。部署面为面向消费者的 Grok 4 Web 与面向企业的 Grok 4 API，含 EU 客户。作者的总判是在现有缓解下，Grok 4「overall presents a low risk」。

训练管线（§3.1）只有定性描述：预训练数据来自公开互联网、第三方为 xAI 生产的数据、用户与承包商数据和内部生成数据，经去重与质量、安全分类；后训练用基于人类反馈、可验证奖励与模型评分的强化学习，加特定能力的监督微调。§3.2 公开了消费产品的系统提示（[xai-org/grok-prompts README](https://github.com/xai-org/grok-prompts)）。

## 二、脉络

| 时间 | 文档 | 变化 |
|---|---|---|
| 2025-07 | Grok 4 发布 | 发布页只讲能力，不附模型卡 |
| 2025-08-20 | Grok 4 Model Card | RMF 三分法；Web 与 API 两种部署 |
| 2025-09-19 | Grok 4 Fast Model Card | 效率变体，本篇不展开 |
| 2025-11-17 | Grok 4.1 Model Card | Thinking 与 Non-Thinking 两种配置；更新输入过滤；更正旧卡只评英文的问题 |
| 2026-04-07 | Grok 4.20 System Card | 改称 System Card；单智能体与多智能体两种模式；FAIF 下按恶意使用、失控与双用途分章 |

## 三、Grok 4 卡的三类评测

### 3.1 滥用潜力（§2.1，Table 1）

| Evaluation | Metric | Grok 4 API | Grok 4 Web |
|---|---|---|---|
| Refusals | answer rate | 0.00 | 0.00 |
| + User Jailbreak | answer rate | 0.00 | 0.01 |
| + System Jailbreak | answer rate | 0.01 | –（Web 不接受用户自定义系统提示） |
| AgentHarm | answer rate | 0.14 | – |
| AgentDojo | attack success rate | 0.02 | – |

拒绝政策重点覆盖 CBRN 与网络武器、暴力犯罪、儿童性剥削、欺诈与黑客等，写进系统提示；作者称政策放进系统提示后，模型会显式对照政策推理，既能拒掉更多有害请求，也只拒绝带明确伤害意图的请求。另有基于模型的输入过滤（生化武器、自伤、CSAM），覆盖 API 与 Web。

### 3.2 可疑倾向（§2.2，Table 2，只报 API）

| Evaluation | Metric | Grok 4 API |
|---|---|---|
| MASK | dishonesty rate | 0.43 |
| Soft Bias（Internal） | average bias | 0.36 |
| Sycophancy | sycophancy rate | 0.07 |

主要缓解同样是系统提示：显式要求诚实与政治客观；作者称这类提示也能防止过度谄媚。

### 3.3 双用途能力（§2.3，Table 3，去掉安全措施后评测）

| Category | Evaluation | Grok 4 API | Grok 4 Web |
|---|---|---|---|
| Persuasion | MakeMeSay | 0.12 | - |
| Biology | BioLP-Bench / VCT / WMDP Bio | 0.47 / 0.60 / 0.87 | 0.44 / 0.71 / 0.88 |
| Chemistry | WMDP Chem | 0.83 | 0.85 |
| Cybersecurity | WMDP Cyber / CyBench | 0.79 / 0.43 | - |

§2.3.2 给出人类专家基线：BioLP-Bench 38.4%、VCT 22.1%，据此称 API 与 Web 在生物协议纠错与湿实验病毒学上达到「superhuman performance」。作者把专家级生物能力列为最高关切；不评估放射与核能力，理由是现有防扩散体制下这类风险总体较低；cyber 知识与利用能力较前代明显提升，但第三方测试显示端到端进攻能力仍低于人类专业水平。缓解为全产品面的窄主题过滤（生化武器关键步骤）。

## 四、Grok 4.1 与 4.20 的增量

**Grok 4.1**（November 17, 2025）：

- 定位为「more natural, fluid dialogue」，分 Non-Thinking 与 Thinking 两种配置。
- 更正：多语拒绝数据集此前「only the English prompts were evaluated」，新卡改报真正的多语结果，「not directly comparable to previous results」。
- 输入过滤对受限生物知识的漏判率 0.03（加 prompt injection 后 0.20），受限化学为 0.00（加 prompt injection 后 0.12）。
- 倾向表中 MASK dishonesty 为 Grok 4 0.43、4.1 Thinking 0.49、4.1 Non-Thinking 0.46；sycophancy rate 依次为 0.07、0.19、0.23。

**Grok 4.20 System Card**（April 7, 2026）：

- 两种部署模式：single-agent（Grok 4.2 SA）与 multi-agent（Grok 4.2 MA），默认按 SA 评测；总判为在安全措施下「not pose significantly more risk than prior generations of models」。
- 拒绝训练：在对拒绝政策进行推理的 rollout 上做监督微调，作者称「similar in spirit to Guan et al. [2024]」，之后在良性与有害请求上做强化学习以调整拒绝边界。
- 恶意使用（Table 1，SA）：Refusals violation rate 0.00；AgentHarm violation rate 0.30；AgentDojo attack success rate 0.33。
- 失控（Table 2）：MASK dishonesty Grok 4 0.43、4.2 SA 0.27；HLE RMS calibration 依次为 0.58、0.19（MA 0.26）。
- 双用途（Table 4）：FigQA 从 Grok 4 的 0.29 到 4.2 SA 的 0.66（人类基线 0.77），作者归因于 multimodal training；CyBench 0.53，作者称「does not exceed the current frontier of capabilities」，因此不认为显著增加 cyber 风险。

## 五、意义

三张卡构成一条清楚的演进线：文档名从 Model Card 改为 System Card，框架名从 RMF 改称 FAIF，章节改为按恶意使用、失控与双用途分章（恶意使用与失控两类风险在 Grok 4 卡里已有），部署变体从 Web 与 API 变成 Thinking 与 Non-Thinking、再到单智能体与多智能体。不变的是公开范围：参数、架构与通用能力榜始终缺席，卡内数字几乎全部是安全与双用途评测。对比读者而言，这组卡最有用的是两点：4.1 对旧卡多语评测错误的公开更正，提醒跨卡纵比前要先查评测设置；4.20 把「政策写进系统提示」升级为「对政策推理的 SFT」，作者称与 Guan et al. [2024] 的做法精神相近（similar in spirit）。

## 六、局限与待核实

1. 三张卡均未给 MMLU、GPQA、SWE-bench 等通用能力分，也未写参数量、架构、上下文窗口与知识截止；这些只能另查 xAI 发布页或 API 文档，并单独注明出处。
2. 4.1 卡更正旧卡拒绝评测只跑英文，因此 Grok 4 卡 Table 1 的拒绝数字不能与后续卡纵向比较。
3. 跨卡数字不一致：Grok 4 卡 VCT 为 API 0.60、Web 0.71，4.20 卡 Table 4 的 Grok 4 列写 0.55；MakeMeSay 在 Grok 4 卡为 0.12，4.20 卡 Grok 4 列为 0.13；原因未说明。
4. 4.20 卡内自相矛盾：Table 4 中 CloningScenarios 为 4.2 SA 0.67、人类基线 0.60，正文却说在 FigQA 与 CloningScenarios 上「performs worse than human baselines」。
5. RMF 与 FAIF 的政策全文未读；4.20 称把早期 checkpoint 交给第三方测试，但未点名机构。
6. Grok 4 卡与 4.20 卡在官方站点没有链接到卡的落地页：Grok 4 卡挂 Grok 4 发布页，4.20 卡不挂链接；另挂的 xAI 开发者文档模型页仅用于核对型号名 grok-4.20，不引其中事实；Grok 4 Fast 卡未做等深对照。
7. 4.20 卡正文称 FAIF，但其引注 [xAI, 2025] 在参考文献中的条目标题仍为「xai risk management framework, 2025」，卡内未说明二者是否为同一文件改名。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[模型卡与SystemCard规范]] | RMF / FAIF 在各家框架中的位置 | 框架定义与跨厂对照 |
| [[SystemCard谱系时间线]] | xAI 三张卡在谱系中的顺序 | 全谱系 |
| [[审慎对齐与断路器]] | 4.20 拒绝训练所参照的方法名 | Deliberative Alignment 的方法细节 |
| [[Prompt注入架构防御]] | AgentDojo 劫持率作为该卡的注入指标 | 注入防御架构 |
| [[安全红队与对抗评测]] | 越狱与红队类评测的接口 | 红队流程与协议 |
| [[LLaMA开源生态里程碑]] | 开放权重一侧的文档形态对照 | Llama 的技术细节 |
| [[MistralLarge4短报]] | 开放权重一侧的另一文档形态对照 | Mistral 的技术细节 |

## 八、延伸阅读

- [[模型卡与SystemCard规范]]：把 RMF / FAIF 放回与 Preparedness、RSP、FSF 的对照中看。
- [[SystemCard谱系时间线]]：xAI 三张卡与他家系统卡的时间顺序。
- [[审慎对齐与断路器]]：4.20 拒绝训练所参照的 Guan et al. 方法。
- [[Prompt注入架构防御]]：该卡 AgentDojo 指标背后的注入防御思路。
- [[安全红队与对抗评测]]：该卡越狱评测所属的红队方法体系。
- [[LLaMA开源生态里程碑]]：开放权重一侧的文档形态对照，可与 xAI 三张卡的公开范围对看。
- [[MistralLarge4短报]]：开放权重一侧的另一文档形态对照。
