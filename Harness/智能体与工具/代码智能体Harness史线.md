---
title: "Code agents harness 史线：SWE-agent → OpenHands SDK"
topic: 代码智能体Harness史线
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
sources:
 - https://arxiv.org/abs/2405.15793
 - https://arxiv.org/abs/2511.03690
arxiv: ["2405.15793", "2511.03690"]
related:
 - "Harness/智能体与工具/智能体工具与长程任务.md"
 - "安全与评测/评测与排行榜可靠性.md"
 - "模型与技术报告/厂商报告/UIVenus2GUI智能体.md"
 - "Harness/EvalHarness/合成用户仿真.md"
archived: 2026-09-22
---

# Code agents harness 史线：SWE-agent → OpenHands SDK

> **主题立轴**：相对「旗舰工具环 / 长程产品叙述」与「SWE-bench 只作文评入口」，本篇专立 **Agent–Computer Interface（ACI）/ 沙箱 harness / 可组合生产 SDK** 子史：决定编码智能体能否**复现实验、隔离执行、上生产**。
> **读者向范围**：架构思想为主，AI Infra（沙箱 / 远程 runtime）为辅。谱系两站：SWE-agent（LM 友好 ACI + Docker 可复现）→ OpenHands Software Agent SDK（可选沙箱、事件源状态、四包可组合、本地→远程同 API）。
> **范围外参见**：
> - MCP / ReAct / 旗舰工具环与 System Card 长程叙事 → 「智能体工具与长程任务」；本篇只把 ReAct 当作 SWE-agent 控制环引用一句，把 MCP 当作 OpenHands **工具抽象的一等公民接入点**（schema 互转），不展开协议史。
> - SWE-bench 数据集构造全文 → 「评测与排行榜可靠性」/ 原 Jimenez et al.；本篇只录 harness 侧 resolve 数字。
> - GUI 基础智能体、合成用户仿真 → 各自专篇，本篇不展开。
> **材料口径**：数字、消融、生产错误率一律锚定官方 PDF（检索截止 2026-09-22）。

---

## 一、材料元信息

| 材料 | 标识 / URL | 角色 |
|---|---|---|
| **站 1** | Yang, Jimenez et al., *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*；arXiv **2405.15793v3** \[cs.SE\]（**11 Nov 2024**）；NeurIPS 2024；https://arxiv.org/abs/2405.15793（**118** 页） | 提出 **ACI**；LM 专用命令面 + 观测格式 + guardrail；Docker 复现；SWE-bench / HumanEvalFix |
| **站 2** | Wang, Rosenberg, Michelini et al., *The OpenHands Software Agent SDK: A Composable and Extensible Foundation for Production Agents*；arXiv **2511.03690v2** \[cs.SE\]（**22 Apr 2026**）；Accepted **MLSys 2026**；https://arxiv.org/abs/2511.03690（**19** 页） | OpenHands **V0→V1** 全量重设计；四包 SDK；opt-in 沙箱；事件源 + 生产可靠性实证 |

**代码 / 评测入口（论文自报）：** swe-agent.com；https://github.com/OpenHands/software-agent-sdk ；https://github.com/OpenHands/benchmarks ；OpenHands Index https://index.openhands.dev

**一句话抓手：** 编码智能体的瓶颈不只是「更会想」，而是 **给 LM 什么动作面、什么反馈、什么隔离与状态合同**——SWE-agent 证明 **为人设计的 Linux shell / IDE 搜索 UI 不直接等于好 ACI**，专用 viewer/edit/search + lint guardrail 把 SWE-bench Lite resolve 从 Shell-only **11.00%** 拉到 **18.00%**；OpenHands SDK 则把「单体、处处沙箱」的研究 harness 改成 **本地默认、沙箱可选、Conversation/Workspace 同 API 切远程** 的生产基础，并在 15 天并行上线里把系统归因失败率降约 **61%**。

---

## 二、问题立轴：为何是 harness，而不是「又一个 agent 提示词」

### 2.1 三层对象（本篇只写中间 + 下层）

| 层 | 含义 | 本篇 |
|---|---|---|
| **策略 / 提示 / 工具协议** | ReAct 环、MCP 协议、产品工具目录 | **点到即止** → 全文见「智能体工具与长程任务」 |
| **ACI / harness** | 动作集合、观测截断、历史折叠、编辑/搜索语义、lint 护栏 | **站 1 主文** |
| **运行时 / SDK / 沙箱** | Docker/进程边界、状态持久化、本地↔远程、确认策略、发布形态 | **站 1 辅线（Docker）+ 站 2 主文** |

