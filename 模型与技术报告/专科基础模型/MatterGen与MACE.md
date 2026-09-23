---
title: "材料科学增量：MatterGen（生成）+ MACE 跨域统一力场（≠ MatterSim）"
topic: MatterGen与MACE
date: 2026-09-22
lines: [架构思想, 任务接口]
status: archived
sources:
 - https://arxiv.org/abs/2510.25380 # 1.60MB / 22p → 外链引用
arxiv: ["2312.03687", "2510.25380", "2401.00096"]
doi:
 - "10.1038/s41586-025-08628-5" # MatterGen Nature 正式刊
related: ["MatterSim材料基础模型", "生物学基础模型", "天气气候基础模型", "蛋白质设计"]
github_mattergen: "https://github.com/microsoft/mattergen"
github_mace: "https://github.com/ACEsuit/mace"
github_mace_foundations: "https://github.com/ACEsuit/mace-foundations"
github_mace_mp: "https://github.com/ACEsuit/mace-mp"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 材料科学增量：MatterGen（生成）+ MACE 跨域统一力场（≠ MatterSim）

> **定位**：材料生成与统一力场方法轴——相对 **[[MatterSim材料基础模型]] MatterSim**（宽温压 MLFF / 物性**预测**主轴）的**正交增量**：
> - **MatterGen**：条件**生成式**无机晶体设计（扩散联合精炼原子类型 / 坐标 / 晶格 + adapter 微调）。
> - **MACE 跨域统一力场**（2510.25380）：分子 / 表面 / 无机晶体 **cross-domain** 多头 replay 后训练；以 **MACE-MP-0**（2401.00096）为 foundation 谱系基线（**正式外链**）。
> **攻坚线**：**架构思想 / 任务接口（生成 vs 力场）（主）** + **文内稳定性 / 物性 / 跨域榜字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[MatterSim材料基础模型]] MatterSim**：不重写主动学习温压构型、M3GNet/Graphormer 双骨干、0–5000 K / 0–1000 GPa、Gibbs/相图主文。MatterGen 文内把 MatterSim 当 **pre-relax / 稳定性过滤 MLFF**（与 RSS/substitution 同配）——本卡只录**接口句**，禁止展开 MatterSim 方法。2510.25380 把 `mattersim-5M` 当跨域对照基线——只录榜名与文内得分，不复述 MatterSim 架构。
> - **≠ [[生物学基础模型]]**：不写 AF3 坐标扩散 / ESM3 多轨道蛋白 LM。
> - **≠ [[天气气候基础模型]]**：不写 Aurora / Earth-system 场预报。
> - **≠ [[蛋白质设计]]**：不写 RFdiffusion / BindCraft 蛋白 binder 设计。
> **禁止编造**：主张与数字一律锚定本地抽取（2026-09-22 CST）。MatterGen **主数字以 arXiv:2312.03687v2 抽取为准**；Nature 正式刊作刊发线 / 实验验证存在性补链（摘要口径「>10× 更近能量最低点」与 arXiv「>15×」不一致处标清来源，**不以刊发页覆盖本地抽取表数字**）。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A · MatterGen** | Zeni, Pinsler, Zügner, Fowler, Horton, … Tomioka\*, Xie\*（MSR AI4Science）*MatterGen: a generative model for inorganic materials design* | arXiv:**2312.03687v2** \[cond-mat.mtrl-sci\] **29 Jan 2024**；PDF https://arxiv.org/pdf/2312.03687（**12,150,197 B ≈ 11.59MB**；**56** 页 A4）→ **未入库二进制**；抽取 | **生成式**无机材料：联合扩散 (A,X,L) + adapter 条件微调；S.U.N. / RMSD / 化学·对称·标量物性 |
| **正式刊（同工作）** | *A generative model for inorganic materials design* | *Nature* **639**, **624–632**（2025）；Published **16 Jan 2025**；DOI **10.1038/s41586-025-08628-5**；Open access；https://www.nature.com/articles/s41586-025-08628-5 | 审稿定稿 + **实验合成验证**（刊发页摘要：合成一样品，测得物性在目标 **20%** 内）。**Nature PDF 未另落盘** |
| **主文 B · MACE 跨域** | Batatia\*, Lin\*, Hart, Kasoar, Elena, Norwood, Wolf, Csányi *Cross Learning between Electronic Structure Theories for Unifying Molecular, Surface, and Inorganic Crystal Foundation Force Fields* | arXiv:**2510.25380v1** \[physics.chem-ph\] **29 Oct 2025**（文内 Dated **October 30, 2025**）；`https://arxiv.org/abs/2510.25380`（**1,677,606 B ≈ 1.60MB**；**22** 页 letter） | **跨域统一 MLIP**：MACE 架构增强 + multi-head replay；OMAT 预训练 → 分子/表面/晶体头 |
| **基线 · MACE-MP-0** | Batatia†, Benner†, Chiang†, … Csányi\* *A foundation model for atomistic materials chemistry* | arXiv:**2401.00096v3** \[physics.chem-ph\] **4 Sep 2025**（文内 **September 8, 2025**）；PDF https://arxiv.org/pdf/2401.00096（**84,050,464 B ≈ 80.16MB**；**153** 页）；官方 PDF 外链 | MACE **foundation** 力场（MPtrj）；稳定 MD 广谱演示；fine-tune + multi-head replay 协议源头 |

