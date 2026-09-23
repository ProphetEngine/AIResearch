---
title: "芯片设计 AI：AlphaChip（宏布局 RL）+ ChipExpert（IC 专科 LLM）"
topic: 芯片设计AI
date: 2026-09-22
lines: [架构思想, 评测/复现争议字段]
status: archived
sources:
 - https://arxiv.org/abs/2004.10746
 - https://arxiv.org/abs/2408.00804
 - https://arxiv.org/abs/2306.09633
 - https://arxiv.org/abs/2302.11014
 - https://arxiv.org/abs/2411.10053
arxiv: ["2004.10746", "2408.00804", "2306.09633", "2302.11014", "2411.10053"]
doi:
 - "10.1038/s41586-021-03544-w"
 - "10.1038/s41586-024-08032-5"
 - "10.1038/s41586-022-04657-6"
related: ["硬件软件协同部署", "AI基础设施总览", "法律专科模型"]
github:
 - "https://github.com/google-research/circuit_training"
 - "https://github.com/NCTIE/ChipExpert"
 - "https://github.com/TILOS-AI-Institute/MacroPlacement"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
archived: 2026-09-22
---

# 芯片设计 AI：AlphaChip（宏布局 RL）+ ChipExpert（IC 专科 LLM）

> **定位**：**P1**——相对 [[硬件软件协同部署]]（加速器代际×精度×互联**选型白皮书**），本篇专写 **设计侧 AI** 两条正交轴：**(A) 宏布局 / floorplanning 的深度 RL**（Nature 2021 → 后命名 AlphaChip + Circuit Training）与 **(B) IC 设计专科开源 LLM**（ChipExpert）。
> **攻坚线**：**架构思想（主）** + **评测 / 复现争议字段（辅，强制单列）**。
> **硬划界（禁止重写）**：
> - **禁止重写** [[硬件软件协同部署]] 的 Blackwell / TPU7x Ironwood / NVL72 选型地图与部署成本叙事。
> - **禁止写成「已证实碾压商业工具」**：Nature 主张、独立评估（Kahng 等 / MacroPlacement）、Markov 元分析、作者 Addendum / 辩护文须**并列呈现**，不替任一侧下最终裁判。
> - **禁止编造**：Nature 全文 PDF 本窗被登录墙拦截，方法细节以 **arXiv:2004.10746** + Nature 着陆页摘要 / Change history 为准；评测数字锚定本地 （2026-09-22 CST）。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文 A（Nature）** | Mirhoseini, Goldie, et al. | *A graph placement methodology for fast chip design*；**Nature 594:207–212 (2021)**；Published **2021-06-09**；DOI **10.1038/s41586-021-03544-w**；摘要见 | 宏布局 RL 正式发表；主张「&lt;6 h、优于或可比人类」 |
| **主文 A′（可读全文）** | 同上团队 | *Chip Placement with Deep Reinforcement Learning*；arXiv:**2004.10746v1**（**2020-04-22**）；`https://arxiv.org/abs/2004.10746`（**15** 页 letter；CreationDate **2020-04-23** CST） | 方法细节（PPO、proxy cost、预训练/微调）主读取源 |
| **Addendum** | Goldie, Mirhoseini, et al. | DOI **10.1038/s41586-024-08032-5**；Published **2024-09-26**；PDF 本窗亦被 idp 墙；内容索引 DeepMind blog + 作者辩护文 | **正式命名 AlphaChip**；补充方法澄清 |
| **批判必读** | Markov | *The False Dawn…*；arXiv:**2306.09633v10**（**2024-09-28**）；`https://arxiv.org/abs/2306.09633`（**18** 页） | 复现缺口、基线、诚信/政策指控的元分析 |
| **独立评估** | Cheng, Kahng, Kundu, Wang, Wang | *An Updated Assessment…*；arXiv:**2302.11014v3**（**2026-03-10**）；`https://arxiv.org/abs/2302.11014`（**16** 页） | 公开 MacroPlacement 流上评估 **CT-Scratch / CT-AC** vs 加强 SA / 人类 / 商业工具 |
| **主文 B** | Xu et al. (NCTIE / SEU) | *ChipExpert…*；arXiv:**2408.00804v1**；`https://arxiv.org/abs/2408.00804`（**17** 页 A4；CreationDate **2024-08-05** CST） | Llama-3 8B IC 专科 LLM + ChatICD-Bench |
| **辅·博客** | DeepMind | https://deepmind.google/blog/how-alphachip-transformed-computer-chip-design/（**2024-09-26**）→ | 命名、checkpoint、TPU/Axion/MediaTek 叙事 |
| **辅·作者辩护（索引）** | Goldie, Mirhoseini, Dean | arXiv:**2411.10053**；`https://arxiv.org/abs/2411.10053` | 对 ISPD/Markov 批评的逐条反驳与时间线 |
| **开源** | Circuit Training / MacroPlacement / ChipExpert | CT：`google-research/circuit_training`；评估：`TILOS-AI-Institute/MacroPlacement`；CE：`NCTIE/ChipExpert` + HF `ChipExpert-8B-Instruct` / `ChatICD-Bench` | 复现入口（**非**「可复现 Nature 表 1」的充分条件） |

