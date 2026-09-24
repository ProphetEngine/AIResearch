---
title: "Agentic RAG：分层检索接口（A-RAG）"
topic: AgenticRAG分层检索接口
date: 2026-09-24
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2602.03442
arxiv: ["2602.03442"]
related: ["检索增强与知识外挂", "SelfRAG与CorrectiveRAG", "HippoRAG2与CatRAG", "图谱检索GraphRAG"]
code: "https://github.com/Ayanami0730/arag"
retrieval_cutoff: 2026-09-24
timezone: Asia/Shanghai (CST)
archived: 2026-09-24
---

# Agentic RAG：分层检索接口（A-RAG）

> **定位**：Agentic RAG / A-RAG——在 [[检索增强与知识外挂]]（B6）稠密检索通史、[[SelfRAG与CorrectiveRAG]] 自省与纠错、[[HippoRAG2与CatRAG]] 记忆式图检索之后，补近窗一刀：**把多粒度检索暴露成 agent 工具**，并考察 **test-time 扩展**。
> **攻坚线**：**架构思想（主）**——`keyword_search` / `semantic_search` / `chunk_read` 分层接口 + 最简 ReAct 环；**评测字段（辅）**——LLM-Acc / Contain-Acc、检索 token 数、max-step 与 reasoning effort 扩展。
> **硬划界**：
> - **≠ [[SelfRAG与CorrectiveRAG]]**：不写 reflection tokens、Correct/Incorrect/Ambiguous 三动作、Web 回退；本文是 **工具接口自主编排**，不是「要不要检索 / 检索坏了怎么办」的固定策略机。
> - **≠ [[HippoRAG2与CatRAG]]**：不写 OpenIE+PPR、查询自适应边权；本文 **不做图索引算法**，关键词层甚至不做离线倒排。
> - **≠ [[图谱检索GraphRAG]]**：不写 Leiden 社区摘要与 map-reduce QFS。
> - **≠ Harness 工具环通史**：不写 MCP / 长程 harness / 生产 Memory API；对象是 **语料库上的检索工具面**。
> **禁止编造**：机制与表数字一律锚定 arXiv:2602.03442v1（跟读 2026-09-24 CST）。图内未抽出的精确曲线点标 **待核实读图**。

---

## 一、材料元信息

| 材料 | 标识 | 角色 |
|---|---|---|
| **主文** | Du, Xu†, Zhu, Wang, Wang, Wang & Mao‡, *A-RAG: Scaling Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces* | 分层检索接口；Agentic vs Graph/Workflow 三分；test-time 扩展 |
| **版本** | arXiv:**2602.03442v1** \[cs.CL\]（**3 Feb 2026** UTC；PDF 页眉 *February 4, 2026*）；`https://arxiv.org/abs/2602.03442`；**18** 页 letter | 本稿唯一数字源 |
| **代码（文内）** | `https://github.com/Ayanami0730/arag` | 文称将释出代码与评测套件；本笔记不展开仓库提交史 |

**一句话抓手：** 现有 RAG 要么「算法一次取段再拼接」，要么「预写工作流让模型逐步执行」——模型都不能真正改检索策略。A-RAG 把 **关键词 / 语义 / 整块阅读** 三层暴露成工具，用最简 ReAct 环让模型按任务自编排，并证明 **步数与 reasoning effort** 可抬升准确率，同时 Full 配置的检索 token 可与传统方法相当甚至更低。

---

## 二、动机：为何「算法一次取」与「预写工作流」都不够

### 2.1 两种旧范式（§1 / Fig.1）

文首把既有 RAG 收成两类（均 **不允许模型参与检索决策**）：

1. **算法一次取**：用（可含图结构的）检索算法一次取出多段，拼接进上下文（GraphRAG、RAPTOR、HippoRAG 系、LinearRAG 等）。
2. **预写工作流**：固定流程，提示模型逐步执行（FLARE、IRCoT、RA-ISF、部分多 agent 编排，以及依赖 SFT/RL 跟流程的训练式方法）。文称此类为 **Workflow RAG**。

二者共同缺口：模型不能按任务改交互策略，也不能自主判断「证据何时够用可作答」。

