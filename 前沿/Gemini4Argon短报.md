---
date: 2026-10-14
status: archived
archived: 2026-10-14
topic: Gemini4Argon短报
title: "Gemini 4 Argon（前沿短报）"
lines: [评测字段, Fairwind放量]
sources:
 - https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/
 - https://deepmind.google/models/model-cards/gemini-4-argon/
 - https://blog.google/innovation-and-ai/technology/safety-security/gemini-4-model-safety-security/
 - https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-argon
 - https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/
 - https://deepmind.google/models/evals-methodology/gemini-4-argon
 - https://deepmind.google/fairwind-program/
 - https://ai.google.dev/gemini-api/docs/pricing
related: ["GPT61Sol系统卡短报", "MiMoV26智能体强化学习短报", "Gemini3Pro模型卡深读", "Gemini37Flash模型卡深读", "Gemini25技术报告深读", "网络防御基准", "Prompt注入架构防御", "安全论证SafetyCases", "ClaudeSonnet55系统卡短报", "ClaudeOpus55系统卡短报", "Gemma4技术报告深读"]
retrieval_cutoff: 2026-10-14
timezone: Asia/Shanghai (CST)
---

# Gemini 4 Argon（前沿短报）

> **主要来源**：[Gemini 4 Argon: Built to solve your hardest problems](https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/)；[Gemini 4 Argon Model Card](https://deepmind.google/models/model-cards/gemini-4-argon/)；[Developing Gemini 4 Argon responsibly and safely](https://blog.google/innovation-and-ai/technology/safety-security/gemini-4-model-safety-security/)；[Gemini 4 Argon（Cloud 文档）](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-argon)；[Gemini 4 Argon: our next era of frontier intelligence](https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/)（首发）；[Fairwind Program](https://deepmind.google/fairwind-program/)（截至 2026-10-14）。下文「GA 博文」指 Introducing 页；「模型卡」指 DeepMind 网页版 Model Card；「安全博文」指 Developing responsibly 页；「Cloud 文档」指 Gemini Enterprise Agent Platform 模型页；「首发博文」指 2026-09-30 发布页；「Fairwind 页」指 Fairwind Program 官方页。完整 Safety & Security Report 仅有 PDF，正文挂安全博文与模型卡入口，不引 PDF 直链。
> **研究线**：评测字段（官方绝对分与 harness 限定）· Fairwind / Cyber Permissive 分阶段放量 · 统一 1M 窗口与 introductory 价
> **意义**：Argon 先经 Fairwind 向受信防御者放量，再于 2026-10-13 全球公开 GA，并配套网页模型卡与安全博文；公开版带护栏，另有 allowlist 的 Cyber Permissive 变体服务防御侧。
> **范围与相邻笔记**：
> - ≠ [[GPT61Sol系统卡短报]]：本篇不写 Sol / DevDay；DeepSWE 等只引 Google 官方分与方法，不以 Sol 相对叙述覆盖 Argon。
> - ≠ [[MiMoV26智能体强化学习短报]]：本篇不写 MiMo 的 RL batch / multi-harness / 开源环境专史；不把 MiMo 分与 Argon 拼成同一实验。
> - ≠ [[Gemini3Pro模型卡深读]] / [[Gemini37Flash模型卡深读]] / [[Gemini25技术报告深读]]：本篇不重写 3.x / 2.5 模型卡或技术报告；仅作 Gemini 族谱系入口与旧代输出上限对照。
> - ≠ [[网络防御基准]] / [[Prompt注入架构防御]] / [[安全论证SafetyCases]]：本篇只点到防御侧评测、IPI **0.7%** 与模型卡 FSF 表结论级表述，不展开基准任务构造或安全论证通史。
> - ≠ [[ClaudeSonnet55系统卡短报]] / [[ClaudeOpus55系统卡短报]]：本篇不重做 Anthropic 系统卡；对照分仅在模型卡 / 评测方法页已列处出现。
> - ≠ [[Gemma4技术报告深读]]：本篇不写 Gemma 4 开源报告。

**背景**：Gemini 2.5 与 3.x 各型号按技术报告或模型卡发布，输入 1M、输出上限 64K（[[Gemini25技术报告深读]]、[[Gemini3Pro模型卡深读]]、[[Gemini37Flash模型卡深读]]）；Argon 是其后 Gemini 4 代的 frontier 旗舰。

**一句话**：Gemini 4 Argon 于 2026-09-30（UTC；上海时间 2026-10-01）经 Fairwind 首发，2026-10-13 全球公开 GA；稀疏 MoE、原生多模态，统一 **1,048,576** token 的 input+output 窗口；introductory API 价为每百万 token 输入 **$2** / 输出 **$10**，至 **2026-11-30**，期满为 **$4** / **$20**；配套网页模型卡与安全博文，另有 allowlist 变体 `gemini-4-argon-cyber-permissive`。

## 一、定位与放量

| 项目 | 内容 | 出处 |
|---|---|---|
| 首发 | 首发博文发布时间 **2026-09-30 20:00 UTC**（≈ 上海 **2026-10-01 04:00**）；作者 Koray Kavukcuoglu | 首发博文页面 |
| 公开 GA | GA 博文页眉 Oct 13, 2026；发布时间 **2026-10-13 16:00 UTC**（≈ 上海 **2026-10-14 00:00**） | GA 博文页面 |
| 定位 | Gemini 4 代 frontier 模型；强调复杂长程工作流：真实软件工程、企业知识工作（法律 / 金融等）、网络安全防御 | GA 博文；模型卡 |
| GA 渠道 | 开发者：Gemini API paid tier（AI Studio、Android Studio）；Google AI Ultra：Antigravity、AI Studio；企业：Gemini for business、API、Antigravity；订阅用户：Gemini app、Search AI Mode（Ultra / Pro） | GA 博文 *Get started today* |
| Fairwind | 继续向更多受信 cyber defenders 滚动扩容；公开版带护栏；无护栏防御能力经 allowlist 的 Cyber Permissive 提供（见第四节） | GA 博文；Cloud 文档 |
| 预发布流程 | 首发时写明参与美国政府自愿预发布模型访问流程 | 首发博文 |
| 文档形态 | 网页 [Model Card](https://deepmind.google/models/model-cards/gemini-4-argon/)（Published **13 October 2026**）；安全博文为完整报告的网页入口；另有首发配套的 Model evaluation PDF（方法 + 结果） | 模型卡；安全博文 |

- **内部使用索引**（细节见首发 / GA 博文）：量子算法子程序时空资源优化；机房侧 profiling 释放内存；大规模 C/C++→Rust 迁移；GA 阶段另索引 Chrome 架构重构、ADK、xTB、Gemma 推理加速等厂商自述案例。

## 二、规格与价

| 项目 | 官方表述 | 出处 |
|---|---|---|
| 统一窗口 | 合并 input+output 上限 **1,048,576** tokens（模型卡写作「combined input-output token context window of up to 1M」；Cloud 写作统一 **1,048,576**） | 模型卡 Inputs/Outputs；Cloud 文档 |
| 与首发措辞差异 | 首发博文突出 **output** 上限 1M（相对此前 **64K**），主博文未单列统一 input 窗口；GA / 模型卡 / Cloud 改为统一 1M I/O | 首发博文；模型卡；Cloud |
| Thinking levels | `LOW` / `MEDIUM`（默认）/ `HIGH`；设 `thinking_budget` 或 `thinking_level="MINIMAL"` 返回 HTTP 400 | Cloud 文档 |
| 产品层差异 | 自定义 `temperature` / `top_p` / `top_k` **被忽略**；仅支持隐式缓存（最小 **6,144** tokens），不支持显式缓存；`GenerateContent` 可用 `continuation_token` 做 long decode | Cloud 文档 |
| Introductory 价 | 每百万 token：输入 **$2** / 输出 **$10**；缓存输入相对输入价 **95% off** | GA 博文脚注 1；与首发一致 |
| Introductory 截止 | 至 **2026-11-30**；之后输入 **$4** / 输出 **$20**（每百万 token；适用于公开版 Argon） | GA 博文脚注 |
| 公开价目 | [Gemini API 定价页](https://ai.google.dev/gemini-api/docs/pricing) 已挂 `gemini-4-argon`：Paid Tier 输入 **$2.00** through November 30, 2026 / **$4.00** starting December 1, 2026；输出 **$10.00** / **$20.00** 同期切换；页脚 Last updated **2026-10-13** UTC | 定价页 |
| 架构摘要 | 大规模稀疏 MoE + transformer；原生多模态（文本 / 视觉 / 音频输入） | 模型卡 Architecture |
| 知识截止 | **March 2026**；部分领域可能更旧 | 模型卡 Known Limitations |

## 三、能力短表（官方绝对分）

下列绝对分以模型卡 Results 表（as of October, 2026）为主；前四行与首发博文 / 评测 PDF 一致。方法限定见 [evals methodology](https://deepmind.google/models/evals-methodology/gemini-4-argon)。

| 评测 | Argon | 官方主张 / 限定 | 出处 |
|---|---:|---|---|
| DeepSWE v1.1 | **77.9%** | 方法页：Argon 分为 **self-computed**，使用 **mini-swe agent harness**；对照分来自公开榜 / 他厂系统卡 | 模型卡；方法页 · Coding |
| AutomationBench | **51.3%** | 方法页：private set，来自 Zapier 公开榜 | 模型卡；方法页 · Knowledge work |
| LVBench | **91.7%** | 方法页：**self-computed without tools**；Gemini 用 **1 FPS**（他厂帧数因 API 限制不同） | 模型卡；方法页 · Multimodal |
| CWE-bench v1 | **68.0%** | 方法页：取自公开榜，按 **pass@1** 排名、**pass@4** 破平 | 模型卡；方法页 · Cybersecurity |
| Vals Index | **68.9%** | 方法页：sourced from Vals AI | 模型卡 |
| Vals Finance Agent v2 | **65.4%** | 方法页：sourced from Vals AI | 模型卡 |
| Harvey's Legal Agent Benchmark | **19.6%** | 方法页：sourced from Vals AI | 模型卡 |
| FrontierSWE v2 | **55.0%** | 方法页：Proximal 公开榜 | 模型卡 |
| Terminal-bench 4.0 | **57.4%** | 方法页：Argon **self-computed**；他厂取公开榜最高 thinking | 模型卡 |
| GraphWalks（≤128k，BFS F1） | **99.7%** | 方法页：self-computed；≤128k 子集 650 题 | 模型卡 |
| GraphWalks（256k–1M，BFS F1） | **84.2%** | 方法页：200 题，上下文 256k–1M | 模型卡 |

- 评测通例（方法页）：Argon 分多为 **pass@1**，经 Gemini API、最高 thinking 设置，小榜多次试验取平均；能力日期方法节写 September 2026、Results 写 October 2026。
- **ERQA 87%**：仅见于 GA 博文机器人节（Embodied Reasoning，纯推理、无工具），**不在**模型卡主表；引用时不与上表混列。

## 四、安全、FSF 与 Cyber Permissive

### 安全四块（结论级；不写攻击步骤）

数字以 GA 博文 / 安全博文为准；相对 Gemini 3.1 Pro 的安全百分点表见模型卡 Training and Development Evaluation Results。

1. **防滥用（misuse）**：多层防护（输入筛选、内部激活探针、连续监控）；对抗集上违规约减半；按 FSF 评估增强能力并部署护栏。相对 3.1 Pro：多语安全 **-3.16** pp、图文安全 **-9.29** pp、无理拒答 **-9.60** pp（模型卡表；lower is better 的项，负值为改善）。
2. **防 prompt injection**：Gray Swan **IPI** 上，15 次自适应尝试的攻击成功率 **0.7%**（GA 博文；安全博文同句）。
3. **错位监控（misalignment monitoring）**：训练尊重系统边界、如实报告负面结果、不可逆步骤前征求确认；编码基准上 shortcut 尝试降至 **2%**；另有实时监控读取 chain-of-thought 与动作，训练中不对思考内容施罚以免塑造沉默捷径。
4. **系统硬化（hardening systems）**：按 agent control 路线图隔离高风险训练 / 评测沙箱（安全博文指向路线图；首发博文同框架）。

### FSF 结论（模型卡 Frontier Safety Assessment）

- **Cybersecurity CCL**：无法排除达到 Level 1 CCL，已做 cyberoffensive safety case，并自评将残余风险降至该 CCL 以下。
- **CBRN / 生物**：模型卡称：无法排除 Argon 在生物信息风险上达到 FSF 的 Level 1 CCL，因而做了 biorisk safety case，并自评将残余风险降至该 CCL 以下。化学 / 放射 / 核域可较有信心排除 Uplift TCL。
- **Stealth and Situational Awareness TCL**：无法排除达到该 TCL，已做残余风险评估并自评降至 TCL 以下。
- Harmful Manipulation、ML R&D 相关档位：模型卡表写明未达到对应 CCL。

### Cyber Permissive（相对公开版）

| | 公开版 `gemini-4-argon` | Cyber Permissive `gemini-4-argon-cyber-permissive` |
|---|---|---|
| 访问 | 公开 GA | Allowlist（Fairwind / 联系 Google 团队）；与 Gemini 3.8 Flash Cyber 访问**不互通**，须单独申请 |
| 默认 thinking | `MEDIUM` | `HIGH` |
| Computer use | 支持 | **不支持** |
| 区域 | `global` / `us` / `eu` | `global` / `us`（无 `eu`） |
| 用途边界 | 通用 frontier | 防御向：漏洞发现、逆向、利用验证、补丁生成（Cloud 文档原句） |

公开版带 cyber 护栏；受信防御侧「无 cyber 护栏」能力由 Cyber Permissive 承担；公开 GA 版本与 Fairwind 受信访问并存。

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT61Sol系统卡短报]] | 读者已知的 DeepSWE / AutomationBench 评测名 | Sol / DevDay 专史；不以 Sol 相对差覆盖 Argon 77.9 |
| [[MiMoV26智能体强化学习短报]] | DeepSWE 作为长程 SWE 评测名；mini-swe 作为 harness 名 | MiMo RL 配方、开源 7k 环境与 MiMo 自家 DeepSWE 分 |
| [[Gemini3Pro模型卡深读]] / [[Gemini37Flash模型卡深读]] / [[Gemini25技术报告深读]] | Gemini 族入口；旧代「输出 64K」对照语境 | 重写 3.x / 2.5 正文 |
| [[Gemma4技术报告深读]] | — | Gemma 4 开源报告 |
| [[网络防御基准]] | 「防御侧评测」读者入口 | SecOps 狩猎任务构造与该基准模型表 |
| [[Prompt注入架构防御]] / [[安全论证SafetyCases]] | IPI **0.7%**、模型卡 FSF 表结论级交叉 | 注入防御架构或 FSF 通史；不展开 safety case 机制 |
| [[ClaudeSonnet55系统卡短报]] / [[ClaudeOpus55系统卡短报]] | 模型卡已列的 Opus / Fable 等对照列身份 | 重做 Anthropic 系统卡 |

## 六、局限与争议

- **知识截止**：模型卡写明 **March 2026**；部分领域可能更旧；另可能幻觉、偶发变慢或超时。
- **安全报告形态**：完整 Safety & Security Report 仅 PDF、无独立 HTML 落地页；正文以安全博文与模型卡为入口，不挂 PDF 直链。
- **模型卡活页**：模型卡写明 may be updated；本篇按 Published **13 October 2026** / Published: October 2026 引用。
- **Fairwind 页措辞**：Fairwind 页仍写 partners 对 Gemini 4 Argon「独家访问」；与公开 GA 并存时，Cloud 文档以 Cyber Permissive allowlist 界定无护栏变体——两处表述并存，本篇以 Cloud / GA 渠道表为准。
- **评测口径**：非 Gemini 分多取自厂商自报 / 公开榜 / 系统卡；思考强度默认取各厂最高或可得最佳——本篇不自造跨厂统一榜。ERQA **87%** 仅 GA 博文，不并入模型卡主表。
- **案例叙事**：GA / 首发博文中的工程与科研案例多为厂商自述，本短报只作索引。

## 七、延伸阅读

1. 先读 GA 博文（渠道、价、IPI **0.7%**、shortcut **2%**、ERQA）与网页模型卡（规格、能力表、FSF）。
2. 再读安全博文（三块防护叙事）与 Cloud 文档（统一窗口、thinking、Cyber Permissive 对照）。
3. 需要 harness 限定时读 [evals methodology](https://deepmind.google/models/evals-methodology/gemini-4-argon)；首发材料见下表「首发」。
4. 定价页：[Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)（已挂 `gemini-4-argon`）。

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| GA 博文 | Gemini 4 Argon: Built to solve your hardest problems | Google，2026-10-13 16:00 UTC | https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-argon/ |
| 开发者博文 | Gemini 4 Argon is now available for developers | Google，页眉 Oct 13, 2026 | https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-argon/ |
| 模型卡（网页） | Gemini 4 Argon Model Card | DeepMind，Published 13 October 2026 | https://deepmind.google/models/model-cards/gemini-4-argon/ |
| 安全博文 | Developing Gemini 4 Argon responsibly and safely | Google，页眉 Oct 13, 2026 | https://blog.google/innovation-and-ai/technology/safety-security/gemini-4-model-safety-security/ |
| Cloud 文档 | Gemini 4 Argon / Cyber Permissive | Google Cloud；Release date October 13, 2026 | https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/4-argon |
| 方法入口 | gemini-4-argon evals methodology | DeepMind（网页） | https://deepmind.google/models/evals-methodology/gemini-4-argon |
| Fairwind | Fairwind Program | Google DeepMind（页面未显示更新日期，按规范不计入截至） | https://deepmind.google/fairwind-program/ |
| 定价 | Gemini API pricing | Google AI for Developers；Last updated 2026-10-13 UTC | https://ai.google.dev/gemini-api/docs/pricing |
| 首发博文 | Gemini 4 Argon: our next era of frontier intelligence | Google，2026-09-30 20:00 UTC | https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-4-argon/ |
| 首发评测 PDF | Gemini 4 Argon Model evaluation | DeepMind；方法 September 2026，Results as of October 2026 | https://storage.googleapis.com/deepmind-media/gemini/gemini_4_argon_model_evaluation.pdf |
