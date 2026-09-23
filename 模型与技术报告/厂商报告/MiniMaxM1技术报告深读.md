---
title: MiniMax-M1 Technical Report 专项深读卡
topic: TR-MiniMax-M1
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2506.13585
archived: 2026-09-22
---

# MiniMax-M1 Technical Report 专项深读卡

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：MiniMax, *MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention*（arXiv:2506.13585）
> 官方 PDF：`https://arxiv.org/abs/2506.13585`（**22** 页 A4）
> 本卡边界：数字与机制一律取自本 PDF 正文/表；**禁止**补 Text-01 未在本报告复述的层宽/隐层维等细节。对照增量旁及 **[[推理时扩展TestTimeScaling]]**（test-time scaling）、**[[长上下文位置编码与系统侧]]**（长上下文）、**[[AI基础设施总览]]**（AI Infra）、**[[注意力效率族MQA到MLA]]**（attention efficiency）。

---

## 一、报告元信息

| 字段 | 核实值 | 出处 |
|---|---|---|
| 标题 | MiniMax-M1: Scaling Test-Time Compute Efficiently with Lightning Attention | 封面 |
| 作者 | MiniMax（PDF 元数据 Author 字段列完整贡献者名单；附录 A. Contributors） | 封面；§A |
| 通信 | model@minimax.io | 封面脚注 |
| arXiv 页眉 | **arXiv:2506.13585v1** \[cs.CL\] **16 Jun 2025** | PDF 第 1 页页眉 |
| PDF 页数 | **22** | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:) | |
| HTML / PDF | https://arxiv.org/abs/2506.13585 ；https://arxiv.org/pdf/2506.13585 | arXiv |
| 权重 / 代码 | https://github.com/MiniMax-AI/MiniMax-M1 ；正文称亦上 Hugging Face；已支持 **vLLM** 与 **Transformers**；商业 API：minimax.io | Abstract；§1 末 |
| 系列定位 | 自称「world’s first **open-weight, large-scale hybrid-attention reasoning model**」；基于前作 **MiniMax-Text-01**（MiniMax et al., 2025）做 continual pretrain + SFT + 大规模 RL | Abstract；§1 |
| 发布变体 | **MiniMax-M1-40k** 与 **MiniMax-M1-80k**（thinking budget / 最大生成长度）；40k 为 80k 训练的中间阶段 | Abstract；§1；§5 |
| 版权行 | © 2025 MiniMax. All rights reserved | 封面 |

**摘要级一句话（不外推）：**
MiniMax-M1 = **hybrid MoE + Lightning Attention**（继承 Text-01：456B 总参 / 45.9B 激活 / 32 experts）+ 原生 **1M** 上下文 + **CISPO** RL，在 **512×H800、约三周、$534,700** 租金下完成全量 RL，并放出 40K / 80K thinking budget 两档开源权重。

---

## 二、架构 / 规模 / 训练对照表（仅报告数字）

### 2.1 规模与注意力结构（Abstract；§1）

| 项 | 报告值 |
|---|---|
| 总参数 | **456B**（继承 MiniMax-Text-01） |
| 每 token 激活参 | **45.9B** |
| MoE 专家数 | **32** experts |
| 注意力混合比 | 每 **7** 个带 lightning attention 的 **TransNormer** block（Qin et al., 2022a）后接 **1** 个带 **softmax attention** 的 transformer block |
| Lightning Attention | Qin et al., 2024b；正文称其为 linear attention 变体（Qin et al., 2022a）的 **I/O-aware** 实现 |
| 原生上下文 | 输入最长 **1M** tokens（相对 DeepSeek R1 称 **8×**） |
| 最大生成 / thinking budget | **40K**（中间阶段）与 **80K**（最终发布档） |
| 相对 DS-R1 推理 FLOPs（理论，Figure 1 Right） | 生成长 **64K**：**<50%** FLOPs；**100K**：约 **25%** FLOPs |

> 本报告**未**另列 hidden dim、层数、GQA/MLA、专家 intermediate 等细表；上述规模字段均写为「developed based on MiniMax-Text-01」。细结构需回查 Text-01 报告 → 见第四节待核实。

### 2.2 输入/输出长度对照（Table 1）

| 模型 | Max Input | Max Output |
|---|---:|---:|
| o3 | 200K | 100K |
| Gemini 2.5 Pro | 1M | 64K |
| Claude 4（表注：Claude-4-Opus） | 200K | 32K |
| DS-R1（表注：DeepSeek-R1-0528） | 128K | 64K |
| Qwen3-235B | 128K | 32K |
| **MiniMax-M1-80k** | **1M** | **80K** |

### 2.3 训练流水线总览（§2–§5；Abstract）

`
MiniMax-Text-01 base
 → Continual Pretraining（+7.5T tokens；STEM/code/book/reasoning 占比提至 ~70%；四阶段上下文 32K→1M）
 → SFT cold-start（长 CoT；math+coding ≈60%）
 → RL（CISPO + hybrid-attention 配方；先 40K 输出上限，再分阶段扩到 80K）
`

