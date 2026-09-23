---
title: Gemini 2.5 Technical Report 深读笔记
topic: TR-Gemini-2.5
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2507.06261
archived: 2026-09-22
---

# Gemini 2.5 Technical Report 深读笔记

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：Gemini Team, Google, *Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities*
> 官方 PDF：`https://arxiv.org/abs/2507.06261`（**73** 页 A4）
> 本卡边界：只写报告正文/表已公开内容；**禁止**补参数量、专家数、未写明的层图。对照增量以本地笔记 **[[开源与闭源前沿模型谱系]]**、**[[多模态架构脉络]]**（并旁及 [[长上下文位置编码与系统侧]] / [[推理时扩展TestTimeScaling]] / [[AI基础设施总览]]）为准。

---

## 一、报告元信息

| 字段 | 核实值 | 出处 |
|---|---|---|
| 标题 | Gemini 2.5: Pushing the Frontier with Advanced Reasoning, Multimodality, Long Context, and Next Generation Agentic Capabilities | 封面 |
| 作者 | Gemini Team, Google | 封面 |
| 通信 | gemini-report@google.com | 封面页脚 |
| arXiv 页眉 | **arXiv:2507.06261v6** \[cs.CL\] **19 Dec 2025** | PDF 第 1 页页眉 |
| PDF 页数 | **73** | |
| HTML / PDF | https://arxiv.org/abs/2507.06261 ；https://arxiv.org/pdf/2507.06261 | arXiv |
| 系列定位 | Gemini **2.X** 族：2.5 Pro、2.5 Flash，以及更早的 2.0 Flash、2.0 Flash-Lite；自称覆盖 capability–cost **Pareto frontier** | Abstract；§1；§6 |
| 相对 Gemini 1.5 | 原生多模态 + **>1M** 输入上下文 + native tool use；2.5 为 **thinking** 模型族；训练稳定与后训练（SFT/RM/RL）显著加码 | §1；§2 |
| 核心产品主张（摘要级） | 2.5 Pro：coding / reasoning SoTA 叙事 + 多模态理解，可处理最长约 **3 小时**视频；2.5 Flash：可控 thinking budget 的 hybrid reasoning；2.0 Flash / Flash-Lite：低延迟低成本 | Abstract；Table 1 |

**摘要级一句话（不外推）：**
Gemini 2.X 把 **稀疏 MoE + 原生多模态 + 百万级上下文 +（2.5）动态 Thinking / Thinking budget + 工具调用** 叠进同一产品族，并用 TPUv5p / Pathways 级 Infra 与加强的 SFT→RM→RL 后训练推高 coding / reasoning / agentic 能力。

---

## 二、模型族 / Thinking / 多模态 / 长上下文对照表（据报告）

### 2.1 型号对照（Table 1，含 1.5 对照）

报告注明：Tool use = 识别并执行 function call（如 web search、算题、执行代码）；标 `*` 者「currently limited to Experimental or Preview, see Section 2.7」；信息截至发表日。

| 型号 | 输入模态 | 输入长度 | 输出模态 | 输出长度 | Thinking | Tool use | Knowledge cutoff |
|---|---|---|---|---|---|---|---|
| Gemini 1.5 Flash | Text, Image, Video, Audio | **1M** | Text | **8K** | No | No | November 2023 |
| Gemini 1.5 Pro | 同上 | **2M** | Text | **8K** | No | No | November 2023 |
| Gemini 2.0 Flash-Lite | 同上 | **1M** | Text | **8K** | No | No | June 2024 |
| Gemini 2.0 Flash | 同上 | **1M** | Text, Image\* | **8K** | Yes\* | Yes | June 2024 |
| Gemini 2.5 Flash | 同上 | **1M** | Text, Audio\* | **64K** | **Dynamic** | Yes | January 2025 |
| Gemini 2.5 Pro | 同上 | **1M** | Text, Audio\* | **64K** | **Dynamic** | Yes | January 2025 |

**定位一句话（§1）：**

