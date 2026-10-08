---
title: "气候科学/政策 Agent：ClimateAgent + ClimateAgents"
topic: 气候科学Agent
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2511.20109
 - https://arxiv.org/abs/2603.13840
arxiv: ["2511.20109", "2603.13840"]
related: ["天气气候基础模型", "地球系统基础模型ESFM", "科研智能体", "智能体工具与长程任务", "代码智能体Harness史线"]
code_climateagent: "https://github.com/Relaxed-System-Lab/ClimateAgent"
retrieval_cutoff: 2026-09-14
timezone: Asia/Shanghai (CST)
---

# 气候科学/政策 Agent：ClimateAgent + ClimateAgents

> **主要来源**：[CLIMATEAGENT: Multi-Agent Orchestration for Complex Climate Data Science Workflows](https://arxiv.org/abs/2511.20109)（Li、Kim 等，HKUST，简称 ClimateAgent，v1 2025-11-25，v2 2026-09-14）；[ClimateAgents: A Multi-Agent Research Assistant for Social-Climate Dynamics Analysis](https://arxiv.org/abs/2603.13840)（Shan，哈工大，简称 ClimateAgents，v1 2026-03-14）；[Relaxed-System-Lab/ClimateAgent README](https://github.com/Relaxed-System-Lab/ClimateAgent)（截至 2026-09-14）。
> **研究线**：架构思想（角色分层、共享工作流上下文、API 自省与自纠，主）· 评测字段（任务完成率、报告质量四维分、社会—气候案例与自动评审分，辅）
> **范围与相邻笔记**：
> - ≠ [[天气气候基础模型]]：本篇不写 Aurora 等格点地球场基础模型的预训练与预报；本篇对象是 LLM 多智能体工作流。
> - ≠ [[科研智能体]]：本篇不写 The AI Scientist、ChemCrow 的通用科研闭环与化学工具链。
> - ≠ [[代码智能体Harness史线]]：本篇不写 SWE-agent、OpenHands 等通用编码智能体的 harness。
>
> **意义**：气候研究的瓶颈之一是把一个分析问题变成「找数据、下数据、处理、出图、写报告」的完整工作流，通用 LLM 智能体缺少气候数据接口的语境，常在数据请求与数组维度上出错。ClimateAgent 用编排、规划、数据、编码四类智能体加持久上下文与多候选自纠，在 85 个真实任务上全部生成报告，报告质量 8.32 分，远高于同用 GPT-5 的单模型基线（3.26）与 GitHub Copilot（6.27）；ClimateAgents 则把多智能体用在社会经济指标与气候政策的探索上。作者称两个基线都以 GPT-5 为底层模型，对照的是专长分工与单模型推理之差。

**一句话**：ClimateAgent 把气候数据分析拆给编排、规划、数据、编码四类智能体，靠持久上下文传递中间产物、靠多候选脚本与迭代调试自纠；ClimateAgents 用感知、推理、操作三层和 11 个角色探索社会—气候问题。

---

## 一、问题背景

气候数据规模大、格式异构，ERA5 等再分析数据要经 Copernicus 气候数据存储（CDS）或 ECMWF 的 API 下载，参数约定不统一；分析又依赖 xarray、CDO、TempestExtremes 等专门工具。ClimateAgent 指出（§1），通用 LLM 智能体与静态脚本缺少气候领域语境与灵活性，生成代码错误率高，非专家难以上手。另一类问题来自社会—气候交叉研究：社会经济指标、碳排放与政策之间的关系需要检索、统计与解释结合，ClimateAgents 认为窄的指标预测模型不足以支持这种探索。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2023-04 | [ChemCrow](https://arxiv.org/abs/2304.05376) | 给 LLM 接上化学专家工具，在 ReAct 循环中完成专业任务；ClimateAgent 在相关工作中把它列为科学流程自动化的先例 |
| 2024-01 | [ClimateGPT](https://arxiv.org/abs/2401.09646) | 训练气候领域专用 LLM，走「专科模型」路线 |
| 2025-11 | ClimateAgent v1 | 多智能体编排端到端气候数据工作流，并发布 Climate-Agent-Bench-85 |
| 2026-03 | ClimateAgents | 多智能体研究助手用于社会—气候动力学 |
| 2026-09 | ClimateAgent v2 | 现行版本 |

## 三、ClimateAgent：气候数据工作流的多智能体编排

### 3.1 持久上下文（§3.1）

给定任务 $T$，Plan-Agent 把它分解为有序子任务 $P=[s_1,\ldots,s_n]$，专长智能体依次执行，并更新工作流上下文 $C_i=\mathrm{Execute}(C_{i-1},s_i,A_k)$。$C_i$ 记录任务、计划、代码、数据、结果与日志，每个子任务后序列化保存，同时充当智能体之间的通信协议、断点恢复的检查点与可复现的溯源记录。

### 3.2 四类智能体与自纠（§3.2–3.4）

| 智能体 | 职责 | 自纠机制 |
|---|---|---|
| Orchestrate-Agent | 建实验目录、持久化上下文、调度全局进度 | — |
| Plan-Agent | 按领域模式分解任务（如气候态 → 距平 → 极端事件 → 报告） | — |
| Data-Agent | 动态查询 CDS / ECMWF API 的参数约定，生成下载脚本 | 一次生成 8 个候选脚本，顺序尝试直到成功 |
| Coding-Agent | 用 xarray、cartopy 等做分析、可视化与报告 | 最多 3 轮迭代精炼，每个候选最多 5 次调试；另用 LLM 做语义校验，抓「能运行但科学上错」的结果 |

### 3.3 基准 Climate-Agent-Bench-85（§4）

85 个真实工作流任务，覆盖大气河、干旱、极端降水、热浪、海表温度、热带气旋六个领域；按难度分为单数据源的简单任务 25 个、多源或多步的中等任务 30 个、需动态调用外部工具的困难任务 30 个。每个任务规定自然语言目标、必须使用的数据与工具和严格的输出约定，并附参考代码与专家报告。报告由 GPT-4o 多模态裁判对照专家参考，按可读性、科学严谨性、完整性、可视化质量四维打 1–10 分。

### 3.4 结果（§5，Table 1–3）

两个基线底层都是 GPT-5，作者称这样能隔离专长分工相对「单模型推理 + 执行校验」的作用：一个是 best-of-4 采样、取第一个能在沙箱跑通的代码，另一个是 GitHub Copilot 的 Agent 模式。

| 领域 | GPT-5 | Copilot | ClimateAgent |
|---|---:|---:|---:|
| 大气河 | 3.05 | 6.78 | 7.32 |
| 干旱 | 7.87 | 6.87 | 8.57 |
| 极端降水 | 0.62 | 5.58 | 8.43 |
| 热浪 | 3.98 | 8.30 | 9.15 |
| 海表温度 | 4.28 | 8.10 | 8.88 |
| 热带气旋 | 0.00 | 2.65 | 7.85 |
| 全部任务 | 3.26 | 6.27 | 8.32 |

ClimateAgent 报告生成成功率 100%；四维中完整性最低（7.75），科学严谨性最高（8.72）（Table 2）。基线在极端降水与热带气旋这类复杂领域几乎失效。GPT-5 基线在 35 个失败任务上的错误分类（Table 3）中，数组维度或键错误 9 个、数据请求错误 6 个，在有名目的类别中居前两位（另有杂项 8 个），正是 Data-Agent 与 Coding-Agent 自纠所针对的问题。

**人机一致性（附录 F，Table 8）**：专家分与 LLM 裁判分的平均绝对差，五个领域在 0.325–0.55 之间，大气河达 1.92，作者认为该领域的空间诊断与可视化更容易放大分歧。

## 四、ClimateAgents：社会—气候动力学的研究助手

**三层结构（§3）**：受 Minsky《心智社会》启发，智能来自众多有限能力智能体的组织化交互。感知层把文本、表格、图像转成结构化表示；推理层由 LLM 做推断、规划与协调；操作层调用检索、统计分析与可视化工具。实现基于 AutoGen 与 GPT-4 系列模型，共 11 个角色（Table 1），包括气候策略师、气候科学家、政策规划者、批评者、数据建模者、代码开发者、图表解读者、知识检索者与事实核查者等。

**案例（§4）**：对气候预测文献做主题聚类；在文献特征上做相关分析与回归，再交给政策解释模块；从全连接因果图出发用 CAM 剪枝得到候选因果结构，作者强调剪枝不能替代混杂控制；以世界银行的清洁燃料可及性与城市化指标演示多智能体问答。

**评测**：用 Stanford Agentic Reviewer 的七维量表评系统生成的报告，总分 6.4；实验严谨性一项最低（5 分），作者承认需要更强的实验验证。

## 五、两篇对照

| 维度 | ClimateAgent | ClimateAgents |
|---|---|---|
| 问题 | 气候数据工作流自动化（获取 → 处理 → 分析 → 报告） | 社会—气候动力学探索与政策叙述 |
| 编排 | 编排 / 规划 / 数据 / 编码四类智能体 + 持久上下文 | 感知 / 推理 / 操作三层 + 11 个角色 |
| 数据接口 | CDS、ECMWF、ERA5、TempestExtremes 等 | 联合国、世界银行指标与 IPCC 报告 |
| 评测 | 85 任务基准、报告四维分、人机一致性 | 自动评审分与案例 |

## 六、意义

ClimateAgent 的贡献主要在工程层面：把气候数据 API 的参数语境、多候选脚本与迭代调试做成系统机制，使「跑不通」从常态变成少数，并配套了可复现的 85 任务基准与人机一致性检查。基线错误集中在数据请求与数组维度，与作者「通用智能体缺少气候数据接口语境」的诊断一致。ClimateAgents 把同样的多智能体思路扩到社会科学一侧，但评测仍停留在案例与自动评审。两篇的共同做法是把领域接口知识写进角色分工，并保留可审计的中间产物。

## 七、局限与待核实

- **评测依赖 LLM 裁判**：ClimateAgent 的报告分来自 GPT-4o，大气河领域与专家分差距明显；100% 指报告生成成功，不等于结论都正确。
- **ClimateAgents 证据弱**：没有定量基准，只有案例与一次自动评审；§4.2 写「the report produced by ClimateAgent」，与题名的 ClimateAgents 不一致，按上下文理解为该论文自身系统的报告；文中称代码托管在 GitHub，但没有给出地址。
- **ClimAgent 已撤回**：[ClimAgent](https://arxiv.org/abs/2604.16922)（开放式气候建模与 ClimaBench）2026-05-29 的 v3 为撤回版本，理由是提交时未获全部合作者同意，本篇不引用其内容。
- **版本**：本篇据 ClimateAgent v2（2026-09-14），未与 v1 比对。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[天气气候基础模型]] | 对照：两者都处理气候数据；那篇是格点场预报的基础模型，本篇是调用数据 API 的 LLM 工作流 | 模型结构与预报技巧 |
| [[地球系统基础模型ESFM]] | 对照：那篇的地球系统基础模型是预报骨干，并把本篇列为多智能体编排一侧 | 地球系统模型训练与评测 |
| [[科研智能体]] | 上游：通用科研智能体与 ChemCrow 式工具代理在该篇，ClimateAgent 在相关工作中引 ChemCrow 为先例 | AI Scientist 与 ChemCrow 细节 |
| [[智能体工具与长程任务]] | 背景：LLM 加工具的多步任务 | MCP 与长程任务通史 |
| [[代码智能体Harness史线]] | 对照：ClimateAgents 把 OpenHands、SWE-Agent 列为通用智能体先例；Coding-Agent 的调试循环与编码智能体同构 | 编码智能体 harness |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [ClimateAgent](https://arxiv.org/abs/2511.20109) §3、§5、附录 F | 四类智能体与自纠、主结果、人机一致性 |
| 2 | [ClimateAgents](https://arxiv.org/abs/2603.13840) §3–4 | 三层结构、11 个角色与案例 |
| 3 | [Relaxed-System-Lab/ClimateAgent README](https://github.com/Relaxed-System-Lab/ClimateAgent) | 代码与基准 |
| 4 | [[天气气候基础模型]] | 气候数据的另一条 AI 路线 |
