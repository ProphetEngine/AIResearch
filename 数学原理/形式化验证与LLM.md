---
title: "Formal verification for LLM：VeriCoT + AlphaProof"
topic: 形式化验证与LLM
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2511.04662
 - https://doi.org/10.1038/s41586-025-09833-y
arxiv: ["2511.04662"]
doi: ["10.1038/s41586-025-09833-y"]
related: ["过程奖励模型PRM谱系", "GRPO与DAPO算法族", "DeepSeekR1推理训练深读", "推理时扩展TestTimeScaling"]
archived: 2026-09-22
---

# Formal verification for LLM：VeriCoT + AlphaProof

> **定位**：[[形式化验证与LLM]] P0——相对 `[[过程奖励模型PRM谱系]]`（PRM 过程奖励）与 `[[GRPO与DAPO算法族]]` / R1（可验证奖励 RL），本篇只补 **符号 / 证明器接地的正确性保证** 枢纽：
> - **VeriCoT**：非数学域 NL CoT → FOL（SMT-LIB）+ Z3 逐步蕴涵/矛盾检查；
> - **AlphaProof**：Lean 交互证明环境上的 AlphaZero 式 RL + 测试时 RL（TTRL）。
> **攻坚线**：**架构思想（主）**——谁在仿什么、校验器接在哪；**数学原理（辅）**——FOL 蕴涵判定与 Lean 证明搜索里的状态/回报。
> **硬划界（禁止重写）**：
> - **禁止重写** `[[过程奖励模型PRM谱系]]` 的 PRM 标注流水线 / ORM vs PRM 谱系 / Math-Shepherd 自动逐步标签（本篇不写「逐步奖励模型怎么训」）。
> - **禁止重写** `[[GRPO与DAPO算法族]]` 的 GRPO→DAPO 技巧清单，以及 [[DeepSeekR1推理训练深读]] 的 **R1 阶段表** / 规则奖励通史。
> - **禁止重写** `[[推理时扩展TestTimeScaling]]` TTS 通史；AlphaProof 的 tree-search / TTRL 只作 **形式证明侧** 的 inference scaling，不串 o1/R1 产品叙事。
> **禁止编造**：公式、表数字、算力预算一律锚定官方 PDF（2026-09-22 CST）。VeriCoT 备链作者页 PDF 未另采；Nature 文以 `https://doi.org/10.1038/s41586-025-09833-y` 为准。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文 A** | Feng, Weir, Bostrom et al., *VeriCoT: Neuro-symbolic Chain-of-Thought Validation via Logical Consistency Checks* | arXiv:**2511.04662v1** \[cs.AI\] **6 Nov 2025**；`https://arxiv.org/abs/2511.04662`（**37** 页 letter；1,423,650 bytes；UPenn + AWS） | NL CoT → FOL/SMT-LIB；Z3 校验；自反思 / SFT / DPO |
| **主文 B** | Hubert, Mehta, Sartran et al. (Google DeepMind), *Olympiad-level formal mathematical reasoning with reinforcement learning* | Nature **Vol 651** \| **19 March 2026** pp.607–…；doi:**10.1038/s41586-025-09833-y**；Received 3 Jun 2025 / Accepted 30 Oct 2025 / Published online **12 Nov 2025**；`https://doi.org/10.1038/s41586-025-09833-y`（**25** 页；CreationDate **2026-03-17** CST） | Lean 环境 RL；auto-formalization 课程；TTRL；IMO 2024 |

**备链（议程）：** VeriCoT 作者页 https://benjaminkiesl.github.io/publications/vericot_feng_et_al.pdf（本笔记主采 arXiv PDF，未另核镜像字节差）。

**一句话抓手：** 两文都用 **外部形式系统** 给 LLM 推理「落地」——VeriCoT 把开放域 CoT 钉到 **Z3 可判定的 FOL 片段** 并显式列出 NL 前提；AlphaProof 把证明过程钉到 **Lean 内核可验证的 tactic 轨迹**，用 RL 在百万级形式题上自学。相对 PRM（学一个打分器）与 outcome RLVR（终答 checker），这里的信号来自 **证明器/求解器**，不是另一套神经判别。

