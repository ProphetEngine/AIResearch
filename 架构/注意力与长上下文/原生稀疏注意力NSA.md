---
title: "原生稀疏注意力（NSA）"
topic: 原生稀疏注意力NSA
date: 2026-09-24
lines: [架构思想, AI Infra]
status: archived
sources:
  - https://arxiv.org/abs/2502.11089
arxiv: ["2502.11089"]
related:
  - "注意力效率族MQA到MLA"
  - "DeepSeekV32技术报告深读"
  - "长上下文与注意力效率时间线"
  - "检索式注意力"
retrieval_cutoff: 2026-09-24
timezone: Asia/Shanghai (CST)
archived: 2026-09-24
---

# 原生稀疏注意力（NSA）

> **定位**：可端到端训练、且与现代 GPU / GQA 内存访问对齐的 **原生稀疏注意力** 入口。主文 Yuan、Gao、Dai 等（DeepSeek-AI / 北大），*Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention*（arXiv:2502.11089）。
> **边界**：相对 [[注意力效率族MQA到MLA]]，头压缩线止于 MLA；本篇另开「可训稀疏」入口，不重写 MQA/GQA/MLA 接线史。相对 [[DeepSeekV32技术报告深读]]，仅交叉一句 DSA 系谱接口，不重写 V3.2 后训练、GRPO 或 agent 合成。相对 [[检索式注意力]]：后者多为推理期 / training-free 检索近似；NSA 把稀疏写进预训练计算图。

---

## 一、动机：可训稀疏 vs 推理期稀疏

长上下文下，softmax 全注意力的时延随序列长度急剧上升；文中估计 64k 解码时注意力可占端到端时延约 70–80%（§1）。利用注意力固有稀疏性是自然方向，但既有路线多把稀疏 **只加在推理**：保留 Full Attention 预训练骨干，再做 KV 驱逐、分块选择或哈希/聚类选 token（H2O、Quest、InfLLM、ClusterKV、MagicPIG、HashAttention 等，§1–§2）。

文中把缺口收成两点（§2）：

1. **推理加速的「幻觉」**：稀疏常只覆盖 prefill 或 decode 其一（相位受限）；或与 GQA/MQA 的「组内共享 KV」冲突——各头独立选块时，组内 KV 加载量变成并集，理论算力稀疏难换真实带宽收益。
2. **可训稀疏的「神话」**：事后剪枝偏离预训练轨迹（如 top-20% 注意力仅覆盖约 70% 分数的叙述，§2.2）；离散聚类 / SimHash 切断计算图；token 级散乱访问又难接 FlashAttention 式分块反传。

因此 NSA 的主张是：**稀疏必须原生进入训练**，并在算法层就按 Tensor Core、连续块访存与算术强度来设计，使加速覆盖训练前向/反向、prefill 与 decode（摘要；§2.3）。

---

## 二、机制：三路层次稀疏与硬件对齐

对查询 $\mathbf{q}_t$，NSA 不直接对全体 $\mathbf{k}_{:t},\mathbf{v}_{:t}$ 做全注意力，而构造更紧凑的 $\tilde{K}_t,\tilde{V}_t$，再按门控聚合多条支路（§3.2，式 3–5）：

$$
\mathbf{o}^{*}_{t}=\sum_{c\in\{\mathrm{cmp},\mathrm{slc},\mathrm{win}\}} g_{t}^{c}\cdot\mathrm{Attn}(\mathbf{q}_{t},\tilde{K}_{t}^{c},\tilde{V}_{t}^{c}),
\quad N_{t}\ll t.
$$

门控 $g_t^c$ 由输入经 MLP + sigmoid 得到。三支路（Figure 2；§3.3）：

| 支路 | 作用 | 要点 |
|---|---|---|
| **压缩（cmp）** | 粗粒度全局 | 长度 $l$、步长 $d$ 的块经可学习 MLP $\varphi$（含块内位置编码）压成单个压缩 KV；通常 $d<l$ 减轻信息碎片（式 7） |
| **选择（slc）** | 细粒度重要块 | **块级** top-$n$ 选择（利于连续访存与 Tensor Core）；重要性由压缩支路的 softmax 分数诱导，并可按块划分关系汇总（式 8–9）；GQA/MQA 下组内各头分数求和，保证 **同组同选块**，避免并集加载（式 10–12） |
| **滑窗（win）** | 局部上下文 | 独立窗口 $w$ 的近邻 KV；与压缩/选择 **分支出、分 KV**，再门控融合，减轻局部模式短路长程支路（§3.3.3） |

