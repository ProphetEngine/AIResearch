---
topic: Gemma4技术报告深读
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# 1：Gemma 4 Technical Report 深读

> 攻坚线：**架构思想（主）** + **AI Infra / 效率·量化（辅）**
> 锚点：Gemma Team, Google DeepMind, *Gemma 4 Technical Report*（arXiv **2607.02770v2**；页眉日期 **2026-06-19**；API published **2026-07-02**，updated **2026-07-24**）
> 官方 PDF：`https://arxiv.org/abs/2607.02770`（**17** 页 A4；Title: *Gemma 4 Technical Report*；741,872 bytes）
> 辅：开发者概述 https://ai.google.dev/gemma/docs/core （Last updated **2026-07-08** UTC；作分发/内存/QAT 产品字段，**不**替代 TR 架构主张）
> 对照笔记：模型与技术报告/厂商报告/Gemini25技术报告深读.md；模型与技术报告/SystemCard/Gemini3ProModelCard.md；模型与技术报告/SystemCard/Gemini37FlashModelCard.md
> **划界（只写开源权重增量）：** 相对已入库 Gemini 2.5 / 3 Pro **闭源卡**与 [[Gemini37FlashModelCard]] Flash **卡**——本卡只录 Gemma 4 **公开权重族**的架构/效率/评测/安全字段；**勿重写** Gemini TR（MoE 口号、1M 窗、Deep Think、TPUv5p/Pathways 细节、FSF 域表等）。可点到 **[[端侧小模型]] on-device** 交叉，**不写**端侧专篇（PLE/mobile QAT 仅作本族效率字段）。
> **禁止编造：** 专家数/路由算法、未给的层宽表、训练 token 总量、视频管线细节若 TR 未写则标「未公开 / 仅 docs」。数字一律锚定 Table / 正文句。

---

## 1. 元信息与一句话抓手

| 字段 | 核实值（PDF / / arXiv API / docs） |
|---|---|
| 标题 | Gemma 4 Technical Report |
| 作者 | Gemma Team, Google DeepMind；联系 `gemma4report@gmail.com` |
| arXiv | **2607.02770v2** \[cs.CL\]（v1 published **2026-07-02**；v2 **2026-07-24**；comment: *17 pages, 2 figures, technical report, updated*） |
| 页数 | **17**（A4） |
| 本地路径 | `https://arxiv.org/abs/2607.02770` |
| 许可 | 正文：**Apache 2.0**（Introduction 末句） |
| 分发（docs） | Kaggle / Hugging Face；官方 QAT 集合见 docs |
| 对照闭源线 | Gemini 2.5 TR / 3 Pro Model Card / 3.7 Flash Model Card **已入库** → 本卡不复述其能力表与 FSF 域结论 |

**型号族（Table 1 + §2 Dense and MoE）：**

| 型号 | 骨架 | 有效 / 总参口径（报告用语） | 模态编码器 |
|---|---|---|---|
| **E2B** | Dense + **per-layer embeddings (PLE)**（沿 Gemma 3n） | **2.3B effective / 5B total** | Audio **305M** + Vision **150M**（冻结） |
| **E4B** | Dense + PLE | **4.5B effective / 8B total** | 同上 305M / 150M |
| **12B** | Dense；**unified encoder-free** | **12B** | **无**独立 vision/audio encoder（线性投影） |
| **26B-A4B\*** | **MoE** | 命名 **A4B**；Abstract 写 **3.8B activated / 26B total**；Table 1 Einsums **24,500M / 2,800M (active)**；Arena 表写 **26B / 4B** → **三处激活口径不一致，照录不调和** | Vision **550M**（无 Audio 列） |
| **31B** | Dense | **31B** | Vision **550M** |

词表：**262k**（与 Gemini Team 2025 tokenizer 同族 SentencePiece：split digits、preserved whitespace、byte-level）。Drafter（MTP）另计：E2B/E4B ~76–77M；12B 400M；26B-A4B 430M；31B 500M（Table 1）。

