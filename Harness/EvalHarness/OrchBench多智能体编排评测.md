---
title: "多智能体编排评测：OrchBench（≠ MAD 机制）"
topic: OrchBench多智能体编排评测
date: 2026-09-22
lines: [评测字段, 编排接口思想]
status: archived
sources:
 - https://arxiv.org/abs/2607.25656 # 3.16M / 25p（主文）
 - https://arxiv.org/abs/2601.02854 # 2.00M / 10p（补链，不升主）
arxiv: ["2607.25656", "2601.02854"]
related: ["多智能体辩论", "MixtureOfAgents与TUMIX", "AgentBazaar经济对齐", "智能体工具与长程任务", "合成用户仿真"]
code_promised: null # OrchBench 文内未见作者自发布评测仓 URL
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 多智能体编排评测：OrchBench（≠ MAD 机制）

> **定位**：编排计划评测主题轴——仓库已有 **[[多智能体辩论]]**（辩论协议：多样性 / 置信度 / 反共识）、**[[MixtureOfAgents与TUMIX]]**（MoA 层间合成 / TUMIX 工具策略混合）、**[[AgentBazaar经济对齐]]**（多代理市场经济对齐）、**[[智能体工具与长程任务]]**（旗舰工具环 / 长程产品叙事）。本卡转问一刀**可隔离的编排计划评测**：
> - **OrchBench**（*Evaluating Multi-Agent Orchestration Plans in Isolation via Deterministic Simulation*）：把端到端 MAS 成绩拆开——**固定任务 DAG + 上下文上限 $L$ + agent 预算 $A_{\max}$**，只评 planner 产出的 $\pi=(\alpha,R)$（子任务分配 × 跨 agent 信息转移与保留比）；**确定性仿真器**代替 worker / 工具 / 环境噪声，输出质量 $Q$、makespan 效率、token 效率与可解释协调失败。
> **攻坚线**：**评测字段（主）**——仿真—真实相关、规模化缺失转移、信息覆盖 vs agent 数；**编排接口思想（辅）**——计划表示 $\pi=(\alpha,R)$、压缩敏感类、缺失转移惩罚 $\lambda$。
> **硬划界（开篇钉死）**：
> - **≠ [[多智能体辩论]]**：禁止重写 MAD 鞅诊断、FREE-MAD 全轨迹打分、分层分歧仪器、DynaDebate 路径生成。本卡**不是**同题 QA 委员会辩论；M3MAD-Bench 与 [[多智能体辩论]] 更近 → **仅 §七补链**，不升主。
> - **≠ [[MixtureOfAgents与TUMIX]]**：禁止重写 MoA Aggregate-and-Synthesize、TUMIX 工具–文本混合池 / 早停。本卡评的是 **DAG 上的分配与 handoff 计划**，不是测试时异构合成或工具策略混合。
> - **≠ [[AgentBazaar经济对齐]]**：禁止重写 Agent Bazaar 市场 POSG、EAS、Sybil / 柠檬市场。本卡**无**经济角色与交易环境。
> - **≠ [[智能体工具与长程任务]]**：禁止重写 Claude/GPT 旗舰 MCP、并行工具、System Card 长程产品叙事；Claude Code 在本卡只作**真实执行对照框架**一句。
> - **≠ [[合成用户仿真]]**：τ-bench / ToolEmu 用户仿与工具仿不重开；OrchBench 固定 DAG，**不**仿真用户。
> **禁止编造**：机制、公式编号、表数字一律锚定官方 PDF（2026-09-22 CST）。图内未列表格的精确曲线点标 **待核实读图**。OrchBench 文内**未见**作者自发布官方评测仓 URL → **无承诺仓**（仅引用 Claude Code / Crush 等第三方框架仓）。
> **二进制**：两篇均 **≪20MB** 且页数 **≪80**（见 §一）→ **官方 HTTPS 外链**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文** | Ren, He, Zhang, Qian, Han, Zheng, Li & Zhang, *OrchBench: Evaluating Multi-Agent Orchestration Plans in Isolation via Deterministic Simulation* | arXiv:**2607.25656**v1 \[cs.AI\] **28 Jul 2026**；Fudan / 中关村学院 / Queen Mary；`https://arxiv.org/abs/2607.25656`（**3.16M**，3,312,344 B；**25** 页 letter） | **编排计划隔离仿真评测**：DAG + $\pi=(\alpha,R)$ + 确定性仿真器；与 Claude Code 质量相关 $r=0.816$ |
| **补链** | Li, Zhang, Li et al., *M3MAD-Bench: Multi-Dimensional Evaluation of Multi-Agent Debate Across Domains and Modalities* | arXiv:**2601.02854**v2 \[cs.AI\]（published **2026-01-06**；v2 **31 Jul 2026**）；ACMMM **2026**；`https://arxiv.org/abs/2601.02854`（**2.00M**，2,093,773 B；**10** 页） | **MAD 多维评测箱**（域×模态×效率）；与 [[多智能体辩论]] 叠床 → **不升主**，仅索引 |

