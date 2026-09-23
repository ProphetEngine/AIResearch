---
title: GLM-4.5 Technical Report 深读笔记
topic: TR-GLM-4.5
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# GLM-4.5 Technical Report 深读笔记

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：GLM-4.5 Team（Zhipu AI & Tsinghua University），*GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models*（arXiv:2508.06471）
> 官方 PDF：`https://arxiv.org/abs/2508.06471`（**26** 页；页眉 **arXiv:2508.06471v1 [cs.CL] 8 Aug 2025**）
> 权重 / 代码（摘要与 §1）：https://github.com/zai-org/GLM-4.5 ；HF `zai-org/GLM-4.5`；评测工具 https://github.com/zai-org/glm-simple-evals ；亦列 Z.ai / BigModel.cn

---

## 一、报告元信息

| 字段 | 核实值 | 出处 |
|---|---|---|
| 标题 | GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models | 封面 |
| 作者 | GLM-4.5 Team；Zhipu AI & Tsinghua University；完整名单见 §6 Contribution（Core / Contributors / Tech Leads / Advisors） | 封面；§6 |
| arXiv | **2508.06471v1** \[cs.CL\] **8 Aug 2025** | PDF 第 1 页页眉 |
| PDF 页数 | **26**（letter） | |
| PDF Creator / Producer | arXiv GenPDF (tex2pdf:)；pikepdf 8.15.1 | |
| PDF CreationDate | 本机 **未给出** CreationDate/ModDate（pikepdf 重打包） | |
| 本地路径 | `https://arxiv.org/abs/2508.06471` | 仓库 |
| 系列定位 | 开源 MoE；面向 **Agentic / Reasoning / Coding (ARC)** 统一能力；**hybrid reasoning**（thinking + direct/non-thinking） | Abstract；§1 |
| 发布型号 | **GLM-4.5**（355B total / 32B activated）；**GLM-4.5-Air**（106B total / **12B** activated，Table 1） | Abstract；Table 1 |
| 预训练体量（摘要） | multi-stage training on **23T** tokens | Abstract |
| 摘要级 ARC 分数（作者宣称） | TAU-Bench **70.1%**；AIME 24 **91.0%**；SWE-bench Verified **64.2%**；总体评测 **第 3**、agentic **第 2**（相对报告当时评测集） | Abstract；§1 |

**摘要级一句话（不外推）：**
GLM-4.5 是首个 GLM 系 MoE（355B/32B），用更「瘦高」的 MoE + loss-free routing + MTP，经约 23T 多阶段预训练/中训，再经 **Expert Model Iteration**（Reasoning / Agent / General 专家 → 统一自蒸馏）与多源 RL，交付同权重 hybrid thinking/non-thinking，并强调 ARC 三角能力与开源权重。

---

## 二、模型族 / 规模对照表（§2.1 / Table 1）

### 2.1 架构差分（相对 DeepSeek-V3 / Kimi K2，报告原文）

- **MoE**：loss-free balance routing [40] + **sigmoid gates** [23]；每层 **1 shared + routed experts**。
- **形态选择（相对 V3 / K2）**：**减小 width**（hidden dim、routed experts 数），**增大 height**（层数）——作者称更深模型推理能力更好。
- **注意力**：**GQA + partial RoPE**；相对同 hidden 用约 **2.5×** 更多 heads（5120 hidden → **96** heads）；加 **QK-Norm**（仅 GLM-4.5 表中为 Yes；Air 为 No）。
- **MTP**：两型号均加 **1** 层 MoE 作 Multi-Token Prediction，服务推理 speculative decoding。
- **计参约定（Table 1 注）**：计入 MTP 层参数；**不计** word embeddings 与 output layer。

### 2.2 Table 1 规模对照（报告原文数字）

| 字段 | GLM-4.5 | GLM-4.5-Air | DeepSeek-V3（对照列） | Kimi K2（对照列） |
|---|---:|---:|---:|---:|
| # Total Parameters | **355B** | **106B** | 671B | 1043B |
| # Activated Parameters | **32B** | **12B** | 37B | 32B |
| # Dense Layers | 3 | 1 | 3 | 1 |
| # MoE Layers | **89** | **45** | 58 | 60 |
| # MTP Layers | 1 | 1 | 1 | 0 |
| Hidden Dim | **5120** | **4096** | 7168 | 7168 |
| Dense Intermediate Dim | 12288 | 10944 | 18432 | 18432 |
| MoE Intermediate Dim | **1536** | **1408** | 2048 | 2048 |
| Attention Head Dim | 128 | 128 | 192 | 192 |
| # Attention Heads | **96** | **96** | 128 | 64 |
| # Key-Value Heads | **8** | **8** | 128 | 64 |
| # Experts (total) | **160** | **128** | 256 | 384 |
| # Experts Active Per Token | **8** | **8** | 8 | 8 |
| # Shared Experts | **1** | **1** | 1 | 1 |
| QK-Norm | **Yes** | **No** | No | No |