**一句话抓手：** Gemma 4 是 Google **Apache 2.0 开源权重**新世代（dense **E2B–31B** + **26B-A4B MoE**）：相对闭源 Gemini 卡，公开了 **参数分项表、local/global 注意力与 p-RoPE/KV 复用配方、12B encoder-free、thinking 控制符、QAT/MTP 效率件与可复现评测表**——产品能力口号与 Gemini 族同源（原生多模态 + reasoning），但文档形态是 **17 页可部署开源 TR**，不是 2.5 那种闭源旗舰长报告，也不是 3.7 Flash 那种「defer 至前代卡」的短增量卡。

---

## 2. 相对 Gemini 2.5 / 3 Pro / 3.7 Flash 的「开源增量」对照

> 左列锚本 PDF；右列仅作「已入库闭源卡已覆盖面」提示，**禁止**把 Gemini 未公开数字外推到 Gemma，也**禁止**把 Gemma 数字回填为 Gemini 架构主张。

| 维度 | Gemini 2.5 / 3 Pro / 3.7 Flash（已入库闭源卡） | **Gemma 4（本 PDF + docs）** | 开源增量读法 |
|---|---|---|---|
| 文档形态 | 2.5：**73** 页 TR；3 Pro：**10** 页 Model Card；3.7 Flash：**9** 页 Flash 增量卡（大量 defer 3.6） | **17** 页开源 TR + 开发者 docs | 技术可核对深度介于「短卡」与「2.5 长 TR」之间；**有** Table 1 参数分项 |
| 权重 | API / 产品；**无**可下载权重 | **Apache 2.0** 权重；Kaggle / HF（docs） | **本议题核心增量** |
| 参数 / MoE | 仅写 sparse MoE；**总参/激活/专家未公开** | Dense 给出 effective/total；MoE 给出 **26B-A4B** 与 Table 1 active 列（口径见上） | 首次在 Google 近月线给出**可下载族**的参量表；**仍无**专家数/路由超参 |
| Thinking | 2.5：Dynamic + **budget**；3 Pro：**Deep Think** optional；3.7：customizable configurations（无数值表） | **thinking mode**：先输出 reasoning trace；IT 用 `<\|think\|>` 等控制符（Table 11） | 开源侧首次把 thinking **格式化进对话协议**；**无** budget 数值曲线 / Deep Think 专名 |
| 上下文 | 卡内 **up to 1M** / 64K out | docs：小尺寸 **128K**、中尺寸 **256K**；Table 9 评到 **~256k**（MTOB full book）；TR **未**写 1M | **勿**把 Gemini 1M 窗抄到 Gemma；以 docs + Table 9 为准 |
| 多模态 | text/image/audio/video（产品卡） | TR：text + image + audio；**12B encoder-free**；docs 另写 Video（E2B/E4B/12B）→ **Video 管线细节 TR 未展开** | 开源增量在 **编码器规格 + 12B 无编码器范式**；视频留给 docs/待核实 |
| Infra | 2.5：TPUv5p + Pathways 细节；3.x 卡多概括 | Table 2：**TPUv4 / v6e** 芯片数与 data/seq/replica 分片；Slice-Granularity Elasticity；JAX + Pathways + GSPMD + MegaScale XLA；ZeRO-3 | 开源 TR 给出**每型号芯片表**；弹性叙事引用 Gemini Team 2025，**不重写** 2.5 SDC 段 |
| 安全文档 | 3 Pro / 3.7：FSF 版本号 + 外链 Frontier Safety 报告 | §5：与 Gemini **同级 safety evaluations**；列内容政策；相对 Gemma 3/3n 各安全类「major improvements」；FSF 引用 Google DeepMind 2024 介绍文 | **无**本 PDF 内 CCL/域分数表 → **勿**复制 3 Pro/3.7 的 FSF 结论表到本卡 |

**增量一句话：** 相对闭源 Gemini 卡「能力/安全产品字段」，Gemma 4 的可研增量几乎全部落在 **可下载权重 + 公开架构/效率旋钮（PLE、local/global、p-RoPE、KV=K、encoder-free 12B、QAT、MTP）+ vs Gemma 3 的可复现榜**；Gemini 旗舰推理/FSF 叙事 **点到为止、不重写**。

---

## 3. 架构主轴（§2）

### 3.1 骨干共性

