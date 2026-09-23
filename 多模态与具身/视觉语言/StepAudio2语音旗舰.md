---
title: "语音旗舰：Step-Audio 2 Technical Report（≠ Qwen-Omni / ≠ Speech-LLM 入门）"
topic: StepAudio2语音旗舰
date: 2026-09-22
lines: [架构思想, 训练数据接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2507.16632 # 872,404 B ≈ 0.83MiB / 21p；≪20MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2507.16632
 - https://arxiv.org/pdf/2507.16632
 - https://github.com/stepfun-ai/Step-Audio2
arxiv: ["2507.16632"]
related: ["SpeechLLM语音语言模型", "QwenOmni音视频原生", "SeamlessM4T语音翻译", "多模态架构脉络"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 语音旗舰：Step-Audio 2 Technical Report（≠ Qwen-Omni / ≠ Speech-LLM 入门）

> **定位**：语音旗舰切片——StepFun Audio Team *Step-Audio 2 Technical Report*（arXiv:**2507.16632v3** \[cs.CL\]，页眉 **27 Aug 2025**）。立「**非 Qwen 系**、工业强度端到端 **音→交织音文 token→波形**」旗舰 TR：latent 音频编码器 + 适配器 + 单 LLM 解码器输出 **离散文本/音频交织 token**，再经 CosyVoice 2 tokenizer 系 detokenizer（Flow Matching + HiFi-GAN）；并接 **RAG / 工具调用**（含独有 **audio search**）。
> **攻坚线**：**架构思想 / 训练数据接口（主）** + **文内 ASR / 副语言 / MMAU / 翻译 / Toolcall / URO-Bench 字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[SpeechLLM语音语言模型]]**：禁止重写 Speech-LLM **入门**（Qwen2-Audio：Whisper 编码器 ⊕ LLM **只出文本**、Voice Chat / Audio Analysis 接口表、三阶段训练全文）。本卡对象是 **音入 + 音文交织出** 的端到端对话旗舰，不是「音频理解→文本」栈入门。
> - **≠ [[QwenOmni音视频原生]]**：禁止写成 **Qwen3/3.5-Omni Thinker–Talker** 复述（AuT、TM-RoPE、多码本 RVQ+MTP、ARIA、首包延迟产品卡）。Step-Audio 2 是 **单 LLM 解码器 + 固定比交织 token**，文内对比 Qwen-Omni / Qwen2.5-Omni 仅作 **基线表**，不展开 Omni 架构正文。
> - **≠ [[SeamlessM4T语音翻译]]**：禁止写成 SeamlessM4T / UnitY **百语翻译 FM + EMMA 同传**通史。本卡 CoVoST 2 / CVSS 只作 **中英双向** 评测字段；翻译不是主架构轴。
> - **≠ [[多模态架构脉络]]**：禁止重写 CLIP→Flamingo→LLaVA→「原生多模态」**视觉—语言通史**；本卡主轴是 **语音/音频 LALM**，视觉不在范围。
> - **禁止 Omni Thinker–Talker 复述**：不得把 Step 的编码器–适配器–LLM–detokenizer 改写成 Thinker/Talker 双塔叙事。
> **禁止编造**：参数量（全文 **未**给出 Step-Audio 2 完整总参，仅称少于 Step-Audio 的 **130B**）、未表格化图点、未公开超参网格 → **不得外推**。主张与表数字一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文** | StepFun Audio Team, *Step-Audio 2 Technical Report* | arXiv:**2507.16632v3** \[cs.CL\] **27 Aug 2025**；XMP MetadataDate 2025-08-28T01:06:32Z（→ **2025-08-28 09:06 CST**）；许可证 arXiv nonexclusive-distrib/1.0；`https://arxiv.org/abs/2507.16632`（**872,404 B ≈ 0.83MiB** / **21** 页 letter） | 主锚：架构 + 预训练/SFT/RL + 评测 + mini 附录 |
| **代码入口（文内明示）** | stepfun-ai/Step-Audio2 | https://github.com/stepfun-ai/Step-Audio2 | 开源入口；含 StepEval 基准与 mini 权重叙事（本篇不跟 commit） |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| 主 PDF | `https://arxiv.org/abs/2507.16632` | **0.83MiB** | **21** | **官方 HTTPS 外链**（远低于 20MB；页数适中） |
| 全文抽取 | | ~1117 行 | — | 全文检索 |

**谱系一句（不升主）：** 同系前作 **Step-Audio**（Huang et al., arXiv:2502.11946）与 **Step-Audio-AQAA**（arXiv:2506.08967）被文内称为「以离散音频 token 统一理解与生成、约 **130B**」的先例；Step-Audio 2 **参数更少**，并把 **音频 token 生成进一步并入语言建模**。细节以本 TR 为准，不另开卡。

**一句话抓手：**
原始音频 → **冻结 25 Hz 编码器** → **2× 下采样适配器（12.5 Hz）** → **LLM 输出文本/音频交织离散 token** → **CosyVoice 2 tokenizer + Flow Matching + HiFi-GAN** 出波形；训练侧 **1.356T token 续预训练（21 天）+ 4B SFT + PPO×2 + GRPO**；推理侧可调 **web / audio search** 等工具做多模态 RAG。

---

## 二、议题边界：端到端语音旗舰 ≠ 入门 Speech-LLM ≠ Omni 产品卡 ≠ 翻译 FM

### 2.1 四向对照（跟读）

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[SpeechLLM语音语言模型]] Qwen2-Audio** | 「音频连续特征条件 LLM → **文本**」是前置轴 | Whisper 初始化、40 ms/帧公式、三阶段与 Voice Chat 接口全文 |
| **[[QwenOmni音视频原生]] Qwen Omni** | 表内 **Qwen-Omni / Qwen2.5-Omni** 作竞品基线 | Thinker–Talker、AuT、RVQ+MTP、ARIA、首包延迟产品叙事 |
| **[[SeamlessM4T语音翻译]] SeamlessM4T** | S2ST/S2TT 作为 **能力面之一** | UnitY / SeamlessAlign / EMMA / 百语覆盖通史 |
| **[[多模态架构脉络]] 视觉多模态** | 「多模态助手」产品默认语境一句 | CLIP/Flamingo/LLaVA 脉络重写 |

