---
title: "Agentic RL 景观与能力模块"
topic: AgenticRL景观与能力模块
date: 2026-09-25
lines: [架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2509.02547
 - https://arxiv.org/pdf/2509.02547
 - https://openreview.net/forum?id=RY19y2RI1O
 - https://github.com/xhyumiracle/Awesome-AgenticLLM-RL-Papers
arxiv: ["2509.02547"]
related: ["GRPO与DAPO算法族", "ToRL工具集成强化学习", "MiMoV26智能体强化学习短报"]
retrieval_cutoff: 2026-09-25
timezone: Asia/Shanghai (CST)
archived: 2026-09-28
---

# Agentic RL 景观与能力模块

> **定位**：对齐与强化学习横切入口——把近一年「Agentic RL」收成**能力模块地图**：规划 / 工具 / 记忆 / 推理 / 自改进。主锚 Zhang 等综述 *The Landscape of Agentic Reinforcement Learning for LLMs: A Survey*（arXiv **2509.02547v5**；TMLR **01/2026**）。
> **一句话**：Agentic RL = 把 agent 的各项能力当成**可学习策略**，在长程、部分可观测环境里用 RL **联合优化**，而不是只对单轮文本打分。
> **范围与相邻笔记**：
> - **≠ [[GRPO与DAPO算法族]]**：不写组相对优势、Clip-Higher、去偏目标等**单步/可验证奖励算法细节**；算法族在此只是「优化器槽位」。
> - **≠ [[ToRL工具集成强化学习]]**：不写解释器进 env、观测 mask、$C$ 次调用闸门等**工具 RL 专线**；本篇只在「工具」格点名 ToRL 所在方向。
> - **≠ [[MiMoV26智能体强化学习短报]]**：不写 batch / grader / multi-harness 的**产品扩算力轴**。
> - 综述另列 **感知（perception）** 与任务域应用；本篇地图按五模块收束，不展开 GUI / 代码 / 搜索专章。

---

## 一、材料元信息

| 材料 | 标识 | 角色 |
|---|---|---|
| **主文** | Zhang, Geng, Yu, Yin, Zhang 等，*The Landscape of Agentic Reinforcement Learning for LLMs: A Survey* | 能力×任务双轴分类；形式化 LLM RL → Agentic RL |
| **版本** | arXiv:**2509.02547v5** \[cs.AI\]（**17 Apr 2026**）；首挂 **2 Sep 2025**；TMLR **01/2026**；OpenReview `https://openreview.net/forum?id=RY19y2RI1O`；**95** 页 | 本稿能力划分与代表方向名的唯一依据 |
| **辅·索引** | `https://github.com/xhyumiracle/Awesome-AgenticLLM-RL-Papers`（重定向至维护仓） | 开源环境 / 论文清单；不另作数字源 |

**形式化抓手（§2）：** 偏好式后训练常被写成 **$T=1$** 的退化 MDP（单 prompt → 单回复 → 标量奖励）；Agentic RL 写成 **POMDP**：多步、部分观测、动作 = 文本 ∪ 环境/工具动作，目标是轨迹折扣回报。

---

## 二、Agentic RL：一句话与位置

**定义（文内）：** 不再把 LLM 只当「对齐单轮输出」的条件生成器，而把它当作嵌在序贯决策环里的**可学习策略**；RL 用来获得规划、推理、工具、记忆与自反思等 agentic 能力，以支撑部分可观测、动态环境中的长程行为。

相对两条旧线：

| 旧线 | 本篇位置 |
|---|---|
| **LLM RL / 偏好后训练** | 单步文本质量；本篇视作内圈，不重写 RLHF/DPO 通史 |
| **提示式 LLM Agent** | 有规划/工具/记忆模块，但多为静态启发式；本篇关心 **RL 如何把模块变成可适应策略** |

文内主旨：RL 是把这些能力从「固定流水线」推进到「可适应行为」的关键机制。

---

## 三、能力模块地图（规划 / 工具 / 记忆 / 推理 / 自改进）

下表按综述 §3 能力轴整理；每格 **2～4 句白话 + 代表方向名**（名称均出自综述）。感知与「长程信用分配」等其它项见文 §3.6–3.7，此处不展开。

| 模块 | 白话要点 | 代表方向（综述点名） |
|---|---|---|
| **规划** | 先想「怎么走」：把目标拆成多步动作。RL 有两条用法——**外挂**：不改（或少改）LLM 本身，训价值/启发函数去导 MCTS 等搜索；**内化**：把 LLM 直接当规划策略，用环境成败轨迹更新。远景是两者合成：既会快出计划，也会学「何时深思、何时剪枝」。 | 外挂：RAP、LATS、Planning without Search；内化：ETO、VOYAGER、AdaPlan / PilotRL、Planner-R1、RLTR |
| **工具** | 从「会跟示例调用」推进到「为结果自己决定何时/用哪个工具」。早期 ReAct / SFT 轨迹易锁死模式；**工具集成 RL（TIR）** 把代码执行、检索等嵌进同一次推理 rollout，用结局或过程奖励学策略。长程瓶颈是：**哪一次调用**该记功/记过（时间信用分配）。 | ReAct 式调用 → ToolRL、ReTool、AutoTIR、**ToRL**、ARTIST、OTC-PO、ASPO；长程信用：GiGPO、SpaRL |
| **记忆** | 记忆从「外挂只读库」变成 **RL 可控子系统**：存什么、取什么、何时忘。路径大致是：先用 RL 调 RAG **何时检索** → 再管 ADD/UPDATE/DELETE → 再到显式/隐式 **token 级**读写；结构化图谱记忆仍多靠启发式，RL 控图谱演化仍属前瞻。 | RAG 式：Memory-R1、Mem-α、Memory-as-action；token 级：MemAgent、MEM1、ReSum、Context Folding、MemGen；结构前瞻：Zep、A-MEM、G-Memory、Mem0 |
| **推理** | 借用快/慢双过程：快推理 ≈ 直觉、短链路；慢推理 ≈ 显式中间痕迹、可多步校验，常与 CoT + RL / test-time 扩展绑定（如 o1 / o3、DeepSeek-R1、DAPO 等族在文中的引用位置）。Agent 场景难在：环境多样导致训练不稳，以及慢推理的 **过思**；前瞻是快慢混合与自适应算力分配。 | 快 vs 慢；慢推理 RL / TTS：o1、o3、DeepSeek-R1、DAPO 等；混合 / 自适应 test-time scaling |
| **自改进** | 让 agent 从自己的错误里持续改。三层：(1) **口头反思**——同一次推理里生成→批评→改写，无梯度（Reflexion 等）；(2) **内化反思**——用 DPO/RL 把纠错写进参数；(3) **迭代自训**——自博弈、执行反馈出题、或集体轨迹库，减少对人工标注的依赖。更高一层是学「如何更好地反思」的元策略。 | 口头：Reflexion、Self-Refine、CRITIC、Chain-of-Verification；内化：KnowSelf、Reflection-DPO、DuPo；自训：R-Zero、Absolute Zero、TTRL、SiriuS、Self-Evolving Curriculum |

**读图方式：** 五格不是互斥产品名，而是**可被 RL 分别或联合优化的策略切片**；真实系统通常多格同时动（例如慢推理 + 工具 + 记忆）。

---

## 四、与算法族 / 工具 RL 的关系（一句表）

| 相邻笔记 | 本篇关系（只取接口） |
|---|---|
| [[GRPO与DAPO算法族]] | 提供 **PPO / GRPO / DAPO…** 等优化器；Agentic RL 在更长的 POMDP 轨迹上**调用**它们，本篇不展开目标函数 |
| [[ToRL工具集成强化学习]] | 落在上表「工具」格的 **TIR / 从 base 探索工具策略** 方向；本篇不写沙箱与超参专线 |
| [[MiMoV26智能体强化学习短报]] | 景观落到生产时的 **扩 batch × 多环境/harness × grader** 实例；本篇不写吞吐与评分器配方 |

---

## 五、交叉

- [[GRPO与DAPO算法族]]
- [[ToRL工具集成强化学习]]
- [[MiMoV26智能体强化学习短报]]

---

## 六、小结

Agentic RL 的景观入口可以压成一句话：**能力模块化 + RL 联合优化 + 长程 POMDP**。先认清五格地图各自在优化什么，再按需下钻到算法族、工具 RL 专线或产品扩算力短报——三篇相邻笔记与本篇互补，不互相重写。
