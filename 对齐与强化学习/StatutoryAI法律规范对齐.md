---
title: "Constitutional 新变体：Statutory AI（法律规范对齐，11）"
topic: StatutoryAI法律规范对齐
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
sources:
 - https://arxiv.org/abs/2608.28593
 - https://arxiv.org/abs/2212.08073
arxiv: ["2608.28593", "2212.08073"]
related: ["宪法分类器防御", "对齐脉络RLHF与偏好优化", "法律专科模型", "审慎对齐与断路器"]
---

# Constitutional 新变体：Statutory AI（法律规范对齐）

> **定位**：[[StatutoryAI法律规范对齐]] **P1**——在经典 **Constitutional AI（CAI，2212.08073）** 的「原则清单 → 批判/修订」谱系上，立近窗 **Statutory AI（2608.28593）**：**规范来源从手写/公司宪法原则 → 成文法律语料（本稿为法国刑法条文英译）**；本卡只做 **推理期 critique–revision 对齐范式** 与文内汇总安全指标，**不**升经典 CAI 为第二主文深读。
> **攻坚线**：**架构思想 / 对齐范式（主）** + **评测字段（辅）**（初始/终态 vulnerability、Comparison Score、单 prompt 耗时；法官为 GPT-5 / Gemini 2.5 Flash）。
> **硬划界（开篇钉死）**：
> - **≠ [[宪法分类器防御]] Constitutional Classifiers**：不写 constitution → 合成数据 → **部署侧** input / output / exchange **分类器护栏** 工程与生产级探针级联。
> - **≠ [[对齐脉络RLHF与偏好优化]]**：不重写 RLHF / DPO / CAI 损失与三阶段通史；CAI 在本卡仅作 **谱系补链**（SL 批判修订环 + RLAIF 一句）。
> - **≠ [[法律专科模型]] 法律专科模型**：SaulLM / Legal-R1 / Unilaw-R1 是 **域适应 / 法律推理任务模型**；本卡是 **用法律条文当对齐宪法**，不是法律考试/文书专科。
> - **≠ [[审慎对齐与断路器]]**：不写 Deliberative Alignment 的规范 CoT 训练，也不写 Circuit Breakers / Representation Rerouting 的 **表征熔断**。
> **硬约束**：**禁止**侧写可复现越狱 / 绕过步骤、对抗提示全文、红队剧本；只保留公开论文中的 **对齐范式与汇总指标**（vulnerability %、Comparison Score、耗时比、分类器 P/R、McNemar 等）。
> **禁止编造**：作者、法条编号、表数字、页数一律锚定官方 PDF（2026-09-22 CST）。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文** | Delage, Canu, Décombas & Foureur (**JustAI** / **INSA Rouen Normandie**), *Statutory AI: Aligning Large Language Models With Legal Norms* | arXiv:**2608.28593v1** \[cs.AI\] **13 Jun 2026**；`https://arxiv.org/abs/2608.28593`（**166K**，**15** 页 letter） | **规范来源变体**：刑法主题分类 → 条文字典 → **单轮** CoT 批判/修订；与 CAI 批判环对照 |
| **补链** | Bai et al. (Anthropic), *Constitutional AI: Harmlessness from AI Feedback* | arXiv:**2212.08073v1** \[cs.CL\] **15 Dec 2022**；`https://arxiv.org/abs/2212.08073`（**2.0M**，**34** 页； CreationDate **2022-12-19 CST**） | **谱系**：SL 批判修订（SL-CAI）+ RLAIF；本卡**不**重写全管线 |

**开源（主文自报，本篇不展开实现）：** `https://github.com/justai-labs/statutory-ai`

**一句话抓手：**
- **CAI**：少量人类写的 **constitution 原则** 驱动 AI 自批自改，再可选进 SL / RLAIF。
- **Statutory AI**：把原则换成 **已有成文法律条文**（本稿五类刑法主题），先 **主题分类** 再 **一次** 批判/修订；文称有害率降幅约 **52–59 pp**，较同设定 CAI 批判环约高 **10 pp**，且计算时间砍半以上。

**体积判定：** 两 PDF 均 **<20MB**，按验收规矩 ****。

---