---

## 二、议题边界：符号接地，不是又一部过程奖励 / RL 算法通史

### 2.1 相对 [[过程奖励模型PRM谱系]] / [[GRPO与DAPO算法族]] / R1 只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[过程奖励模型PRM谱系]] PRM** | 「过程对不对」是信任问题；验证器可喂 TTS / RL | 人类逐步标注、Math-Shepherd 续写金标、PRM800K、逐步 CE / 聚合规则 |
| **[[GRPO与DAPO算法族]] GRPO/DAPO** | 「有可验证奖励就能做组相对 RL」的抽象槽位 | Clip-Higher、动态采样、token-level loss、Dr.GRPO 去偏公式 |
| **[[DeepSeekR1推理训练深读]]** | R1 族用规则/可验证奖励做长 CoT（点名即可） | 冷启动 → 拒绝采样 → 二次 RL **阶段表** |
| **[[推理时扩展TestTimeScaling]]** | 测试时加算力能抬解题率（AlphaProof Fig.4） | o1/R1 产品「势」叙事与非正式数学竞赛通史 |

### 2.2 两条形式接地轴（跟读口诀）

`
VeriCoT NL CoT 逐步 → SMT-LIB FOL → Z3（蕴涵 / 矛盾 / 不可译）
 前提来自：上下文 / 常识 / 已证步骤；可选 LLM-as-Judge 审前提
 域：ProofWriter / LegalBench-SARA / BioASQ（非竞赛数学）

AlphaProof 非形式题 →（auto-formalize）→ Lean 语句 → tactic RL + 树搜索
 奖励：每步 tactic −1；多子目标取 min 回报（最长支）
 域：miniF2F / formal-imo / Putnam；IMO 2024（+ AlphaGeometry 2）
`

| 维度 | **VeriCoT** | **AlphaProof** |
|---|---|---|
| 形式宿主 | SMT-LIB 片段 + **Z3** | **Lean 4** + Mathlib（内核最终校验） |
| LLM 角色 | 自动形式化 + 前提生成 +（可选）judge；执行器 Claude-3.5-Sonnet-V2 | 证明网络（3B enc–dec）产 tactic/value；auto-formalizer 为 Gemini 系微调 |
| 「正确」保证什么 | **形式化后的** $F_i$ 由前提集蕴涵；**不**保证 NL 原文与前提本身为真（§5） | Lean 内核接受的证明项（+ 仅用三个内建公理的终检）；几何另走 AG2 |
| 训练用法 | 校验信号 → 自反思 / SFT 已校验 CoT / DPO 成对奖励 | 主 RL（~80k TPU-day）+ 推理时搜索 / TTRL |
| 与 PRM 的差 | 逐步标签来自 **求解器判定**，不是再训一个过程 RM | 环境奖励来自 **证明成败/长度**，不是答案字符串匹配 |

---

## 三、站 1：VeriCoT — NL CoT 的神经符号校验

### 3.1 问题与主张（Abstract / §1）

- CoT 终答可对、中间步可错（Fig.1 法定年龄例：「at most 15」vs 「at most 18」）。
- 缺口：同时满足 (1) 覆盖 **整条 CoT 逐步**；(2) **形式化每一步对上下文的接地**；(3) 在 **非 code/math** 域用校验信号改进模型。
- 主张：VeriCoT 是据作者所知 **首个** 面向非数学/代码域 CoT 的神经符号校验器。

### 3.2 算法骨架（Alg.1 / §2）

给定上下文（问题 + 可选对话史 + 源文档）与 CoT 步骤 $C_1,\ldots,C_n$：

1. 初始化 $F_0=\emptyset$，$P_0=\emptyset$，`errors`=$\emptyset$。
2. 对每步 $C_i$：
 - **(a) Autoformalization（§2.2）** → FOL 公式 $F_i$；失败 → `untranslatable`。
 - **(b) Consistency**：若 $F_{i-1}\models \neg F_i$ → `contradiction`。
 - **(c) Entailment**：若 $F_{i-1}\models F_i$ → 接受并并入知识。
 - **(d) Premise generation（§2.3）**：否则从上下文/常识生成 $P_i$，检查 $F_{i-1}\not\models\neg P_i$；可选 **LLM-as-Judge（§2.4）** 审前提是否可归因；若 $F_{i-1}\cup\{P_i\}\not\models F_i$ → `ungrounded`。
