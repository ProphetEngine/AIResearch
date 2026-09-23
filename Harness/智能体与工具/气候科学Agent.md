---
title: "气候科学/政策 Agent：ClimateAgent + ClimateAgents（附录 ClimAgent）"
topic: 气候科学Agent
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2511.20109 # 4.2M / 49p
 - https://arxiv.org/abs/2603.13840 # 6.4M / 15p
 - https://arxiv.org/abs/2604.16922 # 1.9M / 23p（附录）
arxiv: ["2511.20109", "2603.13840", "2604.16922"]
related: ["天气气候基础模型", "科研智能体", "智能体工具与长程任务", "代码智能体Harness史线"]
code_climateagent: "https://github.com/Relaxed-System-Lab/ClimateAgent"
code_climagent: "https://github.com/usail-hkust/ClimAgent"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 气候科学/政策 Agent：ClimateAgent + ClimateAgents（附录 ClimAgent）

> **定位**：气候科学智能体主题轴——补 [[天气气候基础模型]]「天气/气候 **foundation model**」之后仍缺的轴：**多代理编排做气候数据科学 / 社会—气候分析**。主锚两篇：**(A) ClimateAgent**（HKUST；气候数据获取→分析→报告的端到端编排）与 **(B) ClimateAgents**（HIT；社会—气候动力学的多智能体研究助手）。附录索引 **ClimAgent**（开放式气候建模 + ClimaBench）。
> **攻坚线**：**架构思想（主）**——角色分层 / 共享上下文 / API 自省与自纠；**评测字段（辅）**——工作流完成率、报告质量多维分、社会—气候案例与 Agentic Reviewer 文内分。
> **硬划界（开篇钉死）**：
> - **≠ [[天气气候基础模型]]**：禁止重写 Aurora / Earth-system FM 的 3D latent、预训练→多域微调、预报 rollout；本卡对象是 **LLM 多代理工作流**，不是格点地球场基础模型。
> - **≠ [[科研智能体]]**：禁止重写 The AI Scientist / ChemCrow 通史；ChemCrow 若出现仅作 ClimateAgent related work 一句邻接，不复述化学工具表。
> - **≠ ClimateGPT（2401.09646）**：专科气候 LLM 若点到，**仅作前置对照一句**，不升主、不拆架构。
> - **≠ [[智能体工具与长程任务]] / [[代码智能体Harness史线]]**：不写 MCP / SWE-bench harness 通史；AutoGen / Copilot 仅作文内对照槽。
> **禁止编造**：表数字、页数、完成率、GitHub 一律锚定官方 PDF（2026-09-22 CST）与 `ls -lh`；图柱未抽出标「待核实读图」；ClimateAgents 自称 GitHub 但**未给完整 URL**——本卡不臆造仓库地址。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主①** | *CLIMATEAGENT: Multi-Agent Orchestration for Complex Climate Data Science Workflows* | arXiv:**2511.20109v2** \[cs.LG\]（文首标 **14 Sep 2026**） | `https://arxiv.org/abs/2511.20109` | **4.2M**（4,340,473 B） | **49** letter | |
| **主②** | *ClimateAgents: A Multi-Agent Research Assistant for Social-Climate Dynamics Analysis* | arXiv:**2603.13840v1** \[cs.MA\]（文首标 **14 Mar 2026**）；Preprint. Under review. | `https://arxiv.org/abs/2603.13840` | **6.4M**（6,704,002 B） | **15** letter | |
| **附录** | *ClimAgent: LLM as Agents for Autonomous Open-ended Climate Science Analysis* | arXiv:**2604.16922v1** \[cs.AI\]（文首标 **18 Apr 2026**）；议程注明无版本后缀 `/pdf` 曾 404，故用 **v1** | `https://arxiv.org/abs/2604.16922` | **1.9M**（1,910,537 B） | **23** A4 | |

