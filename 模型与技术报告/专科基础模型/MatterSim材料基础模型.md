---
title: "Materials FM：MatterSim（跨元素 / 温压的原子势与物性预测）"
topic: MatterSim材料基础模型
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - `https://arxiv.org/pdf/2405.04967`；
arxiv: ["2405.04967"]
related: ["生物学基础模型", "天气气候基础模型"]
blog: "https://www.microsoft.com/en-us/research/publication/mattersim-a-deep-learning-atomistic-model-across-elements-temperatures-and-pressures/"
docs: "https://microsoft.github.io/mattersim/"
github: "https://github.com/microsoft/mattersim"
archived: 2026-09-22
---

# Materials FM：MatterSim（材料原子势 / 物性预测）

> **定位**：材料基础模型主题轴——相对 **[[生物学基础模型]]**（biology FM）与 **[[天气气候基础模型]]**（weather / Earth-system FM）的 **正交平行线**：对象从蛋白坐标 / 地球场，落到 **原子图上的通用机器学习力场（MLFF）+ 宽温压物性**。主锚为 Microsoft Research AI for Science 的 **MatterSim**（arXiv **2405.04967v2**）。
> **攻坚线**：**架构思想（主）**——主动学习拓宽构型空间 + 双骨干（M3GNet / Graphormer）分工；**评测字段（辅）**——能量/力/应力、声子、Gibbs 自由能、相图、MatBench 族。
> **硬划界**：
> - **禁止**重写 AF3 / ESM3 / Aurora（→ 只在接口表点名「科学 FM 平行轴」）。
> - **禁止**写成 DFT / MD / LAMMPS 作业手册或合成路径操作指南。
> - **禁止编造**：参数量、meV、F1、数据规模一律锚定官方 PDF（2026-09-22 CST）与官网文档 / README；图版柱高未抽出者标「待核实读图」。
> - 开源权重叙事以 **文档 + GitHub README** 为准，**不**回写覆盖论文主结果数字。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Yang et al., *MatterSim: A Deep Learning Atomistic Model Across Elements, Temperatures and Pressures* | arXiv:**2405.04967v2** \[cond-mat.mtrl-sci\] **10 May 2024**；`https://arxiv.org/pdf/2405.04967`；（**86** 页；38,910,922 bytes） | 一手：主动学习数据、双骨干、零样本 MLFF、自由能/相图、微调与 MatBench |
| **辅（发布页）** | MSR Publication 页（摘要口径与主文一致） | https://www.microsoft.com/en-us/research/publication/mattersim-a-deep-learning-atomistic-model-across-elements-temperatures-and-pressures/ → | 入口与作者列表；**不**替代 PDF 数字 |
| **辅（文档）** | MatterSim **1.0.0** Sphinx 文档 | https://microsoft.github.io/mattersim/ → | 可安装预训练：**v1.0.0-1M / 5M**（**M3GNet**）；进阶权重指向 Azure Quantum Elements |
| **辅（代码）** | `microsoft/mattersim` README | https://github.com/microsoft/mattersim → | `pip install mattersim`；**Python ≥ 3.12**；预训练目录说明 |

**一句话抓手：** MatterSim 不是「再做一个近平衡晶体能量回归器」，而是用 **主动学习 + 第一性原理监督** 把训练分布推到 **0–5000 K、0–1000 GPa** 的离平衡构型，开箱即用当 **通用 MLFF**（前 **89** 元素），并可 **微调换理论层级** 或做 **结构→物性** 端到端预测。

---

## 二、议题边界：何谓「材料 / 原子势 foundation」

### 2.1 相对 [[生物学基础模型]] / [[天气气候基础模型]] 的平行轴（跟读必钉）

| 轴 | **[[生物学基础模型]] biology** | **[[天气气候基础模型]] weather** | **本卡 MatterSim** |
|---|---|---|---|
| 对象几何 | 生物分子原子坐标 / 蛋白 token | 球面上多通道 3D 地球场 | **周期边界材料图**（原子节点 + 键边） |
| 「Foundation」含义 | 统一结构预测或序列–结构–功能生成 | 异构地球数据 → 统一 latent → 多域微调 | **宽化学 + 宽温压构型**上的通用原子势；可继续主动学习 / 微调 |
| 默认下游 | 结构预测或可控生成 | 自回归场预报 | **能量 / 力 / 应力** → 弛豫、声子、MD、自由能、相图；或端到端物性头 |
| 本篇覆盖 | ✗ | ✗ | ✓ |

