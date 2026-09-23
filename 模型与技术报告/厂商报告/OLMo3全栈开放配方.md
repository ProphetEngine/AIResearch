---
title: "全栈开放配方旗舰：OLMo 3 / Olmo 3（≠ Nemotron Ultra / gpt-oss / Gemma 4）"
topic: OLMo3全栈开放配方
date: 2026-09-22
lines: [架构思想, 开放配方接口, 评测字段]
status: archived
sources:
- https://arxiv.org/abs/2512.13961
arxiv: ["2512.13961"]
related:
 - "Nemotron3Ultra" # Nemotron 3 Ultra（工业开源性能旗舰；本卡写全栈开放配方，对照不重写）
 - "GPTossModelCard"
 - "Gemma4技术报告深读"
 - "Qwen3技术报告深读"
 - "DeepSeekV3训练与MoE基建"
 - "Llama4待核实备忘"
 - "混合专家架构"
 - "对齐脉络RLHF与偏好优化"
 - "推理时扩展TestTimeScaling"
contact: "olmo@allenai.org"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 全栈开放配方旗舰：OLMo 3 / Olmo 3（≠ Nemotron Ultra / gpt-oss / Gemma 4）

> **定位**：全栈开放配方主题轴——立 **AI2「fully-open」全栈 model flow** 锚点：不仅放最终权重，还放 **每阶段数据 / 中间 checkpoint / 代码依赖**。主文：*Olmo 3*（Team Olmo / Allen Institute for AI 等，arXiv:**2512.13961**v2）。旗舰叙事落在 **Olmo 3.1 Think 32B**（全文自称 strongest fully-open thinking model）。
> **攻坚线**：**架构思想 / 开放配方接口（主）** + **评测字段（文内系列对照，辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[Nemotron3Ultra]]**：禁止写成 **Nemotron 3 Ultra**（Hybrid Mamba–Transformer MoE、工业开源性能旗舰）全文；本卡轴是 **数据+配方透明的研究可复现旗舰**，与 [[Nemotron3Ultra]] 对照一句即可。
> - **≠ [[GPTossModelCard]]**：禁止重写 **gpt-oss** Model Card（OpenAI 开源权重 MoE + harmony / effort / MXFP4）；本卡无 MXFP4 / harmony 主轴。
> - **≠ [[Gemma4技术报告深读]]**：禁止重写 **Gemma 4** TR（Google Apache 开源权重族 / PLE / QAT）；本卡是 AI2 dense 7B/32B + Dolma/Dolci 全栈。
> - **≠ 已入库 Qwen / DeepSeek / Llama pending**：[[Qwen3技术报告深读]]、[[DeepSeekV3训练与MoE基建]]、[[Llama4待核实备忘]] 仅作 **对照基线名**（文内 Table 亦列 Qwen 3 / DS-R1 等），**禁止**把其架构/训练配方抄入本卡当 Olmo 主张。
> **禁止编造**：型号、token 量、表数字、算力日一律锚定本地抽取（2026-09-22 CST）。图内未抽出的精确曲线点标 **待核实读图**。正文品牌写 **Olmo 3**（封面/标题）；历史线对照写 **OLMo 2**（文内原样）。

---

## 一、材料元信息与 PDF 体积