> 层数合计核对（仅作跟读）：GLM-4.5 Dense+MoE+MTP = 3+89+1 = **93**；Air = 1+45+1 = **47**。报告未另列「总层数」字段。

### 2.3 上下文与产品形态（报告写明）

| 项 | 报告值 |
|---|---|
| 预训练最大序列 | **4,096** |
| Mid-training 序列 | **32,768** → **131,072**（Figure 3 标 128K；正文写 extend to 128K / 131,072） |
| Overall SFT 最大上下文 | **128K** |
| Reasoning RL 输出长度实验 | 直接在 **64K** 做 single-stage RL（相对逐步加长更优，小模型消融） |
| Hybrid 模式 | thinking（复杂推理 / agentic）+ non-thinking（即时回复）；Overall SFT 中平衡「全推理」与「无显式思维」数据 |

---

## 三、训练与后训练要点

### 3.1 预训练数据与两阶段（§2.2；Figure 3）

**语料来源（报告）：** webpages、social media、books、papers、code repositories；英/中网页为主；多语含自爬 + **Fineweb-2**；代码 GitHub 等；数学/科学自网页/书/论文。

**处理要点（不外推）：**

| 源 | 报告做法 |
|---|---|
| Web | 质量分桶上采样；最高质量桶预训练 **>3.2 epochs**；弃最低桶；MinHash 外再 **SemDedup** |
| Multilingual | 教育效用分类器，上采样高质量多语 |
| Code | 规则过滤 + 语言相关质量三档；高质量上采样、低质剔除；全源码 **Fill-In-the-Middle**；代码相关网页两阶段检索 + 重解析保格式 |
| Math & Science | LLM 打教育内容占比分 → 小分类器 → 阈值上采样 |

**预训练两阶段：**

1. **General**：以网页通用文档为主（Figure 3：**15T** @ **4K**）。
2. **Code & Reasoning Continual**：上采样 GitHub 源码与 coding / math / science 相关网页（Figure 3：**7T** @ **4K**）。

→ 与摘要 **23T** 一致：**15T + 7T = 22T**，再加 mid-training 的 500B+500B+100B（见下）≈ **23.1T** 量级（Figure 3 数字；摘要四舍五入为 23T）。

### 3.2 Mid-training（§2.3；Figure 3）

| 阶段 | 数据量（Figure 3） | 序列长 | 要点 |
|---|---|---|---|
| Repo-level Code | **500B** | **32K** | 同仓文件拼接学跨文件依赖；issues/PRs/commits 拼接，commit 为 diff 风格 |
| Synthetic Reasoning | **500B** | **32K** | 数学/科学/竞赛代码题；用 reasoning 模型合成思维过程 |
| Long Context & Agent | **100B** | **128K** | 上采样长文档；大规模合成 agent 轨迹 |

打包：预训练用随机截断作增强（不用 best-fit packing）；mid-training 用 **best-fit packing**，避免截断推理过程或仓级代码。

### 3.3 预训练超参（§2.4）— Infra / 稳定性抓手

| 项 | 报告值 |
|---|---|
| Optimizer | **Muon**（除 word embedding、bias、RMSNorm 权重）；Newton–Schulz **N=5**；momentum **µ=0.95**；update RMS scale **0.2** |
| LR schedule | **cosine decay**（不用 WSD；作者称 WSD 在 SimpleQA/MMLU 更差、stable 段欠拟合） |
| LR | warm-up **0 → 2.5e-4**，再衰减至 **2.5e-5**（至 mid-training 结束） |
| Batch | 前 **500B** tokens 从 **16M → 64M** tokens warmup，其后恒定 |
| Regularization | weight decay **0.1**；**无 dropout** |
| RoPE base | 扩到 32K 时 **10,000 → 1,000,000** |
| Loss-free routing bias update | 前 **15T**：rate **0.001**；其后 **0.0** |
| Aux sequence-level balance loss | 权重 **0.0001** |
| MTP loss λ | 前 **15T**：**0.3**；其后 **0.1** |