| 型号 | 报告定位 |
|---|---|
| 2.5 Pro | most intelligent **thinking** model；强 reasoning / code；interactive web apps、codebase-level understanding、emergent multimodal coding |
| 2.5 Flash | **hybrid reasoning**，**controllable thinking budget**；在 quality / cost / latency 间权衡 |
| 2.0 Flash | fast、cost-efficient；正文称 everyday 用的 **non-thinking** 型号（Table 1 对其 Thinking 列为 Yes\*，属 Preview/Experimental 路径） |
| 2.0 Flash-Lite | fastest、most cost-efficient；at-scale |

API 映射（Table 2）：`gemini-2.5-pro` / `gemini-2.5-flash` / `gemini-2.0-flash-001` / `gemini-2.0-flash-lite-001` 等。

### 2.2 Thinking（§2.5；Figure 3–4）

| 维度 | 报告内容 |
|---|---|
| 动机 | 过去 Gemini 查询后立刻作答，限制 inference-time compute |
| 训练 | **Reinforcement Learning** 训模型在推理期多用算力；thinking 阶段可达 **tens of thousands of forward passes** |
| 演进 | 实验型号 **Gemini 2.0 Flash Thinking**（2024-12）→ **2.5 Thinking series**，把 Thinking **natively** 写入各域 |
| 与多模态 / 长上下文 | Thinking 与 native multimodal（image/text/video/audio）及 **1M+** 上下文集成；模型自行决定「想多久」 |
| Thinking budget | 用户可设 token 预算约束内部计算；Figure 4：提高 budget → AIME 2025 / LiveCodeBench / GPQA diamond 精度上升 |
| Table 1 写法 | 2.5 Pro / Flash = **Dynamic**；2.0 Flash = Yes\* |

另：§2.7 **Gemini 2.5 Pro Deep Think**——并行 thinking、多假设再批判；宣称在 USAMO 2025、LiveCodeBench、MMMU 等达 SoTA（细节指向 Doshi, 2025b）；I/O 宣布，2025-06 对可信测试者 / 高级用户放实验版。**Deep Think 的算法细节本报告未展开。**

### 2.3 多模态（§2.1 / §2.6 Audio & Video / Table 5–6）

| 维度 | 报告内容 |
|---|---|
| 架构主张 | **sparse MoE transformers**，**native multimodal** 支持 **text, vision, and audio** 输入（§2.1） |
| 视觉 | 相对 1.5，视觉处理架构改进；可处理约 **3 小时**视频；示范视频 → 交互式 coding 应用（引 Baddepudi et al., 2025） |
| 视频 token | 训练使模型在每帧约 **66**（而非 **258**）visual tokens 仍具竞争力 → 同一 **1M** 窗口内约 **3h** 视频（相对约 **1h**）；API 称 *low media resolution* |
| 音频理解→生成 | 1.5 主打理解（转写/翻译/摘要/QA）；**2.5** 增加 TTS、native audio-visual→audio dialog；**causal audio** 表示以支持低延迟流式入出 |
| 音频数据 | 预训练音频覆盖 **>200** 语言；后训练把 thinking、affective dialog、contextual awareness、tool use 写入 native audio 模型 |
| 2.5 Audio 产品路径（§2.7） | Controllable TTS（>80 语、多说话人等）与 Native Audio Dialog（>24 语、工具调用、语气理解）在 AI Studio 分入口；另有 Thinking 变体换延迟换稳健性 |
| 图像生成实验 | **Gemini 2.0 Flash Native Image Generation**（2025-03 实验）：对话式编辑、交错文图等（Table 1 输出 Image\*） |
| 评测指针 | 图像：Table 3（MMMU、Vibe-Eval、ZeroBench、BetterChartQA）；音频 Table 5；视频 Table 6（VideoMME 等，2.5 Pro 宣称相对 GPT-4.1 等同测条件下 SoTA） |

### 2.4 长上下文（§2.1 / §2.6 Long context；Table 3 / 4）