- Decoder-only Transformer；**pre-norm + post-norm** + **RMSNorm** + **QKNorm**。
- **Dense + MoE** 并存：见 §1 型号表。
- E2B/E4B：**PLE**（Gemma 3n 同思路）→ effective ≪ total；docs 解释：各层小 embedding 表大、主要是 lookup → **静态权重内存高于 effective 口径**（与 Table 3 / docs 内存表一致）。

### 3.2 长上下文与 KV 效率（架构 × Infra）

| 机制 | 报告主张 | 出处 |
|---|---|---|
| Local : Global 比 | **5:1**（其余）；**4:1**（E2B）；沿 Gemma 3 | Introduction；§2 |
| 位置编码 | Global：**𝑝-RoPE，𝑝=0.25**；Local：标准 RoPE；freq **1M**（global）/ **10k**（local） | §2 |
| Key-as-Value | Global 层 **values = keys**（**除** E2B/E4B）+ KV sharing（Shazeer 2019）→ 称可减 global KV **至多 37.5%** | Introduction；§2 |
| E2B/E4B KV share | 比率 **20/35**、**18/42** | §2 |
| 评测窗 | RULER / LOFT / GraphWalks / MTOB 至 **128k**；大模型 MTOB **~256k** | Table 9（**without thinking**） |

→ 与 Gemini 卡「1M 口号」正交：本族公开的是 **滑动窗口混合注意力 + 部分 RoPE + KV 复用** 的可部署配方，不是百万窗产品声明。

### 3.3 Vision（§2.1 + Appendix）

| 项 | E2B/E4B | 更大型号（除 12B） | 12B |
|---|---|---|---|
| 编码器 | **150M** ViT | **550M** ViT | **无**（见 §3.5） |
| patch | 16 | 16 | 输入 **48×48×3** RGB patch |
| 位置 | axial **2D-RoPE**（non-causal）+ 2D absolute PE | 同 | 2D coordinate PE + LayerNorm |
| $N_{\max}$ soft tokens | **70 / 140 / 280 / 560 / 1120** | 同 | — |
| 冻结 | 预训练阶段冻结 | 冻结 | 无独立 encoder |

Table 10：550M → $d=1152$，MLP 4304，heads 16，layers 27；150M → $d=768$，MLP 3072，heads 12，layers 16。可变宽高比：Algorithm 1 + Figure 2（pooled patch → soft tokens）。

### 3.4 Audio（§2.2）

- E2B/E4B：**305M** USM 风格（2 层 downsampling conv + **12** Conformer）；**40ms** chunks；Mel filterbank；相对 Gemma 3n **680M→305M（−55%）**；**无** vector quantization；连续表示进 LLM；权重冻结。
- 12B：丢弃 Conformer；**16kHz** 下 40ms → **640-d** 向量直接投影（§2.3）。
- 26B-A4B / 31B：Table 1 **无** Audio Encoder 列（仅 Vision 550M）→ 音频能力边界以正文「E2B, E4B and 12B」预训练数据句为准。

### 3.5 Encoder-free 12B（§2.3）——本代架构新点

- **从零训练**的 unified 范式：用轻量投影替代独立 vision/audio encoder。
- Vision：单次大 matmul **~35M** 参数替代 550M encoder；加 2D 坐标 PE + LayerNorm。
- Audio：见上；时序序列 **不再**额外位置编码。
- 动机：减少独立编码器带来的 **memory fragmentation**。
- Table 8：12B 在无专用 audio encoder 下仍给 CoVoST / FLEURS 数字 → 支撑「竞争力可达到」主张。

### 3.6 MoE 26B-A4B

- 报告确认 MoE（Jacobs et al.）；给出 total/active **数量级**与命名 **A4B**。
- **未公开：** 专家个数、共享/路由专家划分、top-$k$、负载均衡损失等。
- docs 补充产品读法：生成时只激活约 **4B**，但 **26B 全量须装入内存**（路由）——与 Table 3「52.0 / 7.6」bf16 双口径一致。
- → 记入「开源 MoE 小号样本」即可；**禁止**按 DeepSeek/Qwen MoE 史重写。

---

