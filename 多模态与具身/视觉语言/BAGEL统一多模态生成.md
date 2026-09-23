---
title: "统一多模态生成：BAGEL（≠ 视频生成报告 / ≠ LDM·DiT）"
topic: BAGEL统一多模态生成
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
aux:
 - https://arxiv.org/abs/2505.14683
 - https://arxiv.org/pdf/2505.14683
 - https://bagel-ai.org/
 - https://github.com/ByteDance-Seed/Bagel
 - https://huggingface.co/ByteDance-Seed/BAGEL-7B-MoT
 - https://demo.bagel-ai.org/
arxiv: ["2505.14683"]
related:
 - "扩散生成式视觉与LLM"
 - "视频生成正式报告"
 - "多模态架构脉络"
 - "SiLVR与ChainOfFrames"
 - "QwenOmni音视频原生"
 - "DiffusionForcing族"
code_urls:
 - "https://github.com/ByteDance-Seed/Bagel"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 统一多模态生成：BAGEL（≠ 视频生成报告 / ≠ LDM·DiT）

> **定位**：统一多模态生成报告——ByteDance Seed *Emerging Properties in Unified Multimodal Pretraining*（arXiv:**2505.14683**v3 \[cs.CV\]，页眉 **27 Jul 2025**；正文 Date **July 29, 2025**）。立「**开源理解+生成统一 decoder-only（MoT）**」：在 **交错文本/图像/视频/网页** 万亿级 token 上预训练，报告 **涌现式** 复杂多模态推理（自由形式图像操纵、未来帧、3D、世界导航等）。
> **攻坚线**：**架构思想（主）**——MoT / 双编码器（SigLIP2 + FLUX VAE）/ 广义因果注意力 / NTP⊕Rectified Flow；**评测字段（辅）**——Table 4–10 与 IntelligentBench 文内数字转述。
> **硬划界（开篇钉死）**：
> - **≠ B10**：禁止写成 **LDM / DiT 图像潜扩散层图通史**。本卡只写 BAGEL 的 **统一 MoT + RF 视觉头**；LDM/DiT 仅作谱系对照一句，不重写感知压缩 / U-Net→ViT 规模化。
> - **≠ [[视频生成正式报告]]**：禁止写成 **文生视频旗舰正式报告缺口备忘**（Sora 等无可核长 TR）。本卡对象是 **统一理解+生成基础模型**；文内「视频交错数据 / 多帧生成」只作为 **训练源与世界建模定性展示**，不升「视频生成正式报告」主轴。
> - **≠ [[多模态架构脉络]]**：禁止重写 CLIP→Flamingo→LLaVA→「原生多模态」**理解/对话通史**；经典祖先仅 related-work 接口。
> - **≠ [[SiLVR与ChainOfFrames]]**：禁止写成 **SiLVR / Chain-of-Frames 视频理解推理框架**；本卡是 **生成侧统一模型 + 编辑/世界建模**，不是纯语言管道 VideoQA。
> - **≠ [[QwenOmni音视频原生]]**：禁止写成 **Qwen Omni Thinker–Talker 音视频产品卡**；BAGEL 主轴是 **视觉理解+图像生成/编辑**，非流式语音合成 Omni。
> - **谱系一句、不升主**：**Chameleon**（早期融合）过旧 → 仅 Table 4/5 对照与设计空间一句。**Foley-Omni**（音轨统一生成）→ **后置**（议程明示）。
> **禁止编造**：主张与表数字一律锚定本地抽取（2026-09-22 CST）与 GitHub README 明示句。文内未给出的精确 GPU 小时 / 完整层宽公式 / 未表格化图点 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 项 | 报告原文 / 元数据 | 出处 |
|---|---|---|
| 标题 | *Emerging Properties in Unified Multimodal Pretraining* | 封面； Title |
| 产品名 | **BAGEL**（正文亦称 *Scalable Generative Cognitive Model*） | §1；摘要 |
| 作者 | Chaorui Deng\*, Deyao Zhu\*, Kunchang Li\*, Chenhui Gou\*, Feng Li\*；Zeyu Wang；Shu Zhong；Weihao Yu；Xiaonan Nie；Ziang Song；Guang Shi§；Haoqi Fan\*†（\*共一；§通讯；†项目负责人） | 封面 |
| 机构 | ByteDance Seed 等 | 封面 |
| arXiv | **arXiv:2505.14683v3** \[cs.CV\] **27 Jul 2025** | PDF 页眉；XMP `…/2505.14683v3` |
| 正文 Date | July 29, 2025 | 摘要区 Date |
| XMP MetadataDate | 2025-07-29T01:03:11+00:00（→ **2025-07-29 09:03 CST**） | ` -meta` |
| 权利 | `http://creativecommons.org/licenses/by/4.0/` | XMP |
| 产品字段（摘要） | 统一 decoder-only；交错 text/image/video/web；**trillions of tokens**；涌现复杂多模态推理 | Abstract |
| 规模（正文） | **7B active / 14B total** MoT | §1；README |
| 项目页 / Demo | https://bagel-ai.org/ · https://demo.bagel-ai.org/ | 摘要；README |
| 权重 | https://huggingface.co/ByteDance-Seed/BAGEL-7B-MoT | README |
| 代码 | https://github.com/ByteDance-Seed/Bagel（Apache-2.0；2026-09-22 API：★6180 / forks 546） | README / GitHub API |
| PDF 页数 / 纸型 | **37** 页 letter | |
| Producer | pikepdf 8.15.1；arXiv GenPDF | XMP |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| **主 PDF（arXiv）** | https://arxiv.org/pdf/2505.14683 | **29.76MiB**（31,205,015 B） | **37** | 官方 HTTPS 外链（≈29.8MB） |
| **抽取** | | ≈256K（262,247 B / 3039 行） | — | 全文检索 |
| **辅：仓库 README** | | ≈12K | — | 权重/推理超参/发布日志；**不替代** TR 数字源 |

