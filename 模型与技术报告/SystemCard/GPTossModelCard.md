---
topic: GPTossModelCard
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
---

# 3：gpt-oss-120b / gpt-oss-20b Model Card 深读

> 攻坚线：**架构思想（主：开源权重 MoE + harmony/可变 reasoning effort + agentic 工具）** + **评测字段（辅：推理/编码/工具/健康，开源对齐）**
> 锚点：OpenAI, *gpt-oss-120b & gpt-oss-20b Model Card*（封面日期 **August 5, 2025**）
> 官方 PDF（同源卡，文件哈希不同）：
> - CDN：`https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf`（**35** 页 A4；Creator: LaTeX with hyperref；CreationDate **2025-08-12** CST；3,144,103 bytes）← https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf
> - arXiv：`https://arxiv.org/abs/2508.10925`（**35** 页；Title: *gpt-oss-120b & gpt-oss-20b Model Card*；3,049,591 bytes）← https://arxiv.org/pdf/2508.10925 ；API：**2508.10925v1** \[cs.CL\] published **2025-08-08** UTC（换算 Asia/Shanghai：**2025-08-09 03:24 CST**）
> 对照：模型与技术报告/SystemCard/GPT6AstraSystemCard.md（闭源旗舰 **System Card** / Preparedness 全章）；模型与技术报告/SystemCard/GPT5SystemCard.md 等 GPT-5 系；开源 MoE 对照可点 [[混合专家架构]] / DeepSeek / Qwen 笔记，**不**外推参数拓扑
> **划界：** 只写 **OpenAI 开源权重推理/agentic 增量**（可下载权重、公开 MoE/注意力配方、harmony、effort、工具 harness、Table 3 能力表）。**勿重写 [[GPT6AstraSystemCard]] Astra 安全全章**（Cyber Critical、CoT controllability、misalignment monitoring 等）——本卡 §3–5 Preparedness 仅作 **开源风险剖面摘要 + 交叉链**。
> **禁止编造：** 未给的预训练 token 总量、蒸馏配方细节、专家负载均衡损失、未读清的 Figure 柱高，一律不写主张；数字锚定 Table 1/2/3 与正文句。

---

## 1. 元信息与一句话抓手

| 字段 | 核实值（PDF / / arXiv API / 博文） |
|---|---|
| 标题 | gpt-oss-120b & gpt-oss-20b Model Card |
| 作者 | OpenAI（卡末 Contributors 长名单；arXiv 条目署名 OpenAI 等） |
| 文档自我定位 | **model card**（非 system card）：权重将嵌入多方维护的多类系统；默认跟 OpenAI safety policies，但下游须自建系统级护栏 |
| 封面日期 | **August 5, 2025** |
| arXiv | **2508.10925v1** \[cs.CL / cs.AI\]；published **2025-08-08** UTC |
| 页数 | **35**（A4） |
| 许可 | **Apache 2.0** + 「gpt-oss usage policy」（Introduction；博文同） |
| 模态 | **text-only** |
| 分发（博文 Availability） | Hugging Face 权重（原生 **MXFP4**）；harmony renderer（Python/Rust）；PyTorch / Apple Metal 参考推理；多平台合作（Azure、vLLM、Ollama、llama.cpp、LM Studio、AWS 等——博文列举） |
| API 兼容叙事 | 兼容 **Responses API**；支持 **Structured Outputs**；博文：未来「may consider API support for gpt-oss」 |
| Knowledge cutoff | **June 2024**（§2.4） |
| 相对 Astra / GPT-5 系 | 闭源旗舰卡 **已入库** → 本卡 **不**复述 Astra Preparedness 域阈/监控栈；只录 gpt-oss **开源**字段 |

**型号（Table 1 + §2 正文 + 博文表）：**

