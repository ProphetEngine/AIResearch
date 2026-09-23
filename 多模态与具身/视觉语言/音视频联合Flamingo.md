---
title: "开源音视频联合模型：Audio-Visual Flamingo / Nemotron-Labs-AV-Flamingo（≠ Qwen Omni / Speech-LLM / Seamless / 视频生成）"
topic: 音视频联合Flamingo
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2607.16107 # 9.7M / 47p；<20MB
arxiv: ["2607.16107"]
related:
 - "QwenOmni音视频原生"
 - "SpeechLLM语音语言模型"
 - "SeamlessM4T语音翻译"
 - "多模态架构脉络"
 - "视频生成正式报告"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 开源音视频联合模型：Audio-Visual Flamingo（Nemotron-Labs-AV-Flamingo）

> **定位**：开源音视频联合旗舰增量——补仓库在 **[[QwenOmni音视频原生]] Qwen Omni 产品线 TR** 之外仍缺的 **「非 Qwen 栈」开源长视频音视联合理解（AV-LLM）** 锚点。主文：Ghosh, Goel, et al., *Nemotron-Labs-Audio-Visual Flamingo: Open Audio-Visual Intelligence for Long and Complex Videos*（arXiv **2607.16107v1**）。
> **攻坚线**：**架构思想（主）**——OmniVinci 初始化 + SigLip/AF-Whisper + 时序交错与 CRTE + 三阶段课程 + TAVIT/AV-Think；**评测字段（辅）**——文内 Omni / Audio / Video / ASR 表（Table 1）与 AV-Skills 消融（Table 6）。
> **硬划界（开篇钉死）**：
> - **≠ [[QwenOmni音视频原生]] Qwen Omni**：禁止重写 Thinker–Talker MoE、AuT、ARIA、Qwen3/3.5-Omni 产品栈与 36/215 基准表；本卡仅在「同题相邻的闭源/开权 omni 对照」处点名，**不**展开 Qwen Omni 配方。
> - **≠ [[SpeechLLM语音语言模型]] Speech-LLM**：禁止重写 Qwen2-Audio / Whisper→LLM 音频→文本对话栈；本卡是 **音视频联合理解 + 可选流式 TTS**，不是 Voice Chat / Audio Analysis 接口史。
> - **≠ [[SeamlessM4T语音翻译]] SeamlessM4T**：禁止重写 UnitY / EMMA 语音翻译与同传；本卡 **不做** S2ST/S2TT 翻译 FM。
> - **≠ [[多模态架构脉络]] 多模态通史**：禁止重写 CLIP→Flamingo→LLaVA→「原生多模态」阶梯；经典 Flamingo（Alayrac 2022）仅作 related-work 一句祖先，**不**升主。
> - **≠ [[视频生成正式报告]] 视频生成正式报告备忘**：本卡是 **理解 / 推理 AV-LLM**，不是文生视频 / Sora 缺口备忘。
> **禁止编造**：参数量、小时数、表内 ACC/WER、训练超参一律锚定官方 PDF（2026-09-22 CST）；页眉 Code / Model / Project Page / Dataset / Demo **按钮在 PDF 二进制中未抽出可核 URI**（仅见 `arxiv.org/abs/2607.16107v1`）→ **不臆造 GitHub / HF 链接**；文内写「fully open」与 Broader Impacts「non-commercial research use only」**并列表出，不调和**。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主文** | *Nemotron-Labs-Audio-Visual Flamingo: Open Audio-Visual Intelligence for Long and Complex Videos* | arXiv:**2607.16107v1** \[eess.AS\] **17 Jul 2026**（页眉日期 **2026-7-20**）；https://arxiv.org/pdf/2607.16107 → `https://arxiv.org/abs/2607.16107` | **9.7M**（10,120,887 B） | **47** letter（抽取时有 PDF 结构警告，正文可抽） | （1628 行） |

