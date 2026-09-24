---
title: "Prefill–Decode 分离与统一服务（TaiChi：聚合 / 解聚再统一）"
topic: PrefillDecode分离与统一服务
date: 2026-09-24
lines: [AI Infra, 服务架构]
status: archived
sources:
  - https://arxiv.org/abs/2508.01989
  - https://arxiv.org/abs/2401.09670
arxiv: ["2508.01989", "2401.09670"]
related:
  - "连续批处理与Orca"
  - "MegaScaleInfer与UltraEP"
  - "推理引擎生态"
  - "AI基础设施总览"
retrieval_cutoff: 2026-09-24
timezone: Asia/Shanghai (CST)
archived: 2026-09-24
---

# Prefill–Decode 分离与统一服务（TaiChi）

> **定位**：LLM serving 中 **prefill 与 decode 是否同池、如何再统一** 的调度 / 拓扑轴。主文为 TaiChi（Wang, Zuo 等，arXiv:2508.01989）：在 **colocated 聚合** 与 **物理解聚** 之外，用 **能力分化实例 + latency shifting** 覆盖 TTFT / TPOT 任意组合下的 goodput。
> **边界**：本篇不是 [[连续批处理与Orca]]（iteration-level 批内进出）；也不是 [[MegaScaleInfer与UltraEP]] 的 Attention–Expert 节点解耦。PD 池化 / 再统一回答的是「两阶段算力画像是否分实例」；连续批回答的是「一步内如何拼请求」——二者正交、可叠加。

---

## 一、问题设定：两阶段资源画像与双 SLO

自回归 LLM 推理拆成两阶段（TaiChi §2.1；亦见 DistServe 摘要）：

| 阶段 | 计算画像 | 用户侧 SLO |
|---|---|---|
| **Prefill** | 对整段 prompt 并行算，偏 **compute-bound** | **TTFT**（首 token 时延，响应性） |
| **Decode** | 逐步生成，依赖 KV cache，偏 **memory-bound** | **TPOT**（除首 token 外的均 token 时延，流畅度） |

**Goodput** 定义为：在同时满足 TTFT 与 TPOT 约束下，单位资源可支撑的最大请求吞吐（TaiChi 摘要；DistServe 以每 GPU 最大合规速率表述同一思想）。应用 SLO 谱很宽：有的紧 TTFT、松 TPOT；有的紧 TPOT、松 TTFT；大量交互场景要求二者 **平衡**。

同机混跑时，新 prefill 可占满一整次 iteration，拖慢同批 decode（Orca / Sarathi-Serve 叙事）；拆池后可消干涉并独立扩缩，但 prefill 总算力池变小，易在 TTFT 上排队。

---

## 二、演化：colocated → disaggregation → 再统一

### 2.1 PD Aggregation（同实例聚合）

代表：Orca 的 iteration-level 批处理、Sarathi-Serve 的 **chunked prefill**（把 prefill 切块并 piggyback 进 decode 批）。目标是抬利用率、保 TTFT；代价是 decode 仍受 prefill 干涉，**TPOT** 易成为瓶颈。TaiChi 把干涉强度定义为「decode 期间并发算过的 prefill token 数 / 该请求输出长度」，并观察到 TPOT 与干涉强度近似线性（$R^2=0.99$，§2.3.1）。

### 2.2 PD Disaggregation（物理解聚）

代表：DistServe、Splitwise 等——prefill / decode 分到不同 GPU 实例，首 token 后经高速互联搬 KV。消掉同批干涉，利于 **紧 TPOT**；但只有子集实例贡献 prefill 容量，高负载下 **TTFT 排队** 抬升（TaiChi Observation 3 / Fig.7–8）。

史前对照（DistServe，Zhong 等，arXiv:2401.09670）：明确指出 colocated 批处理带来 **prefill–decode 干涉** 与 **资源 / 并行计划耦合**，主张分 GPU、按 TTFT/TPOT 分别做资源与并行优化，并给出带宽感知放置；评测称相对 SOTA 可达约 **7.4×** 更多请求或 **12.6×** 更紧 SLO（>90% 合规）。TaiChi 把 DistServe 放在「解聚一端」的对照轴上，不再重复其放置算法正文。

同谱系的 KV 中心化解聚还有 Mooncake（Qin 等，*A KVCache-centric Disaggregated Architecture for LLM Serving*）；本篇不展开第二主文。[[Kimik15技术报告深读]] 部署叙事中亦出现 Mooncake 传输路径，用途不同，仅作交叉指针。

### 2.3 两极都不够：平衡 SLO 下的困境

TaiChi 用 Vidur 仿真（Llama-2-70B，TP4，Arxiv summarization，QPS=12）对照三类 SLO（Table 2）：

