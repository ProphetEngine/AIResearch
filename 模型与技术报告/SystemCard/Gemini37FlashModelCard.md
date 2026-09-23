---
topic: Gemini37FlashModelCard
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# 5：Gemini 3.7 Flash Model Card 深读

> 攻坚线：**架构思想（产品 / 安全字段）**
> 锚点：Google DeepMind, *Gemini 3.7 Flash Model Card*（**Published: August 2026**；卡页写 **Published 13 August 2026**）
> 官方 PDF：`https://deepmind.google/models/model-cards/gemini-3-7-flash/`（**9** 页 A4；Title: *Gemini-3-7-Flash-Model-Card.pdf*；Producer: Skia/PDF m154 Google Docs Renderer）
> 卡页：https://deepmind.google/models/model-cards/gemini-3-7-flash/
> PDF URL：https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-7-Flash-Model-Card.pdf
> 对照笔记：模型与技术报告/厂商报告/Gemini25技术报告深读.md；模型与技术报告/SystemCard/Gemini3ProModelCard.md
> **只写增量**：相对 2.5 TR / 3 Pro Model Card 已入库面；本卡大量字段「see Gemini 3.6 Flash model card」——**本仓库未入库 3.6 Flash 卡**，不得把 3 Pro / 2.5 数字外推为 3.7 架构主张。
> **禁止编造**：参数量、专家数、未写明的层图/训练规模一律标「未公开 / defer 至 3.6」；能力榜分仅写第 5 页表 / 卡页可读数字。

---

## 1. 元信息与一句话抓手

| 字段 | 核实值（据官方 PDF / 卡页） |
|---|---|
| 标题 | Gemini 3.7 Flash Model Card |
| 文档自我定位 | Model Cards「essential information… known limitations, mitigation approaches, and safety performance」；可随模型改进更新 |
| Published | **August 2026**（PDF）；卡页 **13 August 2026** |
| 页数 | **9**（A4 596×842 pts） |
| 本地路径 | `https://deepmind.google/models/model-cards/gemini-3-7-flash/`（386,307 bytes） |
| 能力评测方法外链 | `deepmind.com/models/evals-methodology/gemini-3-7-flash`（卡页另有 `deepmind.google/...` 同源路径） |
| Frontier Safety 外链 | 「The Gemini 3.7 Frontier Safety Framework Report is available here.」（本 PDF **未附**报告正文；本库未另存该报告正文） |
| FSF 版本 | 「latest Frontier Safety Framework (**April-2026**)」 |
| 直接依赖 | 「**based on Gemini 3.6 Flash**」 |

**型号与族系（Model Information）：**

| 项 | 原文 |
|---|---|
| 定位 | 「next iteration in the Gemini 3 model family」；「algorithmic improvements to its **core reasoning foundation**」；「support for **agentic video understanding**」 |
| Thinking | 「**customizable thinking configurations** to control the mix of quality, cost and latency」 |
| 依赖关系 | 「based on Gemini 3.6 Flash」——Architecture / Training Dataset / Data Processing / Hardware / Software / Acceptable Usage / Safety Policies / Evaluation Approach **一律 defer 至 3.6 Flash 卡** |
| 输入 | Text / images / audio / video；token context **up to 1M** |
| 输出 | Text；**64K** token output |
| Knowledge cutoff | **March 2026**；并写：部分域可更新，另一些域可能仍限于 **January 2025**（「in line with the Gemini 3 Model Family」） |

**一句话抓手：** 这是 **9 页 Flash 线增量 Model Card**（非 2.5 那种 73 页技术报告）：相对 3.6 Flash 报能力/安全 Δ，产品口号落在 **推理地基算法改进 + agentic video + 可配置 thinking**；架构/数据/Infra **本卡无新数字**；FSF 升到 **April-2026**，并引入 **TCL** 与 CBRN/Cyber **alert** 表述。

---

## 2. 相对 Gemini 2.5 TR / 3 Pro Model Card 的增量对照

> 对照源：本卡原文 + 本地 模型与技术报告/厂商报告/Gemini25技术报告深读.md、模型与技术报告/SystemCard/Gemini3ProModelCard.md。只写两侧可锚定或本卡显式相对前代的句子。本卡对照列主轴是 **3.6 Flash**（未入库），故下表「相对 2.5 / 3 Pro」= 产品字段与安全框架差分，**不是**把 3.7 能力表硬并到 3 Pro 第 5 页同名榜。