3. 返回 $P_n,F_n,$ errors。

**有效 CoT 的充要口径（文内）：** 能从 NL 上下文推出一组自洽 FOL 前提 $\mathcal{P}$，使每步形式化 $F_i$ 满足 $\mathcal{P}\models F_i$。

**三类错误（反馈给自反思/蒸馏）：**

| 标签 | 含义 |
|---|---|
| **Ungrounded** | 找不到充分且不矛盾的加强前提使 $F_{i-1}\cup\{P_i\}\models F_i$ |
| **Contradiction** | $F_{i-1}\models\neg F_i$ |
| **Untranslatable** | 超出支持的 FOL 片段，或多次尝试后仍有语法错误 |

**求解器：** 公式编码为 **SMT-LIB**（线性算术、未解释函数、量词等片段）；一致性/蕴涵用 **Z3**。

### 3.3 自动形式化与前提（§2.2–2.4）

**两阶段 autoformalization（均用 LLM）：**

1. 在已有词汇表约束下生成「SMT-LIB + 对齐元数据」中间表示；
2. 不足则 `declare-fun` / `declare-sort` 扩展词汇，再重试；**最多 3 次**，否则标不可译 / 丢弃该前提。

**前提生成：** 多候选 NL 前提 → 各自形式化 → 保留与 $F_{i-1}$ 可满足者 → 合取为 $P_i$；新声明语义未写入前提时再生一轮。

**LLM-as-Judge：** 上下文前提 → 是否可归因到源文本；常识前提 → 在给定上下文/目标步下是否可接受（另可评「是否必要」）。

**跟读例（§2.1，SARA 福利资格）：**
$F_1$ 出生年+同住 → 从问题抽 $P_1$；$F_2:\mathrm{age}\le 18$ ← 常识 $P_2:\forall x,y.\,\mathrm{age}(x,y)\le y-\mathrm{birthYear}(x)$；$F_3$ 资格规则 ← 文档更强前提 $P_3$（<21）；$F_4:\mathrm{Qualifies}(\mathrm{charlie})$ 由已有知识推出。若写「≤15」则与 $P_2$ 矛盾。

### 3.4 实验设置与主表（§3）

| 项 | 文内设定 |
|---|---|
| VeriCoT 执行 LLM | **Claude-3.5-Sonnet-V2**（API） |
| 微调学生 | **Qwen2.5-7B-Instruct**；监督蒸馏自 Claude |
| 数据集（Table 5） | ProofWriter train **5000** / test **400**；BioASQ **5049** / **340**（Task 12b Phase B）；LegalBench-SARA test **367**（Entailment 272 + Numeric 95） |
| 基线 | Explanation-Refiner（ER）；Direct SMT Baseline（DSB）；VeriCoT-NoPrem |

**指标：** Pass Rate（可验证比例）；Precision（已验证中终答正确率）；**VCAR**（既验证又正确）；Task Acc（任务正确率）。

**Table 1（校验，无自反思；%）摘录：**

| 数据集 | 方法 | Pass | Prec | VCAR | Task Acc |
|---|---|---:|---:|---:|---:|
| ProofWriter | ER | 14.8 | 83.3 | 12.3 | 75.8 |
| | DSB | 10.0 | 96.1 | 9.5 | 74.8 |
| | VeriCoT-NoPrem | 3.3 | 100 | 3.3 | 75.8 |
| | **VeriCoT** | **45.2** | **94.1** | **42.5** | 75.8 |
| BioASQ | ER | 1.5 | 80.0 | 1.2 | 81.4 |
| | DSB | 5.9 | 72.2 | 4.2 | 75.7 |
| | **VeriCoT** | **25.3** | **84.3** | **21.3** | 81.4 |
| LegalBench-SARA | ER | 6.8 | 92.0 | 6.3 | 80.0 |
| | DSB | 4.8 | 94.1 | 4.5 | 77.7 |
| | **VeriCoT** | **15.2** | **87.0** | **13.2** | 80.0 |

