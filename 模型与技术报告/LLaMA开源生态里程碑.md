---
date: 2026-09-22
status: archived
archived: 2026-09-22
topic: LLaMA开源生态里程碑
title: "开源生态里程碑：LLaMA 系如何改变复现与竞赛格局"
lines: [架构思想]
sources:
  - https://arxiv.org/abs/2302.13971
  - https://ai.meta.com/blog/llama-4-multimodal-intelligence/
  - https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md
  - https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE
  - https://www.llama.com/models/llama-4/
  - https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama4
  - https://ai.meta.com/blog/llama-2/
  - https://ai.meta.com/blog/meta-llama-3/
  - https://ai.meta.com/blog/meta-llama-3-1/
  - https://arxiv.org/abs/2601.11659
related: ["开源与闭源前沿模型谱系", "DecoderOnly与GPT路线", "注意力与Transformer核心思想", "规模定律与预训练范式", "长上下文位置编码与系统侧", "注意力效率族MQA到MLA", "混合专家架构", "多模态架构脉络", "对齐脉络RLHF与偏好优化", "推理时扩展TestTimeScaling", "AI基础设施总览"]
---

# 开源生态里程碑：LLaMA 系如何改变复现与竞赛格局

> **主要来源**：[LLaMA: Open and Efficient Foundation Language Models](https://arxiv.org/abs/2302.13971)（Touvron 等，2023-02）；[The Llama 4 herd: The beginning of a new era of natively multimodal AI innovation](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)（Meta AI 博文，2025-04-05）；[Llama 4 Model Card](https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md)（meta-llama/llama-models）（截至 2026-01-15）。Llama 2、Llama 3、Llama 3.1 的发布日据各自官方博文。
> **研究线**：架构思想（推理预算优先的训练哲学、开源族系的默认架构积木、从 dense 到 MoE 与原生多模态）
> **范围与相邻笔记**：
> - ≠ [[开源与闭源前沿模型谱系]]：本篇是那篇开源一支的专题，只写 LLaMA 系，不写其他开源族系。
> - 本篇不转述各代 Community License 的条款；第六节把可核对事实与叙事推断分开写。
>
> **意义**：LLaMA（2023）用公开数据、更长训练和已验证的架构积木，把可下载的基座推到能与闭源大模型对照的位置，复现、微调、评测、蒸馏由此在同一套权重上展开；此后 Llama 2 到 Llama 4 把开放权重推进到商用许可、405B 规模、MoE 与原生多模态。Llama 4 也标出了这条路线的文档边界：只有博文与 Markdown 模型卡，没有前几代那样的论文式技术报告。

---

## 一、问题背景

在 LLaMA 之前，许多最强基座要么只开放 API，要么权重申请门槛高、数据配方不透明。社区能做的往往是：

- **黑盒评测**：只能测输出，难做消融、难复现训练曲线；
- **蒸馏代理**：用闭源 API 生成数据再训小模型，受成本与服务条款双重约束；
- **架构猜测**：靠逆向叙事，或「公开但不够强」的权重（如早期 OPT、BLOOM）间接摸索。

LLaMA 论文的核心主张不是「再堆一个更大的模型」，而是在公开可用数据上用更多 token 训练，得到在给定推理预算下更优的模型，并把权重交给研究社区（Abstract、§1、§8）。

## 二、脉络

| 时间 | 节点 | 转折 | 出处 |
| --- | --- | --- | --- |
| 2023-02 | LLaMA | 7B–65B，只用公开数据；13B 在多数评测上超过 GPT-3（175B），向研究社区释放权重 | [arXiv:2302.13971](https://arxiv.org/abs/2302.13971) |
| 2023-07-18 | Llama 2 | 官方称研究与商业可用，提供预训练与对话微调权重及起始代码 | [Meta 博文](https://ai.meta.com/blog/llama-2/) |
| 2024-04-18 | Llama 3 | 首批 8B / 70B 预训练与指令微调模型，官方称是同类中最强的公开可用模型之一 | [Meta 博文](https://ai.meta.com/blog/meta-llama-3/) |
| 2024-07-23 | Llama 3.1 | 发布 405B 等；官方称允许开发者用 Llama 输出（含 405B）改进其他模型 | [Meta 博文](https://ai.meta.com/blog/meta-llama-3-1/) |
| 2025-04-05 | Llama 4 Scout / Maverick | 首次在 Llama 中采用 MoE，原生多模态（early fusion）；Behemoth 作为教师预告，未开放权重；只以博文和 Markdown 模型卡发布 | 第五节 |
| 2026-01 | 第三方「Llama 4 Herd」汇编稿被撤 | arXiv:2601.11659 自称汇总 Llama 4 技术细节，arXiv 管理员以作者署名不实为由移除 | [arXiv:2601.11659](https://arxiv.org/abs/2601.11659) |

## 三、核心思想：可下载权重改变了什么

### 3.1 四个环节

| 环节 | 闭源 / 仅 API 时 | 有可下载（或可申请）权重后 |
| --- | --- | --- |
| 复现 | 难复现训练与中间检查点，只能复现提示词工程 | 可对照架构细节、做消融、复现或质疑评测协议 |
| 微调 | 只能做 prompt 或外部适配器 | SFT、LoRA / QLoRA、RLHF / DPO 全栈可落地，领域模型大量出现 |
| 评测 | 排行榜依赖厂商自报或 API 采样差异 | 同一权重上可复跑，竞技场与开源榜成为对照系 |
| 蒸馏 | 从闭源 API 蒸馏，受服务条款与价格约束 | 从强开源教师蒸馏：Llama 3.1 起官方明确允许用输出改进其他模型；Llama 4 官方公开 Behemoth → Scout / Maverick 的 codistillation |

### 3.2 架构思想上的三层信号

1. **推理预算优先**：同样达标的性能，偏好「更小但训更久」的模型（论文 §1 对 Chinchilla 训练目标的修正）。
2. **可传播的架构积木**：Pre-norm + RMSNorm、SwiGLU、RoPE，成为后续开源族系的默认起点。
3. **开放权重 → 开放竞赛**：社区在同一族系上竞争微调、量化、推理引擎与蒸馏。闭源一侧因此加速迭代属于叙事推断，见第六节。

## 四、LLaMA（2023）的公开主张与架构要点

### 4.1 公开主张（论文原文）

- **模型族**：约 7B–65B 的基座模型（Abstract；Table 2 给出 6.7B / 13.0B / 32.5B / 65.2B）。
- **数据立场**：只用公开可得、与开源兼容的数据，称无需专有语料即可达到 SOTA 级竞争力（Abstract、§2.1）。
- **关键结果**：LLaMA-13B 在多数评测上超过 GPT-3（175B）；LLaMA-65B 与 Chinchilla-70B、PaLM-540B 可比（Abstract）。
- **发布意图**：向研究社区释放全部模型（脚注指向 facebookresearch/llama 仓库）。这是 2023 年初论文语境下的「研究社区发布」，不等于后来 Llama 2 / 3 / 4 的商业许可。

### 4.2 训练哲学：从算力最优转向推理最优

论文 §1 的论证链：

1. Kaplan、Chinchilla 等缩放律针对给定训练算力下的最优模型—数据配比。
2. 部署时推理预算往往更关键：达到同等性能，更小、训更久的模型服务成本更低。
3. 观察：7B 在 1T tokens 之后性能仍在提升。
4. 因此在各规模上都用更多 token 训练，优化不同推理预算下的最佳性能。

这是整篇论文的架构思想入口：不是发明新的注意力变体，而是用公开数据、更长训练和已验证的积木，把可部署的开源基座推到能与闭源大模型对照的位置。

### 4.3 数据混合（论文 Table 1）

分词后总量约 1.4T tokens，1.4T 设定下各子集的采样比例：

| 子集 | 采样比例 | 要点 |
| --- | --- | --- |
| English CommonCrawl | 67% | CCNet 管线；去重、语种、质量过滤 |
| C4 | 15% | 增加 CommonCrawl 预处理的多样性 |
| Github | 4.5% | 只保留 Apache / BSD / MIT 等许可的项目 |
| Wikipedia | 4.5% | 20 种拉丁或西里尔文字语言 |
| Books（Gutenberg + Books3） | 4.5% | 书籍级去重 |
| ArXiv | 2.5% | LaTeX 清洗 |
| StackExchange | 2.0% | 高质量问答 |

7B / 13B 训 1.0T tokens，33B / 65B 训 1.4T（§2.2、Figure 1）。分词器为 SentencePiece BPE，数字拆成单个 digit，未知 UTF-8 回退到 byte（§2.1）。

### 4.4 架构积木（论文 §2.2）

1. **Pre-normalization**（受 GPT-3 启发）：在子层输入处归一化，用 RMSNorm。
2. **SwiGLU**（受 PaLM 启发）：替换 ReLU，FFN 隐层维度取 $\frac{2}{3}4d$（PaLM 为 $4d$）。
3. **RoPE**（受 GPT-Neo 启发）：去掉绝对位置编码，在每层加入旋转位置编码。

Table 2 超参（勿与 Llama 2 / 3 / 4 混淆）：

| params | dim | n_heads | n_layers | lr | batch | n_tokens |
| --- | --- | --- | --- | --- | --- | --- |
| 6.7B | 4096 | 32 | 32 | 3.0e-4 | 4M | 1.0T |
| 13.0B | 5120 | 40 | 40 | 3.0e-4 | 4M | 1.0T |
| 32.5B | 6656 | 52 | 60 | 1.5e-4 | 4M | 1.4T |
| 65.2B | 8192 | 64 | 80 | 1.5e-4 | 4M | 1.4T |

优化器 AdamW，$\beta_1=0.9,\beta_2=0.95$；cosine 学习率，终值为最大值的 10%；weight decay 0.1；梯度裁剪 1.0；warmup 2000 步（§2.3）。

### 4.5 效率、碳排与指令微调

- 65B 在约 2048 张 A100-80GB 上约 380 tokens/sec/GPU，1.4T tokens 约 21 天（§2.4）。
- §6 给出同数据中心假设下的碳排对照（与 OPT、BLOOM 可比口径），并强调释放权重可免去他人重复训练的成本。
- 常识推理、闭卷问答、RACE、MATH / GSM8k、HumanEval / MBPP、MMLU 等结果见 §3 各表。
- §4 用 Flan 类协议做简短指令微调得到 LLaMA-I（65B），MMLU 5-shot 68.9%（Table 10），显示「开源基座 + 少量指令数据」即可快速抬升实用能力。

## 五、Llama 4（2025-04-05）

### 5.1 官方材料

| 类型 | 链接 | 形态 |
| --- | --- | --- |
| 发布博文 | [The Llama 4 herd](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) | HTML，2025-04-05 |
| 模型卡 | [MODEL_CARD](https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md)（meta-llama/llama-models） | Markdown，不是 PDF |
| 文档卡页 | [Llama 4 model card & prompt formats](https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama4) | HTML |
| 产品页 | [llama.com Llama 4](https://www.llama.com/models/llama-4/) | HTML |
| 许可 | [Llama 4 Community License](https://github.com/meta-llama/llama-models/blob/main/models/llama4/LICENSE) | 名称见模型卡，条款不转述 |

Meta 为 Llama、Llama 2 和 Llama 3（*The Llama 3 Herd of Models*）都发表过论文式文稿；Llama 4 没有这样的技术报告，也没有独立的 PDF 模型卡。arXiv:2601.11659（*The Llama 4 Herd: Architecture, Training, Evaluation, and Deployment Notes*，2026-01-15 提交）是第三方汇编，已被 arXiv 管理员以作者署名不实为由移除，Zenodo、HF Papers 上的同名汇编稿同样不是 Meta 材料。

### 5.2 型号一览

| 型号 | 激活 / 总参数 | Experts | 上下文 | 预训练 tokens | 其他 |
| --- | --- | --- | --- | --- | --- |
| Scout | 17B / 109B | 16 | 10M | 约 40T | BF16 权重，可经 int4 即时量化装进单张 H100（模型卡）；知识截止 2024-08 |
| Maverick | 17B / 400B | 128 | 1M | 约 22T | 提供 BF16 与 FP8 权重，FP8 可装进单台 H100 DGX 主机（模型卡）；知识截止 2024-08 |
| Behemoth | 288B 激活 / 近 2T | 16 | — | — | 博文称仍在训练、未开放权重，作为教师；STEM 上称优于 GPT-4.5、Claude Sonnet 3.7、Gemini 2.0 Pro 等（厂商自报） |

### 5.3 模型卡要点

- **架构**：自回归语言模型，MoE，以 early fusion 实现原生多模态；输入多语文本与图像，输出多语文本与代码。
- **训练数据**：公开可得数据、授权数据，以及 Meta 产品与服务中的信息（含 Instagram、Facebook 公开帖子与用户和 Meta AI 的交互）；数据截止 2024-08。
- **语言**：支持阿拉伯语、英语、法语、德语、印地语、印尼语、意大利语、葡萄牙语、西班牙语、他加禄语、泰语、越南语 12 种；预训练覆盖 200 种语言。
- **图像**：图像理解测试到最多 5 张输入图。
- **能耗与碳排**：预训练累计 7.38M H100-80GB GPU 小时（Scout 5.0M、Maverick 2.38M）；location-based 排放合计 1,999 吨 CO2eq（Scout 1,354、Maverick 645），market-based 为 0。

### 5.4 公开的架构与训练要点（据博文）

1. **MoE**：每个 token 只激活部分参数，固定训练 FLOPs 下比 dense 更高效。
2. **Maverick 路由**：dense 层与 MoE 层交替；MoE 层含 128 个 routed experts 与 1 个 shared expert，每个 token 进入 shared expert 及其中一个 routed expert。
3. **原生多模态 / early fusion**：文本与视觉 token 进入统一骨干，可用大量未标注的文本、图像、视频联合预训练。
4. **视觉编码器**：基于 MetaCLIP，与冻结的 Llama 分开联合训练，以适配 LLM。
5. **MetaP**：用于可靠设定分层学习率、初始化等超参，称可跨 batch、宽度、深度与 token 量迁移。
6. **多语言**：预训练覆盖 200 种语言，其中 100 多种各超过 10 亿 tokens；多语 token 量约为 Llama 3 的 10 倍。
7. **数据规模**：预训练混合超过 30T tokens（含文本、图像、视频），是 Llama 3 的两倍以上。
8. **Mid-training**：含长上下文扩展等配方，支撑 Scout 的 10M 上下文。
9. **后训练**（Maverick）：轻量 SFT → online RL → 轻量 DPO；用 Llama 模型作评判，去掉 50% 以上被标为「简单」的数据，以免过度约束 RL 的探索。
10. **Codistillation**：从 Behemoth 向学生蒸馏，博文称设计了动态加权 soft / hard target 的蒸馏损失，并在预训练阶段摊销教师前向的成本。

Llama 4 把 LLaMA 开启的路径推到「开放权重 + MoE + 原生多模态 + 官方教师蒸馏」；竞争也从「能否超过 GPT-3」变成「开源 MoE 多模态能否在成本—性能前沿持续咬住闭源」，后者仍在进行中。

## 六、生态反馈：社区如何反过来影响闭源节奏

本节区分【事实】与【推断】；推断用于理解竞争格局，不作因果认定。

### 6.1 【事实】可观察到的连锁

1. **可复现基座出现**：LLaMA 权重进入研究社区后，公开的架构积木与可下载检查点成为默认参照。
2. **指令微调普及**：论文自身已展示短指令微调抬升 MMLU；随后社区大量基于 LLaMA 族做 SFT / RLHF（具体项目与时间线此处不逐一考证）。
3. **推理与量化栈**：围绕同一族系的量化、推理引擎与 serving 方案快速迭代，「单卡或少卡可跑」成为日常。
4. **官方路线升级**：从研究社区发布，到 Llama 2 的商业可用，再到 Llama 3 / 3.1 / 4 持续扩大开放权重并转向多模态与 MoE，这是 Meta 各代官方博文的连续动作。
5. **蒸馏的许可信号**：Llama 3.1 官方允许用输出改进其他模型；Llama 4 官方公开 Behemoth 教师 → Scout / Maverick 学生的蒸馏。

### 6.2 【推断】影响闭源节奏的机制假说（常见产业叙事，非论文结论）

- **替代弹性**：开源权重在「够用」任务上接近闭源 API 时，采购与学术复现会分流，闭源需以更高能力、更低价格或更强产品闭环回应。
- **评测公开化**：同一套开源权重上的排行榜与竞技场，使暗箱刷分更难单独说服社区。
- **人才与标准外溢**：架构积木、训练配方叙事与安全工具（如后来的 Llama Guard）成为行业共同语言。

**限度**：开放权重不等于全面追上闭源；数据配方、算力、产品分发、安全护栏仍高度不对称。论文自己也报告了毒性与偏见问题（§5），并强调评测不足。

## 七、常见误区

1. **把 LLaMA（2023）的研究社区发布写成完全开源、商用自由**：以当时的申请流程与后续各代 Community License 原文为准，代际条款不同。
2. **把 Table 2 的 33B 写成 34B，或与 Llama 2 的 7 / 13 / 70B 混用**：Table 2 为 32.5B（正文常称 33B）。
3. **以为 LLaMA 只用 CommonCrawl**：CommonCrawl 占 67%，另有 C4、代码、维基、书、ArXiv、StackExchange。
4. **把 Llama 4 Behemoth 当成已开放下载**：2025-04-05 博文明确仍在训练、未释放，开放的是 Scout 与 Maverick。
5. **把 Scout 写成 109B dense**：官方是 17B 激活、109B 总参的 MoE（16 experts）。
6. **把 Llama 4 的第三方汇编稿当作技术报告**：arXiv:2601.11659 已被移除，Meta 未发布 Llama 4 技术报告。
7. **把厂商博文的基准对比当成第三方复现结论**：一律标为官方自报。
8. **忽略公开数据的版权与隐私争议**：论文强调公开可得与开源兼容的过滤（如按许可筛 GitHub），不等于法律风险归零。

## 八、意义

- **把「可下载权重」变成研究基础设施**：复现、微调、评测、蒸馏第一次能在同一套强基座上进行，开源社区的工作从猜测闭源模型转向直接改进权重。
- **确立推理预算优先的训练哲学与默认积木**：「小而训久」与 Pre-norm + RMSNorm、SwiGLU、RoPE 成为后续开源族系的起点。
- **标出开放权重的文档边界**：从 LLaMA 的论文、Llama 3 的 Herd 论文，到 Llama 4 只有博文与 Markdown 模型卡，开放权重不等于开放配方。

## 九、局限与待核实

- **早期博文未逐条核对**：第二节 Llama 2、Llama 3、Llama 3.1 三行的发布日与许可表述，未与三篇官方博文逐条对照。
- **许可条款**：Llama 2 / 3 / 4 Community License 的月活门槛、专利、商标、蒸馏条款差异，本篇不转述，以 LICENSE 与可接受使用政策原文为准。
- **厂商自报**：Llama 4 博文中对外部模型的基准对比，未见独立第三方复现。
- **Behemoth**：是否最终开放权重、最终规格是否与 2025-04-05 的预告一致，未核实。
- **数据争议**：Books3 等子集后来的版权争议属法律层面，本篇不展开。
- **撤稿日期**：arXiv:2601.11659 只能确认 2026-01-15 提交、现已移除，移除日期未见。

## 十、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
| --- | --- | --- |
| [[开源与闭源前沿模型谱系]] | 本篇是那篇开源一支的专题，LLaMA 系在那篇的谱系里定位 | 其他开源族系与闭源前沿 |
| [[DecoderOnly与GPT路线]] | LLaMA 沿用 decoder-only 路线，本篇只写它在开源一侧的变体与积木 | decoder-only 的起源与 GPT 系 |
| [[注意力与Transformer核心思想]] | LLaMA 的 Pre-norm、SwiGLU、RoPE 都是对原始 Transformer 的修改，原始结构在那篇 | 注意力机制本身 |
| [[规模定律与预训练范式]] | 4.2 节「推理最优」是对 Kaplan、Chinchilla 缩放律的修正，缩放律本身在那篇 | 缩放律推导与后续范式 |
| [[长上下文位置编码与系统侧]] | LLaMA 采用 RoPE，Scout 做到 10M 上下文；位置编码与长上下文扩展方法在那篇 | RoPE 外推与系统侧实现 |
| [[注意力效率族MQA到MLA]] | LLaMA（2023）用标准多头注意力；之后 KV 压缩的演进在那篇 | MQA、GQA、MLA |
| [[混合专家架构]] | Llama 4 是 Llama 系第一次采用 MoE，shared + routed expert 的设计背景在那篇 | MoE 通史与路由 |
| [[多模态架构脉络]] | Llama 4 的 early fusion 原生多模态，在那篇的多模态架构演进中定位 | 多模态架构各路线 |
| [[对齐脉络RLHF与偏好优化]] | LLaMA-I 的指令微调与 Llama 4 的 SFT → online RL → DPO 管线，属于那篇的对齐方法线 | RLHF 与偏好优化方法 |
| [[推理时扩展TestTimeScaling]] | 同样以推理成本为中心：LLaMA 用更长训练换更低推理成本，那篇讨论在推理时多花算力换能力，两者方向相反 | 测试时扩展方法 |
| [[AI基础设施总览]] | 65B 用约 2048 张 A100 训练 21 天，开源权重带动量化与推理引擎迭代；训练与 serving 基础设施在那篇 | 并行、分页注意力、量化 |

## 十一、延伸阅读

| # | 来源 | 读什么 |
| --- | --- | --- |
| 1 | [LLaMA](https://arxiv.org/abs/2302.13971) Abstract、§1、§2.2、Table 1–2 | 训练哲学、三块积木、数据与超参 |
| 2 | 同上 §3 Table 3、8、9 | 「13B 对 GPT-3、65B 对 PaLM」的量级 |
| 3 | [The Llama 4 herd](https://ai.meta.com/blog/llama-4-multimodal-intelligence/) | Pre-training、Post-training 与 Behemoth 蒸馏段 |
| 4 | [Llama 4 MODEL_CARD](https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md) | 型号表、语言、能耗与碳排 |
| 5 | [Llama 2](https://ai.meta.com/blog/llama-2/)；[Llama 3](https://ai.meta.com/blog/meta-llama-3/)；[Llama 3.1](https://ai.meta.com/blog/meta-llama-3-1/) 官方博文 | 各代的发布形态与许可表述 |
