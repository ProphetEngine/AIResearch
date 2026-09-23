---
title: "Remote sensing EO FM：SkySense 谱系（含 SkySense++ / V2 对照）"
topic: SkySense遥感基础模型
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - `https://arxiv.org/pdf/2312.10115`；
 - https://arxiv.org/abs/2507.13812
arxiv: ["2312.10115", "2507.13812"]
doi: ["10.1038/s42256-025-01078-8"]
related: ["天气气候基础模型", "MatterSim材料基础模型", "多模态架构脉络"]
github:
 - "https://github.com/kang-wu/SkySensePlusPlus"
 - "https://github.com/LotusWhu/SkySensePlusPlus"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# Remote sensing EO FM：SkySense 谱系（含 SkySense++ / V2 对照）

> **定位**：遥感多模态增量——相对 **[[天气气候基础模型]] Aurora**（地球系统**格点预报**）补一块仍空的 **遥感多模态 EO 影像基础模型**。主锚 Guo et al. *SkySense*（arXiv **2312.10115v2**；Nature ++ 引为 **CVPR 2024**）；对照两支后继——Nature MI **SkySense++**（DOI **10.1038/s42256-025-01078-8**）与 arXiv **SkySense V2**（**2507.13812v1**）。
> **攻坚线**：**架构思想（主）**——因子化多模态时空编码器 →（++）渐进语义增强 /（V2）统一 Transformer；**评测字段（辅）**——16×7（SkySense/V2）vs 12×7 域（++）。
> **硬划界**：
> - **≠ [[天气气候基础模型]] Aurora**：格点大气/海浪/气旋预报 ≠ 本篇卫星·航空 **影像解译**。
> - **≠ [[MatterSim材料基础模型]] MatterSim**：原子势 / 材料物性，无接口。
> - **≠ [[多模态架构脉络]] 通用视觉多模态通史**：不重写 CLIP/Flamingo；只取 RS 多传感器切片。
> **禁止编造**：参数、序列数、GPU 小时、平均增益锚定官方 PDF（2026-09-22 CST）与 Nature **HTML**；Nature **PDF** 本环境未取到，Methods 标 **待核实**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文（原点）** | Guo, Lao, Dang, Zhang, Yu, Ru, Zhong, Huang, Wu, Hu, He, Wang, Chen, Yang, Zhang, Li, *SkySense: A Multi-Modal Remote Sensing Foundation Model Towards Universal Interpretation for Earth Observation Imagery* | arXiv:**2312.10115v2** \[cs.CV\] **22 Mar 2024**；`https://arxiv.org/pdf/2312.10115`；（**29** 页；27,544,899 bytes；CreationDate **2024-03-25 CST**）；单位 **Ant Group / Wuhan University / MYBank**；Nature ++ 引用为 **CVPR 2024** | 因子化 MM-RSFM；**2.06B** 参；**21.5M** 时序样本 |
| **后继 A（语义增强）** | Wu, Zhang, Ru, et al., *A semantic-enhanced multi-modal remote sensing foundation model for Earth observation*（**SkySense++**） | DOI **10.1038/s42256-025-01078-8**；*Nat Mach Intell* **7**, **1235–1249**（2025）；Published **04 Aug 2025**；HTML → ；PDF：**idp.nature.com 登录墙，未落盘**（见 ） | 因子化骨架 + **二阶段**预训练；**27M** 图；**12** 任务 × **7** 域；few-shot |
| **后继 B（统一骨干）** | Zhang, Ru, Wu, Yu, Liang, Li, Chen, *SkySense V2: A Unified Foundation Model for Multi-modal Remote Sensing* | arXiv:**2507.13812v1** \[cs.CV\] **18 Jul 2025**；`https://arxiv.org/abs/2507.13812`（**20** 页；6,579,366 bytes）；**Ant Group / Wuhan University** | 统一骨干 **665M**；APM + modality prompt + MoE；平均超 SkySense **1.8** |
| **代码（++）** | kang-wu/SkySensePlusPlus（Nature Code availability）；议程亦列 LotusWhu/SkySensePlusPlus | 两仓 README **同文** → [kang-wu/SkySensePlusPlus README](https://github.com/kang-wu/SkySensePlusPlus) · [LotusWhu/SkySensePlusPlus README](https://github.com/LotusWhu/SkySensePlusPlus) | 自 SkySense ckpt 续训；RS-Semantic / EO Benchmark 表；Zenodo 数据入口 |

**一句话抓手：** 地理对齐的 **高分光学 + Sentinel-2 时序多光谱 + Sentinel-1 时序 SAR** → 可拆装的 **十亿级因子化** SkySense；后继分两支——**++** 加语义掩码第二阶段换 few-shot，**V2** 把三骨干收成 **统一 665M** 并改对比学习以适配「一幅 RS 图多主题」。

**跟读口诀：**

`
输入：HSROI（静帧高分光学）∥ TMsI（S2 时序）∥ TSARI（S1 时序）
 ↓
SkySense（因子化）：Swin-Huge ∥ ViT-Large ∥ ViT-Large
 + Multi-Granularity Contrastive Learning（像素/对象/图像 × 单模态/融合）
 + Geo-Context Prototype Learning（区域原型）
 + Multi-modal Temporal Fusion Transformer
 ↓ 分叉（并行后继，非严格「++→V2」）
SkySense++：representation-enhanced（MGCL 族）→ semantic-enhanced（masked semantic）→ few-shot
SkySense V2：统一骨干 + Adaptive Patch Merging + modality prompt + MoE
 + MGCL/GCPL 继承 + QSACL（查询聚合对比）
`

---

## 二、议题边界

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[天气气候基础模型]]** Aurora | 「地球相关 FM」相邻意识 | 再分析格点、滚动预报、气旋/海浪指标 |
| **[[MatterSim材料基础模型]]** MatterSim | （无技术接口） | 原子势 / 材料模拟 |
| **[[多模态架构脉络]]** 多模态通史 | 「对齐多传感器」可类比对比学习一句 | CLIP/LLaVA 产品通史 |

