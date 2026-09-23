---
title: "技术报告专项：DeepSeek-V3 报告深读切片（训练配方 / MoE / Infra）"
topic: TR-DeepSeek-V3
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
source_url: https://arxiv.org/abs/2412.19437
archived: 2026-09-22
---

# TR · DeepSeek-V3 报告深读切片：训练配方 / MoE 机制 / Infra

> **定位**：报告级对照表 / 深读卡。数字一律取自官方 PDF `https://arxiv.org/abs/2412.19437`。
> **刻意不写**：Switch→Mixtral→V3 史线叙事（见 [[混合专家架构]]）、开闭源谱系定位（见 [[开源与闭源前沿模型谱系]]）、Megatron/FA/vLLM 通论（见 [[AI基础设施总览]]）。本卡只补「可对表跟读」的配方与机制细节。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | DeepSeek-V3 Technical Report | 封面 |
| 作者 | DeepSeek-AI；`research@deepseek.com` | 封面 |
| arXiv 页眉 | **arXiv:2412.19437v2** \[cs.CL\] **18 Feb 2025** | PDF 第 1 页页眉 |
| PDF 页数 | **53**（A4） | |
| PDF CreationDate / ModDate | Wed Feb 19 10:11:22 **2025 CST** | |
| Producer | pdfTeX-1.40.25；LaTeX with hyperref | |
| 本地路径 | `https://arxiv.org/abs/2412.19437` | 仓库 |
| 权重仓库（摘要） | https://github.com/deepseek-ai/DeepSeek-V3 | Abstract |
| 摘要规模一句话 | 671B total / **37B activated** per token；预训练 **14.8T** tokens；全流程 **2.788M H800 GPU hours**；auxiliary-loss-free 负载均衡 + MTP；训练过程「未出现 irrecoverable loss spikes / 未做 rollbacks」 | Abstract；§1 |

**版本说明（本卡边界）**：本 PDF 页眉仅标 **v2 / 18 Feb 2025**。[[开源与闭源前沿模型谱系]] 另记「Submitted 2024-12-27 / last revised 2025-02-18」来自 arXiv abs 页，**不在本 PDF 正文** → 见第六节待核实。

---

## 二、训练配方对照表（仅报告数字）

### 2.1 阶段与算力成本（Table 1 + §1）

| 阶段 | H800 GPU hours | 按 $2/GPU-hour 折算（报告假设） | 报告补充 |
|---|---|---|---|
| Pre-Training | **2664K** | $5.328M | 每万亿 token ≈ **180K** H800 hours；2048 卡集群上约 **3.7 days / T tokens**；预训练「不到两个月」 |
| Context Extension | **119K** | $0.238M | 两阶段 YaRN：4K→32K→128K |
| Post-Training | **5K** | $0.01M | SFT + RL |
| **Total** | **2788K = 2.788M** | **$5.576M** | 不含「先前研究与消融」成本 |

集群（§3.1）：**2048 NVIDIA H800**；每节点 8 GPU（NVLink + NVSwitch）；跨节点 **InfiniBand**。

### 2.2 数据与分词（§4.1）

| 项 | 报告数字 / 设定 |
|---|---|
| 预训练语料 | **14.8T** high-quality and diverse tokens（相对本 tokenizer） |
| 打包 | document packing；**不做** cross-sample attention masking |
| FIM | 与 DeepSeekCoder-V2 对齐；**PSM**：`<\|fim_begin\|> f_pre <\|fim_hole\|> f_suf <\|fim_end\|> f_middle <\|eos_token\|>`；文档级、pre-packing 阶段；**rate = 0.1** |
| Tokenizer | Byte-level BPE；词表 **128K**；相对 V2 的 pretokenizer 改动（标点+换行合并 token 等）；训练中随机拆分部分合并 token 以缓解 token boundary bias |

### 2.3 模型结构超参（§4.2 Model Hyper-Parameters）

