---
topic: TR-Gemini-3-Pro
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# Gemini 3 Pro Model Card 专项深读卡

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：Google DeepMind, *Gemini 3 Pro Model Card*（**Model Release: November 2025**；**Last Updated: May 2026**）
> 官方 PDF：`https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf`（**10** 页 letter；Title: *Gemini 3 Pro Model Card (May 2026)*；Producer: Skia/PDF m150 Google Docs Renderer）
> 对照笔记：[[Gemini25技术报告深读]]（本地 2.5 技术报告）；旁及 [[开源与闭源前沿模型谱系]] / [[推理时扩展TestTimeScaling]] / [[多模态架构脉络]] / [[AI基础设施总览]]
> **禁止编造**：参数量、专家数、未写明的层图/训练规模一律标「未公开」；能力榜分仅写第 5 页表可读数字。

---

## 1. 元信息

| 字段 | 核实值（据官方 PDF） |
|---|---|
| 标题 | Gemini 3 Pro Model Card |
| 文档自我定位 | Model Cards「essential information… known limitations, mitigation approaches, and safety performance」；可随模型改进更新；DeepMind 站点有 model cards 清单 |
| 相对既往 model card | 正文写：本卡相对以往「includes **more essential information**」——尤其 training dataset、distribution、intended uses |
| Model Release | **November 2025** |
| Last Updated | **May 2026** |
| 页数 | **10**（letter 612×792 pts） |
| PDF 元数据 Title | Gemini 3 Pro Model Card (May 2026) |
| 本地路径 | `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` |
| 能力评测方法外链 | 正文：`deepmind.com/models/evals-methodology/gemini-3-pro`；页脚另写 `deepmind.google/models/evals-methodology/gemini-3-pro`（**同一路径、域名写法不同** → 见 §4 待核实） |
| Frontier Safety 外链 | 「Gemini 3 Pro Frontier Safety Framework Report」（本 PDF **未附**该报告正文） |
| FSF 版本 | 「latest Frontier Safety Framework (**September-2025**)」 |

**型号与族系（Model Information）：**

| 项 | 原文 |
|---|---|
| 定位 | 「next generation in the Gemini series」；「natively multimodal, reasoning models」；「Google’s **most advanced** model for complex tasks」 |
| Deep Think | 「now features **Deep Think mode**, an **optional** setting… enhance complex problem-solving performance **at time of inference**」 |
| 依赖关系 | 「**not** a modification or a fine-tune of a prior model」；后续 3 族型号「based on Gemini 3 Pro」 |
| 族内举例 | Gemini 3 Pro Image；Gemini 3 Flash；Gemini 3.1 Pro；Gemini 3.1 Flash Image；Gemini 3.1 Flash-Lite；Gemini 3.1 Flash Live；Gemini 3.5 Flash |
| 输入 | Text / images / audio / video；token context **up to 1M** |
| 输出 | Text；**64K** token output |
| Knowledge cutoff | **January 2025**（Intended Usage and Limitations） |

**一句话抓手：** 这是 **10 页产品/安全 Model Card**（非 2.5 那种 73 页技术报告）；公开了稀疏 MoE + 原生多模态骨架口号、数据类别、分发渠道、相对 2.5 Pro 的能力表与内部安全 Δ%，以及 FSF 各域「CCL not reached」——**仍无**总参/专家配置/训练 FLOPs。

---

## 2. 相对 Gemini 2.5 的增量对照

> 对照源：本卡原文 + 本地 [[Gemini25技术报告深读]]（Gemini 2.5 Technical Report）。只写两侧都可锚定或本卡显式相对 2.5 的句子。

### 2.1 产品 / 接口级

