---
title: "长程规划记忆：CHIME（信用感知分层演化；≠ Mem0/HippoRAG）"
topic: CHIME长程规划记忆
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.02074 # 811K / 15p（主）
 - https://arxiv.org/abs/2506.15841 # 4.3M / 23p（补链）
 - https://arxiv.org/abs/2509.13313 # 1.3M / 29p（可选补链）
arxiv: ["2609.02074", "2506.15841", "2509.13313"]
related:
 - "智能体长程记忆"
 - "MemoryR1强化学习记忆维护"
 - "Mem0与Zep生产级记忆"
 - "HippoRAG2与CatRAG"
 - "智能体工具与长程任务"
 - "推理时树搜索ABMCTS"
code_promised: "https://github.com/ATH-MaaS/Marco-DeepResearch"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 长程规划记忆：CHIME（信用感知分层演化；≠ Mem0 / HippoRAG）

> **定位**：长程规划记忆主题轴——在已入库记忆轴（[[智能体长程记忆]] OS 分页、[[MemoryR1强化学习记忆维护]] RL 四操作、[[Mem0与Zep生产级记忆]] 生产记忆层、[[HippoRAG2与CatRAG]] 检索式非参记忆）之外，补「**长程 agentic planning × 自演化记忆的信用分配**」空位。主锚 **CHIME**（*Credit-Aware HIerarchical Memory Evolution*）：把终局成败拆成「计划质量 / 执行误差 / 环境噪声」，分设 **planning bank** 与 **execution bank**，先归因再写入（attribute-before-memorize）。
> **攻坚线**：**架构思想（主）**——分层银行 + Credit Attribution Gate + 信用感知演化；**评测字段（辅）**——四榜 train/eval Avg@3 与消融 / RQ 表，禁外推未测场景。
> **硬划界（开篇钉死）**：
> - **≠ [[Mem0与Zep生产级记忆]]**：禁止重写 Mem0 / Zep **生产对话记忆层** API、Graphiti 时序 episode、ADD/UPDATE tool-call 产品面。本卡对象是 **冻结策略上的自演化规划经验库**，不是会话事实抽取–更新服务。
> - **≠ [[HippoRAG2与CatRAG]]**：禁止重写 HippoRAG 2 / CatRAG **文档语料上的检索图算法**（OpenIE+PPR、查询条件边权）。本卡是 **agent 交互轨迹 → 规划/执行经验**，不是非参文档记忆索引。
> - **≠ [[智能体长程记忆]]**：禁止重写 MemGPT 主/档案上下文分页、A-Mem Zettelkasten 卡片链接演化全文。本卡不回答「窗口当物理内存怎么换页」，只回答「终局信号怎么归因到计划 vs 执行」。
> - **≠ [[MemoryR1强化学习记忆维护]]**：禁止重写 Memory-R1 在 `{ADD, UPDATE, DELETE, NOOP}` 上的 **outcome RL / 双 agent 蒸馏**。CHIME **冻结骨干参数**，只更新外置银行；信用门是 **结构化自省**，不是策略梯度。
> - **≠ [[智能体工具与长程任务]]**：禁止重写工具环 / MCP / 旗舰 agent 产品通史；四榜只作「长程工具任务床」接口。
> - **≠ [[推理时树搜索ABMCTS]]**：禁止重写 AB-MCTS **推理期答案树搜索**（宽 vs 深）；CHIME 文内把 test-time search（WebAnchor 等）标为对照范式，本卡不写树搜索内核。
> **补链不升主**：**MEM1**（常量内部状态 RL）与 **ReSum**（长程搜索上下文摘要 / ReSum-GRPO）仅作「长程记忆–上下文效率」对照索引，禁止展开成第二主轴。
> **禁止编造**：机制、公式编号、表数字一律锚定官方 PDF（2026-09-22 CST）。图内未列表格的精确曲线点标 **待核实读图**。文末代码「will be released」→ 记为 **承诺仓**，不以本地克隆为准。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主** | *CHIME: Credit-Aware Hierarchical Memory Evolution for Long-Horizon Agentic Planning* | arXiv:**2609.02074v1** \[cs.AI\]（**2 Sep 2026**）；作者 Ye, Lan, Jiang, Ye, Zhu, Jia, Wang*, Xu, Luo, Shi*（厦大 / 浙大 / 阿里） | `https://arxiv.org/abs/2609.02074` | **811K**（829,476 B） | **15** letter | |
| **补链** | *MEM1: Learning to Synergize Memory and Reasoning for Efficient Long-Horizon Agents* | arXiv:**2506.15841v2** \[cs.CL\]（**17 Jul 2025**）；Zhou*, Qu* et al.（SMART / NUS / MIT / Yonsei） | `https://arxiv.org/abs/2506.15841` | **4.3M**（4,492,356 B） | **23** letter | |
| **可选补链** | *ReSum: Unlocking Long-Horizon Search Intelligence via Context Summarization* | arXiv:**2509.13313v3** \[cs.CL\]（**26 Mar 2026**）；Wu*, Li* et al.（CUHK / 通义 / HKUST / Penn State） | `https://arxiv.org/abs/2509.13313` | **1.3M**（1,360,337 B） | **29** letter | |