### 2.2 本篇立轴问题（2312 摘要/§1；Nature HTML；2507 摘要）

1. 单模态、弱时序、弱 geo-context 的 RSFM 难覆盖真实 EO（光学怕云；SAR 补全天候；变化要时序；区域先验有用）。
2. 下游任务爆炸（作物、灾害、海洋、大气、生物、测绘…），各从零训代价高。
3. 后继动机分叉：**++** → 标注稀缺 / 时效（如快速洪水）；**V2** → 分骨干参数冗余 + 自然图像对比直接搬到「一图多语义」RS 图的失配。

### 2.3 谱系关系（禁编造成单一路线）

| 节点 | 时间锚（可核） | 相对 SkySense 主增量 |
|---|---|---|
| **SkySense** | arXiv v2 **2024-03-22**；++ 引 **CVPR 2024** | 原点：因子化 + MGCL + GCPL |
| **SkySense V2** | arXiv v1 **2025-07-18** | **统一骨干**效率线（同作者群 Ant+WHU） |
| **SkySense++** | Nature MI **2025-08-04** | **语义增强 + few-shot**（GitHub：自 SkySense ckpt 续训） |

> **读法：** V2 与 ++ 为 **并行后继**（日期接近、问题陈述不同），笔记用对照表，不硬串成「三代线性演进」。

---

## 三、SkySense（2312）：因子化十亿级 MM-RSFM

### 3.1 输入与数据（§3 / Table I11 / Appendix I–J）

| 模态 | 传感器（文内） | 波段/极化 | GSD | 典型尺寸 | 平均序列长（Table I11） |
|---|---|---|---|---|---|
| **HSROI** | WorldView-3/4 等 | RGB | **0.3 m** | **2048×2048** | **1**（静帧） |
| **TMsI** | Sentinel-2 Level-2A | B2–8, B8A, B11–12 | **10 m** | **64×64** | **65** |
| **TSARI** | Sentinel-1 Level-1 IW GRD | VV, VH | **10 m** | **64×64** | **13** |

- 预训练：**21.5 million** RSI temporal sequences（摘要）；覆盖约 **8.78 million km²**、**40** 国、六大洲；存储约 **300 TB**（Appendix I）。
- 训练时对 TMsI / TSARI **随机抽固定长度**（实现细节：**20** / **10**），并对获取日期做扰动（§J）。
- 预训练：batch **240**，**875k** steps，**80×A100-80GB**，AdamW；**24600 A100 GPU hours**；文称 **4488.69 GFLOPs**（§J）。

### 3.2 架构三件套

1. **Factorized multi-modal spatiotemporal encoder**
 - 分模态空间编码 `g_HR` / `g_Ms` / `g_SAR` → **Multi-modal Temporal Fusion Transformer**（日期位置编码 + extra token）。
 - 意图：空间与融合解耦 → 下游可拼 **单模态静帧** 或 **多模态时序**（Table 1 对比输入覆盖）。

2. **Multi-Granularity Contrastive Learning（MGCL）**
 - Teacher–student（DINO 系 EMA）。
 - 空间：pixel / object / image；模态：各 $F_i$ 与融合 $F_{\mathrm{fus}}$；另有 cross-modal alignment。

3. **Geo-Context Prototype Learning（GCPL）**
 - 全球划 **4096** 区，每区约 **4294 km²**、**100** 个原型；学生支无监督区域原型，下游可选增强。