### 2.1 产品 / 文档形态

| 维度 | Gemini 2.5（技术报告笔记） | Gemini 3 Pro（Model Card） | **Gemini 3.7 Flash（本卡）** | 增量读法 |
|---|---|---|---|---|
| 文档形态 | **73** 页技术报告 | **10** 页 Model Card（May 2026 更新） | **9** 页 Model Card（Aug 2026） | 继续「短卡 + evals-methodology 外链」形态；技术深度仍弱于 2.5 TR |
| 族定位 | 2.5 Pro / Flash；Flash = hybrid reasoning + **controllable thinking budget** | 3 族旗舰；可选 **Deep Think**；列出 3.x Image/Flash/3.1/3.5 等 | 「next iteration」；**based on 3.6 Flash** | Flash 线迭代卡；**非**「not a fine-tune of a prior model」式独立旗舰叙事（3 Pro 用语） |
| Thinking 旋钮 | Dynamic + **Thinking budget**（报告有 budget→精度曲线） | Deep Think = optional inference 设定；budget **未写** | **customizable thinking configurations**（quality / cost / latency） | 口号延续 2.5 Flash「可控 thinking」产品轴；**无** budget 数值表 / Deep Think 专名 |
| 输入 / 输出 | 1M / 64K（2.5 Pro/Flash） | 1M / 64K | **1M / 64K** | 窗口口径同级 |
| Knowledge cutoff | January 2025（2.5） | **January 2025** | **March 2026**（部分域仍可能停在 Jan 2025） | 相对 3 Pro / 2.5 **明文延长**；双截止口径需产品侧注意 |
| 架构公开 | sparse MoE + native multimodal（报告） | 同句式 +「architecture developments」无具体名 | **本卡无架构段实质内容**；全部「see 3.6 Flash」 | **禁止**把 3 Pro MoE 口号或 2.5 Infra 数字迁移为 3.7 主张 |
| 参数 / 专家 / FLOPs | 未公开 | 仍未公开 | **仍未公开**（且 defer 3.6） | 无增量数字 |

### 2.2 分发渠道（相对 3 Pro 卡）

| 渠道 | 3 Pro Model Card | 3.7 Flash 本卡 |
|---|---|---|
| Gemini App | ✓ | ✓ |
| Google Cloud / Vertex AI | ✓ | **未列此名** |
| Google AI Studio | ✓ | ✓ |
| Gemini API | ✓ | ✓ |
| Google AI Mode | ✓ | ✓ |
| Google Antigravity | ✓ | ✓ |
| Gemini Enterprise App | — | **新增列出** |
| Gemini Enterprise Agent Platform | — | **新增列出** |
| Notebook LM（族内部分型号） | 3 Pro 卡提及 | **本卡未列** |

→ 企业侧渠道命名更「Enterprise App / Agent Platform」化；Vertex AI 是否仍覆盖需外链文档（**本卡未写** → 待核实）。

### 2.3 用途 / 限制增量

| 项 | 3 Pro | 3.7 Flash |
|---|---|---|
| 适合场景 | agentic；advanced coding；long context / multimodal；algorithmic development | **agentic workflows, complex video reasoning, coding tasks, enterprise workflows** |
| 已知限制 | hallucinations；slowness/timeout；cutoff Jan 2025 | 同 + 「continually working to improve **jailbreak resistance**」+ 「recently strengthened… mitigations across **Frontier Safety**」；cutoff **Mar 2026**（双口径） |
| Acceptable Usage | 卡内展开 Prohibited Use 等 | **defer 至 3.6 Flash 卡** |

**产品字段增量一句话：** 相对 3 Pro，本卡把 Flash 线卖点钉在 **agentic video + 可配置 thinking + 企业工作流**；cutoff 名义升到 2026-03，但保留「部分域仍 2025-01」脚注。

---

## 3. 能力榜：相对 3.6 Flash（Results as of August 2026）

> **与 3 Pro 第 5 页表不可无脚注合并**：榜名集合不同（本卡无 HLE/ARC-AGI-2/AIME/SWE-Bench Verified/τ2/Vending 等；有 FrontierCode / DeepSWE / Terminal-bench 2.1·3.0 / AutomationBench / LVBench / HLE-**Verified** 等）。
> 粗体为该行表内最优（读图）。方法论：`evals-methodology/gemini-3-7-flash`（pass@1；默认 `gemini-3.7-flash` API；友商多为自报或公开榜）。

