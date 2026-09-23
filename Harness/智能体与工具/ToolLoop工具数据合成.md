---
title: "Toolformer 谱系新变体：ToolLoop 闭环工具数据合成（≠ ToRL / 旗舰工具环 / ACI）"
topic: ToolLoop工具数据合成
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.09072 # 424K / 15p（主）
 - https://arxiv.org/abs/2609.01736 # 458K / 21p（补链，不升主）
arxiv: ["2609.09072", "2609.01736"]
related: ["ToRL工具集成强化学习", "智能体工具与长程任务", "代码智能体Harness史线"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# Toolformer 谱系新变体：ToolLoop 闭环工具数据合成（≠ ToRL / 旗舰工具环 / ACI）

> **定位**：工具数据合成主题轴——在「Toolformer 式：为工具调用**合成训练对**」谱系上，补近窗一刀 **ToolLoop**：把 generate-then-filter 改成 **generate–verify–refine**，用三阶段分解（ground truth → 反向造 query → 正向造 tool calls）+ 每阶段 **dynamic self-feedback**，用 **11K** 合成样本把 4B 非推理模式推到 BFCL **86.40%**。
> **攻坚线**：**架构思想（主）**——候选函数聚类、三阶段分解、阶段局部校验与重写；**评测字段（辅）**——BFCL non-live/live、ACEBench 五维、消融「无反馈 / 终滤 / 全闭环」、合成重试分布。
> **硬划界（开篇钉死）**：
> - **≠ [[ToRL工具集成强化学习]] ToRL**：禁止重写「代码解释器 ⊂ RL env、从 base 探索工具策略」。ToRL = **训练期交互 RL**（Sandbox Fusion + GRPO）；本篇 = **离线合成 function-calling 数据 → SFT**，评测是 BFCL/ACEBench **静态 schema 命中**，不是 AIME 解释器环。
> - **≠ [[智能体工具与长程任务]]**：禁止重写旗舰 System Card / MCP / Extended thinking with tools / 长程产品叙事；本篇只谈 **训练数据怎么造**。
> - **≠ [[代码智能体Harness史线]]**：禁止重写 SWE-agent ACI / OpenHands SDK / 生产沙箱 harness；本篇沙箱感止于「AST/规则查 JSON 合法性」，不是编码智能体命令面。
> **补链不升主**：**HEART**（arXiv:2609.01736）= Tool Primitives + ToolFace + Planner/Router/Verifier **推理期 harness**，与 ToolLoop「合成训练数据」正交 → **仅索引**，禁止展开成第二主轴。
> **谱系口径（笔记编辑位，非文内自号）**：文 Related Work 主对照 Self-Instruct / APIGen / APIGen-MT / ToolMind 等「合成→过滤」线；本卡用「**Toolformer 谱系**」指仓库横切的 **工具调用合成监督数据** 桶（学何时/调何工具），**不**声称正文自称 Toolformer 后继。
> **禁止编造**：机制、表数字、重试统计一律锚定官方 PDF（2026-09-22 CST）。图内未抽出的精确曲线点标 **待核实读图**。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主** | *ToolLoop: Closed-Loop Tool-Use Data Synthesis via Decomposed Generation and Dynamic Self-Feedback* | arXiv:**2609.09072v1** \[cs.CL\]（**8 Sep 2026**）；作者 Zeng, Liu, Cao, Chen, Li, Liu, Wen, Chen（**vivo AI Lab**） | `https://arxiv.org/abs/2609.09072` | **424K**（433,483 B） | **15** A4 | |
| **补链** | *Harness Engineering in LLM Tool Use via Agent-Native Reusable Tool Primitives*（HEART / Tool Primitives / ToolFace） | arXiv:**2609.01736v1** \[cs.SE\]（**1 Sep 2026**）；作者 Jin, Wang, Yu, Luo, Wang（UIUC / Starc） | `https://arxiv.org/abs/2609.01736` | **458K**（468,562 B） | **21** letter | |

| 材料 | 文内设置 / 入口（本篇不展开实现） |
|---|---|
| ToolLoop 基座 | **Qwen3-4B-Instruct-2507**（非 deliberative / non-reasoning 评测） |
| 嵌入 / 聚类 | **Qwen3-Embedding-8B**；**K=26**（约每簇 200 API） |
| 语义校验器 | **Qwen-Max**（三阶段共用 LLM judge） |
| API 池 | ToolBench + BFCL 子集，共 **5,281** 可执行 API；训练框架 **swift**；节点 **4× L40s 48GB**；seq **16k**；**2 epochs** |
| 合成规模 | 保留 **11,024** 例（文称 **11K**）；Isolate 去 BFCL 重叠候选后约 **10K** |
| HEART（补链） | ToolFace **25,519** 函数；Planner–Router–Verifier；**不**作本卡方法主写 |

**体积判定（2026-09-22 CST，`ls -lh`）：** ToolLoop **424K**、HEART **458K**，均 **<20MB** → 按 Wave10 规矩 ****。

**一句话抓手：**
- **ToolLoop**：先抽「该调哪些函数名」当地真 → **反向**造自然 query → **正向**造 OpenAI 格式 tool calls；每步用 **LLM 语义 + 规则 + AST** 验不过就带 issue 重写（最多 3 次），从「造完再滤」改成「边造边修」。
- **相对 APIGen 类基线**：11K 例上 4B 达 BFCL **86.40%**（Isolate **86.07%**），超过 60K APIGen-4B 的 **83.11%**；ACEBench overall **72.1%**，数据量约为 APIGen 的 **18.3%**。
- **HEART**：推理期自然语言 Tool Primitive + 大库检索 harness——**补链正交**，不抢主轴。

---

## 二、议题边界：只写「闭环合成 FC 数据」，不写 RL 工具环 / 产品长程 / ACI

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[ToRL工具集成强化学习]] ToRL** | 「工具调用可以是可学习策略」这一直觉相邻 | 解释器进 RL rollout、code ratio、AIME 无工具 vs 有工具对照全文 |
| **[[智能体工具与长程任务]]** | BFCL / 工具增强是产品能力切片的上游数据问题 | MCP 史、System Card 长程、extended thinking with tools |
| **[[代码智能体Harness史线]]** | 「格式/执行失败要被看见」的工程直觉 | SWE-agent 命令面、OpenHands 四包 SDK、生产失败率 |
| **经典合成（Self-Instruct / APIGen）** | generate-then-filter 是文内反面教材与 Table 对照 | 各家数据集构造通史 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| 三阶段分解 + 阶段局部 self-feedback；候选 K-means；OpenAI FC schema | ToRL 式「env 里探索何时写码」；多轮 agent 轨迹 RL |
| BFCL / ACEBench 表数字；消融；重试分布；Isolate 防泄漏 | 旗舰并行 tool call 产品叙事；SWE-bench resolve harness |
| HEART 一行：推理 harness / Tool Primitive（补链） | HEART Planner–Router–Verifier 全文、ToolFace 检索算法 |

