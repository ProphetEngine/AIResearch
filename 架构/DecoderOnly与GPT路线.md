---
title: Decoder-only / GPT 路线如何成为主流
topic: DecoderOnly与GPT路线
date: 2026-09-22
lines: [架构思想, AI Infra]
status: archived
archived: 2026-09-22
---

# 2：Decoder-only / GPT 路线如何成为主流

> 攻坚线：架构思想（主）+ AI Infra（辅，数据与训练栈）。入口论文为 Brown et al., *Language Models are Few-Shot Learners*（GPT-3, 2020）；产品与后训练节点以 OpenAI GPT-4 官方页与技术报告为准。未核实处统一标「待核实」。

## 一、从 Encoder / Encoder-Decoder / Decoder-only 三分到产品形态收敛

2017 年 Transformer（Vaswani et al.）原始形态是 **Encoder–Decoder**：编码器做双向语境编码，解码器做因果生成，二者由 cross-attention 连接。随后 NLP 预训练大致分出三条可操作的架构路线：

1. **Encoder-only（理解向）**：以 BERT（Devlin et al., 2018）为代表，用 Masked LM 等目标学双向表示，下游靠分类头或 span 抽取做理解类任务。产品形态更接近「嵌入 / 检索 / 判别」而非开放式对话生成。
2. **Encoder–Decoder（条件生成向）**：以 T5、BART 等为代表，把多种任务统一成 text-to-text；翻译、摘要、改写等「输入→输出」任务天然契合。
3. **Decoder-only（自回归生成向）**：以 GPT 系列为代表，去掉编码器与 cross-attention，只保留带因果掩码的解码器栈，用「下一词 / 下一 token 预测」作为统一预训练目标。

**产品形态为何向 Decoder-only 收敛（公开叙事层面）：**

- **交互界面统一**：聊天、指令、工具调用、代码补全都可以写成「前文条件 → 续写」。同一套自回归接口即可覆盖多数用户可见能力，而不必为每个任务换架构。
- **训练目标与推理路径一致**：训练时预测下一个 token，部署时也是逐步采样；少了「预训练目标与下游格式」之间的硬转换成本（相对大量依赖任务头的 BERT 路线）。
- **规模化叙事绑定**：GPT-2/3 公开论证了「扩大模型与数据 → 零样本 / 少样本能力提升」；一旦产品需要开放域生成与指令跟随，Decoder-only + 规模成为更直接的工程赌注。
- **并非「其它路线消失」**：双向上下文理解、检索增强、多模态编码器等仍大量使用 Encoder 或混合结构；本议题谈的是 **通用对话式大模型（LLM as product）** 的主流收敛，而非学术上唯一正确架构。

GPT-3 论文明确写明：其模型与架构与 GPT-2 相同（含修改后的初始化、pre-normalization、可逆 tokenization），并在层间使用交替的 dense 与局部带状 sparse attention（类似 Sparse Transformer）。也就是说，**到 GPT-3 为止，公开材料把「Decoder-only 自回归 Transformer」固化为可扩展配方**；GPT-4 技术报告则只称自己是「Transformer-style、预训练预测文档中的下一个 token」，**不再公开层数、宽度、参数量等架构细节**。

## 二、架构思想：因果 LM、下一词预测统一目标、in-context / few-shot 如何绑定「规模→涌现」；相对 BERT 理解路线的取舍

### 2.1 因果语言模型（Causal / Autoregressive LM）

Decoder-only 的核心归纳偏置是 **因果掩码**：位置 $t$ 只能看见 $\le t$ 的上下文。训练目标是最大化：

$$
\sum_t \log P(x_t \mid x_{<t})
$$

这把「语言理解、知识记忆、格式模仿、简单推理痕迹」都压进同一个续写分布。优点是目标极简、数据几乎无限（自然语言本身就是监督）；代价是 **默认没有未来上下文**，对「必须双向看全句」的判别任务不如 Encoder 直观，往往要靠提示格式或后训练补齐。