| 维度 | Gemini 2.5 Pro（技术报告笔记） | Gemini 3 Pro（本 Model Card） | 增量读法 |
|---|---|---|---|
| 文档形态 | 73 页技术报告（架构/Infra/评测展开） | **10** 页 Model Card（essential + 安全） | 3 Pro 公开技术深度**明显变浅**；能力细节外链到 evals-methodology |
| 输入上下文 | Table 1：**1M** | **up to 1M** | 窗口口径同级；本卡未写 2M |
| 输出长度 | **64K** | **64K** | 同 |
| Knowledge cutoff | January 2025 | **January 2025** | **未延长**（本卡明文） |
| Thinking / Deep Think | Dynamic Thinking + budget；Deep Think 为 I/O 后实验路径 | **Deep Think mode** 写成 3 Pro 的 **optional** inference 设定；安全/FSF 用 Deep Think 评测「consistent with」默认 3 Pro | Deep Think 从「实验路径」升为卡内正式可选模式；**budget 旋钮本卡未写** |
| 是否前代微调 | 2.5 报告写独立族训练叙事 | 明文「**not** a modification or fine-tune of a prior model」 | 代际独立训练主张（细节未给） |
| 族扩展 | 2.5 Pro / Flash 等 | 列出 Image / Flash / **3.1** / **3.5 Flash** 等多型号 | 3.x 产品树更宽；各型号细节「see each model card」 |

### 2.2 架构 / 数据 / Infra（AI Infra 辅线）

| 维度 | 2.5 技术报告（已记） | 3 Pro Model Card | 增量 / 缺口 |
|---|---|---|---|
| 骨干 | sparse **MoE** Transformer；native multimodal text/vision/audio | 同句式：**sparse mixture-of-experts (MoE)** transformer-based；native multimodal text/vision/audio；引用 Clark/Du/Fedus/Jiang/Lepikhin/Riquelme/Roller/Shazeer + Vaswani | 骨架口号**一致**；本卡加「Developments to the model architecture contribute to… improved performance」——**无具体改动名** |
| 参数 / 专家 | 未公开 | **仍未公开** | 无增量数字 |
| 预训练数据 | 多域多模态公开 web/代码/图像/音频/视频 | 同类列举 + 更细渠道：publicly downloadable；crawlers；**licensed**；**user data**（按 ToS/隐私/控件）；业务/员工数据；**AI-generated synthetic data** | Model Card 对数据来源类别写得更「合规清单」化；仍无 token 量/配比 |
| 后训练 | SFT → RM → RL；verifiable + generative rewards | 「instruction tuning… reinforcement learning data… human-preference」；「RL techniques that can leverage **multi-step reasoning, problem-solving and theorem-proving** data」 | 强调多步推理/证明类 RL 数据；无算法细节 |
| 过滤 | filtering + dedup（报告） | deduplication；**honoring robots.txt**；safety filtering；quality filtering；含 pornographic / violent / **CSAM** 过滤表述 | robots.txt / CSAM 在卡内写明 |
| 硬件 | **TPUv5p**；多 DC、多 8960-chip pods；Pathways 弹性/SDC 数字 | 仅「Google’s **TPUs**」；TPU Pods 可扩展叙述 | **退回概括**；无 v5p / pod 规模 / 时间账 |
| 软件 | JAX + Pathways（报告详） | **JAX and ML Pathways** | 同栈名；无弹性/SDC 段落 |

### 2.3 能力榜：3 Pro vs 2.5 Pro（第 5 页表，Results as of **November 2025**）

> 对照列尚有 Claude Sonnet 4.5、GPT-5.1。粗体为该行表内最优（读图）。SWE-Bench Verified 一行最优为 **Claude Sonnet 4.5（77.2%）**，非 3 Pro。

