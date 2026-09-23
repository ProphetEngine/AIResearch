---
title: "Tool-use RL：ToRL——从基座模型缩放工具集成 RL"
topic: ToRL工具集成强化学习
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2503.23383
arxiv: ["2503.23383"]
related: ["GRPO与DAPO算法族", "代码智能体Harness史线", "智能体工具与长程任务", "DeepSeekR1推理训练深读", "推理时扩展TestTimeScaling"]
archived: 2026-09-22
---

# Tool-use RL：ToRL——从基座模型缩放工具集成 RL

> **定位**：工具集成强化学习主题轴——仓库内 **「把代码解释器嵌进 RL 环境、从 base 直接探索工具策略」** 专篇。相对纯 CoT 的 outcome RL（R1 / SimpleRL 等）与蒸馏轨迹再 SFT 的 TIR（ToRA / MathCoder 等），ToRL 证明：**工具调用本身可以当探索动作**，不必先模仿人类/更强模型的工具脚本。
> **攻坚线**：**架构思想（主）**——TIR rollout 环、沙箱选择、观测 mask、工具次数 $C$；**评测字段（辅）**——AIME/MATH 等相对「无工具 RL」与「Instruct-TIR」的增益、训练中 code ratio / pass ratio。
> **硬划界（禁止重写）**：
> - **禁止重写** [[GRPO与DAPO算法族]] 的 GRPO→DAPO 技巧清单（Clip-Higher / Dynamic Sampling / token-level loss / Overlong 等）。本篇只用到「**用 GRPO 做组相对 RL**」这一抽象槽位；超参见 §3.1，不展开目标函数变体。
> - **禁止重写** [[代码智能体Harness史线]] 的 SWE-agent ACI / OpenHands SDK（编辑器命令面、lint guardrail、生产 harness）。本篇沙箱是 **数学题上的 Python 解释器（Sandbox Fusion）**，不是软件工程 ACI。
> - **禁止重写** [[智能体工具与长程任务]] 旗舰工具环 / MCP / System Card 长程；[[DeepSeekR1推理训练深读]] 多阶段管线表；[[推理时扩展TestTimeScaling]] TTS 通史。
> **禁止编造**：数字、消融、奖励表一律锚定官方 PDF（2026-09-22 CST）与 GitHub README 自报表；图内未抽出可读曲线点标 **待核实读图**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文** | Li, Zou & Liu (SJTU / SII / GAIR), *ToRL: Scaling Tool-Integrated RL* | arXiv:**2503.23383v1** \[cs.CL\] **30 Mar 2025**；`https://arxiv.org/abs/2503.23383`（**10** 页 A4；CreationDate **2025-04-01** CST；565,259 bytes） | 从 **base** 做 Tool-Integrated RL；TIR 进 rollout；涌现工具策略与认知行为 |
| **辅·代码/数据/模型** | `https://github.com/GAIR-NLP/ToRL`（README；数据集 `data/torl_data`；HF `GAIR/ToRL` / `GAIR/ToRL-7B`） | 仓库自报：训练管线、**28k** 题、模型权重；依赖 **veRL** + **SandboxFusion** | 复现入口；与正文数字交叉核对 |

**一句话抓手：** 把 **代码解释器** 放进 RL 的 env 交互环（检测到 code fence → 暂停生成 → 执行 → 把 `output` 写回上下文 → 继续推理），并从 **未后训练的 Qwen2.5-Math base** 起训；ToRL-7B 在 AIME24 达 **43.3%**，相对同设置无工具 RL 约 **+14** 点、相对 Qwen2.5-Math-Instruct-TIR 约 **+17** 点（Abstract / Table 3）。

---

## 二、议题边界：工具进 RL 环，不是又一部 DAPO / ACI 专线

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[GRPO与DAPO算法族]] GRPO/DAPO** | 「有可验证终答就能做组相对 RL」；实验用 GRPO | Clip-Higher、动态采样、token-level loss、Dr.GRPO 去偏公式 |
| **[[代码智能体Harness史线]] ACI/harness** | 「隔离执行环境很重要」这一工程直觉 | SWE-agent 命令面 / OpenHands 四包 SDK / 生产失败率 |
| **[[智能体工具与长程任务]]** | 工具增强推理是产品能力切片 | MCP 协议史、旗舰 System Card 工具环 |
| **[[DeepSeekR1推理训练深读]] / 纯 CoT RL** | 无工具 baseline 对照（SimpleRL-Zero 等点名） | R1 冷启动→拒绝采样阶段表 |
| **经典 TIR（ToRA 等）** | SFT/蒸馏轨迹是「预定工具模式」反面教材 | 各家 TIR 数据集构造全文 |

