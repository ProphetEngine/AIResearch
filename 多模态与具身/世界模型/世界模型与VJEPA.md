---
title: "World models 入门：V-JEPA 2 与非生成式表征预测"
topic: 世界模型与VJEPA
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 # slim: url+extract — V-JEPA2 PDF removed (>15MB)
 - https://arxiv.org/abs/2506.09985
arxiv: ["2506.09985"]
archived: 2026-09-22
---

# World models 入门（V-JEPA 2 等非生成式预测）

> **定位**：世界模型 / JEPA 表征预测横切——立 **世界模型 / JEPA 表征空间预测** 入门线，相对 LLM 自回归与像素生成式视频模型的平行轴。
> **攻坚线**：**架构思想（主）**。
> **刻意不写**：**robotics 控制 / MPC 部署 / Franka·Octo·Cosmos 对比表**（见议程 **[[视觉语言动作谱系]]** Robotics VLA）；本篇只保留「action-conditioned 潜空间预测存在、为规划提供动力学」的接口一句。
> **禁止编造**：数字、配方、对比基线一律取自官方 PDF（2026-09-22 CST）与 Meta 研究页/博文纯文本抽取；Meta 博文「1.2B」与论文 Table 12「ViT-g 1B」不一致处标 **待核实**，不擅自调和。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Assran et al., *V-JEPA 2: Self-Supervised Video Models Enable Understanding, Prediction and Planning* | arXiv:**2506.09985v1** \[cs.AI\] **11 Jun 2025**；文内 Date: **June 13, 2025**；[abs](https://arxiv.org/abs/2506.09985) · [pdf](https://arxiv.org/pdf/2506.09985)；（48 页） | 一手 TR：JEPA 预训练、理解/预测/VidQA、AC 后训练 |
| **代码** | facebookresearch/vjepa2 | https://github.com/facebookresearch/vjepa2（论文页眉） | 复现入口（本篇不跟 commit） |

**一句话抓手：** 用 **互联网规模无动作视频** 在 **表征空间** 做 mask-denoising 预测（非像素生成）→ 得到可探针的运动理解与动作预期 → 再用少量交互数据学 **动作条件** 潜动力学；规划/控制细节留给 [[视觉语言动作谱系]]。

---

## 二、何谓 world model（本议题边界）

### 2.1 Meta 博文的三能力（入口定义）

据 Meta 博文「What are world models?」与「Understanding / Predicting / Planning」条目，世界模型应支持：

| 能力 | 博文原意（压缩） | 本篇覆盖 |
|---|---|---|
| **Understanding** | 从观测识别物体、动作、运动 | §五 probe 分类 + §七 VidQA |
| **Predicting** | 预测世界如何演化；以及「若 agent 采取某动作」会怎样 | §二–四 JEPA 目标；§六 动作预期 |
| **Planning** | 在预测之上，规划达成目标的动作序列 | **仅接口提及**；控制实验 → **[[视觉语言动作谱系]]** |

认知/经典引用链见论文 §1：Craik；Rao & Ballard；Friston；Clark；Sutton & Barto；Ha & Schmidhuber；Wolpert & Ghahramani；以及 LeCun (2022) JEPA 纲领——**本篇不展开哲学史**，只作谱系锚点。

### 2.2 与相邻路线的划界（架构思想）

| 路线 | 预测落在哪 | 与 V-JEPA 2 关系 |
|---|---|---|
| **像素/视频生成式世界模型**（论文 §1、§8：Cosmos 等） | 帧/像素或生成 latent，强调视觉逼真 | JEPA **刻意忽略**不可预测细节（草叶位置等），只学可预测结构 |
| **纯交互数据 WM**（Dreamer 族等，§1/§8） | 状态–动作轨迹，常依赖奖励 | 交互数据稀缺 → V-JEPA 先用 **无动作** 网络视频规模化 |
| **VLA / 行为克隆**（§8；[[视觉语言动作谱系]]） | 直接观测→动作 | 无显式世界动力学；本篇不写 |
| **JEPA / V-JEPA 2** | **learned representation space** 上的预测 | 本篇主轴 |

论文原文对照（§1，意译要点）：相对 video generation，JEPA 聚焦可预测方面（如运动物体轨迹），而生成目标因做像素级预测会强调不可预测细节。

---

## 三、JEPA 元架构与 V-JEPA 2 预训练目标

### 3.1 Encoder + Predictor（两件套）

据 Meta 博文与论文 Figure 2（左）：

- **Encoder** $E_\theta$：原始视频 → embeddings（场景状态语义）。
- **Predictor** $P_\phi$：在给定「要预测什么」的上下文（mask tokens 等）下，输出 **预测 embeddings**（不是重建像素）。

训练为 **自监督、无需额外人工标注**（博文）；论文强调损失只施加于 **被 mask 的 patch 预测**。

### 3.2 Mask-denoising in representation space（式 1，主）

论文 §2.1：从被 mask 的视角 $x$ 预测视频 $y$ 的 **已学表征**。目标（矢量形式以 arXiv HTML/PDF 为准； 会丢掉 EMA 上划线）：

$$
\min_{\theta,\phi,\Delta_y}
\bigl\|
P_\phi\bigl(\Delta_y,\, E_\theta(x)\bigr)
\mathrm{sg}\bigl(E_{\bar\theta}(y)\bigr)
\bigr\|_1
$$

其中：

- $\Delta_y$：可学习 **mask token**，标示被丢弃 patch 的位置；
- $\mathrm{sg}(\cdot)$：stop-gradient；
- $\bar\theta$：encoder 权重的 **EMA**（防表征坍塌）；
- 损失 **仅** 在 mask 位置上算 L1。

流程（Figure 2）：patchify → 丢弃子集 → encoder 出嵌入 → 与 mask tokens 拼接 → predictor → 回归到 EMA-encoder 目标。

### 3.3 架构细节（相对原版 V-JEPA 的增量）

| 组件 | 论文事实 |
|---|---|
| 骨干 | Encoder / Predictor 均为 **ViT**（Dosovitskiy et al., 2020） |
| 位置编码 | **3D-RoPE**（时/高/宽三分特征维分别旋转）；相对 Bardes et al. (2024) 的绝对 sincos，文称有助于稳定最大模型 |
| Tubelet | $2\times 16\times 16$（$T\times H\times W$） |
| Masking | 与 V-JEPA 相同的 **multiblock** 策略（Bardes et al., 2024） |
| Predictor 规模 | 各 encoder 共用同一 predictor，**约 ViT-small / 22M**（Table 12） |

**Table 12（附录 A.3）encoder 族：**

| Model | Params | Width | Depth | Heads | MLP |
|---|---:|---:|---:|---:|---:|
| ViT-L | 300M | 1024 | 24 | 16 | 4096 |
| ViT-H | 600M | 1280 | 32 | 16 | 5120 |
| ViT-g | **1B** | 1408 | 40 | 22 | 6144 |
| Predictor ViT-s | **22M** | 384 | 12 | 12 | 1536 |

> **待核实：** Meta 博文写「**1.2 billion-parameter** model」；论文正文与 Table 12 写 encoder **ViT-g = 1B**（+ predictor 22M 仍远小于 1.2B）。本笔记以 **PDF Table 12** 为准引用参数量，博文数字不合并。

---

## 四、规模化配方：从 V-JEPA → V-JEPA 2

论文 §2 列出四条 **Key Scaling Ingredients**（相对 Bardes et al. 2024）：

| # | 杠杆 | 文内幅度 | Figure 3 累计效应（ViT-L/16 基线 → 最终） |
|---|---|---|---|
| 1 | **Data** | 2M → **22M** videos（VM22M） | +1.0 avg |
| 2 | **Model** | ViT-L 300M → **ViT-g ~1B** | +1.5 |
| 3 | **Longer training** | 90K → **252K** iterations；warmup–constant–decay | +0.8 |
| 4 | **Resolution / duration** | cooldown 阶段升到更高时空分辨率（如 $256\to384$，$16\to64$ frames） | 最终六任务平均 **88.2**（相对基线累计 **+4.0**） |

**渐进分辨率（效率）：** 主阶段用短 clip、低分辨率；仅在 **cooldown** 升分辨率/时长。Figure 5（中）：相对全程全分辨率，可至约 **$8\times$** GPU 时间节省（文内对 64×384×384 量级的对比）。Figure 5（右）：即便评测仍用 16 帧，cooldown 用更长视频仍可 +0.7 avg。

### 4.1 VideoMix22M（Table 1）

| Source | Samples | Type | Total Hours | Curation | Weight |
|---|---:|---|---:|---|---:|
| SSv2 | 168K | EgoVideo | 168 | No | 0.056 |
| Kinetics (400/600/700) | 733K | ExoVideo | 614 | No | 0.188 |
| HowTo100M | 1.1M | ExoVideo | 134K | No | 0.318 |
| YT-Temporal-1B | 19M | ExoVideo | 1.6M | **Yes**（簇检索降噪） | 0.188 |
| ImageNet | 1M | Images | n/a | No | 0.250 |

- 图像：时间维复制为 **16 帧相同帧** 以兼容视频管线。
- YT1B 策展：场景嵌入 + 面向 Kinetics/SSv2/COIN/EpicKitchen **训练集** 分布的 cluster retrieval；验证集视频不进未策展池（§2.3）。
- 策展增益（Figure 4 右，ViT-L）：Curated-YT1B vs 未策展 **+1.4** avg；大数据混合对更大模型更有益（附录 A.2/A.4）。

**数据规模叙事对齐：** 摘要/博文「**>1 million hours** of internet video + **1M images**」；Table 1 各源小时数加总与 YT1B「1.4M video-hours」叙述一致量级——**以论文表述为准**，不另推精确总和。

### 4.2 预训练期冻结评测协议（§2.1）

六任务平均：SSv2、Diving-48、Jester（运动）+ Kinetics、COIN、ImageNet（外观）。
协议：冻结 encoder，训 **4-layer attentive probe**。用于配方消融，细节结果见 §五。

---

## 五、Understanding：探针分类（非生成式表征质量）

**Table 4（节选，同一冻结协议）：**

| Method | Param. | Avg. | SSv2 | Diving-48 | Jester | K400 | COIN | IN1K |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DINOv2 | 1.1B | 81.1 | 50.7 | 82.5 | 93.4 | 83.6 | 90.7 | 86.1 |
| InternVideo2s2-1B | 1B | 87.0 | 69.7 | 86.4 | 97.0 | 89.4 | 93.8 | 85.8 |
| V-JEPA (ViT-H, 2024) | 600M | 85.2 | 74.3 | 87.9 | 97.7 | 84.5 | 87.1 | 80.0 |
| **V-JEPA 2 ViT-g** | 1B | **87.5** | 75.3 | 90.1 | 97.7 | 86.6 | 90.7 | 84.6 |
| **V-JEPA 2 ViT-g384** | 1B | **88.2** | **77.3** | 90.2 | 97.8 | 87.3 | 91.1 | 85.1 |

架构读法：在 **运动理解**（SSv2 等）上相对对比式图像编码器与部分视频–文本预训练编码器优势明显；外观任务 **竞争性** 而非全面碾压。摘要强调的 **77.3 SSv2 top-1** 即 ViT-g384 行。

---

## 六、Prediction：人类动作预期（表征空间「向前看」）

任务：**Epic-Kitchens-100**，默认 **1 秒** anticipation；指标 mean-class **recall-at-5**（verb / noun / action）。

机制（§6）：上下文 clip → encoder；predictor 带 **未来 1s 帧的 mask tokens** 预测未来表征；encoder+predictor 输出拼接后接 attentive probe（三个 query → verb/noun/action）；focal loss。

**Table 5（action recall-at-5 主列）：**

| Method | Param. | Verb | Noun | **Action** |
|---|---:|---:|---:|---:|
| PlausiVL（前 SOTA，专用/LLM） | 8B | 55.6 | 54.2 | 27.6 |
| V-JEPA 2 ViT-L | 300M | 57.8 | 53.8 | 32.7 |
| V-JEPA 2 ViT-H | 600M | 59.2 | 54.6 | 36.5 |
| V-JEPA 2 ViT-g | 1B | 61.2 | 55.7 | 38.0 |
| **V-JEPA 2 ViT-g384** | 1B | 63.6 | 57.1 | **39.7** |

文称 ViT-g384 相对 PlausiVL action 列 **+12.1**（约 **44%** 相对提升）。规模上 action recall 近似随模型线性上升。局限（§6 Limitations）：更长时域预期变差；厨房封闭词表；类别集外不可泛化——**诚实边界，勿夸成通用物理仿真器**。

---

## 七、Understanding × Language：无语言监督视频编码器对齐 LLM

要点（§7）：LLaVA 式 early fusion；文称据其所知，这是 **首个** 用 **无语言监督预训练的视频编码器** 训 VidQA MLLM 的系统结果之一。

**受控设置（Table 6，冻结视觉，Qwen2-7B-Instruct，同数据）：** V-JEPA 2 ViT-g512 平均 **52.3**，高于 DINOv2 / SigLIP2 / PE（同表）；在 MVP、TemporalBench、TVBench 等时间向基准上拉开更明显。

**放大对齐数据（Table 8，88.5M，Llama 3.1 8B 类）：** 文报 8B 档多项 SOTA，例如：

| Benchmark | V-JEPA 2 ViT-g384 + LLaMA 3.1 8B |
|---|---|
| PerceptionTest (test, SFT) | **84.0** |
| MVP paired-acc | **44.5** |
| TempCompass multi-choice | **76.9** |
| TemporalBench (MBA-short QA) | **36.7** |
| TOMATO | **40.3** |

（TVBench / MVBench 未全面超过 PerceptionLM 8B——以 Table 8 原文为准。）

架构含义：JEPA 表征 **可** 与语言对齐并驱动时空推理；「必须对比预训练才能做 VQA」并非本设定下的必然。

---

## 八、Action-conditioned 接口（到此止步；控制见 [[视觉语言动作谱系]]）

论文第二阶段（§3）：**冻结** V-JEPA 2 encoder，新训 ~**300M** block-causal transformer **predictor**，在 Droid 上以 **&lt;62 hours** 未标注机器人视频（文：仅用原始视频 + 末端执行器状态，**不用**任务成功标签/奖励）做 **下一帧表征** 的 teacher-forcing + 短 rollout L1（式 2–4）。

- 输入交织：动作 $a_k$、状态 $s_k$、帧表征 $z_k=E(x_k)$。
- 动作：相邻帧末端状态差分（7 维）。
- 产物名：**V-JEPA 2-AC**——潜空间中的动作条件世界模型。

**本篇不做：** 能量最小化式 (5)、CEM 规划、Franka 双实验室成功率表、与 Octo / Cosmos 的分钟级规划时延对比——以上属 **操作控制 / 具身部署**，移交 **[[视觉语言动作谱系]]**。此处只固定结论句：表征空间动力学使「给定图像子目标做闭环规划」成为可能，且论文强调数据量远小于典型专家轨迹规模。

---

## 九、Meta 附带的物理推理基准（博文；非 V-JEPA 2 自证分数）

博文发布三项评测（强调 **人类近完美 vs 现有视频模型接近随机或明显落后**）：

| 基准 | 测什么 |
|---|---|
| **IntPhys 2** | 成对视频中识别「违反直觉物理」的那条（violation-of-expectation） |
| **MVPBench（Minimal Video Pairs）** | 最小变更视频对 + 同题反义答案，抑制外观/文本捷径 |
| **CausalVQA** | 因果 / 反事实 / 预期 / 规划类视频问答 |

博文称 top models（含 V-JEPA 2）在部分设定上仍有显著人类差距——**作评测地图，不在此编造具体表分**（分数以各基准论文/排行榜为准）。

---

## 十、架构思想总结（可背）

1. **世界模型 ≠ 必须生成像素**：JEPA 在 **embedding 空间** 预测，用 mask-denoising + EMA teacher 防坍塌，逼模型编码 **可预测结构**。
2. **规模化路径可检验**：数据混合与策展、模型到 ~1B、长训程、渐进分辨率——Figure 3 给出可加总的 avg 增益叙事。
3. **无动作预训练已够「懂」与「预期」**：SSv2 77.3、EK100 action 39.7、对齐 LLM 后多项 VidQA SOTA——支撑「观察中学世界」假设的工程证据。
4. **动作条件是薄适配层**：冻结视觉骨干 + 少量交互数据 → 潜动力学；**如何闭环控臂** 不在本篇。
5. **与生成式 WM / VLA 正交**：生成式重逼真与想象视频；VLA 重模仿；JEPA 重 **紧凑可规划表征**——三者可组合（论文 §8/§9 亦如是说），但概念上先分开。

---

## 十一、与仓库已有笔记的边界

| 已有 / 姊妹篇 | 本篇关系 |
|---|---|
| [[多模态架构脉络]] 多模态 | 视觉指令/融合通史；本篇不重写 LLaVA 管线，只写 V-JEPA 作视觉塔的特例 |
| `B10` 扩散视觉 | 生成式图像/视频；本篇对照「非生成式预测」 |
| **[[视觉语言动作谱系]]** Robotics VLA | **承接** AC 规划、RT-2 / OpenVLA / π0 与操作控制；**禁止**在本篇展开 |
| [[视频生成正式报告]] 视频生成报告线 | 像素生成产品/报告；与本篇正交 |

---

## 十二、待核实 / 非本 PDF 范围

- Meta 博文 **1.2B** vs 论文 Table 12 **ViT-g 1B + ViT-s 22M**：以 PDF 为准；1.2B 来源未在本 PDF 解释。
- 论文 HTML 摘要偶见后续日期戳（抓取页曾见 Aug 2026）；**官方 PDF 为 2506.09985v1，Date June 13, 2025**——版本演进若再发 v2+ 需重抽。
- IntPhys 2 / MVPBench / CausalVQA 的完整分表、与人类基线逐格对比：**未写入本 PDF 主实验表**，需各基准独立 PDF。
- I-JEPA / 点云 JEPA / 原版 V-JEPA (2404.08471) 配方细节：仅作谱系引用，**未**深读其 PDF。
- Hugging Face 权重文件名、许可证条文：本篇不抄 CDN/哈希。

---

## 十三、来源清单

1. Assran et al., 2025. *V-JEPA 2* — arXiv:**2506.09985**（https://arxiv.org/abs/2506.09985）；抽取 ；Code: https://github.com/facebookresearch/vjepa2 。
4. 谱系锚点（未深读 PDF）：LeCun, 2022 (JEPA 纲领)；Bardes et al., 2024 *V-JEPA* (arXiv:2404.08471)；Assran et al., 2023 *I-JEPA*。
5. 划界：`notes/` 未来 **[[视觉语言动作谱系]]**（VLA / 控制）；交叉 [[多模态架构脉络]]、`B10` 勿重写。

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

