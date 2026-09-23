---
title: "Quantization-aware training：ZeroQAT（端侧 QAT @ 推理成本级）"
topic: ZeroQAT量化感知训练
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2509.00031
arxiv: ["2509.00031"]
related: ["KV缓存量化与压缩", "Gemma4技术报告深读", "端侧小模型"]
archived: 2026-09-22
---

# Quantization-aware training：ZeroQAT（端到端 on-device QAT @ 推理成本）

> **定位**：**P1**——仓库缺 **训练感知量化 / 端侧 QAT** 一手报告；锚点是 Tan et al. *End-to-End On-Device Quantization-Aware Training for LLMs at Inference Cost*（arXiv **2509.00031v2**）。主写 **零阶（ZO）前向估计梯度 → 去掉反传** 的 Full/PEFT QAT，以及 **可学习平滑 + 可学习权重量化器 + 轻量 Q/V 变体**；辅写精度—比特—内存表与 OnePlus 12 端侧字段。
> **攻坚线**：**架构思想（主）**——ZO-QAT 为何绕开 STE、如何端到端联训模型与量化参数；**评测字段（辅）**——W2A16 / W4A4 的 PPL·零样本·下游 Acc，以及 A100 / 手机内存—时延。
> **硬划界（禁止重写）**：
> - **≠ [[KV缓存量化与压缩]] KV 量化**：本篇是 **权重 / 激活的训练期 QAT**，不是解码期 K/V cache 非对称压缩（KIVI / KVQuant）。
> - **≠ [[端侧小模型]] on-device SLM 通史**：不写 MobileLLM / Phi-4 / LiteRT 产品谱系；只取「端侧能跑 QAT」这一效率接口。
> - **可交叉 [[Gemma4技术报告深读]] 一句**：Gemma 4 TR / docs 有 **产品侧 mobile QAT 与内存表**（int2+int4 权重、激活 int8 等）——那是**已训好权重的分发字段**，不是本篇 ZO 训练算法；详见 [[Gemma4技术报告深读]] §4.2，此处不展开。
> **禁止编造**：主张、公式编号、表数字一律锚定官方 PDF（2026-09-22 CST）；文内未给 GitHub / 代码哈希 → **标「PDF 未声明开源入口」**，不虚构仓库。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Tan, Song, Lu, Li, Liu, Hong, Ding, Li, Zhai, Huang, Niu, Yuan；*End-to-End On-Device Quantization-Aware Training for LLMs at Inference Cost* | arXiv:**2509.00031v2** \[cs.LG\] **29 Sep 2025**；`https://arxiv.org/abs/2509.00031`（**21** 页 letter；1,591,856 bytes） | ZO-QAT 方法 + 预训练/微调/端侧实验 |
| **抽取** | | （1240 行） | 跟读底本 |
| **机构** | UGA / UNT / Northeastern / Minnesota / Virginia / Stevens | 文头 | 署名 |

**一句话抓手：** 传统 QAT 因反传显存「贵到只能放弃」→ PTQ 主导部署；ZeroQAT 用 **只做前向的零阶梯度估计** 把 QAT 的内存压到 **接近推理**，并同时支持 **低比特权重+激活**，还给出只训 Attention **Q/V** 的轻量微调变体——文称可在 **单卡 8GB** 上微调 13B、在 **OnePlus 12** 上微调 OPT-6.7B。

**跟读口诀：**

`
PTQ（便宜、低比特易崩） vs FO-QAT（准、反传显存炸）
 ↓
 ZeroQAT = ZO 前向差分估计 ∇
 + 可学习通道平滑 (s, δ)
 + 可学习步长/零点/裁剪 (Δ, z, α, β)
 +（微调）冻大量参数、只留 Q/V 全精度
 → 端到端目标 ≈ 任务损失，不是逐层重建代理
`

---