| SLO 设定 | PD Aggregation 达标率 | PD Disaggregation 达标率 |
|---|---:|---:|
| 松 TTFT + 紧 TPOT（16s, 60ms） | 7% | **98%** |
| 紧 TTFT + 松 TPOT（5s, 250ms） | **97%** | 42% |
| **平衡**（6s, 100ms） | 16% | 50% |

结论（Observation 1）：聚合擅紧 TTFT；解聚擅紧 TPOT；**平衡双约束时两者 goodput 都不优**。机会在于：各自「富裕」的一侧（聚合侧大量请求 TTFT ≪ SLO；解聚侧大量请求 TPOT ≪ SLO）可把余量 **转移** 给濒临违约的请求（latency shifting，§2.4）。

### 2.4 再统一：同一架构覆盖三态

TaiChi 不在「永远聚合」与「永远解聚」间二选一，而是用 **可配置滑块** 在同一套实例上切到聚合形态、解聚形态或 **混合态**（§3.1）：

- 紧 TTFT → 调成近似全聚合（各实例同 chunk）；
- 紧 TPOT → 调成近似全解聚（D-heavy 侧禁止 / 极小 chunk prefill）；
- 平衡双 SLO → **hybrid-mode**，做跨阶段、跨请求的 latency shifting。

---

## 三、TaiChi 机制要点

### 3.1 能力分化实例与三滑块

实例不按「只能 prefill / 只能 decode」硬切，而按 **chunked prefill 的 chunk 大小** 分化（Fig.11）：

| 类型 | 配置含义 | 特长 | 代价 |
|---|---|---|---|
| **P-heavy** | 大 chunk（$S_P$） | 快 prefill → 利 TTFT | decode 高干涉 → TPOT 差 |
| **D-heavy** | 小 chunk（$S_D$） | 低干涉 decode → 利 TPOT | prefill 慢，但仍可接「可降级」短 prefill |

三滑块：$R_{PD}$（P/D 实例比）、$S_P$、$S_D$。工作负载显著变化时采用类 DistServe 的 **按需搜索重配**（分钟级，相对小时级流量漂移，§3.1）。

### 3.2 Hybrid-mode inference

相对纯聚合 / 纯解聚，混合态同时保留两维（Table 1）：

1. **Aggregated batch handling**：P-heavy 与 D-heavy **都可以**跑含 prefill+decode 的混合批 → 抬总 prefill 容量与利用率（相对纯解聚）。
2. **Disaggregated request handling**：同一请求的 prefill 与 decode **可以落在不同类型实例** → 细粒度把 TTFT / TPOT 往需要的一侧推。

例：关键请求 prefill 走 P-heavy、decode 走 D-heavy；可降级请求则相反，把专用资源让给濒危请求。

### 3.3 Flowing decode scheduling（管 TPOT）

解决「批处理使单请求 TPOT 难单独降级」与「输出长度先验未知」（Challenge 2）：

1. **低干涉起跑**：prefill 结束后 decode **先**上 D-heavy，避免未知短输出在高干涉 P-heavy 上直接违约。
2. **最长优先降级流动**：D-heavy HBM 超水位 $M$（文中例 95%）时，把 **当前已生成最长** 的 decode 迁到 P-heavy（已在低干涉侧「攒」了更多 TPOT 预算，更能吸收降级）；从原批抽出再迁入，避免降级扩散到同批其他请求。
3. **TPOT 感知回流**：P-heavy 上实时 TPOT 接近 $\alpha\cdot$SLO（文中例 $\alpha=0.96$）则回流 D-heavy；回流过频视为架构滑块失配信号。

### 3.4 Length-aware prefill scheduling（管 TTFT）

解决「短 prefill 可降级、长 prefill / 已久等队列不可再降」（Challenge 3）：估计各实例上的排队 + 执行 +（若需）KV 传输时间；若投影 TTFT 仍在 SLO 内，则把短请求派到较慢的 D-heavy，把 P-heavy 留给更紧迫的长 prefill（Algorithm 2 / Fig.13）。

### 3.5 实现钩子

实现于 vLLM：不同 chunk 的 chunked prefill；扩展 KV transfer，实例间经 **NCCL** 互传，并与关键路径异步解耦；接收侧用融合 CUDA 算子写入 paged KV（§3.5）。

---

## 四、证据（文内实验，非外推）

**设定（§4.1）**：单节点 8× A100-80GB（NVLINK）；Qwen2.5-14B / 32B（FP16；32B 用 TP=2）；基线同在 vLLM 上实现的 **PD aggregation（chunked prefill）** 与 **PD disaggregation**。工作负载与 SLO（Table 3）：

