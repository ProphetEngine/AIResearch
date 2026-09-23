---
title: Qwen3 Technical Report 深读笔记
topic: TR-Qwen3
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# Qwen3 Technical Report 深读笔记

> 攻坚线：**架构思想（主）** + **AI Infra（辅）**
> 锚点：Qwen Team, *Qwen3 Technical Report*（arXiv:2505.09388）
> 官方 PDF：`https://arxiv.org/abs/2505.09388`（复用已下载；pdfTeX CreationDate 2025-05-15 CST；35 页）
> 许可（报告摘要）：**Apache 2.0**；权重入口：Hugging Face / ModelScope / GitHub QwenLM/Qwen3

---

## 一、报告元信息

| 字段 | 核实值 |
|---|---|
| 标题 | Qwen3 Technical Report |
| 作者 | Qwen Team（正文 §6 列 Core Contributors / Contributors） |
| arXiv | **2505.09388**（页眉 arXiv:2505.09388v1 [cs.CL] **14 May 2025**） |
| PDF 本地 | `https://arxiv.org/abs/2505.09388` |
| HTML / PDF | https://arxiv.org/abs/2505.09388 ；https://arxiv.org/pdf/2505.09388 |
| 系列定位 | Qwen 家族最新一代开源权重 LLM；Dense + MoE；参数量约 **0.6B–235B** |
| 相对 Qwen2.5 | 多语从 **29 → 119** 语言/方言；预训练约 **36T** tokens（报告称相对 Qwen2.5 约 **2×** tokens、**3×** 语言覆盖） |
| 核心产品主张 | **同一权重**集成 thinking / non-thinking；**thinking budget** 控推理深度；小模型靠旗舰 **Strong-to-Weak Distillation** 省算力 |

**摘要级一句话（不外推）：**
Qwen3 把「慢想（多步推理）」与「快答（非思维）」写进统一框架，并按查询或 chat template 动态切换；同时用 thinking budget 在延迟与效果间自适应分配推理算力。

---

## 二、模型族与规模表（据报告 §2 / Table 1–2 / 对比表）

### 2.1 发布型号一览

| 型号 | 类型 | 总参（报告） | 激活参（报告） | Layers | Heads (Q/KV) | Experts (Total/Act) | Tie Emb | Context（表中） |
|---|---|---|---|---:|---|---|---|---|
| Qwen3-0.6B | Dense | ~0.6B | =总参 | 28 | 16 / 8 | — | Yes | **32K** |
| Qwen3-1.7B | Dense | ~1.7B | =总参 | 28 | 16 / 8 | — | Yes | **32K** |
| Qwen3-4B | Dense | ~4B | =总参 | 36 | 32 / 8 | — | Yes | **128K** |
| Qwen3-8B | Dense | ~8B | =总参 | 36 | 32 / 8 | — | No | **128K** |
| Qwen3-14B | Dense | ~14B | =总参 | 40 | 40 / 8 | — | No | **128K** |
| Qwen3-32B | Dense | ~32B | =总参 | 64 | 64 / 8 | — | No | **128K** |
| Qwen3-30B-A3B | MoE | **30B** | **3B** | 48 | 32 / 4 | **128 / 8** | — | **128K** |
| Qwen3-235B-A22B | MoE（旗舰） | **235B** | **22B** | 94 | 64 / 4 | **128 / 8** | — | **128K** |

> 注：Dense 总参以型号名为准（报告未在 Table 1 另列非嵌入 hidden 等细表）。MoE 总/激活以正文与 Table 5 等对比表一致写法为准（30B/3B；235B/22B）。

### 2.2 稠密骨干组件（§2）

与 Qwen2.5 同类组件：**GQA、SwiGLU、RoPE、RMSNorm pre-norm**。相对 Qwen2：

- **去掉** QKV-bias；
- **引入 QK-Norm**（稳定注意力训练）；
- Tokenizer：Qwen BBPE，词表 **151,669**。

### 2.3 MoE 相对 Qwen2.5-MoE 的差分（§2）

| 维度 | Qwen3-MoE（报告） |
|---|---|
| 专家粒度 | fine-grained expert segmentation（沿用 Qwen2.5-MoE / Dai et al. 思路） |
| 路由规模 | **128** total / 每 token **8** activated |
| Shared experts | **排除**（Unlike Qwen2.5-MoE） |
| 负载均衡 | **global-batch load balancing loss**（引 Qiu et al., 2025） |