| Benchmark（设定摘自同表） | Gemini 3 Pro | Gemini 2.5 Pro | 相对 2.5 的可读 Δ |
|---|---:|---:|---|
| Humanity's Last Exam（No tools） | **37.5%** | 21.6% | +15.9 pp |
| HLE（With search and code execution） | **45.8%** | — | 仅 3 Pro 有工具条件分 |
| ARC-AGI-2（ARC Prize Verified） | **31.1%** | 4.9% | 大幅抬升 |
| GPQA Diamond（No tools） | **91.9%** | 86.4% | +5.5 pp |
| AIME 2025（No tools） | **95.0%** | 88.0% | +7.0 pp |
| AIME 2025（With code execution） | **100%** | — | 与 Claude Sonnet 4.5 同为 100%（表内） |
| MathArena Apex | **23.4%** | 0.5% | 大幅抬升 |
| MMMU-Pro | **81.0%** | 68.0% | +13.0 pp |
| ScreenSpot-Pro | **72.7%** | 11.4% | 屏理解跃迁 |
| CharXiv Reasoning | **81.4%** | 69.6% | +11.8 pp |
| OmniDocBench 1.5（edit distance，**lower better**） | **0.115** | 0.145 | 更好（更低） |
| Video-MMMU | **87.6%** | 83.6% | +4.0 pp |
| LiveCodeBench Pro（Elo，higher better） | **2,439** | 1,775 | +664 Elo |
| Terminal-Bench 2.0（Terminus-2 agent） | **54.2%** | 32.6% | +21.6 pp |
| SWE-Bench Verified（Single attempt） | 76.2% | 59.6% | +16.6 pp（仍略低于 Sonnet 4.5 **77.2%**） |
| τ2-bench（agentic tool use） | **85.4%** | 54.9% | +30.5 pp |
| Vending-Bench 2（Net worth mean，$） | **$5,478.16** | $573.64 | 长程 agent 净值量级跳变 |
| FACTS Benchmark Suite | **70.5%** | 63.4% | +7.1 pp |
| SimpleQA Verified | **72.1%** | 54.5% | +17.6 pp |
| MMMLU | **91.8%** | 89.5% | +2.3 pp |
| Global PIQA | **93.4%** | 91.5% | +1.9 pp |
| MRCR v2 8-needle 128k（average） | **77.0%** | 58.0% | +19.0 pp |
| MRCR v2 8-needle 1M（pointwise） | **26.3%** | 16.4% | +9.9 pp；Claude/GPT 表内为 not supported |

**正文总判（非分数）：** 「significantly outperforms Gemini 2.5 Pro across a range of benchmarks requiring enhanced reasoning and multimodal capabilities。」

### 2.4 内部安全自动评测 Δ（第 8 页表，vs Gemini 2.5 Pro）

| Evaluation | 相对 2.5 Pro | 颜色语义（原文） |
|---|---|---|
| Text to Text Safety | **-10.4%** | 回归（红）；人工复核称 flagged 多为 false positive 或 not egregious |
| Multilingual Safety | **+0.2% (non-egregious)** | 改进（绿） |
| Image to Text Safety | **+3.1% (non-egregious)** | 改进 |
| Tone | **+7.9%** | 改进（拒绝语气更「objective」） |
| Unjustified-refusals | **+3.7% (non-egregious)** | 改进（边界提示更敢答且安全） |

**方法注（原文硬约束）：**

1. 分数为相对指定对照的 **absolute percentage increase/decrease**；自动评测，非 human / red team。
2. 「Overall, Gemini 3 Pro outperforms Gemini 2.5 Pro across both **safety and tone**, while keeping unjustified refusals low」——与 Text-to-Text **-10.4%** 并存；作者用人工复核解释损失。
3. 「performance results reported below are computed with **improved evaluations** and thus are **not directly comparable** with… previous Gemini model cards。」
4. Deep Think 模式下安全评估「**consistent with** the original Gemini 3 Pro safety assessment」。

### 2.5 人类红队 / 风险（相对 2.5，第 9 页）

| 项 | 原文 |
|---|---|
| 儿童安全 | 「satisfied required launch thresholds」 |
| 内容安全总判 | 「similar or **improved** safety performance compared to Gemini 2.5 Pro」 |
| 范围 | 相对 2.5，「scope of red teaming was **expanded**… outside of our strict policies」；「found **no egregious** concerns」 |
| 主风险 | (a) **jailbreak** vulnerability——「improved compared to Gemini 2.5 Pro but still an open research problem」；(b) 「possible degradation in **multi-turn** conversations」 |

---

## 3. 能力 / 安全公开要点

### 3.1 架构思想（公开句，勿外推）

