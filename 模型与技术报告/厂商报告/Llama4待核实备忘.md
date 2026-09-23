---
title: "Llama 4（Scout/Maverick）正式 PDF TR 待核实备忘"
topic: TR-Llama-4
date: 2026-09-22
as_of: 2026-09-22
status: archived
lines: [架构思想]
archived: 2026-09-22
---

# Llama 4 pending：无正式 PDF Technical Report / Model Card

> **结论（2026-09-22 核实）：无正式 PDF TR → 待核实**
> Meta **未**发布类似 Llama 1/2/3 herd paper 的 **PDF** technical report，也 **未**发布独立 PDF model card。
> 本文件**不是**深读卡；禁止把下文表格当「论文已证实」的层图/训练配方来源。**禁止硬编**未在官方材料中出现的参数。

---

## 1. 官方入口（可核对 URL）

| 类型 | URL | 形态 |
|------|-----|------|
| 发布博文 | https://ai.meta.com/blog/llama-4-multimodal-intelligence/ | HTML（2025-04-05；本轮 HEAD **200**） |
| 同博文（大小写路径变体） | https://ai.meta.com/blog/Llama-4-multimodal-intelligence/ | 同上族入口 |
| GitHub Model Card | https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md | **Markdown**（非 PDF） |
| 官方 Docs 卡页 | https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama4 | HTML |
| 产品页 | https://www.llama.com/models/llama-4/ | HTML |
| 许可 | https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE | Llama 4 Community License |

**对照：** Meta Research 有 Llama / Llama 2 / *The Llama 3 Herd of Models* 正式文稿；**检索未找到** “Llama 4 Herd” 官方 PDF 出版物。

---

## 2. 已核实主张（仅据博文 + 官方 MODEL_CARD.md）

来源：GitHub `models/llama4/MODEL_CARD.md`（本轮 raw 拉取）及官博摘要口径；未另开 PDF。

| 项 | 官方声称（摘要） |
|----|------------------|
| 发布日 | **2025-04-05** |
| 架构口号 | 自回归 + **MoE**；**early fusion** 原生多模态 |
| Scout | **17B** activated / **109B** total；**16** experts；上下文 **10M**；预训练 **~40T** tokens |
| Maverick | **17B** activated / **400B** total；**128** experts；上下文 **1M**；预训练 **~22T** tokens |
| 输入 / 输出 | 多语文本+图像 → 多语文本与代码 |
| Knowledge cutoff | **August 2024** |
| 支持语言（卡内列名） | ar/en/fr/de/hi/id/it/pt/es/tl/th/vi（12 种）；图像理解测试至 **5** 张输入图 |
| 量化部署口径 | Scout：BF16；可 **Int4** 单卡 H100；Maverick：BF16 + **FP8**，FP8 可单 H100 host |
| 预训练能耗（卡表） | Scout **5.0M** / Maverick **2.38M** H100-80GB GPU hours；合计 **7.38M**；location-based **1,999** tCO₂eq |
| Behemoth | 官博 **预览**教师模型；**未**作为开放权重发布（卡内亦非完整 TR） |

评测数字、训练配方细节、路由/共享专家结构等：**仅以官方 MD/博文原文为准**；本备忘不转录整表，避免与「正式 TR」混淆。

---

## 3. 明确排除（勿当官方 PDF TR）

| 条目 | 说明 |
|------|------|
| arXiv:**2601.11659**（*The Llama 4 Herd: … Notes*） | **第三方汇编**；arXiv 管理员已撤稿（虚假作者名单）；**非** Meta 正式 TR |
| Zenodo / HF Papers 同名合成稿 | 同上族第三方整理，**不入库** `papers/` |
| GitHub/HF `MODEL_CARD.md` | 官方，但是 **MD/网页卡**，**不是** PDF technical report |

---

## 4. 本地动作与后续

- **未下载** PDF 至 `papers/` / （无可核官方 PDF URL）。
- **未写** Llama 4 深读卡（无 PDF 锚点）。
- 若 Meta 后续放出 herd PDF / 正式 model-card PDF：再下载并改写为深读卡；届时更新 模型与技术报告/SystemCard与TR扫描2025至2026.md 中 Llama 4 行。

**状态标签：无正式 PDF TR → 待核实。**

## 相关笔记

### 技术报告专项
- [[Grok4ModelCard|TR Grok 4 Model Cards]]
- [[Kimik15技术报告深读|TR Kimi k1.5]]
- [[KimiK2技术报告深读|TR Kimi K2]]
- [[Llama4待核实备忘|TR Llama 4 待核实备忘]]
- [[Mistral3公告短卡|TR Mistral / Ministral-3]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

