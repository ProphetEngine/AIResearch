---
title: "浏览/深研 Agent 基准：BrowseComp + Online-Mind2Web"
topic: 浏览与深研Agent基准
date: 2026-09-22
lines: [评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2504.12516
 - https://arxiv.org/abs/2504.01382
arxiv: ["2504.12516", "2504.01382"]
related: ["评测与排行榜可靠性", "计算机使用智能体", "UIVenus2GUI智能体", "DeepSeekV32技术报告深读", "CHIME长程规划记忆", "WorfBench工作流基准", "MCP协议与大规模工具导航评测"]
code_browsecomp: "https://github.com/openai/simple-evals"
code_online_mind2web: "https://github.com/OSU-NLP-Group/Online-Mind2Web"
blog_browsecomp: "https://openai.com/index/browsecomp"
retrieval_cutoff: 2026-09-02
timezone: Asia/Shanghai (CST)
---

# 浏览/深研 Agent 基准：BrowseComp + Online-Mind2Web

> **主要来源**：[BrowseComp: A Simple Yet Challenging Benchmark for Browsing Agents](https://arxiv.org/abs/2504.12516)（Wei、Sun 等，OpenAI，简称 BrowseComp，v1 2025-04-16）；[An Illusion of Progress? Assessing the Current State of Web Agents](https://arxiv.org/abs/2504.01382)（Xue 等，OSU / UC Berkeley，COLM 2025，简称 Illusion，v4 2025-10-08）；[BrowseComp: a benchmark for browsing agents](https://openai.com/index/browsecomp)（OpenAI 博文）（截至 2026-09-02）。
> **研究线**：评测字段（题目构造、难度刻画、主指标、校准与算力缩放、自动评测与人工的一致率）
> **范围与相邻笔记**：
> - ≠ [[计算机使用智能体]]：本篇不写 Operator 系统卡的安全栈、OSWorld 桌面长程任务与 StateAct；Operator 只作为 Online-Mind2Web 人工成功率表中的一行。
> - ≠ [[UIVenus2GUI智能体]]：本篇不写 GUI 基础模型的训练，只写 Online-Mind2Web 的定义与协议。
> - ≠ [[WorfBench工作流基准]]：本篇不写工作流图生成与评测。
>
> **意义**：网页智能体评测从离线缓存与沙箱站点走到开放互联网后，暴露出两类问题：自报分数虚高，深度检索能力难以度量。Online-Mind2Web 在 136 个真实网站上用人工标注重测，发现多数近期智能体的成功率并不比 2024 年初的 SeeAct 高，并给出与人工一致率约 85% 的自动评测 WebJudge；BrowseComp 用「难找、易验」的短答案题考持久浏览，人类两小时内只解出 29.2%，此后成为深研类智能体的通用指标。

**一句话**：BrowseComp 测「能不能在开放网页上坚持找到一个难找的事实」，Online-Mind2Web 测「能不能在真实网站上把一件事办完」，两者主指标、交互对象与难度定义都不同，分数不能横比。

---

## 一、问题背景

网页智能体的早期评测要么用离线缓存（Mind2Web），要么用自建沙箱站点（WebShop、WebArena），站点多样性与可探索性有限；在线评测 WebVoyager 只覆盖约 15 个网站，任务偏简单，且依赖 LLM 自动判分。到 2025 年初，多个智能体在 WebVoyager 上自报接近 90% 的成功率（Illusion §1–2）。另一方面，深度研究类产品需要的是在大搜索空间里持续检索、拼接线索，而 SimpleQA 等事实问答很快饱和，缺少既难又能自动判分的浏览基准。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2022-07 | [WebShop](https://arxiv.org/abs/2207.01206) | 模拟购物网站上的语言智能体交互 |
| 2023-06 | [Mind2Web](https://arxiv.org/abs/2306.06070) | 真实网站的离线任务与动作标注 |
| 2023-07 | [WebArena](https://arxiv.org/abs/2307.13854) | 可复现的自建沙箱网站环境 |
| 2024-01 | [WebVoyager](https://arxiv.org/abs/2401.13919) | 在线真实网站上的端到端多模态智能体与自动判分 |
| 2025-04 | Illusion v1（Online-Mind2Web）、BrowseComp | 前者在线重测并给出 WebJudge；后者用倒置构造的难检索短答案题 |
| 2025-04 | [BrowseComp-ZH](https://arxiv.org/abs/2504.19314) | 中文网页浏览基准 |
| 2025-10 | Illusion v4 | 现行版本 |

## 三、BrowseComp

### 3.1 构造（§2）

- **规模**：1,266 题；原有 1,287 题，对 Deep Research 全部失败的 118 题复核后剔除了 21 道标注有问题的题。
- **答案**：短字符串、唯一、不随时间变化，沿用 SimpleQA 的出题规范。
- **倒置出题**：从一个已知事实出发，组合多个约束，使搜索空间很大而验证很便宜。
- **难度门槛**：出题时 GPT-4o（含浏览）、o1 与早期 Deep Research 都解不出；五次简单 Google 搜索的首页结果里没有答案；出题者判断他人 10 分钟内解不出（部分题由第二位训练员复验，被解出超过 40% 的出题者需返工）。
- **评分与防泄漏**：用与 Humanity's Last Exam 相同的判分提示判断语义等价；数据带 canary 字符串。
- **不测什么**（文内自述）：不能严格排除第二个合法答案；不测长答案，也不测用户意图的歧义消解。作者把它类比为编程竞赛，只代表浏览能力的一个切面。

### 3.2 人类基线（Table 2）

训练员解他人出的题，不得使用 AI 助手，可在两小时后放弃。1,255 题有人尝试，其中 888 题（70.8%）放弃，367 题（29.2%）解出，解出的题中 317 题（86.4%）与参考答案一致。

### 3.3 模型结果（Table 3）

| 模型 | 准确率 (%) | 校准误差 (%) |
|---|---:|---:|
| GPT-4o | 0.6 | 69 |
| GPT-4o + 浏览 | 1.9 | 82 |
| GPT-4.5 | 0.9 | 68 |
| OpenAI o1 | 9.9 | 65 |
| Deep Research | 51.5 | 91 |

只加浏览工具几乎无用，不浏览但推理更强的 o1 反而达 9.9%；Deep Research 的校准误差最高，作者认为浏览可能提高模型在错误答案上的自信。脚注注明 Deep Research 用专门教 BrowseComp 类任务的数据训练过，读数时须带上这一条件。

### 3.4 算力与难度谱（§4）

- **测试时算力**：Deep Research 的准确率随浏览投入平滑上升（Figure 1）。
- **聚合**：每题采 64 个带置信度的答案，多数投票、置信加权投票与取最高置信度三种方法比单次提升 15%–25%，取最高置信度始终最好；作者的解释是题目易验，模型能部分识别自己何时答对。
- **难度谱**：64 次尝试中，Deep Research 有 16% 的题每次都对，14% 的题从未答对；给出参考答案后，模型多能找到支持证据，作者据此认为这些题不是无解，而是缺少有策略的坚持。

## 四、Online-Mind2Web 与 WebJudge

### 4.1 对 WebVoyager 的诊断（§2.1）

一个只用 Google 搜索、点开一条结果就作答的简单智能体，在 WebVoyager 抽样的 100 题上人工评定成功率已达 51%，在 Online-Mind2Web 上只有 22%（简单、中等、困难分别约 50%、18%、3%）。WebVoyager 的覆盖面窄、任务可被捷径解决，其自动判分与人工的一致率也偏低。

### 4.2 构造（§2.2）

- **规模**：300 个任务，跨 136 个热门真实网站；来自 Mind2Web 精选 167 个、改写 24 个、Mind2Web-Live 34 个与新写 75 个；初筛的 650 个旧任务中约 47% 已失效或轨迹过时。
- **难度**：按人类参考步数 $N$ 分为简单（$N\le5$）83 个、中等（$6\le N\le10$）143 个、困难（$N\ge11$）74 个。
- **协议**：每个任务给定起始网址，提示不要用 Google 搜索以防捷径；六个智能体的全部轨迹由至少两人标注、第三人仲裁；过时任务按相近难度替换。

### 4.3 人工成功率（Table 2）

| 智能体 | 人工成功率 (%) |
|---|---:|
| SeeAct | 30.7 |
| Agent-E | 28.0 |
| Browser Use | 30.0 |
| Claude Computer Use 3.5 | 29.0 |
| Claude Computer Use 3.7 | 56.3 |
| OpenAI Operator | 61.3 |

除 Claude Computer Use 3.7 与 Operator 外，近期智能体都没有超过 2024 年初的 SeeAct。从简单到中等任务，平均成功率下降 31.6%，从中等到困难再降 15.4%；Claude 3.7 与 Operator 在简单任务上达 90.4% 与 83.1%，困难任务仍很吃力。

### 4.4 WebJudge（§3–4）

只用截图序列与动作历史，不看智能体的中间思考与最终回复，以减少幻觉干扰。三步：从任务描述中找出完成要点；给每帧截图打相关性分，只留关键截图；综合判定成败。

| 评测器 | 与人工的平均成功率差 | 平均一致率 |
|---|---:|---:|
| WebJudge（GPT-4o） | 7.8 | 83.6% |
| WebJudge（o4-mini） | 3.8 | 85.7% |
| WebJudge-7B（Qwen2.5-VL-7B 微调） | 3.9 | 87.0% |

同一管线重复 3 次，六个智能体成功率的平均标准差为 1.1%。以 GPT-4o 为骨干时，旧方法的一致率为 Autonomous Eval 79.4%、AgentTrek 66.9%、WebVoyager 73.9%（Table 3）。在 AgentRewardBench 的 1,302 条轨迹上，WebJudge（o4-mini）的总体精确率为 82.0%，接近基于规则的 83.8%（Table 4）。作者提出它可作为 RL 或拒绝采样的奖励，论文没有实证。

### 4.5 效率与错误（§5）

Browser Use、Claude 3.7 与 Operator 的失败轨迹步数接近成功轨迹的两倍。Operator 偏向探索，步数约为人类参考的 2.6 倍，困难任务可长达 44 分钟。Operator 的错误以筛选与排序（57.7%）和导航（19.6%）为主；共同弱点是对数值与时间约束不敏感、探索不足、过度依赖关键词搜索、幻觉自己已满足约束。

## 五、两基准对照

| 维度 | BrowseComp | Online-Mind2Web |
|---|---|---|
| 交互对象 | 开放互联网检索，输出短事实答案 | 指定真实网站上的操作任务（筛选、填表等） |
| 规模 | 1,266 题 | 300 任务 / 136 网站 |
| 主指标 | 准确率；辅以校准误差 | 人工成功率；辅以 WebJudge 一致率 |
| 难度定义 | 出题门槛、人类两小时放弃率、通过率谱 | 人类参考步数 |
| 防捷径 | canary；首页搜不到答案 | 禁用 Google、固定起始网址 |
| 算力轴 | 浏览投入与 64 样本聚合 | 步数效率与失败轨迹膨胀 |

## 六、意义

两篇从不同方向修正了网页智能体评测。Online-Mind2Web 用人工金标说明，此前在 WebVoyager 上的进步很大一部分是捷径与宽松判分带来的，并用 WebJudge 把在线评测的成本降到可重复的程度。BrowseComp 用倒置构造得到了「人类也难、但能自动判分」的检索题，配合校准与算力曲线，成为深研类智能体最常用的指标；多份技术报告笔记把它列入主表，并因上下文管理策略不同而得到差别很大的分数。

## 七、局限与待核实

- **BrowseComp**：可能存在第二个合法答案；Deep Research 用同类数据训练过；不测长答案与歧义消解；博文与论文的人类基线和准确率一致，校准误差以论文 Table 3 为准。
- **Online-Mind2Web**：在线网站持续变化，跨时间的可比性依赖维护者替换过时任务；在 AgentRewardBench 上，o4-mini 骨干的 WebJudge 精确率高但偏严、召回偏低，作者称这使它与人工的成功率差更大（§4.3）；WebJudge 作为训练奖励的效果未经实证。
- **只见于图中的数字**：BrowseComp 主题分布（Figure 2）、WebVoyager 自报与人工成功率对比（Figure 1）、Operator 其余错误类型的比例（Figure 7）只出现在图中，本篇不引。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[评测与排行榜可靠性]] | 上游：榜单通胀与评测可靠性的总论在该篇；WebVoyager 自报分数虚高是网页智能体上的一个实例 | 排行榜方法论 |
| [[计算机使用智能体]] | 交叉：Operator 在 Online-Mind2Web 上的人工成功率 61.3%；其安全栈与桌面长程评测在该篇 | Operator 系统卡、OSWorld、StateAct |
| [[UIVenus2GUI智能体]] | 下游使用：该篇的模型对比表列出 Online-Mind2Web 分数 | GUI 模型训练 |
| [[DeepSeekV32技术报告深读]] | 下游使用：DeepSeek-V3.2 报告的 BrowseComp 分数随上下文管理策略显著变化 | 模型训练与架构 |
| [[CHIME长程规划记忆]] | 下游使用：CHIME 把中文版 BrowseComp-ZH 作为四个长程基准之一 | 自演化记忆方法 |
| [[WorfBench工作流基准]] | 并列：同属智能体评测；本篇评浏览问答与在线任务结果，该篇评工作流图 | 工作流图生成与评测 |
| [[MCP协议与大规模工具导航评测]] | 并列：该篇把本篇列为动态信息任务的同类基准；该篇评大规模工具导航 | MCP 协议与工具导航 |

## 九、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [BrowseComp](https://arxiv.org/abs/2504.12516) §2、Table 2–3、§4 | 构造原则、人类基线、校准与算力 |
| 2 | [Illusion](https://arxiv.org/abs/2504.01382) §2、Table 2–4、§5 | WebVoyager 诊断、人工成功率、WebJudge、错误分析 |
| 3 | [openai/simple-evals README](https://github.com/openai/simple-evals)、[OSU-NLP-Group/Online-Mind2Web README](https://github.com/OSU-NLP-Group/Online-Mind2Web) | 评测代码与数据 |
| 4 | [[评测与排行榜可靠性]] | 评测可靠性总论 |