**代码（文内）：** OrchBench → **无作者承诺仓**（2026-09-22 抽取未见 `github.com/.../OrchBench` 类自述）。M3MAD → `https://github.com/liaolea/M3MAD-Bench`（补链文 Abstract）。

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2607.25656-orchbench.pdf` | **3.16M**（3,312,344 B） | 25 | **官方 HTTPS 外链**（≪20MB；≪80 页） |
| `2601.02854-m3mad.pdf` | **2.00M**（2,093,773 B） | 10 | **官方 HTTPS 外链**（补链；≪20MB） |

**一句话抓手：** 端到端 MAS 分数把「编排好不好」与「worker / 工具 / 环境稳不稳」揉在一起且极贵；OrchBench 只让模型交**编排计划**，用**确定性仿真**在相同 DAG / $L$ / $A_{\max}$ 下比 $Q$、makespan、token，并暴露 **missing transfer**——验证侧与 Claude Code 质量相关 **$r=0.816$**，成本约 **1.3% tokens / 10.3% wall-clock**（Abstract）。

---

## 二、议题边界：隔离编排计划 ≠ 辩论 / 聚合 / 市场 / 产品工具环

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **辩论协议** | 多样性初始化、置信度、去共识、分歧测量 | **[[多智能体辩论]]** | **否**（禁 MAD 机制正文） |
| **测试时异构聚合** | MoA 层合成、TUMIX 工具策略混合 | **[[MixtureOfAgents与TUMIX]]** | **否** |
| **多代理市场失败** | B2C/C2C、EAS、harness | **[[AgentBazaar经济对齐]]** | **否** |
| **旗舰工具环叙事** | MCP、并行工具、长程 System Card | **[[智能体工具与长程任务]]** | **否**（Claude Code 仅作真实对照） |
| **编排计划可隔离评测** | DAG 上 $\alpha$+$R$、仿真 $Q$/makespan/token、缺失转移诊断 | **本篇主文** | **是** |
| **MAD 标准化评测箱** | 多域/多模态/多维效率 | **M3MAD 补链** | **索引仅** |

跟读直觉：[[多智能体辩论]] 问「**同题上怎么辩才不退化成贵的多数票**」；[[MixtureOfAgents与TUMIX]] 问「**异构输出怎么合成 / 工具策略怎么混合缩放**」；本卡问「**在已知依赖图上，分配与信息 handoff 计划本身好不好——且不让 worker 噪声掺进来**」。三者都碰「多智能体」，但评测对象与失败模式完全不同。

### 2.2 文内自划界（跟读）

Related Work 三组：① PlanBench / FlowBench / WorFBench 测**结构正确性**，**不**仿真「分配到 agent 之后」的执行后果；② MASBENCH / PerspectiveGap / OrchRM 各切 MAS 的一片，OrchBench 评**完整计划且不跑 worker**；③ HiddenBench / Silo-Bench 评**交互中**的信息合并，OrchBench 评**事先**的分配、调度、转移与压缩。端到端 AgentBench / GAIA / WebArena / SWE-bench / OSWorld / MultiAgentBench 等一律标为「成绩揉在一起」的对照，不重开 [[智能体工具与长程任务]] 产品通史。

`
 多智能体「协调」问题链
 │
 ┌─────────────┼─────────────┬──────────────┐
 ▼ ▼ ▼ ▼
 怎么辩 怎么合成/混工具 市场是否稳 编排计划好不好
 [[多智能体辩论]] [[MixtureOfAgents与TUMIX]] [[AgentBazaar经济对齐]] 本篇 OrchBench
 (禁重写) (禁重写) (禁重写) 隔离仿真评测
 │
 M3MAD 补链
 (辩论评测箱→[[多智能体辩论]])