| 字段 | 文内可核 |
|---|---|
| 作者 / 机构 | Sreyan Ghosh¹·²,∗、Arushi Goel¹,∗ 等；**¹ NVIDIA, USA** · **² University of Maryland, USA**（∗ Project-Leads；排序硬币决定） |
| 简称 | **AV-Flamingo** / **AVF**；变体 **AVF-Instruct**、**AVF-Think** |
| 版权行 | 「© 2026 NVIDIA. All rights reserved.」 |
| 开源主张（摘要 / 贡献 3） | 开源 **model、training、inference code** 及相关技术 |
| 许可边界（Appendix I Broader Impacts） | 释放 **AV-Flamingo 与 AV-Skills** 供 **non-commercial research use only**，并写明禁止有害用途；另有 **AV-Safety QA**（§A，92K QA / 536 hrs）在 long-context SFT 中保留拒绝行为 |
| 页眉按钮 | Code · Model · Project Page · Dataset · Demo —— **本环境对 PDF 做 URI/字符串扫描仅得 arXiv abs/DOI，无额外可核仓链** |

**体积判定**：`ls -lh` → **9.7M < 20MB** → 按验收规矩 ****。权重 / 数据集本体 **禁止**入库。

**一句话抓手：** 从 **OmniVinci** 检查点出发，用自建 **AV-Skills（≈7M caption+QA，含 ≈4.8M QA）** 做短→长三阶段课程，再用 **TAVIT（Temporal Audio-Visual Interleaved Chain-of-Thought）/ AV-Think（≈24K，推理链均长 635.7 词）** 做 SFT+**GRPO**，得到面向 **长、复杂真实音视频** 的开源 AV-LLM（骨干 **Qwen2.5-7B**）。

跟读口诀：

`
数据： AV-Skills-Short（≤60s，100K h，3.8M）→ AV-Skills-Long（60s–15min，~140K h，3.2M）→ AV-Think（24K TAVIT）
课程： Init OmniVinci → Short-SFT（≤5min / 16K）→ Long-SFT（≤15min / 32K）= AVF-Instruct
 → CoT SFT + GRPO = AVF-Think
架构： SigLip + Dynamic S2 ‖ AF-Whisper（30s 滑窗）→ MLP 适配 → 时序交错 + CRTE → Qwen2.5-7B
 （可选 streaming TTS，细节指向 Audio Flamingo 3）
`

---

## 二、议题边界：只写「开源长视频 AV 联合理解」，不写 Omni 产品线 / 语音翻译 / 视频生成

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[QwenOmni音视频原生]]** Qwen3/3.5-Omni | 文内把 Qwen-Omni / Qwen3.5-Omni 列为短片或开权 omni 对照；表内 Qwen2.5-O 等数字 | Thinker–Talker、AuT 小时数、ARIA、256k 产品叙事全文 |
| **[[SpeechLLM语音语言模型]]** Speech-LLM | 「音频可进 LLM」的相邻意识；基线表出现 Qwen2-Audio 等 | Whisper-large-v3 前端、三阶段 Voice Chat 配方 |
| **[[SeamlessM4T语音翻译]]** Seamless | 「语音可端到端」的压力面一句 | UnitY / SeamlessAlign / EMMA 同传 |
| **[[多模态架构脉络]]** | related work 中 Flamingo / LLaVA / InternVL 作视觉 LMM 前史一句 | CLIP→指令微调通史重写 |
| **[[视频生成正式报告]]** | 无接口（生成 ≠ 理解） | Sora / 文生视频正式报告缺口 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| AV-Skills 技能分类与 Short/Long 规模 | 合成标注 prompt 逐字复刻成「可复现假数据配方」操作手册（附录图仅点名存在） |
| 三阶段课程与 Table 4/5 超参 | 把 512×H100 外推成未给出的总 FLOPs / 美元成本 |
| TAVIT 时间戳接地 + GRPO 奖励类型（format / accuracy / structured） | 侧写可复现越狱或有害 AV 请求绕过 |
| Table 1 / Table 6 文内分数 | 未列表的 Figure 1 雷达图读点、未下载的 OmniVinci 原文细节 |
| 「fully open」主张 **与** non-commercial 许可 **并列** | 断言 Apache/商用可任意部署 |