## 二、问题立轴：规范来源从「原则清单」到「成文法律」

### 2.1 谱系位置（相对 CAI / GfH）

| 轴 | 经典 CAI（补链摘要） | GfH 一类总原则（文内对照） | Statutory AI（主文） |
|---|---|---|---|
| **人类介入** | 人类写原则清单；无害标签可极少 | 极简总指令（如 “best for humanity”） | **不新增原则标注**；复用既有法条（作者手工选条） |
| **规范粒度** | 多条自然语言原则，批判时可随机抽 | 过宽、易主观解读偏置 | **主题绑定的具体条文**（定义型条款优先） |
| **本卡深读范围** | 只取 **批判–修订环** 接口 | 动机对照一句 | **推理期两阶段流水线** + 文内表 |

研究问题（Statutory §1，意译）：在 LLM-as-a-judge / constitutional 框架下，**既有法律体系能否充当 constitution**，在无需额外手写规则的情况下给出可操作的「有害」定义？作者自称：就「把既有法条嵌进 CAI 式批判–修订环做 harmlessness」而言，这是首个此类工作（§1.1）。

### 2.2 与相邻笔记只取接口（勿展开）

| 已入库 | 本篇只取 | 本篇明确不写 |
|---|---|---|
| **[[宪法分类器防御]]** | 「constitution 可驱动护栏」同一词根 | 部署侧分类器 / exchange / 探针 / 生产 RT 小时 |
| **[[对齐脉络RLHF与偏好优化]]** | CAI = RLAIF 前史一句 | RLHF/DPO 损失、奖励模型训练通史 |
| **[[法律专科模型]]** | 「法律文本」一词 | 法律专科继续预训练、LawBench/JEC-QA 任务分、替代律师叙事 |
| **[[审慎对齐与断路器]]** | 「规范可进推理」对照 | Deliberative 训练配方、Circuit Breaker 熔断步骤 |

---

## 三、补链速写：Constitutional AI（2212.08073）只要骨架

> **不升主深读。** 只钉与 Statutory 对照所需的两阶段骨架与公开叙事；**不**转载附录原则全文、有害对话样例或可复用攻击材料。

`
Helpful 初模
 │ 对「易引出有害回复」的提示采样
 ▼
Critique ← constitution 原则（自然语言）
 ▼
Revision ← 据批判改写
 ▼
SL-CAI（用修订样本微调）──可选──► RLAIF（AI 偏好 → PM → RL）
`

- **监督阶段（SL-CAI）**：采样 → 自批 → 自改 → 在修订回复上微调；原则列表提供「何谓有害」的显式规格。
- **强化学习阶段（RLAIF）**：从微调模采样成对回复，由模型按原则判优劣，训 preference model，再 RL。
- **与 Statutory 的接口差**：Statutory **POC 只实现批判–修订环**（对应 CAI 监督阶段的前半），文称 **未** 做 SFT / RL；对照基线也是「CAI 批判环 × 最多四轮」，而非完整 RL-CAI。

---

## 四、Statutory AI 范式：主题分类 × 条文字典 × 单轮批判修订

### 4.1 总装（§2）

`
用户提示
 │ Stage 1：主题分类（可多标签；否则 NaN）
 ▼
{歧视 / 泄露机密 / 欺诈性欺凌弱势者 / 身心暴力 / 欺诈} ∪ {NaN}
 │ 查作者手工构建的「主题 → 刑法条文」字典
 ▼
初回复（无额外规范）
 │ Stage 2：CoT 批判（条文是否可能被违反，哪怕轻微）
 ▼
CoT 修订（去有害/违法内容；可引用法条；要求共情与教育性语气）
 │
 └── 结束（单轮；不因多原则随机抽样而多轮循环）
`

**设计要点（文内）：**

1. **中间道路**：介于「公司手写多原则宪法」与「GfH 过宽总原则」之间——用 **已立法、可公开核验** 的条文作规范源。
2. **分类是前置层**：把提示映射到刑法主题，再只注入该主题相关条文，避免「任意塞法条」；五主题文称覆盖红队数据集约 **80%**（POC 取法）。
3. **单轮足够**：因相关条文在首轮批判已全部给出，**不**像多原则 CAI 那样做多轮随机原则批判。
4. **NaN 缺口**：未落入五主题时「无法适用宪法条文」——本稿 **未** 解决，留作未来工作。
5. **CoT**：批判与修订均要求逐步推理；作者援引 CAI 族工作称 CoT 有助于 constitutional 表现。

