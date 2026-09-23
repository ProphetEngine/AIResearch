---
title: "Continuous batching / iteration-level scheduling 理论边界（8 · Orca 专线）"
topic: 连续批处理与Orca
date: 2026-09-22
lines: [AI Infra]
status: archived
sources:
 - https://www.usenix.org/conference/osdi22/presentation/yu
 - https://arxiv.org/abs/2309.06180
usenix: OSDI 2022 (Yu et al., Orca)
arxiv_cross: ["2309.06180"]
archived: 2026-09-22
---

# Continuous batching / iteration-level scheduling 理论边界（Orca 专线）

> **定位**：P1 Infra 子题——钉死 **请求级 vs iteration-level** 的吞吐/延迟边界，以及与 **Prefill–Decode 分离 / 投机解码** 的正交关系。
> **攻坚线**：**AI Infra（主）**。
> **相对已入库**：[[推理引擎生态]] / [[AI基础设施总览]] 以 vLLM·SGLang·TRT-LLM **选型地图**与 PagedAttention 为主；Orca 在彼处仅为次级交叉。本篇 **只做理论边界 / Orca 专线**，**禁止**重写引擎选型表、PagedAttention 分页算法正文、投机解码通史。
> **交叉基线**：vLLM（Kwon et al., arXiv:2309.06180）**仅作对照**——其 Discussion 明确 iteration-level scheduling 与 PagedAttention **互补**，不替代。
> **禁止编造**：术语、数字、实验设定一律取自官方 PDF（2026-09-22 CST）；业界口语「continuous batching」在 Orca 正文中对应 **iteration-level scheduling**（文中未以 continuous batching 作正式章节名）。

---

## 一、材料元信息

| 项 | 内容 |
|---|---|
| **主文献** | Yu, Jeong, Kim, Kim, Chun. *Orca: A Distributed Serving System for Transformer-Based Generative Models*. **OSDI 2022**（Carlsbad, CA；Proceedings of the 16th USENIX Symposium on OSDI） |
| **入口** | https://www.usenix.org/conference/osdi22/presentation/yu ；PDF https://www.usenix.org/system/files/osdi22-yu.pdf |
| **对照基线** | Kwon et al., *Efficient Memory Management for Large Language Model Serving with PagedAttention*（vLLM）→ `https://arxiv.org/abs/2309.06180`；笔记交叉 [[AI基础设施总览]] §4、`B7` §1.3 |
| **本篇不覆盖** | SGLang Radix / TRT-LLM 选型轴（→ B7）；KV 量化通史（→ [[KV缓存量化与压缩]]）；投机算法族正文（→ B7 §三） |

**一句话抓手：** 自回归生成使单请求必须跑 **多次 iteration**（每步产出一 token）；若调度仍锁在 **请求级 batch**，早结束的请求无法立刻返回、晚到的请求必须等整批结束——Orca 把调度粒度改到 **单次 iteration**，并用 **selective batching** 让「已处理 token 数不同」的请求仍能共享非 Attention 算子的批执行。

---

## 二、请求级 vs iteration-level（理论边界）

### 2.1 生成负载的「多 iteration」特性（Orca §1–§2）

据 Orca 摘要与 §2：

- 相对 ResNet / BERT 类「跑一遍模型即结束」，GPT 类生成要对同一请求 **反复跑模型**：每一次 **iteration** = 跑完所有层并产出 **一个** 输出 token，再喂回下一步。
- 文中区分两阶段（fairseq-style incremental decoding 叙述）：
 - **initiation（prompt / 首次）**：可并行处理该请求的全部输入 token；
 - **increment（decode）**：每步通常只吃 **1** 个 token，并依赖已缓存的 Attention K/V。
- 因此服务侧真正「一次调度决策」若覆盖「请求从进入到全部 token 生成完毕」，就会与 **异构输出长度 / 异构到达时间** 强冲突。

### 2.2 请求级调度（canonical request-level）的两条惩罚

Orca 对照 Triton + FasterTransformer 一类接口（§1、§3、Figure 2）：

| 现象 | 机制 | 后果 |
|---|---|---|
| **早结束惩罚** | 引擎在 **整批所有请求都跑完** 后才把结果一次性交回 serving 层 | 已生成完的请求 **不能立刻** 返回客户端 → 延迟抬升 |
| **晚加入惩罚** | 新请求只能等 **当前已派发 batch 完全结束** 才能被纳入下一轮 | 排队时间可被「最长请求」绑架 |

