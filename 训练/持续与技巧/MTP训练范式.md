---
title: "MTP 训练范式：AdaMTP + MTP-D + OCC（≠ EntMTP）"
topic: MTP训练范式
date: 2026-09-22
lines: [架构思想, 训练目标/系数]
status: archived
sources:
 - https://arxiv.org/abs/2608.00434 # 882K
 - https://arxiv.org/abs/2603.23911 # 7.9M
 - https://arxiv.org/abs/2605.28184 # 786K
 - https://arxiv.org/abs/2509.18362 # 540K（补链）
arxiv: ["2608.00434", "2603.23911", "2605.28184", "2509.18362"]
related: ["EntMTP熵引导投机解码", "EAGLE3投机解码", "推理引擎生态"]
github_occ: "https://github.com/MarkXCloud/RL-MTP"
github_fastmtp: "https://github.com/Tencent-BAC/FastMTP"
archived: 2026-09-22
---

# MTP 训练范式：AdaMTP + MTP-D + OCC（≠ EntMTP）

> **定位**：MTP训练范式 **P1 Infra / 训练横切**——在 **B7** 已立投机「草稿—校验」基线、**[[EAGLE3投机解码]]** 已补（草稿头训练增量）、**[[EntMTP熵引导投机解码]]** 已写（**训练免费**的运行时选树调度）之后，本卡只写 **MTP 头/损失本身怎么训**：三条训练范式主文 **AdaMTP**（熵分段 + 动态掩码 MTP）、**MTP-D**（主头→MTP 头自蒸馏 + looped 扩头）、**OCC**（RL 后训联合 MTP 的最优系数在线校准）；**FastMTP** 仅作「训推对齐」补链，不升第三主轴。
> **攻坚线**：**架构思想（主）**——监督深度 / 蒸馏对象 / RL 系数如何改 MTP 训练目标；**训练目标与系数字段（辅）**——文内 Avg、AR/CAR、speedup、AIME avg@32 等照录。
> **硬划界（开篇写清）**：
> - **≠ [[EntMTP熵引导投机解码]] EntMTP**：EntMTP 是推理期 **TopologyBank 选树**、**不改**目标权重；本卡改的是 **训练损失 / 头对齐 / RL λ**。二者都谈「熵」，但 AdaMTP 的熵用于 **训练数据分段与损失掩码**，EntMTP 的熵/path-value 用于 **在线换草稿树**——勿混。
> - **≠ [[EAGLE3投机解码]] EAGLE-3**：不重写 training-time test、低/中/高特征融合、SGLang 大 batch 表；FastMTP 文内只「兼容 EAGLE-style 递归草稿」时点到接口，不展开 EAGLE 谱系。
> - **≠ B7 投机通史**：不写 Leviathan / Chen / Medusa / Lookahead 证明与引擎选型全文；「自投机 draft–verify、同分布」只当无损接口一句。
> **禁止编造**：倍率、AR/CAR、λ、TopN、基准分一律锚定官方 PDF（2026-09-22 CST）。
> **入库体积**（`ls -lh`，均 **<20MB** → 二进制可入库）：AdaMTP **882K**；MTP-D **7.9M**；OCC **786K**；FastMTP **540K**。禁止权重 / 数据集 / 视频。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题（PDF） | arXiv | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主①** | *AdaMTP: An Adaptive Training Paradigm for Multi-Token Prediction* | **2608.00434v1** \[cs.CL\]（**1 Aug 2026**） | `https://arxiv.org/abs/2608.00434` | **882K**（902,242 B） | 12 A4 | （77K） |
| **主②** | *Self-Distillation for Multi-Token Prediction*（方法名 **MTP-D**） | **2603.23911v1** \[cs.CL\]（**25 Mar 2026**） | `https://arxiv.org/abs/2603.23911` | **7.9M**（8,241,991 B） | 18 A4 | （187K） |
| **主③** | *Joint Training of Multi-Token Prediction in Reinforcement Learning via Optimal Coefficient Calibration*（**OCC**） | **2605.28184v1** \[cs.LG\]（**27 May 2026**） | `https://arxiv.org/abs/2605.28184` | **786K**（804,594 B） | 13 A4 | （93K） |
| **补链** | *FastMTP: Accelerating LLM Inference with Enhanced Multi-Token Prediction* | **2509.18362v1** \[cs.LG\]（**16 Sep 2025**） | `https://arxiv.org/abs/2509.18362` | **540K**（552,504 B） | 14 A4 | （69K） |

