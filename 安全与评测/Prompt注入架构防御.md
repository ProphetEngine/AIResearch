---
title: "Prompt injection 架构防御：CaMeL + StruQ（≠ 红队通史 / ≠ 多模态越狱）"
topic: Prompt注入架构防御
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2503.18813
 - https://arxiv.org/abs/2402.06363
 - https://arxiv.org/abs/2503.00061
aux:
 - https://arxiv.org/abs/2503.18813
 - https://arxiv.org/abs/2402.06363
 - https://arxiv.org/abs/2503.00061
 - https://github.com/google-research/camel-prompt-injection
 - https://github.com/Sizhe-Chen/StruQ
 - https://github.com/uiuc-kang-lab/AdaptiveAttackAgent
arxiv: ["2503.18813", "2402.06363", "2503.00061"]
related: ["安全红队与对抗评测", "多模态越狱与OmniSafe", "审慎对齐与断路器", "宪法分类器防御", "SHADEArena隐瞒与监控", "智能体工具与长程任务", "计算机使用智能体"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# Prompt injection 架构防御：CaMeL + StruQ（≠ 红队通史 / ≠ 多模态越狱）

> **主要来源**：[Defeating Prompt Injections by Design](https://arxiv.org/abs/2503.18813)；[StruQ: Defending Against Prompt Injection with Structured Queries](https://arxiv.org/abs/2402.06363)；[Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents](https://arxiv.org/abs/2503.00061)（截至 2026-09-22）。下文「CaMeL §x」「StruQ §x」「Adaptive」分别指三文。
> **研究线**：架构思想与系统接口（主）——把不可信数据从控制平面拆开；安全—效用字段（辅）——AgentDojo、AlpacaEval 与各攻击族的聚合 ASR。
> **范围与相邻笔记**：
> - ≠ [[安全红队与对抗评测]]：本篇不写红队通史、众包协议、ASR 闭环与攻击面地图。
> - ≠ [[多模态越狱与OmniSafe]]：本篇不写多模态越狱。
> - ≠ [[审慎对齐与断路器]]：本篇不写规范推理与表征熔断的对齐范式。
> - ≠ [[宪法分类器防御]]：本篇不写部署侧分类器护栏。
> - ≠ [[SHADEArena隐瞒与监控]]：本篇不写 sabotage × monitor 评测，AgentDojo 只作 CaMeL 的评测入口。
> - 本篇不收注入攻击配方、可复现的注入或越狱步骤与载荷，评测只保留攻击族名与聚合数字。
> **意义**：检测器、提示隔离与对抗微调在自适应攻击下都可被击穿，两文因此改从架构入手：StruQ 把指令与数据分成两个通道并训练模型只听指令通道，CaMeL 不改模型，用可信计划、隔离解析与工具调用点的策略检查，让不可信内容无法改写控制流或把数据外泄。代价是效用与开销，两文也都明确没有「完全解决」prompt injection。

**一句话**：CaMeL 让只看可信查询的 P-LLM 写计划、无工具的 Q-LLM 解析不可信数据，再由解释器按 capability 在每次工具调用前检查策略；StruQ 用双通道结构化查询、过滤保留分隔符的前端，加上只服从 prompt 通道的指令微调。两者正交，可以叠加。

## 一、问题背景

LLM 应用把开发者的指令与外部数据（工具返回、文档、邮件、网页）拼进同一段输入，模型无法从格式上区分哪段是该执行的指令。攻击者只要能改写数据，就可能让模型服从藏在数据里的指令，或调用计划外的工具、外泄数据。两文共享的威胁设定如下：

| 字段 | 含义 |
|---|---|
| 可信方 | 应用开发者给出的 prompt 与用户查询（CaMeL 另假定未被污染的记忆可信） |
| 不可信方 | 工具返回、文档、邮件、网页等数据通道 |
| 攻击者能力 | 可任意改写数据，但不能改写应用 prompt 或计划通道 |
| 成功判据 | 模型服从数据中的隐藏指令，或执行策略外的工具调用与外泄 |

StruQ §2 区分了它与越狱：越狱是用户对抗提供商的安全规范，prompt injection 是不可信数据对抗应用开发者的意图，所以安全对齐的过滤不能直接当作注入防御。

## 二、脉络

- **经典类比**：StruQ 把问题比作 SQL 注入与电话信令混在话音里，经典修法是把控制与数据分开，如 SQL 的 prepared statement。
- **Dual-LLM 模式**：Willison 提出让一个模型做规划、另一个无工具的模型只处理不可信数据；CaMeL 显式实现了这一模式并补上了它的漏洞。
- **2024-02，StruQ**（UC Berkeley；USENIX Security 2025）：在模型 API 与训练层面实现通道分离。
- **2025-02，Adaptive**：针对检测器、提示隔离、sandwich、对抗微调等八类防御，在自适应评测下 ASR 都能超过 50%（InjecAgent 子集，Vicuna-7B prompted agent 与 Llama3-8B finetuned agent）。结论是只靠启发式与检测不能作为唯一防线。
- **2025-03，CaMeL**（Google、DeepMind 与 ETH Zurich）：在系统层实现「by design」的防御，用 AgentDojo 评测。

主线是从「让模型自己识别并拒绝注入」转向「在架构上让注入失去作用」：StruQ 改模型的输入接口，CaMeL 改模型外的运行时。

## 三、两条路线对照

| | CaMeL | StruQ |
|---|---|---|
| 干预层 | agent 运行时：P-LLM、Q-LLM、解释器、工具策略 | LLM 输入 API 与微调：前端编码、结构化指令微调 |
| 是否改权重 | 否，策略与解释器在模型外 | 是，从 base 模型做结构化指令微调 |
| 控制流保护 | 只从可信查询提取计划，不可信数据不能改写程序流 | 模型被训练成只执行 prompt 通道的指令 |
| 数据流保护 | 每个值带 capability（来源与允许的读者），工具调用前执行安全策略 | 前端过滤保留分隔符，数据通道中的指令在训练目标里被忽略 |
| 主要评测 | AgentDojo：效用与成功攻击计数 | AlpacaEval 效用与多族 ASR（Llama / Mistral-7B） |
| 主张 | 违反策略的路径可拦截，AgentDojo 的安全评测「by design」解决，但承认侧信道等非目标 | 手工攻击族 ASR 大幅下降，对优化攻击未完全免疫 |

## 四、CaMeL：系统层的能力与策略

### 4.1 机制

CaMeL 在 agent 外围加一层不修改底层 LLM 的保护环境（CaMeL §5）：

1. **P-LLM（特权模型）**：只读可信的用户查询，输出受限 Python 子集写成的计划，即控制流与数据依赖；看不到工具返回的内容。
2. **Q-LLM（隔离模型）**：被计划以函数形式调用，没有工具，只把不可信的非结构化数据解析成给定 schema 的结构化输出。信息不足时抛错，由 P-LLM 修改代码，但不把「缺什么信息」明文回传 P-LLM，以免成为新的注入通道。
3. **解释器**：执行计划，维护数据依赖图，在每次工具调用前强制执行安全策略。
4. **Capabilities**：挂在每个值上的元数据，记录来源（用户、CaMeL 或某个工具）与允许的读者（公开或特定邮箱集合等）。
5. **安全策略**：以工具名与带 capability 的参数为输入、输出允许或拒绝的 Python 函数；违规时阻断或请用户确认。

只做 Dual-LLM 隔离还不够：即使计划固定，Q-LLM 仍可能在不可信数据的影响下扭曲工具参数（类似「改查询参数」的注入）。capability 与策略挡住的正是这类沿未授权数据流发生的外泄与副作用。

解释器有 NORMAL 与 STRICT 两种模式（CaMeL §5.4）。STRICT 把控制流的条件与迭代对象也计入块内赋值的依赖，用来压低间接依赖造成的侧信道，代价是策略触发更频繁：良性设定下总体触发率 NORMAL 为 33.87%，STRICT 为 53.23%（附录 Table 8）。

### 4.2 证据（AgentDojo）

摘要称 CaMeL 在可证明安全的前提下完成约 77% 的任务，无防御系统约 84%。

| 模型 | 良性效用：原生 → CaMeL | 成功攻击数：原生 → CaMeL（含策略） |
|---|---|---|
| Claude 4 Sonnet | 86.6% → 74.2% | 75 ± 58.6 → 11 ± 4.5 |
| Gemini 2.5 Pro | 73.2% → 41.2% | 163 ± 140.1 → 0 |
| o3 High | 84.5% → 77.3% | 11 ± 4.5 → 0 |
| o4 Mini High | 79.4% → 76.3% | 2 → 1 |

- 效用见 CaMeL Table 2，攻击计数见 Table 4（共 949 个攻击设定）。效用损失因模型而异，Gemini 2.5 Flash 从 55.7% 降到 35.1%；Travel 套件因工具输出文档不足，部分模型掉幅较大。Claude 4 Sonnet 配 Haiku 作 Q-LLM 时效用约 −1%，中位任务成本约 −12%（§6.1.3）。
- 攻击下的效用（Table 3）：o3 High 从 79.0% 到 79.8%（+0.7%），Claude 4 Sonnet 从 80.1% 到 75.7%。
- 残余的「成功攻击」中有一类并非 prompt injection：展示层把不可信的评论文本直接给用户看，即命中基准检查，这属于 CaMeL 声明的非目标，可用依赖图在界面上高亮来源。
- **与启发式防御对照**（Claude 3.5 Sonnet，Table 5 / 7）：无防御效用 90.72%、成功攻击 44 ± 31.3；Spotlighting 为 92.78% / 5 ± 0.6；Tool Filter 为 73.20% / 8 ± 2.5；CaMeL 为 63.92% / 0。CaMeL 换来的是可验证的策略保证，而不是「压低 ASR 同时保住最大效用」；单独使用 instruction hierarchy 的 GPT-4o mini 仍有大量成功攻击，加上 CaMeL 后为 0。
- **开销**（§6.5，Claude 3.5 Sonnet）：中位任务约 2.82 倍输入 token、2.73 倍输出 token；Spotlighting 约 1.06 倍输入，更便宜但没有同类保证。

### 4.3 失效模式

失败归类（CaMeL Table 1）包括：行动取决于只有 Q-LLM 能看到的数据、Q-LLM 上下文不足、API 文档不足、P-LLM 的错误假设等。Dual-LLM 隔离会牺牲「计划必须读不可信内容才能决定分支」的任务，需要在更严格策略下的嵌套规划等新机制，而不是退回单通道。

## 五、StruQ：结构化查询与指令微调

### 5.1 机制

StruQ §4 把 LLM API 从「单字符串混合控制与数据」改为结构化查询 (prompt, data) 两个参数，由两部分实现：

1. **安全前端**：用保留的特殊 token 编码分隔符，替代 Alpaca 式的文本分隔；过滤用户数据中仿造这些保留串的内容，使「伪分隔符」无法在 token 层冒充控制标记。新 token 的嵌入用对应文本 token 初始化，文中指出随机初始化会严重伤效用。
2. **结构化指令微调**：从未经指令微调的 base 模型出发，训练集约 50% 为干净样本、25% 在数据通道中插入简单的错位指令、25% 为 Completion 类错位指令（算法见 StruQ Algorithm 1）；目标响应始终服从 prompt 通道、忽略数据通道中的指令。

### 5.2 证据

Llama-7B 与 Mistral-7B 全参微调 3 个 epoch。效用用 AlpacaEval 1.0：Llama 67.2% → 67.6%，Mistral 80.0% → 78.7%（StruQ Table 3）。安全用 208 条含数据的 AlpacaFarm 样本上的 ASR（Table 2）：

| 攻击族 | Llama 无防御 → StruQ | Mistral 无防御 → StruQ |
|---|---|---|
| Naïve / Ignore / Escape 类 | 2–12% → 0% | 1–11% → 0% |
| Completion 类 | 29–96% → 0–2% | 71–96% → 0–2% |
| HackAPrompt | 52% → 0% | 38% → 0% |
| Tree-of-Attack（TAP） | 97% → 9% | 100% → 36% |
| GCG | 97% → 58% | 99% → 56% |

手工与 Completion 类攻击可压到极低，但任务相关的优化攻击仍有残余，结构化查询是方向而不是终点。对照 BIPIA（Table 7），StruQ 在效用与跨测试集泛化上更稳；BIPIA 在文内设定下 AlpacaEval 从 53.9% 降到 26.0%，GCG 仍可达 100% ASR。

## 六、如何选择与组合

| 约束 | 更贴近 |
|---|---|
| 不能改权重、需要多模型热插拔、需要可审计的策略 | CaMeL |
| 能从 base 模型微调、API 可改成双参数、要压低应用内注入 ASR | StruQ |
| 只有提示工程或检测器 | 不足（见 Adaptive；CaMeL Table 7 中启发式防御仍有成功攻击） |
| 要挡的是违规内容而不是应用控制流 | [[审慎对齐与断路器]]、[[宪法分类器防御]]、[[安全红队与对抗评测]] |

两者可以组合：CaMeL §11 明确可与提升模型自身鲁棒性的方法联用；StruQ 把 instruction hierarchy（Wallace 等）视为多级推广。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[安全红队与对抗评测]] | 评测前提：攻击族与 ASR 的评测框架 | 红队通史、众包协议与攻击面地图 |
| [[宪法分类器防御]] | 互补防线：分类器护栏在部署旁路挡违规内容，本篇在架构上隔离控制流，二者可叠加 | 分类器架构与指标 |
| [[审慎对齐与断路器]] | 互补防线：在权重内用规范推理与表征熔断阻断有害轨迹，干预层不同 | 对齐范式本身 |
| [[多模态越狱与OmniSafe]] | 威胁区分：越狱对抗提供商的安全规范，注入对抗开发者意图 | 多模态越狱攻防 |
| [[SHADEArena隐瞒与监控]] | 共用环境：SHADE-Arena 以 AgentDojo 为脚手架起点，CaMeL 也在 AgentDojo 上评测 | 隐蔽破坏与监控评测 |
| [[智能体工具与长程任务]] | 威胁来源：工具环把不可信的工具结果送进上下文，是注入的主要入口 | 工具环与长程任务全文 |
| [[计算机使用智能体]] | 威胁来源：computer-use agent 读取网页与界面内容，面临同类不可信数据 | computer-use 方法与评测 |

## 八、局限与待核实

- **CaMeL 的非目标**（CaMeL §3.1、§7）：不防无控制流或数据流后果的纯展示层篡改；不追求零人工介入的全自主；侧信道（异常中止、时序等）只能减弱而非消除；策略编写成本与用户确认疲劳是现实负担。
- **StruQ 的范围**（StruQ §6）：面向程序化的应用 API，不适用于终端用户不愿标注指令与数据的开放多轮聊天；对强优化攻击仍有残余 ASR；不声称防越狱或训练数据提取等其他威胁；需要提供商开放 base 模型。
- **开放问题**：解释器与策略的形式化验证、策略冲突消解（CaMeL §10），以及换用显式错误类型的语言以减少异常侧信道；把系统提示纳入多级结构化查询（与 instruction hierarchy 对齐）。两文都明确没有「完全解决」prompt injection。
- **数字口径**：CaMeL 的效用与攻击计数随骨干模型差异很大，摘要的 77% 对 84% 与 o3 High 一行同量级，不代表所有模型；Adaptive 的结论基于 InjecAgent 子集与两种 7–8B agent，外推到更强模型需另行验证。
- **代码可用性**：三个代码仓库可以访问，但本篇没有核验其能否复现文中数字。

## 九、延伸阅读

| 类型 | 标题 | 说明 | URL |
|---|---|---|---|
| 论文 | Defeating Prompt Injections by Design | Debenedetti 等，2025-03（v2 2025-06）；CaMeL | https://arxiv.org/abs/2503.18813 |
| 论文 | StruQ: Defending Against Prompt Injection with Structured Queries | Chen、Piet、Sitawarin、Wagner，2024-02；USENIX Security 2025 | https://arxiv.org/abs/2402.06363 |
| 论文 | Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents | Zhan、Fang、Panchal、Kang，2025-02；防御脆弱性动机 | https://arxiv.org/abs/2503.00061 |
| 代码 | google-research/camel-prompt-injection README | CaMeL 实现 | https://github.com/google-research/camel-prompt-injection |
| 代码 | Sizhe-Chen/StruQ README | StruQ 官方实现 | https://github.com/Sizhe-Chen/StruQ |
