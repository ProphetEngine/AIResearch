---
title: "RAG 2.0 变体：Self-RAG + Corrective RAG（相对 B6 / ≠ 8）"
topic: SelfRAG与CorrectiveRAG
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2310.11511
 - https://arxiv.org/abs/2401.15884
arxiv: ["2310.11511", "2401.15884"]
related: ["B6", "图谱检索GraphRAG", "智能体工具与长程任务", "长上下文位置编码与系统侧"]
code:
 - https://github.com/AkariAsai/self-rag
 - https://github.com/HuskyInSalt/CRAG
archived: 2026-09-22
---

# RAG 2.0 变体：Self-RAG + Corrective RAG（相对 B6 / ≠ 8）

> **定位**：[[SelfRAG与CorrectiveRAG]] **P1**——相对 `B6`（Lewis 检索–生成通史）与 [[图谱检索GraphRAG]]（GraphRAG 社区摘要 + EraRAG 增量索引）的 **两条 agentic RAG 机制线**：**检索必要性自省（Self-RAG）** 与 **检索结果纠错 / 回退 Web（CRAG）**。
> **攻坚线**：**架构思想（主）**——reflection tokens / 三动作触发；**评测字段（辅）**——幻觉/接地（FactScore、citation prec/rec、短答 accuracy）。
> **硬划界（禁止重写）**：
> - **禁止重写** `B6` 的稠密检索 / DPR 双塔 / MIPS / RAG-Token vs RAG-Sequence / 向量库产品对照。本篇只用「**固定 top-K 无差别塞入**」这一对照槽。
> - **禁止重写** [[图谱检索GraphRAG]] 的实体图谱 → Leiden 社区摘要 → map-reduce，或 EraRAG 增量重建。本篇 **不是** 图索引。
> - **禁止重写** [[长上下文位置编码与系统侧]] 长上下文窗口外推；本篇仍是 **库外检索环**，只改「何时取 / 取到坏结果怎么办」。
> **禁止编造**：机制、表数字一律锚定官方 PDF（2026-09-22 CST）。图内未抽出的精确曲线点标 **待核实读图**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 | 角色 |
|---|---|---|---|
| **主文·自省** | Asai, Wu, Wang, Sil & Hajishirzi, *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection* | arXiv:**2310.11511v1** \[cs.CL\] **17 Oct 2023**；`https://arxiv.org/abs/2310.11511`（**30** 页 letter；CreationDate **2023-10-19** CST；1,405,127 bytes；页眉 *Preprint*） | reflection tokens；按需检索；ISREL / ISSUP / ISUSE；段级 beam |
| **主文·纠错** | Yan, Gu, Zhu & Ling, *Corrective Retrieval Augmented Generation* | arXiv:**2401.15884v3** \[cs.CL\]（published **29 Jan 2024**，updated **7 Oct 2024**）；`https://arxiv.org/abs/2401.15884`（**16** 页 A4；CreationDate **2024-10-08** CST；667,756 bytes） | 轻量检索评估器；Correct / Incorrect / Ambiguous；Web 回退；decompose-then-recompose |
| **辅·代码（文内）** | Self-RAG：`https://github.com/AkariAsai/self-rag`（摘要自报 selfrag.github.io）；CRAG：`https://github.com/HuskyInSalt/CRAG` | 复现入口；本笔记不展开仓库提交史 | |

**一句话抓手：**
- **Self-RAG**：把「要不要检索、这段证据是否相关、生成是否被证据支持、整体是否有用」写成 **可被同一 LM 预测的特殊 token**，推理时按需检索并用 critique 分数重排。
- **CRAG**：承认「检索已经发生且可能全错」——用轻量评估器给置信度，再 **精炼库内 / 丢弃并搜 Web / 两者混合**，可插到标准 RAG 或 Self-RAG 上。

---

## 二、议题边界：相对 B6 / [[图谱检索GraphRAG]] 只取接口

