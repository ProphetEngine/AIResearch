---
title: "DeepSeek-V4 Technical Report 深读"
topic: DeepSeekV4技术报告深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
source_url: https://arxiv.org/abs/2606.19348
arxiv: "2606.19348"
archived: 2026-09-22
---

# DeepSeek-V4 Technical Report 深读卡

> **定位**：DeepSeek-V4 技术报告主题轴——补齐 [[DeepSeekV41Flash深读]] 多次声明的「V4 / V4-Flash / V4-Pro 无本仓库独立 TR」缺口。数字一律取自官方 PDF `https://arxiv.org/abs/2606.19348`（2026-09-22 CST）。
> **攻坚线**：**架构思想（主）** + **评测字段（文内长上下文 / agent 表，辅）**。
> **刻意不写**：Switch→Mixtral→V3 MoE 史线与 DualPipe/FP8 分块配方（见 [[混合专家架构]]、[[DeepSeekV3训练与MoE基建]]）；DSA 两阶段继续训与 GRPO 四稳定化全文（见 [[DeepSeekV32技术报告深读]]）；**CED / CSA2 / FP4 main KV / SWA Bounded Replay** 全文（见 **[[DeepSeekV41Flash深读]]**）；通用 KV 量化通史（见 **[[KV缓存量化与压缩]]**，本卡只录 V4 **产品解**）。
> **禁止编造**：本 PDF 自称 **preview**；对照锚点是 **V3 / V3.2**，**不是** V4.1-Flash → 不得把 [[DeepSeekV41Flash深读]] 的 CED/CSA2 数字回贴为 V4 主张；V4.1-Flash 侧数字仅作划界引用。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence | 封面； Title |
| 作者 / 联系 | DeepSeek-AI；`research@deepseek.com`；长名单见附录 A | 封面；§A |
| arXiv 页眉 | **arXiv:2606.19348v1** \[cs.CL\] **26 Apr 2026** | PDF 第 1 页页眉 |
| PDF 页数 | **58**（A4） | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:a6404ea) | |
| 本地路径 | `https://arxiv.org/abs/2606.19348`（4,713,349 bytes） | 仓库 |
| 权重入口 | https://huggingface.co/collections/deepseek-ai/deepseek-v4 | Abstract 末句 |
| 推理参考实现 | https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/tree/main/inference | §2.3 脚注 1 |
| 摘要级关键词 | (1) **CSA+HCA 混合注意力**；(2) **mHC**；(3) **Muon**；(4) **≥32T** PT + 后训练；(5) **1M** 上下文 | Abstract |

**摘要级一句话（不外推）：**
本报告给出 DeepSeek-V4 **系列 preview**：V4-**Pro**（**1.6T** 总参 / **49B** 激活）与 V4-**Flash**（**284B** / **13B**），原生 **1M** 上下文；相对 V3.2，用 **CSA（压缩后 DSA）+ HCA（更重压缩、稠密注意）** 混合把长文单 token FLOPs / KV 压到可规模化部署，再经 specialist GRPO → **OPD** 合并出统一产品模型。

**命名边界（正文用法）：**

| 名称 | 本 PDF 中的关系 |
|---|---|
| DeepSeek-**V4** series | 系列总称；preview |
| DeepSeek-**V4-Pro** / **V4-Flash** | 两档底座规模（Base → 后训练产品） |
| DeepSeek-**V4-Pro-Max** / **V4-Flash-Max** | Think **Max** 推理努力档（Table 2/6/7） |
| Non-think / Think High / Think Max | 三档 reasoning effort（Table 2） |
| DeepSeek-**V4.1-Flash** | **本 PDF 未出现** → 见 [[DeepSeekV41Flash深读]]；本卡不写其 CED/CSA2 |

---

## 二、相对 V3 / V3.2（及划界 V4.1-Flash）增量对照

> 左列以本 PDF 明文为准。V3 / V3.2 列仅作「已入库笔记锚点」；V4.1-Flash 列只标「本卡不写」。

