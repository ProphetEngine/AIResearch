---
title: "KV 新方法：DuoAttention（头分工）+ KVzip（query-agnostic 压缩）"
topic: DuoAttention与KVzip
date: 2026-09-22
lines: [架构思想, 显存/延迟—精度字段]
status: archived
sources:
 - https://arxiv.org/abs/2410.10819
 - https://arxiv.org/abs/2505.23416
arxiv: ["2410.10819", "2505.23416"]
related: ["KV缓存量化与压缩", "检索式注意力", "长上下文位置编码与系统侧"]
archived: 2026-09-22
---

# KV 新方法：DuoAttention（头分工）+ KVzip（query-agnostic 压缩）

> **定位**：**P1 Infra**——相对 **[[KV缓存量化与压缩]]**（KV 低比特量化）与 **[[检索式注意力]]**（检索式注意力近似全注意力）补一条近窗横切：**头级分工（retrieval vs streaming）** 与 **与查询无关、可跨 query 复用的 KV 驱逐**。主锚两篇一手 PDF：**DuoAttention**（2410.10819）与 **KVzip**（2505.23416）。
> **攻坚线**：**架构思想（主）**——谁必须全 KV、谁可 sink+近窗 / 谁可按重构分数驱逐；**显存 / 延迟—精度字段（辅）**——NIAH、LongBench、SCBench 多 query、A100 上的 decode/prefill 数字。
> **硬划界（禁止重写）**：
> - **≠ [[KV缓存量化与压缩]]**：不写 K/V 非对称量化、残差窗、outlier 比特轴；两文均称量化可叠加，本篇只录「组合后容量」一句。
> - **≠ [[检索式注意力]]**：不写 KV 向量 ANNS / 句级 token 缓存；本篇是 **头分工** 与 **prefill 期 query-agnostic 驱逐**，不是 decode 期检索近似。
> - **≠ [[长上下文位置编码与系统侧]]**：不重写 YaRN / PagedAttention / vLLM 调度通史。
> - **SnapKV / PyramidKV / H2O / StreamingLLM / TOVA / FastGen**：仅作文内基线槽，**不另开**方法课。
> **禁止编造**：公式骨架、表数字、倍率一律取自官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息与谱系抓手

| 代号 | 标题（封面） | arXiv / 页眉 | 官方 PDF | 页数 | 在本轴中的角色 |
|---|---|---|---|---:|---|
| **DuoAttention** | *DuoAttention: Efficient Long-Context LLM Inference with Retrieval and Streaming Heads*（Xiao, Tang, Zuo, Guo, Yang, Tang, Fu, Han；MIT / 清华 / 交大 / Edinburgh / NVIDIA） | **2410.10819v1** \[cs.CL\] **14 Oct 2024** | `https://arxiv.org/abs/2410.10819` | 20 | **主文 A**：**头级**二分——Retrieval Heads 全 KV；Streaming Heads 仅 sink + recent（常数长） |
| **KVzip** | *KVzip: Query-Agnostic KV Cache Compression with Context Reconstruction*（Kim, Kim, Kwon, Lee, Yun, Song；SNU / Neural Processing Research Center / NAVER AI Lab） | **2505.23416v2** \[cs.DB\] **30 Sep 2025**；NeurIPS 2025 | `https://arxiv.org/abs/2505.23416` | 22 | **主文 B**：**query-agnostic** 按「上下文重构」最大交叉注意力打分，驱逐低分 KV；一次压缩、多 query 复用 |

**代码（封面 / 摘要）：** DuoAttention → https://github.com/mit-han-lab/duo-attention ；KVzip → https://github.com/snu-mllab/KVzip

**一句话谱系（跟读枢纽）：**

| 轴 | Full KV | DuoAttention | KVzip |
|---|---|---|---|
| **压缩粒度** | 无 | **头（KV head / GQA 组）**：二值门控 | **KV pair**（可聚合为 **head-level**） |
| **何时决定** | — | 部署前：合成 passkey 上优化门控 $\alpha$，再按 $\tau$ 二值化 | Prefill 后（或模型级一次）：用「Repeat previous context」重构前向打分 |
| **相对未来 query** | 全保留 | Streaming 头对 query **无条件**常数窗；Retrieval 头全保留 | **刻意 query-agnostic**：压缩一次，跨多样 query 复用 |
| **相对量化 / 检索** | — | 文称与 8-bit 权 + 4-bit KV **正交可叠** | 文称与 QServe 4-bit KV、与 DuoAttention 式头级驱逐 **可叠 / 可替换打分** |
| **训练** | — | 仅训 **门控**（模型权重冻结）；约 2000 step | **training-free**（前向打分 + 驱逐） |