| 字段 | 核实值（PDF arXiv API / 封面，2026-09-22 CST） |
|---|---|
| 标题 | *Olmo 3* |
| 作者 | Team Olmo（字母序；核心贡献者标 ★）；通讯机构含 AI2 / UW / CMU / Stanford / Mila 等；Contact **olmo@allenai.org** |
| arXiv | **2512.13961**v2 \[cs.CL / cs.LG\]；v1 published **2025-12-15 23:41 UTC** → **2025-12-16 07:41 CST**；v2 updated **2026-04-14 15:12 UTC** → **2026-04-14 23:12 CST**；comment: *minor edit updates* |
| 页数 / 版式 | **118** 页 letter（612×792 pts） |
| 官方深读 PDF | [arXiv:2512.13961](https://arxiv.org/abs/2512.13961) |
| `ls -lh` / `stat` | **6.6M**（**6,817,890** B ≈ **6.50 MiB**） |
| 抽取 | `*.txt`（章节化；见同目录 `README.md`） |
| 官方入口 | abs https://arxiv.org/abs/2512.13961 · PDF https://arxiv.org/pdf/2512.13961 |

**体积判定：** **<10MB 且 <20MB**，但 **118 页极长** → 按议程 **「强烈建议正式外链（或只抽选定章节），不默认整本二进制入库」**。本轮已下载供深读，**验收建议：**；文本抽取 **应入库**。

**一句话抓手：** Olmo 3 = AI2 在 **7B / 32B dense** 上把 **Base → Think / Instruct / RL-Zero** 整条 **model flow**（数据池+实际 mix+中间 ckpt+训练/评测代码）全部公开的 **fully-open** 旗舰；旗舰点 **Olmo 3.1 Think 32B** 在文内后训练套件上自称 **best fully-open @32B**，并以 **约 6× 更少 token** 逼近同规模最强 **open-weight** thinking（Qwen 3 32B 系）——**不是** Nemotron Ultra 那种工业 MoE 性能旗舰，也不是 gpt-oss / Gemma 4 那种「开源权重卡」。

---

## 二、议题边界：全栈开放配方 ≠ 工业 MoE 旗舰 ≠ 开源权重卡

### 2.1 相对相邻笔记只取接口

| 已入库 / 同主题 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[Nemotron3Ultra]]** Nemotron 3 Ultra | 「工业开源性能旗舰」对照位一句 | Hybrid Mamba–Transformer MoE、Nemotron agent 表、CC 语料清洗 |
| **[[GPTossModelCard]]** gpt-oss | 「另一路开源权重推理卡」对照 | harmony / MXFP4 / effort 旋钮 / OpenAI Preparedness 开源剖面 |
| **[[Gemma4技术报告深读]]** Gemma 4 | 「Google 开源权重族」对照 | PLE / QAT / encoder-free / Gemma thinking 符 |
| **[[Qwen3技术报告深读]] / DeepSeek-V3 / Llama-4-pending** | 文内基线名与 Table 数字对照 | 其 MoE/MTP/GRPO 配方正文；禁止用其未公开字段「补全」Olmo |
| **[[对齐脉络RLHF与偏好优化]] / [[推理时扩展TestTimeScaling]]** | SFT–DPO–RLVR / thinking traces 作接口槽 | RLHF 通史、TTS 通史全文 |

### 2.2 文内自划界：fully-open vs open-weight

文用 **fully-open**（Marin / Apertus / Olmo：沿 flow 放数据与中间阶段）对比 **open-weight**（只放最终 ckpt，如 Qwen 3 等）。Figure 1 明示：两者都放最终权重（深青），但 fully-open 另放 flow 上米色中间阶段。本卡主写 **flow 透明性 + 配方**，评测表只作辅证。

跟读口诀：

`
[[Nemotron3Ultra]] = 工业开源性能旗舰（Nemotron 3 Ultra）
[[GPTossModelCard]] = OpenAI 开源权重推理卡（gpt-oss）
[[Gemma4技术报告深读]] = Google 开源权重族（Gemma 4）
[[OLMo3全栈开放配方]] = AI2 全栈开放配方旗舰（Olmo 3 model flow） ← 本卡
`

---

## 三、型号族与开放产物清单（封面）

封面枚举（原样）：

