---
title: "Diffusion Forcing 族：DF → Self Forcing（Causal Forcing 附录）"
topic: DiffusionForcing族
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 # slim: url+extract — Diffusion Forcing PDF removed (>15MB)
 - https://arxiv.org/abs/2407.01392
 - https://arxiv.org/abs/2506.08009
 - https://arxiv.org/abs/2602.02214
arxiv: ["2407.01392", "2506.08009", "2602.02214"]
related: ["扩散语言模型", "视频生成正式报告", "扩散生成式视觉与LLM", "世界模型与VJEPA"]
project_df: "https://boyuan.space/diffusion-forcing"
project_sf: "https://self-forcing.github.io/"
project_cf: "https://thu-ml.github.io/CausalForcing.github.io/"
github_cf: "https://github.com/thu-ml/Causal-Forcing"
archived: 2026-09-22
---

# Diffusion Forcing 族：DF → Self Forcing（Causal Forcing 附录）

> **定位**：Forcing 族谱——立 **序列生成里「噪声当软掩码 / 因果去噪」** 的一条族谱：**Diffusion Forcing（DF，NeurIPS 2024）** 把每 token 独立噪声级与因果 next-token 预测合成；**Self Forcing（SF，NeurIPS 2025）** 把 AR 视频扩散的训练对齐到推理期 **自 rollout + 视频级分布匹配**；附录 **Causal Forcing（CF，ICML 2026）** 指出 SF 式「双向教师 → AR 学生」的 ODE 初始化破坏 **帧级 injectivity**，改用 **AR 教师做因果 ODE 初始化再接 DMD**。
> **攻坚线**：**架构思想（主）**——Teacher / Diffusion / Self / Causal Forcing 各自训什么条件分布、训练–推理是否同分布；**评测字段（辅）**——迷宫规划奖励、VBench / VisionReward / 吞吐–时延。
> **硬划界**：
> - **≠ [[扩散语言模型]] 文本扩散**：不写 LLaDA / Dream 的 **离散 [MASK] MDM**；本卡是 **连续序列（视频 / 轨迹 / 时序）上的高斯噪声级**。
> - **≠ [[视频生成正式报告]] Sora 备忘**：不写旗舰正式报告缺口 / System Card；本卡只跟学术 **AR–扩散杂交 forcing 族**。
> - **≠ B10 图像 LDM 通史**：不重写 LDM→DiT 图像潜扩散史；只用「去噪 / 引导 / DiT 骨干」作接口。
> - **≠ [[世界模型与VJEPA]] V-JEPA**：世界模型是 **表征空间非生成预测**；本卡是 **像素/潜视频与轨迹的生成式 forcing**。
> - **禁止编造**：主张、表数字、步数、FPS/时延一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / 元数据 | 角色 |
|---|---|---|---|
| **主文 A** | Chen, Martí Monsó, Du, Simchowitz, Tedrake & Sitzmann（MIT CSAIL / TUM）, *Diffusion Forcing: Next-token Prediction Meets Full-Sequence Diffusion* | arXiv:**2407.01392v4** \[cs.LG\] **10 Dec 2024**；NeurIPS 2024；[abs](https://arxiv.org/abs/2407.01392) · [pdf](https://arxiv.org/pdf/2407.01392)；（**35** 页 letter） | **族原点**：独立 per-token 噪声；因果 CDF；ELBO；视频/规划/时序/机器人 |
| **主文 B** | Huang, Li, He, Zhou & Shechtman（Adobe Research / UT Austin）, *Self Forcing: Bridging the Train-Test Gap in Autoregressive Video Diffusion* | arXiv:**2506.08009v2** \[cs.CV\] **10 Nov 2025**；NeurIPS 2025；`https://arxiv.org/abs/2506.08009`（**19** 页；3,902,279 bytes） | **暴露偏差主修**：训练期自 rollout + KV cache；DMD/SiD/GAN 视频级损失；rolling KV |
| **附录 / 续篇** | Zhu*, Zhao*, He, Su, Li & Zhu（清华 / 生数 / UT Austin / 人大等）, *Causal Forcing: Autoregressive Diffusion Distillation Done Right…* | arXiv:**2602.02214v5** \[cs.CV\] **1 Jun 2026**；ICML 2026（PMLR 306）；`https://arxiv.org/abs/2602.02214`（**20** 页；9,482,524 bytes） | **蒸馏理论附录**：帧级 injectivity；AR 教师因果 ODE → 同 SF 的 DMD |

**项目页 / 代码（文内明示）：**
- DF：https://boyuan.space/diffusion-forcing
- SF：https://self-forcing.github.io/
- CF：https://thu-ml.github.io/CausalForcing.github.io/ ；代码 https://github.com/thu-ml/Causal-Forcing

**一句话抓手：**
- **DF**：噪声级 = 软掩码；训练「任意噪声日程组合」，采样可 zig-zag / 引导 / 超视界稳定 rollout。
- **SF**：别再只在 GT（或独立噪声）上下文上训——**训练时就按推理做自回归 rollout**，用 **整段视频的分布匹配** 教模型扛自己的误差。
- **CF**：SF 的 ODE 初始化若从 **双向教师** 回归 AR 学生，破坏 **帧级单射**；应先训 **TF-AR 教师**，再做 **因果 ODE**，最后才 DMD。

---

## 二、议题边界与族谱口诀

### 2.1 相对已入库只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[扩散语言模型]] 文本 MDM** | 「扩散」一词与掩码直觉的对照 | LLaDA/Dream、离散词表吸收态、MMLU 表 |
| **[[视频生成正式报告]] 视频旗舰备忘** | 「视频生成存在正式报告 / 产品线缺口」的存在性 | Sora 2 System Card、零样本推理黑盒评测通史 |
| **B10 图像 LDM/DiT** | 潜空间去噪、classifier / score 引导、DiT 作骨干 | LDM 层图、DiT 算力–质量缩放全书 |
| **[[世界模型与VJEPA]] V-JEPA** | 「世界模型 / 交互仿真」叙事可与 AR 视频相遇 | JEPA 表征预测、IntPhys、非生成式动力学 |

### 2.2 跟读口诀（四范式对照）

`
Teacher Forcing (TF) ：去噪当前帧 | 条件 = 干净 GT 前缀（训≠推：推时前缀是模型自己的）
Diffusion Forcing (DF) ：去噪当前帧 | 条件 = 各帧独立噪声的前缀（覆盖「干净前缀+噪当前」切片，但仍非完整自生成分布）
Self Forcing (SF) ：训练期自 rollout（KV）| 损失 = 整视频分布匹配（DMD/SiD/GAN）
Causal Forcing (CF) ：蒸馏管道修 ODE 初始化 | AR 教师保证帧级 injectivity，再接 SF 同款 DMD
`

SF 文 Fig.1 原话级压缩：TF/DF 训练产出 **不属于** 推理时模型生成分布；SF 用自生成上下文 + 视频级匹配 **闭合 train–test 间隙**。

---

## 三、站 1：Diffusion Forcing（架构原点 · 主）

### 3.1 问题：Teacher Forcing vs Full-Sequence Diffusion

文 §1 两条路的短板（跟读）：

| | Next-token + Teacher Forcing | Full-sequence Diffusion |
|---|---|---|
| 强项 | 可变长、条件任意历史、可树搜索 / 在线控制 | 整段联合建模、**diffusion guidance**、连续信号（视频）质量 |
| 短板 | **难引导**整段目标；连续数据超训练视界易 **发散** | 非因果、定长；引导/子序列能力受限 |
| 天真杂交失败 | 因果网上做「全序列同噪声级扩散」→ 忽略「早期小不确定 ⇒ 后期必须大不确定」 | — |

**DF 核心观察：** 加噪 ≈ **部分掩码**（零噪声=未掩、满噪声=全掩）→ 强制模型学会对 **任意噪声级组合** 的 token 集合做「去掩」。

### 3.2 训练与采样（Algorithm 1–2；§3.2）

- **训练**：对轨迹 $x_{1:T}$，为每个 $t$ **独立**采样噪声级 $k_t$；因果网络（RNN / causal Transformer 等）在共享参数下同时去噪各 token。
- **实例化 Causal Diffusion Forcing（CDF）**：未来依赖过去；可一次生成「下一 token 或下几个」。
- **采样**：由噪声日程矩阵 $K$（行=去噪步、列=时间）规定每步每 token 的目标噪声级；从全白噪声起，按行从左到右去噪。同一模型 **不重训** 即可切换：稳定 AR rollout、zig-zag「近确定/远不确定」、长程引导等。

**Theorem 3.1（Informal，文 §3）：** DF 训练过程优化对 $\ln p_\theta((x_t^{k_t})_{1\le t\le T})$ 的 **ELBO 重加权**，期望对 $k_{1:T}$ 与前向加噪；从而 **同时** 对训练所见全部噪声级序列给似然下界。形式证明见 Appendix A（Theorem A.1）。

### 3.3 新能力（§3.3–3.4）

1. **稳定超视界 AR**：用上一潜变量带 **小噪声** $0<k\ll K$ 更新，连续视频可滚出训练长度之外（§4.1：Minecraft / DMLab；文称可达约 **1000** 帧仍稳，而 TF 与因果全序列基线很快发散）。
2. **因果不确定性 / zig-zag**：先充分去噪近未来、保持远未来高噪声。
3. **长程引导 + Monte Carlo Guidance（MCG）**：未来 token 的奖励梯度可回传到过去；对未来多样本平均梯度 ≈ shooting / MPPI 精神。
4. **决策框架**：同一模型可当 **短视界策略** 或 **长视界规划器**（改 lookahead $H$，不重训）。

### 3.4 评测字段（辅）

**迷宫规划（D4RL Maze2D；Table 1，归一化回报，越高越好，节选）：**

| 环境 | Diffuser* | Ours w/o MCG | **Ours** |
|---|---|---|---|
| Maze2D Medium | 121.5±2.7 | 136.1±10.2 | **149.4±7.5** |
| Maze2D Large | 123.0±6.4 | 142.8±5.6 | **159.0±2.7** |
| Single-task 平均 | 119.5 | 129.67 | **141.7** |
| Multi-task 平均 | 129.4 | 127.7 | **146.2** |

\* Diffuser 需手工 PD、忽略生成动作才可跑；「Diffuser w/ diffused action」在 Medium/Large 上崩溃到约 6–13。

**真实机器人（Franka；§4）：** 交换苹果/橙子槽位；DF **80%** 成功率；遮挡关键状态后 **76%**（仅降 4%）；next-frame 扩散基线显著更差（文称对比，细节见原文）。

**时序预测（Table 2，CRPSsum↓）：** 与 TimeGrad / ScoreGrad 等并列量级；文自陈时序非核心应用，仅证目标可迁移。

---

## 四、站 2：Self Forcing（暴露偏差 · 主）

### 4.1 问题设定：AR 视频扩散 + exposure bias

**AR 视频扩散（§3.1）：**
$$
p(x_{1:N})=\prod_{i=1}^{N} p(x_i\mid x_{<i}),\quad
\text{每个条件用扩散过程建模}
$$
实践上可一次一块（chunk），记号仍称「帧」。骨干：因果注意力 DiT + 文本条件 + **因果 3D VAE** 潜空间（文）；初始化自 **Wan2.1-T2V-1.3B**（Flow Matching）。

**TF vs DF（视频语境，Fig.1–2）：**
- TF：当前帧去噪条件 = **干净 GT** 前缀（块稀疏因果 mask，可并行整段）。
- DF：条件 = **各帧独立噪声** 的前缀。
两者都能在训练分布里「碰到」推理切片「干净前缀 + 噪当前」，但 **整段轨迹仍非自生成分布** → 推理误差累积（exposure bias）。CausVid 用 DF+DMD，但训练生成分布 ≠ 推理分布，DMD **匹配错对象**（§2 对 CausVid 的批评）。

### 4.2 Self Forcing 算法（§3.2–3.3；Algorithm 1）

1. **训练期自回归 rollout**：每帧迭代去噪，条件是 **自己已生成的干净前缀 + 当前噪帧**；**训练也用 KV cache**（Fig.2c），无需特殊 attention mask。
2. **少步扩散骨干**：避免多步链反传爆炸。
3. **随机梯度截断**：每序列随机采样去噪步 $s\sim U\{1..T\}$，只对第 $s$ 步开梯度；KV 嵌入对过去帧 **detach**。
4. **整体分布匹配**（噪声后匹配 $p_{\theta,t}$ 与 $p_{\mathrm{data},t}$）：
 - **DMD**（反向 KL，主结果默认）
 - **SiD**（Fisher）
 - **GAN**（JS，relativistic + R1/R2）
5. **Rolling KV（§3.4；Algorithm 2）**：固定最近 $L$ 帧 KV，复杂度 $O(TL)$；训练时限制末块看不见第一块图像 latent，避免外推闪烁。

跟读：**目标首先是修暴露偏差，不是「仅为加速的蒸馏」**——因此只减步数、不对齐生成分布的一致性蒸馏类方法，文称不适用本框架。

### 4.3 评测字段（辅；单卡 H100）

**Table 1（VBench↑；Throughput FPS↑；Latency s↓；节选）：**

| 模型 | #Params | FPS | Latency | Total | Quality | Semantic |
|---|---|---|---|---|---|---|
| Wan2.1（双向，初始化源） | 1.3B | 0.78 | 103 | 84.26 | 85.30 | 80.09 |
| CausVid*（同基座） | 1.3B | 17.0 | 0.69 | 81.20 | 84.05 | 69.80 |
| **SF chunk-wise** | 1.3B | **17.0** | **0.69** | **84.31** | 85.07 | **81.28** |
| **SF frame-wise** | 1.3B | 8.9 | **0.45** | 84.26 | **85.25** | 80.30 |

文称 intro：**17 FPS**、亚秒时延；用户偏好上 SF 优于 CausVid / Wan2.1 / SkyReels-V2 / MAGI-1（Fig.4）。相对 Wan2.1 时延约 **150×** 量级加速（文 §4 表述）。

**Table 2 消融（chunk-wise Total）：** DF 82.95；TF 83.58；DF+DMD 82.76；TF+DMD 82.32；**SF-DMD 84.31**；SF-SiD 84.07；SF-GAN 83.88。Frame-wise 下 TF/DF 系掉分更重，SF 仍稳住（暴露偏差论点的主证据）。

**训练成本（文）：** DMD 设定下约 **1.5 小时 / 64×H100** 收敛。

---

## 五、附录站：Causal Forcing（蒸馏理论补丁）

> **阅读角色**：本卡将 CF 标为 **附录 / 续篇**——承接 SF 的「ODE 初始化 + DMD」管道，专攻 **架构鸿沟（双向 → 因果）** 的理论条件，而非另起一条视频通史。

### 5.1 诊断：两阶段里真正该修的是 ODE，不是 DMD

典型管道（CausVid / Self Forcing）：**双向预训练教师** → ODE 蒸馏初始化 AR 少步学生 → **asymmetric DMD**。

文主张（§3.1–3.2，Fig.2）：把 AR 学生初始化成「已消除步数鸿沟的少步双向 DMD 学生」后，**仅剩架构鸿沟**，表现仍远差标准双向 DMD → **DMD 阶段无法单独补架构鸿沟**，必须在 ODE 初始化修好。

### 5.2 关键原理：帧级 injectivity（Definition 3.1）

- 双向→双向 ODE：视频级 PF-ODE 天然单射。
- AR 学生：需要 **帧级**——固定噪帧 $x_t^i$ 时，AR 教师 PF-ODE 映到 **唯一** 干净帧 $x_0^i$。
- **Self Forcing 式**「双向教师轨迹 + AR 学生回归」（文 Eq.3 / Fig.3c）：同一噪帧可对应多个干净帧（双向去噪看未来）→ **非单射** → 回归学的是条件期望式模糊解（Proposition 3.3 路线；证明见 Appendix B）。

另：**AR 上的 Diffusion Forcing** 相对推理「干净前缀」存在分布错配（Proposition 3.4）；文实证 **Teacher Forcing 训 AR 教师优于 DF**（Table 2：TF VisionReward 3.343 vs DF 1.583 等）。

### 5.3 Causal Forcing 三阶段（§3.3）

1. **TF 训多步 AR 扩散教师**（文：2K steps；3K 条由双向基座合成的 $D_{\mathrm{Bi}}$）。
2. **因果 ODE 蒸馏**：从 AR 教师采 PF-ODE 轨迹 $D_{\mathrm{Causal}}$（3K），学生回归 $G_\theta(x_t^i, x_{gt}^{<i}, t)\to x_0^i$（1K steps）——满足帧级 injectivity。
3. **Asymmetric DMD**：与 Self Forcing **同一程序**（VidProM；750 steps 至收敛）；chunk=3 latent frames；基座 **Wan2.1-T2V-1.3B**，832×480，81 帧设定跟随 SF。

可扩展：**Causal CD**（AR 教师 + TF 式 consistency）优于 asymmetric CD（Table 2）。

### 5.4 评测字段（辅；与 SF 同口径效率）

**Table 1（节选；Dynamic / Vision / Instruct 已×100；Rating↓ 越好）：**

| 模型 | FPS | Latency | Total | Dynamic | Vision | Instruct | Rating↓ |
|---|---|---|---|---|---|---|---|
| Wan2.1-1.3B | 0.78 | 103 | 83.37 | 61 | 5.275 | 42 | 2.29 |
| CausVid | 17.0 | 0.69 | 81.33 | 62 | 5.741 | 12 | 4.27 |
| Self Forcing | 17.0 | 0.69 | 83.74 | 57 | 5.820 | 48 | 2.87 |
| **Causal Forcing** | **17.0** | **0.69** | **84.04** | **68** | **6.326** | **56** | **1.64** |

相对 SF 的文内相对增益（Abstract / §4）：Dynamic Degree **+19.3%**，VisionReward **+8.7%**，Instruction Following **+16.7%**（同训练预算叙述：双方 ODE 初始化均 ≥3K steps 量级后再 DMD）。

**Table 2 关键消融（chunk-wise）：** Self Forcing’s ODE + DMD：Total 82.00 / Dy 24 / Vis 3.330 / Inst 38；**Causal ODE + DMD**：Total **84.04** / Dy **68** / Vis **6.326** / Inst **56**。

**长视频外推：** 文 §5 承认与 SF 一样默认约 **5s** 注意力训练，硬外推有训–推间隙；指向 LongLive / Rolling Forcing / Infinity-RoPE / Deep Forcing 等 **正交** 适配（本卡不展开）。

---

## 六、三文对照总表（跟读用）

| 轴 | Diffusion Forcing (2024) | Self Forcing (2025) | Causal Forcing (2026) |
|---|---|---|---|
| 主问题 | NTP 灵活 ↔ 全序列扩散可引导 | AR 视频 **exposure bias** | AR 蒸馏的 **架构鸿沟 / injectivity** |
| 噪声/条件 | 训练：独立 $k_t$；推理：任意日程 $K$ | 训练=推理自 rollout（干净自前缀） | ODE 阶段：AR 教师因果条件；DMD 同 SF |
| 损失形态 | 去噪 MSE → 子序列 ELBO | 视频级 DMD/SiD/GAN | 因果 ODE 回归 + DMD |
| 典型骨干 | 因果 RNN / 序列网；规划用潜状态 | Wan2.1-1.3B 因果化 + KV | 同左；先 TF-AR 教师 |
| 速度叙事 | 规划/视频稳定性为主 | **17 FPS / ~0.69s**（chunk）H100 | **同 SF 时延**，质量指标抬升 |
| 本卡角色 | **族原点** | **主深读②** | **附录理论补丁** |

---

## 七、开放问题（文内自陈，不外推）

1. **DF**：连续高维超长 rollout 的稳定性机理与噪声日程设计空间仍大；时序任务非主战场。
2. **SF**：自 rollout 训练效率依赖少步 + 截断；rolling KV 对「首帧 latent」分布需特训；与双向多步模型的语义分项仍有消长。
3. **CF**：Causal CD 仍是「vanilla LCM」级实例，文称弱于 score distillation，留待更强 CD；长视频需正交适配；与 APT2 等 **GAN 系 AR 蒸馏** 的边界文 §5 有讨论但不替代本卡主线。

---

## 八、本地路径速查

| 类型 | 路径 |
|---|---|
| 笔记 | 多模态与具身/世界模型/DiffusionForcing族.md |
| PDF / URL | DF → https://arxiv.org/abs/2407.01392 · `https://arxiv.org/abs/2506.08009` · `https://arxiv.org/abs/2602.02214` |
| 抽取 | `*.txt`（及 ） |

**抽取命令备忘：** ` <pdf> <txt>`（2026-09-22 CST）。

## 相关笔记

- [[DiffusionForcing族|Diffusion Forcing]]
- [[WorfBench工作流基准|WorfBench]]
- [[合成对齐数据Magpie|Magpie / ActiveUltraFeedback]]
- [[EntMTP熵引导投机解码|EntMTP]]
- [[DuoAttention与KVzip|DuoAttention / KVZip]]