| 材料 | 作者 / 机构（文首） | 代码（文内明示） |
|---|---|---|
| ClimateAgent | Chenyue Li\*, Hyeonjae Kim\*, Wen Deng, Mengxi Jin, Wen Huang, Mengqian Lu, Binhang Yuan†（\*共一；†通讯）；The Hong Kong University of Science and Technology | https://github.com/Relaxed-System-Lab/ClimateAgent |
| ClimateAgents | Shan Shan；Department of Mathematics / International Center for Interdisciplinary Statistics，Harbin Institute of Technology；`shans@hit.edu.cn` | 文称「source code repository hosted on GitHub」——**未给出可点击完整 URL**（本卡不补造） |
| ClimAgent（附录） | Hao Wang¹, Jindong Han³, Wei Fan⁴, Hao Liu¹,²\*；HKUST(GZ) / HKUST / Shandong University / University of Auckland | https://github.com/usail-hkust/ClimAgent |

**体积判定**：ClimateAgent **4.2M**、ClimateAgents **6.4M**、ClimAgent **1.9M**，均 **<20MB** → 按验收规矩 ****。抽取同步： 与 。

**一句话抓手：**
- **ClimateAgent**：用户气候问题 → Orchestrate + Plan 分解 → Data-Agent（cdsapi / ecmwf-api 动态 introspect，m=8 候选脚本）→ Coding-Agent（自纠 Rmax=3）→ 报告；基准 **Climate-Agent-Bench-85**，文称 **100%** 任务完成、报告质量 **8.32**（vs Copilot **6.27** / GPT-5 **3.26**）。
- **ClimateAgents**：Minsky *Society of Mind* 灵感的三层（Perception / Reasoning / Operation）+ AutoGen 上 **11** 角色智能体；面向 UN / World Bank 等社会经济—气候指标的假设生成、相关/因果探索与情景；评测用 Stanford Agentic Reviewer 文内总体分 **6.4**。
- **ClimAgent（附录）**：Climate Environment（文称 **150** 工具 + **30** 数据库）支撑开放式物理建模四阶段；ClimaBench（文内任务数口径见 §六冲突说明）。

---

## 二、议题边界：只写「气候数据科学 / 社会—气候 Agent」，不写天气 FM / 科学 Agent 通史

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[天气气候基础模型]]** | 「气候/地球数据很大、异构」是动机邻接；ClimateAgent 用 ERA5/CDS 等**数据 API**，不是 Aurora 式场预报骨干 | 3D Perceiver/Swin、预训练小时数、多域微调表、Aurora 1.5 |
| **[[科研智能体]]** | ClimateAgent related work 点名 ChemCrow 作「科学协议自动化」邻接一句 | AI Scientist 三阶段 / ChemCrow 18 工具与双用途细节 |
| **ClimateGPT** | 若需交代「专科气候 LLM ≠ 编排 Agent」 | 任何 ClimateGPT 架构/训练/榜单升主 |
| **[[智能体工具与长程任务]] / [[代码智能体Harness史线]]** | 「LLM + 工具多步」抽象；ClimateAgents 文内点 OpenHands/SWE-Agent 作通用 agent 先例 | MCP 协议史、SWE-bench resolve 表 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| ClimateAgent 三层角色 + 持久上下文 $C_i$ + 自纠（多候选 / 迭代 / 语义校验） | 业务同化、数值天气预报作业流、订正 SLA |
| Climate-Agent-Bench-85 六域任务分层与报告四维分 | 未给出的「生产运维 KPI」外推 |
| ClimateAgents 三层 + Table 1 的 11 Agent 角色；社会指标—碳排放相关/因果管道 | 把 Agentic Reviewer **6.4** 升成跨文客观「可发表裁决」 |
| ClimAgent 附录：CE / 四阶段 / ClimaBench 文内主表数字 | 把附录升成与双主文对等的第三主锚 |

跟读口诀：

`
[[天气气候基础模型]] = 格点地球场怎么预训练成 FM —— 预报骨干
[[科研智能体]] = 通用科学发现 / 化学工具代理通史 —— 邻接一句即可
────────────────────────────────────────
本卡 A = 气候数据科学工作流怎么被多代理编排跑通（CDS/ECMWF → 报告）
本卡 B = 社会—气候动力学怎么被多代理助手探索（指标/政策/因果叙述）
附录 = 开放式物理建模 + ClimaBench（索引，不抢主）
`

