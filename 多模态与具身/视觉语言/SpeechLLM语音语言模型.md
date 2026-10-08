---
title: "Speech-LLM（语音-语言模型）深读：以 Qwen2-Audio 为锚"
topic: SpeechLLM语音语言模型
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2407.10759
 - https://qwenlm.github.io/blog/qwen2-audio/
arxiv: ["2407.10759"]
related: ["多模态架构脉络", "对齐脉络RLHF与偏好优化", "QwenOmni音视频原生", "StepAudio2语音旗舰", "SeamlessM4T语音翻译", "音视频联合Flamingo"]
archived: 2026-09-22
---

# Speech-LLM（语音-语言模型）深读：以 Qwen2-Audio 为锚

> **主要来源**：[Qwen2-Audio Technical Report](https://arxiv.org/abs/2407.10759)（Qwen Team，阿里巴巴，v1 2024-07-15）；[Qwen2-Audio: Chat with Your Voice!](https://qwenlm.github.io/blog/qwen2-audio/)（Qwen 官方博文，2024-08-09）（截至 2026-07-17）。
> **研究线**：架构思想（音频编码器的连续特征接入 LLM、只输出文本）
> **范围与相邻笔记**：
> - ≠ [[QwenOmni音视频原生]]、[[StepAudio2语音旗舰]]：那两篇的模型能直接输出语音，本篇只写「音频入、文本出」一代。
> - ≠ [[多模态架构脉络]]：那篇以视觉为主线，本篇是与之平行的音频一支。
>
> **意义**：让大模型「听懂」声音，最早的做法是先用语音识别转成文字再交给 LLM，口音、情绪、环境声在转写时就丢了。语音 LLM 改为把音频编码器输出的连续特征直接作为 LLM 的条件，Qwen2-Audio 是这一路线的代表：用 Whisper-large-v3 初始化编码器、接 Qwen-7B，预训练改用自然语言提示，再经监督微调与 DPO，一个模型就能既分析语音、环境声与音乐，又能直接听语音指令对话，在音频指令跟随基准 AIR-Bench 上超过 Gemini-1.5-pro。它确立了此后全模态模型沿用的「编码器 + LLM」骨架，也划出了这一代的边界：只出文本，不出语音。

---

## 一、问题背景

语音进入大模型有三种形态：识别—理解—合成的级联；音频编码器接 LLM、输出文本；同一模型直接输出语音。SpeechGPT 指出，当时的语音语言模型多采用级联范式，阻碍了跨模态的知识迁移（SpeechGPT 摘要）。第二种形态把音频当作 LLM 的连续输入，不经文字中转，因此能同时利用语音内容与非语言信息；Qwen2-Audio 的博文称，用户首次可以不经语音识别模块，直接用语音向音频语言模型下指令。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2022-12 | [Whisper](https://arxiv.org/abs/2212.04356) | 68 万小时多语言弱监督训练的语音识别模型，此后多数语音 LLM 用它的编码器 |
| 2023-05 | [SpeechGPT](https://arxiv.org/abs/2305.11000) | 用离散语音单元让 LLM 同时感知和生成语音，构造跨模态指令数据 |
| 2023-10 | [SALMONN](https://arxiv.org/abs/2310.13289) | 把语音与通用音频编码器接到文本 LLM，覆盖语音、音频事件与音乐 |
| 2023-11 | [Qwen-Audio](https://arxiv.org/abs/2311.07919) | 30 多种音频任务联合预训练，用层次化标签缓解任务间干扰 |
| 2024-07 | Qwen2-Audio | 预训练改用自然语言提示，加入语音聊天模式与 DPO |
| 2025-03 | [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) | Thinker–Talker 架构，开始流式输出语音（[[QwenOmni音视频原生]]） |
| 2025-07 | [Step-Audio 2](https://arxiv.org/abs/2507.16632) | 单一 LLM 输出交织的文本与音频 token（[[StepAudio2语音旗舰]]） |

## 三、方法

### 3.1 架构（§2）

模型由音频编码器和 LLM 组成，训练目标是以音频表示为条件预测下一个文本 token：$P_\theta(x_t \mid x_{<t}, \mathrm{Encoder}_\phi(a))$，其中 $a$ 是音频，$x$ 是文本，$\theta$、$\phi$ 分别是 LLM 与编码器的参数。

- **编码器**：与 Qwen-Audio 不同，改用 Whisper-large-v3 初始化。音频重采样到 16 kHz，转成 128 通道梅尔谱（窗长 25 ms、帧移 10 ms），再经步长为 2 的池化，编码器每帧约对应 40 ms 音频。
- **LLM**：仍为 Qwen-7B，模型总参数 8.2B。开源权重名为 Qwen2-Audio-7B 与 Qwen2-Audio-7B-Instruct（博文）。
- 论文没有写投影层结构及音频 token 如何与文本 token 拼接，只给出式 (1) 与 Figure 2 的示意。

### 3.2 两种交互模式（§1、§2）

- **音频分析**：用户提供语音、环境声、音乐或混合音频，指令可以是语音或文字，模型自行分辨音频中哪段是指令；多用于离线分析音频文件。
- **语音聊天**：把模型当语音助手自由对话，随时可改用文字；多用于在线交互。

两种模式在监督微调时联合训练，使用时不需要用系统提示切换。

### 3.3 三阶段训练（§2、Figure 2）

1. **多任务预训练**：用自然语言提示（如「Detect the language and recognize the speech:」）代替 Qwen-Audio 的层次化标签，并扩大数据量；作者称这样泛化和指令跟随更好。
2. **监督微调**：作者强调微调数据的质量与复杂度对性能影响很大，但未公开条数与配方。
3. **DPO**：用人工标注的好、坏回复对优化事实性与期望行为（摘要）。

## 四、结果

以下均为不做任务专用微调的结果（§3.2、Table 2）。

| 任务 | 评测 | Qwen2-Audio | 对照 |
|---|---|---|---|
| 英文识别 | LibriSpeech test-clean / test-other 词错率 | 1.6 / 3.6 | Qwen-Audio 2.0 / 4.2 |
| 中文识别 | Fleurs-zh 词错率（双方均为零样本） | 7.5 | Whisper-large-v3 7.7 |
| 中文识别 | Aishell2 Mic / iOS / Android | 3.0 / 3.0 / 2.9 | Qwen-Audio 3.3 / 3.1 / 3.3 |
| 语音翻译 | CoVoST2 en-zh / zh-en BLEU | 45.2 / 24.4 | Qwen-Audio 41.5 / 15.7 |
| 情感识别 | Meld 准确率 | 0.553 | Qwen-Audio 0.557 |
| 人声分类 | VocalSound 准确率 | 0.9392 | Qwen-Audio 0.9289 |
| 指令跟随 | AIR-Bench chat 语音 / 环境声 / 音乐 / 混合（GPT-4 打分 0–10） | 7.18 / 6.99 / 6.79 / 6.77 | Gemini-1.5-pro 6.97 / 5.49 / 5.06 / 5.27 |

摘要所说「超过 Gemini-1.5-pro 等此前最好模型」指的是 AIR-Bench 的音频指令跟随，不是 Table 2 每一项。

## 五、意义

Qwen2-Audio 把「编码器连续特征 + LLM 下一 token 预测」做成了可直接用语音交互的开源模型，并把 LLM 的后训练流程（指令微调、DPO）完整搬到音频上。用自然语言提示统一预训练任务，缩小了预训练格式与对话格式的差距。此后的全模态模型保留了这一骨架：Qwen2.5-Omni 直接沿用 Qwen2-Audio 的音频编码器、加上流式语音输出，Qwen3-Omni 再用自研的 AuT 替换 Whisper 编码器。

## 六、局限与待核实

- **只出文本**：模型接收音频与文本、输出文本，要语音回复仍需外接语音合成。
- **音频时长**：博文把「支持 30 秒以上更长音频」列为下一步计划，说明当时长音频能力有限；论文没有写最大时长。
- **对比条件不一**：Common Voice 15 上 Qwen2-Audio 不是零样本，Whisper 是零样本；AIR-Bench 上 Gemini-1.5 因安全拦截约少测 1/5 样本（§3.2）。
- **并非全面领先**：Meld 情感识别 0.553，略低于前代 Qwen-Audio 的 0.557。
- **数据未公开**：预训练各类数据的小时数只在 Figure 3 的柱状图中，正文没有给出数字；监督微调数据也未公开。博文称支持 8 种以上语言与方言，论文未给出语种清单。
- **评测集数量**：Figure 1 写覆盖 10 个数据集，§3.1 写评测涉及 13 个数据集。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[多模态架构脉络]] | 平行：那篇写视觉编码器接 LLM，本篇是同一做法在音频上的版本 | 视觉多模态通史 |
| [[对齐脉络RLHF与偏好优化]] | 方法：Qwen2-Audio 第三阶段用的 DPO 在那篇 | DPO 推导与变体 |
| [[QwenOmni音视频原生]] | 下游：Qwen2.5-Omni 沿用本篇的音频编码器并加上流式语音输出，Qwen3-Omni 起改用自研 AuT 替换 Whisper | Thinker–Talker 与全模态评测 |
| [[StepAudio2语音旗舰]] | 下游：Step-Audio 2 让单一 LLM 输出交织的音文 token，其开源 mini 版直接用 Qwen2-Audio 的编码器 | Step-Audio 2 训练与评测 |
| [[SeamlessM4T语音翻译]] | 对照：那篇是专门的多语语音翻译模型，本篇的语音翻译只是通用音频 LLM 的一项能力 | UnitY 与同传策略 |
| [[音视频联合Flamingo]] | 下游：那篇的音频编码器 AF-Whisper 同样基于 Whisper、采用相同的 16 kHz 与 128 通道梅尔谱前端，并加入视频 | 音视频联合训练 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Qwen2-Audio](https://arxiv.org/abs/2407.10759) §2、Figure 2 | 架构、两种模式、三阶段训练 |
| 2 | [Qwen2-Audio](https://arxiv.org/abs/2407.10759) Table 2 与 §3.2 | 结果与对比条件 |
| 3 | [Qwen2-Audio 博文](https://qwenlm.github.io/blog/qwen2-audio/) | 两种模式的演示与后续计划 |
| 4 | [[QwenOmni音视频原生]] | 加上语音输出之后的一代 |