### 2.1 相对已入库只取接口

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **B6 Lewis RAG** | 「库外非参数记忆 + 条件生成」；固定 top-K 可能塞入无关段落 | DPR/MIPS 细节、RAG-Token/Sequence、稠密–稀疏混合、向量库选型通史 |
| **B6「Agentic RAG 名录待核实」** | 本篇用两篇一手 PDF **填上**「自省检索」与「纠错回退」两槽 | 不另编造产品清单或未核论文 |
| **[[图谱检索GraphRAG]] GraphRAG / EraRAG** | 「检索失败模式可换路线」的相邻直觉一句 | 社区摘要、Leiden、LSH 增量重建 |
| **[[长上下文位置编码与系统侧]] 长上下文** | 窗口装不下整库 → 需要外挂环 | YaRN / 稀疏注意力 / lost-in-middle |
| **[[智能体工具与长程任务]] 工具环** | 「何时调用外部知识源」可对照 | MCP / 长程 harness 全文 |

### 2.2 问题立轴（跟读）

`
B6 向量 RAG： 永远 retrieve top-K → 整段塞进生成器
 ✗ 检索未必需要；✗ top-K 可能全错 / 噪声大；✗ 模型未训「跟证据走」

Self-RAG： 每段先预测 Retrieve ∈ {yes,no,continue}
 → 需要则取 K 篇，并行生成，再发 ISREL / ISSUP / ISUSE 自省
 → 用 critique 概率做段级重排 / 硬过滤

CRAG： 检索已发生 → 轻量评估器打分 → 动作三选一
 Correct：库内 decompose→filter→recompose
 Incorrect：丢弃库内 → query rewrite → Web search → 再精炼
 Ambiguous：库内精炼 ⊕ Web 外部知识
`

Self-RAG Abstract 要点：无差别固定篇数检索会损害多样性或引入无关段落；生成也不保证与证据一致。
CRAG Abstract / §1 要点：RAG 效果高度依赖检索相关性；若检索失败，无关信息会误导生成——需 **纠错策略**，而非只问「要不要检索」。

---

## 三、Self-RAG：检索必要性自省 + reflection tokens

### 3.1 四类 reflection tokens（Table 1）

| Type | 输入 | 输出取值 | 定义（文内） |
|---|---|---|---|
| **Retrieve** | $x$ / $x,y$ | `{yes, no, continue}` | 是否调用检索器 $R$ |
| **ISREL** | $x, d$ | `{relevant, irrelevant}` | 段落 $d$ 是否对解题 $x$ 有用 |
| **ISSUP** | $x, d, y$ | `{fully supported, partially supported, no support}` | $y$ 中可核验陈述是否被 $d$ 支持 |
| **ISUSE** | $x, y$ | `{5,4,3,2,1}` | $y$ 对 $x$ 的整体有用性（与是否检索无关的「感知效用」） |

后三类为 **Critique**；文内加粗最理想取值：Relevant / fully supported / 高 utility。

**段单位：** 实验默认 **一句 = 一段**；框架可换更小单位（§3.1 脚注）。

### 3.2 推理环（Algorithm 1 / Fig.1）

对输入 $x$ 与已生成前缀 $y_{<t}$：

1. **预测 Retrieve**。
2. 若 **Yes**：$R$ 取相关段落集 $D$；对每个 $d\in D$，模型预测 **ISREL**、下一段 $y_t$、再预测 **ISSUP** 与 **ISUSE**；按三类 critique 分数排序候选。
3. 若 **No**：直接生成 $y_t$ + **ISUSE**（标准 LM 路径）。

并行处理多段落；可用 **软约束**（加权和）或 **硬过滤**（如 ISSUP=no support 直接丢掉该段候选）。

### 3.3 训练：Critic $C$ → Generator $M$（§3.2）

`
GPT-4 少样本标注 reflection tokens（每类约 4k–20k）
 │
 ▼
Critic C（Llama2-7B 初始化）← 只学预测 reflection token（Eq.1）
 │ 文称多数类别与 GPT-4 一致率 >90%（Appendix Table 5）
 ▼
离线插入：Retrieve / <p>…</p> / ISREL / 文本 / ISSUP / … / ISUSE
 │
 ▼
Generator M（Llama2-7B/13B）← 标准 next-token（Eq.2）
 │ 训练时 mask 掉 <p>…</p> 检索块的 loss
 ▼
推理：不再依赖 C；M 自己发 reflection tokens
`

