---
title: "Graph RAG 增量：GraphRAG 经典 + EraRAG（相对 B6）"
topic: 图谱检索GraphRAG
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
sources:
 - https://arxiv.org/abs/2404.16130
 - https://arxiv.org/abs/2506.20963
arxiv: ["2404.16130", "2506.20963"]
related: ["B6", "智能体长程记忆", "MemoryR1强化学习记忆维护", "长上下文位置编码与系统侧"]
archived: 2026-09-22
---

# Graph RAG 增量：GraphRAG 经典 + EraRAG（相对 B6）

> **定位**：[[图谱检索GraphRAG]] P1——相对 `B6` 的 **图谱社区摘要查询 + 语料增长时的增量索引** 专篇。B6 已立 Lewis 式「检索–生成 / 稠密向量索引 / 热换整库」主轴；本篇只补两块缺口：**(1) Microsoft GraphRAG**——实体图谱 → Leiden 社区 → 社区摘要 → map-reduce 全局问答（面向 *global sensemaking*）；**(2) EraRAG**——超平面 LSH 多层图 + **选择性重分段/重摘要**，避免每次增量全量重建。
> **攻坚线**：**架构思想（主）**——社区层次摘要与全局 map-reduce；**AI Infra（辅）**——增长语料下的局部更新复杂度与 token/时间开销。
> **硬划界（禁止重写）**：
> - **禁止重写** `B6` 的稠密检索 / DPR 双塔 / MIPS / 重排通史、RAG-Token vs RAG-Sequence、向量库产品对照。本篇只用「**向量 RAG 对全局主题问句失败**」这一对照槽位。
> - **禁止重写** [[长上下文位置编码与系统侧]] 长上下文窗口外推；本篇是 **库外图索引**，不是把整库塞进上下文。
> - **禁止重写** [[智能体长程记忆]] MemGPT / A-Mem 分层记忆全文；与 [[MemoryR1强化学习记忆维护]] Memory-R1 并列互补（结构图索引 vs RL 维护记忆银行），本篇不写 ADD/UPDATE/DELETE 策略。
> **禁止编造**：机制、表数字、win rate、复杂度一律锚定官方 PDF（2026-09-22 CST）。图内未抽出的精确曲线点标 **待核实读图**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文·经典** | Edge, Trinh, Cheng, Bradley, Chao, Mody, Truitt, Metropolitansky, Ness & Larson (Microsoft), *From Local to Global: A GraphRAG Approach to Query-Focused Summarization* | arXiv:**2404.16130v2** \[cs.CL\] **19 Feb 2025**；`https://arxiv.org/abs/2404.16130`（**26** 页 letter；CreationDate **2025-02-20** CST；6,893,854 bytes） | 实体 KG + Leiden 社区摘要 + map-reduce 全局答；相对向量 RAG 的 comprehensiveness / diversity |
| **主文·增量** | Zhang, Huang, Zhou et al., *EraRAG: Efficient and Incremental Retrieval Augmented Generation for Growing Corpora* | arXiv:**2506.20963v2** \[cs.IR\] **4 Jul 2025**；`https://arxiv.org/abs/2506.20963`（**14** 页；Title 与作者元数据完整；1,792,984 bytes） | 超平面 LSH 多层图；merge/split + 向上传播的选择性更新；相对 GraphRAG/RAPTOR/HippoRAG 的重建成本 |
| **辅·代码** | GraphRAG：`https://github.com/microsoft/graphrag`；EraRAG：`https://github.com/EverM0re/EraRAG-Official`（摘要自报） | 复现入口；本笔记不展开仓库提交史 | |

**一句话抓手：**
- **GraphRAG**：把「整库主题问句」（QFS / global sensemaking）变成 **预计算社区摘要上的 map-reduce**，而非 top-k 块检索。
- **EraRAG**：承认 Graph-RAG 系在 **增长语料** 上常被迫全量重建；用 **固定超平面 LSH + $S_{\min}/S_{\max}$** 把更新收成 **受影响桶向上传播**，摘要称相对既有 Graph-RAG 可 **省至约 95% 构建时间与 token**（Abstract / Fig.1 文案；细表见 §五）。

---

## 二、议题边界：相对 B6 只取接口

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **B6 Lewis RAG** | 「库外非参数记忆 + 条件生成」；向量 RAG 擅长 **局部可定位** 事实问 | DPR/MIPS 细节、RAG-Token/Sequence、稠密–稀疏混合、rerank 级联通史 |
| **B6「Graph RAG 名录待核实」** | 本篇用两篇一手 PDF **填上**该待核实槽 | 不另编造产品清单或未核论文 |
| **[[长上下文位置编码与系统侧]] 长上下文** | 窗口装不下整库 → 需要外挂 | YaRN / 稀疏注意力 / lost-in-middle |
| **[[智能体长程记忆]] / [[MemoryR1强化学习记忆维护]]** | 「结构记忆要可维护」的工程直觉 | MemGPT 分页、Memory-R1 动作空间 |