**一句话抓手：**
用 **无瓶颈的 Integrated Transformer（MoT）** 把理解专家与生成专家放在同一共享自注意力序列上，在 **≈5T+ 级**（PT 2.5T + CT 2.6T，另加 Alignment/SFT）交错多模态数据上缩放，使能力按「理解/高保真生成 → 经典编辑 → 智能编辑/世界建模」顺序涌现；开源 **7B 激活 / 14B 总参** 权重与代码。

---

## 二、议题边界：统一理解+生成 ≠ 图像扩散通史 / ≠ 视频报告缺口 / ≠ VLM 通史 / ≠ 视频推理 / ≠ Omni 产品

### 2.1 五向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **LDM / DiT 图像扩散** | 潜空间去噪、U-Net→DiT 规模化 | **B10** | **否**（禁层图通史） |
| **视频生成正式报告缺口** | Sora 等无可核长 TR 备忘 | **[[视频生成正式报告]]** | **否** |
| **多模态理解/对话通史** | CLIP→Flamingo→LLaVA→原生主张 | **[[多模态架构脉络]]** | **否** |
| **视频—语言推理框架** | SiLVR 语言管道 / CoF 帧锚定 | **[[SiLVR与ChainOfFrames]]** | **否** |
| **Qwen Omni 产品卡** | Thinker–Talker、流式语音 | **[[QwenOmni音视频原生]]** | **否** |
| **BAGEL 统一 MoT** | 交错预训练 + 理解/生成/编辑/世界建模 | **本篇** | **是** |

### 2.2 与设计空间三族的关系（文内 §2.1，非外推）

文内把统一多模态设计空间拆成三类，并明确选择第三类：

| 族 | 文内定义 | BAGEL 立场 |
|---|---|---|
| **Quantized AR** | 离散视觉 token + NTP | 实现简单，但视觉生成质量经验上弱于扩散系；延迟受序列化约束 |
| **External Diffuser** | LLM/VLM 经轻适配器接外部扩散；LLM 压成少量 latent 作语义条件 | 收敛快、数据省；但 **显式瓶颈**，长上下文多模态推理信息损失风险大 |
| **Integrated Transformer** | 同一 Transformer 内切换 AR 理解与扩散式生成；全层无瓶颈上下文 | **本文选择**；算力更高，但利于大规模交错缩放与长上下文推理 / 后续 RL |