| 材料 | 作者 / 机构（摘要页） | 代码（文内明示） |
|---|---|---|
| AdaMTP | Cui et al.（CityU / Huawei / MBZUAI / McGill / PKU） | 正文摘要区 **未给出** GitHub → 本卡不编造仓址 |
| MTP-D | Zhao, Xie\* 等（Tencent LLM Dept.） | 正文 **未给出** GitHub → 不编造 |
| OCC | Wang, Chai 等（UCAS / CASIA / Meituan） | https://github.com/MarkXCloud/RL-MTP |
| FastMTP | Cai 等（Tencent） | https://github.com/Tencent-BAC/FastMTP ；HF `TencentBAC/FastMTP` |

**体积判定**：四份 PDF 均 **<20MB**，按验收规矩 ****；MTP-D 最大（**7.9M**），仍远低于「正式外链」阈值。同步抽取另存 、、、 的 `full.txt`。

**一句话抓手：** 固定 horizon / 头间分布隙 / RL 联合时的 λ 漂移，是 MTP **训练侧**三大痛点；AdaMTP 用 **熵边界掩码** 清噪声梯度，MTP-D 用 **stop-grad TopN KL** 抬接受率并可 **loop 扩头**，OCC 用 **log-prob 代理** 在线追最优 λ，使 MTP 可安全回流进 RL 主模型。

---

## 二、议题边界：只写「MTP 怎么训」，不写选树 / EAGLE-3 / 投机通史

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[EntMTP熵引导投机解码]]** | 「自投机 + 草稿树」是推理接口；熵可作可预测性信号 | TopologyBank、path-value 选树、Hydra/Medusa 默认树 tok/s 主表 |
| **[[EAGLE3投机解码]]** | FastMTP「EAGLE-style 递归草稿」兼容句 | training-time test、多层特征融合、SGLang Table 3–4 |
| **B7 投机通史** | draft–verify、边际同分布 → 无损加速 | Leviathan/Chen 证明、引擎选型全文 |

### 2.2 本卡三条主轴 vs 补链（训练阶段对照）

| 方法 | 训练阶段 | 改什么 | 不改什么（文内口径） |
|---|---|---|---|
| **AdaMTP** | 预训练 LLM 上 **SFT/retrofit MTP** | 每 token **自适应深度 $d_t$** + 动态掩码 $L_{\mathrm{MTP}}$ | 默认可仍用固定 horizon 自投机解码 |
| **MTP-D** | **预训练 / 续训**（DeepSeek 级联 MTP） | $L^{\mathrm{CE}}+L^{\mathrm{KL}}$（主头 TopN logits → MTP，**sg**）；looped 复制扩头 | 扩头时 **冻结**主模型与已训 MTP 组 |
| **OCC** | **RLVR 后训**（DAPO/GSPO） | 在线 $\lambda_t=\lambda_+\cdot\hat c_t/(\hat v_t^2+\epsilon)$ | 仍允许与 Detach 对照；不重写 PPO/DAPO 算法本身 |
| **FastMTP（补）** | 冻结主模，**轻量 FT 单共享 MTP 头** | 递归多步自蒸馏 + 语言感知词表压缩（草稿侧） | 校验仍全词表 → 无损 |

跟读口诀：