## 4. AI Infra 辅线：预训练 · QAT · MTP · 芯片表

### 4.1 预训练（§2.4）

| 项 | 报告 |
|---|---|
| 配方 | 「similar pre-training as Gemma 3」 |
| 数据 | web / code / images / audio（**E2B、E4B、12B**）；cutoff **January 2025** |
| 过滤 | 去污染基准；降低 unwanted/unsafe / recitation |
| Token 总量 / 配比 | **未给** |
| Optimizer / 并行 | ZeRO-3 分片优化器状态；跨 pod 用 Pathways data replica reduction；JAX 单控制器 + GSPMD + MegaScale XLA |

**Table 2（预训练 Infra）：**

| Model | TPU | #Chips | Data | Seq | Replica |
|---|---|---:|---:|---:|---:|
| E2B | v6e | 4,096 | 16 | 8 | 32 |
| E4B | v6e | 6,144 | 16 | 16 | 24 |
| 12B | **v4** | 12,288 | 16 | 16 | 48 |
| 26B-A4B\* | v6e | 6,144 | 16 | 16 | 24 |
| 31B | v6e | 10,240 | 16 | 16 | 40 |

大模型：**Slice-Granularity Elasticity**（引 Gemini Team 2025）→ 局部故障时减少 slice，中断从「many minutes」压到「a few seconds」。

### 4.2 QAT 与内存（§2.5 + Table 3 + docs）

报告聚焦两类表示：

1. **mobile quantization**：per-channel 低比特权重（**int2 + int4 混合**）+ 激活 **int8**
2. **Q4_0**：blockwise（llama.cpp 生态常用）

另：为稳定 **fp16** 推理，每 block 加 scalar scale 限制激活范围。

**Table 3（text-only，Gb；+ int8 KV @ 32k）：**

| Model | bf16 | Quantized | +KV @32k |
|---|---:|---:|---:|
| E2B | 4.6 | 0.8† | +0.05 |
| E4B | 9.0 | 2.3† | +0.14 |
| 12B | 24.0 | 7.65‡ | +0.28 |
| 26B-A4B\* | 52.0 / 7.6 | 16.2 / 2.8‡ | +0.28 |
| 31B | 64.0 | 19.2‡ | +1.10 |

† mobile；‡ Q4_0。

编码器 QAT：150M 图像 **W8A8** → 前向内存约 **400→200 MB**，相对 Gemma 3n 新硬件延迟 **−44%**；音频盘占用 **390→87 MB（−78%）**（权重 {2,4,8} bit 分层）。

**docs 内存表（含开销约 20%；与 Table 3 口径不同，勿混并）：** E2B BF16 11.4 GB / Q4_0 2.9 GB / Mobile 1.1 GB；…；31B BF16 69.9 GB / Q4_0 17.5 GB。docs 另给 QAT 下载后缀路由（GGUF / w4a16-ct / mobile-ct / assistant draft 等）——**产品工程字段**，交叉 **[[端侧小模型]]**，本卡不展开端侧部署手册。

### 4.3 MTP Drafter（§2.6）

- 与主模型同训的小型 **自回归 multi-token prediction** 头，供 **speculative decoding**。
- 输入：主模型上一布 last-layer activations + token embeddings；4 层 Transformer **cross-attend** 主模型 KV（Figure 1）。
- Drafter 宽度：E2B/E4B **d=256**；26B-A4B/31B **d=1024**；结构 **3 local + 1 global**。
- E2B/E4B 解码优化：词表投影改为 **token cluster top-k** → 最终 matmul **$d×262k → d×4096$**，接受率相近。
- → 与 B7 / 预定 **[[EAGLE3投机解码]] EAGLE-3** 划界：本卡只记 Gemma 官方 MTP 附头，不写投机解码通史。

---

## 5. Instruction Tuning 与对话协议（§3 + Table 11）

- 后训练「similar to Gemma 3」；**显著差异 = thinking mode**（先 trace 再答）。
- 数据过滤：PII / unsafe·toxic / mistaken self-id / 重复；加入 attribution、hedging、refusal 子集以抬事实性且「不伤其他指标」。
- PT vs IT：共享 tokenizer；PT 末 **`<eos>`**，IT 末 **`<turn|>`**；微调须加对应结束符。
- **原生 system turn**（docs 强调；Table 11 有 `<|turn>system`）。

