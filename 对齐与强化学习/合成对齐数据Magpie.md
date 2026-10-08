---
title: "合成对齐数据：Magpie + ActiveUltraFeedback"
topic: 合成对齐数据Magpie
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2406.08464
 - https://arxiv.org/abs/2603.09692
arxiv: ["2406.08464", "2603.09692"]
related: ["对齐脉络RLHF与偏好优化", "SimPO与ORPO偏好优化", "SafeDPO与RePO", "合成数据与教科书式数据", "BeyondWeb合成预训练", "NemotronCC数据策展"]
project:
 - https://magpie-align.github.io/
 - https://hf.co/magpie-align
 - https://github.com/lasgroup/ActiveUltraFeedback
 - https://huggingface.co/ActiveUltraFeedback
 - https://lasgroup.github.io/rlhf/ActiveUltraFeedback.html
archived: 2026-09-22
---

# 合成对齐数据：Magpie + ActiveUltraFeedback

> **主要来源**：[Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing](https://arxiv.org/abs/2406.08464)（Xu 等，UW / AI2，简称 Magpie，v2）；[ActiveUltraFeedback: Efficient Preference Data Generation using Active Learning](https://arxiv.org/abs/2603.09692)（Melikidze 等，ETH / UZH，简称 ActiveUF，v2，ICML 2026）（截至 2026-06-01）。
> **研究线**：架构思想 / 数据流水线（指令数据从哪来、偏好对怎么挑，主）· 评测字段（AlpacaEval 2、Arena-Hard、RewardBench 2 等，辅）
> **范围与相邻笔记**：
> - ≠ [[合成数据与教科书式数据]]、[[BeyondWeb合成预训练]]：本篇不写预训练阶段的教科书式合成与网页改写合成。
> - ≠ [[NemotronCC数据策展]]：本篇不写预训练网页语料的过滤与配比。
> - ≠ [[SimPO与ORPO偏好优化]]、[[SafeDPO与RePO]]：本篇不写偏好损失函数；那些方法是本篇数据的下游消费者。
> - ≠ [[对齐脉络RLHF与偏好优化]]：本篇不写 RLHF、DPO、CAI 通史，只回答「对齐数据从哪来」。
>
> **意义**：对齐数据长期是开源与闭源模型差距最大的一环。Magpie 表明，只给已对齐模型输入对话模板的用户前缀，就能让它自己「吐出」大规模高质量指令，不要种子题也不要提示工程；ActiveUF 则把「每个提示该标哪一对回答」变成主动学习问题，以静态基线约六分之一的标注量取得相当或更好的结果。两者分别降低了指令数据的获取成本和偏好数据的标注成本。

**一句话**：Magpie 是「对着聊天模板空手变出用户问题」；ActiveUF 是「题目已有、候选回答很多，用不确定度和质量差挑出最值得标的一对」。

---

## 一、问题背景

**指令数据一侧**（Magpie §1）：开源权重常见，对齐数据却多为私有；人工标注昂贵；Self-Instruct、Evol-Instruct、UltraChat 等合成方法依赖种子问题和提示工程，数据规模一大，多样性就下降。Magpie 的问题是：能否直接从已对齐的模型中抽出大规模、高质量、多样的指令？

**偏好数据一侧**（ActiveUF §1、§2）：UltraFeedback 一类偏好数据集用多个模型生成候选、再用 LLM 评判打分，但「选哪一对进数据集」靠静态启发式（随机、取最好与最差、固定的大小模型对比）。主动学习文献把它看作上下文对决老虎机（contextual dueling bandit）问题，却多只关注奖励模型或只关注策略优化一侧。ActiveUF 的问题是：能否用不确定度自适应地选对，以更少标注做出同时适合奖励建模和多种偏好优化算法的数据？

## 二、脉络

| 时间 | 节点 | 推进了什么 |
|---|---|---|
| 2022-12 | Self-Instruct | 用模型从少量种子任务自举生成指令 |
| 2023-04 | Evol-Instruct（WizardLM） | 用提示让模型逐步改写、加深指令 |
| 2023-05 | UltraChat | 大规模多轮对话合成，Magpie 的主要对照之一 |
| 2023-10 | UltraFeedback | 多模型生成 + LLM 评判打分的偏好数据范式，ActiveUF 的骨架 |
| 2024-06 | Magpie | 无种子、无提示工程，从对话模板直接生成指令 |
| 2025-07 | Delta Learning Hypothesis | 偏好对的质量差比绝对质量更重要，ActiveUF 的直接动机 |
| 2026-03 | ActiveUF | 不确定度驱动的主动选对 |

日期为 arXiv 首版日期。

## 三、Magpie：从对话模板生成指令

### 3.1 核心观察（§1、§2.1）

已对齐模型的输入可写成「用户前缀模板 ⊕ 用户问题 ⊕ 助手前缀模板」。以 Llama-3-Instruct 为例，用户前缀是 `<|start_header_id|>user<|end_header_id|>`。Magpie 发现：**只输入用户前缀模板**，自回归模型就会自己续写出一条用户问题。再把这条问题按正式模板包好让模型作答，就得到一条指令—回答对。论文称这种做法不需要种子问题和提示工程，多样性不易随规模下降；即使对齐时指令部分的损失被屏蔽，模型仍能生成高质量指令，作者假设模型对指令分布有隐式记忆。

适用于 Llama-3 / 3.1、Qwen2、Gemma-2、Phi-3 等开源对话模型（§2.1、附录 A）。

### 3.2 扩展（§2.2）

- **过滤**：可组合长度、任务类别、输入质量与难度、与最近邻的距离、奖励及奖励差等指标（附录 C）。
- **多轮**（Magpie-MT）：每轮结束再接一次用户前缀；小模型容易忘记自己是用户，需用系统提示固定角色。
- **偏好数据**（Magpie-DPO）：对筛选后的指令以温度 0.8 采样 5 条回答，用奖励模型（ArmoRM-Llama3-8B-v0.1）打分，最高者为被选、最低者为被拒（参数见 §4.1）。
- **领域与多语言**：用系统提示控制任务领域与语言，或直接对代码、数学专用模型运行 Magpie。

### 3.3 数据与成本（§3）

| 数据集 | 生成模型 | 规模 | 成本 |
|---|---|---|---|
| Magpie-Air | Llama-3-8B-Instruct | 3M（评测常用 300K） | 4×A100 上第一步 1.55 小时、第二步 50 小时，共约 206 GPU 小时；云端约 0.12 美元 / 千条 |
| Magpie-Pro | Llama-3-70B-Instruct | 1M（评测常用 300K） | 第一步 3.5 小时、第二步 150 小时，共约 614 GPU 小时；约 1.1 美元 / 千条 |
| Magpie-*-DPO | 同上 + ArmoRM | 各 100K | — |

整个 Magpie 数据家族超过 1,140 万条指令—回答对（附录 A），全程不用人工写题、不调用 GPT-4 API。Llama-Guard-2 检测下潜在有害数据少于 1%（§3.3）。属性分析显示 Pro 版一半以上是信息检索类问题；两版指令多数被评为中等及以上质量，Pro 版整体高于 Air 版（§3.2）。

### 3.4 关键结果（§4）

Llama-3-8B 基座上的对齐结果（Table 1，AE2 LC 为对 GPT-4-Turbo 的长度控制胜率）：

| 对齐设定 | 数据量 | AE2 LC | AE2 WR | Arena-Hard |
|---|---:|---:|---:|---:|
| UltraChat SFT + UltraFeedback DPO | 208K + 64K | 18.36 | 17.33 | 14.8 |
| Magpie-Air-300K-Filtered SFT | 300K | 22.66 | 23.99 | 14.9 |
| + Magpie-Air-DPO | +100K | 45.48 | 50.43 | 35.9 |
| Magpie-Pro-300K-Filtered SFT | 300K | 25.08 | 29.47 | 18.9 |
| + Magpie-Pro-DPO | +100K | 50.10 | 53.53 | 35.7 |
| Llama-3-8B-Instruct（官方 SFT + DPO） | >10M | 22.92 | 22.57 | 20.6 |

- 只用 Magpie 做 SFT 就超过「UltraChat SFT + UltraFeedback DPO」；以 Llama-3-8B-Instruct 为参照时，Magpie-Pro SFT 的 AE2 LC 为 52.12，即胜过官方 Instruct 模型。
- 加 Magpie-DPO 后 AE2 LC 达 50.10，全程不超过 40 万条数据，官方模型用了超过 1,000 万条（§4.2）。
- Qwen 系基座：以官方对齐模型为参照，Qwen2-1.5B 与 Qwen1.5-4B 基座加 Magpie-Pro 后的 AE2 LC 为 56.66 与 68.09，Qwen1.5-7B 为 46.28，略低于 50（Table 2）。
- 短板在推理：Magpie-Pro-300K-Filtered 的 GSM8K 只有 47.92，混入 15 万条数学、代码与推理数据（Pro-Mix）后升到 63.08，Open LLM 平均分 64.21，在全部对照模型中进入前三，仍低于 Llama-3-8B-Instruct 的 GSM8K 71.72 与平均 66.13（Table 3）。
- 附录中的 MagpieLM-8B-Chat：AE2 LC 58.18、Arena-Hard 48.4、WildBench 44.72。

## 四、ActiveUltraFeedback：主动挑选偏好对

### 4.1 形式化与流水线（§3–§4）

把选对建模为上下文对决老虎机：提示是上下文，两条候选回答是两个臂，用奖励的上下置信界驱动选择。每批提示依次执行五步：

1. **生成**：30 个开源模型（12 个家族）各生成回答；仿 UltraFeedback，为每个提示—模型随机抽一条原则（有用、真实、诚实）以增加多样性。
2. **估奖励**：用认知神经网络（ENN，共享冻结骨干加浅层 MLP 集成）给出奖励均值与标准差。
3. **选对**：按下表的方法挑出一对。
4. **标注**：LLM 评判从真实性、指令遵循、诚实、有用四个维度各打 1–5 分，均分高者为被选。
5. **更新**：用累计数据更新 ENN，进入下一批。

| 类别 | 方法 | 每题需评判的回答数 | 做法 |
|---|---|---:|---|
| 被动启发式 | Random | 2 | 随机一对 |
| | MaxMin | 30（整池） | 评判全池，取最高与最低 |
| | UltraFeedback 式 | 4 | 随机 4 条，最高者对其余随机一条 |
| | DeltaQwen | 0 | 固定 Qwen3 0.6B 对 32B，大模型为被选 |
| 对决老虎机 | InfoMax、DTS、MaxMin-LCB | 2 | 分别追求纯探索、双 Thompson 采样、按下置信界选最优与最差 |
| ActiveUF 新方法 | DRTS | 2 | 双向 Thompson：一条取后验最大、一条取后验最小，故意拉大质量差 |
| | DeltaUCB | 2 | 乐观意义下质量差最大的一对 |

两个新方法都把 Delta Learning Hypothesis（质量差比绝对质量更重要）嵌进不确定度驱动的选择，又不锁定单一模型家族。

### 4.2 关键结果（§5，Tulu-3-8B-SFT 起步，提示取自 UltraFeedback）

下游四项（GSM8K、IFEval、TruthfulQA、AlpacaEval 2）相对基座的提升均值，以及独立奖励模型在 RewardBench 2 上的提升（Table 2；基座下游均分 0.506，RewardBench 2 为 0.290）：

| 方法 | 下游均值 Δ | RewardBench 2 Δ |
|---|---:|---:|
| 原始 UltraFeedback 对 | +0.037 | +0.295 |
| Random | +0.046 | +0.278 |
| UltraFeedback 式启发式 | +0.036 | +0.287 |
| MaxMin | +0.111 | +0.318 |
| DeltaQwen | +0.137 | +0.100 |
| InfoMax | +0.016 | +0.297 |
| DTS | +0.023 | +0.224 |
| MaxMin-LCB | +0.016 | +0.230 |
| DRTS | +0.127 | +0.312 |
| DeltaUCB | +0.120 | +0.339 |

论文以下游差至少 0.008、RewardBench 2 差至少 0.02 作为有意义差异的阈值。读表要点（§5.2–§5.3）：

- DRTS 与 DeltaUCB 在下游和奖励建模两侧都强，且超过原始 UltraFeedback 数据。
- DeltaQwen 的 DPO 下游均值略高，但主要由 AlpacaEval 2 拉动，奖励建模很弱（+0.100，不如随机），论文归因于数据锁定在 Qwen 家族的分布内、多样性不足。
- 经典对决老虎机方法确实找到了高质量回答（论文以 DTS、MaxMin-LCB 为例分析），却常给出两条都好的对，缺少学习所需的质量差，论文称这些方法甚至不如随机采样。
- 样本效率：摘要称 ActiveUltraFeedback 只需静态基线约六分之一的标注数据，即可取得相当或更好的结果；奖励建模饱和更慢，约 40k 样本才达到全量静态数据的水平（Figure 3b）。
- 泛化（§5.4–§5.5）：换用 Skywork、Tulu-3 等提示来源，或把 DPO 换成 IPO、SimPO，DRTS 与 DeltaUCB 仍保持优势，DeltaQwen 则在 IPO、SimPO 上明显掉队。

## 五、两项工作对照

| 维度 | Magpie | ActiveUF |
|---|---|---|
| 主要产出 | 指令—回答对（可扩展为多轮与 DPO 偏好对） | 给定提示上的被选—被拒偏好对 |
| 是否需要外部提示库 | 不需要，自己生成指令 | 需要 |
| 是否需要多模型池 | 单个已对齐模型即可闭环 | 30 个模型的池是多样性前提 |
| 相对 UltraFeedback | 替代「指令从哪来」 | 升级「怎么选对」：静态启发式 → 主动选对 |
| 节省的成本 | 指令获取与人工撰写 | 偏好标注 |

## 六、意义

Magpie 把对齐数据的瓶颈从「写题」转到「挑题」：已对齐模型本身就是取之不尽的指令来源，社区可以用很低的成本复现接近官方对齐模型的效果。ActiveUF 则说明，偏好数据的价值主要在每一对的质量差，而不是回答本身有多好；用不确定度加质量差选对，标注预算可以大幅压缩，并且同一份数据能同时服务奖励建模和多种偏好优化算法。两者合起来，覆盖了离线对齐数据「造」与「挑」两个环节。

## 七、局限与待核实

- **Magpie**：生成的数据继承来源模型的风格与偏差；原生数据推理类偏弱，需要域控合成补强；「隐式记忆」只是作者假设；评测多依赖 LLM 评判的 AlpacaEval 2 与 Arena-Hard。
- **ActiveUF**：当前实现为便于大规模消融，对全部提示预先生成了全部回答与评判分数，主要节省的是标注而非生成算力；论文把「先决定该询问哪些模型」列为后续方向（§6）。标注来自 LLM 评判，论文目标是可复现的大规模对照，并未宣称可替代人类标注。
- 附录中的过滤消融、生成温度与难度的关系、GPU 小时与随机种子稳定性等明细未收入，需要时回读原文附录。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[对齐脉络RLHF与偏好优化]] | 上游：RLHF 与 DPO 需要的指令与偏好数据正是本篇两种流水线的产物 | RLHF、DPO、CAI 通史 |
| [[SimPO与ORPO偏好优化]] | 下游：SimPO 的 Base 设定用 UltraFeedback 数据；ActiveUF 把 SimPO 与 IPO 作为检验数据泛化性的下游算法 | 偏好损失推导 |
| [[SafeDPO与RePO]] | 下游：两种方法都消费现成的偏好数据（SafeDPO 另加安全标签），数据怎样造与挑在本篇 | 安全约束与遗憾分解 |
| [[合成数据与教科书式数据]] | 同为「合成数据」，但该篇是预训练阶段的教科书与代码合成，本篇是对齐阶段 | 预训练合成通史 |
| [[BeyondWeb合成预训练]] | 同为合成，该篇是预训练阶段对网页的改写合成及其缩放消融 | 预训练改写合成 |
| [[NemotronCC数据策展]] | 同为数据侧：该篇是预训练网页语料的分类器过滤与合成改写，本篇是对齐阶段的指令与偏好数据 | Nemotron-CC 管线 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Magpie](https://arxiv.org/abs/2406.08464) Figure 1、§2、Table 1 | 两步流水线与主结果 |
| 2 | [Magpie 项目页](https://magpie-align.github.io/) | 数据集与模型 |
| 3 | [ActiveUF](https://arxiv.org/abs/2603.09692) Figure 2、Table 1–2、Figure 3 | 五步循环、选对方法、样本效率 |
| 4 | [lasgroup/ActiveUltraFeedback](https://github.com/lasgroup/ActiveUltraFeedback) | 流水线实现 |
| 5 | [UltraFeedback](https://arxiv.org/abs/2310.01377)、[Delta Learning Hypothesis](https://arxiv.org/abs/2507.06187) | ActiveUF 的骨架与动机 |