边界表述（思想层）：请求级批处理把「批」当成 **原子执行单元**；批内完成时间方差越大，吞吐–延迟帕累托越差。Orca 端到端实验用合成 trace（输入长度 $U(32,512)$、`max_gen_tokens` $U(1,128)$）显式制造这种方差（§6.2）。

### 2.3 Iteration-level scheduling（Orca S1）

定义（摘要 / §3 S1）：调度器以 **iteration** 而非 **request** 为粒度调用执行引擎——每次只跑模型 **一个** iteration；每 iteration 返回后：

1. 可检测哪些请求已结束并 **立刻** 回包；
2. 新到达请求最多等 **当前这一个 iteration**，即可被纳入候选集合；
3. 调度器对「下一步处理哪些请求、处理多少」有完整控制权。

系统环（Figure 4）：Endpoint → Request Pool → Scheduler → Execution Engine；虚线交互表示 **每个 iteration** 都发生选批 / 下发 / 回写 token。

**与业界口语「continuous batching」的对齐：** vLLM 论文 §2.2 把 cellular batching 与 **iteration-level scheduling** 并列为 fine-grained batching：每步结束后移除完成请求、加入新请求，新请求最多等一个 iteration，并可借助专用 kernel **避免 pad 到等长**。本篇以 Orca 正式术语为准，continuous batching 仅作同指别名。

### 2.4 吞吐–延迟旋钮：`max_bs` 与「边际递减」

Orca §4.2：增大 batch size 用更高吞吐换更高延迟，且 **回报递减**；系统提供 **`max_bs`（max batch size）** 由运维在延迟预算下调。§6.2 观察：在其合成异构负载下，增大 Orca 的 `max_bs` 往往抬吞吐而 **中位归一化延迟变化相对温和**——因为 iteration-level 已消解早结束 / 晚加入；但文中明确 **不保证** 任意硬件/模型/负载下增大 batch 都不伤延迟。

---

## 三、Orca 思想：selective batching + 内存预留 + 分布式管线

### 3.1 为何「只改调度粒度」不够（挑战 C2）

Iteration-level 会自然拼出 **任意集合** 的请求：各自已处理 token 数不同、或分别处于 initiation / increment。此时经典「把请求在 batch 维拼成 `[B, L, H]`」会失败，因为 Attention 的 K/V **形状依赖已处理长度**（§3 C2；三种不可直接 batch 的配对：不同长度的 initiation、不同 index 的 increment、跨 phase）。

若因此退回逐请求串行，就丢掉 GPU 并行红利——这是调度思想与 **算子层可批性** 的接缝。

### 3.2 Selective batching（Orca S2）

思想（§3 S2、Figure 5）：

- **非 Attention**（Linear、LayerNorm、Add、GeLU 等）：不依赖「请求边界」区分元素 → 可把各请求 token **展平** 成 token-wise 大张量（如合计 7 个 token → `[7, H]`）做批执行。
- **Attention**：必须按请求隔离（同请求内 token 互相关）→ **Split** 后逐请求算，再 **Merge** 回 token 维。
- **效率辩护（原文）**：Attention **不带模型参数**；不对其做跨请求 batch，不会损失「多请求摊销读权重」的收益；主要瓶颈在大模型 **反复读参数**（§7 设计原则：每次参数读尽量覆盖所有 ready tokens）。

配套：**Attention K/V manager** 按请求保存历史 K/V，直至调度器显式删除（请求结束）。

### 3.3 调度算法要点（Algorithm 1）——理论边界落在「槽位预留」

`Select`（§4.2）：

1. 排除已 `RUNNING` 的请求；按 **到达时间** 排序 → **iteration-level FCFS**（先到的请求完成的 iteration 数 ≥ 后到者；输出长度更短的后到者仍可更早回包）。
2. 装入至多 `max_bs` 条。
3. 对首次进入（`INITIATION`）的请求，用其 **`max_tokens`** 预留 K/V **slots**（`n_rsrv`）；若 `n_rsrv + max_tokens > n_slots` 则停止装入——避免「无槽可写下一 token」的死锁。
4. `n_slots`：运维给定、分给 K/V manager 的槽位数；文称在模型与并行度固定时，显存占用主要随 `n_slots` 变，通常取内存约束下最大可行值。