> **跟读提醒**：本卡写的是 **Integrated + MoT 硬路由** 这一具体配方，不是 B10 的「如何训一个独立 LDM/DiT」，也不是 [[视频生成正式报告]] 的「有无 Sora 级正式 TR」。

---

## 三、架构思想（主）

### 3.1 MoT：理解专家 ⊕ 生成专家，共享自注意力

- **骨干初始化**：Qwen2.5 LLM（decoder-only）；RMSNorm、SwiGLU、RoPE、GQA；并按图像/视频生成通行做法加 **QK-Norm** 以稳定训练。
- **MoT**：复制 Qwen2.5 **全部可训练参数** 得到满尺寸生成专家（对比：MoE 变体只复制 FFN）。
- **硬路由**：生成专家专吃 **VAE token**；理解专家吃 **text + ViT token**（对齐 Qwen-VL 系列策略）。
- **算力声明**：MoE/MoT 总参约 **×2**，但训练/推理 **FLOPs 与 dense 相同**（选择性激活）。
- **1.5B 消融（Fig.3）**：同超参同数据下，MoT 在生成 MSE 上收敛最快、终损最低；理解 CE 波动更大，但 MoT 总体仍优——文内解读为理解/生成目标可能把参数推向不同区域，**分容量**可缓解竞争。

### 3.2 双视觉表示：语义理解 vs 像素级生成

| 路径 | 编码器 / 压缩 | 用途 |
|---|---|---|
| **理解** | **SigLIP2-so400m/14**（固定 384 初始化）→ 插值位置编码、最大输入 **980×980** → **NaViT** 原生宽高比 → 两层 MLP 对齐 LLM 隐维 | ViT token |
| **生成** | **FLUX** 预训练 **VAE**（下采样 **8**、latent 通道 **16**）→ **2×2** patch embed 对齐隐维；**VAE 训练中冻结** | VAE token |
| **位置 / 时间步** | ViT 与 VAE 均用 **2D 位置编码**；扩散时间步按 Causal Diffusion Transformer 做法加到 VAE 初始隐态（**不用**常规 DiT 的 AdaLN） | 架构更干净且宣称不损性能 |

**目标形态：**
- 文本：**Next-Token-Prediction**（CE）。
- 视觉生成：**Rectified Flow**（MSE）。
- 联合损失权重（Table 3）：**CE : MSE = 0.25 : 1**（PT/CT/SFT）。

### 3.3 广义因果注意力（Generalized Causal Attention）

交错样本中，每张图准备三套视觉 token：

1. **Noised VAE** —— 仅用于 RF 训练，算 MSE。
2. **Clean VAE** —— 无噪声 latent，作为后续图/文条件。
3. **ViT** —— SigLIP2；统一交错理解/生成输入格式，经验上提升交错生成质量。

规则要点（§2.3 / Fig.15）：

- 同一样本 token 先按模态切成连续 split；后 split 可 attend 前 split。
- split 内：文本 **因果**；视觉 **双向**。
- 后续生成 **不可** attend 前图的 noised VAE，只可用 clean VAE + ViT。
- 多图/视频片段：采用 **Diffusion Forcing**（独立噪声水平；条件于前图噪声表示）；并可随机把连续图分组、组内全注意力且同噪声水平（增强一致性）。
- 实现：PyTorch **FlexAttention**，相对朴素 SDPA 约 **~2×** 加速；推理可缓存已生成多模态上下文的 KV（只存 clean VAE + ViT；图生成完后用 clean 替换 noised）。
- CFG：随机丢弃 text / ViT / clean VAE，概率 **0.1 / 0.5 / 0.1**。

> **划界**：此处引用 Diffusion Forcing 是 **训练注意力策略**，不是重开 **[[DiffusionForcing族]]** 全文；本卡不展开 DF 论文推导。

