---
title: "DeepSeek-V3.2 Technical Report 专项深读卡"
topic: TR-DeepSeek-V3.2
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2512.02556
archived: 2026-09-22
---

# TR · DeepSeek-V3.2 Technical Report 专项深读卡

> **定位**：报告级增量深读卡（相对 V3 / V3.1-Terminus / V3.2-Exp）。数字一律取自官方 PDF `https://arxiv.org/abs/2512.02556`（2026-09-22）。
> **攻坚线**：**架构思想（主）** + **AI Infra（辅）**。
> **刻意不写**：Switch→Mixtral→V3 MoE 史线（见 [[混合专家架构]]）；开闭源谱系坐标（见 [[开源与闭源前沿模型谱系]]）；V3 完整训练/DualPipe/FP8 配方表（见 [[DeepSeekV3训练与MoE基建]]）。本卡只补「V3.2 相对前代公开了什么」。
> **禁止编造**：本 PDF **未重述** 671B/37B、14.8T、DualPipe、FP8 分块等 V3 配方数字 → 不得从 V3 卡外推为 V3.2 新主张。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models | 封面； Title |
| 作者 | DeepSeek-AI；`research@deepseek.com`； Author 列 Aixin Liu 等长名单 | 封面 |
| arXiv 页眉 | **arXiv:2512.02556v1** \[cs.CL\] **2 Dec 2025** | PDF 第 1 页页眉 |
| PDF 页数 | **23**（A4） | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:4177c2c) | |
| 本地路径 | `https://arxiv.org/abs/2512.02556` | 仓库 |
| 扫描登记 | [[SystemCard与TR扫描2025至2026]] 表：DeepSeek-V3.2 · arXiv 2025-12-02 · 本地已归档 | 模型与技术报告/SystemCard与TR扫描2025至2026.md |
| 开源推理参考实现（脚注） | https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/tree/main/inference | §2.1 脚注 2 |
| 摘要三突破 | (1) **DeepSeek Sparse Attention (DSA)**；(2) **Scalable RL**（称可比 GPT-5；**Speciale** 金奖级 IMO/IOI）；(3) **Large-Scale Agentic Task Synthesis** | Abstract |

**摘要级一句话（不外推）：**
V3.2 从 **V3.1-Terminus（已扩到 128K）** 继续训入 **DSA**，再用大幅加码的 **GRPO 混合 RL** + **合成 agent 任务**把推理与工具使用合轨；架构相对 Terminus「唯一改动」是 DSA，其余能力叙事主要来自后训练算力与数据。

**变体命名（正文用法）：**

| 名称 | 报告关系 |
|---|---|
| DeepSeek-V3.1-**Terminus** | 「last version of DeepSeek-V3.1」；DSA 继续训的起点（128K） |
| DeepSeek-V3.2-**Exp** | 与 V3.2「exactly the same architecture」；后训练管线亦对齐；用于 parity / 合成任务消融 |
| DeepSeek-V3.2 | 正式产品向：specialist 蒸馏 + 混合 RL（含 length penalty） |
| DeepSeek-V3.2-**Speciale** | 仅推理数据、**减弱 length penalty**；并入 DeepSeekMath-V2 数据与 reward；冲金奖 / 更长轨迹 |

---

## 二、相对 V3 / V3.1 增量对照表

> 左列以本 PDF 明文为准；V3 列仅作「本卡对照锚点」，细节见 模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md。V3.1-Terminus **无独立本仓库 TR PDF** → 其数字仅录 V3.2 文中转述。

