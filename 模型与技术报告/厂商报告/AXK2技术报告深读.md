---
title: "A.X K2 Technical Report 深读"
topic: AXK2技术报告深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
source_url: https://arxiv.org/abs/2608.30181
arxiv: "2608.30181"
archived: 2026-09-22
---

# A.X K2 Technical Report 深读卡

> **定位**：A.X K2 增量技术报告主题轴（相对已入库 DeepSeek-V3 / Kimi-K2 / GLM-4.5 / Qwen3）。数字一律取自官方 PDF `https://arxiv.org/abs/2608.30181`（2026-09-22 CST）。
> **攻坚线**：**架构思想（主）** + **评测字段 / agentic bench（辅）**。
> **刻意不写**：DeepSeek-V3 MoE+MLA+DualPipe/FP8 分块配方全文（见 [[DeepSeekV3训练与MoE基建]]）；Kimi-K2 MuonClip / 15.5T / agentic 数据合成通史（见 [[KimiK2技术报告深读]]）；GLM-4.5 / Qwen3 训练 Infra 与 scaling 配方全文；DSA 两阶段续训（见 [[DeepSeekV32技术报告深读]]）；EAGLE 投机解码通史（B7 / 留给 [[EAGLE3投机解码]]）。本卡只补「SKT **A.X K2** 相对 **A.X K1** 与开源 MoE 对照表里的本 PDF 新公开点」。
> **禁止编造**：A.X K1 独立 TR、Nemotron/GLM-5.1/Kimi-K2.6 等对照模型数字 **仅录本 PDF Table 6 转述**；图内未抽出可读点标「待核实读图」。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | A.X K2 Technical Report | 封面 |
| 机构 | **SK Telecom** | 封面 |
| 作者 | 长名单（Model / Data / HPC / Business）；附录 A 按组字母序 | 封面；Appendix A；XMP |
| arXiv 页眉 | **arXiv:2608.30181v1** \[cs.AI\] **31 Aug 2026** | PDF 第 1 页页眉 |
| 封面日期戳 | **2026-09-01**（页眉右上） | PDF 第 1 页 |
| XMP identifier | `https://arxiv.org/abs/2608.30181v1` | ` -meta` |
| XMP MetadataDate | 2026-09-01T01:54:40+00:00（→ **2026-09-01 09:54 CST**） | XMP |
| PDF 页数 | **35**（A4） | |
| 权利声明（XMP） | `http://creativecommons.org/licenses/by/4.0/` | XMP |
| 本地路径 | `https://arxiv.org/abs/2608.30181`（2,203,433 bytes） | 仓库 |
| 权重入口 | https://huggingface.co/skt/A.X-K2 | Abstract 脚注；封面 |
| 摘要四关键词 | (1) **688B MoE** agentic 基座；(2) **~8.5T** tokens（少于 K1）token 效率；(3) **SGA** + **GN**；(4) **Think-Fusion** 可切换 thinking | Abstract |

**摘要级一句话（不外推）：**
A.X K2 = SKT 在韩国 Sovereign AI 叙事下从零训的 **688B / 33B-active MoE**；用更少、更高质、偏 agentic/软工的 **~8.5T** 数据相对前代 K1 全面抬分；架构增量主轴是 **Sparse Gated Attention（SGA）** + **Gated Norm（GN）**，后训练增量主轴是 **Think-Fusion SFT** + 多阶段 RL。

**命名边界（正文用法）：**

| 名称 | 本 PDF 中的关系 |
|---|---|
| **A.X K1**（SKT, 2026） | 前代：约 **519B**、**~10T** tokens、192 routed experts、dual-normalization、dense long-context 对照 |
| **A.X K2** | 本报告主体：688B / 33B、256 experts、SGA+GN、Think-Fusion、原生 128K + YaRN 256K |
| 对照开源基线（Table 6） | Qwen3.5-397B-A17B、Nemotron 3 Ultra、DeepSeek-V4 Flash、GLM-5.1、Kimi-K2.6、MiniMax-M2.7（**均为本表转述**） |

---

## 二、相对已入库超大开源 MoE / 前代 K1 的增量对照

> 左列以本 PDF 明文为准。V3 / Kimi-K2 / GLM-4.5 / Qwen3 列仅作「已入库笔记锚点」，**禁止把本卡写成其 Infra 重写**。