### 3.4 为何不是 External Diffuser / 纯 AR

文内核心哲学：**最大化容量、避免启发式瓶颈与任务专用约束**。共享自注意力使理解与生成在长上下文上交互；作者认为这对「交错数据涌现出的组合能力」以及后续长上下文推理 / RL 更友好——即使相对 External Diffuser 更吃算力。

---

## 四、数据与训练配方（文内可核）

### 4.1 数据规模（Table 1）

| Data Source | # Data (M) | # Tokens (T) |
|---|---|---|
| Text Data | 400 | 0.4 |
| Image-Text-Pair Understanding | 500 | 0.5 |
| Image-Text-Pair Generation | 1600 | 2.6 |
| **Interleaved Understanding** | 100 | 0.5 |
| **Interleaved Generation: Video** | 45 | 0.7 |
| **Interleaved Generation: Web** | 20 | 0.4 |

注：文内强调随机采样，**数据集规模 ≠ 已见 token 总量**。

**交错源要点：**
- **视频**：公开在线视频 + Koala-36M、MVImgNet2.0；帧间变化 caption（蒸馏 Qwen2.5-VL-7B，caption ≤30 token；每 clip 平均约 4 帧）→ **45M** 时序交错序列。
- **网页**：基于 OmniCorpus（Common Crawl）；两阶段 topic（LLM 标小样 → fastText → 再 LLM 细滤）+ Table 2 规则滤；caption-first（图前插 Qwen2.5-VL-7B 短描述）；过长段（>300 token）LLM 摘要 → **20M** 文档。
- **推理增强**：约 **500k** 例（T2I / 自由形式操纵 / 概念编辑），借鉴 O1 / DeepSeek-R1 式长 CoT 思路，在生成前插入语言推理步。

### 4.2 四阶段训练（Table 3）

| | Alignment | PT | CT | SFT |
|---|---|---|---|---|
| LR | $1\times10^{-3}$ Cosine | $1.0\times10^{-4}$ Constant | 同左 | $2.5\times10^{-5}$ Constant |
| Warm-up / Steps | 250 / **5K** | 2500 / **200K** | 2500 / **100k** | 500 / **15K** |
| Seen tokens | **4.9B** | **2.5T** | **2.6T** | **72.7B** |
| Max context | 16K | 16k | **40k** | **40k** |
| Gen 分辨率（短边 min, 长边 max） | — | (256, 512) | **(512, 1024)** | (512, 1024) |
| Und 分辨率 | (378, 378) | (224, 980) | (378, 980) | (378, 980) |
| Diffusion timestep shift | — | 1.0 | **4.0** | 4.0 |
| EMA | — | 0.9999 | 0.9999 | 0.995 |
| 交错采样比趋势 | 仅 I2T | 理解交错 0.1；视频 0.1；网页 0.05 | 交错三类各升至 **0.15** | 交错三类各 **0.2**；T2I 降至 0.3 |

**阶段意图（§4）：**
1. **Alignment**：只训 MLP connector；ViT 与 LLM 冻结；固定 $378\times378$ caption。
2. **PT**：加 QK-Norm；除 VAE 外全可训；原生分辨率约束。
3. **CT**：升分辨率 + 提高交错采样；巩固核心能力后强调跨模态推理。
4. **SFT**：生成侧高质量子集；理解侧滤自 LLaVA-OV、Mammoth-VL；约 **72.7B** token。

**优化器：** AdamW $\beta_1=0.9,\beta_2=0.95,\epsilon=1.0\times10^{-15}$（抑尖峰）；恒定 LR 以便不重启地扩数据。

**采样比消融（1.5B，Fig.5）：** 生成:理解从 1:1 提到 **4:1** 时 MSE 绝对降约 **0.4%**（RF 实践中已可观）；CE 无一致模式 → 协议上 **生成样本显著多于理解样本**。
**LR 消融（Fig.6）：** 更大 LR 利 MSE、更小 LR 利 CE → 用 **损失权重** 调和（见上 CE:MSE）。

---