| 型号 | 层数 | Total / Active（报告口径） | Experts / Top-k | Checkpoint（Table 1） | 部署内存口号（§2.1 / 博文） |
|---|---|---|---|---|---|
| **gpt-oss-120b** | **36** | **116.8B** total / **5.1B** active（Table 1：Total 116.83B，Active 5.13B） | **128** / **4** | **60.8 GiB** | 单卡 **80 GB** GPU |
| **gpt-oss-20b** | **24** | **20.9B** total / **3.6B** active（Table 1：20.91B / 3.61B） | **32** / **4** | **12.8 GiB** | 约 **16 GB** 内存 |

Table 1 分项：120b — MLP 114.71B，Attention 0.96B，Embed+Unembed 1.16B；20b — MLP 19.12B，Attention 0.64B，Embed+Unembed 1.16B。脚注：Unembedding 计入 active，embeddings 不计。命名「120b/20b」为简化，技术参量为 116.8B / 20.9B。

**一句话抓手：** 这是 OpenAI **自 GPT-2 以来首个正式开源权重语言模型卡**（博文明文）：**Apache 2.0** 的 text-only **MoE 推理模型**，用 **MXFP4 MoE 权重**压到单 80GB / 16GB 可跑，产品轴落在 **harmony 对话格式、low/medium/high 可变 reasoning effort、浏览/Python/开发者函数** 的 agentic 工作流；能力表（high）上 120b 叙事为 **超过 o3-mini、逼近 o4-mini**，20b **对标 o3-mini 量级**。安全上强调开源 **可被下游微调绕过拒答** 的不同风险剖面，并对 120b 做了 **对抗微调 Preparedness**——结论写「默认与对抗微调均未达 High」（Tracked Categories）——细节 **交叉 [[GPT6AstraSystemCard]]，不在此重写 Astra 全章**。

---

## 2. 相对闭源 GPT 旗舰卡 / 既有开源 MoE 的「开源增量」对照

> 左列锚本 PDF + 博文；右列仅标已入库闭源卡覆盖面。禁止把 Astra/GPT-5 未公开架构数字回填到 gpt-oss，也禁止用 DeepSeek/Qwen MoE 拓扑「补全」本卡未写字段。

| 维度 | GPT-5 系 / Astra（已入库闭源卡） | **gpt-oss（本卡）** | 开源增量读法 |
|---|---|---|---|
| 文档形态 | System Card / 长安全章（Astra **118** 页量级） | **35** 页 **Model Card**（明确不用 system card 名义） | 技术可核对深度集中在 §2 架构/训练 + Table 3；安全 §3–5 是开源专用剖面 |
| 权重 | API / 产品；**无可下载** LM 权重（相对本议题） | **Apache 2.0** HF 权重 + 参考实现 | **本议题核心增量**；博文称自 GPT-2 后首个 open-weight LM |
| 参数 / MoE | 旗舰卡多未公开总参/专家 | Table 1 + §2.2：**总参/激活/专家数/top-4/层数/残差维** 齐全 | 首次在 OpenAI 近月线给出**可下载** MoE 参量表 |
| Reasoning 旋钮 | o 系列 / 产品 thinking；Astra 另有监控叙事 | System 里 `"Reasoning: low|medium|high"`；Figure 3 显示 AIME/GPQA **随 effort 平滑 TTS** | 开源侧把 effort **写进可复现协议** |
| 对话协议 | API roles | **harmony**：roles + **channels**（analysis / commentary / final）；指令层级 System>Developer>User>Assistant>Tool | 部署关键路径；多轮须去掉历史 assistant reasoning traces（§2.5.1） |
| 工具 | 产品内置 browsing/code 等 | 显式训 **browsing / python(Jupyter) / 任意 developer functions**；可开关 | agentic 开源样本；参考 harness 随开源实现 |
| 上下文 | 产品卡各自口号 | 稠密层 **YaRN 至 131,072**；博文写 **128k** | 以卡内 131,072 / 博文 128k 为准，**勿**抄 Astra 窗长 |
| Preparedness | Astra：Cyber **Critical** 等（见 [[GPT6AstraSystemCard]]） | 默认 **未达** 三类 Tracked 的 High；对抗 FT Bio/Cyber 亦 **未达 High**；并问「是否显著推进开源生物前沿」→ 卡内答 **否** | **只录开源结论句**；域评测表/红队方法 **交叉链 [[GPT6AstraSystemCard]] / 本卡 §5，不重写** |

