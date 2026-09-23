---
title: "Prompt / Prefix Caching：模块化复用与计费经济学"
topic: Prompt前缀缓存
date: 2026-09-22
lines: [AI Infra, 成本模型]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2311.04934 # 885K
 - https://arxiv.org/abs/2312.07104 # 1.4M（仅前缀复用交叉）
arxiv: ["2311.04934", "2312.07104"]
related: ["推理引擎生态", "KV缓存量化与压缩", "DuoAttention与KVzip"]
official_docs_fetched: "2026-09-22 Asia/Shanghai (CST)"
---

# Prompt / Prefix Caching：模块化复用与计费经济学

> **定位**：**P1 Infra / 成本横切**——在 **B7** 已立引擎级前缀复用（RadixAttention 选型轴）之后，本卡补两条独立切片：①学术侧 **Prompt Cache**（模块化注意力复用 / PML schema）；②商业 API 侧 **prompt / context caching 计费字段结构**（write / read / TTL）。SGLang 仅作「自动前缀树复用」交叉句，**禁止**重写 B7 引擎选型表。
> **攻坚线**：**AI Infra / 成本模型（主）**——模块边界、前缀命中、write/read/TTL 如何决定单位成本；**评测字段（辅）**——文内 TTFT 倍率、命中率、MB/token。
> **硬划界（开篇写清）**：
> - **≠ B7**：不写 vLLM / SGLang / TensorRT-LLM 选型对照表；RadixAttention 只取「自动前缀 KV 复用 + 命中率接口」一句。
> - **≠ [[KV缓存量化与压缩]]**：不写 K/V 非对称量化、残差窗、outlier 比特轴。
> - **≠ [[DuoAttention与KVzip]]**：不写 DuoAttention 头分工、KVzip query-agnostic 驱逐。
> **禁止编造**：学术数字一律锚定官方 PDF（2026-09-22 CST）；官方定价页**只核对 write / read / TTL 字段结构**，标注抓取时间 **Asia/Shanghai 2026-09-22**；**绝对 $/MTok 表易过时 → 本卡不抄作事实**，倍率若出现仅作「当日结构倍率」说明。
> **入库体积**：Prompt Cache **885K**；SGLang **1.4M**（均 **<20MB**）→ 二进制可入库。

---

## 一、材料元信息与 PDF 体积

| 角色 | 标题（PDF） | arXiv | 本地路径 | 体积 | 页数 | 抽取 |
|---|---|---|---|---|---|---|
| **主** | *Prompt Cache: Modular Attention Reuse for Low-Latency Inference* | **2311.04934v2** \[cs.CL\]（**25 Apr 2024**）；MLSys 2024 | `https://arxiv.org/abs/2311.04934` | **885K**（905,557 B） | 14 | （91K） |
| **交叉** | *SGLang: Efficient Execution of Structured Language Model Programs* | **2312.07104v2** \[cs.AI\]（**6 Jun 2024**） | `https://arxiv.org/abs/2312.07104` | **1.4M**（1,383,463 B） | 20 | （100K） |

| 材料 | 作者 / 机构（摘要页） | 代码（文内明示） |
|---|---|---|
| Prompt Cache | Gim, Chen, Lee, Sarda, Khandelwal, Zhong（Yale / Google） | https://github.com/yale-sys/prompt-cache |
| SGLang（交叉） | Zheng, Yin, Xie 等（Stanford / Berkeley / SJTU 等） | https://github.com/sgl-project/sglang |

**官方文档（计费字段核对，非论文；抓取：Asia/Shanghai 2026-09-22）：**

| 厂商 | 产品页 | 本卡用途 |
|---|---|---|
| Anthropic | https://platform.claude.com/docs/en/build-with-claude/prompt-caching | `cache_control` / write·read usage 字段 / TTL |
| OpenAI | https://developers.openai.com/api/docs/guides/prompt-caching | `prompt_cache_*` / `cached_tokens`·`cache_write_tokens` / TTL |
| Google | https://ai.google.dev/gemini-api/docs/generate-content/caching | implicit vs explicit / `ttl`·`expire_time` / storage 结构 |

**一句话抓手：** Prompt Cache =「**把可复用片段显式成模块，预计算 KV 再拼接**」；商业 API 缓存 =「**按前缀 write / read / TTL 重新计价**」——二者都砍 **prefill / TTFT 成本**，但一个靠 schema 模块，一个靠云端前缀命中。

---

## 二、议题边界：只写「模块复用 + 计费结构」