---

## 三、ClimateAgent：气候数据科学端到端多代理编排

### 3.1 问题形式化（§3.1）

给定任务 $T$，系统经多阶段分析输出科学报告 $R$；持久工作流上下文：

$$
C_i=\{\mathrm{task}:T,\ \mathrm{plan}:P,\ \mathrm{code}:\{c_j\},\ \mathrm{data}:\{d_j\},\ \mathrm{results}:\{r_j\},\ \mathrm{logs}:\{l_j\}\}
$$
Plan-Agent 将 $T$ 分解为有序子任务 $P=[s_1,\ldots,s_n]$；专长 Agent $A_k$ 执行：$C_i=\mathrm{Execute}(C_{i-1},s_i,A_k)$。上下文同时充当：(1) 跨 Agent 通信协议；(2) 断点恢复检查点；(3) 可复现溯源记录。

### 3.2 三层架构与三大能力（§3.2–3.4，Fig.1 / Algorithm 1）

`
用户气候问题 T
 │
 ▼
Orchestrate-Agent ── 建实验目录 / 持久化上下文 / 调度
Plan-Agent ── 领域模式分解（climatology→anomalies→extremes→report 等）
 │
 ▼
Data-Agent(s) ── CDS(cdsapi) / ECMWF(ecmwf-api-client) 动态 introspect API
 生成 m=8 候选下载脚本，顺序尝试至成功
 │
 ▼
Coding-Agent(s) ── xarray/cartopy/cf-python 等；分析+可视化+报告
 迭代精炼至多 Rmax=3；每候选最多 5 次 debug；
 另有 LLM 语义校验（抓「跑得通但科学错」）
 │
 ▼
科学报告 R（文本 + 图）
`

文内三大能力标签：

| 能力 | 机制要点（文内） |
|---|---|
| **Coordinated Task Planning** | Plan 分解 + 专长委托；Orchestrate 管目录与全局进度 |
| **Contextual Coordination** | $C_i$ 单调累积；每子任务后 JSON 序列化；下游读上游制品 |
| **Adaptive Self-Correction** | Data：m=8 多候选；Coding：Rmax=3 + ≤5 debug；语义校验 |

### 3.3 基准 Climate-Agent-Bench-85（§4）

| 设计点 | 文内口径 |
|---|---|
| 规模 | **85** 真实工作流任务 |
| 六域 | AR 15 / DR 15 / EP 15 / HW 10 / SST 15 / TC 15 |
| 难度 | Easy **25**（30%）· Medium **30**（35%）· Hard **30**（35%；TempestExtremes / CDO 等外部工具） |
| 规格 | 自然语言目标 + 必用数据集/工具 + **严格输出契约**（文件名/格式）；含参考代码与人工报告 |
| 评测 | 报告 1–10 分四维：**Readability / Scientific Rigor / Completeness / Visual Quality**；GPT-4o 多模态 LLM-as-judge，对专家参考 |

### 3.4 主结果（§5，Table 1–2）——评测字段主表

**基线（文内）：** GPT-5 baseline（best-of-N，N=4，沙箱执行选首个成功）；GitHub Copilot Agent Mode。文称两基线底层同为 GPT-5，以隔离「多智能体编排 vs 单模型+执行校验」。

**Table 1 · 分域 Report Quality（1–10，全文任务平均）：**

| Domain | GPT-5 | Copilot | ClimateAgent |
|---|---:|---:|---:|
| Atmospheric River (AR) | 3.05 | 6.78 | **7.32** |
| Drought (DR) | 7.87 | 6.87 | **8.57** |
| Extreme Precipitation (EP) | 0.62 | 5.58 | **8.43** |
| Heatwave (HW) | 3.98 | 8.30 | **9.15** |
| Sea Surface Temperature (SST) | 4.28 | 8.10 | **8.88** |
| Tropical Cyclone (TC) | 0.00 | 2.65 | **7.85** |
| **All Tasks** | **3.26** | **6.27** | **8.32** |

