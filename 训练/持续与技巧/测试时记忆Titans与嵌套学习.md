---
date: 2026-10-09
status: archived
archived: 2026-10-09
topic: 测试时记忆Titans与嵌套学习
title: "测试时记忆Titans与嵌套学习"
lines: [架构思想, 数学原理]
sources:
  - https://arxiv.org/abs/2407.04620
  - https://arxiv.org/abs/2501.00663
  - https://proceedings.neurips.cc/paper_files/paper/2025/hash/a4ca07aa108036f80cbb5b82285fd4b1-Abstract-Conference.html
  - https://arxiv.org/abs/2504.13173
  - https://arxiv.org/abs/2505.23735
  - https://arxiv.org/abs/2505.23884
  - https://arxiv.org/abs/2510.09551
  - https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/
  - https://arxiv.org/abs/2511.07343
  - https://arxiv.org/abs/2512.24695
  - https://proceedings.neurips.cc/paper_files/paper/2025/hash/4309616aaed8e848009bc4a7ef73b493-Abstract-Conference.html
  - https://arxiv.org/abs/2602.21204
  - https://arxiv.org/abs/2605.16350
  - https://arxiv.org/abs/2606.03979
  - https://arxiv.org/abs/2608.16844
  - https://arxiv.org/abs/2609.33325
arxiv: ["2407.04620", "2501.00663", "2504.13173", "2505.23735", "2505.23884", "2510.09551", "2511.07343", "2512.24695", "2602.21204", "2605.16350", "2606.03979", "2608.16844", "2609.33325"]
related: ["测试时训练", "持续学习", "线性注意力与状态空间模型谱系", "条件记忆与查表稀疏Engram", "智能体长程记忆", "优化器与训练稳定性", "OnPolicy蒸馏OPD范式", "门控注意力与注意力汇"]
---

# 测试时记忆Titans与嵌套学习