跟读：**不要把 MatterSim 的温压 MD 写成 Aurora 的天气 rollout；也不要把材料图消息传递当成 AF3 的坐标扩散。**

### 2.2 相对既有「通用 MLFF」叙事（文内自述）

文内把 MPF / Alexandria 等 **弛豫轨迹库** 批评为：近局域极小、结构冗余、元素偏置 → 不足以支撑 **有限温压** 下的动力学。MatterSim 的主张是：用 **材料探索器 + ensemble 不确定性 + 批量主动学习**，在 PBE(+U，Materials Project 标准) 监督下扩到 **∼17M** 第一性原理标注结构，从而在 MPF-TP / Random-TP 等高温高压集上相对「只吃弛豫轨迹」的通用势有 **可达约 10×** 的精度提升（摘要 / §2.1；Table S1）。

### 2.3 刻意不写什么

- VASP / Quantum ESPRESSO 输入卡、赝势选型、k 点收敛操作步骤。
- LAMMPS / ASE 部署 playbook（文档有 Integration / Examples 入口，仅作**存在性**）。
- 完整通用 MLFF 族谱通史（CHGNet / MACE / GNoMe 等只在文内主结果出现时点名）。
- 催化剂表面反应机理或有机合成路径。

---

## 三、架构思想：材料图 → 双骨干 → 力 / 应力

> 核心问题：**同一套表示，如何同时服务「快、能跑长 MD」的零样本力场，和「吃更大数据、更准」的发现 / 端到端物性？**

`
材料结构 ──► 材料图 G=(Z, V, R, [L, S]) （径向截断构图）
 │
 ┌───────┴────────┐
 ▼ ▼
 M3GNet（不变 GNN Graphormer（Transformer
 + 显式三体） + 材料适配）
 参数 ~0.88M→4.5M 总参 182M
 （数据至 ~3M）
 │ │
 ▼ ▼
 能量 E；力/应力 = ∂E（或专用 stress head）
 │
 ├── 零样本：弛豫 / 声子 / MD / 自由能（文内主用 M3GNet）
 └── MatBench Discovery + 端到端物性（文内主用 Graphormer）
`

### 3.1 材料图与对称性（SI §S1.1）

- 节点 = 原子（原子序 $Z_i$ 等）；边由径向截断 $r_c$ 连接；可选全局标量 $S$（温压等）与晶格 $L$。
- 标量性质（总能量）保持 **旋转–平移不变**；力等矢量性质要求 **等变**（文述 MatterSim 维持该约束）。

### 3.2 骨干 A：M3GNet（零样本默认）

| 文内事实 | 跟读 |
|---|---|
| 不变图网络；**显式二体 + 三体**消息传递（球 Bessel / 球谐 + 光滑截断） | 继承 Chen & Ong 2019/2022 线；本文 **PyTorch 重实现**（并注明 MatGL 另有 PyTorch 版） |
| 力 $f=-\partial E/\partial r$、应力经应变对能量求导（自动微分） | 保守力场 → 适合 MD |
| 损失：Huber；$\omega_f=1$，$\omega_\sigma=0.1$；Adam，初学率 **0.001**，200 epochs，batch **128**，**8×A100** | SI §S1.4 |
| 数据增至 **~3M** 时，参数由 **880K → 4.5M**；再盲目加参在当时设定下不稳定 | 规模与稳定性边界 |

### 3.3 骨干 B：Graphormer（更大容量）

| 文内事实 | 跟读 |
|---|---|
| Transformer；结构编码器 + 性质解码器；加 **平移不变 / 周期边界 / 显式等变特征**（相对原 Graphormer 的材料适配，SI §S1.3） | 「能吃更大数据」的一侧 |
| 编码器 **24** 注意力层；解码器 **10** 层 GeoMFormer（应力头 **2** 层）；头数 **32**；隐层 **768**；总参 **182M** | SI §S1.4 |
| AdamW；峰值 LR **2e-4**；**1,562,500** steps（warmup **93,750**）；batch **256**；**64×A100**；先训能量+力，再冻干训应力头 | 两阶段应力头（Fig. S4） |
| 同尺度下相对 M3GNet：更准但更慢、更吃显存（例：~100 原子时约 **10×** GPU 显存，Fig. S5） | 任务选骨干，而非「大即一切」 |