| 分支 | 标识（封面） |
|---|---|
| **Base** | `Olmo-3-1025-7B` · `Olmo-3-1125-32B` |
| **Think** | `Olmo-3-7B-Think` · `Olmo-{3\|3.1}-32B-Think` |
| **Instruct** | `Olmo-3-7B-Instruct` · `Olmo-3.1-32B-Instruct` |
| **RL-Zero** | `Olmo-3-7B-RL-Zero-{Math\|Code\|IF\|General\|Mix}` · `Olmo-3.1-7B-RL-Zero-{Math\|Code}` |
| **Base 数据** | Pretrain **Dolma 3 Mix** · Midtrain **Dolma 3 Dolmino Mix** · Long-ctx **Dolma 3 Longmino Mix** |
| **后训练数据** | **Dolci**-Think-{SFT\|DPO\|RL}；**Dolci**-Instruct-{SFT\|DPO\|RL}；**Dolci**-RL-Zero-* |
| **代码** | 训练：**OLMo-core**（pretrain）· **Open Instruct**（posttrain）；数据：**datamap-rs** / **duplodocus** / **dolma3**；评测：**OLMES** / **decon** |

Abstract / §1：**整个 model flow**——每一阶段、checkpoint、数据点与依赖皆可介入，而非只动最终权重。

---

## 四、Model Flow 总图（§2）——本卡主轴

### 4.1 两段式：Base × 三岔后训练

Figure 2：

`
Pretrain → Midtrain → Long-context ⇒ Olmo 3 Base
 │
 ├─ Think SFT → DPO → RLVR ⇒ Olmo 3 Think
 ├─ Instruct SFT → DPO → RLVR⇒ Olmo 3 Instruct
 └─（直接）RLVR ⇒ Olmo 3 RL-Zero
`

### 4.2 Base 三阶段（§2.1 / §3）

| 阶段 | 数据 | 规模（文） | 目标 |
|---|---|---|---|
| Pretrain | **Dolma 3 Mix** | 至多约 **5.9T**（7B 写 5.93T；32B 余弦截断至 **5.5T**） | 自然多样语料 |
| Midtrain | **Dolma 3 Dolmino Mix** | **100B**（32B：跑两次不同 seed 再 **权重平均**） | 数学/代码/QA/指令/thinking 痕迹，服务后训练 |
| Long-context | **Dolma 3 Longmino Mix** | 7B **50B** / 32B **100B** | 扩至 **65K** 上下文 |

预训练三新意（§2.1）：① 万亿级全局去重工具；② **olmOCR science PDFs**；③ **token-constrained mixing** + **quality-aware upsampling**。

开放数据池声称（§2.1 Open artifacts）：源池约 **9T**（pretrain 清洗源）+ mid **2T** + long-ctx **640B**；另放小样本 mix（pretrain **150B** / mid **10B**）供低算力实验。

### 4.3 后训练三变体（§2.2）

| 变体 | 配方骨架 | 数据套件 | 产品意图 |
|---|---|---|---|
| **Think** | SFT → DPO（**Delta Learning**）→ **OlmoRL**（RLVR） | Dolci Think-* | 先出 thinking traces 再最终答案；旗舰 |
| **Instruct** | SFT（可从 Think SFT **warm-start**）→ DPO（含 **length control**）→ RLVR | Dolci Instruct-* | 短答、聊天、**function calling**；低延迟 |
| **RL-Zero** | **从 Base 直接 RLVR** | Dolci RL-Zero-*（相对 pre/mid **再去污染**） | 研究「基座数据如何影响 RL」；填补 open-weight 基座不公开 mid 数据的空白 |

### 4.4 墙钟成本（§2.4）——代表性格而非单美元口号

- 集群：**1024×H100** 专供 Olmo 3；自训练起至评完 **Olmo 3 Think 32B** 约 **56 天**（3.1 Think/Instruct 在此之后继续训）。
- 若按 **$2 / H100·hour** 粗算 → **$2.75M**（文给换算，非独立审计）。
- Pretrain 段约 **47 天**（含 mid + long-ctx）；Post-train 约 **9 天**（多轮 LR sweep）；3.1 Think 在初始 RL 后再加约 **21 天 / 224 GPU**。
- 配方多在 **7B 或更小** 上开发再快速上 32B。

---

## 五、架构与训练栈（§3.2 + Appendix Table 33–35）

