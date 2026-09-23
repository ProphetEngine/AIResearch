---
title: "端侧 LLM 增量：MobileLLM-Pro + MobileLLM-Flash（≠ 11 / ≠ 7 / ≠ 9）"
topic: MobileLLM端侧增量
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
sources:
 - https://arxiv.org/abs/2511.06719 # 1.35M / 22p
 - https://arxiv.org/abs/2603.15954 # 1.34M / 16p
arxiv: ["2511.06719", "2603.15954"]
related: ["端侧小模型", "ZeroQAT量化感知训练", "硬件软件协同部署", "Gemma4技术报告深读", "B7"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 端侧 LLM 增量：MobileLLM-Pro + MobileLLM-Flash（≠ 11）

> **定位**：**P1**——Meta Reality Labs / Meta AI 在 **2024 MobileLLM（ICML）之后**的两条**增量产品/方法轴**，禁止写成「MobileLLM 原文复述」：
> - **MobileLLM-Pro**（*Technical Report*，arXiv **2511.06719**）：**1.08B** 端侧基础模型；四阶段预训练（SDM 数据混合 → **隐式位置蒸馏**扩到 **128k** → **专家合并** → **4-bit QAT**）+ 三阶段指令微调；对标 Gemma 3-1B / Llama 3.2-1B。
> - **MobileLLM-Flash**（*Latency-Guided On-Device LLM Design*，arXiv **2603.15954**）：在 Pro/浅宽骨干上做 **硬件在环 NAS**（剪枝继承权重 + Ax 两阶段 BO）；产出 **350M / 650M / 1.4B** 族；主张 **skip-attention 交错**优于 SWA；Executorch 原生算子、无定制内核。
> **攻坚线**：**架构思想（主）**——隐式位置蒸馏 / 专家合并 / 延迟—质量 Pareto；**AI Infra（辅）**——端侧 TTFT、INT4 分发、Executorch 可移植。
> **硬划界（开篇钉死）**：
> - **≠ [[端侧小模型]]**：不重写 **MobileLLM 2024**（arXiv **2402.14905**）的深薄四件套、immediate block-wise 权重共享、DRAM/SRAM 层级通史，也不重写 Phi-4 / Gemma 4 E2B 对照全文。本卡只在「家族命名与浅宽反转」处交叉引用。
> - **≠ [[ZeroQAT量化感知训练]]**：不写 ZeroQAT 的 **零阶（ZO）前向估计梯度**、可学习平滑、Q/V 轻量变体算法课；Pro 的 QAT 是 **标准 STE + 可学习量化范围 + FP 自蒸馏**，接口不同。
> - **≠ [[硬件软件协同部署]]**：不写 NVIDIA Blackwell / TPU 机架白皮书、FP4/NVLink 代际表；本卡延迟数字来自 **手机 CPU/HTP + Executorch**，不是数据中心 codesign。
> - **≠ B7**：不写 vLLM/SGLang 选型通史；Executorch / xnnpack 仅作部署字段。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。文内叙述与表冲突时 **以表为准** 并标注。
> **二进制**：两篇均 **≪10MB**（见 §一）→ **官方 HTTPS 外链**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A** | Huber, Chang, Wen, Fedorov et al. (Meta Reality Labs), *MobileLLM-Pro Technical Report* | arXiv:**2511.06719**v1 \[cs.LG\] **10 Nov 2025**；文首 Date **November 11, 2025**；`https://arxiv.org/abs/2511.06719`（**1.35M**，1,419,954 B；**22** 页 letter） | **1B Pro**：四阶段预训练 + IFT + INT4 CPU/加速器分发 |
| **主文 B** | Huang, Fedorov et al. (Meta AI), *MobileLLM-Flash: Latency-Guided On-Device LLM Design for Industry Scale Deployment* | arXiv:**2603.15954**v2 \[cs.LG\] **27 Apr 2026**；文首 Date **April 29, 2026**；`https://arxiv.org/abs/2603.15954`（**1.34M**，1,402,638 B；**16** 页 letter） | **Flash 族**：延迟在环 NAS + skip-attn；350M/650M/1.4B |

**权重 / 代码（文内明示）：**
- Pro 集合：`https://huggingface.co/collections/facebook/mobilellm-pro`
- 具体卡：`facebook/MobileLLM-Pro-base`、`MobileLLM-Pro-base-int4-cpu`、`MobileLLM-Pro-base-int4-accelerator`、`facebook/MobileLLM-Pro`（instruct）
- Flash：**文内未声明独立 HF 集合 URL**（以 PDF 为准；标「待核实」）。

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2511.06719-mobilellm-pro.pdf` | **1.35M**（1,419,954 B） | 22 | **官方 HTTPS 外链**（≪10MB；全文抽取可并存） |
| `2603.15954-mobilellm-flash.pdf` | **1.34M**（1,402,638 B） | 16 | **官方 HTTPS 外链**（≪10MB；全文抽取可并存） |

**一句话抓手：**
- **Pro**：在 ~1B 档用 **教师 logits（Llama 4-Scout）** 串起「数据混合 → 不喂长文却扩 128k → 专家合并 → INT4 QAT」，把 **Gemma 3-1B / Llama 3.2-1B** 在 11 项预训练榜上整体压过，量化平均分仅掉 **0.73 / 1.39** 个点（CPU / Accelerator）。
- **Flash**：承认 **参数量/FLOPs ≠ 手机延迟**（Kendall τ 仅 ~0.4–0.55），用剪枝继承权重 + Ax 两阶段 BO 直接优化 **TTFT**；Pareto 原则钉死 **浅宽优先**、**skip-attn 优于 SWA**；相对 LFM2 声称最高 **1.8× prefill / 1.6× decode**。

---

## 二、议题边界：增量产品轴 ≠ 2024 原文 / ≠ ZO-QAT / ≠ 机架白皮书

### 2.1 四向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **2024 MobileLLM 深薄配方** | 层深、embedding 共享、GQA、immediate share | **[[端侧小模型]]** | **否**（禁原文复述） |
| **训练期 ZO-QAT** | 零阶梯度、端侧可训 QAT 显存 | **[[ZeroQAT量化感知训练]]** | **否**（禁算法课） |
| **数据中心 HW–SW codesign** | Blackwell / TPU / FP4 / NVLink | **[[硬件软件协同部署]]** | **否** |
| **1B 四阶段预训练 + 128k 位置蒸馏** | SDM / IPD / specialist merge / 双路径 INT4 | **本篇主文 A** | **是** |
| **手机 TTFT 在环 NAS + skip-attn 族** | 剪枝搜索、Pareto 原则、Executorch 可移植 | **本篇主文 B** | **是** |

跟读直觉：[[端侧小模型]] 问「**sub-billion 端侧该不该深薄**」；Pro 问「**已有 1B 配方后，数据/长上下文/合并/量化四阶段怎么叠**」；Flash 问「**深薄在手机上是否反而更慢——如何用真实 TTFT 搜出浅宽 + skip**」。三者串成「2024 架构立轴 → 2025 Pro 训练栈 → 2026 Flash 延迟栈」，禁止把后两篇写成 MobileLLM 原文附录。

### 2.2 与 [[端侧小模型]] 的唯一允许接口

| 字段 | [[端侧小模型]]（MobileLLM 2024） | 本篇 Pro | 本篇 Flash |
|---|---|---|---|
| 参量 | 125M–1.5B 深薄族 | **1.084B**（30L / d=1280 / FFN 6144） | **350M / 650M / 1.4B**（更浅：12–16L） |
| 主杠杆 | 深度 + immediate share | **IPD + 专家合并 + SDM + QAT** | **延迟在环 NAS + skip-attn** |
| 上下文 | 短窗叙事为主 | **128k** local-global（local 512，每 4 层一 global） | 预训练 CPT **2k**；IFT **8k**；评测到 **4k** |
| 部署 | 内存层级通史 | INT4 CPU **590 MB** / 加速器 **720 MB**；S25 CPU + S24 HTP | Executorch + XNNPACK；S25 / iPhone 17 对照 |

Flash Related Work 明确点名：先验 **深薄**（含 Liu et al. 2024 = MobileLLM、Huber et al. 2025 = Pro）**常未能改善端侧延迟**——这是本卡相对 [[端侧小模型]] 的**反转句**，不是重写深薄课。

`
 端侧 SLM / OD-LLM 问题链
 │
 ┌──────────┼──────────┐
 ▼ ▼ ▼
 深薄立轴 训练栈增量 延迟在环增量
 [[端侧小模型]] 本篇 A Pro 本篇 B Flash
 (禁复述) 128k+QAT skip-attn NAS
`

---

## 三、MobileLLM-Pro：1B 四阶段预训练 + 助手 IFT（主文 A）

### 3.1 架构规格（Table 1，照录）

| 字段 | 值 |
|---|---|
| Layers / Heads / KV | **30** / **20** / **4**（GQA） |
| Dimension / Hidden（FFN） | **1280** / **6144**（文称 4.8× up-scaling） |
| Vocab | **202,048**（与 Llama 4 同级；embedding **共享**，文称省约 **260M ≈ 25%** 参数） |
| Total params | **1,084M（1.08B）** |
| Context | **128k**；Local-Global：**512** local window，**每 4 层 1 个 global**（首尾层为 global） |
| 模态 / 语言 | Text in/out；**English** |

教师信号：全阶段预训练用 **Llama 4-Scout** 的完整 **202,048** logit 做 **forward KL** 蒸馏（相对 one-hot CE）。

### 3.2 四阶段预训练（Fig.1 + §3–7）

| Phase | 名字 | 核心动作 | 文内预算/要点 |
|---|---|---|---|
| **1** | Language-Acquisition | **Scalable Data Mixer (SDM)** 离线效用估计 → 静态采样权重 | **1.4T** tokens；batch **2M** tok；**640k** steps；LR max **4e-4** → 0 cosine；warmup **10k** |
| **2** | Context-Expansion | **Implicit Positional Distillation（IPD）**：仍用短文数据，靠教师 logits 传长程位置 | 再 **100k** steps / **20B** tokens；LR max **4e-5**；避免 Phase1→2 数据分布漂移 |
| **3** | Specialist Model Merging | 并行域专家小步退火 + **非均匀**参数平均 | 每专家约 **60M** tokens / **500** steps；LR **1e-5→0**；产出 **MobileLLM-Pro-base** |
| **4** | Efficiency / QAT | CPU **group-wise INT4**；加速器 **channel-wise INT4 + 可学习范围**；**FP 自蒸馏** | 约全精度预算的 **5%** ≈ **80B** tokens；CPU **590 MB** / 加速器 **720 MB**（后者因不共享 emb） |

**Phase 1 数据混合（Table 2，权重 %）：** Fineweb-EDU **89.75**、Starcoder **4.66**、Open Web Math **1.92**、Arxiv **1.35**、Wiki **1.02**、Stack Exchange **1.02**、Algebraic Stack **0.24**（合计 tokens 表列 **1640.3B** 行级统计；训练用 **1.4T**）。

**IPD 机制（§5，跟读要点）：**
RoPE 短窗训练只覆盖角度子空间；拼接短文档填满长窗**仍无真实长程语义**。Block causal packing **不阻断** logit 蒸馏中的位置信息迁移 → 学生模仿教师分布即可继承长程位置关系，**无需直接喂长上下文数据**，从而消除 Phase1/2 分布漂移。消融（Table 13）：Phase-1 NIH **6.7**；专用长文 Phase-2 NIH **80.22** 但平均榜 **-5.9**（53.74→47.86）；IPD NIH **99.78**、平均 **53.57**（几乎不掉）。

**专家合并条件（§6）：** (1) 权重空间已稳定（仅晚期有效）；(2) 并行更新足够小。Table 14：Pre-Anneal 平均 **53.57** → Weight Avg **56.73**（不含 NIH），常优于单专家最优。

**双路径量化（Table 3）：**

| | CPU | Accelerator（ANE / HTP） |
|---|---|---|
| Weights & Emb | INT4 sym, **group-size 32** | INT4 sym, **channel-wise** |
| Activations / KV | INT8 dyn asym per-token | **BF16** |
| QAT | Vanilla range | **Learnable quant ranges** |

文称 PTQ 直接砸 Phase-3 会严重回退（Table 17）；channel-wise 需可学习范围（Table 15：**55.67→60.46**，+4.79）；QAT 自蒸馏（Table 16：**58.61→61.04**，+2.43）。

### 3.3 预训练主结果（Table 4 / 5）

相对 Gemma 3-1B / Llama 3.2-1B（照录节选）：

| Benchmark | Pro | Gemma 3-1B | Llama 3.2-1B |
|---|---|---|---|
| HellaSwag | **67.11** | 62.30 | 65.69 |
| BoolQ | **76.24** | 63.20 | 62.51 |
| ARC-Challenge | **52.62** | 38.40 | 38.28 |
| Natural Questions | **15.76** | 9.48 | 5.48 |
| NIH | **100.00** | – | 96.80 |

量化平均（Table 5，含 NIH）：Full **61.81** → Quant-CPU **61.08**（−0.73）→ Quant-Accelerator **60.42**（−1.39）。

### 3.4 指令微调三阶段 + 结果（§9–10）

1. **Diversity-first**：贴近开源 IFT 样本自然分布（Table 6 合计 **7.64M** samples；Nemotron Math + Flan 约占 **70%**）。
2. **Leave-One-Out**：按 LOO 雷达图调高 Tulu 3 / Nemotron Science 等影响大的域。
3. **Safety + Self-ID**：SFT + DPO 合成数据退火；文称与榜分有折中。

Instruct 榜（Table 7 节选）：HumanEval **59.8**（Gemma 41.5 / Llama 37.8）；MBPP **46.8**；BFCL v2 **29.4**；MMLU **44.8**（低于 Llama 49.3，高于 Gemma 29.9）；IFEval **62.0**（低于 Gemma 80.2）。人评（Table 8/9，每维 100 题）：对 Llama 四维皆胜；对 Gemma 在 Recall / Tool Calling 胜，Summarization / Rewrite 略负。Tool Calling 用 **Llama 3-70B** 作裁判（脚注）。

### 3.5 端侧延迟字段（Table 10，S25 CPU / S24 HTP）

| Metric | 2k | 4k | 8k |
|---|---|---|---|
| CPU Prefill (s) | 8.9 | 24.8 | 63.5 |
| HTP Prefill (s) | 2.0 | 3.4 | 9.8 |
| CPU Decode (tok/s) | 33.6 | 24.8 | 19.7 |
| HTP Decode (tok/s) | 31.6 | 29.0 | 22.8 |
| KV Cache (MB) | 14.0 | 23.0 | 40.0 |

导出：**ExecuTorch**；CPU=xnnpack，加速器=HTP。

### 3.6 关键消融速记（§12）

| 消融 | 数字（文内） |
|---|---|
| SDM vs uniform（Table 11，CE 训练） | PT **38.70→49.31**；IFT 表列 **17.94→45.23**（正文另写「17.9→32.7」，**与表冲突，以表为准**） |
| CE vs KD Phase-1（Table 12，FLOP 对齐） | **49.31→53.74**（+4.4，不含 NIH） |
| IPD vs 长文数据（Table 13） | 见 §3.2 |
| Specialist merge（Table 14） | 平均 **53.57→56.73** |

---

## 四、MobileLLM-Flash：延迟在环 NAS + skip-attention 族（主文 B）

### 4.1 问题立轴：TTFT 与可移植，而非代理指标

产业约束（§1）：近实时 **TTFT**（例：4s 可用、10s 不可用）；~**2k** tokens 为实用甜点；必须 **通用运行时**（Executorch），避免专用注意力内核。Key Insight-1：100 个架构在 S25 / 2k 上，参数量 vs 延迟 Kendall τ≈**0.40**，FLOPs vs 延迟 ≈**0.46 / 0.55**（prefill/decode）→ **必须硬件在环**。

### 4.2 方法：剪枝搜索空间 + 两阶段 Ax BO（Fig.2）

**搜索空间 S（Table 3）：**
`dL ∈ {10…16}`；`dffn ∈ {2048…8192}`；`dmodel ∈ {1024…2048}`；每层 `pi ∈ {full_attn, SWA, skip_attn}`（~**70B** 组合量级）。剪枝用激活能量：FFNMetric / ModelDimMetric / LayerMetric（§3.3）。

**两阶段：**
1. 廉价采延迟（~**800** 次手机测量）训 GP，CV **R²=0.97**；
2. 预测延迟 + 真训练质量，NEHVI；参考点 loss **0.6**、TTFT **4s**。每候选 CPT 仅 **2.6B** tokens 得稳定排序（相对全量 **500B**）；相对从头训，剪枝路径约 **35%** token。Kendall τ（剪枝 CPT vs from-scratch）**0.74**（20 候选）。

**Pareto 原则（§3.5）：**
1. **浅宽**在端侧更好平衡准确率—延迟（深模型质量高但更慢；极低延迟区切浅）。
2. **Skip-attn 优于 SWA**；最优为 **skip 与 global 交错**；禁止 ≥3 层连续高效注意力（Table 4：连续 skip 过多时 TQA **8.8%→33.2%** 等崩坏）。

### 4.3 实现与架构表（§4.1 / Table 5）

起点：**MobileLLM-Pro-Shallow-1.8B**（16L / d=2048 / FFN 8192）——同配方浅宽变体。校准 **600M** tokens（~预训练 **0.1%**）。Ax 每轮 8 候选；共 **200** trials；搜索总成本 **200×2.6B=520B**；最终 3 个 Pareto 点各 CPT **500B** + IFT **800B**。对比：Pro 约 **1.6T**、LFM2 **10–12T**（文内陈述）。

| Model | Layers | dmodel | dFFN | H/KV/Hsize | #Attn blocks |
|---|---|---|---|---|---|
| Pro-1B* | 30 | 1280 | 6144 | 20/4/64 | 16 |
| Pro-Shallow-1.8B | 16 | 2048 | 8192 | 32/8/64 | 16 |
| **Flash-350M*** | **12** | **1024** | **4096** | 32/8/64 | **7**（其余 skip；full idx `[0,1,3,6,7,9,11]`） |
| **Flash-650M*** | **13** | **1280** | **6144** | 32/8/64 | **8**（full idx `[0,2,3,5,7,8,9,10]`） |
| **Flash-1.4B*** | **16** | **2048** | **8192** | 32/8/64 | 16 |

\* embedding–unembedding 共享。CPT seq=**2048**，SWA window=**256**；IFT seq=**8192**。

### 4.4 质量与效率（Table 6–8）

**Avg↑ / Prefill TTFT@2k / Decode@2k（S25，节选）：**

| Model | Avg | TTFT 2k (s) | Decode 2k (tok/s) |
|---|---|---|---|
| LFM2 350M | 44.92 | 2.18 | 96.90 |
| **Flash 350M** | **45.46** | 2.78 | **112.58** |
| LFM2 700M | 48.52 | 6.01 | 53.57 |
| **Flash 650M** | **48.57** | **3.34** | **85.35** |
| LFM2 1.2B | 50.48 | 8.41 | 42.15 |
| **Flash 1.4B** | **55.06** | 9.08 | 42.65 |
| Pro-Shallow-1.8B（未剪） | 56.20 | 9.20 | 35.88 |

文称 Flash-1.4B 相对浅宽母体平均准确率只让 **1.1%**，换最高约 **1.2× / 1.3×** prefill/decode；相对 LFM2 族最高 **1.8× / 1.6×**。量化部署字段：W4 group32 + A8 dyn + 量化 KV；Nemotron-Flash-1B 因 JetBlock **不支持 Executorch** 未测延迟。iPhone 17 上相对优势大体保持（Table 8）。

IFT（Table 7）：Flash-1.4B MMLU **47.89**、HumanEval **46.34**；Flash-650M Open Rewrite **46.84** 等——文称助手场景可比或更优；**禁止**与 Pro Table 7 无脚注硬并（评测设定/模型不同）。

### 4.5 局限（文内 Limitations）

- 未与架构联合搜训练超参（LR / optimizer）。
- 为保 Executorch 可部署，**未**纳入 SSM / 线性注意力等缺成熟运行时支持的子二次模块。
- CPU Pareto 未必迁移到 ANE 等异类加速器（延迟排序在手机 CPU 间较稳）。

---

## 五、Pro × Flash 对照

| 维 | MobileLLM-Pro | MobileLLM-Flash |
|---|---|---|
| 发布时间（文内 Date） | 2025-11-11 | 2026-04-29 |
| 目标 | 1B 质量 + 128k + INT4 双路径 | 手机 **TTFT** Pareto 族 |
| 架构哲学 | 30L 深一点 + local-global | **浅宽** + **skip/global 交错** |
| 训练主创新 | IPD / specialist merge / SDM / QAT | 剪枝 NAS + 两阶段 BO |
| 上下文产品叙事 | **128k** | 实用 **~2–8k** |
| 相对 [[端侧小模型]] | 继承「端侧 1B」产品线，**不**复述深薄课 | **显式批评**深薄延迟失效 |

**跟读口诀：**

`
[[端侧小模型]] MobileLLM'24：深薄 × 共享 × DRAM 故事
 ↓（禁复述）
Pro：Scout-KD × SDM × IPD(128k) × Merge × INT4-QAT
 ↓ 浅宽母体
Flash：真机 TTFT × 剪枝 BO × Skip>SWA × Executorch 可移植
`

1. **二进制**：两 PDF 均约 **1.35M / 1.34M ≪ 10MB** → **官方 HTTPS 外链**；全文 已落 。
2. **笔记路径**：推理与基础设施/MobileLLM端侧增量.md（本文件）。
3. **交叉链**：`related` 指向 [[端侧小模型]] / [[ZeroQAT量化感知训练]] / [[硬件软件协同部署]] / [[Gemma4技术报告深读]] / B7；正文禁止展开其主课。
4. **待核实**：Flash 权重/代码公开入口（PDF 未给 HF URL）；Pro IFT Table 11 正文「32.7%」与表「45.23」不一致——引用时锁表。
5. **勿混并**：Pro 128k NIH 与 Flash 4k TTFT、Pro/Flash 的 MMLU/HumanEval **分表引用**，禁止合成「统一端侧榜」。

---

## 六、开放问题（草稿）

1. IPD 对非 RoPE / 非 Scout 教师是否可迁移？文内机制论证偏 RoPE+logit KD。
2. Flash 的 skip-attn Pareto 在 ANE/HTP 上是否翻转？文内已提示跨加速器类可能失效。
3. Pro 专家合并的域划分与权重 `w_b` 选择流程：正文给公式，**未**给完整域列表与权重搜索细节。
4. 与 ZeroQAT（[[ZeroQAT量化感知训练]]）联用：Pro 已是 STE-QAT；端侧「训练期再量化」是否还有增益——超出两文范围。