### 3.4 任务–骨干分工（正文明确）

- **全部零样本原子模拟（除 MatBench Discovery）→ M3GNet**（推理速度）。
- **MatBench Discovery + 端到端物性 → Graphormer**（精度）。
- 开源文档当前释出的 **MatterSim-v1.0.0-1M / 5M** 均标注基于 **M3GNet**（与论文「零样本用 M3GNet」一致；**Graphormer 权重是否开源：文档未列 → 不臆造**）。

---

## 四、数据与主动学习：把分布推离「只弛豫」

### 4.1 闭环（Fig. 2(a) / §2.1）

`
初始公开/自建近平衡库
 │
 ▼
第一性原理监督（PBE + 选定材料 Hubbard U；MP 标准）
 │
 ▼
深度模型（可作 DFT 代理）
 │
 ▼
材料探索器：近平衡 + 离平衡（宽温压）采样
 │
 ▼
ensemble 不确定性监视 → 批量主动学习（避免重标高置信）
 │
 └──► 迭代 → 发布时 ~17M 标注结构
`

### 4.2 覆盖主张（只录文内句）

| 主张 | 锚点 |
|---|---|
| 温压直方图覆盖 **0–5000 K、0–1000 GPa** | Fig. 2(b)；摘要 |
| 相对弛豫库，平均 **2–3×** 更多相异原子环境；惰性气体等可达 **10×+** | §2.1；Fig. S13 |
| 元素对分布更均匀（相对氧化物偏置） | Fig. S11 等 |
| 当前支持周期表前 **89** 元素任意组合（零样本设定） | §2.2 |

---

## 五、评测字段（辅线；禁读图编造）

### 5.1 能量 / 力 / 应力（Table S1 摘要）

摘要主数字：**MPF-TP** 上能量 MAE **36 meV/atom**（并对照化学精度 **43 meV/atom**），称相对先前 best-in-class 可达约 **10×**。Table S1（eV 单位）可核对：

| 测试集 | 量 | M3GNet† | CHGNet | MACE-MP-0 | **MatterSim (M3GNet)** | MatterSim (Graphormer) |
|---|---|---|---|---|---|---|
| **MPF-TP** | Energy [eV/atom] | 0.207 | 0.254 | 256.340 | **0.036** | 0.0400 |
| **MPF-TP** | Force [eV/Å] | 1.224 | 3.313 | 1506.854 | **0.431** | 0.421 |
| **Random-TP** | Energy [eV/atom] | 0.537 | 0.506 | 9.184 | **0.219** | **0.141** |

†表中「M3GNet」列为对比开源检查点，**不是** MatterSim-M3GNet。高温高压集上差距最大——这是文内「必须吃离平衡数据」的证据链。

### 5.2 材料发现

| 指标 | 文内数字 | 锚点 |
|---|---|---|
| MatBench Discovery | **F1 = 0.83**；形成能 MAE 正文写 **25 meV/atom**；Table S2 MAE **0.03**（表列单位与正文 meV 表述并存，**以各表/句原文为准，不手工换算强行合一**） | §2.2；Table S2 |
| Table S2 对照 | GNoMe F1 0.81；CHGNet 0.58；M3GNet 0.57；MACE 0.57 等 | Table S2 |
| RSS 规模 | **4,005** 元/二元体系 × 每体系约 **20,000** 候选 ≈ **8,000 万** 结构；DFT 复核后 **16,399** 结构落在或低于 Alexandria-MP-ICSD 凸包；其中 **852** 在合并凸包上且相对原库为新（元素分布见 Fig. 3；含阴离子校正排除注） | §2.2 |

### 5.3 声子 / 力学 / 自由能 / 相图

