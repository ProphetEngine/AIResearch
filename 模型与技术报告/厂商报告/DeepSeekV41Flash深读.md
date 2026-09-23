---
title: "DeepSeek-V4.1-Flash Technical Report 深读"
topic: DeepSeekV41Flash深读
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2609.19969
arxiv: "2609.19969"
archived: 2026-09-22
---

# DeepSeek-V4.1-Flash Technical Report 深读卡

> **定位**：DeepSeek-V4.1 Flash 增量技术报告主题轴（相对已入库 V3 / V3.2）。数字一律取自官方 PDF `https://arxiv.org/abs/2609.19969`（2026-09-22 CST）。
> **攻坚线**：**架构思想（主）** + **AI Infra / KV·部署（辅）**。
> **刻意不写**：Switch→Mixtral→V3 MoE 史线与 671B/37B/14.8T/DualPipe/FP8 分块配方（见 [[混合专家架构]]、[[DeepSeekV3训练与MoE基建]]）；DSA 两阶段继续训与 GRPO 四稳定化全文（见 [[DeepSeekV32技术报告深读]]）；KV 量化通史（留给 [[KV缓存量化与压缩]]）。本卡只补「相对 V3/V3.2 **本 PDF 新公开** 的 CED / CSA2 / FP4 KV / SWA Bounded Replay」。
> **禁止编造**：本 PDF **对照锚点是 DeepSeek-V4 / V4-Flash / V4-Pro**，**未重开** V3 的 671B/37B 表 → 不得把 V3 数字外推为 V4.1-Flash 主张；V4 本体无本仓库独立 TR → V4 侧数字仅录本 PDF 转述。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression | 封面；Abstract |
| 作者 / 联系 | DeepSeek-AI；`research@deepseek.com`；长名单见封面与附录作者页 | 封面 |
| arXiv 页眉 | **arXiv:2609.19969v1** \[cs.CL\] **17 Sep 2026** | PDF 第 1 页页眉 |
| PDF 页数 | **51**（A4） | |
| 本地路径 | `https://arxiv.org/abs/2609.19969`（1,663,475 bytes） | 仓库 |
| 权重入口 | https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash | Abstract 末句 |
| 摘要四关键词 | (1) **CED**（prefill **8B** / decode **16B**）；(2) **CSA2** 跨层 KV/索引复用；(3) **FP4** global KV；(4) **SWA Bounded Replay** | Abstract |
| 骨干规模（摘要/§2.1） | **552B** backbone；上下文至 **1M** tokens；预训练多模态语料 **45T** tokens | Abstract；§2.1；§4.2 |

**摘要级一句话（不外推）：**
V4.1-Flash 把「长程 agent + 输入重」瓶颈从算力进一步压到 **HBM / SSD / 带宽上的 KV**；用 **CED 砍 prefill 激活**、**CSA2+FP4 砍常驻 HBM 的 global KV（890 B/token ≈ V4-Flash 的 1/4）**、**SWA Bounded Replay 砍持久化 KV（≈ V4-Flash 的 1/8）**，并在 **纯 CSA2（相对 V4 的 CSA–HCA 混合）** 上从零训稀疏注意力。

**命名边界（正文用法）：**

| 名称 | 本 PDF 中的关系 |
|---|---|
| DeepSeek-**V4** / V4-Flash / V4-Pro | 对照基线；CSA–HCA 混合、SWA 持久化策略、Exact SWA replay 成本、FP8 main KV 等对比均相对它们 |
| DeepSeek-**V4.1-Flash** | 本报告主体：CED + 纯 CSA2 + FP4 main KV + SWA Bounded Replay + Engram/DSpark/Single-Pass mHC |
| DeepSeek-V4.1-Flash-**Base** | 预训练底座评测（Table 1 / Fig 6） |
| （产品后训练版）DeepSeek-V4.1-Flash | §5 后训练后的 agent/推理主表（Table 3–4） |

---

## 二、相对 V3 / V3.2（及本 PDF 内 V4）增量对照

> 左列以本 PDF 明文为准。V3 / V3.2 列仅作「已入库笔记锚点」，细节见对应 TR；**本报告几乎不讨论 DSA/MLA 挂接**，主叙事在 CED/CSA2/部署。