与 PPO-RLHF 对照（文内）：critique **离线插入语料**，用标准 LM 目标，避免在线 PPO；代价是依赖 GPT-4 蒸馏标签。

**数据规模（§4.3）：** 约 **150k** instruction-output 对（Open-Instruct 子集 + 知识密集型集）。
**检索器默认：** Contriever-MS MARCO；训练侧可取至多 **10** 篇；推理默认 top **5**（传记 / 开放域 QA 另加 Web 搜的 top 5；ASQA 用作者提供的 GTR-XXL top 5）。

### 3.4 推理可控（§3.3）

| 旋钮 | 机制 | 默认（§4.3） |
|---|---|---|
| **自适应阈值** | $P(\texttt{Retrieve=Yes})$ 归一化后过阈值才检索 | 多数任务 **0.2**；ALCE/ASQA 因引用需求设 **0**（总是倾向检索） |
| **critique 权重** | $S = \sum_G w_G s^G_t$，$s^G$ = 最理想 token 的归一化概率 | $w_{\mathrm{ISREL}}=1.0,\ w_{\mathrm{ISSUP}}=1.0,\ w_{\mathrm{ISUSE}}=0.5$ |
| **段级 beam** | 每段对 $K$ 篇并行候选，beam width $B$ | $B=2$；token 级 greedy |
| **硬约束** | 生成不良 critique 时过滤该候选 | 可选；无需再训即可改行为 |

跟读口诀：**事实任务抬 ISSUP / 检索频率；开放写作抬 ISUSE、压检索。**

### 3.5 主结果切片（Table 2，非专有模型最优加粗口径）

任务：PopQA / TriviaQA（短答 acc）；PubHealth / ARC-Challenge（闭集 acc）；Biography FactScore；ASQA（em / rouge / MAUVE / citation prec·rec）。

| 模型 | PopQA | TQA | Pub | ARC | Bio FS | ASQA prec | ASQA rec |
|---|---:|---:|---:|---:|---:|---:|---:|
| ChatGPT（无检索） | 29.3 | 74.3 | 70.1 | 75.3 | 71.8 | – | – |
| Ret-ChatGPT | 50.8 | 65.7 | 54.7 | 75.3 | – | 65.1 | 76.6 |
| Llama2-FT 7B + 检索 | 48.7 | 57.3 | 64.3 | 65.8 | 78.2 | 5.0 | 7.5 |
| **Self-RAG 7B** | **54.9** | 66.4 | **72.4** | 67.3 | **81.2** | **66.9** | 67.8 |
| **Self-RAG 13B** | **55.8** | **69.3** | **74.5** | **73.1** | 80.2 | **70.3** | **71.3** |

要点（§5.1）：
- 7B/13B 在 PubHealth、PopQA、Bio、ASQA（rouge/MAUVE）等上可 **超过 ChatGPT（无检索）**；引用 **precision** 可超过 Ret-ChatGPT。
- 许多「LM+检索」基线在 PubHealth / ARC 上相对无检索 **提升有限**——说明问题不只是「有没有检索」，而是 **是否学会用证据**。
- 事实精度上 7B 偶发优于 13B：文称较小模型更常产出 **更短、更贴证据** 的输出。

消融方向（文内摘要，细表见图/附录，精确点 **待核实读图**）：无 Critic、无 Retriever、关掉自适应检索等会掉点；critique 权重可在 ASQA 上权衡 citation precision vs MAUVE。

---

## 四、CRAG：检索纠错 + Web 回退

### 4.1 与 Self-RAG 的分工（§2 / §4.1）