---

## 三、架构思想（主读）

### 3.1 总图（§3.1 / Fig.2）

文称架构 **similar to OmniVinci**，五块：

1. **SigLip** 视觉编码器（Zhai et al., 2023）+ **「Spatial-Scale-then-Compress」Dynamic S2**（循 Liu et al. 2025a / Ye et al. 2025）——多尺度编码再压缩，宣称在提高分辨率/帧数时 **不按比例膨胀** LLM token 数。
2. **AF-Whisper** 音频编码器（借自 Audio Flamingo 3 / Next / Music Flamingo）：波形 **16 kHz mono** → **128-ch** log-mel（窗 **25 ms** / hop **10 ms**）→ **非重叠 30 s** 滑窗独立编码再沿时间拼接，以支持长音频。
3. **跨模态时序对齐**：各模态 **2-layer MLP** 投到 LLM 嵌入空间；按时间切同步块后 **交错（interleave）**，使同学段视听 token 相邻，便于自注意力跨模态；再加 **CRTE（Constrained Rotary Time Embeddings）** 编码绝对时间。
4. **LLM 骨干**：**Qwen2.5-7B**（Team, 2025）——文内写 **7B 参数、36 hidden layers、16 attention heads**；前缀为交错 AV 嵌入 + 文本指令，自回归出文本。长视频（文称最长约 **15 min**）训练用 **hybrid sequence parallelism**（Ulysses 节点内 + Ring-Attention 节点间）+ FSDP/ZeRO。
5. **Streaming TTS（可选）**：decoder-only，条件于 LLM 子词与已生成音频 token；细节 **显式外指** Goel et al. 2025（Audio Flamingo 3），本卡不展开声码器。

**与 [[QwenOmni音视频原生]] 接口一句（勿展开）**：Qwen Omni 走 Thinker–Talker + AuT 原生全模态产品栈；本卡是 **OmniVinci 系「双编码器 + 时序交错 + 7B 文本 LLM」** 路线，TTS 为可选外接式模块叙述。

### 3.2 数据：AV-Skills 与 AV-Think（§3.2）

**动机**：公开资源多为单模态或短片识别型 AVQA；许多 omni 模型「分模态训完指望隐式交叉」；长视频联合监督稀缺。作者在 WorldSense、MMOU 等上把多选改开放题以减选项捷径，归纳缺口后建库。

| 子集 | 时长 | 规模（文内） | 技能焦点（摘要） |
|---|---|---|---|
| **AV-Skills-Short** | ≤ **60 s** | **100K hours**；**3.8M** instances（**1M** captions + **2.8M** QA） | Relation / Emotion Change / Temporal / Spatial / Causal / Hallucination Detection / Audio Counting / Video Counting 等 |
| **AV-Skills-Long** | **60 s – 15 min** | ~**140K hours**；**3.2M** instances（**1.2M** captions + **2.0M** QA） | Needle-in-haystack、Temporal Referring/Order/Attribute、Sub-scene、Holistic、Counting、AV Referring、Topic、Detailed Captioning、Event Sequence、AV Event Alignment、Inference、Comparative、Context 等（文列 13 类技能叙事） |
| **合计（摘要）** | — | ≈**7M** caption+QA；≈**4.8M** QA | 强调 temporal / compositional / cross-modal |
| **AV-Think（TAVIT 数据）** | 长视频（预告片、电影回顾、悬疑、多方对话等） | ≈**24K**；推理链均长 **635.7** words | 中间推理步显式挂到 **音+视** 时间戳；TAC 风格时间戳字幕 → LLM 合成 QA–reasoning 三元组 |

公开源举例（文内）：短侧 YouTube-8M、HD-VILA、InternVid、VidChapters；长侧 HarmonySet、LSMDC、MMTrail、MovieClips、MiraData；另有开放互联网按品类采样（播客、城市漫步、访谈、体育等，Fig.4）。