### 2.2 初探：最简 Agentic 已胜过 Naive RAG

文称：即便 **Naive Agentic RAG**（只给单一 embedding 检索工具）也稳定优于 Naive RAG 与若干既有基线（Fig.1 / §4）。这表明收益来自 **检索决策自主权**，而不必先堆复杂索引。

### 2.3 真 Agentic 的三条原则（§2 / Appendix A Table 4）

文用三原则筛「真 agentic」：

| 原则 | 含义 |
|---|---|
| **Autonomous Strategy** | 高层策略（是否/何时/如何检索、分解、验证、再规划）由模型动态组织，而非被外部规则/分类器锁死 |
| **Iterative Execution** | 多轮执行，轮数可随中间结果变化，而非严格 one-shot |
| **Interleaved Tool Use** | ReAct 式 action→observation→reasoning；每次工具调用条件于前次观察 |

Appendix Table 4 将 Self-RAG、CRAG、HippoRAG2、GraphRAG、IRCoT、MA-RAG 等标为 ✗ 或边界 Δ；文称 **仅 A-RAG 三项全 ✓**。跟读用途：这是作者的范式分类锚，不是对相邻笔记机制的否定——相邻笔记仍各自成立，只是 **不满足本文定义的「真 agentic」全集**。

---

## 三、分层检索接口设计

总览（Fig.3）：**分层索引** + **三工具** + **最简 agent 环**。刻意不用并行工具调用等复杂编排，以便隔离「接口形态」对行为的影响（§3.3）。

### 3.1 轻量分层索引（§3.1）

| 层 | 做法 | 备注 |
|---|---|---|
| **Chunk** | 约 **1,000** token / 块，边界对齐句子（跟 LinearRAG 设定） | 完整语义单元；按需读取，而非一律拼接 |
| **Sentence** | 规则分句；预训练句编码器 $f_{\mathrm{emb}}$ 得 $\mathbf{v}_{i,j}$ | 细粒度语义匹配；句→父块可回溯 |
| **Keyword** | **不**做离线倒排或 KG；查询时 **精确文本匹配** | 降索引成本；实体名等精确命中 |

三层合起来支持「先瞥片段、再读全文」的渐进取证。

### 3.2 三个检索工具（§3.2）

**`keyword_search`**  
- 输入：关键词列表 $\mathcal{K}$ 与返回数 $k$。  
- 块分：$\mathrm{Score}_{\mathrm{kw}}(c_i,\mathcal{K})=\sum_{k\in\mathcal{K}}\mathrm{count}(k,T_i)\cdot|k|$（更长词加权更高）。  
- 返回：top-$k$ 块 ID + **含关键词句子的缩略 snippet**（非整块）。

**`semantic_search`**  
- 输入：自然语言查询 $q$；$\mathbf{v}_q=f_{\mathrm{emb}}(q)$，与句向量余弦相似度。  
- 按父块聚合（块分 = 块内最高句分）；返回 top-$k$ 块 ID + 匹配句 snippet。

**`chunk_read`**  
- 据 snippet 判断后读完整块；也可读相邻块补上下文。  
- 与搜索工具配合形成 **「先瞥后读」**：搜索只给缩略，回答前须 `chunk_read`（Appendix 工具说明原文强调）。

### 3.3 Agent 环与 Context Tracker（§3.3 / Appendix C）

- **环**：ReAct 式（Yao et al., 2023）；每轮选 **一个** 工具 → 观察 → 再决策；达最大迭代仍无答案则强制据已有信息作答。  
- **Context Tracker**：维护已读块集合 $\mathcal{C}^{\mathrm{read}}$；重复 `chunk_read` 只返回「This chunk has been read before」，**不**再消耗全文 token，并鼓励探索新块。

对照变体：

| 变体 | 工具面 |
|---|---|
| **A-RAG (Naive)** | 单一 embedding 检索（+ 读块，视提示配置） |
| **A-RAG (Full)** | `keyword_search` + `semantic_search` + `chunk_read` |

---

## 四、与 Self-RAG / CRAG、HippoRAG 2 的分工

