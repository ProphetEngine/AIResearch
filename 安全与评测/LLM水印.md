---
title: "LLM watermarking：SynthID-Text + 理论/鲁棒性复核"
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
related: ["B11", "训练数据污染检测", "评测与排行榜可靠性"]
archived: 2026-09-22
---

# LLM watermarking：SynthID-Text（Nature）+ 理论/鲁棒性复核

> **定位**：**生成文本水印 / 供给链溯源** 横切——相对 `B11`（Model/System Card 文档规范）与 [[训练数据污染检测]]（训练数据污染检测），本篇只写 **LLM 输出侧 generative watermarking**：Tournament 采样、检测统计、公开攻击面分类与检测指标。
> **攻坚线**：**数学原理（主）**——Tournament / g-value / Mean Score vs Bayesian Score / TPR@FPR；**评测字段（辅）**——质量中性、延迟、意义保持变换下的 TPR/FPR/F1。
> **硬划界**：
> - **相对 `B11`**：不重写卡字段谱系；水印可作为「溯源/披露」邻接字段一句交叉。
> - **相对 [[训练数据污染检测]]**：不写 quiz / n-gram / canary 污染探针；本篇 = **生成后文本是否带水印**，≠ 训练语料是否见过评测集。
> - **禁止**写成「如何彻底去水印」操作手册；鲁棒性章节 **只报告公开攻击面分类与检测指标**（不展开可复现 scrubbing 配方）。
> **禁止编造**：主张与数字锚定官方 PDF（2026-09-22 CST）；Nature 主文 14 页正文 + Extended Data；理论/鲁棒性为 arXiv 近窗复核。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主锚（一手）** | Dathathri, See, Ghaisas, Huang, McAdam et al. (Google DeepMind / Google), *Scalable watermarking for identifying large language model outputs* | **Nature** **634**, 818–823 (2024)；doi:**10.1038/s41586-024-08025-4**；Received 8 Apr 2024 / Accepted 5 Sep 2024 / Published **23 Oct 2024**；Open access；`https://doi.org/10.1038/s41586-024-08025-4`（**14** 页；CreationDate **2024-10-14** CST；4,313,074 bytes） | SynthID-Text：Tournament 采样、非失真/失真配置、检测分数、与 speculative sampling 结合、Gemini 直播质量实验、开源入口 |
| **理论复核** | Omidi, Dong & Wang, *On Google’s SynthID-Text LLM Watermarking System: Theoretical Analysis and Empirical Validation* | arXiv:**2603.03410v2** \[cs.CR\] **15 Mar 2026**；`https://arxiv.org/abs/2603.03410`（**34** 页 letter） | MS/BS 的 TPR@FPR 闭式趋势；Bernoulli(0.5) 最优；layer inflation **攻击面**与 MS 脆弱性（本笔记只取分类+指标） |
| **鲁棒性复核** | Han, Li, Ni & Zulkernine, *Robustness Assessment and Enhancement of Text Watermarking for Google’s SynthID* | arXiv:**2508.20228v2** \[cs.CR\] **21 Oct 2025**；`https://arxiv.org/abs/2508.20228`（**12** 页 letter） | 四类 **意义保持**变换下 SynthID 检测指标；SynGuard 混合增强（对比数字，非去水印手册） |
| **代码/数据（文内）** | SynthID-Team | https://github.com/google-deepmind/synthid-text （Nature ref. 7，2024） | 生成/检测参考实现；本篇不展开工程细节 |
| **产品披露（文内）** | DeepMind Blog | *Watermarking AI-generated text and video with SynthID*（Nature ref. 20） | Gemini / Gemini Advanced 生产化一句 |

**一句话抓手：** SynthID-Text 在 **采样层** 用密钥种子的多层 Tournament 偏置选 token，检测端用 Mean / Bayesian 分数读回偏置——**不改训练、检测不用 LLM**；约 **2000 万** Gemini 回应上拇指差 **≤0.02%** 且不显著；理论证明 **Mean Score 的 TPR 对层数单峰**（可被 layer inflation 攻击面击穿），**Bayesian Score 对层数单调不减后饱和**；公开鲁棒性评估显示 **同义替换相对稳、粘贴稀释/释义/回译显著伤 F1**。

---

## 二、议题边界：输出水印溯源 ≠ 卡规范 ≠ 语料污染检测