要点（§3.3）：Pass / VCAR 全面高于基线；**Precision consistently > Task Acc** → 通过校验的 CoT 比「裸终答」更可靠的正确性信号。失败以 **Ungrounded** 为主（过度假设）；自反思后 Valid↑、Ungrounded/Contradiction↓，Untranslatable 比例几乎不变（Fig.2）。

**Table 2（LLMaj 前提质量，%）摘录：** 上下文可归因约 **87–96**；可接受常识约 **84–93**；「必要」常识约 **77–81**。

### 3.5 校验信号的三用途（§3.4）— 点到为止，不抄 DPO 通史

1. **透明性：** 显式 NL 前提 + FOL，便于人审。
2. **推理时自反思：** 失败则把逐步形式化、错误类型、求解器结果（及可选 LLMaj）喂回模型改写 CoT。
 - 文称：Pass 平均 **+12.3 abs / +46.4% rel**；VCAR 平均 **+9.5 abs / +41.1% rel**（Abstract 亦写 ~46% / ~41% relative）。
 - Table 3：VeriCoT-Base / -w LLMaj 在三数据集上 Pass/VCAR 绝对提升最强；w LLMaj 仅略优于 Base（求解器错误信号已够信息）。
3. **SFT + DPO（Table 4，Qwen2.5-7B）：**
 - 仅用 **通过校验（+LLMaj）** 的蒸馏 CoT 做 SFT，相对随机蒸馏，终答准确率平均约 **+3%**（文述 ii vs iii）。
 - 在 SFT 上再 DPO（chosen=再采样仍通过 / rejected=失败）：Pass **+4.3 abs（+18.4% rel）**，VCAR **+3.4 abs（+17.7% rel）**——即 Abstract 的「逻辑一致 CoT +18% relative」。

**与 Lean 系「Theorem Prover-as-a-Judge」（Leang et al. 2025）的划界（§4）：** 对方把陈述钉在 **已有符号库（如 mathlib）** → 偏数学；VeriCoT 把陈述钉在 **从 NL 推断的前提** → 开放域。

### 3.6 局限（§5，必读）

自动形式化与前提推断都依赖 LLM → 可能误译或引入不当前提；支持的 SMT-LIB 子集也可能表达不了原文。因此 VeriCoT **证明的是「形式化后的 CoT 相对推断前提的逻辑后承」**，**不能**保证 NL CoT 或前提本身为真。

---

## 四、站 2：AlphaProof — Lean 上的形式证明 RL

### 4.1 问题与主张（开篇）

- 非形式 LLM 数学强，但缺少能 **保证推理正确** 的形式校验；终答核对 / 不可信逐步比对不够。
- Lean 等把数学变成可交互、可验证环境；RL（AlphaZero 谱系）可在可验证环境里自学。
- **AlphaProof**：AlphaZero 启发的 agent，在 **数百万 auto-formalized** 题上 RL；难题用 **TTRL**（推理时对目标题生成大量变体再 RL）。
- **IMO 2024：** 作核心推理引擎，解出 5 道非几何题中的 **3** 道（含最难 P6）；与 **AlphaGeometry 2** 合解 6 题中的 4 题，得分 **28/42**，银牌区间（官方金牌线差 1 分）；作者称据其所知为 AI **首次** 达任何奖牌级。

### 4.2 Lean RL 环境（主文 + Methods）