| 维度 | DeepSeek-V3 / Kimi-K2 等（已入库） | **A.X K1（本 PDF 转述）** | **A.X K2（本 PDF）** |
|---|---|---|---|
| 报告入口 | V3 2412.19437；K2 2507.20534 等 | 引 SKT 2026，仓库无独立 PDF | arXiv:**2608.30181v1** · **35** 页 · 2026-08-31 |
| 问题设定 | 造超大 MoE 基座 / agentic 开源旗舰 | 前代 Sovereign 基座 | **固定算力+70 天**下抬 token 效率 + **长文可服务** + **可切换 thinking** |
| 总参 / 激活 | V3 671B/37B；K2 1.04T/32.6B（各自 TR） | **519B** / **33B** | **688B** / **33B** |
| Routed experts | V3 256；K2 384（各自 TR） | **192** | **256**（保持 33B 激活） |
| 注意力 | MLA / MLA+DSA 等（已入库） | （未在本 PDF 重开完整表） | **MLA** + 全程 **gated attention** + 长文阶段加 **sparse indexer（SGA）** |
| 归一化稳定 | — | **dual-normalization** | **GN** 替代 dual-norm（吞吐约 −5%，换稳定与低精度） |
| 预训练 token | V3 14.8T；K2 15.5T | **~10T** | 总计 **~8.5T**（预训练 **~8.2T**） |
| 长上下文 | 各系 YaRN / 继续训配方不同 | dense 长文对照 | 原生 **128K（ABF）**；推理 **YaRN→256K**；SGA **k=2048** |
| Indexer warmup | V3.2 / GLM-5：**先 dense 再 sparse**（本 PDF 对比） | — | **sparse warmup**：一开始就对 **自身 top-k** 对齐（相对 dense warmup **更便宜**） |
| 后训练 | 各系 SFT+RL 配方 | 双轨 thinking（本 PDF 称 prior） | **Think-Fusion 单轨配对 SFT** + 多阶段 **CISPO+GDPO** RL |
| 叙事身份 | 开源旗舰 / 推理 | 韩国前代 | **韩国 Sovereign AI**；韩语/文化 + 可控部署 |

**增量一句话：**
相对已入库「V3/Kimi 怎么把 MoE/MLA/优化器训稳」的通史，本卡公开增量几乎全部落在 **相对 K1 的专家扩容（192→256）+ SGA sparse warmup + GN 换 dual-norm + Think-Fusion + 固定 B200×70 天工程包**——**禁止当新 MoE 拓扑史或对照模型 Infra 重写**。

---

## 三、架构主轴（本卡核心）

### 3.1 规模表（Table 1）

| 项 | A.X K2 |
|---|---|
| Total / Activated | **688B** / **33B** |
| Layers | **61**（第 1 层 dense FFN，余 **60** MoE） |
| Heads (Q/KV 列) | **64** |
| Hidden | **7168** |
| Intermediate (Dense / Expert) | **18432 / 2048** |
| Routed / Activated experts | **256 / 8** |
| Shared experts | **1** |
| Vocab | **163,840**（byte-level BPE；英/韩/中/日/西；**继承 K1 未改**） |
| Context (Native / YaRN) | **128K / 256K** |

**设计取舍（§2.1，不外推）：**

- 算力锚：约 **70 天 × 512 NVIDIA B200** → 固定 FLOPs 预算；MoE scaling laws（Tian et al., 2025）指导下 **偏知识容量 + 推理吞吐**，而非严格 compute-optimal token。
- 相对 K1：专家 **192→256**（2 的幂、128 的倍数，对齐 EP sharding / kernel tiling），**激活参保持 33B**。
- 头数 64 + shared dense experts：文称受 Kimi 经验启发，优先 **降注意力推理开销**。
- QK-normalization；路由细节见 §3.6（本卡只录超参，不写 MoE 通史）。

### 3.2 Sparse Gated Attention（SGA，§2.2 + Fig 2）

**两件套：**

1. **Gated attention（全程预训练）**：头特异输出门 $G=\sigma(W_g q_{\mathrm{latent}})$，抑制 attention sink、加非线性、改善收敛。
2. **Sparse attention（长文适配 Stage 3C）**：轻量 **indexer** 选 **top-k=2048**，再对 `KV[I_topk]` 做 **MLA**——128K 时每 query 只读约 **1.6%** 位置，256K 约 **0.8%**（固定预算 → 注意力项近似线性扩）。

**与 indexer 的互增强（明文）：** indexer 要拟合注意力分布；gated 输出把 sink 质量压下去 → top-k 预算更花在相关位置。

**质量中性（Table 9）：** LongBench v1：**62.80（dense, Stage 3B）→ 62.99（sparse, Stage 3C）**，∆ **+0.19**。

