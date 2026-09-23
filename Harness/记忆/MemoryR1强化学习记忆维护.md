---
title: "Memory-R1：用 RL 学会 ADD/UPDATE/DELETE/NOOP 维护记忆库"
topic: MemoryR1强化学习记忆维护
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2508.19828
arxiv: ["2508.19828"]
related: ["智能体长程记忆", "GRPO与DAPO算法族", "ToRL工具集成强化学习", "B6"]
archived: 2026-09-22
---

# Memory-R1：RL 记忆维护策略（相对 13 增量）

> **定位**：记忆维护主题轴 **弱档增量**——相对 **[[智能体长程记忆]]**（MemGPT 分页 OS / A-Mem 卡片盒网络）已入库的「外置记忆怎么分层、怎么长结构」，本篇只收 **「记什么 / 改什么 / 删什么 / 不动」可否被 outcome RL 学会**。
> **攻坚线**：**架构思想（主）**——双 agent（Memory Manager + Answer Agent）+ `{ADD, UPDATE, DELETE, NOOP}` 动作面；**评测字段（辅）**——LoCoMo / MSC / LongMemEval 上相对 Mem0、MemoryOS、A-Mem、Memory-SFT 的 F1 / BLEU-1 / Judge。
> **硬划界（禁止重写）**：
> - **禁止重写** [[智能体长程记忆]] 的 MemGPT 主存/外存/FIFO/分页告警全文，以及 A-Mem 笔记构造·建链·演化全文。本篇仅在对照句中点名二者为「启发式 / 结构记忆」前置，不复述公式与表。
> - **禁止重写** [[GRPO与DAPO算法族]] 的 GRPO→DAPO 技巧清单；本篇只用「PPO / GRPO 作组相对或近端策略优化槽位」。
> - **禁止重写** [[ToRL工具集成强化学习]] ToRL 工具进 env 全文、`B6` 向量 RAG 通史。
> **与 [[智能体长程记忆]] 的接口一句**：[[智能体长程记忆]] 回答「记忆放哪、如何换入换出 / 如何长网」；本篇回答「在 Mem0 式四操作面上，**用下游答对与否当奖励**，能否少标注地学出维护策略与检索后蒸馏」。
> **禁止编造**：机制、操作语义、表内数字一律锚定官方 PDF（2026-09-22 CST）；图内曲线点未列表格处 **不读点**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文** | Yan, Yang et al. (LMU / MCML / TUM / …), *Memory-R1: Enhancing Large Language Model Agents to Manage and Utilize Memories via Reinforcement Learning* | arXiv:**2508.19828v5** \[cs.CL\] **14 Jan 2026**；`https://arxiv.org/abs/2508.19828`（**20** 页 A4；3,472,962 bytes） | 双 agent + outcome RL（PPO/GRPO）；四操作维护记忆库 + 答前蒸馏 |
| **操作集出处（文内）** | Mem0（Chhikara et al., 2025）`{ADD, UPDATE, DELETE, NOOP}`；另引 MemGPT / AIOS CRUD 等为启发式对照 | 本篇不展开 Mem0 产品全文 | 动作面来源 |
| **训练框架（文内）** | VERL（Sheng et al., 2025）；H100×4（14B 用 8 GPU） | Appendix D | 复现入口级信息 |

**一句话抓手：** 把记忆维护从「ICL 启发式选 CRUD」改成 **可学习策略**——Memory Manager 对每条新事实输出 `(操作, 内容)`，用冻结 Answer Agent 的 **Exact Match** 当稀疏奖励；Answer Agent 再对 RAG 取回的约 **60** 条记忆做 **Memory Distillation** 后作答；仅 **152** 条训练 QA 即可在 LoCoMo 上相对强基线大幅提升，并零样本转到 MSC / LongMemEval。

---

## 二、议题边界：学「维护动作」，不是再写一套分页/卡片盒

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[智能体长程记忆]] MemGPT** | 「窗口外事实需显式管理」；文内作启发式基线引用 | 主上下文三段、warning/flush、pgvector 分页检索 |
| **[[智能体长程记忆]] A-Mem** | 同台基线（Table 1）；「结构可演化」直觉 | 式 (1)–(10)、Link/Evolution 消融表 |
| **[[GRPO与DAPO算法族]] GRPO/DAPO** | 组相对优势、无价值函数的稳定更新 | Clip-Higher / Dynamic Sampling / token-level loss |
| **[[ToRL工具集成强化学习]] ToRL** | 「outcome RL + 可验证终答」同族思路 | 代码解释器进 rollout、Sandbox Fusion |
| **B6 RAG** | 「取回后仍可能噪声淹没」 | 索引工程 / 重排器通史 |

### 2.2 问题立轴（跟读）