| 维度 | 报告内容 |
|---|---|
| 窗口 | 2.5 Pro / Flash：**1M** 输入（Table 1）；正文称相对 1.5 Pro，在最长 **1M** 序列上质量超越（见 Table 3） |
| 1.5 对照 | 1.5 Pro 输入曾标 **2M**；2.0 Pro 实验版亦曾带 **2M**（§2.7）——**2.5 主力表列为 1M** |
| 数据形态 | 长文（如 *Moby Dick* / *Don Quixote*）、整仓代码、长音频 / 视频（Appendix 8.5） |
| Hill-climb 靶标 | LOFT（Lee et al., 2024）、MRCR-V2（Vodrahalli et al., 2024）、VideoMME（Fu et al., 2025）等 |
| Table 3 摘录（2.5 Pro vs 1.5 Pro） | LOFT hard ≤128K：**87.0%** vs 75.9%；LOFT 1M：**69.8%** vs 47.1%；MRCR-V2 8-needle ≤128K：**58.0%** vs 26.2%；MRCR-V2 1M：**16.4%** vs 12.1% |
| 视频召回示例 | Appendix 8.5：46 分钟视频中一致召回 **1 秒**视觉事件 |
| Agent 侧注意（§4.1） | 虽支持 1M+，agent 场景下上下文显著增长时出现新研究前沿问题（有效利用 / 行为变化）；报告如实写出观察，未给通用解法 |

### 2.5 架构骨架公开点（§2.1）——无参数表

| 项 | 报告已写 | 报告未写 |
|---|---|---|
| 骨干 | sparse **MoE** Transformer；动态路由子集专家；解耦总容量与每 token 算力/serving 成本 | **总参 / 激活参 / 专家数 / 层数 / 隐藏维** |
| 训练稳定 | 大规模训练稳定性、信号传播、优化动力学改进 → 预训练结束即相对前代大幅提升 | 具体稳定化配方细节 |
| 小模型 | Flash 及以下用 **distillation**；教师 next-token 分布用 **k-sparse** 近似以省存储（吞吐/存储仍约 ×k） | k 的数值、教师型号 |
| 长上下文建模 | 「new modeling advances」使 2.5 Pro 在 1M 上超 1.5 Pro | 位置编码 / 注意力变体名称与公式 |

---

## 三、训练或后训练公开要点

### 3.1 数据（§2.2）

| 项 | 内容 |
|---|---|
| 预训练 | 大规模多域多模态：公开 web、代码、图像、音频、视频 |
| Cutoff | **2.0：June 2024**；**2.5：January 2025**（与 Table 1 knowledge cutoff 一致） |
| 相对 1.5 | 改进 filtering 与 deduplication |
| 后训练数据 | 与 1.5 类似：审慎收集的 instruction 数据；多模态指令–响应对；human preference；**tool-use** 数据 |
| 评测防泄漏（§3） | 除 n-gram decontamination 外，增加 semantic-similarity 与 model-based decontamination；并继续报内部非公开榜（如 HiddenMath） |

**未公开：** 预训练 token 总量、各模态配比、精确过滤管线。

### 3.2 训练 Infra（§2.3）——AI Infra 主轴

| 项 | 报告内容 |
|---|---|
| 硬件 | 本族 **首次**在 **TPUv5p** 上训练 |
| 并行 | **synchronous data-parallel**；跨多个数据中心的多个 **8960-chip** TPUv5p **pods** |
| 软件相对 1.5 | 重点：**elasticity** + 缓解 **SDC（Silent Data Corruption）** |
| Slice-Granularity Elasticity | 局部故障时自动以更少 TPU 「slices」继续训；重配约损失 **数十秒**（相对无弹性 ≥10 分钟）；故障片恢复期间约 **97%** 吞吐；该规模硬件中断可达 **多小时一次**量级 |
| Split-Phase SDC Detection | 可疑 step 立即轻量确定性重放，比对角设备中间 checksum；间歇 SDC 加速器常在 **数分钟内**定位并剔除；约 **0.25%** steps 因疑似 SDC 重放，其中约 **6%** 确认为真硬件损坏 |
| 控制器 | **Pathways** 单控制器（Barham et al., 2022）：单一 Python 全局视图；remote python 监控指标 / straggler / SDC |
| 时间账 | **93.4%** 时间在做 TPU 计算；其余约一半弹性重配、一半弹性失败的稀有尾部；约 **4.5%** computed steps 为调试干预的 replay/rollback |