| 维度 | DeepSeek-V3（已入库 TR） | DeepSeek-V3.2（已入库 TR） | **DeepSeek-V4（本 PDF）** | V4.1-Flash（[[DeepSeekV41Flash深读]]，本卡不写） |
|---|---|---|---|---|
| 报告入口 | arXiv:2412.19437 | arXiv:2512.02556 · 23 页 | arXiv:**2606.19348v1** · **58** 页 · 2026-04-26 | arXiv:2609.19969 · 51 页 |
| 问题设定 | 训 MoE+MLA 基座 | 长文算力 → **DSA**；后训练加码 | **百万 token 上下文**成为主轴；CSA+HCA 混合 | 进一步压 **HBM/SSD 上的 KV** |
| 主干注意力 | MLA | MLA + **DSA** | **CSA–HCA 交错**；前层 SWA/HCA 特例 | **纯 CSA2**（相对本卡的 CSA–HCA） |
| 残差 | 标准 residual | — | **mHC**（双随机流形约束） | Single-Pass mHC 等增量 |
| 优化器 | AdamW 系主叙事 | — | 主体 **Muon** + 部分 AdamW | Muon 等延续 |
| 规模（本 PDF） | 671B / 37B 等 | （本 PDF 对照表用 V3.2-Base） | **Pro 1.6T/49B**；**Flash 284B/13B** | 552B；prefill 8B / decode 16B（CED） |
| 预训练 tokens | 14.8T 等 | DSA 继续训量级 | Flash **32T**；Pro **33T**；语料「>32T」 | **45T** 多模态 |
| 上下文 | YaRN 扩窗等 | 128K 继续训 | 原生扩到 **1M**（4K→16K→64K→1M） | 1M；64K 稀疏从零 |
| 相对 V3.2 效率（1M） | — | 对照基线 | **Pro**：单 token FLOPs **27%**、KV **10%**；**Flash**：FLOPs **10%**、KV **7%**（等价 FP8 FLOPs） | 相对 **V4-Flash** 再压 global/persistent KV |
| 后训练 | SFT+早期 GRPO | 混合 RL + agent 合成 | specialist **SFT→GRPO** → 多教师 **OPD**（**取代** V3.2 混合 RL 合并阶段） | 沿 V4 惯例；作者称无算法创新 |
| MTP | 有 | 沿 V3 | **保留**，配置同 V3 | **省略** MTP → DSpark |

**增量一句话：**
相对 V3「造 MoE+MLA 基座」与 V3.2「DSA 继续训 + 混合 RL」，本卡公开增量几乎全部落在 **CSA+HCA 混合百万窗**、**mHC**、**Muon**、**异构 KV / 磁盘持久化产品解**，以及后训练 **OPD 取代混合 RL 合并**——MoE 只给本代超参与少量改动，**禁止当新专家拓扑史重写**。

---

## 三、架构主轴（本卡核心）

### 3.1 继承自 V3（§2.1；只录差分）

| 组件 | 本 PDF 明文差分 |
|---|---|
| DeepSeekMoE | 仍 shared + fine-grained routed；亲和分 **Sigmoid → Sqrt(Softplus)**；aux-loss-free + 轻微 sequence-wise balance；**去掉** routing 目标节点数约束；前若干层改 **Hash routing**（按 token ID） |
| MTP | 策略与 V3 **相同**，depth=**1**（§4.2.1） |
| 其余未述 | 「All other unspecified details follow … DeepSeek-V3」 |

### 3.2 Manifold-Constrained Hyper-Connections（mHC，§2.2）

**动机：** 朴素 Hyper-Connections（HC）把 residual 宽扩到 $n_{\mathrm{hc}}\times d$，但深层堆叠易数值不稳。

**核心约束：** 把 residual 映射矩阵 $B_l$ 投影到 **双随机矩阵**（Birkhoff）流形 $\mathcal{M}$，使 $\|B_l\|_2\le 1$（非扩张），且 $\mathcal{M}$ 对乘法封闭；输入/输出映射 $A_l,C_l$ 经 Sigmoid 保非负有界（式 2–7）。

