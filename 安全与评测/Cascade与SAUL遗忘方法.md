---
title: "遗忘方法增量：Cascade + SAUL"
topic: Cascade与SAUL遗忘方法
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.16890
 - https://arxiv.org/abs/2608.16249
 - https://arxiv.org/abs/2608.26743
aux:
 - https://arxiv.org/abs/2609.16890
 - https://arxiv.org/abs/2608.16249
 - https://arxiv.org/abs/2608.26743
 - https://github.com/Noryxen/Cascade
 - https://anonymous.4open.science/r/graphSU-35B4
arxiv: ["2609.16890", "2608.16249", "2608.26743"]
related: ["隐私与机器遗忘"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 遗忘方法增量：Cascade + SAUL

> **主要来源**：[Cascade: Hierarchical Recoverability Control for Large Language Model Unlearning](https://arxiv.org/abs/2609.16890)；[SAUL: Sharpness-Aware Augmented-Lagrangian Unlearning](https://arxiv.org/abs/2608.16249)；[Graph-Guided Selective Unlearning for Language Models: Controlling Support Routes Beyond Forget Seeds](https://arxiv.org/abs/2608.26743)（截至 2026-09-22）。下文「Cascade §x」「SAUL §x」「GRAPHSU」分别指三文。
> **研究线**：方法接口与遗忘—效用权衡（主）；文内 TOFU / MUSE / WMDP（及 GRAPHSU 的 PISTOL）评测字段（辅）。
> **范围与相邻笔记**：
> - ≠ [[隐私与机器遗忘]]：本篇不写 180+ 篇方法通史、流水线阶段地图与 OpenUnlearning 的指标元评测，只把 TOFU / MUSE / WMDP 当评测协议入口。
> - 三文都讨论改写、提取与路由探针，本篇只转述评测结论，不写绕过遗忘的操作步骤。
> **意义**：两篇 2026 年的方法从正交方向修改遗忘—效用接口：Cascade 指出「输出层降概率不等于内部不可恢复」，用路径、表征、解码三级一起压低可恢复性；SAUL 把「忘多少」写成显式约束，忘够即停，减少过忘对邻域知识的伤害。GRAPHSU 补上第三个问题：只删 forget seed 不够，还要控制支撑它的样本。

## 一、问题背景

机器遗忘要在不重训全量的前提下，去掉 forget 集对模型的影响，同时保住 retain 集与通用能力；理想对照是只在 retain 集上重训的模型，但对 LLM 来说这通常不可行（见 [[隐私与机器遗忘]]）。常见基线（GradAscent、GradDiff、NPO、SimNPO 等）多在 forget 集上施加遗忘损失，再与 retain 项加权，防止效用塌缩。

三文各自指出这一范式的一个缺口：

- **Cascade §3.1**：输出层的拒答或降概率不等于内部不可恢复，改写、线索或提取提示仍能把知识挖出来。
- **SAUL §3**：forget / retain 加权目标用系数隐式规定「忘多少」，容易过忘，伤及邻域知识。
- **GRAPHSU**：只打显式 forget seed，别名、改写与邻接训练样本仍能重建目标知识；而删除范围扩得太大又伤 retain。

## 二、脉络

[[隐私与机器遗忘]] 记录了这一方向的地图与量尺：综述梳理自 2021 年起的 180+ 篇工作，OpenUnlearning（NeurIPS 2025）把 TOFU、MUSE、WMDP 三个主基准与多种算法、指标放进统一库，并指出评测难在「表面拒答不等于权重真被擦掉」。

本篇三文都出自 2026 年 8–9 月，沿用同一套基准，但不再比较「哪种加权目标更好」，而是改动遗忘问题的形式：

| 方法 | 日期（页眉） | 改动什么 |
|---|---|---|
| SAUL | 2026-08-17 | 优化形式：从加权和改为带阈值的约束优化 |
| GRAPHSU | 2026-08-27 | 删除范围：从 forget seed 扩到支撑路径 |
| Cascade | 2026-09-15 | 遗忘目标：从输出概率改为内部可辨识性 |

## 三、两条主线对照

| | Cascade | SAUL |
|---|---|---|
| 核心不满 | 输出层拒答或降概率不等于内部不可恢复 | 加权目标隐式规定「忘多少」，易过忘、伤邻域效用 |
| 形式化 | $\min_\theta I_{\mathrm{id}}(K^-\!\mid Z_\theta)$ s.t. $U(\theta)\ge\gamma$，用路径、双曲、解码三项代理 | $\min_\theta L_r(\theta)$ s.t. $L_f(\theta)\ge\alpha$（forget 损失足够大） |
| 停忘机制 | 没有自动关闭 forget 的机制，靠 retain 项与三级代理平衡 | 对偶变量为 0 时整支 forget 更新关闭 |
| 主评测场 | TOFU Forget10（附 01/05）；MUSE-News；WMDP-Cyber | TOFU 1%/5%/10%；WMDP-Bio/Cyber；MUSE Books |

## 四、Cascade：层级可恢复性控制

### 4.1 思想

Cascade 把失败模式命名为**内部可辨识性**：目标知识在中间状态上仍能被激活（路径）、被分离（表征几何）、被解码（输出分布）。理想目标是在效用不低于 $\gamma$ 的约束下最小化可辨识性 $I_{\mathrm{id}}$；由于真实的恢复攻击族未知，改用三项可观测代理的加权和（Cascade §3.1）：

$$
I_{\mathrm{id}}^{\mathrm{sur}}=\lambda_{\mathrm{path}}L_{\mathrm{path}}+\lambda_{\mathrm{hyp}}L_{\mathrm{hyp}}+\lambda_{\mathrm{decode}}L_{\mathrm{decode}},
$$

总目标再加上 retain 项：$L_{\mathrm{Cascade}}=I_{\mathrm{id}}^{\mathrm{sur}}+\alpha L_{\mathrm{retain}}$。

### 4.2 三级控制

- **路径级**：比较各候选模块在 forget 与 retain 数据上的激活范数，EMA 平滑后取 Top-$k$ 作为「隐私路由」，只惩罚这些路由上 forget 相对 retain 的过量激活。用意是有选择地压隐私路由，而不是全局掐激活。
- **表征级**：把选中路由上答案位置的表征投影进双曲空间（Poincaré ball），以半径作为「可分性」的代理，把 forget 表征压向低半径区；retain 不做同样收缩。
- **解码级**：抬高 forget 目标的 NLL，并以 retain 的 NLL 为参照边距。消融显示去掉这一级后 Forget ROUGE 回升到 0.8297，CFI / BUS 跌到 0.1458 / 0.2388（Cascade Table 2）：路径与表征被削弱后，残余知识仍可能在解码端冒头。

### 4.3 证据

文内定义两个聚合指标：CFI 为 $1-$Forget Prob、$1-$Forget ROUGE 与 Truth Ratio 的调和平均；BUS 为 CFI 与 Utility 的调和平均，惩罚「只忘不保用」或「保用但忘不掉」。TOFU Forget10 主表摘录（Cascade Table 1）：

| 骨干 | 方法 | Forget ROUGE↓ | Utility↑ | CFI↑ | BUS↑ |
|---|---|---:|---:|---:|---:|
| Llama-3.2-3B-Instruct | Retrained | 0.3860 | 0.6498 | 0.6938 | 0.6711 |
| | AltPO | 0.3618 | 0.6206 | 0.7114 | **0.6629** |
| | Cascade | **0.0180** | 0.6145 | **0.7165** | 0.6616 |
| Qwen3-4B | RMU | 0.3069 | 0.4098 | 0.7171 | 0.5216 |
| | Cascade | 0.0492 | 0.4021 | **0.7481** | **0.5231** |

- Llama 上 Cascade 的 CFI 最高、BUS 次高（AltPO 略高）；Qwen 上两项都最高。优势在遗忘与保留的平衡，而不是单项指标压到零。
- **WMDP-Cyber**（Cascade Table 7）：从 40.36 降到 23.60，MMLU 为 63.75（原模型 62.21）；PDU 能把 WMDP 压到 23.45，但 MMLU 跌到 26.89。Cascade 的安全知识下降不是靠通用能力塌缩换来的。
- **MUSE-News**：文内报告 Cascade 的 Forget Verbatim 最低（0.266），Extraction Strength 为 0.071（完整表见附录 Table 6）。
- **提示鲁棒**（Cascade Fig.5）：五类改写提示上平均 ASR 0.10%、R-ROUGE 0.043，提取提示下为 0.25% / 0.070。对照的 Targeted-IDK-SFT 能压低 ROUGE，但 Forget Prob 与提取强度仍高（Table 9），说明表面拒答不等于内部擦除。

## 五、SAUL：锐度感知增广拉格朗日遗忘

### 5.1 思想

SAUL 不再用 $\lambda_f L_f+\lambda_r L_r$ 的标量加权，而写成约束问题（SAUL §3）：

$$
\min_\theta L_r(\theta)\quad\text{s.t.}\quad L_f(\theta)\ge\alpha .
$$

$\alpha$ 是用户指定的 forget 侧满足水平（交叉熵损失足够大即算忘够），retain 目标阻止超出必要的效用损伤，原则是 *forget enough, but no more than necessary*。此前也有工作把硬约束放在 retain 侧，但 forget 目标始终开着；SAUL 把约束放在 forget 侧，满足后即可关断。

### 5.2 三个组件

- **增广拉格朗日控制器**：对偶变量按 $\lambda^+=[\lambda+\mu(\alpha-L_f(\theta))]_+$ 更新。$\lambda^+>0$ 时施加带二次罚的 forget 压力；$\lambda^+=0$ 时退化为只最小化 $L_r$，forget 梯度被门控关闭。它也可以作为插件，给已有方法加上 $F(\theta)\ge\alpha$ 约束（SAUL §4.4）。
- **非对称锐度感知**：retain 侧在权重邻域的最坏情形下仍保持低损失（平坦保留），forget 侧在「最易恢复」的邻域里仍保持高损失。作者明确这只是权重空间扰动下的鲁棒性，不等于对提示级攻击或再学习攻击免疫。
- **双优化器状态**：同一组参数为 forget 与 retain 分别维护 AdamW 矩，先按 $\lambda^+$ 决定是否做 forget 步，再做 retain 步，减少两类异质梯度对共享矩的干扰。

### 5.3 证据

比较采用**匹配遗忘协议**：各方法先调到相近的遗忘水平再比效用，避免「忘得更狠所以效用更差」的假对比。TOFU 1% 摘录（SAUL Table 1，尽量匹配 $F_{\mathrm{ROUGE}}\le 0.03$）：

| 方法 | $F_{\mathrm{ROUGE}}$↓ | Real Authors↑ | HM↑ |
|---|---:|---:|---:|
| Sharp Min–Max+ALM | 0.01±0.00 | 66.20±0.84 | 67.11±0.25 |
| BLUR | 0.28±0.20 | 73.60±4.00 | 71.40±2.50 |
| SAUL | 0.02±0.02 | 71.40±0.55 | **72.79±0.54** |
| SAUL w/o ALM | 0.01±0.01 | 41.40±1.14 | 57.32±0.48 |

- 在满足 $F_{\mathrm{ROUGE}}$ 阈值的方法里，SAUL 的 GPT-based HM 最高（72.79），比次优的 Sharp Min–Max+ALM（67.11）高约 5.7；BLUR 的 HM 虽高，但 $F_{\mathrm{ROUGE}}=0.28$ 被视为遗忘不足。去掉 ALM 后 Real Authors 与 HM 明显下降，支持「过忘伤邻居」的判断。
- **改写问题**（Table 2，零额外调参迁移）：HM 62.90±2.18，Forget 1.50±1.37，但 $F_{\mathrm{ROUGE}}$ 方差变大（0.13±0.22）。
- **WMDP**（Table 3，Zephyr-7B-β）：Bio 0.268±0.012、Cyber 0.251±0.010，接近随机的 0.25；MMLU 0.542±0.003，与 BLUR（0.540）相当，明显高于 Relearning-resilient（0.414）。
- **MUSE Books**（Table 4，Llama-2-7B）：VerbMem 0.00±0.00，KnowMem $D_f$ 0.77±1.34，PrivLeak −16.66±2.90（BLUR 为 −30.77±5.41），KnowMem $D_r$ 48.25±5.82。

## 六、GRAPHSU：用支持路径图扩展删除范围

GRAPHSU 把「删哪些样本」当作与「用什么遗忘目标」正交的 scope 控制问题，这里只作补充索引：

1. 用实体、关系与符号重叠、句向量语义和答案侧梯度对齐，构建多视图支持图；
2. 从 forget seed 出发做个性化扩散（1–2 跳，PageRank 式），估计支持闭包；
3. 给高风险邻居分配分级遗忘强度，seed 全压、邻居按相关性衰减；控制器与具体的局部遗忘目标无关。

在 GPT-2 Medium、retain PPL ≤ 10 的效用可行条件下（GRAPHSU Table 2），TOFU Complete 的 soft leakage 从 Seed-Only 的 93.25% 降到 46.83%，PISTOL Complete 从 56.33% 降到 6.83%（−49.50 pp）。GRU 在 TOFU Complete 上 Leak 更低（38.13%），但 retain PPL 为 79.11，不满足效用约束。soft leakage 是固定探针族下的行为可恢复性，不是证明式擦除。

三者的分工：Cascade 管内部三级可恢复性，SAUL 管「忘多少」的显式停止条件，GRAPHSU 管「忘掉哪些支撑样本」。可以设想组合使用，但文内没有联合实验。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[隐私与机器遗忘]] | 共用背景：机器遗忘的设定、TOFU / MUSE / WMDP 基准与「表面拒答不等于擦除」的评测难点；本篇是其后的方法增量 | 方法族通史、OpenUnlearning 元评测 |

## 八、意义

| 问题 | 优先看 |
|---|---|
| 表面拒答后仍能被改写或提取挖出 | Cascade：路径定位、双曲压缩与解码边距，关注 CFI / BUS 与改写 ASR |
| 加权遗忘过打，邻域知识（如 Real Authors）掉点 | SAUL：设定 $\alpha$，让 ALM 在满足后关闭 forget；可先把 ALM 插到现有方法上 |
| 删除请求只有 canonical seed，担心别名与邻接泄漏 | GRAPHSU：先扩支持闭包，再套局部目标，关注 PPL ≤ 10 下的 soft leakage |
| 需要方法族地图或统一元评测 | [[隐私与机器遗忘]] |

## 九、局限与待核实

1. **跨文数字不可横向比较**：三文的骨干、匹配协议与指标定义不同（CFI 与 BUS、GPT-based HM、PPL ≤ 10 下的 soft leakage），不宜拼成一张「谁 SOTA」的总榜。
2. **调参敏感**：Cascade 对解码项系数过强敏感（Fig.10，过压可能不稳定），调参应联合看 BUS 而不是只看 Forget ROUGE。SAUL 的 $\alpha$ 依赖数据、模型、遗忘比例与度量，缺少自动选阈方法（SAUL §7）。
3. **鲁棒性的边界**：SAUL 的评测没有覆盖全部对抗提示，也没有针对再学习攻击的形式化保证；GRAPHSU 的 soft leakage 只是行为可恢复性；部分删除（partial）设定下残余泄漏仍高，文中归因于 span 级设定本身难。
4. **成本**：GRAPHSU 的图构建要用 GPT-4.1 提取事实三元组并离线构图，文称成本可按语料摊销。
5. **代码可用性**：Cascade 仓库（Noryxen/Cascade）与 GRAPHSU 匿名仓库只在文内声明，可用性未核验；SAUL 文内没有给公开实现链接。
6. **读图项**：Cascade 机制分析（§4.4，Fig.6–7）中隐私路由稳定性与双曲半径内移的精确分位未从图中读出，待核实读图。

## 十、延伸阅读

| 类型 | 标题 | 说明 | URL |
|---|---|---|---|
| 论文 | Cascade: Hierarchical Recoverability Control for Large Language Model Unlearning | Yu 等，2026-09；三级可恢复性控制 | https://arxiv.org/abs/2609.16890 |
| 论文 | SAUL: Sharpness-Aware Augmented-Lagrangian Unlearning | Choi、Yang、Park，2026-08；显式 forget 约束与 ALM | https://arxiv.org/abs/2608.16249 |
| 论文 | Graph-Guided Selective Unlearning for Language Models | Khan 等，2026-08；支持路径图扩展删除范围 | https://arxiv.org/abs/2608.26743 |