### 2.2 能力面（文内自我定位）

`
输入：原始音频（+ 历史音文特征）
输出：离散文本 token ⊕ 离散音频 token（固定比交织，末尾 padding）
波形：audio detokenizer（Flow Matching Mel → HiFi-GAN）
增强：RAG + 工具（audio search / 日期时间 / 天气 / web search）
`

相对文内点名的既有 LALM 缺口（§1）：多数模型或 **只对齐语义忽略副语言**，或 **能理解副语言却只出文本**，或 **幻觉 / 音色风格选择有限、缺真实世界音文知识接入**。Step-Audio 2 的回应是：**潜空间编码 + 推理中心 RL + 交织音频 token 生成 + 工具/RAG**。

---

## 三、架构思想（主读）

### 3.1 四件套（Figure 3 / §3.1）

| 组件 | 文内要点 |
|---|---|
| **Audio Encoder** | 在 ASR、说话人年龄/性别、音频事件检测等多种理解任务上预训练；输出帧率 **25 Hz**；**整个训练过程冻结** |
| **Audio Adaptor** | 下采样率 **2** → 有效帧率 **12.5 Hz**；连接编码器与 LLM |
| **LLM Decoder** | 直接吃适配器潜特征；输出 **文本与音频离散 token 的交织序列**；历史轮次把输入音频特征与输出交织序列 **pre-fill** 进下一轮 |
| **Audio Detokenizer** | 与 Step-Audio / AQAA 同族：**Flow Matching → Mel**，再 **HiFi-GAN → 波形**；Flow-Matching 在 transformer 块每个 self-attention 后加 **CNN 编码层**，于 **200,000 小时** 高质量语音上训练 |

**音频 tokenizer：** 采用 **CosyVoice 2** [19] 的 tokenizer；文本/音频 token 按 **固定比例交织**，不足则末尾 padding；再从交织序列抽出音频 token 送 detokenizer。