| 项 | 值 |
|---|---|
| Transformer 层数 $L$ | **61** |
| Hidden dim $d$ | **7168** |
| 参数初始化 std | **0.006** |
| MLA：$n_h$ / $d_h$ | **128** / **128** |
| MLA：KV 压缩 $d_c$ / Query 压缩 $d_c'$ | **512** / **1536** |
| MLA：解耦 RoPE per-head $d_h^R$ | **64** |
| MoE 替换范围 | **除前 3 层外**全部 FFN → MoE |
| 每 MoE 层 | **1 shared + 256 routed**；每专家 intermediate **2048** |
| 每 token 激活路由专家 $K_r$ | **8** |
| Node-limited $M$ | **≤ 4 nodes** |
| MTP 深度 $D$ | **1**（主 NTP + 额外预测 1 个未来 token） |
| 总参 / 激活参 | **671B** / **37B** per token |

### 2.4 预训练优化与调度（§4.2 Training Hyper-Parameters）

| 项 | 报告设定 |
|---|---|
| 优化器 | **AdamW**：$\beta_1=0.9$, $\beta_2=0.95$, **weight_decay=0.1** |
| 预训练最大序列长 | **4K** |
| 预训练 token 量 | **14.8T** |
| LR warmup | 线性 **0 → $2.2\times10^{-4}$**，前 **2K steps** |
| LR 恒定段 | $2.2\times10^{-4}$ 直到消耗 **10T** tokens |
| LR cosine 衰减 | 在随后 **4.3T** tokens 内衰减到 $2.2\times10^{-5}$ |
| 末 **500B** tokens | 前 **333B**：恒定 $2.2\times10^{-5}$；后 **167B**：恒定 $7.3\times10^{-6}$ |
| Grad clip | **1.0** |
| Batch size 调度 | 前 **469B** tokens：从 **3072 → 15360**；此后恒定 **15360** |
| 专家部署（训练叙述） | 每层 routed experts **均匀部署在 64 GPUs / 8 nodes** |
| Aux-loss-free $\gamma$（bias update speed） | 前 **14.3T**：$\gamma=0.001$；剩余 **500B**：$\gamma=0.0$ |
| Sequence-wise balance $\alpha$ | **0.0001** |
| MTP loss 权重 $\lambda$ | 前 **10T**：$\lambda=0.3$；剩余 **4.8T**：$\lambda=0.1$ |

**训练目标组成（机制，§2.2）**：主模型 next-token CE + 加权 MTP 损失
$$
\mathcal{L}_{\mathrm{MTP}}=\frac{\lambda}{D}\sum_{k=1}^{D}\mathcal{L}_{\mathrm{MTP}}^{k},\quad D=1.
$$
推理时可丢弃 MTP 模块；也可挪作 speculative decoding。

### 2.5 长上下文扩展（§4.3）

| 项 | 阶段 1 | 阶段 2 |
|---|---|---|
| 目标上下文 | **32K** | **128K** |
| 每阶段 steps | **1000** | **1000** |
| Batch size | **1920** | **480** |
| LR | $7.3\times10^{-6}$（两侧相同；= 预训练末段 LR） | 同左 |
| 方法 | **YaRN**；仅作用于解耦共享 key $k_t^R$；与 V2 一致 | 同左 |
| YaRN 超参 | scale $s=40$, $\alpha=1$, $\beta=32$；scaling factor $t=0.1\ln s + 1$ | 同左 |

### 2.6 后训练配方要点（§5；数字仅报告给出者）

| 项 | 报告数字 / 设定 |
|---|---|
| SFT 数据规模 | **1.5M** instances（多域；推理域用内部 DeepSeek-R1 路线 + rejection sampling；非推理域用 DeepSeek-V2.5 生成 + 人工校验） |
| SFT epochs | **2** |
| SFT LR | cosine：**$5\times10^{-6}$ → $1\times10^{-6}$** |
| SFT packing | 多样本打包进单序列，但 **sample masking** 使样本互不可见 |
| RL 算法 | **GRPO**（与 V2 相同引用链；无同等规模 critic；组内 reward 标准化得 advantage） |
| Reward | **Rule-based RM**（可规则校验题，如数学 boxed / LeetCode 编译）+ **Model-based RM**（自 V3 SFT checkpoint；偏好数据含得到 reward 的 CoT） |
| 后训练算力 | Table 1：**5K** H800 hours（未再拆 SFT/RL 细账） |

---

## 三、MoE 机制对照表

### 3.1 结构与激活