## 五、涌现性质（§6，定义约束）

文内操作定义：

> An ability is **emerging** if it is **not present in earlier training stages** but **is present in later pre-trainings**.

以达峰值 **85%** 所需已见 token 为指示（Fig.7，thinking 关闭）：

| 能力代理 | ≈85% 峰值所需 token |
|---|---|
| 常规理解（多榜均值） | **~0.18T** |
| 生成（GenEval） | **~0.68T** |
| 经典编辑（GEdit） | **~2.64T** |
| **Intelligent Edit** | **~3.61T**（约 3T 后显著跃升；高分辨率 CT 后 IntelligentBench 约 **15→45** 量级叙述） |

消融：去掉 **ViT token** 对 GEdit 影响小，但对 Intelligent Edit 约 **-16%**——语义视觉上下文对复杂编辑关键。定性（Fig.8–9）：高保真 T2I 约在 **1.5T** 前已强；文字渲染「hello」「BAGEL」约 **1.5T–4.5T** 才稳；智能编辑在 **≈3.5T** 前常「几乎原图不动」，之后才出现清晰语义重写。

---

## 六、评测字段（辅，文内表）

### 6.1 理解（Table 4，BAGEL **7B MoT**）

| 指标 | BAGEL 7B MoT | 同表对照摘录 |
|---|---|---|
| MME-P | **1687** | Janus-Pro 7B 1567；Qwen2.5-VL 7B 未列 MME-P |
| MME-S | **2388** | Qwen2.5-VL 7B 2347；InternVL2.5 7B 2344 |
| MMBench | **85.0** | Qwen2.5-VL 83.5；InternVL2.5 84.6；Janus-Pro 79.2 |
| MMMU | **55.3** | Janus-Pro 41.0（文称 +14.3）；Qwen2.5-VL 58.6 |
| MM-Vet | **67.2** | Janus-Pro 50.0（文称 +17.1）；Qwen2.5-VL 67.1 |
| MathVista | **73.1** | Qwen2.5-VL 68.2；InternVL2.5 64.4 |
| MMVP | **69.3** | InternVL2 7B 51.3 |

另报 **1.5B MoT** 行（Table 4）：MME-S 2183、MMBench 79.2、MMMU 43.2 等——定性 Fig.16 称小激活仍可在 T2I/编辑观感上压过更大对照，但与 7B 仍有缩放差距。

### 6.2 文生图 GenEval（Table 5）

| 模型 | Overall |
|---|---|
| BAGEL | **0.82** |
| BAGEL†（LLM rewriter） | **0.88** |
| Janus-Pro-7B | 0.80 |
| FLUX.1-dev† | 0.82 |
| SD3-Medium | 0.74 |

### 6.3 WISE 世界知识 T2I（Table 6）

| 模型 | Overall |
|---|---|
| BAGEL | **0.52** |
| BAGEL w/ Self-CoT | **0.70** |
| MetaQuery-XL | 0.55 |
| FLUX.1-dev | 0.50 |
| GPT-4o\*\*（他测） | 0.80 |

### 6.4 编辑：GEdit-Bench（Table 7）与 IntelligentBench（Table 8）

**GEdit-Bench-EN（GPT-4.1 评）：** BAGEL G_SC **7.36** / G_PQ **6.83** / G_O **6.52**；对照 Step1X-Edit 7.09 / 6.76 / 6.70；Gemini 2.0 6.73 / 6.61 / 6.32；GPT-4o 7.85 / 7.62 / 7.53。CN 集 BAGEL G_O **6.50**。

**IntelligentBench（350 例，GPT-4o 评，归一 100 分）：**

| 模型 | Score |
|---|---|
| GPT-4o\*\*（答 318/350） | 78.9 |
| Gemini 2.0\*\*（答 349/350） | 57.6 |
| BAGEL w/ Self-CoT | **55.3** |
| BAGEL | **44.9** |
| Step1X-Edit | 14.9 |

### 6.5 推理增强编辑续表

