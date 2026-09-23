---
title: "Inference-time tree search：AB-MCTS（Adaptive Branching MCTS）"
topic: 推理时树搜索ABMCTS
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2503.04412
arxiv: ["2503.04412"]
related: ["推理时扩展TestTimeScaling", "过程奖励模型PRM谱系", "形式化验证与LLM", "EAGLE3投机解码"]
blog: "https://sakana.ai/ab-mcts/"
github: "https://github.com/SakanaAI/treequest"
github_arc2: "https://github.com/SakanaAI/ab-mcts-arc2"
archived: 2026-09-22
---

# Inference-time tree search：AB-MCTS（Adaptive Branching MCTS）

> **定位**：AB-MCTS **P0**——相对 **[[推理时扩展TestTimeScaling]]**（test-time scaling 通史 / o1·R1 产品叙事）补一块独立的 **外层多答案树搜索切片**：Sakana AI 的 **AB-MCTS**（*Wider or Deeper?*，arXiv **2503.04412v5**）把 **repeated sampling（只宽）** 与 **sequential refinement（只深）** 统一进 **自适应分支** 的 MCTS，并开源 **TreeQuest**。
> **攻坚线**：**架构思想（主）**——GEN 节点 + Thompson sampling 如何在「扩新枝 / 深挖旧枝」间做贝叶斯决策；**评测字段（辅）**——相对 repeated sampling / 固定宽度 standard MCTS 的同预算表。
> **硬划界**：
> - **≠ [[推理时扩展TestTimeScaling]]**：不写 o1/R1/s1 产品通史与「势」叙事；只取「推理期多算力 → 多答案生成」这一接口。
> - **≠ [[过程奖励模型PRM谱系]]**：不写过程奖励模型怎么训 / ORM vs PRM 谱系；AB-MCTS 的 $R$ 是 **可执行外部评分**（测例通过率、验证集分数等），不是逐步神经判别器。
> - **≠ [[形式化验证与LLM]]**：不写 Lean 形式证明搜索 / TTRL；本卡是 **自然语言+代码答案树**，宿主是测试/验证反馈，不是证明器内核。
> - **≠ [[EAGLE3投机解码]] 投机解码**：不写草稿模型–目标模型 token 级加速；本卡是 **答案级** 宽深搜索，不是解码器内部并行。
> - **禁止编造**：表数字、温度、预算、Pass@k 一律锚定官方 PDF（2026-09-22 CST）与 TreeQuest README / Sakana 博客可核字段。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Inoue, Misaki, Imajuku, Kuroki, Nakamura, Akiba (Sakana AI), *Wider or Deeper? Scaling LLM Inference-Time Compute with Adaptive Branching Tree Search* | arXiv:**2503.04412v5** \[cs.AI\] **7 Nov 2025**；Accepted as a **spotlight** at **NeurIPS 2025**；`https://arxiv.org/abs/2503.04412`（**30** 页 letter；5,138,162 bytes） | 一手：问题设定、Alg.1、AB-MCTS-M/A、主表、附录 Multi-LLM |
| **辅（代码）** | SakanaAI/**treequest** | https://github.com/SakanaAI/treequest → | Apache-2.0；`ABMCTSA` / `ABMCTSM`；ask–tell 批采样；Python ≥ 3.11 |
| **辅（博客）** | Sakana AI, *Inference-Time Scaling and Collective Intelligence…*（**2025-07-01**） | https://sakana.ai/ab-mcts/ → | Multi-LLM 叙事与 ARC-AGI-2 图口径（与附录 D 对齐） |
| **辅（实验码）** | SakanaAI/**ab-mcts-arc2** | https://github.com/SakanaAI/ab-mcts-arc2 | ARC-AGI-2 复现入口（博客点名；本笔记不展开仓库实现） |

**一句话抓手：** 在有 **外部反馈分数** $r=R(t_{\rm out})$ 的任务上，不要事先钉死「每层生几个孩子」——让搜索树在每个节点用 **后验预测 + Thompson sampling** 动态决定 **GEN（再采样一条新答案 = 变宽）** 还是 **沿已有孩子继续 refine（变深）**，从而把 LLM 的温度多样性与多轮修订放进同一框架。

---

## 二、议题边界：外层答案树，不是 TTS 通史 / PRM / 形式证明 / 投机解码

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[推理时扩展TestTimeScaling]]** | 「推理期多算力能抬解题率」；多答案生成是 TTS 三大族之一（文 §1/§2 自述） | o1/o3/R1 产品线、「势」、训练期 RL 长 CoT 通史 |
| **[[过程奖励模型PRM谱系]]** | 「过程对不对」可以用外部信号引导搜索（抽象槽位） | PRM800K、逐步 CE、ORM vs PRM 训练配方 |
| **[[形式化验证与LLM]]** | 「树搜索 + 外部校验」可作 inference scaling（形式侧对照点名即可） | Lean tactic RL、auto-formalize、IMO 2024 赛果表 |
| **[[EAGLE3投机解码]] 等** | 推理加速可与多答案搜索正交组合（文称 orthogonal） | 草稿–目标模型、投机接受准则、token 级并行 |

### 2.2 文内自划的 TTS 三族（跟读锚）

文 §1 / §2 把 inference-time scaling 分成：

1. **Post-training fine-tuning**（o1/o3、R1 等 → **不写**，→ [[推理时扩展TestTimeScaling]] / [[DeepSeekR1推理训练深读]]）；
2. **Reward-guided CoT**（逐步/句子级搜索，主打数学 → 接口留给 [[过程奖励模型PRM谱系]] / 相关树思想，**本卡不展开**）；
3. **Multiple answer generation**（本卡主战场）：同提示非零温度多次采样，再选优。

AB-MCTS 明确落在第 3 族，并主张：在 **编码等可拿外部反馈** 的场景，纯 repeated sampling **只有探索、没有利用**；固定宽度 MCTS（如 LATS §5.2 的 coding 配置）又 **钉死分支因子**，拦不住 LLM「同一提示可无限多样本」的潜力。

### 2.3 刻意不写什么

- Progressive Widening 的完整博弈论通史（文仅对照：PW 用访问次数启发式，**不**用已观察奖励做分支决策；Appendix C.4 有对照实验，本笔记只记结论）。
- 完整 LATS / RAP / SWE-Search / RepoUnderstander 方法复述（§2 点名作「standard MCTS」谱系入口）。
- TreeQuest 源码 walkthrough、PyMC 调参 playbook。
- 把 Multi-LLM 写成 MoA / Debate 通史（→ 可交叉 `[[多智能体辩论]]` / `[[MixtureOfAgents与TUMIX]]`，本卡只写附录 D 的 **多 GEN / 多生成器选择**）。

---

## 三、架构思想：无界分支 + 「更宽还是更深」

> 核心问题：**同一提示下 LLM 可无限多样本 → 分支因子理论上无界；如何在有限 API 预算内，principled 地在「再开一条新枝」与「深挖某条旧枝」之间分配？**

### 3.1 问题设定（§3.1 / Appendix A.1）

| 符号 | 含义（文内） |
|---|---|
| $f_{\rm LLM}(t_{\rm in})\to t_{\rm out}$ | 非零温度生成；根节点用任务提示；非根节点用 **历史答案 + 外部反馈** 做 refine |
| $r=R(t_{\rm out})$ | 评分；常归一到 $[0,1]$，框架允许任意范围 |
| 搜索目标 | 在有限 LLM 调用次数内找高 $r$ 的 $t_{\rm out}$ |
| 典型 $R$ | 公开测例通过率、验证集指标；终评可用隐藏测例（搜索期用 surrogate） |

**无单独 rollout：** 节点一旦生成即可直接算 $r$（相对游戏 MCTS 的简化）。

### 3.2 基线三角（Fig.1 跟读）

`
Repeated Sampling ──► 只宽：同一提示采样 n 次，启发式选优
Sequential Refinement ──► 只深：沿一条链反复 refine
Standard MCTS ──► 固定分支因子（实验取每扩 5 子；末轮贴齐预算）
AB-MCTS ──► 每节点动态：GEN（宽） vs 已有孩子（深）
`

### 3.3 Adaptive Branching MCTS 骨架（Algorithm 1）

每轮三步，共 $n_{\rm nodes}$ 次，每次 **加一个新节点**：

1. **Selection**：从根往下 `SelectChild`；若选中 **GEN** → 停，准备在该父节点上扩新枝；
2. **Expansion**：对选中父节点调用 LLM 生成新答案，挂上新孩子 $N_{\rm new}$；
3. **Score backup**：把 $N_{\rm new}$ 的分数沿树回传（M / A 规则不同）。

**GEN 节点（关键装置）：** 每个节点（含新叶）都挂一个 GEN 子；选中 GEN = 「从这个父答案再采样一条新答案」。于是：

- 非叶也可再扩（放松「只扩叶」）；
- 分支因子 **不** 作为静态超参；
- 同一提示可反复采样 → 自然承接 repeated sampling。

**为何不用 UCT：** GEN 会 **动态生成新臂**，不是标准多臂赌博机的静态臂集合；文改用 **贝叶斯后验 + Thompson sampling**。额外好处：便于并行扩（MLE-Bench 等评分子慢时有用）。

**SelectChild 的 Thompson 三步（所有变体共用）：** 对动作集 $A_N=\{a_0=\mathrm{GEN}, a_1,\ldots,a_{n_{\rm child}}\}$，为每个动作算后验预测 $P_N(r\mid a_j)$，各抽一个分数，取 $\arg\max$。

### 3.4 变体 A：AB-MCTS-M（Mixed Model）

| 要点 | 文内事实 |
|---|---|
| 模型 | 节点局部混合效应：$r=\alpha_j+\sigma_y\epsilon$，$\alpha_j=\mu_\alpha+\sigma_\alpha\epsilon_j$（式 1 / 附录 A.3） |
| 「组」 | 父节点 $N$ 下每个孩子子树 $T_{\rm sub}(N_j)$ 一组；**GEN = 尚无观测的新组**，其 $\alpha_0$ 从 $(\mu_\alpha,\sigma_\alpha)$ 后验借力 |
| 推断 | 每次 `SelectChild` 用 **MCMC（PyMC）** 拟合该节点模型 |
| Backup | 新分数追加到祖先的观测列表；**不**直接写进 GEN，但经共享参数影响 GEN 预测（方差通常更大 → 鼓励探索） |
| 先验（实验共用） | $\mu_\alpha\sim\mathcal{N}(0.5,0.2^2)$，$\sigma_\alpha\sim\mathrm{HalfNormal}(0.2^2)$，$\sigma_y\sim\mathrm{HalfNormal}(0.3^2)$（App. B.2） |

**跟读：** M 在各子树之间 **借统计强度**；适合「结果质量优先、能承受 MCMC 开销」的场景（附录 C.5）。节点度分布上偏深：LiveCodeBench+DeepSeek-V3 上约 **90%** 非叶节点度数仅 **1–3**，但长尾可到 **~40**（Fig.12 / §C.7）。

### 3.5 变体 B：AB-MCTS-A（Node Aggregation）

| 要点 | 文内事实 |
|---|---|
| 结构 | 引入与 GEN 同层的 **CONT**：「继续在已有孩子上 refine」；所有 LLM 孩子挂在 CONT 下（Fig.3） |
| 建模 | **无**跨动作共享参数；共轭先验 → **解析**后验更新（比 M 轻） |
| 两子变体 | **Gaussian**：normal-inverse-$\chi^2$（可非有界分）；**Beta**：分数在 $[0,1]$ |
| Backup | 分数先回传到 **导致该扩枝的 GEN**，再沿 GEN 的祖先（只含答案节点与 CONT）传播——**不会**串到其他 GEN |
| 先验（实验） | Gaussian：$\breve{m}=0,\breve{\kappa}=1,\breve{\nu}=1,\breve{\tau}^2=0.1$；Beta：$\breve{\alpha}=\breve{\beta}=0.5$ |

**跟读：** A 在每一深度先在 GEN vs CONT 间抉择；到深度 $d$ 需要连续 $d$ 次 CONT，故几何上更易 **偏宽**（§C.5）。同设定下低度数（1–3）非叶约占 **30%**，度数可 **>100**（Fig.12）。

### 3.6 M vs A 怎么选（文内建议，§C.5）

| 目标 | 倾向 |
|---|---|
| 结果质量优先 | **AB-MCTS-M**（主表平均秩最好） |
| 选节要快 / LLM 或评分子已是主耗时 | **AB-MCTS-A**（解析更新） |
| 任务已知受益于广探索（如 ARC-AGI） | **AB-MCTS-A** 常更合适 |

先验敏感度（App. A.6）：LiveCodeBench + GPT-4o、预算 $2^4$、$n=5$ 下多组先验 Pass@1 大致稳定——文主张后验很快被数据主导。

### 3.7 Multi-LLM AB-MCTS（Appendix D；博客展开）

在「宽/深」之外加第三维：**选哪个生成器**。

| 算法 | 机制（文） |
|---|---|
| **Generator Selection I** | 先按单模型 AB-MCTS 选节点，再对各 LLM 用其历史节点分数建后验，Thompson 选生成器 |
| **Generator Selection II** | 每个父节点挂 **多个 GEN**（每 LLM 一个）；先在各生成器子树内选，再在 $L$ 个候选间比分数（ARC-AGI-2 实验采用） |

博客日期 **2025-07-01** 将此叙事为 frontier 模型的 **collective intelligence**；实验码见 `ab-mcts-arc2`。与 MoA/Debate 的关系文标为未来工作（博客结语）。

---

## 四、评测字段（同预算对照）

### 4.1 设定（§4.1 / App. B.1）

| 项 | 值 |
|---|---|
| 基准 | **LiveCodeBench**（2024-08～11 题，防污染）、**CodeContest**、**ARC-AGI**（100 public eval，对齐 Greenblatt 提示）、**MLE-Bench** 三道低复杂度 Kaggle（Nomad2018 / Spooky Author / Random Acts of Pizza） |
| 模型 | **GPT-4o**（`gpt-4o-2024-08-06`，$T=0.6$）；**DeepSeek-V3**（`deepseek-chat`，$T=1.0$） |
| 预算 | 生成预算 = API 调用上限 **$2^7=128$**（ARC-AGI 另有扩至 **512** 的 scaling 曲线 Fig.6） |
| 基线 | Repeated Sampling (Best-of-$n$)；Sequential Refinement；Standard MCTS（LATS §5.2：每扩 **5** 子，末扩贴齐 128） |
| 重复 | LCB $n=5$；CodeContest / ARC $n=3$；MLE $n=1$（成本） |
| ARC 指标 | 主表报 **Pass@2**（官方协议）；Pass@1 见 Table 5，**方法排序不变** |
| MLE | 验证集选节点，隐藏测试报分；仅 GPT-4o + **AB-MCTS-M**（与基线） |

### 4.2 主表：Table 1（预算 128；分数↑更好；括号内为该设定下秩）

| Method | LCB GPT-4o | LCB DS-V3 | CC GPT-4o | CC DS-V3 | ARC GPT-4o | ARC DS-V3 | **Avg. Rank** |
|---|---|---|---|---|---|---|---|
| Repeated Sampling | 37.8±0.5 (4) | 40.7±1.9 (6) | 37.9±0.3 (4) | 43.2±0.9 (5) | 15.0±1.0 (**1**) | 18.6±1.0 (**1**) | 3.5 |
| Sequential Refinement | 37.8±2.4 (4) | 41.6±0.6 (5) | 30.1±0.3 (6) | 41.6±0.9 (6) | 8.7±0.9 (6) | 10.0±0.6 (6) | 5.5 |
| Standard MCTS | 36.7±1.0 (6) | **43.2±2.1 (1)** | 37.5±0.0 (5) | 43.8±0.9 (3) | 9.0±1.5 (5) | 14.0±1.5 (5) | 4.2 |
| **AB-MCTS-M** | 38.9±1.9 (2) | 43.0±1.5 (2) | **40.6±1.0 (1)** | 44.6±0.9 (2) | 12.3±1.2 (4) | 16.0±1.0 (3) | **2.3** |
| AB-MCTS-A (Gaussian) | **39.1±1.9 (1)** | 42.5±1.5 (3) | 40.2±1.7 (3) | 43.4±0.9 (4) | 13.0±3.6 (3) | 18.3±0.6 (2) | 2.7 |
| AB-MCTS-A (Beta) | 38.7±1.2 (3) | 42.3±0.8 (4) | 40.4±0.3 (2) | **44.8±0.6 (1)** | 14.0±2.1 (2) | 16.6±0.6 (4) | 2.7 |

**跟读要点（§4.2–4.3）：**

- **平均秩**：AB-MCTS 三变体占据前三；单点上 repeated sampling 仍常在 **ARC-AGI** 拿第一——说明「该任务偏广探索」时纯宽仍强，但 AB-MCTS 能 **接近** 它并在编码基准上拉开。
- **预算曲线（Fig.4，GPT-4o）**：LCB 上预算 $2^3$ 起 AB-MCTS 已常领先；CodeContest 上 $2^5$ 以后优势更明显。
- **树形（Fig.5）**：横轴 $\log(\mathrm{mean\ depth}/\mathrm{mean\ width})$；AB-MCTS 相对 standard MCTS **更宽**，同时又能在 sequential refinement 占优的任务上「够深」——宽深自适应是主叙事。
- **固定宽度敏感（Table 6）**：DeepSeek-V3 + LCB，standard MCTS $w\in\{3,5,10\}$ → Pass@1 最佳为 **$w=5$**（0.432±0.021），过大过小都掉——反衬自适应分支免调 $w$。
- **vs Progressive Widening（Table 4）**：deepseek-v3-0324、预算 128；调好的 PW 可接近 AB-MCTS，但对 $(k,\alpha)$ **敏感且方差大**；AB-MCTS 免这类钉死规则。

### 4.3 Table 2：MLE-Bench（GPT-4o；Avg = 平均秩，↓更好）

| Method | Nomad2018 | Spooky. | Pizza. | Avg. |
|---|---|---|---|---|
| Repeated Sampling | 0.065 (3) | 0.47 (4) | 0.72 (2) | 3.0 |
| Sequential Refinement | **0.059 (1)** | 0.46 (3) | 0.62 (3) | 2.3 |
| Standard MCTS | 0.076 (4) | 0.45 (2) | 0.60 (4) | 3.3 |
| **AB-MCTS-M** | 0.060 (2) | **0.38 (1)** | **0.72 (1)** | **1.3** |

文注：三道题上「最佳基线」各不相同（有的偏深、有的偏宽）——AB-MCTS-M 的价值是 **事先不知最优宽深时仍稳**。

### 4.4 ARC-AGI 大预算（Fig.6）与 Multi-LLM ARC-AGI-2（App. D / 博客）

**ARC-AGI-1 + DeepSeek-V3，预算扩至 $2^9=512$：** 文称 AB-MCTS 在约 200→500 仍明显抬升，而 repeated sampling 增速趋缓；standard MCTS 亦随预算升，但成功率显著低于 AB-MCTS。

**ARC-AGI-2 public eval 120 题；预算 250；生成变换规则为 Python；奖励 = demo 通过数；主报 Pass@k（覆盖，非官方 Pass@2）：**

| 方法 | 文内 / 博客口径 |
|---|---|
| o4-mini Repeated Sampling | **23%** Pass@k |
| o4-mini 单模型 AB-MCTS | **27.5%**（约 50 次调用后相对 repeated 差距更明显） |
| Multi-LLM AB-MCTS（o4-mini + Gemini-2.5-Pro + DeepSeek-R1-0528；Selection II） | **>30%** 找到正确解 |
| 简单规则选 2 答的 Pass@2（参考） | **19.2%**（相对 ~30% Pass@k 仍差 >10 pp；文标答案选择为未来工作） |

模型：`gemini-2.5-pro-preview-05-06`、`o4-mini-2025-04-16`、`deepseek-r1-0528`；温度均为 **0.6**。博客另图示：难例上 LLM 用量更均衡；存在「单模不可解、多模接力 refine 可解」的协作树例。

---

## 五、开源落地：TreeQuest（辅材料）

摘自 README（2026-09-22 抓取），**不**替代论文算法定义：

| 能力 | 说明 |
|---|---|
| API | `algo.init_tree()` / `step`；或 **`ask_batch` / `tell`**（批并行；尤其 AB-MCTS-M 的 `step` 可能慢） |
| 算法类 | `ABMCTSA`、`ABMCTSM`；另有 `StandardMCTS`、BFS 族等 |
| 多动作 | `generate_fns: dict[action_name → (parent_state)→(state, score)]` → 自然支持 Multi-LLM |
| 分数约定 | 期望归一到 **$[0,1]$** |
| 安装 | `pip/uv add "treequest[all]"`；可选 `[abmcts-m]`（PyMC）、`[vis]` |
| 可视化 | `tq.render(..., format="html"|"pdf")`；HTML 含用户 state 时注意 XSS |
| 许可 | **Apache 2.0**；引用 bib 指向 NeurIPS 2025 / OpenReview `jAsr5GHt3P` |

推荐起步：`batch_size<=5`（过大易把树撑得过宽；见仓库 `PROFILING.md`）。

---

## 六、局限与文内自述未来（§5 / §C.10 / §D.3）

1. **依赖可靠评分器 $R$**——任务若无公开测例/验证集，搜索信号本身成瓶颈。
2. **成本模型粗**：当前以 API **调用次数** 为预算；未计入真实延迟、评分子 GPU 小时等细粒度代价。
3. **答案选择缝**：Multi-LLM 上 Pass@k ≫ 简单 Pass@2 → 需更好的终答选择 / 奖励模型 / LLM-as-Judge。
4. **难度自适应**：文提议用累积奖励估难度，在 M（偏深）与 A（偏宽）间切换。
5. **与 MoA / Debate / LE-MCTS 等关系**：博客列为 open。

---

## 七、跟读清单（可操作）

1. 先钉 Fig.1：三基线 vs AB-MCTS 的「宽/深/固定宽」漫画。
2. 读 Alg.1 + GEN 定义 → 理解「无界分支」如何落到数据结构。
3. 对照 §3.3 vs §3.4：M（混合+MCMC）与 A（CONT+共轭）的 backup 差异——这是实现分叉点。
4. 扫 Table 1 的 **Avg. Rank** 与 ARC 列：理解「不是处处第一，但是处处靠前」。
5. 若关心集体智能：Appendix D + 博客 Fig.13–16 + `ab-mcts-arc2`，但 **不要** 把 Pass@k 误写成官方 contest Pass@2。
6. 动手：TreeQuest Quick Start 用假 `generate` 跑通 `ABMCTSA`，再换真实 LLM+测例分数。

---

## 八、交叉引用

- TTS 产品 / 训练侧通史 → `[[推理时扩展TestTimeScaling]]`
- 过程奖励训练 → `[[过程奖励模型PRM谱系]]`
- 形式证明树搜索 → `[[形式化验证与LLM]]`
- 解码器投机加速 → `[[EAGLE3投机解码]]`
- 多代理辩论 / MoA → `[[多智能体辩论]]` / `[[MixtureOfAgents与TUMIX]]`（仅接口，本卡不重写）

---

## 九、本地核验（禁编造备忘）

| 项 | 值 |
|---|---|
| PDF | `https://arxiv.org/abs/2503.04412`；标题 *Wider or Deeper?…*；**30** 页；arXiv **2503.04412v5**；NeurIPS 2025 spotlight |
| 抽取 | （2026-09-22 CST） |
| 主表 Avg.Rank | M **2.3** / A-G **2.7** / A-B **2.7** / RS **3.5** / StdMCTS **4.2** / Seq **5.5** |
| 预算 | 主实验 **128**；ARC scaling **512**；ARC-AGI-2 Multi-LLM **250** |
| 开源 | TreeQuest Apache-2.0；博客 2025-07-01 |

*本笔记为草稿（status: draft）；数字以官方 PDF 为准；博客/README 仅作辅入口与 Multi-LLM 叙事对齐。*

## 相关笔记

- [[推理时树搜索ABMCTS|AB-MCTS]]
- [[SimPO与ORPO偏好优化|SimPO / ORPO]]
- [[VendingBench经营长程评测|Vending-Bench]]