**Table 11 控制符（照录）：**

| 用途 | 标记 |
|---|---|
| Thinking 开关 | `<\|think\|>`（置于 leading system turn） |
| Thinking trace | `<\|channel>thought ...<channel\|>` |
| System / User / Model | `<\|turn>system` / `user` / `model` |
| End of turn | `<turn\|>` |
| Tool declaration / call | `<\|tool>declaration:...<tool\|>`；`<\|tool_call>call:...<tool_call\|>` |

须显式 `[BOS]`（或 `add_bos=True`）；函数声明细节「见官方文档」。

---

## 6. 评测摘录（相对 Gemma 3，非相对 Gemini 闭源榜）

> 主对照是 **Gemma 3 27B**（Table 5/6/9）与 Arena 开源榜（Table 4）。**不要**与 [[Gemini37FlashModelCard]] / 3 Pro 第 5 页闭源友商表无脚注合并。

### 6.1 Arena Text（Table 4，as of **2026-06-19**）

| 模型 | Elo ±CI | 开源 | 类型 | 参 |
|---:|---|---|---|---|
| （尺度）Claude Fable 5 | 1508 ±9 | no | — | — |
| **Gemma 4 31B** | **1451 ±8** | yes | Dense | 31B |
| Gemma 4 26B-A4B | 1438 ±8 | yes | MoE | 26B / 4B（表内写法） |
| Gemma 3 27B | 1366 ±4 | yes | Dense | 27B |

报告主张：31B 为榜上 **leading dense open model**；31B 与 26B-A4B「rival much larger」开源 MoE。

### 6.2 静态文本 / agent（Table 5；**thinking**，Gemma 3 27B 为 non-thinking）

摘显著 Δ（31B vs Gemma 3 27B）：

| Bench | Gemma 4 31B | Gemma 3 27B |
|---|---:|---:|
| MMLU Pro | 85.2 | 67.6 |
| AIME 2026 no tools | 89.2 | 20.8 |
| LiveCodeBench v6 | 80.0 | 29.1 |
| Codeforces Elo | 2150 | 110 |
| GPQA Diamond | 84.3 | 42.4 |
| HLE | 19.5 | — |
| MRCR v2 8-needle 128k | 66.4 | 13.5 |
| Tau2 retail | 86.4 | 6.6 |

报告叙事：E2B 约以 **10× 更少参数**大致追平 Gemma 3 27B 若干项（正文句；逐项见原表）。

### 6.3 Vision（Table 6 @ $N_{\max}=1120$；Table 12 @ 280）

高分辨率例：31B MMMU Pro **76.9**、MATH-Vision **85.6**、InfographicVQA **92.0**；E4B 多项 ≥ Gemma 3 27B（non-thinking + Pan & Scan）。低分辨率 Table 12 同步下降（如 InfographicVQA 31B 92.0→82.8）。

### 6.4 Audio（Table 7/8）

相对 Gemma 3n 同档：翻译相对改进约 **12%/10%**（E2B/E4B），转写约 **17%/12%**，同时音频编码器盘占用 −78%。12B Table 8 证明 encoder-free 仍可竞争。

### 6.5 Long context（Table 9，**without thinking**）

例：RULER 128k — 31B **96.4** vs Gemma 3 27B **66.0**；LOFT Text Retrieval 128k — **79.5** vs **8.6**；MTOB ~256k 仅 **31B / 26B-A4B / 12B** 有 full-book 列。

---

## 7. 责任 / 安全（§5）——开源侧字段，不重写 Gemini FSF