### 2.2 「下一词预测」作为统一任务接口

GPT-1（Radford et al., 2018，《Improving Language Understanding by Generative Pre-Training》）确立了两阶段：大规模无监督语言建模预训练 → 各任务有监督微调，且尽量少改架构。
GPT-2（Radford et al., 2019，《Language Models are Unsupervised Multitask Learners》）进一步主张：在足够多样的 WebText 上做下一词预测，模型开始在 **零样本** 条件下表现出阅读理解、翻译、摘要等「多任务」萌芽，无需显式任务监督。
GPT-3 把这一点推到系统评估：**同一模型、不做梯度更新**，仅靠自然语言指令与示范完成下游任务。

统一目标的产品含义是：新能力优先尝试「改提示 / 加示范 / 加后训练数据」，而不是「为新任务设计新网络头」。这降低了应用侧的架构熵，也强化了「一个基础模型服务所有任务」的商业形态。

### 2.3 In-context / few-shot 与「规模→涌现」叙事如何绑在一起

GPT-3 论文把评估场景明确分成：

| 设定 | 是否更新权重 | 上下文内容 |
|------|--------------|------------|
| Fine-tuning | 是 | 大规模任务标注 |
| Few-shot | 否 | 自然语言说明 + 通常约 10–100 条示范（受 $n_{\mathrm{ctx}}=2048$ 限制） |
| One-shot | 否 | 说明 + 1 条示范 |
| Zero-shot | 否 | 仅自然语言说明 |

论文核心假说：**in-context learning（上下文内学习）** 能力会随模型规模显著增强——大模型更能从提示里的示范中「识别任务格式并继续」。文中用符号去除等合成任务展示：更大模型的 in-context learning 曲线更陡；在 42 个准确率类基准的聚合图上，few-shot 相对 zero-shot 的增益也随规模扩大。作者同时提醒：这不等于严格证明「推理时从零学会新任务」，也可能是识别预训练中见过的模式；「meta-learning」一词被用来描述外环（预训练技能）与内环（单次前向中的任务适应）结构。

与「涌现」相关的公开表述需谨慎：GPT-3 论证的是 **平滑的规模定律式提升 + 若干任务上的质变观感**（算术、词序扰乱、新闻真伪难辨等），并引用 Kaplan et al. 的 scaling laws 作为算力–损失背景。GPT-4 技术报告则强调 **可预测扩展（predictable scaling）**：用最多约为 GPT-4 算力 $1/1000$（能力指标）乃至 $1/10000$（损失拟合）的小模型外推最终损失与部分 HumanEval 表现。这是 Infra/方法论叙事，而非公开给出 GPT-4 参数量。

### 2.4 相对 BERT 理解路线的取舍（公开对比维度）

| 维度 | BERT 类 Encoder | GPT 类 Decoder-only |
|------|-----------------|---------------------|
| 预训练目标 | 双向 Masked LM 等 | 因果下一 token |
| 典型强项 | 分类、匹配、抽取、表示学习 | 开放生成、续写、对话、代码 |
| 下游适配 | 常需任务头 / 微调 | 提示、少样本、指令微调、RLHF |
| 标注依赖 | 每任务往往需要相当标注 | GPT-3 主张大幅降低任务标注；后训练仍需偏好/安全数据 |
| 双向上下文 | 天然 | 需靠更长上下文、提示技巧或外部检索补 |

取舍不是「理解无用」：产业里检索、重排序、分类仍广泛用双向编码器。收敛发生在 **通用助手 / API 补全** 赛道——用户要的是可对话的生成接口，Decoder-only 与之一致。GPT-3 也坦承：在 ANLI、部分阅读理解、WiC 等比较两个片段关系的任务上，few-shot 仍弱，说明「统一续写」并未自动解决所有理解难题。

## 三、AI Infra 辅线：大规模预训练的数据规模与训练栈含义

本节只谈数据混合与算力规划层面的公开信息，不涉及可复现训练代码。