`
AdaMTP = 训练时「别跨语义边界硬预测」
MTP-D = 预训练时「主头教 MTP 头对齐 logits」
OCC = RL 时「MTP 系数别写死，跟着相关/扰动漂移」
FastMTP = 推时「单头递归要按推法训」（补链，非本卡第三范式）
`

---

## 三、AdaMTP：熵分段 + 动态掩码 MTP（arXiv 2608.00434）

### 3.1 诊断：固定 horizon → 表示干扰

标准 MTP（共享骨干 + 主头 $\theta_0$ + $n-1$ 辅助头）在每步强制预测固定 $n$ 个未来 token。文观察：语义块内预测熵近似单调下降，**跨边界**出现熵突增；跨边界的辅助监督 → 噪声梯度经共享 $z_{1:t}$ 回传 → **表示干扰**，标准 MTP 平均分常 **低于** 同设定 NTP（Table 1）。

### 3.2 熵分段与自适应深度（§3.1）

用 **同一待 SFT 基座** 算 next-token 熵 $E_t=H(P(\cdot|x_{<t}))$，差分 $\Delta E_t=E_{t+1}-E_t$。$\Delta E_t>\tau$ 处切组；$\tau$ 按数据集搜索，使 **平均组长大致对齐头数 $n$**。

组 $G_k=[s_k,e_k)$ 内 token $x_t$ 的自适应深度：

$$
d_t=\begin{cases}
e_k-t-1 & t<e_k-1\\
|G_{k+1}| & t=e_k-1
\end{cases}
\qquad\text{有效监督}\ \min(d_t,n)
$$

组内只预测到本组末；**边界 token** 预测 **下一整组**。

### 3.3 两阶段训练 + 掩码损失（§3.2）

1. **Warm-up**：冻骨干与主 LM 头，只训辅助头；自蒸馏数据；CE（式 (6)）。
2. **Adaptive joint**：LoRA（$r=32,\alpha=16$）联合骨干+头；损失

$$
L_{\mathrm{MTP}}=\sum_{j=1}^{n-1}\sum_t \mathbf{1}(j+1\le d_t)\,L_{\mathrm{CE}}(\mathrm{Head}_j(h_t),x_{t+j+1}),\quad
L_{\mathrm{total}}=L_{\mathrm{LM}}+\lambda L_{\mathrm{MTP}}
$$

默认：$n=4$，$\lambda=0.1$；warm-up 1 epoch $10^{-3}$，joint 3 epochs $10^{-5}$；四卡 H800，全局 batch 256。语料：Math + Evol-Instruct-Code + Alpaca-GPT4；二阶段再抽 **10k**（数:码:通 ≈ 4:4:2）。

### 3.4 推理双模式（§3.3，勿升格为 EntMTP）

| 模式 | 行为 | 文内用途 |
|---|---|---|
| **Fixed-horizon（默认）** | 每步仍草稿满 $n$，Medusa 式树校验 | Table 2 加速 **相对标准 MTP 的增益归因于训练**（同推理协议） |
| **Adaptive-horizon** | 用实时熵增量超阈则停草稿，剪验证候选 | 单样本增益有限；**大 batch** 更省验证算力（Fig.4） |

### 3.5 数字照录（Table 1–2）

**任务 Avg（NTP / MTP / AdaMTP）**

| 骨干 | NTP | MTP | **AdaMTP** |
|---|---|---|---|
| Llama-3.1-8B | 36.32 | 35.90 | **36.85** |
| Qwen-2.5-7B | 62.92 | 61.60 | **63.19** |
| Gemma-3-12B | 45.72 | 44.99 | **46.12** |

（Qwen 族上各 SFT 范式均低于 Base **64.95**，文归因微调语料分布偏移，非 MTP alone；AdaMTP 仍压过 NTP/MTP。）

**Speedup vs NTP=1.00×（Fixed-horizon）摘录**

