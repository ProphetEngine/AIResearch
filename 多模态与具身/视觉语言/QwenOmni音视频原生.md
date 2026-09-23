---
title: "Audio-native / Omni 增量：Qwen3-Omni → Qwen3.5-Omni（相对 11）"
topic: QwenOmni音视频原生
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2509.17765
 - https://arxiv.org/abs/2604.15804
arxiv: ["2509.17765", "2604.15804"]
related: ["SpeechLLM语音语言模型", "多模态架构脉络", "Qwen3技术报告深读"]
archived: 2026-09-22
---

# Audio-native / Omni 增量：Qwen3-Omni → Qwen3.5-Omni（相对 11）

> **定位**：原生 Omni 模态横切增量——相对 **[[SpeechLLM语音语言模型]]**（以 Qwen2-Audio 为锚的 Speech-LLM / Audio→Text）已入库的「编码器连续特征 ⊕ LLM 下一文本 token」栈，本篇只收 **原生 Omni**：同一 Thinker–Talker 端到端统一 **文本·图像·音频·视频**，并 **流式合成语音**。
> **攻坚线**：**架构思想（主）**——AuT 替换 Whisper、Thinker/Talker MoE、多码本 RVQ + MTP + Code2Wav、TM-RoPE / 显式时间戳、ARIA；**评测字段（辅）**——36 / 215 音视频基准、VoiceBench、首包延迟、非降级对照同尺 Qwen。
> **硬划界（禁止重写）**：
> - **禁止重抄** [[SpeechLLM语音语言模型]] 的 Qwen2-Audio 章节：Whisper-large-v3 前端、40 ms/帧、三阶段（多任务预训练 / 联合 SFT / DPO）、Voice Chat vs Audio Analysis 接口表、ASR/S2TT 表内逐格数字。本篇仅在对照句点名「[[SpeechLLM语音语言模型]] = 音频理解→文本输出」前置。
> - **禁止重写** [[多模态架构脉络]] 视觉 LMM 通史、[[Qwen3技术报告深读]] 全文；仅取「Qwen3 / Qwen3.5 骨干初始化、Strong-to-Weak Distillation / GSPO」接口。
> - 中间代 **Qwen2.5-Omni**（文内 Xu et al., 2025）本仓库未单独立档；本篇只记两篇 Omni TR **显式声明相对 2.5-Omni / 相对 3-Omni 的升级点**，不编造 2.5-Omni 未引用细节。
> **与 [[SpeechLLM语音语言模型]] 的接口一句**：[[SpeechLLM语音语言模型]] 回答「如何把波形压成连续帧条件在 7B LLM 上出文本」；本篇回答「如何在 **MoE Thinker–Talker** 上做到 **音视频入 + 文本/语音出**、长上下文与低首包延迟，且文本/视觉相对同尺单模态 **不降级**」。
> **禁止编造**：机制、参数量、小时数、延迟、表内分数一律锚定官方 PDF（2026-09-22 CST）与官方 README；图内未表格化的曲线点 **不读点**；3.5 摘要写「数百亿参数」但正文未给出 Plus/Flash 精确总参 → **不臆造 B 数**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文 A** | Qwen Team, *Qwen3-Omni Technical Report* | arXiv:**2509.17765v1** \[cs.CL\] **22 Sep 2025**（页眉日期 **2025-09-23**）；PDF：https://arxiv.org/pdf/2509.17765 → `https://arxiv.org/abs/2509.17765`（**25** 页 A4；4,036,466 bytes） | Thinker–Talker MoE + AuT（20M h）+ 多码本流式；30B-A3B 开源 |
| **主文 B** | Qwen Team, *Qwen3.5-Omni Technical Report* | arXiv:**2604.15804v2** \[cs.CL\] **21 Apr 2026**（页眉 **2026-04-22**）；PDF：https://arxiv.org/pdf/2604.15804 → `https://arxiv.org/abs/2604.15804`（**28** 页 A4；3,669,136 bytes） | Hybrid MoE + AuT（40M h / 6.25 Hz）+ **ARIA** + 256k；Plus/Flash API |

**一句话抓手：**
- **Qwen3-Omni**：在 Qwen2.5-Omni 的 Thinker–Talker 上把 **双方升级为 MoE**，用从零训练的 **AuT（~0.6B，20M 小时监督音频，12.5 Hz）** 替换 Whisper 系编码器，Talker 以 **多码本 RVQ + MTP + 因果 ConvNet Code2Wav** 做首帧即可播的流式语音；宣称冷启理论端到端首包 **234 ms**，单实例 ASR/口语理解可达 **40 分钟**级音频。
- **Qwen3.5-Omni**：再升 **Hybrid-Attention MoE**、上下文 **256k**（>10 h 音频 / 400 s@720P·1FPS AV）、AuT 扩到 **40M 小时、6.25 Hz（~160 ms/帧）**，用 **ARIA** 把双轨文本–语音生改成自适应交织单流；产品面强调可控 AV 字幕、实时打断/音色克隆、原生工具调用与 **Audio-Visual Vibe Coding**；**Plus** 在文内 215 项音视频子任务上报 SOTA。