**理论边界（相对后续分页服务）：** Orca 的活跃并发度受 **「按请求 max_tokens 预留连续/整块槽」** 约束；输出长度未知时，预留策略直接决定能塞进显存的并发请求数。vLLM 对照实验正是沿着这条边界打开三种 Orca 复现变体（Oracle / Pow2 / Max）——见下一节，**不在本篇展开分页算法**。

### 3.4 分布式与管线：与请求级 microbatch 的对照（思想层）

- Intra- / inter-layer 并行组合已知训练侧技巧；控制面与数据面分离，避免每 iteration 用 NCCL 传 CPU 侧元数据（§4.1）。
- 调度保持在途 batch 数 ≈ `n_workers`，从而跨 worker **管线化多个 iteration-batch**（Figure 8a）。
- 对照 FasterTransformer：请求级下常用 **microbatch** 填管线，被迫在「更大 microbatch（更像批）」与「更多 microbatch（更少 bubble）」之间权衡；Orca 称 iteration-level **免除该权衡**，无需为管线再切 microbatch（§4.2、Figure 8）。

### 3.5 论文自报量级（禁外推为 SLA）

| 设定（均据 §6） | 结果（论文数字） |
|---|---|
| 微基准：同构请求、关调度、比引擎 | 13B/101B 上 Orca 引擎与 FasterTransformer **相近或略差**（因 Attention 未跨请求 batch）；175B 关管线时 Orca 引擎最多约 **+47%**（归因控制/数据面分离） |
| 端到端：175B，中位归一化延迟约 190 ms/token 对齐点 | FasterTransformer **0.185 req/s** vs Orca **6.81 req/s** → **36.9×** 吞吐（摘要与 §6.2；合成 Poisson 到达 + 长度方差） |
| 硬件 | Azure ND96asr A100 v4，每 VM 8×40 GB A100；最大用到四机；fp16；模型配置见表 1（13B–341B） |

**边界提醒：** 36.9× 锚定在 **相对 FasterTransformer + 请求级调度、特定合成 trace、特定延迟锚点**；低负载 / 同构长度时差距收窄（§6.2、Figure 11）。

---

## 四、与 Prefill–Decode 分离 / 投机解码的正交关系

> 本节只立 **轴正交**，细节回 `B7` / [[AI基础设施总览]]；不重画引擎地图。

| 轴 | 管什么 | 不替代什么 |
|---|---|---|
| **Iteration-level / continuous batching** | **时间维**：一步（iteration）内如何把活跃序列拼进同一批执行；完成/到达如何即时进出 | 不决定 prefill 与 decode 是否同池；不减少目标模型必须串行的「逻辑步」上限 |
| **Prefill–Decode（PD）分离** | **拓扑 / 池维**：算力型 prefill 与访存型 decode 是否分池扩缩（DeepSeek-V3 §3.4 叙事见 [[AI基础设施总览]]；B7 §1.3） | 分池之后，各池内部仍通常需要某种连续批 / 步进调度 |
| **投机解码** | **串行步维**：用草稿 + 校验减少目标模型前向次数（B7 §三） | 接受/拒绝仍发生在步进循环里；与「批里有哪些序列」是不同旋钮 |

**正交命题（可检验）：**

1. **PD × continuous batching：** B7 误区条已写——二者叠加而非替换。Orca 文中的 initiation/increment 是 **同一引擎时间线上的 phase**，不等于当代「prefill 池 / decode 池」产品形态；把 Orca 直接等同于 PD disaggregation 是范畴错误。
2. **投机 × continuous batching：** 投机改变的是「每步产出几个候选 / 校验几个 token」；continuous batching 改变的是「这些步进如何与其他请求交错」。可同开同关；加速比不可乘成单一 SLA（接受率、批组成、KV 布局均独立）。
3. **PagedAttention × iteration-level：** vLLM Discussion（§8）原话要点——二者 **complementary**：Orca 靠调度交错提高并行度；vLLM 靠降低碎片 / 提高显存利用率让 **更多请求的工作集同时塞进 GPU**；细粒度交错反而使内存管理更关键，故分页更「刚需」。vLLM 摘要区间相对 FasterTransformer / Orca 等约 **2–4×**（已录 [[AI基础设施总览]]；**本篇不重做分页评测表**）。

---

## 五、常见误区

