---
date: 2026-10-20
status: archived
archived: 2026-10-20
topic: Mercury3短报
title: "Mercury 3（前沿短报）"
lines: [扩散语言模型, 商用节点, 厂商自述]
sources:
 - https://www.inceptionlabs.ai/blog/introducing-mercury-3
related: ["扩散语言模型", "开源与闭源前沿模型谱系", "ClaudeHaiku55系统卡短报"]
retrieval_cutoff: 2026-10-19
timezone: Asia/Shanghai (CST)
---

# Mercury 3（前沿短报）

> **主要来源**：[Diffusion at Scale: Introducing Mercury 3](https://www.inceptionlabs.ai/blog/introducing-mercury-3)（Inception Labs，栏目标 Product · Oct 19, 2026）（截至 2026-10-19）。下文「博文」指该发布页。
> **研究线**：扩散语言模型（商用 dLLM 旗舰节点）· 厂商自述（速度与对标）· 产品可用性
> **范围与相邻笔记**：
> - ≠ [[扩散语言模型]]：那篇锚 LLaDA / Dream 学术线与掩码扩散机制；本篇不写扩散数学，只记 Inception Mercury 产品谱系上的商用旗舰节点。
> - ≠ [[开源与闭源前沿模型谱系]]：本篇不复述谱系全表。
> - ≠ [[ClaudeHaiku55系统卡短报]]：博文把 Haiku 5.5 列为速度档对照之一，本篇不复述其系统卡。
>
> **意义**：官方称 Mercury 3 证明文本扩散可以放大：相对 Mercury 1 总参约 40×，仍保持速度档，并自称与 GPT-6 Luna、Claude Haiku 5.5 等同档速度优化模型对标或更好（均为厂商自述）。库内学术扩散篇讨论「非自回归可扩」；本篇提供对应的商用产品声明，二者互补、不互替。

**一句话**：Inception Labs 于 2026-10-19 发布 Mercury 3，自称迄今最强的扩散语言模型（dLLM，diffusion LLM）；上下文 1M token，标价输入 $0.20 / 输出 $0.70（每百万 token）。无新技术报告；参数量只给相对 Mercury 1「约 40×」的口径。

## 一、产品节点

博文栏目标 *Product · Oct 19, 2026*。Mercury 3 定位为实时 AI 产品组合中的旗舰；同页旁注 Mercury Voice（语音低延迟）与 Mercury Decide（高通量分类决策），本篇不单独立项。

可用性：Inception API，以及 OpenRouter、Baseten、Vercel；官方称兼容 OpenAI API，可接入现有调用栈。提供对话试用、API 文档与企业评估入口。

## 二、规格与定价（厂商自述）

- **规模**：相对 Mercury 1 总参约 **40×**；博客未给出 Mercury 3 的绝对参数量。另称从 Mercury 1（mini）到 Mercury 3，标准基准上的「智力」约升 3×（自述，未定义度量）。
- **上下文**：1M token（相对 Mercury 2.5 的 260K）。
- **速度**：称约 4–8× 更快，NVIDIA GPU 上约 1,068 tokens per second（厂商自述）。
- **对标**：称在一系列基准上优于或持平 GPT-6 Luna 与 Claude Haiku 5.5 等同档速度优化模型（厂商自述；对照由厂商选定）。
- **定价**（美元 / 百万 token）：标价输入 $0.20、输出 $0.70；上线优惠 50%（$0.10 / $0.35）；缓存 token 相对输入价减免 90%（博文原文：Cached tokens are 90% off the input price）。

## 三、场景说明（非独立评测）

博文列举早期合作方场景：浏览器智能体、互动教育、实时搜索、客服等，用作延迟敏感场景说明，**不作**独立评测证据。其中浏览器智能体一节称在自有 web-agent harness 上、50 道 live Mind2Web 导航任务中完成 50%，并称显著高于 GPT-6.1-Sol（厂商 / 合作方自测）。本篇不展开该评测设置。

## 四、局限与争议

1. **无公开技术报告**：训练、数据、扩散采样与系统实现均未披露；参数量只有相对 Mercury 1 的约 40× 口径。
2. **速度与对标均为厂商自述**：「4–8× 更快」「1,068 TPS」「优于 Luna / Haiku 5.5」等未见第三方复核；基准表与 harness 未在博文中系统给出。
3. **Mind2Web 等为自测**：50 道任务、自有 harness，样本与设置不透明。
4. **Voice / Decide**：仅作产品组合旁注，本篇不评其基准声明（如 Decide 对 JevBench / LegalBench 的自述）。

## 五、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[扩散语言模型]] | 关系：学术掩码扩散线与本篇商用 dLLM 节点互补；本篇只提供「扩参仍宣称保持速度档」的产品声明，因截至 2026-10-19 未见 Mercury 3 新技术报告而不扩写配方 | LLaDA / Dream 的训练目标、采样与结果；掩码扩散数学 |
| [[开源与闭源前沿模型谱系]] | 所在谱系：商用 dLLM 旗舰产品节点 | 谱系各代模型 |
| [[ClaudeHaiku55系统卡短报]] | 对照对象之一出现在厂商对标句中 | Haiku 5.5 的系统卡与安全评测 |

## 六、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Introducing Mercury 3](https://www.inceptionlabs.ai/blog/introducing-mercury-3) | 定位、规格、定价与场景引言 |