---

## 二、议题边界：从「Audio→Text Speech-LLM」到「原生 Omni」

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[SpeechLLM语音语言模型]] Qwen2-Audio** | 「音频编码器连续特征条件 LLM → **文本**」；无原生波形输出 | Whisper 初始化、40 ms/帧公式、三阶段训练全文、评测表逐格 |
| **[[多模态架构脉络]] / 视觉 LMM** | 「视觉编码器 + LLM」并列轴存在 | LLaVA/Flamingo 接法通史 |
| **[[Qwen3技术报告深读]]** | 骨干初始化、Strong-to-Weak Distillation、GSPO 槽位 | Qwen3 文本训练全文 |
| **Qwen2.5-Omni（文内引用）** | Thinker–Talker 祖先；3-Omni 列出的 5 项升级对照 | 未下载的 2.5-Omni TR 细节 |

### 2.2 能力面跃迁（跟读）

`
[[SpeechLLM语音语言模型]] 锚点： 音频 / 文本入 → 文本出（分析 + 语音聊，仍无 TTS）
Omni 锚点： 文本·图像·音频·视频入 → 文本出 + 流式语音出（同一端到端模型）
额外主张： 早期混入单模态+跨模态预训练 → 相对同尺文本/视觉 Qwen「非降级」
`

**可跟读金句（3-Omni Abstract）：** 「a single multimodal model that for the first time maintains state-of-the-art performance across text, image, audio, and video **without any degradation** relative to single-modal counterparts」；「Talker autoregressively predicts discrete speech codecs using a **multi-codebook** scheme」。

---

## 三、世代对照总表（跟读用）

| 维度 | Qwen3-Omni（2509） | Qwen3.5-Omni（2604）相对 3 的增量 |
|---|---|---|
| 骨干叙事 | Thinker–Talker；双方 **MoE**（相对 2.5-Omni 的 5 升级之首） | 双方 **Hybrid-Attention MoE**（含 GDN，利于长音视频 KV） |
| 音频编码器 | **AuT** 从零训；**~20M** 小时；Conv2D× **8** → **12.5 Hz**（~**80 ms**/帧）；AuT 编码器约 **0.6B / Table1: 650M** | AuT 再训；**~40M** 小时（文称由 Qwen3-ASR 生成音文对）；Conv2D× **4** 下采样 **16×** → **6.25 Hz**（~**160 ms**/帧）；多语比例 **中:英:多语 ≈ 3.5:3.5:3** |
| 视觉 | Qwen3-VL 视觉编码器，**SigLIP2-So400M ~540–543M** | 采用 **Qwen3.5** 视觉编码器（Table1 写 **SigLIP2**） |
| 位置 / 时间 | **TM-RoPE**；音视频按绝对时间对齐，**取消** 2.5-Omni 固定 2s chunk | 保留 TM-RoPE 思路，但改在视频/AV patch 前插入 **秒级文本时间戳**；音频随机插时间戳，减轻长序列稀疏 temporal ID |
| 语音生成 | RVQ 多码本；骨干预测第 0 码本 + **MTP** 残差；**Code2Wav = 因果 ConvNet**（替 block-wise DiT） | 继承 RVQ+MTP+ConvNet；新增 **ARIA**（自适应 speech/text 交织约束，并双轨→单流） |
| Thinker↔Talker 条件 | Talker **不再吃** Thinker 高层文本表示，只吃音视频多模态特征 + 可经外部模块注入文本（便于 RAG/安全过滤） | Talker 条件含历史文本、多模态表示、**当前轮流式文本**；ARIA 对齐文本–语音单元 |
| 上下文 / 时长 | 预训练 S3 到 **32,768**；理解侧宣称单实例 **>40 min** 音频 | 预训练 S3 到 **262,144**；产品宣称 **256k**、**>10 h** 音频、**400 s** 720P@1FPS AV |
| 语言覆盖（表） | 文本 **119**；语音入 **19**；语音出 **10**（Table 3） | 文本 **201**；语音入 **113**（74 语 + 39 中文方言）；语音出 **36**（29 语 + 7 方言）（Table 3）。**注意**：3.5 Abstract 另写「speech generation across **10** languages with human-like emotional nuance」——与 Table 3 的 36 **口径不同**，跟读以表为准，不捏合 |
| 首包延迟（理论） | 30B-A3B：音频/视频 **234 / 547 ms**（Table 1） | Flash：**235 / 426 ms**；Plus：**435 / 651 ms**（Table 1） |
| 开源 / 产品 | **30B-A3B** Instruct / Thinking / Captioner，**Apache 2.0**（README + Abstract） | 文称 **Plus / Flash** Instruct，**经 API 公开**；正文 **未**给 Plus/Flash 精确参数量（仅 Abstract「hundreds of billions」） |
| 训练 token（S2） | ~**2T**（文 0.57 / 音 0.77 / 图 0.82 / 视 0.05 / 视音 0.05） | ~**4T**（文 0.92 / 音 1.99 / 图 0.95 / 视 0.14 / 视音 0.29） |