### 2.1 相对相邻笔记只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **B7** | 「跨请求共享前缀 KV」是 serving 缺口；SGLang RadixAttention = 自动前缀树 | vLLM / SGLang / TRT 选型表、PD 分离、投机通史、6.4× 引擎对照全文 |
| **[[KV缓存量化与压缩]]** | KV 张量可被缓存 / 复用 | KIVI / KVQuant 非对称量化与误差轴 |
| **[[DuoAttention与KVzip]]** | 长上下文下 KV 足迹仍贵 | DuoAttention 头门控、KVzip 重构打分驱逐 |

### 2.2 本卡两条轴

| 轴 | 问题 | 回答形态 |
|---|---|---|
| **学术模块化** | 跨 prompt 的非前缀对齐片段如何复用 KV？ | PML schema + prompt modules + 不连续 position ID |
| **商业计费** | 云 API 如何把「写缓存 / 读缓存 / 存活时间」拆成可计量字段？ | write / read / TTL（及 Google 的 storage）**结构**核对 |

跟读口诀：

`
Prompt Cache = 显式模块 + 预填 KV + 拼接（可非严格前缀）
RadixAttention = 自动前缀树 + LRU（严格前缀匹配）← 仅交叉，详 B7
云 API 缓存 = write 贵一点 / read 便宜 / TTL 决定保活成本
`

---

## 三、Prompt Cache：模块化注意力复用（主文）

### 3.1 动机：从单请求 KV Cache → 跨请求模块复用

文内对照（§2.2 / Fig 1）：

| 形态 | 复用范围 | 实质 |
|---|---|---|
| 朴素自回归 | 无 | 每步对全序列重算注意力 |
| **KV Cache**（Pope et al.） | **同一请求** decode 步 | prefill 一次，后续只算新 token |
| **Prompt Cache** | **多请求** 共享片段 | 预计算「常出现」片段的 KV，命中则跳过该段 prefill |

动机观察（§1）：系统消息、模板、文档池、工具学习模板 → 高重叠。空间/复用复杂度相对片段长度近似线性，而注意力计算对序列长度近似二次——故缓存片段越长，TTFT 收益越大。

### 3.2 两道难题与两记解法

| 难题 | 原因 | Prompt Cache 解法 |
|---|---|---|
| **位置依赖** | 位置编码进入 (k,v)；片段换位则 KV 不可直接复用 | 用 **schema** 给每个 module 固定起始 position ID；经验上 LLM 可在 **不连续 position ID** 上工作（相对序保留即可） |
| **识别可缓存段** | 服务器需知道哪段已有 KV | **PML** 把可复用段显式为 `<module>`，prompt 从 schema **派生** |

近似口径（§3.1）：模块独立编码 ≈ 模块外注意力被 mask（局部注意力类比）。文称：模块宜**语义自洽**；依赖强则可加 **scaffolding**（多模块联合编码，换内存换一致性）。

### 3.3 PML：schema / module / param / union

| 构件 | 作用（§3.2） |
|---|---|
| `<schema name=...>` | 定义模块集合与相对布局 |
| `<module>` | 可缓存文本段；未标模块的文本作「匿名模块」恒包含 |
| `<prompt schema=...>` | 派生请求：列出要 import 的模块 + 追加未缓存指令 |
| `<param name len>` | 模块内占位；实参**不**缓存，用 `<unk>` 占位再替换 |
| `<union>` | 互斥模块共享同一起始 position ID（省 ID、可 prefetch） |
| 嵌套 module | 层级组合 |
| `<system>/<user>/<assistant>` | 适配各模型对话模板 |

运行时（Fig 2 / §3.3–3.4）：① schema 加载时 **encoding** 各模块 KV；② 服务时取模块 KV → 算 param / 新文本 → **concat** 成整段 prompt 的 KV（替代整段 prefill）。**只加速 TTFT**；后续 token 的 decode 成本与普通 KV Cache 同阶。

实现要点（§4）：HuggingFace transformers 原型 ≈ 3K Python；模块可放 **CPU DRAM** 或 **GPU HBM**（GPU 从 CPU 取则有 H2D memcpy）；RoPE / ALiBi 需支持不连续 position ID（文称每模型约 +20 行量级适配）。

### 3.4 评测字段（文内，禁外推）

**延迟（§5.2，Llama 7B，LongBench）：**

| 设定 | TTFT 相对 baseline（文内口径） |
|---|---|
| GPU + 模块在 **GPU 内存** | 约 **5×–10×** |
| GPU + 模块在 **CPU 内存**（含拷贝） | 约 **1.5×–3×** |
| CPU 推理（Intel / AMD） | 最高约 **70×** / **20×** |
| Abstract 总括 | GPU **8×** 量级；CPU **60×** 量级 |

文内解释：CPU 上注意力更贵 → 缓存收益更大；实际落点在「GPU 存 vs CPU 存」上下界之间。

**精度（Table 1）：** Llama2 / MPT / Falcon 上 LongBench 多任务，Cached vs Baseline **大体可比**；文将差值 >2.5 的格子标为 outlier（个别任务有升有降）。确定性采样以便对照。

