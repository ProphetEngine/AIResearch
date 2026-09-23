---
title: "视频—语言推理：SiLVR + Chain-of-Frames（≠ AV-Flamingo）"
topic: SiLVR与ChainOfFrames
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2505.24869 # 1.5M / 25p（主 A）
 - https://arxiv.org/abs/2506.00318 # 5.0M / 22p（主 B）
 - https://arxiv.org/abs/2605.26014 # 4.9M / 18p（可选补链，不升主）
arxiv: ["2505.24869", "2506.00318", "2605.26014"]
related:
 - "音视频联合Flamingo"
 - "视频生成正式报告"
 - "多模态架构脉络"
 - "QwenOmni音视频原生"
code_urls:
 - "https://sites.google.com/cs.unc.edu/silvr"
 - "https://github.com/SaraGhazanfari/CoF"
 - "https://github.com/aiming-lab/storm"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 视频—语言推理：SiLVR + Chain-of-Frames（≠ AV-Flamingo）

> **定位**：多模态推理横切——在已入库 **[[音视频联合Flamingo]] AV-Flamingo（开源音视频联合基础模型卡）**、**[[视频生成正式报告]] 视频生成正式报告备忘**、**[[多模态架构脉络]] 多模态通史**、**[[QwenOmni音视频原生]] Qwen-Omni 产品卡**之外，补「**理解侧视频—语言推理框架**」空位。双主锚：
> - **SiLVR**（*Simple Language-based Video Reasoning*）：**训练免费**；短 clip 视觉描述 + ASR 字幕 → **Adaptive Context Reduction** → 强推理 LLM（默认 DeepSeek-R1）在**纯语言空间**做复杂 VideoQA。
> - **Chain-of-Frames（CoF）**：视频 LLM **单阶段**推理迹中显式引用帧 ID（Frame-k）；用 **CoF-DATA**（真实 VideoEspresso + 合成 CLEVRER，164,186 条）微调 InternVL 等，强化时序锚定。
> **攻坚线**：**架构思想（主）**——语言管道 vs 帧锚定 CoT；**评测字段（辅）**——文内 VideoMME / Video-MMLU / CGBench / VSI-Bench 等表，禁外推未测榜。
> **硬划界（开篇钉死）**：
> - **≠ [[音视频联合Flamingo]] AV-Flamingo**：禁止重写 OmniVinci 初始化、SigLip/AF-Whisper、CRTE、AV-Skills 课程、TAVIT/AV-Think、GRPO 产品配方。本卡对象是 **推理框架 / 数据形态**，不是开源 AV 基础模型卡。
> - **≠ [[视频生成正式报告]]**：禁止重写文生视频 / Sora 正式报告缺口备忘；本卡是 **理解 / 推理**，不是生成。
> - **≠ [[多模态架构脉络]]**：禁止重写 CLIP→Flamingo→LLaVA→「原生多模态」通史阶梯；经典多模态祖先仅作 related-work 接口。
> - **≠ [[QwenOmni音视频原生]] Qwen-Omni**：禁止重写 Thinker–Talker MoE、AuT、ARIA、36/215 基准产品表；本卡不写 Omni 产品栈。
> **补链不升主**：**STORM/TORM**（arXiv **2605.26014**；抽取题名 **TORM**，GitHub `aiming-lab/storm`）——把时空推理**内化到有界连续 latent**，方法面异于「语言管道 / 帧锚定文本 CoT」→ **本波仅附录一句**，禁止升第二主轴。
> **禁止编造**：机制、公式、表数字一律锚定官方 PDF（2026-09-22 CST）。图内未表格化曲线点标 **待核实读图**。SiLVR Table 1 与 Table 2 在 CGBench/CinePile 列出现互换迹象 → **主结果以 Table 1 + 正文叙述为准**。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主 A** | *SiLVR: A Simple Language-based Video Reasoning Framework* | arXiv:**2505.24869v3** \[cs.CV\]（**15 Apr 2026**）；*TMLR*（01/2026）；UNC Chapel Hill（Zhang, Lin, Wang, Bansal, Bertasius）；OpenReview `mQZbh9Zlbw` | `https://arxiv.org/abs/2505.24869` | **1.5M**（1,521,117 B） | **25** letter | |
| **主 B** | *Chain-of-Frames: Advancing Video Understanding in Multimodal LLMs via Frame-Aware Reasoning* | arXiv:**2506.00318v2** \[cs.CV\]（**4 Apr 2026**）；Ghazanfari et al.（NYU / EPFL） | `https://arxiv.org/abs/2506.00318` | **5.0M**（5,146,783 B） | **22** letter | |
| **可选补链** | *TORM: Internalized Modeling for Spatial-Temporal Reasoning in Video-Language Models*（议程称 STORM；GitHub `storm`） | arXiv:**2605.26014v1** \[cs.CV\]（**25 May 2026**）；Liang*, Chen* et al.（Purdue / Harvard / UNC / UCF / NVIDIA / Physion） | `https://arxiv.org/abs/2605.26014` | **4.9M**（5,069,900 B） | **18** letter | |

