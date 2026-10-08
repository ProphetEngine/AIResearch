---
title: "LLM watermarking：SynthID-Text（Nature）+ 理论/鲁棒性复核"
topic: LLM水印
date: 2026-09-22
lines: [数学原理, 评测字段]
status: archived
sources:
 - https://doi.org/10.1038/s41586-024-08025-4
 - https://arxiv.org/abs/2603.03410
 - https://arxiv.org/abs/2508.20228
arxiv: ["2603.03410", "2508.20228"]
doi: ["10.1038/s41586-024-08025-4"]
related: ["模型卡与SystemCard规范", "训练数据污染检测", "评测与排行榜可靠性"]
archived: 2026-09-22
---

# LLM watermarking：SynthID-Text（Nature）+ 理论/鲁棒性复核

> **主要来源**：[Scalable watermarking for identifying large language model outputs](https://doi.org/10.1038/s41586-024-08025-4)；[On Google’s SynthID-Text LLM Watermarking System: Theoretical Analysis and Empirical Validation](https://arxiv.org/abs/2603.03410)；[Robustness Assessment and Enhancement of Text Watermarking for Google’s SynthID](https://arxiv.org/abs/2508.20228)（截至 2026-09-22）。下文「Nature」指 SynthID-Text 主文，「理论复核」「鲁棒性复核」分别指后两篇。
> **研究线**：数学原理（主）——Tournament 采样、g-value、Mean Score 与 Bayesian Score、TPR@FPR；评测字段（辅）——质量中性、延迟、意义保持变换下的 TPR / FPR / F1。
> **范围与相邻笔记**：
> - ≠ [[模型卡与SystemCard规范]]：本篇不写卡字段谱系，水印只作「溯源与披露」的邻接字段。
> - ≠ [[训练数据污染检测]]：本篇不写 quiz、n-gram、canary 等污染探针；本篇问的是生成后的文本是否带水印，不是训练语料是否见过评测集。
> - 本篇不写去水印的操作手册；鲁棒性部分只报告公开的攻击面分类与检测指标。
> **意义**：SynthID-Text 把 LLM 文本水印推到了大规模生产部署：只改采样、不改训练，检测不需要原模型，约 2000 万条 Gemini 回应上用户反馈无显著差异。两篇复核随后表明，检测器选择（Mean 还是 Bayesian）决定它能否抵抗分数操纵，而稀释、释义与回译仍会显著削弱检测，水印更适合作为溯源工具之一，而不是单一判据。

**一句话**：SynthID-Text 在采样层用密钥种子驱动多层 Tournament 偏置 token 选择，检测端用 Mean 或 Bayesian 分数读回偏置；理论上 Mean Score 的 TPR 随层数先升后降（可被层膨胀击穿），Bayesian Score 单调不减后饱和；公开评估显示同义替换相对稳，粘贴稀释、释义与回译明显伤 F1。

## 一、问题背景

SynthID-Text 要解决的是识别 LLM 输出：事后判断一段文字是否出自服务方的模型。Nature 引言把水印（生成时嵌入可统计检测的信号）与检索（保存生成记录再比对）、事后分类器（训练模型判别）对照，认为三者互补。

生成式水印的难点在于三重约束：不能明显降低文本质量，检测要便宜、最好不需要原模型，还要扛住编辑与改写。SynthID-Text 的回答是只改采样算法：用密钥和上下文生成伪随机种子，偏置 token 选择；检测时只需分词后的文本、密钥和种子函数。

## 二、脉络

- **已有方案**：生成式水印此前已有 Soft Red List（失真类）与 Gumbel sampling（非失真类）等，Nature 把它们分别作为失真与非失真配置的对照基线。
- **2024-10，SynthID-Text（Nature）**：Google DeepMind 提出 Tournament 采样，在 Gemini 与 Gemini Advanced 上线，并开源参考实现（google-deepmind/synthid-text）。
- **2025-08，鲁棒性复核**：在四类意义保持的变换下测 SynthID 的检测指标，并提出语义增强的 SynGuard。
- **2026-03，理论复核**：给出 Mean 与 Bayesian 两种分数的 TPR 随层数变化的闭式趋势，并报告利用 Mean Score 弱点的层膨胀攻击面。

主线是从「能部署」走向「检测器在什么条件下可靠」：Nature 证明了质量中性与可检测性，复核把边界补上。

## 三、SynthID-Text 的机制

### 3.1 三件套框架

Nature 沿用 Piet 等的生成式水印框架，把方案拆为三部分：

1. **随机种子生成器** $r_t = f_r(x_{<t}, k)$：默认用前 $H=4$ 个 token 与密钥 $k$ 做滑动窗哈希；配合 repeated context masking（实验多用 $K=1$），避免同一上下文窗反复施加偏置导致循环退化。
2. **采样算法** $S(p_{\mathrm{LM}}(\cdot\mid x_{<t}), r_t)\to x_t$：Tournament 采样。
3. **打分函数** $\mathrm{Score}(x; k)$：只需分词文本、密钥与 $f_r$，不需要原 LLM。

### 3.2 Tournament 采样

对每一层 $\ell=1,\ldots,m$，用伪随机函数 $g_\ell(x, r_t)$（g-value）给候选 token 打分。从 $p_{\mathrm{LM}}$ 抽出 $2^m$ 个候选，逐层两两淘汰，g-value 高者晋级，最后的赢家即输出 token。默认 $m=30$ 层，g-value 主用 Bernoulli(0.5) 分布。

检测时重算全文的 g-value 并聚合。最简单的是 Mean Score：

$$
\mathrm{Score}(x)=\frac{1}{mT}\sum_{t=1}^{T}\sum_{\ell=1}^{m} g_\ell(x_t,r_t).
$$

水印文本因采样偏好高 g-value，期望分数高于非水印文本；默认检测用 Bayesian Score（Nature Supplementary A.4）。可检测性随文本变长、随模型输出熵变高而增强；低温、大模型更「确定」或 RLHF 后 mode collapse 等低熵情形下会变弱，这一点与其他生成式水印相同。

### 3.3 非失真与失真配置

| 配置 | 机制要点 | 权衡 |
|---|---|---|
| 非失真（默认） | 每场恰好 2 名选手，单 token 不改变分布；加上 repeated context masking 后达到单序列非失真 | 保质量，略损跨回应多样性 |
| 失真 | 每场多于 2 名选手 | 水印更强、更易检测，付出质量代价 |

两类配置下 SynthID-Text 的可检测性都优于对应基线（Nature Fig. 3）。理论复核引述的量级是：1,500 条水印文本、30 层、Bernoulli(0.5)、Bayesian 打分时，FPR = 1% 下 TPR 约 85%，基线约 73%。

### 3.4 生产字段

- **主指标**：TPR @ FPR = $x\%$，即在非水印分数上取 top-$x\%$ 作为阈值，再计算水印文本的召回。
- **实验模型**：Gemma 2B / 7B-IT、Mistral 7B-IT v0.2，top-$k=100$，温度 0.5 / 0.7 / 1.0，ELI5 提示。
- **延迟**（Gemma 7B-IT，4×v5e TPU）：基线 15.527 ms/token，30 层 Tournament 为 15.615（+0.57%）；Gumbel 为 +0.26%，Soft Red List 为 +0.28%。
- **Gemini 线上实验**：约 2000 万条水印与非水印回应，点赞率差 0.01%、点踩率差 0.02%，落在 95% 置信区间内、不显著；小规模人工偏好评估（Gemma 7B-IT × 3k ELI5，五个维度）也无显著差异。
- **与 speculative sampling 结合**：有「高可检测」与「快速」两种模式，前者保检测、可能损效率，后者保接受率与延迟、可能损检测（可用学习得到的贝叶斯分数补回）。

## 四、理论复核：检测器选择

理论复核在中心极限定理下推导两种分数的期望 TPR@FPR 随层数 $m$ 的变化，并在公开实现上用 GPT-2B / Gemma-7B / Mistral-7B、约 100 token、FPR = 1% 做验证：

| 分数 | TPR 随层数 $m$ 的行为 | 含义 |
|---|---|---|
| Mean Score | 单峰：先升后降，$m\to\infty$ 时期望 TPR 退化为 FPR | 盲目加层不会单调变强，深层信号弱、分布重叠增大 |
| Bayesian Score | 单调不减，碰撞概率饱和后进入平台 | 加层通常有利，但计算更贵 |
| Bernoulli g-value | 在 Bernoulli 族中 $p=0.5$ 使固定 FPR 下 TPR 最大（Mean Score） | 与 Nature 默认一致 |

经验曲线上，Gemma-7B 的 Mean Score TPR 从第 1 层升到第 28 层约 0.88 后下降，100 层时可落到约 1%（即 FPR）；Bayesian Score 上升后进入平台。

**层膨胀攻击面**：利用 Mean Score 对层数的单峰性，在黑盒水印模型外再叠加额外的 tournament 层，使分数均值越过阈值。额外 10 层后 TPR 降到 0.15（GPT-2B）、0.13（Gemma-7B）、0.16（Mistral-7B），攻击前 1k 条 ELI5 水印样本均能被正确检出；Mean Score 均值从 0.548 降到 0.494，阈值为 0.510（按 FPR = 1% 标定）。Bayesian Score 对层数单调，文中认为相对更抗这类操纵。这里只记攻击面的类别与指标，不转写构造细节；实务上应优先部署 Bayesian（或其他非 Mean）检测，并监控层数与分数分布的异常。

## 五、鲁棒性复核：意义保持变换

鲁棒性复核以 TPR、FPR、最优阈值下的 F1 与 ROC / AUC 为指标，考察四类意义保持的变换（鲁棒性复核 Table V 摘要）：

| 攻击面类别 | 代表设置 | TPR | FPR | F1 |
|---|---|---:|---:|---:|
| 无攻击 | — | 1.0 | 0.0 | 1.0 |
| 语境同义替换 | Word-S(Context)，$\epsilon=0.7$ | 0.82 | 0.035 | 0.884 |
| 粘贴稀释 | 插入自然文本为水印段的 10 倍 | 0.995 | 0.53 | 0.788 |
| 释义 | Dipper，lex=10、order=5 | 0.895 | 0.23 | 0.842 |
| 回译 | 中文为中间语 | 0.675 | 0.225 | 0.711 |

- 同义替换较轻时（$\epsilon=0.3 / 0.5$）F1 仍有 0.987 / 0.936；粘贴比例达到 20 倍及以上时 AUC 约不高于 0.5，接近随机。
- 回译的伤害随中间语不同：日语 0.819、意大利语 0.813、法语 0.738、中文 0.711（Table IV）。作者认为这与翻译质量和工具有关，不宜简化成「语系距离」一条轴。
- 结论：对轻度语境同义替换相对稳；对长上下文稀释、结构级释义与跨语回译，检测指标显著恶化，与 Nature 自述的「编辑与释义会削弱信号」同向。
- **SynGuard**：把语义分量（SIR）与 SynthID 的 tournament 结合，语义分量抗同义与释义，token 侧保留密钥随机性；文称平均 F1 比 SynthID 高 11.1%，如中文回译下 F1 0.777 对 0.711、FPR 0.07 对 0.225。代码见 githshine/SynGuard。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[模型卡与SystemCard规范]] | 披露接口：是否启用水印、检测器类型与 FPR 操作点、已知攻击面覆盖，可作为卡上的溯源字段 | 卡字段谱系与厂商卡数字 |
| [[训练数据污染检测]] | 正交问题：水印回答「这段输出是否出自带钥采样」，污染检测回答「训练是否见过评测题」 | DCQ、Min-K%、canary 等探针 |
| [[评测与排行榜可靠性]] | 评测原则：分数绑定协议；水印的检测结果须声明 FPR 标定、文本长度与温度 | 污染三分法通史 |

