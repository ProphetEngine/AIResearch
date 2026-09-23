---
title: "低资源区域专报：SEA-LION-v4.8（≠ B9 通史）"
topic: SEA-LION低资源区域模型
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.18310 # 2.2M / 19p；≪10MB → 官方 HTTPS 外链
aux:
 - https://sea-lion.ai/
 - https://sea-lion.ai/blog/uplifting-ai-in-southeast-asia-sea-announcing-nemotron-sea-lion-v4-8-in-collaboration-with-nvidia/
 - https://leaderboard.sea-lion.ai/
 - https://huggingface.co/collections/aisingapore/sea-lion-v48-6aaa084b80451baa08e73db0
arxiv: ["2609.18310"]
related: ["多语言与跨语种", "NemotronCC数据策展", "Nemotron3Ultra"]
hf_index_prefix: "aisingapore/Nemotron-SEA-LION-v4.8-*"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 低资源区域专报：SEA-LION-v4.8（≠ B9 通史）

> **定位**：SEA-LION低资源区域模型 **P1 低资源区域专报**——立 **东南亚（SEA）区域适配栈**：在 NVIDIA Nemotron 3 开源基座上做 **继续预训练（CPT）+ SFT / 在线 on-policy 蒸馏（OPD）后训练**，并以更新版 **SEA-HELM** 做区域评测。主文：AI Singapore *SEA-LION-v4.8: A Technical Report*（arXiv:**2609.18310**v3，**18 Sep 2026**）。
> **攻坚线**：**架构思想（区域 CPT / 蒸馏接口，主）** + **评测字段（SEA-HELM 语种分 / 能力分，辅）**。
> **硬划界（开篇钉死）**：
> - **≠ B9**：禁止重写 XLM-R / BLOOM / 旗舰「语种覆盖 × 配比」通史；本卡只写 **SEA 区域落地配方与 SEA-HELM 数字**，多语通史仅作动机一句。
> - **≠ [[NemotronCC数据策展]]**：禁止重写 **Nemotron-CC 语料清洗篇**；本卡 CPT 混合只列文内 Table 2 组件与权重，不展开通用网页过滤管线。
> - **≠ [[Nemotron3Ultra]]**：禁止把本卡写成 **Nemotron 3 Ultra 基座旗舰全文**；基座 **Mamba2–Transformer / LatentMoE 混合 MoE** 只交叉 **一句**，主轴停在 **区域 CPT + OPD + SEA-HELM**。
> **禁止编造**：主张、token 量、表数字一律锚定官方 PDF（2026-09-22 CST）；辅站 / HF 仅作入口索引，**禁下权重**。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题 / 版本 | 标识 | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主文** | *SEA-LION-v4.8: A Technical Report*（AI Products Pillar, AI Singapore） | arXiv:**2609.18310**v3 \[cs.CL\] **18 Sep 2026** | `https://arxiv.org/abs/2609.18310` | **2.2M**（2,270,331 B ≈ **2.17MiB**） | **19** letter | |
| **辅·产品站** | SEA-LION 官网（系列定位 / SEA-HELM / SEA-Guard 入口） | https://sea-lion.ai/ | — | — | — | WebFetch 2026-09-22 |
| **辅·发布博文** | *Uplifting AI in Southeast Asia… Nemotron-SEA-LION-v4.8*（AISG，**2026-09-18**） | https://sea-lion.ai/blog/uplifting-ai-in-southeast-asia-sea-announcing-nemotron-sea-lion-v4-8-in-collaboration-with-nvidia/ | — | — | — | 与 TR 数字交叉核验 |
| **辅·榜单** | SEA-HELM Leaderboard | https://leaderboard.sea-lion.ai/ | — | — | — | 文内 §6.1；Table 5 注明分数采集于 **2026-09-15**，live 可能变更 |

**体积判定（2026-09-22 CST，`ls -lh` / `stat` ）：** **2,270,331 B（2.17MiB）/ 19 页**，**远低于收紧后的 10MB 阈值** → **官方 HTTPS 外链**。**禁**入库模型权重 / 量化包 / 数据集。