跟读：Jimenez et al. 的 SWE-bench 回答「**测什么**」；本篇两文回答「**怎么让 LM 稳定地摸到仓库并复现/部署**」。换 scaffold 可以换故事——「智能体工具与长程任务」已警告公开 SWE-bench 高分绑在工具面与 harness 上；本篇把那句警告展开成可跟读的 ACI→SDK 史。

### 2.2 史线简图

`
Linux shell / 人类 IDE UI
 ↓ （对人友好 ≠ 对 LM 友好）
SWE-agent ACI（少而可组合动作 + 简洁反馈 + guardrail + Docker）
 ↓ （研究 harness → 生产张力：单体、强制沙箱、配置蔓延）
OpenHands V0（开源软件 agent 栈，沙箱中心）
 ↓
OpenHands Software Agent SDK / V1（四包、事件源、opt-in 沙箱、REST/WS）
`

---

## 三、站 1：SWE-agent — Agent–Computer Interface（2405.15793）

### 3.1 主张：LM 是新一类终端用户

Abstract / §1–2：LM agent 常被塞进 **已有人类界面**（Linux shell、Python 解释器）；但复杂 SE 任务上，人类靠 IDE 等应用提效。作者提出 **agent-computer interface（ACI）**：介于 LM 与计算机之间的抽象层——**既规定可用命令，也规定环境状态如何回传**；并管理历史如何拼进下一步输入。

相对 HCI：GUI 富视觉对当代 LM 不友好；人类可忽略冗余，LM 则对无关上下文付 **固定记忆/算力成本**。故 ACI 应：帮助理解变更后状态、管理历史以免过时观测占窗、提供 **高效且可靠** 的动作。

**贡献口径（作者自述，§1 末）：**（1）提出 ACI 概念，证明 **不改权重**、只改界面即可大幅提升；（2）开源 SWE-agent。控制环显式引用 **ReAct**（Yao et al.）——本篇不复述 ReAct 正文。

### 3.2 ACI 设计四原则（§2）

| # | 原则 | 操作含义（文内） |
|---|---|---|
| 1 | **Actions simple** | bash 常有几十选项；给 agent 少选项、短文档，少演示/微调 |
| 2 | **Actions compact & efficient** | 导航/编辑等高阶操作尽量 **单动作完成**，避免多轮拼装 |
| 3 | **Feedback informative but concise** | 编辑后立刻给更新视图；抑制噪声 |
| 4 | **Guardrails** | 语法检查等自动拦错、促恢复，减误差传播 |

### 3.3 SWE-agent 组件（§3）— harness 本体

建在 Linux shell 之上，仍可调普通 Linux 工具；专用面包括：

| 组件 | 命令 / 行为 | 设计要点 |
|---|---|---|
| **Search / navigation** | `find_file`、`search_file`、`search_dir` | 结果 ≤ **50**；过多则 **不返回明细**，要求更具体查询 |
| **File viewer** | `open`；`scroll_down` / `scroll_up`；`goto` | 窗口最多 **100** 行；显示路径、总行数、省略行数、行号 |
| **File editor** | `edit`（起止行 + 替换文本） | 与 viewer **集成**：编辑后自动刷新视图 |
| **Lint guardrail** | 编辑路径内嵌 linter | 选出错误 + 改前/改后片段；**非法编辑丢弃**，要求重试 |
| **Context management** | 指令 + 文档 + 演示；每步 thought+action | 畸形生成 → 错误模板直至合法；**仅保留最近 5 条**完整 observation，更早折叠为单行；空输出有明确文案 |

**Infra 辅线（附录）：** 采用 **Docker** 保证可复现；容器与 agent 实体之间传动作/观测；Dockerfile 可改以支持其他代码库（文内 §A 一带）。

### 3.4 实验设置与主结果（§4–5）

