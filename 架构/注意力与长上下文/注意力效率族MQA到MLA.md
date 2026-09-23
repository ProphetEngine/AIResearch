---
title: 注意力效率族：MHA → MQA/GQA → MLA
topic: 注意力效率族MQA到MLA
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
archived: 2026-09-22
---

# 11　注意力效率族：MHA → MQA/GQA → MLA

入口论文 / 报告：

- Ainslie et al., *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints* (arXiv:2305.13245；下文称 GQA 论文)。MQA 原始动机可追溯至 Shazeer (2019) *Fast Transformer Decoding: One Write-Head Is All You Need*（GQA 论文引用）。
- DeepSeek-AI, *DeepSeek-V3 Technical Report* (arXiv:2412.19437；下文称 V3 报告) **§2.1.1 Multi-Head Latent Attention**。MLA 架构在报告中明确归功于 DeepSeek-V2（DeepSeek-AI, 2024c）；V3 在 Transformer 框架内**复用并简述**该机制。

本笔记以**架构思想**为主线、**数学直觉**为辅线；公式、机制与实验数字均据上述文本，不编造未读到的对比表或吞吐数字。MQA 的「单 KV 头」定义以 GQA 论文对 Shazeer (2019) 的转述为准。

---

## 一、问题：推理 KV 显存与吞吐如何逼出注意力变体

自回归解码时，每生成一步都要读入已缓存的 **Key / Value**，并与当前步的 Query 做注意力。GQA 论文开篇把瓶颈写得很直白（§1）：

> Autoregressive decoder inference is a severe bottleneck for Transformer models due to the **memory bandwidth overhead** from loading decoder weights and **all attention keys and values at every decoding step**.

要点不是「算力不够」，而是**带宽**：序列越长、batch / 并发越大，KV cache 占用的显存与每次 decode 要搬动的字节数都线性膨胀，容易把 GPU 卡在「等数据」而不是「算矩阵」。

经典 **Multi-Head Attention (MHA)**（Vaswani et al., 2017）里，每个注意力头都有独立的 K、V。头数 $H$ 一多，每层、每个已生成 token 要缓存的 K/V 体积就按头数放大——这正是后续变体要动刀的对象。

工程上的压力可以概括成三条（均是对原文动机的归纳，非新实验）：

1. **显存**：KV cache 与「层数 × 序列长度 ×（K/V 头数）× 头维」成正比；长上下文与大并发直接顶满显存。
2. **吞吐**：decode 阶段算量相对小，带宽开销更显眼；GQA 论文强调的是「加载 K/V」带来的 memory bandwidth overhead。
3. **质量—速度张力**：少存一点 K/V 往往意味着少一点表达容量。MQA 把所有 query 头共用**一对** K/V 头，能大幅降带宽，但论文指出可能带来 **quality degradation** 与 **training instability**（摘要与 §1、Appendix A）。

因此注意力效率族的主线不是换掉「缩放点积注意力」本身，而是：**在尽量保住多头 query 表达力的前提下，减少必须驻留与反复加载的 K/V 表示**——从「每头一份 K/V」（MHA），到「全局一份」（MQA），到「每组一份」（GQA），再到「低秩联合压缩后再展开」（MLA）。

---

## 二、架构思想：MHA → MQA → GQA 的共享键值逻辑与取舍

### 2.1 一张图里的三种接线（GQA 论文 Figure 2）

GQA 论文用同一套语言对比三种机制（§2.2 / Figure 2）：

| 机制 | Query 头 | Key / Value 头 | 与其它机制的关系 |
|------|----------|----------------|------------------|
| **MHA** | $H$ | $H$（每头独立） | 满配容量，KV cache 最大 |
| **MQA** | $H$ | **1**（全体 query 共享） | GQA 的端点：GQA-1 ≡ MQA |
| **GQA** | $H$ | **$G$**（每组 query 共享一对 K/V） | 插值；GQA-$H$ ≡ MHA |

形式化表述（据 §2.2）：