**增量一句话：** 相对闭源旗舰「能力/安全产品字段」，gpt-oss 可研增量几乎全部落在 **可下载 MoE + MXFP4 部署配方 + harmony/effort/工具协议 + Table 3 开源对齐榜**；Astra 级安全监控与 Critical 叙事 **点到为止**。

---

## 3. 架构主轴（§2.1–2.2）

### 3.1 骨干

- Autoregressive **MoE Transformer**；自称建于 GPT-2 / GPT-3 架构传统。
- 残差维 **2880**；**Pre-LN** + **RMSNorm**（attention / MoE 块前）。
- MoE：线性 router → 每 token **top-4**；权重为所选专家上 router 的 **softmax**；专家激活 **gated SwiGLU**（脚注：实现含 clamping 与 residual，称 unconventional）。
- 专家数：**120b → 128**；**20b → 32**。

### 3.2 注意力与长上下文

| 机制 | 报告主张 | 出处 |
|---|---|---|
| 模式交替 | 跟随 GPT-3：**banded window** 与 **fully dense** 交替；带宽 **128** tokens | §2.2 |
| 头配置 | **64** query heads，dim **64**；**GQA**，**8** KV heads | §2.2；博文称 group size 8 |
| 位置 | **RoPE**；稠密层用 **YaRN** 扩到 **131,072** | §2.2 |
| Softmax bias | 每头学到的 denominator bias（类 off-by-one / **attention sinks**）→ 可对任意 token「不关注」 | §2.2 |

### 3.3 量化（§2.1）——部署关键旋钮

- 后训练把 **MoE 权重**量化到 **MXFP4**（**4.25 bits/param**）。
- MoE 权重占总量 **90%+** → 120b 进单 **80GB** GPU；20b 可在约 **16GB** 系统跑。
- Checkpoint 尺寸见 Table 1（60.8 / 12.8 GiB）。

→ Infra 读法：这是「开源 MoE × 低比特专家权重 × 单卡」配方样本；**未**公开训练并行拓扑、专家并行策略细节。

---

## 4. Tokenizer / 预训练 / 算力（§2.3–2.4）

| 项 | 核实值 |
|---|---|
| Tokenizer | **o200k_harmony**（TikToken 开源）；在 GPT-4o / o4-mini 的 o200k 上扩展 harmony 专用 token；词表 **201,088** |
| 数据 | text-only；「trillions of tokens」；侧重 STEM / coding / general knowledge；多为英语（博文） |
| 安全过滤 | 预训练复用 GPT-4o 的 **CBRN** 有害内容过滤，尤其生物安全相关 |
| Cutoff | **June 2024** |
| 硬件/框架 | **NVIDIA H100**；PyTorch + 专家优化 **Triton** kernels；**Flash Attention** |
| 算力 | 120b：**2.1 million H100-hours**；20b：约 **少一个数量级（almost 10× fewer）** |

arXiv **abstract** 另写「large-scale **distillation** and reinforcement learning」；正文 §2.5 主轴是「similar **CoT RL** techniques as OpenAI o3」、博文写「similar process as used for **o4-mini**（SFT + high-compute RL）」——**蒸馏具体配方卡内未展开** → 记「abstract 提及 distillation；正文展开 RL/SFT」，**禁止**编造蒸馏数据/教师型号表。

---

## 5. Post-training：harmony · effort · agentic 工具（§2.5）——本卡产品主轴

### 5.1 Harmony Chat Format（§2.5.1）

- 专用 chat format：**特殊 token** 划消息边界；关键字标明 author/recipient（User / Assistant 等）。
- Roles：与 API 相同的 **System / Developer**；冲突解决层级：
 **System > Developer > User > Assistant > Tool**
- **Channels**（可见性）：
 - `analysis` — CoT
 - `commentary` — function / tool calling
 - `final` — 对用户可见答案