| 材料 | 代码 / 承诺（文内） |
|---|---|
| CHIME | Abstract：**Code will be released at** https://github.com/ATH-MaaS/Marco-DeepResearch（截至笔记日作 **承诺仓**，本篇不跟 commit） |
| MEM1 | https://github.com/MIT-MI/MEM1（补链索引，不展开） |
| ReSum | （本卡不跟读实现；仅作摘要范式对照） |

**体积判定**：CHIME **811K**、MEM1 **4.3M**、ReSum **1.3M**，均 **<10MB** → 按本仓库「>10MB 正式外链」规矩 **三份均**（无需降级）。

**一句话抓手：**
- **CHIME**：自演化记忆写银行前先过 **Credit Attribution Gate**（`planning` / `execution` / `both` / `none`）→ 只更新被归因的 bank；检索 = 相似度 Top-N + 信用价值重排 Top-K。
- **MEM1（补）**：每步更新紧凑内部状态 `<IS>`，**常量记忆** + 端到端 RL，解决全历史拼接的上下文膨胀。
- **ReSum（补）**：周期性外部摘要工具压缩交互史；可选 ReSum-GRPO 做分段轨迹信用传播——**上下文摘要轴**，非规划/执行分层银行。

---

## 二、议题边界：只写「规划信用 × 分层自演化」，不写生产 API / 检索图 / 分页 OS / RL 四操作 / 工具通史 / 树搜索

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[Mem0与Zep生产级记忆]] Mem0/Zep** | 「外置可检索记忆」是共同隐喻；对象不同 | 生产 API、Graphiti 双时间轴、LOCOMO 产品对照全文 |
| **[[HippoRAG2与CatRAG]] HippoRAG2/CatRAG** | 「记忆要结构化」一句对照 | OpenIE+PPR、FCR/JSR、文档 hub 漂移 |
| **[[智能体长程记忆]] MemGPT/A-Mem** | 「记忆外置、跨任务复用」前序 | 分页压力告警 / Zettelkasten 建链演化全文 |
| **[[MemoryR1强化学习记忆维护]] Memory-R1** | 「记忆维护可被学」相邻；**训练面不同** | PPO/GRPO 上四操作策略 + Answer Agent 蒸馏 |
| **[[智能体工具与长程任务]]** | 长程工具任务为何难 | MCP / 并行工具环 / 旗舰 System Card agent 叙事 |
| **[[推理时树搜索ABMCTS]] AB-MCTS** | test-time search 是 CHIME §2 三种范式之一 | GEN 节点 / Thompson 宽深决策 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| attribute-before-memorize；`M = (M_plan, M_exec)`；Gate 四类标签 + 置信度 γ | 把 CHIME 写成「又一个 Mem0」或「又一个 HippoRAG」 |
| 价值分 $v_i \in [-1,1]$、重用计数 $n_i$、置信加权更新 | Memory-R1 式 outcome RL 训练曲线 |
| 四榜 τ²-Bench / VitaBench / BrowseComp-ZH / BFCL-v4 文内 Avg@3 | 未给的「跨域生产 SLA」外推 |
| 相对 WebAnchor / TodoEvolve / A-MapReduce 的范式对照 | AB-MCTS / TreeQuest 搜索内核；旗舰 Deep Research 产品通史 |
| MEM1 / ReSum **各一段对照槽** | 把常量记忆 RL 或摘要 GRPO 写成并列主文 |

跟读口诀：

`
[[智能体长程记忆]] = 记忆放哪（分页 OS / 卡片网）
[[MemoryR1强化学习记忆维护]] = 四操作怎么用 RL 学
[[Mem0与Zep生产级记忆]] = 生产记忆层 API
[[HippoRAG2与CatRAG]] = 文档检索图 → 非参记忆
[[CHIME长程规划记忆]] = 终局成败怎么归因到「计划 vs 执行」再写入（CHIME）
MEM1/ReSum = 上下文怎么压成常量/摘要（仅补链）
`

