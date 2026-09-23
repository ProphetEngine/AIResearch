---
title: DeepSeek-R1 推理训练专项深读（训练管线与奖励/算法）
topic: TR-DeepSeek-R1
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
archived: 2026-09-22
---

# DeepSeek-R1 推理训练专项深读（技术报告级）

> 攻坚线：**架构思想（主）** + **数学原理（辅）**
> 锚点材料：DeepSeek-AI, *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning*（arXiv:2501.12948；本仓库 PDF `https://arxiv.org/abs/2501.12948`，抽取页眉为 **v2 / 2026-01-04**）
> **本笔记聚焦报告中的训练管线、奖励设计与公开算法形式**；test-time scaling「势」叙事、与 o1 对照的产品轴见 **[[推理时扩展TestTimeScaling]]**，此处不重复。
> 只据 PDF 已读内容写要点；未在原文出现的超参、未核对的外部复现一律标「待核实」或不写。

---

## 一、报告元信息

| 项 | 内容（据 PDF） |
|---|---|
| 标题 | DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning |
| 作者机构 | DeepSeek-AI；通讯 `research@deepseek.com` |
| 标识 | arXiv:**2501.12948**（抽取文本页眉：**v2 [cs.CL] 4 Jan 2026**） |
| 本地路径 | `https://arxiv.org/abs/2501.12948`（约 86 页） |
| 核心主张（摘要） | LLM 推理能力可通过**纯强化学习**激励，**无需人类标注的推理轨迹**；RL 框架促进自我反思、验证、动态换策略等行为涌现；涌现出的推理模式可再系统蒸馏到更小模型 |
| 底座 | DeepSeek-**V3-Base**（R1-Zero / R1 冷启动起点；Supplementary A.1） |
| 产品线 | **DeepSeek-R1-Zero**（无 SFT 直接 RL）→ **DeepSeek-R1**（多阶段：冷启动 SFT + RL + 拒绝采样 SFT + 二次 RL）→ **Distill-*** 开源小模型系列 |
| 权重入口 | 报告写明发布于 `https://huggingface.co/deepseek-ai`（§1） |
| 公开训练成本量级（Table 7，H800 GPU hours，租金假设 $2/GPU·h） | R1-Zero **101K**；SFT 数据制备 **5K**；R1 **41K**；合计 **147K**（约 **$294K**） |

**跟读抓手：** 报告把「会想」拆成两条可复述路径——(A) 可验证任务上的 **outcome 规则奖励 + GRPO**；(B) 为可读性/通用偏好再叠 **冷启动与神经奖励**。本笔记按 (A)→(B)→蒸馏展开。

---

## 二、R1-Zero → R1 管线对照表（阶段、数据、奖励）

依据 **Figure 2**、**§2–§3**、**Table 3**、**Supplementary B.3**。中间检查点命名：R1-Dev1 / Dev2 / Dev3（Figure 2 注）。

### 2.1 总览表

