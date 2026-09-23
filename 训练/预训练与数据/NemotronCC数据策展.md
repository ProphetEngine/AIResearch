---
title: "数据策展流水线增量：Nemotron-CC"
topic: NemotronCC数据策展
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2412.02595
 - https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html
 - https://developer.nvidia.com/blog/announcing-nemotron-cc-a-trillion-token-english-language-dataset-for-llm-pretraining/
arxiv: ["2412.02595"]
related: ["B3", "B8", "合成对齐数据Magpie", "AXK2技术报告深读"]
project:
 - https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html
 - https://github.com/NVIDIA/NeMo-Curator
 - https://huggingface.co/nvidia/nemocurator-fineweb-nemotron-4-edu-classifier
 - https://huggingface.co/nvidia/nemocurator-fineweb-mixtral-edu-classifier
archived: 2026-09-22
---

# 数据策展流水线增量：Nemotron-CC

> **定位**：数据策展主题 **P1 数据侧横切**——相对 **B3**（FineWeb / DCLM / Dolma 网页策展通史）的 **下一站管线**：NVIDIA *Nemotron-CC* 如何把英文 Common Crawl 做成 **长程预训练**（~15T token 预算）仍可用的高质量语料。
> **攻坚线**：**架构思想 / 管线字段（主）** + **文内下游评测字段（辅）**（8B×1T 对开源 CC 数据集；8B×15T 对 Llama 3.1 8B）。
> **硬划界（禁止重写）**：
> - **≠ B3**：不写 FineWeb / DCLM / Dolma **全文通史**（抽取—启发式—模型过滤骨架只作一句对照；本篇只记 Nemotron-CC **增量**）。
> - **≠ B8**：不写 phi / Textbooks Are All You Need 式 **教科书/代码合成预训练** 主文；本文合成是 **对已有网页的改写/蒸馏/QA**，不是从知识库造新教材。
> - **≠ 数据源引用**：Ax-K2 等只把 Nemotron-CC **当数据源点名**；本篇才是管线主锚。
> - **≠ [[合成对齐数据Magpie]]**：Magpie / ActiveUF 是 **对齐侧**指令/偏好合成；本篇是 **预训练侧** CC 策展 + 合成改写。
> **禁止编造**：数字、表号、快照区间一律取自官方 PDF（2026-09-22 CST）、CC 索引页与 NVIDIA 博文（辅）；不外推未核对比。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 页数 / 版本 | 角色 |
|---|---|---|---|---|
| **主文** | Su, Kong, Lin, Jennings, Norick, Kliegl, Patwary, Shoeybi, Catanzaro (NVIDIA), *Nemotron-CC: Transforming Common Crawl into a Refined Long-Horizon Pretraining Dataset* | arXiv:**2412.02595v2** \[cs.CL\]；published **2024-12-03**，updated **2025-05-30**；comment **ACL 2025**；`https://arxiv.org/abs/2412.02595` | **17** 页（，2026-09-22 CST） | 长程 CC 策展方法 + 8B 实验主锚 |
| **发布索引** | Common Crawl contrib | https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html | — | 分区、路径、Hive key、jsonl 字段 |
| **叙事辅** | NVIDIA Developer Blog, *Announcing Nemotron-CC…*（2025-01-09） | 上表 URL | — | 与摘要一致的对外叙事；不另立主张 |

**开源（论文自报）：** 数据集 CC Terms of Use；参考实现并入 **NeMo Curator**（Apache 2.0）；质量分类器 HF：`nemocurator-fineweb-nemotron-4-edu-classifier`、`nemocurator-fineweb-mixtral-edu-classifier`。

**一句话增量（相对 B3 已读 FineWeb-Edu / DCLM）：**