| | **Self-RAG** | **CRAG** |
|---|---|---|
| 核心问题 | **何时**检索；生成是否被证据支持 | 检索 **已经发生** 且可能 **全错** 时怎么办 |
| 主要装置 | 同一 LM 的 reflection tokens（需指令微调） | **轻量评估器**（T5-large，文称 **0.77B**）+ 动作机 |
| 外部知识 | 部分任务推理侧可加 Web top-5（实验设定） | **Incorrect / Ambiguous** 显式触发 **大规模 Web search** |
| 耦合方式 | 端到端训生成器 | **plug-and-play**：接到标准 RAG 或 Self-RAG（→ Self-CRAG） |

CRAG 文内自述：相关工作多在问「要不要检索 / 怎么当工具用」；本文 **首次系统做 RAG 纠错策略**（§2 末）。

### 4.2 检索评估器（§4.2）

- 初始化：**T5-large**；参数远小于 Llama 级 critic。
- 输入：每个 `(query, document)` **单独**打相关性分；默认约 **10** 篇检索结果（与 Self-RAG 提供的 Contriever 结果对齐以便可比）。
- 监督信号：如 PopQA 的 wiki subject 标题追到「非 100% 相关但高质量」正例；负例从检索结果随机采「看起来像但无关」的。
- 对照：提示 ChatGPT 做相关性判断 **不如** 该微调评估器（§5.5，细节见原文）。

### 4.3 三动作触发（§4.3 / Algorithm 1）

设上下阈值：

| 动作 | 触发条件 | 知识路径 |
|---|---|---|
| **Correct** | **至少一篇**分高于上阈值 | `Knowledge_Refine(x, D)` → 内部知识 $k_{in}$ |
| **Incorrect** | **全部**分低于下阈值 | 丢弃 $D$；query **rewrite** → **Web_Search** → 精炼 → $k_{ex}$ |
| **Ambiguous** | 中间带 | $k_{in} + k_{ex}$ 拼接 |

生成器 $G$ 只看优化后的 $k$，**任意**生成 LM 可接（无需会发 reflection token）。

**为何要 Ambiguous：** 仅 Correct/Incorrect 的硬切换让系统过度依赖评估器准确率；中间带把「不确定」变成 **双源互补**（§4.3 Discussion）。

### 4.4 decompose-then-recompose（§4.4）

对判定相关的文档：

1. **Decompose**：切成 knowledge strips（一两句可整段保留；更长则按长度切成数句级单元）。
2. **Filter**：同一评估器对 strip 再打分，滤掉无关条。
3. **Recompose**：按序拼接 → **internal knowledge**。

目的：即使「文档级相关」，内部仍有噪声条——避免整篇灌进上下文。

### 4.5 Web search 回退（§4.5）

- 动机：静态有限语料只能返回次优文档；系统应能承认「库内不够」并外求。
- 实现要点：对 query **改写**后调 **商业 Web Search API**（脚注：本研究用 **Google Search API**）拿 URL；抓取页面文本；**同一套** decompose-then-recompose 得到 **external knowledge**。
- 偏好：权威受监管站点（如 Wikipedia）以降偏置 / 不可靠信息风险（文内声明；非完整内容安全方案）。

跟读口诀：**Incorrect = 别死磕坏检索；Ambiguous = 库内精炼 ⊕ Web；Correct = 只精炼不外逃。**

### 4.6 主结果切片（Table 1）

数据集：PopQA（acc）、Biography（FactScore）、PubHealth（acc）、Arc-Challenge（acc）。
命名：接到标准 RAG → **CRAG**；接到 Self-RAG → **Self-CRAG**。

**底层 SelfRAG-LLaMA2-7b（与 Self-RAG 论文同族）：**

| Method | PopQA | Bio FS | Pub | ARC |
|---|---:|---:|---:|---:|
| RAG | 52.8 | 59.2 | 39.0 | 53.2 |
| CRAG | 59.8 | 74.1 | **75.6** | **68.6** |
| Self-RAG | 54.9 | 81.2 | 72.4 | 67.3 |
| **Self-CRAG** | **61.8** | **86.2** | 74.8 | 67.2 |