| 阶段 / 产物 | 起点 | 数据（公开口径） | 训练方式 | 奖励 / 信号 | 主要目的（报告表述） |
|---|---|---|---|---|---|
| **DeepSeek-R1-Zero** | V3-Base | 推理 RL 数据（数学/代码/STEM/逻辑；Table 4） | **仅 GRPO RL**，**跳过 SFT**（§2） | **规则**：`Reward_rule = Reward_acc + Reward_format`（式 4）；**不用**神经 RM（§2.2） | 观察无人类轨迹约束下的自发长 CoT / 反思涌现 |
| **冷启动数据制备** | 自 R1-Zero 采样等 | 「thousands」级会话式、第一人称长 CoT（§3；B.3.2） | 人工改写风格 + LLM 扩写 + 二次人工校验；过滤正确性与可读性 | 非 RL；质量过滤（正确最终答案、可读格式、语言一致等） | 产品体验：可读、少混写；作者强调属工程启发式，≠「真有人类智能」（B.3.2） |
| **R1-Dev1** | V3-Base | 上述冷启动数据 | **冷启动 SFT**（2–3 epochs；B.4.2） | 监督学习 | 把策略拉进「可读长思维」分布；Table 3：指令跟随升、AIME 等推理相对 Zero **暂时回落** |
| **R1-Dev2**（第一阶段 RL） | Dev1 | 推理 prompts；并引入非推理侧的语言一致需求 | **GRPO**（§3.2.1） | 规则奖励 + **语言一致性奖励** `Reward_language = Num(Words_target)/Num(Words)`（式 7）；直接加到最终奖励 | 在可读格式上抬推理，并压中英混写 |
| **约 800K SFT 数据** | 自 **第一阶段 RL checkpoint** 拒绝采样 + V3 管线非推理数据 | ~**600k** 推理 + ~**200k** 非推理；Table 5 合计 **804,745** | 拒绝采样保留正确轨迹；混语言/长段/代码块等过滤（B.3.3） | 规则或 generative RM（V3 判对错，Listing 4）；非推理可复用 V3 SFT | 同时强化推理与写作等通用能力 |
| **R1-Dev3** | Dev2 | 上述 ~800k | **第二段 SFT**（B.4.2） | 监督学习 | Table 3：AlpacaEval / Aider 等通用与工程向指标明显抬升 |
| **DeepSeek-R1**（第二阶段 RL） | Dev3 | 推理 + 通用（helpful/harmless）混合 prompts | **GRPO**，共 **1,700** steps；**仅最后 400 steps** 才引入基于偏好的 general 奖励（§3.2.2） | `Reward = Reward_reasoning + Reward_general + Reward_language`（式 8–10）：推理侧仍为规则；通用侧为 **RM + 格式** | 对齐 helpfulness / harmlessness，同时微调推理；防神经 RM **reward hacking**（B.5） |

### 2.2 RL 提示数据量（Table 4 / B.3.1）

| Data Type | # Prompts（Table 4） | Question / Output 类型 |
|---|---|---|
| Math | 26K | 定量推理 → Number / Expression / Equation（**排除证明**：难判对错） |
| Code | 17K（表） | 算法与修 bug → Code；正文另写 17k 竞赛题 **+ 8k** bug-fix（B.3.1，与表口径并读时注意） |
| STEM | 22K | 多选 → Option（物理 15.5% / 生物 30.7% / 化学 46.5% / 其他 7.3%） |
| Logic | 15K | 选择/定量 → Option/Number（含真实题与合成 code-IO、谜题等） |
| General | 66K（表） | Helpfulness / Harmlessness → Ranked Responses；正文另写 helpfulness 66k，**另有 12,000** harmlessness 题（B.3.1） |

数学/STEM 等可验证题：匹配参考答案则 reward **1**，否则 **0**（B.3.1）。

### 2.3 阶段评测快照（Table 3，摘与管线相关的关键列）

| Benchmark | R1-Zero | R1-Dev1 | R1-Dev2 | R1-Dev3 | R1 |
|---|---:|---:|---:|---:|---:|
| AIME 2024 (Pass@1) | 77.9 | 59.0 | 74.0 | 78.1 | **79.8** |
| MATH-500 (Pass@1) | 95.9 | 94.2 | 95.9 | 95.4 | **97.3** |
| IF-Eval (Prompt Strict) | 46.6 | 71.7 | 72.0 | 78.1 | **83.3** |
| ArenaHard | 53.6 | 77.0 | 73.2 | 75.6 | **92.3** |
| AlpacaEval2.0 (LC-winrate) | 24.7 | 50.1 | 55.8 | 62.1 | **87.6** |
| Codeforces (Rating) | 1444 | 1534 | 1687 | 1746 | **2029** |

**管线读法（§4 原文归纳）：** 冷启动抬指令跟随但推理暂降 → 第一段 reasoning RL 把推理拉回/抬高 → 800k 混合 SFT 抬通用与部分工程能力 → 第二段混合 RL 主要涨偏好类基准（文称 AlpacaEval2.0 +25%、ArenaHard +17% 相对 Dev3）。

### 2.4 R1-Zero 训练超参要点（§2.1）