| 任务 | 文内主数字 | 锚点 |
|---|---|---|
| 最大声子频率 vs PhononDB | MAE **0.87 THz** | Fig. 4(a) |
| 0 K 体模量 | MAE **2.47 GPa** | Fig. 4(c) |
| AlN 体温模量（例） | 相对第一性原理 MAE **0.97 GPa**；至 1000 K 误差 **<5%** | Fig. 4(d) |
| Gibbs 自由能 vs PBE-QHA | 至 1000 K **sub-10 meV/atom** | Fig. 4(e)、Fig. S21 |
| vs 实验（>200 材料） | MAE **15 meV/atom**（称低于专训实验数据的模型） | Fig. S22；§2.2 |
| MgO B1→B2（300 K） | MatterSim **584 GPa**；实验 **429–562 GPa**；近期第一性原理 **520 GPa** | Fig. 4(f) |

### 5.4 MD 稳健性

对 **118** 个体系（体相、MOF、2D、界面、分子晶体、聚合物、表面等）做 0→5000 K 升温；成功率定义为实际运行时长 / 预设总时长。文称各材料族成功率 **>90%**；体相另做 0→1000 GPa 压缩后再升温，平均完成率亦 **>90%**（Fig. 5）。

### 5.5 主动学习 / 微调数据效率（水为例）

- 零样本 PBE 级 MatterSim 对液态水结构/动力学不佳——文归因为 **PBE 本身** 对水的已知缺陷，而非「模型不会泛化」的唯一解释。
- 用 **rev-PBE0-D3** AIMD 轨迹：**finetune-30**（30 构型）达到与 **scratch-900** 相当的结构性质；自扩散 $D=1.862\times10^{-5}\,\mathrm{cm}^2/\mathrm{s}$，相对实验误差 **<20%**；数据量约为从头训的 **1/30**（≈摘要「最高可减 **97%** 数据」口径）。
- 复杂固体（如 $\mathrm{Li_2B_{12}H_{12}}$）可用 ensemble 不确定性主动加标少量帧恢复精度（Fig. 6）。

### 5.6 端到端 MatBench（Table 1；越低越好）

| Property | Specialized | From scratch | **MatterSim** |
|---|---|---|---|
| MP Gap (eV) | 0.1559 | 0.3031 | **0.1290** |
| log GVRH (GPa) | 0.0670 | 0.0895 | **0.0608** |
| log KVRH (GPa) | 0.0491 | 0.0687 | **0.0488** |
| Dielectric | 0.2711 | 0.3823 | **0.2516** |
| Phonons (cm⁻¹) | 28.7606 | 65.8220 | **26.0220** |
| jdft2d (meV/atom) | 33.1918 | 47.8040 | **32.7620** |

文称：在本工作大规模库上预训练后，提升**与骨干选择无关**（Table S5）——强调 **数据覆盖** 对可迁移材料特征的重要性。

---

## 六、开源与产品增量（文档 / README；与 PDF 主结果隔离）

| 项 | 可核事实（2026-09-22 抓取） | 笔记处理 |
|---|---|---|
| 安装 | `pip install mattersim`；或 git 源码；**Python ≥ 3.12** | 存在性；不写排错手册 |
| 开放权重 | **MatterSim-v1.0.0-1M**（更快）、**v1.0.0-5M**（更准）；均为 **M3GNet** | 与论文零样本骨干一致 |
| 文档能力页 | Installation / Getting Started / TorchSim / Finetune / LAMMPS；Examples：弛豫、声子、批量弛豫 | 仅索引 |
| 闭源进阶 | 文档：「More advanced… available in **Azure Quantum Elements**」 | **不**编造其内部模型规格 |
| 论文正文 | 未见独立 “Code availability” 专节（至 Acknowledgements）；开源叙事以仓库/文档为准 | 版本关系钉清 |

---

## 七、局限与开放轴（论文 Discussion 自述）

压缩自 §3 Discussion（不扩写工程对策）：

1. **半局域相互作用**：长程主要靠消息传递 / 注意力；在 **聚合物、异质结** 等长程主导场景仍弱。
2. **数据覆盖**：主训 **均匀体相**；**表面 / 界面 / 催化** 未显式纳入。
3. **理论层级**：原生主要 **DFT-PBE(+U)**；复杂聚合物与有机液体等需更高阶理论时，依赖微调或未来多任务预训练。
4. **输出模态**：原生能量 / 力 / 应力；电荷、自旋、磁矩、更丰富电子结构特征尚未纳入。
5. **半监督预训练** 被点名为继续抬数据效率 / 精度的方向。