### 2.2 问题立轴（跟读）

`
B6 向量 RAG：query → top-k 相似块 → 生成
 ✗ 对「整库主旨 / 趋势 / 主题」类问句：没有「该检索哪几块」的局部锚点

GraphRAG： 文档 → 实体/关系图 → Leiden 社区层次 → 预生成社区摘要
 query →（选定社区层级）对社区摘要做 map 局部答 → reduce 全局答

EraRAG： 承认上路线索图在「每天新增语料」时重建成本墙
 固定超平面 LSH 分桶 + 尺寸闸门 → 新块只扰动局部桶，向上重摘要
`

GraphRAG Abstract 原话要点：RAG 在「What are the main themes in the dataset?」这类 **指向整库** 的问题上失败，因为那是 **query-focused summarization (QFS)** 而非显式检索；先验 QFS 又难扩到典型 RAG 索引规模。GraphRAG 要同时随 **问题泛化度** 与 **源文本量** 缩放。

EraRAG Abstract 原话要点：既有 Graph-RAG 常假设 **静态语料**，新文档到来就要昂贵的 **full-graph reconstruction**；目标是动态环境下仍保持检索精度与低延迟。

---

## 三、GraphRAG：图谱社区摘要 → 全局问答

### 3.1 流水线总览（Fig.1 / §3.1）

索引时（Indexing Time）与查询时（Query Time）分离：

`
Source Documents
 → text extraction & chunking → Text Chunks
 → domain-tailored entity/rel/claim 提取 → Entities & Relationships
 → 聚合为图（节点/边/协变量 claims） → Knowledge Graph
 → community detection（文内用 Leiden） → Graph Communities
 → domain-tailored 社区摘要 → Community Summaries
查询时：
 Community Summaries → query-focused 社区答案（map）
 → query-focused 全局答案（reduce）
`

图索引跨 **nodes（实体）**、**edges（关系）**、**covariates（claims）**；LLM prompt 可按领域定制 few-shot。

### 3.2 建索引五步（跟读）

| 步 | 节 | 要点（文内） |
|---|---|---|
| 1 | §3.1.1 | 文档切块。块越长 → 抽取 LLM 调用越少（省钱），但对块前部信息 **recall 下降**（引 Kuratov / Liu）；权衡见 Appendix A.1 |
| 2 | §3.1.2 | 从块中抽 **实体、关系** 及短描述；可选 **claims**（关于实体的可核事实：日期、事件、交互）。默认「named entities」；科学/医学/法律等可用领域 few-shot |
| 3 | §3.1.3 | 多实例聚合为节点/边；关系重复次数作 **边权**；实体匹配文内用 **exact string matching**（可换更软匹配）；重复实体后续社区摘要阶段通常会被聚在一起 |
| 4 | §3.1.4 | **Leiden**（Traag et al., 2019）层次社区：在社区内递归再检测，直到叶社区。每一层给出 **互斥且穷尽** 的节点划分 → 便于分治全局摘要。实现：`graspologic` |
| 5 | §3.1.5 | 生成 **report-like** 社区摘要：叶社区按边两端节点度排序，迭代塞入上下文；高层社区装不下时用 **子社区摘要** 替换更长的元素摘要 |

### 3.3 查询：社区摘要上的 map-reduce（§3.1.6）

对选定社区层级：

1. **Prepare**：社区摘要 **随机打乱** 后按预定 token 切块（避免相关信息挤在同一窗口丢失）。
2. **Map**：并行生成中间答案；LLM 同时打 **0–100 helpfulness**；**score=0 过滤**。
3. **Reduce**：中间答案按分数降序填入新上下文至 token 上限 → 生成返回用户的 **global answer**。

层级条件（评测用，§4.1.2）：

| 条件 | 含义 |
|---|---|
| **C0** | 根层社区摘要（数量最少） |
| **C1–C3** | 逐级更细；若无子社区则向下投影父层 |
| **TS** | 同一 map-reduce，但对象是 **源文本块**（无图索引） |
| **SS** | 向量 RAG：块检索填满上下文窗口上限 |

### 3.4 评测设计：自适应全局问句 + LLM-as-judge（§3.2–3.3）