---

## 四、Qwen3-Omni：架构思想（主读）

### 4.1 相对 Qwen2.5-Omni 的五条升级（§1）

文内显式列举（跟读清单，勿与 [[SpeechLLM语音语言模型]] 混淆）：

1. Thinker / Talker 均改为 **MoE**；
2. **Whisper → AuT**（20M 小时监督，block-wise window attention 以支持实时 prefill 缓存）；
3. 语音侧采用 **多码本** 表示（容量覆盖音色 / 副语言 / 声学现象）；
4. Talker **单轨 → 多轨 codec**，MTP 预测残差层；波形级 **DiT → 轻量 ConvNet**；
5. 入/出音频码率降至 **12.5 Hz**，输出 codec 支持 **单帧即合成**。

另列相对 2.5-Omni 的四条产品向改进：>40 min 音频理解；119/19/10 语覆盖；**Thinking** 全模态推理；端到端延迟低至 **234 ms**。

### 4.2 AuT（§2.2）

- 结构：attention-encoder-decoder；Qwen3-Omni **只用其 encoder**。
- 数据配比（训练）：**80%** 中英伪标 ASR、**10%** 其他语 ASR、**10%** 音频理解。
- 动态注意力窗：**1–8 s** query 模式，兼顾实时 prefill 与离线任务。
- 前端（§2.3）：16 kHz；128-ch mel；窗 **25 ms** / hop **10 ms**——与 [[SpeechLLM语音语言模型]] 前端数字同族，但 **编码器与帧率已换代**（此处只记 Omni 侧：约 **80 ms**/帧 @12.5 Hz）。

### 4.3 Thinker 感知与 TM-RoPE（§2.3）

- 文本：Qwen tokenizer，vocab **151,643**。
- 音视频：按 temporal ID **显式锚定绝对时间**对齐，**不再**像 2.5-Omni 切固定 2 s chunk → 支持任意时长流式输入。
- TM-RoPE：相对 M-RoPE 重分配旋转角（时间/高/宽 **24 / 20 / 20**），缓解长程外推问题。

### 4.4 Talker：多码本流式与「文本解耦」（§2.1, §2.4–2.5）

**控制面关键改动：** Talker **不消费** Thinker 高层文本表示，只条件于音视频多模态特征——动机：(i) 离散文本 token 与 embedding 信息等价；(ii) 翻译等需要保韵律/音色的 AV 协调。解耦后可用 **不同 system prompt** 分别控 Thinker 文风与 Talker 音色；也可让 RAG / function calling / 安全过滤改写 Thinker 文本后再注入 Talker。

**生成路径：** 每步 Talker 出一帧 → MTP 补残差码本 → 仅左上下文的流式 codec 解码 → **首 token 即可出波形**（对比 2.5-Omni 需等够 block 上下文）。

**Table 1 模块账（30B-A3B）：** AuT 650M · SigLIP2-So400M 540M · Thinker **30B-A3B** · Talker **3B-A0.3B** · MTP 80M · Code2wav 200M；端到端首包 **234/547 ms**（音/视）。

### 4.5 预训练三阶段（§3）

| 阶段 | 要点 |
|---|---|
| **S1 Encoder Alignment** | LLM 锁参，初始化自 **Qwen3**；视觉自 Qwen3-VL；音频自 AuT。先训 adapter 再训 encoder；**放弃**「冻 LLM 同时联合训 encoder+adapter」——文称后者会让 encoder 代偿冻住的 LLM，损害感知 |
| **S2 General** | ~**2T** token，早期即混单模态+跨模态；相对 2.5-Omni **多样自然语言提示**（非每任务单提示） |
| **S3 Long Context** | 最大长度 **8,192 → 32,768**；提高长音频/长视频占比 |