- 把 $H$ 个 query 头分成 $G$ 组；**每一组共享一个 key 头与一个 value 头**。
- **GQA-$G$**：组数为 $G$。
- **GQA-1**（单组 → 单对 K/V）≡ **MQA**；**GQA-$H$**（组数等于头数）≡ **MHA**。

**共享键值的逻辑**：Query 侧仍保留多头，以便从不同「视角」去读上下文；Key/Value 侧则做**跨头（或跨组）复用**，直接砍掉必须缓存与加载的 K/V 份数。从 MHA 到 MQA，论文写明（§2.2）：

> Going from MHA to MQA reduces $H$ key and value heads to a single key and value head, **reducing the size of the key-value cache … by a factor of $H$**.

### 2.2 为何不止于 MQA：插值与大模型比例

只做 MQA 有两层代价（§1、§2.2）：

1. **容量砍得太狠**：大模型通常会**加大头数**，于是「$H\to 1$」相对容量与带宽的削减更激进。
2. **分片浪费**：大模型常用张量并行等分片时，**单个** K/V 头往往被复制到各 partition（论文引 Pope et al., 2022）；GQA 用多个 K/V 头可以减轻这类浪费。

因此 GQA 的设计意图是：**在质量与速度之间插值**——中间组数比 MQA 质量高、比 MHA 更快；并让「带宽/容量削减比例」在模型变大、头数变多时仍可控制（§2.2）。

**作用范围**：论文明确 **GQA 不用于 encoder 自注意力**（encoder 并行算完，memory bandwidth 通常不是主瓶颈）；实验里 MQA/GQA 加在 **decoder 自注意力与 cross-attention**（§3.1）。

### 2.3 另一条贡献：从 MHA checkpoint「uptrain」到 MQA/GQA

除提出 GQA 外，论文给出实用配方（摘要、§2.1）：

1. **转换 checkpoint**：把各头的 K、V 投影矩阵 **mean-pool** 成目标结构所需的头（MQA 合成 1 头；GQA 按组内 mean-pool）。消融显示 mean-pool 优于「只留第一头」或「随机初始化」（Figure 4）。
2. **继续预训练一小段**：在同一套预训练配方上再训原步数的比例 $\alpha$；主实验取 **$\alpha=0.05$（5%）**，约 600 TPUv3 chip-days（§3.1）。

动机：不必为「要质量」和「要速度」各训一个完整模型；可用少量算力把已有 MHA 权重迁到多查询族。

### 2.4 实验取舍（仅报告文中数字，不外推）

主结果（Table 1，T5.1.1，XXL 上 5% uptrain；时间单位为文中 *Time per sample*，TPUv4）：

| 模型 | $T_{\mathrm{infer}}$ (s) | Average |
|------|----------------------------|---------|
| MHA-Large | 0.37 | 46.0 |
| MHA-XXL | 1.51 | 47.2 |
| MQA-XXL（uptrain） | 0.24 | 46.6 |
| **GQA-8-XXL（uptrain）** | **0.28** | **47.1** |

解读与文中一致（§3.2 / Figure 3）：uptrained MQA 已相对 MHA-Large 更快且平均分更高；**GQA-8 速度接近 MQA，平均质量接近 MHA-XXL**。组数消融（Figure 6）：从 1（MQA）增到 8 组，推理开销增加有限；再往 MHA 方向加组，代价上升。作者选 **8 组**作折中。

**稳定性**（Appendix A）：从零训的 MQA 在预训练易尖峰、长输入微调易发散；uptrained MQA 仍方差大；**uptrained GQA 在其实验中表现稳定**。

**论文自述局限**（Limitations）：Rouge 等指标不完整；未与「从头训练的 XXL GQA」对比；实验主要在 **encoder–decoder**；作者预期在 **decoder-only**（无独立 cross-attn）上 GQA 相对 MQA 的优势可能更明显——此为文中推测，非其主表实证。

---

## 三、MLA（DeepSeek）：低秩联合压缩思想（以 V3 报告为准）