| 已入库 | 本篇只取 | 本篇不写 |
|---|---|---|
| **B11** Model/System Card | 「披露与可信发布需要可核对接口」的邻接槽 | Mitchell/HF 字段全文、厂商卡数字重抄 |
| **[[训练数据污染检测]]** 污染检测 | 「评测可信需要溯源工具」一句 | DCQ / Min-K% / canary / IFT oracle |
| **[[评测与排行榜可靠性]]** 榜可靠性 | 「分数绑定未声明协议」——本篇把 FPR 标定、文本长度、温度写进评测字段 | 污染三分法通史 |
| 检索/后验分类器文献（Nature 引言对照） | 水印与 retrieval / post-hoc classifier **互补** | DetectGPT 等后验检测全文 |

**跟读口诀（生成时嵌入 → 事后统计检测）：**

`
密钥 k + 滑动窗上下文 (H=4) → 伪随机种子 rt
 │
 ▼
 从 pLM 过采样候选 → m 层 Tournament（按 gℓ 决胜）→ 输出 xt
 │
 ▼
 检测：对全文重算 gℓ，聚合成 Score（Mean / Weighted / Frequentist / Bayesian）
 │
 ▼
 与阈值比 → 判「水印 / 非水印」；主报指标 TPR @ FPR = 1%
`

---

## 三、SynthID-Text 数学原理（Nature 主锚）

### 3.1 三件套框架（与 Piet et al. 生成式水印框架对齐）

Nature 将生成式水印拆为：

1. **Random seed generator** $r_t = f_r(x_{<t}, k)$
2. **Sampling algorithm** $S(p_{\mathrm{LM}}(\cdot\mid x_{<t}), r_t)\to x_t$
3. **Scoring function** $\mathrm{Score}(x; k)$（**只需分词文本 + 密钥 + $f_r$**，**不需要**原 LLM）

实验默认：滑动窗哈希 $r_t = h(x_{t-H},\ldots,x_{t-1},k)$，**$H=4$**；**K-sequence repeated context masking**（实验多用 **$K=1$**）避免同一上下文窗重复偏置导致循环退化。

### 3.2 Tournament sampling（核心新采样）

直觉（Fig. 2）：对每一层 $\ell=1,\ldots,m$，用伪随机 $g_\ell(x, r_t)$（文称 **g-value**）给候选打分；从 $p_{\mathrm{LM}}$ 抽出 $M=2^m$（非失真配置下每场 **2** 名选手）个候选，按层做淘汰赛，最后赢家为 $x_t$。

**Methods 默认实验超参：** $m=30$ 层；$g$-value 分布主用 **Bernoulli(0.5)**（也试 Uniform$[0,1]$）；检测默认 **Bayesian** 打分（Supplementary A.4）。

**Mean score（正文式 (1)）：**

$$
\mathrm{Score}(x)=\frac{1}{mT}\sum_{t=1}^{T}\sum_{\ell=1}^{m} g_\ell(x_t,r_t).
$$

水印文本因采样偏好高 $g$，期望分数高于非水印文本。可检测性随 **文本长度**↑、随 **$p_{\mathrm{LM}}$ 熵**↑；低熵（低温、大模型更「确定」、RLHF mode collapse）时变弱——文中明确与其它生成式水印同构。

### 3.3 非失真谱系（文内澄清术语）

文中把 non-distortion 从弱到强定义（细节在 Suppl. G）：

| 配置 | 机制要点（文内） | 质量/检测权衡 |
|---|---|---|
| **Non-distortionary SynthID-Text**（默认所指） | 每场恰好 **2** 选手 → **single-token non-distortion**；再配合 repeated context masking → 实验用 **single-sequence non-distortionary** | 保质量；略损跨回应多样性 |
| **Distortionary SynthID-Text** | 每场 **>2** 选手（Algorithm 2 一般 $N$） | 更强水印、更高可检测，付质量代价 |

**基线对照（同 seed / 同 masking）：** 非失真对 **Gumbel sampling**；失真对 **Soft Red List**。文称两类下 SynthID-Text 均可检测性更优（Fig. 3；Extended Data Fig. 1–2）。

### 3.4 检测族与生产指标字段

