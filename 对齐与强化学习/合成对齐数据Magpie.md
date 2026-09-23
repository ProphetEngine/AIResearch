---
title: "合成对齐数据：Magpie + ActiveUltraFeedback"
topic: 合成对齐数据Magpie
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2406.08464
 - https://arxiv.org/abs/2603.09692
arxiv: ["2406.08464", "2603.09692"]
related: ["B8", "SimPO与ORPO偏好优化", "对齐脉络RLHF与偏好优化", "B3", "NemotronCC数据策展"]
project:
 - https://magpie-align.github.io/
 - https://hf.co/magpie-align
 - https://github.com/lasgroup/ActiveUltraFeedback
 - https://huggingface.co/ActiveUltraFeedback
 - https://lasgroup.github.io/rlhf/ActiveUltraFeedback.html
archived: 2026-09-22
---

# 合成对齐数据：Magpie + ActiveUltraFeedback

> **定位**：[[合成对齐数据Magpie]] **P1 数据侧横切**——对照两篇对齐数据流水线主文：**无种子提示的自合成指令数据**（Magpie）vs **不确定度驱动的主动偏好对选取**（ActiveUltraFeedback）。
> **攻坚线**：**架构思想 / 数据流水线（主）** + **文内下游评测字段（辅）**（AlpacaEval / Arena-Hard / WildBench；GSM8K / IFEval / TruthfulQA / AlpacaEval 2 / RewardBench 2）。
> **硬划界（禁止重写）**：
> - **≠ B8**：不写 phi / Textbooks Are All You Need 式 **教科书/代码合成预训练** 通史。
> - **≠ [[SimPO与ORPO偏好优化]]**：不写 SimPO / ORPO / IPO **偏好损失函数** 推导与族谱（ActiveUF §5.5 仅把 IPO/SimPO 当**下游消费算法**点名）。
> - **≠ [[对齐脉络RLHF与偏好优化]]**：不重写 RLHF / DPO / CAI 三阶段通史与损失精读（只作「偏好数据从哪来」对照一句）。
> - **≠ B3**：不写 FineWeb / DCLM / Dolma 式 **网页过滤策展**；预训练网页管线见 **[[NemotronCC数据策展]] Nemotron-CC**。
> **禁止编造**：数字、表号、版本一律取自官方 PDF（2026-09-22 CST）与 arXiv API。

---

## 一、材料元信息与对照抓手

| 材料 | 标识 | 本地 | 页数 / 版本 | 流水线角色 |
|---|---|---|---|---|
| **主文 A** | Xu, Jiang, Niu, Deng, Poovendran, Choi, Lin (UW / AI2), *Magpie: Alignment Data Synthesis from Scratch by Prompting Aligned LLMs with Nothing* | arXiv:**2406.08464v2** \[cs.CL\] **7 Oct 2024**；`https://arxiv.org/abs/2406.08464` | **32** 页（ CreationDate **2024-10-08** CST） | **无种子、无提示工程**：只喂 chat **pre-query template**，自回归吐出 user query，再生成 response → SFT / DPO 数据 |
| **主文 B** | Melikidze, Schneider, Lam, Wertich, Hakimi, Pásztor, Krause (ETH / UZH), *ActiveUltraFeedback: Efficient Preference Data Generation using Active Learning* | arXiv:**2603.09692v2** \[cs.LG\] **1 Jun 2026**（published **2026-03-10**）；ICML 2026（文眉 PMLR 306）；`https://arxiv.org/abs/2603.09692` | **40** 页 | **主动学习选偏好对**：多模型池生成候选 → ENN 奖励+不确定度 → DRTS / DeltaUCB 等选对 → LLM judge 标注 → 再训奖励模型 |

**开源（论文自报）：** Magpie `magpie-align.github.io` / `hf.co/magpie-align`；ActiveUF `github.com/lasgroup/ActiveUltraFeedback` + `huggingface.co/ActiveUltraFeedback`

**一句话对照：**

