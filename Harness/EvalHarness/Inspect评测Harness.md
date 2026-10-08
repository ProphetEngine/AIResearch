---
title: "Open eval harness：UK AISI Inspect"
topic: Inspect评测Harness
date: 2026-09-22
lines: [评测字段, AI Infra]
status: archived
sources:
 - https://inspect.aisi.org.uk/
 - https://inspect.aisi.org.uk/solvers.html
 - https://inspect.aisi.org.uk/scorers.html
 - https://inspect.aisi.org.uk/tasks.html
 - https://inspect.aisi.org.uk/sandboxing.html
 - https://inspect.aisi.org.uk/eval-logs.html
 - https://inspect.aisi.org.uk/log-viewer.html
 - https://github.com/UKGovernmentBEIS/inspect_ai
 - https://github.com/EleutherAI/lm-evaluation-harness
 - https://arxiv.org/abs/2211.09110
related:
 - "评测与排行榜可靠性"
 - "代码智能体Harness史线"
 - "WorfBench工作流基准"
 - "智能体工具与长程任务"
 - "VendingBench经营长程评测"
 - "AIControl协议与Scheming倾向"
 - "评测污染可靠性鸿沟"
 - "NemotronCC数据策展"
github: "https://github.com/UKGovernmentBEIS/inspect_ai"
docs: "https://inspect.aisi.org.uk/"
arxiv: []
boundary: "≠榜单通史；≠编码 ACI/SDK 史线；≠lm-eval/HELM全文"
archived: 2026-09-22
---

# Open eval harness：UK AISI Inspect

