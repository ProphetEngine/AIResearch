---
title: "生产级 Agent Memory 层：Mem0 + Zep（≠ MemGPT/A-Mem/Memory-R1）"
topic: Mem0与Zep生产级记忆
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2504.19413
 - https://arxiv.org/abs/2501.13956
arxiv: ["2504.19413", "2501.13956"]
related:
 - "Harness/记忆/智能体长程记忆.md"
 - "Harness/记忆/MemoryR1强化学习记忆维护.md"
 - "检索与知识/图谱检索GraphRAG.md"
 - "检索与知识/检索增强与知识外挂.md"
code_mem0: "https://mem0.ai/research"
code_graphiti: "https://github.com/getzep/graphiti"
product_zep: "https://www.getzep.com"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 生产级 Agent Memory 层：Mem0 + Zep（≠ MemGPT / A-Mem / Memory-R1）

> **主题**：两篇近窗**生产记忆层**系统论文——**Mem0**（可扩展长程记忆抽取–更新–检索；含图变体 Mem0<sup>g</sup>）与 **Zep**（Graphiti 时序知识图记忆服务）。二者是「把对话事实变成可部署记忆 API」的主流入口，而非再做一套研究原型隐喻。
> **读者向范围**：架构思想为主——抽取 / 更新 / 图分层 / 双时间轴；评测字段为辅——LOCOMO / DMR / LongMemEval 文内对照表，不外推未测场景。
> **范围外参见**：
> - MemGPT 主/档案上下文分页、A-Mem Zettelkasten 卡片链接演化 → 「智能体长程记忆」；本文若点到二者，仅作「基线 / related」一句。
> - Memory-R1 在 `{ADD, UPDATE, DELETE, NOOP}` 上的 RL / 双 agent 蒸馏 → 「MemoryR1强化学习记忆维护」；Mem0 本文的四操作是 **LLM tool-call 启发式**，不是 RL 策略学习。
> - 稠密检索 / DPR / 向量库产品通史 → 「检索增强与知识外挂」；RAG 仅作 Mem0 文内 chunk×k 对照槽。
> - Microsoft GraphRAG **文档语料**社区摘要 + map-reduce 全局问答 → 「图谱检索GraphRAG」；Zep 虽引用 GraphRAG 作 community 灵感，对象是 **agent 对话/业务记忆的时序 KG**，不是文档库 QFS。
> **材料口径**：表数字、延迟、token、准确率一律锚定官方 PDF（检索截止 2026-09-22）。Mem0 文对 Zep「构建延迟 / 图 token 膨胀」的批评、Zep 文对 MemGPT/DMR 的批评，均标为**该文主张**，不升为跨文客观裁决。

---

## 一、材料元信息

| 角色 | 题名 / 版本 | 标识（HTTPS） | 页数 |
|---|---|---|---|
| **主①** | *Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory*；arXiv **2504.19413v1** \[cs.CL\]（**28 Apr 2025**） | https://arxiv.org/abs/2504.19413 | **23** |
| **主②** | *Zep: A Temporal Knowledge Graph Architecture for Agent Memory*；arXiv **2501.13956v1** \[cs.CL\]（**20 Jan 2025**） | https://arxiv.org/abs/2501.13956 | **12** |

| 材料 | 作者 / 机构（文首） | 代码 / 产品（文内明示） |
|---|---|---|
| Mem0 | Chhikara, Khant, Aryan, Singh, Yadav（`research@mem0.ai`） | https://mem0.ai/research ；图库实现写明 **Neo4j** |
| Zep | Rasmussen, Paliychuk, Beauvais, Ryan, Chalef（Zep AI） | 产品 https://www.getzep.com ；引擎 **Graphiti** https://github.com/getzep/graphiti ；图检索侧写明 **Neo4j**（含 Lucene） |

PDF 体积约 **1.1 MB**（Mem0）/ **146 KB**（Zep）。

