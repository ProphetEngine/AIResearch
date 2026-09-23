---
title: "MedGemma 1.5 Technical Report（医学专科多模态，12）"
topic: MedGemma医学专科
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2604.05081
 - https://developers.google.com/health-ai-developer-foundations/medgemma
 - https://developers.google.com/health-ai-developer-foundations/medgemma/model-card
arxiv: ["2604.05081"]
related: ["多模态架构脉络", "Gemma4技术报告深读", "B11"]
archived: 2026-09-22
---

# MedGemma 1.5 Technical Report（医学专科多模态）

> **定位**：医学专科短线——相对 **[[多模态架构脉络]] 通用多模态**（CLIP 对齐 → Flamingo 条件生成 → 指令对话 → 原生多模态主张），本卡写 **高监管医学域** 的开源权重向 TR：同一套 decoder-only + 冻结医学视觉编码器，如何把 **3D CT/MRI、WSI、纵向 CXR、解剖定位、实验室报告/EHR** 塞进统一生成式接口。
> **攻坚线**：**架构思想（主）** + **评测字段 / 安全与intended-use 边界（辅）**。
> **硬划界**：
> - **相对 [[多模态架构脉络]]**：只取「通用多模态接口已成立」为前提；**不重写** CLIP/Flamingo/LLaVA/Gemini 2.5 原生多模态史线。
> - **Legal specialty** 窗内无稳定长 TR → **本项不硬凑法律模型**（agenda 已明示）。
> - **禁止编造**：专家数/未给训练 token 总量、未公开的临床部署效果、监管批准状态——TR/卡未写则标「未公开」。数字锚定 Abstract / Table 3–6 / Model Card；摘要措辞与表内口径若不一致，**照录并并列**。
> - 产品页主张：**非 clinical-grade**；须验证与适配后再部署（docs / Model Card）。

---

## 1. 材料元信息