> **主要来源**：[Inspect 官方文档](https://inspect.aisi.org.uk/)；[inspect_ai 代码仓](https://github.com/UKGovernmentBEIS/inspect_ai)；脉络对照 [EleutherAI lm-evaluation-harness README](https://github.com/EleutherAI/lm-evaluation-harness) 与 [HELM（Liang et al., 2022）](https://arxiv.org/abs/2211.09110)（截至 2026-10-08；Inspect 文档访问于 2026-09-22）
> **研究线**：评测字段 / AI Infra——评测运行时怎样把一次 LLM 或 agent 评测写成可组合、可隔离、可复现的程序。
> **范围与相邻笔记**：
> - ≠ [[评测与排行榜可靠性]]：本篇不写榜单污染、scaffold 敏感性的案例史。
> - ≠ [[代码智能体Harness史线]]：本篇不写 SWE-agent 到 OpenHands 的编码 ACI 与生产 SDK 史。
> - ≠ [[WorfBench工作流基准]]：本篇不写任何单一基准的构造与主表。
>
> **意义**：Inspect 把 scaffold（solver）与执行环境（sandbox）变成评测的一等参数，并把完整配置写回日志，使「同一任务换策略、换模型再跑」成为常规操作；代价是一个分数只有连同其配置一起报告才有意义。

**一句话**：一次评测 = `Task(dataset, solver, scorer, …)`。Solver 改写并驱动对话状态（可以是一个工具调用 agent），Scorer 拿输出对照目标打分，sandbox 把不可信的代码执行隔离出去，日志记录全部配置并能反导出来再跑一遍。

---

## 一、问题背景

早期 LLM 评测的主体是静态基准：给定提示，取模型输出，与参考答案比对。随着评测对象转向 agent，这套流程有三处不够用：

1. **被测的不只是模型**。同一个模型配不同的提示、工具和多轮策略，分数会明显不同（这一敏感性问题见 [[评测与排行榜可靠性]]）。评测必须能把「策略」作为参数显式声明并替换。
2. **需要执行不可信代码**。代码、网络安全、操作系统类任务要让模型跑 bash 或 Python、读写文件、访问网络主机，必须有隔离环境。
3. **复现要靠配置而不是分数**。多轮、带工具、带评审模型的评测，只有记下任务、模型、生成参数、solver 与评分设置，别人才可能重跑。

## 二、脉络：评测框架关注点的三次转移

| 框架 | 时间 | 关注重心 | 代表性设计 |
|---|---|---|---|
| EleutherAI lm-evaluation-harness | 2020-08（代码仓创建日期） | 用一个统一框架在大量标准学术基准上测生成式 LM | 60 多个标准学术基准、数百个子任务；v0.4 起以 YAML 配置定义任务；提供 Open LLM Leaderboard 任务组（README） |
| HELM（Stanford） | 2022-11 | 多指标、标准化条件下的整体评测 | 16 个核心场景 × 7 项指标（准确率、校准、鲁棒性、公平、偏见、毒性、效率），30 个模型在相同条件下评测（HELM Abstract） |
| Inspect（UK AISI 与 Meridian Labs） | 2024-05（软件引用日期） | 前沿模型与 agent 评测：工具、沙箱、日志可视化 | Task / Solver / Scorer 可组合构件；200 多个预置评测；Inspect View 与 VS Code 扩展（文档首页） |

三者的分工可以这样看：lm-eval-harness 解决「把很多基准放进同一个框架」，HELM 解决「在同一条件下多维度地比较」——论文称此前模型平均只在 17.9% 的核心场景上评测过，HELM 提高到 96.0%；Inspect 则面向 agent 评测，把多轮交互、工具调用与执行隔离做成框架的原生能力。

lm-eval-harness 至今仍被广泛使用：例如 [[NemotronCC数据策展]] 的预训练数据消融就用它评十项任务。Inspect 并不取代这类静态基准评测，而是覆盖它们不擅长的 agent 场景。

## 三、核心思想：评测即可组合程序

### 3.1 三个原语

| 原语 | 职责 | 典型构件（文档） |
|---|---|---|
| Dataset | 样本合同：`input`（提示）与 `target`（理想答案或评分指导），可附选项、文件、每样本 sandbox | `hf_dataset`、`json_dataset`、`csv_dataset`；字段映射 `FieldSpec` |
| Solver | 对 `TaskState`（消息历史、最终输出、可用工具等）的变换；可串成 chain | `system_message`、`prompt_template`、`chain_of_thought`、`generate`、`use_tools`、`self_critique`、`multiple_choice`；agent 用 `react(...)` |
| Scorer | 拿输出对照 `target` 打分，并声明汇总指标（如 accuracy + stderr） | 提取式 `pattern` / `answer` / `choice`；匹配式 `includes` / `match` / `exact` / `f1`；模型评分 `model_graded_qa` / `model_graded_fact`；`math` |

`Task` 至少由这三者组成，还可附 `sandbox`、`epochs`、`setup`、资源限制和 `model_roles`。用 `@task` 装饰的 Python 函数返回一个 `Task`，命令行与 Python API 都能发现并执行它。

文档首页的两个最小例子说明了这套原语的跨度：

```text
# 静态问答：生成一次，用模型评分
Task(dataset=hf_dataset(...), solver=generate(), scorer=model_graded_qa())

# agent + 沙箱：reason–act–observe 环，最多三次尝试
Task(dataset=json_dataset("challenges.json"),
     solver=react(tools=[bash(), todo_write()], attempts=3),
     scorer=includes(), sandbox="docker")
```

两者用的是同一套 Task 结构，差别只在 solver 和 sandbox 两个参数上——这正是「可组合」的含义。

### 3.2 配置叠层：同一任务，换策略、换模型

文档把配置分成四层，后者覆盖前者：

```text
Task 定义 → task_with() → .env 环境变量 → eval() / 命令行
```

由此得到几种常用操作：

- **换 elicitation 不改数据**：命令行 `--solver`、`-S attempts=5`；`setup` 在换 solver 后仍会先执行。
- **改第三方任务不改源码**：`task_with()` 覆盖外部包里写死的 solver 或 sandbox。
- **评分模型单独指定**：`model_roles={"grader": ...}`，solver 或 scorer 内按角色取模型。
- **整套配置打包**：`--run-config run.yaml` 一次给出 task、model、生成参数、solver 与评测设置。

### 3.3 Sandbox：隔离边界只覆盖经 `sandbox()` 请求的工作

`bash()`、`python()`、`text_editor()`、`web_browser()` 等内置工具需要沙箱。文档特别说明：声明 `sandbox=` 不会把整个 solver 或 scorer 搬进容器，只有经 `sandbox()` 接口请求的执行在容器内，评测编排与模型 API 调用仍在主机侧。

- **绑定层级**：命令行或 `eval()` 的 `--sandbox` 最高，其次是 `Task(sandbox=…)`，再次是每个样本的 `Sample.sandbox`（同类型时样本自带的 compose 配置优先）。
- **类型**：内置 `docker` 与 `local`（本机执行，无隔离）；扩展包提供 `k8s`、`daytona`、`modal`、`ec2` 等。
- **网络默认关闭**：自动生成的 compose 配置带 `network_mode: none`；自备 compose 会替换而不是扩展这一默认。

### 3.4 日志与复现闭环

- **每次评测必写日志**：自 v0.3.46 起默认用二进制 `.eval` 格式（也可选 JSON）。文档建议通过 Log API 读写，而不是自行解析底层格式。
- **查看**：`inspect view` 或 VS Code 扩展可钻到每个样本的消息与评分，区分「答案没提取出来」和「答错」。
- **续跑**：失败或中断的评测可用 `eval-retry` 从日志续跑；复用已完成样本需要稳定的样本 id。
- **配置往返**：`inspect log export-config` 从日志导出 YAML，再交给 `--run-config` 重跑；`inspect score` 可离线换 scorer 重新打分。

文档承诺的是配置层面的往返，并不承诺同一随机种子下逐 token 完全一致。

## 四、设计取舍

| 选择 | 得到什么 | 付出什么 |
|---|---|---|
| 用 Python 程序定义任务（lm-eval-harness 以 YAML 配置为主） | solver 可以是任意代码，包括完整 agent 环 | 任务定义更难做静态比对，复现依赖代码版本 |
| solver 与 sandbox 作为一等参数 | 同一任务换策略、换环境无需改数据 | 分数必须连同 solver 与环境一起报告，否则不可比 |
| 隔离只覆盖 `sandbox()` 调用 | 编排与模型调用保持在主机，调度简单 | 使用者必须清楚哪些执行在容器内，`local` 类型完全无隔离 |
| 日志存完整配置并可反导出 | 跑过的评测天然可复跑、可离线重评分 | 二进制日志需通过官方 API 读取；配置可复现不等于结果逐比特可复现 |

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[评测与排行榜可靠性]] | 该篇指出分数绑定 scaffold 与配置；Inspect 是把这一点落实到工程上的框架 | 榜单污染与敏感性案例 |
| [[代码智能体Harness史线]] | 两者都需要隔离执行与可复现环境；该篇的 harness 让 agent 干活，本篇的 harness 给 agent 打分 | ACI 命令设计、OpenHands 架构、SWE 系列分数 |
| [[智能体工具与长程任务]] | `react` agent 与工具调用是该篇工具环在评测侧的承载方式 | 工具协议史与长程任务结果 |
| [[WorfBench工作流基准]] | 该篇是一个具体的 agent 基准，这类基准可由 Inspect 这样的运行时承载 | WorFEval 匹配算法与主表 |
| [[VendingBench经营长程评测]] | 该基准的 agent 循环基于 inspect-ai 搭建，是 Inspect 承载长程 agent 评测的实例 | 经营环境设计与结果 |
| [[AIControl协议与Scheming倾向]] | 该篇的 ControlArena 构建于 Inspect，是安全评测侧的下游实例 | 控制协议与 scheming 结论 |
| [[评测污染可靠性鸿沟]] | 该篇讨论污染与可靠性鸿沟，并把 Inspect 列为评测 harness 一侧的承接对象 | 污染检测方法 |
| [[NemotronCC数据策展]] | 该篇用 lm-eval-harness 做数据消融评测，是第二节脉络中静态基准框架的使用实例 | 数据策展流程 |