**一句话抓手：**
- **Mem0**：会话对 → 异步摘要 + 近窗 → LLM 抽候选事实 → 对 top-s 相似记忆做 **ADD / UPDATE / DELETE / NOOP** tool-call；Mem0<sup>g</sup> 再叠实体–关系有向标注图。
- **Zep / Graphiti**：episode / entity / community **三层时序 KG** + 双时间轴（事件序 $T$ / 事务序 $T'$）+ 边失效；检索 = 搜索 → 重排 → 构造上下文字符串。

---

## 二、议题边界：只写「生产记忆层」，不写分页 OS / RL 四操作 / 文档 GraphRAG

### 2.1 与相关笔记的分工

| 相关笔记 | 本文只取 | 本文不写 |
|---|---|---|
| 智能体长程记忆 | MemGPT / A-Mem 是「记忆要外置」的前序系统论文；Mem0 表内把二者当 LOCOMO 旧基线 | MemGPT 主上下文压力告警与分页函数；A-Mem 笔记构造 / 链接 / 演化全文 |
| MemoryR1强化学习记忆维护 | Memory-R1 把 Mem0 式四操作当作 **动作面出处**，再用下游答对做 RL | GRPO / Memory Manager–Answer Agent / 蒸馏训练曲线 |
| 检索增强与知识外挂 | 「长对话当文档切块检索」是 Mem0 Table 2 的对照轴 | 稠密双塔 / 向量库选型通史 |
| 图谱检索GraphRAG | Zep community 层「受 GraphRAG 启发」一句；检索方法论与 map-reduce **不同**（Zep §2.3 自述） | Leiden 社区摘要 + 全局 QFS map-reduce 全文 |

### 2.2 本文主轴 vs 禁区

| 写 | 不写 |
|---|---|
| Mem0 抽取–更新双阶段与四操作 **tool-call**（启发式 LLM） | Memory-R1 式策略梯度 / 奖励设计 |
| Mem0<sup>g</sup> 实体–关系图 + 双路检索（实体中心 / 三元组语义） | A-Mem 卡片盒演化算法 |
| Zep Graphiti 三层图、双时间轴、边失效、search–rerank–constructor | MemGPT OS 虚拟上下文管理 |
| 文内 LOCOMO / DMR / LongMemEval 数字 | 未给出的「生产 SLA / 客户实测」外推 |
| 两文互相对照时的 **主张差异**（Mem0 §4.5 批 Zep 图体积；Zep 批 DMR 过易） | 替某方「打赢生产选型」裁决 |

**层次说明（无工号）：**
- 「智能体长程记忆」回答记忆放哪（分页 OS / 卡片网）——研究隐喻；
- 「MemoryR1」回答四操作怎么学（RL）——策略层；
- 本文回答生产记忆层怎么抽、怎么图、怎么评（Mem0 / Zep）——系统层；
- 「图谱检索GraphRAG」回答文档语料全局问答——不是对话时序记忆。

---

## 三、Mem0：抽取–更新记忆层（含 Mem0<sup>g</sup>）

### 3.1 动机与产品定位

文首问题（§1 / Fig.1）：固定上下文窗口下，跨会话偏好（如素食、无乳）易丢；单纯加长窗口只是推迟溢出，且长上下文注意力对「夹在无关长段中的关键偏好」并不稳健。Mem0 自称面向 **production-ready** agent：动态提取、合并、检索显著信息；并给出图增强变体 Mem0<sup>g</sup>（正文上标 $g$，抽取文本常写作 `Mem0g`）。

### 3.2 Mem0 双阶段流水线（§2.1 / Fig.2）

