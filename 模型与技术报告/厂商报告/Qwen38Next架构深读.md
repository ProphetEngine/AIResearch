---
title: "Qwen3.8-Next / Flash-Next 架构 TR 深读"
topic: Qwen38Next架构深读
date: 2026-09-22
lines: [架构思想, 数学原理, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2608.30320
cross_ref:
 - 模型与技术报告/厂商报告/Qwen3技术报告深读.md # Qwen3 全家桶 / think·蒸馏；本卡不重写
 - 训练/持续与技巧/优化器与训练稳定性.md # Muon 通史；本卡只写 Flash-Next 工程差分
 - 架构/注意力与长上下文/注意力效率族MQA到MLA.md # 注意力效率通史；本卡专 QSA/GDN 增量
archived: 2026-09-22
---

# 3　Qwen3.8-Next / Flash-Next 架构 TR 深读

> **定位**：相对已入库 [[Qwen3技术报告深读]] 的**架构世代增量**深读卡。数字一律取自官方 PDF `https://arxiv.org/abs/2608.30320`（2026-09-22；28 页）。
> **攻坚线**：**架构思想（主）** + **数学原理（线性注意力 / 稀疏索引，辅）** + **AI Infra（FlashQLA / Muon / 稳定性，辅）**。
> **刻意不写**：Qwen3 的 Dense/MoE 全家桶表、think/no_think、thinking budget、Strong-to-Weak Distillation、四阶段后训练（见 [[Qwen3技术报告深读]]）；Adam→AdamW→Muon 通史（见 B4）。
> **禁止编造**：本 PDF **未给出** Flash-Next 总层数 / hidden / 专家数 / 预训练总 token 精确账本 → 不得从博文或二级综述外推。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability | 封面； Title |
| 作者 | Qwen Team；Core Contributors: Zihan Qiu 等； Author 长名单含 Dayiheng Liu 等 | 封面 / §6 |
| arXiv 页眉 | **arXiv:2608.30320v1** \[cs.CL\] **31 Aug 2026** | PDF 第 1 页页眉 |
| PDF 页数 | **28**（A4） | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:4af3385) | |
| 本地路径 | `https://arxiv.org/abs/2608.30320` | 本仓库（2026-09-22 自 arXiv 下载） |
| 镜像 | GitHub `QwenLM/Qwen3.8-Flash-Next` · `tech_report.pdf` | 议程入口 |
| 产品名（正文） | **Qwen3.8-Flash-Next**（稀疏 MoE base）；评测表写作 **Qwen3.8-Flash-Next-Base** | Abstract / §4 / Tab. 11 |
| 摘要四支柱 | (1) **GDN + 全局注意力**混合；(2) CPT 期换 **QSA**；(3) **Gated Residual (GR)**；(4) 主机侧 **n-gram embedding** + **Muon** | Abstract |

**摘要级一句话（不外推）：**
Flash-Next 把「损失 / 下游榜 / 训推成本 / 训练稳定性」当成**同一设计问题**：用 GDN 混合 + CPT 期 QSA 控长文注意力，用四分支 GR 加残差容量并稳住训练，用离卡 n-gram 表扩参，用 Muon + 重拟合缩放律抬高最优 LR/batch，在约 **1/3 激活参、1/3 tokens、约 1/9 训练 FLOPs** 下逼近前代 **397B-A17B** 旗舰质量。

---

## 二、相对 Qwen3 TR / 文中前代的增量对照

> 左列锚已入库 Qwen3 TR（arXiv:2505.09388）；中间列为**本 PDF 明文**对照的近期 Qwen 基线（3.5 结构 / 3.7-Plus）；右列为本报告。勿把 Qwen3 的 think 协议或 36T 预训练账本写进本卡。

