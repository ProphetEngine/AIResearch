---
title: "合成预训练新轴：BeyondWeb（≠ Nemotron-CC / FineWeb 通史 / 教科书合成 / 对齐合成）"
topic: BeyondWeb合成预训练
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2508.10975 # 1.56MiB / 29p；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2508.10975
 - https://arxiv.org/pdf/2508.10975
 - https://blog.datologyai.com/technical-deep-dive-curating-our-way-to-a-state-of-the-art-text-dataset/
 - https://www.arcee.ai/blog/announcing-the-official-launch-of-afm-4.5b
arxiv: ["2508.10975"]
related: ["NemotronCC数据策展", "B8", "B3", "合成对齐数据Magpie", "规模定律与预训练范式"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 合成预训练新轴：BeyondWeb（≠ Nemotron-CC）

> **定位**：BeyondWeb合成预训练 **P1 数据侧横切**——DatologyAI *BeyondWeb: Lessons from Scaling Synthetic Data for Trillion-scale Pretraining*（arXiv:**2508.10975**v2，页眉 **19 Aug 2025**）。立「**预训练侧 source-rephrasing 合成新轴 + 系统消融**」：在 web 文档上做多样式/格式改写，把合成语料推到 **万亿 token 预算仍可持续受益**，并给出相对 Cosmopedia / WRAP / **Nemotron-Synth** / RedPajama 的 Pareto。
> **攻坚线**：**架构思想（主）**——generator-driven vs source-rephrasing；质量种子 / 风格对齐 / 多样性三原则；改写器族与规模饱和；**评测字段（辅）**——Table 1 与 Fig.1（1B×1T、3B/8B×180B；14 基准 0+5-shot 均值）。
> **硬划界（开篇钉死）**：
> - **≠ [[NemotronCC数据策展]]**：禁止写成 **Nemotron-CC** 全管线（Justext→分类器集成→全局去重→HQ 合成改写→6.3T）复述。本卡只把 **Nemotron-Synth**（Nemotron-CC 的 **HQ 合成子集**）当 **合成预训练对照基线**；CC 策展增量见 [[NemotronCC数据策展]]。
> - **≠ B8**：禁止写成 phi / *Textbooks Are All You Need* / Cosmopedia 式 **教科书 / de novo 生成器驱动** 通史。本卡主轴是 **对已有网页 source rephrasing**；§4.2 把 Cosmopedia 当「可被简单摘要逼近」的对照，不升教科书主文。
> - **≠ B3**：禁止重写 **FineWeb / DCLM / Dolma** 抽取—启发式—模型过滤通史。文中 BeyondWeb 作用于「DCLM 高质量子集（DatologyAI 策展方法）」仅作 **种子来源一句**；过滤通史留 B3。
> - **≠ [[合成对齐数据Magpie]]**：Magpie / ActiveUltraFeedback 是 **对齐侧**指令/偏好合成；本卡是 **预训练侧** 改写合成 + 长程 scaling 消融。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。文内未公开的完整 prompt 配方 / BeyondWeb 专有生成策略细节 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 项 | 报告原文 / 元数据 | 出处 |
|---|---|---|
| 标题 | BeyondWeb: Lessons from Scaling Synthetic Data for Trillion-scale Pretraining | 封面； Title |
| 作者 | DatologyAI Team（XMP `dc:creator` 列 Pratyush Maini 等；§7 贡献表） | 封面；XMP；§7 |
| arXiv | **arXiv:2508.10975v2** \[cs.LG\]（兼 cs.CL）**19 Aug 2025** | PDF 页眉 |
| XMP identifier | `https://arxiv.org/abs/2508.10975v2` | ` -meta` |
| XMP MetadataDate | 2025-08-21T00:04:36+00:00（→ 用户时区 **2025-08-21 08:04 CST**） | XMP |
| 权利 | `http://arxiv.org/licenses/nonexclusive-distrib/1.0/` | XMP |
| 产品字段（摘要） | 相对 Cosmopedia **+5.1pp**、相对 Nemotron-Synth **+2.6pp**（14 基准均值）；相对 open web **7.7×**、相对 Nemotron-Synth **2.7×** 训练加速；**3B@180B** BeyondWeb **>** **8B@180B** Cosmopedia | Abstract；Fig.1 |
| 生产落地（文内一句） | BeyondWeb 为 DatologyAI 策展平台一部分；用于 ArceeAI **AFM4.5B** 的 **7T** 预训练语料策展 | §1 末 / Atkins 2025 引用 |
| PDF 页数 / 尺寸 | **29** 页 letter | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:) | XMP |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| **主 PDF（arXiv）** | `https://arxiv.org/abs/2508.10975` | **1.56MiB**（1,637,868 B） | **29** | **官方 HTTPS 外链**（≪10MB；页数适中） |
| **抽取** | | 113K（115,599 B） | — | 全文检索 |
| **辅：策展平台博文** | DatologyAI Technical Deep-Dive（文内引用 2024-11） | — | — | HQ 子集选取方法入口；**不替代**本 PDF 数字源 |
| **辅：AFM4.5B 公告** | arcee.ai blog（文内 Atkins 2025） | — | — | 生产落地叙事；**不替代**本 PDF 对照表 |