- 支持 CoT 内交错工具、向用户展示 preamble / 长计划。
- 部署要点：多轮对话中 **应移除** 过往 assistant 轮的 reasoning traces；附录 Table 17/18 有样例。
- 开源实现 + guide 被标为「critical to deploy … properly」。

### 5.2 Variable Effort Reasoning（§2.5.2 + Figure 3）

- 三档：**low / medium / high**；在 system prompt 插入如 `"Reasoning: low"`。
- 更高档 → 平均 **CoT 更长**；Figure 3：AIME / GPQA 上 accuracy 对 CoT+Answer 长度呈 **平滑 test-time scaling**。
- 评测默认：canonical 榜报 **high** + default system prompt 的 pass@1（§2.6）。

### 5.3 Agentic Tool Use（§2.5.3）

训了三类工具（system 可声明启用/关闭）：

1. **Browsing**：search / open，补 cutoff 后事实。
2. **Python**：stateful **Jupyter**。
3. **Arbitrary developer functions**：在 Developer 消息用 harmony 定义 schema（类 API）；可交错 CoT、调用、响应、中间用户可见消息、最终答案。

编码评测另用类似 Codex CLI 的 **terminal / exec** 工具（with/without tools 双列，Figure 2 / Table 3）。

### 5.4 CoT 监督立场（博文 Chain-of-thought）

- 明确：**未**对 CoT 做直接对齐监督（自 o1-preview 原则）；希望开源「非监督 CoT」便于社区研究 **CoT monitoring**。
- 开发者注意：应用中 **不应直接把 CoT 展示给终端用户**（可能含幻觉/有害内容/违背最终输出约束的语言）。
- 博文例：系统禁止说「5」时，**final 服从**、**CoT 常显式讨论如何违规**——开源监控研究的直观样本。

---

## 6. 能力评测（§2.6 + Table 2/3）——开源对齐字段

> 主表 **Table 3**（low / medium / high）。对照叙事（Figure 1–2 图注 + 博文）：120b **surpasses o3-mini、approaches o4-mini**；20b **surprisingly competitive / matches or exceeds o3-mini**（部分域）。Figure 柱与 o3/o4 精确读数 ** 图轴乱码** → **不以读图编造友商分**；友商对比以正文定性 + 博文句为准。

### 6.1 Table 3 精选（Accuracy % / Score % / Elo）

| Benchmark | 120b low / med / **high** | 20b low / med / **high** |
|---|---|---|
| AIME 2024 (no tools) | 56.3 / 80.4 / **95.8** | 42.1 / 80.0 / **92.1** |
| AIME 2024 (with tools) | 75.4 / 87.9 / **96.6** | 61.2 / 86.0 / **96.0** |
| AIME 2025 (no tools) | 50.4 / 80.0 / **92.5** | 37.1 / 72.1 / **91.7** |
| AIME 2025 (with tools) | 72.9 / 91.6 / **97.9** | 57.5 / 90.4 / **98.7** |
| GPQA Diamond (no tools) | 67.1 / 73.1 / **80.1** | 56.8 / 66.0 / **71.5** |
| GPQA Diamond (with tools) | 68.1 / 73.5 / **80.9** | 58.0 / 67.1 / **74.2** |
| HLE (no tools) | 5.2 / 8.6 / **14.9** | 4.2 / 7.0 / **10.9** |
| HLE (with tools) | 9.1 / 11.3 / **19.0** | 6.3 / 8.8 / **17.3** |
| MMLU | 85.9 / 88.0 / **90.0** | 80.4 / 84.0 / **85.3** |
| SWE-Bench Verified | 47.9 / 52.6 / **62.4** | 37.4 / 53.2 / **60.7** |
| Tau-Bench Retail | 49.4 / 62.0 / **67.8** | 35.0 / 47.3 / **54.8** |
| Tau-Bench Airline | 42.6 / 48.6 / **49.2** | 32.0 / 42.6 / **38.0** |
| Aider Polyglot | 24.0 / 34.2 / **44.4** | 16.6 / 26.6 / **34.2** |
| MMMLU (Average) | 74.1 / 79.3 / **81.3** | 67.0 / 73.5 / **75.7** |
| HealthBench | 53.0 / 55.9 / **57.6** | 40.4 / 41.8 / **42.5** |
| HealthBench Hard | 22.8 / 26.9 / **30.0** | 9.0 / 12.9 / **10.8** |
| HealthBench Consensus | 90.6 / 90.8 / **89.9** | 84.9 / 83.0 / **82.6** |
| Codeforces Elo (no tools) | 1595 / 2205 / **2463** | 1366 / 1998 / **2230** |
| Codeforces Elo (with tools) | 1653 / 2365 / **2622** | 1251 / 2064 / **2516** |