## 二、议题边界：训练期 W/A QAT，不是 KV、不是 SLM 通史

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[KV缓存量化与压缩]]** KV cache 量化 | 「推理期也有量化压力」的相邻意识 | per-channel Key / per-token Value、残差窗、KIVI/KVQuant 公式 |
| **[[端侧小模型]]** on-device SLM | 「端侧内存预算极紧」的产品压力面 | MobileLLM 深度—宽度、Phi-4-mini、PLE 通史 |
| **[[Gemma4技术报告深读]]** Gemma 4 | **一句交叉**：开源权重族的 **mobile QAT 分发/内存表**（§4.2） | local/global 注意力、p-RoPE、MTP、整份 TR |
| **B7** 推理引擎 | 无直接重叠；勿把本篇写成 vLLM/GGUF 手册 | PagedAttention、连续批 |

### 2.2 问题立轴（§1–§3，跟读）

据摘要与 §3：

1. **PTQ 便宜但缺端到端适配**：低比特时 range-based（如 SmoothQuant）与 approximation-based（如 OmniQuant）都可能崩。
2. **近似 PTQ 的两病（§3.1，以 OmniQuant 为例）**：
 - **累积误差**：浅层重建变好、深层收益衰减（Figure 1）。
 - **目标不一致**：层重建损失 ↓ 时，PPL 仍可抖（Figure 2）——局部代理 ≠ 全局任务。
3. **微调后的模型更脆**：Table 2 上 Llama2-7B，W4A4 微调 Acc：SmoothQuant **32.9**、OmniQuant **38.8** vs FP ZO **66.0**。
4. **FO-QAT 原则对、资源不对**：要存激活 / 反传梯度 / 优化器状态；文举 Llama-7B 微调可能「上百 GB」量级（§1）。PEFT-QAT（QLoRA / EfficientQAT 等）在 **W4A4 联合量化** 上仍吃力（Table 2：EfficientQAT W4A4 PPL **76.32**）。
5. **本文主张的缺口**：已有 ZO+量化工作多偏 **weight-only**；作者自称 ZeroQAT 是 **首个** 在极低比特下同时稳住 **W+A**、且内存近推理的端到端 QAT（§3.2 / 摘要口径——**记作作者宣称，不作仓库裁决**）。

**Table 2 速览（Llama2-7B，文内主对照表）：**

| Method | Category | Pretrain PPL W6A6 / W2A16 / W4A4 | Finetune Acc W6A6 / W2A16g128 / W4A4 |
|---|---|---:|---:|
| ZO (FP16) | — | 5.47（中列占位） | 66.0 |
| SmoothQuant | Range PTQ | 6.20 / 100.23‡ / 83.12 | 57.2 / 27.7‡ / 32.9‡ |
| OmniQuant | Approx PTQ | 5.87 / 37.37 / 14.26 | 63.9 / 40.6‡ / 38.8‡ |
| EfficientQAT | QAT | 5.60 / 33.40 / 76.32‡ | 66.4 / 45.4 / 28.6‡ |
| **ZeroQAT** | QAT | **5.76 / 29.61 / 12.95** | **65.3 / 54.1 / 55.7** |

‡ 文注：该方法本质上不适合该设定，列出以示局限。

---

## 三、方法站：ZeroQAT（§4）

### 3.1 背景公式：非对称均匀量化（§2）

文聚焦 **asymmetric uniform quantization**（自称精度更好）：

$$
X_{\mathrm{INT}}=\mathrm{clamp}\Big(\Big\lceil\frac{X_{\mathrm{FP16}}}{\Delta}\Big\rfloor+z,\;Q_N,\;Q_P\Big)
$$

- 非对称：$Q_N=0,\;Q_P=2^N-1$，$\Delta=(\max-\min)/Q_P$，$z=-\lceil\min/\Delta\rceil$。
- 记号惯例：文中 **W$x$A$y$** = 权重 $x$ bit、激活 $y$ bit；**g128** = group size 128（Appendix 记号段）。

### 3.2 站 A：量化感知的零阶优化（§4.1）

**核心替换：** 不用反传 + STE，而对量化前向损失做 **有限差分**：

$$
\widehat{\nabla}L(W;B)=\frac{1}{q}\sum_{i=1}^{q}\frac{L\big(Q(W+\epsilon u_i);B\big)-L\big(Q(W-\epsilon u_i);B\big)}{2\epsilon}\,u_i
\quad (2)
$$