> 命名注意：文脚注称本设计的 “SGA” **与** Du et al. (2025) 同名方法 **无关**。

### 3.3 Gated Norm（GN，§2.2 + Fig 3）

- 在 **RMSNorm 后**立刻做可学习、输入依赖的 gating。
- 抑制 **massive activations / 隐状态 outlier** → 利于 **FP8 / NVFP4** 块缩放（尤其 MLA latent KV up-projection 会放大 outlier）。
- 相对 K1：**去掉 dual-normalization**；GN 干跑消融（20B-A3B）显示再叠 post-MLP norm **无额外收益**（Fig 3；曲线点待核实读图）。
- 代价：训练吞吐约 **−5%**（作者接受）。

### 3.4 预训练课程（§3；跟读骨架，不展开对照 Infra）

| 阶段 | Tokens（约） | 上下文 | LR 角色（WSD） |
|---|---|---|---|
| Stage 1 通识 | **6.4T** | 4K | warm-up + **stable** 峰值 **2.2e-4** |
| Stage 2 高质量推理 | **1.4T** | 4K | cosine decay → **7e-5** |
| Stage 3A | **~0.22T** | **32K** | 再 warm → 7e-5 → cosine **2.2e-5** |
| Stage 3B+3C | **~0.14T** | **128K** + SGA | warm/hold **2.2e-5**；3C = sparse 适配 |

**数据增量相对 K1（§3.1，定性为主）：** 刷新 Nemotron-CC v2.1 / Code-v2、韩网、FineWeb2；**显著加大 agentic / 软工 / tool trajectory / repo-level code / 长文**；后期掺 SFT 格式数据。候选池约 **16.2T** → 在预算下做难度递增筛选（Table 2–3）。

**长文配方要点（§3.4）：**

- **ABF**：RoPE base Stages 1–2 = **10⁴**；32K 起升到 **10⁶** 并保持到 128K/SGA——**原生学满 128K**，再靠 YaRN 放大到 256K（mscale=1.0）。
- NIAH @256K：文称 **满分 100**（含 NVFP4 experts-only W4A4；Fig 5）。
- **Sparse warmup**：indexer-only 先冻骨干；**KL 直接对 sparse top-k**（≠ V3.2/GLM-5 先 dense 再开 sparse）；再全模续训并降低 indexer loss 权重。
- Stage 3B/3C **共享数据配比**（异于 3A），文称跟 GLM-5 做法。

**Checkpoint merging（§3.5）：** 最后约 **6** 个 ckpt、间隔 ~1.6B tokens，**WSM 风格 SWA**；含 **MoE router**；$1-\sqrt{\cdot}$ 加权偏新。

**路由超参快照（§3.6，仅表）：** sigmoid pre-softmax；256 experts → **8 groups**；group top-k **4**、token 激活 **8**；top-k scale **2.5**；**global aux loss**（Qiu et al. 2025a）+ learnable expert bias（替代 K1 的 sequence-level aux 主用）；系数随阶段退火。

**并行 / 精度（§3.7，点到为止）：** PP=8（interleaved VP=2）、EP=8、无 TP；HybridEP（非 DeepEP）；32K CP=2 / 128K CP=8；**full activation recompute**；训练 **MXFP8（E4M3, block 32）**；发布 ckpt = **blockwise FP8（128×128 权重块）** 可直接 FP8 服务。

---

## 四、后训练：Think-Fusion + 多阶段 RL（agentic 叙事）

### 4.1 Think-Fusion SFT（§4.1）

**模式格式：**

- Thinking：`<think>...</think>{response}`
- Non-thinking：`</think>{response}`

**问题：** 混训时 thinking 样本更长 → 易 **mode confusion**（即使用户要 non-thinking 仍输出思考链）。
**配方：** **配对数据集**——同一 prompt 同时有 thinking / non-thinking 回答；thinking:non-thinking **token 比约 13:1**；靠 **显式控制 token** 学切换，而非类别伪相关。相对 K1「双轨」或他文 1.5:1 token 比，本报告走 **单轨 Think-Fusion**。

**流程：** 短 **indexer SFT**（模型+indexer 同训，学控制 token）→ **冻 indexer** → **main SFT**；打包长度 **128K**；FFD bin-packing。

**样本规模（Table 4 合计）：** Indexer SFT **437,886** + Main SFT **8,611,778** = **9,049,664** samples；Main 中 **Agent** 类别 Reasoning 侧 **1,602,902**（样本比 17.71%）——与 agentic 叙事一致。Safety 扩展 ESSA 规格演化（50 domain–task 组合）。

### 4.2 RL Infra 两点（§4.2；不写引擎通史）