### 3.1 GPT-3 公开的数据与训练量（论文 Table 2.1 / 2.2）

- **训练 token 总量**：各尺寸模型均训练 **3000 亿（300B）tokens**。
- **上下文窗口**：$n_{\mathrm{ctx}}=2048$。
- **最大模型**：175B 参数；96 层；$d_{\mathrm{model}}=12288$；96 heads；batch 约 3.2M tokens；学习率 $0.6\times10^{-4}$。论文称其为当时非稀疏语言模型的约 **10×** 于此前最大者。
- **数据混合（按训练采样权重，而非原始体积正比）**：

| 数据集 | Token 量级（论文） | 训练混合权重 | 训 300B tokens 时约过的 epoch |
|--------|-------------------|--------------|-------------------------------|
| Common Crawl（过滤后） | 410B | 60% | 0.44 |
| WebText2 | 19B | 22% | 2.9 |
| Books1 | 12B | 8% | 1.9 |
| Books2 | 55B | 8% | 0.43 |
| Wikipedia | 3B | 3% | 3.4 |

要点：**高质量子集被上采样**（可接受轻微过拟合换质量）；Common Crawl 经与高质量语料相似度过滤、文档级模糊去重；并意识到大规模网页语料的 **评测污染** 风险，论文第 4 节系统做了重叠分析。

### 3.2 训练栈在规划层面的含义（GPT-3 → GPT-4）

- **模型并行与集群**：GPT-3 写明沿深度与宽度切分、在矩阵乘内部与跨层做模型并行，使用 Microsoft 提供的高带宽集群上的 V100；batch 随规模增大、学习率减小，并由梯度噪声尺度等指导（附录）。规划含义是：参数量进入 $10^{11}$ 后，**通信拓扑、并行策略、显存墙** 与算法同等重要。
- **Scaling laws 作为排期工具**：先相信损失随算力近似幂律，再决定「更大模型 / 更多 token」的配比；GPT-3 系列从 125M 到 175B 共 8 档，用于验证下游与损失的共变。
- **GPT-4 的 Infra 叙事重心转移**：技术报告称投入大量工作使优化与基础设施在宽尺度上行为可预测，从而能在正式大训练前登记损失与能力预测；同时 **明确不公开** 架构细节、硬件、训练算力、数据构造与训练方法。数据侧仅概括为：公开可用数据（如互联网）+ 第三方授权数据；其后用 RLHF 做后训练对齐。
- **后训练成为产品栈一环**：从 InstructGPT（Ouyang et al., 2022，《Training language models to follow instructions with human feedback》）到 GPT-4，公开叙事是 SFT / 偏好数据 + RLHF（及 GPT-4 所述的 rule-based reward models 等安全管线）。对 Infra 的含义是：预训练集群之外，还需 **人类反馈数据飞轮、奖励模型训练、拒绝/安全策略迭代**——算力与数据预算要为对齐预留，而非「只堆预训练 FLOPs」。

### 3.3 规划时可带走的检查清单（非操作手册）

1. 数据：来源比例、质量过滤、去重、评测污染扫描、多语言占比（GPT-3 称按词计英语约占 93%，其它语言约 7%）。
2. 算力：目标损失/能力 → 反推参数–token–batch；小规模预测再放大（GPT-4 强调）。
3. 并行与稳定性：能否在目标规模上稳定跑完预定 token，而不是只在小模型上调通。
4. 后训练与安全：偏好数据、红队、部署监控与快速迭代通道（GPT-4 System Card / 官方页叙述）。

## 四、关键节点：GPT-1/2/3/4 公开叙述中的转折

以下时间与主张以官方博文 / 论文为准；参数等数字凡来自二手综述且未在本次直接打开官方 PDF 核对者，标「待核实」。