报告宣称：同数据下 MoE 可用约 **1/5** 激活参逼近同系列 Dense；相对 Qwen2.5-MoE 可用 **<1/2** 激活参与更少总参打赢；相对 Qwen2.5 Dense 甚至可用约 **1/10** 激活参达到可比（§3.3 小结，属作者自评，跟读时对照 Table 3–8）。

---

## 三、训练与后训练要点（含 think / no_think）

### 3.1 预训练数据（§3.1）

- 规模：**约 36T** tokens；**119** 语言/方言。
- 扩量手段（报告写明）：
 1. **Qwen2.5-VL** 对大量 PDF 类文档做文本识别 → **Qwen2.5** 精炼，得数 T 级高质量文本；
 2. **Qwen2.5 / Qwen2.5-Math / Qwen2.5-Coder** 合成数 T 级多格式数据（教材、QA、指令、代码等）；
 3. 增补多语。
- 标注：多语数据标注系统覆盖 **>30T** tokens（教育价值、领域、安全等），支持**实例级**配比（相对源级/域级配比），用小代理模型做消融。

### 3.2 预训练三阶段（§3.2）

| 阶段 | 序列长 | 数据量级（报告） | 要点 |
|---|---|---|---|
| **S1 General** | **4,096** | **>30T** | 语言与通用世界知识；119 语 |
| **S2 Reasoning** | **4,096** | 约 **5T** 更高质量 | 提高 STEM/代码/推理/合成占比；**加速 LR decay** |
| **Long Context** | **32,768** | **数百 B** tokens | 75% 文本落在 16K–32K，25% 在 4K–16K；RoPE base **10k → 1,000,000**（**ABF**）；推理期叠 **YARN + Dual Chunk Attention (DCA)**，称可把序列容量提到约 **4×**（与表中 128K 上下文一致） |

另：按三阶段做 scaling-law 式超参预测（LR、batch 等），为每个 Dense/MoE 设定预测最优策略（§3.2 末）。

**报告未给出**与 DeepSeek-V3 同级的「GPU 型号 × 小时 / FP8 配方 / 并行拓扑」表 → 见第六节待核实。

### 3.3 后训练总览（§4 / Figure 1）

两大目标：

1. **Thinking Control**：统一 non-thinking / thinking，并可用 token budget 控思维深度；
2. **Strong-to-Weak Distillation**：小模型（及 30B-A3B）从旗舰蒸馏，省掉完整四阶段算力（报告称相对四阶段约 **1/10 GPU hours**）。

**旗舰路径（Qwen3-235B-A22B、Qwen3-32B）四阶段：**

`
Base → Stage1 Long-CoT Cold Start → Stage2 Reasoning RL (GRPO)
 → Stage3 Thinking Mode Fusion → Stage4 General RL
`

**轻量路径：** Base → **Strong-to-Weak Distillation**
蒸馏覆盖：Dense **0.6B / 1.7B / 4B / 8B / 14B** + MoE **30B-A3B**。

### 3.4 Stage 1–2：把「会想」训出来

**Long-CoT Cold Start（§4.1）**

- 题域：数学、代码、逻辑、一般 STEM；带可验证答案或代码测试。
- 查询过滤：用 Qwen2.5-72B-Instruct 去掉难验证/多子问/纯生成；并去掉「无 CoT 也能答对」的题，避免浅猜。
- 响应用 **QwQ-32B** 生成 N 候选；严滤错误终答、重复、猜答、思维与摘要不一致、语码混杂等。
- 目标：**植入推理范式**，样本与步数宜少，以免锁死后续 RL 空间。

**Reasoning RL（§4.2）**

- **3,995** 条 query–verifier；算法 **GRPO**（Shao et al., 2024）。
- 大 batch、每 query 高 rollout、off-policy 提样本效率；控制熵以平衡探索/利用。
- 例：Qwen3-235B-A22B 在 **170** 个 RL 步内 AIME’24 **70.1 → 85.1**（报告数字）。

### 3.5 Stage 3：Thinking Mode Fusion 与 `/think/no_think`（§4.3 / Table 9）