---

## 三、问题框定：自演化记忆的信用分配失败

CHIME §1 / Abstract 把长程 agentic planning 的改进路径压成三档，并钉死本卡只攻第三档的缺陷：

1. **Test-time search**（ToT / LATS / WebAnchor / MiroThinker-H1 等）：每任务探多候选计划，**推理贵**且不跨任务留经验。
2. **Planner 模型训练**（Plan-and-Act / TodoEvolve 等）：把规划能力内化进参数，**数据与持续更新贵**。
3. **Self-evolving memory**（ReasoningBank / UMEM / A-MapReduce 等）：冻结参数、外置银行从交互中蒸馏经验——**训练免费、可持续**，但是：

**信用分配失败（文内核心诊断）：** 现有自演化方法把 **终局 $s_t \in \{0,1\}$** 直接当记忆监督。同一成败可来自：好计划、执行挽救坏计划、坏计划、执行错、环境噪声。后果两重：（a）偏置经验写入后被反复检索 → 系统性规划错误累积；（b）执行/环境级细节被误当规划记忆 → 检索污染高层分解。

**CHIME 主张的解法（attribute-before-memorize）：** 先把结果归因到 plan / exec / both / none，**再**只更新对应银行；检索与价值更新都按阶段隔离。

---

## 四、方法：三件套（§3）

### 4.1 任务形式（§3.1）

流式任务 $\{x_t\}$，策略参数冻结，适应由外置银行 $M_t$ 承担。朴素自演化：

$$
M_{t+1} = U(M_t, x_t, \tau_t, s_t)
$$
评测时冻结银行，表现只反映评测前累积经验。CHIME 的一集流水线（式 4）：

$$
M_t \to M^{\mathrm{ret}}_{\mathrm{plan},t} \to p_t \to M^{\mathrm{ret}}_{\mathrm{exec},t} \to \tau_t \to s_t \to g_t \to M_{t+1}
$$
### 4.2 Hierarchical Memory Bank（§3.2）

$$
M_t = (M_{\mathrm{plan},t},\, M_{\mathrm{exec},t}),\quad \ell \in \{\mathrm{plan},\mathrm{exec}\}
$$
- **Planning bank**：子任务分解、依赖、约束纳入等**战略**经验。
- **Execution bank**：工具选择与调用等**操作**经验。
- 条目：$m_i = (c_i, e_i, v_i, n_i)$ —— 适用场景键 $c_i$、可复用经验 $e_i$、价值 $v_i\in[-1,1]$、重用次数 $n_i$。

**检索（两阶段）：** 对查询 $q_{\ell,t}$ 先相似度 Top-$N$ 得候选；再按校准价值 $\tilde{v}_i = v_i \cdot n_i/(n_i+\lambda)$ 做价值重排，取 Top-$K$（式 5；$\alpha$ 价值权重、$\beta$ 裁剪使相似度仍主导）。实现默认 $(N,K)=(20,3)$，$\lambda=3.0$，$\alpha=1.0$，$\beta=0.2$（§4 Implementation）。

### 4.3 Credit Attribution Gate（§3.2）

冻结策略的**结构化自省**：审任务、计划、轨迹、终局、已检索记忆 → 诊断

$$
g_t = \Big(a_t,\; \{(c^{\mathrm{new}}_{\ell,t}, e^{\mathrm{new}}_{\ell,t})\}_\ell,\; \gamma_t,\; M^{\mathrm{mis}}_t\Big)
$$
| 字段 | 语义（文内） |
|---|---|
| $a_t$ | `planning` / `execution` / `both` / `none`（成功时改为「归功于哪一阶段」） |
| 新经验对 | 为各阶段生成的场景键 + 可执行经验 |
| $\gamma_t\in[0,1]$ | 归因置信度 |
| $M^{\mathrm{mis}}_t$ | 被标为误导的已检索记忆 |

### 4.4 Credit-Aware Memory Evolution（§3.2）

**(1) 价值演化：** 归因标签决定更新阶段集合 $L(a_t)$（式 7：planning→{plan}，execution→{exec}，both→两者，none→空）。反馈 $\delta_{i,t}$（式 8）：误导 → $-\gamma_t$；成功且该阶段被归功 → $+\gamma_t$；否则 0。在线平均更新 $v_i,n_i$（式 9），再 clip 到 $[-1,1]$。低价值且复用够多则剪枝：$n_i\ge n_{\min}$ 且 $v_i<\theta_{\mathrm{prune}}$（默认 $n_{\min}=3$，$\theta_{\mathrm{prune}}=-0.1$）。