- 主张：开源模型进入企业基座 → provenance/security 更重要；Gemma 4 经历与 **Gemini models 同等严格**的 safety evaluations。
- 政策禁止类（摘要）：CSAM/exploitation；dangerous content；sexually explicit；hate；harassment。
- 缓解：预训练过滤 PII/敏感；post-training 对齐；测试时 **不加 safety filters** 以测固有行为；称 text↔image 各尺寸「minimal policy violations」，相对 Gemma 3/3n 各类安全「major improvements」，并保持低 unjustified refusal。
- 伦理关注点：bias/fairness；misinformation/misuse（指向 Responsible Generative AI Toolkit）；隐私（开发者须本地合规）。
- 框架引用：Frontier Safety Framework（Google DeepMind, **2024** 介绍博文）——**本 PDF 无** 3.7 那种 April-2026 FSF 域表 / TCL alert。
- → 交叉 B5 / [[可扩展监督与弱到强]] 即可；**禁止**把 3 Pro「CCL not reached」表抄入本卡。

---

## 8. 与 [[端侧小模型]] / 仓库其他议题的交叉（不展开）

| 议题 | 本卡只点到的咬合 |
|---|---|
| **[[端侧小模型]] on-device SLM** | E2B/E4B PLE、mobile QAT、LiteRT-LM 内存列、Pixel/Chrome 叙事 → **专篇留给 [[端侧小模型]]**（可与 MobileLLM/Phi-4 对照） |
| B7 / **[[EAGLE3投机解码]]** 投机解码 | 官方 MTP drafter ≠ EAGLE-3 通史 |
| [[多模态架构脉络]] 多模态 | encoder-free 12B 作「去掉独立编码器」开源样本 |
| [[长上下文位置编码与系统侧]] 长上下文 | local/global + p-RoPE + KV 复用；窗长以 128k/256k 评测为准 |
| [[推理时扩展TestTimeScaling]] thinking / TTS | thinking 控制符与轨迹格式；**无** budget 曲线 |
| MedGemma（[[MedGemma医学专科]]） | 本 TR 含 MedXPertQA MM 分数，**不是**医学专科报告 |

---

## 9. 待核实 / 报告内张力

1. **26B-A4B 激活参口径：** Abstract **3.8B** vs Table 1 **2.8B (active)** vs Arena/docs **~4B** ——三处并存，引用时标明来源。
2. **Video：** docs 写 E2B/E4B/12B native video；TR 正文主轴 text/image/audio → 视频编码/采样细节 **待 docs/模型卡补核**。
3. **训练 token 总量、MoE 专家配置、thinking budget 数值：** TR **未给**。
4. **与 Gemini 同 tokenizer / 同安全评估流程：** 报告明文；**不**意味权重或数据配比相同。

---

## 10. 可跟读摘要（中文）

Gemma 4 把 Google 近月的「多模态 + 推理」能力，落成一套 **可下载的 Apache 2.0 权重族**：小模型靠 **PLE + 缩小的视听编码器 + mobile QAT** 打端侧；12B 试 **无独立编码器** 的统一投影；中上尺寸给 **31B dense** 与 **26B-A4B MoE**，并用 **local/global 注意力、p-RoPE、KV 复用、MTP 投机头** 换长文与解码效率。相对已入库的 Gemini **闭源**卡，值得记进仓库的是这些 **公开配方与对 Gemma 3 的跃迁表**，而不是再写一遍 Gemini TR。端侧产品化细节留给 **[[端侧小模型]]**。

---

## 11. 来源与抽取

| 源 | 路径 / URL |
|---|---|
| 一手 PDF | `https://arxiv.org/abs/2607.02770` ← https://arxiv.org/pdf/2607.02770 |
| 文本抽取 | |
| 辅 docs | https://ai.google.dev/gemma/docs/core （2026-07-08） |
| 对照 | 模型与技术报告/厂商报告/Gemini25技术报告深读.md；模型与技术报告/SystemCard/Gemini3ProModelCard.md；模型与技术报告/SystemCard/Gemini37FlashModelCard.md |

**检索截止：** 2026-09-22（Asia/Shanghai，CST）。数字与断言均来自上述 PDF/docs；未出现的专家拓扑、token 预算、视频栈细节未写入主张表。

## 相关笔记

- [[Gemma4技术报告深读|Gemma 4]]
- [[AXK2技术报告深读|AX-K2]]
- [[UIVenus2GUI智能体|UI-Venus-2]]
- [[宪法分类器防御|Constitutional Classifiers]]
- [[过程奖励模型PRM谱系|Process Reward Models]]