| 字段 | 文内取值 / 定义 |
|---|---|
| **主检测指标** | 经验 **TPR @ FPR = $x\%$**（非水印分数上取 top-$x\%$ 阈值，再算水印召回） |
| **模型** | Gemma 2B/7B-IT；Mistral 7B-IT v0.2；top-$k=100$；温度 0.5 / 0.7 / 1.0 |
| **提示** | ELI5；非失真实验各 10k 提示；失真测试 1.5k |
| **延迟（Gemma 7B-IT @ 4×v5e TPU）** | 基线 **15.527** ms/token → $m=30$ Tournament **15.615**（**+0.57%**）；Gumbel **+0.26%**；Soft Red List **+0.28%** |
| **Gemini 直播** | ≈**2000 万** 水印/非水印回应；thumbs-up 差 **0.01%**、thumbs-down 差 **0.02%**，文称不显著、落在 95% CI 内 → 已用于 Gemini / Gemini Advanced |
| **小规模人工偏好** | Gemma 7B-IT × 3k ELI5；五维（语法连贯/相关/正确/有用/总体）无显著差异（Extended Data Table 1） |
| **Speculative 结合** | **high-detectability**（保检测、可能损效率）vs **fast**（保接受率/延迟、可能损检测；可用学习贝叶斯分补回） |

### 3.5 局限（Nature Discussion，跟读边界）

文内自述：需服务方协调嵌水印；难强制开源去中心化部署；对 **stealing / spoofing / scrubbing** 仍属开放研究；**编辑与 LLM 释义**会削弱信号（Suppl. C.6 有评估）。本篇 **不**据此展开去水印步骤。

---

## 四、理论复核（2603.03410）：TPR 对层数的行为 + 检测器选择

### 4.1 设定对齐

论文形式化 SynthID 的 MS / BS，在 **CLT** 下给出期望 **TPR@FPR=$\epsilon$** 对层数 $m$ 的闭式趋势；经验用公开实现 + Gemma-2B / Gemma-7B / Mistral-7B、约 100 token、**FPR=1%** 验证。引言复述 Nature 量级：约 **TPR=85% vs 基线 SOTA 73% @ FPR=1%**（1500 条水印文本、30 层、Bernoulli(0.5)、Bayesian；指向 Nature Fig. 3a）。

### 4.2 主定理级结论（跟读）

| 分数 | 对层数 $m$ 的 TPR@FPR 行为 | 实务含义 |
|---|---|---|
| **Mean Score (MS)** | **单峰**：先升后降；$m\to\infty$ 时期望 TPR → $\epsilon$（=FPR） | 盲目加层 **不**单调变强；深部层信号弱、分布重叠增大 |
| **Bayesian Score (BS)** | **单调不减**后饱和（碰撞概率 $\hat C_{m,t}=1$ 时饱和） | 加层通常有利，但计算更贵 |
| **Bernoulli $g$** | 在 Bernoulli 族中 **$p=0.5$** 使固定 FPR 下 TPR 最大（Thm. 12，MS） | 与 Nature 默认一致 |

经验对齐（文 Fig. 2）：Gemma-7B 上 MS 的 TPR 约从层 1→28 升至 ~0.88，再降，**100 层**时可落到约 **TPR=1%**（=FPR）；BS 上升后平台。

### 4.3 攻击面分类（仅分类 + 指标；禁操作手册）

| 攻击面（公开分类名） | 机制层级（一句话） | 公开检测指标（文内） |
|---|---|---|
| **Layer inflation（层膨胀）** | **分数侧 / 采样管线侧**：利用 MS 对 $m$ 的单峰性，在黑盒水印 LLM 外再叠额外 tournament 层，使 MS 期望下移越过阈值 | Table 1：额外 **10** 层后 TPR — GPT-2B **0.15** / Gemma-7B **0.13** / Mistral-7B **0.16**（攻击前 1k ELI5 水印样本均被正确检出）；Gemma 上 MS 均值 **0.548→0.494**，阈值 **0.510**（FPR=1% 标定） |
| **BS 相对 MS** | 非「去水印配方」，而是 **检测器选择**：BS 对层数单调 → 文称相对更抗此类层操纵；代价是算力 | 定性结论 + §4.1 趋势验证 |

> **安全跟读：** 上表只固定「有人公开报告过这类攻击面及其 TPR 跌幅」；**不**转写论文中的逐步构造伪代码为可跟做 scrubbing 手册。实务上优先部署 **Bayesian（或非 MS）检测**、监控层数/分数分布异常。

---

## 五、鲁棒性复核（2508.20228）：意义保持变换下的指标