| 维度 | Qwen3 TR（已入库，勿重写） | 本 PDF 中的前代锚点 | **Qwen3.8-Flash-Next（本 PDF）** |
|---|---|---|---|
| 报告入口 | 2505.09388 · 2025-05 | Qwen3.5 结构消融；**Qwen3.7-Plus-Base = 397B / 17B 激活**（Tab. 11） | **2608.30320v1** · 2026-08-31 · 28 页 |
| 总参 / 激活 | Dense 0.6–32B；MoE 30B-A3B / 235B-A22B | 397B-A17B（Plus）；消融常用 25B-A3B / 156B-A7B 等 | **125B** 总参 · **6B** 激活/token · 另 **51B** n-gram 表（离加速器） |
| 注意力 | GQA + RoPE + QK-Norm | Qwen3.5：**全注意力 / SWA hybrid / GDN hybrid** 对照（Tab. 1） | 层内 **3×GDN + 1×全注意力**；CPT（256K）把全注意力换为 **QSA** |
| 残差 | 标准 pre-norm residual | Qwen3.5 pre-norm；与 mHC / AttnRes 对照 | **Gated Residual**：$n_r=4$ 分支 + 逐元素 sigmoid 读门；**去掉 $H_{res}$** |
| 容量扩展 | MoE 专家为主 | MoE；本 PDF 另开 n-gram 轴 | **单层 n-gram embedding（Layer 2）**，host prefetch |
| 优化器 | （Qwen3 TR 未主推 Muon） | Qwen3.5 + AdamW 作应力基线 | **Muon**（2D 线性映射）+ **AdamW**（embedding/head/router/GR 低秩等） |
| 稳定性手段 | QK-Norm 等 | 应力下 AdamW 易尖刺 | GR 门控 + Muon；全量训「无 loss spike / 无异常 grad norm」；**未依赖** qk-clip / SwiGLU-clip |
| 后训练叙事 | think/no_think、GRPO、蒸馏 | 本报告主线 **架构 + 预训练稳定性**；仅提及 NoPE 在后训练更易 endless generation | **不展开** think 协议 / RL 配方（本 PDF 无） |

**增量一句话：**
相对 Qwen3「Dense+MoE + 统一 thinking」，本卡公开增量几乎全部落在 **token mixing（GDN/QSA）**、**残差加宽门控（GR）**、**离卡 n-gram** 与 **Muon/缩放律/应力稳定性**；MoE 专家表与后训练协议**本报告未重开**。

---

## 三、架构总览（Figure 1）

`
Input → Vocab Emb → [Layer2: N-gram Emb] → 重复块:
 3× (GR-read → GDN → GR-write → MoE)
 1× (GR-read → QSA → GR-write → MoE) # CPT 前该槽位为 full attention
→ MTP Modules（复用 QSA top-k 索引）→ Prediction Head
`

| 组件 | 报告要点 | 出处 |
|---|---|---|
| 混合比 | **每 4 层 1 个**全注意力（后换 QSA），其余 **GDN** | §2.1.1 / Fig. 1 |
| GR | 每个 attention 子层与每个 MLP 子层各一套 GR；$n_r=4$ | §2.2 |
| N-gram | **仅 Layer 2**；表在主机内存，prefetch 与第 1 层计算重叠 | §2.3.1 / Fig. 1 |
| MTP | backbone 与 MTP 的全注意力均换 QSA；多步投机解码 **复用 top-k 索引** | §2.1.2 / Tab. 4 |
| FlashQLA | TileLang 融合线性注意力核；相对 FLA Triton：**前向 2–3×、反向约 2×**（NVIDIA GPU 多设置） | §2.1.1；仓库 https://github.com/QwenLM/FlashQLA |

---

## 四、重点 1：Gated DeltaNet（GDN）混合（§2.1.1）

### 4.1 动机与混合日程

- 全注意力：内容寻址强，但 **$O(n^2)$** 混合 + KV cache 线性胀。
- SWA：局部窗便宜，窗外信息只能靠深度间接传播。
- **GDN**：把前缀压进**固定尺寸**循环状态，按当前内容更新；交错的全局注意力保留「有限状态记忆难以精确复现」的 token 级检索。
- 日程：**每 4 层放 1 层全注意力（RoPE）+ 3 层 GDN**。消融中 NoPE 在预训练几乎无差，但**后训练 endless generation 显著更高** → 保留 RoPE。