## 六、局限与待核实

1. **只有文档与代码，没有论文**：Inspect 没有对应的学术论文；所有 API 名与行为以文档站为准，文档版本会变。
2. **版本号与默认值会变**：`.eval` 默认格式起始版本（v0.3.46）、沙箱输出与读文件上限、并发默认值等都以访问日期 2026-09-22 的文档为准。
3. **不收录基准得分**：Inspect Evals 中各模型的具体分数未逐一核实，本篇不写。
4. **Agents、Tools、Extensions 专章未展开**：本篇只保留 `react` 与沙箱工具链的入口。
5. **脉络表的时间口径**：lm-eval-harness 的 2020-08 是 GitHub 代码仓创建日期，不是正式发布日期；Inspect 的 2024-05 来自文档页脚的软件引用条目。

## 七、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Inspect 文档首页](https://inspect.aisi.org.uk/) | SimpleQA 与 CTF 两个最小例子 |
| 2 | [Solvers](https://inspect.aisi.org.uk/solvers.html) → [Scorers](https://inspect.aisi.org.uk/scorers.html) | TaskState、solver 协议、scorer 分类 |
| 3 | [Tasks](https://inspect.aisi.org.uk/tasks.html) | 任务参数、四层配置、`task_with`、run-config |
| 4 | [Sandboxing](https://inspect.aisi.org.uk/sandboxing.html) | `sandbox()` 接口、网络默认、清理与并发 |
| 5 | [Eval Logs](https://inspect.aisi.org.uk/eval-logs.html) 与 [Log Viewer](https://inspect.aisi.org.uk/log-viewer.html) | 日志格式、续跑、配置往返、样本诊断 |
| 6 | [lm-evaluation-harness README](https://github.com/EleutherAI/lm-evaluation-harness) 与 [HELM](https://arxiv.org/abs/2211.09110) | 对照前两代评测框架的设计重心 |
