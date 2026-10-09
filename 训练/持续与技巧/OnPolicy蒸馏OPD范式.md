---
title: On-Policy Distillation（OPD）范式
topic: OnPolicy蒸馏OPD范式
date: 2026-09-25
lines: [架构思想, 数学原理]
status: archived
sources:
  - https://arxiv.org/abs/2604.00626
  - https://thinkingmachines.ai/blog/on-policy-distillation/
  - https://arxiv.org/abs/2306.13649
  - https://arxiv.org/abs/2306.08543
  - https://arxiv.org/abs/1503.02531
arxiv: ["2604.00626", "2306.13649", "2306.08543", "1503.02531"]
related:
  - 上下文蒸馏
  - 合成对齐数据Magpie
  - GRPO与DAPO算法族
  - RL算力缩放与环境扩展
  - Qwen3技术报告深读
  - Nemotron3Ultra技术报告深读
  - DeepSeekV4技术报告深读
  - KimiK3技术报告
  - 持续学习
  - QwenOmni音视频原生
github: https://github.com/nick7nlp/Awesome-LLM-On-Policy-Distillation
retrieval_cutoff: 2026-08-07
timezone: Asia/Shanghai (CST)
archived: 2026-09-28
---

# On-Policy Distillation（OPD）范式

> **主要来源**：[A Survey of On-Policy Distillation for Large Language Models](https://arxiv.org/abs/2604.00626)；[On-Policy Distillation](https://thinkingmachines.ai/blog/on-policy-distillation/)（Thinking Machines 博文）；[On-Policy Distillation of Language Models: Learning from Self-Generated Mistakes](https://arxiv.org/abs/2306.13649)；[MiniLLM: On-Policy Distillation of Large Language Models](https://arxiv.org/abs/2306.08543)；[Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531)（截至 2026-08-07）。综述为 Song 与 Zheng（腾讯）所作，首版 2026-04-01，现行 v4 2026-06-18；博文作者 Kevin Lu 等，2025-10-27 发布；GKD（Agarwal 等）与 MiniLLM（Gu 等）均为 ICLR 2024 论文，首版分别为 2023-06-23 与 2023-06-14。
> **研究线**：架构思想（主）——轨迹由谁采样、教师信号从哪来、训练动态如何稳住；数学原理（辅）——$f$-散度族的选择与 RL 式目标。
> **范围与相邻笔记**：
> - ≠ [[上下文蒸馏]]：本篇不写把提示或文档条件行为压进参数的 Snell、OPCD、DiSC 配方与评测。
> - ≠ [[合成对齐数据Magpie]]：本篇不写对齐数据从哪来的合成流水线。
> - ≠ [[GRPO与DAPO算法族]]：本篇不推导 GRPO 损失，只写 OPD 与 KL 约束 RL 的一句交叉。
>
> **意义**：后训练长期在两种做法之间取舍：SFT 式蒸馏信号稠密，但学生学的是教师走过的状态；RL 在学生自己的轨迹上学，但每条轨迹只给一个结果奖励。OPD 让学生自己采样、由教师给每个 token 打分，把两者的长处合在一起。Qwen3 报告它以约十分之一的 GPU 时达到比 RL 更高的成绩，此后 Nemotron 3 Ultra、DeepSeek-V4、Kimi K3 等开放旗舰的后训练都用到了多教师 OPD。

**一句话**：off-policy 蒸馏让学生在教师的完美前缀上模仿；OPD 让学生在自己生成的轨迹上接受教师逐 token 的反馈，把「一次性照抄」改成「边犯错边纠正」。

---

## 一、问题背景

1. **训练态与部署态不一致**：经典的序列蒸馏在固定语料或教师生成的文本上训练，每一步都以无错的教师前缀为条件；部署时学生以自己写出的前缀为条件，早期一个错误会让它进入训练时从未见过的状态，误差沿序列放大。综述（§2）引用 DAgger 的分析：这种误差随长度 $T$ 按 $O(\epsilon T^2)$ 增长，训练分布贴近部署分布后可接近 $O(\epsilon T)$（前提是教师在学生前缀上仍可信）。长链推理、代码与智能体轨迹对此尤其敏感。
2. **只学到风格**：博文指出 off-policy 蒸馏的学生可能学到教师的文风与自信，却学不到事实准确性（引 Gudibande 等 2023）。
3. **RL 的奖励太稀疏**：RL 在学生自己的轨迹上训练，但无论轨迹多长，每条只得到一个对错信号，学生不知道错在哪一步。博文的信息论说法是：RL 每条轨迹只教 $O(1)$ 比特，逐 token 蒸馏教 $O(N)$ 比特（$N$ 为 token 数）。

| 方法 | 采样 | 奖励信号 |
|---|---|---|
| 监督微调 / off-policy 蒸馏 | off-policy | 稠密 |
| 强化学习 | on-policy | 稀疏 |
| On-policy 蒸馏 | on-policy | 稠密 |

（据博文的三分表。）

## 二、脉络

| 节点 | 做法 | 留下的问题 |
|---|---|---|
| Hinton 等知识蒸馏（2015-03） | 用教师的软化输出分布训练学生，把集成模型的知识压进单个模型 | 面向分类，未处理自回归生成的误差累积 |
| MiniLLM（2023-06） | 把前向 KL 换成反向 KL，避免学生高估教师的低概率区；用以教师 log-prob 为奖励的策略梯度在学生样本上优化 | 优化依赖 RL 式技巧 |
| GKD（2023-06） | 学生在自己生成的序列上接受教师反馈，可用 $\lambda$ 在 off/on-policy 之间混合，可换用其他散度，并可与 RLHF 结合 | 不同任务的最优散度不同 |
| DistiLLM（2024） | 用 skew KL 稳住数值 | — |
| Qwen3 技术报告（2025-05） | 小模型从旗舰做 on-policy 蒸馏，以约 RL 十分之一的 GPU 时取得更高成绩 | 只是报告中的一节 |
| Thinking Machines 博文（2025-10） | 用逐 token 反向 KL 作优势、在 RL 代码上做一行改动实现 OPD，系统对比 SFT 与 RL 的成本，并用于个性化与持续学习 | 实验集中在 Qwen3 系 |
| 综述（2026-04） | 把方法收成目标函数、信号来源、训练动态三条设计轴 | 各轴间的系统比较仍少 |
| 多教师 OPD（2026） | Nemotron 3 Ultra、DeepSeek-V4、Kimi K3 等把多教师 on-policy 蒸馏写进后训练 | 细节见各技术报告 |

Hinton 等、MiniLLM、GKD 三行据各自论文；MiniLLM 的 arXiv 现行题名为「MiniLLM: On-Policy Distillation of Large Language Models」，早期版本题为「MiniLLM: Knowledge Distillation of Large Language Models」。

## 三、定义与分界

综述的定义（§2）：只要训练期望的外层采样来自学生当前策略，而不是静态数据集或教师生成的分布，该方法就属于 on-policy。

| | Off-policy 教师轨迹蒸馏 | On-policy 学生自采样加教师信号 |
|---|---|---|
| 轨迹从哪来 | 固定语料，或事先由教师生成的文本 | 训练时由学生当前策略 $p_\theta$ 采样，可与少量真实前缀混合，常见形式 $\pi_{\mathrm{mix}}=\lambda p_\theta+(1-\lambda)p_{\mathrm{data}}$ |
| 每步以什么为条件 | 几乎总是无错的教师前缀 | 学生自己刚写出的前缀，含早期错误 |
| 优化目标 | $\mathbb{E}_{y\sim\mathcal{D}}\sum_t D\big(p_T(\cdot\mid y_{<t})\,\Vert\,p_\theta\big)$ | $\mathbb{E}_{y\sim p_\theta}\sum_t D_f\big(p_T(\cdot\mid y_{<t}),\,p_\theta\big)$ |
| 典型损失 | token 级 KL、教师序列的负对数似然 | $f$-散度（前向 KL、反向 KL、JSD、skew KL）；序列级反向 KL 加策略梯度；按位置自适应切换；蒸馏加奖励 |
| 适用场景 | 短序列、教师前缀质量高、算力紧（不需反复 rollout） | 长链推理、代码、智能体轨迹；多教师合并与后训练巩固 |

**散度怎么选**：前向 KL 覆盖教师的多个峰，学生容量不足时容易在峰间「幻觉」；反向 KL 盯住少数峰（mode seeking），适合答案唯一的任务；JSD 与 $\alpha$-散度居中。一句话：轨迹由谁采样，决定训推是否同分布；散度怎么选，决定学生是铺开学还是收窄学。

## 四、三条设计轴（综述 §3–§6）

1. **优化什么**：固定散度；按位置自适应的散度；RL 增强目标。G-OPD 把 OPD 写成稠密的 KL 约束 RL，并允许 $\alpha>1$ 时做奖励外推。
2. **信号从哪来**：白盒教师可做精确的 token 级散度；黑盒教师只能给文本批评、标量分或偏好对；没有外部教师时，用特权上下文或自我对比做自蒸馏。
3. **如何稳住动态**：混合采样、课程、token 加权。综述点名的失败模式是**有缺陷前缀陷阱**（flawed prefix trap）：学生早期写坏后，教师在该前缀上的条件分布本身也会失准，硬匹配反而伤训练。因此实践中常保留 off-policy 冷启动、按可靠度加权或加信任域，而不是全程无条件 on-policy。

## 五、Thinking Machines 博文的经验证据

**实现**：学生采样轨迹，教师对这些 token 计算 log-prob，两者之差即逐 token 反向 KL，取其负值作为每个 token 的优势，交给 RL 的重要性采样损失；折扣因子取 0。教师只需对学生轨迹做一次前向，不需要单独的奖励模型，也不必等轨迹采完。博文称在带 KL 正则的 RL 实现上只是「把正则参考模型换成教师」的一行改动；反向 KL 低总对应教师眼中的高概率行为，因而难以被投机利用（reward hacking）。

**推理蒸馏**（学生 Qwen3-8B-Base，先在 OpenThoughts-3 上做 off-policy 蒸馏）：

- SFT 40 万条 prompt 后 AIME'24 为 60%；按对数线性趋势外推，SFT 到 70% 约需 200 万条。
- 从 40 万条检查点起做 OPD，约 150 步（约 7.7 万条 prompt，每条 4 个样本）达到 70%。按训练 FLOPs 计，相对外推的 SFT-2M 节省 9 倍（SFT 数据已有时）到约 30 倍（计入教师采样成本时），按 GPU 时约 18 倍。
- 引用 Qwen3 技术报告 Table 21：在相近 SFT 初始化上，RL 用 17,920 GPU 时将 AIME'24 从 55.0% 提到 67.6%，OPD 用 1,800 GPU 时提到 74.4%。
- LoRA（rank 32）在 SFT 后落后全量微调 13%，OPD 后只落后 6%。

**稠密信号的效率**：先对 Qwen3-8B-Base 做 RL 得到教师，再从同一初始化做 OPD，约少 7–10 倍梯度步就追上 RL 策略，累计算力约省 50–100 倍。博文的解释是：RL 的算力主要花在搜索策略上，一旦找到好策略，OPD 只需学最终策略，不必重走中间过程。用单条 prompt 训练 20 步（每步 256 条 rollout）也大致追上教师的 AIME'24 成绩，因为 OPD 学的是教师的完整分布，不是记住一个答案。

**个性化与持续学习**（Qwen3-8B 在内部文档上做中期训练）：

| 模型 | 内部知识问答 | IF-eval |
|---|---:|---:|
| Qwen3-8B | 18% | 85% |
| + 中期训练（文档 100%） | 43% | 45% |
| + 中期训练（文档 70%、对话 30%） | 36% | 79% |
| + 中期训练（70%）+ OPD | 41% | 83% |

用训练前的 Qwen3-8B 当教师、在 Tulu3 prompt 上做 OPD，指令遵循几乎恢复，知识没有损失。博文还发现：即使在模型自己的采样上做 SFT，只要学习率大于零，IF-eval 也会下降，因为有限 batch 的分布偏差会让训练逐渐变成 off-policy；OPD 的教师固定，始终 on-policy，不会出现这种退化，因此适合在「学新知识」与「恢复行为」之间交替的持续学习。

## 六、与推理后训练和上下文蒸馏的交叉

- **KL 约束 RL**：综述把标准 OPD 与稠密 KL 约束 RL 写成形式等价（G-OPD 等）；博文也指出 RL 与 OPD 都在学反向 KL，差别只在奖励密度。
- **多教师 OPD**：[[Nemotron3Ultra技术报告深读]] 的 MOPD（Multi-teacher On-Policy Distillation）、综述所载 Nemotron-Cascade 2 与 DeepSeek-V4 的多教师 OPD 同属「学生 rollout 加教师稠密信号」一族，细节见各技术报告。
- **上下文蒸馏不是 OPD**：[[上下文蒸馏]] 回答的是怎样把富提示或文档条件下的行为压进参数，推理时不再携带原上下文。OPCD 虽然在损失上用「学生采样加反向 KL」，主对象仍是特权上下文的内化；综述也把 OPCD 归在「行为型特权信息 / 上下文蒸馏」分支，而非 OPD 定义的核心。两者可在技术上交叠，议题不同：OPD 看轨迹策略是否 on-policy（学生采、教师评），上下文蒸馏看条件是否卸掉（富条件教师到贫条件学生）。

## 七、意义

- **把蒸馏的期望搬到学生自己的分布上**：OPD 的内核是让学生在部署时会遇到的状态上接受纠正，直接针对误差累积。
- **后训练的成本结构改变**：已有强教师时，OPD 以稠密信号省去 RL 大部分的搜索算力，Qwen3 与博文的数据都在一个数量级左右。
- **成为工业后训练的合并环节**：多个专家模型分别 RL 后，再用多教师 OPD 合成一个统一模型，已出现在多家开放旗舰的报告中。
- **为持续学习提供工具**：用旧版模型作教师恢复行为，使「学新知识」与「保后训练能力」可以交替进行。

## 八、局限与待核实

- **依赖强教师**：OPD 需要一个在目标任务上明显更强、且能给出 log-prob 的教师；黑盒教师只能退到文本批评或标量分，信号精度下降。
- **有缺陷前缀陷阱**：学生写坏后，教师在该前缀上的分布也可能失准；需要冷启动、加权或信任域，综述没有给出统一做法。
- **初始化要求**：博文强调需先做 SFT 或中期训练，使教师的高概率 token 落在学生的支撑集内；否则需要大得多的 batch。
- **博文证据的范围**：实验集中在 Qwen3 系与少数任务，FLOPs 口径会高估 log-prob 计算的实际成本（博文自述）；9–30 倍、50–100 倍等倍数依赖具体实现与是否计入教师采样成本。博文后来补注：原实验的教师 Qwen3-32B 与学生 Qwen3-8B-Base 已从 Tinker 下线，cookbook 中的蒸馏配方改为以 Qwen3.5-9B-Base 为学生、Qwen3.5-9B 为教师，以保证实验仍可复现。
- **综述仍偏分类**：三条设计轴之间缺少同一基准上的系统比较。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[上下文蒸馏]] | 相邻接口：OPCD 同用学生采样与反向 KL，但目标是把上下文写进参数，属于上下文蒸馏而非 OPD 本身 | Snell、OPCD、DiSC 的配方与评测表 |
| [[合成对齐数据Magpie]] | 分界：那篇回答对齐数据从哪来，本篇回答已有教师时学生在什么分布上学 | Magpie 与 ActiveUltraFeedback 流水线 |
| [[GRPO与DAPO算法族]] | OPD 可写成稠密 KL 约束 RL，实现上复用策略梯度框架，只把结果奖励换成逐 token 的负反向 KL | GRPO 损失推导 |
| [[RL算力缩放与环境扩展]] | 那篇写 RL 后训练的算力怎样外推，本篇给出另一条路：已有强教师时，用稠密信号以约十分之一甚至更少的算力达到 RL 的效果 | RL 缩放曲线与环境构建 |
| [[Qwen3技术报告深读]] | 那篇 5.3 节 Strong-to-Weak Distillation 是 OPD 「约 RL 十分之一 GPU 时」结论的出处，博文即以复现它为起点 | Qwen3 四阶段后训练全流程 |
| [[Nemotron3Ultra技术报告深读]] | 多教师 OPD 的工业实例：那篇的后训练在 RLVR 之后做两轮 MOPD | Nemotron 后训练全文 |
| [[DeepSeekV4技术报告深读]] | 工业实例：V4 先按领域 SFT → GRPO 训出专家，再让学生在自身采样上以反向 KL 对齐超过 10 个教师，做多教师 OPD 合并，取代 V3.2 的混合 RL 合并阶段 | V4 架构与后训练全文 |
| [[KimiK3技术报告]] | 多教师 OPD 的工业实例：那篇在九个专家 RL 之后用 MOPD 合并为统一模型 | K3 架构与预训练 |
| [[QwenOmni音视频原生]] | 跨模态实例：那篇的 Qwen3.5-Omni 后训练用 OPD，把同一问题在文本输入下的回答作为音频输入时的蒸馏目标 | 全模态架构与评测 |
| [[持续学习]] | 那篇写持续学习的地图与抗遗忘方法，本篇补一种新工具：在学新知识后用旧版模型作教师做 OPD，恢复被冲掉的后训练行为 | 持续学习场景分类与 Lifelong-MoE |
| [[RL训练系统与异步Rollout]] | 系统接口：本篇的 OPD 同样要让学生在线采样，生成与训练怎样排布、陈旧样本怎样处理，看那篇 | RL 训练系统的架构与调度 |
| [[模型合并]] | 把多个专家能力合成单模型的两条路：本篇的多教师 OPD 用学生采样加教师信号再训练，那篇直接在权重空间合并，不需再训练 | 合并算法与 MergeBench |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Thinking Machines：On-Policy Distillation](https://thinkingmachines.ai/blog/on-policy-distillation/) | 实现、成本对比与持续学习实验 |
| 2 | [On-Policy Distillation 综述](https://arxiv.org/abs/2604.00626) §2–§6 | 定义与三条设计轴 |
| 3 | [GKD](https://arxiv.org/abs/2306.13649)、[MiniLLM](https://arxiv.org/abs/2306.08543) | 两种奠基形式：混合采样与反向 KL 策略梯度 |
| 4 | [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) | 知识蒸馏的起点 |
| 5 | [nick7nlp/Awesome-LLM-On-Policy-Distillation README](https://github.com/nick7nlp/Awesome-LLM-On-Policy-Distillation) | 综述配套文献索引 |
| 6 | [thinking-machines-lab/tinker-cookbook README](https://github.com/thinking-machines-lab/tinker-cookbook) | 博文实验的代码 |
