---
title: Gemini 3.7 Flash Model Card 深读
topic: Gemini37Flash模型卡深读
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://deepmind.google/models/model-cards/gemini-3-7-flash/
related: ["Gemini3Pro模型卡深读", "Gemini25技术报告深读", "Gemini4Argon短报", "模型卡与SystemCard规范", "开源与闭源前沿模型谱系", "推理时扩展TestTimeScaling", "多模态架构脉络", "SystemCard谱系时间线"]
archived: 2026-09-22
---

# Gemini 3.7 Flash Model Card 深读

> **主要来源**：[Gemini 3.7 Flash — Model Card](https://deepmind.google/models/model-cards/gemini-3-7-flash/)（Google DeepMind，2026-08-13 发布，PDF 版 9 页）（截至 2026-09-30）。
> **研究线**：架构思想（产品字段与 Frontier Safety 字段）
> **范围与相邻笔记**：
> - ≠ [[Gemini3Pro模型卡深读]]：本篇不写 3 Pro 的架构口号、数据类别与 Frontier Safety 第 9–10 页表，只列 3.7 Flash 相对它的字段差。
> - ≠ [[Gemini25技术报告深读]]：本篇不写 2.5 的架构、Infra 与 Thinking budget 机制。
> - ≠ [[模型卡与SystemCard规范]]：Frontier Safety Framework 作为治理框架与 Preparedness、RSP 的对照放在该篇，本篇只记该卡的档位结论。
>
> **意义**：这是一张「增量卡」的典型：架构、数据、硬件、软件、用途政策全部指回库内未收的 3.6 Flash 卡，本身只报能力与安全的变化量。它的信息量集中在两处：编码与智能体基准相对 3.6 的大幅提升，以及 Frontier Safety 换到 2026 年 4 月版框架后相对 3 Pro 卡新增 TCL 档，CBRN、Cyber 双双触及 alert 阈值。

**一句话**：Gemini 3.7 Flash 基于 3.6 Flash，主打核心推理算法改进、agentic 视频理解与可配置 thinking；输入 1M、输出 64K，知识截止名义上为 2026 年 3 月；相对 3.6，DeepSWE +16.7 pp、OSWorld-2.0 +14.1 pp、AutomationBench +13.4 pp，CharXiv 两项各降 0.7 pp；安全自动评测与 3.6 相近，Frontier Safety 各域均未达 TCL / CCL，但 CBRN 与 Cyber 触及 alert 阈值。

---

## 一、问题背景

Gemini 的 Flash 线定位于成本与延迟优先的主力型号。2.5 代起 Google 用技术报告讲架构与 Infra（[[Gemini25技术报告深读]]），3 代改为十页左右的模型卡加外链评测方法文档（[[Gemini3Pro模型卡深读]]）。到 3.x 的 Flash 迭代，模型卡进一步缩成「只报变化量」：凡与前代相同的字段一律写「see Gemini 3.6 Flash model card」。

读这类卡的难点在于基线：该卡能力表、安全表的对照对象是 3.6 Flash，而库内没有 3.6 Flash 卡的笔记；tone 一项的对照基准又写的是 Gemini 3 Flash。所以本篇只记卡内可核对的增量，不把 3 Pro 或 2.5 的架构数字外推到 3.7。

## 二、脉络

| 时间 | 节点 | 与该卡的关系 | 出处 |
|---|---|---|---|
| 2025-07 | Gemini 2.5 技术报告 | 稀疏 MoE + 原生多模态 + 可控 thinking budget；输入 1M、输出 64K | [[Gemini25技术报告深读]] |
| 2025-11 | Gemini 3 Pro 模型卡（2026-05 更新） | 3 代旗舰；FSF 2025 年 9 月版，主表以 CCL 为主 | [[Gemini3Pro模型卡深读]] |
| 2026（未收） | Gemini 3.6 Flash 模型卡 | 该卡的直接依赖；架构、数据、政策均指向它 | 该卡 |
| 2026-08-13 | Gemini 3.7 Flash 模型卡 | 该卡；FSF 2026 年 4 月版 | 该卡 |
| 2026-09-30 | Gemini 4 Argon | Gemini 4 代旗舰，输出上限由 3.x 的 64K 升到 1M | [[Gemini4Argon短报]] |

## 三、产品字段

| 字段 | 3.7 Flash | 相对 3 Pro 卡 |
|---|---|---|
| 定位 | Gemini 3 族下一迭代；核心推理算法改进、agentic 视频理解；可配置 thinking 以调质量、成本与延迟 | 3 Pro 写「not a fine-tune of a prior model」；3.7 Flash 明写基于 3.6 Flash |
| 输入 / 输出 | 文本、图像、音频、视频；1M / 64K | 同级 |
| 知识截止 | 2026 年 3 月；部分领域可能仍停在 2025 年 1 月 | 3 Pro 为 2025 年 1 月 |
| 分发渠道 | Gemini App（HTML 卡页作 Gemini App - Spark）、Gemini Enterprise App、Gemini Enterprise Agent Platform、AI Studio、Gemini API、AI Mode（仅 PDF 版列出）、Antigravity | 新增两个 Enterprise 渠道；未列 Vertex AI 与 NotebookLM |
| 适用场景 | agentic 工作流、复杂视频推理、编码、企业工作流 | — |
| 架构、数据、硬件、软件、用途政策 | 全部指回 3.6 Flash 卡 | 3 Pro 卡有稀疏 MoE 口号与数据类别 |

价格（引入价至 2026-12-31）：输入 $0.75、输出 $3.75 / 百万 token，与 3.6 Flash 相同；2027-01-01 起为 $1.50 / $7.50。

## 四、能力：相对 3.6 Flash

卡内能力表（Results as of August 2026）与 3 Pro 卡的榜单集合不同：该卡有 FrontierCode、DeepSWE、Terminal-bench 2.1 / 3.0、AutomationBench、LVBench、HLE-Verified 等，没有原版 HLE、SWE-bench Verified、AIME。下表只选能说明增量形态的行。

| 基准 | 3.7 Flash | 3.6 Flash | 变化 | 表内最优 |
|---|---:|---:|---:|---|
| DeepSWE v1.1 | 65.3% | 48.6% | +16.7 pp | GPT-5.6 Terra 69.6% |
| OSWorld-2.0 | 47.9% | 33.8% | +14.1 pp | GPT-5.6 Terra 50.2% |
| AutomationBench（私有集） | 30.4% | 17.0% | +13.4 pp | 该卡 |
| GDP.pdf | 34.0% | 22.0% | +12.0 pp | 该卡 |
| Terminal-bench 3.0 | 14.9% | 5.4% | +9.5 pp | GPT-5.6 Terra 20.8% |
| FrontierCode 1.1 Main | 43.6% | 34.4% | +9.2 pp | 该卡 |
| GDM-MRCR v2（8-needle，128k 平均） | 97.0% | 91.8% | +5.2 pp | 该卡 |
| HLE-Verified | 53.6% | 51.2% | +2.4 pp | 该卡 |
| LVBench | 85.4% | 84.2% | +1.2 pp | 该卡 |
| CharXiv Reasoning（无工具 / 有工具） | 84.5% / 88.7% | 85.2% / 89.4% | −0.7 / −0.7 pp | 无工具 GPT-5.6 Terra 85.9%；有工具 3.6 Flash |

增量集中在长程软件工程、终端与计算机使用智能体、企业自动化与 PDF 理解；图表推理略降。编码与智能体的几项仍落后表内的 GPT-5.6 Terra。与 3 Pro 不可直接纵比：HLE-Verified 是 1,811 题的核验子集，不是原版 HLE；GDM-MRCR v2 与 3 Pro 卡的 MRCR v2 名称与设定不同。

## 五、安全与 Frontier Safety

**自动安全评测（相对 3.6 Flash，绝对百分点）。** Text-to-Text Safety +1.17 pp（越低越好，略回退）、Multilingual Safety −0.48 pp（略改进）、Image-to-Text Safety 无变化、Tone −0.47 pp（越高越好，略回退）、Unjustified refusals +0.84 pp（略回退）。卡总判为与 3.6「performs similarly」，人工复核认为损失绝大多数是误报或不严重；并声明评测已改进，不可与此前 Gemini 模型卡直接比较。人类红队：儿童安全达到发布阈值；内容安全与 3.6 相近或更好；政策外议题对照 Gemini 3.1 Pro，未见严重问题。

**Frontier Safety（2026 年 4 月版框架）。** Google 的 Frontier Safety Framework 为每个风险域设关键能力档（CCL），并在 CCL 之下设 alert 阈值，用来提示模型可能正在接近该 CCL；该卡首次出现 TCL（tracked capability level）一列。框架本身见 [[模型卡与SystemCard规范]]。

| 风险域 | 档位 | 结论 |
|---|---|---|
| CBRN | Uplift TCL | 未达；理论能力高但缺可执行的专家深度 |
| CBRN | Uplift Level 1 CCL | 未达，但**已达 alert**：专家红队见相对网页基线的适度增益，部分专家能在两个测试场景中取得完整危害链的准确信息；因平均分适度且需专家明确引导，判为低于 CCL |
| Cybersecurity | Uplift Level 1 CCL | 未达，**已达 alert** |
| Harmful Manipulation | Level 1 CCL | 未达 alert；一对一对话中对信念与行为有一定影响 |
| ML R&D 与 Misalignment | Stealth and Situational Awareness TCL | 未达；隐蔽性与 3.1 Pro 相近，情境意识强于 3.1 Pro，能识别测试环境但无法绕过限制 |
| ML R&D | Acceleration / Automation Level 1 CCL | Acceleration 未达 alert；Automation 未达 CCL；能完成单个编码任务，不能独立串成端到端研究流程 |

该卡随发布更新了 CBRN 与 cyber offense 的滥用防护；细节在单独的 *Gemini 3.7 Frontier Safety Framework Report*。相对 3 Pro 卡的字段差：框架版本 2025 年 9 月 → 2026 年 4 月；新增 TCL 列；Misalignment 与 ML R&D 合并叙述，对照锚改为 3.1 Pro。

## 六、意义

3.7 Flash 卡说明，前沿厂商的 Flash 级型号也已进入「需按框架逐域报告危险能力」的阶段：一个价格为旗舰数分之一的型号同时在 CBRN 与 Cyber 触及 alert 阈值。另一方面，增量卡把架构与数据信息全部外包给前一张卡，单读该卡无法回答「改了什么结构」，只能回答「变好了多少、风险档在哪」。

## 七、局限与待核实

- Gemini 3.6 Flash 模型卡未收：该卡架构、数据、硬件、软件与政策全部指向它。
- *Gemini 3.7 Frontier Safety Framework Report* 未读，alert 判定的具体评测与分数不在本篇。
- 评测方法文档的链接最终指向 PDF，本篇不直链；卡内写的是 `deepmind.com` 域名，网页版为 `deepmind.google`。
- 「核心推理算法改进」「可配置 thinking」「agentic 视频理解」都只是口号，卡内没有机制、旋钮名或数值。
- Vertex AI 是否仍覆盖未写明；CharXiv 的 0.7 pp 回退是否在评测噪声内未知。
- 分发渠道 HTML 卡页与 PDF 版不一致：PDF 版列 7 项，含「Google AI Mode」；HTML 卡页列 6 项，没有 AI Mode，且把 Gemini App 写作「Gemini App - Spark」。
- Tone 一项的正向变化以 Gemini 3 Flash 为基准，与列标题「vs 3.6 Flash」并存，引用时需区分。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[Gemini3Pro模型卡深读]] | 3 代旗舰卡的字段作对照（知识截止、渠道、FSF 版本与 CCL 主表） | 3 Pro 的能力表与 Frontier Safety 表全文 |
| [[Gemini25技术报告深读]] | Flash 线可控 thinking 的来历；2.5 的 1M / 64K 窗口 | 2.5 的架构与 Infra |
| [[Gemini4Argon短报]] | 该卡之后的 Gemini 4 代旗舰，输出上限从 64K 升到 1M | Argon 的评测与放量 |
| [[模型卡与SystemCard规范]] | FSF 作为治理框架与他家框架的对照；该卡是「短卡 + 指回前代卡 + FSF 外链」的字段范例 | 框架定义全文 |
| [[开源与闭源前沿模型谱系]] | 谱系中 Google 一行的 3.x Flash 节点 | 谱系全表 |
| [[推理时扩展TestTimeScaling]] | 「可配置 thinking」是测试时算力的产品旋钮，该卡无 budget 曲线 | 测试时扩展机制 |
| [[多模态架构脉络]] | agentic 视频理解与 LVBench 作 Flash 线视频节点 | 视频 token 配方 |
| [[SystemCard谱系时间线]] | 该卡在各厂模型卡序列中的位置 | 各厂全表 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Gemini 3.7 Flash — Model Card](https://deepmind.google/models/model-cards/gemini-3-7-flash/) | 能力表、安全评测表与 Frontier Safety 表 |
| 2 | [[Gemini3Pro模型卡深读]] | 3 代旗舰卡的对照字段 |
| 3 | [[模型卡与SystemCard规范]] | FSF 与 Preparedness、RSP 的框架对照 |