| 维度 | DeepSeek-V3（已入库 TR） | DeepSeek-V3.2（已入库 TR） | **DeepSeek-V4.1-Flash（本 PDF）** |
|---|---|---|---|
| 报告入口 | arXiv:2412.19437 | arXiv:2512.02556 · 23 页 | arXiv:**2609.19969v1** · **51** 页 · 2026-09-17 |
| 问题设定 | 训 MoE+MLA 基座；部署侧重并行/FP8 | 长文算力 → **DSA**；后训练加码 RL/agent 合成 | **KV 存储与迁移**成为主瓶颈（HBM 上 global KV；SSD/主机上 persistent KV）|
| 主干注意力 | MLA（稠密核心） | MLA + **DSA**（lightning indexer + top-$k$） | **纯 CSA2**（相对 V4 的 **CSA–HCA 混合**）；每层另有 **SWA**（前两层仅 SWA） |
| 层结构 | Decoder-only | Decoder-only（相对 Terminus「唯一架构改动=DSA」） | **CED**：40 层 = **20** causal encoder + **20** decoder；decoder **global KV 由 $H_{L/2}$ 投影**（式 1） |
| 激活参（本 PDF） | （本 PDF 未重述 V3 数字） | （本 PDF 未重述） | **prefill 8B / decode 16B**；backbone **552B**；Engram **196B** |
| KV 精度叙事 | 训练/推理 FP8 配方（V3 TR） | indexer 可 FP8（DSA） | **FP4 main KV**（post-training QAT）；indexer 侧 V4 已有 FP4 QAT；**SWA KV 仍 FP8** |
| 全局 KV 足迹 | Fig 1(b) 代际对比链上的前代 | — | **890 bytes/token**（always in HBM）≈ **V4-Flash 的 1/4**；相对 V1 约 **437×** 缩小（Fig 1(b)） |
| 持久化 KV | — | — | **SWA Bounded Replay** → persistent footprint ≈ **V4-Flash 的 1/8**（不再把 SWA KV 进 SSD 持久层） |
| 上下文 / PT | 14.8T；YaRN 扩窗等 | DSA 继续训 128K | **45T** 多模态；**64K 稀疏从零训**（无 dense warmup）；**34T** 起扩到 **1M** |
| 投机 / 多 token | **MTP** 与骨干联合预训练 | （沿 V3 叙事） | **省略 MTP**；预训练后独立训 **DSpark**，后训练继续对齐但不回传骨干 |
| 后训练主张 | SFT+早期 GRPO | 算法增量重（GRPO 稳定化、DSA 继续训） | **明确：无算法创新**；SFT→RL→OPD 沿 V4 惯例；增量在 **数据/环境合成与规模** |
| MoE | DeepSeekMoE 完整配方 | 本报告未重开 MoE 表 | **保留** shared + fine-grained routed；本 PDF 给出本代配置（§4.2.1），**不重写 V3 MoE 全文** |

**增量一句话：**
相对 V3「造 MoE+MLA 基座」与 V3.2「DSA 继续训 + 加码 RL」，本卡公开增量几乎全部落在 **CED 半深 prefill**、**CSA2 三模式跨层复用 + 层次化 indexer**、**FP4 main KV QAT**、**SWA Bounded Replay 部署折中**——MoE 只给本代超参表，**禁止当新专家拓扑史重写**。

---

## 三、四大重点机制（本卡主轴）

### 3.1 Causal Encoder-Decoder（CED，§2.2）

**动机：** agent 工具调用频繁 → **prefill / KV miss** 贵；YOCO（Sun et al., 2024）让上半层共享下半层 KV。CED 在此上加强「KV 容量 + KV 生成深度」。

**全局注意力：**

- 底 **$L/2$** 层 = causal encoder。
- 对 decoder 层 $l > L/2$：KV **不**从本层 $H_l$ 来，而从 **$H_{L/2}$** 用层相关投影得到：

$$
C_l = H_{L/2} W_l^{KV},\quad Z_l = H_{L/2} W_l^{Z},\quad l > L/2
$$

（式 1；$C$=KV entries，$Z$=compression weights。）

- Prefill 时只需跑前半网络即可拿到上半层 global KV → **近乎减半 prefill 计算**。

**SWA：**

- 仍 **逐层** 从本层 $H_l$ 生成 local KV（加深局部计算深度）。
- 完整 decoder SWA 需额外处理约 $n_{\mathrm{win}} \times L/2$ tokens；短 turn 多轮时开销显著。
- → 引入 **Decoder SWA Bounded Replay**：只对 prompt **最后 $n_{\mathrm{win}}$** tokens 做 SWA 回放（细节 §3.2.2）。