## 七、局限与待核实

- **Nature 自述的边界**（Nature Discussion）：需要服务方配合嵌入水印，难以约束开源权重的去中心化部署；对 stealing、spoofing、scrubbing 仍是开放问题；编辑与 LLM 释义会削弱信号（Supplementary C.6 有评估）。
- **低熵场景**：低温、确定性强的大模型或 mode collapse 后，可检测性下降，短文本也更难检测。
- **未读部分**：Nature Supplementary Information（打分细节、复杂度、speculative 的证明、C.6 编辑评估等）本篇未补读，相关细节待核实。
- **生产参数**：Gemini 实际使用的层数、密钥管理、是否对外开放检测 API，主文没有给出可复现的数字，待核实。
- **版本**：两篇复核均为 arXiv 预印本，若日后正式出版以出版版本为准。

## 八、延伸阅读

| 类型 | 标题 | 说明 | URL |
|---|---|---|---|
| 论文 | Scalable watermarking for identifying large language model outputs | Dathathri 等（Google DeepMind），Nature 634, 818–823，2024-10-23 | https://doi.org/10.1038/s41586-024-08025-4 |
| 论文 | On Google’s SynthID-Text LLM Watermarking System: Theoretical Analysis and Empirical Validation | Omidi、Dong、Wang，2026-03；TPR 随层数的闭式趋势与层膨胀 | https://arxiv.org/abs/2603.03410 |
| 论文 | Robustness Assessment and Enhancement of Text Watermarking for Google’s SynthID | Han、Li、Ni、Zulkernine，2025-08（v2 为 2025-10）；意义保持变换与 SynGuard | https://arxiv.org/abs/2508.20228 |
| 代码 | google-deepmind/synthid-text README | 生成与检测的参考实现 | https://github.com/google-deepmind/synthid-text |
| 代码 | githshine/SynGuard README | SynGuard 实现 | https://github.com/githshine/SynGuard |