| RL 要素 | 定义 |
|---|---|
| **状态 $s_t$** | Lean 证明状态（假设 + 剩余目标）；观测为 tactic state 的 pretty-print 字符串 |
| **动作 $a_t$** | 一条 Lean **tactic**（文本） |
| **转移** | 环境执行 tactic；须无错、不用 `sorry`、类型正确（临时用 private `internalSorry` 关未处理目标以检查） |
| **回合结束** | 找到内核可接受的完整证明，或算力耗尽 |
| **奖励** | 每应用一步 tactic：$r_t=-1$（偏好短证明） |
| **回报 $G_t$** | 至终止的奖励和；**多独立子目标（AND）时取各子目标回报的 min**（= 最长/最难支），而非求和——激励子目标难度均衡；价值对应 $-T_{\mathrm{steps}}$（最长支 tactic 数） |
| **证伪** | 自定义 tactic + 私有公理把目标变为其否定，仍使最终证明可被内核检查 |

**终检：** 独立跑 Lean CLI 对完整 `.lean` 文件；并检查仅依赖 Lean 三公理（命题外延、全局选择、商类型可靠性）。

### 4.3 证明网络 + 树搜索（Fig.1）

- **Proof network：** **30 亿** 参数 encoder–decoder Transformer；encoder 读 tactic state；decoder = **policy**（并行采样 $K$ 条 tactic）；value head 在 encoder 上，**类别分布**估期望回报。
- **树搜索：** AlphaZero / Sampled MuZero 变体；节点=状态，边=tactic；**AND–OR** 结构处理多子目标（AND 上回传取 min $V$）；开放 tactic 空间用 **采样动作 + progressive sampling**。
- 执行闭环：网络提议 → Lean 执行出子状态 → value 引导加深有希望的分支。

### 4.4 训练三阶段 + 课程规模（Fig.2a）

| 阶段 | 内容（文内数量） |
|---|---|
| Pretrain | ~**3000 亿** token 代码+数学文本，next-token |
| SFT | ~**30 万** Mathlib 人工 state–tactic 对 |
| **Main RL** | Gemini 系 auto-formalizer：~**100 万** 非形式题 → ~**8000 万** 形式 Lean 题；matchmaker 随机指派 **证明或证伪**；~**80,000 TPU-day**（文例：4000 TPU × 20 天量级） |

要点：auto-formalization **不必忠实于原文**——只要得到合法形式语句，即可作 RL 实例。经验来自成功证明 **与** 证伪。训练中训练集 proved/disproved 比例上升；held-out（miniF2F-valid / formal-imo / PutnamBench-test）solve rate 随 RL 上升，且同样 solve rate 所需仿真次数下降（Fig.3）。

### 4.5 推理时扩展：搜索 vs TTRL（Fig.2b / Fig.4）

| 机制 | 做什么 | 算力刻度（文） |
|---|---|---|
| **加大树搜索** | 同一主 RL agent，加仿真预算 | 例：2 TPU-min → 12 TPU-hour：formal-imo / PutnamBench-test **+>10 abs pp** |
| **TTRL** | 围绕目标题生成形式变体（简化/推广等；Fig 示 ~**40 万** 变体量级）再跑聚焦 AlphaZero 式 RL | 例：相对 12 TPU-hour 搜索，再 **+~15 abs pp**（formal-imo / Putnam）；横轴为 **数百 TPU-day / 题** |

### 4.6 基准与 Table 1（摘录）

评测均为 **人工 Lean 形式化**：校正版 **miniF2F**；**formal-imo**（历史 IMO **非几何**，因 Olympiad 几何 Mathlib 限制）；**PutnamBench**（偶数年 1990+ 为 PutnamBench-test）。全程数据隔离（Methods）。

| 设定（每题平均推理算力） | miniF2F-test | formal-imo | PutnamBench-test |
|---|---:|---:|---:|
| AlphaProof · 2 TPU minutes | 96.3% | 33.2% | 27.9% |
| AlphaProof · 12 TPU hours | 97.7% | 43.7% | 39.4% |
| + TTRL · 50 TPU days | 97.5% | 53.9% | 45.5% |
| + TTRL · 500 TPU days | **99.6%** | **58.3%** | **56.1%** |

对照（表内「此前 SOTA」摘录）：DeepSeek-Prover-V2 miniF2F-test **88.9%** / Putnam **5.3%**；Kimina-Prover Preview **80.7%** / **1.6%**。文强调 miniF2F 版本校正后与他法 **不可直接逐点比**；Putnam 按公开证明在统一 test split 上重算。