1. **稀疏 MoE + 原生多模态**：每 token 动态路由到专家子集，解耦总容量与 per-token 算力/serving 成本；输入含 text / vision / audio。
2. **推理期 Deep Think（可选）**：卡内将其定义为 inference-time 加强复杂解题的可选设定；与 2.5 报告中的 Dynamic Thinking / budget **本卡未做机制对照**。
3. **RL 后训练叙事**：可利用 multi-step reasoning / problem-solving / theorem-proving 数据——与能力表上 HLE / MathArena / agentic 项的「叙事对齐」，但**无**损失/奖励公式。
4. **非前代微调**：明确否定「modification or fine-tune of a prior model」。

### 3.2 分发与用途

**分发渠道：** Gemini App；Google Cloud / Vertex AI；Google AI Studio；Gemini API；Google AI Mode；**Google Antigravity**；族内部分型号还可经 Notebook LM。

**适合场景（原文 bullet）：** agentic performance；advanced coding；long context and/or multimodal understanding；algorithmic development。

**已知限制：** hallucinations；occasional slowness or timeout；cutoff January 2025。

**可接受使用：** 适用 Google Generative AI Prohibited Use Policy；并列举不应接入的系统类型（危险非法、破坏安全、性暴力仇恨有害、虚假误导等——原文四类）。

### 3.3 安全治理流程（Ethics and Content Safety）

评测类型：Training/Development Evaluations（自动+人工，训中/训后持续）；Human Red Teaming（独立专家队）；Automated Red Teaming（规模化）；Ethics & Safety Reviews（发布前）；并按 **FSF** 指南测试。

**Safety Policies 六类：** CSAM/剥削；Hate speech；Dangerous content；Harassment；Sexually explicit；与科学/医学共识相悖的 medical advice。

**缓解手段（非穷尽）：** dataset filtering；**conditional pre-training**；SFT；RL from human and critic feedback；safety policies and desiderata；product-level safety filtering。

### 3.4 Frontier Safety（第 9–10 页表）——均「CCL not reached」

| Domain | Key Results（摘要） | CCL | CCL reached? |
|---|---|---|---|
| CBRN | 信息偶有 actionable，但一般不足以显著增强 low–medium resource 威胁行为者 | Uplift Level 1 | **CCL not reached** |
| Cybersecurity | key skills：v1 hard **11/12** solved；v2 **0/13** end-to-end；「Alert threshold **met**」 | Uplift Level 1 | **CCL not reached** |
| Harmful Manipulation | 相对 non-generative AI baseline 操纵效力上升，但相对前代无显著 uplift；未达 alert | Level 1 (exploratory) | **CCL not reached** |
| Machine Learning R&D | 优于 Gemini 2.5（尤其 RE-Bench 的 Scaling Law Experiment 与 Optimize LLM Foundry）；聚合分仍「substantially below」alert | Acceleration level 1；Automation level 1 | **CCL not reached** |
| Misalignment (Exploratory) | situational awareness **3/11**；stealth **1/4** | Instrumental Reasoning Levels 1+2 | **CCL not reached** |

Deep Think 的 FSF 评测：「consistent with the original Gemini 3 Pro assessment」。细节见外链 *Gemini 3 Pro Frontier Safety Framework Report*（**本仓库 PDF 未收录**）。

### 3.5 与横比友商（第 5 页，仅表内）

- 多数推理/多模态/长上下文行：**Gemini 3 Pro** 最优。
- **SWE-Bench Verified（single attempt）**：Sonnet 4.5 **77.2%** > GPT-5.1 76.3% > Gemini 3 Pro 76.2% > 2.5 Pro 59.6%。
- MRCR 1M：仅 Gemini 3/2.5 有分；Claude / GPT-5.1「not supported」。
- 脚手架差异未在本卡展开 → 跨卡硬比需回 evals-methodology（待核实）。

---

## 4. 待核实与引用

### 4.1 待核实