| 字段 | 核实值 |
|---|---|
| 标题 | *MedGemma 1.5 Technical Report* |
| 机构 | Google Research and Google DeepMind |
| 通信作者邮箱（页脚） | `{chufang, dangolden, asellerg}@google.com` |
| arXiv | **2604.05081v2** \[cs.AI\]（页眉：**1 May 2026**；官方 PDF 页眉日期 **2026-5-5**） |
| 官方 PDF | `https://arxiv.org/abs/2604.05081`（**23** 页 A4；约 **3.75 MB**） |
| 辅·产品概述 | [MedGemma \| Health AI Developer Foundations](https://developers.google.com/health-ai-developer-foundations/medgemma)（Last updated **2026-01-13** UTC） |
| 辅·Model Card | [MedGemma 1.5 model card](https://developers.google.com/health-ai-developer-foundations/medgemma/model-card)（Last updated **2026-04-21** UTC；**4B multimodal IT = 1.5.0**，**Model created: Jan 13, 2026**） |
| 资源入口 | TR：`https://goo.gle/medgemma`；HAI-DEF：`https://goo.gle/hai-def` |
| 许可 / ToU | 使用受 **Health AI Developer Foundations terms of use** 约束（Model Card；**非**「随便当诊断工具」） |
| 对照笔记 | 多模态与具身/视觉语言/多模态架构脉络.md（通用多模态脉络）；[[Gemma4技术报告深读]]（同系开源 TR 体例，**本卡骨干是 Gemma 3 而非 Gemma 4**） |

**集合内型号（Figure 1 + docs，勿混）：**

| 型号 | 本 TR 主写？ | 角色（报告/docs 用语） |
|---|---|---|
| **MedGemma 1.5 4B**（multimodal IT） | **是** | 本报告主角；新增高维影像 + 文档理解 |
| MedGemma 1 **4B** multimodal | 对照基线 | 前代 4B |
| MedGemma 1 **27B** text-only / multimodal | 对照；**本 TR 不更新 27B** | 「复杂临床知识与推理」仍可用 27B（Figure 1 文） |
| **MedSigLIP 0.4B** | 编码器组件 | 医学图分类 / 检索；无文本生成时优先用编码器本身（Model Card） |

**一句话抓手：** MedGemma 1.5 4B = **Gemma 3 同架构** + **冻结 400M MedSigLIP** + 继续 PT / 蒸馏 / RL；在 **不换骨干** 的前提下，用 **长上下文切片 / 病理 patch 采样 / 专科教师蒸馏** 把高维医学模态塞进统一 VLM——产品定位是 **可微调的开发者基础模型**，不是开箱临床决策系统。

---

## 2. 相对 [[多模态架构脉络]]：为何是「高监管专科」而非再写一遍通用多模态

| 维度 | [[多模态架构脉络]] 通用多模态 | **本卡：医学专科** |
|---|---|---|
| 问题 | 如何让同一助手接口吃图/文（对齐 → 生成 → 指令 → 原生主张） | 在**已成立的生成式接口**上，如何覆盖 **CT/MRI 体数据、WSI、纵向片、解剖框、实验室 PDF/EHR** |
| 数据监督 | 互联网图文 / 交错网页 / 视觉指令 | **去标识临床影像 + 报告 + FHIR/合成 EHR + 实验室 PDF**；大量 **internal / licensed**（Table 1；Model Card Data） |
| 视觉编码 | CLIP / NFNet / 通用 SigLIP 等 | **MedSigLIP**（医学去标识数据上预训练的 SigLIP 变体）；本版 **冻结** |
| 输出责任 | 一般助手错误可纠正 | **输出不得直接用于诊断/治疗**；须独立验证与临床相关性（Model Card Limitations） |
| 评测 | VQA / caption / 通用榜 | **医学 MCQ + 专科影像分类/报告/定位/纵向 + 文档 JSON 抽取**；另有 **内容安全 / 医疗伤害** 类别（Model Card） |
| 本卡不写 | — | **法律 LLM / 判例检索 / 合同审查**（无稳定长 TR；agenda 禁硬凑） |

跟读口诀：**[[多模态架构脉络]] 解决「能不能看图说话」；[[MedGemma医学专科]] 解决「在监管敏感域里，看哪些图、怎么切片、评什么、以及不能声称什么」。**

---

## 3. 架构主轴（§2 Methods）

### 3.1 骨干：与 Gemma 3 同构，视觉侧冻结 MedSigLIP

TR §2 原文要点：

- MedGemma 4B 1.5 **基于 Gemma 3**（Team et al., 2025），**same architecture**。
- 视觉编码器：**400M MedSigLIP**（Sellergren et al., 2025；Zhai et al., 2023）。
- 训练时：**vision encoder frozen**；对 **language decoder** 做额外预训练（supervised finetuning of the LLM）。
- 数据混合：原 Gemma mixture 的 **text + interleaved imaging** + 新医学域图文对（Table 1）；经由 **additional pretraining、distillation、RL** 组合使用。

Model Card 技术规格（与 TR 对齐、作部署字段）：

| 项 | 值 |
|---|---|
| 类型 | Decoder-only Transformer（见 Gemma 3 TR） |
| 输入 | Text + vision；图规范化为 **896×896**，每图编码为 **256** soft tokens |
| 输出 | **Text only** |
| 注意力 | GQA |
| 上下文 | **至少 128K** tokens |
| 输出长度（卡） | 总输出至多 **8192** tokens（卡字段；TR 训练时另有 32K 量级内存约束，见下） |

→ 相对 [[多模态架构脉络]] 的 Flamingo「插 gated xattn」叙事：本卡公开的是 **「专科编码器 + 同系 LLM 继续训」** 产品线增量，**不是**新提出一种跨模态耦合算子。架构思想增量主要在 **预处理把 3D/WSI 变成可吃的 2D token 序列** 与 **专科蒸馏/RL 配方**。

### 3.2 后训练：与 Gemma 3 同配方 + 医学教师

§2.2：

- **Distillation + RL**，recipes **same as Gemma 3**，但两边都加医学数据。
- 蒸馏：每 token 采样 **256** 个 teacher logits，按 teacher 概率加权，对学生做交叉熵（引 Team et al., 2025）。
- 1.5 增量：除改进的大型 IT teacher 外，增加 **域专科 teacher**（例：在 CT Dataset 1、MRI Dataset 1、Internal histopathology 上训的 supplementary teachers）。
- 文档理解：蒸馏 **EHRQA**（Synthea 合成 FHIR）及 EHR Datasets **2–5**。

### 3.3 高维影像如何进 2D 编码器（本卡真正的「架构接口」）

#### 3.3.1 体数据 CT / MRI（§2.3.1）

| 步骤 | 报告做法 |
|---|---|
| 为何要切 | 编码器 **只能吃 2D RGB** → 3D 体 → **轴向 2D 切片序列** |
| 分辨率 | 每片 rescale 到 **896×896** |
| 切片上限 | 训练/评测每 query **最多 85 片** ≈ **21,760** vision tokens；加上 indication / findings，控制在约 **32K** tokens 以内（内存） |
| 体纳入条件 | 每片 ≤ **512×512**；轴向；同层厚；≥5 片；可自多卷 z-stack |
| CT 窗映射→RGB | R (−1024,1024)；G (−135,215)；B (0,80)（HU multi-channel windowing） |
| MRI | **无**生理窗；体级 min-max；R=G=B |
| 过长体 | 沿 z **等距抽片** |

#### 3.3.2 病理 WSI（§2.3.2）

| 步骤 | 报告做法 |
|---|---|
| 组织掩膜 | 低倍（5×）HSV 多阶段分割（引 Ahmed et al., 2025） |
| 倍率随机 | P(5×)=0.34，P(10×)=0.33，P(20×)=0.33 |
| Patch | **896×896** 非重叠；仅组织区 |
| 上限 | **126** patches / slide → **32,256** vision tokens（比 CT 的 85 片更高：因 caption 更短） |
| 顺序 | **保留原始空间顺序** |
| 数据规模 | 内部 ~**335,825** WSI–text；评测 **9,614**；RL 用 **token-level ROUGE-L** |

**跟读点：** 「单一架构支持 3D/WSI」在工程上 ≈ **序列化 + token 预算 + 域预处理**，不是换一个 3D 卷积骨干。Appendix A 还点明：对 CT-RATE 等任务，VLM 常需 **按条件多次查询**（18 次/例），相对专用 CT 分类器有推理成本瓶颈。

---

## 4. 训练数据增量（Table 1，相对 MedGemma 1）

> 仅录报告给出的 **No. Train Examples** 与阶段标签（PT / Distill / RL）；**不**臆造总 token。

| 模态 | 数据集（报告名） | 规模（Train） | 阶段 |
|---|---|---|---|
| Radiology | CXR-IND1 | 605,732 | PT, Distill, RL |
| | CT Dataset 1 | 282,963 | PT, Distill, RL |
| | MRI Dataset 1 | 167,674 | PT, Distill, RL |
| | Chest ImaGenome | 39,968 | RL |
| Pathology WSI | Internal WSI Histopathology | 335,825 | PT, RL |
| Dermatology | Dataset 4 / 5 / ISIC | 25,560 / 87,879 / 40,269 | 见表 |
| EHR / Lab | EHRQA∗ | 9,809 QA pairs | Distill |
| | EHR Dataset 2–4 | 页级见 Table 1 | Distill |
| | EHR Dataset 5 | 33,882 user queries | Distill |

∗ 注：EHRQA 曾用于 MedGemma 1 **27B** 训练，**未**纳入 MedGemma 1 **4B**；Model Card 亦称其为 EHR Dataset 1。

---

## 5. 评测字段（§3 + Figure 2 + Tables）

### 5.1 Abstract 宣称的绝对增益（相对 MedGemma 1 4B）

| 能力 | Abstract 数字 | 表内锚点（照录） |
|---|---|---|
| 3D MRI 条件分类 | **+11%** accuracy | Table 4：51.3 → **64.7** |
| 3D CT 条件分类 | **+3%** accuracy | Table 4：58.2 → **61.1** |
| WSI | **+47%** macro F1（摘要措辞） | Table 4 指标为 **ROUGE-L**：2.2 → **49.4**（约 +47pp；指标名与摘要「macro F1」不一致 → **并列保留**） |
| 解剖定位 | IoU **+35%** | Table 4：3.1 → **38.0** |
| 纵向 CXR | macro accuracy **+4%** | Table 4：61.1 → **65.7** |
| MedQA | **+5%** | Table 3：64.4 → **69.1** |
| EHRQA | **+22%** | Table 3：67.6 → **89.6** |
| Lab report 抽取 | 摘要：「4 个数据集上平均 **18%** macro F1」 | Table 4 绝对 Macro F1：91 / 71 / 64 / 85；相对 1.0 的增益约 +13/+21/+39/+0 → **平均约 +18pp**（摘要「achieves … 18%」更像增益口径；**勿把 18 当成绝对分数**） |

Figure 2 脚注硬约束：**out-of-the-box 有希望，但模型「is not meant to be deployed without the necessary clinical fine-tuning」。**

### 5.2 原任务表节选（Table 3，Small Models 列）

| 任务 | 指标 | MedGemma 1 4B | **1.5 4B** | MedGemma 1 27B |
|---|---|---|---|---|
| MedQA (4-op) | Acc | 64.4 | **69.1** | 85.3 |
| MedMCQA | Acc | 55.7 | **59.8** | 70.2 |
| PubMedQA | Acc | 73.4 | 67.6 ↓ | 77.2 |
| MMLU Med | Acc | 70.0 | 69.7 | 86.2 |
| EHRQA | Acc | 67.6 | **89.6** | 90.5 |
| EyePACS | Acc | 64.9 | **76.8** | 75.3 |
| SLAKE tokenized F1 | | 72.3 | **59.8** ↓ | 70.3 |
| VQA-RAD tokenized F1 | | 49.9 | 48.1 | 46.7 |
| MedXpertQA (text+MM) | Acc | 18.8 | **26.4** | 26.8 |
| MIMIC CXR report | RadGraph F1 | 21.9 | **27.2** | 27.0 |

评测协议要点（§3）：MedGemma 1.5 多用 **temperature 0.0**；提示词相对 1.0 **有更新**（Appendix B）；宣称评测 split **完全 held-out**。Model Card 注：SLAKE 上 1.5 **弱于** 1.0，因对 SLAKE Q&A 格式优化更少，可用微调补回。

### 5.3 新任务（Table 4）+ CT-RATE（Table 5）

| 任务 | 指标 | 1 4B | **1.5 4B** | 备注 |
|---|---|---|---|---|
| Chest ImaGenome 定位 | Mean IoU | 3.1 | **38.0** | 输出归一化 bbox JSON `[y0,x0,y1,x1]` |
| MS-CXR-T 纵向 | Macro-Acc | 61.1 | **65.7** | Improved / Stable / Worsened；†预训练时去掉报告中时间关系表述 |
| CT Dataset 1 | Acc | 58.2 | **61.1** | 头/胸/腹；条件平衡抽样 |
| MRI Dataset 1 | Acc | 51.3 | **64.7** | 脑/膝/腹 |
| WSI Histopath | ROUGE-L | 2.2 | **49.4** | vs PolyPath SOTA 49.8 |
| EHR Dataset 2/3/4 | Macro F1 | 78/50/25 | **91/71/64** | PDF/图 → JSON |
| CT-RATE（OOD，App. A） | Macro F1 | 23.5 | **26.9** | Gemini 3.0 Flash：**8.5**（同表） |

### 5.4 通用非医学能力的代价（Table 6）

| Benchmark | MedGemma 1 4B | **1.5 4B** | Gemma 3 4B§ |
|---|---|---|---|
| MMLU Pro | 39.1 | **33.8** ↓ | 43.6 |

报告解释：4B 档强推医学影像特化 → **域外通用推理下降**；认为医学多模态增益值得该 trade-off。

### 5.5 Limitations（§4）与 Discussion 设计哲学

- **Trade-off**：更「medical generalist」→ SLAKE / VQA-RAD 等遗留榜小幅回退；作者认为这些榜依赖 token overlap、标准答案未统一，且 1.5 在高维与 bbox 上更有用；窄任务可用 **targeted fine-tuning** 补。
- vs **Qwen3 VL 4B**：通用生物医学文本知识（如 MedQA）上 Qwen 更强；**所有视觉任务**上 MedGemma 1.5 更高——专科后训练 / 蒸馏的设计哲学差异。
- Discussion 明确：开箱功能是 **foundational data processing tools**，**distinct from automated clinical decision-making or the practice of medicine**。

---

## 6. 高监管边界（辅：docs + Model Card；非法律模型）

> 本节只录 **官方 intended use / limitations / 安全评测类别**，作「专科多模态」监管敏感面字段；**不**写临床操作指南，也**不**延伸到法律 AI。

### 6.1 Intended use（Model Card）

- 面向 **生命科学 / 医疗开发者** 的 **起点模型**，用于更高效开发含医学文本与图像的下游应用。
- 开发者负责：**训练、适配、有意义修改** 后用于其具体意图。
- 训练覆盖举例：CXR、病理、皮科、眼底、CT、MR、医学文本/文档、EHR；任务含医学 VQA、文档理解、文本医学问答等。

### 6.2 硬限制（Model Card Limitations，压缩）

1. **未经验证/适配，不得使用**；输出 **不**旨在直接指导临床诊断、患者管理、治疗建议或任何直接临床实践。输出视为 **preliminary**，需独立核实与临床相关。
2. 多模态评测 **primarily single-image**；**未**评多图理解用例（注：1.5 实际支持多片序列——卡文仍写「未评多图 comprehension」→ 跟读时区分「能输入多片」≠「已完成多图产品评测」）。
3. **未**针对 multi-turn 优化/评测。
4. 对 prompt 可能比 Gemma 3 **更敏感**。
5. 适配时注意：**验证集偏见**（人群、设备等）与 **数据污染**高估泛化风险。

### 6.3 安全评测类别（Model Card；无本 PDF 分数表）

开发期 + assurance（arms-length）评测类别包括：

- Child safety
- Content safety（骚扰、暴力血腥、仇恨等）
- Representational harms
- **General medical harms**（信息质量、潜在有害/不准确回答）

声称：相对既往 Gemma，上述类别达 **safe levels**；**无安全过滤器**下测能力；**主要是英语提示**（局限）。高层面发现反馈给模型组，prompt set **hold-out** 防过拟合。**本 PDF 未附各类别数值表** → 勿编造分数。

### 6.4 产品页适应路径（docs，高阶）

docs 允许的适应类型（须同等验证）：**prompt / ICL**、**fine-tuning**（含 LoRA 笔记本）、**RL 笔记本**、**agentic orchestration**（与检索、FHIR、Gemini 等编排；可本地解析私有健康数据后再发匿名请求）。
→ 与 [[智能体工具与长程任务]] agents 线可交叉，但 **本卡不展开 agent 史线**。

---

## 7. 跟读地图（建议顺序）

1. Abstract + Figure 1：能力扩容清单。
2. §2.3 预处理：85 片 / 126 patch / CT 三窗——理解「高维进 2D」。
3. Table 1：数据与 PT/Distill/RL 标签。
4. Figure 2 + Table 3–4：增益与回退并读。
5. §4 Limitations + Table 6：专科化代价。
6. Model Card Intended use / Limitations：监管话术与「非临床级」边界。
7. （可选）Appendix A CT-RATE：OOD + 多次查询成本。

---

## 8. 未公开 / 勿外推清单

| 项 | 状态 |
|---|---|
| 完整预训练 token 总量 / 学习率表 | TR **未**给 → 不编 |
| MedSigLIP 解冻消融、3D 原生编码器对比 | **未**做（设计选择是冻结 2D） |
| 27B 的 1.5 更新 | **无**；集合仍指向 MedGemma 1 27B |
| 监管批准 / 临床试验终点 | **无**；明确非直接临床使用 |
| Legal specialty 对照模型 | **不做**（划界） |
| Model Card 与 TR 个别数字微差（如部分 MedXpert / CT-RATE 四舍五入） | **以本地下载 PDF Table 为准**，卡作产品字段 |

---

## 9. 五句话摘要（回报用）

1. **MedGemma 1.5 4B**（arXiv **2604.05081v2**，23 页）是 Google 医学开源多模态集合的增量 TR：骨干 = **Gemma 3**，视觉 = **冻结 400M MedSigLIP**。
2. 相对 [[多模态架构脉络]] 通用多模态，增量不在新耦合算子，而在 **高监管专科接口**：CT/MRI 轴向切片（≤85）、WSI patch 序列（≤126）、纵向 CXR、bbox 定位、实验室 PDF→JSON / EHR。
3. 训练路径 = 医学数据上的 **继续 PT + 专科教师蒸馏 + RL**；评测上 MRI 分类 **+11pp**、定位 IoU **3.1→38.0**、EHRQA **+22pp**，同时 SLAKE / MMLU Pro 等出现 **可预期回退**。
4. 官方定位是 **开发者基础模型**（须验证与微调），**不是**开箱临床决策；安全卡列 child/content/representational/**medical harms**，PDF 无细分数。
5. **不写法律模型**；材料以官方 PDF + HAI-DEF docs/Model Card 为限，禁编造未公开超参与监管状态。

## 相关笔记

- [[端侧小模型|On-device SLM]]
- [[MedGemma医学专科|MedGemma]]
- [[生物学基础模型|Biology Foundation Models]]
- [[表格与时序基础模型|Tabular / Time-series FM]]
- [[合成用户仿真|Synthetic User Simulation]]
- [[Gemma4技术报告深读|Gemma 4]]