**部署：** 沿用 Step-Audio / AQAA 基建，含 **VAD** 滤输入，支撑实时语音对话（§3.1 末）。

### 3.2 与「Thinker–Talker」的硬区分（防滑）

| 维度 | Step-Audio 2（本卡） | Qwen2.5-Omni 类（[[QwenOmni音视频原生]]，仅对照） |
|---|---|---|
| 生成侧组织 | **单一 LLM** 自回归出 **交织** 音文 token | Thinker 出文本侧表示 / Talker 出语音 codec |
| 音频入 | 冻结 latent encoder + adaptor适配器 | AuT 等可训音频编码器叙事（不在此展开） |
| 波形头 | CosyVoice 2 系 + Flow Matching + HiFi-GAN | 多码本 RVQ + MTP + Code2Wav 等（不在此展开） |
| 知识接入 | **显式工具 / RAG**（含 audio search 换音色） | 产品卡另述；本卡不借用其接口表 |

### 3.3 工具与 audio search（§3.1）

文内设计的工具：用显式或隐式语音指令检索 **音频、当前日期时间、天气预报、网页内容**。
**Audio search（自称 LALM 独有）：** 语音库规模为 **数十万** 条语音及其转写与描述；检索到的语音可让模型 **模仿说话风格或切换音色**。推理时，检索信息 **接在输入音频特征之后**、再生成语音输出。

---

## 四、训练数据接口（主读）

### 4.1 总口径（文内两套并行说法，不调和编造）

| 口径 | 文内表述 | 位置 |
|---|---|---|
| **小时 + 文本 token** | 「**680B** tokens of text data and **8 million hours** of real and synthesized audio」 | §1 末 / Conclusion 亦写 8M hours |
| **续预训练 token 账** | 文本 LLM 初始化后，在 **1.356T** 文本+音频 token 上续预训练 **21 天** | §3.2 开篇 |
| **Abstract** | 「millions of hours of speech and audio data」 | 摘要 |

跟读原则：小时数与 T 级 token 是 **不同计量**；本卡 **并列转述**，不把 8M hours 换算成 token。

### 4.2 预训练四段（§3.2）

1. **适配器对齐**
 - **100B** ASR token；**冻结** 编码器与 LLM，只训适配器；**12K** steps；序列长 **8,192**；lr $10^{-4}\to 2\times10^{-5}$。

2. **扩词表 + 保文本能力**
 - 文本 tokenizer 扩展 **6.6K** 音频 token；再训 **128B** 文本 + **128B** 音频。
 - 音频侧细分：**80B TTS / 32B speech-to-speech conversation / 16B utterance-level text-speech interleaved continuation**。
 - 序列长 **16,384**；LLM / 适配器 / embedding / output 的 lr 分别为 $2\times10^{-5},\ 5\times10^{-5},\ 5\times10^{-5},\ 4\times10^{-5}$。

3. **主预训练（再 +800B）**
 - 统一 lr $2\times10^{-5}$；**400B** 文本 + 音频任务混合：**42B ASR / 120B TTS / 8B S2TT / 30B T2ST / 5B speech-to-text continuation / 45B utterance-level 交织续写 / 150B speech-to-speech conversation**。

4. **Cooldown（再 +200B 高质量）**
 - 音频：**24.6B** 多语/方言 ASR、**12.4B** TTS、**2.4B** 副语言理解、**3.6B** S2TT；合成管线再造 **6B** S2ST、**15B** 交织对话、**36B** speech-to-speech conversation。
 - 合成参考约 **50k** 独特说话人；另配 **100B** 高质量文本；lr $2\times10^{-5}\to 5\times10^{-6}$。

### 4.3 SFT（§3.3）