1. **「Continuous batching = PagedAttention / = vLLM」**
 Orca（2022）立的是 **调度粒度 + selective batching**；vLLM（2023）立的是 **KV 分页布局**。vLLM 自身把前者当已有 fine-grained batching 背景，并实现自研 Orca 对照基线（因原系统未公开）。混名会导致把内存碎片问题误判成「再调大一点 batch」可解。

2. **「Orca 36.9× 是任意部署保证」**
 数字来自 175B、合成 Poisson trace、与 FasterTransformer 在 **相近归一化延迟锚点** 上的吞吐比（§6.2）。同构长度、低到达率、或引擎实现已极强时，倍率不可外推。

3. **「不 batch Attention 一定很亏」**
 Orca 的辩护是 Attention **无权重摊销**；微基准上与 FasterTransformer 接近。但这不蕴含「Attention kernel 无需优化」——只说明 **跨请求 batch Attention** 不是其主杠杆；后世 FlashAttention 等走的是另一条 IO 轴（→ [[AI基础设施总览]]，本篇不展开）。

4. **「请求级 + 更大静态 batch 就能等价 continuous batching」**
 静态大 batch 在 **长度方差大** 时放大早结束 / pad / 排队；Orca Figure 10 vs 11：异构时 FasterTransformer 增大 `max_bs` 甚至不一定抬吞吐，同构时才更明显——说明病根是 **调度原子性**，不是单纯「batch 数字不够大」。

5. **「PD 分离或投机解码可以替代 continuous batching」**
 见 §四：池拓扑与串行步压缩都不自动提供「每 iteration 进出请求」的接口语义。

6. **「Iteration-level FCFS 禁止短请求插队完成」**
 Orca 定义的是 **已跑 iteration 数** 上的 FCFS，不是「后到者不得先返回」；输出更短的后到请求仍可更早结束回包（§4.2）。

7. **「`max_tokens` 预留已解决 KV 显存」**
 预留避免死锁，但把 **未知输出长度** 转成 **保守占坑**；vLLM 用 Oracle/Pow2/Max 三种复现暴露该边界。真正的块级共享 / 近零碎片是下一篇（已入库）问题，不是 Orca 调度定理的推论。

8. **编造「Orca 论文写了 continuous batching 专章 / PD disaggregation API」**
 正文关键词是 **iteration-level scheduling** 与 **selective batching**；PD 产品语汇与 continuous batching 营销语汇属后续生态，交叉时必须降级为对照而非伪引 Orca。

---

## 六、引用与本地路径

| 文献 / 入口 | 标识 | 本地 / URL |
|---|---|---|
| Yu et al., *Orca* | OSDI 2022 | `https://www.usenix.org/conference/osdi22/presentation/yu`；https://www.usenix.org/system/files/osdi22-yu.pdf ；会议页 https://www.usenix.org/conference/osdi22/presentation/yu |
| Kwon et al., *PagedAttention / vLLM*（对照基线） | arXiv:2309.06180 | `https://arxiv.org/abs/2309.06180`；交叉 [[AI基础设施总览]] §4、[[推理引擎生态]] §1.3 |

**次级交叉（点到为止，不入库为本篇主证据）：** BatchMaker（Orca §7，RNN cell 级批处理前史）；DeepSeek-V3 Prefill/Decode 部署表（[[AI基础设施总览]]）；B7 投机解码四篇一手 PDF。

---

## 七、待核实 / 刻意未写

- Orca 原系统公开可用性与生产分支演化（vLLM 评测写明需自研复现）。
- 当代引擎中 continuous batching 与 chunked prefill、prefix cache、PD disagg 的具体默认组合——属 B7 选型层，本篇不附表。
- EAGLE 等更新一代投机与步进调度的共设计：议程明确本波不派投机专线。

## 相关笔记

- [[Gemini37FlashModelCard|Gemini 3.7 Flash]]
- [[KV缓存量化与压缩|KV Cache 量化]]
- [[连续批处理与Orca|Continuous Batching / Orca]]
- [[机制可解释性入门|机制可解释性]]
- [[世界模型与VJEPA|World Models / V-JEPA]]
- [[SpeechLLM语音语言模型|Speech LLM]]
- [[视觉语言动作谱系|Robotics / VLA]]
- [[智能体长程记忆|Agent 长期记忆]]
- [[可扩展监督与弱到强|Scalable Oversight]]