更新：$W_{t+1}=W_t-\eta\,\widehat{\nabla}L(W_t;B_t)$ (3)

| 设计选择 | 文内说法 |
|---|---|
| 前向用量化权重，后台仍维护 **FP 权重** | 沿用 QAT 惯例 |
| **不需要 STE** | 梯度由 ZO 差分直接估，绕过量化不可微 |
| 相对 STE 的叙事 | STE 是有偏代理梯度；低比特时真平滑梯度已小、STE 仍给大更新 → 不稳（形式分析放 Appendix G，本卡不展开证明） |
| 内存 | 不存激活反传、不存典型优化器状态 → 「近推理」 |

### 3.3 站 B：自适应异常值平滑 + 自适应权重量化器（§4.2）

**（1）可学习通道平滑（把激活难点迁到权重侧，但改为端到端联训）：**

$$
Y=XW+B=\big[(X-\delta)\oslash s\big]\cdot[s\odot W]+\big[B+\delta W\big]
\quad (4)
$$

- $s,\delta$：**可学习** per-channel scale / shift（灵感来自 SmoothQuant、Outlier Suppression+ 的静态操作，但此处与模型参数一起被 ZO 更新）。
- 动机：手搓或逐层标定的平滑 → 缺全局一致性；QAT 框架可联训。

**（2）自适应权重量化（可学习 Δ、z + 裁剪 α,β）：**

$$
W=\mathrm{clamp}\Big(\Big\lceil\frac{W}{\Delta}\Big\rfloor+z,\;\alpha\cdot Q_P,\;\beta\cdot Q_P\Big)
\quad (5)
$$

- $\Delta,z$：可学习步长与零点（LSQ / LSQ+ 谱系）。
- $\alpha<\beta$：可学习裁剪；平滑后某些通道权重变偏，需非对称裁剪。
- **WO（weight-only）特例**：Llama 系 WO 实验 **去掉 smoothing、只留 weight clipping**（§5.1 / Appendix C.2）——文称 WO 时平滑收益有限。

### 3.4 站 C：轻量 ZeroQAT（仅微调，§4.3 / Figure 3）

| 项 | 设定 |
|---|---|
| 动机 | ZO 下内存主要来自 **正在更新的参数**；全模型预量化会导致小扰动被 round 掉、大扰动不稳 |
| 做法 | **冻结并预量化**大部分参数；Attention 的 **Q、V** 保持全精度并更新 |
| 适用 | **仅微调**；用于量化预训练会明显掉点（Appendix D.3：Llama2-7B W2A16 Wiki PPL 29.61→**41.05**） |
| 文内收益 | OPT-13B 低比特微调内存低至 **6.8 GB**（Table 7） |

**层选择消融（Table D.4，跟读）：** 只更 Q+V 时，相对全参约 **27% / 38%** 内存（W2A16g128 / W4A4），Acc 与全参接近（54.5 vs 55.0；55.6 vs 56.8）；只更 Q 则明显掉（44.3 / 46.9）。

---

## 四、评测字段（§5）

**协议锚点（Appendix C）：**

| 设定 | 文内 |
|---|---|
| GPU | NVIDIA **A100** |
| 端侧 | **OnePlus 12**，Snapdragon **8 Gen 3**，**16GB** RAM |
| 重复 | 结果 **三跑平均** |
| 量化预训练数据 | WikiText2 + C4 混合 segment，长度 **2048**，总量与 OmniQuant 等对齐为 **128** segments |
| 平滑初始化 | 先用 OmniQuant 式重建训少量 epoch（W4A4：**2**；W2A16：**4**；约全量 OmniQuant 的 10%），再进 ZO |
| 微调数据 | Alpaca **小子集**；分类/QA 另采 1000/500/1000 train/val/test（跟 MeZO 少样本协议） |
| 微调时量化参数 | **冻结**（与预训练同初始化），直接做 quantized fine-tuning |
| 超参摘要（Table C.1） | 预训练：bsz 4，10K iter，lr ∈ {5e-7,1e-8}，ϵ ∈ {1e-3,5e-4,1e-4}；微调：bsz {32,16}，8K iter，lr ∈ {1e-6,5e-7}，ϵ=1e-3 |