- **问句生成（Algorithm 1）**：由语料用途描述 → $K$ 用户画像 → 每用户 $N$ 任务 → 每 (用户,任务) $M$ 条 **需整库理解、勿依赖低层事实检索** 的问句。评测取 $K=M=N=5$ → **每库 125** 题。
- **判据**：Comprehensiveness（覆盖面细节）、Diversity（视角丰富）、Empowerment（助读者知情判断）；另加对照 **Directness**（向量 RAG 理应更「直给」）。
- **数据**：约 **百万 token** 量级——Podcast（Behind the Tech，~1M tokens）、News（2013-09 起新闻，~1.7M tokens）。
- **配置**：社区摘要/社区答/全局答上下文 **8k**；索引抽取窗 **600** token；Podcast 索引约 **281 min**（16GB VM + gpt-4-turbo 公网端点）。图谱规模：Podcast **8,564** 节点 / **20,691** 边；News **15,754** / **19,520**。

### 3.5 主结果（§5.1–5.2；数字锚定正文）

**相对向量 RAG（SS）**：全局法在 comprehensiveness / diversity 上显著胜出——comprehensiveness win rate Podcast **72–83%**、News **72–80%**（$p<.001$）；diversity Podcast **75–82%**、News **62–71%**（$p<.01$）。Directness 则确认向量 RAG 最「直接」。Empowerment 结果 **混杂**。

**相对无图的源文本 map-reduce（TS）**：中间/低层社区摘要有小而一致增益（例：Podcast 中层 comprehensiveness **57%** win；News 低层 **64%**；diversity 对应 **57%** / **60%**）。

**Token 可扩展性（Table 2）**：相对 TS 的 max tokens——

| | Podcast C0 | Podcast C3 | Podcast TS | News C0 | News C3 | News TS |
|---|---|---|---|---|---|---|
| Units | 34 | 1310 | 1669 | 55 | 2142 | 3197 |
| Tokens | 26,657 | 746,100 | 1,014,611 | 39,770 | 1,140,266 | 1,770,694 |
| % Max | 2.6% | 73.5% | 100% | 2.3% | 66.8% | 100% |

文内结论：C0 每查询 token 可比 TS **少 9×–43×**；C3 仍比 TS **少 26–33%** 上下文 token；C0 相对 SS 仍有 comprehensiveness **72%**、diversity **62%** win，适合 sensemaking 的迭代追问。

**Claim 验证（Experiment 2）**：用 Claimify 抽可核事实句；全局条件与 TS 的平均 claim 数均高于 SS（Table 3：News SS **25.23** vs C0 **34.18** 等）；与 Experiment 1 方向一致。

### 3.6 对 Infra 的直接含义（不写向量库通史）

- **预计算贵、查询可分层选成本**：索引一次性 LLM 抽取 + 全社区摘要；查询可走 C0「极省」或 C3「更细」。
- **与 B6「热换整库」不同**：GraphRAG 论文主线是 **静态语料上的全局 QFS**；语料持续增长时，实体图与社区摘要如何增量维护——**正是 EraRAG 切口**（见下节）。文内未给出与 EraRAG 同设定的增量协议，勿把 GraphRAG 写成已解决动态重建。

---

## 四、EraRAG：增长语料上的选择性增量图

### 4.1 动机：Graph-RAG 的重建墙（§I / Fig.1）

场景：新闻日更、UGC、arXiv 日投稿（文举例 cs.CL 日增百篇级）。既有 Graph-RAG 往往 **轻微语料变更也触发完整图重建**。EraRAG 自称可 **Save up to 95% building time and token cost**（Fig.1 文案）；Abstract：**up to an order of magnitude** 降低更新时间与 token，同时精度更优。

对照系（Related / 实验）：RAPTOR、HippoRAG、GraphRAG、LightRAG（L/G/H）；动态相关还点名 DRAGIN、DyPRAG，但批评其 **高频率更新下的消耗** 仍被忽视。

### 4.2 构造：超平面 LSH + 尺寸闸门 + 递归摘要（Algorithm 1）

**记号（Table I）**：语料块 $c_i$、归一化嵌入 $v_i\in\mathbb{R}^d$、随机超平面 $h_j$、哈希码 $b_i\in\{0,1\}^k$、桶大小界 $S_{\min},S_{\max}$、层 $\ell=0\ldots L$。

**跟读步骤：**

1. 切块并算归一化嵌入。
2. 采样 $n$ 条随机超平面；$b_i$ 由 $\mathrm{sign}(v_i\cdot h_j)$ 得到 → 入桶 $B_{b_i}$。
3. **尺寸校正**：$|B|>S_{\max}$ → split；$|B|<S_{\min}$ → 与 Hamming 邻近桶 merge，直至落在 $[S_{\min},S_{\max}]$。
4. 每最终段 $S_i$ LLM 摘要为节点 $s_i$；摘要再当作「块」向上递归，形成多层 $G_\ell$（架构对齐 RAPTOR 式递归，但分组改 LSH+闸门）。