- **4B** 文本+音频 token，**单 epoch**；lr $10^{-5}\to10^{-6}$。
- 数据接口要点：GigaSpeech / WenetSpeech 等强化多语多方言 ASR；AudioSet / AudioCaps 改写成语音 QA；自建 **详细 speech captioning**（覆盖 **11** 个副语言/环境维度）；TTS 用内部专业标注；CoVoST 2 中英子集做 S2ST；文本对话经多 LLM 改写为口语脚本并随机插入情绪/语速指令后再合成；每类外部工具约 **1K** 对话脚本再合成。
- **推理冷启动：** 两套 reasoning-centric 数据——复杂声学混合理解，以及带情绪描述的合成对话；再用具备推理能力的文本 LLM 生成带 **逐步推理轨迹** 的 QA。

### 4.4 RL（§3.4）

多阶段强化，服务「音频理解 + 语音交互」推理：

| 阶段 | 算法 | 奖励 / 规模（文内） |
|---|---|---|
| 1 | **PPO** | **二元**奖励：思考序列长度既非空也不过长 → 1，否则 0；**60** iter；global batch **64**；actor lr $1\times10^{-6}$，critic $2.5\times10^{-6}$ |
| 2 | **PPO** | 改为 **学得偏好打分**（训练好的 reward model）；再 **120** iter；batch/lr 同上 |
| 3 | **GRPO** | 再 **400** iter，强化音频感知 |

**跟读注意（不编造修正）：** 正文 PPO/GRPO 均标引用 **[54]**，而文末 References [54] 条目为 Rafailov et al. *Direct preference optimization*——属文内引用与书目不一致；本卡只记 **算法名与超参**，不替作者改引用。

---

## 五、评测字段（辅读，表内数字）

评测协议要点：多数 ASR **不指定语言**（脚注：Qwen-Omni 无语言无关测法，指定语言可能更好）；GPT-4o 系在 ASR 用 **gpt-4o-transcribe**，其余多用 **gpt-4o-audio-preview-2025-06-03**；Kimi-Audio 因常忽略翻译提示被排除出翻译评测。

### 5.1 ASR（Table 1）— Step-Audio 2 均值

| 类别 | Step-Audio 2 | 文内主张对照 |
|---|---|---|
| English WER avg | **3.14** | 优于所列开源/商用（含 Doubao LLM ASR 6.17、GPT-4o Transcribe 4.50、Kimi 4.18、Qwen-Omni 5.35） |
| Chinese CER avg | **3.08** | 优于同列（Doubao 3.81、Kimi 3.75、Qwen-Omni 4.81；GPT-4o Transcribe 14.05） |
| In-house 口音/方言 CER avg | **8.85** | 显著低于同列（Doubao 14.66、Kimi 25.52、Qwen-Omni 19.40、GPT-4o Transcribe 40.49） |
| 多语单点 | Arabian 14.22；yue 7.90；Japanese 3.18 | 称与 GPT-4o Transcribe（阿/日）或 Qwen-Omni（粤）可比 |

### 5.2 副语言：StepEval-Audio-Paralinguistic（Table 2）

自建 **550** 条、**11** 维单轮 QA；协议：ASR 转写输出 → 文本 LLM 自动判定；代码与测试集放 GitHub。
**Avg：** Step-Audio 2 **83.09** vs GPT-4o Audio 43.45 / Kimi 49.64 / Qwen-Omni 44.18 / Step-Audio-AQAA 36.91。

### 5.3 MMAU（Table 3，v05.15.25 test-mini）

| Model | Avg | Sound | Speech | Music |
|---|---|---|---|---|
| Step-Audio 2 | **78.0** | **83.5** | **76.9** | 73.7 |
| Omni-R1 | 77.0 | 81.7 | 76.0 | 73.4 |
| Audio Flamingo 3 | 73.1 | 76.9 | 66.1 | 73.9 |
| Qwen2.5-Omni | 71.5 | 78.1 | 70.6 | 65.9 |

文称 sound/speech 最优，music 与最优持平量级。

### 5.4 翻译（Table 4）

| 基准 | Step-Audio 2 Avg | 对照高点 |
|---|---|---|
| CoVoST 2 S2TT BLEU | **39.26**（en→zh 49.01 / zh→en 29.51） | Qwen2.5-Omni 35.40；GPT-4o Audio 29.61 |
| CVSS S2ST BLEU | **30.87**（en→zh 34.83 / zh→en 26.92） | Step-Audio-AQAA 27.36；GPT-4o Audio 23.68；Qwen-Omni 15.35 |