| | Magpie | ActiveUltraFeedback |
|---|---|---|
| **缺什么就补什么** | 缺 **公开、可规模化的指令（+可选偏好）数据本身** | 缺 **在有限标注预算下选哪一对 response 最值得标** |
| **输入前提** | 已对齐开源 chat 模型 + 其 chat template | 已有 **prompt 集合** + **多 LLM 响应池** |
| **核心动作** | `T_pre-query` → 自合成 instruction → 再合成 response | 批循环：生成 → ENN 估奖励/σ → acquisition → judge → 更新 ENN |
| **相对静态 UltraFeedback** | Magpie 可自产指令；也可扩展 Magpie-DPO | 保留 UltraFeedback 式多模型+judge 骨架，把「每 prompt 固定启发式选对」换成 **主动 / delta 选对** |
| **公开主指标轴** | AlpacaEval 2 LC/WR、Arena-Hard WR、WildBench；辅 Open LLM Leaderboard | 下游 Mean（GSM8K+IFEval+TruthfulQA+AlpacaEval 2）Δ + RewardBench 2 Δ；样本效率曲线 |

`
Magpie（造指令/响应对） ActiveUF（在已有 prompt 上选偏好对）
 T_pre-query ──► instruction prompts P
 │ │
 ▼ ▼
 wrap + T_post ──► response m=30 LLMs → candidates
 │ │
 ▼ ▼
 filter / MT / DPO 扩展 ENN r±βσ → DRTS/DeltaUCB/...
 │
 ▼
 LLM-as-Judge → (x,y+,y−)
 │
 ▼
 更新 ENN，下一批
`

---

## 二、问题立轴：对齐数据侧的两个缺口

两文诊断互补（意译压缩，非通史）：

1. **Magpie §1**：开源权重常有、**对齐数据仍私有**；人工标注贵；既有合成（Self-Instruct / Evol-Instruct / UltraChat 等）依赖 **seed + 提示工程**，规模一大多样性塌缩。问：能否 **直接从已对齐 LLM 抽出** 大规模高质量指令？
2. **ActiveUF §1 / Related**：UltraFeedback / Magpie / Nectar 等偏好数据多用 **静态启发式**（随机、best-of-N、固定族内大小对比 DeltaQwen）；dueling-bandit 文献又常只盯奖励模型或只盯策略优化一侧。问：能否在 **contextual dueling bandit** 框架下，用不确定度 **自适应选对**，用更少标注做出可同时服务 **奖励建模与多种偏好优化算法** 的数据？

本篇只立这两条 **数据流水线**；损失族、网页预训练策展、教科书合成见划界笔记。

---

## 三、流水线 A：Magpie（2406.08464）

### 3.1 核心观察（架构）

对齐 LLM 的输入可写为
$x = T_{\mathrm{pre\text{-}query}} \oplus q \oplus T_{\mathrm{post\text{-}query}}$。
例（Llama-3-Instruct）：
- $T_{\mathrm{pre\text{-}query}} =$ `<|start_header_id|>user<|end_header_id|>`
- $T_{\mathrm{post\text{-}query}} =$ `<|eot_id|><|start_header_id|>assistant<|end_header_id|>`

**关键观察（§1 / §2.1）：** 只喂 $T_{\mathrm{pre\text{-}query}}$（到「用户消息槽位」为止），自回归模型会 **自己生成一条 user query**；再把该 query 按正式 chat 模板包起来生成 assistant response → 得到指令数据。
文称：**无需 seed、无需专门提示工程**；相对既有合成，多样性不易随规模塌缩。
Remark：即使对齐时 instruction loss 被 mask，仍能生成高质量指令——作者假设存在对指令分布的隐式记忆（留作未来问题）。

### 3.2 两步流水线（Fig.1）

| 步 | 动作 | 产物 |
|---|---|---|
| **Step 1 Instruction** | 输入 pre-query template；采样至 EOS | 指令集合 |
| **Step 2 Response** | 用 post-query + 再开一轮 pre-query 包住 Step 1 指令，让同一（或指定）LLM 答 | (instruction, response) |

适用模型族（§2.1 / App.A）：Llama-3 / 3.1、Qwen2、Gemma-2、Phi-3 等开源 chat。

### 3.3 扩展（§2.2）——本篇只记接口，不展开损失