文内强调：相对传统 LSH 检索，这里是 **为 RAG 定做的多层 + 动态分段**；固定超平面使后续插入 **可复现地落入原桶**，无需重采样超平面。

**静态构建复杂度（文内推导）**：在 $1<S_{\min}\le S_{\max}=O(1)$ 下，
$T_{\mathrm{build}}=O\big(|C|(nd+S_{\mathrm{LLM}})\big)$（几何级数层衰减使层和为常数因子）。

### 4.3 查询：Collapsed graph search（Algorithm 2）

- 所有层节点投入 **同一扁平检索空间**（collapsed）；query 同编码器嵌入 → 在 token budget $T$ 下 top-$k$。
- 文称在多种层次结构上，**flat top-$k$ consistently outperforms** 仅按层挑的策略；实验默认 collapsed。
- 另讨论按层混合比例 $p$ 的变体（细粒度偏叶层、抽象偏高层），但主实验仍用 standard collapsed。

### 4.4 增量：Selective Re-Segmenting and Summarization（Algorithm 3 / Theorem 4）——本篇 Infra 核心

`
新块 c_new → embed → 用【同一组】超平面算 hash → 插入桶 Bb
 if |Bb| > Smax: split；if |Bb| < Smin: merge 邻近桶
 标记受影响段 → 重摘要；父节点标记 affected
 向上：对受影响摘要再 hash / 再分区 / 再摘要（传播有界）
 若当前最高层过大且 l < L：可开新层
`

- **不**全图重聚类；无关拓扑保持。
- 重摘要时：**新建**含更新摘要的节点，保留原节点引用完整性（文述方案）。
- **Theorem 4**：单次更新处理 $\Delta$ 新块时
 $T_{\mathrm{update}}(\Delta)=O\big(\Delta(nd+S_{\mathrm{LLM}})\big)$
 （每块 $O(nd)$ 投影 + 常数个桶的 split/merge；向上至多 $L$ 层、每层摊销常数段需 $S_{\mathrm{LLM}}$）。

**动态实验协议（§V）**：语料半分——**50% 初始建图**，其余 **10 轮 × 每轮 5%** 插入；无动态能力的基线每轮 **从头重建**（含已有 50%+新增）。只计图构建时间（GraphRAG 的 community detection 等预处理 **排除在计时外**——文内 Note）。

### 4.5 静态 QA 与动态消耗（Table II / Fig.4 文述）

**设置**：默认 LLM **Llama-3.1-8B-Instruct-Turbo**；嵌入 **BGE-M3**；统一框架 \[33\]。指标 Accuracy / Recall（答案 **包含** gold 即算对；QuALITY 仅 Accuracy）。

**Table II（部分，EraRAG vs 强基线）**：

| Method | PopQA Acc | QuALITY Acc | HotpotQA Acc | MuSiQue Acc | MultihopQA Acc |
|---|---|---|---|---|---|
| Vanilla RAG | 56.21 | 39.87 | 48.32 | 14.22 | 50.50 |
| GraphRAG | 49.98 | 44.90 | 40.84 | 19.32 | 56.98 |
| HippoRAG | 59.29 | 53.31 | 50.46 | 25.15 | 57.49 |
| RAPTOR | 59.02 | 55.48 | 53.29 | 24.02 | 60.11 |
| **EraRAG** | **62.98** | **60.25** | **55.39** | **25.39** | **62.87** |

文称在 10 项指标中 **8 项最优**；QuALITY Acc 相对 RAPTOR **+4.8** 点。归因：相对 RAPTOR 重叠聚类，EraRAG **一对一分桶 + 尺寸约束** → 层次更稳、冗余更少。

**动态消耗（正文叙述 Fig.4）**：相对 RAPTOR，EraRAG token **最多降约 57.6%**（PopQA）、重建时间 **降约 77.5%**（QuALITY）。GraphRAG 每更一版全量重聚类 → 时间/内存极高；HippoRAG 虽可增量，但路径扩展与语义过滤拉高 token。

**增量质量（Fig.5）**：HotpotQA / QuALITY / PopQA 上 Acc/Recall 随插入轮次上升，末轮接近 **全量静态上界**（点线）——选择性重建 **未**明显毁掉已有结构。精确点值：**待核实读图**。

