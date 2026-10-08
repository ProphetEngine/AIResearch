---
title: On-Policy Distillation（OPD）范式
topic: OnPolicy蒸馏OPD范式
date: 2026-09-25
lines: [架构思想, 蒸馏目标]
status: archived
sources:
  - https://arxiv.org/abs/2604.00626
arxiv: ["2604.00626"]
related:
  - 上下文蒸馏
  - 合成对齐数据Magpie
  - GRPO与DAPO算法族
  - Nemotron3Ultra技术报告深读
github: https://github.com/nick7nlp/Awesome-LLM-On-Policy-Distillation
retrieval_cutoff: 2026-09-25
timezone: Asia/Shanghai (CST)
archived: 2026-09-28
---

# On-Policy Distillation（OPD）范式

## 本文范围 / 与相关笔记分工

本文把 **On-Policy Distillation（OPD，同策略蒸馏）** 写成训练横切范式：说明「学生自己采轨迹、教师在这些状态上给信号」如何区别于经典 off-policy 模仿，以及目标函数、信号来源、训练动态三条设计轴如何合读。主依据是 Song & Zheng 的综述 *A Survey of On-Policy Distillation for Large Language Models*（arXiv:2604.00626v4，2026；89 页）及配套索引仓 [Awesome-LLM-On-Policy-Distillation](https://github.com/nick7nlp/Awesome-LLM-On-Policy-Distillation)。

与库内相关笔记的分工如下：

| 笔记 | 本文只取 | 本文不展开 |
| --- | --- | --- |
| [[上下文蒸馏]] | 「条件行为可进参数」是相邻接口；OPCD / DiSC 属**上下文→参数** | Snell / OPCD / DiSC 配方与评测表 |
| [[合成对齐数据Magpie]] | 「偏好 / 指令数据从哪来」不属本范式 | Magpie / ActiveUltraFeedback 数据流水线 |
| [[GRPO与DAPO算法族]] / [[Nemotron3Ultra技术报告深读]] | OPD 与 KL 约束 RL、多教师后训的**一句交叉** | GRPO 损失推导；Nemotron 后训技术报告全文 |
| [[DeepSeekV4技术报告深读]] | 工业实例：V4 先按领域 SFT → GRPO 训出专家，再让学生在自身采样上以反向 KL 对齐超过 10 个教师，做多教师 OPD 合并，取代 V3.2 的混合 RL 合并阶段 | V4 架构与后训练全文 |

**范围与相邻笔记：** OPD ≠ [[上下文蒸馏]]（上下文内化）；OPD ≠ [[合成对齐数据Magpie]]（对齐数据合成）。

---

## 一、材料元信息

| 项 | 内容 |
| --- | --- |
| 题名 | *A Survey of On-Policy Distillation for Large Language Models* |
| 作者 / 机构 | Mingyang Song, Mao Zheng（Tencent，Large Language Model Department） |
| 版本 | arXiv:**2604.00626v4** \[cs.LG / cs.CL\]；published **2026-04-01**；updated **2026-06-18**（UTC）→ CST **2026-06-19 01:00** |
| 链接 | https://arxiv.org/abs/2604.00626 · https://arxiv.org/pdf/2604.00626 |
| 页数 | 89（letter） |
| 辅索引 | https://github.com/nick7nlp/Awesome-LLM-On-Policy-Distillation |

**一句话抓手：** off-policy 蒸馏让学生在**教师完美前缀**上模仿；OPD 让学生在**自己生成的轨迹**上接受教师反馈——把「一次性照抄」改成「边犯边纠」。

---

## 二、白话分界：教师轨迹 vs 学生自采样

| | Off-policy 教师轨迹蒸馏 | On-policy 学生自采样 + 教师信号 |
| --- | --- | --- |
| **轨迹从哪来** | 固定语料，或事先由教师生成的文本 | 训练时由学生当前策略 $p_\theta$ 滚动采样（可与少量真实前缀混合） |
| **每步条件什么** | 几乎总是**无错的教师前缀** | **学生自己刚写出的前缀**（含早期错误） |
| **推理时会怎样** | 训练态 ≠ 部署态 → 误差沿序列放大（综述引 DAgger：$O(\epsilon T^2)$） | 训练态贴近部署态 → 理论上可压到更接近线性 $O(\epsilon T)$（需教师在学生前缀上仍可信） |
| **在优化什么** | $\mathbb{E}_{y\sim\mathcal{D}}\sum_t D(\,p_T(\cdot\mid y_{<t})\,\|\,p_\theta\,)$ | $\mathbb{E}_{y\sim p_\theta}\sum_t D_f(\,p_T(\cdot\mid y_{<t}),\,p_\theta\,)$ |

综述定义（§2）：只要训练期望的外层采样来自**学生当前策略**（而非静态 $\mathcal{D}$ 或教师生成分布），该方法即属 on-policy。目标可写成 $f$-散度族在学生轨迹上的最小化：Forward KL（覆盖教师多峰，易在峰间「幻觉」）、Reverse KL（盯住少数峰，适合唯一正解任务）、JSD / $\alpha$-散度等折中。白话说：**轨迹谁采，决定训推是否同分布；散度怎么选，决定学生是「铺开学」还是「收窄学」。**

奠基代表：GKD（Agarwal et al., 2024）用 $\lambda$-混合在 off/on 之间拨档；MiniLLM（Gu et al., 2024）把序列级 Reverse KL 写成以教师 log-prob 为奖励的 REINFORCE；DistiLLM（Ko et al., 2024）用 skew KL 稳住数值。后续工作在此之上分出固定散度、按位置自适应散度、以及 RL 增强目标（如 G-OPD 把 OPD 写成稠密 KL 约束 RL，并允许 $\alpha>1$ 时的 reward extrapolation）。

---

## 三、对照表：跟读综述的四列读法

综述把方法收成三条设计轴（§3–§6）：**优化什么（目标）**、**信号从哪来（白盒 logits / 黑盒文本或分数 / 自蒸馏）**、**如何稳住动态（混合采样、课程、token 加权）**。下表用四列对照，便于一眼分清与 off-policy 的差别（据 §2–§3 与 Table 1 口径压缩，不堆消融）：

| 维度 | Off-policy KD / Seq-KD | OPD（综述口径） |
| --- | --- | --- |
| **轨迹来源** | 静态 $\mathcal{D}$ 或教师预先生成 | 学生 rollout；常见 $\pi_{\mathrm{mix}}=\lambda p_\theta+(1-\lambda)p_{\mathrm{data}}$ |
| **分布匹配** | 匹配教师态上的下一 token；部署时落在学生态 → exposure bias | 在学生将访问的状态上匹配教师反馈；训推状态分布对齐 |
| **典型损失族** | Token-KL / 教师序列 NLL（Seq-KD 近似） | $f$-散度（FKL / RKL / JSD / skew KL）；序列级 RKL+PG；自适应 FKL↔RKL；KD+奖励 / G-OPD 式 KL-RL |
| **适用场景** | 短序列、教师前缀质量高、算力紧（免反复 rollout） | 长链推理 / 代码 / agent 轨迹，早期一步错就整条塌；工业侧多教师合并与后训巩固 |

**信号侧速览（不展开方法百科）：** 白盒可做精确 token 散度；黑盒退到文本批判、标量分或偏好对；无外教师时用特权上下文或自对比做自蒸馏。失败侧综述点名 **flawed prefix trap**（学生早期写坏后，教师条件分布本身失准，硬匹配会伤训练）——故实践常保留 off-policy 冷启动、可靠度加权或信任域，而非「全程无条件 on-policy」。

---

## 四、与推理后训练的交叉（一句）

综述将标准 OPD 与稠密 **KL 约束 RL** 形式等价（G-OPD 等）；工业配方里，多教师 on-policy 蒸馏可嵌在推理后训管线中——例如 [[Nemotron3Ultra技术报告深读]] 的 **MOPD（Multi-teacher On-Policy Distillation）** 与综述所载 Nemotron-Cascade 2 / DeepSeek-V4 多教师 OPD 同属「学生 rollout + 教师稠密信号」族，细节见各 TR，本文不重写。

---

## 五、划界交叉：[[上下文蒸馏]] 不是 OPD

[[上下文蒸馏]]（Snell → OPCD / DiSC）回答的是：**把富提示 / 文档条件行为压进参数**，推理时可不再携带原上下文。OPCD 虽在损失上用「学生采样 + reverse KL」，但其主对象仍是**特权上下文内化**；综述亦将 OPCD 归在「行为型特权信息 / context distillation」分支，而非 OPD 范式本身的定义核。

对照口诀：

- **OPD**：轨迹策略是否 on-policy——学生采、教师评（能力迁移 / 训推对齐）。
- **上下文蒸馏**：条件是否卸掉——富教师条件 → 贫学生条件（上下文→参数）。

二者可技术交叠（同用 on-policy + RKL），议题边界不同；本卡不写 OPCD / DiSC 评测表。

---

## 六、小结

OPD 的范式内核是**把蒸馏期望搬到学生自己的生成分布上**，用教师（或自教师）反馈纠正部署态误差，而不是在静态教师轨迹上做单次模仿。读文献时优先问三句：轨迹谁采？信号白盒还是黑盒？散度固定、自适应还是 RL 增强？与 [[上下文蒸馏]]、[[合成对齐数据Magpie]] 的分工已在开篇钉死；与 KL-RL / 多教师后训的接口点到为止。