| 维度 | DeepSeek-V3（[[DeepSeekV3训练与MoE基建]] / 本仓库 PDF） | V3.1-Terminus（仅 V3.2 文中） | **DeepSeek-V3.2（本 PDF）** |
|---|---|---|---|
| 报告入口 | arXiv:2412.19437v2 · 53 页 | 无本仓库专项 TR | arXiv:**2512.02556v1** · **23** 页 · 2025-12-02 |
| 主干结构 | MLA + DeepSeekMoE + MTP；671B / 37B 等 | 作为 V3.2 继续训起点；文称上下文已扩至 **128K** | **与 V3.2-Exp 同架构**；相对 Terminus **唯一架构修改 = DSA**（§2.1） |
| 注意力 | MLA（稠密核心注意力） | 同左（无 DSA） | **DSA**：lightning indexer + top-$k$ 细粒度选 token；挂在 MLA 的 **MQA 模式**（§2.1） |
| 预训练路径 | 14.8T + YaRN 4K→32K→128K 等 | 128K 长上文扩展已完成 | **Continued PT** 两阶段（数据分布「totally aligned」于 Terminus 的 128K 扩展数据）：Dense warm-up **2.1B** + Sparse **943.7B** tokens（§2.1.1） |
| 后训练算力叙事 | Table 1：Post-Training **5K** H800 hours（相对预训练极小） | （本 PDF 未给独立账） | 称 RL 预算 **已超过预训练成本的 10%**（§1 / §4.1）；「thousands of steps」持续 RL（§3） |
| RL 算法 | GRPO + rule/model RM | — | 仍 **GRPO**；合并 reasoning / agent / human alignment 为 **单阶段混合 RL**；新增稳定化：**Unbiased KL、Off-Policy Sequence Masking、Keep Routing、Keep Sampling Mask**（§3.1） |
| Agent / 工具 | V3 报告后训练不以大规模 agent 合成为主叙事 | — | Cold-start 把工具写入 `<think>` 轨迹；合成 **>1,800** 环境、**85,000** complex prompts（§1）；Table 1 四类任务计数；tool-calling **thinking 上下文保留规则**（§3.2） |
| 推理成本公开 | 侧重训练/部署并行与 FP8 | Figure 3 对照基线 | Figure 3：H800 服务实测 prefilling/decoding **$/M tokens vs 位置**；租金假设 **$2 / GPU hour**（与 V3 报告同假设口径） |
| 旗舰评测叙事 | 通用榜 + 成本 | Exp 与 Terminus Elo/长文 parity（§2.2） | Thinking 主表对齐 GPT-5-High / Gemini-3.0-Pro / Kimi-K2-Thinking 等；**Speciale** 冲 IMO/IOI/ICPC/CMO **Gold**（Table 3–4） |
| 世界知识 / 总训算力 | 预训练 14.8T 为主轴 | — | §5 自承：相对 Gemini-3.0-Pro，**总训练 FLOPs 更少 → 世界知识 breadth 仍落后**；计划未来加预训练算力 |

**增量一句话：**
相对 V3「训出 MoE+MLA 基座」，V3.2 公开增量几乎全部落在 **稀疏注意力继续训（DSA）**、**后训练算力比例（>10% 预训练）** 与 **agent 合成/思维进工具**；MoE 主结构数字本报告**未重开表**。

---

## 三、架构 / 训练 / 推理公开要点

### 3.1 DSA 机制（§2.1）

| 组件 | 报告要点 |
|---|---|
| Lightning indexer | 对 query $h_t$ 与前序 $h_s$ 算 index score $I_{t,s}$（式 1）：多 indexer head、ReLU、可 **FP8**；头数少 → 吞吐友好 |
| Fine-grained selection | 按 $I_{t,:}$ 取 **Top-$k$** 对应的 KV 条目 $\{c_s\}$，再对选中子集做注意力（式 2） |
| 与 MLA 的接法 | 为继续训兼容 + 核级多 query 共享 KV：基于 MLA 的 **MQA 模式**（每 latent / KV entry 被该 token 全部 query heads 共享）；App. A 对比 MHA vs MQA 模式 |
| 复杂度 | 主干注意力 $O(L^2)\to O(Lk)$，$k\ll L$；indexer 仍 $O(L^2)$ 但算量远小于 Terminus 的 MLA；短序列 prefill 另用 **masked MHA** 模拟 DSA 以提效（§2.3） |
| 开源锚定 | HF `DeepSeek-V3.2-Exp/.../inference` 实现细节「unambiguously」（脚注 2） |

### 3.2 Continued Pre-Training 两阶段（§2.1.1）

| 阶段 | 冻/训什么 | LR | Steps / batch 形态 | Token 量 | Top-$k$ |
|---|---|---|---|---|---|
| **Dense Warm-up** | 稠密注意力；**仅训 lightning indexer**（其余冻结）；KL 对齐「各 head 注意力分求和 → L1 归一化」目标分布（式 3） | $10^{-3}$ | 1000 steps；每步 **16** 条 × **128K** | **2.1B** | （仍稠密） |
| **Sparse Training** | 引入 top-$k$ 选择；**全参**适应稀疏；indexer 仅由 $\mathcal{L}_I$（式 4，只在选中集上 KL）优化，且 **detach** indexer 输入；主模型只吃 LM loss | $7.3\times10^{-6}$ | 15000 steps；每步 **480** 条 × **128K** | **943.7B** | **2048** KV tokens / query |