| 阶段 | 输入 | 做什么 |
|---|---|---|
| **Extraction** | 新消息对 $(m_{t-1}, m_t)$ + 会话摘要 $S$ + 近窗 $\{m_{t-m},\ldots,m_{t-2}\}$ | LLM 抽取函数 $\phi(P)$ 产出候选事实集 $\Omega=\{\omega_i\}$ |
| **Update** | 每个 $\omega_i$ + 向量库 top-$s$ 相似既有记忆 | LLM **tool-call** 在四操作中选一并写回库 |

四操作（文内定义；**≠ Memory-R1 的 RL 学法**）：

| 操作 | 语义 |
|---|---|
| **ADD** | 无语义等价记忆 → 新建 |
| **UPDATE** | 用互补信息增强既有记忆 |
| **DELETE** | 新信息与既有矛盾 → 删除 |
| **NOOP** | 无需改库 |

实验默认（§2.1 末）：$m=10$，$s=10$；抽取/更新 LLM = **GPT-4o-mini**；向量侧用 dense embedding。摘要模块**异步**刷新，避免阻塞主路径。

### 3.3 Mem0<sup>g</sup>：图记忆（§2.2 / Fig.3）

记忆表示为有向标注图 $G=(V,E,L)$：节点=实体（类型 + embedding + 创建时间戳），边=关系三元组 $(v_s,r,v_d)$。

| 子模块 | 作用 |
|---|---|
| Entity extractor | 从对话抽关键实体与类型 |
| Relationship generator | 产关系三元组（显式/隐式） |
| 入库 | 按实体 embedding 相似度阈值 $t$ 决定新建/复用节点，再挂边 |
| Conflict / update resolver | LLM 判冲突；**失效标记**而非物理删除 → 支持时序推理 |
| 检索双路 | **Entity-centric**：锚实体扩邻接子图；**Semantic triplet**：整查询 embedding vs 三元组文本，超阈值返回 |

实现：图库 **Neo4j**；抽取/更新同样 GPT-4o-mini + function calling。

### 3.4 评测设定：LOCOMO（§3）

| 字段 | 文内取值 |
|---|---|
| 数据 | LOCOMO：约 **10** 段长对话；每段约 **600** 轮、**26k** tokens；平均约 **200** 题 |
| 题型 | single-hop / multi-hop / temporal / open-domain（**去掉** adversarial：无 ground truth） |
| 质量指标 | F1、BLEU-1、**LLM-as-a-Judge (J)**（10 次均值 ±1 std；理由：词面指标对事实错误不敏感） |
| 部署指标 | 检索上下文 **token**（`cl100k_base`）；search latency 与 total latency 的 **p50 / p95** |
| 基线族 | LOCOMO 旧系（含 MemGPT、A-Mem）；LangMem；RAG（chunk 128–8192 × $k\in\{1,2\}$）；full-context；OpenAI ChatGPT memory；**Zep 平台版** |

> 接口提醒：表内 MemGPT / A-Mem **只作数字对照** → 机制细节见「智能体长程记忆」。

### 3.5 LOCOMO 主结果（Table 1 / Table 2；仅文内数字）

**分题型 J（Table 1，节选）：**

| Method | Single-hop J | Multi-hop J | Open-domain J | Temporal J |
|---|---|---|---|---|
| A-Mem* | 39.79±0.38 | 18.85±0.31 | 54.05±0.22 | 49.91±0.31 |
| LangMem | 62.23±0.75 | 47.92±0.47 | 71.12±0.20 | 23.43±0.39 |
| Zep | 61.70±0.32 | 41.35±0.48 | **76.60±0.13** | 49.31±0.50 |
| OpenAI | 63.79±0.46 | 42.92±0.63 | 62.29±0.12 | 21.71±0.20 |
| **Mem0** | **67.13±0.65** | **51.15±0.31** | 72.93±0.11 | 55.51±0.34 |
| **Mem0<sup>g</sup>** | 65.71±0.45 | 47.19±0.67 | 75.71±0.21 | **58.13±0.44** |