**(2) 内容演化（式 10）：** 仅对 $L(a_t)$ 内阶段：相似则 merge（$\mathrm{sim}>\theta_{\mathrm{merge}}=0.88$）、否则 insert（新条目 $v=0,n=0$）、不满足 $\gamma_t\ge\theta_{\mathrm{conf}}=0.5$ 或内容不可执行则 discard。

**与「vanilla 自演化」的图示对照（Figure 1）：** 共享银行直接写 vs 经 Credit Attribution Gate 分流到 Plan/Execution bank。

---

## 五、实验设置（§4）

| 维度 | 文内设定 |
|---|---|
| **基线（由远及近）** | No-Plan；**WebAnchor**（冻结策略 + 测试时候选计划搜索）；**TodoEvolve**（训 meta-planner、不累积经验）；**A-MapReduce**（最近邻：从轨迹蒸馏提示，但**直接用终局更新记忆**） |
| **榜** | τ²-Bench（多轮客服）；VitaBench（多轮生活服务、意图漂移、大工具空间）；BrowseComp-ZH（长程中文 InfoSeeking）；BFCL-v4（Live + long-horizon Agentic 函数调用组） |
| **骨干** | Qwen3.5-Flash（35B total / 3B active）；DeepSeek-V4-Flash（284B total / 13B active）；规划 / 执行 / Gate **同骨干** |
| **协议** | 每榜作顺序任务流，**7:3 train/eval**；多域则裁到最小域再按域切分；train 上累积更新，eval **冻结银行**只检索；三随机序 **Avg@3** |
| **评测侧模型** | 各榜官方协议下评测 LLM 用 Qwen3.6-Flash；检索用 Qwen3-Embedding-0.6B；温度 0.0（WebAnchor 计划采样 0.6） |

---

## 六、主结果与消融（§5；数字锚定 Table 1–2）

### 6.1 Table 1 摘要（Avg@3，%）

**Qwen3.5-Flash — Eval Average：** No-Plan 30.83 → WebAnchor 31.91 → TodoEvolve 29.53 → A-MapReduce 29.50 → **CHIME 34.87**（文称相对最强基线 **+2.96**；相对 A-MapReduce **+5.37**）。
**DeepSeek-V4-Flash — Eval Average：** No-Plan 32.98 → WebAnchor 33.13 → TodoEvolve 30.60 → A-MapReduce 35.33 → **CHIME 39.01**（相对最强基线 **+3.68**）。

Train 侧 CHIME 亦最高：Qwen **35.02**、DeepSeek **38.00**（相对最强基线 +3.38 / +0.90）。
分榜 Eval（摘）：Qwen 上 VitaBench CHIME **15.83** vs 最强对照约 11.94；DeepSeek 上 τ² Eval **36.28**、BrowseComp-ZH **31.50** 领先明显。BFCL-v4 上 Qwen CHIME **73.91** 最高；DeepSeek 上 A-MapReduce Eval **69.98** > CHIME **67.15**（文仍报平均领先，跟读时勿抹掉单榜例外）。

### 6.2 Table 2 消融（Qwen3.5-Flash，Eval Average 相对 CHIME 34.87）

| 变体 | Eval Avg | Δ |
|---|---|---|
| w/o Plan Memory | 31.61 | ↓3.3 |
| w/o Execution Memory | 30.06 | ↓4.8 |
| w/o All Memory | 31.74 | ↓3.1 |
| w/o Hierarchical Bank（并成共享库） | 31.27 | ↓3.6 |
| w/o Attribution Gate（退回终局直写） | 32.43 | ↓2.4 |
| w/o Credit Rerank | 32.83 | ↓2.0 |
| w/o Memory Evolution | 31.83 | ↓3.0 |

文内解读：增益来自**阶段专用经验 + 显式分库**，而非「多记一点」；Gate 决定反馈进哪一层，价值重排与演化决定复用/保留谁。

---

## 七、分析六问（§6；RQ1–RQ6）