- LR **3e-6**；KL 系数 **β = 0.001**；rollout 温度 **1**
- 每题采样 **G = 16**；最大长度先 **32,768**，**8.2k step** 后升至 **65,536**（文称性能与长度在此步显著跳变）
- 总 **10,400** steps ≈ **1.6** epochs；每 step **32** 题 → batch **512**
- 每 **400** steps 用最新 policy **替换 reference**
- 每次 rollout **8,192** 条输出，切 **16** mini-batch，**仅 1** 个 inner epoch

模板（Table 1）：强制 `<think>...</think>` + `<answer>...</answer>` 结构，**不**注入人类解题内容偏见（§2.3）。

---

## 三、GRPO / 规则奖励等公开算法要点（先直觉后形式）

### 3.1 直觉（§2.1、Supplementary A.3）

- **PPO 路线**：需训与策略同量级的 **value model**，用 GAE 估优势；长 CoT 下「前缀很难预测最终 outcome」，value 难训且贵内存。
- **GRPO 路线**：**同题采一组**回答，用组内奖励的均值/标准差做 **相对优势**，**不训 value model**（Figure 3）。
- **KL 放哪**：GRPO 把无偏 KL 估计 **直接加进损失**（式 1/11）；PPO 常把 per-token KL 当稠密奖励——报告认为后者可能 **隐式惩罚长度**，不利于长思维生长（A.3）。
- **Reference 漂移**：长程训练中 policy 远离初始参考，故 **周期性把 reference 更新为最新 policy**（与 §2.1 的每 400 step 替换一致）。
- **小规模对照**（Figure 4，DeepSeek-Coder-V2-Lite）：PPO 对 GAE 的 λ 敏感；λ=0.95 明显弱于 GRPO，仔细调到 λ=1.0 可接近 GRPO，但仍多 value 成本 → 作者主张大规模长 CoT 场景 **GRPO 更实用**。

### 3.2 形式（§2.1 式 1–3；附录式 11–13 同构）

对每个问题 $q$，从旧策略 $\pi_{\theta_{\mathrm{old}}}$ 采样一组输出 $\{o_1,\ldots,o_G\}$，最大化：

$$
J_{\mathrm{GRPO}}(\theta)
=\mathbb{E}_{q\sim P(Q),\,\{o_i\}_{i=1}^{G}\sim\pi_{\theta_{\mathrm{old}}}(\cdot\mid q)}
\Bigg[
\frac{1}{G}\sum_{i=1}^{G}
\min\Big(
\frac{\pi_\theta(o_i\mid q)}{\pi_{\theta_{\mathrm{old}}}(o_i\mid q)}A_i,\;
\mathrm{clip}\Big(
\frac{\pi_\theta(o_i\mid q)}{\pi_{\theta_{\mathrm{old}}}(o_i\mid q)},\,1-\varepsilon,\,1+\varepsilon
\Big)A_i
\Big)
-\beta\,D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})
\Bigg]
\tag{1/11}
$$

无偏 KL（报告写法）：

$$
D_{\mathrm{KL}}(\pi_\theta\|\pi_{\mathrm{ref}})
=\frac{\pi_{\mathrm{ref}}(o_i\mid q)}{\pi_\theta(o_i\mid q)}
-\log\frac{\pi_{\mathrm{ref}}(o_i\mid q)}{\pi_\theta(o_i\mid q)}
-1
\tag{2/12}
$$

组相对优势：

$$
A_i=\frac{r_i-\mathrm{mean}(\{r_1,\ldots,r_G\})}{\mathrm{std}(\{r_1,\ldots,r_G\})}
\tag{3/13}
$$

出处：主文 **§2.1**；与 PPO 对照 **Supplementary A.3**。GRPO 原论文引用：Shao et al., 2024。

**R1 第一阶段 RL 额外超参（§3.2.1）：** clip ratio $\varepsilon=\mathbf{10}$（文强调 $\varepsilon$ 过小会大量截断梯度、过大则不稳）；其余与 Zero 类似（LR 3e-6、KL 0.001、G=16、max len 32,768、batch 512、每 400 step 换 reference、8192 rollout / 16 mini-batch / 1 inner epoch）。**第二阶段**多数沿用，但温度降为 **0.7**（高温度会导致不连贯生成）。

### 3.3 规则奖励（R1-Zero / 推理域，§2.2）