**代码（文内 / 刊发页明示，本篇不展开部署）：**
- MatterGen → https://github.com/microsoft/mattergen（Nature Data/Code availability）
- MACE → https://github.com/ACEsuit/mace ；foundations → https://github.com/ACEsuit/mace-foundations ；MP 系列 → https://github.com/ACEsuit/mace-mp/

| 文件 | 体积 | 备注 |
|---|---|---|
| MatterGen PDF（arxiv.org） | **≈11.59MB** / 56 页 | **建议正式外链**（>10MB 且页数偏长；本仓**未**落  二进制） |
| `2510.25380-mace-cross.pdf` | **1.60MB** / 22 页 | **官方 HTTPS 外链**（≪20MB） |
| MACE-MP-0 PDF（arxiv.org） | **≈80.16MB** / 153 页 | https://arxiv.org/pdf/2406.17867 |

**一句话抓手：**
- **MatterGen**：别再「筛已知结构」——用 **(A,X,L) 联合扩散** 直接生成跨周期表稳定晶体，再用 **adapter + CFG** 把生成推向化学 / 对称 / 磁密·带隙·体模等约束。
- **MACE-MP-0 → 跨域 MH**：先立 **MPtrj foundation 力场** 可开箱跑稳定 MD；再以 **非线性能量积分解 + 多头 replay** 把分子 / 表面 / 晶体统一到单一连续势（主头常取 PBE/OMAT），避免「每域一势」。

---

## 二、议题边界：生成设计 × 跨域力场 ≠ MatterSim 预测主文

### 2.1 四向对照（跟读必钉）

| 轴 | **[[MatterSim材料基础模型]] MatterSim** | **本卡 MatterGen** | **本卡 MACE-MP-0 / 跨域** | **[[生物学基础模型]] / [[天气气候基础模型]] / [[蛋白质设计]]** |
|---|---|---|---|---|
| 任务 | 原子图 → **能量/力/应力 → 物性预测 / MD** | 噪声结构 → **生成**晶体；条件约束 | 原子坐标 → **统一 MLIP**（跨电子结构理论 / 跨化学域） | 蛋白结构·序列 / 地球场 / binder |
| 「Foundation」含义 | 宽化学 + 宽温压构型上的通用势 | 跨周期表 **S.U.N.** 生成底座 + 条件微调 | 开箱 MD + 少量点微调；再跨域多头 | 生物 / 气象 / 蛋白设计 FM |
| 与 MatterSim 关系 | **主文** | 文内 **调用** MatterSim 做 pre-relax 过滤（接口） | 跨域榜对照 `mattersim-5M`（接口） | 平行科学 FM，对象不同 |
| 本篇是否主写 | ✗（禁重写） | ✓ | ✓（MP-0 作谱系基线，禁巨本二进制） | ✗ |

### 2.2 刻意不写什么

- VASP / QE 输入卡、赝势、k 点收敛操作步骤。
- MatterSim / MACE 的 LAMMPS·ASE 部署 playbook。
- 完整生成模型族谱通史（CDVAE / DiffCSP / GNoME 等只在文内对照出现时点名）。
- 催化剂反应机理细节或合成路径操作层（Nature 实验验证仅录**结果字段存在性**）。

---

## 三、MatterGen：条件生成式无机材料设计

> 核心问题：**如何在周期边界下联合生成原子类型、分数坐标与晶格，并在小标签集上把生成推向目标化学 / 对称 / 标量物性？**

### 3.1 联合扩散过程 (A, X, L)

文内把晶体单位胞定义为原子类型 **A**、坐标 **X**、周期晶格 **L**。前向损坏为各分量定制、并带物理动机的极限噪声分布（§2.1 / Fig. 1a；抽取）：