**AV-Safety QA（Appendix A）**：long-context SFT 中 **536 hrs / 92K** QA，针对识别私人、骚扰描述、抽取敏感信息等请求，目标回答为安全拒绝/重定向。

单模态混料大量借自 OmniVinci / Audio Flamingo 3 / Music Flamingo 等（Table 2 有 epoch 配比；CoT 列仅 **AV-Think** 标 2.0）。

### 3.3 三阶段课程（§3.3 + Table 4/5）

| 阶段 | 产出 | 数据重心 | 时长 / 上下文上限 | 全局 batch / LR / epoch | 并行 |
|---|---|---|---|---|---|
| **Pre-training** | 基础能力 | Init **OmniVinci** → Short-SFT：单模态 + **AV-Skills-Short** | ≤**5 min** / **16K** tokens | 128 / **1e-5** / 1 | ZeRO-3；**512×H100** |
| **Mid-training** | **AVF-Instruct** | **AV-Skills-Long** + 降采样 Short 等 | ≤**15 min** / **32K** | 128 / **1e-5** / 1 | ZeRO-3 + **SP**；同 512×H100 |
| **Post-training** | **AVF-Think** | **AV-Think**：先 SFT 再 **GRPO**（Shao et al., 2024） | ≤**15 min** / **32K** | 64 / **2e-5** / 2 | ZeRO-3 + SP；同 512×H100 |

共性（Table 4）：cosine decay；warmup ratio **0.03**；weight decay **0.0**；bf16；grad accumulate **8**。

**假设（文内）**：早期单模态+短上下文打感知与弱对齐；后期长真实视频才强化强对齐、长上下文与时间推理。

### 3.4 TAVIT 与 GRPO（§3.2 末 + Appendix E）

- **TAVIT**：相对「视频-only CoT」或短音频上事后贴推理，强调在 **长、证据分散** 的真实 AV 流里，把中间思维绑到时间戳，并 **交错** 音/视证据。
- **GRPO**：去掉显式 value，用同题多样本奖励均值估优势；Appendix E 写明 group size **G=5**。奖励：
 - **Format**：须落在 `<think>…</think>` + `<answer>…</answer>`；
 - **Accuracy**（QA）：规范化答案匹配；
 - **Structured**（开放 caption/回复）：LLM 抽 JSON 字段（场景、参与者、话题等）再比重叠。
 QA 用 format+accuracy；开放生成用 format+structured。

---

## 四、评测字段（辅读，Table 1 / §5 / Table 6）

文称在 **15+** AV / omni / audio / vision 基准上评测；Table 1 标注 closed / open-weight / open-source。下表只录 **文内写出的数字**（ACC↑，ASR 为 WER↓）。

### 4.1 Omni / 长 AV

| 基准 | 对照（文内） | AVF-Instruct | AVF-Think |
|---|---|---|---|
| WorldSense | Qwen2.5-O **45.4**；OmniVinci **48.2** | **50.3** | **51.6** |
| DailyOmni | OmniVinci **66.5** | **72.4** | **73.9** |
| OmniBench | Gemini-1.5 Pro **47.6** | **48.5** | **50.6** |
| MMOU | Gemini-2.5 Pro **64.2**；Minicpm-o 4.5 **46.8** | **56.9** | **60.2** |
| AVHBench A→V \| V→A Hall. | Gemini-2.0 Flash **83.3 \| 63.3** | **77.0 \| 81.1** | **79.0 \| 85.9** |

正文强调：MMOU 上相对开源平台 **46.8** 有明显提升；长复杂真实 AV 是主卖点。AVHBench 上 A→V 低于 Gemini-2.0 Flash，V→A 高于该对照——**分列，不捏合成「全面超过」**。

### 4.2 Audio / Video / ASR（多为 Instruct）