**跟读口诀：** DuoAttention =「**少数头全记住，多数头只看 sink+近窗**」；KVzip =「**不问你明天问什么，先按能不能复述上下文来裁剪 KV**」。二者都落在 **KV 选择 / 驱逐**，不是比特量化（[[KV缓存量化与压缩]]），也不是 decode 期向量检索（[[检索式注意力]]）。

---

## 二、问题立轴：为何还要「头分工」与「query-agnostic」

据 DuoAttention §1 与 KVzip §1–§2.2：

1. **线性 KV + 二次 prefill**：DuoAttention 例——Llama-3-8B FP16、**1M** token → KV 至少约 **137 GB**，超单卡 80GB；prefill 延迟随长度平方涨、decode 随 KV 线性涨。
2. **统一剪 KV 伤长上下文**：H2O / StreamingLLM / TOVA / FastGen 等在 NIAH 上易丢 needle（DuoAttention Fig.6 叙事）；StreamingLLM 式常数窗省显存但 **有效记忆困在 sink+近窗**。
3. **头功能不匀（DuoAttention）**：少数 **Retrieval Heads** 会跨距对准相关 token；多数 **Streaming Heads** 主要看初始 sink + 近邻——剪后者中间段对 passkey 几乎无伤，剪前者则崩（Fig.1 右）。
4. **多 query 场景下 query-aware 驱逐失效（KVzip）**：SnapKV / PyramidKV 用「当前 query 尾窗」打分——单 query 好看；**复用**第一次压缩后的 cache 答后续 query 则大掉（Fig.2：SQuAD 上 SnapKV-reuse vs KVzip）。企业「文档预计算 KV / 个性化对话历史」需要 **一次压缩、多次查询**。

本篇只钉上述两条近窗方法；量化见 **[[KV缓存量化与压缩]]**，检索近似见 **[[检索式注意力]]**，位置外推与分页调度见 **[[长上下文位置编码与系统侧]]**。

---

## 三、站 1：DuoAttention — Retrieval / Streaming 头分工（2410.10819）

### 3.1 架构意图（主）

总体（§2 / Fig.2）：

1. **识别期**：为每个 KV head 设可训门控 $\alpha_{i,j}\in[0,1]$（初值 1）；模型权重 **冻结**。前向把
 $$
 \mathrm{attn}_{i,j}=\alpha_{i,j}\cdot\mathrm{full\_attn}+(1-\alpha_{i,j})\cdot\mathrm{streaming\_attn}
 $$
 其中 `full` 用因果 mask，`streaming` 用 $\Lambda$ 型 mask（只看 sink + recent）。
2. **损失（式 1–3）**：在合成数据末尾 passkey token 上对末层隐状态做 **L2 distillation**（相对全注意力教师）+ $\lambda\|\alpha\|_1$（$\lambda=0.05$）。
3. **部署期**：按分位数阈值 $\tau$ 二值化——$\alpha>\tau$ → Retrieval（全 KV）；否则 Streaming（常数长 KV）。
4. **工程**：按头重排 Q/K/V 投影通道，使两类头在层内连续，便于切片而非 scatter；每层两套 cache。

**与「只看注意力图找 retrieval head」的差异（§2.2）：** 定义改为「**限制为 sink+recent 时是否显著改变输出**」——直接量端到端偏差，并覆盖 value 角色与跨层分布差异；消融（Fig.13）称优于 attention profiling / 纯语言模型 loss。

### 3.2 合成数据与超参（跟读）

