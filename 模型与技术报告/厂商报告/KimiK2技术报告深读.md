---
title: "技术报告专项：Kimi K2 Technical Report 深读切片（架构 / MoE / Infra）"
topic: TR-Kimi-K2
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2507.20534
archived: 2026-09-22
---

# TR · Kimi K2 Technical Report 深读切片：架构 / MoE / Infra

> **定位**：报告级对照表 / 深读卡。数字一律取自官方 PDF `https://arxiv.org/abs/2507.20534`。
> **刻意不写**：开闭源谱系叙事（见 [[开源与闭源前沿模型谱系]]）、MoE 通史（见 [[混合专家架构]]）、Megatron/FA/vLLM 通论（见 [[AI基础设施总览]]）。本卡只补「可对表跟读」的规模、MuonClip、稀疏度选择与训练 Infra 要点。
> **评测分**：摘要级亮点可录；完整 Table 3/4 不逐行抄入（见第六节待核实）。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | Kimi K2: Open Agentic Intelligence（封面另标 *Technical Report of Kimi K2*） | 封面 |
| 作者 | Kimi Team（XMP 另列大量具名贡献者） | 封面；XMP |
| arXiv 页眉 | **arXiv:2507.20534v2** \[cs.LG\] **3 Feb 2026** | PDF 第 1 页页眉 |
| XMP identifier | `https://arxiv.org/abs/2507.20534v2` | ` -meta` |
| XMP MetadataDate | 2026-02-04T01:38:06+00:00（→ 用户时区 **2026-02-04 09:38 CST**） | XMP |
| PDF 页数 | **32**（letter） | |
| Creator / Producer | arXiv GenPDF (tex2pdf:57610bf)；pikepdf 8.15.1 | |
| 权利声明（XMP） | `http://creativecommons.org/licenses/by-nc-nd/4.0/` | XMP |
| 本地路径 | `https://arxiv.org/abs/2507.20534` | 仓库 |
| 权重（摘要脚注） | https://huggingface.co/moonshotai/Kimi-K2-Instruct | Abstract 脚注 1 |
| Checkpoint engine（§3.3） | https://github.com/MoonshotAI/checkpoint-engine | §3.3.2 脚注 4 |
| 摘要规模一句话 | MoE；摘要写 **32B activated / 1T total**；MuonClip；预训练 **15.5T** tokens、「zero loss spike」；后训练含 agentic 数据合成 + 联合 RL | Abstract |

**版本说明（本卡边界）**：本 PDF 页眉仅标 **v2 / 3 Feb 2026**。首发日、v1 修订史若不在本 PDF 正文 → 见第六节待核实。摘要「1 trillion / 32 billion」与正文 Table 2「**1.04T / 32.6B**」并存，对表时以后者为准并在待核实中标注。

---

## 二、模型规模 / MoE / 训练对照表（仅报告数字）

### 2.1 与 DeepSeek-V3 的架构对照（Table 2 + §2.3）

| 项 | DeepSeek-V3（报告表内） | Kimi K2 | 报告 ∆ |
|---|---|---|---|
| #Layers | 61 | **61** | = |
| Total Parameters | 671B | **1.04T** | ↑ 54% |
| Activated Parameters | 37B | **32.6B** | ↓ 13% |
| Experts (total) | 256 | **384** | ↑ 50% |
| Experts Active per Token | 8 | **8** | = |
| Shared Experts | 1 | **1** | = |
| Attention Heads | 128 | **64** | ↓ 50% |
| Number of Dense Layers | 3 | **1** | ↓ 67% |
| Expert Grouping | Yes | **No** | — |
| Hidden dim（正文） | — | **7168** | §2.3 |
| MoE expert hidden dim（正文） | — | **2048** | §2.3 |
| Attention | MLA（报告称 similar to V3） | **MLA** | §2.3 |
| Sparsity（= total / activated experts） | — | **48**（8/384） | §2.3 |

> 摘要/引言另写「32 billion activated」「1 trillion / 1.04 trillion」——与 Table 2 的 **32.6B / 1.04T** 口径不完全同一；本卡规模表以 **Table 2** 为准。