### 4.2 门控 Delta 递推（式 (1)–(5)）

每头状态 $S_t \in \mathbb{R}^{d_k \times d_v}$（实现约定：为原文转置约定）：

$$
\begin{aligned}
\tilde S_{t-1} &= \alpha_t S_{t-1}, \\
\tilde e_t &= v_t - \tilde S_{t-1}^\top k_t, \\
S_t &= \tilde S_{t-1} + \beta_t k_t \tilde e_t^\top, \\
y_t &= S_t^\top q_t,
\end{aligned}
$$

等价形式：$S_t = \alpha_t\bigl(I - \beta_t k_t k_t^\top\bigr)S_{t-1} + \beta_t k_t v_t^\top$。

| 门 | 作用 |
|---|---|
| $\alpha_t \in (0,1)$ | 数据依赖 **衰减**：控制已有状态寿命 |
| $\beta_t \in (0,1)$ | **写入强度**：先估计 $k_t$ 已关联的值，只写残差误差 → 避免纯加性线性注意力的无界外积堆积 |

参数化（式 (6)–(11)）：$q/k/v$ 经短因果 depthwise conv + SiLU；$q/k$ 再 **L2Norm**；$\beta_t=\sigma(W_\beta x_t)$；$\alpha_t=\exp[-\exp(A)\,\mathrm{softplus}(W_\alpha x_t+b_\alpha)]$；输出用 **sigmoid** 门控 × **zero-centered RMSNorm**（相对原 GDN 的 SiLU 输出门，作者称更稳更好）；RMSNorm 零中心化沿用 Qwen3-Next 做法。

### 4.3 架构消融（Tab. 1）

设置：28 层 **25B-A3B** MoE（Qwen3.5 结构），400B@4K + 80B@32K；SWA 窗 **128**。

| Architecture | Avg.（9 榜算术均） |
|---|---:|
| Full attention | 49.87 |
| SWA hybrid | 51.15 |
| **GDN hybrid** | **53.81** |

GDN hybrid 在 9 榜中 **8** 项优于 Transformer、**7** 项优于 SWA hybrid。

---

## 五、重点 2：Qwen Sparse Attention（QSA）（§2.1.2）

### 5.1 与 DSA 的差分动机

- 参照 DSA（Liu et al., 2025a）的轻量 indexer + top-$k$，但 indexer 仍 **$O(n^2)$**，长序列不可忽视。
- QSA：**微块（micro-block）粒度**压缩 key，再选 top 块 → indexer 复杂度 **$O(n^2/r)$**。
- 相对跨层 IndexShare：混合架构层间相似度低，**层内压缩**更合适（Fig. 5a）。

### 5.2 压缩轻量 Indexer

- 结构：**MQA**，$H$ 个 query 头 + **1** 个共享 key 头（Flash-Next 落地：**4** query 头）。
- Key 按非重叠块大小 $r$ **AvgPool** → 块级 key；**先压缩再 Partial RoPE**（每头 128 维中对 **64** 维做旋转，与 core attention 对齐），避免不同旋转相位 token 被平均。
- 块因果打分：完整观察到的块上，对各 indexer head 做 $\mathrm{ReLU}(\langle q,k\rangle)$ 求和（式 (15)）。
- Token 预算 $K$ → 块预算 $K_B=\lceil K/r\rceil$；选中块展开为 token，并**始终并入**末尾未满块。

**Flash-Next 配置：** $K=2048$，$r=4$ → 至多 **512** 完整块 + tail tokens。

### 5.3 CPT 两阶段引入（256K）

| 阶段 | 训什么 | LR | Steps / 形态 | Token 量级 |
|---|---|---|---|---|
| **Dense Distillation** | **仅 indexer**；teacher = 各头 softmax 注意力求和再 L1 归一；**MaxPool** 对齐到块后 KL（式 (17)–(18)） | $1\times10^{-3}$ | 1000 steps；8×256K/step | ≈ **2B** |
| **Sparse Training** | 全骨干 + indexer；KL 仅在 top-$K_B$ 块上重归一后计算（式 (20)） | $2.5\times10^{-5}$ | 8000 steps；96×256K/step | ≈ **200B** |