### 2.2 问题立轴（跟读）

`
旧路 A：纯 CoT + outcome RL → 算不清 / 枚举不完时硬推
旧路 B：强模型蒸馏 TIR 轨迹 + SFT → 工具用法被锁死，难探索
新路 ：Code Interpreter ⊂ RL env → 从 base 用奖励自己学「何时写码、写什么、错了怎么办」
`

作者批评点（§1）：多数 TIR 靠蒸馏 + SFT；即便 Qwen-Math 等在 SFT 后再 RL，**工具如何嵌进 RL 框架**也不透明。ToRL 的主张是：**去掉先验 SFT 约束，让探索本身发现工具策略**。

---

## 三、方法骨架：TIR 轨迹形式 + ToRL 设计选择

### 3.1 数据集（§2.1）

- 源：NuminaMATH、MATH、DeepScaleR 等竞赛可验证题。
- 过滤证明题与验证标准模糊题 → **75,149** 可验证题。
- 再用 **LIMR**（Li et al., 2025）做 RL 数据蒸馏 / 难度平衡 → 最终 **28,740** 题（仓库称「28k」，与正文一致）。

### 3.2 TIR 形式化（§2.2）

给定模型 $M$、解释器 $I$、问题 $Q$，第 $k$ 步轨迹：

$$
s_k=\{r_1,c_1,o_1,\ldots,r_k,c_k,o_k\}
$$
$$
(r_k,c_k)=M(Q\oplus s_{k-1}),\quad o_k=I(c_k),\quad s_k=s_{k-1}\oplus r_k\oplus c_k\oplus o_k
$$
其中 $r$=自然语言推理，$c$=代码，$o$=执行结果。循环直到给出终答。相对纯 CoT：中间步可被 **可执行反馈** 校正（Fig.2 CoT vs TIR 对照题）。

### 3.3 TIR Rollout 进 RL 环（§2.3.1）——本篇核心

**提示模板（Fig.3，文内原文要点）：** User/Assistant 对话；要求「integrate natural language reasoning with programs」，终答放 `\boxed{}`。

**交互协议（跟读）：**