### 4.1 量化预训练：PPL（Table 3，Llama 系 · Wiki / C4）

摘硬设定（跟读用；完整四模型见原文）：

| 设定 | 模型 | FP16 Wiki | OmniQuant | **ZeroQAT** |
|---|---|---:|---:|---:|
| W2A16 | Llama2-7B | 5.47 | 37.37 | **29.61** |
| W2A16 | Llama2-13B | 4.88 | 17.21 | **15.97** |
| W4A4 | Llama2-7B | 5.47 | 14.26 | **12.95** |
| W4A4 | Llama2-13B | 4.88 | 12.30 | **10.41** |
| W6A6 | Llama2-7B | 5.47 | 5.87 | **5.76**（与基线同属近无损带） |

文述：W6A6 各法与 FP 差距多 **\<1** PPL；硬设定下 ZeroQAT **一致更低 PPL**。OPT 族见 Table E.1（本卡不逐格抄）。

### 4.2 零样本 Acc（Table 4，Llama-1-7B，五任务均分）

| #Bits | Method | Avg ↑ |
|---|---|---:|
| FP16 | — | 65.26 |
| W2A16 | EfficientQAT | 47.65 |
| W2A16 | **ZeroQAT** | **51.75** |
| W4A4 | OmniQuant | 52.15 |
| W4A4 | **ZeroQAT** | **53.11** |

五任务：PIQA / ARC-e / ARC-c / HellaSwag / Winogrande（lm-eval-harness，GPTQ 设定口径）。
摘要另称「五任务平均 +5.1%、四下游 +9.1%（2-bit WO）」——**以表内格子为准核对**；单表相对 EfficientQAT 为 **+4.1** Avg（51.75−47.65），与摘要措辞不必强行等同。

### 4.3 量化微调（Table 5 OPT · Table 6 Llama 均分）

**OPT（Table 5）跟读要点：**

- 基线 PTQ：先 FP + **ZO** 微调，再套量化（对齐起点）；QAT（含 ZeroQAT）**微调过程中直接出量化模型**。
- W4A4：ZeroQAT 在 SST-2 上三尺寸约 **87.8 / 87.9 / 88.2**，而 SmoothQuant / OmniQuant 多在 **~56–61**。
- W2A16g128：ZeroQAT 相对 EfficientQAT 在生成任务（SQuAD/DROP）拉开更明显（如 OPT-13B SQuAD **59.6** vs **46.7**）。

**Llama-1 微调后五数据集均分（Table 6）：**

| Method | #Bits | 7B | 13B |
|---|---|---:|---:|
| FP | — | 67.0 | 69.3 |
| EfficientQAT | W2A16 | 49.1 | 52.1 |
| **ZeroQAT** | W2A16 | **53.9** | **55.7** |
| OmniQuant | W4A4 | 52.3 | 54.2 |
| **ZeroQAT** | W4A4 | **54.8** | **57.4** |

文称相对 EfficientQAT，2-bit 上 **+4.8 / +3.6**（7B/13B）——与表一致。

### 4.4 效率：服务器（Table 7）与手机（Table 8）

**服务器 · W2A16g128（Table 7 摘）：**

| 阶段 | 对照 | OPT-1.3B Mem | OPT-13B Mem |
|---|---|---:|---:|
| 量化预训练 bsz=1 | LLM-QAT | 28.8 GB | ~337 GB |
| | OmniQuant | 6.1 GB | 16.8 GB |
| | **ZeroQAT** | **3.1 GB** | **26.6 GB** |
| 量化微调 bsz=16 | EfficientQAT | 5.9 GB | 17.2 GB |
| | **ZeroQAT** | **0.8 GB** | **6.8 GB** |

文强调：ZeroQAT **只存权重相关**，预训练内存 **不随 batch 涨**（同表 bsz=1 与 bsz=4 同为 3.1 / 6.1 / 14.2 / 26.6 GB）。相对 LLM-QAT 称内存降 **89–92%**；微调相对 EfficientQAT，OPT-1.3B：**5.9→0.8 GB（−86%）**，wallclock **0.69→0.31 s（−55%）**。