| 轴 | B3 已立（仅对照） | 本篇增量 |
|---|---|---|
| **过滤哲学** | 强模型打分 → 大幅砍量、抬短程精度 | **分类器集成抬 HQ 召回** + **HQ 上关启发式** → 量质双保 |
| **重复与长程** | DCLM / FineWeb-Edu 文内约 **80%** near-dup；长程会反复见同一样本 | **全局模糊去重** → **4.4T unique real**；合成再补 **1.9T** |
| **合成角色** | （B8 轴：教科书造内容） | **改写/蒸馏/抽知识/QA**——模型当「风格/结构变换器」，非知识库造新教材 |

`
Common Crawl (99 snaps)
 │
 ▼
Justext 抽取 → 英滤 → 全局 fuzzy + exact substring 去重
 │
 ▼
三分类器打分 → max 集成 → 0–19 bucket → 退火映射 5 档 quality
 │
 ├─ High：启发式 OFF；合成（Diverse QA / Distill / Extract / Knowledge list / Wiki 改写）
 ├─ Medium*：启发式 ON；无合成（资源约束）
 └─ Low：启发式 ON；Wiki-style 改写
 │
 ▼
Nemotron-CC 6.3T（4.4T real unique + 1.9T synthetic）
 或 HQ 子集 1.1T（短程对照）
`

---

## 二、问题立轴：短程砍量 vs 长程 unique token

§1 / 摘要诊断（意译压缩，非 FineWeb/DCLM 通史）：

1. **爬取语料两用途**：高质量内容 + **多样性**；近年英文 CC 集（FineWeb-Edu、DCLM）用 **model-based filter** 抬基准，但约删 **90%**，短程好看、长程（Llama 3.1 的 **15T**、Gemma 2 27B 的 **13T**）吃紧。
2. **重复陷阱**：文称 FineWeb-Edu / DCLM 约含 **80%** near-duplicates（unique 约 **0.2T / 1T**）；多万亿训练等于反复见同一样本；Muennighoff et al. (2024) 指约 **4 epoch** 后相对更多 unique token 收益递减。
3. **本文主张**：用 **分类器集成 + 合成改写 + 减少对启发式依赖**，在 **准确率 ↔ 数据量（以 unique real token 计）** 上取得更好折中；指导原则是从「静态非学习启发式管线」转向 **learned flywheel**（更好数据 → 更好 LLM → 更好合成与分类）。

本篇只立这条 **预训练网页策展增量**；tokenizer/配比通史见 B3，教科书合成见 B8，对齐合成见 [[合成对齐数据Magpie]]。

---

## 三、管线增量（§2）——架构思想主线

### 3.1 HTML 抽取与启发式：Justext +「HQ 不滤」（§2.1，Table 1 / 7）

| 设计点 | 文内做法 | 跟读抓手 |
|---|---|---|
| **抽取器** | 对比 Trafilatura vs Justext；选定 Justext（质感相当，**token 与 HQ 产量更高**） | Table 1（去重后，B tokens）：Trafilatura-filtered 994 / HQ 80；Justext-filtered 1,380 / HQ 104（**+28.6%** HQ）；Justext **未滤** 1,804 / HQ 127（相对 Trafilatura-filtered **+57.4%** HQ） |
| **英滤** | pycld2 + FastText lid176，阈值 **0.3** | 标准语言门 |
| **去重** | **全局** fuzzy（NeMo Curator）+ exact substring（对快照八分之一；Lee et al. 2022；`deduplicate-text-datasets`） | 相对「分片近似去重」抬 unique real |
| **启发式** | 复访 Parmar et al. (2024) 管线（Raffel/Rae 启发式 + KenLM perplexity）；FineWeb-Edu 分类器显示该滤会再砍约 **18.1%** HQ | **主张：对模型判为 HQ 的文档关闭启发式**；启发式只打在低质 split |

**8B×1T 消融（Table 7，HQ 由 FineWeb-Edu score∈{3,4,5} 定义；本消融不用最终三分类器）：**

| Exp | MMLU | Avg (non-MMLU) |
|---|---|---|
| Trafilatura filtered | 55.4 | 60.6 |
| Justext filtered | 54.1 | 60.9 |
| Justext unfiltered | 55.5 | 60.3 |
| **Justext HQ-unfiltered**（仅 LQ 过启发式） | **57.5** | 60.6 |