| 材料 | 代码 / 主页（文内可核） |
|---|---|
| SiLVR | https://sites.google.com/cs.unc.edu/silvr（摘要）；OpenReview 论坛上列 |
| CoF | PDF 注解 URI：https://github.com/SaraGhazanfari/CoF（摘要写「Code available at GitHub」） |
| STORM/TORM | https://github.com/aiming-lab/storm（摘要；仅补链） |

**体积判定（2026-09-22 CST）**：SiLVR **1.5M**、CoF **5.0M**、STORM **4.9M**，均 **<10MB** → 按「>10MB 正式外链」规矩 **三份均**（无需降级）。权重 / CoF-DATA 本体 / 视频 **禁止**入库。

**一句话抓手：**
- **SiLVR**：别再为视频专门训 RL/CoT——把多感官视频**压成语言**，交给已会推理的 LLM；用 **ACR** 按上下文上限自适应加粗 clip。
- **CoF**：别做多阶段「先抽关键帧再答」——在**单次解码**的推理迹里写「Frame k: …」，用可规模化 **CoF-DATA**（含低成本合成）教会模型时序锚定。
- **STORM/TORM（补）**：别把中间证据外化成文本/工具——训练期用 thought-video 对齐 **latent slots**，推理期只做有界 latent rollout。

---

## 二、议题边界：只写「理解侧推理框架」，不写 AV 基础卡 / 生成 / 通史 / Omni 产品

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[音视频联合Flamingo]] AV-Flamingo** | 「长复杂真实音视频理解」是共同任务床 | OmniVinci/SigLip/CRTE/AV-Skills/TAVIT/GRPO 配方全文 |
| **[[视频生成正式报告]]** | 「视频」一词相邻 | 文生视频正式 TR 缺口 / Sora System Card |
| **[[多模态架构脉络]]** | 多模态生成式接口是前序 | CLIP/Flamingo/LLaVA/Gemini 阶梯通史 |
| **[[QwenOmni音视频原生]] Qwen-Omni** | 「端到端多模态助手」产品对照一句 | Thinker–Talker / AuT / ARIA / 延迟与非降级表 |

### 2.2 双主轴 vs 补链 vs 禁区

`
视频—语言「理解侧推理」横切（本卡）
 │
 ┌────┼────────────────┐
 ▼ ▼ ▼
 SiLVR Chain-of-Frames STORM/TORM（不升主）
 训练免费语言管道 帧锚定单阶段 CoT 内化时空 latent
 NVILA+Whisper CoF-DATA SFT thought-video→latent
 → DeepSeek-R1 InternVL / Phi 推理无再生视频
`

| 问题 | SiLVR | CoF | STORM/TORM（补） |
|---|---|---|---|
| 视觉证据何时进模型？ | **前置**成 caption/字幕文本 | **始终**以帧序列进视觉 LLM；推理迹里**引用帧 ID** | 训练用 thought-video；推理只跑 **latent** |
| 要不要视频侧训？ | **否**（captioner/ASR/LLM 即插即用） | **要**（在 CoF-DATA 上 SFT/LoRA） | **要**（两阶段 latent 对齐） |
| 相对多阶段 keyframe agent？ | 单次 LLM 调用 + ACR | 单阶段、无辅助帧选模块 | 无工具 / 无帧重插 |

---

## 三、SiLVR：训练免费的语言管道式视频推理

### 3.1 两阶段分解（§3 / Fig. 2）