| 扩展 | 机制（文内） |
|---|---|
| **Filtering** | 八类指标可组合（App.C）：Input/Output Length、Task Category、Input Quality、Input Difficulty、Min Neighbor Distance、Reward $r_*$、Reward Difference $r_*-r_{\mathrm{base}}$；表 5 给 6 套现成 Filter（如 Air Filter：≥good、≥medium、邻域距离>0、$r_*-r_{\mathrm{base}}>\tau_2$，再取最长输出） |
| **Magpie-MT** | 每轮末再接 pre-query；8B 易「忘了自己是 user」→ 用 system prompt 锁角色（Fig.14） |
| **Magpie-DPO** | 先筛高质量多样指令；对每条以 $T=0.8$ 采样 $k=5$ 条响应；RM 打分，最高=chosen、最低=rejected（文用 ArmoRM-Llama3-8B-v0.1） |
| **Domain / Multilingual** | 用 **system prompt** 控任务域与语言（Fig.2：数学 / 中文）；或直接对专用 code/math 模型跑 Magpie |

### 3.4 数据集产物与成本（§3）

| 数据集 | 生成器 | 规模（文） | 算力/成本要点 |
|---|---|---|---|
| **Magpie-Air** | Llama-3-8B-Instruct | 原文造 **3M**；评测常用 **300K** Raw/Filtered | Step1 **1.55h** + Step2 **50h**（4×A100-80GB + vLLM bf16）；约 **206 GPU hours**；云端约 **$0.12 / 1k** |
| **Magpie-Pro** | Llama-3-70B-Instruct | 原文造 **1M**；评测常用 **300K** | Step1 **3.5h** + Step2 **150h**；约 **614 GPU hours**；约 **$1.1 / 1k** |
| **Magpie-*-DPO** | 同上 + ArmoRM | 各 **100K**（$k=5,T=0.8$） | — |
| **家族合计（App.A）** | 多骨干 | 称 **>11.4M** 指令-响应对（含 Qwen2 / Gemma-2 / Phi-3 / Llama-3.1 等变体） | 无人工写题、无 GPT-4 API |

**属性分析（§3.2，跟读）：**
- 任务类：Pro 上一半以上为 **information seeking**，其次 creative writing / advice / planning / math。
- 质量：Llama-3-8B-Instruct 五档打分；多数 ≥ average，**Pro > Air**。
- 难度：两集分布相近；Pro 略多难题。
- 相似性：mpnet 嵌入 + FAISS 最小邻域距离去重。
- 响应质量：FsfairX-LLaMA3-RM-v0.1；看 $r_*-r_{\mathrm{base}}$（base 用 URIAL elicitation）。
- **安全（§3.3）：** Llama-Guard-2 → **潜在有害 <1%**；过滤可去。

### 3.5 公开评测字段（只录表内数字）

#### Table 1（Llama-3-8B base；AlpacaEval 2 + Arena-Hard）

| Alignment Setup | #Convs | AE2 LC (GPT-4-Turbo) | AE2 WR | AE2 LC (Llama-3-8B-Inst ref) | AE2 WR | Arena-Hard WR |
|---|---:|---:|---:|---:|---:|---:|
| UltraChat SFT + UltraFeedback DPO | 208K+64K | 18.36 | 17.33 | 44.42 | 42.36 | 14.8 |
| Magpie-Air-300K-Raw SFT | 300K | 21.99 | 21.65 | 48.63 | 48.06 | 15.8 |
| Magpie-Air-300K-Filtered SFT | 300K | 22.66 | 23.99 | 49.27 | 50.8 | 14.9 |
| + Magpie-Air-DPO | +100K | **45.48** | **50.43** | **75.06** | **79.64** | **35.9** |
| Magpie-Pro-300K-Filtered SFT | 300K | 25.08 | 29.47 | 52.12 | 53.43 | 18.9 |
| + Magpie-Pro-DPO | +100K | **50.10** | **53.53** | **78.52** | **80.82** | **35.7** |
| Llama-3-8B-Instruct（官方 SFT+DPO） | >10M | 22.92 | 22.57 | 50 | 50 | 20.6 |

文内主张（§4.2，跟读）：
- **仅 SFT Magpie** 可超过「UltraChat SFT + UltraFeedback DPO」；
- Magpie SFT 在 AE2（以 Llama-3-8B-Instruct 为 ref）上 LC 可 **>50%**（偏好自家 SFT 胜过官方 Instruct）；
- Magpie + DPO 后 AE2 相对 GPT-4-Turbo(1106) LC 可到 **50.10**（文称可超过该裁判基线）；全程用数据 **≤约 400K**，对照官方 **>10M**。

#### Table 2（Qwen 骨干 + Magpie-Pro-300K-Filtered）