| 维度 | DeepSeek-V3（报告） |
|---|---|
| 范式 | DeepSeekMoE：细粒度专家 + **shared experts 隔离**（相对 GShard 类粗粒度叙述） |
| Shared / Routed | $N_s=1$, $N_r=256$（§4.2） |
| 激活 | 每 token：**8 routed** + shared 始终参与（§2.1.2 / §4.2） |
| 专家宽度 | intermediate hidden **2048** |
| 亲和度 | $s_{i,t}=\mathrm{Sigmoid}(u_t^\top e_i)$（**相对 V2 改为 sigmoid**；选中专家上再归一化得门控 $g_{i,t}$） |
| 门控 | Top-$K_r$ 选中后，对选中亲和度归一化；未选中为 0（式 13–15） |
| Node-limited routing | 每 token 最多 **$M=4$** 节点；按各节点上最高 $K_r/M$ 亲和度和选节点（§2.1.2） |
| Token drop | **训练与推理均 no token-dropping**（称均衡有效 + 推理侧部署策略） |

### 3.2 负载均衡：auxiliary-loss-free + 极小序列辅助损失

| 机制 | 报告要点 | 超参 |
|---|---|---|
| **Auxiliary-loss-free**（主路径） | 每专家偏置 $b_i$；用 $s_{i,t}+b_i$ 做 Top-$K$ **选择**；真正乘到专家输出的门控仍来自原始 $s_{i,t}$。按 **整 batch** 监测负载：过载则 $b_i\leftarrow b_i-\gamma$，欠载则 $+\gamma$ | $\gamma=0.001$（前 14.3T）；末 500B $\gamma=0$ |
| **Sequence-wise complementary aux loss** | 防止单条序列内极端不均；$\alpha$「extremely small」 | $\alpha=0.0001$ |
| 动机（报告表述） | 过大 aux loss 伤主任务；无 aux 主路径旨在减少「为均衡牺牲质量」 | §2.1.2 |
| 消融/现象 | §4.5 / Fig.9 / App.C：aux-loss-free 在 Pile 域上呈现 **更强专家特化**（relative expert load 可视化）；完整层图在附录 | 详见原文图，本卡不抄评分数 |

### 3.3 与训练并行的接口（机制侧）

| 项 | 报告 |
|---|---|
| 训练 EP 叙述 | routed experts 均匀部署在 **64 GPUs / 8 nodes**（与 §3.2「64-way EP spanning 8 nodes」一致） |
| 通信约束 | Node-limited $M=4$ 使框架「nearly achieve full computation-communication overlap」 |
| 推理冗余专家（§3.4，机制摘要） | Prefill：EP32 + 冗余专家；Decode：把 shared 也当 routed（每 token 选 **9** 专家视角）、EP320 等——**部署数字**见第四节 Infra 表 |

---

## 四、Infra 对照表（并行 / 精度 / 流水线）

### 4.1 训练并行组合（§3.2）

| 维度 | 设定 |
|---|---|
| 框架 | **HAI-LLM**（自研） |
| Pipeline Parallelism | **16-way PP** |
| Expert Parallelism | **64-way EP**，跨 **8 nodes** |
| Data Parallelism | **ZeRO-1 DP** |
| Tensor Parallelism | 报告称通过显存优化，**训练不使用昂贵的 TP** |
| 算通比痛点 | 跨节点 EP 下 computation-to-communication ≈ **1:1** → DualPipe 动机 |

### 4.2 DualPipe（§3.2.1，Table 2）

| 项 | 报告内容 |
|---|---|
| 核心想法 | 在一对 forward/backward **chunk** 内重叠计算与通信；双向 pipeline（两端同时灌 micro-batch） |
| Chunk 拆分 | forward：attention / all-to-all dispatch / MLP / all-to-all combine；backward 再拆 **backward for input** 与 **backward for weights**（类 ZeroBubble）；另有 PP communication |
| 目标 | all-to-all 与 PP 通信 **fully hidden**；保持恒定算通比时可继续跨节点细粒度专家、近零 all-to-all 开销 |
| 约束 | pipeline stages 与 micro-batches **均可被 2 整除**；不要求 micro-batches 可被 stages 整除；气泡与 activation 不随 micro-batch 数增加而恶化 |
| 参数副本 | DualPipe 需 **2×** 参数副本；大 EP 下称内存影响有限 |
| 与 MTP | 最浅层（含 embedding）与最深层（含 output head）放同一 PP rank → MTP 与主模型 **物理共享** emb/head |