### 2.2 稀疏度与注意力头选择（§2.3；Figure 5–6）

| 主张 / 数字 | 报告表述 |
|---|---|
| 稀疏度定义 | total experts / activated experts |
| 小规模规律 | 固定激活参（恒 FLOPs）下，提高 total experts（提高 sparsity）→ train/val loss 更低 |
| 同 val loss=1.5 时 | sparsity **48** 相对 8 / 16 / 32 约减 FLOPs **1.69× / 1.39× / 1.15×** |
| K2 取舍 | sparsity **48**（性能 vs Infra 复杂度） |
| 头数动机 | agentic 长上下文推理成本：128k 上 heads 64→128（experts 固定 384）→ inference FLOPs **+83%** |
| 头数实验 | iso-token 下加倍 heads，val loss 改善约 **0.5%–1.2%**；相对 sparsity 48 收益不划算 → 选 **64** heads |

### 2.3 预训练配方（§2.5 + §2.1 + §2.2）

| 项 | 报告设定 |
|---|---|
| 优化器 | **MuonClip** = Muon + weight decay + consistent update RMS scaling + **QK-Clip**（Algorithm 1） |
| QK-Clip 阈值 $\tau$（K2 正式跑） | **100** |
| 预训练上下文 | **4,096** tokens |
| 总 token | **15.5T** |
| LR 调度 | **WSD** [26]：500-step warm-up 后，前 **10T** 恒定 **2e-4**；随后 **5.5T** cosine **2e-4 → 2e-5** |
| Weight decay | **0.1**（全程） |
| Global batch | **67M** tokens（恒定） |
| 损失曲线 | Figure 3：全程 **no spikes**（未平滑/未抽样） |
| 退火 + 长上下文激活 | batch 仍 67M；LR **2e-5 → 7e-6**；**400B** @ 4k + **60B** @ **32k**；再用 **YaRN** 扩到 **128k** |
| 语料域 | Web Text / Code / Mathematics / Knowledge；处理管线多沿用 Kimi K1.5；知识/数学域强调 **rephrasing** 提 token utility |
| 中尺度对比实验（Muon 不稳定） | 9B activated / 53B total MoE + vanilla Muon：max attention logits 快速 **>1000** |

**MuonClip / QK-Clip 机制要点（§2.1；不编造超参外数字）**：

- 问题：Muon 相对 AdamW 更易出现 **exploding attention logits**；logit soft-cap 不够；**QK-Norm 不适用于 MLA**（推理时 Key 未完全物化）。
- 做法：用 batch 内 per-head max logit $S_{\max}^h$ 作信号；超过 $\tau$ 时 **post-update** 缩放 $W_q/W_k$（**不改当前步 forward/backward**）。
- MLA 裁剪：仅 unshared 分量——$q_C,k_C$ 各乘 $\sqrt{\gamma_h}$；$q_R$ 乘 $\gamma_h$；**共享 $k_R$ 不动**。
- Appendix D：K2 上前约 **70k steps** 有 **12.7%** heads 至少触发一次 clip；之后 heads 的 $S_{\max}$ 落到 100 以下 → clip **自停用**。

### 2.4 后训练配方（公开级；§3）

| 项 | 报告设定 |
|---|---|
| SFT / RL 优化器 | **Muon**（作者建议：Muon 预训练 ckpt 用 Muon 微调） |
| Agentic SFT 数据 | 工具规格仓：真实 **MCP 工具 3000+** + 合成工具 **>20,000**；三阶段：tool spec → agent/task → trajectory；LLM judge + rubric 过滤；编码/SE 另接 **真实 sandbox** |
| RL 框架 | verifiable rewards（**RLVR**）+ **self-critique rubric reward**；Gym-like 可扩展任务集 |
| RL 算法 | 沿用 **K1.5** 的 policy optimization；组采样 $K$ 条、相对均值奖励、带 $\tau\log(\pi_\theta/\pi_{\mathrm{old}})^2$ 正则项（公式见 §3.2.3）；另加 **Budget Control / PTX Loss / Temperature Decay** |
| SE sandbox | Kubernetes；**>10,000** 并发 sandbox 实例（§3.2.1） |