→ 产量动机 + 下游：**只对 HQ 关启发式** 时 MMLU **+2**（相对 Justext unfiltered）。

### 3.2 模型质量标注：三分类器 max 集成 → 5 档（§2.2，Table 2 / 8 / 9）

**动机：** 单分类器 HQ 召回约 **10%**（Table 9）；标签未必对齐下游。

**三分类器：**

| 分类器 | 训练/来源（文内） | 偏好 |
|---|---|---|
| **Ours-mistral** | 同 FineWeb-Edu-Annotation 的 **460K** 文档；**Mistral 8×22B-instruct** 按教育价值 0–5 打分；在 Snowflake-arctic-embed-m 上训线性回归（embed/encoder 冻结，20 epoch，lr 3e-4，按 held-out F1 选 ckpt） | 教育向 |
| **Ours-nemotron-340B** | 同上，标注教师换 **Nemotron-340B-instruct** | 教育向（另一教师） |
| **DCLM** | Li et al. 公开 fastText；指令格式数据 + ELI5 高分帖 | 信息量 / instructional |

> **许可注（脚注 18）：** 最终集成 **未用** FineWeb-Edu 官方分类器（Llama3 标注许可问题）；FineWeb-Edu 只用于 Table 1/7 等分析。

**打分与分桶：**

1. 三分类器各自输出 → 按分位取整到整数桶 **0–19**（每桶约 **5%** 文档）。
2. 文档最终分 = 三桶号的 **max**（抬召回，分布变偏）。
3. **退火标定下游质量**：对已训 **70%** 的 8B，用 **50B** token 续训；**66%** 默认 mix + **34%** 待测桶；按 **9** 任务均值把 20 桶并成 **5** 档（Table 2）：

| Quality Label | Buckets | # Tokens (B) | Token (%) |
|---|---|---|---|
| High | 19 | 553 | 12.63 |
| Medium-High | 18 | 504 | 11.52 |
| Medium | 12–17 | 2,023 | 46.24 |
| Medium-Low | 7–11 | 894 | 20.43 |
| Low | 0–6 | 402 | 9.18 |

**重叠与集成下游（Table 8 / 9，13 快照子集）：** FineWeb-Edu-only HQ **35.4%**、DCLM-only **54.4%**、交集仅 **10.1%** → 集成抬多样性。集成后 HQ 文档占比 **25%**（单分类器约 8–14%），平均任务分 **59.4**（不低于 FineWeb-Edu 的 59.0 / DCLM 的 58.4）。

### 3.3 合成数据：低质改写 vs 高质多样化（§2.3，Table 3）——≠ B8

文明确对照：不像 Wang/Eldan/Gunasekar 等 **造新内容**（教科书、短故事），而是 **把给定文本改成另一风格**；可用更轻模型（Maini et al. 2024 Wikipedia-style）。**中档未做合成**（时间/资源）。

| 源 | #Raw (B) | Prompt | #Synthetic (B) |
|---|---|---|---|
| Low | 403.0 | Wikipedia-style | 336.3 |
| High | 451.3 | Wikipedia | 372.9 |
| | | Diverse QA pairs | 499.5 |
| | | Distill | 157.6 |
| | | Extract knowledge | 303.6 |
| | | Knowledge list | 203.2 |

生成器：**Mistral NeMo 12B Instruct**，FP8，top-p **0.9**，T=**0.5**；TensorRT-LLM + NeMo-Skills。文档切段（完整行、长度上限：Wiki **512** / Distill **2000** / Extract **1400** / QA&List **1000**，含 prompt）。后处理：去不完整、去 Markdown 星号、剥「Here is a paraphrased…」等前缀、去整段引号、滤短于 50 token；Wiki 段回拼同文档；Diverse QA 打乱后按段长保留对数并 **追加到段末**。

