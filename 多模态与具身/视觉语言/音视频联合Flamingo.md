---
title: "开源音视频联合模型：Audio-Visual Flamingo / Nemotron-Labs-AV-Flamingo（≠ Qwen Omni / Speech-LLM / Seamless / 视频生成）"
topic: 音视频联合Flamingo
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2607.16107
arxiv: ["2607.16107"]
related:
 - "QwenOmni音视频原生"
 - "SpeechLLM语音语言模型"
 - "StepAudio2语音旗舰"
 - "多模态架构脉络"
 - "SiLVR与ChainOfFrames"
 - "GRPO与DAPO算法族"
 - "视频生成模型脉络"
retrieval_cutoff: 2026-07-17
timezone: Asia/Shanghai (CST)
---

# 开源音视频联合模型：Audio-Visual Flamingo / Nemotron-Labs-AV-Flamingo（≠ Qwen Omni / Speech-LLM / Seamless / 视频生成）

> **主要来源**：[Audio-Visual Flamingo: Open Audio-Visual Intelligence for Long and Complex Videos](https://arxiv.org/abs/2607.16107)（Ghosh、Goel 等，NVIDIA / 马里兰大学，v1 2026-07-17；正文标题为 Nemotron-Labs-Audio-Visual Flamingo，简称 AV-Flamingo 或 AVF）（截至 2026-07-17）。
> **研究线**：架构思想（主：双编码器、按时间交错的音视 token、短到长三阶段课程、带时间戳的推理链）；评测字段（辅：全模态、音频、视频、语音识别基准与数据消融）
> **范围与相邻笔记**：
> - ≠ [[QwenOmni音视频原生]]：那篇是 Qwen 系开放权重的全模态产品线，本篇是训练数据与代码都公开的非 Qwen 系音视频联合理解模型。
> - ≠ [[SpeechLLM语音语言模型]]：那篇只处理音频，本篇把音频与视频按时间对齐后一起理解。
> - ≠ [[视频生成模型脉络]]：本篇是理解与推理，不是生成。
>
> **意义**：此前的音视频大模型多在短片段上训练，且常把音频与视觉分开训练、指望跨模态推理自然出现；最强的模型要么闭源，要么只开放权重。AV-Flamingo 从 OmniVinci 出发，用约 700 万条专门要求音视联合推理的长视频描述与问答，按短到长三阶段训练，再用把推理步骤挂到音视时间戳上的思维链做 SFT 与 GRPO，在面向长视频音视理解的 MMOU 上把开源模型此前 46.8% 的水平提到 56.9%（推理版 60.2%），并公开模型、训练与推理代码。它说明在 7B 规模上，开源路线可以靠专门构造的联合监督缩小与闭源模型在长视频音视理解上的差距；但许可只限非商业研究。

---

## 一、问题背景

作者归纳了长视频音视理解的三个缺口（§1）：一是公开数据多为单模态或短片段的识别型问答，长视频的联合监督稀缺；二是许多全模态模型分别训练音频与视觉理解，跨模态推理只能隐式获得，已有分析还发现深层网络偏向视觉、压制音频表示；三是能力最强的音视频模型闭源或只开放权重，数据、代码与方法不公开。作者在相关工作部分指出，Video-MME 与 MMOU 都显示性能随视频变长系统性下降，MMOU 上最好的闭源模型只有 64.2% 准确率，开源模型停在 46.8%；这两个数即 Table 1 中 MMOU 的两个对照 Gemini-2.5 Pro 与 MiniCPM-o 4.5。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2022-04 | [Flamingo](https://arxiv.org/abs/2204.14198) | 桥接冻结的预训练视觉与语言模型，处理任意交错的图文序列，靠少样本提示适配新任务 |
| 2025-03 | [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) | 音频与视频按时间交错排列，用 TMRoPE 对齐时间戳，Thinker–Talker 同时出文本与语音（[[QwenOmni音视频原生]]） |
| 2025-07 | [Audio Flamingo 3](https://arxiv.org/abs/2507.08128) | 统一语音、环境声与音乐的 AF-Whisper 编码器，按需思考，最长 10 分钟音频，只用开源音频数据训练 |
| 2025-10 | [OmniVinci](https://arxiv.org/abs/2510.15870) | OmniAlignNet 对齐视觉与音频嵌入，加时间嵌入分组与约束旋转时间嵌入（CRTE），用 0.2T token 训练，为 Qwen2.5-Omni 的六分之一 |
| 2026-07 | AV-Flamingo | 以 OmniVinci 初始化，构造长视频音视联合数据与带时间戳的推理链 |

## 三、方法

### 3.1 架构（§2.1）

架构与 OmniVinci 相近，五个部件：

1. **视觉编码器**：SigLip 加先多尺度编码再压缩的 Dynamic S2 模块，使分辨率与帧数提高时送进 LLM 的 token 数不按比例增长。
2. **音频编码器**：沿用 Audio Flamingo 系列的 AF-Whisper，16 kHz 单声道、128 通道对数梅尔谱，切成不重叠的 30 秒片段分别编码再按时间拼接，可处理整集播客或电影音轨。
3. **跨模态对齐**：两路各用两层 MLP 投到 LLM 嵌入空间；按时间切成同步片段后交错排列，使同一时间窗的视觉与音频 token 相邻，自注意力可直接跨模态关联；再加 CRTE 编码绝对时间。
4. **语言骨干**：Qwen2.5-7B（36 层），以交错音视嵌入为前缀、文本指令在后，自回归输出文本；最长 15 分钟视频的训练靠混合序列并行（节点内 Ulysses、节点间 Ring-Attention）。
5. **流式语音合成（可选）**：仅解码器 Transformer，根据 LLM 输出的子词与已生成的音频 token 预测下一个音频 token，细节指向 Audio Flamingo 3。

### 3.2 数据：AV-Skills 与 AV-Think（§2.2、附录 A）

作者把 WorldSense、MMOU 等基准的多选题改成开放题，归纳模型的失败类型，再据此构造数据：

| 子集 | 视频时长 | 规模 | 侧重 |
|---|---|---|---|
| AV-Skills-Short | 不超过 60 秒 | 10 万小时，380 万条（100 万描述 + 280 万问答） | 关系、情绪变化、时序、空间、因果、幻觉识别、音频与视频计数等 |
| AV-Skills-Long | 60 秒至 15 分钟 | 约 14 万小时，320 万条（120 万描述 + 200 万问答） | 大海捞针、时序指代与排序、整体推理、音视事件对齐、比较与上下文等 |
| AV-Think | 长视频（预告片、电影回顾、多人对话等） | 约 2.4 万条，推理链平均 635.7 词 | 每个推理步骤都挂到音频与视觉的时间戳上 |
| AV-Safety QA | 长视频 | 536 小时，9.2 万条问答 | 对识别私人身份、提取敏感信息等请求给出安全拒绝 |

AV-Skills 合计约 700 万条描述与问答，其中问答约 480 万条。AV-Think 的生成方式：先产生带时间戳的音视描述，再由 LLM 合成问题、推理与答案三元组。

### 3.3 三阶段课程（§2.3）

1. **预训练**：从 OmniVinci 检查点出发，用单模态数据加 AV-Skills-Short 训练，视频最长 5 分钟、上下文 16K。
2. **中段训练**：加入 AV-Skills-Long，视频最长 15 分钟、上下文 32K，得到 AVF-Instruct。
3. **后训练**：在 AV-Think 上先做 SFT 再做 GRPO，得到 AVF-Think。

作者的假设：早期的单模态与短上下文训练建立感知与弱对齐，后期的长真实视频才建立强对齐、长上下文与时间推理。三阶段都在 512 张 H100 上训练（§3）。

### 3.4 带时间戳的推理链与 GRPO（§2.2、附录 E）

TAVIT（Temporal Audio-Visual Interleaved Chain-of-Thought）要求在证据分散的长音视流里，把中间推理步骤绑定到时间戳，并交错引用音频与视觉证据。GRPO 每题采样 5 个回答（G=5），组内归一化奖励作为优势；奖励有三种：格式（推理与答案须放在规定标签内）、准确率（问答题规范化后比对答案）、结构化（开放描述由 LLM 提取场景、参与者、话题等字段再比重叠）。问答题用格式加准确率，开放生成用格式加结构化。

## 四、结果

作者在 15 个以上的音视频、全模态、音频与视觉基准上评测（摘要）。以下取自 Table 1（准确率，语音识别为 WER）：

| 基准 | 对照 | AVF-Instruct | AVF-Think |
|---|---|---|---|
| WorldSense | Qwen2.5-Omni 45.4；OmniVinci 48.2 | 50.3 | 51.6 |
| DailyOmni | OmniVinci 66.5 | 72.4 | 73.9 |
| OmniBench | Gemini-1.5 Pro 47.6 | 48.5 | 50.6 |
| MMOU | Gemini-2.5 Pro 64.2；MiniCPM-o 4.5 46.8 | 56.9 | 60.2 |
| AVHBench 音→视、视→音幻觉 | Gemini-2.0 Flash 83.3、63.3 | 77.0、81.1 | 79.0、85.9 |
| MMAU（test，平均） | Audio Flamingo 3 72.42；OmniVinci 71.60 | 73.49 | — |
| Video-MME（无字幕、有字幕） | OmniVinci 67.3、68.6 | 70.7、71.2 | — |
| LongVideoBench | OmniVinci 62.0 | 60.1 | — |
| LibriSpeech clean、other（WER） | 对照各取最好：clean 为 Phi-4-mm 1.67，other 为 Qwen2.5-Omni 3.4 | 1.64、3.5 | — |

数据消融（Table 6）：OmniVinci 在 DailyOmni、WorldSense、Video-MME 上为 66.5、48.2、67.3；加 AV-Skills-Short 训练后为 69.5、48.5、68.5；再加 AV-Skills-Long 得到 AVF-Instruct，为 72.4、50.3、70.7。短数据先带来跨模态推理，长数据再提升长程理解。

## 五、意义

AV-Flamingo 的贡献主要在数据与训练流程而非新结构：架构基本沿用 OmniVinci，提升来自专门要求音视联合推理的长视频数据、由短到长的课程，以及把推理绑定到时间戳的后训练。消融显示短、长两类联合数据都带来增益，长数据在 WorldSense 与 Video-MME 上的增益更大。数据、代码与配方公开，给长视频音视理解提供了一条可复现的开源基线；它与 Qwen-Omni 的开放权重路线、SiLVR 的外接推理路线形成三种可比较的做法。

## 六、局限与待核实

- **作者自陈**（§5）：AV-Skills 来自公开数据集与开放互联网，可能有来源偏差，并与预训练数据重叠；极长、信息密集且证据分散的视频仍然困难；现有基准不足以代表开放的真实场景。
- **不是全面领先**：AVHBench 音→视幻觉低于 Gemini-2.0 Flash，MMOU 仍低于 Gemini-2.5 Pro，LongVideoBench 低于初始化来源 OmniVinci。
- **许可**：论文称「fully open」，但 AV-Flamingo 与 AV-Skills 仅限非商业研究使用（附录 I）；初始化检查点与音频编码器为 NVIDIA OneWay Noncommercial License，Qwen2.5-7B 为 Apache 2.0（附录 H、Table 9）。训练用的 Aidatatang 语料在训练后被发行方撤回，不随模型再分发（附录 H）。
- **标题不一致**：arXiv 页面标题为 Audio-Visual Flamingo，PDF 正文标题前加了 Nemotron-Labs；仅有 v1。
- **MMAU 口径**：本篇引用的是 MMAU test 集（v05.15.25），[[StepAudio2语音旗舰]] 引用的是 test-mini，两篇的 Audio Flamingo 3 数字不同，不能横向比较。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[QwenOmni音视频原生]] | 对照：Qwen2.5-Omni 在 Table 1 中作为开放权重对照；两者都把音视 token 按时间交错，Qwen 系用 TMRoPE，本篇用 CRTE | Thinker–Talker 与 Qwen-Omni 产品线 |
| [[SpeechLLM语音语言模型]] | 上游：Whisper 系编码器接 LLM 的音频理解骨架在那篇，本篇的 AF-Whisper 沿用同一思路并加入视频 | 纯音频模型的训练 |
| [[StepAudio2语音旗舰]] | 对照：那篇是音频入、音频出的端到端语音对话模型，本篇是音视入、文本出（语音合成可选）的联合理解模型；两篇的 MMAU 口径不同 | 语音对话与副语言 |
| [[多模态架构脉络]] | 上游：Flamingo 到 LLaVA 的视觉语言模型史在那篇，本篇是加入音频的长视频分支 | 视觉语言模型通史 |
| [[SiLVR与ChainOfFrames]] | 对照：同样面向长时真实音视频理解，那篇用现成语音识别与描述模型外接推理 LLM，本篇训练一个联合模型 | 视频推理框架 |
| [[GRPO与DAPO算法族]] | 方法：AVF-Think 的后训练用 GRPO，组大小 5 | GRPO 的推导与变体 |
| [[视频生成模型脉络]] | 辨析：那篇的音视频联合生成与本篇的音视频联合理解方向相反 | 视频生成 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [AV-Flamingo](https://arxiv.org/abs/2607.16107) §1、Figure 2 | 三个缺口与五部件架构 |
| 2 | [AV-Flamingo](https://arxiv.org/abs/2607.16107) §2.2–2.3、Table 6 | 数据构造、三阶段课程与消融 |
| 3 | [OmniVinci](https://arxiv.org/abs/2510.15870) | 初始化来源的对齐模块与时间嵌入 |
| 4 | [Audio Flamingo 3](https://arxiv.org/abs/2507.08128) | AF-Whisper 与流式语音合成 |
| 5 | [NVIDIA/audio-flamingo](https://github.com/NVIDIA/audio-flamingo) | 官方代码仓 |
| 6 | [nvidia/audio-visual-flamingo-hf](https://huggingface.co/nvidia/audio-visual-flamingo-hf) | 模型权重页（Hugging Face） |