### 5.1 评测字段

| 字段 | 文内 |
|---|---|
| **对象** | SynthID-Text（及对比增强 **SynGuard** = SIR 语义对齐 + SynthID tournament） |
| **指标** | TPR / FPR / 最优阈值下 **F1**；ROC / AUC |
| **攻击面族（意义保持）** | ① 同义替换 ② copy-and-paste 稀释 ③ 释义（Dipper） ④ 回译（NLLB 等） |
| **代码** | https://github.com/githshine/SynGuard |

### 5.2 SynthID-Text 攻击面 × 检测指标（Table V 摘要）

| 攻击面分类 | 代表设置 | TPR | FPR | F1 |
|---|---|---|---|---|
| 无攻击 | — | 1.0 | 0.0 | 1.0 |
| **同义替换（语境）** | Word-S(Context) $\epsilon=0.7$ | 0.82 | 0.035 | **0.884** |
| **Copy-and-paste 稀释** | ratio = 10（插入自然文本为水印段 10×） | 0.995 | **0.53** | **0.788** |
| **释义** | Dipper lex=10, order=5 | 0.895 | 0.23 | **0.842** |
| **回译** | 中文枢纽 | 0.675 | 0.225 | **0.711** |

补充（同文表）：同义 $\epsilon=0.3/0.5$ 时 F1 仍高（0.987 / 0.936）；粘贴 ratio≥20 时 AUC≈≤0.5（近随机）；回译枢纽间 F1：日 **0.819** > 意 **0.813** > 法 **0.738** > 中 **0.711**（Table IV）。文称回译伤害与 **翻译质量/工具**相关，不宜简化为「语系距离」单一轴。

**分类结论（非步骤）：** 对 **轻度语境同义**相对稳；对 **长上下文稀释、结构级释义、跨语回译** 检测指标显著恶化——与 Nature「编辑/释义削弱」自述同向。

### 5.3 SynGuard（增强对照，非本篇主线）

文称相对 SynthID **平均 F1 +11.1%**；同设置攻击下 SynGuard 多保持更高 F1（如 NLLB 中文回译 F1 **0.777** vs SynthID Table V **0.711**；FPR **0.07** vs **0.225**）。机制一句话：语义 SIR 分量抗同义/释义，token 侧保留密钥随机性。本篇 **不**展开其嵌入算法实现细节为对抗手册。

---

## 六、研究会可落字段（归档最小集）

写 Model/System Card 或内部溯源页时，建议至少固定（交叉 B11，不重写 B11）：

1. **是否启用生成式水印**（方案名：SynthID-Text / 其它；non- vs distortionary）
2. **检测器类型**（MS / BS / 其它）与 **FPR 操作点**（如 1%）
3. **文本长度 / 温度 / top-$k$-$p$** 对 TPR 的依赖声明
4. **已知公开攻击面覆盖**：编辑·释义·粘贴稀释·回译·（若用 MS）层膨胀类分数操纵——用 **TPR/FPR/F1** 表，不写清除步骤
5. **与污染检测（[[训练数据污染检测]]）正交**：水印答「这段输出是否来自我方带钥采样」；污染答「训练是否见过该评测题」

---

## 七、待核实 / 未读

- Nature **Supplementary Information**（A–I：打分细节、复杂度、speculative 证明、C.6 编辑评估等）本抽取仅覆盖主 PDF 14 页正文 + Extended Data；补读 Suppl. 前相关细节标「待核实」。
- 生产 Gemini 实际 $m$、密钥管理、对外检测 API 是否开放：主文未给可复现数字 → **待核实**。
- 2603.03410 / 2508.20228 均为 arXiv；若日后正式出版以版本页为准。

---

## 八、交叉引用

- 模型与技术报告/SystemCard/模型卡与SystemCard规范.md — 披露字段接口（不重写）
- 安全与评测/训练数据污染检测.md — 语料污染检测（正交）
- 安全与评测/评测与排行榜可靠性.md — 评测协议纪律
- [[MOC_安全与评测]]

## 相关笔记

- [[恶意软件分析评测|Malware Analysis Evals]]
- [[LLM水印|LLM Watermarking]]
- [[持续学习|Continual Learning LLM]]
- [[SelfRAG与CorrectiveRAG|Self-RAG / CRAG]]
- [[MMMU多模态推理基准|MMMU-Pro]]