| 骨干 | 任务 | MTP | AdaMTP |
|---|---|---|---|
| Llama3.1 | GSM8K | 1.65× | **2.12×** |
| Llama3.1 | HumanEval | 1.86× | **2.01×** |
| Gemma3 | GSM8K | 2.38× | **2.75×** |

头数扫描（Llama GSM8K）：标准 MTP 随 $n$ 升准确率近单调降；AdaMTP 维持高于 NTP，峰值 $n=4$ 准确率 **13.12**。

---

## 四、MTP-D：主头自蒸馏 + looped 扩头（arXiv 2603.23911）

### 4.1 设定：DeepSeek 级联 MTP 上的两痛点

沿用 DeepSeek-V3 级联 MTP 损失 $L^{\mathrm{CE}}_{\mathrm{mtp}}=\sum_k\alpha_k\mathrm{CE}(\hat P^{k},\cdot)$。痛点：(a) MTP 头接受率有限 → **累积接受率**指数塌；(b) 多头 CE 与主头 **跷跷板**，工业常只挂 1–4 头。

### 4.2 方法：梯度切断的 TopN KL 自蒸馏（§3.2）

$$
L^{\mathrm{KL}}_{\mathrm{mtp}}=\sum_k\beta_k\,\mathrm{KL}\big(\tilde P^{k},\,\mathrm{sg}(\tilde Q)\big),\quad
L_{\mathrm{mtp}}=L^{\mathrm{CE}}_{\mathrm{mtp}}+L^{\mathrm{KL}}_{\mathrm{mtp}}
$$

- $\mathrm{sg}$：**切断**主头 logits $Q$ 回流 → 主头不被蒸馏拖垮。
- **TopN**：默认 $N=10{,}000$（词表例 122,880；全词表 KL 贵且长尾噪声）。
- 默认 $\beta_k=1.0$、**forward KL**。消融（Table 2）：去 detach → 主头均值掉约 **1.49** 点；TopN 过小伤 AR；$\beta_k=1.5$ 主头 loss 升。

### 4.3 Looped extension（§3.3）

把已训 $m$ 头 **权重复制**初始化下一组 $m$ 头，续训；主模与旧头 **冻结**。训练免费 loop 试点：1→8 时普通 MTP 在 AGIEval-en 上第 3 头 CAR 可到 **0.6%**，MTP-D 仍 **26.70%**。续训（约 **70B** tokens；主预训练 **350B** FineWeb-Edu）可扩到 **8–16** 头；摘要：4 头相对基线 **+7.5%** 接受率 ≈ **+22.9%** 加速；loop 扩头相对 1-head MTP 可达摘要所称 **+220.4%**（Fig.5 中 4-head MTP-D loopto8 平均加速约 **3.052×** 量级，以图/附录为准跟读）。

### 4.4 设定与主表口径（§4）

| 项 | 值 |
|---|---|
| 模型 | **2B Dense**；**N10B-A1B MoE**（文写 A1B MoE） |
| 数据 | FineWeb-Edu-**350BT**；loop 续训 **70B** |
| 硬件 | 主实验 **256× H20** |
| 指标 | 主头 Accuracy；每头 **AR** / **CAR**；Speedup 相对 **1-head DeepSeek MTP** |
| 解码 | 主头约束投机（Algorithm 1）→ 与主头采样一致 |

Table 1 例：2B Dense $K=1$，AGIEval-en AR：MTP **85.75** → MTP-D **88.98**；$K=4$ 第 4 头 CAR/AR：MTP **45.47/83.77** → MTP-D **52.96/86.46**（他任务同表）。文称 4 头时第 4 头 CAR 平均约 **+7.5%** → **+22.9%** 加速；相对单头配置四头 MTP-D 加速可达约 **107.4%**（§4.2 叙述）。

---

## 五、OCC：RL 联合 MTP 的最优系数校准（arXiv 2605.28184）