| 阶段 | 报告要点 | 出处 |
|---|---|---|
| Continual PT 数据量 | 额外 **7.5T** tokens；reasoning-intensive、精心筛选；**严格避免 synthetic data**；优先抽取自然 QA；QA 做 semantic dedup | §2.1 |
| Continual PT 配比 | STEM / code / book / reasoning-related 提升至 **70%** | §2.1 |
| Continual PT 优化 | 降低 MoE auxiliary loss 系数；调整并行策略以增大 micro batch；**constant LR 8e-5 × 2.5T**，再 **decay 5T → 8e-6** | §2.1 |
| 长上下文扩展 | **四阶段**平滑扩展：自 **32K** 起最终训到 **1M**；动机：hybrid-lightning 过激进拉长易梯度爆炸（早层 decay 慢、偏局部，赶不上后层） | §2.1 |
| SFT | 注入 reflection-based 长 CoT；域：math / coding / STEM / writing / QA / multi-turn chat；math+coding ≈ **60%** | §2.2 |
| RL 算力与成本 | **512 H800**；完整 RL 周期 **3 weeks**；租金约 **$534,700**（正文亦写 ≈ **$0.53M**） | Abstract；§1；§3 开篇 |
| RL 算法 | **CISPO**（Clipped IS-weight Policy Optimization）：clip **importance sampling weight**，而非 PPO/GRPO 式 token update clip；采用 GRPO 式 group-relative advantage + token-level loss | §3.1 |
| CISPO 受控消融 | 在 **Qwen2.5-32B-base** + Yu et al. (2025) 数学数据上：同 step 优于 GRPO/DAPO；达 DAPO 同等表现约用 **50%** steps（正文亦称相对 DAPO **2×** speedup） | §3.1；Figure 2 |
| RL 优化器 | **AdamW**：$\beta_1=0.9$, $\beta_2=0.95$, **eps=1e-15**（相对 VeRL 默认 0.999 / 1e-8；因梯度量级跨 1e-18～1e-5、多数 \<1e-14） | §3.2 |
| Train/Infer 对齐 | LM output head 提到 **FP32**，使 train/infer token 概率相关从约 0.9x → **0.99x**（Figure 3） | §3.2 |
| 病理重复截断 | 连续 **3,000** 个 token 概率均 **>0.99** → early truncation | §3.2 |
| 40K→80K 扩窗 | 分阶段：**40→48→56→64→72→80K**；用 40K 模型滤难例、下调 synthetic、监控 PPL / P99 长度再升窗；并加 sample-level loss + token-level norm、降低 grad clip 与 $\epsilon^{IS}_{high}$ | §5 |

### 2.4 RL 数据规模（§4）

| 类别 | 规模（报告） | 奖励 | 备注 |
|---|---|---|---|
| Mathematical Reasoning | 近 **50K** | 规则正确性 + format | 去重、与 SFT/基准防泄漏；pass@10 ∈ (0, 0.9) |
| Logical Reasoning | 约 **53K**；**41** 类任务 | SynLogic 任务专用规则 verifier | 难度上下界用强模型 / Text-01 的 pass@10 约束 |
| Competitive Programming | **30K** | 规则 / 测试套件 | 缺测例时用 Text-01 工作流合成 |
| Software Engineering | **several thousand** | sandbox 执行 pass/fail | 自 GitHub issues/PRs；容器化执行 |
| General domain | **25K** | GenRM（有 GT：五档；无 GT：pairwise −1/0/1） | STEM/事实 + IF/创意写作等；在线监控长度偏见 |

**课程（§4.3）：** 先只训 rule-based reasoning，再逐步混入 general-domain，避免专长灾难性遗忘。

---

## 三、公开亮点（长上下文 / 推理 / Agent，据报告）

### 3.1 长上下文（Table 1–2；§6.1）

- 原生 **1M** 输入 + **80K** 输出（开源 LRM 中自称领先一档）。
- **OpenAI-MRCR (128k)**：M1-40k **76.1** / M1-80k **73.4**（同表 o3 56.5；Claude 4 Opus 48.9；Gemini 2.5 Pro 76.8）。
- **OpenAI-MRCR (1M)**：M1-40k **58.6** / M1-80k **56.2**（同表仅 Gemini 2.5 Pro 有 **58.8**；多数对照为 —）。
- **LongBench-v2**：M1-40k **61.0** / M1-80k **61.5**（相对多数开源对照更高；Gemini 2.5 Pro 65.0）。
- 作者自评：长上下文理解超过 o3 / Claude 4 Opus，全球第二、仅略逊 Gemini 2.5 Pro（§6.1 Highlights）。

### 3.2 推理与 test-time scaling（Abstract；§5–§6.2；Figure 4）

- 产品叙事：hybrid-attention 使 test-time compute **近线性**扩展（Figure 1 Right）。
- 两档 thinking budget：**40K** → **80K**；80k 在多数复杂数学/编码上优于 40k。
- Table 2 摘录（M1-80k）：AIME 2024 **86.0**；AIME 2025 **76.9**；MATH-500 **96.8**；LiveCodeBench (24/8∼25/5) **65.0**；GPQA Diamond **70.0**；ZebraLogic **86.8**。
- Figure 4：RL 过程中 AIME / LiveCodeBench 准确率与平均生成长度同步上升；AIME/LiveCodeBench 平均响应长度可超 **20K**；文中示例 AIME 2024 从约 **68%→80%**（训练曲线叙述）。

