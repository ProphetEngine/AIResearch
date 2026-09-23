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
related:
 - "安全与评测/评测与排行榜可靠性.md"
 - "Harness/智能体与工具/代码智能体Harness史线.md"
 - "Harness/EvalHarness/WorfBench工作流基准.md"
 - "Harness/智能体与工具/智能体工具与长程任务.md"
github: "https://github.com/UKGovernmentBEIS/inspect_ai"
docs: "https://inspect.aisi.org.uk/"
arxiv: []
boundary: "≠榜单通史；≠编码 ACI/SDK 史线；≠lm-eval/HELM全文"
archived: 2026-09-22
---

# Open eval harness：UK AISI Inspect

> **本文写什么**：UK AI Security Institute（UK AISI）与 Meridian Labs 维护的开源评测运行时 **Inspect**——可组合的 Task / Solver / Scorer、sandbox，以及可复现日志。一手入口为文档站与 GitHub 仓。
> **本文不写**：榜单污染 / scaffold 敏感性通史（见「评测与排行榜可靠性」）；SWE-agent → OpenHands 的编码 ACI / 生产 SDK 史线（见「代码智能体Harness史线」）；WorfBench 等某一基准的构造细节；lm-eval-harness / HELM 全文（仅对照表一行）。
> **材料口径**：无单一学术论文 PDF、无 arXiv 号；数字与 API 名锚定官方文档 / README（文档访问日期 2026-09-22）。文档站未写死的版本号、星标瞬时值、未核对照片内数字一律不写或标「以页面为准」。

---

## 一、材料元信息

| 材料 | 标识 | URL | 角色 |
|---|---|---|---|
| **文档站（主锚）** | Inspect 官方文档 | https://inspect.aisi.org.uk/ （访问日期 2026-09-22） | Task / Solver / Scorer、sandbox、logs、view |
| **代码仓** | `UKGovernmentBEIS/inspect_ai` | https://github.com/UKGovernmentBEIS/inspect_ai | 安装、开发、引用；文档入口回链 |
| **子页（跟读）** | solvers / scorers / tasks / sandboxing / eval-logs / log-viewer | 同站路径 `*.html` | 本笔记字段源 |
| **对照一行（非主锚）** | EleutherAI `lm-evaluation-harness` README | https://github.com/EleutherAI/lm-evaluation-harness | 见 §二表；**不展开** |

**安装（文档 Getting Started）：** `pip install inspect-ai`；VS Code 可选「Inspect」扩展；模型侧另装 provider 包并设 API key（例：`openai` / `anthropic` / `google-genai` / HF）。

**官方软件引用（文档页脚 BibTeX，非论文）：**

`bibtex
@software{UK_AI_Security_Institute_Inspect_AI_Framework_2024,
 author = {AI Security Institute, UK},
 title = {Inspect AI: Framework for Large Language Model Evaluations},
 date = {2024-05},
 url = {https://github.com/UKGovernmentBEIS/inspect_ai},
 langid = {en}
}
`

**一句话抓手：** Inspect 把一次评测收成 **`Task(dataset, solver, scorer[, sandbox, …])`**——Solver 改写 / 驱动 `TaskState`（含工具与 agent 环），Scorer 对照 `target` 出分，sandbox 把不可信代码执行隔到 Docker/K8s/云机等，日志用 `.eval` + `inspect view` / `inspect log export-config` 闭合 **eval → log → 再跑** 复现环。

---

## 二、议题边界与对照

### 2.1 本文只回答什么

| 问题 | 本文 | 相关笔记 |
|---|---|---|
| 榜单分数为何不可信 / 污染 / scaffold 敏感？ | **不写** | 安全与评测/评测与排行榜可靠性.md |
| 编码 agent 的 ACI / 生产 SDK 史？ | **不写** | Harness/智能体与工具/代码智能体Harness史线.md |
| 工作流 DAG 是否生成对？ | **不写** | Harness/EvalHarness/WorfBench工作流基准.md |
| 如何**声明并跑**一个可组合、可沙箱、可复现的 LLM/agent 评测？ | **主文** | — |

### 2.2 与 lm-eval-harness（一行对照，止于此）

