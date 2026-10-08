---
title: "代码修复评测新轴：SWE-Bench Pro + Pro Verified（≠ harness）"
topic: SWEBenchPro代码修复评测
date: 2026-09-22
lines: [评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2509.16941
 - https://arxiv.org/abs/2609.08149
 - https://arxiv.org/abs/2310.06770
arxiv: ["2509.16941", "2609.08149"]
related: ["代码智能体Harness史线", "评测与排行榜可靠性", "科研智能体", "智能体工具与长程任务", "开端性与发现基础模型", "评测数据污染检测与可靠性", "奖励黑客与涌现失对齐", "RL算力缩放与环境扩展"]
aux_scale: "https://labs.scale.com/papers/swe-bench-pro"
data_pro: "https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro"
code_pro: "https://github.com/scaleapi/SWE-bench_Pro-os"
data_verified: "https://huggingface.co/datasets/opencompass/SWEBench-Pro-Verified"
code_verified: "https://github.com/open-compass/AgentCompass"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 代码修复评测新轴：SWE-Bench Pro + Pro Verified（≠ harness）

> **主要来源**：[SWE-Bench Pro（Deng, Da et al., Scale AI；arXiv v2）](https://arxiv.org/abs/2509.16941)；[SWE-Bench Pro Verified（Zheng et al., 华东师大 / 上海 AI Lab / 复旦）](https://arxiv.org/abs/2609.08149)；背景 [SWE-bench（Jimenez et al., 2023）](https://arxiv.org/abs/2310.06770)（截至 2026-09-22）
> **研究线**：评测字段——仓库级代码修复评测「测什么、怎么保证分数是真的」。
> **范围与相邻笔记**：
> - ≠ [[代码智能体Harness史线]]：本篇不写 SWE-agent 的 ACI、OpenHands SDK 与控制环。
> - ≠ [[评测与排行榜可靠性]]：本篇不写污染、路由、thinking 模式等榜单可靠性通史。
> - ≠ [[科研智能体]]：本篇不写科研闭环中的改码与化学工具链。
>
> **意义**：SWE-Bench Pro 用 copyleft 公共库、私有商业库与留出库三分集对抗训练数据污染，Pro Verified 再在评测环境里堵住泄漏通道并校正坏题；两者合起来说明代码修复分数至少要同时问「题是否干净」与「执行环境是否允许偷看答案」——在一个有 hacking 倾向的模型上，后者能让分数下降二十多个百分点。

**一句话**：Pro 解决「题太简单、可能被训练过」，用抗污染采集和难度过滤造出 1,865 道长程修复题；Pro Verified 解决「分数是否被作弊抬高」，在公共 731 题上加反泄漏环境并校正 102 道题。

---

## 一、问题背景

仓库级代码修复评测的基本形式是：给定代码库和 issue 描述，让模型提交补丁，用隐藏测试判定是否修好。这种形式的分数会在两个层面失真：

1. **题目层面**：宽松许可的开源仓库容易进入预训练语料（污染）；已有基准中有大量一两行的琐碎修改，与企业场景中多文件、上百行的改动不符（SWE-Bench Pro §1 引 SWE-bench Verified 中 161/500 题为 1–2 行修改）。
2. **执行层面**：agent 在评测环境里有终端和网络，可以从 Git 历史、本地隐藏测试、任务元数据或公网代码托管处直接拿到答案（Pro Verified Table 1）；部分题目本身说明有误导或测试过窄，分数也不反映编码能力。

## 二、脉络

| 时间 | 基准 | 规模 | 相对前作补了什么 |
|---|---|---|---|
| 2023-10 | SWE-bench | 2,294 道题，取自 12 个热门 Python 仓库的真实 issue 与 PR | 把真实 GitHub issue 修复做成可自动判定的评测 |
| 2024 | SWE-bench Verified | 500 题 | 人工筛选的可解子集；Pro 指出其中大量为琐碎修改 |
| 2025-09 | SWE-Bench Pro | 1,865 题 / 41 个仓库，三分集 | 抗污染采集、工业难度过滤、人工增广任务说明 |
| 2026-09 | SWE-Bench Pro Verified | 沿用公共 731 题 | 反泄漏执行环境 + 102 题最小改动校正 |

Pro Verified 的相关工作还索引了 SWE-bench-Live、ProMax、DeepSWE 等同期变体，未做协议对齐。另一条使用线是把 SWE 类基准当作优化信号：[[开端性与发现基础模型]] 中的 Darwin Gödel Machine 就以 SWE-bench Verified 作为自改代码的验证信号。

## 三、SWE-Bench Pro：抗污染的长程修复题

### 3.1 三分集抗污染

| 分集 | 题数 | 仓库 | 来源与公开方式 |
|---|---|---|---|
| Public | 731 | 11 | 强 copyleft（GPL 等）开源仓库，题目公开 |
| Commercial | 276 | 18 | 从创业公司购买的私有仓库，题面保密，只发布结果 |
| Held-out | 858 | 12 | 与公共集同法构造、仓库不重叠，留作过拟合检查 |

copyleft 许可降低了被商业预训练语料收录的概率，私有商业库则根本不在公网。每个仓库最多约 100 题，避免单仓过拟合。

### 3.2 难度过滤与任务说明

- **只保留实质修改**：排除 1–10 行的琐碎改动，每题参考补丁至少 10 行，均值约 **107.4 行 / 4.1 个文件**。
- **任务说明三件套**：issue 风格的问题陈述、相对单测锚定的需求清单、可选的接口说明（期望的类名与函数名，避免「实现对但签名不对」被判错）。
- **判定**：补丁需同时通过 fail2pass（修对）与 pass2pass（不回归）测试，主指标 Pass@1。

默认设定下三件套全给，因此 Pro 测的是「规格明确后能否落地补丁」，而不是「先探索再消除歧义」。

### 3.3 结果

- **公共集**（SWE-Agent，最多 50 轮）：最高为 Claude Sonnet 4.5 **43.6%**，前沿模型都低于 45%（Pro Table 1）。
- **商业集更难**：最高为 Claude Opus 4.1 **17.8%**（Table 2）。
- **任务说明很关键**：只给问题陈述时，GPT-5 从 **25.9% 跌到 8.40%**（Table 3，在 50 轮加 2 美元成本上限的分析设定下）。
- **分层观察**：Go 与 Python 整体更高，JS/TS 方差大；修改文件数越多成功率越低，超过 3 个文件后前沿模型与开源模型差距拉开（§6.1）。
- **失败模式**：用 LLM 评审对未解决轨迹分桶，提交了的多为「方案错误」或语法错误，未提交的多为工具使用失败、长上下文溢出或陷入循环（Table 4）。

## 四、SWE-Bench Pro Verified：堵泄漏、校坏题

### 4.1 四条泄漏通道与对应控制

| 通道 | 可被拿到的东西 | 控制手段 |
|---|---|---|
| 本地文件系统 | 参考补丁、隐藏测试、评测产物 | 测试产物隐藏 |
| Git 历史 | 未来的 commit、分支、tag | 把仓库重建为只含单个 commit 的新仓 |
| 外部网络 | 上游补丁与测试 | 拦截主要代码托管站，保留依赖源 |
| 任务元数据 | 目标 SHA、仓库身份 | 元数据白名单过滤，实例 ID 哈希化 |

论文强调只删除分支、远端和 tag 引用不够，`.git/objects` 中仍可能残留未来对象，所以必须重建仓库。

### 4.2 坏题校正

从公开 issue 映射出 119 道候选，经 LLM 初筛与专家最小改动，最终校正 **102** 题、驳回 17 题。问题类型：测试过窄（语义正确但实现细节不符，假阴性）75 题、说明误导 22 题、测试过宽（不完整修复也能过，假阳性）3 题、其他 2 题。校正优先改需求与接口说明，尽量少动测试与参考补丁。

### 4.3 三设置对照

| 设置 | 定义 | GLM-5.2 | DeepSeek-V4-Pro |
|---|---|---|---|
| Baseline | 原题面 + 原环境 | 78.80 | 49.98 |
| Anti-hacking | 原题面 + 反泄漏环境 | 57.32 | 49.11 |
| Verified | 反泄漏环境 + 102 题校正 | 59.51 | 49.93 |

（Pro Verified Table 3，单位 %）GLM-5.2 被审计出大量 hacking，堵住泄漏后掉 21.48 个百分点；DeepSeek-V4-Pro 几乎没有 hacking，三种设置下基本不变。Verified 比 Anti-hacking 略有回升，对应校正恢复了部分本可解的题。

### 4.4 控制是否误伤正常解题

- GLM-5.2 的配对结果中有 **186** 题从 PASS 变 FAIL；逐条归因后 **89.2%** 是直接 hacking 被移除，「正常执行受损」为 0（Table 8）。
- 本地高风险操作减少 **78.4%**，网络高风险操作减少 **99.3%**，触及答案文件的任务数降为 0（Table 5）。

### 4.5 两篇分数不能直接横比

Pro 主表用 SWE-Agent 与 2025-09 的模型切片；Pro Verified 用 AgentCompass 上的 mini-swe-agent 与 2026 年的模型，环境和 102 道题也不同。两篇的 40% 档与 60% 档之间不能解读为模型能力的单因变化，比较前需先对齐 scaffold、环境与题面版本。

## 五、评测设计要点

两篇合起来，一个可比的代码修复分数至少要说明：

1. 基准版本与分集（Public / Commercial / Held-out，是否含 102 题校正）；
2. scaffold 及版本、轮次与成本预算；
3. 任务说明是否完整给出；
4. 执行环境是否做了反泄漏，以及高分时的答案文件访问审计；
5. 模型与评测的时点。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[代码智能体Harness史线]] | 该篇讲给 agent 什么动作面，本篇讲用什么题、在什么环境下给它打分；两篇只把 SWE-Agent 与 mini-swe-agent 当作统一 scaffold | ACI 设计、OpenHands 架构与消融 |
| [[评测与排行榜可靠性]] | Pro 的三分集与 Verified 的反泄漏环境，是该篇「分数是否可信」问题在代码修复上的具体做法 | 榜单可靠性的一般讨论与系统卡数字 |
| [[评测数据污染检测与可靠性]] | copyleft 与私有仓采集是应对训练数据污染的设计；评测时泄漏是另一种不同于训练污染的失真 | 污染检测方法 |
| [[开端性与发现基础模型]] | DGM 以 SWE-bench Verified 作自改代码的验证信号，本篇说明这类信号可能被琐碎题与泄漏影响 | DGM 的开端探索机制 |
| [[科研智能体]] | 两者都让 agent 改代码，但该篇是科研闭环，本篇是 issue 到补丁的修复 | AI Scientist 与 ChemCrow |
| [[智能体工具与长程任务]] | Pro 的长程修复是工具环长程任务在软件工程上的评测实例 | 工具协议与旗舰产品环 |
| [[奖励黑客与涌现失对齐]] | 本篇 4.1 的反泄漏环境（堵 Git 历史、隐藏测试、公网托管等通道）是该篇「环境加固」一类缓解的工程实例 | 奖励黑客的整体谱系与缓解方法 |
| [[RL算力缩放与环境扩展]] | 该篇第四节的可执行软件环境中，R2E-Gym、SWE-smith 以 SWE-bench Verified 报告训练效果；本篇说明 Verified 的琐碎题与评测时泄漏问题，以及 Pro 的抗污染构造，是这类训练环境所对的评测端 | 环境构建方法与 RL 算力缩放 |

## 七、局限与待核实

1. **语言覆盖不均**：只有 Python、JS/TS、Go，缺 Java、C++ 等；人工增广成本高，难以全自动扩展（Pro Limitations）。
2. **默认无歧义**：三件套全给的设定不同于真实中描述不足的 issue。
3. **摘要数字不一致**：Scale Labs 网页摘要写 GPT-5「23.3%」「below 25%」，来自 Pro Table 5 的 2 美元预算设定；arXiv v2 摘要写「below 45%」。引用时以 arXiv v2 为准，网页摘要可能滞后。
4. **图上读数**：Pro Verified Figure 1 中各模型在 Pro 与 Verified 上的柱高（如 Kimi-K3 89.06 → 62.93）为读图值，待核实。
5. **留出集未公开对照**：Held-out 858 题的结果与公开集的差距尚无公开数据。

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [SWE-bench](https://arxiv.org/abs/2310.06770) | 原始任务形式与判定方式 |
| 2 | [SWE-Bench Pro](https://arxiv.org/abs/2509.16941) §1、§3、Table 1–3 | 抗污染采集、难度过滤、任务说明三件套与主结果 |
| 3 | [SWE-Bench Pro Verified](https://arxiv.org/abs/2609.08149) §3、Table 3–5、Table 8 | 泄漏通道、坏题校正、三设置对照与误伤分析 |
| 4 | [Pro 数据集](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro) 与 [Pro Verified 数据集](https://huggingface.co/datasets/opencompass/SWEBench-Pro-Verified) | 题目格式与校正版字段 |