**动态参数化：** $A,B,C$ 各 = 输入依赖动态项 + 静态 bias + 可学习门控 $\alpha$（式 3–5）；$B$ 用 **Sinkhorn-Knopp**，$t_{\max}=$**20**。

**本代超参：** $n_{\mathrm{hc}}=$**4**（Flash 与 Pro 同，§4.2.1）。

### 3.3 Hybrid Attention：CSA + HCA（§2.3）

**总设定：** 交错混合；CSA 先把每 $m$ token 压成 1 条再做 **DSA top-$k$**；HCA 用更大 $m'\gg m$ 压缩但 **保持稠密** 注意；二者均附带 **SWA 分支**（窗 $n_{\mathrm{win}}$）。开源实现见脚注 1。

#### 3.3.1 CSA（Compressed Sparse Attention）

1. **压缩 KV：** 两路 $C^a,C^b$ 与权重 $Z^a,Z^b$；每 entry 由 **$2m$** 原始 KV 加权合成，相邻 entry **索引重叠** → 序列长度压到约 $1/m$（式 9–12；Fig 3）。
2. **Lightning indexer：** 同压缩得到 indexer K；query 侧低秩（式 13–16）；**Top-$k$** 选压缩 KV（式 17）。
3. **Shared-KV MQA：** 选中压缩条目同时作 K/V；query 与 indexer 共享压缩 latent $c_t^Q$（式 18–19）。
4. **Grouped output projection：** $n_h$ 头先分成 $g$ 组中间投影再拼回，减轻大 $c\cdot n_h$ 投影负担。

#### 3.3.2 HCA（Heavily Compressed Attention）

- 压缩比 $m'\gg m$；**无** CSA 式重叠压缩；**无** sparse top-$k$（式 20–26；Fig 4）。
- 同样 Shared-KV MQA + grouped output projection。

#### 3.3.3 其它注意细节（§2.3.3）

| 技巧 | 要点 |
|---|---|
| Q/KV RMSNorm | core attention 前对 query 各头与压缩 KV 单头做 RMSNorm |
| Partial RoPE | 对 query / KV / core 输出 **末 64 维**；输出侧用位置 $-i$ 抵消绝对位置，保留相对距离 |
| SWA 分支 | 每 query 另产最近 $n_{\mathrm{win}}$ **未压缩** KV，与压缩 KV 一并进 core attention（保证块内因果 + 近邻） |
| Attention sink | 每头可学习 sink logit，允许总注意质量 $\ne 1$（式 27） |

#### 3.3.4 效率口径（§2.3.4 + Abstract / §1）

| 点 | 报告要点 |
|---|---|
| KV 存储混合精度 | RoPE 维 **BF16**，其余 **FP8** → 相对纯 BF16 KV **近乎减半** |
| Indexer 计算 | lightning indexer 注意力 **FP4** |
| top-$k$ | 相对 V3.2 **更小** top-$k$，利短/中文 |
| 相对 BF16 GQA8（d_h=128） | 1M 设定下 KV ≈ 基线的 **2%** |
| 相对 V3.2 @1M | Pro：**27%** FLOPs / **10%** KV；Flash：**10%** FLOPs / **7%** KV |
| Expert 权 | routed expert **FP4**；作者称现硬件 FP4×FP8 峰值与 FP8×FP8 同，未来硬件可再挖约 **1/3** |

### 3.4 本代层 / MoE 超参快照（§4.2.1）