### 3.1 定价

| 项 | 3.7 Flash | 3.6 Flash | 注 |
|---|---:|---:|---|
| Input $/1M | **$0.75\*** | **$0.75\*** | 引入价至 **2026-12-31**；自 **2027-01-01** → **$1.50 / $7.50** |
| Output $/1M | **$3.75\*** | **$3.75\*** | 同上 |

相对表内 Sonnet 5（$2 / $10）、GPT-5.6 Terra（$2 / $12）仍明显更低（引入价期）。

### 3.2 主表摘录（3.7 vs 3.6 及可读胜负）

| Benchmark（设定摘自同表/方法页） | Gemini 3.7 Flash | Gemini 3.6 Flash | 相对 3.6 的可读 Δ | 表内备注 |
|---|---:|---:|---|---|
| Artificial Analysis Intelligence Index | 56 | 52 | +4 | 表内最优 57（GPT-5.6 Terra / Muse Spark 1.2） |
| FrontierCode 1.1 Main（Score） | **43.6%** | 34.4% | **+9.2 pp** | 表内最优 |
| DeepSWE v1.1 | 65.3% | 48.6% | **+16.7 pp** | 表内最优 GPT-5.6 Terra **69.6%** |
| Code Arena（Elo） | **1588** | 1538 | +50 Elo | 表内最优 |
| Terminal-bench 2.1 | 85.8% | 78.0% | +7.8 pp | 表内最优 GPT-5.6 Terra **87.4%** |
| Terminal-bench 3.0 | 14.9% | 5.4% | **+9.5 pp** | 表内最优 GPT-5.6 Terra **20.8%** |
| AutomationBench（Private set） | **30.4%** | 17.0% | **+13.4 pp** | 表内最优 |
| GDPVal-AA v2（Elo） | 1525 | 1422 | +103 Elo | 表内最优 Muse Spark 1.2 **1628** |
| Harvey LAB-AA | **90.7%** | 85.1% | +5.6 pp | 表内最优 |
| GDP.pdf | **34.0%** | 22.0% | **+12.0 pp** | 表内最优 |
| CharXiv Reasoning（No tools） | 84.5% | 85.2% | **−0.7 pp** | 表内最优 GPT-5.6 Terra **85.9%** |
| CharXiv Reasoning（With tools） | 88.7% | **89.4%** | **−0.7 pp** | 3.6 高于 3.7（表内该行最优） |
| LVBench | **85.4%** | 84.2% | +1.2 pp | 表内最优；方法页：Gemini/GPT 用 **1024** frames，Sonnet **300**（API 限） |
| GDM-MRCR v2（8-needle）128k average | **97.0%** | 91.8% | **+5.2 pp** | 表内最优 |
| OSWorld-2.0 | 47.9% | 33.8% | **+14.1 pp** | 表内最优 GPT-5.6 Terra **50.2%**；Sonnet「—」 |
| Agent's Last Exam（Pass rate） | 26.3% | 24.2% | +2.1 pp | 表内最优 Sonnet 5 **33.3%** |
| HLE-Verified | **53.6%** | 51.2% | +2.4 pp | 表内最优；方法页：全 1,811 verified 集 |
| BioMysteryBench（Human solvable） | 87.1% | 80.6% | +6.5 pp | 表内最优 Sonnet 5 **87.5%** |
| BioMysteryBench（Human difficult） | 43.5% | 41.2% | +2.3 pp | 表内最优 GPT-5.6 Terra **49.4%** |
| LABBench2 | **82.1%** | 76.1% | +6.0 pp | 表内最优 |

**能力总判（非分数，据 Δ 形态）：** 相对 3.6 Flash，增量集中在 **长程软件工程 / 终端 agent / 企业自动化 / PDF 理解 / 计算机使用 / 长上下文 MRCR**；**CharXiv** 两条相对 3.6 **略降**（表内如实）。相对表内友商：编码/agent 多项仍被 GPT-5.6 Terra 压一头（DeepSWE、Terminal-bench、OSWorld）；综合价效与若干文档/法律/视频项本卡列最优。

### 3.3 与已入库 3 Pro / 2.5 能力叙事的「可交叉、不可硬并」点