**一句话抓手：**
相对「堆更多网页」与「用大模型从零写教材」，BeyondWeb 把杠杆放在 **对 HQ 网页做多样式 source rephrasing**：在固定真实知识预算下抬 per-token 信息密度与部署风格对齐，并用 **多样性** 撑住 **1T 级**长训；系统消融证明 **没有银弹**——质量种子、风格、多样性、改写器选择须联合优化。

---

## 二、议题边界：合成预训练新轴 ≠ CC 策展通史 / ≠ 教科书 / ≠ 对齐合成

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **Nemotron-CC 全管线** | CC→过滤/去重/分类器→real+synth 6.3T | **[[NemotronCC数据策展]]** | **否**（仅 Nemotron-Synth 作基线） |
| **FineWeb / DCLM 过滤通史** | 抽取—启发式—模型过滤骨架 | **B3** | **否**（禁通史） |
| **教科书 / de novo 合成** | phi / Self-Instruct / Cosmopedia 生成器驱动 | **B8** | **否**（Cosmopedia 仅对照） |
| **对齐侧指令/偏好合成** | Magpie / ActiveUF | **[[合成对齐数据Magpie]]** | **否** |
| **BeyondWeb 合成预训练轴** | source rephrasing 原则 + 万亿预算消融 + 文内 Pareto | **本篇** | **是** |

跟读直觉：[[NemotronCC数据策展]] 问「**如何把 CC 做成长程仍可用的策展语料**」；B3 问「**网页过滤通史**」；B8 问「**从知识库/模型造教科书式内容**」；[[合成对齐数据Magpie]] 问「**对齐数据从哪来**」；本卡问「**预训练合成改写的哪些因素真正决定质量，以及如何在万亿预算下持续受益**」。共享「合成 / Nemotron / Cosmopedia」词汇，但 **阶段（预训练 vs 对齐）与范式（rephrase vs de novo vs CC 全管线）不同**——禁止写成「又一篇 Nemotron-CC」或「FineWeb 过滤续篇」。

`
 数据侧「合成 / 策展」近窗
 │
 ┌─────────┼─────────┬──────────────┐
 │ │ │ │
 [[NemotronCC数据策展]] B3 B8 [[合成对齐数据Magpie]]
 Nemotron- FineWeb/ 教科书/ Magpie/
 CC 管线 DCLM 通史 Cosmopedia ActiveUF
 │ │ │ │
 └─────────┴────┬────┴──────────────┘
 │ 禁止复述 / 禁过滤通史
 ▼
 ★ BeyondWeb BeyondWeb
 source-rephrasing 合成预训练
 + 七问消融 + Pareto（vs Nemotron-Synth）
`

### 2.2 两范式对照（§2，本卡主骨架）

| | **Generator-driven** | **Source rephrasing**（本卡主轴） |
|---|---|---|
| 知识来源 | 大模型参数记忆 → de novo 写教材/故事 | **已有网页** → 小/中模型改写为更高信息密度 / 任务对齐格式 |
| 代表 | TinyStories；Phi；**Cosmopedia** | WRAP；Nemotron-CC 合成；**BeyondWeb** |
| 成本/风险 | 依赖 GPT-4 级生成器；覆盖与幻觉/collapse 风险（§2.1） | 条件于真实文档 → 覆盖广、算力更低；工业界 2025 主范式（文称 Kimi K2 / Qwen2.5 / Grok / GPT-5 均报道重用） |
| 本卡结论入口 | §4.2：简单 **摘要** ≈ Cosmopedia → 收益大量来自 **信息密度**，非「复杂知识蒸馏」 alone | BeyondWeb 再显著拉开摘要 / Cosmopedia |

