---
title: "Prompt / Prefix Caching：模块化复用与计费经济学"
topic: Prompt前缀缓存
date: 2026-09-22
lines: [AI Infra, 成本模型]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2311.04934
 - https://arxiv.org/abs/2312.07104
arxiv: ["2311.04934", "2312.07104"]
related: ["推理引擎生态", "KV缓存量化与压缩", "DuoAttention与KVzip", "HiCache层次化KV缓存", "上下文工程与智能体技能"]
official_docs_fetched: "2026-09-22 Asia/Shanghai (CST)"
---

# Prompt / Prefix Caching：模块化复用与计费经济学

> **主要来源**：[Prompt Cache: Modular Attention Reuse for Low-Latency Inference（Gim, Chen, Lee, Sarda, Khandelwal, Zhong，Yale / Google，MLSys 2024）](https://arxiv.org/abs/2311.04934)；交叉：[SGLang（Zheng, Yin, Xie 等）](https://arxiv.org/abs/2312.07104)；计费字段：[Anthropic Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)、[OpenAI Prompt Caching](https://developers.openai.com/api/docs/guides/prompt-caching)、[Google Context Caching](https://ai.google.dev/gemini-api/docs/generate-content/caching)（官方页核对于 2026-09-22）
> **研究线**：AI Infra / 成本模型——缓存边界、前缀命中、写入 / 读取 / 存活时间如何决定单位成本
> **范围与相邻笔记**：
> - ≠ [[推理引擎生态]]：本篇不写引擎选型表，RadixAttention 只取「自动前缀复用」一句对照。
> - ≠ [[HiCache层次化KV缓存]]：本篇不写引擎内 KV 的多级存储。
> - ≠ [[KV缓存量化与压缩]]、[[DuoAttention与KVzip]]：本篇不写 KV 的量化与驱逐。
> - 绝对价格（每百万 token 多少美元）易过时，本篇只记字段结构与当日所见倍率。
>
> **意义**：长系统提示、文档、工具模板在请求之间大量重复，重复部分的 prefill 是可以省掉的成本；学术侧的 Prompt Cache 用显式模块把可复用片段的 KV 预先算好再拼接，商业 API 则把前缀缓存拆成写入、读取、存活时间三个计费字段——两者都把 TTFT 与输入成本从「按长度付费」改成「按是否命中付费」。

**一句话**：Prompt Cache 是「把可复用片段声明成模块，预计算 KV 再拼接」；商业 API 缓存是「按前缀命中重新计价：写入略贵、读取便宜、存活时间决定保活成本」。

---

## 一、问题背景：重复前缀的 prefill 浪费

- **KV Cache 只在一个请求内复用**：prefill 一次，之后 decode 只算新 token（Prompt Cache §2.2 引 Pope 等）。但跨请求时，同样的系统消息、模板、文档每次都要重新 prefill。
- **重复很常见**：系统消息、提示模板、文档池、工具使用模板之间高度重叠（Prompt Cache §1）。
- **越长越值得缓存**：缓存片段的存储与复用开销大致随片段长度线性增长，而注意力计算随序列长度近似二次增长，所以片段越长、TTFT 收益越大（Prompt Cache §1、§5.4）。

## 二、脉络

| 节点 | 复用范围 | 来源 |
|---|---|---|
| KV Cache | 同一请求的 decode 步 | Prompt Cache §2.2 引 Pope 等 |
| Prompt Cache（arXiv 2023-11，MLSys 2024） | 跨请求的声明式模块，可不是严格前缀 | Prompt Cache |
| RadixAttention（SGLang，arXiv 2023-12） | 跨请求自动匹配 token 前缀，前缀树 + LRU | SGLang §3 |
| 引擎内多级存储 | 把前缀命中范围扩到主机内存与存储 | [[HiCache层次化KV缓存]] |
| 商业 API 缓存 | 云端前缀命中，按写入 / 读取 / 存活时间计价 | 三家官方页 |

## 三、机制概括

所有前缀缓存都要回答三个问题：

1. **边界谁定**：开发者显式声明（Prompt Cache 的 schema、API 的断点、Google 的显式缓存资源），还是系统自动匹配（RadixAttention、API 的隐式缓存）。
2. **位置怎么处理**：位置编码写进了 K/V，片段换了位置 KV 就不能直接复用。严格前缀匹配回避了这个问题；Prompt Cache 用固定起始位置绕过它。
3. **存多久、谁付钱**：自建系统里是显存与驱逐策略（LRU）；云 API 里是 TTL 与存储费。

## 四、Prompt Cache：模块化注意力复用

### 4.1 两道难题与解法（§3）

| 难题 | 原因 | 解法 |
|---|---|---|
| 位置依赖 | 片段换位后 KV 不可直接复用 | schema 给每个模块固定起始位置 ID；经验上模型能在不连续的位置 ID 上工作 |
| 识别可缓存段 | 服务器要知道哪段已有 KV | 用 PML 标记语言把可复用段显式写成模块，请求从 schema 派生 |

PML 的构件包括：schema（模块集合与布局）、module（可缓存段）、param（模块内占位参数，实参不缓存）、union（互斥模块共用起始位置）。模块独立编码近似于把模块外的注意力 mask 掉；模块间依赖强时可把多个模块联合编码（scaffolding），用内存换一致性。

### 4.2 运行时

加载 schema 时预算各模块的 KV；服务时取出模块 KV，只算参数与新文本，拼接成整段 prompt 的 KV。只加速 TTFT，之后的 decode 与普通 KV Cache 相同。模块可放 CPU 内存或 GPU 显存。

### 4.3 结果（§5，Llama 7B，LongBench 等）

| 项 | 结果（论文口径） |
|---|---|
| TTFT，模块在 GPU 显存 | 约 5–10× |
| TTFT，模块在 CPU 内存（含拷贝） | 约 1.5–3× |
| CPU 推理 | 最高约 70×（Intel）/ 20×（AMD）；摘要总括 GPU 8×、CPU 60× 量级 |
| 精度（Table 1） | 与基线大体可比，个别任务差值超过 2.5 被标为 outlier |
| 显存开销（Table 2） | 随缓存 token 数线性增长，每 token 开销（单位 MB/token）Llama 7B 0.50、13B 0.78、70B 2.5 |
| 长度效应（§5.4） | RTX 4090、Llama 7B、3K 上下文：TTFT 900 ms → 90 ms |

## 五、与 RadixAttention 的对照（SGLang §3）

| 维度 | Prompt Cache | RadixAttention |
|---|---|---|
| 匹配对象 | 用户声明的模块，可非严格前缀 | 自动匹配 token 前缀 |
| 写入时机 | schema 加载时 | 请求结束后保留 prompt 与生成的 KV |
| 驱逐 | 论文留作未来工作 | LRU，叶子优先 |
| 精度主张 | Table 1 称与基线可比 | SGLang 相关工作称 Prompt Cache 的模块复用可能使精度最多下降约 43%；两说并列，不作仲裁 |
| 命中率 | — | 多个基准约 50%–99% |

分工：要模块拼装、文档池、参数化模板，看 Prompt Cache；要多轮、few-shot、分叉自动吃前缀，看 RadixAttention。

## 六、商业 API：写入 / 读取 / 存活时间

### 6.1 字段结构（三家官方页，2026-09-22 核对）

| 轴 | Anthropic | OpenAI | Google |
|---|---|---|---|
| 启用 | cache_control 断点，显式最多 4 个，也可自动 | 默认隐式；GPT-5.6+ 可选显式断点 | 隐式（自动，无节省保证）/ 显式（创建缓存资源） |
| 写入计量 | cache_creation_input_tokens | cache_write_tokens | 显式缓存创建时按输入计费，另按 TTL 收存储费 |
| 读取计量 | cache_read_input_tokens | cached_tokens | 后续请求中的缓存命中 token |
| 存活时间 | 默认 5 分钟，命中刷新；可选 1 小时 | GPT-5.6+ 为 30 分钟；更早模型另有保留选项 | 显式缓存可设 TTL，默认约 1 小时 |
| 最短可缓存 | 按模型不同 | GPT-5.6+ 为 1024 token | 按模型不同 |

### 6.2 当日所见的结构倍率（非价目表）

| 厂商 | 写入 | 读取 |
|---|---|---|
| Anthropic | 5 分钟写入约 1.25× 基础输入价，1 小时写入约 2× | 约 0.1× |
| OpenAI（GPT-5.6+） | 约 1.25× | 约 0.1× |
| Google 显式缓存 | 按标准输入价 + 与 TTL 成正比的存储费 | 折扣输入价 |

### 6.3 成本结构

单位成本 ≈ 写入 × 冷启动次数 + 读取 × 命中次数 + 存储 × TTL + 未缓存输入 + 输出。

- 写入溢价要靠足够多次读取摊掉；
- TTL 太长浪费存储与溢价，太短则反复写入；
- Anthropic 页说明 TTL 从请求开始计时，长时间流式输出会吃掉存活窗口。

## 七、学术轴与 API 轴的接口

| 问题 | 学术 Prompt Cache | 云 API 缓存 |
|---|---|---|
| 谁定边界 | 开发者写 schema | 断点、自动前缀或显式缓存资源 |
| 能否非前缀拼装 | 能 | 主流是前缀匹配 |
| 成本可见性 | 自托管的算力与显存 | 账单上的写入 / 读取 / TTL 字段 |

应用层的「前缀稳定、只追加」原则见 [[上下文工程与智能体技能]]：本篇只锁计费字段结构，那篇把它当作智能体上下文设计的成本约束。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[推理引擎生态]] | 那篇把跨请求前缀复用列为引擎选型轴，本篇把它和模块化缓存、API 计费放在一起比较 | 引擎选型表 |
| [[HiCache层次化KV缓存]] | 那篇把引擎内前缀缓存扩到主机内存与存储，是本篇脉络里自建侧的下一步 | 多级存储机制 |
| [[KV缓存量化与压缩]] | 那篇减少每条 KV 的字节数，本篇讨论 KV 能否跨请求复用，两者可叠 | 量化方法 |
| [[DuoAttention与KVzip]] | 那篇的 KVzip 主张「压缩一次、多问复用」，与本篇的预计算文档 KV 是同一类使用场景 | 头分工与驱逐算法 |
| [[上下文工程与智能体技能]] | 那篇把「前缀稳定、只追加」当作智能体上下文设计的成本约束，并推论压缩、清除工具结果会放弃此前的缓存；本篇给出这条约束背后的写入 / 读取 / 存活时间计费结构 | 上下文组织与压缩策略 |