| 分量 | 损坏几何（文内） | 噪声极限（文内） |
|---|---|---|
| **坐标 X** | 尊重 PBC 的 **wrapped Normal** | 趋向均匀 |
| **晶格 L** | 对称形式；方差保持类扩散 | 均值趋向训练数据平均原子密度的立方晶格 |
| **原子类型 A** | 范畴空间；原子损坏到 **masked** 态 | （mask 终点） |

学习 **等变 score 网络**，分别输出原子类型 / 坐标 / 晶格分数，避免从数据硬学对称性（「base model」）。相对 CDVAE 等基线，文内强调晶格在去噪中**一并演化**（附录对照），而非固定晶格只扩坐标。

### 3.2 Adapter 微调 + classifier-free guidance

属性约束走 **adapter modules**：注入 base 各层，按编码条件 **c** 改写输出；与 **classifier-free guidance** 联用（§2.1；Fig. 1b–c）。动机：属性标签贵、量常远小于无标结构集——微调仍可用。文内覆盖：

- **化学组成**（目标化学体系 + hull≈0）
- **对称性**（空间群）
- **标量物性**：磁密度、带隙、体模量等

### 3.3 数据与 S.U.N. 口径（arXiv v2 抽取）

| 字段 | 文内口径（本地抽取） |
|---|---|
| 预训练集 **Alex-MP-20** | **607,684** 条稳定结构（≤20 原子；自 MP + Alexandria 重算） |
| 稳定 | DFT 弛豫后相对参考凸包 **≤ 0.1 eV/atom** |
| 参考包 **Alex-MP-ICSD** | **1,081,850** unique（MP + Alexandria + ICSD 重算；抽取 §2.2） |
| **Novel** | 不在 Alex-MP-ICSD |
| **S.U.N.** | Stable + Unique + Novel |

**无条件生成质量（抽取 Fig. 2 / §2.2）：**
- 相对 MP 凸包：约 **78%** 在 0.1 eV/atom 下（**13%** 在 0 下）；相对 Alex-MP-ICSD：**75%** / **3%**。
- **95%** 结构相对 DFT 弛豫构型 RMSD **< 0.076 Å**。
- 生成 1000 条时 unique **100%**；至 **一百万** 条约 **86%** unique；novelty 约稳定在 **~68%**。（*Nature 刊发页对更大规模饱和曲线有不同数字；本卡不覆盖本地抽取。*）

**相对 CDVAE 等（抽取 Fig. 2e–f）：**
- **MatterGen-MP**（仅 MP-20，与基线同数据）：相对 CDVAE → S.U.N. 比例 **↑1.8×**，平均 RMSD **↓3.1×**。
- 全量 **MatterGen** 相对 MatterGen-MP：再 **↑1.6×** S.U.N.、**↓5.5×** RMSD（数据扩容）。
- 摘要口径：相对先前生成模型，结构 **>2×** 更可能 novel+stable，且 **>15×** 更接近局域能量最低点（arXiv；Nature 摘要写 **>10×**——**以本地 arXiv 抽取为准并双记**）。

### 3.4 条件生成任务切片（文内）

| 任务 | 微调标签规模（抽取） | 目标示例 | 文内对照 |
|---|---|---|---|
| 目标化学体系 | adapter 指向体系 + E_hull=0 | 9×三元 / 9×四元 / 9×五元（well / partial / not explored） | 与 **RSS / substitution** 比；**三者皆配 MatterSim** 做 pre-relax 与稳定性过滤后再 DFT（§2.3）——**接口句，不展开 MatterSim** |
| 空间群对称 | 空间群标签微调 | 14 个随机空间群跨七晶系 | S.U.N. 中属目标空间群的比例（Fig. 4；抽取） |
| 磁密度 | **605,000** DFT 磁密度（铁磁序假设） | 高磁密度（如 **0.15–0.20 Å⁻³** 量级目标，见文内图） | 分布向目标尾部推移 |
| 带隙 | **42,000** DFT 带隙 | **3.0 eV** | 同上 |
| 体模量 | 仅 **5,000** 标签 | 高体模（如 **400 GPa** 量级） | 小标签仍可推向目标 |
| 多属性 | 磁密度 + **HHI**（供应链风险） | 高磁密 + 低 HHI（如文内 **1250** 量级） | 联合目标下 Co/Gd 等近消失（Fig. 6；抽取） |

极端约束预算实验（抽取）：在有限 DFT 物性计算预算下，MatterGen 可找到至多约 **47** 条磁密度 **>0.2 Å⁻³** 的 S.U.N.（相对微调集中仅 **26** 条同类）；体模极端约束下相对 screening 持续发现更多候选（Fig. 5g 等；柱高未全抽出者标「待核实读图」）。

### 3.5 Nature 增补（刊发页；本地无 Nature PDF）