### 3.3 后训练（§2.4）

| 项 | 内容 |
|---|---|
| 阶段 | **SFT → Reward Modeling (RM) → Reinforcement Learning (RL)**，全程强调 **data quality** |
| 模型自助 | 用模型自身辅助质控，提高效率与细粒度 |
| RL 算力 | 分配给 RL 的训练算力增加，加深行为探索与精炼 |
| 奖励 | **verifiable rewards** + **model-based generative rewards** |
| 算法 | RL 算法改动以改善长训稳定性 |
| 环境 | 更多样、更复杂的 RL 环境，含 **multi-step actions** 与 **tool use** |
| 结果叙事 | LMArena Elo：相对 1.5 对照，2.5 Pro **+122**、2.5 Flash **+111**（Figure 1）；多条 frontier 榜提升（§3） |

### 3.4 能力专项（§2.6 摘要，跟读用）

| 能力 | 公开要点 |
|---|---|
| Code | 预训练加重仓库/网页代码；后训练引入 reasoning + 工程任务；LiveCodeBench 1.5 Pro **30.5%→** 2.5 Pro **74.2%**；Aider Polyglot **16.9%→82.2%**；SWE-bench Verified **34.2%→67.2%**（§2.6 / Table 3） |
| Factuality | 2.0 起原生调用 Google Search 等工具；2.5 将 search 与内部 thinking **交错**做多跳 / 长程核实 |
| Multilinguality | 1.5 已预训练覆盖 **>400** 语言；2.X 在 Indic / CJK 等做数据与 tokenization / 建模 hill-climb |
| Agentic / Deep Research | Deep Research 基于 2.5 Pro；HLE：2024-12 **7.95%** → 2025-06 SoTA **26.9%**（更高算力 **32.4%**） |

### 3.5 路径上的实验型号（§2.7，时间线）

| 型号 / 能力 | 时间（报告） | 要点 |
|---|---|---|
| 2.0 Flash Thinking | 2024-12 | 实验 thinking |
| 2.0 Pro（实验） | 2025-02 | 当时族内最强 coding / 知识；上下文 **2M** |
| 2.0 Flash Native Image Gen | 2025-03 | 原生图像生成 / 编辑 |
| 2.5 Flash-Lite（实验） | 2025-06（preview-06-17） | 可开 thinking + budget；Search / code execution；多模态；**1M** |
| 2.5 Pro Deep Think | I/O 宣布；2025-06 实验 | 并行假设式推理 |

---

## 四、相对 [[开源与闭源前沿模型谱系]] / [[多模态架构脉络]] 的增量

> 对照对象：本地 模型与技术报告/开源与闭源前沿模型谱系.md、多模态与具身/视觉语言/多模态架构脉络.md（旁及 架构/注意力与长上下文/长上下文位置编码与系统侧.md、架构/推理时扩展TestTimeScaling.md、推理与基础设施/AI基础设施总览.md）。下列只写「博客/谱系卡 → 本技术报告」可核实的增量。

### 4.1 相对 [[开源与闭源前沿模型谱系]]（前沿谱系）

