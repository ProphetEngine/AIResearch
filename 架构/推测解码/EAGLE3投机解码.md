---
title: "EAGLE-3 投机解码增量切片（相对 B7，6）"
topic: EAGLE3投机解码
date: 2026-09-22
lines: [AI Infra, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2503.01840
 - https://github.com/SafeAILab/EAGLE
 - https://papers.nips.cc/paper_files/paper/2025/file/c7b5a35ea98b62512a869c19ea7b03cb-Paper-Conference.pdf
arxiv: ["2503.01840"]
related: ["B7", "AI基础设施总览", "投机解码发展时间线"]
archived: 2026-09-22
---

# EAGLE-3 投机解码增量切片（相对 B7）

> **定位**：EAGLE-3 投机解码 P1 Infra 切片——在 **B7** 已立的投机解码**基线**（Leviathan / Chen / Medusa / Lookahead 与引擎选型轴）之上，只补 **EAGLE-3** 相对 **EAGLE / EAGLE-2** 的可核对增量。
> **攻坚线**：**AI Infra（主）** + **数学原理（接受长度 / 推测接受率，辅）**。
> **硬划界（禁止重写）**：
> - **禁止重写 B7** 投机解码通史与 Leviathan / Chen / Medusa / Lookahead 正文（→ [[推理引擎生态]]）；本篇不复述「草稿—校验」框架证明。
> - **禁止重写** [[AI基础设施总览]] / B7 的 PagedAttention、Radix、PD 分离全文；SGLang 只写论文给出的 **EAGLE-3 吞吐表**，不重写引擎架构。
> - **禁止**把 Table 1 中 Medusa / Lookahead / Hydra 等对照列展开成谱系课（数字仅作「相对 EAGLE-2」旁证时点到）。
> **禁止编造**：倍率、τ、吞吐、批次、数据倍数一律锚定官方 PDF（2026-09-22 CST）；层号若正文未写具体层索引则标「未公开具体层下标」。

---

## 一、材料元信息

| 字段 | 核实值（PDF / / arXiv API） |
|---|---|
| 标题 | *EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test* |
| 作者 | Yuhui Li, Fangyun Wei, Chao Zhang, Hongyang Zhang（Peking University / Microsoft Research / University of Waterloo / Vector Institute） |
| arXiv | **2503.01840v3** \[cs.CL\]（published **2025-03-03**；updated **2025-04-23**） |
| 官方 PDF | `https://arxiv.org/abs/2503.01840`（**12** 页 A4；CreationDate **2025-04-24** CST；946,062 bytes） |
| 可选镜像 | NeurIPS 2025 Conference PDF（`curl -I` → **200**；`Content-Disposition: …eagle-3-…-Paper-Conference.pdf`） |
| 代码 | https://github.com/SafeAILab/EAGLE（摘要末句） |
| 相对 B7 | B7「待核实」明示：EAGLE / EAGLE-2 须单独 PDF 后再补 → **本篇即该增量** |

**一句话抓手：** EAGLE 系在特征层做草稿；扩数据却几乎不涨速。EAGLE-3 用 **training-time test** 去掉特征回归约束、改直接预测 token，并把目标模型 **低/中/高层特征融合** 喂给草稿头——从而出现「数据↑ → 加速比↑」的 scaling 曲线（Figure 1），相对 EAGLE-2 约 **1.4×** 延迟加速，并在 **SGLang** 大 batch 仍给出正吞吐增益。

---

## 二、相对 B7 / EAGLE-2 的增量立轴（不展开通史）

| 已覆盖（B7） | 本篇只补 |
|---|---|
| 投机采样「草稿—并行校验、同分布」思想；Medusa / Lookahead 等入口 PDF | **不**重写；Table 1 有对照列时只录 EAGLE-2 vs EAGLE-3 |
| 引擎选型：vLLM / SGLang / TRT-LLM；投机为 decode 轴因子 | **SGLang 集成表**（§4.3 Table 3–4）；vLLM Table 5 仅作附录交叉一句 |
| 「勿编造未归档 EAGLE 倍率」 | 本 PDF 已落盘 → 倍率全部出摘要 / Table 1–4 |

**EAGLE → EAGLE-2 → EAGLE-3（论文自述，一句链）：**

- **EAGLE**：复用目标模型 **顶层特征**（LM head 前），在特征空间自回归，再用目标 LM head 出草稿 token；树状草稿 + tree attention 校验（§2.2；细节不展开）。
- **EAGLE-2**：在 EAGLE 上加 **上下文感知动态草稿树**（用草稿置信度近似接受率并剪枝）；EAGLE-3 **兼容并沿用**该树技术（§2.2 末、贡献列表）。
- **EAGLE-3 两刀**：① 去掉特征预测损失 $l_{\mathrm{fea}}$，训练期模拟多步生成（**training-time test**）；② 输入改为 **低/中/高** 层融合特征 $g$，不再锁死顶层 $f$（摘要 + §3）。

---

## 三、Training-time test（训练期「测」多步）

### 3.1 问题：为何扩数据救不了原 EAGLE

摘要 / §1 观察：把训练数据相对 ShareGPT 放大，**EAGLE 加速比与接受长度几乎不涨**（Figure 1 平线）；EAGLE-3 才出现上升曲线。

论文归因（§1 + Figure 3 上/中）：

1. EAGLE 损失含 **特征预测** $l_{\mathrm{fea}}$ + **token 预测** $l_{\mathrm{token}}$；特征拟合是额外约束，限制草稿模型表达力，难吃数据。
2. 仅去掉特征约束、仍用「真特征序列训练、推时塞入自预测特征」：第一步接受率 $0\textrm{-}\alpha$ 会升，但 Step 1 输出 $\hat a_{t+1}$ 远离真特征 $f_{t+1}$，Step 2 输入分布偏移 → $1\textrm{-}\alpha$ 崩（Figure 4）。

### 3.2 做法：训练时把「测试步」嵌进去

**Training-time test**（Figure 3 底 + §3.2）：训练中执行测试步——草稿头产出无约束向量 $a$，再 **反馈** 进草稿模型继续训，使训练分布覆盖推理时「前缀真特征 + 后续自预测 $a$」的混合输入。

跟读口径（中文）：

`
目标前向 → 得到可用的融合特征 g（或训练数据位置上的真特征）
 ↓
草稿 decoder 一步 → 输出 a，LM head → 草稿 token
 ↓
下一步把 a（而非尚未校验的真 g）拼上 token embedding 再喂草稿
 ↓
训练 loss 只盯 token 侧（去掉 l_fea），多步模拟与推理对齐
`

**注意力掩码**（Figure 6）：原生一步用标准下三角；模拟第二/三步时，草稿自预测 token 与训练数据 token 的依赖呈树状，掩码改成「对角 + 指向原始训练 key」的稀疏模式；论文建议对应对位置用向量点积算注意力，避免稠密 matmul 浪费（§3.2）。

**与 HASS 划界（论文原话动机不同，§3.2）：** HASS 仍做特征预测、保留 $l_{\mathrm{fea}}$、输入仍须顶层特征，动机是缓解特征误差累积；EAGLE-3 动机是 **去掉不必要约束以提升表达力**，输出不必拟合顶层特征。本篇不展开 HASS 算法细节。

### 3.3 接受率证据（相对「训练–推理不一致」）

Figure 7（MT-bench，LLaMA-Instruct 3.1 8B）：$n\textrm{-}\alpha$ = 输入含 $n$ 个自估计特征/向量、且此前草稿均被目标接受时的接受率。EAGLE 随 $n$ 上升接受率显著下降；**EAGLE-3 几乎不掉**——论文将其归为 training-time test 有效（§4.1）。

---

## 四、多层特征融合（low / mid / high → $g$）

### 4.1 为何不能只啃顶层

§1：全秩 LM head 下，顶层特征与「下一 token logits」一一对应；**仅凭顶层去预测「下下个」token** 信息不足。去掉 $l_{\mathrm{fea}}$ 后，才允许改用中间层特征（不再强迫输出靠近顶层 $f$）。

### 4.2 推理管线中的融合（§3.1 / Figure 5）

在 prefill 或上一轮校验的目标模型前向中，记录 **低 / 中 / 高** 层特征序列 $l,m,h$（各为 $k$ 维，$k=$ 目标 hidden size）：

1. $\mathrm{concat}(l,m,h)\in\mathbb{R}^{3k}$
2. **FC** 压回 $k$ 维 → 融合特征 $g$
3. 将 $g$ 与已采样 token 的 embedding $e$ 再经 FC 压到 $k$，送入 **单层** Transformer decoder（草稿核心），输出 $a$
4. $a$ 过 **目标 LM head** 采样得到草稿 token

多步时：尚未被目标校验的位置 **没有** 真 $g$，用上一步草稿输出 $a$ 顶替，再与新 token embedding 拼接（与 training-time test 一致）。

**未公开：** 正文写 low/middle/high，**未**给出具体层下标（如第几层）——笔记不编造层号。

### 4.3 消融：两刀都必要（Table 2）

目标：LLaMA-Instruct 3.1 8B；相对 EAGLE-2 逐步加件：

| Method | MT-bench Speedup / τ | GSM8K Speedup / τ |
|---|---|---|
| EAGLE-2 | 3.16× / 4.05 | 3.39× / 4.24 |
| \+ remove fea con（去特征约束） | 3.82× / 5.37 | 3.77× / 5.22 |
| \+ fused features（ours） | **4.40× / 6.13** | **4.48× / 6.23** |

论文结论：去约束与融合特征 **各自** 抬升接受长度与加速比（§4.2）。

---

## 五、相对 EAGLE-2 的加速轴（论文数字）

### 5.1 摘要级主张（照录）

- 加速比最高约 **6.5×**（相对 vanilla 自回归）。
- 相对 EAGLE-2 约 **1.4×** 改进（摘要；贡献条另写：约 **8×** 于 EAGLE 的训练数据下，batch size 1 延迟 **1.4×** over EAGLE-2）。
- §4.1：约 **3.0×–6.5×** vs vanilla；相对 EAGLE-2 约 **20%–40%** 提升。

### 5.2 Table 1 精读：EAGLE-2 vs EAGLE-3（Temperature=0，Mean 列）

| Target | EAGLE-2 Mean Speedup / τ | EAGLE-3 Mean Speedup / τ |
|---|---|---|
| Vicuna 13B | 4.22× / 4.83 | **5.51× / 6.62** |
| LLaMA-Instruct 3.1 8B | 3.23× / 4.11 | **4.44× / 6.23** |
| LLaMA-Instruct 3.3 70B | 2.85× / 3.78 | **4.12× / 5.88** |
| DeepSeek-R1-Distill-LLaMA 8B | 3.26× / 3.92 | **4.16× / 5.84** |

单点峰值（正文）：HumanEval 上 EAGLE-3 可达约 **6.5×**、平均接受长度最高约 **7.5**（§4.1；Vicuna 13B HumanEval 行：6.47× / 7.54）。DSL 8B 在 GSM8K 最高加速——论文归因草稿还用了 **OpenThoughts-114k-math**（§4.1）。

**指标定义（§ Metrics，无损前提）：** 不改目标权重；严格投机接受条件 → **不评生成质量**。汇报：

- **Speedup**：相对 vanilla AR 实测加速比
- **τ**：每轮草稿–校验平均接受 token 数
- **$n\textrm{-}\alpha$**：链状草稿下的接受率（测接受率时不用树）

Temperature=1 时 Table 1 仍给 EAGLE-2/3；对 Medusa 等「放宽接受、不保证无损」的方法，论文声明 **不与 EAGLE-3 比 temperature=1**（Table 1 题注）——本篇不展开那些方法。

### 5.3 数据 scaling（Figure 1）

横轴：相对 ShareGPT 的数据倍数（1 / 2 / 4 / 8）。EAGLE-2：加速与接受长度近乎平台；EAGLE-3：随数据上升。训练数据：ShareGPT + UltraChat-200K（约 68K / 464K 条）；响应用 **目标模型生成** 而非固定语料（Implementation）。GPU 约束下未测 405B / 671B（§4 Models）。

---

## 六、SGLang 集成叙述（生产框架吞吐）

> 本节只录论文 §4.3 与 Acknowledgement；**不**重写 SGLang Radix/FSM（→ B7）。

### 6.1 设定与声明

- 环境：**SGLang v0.4.4**；单卡 **H100**；目标 **LLaMA-Instruct 3.1 8B**；数据集 **MT-Bench**。
- 实验由 **SGLang 团队**完成（Acknowledgement：James Liu, Ke Bao, Yineng Zhang, Lianmin Zheng, Ying Sheng 等合并与评测）。
- **本部分未用树结构**；**链长设为 3**（§4.3）。基线：SGLang **无**投机 = 1.00×。

### 6.2 大 batch 吞吐（Table 3）

| Batch size | 2 | 4 | 8 | 16 | 24 | 32 | 48 | 56 | 64 |
|---|---|---|---|---|---|---|---|---|---|
| EAGLE | 1.40× | 1.38× | 1.23× | 1.02× | 0.93× | 0.94× | 0.88× | 0.99× | 0.99× |
| **EAGLE-3** | **1.81×** | **1.82×** | **1.62×** | **1.48×** | **1.39×** | **1.32×** | **1.38×** | **1.34×** | **1.38×** |

摘要 / §4.3：EAGLE 在 bs≈24 已损吞吐；**EAGLE-3 在 bs=64 仍约 1.38×（+38%）**。叙事抓手：投机常被质疑「大 batch 没用甚至负优化」——在高度优化的 SGLang 上，EAGLE-3 仍给出正增益（§4.3 开篇讨论访存墙 vs 算力冗余随 batch 变小）。

### 6.3 Batch size = 1 吞吐（Table 4，同 H100 / MT-bench）

| Method | Throughput (bs=1) |
|---|---|
| SGLang（无投机，1×H100） | 158.34 tokens/s |
| SGLang + EAGLE-2 | 244.10 tokens/s |
| SGLang + EAGLE-3 | **373.25 tokens/s** |

相对无投机：373.25 / 158.34 ≈ **2.36×**（算术核对，论文未单列该比值）；相对 EAGLE-2：373.25 / 244.10 ≈ **1.53×**（同，仅供跟读）。

### 6.4 与 vLLM 表的交叉（非本篇主轴）

§4.4 Table 5 另给 vLLM 大 batch 对照（链长最大 2、无树、MT-Bench）。正文写结果在 **RTX3090**，表题写 **A100**——**论文内部硬件表述不一致，照录不调和**；详细数字不占本篇主表。选型含义仍落在 B7：「投机因子 × 引擎实现」需版本锁定后再比。

---

## 七、跟读清单（可复述）

1. **EAGLE 扩数据不涨速** ← 特征预测约束 + 多步分布偏移。
2. **Training-time test** ← 训练时把自预测 $a$ 喂回，对齐推理；去 $l_{\mathrm{fea}}$。
3. **多层融合** ← $\mathrm{FC}(\mathrm{concat}(l,m,h))\to g$，再单层 decoder 出 $a$。
4. **相对 EAGLE-2** ← Table 1 Mean 全面更高；摘要约 1.4×；HumanEval 峰值 ~6.5×。
5. **SGLang** ← 团队实测；bs=64 仍 1.38×；bs=1 上 373 tokens/s vs EAGLE-2 的 244。

---

## 八、待核实 / 不写

- 低/中/高层的 **具体层索引**与 FC 初始化：PDF 未给 → 读代码仓库再补。
- EAGLE-3 在 TRT-LLM / 更新版 vLLM 默认图与接受率曲线：超出本 PDF 主表。
- 405B / 671B：作者声明未测。
- NeurIPS 相机就绪与 arXiv v3 是否逐字同文：镜像已 200，本笔记数字以落盘 arXiv PDF 为准。

---

## 九、一句话收束

相对 B7 的投机**基线**，EAGLE-3 的可研增量不在「再讲一遍草稿校验」，而在：**用 training-time test 拆掉特征回归枷锁，用低/中/高融合特征抬草稿表达力，让加速比重新吃上数据 scaling，并在 SGLang 大 batch 上交出仍为正的吞吐表**。

---

*笔记状态：draft · 攻坚线 AI Infra · 相对 B7 增量切片 · PDF 已归档 2026-09-22 CST*

## 相关笔记

- [[EAGLE3投机解码|EAGLE-3]]
- [[代码智能体Harness史线|Code Agents / Harness]]
- [[扩散语言模型|Diffusion Language Models]]
- [[硬件软件协同部署|硬件软件协同设计]]
- [[隐私与机器遗忘|Privacy / Unlearning]]
- [[推理引擎生态|B7 推理引擎]]
- [[AI基础设施总览|AI Infra]]