**落盘说明：** Nature / Addendum PDF `curl` → **303 → idp.nature.com**（见 ）。笔记内凡写「Nature 主张」均指着陆页摘要 + Change history；架构步骤以 arXiv 为准，并标明预印本≠期刊版可能存在差异。

**一句话抓手：** AlphaChip 把 **宏布局** 做成「可预训练的序贯放置游戏」；ChipExpert 把 **IC 知识问答** 做成「CPT→SFT→DPO→RAG」专科 LLM——前者争的是 **PPA / 复现**，后者争的是 **领域 QA 分数**，二者都不是 GPU/TPU **选型**问题。

---

## 二、议题边界：设计算法 ≠ 硬件选型

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **[[硬件软件协同部署]]** | 「TPU 代际存在、物理设计影响加速器交付」的**邻接标签** | Blackwell / NVL72 / TPU7x 规格表与精度选型 |
| **[[AI基础设施总览]]** | 「分布式 RL 训练需要多 GPU collect」的**存在** | DualPipe / FlashAttention / 训练并行通史 |
| **[[法律专科模型]] 等专科 LLM** | 「域继续预训练 + 对齐」**抽象对照** | 法律域数据配方全文 |
| **本篇** | 宏布局 MDP + edge-GNN；ChipExpert 训练栈与 ChatICD | 完整 EDA 工具链手册、商业 Innovus 操作步骤 |

### 2.2 问题立轴（可跟读）

`
[[硬件软件协同部署]] 硬件选型 ：买哪代加速器 / 哪档精度 / 哪类互联
────────────────────────────────────────────────────────
本篇 A 宏布局 RL ：给定 netlist，宏放在哪 → proxy / 后路由 PPA
本篇 B IC 专科 LLM ：IC 知识问答 / 教学助手（非自动布局器）
`

---

## 三、AlphaChip / Nature 线：宏布局作为 RL 游戏

### 3.1 问题形式（arXiv §1–3；Nature 摘要同口径）

- **对象：** netlist 图上的 **macros**（如 SRAM）与 **standard cells**（逻辑门）；目标优化 **PPA**（power / performance / area），并满足密度与布线拥塞约束。
- **Nature 摘要主张（着陆页原文口径）：** 「In under six hours… superior or comparable to those produced by humans in all key metrics」；并称方法用于 Google 下一代 AI 加速器。
- **MDP 化（arXiv）：** 智能体**逐个**把节点放到 chip canvas 网格；用 **PPO** 更新策略；终局奖励为 **负的 proxy cost**（需快评、且与真实 EDA 度量正相关）。

### 3.2 架构骨架（跟读）

`
netlist →（可选）标准单元聚类 / soft macros
 → RL 序贯放置 macros（edge-based graph embedding + policy/value net）
 → force-directed 放置标准单元簇
 → proxy cost（wirelength + density + congestion）→ reward
 → 预训练多块 → 目标块微调 / zero-shot
`

要点（arXiv + Nature 摘要交叉）：