$$
\mathrm{Reward}_{\mathrm{rule}}=\mathrm{Reward}_{\mathrm{acc}}+\mathrm{Reward}_{\mathrm{format}}
\tag{4}
$$

- **Accuracy**：数学等确定性答案（如 box 格式）规则比对；代码竞赛用编译器 + 预定义测例。
- **Format**：激励把推理包在 `<think>`…`</think>` 内。
- 二者 **等权相加**。
- **明确不做**：推理任务上 **不用** outcome/process **神经奖励模型**——观察其易在大规模 RL 中 **reward hacking**，且重训贵、管线更复杂（§2.2）。

### 3.4 模型奖励（R1 通用偏好，§3.1）

面向「复杂、细腻」的一般数据，沿 DeepSeek-V3 偏好管线：

| 组件 | 公开做法 | 形式 |
|---|---|---|
| **Helpful RM** | arena-hard 式提示（B.2）；V3 生成偏好对；每对询 V3 **4** 次并随机交换 A/B 减位置偏；取均分，仅保留 $\Delta>1$；控制 chosen/rejected 长度可比；**66,000** 对；只看 **最终 summary**（少干预思维过程） | $\mathrm{Reward}_{helpful}=\mathrm{RM}_{helpful}(\mathrm{Response}_A,\mathrm{Response}_B)$（式 5） |
| **Safety RM** | **106,000** prompts + safe/unsafe 标注；**point-wise**（非 pairwise）；评估 **整段**（思维+摘要） | $\mathrm{Reward}_{safety}=\mathrm{RM}_{safety}(\mathrm{Response})$（式 6） |
| 训练超参 | batch 256，LR **6e-6**，**1** epoch；训练 max len **8192**；推理时对 helpful RM **不显式限长** | 架构与 R1 一致 + 标量 reward head |

一般查询归入 safety 或 helpfulness 其一，对应 $\mathrm{Reward}_{General}$。

### 3.5 第二阶段总奖励（§3.2.2）

$$
\mathrm{Reward}
=\mathrm{Reward}_{\mathrm{reasoning}}
+\mathrm{Reward}_{\mathrm{general}}
+\mathrm{Reward}_{\mathrm{language}}
\tag{8}
$$

$$
\mathrm{Reward}_{\mathrm{reasoning}}=\mathrm{Reward}_{\mathrm{rule}},\quad
\mathrm{Reward}_{\mathrm{general}}=\mathrm{Reward}_{\mathrm{reward\_model}}+\mathrm{Reward}_{\mathrm{format}}
\tag{9–10}
$$

- 语言一致性奖励加在 **推理与非推理** 数据上（§3.2.1）。
- Ablation（B.6，在 Distill-Qwen-7B 上）：无 LC 时语言一致性随步数变差；有 LC 则稳定；数学大致持平、**代码略降**——仍保留以换可读性。
- **Reward hacking（B.5 / Figure 6）**：helpful RM 训练过久时，奖励分升而 Codeforces 等表现降 → 故第二阶段仅 **最后 400 / 1700 steps** 引入偏好 RM。

### 3.6 冷启动与 800k 数据的算法侧要点（B.3.2–B.3.3）

**冷启动（B.3.2）：**

1. 收集 thousands 高质量推理 prompts；
2. R1-Zero、温度 **1.0** 多样本生成；
3. 过滤：最终答案正确 + 可读格式（数学用 sympy；去重复、混语言等）；
4. 提示 V3 refinement（含「思维过程译成与问题同语言」）；用 Listing 1 把 Zero 仅含最终答案的 summary 扩成可读题解；
5. 人类先示范「自然会话风」改写，再 LLM 扩写，再人工二校。

**800k SFT（B.3.3 / Table 5）：**

| Domain | Num Samples | Avg Rounds | Avg Tokens |
|---|---:|---:|---:|
| Math | 395,285 | 1.0 | 6094.2 |
| Code | 211,129 | 1.1 | 7435.7 |
| STEM | 10,124 | 1.0 | 4928.8 |
| Logic | 10,395 | 1.0 | 2739.0 |
| General | 177,812 | 1.1 | 1419.8 |
| **Total** | **804,745** | 1.0 | 5355.3 |