### 3.3 参数分解（Table J12）

| 模块 | 架构 | #Params |
|---|---|---:|
| Spatial Encoder-HSROI | **Swin-Huge** | **654M** |
| Spatial Encoder-TMsI | **ViT-Large** | **302M** |
| Spatial Encoder-TSARI | **ViT-Large** | **302M** |
| Multi-modal Temporal Fusion Transformer | Transformer Encoder（文述 **24** 层） | **398M** |
| Geo-Context Prototype | — | **215M** |
| Others | — | **189M** |
| **合计（文述）** | | **2.06B** |

附录报告换 **Swin-Large（197M）** 的消融：参数大降，仍强于若干基线——文强调增益 **不只靠堆参**（Table D8 一带）。

### 3.4 评测字段（摘要口径）

- **16** datasets × **7** tasks；对比 **18** 个近期 RSFM。
- 相对 **GFM / SatLas / Scale-MAE** 平均高出 **2.76% / 3.67% / 3.61%**（摘要原文）。
- 覆盖叙述：单→多模态、静→时序、分类→定位（检测/分割/变化检测等）。

---

## 四、SkySense++（Nature MI）：语义增强与 few-shot

> 依据：**Nature HTML 摘要 + Data/Code + GitHub README**。PDF Methods / Extended Data **待核实**。

### 4.1 问题陈述（HTML 摘要）

- 既有 RSFM 常 **单模态时序** 预训练 → 多模态不足。
- 下游仍需 **大量标注微调** → 时效场景（如 rapid flood mapping）吃力。
- 回答：保持 **factorized** 多传感器架构；**progressive pretraining** 两阶段；数据 **27 million** multi-modal RS images。

### 4.2 两阶段（HTML 摘要原词）

| 阶段 | 名称 | 方法 | 目标 |
|---|---|---|---|
| 1 | **representation-enhanced** | **multi-granularity contrastive learning** | 通用表示（与 SkySense MGCL 同族） |
| 2 | **semantic-enhanced** | **masked semantic learning** | 语义更丰 → **few-shot** |

### 4.3 评测与开放资源

- **12 EO tasks × 7 domains**：agriculture, forestry, oceanography, atmosphere, biology, land surveying, disaster management（HTML；README EO Benchmark 表对齐）。
- 任务类型：classification / detection / segmentation；相对 previous SOTA（含 SkySense）一致提升（HTML；**具体百分点待 PDF**）。
- **Data**：Zenodo `10.5281/zenodo.14994429`；部分源数据禁止再分发。
- **Code**：Nature → https://github.com/kang-wu/SkySensePlusPlus；LotusWhu 镜像 README 同文。
- GitHub：RS-Semantic **13** 像素级数据集表；预训练 **从 SkySense 权重继续**；1-shot flood-3i 脚本；antmmf + mmseg，A100。

### 4.4 与 V2 一句对照

++ 主叙事：**语义第二阶段 → 少样本应急**；V2 主叙事：**统一骨干 → 参数效率 + QSACL**。共享 Ant + WHU 作者群，**主张不同**，勿混为一个 checkpoint 名。

---

## 五、SkySense V2（2507）：统一骨干与参数效率

### 5.1 批评点（§1，针对 SkySense）

- SkySense：HR→**Swin**，MS/SAR→**ViT** → 三套骨干，文称合计约 **1.26B**（仅分模态骨干口径），冗余。
- 预训练偏 DINOv2 式自然图像对比：RS **单图多地物**，不同 crop 可能语义不一致 → 视图对比易错配。

### 5.2 统一 Transformer + APM + prompt + MoE

| 组件 | 作用（文内） |
|---|---|
| **Unified hierarchical backbone** | 四阶段共享；前两阶段 **SwinV2 blocks**，后两阶段 **vanilla Transformer blocks** |
| **Adaptive Patch Merging（APM）** | HR：2×2 合并降分辨率；MS/SAR：**保持分辨率**（投影/平均），对齐同位置特征 |
| **Modality-specific prompt tokens** | 后两阶段插入可学习 prompt，注意力交互后丢弃 |
| **MoE** | 文内 **L = 6, M = 8, k = 1**；消融称更多专家更强但参数大增，默认 **8** |

**参数口号：** 统一骨干同时吃三模态，仅 **665M**；相对 SkySense 三骨干 **1.26B**。

### 5.3 预训练损失（§3.2 / Fig.5）

继承 teacher–student，组合（加权和）：

- **MGCL**（多粒度对比，承 SkySense）
- **GCPL**（geo-context，承 SkySense）
- **QSACL**（Query-based Semantic Aggregation Contrastive Learning）：可学习 query 跨区域聚合同类语义再对比
- 管线叙述另含 **Dense Image-Text Alignment**（细节多在附录）