| 构件 | 文内角色 |
|---|---|
| **Edge-based GCN / graph embedding** | 学习可迁移的 netlist 表示；支撑「见过更多块 → 更快更好」叙事 |
| **Proxy cost** | 代替完整 P&R（后者可数小时–数天）；争议焦点之一见 §四 |
| **Pre-train → fine-tune / zero-shot** | 作者侧强调「像人类一样积累经验」；批评侧强调**未预训练的复现不算同方法** |
| **Force-directed 收尾** | macros 放完后放置标准单元簇（非纯端到端 RL 放置一切） |

### 3.3 Circuit Training（开源落地名）

- **Author Correction（2022-03-31，DOI 10.1038/s41586-022-04657-6）** 与 Change history：**代码可用性**问题先被编辑记录（2021-10-26 告知不可用），后指向 GitHub **`google-research/circuit_training`**。
- **2024-09：** DeepMind blog / Addendum **命名 AlphaChip**，并公开 **预训练 checkpoint**（评估论文记为 **CT-AC**）。
- **重要：** CT 开源 ≠ 自动复现 Nature 表 1：专有 TPU 块、预训练数据、部分实现细节在独立评估中仍被标为缺口（见 §四）。

### 3.4 作者侧影响叙事（blog，2024-09-26；非独立审计）

Blog 主张（**待第三方同口径核验**）：用于 Google **多代 TPU** 布局；扩展至 **Axion** 等；**MediaTek** 称扩展用于先进工艺芯片。本笔记**索引主张、不升格为已证实产业碾压**。

---

## 四、【强制单列】Nature 争议 / 复现争议字段

> 本节只做**时间线 + 三方主张对照**。读者结论应来自对照，而非本笔记替 Nature「洗白」或「定罪」。

### 4.1 公开时间线（锚定 Nature Change history + 批判/辩护文）

| 时间（文内） | 事件 |
|---|---|
| **2020-04-22** | arXiv:2004.10746 预印本 |
| **2021-06-09** | Nature 正式发表；同期 Kahng *News & Views*（后撤回） |
| **2021-10-26** | Change history：编辑获悉**代码当时不可用** |
| **2022-03-31 / 04-01** | Author Correction；指向 Circuit Training 仓库 |
| **2022** | 内部「Stronger Baselines」等批评线；批判文称内部吹哨人争议与诉讼材料（**本篇不展开诉讼事实认定**） |
| **2023-09-20** | Nature **Editor’s Note**：性能主张遭质疑，编辑启动调查 |
| **2023-09-21** | Kahng *News & Views* **Retraction**（着陆页标题 *RETRACTED ARTICLE: AI system outperforms humans…*） |
| **2024-09-26** | **Addendum** 发表；Editor’s Note **移除**；编辑声明 post-publication review 后「issues… resolved to our satisfaction」并关闭调查；DeepMind 发 AlphaChip blog + checkpoint |
| **2024-09-28** | Markov arXiv **v10**：坚持主要关切未被 Addendum 消解 |
| **2024-11** | 作者辩护文 arXiv:2411.10053（*That Chip Has Sailed*） |
| **2026-03-10** | Kahng 等评估 arXiv **2302.11014v3**：在公开流上评估 **CT-AC / CT-Scratch** |

### 4.2 三方主张对照（禁止单边叙事）

