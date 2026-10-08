---
title: "可解释电路新方法：CircuitLasso + Anthropic Circuit Tracing（≠ RepE）"
topic: CircuitLasso与电路追踪
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.16939
urls:
 - https://arxiv.org/abs/2606.16939
 - https://transformer-circuits.pub/2025/attribution-graphs/methods.html
 - https://transformer-circuits.pub/2025/attribution-graphs/biology.html
arxiv: ["2606.16939"] # Anthropic 两篇为 HTML，无 arXiv 号
related:
 - "机制可解释性入门"
 - "激活操控与表征工程"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 可解释电路新方法：CircuitLasso + Anthropic Circuit Tracing（≠ RepE）

> **主要来源**：[Scalable Circuit Learning for Interpreting Large Language Models](https://arxiv.org/abs/2606.16939)；[Circuit Tracing: Revealing Computational Graphs in Language Models](https://transformer-circuits.pub/2025/attribution-graphs/methods.html)；[On the Biology of a Large Language Model](https://transformer-circuits.pub/2025/attribution-graphs/biology.html)（截至 2026-09-22）。下文「CircuitLasso §x」指 Yin 等的论文，「Circuit Tracing」「Biology」指 Anthropic 的两篇 HTML 文章。
> **研究线**：架构思想与方法接口（主）——观测式稀疏回归 vs 替换模型上的线性归因；干预 faithfulness 字段（辅）——InterpBench SHD 与墙钟、CoLA faithfulness / completeness、CLT 重构与 L0、影响–消融相关、扰动一致性。
> **范围与相邻笔记**：
> - ≠ [[机制可解释性入门]]：本篇不写 polysemanticity → SAE → 电路 → 归因图的概念阶梯，也不重复 CLT、局部替换模型与归因图的机制说明，只补可核对的定量字段。
> - ≠ [[激活操控与表征工程]]：本篇不写推理期加减概念向量来操控行为。
> - Biology 中拒答、越狱与隐藏目标等安全案例只保留「存在可归因的内部结构」这一结论，不复述攻击步骤或提示全文。
> **意义**：电路发现长期依赖逐边干预，在高维 SAE 特征上算力不可承受；CircuitLasso 用只需观测激活的稀疏回归，在结构精度与干预式基线持平的同时快约 3 倍，让高维 SAE 上的数据集级电路学习变得可行。与 Anthropic 的逐提示归因图并读，可以看清两条路线在成本、粒度与因果保证上的取舍。

**一句话**：CircuitLasso 在已知前馈计算序的约束下，对激活或 SAE 特征做块上三角 Lasso，直接得到依赖骨架；Circuit Tracing 先训练跨层 transcoder 把 MLP 换成可解释的替换模型，再在单条提示上画归因图，并用扰动检验图与真模型是否一致。

## 一、问题背景

CircuitLasso §3.1 把电路发现的困境归为三点：

1. **神经元多义**：直接在原始神经元上学到的电路稠密、噪声大、难以解读。
2. **SAE 特征维度高**：稀疏自编码器（SAE）把激活拆成更单义的特征，但特征维度 $D$ 远大于隐藏维度 $d$。causal mediation、causal tracing、attribution patching 一类干预式方法需要对候选边逐一干预或反传，在高维特征上算力爆炸。
3. **作者的出路**：借鉴连续因果发现，用稀疏线性回归作为电路发现的代理，只用观测到的激活；由于 Transformer 的计算顺序已知，无环约束可以直接写成块上三角结构。

## 二、脉络

电路研究的主线是「先有可读的节点，再连成计算图」（见 [[机制可解释性入门]]）：组件级电路（如 induction head）→ 字典学习拆出单义特征（2023）→ 以特征为节点的稀疏特征电路与各类归因、patching 方法 → Anthropic 的 Circuit Tracing（2025-03-27）用跨层 transcoder（CLT）与局部替换模型在单条提示上画归因图，配套的 Biology 把方法用到 Claude 3.5 Haiku 的多种行为上。

CircuitLasso（2026-06，ICML 2026 MI Workshop）走的是另一条路：不训练新的字典，也不做逐边干预，而是在现成 SAE 特征上用回归直接学数据集级的依赖结构，对照基线是 EAP 与 EAP-ig 这类 attribution patching 方法。

| | CircuitLasso | Circuit Tracing |
|---|---|---|
| 数据接口 | 观测式：收集激活或 SAE 特征，不做逐边干预 | 先付 CLT 训练成本，再对单条提示建局部替换模型 |
| 图对象 | 跨提示、数据集级的依赖骨架，可再做提示特异的重加权 | 逐提示的归因图（节点为活跃特征、嵌入、误差项与 logit） |
| 线性从哪来 | 显式的 $\ell_1$ 稀疏回归假设 | 冻结注意力模式与归一化分母，transcoder 桥接 MLP 非线性 |
| 验证 | InterpBench SHD；CoLA faithfulness / completeness；下游效用演示 | 扰动实验对照图的预测；影响–消融相关；机制忠实性 |
| 规模痛点 | 不需要对 LLM 反传，适合高维 SAE | CLT 字典可达 1000 万（18 层模型）/ 3000 万（Haiku）特征；图边可达百万级，需剪枝与交互界面 |

## 三、CircuitLasso：稀疏回归作电路发现代理

### 3.1 方法

**神经元设定**（CircuitLasso §3.2）：收集 $L$ 个位点、宽度 $d$、$M$ 条输入的激活矩阵 $H$，按层序与「注意力先于 MLP」重排后求解

$$
\min_A \|H - A^\top H\|_F^2 + \lambda\|A\|_1 ,
$$

并把下三角块固定为零，用模型结构本身保证无环；电路图由估计出的 $\hat A$ 的非零模式给出。直觉是：在计算序上，一个位点的激活若能被少数上游位点线性解释，这些上游位点就是它的候选父节点，$\ell_1$ 罚负责把其余边压成零。

**SAE 特征设定**（CircuitLasso §3.3）：对计算序上的每对位点 $i \prec j$，用 $Z_i$ 回归 $Z_j$ 并加 $\ell_1$ 罚，得到 $D\times D$ 的稀疏连接；还可以把下游标签 $y$ 作为回归目标，用于解释预测并做下游编辑。

**复杂度**：用 FISTA 求解到 $\epsilon$-次优时，神经元设定的总成本量级为 $O\!\big(M L(L-1)d^2 / \sqrt{\epsilon}\big)$，SAE 设定每对位点为 $O(M D^2/\sqrt{\epsilon})$；作者给出相对 EAP-ig（每个观测约两次前向加一次反传）何时更省的充分条件（Prop 3.1–3.2，细节见附录 A）。非线性扩展见附录 B，拓扑骨架相近但成本更高，主文以线性为主；SAE 直接用预训练版本（附录 D.1）。

### 3.2 证据

- **InterpBench 结构精度与墙钟**（CircuitLasso §4.1，Figure 2）：16 个合成案例加真实 IOI 任务，单卡 A100、三次平均。线性版平均 SHD 3.16，与 EAP-ig 的 2.98 接近、优于 EAP 的 3.61；平均每案 16.3 s，比 EAP-ig（49.1 s）快约 3.0 倍、比 EAP（33.7 s）快约 2.1 倍。非线性版 SHD 最低（2.84），但耗时约为线性版的 3.7 倍，多数案例慢于 EAP-ig。作者的主张是「精度持平下的效率」。
- **SAE 电路**（CircuitLasso §4.2.1，Figure 3–4）：在 GPT-2 small 上用 OpenAI 预训练 SAE、CoLA 公开训练句 8,551 条（作者称 MI 文献中此前没用过 CoLA）。图上可读出特征跨层延续、合并与消失，也有伪相关（如「-self」与「hunger / thirst」）；方向被强制对齐计算序，因此会出现「反常识因果」边，文中自承。节点消融下的 faithfulness / completeness 与干预式的 SHIFT 相当，且回归显式给出边权，还能做 SHIFT 不支持的边消融。
- **下游效用演示**（CircuitLasso §4.2.2，Table 1–2）：在 Bias-in-Bios 上按回归系数排名单层 SAE 特征，人工标出性别相关特征并置零。耗时（不含人工解释）Pythia-70M 上 SHIFT 257.6 s、CircuitLasso 36.5 s，Gemma-2-9b 上 908.4 s 对 107.4 s，差距随模型增大；精度与最强非 ORACLE 基线可比或略优（如 Pythia-70M Profession 上 CircuitLasso-retrain 94.2 对 SHIFT-retrain 93.1）。作者把精度优势归于解缠 SAE 特征的细粒度操作，而不是电路学习本身。

## 四、Circuit Tracing：可核对的定量字段

CLT、局部替换模型、归因图的节点与边、global weights 与局限清单的机制说明见 [[机制可解释性入门]] 第六节，这里只补可核对的数字与本篇对照所需的要点。

### 4.1 CLT 规模与重构

| 模型 | 跨层总特征 | 归一化均值重构误差 | 平均 L0（每 token 活跃特征） |
|---|---|---|---|
| 18 层模型最大 run | 10M | ~11.5% | 88 |
| Claude 3.5 Haiku 最大 run | 30M | 21.7% | 235 |

- 最大的 18 层 CLT 作为替换模型时，在多样的预训练风格提示上，与原模型的下一 token 一致率约 50%，优于逐层 transcoder 与阈值神经元基线。
- 跨层写出的主要收益是缩短归因路径（例如 Zagreb:Croatia::Copenhagen: 一例中，逐层 transcoder 上长度 7 的链可塌缩到第 1 层），代价是可能抹去底层「互相放大」的因果动力学，增加机制不忠实的风险。

### 4.2 影响与干预的一致性

- 节点对 logit 的影响度量优于「只看直接边」或「只看激活幅度」的基线；特征对之间的影响与消融相对效应的 Spearman 相关为 0.72。
- 对整个局部替换模型做扰动，干预后一层内约为 0.8 cosine / 0.4 NMSE，跨层误差会累积；幅度偏差可能与冻结 LN 分母有关，方向相关但字典越大幅度忠实性可能越差。
- 方法案例（18 层模型）：缩写补全（The National Digital Analytics Group (N → DAG）、事实回忆（Michael Jordan plays the sport of → basketball，约 65% 置信）、两位数加法（模型多用中间启发式而非单一程序）；缩写一例中「National」对 logit 影响弱，作者推测主贡献走注意力模式，正是归因图看不到 QK 的盲区。
- 原文 Limitations 列了七条：缺注意力（QK）电路、重构误差与「暗物质」、未激活特征与抑制回路、图复杂度、特征抽象层级错位、全局电路难、机制忠实性。归因图因此是假说生成器，结论须靠干预确认。

### 4.3 Biology（索引）

Biology 与方法篇同日发布，用同一套方法考察 Claude 3.5 Haiku 的多种行为，包括多步推理、诗歌规划、多语电路、加法、医疗诊断、实体识别与幻觉、拒答、越狱、思维链忠实性、隐藏目标等。与方法接口直接相关的几点：

- **思维链忠实性**：归因结构能区分「真在计算」、「随口编」与「从人类暗示倒推」（例如 $\sqrt{0.64}$ 与 $\cos(23423)$ 的对比）。
- **诗歌规划**：模型在换行 token 上提前激活候选韵脚特征，抑制该计划可改写后续诗行。
- **幻觉与实体识别**：「无法回答」等抑制回路，是方法篇「未激活特征与抑制回路」这条局限的正面例证。

## 五、何时用哪种方法

| 需求 | 更贴近 |
|---|---|
| 没有 CLT 训练预算，已有 SAE，想快速拿到数据集级的稀疏依赖或做下游特征剪除 | CircuitLasso |
| 需要单条提示上的逐步计算故事、交互图与定点干预 | Circuit Tracing |
| 只需要 MI 的概念与思想史 | [[机制可解释性入门]] |
| 想在推理期用向量改变行为 | [[激活操控与表征工程]] |

共同点：都以可读特征（SAE 或 CLT）为节点，都强调用消融或扰动做验证，而不只是可视化。分歧在于：观测回归便宜、偏群体级，但边权不是精确的因果效应；替换模型上的线性归因贵在 CLT 训练、偏单例，但明确了 OV / QK 的分工与已知失败模式。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[机制可解释性入门]] | 共用背景：特征 → 电路 → 归因图的概念阶梯，以及 CLT 与归因图的机制说明；本篇在其上补 CircuitLasso 增量与 Circuit Tracing 的定量字段 | 概念阶梯与归因图机制的重复叙述 |
| [[激活操控与表征工程]] | 方法对照：两者都读模型内部表征，那篇用表征方向改行为，本篇用表征之间的依赖发现电路 | ActAdd、CAA、ITI 等操控方法 |

## 七、意义

CircuitLasso 把电路发现的主要成本从「逐边干预或反传」换成「一次性的稀疏回归」，让高维 SAE 上的数据集级电路学习变得可行；Circuit Tracing 则在单条提示上给出了最细的计算故事和一组可核对的忠实性字段。两者的共同教训是：画出来的图只是假说，必须用消融或扰动验证。

## 八、局限与待核实

- **CircuitLasso 的边界**（CircuitLasso §5）：线性系数不等于底层非线性的精确因果效应，何时定量忠实仍是开放问题；层内反馈或非严格前馈的架构会让三角无环假设失效。
- **Circuit Tracing 的边界**：见 4.2 的七条局限；跨层 CLT 缩短路径的同时可能掩盖真实的因果动力学。
- **未抄录的内容**：CircuitLasso 附录 Table 3–7 的逐特征标签与 $\lambda$ 消融曲线；Anthropic 页面内交互图与曲线的精确读数（本篇只用正文明确写出的聚合数）；CLT / SAE 训练算力的美元级估计（方法篇链出的 open-weights 成本估计，本篇不二次估算）。
- **Biology 案例**：机制细节未展开，只作索引。

## 九、延伸阅读

| 类型 | 标题 | 说明 | URL |
|---|---|---|---|
| 论文 | Scalable Circuit Learning for Interpreting Large Language Models | Yin、Wei、Gao、Dhurandhar、Natesan Ramamurthy、Yu；先读摘要、§3 框架与 Figure 2、Table 1–2 | https://arxiv.org/abs/2606.16939 |
| 方法篇 | Circuit Tracing: Revealing Computational Graphs in Language Models | Ameisen 等，Transformer Circuits Thread，2025-03-27；按 Introduction → Replacement Model → Attribution Graphs → Validating → Limitations 读 | https://transformer-circuits.pub/2025/attribution-graphs/methods.html |
| 案例篇 | On the Biology of a Large Language Model | Lindsey 等，2025-03-27；读目录与自己关心的一案 | https://transformer-circuits.pub/2025/attribution-graphs/biology.html |