### 3.1 定位：不是「再少几个 KV 头」，而是「先压成低维再展开」

V3 报告 §2.1.1 开宗明义：DeepSeek-V3 的注意力采用 **MLA**；并写明其核心是：

> the **low-rank joint compression** for attention keys and values to reduce Key-Value (KV) cache during inference.

与 GQA「减少 K/V **头的个数**」不同，MLA 把每个 token 的 K/V 信息先压进一个**共享的低维潜向量**，推理时主要缓存这个紧凑表示（外加解耦的 RoPE 键），需要时再 **up-project** 回多头 K/V。报告称该设计在 DeepSeek-V2 已充分验证，V3 继续采用（§2.1）。

符号（报告原文）：嵌入维 $d$，头数 $n_h$，每头维 $d_h$；第 $t$ 个 token 的层输入 $\mathbf{h}_t\in\mathbb{R}^d$。

### 3.2 KV 侧：联合下投影 + 上投影 + 解耦 RoPE

报告给出（式 (1)–(5)）：

$$
\mathbf{c}_t^{KV} = W^{DKV}\mathbf{h}_t
$$

$$
[\mathbf{k}_{t,1}^{C};\ldots;\mathbf{k}_{t,n_h}^{C}] = \mathbf{k}_t^{C} = W^{UK}\mathbf{c}_t^{KV}
$$

$$
\mathbf{k}_t^{R} = \mathrm{RoPE}(W^{KR}\mathbf{h}_t)
$$

$$
\mathbf{k}_{t,i} = [\mathbf{k}_{t,i}^{C};\,\mathbf{k}_t^{R}]
$$

$$
[\mathbf{v}_{t,1}^{C};\ldots;\mathbf{v}_{t,n_h}^{C}] = \mathbf{v}_t^{C} = W^{UV}\mathbf{c}_t^{KV}
$$

要点（据报告文字与式注）：

- $\mathbf{c}_t^{KV}\in\mathbb{R}^{d_c}$ 是 K 与 V **共用**的压缩潜向量；$d_c\ll d_h n_h$。
- $W^{DKV}$ 下投影；$W^{UK},W^{UV}$ 分别上投影出多头 compressed keys / values。
- **位置信息**：另用 $W^{KR}$ 产生**解耦**的 RoPE key $\mathbf{k}_t^{R}$，再与各头的 $\mathbf{k}_{t,i}^{C}$ 拼接成最终 key。这是为了在低秩压缩设定下仍能注入旋转位置编码（报告引 Su et al., 2024）。
- **推理缓存**：报告强调生成时只需缓存图中蓝框向量——即 **$\mathbf{c}_t^{KV}$ 与 $\mathbf{k}_t^{R}$**——从而显著减小 KV cache，并称性能可与标准 MHA 相当（§2.1.1）。

### 3.3 Query 侧：同样低秩压缩（主为训练激活显存）

式 (6)–(9)：先 $W^{DQ}$ 得到 $\mathbf{c}_t^{Q}$，再上投影出 compressed queries，并对 RoPE 分支做解耦；最终 $\mathbf{q}_{t,i}=[\mathbf{q}_{t,i}^{C};\,\mathbf{q}_{t,i}^{R}]$。报告写明 query 压缩的目的是 **reduce the activation memory during training**（与 KV 压缩服务推理缓存是不同目标）。

注意力输出仍是标准多头加权（式 (10)–(11)），softmax 缩放维为 $\sqrt{d_h+d_h^{R}}$（因 key/query 拼接了 RoPE 维）。

### 3.4 V3 中的 MLA 超参（§4.2，可核对规模直觉）

报告给出 DeepSeek-V3 配置：

- $n_h=128$，$d_h=128$
- KV 压缩维 $d_c=512$；query 压缩维 $d_c'=1536$
- 解耦 RoPE 每头维 $d_h^{R}=64$
- 另：压缩潜向量后接额外 RMSNorm，并在宽度瓶颈处乘额外缩放因子（与 DeepSeek-V2 相同做法）

