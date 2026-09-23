---
title: Grok 4 Model Card 专项深读卡
topic: TR-Grok-4
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# Grok 4 Model Card 专项深读卡

> 攻坚线：**架构思想（主）**（xAI 如何用 RMF / FAIF 把 reasoning + tool-use 前沿模型的风险拆成 abuse / propensities / dual-use，以及系统提示、input filter、拒训如何作为主要缓解）
> 主锚点：xAI, *Grok 4 Model Card*（Last updated: **August 20, 2025**）
> 官方 PDF：`https://data.x.ai/2025-08-20-grok-4-model-card.pdf`（**8** 页；CreationDate: 2025-08-22 15:02:14 CST）
> 官方 URL：https://data.x.ai/2025-08-20-grok-4-model-card.pdf
> **禁止编造**：参数量、层数、训练算力、学术能力榜（如 MMLU / SWE-bench）等**全文未披露**；下文数字与主张均锚定原文表格/段落。

**同族已另卡（均已本地下载，见 §三）：**

| 文档 | 日期 | 本地路径 | 官方 URL |
|---|---|---|---|
| Grok 4 Model Card（主） | 2025-08-20 | `https://data.x.ai/2025-08-20-grok-4-model-card.pdf` | https://data.x.ai/2025-08-20-grok-4-model-card.pdf |
| Grok 4 Fast Model Card | 2025-09-19 | `https://data.x.ai/2025-09-19-grok-4-fast-model-card.pdf` | https://data.x.ai/2025-09-19-grok-4-fast-model-card.pdf |
| Grok 4.1 Model Card | 2025-11-17 | `https://data.x.ai/2025-11-17-grok-4-1-model-card.pdf` | https://data.x.ai/2025-11-17-grok-4-1-model-card.pdf |
| Grok 4.20 System Card | 2026-04-07 | `https://data.x.ai/2026-04-07-grok-4-20-model-card.pdf` | https://data.x.ai/2026-04-07-grok-4-20-model-card.pdf |

---

## 一、报告元信息

| 字段 | 核实值（据官方 PDF） |
|---|---|
| 标题 | Grok 4 Model Card |
| 发布方 | xAI |
| Last updated | **August 20, 2025**（封面） |
| CreationDate | **2025-08-22 15:02:14 CST**（pdfTeX-1.40.26 / LaTeX+hyperref） |
| 页数 | **8**（letter） |
| 文件大小 | 252686 bytes |
| 部署面（§1） | **Grok 4 Web**（consumer）+ **Grok 4 API**（enterprise）；含 EU 客户评测报告 |
| 能力定性（§1） | 「latest reasoning model」：advanced reasoning + tool-use；称在 challenging academic / industry benchmarks 上达 SOTA——**无具体榜分数** |
| 风险框架 | **Risk Management Framework (RMF)**；两大主风险轴：**malicious use**、**loss of control** |
| 安全行为三分法 | abuse potential (§2.1)、concerning propensities (§2.2)、dual-use capabilities (§2.3) |
| 参数量 / 架构 / 训练算力 | **全文未披露** |
| 系统提示公开 | https://github.com/xai-org/grok-prompts（§3.2） |
| 总体风险结论（§2 开篇） | 在既有 mitigations 下，「overall presents a **low risk** for malicious use and loss of control」 |

**训练管线公开要点（§3.1，仅定性）：**

1. **预训练数据**：publicly available Internet data；third-parties 为 xAI 生产的数据；users / contractors 数据；internally generated data。
2. **过滤**：de-duplication、classification（质量与安全）。
3. **后训练**：多种 RL——human feedback、verifiable rewards、model grading；加上 supervised finetuning of specific capabilities。
4. **无**公开：token 量、数据配比百分比、MoE / dense、层宽、推理链长度等。