---

## 三、BeyondWeb 方法与实验设定（§3）

### 3.1 主张（压缩）

BeyondWeb：**以 grounding（锚定真实网页）+ diversity（多样生成策略）** 做合成预训练数据。策略族包括（文内列举，**无完整 prompt 公开**——笔记不编造配方）：

- **格式变换**（如网页 → QA）
- **风格修改**（如增强教学语气）
- **内容重组**（抬信息密度与可学性）

作用于：**DCLM 的高质量子集**（选取方法见 DatologyAI et al. 2024；**不在此复述 B3/DCLM 过滤通史**）。

### 3.2 对照数据集（混合策展）

除纯真实基线外，合成对照采用 **60% 随机 RPJ + 40% 合成**：

| 数据集 | 角色（据 §3） | 笔记边界 |
|---|---|---|
| **RedPajama (RPJ)** | 最少策展 open web；真实基线 | 本卡真实对照 |
| **Cosmopedia-v2** | 生成器驱动；≈**27B** token；不够则 **重复**（作者承认是生成器范式局限） | ≠B8 通史；仅数字对照 |
| **QA WRAP** | WRAP 式；源=RPJ；改写器=**Llama-3.1-8B-Instruct**；主风格 QA | WRAP 方法点名 |
| **Nemotron-Synth** | Nemotron-CC **HQ 输入**上多样式改写的 **HQ 合成子集**；文称含 **1.5T** token，实验随机子采样保比例 | **≠[[NemotronCC数据策展]] 全管线**；仅此子集作最强合成基线 |
| **BeyondWeb** | 本方法；种子=DatologyAI 选的 DCLM HQ | 本卡主对象 |

### 3.3 训练 / 评测设定

| 项 | 设定（§3 / App. A.1） |
|---|---|
| 模型 | **1B**：Llama-3.2，**1T** token；**3B**：Llama-3.2，**180B**；**8B**：Llama-3.1，**180B** |
| 优化 | AdamW β1=0.9 β2=0.95；lr **5e-4**；wd **1e-7**；warmup 1B:**4K** / 3B&8B:**16K**；FSDP；batch **512**；ctx **2048** |
| 超参 | 除早期在 RPJ 上搜索外，**不广泛调参**——目标是 **仅数据干预** 抬性能 |
| 评测 | **14** 任务（App. A.2：含 FineWeb 常用 8 + 额外）；**0-shot + 5-shot** 均值；多选 relative / cloze-form（HF OpenLLM / Gu et al. 2025） |

---

## 四、主结果：Pareto 与 Table 1（§3 / Fig.1）

### 4.1 尺度一致增益（相对 RPJ / Nemotron-Synth）

| Scale | BeyondWeb Avg. | vs RPJ | vs Nemotron-Synth |
|---|---|---|---|
| **1B (1T)** | **57.4%** | **+6.7pp** | **+3.1pp** |
| **3B (180B)** | **60.8%** | **+7.3pp** | **+2.0pp** |
| **8B (180B)** | **63.7%** | **+7.1pp** | **+2.6pp** |

摘要另述：相对 Cosmopedia 最高 **+5.1pp**（14 基准均值口径）。

### 4.2 训练加速（8B，Fig.1 Right）

| 对照 | BeyondWeb 追平其 180B 精度所需 token | 加速 |
|---|---|---|
| RedPajama | **23.2B** | **7.7×** |
| Nemotron-Synth | **66.2B** | **2.7×** |

### 4.3 跨参数 Pareto

- **3B BeyondWeb（60.8%）** 在同 token 预算（180B）下超过 **几乎所有** 8B 基线（Fig.1 / 文述「all but one 8B baseline」；相对 Cosmopedia 8B 明确更强）。
- Table 1：BeyondWeb 在 1B/3B/8B 上分别于 **13 / 12 / 13** of **14** 任务取最高（或并列语境下领先多数）。

**Table 1 摘要 Avg.（0+5-shot 均值；完整分任务见 PDF）：**

| Scale | RPJ | QA WRAP | Cosmopedia | Nemotron-Synth | **BeyondWeb** |
|---|---|---|---|---|---|
| 1B | 50.7 | 52.5 | 52.2 | 54.3 | **57.4** |
| 3B | 53.5 | 55.3 | 55.8 | 58.8 | **60.8** |
| 8B | 56.6 | 58.4 | 58.6 | 61.1 | **63.7** |