| 基准 | BAGEL | + Self-CoT |
|---|---|---|
| RISEBench Overall（Table 9，GPT-4.1） | 6.1 | **11.9** |
| KRIS-Bench Overall（Table 10，GPT-4o 均分） | 56.21 | **60.18** |

README（2025-06-15）称已修正 KRIS/RISE 评测结果，并称在这些推理基准上表现 **comparable to Gemini 2.0**——以 PDF Table 9/10 与 README 并存核验，**主数字仍以 PDF 表为准**。

### 6.6 世界建模（§7.5，定性）

提高视频与导航数据比例微调；导航轨迹用 ParticleSfM 标注。Fig.14：导航、旋转、多图生成；宣称从真实街景训练可泛化到水墨、卡通、游戏等域。**非** [[视频生成正式报告]] 视频旗舰正式报告，亦 **非** [[MatrixGame与Cosmos]] 交互世界模型平台卡。

### 6.7 失败模式（§7.6 / Fig.17，文内承认）

特殊 IP、复杂文字渲染、复杂人体姿态、多实例同生；编辑侧物体换位、大量实例同时改——当代 T2I/编辑通病。复杂指令遵循上 BAGEL 与 Gemini 2.0 可同现困难；GPT-4o 更稳。改进方向文内点到：加含字图像数据、扩模型、或后训 **RLHF**（未给本卡可核 RL 配方）。

---

## 七、代码辅（GitHub，不跟 commit）

| 项 | 内容（README，2026-09-22 抓取） |
|---|---|
| 仓库 | https://github.com/ByteDance-Seed/Bagel |
| 许可 | **Apache 2.0** |
| 权重 | `ByteDance-Seed/BAGEL-7B-MoT`（HF） |
| 文档 | `TRAIN.md`、`EVAL.md`（含 KRIS / RISE / ImgEdit） |
| 推理超参（README Notice） | `cfg_text_scale` 典型 4–8；`cfg_image_scale` 1–2；`num_timesteps` 典型 50；`cfg_renorm_type`∈{global, channel, text_channel}；编辑发糊可试 global / 降 renorm_min / 降 cfg |
| 社区衍生（README News） | ComfyUI、DF11/INT8 压缩、Docker、HF Space 等——**索引，不核性能** |

---

## 八、跟读清单与禁区

**应记住：**
1. **MoT + 双编码器 + 无瓶颈共享注意力** 是相对 External Diffuser / 纯离散 AR 的主架构选择。
2. **交错视频/网页数据 + 推理增强** 是「涌现」叙事的数据前提，不是只堆 T2I 对。
3. 能力顺序：**理解/生成 → 经典编辑 → 智能编辑**；IntelligentBench / Self-CoT 是文内用来暴露组合推理的探针。
4. 开源落点：**7B/14B MoT 权重 + Apache 代码**；项目页 bagel-ai.org。

**禁止：**
- 把本卡写成 B10 LDM/DiT 教程或 [[视频生成正式报告]] 视频 TR 缺口复述。
- 把视频交错/多帧定性展示写成「BAGEL = 开源 Sora」。
- 把 [[QwenOmni音视频原生]] Omni 语音栈或 [[SiLVR与ChainOfFrames]] VideoQA 框架配方塞进正文。
- 外推未给的总 GPU 时、层配置细节、或把 Fig 柱未对齐读数当表。
- **建议把 29.76MiB PDF 入库二进制**（违反本波 >20MB 规矩）。

---

## 九、来源与核验

| 来源 | 用途 |
|---|---|
| arXiv PDF 2505.14683v3（临时下载 + ） | 架构、Table 1–10、涌现定义与主结果 |
| | 入库检索文本 |
| GitHub README → | 权重入口、许可、推理超参、发布日志 |
| [[MOC_多模态与具身]] | 划界对齐 |

**体积与入库结论（回报用）：**
- PDF：https://arxiv.org/pdf/2505.13427（**29.76MiB / 37p**）。

- （≈256K）+ [外部仓库 README](https://github.com/ByteDance-Seed/Bagel)。
- 笔记：多模态与具身/视觉语言/BAGEL统一多模态生成.md。