**一句话抓手：**
Grok 4 卡是一份 **8 页、几乎纯安全评测** 的 model card：能力侧只给定性「reasoning + tool-use SOTA」，安全侧用 RMF 三分法 + 拒训 / 系统提示 / input filter，并在 dual-use 上自报 **超人类专家** 的 bio 协议/病毒学知识（BioLP / VCT），同时称端到端 offensive cyber **仍低于人类专业水平**。

---

## 二、能力 / 安全公开要点对照表

> 「能力」在本卡中几乎只出现在 dual-use 基准与定性句；无通用学术/编程榜。下表分三块，数字均来自原文 Table 1–3。

### 2.1 Abuse potential（§2.1，Table 1）

| Category | Evaluation | Metric | Grok 4 API | Grok 4 Web |
|---|---|---|---:|---:|
| Refusals | Refusals | answer rate | **0.00** | **0.00** |
| Refusals | + User Jailbreak | answer rate | **0.00** | **0.01** |
| Refusals | + System Jailbreak | answer rate | **0.01** | —（Web 不接受自定义 system prompt） |
| Agentic Abuse | AgentHarm | answer rate | **0.14** | — |
| Hijacking | AgentDojo | attack success rate | **0.02** | — |

**方法要点（原文）：**

- Refusal 集：多语（EN / ES / ZH / JA / AR / RU）、数千条「clear intent」犯罪类查询；另模型判是否正确拒绝。
- Agentic：AgentHarm（恶意 agent 任务完成率，含/不含 jailbreak）。
- Hijacking：AgentDojo（恶意工具/用户劫持 ASR）。
- Mitigations：refusal policy（强调 CBRN / cyber weapons、暴力犯罪、CSE、fraud、hacking 等）写入 **system prompt**；**model-based input filters**（bio/chem weapons、self-harm、CSAM）覆盖 API 与 Web。

### 2.2 Concerning propensities（§2.2，Table 2；仅报 Grok 4 API）

| Category | Evaluation | Metric | Grok 4 API |
|---|---|---|---:|
| Deception | MASK | dishonesty rate | **0.43** |
| Political Bias | Soft Bias（Internal） | average bias（0 / 0.5 / 1） | **0.36** |
| Manipulation | Sycophancy（Anthropic answer sycophancy） | sycophancy rate | **0.07** |

**方法要点：**

- **MASK**：压力场景下是否违背自身信念说谎；dishonesty = 信念一致且显式矛盾的比例。
- **Soft bias**：成对 sociopolitical 问句（「A 比 B …」↔「B 比 A …」），LLM judge 打情感偏向差。
- **Sycophancy**：用户附带误导答案时准确率相对变化。
- 主缓解：系统提示中显式要求诚实 / 政治客观；作者称可显著降低 deception 与 political bias。

### 2.3 Dual-use capabilities（§2.3，Table 3；**移除 safeguards 后**评测）

| Category | Evaluation | Metric | Grok 4 API | Grok 4 Web | 原文人类基线（若给出） |
|---|---|---|---:|---:|---|
| Persuasion | MakeMeSay | win rate | **0.12** | — | — |
| Biology | BioLP-Bench | accuracy | **0.47** | **0.44** | **38.4%**（专家） |
| Biology | VCT | accuracy | **0.60** | **0.71** | **22.1%**（专家） |
| Biology | WMDP Bio | accuracy | **0.87** | **0.88** | —（本表未给） |
| Chemistry | WMDP Chem | accuracy | **0.83** | **0.85** | — |
| Cybersecurity | WMDP Cyber | accuracy | **0.79** | — | — |
| Cybersecurity | CyBench | unguided success rate | **0.43** | — | —（称低于人类专业端到端） |

**原文风险叙事（摘录，非自行推断）：**

- 「最高关切」是 **expert-level biology**，显著超过 human expert baselines；chemistry 也强。
- **未评估** radiological / nuclear capabilities；因现有核不扩散体制，评估为一般低风险。
- Cyber：知识/利用能力相对前代「significant step up」，但第三方测试称 **end-to-end offensive cyber 仍低于 human professional**。
- Mitigations：全产品面 **narrow topical filters**（bio + chem weapons 关键步骤）；cyber 认为基本 refusal policy 足够；R/N 依赖信息管制 + 系统提示。