跟读口诀：

`
[[ToRL工具集成强化学习]] ToRL = 训练期：工具 ⊂ RL 环境（数学解释器）
[[代码智能体Harness史线]] = 运行期：编码 ACI / 生产 SDK
[[智能体工具与长程任务]] = 产品期：旗舰工具环 / 长程叙述
[[ToolLoop工具数据合成]] = 数据期：单轮 FC 合成 — generate–verify–refine
HEART(补) = 运行期：NL Tool Primitive + harness（≠ 数据合成）
`

### 2.3 文内问题立轴（跟读）

作者批评现有合成（§1）三病：

1. **一次生成难选对工具**：候选多、场景杂，单次出完整样本易错。
2. **静态终滤 = 二值丢弃**：坏样本直接扔，不给修正信号 → 保留集特征偏斜。
3. **缺中间监督**：query 与 tool call 是否逻辑一致，生成过程中无人管。

范式迁移（Figure 1）：

`
旧：LLM 一次造 Query+Calls → Filter → 丢弃 / 保留
新：Sample GT → Backward Query → Forward Calls
 每步 Self-Feedback（验不过 → 带 issue 重写，≤3）
`

---

## 三、方法：候选构造 + 三阶段闭环

### 3.1 场景覆盖（§3.1）

单轮四类（与 BFCL 切分对齐）：

| 场景 | 含义 |
|---|---|
| **Simple** | 给定单函数，调一次 |
| **Multiple** | 多候选，只需选对一个 |
| **Parallel** | 同一函数多次独立并行调用 |
| **Parallel Multiple** | 多候选里选若干，可并行多次 |

### 3.2 候选函数构造（§3.2）

1. 函数描述 → 向量嵌入；
2. **K-means** 分簇（同域 / 同用法）；
3. 簇内再由 LLM 采样出该次合成的 **candidate functions**。

实验设定（§4.1）：5,281 API → **K=26**；Figure 3 给域分布饼图（Data Query / Travel / Code 等；精确扇区百分比 **待核实读图**）。

### 3.3 三阶段分解（§3.3）