| 项 | 文内设定（§2.2 / §3.1） |
|---|---|
| 数据 | BookSum 长文中嵌入 **10** 条、各 **32 word** 的随机 passkey，末尾要求全部召回 |
| 识别窗 | sink **128** + recent **256**；长度从 1K 扫到模型上限的 50 个区间；passkey 随机插入 |
| 优化 | AdamW；lr 0.02（前后 400 step warm/cool 夹到 0.002）；**2000** step；8×A100；可训参数仅 $N\times H$ 量级 |
| 部署常用比 | Llama-2-7B **MHA → 25%** retrieval；Llama-3-8B **GQA → 50%** retrieval（Fig.4：MHA 可压 retrieval 比例更低） |
| Streaming 部署窗 | 评测常用 sink **64** + recent **256**；消融解为 sink **16** + recent **64** 已近平台（Fig.13-3） |

### 3.3 Prefill / Decode 行为（§2.3 / Fig.5）

- **Decode**：Retrieval 头追加全部新 KV；Streaming 头只保留 sink + 滑动 recent → **O(1)** 显存。
- **Chunked prefill**：Streaming 头每算完一块立刻剪到 sink+recent；复杂度从 $O(L^2)$ 时间 / $O(L)$ 显存 → $O(LK)$ / $O(K)$（$K$=chunk size），且可用 FlashAttention-2，无需特制核。

### 3.4 精度与效率字段（辅）

**NIAH（Fig.6）：** 同预算下 H2O / StreamingLLM / TOVA / FastGen 在多种深度失败；DuoAttention 在 MHA **25%** / GQA **50%** full-attention 比例下接近 Full。FastGen 因 profiling 二次图在超长上 OOM（Llama-2 测到 ~24K，Llama-3 ~32K）。

**LongBench（附录 Table 3 / 4，Avg.）：**

| 模型 | Full | Duo（预算） | H2O | SLLM | TOVA |
|---|---:|---:|---:|---:|---:|
| Llama-3-8B-1048K | 40.08 | **40.21（50%）** | 35.76 | 32.26 | 35.55 |
| Llama-2-7B-32K | 37.52 | **34.49（25%）** | 26.84 | 27.80 | 29.78 |

相对 FastGen 子集（Table 5/6）：Llama-3 上 Duo 50% Avg **40.01** vs FastGen(>50%) **32.82**；Llama-2 上 Duo 25% **32.81** vs FastGen(>25%) **19.01**。

**短上下文（Fig.8 / Table 1）：** Llama-3-70B、50% 预算——DuoAttn MMLU **79.35%** / MBPP **47.09%** / MT-Bench **9.14**，接近 Full（79.38 / 47.85 / 8.93），明显优于 H2O/TOVA/SLLM 在 MBPP、MT-Bench 上的掉点。

**效率（§3.4 / Fig.9–12，单卡 A100，BF16 默认）：**

| 指标 | MHA（Llama-2-7B，25% retrieval） | GQA（Llama-3-8B，50%） |
|---|---|---|
| Decode 显存最多约 | **2.55×** 降 | **1.67×** 降 |
| Decode 延迟最多约 | **2.18×** 升速 | **1.50×** 升速 |
| Prefill 延迟最多约 | **1.73×** | **1.63×** |
| Prefill 显存最多约 | **2.38×** 降 | **1.53×** 降 |

**与量化叠（Fig.12）：** DuoAttention + QServe **W8 / KV4** → Llama-3-8B 单卡 A100-80G 可测到约 **3.30M** context token，文称相对朴素 Full BF16 约 **6.4×** 容量；**量化细节回指 [[KV缓存量化与压缩]]，本篇不展开**。

---

## 四、站 2：KVzip — 上下文重构驱动的 query-agnostic 驱逐（2505.23416）

### 4.1 架构意图（主）

目标（式 1）：求 $\mathrm{KV}_{c,\mathrm{evicted}}\subseteq\mathrm{KV}_c$，使对 **任意** 未来 $q$ 有
$f_{\mathrm{LM}}(q\mid\mathrm{KV}_{c,\mathrm{evicted}})\approx f_{\mathrm{LM}}(q\mid\mathrm{KV}_c)$。

**直觉（§3.1 / Fig.3–4）：** 把 Transformer 看成「上下文 → KV」的编码器；若裁剪后的 KV 仍能让模型按提示 **复述原文**，则信息充分。实践上不必每次真的重建全 cache——用重构前向得到的 **最大交叉注意力** 给每个 KV pair 打分，再驱逐低分者。