| 项 | **V4-Flash** | **V4-Pro** |
|---|---|---|
| 层数 / $d$ | **43** / **4096** | **61** / **7168** |
| 前层注意 | 前 **2** 层 **纯 SWA** | 前 **2** 层 **HCA** |
| 其后 | CSA / HCA **交错** | 同左 |
| CSA $m$ / top-$k$ / indexer | $m=$**4**；top-$k$=**512**；$n_h^I=$64，$c_I=$128 | $m=$**4**；top-$k$=**1024**；indexer 同 |
| HCA $m'$ | **128** | **128** |
| Query 头 / $c$ / $d_c$ | $n_h=$64，$c=$512，$d_c=$1024 | $n_h=$128，$c=$512，$d_c=$1536 |
| 输出分组 | $g=$8，$d_g=$1024 | $g=$16，$d_g=$1024 |
| $n_{\mathrm{win}}$ | **128** | **128** |
| MoE | 1 shared + **256** routed；激活 **6**；中间维 **2048**；前 **3** 层 Hash routing | 1 shared + **384** routed；激活 **6**；中间维 **3072**；前 **3** 层 Hash |
| mHC / MTP | $n_{\mathrm{hc}}=$4；MTP depth 1 | 同 |
| 总参 / 激活 | **284B / 13B** | **1.6T / 49B** |

> **未在正文给出** CSA:HCA 精确层比数字 → 划入待核实；开源 inference 树可核。

### 3.5 Muon 优化器（§2.4）

- 主体模块用 **Muon**（Alg. 1）；embedding / 预测头 / mHC 静态 bias 与门控 / 全部 RMSNorm 仍 **AdamW**。
- Nesterov + weight decay；更新 RMS 重标定以复用 AdamW LR。
- **Hybrid Newton-Schulz**：共 10 步——前 8 步系数 (3.4445, −4.7750, 2.0315)，后 2 步 (2, −1.5, 0.5)。
- 因 Q/KV RMSNorm 已抑 logit 爆炸 → **不用** QK-Clip。

---

## 四、Infra 与 V4 产品级 KV 解（辅；≠ [[KV缓存量化与压缩]] 通史）

> 本节只录本 PDF **产品/部署解**。量化误差轴、通史 taxonomy → **[[KV缓存量化与压缩]]**。CED/Bounded Replay → **[[DeepSeekV41Flash深读]]**。

### 4.1 训练 / 核侧摘要（§3.1–3.4；跟读）

| 主题 | 要点 |
|---|---|
| EP 细粒度重叠 | Dispatch/Combine 与 Linear1/2 融为单管线；专家 **wave** 调度；Flash 配置理论加速示意最高约 **1.92×**（Fig 5）；实测相对强非融合基线推理 **1.50–1.73×**，RL rollout 等至 **1.96×**；开源 MegaMoE / DeepGEMM PR |
| TileLang | 大量融合核 DSL（§3.2） |
| 批不变 / 确定性核 | 训推 bitwise 可复现（§3.3） |
| Muon 实现 | hybrid ZeRO 等（§3.4.1） |
| mHC 实现 | 重算 + 融合核控成本（§3.4.2） |
| Contextual parallelism | 压缩注意两阶段上下文并行（§3.4.3） |
| Autograd | tensor-level checkpoint（§3.4.4） |

### 4.2 KV Cache 结构与磁盘策略（§3.5；本卡「产品解」主段）

**异构条目：** CSA main / CSA indexer / HCA / SWA / 未满压缩块的 uncompressed tail —— 尺寸与更新规则各异，打破经典 PagedAttention「全层统一页」假设。

**两池布局（Fig 6）：**