---

## 八、与仓库相邻笔记的接口

| 笔记 | 接口一句 | 本篇不写 |
|---|---|---|
| **[[生物学基础模型]]** | 同属「科学 foundation」横切；对象从生物分子 → **无机/材料原子势** | AF3 扩散步、ESM3 token |
| **[[天气气候基础模型]]** | 同属 MSR AI for Science 叙事邻居；Aurora = 地球场模拟器，MatterSim = 原子图力场 | 3D Perceiver / 天气四域 |
| **[[科研智能体]] science agents**（若后续成稿） | 可把 MatterSim 当「材料工具」存在性索引 | ChemCrow 操作链 |
| **[[多模态架构脉络]] / B10** | Graphormer 血统可点名 Transformer；此处是 **3D 材料图** 而非图文 | VL 通史 |

---

## 九、对照卡（跟读）

| 维度 | 典型「弛豫库通用 MLFF」 | **MatterSim（论文）** | **开源 v1 文档切片** |
|---|---|---|---|
| 训练分布 | 近平衡弛豫轨迹为主 | ~17M；主动学习扩到宽温压离平衡 | 文称沿用稿内 workflow 数据 |
| 骨干 | 各家 GNN/等变网 | **M3GNet（快）∥ Graphormer 182M（准）** | 公开 **1M / 5M M3GNet** |
| 零样本半径 | 多在近平衡能量好 | 宣称 0–5000 K、0–1000 GPa；89 元素 | 文档：跨元素/温压模拟 |
| 可定制 | 常需重训 | 主动学习加标 + 换理论微调（水：~3% 数据） | 文档有 Finetune 页 |
| 不该问它的问题 | 「已替代全部 DFT」 | 同左；外加「已覆盖催化界面 / 长程聚合物」——文**自承未覆盖** | 同左；Azure 进阶规格勿臆造 |

`
弛豫库 MLFF： 近平衡结构 ──► GNN ──► E/F（近平衡准）
MatterSim： 近平衡 + 离平衡主动学习 ──► 双骨干 ──► 零样本温压模拟
 └── 微调换理论 / 端到端物性头
`

---

## 十、可跟读摘要

1. **平行线**：[[生物学基础模型]] 生物、[[天气气候基础模型]] 天气之后，本卡补 **材料原子尺度 FM**；对象是 **材料图上的通用力场**，不是蛋白扩散或地球场预报。
2. **架构一句**：**主动学习扩构型** + **M3GNet（零样本 MD）∥ Graphormer 182M（发现/物性）**；力由能量导数给出。
3. **主数字**：~**17M** 结构；MPF-TP 能量 MAE **36 meV/atom**；MatBench Discovery **F1 = 0.83**；最大声子频率 MAE **0.87 THz**；相对实验 Gibbs 自由能 MAE **15 meV/atom**；水微调约 **1/30** 数据。
4. **开源**：文档 **v1.0.0-1M / 5M（M3GNet）** + `pip install mattersim`；进阶在 Azure Quantum Elements。
5. **禁区**：不是 DFT 作业手册；不是「已解决催化界面与长程有机」；不要和 AF3/Aurora 混写。

---

## 十一、验收自检

- [x] 立轴为 **materials / 原子势 FM 架构思想**，相对 [[生物学基础模型]] / [[天气气候基础模型]] **正交平行**，**未**重写 biology / weather 正文。
- [x] 双骨干分工、主动学习闭环、~17M / 89 元素 / 温压范围写清。
- [x] 评测数字均有句点或表号；MatBench Discovery 正文 25 meV 与 Table S2 MAE 0.03 **并存标注**，未擅自「统一」。
- [x] 开源权重仅用文档/README；Azure 进阶仅存在性。
- [x] 中文可跟读；禁编造；YAML `date: 2026-09-22status: draft`。
- [x] PDF 已落盘：`https://arxiv.org/pdf/2405.04967`；抽取在 。

## 相关笔记

- [[MatterSim材料基础模型|MatterSim]]
- [[芯片设计AI|AlphaChip / ChipExpert]]
- [[科研智能体|Science Agents]]
- [[AgentBazaar经济对齐|Agent Bazaar]]
- [[网络防御基准|Cyber Defense Benchmark]]