---

## 三、架构与 Infra 公开要点

### 3.1 预训练集群与并行（§2.4.1–2.4.2）

| 项 | 报告 |
|---|---|
| GPU | **NVIDIA H800** |
| 节点 | 每节点 **2 TB RAM**；**8 GPUs**；节点内 **NVLink + NVSwitch** |
| 跨节点 | **8×400 Gbps RoCE** |
| 弹性目标 | 可用任意 **32 的倍数** 节点数训练；小/大实验复用同一并行配置 |
| 并行组合 | **16-way PP**（virtual stages）+ **16-way EP** + **ZeRO-1 DP** |
| 模型并行组显存 | BF16 参数 + FP32 grad accum ≈ **6 TB**，摊在 **256 GPUs** 的 MP group |
| 每卡状态预算 | 约 **30 GB** 装 parameters / grads / optimizer states；余量给 activations |
| 优化器状态 | 大集群：分布式；小集群（例 **32** 节点）：可 **CPU offload** 部分 optimizer states |
| DualPipe | **明确不用**：会加倍参数/梯度显存，迫使加大并行 → 气泡或 EP 开销对 **>1T** 参数「prohibitively high」 |
| EP 通信重叠 | 增加 warm-up micro-batches，在标准 **interleaved 1F1B** 下叠 EP all-to-all；并把 weight-grad 与 PP 通信并行，使 warm-up 外 PP 通信可重叠 |
| EP 规模 | 取可行最小 **EP=16**（K2 仅 64 attn heads，算力段更短，需缩短 EP 时间；小 EP 也放松 expert-balance 约束） |

### 3.2 Activation 压缩与卸载（§2.4.3）

| 技巧 | 报告要点 |
|---|---|
| Selective recomputation | LayerNorm、SwiGLU、**MLA up-projections**；另可选重算 **MoE down-projections**（防早期 expert imbalance OOM） |
| FP8 **存储**（非计算） | MoE up-projection 与 SwiGLU 的 **inputs** → **FP8-E4M3**，**1×128 tiles** + FP32 scales；小规模称无 measurable loss 上升；**不把 FP8 用于 computation**（初步研究担心性能退化） |
| Activation CPU offload | 剩余 activation → CPU；copy engine 与 compute/comm 重叠；1F1B 阶段 offload 上一 micro-batch forward、prefetch 下一 backward（Figure 7） |

### 3.3 RL Infra（§3.3；与预训练 Infra 并列记录）

| 项 | 报告 |
|---|---|
| 架构 | 与 K1.5 类似的 **hybrid colocated**：train / inference engine 同 worker，交替占用 GPU |
| 权重同步 | 专用 **checkpoint engine**；选择「整模 broadcast」换简单解耦；K2 全量参数更新 **<30 s** |
| H800 细节（App. G） | 并发 H2D+broadcast 会打满共享 PCIe → 实际采用 **two-stage**（同步 H2D 后，broadcast∥reload） |
| 启动 | 训练侧集体只读盘一次再 peer broadcast；推理副本复用 checkpoint engine，降低单点故障联动 |
| Agentic rollout | 重环境独立可扩服务；大量并发 rollout；**partial rollout** 暂停长尾轨迹到下一 RL iter；Gym 风格统一环境接口 |

---

## 四、摘要级能力锚点（非评测深挖）

报告自称 open-source **non-thinking** 设定下的 agentic/SWE 强项（Abstract / §1 / §4；完整表见 Table 3）：

| 基准（报告给出） | K2 分数（报告） |
|---|---|
| Tau2-Bench | **66.1** |
| ACEBench (En) | **76.5** |
| SWE-Bench Verified | **65.8**（文中另写 multiple attempts **71.6%**） |
| SWE-Bench Multilingual | **47.3** |
| LiveCodeBench v6 | **53.7** |
| AIME 2025 | **49.5** |
| GPQA-Diamond | **75.1** |
| OJBench | **27.1** |
| LMSYS Arena（报告引用日期） | 2025-07-17：open-source top-1、overall 第 5（>3000 votes） |