### 5.1 相对 OLMo 2 的增量（正文主张）

- **Dense** decoder-only Transformer；**7B / 32B**；超参大体沿 OLMo 2。
- 预训练/中训上下文：**8192**（OLMo 2 为 4096）。
- **SWA**：每 **4 层中 3 层** sliding window **4096**；**最后一层始终 full attention**。
- Tokenizer：与 OLMo 2 同族，源自 OpenAI **cl100k**。
- 栈：**OLMo-core**；7B ≈ **7700 tok/s/GPU**、32B ≈ **1960 tok/s/GPU** @8192、bf16；约 **43% / 41% MFU**。DPO/RL 支持「planned but not yet complete」（相对 OLMo-core；后训练主落 **Open Instruct**）。

### 5.2 Table 33 架构表（附录，7B / 32B）

| 项 | 7B / 32B |
|---|---|
| Layers | **32 / 64** |
| Hidden $d_{model}$ | **4096 / 5120** |
| Q heads | **32 / 40** |
| KV heads | **32 / 8**（7B **MHA**；32B **GQA**） |
| Activation | **SwiGLU** |
| Norm | **RMSNorm**（输出）；**QK-Norm** |
| SWA | 3/4 层；窗 **4096** |
| RoPE | θ = $5\cdot10^5$；**YaRN 仅施于 full-attn 层**（长文扩展） |
| 其他 | Grad clip 1.0；Z-loss $10^{-5}$；embedding 无 weight decay |

### 5.3 长上下文（§3.6）

- 扩展后支持至 **65K**（序列长 Table 35：**65,536**）。
- 骨干数据：**olmOCR science PDFs**——文称 >**22.3M** 篇 >8K（合计 **640B** tokens），其中 **4.5M** 篇 >32K（**380B**）。
- Longmino Mix：约 **34%** 长文 + **66%** 高质量 mid 类数据；32B 用 **100B**、7B **50B**。
- 位置：仅对 **full attention** 层施 **YaRN**（消融称优于全层改 RoPE；**待核实读图** Figure 13）。
- 基建：长文段用 **8-way context parallel**（Table 34 CP=8）。

---

## 六、后训练配方要点（Think / Instruct / RL-Zero）

### 6.1 Think：SFT → Delta-Learning DPO → OlmoRL（§4）

**评测协议（§4.1.1）：** max ctx **32K**；temp **0.6**；top-p **0.95**（对齐 Guo/Adler/Qwen3 等写法）。方差分桶：高方差含 GPQA / AlpacaEval / IFEval 等。

**Delta Learning（§4.3 / §4.5）：**
- 直接对 DPO「chosen」（常为 Qwen3-32B Thinking）做续 SFT 会 **伤** 已饱和的 Think SFT（Table 21：Dev 7B SFT 70.3 → Cont.SFT 64.5）。
- 用弱模型（如 Qwen3-0.6B Thinking）作 rejected，拉大 **delta** → DPO 抬升（同表 Delta learning **72.9**）。
- Table 22：SFT+DPO+RLVR **优于** SFT+RLVR；**DPO 是更好的 RL 起点**。

**OlmoRL（§4.4.1）相对 vanilla GRPO 的改进清单（文列）：**
zero-gradient 组过滤；**active sampling**；**token-level loss**；**无 KL**；**clip-higher**；**truncated importance sampling**（对齐 vLLM vs train logprob）；**无 std 归一化 advantage**（降难度偏置）。目标式见文 Eq.(1)–(2)。
Verifier 扩到 math / code / IF / general chat（含 LM-judge）。
基建：continuous batching + **inflight updates** → Table 23 相对 OLMo 2 RL 吞吐大幅上升；文称可达约 **4×**（§4.4.3 叙述）/ 「一半 GPU 上 2× 更快」等口径——**照录不等式调和**。

**3.0 → 3.1：** Think 32B 初版 RL **750** steps；续训至 **2300** steps → **Olmo 3.1 Think 32B**（未饱和即停，因算力）。文称 AIME / ZebraLogic / IFEval / IFBench 等有可观增益，AlpacaEval 掉约 5 分。