| | **Inspect（本文）** | **EleutherAI lm-evaluation-harness（对照）** |
|---|---|---|
| README / 文档自述重心 | Frontier / agent / 工具 / **sandbox** / 日志可视化；可组合 Task·Solver·Scorer | 「统一框架，在大量不同评测任务上测生成式 LM」；Open LLM Leaderboard 等后端叙事（README Overview） |
| 本仓库跟读深度 | **全文跟读文档原语** | **仅此一行**；不写 task YAML / fewshot / vLLM 细节 |

---

## 三、核心组合：Task = Dataset + Solver + Scorer

文档首页与 Tasks 页把 **Task** 定义为评测集成单元：最少是 **dataset + solver + scorer**（可再加 `sandbox`、`epochs`、`setup`/`cleanup`、limits、`model_roles` 等）。用 `@task` 装饰的函数返回 `Task(...)`，供 `inspect eval` / `eval()` 发现与执行。

### 3.1 Dataset（样本合同）

- 典型列：`input`（提示）与 `target`（理想答案或评分指导）。
- 加载：`hf_dataset`、`json_dataset`、`csv_dataset`、内存列表等；`FieldSpec` 可把远端列名映射到 `input`/`target`（文档 SimpleQA 例：`problem`→`input`，`answer`→`target`）。
- Sample 还可带：`choices`（选择题）、`files` / `setup` / 每样本 `sandbox`（见 §五）。

### 3.2 Solver：对 `TaskState` 的变换计划

**角色（Solvers 页）：** 系统提示、prompt engineering（如 CoT）、调用模型、self-critique、多轮对话、**agent scaffold**。Task 有一个顶层 solver（任意 Python，或 **chain** 组合多个 solver 组件）。

**简化后的 `TaskState`（文档示意）：**

`text
TaskState:
 messages: list[ChatMessage] # 由 input 衍生，经模型交互扩展
 output: ModelOutput # 求解完成后的「最终」输出
 # 另有 sample_id / target / tools / metadata / scores 等（见文档表）
`

**Solver 协议：** `async def solve(state, generate) -> TaskState`；`generate` 是便利函数（用当前 state 调模型、追加 assistant、写 `output`）。`@solver` 注册名称与参数，便于日志与 CLI/`--solver` 替换。

**内置组件（文档列表，跟读用）：**

| Solver | 作用（据文档） |
|---|---|
| `system_message` / `user_message` / `prompt_template` | 插入或改写 chat |
| `chain_of_thought` | 改写用户提示，要求末行给最终答案 |
| `generate` | `return await generate(state)`；未指定 solver 时的默认 |
| `use_tools` | 设定 `generate` 可用工具集 |
| `self_critique` | 用（可另选）模型批判再 regenerate |
| `multiple_choice` | 展示 A/B/C/D；**配对** `choice()` scorer；内部已 `generate` |

文档例（组合）：`system_message` → `prompt_template` → `generate` → `self_critique`，scorer 用 `model_graded_fact()`。

**Agent 路径（首页 CTF 例，点到为止）：** `react(...)` + `bash()` / `todo_write()`，`attempts=3`，`sandbox="docker"`，scorer `includes()`——说明 Solver 可升到 **reason–act–observe 环**，但本文不展开 Agents 专章全文。

**与 Task 的可替换性（Tasks 页）：** `--solver` / `eval(solver=…)` 可换策略；`setup=` 在换 solver 时仍先跑（动态 prompt / 初始化沙箱资源）；`task_with()` 可改外来包里硬编码的 solver/sandbox 而不改源码。

### 3.3 Scorer：从 `output` 相对 `target` 打分

文档：Scorer 判定 solver 是否在何种程度上命中 dataset 的 `target`；并声明 **metrics**（如 `accuracy`+`stderr`，或 `mean`+`stderr`）。

| 形态（文档 Overview） | 代表 API |
|---|---|
| 从 completion **抽取**答案 | `pattern`、`answer`（`ANSWER: X`）、`choice` |
| **文本匹配 / 相似度** | `includes`、`match`、`exact`、`f1` |
| **模型打分** | `model_graded_qa`、`model_graded_fact` |
| 其他量尺 | `math`（可选 `inspect-ai[math]`）、`perplexity` / `target_perplexity` |