1. **多感官→语言**：视频切成非重叠短 clip `{v_i}`，预训练 captioner `M`（默认 **NVILA**）得 `C={c_i}`；并行用 **Whisper-large-v3** 得带时间戳字幕 `S={s_j}`；拼接 `Z = concat(S, C)`。
2. **语言→推理**：把 `Z` 与问题 `Q` 喂给强推理 LLM `F`（默认 **DeepSeek-R1**，temperature **1.0**）。推理**完全在语言空间**，不依赖视频侧 RL/专门 CoT 数据。

文内主张的好处：**简单 / 可泛化 / 模块化 / 可插拔**（换 captioner、ASR、LLM 无需重训整条视频栈）。

### 3.2 Adaptive Context Reduction（Algorithm 1）

长视频（文内强调 CGBench / EgoLife 等平均 **>1 小时**）易撑爆 LLM 上下文。ACR：

`
Require: V, Q, F, M, W, 初始 clip 长 L
S ← ASR(V)
limit ← getContextLength(F)
while True:
 按 L 切分 → 生成 captions C → Z = concat(S, C)
 if tokens(Z) > limit: L ← L × 2
 else: break
return answer(Z, Q, F)
`

直觉：从细粒度起步，**超限则加倍 clip 长度**以减少段数/token，适配不同时长仍尽量保性能。Table 8（VideoMME overall）：ACR **76.7** vs 最佳固定 8s **74.2**（+2.5%）。

### 3.3 评测字段（锚定 Table 1 / 正文；辅表）

**设定（§4.1）**：Video-MMMU 用 **comprehension** split；VideoMME 用 **long + subtitles**（主表）。分「推理榜」与「通识视频榜」。

**Table 1 · SiLVR（ours）主数字（可核）：**

| 榜 | Video-MMMU | Video-MMLU | MMVU | MMWorld | VideoMME (long+sub) | CGBench | EgoLife | CinePile |
|---|---|---|---|---|---|---|---|---|
| **SiLVR** | **82.7** | **83.1** | 68.2 | 59.9 | **77.7** | **51.8** | **42.0** | 59.4 |

正文声称：**best-reported** 于 Video-MMLU、VideoMME（long+sub）、CGBench、EgoLife；Video-MMLU 相对 Claude 3.5 Sonnet（71.3）**+11.8**；CGBench 相对 Qwen-2-VL-72B（45.3）**+6.9**；VideoMME / EgoLife 相对 Gemini 1.5 Pro **+0.3 / +5.1**。

**推理 LLM 是否关键（Table 2）**：同管道换 DeepSeek-R1 vs DeepSeek-V3 / Llama 4——推理榜平均增益 **+8.0**，通识榜 **+3.8**（相对 V3）；VideoMME 类别上推理类问题 vs Llama 4 **+11.1%**，非推理类 **+4.9%**（Fig. 3 / 正文）。

**vs agent 多轮（Table 3，VideoMME long，无字幕）**：SiLVR（NVILA-7B + DeepSeek-R1）**62.7** > VCA 56.3 / VideoTree 54.2 / DrVideo 51.7 / VideoAgent 46.4；文内强调对手多轮 LLM 交互，SiLVR **单次**推理调用。

**时序 grounding（Table 5）**：CGBench Grounded VideoQA **mIoU = 11.84**（摘要写相对先前最佳 **+6.1%**；正文相对 VideoMind-7B 7.10 / Claude 4.17 等）。Video-MMMU **Δknowledge = 17.2**（高于 GPT-4o 15.6）。

**效率（Table 4，VideoMME Long，无 ASR 设定）**：SiLVR-best **442s / 62.7**；SiLVR-fast **83s / 57.2**（仍高于多个 agent / 原生视频基线）。具体硬件：多数单卡 A6000；Qwen-2.5-VL-7B 768-frame 例外需四卡。

**模态消融要点（正文 §）**：砍 50–75% **语音** token 掉点 **11.4–20.7%**，砍同比例 **视觉 caption** token 仅 **7.8–9.0%** → 该设定下语音 token 信息量更大（Table 7，本卡不逐格抄）。

> **表一致性备注**：Table 2 打印行把 CGBench/CinePile 写成 59.4 / 51.8，与 Table 1（51.8 / 59.4）及正文「CGBench 51.8%」冲突 → **入库跟读以 Table 1 + 正文叙述为准**，不调和编造。

---

## 四、Chain-of-Frames：帧锚定的单阶段视频 CoT