| 基准 | 文内要点 |
|---|---|
| MMAR | OmniVinci **58.4** → Instruct **60.1** |
| MMSU | Gemini 1.5 Pro **60.7** → Instruct **61.5** |
| MMAU-v05.15.25 Sound\|Music\|Speech\|Avg | AF3 **75.83\|74.47\|66.97\|72.42**；OmniVinci **73.57\|73.07\|68.17\|71.60**；Instruct **77.97\|73.17\|69.33\|73.49**（文称 overall avg 最佳） |
| CMM Hallucination | Gemini 2.5 Pro **82.0** → Instruct **86.7** |
| Video-MME w/o \| w/ subs | OmniVinci **67.3\|68.6**；Instruct **70.7\|71.2**（相对 NVILA **64.2\|-** 亦高） |
| LongVideoBench | OmniVinci **62.0**；NVILA **58.7**；Instruct **60.1**（**低于** OmniVinci，文内如实写 competitive） |
| MVHBench | OmniVinci **70.6** → Instruct **71.7** |
| LibriSpeech clean\|other WER | Phi-4-mm\|Qwen2.5-O **1.67\|3.4**；Instruct **1.64\|3.5** |
| SPGISpeech / TEDLIUM / GigaSpeech / VoxPopuli WER | Instruct **2.8** / **3.0** / **10.2** / **5.8**（与表内 Phi-4-mm 等对照，互有胜负） |

### 4.3 消融（Table 6）

| 模型 | DailyOmni | WorldSense | VideoMME |
|---|---|---|---|
| OmniVinci | 66.5 | 48.2 | 67.3 |
| AVF-Stage1（+AV-Skills-Short） | 69.5 | 48.5 | 68.5 |
| AVF-Instruct（+AV-Skills-Long） | 72.4 | 50.3 | 70.7 |

文内解读：Short 注入跨模态推理；Long 再抬长程与 grounding。

---

## 五、局限与开放声明（§6 + Appendix I）

文内自陈：

1. AV-Skills 来自公开集 + 开放互联网 → **源偏差**、与先验训练数据 **潜在重叠**；
2. **极长、极密** 且证据稀疏/分散的视频仍难；
3. 现有基准 **不足以** 代表开放真实部署。

未来工作：扩域、更难长视频、更真实评测协议。

Broader Impacts：正向（无障碍音频描述、讲座/纪录片理解、内容审核辅助）；风险（监控滥用、深伪辅助、多模态虚假信息）。缓解叙述：non-commercial 许可 + AV-Safety QA + 呼吁社区护栏。Aidatatang 语料在训练后被发行方撤回——Table 9 保留透明度说明，**不**随 AVF 产物再分发（Appendix H）。

---

## 六、本卡不回答的问题

- Qwen3.5-Omni 如何做到 256k / ARIA / 非降级 → **[[QwenOmni音视频原生]]**。
- Qwen2-Audio 三阶段与 Voice Chat 接口 → **[[SpeechLLM语音语言模型]]**。
- Seamless 百语 S2ST 与 EMMA 同传 → **[[SeamlessM4T语音翻译]]**。
- CLIP/Flamingo/LLaVA 视觉指令通史 → **[[多模态架构脉络]]**。
- Sora 等视频**生成**正式 TR 缺口 → **[[视频生成正式报告]]**。
- OmniVinci（Ye et al., 2025）自身训练全配方 → 本卡仅作 **初始化检查点** 接口，不代替其专篇。
- 页眉 Code/Model 的具体 GitHub/HF URL → **本 PDF 未抽出可核链接，标待核实**。

---

## 七、来源与核验

| 项 | 值 |
|---|---|
| 主 PDF | `https://arxiv.org/abs/2607.16107`（**10,120,887 B / 9.7M**；**47** 页） |
| 抽取 | |
| arXiv | https://arxiv.org/abs/2607.16107 · https://arxiv.org/pdf/2607.16107 |
| 核验日 | 2026-09-22 CST；`curl` PDF → 200； Pages=47；`ls -lh` 9.7M |
| 笔记路径 | [[音视频联合Flamingo]] |

**交付状态：** draft。数字与机制均跟读本地抽取；开源仓链与商业许可以作者后续正式页为准，**禁止**用二手博客补 URI。
