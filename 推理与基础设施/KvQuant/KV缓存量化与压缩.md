---
title: "KV Cache 量化与极限压缩"
topic: KV缓存量化与压缩
date: 2026-09-22
lines: [AI Infra, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2402.02750
 - https://arxiv.org/abs/2401.18079
 - 模型与技术报告/厂商报告/DeepSeekV41Flash深读.md
arxiv: ["2402.02750", "2401.18079"]
archived: 2026-09-22
---

# KV Cache 量化与极限压缩

> **定位**：P1 横切——立 **K/V 非对称量化与误差轴**（per-channel Key、per-token Value、RoPE 前后、残差窗 / dense-sparse），**不**写权重量化通史，**不**重写 V4.1-Flash 产品解全文（见 [[DeepSeekV41Flash深读]]）。
> **攻坚线**：**AI Infra（主）** + **数学原理 / 量化误差（辅）**。
> **刻意不写**：AWQ/GPTQ/SmoothQuant 权重史；token eviction / H2O / StreamingLLM 正文；PagedAttention / continuous batching（见 [[长上下文位置编码与系统侧]]、B7、[[连续批处理与Orca]]）；CSA2 / CED / SWA Bounded Replay 机制全文（[[DeepSeekV41Flash深读]]）。
> **禁止编造**：公式、配置、评测数字一律取自官方 PDF（2026-09-22 CST）与已入库 [[DeepSeekV41Flash深读]]；两文互相称 concurrent，不以「谁先谁后」叙事替代方法差异。

---

## 一、问题动机：为何 KV 成为瓶颈、为何「对称 per-token」不够

### 1.1 瓶颈从权重迁到 KV

两篇入口文同一观察（KIVI Abstract / §1；KVQuant Abstract / Fig 1）：

| 设定 | 现象（原文口径） |
|---|---|
| **短上下文 / 小 batch** | 权重主导显存与带宽 |
| **长上下文 / 大 batch** | **KV cache** 主导；生成阶段反复把整段 KV 从 HBM 装入 SRAM，算核常闲 |
| 量级例（KIVI） | 540B PaLM、batch 512、ctx 2048 → KV 约 **3 TB**，约参数的 **3×**（Pope et al. 转述） |
| 量级例（KVQuant） | LLaMA-7B：短序列权重主导 → 128K 时 KV 主导；3-bit 路径称 **4.8×** 激活足迹压缩（Fig 1 / Table 1） |

**与仓库边界：** [[长上下文位置编码与系统侧]] / B7 已谈窗口与引擎；本篇只补「**把已有 K、V 张量压到更低比特**」这一正交手段——不替代稀疏注意力、不替代 eviction。

### 1.2 误差轴抓手（读两文前先立）

解码注意力（KIVI 式 1）：$A=\mathrm{Softmax}(t_Q X_K^\top)$，$t_O=A X_V$。

| 张量 | 分布观察（两文一致） | 量化维度含义 |
|---|---|---|
| **Key** | 少数 **固定 channel** 幅值极大（KIVI Fig 2；KVQuant Fig 2 pre-RoPE） | **per-channel**：scale/zero 沿 channel 共享 → 大通道误差不污染普通通道 |
| **Value** | **无明显固定通道 outlier**；注意力对 $X_V$ 是稀疏加权求和（KIVI 式 2） | **per-token**：误差困在单 token，重要 token 不被旁路 token 的量化拖垮 |
| **RoPE** | 旋转把成对 channel 混在一起 → post-RoPE Key 的通道一致性变差（KVQuant Fig 2） | 是否在 **RoPE 前**量化 Key，成为第二误差轴 |

**共同结论（OB / 消融口径）：** 把 K、V 都做成「按 token 的均匀 INT」在 **≤3–4 bit** 会崩；**K per-channel + V per-token** 是两文共享的非对称起点。分歧在：流式残差窗 vs 离线标定 / 非均匀数据类型 / 稀疏 outlier / Attention Sink。

---

## 二、KIVI（Liu et al.）— Tuning-Free 非对称 2-bit

| 项 | 值 |
|---|---|
| 标题 | *KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache* |
| 页眉 | **arXiv:2402.02750v2** \[cs.CL\] **25 Jul 2024** |
| 会议 | ICML 2024（Proceedings PMLR 235） |
| 本地 | `https://arxiv.org/abs/2402.02750`（15 页） |
| 代码 | https://github.com/jy-yuan/KIVI |

### 2.1 核心设计：非对称轴 + 残差窗解决流式 per-channel

1. **Key → per-channel group-wise**；**Value → per-token group-wise**（§3.1–3.2）。
2. **流式障碍：** 新 token 的 Key 无法立刻完成「跨 token 的 channel 统计」。做法：把 Key（及 Value）拆成
 - **Grouped** $X_{K_g}/X_{V_g}$：每 $G$ token 成组后量化存低比特；
 - **Residual** $X_{K_r}/X_{V_r}$：最近至多 $R$ token **保留全精度**；满窗则量化并拼回 grouped（§3.3；Fig 3；App. Algorithm 1）。
3. Attention logits 用 tiled / mix-precision matmul：$A_g$ 对量化 Key，$A_r$ 对残差 FP Key，再 concat（式 3）。
4. Prefill：层间仍传 **精确** K/V；**仅缓存侧**保留量化 KV（§3.3）。

**默认超参（§4.1）：** $G=32$，$R=128$（消融亦测 $R\in\{32,64,96,128\}$）。文称 $R$ 相对长序列可忽略，但对 **GSM8K** 等难生成任务，「局部全精度滑窗」关键（假量化全量 2-bit 会大掉，真 KIVI 掉点小）。

### 2.2 为何 V 不能 per-channel（误差轴辅）

Table 2（Llama-2-13B，层/头平均）：

| 量 | Per-token | Per-channel |
|---|---:|---:|
| Key 相对重构误差 $\|X_K-X_K'\|_F/\|X_K\|_F$ | 13.67 | **4.55** |
| Attention score 相对误差 | 47.00 | **9.60** |
| Value 相对重构误差 | 4.57 | 3.73（接近） |
| 输出相对误差 $\Delta=\|AX_V-AX_V'\|_F/\|AX_V\|_F$ | **3.55** | **49.89**（约 **15×**） |

解释（§3.2）：注意力稀疏 → $t_O$ 只由少数重要 token 的 Value 行加权；**per-token** 把误差关在 token 内；**per-channel** 让跨 token 误差搅进同一重要行 → $\Delta$ 爆炸。这与「Value 看起来没有固定通道 outlier」并不矛盾——**下游算子结构**决定量化轴，不只看边缘分布。

### 2.3 假量化配置崩溃 vs 真 KIVI（Table 1 / Table 3 摘录）

假量化（全 token 量化、无残差窗；组大小 32）在 Llama-2-13B CoQA / TruthfulQA：

| 配置 | CoQA | TruthfulQA |
|---|---:|---:|
| 16bit | 66.37 | 29.53 |
| 2bit (K-C, V-T) | **63.53** | **28.60** |
| 2bit (K-T, V-T) | 52.93 | 24.98 |
| 2bit (K-C, V-C) / (K-T, V-C) | ~2.8 | ~0.3–0.7（崩溃） |

真 KIVI-2（有残差窗）例：Llama-2-7B GSM8K **13.50 → 12.74**；Llama-2-13B **22.67 → 20.77**；Mistral-7B **38.36 → 36.01**（Table 3）。Falcon-7B（MQA，KV 已极瘦）文称常需 **KIVI-4** 才能稳住，2-bit 掉点更大。

LongBench 均值：Llama2-7B 16bit **44.52** / KIVI-2 **44.27**；Mistral-7B **46.58 → 45.85**（Table 4）。NIAH（Fig 4）：Llama-3-8B-Instruct / Mistral-7B-Instruct-v0.2 上 2-bit 仍可保检索轮廓。

### 2.4 系统收益（摘要主张 + Fig 5）

- Llama-2-7B：**约 2.6×** peak memory（含权）↓ → 同卡可 **至多 4×** batch → ShareGPT 合成负载上吞吐 **2.35×–3.47×**（A100-80GB；$R$ 测 32 与 128）。
- 实现：反量化与 Q_MatMul **CUDA 融合**；group-wise 量化 **Triton**；与 weight-only 量化兼容（§3.3 / §4.2.4）。

**一句话：** KIVI = **无微调**的「K 通道 / V token + 局部 FP 残差窗」，把 **2-bit** 推到可服务；硬任务靠 $R$ 窗兜底，不是靠假量化全量 2-bit。

---

## 三、KVQuant（Hooper et al.）— 标定 + 非均匀 + Dense-Sparse 冲长上下文

| 项 | 值 |
|---|---|
| 标题 | *KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization* |
| 页眉 | **arXiv:2401.18079v6** \[cs.LG\] **28 May 2025** |
| 会议 | NeurIPS 2024 |
| 本地 | `https://arxiv.org/abs/2401.18079`（27 页） |
| 代码 | https://github.com/SqueezeAILab/KVQuant |

### 3.1 四件套 + Attention Sink（§3）

| # | 组件 | 作用（原文） |
|---|---|---|
| (i) | **Per-Channel Key Quantization** | 对齐 Key 通道 outlier；Value 仍偏 **per-token**（§3.1；与 KIVI concurrent，文内 [26]） |
| (ii) | **Pre-RoPE Key Quantization** | 在旋转前量化 $K_n$，推理时 dequant 后 **on-the-fly 施 RoPE**（融合核 §3.7）；消融称 3-bit LLaMA-7B Wikitext-2 约 **+0.82** PPL 收益（§3.2） |
| (iii) | **nuqX**：层敏感度加权非均匀码本 | 离线 Fisher 加权 k-means（式 1）得 per-layer signposts；在线只做 per-vector rescale（§3.3） |
| (iv) | **Per-Vector Dense-and-Sparse** | 按 channel/token **各自**阈值隔离约 **1%** outlier 存高精，压动态范围（§3.4）；相对全局阈值更贴向量粒度 |
| (+) | **Attention Sink-Aware** | 首 token 对量化极敏感 → **首 token 留 fp16**；标定亦忽略首 token（§3.5） |

**相对 KIVI 的工程分叉（§3.1 / §3.6）：**
- KIVI：在线 group + **残差 FP 窗**，无需标定。
- KVQuant：Key 的 per-channel **scale/zero 离线标定**，避免每来一个 token 就重算整列统计；Value 的 per-token 统计 / outlier 阈值可在线（可卸到 CPU）。文称由此可 **无 grouping** 地做准 per-channel Key。

### 3.2 主表数字（Table 1，Wikitext-2 PPL；128K KV 体积估计）

LLaMA-7B 摘录（baseline PPL **5.68**，fp16 KV **64.0 GB** @128K）：

| Method | PPL | KV (GB) |
|---|---:|---:|
| int3 / nf3 | 10.87 / 7.33 | 12.0 |
| ATOM-3bit / FlexGen-3bit | 6.17 / 5.93 | 12.6 / 13.2 |
| **KVQuant-3bit** | **5.87** | **12.0** |
| **KVQuant-3bit-1%** | **5.75** | **13.3** |
| KVQuant-2bit / 2bit-1% | 7.23 / **6.01** | 8.0 / 9.3 |

摘要口径：3-bit 在 Wikitext-2 / C4 上 **PPL 退化 < 0.1**（相对 fp16）；相对基线约 **4.8×** 激活压缩。自定义 CUDA：相对 fp16 matvec，LLaMA-7B 上 Key/Value 可达约 **1.7×**（§4.4 / Abstract）。

### 3.3 「百万 / 千万」上下文叙事（Abstract / App. A）

在 **估算** KV 体积前提下（Table 7–8）：

- LLaMA-7B **nuq2**：单卡 A100-80GB 可撑约 **1M** ctx（KV ≈ 64 GB 量级）；
- 8 卡系统可估算到约 **10M**；
- LLaMA-65B：**nuq2-1%** 等配置用于「单卡 32K」等体积账（权重 4-bit + KV 压缩的组合叙述，见 App. A）。

**读法：** 这是 **显存可行性估算 + PPL/检索评测**，不是声称已开源 10M 产品服务；Passkey / RULER 等另表（§4；与 KIVI 对照时注明 GQA 支持差异）。

### 3.4 与 KIVI 对照时文内自陈差异

- Passkey：KVQuant 量化 **含首 token 外的全序列**；KIVI 保留尾部残差 FP 窗 → 「尾部友好」叙事不同（§4）。
- RULER（Table 4 叙述）：称 3-bit KVQuant 在相近平均比特下优于 KIVI；2-bit KVQuant 可达相近精度且比特更低（以文内表为准，此处不逐格抄全）。
- Llama-2-70B-32K：文称 KIVI 对 LLaMA 侧 **未支持 GQA**，故未做该对照。

**一句话：** KVQuant = **离线敏感码本 + Pre-RoPE per-channel Key + per-vector 1% sparse + Sink token**，主打 **3-bit 近无损 PPL** 与极端上下文显存账；与 KIVI 共享非对称轴，系统处方不同。

---

## 四、与 V4.1-Flash 部署交叉（只串轴，不重写 [[DeepSeekV41Flash深读]]）

权威数字与机制全文见 模型与技术报告/厂商报告/DeepSeekV41Flash深读.md §3.3 / Abstract。本处只立 **对照轴**：

| 轴 | KIVI / KVQuant（方法文） | DeepSeek-V4.1-Flash（产品 TR） |
|---|---|---|
| 目标对象 | 稠密 / GQA 类开源 Llama·Mistral 等的 **标准 KV 张量** | **CSA2 main KV**（已跨层复用 / 序列压缩）+ 另路 **SWA KV** |
| 比特形态 | INT / **nuq** 2–4 bit；可选 1% FP outlier | **FP4** main KV：文称 **E2M1 + 每 16 channel 一个 E4M3 scale**（类 NVFP4，去二级 global scale） |
| 训练介入 | KIVI **tuning-free**；KVQuant **离线标定**（非端到端重训） | **Post-training QAT** 扩到 main KV；V4 已对 indexer Q/K 做过 FP4 QAT |
| RoPE 时机 | KVQuant 主张 **Pre-RoPE** Key；KIVI 沿缓存流式轴（未以 Pre-RoPE 为主贡献） | 文称 **RoPE 之后**量化；RoPE 前量化「仅边际收益且解码开销↑」 |
| 非对称保留 | K≠V 量化维；残差窗 / Sink / sparse | **SWA KV 仍 FP8**（对量化敏感）；main KV 走 FP4 |
| 压缩乘积 | 单靠低比特（+outlier） | **CSA2 层复用 × FP4** → HBM global KV **890 B/token ≈ V4-Flash 的 1/4**；再乘 SWA Bounded Replay → persistent ≈ **1/8** |
| 用途表述 | 省 KV 存储 / 抬 batch·上下文 | FP4 **省存储而非加速 matmul**；**先反量化再注意力** |

**串联读法（勿混）：**

1. **学术非对称 INT/NUQ** 证明：误差由 **K/V 算子角色 + RoPE + outlier** 决定，不是「一律 per-token 4-bit」口号。
2. **V4.1** 在已稀疏/复用的 main KV 上再做 **硬件友好 FP4 QAT**，并显式留下 SWA 高精——是 **架构压缩 × 格式压缩** 的部署解，不是对 KIVI/KVQuant 的逐条复刻。
3. RoPE 前后结论 **相反方向都有文献支持**：KVQuant（开源 RoPE 模型、标定路径）vs V4.1（自家 QAT + 解码开销权衡）。跟读时以 **各自问题设定** 为准，禁止合成「统一最优 RoPE 时机」。

---

## 五、误区（跟读用）

1. **「KV 量化 = 权重量化缩小版」** — 流式追加、无法随便 GPTQ；K/V 下游算子不同，轴必须非对称（KIVI OB1–3）。
2. **「一律 per-token 最贴自回归」** — 实现方便，但对 Key 的通道 outlier 在 ≤2–3 bit 会炸 attention（两文 Fig/表）。
3. **「假量化分数 = 可上线分数」** — KIVI：全量 2-bit 假量化 GSM8K 大掉，真算法靠 **残差 FP 窗**才接近 16-bit。
4. **「Pre-RoPE / Post-RoPE 有唯一正确答案」** — KVQuant 与 V4.1 结论依赖路径（标定 vs QAT、是否融合 RoPE 核）；只记 **各自文内消融**。
5. **「eviction / CSA / MLA = 量化」** — 正交：少存 token / 少存层或 entry / 低比特存 entry；本篇只覆盖第三类。
6. **「890 B/token 可从 KIVI 2-bit 外推」** — 890 是 V4.1 **CSA2+FP4** 产品足迹，禁止用 Llama 稠密 KV 公式反推。
7. **「10M context 已等于生产 SLA」** — KVQuant 为显存估算 + 质量评测叙事；落地仍受内核、页表、调度、前缀缓存等约束（见 B7 / [[DeepSeekV41Flash深读]] 部署章）。

---

## 六、待核实 / 非本篇范围

- KIVI Table 3 全模型逐格、LongBench 分任务、KVQuant RULER/Passkey 全表：本篇只摘主结论与代表性格。
- 两文后续开源实现是否已并入 vLLM/SGLang 默认路径：**不跟代码默认值**。
- MLA / DSA / CSA2 与「per-channel Key」在 **压缩 latent** 上是否同构：V4.1 PDF 未用 KIVI 术语复述 → **禁止类推证明**。
- 权重 INT4 + KVQuant 联合表（KVQuant Table 5 等）未展开。

---

## 七、引用

1. Liu, Yuan, Jin, Zhong, Xu, Braverman, Chen, Hu, 2024. *KIVI: A Tuning-Free Asymmetric 2bit Quantization for KV Cache* — arXiv:**2402.02750**；ICML 2024；本地 `https://arxiv.org/abs/2402.02750`。
2. Hooper, Kim, Mohammadzadeh, Mahoney, Shao, Keutzer, Gholami, 2024/2025. *KVQuant: Towards 10 Million Context Length LLM Inference with KV Cache Quantization* — arXiv:**2401.18079**；NeurIPS 2024；本地 `https://arxiv.org/abs/2401.18079`。
3. 交叉部署：DeepSeek-AI, *DeepSeek-V4.1-Flash* — arXiv:**2609.19969**；笔记 模型与技术报告/厂商报告/DeepSeekV41Flash深读.md（FP4 main KV / CSA2 / 890 B/token；**勿在本篇重写**）。
4. 背景交叉（不展开）：[[长上下文位置编码与系统侧]] 长上下文；B7 推理引擎；Pope et al. 服务化 KV 体积论述（KIVI §1 转述）。

## 相关笔记

- [[Gemini37FlashModelCard|Gemini 3.7 Flash]]
- [[KV缓存量化与压缩|KV Cache 量化]]
- [[连续批处理与Orca|Continuous Batching / Orca]]
- [[机制可解释性入门|机制可解释性]]
- [[世界模型与VJEPA|World Models / V-JEPA]]
- [[SpeechLLM语音语言模型|Speech LLM]]
- [[视觉语言动作谱系|Robotics / VLA]]
- [[智能体长程记忆|Agent 长期记忆]]
- [[可扩展监督与弱到强|Scalable Oversight]]