**架构思想一句话**：GQA 族通过「**少存几份完整头维的 K/V**」省缓存；MLA 通过「**每 token 只存低维联合潜码（+短 RoPE key），用时再展开成多头**」省缓存，并试图用低秩结构保住接近 MHA 的表达。

> **边界说明（待核实）**：V3 报告对 MLA **复述机制与超参**，并声明性能可比 MHA；**未在本文展开**与 MHA/GQA 的逐项消融表或逐层 KV 字节对比。更细的 MLA 消融与动机展开在 DeepSeek-V2 技术报告（文中引用 DeepSeek-AI, 2024c）。本笔记不把 V2 未读章节中的数字写进来。

---

## 四、数学辅线：头数 / 组数与 KV cache 规模的直觉关系

以下只建立**数量级直觉**，帮助跟读「为何改接线能省显存」；具体实现还会受 dtype、分页、是否存 RoPE 前后、实现是否吸收投影等影响。

### 4.1 按「每层、每 token」计的 K/V 驻留规模（示意）

设每头内容维为 $d_h$，K 与 V 都缓存：

| 机制 | 需缓存的「头份数」直觉 | 每层每 token 量级（示意） |
|------|------------------------|---------------------------|
| MHA | $H$ 份 K + $H$ 份 V | $\propto 2\,H\,d_h$ |
| GQA | $G$ 份 K + $G$ 份 V | $\propto 2\,G\,d_h$ |
| MQA | 1 份 K + 1 份 V | $\propto 2\,d_h$ |
| MLA（V3 表述） | 潜向量 $\mathbf{c}^{KV}$ + 解耦 $\mathbf{k}^{R}$ | $\propto d_c + d_h^{R}$（报告：此二者需缓存） |

因此：

- **MHA → MQA**：cache 体量约除以 $H$（GQA 论文原句）。
- **MHA → GQA**：约除以 $H/G$（或说变为 MHA 的 $G/H$）。
- **组数旋钮**：$G$ 从 1 调到 $H$，在「最省」与「最满配」之间滑动——这就是 GQA「插值」的数学含义。

### 4.2 代入 V3 超参做对照（仅算术，非报告对比表）

若用同一套 $n_h=128,\,d_h=128$ 想象「若是满配 MHA」：每层每 token 约 $2\times 128\times 128=32768$ 个数。
按报告「只缓存 $\mathbf{c}^{KV}$ 与 $\mathbf{k}^{R}$」：$d_c+d_h^{R}=512+64=576$ 个数。
比值约 $32768/576\approx 57\times$ 量级——**说明「联合低秩压缩」相对满配多头缓存可以非常省**；但这是对报告缓存声明的直接算术，**不是** V3 文中给出的官方加速比，也未计入实现细节。

若想象 GQA 取 $G=8$、仍用 $d_h=128$：约 $2\times 8\times 128=2048$ 个数/层/token，介于 MQA（$2\times 128$）与 MHA（$32768$）之间——与 GQA「插值」叙事一致。

### 4.3 和「算力」不是同一回事

- **Prefill（预填充）**：往往算力更重；KV 写入一次后供后续复用。
- **Decode**：每步小算力、反复读 KV → **带宽与显存**更致命。

GQA 论文还提醒：更大模型上，KV cache 随模型维近似线性，而 FLOPs/参数随维平方增长，故「注意力带宽」相对权重计算的比重会变化（§2.2）——这也是为何「绝对最优 $G$」会随规模漂移，需要经验折中（其选 GQA-8）。

### 4.4 MLA 拼接维上的一点形式细节

最终注意力 logits 使用拼接后的 q/k，缩放分为 $\sqrt{d_h+d_h^{R}}$（式 (10)）。直觉上：RoPE 通道与 content 通道维数相加后，再做标准缩放点积——跟读时不要误用「只按 $d_h$ 缩放」。

---

## 五、常见误区与引用