文内解读要点（§4.1–4.2，跟读勿改写）：
- 单跳 / 多跳：稠密自然语言记忆 **Mem0** 更强；图结构对「单轮事实」增益有限，多跳上 Mem0<sup>g</sup> 甚至略逊。
- 时序：Mem0<sup>g</sup> 最高 J；OpenAI memory 因多数记忆缺时间戳而崩。
- 开放域：同台 **Zep** 以 J=76.60 略胜 Mem0<sup>g</sup>（75.71）。

**Overall J + 延迟 + 检索 token（Table 2）：**

| Method | memory/chunk tokens | Search p50/p95 (s) | Total p50/p95 (s) | Overall J |
|---|---|---|---|---|
| Full-context | 26031 | — | 9.870 / **17.117** | 72.90±0.19% |
| A-Mem | 2520 | 0.668 / 1.485 | 1.410 / 4.374 | 48.38±0.15% |
| LangMem | 127 | 17.99 / 59.82 | 18.53 / 60.40 | 58.10±0.21% |
| Zep | 3911 | 0.513 / 0.778 | 1.292 / 2.926 | 65.99±0.16% |
| OpenAI | 4437 | — | 0.466 / 0.889 | 52.90±0.14% |
| **Mem0** | **1764** | **0.148 / 0.200** | **0.708 / 1.440** | **66.88±0.15%** |
| **Mem0<sup>g</sup>** | 3616 | 0.476 / 0.657 | 1.091 / 2.590 | **68.44±0.17%** |

与摘要口号对齐（用 Table 2 验算，不另造）：
- Mem0 vs OpenAI Overall J：$(66.88-52.90)/52.90\approx$ **+26%** 相对提升。
- Mem0<sup>g</sup> vs Mem0 Overall J：$68.44$ vs $66.88$ ≈ **+2%** 相对。
- Mem0 total p95 vs full-context：$(17.117-1.440)/17.117\approx$ **91%** 降幅；检索上下文相对 26k 亦 **>90%** token 节省。
- 但 full-context 仍有最高 Overall J（~73%），代价是尾延迟 ~17s——文强调的是 **精度–延迟–成本** 折中，不是「全面碾压全上下文」。

### 3.6 Mem0 文对 Zep 的系统侧批评（§4.5；标为该文主张）

| 主张（Mem0 §4.5） | 数字 |
|---|---|
| 物化记忆平均 token | Mem0 ~**7k** / 对话；Mem0<sup>g</sup> ~**14k**；Zep 图 **>600k**（节点摘要 + 边事实冗余） |
| 构建可用性 | 称 Zep 写入后立刻检索常失败，数小时后再查变好 → 异步多 LLM / 后台构图；Mem0 图构建「最坏情况仍 **<1 分钟**」 |

→ 跟读时当作 **Mem0 同台实验观察**，与 Zep 本文自称「生产系统、重延迟」可并存；本文不替某方结案。

---

## 四、Zep：Graphiti 时序知识图记忆层

### 4.1 定位：动态记忆服务，而非静态文档 RAG

摘要 / §1：现有 agent RAG 多面向**静态语料**；企业场景需要持续写入对话 + 业务结构化数据。Zep 以 **Graphiti** 为核：时序感知动态 KG，非损失地保留事实有效期；对标评测用 MemGPT 的 **DMR**，并加更难的 **LongMemEval**（企业向）。

> 接口：文中对比 MemGPT **只取 DMR 分数** → 分页机制见「智能体长程记忆」。GraphRAG 引用只解释 community 灵感 → 文档 GraphRAG 见「图谱检索GraphRAG」。

### 4.2 三层子图（§2）

形式化：$G=(N,E,\phi)$，$\phi:E\to N\times N$。

| 层 | 内容 | 作用 |
|---|---|---|
| **Episode** $G_e$ | 原始消息 / 文本 / JSON 节点；边连到语义实体 | **非损失**原料仓；可回指引用 |
| **Semantic entity** $G_s$ | 实体节点 + 实体间语义边（事实） | 解析、消歧、关系 |
| **Community** $G_c$ | 强连通实体簇 + 高层摘要；边连成员实体 | 全局主题视图（灵感来自 GraphRAG，但检索 **不是** map-reduce） |