**一手 PDF：** **有** — `curl` → 200； Title=`SEA-LION-v4.8: A Technical Report`。

### 1.1 Hugging Face 索引（禁下权重）

Collection：`aisingapore/sea-lion-v48-6aaa084b80451baa08e73db0` → https://huggingface.co/collections/aisingapore/sea-lion-v48-6aaa084b80451baa08e73db0

API 索引（`author=aisingapore&search=Nemotron-SEA-LION-v4.8`，2026-09-22；**仅列 ID，不下权重**）：

| HF ID | 角色（据 model card / TR Table 1） |
|---|---|
| `aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-Base` | CPT base（30B / 3B active） |
| `aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B` | 后训练 instruct |
| `aisingapore/Nemotron-SEA-LION-v4.8-30B-A3B-FP8` / `-NVFP4` / `-GGUF` | 量化 / 边缘部署变体（索引） |
| `aisingapore/Nemotron-SEA-LION-v4.8-120B-A12B-Base` | CPT base（120B / 12B active） |
| `aisingapore/Nemotron-SEA-LION-v4.8-120B-A12B` | 后训练 instruct |
| `aisingapore/Nemotron-SEA-LION-v4.8-120B-A12B-FP8` / `-NVFP4` / `-GGUF` | 量化变体（索引） |

文内 / card：许可证 **MIT**；联系 `sealion@aisingapore.org`。

**一句话抓手：** 不从零训基座——在 Nemotron 3 Nano/Super 上灌 **SEA 定向 CPT**（30B：**150B** tokens；120B：**33.5B** tokens），再用 **SFT ∪ 在线 OPD**（教师：Nemotron 3 Ultra 550B-A55B）把区域能力拧到 **SEA-HELM**；120B 总体 SEA 分 **49.30→63.44**，缅甸语 / 泰米尔涨幅最大。

---

## 二、议题边界：区域适配栈 ≠ 多语通史 ≠ 语料篇 ≠ 基座旗舰

### 2.1 相对相邻笔记只取接口

| 已入库 / 同波 | 本卡只取 | 本卡不写 |
|---|---|---|
| **B9** | 「多语覆盖不均、低资源脚本吃亏」动机一句；XLM-R curse / BLOOM ROOTS **不重写** | 编码器多语 MLM、ROOTS 语种表、旗舰配比旋钮通史 |
| **[[NemotronCC数据策展]]** | CPT 用到的 Nemotron 系 SFT/推理子集名可索引；清洗哲学不展开 | Nemotron-CC 过滤 / 去重 / 质量分类全文 |
| **[[Nemotron3Ultra]]** | 初始化自 Nemotron 3 Nano / Super；教师 Ultra 550B **作 OPD 信号源一句**；混合 MoE 架构名一句 | Ultra 训练配方、agentic 旗舰评测、LatentMoE 消融全文 |

### 2.2 本卡主轴 vs 禁区

| 写 | 不写 |
|---|---|
| 四卡发布：30B/120B × Base/Instruct；CPT 混合 Table 2；OPD+SFT 异步管线 Figure 5 / Table 4 | 从零预训练配方；Nemotron 3 Ultra 模型 TR |
| Tokenizer **保留原 Nemotron** 的效率瓶颈（Khmer/Lao/Tamil≈5×）；Filipino **未入 CPT** 的失败模式分化 | 词表扩张 / 新 tokenizer 训练实现细节（文内留作未来工作） |
| SEA-HELM 7 语 + 8 能力维；Table 5–7 点估计 | 把 SEA-Guard 产品线写成第二主轴；编造 live 榜未核分数 |

跟读口诀：**B9 问「多语权衡通史」；[[NemotronCC数据策展]] 问「通用语料怎么洗」；[[Nemotron3Ultra]] 问「Nemotron 3 旗舰怎么训」；本卡问「已有强基座如何 CPT+OPD 成 SEA 区域模型，并用 SEA-HELM 量出来」。**

---

## 三、发布家族与基座交叉（一句）

文内 Table 1 / §2.1 四卡：