| 模式 | 用户侧标志 | Assistant 形态 |
|---|---|---|
| Thinking（默认） | `/think` 可省略 | `<think>{thinking}</think>` + response |
| Non-thinking | `/no_think` | **空** `<think></think>` + response |

- HF chat template 参数：`enable_thinking=False` 可关思维（脚注叙述；原文写作 `enable thinking=False`）。
- 多轮：随机插入多个 `/think/no_think`，**以最后一次标志为准**。
- Thinking 数据：对 Stage1 查询用 Stage2 模型做 **rejection sampling**，以免 SFT 伤 Stage2。
- Non-thinking 数据：代码/数学/指令遵循/多语/创作/QA/角色等；低资源语提高翻译占比。

**Thinking Budget（涌现，非专项训）：**
思维长度达用户阈值时，人工截断并插入固定英文 stop 指令再接 `</think>`，随后基于已有思维直接出最终答。报告强调该能力来自 mode fusion 的**自然涌现**。Figure 2：235B-A22B 在数学/代码/STEM 上随 budget **平滑涨分**；并称若输出超 32K 仍可能继续涨（留作未来工作）。

### 3.6 Stage 4：General RL（§4.4）

覆盖 **>20** 类任务，能力轴包括：指令遵循、格式遵循（含 `/think/no_think` 与 `<think>` 分隔）、偏好对齐、**Agent**（多轮真实环境反馈）、RAG 等专用场景。

三类奖励：

1. Rule-based；
2. Model-based **有参考答案**（Qwen2.5-72B-Instruct 打分）；
3. Model-based **无参考**（人类偏好训出的标量 RM）。

### 3.7 Strong-to-Weak Distillation（§4.5 / §4.7）

| 阶段 | 做法 |
|---|---|
| Off-policy | 教师在 `/think` 与 `/no_think` 下的输出做 response 蒸馏 → 学生学会推理 + 模式切换 |
| On-policy | 学生自采样序列；对齐教师（**Qwen3-32B 或 235B-A22B**）logits，最小化 **KL** |

Table 21（Qwen3-8B，自同一 off-policy 检查点起，仅数学/代码查询）：

| 方法 | AIME’24 | GPU Hours |
|---|---|---|
| Off-policy Distillation | 55.0 (pass@64 90.0) | — |
| + Reinforcement Learning | 67.6 (90.0) | **17,920** |
| + On-policy Distillation | **74.4 (93.3)** | **1,800**（约 RL 的 **1/10**） |

蒸馏相对 RL 还抬高 pass@64；RL 则未抬高 pass@64（报告观察）。

### 3.8 评测采样设定（§4.6 摘录）

- Thinking：temperature **0.6**，top-p **0.95**，top-k **20**；
- Non-thinking：temperature **0.7**，top-p **0.8**（同段后续配置）；
- 长文 RULER：YARN scaling factor=**4**；thinking mode 下 budget 设 **8192** 以防过长思维干扰检索（附录）。

---

## 四、架构与 Infra 亮点对照表

| 维度 | Qwen3 报告要点 | Infra / 架构跟读抓手 |
|---|---|---|
| 注意力 | GQA + **QK-Norm**；去 QKV-bias | 训练稳定性优先于「多一个 bias」 |
| 位置 / 长文 | 训至 **32K**；RoPE base **1e6**（ABF）；推 **YARN+DCA → ~4×** | 训练短、推理外推；表中 128K 与 4× 一致 |
| MoE | 128/8；**无 shared**；**global-batch LB** | 与 DeepSeek「aux-loss-free + shared」路线不同，勿混记 |
| Thinking 产品化 | 同权重 `/think/no_think` + **budget 涌现** | 属 [[推理时扩展TestTimeScaling]] test-time scaling 的「可旋钮」落地，非独立 o 系型号 |
| 后训练算力策略 | 旗舰四阶段；小模型 **logits KL 蒸馏** | Table 21：蒸馏 ~**1/10** GPU hours 且分数更好 |
| 数据 Infra | VL OCR + 系列模型合成 + 实例级标注配比 | 强调「标注→配比」管线，而非只堆 raw web |
| 集群 / 精度 | **未在报告给出** GPU 型号、并行度、FP8/BF16 配方 | 相对 V3 报告的 Infra 缺口 → 待核实 |
| 许可与交付 | Apache 2.0；开源权重 | 与 Llama 许可不可默认等同 |