---

## 五、系统消融：七问（§4）——本卡思想主货

消融默认（§4.1，除非另述）：Llama-3.2-**1B**；总 **20B** token；**50:50** 真实 HQ Web : 合成；合成改写同一 **10B** HQ 种子（RPJ 上 DatologyAI HQ 切分）；RPJ-HQ 基线对同 10B **见两遍**以控「新知识量」。评测同 14 任务 0+5-shot 均值。

### 5.1 RQ1 — 生成器驱动 ≈ 摘要？（§4.2）

| 条件 | Avg. | 读法 |
|---|---|---|
| RPJ-HQ（无合成） | **45.5%** | 基线 |
| Summarization（8B 简单摘要 prompt） | **≈46.7–46.8%** | 抬信息密度 |
| Cosmopedia（8×7B + 主题种子） | **≈47.1%**（Fig.2 黄线文述 46.8%/47.1% 邻近） | 昂贵生成器驱动 |
| **BeyondWeb** | **50.4%** | 显著超摘要 |

**Takeaway：** 简单 source-rephrasing 摘要即可接近 Cosmopedia → 大量收益来自 **per-token 信息密度**；BeyondWeb **+3.7pp** over 摘要 → **不止蒸馏**。

### 5.2 RQ2 — 能否打破 data wall？（§4.3）

受控三语料（均 20B）：

| 语料 | 构造 | Avg. |
|---|---|---|
| Full Data（上界） | 两半真实各 10B | **46.2%** |
| 2× Repeat（下界） | 仅前半 10B 真实重复两次 | **45.5%** |
| Continuation（朴素合成） | 后半真实 + 同风格续写 10B | **46.2%**（≈上界） |
| **BeyondWeb** | 策略改写 | **50.4%**（**超上界 +4.2pp**） |

**Takeaway：** 朴素续写几乎打不破墙；**有设计的合成**可超过「全真实」。

### 5.3 RQ3 — 种子质量？（§4.4）

| 组合 | Avg. |
|---|---|
| LQ Web + HQ Web | **45.6%** |
| LQ Synth + HQ Web | **48.6%** |
| HQ Synth + HQ Web | **49.2%** |
| BeyondWeb | **50.4%** |

**Takeaway：** 有限 HQ 时，**优先用 HQ 做改写种子**（质量 > 单纯追求知识新颖）；但 **仅 HQ 种子仍不够** 达到最优。

### 5.4 RQ4 — 分布风格对齐？（§4.5）

- GPT-4o 在 RPJ 样本上标会话性 ≈ **2.7%**；Organize the Web 四类会话风格自然占比 **3.67%**。
- 上采样会话至 10% / 20% / 50%（其余随机 RPJ；总 20B；本RQ只报 **5-shot**）：基线 **43.2%** → 50% 会话 **44.1%**；增益在 **>20%** 后饱和。

**Takeaway：** 风格匹配 **有用但不充分**。

### 5.5 RQ5 — 规模上的多样性？（§4.6 / Fig.7）

长训动态（1B→1T；3B/8B→180B）：

- 单策略（如固定教科书风 Cosmopedia、偏 QA 的 WRAP）早期有增益，随后 **平台期**。
- **BeyondWeb** 多样策略：各尺度上相对 RPJ 的增益曲线 **持续上扬**；1B 约 **50×** Chinchilla-optimal 过训时，他法开始过拟合下滑，BeyondWeb 仍改善。

**Takeaway：** 万亿预算下 **多样性是抗饱和关键**。

### 5.6 RQ6 — 改写器族？（§4.7）

同 prompt、各生成 **10B** 合成 + **10B** web → 训 1B：

| 改写器 | 自身基准（文内） | 合成数据训出模型 |
|---|---|---|
| OLMo-2-7B | 59.6% | **49.9%**（最高） |
| Phi-4-14B | 66.6% | 49.5% |
| Llama-3.1-8B | 61.2% | 49.2% |
| Mistral-7B-v0.3 | 66.0% | 48.9% |
| RPJ 基线 | — | 45.5% |

改写器自身基准跨约 **7pp**，下游合成质量差 **<1pp**；**无正相关**。

**Takeaway：** 改写是相对泛化能力；**选「够用」易、选「最优」难**。