**报告未给出：** 预训练 GPU 型号、卡数、总 GPU-hours、TP/PP/EP 拓扑、预训练 BF16/FP8 配方 → 见第四节待核实。

### 3.4 后训练总览：Expert Model Iteration（§3）

`
Stage 1 Expert Training: Reasoning / Agent / General chat 各专家
 └─ Cold-start SFT → 各域 Expert RL
Stage 2 Unified Training: self-distillation 融合专家
 └─ Overall SFT（hybrid）→ General RL 等
`

目标：同一模型可走 **deliberative reasoning** 与 **direct response**。

### 3.5 SFT（§3.1）

- **Cold Start SFT**：小规模带长 CoT 的 SFT，为各专家 RL 奠基。
- **Overall SFT**：数百万样本；覆盖推理 / 通用聊天 / agentic（工具与真实项目开发）/ 长文；蒸馏各专家输出；**128K**；平衡有/无显式思维数据 → hybrid。
- **Function-call 模板**：键值用 **XML-like special tokens** 包住，减少代码参数 JSON 转义负担（Figure 4 示例；实现见开源仓）。
- **Rejection sampling**：去重复/过短/截断/非法格式；客观题验正确性；主观题用 RM；工具轨迹验协议与终态。
- **Prompt 选择**：去掉响应长度后 **50%** 短样本 → 数学/科学约 **+2%–4%**（半数据）；难 prompt **4** 响应 → 再 **+1%–2%**。
- **Agentic SFT 自动构建四步**：框架与工具收集（含 MCP / LLM 模拟工具）→ 任务合成 → 轨迹生成（含 user simulator 多轮）→ 多 judge agent 过滤成功轨迹。

### 3.6 Reasoning RL（§3.2）

- 算法骨架：**GRPO**，**去掉 KL loss**。
- 本节曲线基于 **smaller experimental model**，非 GLM-4.5 本体。
- **难度课程两阶段**：后期切到极难（pass@8=0 且 pass@512>0），答案均经验证。
- **64K 输出 single-stage RL** 优于逐步加长（短上限 RL 会「忘掉」长输出）。
- **动态采样温度**：奖励平稳则升温；校验集上取「性能掉幅 ≤1%」的最大温度。
- Code RL：**token-weighted mean loss** 优于 sequence-mean。
- Science RL：仅用专家验证的高质量多选题优于混合质量数据（GPQA-Diamond 消融）。

### 3.7 Agentic RL（§3.3）

- 数据：网页多跳/混淆 QA 合成；GitHub PR/issue + 可执行单测（沙箱分布式）。
- 优化：group-wise policy optimization；**仅对模型生成 token 计 loss，忽略环境反馈 token**。
- 奖励：网页看终答正确；编码主用可验证 SWE；另加 **process action format penalty**（格式错则停并零奖）。
- **Iterative self-distillation**：RL → 用 RL 轨迹替换 cold-start → 再 RL，抬高平台。
- Test-time：靠 **interaction turns** 扩展算力（BrowseComp 随 turns 平滑上升，Figure 8）。

### 3.8 General RL（§3.4）

多源反馈：**规则 + RLHF + RLAIF**。

| 子任务 | 报告要点 |
|---|---|
| Holistic RL | ~**5,000** prompts；7 / 33 / 139 级类目；人偏好 RM + 按是否有客观答案的 AI rubric |
| Instruction Following RL | 7 major + **151** minor 约束；规则 + RM + critique；GRPO 至约 **1,000** steps 未见明显 reward hacking（Figure 9 / SysBench-ISR） |
| Function Calling RL | (1) **step-wise** 严格匹配格式与 GT（0/1）；并入 general RL；(2) **end-to-end multi-turn**（MCP 合成 + Agentgym 等）；先训专家再蒸馏回主模型 |
| Pathology RL | 针对语码混杂、重复、格式错误；用易触发病理的 prompt 集中惩罚 |

### 3.9 RL Infrastructure（§3.5）— AI Infra 主抓手

- 框架：**Slime**（https://github.com/THUDM/slime）；三模块 — Training（**Megatron**）/ Rollout（**SGLang + Router**）/ Data Buffer（Figure 10）。
- **同步同置** vs **异步解耦**：数学/代码等 reasoning 用 colocated sync + dynamic sampling 减 GPU 空转；SWE 等长时 agent 用 disaggregated async（Ray 调度；rollout 与 train GPU 可同卡或分卡）。
- **精度分工**：**BF16 训练** + rollout 前 **online block-wise FP8 量化** → **FP8 推理**加速采数。
- Agent 向：高并发 **Docker** 隔离环境；rollout/train 引擎分池；统一 HTTP + 中央 data pool（message-list 轨迹），解耦异构 agent 框架。

