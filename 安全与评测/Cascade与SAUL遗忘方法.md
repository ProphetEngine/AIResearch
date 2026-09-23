---
title: "遗忘方法增量：Cascade + SAUL（≠ 10 综述 / OpenUnlearning 复读）"
topic: Cascade与SAUL遗忘方法
date: 2026-09-22
lines: [方法接口, 遗忘—效用权衡, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.16890 # 1.38MiB / 27p；≪10MB → 官方 HTTPS 外链
 - https://arxiv.org/abs/2608.16249 # 0.63MiB / 29p；≪10MB → 官方 HTTPS 外链
 - https://arxiv.org/abs/2608.26743 # 1.24MiB / 17p；补链；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2609.16890
 - https://arxiv.org/pdf/2609.16890
 - https://arxiv.org/abs/2608.16249
 - https://arxiv.org/pdf/2608.16249
 - https://arxiv.org/abs/2608.26743
 - https://arxiv.org/pdf/2608.26743
 - https://github.com/Noryxen/Cascade
 - https://anonymous.4open.science/r/graphSU-35B4
arxiv: ["2609.16890", "2608.16249", "2608.26743"]
related: ["Cascade与SAUL遗忘方法", "对齐脉络RLHF与偏好优化", "LLM水印", "TEE机密推理"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 遗忘方法增量：Cascade + SAUL（≠ 10 综述）

> **定位**：**隐私/遗忘方法切片**——在 **[[隐私与机器遗忘]]** 已立「遗忘综述 + OpenUnlearning 元评测框架」之后，本卡只写 **2026 近窗两条正交方法增量**：
> - **Cascade**（*Hierarchical Recoverability Control*，arXiv:**2609.16890**v1，页眉 **15 Sep 2026**）：把遗忘写成 **内部可辨识性（internal identifiability）最小化**，用 **路径 / 双曲表征 / 解码** 三级压低可恢复性。
> - **SAUL**（*Sharpness-Aware Augmented-Lagrangian Unlearning*，arXiv:**2608.16249**v1，页眉 **17 Aug 2026**）：把遗忘写成 **显式约束**「忘够即可」，用 **增广拉格朗日控制器** 在满足阈值后 **关掉 forget 侧更新**，并配 **非对称锐度感知 + 双优化器状态**。
> **补链（不升主）**：**GRAPHSU**（*Graph-Guided Selective Unlearning*，arXiv:**2608.26743**v1，页眉 **27 Aug 2026**）——用多视图支持路径图扩展删除范围，超出 forget seed；议程标 **仅补链/后置**。
> **攻坚线**：**方法接口 / 遗忘—效用权衡（主）** + **文内 TOFU / MUSE / WMDP（及 GRAPHSU 的 PISTOL）字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[隐私与机器遗忘]]**：禁止重做 **180+ 篇通史**、流水线阶段地图、OpenUnlearning **13×16 元评测全文**。本卡 **不复读** OpenUnlearning 指标 Faithfulness/Robustness 元评测；仅在需要时把 TOFU/MUSE/WMDP 当 **评测协议入口**。
> - **≠ [[对齐脉络RLHF与偏好优化]]**：禁止写成 RLHF / DPO / CAI 对齐通史。SAUL 的约束优化与偏好优化 **共享「拉格朗日/对偶」词汇**，但目标是 **forget-set 损失阈值**，不是人类偏好 BT/DPO。
> - **≠ [[LLM水印]]**：禁止写成生成文本水印 / SynthID / 去水印。遗忘擦权重 ≠ 输出侧溯源水印。
> - **≠ [[TEE机密推理]]**：禁止写成 GPU/CPU TEE 机密推理。擦 forget 集 ≠ data-in-use 加密隔离。
> - **禁止写成 OpenUnlearning 复读**：不展开统一库算法枚举、450+ checkpoint、指标 meta-eval 主文；本卡是 **两条（+一条补链）方法深读**。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。文内未给出的完整超参网格 / 未发表攻击复现步骤 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A · Cascade** | Yu, Duan, Li, Wang, Li, Zhou, Sun & Fan, *Cascade: Hierarchical Recoverability Control for Large Language Model Unlearning* | arXiv:**2609.16890v1** \[cs.CL\] **15 Sep 2026**；XMP MetadataDate 2026-09-16T00:58:14Z（→ **2026-09-16 08:58 CST**）；`https://arxiv.org/abs/2609.16890`（**1,450,150 B ≈ 1.38MiB** / **27** 页 A4） | 主锚：三级可恢复性控制 |
| **主文 B · SAUL** | Choi, Yang & Park, *SAUL: Sharpness-Aware Augmented-Lagrangian Unlearning* | arXiv:**2608.16249v1** \[cs.LG\] **17 Aug 2026**；XMP MetadataDate 2026-08-18T01:46:15Z（→ **2026-08-18 09:46 CST**）；CC-BY-4.0；`https://arxiv.org/abs/2608.16249`（**661,815 B ≈ 0.63MiB** / **29** 页 A4） | 主锚：显式 forget 约束 + ALM |
| **补链 · GRAPHSU** | Khan, Sarwar, Cong, Yi & He, *Graph-Guided Selective Unlearning for Language Models: Controlling Support Routes Beyond Forget Seeds* | arXiv:**2608.26743v1** \[cs.AI\] **27 Aug 2026**；XMP MetadataDate 2026-08-28T00:39:19Z（→ **2026-08-28 08:39 CST**）；CC-BY-4.0；`https://arxiv.org/abs/2608.26743`（**1,295,420 B ≈ 1.24MiB** / **17** 页 A4） | 补链：支持路径图扩 scope |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| Cascade PDF | `https://arxiv.org/abs/2609.16890` | **1.38MiB** | **27** | **官方 HTTPS 外链**（≪10MB；页数适中） |
| Cascade 抽取 | | 186K | — | 全文检索 |
| SAUL PDF | `https://arxiv.org/abs/2608.16249` | **0.63MiB** | **29** | **官方 HTTPS 外链** |
| SAUL 抽取 | | 118K | — | 全文检索 |
| GRAPHSU PDF | `https://arxiv.org/abs/2608.26743` | **1.24MiB** | **17** | **官方 HTTPS 外链**（补链；仍 ≪10MB） |
| GRAPHSU 抽取 | | 101K | — | 全文检索 |

**代码入口（文内明示，2026-09-22 未做线上可用性核验）：**
- Cascade：`github.com/Noryxen/Cascade`
- GRAPHSU：`https://anonymous.4open.science/r/graphSU-35B4`（匿名仓；落地以作者正式发布为准）
- SAUL：正文未给独立公开仓链接（以 PDF / 作者页为准；**不编造 URL**）。

**一句话抓手：**
[[隐私与机器遗忘]] 回答「遗忘领域有哪些方法族、怎么统一评」；本卡回答「**2026 近窗两条具体算法如何改遗忘—效用接口**」——Cascade 攻 **内部仍可被改写/抽取提示恢复**；SAUL 攻 **加权目标隐式规定「忘多少」导致过忘**；GRAPHSU 补一句 **删 seed 不够、还要控支持路径**。

---

## 二、议题边界：近窗方法切片 ≠ 通史 / ≠ 对齐 / ≠ 水印 / ≠ TEE

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **遗忘综述 + OpenUnlearning** | 180+ 方法地图；统一基准与指标元评测 | **[[隐私与机器遗忘]]** | **否**（禁通史 / 禁元评测复读） |
| **RLHF / DPO / CAI** | 偏好对齐流水线 | **[[对齐脉络RLHF与偏好优化]]** | **否**（禁对齐通史） |
| **LLM 水印** | 生成侧溯源 / SynthID | **[[LLM水印]]** | **否** |
| **TEE 机密推理** | data-in-use 隔离与 CC tax | **[[TEE机密推理]]** | **否** |
| **Cascade + SAUL（+ GRAPHSU 补链）** | 可恢复性控制 / 显式约束优化 / 支持路径扩 scope | **本篇** | **是** |

跟读直觉：[[隐私与机器遗忘]] 是 **地图与量尺**；本卡是 **两把新扳手**（+一把扩 scope 的夹具）。共享 TOFU/MUSE/WMDP 词表，但 **禁止**把本卡写成「OpenUnlearning 第二张表」或「又一篇 GA/NPO 加权目标综述」。

`
 隐私 / 合规近窗
 │
 ┌─────────┼──────────┬────────────┐
 │ │ │ │
 [[隐私与机器遗忘]] [[对齐脉络RLHF与偏好优化]] [[LLM水印]] [[TEE机密推理]]
 遗忘通史 对齐通史 水印 TEE 推理
 +OpenUnl. RLHF/DPO SynthID CC tax
 │ │ │ │
 └─────────┴────┬─────┴────────────┘
 │ 禁止复读
 ▼
 ★ [[Cascade与SAUL遗忘方法]] Cascade + SAUL
 可恢复性三级控制 ‖ 「忘够即可」ALM
 （GRAPHSU = 支持路径补链）
`

### 2.2 两条主轴正交（本卡骨架）

| | **Cascade** | **SAUL** |
|---|---|---|
| 核心不满 | 输出层拒答 / 降概率 ≠ 内部不可恢复（改写、线索、抽取仍漏） | 加权 forget/retain 用系数隐式规定「忘多少」→ 易过忘、伤邻域效用 |
| 形式化 | $\min_\theta I_{\mathrm{id}}(K^-\!\mid Z_\theta)$ s.t. $U(\theta)\ge\gamma$；用路径/双曲/解码 **代理** | $\min_\theta L_r(\theta)$ s.t. $L_f(\theta)\ge\alpha$（forget loss **够大**） |
| 控制旋钮 | $\lambda_{\mathrm{path}},\lambda_{\mathrm{hyp}},\lambda_{\mathrm{decode}},\alpha$ + 路由预算 $k$ | 阈值 $\alpha$、ALM $\mu/\lambda$、SAM 半径 $\rho_r,\rho_f$、双 AdamW 状态 |
| 停忘机制 | 无「自动关 forget」；靠 retain 项与三级代理平衡 | **$\lambda^+=0$ 时 forget 更新整支关掉**（「忘够即可」） |
| 主评测场 | TOFU Forget10（+01/05）；MUSE-News；WMDP-Cyber | TOFU 1%/5%/10%；WMDP-Bio/Cyber；MUSE Books（News 附录） |

---

## 三、Cascade：层级可恢复性控制

### 3.1 问题重述（§3.1）

文内把失败模式钉成 **internal identifiability**：目标知识在中间状态上仍可被 **激活（路径）、分离（表征几何）、解码（输出分布）**。理想目标（文 Eq.2）：

$$
\min_\theta I_{\mathrm{id}}(K^-\mid Z_\theta)\quad\text{s.t.}\quad U(\theta)\ge\gamma.
$$

因真实恢复函数族 $\mathcal{A}$ 未知，改用可观测代理（Eq.3）：

$$
I_{\mathrm{id}}^{\mathrm{sur}}=\lambda_{\mathrm{path}}L_{\mathrm{path}}+\lambda_{\mathrm{hyp}}L_{\mathrm{hyp}}+\lambda_{\mathrm{decode}}L_{\mathrm{decode}}.
$$

### 3.2 三级控制（§3.2）

**① 路径级路由（Path-level）**
- 对候选模块比较 forget vs retain 激活范数，得路线分 $s_i=a_i^--a_i^+$；EMA 平滑后 **Top-$k$** 选隐私相关路由集 $R$。
- 惩罚 forget 相对 retain 的过量激活（文式 softplus 边距形式；stop-gradient 挡住 retain 侧被拖垮）。
- 设计意图：**选择性**压隐私路由，而非全局掐激活。

**② 表征级双曲压缩（Representation-level）**
- 在选中路由与答案 token 位上 mean-pool → 固定投影头映入 **Poincaré ball**；半径 $r_c$ 作「分辨力 / 可分性」代理。
- $L_{\mathrm{hyp}}=\mathbb{E}_{x^-}\,\mathrm{softplus}(r_c(\tilde z_\theta^-)-\tau_h)$：把 forget 表征压向低半径区；**不对 retain 做同款收缩**（retain 靠 $L_{\mathrm{retain}}$）。

**③ 解码级干预（Decoding-level）**
- 抬高 forget 目标 NLL，并以 retain NLL 为参照边距：
 $L_{\mathrm{decode}}=-\ell^-+\mathrm{softplus}\big(m_d-(\ell^--\mathrm{sg}(\ell^+))\big)$。
- 消融（Table 2）：**去掉 Decoding** 后 Forget ROUGE 回升到 **0.8297**、Ext. **0.7761**，CFI/BUS 崩到 **0.1458 / 0.2388**——文内据此强调「路径+表征削弱后，残差仍可能在解码冒头」。

**总目标（Eq.16）：** $L_{\mathrm{Cascade}}=I_{\mathrm{id}}^{\mathrm{sur}}+\alpha L_{\mathrm{retain}}$。

### 3.3 文内评测字段（Cascade）

**协议骨架：** TOFU（主报 Forget10；附录 Forget01/05）、MUSE-News、WMDP-Cyber；骨干含 Llama-3.2-1B/3B-Instruct、Qwen3-1.7B/4B（附录 Gemma-3-4B-it）。基线含 GradAscent / GradDiff / NPO / SimNPO / PDU / RMU / UNDIAL / AltPO / WAGLE 等（同数据划分与评测管线）。

**聚合指标（附录 C.2）：**
- **CFI** $=\mathrm{HM}(1-\mathrm{FP},\,1-\mathrm{FR},\,\mathrm{TR})$（Truth Ratio 方向已校正，越高越好）
- **BUS** $=\dfrac{2\cdot\mathrm{CFI}\cdot\mathrm{Utility}}{\mathrm{CFI}+\mathrm{Utility}}$（调和，惩罚「只忘不保用」或「只用忘不掉」）

**Table 1（TOFU Forget10，摘主表）：**

| 骨干 | 方法 | Forget Prob↓ | Forget ROUGE↓ | Ext. Strength↓ | Utility↑ | CFI↑ | BUS↑ |
|---|---|---:|---:|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct | Original | 0.9510 | 0.9262 | 0.8904 | 0.6661 | 0.0832 | 0.1479 |
| | Retrained | 0.1241 | 0.3860 | 0.0648 | 0.6498 | 0.6938 | 0.6711 |
| | AltPO | 0.0948 | 0.3618 | 0.0587 | 0.6206 | 0.7114 | **0.6629** |
| | **Cascade** | 0.1633 | **0.0180** | 0.1775 | 0.6145 | **0.7165** | 0.6616 |
| Qwen3-4B | Original | 0.9659 | 0.9596 | 0.8327 | 0.4093 | 0.0534 | 0.0945 |
| | RMU | 0.1417 | 0.3069 | 0.0659 | 0.4098 | 0.7171 | 0.5216 |
| | **Cascade** | 0.0594 | 0.0492 | 0.4718 | 0.4021 | **0.7481** | **0.5231** |

读表要点（文内表述，非外推）：Llama 上 Cascade **CFI 最高**、BUS **次高**（AltPO BUS 略高）；Qwen 上 Cascade **CFI 与 BUS 均最高**。优势不在单指标「压到零」，而在 **遗忘—保留平衡**。

**MUSE-News / WMDP（文内）：**
- MUSE-News：Cascade 报 **最低 Forget Verbatim 0.266**、**Extraction Strength 0.071**（完整表见附录 Table 6）。
- WMDP-Cyber（Table 7）：Original **40.36** → Cascade **23.60**；MMLU **63.75**（Original **62.21**）。对照 PDU 可到更低 WMDP（**23.45**）但 MMLU 掉到 **26.89**——文强调 Cascade 的安全知识下降 **不是**靠通用能力塌缩。

**提示鲁棒（Fig.5 / 文内）：** 五类改写（Original / Paraphrase / Indirect / Clue / Extraction）上 Cascade 平均 ASR **0.10%**、R-ROUGE **0.043**；抽取提示下 **0.25% / 0.070**。Targeted-IDK-SFT 可压 ROUGE，但 Forget Prob / Ext. 仍高（Table 9），说明 **拒答表面 ≠ 内部擦除**。

**机制（§4.4）：** Top-$K$ 隐私路由跨采样稳定；forget–retain 激活差下降；forget 表征双曲半径分布内移，并与答案恢复关联减弱（Fig.6–7；细节读图标「待核实读图」若未抽到精确分位）。

---

## 四、SAUL：锐度感知增广拉格朗日遗忘

### 4.1 约束问题（§3）

相对「$\lambda_f L_f+\lambda_r L_r$」标量加权，SAUL 写（Eq.1）：

$$
\min_\theta L_r(\theta)\quad\text{s.t.}\quad L_f(\theta)\ge\alpha.
$$

$\alpha$ 是 **用户指定的 forget-side 满足水平**（交叉熵损失够大 = 忘得够）；retain 目标阻止 **超过必要** 的效用损伤。文内原则句：**forget enough, but no more than necessary**。

对照：Entesari et al. / Cheng et al. 等把硬约束放在 **retain 侧**，forget 目标仍持续开着；SAUL 把约束放在 **forget 侧**，满足后可关断。

### 4.2 三件套（§4）

**① ALM 控制器**
- 对偶更新 $\lambda^+=[\lambda+\mu(\alpha-L_f(\theta))]_+$（$c_f=\alpha-L_f$）。
- $\lambda^+>0$：带二次罚的 forget 压力；**$\lambda^+=0$：退化为纯 $\min L_r$**——forget 梯度门控关闭。
- 可作 **drop-in**：对既有目标 $J(\theta)$ 与遗忘度量 $F(\theta)$ 施加 $F(\theta)\ge\alpha$（§4.4）；Fig.1–2 显示多条基线 +ALM 后 GPT-based / Model Utility 改善。

**② 非对称锐度感知（SAM）**
- Retain：$\max_{\|\delta_r\|\le\rho_r}L_r(\theta+\delta_r)$（最坏情形仍低 → 平坦保留）。
- Forget：$\min_{\|\delta_f\|\le\rho_f}L_f(\theta+\delta_f)$（对「最易恢复」邻域仍保持高损失）。
- 文明确限定：此鲁棒性是 **权重空间扰动**，**不**自动蕴含提示级对抗 / 恢复攻击免疫。

**③ 双优化器状态**
- 同一 $\theta$，forget / retain 各维护 AdamW 矩（Zhong et al., 2025 思路）；先按 $\lambda^+$ 决定是否做 forget 步，再做 retain 步，降低异质梯度对共享矩的干扰。

### 4.3 文内评测字段（SAUL）

**匹配遗忘协议：** 各方法调到相近遗忘水平再比效用（避免「忘得更狠所以效用差」的假对比）。

**TOFU 1%（Table 1，匹配 $F_{\mathrm{ROUGE}}\le 0.03$ 当可能）：**

| 方法 | MU↑ | $F_{\mathrm{ROUGE}}$↓ | Retain↑ | World Facts↑ | Real Authors↑ | HM↑ | Forget↓ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Original | 0.60 | 0.87 | 90.0 | 80.3 | 81.4 | 81.9 | 82.5 |
| Dual AdamW | 0.57±0.00 | 0.02±0.00 | 64.25±0.56 | 80.00±1.43 | 49.00±1.58 | 61.87±0.87 | 0.03±0.02 |
| Dual AdamW+ALM | 0.57±0.00 | 0.01±0.00 | 63.20±0.27 | 82.56±1.43 | 54.40±1.14 | 64.76±0.68 | 0.01±0.01 |
| Sharp Min–Max+ALM | 0.58±0.01 | 0.01±0.00 | 58.05±0.37 | 80.85±0.76 | 66.20±0.84 | 67.11±0.25 | 0.03±0.03 |
| BLUR | 0.57±0.14 | **0.28±0.20**（红区） | 63.00±1.40 | 80.00±3.40 | 73.60±4.00 | 71.40±2.50 | 36.00±2.80 |
| **SAUL** | **0.59±0.01** | 0.02±0.02 | **68.25±1.09** | 79.66±1.27 | **71.40±0.55** | **72.79±0.54** | **0.01±0.01** |
| w/o ALM | 0.57±0.01 | 0.01±0.01 | 64.95±0.60 | 78.29±1.55 | 41.40±1.14 | 57.32±0.48 | 0.02±0.02 |

读表要点：在 **满足** $F_{\mathrm{ROUGE}}$ 阈值的方法里，SAUL **GPT-based HM 最高（72.79）**，相对次优约束满足法 Sharp Min–Max+ALM（67.11）约 **+5.7**；BLUR HM 高但 $F_{\mathrm{ROUGE}}=0.28$ 被标为遗忘不足，文将其视为 **未进入严格答案级遗忘工况**。消融：**去 ALM** 后 Real Authors / HM 明显掉（邻域泛化），支持「过忘伤邻居」叙事。

**改写问题（Table 2，1%，超参在原问题上选定后 **零额外调参** 迁移）：** SAUL HM **62.90±2.18**，Forget **1.50±1.37**；相对多数非 ALM 基线仍强，但 $F_{\mathrm{ROUGE}}$ 方差增大（0.13±0.22）——文称整体趋势在 5%/10% 与 3B 骨干附录中保持。

**WMDP（Table 3，Zephyr-7B-β；匹配 Bio/Cyber≈随机 0.25）：**
SAUL Bio **0.268±0.012**、Cyber **0.251±0.010**、MMLU **0.542±0.003**（≈BLUR 0.540；明显高于 Relearning-resilient 的 0.414）。

**MUSE Books（Table 4，Llama-2-7B；与 BLUR 匹配 KnowMem $D_f\approx5$）：**

| 方法 | VerbMem↓ | KnowMem $D_f$↓ | PrivLeak→0 | KnowMem $D_r$↑ |
|---|---:|---:|---:|---:|
| Original | 99.8 | 59.4 | −57.5 | 66.9 |
| Retrain | 14.3 | 28.9 | 0.0 | 74.5 |
| BLUR | 0.00±0.00 | 3.09±4.97 | −30.77±5.41 | 48.40±1.50 |
| **SAUL** | **0.00±0.00** | **0.77±1.34** | **−16.66±2.90** | 48.25±5.82 |

**局限（文 §7）：** $\alpha$ 依赖数据/模型/遗忘比例/度量，缺自动选阈；评测未覆盖全部对抗提示 / 再学习攻击的形式化保证。

---

## 五、补链 GRAPHSU：支持路径图扩展删除范围（不升主）

> 议程：**GRAPHSU / BLADE → 仅 [[Cascade与SAUL遗忘方法]] 补链或后置**。此处只立 **scope 控制** 接口，不把 GRAPHSU 写成第三条主方法全文。

**不满：** 选择性遗忘若只打 **显式 forget seed**，别名 / 改写 / 邻接训练样本仍可重建目标知识；扩太大又伤 retain。文称这是与「选哪个遗忘目标函数」正交的 **scope-control** 问题。

**做法（压缩）：**
1. 多视图支持图：实体 / 关系 / tail 符号重叠 + 句向量语义 + 答案侧梯度对齐 → 边权。
2. 自 seed 做个性化扩散（1–2 hop / PageRank 式），估支持闭包。
3. 对高风险邻居赋 **分级遗忘强度** $\omega_i$，再套局部遗忘目标（seed 全压、邻居按相关性衰减）；控制器 **loss-agnostic**，可接不同局部目标。

**文内主结果（GPT-2 Medium，Table 2；效用可行阈：retain PPL≤10）：**

| 数据集 | 设置 | Seed-Only Leak% / PPL | GRAPHSU Leak% / PPL | ∆Leak（文内） |
|---|---|---|---|---|
| TOFU | Complete | 93.25 / 2.61 | **46.83 / 3.27** | −46.42 pp |
| TOFU | Entity | 96.25 / 4.40 | **54.60 / 4.94** | −41.65 pp |
| TOFU | Partial | 100.00 / 7.90 | **81.67 / 1.91** | −18.33 pp |
| PISTOL | Complete | 56.33 / 1.09 | **6.83 / 1.05** | **−49.50 pp**（摘要「up to 49.5」） |
| PISTOL | Entity | 26.33 / 1.10 | **4.67 / 1.10** | −21.66 pp |
| PISTOL | Partial | 41.39 / 1.22 | **29.17 / 1.19** | −12.22 pp |

文强调：GRU 等可在 TOFU Complete 上拿到更低 Leak（**38.13%**），但 retain PPL **79.11**，不满足效用可行；GRAPHSU 争的是 **utility-feasible soft leakage** 最低。Llama-3.2-3B-Instruct 结果在附录；soft leakage 是固定路由探针族下的 **行为可恢复性**，非证明式擦除。

**与两主锚关系：** Cascade 管「内部三级可恢复性」；SAUL 管「忘多少的显式停条件」；GRAPHSU 管「**忘掉哪些支撑样本**」。三者可组合想象，但 **本卡不编造未做的联合实验**。

---

## 六、对照小结与可行动取舍

| 问题 | 优先看 |
|---|---|
| 表面拒答后仍被改写/抽取挖出？ | **Cascade**（路径定位 + 双曲压缩 + 解码边距；盯 CFI/BUS 与改写 ASR） |
| 加权遗忘总过打、Real Authors/邻域掉点？ | **SAUL**（设 $\alpha$，让 ALM 在满足后关 forget；可先把 ALM drop-in 到现有锐度基线） |
| 企业删除请求只有 canonical seed、担心别名/邻接泄漏？ | **GRAPHSU 补链**（先扩 support closure，再套本地目标；盯 soft leakage @ PPL≤10） |
| 需要方法族地图 / 统一元评测？ | 回 **[[隐私与机器遗忘]]**，不要在本卡重开 |

**工程提示（严格限文内已写）：**
- Cascade 对 decoding 系数过强敏感（Fig.10：过压可不稳定）——调参应联合看 BUS，而非单看 Forget ROUGE。
- SAUL 的 $\alpha$ 是产品旋钮也是负担；附录 F 提及 margin 证书式实例化，作 **事后检验** 而非本卡展开。
- GRAPHSU 图构建含 GPT-4.1 抽事实三元组 + 离线构图成本（文称按语料摊销）；部分删除（partial）残余泄漏仍高——文归因于 span 级设定本身难，而非单点实现瑕疵。

---

## 七、局限与待核实

1. **跨文数字不可横向总分：** Cascade / SAUL / GRAPHSU 骨干、匹配协议、指标定义不同（CFI·BUS vs GPT-HM vs soft leakage@PPL≤10）——**禁止**拼成「谁 SOTA」总榜。
2. **Cascade 代码仓** `github.com/Noryxen/Cascade`、**GRAPHSU 匿名仓** 仅文内声明；2026-09-22 **未**做 clone/CI 核验。
3. **SAUL** 无文内唯一公开实现 URL；复现依赖作者后续发布。
4. **攻击面：** 三文均讨论改写/抽取/路由探针，但均 **不**提供「如何绕过遗忘」操作手册；本笔记只转述其 **评测结论**。
5. **BLADE** 等近邻遗忘文按议程 **后置**，本卡不展开。

---

| 项 | 建议 |
|---|---|
| 笔记路径 | 安全与评测/Cascade与SAUL遗忘方法.md |
| PDF | 三篇均 **≪10MB** 且页数 ≤29 → **以官方 HTTPS 外链为准**至 （已落盘）；`*.txt` |
| 与 [[隐私与机器遗忘]] | 双链交叉即可；**不要**把本卡合并进 [[隐私与机器遗忘]] 通史 |
| 升主下一项 | 若遗忘轴继续加密，优先 **BLADE** 或 Cascade×SAUL **联合协议**（均未做，仅备忘） |

**摘要（≤6 句）：**
[[Cascade与SAUL遗忘方法]] 在 [[隐私与机器遗忘]] 通史/OpenUnlearning 之外，深读 2026 近窗两篇遗忘方法：Cascade（2609.16890）以路径—双曲—解码三级代理最小化内部可辨识性，TOFU Forget10 上 Llama-3.2-3B 达 CFI 0.7165 / BUS 0.6616，并保持改写下低 ASR；SAUL（2608.16249）以 forget-loss 约束 + ALM 在满足 $\alpha$ 后关闭 forget 更新，配合非对称 SAM 与双优化器，TOFU 1% 匹配遗忘下 GPT-HM 72.79。补链 GRAPHSU（2608.26743）用支持路径图扩展删除 scope，PISTOL Complete 上 soft leakage 相对 Seed-Only 降约 49.5 pp（PPL 仍 ≤10）。三 PDF 均 <1.5MiB，以官方 HTTPS 外链为准；本卡禁止写成 OpenUnlearning 复读。
