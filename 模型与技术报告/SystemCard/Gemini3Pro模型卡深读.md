---
title: Gemini 3 Pro Model Card 深读
topic: Gemini3Pro模型卡深读
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
sources:
 - https://deepmind.google/models/model-cards/
 - https://blog.google/products-and-platforms/products/gemini/gemini-3/
related: ["Gemini25技术报告深读", "Gemini37Flash模型卡深读", "模型卡与SystemCard规范", "推理时扩展TestTimeScaling", "开源与闭源前沿模型谱系", "AI基础设施总览", "SystemCard谱系时间线"]
archived: 2026-09-22
---

# Gemini 3 Pro Model Card 深读

> **主要来源**：[Gemini 3 Pro Model Card](https://deepmind.google/models/model-cards/)（Google DeepMind，Model Release: November 2025，Last Updated: May 2026，仅有 PDF 版，此处挂官方模型卡索引页，以下简称该卡）；[A new era of intelligence with Gemini 3](https://blog.google/products-and-platforms/products/gemini/gemini-3/)（Google 发布博文，2025-11-18，以下简称博文）（截至 2026-05）。
> **研究线**：架构思想（模型卡公开了哪些架构与数据字段）+ AI Infra（训练硬件与软件栈的公开程度）
> **范围与相邻笔记**：
> - ≠ [[Gemini25技术报告深读]]：2.5 的架构、Infra 与评测细节在那篇，本篇只写 3 Pro 相对它的字段变化。
> - ≠ [[Gemini37Flash模型卡深读]]：后续 Flash 增量卡在那篇，本篇不写。
> - ≠ [[模型卡与SystemCard规范]]：Frontier Safety Framework 作为治理框架的背景与他家框架对照在那篇，本篇只记该卡的档位结论。
> - 参数量、专家数与训练规模该卡未写，本篇不推测。
>
> **意义**：Gemini 3 Pro 是 Google 从「技术报告」转向「十页模型卡加外链方法文档」的代表。该卡比此前的模型卡多写了训练数据来源类别、分发渠道与预期用途，却把 2.5 技术报告里的 TPU 代数、集群规模和评测细节全部收回成概括句；架构上只确认稀疏 MoE 与原生多模态，并声明不是前代模型的微调。安全部分的信息量集中在两处：内部自动评测里 Text to Text Safety 相对 2.5 Pro 为 -10.4%，作者以人工复核解释；Frontier Safety 各域均未达 CCL，但 Cybersecurity 已达 alert 阈值。

## 一、问题背景

Gemini 2.5 用一份技术报告公开了 MoE 骨架、TPUv5p 集群与评测细节（见 [[Gemini25技术报告深读]]）。到 3 代，Google 改为发布模型卡：该卡开篇称其目的在于提供「essential information on Gemini models, including known limitations, mitigation approaches, and safety performance」，并说这一版比此前的模型卡包含更多关于训练数据、分发与预期用途的信息。能力评测的设置与方法另放在外链的 evals-methodology 文档中。

## 二、脉络

| 时间 | 文档 | 变化 |
|---|---|---|
| 2025-07 | Gemini 2.5 技术报告（arXiv 2507.06261） | 长篇技术报告，公开 Infra 与评测细节 |
| 2025-11 | Gemini 3 Pro 模型卡与博文 | 改为模型卡；Deep Think 写成可选推理模式；Frontier Safety 按 2025 年 9 月版框架 |
| 2026-05 | 该卡 Last Updated | 族内型号列表扩到 3.1 与 3.5 系列 |

## 三、模型信息与相对 2.5 的字段变化

| 字段 | 该卡原文要点 |
|---|---|
| 定位 | 「natively multimodal, reasoning models」；「Google’s most advanced model for complex tasks」 |
| Deep Think | 「an optional setting designed to enhance complex problem-solving performance at time of inference」 |
| 依赖关系 | 「not a modification or a fine-tune of a prior model」；族内后续型号都基于 3 Pro，列出 Gemini 3 Pro Image、Gemini 3 Flash、Gemini 3.1 Pro、Gemini 3.1 Flash Image、Gemini 3.1 Flash-Lite、Gemini 3.1 Flash Live、Gemini 3.5 Flash |
| 输入 / 输出 | 文本、图像、音频、视频，上下文 up to 1M；输出文本，64K token |
| 知识截止 | January 2025 |
| 架构 | 稀疏 MoE、基于 Transformer、原生支持文本、视觉与音频输入；只说「Developments to the model architecture contribute to the significantly improved performance」，没有具体改动 |
| 预训练数据 | 公开网页、文本、代码、图像、音频与视频；另列可下载公开数据集、爬虫数据、商业授权数据、按服务条款与用户控制使用的用户数据、业务运营与员工数据、AI 生成的合成数据 |
| 后训练 | 指令微调、强化学习与人类偏好数据；强化学习可利用「multi-step reasoning, problem-solving and theorem-proving data」 |
| 数据处理 | 去重、遵守 robots.txt、安全过滤与质量过滤，含色情、暴力与 CSAM 过滤 |
| 硬件 / 软件 | 只写 Google 的 TPU 与 TPU Pods 的一般性说明；软件为 JAX 与 ML Pathways |
| 分发 | Gemini App、Google Cloud / Vertex AI、Google AI Studio、Gemini API、Google AI Mode、Google Antigravity；族内部分型号可经 Notebook LM |

与 2.5 技术报告对照，骨架表述一致，而 TPU 代数、pod 规模与训练时间账都没有出现在该卡中，2.5 的这些数字不能直接套到 3 Pro 上。

## 四、能力

该卡第 5 页的能力表是图片，正文只给出总判：「Gemini 3 Pro significantly outperforms Gemini 2.5 Pro across a range of benchmarks requiring enhanced reasoning and multimodal capabilities」，结果截至 November 2025。博文以文字给出的数字如下：

| 评测 | Gemini 3 Pro（博文） |
|---|---|
| Humanity’s Last Exam（不用工具） | 37.5% |
| GPQA Diamond | 91.9% |
| MathArena Apex | 23.4% |
| MMMU-Pro | 81% |
| Video-MMMU | 87.6% |
| SimpleQA Verified | 72.1% |
| Terminal-Bench 2.0 | 54.2% |
| SWE-bench Verified | 76.2% |
| LMArena / WebDev Arena | 1501 Elo / 1487 Elo |

博文另报 Deep Think 模式：Humanity’s Last Exam 41.0%（不用工具），GPQA Diamond 93.8%，ARC-AGI-2 45.1%（with code execution, ARC Prize Verified）。

## 五、内容安全

**评测类型**：训练与开发期的自动和人工评测、模型团队之外的专家人工红队、自动红队、发布前的伦理与安全审查，并按 Frontier Safety Framework 测试。安全政策列六类：儿童性虐待材料、仇恨言论、危险内容、骚扰、色情内容、违背科学或医学共识的医疗建议。

**内部自动评测**（相对 Gemini 2.5 Pro，绝对百分比增减）：

| Evaluation | vs. Gemini 2.5 Pro |
|---|---|
| Text to Text Safety | -10.4% |
| Multilingual Safety | +0.2% (non-egregious) |
| Image to Text Safety | +3.1% (non-egregious) |
| Tone | +7.9% |
| Unjustified-refusals | +3.7% (non-egregious) |

作者称总体在安全与语气上优于 2.5 Pro、同时保持低无理拒绝；人工复核确认损失「overwhelmingly either a) false positives or b) not egregious」。该卡同时说明这些结果用改进后的评测计算，不能与此前 Gemini 模型卡直接比较；Deep Think 模式的安全评测结果与默认模式一致。