### 4.6 后训练（§4）

**Thinker 三阶段：** 轻量 **SFT** → Qwen3 式 **Strong-to-Weak Distillation**（off-policy 响应蒸馏 + on-policy KL 对齐教师 **Qwen3-32B / Qwen3-235B-A22B**）→ **GSPO**（规则奖励 + LLM-as-judge；视觉任务用 Qwen2.5-VL 作裁判）。

**Talker 四阶段：** 大规模多模态语境语音映射 → 高质量 **CPT** + 长上下文 → 多语偏好 **DPO** → **speaker fine-tuning**。

**Captioner：** 在 30B-A3B 上微调细粒度音频描述 → **Qwen3-Omni-30B-A3B-Captioner**（开源；填补「通用音频 caption」缺口）。

### 4.7 开源变体（README + Abstract）

| 名称 | 角色（README） |
|---|---|
| **Instruct** | Thinker+Talker；音/视/文入，音+文出 |
| **Thinking** | 仅 Thinker + CoT；音/视/文入，**文本出** |
| **Captioner** | 自 Instruct 下游微调；音频入→细粒度文本 caption |

另有文内 **Flash-Instruct / Flash-Thinking**（in-house，强调效率与方言等；非上述三权重同级开源声明）。

---

## 五、Qwen3.5-Omni：相对 3-Omni 的架构增量

### 5.1 文内五条技术升级 + 三条新能力（§1）

**技术：** (1) Hybrid-Attention MoE；(2) **256k** 与超长音/AV；(3) 多码本单帧即合成（继承并强化）；(4) **ARIA**；(5) 多语大幅扩展（识别 113 / 合成 36，Table 3）。

**新能力叙事：** (1) 可控 AV 字幕（结构化、时间戳、分镜/人物–音频关系）；(2) 全面实时交互（原生轮次意图打断、音量/语速/情绪端到端控制、用户样本零样本克隆）；(3) 原生 Omni **agent**——自主 WebSearch、复杂 FunctionCall、以及涌现的 **Audio-Visual Vibe Coding**（直接按音视频指令写可执行代码）。

### 5.2 ARIA（§2.4–2.5）——本代最宜跟读的生成侧新件

问题陈述：流式合成不稳/不自然，常因 **文本 tokenizer 与语音 tokenizer 编码效率不一致**。

机制要点：

- 把 3-Omni 的 **dual-track** Talker 输入改成 **单通道交织**；
- **不用** MFA 对齐或固定交织率；
- 约束：对生成序列任意前缀，累积 **speech/text token 比** 不得超过该样本级全局比；
- 效果主张：减少跳词、错音、数字含糊；支持任意文本前缀后续接连贯语音 token；并降低双轨同步开销。

### 5.3 时间戳策略修正（§2.3 / §3）

诊断 TM-RoPE 直接绑绝对时间的两点限制：长 AV 上 temporal ID **过大过稀**；且需要跨 fps **均匀大采样** 抬高数据成本。对策：每个视频/AV temporal patch 前置 **「秒」格式文本时间戳**；音频序列 **随机间隔** 插时间戳。代价：上下文略增；收益：长上下文时间感知更稳。

### 5.4 预训练 / 后训练增量要点

**预训练：** 同三阶段骨架；S2 ~**4T**；S3 **32,768 → 262,144**；初始化改 **Qwen3.5** 文本+视觉 + AuT。

**Thinker 后训练（三阶段叙事变了）：**

1. **Specialist Distillation**：各域教师（含视觉/音频）独立 SFT+RL，再蒸馏进统一模型；
2. **On-Policy Distillation**：针对「同题音频条件回答质量弱于文本条件」——用文本条件响应作音频条件蒸馏目标；
3. **Interaction-Aligned RL**：多轮轨迹上针对语码切换、人设漂移、长程指令遵循等交互体验塑奖。

**Talker：** General（>**20M** 小时多语语音+多模态语境）→ 长上下文 CPT（至 **64k**，并借助 3-Omni-Captioner 抑幻觉）→ **DPO + 规则奖励 / GSPO** → speaker FT。相对 3-Omni Talker，文强调更多 **instruction-following speech** 任务，而非单纯单调映射。

---

## 六、评测字段（辅；只摘主张与可核验锚点）

### 6.1 Qwen3-Omni（§5–6）

