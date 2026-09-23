---
title: "RAG→记忆新范式：HippoRAG 2 + CatRAG（≠ GraphRAG / Self-RAG）"
topic: HippoRAG2与CatRAG
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2502.14802 # 2.4M / 19p
 - https://arxiv.org/abs/2602.01965 # 655K / 13p
 - https://aclanthology.org/2026.findings-acl.290/ # ACL 会刊近重复，仅 URL+抽取
arxiv: ["2502.14802", "2602.01965"]
acl: ["2026.findings-acl.290"]
related: ["检索增强与知识外挂", "图谱检索GraphRAG", "SelfRAG与CorrectiveRAG", "检索式注意力", "Mem0与Zep生产级记忆", "智能体长程记忆"]
code_hipporag: "https://github.com/OSU-NLP-Group/HippoRAG"
code_catrag: "https://github.com/kwunhang/CatRAG"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# RAG→记忆新范式：HippoRAG 2 + CatRAG（≠ GraphRAG / Self-RAG）

> **定位**：[[HippoRAG2与CatRAG]] **P0 RAG / 记忆检索**——在 B6 稠密检索通史、[[图谱检索GraphRAG]] 社区摘要 GraphRAG、[[SelfRAG与CorrectiveRAG]] Self-RAG/CRAG 自适应检索之后，补近窗两刀：**HippoRAG 2**（把 RAG 推向**非参数长期记忆**的事实 / 联想 / 通感三维评测）与 **CatRAG**（在 HippoRAG 2 图上解决「静态图谬误 / hub 漂移」，做**查询自适应遍历**）。
> **攻坚线**：**架构思想（主）**——OpenIE+PPR 记忆索引、dense-sparse、recognition memory、查询条件边权；**评测字段（辅）**——三轴记忆表 / FCR·JSR 完整性，禁外推未测场景。
> **硬划界（开篇钉死）**：
> - **≠ B6**：禁止重写稠密双塔 / DPR / MIPS / 向量库产品通史；本卡只用「标准向量 RAG 缺联想与通感」对照槽。
> - **≠ [[图谱检索GraphRAG]]**：禁止把 HippoRAG 写成 **GraphRAG 重写**。GraphRAG = 实体图 → Leiden 社区 → **预计算摘要扩库** → map-reduce 全局 QFS；HippoRAG 2 文内自述：KG **辅助检索过程**，**不**用摘要去膨胀检索语料（§2.2）。
> - **≠ [[SelfRAG与CorrectiveRAG]]**：禁止重写 Self-RAG reflection tokens / CRAG 三动作 Web 回退；CatRAG 文内把 Self-RAG 等标为**多轮迭代检索**，自称 **one-shot** 改权再单次 PPR（§2.3）。
> - **≠ [[检索式注意力]]**：禁止重写 RetrievalAttention 式「模型内注意力检索」；本卡是**库外开放 KG + PPR**。
> - **≠ [[Mem0与Zep生产级记忆]]**：禁止重写 Mem0 / Zep **生产对话记忆层** API；本卡是**文档语料上的检索图算法**，不是会话事实抽取–更新服务。
> **禁止编造**：机制、表数字、消融一律锚定官方 PDF（2026-09-22 CST）。图内未抽出的精确曲线点标 **待核实读图**。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主①** | *From RAG to Memory: Non-Parametric Continual Learning for Large Language Models*（HippoRAG 2） | arXiv:**2502.14802v2** \[cs.CL\]（**19 Jun 2025**）；ICML 2025（PMLR 267）；作者 Gutiérrez*, Shu*, Qi, Zhou, Su（OSU / UIUC） | `https://arxiv.org/abs/2502.14802` | **2.4M**（2,498,688 B） | **19** letter | |
| **主②·arXiv** | *Breaking the Static Graph: Context-Aware Traversal for Robust Retrieval-Augmented Generation*（CatRAG） | arXiv:**2602.01965v1** \[cs.CL\]（**2 Feb 2026**）；作者 Lau†, Zhang, Ruan, Zhou, Guo, Zhang, Zhou（Huawei HKRC / HKUST / CUHK-Shenzhen） | `https://arxiv.org/abs/2602.01965` | **655K**（670,229 B） | **13** A4 | |
| **主②·ACL** | *Breaking the Static Graph: Context-Aware Traversal for Graph-Based RAG* | ACL Findings **2026** pp.**5849–5863**； CreationDate **2026-06-09 22:00:05 CST** | [`ACL Anthology`](https://aclanthology.org/2026.findings-acl.290/)（近重复，仅 URL+抽取） | **—**（未入库） | **15** A4 | |

| 材料 | 代码 / 数据（文内或仓库自报） |
|---|---|
| HippoRAG 2 | https://github.com/OSU-NLP-Group/HippoRAG ；README 另链 HuggingFace `osunlp/HippoRAG_2`；前作 HippoRAG 1：arXiv 2405.14831 / `legacy` 分支 |
| CatRAG | https://github.com/kwunhang/CatRAG ；README：**2026-04-14** 录 ACL Findings 2026；**2026-08-20** 释出**复现实现**与 HoVer 数据。注意：论文 Limitations 写「**完整源码因专有数据政策不能公开**」，仅给超参表；跟读以「复现仓库 ≠ 论文作者原仓库全量」标注 |

**体积判定**：HippoRAG 2 **2.4M**、CatRAG arXiv **655K**，均 **<20MB** → 按 Wave10 验收规矩入库；ACL Findings 与 arXiv 近重复，按验收规矩仅保留 URL+抽取。

**一句话抓手：**
- **HippoRAG 2**：OpenIE 短语图 + **passage 节点 / context 边**（dense-sparse）+ **query-to-triple** + LLM **recognition memory** 滤三元组 → PPR → 段落 QA；用事实 / 联想 / 通感三轴证明「结构增强不必牺牲简单事实」。
- **CatRAG**：承认 HippoRAG 2 转移矩阵在索引期**冻结** → hub 漂移 / 高部分召回但证据链断裂；用 **Symbolic Anchoring + 查询感知动态边权 + Key-Fact 段落加权** 把静态图改成查询条件导航，主指标升 **FCR / JSR**。

---

## 二、议题边界：只写「记忆式检索图」，不写社区摘要 / 自省检索 / 生产记忆 API

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **B6** | 「向量 top-k 缺多跳联想」是两文共同对照槽 | 稠密双塔 / 向量库选型通史 |
| **[[图谱检索GraphRAG]]** | GraphRAG / RAPTOR / LightRAG 作为 HippoRAG 2 Table 2–3、CatRAG Table 2–3 **结构增强基线**；HippoRAG 2 §2.2 一句点明与 GraphRAG「摘要扩库」之别 | Leiden 社区摘要 + map-reduce 全局 QFS 全文；EraRAG 增量 LSH |
| **[[SelfRAG与CorrectiveRAG]]** | CatRAG §2.3 把 Self-RAG / IRCoT 标为多轮迭代对照 | reflection tokens / Corrective 三动作 / Web 回退全文 |
| **[[检索式注意力]]** | （无直接依赖）仅防混淆：都叫「检索」 | 注意力内核内检索 |
| **[[Mem0与Zep生产级记忆]] / [[智能体长程记忆]]** | 「长期记忆」隐喻相邻；对象不同 | Mem0 四操作 tool-call、Zep Graphiti 时序 episode、MemGPT 分页 |

### 2.2 本卡主轴 vs 禁区（防「GraphRAG 重写」）

| 写 | 不写 |
|---|---|
| HippoRAG 2：OpenIE 开放 KG + PPR；passage 节点与 context 边；query-to-triple；recognition memory | GraphRAG 社区摘要管线；把 HippoRAG 说成「又一个社区 map-reduce」 |
| 三轴评测：factual（NQ/PopQA）/ associativity（MuSiQue/2Wiki/Hotpot/LV-Eval）/ sense-making（NarrativeQA） | 把 NarrativeQA 误写成 GraphRAG 式「全局主题 QFS」专属 |
| CatRAG：Static Graph Fallacy、hub bias、FCR/JSR | Self-RAG 式反复 generate–retrieve 环 |
| 两文数字锚定 Table | 未给出的「生产 SLA / 客户语料」外推；跨文不同 embedding 直接比绝对分决胜负 |

跟读口诀：

`
B6 = 向量 RAG 通史
[[图谱检索GraphRAG]] = 文档 GraphRAG：摘要扩库 + 全局 QFS
[[SelfRAG与CorrectiveRAG]] = 何时取 / 取坏了怎么办（自省·纠错）
[[HippoRAG2与CatRAG]] = 记忆式开放 KG + PPR；再升级查询自适应遍历
[[Mem0与Zep生产级记忆]] = 对话/业务生产记忆层（≠ 文档检索图算法）
`

---

## 三、HippoRAG 2：从 RAG 到非参数长期记忆

### 3.1 动机：结构增强不能牺牲事实记忆

文首诊断（Abstract / §1 / Fig.1）：标准 RAG 靠向量检索，难捕获人类长期记忆的 **sense-making**（Klein et al.）与 **associativity**（Suzuki）；近期结构增强 RAG（摘要树 / KG / 社区）在多跳与长语篇上有收益，但在**简单事实 QA**上相对最强 embedding RAG **全面掉队**。HippoRAG 2 目标：在联想任务上相对 SOTA embedding **约 7 个点**提升的同时，事实与通感**不劣化甚至略升**（Abstract：「7% improvement in associative memory…」；正文 §1：「average 7 point improvement… associativity」）。

与 GraphRAG 的关键一句（§2.2，跟读必留）：GraphRAG / LightRAG 用 KG **生成高层摘要以扩展检索语料**；HippoRAG 2 的 KG **用于辅助检索过程本身**，从而少引入 LLM 摘要噪声——这正是「≠ [[图谱检索GraphRAG]]」的文内锚点。

### 3.2 相对 HippoRAG 1 的三处加深（§3）

沿用神经生物学隐喻：LLM≈新皮层；开放 KG + PPR≈海马联想；encoder≈旁海马联结。流水线仍分 **offline indexing / online retrieval**（Fig.2），但 2 做了三刀：

| 模块 | 做什么 | 相对 HippoRAG 1 |
|---|---|---|
| **Dense-Sparse Integration（§3.2）** | 短语节点=稀疏概念；新增 **passage 节点**，以 labeled **「contains」context 边**连回该段抽出的短语 | 1 的 document ensemble 只是分数融合；2 把段落**嵌进图结构** |
| **Deeper Contextualization（§3.3）** | 默认 **Query → Triple**（整查询对三元组 embedding）；对照 NER→Node / Query→Node | 1 偏 NER 实体中心，上下文信号浪费 |
| **Recognition Memory（§3.4）** | embedding 取 top-$k$ 三元组后，**LLM 过滤**得 $T'\subseteq T$（prompt Appendix A；DSPy MIPROv2 调优） | 线上引入「识别」过滤种子噪声 |

**Online（§3.5）**：过滤后的短语作 seed；**所有 passage 节点**亦作 seed（文称更宽激活利于多跳）；passage reset 概率按 embedding 相似度再乘 **weight factor**（默认 **0.05**，Table 5）；跑 PPR；按 PageRank 取 top 段落给 QA。

边类型（后文 CatRAG 也沿用）：Relation / Synonym / Context。

### 3.3 实验配置（§4）

| 项 | 文内设定 |
|---|---|
| 抽取 / 过滤 LLM | **Llama-3.3-70B-Instruct**（OpenIE + triple filter） |
| Retriever | **nvidia/NV-Embed-v2**（主）；另测 GTE-Qwen2-7B、GritLM-7B（Table 7） |
| QA reader | Llama-3.3-70B-Instruct（主表）；附录含 GPT-4o-mini |
| 指标 | 检索 **passage recall@5**；QA **token F1**（MuSiQue 协议） |
| 结构基线 | RAPTOR、**GraphRAG**、LightRAG、HippoRAG（同 extractor+retriever 复现） |
| 数据（Table 1） | NQ/PopQA/MuSiQue/2Wiki/Hotpot 各 1,000 查询；LV-Eval 124；NarrativeQA 293（10 部长文） |

### 3.4 主结果（Table 2 / Table 3；QA reader = Llama-3.3-70B）

**Table 2 · QA F1（节选）：**

| Retrieval | NQ | PopQA | MuSiQue | 2Wiki | HotpotQA | LV-Eval | NarrativeQA | Avg |
|---|---|---|---|---|---|---|---|---|
| NV-Embed-v2 | 61.9 | 55.7 | 45.7 | 61.5 | 75.3 | 9.8 | 25.7 | 57.0 |
| GraphRAG | 46.9 | 48.1 | 38.5 | 58.6 | 68.6 | 11.2 | 23.0 | 49.6 |
| HippoRAG | 55.3 | 55.9 | 35.1 | 71.8 | 63.5 | 8.4 | 16.3 | 53.1 |
| **HippoRAG 2** | **63.3†** | 56.2 | **48.6†** | **71.0†** | 75.5 | **12.9†** | 25.9 | **59.8** |

†：相对最佳 NV-Embed-v2 基线 bootstrap $p<0.05$（表注）。
跟读：结构增强里 GraphRAG / RAPTOR / LightRAG **Avg 全面低于** NV-Embed-v2；HippoRAG 2 是表内**唯一**全面压过最强稠密检索的结构方法——支持「记忆范式」而非「又一个 GraphRAG」。

**Table 3 · recall@5（节选）：** HippoRAG 2 Avg **78.2** vs NV-Embed-v2 **73.4**；MuSiQue **74.7** vs **69.7**（文称相对最强稠密 +5.0 / 对 2Wiki +13.9 百分点量级，§5）。

### 3.5 消融与稳健性（§6）

**Table 4 · recall@5 消融（多跳 Avg）：** HippoRAG 2 **87.1**；换 NER-to-node **74.6**；Query-to-node **59.6**；去 Passage Node **81.0**；去 Filter **86.4**。文称 query-to-triple 相对 NER-to-node 平均 Recall@5 **+12.5%**（§6.1）。

**Table 5**：passage reset 权重 0.01–0.5；默认 **0.05**（MuSiQue/NQ dev 折中）。

**Table 7**：换 GTE / GritLM / NV-Embed，HippoRAG 2 相对纯稠密检索在 MuSiQue 子集均稳定抬升（如 NV-Embed 69.7→74.7）。

**Fig.3（待核实读图）**：NQ / MuSiQue 四段增量语料的 continual 模拟；文称相对 NV-Embed 的优势在简单与联想轴上**保持一致**，但联想任务随语料膨胀**双方以相近速率下降**——提示未来 continual benchmark 要混复杂度。

---

## 四、CatRAG：打破静态图——查询自适应遍历

### 4.1 问题：Static Graph Fallacy

建立在 **HippoRAG 2 架构之上**（Abstract / §3.1）：索引期固定转移矩阵 $T$，边相关性与查询无关 → **semantic drift**（概率被高权泛化边吸走，如 Marie Curie→Radioactivity）与 **hub node** 汇点（Nobel Prize、French 等）。表观 Recall 可因「部分命中」偏高，但**完整证据链**断裂。示例查询：「Which university did Marie Curie’s doctoral advisor attend?」（Fig.1）。

与 [[SelfRAG与CorrectiveRAG]] 的边界（§2.3）：IRCoT / Self-RAG / 若干 agentic 环靠**多轮 LLM 检索**，延迟高；CatRAG 自称 **one-shot** 上下文改权后再单次遍历，保留图检索速度形态。

### 4.2 三机制（§3.2–3.5）

图定义沿用 HippoRAG 2：$V=V_E\cup V_P$；边 = Relation / Synonym / Context。PPR：$v^{(k+1)}=(1-d)\,e_s + d\,v^{(k)}T$；目标把 $T$ 炼成查询条件 $\hat T_q$。

| 机制 | 操作要点 | 成本感（文内） |
|---|---|---|
| **Symbolic Anchoring** | NER 实体作**弱 seed**，reset 小概率 $\epsilon$，从属于 query-to-triple 主种子；对抗向 hub 扩散 | 轻 |
| **Query-Aware Dynamic Edge Weighting** | 先拓扑粗剪（$N_{\mathrm{seed}},K_{\mathrm{edge}}$）；再 LLM 对出边打相关性，$\hat w_{uv}=\phi(\mathrm{LLM}(\cdot))\cdot w_{uv}^{(\mathrm{static})}$；仅对 seed 出发的前向边 | **需线上 LLM**（Limitations 主要开销） |
| **Key-Fact Passage Weight Enhancement** | 若 context 边被 recognition 过滤后的 $T_{\mathrm{seed}}$ 支持，则 $\hat w_{up}=w_{up}(1+\beta\cdot I(\cdot))$ | **零额外 token** |

默认超参（§4.4）：$\epsilon=0.2$（按 $|P_i|^{-1}$ 加权）、$\beta=2.5$、$N_{\mathrm{seed}}=5$、$K_{\mathrm{edge}}=15$；LLM=**GPT-4o-mini**；embedding=**text-embedding-3-small**（刻意不用 NV-Embed-v2，以**隔离拓扑增益**）；QA=Llama-3.3-70B-Instruct；主基线=**同栈复现的 HippoRAG 2**。

### 4.3 指标升级：FCR / JSR（§4.3）

| 指标 | 定义 |
|---|---|
| Recall@5 / F1 | 常规 |
| **FCR**（Full Chain Retrieval） | 检索上下文覆盖**全部**金标支持文档的查询占比 |
| **JSR**（Joint Success Rate） | **同时**满足 FCR 且生成答案正确（对齐 FEVER/HoVer 严格口径） |

数据：MuSiQue / 2Wiki / Hotpot 各 1,000（与 HippoRAG 子集协议）；**HoVer** 1,000 条 3–4 hop 声明（Table 1）。

### 4.4 主结果（Table 2–4；数字取 arXiv 抽取）

**Table 2 · Recall@5：**

| Method | MuSiQue | 2Wiki | HotpotQA | HoVer |
|---|---|---|---|---|
| text-embedding-3-small | 55.4 | 70.8 | 81.3 | 65.7 |
| HippoRAG 2 | 61.4 | 85.9 | 87.1 | 71.2 |
| **CatRAG** | **64.9** | **87.0** | **89.5** | **76.8** |

**Table 3 · QA（F1；HoVer=accuracy）：** CatRAG MuSiQue **45.0** / 2Wiki **69.7** / Hotpot **71.4** / HoVer **69.0**；HippoRAG 2 为 43.2 / 68.1 / 69.4 / 67.2。

**Table 4 · FCR/JSR：**

| Method | MuSiQue | 2Wiki | HotpotQA | HoVer |
|---|---|---|---|---|
| HippoRAG 2 | 30.5/21.5 | 66.1/53.0 | 75.5/53.4 | 34.8/26.2 |
| **CatRAG** | **34.6/24.3** | **67.6/55.0** | **80.4/56.8** | **42.5/31.1** |

正文强调：MuSiQue FCR 30.5→**34.6**；HoVer JSR **31.1**，相对 HippoRAG 2 约 **+18.7% 相对提升**（§5）。标准 Recall「温和」、**完整性指标**拉开——这是本卡相对 [[图谱检索GraphRAG]]/[[SelfRAG与CorrectiveRAG]] 的评测增量。

### 4.5 消融与 hub 分析（Table 5 / §6.1）

**Table 5 · recall@5：** CatRAG 64.9/87.0/89.5/76.8；去 Symbolic 63.0/86.1/88.6/**73.6**（HoVer −3.2）；去 $E_{\mathrm{rel}}$ 加权 63.2/85.6/88.1/75.0；去 Passage Enhance 64.7/**88.4**/89.0/76.6——文称 2Wiki 上去 Key-Fact 略升、非结构化集上 Key-Fact 更有用。

Hub 量化（100 条 MuSiQue 抽样）：Mean PPR-Weighted Strength **837.0→761.7**；top-1% super-hub 概率质量 **45.7%→42.5%**（§6.1）。Fig.2 分布左移 → **待核实读图**。

### 4.6 Limitations（跟读必留）

- 动态边权需运行时 LLM → 延迟/费用高于纯静态 PPR。
- 实验刻意用较小 embedding，**绝对上限**可能被更大 encoder 抬高（非本卡可外推）。
- **完整源码因专有政策未公开**；公开 GitHub 为后续**复现实现**（README 2026-08-20）——笔记索引代码时两者并存、勿混称为「论文官方全量开源」。

---

## 五、双主文对照（仅文内字段；不替选型拍板）

| 维度 | HippoRAG 2 | CatRAG |
|---|---|---|
| 问题框 | 结构 RAG 伤事实记忆；要事实+联想+通感三轴 | 静态 $T$ → hub 漂移；部分召回≠完整证据链 |
| 图角色 | 开放 KG **辅助检索**（≠ 摘要扩库） | **同一 HippoRAG 2 图**上查询条件改 $T$ |
| 线上 LLM | recognition 滤三元组 | 再加出边相关性打分（+弱锚定 / Key-Fact 无 LLM） |
| 主 embedding（文内主表） | NV-Embed-v2 | text-embedding-3-small（隔离拓扑） |
| 主增量指标 | 三轴 F1 / recall@5；Avg QA 59.8 | FCR / JSR；HoVer 链完整 |
| 与 GraphRAG | Table 内基线；§2.2 机制划界 | 相关工作提及；**非**社区摘要主轴 |
| 与 Self-RAG | 未作主对照 | §2.3：多轮迭代 vs one-shot 改权 |

选型跟读建议（仍非裁决）：若问题框是「**文档库非参数记忆是否在简单事实上不崩**」→ HippoRAG 2 Table 2；若问题框是「**多跳证据链是否收全（FCR）**、hub 是否吸走概率」→ CatRAG Table 4；若问题框是「**全局主题综述**」→ 回 **[[图谱检索GraphRAG]]**；若「**对话生产记忆 API**」→ 回 **[[Mem0与Zep生产级记忆]]**。

---

## 六、可复核清单与已知缺口

**可复核：**
1. 本地体积：`ls -lh https://arxiv.org/abs/2502.14802 https://arxiv.org/abs/2602.01965` → **2.4M / 655K**；ACL Findings：[`ACL Anthology`](https://aclanthology.org/2026.findings-acl.290/) + （ACL 会刊近重复，仅 URL+抽取）。
2. 页数：**19 / 13 / 15**；ACL 页码 **5849–5863**。
3. HippoRAG 2 Table 2/3/4、CatRAG Table 2/3/4/5 与 `*.txt` 一致。
4. 划界句可回链：HippoRAG 2 §2.2「aid in the retrieval process rather than to expand the retrieval corpus」；CatRAG §2.3 one-shot vs Self-RAG 迭代。

**缺口 / 勿编造：**
- HippoRAG 2 Fig.3 折线具体点坐标未从文本抽出 → 只保留文内定性。
- 两文主表 **embedding 栈不同**（NV-Embed-v2 vs text-embedding-3-small），**禁止**把 CatRAG 表内 HippoRAG 2 分数与 HippoRAG 2 原文 Table 3 直接纵向比绝对召回。
- CatRAG 论文「源码未全公开」与 GitHub「复现实现」并存；本卡不臆测二者 diff。
- 禁止把 Mem0/Zep 的 LOCOMO/LongMemEval、Memory-R1 的 RL 增益写进本卡能力。
- 禁止把 HippoRAG 2 叙事改写成 GraphRAG 社区摘要变体。

---

## 七、与 Wave10 agenda 的对齐句

Agenda [[HippoRAG2与CatRAG]]：「B6 立稠密检索；[[图谱检索GraphRAG]] 立社区摘要 GraphRAG；[[SelfRAG与CorrectiveRAG]] 立 Self-RAG/CRAG。近窗 **HippoRAG 2** 推向非参数长期记忆（事实/联想/通感）；**CatRAG** 针对静态图 hub 漂移做查询自适应边权与锚定。划界 ≠B6/[[图谱检索GraphRAG]]/[[SelfRAG与CorrectiveRAG]]/[[检索式注意力]]/[[Mem0与Zep生产级记忆]]；禁止写成 GraphRAG 重写。」本卡交付即该缺口：双主文入库 + ACL Findings 近重复仅 URL+抽取，开篇划界钉死，评测字段锚定 PDF。