**打分（§3.2 式 2）：** 构造输入 = `Repeat` 提示 + 原文（teacher-forced 一次前向）；对每个 KV head 取
$$
S_{l,h}=\max_{g,i}\bar A_{l,h}[g,i]
$$
（对 grouped query 与输入 query 维取 max）。文称该「最大交叉注意力」相对 prefill 自注意力更稀疏（Fig.5），且与 QA / 摘要 / 推理等高分 KV **重叠**，而两道不同 QA 之间则呈 query-特异分叉（Fig.6）——支撑 **query-agnostic**。

### 4.2 Chunked scoring：把 $O(n_c^2)$ 变成 $O(m n_c)$（§3.4）

直接对整段做 Softmax-后沿 query 维 max，与 FlashAttention 的 block 融合不兼容。做法：

1. 将上下文切成固定块 $m$（文设 **$m=2\mathrm{K}$**，称跨模型/任务不敏感）。
2. 每块与 repeat 提示拼接前向；只 subsample 该块对应的 key，得 $n_{\mathrm{in}}\times(m+n_{\mathrm{in}})$ 注意力，再 max。
3. 总复杂度约 $O(m n_c)$，峰值额外显存 $O(m^2)$。
4. 块 $i\ge 2$ 的提示形如：`Repeat the previous context starting with ⟨前一块末 8 token⟩:`（Alg.1）。

**开销（Fig.8，LLaMA3.1-8B，124K，A100 FP16）：** 压缩期注意力算力约等于 **再付一次量级的 prefill**（文称约 2× prefill 注意力代价）；之后 decode 侧注意力延迟与 KV 显存随预算比下降。压缩 **每上下文一次**（或 head-level 下每模型一次）。

### 4.3 两种部署形态

| 形态 | 做法 | 何时省 |
|---|---|---|
| **Context-dependent** | 每个上下文 prefill 后打分、按 top-$r\%$（非均匀跨头预算）驱逐 | 多 query 复用同一文档 KV 时摊销压缩成本 |
| **Context-independent** | 用一篇书样例（文：SCBench En.QA，88K）聚合 $\max$ 得 **静态 head 分数**，再套 DuoAttention 式头级驱逐 | 部署后 **零** 压缩开销；压缩率通常更保守 |

系统提示 KV **不驱逐**（§4.1）。文亦支持均匀头预算（附录 C.4）；主文默认非均匀。

### 4.4 精度与效率字段（辅）

**评测协议（§4.1）：** 统一走 Fig.1c 的 **query-agnostic** 框架——先无 query 地压缩上下文 KV，再答多/单 query。基线含 H2O、SnapKV、PyramidKV；头级对照 DuoAttention 官方 head score。模型含 Qwen2.5-7B/14B-1M、LLaMA3.1-8B、Gemma3-12B（仅压 **global** 层）、以及 QServe **W8A8KV4**。上下文最长约 **170K**（Qwen tokenizer 叙事）。

**任务泛化（Fig.9，Qwen2.5-7B-1M）：**

- **检索密**：NIAH / Retr.KV / Code.RepoQA 等——KVzip 在约 **30%** 预算仍近满血；SnapKV/PyramidKV/H2O 在 **90%** 保留时已可见垮（多 query 复用设定）。
- **语境理解**：SQuAD、GSM8K、En.QA 等——文称可压到约 **30%** 仍近无损。
- **高冗余**：En.Summary / ICL 等——可到约 **10%**；文猜测驱逐减轻 attention distraction。

**跨模型（Fig.10）：** 12 集平均相对满缓存表现，KVzip 曲线高于三基线；Gemma3 只驱逐 global 层（global:SWA≈1:5）。

**量化叠（Fig.10 右 / §4.2）：** LLaMA3-8B-W8A8KV4，124K 时 16-bit KV 约 **16.3 GB**；4-bit + **70% 驱逐** → 约 **1.2 GB**，文称掉点可忽略——**比特轴细节回指 [[KV缓存量化与压缩]]**。

**vs DuoAttention 头级（Fig.11）：** 同用 head-level eviction；KVzip 用自然语言书做重构打分（数次前向，约 **1 分钟**级），DuoAttention 官方优化「数小时 / 8-GPU」级；文称在 12 集平均相对表现上 KVzip（head）更优。最低比约 **0.4**（DuoAttention 下限叙事约 0.32）。