| 模型 | 阶段 | 总参 / 激活 | 架构（文内名） | Context（Table 1） |
|---|---|---|---|---|
| `…-30B-A3B-Base` | CPT | 30B / 3B | Mamba2-Transformer Hybrid MoE | 128K |
| `…-30B-A3B` | Post | 同上 | 同上 | 128K |
| `…-120B-A12B-Base` | CPT | 120B / 12B | Mamba2-Attention Hybrid LatentMoE（含 MTP） | 128K |
| `…-120B-A12B` | Post | 同上 | 同上 | 128K |

**基座交叉一句（≠ [[Nemotron3Ultra]]）：** 30B 初始化自 `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-Base-BF16`，120B 初始化自 `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16`；二者均为 Nemotron 3 系 **Mamba2–Attention 混合 MoE**，本卡不展开 Ultra/LatentMoE 训练与消融。

注：§2.1 正文写 CPT 后仍保留基座最大上下文 **1M tokens**，脚注说明 **后训练阶段将 context 设为 128k**——与 Table 1「128K」列一致；跟读以「部署/评测窗口 128k、基座宣称 1M」区分。HF card 另写部署字段 → **本卡以 PDF 为准**，不把 card 数字回写进 TR。

---

## 四、区域 CPT：数据混合、配方与瓶颈（主轴）

### 4.1 设计目标（§3）

CPT 目标：**加强 SEA 语言表征**，同时 **保住** Nemotron 3 继承的推理 / 代码 / 通用能力。刻意少用「泛网页原文」，加重 **结构化、能力导向** 数据：QA、CoT/数理/科学推理、代码、双语平行。

| 规模 | Init | CPT tokens | 框架 | 峰值 LR | LR 日程 | seq | 硬件 | 时长（Table 3） |
|---|---|---|---|---|---|---|---|---|
| 30B-A3B | Nano Base | **150B** | Megatron Bridge | $3\times10^{-5}$ | WSD **省略最终 decay** | 8192 | 32×H200 | 114.23 h |
| 120B-A12B | Super Base | **33.5B** | NeMo AutoModel | $1\times10^{-5}$ | 同上 | 8192 | 32×H200 | 186.65 h |

共同：保留 **原 Nemotron tokenizer**；AdamW；global batch 1024；BF16。省略 final decay 的动机（§3.3）：避免 CPT 过度收敛，给后训练留塑性。

### 4.2 混合组成（Table 2 + Figure 2）

三大组（采样权重决定在 **150B** 语料中的相对贡献）：

1. **SEA-Instruct（高权）**：Indonesian / Malay / Burmese / Tamil / Vietnamese — 各 **weight 10**。
2. **Reasoning / Code**：Code、Math、Scientific reasoning、General reasoning/CoT — 各数据集 **2.5**；另加 Thai medical reasoning **2.5**。
3. **Parallel（SEA↔EN，双向交替）**：ID/KM/LO/MS/MY/TA/TH/VI/ZH — 各 **2**；BN/JV/SU — 各 **0.25**。

SEA 覆盖语种叙述（§3.1）：Balinese, Burmese, Indonesian, Javanese, Khmer, Lao, Malay, Sundanese, Tamil, Thai, Vietnamese 等；高权 instruct 集中在 MY/ID/MS/TA/VI。

博文补充的公开数据集名（辅，**非** PDF Table 2 全量）：如 `aisingapore/SEA-Instruct-2602`、若干 `nvidia/Nemotron-SFT-*`、平行/推理公开集等——跟读以 PDF 权重表为准，博文仅作命名索引。

### 4.3 Tokenizer 瓶颈与 Filipino 缺口（§3.2 / §3.4 / §8）

文内明确：**区域适配不能只当「数据 scaling」问题**。

- 保留原 tokenizer → Khmer / Lao / Tamil 相对「前代 SEA-LION tokenizer」约 **5×** token（§3.2）；fertility 差导致固定 context 内信息密度低。
- **Filipino 未进入当前 CPT 混合**：评测上的 TL 增益主要来自跨语迁移与通用多语能力，**非**菲律宾语定向 CPT。
- 失败模式分化：TA/MY = **有数据、被表示/切词卡住**；TL = **缺直接 CPT 覆盖**。未来工作：词表扩张 / tokenizer 适配 / 高质量菲律宾语料（文内未做）。