评测配置要点（§4.1.1）：一律 **non-thinking**；输出默认 cap **8192**（SWE Agentless **16384**）；长上下文评测窗口 **128K**。

---

## 五、与既有笔记的差异说明

| 已有笔记 | 已覆盖（本卡不复述） | **本 TR 卡新增 / 加深** |
|---|---|---|
| **[[混合专家架构]]** MoE | 稀疏 MoE / V3 头条结构 | K2：**384 experts / top-8 / sparsity 48 / 无 expert grouping / dense layers=1 / heads=64**；Muon 下 sparsity scaling 数字 |
| **[[开源与闭源前沿模型谱系]]** 谱系 | 开闭源坐标 | 报告页元信息（arXiv v2 · 32 页）；1.04T/32.6B 可对表口径 |
| **[[AI基础设施总览]]** Infra | DualPipe/FP8/EP 通论 | K2：**不用 DualPipe**；EP=16+PP=16+ZeRO-1；FP8 **仅存不算**；activation CPU offload；RL colocated + checkpoint-engine <30s |
| **[[DeepSeekV3训练与MoE基建]]** | V3 训练/MoE/Infra 深表 | 本卡提供 **K2↔V3 Table 2 差分** 与 MuonClip 专页 |

**一句话**：K2 在 V3 式 MLA-MoE 骨架上走「更稀、更少头、MuonClip 换 token 效率」，Infra 则用较小 EP + 1F1B 重叠 + CPU offload，并显式拒绝 DualPipe。

---

## 六、待核实与引用

### 6.1 待核实（禁止当作已确认）

1. arXiv **首发 / v1 日期**与 revision 历史：本 PDF 页眉仅见 **v2 · 3 Feb 2026**；写「首发日」需回查 https://arxiv.org/abs/2507.20534。
2. 摘要「**1T / 32B**」vs Table 2「**1.04T / 32.6B**」vs 引言「1.04 trillion / 32 billion」——三处口径并存；对外引用建议标明来源表/段。
3. Tokenizer 词表大小、路由函数（sigmoid/softmax）、aux-loss / bias 负载均衡细节、MLA 压缩维 $d_c,d_c'$ 等：**本 PDF 正文未给出与 V3 §4.2 同级的完整超参表** → 勿从 V3 卡直接搬运。
4. 总 GPU hours / 美元成本：报告**未**给出类似 V3 Table 1 的全流程 H800 hours 汇总。
5. YaRN 的具体 $s,\alpha,\beta$ 等超参：仅写「employed the YaRN method」，细参未在 §2.5 展开。
6. Table 3/4 全部分数、安全评测、Appendix 曲线：本专项聚焦架构/训练/Infra，**未逐格录入**。
7. XMP 权利为 **BY-NC-ND 4.0**；权重仓库实际许可证以 Hugging Face 页面为准（本 PDF 未在摘要写死 Apache 等）。
8. LMSYS 排名绑定报告所写 **2025-07-17** 快照，非永久状态。

### 6.2 引用

- Kimi Team. *Kimi K2: Open Agentic Intelligence* (Technical Report). arXiv:2507.20534v2 \[cs.LG\], 3 Feb 2026.
 PDF：https://arxiv.org/pdf/2507.20534
 本地：`https://arxiv.org/abs/2507.20534`
 （2026-09-22，Asia/Shanghai）

### 6.3 关联笔记

- [[混合专家架构]]：架构/MoE与稀疏/混合专家架构.md（MoE 史线）
- [[开源与闭源前沿模型谱系]]：模型与技术报告/开源与闭源前沿模型谱系.md（谱系）
- [[AI基础设施总览]]：推理与基础设施/AI基础设施总览.md（Infra 通论）
- [[DeepSeekV3训练与MoE基建]]：模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md（V3 对照底表）

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