Fig. 4：Stage 2 与全注意力 LM loss 差约 **$10^{-4}$** 量级。

### 5.4 效果与核级效率（Tab. 2–4，Fig. 6）

| 指标 | Full Attn | w/ QSA |
|---|---:|---:|
| 短文 8 榜 Avg. | 75.9 | **76.8**（7/8 持平或更好） |
| RULER 512K–1M | 90.08 | **93.00** |
| MRCR @512K / @1M | 30.66 / 20.71 | **40.53 / 26.44** |
| MTP 四步投机 mean accept（5 任务 Avg.） | 4.06 | 4.07（索引复用无显著伤害） |
| Attention 模块 @1M（相对 paged GQA） | — | Prefill **7.6×** · Decode **4.9×**（含 indexer + sparse core） |

---

## 六、重点 3：Gated Residual（GR）（§2.2）

### 6.1 设计路径（消融逻辑）

1. **加宽残差**（简化 AltUp）：$n_r$ 分支加权读 + round-robin 写 → 几乎无算力，25B-A3B@400B 上 loss ↓约 **0.01**。
2. **HC / mHC** 三算子：$H_{mix}$ 读、$H_{combine}$ 写、$H_{res}$ 分支混合；可静态或由残差预测。
3. 消融结论（Tab. 5，25B-A3B@560B，$n_r=4$）：
 - sigmoid 门优于 tanh；
 - 数据依赖读/写：loss 再降仅 **0.002**，但榜均再升约 **1.98** 点（相对 static 相对 baseline 的 1.58）——**loss 与下游可分离**；
 - **读粒度**（逐分支×通道）比写粒度重要；写保持每分支标量；
 - $H_{res}$ 在读/写够表达后**几乎无增益** → **删掉**（少一次整段残差读，推理省带宽）。

| Residual | Loss | Avg. |
|---|---:|---:|
| Pre-norm | 1.617 | 50.91 |
| mHC (static) | 1.596 | 52.49 |
| mHC (dynamic) | 1.594 | 54.47 |
| **GR** | **1.590** | **54.66** |

### 6.2 GR 公式要点（式 (29)–(34)）

- 与 **GatedNorm**（RMSNorm 后低秩 sigmoid 自门）合并：对加宽流做**逐分支 RMSNorm** → 由全部支预测 **逐元素门** $G\in\mathbb{R}^{n_r\times d}$（瓶颈秩 $r=d/8$）→ 平均得块输入；
- 写出：每分支一个数据依赖标量 $s_i=2\sigma(\cdot)$，$R_i' = R_i + s_i y$；
- GR **替代**块的 pre-norm（不再叠一层 Norm）；attention 与 MLP **各一套** GR。

### 6.3 分支用途（机制分析，Fig. 7）

无 $H_{res}$ → 可精确分解「谁写、谁读」。相对无 GR 参考：

- **恰好一条**长程分支（典型 skip ≈ **10.9** 层），另三条偏局部（skip 约 3.4–3.9）；
- 长程多把 **早期 GDN 输出**保到深处，且主要被 **softmax 注意力层**读回——全局注意力成「整合 GDN 压掉的长程历史」的枢纽；
- 总跨层信息量相近，但分布从 mid-range 挪到 **邻接 + 超长程**。

### 6.4 推理侧取舍

- **稀疏只读 top-2 分支**：预训练几乎无损，**后训练明显变差** → 未采用（又一例「预训练指标会误导」）。
- 残差状态可 **FP8** 存（门控限幅）≈ 相对 BF16 带宽减半；读/写各融合成单核。

---

## 七、N-gram Embedding（§2.3，辅）

