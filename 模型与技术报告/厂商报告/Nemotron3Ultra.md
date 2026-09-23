---
title: "开源旗舰：Nemotron 3 Ultra（≠ Nemotron-CC）"
topic: Nemotron3Ultra
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.15007 # 3.8M / 65p；≪10MB → 官方 HTTPS 外链
 - https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf # 3.7M / 65p；辅 Labs → ，仅 URL+抽取
aux:
 - https://arxiv.org/abs/2606.15007
 - https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf
 - https://github.com/NVIDIA-NeMo/Nemotron
 - https://github.com/NVIDIA-NeMo/Evaluator/blob/main/examples/nemotron/nemotron-3-ultra
 - https://github.com/NVIDIA-NeMo/Gym
 - https://github.com/NVIDIA-NeMo/Skills
arxiv: ["2606.15007"]
related: ["NemotronCC数据策展", "SEA-LION低资源区域模型", "OLMo3全栈开放配方", "MTP训练范式", "混合专家架构"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 开源旗舰：Nemotron 3 Ultra（≠ Nemotron-CC）

> **定位**：Nemotron 开源旗舰主题轴——立 NVIDIA **Nemotron 3 Ultra** 模型技术报告：Hybrid Mamba–Attention + LatentMoE、面向 **agentic reasoning** 的预训练 / 后训练 / 量化 / 推理配方与文内评测。主文：NVIDIA *Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning*（arXiv:**2606.15007**v1，**12 Jun 2026**）。
> **攻坚线**：**架构思想（主）** + **评测字段（文内 agent / 推理表，辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[NemotronCC数据策展]]**：禁止重写 **Nemotron-CC 语料清洗章**（过滤 / 去重 / 质量分类 / 合成改写管线）。本卡预训练数据只记 **Ultra 相对 Super 新增发布集 + 两阶段配比骨架**，不展开通用网页策展全文。
> - **≠ [[SEA-LION低资源区域模型]]**：禁止写成 **SEA-LION 区域 CPT / OPD / SEA-HELM**；SEA 卡里 Ultra 仅作教师信号源一句 → 本卡才是 **基座旗舰 TR**。
> - **≠ 其他厂商 TR**：禁止把本卡写成 DeepSeek / Qwen / Kimi / GLM / OLMo 等对照全文；对照模型只出现在 **文内 Table 2 / Table 10 数字转述**。OLMo 3 开放配方旗舰见 **[[OLMo3全栈开放配方]]**。
> **禁止编造**：主张、表数字、吞吐倍率一律锚定官方 PDF（2026-09-22 CST）；图内未抽出的精确曲线点标 **待核实读图**。**禁**下权重 / 大数据集。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主文** | *Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning* | arXiv:**2606.15007**v1 \[cs.CL\] **12 Jun 2026**（PDF 页眉 **2026-6-16**） | `https://arxiv.org/abs/2606.15007` | **3.8M**（3,973,681 B ≈ **3.79MiB**） | **65** A4 | |
| **辅·NVIDIA Labs** | 同题 TR（页眉 **2026-6-9**；无 arXiv 水印） | https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf | —（未入库；[`Labs TR`](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf)） | **3.7M**（3,876,804 B ≈ **3.70MiB**） | **65** A4 | |

**体积判定（2026-09-22 CST，`stat` ）：** 主 **3,973,681 B**、辅 **3,876,804 B**，均 **≪10MB** → **官方 HTTPS 外链**。md5 不同（`dc78208b…` vs `5685e668…`）→ 视为 **近同文两版**；主张以 **arXiv 主文抽取**为准，辅仅作交叉核验。

**一手 PDF：** **有** — 两源 `curl` → 200； Title（主）=`Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning`。

**开源入口（文内明示，禁下权重）：**
- 配方仓：https://github.com/NVIDIA-NeMo/Nemotron
- 评测示例：https://github.com/NVIDIA-NeMo/Evaluator/blob/main/examples/nemotron/nemotron-3-ultra
- HF：文称开源 **Base / Post-Trained / NVFP4 量化** checkpoint，以及训练数据与 recipe（具体 repo ID 以 HF 检索为准，本卡不编造 ID）。

**一句话抓手：** **550B total / 55B active** Hybrid Mamba–Attention LatentMoE；**20T** 预训练 + **1M** 上下文扩展；后训练 **SFT → RLVR → 两轮 MOPD（Multi-teacher On-Policy Distillation）→ MTP Boosting**；宣称相对公开旗舰最高约 **∼6×** 推理吞吐（文内 Fig.1：8K in / 64K out、GB200、NVFP4；对 GLM-5.1 / Kimi-K2.6 / Qwen-3.5 为 **5.9× / 4.8× / 1.6×**），精度持平（on-par accuracy）。