### 4.2 规范字典与法域（附录 B，只列编号与主题）

| 主题（英文标签） | 法国《刑法典》条文（文内） |
|---|---|
| Fraud | 313-1, 226-4-1, 441-1, 223-1, 322-14, 323-1 |
| Confidential Information Disclosure | 226-13 |
| Discrimination | 225-1 |
| Violence | 222-7, 222-9, 222-14-2, 222-14-4, 222-16 |
| Fraudulent Abuse of a Vulnerable Person | 223-15-2 |

条文由作者 **手工英译** 以与 CAI 实验语言一致；**法域 = 法国刑法**（非多国法典专家系统）。本笔记 **不** 复述条文正文全文（体积与安全口径）；需要核验时读 PDF 附录与公开法典。

### 4.3 实验槽位（§2.1–2.2 / §3.1）——只留角色，不留攻击面

| 槽位 | 文内选择 | 备注（公开聚合） |
|---|---|---|
| **分类器** | Gemini 2.5 Flash（全程固定） | 为隔离「分类误差 vs 法定批判」混淆 |
| **批判/修订模** | Mistral 7B（Ollama `mistral:7b` Q4_K_M）；Gemini 2.5 Flash；Qwen3-VL-30B-A3B-Thinking（HF 端点，Q8 量化变体） | 开源弱 / 专有 / 开源强三档 |
| **评测集** | 自 *Adversarial Dataset* \[Jiang et al., WildTeaming\] 随机 **1000** 条非 NaN 提示 | 文称相对 ALERT / Perez 等「过显式」基准，近模更不易被击穿；**本卡不转载样本提示** |
| **CAI 基线** | 同批判–修订环，最多 **四** 轮；用 CAI 文 few-shot；同样 CoT 指令 | **无** SFT/RL |
| **法官** | **主**：GPT-5；**辅**：Gemini 2.5 Flash（因同族入流水线，可能偏置） | 作者人工抽查推理迹 |

**安全读法：** 文中出现的「vulnerability / ART %」仅作 **公开聚合字段**；本卡 **禁止** 复述具体对抗提示、绕过手法或可复现攻击步骤。

---

## 五、评测字段（只汇总表内公开指标）

### 5.1 分类器抽检（Table 1，n=278，人工金标；95% 置信 / 5% 误差口径）

| Category | Precision | Recall |
|---|---:|---:|
| Violence | 90% | 96% |
| Confidential Information Disclosure | 96.7% | 96.6% |
| Fraud | 89% | 98% |
| Discrimination | 99% | 95% |
| Fraudulent Abuse of a Vulnerable Person | 100% | 100% |
| NaN | 82% | 100% |

文称各类 P/R 均 **>80%**，歧视与泄密类 **>95%**，作为进入批判阶段的充分条件。

### 5.2 批判–修订主结果（Table 2；格式 = GPT-5 / Gemini 2.5 Flash）

**指标定义（文）：**
- **Initial vulnerability**：初回复是否有害。
- **Comparison Score**：两方法二选优（有害优先；仅当修订严重失用才罚有用性）。
- **Final vulnerability**：修订后是否仍有害。

| 被评模型 | Initial vuln. | CAI Comparison | CAI Final vuln. | Statutory Comparison | Statutory Final vuln. |
|---|---|---|---|---|---|
| Gemini 2.5 Flash | 62.3% / 66.3% | 85.5% / 80.8% | 14.5% / 19.2% | **96.4% / 90.6%** | **3.6% / 9.4%** |
| Mistral 7B | 80.6% / 94.1% | 70.5% / 57.2% | 29.5% / 42.8% | **78.2% / 69.7%** | **21.8% / 30.3%** |
| Qwen 30B | 57.3% / 66% | 85.1% / 80.8% | 14.9% / 19.2% | **95% / 93.2%** | **5% / 6.8%** |

**摘要口径（与 Abstract / §3.3 对齐，不另推算）：**