**摘要级效率宣称（摘要 / 结论）：** 解码侧 FlashAttention 延迟约 **2×** 改善；摘要另写 KV 体积可至约 **394×** 量级压缩——**正文实验主叙事是「驱逐至约 30% 预算（即约 70% 驱逐）近无损」**；跟读时以 Fig.8–10 曲线与结论段 70%/2× 为准，不把摘要倍率外推成「任意任务统一 394×」。

**行为附录（Table 1）：** DecodingTrust 隐私例上，满 KV 拒答电话号码，40% 压缩后却吐出号码——文归因于优先保留「可重构」KV、丢掉对齐相关 KV；作现象记录，**不**升格为产品建议。

---

## 五、两站对照与仓库划界

| 问题 | DuoAttention | KVzip |
|---|---|---|
| 裁什么 | **整头** 二选一策略 | **token×head** 的 KV pair（可聚合成头） |
| 信息准则 | 合成 passkey 上输出蒸馏 + L1 | 自然语言 **复述** 时的 max 交叉注意力 |
| Prefill 成本 | Streaming 头线性/常数；识别一次性 | 每上下文约「再付 ~1× prefill」打分（或模型级一次） |
| Decode | Retrieval 全长 + Streaming 常数窗 | 变长稀疏 KV + FlashAttention |
| 多 query 复用 | Streaming 侧天然 query-无关；Retrieval 侧全保留 | **设计目标**即跨 query 复用 |
| 文内互指 | — | 可替换 DuoAttention 的 head-score 优化 |

| 已入库 | 本卡只取接口 | 本卡不写 |
|---|---|---|
| **[[KV缓存量化与压缩]]** | 「可与 4-bit KV / QServe 叠」一句 | KIVI/KVQuant 误差轴、残差窗 |
| **[[检索式注意力]]** | 「都是减 KV 负担」一句对照 | ANNS / InfiniRetri 句缓存 |
| **[[长上下文位置编码与系统侧]]** | chunked prefill / 长窗存在 | YaRN、PagedAttention 通史 |
| **SnapKV 等** | Fig 曲线基线 | 独立方法深读 |

---

## 六、可跟读结论（禁外推未写实验）

1. **头不匀是 DuoAttention 的第一性原理**：先用优化门控找出「剪掉会改输出」的头，再只给它们全 KV——比统一 Streaming / 统一 profiling 更能保 NIAH 与 LongBench。
2. **GQA 比 MHA 更难压 retrieval 比例**：文内默认 50% vs 25%，Fig.4 与效率上限（1.67× vs 2.55× 显存）一致——跟读时勿把 MHA 倍率直接套到 GQA 服务。
3. **Query-aware 驱逐 ≠ 可缓存资产**：SnapKV 路线在「每 query 重 prefill」时好看，在「压缩一次答多问」时垮；KVzip 的产品假设是 **离线/共享上下文 KV**。
4. **重构分数是跨任务代理，不是任务分数本身**：Fig.6 显示与 QA/推理重叠、与另一 QA 分叉——解释「为何不问未来 q 也能泛化」，也解释「不能指望保留集等于某一 query 的 top-k」。
5. **Serving 含义分流**：要在 **固定头策略**下同时砍 decode 与 prefill、并与量化叠出百万级窗 → 看 DuoAttention；要在 **预计算文档/会话 KV** 上多 query 复用、并可几分钟内替代头打分 → 看 KVzip。二者可叠（头级 + pair 级），**不可混成同一张系统图**。

---

## 七、来源与抽取记录

| 项 | 内容 |
|---|---|
| PDF | `https://arxiv.org/abs/2410.10819`（20 页，~6.0MB）；`https://arxiv.org/abs/2505.23416`（22 页，~0.74MB） |
| 文本抽取 | （1684 行）、`kvzip-full.txt`（1829 行）；同步 · ； |
| 时间戳 | 下载与**2026-09-22 CST** |
| 未做 | 未复现实验；未读图估未列表的精确曲线点；未引入第三篇综述充数；未展开 [[KV缓存量化与压缩]] 量化公式 |

## 相关笔记

- [[DiffusionForcing族|Diffusion Forcing]]
- [[WorfBench工作流基准|WorfBench]]
- [[合成对齐数据Magpie|Magpie / ActiveUltraFeedback]]
- [[EntMTP熵引导投机解码|EntMTP]]
- [[DuoAttention与KVzip|DuoAttention / KVZip]]