---

## 二、议题边界：旗舰模型 TR ≠ 语料清洗 ≠ 区域适配 ≠ 他厂通史

### 2.1 相对相邻笔记只取接口

| 已入库 / 同主题 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[NemotronCC数据策展]]** | Ultra 预训练「网页 / Crawl++」作配比分量名一句；新增 Legal / Specialized 等 **发布集索引** | Nemotron-CC Justext→分类器→合成改写 **全文** |
| **[[SEA-LION低资源区域模型]]** | SEA-LION 以 Ultra 为 OPD 教师 → 本卡提供教师侧配方与 agent 评测 | SEA CPT token 量、SEA-HELM 语种表 |
| **[[OLMo3全栈开放配方]]** | 「工业开源性能旗舰」对照位一句 | OLMo 3 全栈开放数据配方 |
| **[[MTP训练范式]] / [[混合专家架构]]** | MTP / MoE 名词与稀疏激活接口 | MTP 训练稳定性通史、通用 MoE 综述 |
| **其他厂商 TR** | Table 2 / 10 中的对照分 | DeepSeek / Qwen / Kimi / GLM 架构与训练全文 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| Hybrid 层型、Table 1 维度、LatentMoE / MTP / NVFP4 预训练要点 | 把 §2.3 写成 [[NemotronCC数据策展]] 语料清洗重写 |
| 后训练管线 Fig.9：SFT → RLVR → MOPD Warmup → 两轮 MOPD → MTP Boosting；reasoning budget | SEA 区域 CPT；他厂系统卡复述 |
| Base Table 2；Post Table 10（agent / 推理 / 长上下文）；吞吐口径（Fig.1） | 未给出的生产 SLA；图内未读出的精确柱高外推 |

跟读口诀：

`
[[NemotronCC数据策展]] = Nemotron-CC：网页怎么洗成可训语料
[[SEA-LION低资源区域模型]] = SEA-LION：强基座如何 CPT+OPD 成区域模型
[[OLMo3全栈开放配方]] = OLMo 3：可复现开放研究配方旗舰
[[Nemotron3Ultra]] = Nemotron 3 Ultra：NVIDIA 开源 agentic 旗舰怎么训、怎么评、怎么快
`

---

## 三、架构与预训练（§2）

### 3.1 规模与层型（Table 1 / Fig.2）

与 **Nemotron 3 Super** 同族 Hybrid Mamba–Attention MoE，扩到 **550B total / 55B active**；MoE 用 **LatentMoE**；预训练带 **2** 个 **共享权重** MTP head（单 Attention + 单 MoE），服务投机解码。

| 配置（Table 1） | 值 |
|---|---|
| Total Layers | **108** |
| Model Dimension | **8192** |
| Q / KV Heads | **64 / 2**；Head Dim **128** |
| Mamba State / Groups / Heads / Head Dim | **128 / 8 / 256 / 64** |
| Expert Hidden / Shared Expert Intermediate | **5120 / 10240** |
| Experts per layer / Top-𝑘 | **512 / 22** |
| MoE Latent Size | **2048** |
| MTP layers（shared） | **2** |

Fig.2：层块按 **Mamba-2 × Attention** 混合重复（文内示意倍数 x3 / x2 / x3 / x3 / x4），MoE 稀疏叠在 LatentMoE 上——细节以 PDF 图为准，**禁止**自造未写明的精确交错公式。

### 3.2 NVFP4 预训练与稳定性（§2.2 / §2.7）

- 与 Super 同款 **NVFP4** 配方（Transformer Engine cuBLAS NVFP4 GEMM；E2M1 + 2D block 权重量化等）。
- 末 **15%** 网络（**16** 层）、Mamba 输出投影、latent / QKV / attention 投影、MTP、embedding 保持更高精度。
- 文称此为迄今 **最大规模**稳定准确的 NVFP4 训练演示之一。
- 在 5T / 10T / 16T 分支切 BF16 的相对 train loss gap 平均 **<0.4%**（§2.2）。
- §2.7：训练出现过 loss 发散；文记 MTP-2 loss 先于主 CE 尖刺；回滚并恢复 **全 FP32 gradient reduction** 后复稳；第二处发散在 ~15T 附近用 rewind 等缓解。**本卡只记现象与文内对策名，不外推未写明的根因定论。**

### 3.3 数据与课表（≠ [[NemotronCC数据策展]]）

