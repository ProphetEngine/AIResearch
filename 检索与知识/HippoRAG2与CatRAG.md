---
date: 2026-09-22
topic: HippoRAG2与CatRAG
title: "RAG→记忆新范式：HippoRAG 2 + CatRAG"
lines: [架构思想, 评测字段]
sources:
 - https://arxiv.org/abs/2502.14802
 - https://arxiv.org/abs/2602.01965
 - https://aclanthology.org/2026.findings-acl.290/
related: ["检索增强与知识外挂", "图谱检索GraphRAG", "SelfRAG与CorrectiveRAG", "AgenticRAG分层检索接口", "Mem0与Zep生产级记忆", "智能体长程记忆", "CHIME长程规划记忆", "持续学习"]
retrieval_cutoff: 2026-09-02
timezone: Asia/Shanghai (CST)
status: archived
arxiv: ["2502.14802", "2602.01965"]
acl: ["2026.findings-acl.290"]
code_hipporag: "https://github.com/OSU-NLP-Group/HippoRAG"
code_catrag: "https://github.com/kwunhang/CatRAG"
---

# RAG→记忆新范式：HippoRAG 2 + CatRAG

> **主要来源**：[From RAG to Memory: Non-Parametric Continual Learning for Large Language Models](https://arxiv.org/abs/2502.14802)；[Breaking the Static Graph: Context-Aware Traversal for Robust Retrieval-Augmented Generation](https://arxiv.org/abs/2602.01965)；[Breaking the Static Graph: Context-Aware Traversal for Graph-Based RAG](https://aclanthology.org/2026.findings-acl.290/)（截至 2026-09-02）。下文「HippoRAG 2」指第一篇（Gutiérrez 等，OSU / UIUC，ICML 2025；arXiv 现行 v2 2025-06-19）；「CatRAG」指后两篇（Lau 等，Huawei HKRC / HKUST / CUHK-Shenzhen；arXiv v1 2026-02-02 为唯一版本，ACL Findings 2026 正式版改了副标题）。数字除特别注明外取自 arXiv 版。
> **研究线**：架构思想（主）——开放知识图谱加个性化 PageRank（PPR）的记忆式检索、查询条件下的图遍历；评测字段（辅）——事实 / 联想 / 意义建构（sense-making）三类记忆任务，完整证据链指标 FCR 与 JSR。
> **范围与相邻笔记**：
> - ≠ [[检索增强与知识外挂]]：本篇不写稠密双塔、DPR 与向量库通史，只用「向量检索缺联想与意义建构」作对照。
> - ≠ [[图谱检索GraphRAG]]：本篇不写社区摘要与 map-reduce 全局问答；HippoRAG 2 的图用来辅助检索本身，不用摘要扩充检索语料。
> - ≠ [[SelfRAG与CorrectiveRAG]]：本篇不写反思 token 与纠错动作；CatRAG 只调整一次图边权，不做多轮生成–检索。
> - ≠ [[Mem0与Zep生产级记忆]]：本篇不写对话记忆层的接口与更新操作；对象是文档语料上的检索图算法。
>
> **意义**：HippoRAG 2 把 RAG 重新定位为大模型的「非参数持续学习」，并给出三类记忆任务的评测：它是同一组实验里唯一在简单事实、多跳联想和长篇理解上都不输最强向量检索的结构化方法，说明图结构不必以牺牲事实召回为代价。CatRAG 进一步指出，图在索引时就固定的转移概率会让检索被高连接度的「枢纽」节点吸走，改为按查询调整边权后，在 HoVer、MuSiQue 上完整证据链召回明显提高（FCR 34.8→42.5、30.5→34.6）。

**一句话**：HippoRAG 2 用「短语图 + 段落节点 + 三元组过滤 + PPR」模仿海马体的联想记忆；CatRAG 在同一张图上按查询重新分配边权，让随机游走走完整条证据链。

---

## 一、问题背景

1. **持续更新知识的三条路**（HippoRAG 2 §2.1）：继续微调会灾难性遗忘且代价高；模型编辑的修改过于局部，相关知识不随之更新；RAG 不改模型、推理时取外部信息，是可扩展的非参数路线。但标准向量 RAG 难以做到人类长期记忆的两种能力：**意义建构**（理解更大、更复杂的语境）与**联想**（在分散的事实之间建立多跳联系）。
2. **结构化 RAG 的代价**（HippoRAG 2 §1）：RAPTOR、GraphRAG、LightRAG 等用摘要树、知识图谱或社区摘要增强结构，在多跳与长篇任务上有收益，但在简单事实问答上反而不如最强的向量检索。
3. **静态图的谬误**（CatRAG §1、§3.1）：HippoRAG 2 的图转移矩阵在索引时就固定了，边的重要性与查询无关。随机游走的概率会被泛化的高权边吸走（论文例：Marie Curie → Radioactivity），并汇集到「Nobel Prize」「French」这类高连接度枢纽节点。结果是 Recall 看似不低，却常常只召回证据链的一部分。

## 二、脉络

| 时间 | 工作 | 增量 |
|---|---|---|
| 2024 | GraphRAG、RAPTOR、LightRAG | 用社区摘要、递归摘要树或图加向量增强结构；见 [[图谱检索GraphRAG]] |
| 2024-05 | [HippoRAG](https://arxiv.org/abs/2405.14831)（NeurIPS 2024） | 以海马体索引理论为隐喻：开放知识图谱加 PPR 做多跳检索，偏实体中心 |
| 2025-02 | HippoRAG 2（ICML 2025） | 段落节点嵌入图中、查询对三元组匹配、LLM 过滤三元组；补齐简单事实任务 |
| 2026-02 | CatRAG（ACL Findings 2026） | 沿用 HippoRAG 2 的图，按查询动态调整边权，主打完整证据链 |
| 2026-02 | A-RAG | 把 HippoRAG2 当作图检索强基线，转向由智能体编排检索工具；见 [[AgenticRAG分层检索接口]] |

## 三、HippoRAG 2：从 RAG 到非参数长期记忆

### 3.1 结构与隐喻（§3）

沿用 HippoRAG 的类比：大模型相当于新皮层，开放知识图谱加 PPR 相当于海马体的联想索引，编码器相当于连接两者的旁海马区域。流程分为离线建索引与在线检索。

- **离线**：用 LLM 做开放信息提取，得到三元组；三元组中的短语成为图节点，关系成为边，向量相似的短语之间加同义边。
- **在线**：用查询找到相关三元组，作为 PPR 的起点在图上扩散，按最终分数取段落交给阅读模型作答。

### 3.2 相对 HippoRAG 的三处改进（§3.2–3.5）

| 改进 | 做法 | 解决什么 |
|---|---|---|
| 稠密–稀疏融合 | 新增段落节点，用「contains」上下文边连到该段提取出的短语 | HippoRAG 只在分数层面融合段落；现在段落本身进入图结构 |
| 更深的语境化 | 用整个查询去匹配三元组（query-to-triple），而不是先做命名实体识别再匹配节点 | 实体中心的匹配丢掉了查询中的上下文信号 |
| 识别记忆 | 向量检索取 top-$k$ 三元组后，由 LLM 过滤掉无关三元组 | 减少 PPR 起点中的噪声 |

在线检索时，过滤后的短语节点和**所有**段落节点都作为起点，段落节点的重置概率按向量相似度设定并乘以权重 0.05（Table 5 的折中值）。论文称更宽的起点有利于多跳。

### 3.3 关键结果（§5–6）

实验用 Llama-3.3-70B-Instruct 做信息提取、三元组过滤与阅读，NV-Embed-v2 做检索器；结构化基线都用同一提取模型与检索器复现。

QA F1（Table 2，节选）：

| 检索方式 | NQ | MuSiQue | 2Wiki | NarrativeQA | 七项平均 |
|---|---:|---:|---:|---:|---:|
| NV-Embed-v2 | 61.9 | 45.7 | 61.5 | 25.7 | 57.0 |
| GraphRAG | 46.9 | 38.5 | 58.6 | 23.0 | 49.6 |
| HippoRAG | 55.3 | 35.1 | 71.8 | 16.3 | 53.1 |
| HippoRAG 2 | 63.3 | 48.6 | 71.0 | 25.9 | 59.8 |

- GraphRAG、RAPTOR、LightRAG 的平均分都低于 NV-Embed-v2；HippoRAG 2 是表中唯一在七个数据集上都高于 NV-Embed-v2 的结构化方法。摘要称它在联想任务上比最强向量模型提升约 7%。
- 检索 Recall@5 平均 78.2，对比 NV-Embed-v2 的 73.4；2Wiki 上 90.4 对 76.5。
- 消融（Table 4，多跳平均 Recall@5）：完整方法 87.1；改回实体匹配节点降到 74.6，去掉段落节点 81.0，去掉三元组过滤 86.4。论文称 query-to-triple 比实体匹配平均提升 12.5%。
- 换用 GTE-Qwen2、GritLM 等检索器，HippoRAG 2 相对纯向量检索的提升依然存在（Table 7）。
- 在 NQ 与 MuSiQue 的分批增量语料模拟中（Fig.3），相对 NV-Embed-v2 的优势保持稳定，但随语料增长，两者在联想任务上以相近速度下降。

## 四、CatRAG：按查询调整图遍历

### 4.1 三种机制（§3.2–3.5）

图结构沿用 HippoRAG 2（短语节点与段落节点，关系、同义、上下文三类边）。PPR 迭代为 $v^{(k+1)}=(1-d)\,e_s+d\,v^{(k)}T$，CatRAG 的目标是把固定的转移矩阵 $T$ 换成随查询变化的 $\hat T_q$。

| 机制 | 做法 | 成本 |
|---|---|---|
| 符号锚定 | 把查询中识别出的实体作为弱起点，以小概率 $\epsilon$ 重置，牵制随机游走不要漂向枢纽 | 很低 |
| 查询感知的动态边权 | 先按拓扑粗剪，再让 LLM 给起点出发的边打相关性分，用分数乘原始边权 | 需要在线调用 LLM，是主要开销 |
| 关键事实段落加权 | 若某条上下文边被过滤后的种子三元组支持，就放大该边权重 | 不需要额外 LLM 调用 |

默认设置（§4.4）：$\epsilon=0.2$、放大系数 $\beta=2.5$、每次最多 5 个种子与 15 条边参与打分；打分 LLM 为 GPT-4o-mini；检索器刻意用较小的 text-embedding-3-small，以便单独衡量拓扑上的增益；主要对照是同一套组件复现的 HippoRAG 2。

### 4.2 完整证据链指标（§4.3）

- **FCR**（Full Chain Retrieval）：检索结果覆盖**全部**标准支持文档的查询比例。
- **JSR**（Joint Success Rate）：既满足 FCR、答案又正确的比例，对应 FEVER / HoVer 的严格口径。

数据为 MuSiQue、2Wiki、HotpotQA 各 1,000 题，以及 HoVer 的 1,000 条 3–4 跳声明核查。

### 4.3 关键结果（Table 2–4、§6.1）

| 方法 | 指标 | MuSiQue | 2Wiki | HotpotQA | HoVer |
|---|---|---:|---:|---:|---:|
| HippoRAG 2 | Recall@5 | 61.4 | 85.9 | 87.1 | 71.2 |
| CatRAG | Recall@5 | 64.9 | 87.0 | 89.5 | 76.8 |
| HippoRAG 2 | FCR / JSR | 30.5 / 21.5 | 66.1 / 53.0 | 75.5 / 53.4 | 34.8 / 26.2 |
| CatRAG | FCR / JSR | 34.6 / 24.3 | 67.6 / 55.0 | 80.4 / 56.8 | 42.5 / 31.1 |

- 常规 Recall 只是温和提升，完整性指标拉开得更多：HoVer 上 JSR 从 26.2 到 31.1，论文称相对提升 18.7%。QA 上 CatRAG 在四个数据集上都略高于 HippoRAG 2（如 MuSiQue F1 45.0 对 43.2）。
- 枢纽分析（100 条 MuSiQue 抽样）：PPR 加权的平均节点强度从 837.0 降到 761.7，前 1% 超级枢纽占的概率质量从 45.7% 降到 42.5%。
- 消融（Table 5）：去掉符号锚定在 HoVer 上掉得最多（76.8→73.6）；去掉关键事实加权在 2Wiki 上反而略升，论文称该机制主要对非结构化语料有用。

## 五、两篇对照

| 维度 | HippoRAG 2 | CatRAG |
|---|---|---|
| 要解决的问题 | 结构化 RAG 伤事实记忆，需要事实、联想、意义建构三类都不输 | 固定转移矩阵导致漂移与枢纽偏向，部分召回不等于完整证据链 |
| 图的角色 | 开放知识图谱辅助检索 | 同一张图，按查询改转移概率 |
| 在线 LLM | 过滤三元组 | 过滤三元组之外，再给出边打分 |
| 主表检索器 | NV-Embed-v2 | text-embedding-3-small（隔离拓扑增益） |
| 主要指标 | 三类任务的 F1 与 Recall@5 | FCR / JSR |

两篇的检索器不同，CatRAG 表里的 HippoRAG 2 分数不能与 HippoRAG 2 原文的分数直接比较。

## 六、意义

- **结构化与事实召回可以兼得**：HippoRAG 2 表明，图只要用来辅助检索而不是替代原文，就能在多跳任务上获益而不损失简单事实问答。
- **把 RAG 当作记忆来评测**：事实、联想、意义建构三分法和增量语料模拟，使 RAG 评测从单一问答准确率扩展到记忆能力。
- **完整性比召回更能暴露问题**：CatRAG 用 FCR / JSR 表明，常规 Recall 会掩盖证据链断裂，而按查询调整图遍历能补上一部分。

## 七、局限与待核实

- **检索器不同不可混比**：两篇主表的检索器不同，跨篇比较绝对分数没有意义。
- **在线 LLM 开销**：CatRAG 的动态边权需要运行时调用 LLM。ACL 版新增的效率分析（ACL 版 §6.2、Table 6，MuSiQue）显示检索约慢 2.6 倍，每次查询多约 4.8 秒、多约 0.0015 美元。
- **基线随版本变化**：ACL 版新增 PropRAG、LightRAG、HyperGraphRAG 等基线，CatRAG 自身数字与 arXiv 版相同；但在新增基线下它不再全部最好，例如 PropRAG 在 MuSiQue F1（46.1 对 45.0）、HotpotQA Recall@5（90.0 对 89.5）与 HotpotQA FCR / JSR（81.0 / 58.2 对 80.4 / 56.8）上更高。
- **代码并非论文原版**：CatRAG 论文称因专有数据政策不能公开完整源码，只给超参数表；GitHub 仓库是 2026-08-20 发布的复现实现，与论文原实现的差异未核对。
- **上限未测**：CatRAG 刻意用较小的检索器，换更强编码器后的绝对水平未知。
- **待核实读图**：HippoRAG 2 增量语料模拟（Fig.3）与 CatRAG 枢纽强度分布（Fig.2）只取论文文字描述，未读图取点。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[检索增强与知识外挂]] | 那篇是 RAG 通史与共用背景；两篇论文都以向量检索为主要对照，并指出它缺联想与意义建构 | 稠密双塔、向量库选型 |
| [[图谱检索GraphRAG]] | GraphRAG 是 HippoRAG 2 主表的结构化基线；区别在于 GraphRAG 用图生成摘要扩充语料，HippoRAG 2 用图直接辅助检索（§2.2） | 社区摘要、map-reduce、EraRAG 增量索引 |
| [[SelfRAG与CorrectiveRAG]] | CatRAG 把 Self-RAG、IRCoT 归为多轮迭代检索，认为延迟高，自己改为一次性调整边权后单次遍历（§2.3） | 反思 token、纠错动作 |
| [[AgenticRAG分层检索接口]] | A-RAG 用 HippoRAG2 作图检索基线，并在多数数据集上超过它；两篇代表「索引侧更聪明」与「接口侧更自主」两条路线 | 分层工具与智能体环 |
| [[Mem0与Zep生产级记忆]] | 同样以「长期记忆」为目标，但那篇是对话与业务记忆的写入、更新服务，本篇是文档语料上的检索图 | 记忆操作接口、时序知识图谱 |
| [[智能体长程记忆]] | 那篇写 MemGPT 分页与 A-Mem 卡片盒式记忆，本篇走检索图路线，两者同问「长期记忆怎样组织与取回」 | 分页与记忆演化 |
| [[CHIME长程规划记忆]] | 同属不改模型参数、只更新外部存储的非参数记忆：本篇把文档语料写成知识图谱供检索，那篇把智能体轨迹提炼成规划与执行经验，并按信用归因决定写入哪条 | 轨迹经验库与信用归因 |
| [[持续学习]] | 那篇的综述把检索列为持续学习的「外部知识」路线；HippoRAG 2 正是把 RAG 定位为非参数持续学习 | 持续学习的参数路线 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [HippoRAG 2](https://arxiv.org/abs/2502.14802) §3 | 离线建图、在线检索与三处改进 |
| 2 | [CatRAG（arXiv）](https://arxiv.org/abs/2602.01965) §3 | 静态图谬误与三种机制 |
| 3 | [CatRAG（ACL Findings 2026）](https://aclanthology.org/2026.findings-acl.290/) §5–6 | 新增基线与效率分析 |
| 4 | [HippoRAG](https://arxiv.org/abs/2405.14831) | 前作与海马体索引隐喻 |
| 5 | [OSU-NLP-Group/HippoRAG README](https://github.com/OSU-NLP-Group/HippoRAG) | HippoRAG 2 代码 |
| 6 | [kwunhang/CatRAG README](https://github.com/kwunhang/CatRAG) | CatRAG 复现实现与 HoVer 数据 |