`

---

## 三、问题形式与三阶段管线（编排接口）

### 3.1 固定依赖，只评编排

Problem Formulation：任务分解与依赖图 $G=(V,E)$ **固定**（$n=|V|$），不是编排决策。每个子任务带描述、输入/执行/输出 token 预算、时间预算 $\tau_v$、以及压缩敏感类 $c_v\in\{\mathrm{robust},\mathrm{balanced},\mathrm{fragile}\}$。评测输入再加每 agent 上下文上限 $L$ 与最大 agent 数 $A_{\max}$。

被测 planner 产出计划 $\pi=(\alpha,R)$：

- **$\alpha: V\to\{1,\ldots,A_{\max}\}$**：子任务→agent；同 agent 上依赖结果**本地复用**（100%）。
- **$R$**：跨 agent 依赖边 $(u,v)$ 须声明转移与保留比 $e\in(0,1]$；漏报 → **missing transfer**；声明了但 $E$ 中无边 → invalid。

仿真器在任务与上下文约束下返回结果质量 $Q$、makespan $M$、总 token $T$。

### 3.2 DAG Construction → Planning → Deterministic Simulation

Fig.2 三阶段：

1. **DAG Construction**：种子题来自 Finance Agent / DS-1000 / Qasper / BIRD-SQL；用自然并行度 $k_{99}/n$（达最大 makespan 压缩约 99% 所需最少 worker 数）控制并行；judge（格式）+ judge（分解/并行）+ refiner 迭代，直到双法官通过。主实验 **240** 个任务 DAG；另造 $n\in\{200,500,1000\}$ 做可扩展性。
2. **Orchestration Planning**：planner $F_\theta$ 产出 workflow script $z$，确定性解释器展开为 $\pi=(\alpha,R)$。$e$ 越大保信息越多、通信与上下文越贵；fragile 输出要求更高保留。
3. **Deterministic Simulation**：对齐真实框架六段生命周期——依赖解析、agent 调度、上下文获取、上下文管理、子任务执行、状态更新——**不调用 worker LLM / 工具**。

调度时钟（文内式 (1)）：子任务 $v$ 在 agent $a=\alpha(v)$ 上的开始时间
$s_v=\max\bigl(c_a,\ \max_{u\in\mathrm{Parents}(v)} f_u\bigr)$——同 agent 串行、异 agent 可并行。缺失转移时父包有效质量乘惩罚 $\lambda$（主设定 $\lambda=0.5$，$A_{\max}=100$）。压缩（式 (2)）按敏感类折损质量；终端任务宏平均得 $Q$（式 (5)）。

### 3.3 分数定义（评测字段接口）

| 分量 | 定义要点（文内） | 直觉 |
|---|---|---|
| $Q$ | 终端任务质量宏平均 | 信息是否传到、压缩是否毁 fragile 边 |
| $E_{\mathrm{time}}$ | $\min(1, C/M)$，$C$=加权关键路径，$M$=观测 makespan | 离理想并行下界有多近 |
| $E_{\mathrm{token}}$ | $\min(1, T_{\mathrm{single}}/T)$ | 相对单 agent 串行基线的 token 效率 |
| **Score** | $(Q+E_{\mathrm{time}}+E_{\mathrm{token}})/3$（式 (7)） | 综合；另报 makespan、token、#agents、missing transfers 作诊断 |

文内明确：仿真对**真实时间/token**的相关弱（框架依赖，Appendix D-II），但对**质量**强——OrchBench 适合筛计划，目标框架上再少量实跑验证。

---

## 四、仿真保真：与真实执行对齐

### 4.1 结构与结果相关（MultiAgentBench × Claude Code）

**Table 1（结构/规模）：** Scale 侧 DA（声明子 agent 数）Pearson $r=0.973$；CA $0.749$；SA $0.829$。Structure 侧 SDT $0.928$、PU $0.768$、WD $0.887$、ILR（缺失信息转移）$0.664$。

**Table 2（结果）：** Final score vs 真实任务质量 **Pearson $r=0.816$**（$p=0.047$），Spearman $\rho=0.771$；Time / Token usage 相关为负且不显著——印证「筛质量、不替框架计费」。

**Table 3（leave-one-model-out）：** 去掉任一验证模型后相关仍为正；去掉 GLM-5.1 时升至 $r=0.949$。

**Fig.3（跨框架）：** 与 Claude Code、SWE-mini、OpenHands、Crush 四处真实执行均保持正相关（上三角 Pearson / 下三角 Spearman；矩阵格点 OrchBench–Claude Code 约 **0.82 / 0.77**）→ 预测不绑死单一 harness。

### 4.2 成本与筛选用途

| 证据 | 文内数字 | 用途 |
|---|---|---|
| Abstract | **1.3%** tokens、**10.3%** wall-clock（相对 Claude Code） | 总括效率 |
| Table 8 WideSearch | 真实 **17.35M** / 仿真 **44.61K** tokens；**56.13** / **0.51** min（约 **389× / 110×**） | 大任务极便宜 |
| Table 8 MultiAgentBench | **383.09K** / **5.16K**；**5.61** / **0.58** min（文称至少 **74× / 9.7×**） | 与 Fig.1「9.7× Faster」一致 |
| Table 7 | 按仿真分歧挑 5 题实跑：排序 Spearman **0.754**、pair accuracy **0.800** ≫ Random **0.176 / 0.613** | 有限实跑预算下的模型比较 |
| Table 9 | 仿真引导补一条跨角色 handoff：真实分 **3.754→4.150** /5 | 诊断可回流改计划 |

验证模型池（文内）：GLM-5.1、DeepSeek-V4-Pro/Flash、Qwen3.6-35B-A3B、Kimi-K2.6、Doubao-Seed-2.0-Mini；主评再加 Gemini-3.1-Pro-Preview、Claude-Opus-4.8、GPT-5.5。真实执行对照：**Claude Code** dynamic-workflow。

---

## 五、主发现：保信息 > 堆 agent；并行收益随协调失败衰减

### 5.1 主表随规模恶化（Table 4 压缩）

在 $n\in\{10,20,50,100\}$ 上，平均 missing transfers 区间从 $n=10$ 的 **[0.00, 0.43]** 拉到 $n=100$ 的 **[0.07, 22.70]**。**没有**模型在所有规模都拿最高 Score：

| $n$ | Score 领先（文内） | 旁注 |
|---|---|---|
| 10 | GPT-5.5 **0.810** | Gemini Miss.=**0.00**；Claude Miss.=**0.00** |
| 20 | GLM-5.1 **0.746** | Doubao / Qwen Miss. 升至 **3.47 / 3.60** |
| 50 | Claude-Opus-4.8 **0.644** | Gemini Miss.=**0.00** 仍 Score≈**0.642** |
| 100 | Gemini-3.1-Pro **0.573** | Doubao Miss.=**22.70**；Qwen **14.37**；Kimi **13.00** |

跟读：大规模下分数被 **信息路由完整性** 拉开，而不是被「声明了多少 agent」拉开。

### 5.2 Transfer Coverage Matters More Than Agent Count

**Table 5：** Coverage–Q（成功转移覆盖 vs 质量）在各规模 **0.614–0.952**；Agents–Q 在 $n=100$ 仅 **-0.021**，Agents–Score **-0.676**。结论句（Results）：**保任务关键信息比单纯加 agent 更重要**；并行收益随协调失败累积而衰减。

**极端规模（Fig.5，$A_{\max}=100$，$n=200/500/1000$）：** 从 500→1000，Claude 转移覆盖 **0.981→0.441**；DeepSeek **0.981→0.398**，并产生约 **872.3 / 907.4** 次 missing transfers；Gemini 仍保持完整覆盖与明显更高质量（正文叙述；曲线点 **待核实读图**）。

**Fig.4（$A_{\max}$ 扫描，六底座 × 50 DAG）：** 增大预算先减压压缩、抬 Score，但很快饱和——$A_{\max}$ 从 **16→64** 时 agent 数翻倍以上，Score 几乎不动。

### 5.3 何时多 agent 才有用（Table 6）

同一 50 个 DAG 上单 vs 多 agent，扫上下文上限 $L$：

| $L$ | Single Qual. | Multi Qual. | $\Delta$ Qual. |
|---|---|---|---|
| 16k | 0.423 | 0.725 | **+0.302** |
| 32k | 0.649 | 0.821 | +0.172 |
| 64k | 0.792 | 0.852 | +0.060 |
| 128k | 0.852 | 0.859 | **+0.007** |

接口句：工作状态**塞不进**单窗口时，多 agent 靠拆分避免反复压缩；一旦装得下，协调本身可变成纯开销。这与 [[多智能体辩论]]「辩论很贵」同属成本自觉，但失败模式是 **handoff/压缩**，不是 **从众/鞅**。

### 5.4 消融与敏感度（跟读锚点，不展开附录课）

- 缺失转移因子 $\lambda$（Table 20）：$\lambda\uparrow$ 机械抬高 Quality/Final，但模型区分度 $\sigma_Q$ 下降；主文取 **$\lambda=0.5$** 作折中。
- Appendix 另有转移/压缩设计消融、DAG 质量与失败案例——本卡不重抄附录教程，跟读时按需打开 。

---

## 六、对研究会的含义（评测字段优先）

1. **归因隔离**：若产品叙事只报端到端 MAS 分，无法回答「是编排烂还是 worker/工具炸」。OrchBench 把问题收成可复现的 $\pi$ 比较——适合作为编排研究的**前置筛**，再在目标框架（Claude Code 等）上少量实跑。
2. **诊断优于堆料**：Coverage 相关稳、agent 数相关垮；工程默认「再开几个 subagent」在大 DAG 上可能制造更多 missing transfer。仿真引导补 handoff（Table 9）是可操作的改进环。
3. **效率承诺有条件**：token/时间狂降成立于**仿真代替执行**；真实时间/token **不可**由仿真可靠预测（文内自承）→ 入库评测卡应同时记 Score 与框架实跑计费，禁止把 $E_{\mathrm{token}}$ 误读成「线上账单」。
4. **与相邻卡接线**：要写辩论机制 → **[[多智能体辩论]]**；要写异构合成/工具混合 → **[[MixtureOfAgents与TUMIX]]**；要写市场系统风险 → **[[AgentBazaar经济对齐]]**；要写旗舰工具环产品 → **[[智能体工具与长程任务]]**。本卡只钉「编排计划隔离仿真」。

---

## 七、补链 · M3MAD-Bench（不升主）

**为何只补链：** Agenda 与本卡划界一致——M3MAD 是 **MAD 方法的多维评测箱**（Multi-domain × Multi-modal × Multi-dimensional metrics），评的是辩论策略在 13 数据集 / 9 底座上的准确率与 token·时间代价，并给九条「MAD 并非处处有效」洞察（协作优于对抗、成本高、多轮收益有限、互相强化错误等）。这与 **[[多智能体辩论]]** 同题族，升主会叠床；与 OrchBench「DAG 编排计划隔离」正交。

**仅录接口（禁止展开成第二主文）：**

| 字段 | 文内 |
|---|---|
| 定位 | 统一 MAD 评测协议；补文本-only 局限，纳入视觉–语言 |
| 覆盖 | 五域（Knowledge / Math / Medicine / Natural Sciences / Complex Reasoning），**13** 数据集（7 文本 + 6 多模态） |
| 底座 | **9** 个不同架构/规模/模态能力模型 |
| 指标 | 准确率 + token + 推理时间 |
| 代码 | `https://github.com/liaolea/M3MAD-Bench` |
| 会议 | ACMMM **2026**（文内 MM ’26） |