### 3.3 软件工程 / 工具使用（§4.1；§6.1；Table 2）

- RL 含 SWE-bench 风格 **execution-based sandbox**。
- **SWE-bench Verified**（Agentless scaffold + 两阶段定位、无 embedding 检索）：M1-40k **55.6** / M1-80k **56.0**（DS-R1-0528 57.6；显著高于其他多数开源列）。
- **TAU-bench**：airline M1-80k **62.0**；retail M1-40k **67.8** / M1-80k **63.5**。作者称 M1-40k 在 agentic tool-use 上超过所有开源对照乃至 Gemini 2.5 Pro（airline/retail 需分列阅读 Table 2）。

### 3.4 Infra / RL 可复用配方要点（架构思想 × AI Infra 交汇）

| 问题 | 报告解法 | 出处 |
|---|---|---|
| Softmax 二次代价阻碍长 thinking | Hybrid：**7× lightning (linear) + 1× softmax** | §1 |
| GRPO/PPO clip 掉低概率「反思 fork」token | **CISPO**：clip IS weight，保留全部 token 梯度 | §3.1 |
| Train/infer 概率漂移导致 reward 不涨 | LM head **FP32** | §3.2 |
| Adam 默认超参不收敛 | $\beta_2=0.95$, **eps=1e-15** | §3.2 |
| 长重复响应炸梯度 | 连续 3k token p>0.99 截断 | §3.2 |
| 扩窗后期 pattern collapse / 负样本偏长 | 早停重复 + sample-level loss & token-level norm + 降 clip/$\epsilon^{IS}_{high}$ | §5 |
| GenRM 偏好更长 CoT | 在线监控长度偏见并重标定 GenRM；辅以 reward shaping / value clip / 归一化 | §4.2.2 |

---

## 四、待核实与引用

### 4.1 本 PDF 未给出 / 需外查

| 缺口 | 说明 |
|---|---|
| Text-01 细结构 | 层数、hidden、专家 intermediate、共享专家与否、路由 top-k、归一化等——本报告只给 456B / 45.9B / 32 experts / 7:1 hybrid 比 |
| 预训练至 Text-01 的原始 token 量与集群 | 本报告只覆盖 **continual** +7.5T 与 RL 段 512×H800 |
| CISPO 在 M1 本体上的完整超参表 | $\epsilon^{IS}_{high/low}$、group size $G$、off-policy 轮数等仅有叙述与 Qwen2.5-32B 消融，无 M1 全表 |
| FLOPs 曲线假设 | Figure 1 Right 为 **theoretical inference FLOPs**；实现侧 kernel / 显存带宽未在本报告量化 |
| 评测脚手架细节 | SWE-bench 两阶段定位、TAU-bench 系统 prompt / GPT-4.1 user model、HLE 标 `*` 为 text-only subset——复现需对照原文脚注与外部仓库 |
| 许可 SPDX | 封面 © 2025 MiniMax；具体权重 license 以 GitHub/HF 页面为准（本 PDF 未写 SPDX 字符串） |
| arXiv 后续版本 | 本卡仅跟读 **v1 / 16 Jun 2025**；若有 v2+ 需重抽 |

### 4.2 关键引用（报告内）

- Qin et al., 2022a / 2024b — TransNormer / Lightning Attention
- Shao et al., 2024 — GRPO
- Yu et al., 2025 — DAPO（及 CISPO 消融所用数学数据）
- Schulman et al., 2017 — PPO
- Jimenez et al., 2024 — SWE-bench
- Liu et al., 2025a — SynLogic
- Yao et al., 2025 — TAU-bench
- OpenAI, 2024b — OpenAI-MRCR
- Bai et al., 2024 — LongBench-v2
- MiniMax et al., 2025 — MiniMax-Text-01（底座）

### 4.3 跟读指针（本仓库）

- **[[推理时扩展TestTimeScaling]]** test-time scaling / LRM 叙事
- **[[长上下文位置编码与系统侧]]** 长上下文方法谱系（与 1M 窗口对照）
- **[[注意力效率族MQA到MLA]]** attention efficiency（linear / sparse / hybrid）
- **[[AI基础设施总览]]** AI Infra（并行、RL 训练栈；本报告点名 VeRL 默认超参作反例）
- **[[DeepSeekR1推理训练深读]]** / **[[Qwen3技术报告深读]]** — 同档开源推理模型配方对照

---

*抽取工具： + 。所有数字与机制主张均可回指本 PDF 对应节/表；未在正文出现的规格一律不补。*

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[DeepSeekV32技术报告深读|TR DeepSeek-V3.2]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[GPT5SystemCard|TR GPT-5]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[KimiK2技术报告深读|TR Kimi K2]]
- [[GLM45技术报告深读|TR GLM-4.5]]
- [[MiniMaxM1技术报告深读|TR MiniMax-M1]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[混合专家架构|MoE]]
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[AI基础设施总览|AI Infra]]