| 笔记 / 范式 | 主问题 | 本篇只取 | 本篇不写 |
|---|---|---|---|
| [[检索增强与知识外挂]] | 库外非参数记忆 + 条件生成 | 「固定 top-K 无差别塞入」对照槽 | DPR/MIPS、RAG-Token/Sequence 通史 |
| [[SelfRAG与CorrectiveRAG]] | 何时检索；检索坏了如何纠错 | Table 4 中 Self-RAG / CRAG 作「非全自主」对照；Workflow 谱系中的自省/纠错定位一句 | reflection tokens；CRAG 三动作与 Web 回退 |
| [[HippoRAG2与CatRAG]] | 记忆式开放 KG + PPR；查询自适应遍历 | Table 1/3 中 HippoRAG2 作 **Graph-RAG 系基线**；文 §2.2 一句：结构丰富仍靠预定义检索算法 | OpenIE、PPR、CatRAG 动态边权 |
| [[图谱检索GraphRAG]] | 社区摘要全局 QFS | 同作 Graph-RAG 基线 | Leiden / map-reduce 全文 |
| **本篇 A-RAG** | **多粒度检索工具面 + 模型自编排 + test-time 扩展** | — | — |

跟读口诀：

```
B6            = 向量 RAG 通史（一次取段拼接）
Self/CRAG     = 何时取 / 取坏了怎么办（自省·纠错策略机）
HippoRAG2 等  = 记忆式图算法（索引侧聪明）
A-RAG         = 检索接口侧 agent 化（工具面聪明 + 测时算力可扩）
```

---

## 五、评测与扩展结果（仅文内可核）

### 5.1 设定（§4.1）

| 项 | 文内 |
|---|---|
| 数据 | HotpotQA、2WikiMultiHopQA、MuSiQue、GraphRAG-Bench（Med. / Novel；跟 LinearRAG 同语料与题） |
| 骨干 | **GPT-4o-mini**、**GPT-5-mini** |
| 稠密检索 | 除 LinearRAG 外统一 **Qwen3-Embedding-0.6B**，$k=5$ |
| 指标 | **LLM-Acc**（语义等价，judge=GPT-5-mini）；短答另报 **Contain-Acc**；GraphRAG-Bench 长答只报 LLM-Acc |
| 基线组 | Vanilla：Direct / Naive RAG；Graph+Workflow：GraphRAG、HippoRAG2、LinearRAG、FaithfulRAG、MA-RAG、RAGentA |

### 5.2 主结果摘录（Table 1，%）

**GPT-5-mini · LLM-Acc（全文最优加粗语义由文标注）：**

| Method | MuSiQue | HotpotQA | 2Wiki | Med. | Novel |
|---|---:|---:|---:|---:|---:|
| Naive RAG | 52.8 | 81.2 | 50.2 | 86.1 | 70.6 |
| HippoRAG2 | 61.7 | 84.8 | 82.0 | 78.2 | 54.3 |
| LinearRAG | 62.4 | 86.2 | 87.2 | 79.2 | 54.7 |
| A-RAG (Naive) | 66.2 | 90.8 | 70.6 | 92.7 | 80.4 |
| **A-RAG (Full)** | **74.1** | **94.5** | **89.7** | **93.1** | **85.3** |

文述三点：

1. 统一评测下，Vanilla / Naive RAG 仍强；Graph/Workflow 系 **未能**在全部集上一致压过简单基线。  
2. **Naive A-RAG** 已在多集上超过 Graph/Workflow，说明仅「给自主权」就有范式红利；换 GPT-5-mini 后更明显。  
3. **Full** 在 GPT-4o-mini 上 5 集中 **3** 集最优；在 GPT-5-mini 上 **全部**最优——分层工具面与更强推理/工具调用能力同向放大。

GPT-4o-mini 上 Full 的 LLM-Acc：MuSiQue **46.1**、Hotpot **77.1**、2Wiki **60.2**、Med. **79.4**、Novel **72.7**（相对同骨干 Naive A-RAG 与多数 Graph/Workflow 基线仍整体占优，但 2Wiki 上 HippoRAG2 的 64.7 高于 Full 的 60.2——跨骨干不可混比决绝对胜负）。