- 两法官均认为 vulnerability **大幅下降**：CAI 至少约 **42 pp**；Statutory 至少约 **52 pp**（文）。
- Abstract：Statutory 跨测试模有害内容降 **52–59 pp**，约比标准 CAI **高 10 pp**。
- McNemar：Statutory 相对 CAI 在全部「法官 × 模型」组合上显著；绝对增益约 **∆ = +7.7～+13 pp**；Cohen’s *h* ≈ **0.18–0.51**；匹配优势比约 **1.5–4.5×**（Statutory 在 CAI 失败案例上更常成功）。
- **不**把 Comparison Score 解读为「可上线合规产品」——仍是 POC + LLM-as-judge。

### 5.3 计算时间（Table 3，秒 / prompt 均值）

| 模型 | Constitutional AI | Statutory AI | Runtime Ratio（CAI / Statutory） |
|---|---:|---:|---:|
| Gemini 2.5 Flash | 100.99 | 44.08 | 2.29 |
| Mistral 7B | 70.8 | 32.3 | 2.19 |
| Qwen 30B | 150.61 | 47.94 | 3.14 |

Abstract：**计算时间削减超过 50%**（与单轮 vs 最多四轮、以及条文一次给全一致）。

### 5.4 讨论中的架构结论（§3.4，压缩）

1. **分类关键**：成功常被法官归因于「先明确识别有害要素再拒绝」；分类错误会直接伤后续批判。
2. **法条 grounding 的教学性**：相对宽泛伦理原则，显式引用成文规范更易被法官视为「直接挡有害 + 可解释拒绝」。
3. **覆盖面互补**：Statutory 强在 **已法典化伤害**；CAI 原则覆盖面更宽、可及「弥散 / 社会建构」伤害——文称两者 **互补**，非互相替代。
4. **语气风险**：纯法条语境易显生硬；修订指令中显式要求共情/教育性语气作缓解（POC 级）。
5. **全文条 vs 仅标签**：作者初步认为 **给全文条** 对更小/更脆弱模型的修订质量更有帮助（开放问题，非消融完结）。
6. **未来**：扩主题与法域；接入完整 CAI 管线（SFT/RL）；量化与规模消融；训练期整合 vs 纯推理期审核的时延/吞吐权衡。

---

## 六、对齐范式对照总览

`
规范来源光谱（本卡主轴）
 GfH 总原则 ──► 手写多原则宪法（CAI）──► 成文法律字典（Statutory）
 │
 ├─ Stage1 主题分类
 └─ Stage2 单轮 CoT 批判/修订

部署 / 训练正交轴（勿混进本卡）
 [[宪法分类器防御]]：serving 旁路分类器护栏
 [[审慎对齐与断路器]]：规范 CoT 训练 或 表征熔断
 [[对齐脉络RLHF与偏好优化]]：偏好优化改权重
 [[法律专科模型]]：法律任务专科权重
`

**可迁移问题（给后续波次，只问评测/架构）：**

1. 主题分类换成检索/法定解释模型后，Final vulnerability 与 NaN 覆盖如何变？
2. 单轮条文批判能否蒸馏进 SL-CAI / RLAIF，而不只做推理期审核？
3. 多法域条文冲突时，Comparison Score 协议如何改（本卡法国刑法单法域）？
4. 与 [[宪法分类器防御]] 级联：Statutory 修订输出能否作为 **exchange 分类器** 的合成规格——只问接口，不写攻击。

---

## 七、來源与抽取索引

| 路径 | 体积 | 页数 | 用途 |
|---|---|---|---|
| `https://arxiv.org/abs/2608.28593` | **166K** | 15 | Statutory AI 全文（主） |
| `https://arxiv.org/abs/2212.08073` | **2.0M** | 34 | CAI 谱系补链 |
| | — | — | |
| | — | — | 同上 |

**体积政策：** 两篇均 **≪20MB**，二进制保留；无权重 / 数据集 / 视频附件。
**安全政策：** 笔记 **未** 收录对抗提示样例、越狱步骤或可复现绕过配方；评测仅保留表内聚合字段。

**状态：** `draft` · date **2026-09-22** · 跟读语言：中文。
