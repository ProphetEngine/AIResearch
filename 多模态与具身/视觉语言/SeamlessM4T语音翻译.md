---
title: "Speech translation / simultaneous：SeamlessM4T 及流式同传族"
topic: SeamlessM4T语音翻译
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2308.11596
 - https://doi.org/10.1038/s41586-024-08359-z
 - https://arxiv.org/abs/2312.05187
arxiv: ["2308.11596", "2312.05187"]
doi: ["10.1038/s41586-024-08359-z"]
related: ["SpeechLLM语音语言模型", "多语言与跨语种", "QwenOmni音视频原生", "StepAudio2语音旗舰"]
retrieval_cutoff: 2026-04-21
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# Speech translation / simultaneous：SeamlessM4T 及流式同传族

> **主要来源**：[SeamlessM4T: Massively Multilingual & Multimodal Machine Translation](https://arxiv.org/abs/2308.11596)（Seamless Communication，Meta，v1 2023-08-22，v3 2023-10-25）；Nature 定稿 [Joint speech and text machine translation for up to 100 languages](https://doi.org/10.1038/s41586-024-08359-z)（2025-01-15 在线发表）；[Seamless: Multilingual Expressive and Streaming Speech Translation](https://arxiv.org/abs/2312.05187)（v1 2023-12-08）（截至 2026-04-21）。
> **研究线**：架构思想（主：自监督语音编码器 → 多任务到文本 → 两遍解码出语音单元 → 声码器；流式同传的单调注意力策略）；评测字段（辅：BLEU、ASR-BLEU、延迟指标）
> **范围与相邻笔记**：
> - ≠ [[SpeechLLM语音语言模型]]：那篇是音频进、文本出的对话 LLM；本篇是语音与文本互译的翻译基础模型，不是聊天助手。
> - ≠ [[QwenOmni音视频原生]]：本篇的「流式」指同传的读写策略，不是全模态对话里的流式语音合成。
>
> **意义**：传统语音翻译是识别、翻译、合成三段级联，误差层层叠加，且多数系统只擅长译成英语。SeamlessM4T 用一个模型同时做语音到语音、语音到文本、文本到语音、文本到文本翻译与语音识别，覆盖约百种语言，在多项翻译基准上超过最强的级联系统，并开源模型、对齐数据元信息与训练配方；随后的 Seamless 系列用非自回归单元解码与单调注意力，把离线翻译推进到边听边译的低延迟同传，并保留说话人的语速与停顿。它是「通用语音翻译机」第一次以开源单模型的形式接近可用。

---

## 一、问题背景

文本机器翻译已覆盖 200 多种语言（NLLB），语音翻译却远远落后：语音平行数据稀缺，级联系统难以扩展，而且多数系统偏向「译成英语」，从英语译出和低资源语种都弱（SeamlessM4T §1–2；Nature 开篇）。直接语音翻译模型要同时解决三件事：语音表征、跨语种对齐数据、以及从文本生成语音。同传还要再加一条：不等说话人讲完就开始输出，在延迟与质量之间取舍（Seamless §1–2）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2021-08 | [w2v-BERT](https://arxiv.org/abs/2108.06209) | 对比学习加掩码预测的语音自监督预训练，SeamlessM4T 的语音编码器沿此扩展 |
| 2022-07 | [NLLB](https://arxiv.org/abs/2207.04672) | 200 种语言的文本翻译模型，SeamlessM4T 的文本翻译块由此初始化 |
| 2022-12 | [UnitY](https://arxiv.org/abs/2212.08055) | 两遍直接语音翻译：先生成文本，再由文本生成离散语音单元 |
| 2023-08 | SeamlessM4T | 单一 UnitY 多任务模型覆盖约百种语言的五类任务 |
| 2023-12 | [EMMA](https://arxiv.org/abs/2312.04515) | 数值稳定、可并行训练的单调多头注意力同传策略 |
| 2023-12 | Seamless | SeamlessM4T v2（UnitY2）、表现力保持与流式同传合为一体 |
| 2025-01 | Nature 定稿 | 以 SeamlessM4T 为对象的刊发版，覆盖口径改为 101 种语音输入 |

## 三、方法

### 3.1 SeamlessM4T（§3–4）

- **语音编码器**：w2v-BERT 2.0，24 层 Conformer、约 6 亿参数，在 100 万小时、143 种以上语言的开放语音上自监督预训练（§4.1）。
- **对齐数据**：用句级多模态嵌入 SONAR 从网络语音与文本中自动挖掘平行对，得到 SeamlessAlign（超过 47 万小时，开源其元数据）；与人工标注和伪标注数据合并后，训练用数据共约 40.6 万小时（§3、摘要）。
- **多任务到文本（X2T）**：语音编码器与文本编码器共用一个文本解码器，联合训练语音识别、语音到文本与文本到文本翻译（§4.2）。
- **语音输出**：冻结 X2T，只训练文本到单元模块；推理时先生成文本假设，再生成离散单元，最后由多语种 HiFi-GAN 声码器转成波形（§4.3）。

### 3.2 Seamless 系列（Seamless §3–6）

- **SeamlessM4T v2**：SeamlessAlign 再增 114,800 小时，覆盖 76 种语言；UnitY2 把第二遍单元解码改为非自回归，并按子词 → 字符 → 单元逐层上采样。最好的非自回归单元模型比最好的自回归模型 ASR 词错率低 35%（§3.3），且生成速度更适合流式。
- **SeamlessExpressive**：在翻译中保留语速、停顿与音色风格（§4）。
- **SeamlessStreaming**：用 EMMA 在每步决定「再读一段」还是「写出译文」：由逐步概率递推单调对齐，加入期望延迟正则防止退化成等整句再译；新语音块到达时重跑编码器，解码器超过阈值才输出，非自回归单元模块随即合成语音（§5.1）。
- **Seamless**：把流式与表现力合成一个实时系统（§6）。

## 四、结果

| 工作 | 评测 | 结果 |
|---|---|---|
| SeamlessM4T-Large（2.3B） | Fleurs 语音到文本，译成英语（摘要、§1） | 比此前最好的直接模型 AudioPaLM-2-8B-AST 高 4.2 BLEU（约 20%）；比 Whisper-Large-v2 + NLLB-3.3B 级联高 1.3 BLEU |
| SeamlessM4T-Large | Fleurs 语音到语音，译成英语（§4.4.1） | 比三段级联（Whisper-Large-v2 + NLLB-3.3B + YourTTS）高 2.6 ASR-BLEU |
| SeamlessM4T-Large | CVSS 语音到语音（Table 15） | ASR-BLEU 36.5，两段级联（Whisper-Large-v2 + YourTTS）为 22.6 |
| SeamlessM4T-Large | 鲁棒性（摘要） | 背景噪声与说话人变化下，语音到文本平均比此前最好模型好 38% 与 49% |
| SeamlessM4T | 新增毒性（摘要、§1） | 各条件下 0.11%–0.21%，比当时最好模型降低 26%–63% |
| SeamlessStreaming | 高资源语种译成英语，文本输出（Table 31） | 相对离线 v2 的 BLEU 损失 10.1%，平均延迟（AL）1.75 秒 |
| SeamlessStreaming | 高资源语种译成英语，语音输出（Table 32） | ASR-BLEU 损失 16.0%，译语音结束比源语音晚 2.25 秒 |

Nature 摘要的口径是：相对最强级联，语音到文本与语音到语音的 BLEU 最多分别高 8% 与 23%，鲁棒性平均高约 50%。

## 五、意义

SeamlessM4T 表明大规模多语语音翻译可以由单一模型完成，并在质量、鲁棒性和安全上同时超过级联；它开源的对齐数据元信息、模型与评测工具（如跨模态质量估计 Blaser 2.0）成为后续语音翻译研究的公共底座。Seamless 系列则把「翻译得准」扩展到「译得快、像本人在说」，为实时跨语种交流铺路。与通用全模态助手相比，它代表专用翻译模型路线：语种覆盖更广、评测更系统，但不做开放对话。

## 六、局限与待核实

- **以英语为中心**：成对数据大多绕英语，非英语方向与低资源语种仍弱；SeamlessStreaming 在零样本方向 BLEU 损失达 31.4%，延迟却极小，作者解释为过度生成的迹象（Seamless Table 31）。同传质量也随语系不同：与英语相近的意大利语族、日耳曼语族滞后更低，汉语族、日语族等更难（Seamless §5.3）。
- **评测依赖 ASR**：语音输出用 ASR-BLEU 评，受识别误差影响；Blaser 2.0 与人工评测是补充而非替代。
- **CVSS 领先幅度口径不一**：SeamlessM4T v3 摘要写领先两段级联 58%，§1 写 8.5 分（50%），§4.4.1 写 14 分，Table 15 为 36.5 对 22.6；本篇按 Table 15。
- **arXiv 与 Nature 覆盖口径不同**：arXiv Table 2 写语音到语音为 100 → 英语、英语 → 35；Nature 摘要写 101 → 36，文本翻译 96 种。两版数字不能混用。
- **许可**：Nature 摘要写明所有成果仅供非商业用途。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[SpeechLLM语音语言模型]] | 对照：那篇是 Whisper 编码器接 LLM 的音频对话模型，输出文本；本篇是专门的语音翻译模型，能直接输出语音 | 语音 LLM 的训练与评测 |
| [[多语言与跨语种]] | 背景：那篇讲多语共享表征中高低资源语种的此消彼长，本篇在语音翻译上遇到同样问题，低资源与非英语方向更弱 | XLM-R、BLOOM 与语种配比 |
| [[QwenOmni音视频原生]] | 对照：Qwen-Omni 是能流式说话的通用全模态助手，语音输出约 10–36 种语言；本篇专做翻译，语种覆盖更广 | Thinker–Talker 与 ARIA |
| [[StepAudio2语音旗舰]] | 对照：Step-Audio 2 把中英语音翻译作为能力之一，用 CoVoST 2 与 CVSS 评测；本篇是以翻译为主轴的百语模型 | Step-Audio 2 架构 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [SeamlessM4T](https://arxiv.org/abs/2308.11596) §1、§4、Table 15 | 动机、模型构件与对级联的比较 |
| 2 | [Nature 版](https://doi.org/10.1038/s41586-024-08359-z) | 刊发口径的覆盖与主结果 |
| 3 | [Seamless](https://arxiv.org/abs/2312.05187) §3.3、§5 | UnitY2 与 EMMA 同传 |