| 轴 | Nature / 作者侧（摘要·Addendum·blog·2411.10053） | 批判侧（2306.09633 Markov） | 独立评估侧（2302.11014v3 MacroPlacement） |
|---|---|---|---|
| **顶线性能** | &lt;6 h 生成优于或可比人类的 floorplan；生产部署于 TPU 等 | 元分析称 RL **落后于**人类、**Simulated Annealing**、一般可得商业软件，且更慢；MLCAD 2023 公开赛 RL 未进前 5 | **加强 SA（GWTW+多线程）**与人类基线在多数公开用例上仍优于最新 CT；**未声称**「商业工具全面碾压一切」亦**未复现** Nature 表 1 专有块结果 |
| **复现条件** | CT 开源 + 2024 预训练权重；辩护文称批评者**未按 Nature 所述跑全流程**（缺预训练、算力×约 20 少 collect、未训至收敛、测例不代表现代芯片） | 关键步骤与多数输入被隐瞒；CT 仍缺复现 Nature 结果的关键部件；专有 TPU 块不可得 | 截至文内 **2025-11** 口径：**尚无**他人在会议/期刊上成功复现 [Nature] 主张的发表记录；数据与代码仍非完全可得 |
| **Proxy vs 真 PPA** | Proxy 与目标相关，支撑快速 RL | Proxy 设计有缺陷；与后路由真值可能脱节 | 在低 proxy cost 区间，proxy 与 Nature「Table 1」后路由指标 **Kendall 相关弱**（延续其先前观察） |
| **初始位置 / 聚类** | Addendum / 辩护文补充方法澄清（含预训练必要性等） | 指使用商业工具给出的初始 (x,y) 等**未充分披露**细节会显著改变结果 | 继续做 grouping 种子、SA 种子、预训练多样性等消融；记录 **发散 / 不稳定** |
| **编辑部立场** | 2024-09-26：调查关闭，发 **Addendum（非 Correction）** | 认为 Addendum **未回答**主要关切（樱桃采摘、数据污染风险、预训练数据不透明等） | 强调可重复评估责任；指出 CT 可扩展性与预训练方法仍有 **still-missing confirmations** |
| **CT-AC vs SA（公开数字，评估文）** | （作者侧强调预训练与生产影响） | （与 Google Team 2 / UCSD 线交叉引用） | 文内要点：**CT-AC** 在 **6/9** 例 **TNS** 更好；**SA** 在 **7/9** 例 **rWL**、**6/9** 例 **proxy cost** 更好；大体量设计上人类专家在多数 Nature Table 1 口径上优于 CT-AC；**SA 用显著更少资源**仍具优势 |

### 4.3 本笔记的读写纪律（硬约束落地）

1. **禁止**把 blog / Addendum 的「superhuman / 世界范围采用」写成已由独立评测锁死的事实。
2. **禁止**把 Markov 的「integrity substantially undermined」写成已被 Nature 编辑采纳的最终判决——编辑部选择了 **Addendum + 撤 Editor’s Note**。
3. **允许**陈述可核事实：Editor’s Note 曾挂一年；News & Views 已撤；公开 MacroPlacement 评估**未**复现「碾压商业/人类」的顶线故事，且报告 SA/人类在多指标上仍强。
4. **Circuit Training** = 社区可触达的方法近似实现；**≠** Nature 专有实验的充分复现包。

---

## 五、ChipExpert：IC 设计专科开源 LLM

### 5.1 定位（arXiv Abstract）

- **自称：** 「first open-source, instructional LLM specifically tailored for the IC design field」。
- **基座：** **Llama-3 8B**。
- **产物：** 代码 `NCTIE/ChipExpert`；权重 `China-NCTIEDA/ChipExpert-8B-Instruct`；基准 `ChatICD-Bench`（文内亦写 ChipICD-Bench）。
- **目标用户：** 学生基础学习、工程师查技术细节、研究者跟前沿——**知识问答 / 助教**，**不是**宏布局 RL 替代品。

### 5.2 训练管线（跟读）

`
数据准备（人工精选 + 合成）
 → Continue Pre-Training（IC 长文语料）
 → Instruction SFT（通用 QA + 域 QA 混合）
 → DPO 偏好对齐（含 red teaming）
 → 推理期 RAG（IC 知识库，抑幻觉）
`

**CPT 配比（Table 1）：**

| Data Type | Source | Original Tokens (B) | Training Tokens (B) | Ratio |
|---|---|---|---|---|
| Domain knowledge | Textbooks, Papers, etc. | 2.8 | 11.2 | 0.85 |
| Code | Verilog code, etc. | 0.6 | 0.6 | 0.05 |
| Wiki | Wikipedia | 1.3 | 1.3 | 0.10 |

其他可核锚点：SFT **2 epochs**；训练框架文内为 **ModelLink**、**8× Ascend-910B**；对齐用 **DPO**（相对 RLHF 的稳定/成本理由）；合成 QA 框架 **ChipInstruct**（多 GPT-4 agent 角色协作）；GQA 继承自 Llama-3。

