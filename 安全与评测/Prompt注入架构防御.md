---
title: "Prompt injection 架构防御：CaMeL + StruQ（≠ 红队通史 / ≠ 多模态越狱）"
topic: Prompt注入架构防御
date: 2026-09-22
lines: [架构思想, 系统接口, 安全—效用字段]
status: archived
sources:
 - https://arxiv.org/abs/2402.06363 # 0.64MiB / 20p；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2503.18813
 - https://arxiv.org/pdf/2503.18813
 - https://arxiv.org/abs/2402.06363
 - https://arxiv.org/pdf/2402.06363
 - https://arxiv.org/abs/2503.00061
 - https://arxiv.org/pdf/2503.00061
 - https://github.com/google-research/camel-prompt-injection
 - https://github.com/Sizhe-Chen/StruQ
 - https://github.com/uiuc-kang-lab/AdaptiveAttackAgent
arxiv: ["2503.18813", "2402.06363", "2503.00061"]
related: ["B5", "多模态越狱与OmniSafe", "审慎对齐与断路器", "宪法分类器防御", "SHADEArena隐瞒与监控", "智能体工具与长程任务"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# Prompt injection 架构防御：CaMeL + StruQ（≠ 红队通史 / ≠ 多模态越狱）

> **定位**：**收口横切**——仓库安全轴已有 **攻击/红队/越狱/分类器护栏/表征熔断/隐瞒评测**，缺的是「**即使底层模型可被注入，系统层仍可约束控制流与数据外泄**」的 **by-design 防御主文**。对照两条正交架构路线：
> - **CaMeL**（*Defeating Prompt Injections by Design*，arXiv:**2503.18813**v2，页眉 **24 Jun 2025**）：能力标记 + 控制/数据流提取 + 自定义解释器策略强制——**系统层脚手架**，不改底层 LLM。
> - **StruQ**（*StruQ: Defending Against Prompt Injection with Structured Queries*，arXiv:**2402.06363**v2，页眉 **25 Sep 2024**；USENIX Security 2025）：prompt/data **双通道结构化查询** + 安全前端 + **结构化指令微调**——**模型 API / 训练接口**改造。
> **补链（不升主）**：**Adaptive Attacks…**（arXiv:**2503.00061**v2，页眉 **4 Mar 2025**）——说明检测/提示/微调类防御在自适应评测下脆弱；**只作动机补链**，不立主轴。
> **攻坚线**：**架构思想 / 系统接口（主）** + **文内 AgentDojo / AlpacaEval 等安全—效用汇总字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ B5**：禁止重写红队通史、众包协议、ASR 闭环与攻击面地图。
> - **≠ [[多模态越狱与OmniSafe]]**：禁止写成多模态越狱 / MMJail / OmniSafe。
> - **≠ [[审慎对齐与断路器]]**：禁止重写 Deliberative Alignment / Circuit Breakers 表征熔断对齐范式。
> - **≠ [[宪法分类器防御]]**：禁止重写 Constitutional Classifiers 部署侧分类器护栏工程。
> - **≠ [[SHADEArena隐瞒与监控]]**：禁止重写 SHADE-Arena sabotage×monitor 双角色评测（AgentDojo 在本篇只作 **CaMeL 评测入口**，不展开隐瞒/破坏剧本）。
> - **禁止写成注入攻击百科**：不枚举攻击族配方、不侧写可复现注入/越狱步骤或载荷；评测轴只保留 **族名 + 聚合 ASR/效用数字**。
> **禁止编造**：主张与表数字一律锚定本地抽取（2026-09-22 CST）与 arXiv 元数据。文内未列表的读图点不外推。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A · CaMeL** | Debenedetti, Shumailov, Fan, Hayes, Carlini, Fabian, Kern, Shi, Terzis & Tramèr (Google / DeepMind / ETH Zurich), *Defeating Prompt Injections by Design* | arXiv:**2503.18813v2** \[cs.CR\] **24 Jun 2025**；XMP MetadataDate 2025-06-25T00:35:04Z（→ **2025-06-25 08:35 CST**）；CC-BY-4.0；官方 PDF：https://arxiv.org/pdf/2503.18813；（**125** 页 A4 / **5,531,468 B ≈ 5.53MiB**） | 主锚：系统层控制/数据流 + capability 策略 |
| **主文 B · StruQ** | Chen, Piet, Sitawarin & Wagner (UC Berkeley), *StruQ: Defending Against Prompt Injection with Structured Queries* | arXiv:**2402.06363v2** \[cs.CR\] **25 Sep 2024**；CreationDate **2024-09-27 08:08 CST**；`https://arxiv.org/abs/2402.06363`（**644,650 B ≈ 0.64MiB** / **20** 页 letter）；USENIX Security 2025 | 主锚：结构化查询 API + 结构化指令微调 |
| **补链 · Adaptive Attacks** | Zhan, Fang, Panchal & Kang, *Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents* | arXiv:**2503.00061v2** \[cs.CR\] **4 Mar 2025**；CreationDate **2025-03-05 09:28 CST**；官方 PDF：https://arxiv.org/pdf/2503.00061；（**17** 页 A4 / **3,621,352 B ≈ 3.62MiB**） | 补链：启发式/检测类防御脆弱性；**不升主** |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| CaMeL PDF | （仅 arXiv 链接） | **≈5.53MiB** | **125** | （>80 页；议程「强烈建议正式外链」） |
| StruQ PDF | `https://arxiv.org/abs/2402.06363` | **0.64MiB** | **20** | **官方 HTTPS 外链**（≪10MB；页数适中） |
| StruQ 抽取 | | ≈134K | — | 全文检索 |
| Adaptive PDF | （仅 arXiv 链接） | **≈3.62MiB** | **17** | **可链可不入二进制**；补链不升主 |
| Adaptive 抽取 | | ≈81K | — | 可选瘦身检索 |

**代码入口（文内 / USENIX 明示，2026-09-22 未做线上可用性核验）：**
- CaMeL：`https://github.com/google-research/camel-prompt-injection`
- StruQ：`https://github.com/Sizhe-Chen/StruQ`（USENIX 页与作者仓）
- Adaptive（补链）：`https://github.com/uiuc-kang-lab/AdaptiveAttackAgent`

**一句话抓手：**
B5/[[宪法分类器防御]]/[[审慎对齐与断路器]] 等回答「如何评攻击、如何在模型内或护栏层挡越狱」；本卡回答「**如何在架构上把不可信数据从控制平面拆开**」——CaMeL 用 **P-LLM 只见可信查询写计划 + Q-LLM 无工具解析不可信数据 + capability 在工具调用点强制策略**；StruQ 用 **双通道结构化查询 + 保留分隔符前端过滤 + 只服从 prompt 通道的指令微调**。二者正交、可叠加（CaMeL 文亦称可与使模型更鲁棒的方法联用）。

---

## 二、议题边界：架构防御 ≠ 攻击通史 / ≠ 分类器 / ≠ 熔断 / ≠ 隐瞒评测

### 2.1 五向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **红队 / 对抗评测通史** | 流程、众包、ASR 闭环 | **B5** | **否** |
| **多模态越狱** | MMJail / OmniSafe | **[[多模态越狱与OmniSafe]]** | **否** |
| **对齐范式（规范推理 / 表征熔断）** | Deliberative + Circuit Breakers | **[[审慎对齐与断路器]]** | **否** |
| **部署侧分类器护栏** | Constitutional Classifiers | **[[宪法分类器防御]]** | **否** |
| **sabotage×monitor 评测** | SHADE-Arena | **[[SHADEArena隐瞒与监控]]** | **否**（AgentDojo 仅作 CaMeL 数字入口） |
| **Agent 工具长程** | 工具环 / computer-use | **[[智能体工具与长程任务]] / [[计算机使用智能体]]** | **否**（只取「不可信工具结果」接口一句） |
| **注入架构防御** | 系统层隔离 + 结构化查询 | **本篇** | **是** |

跟读直觉：[[宪法分类器防御]] 问「**serving 旁路分类器如何挡**」；[[审慎对齐与断路器]] 问「**权重内嵌推理/表征如何阻有害轨迹**」；本卡问「**控制流与数据流如何在系统设计上不可被不可信内容劫持**」——共享「安全」词汇，但 **干预层是系统/API/解释器，不是攻击剧本或模型内对齐全文**。

`
 安全相关已入库
 │
 ┌─────────┼─────────┬──────────┬──────────┐
 │ │ │ │ │
 B5 [[多模态越狱与OmniSafe]] [[审慎对齐与断路器]] [[宪法分类器防御]] [[SHADEArena隐瞒与监控]]
 红队通史 多模态越狱 对齐范式 分类器护栏 隐瞒评测
 │ │ │ │ │
 └─────────┴────┬────┴──────────┴──────────┘
 │ 禁止复述
 ▼
 ★ [[Prompt注入架构防御]] 架构防御（CaMeL ⊕ StruQ）
 ▲
 │ 补链动机（不升主）
 Adaptive Attacks（2503.00061）
`

### 2.2 威胁设定（只记接口，不记配方）

两文共享的工程设定（意译压缩）：

| 字段 | 含义（架构接口） |
|---|---|
| **可信方** | 应用开发者给出的 **prompt / 用户查询**（CaMeL 另假定用户查询与未污染记忆可信） |
| **不可信方** | 工具返回、文档、邮件、网页等 **data 通道** |
| **攻击者能力（威胁模型摘要）** | 可任意改写 data；**不能**改写应用 prompt / 计划通道（CaMeL：不能改 P-LLM 所见查询） |
| **成功判据（评测接口）** | 模型/agent **服从 data 中隐藏指令**或执行 **策略外工具调用 / 外泄**（各文用各自基准的聚合指标；本篇不展开判据细则） |
| **与 jailbreak 的划界（StruQ §2）** | jailbreak：用户 vs 提供商安全规范；**prompt injection**：应用开发者意图 vs 不可信数据源——安全对齐过滤 **不能**直接当注入防御 |

**补链一句（Adaptive，不升主）：** 针对 **检测器 / 提示隔离 / sandwich / 对抗微调** 等八类防御，文称在自适应评测下 **ASR-adaptive 均可 >50%**（InjecAgent 子集；Vicuna-7B prompted agent 与 Llama3-8B finetuned agent）。结论接口：仅靠启发式与检测 **不足以** 充当唯一防线 → 抬升本卡「架构 by design」动机。**本篇不转述其攻击优化步骤。**

---

## 三、范式对照：系统层脚手架 vs 结构化查询 API

| | **CaMeL** | **StruQ** |
|---|---|---|
| **干预层** | Agent **运行时**：P-LLM / Q-LLM / 解释器 / 工具策略 | LLM **输入 API + 微调**：前端编码 + 结构化指令微调 |
| **是否改模型权重** | **否**（策略与解释器在外围） | **是**（从 base 模型做 structured instruction tuning） |
| **控制流保护** | 仅从可信查询提取计划（代码）；不可信数据 **不得改写程序流** | 模型被训成 **只执行 prompt 通道指令** |
| **数据流保护** | 每值带 **capability**（来源 / 允许读者）；工具调用前跑 **security policy** | 前端 **过滤保留分隔符**；data 通道指令在训练目标中被忽略 |
| **Dual-LLM** | **显式实例化** Willison 模式（P 规划、Q 无工具解析） | 单模型；通道分离在编码格式中 |
| **主要评测** | **AgentDojo**（效用 % + 成功攻击计数） | **AlpacaEval** 效用 + 多族 ASR（Llama/Mistral-7B） |
| **provable / by-design 主张** | 策略违反路径可拦；文称 AgentDojo 安全评测 **by design** 解决（仍承认侧信道等非目标） | 手工族 ASR 大幅下降；对优化族 **未完全免疫** |
| **局限（文内）** | 非目标含：无数据流后果的纯文本篡改、需人确认的歧义流；侧信道；策略编写与用户疲劳 | 不覆盖开放多轮聊天机器人；对强优化攻击仍有残差 ASR |

---

## 四、架构 A：CaMeL（2503.18813）

### 4.1 核心主张（系统接口）

摘要 / §1 / §5：在 agent 外围加一层 **不修改底层 LLM** 的保护环境——

1. **P-LLM（Privileged）**：只读 **可信用户查询**，输出表达任务意图的 **受限 Python 子集代码**（计划 = 控制流 + 数据依赖）；**看不到**工具返回内容。
2. **Q-LLM（Quarantined）**：以函数形式被计划调用；**无工具**；把不可信非结构化数据解析为给定 schema 的结构化输出（另含 `have_enough_information` 布尔；不足则抛错并由 P-LLM 修代码——**禁止**把「缺什么信息」明文回传 P-LLM，以免成注入向量）。
3. **CaMeL 解释器**：执行计划、维护 **数据依赖图**、在工具调用前强制 **security policies**。
4. **Capabilities**：挂在每个值上的元数据（来源：User / CaMeL / 某工具及 inner source；允许读者：`Public` 或邮箱集合等）；工具也可按语义标注（如云盘文档编辑者）。
5. **Security policies**：Python 可调用函数；输入工具名与参数（含 capability）；输出 Allowed / Denied + 理由。违规 → 阻断或 **要求用户确认**（文述产品路径）。

相对「只隔离 Dual-LLM」：即使计划固定，**工具参数仍可能被 Q-LLM 在不可信数据上扭曲**（类比「改查询参数的注入」）；capability + 策略挡住 **未授权数据流上的外泄/副作用工具**。

### 4.2 流水线（Fig.5 意译）

`
可信用户查询
 ↓
P-LLM：生成受限 Python 计划（含对 Q-LLM / 工具的调用骨架与 schema）
 ↓
CaMeL 解释器执行
 ├─ 工具返回值 → 写入变量并打上 capability / 依赖边
 ├─ Q-LLM(schema, 不可信片段) → 结构化字段（仍带依赖）
 └─ 每次 tool(args) 前：policies.check(tool, args, mem)
 ├─ Denied → 停 / 请用户确认
 └─ Allowed → 执行，更新 Trace 与 mem
`

**解释器模式（§5.4）：** `NORMAL` vs `STRICT`——STRICT 把控制流条件/迭代对象加入块内赋值依赖，用于压低 **间接依赖侧信道**（§7）；代价是策略触发更频（附录 Table 8：总体 NORMAL **33.87%** vs STRICT **53.23%**，良性设定下）。

**显式非目标（§3.1，只记边界）：** 不声称防御「无控制/数据流后果」的纯展示层篡改；不追求零人介入全自主；侧信道（异常停机、时序等）文内单列讨论——**强化相对现状，而非宣称绝对无泄漏**。

### 4.3 安全—效用字段（AgentDojo；只录表内汇总）

**摘要句：** 在 AgentDojo 上，CaMeL 在 **可证明安全** 前提下完成约 **77%** 任务，对照无防御系统约 **84%**（摘要；与 Table 2 中 o3 High：Native **84.5%** → CaMeL **77.3%** 同量级）。

#### 4.3.1 效用（Table 2，良性；Overall）

| 模型 | Native Tool Calling | CaMeL | ∆ |
|---|---:|---:|---:|
| Claude 4 Sonnet | 86.6% ± 6.8 | 74.2% ± 8.7 | −12.4% |
| Claude 4 Sonnet*（推理） | 83.5% ± 7.4 | 70.1% ± 9.1 | −13.4% |
| Gemini 2.5 Flash | 55.7% ± 9.9 | 35.1% ± 9.5 | −20.6% |
| Gemini 2.5 Pro | 73.2% ± 8.8 | 41.2% ± 9.8 | −32.0% |
| **o3 High** | **84.5% ± 7.2** | **77.3% ± 8.3** | **−7.2%** |
| o4 Mini High | 79.4% ± 8.1 | 76.3% ± 8.5 | −3.1% |

文注：Travel 套件因工具输出文档不足，部分模型 CaMeL 效用掉幅大；较新模型更多用 Q-LLM 补解析。Claude 4 Sonnet + Haiku Q-LLM：效用约 **−1%**，中位任务成本约 **−12%**（§6.1.3）。

#### 4.3.2 攻击下效用（Table 3，Overall 摘录）

| 模型 | Native | CaMeL | ∆ |
|---|---:|---:|---:|
| Claude 4 Sonnet | 80.1% | 75.7% | −4.4% |
| o3 High | 79.0% | 79.8% | **+0.7%** |
| Gemini 2.5 Pro | 58.0% | 45.3% | −12.6% |

#### 4.3.3 成功攻击计数（Table 4；文称共 **949** 次攻击设定）

| 模型 | Native（Overall） | CaMeL（no policies） | CaMeL（含策略） |
|---|---:|---:|---:|
| Claude 4 Sonnet | 75 ± 58.6 | 13 ± 6.0 | 11 ± 4.5 |
| Gemini 2.5 Flash | 297 ± 268.7 | 1 | 1 |
| Gemini 2.5 Pro | 163 ± 140.1 | **0** | **0** |
| o3 High | 11 ± 4.5 | 1 | **0** |
| o4 Mini High | 2 | 1 | 1 |

文解释：残差「成功」中有一类 **并非 prompt injection**（展示层把不可信评论文本打给用户即命中基准检查），属 §3.1 非目标；可用依赖图在 UI 上 **高亮来源**。

#### 4.3.4 与 AgentDojo 内启发式防御对照（Claude 3.5 Sonnet；Table 5 / 7）

| 防御 | 效用 Overall（Table 5） | 成功攻击数 Overall（Table 7） |
|---|---:|---:|
| Undefended | 90.72% | 44 ± 31.3 |
| Spotlighting | 92.78% | 5 ± 0.6 |
| Prompt Sandwiching | 89.69% | 24 ± 14.5 |
| Tool Filter | 73.20% | 8 ± 2.5 |
| **CaMeL** | 63.92% | **0 ± 0.0** |
| CaMeL (no policies) | — | 1 ± 0.0 |

文强调：CaMeL 换的是 **可验证策略保证**，不是单纯「压 ASR 同时保最大效用」；启发式在自适应提示下可能塌陷（文引 US-AISI 2025）。GPT-4o mini 的 instruction hierarchy **单独**仍在 AgentDojo 上有大量成功攻击；**加 CaMeL 后文称 0**。

#### 4.3.5 开销（§6.5）

相对原生 tool-calling（Claude 3.5 Sonnet 骨干；tiktoken 估）：中位任务约 **2.82×** 输入 token、**2.73×** 输出 token。Spotlighting 约 1.06× 输入——更便宜但无同类保证。

### 4.4 失效模式接口（Table 1 类别名；不写任务剧本）

文对 Claude 的失败归类（架构相关）：**Data requires action**（行动取决于仅 Q 可见的数据）、**Not enough context for Q-LLM**、**Underdocumented API**、P-LLM 错误假设等。含义：Dual-LLM 隔离会牺牲「计划必须读不可信内容才能分支」的任务——需更严策略下的嵌套规划工具等未来件，而非回到单通道。

---

## 五、架构 B：StruQ（2402.06363）

### 5.1 核心主张（API 接口）

§4：把 LLM API 从「单字符串混控」改为 **structured query = (prompt, data)** 双参数——类比 SQL prepared statement / 电话信令与话音分离的经典修复模式（§2 注入史只作类比，**不展开攻击史**）。

系统两件套：

1. **Secure front-end**
 - 用 **保留特殊 token** 编码分隔（文：`[MARK]` / `[INST]` / `[INPT]` / `[RESP]` / `[COLN]` 等，替代 Alpaca 风格文本分隔）。
 - **过滤**用户 data 中对这些保留串（及文述额外模式）的仿造，使 Completion 类「伪分隔」无法在 token 层伪造成控制标记。
 - 新 token 嵌入 **用对应文本 token 初始化**再微调（文：随机初始化会严重伤效用）。

2. **Structured instruction tuning**
 - 从 **非指令微调 base** 出发（文鼓励提供商开放 base）。
 - 训练集约 **50% 干净** + **25% Naive 位错指令** + **25% Completion-Other 风格位错**（算法级描述见文 Algorithm 1；**本篇不抄注入句模板**）。
 - 目标响应始终服从 **prompt 通道** 指令，忽略 data 通道指令。

### 5.2 安全—效用字段（只录聚合）

**模型：** Llama-7B、Mistral-7B；全参微调 3 epoch；效用 **AlpacaEval 1.0**（vs davinci003 win rate）；安全：对各攻击族在 208 条含 data 的 AlpacaFarm 样本上的 **ASR↓**（成功 = 把注入指令当新指令执行；人工排除假阳性）。

#### 5.2.1 效用（Table 3）

| | Llama Undef. | Llama StruQ | Mistral Undef. | Mistral StruQ |
|---|---:|---:|---:|---:|
| AlpacaEval (↑) | 67.2% | **67.6%** | 80.0% | 78.7% |

#### 5.2.2 安全汇总（Table 2；ASR↓；摘关键手工族与优化族）

| 攻击族（文内名称） | Llama Undef. | Llama StruQ | Mistral Undef. | Mistral StruQ |
|---|---:|---:|---:|---:|
| Naïve / Ignore / Escape-* | 2–12% | **0%** | 1–11% | **0%** |
| Completion-Other / OtherCmb | 29–41% | **0%** | 71–77% | **0%** |
| Completion-Real / RealCmb | 71–96% | **0–2%** | 83–96% | **0–2%** |
| HackAPrompt | 52% | **0%** | 38% | **0%** |
| Tree-of-Attack (TAP) | 97% | **9%** | 100% | **36%** |
| GCG | 97% | **58%** | 99% | **56%** |

文结论接口：手工与 Completion 族可压到极低；**任务相关的优化攻击**仍有残差 → 结构化查询是方向而非终点。与 BIPIA 对照（Table 7）：StruQ 在效用与跨测试集泛化上更稳；BIPIA 在文内设定下 AlpacaEval **53.9%→26.0%**，且 GCG 仍可达 **100%** ASR。

**范围（§6）：** 面向 **程序化应用 API**；不适用于终端用户不愿标注「哪段是指令/数据」的开放多轮聊天；不声称防 jailbreak / 训练数据抽取等其它威胁。

---

## 六、两条路线如何拼进工程栈（接口级）

`
 不可信工具/检索结果
 │
 ┌────────────────────┼────────────────────┐
 │ │ │
 ▼ ▼ ▼
 [可选] StruQ 式 CaMeL 解释器 [可选] [[宪法分类器防御]]
 双通道编码+ P/Q + capability 分类器护栏
 结构化指令模型 策略在 tool 边界 （部署旁路）
 │ │ │
 └────────────┬───────┴────────────────────┘
 ▼
 应用副作用 / 外发通道
`

| 若你的约束是… | 更贴哪条 |
|---|---|
| 不能改权重 / 要多模型热插拔 / 要策略可审计 | **CaMeL** |
| 能从 base 微调、API 可改成双参数、要压应用内注入 ASR | **StruQ** |
| 只要提示/检测器 | **不足**（见 Adaptive 补链；且 CaMeL Table 7 启发式仍有成功攻击） |
| 要挡的是越狱违规内容而非应用控制流 | → **[[审慎对齐与断路器]] / [[宪法分类器防御]] / B5**，非本卡 |

**可组合性：** CaMeL §11 明确可与「提升模型自身鲁棒」的方法联用；StruQ 把 instruction hierarchy（Wallace et al.）视为多级推广。本库不把 hierarchy 升为本卡主文。

---

## 七、硬约束执行清单（写作自检）

| 禁止 | 本篇处理 |
|---|---|
| 可复现注入/越狱步骤、载荷、优化后缀、忽略指令句表 | **未收录**；攻击仅以 **族名 + ASR** 出现 |
| 注入攻击百科 / 红队通史 | 划界至 B5；§2 仅保留威胁模型接口表 |
| 多模态越狱 | → [[多模态越狱与OmniSafe]] |
| 分类器护栏 / 表征熔断 / SHADE 隐瞒剧本 | → [[宪法分类器防御]] / [[审慎对齐与断路器]] / [[SHADEArena隐瞒与监控]] |
| 编造 GitHub / 表数字 | 仅用文内与 USENIX/作者仓明示链接；数字出 Table 2–7 / 摘要 |

---

| 资产 | 建议 | 理由（2026-09-22 CST ） |
|---|---|---|
| CaMeL PDF | **链接 + ** | 125 页 / 5.53MB；议程 >80 页优先抽取 |
| StruQ PDF | **`https://arxiv.org/abs/2402.06363` 入库** | 20 页 / 0.64MB ≪10MB |
| Adaptive PDF | **可链；二进制可选不入** | 补链不升主；3.62MB |
| 本笔记 | 安全与评测/Prompt注入架构防御.md | status:**archived**；date:**2026-09-22** |

---

## 九、开放问题（文内，非外推）

1. **优化攻击残差（StruQ）** 与 **侧信道 / 策略疲劳（CaMeL）** 仍开放；二者都把「完全解决 prompt injection」明确标为否。
2. **形式化验证解释器与策略冲突消解**（CaMeL §10）；换用显式错误类型语言以减异常侧信道。
3. **提供商开放 base 模型**（StruQ）以便结构化指令微调；系统提示进入多级 structured query（与 instruction hierarchy 对齐）。
4. 本波收口后：与 [[宪法分类器防御]]/[[审慎对齐与断路器]] 的 **defense-in-depth** 拼装属维护期补注，不新开攻击百科波次。

---

**成稿路径：** `/workspace/AIResearch-drafts/安全与评测/Prompt注入架构防御.md
**入库二进制：** 仅 `https://arxiv.org/abs/2402.06363`（CaMeL / Adaptive 按议程不默认入库）。
