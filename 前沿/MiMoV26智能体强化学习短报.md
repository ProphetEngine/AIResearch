---
date: 2026-09-23
status: archived
archived: 2026-09-23
topic: MiMoV26智能体强化学习短报
title: "MiMo-V2.6：Scaling RL Towards Self-Improvement（前沿短报）"
lines: [架构思想, AI Infra]
sources:
 blog: https://mimo.mi.com/docs/en-US/news/latest/v2-6
 pdf: https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL/resolve/main/MiMo_V2_6_technical_report.pdf
 alphaxiv: https://www.alphaxiv.org/abs/2609.mimo-scaling-reinforcement-learning
 hf_collection: https://huggingface.co/collections/XiaomiMiMo/mimo-v26
related: ["AgenticRL景观与能力模块", "GRPO与DAPO算法族", "ToRL工具集成强化学习", "代码智能体Harness史线", "KimiK3技术报告", "RL算力缩放与环境扩展"]
retrieval_cutoff: 2026-09-23
timezone: Asia/Shanghai (CST)
---

# MiMo-V2.6：Scaling RL Towards Self-Improvement（前沿短报）

> **主要来源**：Xiaomi MiMo Team，[MiMo-V2.6 技术报告](https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL/resolve/main/MiMo_V2_6_technical_report.pdf)；[MiMo-V2.6 发布页](https://mimo.mi.com/docs/en-US/news/latest/v2-6)（2026-09-22 更新；截至 2026-09-23）。下文「§x」指技术报告章节，「官博」指发布页。
> **研究线**：架构思想（RL 扩算力三轴、组内 agentic grader、multi-harness）· AI Infra（异步 partial rollout、控制面与数据面解耦）
> **范围与相邻笔记**：
> - ≠ [[AgenticRL景观与能力模块]]：本篇不写 Agentic RL 的能力模块地图与综述分类。
> - ≠ [[GRPO与DAPO算法族]]：本篇不写 GRPO 的目标函数与变体推导。
> **意义**：MiMo-V2.6 把「扩大 RL」从单纯堆算力拆成 batch 吞吐、环境与 harness 多样性、grader 算力三条可核对的轴，并为 grader 与 multi-harness 给出消融证据；同时开源约 7k 可验证环境、RL 代码与 9B 蒸馏基线，让同一配方可以在小模型上复现。

**一句话**：MiMo-V2.6 把 Agentic RL 写成「算力三维放大」：更大 batch、更多环境与 harness、更多 grader 算力，在一次混合任务 run 里完成 You-Only-RL-Once；开源约 7k 可验证环境与 Distill-9B 基线，便于社区复现同一套路。

## 一、背景与脉络

官博把 V2.6 定位为 RSI（recursive self-improvement）路线上的一步：在可验证的复杂任务上放大 RL 算力，让模型在持续探索与反馈中扩展能力边界。系列含 Pro 与 Flash 两个原生全模态模型，API 价格与 V2.5 系列相同；官博称 Flash 全面超过 MiMo-V2.5-Pro，Pro 在 AA Intelligence Index 得 46 分，超过 Kimi K3 与 Qwen3.8 Max，与 Claude Fable 5.1、GPT-6 Astra 仍有差距。

脉络上，Agentic RL 把模型当作长程、部分可观测环境中的可学习策略来优化，而不是只对单轮文本打分（见 [[AgenticRL景观与能力模块]]）。V2.6 是这条线落到生产规模的一个实例：技术报告关心的是 RL 算力往哪里加，答案是吞吐、环境与 harness、grader 三轴同时放大。

## 二、扩算力三轴

### 2.1 吞吐轴：大 batch 与异步 rollout

- **批次**：每步 1,568 个 prompt，组大小 G = 16，约 25K 条轨迹；每步 2.7B–3.7B tokens（约 110K–150K tokens/seq；§4.1、§5.1）；官博写每步 3.5～3.7B，并称支持 1M 上下文训练。
- **算法**：GRPO，用组内相对优势替代价值网络（算法见 [[GRPO与DAPO算法族]]）；生成与训练异步进行（partial rollout，staleness 4），采用 prompt-mean 聚合（§4.1、§5.1）。
- **域混合**：Code 68%、Aesthetic 13%、General tool 12%、Cyber 4%、Context following 3%（§5.1）。
- **稳定前置**：冻结 MoE router。官博的理由是抑制专家负载漂移；报告给出对照：router 可训时负载 CV 从 0.78 升到 2.0，冷专家从 0.5% 升到 22%（§5.4）。
- **成本**：Pro 的 RL 成本中 rollout 占 43.8%、训练 43.5%、grader 12.7%；RL 后训练花费 Pro 约 $2.6M、Flash 约 $0.9M（§4.1）。
- **Live 训练（官博）**：不到 6 天，Flash 与 Pro 各约 30 步，累计约 750k 条轨迹；训练任务平均通过率相对提升 25%（Flash）与 12%（Pro）。

### 2.2 信号轴：组内 agentic grader

二元测试只能判过与不过，分不出「都过测」的解孰优孰劣。报告因此在组内做 agentic grading（§4.3）：

- **GRS（离线）**：用于高通过率子集。离线对照多条 rollout，建立 solution 与 behavior 两类 rubric；训练时奖励为 $R_i = R_i^{\mathrm{test}} \cdot S_i^{\mathrm{sol}} \cdot S_i^{\mathrm{beh}}$，测试失败仍为 0。
- **GAR（在线）**：用于其余 code 任务。组内共享 workspace，经 SFT 训练的 grader 沿五个维度给通过测试的 patch 排序（方案适配、实现精度、最小改动、范围外副作用、代码风格）；确认 reward hacking 时把该样本奖励置 0 并重算组统计，从而把正优势从低质量的通过解挪到高质量的通过解。
- **消融**（Flash，仅 code，batch 128）：去掉 GAR 后轮数与长度飙升、通过率早早进入平台；保留 GAR 时通过率持续上升更久、长度增长更慢（§4.3.2，Fig.8）。
- **防 reward hacking（官博）**：覆盖奖励设计、对抗评测、异常检测与验证器交叉核验四个环节。

### 2.3 交互轴：multi-harness

- **动机**：harness 是包在模型外的 agent 循环（工程背景见 [[代码智能体Harness史线]]）。只用一个 harness，解题策略会绑死在其实现细节上；生产 harness（MiMo Code、Codex 等）的指令与工程包装多、落在奖励之外，信用分配差（§4.2.5）。
- **做法**：从同一个 minimal agent loop（system prompt、工具、上下文管理）派生可重组的 mini-harness，覆盖 Code、General、Visual、Cyber，训练时混用多个 harness。
- **证据**（DeepSWE v1.1）：4 个训练用 mini-harness 与 held-out 的 codex、claude code、mini-swe-agent 都随训练提升，held-out 平均 Pass@1 约从 50% 升到 66%，训练与测试 harness 的差距收窄（§5.3，Fig.10）。
- **Infra**：Harness Pool 负责多租户并发，Payload Porter 把控制面与数据面解耦，支撑大批次、多 harness 训练（§6.2）；官博另述统一轨迹表示，并稳定混合批次中各任务的样本比例。

## 三、开源与复现

报告 Table 5（§7.2；按 distinct task id 计的约数）：

| 域 | 任务族 | 约任务数 | 验证方式 |
|---|---|---:|---|
| Code | Software engineering | 3k | 可执行测试 |
| Cyber | Vulnerability reproduction | 1k | 规则检查 |
| General | Knowledge work | 1k | 基于 rubric 的评判 |
| Visual | Web development | 2k | 视觉评分 |
| 另列 | Music generation（支持 GRPO 实验） | 约 1k | 文中未单列 |

四类合计约 7k，与官博「7k+ high-quality RL task environments」一致。配套开源：

- MiMo-V2.6-Distill-Qwen-9B：在 Qwen3.5-9B 上 SFT，总计 77.4B tokens，其中计损失的 27.2B。
- 端到端 RL 框架：官博称基于 verl、uni-agent 与 mini-swe-agent。
- 轻量可组合的 mini-harness；开源链接见 [HF collection](https://huggingface.co/collections/XiaomiMiMo/mimo-v26)。

9B 模型在域内做 GRPO 后相对 SFT 基线 11 项评测全部上涨（Table 6 摘录）：SWE-bench Verified 61.1→66.2，MiMo Cyber (mini) 31.3→47.0，Terminal Bench 2.1 37.1→52.8，MiMo Visual Coding (mini) 64.0→72.4。

## 四、关键结果

- **DeepSWE v1.1**（avg@3）：Pro 58.4→72.6，Flash 48.7→65.7（§4.1）。
- **token 开销**：主 run 分数上涨常伴随总 token 上升（Fig.9）。

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[AgenticRL景观与能力模块]] | 所在研究线：Agentic RL 的 POMDP 框定；本篇是其「扩 batch × 多环境与 harness × grader」的生产规模实例 | 能力模块地图与综述代表方法 |
| [[GRPO与DAPO算法族]] | 算法背景：主 run 与 9B 实验所用 GRPO 的组相对优势 | 目标函数、DAPO 与 Dr.GRPO 变体 |
| [[ToRL工具集成强化学习]] | 方法前史：把工具放进 rollout 环的单工具 RL（数学解释器）；本篇把环境扩到多域、多 harness | ToRL 的沙箱、观测 mask 与调用次数设计 |
| [[代码智能体Harness史线]] | harness 背景：动作面、反馈与隔离执行如何决定编码智能体的表现 | SWE-agent 与 OpenHands SDK 细节 |
| [[KimiK3技术报告]] | 同期开源对照：官博 AA 对比对象之一；K3 报告同样有 agentic RL 环境，并用可实例化多种 coding harness 的白盒配置 | K3 架构、Infra 与评测 |
| [[RL算力缩放与环境扩展]] | 专题归属：RL 算力缩放与环境扩展的工业案例；本篇的成本拆分（Pro 单次运行）与约 7k 环境在那篇与 DeepSeek-V3.2 等并列对照 | ScaleRL 曲线与跨厂商环境规模对比 |

## 六、意义

1. **扩 RL 拆成可核对的三轴**：不只堆 GPU，而是 batch 吞吐、环境与 harness 多样性、grader 算力（约占 Pro RL 成本的 1/8）一起放大；GAR 消融为「长程 agent 任务只靠 pass/fail」给出反例。
2. **multi-harness 作为一等公民**：用可控的 mini-harness 换跨框架泛化，held-out 的生产 harness 同步上涨，比只在自家脚手架上刷分更接近真实部署。
3. **开源包可复现小规模闭环**：7k 环境、Distill-9B 与 RL 代码，让社区验证同一配方在小模型上是否也有效，而不必复刻主 run。

## 七、局限与待核实

1. **起分偏差**：Flash 的 DeepSWE 起分报告写 48.7、官博写 48.8，本篇以报告为准。
2. **成本口径**：报告写 Flash 约 $0.9M、Pro 约 $2.6M，官博写约 $850k 与 $2.62M，取整或口径差异待核实。
3. **每步 token 数**：报告写 2.7B–3.7B，官博写 3.5～3.7B，范围下限不一致。
4. **token 与 GAR**：GAR 消融显示的是相对无 grader 更克制，不等于全局一定更短；主 run 总 token 仍在上升。
5. **AA 46 分**：属产品页主张，技术报告正文未作展开；「超过 Kimi K3 与 Qwen3.8 Max」同样出自官博，不宜外推为全面 SOTA。

## 八、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 技术报告 | MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement | Xiaomi MiMo Team；重点 §4.1–4.3、§5.1、§5.3、§5.4、§6.2、§7.1–7.2 | https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL/resolve/main/MiMo_V2_6_technical_report.pdf |
| 发布页 | MiMo-V2.6: Scaling Up Reinforcement Learning for Self-Improvement | Xiaomi MiMo，2026-09-22 更新 | https://mimo.mi.com/docs/en-US/news/latest/v2-6 |
| 开源合集 | MiMo-V2.6 HF collection | Hugging Face；官博所列开源链接 | https://huggingface.co/collections/XiaomiMiMo/mimo-v26 |
| 索引页 | alphaXiv 2609.mimo-scaling-reinforcement-learning | Submitted 21 Sept 2026 | https://www.alphaxiv.org/abs/2609.mimo-scaling-reinforcement-learning |