> **主要来源**：[Titans: Learning to Memorize at Test Time](https://arxiv.org/abs/2501.00663)（简称 Titans）；[It's All Connected: A Journey Through Test-Time Memorization, Attentional Bias, Retention, and Online Optimization](https://arxiv.org/abs/2504.13173)（简称 Miras）；[ATLAS: Learning to Optimally Memorize the Context at Test Time](https://arxiv.org/abs/2505.23735)（简称 ATLAS）；[Nested Learning: The Illusion of Deep Learning Architectures](https://arxiv.org/abs/2512.24695)（简称嵌套学习论文）；[TNT: Improving Chunkwise Training for Test-Time Memorization](https://arxiv.org/abs/2511.07343)（简称 TNT）；[Titans Revisited: A Lightweight Reimplementation and Critical Analysis of a Test-Time Memory Model](https://arxiv.org/abs/2510.09551)（简称 Titans Revisited）；[Test-Time Training with KV Binding Is Secretly Linear Attention](https://arxiv.org/abs/2602.21204)（简称 KV 绑定论文）（截至 2026-09-27）。其余来源见第十四节。
> **研究线**：架构思想（把一个小网络当作长期记忆，在推理时按梯度写入、按门控遗忘，并与注意力这一短期记忆组合；再把优化器与架构放进同一套多层优化视角）· 数学原理（关联记忆的内部目标、保持正则与在线优化之间的对应关系）
> **范围与相邻笔记**：
> - ≠ [[测试时训练]]：本篇不写 In-Place TTT、TEMPO、Modular TTT 等方法本身，TTT 层与 LaCT 只作前置。
> - ≠ [[持续学习]]：本篇不写持续学习的综述地图、灾难性遗忘的通用技法与 MoE 扩容做法。
> - ≠ [[线性注意力与状态空间模型谱系]]：本篇不写线性注意力、DeltaNet、Mamba 的谱系与「线性 RNN 即在线学习」的一般推导。
> - ≠ [[条件记忆与查表稀疏Engram]]：本篇不写按 token 序列查表的参数记忆。
> - ≠ [[智能体长程记忆]]：本篇不写智能体在模型外部维护的分层记忆与笔记网络。
> - ≠ [[优化器与训练稳定性]]：本篇不写优化器谱系本身，只写嵌套学习对优化器的重新解释。
> - ≠ [[门控注意力与注意力汇]]：本篇不写注意力汇的成因与门控注意力。
>
> **意义**：注意力能精确看到窗口里的每个 token，但代价随长度平方增长；线性循环模型把历史压进固定大小的状态，长了就装不下。Titans 提出第三种做法：让一个深层 MLP 充当长期记忆，在推理时用「惊奇度」（关联记忆损失对输入的梯度）决定写入多少，用遗忘门决定丢掉多少，再与注意力组合。同一作者团队随后用 Miras 把 Transformer、Titans 与现代线性 RNN 统一为「带内部目标的关联记忆」，用 ATLAS 改进记忆容量与更新方式，最后在嵌套学习中把优化器也看成关联记忆，提出多频率的连续记忆系统与 Hope 架构，并把这条路线定位为持续学习的一种方案。独立复现、训练效率改进与「它其实是线性注意力」的反驳在 2025 至 2026 年陆续出现。本篇所读论文中，从头训练的语言模型最大为 1.3B；Hope 的持续学习实验是在 8B 骨干上做持续预训练改造。

## 一、问题背景

**两种记忆的取舍**：Titans 把注意力看作关联记忆：键值对就是记忆，按查询与键的相似度读取。它精确，但只覆盖当前窗口，复杂度是平方级。线性 Transformer 与线性 RNN 把历史压缩进矩阵或向量状态，可扩展，但很长的上下文难以压进很小的状态（Titans 第 1 节）。Titans 据此提出五个问题：什么样的记忆结构好、怎样更新、怎样读取、怎样把不同记忆模块连成一个系统、是否需要深层记忆（Titans 第 1 节）。

**「测试时记忆」指什么**：记忆模块本身是一个小网络，它的权重在推理期随输入在线更新（内层循环）；投影矩阵、门控参数等其余参数在训练期学好后固定（外层循环）（Titans 第 3.1 节）。上下文移除后，写进记忆的内容也随之消失；嵌套学习论文因此把它称为「参数化的上下文学习」，并指出在持续学习设定下，「测试时」这个说法容易误导（嵌套学习论文第 6 节）。

**本篇「记忆」的范围**：这里的记忆指序列模型内部、随上下文写入的权重。它不同于三种同名概念：

- 按 token 序列查表、训练后固定的参数记忆，见 [[条件记忆与查表稀疏Engram]]；
- 线性注意力与状态空间模型中的矩阵或向量状态。Titans 指出矩阵形式的记忆相当于在线线性回归，并改用深层 MLP 作记忆（Titans 第 3.1 节）；状态本身的谱系见 [[线性注意力与状态空间模型谱系]]；
- 智能体在模型外部存取的文本与图谱记忆，见 [[智能体长程记忆]]。

## 二、发展脉络

| 时间 | 节点 | 内容 |
|---|---|---|
| 2024-07 | [TTT 层](https://arxiv.org/abs/2407.04620) | 隐状态本身是一个模型，更新规则是一步自监督学习（前置） |
| 2024-12 | [Titans](https://arxiv.org/abs/2501.00663) | 深层神经长期记忆，惊奇度写入、动量与遗忘；与注意力的三种组合 |
| 2025-04 | [Miras](https://arxiv.org/abs/2504.13173) | 序列模型统一为以「注意力偏置」为内部目标的关联记忆；遗忘即保持正则 |
| 2025-05 | [ATLAS](https://arxiv.org/abs/2505.23735) | 按窗口而非单个 token 优化记忆；多项式特征扩容；记忆内部用 Muon |
| 2025-05 | [LaCT](https://arxiv.org/abs/2505.23884) | 大块更新提高 TTT 的硬件利用率（前置） |
| 2025-10 | [Titans Revisited](https://arxiv.org/abs/2510.09551) | 轻量复现：分块使 Titans 不总优于基线，神经记忆组件一致有益 |
| 2025-11 | [嵌套学习博文](https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/) | Google Research 介绍嵌套学习与 Hope |
| 2025-11 | [TNT](https://arxiv.org/abs/2511.07343) | 分层记忆与周期性重置，两阶段训练提速 |
| 2025-12 | [嵌套学习论文](https://arxiv.org/abs/2512.24695) | 模型即嵌套优化问题；优化器是关联记忆；连续记忆系统与 Hope |
| 2026-02 | [KV 绑定论文](https://arxiv.org/abs/2602.21204) | 带 KV 绑定的 TTT 可改写为学习得到的线性注意力 |
| 2026-05 | [FedNL](https://arxiv.org/abs/2605.16350) | 联邦学习改写为三层嵌套优化 |
| 2026-06 | [Sleep](https://arxiv.org/abs/2606.03979) | 在线记忆之外加入离线巩固与自我演练 |
| 2026-08 | [Proteus](https://arxiv.org/abs/2608.16844) | 随上下文增长逐步开放记忆容量 |
| 2026-09 | [VisionHOPE](https://arxiv.org/abs/2609.33325) | 把自修改学习系统用作视觉骨干 |

Titans 的 arXiv 编号是 2501.00663，但 v1 的 abs 页提交日为 2024-12-31（UTC），脉络按提交日记。

主线是：TTT 层提出「隐状态即模型」（2024-07）；Titans 把深层神经记忆与注意力组合（2024-12）；Miras、ATLAS 给出统一框架与容量改进（2025-04 至 05）；嵌套学习把优化器与架构放进同一多层优化视角，提出 Hope（2025-11 至 12）；随后是训练效率、独立复现与「记忆还是线性注意力」的争论，以及向联邦学习、离线巩固与视觉骨干的延伸（2025-10 至 2026-09）。

## 三、前置：TTT 层与大块更新

这两项在 [[测试时训练]] 的脉络中已有概述，这里只交代与本篇相关的一点。

- **TTT 层**：Sun 等把隐状态做成一个机器学习模型，更新规则是一步自监督学习；因为隐状态在测试序列上也被训练，这种层称为 TTT 层。TTT-Linear 的隐状态是线性模型，TTT-MLP 是两层 MLP，实验规模为 125M 到 1.3B（TTT 层摘要）。Titans 的并行训练算法就建立在 TTT 层的小批量梯度下降张量化之上（Titans 第 3.2 节）。
- **LaCT**：现有 TTT 方法每 16 或 64 个 token 更新一次快权重，FLOPs 利用率常低于 5%；LaCT 改用 2K 到 1M token 的大块更新（LaCT 摘要）。这正是 TNT 后来要解决的同一个瓶颈（见第七节）。

## 四、Titans：神经长期记忆

### 4.1 记忆怎样写入

- **内部目标**：记忆模块学习键到值的映射。输入经两个线性层投影为键与值，损失是记忆对键的输出与值之差的平方（Titans 第 3.1 节）。
- **惊奇度**：作者借用「出乎意料的事件更容易被记住」这一说法，把惊奇度定义为该损失对记忆参数的梯度；梯度越大，说明新输入与过去越不同（Titans 第 3.1 节）。
- **动量**：只用瞬时梯度，在一次大的惊奇之后梯度会变得很小，后续信息容易漏掉。因此惊奇度拆成「过去的惊奇」与「瞬时惊奇」两项，形式上就是带动量的梯度下降；动量的衰减系数随输入变化，可以在上下文切换时丢弃旧的惊奇（Titans 第 3.1 节）。
- **遗忘**：每步更新前，旧记忆先乘以「一减去遗忘门」。遗忘门取 0 时完全保留，取 1 时清空记忆。作者指出这一机制推广了现代循环模型中的遗忘门，整个更新等价于用带动量和权重衰减的小批量梯度下降训练一个元模型（Titans 第 1 节、第 3.1 节）。
- **深层记忆**：矩阵形式的记忆相当于在线线性回归，隐含「历史依赖是线性的」这一假设；Titans 改用至少两层的 MLP 作记忆（Titans 第 3.1 节）。
- **读取**：用查询做一次不更新权重的前向计算（Titans 第 3.1 节）。

### 4.2 并行训练与持久记忆

**并行训练**：把序列切成块，块内的梯度都相对于块起点的记忆计算，就可以把带权重衰减的小批量梯度下降改写成矩阵乘法；动量项是块内的线性递推，可用并行扫描计算（Titans 第 3.2 节）。

**持久记忆**：除了随上下文变化的长期记忆，Titans 还在序列开头放一组与输入无关的可学习参数，用来存放任务知识。作者从三个角度说明它的作用，其中一个是：因果注意力天然偏向开头的 token，开头放可学习参数可以重新分配注意力权重（Titans 第 3.3 节）。

### 4.3 与注意力的三种组合

Titans 的系统由三支组成：核心支（注意力，作短期记忆）、上下文记忆支（神经长期记忆）、持久记忆支（Titans 第 4 节）。

| 变体 | 做法 | 论文的评价 |
|---|---|---|
| 记忆作为上下文（MAC） | 序列分块；用当前块作查询从长期记忆中取回历史信息，与持久记忆、当前块拼接后做块内全注意力；注意力的输出再写入记忆 | 注意力可以决定是否需要长期记忆，并帮记忆只存有用的信息；长依赖上最好 |
| 记忆作为门控（MAG） | 一支用滑动窗口注意力，一支直接用输入更新长期记忆，两支输出经非线性门控合并 | 滑动窗口是精确的短期记忆，神经记忆是渐隐的记忆；语言建模上与 MAC 接近 |
| 记忆作为层（MAL） | 记忆层先压缩上下文，再接滑动窗口注意力 | 文献中常见的混合方式；表达力受每一层限制；借助 FlashAttention，训练吞吐高于各基线与单独的记忆模块 |

另有只用神经记忆、不带注意力的变体，论文称为 LMM（Titans 第 4.3 节）。

### 4.4 论文报告的结果

- **规模**：170M、340M、400M、760M 四档，前三档在 FineWeb-Edu 上训练 15B token，760M 训练 30B token（Titans 第 5.1 节）。
- **语言建模**：不带注意力的神经记忆在非混合模型中困惑度与准确率最好；三种 Titans 混合变体都优于 Samba 与 Gated DeltaNet-H2（Titans 第 5.2 节）。
- **长上下文**：摘要称 Titans 可扩展到超过 2M 的上下文，在大海捞针任务上准确率高于基线（Titans 摘要）。在 BABILong 上，微调后的 Titans（MAC）在论文的比较中优于包括 GPT-4 在内的所有模型；加 RAG 的 Llama3.1-8B 参数量约为它的 70 倍，表现仍不如它（Titans 第 5.4 节）。
- **消融**：所有组件都有正贡献，贡献从大到小依次是权重衰减（遗忘）、动量、卷积和持久记忆（Titans 第 5.9 节）。
- **效率**：神经记忆模块的训练吞吐略低于 Mamba2 与 Gated DeltaNet（Titans 第 5.8 节）。

作者在实验节脚注中说明，这是论文的第一版，更大模型的结果将在下一版报告；arXiv 上目前只有 v1（Titans 第 5 节脚注、abs 页）。论文以 NeurIPS 2025 论文发表，会议版摘要只写「与基线相比有效」「能有效扩展到更大的上下文窗口」，没有保留 arXiv 版「超过 2M」与「比 Transformer 更有效」的说法（NeurIPS 2025 论文页）。

## 五、Miras：把序列模型统一为关联记忆

**定义**：Miras 把关联记忆定义为从键到值的映射算子，学习这个映射的目标称为「注意力偏置」，决定记忆的类型和它优先记住什么；记忆参数在内层循环优化，其余参数在外层循环优化（Miras 第 3 节）。作者观察到，几乎所有现有序列模型用的是同一类注意力偏置：点积相似度或 L2 回归（Miras 摘要）。

**遗忘即保持正则**：现代架构中的遗忘机制被重新解释为对注意力偏置加的保持正则，用来平衡「学新的」与「保住旧的」（Miras 第 1 节）。

**四个设计选择**：记忆架构、注意力偏置、保持门、记忆学习算法（Miras 摘要）。在这一框架下：

- 用点积偏置加梯度下降，得到 Hebbian 式更新：保持系数取 1 时是线性注意力，取可学习常数时是 RetNet 或 Lightning Attention，取数据依赖的值时是 Mamba2（Miras 第 4 节）；
- 用 L2 回归偏置加梯度下降，得到 Delta 规则：对应 DeltaNet、Gated DeltaNet 与 RWKV-7（Miras 第 4 节）；
- Titans 的长期记忆是用非线性 L2 目标、局部与全局两种保持正则、带动量梯度下降的特例（Miras 第 4 节）；
- softmax 注意力是 L2 回归目标的非参数解（Nadaraya-Watson 估计），没有保持项（Miras 第 4 节）。

**三个新变体**：Moneta 用 ℓp 范数偏置，Yaad 用对极端 token 更稳健的 Huber 损失，Memora 用 KL 散度作保持门（Miras 第 5.3 节）。实验规模为 120M 到 1.3B，1.3B 训练 100B token；论文称三者都是纯循环（无注意力）模型，却优于 Transformer++、现代线性循环模型与混合模型（Miras 第 6 节、第 6.1 节）。

## 六、ATLAS：从记住 token 到记住上下文

ATLAS 把现代循环模型在长上下文上的不足归为三点：记忆容量受记忆架构与输入特征映射所限；更新是在线的，只针对最后一个输入优化；固定大小记忆的管理方式表达力不足（ATLAS 摘要）。对应的改动：

- **容量**：对键和查询用多项式等高阶特征映射，并从理论上说明深层记忆与高阶映射都能提高容量，即记忆能精确映射的线性无关键值对的最大数目（ATLAS 第 1 节）。
- **Omega 规则**：在一个滑动窗口内对过去所有 token 的损失一起优化记忆，而不只看最后一个 token，使记忆记住的是局部上下文而不是单个 token（ATLAS 第 1 节、第 3.2 节）。
- **记忆内部的优化器**：用 Muon 更新记忆，近似二阶信息；Newton-Schulz 迭代的步数可以看作记忆内部的一种测试时算力（ATLAS 第 5 节）。作者称 ATLAS 是第一个用二阶信息近似优化记忆、且可并行训练的循环架构（ATLAS 第 1 节）。
- **DeepTransformers**：把 Omega 规则与 softmax 注意力联系起来，得到严格推广原始 Transformer 的一族架构（ATLAS 第 1 节）。

**结果**：模型规模为 340M 到 1.3B（ATLAS 第 6 节）。在 BABILong 上，1M 长度以内 ATLAS 与 Titans 相当；到 10M 时 Titans 性能下降，ATLAS 保持性能，摘要写作「+80% accuracy」（ATLAS 摘要、第 6.3 节）。

## 七、训练效率与独立复现

### 7.1 TNT：解开分块大小的两难

**问题**：深层记忆需要 16 到 64 个 token 的小块才能保持细粒度的学习信号，这使训练受内存带宽限制，FLOPs 利用率常低于峰值的 5% 到 10%（TNT 第 3 节）。在分块大小 64 上预训练的模型，只有推理时用同样的分块大小才达到最佳困惑度，这与「推理时块越小越好」的直觉相反（TNT 第 3 节）；图注写明该模型为 550M 的 Titans（TNT 图 2 图注）。

**做法**（TNT 摘要、第 4 节）：

- 第一阶段为效率而预训练：一个全局记忆处理大块（实验中为 2048），若干局部记忆处理小块，并周期性重置局部记忆的状态，打断序列依赖以实现上下文并行；
- 第二阶段为性能而微调：只把局部记忆调到更小的分块，可以一直调到分块为 1，与自回归解码的方式一致。

**结果**：在 150M 模型上，TNT 达到同一目标损失的时间最多比最准确的 Titans 配置快 17 倍（TNT 摘要、表 1）。第一阶段最好的平均困惑度为 23.13，优于 Titans 的 25.07 与普通 Transformer 的 23.58，但不如带门控的 Transformer 的 22.39；第二阶段只增加约 5% 的预训练算力，把困惑度降到 23.09（TNT 第 5.3 节）。同一张效率表中，用 FlashAttention 实现的带门控 Transformer 达到目标损失用时 0.96 小时，TNT 最快的配置为 1.12 小时（TNT 表 1）。

### 7.2 Titans Revisited：复现中看到的问题

Di Nepi 等指出原论文没有公开代码，描述也有多处不明确，例如预测只用最后一块还是所有块、MAC 是浅层编码器还是可堆叠的层、内部注意力的头数与位置编码等（Titans Revisited 第 2.2 节）。他们的轻量复现主要针对 MAC 变体，在掩码语言建模、时间序列预测与推荐三类任务上评测，序列被切成 32 到 128 个 token 的块（Titans Revisited 第 2 节）。结论：

- 由于分块，Titans 不总能超过成熟基线；但神经记忆组件相对只有注意力的模型一致带来提升（Titans Revisited 摘要）。
- 分块越大效果越好，代价是计算量上升（Titans Revisited 第 3 节）。
- 推荐任务上 Titans 不如 BERT4Rec，但加入记忆后 MRR 从 0.34 升到 0.43（Titans Revisited 第 3 节）。
- 冻结主干、只在测试时更新神经记忆，性能在 50 个 epoch 后基本不变，之后缓慢下降；作者认为单靠记忆更新不足以实现有意义的测试时学习，可能原因是冻结的键值投影与不断变化的记忆不匹配（Titans Revisited 第 3 节）。

## 八、嵌套学习

### 8.1 核心主张

嵌套学习论文把一个机器学习模型表示为一组嵌套、多层或并行的优化问题，每个问题有自己的「上下文流」；按此视角，现有深度学习方法是在压缩各自的上下文流（嵌套学习论文摘要）。

- **按更新频率分层**：把每个组件单位时间内的更新次数定义为它的频率，按频率把组件排成「层级」；层级越高，频率越低（嵌套学习论文第 3.2 节）。
- **架构与优化器是同一类东西**：作者认为优化过程与架构本质上是同一概念，只是处在系统的不同层级、面对不同的上下文（梯度或 token）；架构生成的梯度就是优化器的上下文，因此主张为特定架构设计优化器（嵌套学习论文第 1.2 节）。
- **优化器是关联记忆**：反向传播被解释为训练一个把各层输入映射到局部误差的关联记忆；带动量的 SGD、Adam、AdaGrad 都可以拆成两层嵌套优化，动量在压缩梯度信息。作者据此称，在逐元素 L2 回归目标下，Adam 是压缩梯度的最优关联记忆（嵌套学习论文第 1.2 节、第 4 节）。由此提出了 Delta 梯度下降与多尺度动量 Muon（M3）等新的更新规则（嵌套学习论文第 10 节）。
- **重新解释常用术语**：上下文学习被看作「有多个嵌套层级」的直接结果，而不是一种涌现特性；预训练被看作以整个预训练数据为上下文的一种上下文学习（嵌套学习论文第 6 节）。

### 8.2 连续记忆系统

传统架构里，注意力是工作记忆，MLP 存放预训练知识。连续记忆系统（CMS）把 MLP 换成一串更新频率各不相同的 MLP 块，每块每隔固定步数用自己那段上下文更新一次；普通 Transformer 是只有一块、更新频率为零的特例（嵌套学习论文第 7.1 节）。

作者给出的持续学习理由是：更新某个高频块时被遗忘的知识，可能仍保存在低频块中，并通过初始状态的反向传播回流到高频块，在时间维度上形成循环（嵌套学习论文第 7.1 节）。在效率上，每一时刻只有临近更新时刻的块需要更新，且块内不需要按顺序计算，可以并行（嵌套学习论文第 7.1 节）。

### 8.3 自修改 Titans 与 Hope

- **自修改 Titans**：Transformer 的键、值、查询投影在预训练后固定，模型无法在上下文中改变自己映射 token 的方式。自修改 Titans 让键、值、查询、学习率与遗忘门的投影都成为各自在线更新的记忆，从而学习自己的更新算法（嵌套学习论文第 8 节）。
- **Hope**：自修改 Titans 后接连续记忆系统。前者容量小、学习规则复杂，后者容量大、规则简单，作者认为两者互补（嵌套学习论文第 8.3 节）。另有 Hope-Attention 变体，把自修改 Titans 换成 softmax 全局注意力（嵌套学习论文第 8.3 节）。
- Google Research 的博文把 Hope 描述为 Titans 架构的变体：Titans 只有两层参数更新，属于一阶上下文学习；Hope 是自修改的循环架构，并加入 CMS 块以扩展到更大的上下文窗口（嵌套学习博文）。

### 8.4 论文报告的结果

- **语言建模**：760M 训练 30B token、1.3B 训练 100B token，从头训练；Hope 在语言建模与常识推理的平均表现上优于所有基线，规模增大时相对其他无注意力模型的优势更大（嵌套学习论文第 9.3 节）。
- **上下文召回**：Transformer 仍然最好，Hope 优于所有无注意力基线并缩小了差距（嵌套学习论文第 9.4 节）。
- **持续学习**：以 Llama3-8B 与 Llama-3B 为骨干，把 MLP 块改造成多频率并持续预训练 15B token，在三个文本分类数据集的类增量学习上优于上下文学习、EWC 与 InCA（嵌套学习论文第 9.1 节）。在先后学习两种新语言（满语、卡拉芒语）的翻译任务中，只靠上下文学习的基线显著退化，Hope 增加记忆层级后明显改善，带三层附加记忆的版本几乎恢复到第一种设定（各语言分开学习、不做持续学习）下上下文学习的水平（嵌套学习论文第 9.1 节）。
- **优化器**：M3 在 ViT 预训练中训练与测试损失都优于 AdamW 和 Muon；由于使用多个动量，它比 Muon 慢，与 AdaMuon 效率相当（嵌套学习论文第 9.7 节）。

### 8.5 会议版与 arXiv 版

嵌套学习论文收入 NeurIPS 2025 主会议（Advances in Neural Information Processing Systems 38，Main Conference Track）（NeurIPS 2025 论文页）。arXiv v1 提交于 2025-12-31，晚于会议，其注释写明「此工作的一个版本发表于 NeurIPS 2025」（嵌套学习论文 abs 页）。两版摘要措辞不同：会议版第一项贡献称「Deep Optimizers」，arXiv 版称「Expressive Optimizers」；arXiv 版列出的 Hope 评测比会议版多了知识吸收与少样本泛化（NeurIPS 2025 论文页、嵌套学习论文摘要）。

## 九、解释上的争议：记忆还是线性注意力

KV 绑定论文（ICML 2026）针对的是内层循环以键值关联为目标的 TTT，并认为「测试时记住键值映射」这一主流解释与多项现象矛盾（KV 绑定论文第 1 节、第 4 节）：

- 增加推理时内层循环的梯度步数，内层损失更低，下游表现却持续变差；
- 把内层的梯度下降换成梯度上升并重新训练，性能保持，有时还更好；
- 收敛后的模型中查询与键的分布明显不同；
- 用键替换查询，性能几乎不变。

作者证明，即使快权重是多层 MLP 并带动量，这类 TTT 也可以等价改写为一种学习得到的线性注意力算子；内层循环不是在做元学习，而是对查询、键、值做结构化、依赖历史的混合（KV 绑定论文第 1 节、第 5 节）。由此带来的实际改动：只更新最后一层即可得到最好的整体表现；去掉权重归一化后可以写成完全并行的形式，注意力计算的推理吞吐最多提高 4.0 倍，端到端训练提速 1.19 倍（KV 绑定论文第 6 节）。

**适用范围**：实验只在 LaCT 与 ViTTT 上做；作者认为 Titans 与 ATLAS 也满足其定理的假设，预期结论可以推广，但没有做实验验证（KV 绑定论文第 7 节）。分析还限于内层最后一层为线性且无偏置的情形（KV 绑定论文第 7 节）。

## 十、延伸

- **联邦学习（FedNL）**：把联邦学习改写为三层嵌套优化，服务器聚合的是「怎样构造和更新记忆」的规则，而不是记忆内容本身。客户端在冻结的预训练模型（论文举例为 Llama-3.2-1B）上加 Titans 式、以 Delta 规则更新的线性注意力，只训练并通信 LoRA 投影与记忆门控，以零样本方式做测试时适应（FedNL 摘要、第 2.2 节）。作者说明实验只到 1B 至 1.5B 规模（FedNL 第 5 节）。
- **离线巩固（Sleep）**：Behrouz 等认为模型还缺少把短期记忆转为长期知识的能力，提出「睡眠」阶段：先通过知识播种把小模型的记忆蒸馏进更大的网络，蒸馏过程结合在线策略蒸馏与基于强化学习的模仿学习；再通过「做梦」用强化学习生成合成数据来复习新知识（Sleep 摘要）。
- **容量调度（Proteus）**：静态记忆让早期 token 占用过多自由度、挤占后续上下文的容量；Proteus 随上下文增长逐步开放有效容量，在 Titans、Hope-Attention 等模型上报告了一致提升，且上下文越长提升越大（Proteus 摘要）。
- **视觉骨干（VisionHOPE）**：把嵌套学习的自修改结构用于视觉骨干，用五个耦合记忆分别存放内容、生成键值、控制学习率与保持；作者指出直接套用不受约束的自修改更新会不稳定，因此加入步长控制（VisionHOPE 摘要）。

## 十一、意义

1. **给「记忆」一个可以设计的结构**：Titans 把写入（惊奇度）、保留（动量）、遗忘（门控）和读取拆成可以分别设计的部件；Miras 进一步说明，线性注意力、Delta 规则、Mamba2 乃至 softmax 注意力，都可以看作同一框架下不同的目标、保持项与优化算法组合。这使比较不同序列模型有了共同的维度。
2. **长期记忆与短期记忆的组合方式**：Titans 的三种变体给出了把循环记忆与注意力组合的不同位置，论文的结果显示「作为上下文」与「作为门控」都优于文献中常见的逐层堆叠。
3. **把持续学习放进架构**：嵌套学习把优化器、架构和训练阶段放进同一多层优化视角，提出多频率的连续记忆系统，把防止遗忘的一部分责任从训练流程移到了架构上的多频率记忆。
4. **引出机制层面的讨论**：独立复现与 KV 绑定论文促使人们追问，这类模型的收益来自「测试时记忆」，还是来自更强的线性注意力式特征混合。

## 十二、局限与待核实

1. **规模**：Titans 最大到 760M，Miras、ATLAS 与 Hope 的从头训练最大到 1.3B，TNT 的实验为 150M，FedNL 为 1B 至 1.5B；Hope 的持续学习实验在 8B 骨干上做持续预训练。本篇所读材料中没有更大规模的从头训练结果，也没有旗舰模型采用这类架构的公开报告。
2. **主要证据来自同一团队**：Titans、Miras、ATLAS、TNT、嵌套学习、Sleep、Proteus 都有 Behrouz 与 Mirrokni 参与；独立工作中，Titans Revisited 的复现规模小，且结论与原文不完全一致。
3. **可复现性**：Titans Revisited 指出原文没有公开代码、多处细节未说明；KV 绑定论文也因 Titans 与 ATLAS 没有公开实现而未做实验。Titans 原文称更大模型的结果将在下一版报告，arXiv 上至今只有 v1。
4. **会议版与 arXiv 版的措辞**：Titans 的 NeurIPS 2025 版摘要删去了「超过 2M 上下文」与「比 Transformer 更有效」的说法。嵌套学习两版摘要的贡献命名与评测范围也不同。本篇的结果按 arXiv v1 全文写。
5. **「持续学习」的边界**：Google Research 博文称嵌套学习可以缓解甚至完全避免灾难性遗忘；论文结论则明确写灾难性遗忘在一般意义上「没有被解决」，并把它看作有限容量下压缩的自然结果。本篇按论文写。
6. **解释之争未定**：KV 绑定论文把带 KV 绑定的 TTT 改写为线性注意力，但对 Titans 与 ATLAS 只是预期推广，没有实验。该论文对化简代价有两处表述：引言写完整 TTT 只比化简后的线性注意力好 0.87 困惑度，第 6.1 节写化简到标准线性注意力（变体 6）相对原始 TTT 只退化 0.4 困惑度。两者参照对象不同，并不矛盾：按表 2，前者对应表现最好的变体 1（只更新最后一层），后者对应原始 LaCT 基线；原文没有明说这一对应。
7. **测试时学习本身的效果**：Titans Revisited 在冻结主干时只更新记忆，没有观察到有意义的测试时学习；这与原文的设定不同（原文主干与记忆联合训练），不能直接否定原文结论。
8. **版本**：TTT 层为 v4，KV 绑定论文为 v4，Sleep 为 v2，其余 arXiv 论文都只有 v1。嵌套学习论文 HTML 全文页的标题写作「Architecture」，abs 页与 NeurIPS 页为「Architectures」，本篇按 abs 页写。ATLAS 摘要中的「+80% accuracy」按原文转述，没有换算。
9. **嵌套学习论文对上下文学习的两处说法**：arXiv 摘要写上下文学习在大模型中「自然涌现」，第 6 节写它本身不是涌现特性，而是多层级的直接结果。本篇第 8.1 节按第 6 节写。

## 十三、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[测试时训练]] | 前置：该篇脉络中的 TTT 层与 LaCT 是本篇 Titans 并行算法与 TNT 所针对瓶颈的出发点 | In-Place TTT、TEMPO、Modular TTT |
| [[持续学习]] | 路线：嵌套学习用多频率记忆在参数内吸收新知识，是该篇所写「参数内吸收」路线上的一种架构做法 | 综述地图与通用技法 |
| [[线性注意力与状态空间模型谱系]] | 统一：Miras 把该篇谱系中的线性注意力、Mamba2、DeltaNet、Gated DeltaNet 纳入关联记忆框架；KV 绑定论文则反过来把 TTT 改写为线性注意力 | 线性注意力与 SSM 的谱系与推导 |
| [[条件记忆与查表稀疏Engram]] | 区分：该篇的记忆是训练后固定、按 token 序列查表的参数；本篇的记忆是推理时随上下文写入的权重 | 查表式条件记忆 |
| [[智能体长程记忆]] | 区分：该篇的记忆在模型外部，由智能体读写；本篇的记忆在模型内部，由梯度写入 | 智能体外部记忆系统与生产记忆层 |
| [[优化器与训练稳定性]] | 对照：ATLAS 用该篇所写的 Muon 更新记忆；嵌套学习把动量与 Adam 重新解释为压缩梯度的关联记忆 | 优化器谱系 |
| [[OnPolicy蒸馏OPD范式]] | 应用：Sleep 的知识播种结合了在线策略蒸馏与基于强化学习的模仿学习 | OPD 的目标函数与工业配方 |
| [[门控注意力与注意力汇]] | 对照：Titans 的持久记忆有一项动机是因果注意力偏向开头 token，开头放可学习参数可以重新分配注意力权重（Titans 第 3.3 节引 Xiao 等）；TNT 的基线之一是带门控的 Transformer（TNT 第 5.1 节引门控注意力论文）。注意力汇的成因与门控注意力本身归该篇 | 注意力汇与门控注意力 |

## 十四、延伸阅读

建议顺序：先读 Titans 理解神经长期记忆与三种组合；再读 Miras 建立统一框架；然后读嵌套学习论文（可先读 Google Research 博文）；最后读 Titans Revisited 与 KV 绑定论文了解复现与争议。ATLAS、TNT 可按需要补读。

| 文献 | 链接 | 与本篇的关系 |
|---|---|---|
| Learning to (Learn at Test Time): RNNs with Expressive Hidden States（Sun et al., 2024） | https://arxiv.org/abs/2407.04620 | TTT 层（前置） |
| Titans: Learning to Memorize at Test Time（Behrouz et al., 2024） | https://arxiv.org/abs/2501.00663 | 神经长期记忆 |
| 同上，NeurIPS 2025 论文页 | https://proceedings.neurips.cc/paper_files/paper/2025/hash/a4ca07aa108036f80cbb5b82285fd4b1-Abstract-Conference.html | 会议版摘要 |
| It's All Connected: A Journey Through Test-Time Memorization, Attentional Bias, Retention, and Online Optimization（Behrouz et al., 2025） | https://arxiv.org/abs/2504.13173 | Miras 统一框架 |
| ATLAS: Learning to Optimally Memorize the Context at Test Time（Behrouz et al., 2025） | https://arxiv.org/abs/2505.23735 | Omega 规则与记忆容量 |
| Test-Time Training Done Right（Zhang et al., 2025） | https://arxiv.org/abs/2505.23884 | LaCT（前置） |
| Titans Revisited: A Lightweight Reimplementation and Critical Analysis of a Test-Time Memory Model（Di Nepi et al., 2025） | https://arxiv.org/abs/2510.09551 | 独立复现 |
| Introducing Nested Learning: A new ML paradigm for continual learning（Google Research, 2025） | https://research.google/blog/introducing-nested-learning-a-new-ml-paradigm-for-continual-learning/ | 嵌套学习的通俗介绍 |
| TNT: Improving Chunkwise Training for Test-Time Memorization（Li et al., 2025） | https://arxiv.org/abs/2511.07343 | 训练效率 |
| Nested Learning: The Illusion of Deep Learning Architectures（Behrouz et al., 2025） | https://arxiv.org/abs/2512.24695 | 嵌套学习、CMS 与 Hope |
| 同上，NeurIPS 2025 论文页 | https://proceedings.neurips.cc/paper_files/paper/2025/hash/4309616aaed8e848009bc4a7ef73b493-Abstract-Conference.html | 会议版摘要 |
| Test-Time Training with KV Binding Is Secretly Linear Attention（Liu et al., 2026） | https://arxiv.org/abs/2602.21204 | 线性注意力解释 |
| Federated Nested Learning: Collaborative Training of Self-Referential Memories for Test-Time Adaptation（Chen et al., 2026） | https://arxiv.org/abs/2605.16350 | 联邦学习延伸 |
| Language Models Need Sleep: Learning to Self-Modify and Consolidate Memories（Behrouz et al., 2026） | https://arxiv.org/abs/2606.03979 | 离线巩固 |
| Proteus: Incremental Memory Activation for Long-Context Sequence Modeling（Bayat et al., 2026） | https://arxiv.org/abs/2608.16844 | 容量调度 |
| VisionHOPE: Visual Backbones as Self-Modifying Learning Systems（Peng et al., 2026） | https://arxiv.org/abs/2609.33325 | 视觉骨干延伸 |