---

## 五、与 [[开源与闭源前沿模型谱系]] 谱系条目的增量

对照 [[开源与闭源前沿模型谱系]] §3.3 / 第四节横切表，本深读**新增或加细**（非改写谱系结论）的点：

1. **完整 Dense/MoE 配置表**：Layers、Q/KV heads、Tie Embedding、各型号上下文 32K vs 128K（[[开源与闭源前沿模型谱系]] 仅列型号名与专家 128/8）。
2. **预训练三阶段量化**：S1 >30T @4K、S2 ~5T @4K、长文数百 B @32K、语料长度配比 75%/25%、ABF+YARN+DCA 机制链。
3. **后训练可复述数字**：Reasoning RL **3995** pairs、**GRPO**、AIME’24 **70.1→85.1 / 170 steps**；蒸馏 Table 21 GPU hours **17920 vs 1800**。
4. **Chat 协议细节**：空 think block、多轮「最后标志生效」、`enable_thinking=False`、budget 截断时的**固定英文 stop 指令原文**。
5. **General RL 奖励三分法**与 Agent 多轮真实环境反馈叙述（谱系未展开）。
6. **蒸馏覆盖清单**：明确 30B-A3B 走蒸馏而非旗舰四阶段。
7. **长文评测脚注**：thinking 在 RULER 上略降、作者归因「检索任务不靠推理、思维可能干扰」——谱系未写。
8. **与横切表一致的确认**：集群 GPU-hour **仍待核实**；报告主线为 LLM，多模态姊妹不在本 PDF 展开。

**不新增臆造：** 未声称报告未写的 hidden size、专家中间维、训练并行拓扑或 FP8。

---

## 六、待核实与引用

### 6.1 待核实（禁止编造）

| # | 项目 | 原因 |
|---|---|---|
| 1 | 预训练 / 后训练 **GPU 型号、卡数、总 GPU-hours**（蒸馏以外） | 正文未给 V3 级集群表；仅 Table 21 有 8B 局部 GPU hours |
| 2 | 训练精度（BF16/FP8 等）与并行策略（TP/PP/EP/DP） | 报告未写 |
| 3 | 各 Dense 的 hidden / FFN / 非嵌入参数精确表 | Table 1 无 Layers/Heads/Tie/Ctx，无 hidden 列 |
| 4 | MoE 专家 FFN 宽度、路由得分函数（softmax vs sigmoid 等） | 仅写 128/8、无 shared、global-batch LB |
| 5 | 推理默认上下文与部署推荐（vLLM 等）官方页数值 | 以模型卡 / 发布页为准，本 PDF 以 Table 1–2 与 YARN 叙述为准 |
| 6 | Qwen3 视觉/多模态姊妹型号与本系列权重关系 | 本报告主线 LLM；预训练用到 Qwen2.5-VL 作 OCR 工具 |
| 7 | `/think` 标志在 system 与 user 的产品默认优先级 | 报告写可放 user query **或** system message，产品默认需模型卡核实 |
| 8 | 报告之后的 Qwen3 系列增量型号 / 量化版 | 超出本 PDF 提交日（2025-05-14） |

### 6.2 引用

| 编号 | 文献 | 日期 | URL / 路径 |
|---|---|---|---|
| [QWEN3] | Qwen3 Technical Report | arXiv Submitted **2025-05-14**（v1 页眉） | https://arxiv.org/abs/2505.09388 ；PDF https://arxiv.org/pdf/2505.09388 |
| [QWEN3-PDF] | 本地副本 | CreationDate 2025-05-15 CST | `https://arxiv.org/abs/2505.09388` |
| [[开源与闭源前沿模型谱系]] | 开源与闭源前沿模型谱系 | 笔记 date 2026-09-22 | [[开源与闭源前沿模型谱系]] |

### 6.3 跟读一句话

> **Qwen3 = Dense+MoE 全家桶 + 同权重 think/no_think（可 budget）+ 36T/119 语三阶段预训练 + 旗舰四阶段（Cold-start→GRPO→Fusion→General RL）/ 小模型强师蒸馏。**

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