| 选择 | 报告结论 |
|---|---|
| 放置 | 固定参预算下多层无稳定收益；选 **Layer 2**（便于 prefetch 盖住第 1 层计算） |
| 与 MoE 抢预算 | 固定总参时抬 n-gram、减专家 → loss 非单调，下游**无明显优于纯 MoE** → **MoE 预算固定，额外加表** |
| 词表放大（相对 tokenizer $V=250K$，Qwen3.5） | **20×→200×**：loss **单调下降**；下游整体增益但部分饱和/波动；中文 C-Eval/CMMLU **随词表持续升**（Tab. 9） |
| 产品规模 | 摘要 / Tab. 11：**51B** n-gram 参数，**off-accelerator** |

---

## 八、重点 4：Muon 与超参 / 稳定性（§3）

### 8.1 谁用 Muon（§3.1）

| 用 Muon | 用 AdamW / Adam |
|---|---|
| 作线性映射的 2D 权重：Attn q/k/v/o、GDN 入/出投影、routed+shared expert fc1/fc2、n-gram 的 key/value 投影 | 输入 embedding、输出 head；**MoE router**（Muon 早期扰动路由，中后期也无明显收益）；**GR 两个低秩投影**（极瘦长）；n-gram **表本体**用 Adam **且关 weight decay** |
| NS：**8** 步；Polar Express 系数；$\mu=0.95$；$\gamma(A,B)=0.2\sqrt{\max(A,B)}$；Frobenius 稳定常数 $10^{-14}$ | — |

**融合参数必须先拆再正交化**：qkv / GDN 输入按 **per-head** 拆；SwiGLU fc1 拆 gate/up。融合整矩阵正交化会混奇异方向且 $\gamma$ 形状错。GDN 的 decay/β（每头标量）与若干 output gate 走 AdamW。

**工程：** Canzona —— 按估计 NS FLOPs 做 α-balanced 整参划分 + 跨 TP All-to-All 拼满矩阵；拆分后小核用 **CUDA graph** 包住整步。

### 8.2 缩放律重拟合（§3.2）

架构 + Muon → 相对 Qwen3.5 配方，预测 **更大 batch、更大 LR、随规模衰减更慢**。

| 验证 | 设置 | 结果（报告数字） |
|---|---|---|
| Batch @大 token | 20 层 10.8B-A0.89B · **4T** tokens | 新最优点 $B=25.2M$ 相对旧 $B=12.6M$ 终局 loss 优 **$7.2\times10^{-3}$**；$B=37.7M$ 仅差 $4.3\times10^{-4}$ |
| Batch warmup | 6.3M 阶梯升到 25.2M（524B tokens 处到位） | **不优于**从一开始用目标 B；多 **18.8%** optimizer steps → **生产不用 warmup** |
| LR @更大模型 | 48 层 **156B-A7B** · 419B tokens | 相对 Qwen3.5 配方终局 loss 优 **$7.8\times10^{-3}$**；预测点附近碗底平坦；榜均 **60.55 vs 56.41**（Tab. 10） |

### 8.3 稳定性应力测试（§3.3）

协议：28 层 MoE，LR **恒定**在最优的 **2× / 4×**（模拟长时峰值 LR）；clip 阈值 **0.5**。

| 应力 | AdamW + Qwen3.5 结构 | Muon ± GR |
|---|---|---|
| 2× LR | spike **4.3 / 10k steps** | **0.2 / 10k** |
| 4× LR | spike **183 / 10k**；clip 触发 213/19932 | Muon **从不**触 clip；**Muon+GR：零 loss spike** |

单变量开/关 GatedNorm（AdamW、结构固定，3× LR）：spike **32.0→3.2 / 10k**，clip 穿越 **256→20**。机制叙述：高 LR 需要重缩放；无显式门则靠激活 outlier 长大 → 脆弱；乘性门直接提供重缩放。

**生产前 276B tokens**（同数据序 / LR schedule / optimizer）：相对「Qwen3.5+Muon」，+GR loss ↓**0.026**，完整 Flash-Next 再 ↓**0.032**（合计 **0.058**）；门控跑梯度 p99.9 与滑动 std 显著更低，且可无 qk-clip / SwiGLU-clip。全文称全量 Flash-Next 训练 **无单次 loss spike / 无异常 grad norm 波动**。

---

## 九、Base 评测（§4 / Tab. 11）