**只记 Ultra 相对 Super 的增量与课表骨架**（禁止清洗管线重写）：

| 文内发布 / 增量（Intro / §2.3） | 角色（文内） |
|---|---|
| Nemotron-Pretraining-Code-v3 | **173B** tokens 新鲜代码（GitHub → **2025-09-30**） |
| Nemotron-Pretraining-Legal-v1 | 法律合成；Nano 消融 proxy LegalBench **64.6→74.7** |
| Nemotron-Pretraining-Specialized-v1.2 | 事实召回 / 道德情景 / 多样生成与选择题 |
| Nemotron-Posttraining-v3 | 后训练 agentic / reasoning / 通用（SFT+RL） |

- **总量**：**20T** 文本；**Warmup–Stable–Decay**：warmup **200B** → peak LR **2.5×10⁻⁴**；末 **5T** minus-sqrt 衰减至 **2.5×10⁻⁶**。
- **两阶段**：约前 **15T（~75%）** 偏多样性；后 **5T** 偏高质量（Fig.4）。网页类（crawl / syn-crawl）仍是最大块——**名称索引即可，过滤细节见 [[NemotronCC数据策展]]**。
- **长上下文 CPT（§2.5）**：恒定 LR **2.5×10⁻⁶**；**92%** iter 用 **1,048,576（1M）**，**8%** 用 **4K**（不混长）；长上下文数据 **46%** + Phase-2 **54%**；**未**混入 RULER 式数据。GB200，32-way CP 等并行配置见文。

### 3.4 Base 评测摘录（Table 2，抽关键列）

对照：DeepSeek-V3.2-Exp-Base、Mistral-Large-3-675B-Base-2512、Kimi-K2-Base、GLM-4.5-Base（文内全名见表注）。**粗体为文内「Best available」口径下 Ultra 占优项（转述，非本卡另评）。**

| 任务 | Ultra Base | 备注 |
|---|---|---|
| MMLU-Pro（5-shot CoT EM） | **79.07** | 显著高于表内对照 |
| GPQA（5-shot CoT EM） | **50.00** | |
| MATH（4-shot EM） | **82.00** | |
| HumanEval（pass@1 n=32） | **83.84** | |
| MBPP-Sanitized | **85.97** | |
| MGSM（8-shot native CoT） | **87.73** | |
| RULER 64K / 128K / 1M | **95.30 / 92.49 / 76.83** | 1M 多项对照缺测 |

GSM8K 上 Ultra **88.10**，低于 Mistral-Large-3 **91.21** / Kimi-K2 **91.05**（文内表）。完整列见 PDF Table 2。

---

## 四、后训练（§3）：SFT → RLVR → MOPD

### 4.1 管线骨架（Fig.9）

`
Base (1M 扩展)
 → SFT（两阶段；共享权重 MTP 辅助损失 0.1）
 → RLVR（多环境可验证奖励：推理 / agent / 代码 / 安全 / 可用性 / chat）
 → MOPD Warmup（轻量 SFT，对齐教师支持分布）
 → MOPD ×2 轮（异步 on-policy；多领域教师稠密 token 指导）
 → MTP Boosting（head-only KL，对齐投机草稿）
 → Nemotron 3 Ultra（+ reasoning effort / budget 控制）
`

相对 Super：**大幅重设计**，核心增量是 **Multi-teacher On-Policy Distillation（MOPD）**，而非「只叠更多 RL 阶段」。

### 4.2 SFT / RLVR（接口级）

- SFT Stage1：pack **294,912**；GBS **64**；**204,800** samples；peak LR **1.5×10⁻⁵**。
- Stage2：pack **515,000**（含至 **512K** 长上下文）；**19,200** samples；peak **1×10⁻⁵**。
- 数据槽（只列类，不展开合成流水线全文）：长上下文、reasoning efficiency/control（含 GPT-OSS-120B medium-effort 轨迹；截断预算样本对 `</think>` **mask 损失**）、安全（英 **~45K** + 六语翻译后合计 **~135K**）、搜索 / 终端 / 对话工具 / GitHub issue 轨迹等。
- RLVR：统一可验证奖励，覆盖 agentic 与推理等多环境；生产集群在 **GB200** + Slurm（§3.6）。

### 4.3 MOPD（§3.3）