| 阶段 | 输入 → 输出 | 约束要点（文内） | 校验组合 |
|---|---|---|---|
| **1 Ground Truth Sampling** | 候选 → **函数名序列**（将调用谁） | 可并行无依赖；场景连贯；并行类 **2–4** 次调用（可同名重复）；Simple/Multiple 单目标 | LLM 语义 + 规则格式 |
| **2 Backward Query** | GT + 候选 → **自然语言 query** | 意图与 GT **精确对齐**（不多不少）；参数与签名一致；信息完备；自然口语 | LLM 语义 |
| **3 Forward Tool Calls** | query + 候选 → **带参 tool calls** | Schema 合规；功能准确；**OpenAI function-calling** 格式 | LLM 语义 + 规则 + **AST** |

跟读：Stage 1 钉「**答什么工具组合**」；Stage 2 反推「**用户会怎么问**」；Stage 3 前推「**调用串怎么填参**」——中间态显式，错误可归阶段。

非并行场景 Stage 1 可 **随机采样** 目标函数；并行场景由 LLM 选可并行组合。

### 3.4 Dynamic Self-Feedback（§3.3.4）

- **失败时重写提示**含：原生成提示 + 失败输出（负例）+ **具体 issue**（例：AST「arguments 括号不匹配」），而非笼统 invalid。
- **迭代**：初始生成 + 最多 **3** 次反馈重生；全过 → 进下一阶段；满次仍挂 → **丢弃**。
- 设计动机：终滤易扔掉「难但可修」样本，偏向短 query / 简单 schema；闭环则在 GT 已定后**修** query/calls，而不是整段重掷。

---

## 四、实验与评测字段

### 4.1 设置摘要（§4.1）

| 项 | 文内 |
|---|---|
| 基座 | Qwen3-4B-Instruct-2507 |
| 对照 | 商用（GPT-5.2 / Gemini-3-Pro / Grok-4.1 / Claude-Opus-4.5 / Nova-2 等）、开源（Qwen3-32B、Llama-4-Scout、Gemma-3-27B、GLM-4.6）、数据中心（**APIGen-4B 60K**、**ToolMind-4B 55K**） |
| 泄漏控制 | **ToolLoop-4B-Isolate**：合成前滤掉与 BFCL 评测候选重叠的函数 → **10K** |
| 推理设定 | **non-reasoning**：直接输出 benchmark 兼容 FC 格式，**禁止**额外 CoT 救场 |
| BFCL | v4；文称 last updated **2025-12-16**；2,501 测例；Simple / Multiple / Parallel / Parallel Multiple × non-live / live |

### 4.2 主结果 BFCL（Table 1）

| 模型（数据量） | Non-Live | Live | **Overall** |
|---|---:|---:|---:|
| Qwen3-4B-Instruct-2507（基座） | 87.88 | 76.39 | 82.14 |
| APIGen-4B（60K） | 89.90 | 76.31 | 83.11 |
| ToolMind-4B（55K） | 89.48 | 77.57 | 83.53 |
| **ToolLoop-4B-Isolate（10K）** | **91.08** | **81.05** | **86.07** |
| **ToolLoop-4B（11K）** | **91.29** | **81.50** | **86.40** |

要点（§4.2，跟读）：

- 相对 APIGen-4B **+3.29**、相对 ToolMind-4B **+2.87** overall；数据量约 **1/5–1/6**。
- Non-live Multiple **96.50%**、Parallel_Multiple **94.50%**；Isolate 在 Multiple 甚至 **97.00%**。
- Isolate 仅低全量 **0.33** 点 → 增益不像「背 BFCL 候选 schema」。
- Live-Parallel_Multiple：ToolLoop **79.17%** vs APIGen **83.33%**——文自注该 split 仅 **24** 例，差 **1** 个样本量级，**不宜做强类别结论**。

### 4.3 消融：过滤 ≠ 精炼（Table 2）

| 变体 | Non-Live | Live | Overall |
|---|---:|---:|---:|
| Base | 87.88 | 76.39 | 82.14 |
| w/o Feedback | 85.02 | 74.97 | **79.97**（相对 base **−2.17**，噪声有害） |
| w/ Final Filtering | 88.81 | 76.31 | 82.56 |
| **w/ Feedback（ToolLoop）** | **91.29** | **81.50** | **86.40** |

文内区分：终滤能扔掉畸形，但救不了「query / GT / 参数各自看似合理却互不一致」；阶段反馈在错误传播前纠偏。

### 4.4 ACEBench 泛化（Table 3）

| 模型 | Overall | Atom | Single Turn | Similar API | Profile |
|---|---:|---:|---:|---:|---:|
| Base | 64.9 | 68.0 | 59.5 | 68.0 | 64.0 |
| APIGen-4B（60K） | 67.0 | 76.0 | 62.0 | 76.0 | 54.0 |
| ToolMind-4B（55K） | 70.2 | 83.3 | **69.5** | 74.0 | 54.0 |
| **ToolLoop-4B（11K）** | **72.1** | **84.0** | 66.5 | **78.0** | 60.0 |