| 项 | 事实 |
|---|---|
| 主评测 | **SWE-bench** 全量 **2,294**；消融/分析用 **SWE-bench Lite 300**；另 **HumanEvalFix** |
| 模型 | 主：**GPT-4 Turbo**（`gpt-4-1106-preview`）、**Claude 3 Opus**（`claude-3-opus-20240229`）；文称其他开源/闭源 agent 设定表现不佳 / 窗过小 |
| 基线 | **RAG**（BM25 检索后一次出 patch，Jimenez et al.）；**Shell-only**（InterCode 式纯 shell 交互，Yang et al.） |
| 指标 | **% Resolved / pass@1**；**$ Avg. Cost**（仅对成功实例均摊）；单实例预算 **$4**，超预算自动提交已有编辑 |
| SWE-bench 全量 | GPT-4 Turbo **12.47%**（286/2294）；Claude 3 Opus **10.46%** |
| SWE-bench Lite | GPT-4 Turbo **18.00%**；Claude **13.00%**；Shell-only GPT-4 **11.00%**（无演示 7.33%）；RAG GPT-4 **2.67%** / Claude **4.33%** |
| HumanEvalFix pass@1 | Abstract 汇总 **87.7%**；Table 2：Python **87.7** / JS **89.7** / Java **87.9**（SWE-agent w/ GPT-4 Turbo） |

相对 RAG：Lite 上约 **8–13×** 更贵、约 **6.7×** resolve；相对 Shell-only：同 GPT-4 Turbo 约 **+64%** 相对提升（11.00→18.00）。

### 3.5 消融：人类 UI ≠ ACI（Table 3，Lite，GPT-4）

默认 ACI（含 lint、Summarized search、100 行窗、Last 5 Obs）= **18.0%**。对照（文内 ↓ 相对默认）：

| 轴 | 变体 | % Resolved |
|---|---|---|
| Editor | edit **w/ linting**（默认） | **18.0** |
| | edit **无** linting | 15.0 ↓3.0 |
| | **No edit**（靠重定向/`sed` 等） | 10.3 ↓7.7 |
| Search | **Summarized**（默认） | **18.0** |
| | **Iterative**（仿 Vim/VSCode 逐条 next/prev） | 12.0 ↓6.0 |
| | **No search** | 15.7 ↓2.3 |
| File viewer | **100 lines**（默认） | **18.0** |
| | 30 lines | 14.3 ↓3.7 |
| | Full file | 12.7 ↓5.3 |
| Context | **Last 5 Obs.**（默认） | **18.0** |
| | Full history | 15.0 ↓3.0 |
| | w/o demo. | 16.3 ↓1.7 |

**跟读结论（文内 §5.1）：**

1. **Iterative search 比「无搜索」更差**：agent 倾向穷尽每条匹配 → 烧预算/上下文；**压缩汇总 + 过多则拒** 更 LM 友好。
2. **紧凑多行编辑 + 自动刷新视图** 远好于整文件重写/`sed`；lint 再抬一截。
3. **窗口过大或过小都伤**；历史全量不如折叠旧观测。

行为侧补充（§5 后文）：失败轨迹更常顶满预算；成功轨迹更早更便宜——单纯加长预算未必救得了坏 ACI。

### 3.6 站 1 收束

SWE-agent 把「编码 agent」从 **提示词 + 裸 shell** 提升为 **可消融的界面工程问题**：动作语义、观测带宽、护栏与上下文折叠是一阶杠杆。Docker 把该 ACI 钉在可复现沙箱上——这是 harness，还不是可组合生产 SDK。

---

## 四、站 2：OpenHands Software Agent SDK — 可组合生产 harness（2511.03690）

### 4.1 从 OpenHands V0 到 V1：为何必须重写

文内背景：OpenHands（Wang et al., 2025）开源软件 agent 获广泛采用（文称约 **18 个月**内 **>64k** GitHub stars、数百贡献者）。V0 **单体 + 强制沙箱** 在规模化后暴露：

| V0 张力（§3） | 症状（文内） | V1 原则 |
|---|---|---|
| **Universal sandboxing** | 对话常跨 agent/沙箱两进程，状态易分叉；多租户资源互相拖垮；本地 CLI/MCP 要绕路复制实现 | **Optional isolation**：默认同进程本地跑；隔离 **opt-in** |
| **Mutable config sprawl** | **140+** 字段、**15** 类、**2.8K** 行配置；多入口各自覆盖 | **Stateless by default**：Agent/Tool/LLM 等不可变；**唯一可变** = ConversationState |
| **Monorepo** | agent 核与 CLI/Web/评测缠死；基准依赖泄漏 | **Strict SoC**：SDK 作共享库，应用只调 API |
| **难扩展** | 新行为常改核心或按入口打补丁 | **Two-layer composability**：部署四包 + 类型化组件扩展 |

> **范围说明：** 文中多次出现 MCP（V0 早于 structured tool use / MCP；V1 与 MCP 假设对齐）。本篇只记 **「工具 schema ↔ Action/Observation 互转、MCP 工具与原生工具同接口」**，不写 MCP 协议正文（详见「智能体工具与长程任务」）。

