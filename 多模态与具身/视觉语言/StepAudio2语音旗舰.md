---
title: "语音旗舰：Step-Audio 2 Technical Report（≠ Qwen-Omni / ≠ Speech-LLM 入门）"
topic: StepAudio2语音旗舰
date: 2026-09-22
lines: [架构思想, 训练数据接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2507.16632
 - https://github.com/stepfun-ai/Step-Audio2
arxiv: ["2507.16632"]
related: ["SpeechLLM语音语言模型", "QwenOmni音视频原生", "SeamlessM4T语音翻译", "多模态架构脉络", "音视频联合Flamingo", "GRPO与DAPO算法族"]
retrieval_cutoff: 2026-07-17
timezone: Asia/Shanghai (CST)
---

# 语音旗舰：Step-Audio 2 Technical Report（≠ Qwen-Omni / ≠ Speech-LLM 入门）

> **主要来源**：[Step-Audio 2 Technical Report](https://arxiv.org/abs/2507.16632)（StepFun Audio Team，阶跃星辰，v1 2025-07-22，v3 2025-08-27）；[stepfun-ai/Step-Audio2](https://github.com/stepfun-ai/Step-Audio2)（代码、mini 版权重与自建评测集）（截至 2026-07-17）。
> **研究线**：架构思想（主：单一 LLM 解码器输出交织的文本与音频 token，接入检索与工具）；训练数据接口（续预训练、监督微调与强化学习的数据构成）；评测字段（辅：语音识别、副语言理解、MMAU、语音翻译、工具调用、语音对话）
> **范围与相邻笔记**：
> - ≠ [[SpeechLLM语音语言模型]]：那篇是「音频入、文本出」的入门，本篇的模型直接输出语音。
> - ≠ [[QwenOmni音视频原生]]：Qwen-Omni 在本篇只作对照基线，不展开 Thinker–Talker。
>
> **意义**：此前的开源语音大模型要么只对齐语音的语义、忽略语气和情绪，要么能理解这些信息却只会输出文字，还常有幻觉、音色单一。Step-Audio 2 把冻结的音频编码器接到单一 LLM 上，让 LLM 直接输出按固定比例交织的文本与音频 token，再用推理导向的强化学习和检索、工具调用补足知识，其中「音频检索」能按检索到的语音切换音色与说话风格。报告在中英文语音识别、自建副语言理解基准、MMAU、中英语音翻译和中文语音对话上超过 GPT-4o Audio、Kimi-Audio 与 Qwen-Omni 等对照，说明非 Qwen 系、单解码器的端到端语音对话也能做到工业强度。

---

## 一、问题背景

GPT-4o 开创了不经中间文字转换的端到端语音交互，此后出现大量开源语音大模型（§1）。作者指出三类缺口（§1）：Spirit LM、GLM-4-Voice 等主要把语音的语义对齐到文本，忽略副语言信息；Qwen-Audio、Qwen2-Audio 与 Audio Flamingo 系列能理解这些信息，却通常只输出文本，无法据此生成有表现力的语音回复；多模态建模复杂，模型常有幻觉，音色与说话风格选择有限，也缺少接入真实世界文本和声学知识的途径。同系前作 Step-Audio 与 Step-Audio-AQAA 已用离散音频 token 统一语音理解与生成，规模为 1300 亿参数；Step-Audio 2 参数更少（§1）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-07 | [Qwen2-Audio](https://arxiv.org/abs/2407.10759) | 音频编码器接 LLM，能理解副语言但只输出文本（[[SpeechLLM语音语言模型]]） |
| 2024-10 | [GPT-4o System Card](https://arxiv.org/abs/2410.21276) | 公开 GPT-4o 端到端语音交互的系统卡 |
| 2024-12 | [CosyVoice 2](https://arxiv.org/abs/2412.10117) | 流式语音合成，Step-Audio 2 用它的音频分词器 |
| 2025-02 | [Step-Audio](https://arxiv.org/abs/2502.11946) | 1300 亿参数的语音—文本统一模型，开源 Step-Audio-Chat |
| 2025-03 | [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) | Thinker–Talker 双模型流式输出语音（[[QwenOmni音视频原生]]） |
| 2025-04 | [Kimi-Audio](https://arxiv.org/abs/2504.18425) | 连续特征输入、离散 token 输出，超过 1300 万小时音频预训练 |
| 2025-06 | [Step-Audio-AQAA](https://arxiv.org/abs/2506.08967) | 端到端音频问答、音频回答 |
| 2025-07 | Step-Audio 2 | 单一 LLM 输出交织音文 token，接入检索与工具 |

## 三、方法

### 3.1 架构（§3.1、Figure 3）

| 组件 | 做法 |
|---|---|
| 音频编码器 | 在语音识别、说话人年龄与性别、音频事件检测等任务上预训练，输出 25 Hz，整个训练过程冻结 |
| 适配器 | 2 倍下采样到 12.5 Hz，连接编码器与 LLM |
| LLM 解码器 | 直接读入适配器输出的连续特征，输出按固定比例交织的离散文本与音频 token（不足时末尾补齐）；上一轮的输入音频特征与输出序列作为历史预填充到下一轮 |
| 音频去分词器 | LLM 输出的音频 token 用 CosyVoice 2 的分词器；去分词器与 Step-Audio 同族，由流匹配模块生成梅尔谱、HiFi-GAN 声码器转成波形；流匹配模块在每个自注意力后加一层卷积编码，在 20 万小时高质量语音上训练 |

部署沿用 Step-Audio 的基建，含语音活动检测模块，支持实时语音对话。

### 3.2 工具与音频检索（§3.1）

模型可用显式或隐式的语音指令调用工具，检索音频、当前日期时间、天气预报与网页内容。音频检索是作者称为语音大模型独有的工具：语音库含数十万条语音及其转写与描述，模型可据检索到的语音模仿说话风格或切换音色。推理时检索结果接在输入音频特征之后，再生成语音输出。

### 3.3 训练（§3.2–3.4）

- **续预训练**：从文本 LLM 初始化，在 1.356T 文本与音频 token 上续训 21 天，分四段：只训适配器的语音—文本对齐（100B 语音识别 token）；给文本分词器加入 6.6K 个音频 token，并用等量文本与音频数据（各 128B）保住文本能力；800B token 的主预训练，混合语音识别、语音合成、语音翻译、语音续写与语音对话等任务；200B 高质量数据的冷却阶段，其中语音翻译与语音对话数据由对话合成管线生成，参考约 5 万名不同说话人。报告另称全程用 6800 亿文本 token 与 800 万小时真实及合成音频训练（§1、§5），这与 1.356T token 的续预训练账是两种计量，不能互相换算。
- **监督微调**：4B token 单轮训练。自建详细语音描述任务，覆盖 11 个副语言与环境维度；文本对话由多个 LLM 改写成口语脚本，随机插入情绪与语速指令后合成为语音；每类工具约 1K 条对话脚本。另构造两套推理数据（复杂声学混合理解、带情绪描述的合成对话），由会推理的文本 LLM 生成逐步推理轨迹，作为强化学习的冷启动。
- **强化学习**：两段 PPO 再接 GRPO。第一段用二元奖励把思考长度限制在既不为空也不过长；第二段改用训练好的奖励模型打分；最后用 GRPO 进一步提高音频感知能力。

## 四、结果

| 评测 | Step-Audio 2 | 对照 |
|---|---|---|
| 语音识别：英文平均词错率 / 中文平均字错率（Table 1） | 3.14 / 3.08 | GPT-4o Transcribe 4.50 / 14.05，Kimi-Audio 4.18 / 3.75，Qwen-Omni 5.35 / 4.81 |
| 语音识别：自建四种口音与两种方言平均字错率（Table 1） | 8.85 | 豆包 LLM ASR 14.66，Qwen-Omni 19.40 |
| 副语言理解：StepEval-Audio-Paralinguistic，550 条、11 个维度（Table 2） | 83.09 | Kimi-Audio 49.64，Qwen-Omni 44.18，GPT-4o Audio 43.45 |
| MMAU v05.15.25 test-mini 平均（Table 3） | 78.0 | Omni-R1 77.0，Audio Flamingo 3 73.1，Qwen2.5-Omni 71.5 |
| 中英语音转文本翻译：CoVoST 2 平均 BLEU（Table 4） | 39.26 | Qwen2.5-Omni 35.40，GPT-4o Audio 29.61 |
| 中英语音到语音翻译：CVSS 平均 BLEU（Table 4） | 30.87 | Step-Audio-AQAA 27.36，GPT-4o Audio 23.68 |
| 工具调用：音频检索的触发精确率 / 召回率（Table 5） | 86.8 / 99.5 | Qwen3-32B（文本输入）67.5 / 98.5 |
| 语音对话：URO-Bench 中文 Basic / Pro（Table 6） | 83.32 / 68.25 | GPT-4o Audio 78.59 / 67.10 |
| 语音对话：URO-Bench 英文 Basic / Pro（Table 6） | 83.90 / 66.07 | GPT-4o Audio 84.54 / 67.51 |

开源的 Step-Audio 2 mini 改用 Qwen2-Audio 的编码器、以 Qwen2.5-7B 初始化，用同一数据集训练、工具只保留网页搜索；其 MMAU 平均 73.2、副语言平均 80.00、CoVoST 2 平均 39.29（附录 B）。

## 五、意义

Step-Audio 2 表明不用 Thinker–Talker 双模型、只用一个 LLM 交织生成文本与音频 token，也能做出端到端的工业级语音对话；它把副语言理解当作一等目标，专门构造数据与评测。把「换音色」做成可调用的音频检索，而不只靠模型隐式生成，是语音助手接入外部知识与声学资源的一个新做法。

## 六、局限与待核实

- **参数量未公开**：报告只说参数少于 Step-Audio 的 1300 亿，没有给出总参数、层数或是否为 MoE；交织的固定比例与首包延迟也未给出。
- **版本间评测数字多数变动**：v1、v2 与 v3 的多数评测结果不同，例如副语言平均由 76.55 升到 83.09，英文与中文识别平均由 3.18 / 3.11 降到 3.14 / 3.08，URO-Bench 中文 Basic 由 78.86 升到 83.32，工具调用（Table 5）未变；v3 还新增了 mini 版附录。报告没有说明原因，本篇按 v3。
- **引用错误**：正文给 PPO 与 GRPO 标注的文献 [54]，在参考文献中是 DPO 论文。
- **自建评测**：副语言与工具调用两个基准都是作者自建。副语言用 ASR 转写模型输出、再由文本 LLM 判定；工具调用由 Qwen3-32B 自动判分，而对照基线也是 Qwen3-32B（文本输入）。URO-Bench 经 Whisper 转写、GPT-4o-mini 判分。
- **对照条件**：所有模型的语音识别都不指定语言，作者注明 Qwen-Omni 若指定语言可能更好；Kimi-Audio 因常忽略翻译提示被排除出翻译评测；英文语音对话上 Step-Audio 2 低于 GPT-4o Audio。
- **MMAU 不可跨篇直接比较**：本篇用 test-mini，[[音视频联合Flamingo]] 的 MMAU 表用 test 集，两篇里 Audio Flamingo 3 的分数不同。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[SpeechLLM语音语言模型]] | 上游：Qwen2-Audio 的「编码器接 LLM、只出文本」是本篇要补的缺口之一，mini 版直接用它的编码器 | Whisper 前端与三阶段训练 |
| [[QwenOmni音视频原生]] | 对照：Qwen-Omni 用 Thinker–Talker 双模型，本篇用单一 LLM 交织输出；Qwen-Omni 与 Qwen2.5-Omni 在本篇是基线 | Thinker–Talker、AuT 与全模态评测 |
| [[SeamlessM4T语音翻译]] | 对照：那篇是专门的多语语音翻译模型，本篇的语音翻译只测中英双向 | UnitY 与同传策略 |
| [[多模态架构脉络]] | 定位：那篇「全模态入、语音出」一条把本篇列为音频入、音文交织 token 出的端到端语音路线 | 视觉多模态通史 |
| [[音视频联合Flamingo]] | 对照：MMAU 基线中的 Audio Flamingo 3 是那篇音频编码器的来源，那篇把音频与长视频联合理解，语音输出为可选模块 | 音视频联合训练 |
| [[GRPO与DAPO算法族]] | 方法：本篇强化学习最后一段用的 GRPO 在那篇 | GRPO 目标与变体 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Step-Audio 2](https://arxiv.org/abs/2507.16632) §3.1、Figure 3 | 架构、交织输出与音频检索 |
| 2 | [Step-Audio 2](https://arxiv.org/abs/2507.16632) §3.2–3.4 | 续预训练四段、监督微调数据与强化学习 |
| 3 | [Step-Audio 2](https://arxiv.org/abs/2507.16632) §4、附录 B | 六类评测与 mini 版 |
| 4 | [[QwenOmni音视频原生]] | 另一种端到端语音输出架构 |