1. **Trainer–rollout 精度一致**：统一 **blockwise FP8**（vLLM 成熟路径）；MXFP8 trainer × blockwise rollout → reward **崩溃**（Fig 6）；对齐后稳定。TIS 挡不住精度失配。
2. **异步 DP rollout**：veRL 原 DP1 不够；rollout 侧 **TP1/DP8 + EP8**，相对 TP8/DP1 输出吞吐 **1.6×**（Table 5，输入 131,072）。

### 4.3 多阶段 RL（§4.3）

- **每阶段联合**优化：instruction following / human preference / agentic tool use；（后期加）safety——避免单能力过优化。
- Thinking / non-thinking **约等比例**采样。
- 奖励：规则可验证 IF；pointwise LLM-as-judge 偏好；tool **单步可验证 + 长程 gated judge**；safety 九维 judge。
- 算法：**CISPO**（裁 importance weight）+ **GDPO**（分奖励归一化）；**无 KL penalty**；16 rollouts/prompt；batch 80 prompts；LR **2e-6**；AdamW ε **1e-15**；总约 **100K prompts**。
- 文自承：agentic RL **有限** → Terminal Bench / BrowseComp 仍有明显缺口（见下表）。

---

## 五、评测字段（辅轴；跟读摘录）

### 5.1 主对照表摘录（Table 6，thinking；* = Artificial Analysis）

| Benchmark | A.X K2 | A.X K1 | 备注（本 PDF） |
|---|---:|---:|---|
| AIME26 | **97.1** | 91.3 | Math 最强档之一 |
| Apex | **45.8** | 1.0 | 相对 K1 **+44.8 pp** |
| KMMLU-Pro | **80.5** | 68.9 | Korean 领先 |
| CLIcK | **91.6** | 85.3 | Korean |
| LiveCodeBench v6 | 84.0 | 74.9 | 低于 DeepSeek-V4 Flash 89.4 等 |
| HLE | 27.8 | 8.3 | 中游 |
| GPQA Diamond | 85.6 | 76.4 | 低于顶尖开源对照 |
| τ²-Bench Telecom* | **98.0** | 86.0 | **Agentic 本表最强** |
| GDPval Elo* | 1031 | 500 | 仍低于 GLM-5.1 1257 等 |
| Terminal Bench v2.1* | 36.0 | – | 明显落后重 agentic 优化模型 |
| BrowseComp (≤10)* | 9.3 | – | 明显缺口 |

**证明向插曲（正文，非 Table 6）：** IMO 2025 **35/42**（前五题各 7/7，达金牌线）；KMO26 二轮 **8/8** 正确证明（DeepSeekMath-V2 迭代证明流程）。

### 5.2 长上下文（§5.3）

| 指标 | 数字 |
|---|---|
| RULER overall（至 256K，Table 7） | **94.6**（4K 97.5 → 128K 92.7 → 256K 86.6） |
| LongBench v2 filtered 416（去 Han 字符项） | **63.9**（Qwen3.5 64.2；GLM-5.1 63.2） |
| LongBench v2 full 503 | 62.2（排第三；过滤使本模型 +1.7、他模略降——**引用须标明集合**） |
| AA-LCR | 66.0（K1 26.0） |
| NIAH 探测 | 128K/256K/512K 文称满分；**512K 仅 retrieval probing，非支持服务配置** |

### 5.3 韩语中心 / 制造 / 红队（§5.4）

- **KS-Eval**（26 tasks / 1800 items）：相对 K1 四类均升（IF **+27.98 pp**，Long Context **+27.11 pp**）；Common Sense / IF 领先 Qwen3.5；STEM 仍落后 Qwen3.5/GLM-5.1。
- **Manufacturing Benchmark**（836 项）：overall F1 **69.0** 最高；优势主要来自 **abstention 61.1**；文档误导条件下 overall **41.4**（仍领先但远低于 user-assertion **67.8**——作者标优先改进）。
- **红队**（224 韩文对抗，78% 多轮）：non-thinking ASR **12.1**（最强）；thinking ASR **33.9**（升 **+21.8**，弱于 Qwen3.5 的 21.0）——**延长推理不一定更安全**。

### 5.4 部署数字快照（§6；辅，不写投机通史）

