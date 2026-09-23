---
title: "可解释电路新方法：CircuitLasso + Anthropic Circuit Tracing（≠ RepE）"
topic: CircuitLasso与电路追踪
date: 2026-09-22
lines: [架构思想, 方法接口, 干预 faithfulness 字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.16939 # 1.42MB / 19p（主 A）
urls:
 - https://arxiv.org/abs/2606.16939
 - https://arxiv.org/pdf/2606.16939
 - https://transformer-circuits.pub/2025/attribution-graphs/methods.html
 - https://transformer-circuits.pub/2025/attribution-graphs/biology.html
arxiv: ["2606.16939"] # Anthropic 两篇 HTML：禁止虚构 arXiv 号
related:
 - "机制可解释性入门"
 - "审慎对齐与断路器"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 可解释电路新方法：CircuitLasso + Anthropic Circuit Tracing（≠ RepE）

> **定位**：**可解释横切**——仓库已有 **[[机制可解释性入门]]**（特征→电路→归因图的 **MI 入门史**）与 **[[激活操控与表征工程]]**（**RepE / 推理期激活加向量**）。本卡立「**如何规模化发现与验证机制电路**」方法篇，两条正交接口：
> - **CircuitLasso**（Yin, Wei, Gao, Dhurandhar, Natesan Ramamurthy, Yu；arXiv:**2606.16939v1**）：用 **观测式稀疏线性回归（Lasso）** 在神经元 / SAE 特征上恢复依赖骨架；宣称与干预式基线 **结构精度持平、算力更低**，并扩到高维 SAE。
> - **Anthropic Circuit Tracing / attribution graphs**（Ameisen et al.，*Transformer Circuits Thread*，**2025-03-27**）：用 **cross-layer transcoder（CLT）→ replacement model → 逐提示归因图**，再以干预检验机理；**Biology** 同伴文把同套方法落到 Claude 3.5 Haiku 多行为案。
> **攻坚线**：**架构思想 / 方法接口（主）**——观测稀疏回归 vs 可替换模型上的线性归因；**干预 faithfulness 字段（辅）**——InterpBench SHD/runtime、CoLA faithfulness/completeness、CLT 重构/L0、节点→logit / 特征→特征影响相关、局部替换模型扰动一致性。
> **硬划界（开篇钉死）**：
> - **≠ [[激活操控与表征工程]]（RepE / Activation Steering）**：本卡 **不** 主写推理期「加/减概念向量」操控行为；只在对照句点出「读表征」与「发现电路」正交。禁止把 CircuitLasso / 归因图写成 ActAdd/CAA/ITI 续作。
> - **≠ [[机制可解释性入门]]（MI 通史）**：禁止重写 polysemanticity → SAE → sparse feature circuits 的 **入门阶梯叙事**；[[机制可解释性入门]] 已立概念骨架与 Circuit Tracing **证据结构摘要**。本卡下沉到 **可扩展电路学习算法接口 + 归因图方法细节与 faithfulness 字段**。
> - **≠ [[审慎对齐与断路器]]（Deliberative Alignment + Circuit Breakers）**：[[审慎对齐与断路器]] 的「circuit」是 **安全产品 / Representation Rerouting 熔断**；本卡「circuit」是 **机制可解释性子图**。禁止把熔断训练写成电路发现。
> **禁止编造**：主张、表号、百分比、页数一律锚定官方 PDF与 2026-09-22 CST 抓取的官方 HTML；**Anthropic 两文无 arXiv PDF → 禁止虚构 arXiv 号**。

---

## 一、材料元信息

| 角色 | 标识 | 一手形态 | 本地 | 体积 | 页数 / 日期 | 备注 |
|---|---|---|---|---|---|---|
| **主 A** | Yin et al., *Scalable Circuit Learning for Interpreting Large Language Models*（CircuitLasso） | arXiv:**2606.16939v1** \[cs.LG\] **Submitted 15 Jun 2026**；MI Workshop @ ICML 2026 | `https://arxiv.org/abs/2606.16939` | **1.42MB**（1,490,729 B） | **19** 页 letter | **官方 HTTPS 外链**（≪10MB） |
| **主 B** | Ameisen, Lindsey, Pearce, Gurnee, Turner, Chen, Citro et al., *Circuit Tracing: Revealing Computational Graphs in Language Models* | **官方 HTML**（**无 arXiv PDF**）；Published **March 27, 2025** | `{html,txt}` | HTML **271K** / txt **191K** | HTML 方法页 | **正式外链**；**禁止虚构 arXiv** |
| **补链 C** | Lindsey, Gurnee, Ameisen et al., *On the Biology of a Large Language Model* | **官方 HTML**；Published **March 27, 2025**（methods 同伴） | `{html,txt}` | HTML **241K** / txt **180K** | Claude 3.5 Haiku 案 | **补链抽取**；不升主写全案 |

**一手 URL（核验 2026-09-22 CST，`curl`→200）：**
- CircuitLasso：https://arxiv.org/abs/2606.16939 · PDF https://arxiv.org/pdf/2606.16939
- Methods：https://transformer-circuits.pub/2025/attribution-graphs/methods.html
- Biology：https://transformer-circuits.pub/2025/attribution-graphs/biology.html

**一句话抓手：**
- **CircuitLasso**：别再对每个候选边做干预——在**计算序约束**下对激活/SAE 特征做 **block 上三角 Lasso**，拿依赖骨架；高维 SAE 上仍可跑。
- **Circuit Tracing**：先训 **CLT** 把 MLP 换成可解释「替换模型」，再在**冻结注意力与归一化分母**后画 **逐提示归因图**，用扰动对齐「图说 vs 真模型」。

---

## 二、议题边界：规模化电路方法 ≠ 通史 / 操控 / 安全熔断

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| MI 概念阶梯（特征→电路→归因图史） | 为何要 SAE、电路节点如何进化 | **[[机制可解释性入门]]** | **否**（禁通史重写） |
| RepE / ActAdd / CAA / ITI | 推理期对激活加向量改行为 | **[[激活操控与表征工程]]** | **否**（≠ 操控主轴） |
| Deliberative Alignment + Circuit Breakers（RR） | 规范 CoT / 表征熔断安全产品 | **[[审慎对齐与断路器]]** | **否**（「circuit」同名异物） |
| **可扩展电路学习 + 归因图方法** | 如何高效发现/验证机制子图 | **本篇** | **是** |

跟读直觉：[[机制可解释性入门]] 问「**思想阶梯怎么排**」；[[激活操控与表征工程]] 问「**已有方向时怎么拧旋钮**」；[[审慎对齐与断路器]] 问「**安全对齐新范式**」；本卡问「**电路怎么规模化找出来、怎么验证图不是幻觉**」。

### 2.2 两方法正交轴

| | CircuitLasso | Anthropic Circuit Tracing |
|---|---|---|
| **数据接口** | **观测式**（收集激活 / SAE 特征，无 per-edge 干预） | 先付 **CLT 训练成本**，再对单提示建 **local replacement model** |
| **图对象** | 跨提示/数据集级依赖骨架；可再做 prompt 特异重加权 | **逐提示** attribution graph（节点=活跃特征/嵌入/误差/logit） |
| **线性从哪来** | 显式 $\ell_1$ 稀疏回归假设 | 冻结 attn 模式 + LN 分母 + transcoder「桥过」MLP 非线性 → 特征预激活对上游线性 |
| **验证** | InterpBench **SHD**；CoLA **faithfulness/completeness**；DG 效用演示 | 扰动实验 vs 图预测；节点→logit / 特征→特征影响相关；mechanistic faithfulness |
| **规模痛点** | 宣称相对 EAP-ig 等 **免 LLM 反传**，适合高维 SAE | CLT 字典可达 **10M（18L）/ 30M（Haiku）**；图边可至百万级 → 需剪枝+交互界面 |

`
 机制电路「发现 / 验证」
 │
 ┌───────────┴───────────┐
 ▼ ▼
 CircuitLasso Circuit Tracing
 (观测 Lasso 骨架) (CLT 替换模型 + 归因图)
 群体/层间稀疏回归 逐提示线性归因 + 干预
 本篇 A 本篇 B（Biology=案）
`

---

## 三、主文 A · CircuitLasso：稀疏回归作电路发现代理

### 3.1 问题诊断（文内）

1. **原始神经元多义** → 学到的电路密、噪、难读（引 Elhage et al. 2022）。
2. **SAE 特征更单义**，但维度 $D \gg d$ → 既有 **干预式** 电路学习（causal mediation / tracing / attribution patching 等）在高维上 **算力爆炸**。
3. 作者主张：借鉴连续因果发现，用 **稀疏线性回归** 作电路发现代理；在 **已知前馈计算序** 下把无环约束收成 **block 上三角 Lasso**，只吃观测激活。

### 3.2 方法接口（压缩跟读，非教程）

**神经元设定（§3.2）：** 收集 $L$ 个位点、宽 $d$、$M$ 条输入的激活 $H$；按层序与「注意力先于 MLP」重排后，解形如
$$
\min_A \|H - A^\top H\|_F^2 + \lambda\|A\|_1
$$
并 **固定下三角块为零**（建筑性无环）。结构图 $G$ 由 $\hat A$ 推断。

**复杂度主张（Proposition 3.1）：** FISTA 达 $\epsilon$-次优时，CircuitLasso 总成本量级
$O\!\big(M L(L-1)d^2 / \sqrt{\epsilon}\big)$；相对 EAP-ig「每观测约 2 前向 + 1 反传」的主导成本，作者给出何时回归更省的充分条件（Prop 3.2；细节见附录 A）。

**SAE 特征设定（§3.3）：** 对计算序上位点 $i \prec j$，解
$$
\hat A_{i,j}=\arg\min_{A_{i,j}} \|Z_j - A_{i,j}^\top Z_i\|_F^2 + \lambda\|A_{i,j}\|_1,\quad A_{i,j}\in\mathbb{R}^{D\times D}
$$
代价 $O(M D^2/\sqrt{\epsilon})$。另可选把下游标签 $y$ 纳入
$\min L_{\mathrm{pred}}(y, A_{i,y}^\top Z_i)+\lambda\|A_{i,y}\|_1$，用于解释预测并做下游编辑。

**非线性扩展：** Appendix B；主结果称拓扑骨架相近、成本更高，主文以线性为主。

**刻意不写：** SAE 训练配方（文称直接用预训练 SAE，细节 Appendix D.1）；本卡不复刻超参表。

### 3.3 实验字段（官方 PDF 数字）

#### （1）InterpBench：结构精度 × 墙钟（Figure 2 / §4.1）

- **设定：** Gupta et al. (2024) *InterpBench*；跟协议评 **16** 个主合成案 + 真实 **IOI**；基线 **EAP**（Syed et al. 2024）、**EAP-ig**（Hanna et al. 2024）；指标 **SHD**（↓）与 runtime（秒，↓）；单卡 A100，三试平均。
- **结果（文称）：**
 - CircuitLasso-**linear** 均值 SHD **3.16** ≈ EAP-ig **2.98**，优于 EAP **3.61**；
 - 均值 runtime **16.3 s/案**，相对 EAP-ig **49.1 s** 约 **3.0×** 快，相对 EAP **33.7 s** 约 **2.1×** 快；
 - CircuitLasso-**nonlinear** 均值 SHD 最低 **2.84**，但 runtime 约线性的 **3.7×**，多数案甚至慢于 EAP-ig。
- **主张句：** 「efficiency at parity of accuracy」。

#### （2）SAE 电路：CoLA + GPT-2 small（§4.2.1 / Figure 3）

- **数据：** CoLA（Warstadt et al. 2019）公开训练句 **8,551**（全文称数据集共 10,657）；作者称 **MI 文献中未见用 CoLA**。
- **特征：** OpenAI 预训练 SAE（Gao et al. 2025）于 GPT-2 small。
- **电路粒度：** 数据集级 $|A_{L,y}|$（群体依赖）vs 单提示 $s=|A_{L,y}|\odot|z_L|$；主图用 prompt averaging。
- **可读观察（Figure 3 叙述）：** Persistence（如 “-self” 跨层）、Merging / Dropping、Cause–Effect 与 **伪相关**（如 “-self” 与 “hunger/thirst”）；方向强制对齐计算序 → 可出现「反常识因果」边——文内自承。
- **Faithfulness / Completeness（Figure 4，Marks et al. 2025 指标）：** 节点消融下与干预式 **SHIFT** 匹配，且无需 per-edge 干预；因回归显式给边权，额外做 **edge ablation**（SHIFT 不支持）。理想 faithfulness=1、completeness=0。

#### （3）下游效用：Bias-in-Bios（BiB）域泛化（§4.2.2 / Table 1–2）

- **定位：** 文称 **utility demonstration**，非多层电路主实验；精度优势归因于 **解缠 SAE 特征的细粒度操作**，非「电路学习效应」本身。
- **做法：** 按 $|\hat A_{i,y}|$ 排名单层 SAE 特征，人工标出性别相关特征并置零 → 原分类器或重训分类器。
- **Table 1 runtime（不含人工解释）：** 例 Pythia-70M：SHIFT **257.6 s** / CircuitLasso **36.5 s**；Gemma-2-9b：SHIFT **908.4 s** / CircuitLasso **107.4 s**（差距随模型增大）。
- **Table 2：** CircuitLasso / CircuitLasso-retrain 与最强非-ORACLE 基线 **可比或略优**（列内粗体为非-ORACLE 最优）。例 Pythia-70M Profession：CircuitLasso-retrain **94.2** vs SHIFT-retrain **93.1**；Gender 近 50% 为目标。

### 3.4 局限与未来（§5，跟读）

- 线性系数 **≠** 底层非线性精确因果效应；何时定量 faithful 仍开放。
- 层内反馈 / 非严格前馈架构 → 三角无环假设失效。
- 本卡不展开附录证明与全部特征表（Tables 3–7）。

---

## 四、主文 B · Anthropic Circuit Tracing：CLT → 归因图 → 干预

> **形态声明：** 一手为 **https://transformer-circuits.pub** HTML（Published **2025-03-27**）。仓库 **无** 对应 arXiv PDF；**禁止编造 arXiv 号**。[[机制可解释性入门]] 已写概念阶梯；本节写 **方法接口与可核对字段**。

### 4.1 流水线（methods 开篇主张）

1. **稀疏编码部件：** 选用 **transcoder** 族（相对只重构激活的 SAE，更直接逼近 MLP 输入→输出），并采用 **cross-layer transcoder（CLT）**：特征在层 $\ell$ 读 residual，可写到 **后续所有** MLP 输出。
2. **Replacement model：** 用 CLT 重构替换各层 MLP 输出；注意力仍按原模型跑。最大 **18L** CLT（总特征至 **10M**）在多样预训练风格提示上，与底层模型 **next-token 最可能 token 一致率约 50%**（相对 per-layer transcoder / 阈值神经元基线更优）。
3. **Local replacement model（对固定提示 $p$）：** 再 **冻结注意力模式与归一化分母**，并在每（token, layer）加 **CLT 相对真 MLP 的误差校正** → 激活与 logit **局部精确匹配**底层；但机制未必相同 → 需 **mechanistic faithfulness**。
4. **Attribution graph：** 节点：活跃 CLT 特征、提示 token 嵌入、**error nodes**、输出 logit；边：冻结非线性后的 **线性直接效应**（预激活 = 入边之和，至阈值）。捕获 **OV** 信息流，**忽略 QK**（为何注意该位置）。
5. **剪枝 + 交互界面：** 短提示边亦可至百万级；剪枝后仍可达数百节点 / 数万边 → 交互「tracing」界面。
6. **干预验证：** 改特征激活并注入其解码；CLT 跨层写出 → 需选择干预层范围；验证「图假说」对下游特征与 logit 的预测。

### 4.2 规模与 CLT 定量字段（§ Evaluations）

| 模型 | 字典规模（跨层总特征） | 归一化均值重构误差 | 平均 L0（活跃特征/token） |
|---|---|---|---|
| 18L 最大 run | **10M** | **~11.5%**（归一化均值重构误差） | **88** |
| Claude 3.5 Haiku（Haiku 3.5）最大 run | **30M** | **21.7%** | **235** |

文称：相对 **per-layer transcoder（PLT）** 与阈值神经元，CLT 在重构–稀疏–自动可解释性上呈 **Pareto 改进**；跨层的关键定性收益是 **缩短归因路径**（例：Zagreb:Croatia::Copenhagen: 上 PLT 长度 7 的 Copenhagen 链可塌到层 1），但也可能 **抹去** 底层「互相放大」的因果动力学 → 增加机制不忠实风险。

**图充分性相关：** unpruned 图上 embedding 影响归一化因子即 **replacement score**；另报 completeness（特征节点 vs error nodes 影响占比）等——具体曲线以 HTML 图为准，本卡不臆造未列表格的逐点读数。

**影响 vs 干预：** 节点 logit influence 优于「仅直接边 / 仅激活幅度」基线；特征对影响与消融相对效应 **Spearman 0.72**（文内）。整体局部替换模型扰动：干预后 **一层** 约 **0.8 cosine / 0.4 NMSE**，跨层误差 **累积**；幅度偏差可能与冻结 LN 分母有关；方向相关但字典越大幅度 faithfulness 可更差。

### 4.3 方法案（18L，跟读抓手，不写操作手册）

- **缩写补全：** `The National Digital Analytics Group (N` → `DAG`；图上可见 acronym / “say _A” / “say DA_” 等超节点路径；“National” 对 logit 影响弱——作者假设主贡献走 **注意力模式**（方法盲区）。
- **事实回忆：** `Michael Jordan plays the sport of` → basketball（约 65% 置信）。
- **两位数加法：** operand / lookup-table / 启发式特征；CLT 视角下模型多用 **中间启发式** 而非单一程序；与 Kantamneni & Tegmark 表征「时钟」工作互补。干预抑制超节点结果与图 **大体一致**。

### 4.4 局限清单（methods § Limitations，必录）

文内高亮七条（标题级）：

1. **Missing Attention Circuits**（QK；induction / 选择题可「跳过故事」）
2. **Reconstruction Errors & Dark Matter**
3. **Inactive Features & Inhibitory Circuits**（「未激活」本身可能是机制）
4. **Graph Complexity**
5. **Features at Wrong Abstraction**（splitting / absorption）
6. **Difficulty of Global Circuits**（虚拟权重干扰；抑制边难靠共现过滤）
7. **Mechanistic Faithfulness**（替换模型机制 ≠ 原 MLP）

**跟读含义：** 归因图是 **假说生成器**，不是终审；干预与忠实性字段是本卡辅线的理由。

### 4.5 Global weights（辅）

残差直达虚拟权重 + 期望残差归因（ERA）/ **TWERA**（按目标激活加权）减轻干扰；在加法全局连接与 Biology 拒答上游等处有用，但 **非** 本卡主战场。

---

## 五、补链 C · Biology（Claude 3.5 Haiku 案索引）

> **角色：** methods 的 **应用同伴**（同日 **2025-03-27**；methods 自述 *nine behavioral case studies*）；本卡 **不** 重写九案全文，只钉索引与和 faithfulness 相关的方法消费点。

**文首主张：** 用同一套 circuit tracing 考察 Claude 3.5 Haiku 多情境内部机制。

**案目录（HTML Contents，名称级）：** Multi-step Reasoning；Planning in Poems；Multilingual Circuits；Addition；Medical Diagnoses；Entity Recognition and Hallucinations；Refusals；Life of a Jailbreak；Chain-of-thought Faithfulness；Uncovering Hidden Goals in a Misaligned Model；另有 Commonly Observed Circuit Components / Limitations。

**与方法接口直接相关的消费点（摘要，禁剧本化 jailbreak 步骤）：**
- **CoT Faithfulness：** 可区分「真在算」vs「bullshit」vs「从人类暗示倒推」的归因结构（例 $\sqrt{0.64}$ vs $\cos(23423)$）。
- **诗歌规划：** 在换行 token 上提前激活候选韵脚特征；抑制偏好计划可改写后续行。
- **多语 / 加法：** 语言无关抽象与跨情境复用加法电路；相对更小模型更显著。
- **幻觉 / 实体：** “can’t answer” 等抑制回路——对应 methods 对 **inactive / inhibitory** 局限的正面例。

**安全相关案（拒答 / jailbreak / 隐藏目标）：** 本卡只保留「存在可归因内部结构」的索引级结论；**禁止**复述可复用攻击步骤或提示全文（与 [[审慎对齐与断路器]] / [[激活操控与表征工程]] 硬约束一致）。

---

## 六、对照综合：何时用哪把刀

| 需求 | 更贴近 |
|---|---|
| 无 CLT 预训练预算；要在 **SAE 已有** 时快速拿 **群体级** 稀疏依赖 / 下游剪特征 | **CircuitLasso** |
| 需要 **单条提示上的逐步计算故事** + 交互图 + 定点干预叙事 | **Circuit Tracing** |
| 只要 MI 词汇与思想史 | → 回 **[[机制可解释性入门]]** |
| 要改行为的推理期向量 | → 回 **[[激活操控与表征工程]]** |
| 要对齐安全熔断产品 | → 回 **[[审慎对齐与断路器]]** |

**共同点：** 都以「可读特征（SAE/CLT）为节点」；都强调 **验证**（消融 / 扰动）而不止可视化。
**分歧点：** 观测回归骨架（便宜、偏群体、边权非精确因果）vs 替换模型线性归因（贵在 CLT、偏单例、明确 OV/QK 分工与失败模式）。

---

## 七、跟读清单（建议顺序）

1. 本卡 §二划界表（确认不是 [[机制可解释性入门]]/[[激活操控与表征工程]]/[[审慎对齐与断路器]]）。
2. CircuitLasso：摘要 + §3 框架 + Figure 2 / Table 1–2。
3. Circuit Tracing methods：Introduction → Building Replacement Model → Attribution Graphs → Validating… → Limitations（HTML 或 `.txt`）。
4. Biology：只读 Contents + 与自身问题相关的一案；勿把九案抄进通史。
5. 需要概念阶梯时跳转 **[[机制可解释性入门]]**，不要在本卡重写。

---

| 路径 | 体积（2026-09-22 CST） | 建议 |
|---|---|---|
| `https://arxiv.org/abs/2606.16939` | **1.42MB** / 19p | **入库二进制** |
| | **116K** | 入库抽取 |
| | **271K** | **入库抽取**（一手；无 PDF） |
| | **191K** | 入库抽取 |
| | **241K** | 补链抽取 |
| | **180K** | 补链抽取 |
| Anthropic arXiv PDF | **无** | **禁止虚构 arXiv 号**；笔记用 `urls:` 字段 |

**笔记路径：** [[CircuitLasso与电路追踪]]（本文件）
**状态：** `archived` · `date: 2026-09-22`

---

## 九、待核实 / 刻意省略

- CircuitLasso 附录 Table 3–7 逐特征标签与 $\lambda$ 消融曲线点：未全表抄录。
- Anthropic HTML 内嵌交互图 / 曲线的精确像素读数：以官方页为准，本卡只用正文明确写出的聚合数。
- CLT / SAE 训练算力美元级估计：methods 提及「open-weights cost estimates」链出，本卡不二次估算。
- Biology 九案机制细节：升主需另开专题卡；本波仅补链。