**内存（Table 2，MB/token）：** 例 Llama 7B **0.50**、Llama 13B **0.78**、Llama 70B **2.5**（按模型 hidden 维增长）。开销 ∝ 缓存 token 总数。

**二次优势（§5.4 / Fig 5）：** KV Cache prefill 延迟随长度近似二次增长，Prompt Cache 的 memcpy 近似线性 → 差距随长度/模型维二次拉开。例：RTX 4090、Llama 7B、3K ctx，TTFT 900 ms → 90 ms；TTST 仍约 32 ms/token。

**应用示意（§5.6）：** 多文件代码生成（每源文件一模块）、个性化（union 选特质）、参数化旅行计划——展示 schema 表达力；定性并置生成文本称质量可接受。

---

## 四、SGLang 交叉：自动前缀复用（≠ B7 选型表）

> 本节约束：**只写 RadixAttention 与 Prompt Cache 的对照接口**；引擎对照、FSM、投机、硬件覆盖 → **B7**。

| 维度 | Prompt Cache（本卡主文） | RadixAttention（SGLang §3；交叉） |
|---|---|---|
| **匹配对象** | 用户声明的 **modules**（可非严格前缀对齐，靠 schema 位置） | **token 前缀**自动匹配（radix tree） |
| **写入时机** | schema 加载 / 首次 encoding | 请求结束后仍保留 prompt+生成 KV 入树 |
| **驱逐** | 文留「未来替换策略」 | **LRU 叶优先** + 运行中 refcount |
| **调度** | 同 schema 批次可共享指针（可叠 PagedAttention） | **最长共享前缀优先**（近似 DFS） |
| **准确率主张** | Table 1 称与 baseline 可比 | Related Work 称 PromptCache 模块复用「可影响准确率最高约 43% 降」（SGLang §7 转述——本卡并列，不代仲裁） |
| **无命中开销** | — | ShareGPT 100 请求 74.3 s 中树管理约 0.2 s（**<0.3%**） |

文内命中率示例（SGLang 评测段）：多基准 cache hit rate 约 **50%–99%**；生产多模态观察例 LLaVA-Next-34B **52.4%**、另一模型 **74.1%**（文内自述窗口）。更高命中 → 更大 batch / 更高吞吐 / 更低延迟（Fig 8）。

**跟读分界：** 要「模块拼装、文档池、参数化模板」→ Prompt Cache；要「多轮 / few-shot / fork 树自动吃前缀」→ RadixAttention（细节回 **B7**）。

---

## 五、商业 API 缓存：只锁 write / read / TTL 字段结构

> **抓取时间：Asia/Shanghai 2026-09-22（CST）。**
> **规矩：** 下列为各官方「prompt / context caching」产品页**字段与计费轴结构**；**不把绝对 $/MTok 表当永久事实**；若页上出现倍率，仅标「当日结构倍率」，落地请回活页。

### 5.1 三家字段骨架（同日核对）

| 轴 | **Anthropic** Prompt Caching | **OpenAI** Prompt Caching | **Google** Context Caching |
|---|---|---|---|
| **启用方式** | 顶层或块级 `cache_control: {type: "ephemeral", ttl?}`；自动 / 显式断点 | 默认隐式；GPT-5.6+ 可用 `prompt_cache_options.mode` = `implicit` \| `explicit` + `prompt_cache_breakpoint` | **Implicit**（自动，无节省保证）/ **Explicit**（`caches.create`，可保证折扣口径） |
| **Write 计量** | `usage.cache_creation_input_tokens`；（可选细分）`cache_creation.ephemeral_5m_input_tokens` / `ephemeral_1h_input_tokens` | `usage.input_tokens_details.cache_write_tokens` | Explicit：**创建时**对缓存内容计输入侧费用 + **按 TTL 的 storage**（页述「token 数 × 存活时长」） |
| **Read 计量** | `usage.cache_read_input_tokens` | `usage.input_tokens_details.cached_tokens` | 后续请求 `usage_metadata` 中的缓存命中 token（页称 cached 前缀） |
| **未缓存输入** | `usage.input_tokens` = **断点之后**的 token（≠ 总输入） | 普通 input = 总 input − cached − cache_write（文档成本公式口径） | 非缓存输入 + 输出照常 |
| **TTL / 存活** | 默认 **5 分钟**（命中刷新）；可选 **`ttl: "1h"`** | GPT-5.6+：`prompt_cache_options.ttl` 仅 **`"30m"`**（默认=唯一支持值；可保留更久为厂商侧）；更早模型用 `prompt_cache_retention`: `in_memory` \| `24h` | Explicit：`ttl`（Duration，如 `"300s"`）或 `expire_time`；**默认约 1 小时**；可 patch 更新 |
| **断点上限** | 显式最多 **4**；自动占 1 槽 | 每请求最多约 **4** 次 cache write（显式） | Explicit 以 **cache 资源名**引用，非「前缀断点」同一模型 |
| **最短可缓存** | **按模型/平台变**（页列 512–4096 等；过短则两字段为 0、不报错） | GPT-5.6+：**1024** visible tokens（hidden system 不计） | 按模型表（页列如 2.5 系 2048、3.x Flash/Pro 4096 等） |
| **预热** | `max_tokens: 0` 写缓存不产出 | `prompt_cache_options.prewarm: true` | 无对等「零输出预热」主推；靠提前 `caches.create` |
| **隔离** | workspace / org 级隔离（页述） | org + 处理区域内；`prompt_cache_key` 可分账/辅助路由 | Explicit cache 为独立资源（可 list/get/delete 元数据） |