**内核要点（§3.4）**：压缩与滑窗可接 FlashAttention-2；选择支路在 Triton 上按 **GQA 组**装载同位置全部 query 头及其共享稀疏 KV 块索引，内层顺序取连续 KV 块进 SRAM，外层用 grid 调度——对齐算术强度，消冗余 KV 搬运。目标架构是共享 KV 的 GQA/MQA，而非访存更重的纯 MHA。

主实验超参（§4.1）：$l=32$，$d=16$，$l'=64$，$n=16$（含固定激活 1 个初始块与 2 个局部块），$w=512$。

---

## 三、训练与效率证据

**骨干**：GQA + DeepSeekMoE，总参约 **27B**、激活约 **3B**；30 层、隐维 2560；GQA 组数 4、共 64 头；$d_q=d_k=192$，$d_v=128$；MoE 为 72 路由 + 2 共享、top-6（§4.1）。

**训练日程**：在约 **270B** token 的 8k 文本上预训练（摘要写作 260B；§4.1 写 270B），再以 YaRN 做 32k 继续训与 SFT；与 Full Attention 对照训至收敛。预训练损失曲线上 NSA 不低于对照（Figure 4）。

**能力（论文表数字，非外推）**：

| 轴 | 结果（相对 Full Attention） |
|---|---|
| 通识套件平均（Table 1） | NSA **0.456** vs Full **0.443**（9 项中 7 项更高） |
| LongBench 子集平均（Table 2） | NSA **0.469** vs Full **0.437**；亦高于 H2O / InfLLM / Quest / Exact-Top（各方法在约 2560 激活 token 预算下对齐稀疏度） |
| 64k Needle-in-a-Haystack | 文称各位置检索准确率完美（Figure 5） |
| AIME24（R1 蒸馏 10B×32k SFT 后，Table 3） | 8k 生成限：NSA-R **0.121** vs Full-R **0.046**；16k：**0.146** vs **0.092** |

**效率（A100 ×8；Triton NSA vs Triton FlashAttention-2；§5）**：64k 上下文前向最高约 **9×**、反向约 **6×**；解码侧按 KV 加载量估计，64k 期望加速约 **11.6×**（Table 4：Full 加载 65536 token 等价量，NSA 5632）。加速随长度增大而更明显（Figure 6）。

---

## 四、与 MLA 通史、V3.2 DSA 的接口

- **[[注意力效率族MQA到MLA]]** 主线是 **减少须驻留与反复加载的 K/V 表示**（MHA→MQA→GQA→MLA 潜空间压缩）。NSA **假定** 已采用 GQA/MQA 类共享 KV，再在「算哪些位置」上做可训层次稀疏；二者正交：MLA 压表示维，NSA 压注意力支撑集。
- **[[DeepSeekV32技术报告深读]]** 中的 **DSA**（lightning indexer + top-$k$、挂 MLA 的 MQA 模式）同属 DeepSeek 系「稀疏注意力继续训」叙事；机制细节、两阶段继续训与后训练增量以该卡为准，本篇不展开。

时间线增量挂点见 [[长上下文与注意力效率时间线]]；推理期检索式近似对照见 [[检索式注意力]]。

---

## 五、局限与开放问题

1. **选择仍含离散 top-$n$**：重要性虽由压缩注意力可微分数诱导，最终块选择仍是排序截断；与「全程光滑可微选 token」仍有差距（§3.3.2；§6 对辅助损失 / 启发打分替代方案的失败经验）。
2. **实现绑定块结构与 GQA**：收益依赖连续块访存与组内同选；换纯 MHA 或强 token 级散乱选择，文中论证的内核优势可能削弱（§2.1、§3.4）。
3. **证据尺度**：主结果来自约 27B/3B 激活骨干与给定稀疏预算；更大规模、与 MLA 同栈联合、或与生产 serving 栈端到端对照，正文未给出。
4. **对照范围**：通识评测主要对 Full Attention；长上下文才系统对比推理期稀疏法。推理期方法本身多不可训，公平性依赖「同激活 token 预算」设定（§4.2）。

---

## 六、文献

| 文献 | 角色 |
|---|---|
| Yuan, Gao, Dai, et al., *Native Sparse Attention: Hardware-Aligned and Natively Trainable Sparse Attention*. arXiv:2502.11089. https://arxiv.org/abs/2502.11089 | **主文献** |
| Ainslie et al., GQA. https://arxiv.org/abs/2305.13245 | 共享 KV 前提；见 [[注意力效率族MQA到MLA]] |
| DeepSeek-AI, *DeepSeek-V3.2 Technical Report*. https://arxiv.org/abs/2512.02556 | DSA 产品化交叉；见 [[DeepSeekV32技术报告深读]] |
| Tang et al., Quest; Xiao et al., InfLLM; Zhang et al., H2O 等 | 推理期稀疏对照（正文 §4.2、§7） |