要点：

- 匹配失败多为 `INCORRECT`（计 0）；`pattern`/`answer` 抽不出格式时可带 `reason="invalid_response_format"`。
- **离线重打分：** `inspect score log_file.eval --scorer …`（Tasks 页 Tip）；live eval 时 scorer 主要靠 `task_with` 覆盖，无通用 `--scorer` CLI。
- 自定义 scorer 应尽量填 `Score.answer` / `explanation`，便于 Log Viewer 诊断「抽答案失败 vs 真错」（Log Viewer「Scores and Answers」）。

### 3.4 最小可跑形状（文档 Hello）

**Benchmark（SimpleQA 思路）：**

`text
@task
def simpleqa():
 return Task(
 dataset = hf_dataset(..., sample_fields=FieldSpec(input=..., target=...)),
 solver = generate(),
 scorer = model_graded_qa(),
 )
# inspect eval simpleqa.py --model <provider/model>
# inspect view
`

**Agent + sandbox（CTF 思路）：**

`text
Task(
 dataset = json_dataset("challenges.json"),
 solver = react(prompt=..., tools=[bash(), todo_write()], attempts=3),
 scorer = includes(),
 sandbox = "docker", # 任务旁 Dockerfile / compose.yaml
)
`

CLI 与 Python 对等：`from inspect_ai import eval` → `eval(task_fn(), model="…")`。

---

## 四、配置叠层与「可组合」工程含义

Tasks「Configuration」把覆盖分成四层（后者覆盖前者）：

`text
Task 定义 → task_with() → .env / INSPECT_EVAL_* → eval() / CLI
`

跟读抓手：

1. **同一 Task，换 elicitation**：`--solver` / `-S attempts=5`，不必改数据集。
2. **同一 Task，换被测模型与温度**：`--model`、`--temperature`、`--run-config`。
3. **模型打分角色**：`model_roles={"grader": "…"}` + solver/scorer 内 `get_model(role="grader")`。
4. **论文级复现配置**：`--run-config run.yaml` 可打包 task / model / generate_config / solver / eval_config；也可从日志 `inspect log export-config` 反导出（见 §六）。

这与「只报一个榜上分数」不同：Inspect 把 **scaffold（solver）与环境（sandbox）写成一等公民参数**，呼应「评测与排行榜可靠性」中的敏感性警告，但本文只立 **API 轴**，不写污染案例通史。

---

## 五、Sandbox：不可信执行的隔离面

### 5.1 为何需要

Sandboxing 页：工具调用本身在评测主进程；但 **bash / python / 编辑 / 浏览器** 等常要在隔离环境跑——执行任意代码、按样本挂文件系统、或搭网络主机（如网络安全评测）。**内置工具**中 `bash()`、`python()`、`text_editor()`、`web_browser()` 等需要 sandbox。

重要澄清（文档原文意）：

> 声明 `sandbox=` **不会**自动把整个 solver/scorer 搬进容器；只有经 `sandbox()` 接口请求的工作在容器内。评测编排与模型 API 仍在主机侧。

### 5.2 绑定与类型

| 绑定层 | 说明 |
|---|---|
| `eval()` / CLI `--sandbox` | 最高优先（类型层） |
| `Task(sandbox=…)` | 任务默认 |
| `Sample.sandbox` | 每样本；**同类型时**样本侧 compose/Dockerfile **优先** |

文档表（类型；以文档为准）：

| Type | 包 | Dockerfile 兼容（文档列） |
|---|---|---|
| `docker` | 内置 | Yes |
| `local` | 内置 | No（本机，无隔离） |
| `k8s` | `inspect-k8s-sandbox` | Yes |
| `daytona` / `modal` | `inspect-sandboxes` | Yes |
| `ec2` / `proxmox` / `vagrant` | 各自扩展包 | No（文档列） |

配置发现：任务目录下自动找 `Dockerfile` / `compose.yaml`；或 `sandbox=("docker", "attacker-compose.yaml")`；或编程式 `SandboxEnvironmentSpec` + `ComposeConfig`。