**合成消融（Table 10，8B×1T）：** LQ 改写相对 LQ-Base：Avg **52.5→54.0**（+1.5）；HQ 用合成替换 8 次重复中的 4 次：Avg **55.8→56.7**。文承认部分任务微降，可能引入误信息；未做事实校验（§6 Limitations）。

### 3.4 合成总装与规模（§2.4，Table 4）

对 **99** 个快照 **CC-MAIN-2013-20 … CC-MAIN-2024-30**：

| Dataset | Total (T) | Unique real (T) | Synthetic (T) |
|---|---|---|---|
| FineWebEdu-2 | 5.4 | 1.1 | — |
| FineWebEdu | 1.3 | 0.2 | — |
| DCLM | 3.8 | 1.0 | — |
| **Nemotron-CC** | **6.3** | **4.4** | **1.9** |
| **Nemotron-CC-HQ** | **1.1** | **0.6** | **0.5** |

HQ 子集 = 最高分 **真实** + **Diverse QA** 合成（短程公平对照用）。全文称合成「over 1.8T」与 Table 3 合计一致量级；摘要/Table 4 统一报 **1.9T**。

---

## 四、发布物与 Hive 分区（CC 索引，辅）

| 项 | 内容（索引页） |
|---|---|
| 格式 | `.jsonl.zstd`；约 **10.4 TiB**；**31,279** objects；parquet「coming soon」 |
| Hive keys | `quality` ∈ {high, medium-high, medium, medium-low, low}；`kind` ∈ {actual, synthetic}；`kind2` ∈ {actual, distill, diverse_qa_pairs, extract_knowledge, knowledge_list, wrap_medium} |
| 存在组合 | high 下 actual + 五种 synthetic；medium-* 仅 actual；**low** 有 actual + `wrap_medium` synthetic |
| jsonl 字段 | `text`, `language`（现恒 `"eng"`）, `warc_record_id`, `url` |

→ 社区可按 **质量档 × 真实/合成类型** 做短/长程课程实验（§5 Conclusion）。

---

## 五、评测字段（辅）

### 5.1 设定（§3.1）

- **模型：** Megatron-LM **8B**（32L / d=4096 / 32 heads / GQA 8 groups / SwiGLU；Adam β=(0.9,0.95)；cosine peak 3e-4 → 3e-6；约 **40h × 1024 H100** / 1T run，App.D）。
- **短程配比：** **73%** 英文 CC（被测数据集变）+ **27%** 固定 code/papers/books/patents/Wikipedia（Adler et al. Nemotron-4；Table 12）。
- **评测：** LM Evaluation Harness；十任务：ARC-E/C、Hellaswag、Winogrande、RACE、PIQA、SIQA、CSQA、OBQA、MMLU。

### 5.2 短程 1T（Table 5）——对开源 CC 集

| Dataset | MMLU | Avg |
|---|---|---|
| FineWebEdu-2 | 42.4 | 53.2 |
| FineWebEdu | 42.9 | 53.2 |
| DCLM | 53.4 | 57.0 |
| Nemotron-CC（全量） | 53.0 | 57.8 |
| **Nemotron-CC-HQ** | **59.0** | **60.1** |

→ HQ 相对 DCLM：**MMLU +5.6**、Avg **+3.1**；全量与 DCLM MMLU 持平量级，但 unique real **约 4×**。

### 5.3 长程 15T（Table 6 + App.E）

- 本数据集贡献约 **7.2T / 7.17T**（两阶段：前 **9T** 用 59% 英文 CC≈5.31T 的 med/med-high/high；后 **6T** 用 31%≈1.86T **仅 high**；课程细节指向 Feng et al. 2024 arXiv:2412.15285）。
- 自报 lm-eval 数字（可能与 Meta 公开数不同）：

| Model | ARC-C | MMLU | Avg |
|---|---|---|---|
| Llama 3.1 8B | 55.0 | 65.3 | 64.2 |
| Ours 8B | **58.1**（+3.1） | **70.3**（+5） | **64.7**（+0.5） |

---

## 六、限制与跟读注意（§6）

文内自报（勿扩写为已解决）：