**复杂度（§2.2）：** $N \gg n_{\mathrm{win}}$ 时，prefill $\mathrm{O}(NL) \to \mathrm{O}(NL/2 + n_{\mathrm{win}} L/2) \approx \mathrm{O}(NL/2)$。

**与激活数字的衔接（§2.1 / Abstract）：** CED 使 **prefill 激活 8B、decode 激活 16B**——对 input-heavy agent 特别划算。

### 3.2 Compressed Sparse Attention 2（CSA2，§2.3）

**三维压缩乘积（§2.3 引言）：** entry 大小（GQA/MLA 类）× 序列压缩（每 $m$ token 一 entry，如 V4 的 CSA/HCA）× **层维复用**。CSA2 声称同时覆盖三者，且 **cache 共享与 index 复用解耦**。

**相对 CSA 的简化（明文）：**

| 项 | CSA（V4） | **CSA2（本报告）** |
|---|---|---|
| 压缩源重叠 | 压缩比 $m$ 时每 entry 来自 **$2m$** 原始 KV，相邻 entry **重叠** | **去掉重叠** |
| 位置编码 | 压缩时含 **absolute PE** | **去掉** |
| Indexer K | 自 hidden 另开压缩路径 | **由 main KV 投影**得到 |
| 架构组合 | V4：**CSA–HCA 混合** | V4.1-Flash：**纯 CSA2** |

**三模式（静态分配；Fig 4）：** 三模式均在本层算 **main Q + SWA KV**，再与选中的 main KV 做注意力。

| 模式 | main KV / indexer K | Top-K indices | 作用 |
|---|---|---|---|
| **Full** | 本层生成；indexer K 由本层 main KV 投影 | 本层 indexer 新算 | 完整路径（≈ V4 完整 CSA） |
| **Reindex** | **复用**最近 Full 层的 main KV + indexer K | 本层 indexer Q **重打分** → 新 Top-K | 共享 cache，允许层间选中集变化 |
| **Reuse** | 同上复用 | **复用**最近 Full/Reindex 的 Top-K | 不再算 indexer Q / scores |

**与 CED 结合：** decoder 的 Full 层从 **$H_{L/2}$**（encoder 末层）投影自己的 global KV；Reindex/Reuse 不变。

**Hierarchical Sparse Indexer（仅 decoder，§2.3.2）：**

- 首个 Full 层：全上下文打分 → 本层 Top-K；并做 **blockwise** 候选：块分=块内 max score，选高分块拼成 **candidate pool**。
- 例：选 **2048** blocks × **8** positions → 至多 **16,384** candidates。
- 后续 Reindex：只在 pool 内打分选 Top-K；Reuse：不索引。
- 固定 pool 大小 → 深层 indexer **每 query 代价对上下文长度恒定**；首 Full 仍全扫。
- **训练感知**：后训练引入；训推同一候选限制。

**本代层分配（§4.2.1，可对表 Fig 3）：**

| 区段 | 层数 / 配置 |
|---|---|
| 总层 | **40**；encoder **20** + decoder **20**；$d=5120$ |
| Encoder 前 2 层 | **仅 SWA** |
| Encoder 余 18 层 | CSA2，$m=2$；3 组×6：每组 **1 Full + 5 Reuse** |
| Decoder 20 层 | CSA2，$m=1$；第 1 组 4 层：**1 Full + 3 Reuse**；后 4 组×4：**1 Reindex + 3 Reuse** |
| Indexer / 稀疏 | indexer Q heads **32**，dim **128**；attention top-$k$=**512**；query heads **64**，head dim **512**，query compression dim **1280** |
| SWA 窗 | $n_{\mathrm{win}}=$**128** |
| Hier. indexer | max **2048** blocks × **8** pos → **16,384** candidates |

### 3.3 FP4 Main KV Cache（§2.4.4）

| 点 | 报告要点 |
|---|---|
| 前史 | V4 已对 **indexer Q/K** 做 FP4 QAT；格式取 **OCP MXFP4**（兼容硬件面优先，实验中别的格式可能更准） |
| 本代扩展 | QAT 扩到 **main KV**：**省存储**而非加速 matmul；**先反量化再注意力** → 可用更准格式且不要求原生 FP4 GEMM |
| 选用格式 | 约 4-bit 候选中选 **E2M1 + 每 16 channel 一个 E4M3 scale**（跟 NVFP4，但 **去掉二级 global scale**） |
| 动态范围论证 | 最大 RMSNorm 权重量级约 **1**；512-d KV latent L2 上界约 $\sqrt{512}$；RoPE 保范；训练观测最大幅约 **10** ≪ $448\times6=2688$ → 去 global scale **无测得掉点** |
| 何时量化 | **Post-training** 引入 QAT；**RoPE 之后**量化（RoPE 前量化仅边际收益且解码开销↑） |
| 非对称保留 | **SWA KV 仍 FP8**（对量化敏感） |
| 相对 V4 | 相对 V4 的 **FP8 main KV**，该格式 **近乎减半** HBM 与 SSD 上的 main KV 体积 |