### 3.10 评测锚点（§4，便于跟读，非全面抄表）

| 维度 | GLM-4.5 | GLM-4.5-Air | 备注 |
|---|---:|---:|---|
| TAU-Retail / Airline | 79.7 / 60.4 | 77.9 / 60.8 | Abstract 70.1% ≈ (79.7+60.4)/2 |
| BFCL V3 | 77.8 | 76.4 | Table 3 |
| BrowseComp | 26.4 | 21.3 | Table 3；agentic avg 58.1 / 55.7 |
| AIME 24 | 91.0 | 89.4 | Avg@32；Table 4 |
| GPQA | 79.1 | 75.0 | Avg@8 |
| SWE-bench Verified | 64.2 | 57.6 | OpenHands v0.34.0；≤100 iter；128K；T=0.6 |
| Terminal-Bench | 37.5 | 30.0 | Terminus + standard FC |
| 作者排位叙述 | overall **3rd**；agentic **2nd**（跟 o3）；coding 近 Claude Sonnet 4 | Air overall **6th** | §1；相对报告当时 12-bench 集 |

Base（Table 2）：GLM-4.5-Base 355B/32B；内部评测框架；未训指令数据。

---

## 四、待核实与引用

### 4.1 待核实（禁止编造）

| # | 项目 | 原因 |
|---|---|---|
| 1 | 预训练 / mid-training **GPU 型号、卡数、总 GPU-hours** | 正文未给 V3 级算力表；仅 RL 侧写 BF16/FP8 与 Slime |
| 2 | 预训练并行拓扑（TP/PP/EP/DP）与预训练精度 | §2.4 仅 Muon/LR/batch/路由；无并行与 dtype |
| 3 | 「partial RoPE」的具体分维比例 / 实现 | 仅写 GQA with partial RoPE，无公式或分维表 |
| 4 | Air 为何 **无 QK-Norm**、以及与 96 heads 决策的完整消融表 | Table 1 有差分；正文消融叙事以旗舰 heads/QK-Norm 为主 |
| 5 | Figure 3 各阶段 token 与摘要 23T 的官方精确加总式 | 15T+7T+0.5T+0.5T+0.1T 可自洽，报告未逐行求和说明 |
| 6 | Expert 三域各自 RL 步数、数据量、与最终统一模型的权重继承细节 | 有流程无完整超参表 |
| 7 | 开源权重 **许可证**（Apache/MIT 等） | 报告写 open-source / release weights；**未在本 PDF 写明 license 字符串** → 以 HF/GitHub 模型卡为准 |
| 8 | 推理默认上下文、部署推荐（vLLM 等）与 chat template 产品默认 | 训练写到 128K/131072；产品默认以模型卡为准 |
| 9 | arXiv abs 页提交/修订史、是否有 v2+ | 本 PDF 仅 **v1 / 8 Aug 2025** |
| 10 | 报告日后的 GLM-4.5 量化版 / 增量型号 | 超出本 PDF 边界 |

### 4.2 引用

| 编号 | 文献 | 日期 | URL / 路径 |
|---|---|---|---|
| [GLM45] | GLM-4.5: Agentic, Reasoning, and Coding (ARC) Foundation Models | arXiv **2508.06471v1**，页眉 **8 Aug 2025** | https://arxiv.org/abs/2508.06471 ；PDF https://arxiv.org/pdf/2508.06471 |
| [GLM45-PDF] | 本地副本 | 26 页；Creator arXiv GenPDF | `https://arxiv.org/abs/2508.06471` |
| [GLM45-GH] | 权重与代码入口（报告） | — | https://github.com/zai-org/GLM-4.5 ；https://huggingface.co/zai-org/GLM-4.5 |
| [SLIME] | RL 框架（报告脚注） | — | https://github.com/THUDM/slime |
| [EVALS] | 评测复现工具（报告） | — | https://github.com/zai-org/glm-simple-evals |

### 4.3 跟读一句话

> **GLM-4.5 = 瘦高 MoE（355B/32B，160×8+shared，MTP，GQA+partial RoPE+多头+QK-Norm）+ Muon/23T 多阶段预训与中训（4K→32K→128K）+ Expert Iteration（Reasoning/Agent/General → 自蒸馏 hybrid）+ Slime（Megatron 训 / SGLang 采 / BF16+FP8）支撑的 ARC 开源旗舰；Air 为 106B/12B 同族压缩版。**

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