`
旧路：外置记忆银行 + 提示词教 LLM 选 ADD/UPDATE/DELETE/NOOP
 → 无「答对/答错」学习信号；易误判矛盾 → 错误 DELETE+ADD 碎片化事实
新路：同一动作面，用下游 QA Exact Match 作奖励（PPO 或 GRPO）
 → Manager 学巩固（UPDATE）而非撕裂；Answer Agent 学先蒸馏再答
`

**动机例（Figure 1 / §1）：** 用户先说「领养了 Buddy」，后说「又领养了 Scout」。Vanilla Manager 当成矛盾发 **DELETE+ADD**；RL Manager 发一次 **UPDATE** 合并成「Andrew 养了两只狗 Buddy 与 Scout」；Answer Agent 再从约 60 条检索结果压到相关条目后答「2 dogs」。

---

## 三、方法骨架：双 Agent + 四操作 + Outcome RL

### 3.1 流水线两阶段（§3 / Figure 2）

| 阶段 | 角色 | 输入 → 输出 |
|---|---|---|
| **Stage 1** | **Memory Manager** | 新抽取事实 $x$ + 当前库 $M_{\mathrm{old}}$ → 操作 $o\in\{\mathrm{ADD},\mathrm{UPDATE},\mathrm{DELETE},\mathrm{NOOP}\}$ 与内容 $m'$，写回记忆库 |
| **Stage 2** | **Answer Agent** | 问题 $q$ + RAG 检索集 $M_{\mathrm{ret}}$（文内默认约 **60** 条，跟 Mem0）→ **Memory Distillation**（筛相关条目）→ 答案 $y$ |

形式化（式 1 / 5）：