**OnePlus 12 · W4A4（Table 8）：**

| 模型 | 阶段 | FP16 | ZeroQAT |
|---|---|---|---|
| OPT-1.3B | FT running mem | 3.5 GB | **1.2 GB** |
| OPT-2.7B | FT running mem | 8.1 GB | **2.6 GB** |
| OPT-6.7B | FT running mem | **OOM** | **6.4 GB**（latency 29.1 s） |
| 推理 | token/s 加速 | 1.0× | **1.41×–1.52×** |

→ 兑现标题「at Inference Cost / on-device」的经验字段；**不是** [[端侧小模型]] 那种端侧模型族通史。

### 4.5 消融速记（§5.3 / Appendix D）

| 消融 | 结论（文内） |
|---|---|
| 平滑初始化 epoch（Table D.5） | 0 epoch 明显差；默认 **2\***；20 仍可再降 PPL，但成本权衡取 2 |
| 可学习平滑 / 裁剪（Table D.1） | W4A4 去平滑 → PPL 爆炸（Llama-7B 12.95→**1.4e3**）；WO 去裁剪同样崩 |
| 轻量变体用于预训练（D.3） | **不建议**；预训练需更大可更新空间 |
| 训练 sample 数（D.6） | 32–512 segments，PPL 波动多在 **0.5** 内；文称更吃 **迭代次数** 而非大数据 |

---

## 五、交叉引用（不展开）

| 笔记 | 交叉方式 |
|---|---|
| **[[KV缓存量化与压缩]]** | 推理 KV 压缩 ↔ 本篇训练期 W/A QAT；问题域正交 |
| **[[Gemma4技术报告深读]]** | Gemma 4 **产品 QAT/内存列**（mobile int2+int4、act int8、docs 下载后缀）≠ ZeroQAT 的 ZO 训练算法——**仅一句索引** |
| **[[端侧小模型]]** | 端侧 SLM 产品与架构通史；本篇只贡献「边缘设备上能否跑 QAT」的方法证据 |
| 议程附注 | 近月 **QUASAR QAT（2608.13966）** 可作补链，**不升**本篇主锚 |

---

## 六、可带走的判断（跟读收束）

1. **问题诊断清楚：** 低比特部署卡在「PTQ 不够适配、FO-QAT 显存不可达」；近似 PTQ 还有 **累积误差 + 重建目标错位**。
2. **方法主轴是 ZO，不是又一个静态平滑公式：** 平滑与裁剪都被收进 **同一端到端 ZO 环**；WO 与 WA 配方有分叉（WO 常关 smoothing）。
3. **轻量 Q/V 变体是微调专用旋钮：** 换预训练会伤 PPL；层选择消融支持「Q+V 够用、只 Q 不够」。
4. **评测叙事双轨：** 语言建模（PPL）+ 下游（零样本/微调 Acc）+ **真机（OnePlus 12）**；读表时分清预训练 vs 微调、WO vs WA、g128 与否。
5. **仓库用法：** 需要「训练期量化算法」时引本卡；需要「推理 KV」看 [[KV缓存量化与压缩]]；需要「端侧小模型产品族」看 [[端侧小模型]]；Gemma 分发 QAT 只回 [[Gemma4技术报告深读]] §4.2。

**开放缺口（文内未填，勿脑补）：** PDF **未声明**官方代码仓；端侧实验停留在 OPT≤6.7B + 固定 SoC；与更新一代开源权重（Gemma 4 QAT 包等）**无直接对照实验**。

---

## 七、本地路径速查

| 用途 | 路径 |
|---|---|
| 笔记 | 推理与基础设施/KvQuant/ZeroQAT量化感知训练.md |
| PDF | `https://arxiv.org/abs/2509.00031` |
| 抽取 | |
| 主题索引 | [[MOC_推理与基础设施]] |

## 相关笔记

- [[检索式注意力|RetrievalAttention]]
- [[TEE机密推理|TEE Confidential Inference]]
- [[模型合并|Model Merging]]
- [[ZeroQAT量化感知训练|ZeroQAT]]
- [[SeamlessM4T语音翻译|SeamlessM4T]]

