---
title: "开源前沿旗舰：Kimi K3 Technical Report（≠ Nemotron/OLMo/Coder-Next/DeepSeek-V4）"
topic: KimiK3技术报告
date: 2026-09-22
lines: [架构思想, AI Infra, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2607.24653 # 1.71MiB / 47p；≪10MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2607.24653
 - https://arxiv.org/pdf/2607.24653
 - https://www.kimi.com/blog/kimi-k3
 - https://huggingface.co/moonshotai/Kimi-K3
 - https://github.com/MoonshotAI/MoonEP
 - https://github.com/kvcache-ai/AgentENV
arxiv: ["2607.24653"]
related: ["KimiK2技术报告深读", "Kimik15技术报告深读", "DeepSeekV4技术报告深读", "Nemotron3Ultra", "OLMo3全栈开放配方", "Qwen3CoderNext", "开源与闭源前沿模型谱系", "混合专家架构", "推理时扩展TestTimeScaling"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 开源前沿旗舰：Kimi K3 Technical Report（≠ Nemotron / OLMo / Coder-Next / DeepSeek-V4）

> **定位**：开源前沿旗舰主题轴——Kimi Team *Kimi K3: Open Frontier Intelligence*（arXiv:**2607.24653**v2，页眉 **7 Aug 2026**；XMP identifier `…/2607.24653v2`）。立「**开源 3T 级原生多模态 MoE 旗舰 TR**」：在 **预训练规模轴（≈2.8T / 104B 激活）** 与 **1M 上下文 test-time / agentic RL 轴** 上同时推进，公开全权重。
> **攻坚线**：**架构思想（主）**——Hybrid KDA–MLA、AttnRes、Stable LatentMoE（SiTU-GLU / Quantile Balancing）、MoonViT-V2、Per-Head Muon；**AI Infra（辅）**——FlashKDA / KCP、MoonEP、1M agentic RL + AgentENV、KDA-aware prefix cache / QAT 服务；**评测字段（文内表，辅）**——Table 2/3 与 Fig.1 主结果转述。
> **硬划界（开篇钉死）**：
> - **≠ [[Nemotron3Ultra]]**：禁止写成 **Nemotron 3 Ultra**（Hybrid Mamba–Attention + LatentMoE / NVIDIA 开源旗舰）配方复述。本卡只写 **Moonshot Kimi K3** 本体；Nemotron 数字若不在本 PDF → 不出现。
> - **≠ [[OLMo3全栈开放配方]]**：禁止写成 **OLMo 3** 全开放数据/配方旗舰对照全文。
> - **≠ [[Qwen3CoderNext]]**：禁止写成 **Qwen3-Coder-Next**「代码专用小激活脚印 + 可执行反馈中训」轴。K3 的编码能力只作为 **文内 coding / agent 评测与 RL 域之一**，不立「Coder 专用旗舰」主轴。
> - **≠ [[DeepSeekV4技术报告深读]]**：禁止写成 **DeepSeek-V4**（CSA+HCA / mHC / 百万上下文）配方复述。本 PDF 虽保留 **Gated MLA** 与 **MoonEP↔DeepEP** 对照句，但 **主注意力是 KDA 混合栈**，残差是 **AttnRes**——**禁止**滑成「又一篇 DeepSeek 百万上下文 TR」。
> - **≠ [[开源与闭源前沿模型谱系]]**：禁止写成开闭源谱系通史 / 代际叙事；本卡是 **单篇 TR 深读**，他厂型号只出现在 **文内 Table 2/3 数字转述**。
> - **≠ [[KimiK2技术报告深读]] / [[Kimik15技术报告深读]]**：K2 的 MuonClip / MLA-only / 1.04T 表、K1.5 的 RL 通史不重开；本卡只录 **相对 K2 的 ∆（Table 1）** 与 K3 新增件。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）与辅博文明示句。文内未给出的精确总 token 账本 / GPU 小时 / 完整层宽公式推导 → **不得外推**。图柱未与表对齐的读数标 **待核实读图**。

---

## 一、材料元信息与 PDF 体积

| 项 | 报告原文 / 元数据 | 出处 |
|---|---|---|
| 标题 | Kimi K3: Open Frontier Intelligence（页内另标 *Technical Report of Kimi K3*） | 封面； Title |
| 作者 | Kimi Team（XMP `dc:creator` 另列大量具名贡献者） | 封面；XMP |
| arXiv | **arXiv:2607.24653v2** \[cs.CL\] **7 Aug 2026** | PDF 页眉 |
| XMP identifier | `https://arxiv.org/abs/2607.24653v2` | ` -meta` |
| XMP MetadataDate | 2026-08-10T00:33:42+00:00（→ 用户时区 **2026-08-10 08:33 CST**） | XMP |
| 权利 | `http://creativecommons.org/licenses/by-nc-nd/4.0/` | XMP |
| 产品字段（摘要） | **2.8T** MoE；**104B** activated；原生视觉；**1M** 上下文；相对 K2 约 **2.5×** scaling efficiency | Abstract |
| 权重入口 | https://huggingface.co/moonshotai/Kimi-K3 | Abstract 脚注 1 |
| PDF 页数 / 尺寸 | **47** 页 letter | |
| Producer / Creator | pikepdf 8.15.1；arXiv GenPDF (tex2pdf:8def8d8) | XMP |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| **主 PDF（arXiv）** | `https://arxiv.org/abs/2607.24653` | **1.71MiB**（1,790,685 B） | **47** | **官方 HTTPS 外链**（≪10MB；页数适中） |
| **抽取** | | 265K | — | 全文检索 |
| **辅博文** | https://www.kimi.com/blog/kimi-k3 | — | — | 产品案例 / 可用性 / 局限；**不替代** TR 数字源 |

**一句话抓手：**
把开源预训练规模推到 **3T 级（Table 1：2.78T / 104.2B 激活）**，用 **KDA+AttnRes+Stable LatentMoE** 换约 **2.5×** 相对 K2 的 scaling efficiency，再在 **1M 上下文**上做多域多努力度 RL → **MOPD** 合并，公开全权重；整体仍落后 Claude Fable 5 / GPT-5.6 Sol，但文内套件上 consistently 领先其余对照（含 GLM-5.2）。

**辅博文（产品层，非 TR 权威数字源）要点（2026-09-22 WebFetch）：**
- 自称「world's first open 3T-class model」；权重计划 **July 27, 2026** 全量释放（博文句；与 TR Abstract「we release」并存——以落地 HF 为准）。
- 产品入口：Kimi.ai / Work / Code / API（`kimi-k3`）；launch 默认 **max thinking**；low/high 后续。
- API 价（博文）：cache-hit input **$0.30**/MTok、cache-miss **$3.00**/MTok、output **$15.00**/MTok；称 Mooncake 分离推理、coding 场景 cache hit >90%。
- 局限（博文）：thinking history 敏感；过度主动；相对 Fable 5 / GPT-5.6 Sol 仍有 UX 差距。

---

## 二、议题边界：Kimi 开源 3T 旗舰 ≠ 他厂配方 / ≠ 谱系通史 / ≠ 代码专用卡

### 2.1 五向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **Nemotron 3 Ultra** | Hybrid Mamba–Attn + LatentMoE 开源旗舰 | **[[Nemotron3Ultra]]** | **否** |
| **OLMo 3** | 全开放数据/配方旗舰 | **[[OLMo3全栈开放配方]]** | **否** |
| **Qwen3-Coder-Next** | 代码专用 80A3 + 可执行反馈中训 | **[[Qwen3CoderNext]]** | **否**（禁滑成 Coder 卡） |
| **DeepSeek-V4** | CSA+HCA / mHC / 1M 上下文 | **[[DeepSeekV4技术报告深读]]** | **否**（禁 DeepSeek 配方复述） |
| **开闭源谱系** | 代际 / thinking 产品化通史 | **[[开源与闭源前沿模型谱系]]** | **否** |
| **Kimi K2 / K1.5** | 前代 TR 全文 | **[[KimiK2技术报告深读]] / [[Kimik15技术报告深读]]** | **否**（仅 ∆） |
| **Kimi K3 开源前沿旗舰** | 3T 架构 + 1M agentic RL + Infra + 文内评测 | **本篇** | **是** |

跟读直觉：[[DeepSeekV4技术报告深读]] 问「**DeepSeek 如何压百万上下文 KV/算力**」；[[Nemotron3Ultra]] 问「**NVIDIA 开源旗舰 Hybrid+LatentMoE**」；[[Qwen3CoderNext]] 问「**小激活脚印上的代码 agent 反馈栈**」；本卡问「**Moonshot 如何同时推开源预训练规模到 3T 类、并用 KDA/AttnRes/Stable LatentMoE + 1M RL 立开源前沿**」。共享「MoE / 长上下文 / agent RL」词汇，但 **厂商栈与主杠杆不同**——禁止写成「DeepSeek/Nemotron 配方换皮」。

`
 开源「旗舰 TR」近窗
 │
 ┌─────────┼─────────┬──────────────┐
 │ │ │ │
 [[Nemotron3Ultra]] [[OLMo3全栈开放配方]] [[Qwen3CoderNext]] [[DeepSeekV4技术报告深读]]
 Nemotron OLMo3 Coder-Next DeepSeek-V4
 Ultra (CSA/HCA)
 │ │ │ │
 └─────────┴────┬────┴──────────────┘
 │ 禁止复述
 ▼
 ★ [[KimiK3技术报告]] Kimi K3
 KDA+AttnRes+Stable LatentMoE
 2.78T/104.2B · 1M · 开权
`

### 2.2 本卡故意不写什么

| 不写 | 原因 |
|---|---|
| DeepSeek MoE/MLA/DeepEP 通史与 V4 CSA 配方 | → [[DeepSeekV4技术报告深读]] / DeepSeek 系列技术报告；本 PDF 仅借用 MLA 周期层与 DeepEP 对照句 |
| Nemotron LatentMoE / Mamba hybrid 全文 | → [[Nemotron3Ultra]]；名称「LatentMoE」同源引用 ≠ 同一配方卡 |
| OLMo 开放数据账本 | → [[OLMo3全栈开放配方]] |
| Qwen Coder MegaFlow / 80A3 训练栈 | → [[Qwen3CoderNext]] |
| [[开源与闭源前沿模型谱系]] 开闭源谱系长表 | 本卡单篇深读 |
| K2 MuonClip / 15.5T token 账本全文 | → [[KimiK2技术报告深读]]；本卡只录相对 ∆ |
| 博文案例的「芯片设计 / MiniTriton」完整复现步骤 | 辅材料；以 §7 Case Studies 提纲为准，不编造指标 |

---

## 三、模型规模与架构（相对 K2 的 ∆）

### 3.1 Table 1：K2 → K3（报告明文）

| 项 | Kimi K2 | Kimi K3 | ∆ |
|---|---|---|---|
| Architecture | MoE | MoE | – |
| #Layers | 61 | **93** | ↑ 52% |
| Total Parameters | 1.04T | **2.78T** | ↑ 167% |
| Activated Parameters | 32.6B | **104.2B** | ↑ 220% |
| Hidden Dimension | 7,168 | 7,168 | = |
| Latent MoE Dimension | – | **3584 (0.5×)** | – |
| MoE Hidden Dim / Expert | 2,048 | **3,072** | ↑ 50% |
| Routed Experts | 384 | **896** | ↑ 133% |
| Experts Active / Token | 8 | **16** | ↑ 100% |
| Shared Experts | 1 | **2** | ↑ 100% |
| Attention Heads | 64 | **96** | ↑ 50% |
| Dense Layers | 1 | 1 | = |
| Vocabulary | 160K | 160K | = |
| Training Context | 128K | **1M** | 8× |
| Attention | MLA | **Hybrid KDA–MLA** | – |
| Activation | SwiGLU | **SiTU-GLU** | – |
| Attention-Layer Composition | 61 MLA | **69 KDA + 24 MLA** | – |
| MTP Layers | 1 | 1 | = |
| ViT | – | **401M**；27 layers；patch 14；12 heads | – |

> 摘要口语写「2.8T / 104 billion activated」；对表以 **Table 1：2.78T / 104.2B** 为准。稀疏度口径：16/896 routed ≈ **56**（正文 §2.3）。

### 3.2 三维信息流（§2 总览）

| 维 | 机制 | 本卡一句话 |
|---|---|---|
| **序列** | Hybrid Attention：每 block **3× KDA + 1× Gated MLA**；骨干末再加一层 Gated MLA | 线性态长序列 + 周期全局交互；MLA 层 **NoPE** |
| **深度** | **Attention Residuals (AttnRes)**：伪 query 对前层/块表示做注意力残差；K3 划 **8 块 × 约 12 层**（含 embedding 计 9 块级源） | 突破「单状态累加」深度瓶颈；Block AttnRes 降内存/通信 |
| **宽度** | **Stable LatentMoE**：共享专家全宽 + 路由专家在 latent 宽 $\ell$；**16/896** | 极端稀疏下用 RMSNorm↑、**SiTU-GLU**、**Quantile Balancing** 稳住 |

### 3.3 Kimi Delta Attention：相对 Kimi Linear 的 K3 增量（§2.1.1）

| 增量 | 报告主张 |
|---|---|
| **Lower-bounded decay** | $g = g_{\min}\mathrm{Sigmoid}(e^{A}z)$，$g_{\min}=-5$；避免负 Softplus 无界导致 chunk 对角 tile 只能走 position-pair；使对角/非对角均可走 Tensor Core 稠密 matmul |
| **Full-rank output gate** | 相对 Kimi Linear 低秩门 → 输入依赖全秩 $\mathrm{Sigmoid}(W_g x)$ 门控 RMSNorm 后的循环输出 |
| **Chunkwise** | 块内并行、块间递归；FlashKDA（§5）服务训练与 prefill |

### 3.4 Gated MLA（§2.1.2）

- 继承 DeepSeek-V2 MLA 的 KV 压缩思路（**引用关系，非本卡主写 DeepSeek**）。
- 相对 K2/K2.5：**全部 MLA 层 NoPE**；位置感由穿插 KDA 承担 → 扩上下文时不改 RoPE/YaRN。
- 同样加 **全秩输出门**；训练时 attention 输出保持 FP32 以纠正 flash attention 偏置舍入（报告称）。

### 3.5 Stable LatentMoE 三件套（§2.3）

| 组件 | 作用（报告） |
|---|---|
| **Normalized LatentMoE** | 路由聚合 $u$ 后 **RMSNorm** 再 $W^\uparrow$；抑尺度敏感、改善 val/下游 |
| **SiTU-GLU** | 对 SwiGLU 两支做 softcap：$\beta_1=4,\beta_2=25$；近原点近似 SwiGLU，大正输入有界 $\lvert f\rvert\le\beta_1\beta_2=100$ |
| **Quantile Balancing (QB)** | 无辅助损失路由；用 margin 分位数设 expert bias，histogram 估计全局 batch 分位；推理冻结 bias |

### 3.6 原生视觉 MoonViT-V2（§2.4）

- **从零** next-token 训视觉塔（相对 K2.5 SigLIP 初始化）；报告称梯度更稳、视觉评测可匹配 SigLIP init。
- ~**0.4B / 401M**，27 层；图/视频共享；空间+时间分解注意力 + 时间池化；$2\times2$ pixel-shuffle → 视觉 token ÷4；支持至 **3584×3584** 像素输入（在 1M 上下文预算内）。

### 3.7 Per-Head Muon（§2.5）

- 矩阵参数用 Muon；注意力 Q/K/V 对 **逐 head** 做 Newton–Schulz 正交化，避免大尺度 head 主导整矩阵更新。

---

## 四、预训练与长上下文（§3）

| 项 | 报告设定 |
|---|---|
| 数据域 | Web / Code / Math / Knowledge + 大规模视觉（caption、交错图文、OCR、感知、视频、视觉编码等）；知识/数学延续 K2 **改写**配方 |
| Scaling | 相对 K2 约 **2.5×** overall scaling efficiency（Fig.7；OOD val） |
| LR 日程 | 独立搜参后 **cosine** 优于 WSD（同最小 LR、各自最优峰 LR/BS） |
| 优化 | Per-Head Muon + K2 **weight-clipping**；QB 负载均衡；WD **0.1**；cosine + **1%** warmup |
| 多模态策略 | **原生联合** NTP（非后置对齐） |
| 上下文课程 | PT：**8K→64K**；cooldown：**256K→1M**（四阶段） |
| 位置编码 | **NoPE**；位置由 KDA 门控/衰减隐式编码 → 宣称可直接外推 1M、无需 RoPE 改参 |
| 长文数据 | 清洗+上采样真长文/视频；并 **置换拼接** 合成「必须跨全上下文」任务，防注意力塌成局部模式 |

> **待核实**：本 PDF **未**给出与 K2「15.5T tokens」同口径的 K3 总 token 账本 → **不编造**。

---

## 五、后训练：SFT → 九专家 RL → MOPD（§4）

### 5.1 三阶段范式

1. **SFT**：扩 agentic 轨迹；XTML chat template（§F）；自 SFT 起 **QAT**（专家权重 **MXFP4**、激活 **MXFP8**；非专家更高精度）。
2. **RL**：三大域 × 三努力度 `{low, high, max}` → **9** 个专家：
 - general（经验/视觉/推理/忠实/搜索/知识工作）
 - general agents（长程助手、深度研究、段落写作）
 - coding agents（SWE、编码体验、kernel、webdev）
3. **MOPD**：多教师 on-policy 蒸馏合并为统一模型（per-token OPD reward + clip）。

### 5.2 RL 算法与努力度（报告骨架）

- 延续同步 RL + **partial rollout**（完成比例 $\lambda$ 即进入优化；长轨迹跨迭代 → 依赖 per-token 正则容忍 stale）。
- **Reasoning Effort RL**：按题初始预算 $b_0(x)$，超 $\tau\cdot b_0$ 则 reward 置 **-1**；先训 max 再退火得 high/low。
- 非可验证任务：**Agentic GRM**（锦标赛二元比较 + 强制 rubric 协议 + 冗长度惩罚）。

### 5.3 任务/环境合成（只列品类，不抄环境实现通史）

统一 **white-box** harness 配置空间（可实例化 Kimi Code / Claude Code / Codex 等）；知识图谱引导任务合成；可验证搜索/专业工作/视觉工具环；**kernel 优化**（正确性+性能，反 hacking）；个人助理 mock app 跨日任务；**AET** verify-in-the-loop；webdev 确定性检查 + 模型评判。

### 5.4 部署感知：QAT + EAGLE-3 式 draft（§4.1.4）

- 专家 MXFP4 / 激活 MXFP8；RL rollout 与训练同量化方案。
- 预训练 MTP 层微调为 EAGLE-3 风格 draft；融合 AttnRes **第 1 / 4 / 末**块特征；直接优化 **LK loss**（接受率负对数）而非仅 KL。

---

## 六、基础设施要点（§5，跟读字段）

| 子系统 | 关键词（报告） |
|---|---|
| **KDA 系统** | FlashKDA（CUTLASS chunkwise）；设备内 SM 级 CP；跨设备 **KCP**（固定大小 all-gather 状态片段 + prefix scan） |
| **3T 预训练** | PP+VP、EP、ZeRO-1、Pipeline ZeRO-2、CP；**MoonEP**（完美负载、冗余专家 ≤E/R、静态 shape、零拷贝 permute）；统一 activation manager（FP8 量化/offload/重算）；Block AttnRes 通信下界；P2P Muon 正交化；ViT 动态 CP + PP bubble 藏算 |
| **1M Agentic RL** | 同置训练；外置 KV/KDA 状态池；rollout auto-throttle；梯度 buffer 复用非策略前向；**AgentENV** microVM（Firecracker；pause/fork/snapshot；文称共创建 **51,219,741** sandboxes / **1,505,678** images） |
| **在线服务** | KDA–MLA 统一分页前缀缓存；细粒度 hash block vs 稀疏 KDA checkpoint；专用 decode/AttnRes/稀疏 LatentMoE kernel；cache-aware 调度 + budget admission |

开源入口（文内脚注）：MoonEP `github.com/MoonshotAI/MoonEP`；AgentENV `github.com/kvcache-ai/AgentENV`。

---

## 七、评测字段（§6；文内表转述）

### 7.1 评测协议（跟读约束）

- K3：**reasoning effort = max**，temperature **1.0**；单步知识/推理 top-p **0.95**，agentic top-p **1.0**。
- 对照：Claude Fable 5（**含 potential fallbacks**）、GPT-5.6 Sol（**含 potential cyberguards**）、Opus 4.8、GPT-5.5（**xhigh**）、开源对照 **GLM-5.2**。
- Coding harness：Kimi Code / Claude Code / Codex 分任务选用（脚注级细节见原文 §6.1.3）。
- BrowseComp：默认 300K 触发 compaction；**无管理 1M** 时文称 **90.4%**（主表 BrowseComp 为 **91.2%**——口径见原文，勿混）。

### 7.2 Table 2 精选（K3 max；完整表见 PDF）

| 轴 | 基准 | K3 | Fable 5 | GPT-5.6 Sol | 备注 |
|---|---|---|---|---|---|
| 知识/推理 | GPQA Diamond | **93.5** | 92.6 | **94.1** | 接近前沿 |
| | CritPt | 23.4 | 28.6 | **32.3** | 报告自承研究级差距 |
| | HLE-Full (w/o / w tool) | 43.5 / 56.0 | **53.3 / 63.0** | 44.5 / 58.0 | |
| Coding | DeepSWE | 67.5 | 70.0 | **73.0** | |
| | ProgramBench | **77.8** | 76.8 | 77.6 | K3 文内最优 |
| | Terminal-Bench 2.1 | 88.3 | 88.0 | **88.8** | 近并列 |
| | FrontierSWE | 81.2 | **86.6** | 71.3 | 次优、远超其余 |
| | SWE-Marathon | **42.0** | 35.0 | 39.0 | GPU kernel 向 |
| Agentic | BrowseComp | **91.2** | 88.0 | 90.4 | |
| | AutomationBench | **30.8** | 29.1 | 29.7 | |
| | GDPval-AA v2 Elo | 1686 | **1747** | 1736 | 第三方至 2026-07-23 |
| Vision | OmniDocBench | **91.1** | 89.8 | 85.8 | |
| | ZeroBench pass@5 (w/o / w Py) | 23.0 / 41.0 | 23.0 / **46.0** | 17.0 / 35.0 | |

**报告级结论句（§6.1.4）：** 整体紧追 Fable 5 / GPT-5.6 Sol，并 consistently 优于 Opus 4.8、GPT-5.5、GLM-5.2。

### 7.3 成本效率（Fig.13；定性）

文称在 KCB 2.0 / BrowseComp / GDPval-AA v2 / AA-Briefcase 上，K3 落在或靠近 **score–cost 前沿**，相对 Fable 5 成本更低（精确曲线点 → **待核实读图**）。

---

## 八、结论与跟读建议

**结论（§8 转述）：** K3 是开源 **2.8T** 级原生视觉 MoE、**1M** 上下文，基于 KDA 与 AttnRes；自称首个开源 **3T-class** 模型；在长程编码 / agentic / 知识 / 推理 / 视觉上达 frontier-level，与最强闭源仍有差距，但立新的开源前沿并公开权重。

**跟读顺序建议：**

1. Abstract + Fig.1 + Table 1（规模与主结果）
2. §2.1–2.3（KDA lower-bound / AttnRes / SiTU+QB）—架构主杠杆
3. §4.1（SFT→9专家 RL→MOPD + QAT）—后训练主杠杆
4. §5.1–5.3（FlashKDA/KCP、MoonEP、AgentENV）—Infra 可迁移字段
5. Table 2/3—评测口径与 harness 脚注
6. 辅博文：产品可用、案例、局限（与 TR 交叉，不以博文覆盖 Table）

- PDF **1,790,685 B ≈ 1.71MiB ≪10MB** → **官方 HTTPS 外链** `https://arxiv.org/abs/2607.24653`。
- 抽取已存 （及 镜像）。
- 笔记路径：模型与技术报告/厂商报告/KimiK3技术报告.md（本文件）。

---

## 九、待核实 / 缺口清单

| 项 | 状态 |
|---|---|
| K3 预训练总 token / GPU-小时精确账本 | 本 PDF 未给 → 不编造 |
| Fig.7 / Fig.13 曲线精确坐标 | 需读图；已标 **待核实读图** |
| 权重实际落地日 vs 博文「July 27, 2026」 | 以 HF `moonshotai/Kimi-K3` 为准复核 |
| §F XTML 模板全文、附录 B–E 证明细节 | 本卡未展开；需要时回 PDF |
| 与 Nemotron LatentMoE / DeepSeek MLA 的「同名组件」细对比实验 | **划界禁止**在本卡展开；另立项再写 |

