---
date: 2026-10-21
status: archived
archived: 2026-10-21
topic: Ornith15-122B短报
title: "Ornith-1.5-122B（前沿短报）"
lines: [开源权重, MoE, 厂商自测]
sources:
 - https://huggingface.co/ornith-ai/Ornith-1.5-122B
 - https://x.com/ornith_/status/2112553477457268799
 - https://ornith.ai/ornith_1_5.html
related: ["开源与闭源前沿模型谱系"]
retrieval_cutoff: 2026-10-20
timezone: Asia/Shanghai (CST)
---

# Ornith-1.5-122B（前沿短报）

> **主要来源**：[ornith-ai/Ornith-1.5-122B](https://huggingface.co/ornith-ai/Ornith-1.5-122B)（Hugging Face 模型卡）；官方 X 宣布帖 [Meet Ornith-1.5-122B](https://x.com/ornith_/status/2112553477457268799)（2026-10-20 14:36 UTC，上海 22:36）（截至 2026-10-20）。家族方法页 [Ornith-1.5: From Self-Scaffolding to Self-Improvement](https://ornith.ai/ornith_1_5.html)（Ornith，栏目标 Aug. 2026）只作旁链，本篇不展开配方。
> **研究线**：开源权重（122B MoE 节点）· 单卡可服叙事（厂商自述）· 厂商自测（编码 / 智能体等类别，不堆分）
> **范围与相邻笔记**：
> - ≠ [[开源与闭源前沿模型谱系]]：本篇不复述谱系全表；可作为开源 MoE 档时间线节点旁链。
> - ≠ [[DeepInfer短报]]：同窗对照轴为「栈开 vs 权重开」——DeepInfer 开生产推理栈、本篇开权重；互不替对方材料。
> - 方法页为 2026-08 家族文；本篇只记 122B 开源节点，不重开 Self-Scaffolding / Self-Improvement 通史。
>
> **意义**：Ornith 在 1.5 家族上新增 122B MoE 开放权重档，官方称可在单张 80GB GPU（或单张 NVIDIA DGX）上服务，并强调编码与智能体向能力（均为厂商自述）。无 122B 专属技术报告；基准全为模型卡 / 厂商自测。

**一句话**：Ornith 于 2026-10-20 开源 Ornith-1.5-122B（122B MoE，MIT）；模型卡称可在单张 80GB GPU 上服务，上下文标 262K，可用 YaRN 扩展（均为厂商自述）。

## 一、产品节点

模型卡将 Ornith-1.5-122B 记为 1.5 家族「最强且偏高效」成员：122B MoE 推理模型，面向高效单卡部署；另有量化 Mobile 变体旁注，本篇不展开端侧。官方 X 称开放权重、MIT，并称在可比规模开源模型中达到顶尖表现、可跑在单张 NVIDIA DGX 上（厂商自述）。

与同窗 [[DeepInfer短报]] 对照一句即可：**栈开 vs 权重开**——DeepInfer 开的是 V4.1-Flash 生产推理栈的离线子集；本篇开的是 Ornith 权重本身。

## 二、规格与可用性（厂商自述）

- **规模与许可**：122B MoE；开放权重，MIT。
- **上下文**：标 262,144 token；任务输入+输出需更长时，官方建议用 YaRN（RoPE scaling）扩展，并称 factor 4.0 时可用窗口大约到 1M token（厂商自述；已写入 vLLM / SGLang 用法说明）。
- **推理形态**：reasoning 模型；助手轮默认以 think 块再给最终答案；服务侧可用 reasoning parser，把思维链放到 `reasoning_content`。
- **工具调用**：发出 `<tool_call>` 块，经服务端解析为 OpenAI 风格 `tool_calls`。
- **服务入口**：Hugging Face 权重；文档给出 vLLM（≥ 0.19.1）、SGLang（≥ 0.5.9）、Ollama（`ollama run ornith-1.5:122b`）等；社区量化（GGUF、Atomic.chat、Unsloth 等）作生态旁注即可，本篇不评量化质量。

「单张 80GB GPU 可服」依赖具体精度、并行与显存占用设置，稿中一律按厂商自述，不作部署保证。

## 三、能力取向与代表性基准

模型卡基准**全部为厂商自测**；本篇只点类别，不堆分表。CyberGym **只点类别**，不展开题面与方法。

| 类别 | 代表性基准（模型卡点名） | 说明 |
|---|---|---|
| 编码 | SWE-bench Verified / Pro（及 Multilingual）；Terminal-Bench 2.1；NL2Repo | 软件工程与终端智能体向 |
| 智能体 | BrowseComp；MCP-Atlas；Toolathlon-Verified；WideSearch；ClawEval 等 | 浏览、工具与任务分布向 |
| 网络安全 | CyberGym | 只点类别；不展开题面与方法 |
| 推理 | HLE（with / without tools）；SciCode | 模型卡另列；本篇不展开 |

对照模型与 harness 均由厂商选定；无第三方复核。

## 四、方法外链（不展开）

家族方法指向 2026-08 页 [Ornith-1.5: From Self-Scaffolding to Self-Improvement](https://ornith.ai/ornith_1_5.html)：Self-Scaffolding → Self-Improvement。该页覆盖 397B / 35B / 9B 等既有档位；**无** 122B 专属方法披露。短报不写任务生成、scaffold 与 GRPO 配方。

## 五、局限与争议

1. **无 122B 专属方法披露**：训练、数据与奖励设计未随本档单独成文；只能旁链 8 月家族页。
2. **基准为自测**：编码 / 智能体 / CyberGym 等分数与「可比规模 SOTA」均为厂商自述。
3. **单卡可服依赖设置**：80GB / 单 DGX 叙事依赖精度、TP 与运行时版本；模型卡示例默认未强制多卡，但不等于任意精度下可服。
4. **与 DeepInfer 不可横向比能力**：一为栈、一为权重，同窗只作开放形态对照。

## 六、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[开源与闭源前沿模型谱系]] | 所在谱系：开源 MoE 权重节点 | 谱系各代模型 |
| [[DeepInfer短报]] | 对照轴：栈开 vs 权重开 | DeepInfer 的离线边界与硬件表 |

## 七、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Ornith-1.5-122B 模型卡](https://huggingface.co/ornith-ai/Ornith-1.5-122B) | 定位、规格、服务命令、基准类别 |
| 2 | [官方 X 宣布帖](https://x.com/ornith_/status/2112553477457268799) | 窗内首发口径与 MIT |
| 3 | [Ornith-1.5 家族方法页](https://ornith.ai/ornith_1_5.html) | Self-Scaffolding → Self-Improvement（旁链，不深挖） |