跟读建议：若后续要加深 MAD **评测协议**而非机制，可开 [[多智能体辩论]] 附录或独立短卡；**不要**并进本 OrchBench 正文。

---

## 八、跟读清单与开放问题

**建议跟读顺序：** Abstract + Fig.1 → §Problem Formulation（$\pi=(\alpha,R)$）→ §Methodology 仿真六段 → Table 2/4/5/6/8/9 → Conclusion。Fig.4/5 曲线点以读图核实为准。

**开放问题（不编答案）：**

1. 仿真质量模型（几何均值父质量 × 压缩敏感指数）对真实 worker 错误模式的覆盖边界在哪？
2. 固定 DAG 假设下，「先分解再编排」的联合优化如何接入而不重新揉进端到端噪声？
3. 与 HiddenBench / Silo-Bench 的「交互中通信」能否共用同一缺失转移仪器？
4. 作者评测仓若后续公开，应补 `code_promised` 字段并核版本哈希。

---

## 九、材料体积

| 项 | 结论 |
|---|---|
| 一手 PDF | **有**（主文 + 补链均已 `curl`→本地） |
| OrchBench | **3.16MB / 25 页** → **官方 HTTPS 外链**至 （已落盘）；正式库可同步  |
| M3MAD | **2.00MB / 10 页** → **官方 HTTPS 外链（补链）**；不另开议题卡 |
| >20MB / >80 页规则 | **均不适用**； |
| 抽取 | 已存 `*.txt`；瘦身备份可只保留抽取 + arXiv 链 |
| 成稿路径 | [[OrchBench多智能体编排评测]] |

**回报表摘要：** [[OrchBench多智能体编排评测]] 主锚 OrchBench（编排计划隔离仿真；≠ MAD/MoA/市场/旗舰工具环）；M3MAD 仅补链；禁编造；中文归档；date 2026-09-22。