| [[开源与闭源前沿模型谱系]] 当时写法 | 本报告增量（可回填谱系表） |
|---|---|
| Gemini 2.5：**Dense/MoE = 未公开** | §2.1 明确 **sparse mixture-of-experts (MoE)** transformers；仍 **未给**总参/激活参/专家配置 |
| Thinking：内建 thinking；细节少 | §2.5：RL 训 inference-time thinking；**Dynamic** + **Thinking budget**；与多模态/1M+ 集成；Figure 3–4；另有 **Deep Think** 产品路径（细节外链） |
| 上下文：**1M（2M soon）**（博客口径） | Table 1：2.5 Pro/Flash 输入 **1M**、输出 **64K**；1.5 Pro / 2.0 Pro 实验曾有 **2M**，**2.5 表列非 2M**——「2M soon」是否落到 2.5 正式 API **本报告未承诺** |
| 训练集群：未公开 | **TPUv5p**；多 datacenter、多 **8960-chip pods**；**Pathways**；Slice 弹性 + Split-Phase SDC；时间账 93.4% 等——仍无 GPU-hour / FLOPs 总量 |
| 安全 / Critical Capabilities | §5 / Table 10：CBRN、cyber、ML R&D、deceptive alignment 等；报告称 **未达到**任一 Critical Capability Level（跟读安全章时回原表，本卡不展开方法） |

**对 [[开源与闭源前沿模型谱系]] 表「Google Gemini 2.5」列建议改写（事实级）：**
Dense/MoE → **稀疏 MoE（参数量未公开）**；Thinking → **Dynamic + budget（RL）**；Infra → **TPUv5p + Pathways 弹性/SDC（规模数字有限）**。

### 4.2 相对 [[多模态架构脉络]]（多模态脉络）

| [[多模态架构脉络]] 待核实 / 主张 | 本报告可确认 | 仍未解决 |
|---|---|---|
| 「原生多模态」仅为博客主张 | §2.1：**native multimodal** text / vision / audio；与稀疏 MoE 同句陈述 | **无** CLIP/Flamingo 级模块图；未说明是否仍有独立视觉编码器 / Perceiver / early-fusion 细节 |
| 实现级：融合方式、预训练阶段 | 视频：**66 vs 258** tokens/frame → ~3h/@1M；音频：causal 表示 + 生成式 TTS/dialog；图像生成走 2.0 Flash 实验路径 | 「取消外挂编码器？」**不可**由报告推出；勿把 native 等同「无视觉塔」 |
| 多模态 + thinking | Thinking **明确**叠在多模态输入与长上下文上（§2.5） | Thinking 与视觉 token 交互的内部机制未写 |

### 4.3 旁及增量（非标题主轴，便于串联）

| 笔记 | 增量要点 |
|---|---|
| **[[长上下文位置编码与系统侧]] 长上下文** | LOFT / MRCR-V2 在 ≤128K 与 **1M** 两档数字（Table 3）；视频 1s/@46min 召回示例；agent 长上下文有效利用仍是开放问题（§4.1） |
| **[[推理时扩展TestTimeScaling]] test-time scaling** | Thinking budget 曲线（Figure 4）= 官方可控 test-time compute 旋钮；Deep Think = 并行假设路径（细节不足） |
| **[[AI基础设施总览]] AI Infra** | Pathways 单控制器 + 切片弹性 + SDC 确定性重放 → 可补「超大 TPU 训练可靠性」案例；**非**开源并行栈配方 |

### 4.4 关键评测锚点（Table 3，2.5 Pro；便于与谱系横比时核对口径）

| 榜 | Gemini 2.5 Pro | 同表 1.5 Pro |
|---|---:|---:|
| LiveCodeBench | 74.2% | 29.7%（§2.6 正文写 30.5%，引用时以表/脚注为准 → 见第五节） |
| Aider Polyglot | 82.2% | 16.9% |
| SWE-bench Verified（multiple attempts） | 67.2% | 34.2% |
| GPQA diamond | 86.4% | 58.1% |
| AIME 2025 | 88.0% | 17.5% |
| MMMU | 82.0% | 67.7% |
| Humanity’s Last Exam（no tools） | 21.6% | 4.6% |

Table 4 另与 o3 / o4-mini / Claude 4 / Grok 3 / DeepSeek R1 等横比；**脚手架与尝试次数不同时禁止无脚注硬比**（[[开源与闭源前沿模型谱系]] 已警告）。