数据：两阶段分布均与 Terminus 的 **128K long context extension data**「totally aligned」。

### 3.3 Parity 与推理成本（§2.2–2.3）

- **标准榜 / ChatbotArena Elo（2025-11-10）/ AA-LCR / Fiction.liveBench**：作者称 V3.2-Exp 相对 Terminus **无明显退化**，部分长文还略高（§2.2；第三方榜链见脚注 3–4）。
- **Figure 3**：H800 集群服务成本曲线（prefilling / decoding）；V3.2 长上下文端到端显著低于 Terminus（定性读图；本卡不数字化曲线点）。

### 3.4 后训练公开要点（§3）

| 块 | 要点 |
|---|---|
| 管线 | 与 V3.2-Exp 相同：**specialist distillation → mixed RL**；后训练阶段注意力与稀疏继续训一致（仍用 DSA） |
| Specialist | 同一 V3.2 base 上分域训专家：写作/通用 QA + **数学、编程、通用逻辑、general agentic、agentic coding、agentic search**；均支持 thinking / non-thinking；专家大规模 RL 后蒸馏进最终 checkpoint；称蒸馏后略低于专家、再 RL 可抹平差距 |
| Mixed RL | **GRPO**；reasoning + agent + human alignment **合并单阶段**（抗 catastrophic forgetting） |
| Reward | 推理/agent：**rule-based outcome + length penalty + language consistency**；通用任务：**generative RM + per-prompt rubrics** |
| Speciale | 仅 reasoning 数据；**reduced length penalty**；并入 **DeepSeekMath-V2** 数据与 reward（数学证明） |
| 算力口径 | 「already exceeds **10%** of the pre-training cost」（§4.1；§1 同口径）；未给绝对 GPU-hours 表 |

**GRPO 稳定化四件套（§3.1，相对「裸 GRPO」公开增量）：**

1. **Unbiased KL Estimate**：用 $\pi_\theta/\pi_{\mathrm{old}}$ 重要性校正 K3 估计（式 7）；数学域可弱化甚至去掉 KL。
2. **Off-Policy Sequence Masking**：大 batch rollout 切 mini-batch + 训推不一致 → 对 **负优势且 KL($\pi_{\mathrm{old}}\|\pi_\theta)>\delta$** 的序列置 mask（式 8–9）。
3. **Keep Routing**：推理采样时的 **专家路由路径在训练时强制复用**（MoE 训推路由不一致会抖参数子空间）；称自 **DeepSeek-V3-0324** 起采用。
4. **Keep Sampling Mask**：保留 top-$p$/top-$k$ 截断 mask，使 $\pi_{\mathrm{old}}$ 与 $\pi_\theta$ 动作空间一致；称有助 language consistency。

### 3.5 Thinking × Tool-Use（§3.2）

| 主题 | 报告要点 |
|---|---|
| Context management（Fig 4） | **仅在新 user message 到来时**丢弃历史 reasoning；若只追加 tool 消息则 **保留** thinking；即使去掉 reasoning，**tool call/结果历史仍保留** |
| 框架兼容警告 | Roo Code / Terminus 等用 **user 消息模拟 tool** → 可能吃不到上述保留；建议对此类框架用 **non-thinking** |
| Cold-start | 用系统提示把「推理标签 `<think>`」与「toolcall 指导」拼进同轨迹（App. Table 6–8 竞程示例）；先偶尔走出可用轨迹，再交给 RL |
| Table 1 任务库存 | code agent **24667**（real env / extracted）；search **50275**（real / synthesized）；general **4417**（synthesized / synthesized）；code interpreter **5908**（real / extracted） |
| 合成规模（§1 vs §3.2.3） | 引言：over **1,800** environments 与 **85,000** complex prompts；§3.2.3：自动合成后经 RL 筛 **pass@100>0** → **1,827** 环境、对应任务合计 **4,417**（general agent 行） |
| Search / Code / Interpreter | 多 agent 造可验证搜索题；GitHub issue–PR 挖可执行环境（多语言）；Jupyter 作 interpreter |
| 消融（§4.3 / Table 5 / Fig 5） | 合成 general 任务对 Exp/闭源仍难（Pass@1：Exp 12% … GPT-5-Thinking 62%）；**仅**在合成 general agent 上 RL（non-thinking）可抬 Tau2 / MCP-Mark / MCP-Universe；仅 code+search RL 则不抬这些榜 |