| 应用 | 输入/输出均值（文内） | SLO1 | SLO2 |
|---|---|---|---|
| ShareGPT（chatbot） | ≈661 / ≈257 | (3s, 110ms) | (4s, 70ms) |
| Arxiv Summarization | ≈7317 / ≈201 | (4s, 70ms) | (6s, 50ms) |

指标：在 **90% SLO attainment** 下的最大 goodput。

**端到端（§4.2）**：相对 PD aggregation goodput **+9–47%**；相对 PD disaggregation **+29–77%**（跨 chatbot / summarization 与两档 SLO）。摘要与结论中的「up to **77%**」对应 summarization、相对解聚的上沿（14B / 32B 在 SLO1 下分别约 77% / 74%）。

**尾延迟（§4.3）**：在 TaiChi 最大合规负载下，相对解聚的 P90 TTFT 降 **2.42×–13.20×**；相对聚合的 P90 TPOT 降 **1.11×–1.69×**。

**消融（§4.4，summarization SLO1、Qwen2.5-14B）**：CP256 基线 SLO 达标 **66.6%** → 加 hybrid 架构与流动 decode / 长度感知 prefill 后至 **91.2%**。

**开销（§4.5）**：单请求时间中，KV 传输 / prefill 调度 / decode 调度约占 **0.20% / 0.01% / 0.89%**。

---

## 五、与 Orca / MegaScale 的分工

| 议题 | 动什么 | 本篇角色 |
|---|---|---|
| [[连续批处理与Orca]] | 调度粒度：请求级 → **iteration-level**；selective batching | **正交**：连续批解决批内早结束 / 晚加入；PD 轴解决两阶段是否同池。TaiChi Related works 亦称 goodput 优化与 continuous batching 等正交。引擎侧常叠加（vLLM 上既有 continuous batching，又可做 PD 分池）。 |
| [[MegaScaleInfer与UltraEP]] | MoE 服务：**Attention 节点 ↔ Expert 节点** 解耦、大 EP 均衡 | **另一解耦轴**：专家稀疏利用率，不是 TTFT/TPOT 双 SLO 的 PD 池化。 |
| [[推理引擎生态]] / [[AI基础设施总览]] | 引擎选型、DeepSeek-V3 报告级 Prefill/Decode 分阶段部署表 | 本篇补 **学术系统侧**「聚合 ↔ 解聚 ↔ 再统一」机制与证据，不重写引擎对照表。 |

一句话：Orca 管「批怎么连续」；MegaScale 管「Attention 与 Expert 分不分机」；本篇管「Prefill 与 Decode 分不分池、平衡 SLO 时如何把余量挪给濒危请求」。

---

## 六、开放问题

1. **输出长度先验**：流动 decode 用「当前最长」启发式规避预测器；文内称长度预测准确率常见仅约 60%–81%，误差会直接吃掉 SLO 达标率——生产级预测是否可嵌进水位策略，仍开放。
2. **滑块搜索与在线漂移**：最优 $(R_{PD},S_P,S_D)$ 依赖离线搜索；重配分钟级是否覆盖突发、多租户混合 SLO，需运维层证据。
3. **规模外推**：主评测为单节点 8×A100、Qwen2.5 14B/32B；多节点、更强互联、MLA/GQA 下 KV 传输占比变化后，hybrid 相对纯解聚的优势幅度需重测。
4. **与其他解耦轴叠乘**：PD 统一服务与 Attention–Expert 解耦、前缀缓存、投机解码叠乘时的联合调度，主文未系统评价。
5. **开源与可复现**：文称基于 vLLM 实现并计划开源；入库时以 arXiv 叙述为准，不以未核验仓库状态作事实。

---

## 七、文献

| 角色 | 文献 | 入口 |
|---|---|---|
| **主** | Wang, Zuo, Chen, Liang, Yu, Yang. *Prefill-Decode Aggregation or Disaggregation? Unifying Both for Goodput-Optimized LLM Serving*（TaiChi） | https://arxiv.org/abs/2508.01989 （v1，2025-08-04；17 pages） |
| **史前对照** | Zhong, Liu, Chen, Hu, Zhu, Liu, Jin, Zhang. *DistServe: Disaggregating Prefill and Decoding for Goodput-optimized Large Language Model Serving* | https://arxiv.org/abs/2401.09670 |
| **一句交叉** | Qin et al. *Mooncake: A KVCache-centric Disaggregated Architecture for LLM Serving* | 见主文 References；不升第二主文 |
| **聚合侧基线（文内）** | Orca（OSDI 2022）；Sarathi-Serve（OSDI 2024，chunked prefill） | 详见 [[连续批处理与Orca]]；Sarathi 不另开题 |