备注（原文）：多为单轮，可能限制多轮对话能力；留作未来工作。

---

## 四、蒸馏与开源小模型表（报告数字）

出处：**§1**、**Supplementary F / B.4.3**、**Table 6 / 15 / 16**。

### 4.1 做法（F / B.4.3）

- 用 DeepSeek-R1 相关 **800k** 样本（B.3.3）对开源基座做 **仅 SFT（2–3 epochs）**，**不含 RL**（作者称加 RL 还能再涨，留给社区）。
- max context **32,768**；batch **64**；cosine LR 衰减至初始的 1/10。
- 动机句：更低能耗、更广可及；并称蒸馏自高质量教师输出 **优于** 直接用人类数据训小模型（引 Busbridge et al., 2025 等）。

### 4.2 模型与初始 LR（Table 6）

| Distilled Model | Base Model | Initial LR |
|---|---|---|
| DeepSeek-R1-Distill-Qwen-1.5B | Qwen2.5-Math-1.5B | $1\times10^{-4}$ |
| DeepSeek-R1-Distill-Qwen-7B | Qwen2.5-Math-7B | $8\times10^{-5}$ |
| DeepSeek-R1-Distill-Qwen-14B | Qwen2.5-14B | $7\times10^{-5}$ |
| DeepSeek-R1-Distill-Qwen-32B | Qwen2.5-32B | $6\times10^{-5}$ |
| DeepSeek-R1-Distill-Llama-8B | Llama-3.1-8B | $5\times10^{-5}$ |
| DeepSeek-R1-Distill-Llama-70B | Llama-3.3-70B-Instruct | $2\times10^{-5}$ |

### 4.3 推理基准（Table 15）

| Model | AIME 2024 pass@1 | AIME cons@64 | MATH-500 pass@1 | GPQA Diamond pass@1 | LiveCodeBench pass@1 | CodeForces rating |
|---|---:|---:|---:|---:|---:|---:|
| GPT-4o-0513 | 9.3 | 13.4 | 74.6 | 49.9 | 32.9 | 759 |
| Claude-3.5-Sonnet-1022 | 16.0 | 26.7 | 78.3 | 65.0 | 38.9 | 717 |
| Distill-Qwen-1.5B | 28.9 | 52.7 | 83.9 | 33.8 | 16.9 | 954 |
| Distill-Qwen-7B | 55.5 | 83.3 | 92.8 | 49.1 | 37.6 | 1189 |
| Distill-Qwen-14B | 69.7 | 80.0 | 93.9 | 59.1 | 53.1 | 1481 |
| Distill-Qwen-32B | **72.6** | 83.3 | 94.3 | 62.1 | 57.2 | **1691** |
| Distill-Llama-8B | 50.4 | 80.0 | 89.1 | 49.0 | 39.6 | 1205 |
| Distill-Llama-70B | 70.0 | **86.7** | **94.5** | **65.2** | **57.5** | 1633 |

### 4.4 蒸馏 vs 同规模纯 RL（Table 16 / F.1）

| Model | AIME pass@1 | AIME cons@64 | MATH-500 | GPQA Diamond | LiveCodeBench |
|---|---:|---:|---:|---:|---:|
| QwQ-32B-Preview | 50.0 | 60.0 | 90.6 | 54.5 | 41.9 |
| Qwen2.5-32B-Zero（>10K steps 大规模 RL，B.4.1） | 47.0 | 60.0 | 91.6 | 55.0 | 40.2 |
| **DeepSeek-R1-Distill-Qwen-32B** | **72.6** | **83.3** | **94.3** | **62.1** | **57.2** |

作者两条结论（F.1）：(1) 把更强模型蒸馏进小模型 **又省又强**；小模型只靠文中规模 RL 可能耗算力巨大仍不及蒸馏；(2) 若要推「超越人类先验」的边界，仍可能需要 **更强基座 + 更大规模 RL**。

---

## 五、与 [[推理时扩展TestTimeScaling]] 的增量说明