| | AE2 LC vs GPT-4-Turbo | AE2 LC vs 官方对齐模型 |
|---|---:|---:|
| Qwen2-1.5B-Instruct | 3.91 | 50 |
| Base + Magpie | 3.48 | **56.66** |
| Qwen1.5-4B-Chat | 5.89 | 50 |
| Base + Magpie | **9.1** | **68.09** |
| Qwen1.5-7B-Chat | 14.75 | 50 |
| Base + Magpie | **15.10** | 46.28（WR 58.53） |

#### Table 3（Open LLM Leaderboard 子集；Llama-3-8B base SFT）

| Setup | MMLU(5) | GSM8K(5) | Average |
|---|---:|---:|---:|
| Magpie-Air-300K-Filtered | 64.45 | 52.24 | 62.25 |
| Magpie-Pro-300K-Filtered | 64.25 | 47.92 | 61.58 |
| **Magpie-Pro-Mix-Filtered**（+150K math/code/reasoning booster） | 65.65 | **63.08** | **64.21** |
| Llama-3-8B-Instruct | 67.82 | 71.72 | 66.13 |

文承认：原生 Magpie 推理向偏弱 → 用 §2.2 域控合成 **150K booster** 混入后 GSM8K 明显回升；Mix 称进 Open LLM 相关 **top-3**（同设定叙述）。

#### App.B MagpieLM（<10B 对照，文内图）

MagpieLM-8B-Chat：AlpacaEval 2 LC **58.18** / Arena-Hard **48.4** / WildBench **44.72**（高于文内列出的 Gemma-2-9b-it、Llama-3.1-8B-Instruct 等）。

---

## 四、流水线 B：ActiveUltraFeedback（2603.09692）

### 4.1 问题形式化（§3–4）

- 偏好数据 $D=\{(x_i,y_i^+,y_i^-)\}$；Bradley-Terry：$p(y^+\succ y^-|x)=\sigma(r(x,y^+)-r(x,y^-))$。
- 标准 RLHF/DPO 把 $D$ 当 **静态** 产物；本文把选对建成 **contextual dueling bandit**：prompt=context，两臂=两条候选响应。
- 用奖励的 **UCB/LCB**（§3 Eq.3–4）驱动 acquisition。

### 4.2 五步批循环（Fig.2 / §4）

对 prompt 集 $P$ 分批，直至处理完：

1. **Response Generation**：$m=30$ 开源 LLM、**12** 家族（Qwen2.5/3、Llama3、Gemma3、SmolLM2 等，App. Table 3）；仿 UltraFeedback，每 prompt–LLM 随机抽一条原则（helpfulness / truthfulness / honesty）以增多样性。
2. **Reward Prediction**：**ENN**（Osband et al.；共享冻结 backbone + 浅层 MLP 集成）→ 均值 $r_\phi$、标准差 $\sigma_\phi$；$r\pm\beta\sigma$。
3. **Response Pair Selection**：见下表（Table 1）。
4. **Preference Annotation**：**LLM judge** 对四维（truthfulness / instruction following / honesty / helpfulness）各 1–5 分，均值高者为 preferred（§4.4；目标是可复现的大规模对照，非宣称完全替代人类）。
5. **Reward Model Training**：用累计 $D$ 更新 ENN，供下一批。

### 4.3 选对方法族（Table 1）——跟读口诀

| 族 | 方法 | 每 prompt 需 judge 的响应数 | 直觉 |
|---|---|---:|---|
| **被动启发式** | Random | 2 | 均匀抽一对 |
| | MaxMin | **m**（整池） | judge 全池后取最高+最低 |
| | UltraFeedback 式 | 4 | 随机 4 条，最高 vs 余下随机一条 |
| | **DeltaQwen**（DLH） | **0**（无 judge） | 固定 Qwen3 **0.6B vs 32B**，大模型当 preferred |
| **Dueling bandit** | InfoMax | 2 | 最大化 UCB−LCB（纯探索） |
| | DTS | 2 | 双 Thompson：两独立后验样本各取最大 |
| | MaxMin-LCB | 2 | 先选对他人 LCB 最优者，再选对其 LCB 最差者 |
| **本文 Active Delta†** | **DRTS** | 2 | **双反向** Thompson：一条取后验最大、一条取后验最小 → 故意拉大质量差，仍保留随机探索 |
| | **DeltaUCB** | 2 | $\arg\max_{j\neq j'} \bar p_\phi(y_j\succ y_{j'})$：乐观意义下质量差最大的一对 |

