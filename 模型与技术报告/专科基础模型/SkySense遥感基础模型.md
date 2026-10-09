---
title: "Remote sensing EO FM：SkySense 谱系（含 SkySense++ / V2 对照）"
topic: SkySense遥感基础模型
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2312.10115
 - https://arxiv.org/abs/2507.13812
arxiv: ["2312.10115", "2507.13812"]
doi: ["10.1038/s42256-025-01078-8"]
related: ["天气气候基础模型", "地球系统基础模型ESFM", "多模态架构脉络"]
github:
 - "https://github.com/kang-wu/SkySensePlusPlus"
 - "https://github.com/LotusWhu/SkySensePlusPlus"
retrieval_cutoff: 2025
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# SkySense 谱系：多模态遥感基础模型（含 SkySense++ 与 SkySense V2）

> **主要来源**：[SkySense: A Multi-Modal Remote Sensing Foundation Model Towards Universal Interpretation for Earth Observation Imagery](https://openaccess.thecvf.com/content/CVPR2024/html/Guo_SkySense_A_Multi-Modal_Remote_Sensing_Foundation_Model_Towards_Universal_Interpretation_CVPR_2024_paper.html)（Guo 等，CVPR 2024，pp. 27672–27683，2024-06；预印本 [arXiv:2312.10115](https://arxiv.org/abs/2312.10115)）；[A semantic-enhanced multi-modal remote sensing foundation model for Earth observation](https://www.nature.com/articles/s42256-025-01078-8)（SkySense++，Wu 等，Nature Machine Intelligence 第 7 卷第 8 期，pp. 1235–1249，2025-08-04 在线发表，2025-08 刊期）；[SkySense V2: A Unified Foundation Model for Multi-modal Remote Sensing](https://openaccess.thecvf.com/content/ICCV2025/html/Zhang_SkySense_V2_A_Unified_Foundation_Model_for_Multi-modal_Remote_Sensing_ICCV_2025_paper.html)（Zhang 等，ICCV 2025，pp. 9136–9146；预印本 [arXiv:2507.13812](https://arxiv.org/abs/2507.13812)）（截至 2025）。SkySense++ 正文与 Methods 未能读到，只用其摘要与数据、代码说明。
> **研究线**：架构思想（主：因子化多模态时空编码器，后继分为语义增强与统一骨干两支）+ 评测字段（辅）
> **范围与相邻笔记**：
> - ≠ [[天气气候基础模型]]：本篇不写再分析格点场的天气预报，只写卫星与航空影像解译。
> - ≠ [[地球系统基础模型ESFM]]：本篇不写把卫星产品当物理变量场做预报的做法。
> - ≠ [[多模态架构脉络]]：本篇不写 CLIP、Flamingo 等通用多模态通史，只取遥感多传感器这一切面。
>
> **意义**：SkySense 把高分辨率光学、多光谱时序与 SAR 时序三类遥感数据放进一个可拆装的十亿级模型，证明多模态、时序与地理上下文能同时提升从分类到检测、分割、变化检测的大范围遥感任务；两条后继分别回答「标注稀缺时如何少样本迁移」（SkySense++）和「三套骨干能否合成一套」（SkySense V2），代表遥感基础模型从堆规模转向语义能力与参数效率。

## 一、问题背景

遥感影像解译要面对多种传感器：高分辨率光学影像细节丰富但怕云，多光谱影像覆盖广、可看植被与水体，合成孔径雷达（SAR）能全天候成像；许多任务（作物、变化检测）还依赖时间序列，区域地理先验也有用。此前的遥感基础模型大多只用单一模态，缺少时序与地理上下文建模，难以覆盖多样任务（SkySense 摘要）。下游任务又极其分散，涵盖农业、林业、海洋、大气、生物、测绘、灾害等，每类从零训练代价高。后继工作在此基础上发现两类新问题：一是下游仍需大量标注微调，应急场景（如快速洪水制图）等不及（SkySense++ 摘要）；二是为每种模态单独训练骨干造成参数冗余，且直接搬用自然图像的自监督方法，不适应「一幅遥感图里有多种地物」的特点（SkySense V2 摘要）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2023-12 | SkySense 预印本（v2 2024-03-22） | 提出因子化多模态时空编码器、多粒度对比学习与地理上下文原型学习 |
| 2024-06 | SkySense 正式发表（CVPR 2024） | 十亿级多模态遥感基础模型 |
| 2025-07 | SkySense V2 预印本 | 三模态共享一套 Transformer 骨干，追求参数效率；后于 ICCV 2025 正式发表 |
| 2025-08 | SkySense++（Nature Machine Intelligence） | 保留因子化架构，加入语义增强的第二阶段预训练，支持少样本 |

SkySense 出自蚂蚁集团、武汉大学与网商银行。V2 与 SkySense++ 是同一作者群（蚂蚁集团与武汉大学）几乎同时发表的两条后继，问题陈述不同，不宜串成「三代线性演进」。

## 三、SkySense：因子化的十亿级多模态模型

- **输入**：地理对齐的三类数据，WorldView 等高分辨率光学 RGB 影像（静帧，原文记作 HSROI）、Sentinel-2 多光谱时序（TMsI）、Sentinel-1 SAR 时序（TSARI，VV、VH 极化）；预训练数据为 21.5M 条遥感时序样本（CVPR 版摘要与 §3）。
- **因子化时空编码器**：先按模态分别做空间编码（光学用 Swin-H，多光谱与 SAR 用 ViT-L），再由多模态时序融合 Transformer 融合，日期作为位置编码。空间与融合解耦，下游既可只用单模态静帧，也可用多模态时序。
- **多粒度对比学习**：师生框架下，在像素、对象、图像三种空间粒度与单模态、融合两种模态粒度上做对比学习。
- **地理上下文原型学习**：把全球分成 4096 个区域，为每个区域学习一组原型，下游可选用以引入区域先验。
- **规模与结果**：共 2.06B 参数；在 7 类任务的 16 个数据集上评测，超过 18 个近期遥感基础模型，相对 GFM、SatLas、Scale-MAE 平均分别高 2.76%、3.67%、3.61%（摘要；参数量见 §1）。

## 四、两条后继

### 4.1 SkySense++：语义增强与少样本

据 Nature Machine Intelligence 摘要：保留因子化架构，在 2700 万幅多模态遥感影像上做两阶段渐进预训练。第一阶段「表征增强」用多粒度对比学习获得通用表征；第二阶段「语义增强」用掩码语义学习获得更丰富的语义表征，从而能以极少标注处理未见任务。在农业、林业、海洋、大气、生物、测绘、灾害管理 7 个领域的 12 项任务上，分类、检测、分割一致优于此前最好模型。论文给出的代码仓库为 kang-wu/SkySensePlusPlus；其 README 的预训练步骤要求先下载 SkySense 的预训练权重，并列出语义增强预训练所用的 RS-Semantic 数据集（由 13 个带像素级标注的数据集组成），数据经 Zenodo 发布。部分原始数据的提供方禁止再分发，使用者需直接与原始数据提供方签署协议（Nature 页 Data availability）。

### 4.2 SkySense V2：统一骨干与参数效率

- **批评点**：SkySense 的光学用 Swin、多光谱与 SAR 用 ViT-L，三套骨干合计 1.26B 参数，存在冗余（ICCV 版 §1）。
- **统一骨干**：三模态共用四个阶段的骨干（前两阶段用 SwinV2 块，后两阶段用标准 Transformer 块），参数共享；自适应 patch 合并（APM）在高分辨率光学分支做 2×2 下采样，在多光谱与 SAR 分支保持分辨率，以对齐不同地面分辨率；后两阶段插入可学习的模态提示 token，并加入混合专家（MoE）模块（§3）。
- **预训练**：沿用 SkySense 的多粒度对比与地理原型学习，新增基于查询的语义聚合对比学习（QSACL），用可学习查询在不同区域间聚合同类语义再做对比，以适应一图多地物；训练数据与 SkySense 相同，约 2100 万组多模态影像（§3、§4.1）。
- **结果**：统一骨干只有 665M 参数即可处理三种模态；在同样的 16 个数据集、7 类任务上平均超过 SkySense 1.8 个点（摘要）。

### 4.3 小对照表

| 维度 | SkySense | SkySense++ | SkySense V2 |
|---|---|---|---|
| 骨干 | 因子化三编码器 | 沿用因子化 | 三模态共享一套骨干 |
| 特色模块 | 时序融合 Transformer、地理原型 | 第二阶段掩码语义学习 | APM、模态提示、MoE、QSACL |
| 预训练数据（各文口径） | 21.5M 条时序样本 | 27M 幅多模态影像 | 约 21M 组多模态影像（与 SkySense 同一数据集） |
| 规模 | 2.06B 参数 | 摘要未给 | 骨干 665M 参数 |
| 评测 | 7 类任务 16 个数据集 | 7 个领域 12 项任务，强调少样本 | 同 SkySense，平均高 1.8 点 |

## 五、局限与待核实

1. **SkySense++ 正文未读**：Nature 全文需登录，Methods、Extended Data 与少样本曲线的具体数字未核，本篇只用摘要与数据、代码说明；其总参数量未在摘要中给出。
2. **数据口径**：SkySense 的 21.5M 时序样本与 V2 的约 21M 组影像，V2 明说是同一数据集，计数措辞不同；SkySense++ 的 27M 幅影像与前两者的关系，摘要未说明。
3. **V2 与 SkySense++ 的关系**：两者是否共享权重或骨干，未见说明。
4. **评测可比性**：比较分数时须核对模态组合、输入尺寸与冻结或全量微调协议；V2 的分任务平均要回原文表格，不宜跨表平均。
5. **权重可得性**：SkySense 正式版称将发布预训练权重；实际可用性随时间变化，本篇未核。
6. **版本**：SkySense 与 V2 的数字按 CVPR 2024、ICCV 2025 正式版；SkySense 的参数分解、预训练算力等细节只见于 arXiv 版附录，本篇不再列出。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[天气气候基础模型]] | 两篇都是地球观测相关的基础模型，那篇输入再分析格点场做预报，本篇输入光学与 SAR 影像做解译 | 天气预报指标与多域微调 |
| [[地球系统基础模型ESFM]] | 两篇都使用卫星数据，那篇把卫星产品当物理变量场做预报，本篇做影像语义解译 | 缺失数据编码与集合预报 |
| [[多模态架构脉络]] | 多传感器对齐可类比通用多模态的对比学习 | 通用视觉语言模型通史 |

## 七、延伸阅读

- SkySense：原文 §3（因子化编码器、多粒度对比与地理原型）与主结果表。
- SkySense V2：原文 §3（统一骨干、APM、MoE 与 QSACL）、§4.1（训练数据）。
- SkySense++：Nature 页的 Data availability 与 Code availability；[kang-wu/SkySensePlusPlus README](https://github.com/kang-wu/SkySensePlusPlus)（Nature 论文 Code availability 指向的代码仓库，含评测基准表与数据入口）；[LotusWhu/SkySensePlusPlus README](https://github.com/LotusWhu/SkySensePlusPlus)（与 kang-wu 仓库 README 内容相同的另一处发布仓库）。