**Table 2 · 四维拆解：**

| System | Readability | Sci. Rigor | Completeness | Visual Quality | Report Quality |
|---|---:|---:|---:|---:|---:|
| ClimateAgent | 8.40 | 8.72 | 7.75 | 8.41 | **8.32** |
| GPT-5 | 3.48 | 3.41 | 2.8 | 3.34 | 3.26 |
| Copilot | 6.68 | 6.89 | 5.62 | 5.87 | 6.27 |

摘要与 §1/§5 另主张：**100%** 任务完成（生成报告）。复杂域（EP/TC）基线崩塌、ClimateAgent 仍维持 >7.8 是文的核心叙事。

**基线失败模式消融（§5.4，Table 3；GPT-5 在 35 个失败任务上分类）：** Data/Array Shape or Key **9**（26%）· Data Request **6**（17%）· Syntax/Indentation **4** · Timeout **4** · Type **4** · Misc **8**。文用 Fig.3–6 对照展示索引形状、ERA5 日期串、语法括号、经度对齐等自纠前后差异（细节跟图，本卡不复述代码配方）。

**人机一致性（Appendix F，Table 8；\|s_expert − s_LLM\| 越小越好）：** AR **1.9167**（明显偏大）；DR **0.3250**；EP **0.5500**；HW **0.4250**；SST **0.4750**；TC **0.4750**。文解读：五域约 0.3–0.55，AR 可视化/空间诊断更易放大专家—裁判差。

### 3.5 跟读注意

- 文把「通用 LLM agent / 静态脚本」批为缺气候 API 语境与柔性；本卡接受为**该文主张**，不外推到一切科学 Agent。
- ChemCrow 仅出现在 related work，**不**因此把本卡并入 [[科研智能体]]。
- 「100% completion」指文内协议下报告生成成功；不等价于「科学结论全正确」——Completeness **7.75** 仍低于 Rigor **8.72**。

---

## 四、ClimateAgents：社会—气候动力学多代理研究助手

### 4.1 立轴（Abstract / §1）

相对「窄指标预测模型」，ClimateAgents 主张：**可解释、可适配的多智能体助手**，把多模态检索、统计建模、文本分析与自动化推理接到同一研究工作流——假设生成、数据分析、证据检索、结构化报告。数据叙事侧强调 **United Nations / World Bank**（及后文 IPCC）等社会经济—气候指标；政策锚点提及 **UN SDG 13**。

哲学资源：Marvin Minsky *The Society of Mind*——智能来自众多有限能力 Agent 的组织化交互，而非单体全知。

### 4.2 三层 + AutoGen 角色表（§3，Table 1）

**三层（文内）：**

| 层 | 职责 |
|---|---|
| **Perception** | 文本 / 表 / 图像 → 结构化表示 |
| **Reasoning** | 前沿 LLM：推断、规划、决策与协调 |
| **Operation** | 检索、统计分析、可视化等外部工具执行 |

**实现栈（文内）：** GPT-4 家族；**AutoGen**（UserProxyAgent / RetrieveAssistantAgent / MultimodalConversableAgent / AssistantAgent / GroupChatManager）；角色写在 system message。

**Table 1 · 11 Agents（编号与角色名照录）：**

| # | Agent | Role（文内摘要） |
|---|---|---|
| 1 | User | 发起任务、设目标、反馈 |
| 2 | Climate Strategist | 全局策略与外部工具（情景/建模平台） |
| 3 | Climate Scientist | 领域假设（碳汇、反馈环等） |
| 4 | Dialogue Manager | 消息流与轮转协调 |
| 5 | Policy Planner | 仿真式政策路径 |
| 6 | Critic | 可行性与气候对齐评审 |
| 7 | Data Modeler | 气候/环境数据统计洞察 |
| 8 | Code Developer | 处理与可视化脚本 |
| 9 | Plot Interpreter | 图解读 |
| 10 | Knowledge Retriever | 报告/数据库证据 |
| 11 | Fact Checker | 引用一致性与正确性校验 |