**Table 2 气泡 / 显存对照**（符号：$F$ forward chunk；$B$ full backward；$W$ backward-for-weights；$F\&B$ 互相重叠的一对 forward+backward）：

| Method | Bubble | Parameter | Activation |
|---|---|---|---|
| 1F1B | $(PP-1)(F+B)$ | $1\times$ | $PP$ |
| ZB1P | $(PP-1)(F+B-2W)$ | $1\times$ | $PP$ |
| **DualPipe** | $\bigl(\frac{PP}{2}-1\bigr)(F\&B + B - 3W)$ | $2\times$ | $PP+1$ |

> PDF 文本抽取时 Table 2 的 DualPipe 气泡行有折行；上表按正文叙述与常见排版还原。**引用气泡公式时建议回看 PDF 原表**（亦见第六节）。

### 4.3 跨节点 All-to-All（§3.2.2）

| 项 | 报告数字 / 设定 |
|---|---|
| 拓扑 | 跨节点 **IB**；节点内 **NVLink** |
| 带宽叙述 | NVLink **160 GB/s** ≈ IB **50 GB/s** 的 **3.2×** |
| 与路由协同 | 每 token ≤ **4** 节点 → 压低 IB 流量；先 IB 到目标节点同 index GPU，再 NVLink 转发到托管专家的 GPU；IB∥NVLink |
| 每节点可选专家均值 | 约 **3.2 experts/node** 无额外 NVLink 开销 → 理论上限约 **4×3.2=13** 路由专家同通信成本（实际 $K_r=8$） |
| SM 占用 | **20 SMs** 即可打满 IB+NVLink；10 channels；warp specialization；定制 PTX + chunk auto-tune |

### 4.4 显存技巧（§3.2.3）

| 技巧 | 作用 |
|---|---|
| 重计算 **全部 RMSNorm** 与 **MLA up-projections** | 少存 activation |
| **EMA** 参数放 **CPU**，异步更新 | 估 LR decay 后表现；几乎不占 GPU 时/存 |
| DualPipe 同 rank 共享 emb/head | 服务 MTP，进一步省显存 |

### 4.5 FP8 混合精度训练（§3.3）

| 维度 | 报告设定 |
|---|---|
| 主张 | 「首次」在极大规模上验证 FP8 混合精度训练可行性（摘要 / §1 / §3.3） |
| 小规模验证 | 类 V2-Lite / V2 规模，约 **1T** tokens（App. B.1）；相对 BF16，相对 loss error **持续 < 0.25%** |
| GEMM | Fprop / Dgrad / Wgrad **走 FP8**；输出 BF16 或 FP32；相对 BF16 理论算力「约翻倍」 |
| 保留高精度 | embedding、output head、**MoE gating**、normalization、**attention** → BF16/FP32 |
| Master / 梯度 / 优化器 | master weights、weight gradients、以及用于 batch 累积的梯度等保持高精度；AdamW 一二阶矩可用 **BF16**；master 等仍 **FP32**（§3.3.3） |
| 量化粒度 | Activations：**1×128 tile**（per token per 128 channels）；Weights：**128×128 block** |
| FP8 格式选择 | **全部张量用 E4M3**（对比部分工作 Fprop=E4M3、Dgrad/Wgrad=E5M2） |
| 缩放 | **Online** max-abs → scale（不用 delayed scaling 推断） |
| 累加 | H800 上 FP8 Tensor Core 累加约 **14 bits**；每隔 $N_C=\mathbf{128}$ MMA 元素 **promote 到 CUDA Core FP32 累加** |
| 特殊激活 | Attention 后 Linear 输入等：定制 **E5M6**；scale 取 2 的整数次幂；反向 1×128↔128×1 转换时避免额外量化误差 |
| 低精度通信 | MoE **dispatch 前**激活量化到 FP8；**combine** 路径保留 **BF16** |

### 4.6 推理部署并行（§3.4，摘要级）