**小规模插入（Exp-1 / Fig.6）**：50% 初始后插入 **1 条文档（2 chunks）**；EraRAG 更新约 **20 s**；相对 RAPTOR/HippoRAG **over an order of magnitude** 降时间与 token；相对 GraphRAG **two-order-of-magnitude** 降更新开销。

**初始覆盖（Table IV，MultihopQA）**：初始 0%→100% 再建完增量后——Accuracy 约 **41.3 → 62.9**，Recall **13.9 → 42.9**；文建议 **50–70%** 初始覆盖作性能与灵活性折中（Accuracy 在约 50% 后趋于饱和）。

**抽象问句（Table III，LLM win rate）**：相对 GraphRAG / RAPTOR，在 UltraDomain（Mix/CS/Legal）与 MultihopSum 上综合 Overall 多在 **46–55%** 区间互有胜负；文称多数设定综合更优——按表逐格读，勿夸成全面碾压（例如 vs GraphRAG 的 Legal Overall **42%**）。

---

## 五、对照表：社区摘要 vs 增量索引（本篇收束）

| 维度 | GraphRAG（2404.16130） | EraRAG（2506.20963） |
|---|---|---|
| 图怎么来 | LLM 抽实体/关系/claim → 聚合 KG | 嵌入 + **超平面 LSH** 分桶 → 段摘要节点 |
| 层次怎么来 | **Leiden** 社区递归 | 摘要再 LSH，叠到 $L$ 层 |
| 查询形态 | **社区摘要 map-reduce**（可按 C0–C3 选粒度） | **Collapsed** 扁平 top-$k$（叶块+各层摘要） |
| 擅长问题 | **全局 sensemaking / QFS**（百万 token 库主题） | 多跳/开放域 QA + **语料持续增长** |
| 更新模型 | 论文主线 **静态索引**；增长场景重建成本留给后续 | **Algorithm 3** 局部 split/merge + 向上重摘要；$T_{\mathrm{update}}=O(\Delta(nd+S_{\mathrm{LLM}}))$ |
| 与 B6 关系 | 打补丁：「向量 top-k 不够用时的全局层」 | 打补丁：「图索引运维不能每次全量重建」 |

**跟读口诀：**
B6 解决「事实在库外、可热换向量索引」；
GraphRAG 解决「问题指向整库主题时，用社区摘要做全局 QFS」；
EraRAG 解决「图索引要跟着语料长，更新必须局部化」。

---

## 六、开放问题 / 待核实

1. GraphRAG 开源仓库相对论文 v2 的默认管线（实体类型、claim 开关、社区层级默认）——以 GitHub 当前 README 为准，**本笔记不跟踪 commit**。
2. Fig.2 / Fig.4 / Fig.5 / Fig.6 曲线上的精确坐标：正文已给数量级与百分比处已录入；其余标 **待核实读图**。
3. EraRAG「95%」来自 Abstract/Fig.1 宣传句；与正文「order of magnitude / 57.6% token / 77.5% time / 两数量级 vs GraphRAG」并存——引用时区分 **摘要口号 vs 具体表/节数字**。
4. LightRAG 等「可动态加文档」声明与 EraRAG 高频更新消耗批评的边界——未展开第三方复现，不编造排名。
5. 与 [[MemoryR1强化学习记忆维护]] Memory-R1：图索引选择性更新 vs RL 维护记忆条目——交叉实验 **待后续专篇**，本篇不合并。

---

## 七、可跟读检查清单

- [ ] 能用自己的话区分：**向量 RAG（SS）** vs **社区摘要 map-reduce（C0–C3）** vs **无图源文本 map-reduce（TS）**
- [ ] 能说出 Leiden 社区摘要的叶层 / 高层填窗策略（度排序 vs 子摘要替换）
- [ ] 能默写 EraRAG 增量三件套：**固定超平面**、**$S_{\min}/S_{\max}$**、**受影响段向上重摘要**
- [ ] 能解释为何 Theorem 4 是 $O(\Delta(\cdot))$ 而不是 $O(|C|)$ 全量
- [ ] 不把本篇写成 B6 稠密检索/重排复习课

---

*起草：AI研究会·攻坚研究员执行助手 · 2026-09-22 16:58 CST（Asia/Shanghai）· status: draft · 据官方 PDF/；禁止重写 B6 向量 RAG 通史；禁止编造未核数字*

## 相关笔记

- [[法律专科模型|Legal Specialty Models]]
- [[MixtureOfAgents与TUMIX|MoA / TUMIX]]
- [[图谱检索GraphRAG|Graph RAG]]
- [[MemoryR1强化学习记忆维护|Memory-R1]]
- [[安全论证SafetyCases|Safety Cases]]

