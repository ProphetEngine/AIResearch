---
date: 2026-10-09
status: archived
archived: 2026-10-09
topic: RL训练系统与异步Rollout
title: "RL训练系统与异步Rollout"
lines: [AI Infra, 架构思想]
sources:
  - https://arxiv.org/abs/2409.19256
  - https://arxiv.org/abs/2505.24298
  - https://arxiv.org/abs/2509.19128
  - https://arxiv.org/abs/2510.12633
  - https://arxiv.org/abs/2510.26788
  - https://arxiv.org/abs/2405.11143
  - https://arxiv.org/abs/2410.18252
  - https://arxiv.org/abs/2501.12599
  - https://arxiv.org/abs/2504.15930
  - https://arxiv.org/abs/2505.24034
  - https://arxiv.org/abs/2506.06122
  - https://arxiv.org/abs/2506.13585
  - https://www.lmsys.org/blog/2025-07-09-slime/
  - https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/
  - https://arxiv.org/abs/2510.11370
  - https://arxiv.org/abs/2601.12784
  - https://arxiv.org/abs/2604.26256
  - https://arxiv.org/abs/2607.18722
  - https://github.com/verl-project/verl
  - https://github.com/OpenRLHF/OpenRLHF
  - https://github.com/areal-project/AReaL
  - https://github.com/THUDM/slime
  - https://github.com/alibaba/ROLL
arxiv: ["2409.19256", "2505.24298", "2509.19128", "2510.12633", "2510.26788", "2405.11143", "2410.18252", "2501.12599", "2504.15930", "2505.24034", "2506.06122", "2506.13585", "2510.11370", "2601.12784", "2604.26256", "2607.18722"]
related: ["分布式训练并行策略", "AI基础设施总览", "推理引擎生态", "PrefillDecode分离与统一服务", "连续批处理与Orca", "RL算力缩放与环境扩展", "GRPO与DAPO算法族", "MiniMaxM1技术报告深读", "Kimik15技术报告深读", "KimiK2技术报告深读", "KimiK3技术报告", "GLM45技术报告深读", "MiMoV26智能体强化学习短报", "MistralLarge4短报", "SEA-LION低资源区域模型", "NVSHMEM与DeepEP通信", "混合专家架构", "OnPolicy蒸馏OPD范式"]
---

# RL训练系统与异步Rollout