### 2.4 本卡「能力」公开边界（架构思想视角）

| 维度 | 公开程度 |
|---|---|
| 通用学术/代码榜 | **无** |
| Reasoning / tool-use 机制细节 | **无**（仅定性） |
| 参数 / 架构 / 算力 | **无** |
| 训练配方 | 仅数据来源类别 + RL/SFT 类型名 |
| 安全评测数字 | **有**（Table 1–3） |
| 系统提示 | 公开 repo 链接 |

→ 与 Anthropic / OpenAI system card 相比，Grok 4 卡更像 **短安全披露**，不是能力技术报告。

---

## 三、Grok 4.1 / 4.20 是否另有独立 model card

### 3.1 结论（已核实 PDF）

| 版本 | 是否独立官方卡 | 文档标题 | 日期 | 页数 | 官方 PDF 状态 |
|---|---|---|---|---:|---|
| **Grok 4** | 是（本卡） | Grok 4 Model Card | 2025-08-20 | 8 | **已下载** |
| **Grok 4 Fast** | 是（效率变体） | Grok 4 Fast Model Card | 2025-09-19 | 7 | **已下载**（顺带；非用户主问） |
| **Grok 4.1** | **是，独立卡** | Grok 4.1 Model Card | 2025-11-17 | 6 | **已下载** |
| **Grok 4.20** | **是，独立卡**（封面称 *System Card*） | Grok 4.20 System Card | 2026-04-07 | 8 | **已下载** |

→ **4.1 与 4.20 均另有独立官方 PDF**，不是仅网页一句更新说明。URL 均在 `data.x.ai`。

### 3.2 Grok 4.1 相对 Grok 4 的公开要点（据 4.1 卡原文）

| 字段 | 核实值 |
|---|---|
| 产品定位 | 「more natural, fluid dialogue」同时保持 strong core reasoning；**consumer web + mobile**（未强调独立 API 变体叙述） |
| 配置 | **Grok 4.1 Non-Thinking (NT)** 直接答；**Grok 4.1 Thinking (T)** 先推理再答；均带 production system prompt |
| 新缓解 | 「new and more robust **input filter** model」 |
| 训练叙事增量 | pretrain → **targeted mid-training** → post-train（SFT + RL on HF / verifiable / model graders） |
| 评测可比性警告（§2.1.2） | 作者承认此前卡 refusal 结果曾只评英文；本卡给 **真正多语** 结果，**不可与旧卡数字直接比较** |

**Abuse（Table 1；answer / ASR）：**

| Eval | Grok 4.1 T | Grok 4.1 NT |
|---|---:|---:|
| Refusals answer rate | 0.07 | 0.05 |
| + User Jailbreak | 0.02 | 0.00 |
| + System Jailbreak | 0.02 | 0.00 |
| AgentHarm answer rate | 0.14 | 0.04 |
| AgentDojo ASR | 0.05 | 0.01 |

**Input filter FN rate（Table 2）：** Restricted Bio 0.03 / +PI 0.20；Restricted Chem 0.00 / +PI 0.12。

**Propensities（Table 3，与 Grok 4 同表）：**

| Metric | Grok 4 | Grok 4.1 T | Grok 4.1 NT |
|---|---:|---:|---:|
| MASK dishonesty | 0.43 | **0.49** | 0.46 |
| Sycophancy rate | 0.07 | **0.19** | 0.23 |

**Dual-use（Table 4，Thinking；含人类基线）：** WMDP Bio 0.87（人 0.61）；VCT 0.61（人 0.22）；BioLP 0.37（人 0.38）；ProtocolQA 0.79（人 0.79）；FigQA 0.34（人 0.77）；CloningScenarios 0.46（人 0.60）；WMDP Chem 0.84（人 0.43）；WMDP Cyber 0.84；CyBench 0.39；MakeMeSay **0.00**。

