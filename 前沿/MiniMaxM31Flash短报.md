---
date: 2026-10-20
status: archived
archived: 2026-10-20
topic: MiniMaxM31Flash短报
title: "MiniMax M3.1 Flash（前沿短报）"
lines: [智能体, 效率与定价, 厂商自测]
sources:
 - https://www.minimax.io/blog/minimax-m31f
 - https://platform.minimax.io
 - https://agent.minimax.io/download
related: ["MiniMaxM1技术报告深读", "开源与闭源前沿模型谱系", "MistralLarge4短报"]
retrieval_cutoff: 2026-10-19
timezone: Asia/Shanghai (CST)
---

# MiniMax M3.1 Flash（前沿短报）

> **主要来源**：[MiniMax M3.1 Flash: Redefining Agent Performance and Cost](https://www.minimax.io/blog/minimax-m31f)（MiniMax，页面标 2026-10-19）（截至 2026-10-19）。下文「博文」指该发布页。API 与桌面入口见 [platform.minimax.io](https://platform.minimax.io)、[agent.minimax.io/download](https://agent.minimax.io/download)（仅用于核对入口，不引事实）。
> **研究线**：智能体（复杂任务、编码、Computer Use）· 效率与定价（稀疏推理与按 token 计价）· 厂商自测（无第三方复核）
> **范围与相邻笔记**：
> - ≠ [[MiniMaxM1技术报告深读]]：那篇是 M1 代开放权重混合注意力推理模型的技术报告；本篇是 M3.1 Flash 产品节点，**非同代**，无技术报告，只作旁链。
> - ≠ [[开源与闭源前沿模型谱系]]：本篇不复述谱系；权重尚未发布，不作开放权重节点。
> - ≠ [[MistralLarge4短报]]：两者只对照「API 先发、材料以厂商博文为主」的发布形态，不复述对方能力。
>
> **意义**：M3.1 Flash 把下一代 Flash 定位在智能体任务上的性能–成本平衡：官方称在复杂智能体、编码、Computer Use 与网络安全上相对上一代有明显提升，同时在线推理更快、使用成本更低。截至 2026-10-19 无技术报告、权重未发，本篇只记录产品节点与披露边界。

**一句话**：MiniMax 于 2026-10-19 发布 MiniMax M3.1 Flash；官方称其为下一代 Flash，面向复杂智能体、编码、Computer Use 与网络安全，在线推理相对上一代近 3 倍速、使用成本约降 70%（均为厂商自述）。无技术报告；权重称稍后发布。

## 一、产品节点

博文称 M3.1 Flash 已正式上线，可通过 MiniMax API、M Plan 与 MiniMax Code 使用；桌面端提供 MiniMax Code 下载。匿名运营的 Space Bunny 被官方称为其早期版本，并称该版本处理了超过 200 万亿 token（厂商自述）。

与库内 [[MiniMaxM1技术报告深读]] 的关系：M1 是带技术报告的开放权重混合注意力推理模型；M3.1 Flash 是其后的 Flash 产品节点，材料只有厂商博文，**不能**按同模型 minor update 写 addendum。官方另称推动能力上限的 Pro「也将到来」，截至本篇截至日尚未发布。

## 二、效率与定价（厂商自述）

- **推理效率**：官方称通过更激进的稀疏化优化推理；日常输出可达 200+ TPS（tokens per second），P50 约 170+ TPS。
- **相对上一代**：在线推理近 3 倍速；智能体任务整体使用成本约降 70%。
- **定价**（美元 / 百万 token）：输入 $0.15、输出 $0.60、缓存输入 $0.015。

以上速度、倍数与成本降幅均为厂商自述，未见第三方复核。

## 三、能力取向与代表性基准

官方称 M3.1 Flash 在复杂智能体任务（cowork）、Computer Use、软件开发与网络安全上达到领先模型水平（厂商自述）。博文给出的基准**全部为厂商自测**；本篇只点类别与少量代表性数字，不堆分表。

| 类别 | 代表性基准（博文） | 说明 |
|---|---|---|
| 复杂任务与工具链 | AutomationBench-AA；BankerToolBench（76.2） | 企业工作流、多步规划与链式工具调用 |
| 编码 | DeepSWE v1.1（73.7%） | 长序列软件工程执行 |
| Computer Use | OSWorld V2（61.7） | 跨应用操作；官方另报 Agents' Last Exam，称两项在中国模型中均第一（自述） |
| 网络安全 | CyberGym（82%） | 只点类别与厂商自述分数；不展开题面与方法 |

官方另称在 Automation-Bench、DeepSWE 与 Agents' Last Exam 三项上，以很低的任务成本达到与顶尖模型相当的表现（厂商自述）。对照模型、harness 与评测时点均由厂商选定。

## 四、局限与争议

1. **无技术报告**：架构、训练、数据与奖励设计均未披露；本篇不作方法推测。
2. **权重未发**：博文写「Model weights will be released later」；截至 2026-10-19 未见官方权重页，不能按开放权重节点写入谱系。
3. **全为厂商自测**：基准与「达到领先模型水平」「近 3 倍速」「成本降约 70%」等均为自述，无第三方复核；与同价位 Flash 横比须另核数据来源与时点。
4. **Pro 未发布**：官方预告 Pro 将至，本篇不把它当作已发布产品。

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[MiniMaxM1技术报告深读]] | 旁链：标明非同代；那篇是 M1 技术报告深读 | M1 的混合注意力、CISPO 与报告数字 |
| [[开源与闭源前沿模型谱系]] | 所在谱系：本篇是 Flash 代 API 产品节点 | 谱系各代模型 |
| [[MistralLarge4短报]] | 发布形态对照：API 先发、材料以厂商博文为主 | Large 4 的规格与网安叙事 |

## 六、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [MiniMax M3.1 Flash 博文](https://www.minimax.io/blog/minimax-m31f) | 定位、基准类别、效率与定价 |
| 2 | [MiniMax API](https://platform.minimax.io) | 调用入口 |
| 3 | [MiniMax Code 下载](https://agent.minimax.io/download) | 桌面端入口 |