1. 模型正常采样文本。
2. 检测到代码终止标识（文述  `output  检测；即写完 code fence 后准备要输出）→ **暂停生成**。
3. 抽出最新 code block → 解释器执行。
4. 把结果以  `output\nOBSERVATION\n` 形式 **插入上下文**。
5. 继续生成 NL 推理或下一段代码；失败时 **故意回传错误信息**（作者假设错误诊断能促进后续写出可执行码）。

**效率闸门 $C$：** 单次回复允许的最大工具调用次数。超过后 **忽略后续执行请求**，强迫切回纯文本推理。默认实验 $C=1$（§3.1）。

### 3.4 四项工程设计选择（§2.3.2）——只记「工具进 env」相关

| # | 选择 | 文内结论 |
|---|---|---|
| 1 | **Tool call 频率 $C$** | 调用越多 GPU idle 越重；$C$ 换性能但换吞吐 |
| 2 | **执行环境** | 先试 qwen-agent Python executor（低延迟但与训练进程 **不隔离**，segfault 可拖垮训练）→ 改用 **Sandbox Fusion**（隔离稳，延迟略高） |
| 3 | **错误信息裁剪** | Sandbox 冗长 traceback 只保留 **最后一行**（如 `NameError: ...`），控上下文长度 |
| 4 | **Sandbox Output Masking** | **loss 计算时 mask 掉 OBSERVATION**，避免模型背诵具体输出、促可泛化推理 |

> **与 [[代码智能体Harness史线]] 划界：** 这里的「沙箱」是 RL rollout 里的 **数值/符号计算解释器**；不是 SWE-agent 的 LM-友好文件系统 ACI。只借用「隔离执行很关键」一句，不展开 harness 史。

### 3.5 奖励设计（§2.3.3）

| 信号 | 值 |
|---|---|
| 答案正确 | $+1$ |
| 答案错误 | $-1$ |
| 代码可执行 | $0$（附加项） |
| 含不可执行代码 | $-0.5$（Code Executability Reward） |

**默认实验只保留答案正确性奖励**；可执行性惩罚在 §3.3.2 消融——**未提升**最终表现（作者猜测：惩罚会诱使模型写过简代码以避错，反而伤解题）。

### 3.6 训练/评测设置（§3.1）——算法槽位点到为止

- 框架：**veRL**；解释器：Sandbox Fusion。
- 算法：**GRPO**（rollout batch **128**，每题 **16** 条样本）。
- 为增强探索：**省略 KL loss**；temperature **1**。
- 基座：**Qwen2.5-Math** 1.5B / 7B **Base**（非 Instruct 起训）。
- 默认 $C=1$；评测 greedy（temp **0**）。
- 基准：AIME24、AIME25、MATH500、OlympiadBench、AMC23。

> **不在此复述** GRPO 目标式 / DAPO 四技——见 [[GRPO与DAPO算法族]]。

---

## 四、主结果（Table 3 / Fig.4）

公平对照：Instruct-TIR 评测也限制 **最大工具调用 = 1**。

### 4.1 1.5B 族（同 Qwen2.5-Math-1.5B-Base 线）

| Model | Tool | AIME24 | AIME25 | MATH500 | Olympiad | AMC23 | Avg |
|---|:---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-Math-1.5B-Instruct | ✗ | 10.0 | 10.0 | 66.0 | 31.0 | 62.5 | 35.9 |
| Qwen2.5-Math-1.5B-Instruct-TIR | ✓ | 13.3 | 13.3 | 73.8 | 41.3 | 55.0 | 41.3 |
| **ToRL-1.5B** | ✓ | **26.7** | **26.7** | **77.8** | **44.0** | **67.5** | **48.5** |

相对 Instruct-TIR：Avg **+7.2**；AIME24/25 各 **+13.3**。

### 4.2 7B 族

| Model | SFT/RL | Tool | AIME24 | AIME25 | MATH500 | Olympiad | AMC23 | Avg |
|---|---|:---:|---:|---:|---:|---:|---:|---:|
| Qwen2.5-Math-7B-Instruct | RL | ✗ | 10.0 | 16.7 | 74.8 | 32.4 | 65.0 | 39.8 |
| Qwen2.5-Math-7B-Instruct-TIR | RL | ✓ | 26.7 | 16.7 | 78.8 | 45.0 | 70.0 | 47.4 |
| SimpleRL-Zero | RL | ✗ | 33.3 | 6.7 | 77.2 | 37.6 | 62.5 | 43.5 |
| rStar-Math-7B | SFT | ✗ | 26.7 | — | 78.4 | 47.1 | 47.5 | — |
| Eurus-2-7B-PRIME | RL | ✗ | 26.7 | 13.3 | 79.2 | 42.1 | 57.4 | 43.1 |
| **ToRL-7B** | RL | ✓ | **43.3** | **30.0** | **82.2** | **49.9** | **75.0** | **62.1** |

- Abstract：相对「无工具 RL」约 **+14**（AIME24 口径）；相对「最佳既有 TIR」约 **+17**。
- Table 3 脚注式增量：相对 Instruct-TIR，AIME24 **+10.0**、Avg **+14.7**。
- 文述 ToRL-7B AIME 表现可与部分 **32B** RL 模型相比（§1，引 Hu et al. 2025 Open-Reasoner-Zero）。
- Fig.4：五基准训练曲线上 ToRL-7B 持续高于无工具 baseline 与 Instruct-TIR（细点 **待核实读图**）。

**跟读口诀：** 同样「能调代码」，**从 base 用 RL 自己探索** 显著强于「Instruct 再塞进 TIR 环境」；工具不是外挂评测模式，而是 **训练动力学的一部分**。

---

## 五、分析：工具行为如何被 RL「养」出来

### 5.1 Part I · 训练中的代码行为（§3.3.1 / Fig.5）

前约 100 step 量级观察（文述）：

| 指标 | 趋势 | 含义 |
|---|---|---|
| **Code Ratio** | ~40% → ~80% | 越来越多题选择写码 |
| **Pass Ratio** | 持续上升 | 可执行语法/语义变好 |
| **Correct vs Incorrect 的 Pass** | 正解轨迹 pass 更高 | 执行成败与终答相关 |
| **Effective Code Ratio** | 上升 | 计入：实际被解释器跑到的码；以及 **终答前** 的码（排除答完后只做校验的码） |

**Takeaway-I（文内）：** 训练步数增加 → 用码解题比例↑、可执行比例↑；同时模型学会 **识别并减少无效代码**（自我调节，无显式指令）。

### 5.2 Part II · $C$ 与可执行性惩罚（§3.3.2 / Table 4 / Fig.6）

| 设置 | 效果 |
|---|---|
| $C: 1\to 2$ | 平均准确率约 **+2%**；但单步时间：$C=0$ **118s** → $C=1$ **237s** → $C=2$ **288s**（8×A800） |
| Code Executability Reward（−0.5） | **不提升**表现（Fig.6c–d） |

**Takeaway-II：** 提高 $C$ 换性能、重创吞吐；可执行性 shaping 在此设置下无效甚至可能诱发「写太简单的码」。

### 5.3 Part III · 涌现认知行为（§3.3.3 / Table 5–6 / Fig.1 bottom）

文内定性案例（后期训练）：

1. **执行错误 → 自修代码**（Table 5）：Horner 法实现先触发 `TypeError: 'int' object is not subscriptable`，读错误后改返回值结构，再跑通。
2. **NL 推理错 → 用代码验算翻案**（Table 6）：自然语言先给出错误球号组合，代码验证输出不同结果后改 boxed 答案。
3. **交叉验证 / 反思**（Fig.1 bottom）：工具输出与解析推理不一致时，再反思并用工具复验（抛物线交点 $k+m$ 例：解析得 −9、代码得 16，最终以代码侧为准并 boxed 16）。

**Takeaway-III：** 奖励驱动下出现「吃解释器反馈、代码⇄自然语言交叉核对、自适应选计算或分析路径」——**不是**模仿人工 TIR 模板抄来的。

---

## 六、仓库复现要点（辅，README）

- 先按 [SandboxFusion](https://github.com/bytedance/SandboxFusion) 起在线沙箱；conda env 名需为 `sandbox-runtime`。
- 改 veRL rollout 文件中 `sandbox_url`（README 指 `vllm_rollout_spmd.py` 约 L109）。
- `bash scripts/torl_1.5b` 启动训练；依赖含 `math-verify`、`qwen-agent[code_interpreter]` 等。
- 致谢栈：DeepSeek R1 / Kimi-k1.5 报告、Qwen2.5-Math、veRL、vLLM、Qwen-Agent、Sandbox Fusion。

---

## 七、可迁移清单（写进自己实验前）

1. **工具是 env，不是后处理：** 在 rollout 中途插入 OBSERVATION，而不是只在评测时开 TIR。
2. **从 base 探索：** 若目标是发现新工具策略，先验 SFT 轨迹可能锁死模式。
3. **mask 工具观测：** 防背诵执行串；保留错误最后一行作反馈。
4. **隔离沙箱优先于极致低延迟：** 训练进程与解释器共址的 segfault 成本 > 几毫秒延迟。
5. **$C$ 是性能–吞吐旋钮：** 默认 1 可训；2 有增益但步时近翻倍量级。
6. **答案正确性优先：** 额外「跑不通就扣分」未必帮——至少 ToRL 消融如此。
7. **观测学什么：** 不只看终表，盯 code ratio / pass ratio / 「终答前有效码」是否在涨。

---

## 八、与邻篇交叉索引

| 邻篇 | 交叉一句 | 分界 |
|---|---|---|
| [[GRPO与DAPO算法族]] | ToRL 用 GRPO + 去 KL + temp=1 | 不写 DAPO 技巧清单 |
| [[代码智能体Harness史线]] | 「隔离执行」同属 harness 直觉 | 本篇是数学解释器，不是 SWE ACI |
| [[智能体工具与长程任务]] | 工具增强推理产品能力 | 不写 MCP / 旗舰工具环 |
| [[DeepSeekR1推理训练深读]] / SimpleRL | 无工具 RL 对照 | 不写 R1 阶段表 |
| [[GPTossModelCard]] gpt-oss | developer terminal tool **评测** | 不是 tool-use RL 算法 |

---

## 九、来源与版本钉死

- PDF：`https://arxiv.org/abs/2503.23383`（arXiv **2503.23383v1**，2025-03-30；本地 CreationDate 2025-04-01 CST）。
- 辅：`https://github.com/GAIR-NLP/ToRL`（README 表与 Table 3 一致；stargazers 等元数据随时间变，**不以星数为科学主张**）。
- 笔记状态：`date: 2026-09-22` · `status: draft`。

## 相关笔记

- [[多智能体辩论|Multi-Agent Debate]]
- [[形式化验证与LLM|Formal Verification for LLM]]
- [[GPTossModelCard|gpt-oss Model Card]]
- [[计算机使用智能体|Computer-Use Agents]]
- [[ToRL工具集成强化学习|Tool-Use RL / ToRL]]