### 5.7 RQ7 — 改写器规模？（§4.8）

Llama-3 系 1B / 3B / 8B 做改写器：

| 改写器 | 下游 Avg. | Δ vs RPJ 45.5% |
|---|---|---|
| 1B | 47.3% | +1.8pp |
| 3B | 48.8% | +3.3pp |
| 8B | 49.2% | +3.7pp |

**1B→3B** 跳 **+1.5pp**；**3B→8B** 仅 **+0.4pp** → **约 3B 饱和**。

**Takeaway：** 有效合成预训练数据 **不必** 依赖超大改写器（在本文设定下）。

### 5.8 原则汇总（§6）

文末三条（联合才够，单因子常只温和收益）：

1. **质量优先于新颖**：改写 HQ，而非堆 LQ。
2. **训练风格对齐部署用例**。
3. **保持生成多样性** 以支撑长训。

并强调：**无银弹**；朴素合成可能贵而无功，精细联合优化可 transformative（BeyondWeb 例证）。

---

## 六、Infra 附注与未来方向（§3 Infra / §5）

### 6.1 生成基建（产品化一句）

- 初：Slurm + AWS Hyperpod **H100**。
- 现： **Ray + vLLM on Kubernetes**（异构 GPU；接入既有 Ray/Spark 策展；端到端实验追踪）。
- 文称将另文详述生成 Infra；**本笔记不展开未给出的规模数字**。

### 6.2 Future（仅列文内方向，不外推）

- 合成数据特有的 scaling laws / **内在重复**度量。
- 进一步 **缩小** 改写器。
- 预训练期对齐人类价值（相对 post-hoc）。
- 扩展至非网页 / 多模态 / 专有域（改写器无需域专家）。

---

## 七、与仓库他卡的接口（只钉钉子）

| 卡 | 接口一句 | 禁止 |
|---|---|---|
| **[[NemotronCC数据策展]]** | Nemotron-Synth = 其 HQ 合成子集；作本卡最强公开合成基线 | 复述 CC→6.3T 管线 |
| **B3** | BeyondWeb 种子 ⊂ DCLM HQ（DatologyAI 选） | FineWeb/DCLM 过滤通史 |
| **B8** | Cosmopedia / Phi 为 generator-driven 对照；§4.2 用摘要逼近 | 教科书合成通史 |
| **[[合成对齐数据Magpie]]** | 同属「合成数据」词，但阶段=对齐 | Magpie/ActiveUF 流水线 |
| **[[规模定律与预训练范式]]** | 本卡动的是 **数据质量/形态轴**，非 $N$–$D$ 公式 | 重写 Kaplan/Chinchilla |

---

## 八、局限与笔记诚实边界

1. **BeyondWeb 具体 prompt/策略配方未在 PDF 公开** → 可复述原则与消融，**不可编造**「官方模板」。
2. 主对照混合为 **60/40** RPJ:synth；消融为 **50/50** HQ:synth——读表时勿混口径。
3. Cosmopedia 不足 token **靠重复**；作者自承生成器范式局限。
4. Continuation 实验存在混淆：续写模型见过远超 20B 的语料，可能注入参数知识（文内自陈）。
5. AFM4.5B / 7T 为 **生产叙事引用**，完整配比不在本 PDF → 不写细账。
6. 评测为 14 任务相对打分均值，**非**全面 Open LLM Leaderboard / 聊天 Arena 主张。

---

## 九、可引用金句（意译压缩，核对原文）

1. 「没有生成高质量合成预训练数据的银弹；最佳结果需要联合优化众多因素。」（摘要 / §6）
2. 「简单摘要可接近 Cosmopedia；BeyondWeb 再显著超过摘要——合成不止是知识蒸馏。」（§4.2）
3. 「朴素续写难破 data wall；有设计的合成可超过全真实上界。」（§4.3）
4. 「万亿预算下，多样性使收益可持续；单策略易饱和。」（§4.6）
5. 「改写器族稳健、自身基准不预测合成质量；规模约 3B 后收益递减。」（§4.7–4.8）

---

## 十、来源与抽取

- 主 PDF：`https://arxiv.org/abs/2508.10975`（2026-09-22 CST 自 arXiv 拉取）
- 元数据：` -meta`；页眉 v2 **19 Aug 2025**；XMP MetadataDate → **2025-08-21 08:04 CST**
- 辅链仅作入口，数字以本 PDF 为准。
