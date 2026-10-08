---
title: "视频—语言推理：SiLVR + Chain-of-Frames（≠ AV-Flamingo）"
topic: SiLVR与ChainOfFrames
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2505.24869
 - https://arxiv.org/abs/2506.00318
 - https://arxiv.org/abs/2605.26014
arxiv: ["2505.24869", "2506.00318", "2605.26014"]
related: ["音视频联合Flamingo", "视频生成模型脉络", "多模态架构脉络", "DeepSeekR1推理训练深读", "潜空间推理Coconut"]
code_urls:
 - "https://sites.google.com/cs.unc.edu/silvr"
 - "https://github.com/SaraGhazanfari/CoF"
 - "https://github.com/aiming-lab/storm"
retrieval_cutoff: 2026-07-17
timezone: Asia/Shanghai (CST)
---

# 视频—语言推理：SiLVR + Chain-of-Frames（≠ AV-Flamingo）

> **主要来源**：[SiLVR: A Simple Language-based Video Reasoning Framework](https://arxiv.org/abs/2505.24869)（Zhang 等，UNC Chapel Hill，TMLR 2026-01，v3 2026-04-15）；[Chain-of-Frames: Advancing Video Understanding in Multimodal LLMs via Frame-Aware Reasoning](https://arxiv.org/abs/2506.00318)（Ghazanfari 等，NYU / EPFL，简称 CoF，v2 2026-04-04）；补充：[STORM: Internalized Modeling for Spatial-Temporal Reasoning in Video-Language Models](https://arxiv.org/abs/2605.26014)（Liang、Chen 等，v1 2026-05-25，正文题名为 TORM）（截至 2026-07-17）。
> **研究线**：架构思想（主：把视频转成语言交给推理模型，或在推理链中显式引用帧号）；评测字段（辅：VideoMME、Video-MMLU、CGBench、VSI-Bench 等）
> **范围与相邻笔记**：
> - ≠ [[音视频联合Flamingo]]：那篇是开源音视频联合基础模型，本篇是视频推理的框架与数据形态。
> - ≠ [[视频生成模型脉络]]：本篇是理解与推理，不是生成。
>
> **意义**：推理模型（如 DeepSeek-R1）在文本上进步很快，视频理解却难以直接受益：要么为视频专门收集思维链数据再训练，要么用多阶段代理先挑关键帧再回答，成本高且时间定位弱。两篇给出相反的两种简化：SiLVR 完全不训练，把视频切段写成描述、配上语音转写，交给推理 LLM 在纯语言空间作答，在 Video-MMLU、CGBench 等长视频基准上取得当时最好成绩；CoF 让视频模型在一次解码的推理链里写出「第 k 帧：……」，用 16 万条含低成本合成数据的样本微调，就让 InternVL3-8B 在五个基准上平均提高 5.1 分。前者说明强推理 LLM 可以零训练迁移到视频，后者说明时间定位可以靠推理链格式学会。

---

## 一、问题背景

长视频问答的难点有两个：信息量远超上下文（CGBench、EgoLife 的视频平均超过 1 小时，SiLVR §4.1），以及回答需要定位到具体时刻。CoF §3.1 把已有视频思维链做法的问题归为两类：一类靠 LLM 加人工标注生成思维链数据，成本高（VideoCoT 只有 11k 条），且推理步骤不与具体帧对齐；另一类用多个辅助模型先找关键帧再推理（如 VideoEspresso），推理开销大，且只把部分帧交给模型，丢失完整时间上下文。LLM 代理（VideoAgent、VideoTree 等）则需要与大模型多轮交互（SiLVR §4.4）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-03 | [VideoAgent](https://arxiv.org/abs/2403.10517) | 以 LLM 为代理，多轮检索帧来回答长视频问题 |
| 2024-05 | [VideoTree](https://arxiv.org/abs/2405.19209) | 自适应树状组织视频片段供 LLM 推理 |
| 2024-11 | [VideoEspresso](https://arxiv.org/abs/2411.14794) | 带核心帧选择的大规模视频思维链数据集，CoF 的真实数据来源 |
| 2025-01 | [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | 强化学习训出的推理 LLM，SiLVR 的默认推理器 |
| 2025-05 | SiLVR | 免训练：视频转语言后交给推理 LLM |
| 2025-05 | Chain-of-Frames | 单阶段推理链中引用帧号，配套 CoF-DATA |
| 2026-05 | TORM（STORM） | 把时空推理内化到有界的连续隐向量中，推理时不再输出文字思维链 |

## 三、方法

### 3.1 SiLVR（§3）

1. **视频转语言**：把视频切成短片段，用预训练描述模型（默认 NVILA）逐段描述，并用 Whisper-large-v3 做语音转写，二者拼接（§3.1、§3.3）。
2. **语言推理**：把拼接文本与问题交给推理 LLM（默认 DeepSeek-R1，温度 1.0），推理完全在语言空间完成（§3.2、§3.3）；描述模型、语音识别与 LLM 都可替换，无需重训。
3. **自适应上下文压缩（ACR）**：从细粒度片段开始，若文本超出 LLM 上下文上限就把片段长度加倍重新描述，直到放得下（Algorithm 1）。

### 3.2 Chain-of-Frames（§3–§4.1）

- **推理链格式**：模型在一次推理中写出引用相关帧的推理过程再给答案；帧号用帧在视频中的位置（「Frame 1」「Frame 2」），而非时间戳，因此与视频时长和采样频率无关（§3.2）。InternVL 的视频输入本来就在各帧之间插入「Frame-1」「Frame-2」等文字标记，所以作者认为这种格式特别适合 InternVL（§4.1）。
- **CoF-DATA**：真实部分来自 VideoEspresso 的关键帧描述，先重标帧号，再用 Llama-3.1-8B-Instruct 生成问题、推理链与答案；合成部分来自 CLEVRER 三维物体交互视频，用手工模板生成计数、出现顺序、相对距离等问题，无需 LLM。过滤掉问题中已点名帧的样本，并减少但不完全去掉推理链不引用帧的样本，共 164,186 条（§3.3）。
- **训练**：InternVL2.5-4B 冻结视觉编码器、全量微调语言模型与投影层；InternVL3-8B 用 LoRA。推理时均匀采 30 帧（§4.1）。

### 3.3 TORM（补充）

第一阶段用生成的「思维视频」表示对齐若干隐向量 token，第二阶段只用答案监督，让推理过程内化到隐向量中。思维视频只在训练时使用，推理时只做有界的隐向量展开，不再生成视频、重插帧或调用外部视觉工具（摘要、§3）。

## 四、结果

| 工作 | 评测 | 结果 |
|---|---|---|
| SiLVR | Video-MMLU（Table 1） | 83.1，比此前最好的 Claude 3.5 Sonnet 高 11.8 分 |
| SiLVR | CGBench 问答（Table 1、§4.2） | 51.8%，比此前最好的 Qwen-2-VL-72B 高 6.9 分 |
| SiLVR | VideoMME 长视频加字幕 / EgoLife（Table 1） | 77.7 / 42.0，比 Gemini 1.5 Pro 高 0.3 / 5.1 分 |
| SiLVR | 推理 LLM 的作用（Table 2） | DeepSeek-R1 比 DeepSeek-V3 在推理类基准平均高 8.0 分、通用视频基准高 3.8 分 |
| SiLVR | VideoMME 长视频无字幕，对比多轮代理（Table 3、§4.4） | 62.7，高于 VideoAgent、VideoTree 等，且只调用一次 LLM |
| SiLVR | CGBench 定位问答 mIoU（Table 5、§4.6） | 11.84，比 GPT-4o 高 6.11，比同期的 VideoMind 高 4.74 |
| CoF | 五基准平均（Table 1） | InternVL2.5-4B 由 60.8 升到 64.6（+3.8），InternVL3-8B 由 67.0 升到 72.1（+5.1） |
| CoF | VSI-Bench / Video-MME（Table 1） | CoF-InternVL3-8B 为 51.3 / 73.7，底座为 41.0 / 66.5 |
| TORM | Qwen2.5-VL-7B 底座，32 帧（Table 1） | VideoMME 61.0、MVBench 61.1、TempCompass 74.3 |

SiLVR 的消融显示语音转写比画面描述更重要：在 VideoMME 上，去掉 50% / 75% 的语音 token，准确率由 70.3 降到 65.3 / 56.0，去掉同比例的画面描述只降到 68.9 / 67.7（Table 7）；ACR 比最好的固定 8 秒片段高 2.5 分（76.7 对 74.2，Table 8）。CoF 的消融中，同样规模下只用合成数据在多数基准上好于只用真实数据，二者合用则在 EventHallusion 以外的基准上都最好（§5.1）。

## 五、意义

两篇代表视频推理的两种成本取舍。SiLVR 把视频理解拆成感知与推理两个模块，推理端直接继承文本推理模型的进步，换模型不必重训，在长视频上尤其有效；它也提示语音转写在许多视频问答中比画面描述更有信息量。CoF 则保留端到端视频模型，只改变推理链的书写格式，并表明低成本的合成数据就能教会帧级定位。TORM 再往前一步，把推理从可读文字改成连续隐向量，以可解释性换取推理开销。

## 六、局限与待核实

- **SiLVR 的信息瓶颈**：画面先被压成文字，细粒度视觉信息可能丢失；去掉语音转写后八个基准全部下降（VideoMME 由 77.7 降到 62.7，Table 6），说明它依赖带语音的视频。
- **SiLVR 表格不一致**：Table 2 中 DeepSeek-R1 一行的 CGBench 与 CinePile 两列写成 59.4 / 51.8，与 Table 1（51.8 / 59.4）及正文「CGBench 51.8%」相反，本篇按 Table 1 与正文。
- **SiLVR 正文与表格口径不一**：摘要说 CGBench mIoU 比此前最好方法高 6.1%，但 Table 5 中最好的基线是 VideoMind（7.10），差距为 4.74，6.11 是相对 GPT-4o 的差距；§4.7 写去掉语音 token 下降 11.4%–20.7%、去掉画面描述下降 7.8%–9.0%，与 Table 7 的数值对不上，本篇只用表中数值。
- **CoF 的基线口径随提示方式而变**：Table 1 中 InternVL2.5-4B 的基线是 CoT 提示下的分数（与 Table 4 的 CoT 提示行、Table 3 的「+ CoT Prompting」行相同），Table 3 的「Original」用的是标准提示，所以 Video-MME 有 54.7 与 54.9 两个值；InternVL3-8B 在 Table 1 中的基线与 Table 4 标准提示、CoT 提示两行都对不上（如 MVBench 为 74.4，两行分别为 72.0 与 74.3）。比较增益时要说明用的是哪种提示，本篇正文的 +3.8 / +5.1 按 Table 1 计；CoF 依赖 InternVL 的帧号交织格式，合成数据与真实视频之间也有分布差。
- **STORM 与 TORM 名称不一**：arXiv 页面题名为 STORM（摘要里写作 STORMS），正文题名为 TORM，代码仓库名为 storm。
- **TORM 证据有限**：只有 v1，主结果只在一个 7B 底座上报告。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[音视频联合Flamingo]] | 对照：同样面向长时真实音视频理解，那篇训练一个音视频联合模型，SiLVR 用现成语音识别与描述模型外接推理 LLM | 音视频联合模型的训练配方 |
| [[视频生成模型脉络]] | 辨析：那篇讨论的 Wiedemer 等「逐帧生成即逐步推理」的 chain-of-frames，与本篇在推理链中引用帧号的 Chain-of-Frames 同名不同义 | 视频生成通史 |
| [[多模态架构脉络]] | 上游：CoF 微调的 InternVL 属于那篇所写的「视觉编码器接 LLM」路线 | 多模态理解通史 |
| [[DeepSeekR1推理训练深读]] | 上游：SiLVR 的默认推理器 DeepSeek-R1 的训练方法在那篇，本篇的 Table 2 显示换成非推理 LLM 会明显掉分 | R1 的强化学习配方 |
| [[潜空间推理Coconut]] | 上游：TORM 把那篇所写的连续隐向量推理（被 TORM 引为相关工作）用到视频时空推理上 | 文本侧潜空间推理 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [SiLVR](https://arxiv.org/abs/2505.24869) §3、Table 1–3、Table 6–8 | 两阶段框架、ACR、主结果与消融 |
| 2 | [Chain-of-Frames](https://arxiv.org/abs/2506.00318) §3.2–3.3、Table 1、§5.1 | 推理链格式、CoF-DATA 与合成数据的作用 |
| 3 | [TORM（STORM）](https://arxiv.org/abs/2605.26014) 摘要、Figure 1 | 隐向量内化推理的思路 |