### 4.1 问题诊断（§3.1）与提案（§3.2）

既有视频 CoT 两极：
- **多阶段**：辅助网络抽关键帧再推理（VideoEspresso、Video-of-Thought 等）→ 贵、任务特化、偏离「自然语言 CoT」。
- **单阶段纯文本 CoT**：无显式帧—推理连接 → **时序接地差**。

**CoF**：在**单次推理**的文本迹中用 **Frame-k**（位置 ID，非时间戳）引用相关帧，再给答案。声称四点：数据质量可规模化、简单（无辅助模块）、显式时序 grounding、可解释。

与 InternVL 编码亲和：帧前已有 `Frame-1` 等文本标识（Fig. 4），利于长上下文里对齐「说到的帧」与「看到的帧」。

### 4.2 CoF-DATA（§3.3 / Fig. 3）

| 子集 | 源 | 生成方式 |
|---|---|---|
| **CoF-DATA_real** | VideoEspresso 训练集关键帧描述 | 对齐帧 ID → **Llama-3.1-8B-Instruct** 从原始标注生成 (Q, CoF-trace, A) |
| **CoF-DATA_synth** | **CLEVRER** 合成 3D 交互 | **手工模板**（计数 / 出现顺序 / 相对距离等），无需 LLM，成本低 |

流水线：先 **Frame ID alignment**（下采样 / 裁到模型可接受时长如 30s，重标定帧号，保持标注对齐）→ 生成迹 → 过滤「问题里已点名帧」样本；保留一定比例「无帧引用」样本以免强迫无关问题也出 CoF。**最终 164,186** 条。

### 4.3 训练与推理

- **CoF-InternVL2.5-4B**：全量微调 LLM + projection，**冻视觉编码器**。
- **CoF-InternVL3-8B**：**LoRA**。
- 另测 **Phi-3.5-Vision**（附录，本卡不展开数字）。
- 推理：均匀采 **30** 帧；不限死 30 秒视频时长。

### 4.4 评测字段（Table 1 / 2 / 3 / Fig. 6）

**Table 1（五榜 + Average）：**

| Model | VSI-Bench | Video-MME | MVBench | VidHal | EventHallusion | Average |
|---|---|---|---|---|---|---|
| InternVL2.5-4B | 33.5 | 54.7 | 71.5 | 77.0 | 67.4 | 60.8 |
| **CoF-InternVL2.5-4B** | 36.9 | 59.7 | 76.1 | 79.2 | 71.2 | **64.6**（**+3.8**） |
| InternVL3-8B | 41.0 | 66.5 | 74.4 | 80.9 | 72.1 | 67.0 |
| **CoF-InternVL3-8B** | **51.3** | **73.7** | **77.1** | 79.5 | **78.7** | **72.1**（**+5.1**） |

文内：更大骨干增益更大；CoF-8B 在 VSI / MVBench 取最佳或前列，Video-MME / VidHal 第二优等（相对表内闭源/大开源对照）。

**vs 多阶段视频 CoT（Table 2，共享榜）**：相对各法自报基线，CoF-InternVL3-8B 在 NEXT QA **+4.9**（对比 M-LLM 相对其基线 **+0.8**）；CoF-4B 在 Video-MME **+4.8**、NEXT QA **+4.3**（相对本骨干 Original）。

**CoF vs 朴素 CoT 变体（Table 3，InternVL2.5-4B）**：CoT prompting / SFT-QA-only / SFT-CoT（去帧引用）均不如 **SFT with CoF**；五榜上 CoF 行全面最优（表内：36.9 / 59.7 / 76.1 / 79.2 / 71.2）。

**合成数据（Fig. 6，等量 164k）**：多数榜上 **仅 synth > 仅 real**；**combined** 除 EventHallusion 外全面更好——文内强调合成 OOD 仍可迁移「计数/顺序」类技能。

---

## 五、双主轴对照（跟读用）