### 3.6 评测快照（§4；跟读用，非本卡主轴）

评测设定摘录：temperature **1.0**；context **128K**；tool 榜用 function call + thinking（除非另注）。

| Benchmark（Metric） | Claude-4.5-Sonnet | GPT-5-High | Gemini-3.0-Pro | Kimi-K2-Thinking | MiniMax-M2 | **V3.2-Thinking** |
|---|---:|---:|---:|---:|---:|---:|
| MMLU-Pro (EM) | 88.2 | 87.5 | 90.1 | 84.6 | 82.0 | **85.0** |
| GPQA Diamond | 83.4 | 85.7 | 91.9 | 84.5 | 77.7 | **82.4** |
| HLE Pass@1 | 13.7 | 26.3 | 37.7 | 23.9 | 12.5 | **25.1** |
| LiveCodeBench | 64.0 | 84.5 | 90.7 | 82.6 | 83.0 | **83.3** |
| Codeforces Rating | 1480 | 2537 | 2708 | — | — | **2386** |
| AIME 2025 | 87.0 | 94.6 | 95.0 | 94.5 | 78.3 | **93.1** |
| Terminal Bench 2.0 | 42.8 | 35.2 | 54.2 | 35.7 | 30.0 | **46.4**† |
| SWE Verified | 77.2 | 74.9 | 76.2 | 71.3 | 69.4 | **73.1** |
| BrowseComp | 24.1 | 54.9 | — | -/60.2* | 44.0 | **51.4 / 67.6*** |
| Tool-Decathlon | 38.6 | 29.0 | 36.4 | 17.6 | 16.0 | **35.2** |

† Terminal 46.4 用 **Claude Code** 框架（thinking 与 Terminus 不兼容）；Terminus + non-thinking = **39.3**。
\* BrowseComp 带 context management；无管理为 51.4；Discard-all 等可达 **67.6**（§4.4）。

**Speciale（Table 3–4）摘录：** AIME 96.0 (23k tokens)、HMMT Feb 99.2 (27k)、Codeforces **2701** (77k)；IMO 2025 **35/42 Gold**；CMO **102/126 Gold**；IOI **492/600 Gold**（排名第 10）；ICPC WF **10/12 Gold**（排名第 2）。作者强调 Speciale **token 效率仍显著劣于** Gemini-3.0-Pro，故正式 V3.2 加严 length 约束。

### 3.7 局限（§5，作者自承）

1. 总训练 FLOPs 较少 → **世界知识 breadth** 落后前沿闭源；拟加预训练算力。
2. **Token 效率**：需更长轨迹才能逼近 Gemini-3.0-Pro 质量；拟优化「intelligence density」。
3. 复杂任务求解仍逊前沿；拟继续打磨基座与后训练配方。

---

## 四、相对 [[DeepSeekV3训练与MoE基建]] 与 [[混合专家架构]] 的增量

| 已有笔记 | 已覆盖（本卡不复述） | **本 TR 卡新增 / 加深** |
|---|---|---|
| **[[DeepSeekV3训练与MoE基建]]** | 671B/37B；14.8T；LR/batch/$\gamma$/$\lambda$；YaRN；DualPipe 气泡；FP8 E4M3 分块；EP/PP/ZeRO；SFT 1.5M；早期 GRPO+双 RM | **DSA 公式与两阶段继续训超参**；相对 Terminus「唯一架构改动」边界；**>10% 预训练**后训练算力主张；GRPO 四稳定化技巧（含 Keep Routing 自 V3-0324）；thinking×tool 上下文规则；合成 agent 库存与消融；Speciale / 金奖表；H800 推理成本 Fig 3 口径 |
| **[[混合专家架构]]** MoE 史线 | Switch / Mixtral / V3 思想跳跃；aux-loss-free、$M=4$、MLA/MTP 一句话 | **本报告几乎不新增 MoE 结构数字**；增量在「RL 时 Keep Routing」与「稀疏注意力挂 MLA-MQA」——属 **训推一致 / 注意力稀疏**，不是新专家拓扑 |
| **[[开源与闭源前沿模型谱系]]** | 谱系坐标；曾列 V3.1/V3.2 新闻日为待核实 | 本卡把 **V3.2 正式 TR（2512.02556）** 落成可对表深读；架构细节以本 PDF 为准，不再用新闻标题填表 |
| **[[注意力效率族MQA到MLA]] / [[长上下文位置编码与系统侧]]**（相关） | 注意力效率 / 长上下文通论 | DSA 的 indexer+top-$k$、$O(Lk)$、短文 masked MHA、128K agent 溢窗的 Summary/Discard 策略 → 可回链效率与长上下文笔记 |