- **>10** 个领域专家教师并行特化；agentic 教师走独立 agentic SFT 路径。
- 学生在教师支持的状态上做 **稠密 token 级** on-policy 蒸馏；异步流水线；**两轮**共演化（Fig.10）。
- **Warmup 关键**：教师配方差异大时直接 merge 差 → 先轻量 SFT warmup（Table 4：GDPVal 学生 **28.9** → warmup 后 MOPD **46.7** vs 无 warmup **35.3**）。
- Table 5（摘）：相对 RLVR，MOPD2 在 Terminal Bench 2.0 **44.5→54.0**（Recovery **172.7%**，可超教师）、SWE-Bench Verified **65.8→71.7**、TauBench Telecom **82.7→92.9**；HLE（no tools）增益较小（**25.6→26.7**）——文解释为 on-policy 蒸馏在「学生难以采样到教师优势轨迹」时受限。

### 4.4 Reasoning 效率控制（§3.5）

三模式：**reasoning-off / regular / medium-effort**；后两者可叠加 **推理时 budget control**。
文称 medium-effort 相对 regular 平均约 **2.5× 更少 token**，AA Index V4 精度约降 **7%**（Fig.11，**精确点待核实读图**）。

### 4.5 后训练主表（Table 10，抽 agent / 推理 / 长上下文）

对照开源：MiniMax-2.7、GLM-5.1、Kimi-K2.6、Qwen-3.5、DS-v4-Pro、DS-v4-Flash。口径与 harness 见文 §3.7 / Appendix；**禁止**跨表不同设置硬比绝对胜负。

| Benchmark | N-3-Ultra 550B-A55B |
|---|---|
| Terminal Bench 2.1 | 56.4 |
| GDPVal | 46.7 |
| SWE-Bench Verified | 70.7 |
| SWE-Bench Multilingual | 67.7 |
| ProfBench (Search) | 56.0 |
| PinchBench | 90.0 |
| TauBench V3 Average | 70.9 |
| BrowseComp | 44.4 |
| LiveCodeBench v6 | 89.0 |
| IOI 2025（/600） | 570.0 |
| GPQA (no tools) | 87.0 |
| MMLU-Pro | 86.8 |
| RULER (1M) | 94.7 |
| AA-LCR | 65.4 |

文强调 **PinchBench / ProfBench** 为 **held-out**（开发期不用于监控与选点，终模型后只评一次）。吞吐：Fig.1 称相对 GLM-5.1 / Kimi-K2.6 / Qwen-3.5 在 **8K in / 64K out**、GB200、NVFP4 max-throughput 下约 **5.9× / 4.8× / 1.6×**（Ultra 用 TRT-LLM，对照用 vLLM；有无投机解码取各模型最佳）。结论段另写「**5×** 更高吞吐」——与摘要「**∼6×**」同族口径，**引用时标明出处句**。

---

## 五、量化与推理（§4–§5，极短）

- §4：给出面向部署的 **NVFP4** 等量化配方与 Mamba cache / checkpointing 处理（Table 12 等）；细节以 PDF 为准，本卡不抄算子表。
- §5：Hybrid 在 **decode-heavy**（例 8K/64K）上相对纯 Attention MoE 更吃香；**prefill-heavy**（例 50K/2K）时 active FLOPs 劣势更明显（文内相对 Qwen-3.5-397B-17B 约 **3.2×** FLOPs 惩罚的叙述）。MTP 投机：小 batch 偏延迟、大 batch 可能关掉 MTP 更赚吞吐；Mamba SSM 拒绝草稿时需 **snapshot state**（并可用于粗粒度 prefix cache）。

---

## 六、开放清单与本卡未覆盖

**文内声称开源：** Base BF16、Post-Trained BF16、Post-Trained NVFP4、GenRM；若干预训练 / 后训练数据集；训练 recipe；RL environments（NeMo Gym 等链接见文）。
**本卡未写：** 完整教师列表与 RL 环境失败归因表（Table 7–9）、量化逐层 bit 表、全部附录评测协议。需要时回 PDF / 。

---

| 资产 | 路径 | 体积 | 建议 |
|---|---|---|---|
| 主 PDF | `https://arxiv.org/abs/2606.15007` | **3.79MiB / 65p** | **入库二进制**（≪10MB） |
| 辅 PDF | [`NVIDIA Labs TR`](https://research.nvidia.com/labs/nemotron/files/NVIDIA-Nemotron-3-Ultra-Technical-Report.pdf) | **3.70MiB / 65p** | ****（近同文辅；仅 URL + ；主张以 arXiv 为准） |
| 抽取 | （+ `nvidia-labs.txt`） | ~281KB / ~279KB 文本 | **优先保留**（页数长，抽取优先） |
| 笔记 | [[Nemotron3Ultra]] | 本文件 | status:**archived** |

**禁止入库：** 模型权重、量化包、原始数据集 shard。