| 维度 | SiLVR | Chain-of-Frames |
|---|---|---|
| 范式 | **外置语言管道** + 推理 LLM | **内生视频 LLM** + 帧锚定 CoT |
| 训练 | **Training-free**（换件即用） | **需要** CoF-DATA SFT/LoRA |
| 时序接地 | 靠 caption/字幕时间戳与 ACR 粒度；另有 Grounded QA prompt 解 start–end | 推理迹内 **Frame-k** |
| 多感官 | **显式 ASR**（Whisper） | 主文设定为视觉帧序列（不主打音频） |
| 长视频策略 | ACR 加倍 clip | 均匀 30 帧；训练裁段对齐 |
| 代表涨点 | Video-MMLU **83.1**；CGBench QA **51.8** / mIoU **11.84** | CoF-8B Avg **72.1**（+5.1）；VSI **51.3** |
| 典型风险 | caption/ASR 信息瓶颈；纯语言可能丢细粒度像素 | 依赖帧 ID 与 InternVL 交织格式；合成—真实分布差 |

二者正交：**SiLVR** 回答「已有强推理 LLM 时，如何**零训**吃长视频多感官」；**CoF** 回答「视频 LLM 如何在**不引入多阶段管线**的前提下学会**指向帧**的推理」。禁止把任一写成 AV-Flamingo / Omni 产品续作。

---

## 六、可选补链：STORM / TORM（不升主）

抽取 PDF 题名为 **TORM**（*Spatial-Temporal reasOning via inteRnalized Modeling*）；GitHub 与议程写作 **STORM**（`aiming-lab/storm`）。**本卡不升主**，只记方法面差异：

- **动机**：文本 CoT / 关键帧重插 / 工具链把时空证据**外化**，延迟与工程复杂。
- **做法**：Stage I 用生成 **thought-video** 对齐有界 **latent tokens**（答损 + λ·latent 对齐）；Stage II 仅答损（Coconut 式），逼 latent 内化。**推理期不再生视频、不重插帧、不调外部视觉工具**。
- **骨干**：Qwen2.5-VL-7B-Instruct；Table 1：**VideoMME 61.0 / MVBench 61.1 / TempCompass 74.3**（32 frames）；Table 2：**VideoEspresso 58.7 / Video-Holmes 37.8 / MMVU 65.9**。

与双主轴关系：同属「视频推理」，但旋钮是 **连续 latent 内化**，不是语言管道、也不是帧锚定文本迹 → 仅作邻域索引。

---

### 7.1 建议跟读顺序

1. SiLVR Abstract + §3（含 Algorithm 1）+ Table 1/2/3/5。
2. CoF Abstract + §3.2–3.3 + Table 1/2/3 + Fig. 6。
3. （可选）STORM/TORM Abstract + Fig. 1/3 + Table 1/2 —— 只记「latent 内化」对照句。

### 7.2 备注

| 路径 | 体积 | 页数 | 建议 |
|---|---|---|---|
| `https://arxiv.org/abs/2505.24869` | **1.5M** | 25 | **官方 HTTPS 外链** + 已抽 |
| `https://arxiv.org/abs/2506.00318` | **5.0M** | 22 | **官方 HTTPS 外链** + 已抽 |
| `https://arxiv.org/abs/2605.26014` | **4.9M** | 18 | **（补链）**；**不升主议题**；已抽 |
| 多模态与具身/视觉语言/SiLVR与ChainOfFrames.md | （本笔记） | — | **draft**；日期 **2026-09-22** |

均 **远低于 10MB / 20MB 阈值**，禁止入库：模型权重、CoF-DATA、视频语料。

### 7.3 开放核对点（不编造）

- SiLVR Table 1↔Table 2 的 CGBench/CinePile 列不一致 → 跟读以 Table 1 + 正文「CGBench 51.8%」为准。
- CoF 摘要「Code available at GitHub」具体仓由 PDF 注解确认为 `SaraGhazanfari/CoF`；本篇不跟 commit。
- STORM vs TORM 命名：抽取题名 **TORM**，仓名 **storm**——引用时两者并列，勿臆造第三名称。

---

## 八、摘要（给议程回报表）

**[[SiLVR与ChainOfFrames]]** 立「视频—语言**理解侧推理**」横切：**SiLVR** = 多感官→语言→DeepSeek-R1 + ACR（训练免费）；**Chain-of-Frames** = 帧锚定单阶段 CoT + CoF-DATA（164k）微调 InternVL。硬划界 **≠[[音视频联合Flamingo]] / ≠[[视频生成正式报告]] / ≠[[多模态架构脉络]] / ≠[[QwenOmni音视频原生]]**；**STORM/TORM** 仅补链不升主。三 PDF 均 <10MB，**以官方 HTTPS 外链为准**。