> **主要来源**：[HybridFlow: A Flexible and Efficient RLHF Framework](https://arxiv.org/abs/2409.19256)；[AReaL: A Large-Scale Asynchronous Reinforcement Learning System for Language Reasoning](https://arxiv.org/abs/2505.24298)；[PipelineRL: Faster On-policy Reinforcement Learning for Long Sequence Generation](https://arxiv.org/abs/2509.19128)；[Laminar: A Scalable Asynchronous RL Post-Training Framework](https://arxiv.org/abs/2510.12633)；[Defeating the Training-Inference Mismatch via FP16](https://arxiv.org/abs/2510.26788)（简称 FP16 论文）（截至 2026-08-03）。其余来源见第十二节。
> **研究线**：AI Infra（RL 后训练的生成、打分、训练三段如何放到 GPU 上，权重如何在训练后端与推理引擎之间同步，长尾生成怎样调度）· 架构思想（异步换来的吞吐与离策偏差如何权衡，训推数值不一致如何破坏同策假设）
> **范围与相邻笔记**：
> - ≠ [[GRPO与DAPO算法族]]：本篇不推导策略优化目标，只写系统对离策数据的处理思路。
> - ≠ [[MiniMaxM1技术报告深读]]：本篇不写 M1 的架构与 CISPO 目标，只取其训推概率对齐的做法。
> - ≠ [[RL算力缩放与环境扩展]]：本篇不写算力缩放曲线、环境构建与 rollout 策略分类，只展开其中异步与部分 rollout 的系统实现。
> - ≠ [[分布式训练并行策略]]：本篇不重写各种并行与 ZeRO/FSDP，只写 RL 中训练与生成两套并行如何共存。
> - ≠ [[推理引擎生态]]：本篇不写推理引擎本身与选型，只写引擎在 RL 环路中的用法。
> - ≠ [[连续批处理与Orca]]：本篇不写推理引擎内部的 KV 管理与批处理调度。
> - 本篇不写各厂商技术报告的完整 RL 配方，只取系统设计要点作案例。
>
> **意义**：长推理与智能体 RL 让生成成为后训练的主要耗时，系统设计决定了同样的 GPU 能跑多少步 RL。异步把 GPU 利用率换成离策偏差，训推不一致又让名义上的同策训练悄悄变成离策；这两件事把 RL 系统从「把训练和推理接起来」的工程问题，变成了需要系统与算法协同设计的问题。

**一句话**：RL 后训练每一步都要先用当前策略生成一批轨迹、打分，再用它们更新策略。生成是长度呈长尾的自回归解码，同步执行时整批都要等最长的那条，GPU 大量空转。系统的演进沿两条线展开：一是让生成和训练不再互相等待，从共置分时、资源分离、跨迭代续写长轨迹，到生成不等训练的全异步、生成途中换权重、以单条轨迹为粒度的异步；二是补偿由此带来的偏差，包括限制陈旧度、解耦行为策略与近端策略、截断重要性采样，以及从精度、路由与内核上消除训练与推理之间的数值差异。

## 一、问题背景：生成是瓶颈，两套引擎要对齐

1. **一步 RL 由三段组成**。生成（rollout）用当前策略为每个提示采样回答或多轮轨迹；打分由规则验证器、奖励模型或环境给出；训练用这些样本计算梯度并更新策略。StaleFlow 把这三段称为 rollout、reward、training，并指出近来的趋势是把它们放到不同资源上异步执行（StaleFlow 论文摘要）。
2. **生成占大头且有长尾**。DORA 称 rollout 阶段占每步总时间的 50–80%，长尾轨迹对模型表现不可缺少，却会阻塞整条训练流水线（DORA 论文摘要）。AReaL 描述了同步系统的根本低效：训练前必须等批内最长的输出完成，GPU 利用率因此偏低（AReaL 论文摘要）。Laminar 把这种极端长尾称为造成 GPU 严重闲置的主因（Laminar 论文摘要）。
3. **生成与训练用不同的引擎**。为了吞吐，生成通常交给 vLLM、SGLang 这类推理引擎，训练用 FSDP、Megatron 等后端，两者的并行切法可能不同，每次更新后都要把权重从训练端传到推理端。Kimi k1.5 报告列出了这一点带来的困难：Megatron 与 vLLM 的并行策略可能不同，分布在多个节点上的训练权重难以直接共享给 vLLM（Kimi k1.5 论文 §2.6.3）。
4. **两套引擎算出的概率不一样**。即使权重相同，推理引擎与训练后端因精度误差和硬件相关的优化，输出的数值也不同；FP16 论文称这种训推不一致是 RL 微调不稳定的关键来源之一（FP16 论文 §1）。

## 二、发展脉络

| 时间 | 节点 | 推进了什么 |
|---|---|---|
| 2024-05 | [OpenRLHF](https://arxiv.org/abs/2405.11143) | 基于 Ray、vLLM、DeepSpeed 的开源 RLHF 框架，各模型可放在不同的 GPU 组上 |
| 2024-09 | [HybridFlow（verl）](https://arxiv.org/abs/2409.19256) | 单控制器管数据流、多控制器管分布式计算的混合编程模型；训练与生成之间零冗余的权重重分片 |
| 2024-10 | [Asynchronous RLHF（Noukhovitch 等）](https://arxiv.org/abs/2410.18252) | 把生成与学习分开、在旧样本上训练；核心问题是能容忍多大的离策程度 |
| 2025-01 | [Kimi k1.5](https://arxiv.org/abs/2501.12599) | 部分 rollout：每轮设输出 token 预算，超长轨迹存入回放缓冲区、下一轮续写；训练与推理共置 |
| 2025-04 | [StreamRL](https://arxiv.org/abs/2504.15930) | 论证共置架构的资源耦合问题，分离式架构便于异构与跨数据中心部署 |
| 2025-05 | [LlamaRL](https://arxiv.org/abs/2505.24034)、[AReaL](https://arxiv.org/abs/2505.24298) | 工业级与开源的全异步系统：生成不等训练；陈旧度上限与解耦 PPO |
| 2025-06 | [ROLL](https://arxiv.org/abs/2506.06122)、[MiniMax-M1](https://arxiv.org/abs/2506.13585) | 面向智能体 RL 的库，rollout 调度器管理单个样本的生命周期；M1 把输出头提到 FP32 以对齐训推概率 |
| 2025-07 | [slime](https://www.lmsys.org/blog/2025-07-09-slime/) | SGLang 原生的 RL 框架，用一个参数切换共置或分离，借助 Ray 的异步执行支持异步训练 |
| 2025-08 至 2025-10 | Yao 等的博文（见 6.2）、[Thinking Machines 博文](https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/)、[R3](https://arxiv.org/abs/2510.11370)、[FP16 论文](https://arxiv.org/abs/2510.26788) | 训推不一致被系统识别：截断重要性采样修正、推理非确定性的来源与批不变内核、MoE 路由回放、改用 FP16 |
| 2025-09 | [PipelineRL](https://arxiv.org/abs/2509.19128) | 在途权重更新：生成途中短暂暂停换新权重，再继续生成未完成的序列 |
| 2025-10 | [Laminar](https://arxiv.org/abs/2510.12633) | 轨迹级异步：中继 worker 作分布式参数服务，长尾轨迹动态重打包到少数实例 |
| 2026-01 至 2026-07 | [StaleFlow](https://arxiv.org/abs/2601.12784)、[DORA](https://arxiv.org/abs/2604.26256)、[SAT](https://arxiv.org/abs/2607.18722) | 全分离架构下同时约束陈旧度与长尾倾斜；多版本流式 rollout 与滑动陈旧度窗口；按陈旧度收紧 PPO 裁剪区间 |

主线可以概括为：同步的开源 RLHF 框架（2024）；长推理 RL 让生成长尾成为主瓶颈，出现部分 rollout 与全异步（2025 上半年）；训推不一致被识别为同策假设失效的另一来源（2025 下半年）；在途权重更新与轨迹级异步把异步细化到单条轨迹（2025-09 至 2025-10）；陈旧度控制从一个工程参数变成系统与算法协同设计的对象（2026）。

## 三、术语：几种「异步」

不同论文说的「异步」指代不同，先对齐术语：

| 说法 | 指什么 | 代表 |
|---|---|---|
| 同步、共置 | 生成与训练在同一组 GPU 上轮流执行，每批样本都由当前策略生成 | Kimi k1.5 的混合部署；DeepSpeed-Chat 式系统 |
| 资源分离 | 生成与训练各用一组 GPU，可以同步也可以异步执行 | StreamRL、OpenRLHF |
| 部分 rollout | 每轮只生成固定 token 预算，未完成的轨迹下一轮续写，一条轨迹可能跨多个策略版本 | Kimi k1.5 |
| 全异步 | 生成端持续生成、不等训练，训练端凑够一批即更新 | LlamaRL、AReaL |
| 在途权重更新 | 生成途中换新权重，已生成的前缀不重算，序列后段由新策略生成 | PipelineRL |
| 轨迹级异步 | 每条轨迹独立生成、独立被消费，各 rollout 实例自行拉取新权重 | Laminar |
| 多版本流式 | 同时维持多个策略版本的 rollout，以单个请求为粒度跨版本派发与收集 | DORA |
| 陈旧度 | 生成某条样本所用的策略版本落后于当前训练版本的步数 | AReaL、StaleFlow |

## 四、系统架构谱系

### 4.1 控制器：单控制器与多控制器

HybridFlow 把 RL 建模为数据流：每个节点是一次神经网络计算，每条边是数据依赖。在 LLM 场景下，每个节点都扩展成分布式的训练或生成程序，每条边变成多对多的数据传输。传统 RL 框架用单个控制器同时指挥节点内计算和节点间通信，分布式计算的调度开销大；已有的 RLHF 系统用多控制器，又因为分布式计算与数据通信相互嵌套而不灵活。HybridFlow 的做法是混合：单控制器表达节点之间的数据流，多控制器执行节点内的分布式计算，并用一组分层 API 把计算与数据依赖解耦（HybridFlow 论文摘要）。verl 是 HybridFlow 的开源版本，README 自述其混合控制器编程模型可以用几行代码搭出 GRPO、PPO 等数据流，并支持把模型灵活映射到不同的 GPU 组（verl README）。后来的 LlamaRL、ROLL 也采用单控制器架构（LlamaRL 论文摘要；ROLL 论文摘要）。

### 4.2 共置与分离

- **共置**：生成与训练分时复用同一组 GPU。Kimi k1.5 的混合部署是一个例子：Megatron 训练完成后卸载显存，vLLM 以空权重启动、接收最新权重并完成 rollout，之后释放显存，Megatron 重新加载并开始下一轮训练（Kimi k1.5 论文 §2.6.3）。HybridFlow 的 3D-HybridEngine 解决共置下的权重重分片问题：同一个 actor 在训练与生成阶段使用不同的并行切法，切换时做到零显存冗余并显著降低通信开销（HybridFlow 论文摘要）。HybridFlow 对比了几种放置方式：DeepSpeed-Chat 把所有模型共置在同一组设备上，OpenRLHF 把每个模型放在不同设备上，NeMo-Aligner 把 actor 与参考模型共置、critic 与奖励模型共置在另一组设备上，HybridFlow 支持多种放置（HybridFlow 论文表 1）。
- **分离**：StreamRL 指出，一般认为共置优于分离，但在真实部署中共置存在资源耦合，两段被迫使用同样的资源，影响大规模训练的扩展性与成本；分离式允许灵活分配资源、支持异构硬件，也便于跨数据中心部署（StreamRL 论文摘要）。分离的代价是两种气泡：阶段依赖造成的流水气泡，以及长尾输出长度造成的倾斜气泡。StreamRL 用流式生成打破同步算法中的阶段边界，并在异步算法中做到完全重叠；用一个输出长度排序模型识别长尾样本，再做倾斜感知的派发与调度（StreamRL 论文摘要）。

推理服务里也有「prefill 与 decode 共置还是分离」的同类问题，两者的取舍逻辑相近，但约束不同，见第十一节。

### 4.3 部分 rollout：把长轨迹切段

Kimi k1.5 为长上下文 RL（上下文窗口扩到 128k）设计了部分 rollout：每条轨迹设固定的输出 token 预算，超出预算的未完成部分存入回放缓冲区，下一轮继续生成，避免单条长轨迹独占资源；rollout worker 异步运行，有的处理长轨迹时，其他 worker 可以处理新的短任务。只有当前这一轮的片段需要同策计算，之前各轮的片段从缓冲区复用；训练时还可以把某些片段排除在损失之外（Kimi k1.5 论文 §1、§2.6.2）。部分 rollout 的代价是一条轨迹的不同片段来自不同的策略版本。

### 4.4 全异步：生成不等训练

- **可行性**。Noukhovitch 等借鉴经典深度 RL 的做法，把 RLHF 的生成与学习分开，在训练旧样本的同时异步生成新样本；这进入了「在线但离策」的区域，样本来自模型之前的版本，训练信号更差。他们在测试的几种 RLHF 算法中发现在线 DPO 对离策数据最稳健，且稳健性随策略模型规模增大而提高；用 LLaMA 3.1 8B 训练通用对话模型时，异步训练更快，最终表现与同步持平（Noukhovitch 等论文摘要）。
- **工业规模**。LlamaRL 是完全分布式的异步 RL 框架，基于原生 PyTorch 和单控制器架构，在 Llama 3 后训练中结合共置模型卸载、异步离策训练和用于权重同步的分布式直接内存访问；论文还给出异步设计带来严格加速的形式化证明（LlamaRL 论文摘要）。
- **开源系统**。AReaL 完全解耦生成与训练：rollout worker 持续生成、不等待，训练 worker 每凑够一批数据就更新模型；为稳定训练，它平衡 rollout 与训练两侧的负载以控制陈旧度，并采用针对陈旧样本增强的 PPO 变体（AReaL 论文摘要）。具体做法见第五节。

### 4.5 在途权重更新

PipelineRL 把异步思想用到长序列生成上：生成与训练并发进行，新权重就绪时，生成引擎只短暂暂停，经高速互联接收权重，然后继续生成进行中的序列。这样不必等最后一条序列结束，生成批大小保持恒定，最近生成的 token 也最大程度地贴合当前策略（PipelineRL 论文摘要、§1）。代价是同一条序列的前段与后段可能来自不同的策略版本。

### 4.6 轨迹级异步与多版本流式

- **Laminar**。已有的异步系统依赖 actor 与所有 rollout 之间的全局权重同步，更新节奏僵硬，不适合高度倾斜且不断变化的生成时长分布。Laminar 用一层中继 worker 充当分布式参数服务，actor 不间断训练，各 rollout 随时可从中继拉取最新权重；再用动态重打包机制把未充分利用的 rollout 上的长尾轨迹集中到少数专门实例上。完全解耦的设计也隔离了故障，有利于长时间运行的任务（Laminar 论文摘要、§1）。
- **StaleFlow**。在全分离架构下，严格控制陈旧度会限制长尾倾斜的缓解，激进地缓解倾斜又会加剧陈旧度，已有系统只能在收敛与性能之间二选一。StaleFlow 用全局一致性协议跟踪每条轨迹的完整生命周期并约束陈旧度，同时为轨迹和参数构建数据服务器以灵活协调 rollout，再配合一组陈旧度感知、面向吞吐的策略（StaleFlow 论文摘要）。
- **DORA**。DORA 提出保持收敛的三个约束：轨迹内策略一致、数据完整、陈旧度有界（DORA 论文摘要）。它指出部分 rollout 一类方法在每次权重更新时切断长轨迹、用新策略续写，系统上每次更新都让 KV 缓存失效、需要重新 prefill，算法上一条轨迹拼接了多个策略版本（DORA 论文 §2）。它的多版本流式 rollout 同时维持多个策略版本，以单个请求为粒度跨版本派发和收集轨迹，用滑动窗口约束陈旧度，并由中心化的编排器按各版本待处理的工作量重新划分数据并行组、迁移请求（DORA 论文摘要、§1）。DORA 也指出，MoE 模型的负载不均衡会进一步加剧长尾问题（DORA 论文摘要）。

### 4.7 权重同步

无论共置还是分离，每次更新后都要把权重从训练端交给推理端。几种公开的做法：Kimi k1.5 通过 checkpoint-engine 进程协调，经 Mooncake 把 Megatron 的权重传给 vLLM（Kimi k1.5 论文 §2.6.3）；LlamaRL 用分布式直接内存访问做权重同步（LlamaRL 论文摘要）；PipelineRL 经高速互联在途推送（PipelineRL 论文 §1）；Laminar 由中继 worker 提供异步、细粒度的拉取（Laminar 论文摘要）。slime 的 README 列出增量权重同步、跨 GPU 集群的外部 rollout 引擎等部署选项（slime README）。

## 五、陈旧度与离策修正

异步的收益依赖算法能否容忍旧策略生成的数据。各系统的补偿思路可以分四类：

1. **给陈旧度设上限**。AReaL 引入超参数，规定每个训练批中允许的最大陈旧度，取零时系统退化为同步 RL。实现上，rollout 控制器跟踪已生成的样本数和参数服务器上的策略版本，拒绝可能违反约束的新生成请求，并优先用较旧的轨迹组成训练批。作者发现上限太小时，个别极长的轨迹会拖慢生成吞吐，因此建议取较大的上限以获得最佳吞吐，再用更强的算法利用更陈旧的数据（AReaL 论文 §5.1）。DORA 的滑动窗口、StaleFlow 的全局一致性协议也属这一类（DORA 论文 §1；StaleFlow 论文摘要）。
2. **解耦行为策略与近端策略**。标准 PPO 用采样策略同时充当重要性采样的分母和裁剪的参照。AReaL 采用解耦的 PPO 目标，把用于采样轨迹的行为策略和用来约束更新幅度的近端策略分开：近端策略是一个较新的目标策略，对行为策略的偏差用重要性采样修正，裁剪则相对近端策略进行（AReaL 论文 §5.2）。这样旧样本仍可使用，而更新不至于因参照过旧而失控。
3. **截断重要性采样**。用推理侧与训练侧概率之比作为重要性权重，理论上可得到无偏梯度，但长序列上比值容易极端、方差很大；截断重要性采样（TIS）给权重设上限，以少量偏差换取方差的大幅下降，掩码重要性采样（MIS）则直接屏蔽比值异常的样本（FP16 论文 §2.1）。这类修正最早用于训推不一致，见 6.2。
4. **按陈旧度收紧信赖域**。SAT 从信赖域角度指出，PPO 裁剪只约束被采样到的、向外的更新，只是全策略约束的一个采样替代，因此在陈旧样本最多的异步区间，高陈旧度的更新恰恰控制最弱。SAT 用采样到的对数比作为陈旧度的代理，识别每批中失配最严重的尾部，只对这些 token 收紧 PPO 裁剪区间对应的一端，普通 token 保持基线行为（SAT 论文摘要）。SAT 还把陈旧度的来源归为策略滞后、引擎延迟和 MoE 路由三者的叠加（SAT 论文摘要），这说明异步造成的陈旧与第六节的训推不一致在算法上是同一个问题。

## 六、训推不一致：同一权重，两种概率

### 6.1 现象与来源

- **现象**。MiniMax-M1 在 RL 训练中观察到，同一个已生成 token 在训练模式与推理模式下的概率差异显著，阻碍了奖励增长；这一问题在较小的、使用 softmax 注意力的稠密模型上没有出现（MiniMax-M1 论文 §3.2）。R3 论文指出，推理与训练引擎分离会导致 token 概率分歧，甚至引发 RL 训练崩溃（R3 论文 §1）。
- **数值精度**。FP16 论文认为根因在浮点精度本身：广泛采用的 BF16 动态范围大，但精度低，舍入误差累积后让训练策略与推理策略分离（FP16 论文摘要、§1）。MiniMax-M1 逐层分析后，把误差主要来源定位到输出层 LM head 的大幅值激活（MiniMax-M1 论文 §3.2）。
- **推理非确定性**。Thinking Machines 的博文指出，即使温度设为零，vLLM、SGLang 等推理库的采样仍不确定；常见的「并发加浮点」假设不足以解释，关键是常用内核缺乏批不变性：批大小一变，批内同一元素的计算结果就可能不同（Thinking Machines 博文「Batch invariance and determinism」一节）。服务器负载决定批大小，同一请求因此会得到不同结果。
- **MoE 路由**。R3 论文发现 MoE 模型在训练与推理两个阶段的路由行为明显不同，甚至在相同条件下，重复前向也可能选出不同的专家；路由的变化让 MoE 模型的训推策略差异大于稠密模型（R3 论文摘要、§1）。

### 6.2 补偿与消除

| 做法 | 思路 | 依据 | 代价 |
|---|---|---|---|
| 截断重要性采样 | 训练时用推理与训练概率之比修正梯度并截断 | Yao 等提出逐 token 的重要性比修正，后续工作改用序列级比值（FP16 论文 §1） | FP16 论文指出逐 token 修正有偏、不足以完全稳定训练，序列级修正收敛慢；都需要额外一次前向，约增加 25% 训练成本；训练后的参数对推理引擎并非最优 |
| 输出头 FP32 | 提高 LM head 的计算精度 | MiniMax-M1 论文 §3.2 | 只针对已定位的误差源 |
| 改用 FP16 | 用尾数位更多的 FP16 取代 BF16 | FP16 论文摘要、§1 | 论文称只需改几行代码，无需改模型结构或算法；同时消除了部署时的不一致 |
| 路由回放（R3） | 记录推理引擎的路由分布，训练时回放 | R3 论文摘要、§1 | 针对 MoE；论文称不影响训练速度，显著概率差异的 token 数约减少一个数量级 |
| 批不变的确定性内核 | 让推理与训练得到逐位相同的结果 | Thinking Machines 博文「True on-policy RL」一节 | 需要改写 RMSNorm、矩阵乘、注意力等内核 |

两类做法的思路不同：重要性采样一类在算法上补偿不一致，FP16、路由回放与确定性内核在数值上消除不一致。FP16 论文特别指出，补偿类做法无法弥合「部署差距」：模型参数是按训练引擎的分布优化的，部署时用的却是推理引擎（FP16 论文 §2）。Thinking Machines 的实验显示，不做离策修正时奖励在训练中途崩溃，加入重要性加权后训练平稳，而做到采样与训练逐位一致时，两者之间的 KL 散度始终为零，训练同样平稳（Thinking Machines 博文「True on-policy RL」一节）。R3 论文称在其设定下优于 GSPO 与 TIS（R3 论文摘要）；SAT 在 R3 之上叠加按陈旧度收紧裁剪（SAT 论文摘要），说明消除类与补偿类做法可以组合使用。

## 七、智能体 RL 带来的系统约束

多轮工具调用、代码执行和外部环境让 rollout 时长更不均匀，也让「生成」不再只是推理引擎的事。公开系统的应对集中在接口与调度上：

- **环境与奖励独立成 worker**。ROLL 的环境 worker 与奖励 worker 支持快速试验智能体 RL 算法和奖励设计，rollout 调度器对 rollout 阶段每个样本的生命周期做细粒度管理，AutoDeviceMapping 允许在不同阶段把资源灵活分配给不同模型（ROLL 论文摘要）。
- **可定制的生成接口**。slime 在框架内用路由器管理所有 SGLang 服务器，并提供数据生成接口供用户注入自定义逻辑；通过 OpenAI 兼容的接口，复杂的智能体环境可以不改代码直接与 slime 交互（slime 博文）。README 称多轮循环、工具调用、环境与沙箱交互、基于验证器的奖励都可以包进自定义生成函数（slime README）。
- **沙箱作为环境服务**。Kimi k1.5 报告单列了代码沙箱一节（Kimi k1.5 论文 §2.6.4）。环境本身怎样构建、怎样批量扩展，属于 [[RL算力缩放与环境扩展]] 的范围。

## 八、开源框架格局

以下定位均以各项目论文与 README 的自述为准，不做性能排名：

| 框架 | 自述定位 | 训练与生成后端 | 来源 |
|---|---|---|---|
| OpenRLHF | 基于 Ray 与 vLLM 分布式架构的开源 RLHF 框架，强调易用 | Ray、vLLM、DeepSpeed | OpenRLHF 论文摘要；OpenRLHF README |
| verl | HybridFlow 的开源版本，混合控制器编程模型，灵活的设备映射 | FSDP、Megatron-LM、vLLM、SGLang 等 | verl README |
| AReaL | 基于全异步 RL 范式，面向推理与智能体模型 | 论文实现用 SGLang 生成、Megatron-Core 训练 | AReaL 论文摘要、§6；AReaL README |
| slime | SGLang 原生的后训练框架，共置或分离用一个参数切换，同步与异步训练均支持 | Megatron、SGLang，经数据缓冲区衔接 | slime 博文；slime README |
| ROLL | 面向大规模 GPU 的 RL 库，覆盖偏好对齐、复杂推理与多轮智能体交互 | Ray、Megatron-Core、SGLang、vLLM | ROLL 论文摘要；ROLL README |

各系统论文报告的加速比来自不同的基线、模型规模与集群，只能在各自设定内理解，不可横向比较：

| 系统 | 原文结论 | 对比基线与设定 |
|---|---|---|
| AReaL | 训练加速最高 2.77 倍，最终表现持平或更好 | 相同 GPU 数的同步系统，数学与代码推理 |
| PipelineRL | 学习速度约快 2 倍，数据保持高度同策 | 128 张 H100，对比常规 RL 基线 |
| StaleFlow | 吞吐高 1.42–2.68 倍（平均 1.18–1.91 倍），不损收敛 | 对比先进系统 |

## 九、意义

- **异步是吞吐与偏差的交换**：从部分 rollout 到多版本流式，每一步都在让 GPU 更少空转，同时让训练数据更离策；系统能走多远，取决于算法能容忍多大的陈旧度。陈旧度上限、解耦 PPO、按陈旧度收紧裁剪让这一容忍度可以显式设定。
- **同策是一个需要工程保证的假设**：训推不一致说明，即使完全同步，只要生成与训练用两套引擎，RL 就已经是离策的。精度、路由与内核层面的对齐，把「同策」从默认前提变成需要验证的系统属性。
- **系统与算法开始协同设计**：DORA 的三个约束、StaleFlow 对陈旧度与倾斜的联合处理、SAT 把陈旧度信号接进信赖域，说明 RL 系统不再只是加速器，它的设计选择直接决定算法所见的数据分布。

## 十、局限与待核实

1. **加速比不可比**：第八节的数字来自不同基线、模型、任务与集群，多为论文作者在自选设定下的结果；各系统之间没有统一基准的对比。
2. **收敛结论依赖设定**：「不损收敛」「表现持平」多基于数学、代码推理等可验证任务，在奖励来自评分模型的任务或长程智能体任务上是否成立，各文证据有限。Noukhovitch 等也发现进一步的算力优化会带来表现损失，存在权衡（Noukhovitch 等论文摘要）。
3. **训推不一致的根因仍有分歧**：FP16 论文把根因归于 BF16 精度，MiniMax-M1 定位到输出头，R3 强调 MoE 路由，Thinking Machines 强调内核缺乏批不变性；这些结论来自不同模型与设定，相互之间的相对重要性未见系统比较。
4. **Yao 等的博文未能直接读取**：该博文托管在 Notion 上，页面需脚本渲染，本篇不挂链接，关于它的描述取自 FP16 论文与 R3 论文的引述，首发时间只写到月（2025-08）。
5. **StaleFlow 改过题名**：该文 v1 题为 *Unleashing Efficient Asynchronous RL Post-Training via Staleness-Constrained Rollout Coordination*，本篇所用的 v2 改题为 *StaleFlow: Staleness-Aware Data Management for Mitigating Data Skewness in Fully Disaggregated RL Post-Training*；两版摘要中的平均加速区间也略有不同，本篇按 v2 写。
6. **README 会变**：第八节的框架定位与后端取自当前 README，项目演进后可能变化。
7. **未覆盖的方向**：量化 rollout、推测解码在 rollout 中的应用、容错与检查点恢复、多智能体自博弈的系统设计，本篇未展开。

## 十一、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[分布式训练并行策略]] | 前置知识：本篇用到的并行术语出自该篇；训练与生成两套并行切法不同，正是权重重分片与训推不一致的来源之一 | 各种并行与 ZeRO/FSDP |
| [[AI基础设施总览]] | 上位总览：本篇补上总览中 RL 训练系统这一层 | 训练并行、注意力核、推理 KV 与低精度总览 |
| [[推理引擎生态]] | 上游组件：rollout 后端用的推理引擎由该篇介绍，本篇只写它们在 RL 环路中的用法与权重热更新 | 推理引擎本身 |
| [[连续批处理与Orca]] | 上游组件：推理引擎的批处理机制是 rollout 吞吐的基础 | 连续批处理与调度 |
| [[PrefillDecode分离与统一服务]] | 类比：推理服务中 prefill 与 decode 的共置与分离，与第四节生成与训练的共置与分离是同一类取舍 | prefill 与 decode 分离 |
| [[RL算力缩放与环境扩展]] | 上位视角：该篇的 rollout 控制模块中的异步与部分 rollout，由本篇展开系统实现；环境构建归该篇 | 算力缩放曲线、环境扩展与 rollout 策略分类 |
| [[GRPO与DAPO算法族]] | 算法层：本篇第五节的离策修正作用在这些目标函数之上 | 目标函数与稳定化技巧 |
| [[MiniMaxM1技术报告深读]] | 工业案例：训推不一致一节引用的输出头精度问题出自 M1 | M1 架构与 CISPO |
| [[Kimik15技术报告深读]] / [[KimiK2技术报告深读]] / [[KimiK3技术报告]] | 工业案例：部分 rollout 与共置部署的系统要点出自 Kimi 系列 | 各报告的模型与训练全貌 |
| [[GLM45技术报告深读]] | 厂商侧用法：本篇第八节的 slime 只取框架自述，它在厂商后训练中的配置看那篇 | GLM-4.5 的模型与后训练 |
| [[MiMoV26智能体强化学习短报]] / [[MistralLarge4短报]] | 工业案例：近一年异步 RL 在厂商训练中的落地 | 两份短报全文 |
| [[SEA-LION低资源区域模型]] | 实例：第五节第 1 类「给陈旧度设上限」在该篇训练中的一个具体取值 | 区域模型的数据与训练 |
| [[NVSHMEM与DeepEP通信]] / [[混合专家架构]] | MoE 背景：第六节的路由不一致与第四节 MoE 加剧长尾都以 MoE 结构与专家并行为前提 | 专家并行通信与 MoE 结构 |
| [[OnPolicy蒸馏OPD范式]] | 同类负载：在线蒸馏同样需要学生在线生成，可复用本篇的系统设计 | OPD 方法 |

## 十二、延伸阅读

建议顺序：先读 HybridFlow 与 OpenRLHF 理解同步框架与放置方式，再读 Kimi k1.5 第 2.6 节与 StreamRL 理解共置、分离与部分 rollout，然后读 AReaL 与 PipelineRL 理解全异步与在途更新，接着读 FP16 论文、R3 与 Thinking Machines 博文理解训推不一致，最后按兴趣读 Laminar、StaleFlow、DORA 与 SAT。

| 文献 | 链接 | 与本篇的关系 |
|---|---|---|
| OpenRLHF（Hu et al., 2024） | https://arxiv.org/abs/2405.11143 | 基于 Ray 的开源 RLHF 框架 |
| HybridFlow（Sheng et al., 2024） | https://arxiv.org/abs/2409.19256 | 混合控制器与 3D-HybridEngine |
| Asynchronous RLHF（Noukhovitch et al., 2024） | https://arxiv.org/abs/2410.18252 | 异步 RLHF 与离策容忍度 |
| Kimi k1.5（Kimi Team, 2025） | https://arxiv.org/abs/2501.12599 | 部分 rollout 与混合部署 |
| StreamRL（Zhong et al., 2025） | https://arxiv.org/abs/2504.15930 | 分离式架构与长尾调度 |
| LlamaRL（Wu et al., 2025） | https://arxiv.org/abs/2505.24034 | 工业级异步框架 |
| AReaL（Fu et al., 2025） | https://arxiv.org/abs/2505.24298 | 全异步、陈旧度上限与解耦 PPO |
| ROLL（Wang et al., 2025） | https://arxiv.org/abs/2506.06122 | 面向智能体 RL 的库 |
| MiniMax-M1（MiniMax, 2025） | https://arxiv.org/abs/2506.13585 | 输出头 FP32 的训推对齐 |
| slime（LMSYS 博文, 2025-07） | https://www.lmsys.org/blog/2025-07-09-slime/ | SGLang 原生 RL 框架 |
| Defeating Nondeterminism in LLM Inference（Thinking Machines, 2025-09） | https://thinkingmachines.ai/blog/defeating-nondeterminism-in-llm-inference/ | 批不变内核与真同策 RL |
| PipelineRL（Piché et al., 2025） | https://arxiv.org/abs/2509.19128 | 在途权重更新 |
| R3（Ma et al., 2025） | https://arxiv.org/abs/2510.11370 | MoE 路由回放 |
| Laminar（Sheng et al., 2025） | https://arxiv.org/abs/2510.12633 | 轨迹级异步与中继权重分发 |
| Defeating the Training-Inference Mismatch via FP16（Qi et al., 2025） | https://arxiv.org/abs/2510.26788 | 精度根因与 FP16 |
| StaleFlow（Li et al., 2026） | https://arxiv.org/abs/2601.12784 | 陈旧度与倾斜的联合处理 |
| DORA（Hu et al., 2026） | https://arxiv.org/abs/2604.26256 | 多版本流式 rollout |
| Stale but Stable（Yang et al., 2026） | https://arxiv.org/abs/2607.18722 | 按陈旧度自适应的信赖域 |
| verl-project/verl README | https://github.com/verl-project/verl | verl 自述 |
| OpenRLHF/OpenRLHF README | https://github.com/OpenRLHF/OpenRLHF | OpenRLHF 自述 |
| areal-project/AReaL README | https://github.com/areal-project/AReaL | AReaL 自述 |
| THUDM/slime README | https://github.com/THUDM/slime | slime 自述 |
| alibaba/ROLL README | https://github.com/alibaba/ROLL | ROLL 自述 |