**读表要点（正文）：**

- 数学尤强；AIME 高档可到 **~20k CoT tokens/题** 量级（§2.6.1）。
- 知识向（GPQA）20b 因规模落后更明显。
- 工具对 AIME/HLE/Codeforces 等有增益；Airline 上 20b high（38.0）**低于** medium（42.6）——**照录，不圆场**。
- Health：正文称 120b **nearly matches o3** on HealthBench / Hard，并 **显著优于** GPT-4o、o1、o3-mini、o4-mini；博文免责：**不替代医疗专业人员、非诊疗用途**。
- MMMLU（Table 2）：14 语；120b high Average **81.3** vs o4-mini-high **85.2**、o3 **88.8**（表内 baselines）；Swahili/Yoruba 明显更低（120b high 72.3 / 62.4）。

### 6.2 与 agent / 工具线的咬合（不展开他篇）

| 议题 | 本卡只点到 |
|---|---|
| [[智能体工具与长程任务]] / [[代码智能体Harness史线]] / **[[ToRL工具集成强化学习]] ToRL** | developer functions + terminal tool 评测；**不是** tool-use RL 算法专篇 |
| τ-Bench（[[评测与排行榜可靠性]] 周边） | Retail / Airline 双列；agentic function-calling 字段 |
| [[推理时扩展TestTimeScaling]] test-time scaling | Figure 3 effort 曲线；无 budget API 数值产品名 |
| [[计算机使用智能体]] computer-use | **本卡无** OSWorld/Operator；browsing ≠ 桌面 computer-use |

---

## 7. 安全与 Preparedness（§3–5）——摘要 + 交叉链，勿重写 Astra

> **划界执行：** 下列仅保留开源卡特有结论与默认安全评测骨架；**不**展开 Astra 的 Cyber Critical、CoT controllability 百分比、misalignment monitoring 部署栈等（见 模型与技术报告/SystemCard/GPT6AstraSystemCard.md）。

### 7.1 方法论立场（§3）

- Post-training：**deliberative alignment** → 拒答 / jailbreak 鲁棒 / **instruction hierarchy**。
- 开源特有：下游可改权重 → 风险评测「应覆盖恶意方可实现的修改（含 fine-tune）」；卡内对 120b 做了 **内部对抗微调变体（不发布）**。
- 默认模型：三类 Tracked Categories（Bio/Chem、Cyber、AI Self-Improvement）**均未达 High 指示阈**。
- 两问两答（Introduction / §3）：
 1. 对抗 FT 能否把 Bio/Chem 或 Cyber 推到 High？→ SAG 审阅后：**否**（即便用 OpenAI 自有训练栈）。
 2. 发布是否显著推进**开源**生物能力前沿？→ 多数评测上已有其他开源模型接近 120b → **认为不太可能显著推进**。

### 7.2 默认安全评测骨架（§4，不抄全表）

卡内覆盖：Disallowed Content（含更新的 **Production Benchmarks**）、Jailbreaks、Instruction Hierarchy、Hallucinated CoT、Hallucinations、Fairness/Bias 等。正文定性：gpt-oss 与 **o4-mini** 大体同级（具体分数表见 PDF §4，**若需逐格引用回原文**，勿与 Astra 表合并）。

### 7.3 Preparedness §5（仅结论指针）

