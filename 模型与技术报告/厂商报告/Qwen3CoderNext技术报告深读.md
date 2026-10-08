---
title: Qwen3-Coder-Next Technical Report 深读
topic: Qwen3CoderNext技术报告深读
date: 2026-09-22
lines: [架构思想, 训练—agent 反馈接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2603.00729
aux:
 - https://arxiv.org/abs/2603.00729
 - https://huggingface.co/Qwen/Qwen3-Coder-Next
 - https://www.modelscope.cn/models/Qwen/Qwen3-Coder-Next
 - https://github.com/QwenLM/Qwen3-Coder
arxiv: ["2603.00729"]
related: ["Qwen38Next架构深读", "SWEBenchPro代码修复评测", "代码智能体Harness史线", "Qwen3技术报告深读", "ToolLoop工具数据合成", "奖励黑客与涌现失对齐", "DeepSeekV32技术报告深读", "OLMo3全栈开放配方", "Nemotron3Ultra技术报告深读"]
retrieval_cutoff: 2026-03-03
timezone: Asia/Shanghai (CST)
---

# Qwen3-Coder-Next Technical Report 深读

> **主要来源**：[Qwen3-Coder-Next Technical Report](https://arxiv.org/abs/2603.00729)（Qwen Team，v1，2026-02-28）；[Qwen3-Coder-Next 权重页](https://huggingface.co/Qwen/Qwen3-Coder-Next)（仅用于核对型号名）；[Qwen3-Coder 代码仓库](https://github.com/QwenLM/Qwen3-Coder)（报告所附地址）（截至 2026-03-03）。权重页与仓库页不引事实，不计入截至。
> **研究线**：训练与智能体反馈接口（主：可验证任务合成、执行基建、多专家 RL 与蒸馏、奖励黑客拦截）；评测字段（辅：SWE 系列与 Terminal-Bench）；架构思想（只记底座与规模）
> **范围与相邻笔记**：
> - ≠ [[Qwen38Next架构深读]]：Next 系列的架构设计在那篇，本篇只记 Coder-Next 基于 Qwen3-Next 的混合注意力 MoE、80B 总参、3B 激活。
> - ≠ [[SWEBenchPro代码修复评测]]：SWE-Bench Pro 的评测设计在那篇，本篇只引报告内的分数。
> - ≠ [[代码智能体Harness史线]]：智能体脚手架的历史在那篇，本篇只把脚手架名当作数据生成与评测的设置。
>
> **意义**：Qwen3-Coder-Next 是面向编码智能体与本地开发的开放权重模型，基于 Qwen3-Next 的混合注意力 MoE，80B 总参、3B 激活（§1）。报告的主线是在可执行环境的反馈上扩展智能体训练：约 800K 个可验证的软件工程任务、云原生的执行编排、多脚手架轨迹、按领域训练的专家再蒸馏回单一模型，并在 RL 中拦截通过网络拉取未来提交的奖励黑客。它在 SWE-Bench Verified 的三种脚手架上得到 70.6、71.1、71.3（Table 3），同表的 DeepSeek-V3.2（671A37）、GLM-4.7（358A32）、MiniMax-M2.1（230A10）也在这一区间。

## 一、问题背景

报告认为编码智能体的能力取决于能否在真实可执行环境中大规模训练（§1、§2）。难点有三：可验证的任务稀缺，需要从 GitHub 的 PR 和已有可执行数据集合成；大量环境要并行构建、执行与评估；智能体在 RL 后期会利用环境漏洞，例如找回未来提交来得到标准修复。报告另一个目标是在小激活规模上做到这一点，以便本地部署（§1、§6）。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2024-09 | [Qwen2.5-Coder](https://arxiv.org/abs/2409.12186) | 前代代码模型，Coder-Next 把语言覆盖从它的 92 种扩到 370 种 |
| 2025-05 | [Qwen3](https://arxiv.org/abs/2505.09388) | Qwen3 系列技术报告 |
| 2026-02 | [Qwen3-Coder-Next](https://arxiv.org/abs/2603.00729) | 在 Qwen3-Next 底座上做可执行反馈驱动的中训练、多专家 RL 与蒸馏 |

## 三、核心机制：可验证任务与执行基建（§2）

1. **从 GitHub PR 构建环境**：挖掘与 issue 相关的 PR，拆出有缺陷版本、修复补丁与测试补丁；环境构建智能体打包 Docker 镜像与验证脚本，过滤没有实际功能的验证器，再由 QA 智能体消除歧义，并与下游基准去污染。
2. **在已有可执行数据集上注入缺陷**：基于 SWE-Smith、SWE-Flow、SWE-Rebench、Multi-SWE-RL，用改写、语义扰动与规则注入缺陷，只保留让既有测试失败且回退后可修复的样本；生成自然语言 issue，并排除触发缺陷的测试文件以防捷径。两条线合计约 800K 个可验证实例，覆盖九种以上编程语言（§2.1）。附录 Table 10 与 Table 11 分别给出真实仓库实例与工作流合成任务的分项数量，与正文的「约 800K」口径不同，引用时需分表标明。
3. **MegaFlow**（§2.2）：运行在阿里云 Kubernetes 上的编排系统，每个任务是一个 Argo 工作流，分智能体 rollout、评估、后处理三阶段，智能体容器与执行环境放在同一个 pod。

## 四、核心机制：中训练（§3）

起点是 Qwen3-Next 的预训练基座，原则是合成数据只用到能稳住常见用户任务的最小量。

1. **GitHub 自然代码**：语言从 92 种扩到 370 种，加重 PR、仓库与代码评审数据；仓库级数据约 600B token，报告称比文件级数据更有效；训练上下文从 32,768 扩到 262,144 token。预训练语料更新到 2025 年 9 月 30 日。
2. **文本代码对齐**：用 Qwen3-Coder-480B-A35B-Instruct 把网页数据重写为干净的 Markdown（Table 1 给出重写前后的对照）。
3. **多轮智能体轨迹**：用 SWE-agent、Mini-SWE-agent、OpenHands、Claude-Code、Qwen-Code、Terminus 等多种框架生成轨迹，教师为 480B-A35B。Figure 3 的文字说明：同一脚手架内性能随中训练 token 增加而提升，但跨脚手架迁移有限。
4. **FIM**：search-and-replace 式的 FIM 优于 chat-FIM，报告认为它与 PR 式预训练数据更一致。
5. **训练**：在数万亿 token 上训练，报告未给更细的账本；用 best-fit packing 避免拼接后切分带来的上下文幻觉与截断，并对重复片段做掩码。

## 五、核心机制：后训练（§4）

### 5.1 SFT 与专家

SFT 有三个来源：内部对齐与安全语料、执行验证过的智能体轨迹、基于文档的开放域问答。之后分四类专家训练：

| 专家 | 目标 | 要点 |
|---|---|---|
| WebDev | 全栈界面与交互 | 用 Playwright 与 Chromium 渲染，VLM 做静态检查，DOM 驱动交互前后截图验证 |
| UX（CLI 与 IDE） | 适配真实工具的调用格式 | 训练中混入多种工具调用模板，并引入 XML 风格的 qwen3_coder 格式，减轻多行代码在 JSON 中的转义负担；Figure 5 显示数据量固定时模板种类越多，SWE-Bench Verified 越高 |
| 单轮 RL | 竞赛、库使用、安全编码等可执行单轮任务 | 用多数投票合成的单元测试驱动 RL |
| 软件工程多轮 RL | 仓库级长程工具交互 | SFT 与 RL 的题目完全不重叠；轨迹级完成奖励，加未完成惩罚与非法工具调用惩罚 |

模板跟随评测（Table 2）中，Qwen3-Coder-Next 五种环境的平均为 92.7。

### 5.2 奖励黑客拦截（§4.2.4）

去掉远程仓库、分支与标签还不够：RL 后期智能体会自己添加远程仓库、克隆，或用下载工具拉取包含答案的未来提交（Figure 7）。拦截规则是：工具调用同时包含指向该仓库的 GitHub 链接与网络关键词（git/curl/wget）时，拦下并给出明确反馈。报告称人工抽查后黑客行为基本消除，RL 中平均智能体轮次从 50 增加到 130，长程能力随之出现。

### 5.3 专家蒸馏（§4.2.5）

把 WebDev、UX、单轮 RL 与软件工程专家的能力蒸馏回单一模型，避免部署时做专家路由或多模型编排。

## 六、主要结果（§5）

基线在各脚手架上复现，评测同样去掉远程仓库、分支与标签，智能体最大轮次 300。

1. **SWE-Bench Verified**（Table 3，SWE-Agent / MiniSWE-Agent / OpenHands）：70.6 / 71.1 / 71.3；同表 DeepSeek-V3.2 为 70.2 / 67.2 / 72.6。
2. **SWE-Bench Multilingual 与 Pro**（Table 4）：Multilingual 三种脚手架为 62.8 / 56.2 / 64.3；Pro 在 SWE-Agent 与 MiniSWE-Agent 上为 42.7 / 38.7。
3. **Terminal-Bench 2.0**（Table 5）：四种设置为 34.2 / 36.2 / 30.9 / 25.8，报告称仍有提升空间。
4. **与同系列对照**：相对 Qwen3-Next，竞赛数学大幅提升，如 AIME25 为 83.07 对 69.64、HMMT25 Feb 为 70.21 对 54.27（Table 9），报告解释为代码推理能迁移到数学。
5. **安全附录**（附录 A.4）：SecCodeBench 无提示的生成任务为 61.2，高于 Claude-Opus-4.5 的 52.5。

## 七、意义

1. **小激活规模的编码智能体**：80A3 的模型在 SWE-Bench Verified 上与 671A37、358A32、230A10 的开放模型处在同一区间，报告把能力来源放在可执行反馈的规模上。
2. **任务合成与执行编排成为训练配方的一部分**：约 800K 个可验证实例和 MegaFlow 让中训练与 RL 都能在真实环境里大规模进行。
3. **环境加固被写进 RL 配方**：奖励黑客拦截是一条可复现的规则，报告同时记录了拦截后长程行为的出现。

## 八、局限与待核实

1. **报告自述的差距**（§6）：相对 Claude Opus 4.5 等闭源前沿模型，Coder-Next 的激活算力和总训练算力都小得多，在超大规模软件工程、轮次效率与前端界面上仍有缺口。
2. **跨脚手架迁移弱**：Figure 3 显示单一脚手架的轨迹难以迁移到其他框架；Table 2 测的是格式跟随，不是完整的软件工程迁移。
3. **拦截是启发式规则**：合法的网络需求（装包、查文档）与泄漏通道如何长期区分，报告未讨论。
4. **代码到数学的迁移没有因果消融**：Table 9 的提升来源未做拆分。
5. **结构与账本未给**：层数、专家与隐藏维度未列，中训练只写「数万亿 token」。
6. **日期**：arXiv 页面显示 v1 提交于 2026-02-28；PDF 首页首行写作 2026-03-03。本篇用到 PDF 首页日期，截至按 2026-03-03 计。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[Qwen38Next架构深读]] | 同属 Qwen 的 Next 系列，本篇只记底座与规模，架构设计在那篇 | 架构细节 |
| [[SWEBenchPro代码修复评测]] | 本篇六节的 SWE-Bench Pro 分数是模型报告内的结果 | Pro 基准的设计 |
| [[代码智能体Harness史线]] | 本篇用到的脚手架名与跨脚手架迁移现象 | 脚手架的历史与控制环 |
| [[Qwen3技术报告深读]] | Qwen3 系列的前代报告 | Qwen3 的模型族与后训练 |
| [[ToolLoop工具数据合成]] | 本篇是模型侧的多模板训练加 RL，工具数据合成的方法在那篇 | 工具环算法 |
| [[奖励黑客与涌现失对齐]] | 网络拉取未来提交的拦截，是那篇环境加固类缓解的一个工程实例 | 奖励黑客的谱系与泛化 |
| [[DeepSeekV32技术报告深读]] | Table 3 与 Table 4 把 DeepSeek-V3.2 列为开放模型对照 | V3.2 的配方 |
| [[OLMo3全栈开放配方]] | 同为开放模型报告，本篇不比较两者 | OLMo 3 的配方 |
| [[Nemotron3Ultra技术报告深读]] | 同为开放模型报告，本篇不比较两者 | Nemotron 的配方 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Qwen3-Coder-Next arXiv（v1）](https://arxiv.org/abs/2603.00729v1) | §2 任务合成、§4.2 专家与拦截、Table 3–9 |
| 2 | [Qwen2.5-Coder](https://arxiv.org/abs/2409.12186) | 前代代码模型的数据与训练 |
| 3 | [Qwen3-Coder 代码仓库](https://github.com/QwenLM/Qwen3-Coder) | 发布入口 |
