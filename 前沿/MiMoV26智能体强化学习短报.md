---
date: 2026-09-23
status: archived
archived: 2026-09-23
topic: frontier-mimo-v2-6
title: "B · MiMo-V2.6 技术报告（Agentic RL）轻量深读"
sources:
 blog: https://mimo.mi.com/docs/en-US/news/latest/v2-6
 pdf: https://huggingface.co/XiaomiMiMo/MiMo-V2.6-Flash-RL/resolve/main/MiMo_V2_6_technical_report.pdf
 alphaxiv: https://www.alphaxiv.org/abs/2609.mimo-scaling-reinforcement-learning
 hf_collection: https://huggingface.co/collections/XiaomiMiMo/mimo-v26

# B · MiMo-V2.6：Scaling RL Towards Self-Improvement（Agentic RL）

> **跟读定位**：一页卡，只锁 **RL batch / agentic grader / multi-harness / 开源环境清单**。数字与机制均出自官博与技术报告；**禁编造**。

## 一句话

MiMo-V2.6 把 Agentic RL 写成「算力三维放大」：**更大 batch + 更多环境/harness + 更多 grader 算力**，在一次混合任务 run 里做 You-Only-RL-Once；开源约 **7k** 可验证环境 + Distill-9B 基线，便于社区复现同套路。

## 要点（优先四字段）

### 1. RL batch（吞吐轴）