**一句话：**
[[混合专家架构]] / [[DeepSeekV3训练与MoE基建]] 讲清「V3 基座怎么训、MoE/Infra 怎么叠」；本卡讲清「V3.2 在 **同一基座叙事** 上如何用 **DSA 继续训 + 加码混合 RL + 合成 agent** 追闭源推理/工具面——并标明本 PDF **未重开** V3 参数量表」。

---

## 五、待核实与引用

### 5.1 待核实（禁止当作已确认）

1. **V3.1-Terminus / V3.2-Exp 独立技术报告或模型卡**：本仓库仅有本 V3.2 PDF；Terminus 的层数/总参/激活参/专家数等 **未在本 PDF 重述** → 不得默认「仍严格等于 V3 的 671B/37B」而不标注推断。
2. **「>10% of pre-training cost」的分母**：是 V3 的 2.788M H800 hours、Terminus 继续训成本，还是内部另一口径？正文未给绝对 GPU-hours 表。
3. **引言 85,000 complex prompts** 与 Table 1 / 1,827 环境·4,417 任务的精确包含关系（是否含 search/code 全量 vs 仅 general 合成）→ 引用时宜分项标注出处段落。
4. **Figure 3 成本曲线数值点**：文本层无逐点表；若需报价对比应回读原图或官方 blog。
5. **ChatbotArena Elo「closely matched」**：未在正文给具体 Elo 数字。
6. **MCP-Universe / MCP-Mark**：作者注明用 **内部环境**，可能与官方略有差。
7. **Gold-medal** 协议：细节在 App. D；IMO/CMO 题与推理代码指向 DeepSeek-Math-V2 GitHub——本卡未逐条复核提交规则。
8. 官方后续权重许可、API 定价、与新闻站 V3.2 发布日差异：以 arXiv 页眉 **2025-12-02** 与官方 PDF 为准；商业条款不在本 PDF。

### 5.2 引用

- DeepSeek-AI. *DeepSeek-V3.2: Pushing the Frontier of Open Large Language Models*. arXiv:**2512.02556v1** \[cs.CL\], **2 Dec 2025**.
 PDF：https://arxiv.org/pdf/2512.02556
 Abs：https://arxiv.org/abs/2512.02556
 本地：`https://arxiv.org/abs/2512.02556`
 （2026-09-22 CST / Asia/Shanghai）

### 5.3 关联笔记

- [[DeepSeekV3训练与MoE基建]]：模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md（基座训练 / MoE / Infra）
- [[DeepSeekR1推理训练深读]]：模型与技术报告/厂商报告/DeepSeekR1推理训练深读.md（推理 RL 前史）
- [[混合专家架构]]：架构/MoE与稀疏/混合专家架构.md（MoE 史线；本卡无新专家拓扑）
- [[开源与闭源前沿模型谱系]]：模型与技术报告/开源与闭源前沿模型谱系.md（谱系；V3.2 TR 此前为待核实项）
- [[AI基础设施总览]] / [[注意力效率族MQA到MLA]]：推理与基础设施/AI基础设施总览.md、架构/注意力与长上下文/注意力效率族MQA到MLA.md（Infra / 稀疏注意力通论）
- [[智能体工具与长程任务]]：Harness/智能体与工具/智能体工具与长程任务.md（agent / 工具长程）
- 扫描表：模型与技术报告/SystemCard与TR扫描2025至2026.md

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