**网络默认：** 自动生成的 compose 含 `network_mode: none`。自备 compose **替换**而非扩展该默认——若需出网，文档建议省略 `network_mode`（项目网络隔离但仍可出站），慎用共享 `bridge`。

### 5.3 工具侧合同：`SandboxEnvironment`

经 `sandbox()` / `sandbox("victim")` 取得环境后，主要方法（文档）：

| 方法 | 用途 |
|---|---|
| `exec(cmd, …)` | 跑命令；输出默认上限约 **10MB**（可 `INSPECT_SANDBOX_MAX_EXEC_OUTPUT_SIZE`）；溢出时内置 provider **前端截断**（可能静默不完整） |
| `read_file` / `write_file` | 文件；读上限默认约 **100MB**，超限抛错 |
| `connection()` | 可选：登录容器的连接信息 |
| `exec_remote` | 流式 / 可 await 的远端执行变体 |

Sample 级：`files`（可 `env:path` 前缀写到命名环境）、`setup` bash（拷文件后执行）。多服务 compose 时：名为 `default` 或 `x-default: true` 或列表首个为默认；`sandbox_default("victim")` 可临时改默认。

### 5.4 运维与资源（Infra 辅）

- Docker Engine **≥ 24.0.6**；Compose **≥ 2.21.0**（从 registry 拉镜像时 **≥ 2.22.0**）（文档 Installation）。
- `max_sandboxes`：并行沙箱上限（Docker 默认约 **2× CPU**）；会有效变成全局 `max_samples` 上限。
- `inspect sandbox cleanup docker`；调试用 `--no-sandbox-cleanup` 保留容器再 `docker exec`。
- `--sandbox-prebuilt` / `INSPECT_EVAL_SANDBOX_PREBUILT`：气隙机跳过 build，只校验本地镜像。

**与编码 harness 的分工：** 此处 sandbox 服务 **评测样本的工具执行隔离与复现**；不是 SWE-agent「给人/LM 的仓库 ACI」产品叙事，也不是 OpenHands「本地默认、沙箱 opt-in」的生产 SDK 史（详见「代码智能体Harness史线」）。

---

## 六、日志与复现闭环

### 6.1 每次 eval 必写日志

- 默认目录：`./logs`；可 `--log-dir` / `INSPECT_LOG_DIR`（相对路径相对 `.env` 所在目录解析）。
- 格式：自 **v0.3.46** 默认 **`.eval`**（二进制，体积与增量读样本优化）；亦可 `.json`。文档强调：**用 Log API 读写，勿手写解析 JSON 当唯一路径**（底层格式可变）。
- 自 **0.3.206** 起：消息去重 + zstd 等优化；agent 类基准文档称可见约 **10:1** 量级体积改善（以文档表述为准）。

**`EvalLog` 顶层字段（文档表）：** `status`、`eval`（任务/模型等）、`plan`（solvers + generate config）、`results`、`stats`、`error`、`samples`、`reductions`、`tags`/`metadata` 等。

### 6.2 查看与分析

| 方式 | 命令 / API |
|---|---|
| 交互查看 | `inspect view`（默认端口 **7575**）；VS Code Inspect 扩展 |
| 列出 / dump | `inspect log list`、`inspect log dump`（任意格式 → 明文 JSON） |
| Python | `list_eval_logs`、`read_eval_log(..., header_only=True)`、`read_eval_log_samples` 流式 |
| 发布静态站 | `inspect view bundle`（可推 HF Spaces `hf/org/space`） |

Log Viewer 强调：钻 **Messages**（工具多轮）、**Scoring**（抽取是否失败）、按分数过滤——对齐「scorer 工程」而非只看聚合 accuracy。

### 6.3 失败可续跑与样本保留

- 失败/中断仍写日志 → `inspect eval-retry <log>` / `eval_retry(...)`；**新文件**，保留原 `task_id`。
- 仅对 **`@task` 函数**创建的任务可重建。
- 复用已完成样本需要稳定 `id`；若 `dataset.shuffle()`，文档会警告且可能不重用。
- `max_samples` 过大 → 完成样本落盘变稀 → 中断时可恢复样本变少（与 sandbox 并发调参相关）。