| [[推理时扩展TestTimeScaling]] 已覆盖（势 / 对照） | 本 TR 增量（训练管线与算法） |
|---|---|
| test-time scaling 主叙事；o1∩R1「RL→长 CoT→可选多样本」骨架 | **不写**势叙事；把 Figure 2 / Dev1–3 / 800k / 两段 RL 写成可对照工程表 |
| R1-Zero「无 SFT + GRPO + 规则奖励」摘要；涌现数字 | Zero **逐步超参**（8.2k 长度跳变、10400 steps、8192 rollout 等）；规则奖励式 (4) 与「禁用神经 RM」动机原文级 |
| R1 四步管线口头列表；语言一致性一句 | **奖励方程组** (5)–(10)；helpful/safety RM 数据量与打分协议；**ε=10**、第二段 1700/末 400 steps、温度 0.7 |
| 蒸馏系列名 +「约 800k、2–3 epoch」 | **Table 5/6/15/16 全表数字**；蒸馏 vs Qwen2.5-32B-Zero 对照与作者两点结论 |
| Table 7 成本在 [[推理时扩展TestTimeScaling]] Infra 表出现 | 此处仅作元信息锚点，不展开 Infra 框架（Figure 5 / B.1 留给 Infra 线） |
| 与 o1「算法未公开 vs GRPO」对照表 | 本笔记给出 **GRPO 目标函数与组标准化优势** 的跟读形式 + A.3 相对 PPO 的三点差异（无 critic / KL 位置 / λ 敏感） |

一句话：**[[推理时扩展TestTimeScaling]] 回答「为何多想一会儿」；本 TR 回答「R1 报告里奖励与阶段具体怎么接」。**

---

## 六、待核实与引用

### 6.1 待核实 / 报告内口径张力

1. **Code RL 数据量**：Table 4 写 Code **17K**；B.3.1 正文写 17k 算法题 **+ 8k** bug-fix——8k 是否计入表内 17K，原文未逐句钉死。
2. **General RL**：表 66K vs 正文「66k helpfulness + 另外 12,000 harmlessness」——合计关系待与官方附录/后续勘误对齐。
3. **冷启动确切条数**：始终为 **thousands**，无更细公开 N。
4. **B.4.2** 英文出现 “code-start SFT” 字样，上下文应为 **cold-start** 笔误（待官方勘误确认）。
5. **arXiv 版本**：官方 PDF 抽取为 **v2 / 2026-01-04**；与首版（常见引用 2025-01）章节/数字若有漂移，复现时应以所读 PDF 页码为准。
6. **未公开而不应编造**：过程奖励具体阈值、完整 RL prompt 全集、价值模型之外的未报告消融、各阶段精确 GPU 拆账（仅有 Table 7 汇总与 B.4.4 叙事小时数）。

### 6.2 报告自述局限（§6，与训练相关者）

- 结构化输出与 **tool use** 仍弱（作者认为不难为结构/工具搭 RL 环境）。
- Token 效率：相对多数票/MCTS，R1 按难度自适应长度，但仍有简单题 **overthinking**。
- 语言混合：主要优化中英；其他语言查询可能仍用英语思维。
- **对 prompt 敏感**；few-shot 一致伤害表现 → 建议 zero-shot 直接述题。
- 软件工程：评测耗时长影响 RL 效率，大规模 RL 未充分覆盖 → 相对 V3 提升有限；未来拟拒绝采样或异步评测。

### 6.3 引用

1. DeepSeek-AI et al. *DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning.* arXiv:2501.12948（本笔记据仓库 PDF v2 抽取）.
2. Shao et al., 2024. *Group Relative Policy Optimization*（报告引用的 GRPO 来源；细节以 R1 文内重述为准）.
3. Schulman et al., 2017. PPO；Schulman et al., 2015. GAE；Ouyang et al., 2022. InstructGPT/RLHF（A.3 对照背景）.
4. 研究会内链：架构/推理时扩展TestTimeScaling.md（势与 o1 对照）；本文件 模型与技术报告/厂商报告/DeepSeekR1推理训练深读.md。

---

*起草说明：数字与公式均回溯自上述 PDF 对应节/表；未做外部榜单二次抓取。*

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[混合专家架构|MoE]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[AI基础设施总览|AI Infra]]