### 4.2 四包架构（§4.1）— Infra 主图

| 包 | 职责 |
|---|---|
| **`openhands.sdk`** | 核心抽象：Agent、Conversation、LLM、Tool、MCP、事件系统 |
| **`openhands.tools`** | 基于 sdk 抽象的具体工具实现 |
| **`openhands.workspace`** | 执行环境（Docker、hosted API 等），扩展 sdk 基类 |
| **`openhands.agent_server`** | REST + WebSocket，远程执行 API 服务 |

最小用法（Figure 2）：`LLM` → `get_default_agent` → `Conversation(agent, workspace=...)` → `send_message` / `run`。本地改远程：把 workspace 换成 `DockerWorkspace`（Figure 5），其余配置不变——**local-first, deploy-anywhere**。

### 4.3 SDK 九块积木（§4.2–4.10，跟读清单）

1. **Event-sourced state**：不可变事件追加；`ConversationState` 单源真相；元数据写 `base_state.json`，事件分文件；崩溃恢复可从日志重放。
2. **LLM 层**：经 LiteLLM 接 **100+** provider；Chat Completions + OpenAI Responses；原生 reasoning/extended thinking 字段；无 function-calling 模型用文本工具协议 mixin；**`RouterLLM`** 按消息选模型。
3. **Tool 系统**：Action（校验）→ Executor → Observation（转 LLM 内容）；自定义工具与 **MCP 工具同抽象**；registry 把可序列化 spec 与不可序列化 executor 解耦，便于跨进程。
4. **Agent**：无状态规格（可序列化、可跨边界传送）；事件驱动步进；可插入安全审核、暂停/恢复、condensation。
5. **Context / Condenser**：历史过大时丢事件并插入摘要事件；默认 `LLMSummarizingCondenser`，文称可把 API 成本降到约 **2×** 且不伤性能（引 Smith 2025）。
6. **LocalConversation**：进程内全环，便于调试。
7. **SecretRegistry**：按会话隔离；执行时注入、输出自动 mask（如 `<secret-hidden>`）；支持热更新。
8. **SecurityAnalyzer + ConfirmationPolicy**：动作风险 low/medium/high/unknown；需确认则进入 `WAITING_FOR_CONFIRMATION`；内置 `LLMSecurityAnalyzer` + `ConfirmRisky`（默认拦 high）。
9. **Workspace + Agent Server**：`LocalWorkspace` 直调本机；`RemoteWorkspace` HTTP 委托；官方镜像可捆 API + VS Code Web + VNC + Chromium，每 agent 一容器。

### 4.4 相对其他 SDK 的「独特组合」（Table 6，截至文内 2025-10 文档口径）

作者对比 OpenAI Agents SDK、Claude Agent SDK、Google ADK、LangChain/LangGraph 等。OpenHands **自述独有组合**：（i）原生远程执行 + **环境沙箱**；（ii）LLM 驱动的 **动作级安全分析**；（iii）模型无关 **多 LLM 路由** + 非 function-calling 一等支持；（iv）内置学术基准评测 / QA。表中多项（如 Builtin REST+WS、Agent Environment Sandboxing、Secrets auto-mask、Built-in academic benchmark eval）在对比列上对 OpenHands 为 ✓、对多数 provider SDK 为 × 或 ∼——**以 Table 6 为准，不外推未评估版本**。

### 4.5 可靠性与能力实证（§5）

**生产（15 天 V0/V1 并行，Table 2）：** 系统归因错误 / 1k conversations：V0 **78.0** → V1 **30.0**（约 **−61%**）。V0 基建错误（如跨 pod HTTP 401、runtime 未就绪）在 V1 **共置执行** 后观测为 **0.0 / 1k**；V1 剩余 SDK 错误 **29.7 / 1k**（文称 rollout 期 condensation × extended thinking 约束 bug，后续正式版已修）。

**事件源开销（Table 3，433 条 SWE-Bench Verified 轨迹，39,870 events）：** 单事件持久化中位 **0.20 ms**；全量 replay 中位 **4.1 ms**；崩溃恢复中位 **7.4 ms**（最长 358 events 时 recovery **32.1 ms**）——相对 LLM 往返可忽略。

**能力保持（Table 4，SWE-Bench Verified）：** Claude Sonnet 4：V0=V1 **68.0%**（架构换皮不伤基线）；Sonnet 4.5：V0 **64.6%** → V1 **72.8%**（+8.2；作者归因 V1 更易接 extended thinking）。