- **音视频榜面主张（Abstract / Conclusion）：** 36 项音/AV 基准上开源 SOTA **32**、总体 SOTA **22**；并点名优于 Gemini-2.5-Pro、Seed-ASR、GPT-4o-Transcribe 等（具体格点见正文大表，本笔记不整表重抄）。
- **VoiceBench Overall（Table 7）：** Gemini-2.5-Pro **89.6**；Qwen3-Omni-Flash-Thinking **89.5**；30B-A3B-Thinking **88.8**；30B-A3B-Instruct **85.5**。（正文叙述写「Thinking … 89.5」与表中 **Flash-Thinking** 列对齐时需小心——**以 Table 7 列名为准**。）
- **非降级（§6）：** 与同尺 **Qwen3-30B-A3B** / **Qwen3-VL-30B-A3B** 对照；文称 Omni 在文本与视觉上匹配同尺单模态，同时具备音频/AV。
- **延迟：** 理论首包 **234 ms**（音频入，1 并发）；Table 2 给出 4/6 并发下延迟与 RTF（RTF 均 **<1**）。

### 6.2 Qwen3.5-Omni（§5）

- **规模主张：** Plus 在 **215** 项音/AV 理解·推理·交互子任务上报 SOTA；相对 **Gemini-3.1 Pro**，文称在通用音频理解/推理/识别/翻译/对话上超越，AV 理解整体达同级。
- **VoiceBench（Table 5）：** Gemini-3.1 Pro **88.9**；Flash **87.8**；**Plus 93.1**。
- **ASR 摘录（Table 5，WER↓）：** 如 Librispeech clean|other：Gemini **3.36|4.41** vs Plus **1.11|2.23**；KeSpeech：Gemini **23.67** vs Plus **3.46**（完整语种/方言列见原表）。
- **非降级：** Table 4 对照 **Qwen3.5-Plus-Instruct**，文称 Omni-Plus 文本能力持平；Table 6 视觉持平且视频更强。
- **延迟：** Flash 音频首包 **235 ms** 与 3-Omni 234 ms 同量级；Plus 更重（**435 ms**）。Table 2 注明 Flash/Plus **部署资源不同，不宜硬比横向**。

### 6.3 诚实边界

- 3.5 **未**在 TR 中给出 Plus/Flash 的 Thinker/Talker 精确 B 数或专家配置；「hundreds of billions」仅摘要措辞。
- 「Audio-Visual Vibe Coding」为文内**涌现能力叙事**，本篇不另造评测协议。

---

## 七、跟读路线（建议 25–35 分钟）

1. **3-Omni** Abstract + §1 五升级清单 + Figure 2 文字说明（Thinker–Talker / MTP / Code2Wav）。
2. §2.2 AuT → §2.1 Talker 与文本解耦 → §2.5 Table 1–2 延迟账。
3. §3 S1–S3 与「放弃冻 LLM 联合训 encoder」一句；§4 Thinker/Talker/Captioner 阶段名。
4. **3.5-Omni** Abstract + §1 五升级/三能力 → §2.2 AuT 6.25 Hz → **§2.4 ARIA** → Table 1 延迟。
5. §3 时间戳修正 + 4T / 262k；§4 Specialist / OPD / Interaction-Aligned RL。
6. 扫 Table 7（3-Omni VoiceBench）与 Table 5（3.5 vs Gemini-3.1 Pro）核对主张，不背全表。

---

## 八、可回收结论（写进总账时用）

1. **相对 [[SpeechLLM语音语言模型]]：** 问题从「Audio-Language → 文本」升级为「**原生 Omni** → 文本+流式语音」，并纳入视觉/视频与工业级首包延迟；音频栈核心符号从 Whisper 连续帧变为 **AuT + 离散多码本 Talker**。
2. **3 → 3.5：** 主增量不是再换一套 Thinker–Talker 口号，而是 **Hybrid MoE + 更长上下文 + 更重 AuT + ARIA 对齐 + 交互/Agent 后训练**；语言与时长覆盖数量级上跳。
3. **共用科学主张：** 早期混合单模态与跨模态预训练，追求相对同尺 Qwen **文本/视觉不降级**——两篇均把「非降级」写成可检的同尺对照，而非口号。
4. **落地分流：** 要权重与本地复现 → **3-Omni 30B-A3B（Apache 2.0）**；要更长上下文/更强交互与 API → **3.5-Omni Plus/Flash**（TR 口径）。

---

## 九、来源与抽取指纹

| 文件 | 用途 |
|---|---|
| `https://arxiv.org/abs/2509.17765` | 一手 TR A |
| `https://arxiv.org/abs/2604.15804` | 一手 TR B |

## 相关笔记

- [[SHADEArena隐瞒与监控|SHADE-Arena]]
- [[天气气候基础模型|Weather / Climate FM]]
- [[QwenOmni音视频原生|Qwen Omni]]
- [[LearnLM教育辅导|LearnLM]]