刊发页相对 arXiv 的**可核存在性**（非覆盖本地表数字）：
- 增加 **实验合成验证**：筛选后尝试合成 4 候选，成功 1 例 **TaCr₂O₆**（相对生成有序结构的成分无序变体）；纳米压痕估计体模相对目标口径摘要称测得物性在目标 **20%** 内。
- 基线名单显式含 **DiffCSP**；数据/代码指向 `microsoft/mattergen`。
跟读：**实验细节与合成操作不写**；只立「生成 → 可合成验证」这一任务接口。

### 3.6 自述局限（抽取 §3 Discussion）

- 生成空间群偏 **P1**（对称性不足，大胞尤甚）。
- 评测仍难覆盖真实应用全部判据；实验表征是最终检验。
- 展望：催化表面 / MOF、非标量条件（能带 / XRD）等——**本卡不展开**。

---

## 四、MACE-MP-0：原子材料化学 foundation 力场（谱系基线）

> 角色：为 **2510.25380 跨域统一** 提供「foundation MLIP + multi-head replay」谱系起点；**禁止**把 153 页 / ~80MB 巨本当默认。

### 4.1 主张与训练设定（抽取摘要 / Methods）

- **主张**：在中等规模公开数据（**MPtrj**，CHGNet 同族整理；PBE）上训练通用原子 ML 模型，可对广谱分子 / 材料跑 **稳定 MD**；需要时用**少量**应用特异点微调到近 ab initio。文内称系列为 **MACE-MP-0**，本稿数字默认对应 **MACE-MP-0b3**（另有 0a 等历史版本；GitHub `ACEsuit/mace-mp`）。
- **架构要点（Methods）**：MACE 等变消息传递；**2** 层；**l_max=3**；每层 4-body（correlation order 3）；**128** channel；径向截断 **6 Å**；**10** Bessel；**L=1**「medium」；短程 **ZBL** + 距离变换。
- **微调协议**：引入 **multi-head replay fine-tuning**——微调新数据时在损失中保留 foundation 训练子集，防灾难遗忘（§3 Fine-tuning；Fig. 4）。**此协议被 2510.25380 升格为跨域后训练主轴。**

### 4.2 能力切片（只立存在性，不抄 80 页案例通史）

文内演示覆盖：水系 / 固液界面、催化表面与 NEB（常需少量 DFT 点微调）、**QMOF 外推**、小蛋白动力学等。跟读：本卡**不**把 MP-0 写成「又一篇通用 MLFF 通史」；数字与案例细节以抽取为准，未抽出柱高标「待核实读图」。

---

## 五、MACE 跨域：电子结构理论之间的 cross-learning

> 核心问题：**如何在不一致的电子结构理论标签下，仍学出可开箱用于多化学语境的单一连续势能（主头）？**

### 5.1 相对「任务嵌入 / 元学习」的接口差

文内批评碎片化景观：分子势 / 表面势 / 体材料势割裂。对照路径（抽取 Introduction）：

| 路径 | 代表（文内点名） | 推理时是否需指定任务 |
|---|---|---|
| 任务嵌入输入 | UMA、DPA-3、SevenNet | 通常要 |
| 元学习再特化 | （文内综述） | 通常要 |
| 多头 + 下游特化 | DPA-2、JMP | 常特化某一头 |
| **本文** | multi-head + **replay 后训练**，评测 **主头（PBE/OMAT）** 跨任务 | 目标：**单一连续势**开箱尽量通用 |

### 5.2 架构增强（相对原版 MACE）

网格搜索后写入公式的蓝改（§II.B；抽取）：

1. **跨元素更多权共享** → 更强化学域压缩。
2. **积分解中的非线因子**（非纯多项式特征）→ 大化学多样库上精度更好。
3. 其它实现细节（抽取）：源/目标元素分离嵌入进径向 MLP；**f_cut 移到 MLP 外**使截断更平滑；标量通道 gated 非线性等。

消融轨迹（文内）：`mace-omat-0`（线性块）→ `mace-omat-1`（非线性块，且 L:1→2 等）→ `mace-mh-1-omat`（多头 replay）。

### 5.3 两阶段协议 + 数据头

`
Stage 1 预训练：OMAT（~100M 构型，89 元素，PBE(+U)）→ 共享几何/化学表示
 │
Stage 2 Multi-Head Replay Post-Training
 ├─ OMAT Replay 10%（~10M）→ 保留为 PBE/OMAT 主头
 ├─ MPTraj（~1.5M 轨迹）
 ├─ SPICE-1（~500K 有机分子）
 ├─ RGD1（反应中间体 / TS；B3LYP/6-31G*）
 ├─ OC20 子样（~2M 表面–吸附）
 ├─ OMOL-1%（~1.2M；ωB97M-D3(BJ)/def2-TZVPP 等，文内）
 └─ MATPES R2SCAN（~400K）等
 │
 推理默认强调：mace-mh-1 的 **OMAT 头**（mace-mh-1-omat）
`

