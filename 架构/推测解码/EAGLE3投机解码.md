---
title: "EAGLE-3 投机解码增量切片（相对推理引擎生态）"
topic: EAGLE3投机解码
date: 2026-09-22
lines: [AI Infra, 数学原理]
status: archived
sources:
 - https://arxiv.org/abs/2503.01840
 - https://github.com/SafeAILab/EAGLE
 - https://papers.nips.cc/paper_files/paper/2025/hash/c7b5a35ea98b62512a869c19ea7b03cb-Abstract-Conference.html
arxiv: ["2503.01840"]
related: ["推理引擎生态", "投机解码发展时间线", "AdaptiveSpec与Goose", "EntMTP熵引导投机解码", "MTP训练范式"]
archived: 2026-09-22
---

# EAGLE-3 投机解码增量切片（相对推理引擎生态）

> **主要来源**：[EAGLE-3: Scaling up Inference Acceleration of Large Language Models via Training-Time Test](https://arxiv.org/abs/2503.01840)（Li、Wei、Zhang、Zhang，v3；NeurIPS 2025 [论文页](https://papers.nips.cc/paper_files/paper/2025/hash/c7b5a35ea98b62512a869c19ea7b03cb-Abstract-Conference.html)）；[SafeAILab/EAGLE](https://github.com/SafeAILab/EAGLE)（截至 2026-07-03）。
> **研究线**：AI Infra（草稿头设计，主）· 数学原理（接受长度与多步接受率，辅）
> **范围与相邻笔记**：
> - ≠ [[推理引擎生态]]：本篇不写「草稿—并行校验、分布不变」的框架与 Medusa / Lookahead，投机解码共用背景见该篇第三节。
> - ≠ [[AdaptiveSpec与Goose]]：本篇不写在 EAGLE-3 草稿器之上做的运行时树形与有损校验。
> - ≠ [[MTP训练范式]]：本篇不写与主模型联训的多 token 预测头。
>
> **意义**：EAGLE-3 让 EAGLE 系草稿头能随训练数据扩大持续获益：去掉特征回归约束、训练时模拟多步推理之后，加速比随训练数据增加而上升，投机解码的草稿侧由此有了缩放路径；它也常被后续工作当作强基线和草稿器（如 AdaptiveSpec）。

**一句话**：EAGLE 系在特征层做草稿，但扩大训练数据几乎不涨速；EAGLE-3 用两点改动解决——training-time test（训练时把草稿自己的输出喂回去，对齐推理时的多步输入）和多层特征融合（用目标模型低、中、高层特征代替只用顶层特征）。

---

## 一、问题背景

EAGLE 复用目标模型顶层特征（LM head 之前），在特征空间自回归出草稿，再用目标 LM head 得到草稿 token；EAGLE-2 加上按草稿置信剪枝的动态草稿树。论文观察到：把训练数据相对 ShareGPT 放大到 8 倍，EAGLE 的加速比和接受长度几乎是平线（Figure 1）。

论文的归因（§1、Figure 3–4）有两层：
1. EAGLE 的损失里有特征预测项 $l_{\text{fea}}$，要求草稿输出贴近目标顶层特征，这个额外约束限制了草稿模型的表达力。
2. 只删掉 $l_{\text{fea}}$ 还不够：训练时草稿的输入都是真特征，推理第二步起输入却是草稿自己的输出，分布偏移让后续步的接受率崩掉。

## 二、脉络

| 节点 | 内容 | 来源 |
|---|---|---|
| 投机采样（2022–2023） | 草稿 + 并行校验，输出分布不变 | [[推理引擎生态]] 第三节 |
| Medusa | 在目标模型上挂多个解码头出草稿 | [[推理引擎生态]] 第三节 |
| EAGLE | 顶层特征上自回归的草稿头 + 树注意力校验 | EAGLE-3 §2 |
| EAGLE-2 | 上下文感知的动态草稿树，EAGLE-3 沿用 | EAGLE-3 §2 |
| HASS | 保留特征预测、缓解特征误差累积 | EAGLE-3 §3.2 |
| EAGLE-3（2025） | 去掉特征约束 + training-time test + 多层特征融合 | EAGLE-3 |
| 运行时方法（2026） | 以 EAGLE-3 为草稿器调树形与校验 | [[AdaptiveSpec与Goose]] |

## 三、思想一：training-time test

做法（§3.2、Figure 3 下）：训练时就执行「测试步」。草稿头输出一个不受约束的向量 $a$，过目标 LM head 得到草稿 token；下一步把 $a$（而不是尚未校验的真特征）与新 token 的嵌入拼起来继续喂给草稿头。训练损失只留 token 预测项。这样训练分布覆盖了推理时「前缀是真特征、后面是自预测向量」的混合输入。

模拟第二、三步时，自预测 token 与训练数据 token 的依赖呈树状，注意力掩码随之改成稀疏模式（Figure 6）。

与 HASS 的区别（§3.2）：HASS 仍做特征预测、输入仍是顶层特征，动机是减少特征误差累积；EAGLE-3 的动机是去掉不必要的约束、提高表达力，输出不必拟合顶层特征。

证据（Figure 7，MT-bench，LLaMA-Instruct 3.1 8B）：$n$-$\alpha$ 指输入含 $n$ 个自预测向量时的接受率。EAGLE 随 $n$ 增大明显下降，EAGLE-3 几乎不变。

## 四、思想二：多层特征融合

为什么不能只用顶层（§1）：LM head 满秩时，顶层特征基本只编码「下一个」token 的分布，用它预测再下一个 token 信息不足。去掉 $l_{\text{fea}}$ 后，草稿输出不必再贴近顶层特征，才可以改用中间层特征。

管线（§3.1、Figure 5）：在 prefill 或上一轮校验的目标前向中记录低、中、高三层特征 $l,m,h$（各为目标隐维 $k$），拼接后经全连接层压回 $k$ 维得到融合特征 $g$；$g$ 与已采样 token 的嵌入再经全连接层送入**单层** Transformer decoder，输出 $a$，过目标 LM head 采样草稿 token。尚未校验的位置没有真 $g$，用上一步的 $a$ 代替，与 training-time test 一致。论文未给出三层的具体层号。

消融（Table 2，LLaMA-Instruct 3.1 8B，Speedup / τ）：

| 配置 | MT-bench | GSM8K |
|---|---|---|
| EAGLE-2 | 3.16× / 4.05 | 3.39× / 4.24 |
| 去掉特征约束 | 3.82× / 5.37 | 3.77× / 5.22 |
| 再加多层融合（EAGLE-3） | **4.40× / 6.13** | **4.48× / 6.23** |

两点改动各自都抬升接受长度和加速比。

## 五、结果要点

- **相对 vanilla 与 EAGLE-2**：论文称加速比 3.0×–6.5×，相对 EAGLE-2 提升 20%–40%（摘要写约 1.4×）；峰值在 HumanEval，Vicuna 13B 上 6.47×、平均接受长度 7.54（§4.1、Table 1，temperature 0）。
- **数据缩放**：训练数据从 1 倍到 8 倍 ShareGPT，EAGLE-2 近乎平台、EAGLE-3 持续上升（Figure 1）。训练数据为 ShareGPT 与 UltraChat-200K，响应由目标模型重新生成。
- **生产框架**：SGLang 团队在单卡 H100、链长 3、不用树的设定下测得 batch size 64 时 EAGLE-3 仍有 1.38× 吞吐，而 EAGLE 在 batch 24 起已低于 1×（§4.3、Table 3）。投机解码常被认为大 batch 下无用，这一组数字是反例。

## 六、意义

EAGLE-3 把「草稿头训练」从固定约束下的拟合问题改成可随数据缩放的问题：两点改动都不改目标模型、不放松接受条件，因此仍是无损加速。它在 SGLang 等引擎中落地后，常被后续投机解码研究当作强基线和草稿器宿主，例如 2026 年的 AdaptiveSpec 就直接建立在它之上。

## 七、局限与待核实

- 低、中、高三层的具体层号与全连接层初始化，论文未给出，需读代码仓。
- 405B、671B 级目标模型作者声明未测；TRT-LLM 与新版 vLLM 下的表现超出论文主表。
- vLLM 对照表（§4.4、Table 5）正文写 RTX3090、表题写 A100，论文内部不一致。
- 数字以 arXiv v3 为准（v3 即最新版）；NeurIPS 相机就绪版是否逐字相同未核对。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[推理引擎生态]] | 投机解码共用背景（decode 受带宽束缚、草稿—校验框架、Medusa / Lookahead）在那篇第三节，本篇是其后 EAGLE 系草稿头的增量 | 引擎选型、经典框架证明 |
| [[投机解码发展时间线]] | EAGLE-3 列在该时间线的投机与多 token 预测族中 | 族谱全表 |
| [[AdaptiveSpec与Goose]] | AdaptiveSpec 以 EAGLE-3 为草稿器和静态基线，在其上每步调树形、放宽校验；Goose 是无草稿头的对照路线 | margin 校验、各向异性树 |
| [[EntMTP熵引导投机解码]] | EntMTP 借用 EAGLE-2 的 path value 作为选树特征，是同一「草稿置信驱动树形」思路在 MTP 头上的变体 | TopologyBank、Hydra 栈评测 |
| [[MTP训练范式]] | 两者都训练草稿头：EAGLE-3 是独立的特征级草稿模型，那篇的 MTP 头与主模型联训；FastMTP 兼容 EAGLE 式递归草稿 | MTP 损失与头对齐 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [EAGLE-3](https://arxiv.org/abs/2503.01840) Figure 1、3–5、§3 | 数据缩放曲线；training-time test 与融合管线 |
| 2 | 同上 Table 2、Figure 7 | 两点改动的消融；多步接受率不衰减 |
| 3 | [SafeAILab/EAGLE](https://github.com/SafeAILab/EAGLE) | 实现与层号 |
| 4 | [[AdaptiveSpec与Goose]] | 以 EAGLE-3 为草稿器的运行时扩展 |