### 5.5 Tool calling：StepEval-Audio-Toolcall（Table 5）

自建中文语音多轮；与 **Qwen3-32B（文本输入）** 对照。Trigger Precision/Recall 示例：Audio search 上 Step **86.8 / 99.5** vs Qwen3 **67.5 / 98.5**；Type/Parameter Accuracy 多维接近或持平。文强调：**在语音输入下**工具调用精度可与文本 LLM 相当，且 audio search 显著优于纯文本基线。

### 5.6 语音对话：URO-Bench（Table 6）

ASR 中介（Whisper）+ GPT-4o-mini 评判。
- **中文 Basic / Pro Avg：** Step-Audio 2 **83.32 / 68.25**（高于 GPT-4o Audio 78.59 / 67.10 等）。
- **英文 Basic / Pro Avg：** **83.90 / 66.07**（Basic 略低于 GPT-4o Audio 84.54，仍高于其他开源列）。

---

## 六、开源变体：Step-Audio 2 mini（Appendix B，不升主）

| 字段 | 文内 |
|---|---|
| 编码器 | **Qwen2-Audio** 的 encoder |
| 初始化 | **Qwen2.5-7B** |
| 数据 | 与 Step-Audio 2 **同一数据集**；工具仅限 **web search** |
| 定位 | 更利于与 Qwen-Omni / Kimi-Audio 等比参对照的开发者友好版 |
| 表内趋势 | ASR / 副语言 / MMAU / 翻译 / URO 多表与满血版接近（如 MMAU avg **73.2**；副语言 avg **80.00**；CoVoST avg **39.29**） |

满血版 **精确总参数未给出** → 不得用 mini 的 7B 反推满血 B 数。

---

## 七、可迁移结论与跟读口诀

1. **架构口诀：** `冻 25Hz 编码 → 2× 适配 12.5Hz → 单 LLM 交织音文 token → CosyVoice2 FM+HiFi-GAN`；**不是** Thinker–Talker。
2. **数据口诀：** 续预训练 **1.356T / 21 天**（四段：对齐→扩词表→主训→cooldown）；产品叙事另给 **8M 小时 + 680B 文本 token**。
3. **对齐口诀：** SFT 灌副语言 caption + 工具脚本 + 推理轨迹冷启动 → **PPO（长度二元→偏好 RM）→ GRPO**。
4. **产品差异点：** **audio search** 把「换音色/风格」做成可调用检索，而不只靠隐式生成。
5. **仓库位置：** 填补「非 Qwen 系开源语音旗舰 TR」空位；与 [[SpeechLLM语音语言模型]]（入门音→文）、[[QwenOmni音视频原生]]（Omni 产品卡）、[[SeamlessM4T语音翻译]]（翻译 FM）正交。

---

## 八、未写 / 待核实

- Step-Audio 2 **满血总参数、层宽、专家数**（若 MoE）——正文未给 → **待核实 / 不编造**。
- 交织固定比的具体数字、实时首包延迟毫秒数——正文未表格化 → **不读点**。
- PPO/GRPO 的 [54] 书目与算法名不一致——记为文内问题，不外补标准引用冒充原文。
- GitHub 权重/commit、商业 API 可用性——2026-09-22 **未做线上核验**。
- Figure 1 雷达图各轴精确读点——以 Table 1–6 为准。

---

## 九、来源与检索截止

- 主 PDF：`https://arxiv.org/abs/2507.16632`（2026-09-22 自 https://arxiv.org/pdf/2507.16632 拉取； **21** 页 / **872404** bytes）。
- 。
- 检索截止：**2026-09-22 CST**。
- 相邻划界：多模态与具身/视觉语言/SpeechLLM语音语言模型.md · 多模态与具身/视觉语言/QwenOmni音视频原生.md · 多模态与具身/视觉语言/SeamlessM4T语音翻译.md · 多模态与具身/视觉语言/多模态架构脉络.md。