认知隐喻：episodic vs semantic memory；社区层对齐「全局理解」。

### 4.3 双时间轴与边失效（§2.1 / §2.2.3）——相对文档 GraphRAG 的关键差分

| 时间轴 | 含义 |
|---|---|
| $T$ | 事件/事实在世界中的**有效序**（$t_{\mathrm{valid}}, t_{\mathrm{invalid}}$） |
| $T'$ | 系统**摄入事务序**（$t'_{\mathrm{created}}, t'_{\mathrm{expired}}$；审计） |

消息带参考时间戳 $t_{\mathrm{ref}}$，用于解析「下周四 / 两周前」等相对时间。新边可令旧边失效：LLM 比对新旧语义边；若时间重叠矛盾，将旧边 $t_{\mathrm{invalid}}$ 设为新边 $t_{\mathrm{valid}}$；事务序上**优先新信息**。

实体当前消息 + 近 $n=4$ 条上下文；说话人自动为实体；embedding **1024** 维 + 全文检索候选 → LLM 实体消解；写库用**预写 Cypher**（非 LLM 生成查询）降幻觉。事实边在同实体对之间做去重；支持多实体事实的 hyper-edge 式建模。

Community：用 **label propagation**（非 Leiden），便于新节点动态挂到邻居多数社区并更新摘要；承认与全量传播结果会渐偏，需周期性刷新。

### 4.4 检索管线：$f=\chi\circ\rho\circ\phi$（§3）

| 步 | 符号 | 内容 |
|---|---|---|
| Search | $\phi$ | $\phi_{\cos}$ + $\phi_{\mathrm{BM25}}$ + $\phi_{\mathrm{bfs}}$（Neo4j Lucene）；对象字段：边 fact / 实体名 / 社区名 |
| Rerank | $\rho$ | RRF、MMR、episode-mention 频次、节点距离、cross-encoder（最贵） |
| Constructor | $\chi$ | 把边事实（含有效期）+ 实体摘要 + 社区摘要格式化为上下文字符串 $\beta$ |

实验默认：检索 top **20** 边与实体节点再格式化（§4 开篇）；DMR 描述另写 top **10** nodes/edges（§4.2）——跟读时按节保留，不强行合并。

### 4.5 评测：DMR + LongMemEval（§4）

**模型配置（§4.1）：** embedding/rerank = **BGE-m3**；构图 gpt-4o-mini-2024-07-18；作答 gpt-4o-mini / gpt-4o；DMR 对齐 MemGPT 时另用 gpt-4-turbo-2024-04-09。

**Table 1 · DMR（500 段多会话；MemGPT 主指标）：**

| Memory | Model | Score |
|---|---|---|
| Recursive Summarization† | gpt-4-turbo | 35.3% |
| MemGPT† | gpt-4-turbo | 93.4% |
| Full-conversation | gpt-4-turbo | 94.4% |
| **Zep** | gpt-4-turbo | **94.8%** |
| Full-conversation | gpt-4o-mini | 98.0% |
| **Zep** | gpt-4o-mini | **98.2%** |

† 取自 MemGPT 原文报告。文自评：DMR 对话仅 ~60 条消息、题型偏单跳事实检索，**全上下文已接近饱和** → 不足以区分企业记忆系统。

**Table 2 · LongMemEvals（均长 ~115k tokens）：**

| Memory | Model | Score | Latency | Avg Context Tokens |
|---|---|---|---|---|
| Full-context | gpt-4o-mini | 55.4% | 31.3 s | 115k |
| **Zep** | gpt-4o-mini | **63.8%** | **3.20 s** | **1.6k** |
| Full-context | gpt-4o | 60.2% | 28.9 s | 115k |
| **Zep** | gpt-4o | **71.2%** | **2.58 s** | **1.6k** |