1. **Classical KV cache：** CSA/HCA 压缩条目；每块覆盖 $\mathrm{lcm}(m,m')$ 原始 token → $k_1=\mathrm{lcm}/m$ CSA 条目、$k_2=\mathrm{lcm}/m'$ HCA 条目。
2. **State cache：** 每请求固定块；存最近 $n_{\mathrm{win}}$ 的 **SWA** + 尚未可压缩的尾状态。

**On-disk（§3.5.2）：**

| 对象 | 策略 |
|---|---|
| CSA/HCA 压缩 KV | **全部落盘**；命中前缀则复用至最后一个完整压缩块；**尾部未满块仍需重算**（未存 uncompressed） |
| SWA KV | 体积约压缩 CSA/HCA 的 **8×**；三选一权衡：**(1) Full SWA Caching**（零重算，写放大差）；**(2) Periodic Checkpointing**（每 $p$ token 存末窗，可调存算）；**(3) Zero SWA Caching**（不存 SWA；凭已缓存 CSA/HCA 重放末 $n_{\mathrm{win}}\cdot L$ token 重建） |

> [[DeepSeekV41Flash深读]] 后续把 Zero/Exact replay 成本与 **SWA Bounded Replay** 写成 V4.1 部署折中——**本卡只立 V4 三策略菜单，不展开 V4.1 近似 replay 全文。**

### 4.3 后训练期 FP4 QAT（§5.2.1；产品解，非通史）

- **对象：** (1) MoE **expert 权重**；(2) CSA indexer 的 **QK 路径**（激活缓存/乘全 FP4）；另将 index scores FP32→BF16，top-$k$ selector **2×**，KV 条目 recall **99.7%**。
- Expert：FP32 master → FP4 → 无损反量化回 **FP8** 计算（E4M3 动态范围论证）；反传 STE。
- **≠** [[DeepSeekV41Flash深读]] 的 **main KV FP4**（本 PDF 主 KV 仍是 RoPE-BF16 + 其余 FP8 叙事）。

---

## 五、预训练要点（§4）

### 5.1 数据（§4.1）

- 在 V3 语料上加多样/长文；滤批量模板；中期掺 **agentic** 代码数据；加强多语长尾；强调长文档（论文/技术报告）。
- **>32T** tokens；词表仍 **128K**（少量特殊 token）；继承 token-splitting / FIM；文档打包减截断；**sample-level attention mask**（相对 V3 差分）。

### 5.2 训练日程（§4.2.2）

| 项 | Flash | Pro |
|---|---|---|
| Tokens | **32T** | **33T** |
| 峰值 batch | **75.5M** tokens | **94.4M** |
| 峰值 / 末 LR | $2.7\times10^{-4}$ → $2.7\times10^{-5}$ | $2.0\times10^{-4}$ → $2.0\times10^{-5}$ |
| 序列 | 4K→16K→64K→**1M** | 同 |
| 稀疏引入 | 前 **1T** dense warmup；64K 起 sparse；先短阶段暖 indexer | dense 阶段更长，其余同两阶段 |
| MTP loss 权重 | 主程 0.3；LR decay 起 0.1 | 同 |
| Muon | momentum 0.95；update RMS rescale **0.18** | 同 |

### 5.3 稳定性两招（§4.2.3）

1. **Anticipatory Routing：** 特征用 $\theta_t$，路由索引用历史 $\theta_{t-\Delta t}$；预取数据预计算路由；额外 wall-clock ≈ **20%**；尖峰时自动短回滚并临时启用，之后退回标准训。
2. **SwiGLU Clamping：** 线性支路 $[-10,10]$，gate 上界 **10**。

### 5.4 Base 评测摘录（Table 1；内部统一框架）

| 项 | V3.2-Base | **V4-Flash-Base** | **V4-Pro-Base** |
|---|---:|---:|---:|
| Activated / Total | 37B / 671B | **13B / 284B** | **49B / 1.6T** |
| MMLU-Pro (EM) | 65.5 | **68.3** | **73.5** |
| Simple-QA verified | 28.3 | 30.1 | **55.2** |
| SuperGPQA | 45.0 | 46.5 | **53.9** |
| HumanEval Pass@1 | 62.8 | **69.5** | **76.8** |
| LongBench-V2 | 40.2 | **44.7** | **51.5** |

作者口径：Flash-Base 以更小激活/总参在多数榜超 V3.2-Base；Pro-Base 在知识/长文等再抬一档。

---

## 六、后训练与评测字段（辅）

### 6.1 管线（§5.1）

- 对标 V3.2，但 **混合 RL 合并阶段整体换成多教师 OPD**（式 29，reverse KL；**full-vocabulary** logits，非 token 级优势估计）。
- 域专家：SFT → **GRPO**（超参对齐既有工作）；领域含数学/代码/agent/指令等；合并时 **>10** 教师。
- **三档 effort**（Table 2）：Non-think / Think High / Think Max；Max 注入系统提示（Table 3）。
- **GRM：** 难验证任务用 rubric + Generative Reward Model，并对 GRM 自身做 RL（actor 兼任评判）。
- **工具 schema：** `<|DSML|…>` XML 风格（Table 4）；thinking 模式须先完整 `<think>` 再调工具。
- **Interleaved thinking（相对 V3.2）：** 工具场景下 **跨用户轮次保留全部思维**；普通对话仍在新用户消息时丢弃旧思维（Fig 7）。
- **Quick Instruction：** 专用特殊 token 复用已有 KV 做搜否/标题/query/权威性等，砍冗余 prefill（Table 5）。

### 6.2 后训练主表摘录（Table 6；V4-Pro-**Max**）

| Benchmark | Opus-4.6 Max | GPT-5.4 xHigh | Gemini-3.1-Pro High | K2.6 Thinking | GLM-5.1 Thinking | **DS-V4-Pro Max** |
|---|---:|---:|---:|---:|---:|---:|
| SimpleQA-Verified | 46.2 | 45.3 | 75.6 | 36.9 | 38.1 | **57.9** |
| GPQA Diamond | 91.3 | 93.0 | 94.3 | 90.5 | 86.2 | **90.1** |
| HLE | 40.0 | 39.8 | 44.4 | 36.4 | 34.7 | **37.7** |
| LiveCodeBench | 88.8 | — | 91.7 | 89.6 | — | **93.5** |
| Codeforces Rating | — | 3168 | 3052 | — | — | **3206** |
| Apex Shortlist | 85.9 | 78.1 | 89.1 | 75.5 | 72.4 | **90.2** |
| MRCR 1M | 92.9 | — | 76.3 | — | — | **83.5** |
| CorpusQA 1M | 71.7 | — | 53.8 | — | — | **62.0** |
| Terminal Bench 2.0 | 65.4 | 75.1 | 68.5 | 66.7 | 63.5 | **67.9** |
| SWE Verified | 80.8 | — | 80.6 | 80.2 | — | **80.6** |
| Toolathlon | 47.2 | 54.6 | 48.8 | 50.0 | 40.7 | **51.8** |

**Flash vs Pro 努力档（Table 7 摘）：** Max 抬最难任务；知识缺口主要在 Flash 参数规模；推理上 Flash-Max 可逼近/超过前代开源强档；agent 上 Flash 在 Terminal Bench 等仍落后 Pro。

**作者自承差距（§1 / §5.3 / §6）：** 知识仍落后 Gemini-3.1-Pro；推理约落后前沿闭源 **3–6 个月**；agent 开源并列、闭源仍略强；内部 R&D coding（Table 8）Pro-Max Pass **67%** vs Opus 4.5 **70%** / Opus 4.6 Thinking **80%**。

### 6.3 局限与未来（§6）

1. 为冲长文效率，架构偏复杂；未来要「蒸馏到本质」。
2. Anticipatory Routing / SwiGLU Clamping **机理未透**。
3. 继续探 embedding 稀疏、低延迟系统、长程多轮 agent、**多模态**、数据策展。

---

## 七、相对已入库笔记的增量边界

| 已有笔记 | 已覆盖（本卡不复述） | **本卡新增 / 加深** |
|---|---|---|
| **[[DeepSeekV3训练与MoE基建]]** | MLA/MoE/MTP 基座；14.8T；DualPipe；FP8 训推配方 | V4 MoE **仅差分+超参表**；MTP **保留同 V3**；mHC / Muon / CSA+HCA |
| **[[DeepSeekV32技术报告深读]]** | DSA 两阶段；GRPO 四件套；128K agent 合成 | CSA=「压缩 + DSA」；HCA；**OPD 取代混合 RL 合并**；1M 效率账 vs V3.2 |
| **[[DeepSeekV41Flash深读]] V4.1-Flash** | CED / CSA2 / FP4 main KV / SWA Bounded Replay | 本卡立 **V4 本体** CSA–HCA、三策略 on-disk SWA、异构 KV 布局；**不写** CED/CSA2 全文 |
| **[[KV缓存量化与压缩]] KV 量化通史** | 通史 / 误差轴 | 只录 V4：**RoPE-BF16+其余 FP8**、indexer FP4、expert FP4 QAT、磁盘三策略 |
| **[[混合专家架构]] / [[长上下文位置编码与系统侧]] / [[注意力效率族MQA到MLA]]** | MoE 史、长上下文通论、注意力效率通论 | 本代数：284B/13B、1.6T/49B、$m=4$/$m'=128$、1M 27%/10% 等 |
| **[[AI基础设施总览]] / B7** | Infra / 引擎选型通史 | MegaMoE、TileLang、contextual parallelism——点到为止 |

**一句话：**
V3/V3.2 卡讲清「基座与 DSA/RL」；[[DeepSeekV41Flash深读]] 讲清「在 V4 系上再压 KV 的 CED/CSA2/FP4/Bounded Replay」；**本卡讲清 V4 本体如何用 CSA+HCA+mHC+Muon 把百万窗做成可训可服的开源旗舰锚点**——并显式禁止把 V4.1 增量回贴到 V4。

---

## 八、待核实与引用

### 8.1 待核实（禁止当作已确认）

1. **CSA:HCA 精确层交错比 / 层类型表：** 正文只写「interleaved」+ 前层特例；细表需开源 inference 或后续 blog。
2. **Fig 1 右图逐点 FLOPs/KV 曲线：** 文本层给 1M 相对比例，无逐位置表。
3. **「相对 BF16 GQA8 ≈ 2% KV」** 的逐字段字节账：正文定性+比例，未给拆解表。
4. **Table 6/7 对照模型 API / scaffold：** 部分空缺因 API 繁忙；跨 scaffold 引用须标明设置（§5.3.1）。
5. **Terminal-Bench 2.0 Verified ≈72.0（Pro）：** 正文补充句；主表仍报原版 **67.9**。
6. **Preview vs 正式产品差异、HF 许可、定价、新闻站日期：** 以本 PDF 页眉 **2026-04-26** 与本地归档为准。
7. 文中外部型号（GPT-5.4、Gemini-3.1-Pro、Kimi-K2.6、GLM-5.1、Opus-4.6 等）为作者对比叙事；**本卡不核验其独立卡**。

### 8.2 引用

- DeepSeek-AI. *DeepSeek-V4: Towards Highly Efficient Million-Token Context Intelligence*. arXiv:**2606.19348v1** \[cs.CL\], **26 Apr 2026**.
 Abs：https://arxiv.org/abs/2606.19348
 PDF：https://arxiv.org/pdf/2606.19348
 HTML：https://arxiv.org/html/2606.19348
 本地：`https://arxiv.org/abs/2606.19348`
 （2026-09-22 CST / Asia/Shanghai）
 权重集合：https://huggingface.co/collections/deepseek-ai/deepseek-v4
 推理参考：https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/tree/main/inference

### 8.3 关联笔记

- [[DeepSeekV41Flash深读]] DeepSeek-V4.1-Flash：模型与技术报告/厂商报告/DeepSeekV41Flash深读.md（增量卡；对照基线即本 TR）
- [[DeepSeekV3训练与MoE基建]]：模型与技术报告/厂商报告/DeepSeekV3训练与MoE基建.md
- [[DeepSeekV32技术报告深读]]：模型与技术报告/厂商报告/DeepSeekV32技术报告深读.md
- [[KV缓存量化与压缩]] KV 量化通史：推理与基础设施/KvQuant/KV缓存量化与压缩.md（通史；本卡只录产品解）
- [[混合专家架构]] / [[长上下文位置编码与系统侧]] / [[注意力效率族MQA到MLA]] / [[AI基础设施总览]] / [[智能体工具与长程任务]]：MoE、长上下文、注意力效率、Infra、agent
- [[MOC_模型与技术报告]]

## 相关笔记

- [[测试时训练|Test-Time Training]]
- [[潜空间推理Coconut|Coconut]]
- [[审慎对齐与断路器|Deliberative / Circuit Breakers]]
- [[DeepSeekV4技术报告深读|DeepSeek-V4]]