### 6.4 配置往返：eval → log → 再 eval

文档明确闭合：

`text
inspect log export-config logs/my_run.eval > run.yaml
inspect eval --run-config run.yaml
`

即把已实现的 task / model / roles / generate / solver / eval 设置导出为可再喂给 `--run-config` 的 YAML——这是本文「**日志复现**」的主工程语义（不是「同一随机种子保证逐 token 比特级相同」，文档未作该承诺）。

附加：`edit_score` / `edit_eval_log` 带 provenance 的事后改分与标签；`inspect score` 换 scorer 重打。

### 6.5 安全相关开关（文档点名即止）

- `--log-refusals`：拒绝计警告；`--fail-on-refusal` 可使样本失败。
- `--log-model-api` / `--no-log-model-api`：原始 API 载荷记录粒度。
- `--no-log-images`：大 `.json` 日志时可关媒体保留。

---

## 七、跟读清单（建议顺序）

1. 首页 Hello：SimpleQA（`generate` + `model_graded_qa`）与 CTF（`react` + `sandbox="docker"`）。
2. Solvers → TaskState / `@solver` / chain；再扫 Scorers 表。
3. Tasks：参数 `-T`、`--solver`、`setup`、`task_with`、四层配置、`export-config`。
4. Sandboxing：`sandbox()` 接口、compose `network_mode`、limits、cleanup。
5. Eval Logs + Log Viewer：`.eval`、`eval-retry`、流式读样本、bundle。
6. （可选）Evals 列表：https://inspect.aisi.org.uk/evals/ —— **200+** 预置评测（文档数字）；本文不逐条抄基准。

LLM 辅助文档索引（站点提供）：`llms.txt` / `llms-guide.txt`；页面可 Copy Page 为 Markdown。

---

## 八、与相关笔记的分工

| 相关笔记 | 本文只取 | 本文明确不写 |
|---|---|---|
| 评测与排行榜可靠性 | 「分数绑 scaffold / 污染」动机一句 | 榜通史、污染检测、HELM 方法论全文 |
| 代码智能体Harness史线 | 「隔离执行 / 可复现环境」抽象需求 | ACI 命令表、OpenHands 四包、SWE resolve % |
| 智能体工具与长程任务 | ReAct / 工具环存在 | MCP 协议史、旗舰 System Card 长程 |
| WorfBench工作流基准 | agent 任务可被 harness 承载 | WorFEval 子图匹配公式与主表 |

---

## 九、待核实 / 故意不写

- 以文档站与 GitHub 为一手入口；不以二手博客补「论文贡献列表」。
- GitHub **瞬时 star / fork / release tag**：页面会变；引用以仓 URL + 文档版本行为为准。
- 具体基准得分、某模型在 Inspect Evals 上的数字：需另开评测日志笔记，本文不写未核数字。
- Agents / Tools / Extensions 专章全文：本文只保留 CTF/`react` 与 sandbox 工具链入口。

---

## 十、摘要

**路径：** Harness/EvalHarness/Inspect评测Harness.md

**要点：** 以 UK AISI Inspect **文档站 + GitHub** 为一手入口，写清开源评测运行时三原语——**Task** 组装 **Dataset + Solver + Scorer**；**Solver** 变换 `TaskState`（可 chain / agent）；**Scorer** 相对 `target` 抽取或模型打分；**sandbox**（Docker 等）隔离工具侧 `exec`/文件，编排仍在主机；**日志**默认 `.eval`，经 `inspect view` / `eval-retry` / `inspect log export-config → --run-config` 形成复现环。分工：≠榜单通史、≠编码 harness、lm-eval 仅一行对照。

## 相关笔记

- [[Inspect评测Harness|Inspect Eval Harness]]
- [[NemotronCC数据策展|Nemotron-CC 数据策展]]
- [[评测与排行榜可靠性|评测与排行榜可靠性]]
- [[代码智能体Harness史线|代码智能体 Harness 史线]]
- [[WorfBench工作流基准|WorfBench 工作流基准]]
- [[智能体工具与长程任务|智能体、工具与长程任务]]