| 节点 | 公开入口 | 转折要点 |
|------|----------|----------|
| **GPT-1（2018）** | Radford et al., *Improving Language Understanding by Generative Pre-Training*；OpenAI: [Improving language understanding with unsupervised learning](https://openai.com/index/language-unsupervised/) | **Decoder-only + 生成式预训练 + 任务微调** 打通：一套 Transformer 解码器栈，先 LM 再微调，少改架构即可迁移到多种理解任务。相对「每任务定制网络」是范式收缩的第一步。具体层数/参数量：常见二手来源称约 12 层、约 1.17 亿参数——**待核实（需对照官方 PDF）**。 |
| **GPT-2（2019）** | Radford et al., *Language Models are Unsupervised Multitask Learners*；OpenAI: [Better language models](https://openai.com/index/better-language-models/) | 目标叙事从「预训练+微调」转向 **零样本多任务**：WebText 上的下一词预测涌现初步的问答/翻译/摘要等能力；最大公开型号 **1.5B** 参数；强调容量对零样本迁移关键。发布策略上曾分阶段放模型（安全顾虑）——属产品/治理转折，亦强化「LM 已强到需管控」的社会叙事。 |
| **GPT-3（2020）** | Brown et al., [arXiv:2005.14165](https://arxiv.org/abs/2005.14165) | **Few-shot / in-context learning** 成为主角：175B、300B tokens；系统比较 0/1/few-shot；在多项任务上逼近或超过当时部分微调 SOTA（如 TriviaQA closed-book few-shot 等，细节见论文表）。架构上公开仍跟 GPT-2 配方并加 sparse attention。污染与偏见、社会影响专章进入「必写」。 |
| **InstructGPT / 对齐转折（2022）** | Ouyang et al., *Training language models to follow instructions with human feedback*（[arXiv:2203.02155](https://arxiv.org/abs/2203.02155)） | 公开叙事：仅靠变大不足以让模型「按用户意图行事」；**SFT + RLHF** 提升真实用户提示上的偏好胜率。ChatGPT（官方称基于 GPT-3.5 系）把对齐后的 Decoder-only 推成消费级产品——**「架构收敛」之后是「目标函数/后训练收敛」**。GPT-3.5 与 ChatGPT 的精确底座参数：**待核实**（需对照当时 OpenAI 说明，非 GPT-4 报告核心披露）。 |
| **GPT-4（2023-03）** | 官方页 [GPT-4](https://openai.com/index/gpt-4-research/)；[GPT-4 Technical Report](https://arxiv.org/abs/2303.08774) / [cdn PDF](https://cdn.openai.com/https://arxiv.org/abs/2303.08774) | 仍宣称 **Transformer-style、下一 token 预训练**；新增 **图文多模态输入、文本输出**；强调专业/学术考试表现（如模拟律师资格考试约前 10% 百分位，对比叙述中 GPT-3.5 约后 10%）；**RLHF 后训练**；**可预测扩展** Infra；**故意不公开** 模型尺寸、硬件、算力、数据与训练细节。产品形态上，通用助手 + API 成为默认，Decoder-only（外加视觉前端）成为产业默认假设。 |

**收敛一句话**：架构上从「三种 Transformer 用法并存」收束到「因果 Decoder 做通用接口」；目标上从「为每个基准微调」收束到「预训练续写 + 提示/少样本 + 指令与偏好对齐」；披露上从 GPT-3 的相对透明缩放表，收到 GPT-4 的能力与安全报告。

## 五、常见误区

1. **「Decoder-only 全面取代 BERT」**
 误。双向编码器在检索、分类、重排、领域 NLU 流水线中仍极常见。收敛的是 **通用生成式助手** 赛道，不是全部 NLP。

2. **「Few-shot = 推理时梯度学习」**
 误。GPT-3 定义的 few-shot **不更新权重**，只是把示范拼进上下文做条件生成。是否「真正学习」仍是论文自己标出的开放问题。

3. **「涌现 = 不可预测的魔法」**
 过度解读。GPT-3 多任务随规模大致变好；GPT-4 反而强调 **用小规模实验预测大训练结果**。部分能力曲线可能陡峭，但不等于无法做工程外推。

4. **「GPT-4 已公开与 GPT-3 同级的架构表」**
 误。技术报告写明因竞争与安全考虑，**无架构（含模型大小）、硬件、训练算力、数据构造、训练方法等细节**。外传参数量均应标 **待核实**，不能当事实写入决策材料。

5. **「下一词预测只学表面统计，对推理无贡献」或反之「只靠续写就等于可靠推理」**
 两端都过绝对。公开评测显示规模与后训练能提升考试与部分推理基准，但也明确保留幻觉、校准变差（GPT-4 称后训练后校准不如基座）、知识截止等限制。

6. **「数据越多越好、均匀混合即可」**
 与 GPT-3 做法不符。论文对 Common Crawl **过滤 + 去重**，并对高质量子集 **上采样**；同时警示污染。质量与配比是一等公民，而非只看原始 TB 数。

7. **「对齐只是套壳，与 Decoder-only 路线无关」**
 不完整。产品能成为主流，公开叙事里 **Instruct/RLHF** 与规模同等关键：同样是因果 LM，未对齐模型更难稳定遵循用户意图与安全策略。

## 六、引用

### 论文与官方页（完整 URL）

1. Brown et al. (2020). *Language Models are Few-Shot Learners*. https://arxiv.org/abs/2005.14165 ；PDF: https://arxiv.org/pdf/2005.14165
2. OpenAI (2023). GPT-4 官方介绍页. https://openai.com/index/gpt-4-research/
3. OpenAI (2023). *GPT-4 Technical Report*. https://arxiv.org/abs/2303.08774 ；官方 CDN PDF: https://cdn.openai.com/https://arxiv.org/abs/2303.08774
4. Radford et al. (2018). *Improving Language Understanding by Generative Pre-Training*. https://openai.com/index/language-unsupervised/ ；PDF: https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
5. Radford et al. (2019). *Language Models are Unsupervised Multitask Learners*. https://openai.com/index/better-language-models/ ；PDF: https://d4mucfpksywv.cloudfront.net/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
6. Ouyang et al. (2022). *Training language models to follow instructions with human feedback*. https://arxiv.org/abs/2203.02155
7. Devlin et al. (2018). *BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding*. https://arxiv.org/abs/1810.04805 （对照理解路线）
8. Vaswani et al. (2017). *Attention Is All You Need*. https://arxiv.org/abs/1706.03762 （原始 Encoder–Decoder Transformer）
9. Kaplan et al. (2020). *Scaling Laws for Neural Language Models*. https://arxiv.org/abs/2001.08361 （GPT-3 引用的规模定律背景）

### 官方 PDF（相对本仓库 ）

- GPT-3：`https://arxiv.org/abs/2005.14165`（自 https://arxiv.org/pdf/2005.14165 下载）
- GPT-4 技术报告：`https://arxiv.org/abs/2303.08774`（自 https://cdn.openai.com/https://arxiv.org/abs/2303.08774 下载；与 arXiv:2303.08774 对应）

### 撰写说明

- GPT-3 要点主要依据 arXiv 摘要页全文抓取与论文表格数字；GPT-4 要点依据 arXiv:2303.08774 正文抓取与官方页元信息/检索摘要。
- WebFetch 访问 `openai.com/index/gpt-4-research/` 曾返回 403，已用 curl 拉取页面并与 arXiv / CDN PDF 交叉核对。
- 凡二手博客给出但未在本次打开的 PDF 中逐字核对的型号细节（如 GPT-1 精确参数量、GPT-3.5 具体参数），正文已标「待核实」。

## 相关笔记

- [[注意力与Transformer核心思想|Attention / Transformer]]
- [[DecoderOnly与GPT路线|Decoder-only / GPT]]
- [[规模定律与预训练范式|规模定律与预训练]]
- [[混合专家架构|MoE / 稀疏激活]]
- [[对齐脉络RLHF与偏好优化|对齐 RLHF / DPO]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿模型谱系]]