## 九、局限与待核实

- **非前缀复用的精度**：Prompt Cache 称与基线可比，SGLang 转述其可能掉点约 43%，口径不同，未见独立复核。
- **位置 ID 不连续的适用性**：论文是经验观察，在更新的长上下文模型上是否同样成立未见核验。
- **计费字段易变**：6.1、6.2 只代表 2026-09-22 的官方页，TTL、倍率、最短长度可能已改，落地以活页为准。
- **隐式缓存无保证**：Google 隐式缓存明确不保证节省；各家隐式缓存的命中率不可控、不公开。
- **跨云对齐**：三家的 TTL 刷新语义不同，统一到一个成本模型时需逐项映射，本篇未做。

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Prompt Cache](https://arxiv.org/abs/2311.04934) §3、§5 | PML 设计与 TTFT 结果 |
| 2 | [SGLang](https://arxiv.org/abs/2312.07104) §3 | RadixAttention 的匹配与驱逐 |
| 3 | [Anthropic Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching) | 断点与 TTL 语义 |
| 4 | [OpenAI Prompt Caching](https://developers.openai.com/api/docs/guides/prompt-caching) | 写入计量与成本公式 |
| 5 | [Google Context Caching](https://ai.google.dev/gemini-api/docs/generate-content/caching) | 隐式与显式缓存 |
