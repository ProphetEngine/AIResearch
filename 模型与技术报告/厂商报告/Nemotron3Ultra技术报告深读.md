---
title: Nemotron 3 Ultra 技术报告深读
topic: Nemotron3Ultra技术报告深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2606.15007
aux:
 - https://arxiv.org/abs/2606.15007
 - https://github.com/NVIDIA-NeMo/Nemotron
 - https://github.com/NVIDIA-NeMo/Evaluator/blob/main/examples/nemotron/nemotron-3-ultra
 - https://github.com/NVIDIA-NeMo/Gym
 - https://github.com/NVIDIA-NeMo/Skills
arxiv: ["2606.15007"]
related: ["NemotronCC数据策展", "SEA-LION低资源区域模型", "OLMo3全栈开放配方", "MTP训练范式", "混合专家架构", "混合Mamba与注意力架构设计菜谱", "线性注意力与状态空间模型谱系", "OnPolicy蒸馏OPD范式", "KimiK3技术报告"]
retrieval_cutoff: 2026-06-12
timezone: Asia/Shanghai (CST)
---

# Nemotron 3 Ultra 技术报告深读

> **主要来源**：[Nemotron 3 Ultra: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning](https://arxiv.org/abs/2606.15007)（NVIDIA，v1，2026-06-12）；[Nemotron 配方仓库](https://github.com/NVIDIA-NeMo/Nemotron) 与 [评测示例](https://github.com/NVIDIA-NeMo/Evaluator/blob/main/examples/nemotron/nemotron-3-ultra)（报告所附代码地址）（截至 2026-06-12）。仓库页不引事实，不计入截至。
> **研究线**：架构思想（主：混合 Mamba–注意力加 LatentMoE、NVFP4 预训练、多教师 on-policy 蒸馏）；评测字段（辅：Base 与后训练主表）
> **范围与相邻笔记**：
> - ≠ [[NemotronCC数据策展]]：网页语料的过滤、去重与合成改写在那篇，本篇只记 Ultra 新增的数据集与两阶段配比。
> - ≠ [[SEA-LION低资源区域模型]]：区域持续预训练与评测在那篇，本篇是基座旗舰报告。
> - ≠ [[OLMo3全栈开放配方]]：完全开放的研究配方在那篇，本篇写工业开放权重旗舰。
>
> **意义**：Nemotron 3 Ultra 是 NVIDIA Nemotron 3 家族中最大的模型，550B 总参、每 token 激活 55B，沿用 Nemotron 3 Super 的混合 Mamba–注意力 MoE 架构（§2.1），在 20T token 上以 NVFP4 预训练，并扩展到 1M 上下文。后训练的核心改动是多教师 on-policy 蒸馏（MOPD）：十多个领域教师经两轮蒸馏合进一个学生。报告称它在 8K 输入、64K 输出设置下的推理吞吐最高约为同类开放模型的 6 倍，精度持平（摘要）。

## 一、问题背景

报告把目标定为面向智能体推理的开放模型（§1）。智能体任务输出长、调用多，解码阶段的吞吐和 KV 缓存成为主要成本；纯注意力 MoE 在长输出上代价高。Ultra 用 Mamba 层替代大部分注意力层以降低注意力成本与 KV 缓存占用，用 LatentMoE 控制专家通信，用共享权重的 MTP 头做投机解码。后训练方面，报告说明多个领域教师与学生并行开发、各自走不同的 SFT 管线，直接合并效果差，这是引入 MOPD 预热与两轮蒸馏的原因（§3.3.3）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2025-12 | [NVIDIA Nemotron 3](https://arxiv.org/abs/2512.20856) | Nemotron 3 家族的总报告 |
| 2026-01 | [LatentMoE](https://arxiv.org/abs/2601.18089) | 路由专家在窄潜空间计算，Super 与 Ultra 的 MoE 层采用 |
| 2026-04 | [Nemotron 3 Super](https://arxiv.org/abs/2604.12374) | 混合 Mamba–注意力 MoE、NVFP4 预训练与共享 MTP 头，Ultra 的直接前代 |
| 2026-06 | [Nemotron 3 Ultra](https://arxiv.org/abs/2606.15007) | 扩到 550B、两轮 MOPD、MTP Boosting |

## 三、核心机制：架构与预训练（§2）

### 3.1 架构（§2.1、Table 1）

Ultra 与 Super 同为混合 Mamba–注意力 MoE，MoE 层用 LatentMoE；预训练带两个共享参数的 MTP 头，每个由一层注意力加一层 MoE 组成，用于自回归起草。

| 配置 | 值 |
|---|---|
| 总层数 | 108 |
| 模型维度 | 8192 |
| Q 头 / KV 头 / 头维度 | 64 / 2 / 128 |
| Mamba 状态维度 / 组数 / 头数 / 头维度 | 128 / 8 / 256 / 64 |
| 专家隐藏维度 / 共享专家中间维度 | 5120 / 10240 |
| 每层专家数 / 激活数 | 512 / 22 |
| MoE 潜空间宽度 | 2048 |
| 共享权重 MTP 层 | 2 |

层的交错方式只在 Figure 2 中给出，正文没有写成公式，本篇不读图。

### 3.2 NVFP4 预训练（§2.2、§2.7）

1. **精度配方**：沿用 Super 的 NVFP4 配方；网络最后 15%（16 层）、Mamba 输出投影、潜空间投影、QKV 与注意力投影、MTP 与嵌入层保持更高精度。报告称这是迄今规模最大的稳定、准确的 NVFP4 训练演示。
2. **对照**：从 5T、10T、16T 检查点分出切到 BF16 的消融，相对训练损失差平均低于 0.4%。
3. **两次发散**：预训练中出现两次损失发散。用原有的 FP32 梯度归约配方从发散前的检查点回滚，仍然发散；第二次在约 15T token 处，回退到发散前检查点后提前退火学习率（§2.7）。报告未给出确定的根因。

### 3.3 数据与课表（§2.3–§2.5）

1. **新增数据集**：Nemotron-Pretraining-Code-v3 新增 173B token 的 GitHub 代码，截止 2025 年 9 月 30 日；Nemotron-Pretraining-Legal-v1 是法律合成数据，报告称加入 Nemotron 3 Nano 预训练后代理 LegalBench 平均准确率从 64.6 升到 74.7。
2. **日程**：共 20T 文本 token；学习率在 200B token 内预热到 2.5×10⁻⁴，最后 5T token 按 minus-sqrt 衰减到 2.5×10⁻⁶。数据分两阶段混合，阶段一偏多样性，阶段二偏高质量。
3. **长上下文持续预训练**（§2.5）：长上下文数据占 46%、阶段二数据占 54%，不混入 RULER 式数据；92% 的迭代用 1,048,576（1M）长度，其余 8% 用 4,096（4K）。

## 四、核心机制：后训练（§3）

### 4.1 管线

SFT（两阶段，带共享权重 MTP 辅助损失，系数 0.1）→ 统一 RLVR（推理、智能体、代码、安全、可用性、对话环境）→ MOPD 预热 → 两轮 MOPD → MTP Boosting。报告称并行训练了十多个领域专家教师，其中智能体教师走独立的智能体 SFT 路径。安全数据沿用 Super 的 45K 混合，再翻译为德、西、法、日、意、中六种语言。

### 4.2 MOPD（§3.3）

1. **目标**：学生在自己生成的前缀上匹配对应领域的教师，完全 on-policy 时等价于最大化负的反向 KL（式 1）；按领域加权，异步执行。
2. **预热是关键**：教师与学生用不同 SFT 数据训练时，学生的轨迹对教师是分布外的，监督信号变差。做法是先在教师训练分布上对学生做很轻的 SFT。Table 4：GDPVal 上学生起点 28.9，加预热后 MOPD 到 46.7，不加预热只有 35.3。
3. **结果**（Table 5，RLVR → MOPD2）：Terminal Bench 2.0 从 44.5 到 54.0（教师 50.0，恢复率 172.7%）；SWE-Bench Verified 从 65.8 到 71.7；TauBench Telecom 从 82.7 到 92.9；HLE（不用工具）从 25.6 到 26.7。恢复率定义为（MOPD2 − RLVR）/（教师 − RLVR）。
4. **报告的解释**：教师的优势能表达为学生已能采到的轨迹上的 token 级偏好时（工具调用、环境交互、弃答、多步执行），MOPD 最有效；HLE 增益小，是因为通用推理教师的优势来自学生没见过的额外离策略数据，而不只是对学生轨迹的不同偏好（§3.3.4）。

### 4.3 MTP Boosting 与推理强度（§3.4–§3.5）

MTP 头在所有训练阶段都参与训练；共享头按多步递归使用，起草长度增加不需要额外参数。Boosting 阶段专门处理教师强制训练与自回归推理之间的不一致。推理分为关闭、常规、中等强度三档，后两档可叠加推理时预算控制；报告称在 AA Index V4 的 10 个任务上，中等强度平均比常规少用约 2.5X 的 token，准确率下降约 7%（§3.5）。

## 五、主要结果

1. **Base**（Table 2）：MMLU-Pro 79.07、GPQA 50.00、MATH 82.00、HumanEval 83.84、MBPP-Sanitized 85.97；RULER 64K / 128K / 1M 为 95.30 / 92.49 / 76.83。GSM8K 为 88.10，低于表中 Mistral-Large-3 的 91.21 与 Kimi-K2 的 91.05。
2. **后训练**（Table 10）：Terminal Bench 2.1 为 56.4，GDPVal 46.7，SWE-Bench Verified 70.7，PinchBench 90.0，TauBench V3 平均 70.9，BrowseComp 44.4，GPQA（不用工具）87.0，RULER（1M）94.7。报告把 PinchBench 与 ProfBench 作为留出的泛化关口，开发期间不用于监控与选点（§3.7）。
3. **吞吐**（§1、Figure 1）：8K 输入、64K 输出设置下，相对 GLM-5.1、Kimi-K2.6、Qwen-3.5 分别为 5.9 倍、4.8 倍、1.6 倍。
4. **推理侧取舍**（§5）：解码为主的设置下 Ultra 领先 Qwen-3.5；预填充为主时落后，报告称 Ultra 相对 Qwen-3.5-397B-17B 有约 3.2 倍的 FLOPs 劣势（55B 对 17B 激活）。小批量时长起草更利于延迟，大批量时缩短起草或关掉 MTP 往往吞吐更高。

## 六、意义

1. **混合 Mamba–注意力进入 500B 级开放旗舰**：Ultra 把 Super 的架构放大，并把吞吐优势明确限定在解码为主的场景，预填充为主时承认落后。
2. **多教师蒸馏取代继续叠 RL 阶段**：报告给出 MOPD 何时有效、何时无效的判断，预热步骤处理教师与学生分布不一致的问题。
3. **NVFP4 预训练的规模化证据**：从多个检查点切 BF16 对照，同时记录了两次发散及处理办法。

## 七、局限与待核实

1. **吞吐口径**：摘要写「up to ∼6×」，结论写「5x」，Figure 1 给出 5.9、4.8、1.6 倍；Ultra 用 TRT-LLM，对照用 vLLM。引用时需标明出处句。
2. **发散根因**：§2.7 只记录现象与处理，没有确定根因。
3. **MOPD 的未解问题**：§3.3.5 列出 logit 匹配等未见收益的变体，报告说明这些不能当作方法无效的证据。
4. **数据比例与层交错**：阶段配比与层的交错方式主要在图中，本篇未录。
5. **两份 PDF**：NVIDIA 研究站另有一份同题报告，页眉日期为 2026-6-9，arXiv v1 提交于 2026-06-12。本篇以 arXiv v1 为准。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[NemotronCC数据策展]] | Ultra 预训练的数据集名称与两阶段配比，网页语料的处理在那篇 | Nemotron-CC 的清洗管线 |
| [[SEA-LION低资源区域模型]] | 那篇以 Ultra 为教师，本篇提供教师侧的配方与评测 | 区域持续预训练与评测 |
| [[OLMo3全栈开放配方]] | 同为开放模型，那篇是完全开放的研究配方，本篇是工业开放权重旗舰 | OLMo 3 的配方 |
| [[MTP训练范式]] | 共享权重 MTP 头与 MTP Boosting | MTP 训练通论 |
| [[混合专家架构]] | Ultra 的 512 专家、激活 22 的 LatentMoE 配置 | MoE 通史 |
| [[混合Mamba与注意力架构设计菜谱]] | 那篇给出同预算下的对照与 MoE 兼容性；本篇 Ultra 是一整套系统配方。 | 混合比例的消融 |
| [[线性注意力与状态空间模型谱系]] | Ultra 的 Mamba 层是那篇状态空间模型一支的工业节点 | 状态空间模型通史 |
| [[OnPolicy蒸馏OPD范式]] | 两轮 MOPD 与预热，归入多教师 on-policy 蒸馏 | OPD 的方法谱系 |
| [[KimiK3技术报告]] | 两篇同属 2026 年开放权重的混合注意力 MoE 旗舰报告，本篇不比较两者配方 | K3 的配方与结果 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Nemotron 3 Ultra arXiv（v1）](https://arxiv.org/abs/2606.15007v1) | §2.2 NVFP4、§3.3 MOPD、Table 10 完整评测、§5 推理分析 |
| 2 | [Nemotron 3 Super](https://arxiv.org/abs/2604.12374) | Ultra 沿用的架构与 NVFP4 配方 |
| 3 | [Nemotron 配方仓库](https://github.com/NVIDIA-NeMo/Nemotron) | 训练配方 |
| 4 | [NeMo Gym](https://github.com/NVIDIA-NeMo/Gym) | RL 环境 |