规划流：User → Climate Strategist → Policy Planner；Dialogue Manager 穿插；执行期 Climate Scientist / Data Modeler / Plot Interpreter / Knowledge Retriever / Fact Checker / Code Developer 协作。

### 4.3 结果叙事（§4）——案例型，非 Bench-85 式大表

| 小节 | 内容（文内） |
|---|---|
| Perception | Agent planner 对气候预测文献做主题聚类（模型族、区域/全球、公平、时间粒度、驱动因子、指标、预警 vs 长期政策等） |
| Reasoning · Correlation | 文献分类 → 特征相关矩阵 → SVR / 决策树等 → MAE/RMSE/R² → 政策解释模块 |
| Reasoning · Causation | 全连接因果图 → **CAM pruning**（跟 Rolland et al. score matching / additive noise 叙事）→ 专家校验；文强调 pruning **不替代**混杂控制 |
| Operation | 清洁燃料可及性（如 `EG.CFT.ACCS.RU.ZS` / `.UR.ZS`）与城市化（`SP.URB.TOTL.IN.ZS`）等指标上的多 Agent 问答示例（Fig.5） |

### 4.4 评测字段（§4.2）：Stanford Agentic Reviewer

七维：originality · importance · support of claims · soundness of experiments · clarity · value to community · contextualization。文内给出：

| 维度 | 分（文述） |
|---|---|
| originality / importance | **6** |
| support of claims / contextualization | **7** |
| clarity of writing | **8** |
| soundness of experiments | **5**（最低；文自承需更强实验验证） |
| **overall** | **6.4** |

注意：正文写「assessment of the report produced by **ClimateAgent**」——与题目 **ClimateAgents** 撞名，属文内笔误风险；本卡按 **ClimateAgents 论文的自审**理解，不把它并入 §三系统。Fig.6/7 柱/矩阵以读图为准，未抽出的细分标「待核实读图」。

### 4.5 局限（§5，文内）

依赖输入数据质量与代表性；全球碳排放/气候模型假设未必迁移到异质区域；任务特化导致跨域迁移需大改；「awareness / 道德因果」文自认当前模型未达。未来方向：本地化异构数据、教育/公卫/城市韧性垂直扩展、符号+仿真+伦理建模等——**仅索引，不展开操作手册**。

---

## 五、双主文对照（仅文内字段；不替选型拍板）

| 维度 | ClimateAgent（主①） | ClimateAgents（主②） |
|---|---|---|
| 问题框 | 气候**数据科学工作流**自动化（获取→处理→分析→报告） | **社会—气候**动力学探索与政策相关叙事 |
| 编排重心 | Orchestrate/Plan/Data/Coding + 持久 $C_i$ + API 自纠 | Perception/Reasoning/Operation + AutoGen 11 角色 |
| 数据接口 | CDS / ECMWF / ERA5 / TempestExtremes 等 | UN / World Bank / IPCC 报告与指标；清洁燃料与城市化示例 |
| 主评测 | Climate-Agent-Bench-85；报告四维 + 分域表；宣称 100% 完成 | Stanford Agentic Reviewer；overall **6.4**；案例图为主 |
| 骨干 LLM（文内） | 与 GPT-5 基线对照；裁判 GPT-4o | GPT-4 家族 |
| 代码 | 明确 GitHub URL | 「hosted on GitHub」无完整 URL |
| 与本仓库 | 对照 [[天气气候基础模型]]：用同一「气候数据」词，对象是 **Agent 编排** 非 FM | 对照 [[科研智能体]]：同属科学域 Agent，但介质是**社会指标/政策**，非 ML 模板或化学工具 |

选型跟读建议（仍非裁决）：若问题是「把一句气候分析需求变成 CDS 下载 + xarray 图 + 报告」，跟 **ClimateAgent** Bench-85；若问题是「社会经济指标与排放/政策的可解释多智能体探索」，跟 **ClimateAgents** 三层+角色表；若问题是「格点预报 FM」，回 **[[天气气候基础模型]]**。