$$
(o,m')\sim\pi_\theta(\cdot\mid x,M_{\mathrm{old}}),\qquad
y\sim\pi_\theta(\cdot\mid q,M_{\mathrm{ret}}).
$$
两 agent **分开** RL 微调（Limitations：稀疏奖励下为求稳定；端到端 multi-agent RL 留作未来工作）。

### 3.2 四操作语义（Appendix C.1；提示词 Figure 9–10）

操作集采用 Mem0 设定；提示里 NOOP 亦写作 **NONE / No Change**。跟读规则（文内示例，非本仓库发明）：

| 操作 | 何时用（提示要点） | 实现注意（文内） |
|---|---|---|
| **ADD** | 新事实在库中不存在 | 生成新 `id`；`event: ADD` |
| **UPDATE** | 同主题但信息不同 / 更细；或可合并 | **保留同一 `id`**；写 `old_memory`；信息等价则勿更新 |
| **DELETE** | 新事实与旧记忆**矛盾** | 返回原 `id`，`event: DELETE`，勿造新 id |
| **NOOP / NONE** | 事实已在库中或无关 | `event: NONE`，库不变 |

**RL 相对启发式的差异不在动作表，而在学习信号：** 训练时 **不**人工标注「该 ADD 还是 UPDATE」；只看操作应用后，冻结 Answer Agent 能否答对关联 QA（§3.1）。

### 3.3 Memory Manager 的 RL（§3.1）

- **状态：** $(x, M_{\mathrm{old}})$；**动作：** $(o,m')$。
- **奖励：** $R_{\mathrm{answer}}=\mathrm{EM}(y_{\mathrm{pred}},y_{\mathrm{gold}})$（式 4）——Exact Match，无需逐步操作标签。
- **PPO：** 标准 clipped surrogate（式 2），重要性比 $\rho_\theta=\pi_\theta/\pi_{\mathrm{old}}$。
- **GRPO：** 每状态采样 $G$ 个候选，组内标准化优势 $A_i=(r_i-\mathrm{mean})/\mathrm{std}$，加 KL 到 $\pi_{\mathrm{ref}}$（式 3）。

### 3.4 Answer Agent 的 RL + Memory Distillation（§3.2）

- 先相似度 RAG 取回约 60 条；策略需 **先选出有用记忆再答**（提示要求先输出选中 memories，再 `**Answer:**`，且答案宜短，Appendix C.2）。
- 奖励同样为 **EM**；PPO/GRPO 对称套用。
- 文内消融称：去掉蒸馏 → F1/B1/J 下降（§4.4 数字见下）。

### 3.5 训练数据构造（Appendix B.2 / Algorithm 1–2）

- **LoCoMo 划分（§4.1，跟 Mem0）：** 去掉 adversarial 子集；**train/val/test = 152 / 81 / 1307**（约 1:1:8）。
- **Manager：** 每 turn 配「时序记忆快照 + 当前 turn + 相关 QA」；文内叙述用 GPT-4o-mini 建快照（B.2 写 preceding **24** turns；Algorithm 1 写 previous **50** turns——**原文自相出入，录两处，不擅自统一**）。**无**操作黄金标签。
- **Answer Agent：** 用已训 Manager 维护的库，对每题 RAG top 记忆（Algorithm 2：每说话人 top **30** → 合计 **60**）+ gold answer 成对。
- **Memory-SFT 对照：** 同架构同数据，但用 **GPT-5 轨迹行为克隆** 替代 RL（§4.1）。

### 3.6 实现要点（Appendix D，只记可跟读项）

- 底座：**LLaMA-3.1-8B-Instruct**；**Qwen-2.5-3B/7B/14B-Instruct**。
- 优化：VERL；PPO actor/critic lr $1\times10^{-6}$ / $1\times10^{-5}$；batch 128，micro-batch 2/GPU；prompt/response 上限 4096 / 2048。
- 解码：训练探索 $\tau=1.0$；验证/测试 greedy $\tau=0$。
- 提示改编自 Mem0 / MemGPT 公开提示（Appendix C）。

---

## 四、评测锚点（只记表内 / 正文可核对数字）

### 4.1 设置（§4.1）

| 项 | 文内 |
|---|---|
| **主榜** | LoCoMo：多 session 对话 QA（§4.1 叙述约 **600** turns / **26k** tokens；Appendix B.1 另述均值约 **300** turns / **9k** tokens、最多约 **35** sessions——**两处口径不同，引用时标明章节**） |
| **题型** | Single-Hop / Multi-Hop / Open-Domain / Temporal（主表不含 adversarial） |
| **泛化** | 仅在 LoCoMo 上训 → **零样本** MSC、LongMemEval |
| **指标** | token F1、BLEU-1（B1）、LLM-as-a-Judge（J；CORRECT/WRONG，Appendix C.3） |
| **基线（同骨干重实现）** | LoCoMo(RAG)、**A-Mem**、**Mem0**、**MemoryOS**、**Memory-SFT**；温度 0、max tokens 2048 |

### 4.2 LoCoMo 主结果（Table 1，Overall）

| Backbone | Method | F1↑ | B1↑ | J↑ |
|---|---|---:|---:|---:|
| LLaMA-3.1-8B-Instruct | LoCoMo (RAG) | 11.41 | 8.71 | 13.62 |
| | A-Mem | 29.20 | 24.40 | 44.76 |
| | Mem0 | 30.41 | 22.22 | 45.68 |
| | MemoryOS | 35.04 | 27.99 | 48.20 |
| | Memory-SFT | 42.81 | 32.98 | 58.76 |
| | Memory-R1-PPO | 41.05 | 32.91 | 57.54 |
| | **Memory-R1-GRPO** | **45.02** | **37.51** | **62.74** |
| Qwen-2.5-7B-Instruct | MemoryOS | 34.64 | 29.36 | 51.26 |
| | Memory-SFT | 39.51 | 30.84 | 61.13 |
| | Memory-R1-PPO | 41.72 | 33.70 | 59.53 |
| | **Memory-R1-GRPO** | **43.14** | **36.44** | **61.51** |

**正文相对增益叙述（相对最强非 RL 基线 MemoryOS，LLaMA）：** GRPO 相对提升约 **F1 +28.5% / B1 +34.0% / J +30.2%**；PPO 约 **+17.2% / +17.6% / +19.4%**（§4.2）。Qwen 上 GRPO 相对 MemoryOS 约 **+24.5% / +24.1% / +20.0%**。作者强调：**RL 仍可超过 GPT-5 轨迹的 Memory-SFT**。

题型分解（同表）：LLaMA + GRPO 在 Multi-Hop F1 **35.65**、Temporal F1 **49.86** 等均为该骨干行内最高或并列前列——完整格以 PDF Table 1 为准。

### 4.3 缩放与泛化（§4.3；图为主）

- **Figure 3：** Qwen-2.5 **3B / 7B / 14B** 上 PPO/GRPO 均持续高于 base（**逐点数字以图为准，不臆造**）。Appendix Table 3 给出扩展数值表可核对。
- **Figure 4：** 仅 LoCoMo 训练的管线在 **MSC、LongMemEval** 上仍一致增益。
- **LongMemEval Overall（Table 5）：** 例 LLaMA 上 GRPO **45.20 / 39.30 / 55.40**（F1/B1/J）高于 Memory-SFT **43.89 / 36.72 / 54.80** 与 A-Mem **38.36 / 33.30 / 54.20**；Qwen 上 GRPO **46.70 / 41.10 / 57.80**。分任务（SSU/SSP/OD/MS/KU/TR）见 Table 4。

### 4.4 消融与奖励设计（§4.4；LLaMA-3.1-8B 叙述）

| 消融 | 文内数字（F1 / B1 / J） |
|---|---|
| 去掉 RL Manager（相对满分管线） | PPO：41.0/32.9/57.5 → **34.5/28.1/49.0**；GRPO → **37.5/30.6/52.9** |
| 无 RL Answer Agent → 满分管线 | PPO：32.5/24.6/59.4 → **41.0/32.9/57.5**；GRPO：33.0/24.9/59.9 → **45.0/37.5/62.7** |
| 无 Memory Distillation → 有蒸馏 | PPO：39.3/30.9/57.4 → **41.0/32.9/57.5**；GRPO：41.0/34.4/60.1 → **45.0/37.5/62.7** |
| 更强 Manager（GPT-4o-mini vs LLaMA-8B）放大 Answer Agent 增益 | ΔF1 **+19.72 vs +10.10**；ΔB1 **+18.19 vs +10.81**；ΔJ **+15.76 vs +5.05**（Figure 6） |

**奖励选择（Table 2，PPO Answer Agent）：**

| Reward | F1 | B1 | J |
|---|---:|---:|---:|
| J-based | 33.69 | 23.36 | **63.58** |
| **EM-based（采用）** | **41.05** | **32.91** | 57.54 |

文内解释：J 奖励诱使冗长答案，抬高 Judge、压低字符串重叠；为与基线公平对比采用 **EM**。

**训练动态（Figure 7）：** GRPO 早期收敛更快，后期与 PPO 终奖相近（曲线点不读）。

### 4.5 延迟叙事（Appendix G / Figure 8）

- 相对 Base + Reranker：学到的蒸馏在更高准确率下仍有更好 latency 权衡（图；**不读精确 ms 点**）。
- Manager：LLaMA 上 p50 约 **1.98–2.17 s**，p95 约 **3.4–3.6 s**；Qwen-7B p50 **\<1.4 s**——文称 RL **未明显加重**操作选择成本。
- Memory Search：两骨干 p50 **\<0.35 s**，p95 **\<0.65 s**。

---

## 五、相对 [[智能体长程记忆]] 的增量对照（一句表，禁止展开成第二遍 [[智能体长程记忆]]）

| 维度 | [[智能体长程记忆]]（已入库） | 本篇 Memory-R1 |
|---|---|---|
| **核心问题** | 分层分页 / 笔记图如何组织外置记忆 | 四操作策略与读后蒸馏 **如何被奖励学会** |
| **决策信号** | 提示 + 函数调用 / LLM 建链演化（无 outcome RL） | 下游 **EM** → PPO/GRPO |
| **同台关系** | A-Mem、MemGPT 为结构/OS 主文 | Table 1 把 **A-Mem、Mem0、MemoryOS** 当基线；MemGPT 在 related work 中作启发式代表 |
| **数据效率叙事** | （各文自有） | **152** QA 即宣称大幅增益 |

**跟读卡片：**

> [[智能体长程记忆]]：**记忆子系统的形态**（RAM/磁盘 vs 卡片盒）。
> [[MemoryR1强化学习记忆维护]]：**同一 CRUD 面上的策略学习**——少标签、outcome-driven，让 Manager 倾向 **UPDATE 巩固** 而非错误 **DELETE+ADD**，并让 Answer Agent **先滤噪再答**。

---

## 六、局限与开放问题（文内 + 笔记边界）

**作者 Limitations：**

1. 评测偏 **对话中心**；多模态记忆未覆盖。
2. Manager 与 Answer Agent **分训** 换稳定，端到端 multi-agent RL 未做。

**笔记侧待核实（不填空）：**

- Appendix B.2「24 turns」vs Algorithm 1「50 turns」快照长度不一致。
- LoCoMo 规模在 §4.1 与 Appendix B.1 口径不一致；引用请带章节。
- Figure 3/4/7/8 精确点值未列表 → 需要时重读图或作者发布数据，**禁止目测填数**。
- 与生产 Mem0 / MemoryOS 的实现是否逐 API 对齐，原文称「re-implemented」——深度复现应核附录与开源（若后续发布）。

---

## 七、本地路径速查

| 类型 | 路径 |
|---|---|
| 笔记 | Harness/记忆/MemoryR1强化学习记忆维护.md |
| PDF | `https://arxiv.org/abs/2508.19828` |
| 交叉 | Harness/记忆/智能体长程记忆.md（禁止当本稿重写底稿） |

## 相关笔记

- [[法律专科模型|Legal Specialty Models]]
- [[MixtureOfAgents与TUMIX|MoA / TUMIX]]
- [[图谱检索GraphRAG|Graph RAG]]
- [[MemoryR1强化学习记忆维护|Memory-R1]]
- [[安全论证SafetyCases|Safety Cases]]

