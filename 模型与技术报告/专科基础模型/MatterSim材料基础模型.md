---
title: "Materials FM：MatterSim（跨元素 / 温压的原子势与物性预测）"
topic: MatterSim材料基础模型
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2405.04967
arxiv: ["2405.04967"]
related: ["生物学基础模型", "天气气候基础模型", "MatterGen与MACE"]
blog: "https://www.microsoft.com/en-us/research/publication/mattersim-a-deep-learning-atomistic-model-across-elements-temperatures-and-pressures/"
docs: "https://microsoft.github.io/mattersim/"
github: "https://github.com/microsoft/mattersim"
archived: 2026-09-22
---

# Materials FM：MatterSim（跨元素 / 温压的原子势与物性预测）

> **主要来源**：[MatterSim: A Deep Learning Atomistic Model Across Elements, Temperatures and Pressures](https://arxiv.org/abs/2405.04967)；[MatterSim 1.0.0 documentation](https://microsoft.github.io/mattersim/)；[microsoft/mattersim README](https://github.com/microsoft/mattersim)（截至 2024-05-10）。论文以 arXiv v2 为准；文档与 README 没有更新日期，不计入时间锚点。
> **研究线**：架构思想（主：主动学习把训练分布推到宽温压离平衡构型，M3GNet 与 Graphormer 双骨干按任务分工）；评测字段（辅：能量、力、应力，声子，自由能与相图，MatBench）
> **范围与相邻笔记**：
> - ≠ [[生物学基础模型]]：生物分子结构预测与生成在那篇，本篇对象是材料原子图上的力场。
> - ≠ [[天气气候基础模型]]：地球系统场的预报在那篇，本篇的温压分子动力学不是天气 rollout。
> - ≠ [[MatterGen与MACE]]：材料生成与跨域统一力场在那篇，本篇只写 MatterSim 本身。
>
> **意义**：此前的通用机器学习力场多在弛豫轨迹上训练，只在近平衡结构上准。MatterSim 用主动学习加第一性原理标注，把训练数据推到 0–5000 K、0–1000 GPa 的离平衡构型，开箱即可作周期表前 89 种元素的零样本力场，在高温高压测试集上的误差比此前的通用力场最多低 10 倍，并可用少量数据微调到更高理论层级或直接预测物性。

## 一、问题背景

材料设计需要在巨大的组成与结构空间里，按真实工况的温度和压力预测性质。第一性原理计算准确但昂贵；机器学习力场快，但泛化受训练数据覆盖限制。论文指出，现有数据库存在明显的化学与结构偏置：多数开放数据库由实验晶体结构经第一性原理弛豫得到，弛豫轨迹集中在局域能量极小附近、结构高度冗余，用它训练的模型难以模拟有限温压下的材料（§1、§2.1）。

另一类需求是从结构直接预测物性。领域数据少时，专门训练的模型误差往往太大而难以实用（§2.5）。MatterSim 想用同一套大规模预训练同时服务这两类需求。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2021-06 | [Graphormer](https://arxiv.org/abs/2106.05234) | 把 Transformer 用到图表示学习，后被 MatterSim 改造为材料骨干 |
| 2022-02 | [M3GNet](https://arxiv.org/abs/2202.02450) | 带显式三体相互作用的不变图网络，覆盖周期表的通用原子势 |
| 2023-02 | [CHGNet](https://arxiv.org/abs/2302.14231) | 在 Materials Project 轨迹上预训练的通用图网络势 |
| 2023-12 | [MACE-MP-0](https://arxiv.org/abs/2401.00096) | 用 MPtrj 训练的 MACE 基础势，是 MatterSim 的对照基线之一 |
| 2024-05 | [MatterSim](https://arxiv.org/abs/2405.04967) | 主动学习覆盖宽温压构型，双骨干分别承担零样本模拟与物性预测 |

## 三、核心机制

### 3.1 材料图与双骨干

材料结构被编码成图：节点是原子，边按径向截断连接，可附晶格与全局标量。总能量对旋转和平移不变，力和应力由能量对坐标与应变求导得到（SI §S1.1）。

| 骨干 | 设计 | 规模与训练（SI §S1.4） |
|---|---|---|
| M3GNet | 不变图网络，显式二体与三体消息传递；论文用 PyTorch 重新实现 | 训练数据增至 3M 时，参数由 880K 增至 4.5M；在当时设定下继续加参会不稳定；8 张 A100 |
| Graphormer | Transformer 结构编码器加性质解码器，补入平移不变、周期边界与显式等变特征（SI §S1.3） | 编码器 24 个注意力层，解码器 10 层 GeoMFormer（应力头 2 层），32 头，隐层 768，总参 182M；1,562,500 步，64 张 A100；先训能量与力，再单独训应力头 |

Graphormer 容量更大、潜在精度更高，但计算更慢、显存需求明显更高，大体系常触及 A100 的显存上限（SI §S1.5）。因此论文按任务分工：除 MatBench Discovery 外的零样本原子模拟都用 M3GNet，MatBench Discovery 与端到端物性预测用 Graphormer。

### 3.2 主动学习数据

闭环由四部分组成：深度图网络、材料探索器、第一性原理监督（PBE，部分材料加 Hubbard U，沿用 Materials Project 标准）和集成不确定性监视（§2.1，Fig. 2(a)）。探索器同时采样近平衡与离平衡构型，按集成模型的不确定性批量挑选需要标注的结构。

截至论文发布，训练集约 17M 个第一性原理标注结构，温压覆盖 0–5000 K、0–1000 GPa。补充材料 §S3 的覆盖度分析称，在整个周期表上平均，本数据集的覆盖度是 MPtrj 的 3 倍、Alexandria 的 2.15 倍；MPtrj 与 Alexandria 中稀有气体元素样本极少。

### 3.3 开源权重

文档与 README 提供两个基于 M3GNet 的预训练模型：MatterSim-v1.0.0-1M（更快）与 MatterSim-v1.0.0-5M（更准），用论文所述流程生成的数据训练；更高级的版本在 Azure Quantum Elements 中提供。这与论文「零样本模拟用 M3GNet」一致；Graphormer 权重未见公开。

## 四、主要结果

| 任务 | 论文数字 | 出处 |
|---|---|---|
| 高温高压能量（MPF-TP） | 能量 MAE 36 meV/atom（化学精度 43 meV/atom）；相对此前通用力场误差最多低 10 倍 | §1、§2.2，Table S1 |
| MatBench Discovery | F1 0.83，形成能 MAE 25 meV/atom | §2.2，Table S2 |
| 随机结构搜索 | 4,005 个一元与二元体系，每体系 20,000 个候选，总计约 80 million 个结构；DFT 复核后 16,399 个结构位于或低于 Alexandria-MP-ICSD 凸包；排除阴离子校正可能影响的元素后，852 个材料位于合并凸包上 | §2.2，SI §S8 |
| 声子 | PhononDB 最大声子频率 MAE 0.87 THz | §2.2 |
| 力学 | 0 K 体模量 MAE 2.47 GPa；AlN 体模量随温度变化的 MAE 0.97 GPa，至 1000 K 误差小于 5% | §2.2 |
| 自由能与相图 | 至 1000 K 与 PBE 准谐近似相比误差 sub-10 meV/atom；对 200 余种材料的实验值 MAE 15 meV/atom；MgO 在 300 K 的 B1→B2 相变压力预测 584 GPa，实验 429–562 GPa，第一性原理 520 GPa | §2.2 |
| 分子动力学稳健性 | 118 个体系从 0 升温到 5000 K，各材料族成功率均超过 90%；体相加压至 1000 GPa 后升温，平均完成率也在 90% 以上 | §2.2 |
| 微调 | 液态水只用 30 个 rev-PBE0-D3 构型微调，结构性质即达到用全部 900 个构型从头训练的水平；自扩散系数与实验误差低于 20%；摘要称数据需求最多减少 97% | §2.4 |
| 端到端物性 | MatBench 六项（带隙、剪切与体模量、介电、声子、二维剥离能）均优于专门模型与从头训练；预训练带来的提升与骨干无关（Table S5） | §2.5，Table 1 |

零样本 PBE 级模型模拟液态水时结构过强，论文归因于 PBE 泛函本身对水的已知缺陷，因此用更高理论层级的少量数据微调。

## 五、意义

MatterSim 的主张是：通用力场的瓶颈在数据覆盖而不只在架构。主动学习把训练分布从近平衡推到宽温压，零样本力场随之能做声子、自由能、相图和长时分子动力学；同一份预训练还能迁移到端到端物性预测，且提升与骨干无关。双骨干分工也说明，任务按速度与精度选骨干，比一味加大模型更实际。

## 六、局限与待核实

1. **论文自述的局限**（§3）：原子相互作用是半局域描述，在聚合物、异质结等长程主导的体系上效果不佳；只在均匀体相上训练，未显式纳入表面与界面数据，催化等应用受限；原生只支持 DFT-PBE 理论层级；只输出能量、力、应力，电荷、自旋、磁矩等尚未纳入；半监督预训练被列为后续方向。
2. **版本差**：v2（2024-05-10）相对 v1（2024-05-08）主要是措辞修订与参考文献重排；摘要对端到端预测的说法由 v1 的「达到 SOTA」改为 v2 的「优于只用领域数据训练的专门模型」。本篇以 v2 为准。
3. **开源与论文的对应**：公开权重只有 M3GNet 版，论文中 Graphormer 的结果（MatBench Discovery 与端到端物性）无法用公开权重复现；Azure Quantum Elements 中更高级版本的规格未公开。
4. **图中数字**：温压直方图、元素分布、显存对比等只在图中给出，本篇不录。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[生物学基础模型]] | 同属科学基础模型，对照对象的差别：生物分子坐标与材料周期图 | 生物分子结构预测与生成 |
| [[天气气候基础模型]] | 同属科学基础模型，对照「大规模预训练加领域微调」的做法 | 地球系统场的预报 |
| [[MatterGen与MACE]] | 边界：材料生成与跨域统一力场见 [[MatterGen与MACE]] | 那篇中的任何结果 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [MatterSim arXiv（v2）](https://arxiv.org/abs/2405.04967v2) | 主动学习闭环、双骨干设定与附录里的评测表 |
| 2 | [MatterSim 文档](https://microsoft.github.io/mattersim/) | 安装、微调与示例 |
| 3 | [microsoft/mattersim](https://github.com/microsoft/mattersim) | 预训练权重与用法 |
