---
title: "数据策展流水线增量：Nemotron-CC"
topic: NemotronCC数据策展
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2412.02595
 - https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html
arxiv: ["2412.02595"]
related: ["分词器与数据配比", "合成数据与教科书式数据", "合成对齐数据Magpie", "BeyondWeb合成预训练", "Inspect评测Harness", "评测数据污染检测与可靠性", "Nemotron3Ultra技术报告深读"]
project:
 - https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html
 - https://github.com/NVIDIA-NeMo/Curator
 - https://huggingface.co/nvidia/nemocurator-fineweb-nemotron-4-edu-classifier
 - https://huggingface.co/nvidia/nemocurator-fineweb-mixtral-edu-classifier
archived: 2026-09-22
---

# 数据策展流水线增量：Nemotron-CC

> **主要来源**：[Nemotron-CC: Transforming Common Crawl into a Refined Long-Horizon Pretraining Dataset](https://arxiv.org/abs/2412.02595)（NVIDIA，v2，2025-05-30；首次提交 2024-12-03；ACL 2025）；[Nemotron-CC 数据集页](https://data.commoncrawl.org/contrib/Nemotron/Nemotron-CC/index.html)（报告所附数据集地址，不引页面事实，不计入截至）（截至 2025-05-30）
> **研究线**：架构思想（主：分类器集成、只对低质数据用启发式过滤、按质量分档的合成改写）；评测字段（辅：8B 模型在 1T 与 15T token 两种训练长度上的对照）
> **范围与相邻笔记**：
> - ≠ [[分词器与数据配比]]：FineWeb、DCLM、Dolma 等网页策展的通史在那篇，本篇只记 Nemotron-CC 的增量。
> - ≠ [[合成数据与教科书式数据]]：从知识造新教材的合成预训练在那篇，本篇的合成是对已有网页做改写与结构变换。
> - ≠ [[合成对齐数据Magpie]]：对齐阶段的指令与偏好合成在那篇，本篇是预训练语料。
>
> **意义**：Nemotron-CC 针对一个矛盾：模型过滤能抬高短训练长度上的分数，但砍掉的数据太多，撑不起 15T 量级的长程训练。报告用三个分类器的集成提高高质量数据的召回、对高质量文档关闭启发式过滤、再用合成改写补充新的唯一 token，得到 6.3T token 的英文 Common Crawl 语料，其中 4.4T 为全局去重后的真实 token、1.9T 为合成 token（摘要）。在 1T token 的训练长度上，其中的高质量子集比 DCLM 的 MMLU 高 5.6；在 15T token 的训练长度上，含 7.2T 本数据集 token 的 8B 模型比 Llama 3.1 8B 的 MMLU 高 5、ARC-Challenge 高 3.1、十项任务平均高 0.5（摘要）。报告的指导原则是从静态、非学习的启发式管线，转向随模型变好而自然变好的学习式飞轮（§1）。

## 一、问题背景

近年的英文 Common Crawl 数据集，如 FineWeb-Edu 与 DCLM，用模型过滤大幅抬高基准分数，但删掉了大量数据（§1）。长程训练需要的 token 远多于此：Llama 3.1 训练了 15T token，Gemma 2 27B 训练了 13T token。DCLM 与 FineWeb-Edu 约含 80% 的近重复，唯一 token 分别为 1T 与 0.2T；在这样的数据上训多万亿 token，等于反复看同一批样本，而 Muennighoff 等发现，超过四个 epoch 后，重复 token 的收益相对更多唯一 token 递减（§1）。报告要在基准精度与数据量（按唯一真实 token 计）之间取得更好的折中。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2023-05 | [Scaling Data-Constrained Language Models](https://arxiv.org/abs/2305.16264) | 重复数据收益递减，报告据此强调唯一 token |
| 2024-06 | [DataComp-LM](https://arxiv.org/abs/2406.11794) | DCLM 分类器过滤，报告的主要对照与集成成员之一 |
| 2024-06 | [The FineWeb Datasets](https://arxiv.org/abs/2406.17557) | FineWeb-Edu 教育价值分类器，报告用于分析与标注流程参照 |
| 2024-12 | [Nemotron-CC](https://arxiv.org/abs/2412.02595) | 分类器集成、高质量数据关闭启发式、合成改写，6.3T token |

## 三、核心机制：提取、去重与启发式（§2.1）

1. **提取器**：在 13 个快照上比较 Justext 与 Trafilatura，两者质量相当，Justext 产出更多 token，按 FineWeb-Edu 分类器的标准（3、4、5 分），高质量 token 多 28.6%（Table 1）。
2. **语言与去重**：用 pycld2 与 FastText lid176 做英文过滤，阈值 0.3；再做全局模糊去重，并在每八分之一的快照内做精确子串去重（v2 措辞）。
3. **启发式**：复用 Parmar 等的启发式与困惑度过滤，报告发现它会去掉 18.1% 被 FineWeb-Edu 分类器判为高质量的 token（Table 1）。因此只对低质文档使用启发式过滤，高质量文档不过滤。8B 模型训练 1T token 的消融里，这样做的 MMLU 为 57.5，高于全部不过滤的 55.5 与 Justext 全部过滤的 54.1（Table 7）。

## 四、核心机制：分类器集成与质量分档（§2.2）

1. **三个分类器**：两个用与 FineWeb-Edu-Annotation 相同的 460K 文档，分别让 Mistral 8x22B-instruct 与 Nemotron-340B-instruct 按教育价值打分，再训练分类器；第三个是 DCLM 的公开分类器。最终集成没有用 FineWeb-Edu 的官方分类器。
2. **为什么集成**：单个分类器对高质量 token 的召回约 10%（Table 9，v2 措辞；v1 写作不到 10%）。集成把高质量 token 的占比从 9% 提到 25%，平均任务分为 59.4，在各分类器中最高（Table 9）。
3. **分桶与分档**：三个分类器的分数各取整到 0–19 共 20 个桶，文档取三个桶号中的最大值。再用退火标定下游质量：在已训练 70% 的 8B 模型上续训 50B token，默认数据占 66%、待测桶占 34%，按 9 项任务的平均把 20 个桶并成 5 档（Table 2）：

| 质量档 | 桶 | token（B） | 占比（%） |
|---|---|---|---|
| High | 19 | 553 | 12.63 |
| Medium-High | 18 | 504 | 11.52 |
| Medium | 12–17 | 2,023 | 46.24 |
| Medium-Low | 7–11 | 894 | 20.43 |
| Low | 0–6 | 402 | 9.18 |

## 五、核心机制：合成改写（§2.3–§2.4）

1. **定位**：不像教科书式合成那样造新内容，而是把给定文本改写成另一种风格或结构。
2. **低质数据**：改写成 Wikipedia 风格，以去噪。
3. **高质量数据**：用四种额外提示生成变体，分别是多样问答对、精炼重写、提取知识、知识清单，此外也做 Wikipedia 风格改写。中档数据因时间与资源未做合成。
4. **生成**：用 Mistral NeMo 12B Instruct，FP8 推理，top-p 0.9，温度 0.5，共合成超过 1.8T token，其中 336.3B 来自低质文档、1.5T 来自高质量文档（§2.3）。
5. **规模**（Table 4）：覆盖 99 个 Common Crawl 快照。完整的 Nemotron-CC 共 6.3T token，其中唯一真实 token 4.4T、合成 token 1.9T；高质量子集 Nemotron-CC-HQ 共 1.1T，由最高分的真实数据与多样问答合成组成，用于短训练长度上的公平对照。对照的 DCLM 为 3.8T（唯一真实 1.0T）、FineWebEdu 为 1.3T（0.2T）、FineWebEdu-2 为 5.4T（1.1T）。
6. **合成消融**（Table 10，8B 训练 1T token）：低质数据改写后平均分从 52.5 到 54.0；高质量数据用合成替换部分重复后从 55.8 到 56.7。报告也看到部分任务略降，可能引入了错误信息（§3.3）。

## 六、主要结果（§3）

1. **设定**（§3.1）：Megatron-LM 训练的 8B 模型，单次 1T token 的训练用 1024 张 H100 约 40 小时。数据配比中 73% 为被测的英文 Common Crawl 数据集，其余固定。评测用 LM Evaluation Harness 的十项任务。
2. **1T token**（Table 5）：Nemotron-CC-HQ 的 MMLU 为 59.0、平均 60.1；DCLM 为 53.4 与 57.0；完整 Nemotron-CC 为 53.0 与 57.8。Figure 1 的说明写道，相对 DCLM，报告的方法既可以得到大 4 倍、质量相近的数据集，也可以用高质量子集提高 MMLU。
3. **15T token**（Table 6、附录 E）：本数据集贡献 7.2T token（附录写作 7.17T）。课程分两阶段，前 9T token 中英文 Common Crawl 占 59%（5.31T），用中、中高、高三档；后 6T token 中占 31%（1.86T），只用高档。自报的 lm-eval 结果中，8B 模型的 ARC-C 为 58.1、MMLU 为 70.3、平均 64.7，Llama 3.1 8B 为 55.0、65.3、64.2。

## 七、意义

1. **把「砍量换分」改成「量质兼顾」**：集成提高召回，高质量数据不再被启发式误删，长程训练有了足够的唯一 token。
2. **合成承担的是变换，不是造知识**：低质改写去噪，高质量改写增加新鲜 token，这条路线与教科书式合成分工不同。
3. **数据管线向学习式飞轮靠拢**：分类器与改写模型都随 LLM 变好而变好，报告把这当作总的设计原则。

## 八、局限与待核实

1. **报告自述**（§6）：集成与分桶只试了一种策略；改写没有做事实忠实度校验；管线没有完整消融；只覆盖英文；没有去污染。
2. **自报评测**：15T 的对照数字用报告自己的 lm-eval 设置，可能与 Meta 公布的 Llama 3.1 8B 数字不同（§3）。
3. **合成总量两种写法**：§2.3 写作超过 1.8T，摘要与 Table 4 写作 1.9T，照录不调和。
4. **版本差异**：v1（2024-12-03）到 v2（2025-05-30），附录重排并新增管线总览与长程课程细节，发布说明补了 Common Crawl 使用条款、NeMo Curator 的 Apache 2.0 许可与已发布的分类器，语言过滤补了 pycld2，去重补了「每八分之一快照」，单分类器召回由「不到 10%」改为「约 10%」。本篇按 v2。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[分词器与数据配比]] | FineWeb-Edu 与 DCLM 作为对照与集成成员 | 网页策展通史、分词器与配比 |
| [[合成数据与教科书式数据]] | 本篇的合成是改写与结构变换，与那篇的造教材路线并列 | 教科书式合成预训练 |
| [[合成对齐数据Magpie]] | 同为数据侧：本篇是预训练网页语料，那篇是对齐阶段的指令与偏好数据 | 对齐数据合成 |
| [[BeyondWeb合成预训练]] | 那篇把本篇管线里的高质量合成子集当作对照基线 | 合成预训练的后续方法 |
| [[Inspect评测Harness]] | 本篇的消融用 lm-eval-harness 评十项任务，是那篇脉络中静态基准框架的使用实例 | 评测框架设计 |
| [[评测数据污染检测与可靠性]] | 本篇作者未做去污染，属于那篇讨论的训练方责任一侧 | 污染检测方法 |
| [[Nemotron3Ultra技术报告深读]] | 同为 NVIDIA 的预训练侧报告：那篇记 Nemotron 3 旗舰的数据集与配比，网页语料的过滤、去重与合成改写在本篇 | 旗舰模型的数据配比与训练 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Nemotron-CC arXiv（v2）](https://arxiv.org/abs/2412.02595v2) | Table 1、2、4–7、9、10 与附录 E |
| 2 | [NeMo Curator](https://github.com/NVIDIA-NeMo/Curator) | 报告所附参考实现地址，不引仓库页事实 |
| 3 | [nemocurator-fineweb-mixtral-edu-classifier](https://huggingface.co/nvidia/nemocurator-fineweb-mixtral-edu-classifier) | 报告所附分类器地址，仅用于核对名称 |