### 6.2 Instruct：短答 + 工具（§5）

- 从 **Think SFT warm-start** 有益，且平均长度几乎不被 thinking 痕迹污染（Table 29 / §5.5）。
- Function calling 数据与 **BFCLv3** / LitQA2 / SimpleQA 等评测（Table 27、31）。
- DPO：**高对比** + **delta-aware** + 与 GPT-judge 信号 **混合**；**length control** 换可用性，且声称最终对 RL 更稳（§5.5）。

### 6.3 RL-Zero：从 Base 直接 RL（§6）

- 动机：既有开源 RLVR 多搭在 **不公开 pre/mid 数据** 的 open-weight 上 → 污染与「假奖励」难辨。
- Dolci RL-Zero 对 pre/mid **再去污染**；域：Math / Code / IF / General / Mix。
- 发现：单域奖励升得快；**Mix** 更难、各域相对欠优化 → 多目标 RLVR 基准位；亦可反查 midtrain 数据对 RL 的影响（Figure 25）。

---

## 七、评测字段摘录（辅；禁跨表硬比绝对分）

> 协议、解码、是否 thinking、是否 Avg@k 均不同源表自洽；**禁止**与 [[GPTossModelCard]] / [[Gemma4技术报告深读]] / Qwen3 TR 表直接「决胜负」。

### 7.1 旗舰快照 Table 1 / Table 14（Olmo 3.1 Think 32B 选列）

| 基准 | 3.1 Think 32B | Qwen 3 32B（文列） | 备注 |
|---|---:|---:|---|
| MATH | **96.2** | 95.4 | Table 1/14 |
| AIME 2024 | **80.6** | 80.8 | |
| AIME 2025 | **78.1** | 70.9 | 3.1 相对 3.0（72.5）再升 |
| OMEGA | **53.4** | 47.7 | |
| BigBenchHard | 88.6 | 90.6 | |
| ZebraLogic | **80.1** | 88.3 | 仍落后 Qwen 3 |
| HumanEvalPlus | **91.5** | 91.2 | |
| LiveCodeBench v3 | 83.3 | 90.2 | |
| IFEval | **93.8** | 86.5 | |
| IFBench | **68.1** | 37.3 | 3.1 相对 3.0（47.6）大涨 |
| MMLU | 86.4 | 88.8 | |
| GPQA | 57.5（Table 1）/ 56.7（Table 14 列） | 67.3 | **两表 GPQA 口径略异，照录不调和** |
| AlpacaEval 2 LC | 69.1 | 75.6 | 3.1 相对 3.0（74.2）下降 |

文主张：优于 Qwen2.5-Instruct / Gemma 2&3 27B / DS-R1-32B 等；逼近 Qwen 3 / Qwen 3 VL 32B Think；**约 6× 更少 token**。

### 7.2 Base 合成指标（Table 2 / 3，OlmoBaseEval）

| 合成 | Olmo 3 Base 32B | Marin 32B | Qwen 2.5 32B（open-weight 列） |
|---|---:|---:|---:|
| Math | **61.9** | 49.3 | 64.7 |
| Code | **39.7** | 30.8 | 48.3 |
| MC STEM | 74.5 | 75.9 | 82.2 |
| MC Non-STEM | **85.6** | 84.5 | 89.3 |
| GenQA | 79.8 | **80.3** | 68.5 |

7B：Math **54.7** / Code **30.7**——文称 fully-open 同档领先 Marin 8B / Apertus 8B / OLMo 2 7B；相对 Qwen3 8B / Nemotron Nano 等仍有差距。

### 7.3 阶段消融 Table 13（累计 token；选 32B）

| 阶段 | 累计 tok | Math | Code |
|---|---:|---:|---:|
| Stage 1 Pretrain | 5.5T | 48.4 | 29.8 |
| Stage 2 Soup（mid） | 5.7T | **69.7** | **39.7** |
| Stage 3 LC | 6.2T | 61.4 | 39.7 |