| 阶段 | 规模（报告） | 并行要点 |
|---|---|---|
| Prefilling | 例：涉及多节点 H800；MoE **EP32** | 冗余专家（文中：prefill 设 **32** redundant experts；每 GPU 原有 8 专家 + 1 冗余等） |
| Decoding | MoE **EP320**；例述 40 节点 / 320 GPU 量级 | 每 GPU 约 1 专家；shared 视为 routed → 每 token 选 **9**；另有冗余专家统计轮换 |

（完整 prefill/decode 节点表与冗余策略以 §3.4 原文为准；[[AI基础设施总览]] 已有摘要表，本卡不重复展开 serving 叙事。）

---

## 五、与 [[混合专家架构]] / [[开源与闭源前沿模型谱系]] 的差异说明（本卡新增了什么）

| 已有笔记 | 已覆盖（本卡不再复述） | **本 TR 卡新增 / 加深** |
|---|---|---|
| **[[混合专家架构]]** MoE 史线 | Switch / Mixtral / V3 思想跳跃；V3 头条：671B/37B、1 shared+256 routed、top-8、sigmoid、$M=4$、aux-loss-free 直觉、MLA/MTP 一句话、2.788M hours | **完整训练调度表**（LR / batch / $\lambda$ / $\gamma$ 分段）；YaRN 两阶段超参；SFT 1.5M / 2 epoch / LR；GRPO+双 RM；FIM 0.1；tokenizer 128K；**Table 2 DualPipe 气泡公式**；FP8 **E4M3 / 1×128 / 128×128 / $N_C=128$**；all-to-all 带宽与 20 SM / 3.2 experts/node |
| **[[开源与闭源前沿模型谱系]]** 谱系 | 开闭源坐标；V3 代际定位与头条数字；与 Llama4/Qwen3 对照表 | **报告页元信息（v2 / 53 页）**；按章节可对表的配方与 Infra 深读卡；明确「成本不含消融」等脚注级陈述 |
| **[[AI基础设施总览]]**（相关但不在任务强制对比列） | DualPipe/FP8/EP 的 Infra「势」通论与抓手 | 本卡把 V3 **单独拆成可打印对照表**，并补齐训练配方轴（[[AI基础设施总览]] 不展开 LR/batch/SFT） |

**一句话**：P0 讲「为什么重要 / 放在哪条史线」；本卡讲「报告里训练怎么配、MoE 怎么路由均衡、Infra 怎么叠 PP×EP×FP8×DualPipe——数字可回查页码」。

---

## 六、待核实与引用

### 6.1 待核实（禁止当作已确认）

1. arXiv **Submitted 2024-12-27** 与 abs 页 revision 历史：来自 [[开源与闭源前沿模型谱系]] / abs 页，**本 PDF 页眉仅见 v2 · 18 Feb 2025**；若写「首发日」需回查 https://arxiv.org/abs/2412.19437。
2. Table 2 DualPipe 气泡公式：PDF 文本层折行，公式以 **PDF 原表排版**为准复核一次。
3. §3.4 推理部署的完整节点/冗余专家表、动态 redundancy「探索中」表述：本卡只录摘要数字，未逐句抄全部署脚本级细节。
4. App. B.1/B.2 FP8 vs BF16 曲线、App. C 全部层专家负载图：未在本卡逐图数字化。
5. 评测表分数（MMLU / MATH / SWE-bench 等）：本专项聚焦训练/MoE/Infra，**不收录基准分**；需要时另开评测切片。
6. 官方新闻后续 V3.1 / V3.2 / V4 等：不在本 PDF；勿用本卡数字外推后续代际。
7. 「$2 / H800 GPU hour」与 $5.576M：报告**假设租金**折算，非独立审计账单。

### 6.2 引用

- DeepSeek-AI. *DeepSeek-V3 Technical Report*. arXiv:2412.19437v2 \[cs.CL\], 18 Feb 2025.
 PDF：https://arxiv.org/pdf/2412.19437
 本地：`https://arxiv.org/abs/2412.19437`
 （2026-09-22）

### 6.3 关联笔记

- [[混合专家架构]]：架构/MoE与稀疏/混合专家架构.md（MoE 史线）
- [[开源与闭源前沿模型谱系]]：模型与技术报告/开源与闭源前沿模型谱系.md（谱系）
- [[AI基础设施总览]]：推理与基础设施/AI基础设施总览.md（Infra 通论，含 DualPipe/FP8 抓手）

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