1. 集成/分桶只试了一种策略；高质端灵敏度可再调。
2. **改写未做事实忠实度校验**；幻觉 / 多样性损失风险未系统消解；中档未改写。
3. 管线未全消融（如语言识别）。
4. **仅英文**。
5. **未去污染**；对照集与 Llama 3.1 亦常未去污；污染影响在不同规模/地平线上仍开放（回指 DCLM §4.6）。

博文（2025-01-09）数字与摘要一致（6.3T / 1.9T 合成 / HQ +5.6 MMLU / 15T 对 Llama 3.1），并强调 NeMo Curator 抽取—清洗—英滤—去重—分类/困惑度；**主张以论文表为准**。

---

## 七、与相邻笔记接口（只点名，不重写）

| 笔记 | 接口一句 |
|---|---|
| **B3** | FineWeb / DCLM / Dolma / SentencePiece **通史**已入库；本篇只记 Nemotron-CC 对「砍量换分」的 **长程修正** |
| **B8** | Textbooks / Self-Instruct 是 **造教材/指令**；本篇合成是 **网页改写与结构变换** |
| **[[合成对齐数据Magpie]]** | Magpie / ActiveUF = 对齐数据；并行数据侧，非本篇 |
| **数据源引用** | 若点名 Nemotron-CC 为训练源，回指本卡管线 |
| **污染检测** | 污染检测横切；本数据集作者 **未** decontaminate |

---

## 八、可跟读清单（中文）

1. **先立矛盾**：短程要狠滤，长程要 unique——Nemotron-CC 用「集成抬召回 + HQ 关启发式 + 改写补新鲜 token」同时打两头。
2. **跟 Table 1→7**：Justext 多产 HQ；**只对 HQ 关启发式** 不伤分还抬 MMLU。
3. **跟 Table 8→9→2**：分类器偏好几乎不重叠 → max 集成；再用退火把 20 桶收成 5 档训练课表。
4. **跟 Table 3→10**：Low=去噪 Wiki 改写；High=QA/蒸馏/抽知识——**不是** B8 教科书造内容。
5. **跟 Table 4→5→6**：全量 6.3T（4.4+1.9）对标 DCLM 短程持平、长程靠量；HQ 1.1T 专打短程 +5.6 MMLU；15T 课表里本集 ~7.2T 胜过 Llama 3.1 8B（同自报 harness）。
6. **划界自检**：写到 FineWeb/DCLM 方法细节就停，回 B3；写到 phi 教科书就停，回 B8。

---

## 九、来源与核验

| 主张 | 出处 |
|---|---|
| 6.3T = 4.4T unique real + 1.9T synthetic；HQ 1.1T | 摘要；Table 4；§2.4 |
| HQ vs DCLM MMLU 59.0 vs 53.4（+5.6） | 摘要；Figure 1；Table 5 |
| 15T：MMLU 70.3 vs Llama 3.1 65.3；ARC-C +3.1；Avg +0.5 | 摘要；Table 6 |
| 99 snaps CC-MAIN-2013-20…2024-30 | §2.4；App.F；CC 索引 |
| 三分类器 + max 桶 + 5 档；HQ 关启发式 | §2.1–2.2；Table 2/7/9 |
| 合成 prompt 五类与 token 统计 | §2.3；Table 3；App.H Prompt 1–5 |
| 未用 FineWeb-Edu 分类器入最终集成（许可） | §2.2 脚注 18；App.G |
| CC 分区 kind2 / 10.4 TiB | CC contrib 索引页（2026-09-22 抓取） |
| NeMo Curator / 分类器 HF / 博文叙事 | 论文脚注 3–4；NVIDIA Blog 2025-01-09 |

**本地核验：** `https://arxiv.org/abs/2412.02595`（ 17 页）；arXiv API `2412.02595v2`（ACL 2025）。

## 相关笔记

- [[Inspect评测Harness|Inspect Eval Harness]]
- [[NemotronCC数据策展|Nemotron-CC]]