### 5.1 问题：为何工业默认 detach MTP

veRL / slime 等文档：MTP 梯度回主模易严重掉分 → 默认 **detach**。GLM-5、Composer-2、Nemotron-3 Super 等亦隔离或事后单独 FT MTP。目标：在 **不 detach** 时仍让联合训练不崩。

### 5.2 分解：一阶相关 + 二阶扰动（§3.1–3.2）

$L$-smooth 下，带 $\lambda$ 的 MTP 更新使每步改进含

$$
\Delta_{\mathrm{MTP}}=\eta\lambda(1-L\eta)\underbrace{\langle g_{\mathrm{RL}},g_{\mathrm{MTP}}\rangle}_{c}
-\frac{L\eta^2\lambda^2}{2}\underbrace{\|g_{\mathrm{MTP}}\|^2}_{v^2}.
$$

| 体制 | 文内结论 |
|---|---|
| **Detach** | $g_{\mathrm{MTP}}=0$ w.r.t. 主模 → $\Delta=0$ |
| **CE Loss** | 与 advantage 加权的 RL 方向期望相关≈0 → 只剩负的二阶项 → 系统性掉分 |
| **Policy Loss**（同 RL 目标、**固定 λ**） | 早期 $c$ 大 → 升；后期平坦区 $c$ 衰减而 $v^2$ 仍在 → **先升后降** |

闭式最优：$\lambda^*\propto c/v^2$（平滑常数并入全局比例 $\lambda_+$）。

### 5.3 OCC：log-prob 代理在线追 $\lambda_t$（§3.4）

小步更新下 $\delta=\log\pi_\theta-\log\pi_{\mathrm{old}}$：

$$
\hat c_t=\langle\delta_{\mathrm{RL}},\delta_{\mathrm{MTP}}\rangle,\quad
\hat v_t^2=\|\delta_{\mathrm{MTP}}\|^2,\quad
\lambda_t=\lambda_+\cdot\frac{\hat c_t}{\hat v_t^2+\epsilon}
$$

默认 $\lambda_+=1.0$，$\epsilon=10^{-8}$。Fig.4：$\lambda_t$ 早期大、相关衰减后趋近 0。墙钟（Fig.5）：OCC **8.07 s/step** ≈ Detach **8.11 s**；全模梯度 **45.06 s**（约 **5.6×** 慢）。

### 5.4 主结果（Table 1，avg@32 %）

训练：DAPO-Math-**17k**；200 steps；bs 128；lr $10^{-6}$；**128× H20**；veRL。基座 MiMo-7B-RL（+GSPO 复现）、GLM-4.5-Air（106B-A12B MoE）。

| 设定 | Detach | CE | Policy | **OCC** |
|---|---|---|---|---|
| MiMo + DAPO Avg | 58.9 | 47.7 | 57.4 | **61.7** |
| MiMo + GSPO Avg | 57.8 | 50.0† | 56.2 | **60.1** |
| GLM-4.5-Air + DAPO Avg | 65.9 | 54.8 | 64.4 | **67.6** |

†表中 GSPO-CE Avg 文录 **50.0**（CE 仍最差）。AIME24 例（MiMo+DAPO）：Detach **45.3** / CE **16.1** / Policy **38.9** / OCC **45.9**；AIME25：Detach **36.7** / OCC **46.7**。Table 2：固定 $\lambda\in\{0.1,0.2,0.5,1.0\}$ 的 Policy 均压不过 OCC。

---

## 六、FastMTP 补链：训推对齐的单共享头（arXiv 2509.18362）

> **角色**：OCC 相关工作已点名 FastMTP；本卡只录「**按递归推理模式训单头** + 草稿侧词表压缩」，**不**升为与 AdaMTP/MTP-D/OCC 并列的第三训练范式，**不**展开 EAGLE-3。