- §5.1 Adversarial Training + 外部安全专家反馈（附录 2：采纳 / 未采纳建议）。
- §5.2 Capability findings：Bio/Chem、Cyber、AI Self-Improvement（含 SWE-bench Verified N=477、OpenAI PRs、PaperBench 等子节）。
- → **完整域分数与红队程序：读本 PDF §5 或交叉 [[GPT6AstraSystemCard]] 的框架术语，不在本笔记复述为「Astra 同款结论」。** Astra（2026-09）与 gpt-oss（2025-08）**代际与部署形态均不同**，禁止时间线混读。

### 7.4 博文附加

- **Red Teaming Challenge**（$500,000 奖金池）→ 结束后将发报告并开源基于验证发现的评测集（博文；非本 PDF 正文义务）。

---

## 8. 待核实 / 报告内张力

1. **CDN PDF vs arXiv PDF：** 同为 35 页、同日封面；文件 MD5 不同；arXiv 版页眉含 `arXiv:2508.10925v1`。正文抽取几乎同构 → 笔记以 **CDN + Table 数字** 为主，arXiv 作可引用 preprint。
2. **「蒸馏」：** abstract 有、§2.5 正文未展开配方 → 标「提及未展开」。
3. **Post-train 参照系：** 正文「similar CoT RL as **o3**」vs 博文「similar process as **o4-mini**」——并存照录。
4. **Figure 1/2/4 友商精确柱高：** 需读图；本笔记未把乱码 OCR 当数。
5. **Tau-Bench Airline 20b：** high < medium（Table 3）——保留异常，待复现或勘误。
6. **API 托管：** 博文称 gpt-oss 适合自托管微调；平台 API「仍是多模态/内置工具最佳选项」；「may consider」未来 API 支持——**非**已上架主张。

---

## 9. 可跟读摘要（中文）

OpenAI 在 **2025-08-05** 放出 **gpt-oss-120b / 20b**：Apache 2.0、纯文本、**MoE**（120b：约 **117B** 总参 / **5.1B** 激活 / **128** 专家 top-4；20b：约 **21B** / **3.6B** / **32** 专家），MoE 权重 **MXFP4**，目标是一张 **80GB** 卡或 **16GB** 级机器就能跑开源推理模型。架构上是熟悉的 Pre-LN MoE + **窗口/稠密交替注意力** + GQA + RoPE/**YaRN(128k 级)**；真正当产品说明书的是 **harmony 格式**（analysis/commentary/final 通道与角色层级）、**低/中/高 reasoning effort**，以及浏览 / Python / 自定义函数这套 **agentic** 工具叙事。榜上（high）数学与工具调用很亮，120b 对标话术是「超 o3-mini、近 o4-mini」，健康榜甚至喊到逼近 o3——但 cutoff 停在 **2024-06**，且博文写明不替代医生。安全上这篇卡的新意是 **开源可被恶意微调** 的剖面，并对 120b 做了对抗微调 Preparedness；结论写默认与对抗版都 **未达 High**。闭源旗舰那套 Astra 监控与 Critical 判定，去读 **[[GPT6AstraSystemCard]]**，这里不重写。

---

## 10. 来源与抽取

| 源 | 路径 / URL |
|---|---|
| CDN 模型卡 PDF | `https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf` ← https://cdn.openai.com/pdf/419b6906-9da6-406c-a19d-1bb078ac7637/oai_gpt-oss_model_card.pdf |
| arXiv PDF | `https://arxiv.org/abs/2508.10925` ← https://arxiv.org/pdf/2508.10925 （abs: https://arxiv.org/abs/2508.10925） |
| 安全交叉 | 模型与技术报告/SystemCard/GPT6AstraSystemCard.md（勿在本文件重写） |

**检索截止：** 2026-09-22（Asia/Shanghai，CST）。数字与断言均来自上述 PDF/博文；未读清的图柱、未公开的蒸馏配方与专家并行细节未写入主张表。

## 相关笔记

- [[多智能体辩论|Multi-Agent Debate]]
- [[形式化验证与LLM|Formal Verification for LLM]]
- [[GPTossModelCard|gpt-oss Model Card]]
- [[计算机使用智能体|Computer-Use Agents]]
- [[ToRL工具集成强化学习|Tool-Use RL / ToRL]]