TTRL 后 formal-imo 分科（主文）：数论 **75.7%**、代数 **72.6%**、组合 **20.3%**。

### 4.7 IMO 2024 管线（主文）

- 几何 **P4** → **AlphaGeometry 2**；其余五题专家 **立即** 人工 Lean 形式化。
- 「找所有…」类：Gemini 1.5 Pro + Python 工具少样本产数百候选答案 → AlphaProof **快速证伪**错误候选 → TTRL 证明正确候选。
- **证明：** P1、P2、P6（代数/数论）；各约 **2–3 天** TTRL；组合 **P3、P5 未解**。
- 合计 4/6 题、**28/42**；P6 为 2024 最难题（文称仅 5 名选手解出）。
- 局限自陈：主 RL / TTRL 算力远超人类赛时；组合与开放域数学仍弱；后续目标降算力门槛、提供交互探索工具。

---

## 五、对照综合：证明器接地的两种「正确」

| | **VeriCoT** | **AlphaProof** |
|---|---|---|
| **接地对象** | 开放域 NL 推理链 | 形式数学证明过程 |
| **机器信任根** | Z3 对 SMT-LIB 片段的可满足/蕴涵 | Lean 内核（+ CLI 终检） |
| **神经部分仍可能错在哪** | 翻译失真、坏前提、表达力外（§5） | auto-formalization 保真度、几何外包、TTRL 算力墙 |
| **对仓库谱系的补位** | 给 [[过程奖励模型PRM谱系]]「过程对不对」一条 **非 PRM** 的逐步验真路径；给法律/生物医学 CoT 可检查前提 | 给 [[GRPO与DAPO算法族]]「可验证奖励」一条 **Lean 环境** 的极致实例；TTS 是搜索/TTRL 而非 PRM Best-of-N |
| **不要混用的口号** | 「通过 VeriCoT ≠ NL 事实为真」 | 「银牌级 ≠ 人类时限内可复现」 |

**跟读小结：**
想要 **非形式域** 的逐步逻辑卫生 → VeriCoT（显式前提 + Z3）。
想要 **数学命题** 的机器可检证明 → AlphaProof（Lean + RL + TTRL）。
二者都把「正确性」从 **另一神经网络的分数** 挪到 **外部形式系统**；PRM / GRPO 笔记里的配方在此 **只作槽位，不重写**。

---

## 六、可复查锚点（防编造）

| 主张 | 锚 |
|---|---|
| VeriCoT arXiv / 页数 | 2511.04662v1； 37 页 |
| Z3 + SMT-LIB | §2 末；Barrett et al. 2016；de Moura & Bjørner 2008 |
| Table 1 Pass：PW 45.2 / Bio 25.3 / SARA 15.2 | §3.3 Table 1 |
| 自反思 +46.4% / +41.1% rel（Pass / VCAR） | §3.4 正文；Abstract 约 46% / 41% |
| DPO 后 Pass +18.4% rel | §3.4；Abstract「18%」 |
| AlphaProof Nature doi / 卷期 | 10.1038/s41586-025-09833-y；Nature Vol 651, 19 Mar 2026 |
| ~1M→~80M 形式题；~80k TPU-day 主 RL | Fig.2 / 主文 Training & Main RL |
| 3B 网络；$r_t=-1$；AND 上 min return | 主文 Prover / Methods Lean environment |
| Table 1 TTRL 500d：99.6 / 58.3 / 56.1 | Table 1 |
| IMO 2024：3 非几何 + AG2→4/6，28/42 | 主文 Performance at the 2024 IMO |

**未写入本笔记（避免越界）：** PRM800K / Math-Shepherd 标签生成细节；GRPO 目标公式与 DAPO 四技；R1-Zero→R1 阶段表。

## 相关笔记

- [[多智能体辩论|Multi-Agent Debate]]
- [[形式化验证与LLM|Formal Verification for LLM]]
- [[GPTossModelCard|gpt-oss Model Card]]
- [[计算机使用智能体|Computer-Use Agents]]
- [[ToRL工具集成强化学习|Tool-Use RL / ToRL]]