### 5.1 常见误区

1. **「MQA/GQA 改的是注意力公式」**
 误。缩放点积形式未变；变的是 **K/V 是否跨 query 头共享**（以及由此少存多少 cache）。

2. **「GQA 一定全面强于 MQA」**
 在 GQA 论文的 T5 uptrain 设定下，GQA-8 平均质量更接近 MHA-XXL、速度接近 MQA；但最优 $G$、是否 from-scratch，文中并未穷尽，且 Limitations 提醒指标与设定边界。

3. **「MLA = 一种 GQA」**
 误。GQA 减少的是 **KV 头个数**；MLA 是对 K/V（及训练时 Q）做 **低秩联合压缩 + 推理时缓存潜向量与解耦 RoPE key**。二者同属「降 KV 代价」，机制不同。

4. **「V3 报告里有完整的 MLA vs GQA 对比表」**
 就本文所读 §2.1.1 / §4.2 而言：**没有**展开该对比表；MLA 细节与验证指向 DeepSeek-V2。勿把社区二手表当成 V3 原文。

5. **「KV cache 公式可以忽略 RoPE / 实现吸收」**
 报告明确 MLA 还要缓存 $\mathbf{k}^{R}$；实现若把部分投影吸收进矩阵，字节数会变。第四节算术只用于直觉。

6. **「Encoder 也必须上 GQA」**
 GQA 论文明确未对 encoder self-attention 使用 GQA，理由是 encoder 并行计算时带宽通常非主瓶颈。

### 5.2 引用（跟读用）

- Ainslie, J., Lee-Thorp, J., de Jong, M., Zemlyanskiy, Y., Lebrón, F., & Sanghai, S. (2023). *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*. arXiv:2305.13245. PDF: `https://arxiv.org/abs/2305.13245`
- DeepSeek-AI. (2024/2025). *DeepSeek-V3 Technical Report*. arXiv:2412.19437. §2.1.1 MLA；§4.2 超参。PDF: `https://arxiv.org/abs/2412.19437`
- Shazeer, N. (2019). *Fast Transformer Decoding: One Write-Head Is All You Need*. arXiv:1911.02150.（MQA 源头，经 GQA 论文引用）
- Vaswani, A., et al. (2017). *Attention Is All You Need*.（标准 MHA）
- DeepSeek-AI. (2024). DeepSeek-V2 技术报告（V3 文中作 DeepSeek-AI, 2024c）——**MLA 原始验证与更细消融；本笔记未展开精读**。

### 5.3 待核实 / 后续可补

- [ ] 精读 DeepSeek-V2 中 MLA 专章：与 MHA/GQA 的消融、缓存字节表、训练稳定性叙述。
- [ ] MQA 原始论文（Shazeer 2019）中的「one write-head」表述与实现约束。
- [ ] 当代 decoder-only 开源模型（LLaMA 等）默认 GQA 组数与推理栈中的具体 KV layout（非本两篇正文范围）。
- [ ] V3 实现是否在推理中吸收 $W^{UK}/W^{UV}$ 等（影响「576 维」直觉是否等于实际存储）。

---

*草稿状态：draft。架构主线据 GQA 全文 + V3 §2.1.1；数学辅线为 cache 规模直觉，算术示例已标明非官方对比表。*

## 相关笔记

### P0
- [[注意力与Transformer核心思想|Attention / Transformer]]
- [[DecoderOnly与GPT路线|Decoder-only / GPT]]
- [[规模定律与预训练范式|规模定律与预训练]]
- [[混合专家架构|MoE / 稀疏激活]]
- [[对齐脉络RLHF与偏好优化|对齐 RLHF / DPO]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿模型谱系]]

### P1
- [[长上下文位置编码与系统侧|长上下文]]
- [[多模态架构脉络|多模态]]
- [[AI基础设施总览|AI Infra]]
- [[注意力效率族MQA到MLA|注意力效率]]
- [[LLaMA开源生态里程碑|LLaMA 生态]]