**Delta Learning Hypothesis（文引 Geng et al. 2025）跟读：** 绝对质量不如 **相对质量差（delta）**；清晰边界比「两强互搏」噪声更低。DRTS/DeltaUCB 把该洞见嵌进不确定度 acquisition，且不锁死单一模型族。

### 4.4 实验设置（§5.1）

| 项 | 文内设定 |
|---|---|
| 主 prompt 源 | `allenai/ultrafeedback_binarized_cleaned` |
| 评测初始化 | `allenai/Llama-3.1-Tulu-3-8B-SFT` |
| 下游 | GSM8K、IFEval、TruthfulQA、AlpacaEval 2；报相对 base 的 **Δ**；Mean 为四者平均 |
| 奖励建模 | 独立 BT 奖励模型 → **RewardBench 2**（与环内 ENN 分离） |
| 显著性阈值（文） | 下游 ≥ **0.008**；RewardBench 2 ≥ **0.02** |
| 样本效率叙述 | 摘要/贡献：可比或更优，标注量可低至静态基线的 **约 1/6**；每 prompt **单次** pairwise |

### 4.5 公开评测字段（Table 2；相对 Tulu-3-8B-SFT base）

Base 绝对分：GSM8K **0.758** / IFEval **0.713** / TruthfulQA **0.468** / AlpacaEval 2 **0.083** / Mean **0.506** / RewardBench 2 **0.290**。

| Method | GSM8K Δ | IFEval Δ | TruthfulQA Δ | AlpacaEval 2 Δ | Mean Δ | RewardBench 2 Δ |
|---|---:|---:|---:|---:|---:|---:|
| Original UltraFeedback 对 | +0.039 | +0.025 | +0.055 | +0.030 | +0.037 | +0.295 |
| Random | +0.024 | +0.028 | +0.056 | +0.077 | +0.046 | +0.278 |
| UltraFeedback 启发式 | +0.037 | −0.001 | +0.039 | +0.072 | +0.036 | +0.287 |
| MaxMin | +0.022 | −0.016 | +0.150 | +0.289 | +0.111 | +0.318 |
| DeltaQwen | **+0.055** | +0.047 | +0.130 | **+0.316** | **+0.137** | +0.100 |
| InfoMax | +0.011 | +0.019 | +0.018 | +0.020 | +0.016 | +0.297 |
| DTS | +0.011 | +0.034 | +0.013 | +0.037 | +0.023 | +0.224 |
| MaxMin-LCB | +0.015 | +0.017 | +0.006 | +0.027 | +0.016 | +0.230 |
| **DRTS†** | **+0.055** | **+0.050** | **+0.143** | +0.259 | +0.127 | +0.312 |
| **DeltaUCB†** | +0.040 | +0.025 | +0.137 | +0.281 | +0.120 | **+0.339** |

**文内读表要点（§5.2–5.3，跟读）：**
- **DRTS / DeltaUCB**：下游与奖励建模 **双强**；可超过 Original UltraFeedback 对。
- **DeltaQwen**：DPO 下游 Mean 略高（+0.137），但 **RewardBench 2 很弱（+0.100）**——归因于锁在 Qwen 族训练分布、多样性不足。
- 经典 **DTS / MaxMin-LCB**：理论目标是找「好回答」，常变成 **两强对比** → 监督信号弱，甚至不如 Random。
- **样本效率（Fig.3a）：** DRTS/DeltaUCB 在约 **5k–10k** 样本上即可超过 Random/UltraFeedback 启发式在 **60k** 上的下游表现（「约六分之一」叙述的实验锚点）。
- **奖励建模（Fig.3b）：** 更慢饱和；约 **40k** 才接近全量静态；Random 因多样性在 RM 上意外不差。

### 4.6 泛化消融（只记结论轴）

| 消融 | 设定 | 结论（文） |
|---|---|---|
| **§5.4 Prompt 源** | UltraFeedback；Skywork-Reward-Preference-80K-v0.2；Combined(~140k)；Tulu-3 Preference Mixture(~272k) | Fig.4：DRTS/DeltaUCB 跨源稳定优于启发式；DeltaQwen 仍偏 AE2、弱 RM |
| **§5.5 优化算法** | DPO → **IPO**、**SimPO** | Fig.5：DRTS/DeltaUCB 仍高样本效率；**DeltaQwen 在 IPO/SimPO 上明显掉队**（多样性不足） |
| 局限（§6） | 当前实现对全 prompt 预计算响应与 judge 分以便大规模 ablation | **标注效率**主收益；生成侧算力仍重；未来优先「先选该问哪几个模型」 |