- overall 相对 APIGen **+5.1**，数据量约其 **18.3%**；相对 ToolMind **+1.9**、约其 **1/5**。
- 弱项：Single Turn 落后 ToolMind；Profile 上所有微调都低于 base（文释：合成未显式建模个性化偏好），ToolLoop **60.0** 仍高于两数据基线的 **54.0**。

---

## 五、合成效率与校验器可信度（§5）

### 5.1 重试分布（Table 4）与成本

在保留的 **11,024** 例上（各阶段计数之和）：

| 阶段 | 0 retry | 1 | 2 | 3 |
|---|---:|---:|---:|---:|
| Stage 1 GT | 10720 | 114 | 161 | 29 |
| Stage 2 Query | 9029 | 1108 | 530 | 357 |
| Stage 3 Calls | 10257 | 299 | 298 | 170 |

- Stage 2 最难：约 **18.1%** 至少重试一次——「符号计划 → 自然语言」最易漏参 / 多暗示工具 / 场景漂移。
- Stage 3 相对轻：query 对齐后，规则+AST 护栏下 schema 落地更容易。
- 满 3 次仍废：**280** 例（192 语义反复挂、83 规则挂、5 双挂）—相对 11K 保留集很小。
- Token 账（Qwen tokenizer）：输入 **26.13M** + 输出 **7.28M** = **33.41M**；并行类因 LLM 造链、组合更长而最贵。

### 5.2 数据类别分布（Appendix A / Figure 4）

| 类别 | 数量 | 占比 |
|---|---:|---:|
| Simple | 4,453 | 40.4% |
| Parallel | 3,634 | 33.0% |
| Multiple | 1,783 | 16.2% |
| Parallel Multiple | 1,154 | 10.5% |
| **合计** | **11,024** | 100% |

### 5.3 Verifier（§5.2）

- 三阶段语义裁判均为 **Qwen-Max**。
- 人工抽 **100** 例比对：**94%** 一致——文自定位为 **sanity check**，非全错误类型标定。
- 分歧多为类型约束（schema 要 int、生成给了带小数 float）与少量语义落地（地名粒度）；前者可靠规则/AST 补，后者 AST 不够。

---

## 六、局限（文内 Limitations）

1. **无真实环境反馈**：超时、畸形 API 回包、ground-truth 级联失败等 **未**进合成与静态评测；真实工具用常依赖执行结果迭代——当前协议未测。
2. **单一语义裁判**：Qwen-Max 可能有模型相关 / 相关偏置；需独立裁判对比、阶段级校准，并接入可执行环境。

Ethics：合成数据、不采 PII；人工标只标合成例；API 规格与基准公开。

---

## 七、补链 HEART（2609.01736）——仅索引

| 项 | 一文摘要（禁止当本卡主方法展开） |
|---|---|
| 问题 | 多步/多轮工具因 **异构 schema / 输出类型** 易脆；大工具目录塞进上下文掉点 |
| 组件 | **Tool Primitives**（NL 接口包住 schema 解析与执行）；**ToolFace**（**25,519** 函数库，动态检索）；**HEART** harness（Planner / Router / Verifier） |
| 与 ToolLoop | ToolLoop = **训练数据闭环合成**；HEART = **推理期编排与接口抽象** → 正交；同属「工具」近窗，**划界为补链** |

---

## 八、跟读清单（验收自检）

- [ ] 开篇划界：≠ [[ToRL工具集成强化学习]] / ≠ [[智能体工具与长程任务]] / ≠ [[代码智能体Harness史线]]；HEART 仅补链
- [ ] 范式：generate-then-filter → generate–verify–refine；三阶段 + ≤3 重写
- [ ] 数字锚：11K / 86.40% / Isolate 86.07%；消融 79.97→82.56→86.40；ACE 72.1% @ 18.3% 数据
- [ ] 未把 ToRL RL 环、旗舰 MCP、SWE ACI 写进主轴
- [ ] PDF：`ls -lh` 主 **424K**、补 **458K**，均可二进制入库

**结论句：** ToolLoop 把 Toolformer 谱系里「造 FC 监督数据」的瓶颈，从「多造再滤」拧到「**先钉函数组合、再反向问句、再正向填参，且每步可修**」——用更少样本换更高 BFCL/ACEBench 一致性；它解决的是 **数据对齐**，不是 [[ToRL工具集成强化学习]] 的 **RL 探索**，也不是 [[代码智能体Harness史线]]/[[智能体工具与长程任务]] 的 **运行时 harness / 产品长程**。