---

## 六、附录索引：ClimAgent（不升主）

> 议程指定附录：开放式气候科学分析 Agent + ClimaBench；**禁止**与双主文对等展开。

| 字段 | 文内口径（锚定 PDF） |
|---|---|
| 目标 | 超越气候 Q&A，做数据驱动的开放式建模与报告 |
| Climate Environment (CE) | **150** specialized climate tools + **30** databases；自大量气候文献/子领域策展 |
| 四阶段 | Problem Analysis → Climate Modeling（知识检索 + 任务特化优化 / Critic 循环）→ Computational Solving → Solution Reporting |
| ClimaBench | 摘要贡献条写 **220** 题；§4.2 正文写 **320** tasks / 「scale of 320 tasks」——**文内口径冲突，并列照录，不擅自统一** |
| 五类任务（正文） | data query · concept analysis · predictive analysis · causal inference · policy making |
| 摘要增益主张 | 相对「original LLM solutions」**40.21%** improvement（solution rigorousness and practicality）——**摘要句**；细节跟主表 |
| Table 1（节选，GPT-4o 骨干，Overall） | 2000–2024：ClimAgent **8.92** vs GPT-4o **6.29** / DS-Agent **7.91** / ResearchAgent **7.79** / Agent Laboratory **7.35** / DeepAnalyze **7.34**；2025：ClimAgent **8.47** vs GPT-4o **6.55** 等（全文见抽取） |
| 评测四维 | AE · SC · PS · RBA（Analysis Evaluation / Solution Correction / Practicality and Scientificity / Result and Bias Analysis） |
| 代码 | https://github.com/usail-hkust/ClimAgent |

与双主文差一刀：ClimAgent 强调 **物理方程/工具检索的开放式建模**；ClimateAgent 强调 **业务气候 API 工作流鲁棒编排**；ClimateAgents 强调 **社会指标—政策多智能体**。三者不可互相替代。

---

## 七、可复核清单与已知缺口

**可复核：**
1. 本地体积：`ls -lh https://arxiv.org/abs/2511.20109 https://arxiv.org/abs/2603.13840 https://arxiv.org/abs/2604.16922` → **4.2M / 6.4M / 1.9M**。
2. 页数：**49 / 15 / 23**。
3. ClimateAgent Table 1/2、Table 3、Table 8 与 一致；摘要 8.32 / 6.27 / 3.26 / 100% 一致。
4. ClimateAgents Table 1 十一角色；Agentic Reviewer overall **6.4**、soundness **5** 与抽取一致。
5. ClimAgent CE「150 tools / 30 databases」、GitHub `usail-hkust/ClimAgent`、Table 1 Overall 数字与抽取一致。

**缺口 / 勿编造：**
- ClimateAgents **无**文内完整自有 GitHub URL——禁止补造。
- ClimAgent **220 vs 320** 任务数冲突未在文内消解——禁止选边「纠正」。
- 40.21% 仅摘要出现；未在本抽取中还原为 Table 1 的显式算术——引用时标「摘要主张」。
- ClimateAgents §4.2 误写「ClimateAgent」——标笔误风险，不合并系统。
- 禁止把 [[天气气候基础模型]] Aurora 参数量/技巧写进本卡；禁止把 [[科研智能体]] 成本 <$15/篇 等数字挪来。
- ClimateGPT 未下载、不升主。

---

## 八、与 Wave9 agenda 的对齐句

Agenda [[气候科学Agent]]：「[[天气气候基础模型]] 立的是天气/气候基础模型；缺『多代理编排做气候数据科学 / 社会—气候分析』轴。ClimateAgent（2511.20109）与 ClimateAgents（2603.13840）可核；≠ [[科研智能体]] 通史；≠ ClimateGPT 升主；ClimAgent（2604.16922v1）附录。」本卡交付即该缺口：双主文架构+评测字段钉死，附录索引，划界开篇钉死，PDF 体积可入库。

*2026-09-22 CST。体积：`ls -lh` 同日核对。*