---

## 五、后训练：SFT ∪ 在线 OPD（区域接口）

### 5.1 数据流（§4.1）

- **离线 SFT**：`aisingapore/SEA-Instruct-2602` 子集；语种 ID/VI/TH/Filipino/Tamil/Tagalog/MS/MY + EN，**等比例**。
- **在线交互**：同一批 prompt 经环境–agent harness 产出轨迹；≈**3,000** 并发 agent、训练期 **≥100,000** sessions；agent **不含独立 LM**，一律打到「当前在训学生」。

### 5.2 管线五件套（Figure 5 / §4.2）

`environment-agent orchestrator` → `Conductor`（token-exact 捕获 + 训练库）→ `serving fleet`（改版 SGLang）→ `reward fleet`（教师 top-k 压缩二进制）→ `asynchronous trainer`（改版 AutoModel）。

关键机制（跟读，不写可复现攻击细节）：

- 学生 on-policy 生成 $\tau_t\sim p_{\theta_t}$ → 教师在 $\tau_t$ 上给监督 → reverse KL OPD → $\theta$ 更新后分布再变。
- 教师（两规模共用）：`RedHatAI/NVIDIA-Nemotron-3-Ultra-550B-A55B-FP8-dynamic`（**仅作蒸馏教师一句 → 详见 [[Nemotron3Ultra]]，本卡不展开 Ultra**）。
- 训练记录 staleness 窗 **≤32**（超窗 mask）；同 prompt 的 rollout 与 off-policy 参考答打包同 batch。
- 有效流：$D_{\mathrm{train}}=D_{\mathrm{SFT}}\cup D_{\mathrm{OPD}}$。
- 后训练后再与对应 Nemotron 参考权重 **merge**（30B：`nvidia/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-BF16`；120B：`nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16`）；步数 30B **1200** / 120B **1600**（§4.2）。

| 配置（Table 4） | 30B-A3B | 120B-A12B |
|---|---|---|
| 方法 | SFT + online OPD | 同左 |
| max seq | 128,000 | 128,000 |
| max LR | 1e-5 | 1e-5 |
| GBS | 24 | 24 |
| Train / Reward / Serve GPU | 16 / 48 / 8 | 48 / 48 / 16 |
| 时长 | 12 h | 24 h |

（Reward/Serve GPU 为初始化值，文内注可动态伸缩。）

---

## 六、评测字段：SEA-HELM（辅轴）

### 6.1 套件设定（§5）

- **SEA-HELM**（Susanto et al., 2025 Findings ACL；本版更新）：社区参与、尽量 **母语撰写 / 本地化**，避免纯机翻 translationese；任务提示用目标语；分数相对随机基线归一后分层聚合 → 公开榜 https://leaderboard.sea-lion.ai/ 。
- **语种（7）**：Filipino, Indonesian, Tamil, Thai, Vietnamese + 本版新增 **Malay、Burmese**。
- **增量维**：文化（SEA-NLI；Filipino 另 KALAHI 生成式）；知识（Global MMLU-Lite、Thai Exam）；语言诊断 LINDSEA（含生成式变体）；安全 **SEA-SafeguardBench**。
- **方法**：每模型 **8** 次独立运行（默认生成配置）取 prompt 均分；任务级 **2000** bootstrap → 95% CI（表中点估计；Table 5 注：采集 **2026-09-15**）。

### 6.2 语种总分（Table 5）

| Model | Size | SEA | MY | TL | ID | MS | TA | TH | VI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Nemotron 3 Nano | 30 | 46.89 | 3.23 | 55.53 | 65.36 | 58.00 | 22.50 | 62.90 | 60.72 |
| Nemotron 3.5 Lightning | 30 | **46.06** | 3.79 | 58.69 | 64.34 | 58.76 | 17.23 | 58.66 | 60.97 |
| **SEA-LION v4.8 30B** | 30 | **51.57** | **10.61** | **61.82** | **65.87** | **62.09** | **33.14** | 62.60 | **64.86** |
| Nemotron 3 Super | 120 | 49.30 | 4.98 | 66.92 | 70.78 | 68.66 | 21.83 | 56.61 | 55.31 |
| **SEA-LION v4.8 120B** | 120 | **63.44** | **31.35** | **71.01** | **73.10** | **73.25** | **56.35** | **68.66** | **70.36** |