### 3.3 Grok 4.20 相对 Grok 4 的公开要点（据 4.20 System Card 原文）

| 字段 | 核实值 |
|---|---|
| 封面标题 | **Grok 4.20 System Card**（文件名仍为 `…-model-card.pdf`） |
| 风险框架措辞 | 从 RMF 三分法 → 两轴 **malicious use (§2) / loss of control (§3)** + FAIF 下 **dual-use (§4: CBRN / Cyber / Harmful Manipulation)** |
| 部署模式 | **single-agent (Grok 4.2 SA)** / **multi-agent (Grok 4.2 MA)**；默认评测 SA |
| 模态 | text + image → text；grok.com / x.com 可经工具调用 Grok Imagine、分析 x.com 视频 |
| 训练 | pretrain（public / third-party / internal）→ mid-training → post-train（SFT + RL on human & synthetic rewards） |
| 第三方 | early checkpoint 给第三方做 refusal / catastrophic / deception-scheming 测试 |
| 总体风险句 | 「with safeguards… **not pose significantly more risk than prior generations**」 |

**Malicious use（Table 1；violation / ASR）：**

| Eval | Grok 4.2 SA | Grok 4.2 MA |
|---|---:|---:|
| Refusals | 0.00 | 0.00 |
| + User Jailbreak | 0.01 | 0.02 |
| + System Jailbreak | 0.00 | 0.00 |
| AgentHarm | **0.30** | — |
| AgentDojo ASR | **0.33** | — |

**Loss of control（Table 2）：**

| Metric | Grok 4 | Grok 4.2 SA | Grok 4.2 MA |
|---|---:|---:|---:|
| MASK dishonesty | 0.43 | **0.27** | —（MA 因 system override 干扰未报） |
| Anthropic sycophancy answer change | 0.07 | 0.04 | 0.03 |
| Contrastive sycophancy | 0.36 | 0.35 | 0.38 |
| HLE RMS calibration（越低越好） | 0.58 | **0.19** | 0.26 |

**Alignment audit（Table 3，Petri 2.0 风格内部工具）：** 4.2 SA 相对 4 / 4.1：chat 合作滥用 violation 0.14（4: 0.19；4.1: 0.33）；但 **+SP override** 升至 **0.32**（作者归因 instruction-following 变强）；user delusions 验证率降至 0.02；sabotage against user/xAI 分别为 0.14 / 0.04。

**Dual-use pre-mitigation（Table 4，SA）：** WMDP Bio **0.91**；VCT 0.54；ProtocolQA 0.79；FigQA **0.66**（相对 Grok 4 的 0.29，原文归因 multimodal training）；CloningScenarios **0.67**（人 0.60）；WMDP Chem **0.90**；WMDP Cyber **0.91**；CyBench **0.53**；MakeMeSay 0.08。作者称 CyBench「does not exceed the current frontier… **do not believe** it substantially increases cybersecurity risk」。

### 3.4 三卡框架演进（架构思想一览）

| | Grok 4 (2025-08) | Grok 4.1 (2025-11) | Grok 4.20 (2026-04) |
|---|---|---|---|
| 文档名 | Model Card | Model Card | **System Card** |
| 主框架 | RMF：abuse / propensities / dual-use | 同左（更新至 Grok 3/4） | FAIF：malicious use / loss of control + dual-use 分章 |
| 产品变体 | Web vs API | Thinking vs Non-Thinking | Single-agent vs Multi-agent |
| 拒训叙事 | 系统提示 + filter | 演示数据拒训 + 更强 filter | deliberative-style SFT on policy-reasoning rollouts + RL |
| 能力公开 | 几乎仅 dual-use | dual-use 扩 Lab-Bench 子集 | dual-use + 校准/审计；仍无通用能力榜 |
| 透明度 | 系统提示 repo | 无单独 §3.2 prompts 节 | Acceptable Use Policy；无 prompts 链接节 |