### 5.2 结构倍率（仅作「当日页所见」，非费率事实表）

> 下列倍率来自 **2026-09-22** 官方页叙述；**绝对美元价请以当日 Pricing 页为准，本卡不收录模型价目表。**

| 厂商 | Write 结构 | Read 结构 | 备注 |
|---|---|---|---|
| Anthropic | 5m write ≈ **1.25×** base input；1h write ≈ **2×** | read/refresh ≈ **0.1×**（个别型号页脚例外） | 命中刷新默认不另收「续命费」口径见页 |
| OpenAI（GPT-5.6+） | cache write ≈ **1.25×** uncached input | cached input ≈ **0.1×** | 更早代：页称「无额外 write 费」、read 折扣按型号；TTL 控件名不同 |
| Google Explicit | 创建按**标准输入**计 + **storage ∝ TTL** | 缓存 token 按**折扣输入价** | Implicit：**无成本节省保证**；Explicit 才有保证口径 |

**经济学跟读（结构，非报价）：**

`
单位成本 ≈ write×(冷启动次数) + read×(命中次数) + storage×TTL + 尾部未缓存输入 + 输出
保本直觉： write 溢价需被足够多次 read 摊掉；TTL 选太长 → storage/溢价浪费；太短 → 反复 write
`

Anthropic 页：TTL 从「写或读该条目的请求**开始**」计时，流式长响应会吃掉存活窗口。OpenAI 页：复用刷新寿命且不再收 write。Google 页：Explicit storage 按声明 TTL 计，与「是否提前 delete」的计费细则以活页为准。

### 5.3 与学术轴的接口（勿混）

| 问题 | 学术 Prompt Cache | 云 API Prompt/Context Cache |
|---|---|---|
| 谁决定缓存边界？ | 开发者写 **PML schema** | 断点 / 自动前缀 / `caches.create` 内容 |
| 能否非前缀模块拼装？ | **能**（concat 模块 KV） | 主流是 **前缀匹配**（Google explicit 是「命名前缀资源」） |
| 计费可见性 | 自托管算力/显存 | **write / read / TTL(/storage)** 账单字段 |
| 与 B7 关系 | 可启发 serving 模块管理 | 与引擎 Radix 命中率正交：一个在云账单，一个在自建吞吐 |

---

## 六、可迁移问题（给后续波次）

1. **模块 mask vs 全注意力**：scaffolding 的内存–一致性曲线如何标定？与 [[DuoAttention与KVzip]] 头级保留是否可叠？
2. **Schema 自动归纳**：能否从流量里挖掘高频片段生成 PML，而不靠手写？
3. **计费字段对齐**：跨云把 `cache_creation_*` / `cache_write_tokens` / storage 映射到同一 FinOps 模型时，TTL 刷新语义差如何归一？
4. **命中率 SLA**：Radix LRU vs 云侧「可能更长保留」——生产 agent 长系统提示下，write 溢价与 TTFT SLA 如何联合优化（只问字段，不编费率）？

---

## 七、來源与抽取索引

| 路径 | 体积 | 页数 | 用途 |
|---|---|---|---|
| `https://arxiv.org/abs/2311.04934` | **885K**（905,557 B） | 14 | Prompt Cache 全文 |
| `https://arxiv.org/abs/2312.07104` | **1.4M**（1,383,463 B） | 20 | 仅 RadixAttention / 前缀复用交叉 |
| | 91K | — | |
| | 100K | — | 同上 |
| Anthropic / OpenAI / Google 官方 caching 文档 | HTML | — | write/read/TTL **字段结构**；抓取 **2026-09-22 CST** |

**体积政策：** 两篇 PDF 均 **<20MB**，二进制保留；无权重 / 数据集 / 视频。官方费率**不**以过时数字入库。

**状态：** `archived` · date **2026-09-22** · 跟读语言：中文。