数据叙述：约 **21 million** multi-modal RS imagery **sets**（每套 HR + S2 时序 + S1 时序）——与 SkySense「21.5M sequences」、++「27M images」**单位不同，禁自行等同**。

### 5.4 评测字段

- **16 datasets × 7 tasks**。
- 摘要：平均超过 SkySense **1.8** points。
- 正文另有分任务平均叙述（如变化检测等表）；引用时回原文表，勿跨表平均。

---

## 六、三方对照表

| 维度 | **SkySense** | **SkySense++** | **SkySense V2** |
|---|---|---|---|
| 文献 | arXiv 2312.10115v2 / CVPR 2024（++ 引） | Nature MI 2025 DOI …01078-8 | arXiv 2507.13812v1 |
| 骨干哲学 | **因子化三编码器** | **继承因子化**（HTML） | **统一共享 Transformer** |
| HR / MS / SAR | Swin-Huge / ViT-L / ViT-L | （PDF 待核实；GitHub 续训 SkySense） | 共享四阶段 + **APM** |
| 特色模块 | Fusion Transformer + **GCPL** | **Masked semantic** 第二阶段 | **Prompt + MoE + QSACL** |
| 预训练数据口径 | **21.5M** temporal sequences | **27M** multi-modal images | ~**21M** multi-modal sets |
| 规模口号 | **2.06B** 总参 | （HTML 未给总参 → 待核实） | 统一骨干 **665M**（vs 三骨干 **1.26B**） |
| 下游卖点 | 16×7，全面超 18 RSFM | **12×7 域** + **few-shot** | 16×7，平均 **+1.8** vs SkySense |
| 开源重心 | 文称将释权重 | GitHub + Zenodo | （本稿以 arXiv 为主） |

---

## 七、评测地图（字段级）

### 7.1 SkySense / V2：「16×7」

典型簇：场景分类（AID, RESISC-45, BEN…）、语义分割（Potsdam, iSAID, DynamicEarthNet…）、检测（DIOR, DIOR-R, FAIR1M）、变化检测（OSCD, LEVIR-CD…）、多模态作物/土地覆盖（PASTIS-MM, BEN-MM…）。
比分数时核对 **模态组合、输入尺寸、冻结/全微调协议**。

### 7.2 SkySense++：「12×7 域」（README）

域例：Agriculture（Germany crop）、Forestry（TreeSatAI / Atlantic deforestation）、Oceanography（SOS oil spill）、Atmosphere（3pollution）、Biology（Kenya wildlife）、Land surveying（C2Seg-BW / dsifn-cd）、Disaster（Flood-3i, C2SMSFloods, CABUAR, GVLM, xBD）。
强调跨域泛化 + 少样本，与 SkySense 主表的经典视觉基准叙事互补。

---

## 八、开放资源与核实状态（2026-09-22 CST）

| 项 | 状态 |
|---|---|
| `https://arxiv.org/pdf/2312.10115`； | **已下载**，全文可核 |
| `https://arxiv.org/abs/2507.13812` | **已下载**，全文可核 |
| Nature PDF `s42256-025-01078-8` | **未取得**（idp 登录墙）；HTML 摘要/作者/DOI/数据代码链 **已核** |
| GitHub ++ | kang-wu 与 LotusWhu README **一致**；不跟踪 commit/哈希 |
| SkySense 权重 | 文承诺 release；++ README 给 Notion 入口——可用性随时间变 |

---

## 九、可撤回主张 / 待核实

1. Nature **Methods、Extended Data、few-shot 精确曲线**：仅 HTML 摘要级，**待 PDF**。
2. 「21.5M sequences / ~21M sets / 27M images」——**计数单位不同**，未在公开摘要中声明为同一语料简单增量。
3. V2 官方仓、与 ++ 是否共享 backbone——**本稿未证实**。
4. SkySense 会议页码以 CVPR 程序为准；本笔记以 arXiv v2 + Nature 引用为锚。

---

## 十、与相邻笔记的一句话接口

- → **[[天气气候基础模型]]**：同属「地球」大词；Aurora 吃 **再分析格点场**，SkySense 族吃 **光电/SAR 影像像素**。
- → **[[MatterSim材料基础模型]]**：无接口。
- → **[[多模态架构脉络]]**：对比学习/融合可交叉引用一句，不把本篇写进通用 VLM 通史。

## 相关笔记

- [[SkySense遥感基础模型|SkySense]]
- [[蛋白质设计|Protein Design]]
- [[ClaudeFable与Mythos51|Claude Fable / Mythos 5.1]]