| 主题 | 已入库锚 | 本卡可交叉句 | 硬并禁令 |
|---|---|---|---|
| 长上下文 | 3 Pro MRCR v2 8-needle 128k **77.0%**（vs 2.5 Pro 58.0%） | 本卡 **GDM-MRCR v2** 128k **97.0%**（vs 3.6 91.8%） | 名称/脚手架/「GDM-」前缀不同 → **不可**直接当 3.7>3 Pro |
| 视频 | 2.5 / 3 Pro：Video-MMMU 等 | 本卡强调 **agentic video** + **LVBench 85.4%** | 榜不同；帧数设定见方法页 |
| Thinking | 2.5 budget；3 Pro Deep Think | 「customizable thinking configurations」 | 无机制/曲线 |
| 推理旗舰分 | 3 Pro HLE 37.5%（no tools）等 | 本卡 **HLE-Verified 53.6%** | **Verified 集 ≠ 原 HLE**（方法页显式） |

---

## 4. 安全与 Frontier Safety 增量

### 4.1 内部自动安全评测（vs Gemini 3.6 Flash）

> 绝对百分比点（pp）增减；自动评测非 human/red team。原文总判：「performs **similarly** to Gemini 3.6 Flash across both safety and tone, with low unjustified refusals。」
> 脚注：Tone / instruction following 的「正 Δ = 改进」对照基准写的是 **Gemini 3 Flash**（非 3.6）——与列标题「vs 3.6」并存，引用时勿混。
> 另有硬约束：「computed with **improved evaluations**… **not directly comparable** with… previous Gemini model cards。」

| Evaluation | 3.7 vs 3.6 | 方向语义（原文） |
|---|---|---|
| Text to Text Safety | **+1.17 pp** | Lower is better → 略回归 |
| Multilingual Safety | **−0.48 pp** | Lower is better → 略改进 |
| Image to Text Safety | **No change** | — |
| Tone | **−0.47 pp** | Higher is better → 略回归 |
| Unjustified-refusals | **+0.84 pp** | Lower is better → 略回归 |

人工复核：flagged 损失「overwhelmingly」为 false positives 或 not egregious。

**相对 3 Pro 卡（vs 2.5 Pro）的读法差异：** 3 Pro 曾报 Text-to-Text **−10.4%** 量级回归；本卡相对 3.6 的安全 Δ 在 **±1 pp 量级**，叙事为「similar」。**禁止**跨卡把百分比符号与 pp 混比。

### 4.2 人类红队

| 项 | 原文 |
|---|---|
| 儿童安全 | 「satisfied required launch thresholds」 |
| 内容安全总判 | 「similar or **improved**… compared to Gemini **3.6 Flash**」 |
| 范围 | 覆盖政策外议题；对照 **Gemini 3.1 Pro**；「found **no egregious** concerns」 |

### 4.3 Frontier Safety（April-2026）——相对 3 Pro（Sep-2025）框架差分

| Domain | Key Results（摘要） | T/CCL | reached? |
|---|---|---|---|
| CBRN | 可合理排除 **TCL**；理论能力高但缺可行动深度 | Uplift **TCL** | **TCL not reached** |
| CBRN | 专家红队有 modest uplift；**达 alert**；因平均分 modest + 需 explicit expert steering → 判低于 CCL | Uplift Level 1 **CCL** | **CCL not reached**（**alert 已达**） |
| Cybersecurity | **达 alert**，未达 CCL；继续部署缓解 | Uplift Level 1 CCL | **CCL not reached** |
| Harmful Manipulation | 一对一对话有一定影响；整体低于 **CCL alert** | Level 1 CCL | **CCL not reached** |
| ML R&D and Misalignment | Stealth ≈ 3.1 Pro；situational awareness **强于** 3.1 Pro；能识别测试环境但无法绕过限制 | Stealth and Situational Awareness **TCL** | **TCL not reached** |
| （同上） | 能完成单任务编码，缺独立串联端到端研究工作流；未达 CCL alert | Acceleration Level 1 CCL；Automation Level 1 CCL | **CCL not reached** |

**相对 3 Pro 卡的框架增量（仅字段级）：**

1. FSF 版本：**September-2025 → April-2026**。
2. 出现 **TCL**（Tracked Capability Level）列——3 Pro 卡主表以 CCL 为主。
3. CBRN 与 Cyber 均写明 **alert threshold** 已触及但 CCL 未达（3 Pro Cyber 亦有「Alert threshold met / CCL not reached」同类结构）。
4. Misalignment 与 ML R&D 合并叙述；对照锚改为 **3.1 Pro**（非 2.5）。
5. 出货声明：更新了 **CBRN + cyber offense** misuse 防护。
6. 细节外链 *Gemini 3.7 Frontier Safety Framework Report*（**本仓库未收录**）。