---

## 五、待核实与引用

### 5.1 待核实（禁止当作已确认）

| # | 项 | 原因 |
|---|---|---|
| 1 | 总参数量、激活参数、专家数/层数/隐藏维、路由算法细节 | 报告仅写 sparse MoE，无配置表 |
| 2 | 预训练 token 总量、模态配比、精确数据管线 | §2.2 仅定性 |
| 3 | Thinking / Deep Think 的算法伪代码、并行宽度、与 CoT 标记格式 | §2.5 / §2.7 产品级描述；Deep Think 细节指向外链博客 |
| 4 | 蒸馏教师型号与 k-sparse 的 k | §2.1 仅机制 |
| 5 | 位置编码 / 长上下文注意力变体名称 | 「new modeling advances」无公式 |
| 6 | 2.5 正式产品是否提供 **2M** 上下文 | Table 1 为 1M；2M 见于 1.5 Pro / 2.0 Pro 实验叙述 |
| 7 | LiveCodeBench：§2.6「1.5 Pro 30.5%」vs Table 3「29.7%」 | 正文与表不一致，引用前以 PDF 原表 + 评测脚注（Table 11）为准 |
| 8 | Table 1 中 2.0 Flash「Thinking=Yes\*」与 §1「non-thinking everyday model」的产品口径差 | 以 Preview/Experimental 脚注理解，勿混成「默认 thinking」 |
| 9 | 外部安全测试全文与 Critical Capability 方法学细节 | §5 篇幅大；本卡未逐条转写 |
| 10 | arXiv 版本史（v1…v6）各版差分 | 本 PDF 页眉为 **v6 / 19 Dec 2025**；更早版变更未在本任务逐 diff |

### 5.2 主要引用（报告内）

| 标签 | 内容 |
|---|---|
| [G25-TR] | Gemini Team, Google. *Gemini 2.5: Pushing the Frontier…* arXiv:2507.06261v6, 19 Dec 2025. 本地：`https://arxiv.org/abs/2507.06261` |
| Table 1–6 | 型号对照；API ID；核心能力；跨模型；音频；视频 |
| §2.1–2.7 | 架构 / 数据 / Infra / 后训练 / Thinking / 能力专项 / 路径型号 |
| §3 | 定量评测与方法论 |
| §4 | Gemini Plays Pokémon 等 agentic 用例 |
| §5 | Safety / Frontier Safety Framework |
| §6 | Discussion |

### 5.3 本地笔记交叉

| 笔记 | 关系 |
|---|---|
| [[开源与闭源前沿模型谱系]] | 谱系「Gemini 行」应用本卡回填 MoE / Thinking budget / TPUv5p |
| [[多模态架构脉络]] | 「原生多模态」从博客主张 → 报告确认输入模态与视频/音频专项；**架构图仍缺** |
| [[长上下文位置编码与系统侧]] | 1M 档 LOFT/MRCR 与视频长上下文示例 |
| [[推理时扩展TestTimeScaling]] | Thinking budget / Deep Think ↔ test-time scaling |
| [[AI基础设施总览]] | Pathways 弹性与 SDC 检测作 Infra 案例 |
| [[混合专家架构]] / [[DeepSeekV3训练与MoE基建]] | 同为 MoE，但 Gemini **无**可对表的专家配置 / FP8 / 并行拓扑细表——不可硬套 DeepSeek 数字 |

---

## 附：抽取与写作约束备忘

- 原文 https://arxiv.org/abs/2507.06261`
- 数字与断言均来自上述 PDF；未在报告出现的参数量、层图、训练 FLOPs **未写入正文表**。
- 安全章（CBRN / cyber CTF 风格评测图等）仅作「未达 CCL」元结论索引，**不**转写攻击步骤。

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[GPT5SystemCard|TR GPT-5]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[智能体工具与长程任务|智能体与工具]]
- [[评测与排行榜可靠性|评测可靠性]]