| 项 | 报告明文 | 出处 |
|---|---|---|
| Prompt batch | **1,568** prompts / step | §4.1；§5.1 |
| Group size | **𝐺 = 16** rollouts → 约 **25K** trajectories / step | §4.1；§5.1 |
| Tokens / step | **2.7B–3.7B**（约 110K–150K tokens/seq）；官博写 3.5～3.7B | §4.1；[blog](https://mimo.mi.com/docs/en-US/news/latest/v2-6) |
| 算法 / 异步 | **GRPO**；asynchronous **partial rollout**，staleness **4**；prompt-mean aggregation | §5.1；§4.1 |
| 成本拆分（Pro） | Rollout **43.8%** / Training **43.5%** / **Grader 12.7%**；RL 后训花费 Pro **$2.6M**、Flash **$0.9M** | §4.1 |
| Live 叙事（官博） | <6 天 Live RL；Flash/Pro 各约 **30** steps；累计 ≈**750k** trajectories；训练任务平均 passrate 相对 +**25%** / +**12%** | [blog](https://mimo.mi.com/docs/en-US/news/latest/v2-6) |
| 域混合比例 | Code **68%** · Aesthetic **13%** · General tool **12%** · Cyber **4%** · Context following **3%** | §5.1 |
| 稳定前置 | **冻结 MoE router**（可训 router 时 CV 0.78→2.0、冷专家 0.5%→22%） | §5.4 |

### 2. Agentic grader（信号轴）

二元测试无法区分「都过测」的好坏解；报告用 **groupwise agentic grading**（§4.3）：

- **GRS（Offline）**：高 passrate 子集；离线对照多条 rollout 建 *solution / behavior* rubrics；训练时
 $R_i = R_i^{\mathrm{test}} \cdot S_i^{\mathrm{sol}} \cdot S_i^{\mathrm{beh}}$（失败仍为 0）。
- **GAR（Online）**：其余 code 任务；组内共享 workspace，SFT 训好的 grader 沿五维排序 passing patches（方案适配、实现精度、最小改动、范围外副作用、代码风格）；确认 hack → $R\leftarrow 0$ 再重算组统计，把正 advantage 从低质 pass 挪到高质 pass。
- **消融（Flash，code-only，batch 128）**：无 GAR → turns/长度飙升、passrate 早平台；有 GAR → passrate 可持续更久、长度涨得更慢（Fig.8 / §4.3.2）。

### 3. Multi-harness（交互轴）

- 动机：单 harness 会把解题策略绑死在实现细节上；生产 harness（MiMo Code / Codex 等）指令与工程包装太多，落在 reward 外，信用分配差（§4.2.5）。
- 做法：从同一 **minimal agent loop**（system prompt · tools · context mgmt）派生可重组 **mini-harnesses**，覆盖 Code / General / Visual / Cyber；训练期混多个 harness。
- 证据（DeepSWE v1.1）：4 个 training mini-harness + held-out **codex / claude code / mini-swe-agent** 均随训提升；held-out 均值 Pass@1 ≈ **50% → 66%**，训测差距收窄（Fig.10 / §5.3）。
- Infra：Harness Pool（多租户并发）+ Payload Porter（控制面/数据面解耦），支撑大批次多 harness（§6.2）。

### 4. 开源环境清单（复现轴）

报告 Table 5（§7.2；约数，按 distinct task id）：

| Domain | Task family | ≈Tasks | Verifier |
|---|---|---:|---|
| Code | Software engineering | **3k** | Executable tests |
| Cyber | Vulnerability reproduction | **1k** | Rule checks |
| General | Knowledge work | **1k** | Rubric-based judging |
| Visual | Web development | **2k** | Visual grading |
| （另） | Music generation（支持 GRPO 实验） | **≈1k** | （文中未单列 verifier） |

合计训练集约 **7k**（与官博「7k+ high-quality RL task environments」一致）。配套：

- **MiMo-V2.6-Distill-Qwen-9B**（Qwen3.5-9B 上 SFT，77.4B total / 27.2B loss tokens）
- 端到端 RL 框架（官博：基于 **verl / uni-agent / mini-swe-agent**）
- 轻量可组合 mini-harness；HF collection：<https://huggingface.co/collections/XiaomiMiMo/mimo-v26>

9B 域内 GRPO 相对 SFT（Table 6 摘录）：SWE-bench Verified **61.1→66.2**；MiMo Cyber (mini) **31.3→47.0**；Terminal Bench 2.1 **37.1→52.8**；MiMo Visual Coding (mini) **64.0→72.4**——**11/11** 评测全涨。

## 为何重要（跟读用）

1. **把「扩 RL」拆成可核对的三轴**：不只堆 GPU，而是 batch 吞吐、环境/harness 多样性、grader 算力（≈Pro RL 成本的 1/8）一起上；对「agent 长程任务只靠 pass/fail」给出可消融的反例（GAR）。
2. **Multi-harness 作为一等公民**：用可控 mini-harness 换跨框架泛化，held-out 生产 harness 同步涨——比「只在自家脚手架上刷分」更接近真实部署。
3. **开源包可复现小规模闭环**：7k 环境 + Distill-9B + RL 代码，让社区验证「同一配方是否在小模型上也涨」，而不必复刻万卡主 run。

## 关键结果锚点（勿外推为全面 SOTA）

- DeepSWE v1.1 avg@3：Pro **58.4→72.6**，Flash **48.7→65.7**（§4.1；官博 Flash 起分写 48.8，以报告为准并注明偏差）。
- 主 run 分数上涨常伴随 **total tokens 上升**（Fig.9）；GAR 消融显示的是「相对无 grader」更克制，不是全局一定更短。
- AA Intelligence Index：官博称 Pro **46**（开源侧叙事；闭源仍有差距）——属产品页主张，技术报告正文未作为本文优先字段展开。

## 引用

1. Xiaomi MiMo Team. *MiMo-V2.6: Scaling Reinforcement Learning Towards Self-Improvement*. Technical report PDF（HF：https://huggingface.co/XiaomiMiMo ；文件 `MiMo_V2_6_technical_report.pdf`，约 3.05MB）。重点 §4.1–4.3、§5.1/5.3/5.4、§6.2、§7.1–7.2。
2. 产品/开源说明：[MiMo-V2.6 发布页](https://mimo.mi.com/docs/en-US/news/latest/v2-6)（2026-09-22 更新）；[HF collection](https://huggingface.co/collections/XiaomiMiMo/mimo-v26)。
3. 索引页：[alphaXiv 2609.mimo-scaling-reinforcement-learning](https://www.alphaxiv.org/abs/2609.mimo-scaling-reinforcement-learning)（Submitted 21 Sept 2026）。