| 项 | 数字 |
|---|---|
| 最低服务显存（Table 13） | K1 BF16 **1038 GB**；K2 FP8 **646 GB**；K2 NVFP4 **370 GB** |
| NVFP4 vs FP8 基座均分（Table 14） | 78.19 vs 78.95（**−0.76**，保留 **99.0%**）；experts-only W4A4 |
| 相对 K1 吞吐 crossover（Table 15） | FP8：**64K**；+EAGLE3：**32K**；NVFP4：**全长度** |
| EAGLE3 | 平均接受 **2.24** tok/step；drafter **5.6 GiB**（<1% of 688B）；相对非投机 **+23–30%** |

---

## 六、局限（§7）与划界

1. **EP=8 锁在节点内 NVLink** → 未探索多节点细粒度专家并行。
2. **固定时间/GPU 预算** → 相对「更大算力同规模」模型有作者自承的性能短板。
3. **纯文本**；计划原生多模态；结论展望万亿参。

**相对已入库笔记的增量边界：**

| 已有笔记 | 本卡不复述 | **本卡新增** |
|---|---|---|
| [[DeepSeekV3训练与MoE基建]] / [[DeepSeekV32技术报告深读]] | MLA/MoE/DSA/FP8 训练全文 | 仅引用「dense warmup vs **sparse warmup**」对比句 |
| [[KimiK2技术报告深读]] | MuonClip、1T MoE、agentic 合成通史 | 头数 64 的「受 Kimi 启发」一句 + Table 6 对照分 |
| [[GLM45技术报告深读]] / [[Qwen3技术报告深读]] | 各自 Infra / 后训练全文 | Stage 3B/3C 共享配比「跟 GLM-5」；对照表分数 |
| [[混合专家架构]] / [[长上下文位置编码与系统侧]] / [[注意力效率族MQA到MLA]] | MoE/长文/注意力效率通论 | SGA k=2048、ABF+YaRN、RULER 94.6 |
| [[智能体工具与长程任务]] | 工具环/MCP 通论 | Think-Fusion + τ²/τ³/BrowseComp/Terminal 字段 |
| [[EAGLE3投机解码]] EAGLE-3 | — | 本卡只记产品侧 **2.24 accept / 5.6 GiB drafter**；通史留给 [[EAGLE3投机解码]] |

---

## 七、待核实与引用

### 7.1 待核实（禁止当作已确认）

1. **A.X K1 独立完整 TR / 权重卡**：本仓库无 PDF；519B、~10T、192 experts、dual-norm 等 **仅本报告转述**。
2. **Fig 1 / 3 / 4 / 5 / 7–9 曲线逐点**：文本层无完整数值表；吞吐绝对 tok/s 以正文叙述与 Table 15 相对值为准。
3. **Table 6 标 \* 的 Artificial Analysis 分数**：他模分数来源为 AA，**非本团队复现**；跨 scaffold 引用须注明。
4. **LongBench v2 去 Han 过滤**：改变排名；对外引用须标明 **416 vs 503**。
5. **512K NIAH**：作者明确 **非支持服务长度**。
6. **HF 许可 / 商用条款 / 与新闻站日期差**：以 arXiv **v1 2026-08-31** 与官方 PDF 为准。
7. 对照型号（Qwen3.5 / GLM-5.1 / Kimi-K2.6 / DeepSeek-V4 Flash 等）独立卡 **本主题不核验**。

### 7.2 引用

- SK Telecom. *A.X K2 Technical Report*. arXiv:**2608.30181v1** \[cs.AI\], **31 Aug 2026**.
 Abs：https://arxiv.org/abs/2608.30181
 PDF：https://arxiv.org/pdf/2608.30181
 本地：`https://arxiv.org/abs/2608.30181`
 （2026-09-22 CST / Asia/Shanghai）
 权重：https://huggingface.co/skt/A.X-K2

### 7.3 关联笔记

- 模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md / 模型与技术报告/厂商报告/DeepSeekV32技术报告深读.md / 模型与技术报告/厂商报告/KimiK2技术报告深读.md / 模型与技术报告/厂商报告/GLM45技术报告深读.md / 模型与技术报告/厂商报告/Qwen3技术报告深读.md
- [[混合专家架构]] MoE；[[长上下文位置编码与系统侧]] 长上下文；[[注意力效率族MQA到MLA]] 注意力效率；[[智能体工具与长程任务]] agents
- [[MOC_模型与技术报告]]；交叉 **[[EAGLE3投机解码]]** EAGLE-3 增量（勿在本卡展开）

## 相关笔记

- [[Gemma4技术报告深读|Gemma 4]]
- [[AXK2技术报告深读|AX-K2]]
- [[UIVenus2GUI智能体|UI-Venus-2]]
- [[宪法分类器防御|Constitutional Classifiers]]
- [[过程奖励模型PRM谱系|Process Reward Models]]