多头读出：共享节点特征 → 浅头（首层线性 + 次层单隐层 MLP）映射到各理论层级能量；头特异原子参考能 **E₀**（§II.A）。

### 5.4 跨域榜字段（文内 Fig. 2；抽取）

**全局分**加权（文内自述主观，呼吁社区共议）：Materials **0.25** · Molecules **0.25** · Surfaces **0.20** · Molecular Crystals **0.20** · Physicality **0.10**。

抽取可见的总体排序片段（越高越好）：

| 模型（文内记号） | Global score（抽取 Fig. 2b） |
|---|---|
| **MACE-MH-1-OMAT** | **0.862**（文内 top） |
| MACE-OMAT-1 | 0.786 |
| ORB-v3 | 0.739 |
| MatterSim-5M | 0.725 |
| UMA-S-1.1-OMAT | 0.671 |
| MACE-OMAT-0 | 0.636 |
| UMA-M-1.1-OMAT | 0.632 |

文内叙事：MH 模型在 Molecules / Molecular Crystals 上明显增益，Materials 保持竞争；相对 UMA 的「理论层级全局嵌入」，作者认为**更少灵活性的多头 + 共享表示**反而更利于向主头迁移知识（§XIV）。速度表（Table XV，H100，1000-atom diamond，含 cuEquivariance / compile）：`mace-mh-1` / `mace-omat-1` **43** steps/s；`mace-mp-0a` / `mace-omat-0` **83** steps/s（更大 L=2 / 512 channel 代价，非架构改动本身）。

**与 [[MatterSim材料基础模型]] 接口**：此处 `mattersim-5M` 仅为跨域总分对照——**禁止**回写 MatterSim 温压主动学习正文。

### 5.5 代码与利益声明（抽取）

- 代码 / 权重入口：`ACEsuit/mace`、`ACEsuit/mace-foundations`；基准复现指向 ML-PEG。
- Conflict：Csányi 等商业力场 / Ångström AI 权益；Norwood 与 Mirror Physics 关联——跟读时知会即可。

---

## 六、双轴合成：生成器 × 统一势

| 问题 | MatterGen | MACE-MP-0 / 跨域 MH |
|---|---|---|
| 输入 | 噪声 / 条件 c | 原子坐标 + 元素（+ 头） |
| 输出 | 候选晶体结构 | 能量 / 力（连续势） |
| 典型闭环 | 生成 →（可选 MLFF 预弛豫，文内用 MatterSim）→ DFT 验稳 / 验性 | 开箱 MD / 微调 → 动力学与物性 |
| 相对 [[MatterSim材料基础模型]] | **正交**：设计侧生成 | **同族升级**：从「材料 MD foundation」到「跨域单一势」；[[MatterSim材料基础模型]] 仍是宽温压预测另一条自洽线 |

跟读口令：**[[MatterSim材料基础模型]] 回答「这结构在温压下物性如何」；[[MatterGen与MACE]] 回答「给我满足约束的新结构」+「一个势能否从分子打到表面再到晶体」。**

---

## 七、跟读清单 / 待核实

1. MatterGen：**本地以 arXiv v2 抽取为准**；若需 Nature 表数字 / Extended Data，另抽 Nature PDF（本仓未落）。注意摘要 **15×（arXiv）vs 10×（Nature）**。
2. MatterGen 化学体系实验中 **MatterSim 仅过滤接口**——细节回链 [[MatterSim材料基础模型]]。
3. MACE-MP-0 巨本案例图大量「待核实读图」；跨域文 Table 细分 MAE 未尽录——需要时按 定点补。
4. 二进制纪律：确认  **无** `2312.03687*` / `2401.00096*`；**有** `2510.25380-mace-cross.pdf`。

---

## 八、来源速查

| 文档 | 用途 |
|---|---|
| | MatterGen 方法 / S.U.N. / 条件任务主数字 |
| https://www.nature.com/articles/s41586-025-08628-5 | Nature 刊发线、实验验证存在性、Code/Data availability |
| `https://arxiv.org/abs/2510.25380` + 同名 `.txt` | 跨域架构、数据头、全局分 |
| | MP-0 foundation 设定与 replay 协议源头 |
| [[MatterSim材料基础模型]] | 预测势主轴；本卡禁重写 |