### 5.3 消融（Table 2，GPT-5-mini 设定下 Full 为参照）

| 变体 | MuSiQue LLM | Hotpot LLM | 2Wiki LLM |
|---|---:|---:|---:|
| Full | 74.1 | 94.5 | 89.7 |
| w/o KW Search | 72.6 | 93.0 | 88.9 |
| w/o Semantic | 69.4 | 93.9 | 89.1 |
| w/o Chunk Read | 73.6 | 93.6 | 89.0 |

文释：去掉关键词或语义任一层会伤多跳；去掉 `chunk_read`（搜索直接回整块）劣于「先 snippet 再精读」，说明渐进披露既增自主性又减噪声。

### 5.4 Test-time 扩展（§5.1 / Fig.4）

在 MuSiQue **前 300** 题：

| 扩展轴 | 文内可核表述 |
|---|---|
| max-step **5→20** | GPT-5-mini LLM-Acc 约 **+8%**；GPT-4o-mini 约 **+4%**（强推理模型更吃长程探索） |
| reasoning effort **minimal→high** | GPT-5-mini 与 GPT-5 均约 **+25%** |

精确曲线点：**待核实读图**（Fig.4）。

### 5.5 上下文效率（Table 3，GPT-5-mini，检索 token）

| Method | MuSi. | Hotpot. | 2Wiki | Med. | Novel |
|---|---:|---:|---:|---:|---:|
| Naive RAG | 5,387 | 5,358 | 5,506 | 5,418 | 4,997 |
| HippoRAG2 | 5,411 | 5,380 | 5,538 | 5,447 | 5,019 |
| A-RAG (Naive) | 56,360 | 27,455 | 45,406 | 23,657 | 22,391 |
| **A-RAG (Full)** | **5,663** | **2,737** | **2,930** | **7,678** | **6,087** |

要点：Full 在更高准确率下检索 token **可比或更少**；Naive 变体 token 暴涨但分数更低——分层「先瞥后读」是效率关键，而非「多取必好」。

### 5.6 失败模式（§5.3 / Appendix D）

对 MuSiQue 上 A-RAG 前 **100** 错例人工归类：主因是 **推理链错误**（Appendix：MuSiQue 上约占 **82%**），其内 **实体混淆** 最常见（约 **40%**）；另有错误检索策略、题意误解等。相对 Naive RAG「找不到文档」瓶颈，Agentic 后瓶颈转为「找到了但推错」——优化方向偏实体消歧与策略，而非再堆索引复杂度。

---

## 六、局限（文内 Limitations）

1. **工具设计未穷尽**：未系统比较任意工具子集与行为差异；更全消融留待后续。  
2. **更大骨干未验证**：算力所限，未在 GPT-5、Gemini-3 等更强模型上验证（文预期增益会更大，但属预期而非结果）。  
3. **任务面偏多跳 QA**：事实核查、对话、长文生成等知识密集任务的泛化待证。

结论取向（§6）：未来重点宜放在 **agent-friendly 接口设计**，而非继续堆复杂检索算法。

---

## 七、文献

| 角色 | 文献 | 链接 |
|---|---|---|
| **主锚** | Du et al., *A-RAG: Scaling Agentic Retrieval-Augmented Generation via Hierarchical Retrieval Interfaces*, arXiv:2602.03442v1, 2026 | https://arxiv.org/abs/2602.03442 |
| 代码（文内） | Ayanami0730/arag | https://github.com/Ayanami0730/arag |
| 语料设定参照 | Zhuang et al., LinearRAG, arXiv:2510.10114 | https://arxiv.org/abs/2510.10114 |
| Agent 环骨架 | Yao et al., *ReAct*, 2023 | https://arxiv.org/abs/2210.03629 |
| 划界对照 | Self-RAG https://arxiv.org/abs/2310.11511 ；CRAG https://arxiv.org/abs/2401.15884 ；HippoRAG 2 https://arxiv.org/abs/2502.14802 ；GraphRAG https://arxiv.org/abs/2404.16130 | 见各相邻笔记 |