---

## 5. 待核实与引用

### 5.1 待核实

| # | 项 | 原因 |
|---|---|---|
| 1 | Gemini **3.6 Flash** Model Card 全文 | 本卡架构/数据/硬件/软件/政策均 defer；本库未另存 3.6 PDF |
| 2 | *Gemini 3.7 Frontier Safety Framework Report* | 本卡仅「available here」；本地未见 PDF |
| 3 | `deepmind.com` vs `deepmind.google` evals URL | 与 3 Pro 卡同类域名写法差；方法页两种均可开 |
| 4 | 「algorithmic improvements to… core reasoning foundation」具体内容 | 仅口号；无层/路由/损失名 |
| 5 | 「customizable thinking configurations」与 2.5 Thinking budget / 3 Pro Deep Think 的 API 映射 | 本卡无旋钮名与数值 |
| 6 | 「agentic video understanding」产品能力边界 | 仅 LVBench + 用途 bullet；无系统图 |
| 7 | Vertex AI / Cloud 分发是否仍覆盖 | 本卡改列 Enterprise App / Agent Platform，未写 Vertex |
| 8 | CharXiv 相对 3.6 的小幅回退是否方法噪声 | 表内 −0.7 pp；方法页 Gemini「with tools」= search + code execution |
| 9 | HLE-Verified vs 3 Pro HLE | 集合定义不同（方法页 1,811 verified）；禁直接纵向比 |
| 10 | 引入价到期后价格与 3.6 博文标价关系 | 本卡脚注 2027-01-01 起 $1.50/$7.50；与公开 3.6 博文常驻价叙述需产品页再核 |

### 5.2 主要引用（本地可核对）

| 类型 | 路径 / 标识 |
|---|---|
| 主 PDF | `https://deepmind.google/models/model-cards/gemini-3-7-flash/` |
| 卡页 | https://deepmind.google/models/model-cards/gemini-3-7-flash/ |
| 方法页 | https://deepmind.google/models/evals-methodology/gemini-3-7-flash |
| 2.5 / 3 Pro 对照 | 模型与技术报告/厂商报告/Gemini25技术报告深读.md；模型与技术报告/SystemCard/Gemini3ProModelCard.md |

### 5.3 跟读回填建议（不写进事实栏）

- **[[开源与闭源前沿模型谱系]]**：Gemini 行可加 **3.7 Flash（2026-08）**——Flash 线迭代；参数仍未公开；依赖 3.6。
- **[[推理时扩展TestTimeScaling]]**：可记「可配置 thinking」产品旋钮延续，但无 budget 曲线。
- **[[多模态架构脉络]]**：agentic video / LVBench 作 Flash 线视频锚；勿覆盖 2.5 视频 token 配方。
- **B11**：短卡 + defer 前代卡 + FSF 外链，是 DeepMind「增量 Model Card」字段范例。

---

## 6. 摘要（给父代理 / 速览）

Gemini 3.7 Flash Model Card（**2026-08-13** 发布，**9** 页）把该型号定位为基于 **3.6 Flash** 的 Gemini 3 族下一迭代：口号为 **核心推理算法改进 + agentic video + 可配置 thinking（质量/成本/延迟）**；上下文 **1M** / 输出 **64K**；knowledge cutoff 名义 **2026-03**（部分域仍可能 **2025-01**）。架构/数据/硬件/软件/安全政策正文 **全部 defer 至 3.6 Flash 卡**（本仓库未入库）——相对 2.5 TR / 3 Pro 卡**无新 MoE/Infra 数字**。能力表（vs 3.6）显示 DeepSWE **+16.7 pp**、AutomationBench **+13.4 pp**、OSWorld-2.0 **+14.1 pp**、GDP.pdf **+12.0 pp**、MRCR 128k **+5.2 pp** 等；CharXiv 相对 3.6 **略降 ~0.7 pp**。引入价 **$0.75 / $3.75**（至 2026-12-31）。安全相对 3.6 近似持平（±1 pp）；FSF **April-2026** 下 CBRN/Cyber **达 alert、未达 CCL**，并报告 **TCL not reached**；出货加强 CBRN/cyber offense 防护。技术深度仍依赖外链方法页与 FSF 报告。

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