| 要点 | 文内 |
|---|---|
| 架构 | DeepSeek-V3 式 MTP，但 **单头共享权重** 递归 $K$ 步（省多模块 KV/调度） |
| 训练 | 冻主模（<3% 参数）；自蒸馏数据；指数衰减 $\alpha_k\propto\beta^{k-1}$ |
| 草稿加速 | 语言感知高频词表压缩（FR）；**校验仍全词表** → 无损 |
| 推理 | EAGLE-style 递归草稿 + 并行校验 |
| 基座 / 仓 | MiMo-7B-RL；GitHub / HF 见 frontmatter |

**Table 1 抓手（MiMo-RL-7B，Self-data FT+FR，avg）**：**2.03×** vs NTP；vanilla MTP reuse **1.21×** → 文称相对 vanilla **+82%**；接受率约 **70%→81% / 11%→56% / 2%→36%**（第 1/2/3 草稿位；贡献列表另写首 token **81%**）。七基准；本卡不重抄全表 tok/s。

---

## 七、三条范式对照（跟读用）

| 维 | AdaMTP | MTP-D | OCC |
|---|---|---|---|
| 阶段 | SFT retrofit | 预训练 + 续训扩头 | RLVR 后训 |
| 核心旋钮 | 掩码深度 $d_t$ | TopN KL + loop 复制 | $\lambda_t(\hat c,\hat v)$ |
| 主风险 | 跨边界噪声 CE | 头间分布隙 / 主头被拖 | CE 无关扰动；固定 λ 相变 |
| 熵角色 | **训练分段** | 非主轴 | 非主轴（相关衰减相变） |
| 与 EntMTP | 都谈熵，**损失掩码 ≠ 选树** | 抬 AR 可服务投机，**不调度树** | 联合 RL，**不调度树** |

---

## 八、跟读清单（可复述）

1. **划界** ← 本卡 = MTP **训练**；EntMTP = **推理选树**；EAGLE-3 / B7 不重写。
2. **AdaMTP** ← $\Delta E>\tau$ 切组 → $d_t$ → $\mathbf{1}(j{+}1\le d_t)$ 掩码；Avg 三骨干皆高于 NTP/MTP；GSM8K 上 Llama **2.12×**、Gemma **2.75×**。
3. **MTP-D** ← $\mathrm{sg}$ + TopN=10k KL；4 头 **+7.5%** AR ≈ **+22.9%** 速；loop 可扩 8–16，摘要相对 1-head **+220.4%**。
4. **OCC** ← $\Delta_{\mathrm{MTP}}=$ 相关 − 惩罚；CE 崩、Policy 先升后降；OCC Avg **61.7**（MiMo+DAPO）压过 Detach **58.9**，步时≈Detach。
5. **FastMTP（补）** ← 单共享头按递归推法自蒸馏 + FR → **2.03×**（vs vanilla MTP **1.21×**）。

---

## 九、待核实 / 不写

- **不写**：EntMTP TopologyBank 主表；EAGLE-3 SGLang 表；B7 通史；Medusa/Hydra 方法课。
- 正式引用以官方 PDF / arXiv HTTPS 为准；勿提交权重、数据集镜像、视频。
- **AdaMTP / MTP-D**：文内无 GitHub → 不强行补仓。
- **MTP-D「+220.4%」**：摘要宣称；细粒度任务分解以 Fig.5 / Table 8 为准，跨表勿自行换算成未出现的 tok/s。
- **OCC**：GSPO 行 CE Avg 文表为 50.0，与各点分手算均值若有排版歧义，以 PDF Table 1 印刷为准。
- **FastMTP**：仅补链；中英词表压缩细节、完整七基准 tok/s 表不升主文。

---

*2026-09-22 CST。体积：`ls -lh` 同日核对。*

## 相关笔记

- [[激活操控与表征工程|Activation Steering]]
- [[MTP训练范式|MTP Training]]
- [[MOC_阅读入口|内容地图]]