→ Midtrain 对 Math/Code 拉升显著；LC 阶段部分合成分回落——文仍强调长文能力解锁（细节见 Table 12，本抽取已落 `03-*.txt`，逐格未全抄）。

---

## 八、开放配方接口清单（验收用）

| 接口层 | 文内锚点 | 本卡用法 |
|---|---|---|
| 数据池 → mix | Dolma 3 / Dolmino / Longmino；源池 9T / 2T / 640B | 写「可复现介入点」，不重写通用 CC 清洗通史 |
| 后训练数据 | Dolci Think / Instruct / RL-Zero | Delta Learning + 多域 RLVR 样本 |
| 训练代码 | OLMo-core · Open Instruct | 架构/吞吐字段锚附录表 |
| 评测 | OlmoBaseEval · OLMES · decon | 决策用聚类/代理指标/SNR，非榜单通史 |
| 中间 ckpt | 每阶段释放 | fully-open 相对 open-weight 的核心增量 |
| 追踪 | thinking 链可回溯至训练数据（§1） | 研究机会句；禁止外推未给工具链 |

---

## 九、明确不写 / 待核实

| 不写 | 原因 |
|---|---|
| Nemotron 3 Ultra / gpt-oss / Gemma 4 架构与表 | 划界 ≠ [[Nemotron3Ultra]] / [[GPTossModelCard]] / [[Gemma4技术报告深读]] |
| Qwen3 / DeepSeek / Llama4 配方回填 | ≠ 已入库 TR；仅基线名 |
| 未抽出的 Figure 精确点、附录全表逐格 | 页数极长；需要时回 或 PDF |
| 权重 / 数据集整包下载入库 | 体积与许可另议；本卡只链配方接口 |
| 「已超越 Qwen 3」类外推 | 文写 *narrowing the gap* / *close to*；照录 |

**待核实读图：** Figure 1/2/13/18–21/24–26 等曲线与饼图像素值；Appendix A.3–A.8 大量配表未整章抄入笔记。

---

## 十、交叉双链

- **[[Nemotron3Ultra]]**：工业开源性能旗舰对照（Nemotron 3 Ultra）——同主题并行，不互相重写。
- **[[GPTossModelCard]] / [[Gemma4技术报告深读]]**：另两路「开源权重卡」样本。
- [[Qwen3技术报告深读]] / [[DeepSeekV3训练与MoE基建]] / [[Llama4待核实备忘]]：基线与 pending 位。
- **[[对齐脉络RLHF与偏好优化]] / [[推理时扩展TestTimeScaling]]**：偏好优化与 test-time thinking 通史接口。
- 同主题过程监督 / 工具环（[[可验证过程监督]] / [[ToolLoop工具数据合成]]）可作 RLVR / function-calling **下游用法**交叉，不升本卡主轴。

---

## 十一、验收摘要（给主管）

| 项 | 内容 |
|---|---|
| 笔记路径 | [[OLMo3全栈开放配方]] |
| 页数 | **118** |
| 深读 PDF | [arXiv:2512.13961](https://arxiv.org/abs/2512.13961)（**6,817,890 B / 118p**） |
| 备注 | 正式引用 arXiv HTTPS（页数较长，跟读以章节为准） |
| 主结论 | AI2 **fully-open model flow** 旗舰：Dolma 3 三阶段 Base（至 ~6T 级 + 65K）→ Dolci 后训练三角（Think / Instruct / RL-Zero）；旗舰 **Olmo 3.1 Think 32B** 文内称 strongest fully-open thinking @32B，并以更少 token 逼近 Qwen 3 开源权重 thinking |
| 划界 | ≠ [[Nemotron3Ultra]]；≠ [[GPTossModelCard]]；≠ [[Gemma4技术报告深读]]；≠ Qwen/DeepSeek/Llama pending 正文 |