**多模型五类任务（Table 5，14 模型）：** Best SDK 示例——SWE-Bench Verified **76.6%**（Opus 4.5）、Commit0 **56.2%**（GPT-5.4）、SWE-Bench MM **44.1%**（Gemini 3.1 Pro）、SWT-Bench V. **78.8%**（Opus 4.6）、GAIA test **80.0%**（Opus 4.6）。文称 5 项中 3 项超当时 published SOTA；完整分模型见 Index（持续更新，笔记只钉 PDF 表内数字）。

### 4.6 站 2 收束

OpenHands SDK 把 SWE-agent 时代的问题从「**设计一个好 ACI**」推进到「**把 ACI + 工具 + 状态 + 沙箱做成可版本化、可远程、可确认、可测的 SDK 合同**」。沙箱从 **默认枷锁** 变为 **部署旋钮**；状态从 **散落可变配置** 变为 **事件源单源真相**。

---

## 五、两站对照：同一史线的升级维度

| 维度 | SWE-agent（2024） | OpenHands Software Agent SDK（2025–26 文） |
|---|---|---|
| 核心概念 | **ACI**（命令 + 反馈格式 + 历史策略） | **Composable SDK**（四包 + 类型化 Tool/LLM/Workspace） |
| 动作面 | 少量 SE 专用命令（viewer/edit/search）+ bash | Action–Observation 统一；原生工具 ∪ MCP 工具 |
| 隔离 | Docker 复现为默认研究设定 | **默认本地**；Docker/远程 **opt-in** |
| 状态 | 轨迹提示折叠（last-5 obs 等） | 事件源 + Condenser；可暂停/恢复/跨进程序列化 Agent |
| 安全 | lint 等编辑护栏 | SecurityAnalyzer + ConfirmationPolicy + Secret mask |
| 成功判据 | SWE-bench resolve / HumanEvalFix | 生产失败率 + 事件源开销 + 多基准 Index |
| 与工具环笔记关系 | 证明 **scaffold/ACI** 改变分数 | 证明 **运行时合同** 改变可上线性 |

**连续读法：** SWE-agent 回答「LM 需要什么样的 **计算机界面**」；OpenHands SDK 回答「这个界面如何变成 **可复用库 + 可选沙箱 + 远程服务**，而不绑死在一个单体研究仓库」。

---

## 六、待核实 / 本篇明确不做

| 项 | 说明 |
|---|---|
| SWE-agent 之后社区 ACI 变体（更多 viewer/编辑 DSL）与 2025–26 私有 coding agent 内部 harness | 非本 PDF → **待核实 / 不写入数字** |
| OpenHands Index 上晚于 PDF 表 5 的刷新分数 | 以 PDF 钉死；线上榜 **待同步核实** |
| MCP / ReAct / Claude Code / 旗舰 System Card 工具环 | 范围外 → 「智能体工具与长程任务」 |
| SWE-bench 污染、scaffold 公平性方法论 | 点到即止 → 「评测与排行榜可靠性」及相关污染专篇 |
| GUI 基础智能体（UI-Venus-2 等） | → 「UIVenus2GUI智能体」 |
| 合成用户 / ToolEmu / τ-bench | → 「合成用户仿真」 |

---

## 七、跟读收束句

> **架构思想上**，编码智能体史线的关键变量是 **界面与运行时合同**：SWE-agent 用 ACI 四原则证明「少而高效的动作 + 简洁反馈 + guardrail」可在不改权重下显著抬升真实仓库修复率；OpenHands SDK 用四包与事件源把同一问题提升为 **可组合、可确认、可本地/远程切换** 的生产基础。
> **AI Infra 辅线上**，Docker/进程边界、状态持久化开销、跨 pod 认证失败、opt-in 沙箱与 REST/WebSocket 服务，决定的是 **复现与上线**，不是榜面文案——换 harness 仍可能换故事，但合同应可审计。

---

**材料版本：** arXiv 2405.15793v3 + 2511.03690v2（官方 PDF）；笔记日期 2026-09-22（Asia/Shanghai）。

## 相关笔记

- [[智能体工具与长程任务|智能体、工具与长程任务]]
- [[评测与排行榜可靠性|评测与排行榜可靠性]]
- [[Inspect评测Harness|Inspect 评测 Harness]]
- [[UIVenus2GUI智能体|UI-Venus-2 GUI 智能体]]
- [[合成用户仿真|合成用户仿真]]
- [[推理引擎生态|推理引擎生态]]
- [[AI基础设施总览|AI 基础设施总览]]