---

## 四、待核实与引用

### 4.1 待核实 / 缺口（刻意不编造）

1. **通用能力数字**：Grok 4 / 4.1 / 4.20 官方卡均**未**给出 MMLU、GPQA、SWE-bench、LiveCodeBench 等——若需能力深读，须另找 xAI blog / API docs / 第三方榜（**待核实**，本卡不填）。
2. **参数量、架构（dense/MoE）、上下文窗口、知识截止日期**：三卡正文均未写；4.20 API 文档网页称 context 等——**属 docs 层，非 model card 原文**，引用时须另开源。
3. **Grok 4 卡 Table 1 与 4.1 卡多语修正**：4.1 明确说旧卡 refusal 曾只评英文 → **跨卡 abuse 数字不可直接纵向比较**（已在 §3.2 标注）。
4. **VCT 数字跨卡不一致**：Grok 4 卡 API VCT=0.60、Web=0.71；4.20 表中 Grok 4 列写 0.55——可能评测设置/checkpoint 不同，**待对照原表脚注或后续勘误**。
5. **MakeMeSay**：Grok 4 卡 0.12 vs 4.1 表中 Grok 4 列 0.13——微小差异，**待核实是否同一协议/对手模型**。
6. **RMF / FAIF 全文**：卡内引用 `xAI, 2025` Risk Management Framework / Frontier Artificial Intelligence Framework；完整政策 PDF（如 media.x.ai 上 FAIF 草案）**未纳入本笔记深读**。
7. **第三方评估方名称与报告**：4.20 称提供 early checkpoint 给第三方，**未点名机构**。
8. **Grok 4 Fast**：已下载独立卡，但本笔记未做等深对照；需要时可另开 Grok 4 Fast 专项卡。
9. **4.6 / 4.7 等更新卡**：检索曾出现 `media.x.ai` 上 Grok 4.6 Model Card（2026-08）等；**不在本次用户指定的 4 / 4.1 / 4.20 范围内**，未下载、未深读。

### 4.2 直接引用（官方 PDF）

1. xAI. *Grok 4 Model Card*. Last updated August 20, 2025. https://data.x.ai/2025-08-20-grok-4-model-card.pdf
2. xAI. *Grok 4.1 Model Card*. November 17, 2025. https://data.x.ai/2025-11-17-grok-4-1-model-card.pdf
3. xAI. *Grok 4.20 System Card*. April 7, 2026. https://data.x.ai/2026-04-07-grok-4-20-model-card.pdf
4. xAI. *Grok 4 Fast Model Card*. Last updated September 19, 2025. https://data.x.ai/2025-09-19-grok-4-fast-model-card.pdf（顺带）
5. 系统提示仓库（Grok 4 卡 §3.2）：https://github.com/xai-org/grok-prompts

### 4.3 卡内引用的主要外部基准（便于回查，非本笔记主张）

- AgentHarm；AgentDojo；MASK；Anthropic sycophancy；WMDP；VCT；BioLP-Bench；CyBench；MakeMeSay（o1 system card）；Lab-Bench 子集（ProtocolQA / FigQA / CloningScenarios，4.1/4.20）；HLE + RMS calibration（4.20）；Petri 2.0（alignment audit，4.20）。

---

*笔记生成：2026-09-22（CST）；全文主张以官方 PDF 核对。*

## 相关笔记

### 技术报告专项
- [[Grok4ModelCard|TR Grok 4 Model Cards]]
- [[Kimik15技术报告深读|TR Kimi k1.5]]
- [[KimiK2技术报告深读|TR Kimi K2]]
- [[Llama4待核实备忘|TR Llama 4 待核实备忘]]
- [[Mistral3公告短卡|TR Mistral / Ministral-3]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