**读表注意（禁混比）：**
- Abstract / Figure 1a 叙述 30B 总体 **46.06→51.57**（对 **Lightning**）；§6.1 正文写 **46.89→51.57**（对 **Nano**）。两基线同表均给出，跟读时标明对照对象。
- 120B：**49.30→63.44**（对 Super）无歧义。
- 最大相对跃升（120B）：**MY 4.98→31.35**；**TA 21.83→56.35**（与博文 6.3× / 2.6× 叙述一致）。
- 绝对水平仍不均：MY/TA 弱于 ID/MS/TL/TH/VI（§6.1 归因回切词效率）。

### 6.3 能力维摘要（Tables 6–7；八类）

八类：Cultural / Instruction Following / Knowledge / Multi-turn / NLG / NLR / NLU / Safety。

文内定性（§6.2，数字已在表）：

- **30B**：NLG、Instruction Following 面较宽；NLU 上 **Tamil 75.26** vs Nano **19.38** / Lightning **23.48** 跃升显著；Cultural/Knowledge 在 TL/ID/MS 等有增益，TH/VI 等处参考模型仍可更强。
- **120B**：Cultural、IF、Knowledge、NLR、NLU **更一致**；Cultural 七语全面提升（含 MY **0.00→37.68**）；NLU Tamil **17.89→80.04**，Burmese **2.25→43.46**。
- **Safety**：30B 在 TL/VI 等相对双基线有改善，TH 相对 Lightning 大涨；120B 在 MY/MS/TA/TH/VI 等有改善——**非**均匀碾压，文内 §8 承认能力维 trade-off。

### 6.4 Limitations（§8）对齐读

1. Tokenizer 低效（KM/LO/TA 等）。
2. CPT 无显式 Filipino。
3. 能力增益不均（IF/推理/NLU 最清晰；文化/生成/安全/知识/多轮更依赖语种）。
4. 评测仅 **7** 语，未覆盖区域全部语言多样性。

---

## 七、跟读清单与验收锚点

1. 本地体积：`ls -lh https://arxiv.org/abs/2609.18310` → **2.2M**（2,270,331 B）； → **19** 页；**≪10MB → 官方 HTTPS 外链**。
2. 开篇划界句可回链 Agenda [[SEA-LION低资源区域模型]]：「≠ B9；≠ [[NemotronCC数据策展]]；≠ [[Nemotron3Ultra]]——只写区域适配与评测，基座架构交叉一句」。
3. 主数字锚：CPT **150B / 33.5B**；SEA **51.57 / 63.44**；MY/TA 120B 分；教师 Ultra 仅作 OPD 交叉。
4. HF：十个 `Nemotron-SEA-LION-v4.8-*` ID **仅索引**；确认未 `huggingface-cli download` 权重。
5. 禁止把本卡扩写成 B9 多语通史、[[NemotronCC数据策展]] 语料篇或 [[Nemotron3Ultra]] Ultra 旗舰正文。

---

## 八、缺口回填（对照 Agenda）

Agenda [[SEA-LION低资源区域模型]]：「B9 写 XLM-R/BLOOM/旗舰语种配比通史。近窗 **SEA-LION-v4.8** 提供东南亚多语（含缅甸/泰米尔等）继续预训练 + SEA-HELM 评测的一手专报，可补『区域低资源落地栈』。划界 ≠B9；≠[[NemotronCC数据策展]]；≠[[Nemotron3Ultra]]。」

本卡交付：主 PDF 入库 + 抽取（体积 **2.17MiB ≪10MB**，建议二进制）；开篇硬划界；CPT/OPD 区域接口 + SEA-HELM Table 5–7；HF/官网索引；基座仅一句交叉。