文内相对该底层 RAG 的增益口径（§5.3）：PopQA **+7.0**、Bio FS **+14.9**、PubHealth **+36.6**、Arc **+15.4**（百分点）。
相对 Self-RAG：Self-CRAG 在 PopQA **+6.9**、Bio **+5.0**、Pub **+2.4**（同段叙述；ARC 上 Self-CRAG 67.2 vs Self-RAG 67.3，基本持平）。

**底层 LLaMA2-hf-7b（未学 reflection token）：**

| Method | PopQA | Bio FS | Pub | ARC |
|---|---:|---:|---:|---:|
| RAG | 50.5 | 44.9 | 48.9 | 43.4 |
| CRAG | **54.9** | 47.7 | **59.5** | **53.7** |
| Self-RAG*（作者复现） | 29.0 | 32.2 | 0.7 | 23.9 |
| Self-CRAG | 49.0 | 69.1 | 0.6 | 27.9 |

文内解释：Self-RAG **依赖** reflection-token 指令微调；换到普通 hf-7b 时能力坍塌，而 CRAG **不要求**该能力，换生成器更灵活。\* 行为作者复现，与官方 Self-RAG-7B 表数字不同——跟读时 **分栏，勿混用**。

### 4.7 消融（Table 2 / 3，PopQA acc）

**去动作（SelfRAG-LLaMA2-7b 上的 CRAG 59.8）：**
w/o Correct 58.3；w/o Incorrect 59.5；w/o Ambiguous 59.0 → 三者都贡献。

**去利用步骤（同设定）：**
w/o refinement 54.2；w/o rewriting 56.2；w/o selection 58.6 → 精炼与改写更关键。

（LLaMA2-hf-7b 列同见表；Self-CRAG 在 hf-7b 上对 refinement/selection 更敏感，如 w/o selection 掉到 24.9——说明坏 Web/坏条过滤在弱生成器上伤害更大。）

---

## 五、两条线如何拼进「生产 agentic RAG」

`
用户 query
 │
 ├─【Self-RAG 轴】需要检索吗？ → Retrieve token / 阈值
 │ │
 │ ▼ 取 top-K
 │
 ├─【CRAG 轴】这批结果整体可信吗？ → Correct / Incorrect / Ambiguous
 │ │
 │ ├─ Correct → strip 精炼
 │ ├─ Incorrect → Web 回退精炼
 │ └─ Ambiguous → 库内 ⊕ Web
 │
 └─ 生成（可再跑 ISSUP/ISUSE 或引用约束）
`

| 生产直觉 | Self-RAG 贡献 | CRAG 贡献 |
|---|---|---|
| 省检索 / 保创意任务 | 按需 Retrieve=No | （假设已检索）不替代「不检索」决策 |
| 证据接地 | ISSUP + 段级重排 | strip 过滤噪声 |
| 库内 miss / 过时 | 实验侧可加 Web top-5，但不是纠错机 | **Incorrect → Web** 显式纠错 |
| 换底座 LM | 需再训 / 蒸馏 reflection | 评估器独立，生成器可换 |

**与 B6 / [[图谱检索GraphRAG]] 的最终划界一句：** B6 回答「为何外挂索引」；[[图谱检索GraphRAG]] 回答「全局主题问句与增长语料怎么建图索引」；本篇回答「**环上的控制流**——何时取、取坏了怎么纠」。

---

## 六、误区（跟读时主动避开）

1. **「Self-RAG = 普通 RAG + 多检几篇」**
 关键是 **同一 LM 学会发 Retrieve/Critique 特殊 token**，并能在推理期改权重/硬过滤。

2. **「CRAG = 再训一个 Self-RAG」**
 CRAG 是 **检索后动作机 + 轻量评估器**；可不碰生成器的 reflection 词表。

3. **「有了自省就不会幻觉」**
 两文都仍依赖检索器质量、评估器阈值与 Web 噪声；CRAG 明确警告大规模 Web 可引入偏置。

4. **「Incorrect 就是再 embedding 一次同一库」**
 文内 Incorrect 是 **丢弃当前检索** 并 **改写后搜 Web**，不是同库重排通史（重排通史归 B6，本篇不写）。