摘要口径：准确率提升最高约 **18.5%**（gpt-4o：60.2→71.2）；延迟约 **90%** 降幅（数量级：28.9s→2.58s）。上下文从 115k → 1.6k。

**Table 3 · 题型差分（节选，文内 Delta）：** preference / temporal / multi-session 等大幅上升；**single-session-assistant** 反而下降（gpt-4o −17.7%，gpt-4o-mini −9.06%）——文承认需继续工程。MemGPT 在 LongMemEval 上因无法直接摄入历史消息而**未能成功同台**（§4.3.1）。

实验环境备注（§4.3）：2024-12～2025-01，波士顿住宅网连 AWS us-west-2 上的 Zep 服务 → Zep 延迟含跨网，基线全上下文无此开销。

---

## 五、两系统对照（仅文内字段；不替选型拍板）

| 维度 | Mem0 / Mem0<sup>g</sup> | Zep / Graphiti |
|---|---|---|
| 主数据结构 | 自然语言事实库 +（可选）实体–关系图 | Episode / Entity / Community **三层时序 KG** |
| 更新原语 | ADD/UPDATE/DELETE/NOOP（LLM tool-call） | 边创建 + **双时间轴失效**；社区动态 label propagation |
| 默认推理 LLM（文内） | GPT-4o-mini | gpt-4o-mini 构图；作答含 gpt-4o / gpt-4-turbo |
| 图库 | Neo4j（Mem0<sup>g</sup>） | Neo4j + Lucene |
| 主基准 | **LOCOMO**（质量 + p50/p95 + token） | **DMR** + **LongMemEval**（准确率 + 延迟 + 上下文 token） |
| 文内交叉 | Table 1/2 把 Zep 当基线；§4.5 批 Zep 图 token 与异步延迟 | 摘要/DMR 对标 MemGPT；未在 LongMemEval 成功跑通 MemGPT |
| 与本仓库其他笔记 | 四操作面 → 被 Memory-R1 笔记引用为 RL 动作集出处 | community 灵感 → GraphRAG 笔记；MemGPT 分数 → 长程记忆笔记 |

选型跟读建议（仍非裁决）：若问题框是 **LOCOMO 式多跳对话事实 + 低 p95 检索延迟**，跟 Mem0 Table 2；若问题框是 **~100k+ token 长会话 + 时序/跨会话偏好 + 事实有效期**，跟 Zep LongMemEval；若问题框是 **文档库全局主题问答**，回「图谱检索GraphRAG」，不要用本篇硬套。

---

## 六、可复核清单与已知缺口

**可复核：**
1. 官方 PDF：https://arxiv.org/abs/2504.19413 、https://arxiv.org/abs/2501.13956 ；体积约 **1.1 MB / 146 KB**。
2. 页数：**23 / 12**。
3. Mem0 Table 1/2、Zep Table 1/2/3 数字与原文一致。
4. 摘要「26% / 2% / 91% / >90% token」与 Table 2 算术一致。

**缺口 / 勿外推：**
- 两文均未给出可复现的公开「客户生产 SLA」曲线；Mem0 §4.5 与 Zep 延迟测量条件不同，**不可直接比绝对秒数决胜负**。
- Zep 称可合成 **structured business data**，但本文实验主轴仍是对话记忆；业务 JSON 摄入效果**无同台数字**。
- Mem0 代码入口给的是 https://mem0.ai/research ；具体开源 commit / SDK API 面本篇不跟。
- 不把 Memory-R1 的 RL 增益写进本篇「Mem0 系统能力」。

---

## 七、收束

本文补齐 Mem0 系统论文与 Zep 时序知识图记忆的独立跟读：生产记忆层双主文，范围划清，评测字段锚定 PDF。