| # | 项 | 原因 |
|---|---|---|
| 1 | `deepmind.com` vs `deepmind.google` evals-methodology URL | 正文与页脚域名写法不一致；需浏览器确认最终落地页 |
| 2 | 第 5 页全部榜分的官方可复制表 | 主表为图；本卡数字来自 `pdftoppm` 读图；建议与 evals-methodology 页交叉 |
| 3 | *Gemini 3 Pro Frontier Safety Framework Report* | 本卡仅引用标题；本地  **未见**该 PDF |
| 4 | Deep Think 算法 / 与 Thinking budget 关系 | 本卡仅「optional setting」；2.5 报告 Deep Think 细节亦外链 Doshi 2025b——机制仍缺 |
| 5 | 「architecture developments」具体是什么 | 仅有贡献声明，无层/路由/注意力改动名 |
| 6 | TPU 代数与集群规模 | 本卡只写 TPUs；2.5 报告的 TPUv5p / 8960-chip pods **不能**自动继承到 3 Pro |
| 7 | Cyber「Alert threshold met」但「CCL not reached」的阈值含义 | 需 FSF（Sep-2025）原文定义 alert vs CCL |
| 8 | Google Antigravity 产品形态 | 仅出现在分发列表；本卡无解释 |
| 9 | 与 2.5 技术报告 Table 3 同名榜的口径差 | 例：2.5 笔记 SWE-bench Verified **67.2%（multiple attempts）** vs 本卡 2.5 Pro **59.6%（single attempt）**——**不可无脚注合并** |
| 10 | CharXiv 拼写 | 读图为 CharXiv Reasoning；若官方页写 ChartXiv 需再核 |

### 4.2 主要引用（本地可核对）

| 类型 | 路径 / 标识 |
|---|---|
| 主 PDF | `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` |
| 2.5 对照 | `https://arxiv.org/abs/2507.06261`；笔记 [[Gemini25技术报告深读]] |
| 外链（卡内） | evals-methodology（上表域名待核）；Frontier Safety Framework Report；FSF September-2025 |

### 4.3 跟读回填建议（不写进事实栏）

- **[[开源与闭源前沿模型谱系]]**：Gemini 行代际加 **3 Pro（2025-11 发布 / 卡更新 2026-05）**；Dense/MoE 仍「稀疏 MoE，参数未公开」；Deep Think = 可选 inference 模式。
- **[[推理时扩展TestTimeScaling]]**：可记「3 Pro 卡确认 Deep Think 为产品旋钮」，但无 budget 曲线。
- **[[AI基础设施总览]]**：Infra 公开度低于 2.5 报告——勿把 v5p/SDC 数字迁移到 3 Pro。
- **[[多模态架构脉络]] / [[长上下文位置编码与系统侧]]**：多模态与 1M 长上下文仍在，ScreenSpot-Pro / MRCR 数字可作 3 vs 2.5 增量锚。

---

## 5. 摘要（给父代理 / 速览）

Gemini 3 Pro Model Card（发布 2025-11，更新 2026-05，**10** 页）把 3 Pro 定位为独立训练的稀疏 MoE 原生多模态推理旗舰，可选 **Deep Think**；上下文 **1M** / 输出 **64K** / cutoff **2025-01**（与 2.5 Pro 同截止）。相对 2.5 Pro，第 5 页表显示推理（HLE 37.5% vs 21.6%、ARC-AGI-2 31.1% vs 4.9%）、屏理解、agentic（τ2、Vending-Bench、Terminal-Bench）与长上下文（MRCR）全面抬升，SWE-Bench Verified single-attempt 76.2% 仍略低于表内 Sonnet 4.5。安全上内部 Text-to-Text 自动分相对 2.5 **-10.4%**（作者称多为非严重/假阳性），tone / 无理拒绝改进；FSF 各域均 **CCL not reached**（Cyber 达 alert 但未达 CCL）。架构与 Infra **无**参数量或 TPU 代际数字——技术深度弱于 2.5 技术报告，细节依赖外链报告。

## 相关笔记

### 技术报告专项
- [[GPT5SystemCard|TR GPT-5]]
- [[GPT51SystemCard附录|TR GPT-5.1 Addendum]]
- [[GPT52SystemCard更新|TR GPT-5.2 Update]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[Gemini3ProModelCard|TR Gemini 3 Pro Model Card]]
- [[ClaudeOpus41SystemCard|TR Claude Opus 4.1]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