**与 CSA2 合读（Abstract / §1）：** CSA2 跨层复用 + FP4 → global KV（always in HBM）**890 B/token ≈ V4-Flash 的 1/4**。

### 3.4 SWA Bounded Replay（§3.2.1–3.2.2）

**问题：** SWA 跨层依赖累积 → **精确**重建 $L$ 层 SWA KV 需回放 **$L \times n_{\mathrm{win}}$** tokens（V4「Zero SWA Caching / Exact reconstruction」在生产中过贵）。SWA 复用窗口短（分钟级 session），却占 V4 persistent cache **近一半**，与「≥72h 长尾复用」的 global KV 策略不匹配。

**近似定义：** 只回放最近 **$n_{\mathrm{win}}$** tokens，并把 SWA 截断到回放段：从位置 $s$ 起，query $i$ 只看 $\bigl[\max(s, i-W+1), i\bigr]$ 内的 SWA keys。

**两路径：**

| 路径 | 作用 | 做法 |
|---|---|---|
| **Encoder SWA Bounded Replay** | 让 prefix cache **只依赖 global KV** → SWA 可移出 persistent 层 | miss 时回放 cached prefix 的最后 $n_{\mathrm{win}}$（只再生 SWA，**复用且不覆写** cached global KV）+ 处理 uncached suffix（生成 global+SWA） |
| **Decoder SWA Bounded Replay** | 配 CED：几乎半掉 prefill | 每轮 prefill 回放 prompt 末 $n_{\mathrm{win}}$，encoder 输出过 decoder 层（同截断）；得到的 decoder SWA **仅供 decode，不进 prefix cache** |

**持久化管理变更（§3.2.1）：**

1. SWA KV **不再**进 SSD persistent；改放各机 **host DRAM 的 10%** 组成的分布式内存池；TTL **仅分钟级**；global KV 仍 persistent，保证寿命 **≥72h**。
2. SWA miss 用 Encoder Bounded Replay 兜底：回放 **$n_{\mathrm{win}}$** 而非 **$L\times n_{\mathrm{win}}$**。

**乘积账（明文）：** 去掉 persistent SWA（约 **×1/2**）× global 压到 V4 的 **1/4** → persistent 总体 ≈ **V4 的 1/8**。
**质量：** 文称近似状态 **几乎不影响** response quality；decoder 路径在后训练中 **模拟同 replay** 做 train-aware。

---

## 四、架构扩展与训练/推理要点（辅，防漏读）

### 4.1 其他架构扩展（§2.4–2.5；非本卡主轴）

| 组件 | 要点（仅录本 PDF） |
|---|---|
| **Single-Pass mHC** | 相对 V4 mHC：输入混合系数 **错一位**消依赖；部署 **Mega-mHC** 单核实现 mHC $(3n+2)d$ / Single-Pass $(2n+2)d$ 激活读写，相对原四核实现约 **减半**（§2.4.1） |
| **Engram** | 条件记忆；**196B** 参数均分两模块；$N$-gram \{2,3,4\}；8 hash heads；省略短因果卷积；层 **1、14**（0-index）；表与 KV 投影 **FP8**；推理可 host RDMA prefetch |
| **DSpark** | 投机解码：3 Transformer block、窗 **128**；单次前向并行 **5** draft 位 + 轻量 Markov 头；confidence-scheduled verify；**预训练后**单独训（冻骨干）；后训练继续训且 **不**把 DSpark loss 回传骨干 |
| **DeepSeek-ViT** | 从零训；2D-RoPE；线性 patch proj（Muon 兼容）；RMSNorm+SwiGLU；3×3 pixel-unshuffle → 视觉 token **÷9**；约支持至 **1344×1344** |
| **MoE 本代超参** | 每层 **1 shared + 384 routed**；每 token 激活 **6** routed；expert FFN 中间维 **2304**；SwiGLU clamp **10**；图/文 **分模态** aux-loss-free bias |
| **MTP** | 骨干预训练 **省略** MTP |