### 5.3 ChatICD-Bench 与结果（§5；人类评分 0–1）

| 分层 | 构造 | 子域 |
|---|---|---|
| **Foundational** | 经典教材；专家出主观题 | **7**：analog / digital / EDA / SoC / power device / RF / RF antenna |
| **Advanced** | 近期刊论文 | 同上 **+ compute-in-memory + neural networks**（文称共 **9** 个 advanced 子域） |

文内人类评估主张（**作者自报，非第三方复现**）：

- 基础题：相对 Llama3-8B **显著提升**；与 **GPT-4** 整体可比；**EDA** 子域 ChipExpert **0.93** vs GPT-4 **0.87**。
- 进阶题：全子域优于 Llama3-8B；**9 个 advanced 子域中 6 个**优于 GPT-4；**compute-in-memory** 相对 GPT-4 高出 **0.28**（图读分，口径为人类均分差）。
- Analog 基础题相对 GPT-4 仍有缺口，作者归因于预训练覆盖。

**划界：** 这些数字衡量的是 **IC 知识问答**，**不能**外推为「ChipExpert 能自动做出比商业工具更好的 floorplan」。

---

## 六、两条线如何并列、如何不混写

| | AlphaChip / CT | ChipExpert |
|---|---|---|
| **决策对象** | 几何放置（macros on canvas） | 自然语言答疑 |
| **学习范式** | 在线 RL（PPO）+ 图网络 + proxy | CPT / SFT / DPO + RAG |
| **真值源** | 后路由 PPA / 商业 P&R（贵、慢） | 专家打分 /（可选）自动评 |
| **开源含义** | 算法骨架可跑；顶线 Nature 表难复现 | 权重+基准可下载；分数为作者评测 |
| **与 [[硬件软件协同部署]]** | 最多索引「曾用于 TPU 物理设计」 | 无加速器选型含义 |

共同教训（研究会可读）：**高影响力设计 AI 主张必须自带复现包与公开基准**；专科 LLM 降低的是**知识获取门槛**，不自动降低**物理设计 NP-hard 优化**的验证成本。

---

## 七、开放问题 / 待核实

1. **Nature / Addendum 全文 PDF**：本窗登录墙；若后续取得，应对照 arXiv 做「期刊版 vs 预印本」diff（尤其表格与预训练描述）。
2. **CT-AC 预训练数据清单**：公开指导有，完整数据与「是否污染测试块」在批评侧仍为开放指控——本笔记不裁决。
3. **ChatICD-Bench 题目数量、评委人数、自动评协议**：正文以图为主；精确 *n* **待核实**读图/附录。
4. **MediaTek / Axion 量化收益**：仅 blog 级主张；无独立对照实验入库。
5. **与更新 RL 布局器（Chipformer、AutoDMP 等）**：评估文明确**不**与后于 Nature 的方法主比；可另开议题，不塞进本篇顶线。

---

## 八、速查

| 项 | 值 |
|---|---|
| Nature DOI | 10.1038/s41586-021-03544-w |
| Addendum DOI | 10.1038/s41586-024-08032-5（2024-09-26） |
| Editor’s Note | 2023-09-20 挂上 → 2024-09-26 移除 |
| News & Views | Kahng；**2023-09-21 Retracted** |
| 可读方法 PDF | `https://arxiv.org/abs/2004.10746` |
| 批判 / 评估 | `2306.09633` / `2302.11014v3` |
| ChipExpert | `2408.00804`；Llama-3 8B；CPT 域知识 **0.85** |
| 禁止叙事 | 「已证实碾压商业工具」；重写 [[硬件软件协同部署]] GPU/TPU 选型 |

## 相关笔记

- [[MatterSim材料基础模型|MatterSim]]
- [[芯片设计AI|AlphaChip / ChipExpert]]
- [[科研智能体|Science Agents]]
- [[AgentBazaar经济对齐|Agent Bazaar]]
- [[网络防御基准|Cyber Defense Benchmark]]