---

## 五、两文合读：合成对齐数据的分工

| 维度 | Magpie | ActiveUltraFeedback |
|---|---|---|
| **主要产出** | 指令–响应对（可扩 MT / DPO 对） | 在给定 prompts 上的 **chosen–rejected** 对 |
| **是否需要外部 prompt 库** | **不需要**（自造 instruction） | **需要**（UltraFeedback / Skywork / Tulu-3 …） |
| **是否需要多模型池** | 单对齐模型即可闭环；DPO 扩展用 RM 打分 | **30 模型池** 是多样性前提 |
| **相对 UltraFeedback** | 可替代「从哪来指令」；Magpie-DPO 是另一条造偏好路径 | **升级「怎么选对」**：静态启发式 → 主动/delta |
| **本仓库下游消费** | SFT 数据质量故事 | 偏好数据 **标注预算** 故事 |
| **明确不写** | 不写成预训练教科书合成（B8） | 不写成 SimPO/ORPO 损失精读（[[SimPO与ORPO偏好优化]]） |

**跟读口诀：** Magpie =「对着 chat 模板空手变出用户题」；ActiveUF =「题已有、答案很多，用不确定度+质量差挑最值得标的一对」。

---

## 六、与相邻笔记的边界（再钉一次）

| 笔记 | 本篇不进入 |
|---|---|
| **B8** | phi / textbook / 代码合成 **预训练向** 数据 |
| **[[SimPO与ORPO偏好优化]]** | SimPO / ORPO / IPO **目标函数** 推导；此处 IPO/SimPO 只作 ActiveUF 消融消费者 |
| **[[对齐脉络RLHF与偏好优化]]** | RLHF–DPO–CAI 通史与损失精读 |
| **B3** | 网页过滤 / FineWeb–DCLM 策展 |
| **[[NemotronCC数据策展]]** | Nemotron-CC 长程预训练数据管线（并行数据侧，非本篇） |

---

## 七、可跟读清单（中文）

1. Magpie Step1 只喂 **user 头模板**，模型自己吐 **用户问题**；Step2 再按正式模板生成回答。
2. Magpie **无 seed、无提示工程**；过滤看质量/难度/邻域距离/奖励差；可扩多轮、DPO、域控与多语。
3. Magpie-Pro-300K-Filtered 仅 SFT，在 AE2/Arena-Hard 上可压过「UltraChat+UltraFeedback DPO」；再加 Magpie-DPO 后 AE2 LC（对 GPT-4-Turbo）到 **50.10**。
4. ActiveUF 五步：**多模型生成 → ENN 估 r±σ → 选对 → Judge → 更新 ENN**。
5. 记住两个新方法：**DRTS**（一高一低后验采样）、**DeltaUCB**（乐观质量差最大）；都只要 **2** 条进 judge。
6. DeltaQwen 省标注但 **RM 差、换 IPO/SimPO 易崩**；DRTS/DeltaUCB 追求 **下游+RM 双线** 与 **约 1/6 标注** 效率。
7. 本篇是 **对齐数据怎么造/怎么挑**，不是损失怎么写，也不是网页怎么滤。

---

## 八、来源与核验

| 项 | 路径 / 标识 |
|---|---|
| Magpie PDF | `https://arxiv.org/abs/2406.08464`（32 页，v2，2024-10-08 CST） |
| ActiveUF PDF | `https://arxiv.org/abs/2603.09692`（40 页，v2） |
| 文本抽取 | · `activeultrafeedback.txt`（2026-09-22 CST） |
| arXiv API | 2406.08464v2；2603.09692v2（查询 2026-09-22） |

**未覆盖（有意）：** Magpie 附录全部 filter 消融表、生成温度对难度的细曲线；ActiveUF 全部 GPU-hour 表与种子稳定性数值表——需要时回 PDF App.F/G，不在本卡扩写。

## 相关笔记

- [[DiffusionForcing族|Diffusion Forcing]]
- [[WorfBench工作流基准|WorfBench]]
- [[合成对齐数据Magpie|Magpie / ActiveUltraFeedback]]
- [[EntMTP熵引导投机解码|EntMTP]]
- [[DuoAttention与KVzip|DuoAttention / KVZip]]