### 4.2 预训练数字快照（§4.2）

| 项 | 值 |
|---|---|
| 语料 | **45T** tokens 多模态；text:multimodal token 比约 **7:1**（去重并集后） |
| 序列 | **64K** 稀疏从零（**无** dense warmup）；**34T** 处扩到 **1M** |
| Batch | 固定 **100.6M** tokens/step |
| LR | warmup 2000 steps → $2.6\times10^{-4}$ 至 28T；28T–40T cosine 至 $2.6\times10^{-5}$；40T–45T 保持；称 **no instability** |
| 优化器 | 线性层 **Muon**；RMSNorm 等 **AdamW**；embedding/预测头 **Sinkhorn-balanced**；Engram LR ×**5** |

### 4.3 推理系统要点（§3.2）

- **EPD** 分离：Encoder–Prefill–Decode（文中亦称 EPD disaggregation）可独立扩缩。
- CSA2 **Reuse** 层：prefill **15** kernels / decode **11** kernels（融合后）。
- Decode FLOPs（Fig 2，精度加权 BF16/FP8/FP4 = 1/0.5/0.25）：4K→1M（**256×** 上下文）Decode FLOPs 仅增约 **1/4**，显著低于 V4-Flash 的增长。

### 4.4 后训练定位（§5；非主轴）

- 作者自陈：**无后训练算法创新**；SFT → RL → **OPD**（on-policy distillation），沿 V4 惯例。
- 增量在任务/环境合成、难度与正确性奖励、规模化 rollout（含 DSec 等）。
- Controllable reasoning effort：API 档对应标量 $b$（Table 2：如 100/75/…）；effort 25→100：八项推理均分 67.1%→76.3%；DeepSWE v1.1 66.0%→74.2%；Terminal-Bench 2.1 82.4%→90.6%；输出约 **2.5×**。

---

## 五、评测快照（跟读用，非主轴）

### 5.1 Base（Table 1 摘录；内部框架同设定）

| 项 | V4-Flash-Base | V4-Pro-Base | **V4.1-Flash-Base** |
|---|---:|---:|---:|
| Activated params | 13B | 49B | **8B/16B** |
| Backbone params | 284B | 1.6T | **552B** |
| MMLU-Pro (EM) | 68.3 | 73.5 | **74.1** |
| HumanEval Pass@1 | 69.5 | 76.8 | **79.4** |
| SuperGPQA (EM) | 46.5 | 53.9 | 53.1 |
| 多模态列 | — | — | MMMU-Pro 56.5；CVBench 77.9；DocVQA 95.6；RefCOCO-avg 86.0 |

引言口径：相对 V4-Pro-Base，用约 **1/3** 总参、**1/4** 激活参，世界知识/推理/代码可比，held-out 有 **5%–10%** 改进（Fig 6 BPB 全任务最低）。

### 5.2 后训练主表（Table 3 摘录，Max effort）

| Benchmark | Opus-5 | GPT-5.6 Sol | DS-V4-Pro | DS-V4-Flash | **DS-V4.1-Flash** |
|---|---:|---:|---:|---:|---:|
| GPQA Diamond | 93.4 | 94.1 | 92.4 | 89.9 | **90.9** |
| Codeforces Rating | — | — | 3348 | 3289 | **3471** |
| Terminal-Bench 2.1 | 89.1 | 88.8 | 87.9 | 82.7 | **90.6** |
| Terminal-Bench 4.0 | 51.8 | 39.9 | 12.4 | 7.0 | **31.2** |
| DeepSWE v1.1 | 74.0 | 73.0 | 62.7 | 54.4 | **74.2** |

**自承差距：** 科学向超难 agent（如 TB 4.0）相对巨型闭源仍有缺口；多模态整体相对顶尖闭源仍有可见差距；引言称日常任务可完成 **>95%**（作者主张，非第三方审计）。

### 5.3 局限（§6）

1. 新架构带来的 **鲁棒边界未充分刻画**：CSA2 选错、SWA Bounded Replay 近似重建可能在未测边界掉点。
2. 标准榜趋饱和；相对顶尖闭源在 **最难推理/边角** 仍有真实差距。
3. 未来：扩 stress-test；数据×容量×RL 协同扩展；model–harness 共设计。

---

## 六、相对已入库笔记的增量边界