对照：**Qwen3.8-Flash-Next-Base** vs **Qwen3.8-27B-Base** vs **Qwen3.7-Plus-Base（397B / 17B act）**。

| | Flash-Next | 27B | 3.7-Plus |
|---|---:|---:|---:|
| # Params | **125B** | 27B | 397B |
| # Activated | **6B** | 27B | 17B |
| # N-gram | **51B** | — | — |

摘要宣称：14 榜中 **领先 Plus 8 项**，其余落后至多 **2.6** 点；激活参约 **1/3**、训练 tokens 约 **1/3**、训练 FLOPs 约 **1/9**。
全文 14 项均 **高于 27B**；相对 Plus：例如 MMLU-Pro **73.23 > 70.90**，SuperGPQA **51.36 > 48.42**，MATH **72.78 < 74.38**，MultiPL-E **79.09 < 81.68**（完整表见 PDF Tab. 11）。

> 本报告 **未**给出后训练 chat / thinking 主表；评测对象为 **Base**。

---

## 十、待核实与引用

### 10.1 待核实（禁止编造）

| # | 项目 | 原因 |
|---|---|---|
| 1 | Flash-Next **总层数 / hidden / heads / 专家总数与激活专家数** | Tab. 11 仅总参/激活/n-gram；Fig. 1 未标 $N$ |
| 2 | 预训练 **总 token、阶段划分、数据配比、GPU 型号×小时** | 仅有消融尺度与「约 1/3 tokens、约 1/9 FLOPs」相对 Plus 的说法 |
| 3 | n-gram **具体阶数、hash 头数、51B 如何对应 vocab scale** | §2.3 给方法族与消融表，未把 51B 拆成配置单 |
| 4 | 原生上下文 / YaRN 扩展到产品宣称长度 | 本 PDF 评测到 **1M**（RULER/MRCR）；产品卡数字需发布页/模型卡 |
| 5 | 后训练 / multimodal 权重关系 | 本报告主线架构与 Base；博文「预览 Qwen4」不写入本卡数字 |
| 6 | Canzona / FlashQLA 之外的并行拓扑与精度配方 | 仅描述 Muon 分片与 QSA/GDN 核 |

### 10.2 引用

| 编号 | 文献 | 日期 | URL / 路径 |
|---|---|---|---|
| [Q38N] | On the Design of Qwen3.8-Next Architecture… | arXiv **2026-08-31**（v1） | https://arxiv.org/abs/2608.30320 ；PDF https://arxiv.org/pdf/2608.30320 |
| [Q38N-PDF] | 本地副本 | 2026-09-22 下载 | `https://arxiv.org/abs/2608.30320` |
| [Q38N-GH] | QwenLM/Qwen3.8-Flash-Next（含 tech_report.pdf） | — | https://github.com/QwenLM/Qwen3.8-Flash-Next |
| [QWEN3] | Qwen3 Technical Report（对照锚，勿重写） | 2025-05 | 模型与技术报告/厂商报告/Qwen3技术报告深读.md |
| [B4] | 优化器与训练稳定性 | 2026-09-22 | 训练/持续与技巧/优化器与训练稳定性.md |

### 10.3 跟读一句话

> **Qwen3.8-Flash-Next = 125B/6B MoE + 51B 离卡 n-gram +（3 GDN : 1 Attn→CPT 换 QSA）+ 四分支 Gated Residual + Muon（拆融合、8×NS）+ 重拟合更大 LR/B（无 batch warmup）——用稳定性余量换效率，Base 上以约 1/9 FLOPs 逼近 397B-A17B。**

## 相关笔记

- [[GPT6AstraSystemCard|GPT-6 Astra]]
- [[DeepSeekV41Flash深读|DeepSeek-V4.1 Flash]]
- [[Qwen38Next架构深读|Qwen3.8-Next]]
- [[ClaudeOpus5SystemCard|Claude Opus 5]]
- [[GRPO与DAPO算法族|GRPO→DAPO]]
- [[SystemCard与TR扫描2025至2026|TR 扫描]]