5. **「本篇该写 FAISS / 向量库选型 / 社区摘要」**
 **禁止**——分别归 B6 / [[图谱检索GraphRAG]]。

6. **「把 CRAG Table 1 的 Self-RAG*（hf-7b 复现）当成官方 Self-RAG-7B」**
 分栏：官方 54.9/81.2/72.4/67.3；\* 复现 29.0/32.2/0.7/23.9。

7. **「Agentic RAG 产品清单可以凭记忆补全」**
 本篇只核这两篇一手 PDF；其余名录仍 **待核实**。

---

## 七、待核实

1. Self-RAG 后续正式发表版本（若有 ICLR 相机稿）与本地 **v1 Preprint** 数字差异——本笔记锚定 `2310.11511v1` PDF。
2. Self-RAG 消融图（检索频率–准确率、权重–citation/MAUVE）的精确点值： 对图不可靠。
3. CRAG 评估器上下阈值的具体数值、Google API 调用限额：正文 Algorithm 只给逻辑，细参见 Appendix（本卡未逐条抄附录超参表）。
4. CRAG §5.5 ChatGPT-as-evaluator 的完整数字表。
5. 与当代商业「agentic RAG」编排产品的一一对应——禁止编造；仅保留机制接口。

---

## 八、引用

### 8.1 本议题主源

- Asai, A., Wu, Z., Wang, Y., Sil, A., & Hajishirzi, H. (2023). *Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection*. arXiv:2310.11511v1.
 - https://arxiv.org/abs/2310.11511
 - 本地：`https://arxiv.org/abs/2310.11511`
 - 代码（文内）：https://github.com/AkariAsai/self-rag

- Yan, S.-Q., Gu, J.-C., Zhu, Y., & Ling, Z.-H. (2024). *Corrective Retrieval Augmented Generation*. arXiv:2401.15884v3.
 - https://arxiv.org/abs/2401.15884
 - 本地：`https://arxiv.org/abs/2401.15884`
 - 代码（文内）：https://github.com/HuskyInSalt/CRAG

### 8.2 划界与交叉（已有笔记）

- 经典 RAG / 知识外挂：检索与知识/检索增强与知识外挂.md
- GraphRAG + 增量索引：检索与知识/图谱检索GraphRAG.md
- 长上下文：架构/注意力与长上下文/长上下文位置编码与系统侧.md
- 智能体工具环：Harness/智能体与工具/智能体工具与长程任务.md
- [[MOC_检索与知识]]

### 8.3 文中点到、未全文深读

- Lewis et al., RAG，arXiv:2005.11401（→ B6）
- Contriever / Izacard et al.；FactScore（Min et al.）；ALCE-ASQA（Gao et al.）
- SAIL、Toolformer、Active RAG（Jiang et al.）——仅作相关工作坐标

---

## 九、一句话收束

**Self-RAG** 把「要不要检索、证据是否相关/是否支持、回答是否有用」收成可推理期调控的 **reflection tokens**；**CRAG** 在检索已发生后用轻量评估器触发 **精炼 / Web 纠错 / 双源混合**，并可插到标准 RAG 或 Self-RAG 上。二者相对 B6 补的是 **控制流与鲁棒性**，相对 [[图谱检索GraphRAG]] 补的是 **非图索引的 agentic 环**——不是向量库通史，也不是社区摘要。

---

*起草：AI研究会·攻坚研究员执行助手 · 2026-09-22 17:15 CST（Asia/Shanghai）· status: draft · 据官方 PDF/；禁止编造；≠ B6 向量通史 / ≠ [[图谱检索GraphRAG]] 图谱社区摘要*

## 相关笔记

- [[恶意软件分析评测|Malware Analysis Evals]]
- [[LLM水印|LLM Watermarking]]
- [[持续学习|Continual Learning LLM]]
- [[SelfRAG与CorrectiveRAG|Self-RAG / CRAG]]
- [[MMMU多模态推理基准|MMMU-Pro]]