**人工红队与风险**：儿童安全达到上线阈值；内容安全总体与 2.5 Pro 相近或更好；红队范围扩展到严格政策之外，未发现严重问题。主要风险为越狱（较 2.5 Pro 改善，但仍是开放研究问题）与多轮对话中可能的退化。缓解手段包括数据过滤、conditional pre-training、SFT、人类与 critic 反馈强化学习以及产品级安全过滤。

## 六、Frontier Safety

该卡按 2025 年 9 月版 Frontier Safety Framework 评估，各域均未达到关键能力档（CCL）；alert 阈值是 CCL 之下的预警线，框架本身见 [[模型卡与SystemCard规范]]。

| 领域 | 该卡要点 | CCL | 结论 |
|---|---|---|---|
| CBRN | 信息准确、偶有可操作性，但一般不足以显著增强中低资源威胁者的能力 | Uplift Level 1 | 未达 |
| Cybersecurity | key skills 基准 v1 hard 11/12 解出；v2 端到端 0/13；Alert threshold met | Uplift Level 1 | 未达 |
| Harmful Manipulation | 操纵效力高于非生成式 AI 基线，相对前代无显著提升，未达 alert | Level 1 (exploratory) | 未达 |
| ML R&D | 优于 Gemini 2.5，尤以 RE-Bench 的 Scaling Law Experiment 与 Optimize LLM Foundry 为甚；聚合分仍远低于 alert | Acceleration level 1；Automation level 1 | 未达 |
| Misalignment (Exploratory) | situational awareness 3/11，stealth 1/4 | Instrumental Reasoning Levels 1 + 2 | 未达 |