| 已有笔记 | 已覆盖（本卡不复述） | **本卡新增 / 加深** |
|---|---|---|
| **[[DeepSeekV3训练与MoE基建]]** | MLA/MoE/MTP；14.8T；DualPipe；FP8 训练配方 | **CED 式 (1)**；本代 MoE **仅超参表**；**无 MTP**、改 DSpark |
| **[[DeepSeekV32技术报告深读]]** | DSA 两阶段；GRPO 四件套；128K agent 合成 | **不是 DSA 续篇**：纯 **CSA2** 三模式 + Hier. indexer；部署侧 **SWA Bounded Replay**；**FP4 main KV** |
| **[[混合专家架构]]** | MoE 史线 | 无新专家拓扑哲学；仅 384/6/2304 等本代数 |
| **[[长上下文位置编码与系统侧]] / [[注意力效率族MQA到MLA]]** | 长上下文 / 注意力效率通论 | 890 B/token、1/4 & 1/8 相对 V4-Flash、Reuse 核数、Decode FLOPs 近恒 |
| **[[AI基础设施总览]] / B7** | Infra / 引擎选型 | EPD；persistent vs host DRAM 10%；不写引擎通史 |
| **[[KV缓存量化与压缩]]（待做）** | — | 本卡只记 V4.1 **产品解**（E2M1+scale16、RoPE 后 QAT）；通史/误差轴留给 [[KV缓存量化与压缩]] |

**一句话：**
V3/V3.2 卡讲清「基座怎么训、DSA/RL 怎么叠加」；本卡讲清「在 V4 系上如何用 **CED+CSA2+FP4+Bounded Replay** 把 KV 压到可规模化部署长程 agent」——并标明 **对照基线是 V4-Flash，不是把 V3 数字改名重贴**。

---

## 七、待核实与引用

### 7.1 待核实（禁止当作已确认）

1. **DeepSeek-V4 / V4-Flash / V4-Pro 独立完整 TR**：本仓库暂无对应 PDF；CSA–HCA 细节、V4 Exact SWA replay 数字等 **仅本 PDF 转述**。
2. **890 bytes/token 的逐项分解表**：正文给总数与「≈1/4 V4-Flash」，未在抽取文本中给逐字段字节账；若需拆解应回读 Fig 1(b) 或后续 blog。
3. **「1/3 total / 1/4 activated vs V4-Pro」**：以引言对 Base 的参数对比为准（Table 1：552B vs 1.6T；8B/16B vs 49B）——引用时注明是作者口径。
4. **Fig 2 / Fig 6 曲线数值点**：文本层无逐点表。
5. **Table 3 对照模型全名与评测 scaffold**：正文有 Max effort 与 scaffold 附录；跨 scaffold 方差见 Table 4/5——引用单点分数须标明 scaffold。
6. **HF 权重许可、API 定价、与新闻站发布日差异**：以 arXiv **2026-09-17** 与官方 PDF 为准。
7. 结论中出现的外部型号名（如 GLM-5.3、Kimi-K3、Fable-5、GPT-6 Astra 等）为作者对比叙事；**本卡不核验其独立卡**。

### 7.2 引用

- DeepSeek-AI. *DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression*. arXiv:**2609.19969v1** \[cs.CL\], **17 Sep 2026**.
 Abs：https://arxiv.org/abs/2609.19969
 PDF：https://arxiv.org/pdf/2609.19969
 本地：`https://arxiv.org/abs/2609.19969`
 权重：https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash

### 7.3 关联笔记

- [[DeepSeekV3训练与MoE基建]]：模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md
- [[DeepSeekV32技术报告深读]]：模型与技术报告/厂商报告/DeepSeekV32技术报告深读.md
- [[混合专家架构]] / [[长上下文位置编码与系统侧]] / [[注意力效率族MQA到MLA]] / [[AI基础设施总览]] / [[智能体工具与长程任务]]：MoE 史、长上下文、注意力效率、Infra、agent
- [[MOC_模型与技术报告]]；交叉 **[[KV缓存量化与压缩]]** KV 量化通史（勿在本卡展开）

## 相关笔记

- [[GPT6AstraSystemCard|GPT-6 Astra]]
- [[DeepSeekV41Flash深读|DeepSeek-V4.1 Flash]]
- [[Qwen38Next架构深读|Qwen3.8-Next]]
- [[ClaudeOpus5SystemCard|Claude Opus 5]]
- [[GRPO与DAPO算法族|GRPO→DAPO]]
- [[SystemCard与TR扫描2025至2026|TR 扫描]]