| RQ | 文内结论（锚定表/图，不读未列表曲线点） |
|---|---|
| **RQ1 记忆质量** | GLM-5.2 外判 train 银行：CHIME Correctness/Non-Red./Generality/**All** = **81.20 / 93.60 / 90.13 / 81.04**；A-MapReduce All 仅 **36.08**；去 Gate 后 All **21.38**（Table 3） |
| **RQ2 演化效率** | τ²-Bench 累积检查点：CHIME 终局仅 **129** 条记忆 vs A-MapReduce **3,585**，准确率仍最高；无归因基线银行膨胀、准确率在 75% 检查点后下滑（Figure 3，柱高以文述为准） |
| **RQ3 价值效用** | 按 $v$ 分低/中/高：规划记忆准确率 **21.7%→50.8%**，执行 **23.7%→35.4%**（Figure 4）；规划高价值增益更大（文称组差 29.1 vs 11.7 pp） |
| **RQ4 Gate 可靠** | VitaBench / BFCL-v4：规划/执行 Stability 约 **87.8–97.9%**；失败被「仅用生成记忆重跑」Rescue 约 **56.3–67.6%**（Table 4） |
| **RQ5 更强信用模型** | Gate 换 Qwen3.7-Flash：τ² / Vita / BFCL Eval **+3.12 / +2.50 / +2.25**（Table 5；**单次跑**非 Avg@3） |
| **RQ6 跨骨干迁移** | 源银行冻结合入目标 eval：CHIME 迁移优于 A-MapReduce **2.25–4.68** pp，并接近目标自累积上界（Table 6） |

**附录 B 边界（跟读必记）：**（1）**Agent Capability**——记忆帮不到跟不住指导的骨干；Rescue 不是 100%。（2）**Memory Transferability**——同榜跨骨干可迁；**跨榜**因工具/动作/成功准则不同而弱。

---

## 八、补链对照（不升主）

### 8.1 MEM1（2506.15841）— 常量内部状态 RL

- **问题**：长程多轮把全部 thought/action/observation 拼进上下文 → 成本与 OOD 长度退化。
- **方法**：每步更新紧凑共享内部状态（文内 `<IS></IS>`），融合先验记忆与新观测并丢弃冗余；端到端 RL；另给「组合已有数据集成任意长任务序列」的环境构造。
- **与 CHIME 正交点**：MEM1 攻 **上下文长度/常量记忆**；CHIME 攻 **外置银行写入前的阶段信用**。二者都谈 long-horizon agents，但一个是 **参数内状态压缩**，一个是 **冻结参数 + 分库自演化**。本卡禁止把 MEM1 写成「CHIME 的训练版」。

### 8.2 ReSum（2509.13313）— 上下文摘要轴（可选）

- **问题**：Web agent 要广探索 vs 上下文窗硬顶；改架构（内部 memory token）破坏兼容且需重训。
- **方法**：周期性调用**外部摘要工具**压缩史 → 从压缩态续探（训练免费即可用）；**ReSum-GRPO** 用 advantage broadcasting 把终奖传到分段轨迹。文称相对 ReAct 训练免费 **+4.5%**，再 GRPO **+8.2%**（Abstract；细节不展开）。
- **与 CHIME 正交点**：ReSum 是 **搜索轨迹上下文管理**；CHIME 是 **计划/执行经验归因入库**。议程明确 **不升主**。

---

## 九、跟读清单与误区

**建议跟读顺序：** §1 信用失败诊断 → Figure 1–2 与 §3.2 三组件 → Table 1–2 → RQ1/RQ2/RQ4 → 附录 B 边界；MEM1/ReSum 只读 Abstract 对照槽。

**常见误区：**
1. 把 CHIME 当成 Mem0/Zep「又一层生产记忆 API」。
2. 把分层银行当成 HippoRAG「文档 KG」。
3. 把 Credit Gate 当成 Memory-R1「RL 学 CRUD」。
4. 把 WebAnchor 对照写成「本卡在做 AB-MCTS」。
5. 忽略 BFCL 上 DeepSeek 单榜 A-MapReduce 更高的例外，只报平均。
6. 把「Code will be released」当成已可复现的冻结 commit。

**开放问题（文内已暗示、本卡不编造答案）：** 跨榜迁移弱；Gate 依赖骨干自省能力（RQ5）；记忆指导仍受执行能力上限约束（附录 B）。

---

## 十、来源与体积验收（2026-09-22 CST）

| 文件 | `ls` 体积 | 页数 | 备注 |
|---|---|---|---|
| `https://arxiv.org/abs/2609.02074` | 829,476 B（**811K**） | 15 | **入库二进制** + 抽取 |
| `https://arxiv.org/abs/2506.15841` | 4,492,356 B（**4.3M**） | 23 | **入库二进制**（补链）+ 抽取 |
| `https://arxiv.org/abs/2509.13313` | 1,360,337 B（**1.3M**） | 29 | **入库二进制**（可选补链）+ 抽取 |

{chime,mem1,resum}.txt`。
笔记路径：`/workspace/AIResearch-drafts/Harness/记忆/CHIME长程规划记忆.md。