细节在单独的 *Gemini 3 Pro Frontier Safety Framework Report*；Deep Think 模式的 Frontier Safety 评测结果与默认模式一致。

## 七、意义

该卡显示前沿闭源厂商的公开文档在变短：架构只剩一句骨架描述，Infra 只剩硬件品类与软件栈名，能力数字移到图片与外链文档。它的增量在合规字段：数据来源类别、robots.txt 与 CSAM 过滤、分发渠道与禁止用途都写得比 2.5 更完整。对研究者而言，可直接引用的是 Deep Think 被定义为推理期可选设定、「非前代微调」的声明，以及 Frontier Safety 表中 cyber 达 alert 而未达 CCL 的判定。

## 八、局限与待核实

1. 版本：官方模型卡索引页的条目写「Updated 18 November 2025」，该卡 PDF 写「Last Updated: May 2026」，两者不一致；本篇按正文所用 PDF 的日期计，截至只到月份。
2. 第 5 页能力表与 evals-methodology 文档里的结果表都是图片，本篇只录博文文字给出的数字；与 Claude、GPT 的横比不录。
3. *Gemini 3 Pro Frontier Safety Framework Report* 未读，cyber alert 的具体评测与分数不在本篇。
4. 「architecture developments」没有具体内容；Deep Think 的机制与思考预算的关系该卡未写。
5. 该卡正文写 evals-methodology 的链接为 deepmind.com 域名，页脚为 deepmind.google 域名，两者都跳转到同一份方法文档。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[Gemini25技术报告深读]] | 2.5 的骨架、TPU 与评测作对照 | 2.5 的技术细节 |
| [[Gemini37Flash模型卡深读]] | 边界：Gemini 3 Pro 之后的变化见 [[Gemini37Flash模型卡深读]] | 3.7 Flash 的增量字段 |
| [[模型卡与SystemCard规范]] | Frontier Safety Framework 的框架背景 | 框架定义与他家框架对照 |
| [[推理时扩展TestTimeScaling]] | Deep Think 作为推理期可选设定 | 推理时扩展的方法与曲线 |
| [[开源与闭源前沿模型谱系]] | Gemini 代际中 3 Pro 的位置 | 全谱系 |
| [[AI基础设施总览]] | 该卡 Infra 公开度低于 2.5 报告 | TPU 与训练系统细节 |
| [[SystemCard谱系时间线]] | 该卡在各厂文档谱系中的位置 | 全谱系 |

## 十、延伸阅读

- [[Gemini25技术报告深读]]：对照阅读可看出 3 Pro 模型卡收回了哪些技术细节。
- [[Gemini37Flash模型卡深读]]：同族后续卡如何在 3 Pro 字段之上只报增量。
- [[模型卡与SystemCard规范]]：Frontier Safety Framework 与 Preparedness、RSP 的对照。
- [[推理时扩展TestTimeScaling]]：Deep Think 这类推理期加算的方法背景。
- [[开源与闭源前沿模型谱系]]：3 Pro 在闭源前沿模型中的代际位置。
- [[AI基础设施总览]]：该卡只写 TPU 品类，训练系统可回到这篇查。
- [[SystemCard谱系时间线]]：各厂模型卡与系统卡的时间顺序。
