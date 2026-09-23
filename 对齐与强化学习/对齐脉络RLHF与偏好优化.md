---
title: 对齐脉络：RLHF / 偏好优化 / 宪法式方法
topic: 对齐脉络RLHF与偏好优化
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
archived: 2026-09-22
---

# 7　对齐脉络：RLHF / 偏好优化 / 宪法式方法

> 攻坚线：**架构思想（主）+ 数学原理（辅）**。入口论文：
> - InstructGPT / RLHF：Ouyang et al., *Training language models to follow instructions with human feedback* (arXiv:2203.02155)
> - Constitutional AI / RLAIF：Bai et al., *Constitutional AI: Harmlessness from AI Feedback* (arXiv:2212.08073)；Anthropic 介绍页同日发布
> - DPO：Rafailov et al., *Direct Preference Optimization: Your Language Model is Secretly a Reward Model* (arXiv:2305.18290, NeurIPS 2023)
> 本笔记只据已读 PDF / 介绍页写要点；未在原文中读到的奖励模型层内结构细节、未核对的实验分一律标「待核实」或不写。

---

## 一、为何需要对齐流水线（基座 → 助手）

### 1.1 预训练目标与「跟用户意图」不对齐

InstructGPT 开篇写得很直接：把语言模型做大，**本身并不会**让它更好地理用户意图。大模型仍可能编造事实、产生有毒输出，或对用户毫无帮助——也就是 **not aligned with their users**。

根因是目标函数错位：近年大 LM 常用的语言建模目标是「在网页上预测下一个 token」，这与「有帮助且安全地遵循用户指令」不是同一件事。论文沿用 Askell et al. (2021) 的 HHH 框架，希望模型：

- **Helpful**：帮用户完成任务；
- **Honest**：不捏造、不误导（实践中常用可测的 *truthfulness* 代理）；
- **Harmless**：不造成身心 / 社会等伤害。

Constitutional AI 同样把「即使能力逼近或超过人类，仍保持 helpful / honest / harmless」写成动机，并强调：能力上去之后，不能指望人类逐条监督所有行为，需要可扩展的监督（scaling supervision）。

DPO 从另一侧说同一件事：无监督 LM 在海量、目标混杂的人类文本上学会了广谱知识与部分推理，但「在宽广能力中选出我们想要的行为」才是可控与安全的关键——这正是偏好学习 / 对齐阶段要做的事。

### 1.2 「对齐流水线」在工程上是什么意思

公开叙事里，一条常见流水线是：

1. **基座（pretrained LM）**：下一 token 预测，能力广、行为难刻画；
2. **监督微调（SFT / instruction tuning）**：在「期望行为示范」上模仿，把模型拉进「助手」分布；
3. **偏好对齐（RM + RL，或 DPO 一类直接偏好优化，或 CAI / RLAIF）**：用相对偏好进一步塑形，尤其在安全、诚实、风格等难用单条示范写死的轴上。

InstructGPT 明确说他们做的是 **fine-tuning approaches**，用 RLHF 把 GPT-3 调到能跟随宽广指令；并坦承：这是对齐到「特定一群人（标注者与研究者）陈述的偏好」，而非任何更广的「人类价值观」抽象。Constitutional AI 则把「原则列表（constitution）」推到前台，试图让治理规则更显式、更少依赖海量有害性人工标注。

**跟读抓手：**「基座会说话」≠「助手会按意图、按约束说话」；对齐流水线是在**改目标与反馈来源**，而不只是继续堆参数。

---

## 二、架构思想

### 2.1 InstructGPT / RLHF 三阶段（Figure 2）

方法论沿袭 Ziegler et al. (2019)、Stiennon et al. (2020) 的「人类偏好作奖励信号」路线，应用到更广的指令跟随。三步（论文 §3.1）：

| 步骤 | 做什么 | 产出 |
|------|--------|------|
| **Step 1 SFT** | 标注者在提示分布上写「期望行为」示范；对预训练 GPT-3 做监督学习微调 | 监督策略 $\pi^{\mathrm{SFT}}$ |
| **Step 2 RM** | 收集模型输出之间的比较；训练奖励模型预测标注者更偏好哪一个 | 标量奖励 $r_\theta(x,y)$ |
| **Step 3 PPO** | 以 RM 输出为奖励，用 PPO 微调监督策略；并对 SFT 策略加 KL 惩罚 | InstructGPT 策略（文中主推 PPO-ptx） |

要点补充（据 §3.2–3.5，不外推未写结构）：

- **提示来源**：早期靠标注者手写三类提示（Plain / Few-shot / User-based）做冷启动；之后主要用 API Playground 上提交的提示（去重、按 user ID 切分、训练侧滤 PII）。三个数据集规模数量级：SFT 约 13k、RM 约 33k、PPO 约 31k training prompts（Table 6 细节见原文附录）。
- **比较收集**：为加速，每次给标注者 $K=4$–$9$ 条回复排序，从而得到 $\binom{K}{2}$ 对比较；训练时把同一 prompt 的全部比较当作**一个 batch element**，避免「打散后一轮就过拟合」。
- **RM 初始化（论文写到的部分）**：从 **SFT 模型去掉最后 unembedding 层**起步，输入 prompt+response，输出**标量**奖励。文中实际用 **6B RM**（省算力；并称 175B RM 训练不稳定、不太适合再当 RL 的 value function——细节指向 Appendix C，本笔记不展开未读附录）。
- **RL 设定**：环境是 bandit——随机抽客户提示，模型回一条，RM 给奖励后 episode 结束；另加 **per-token KL** 相对 SFT，减轻对 RM 的过优化；value function 从 RM 初始化。
- **PPO-ptx**：把预训练梯度混进 PPO，缓解公开 NLP 基准上的「alignment tax」；InstructGPT 在文中默认指 PPO-ptx。

主结果叙事（摘要 / §1，便于跟读，非本笔记复现）：1.3B InstructGPT 输出在其 prompt 分布上可被偏好于 175B GPT-3；真实性提升、毒性有小幅改善；偏见相关基准未必改善；RLHF 可能带来公开基准回退，可用预训练混合缓解。

**架构直觉：** RLHF 把「人类相对偏好」压成一个**可打分的 RM**，再把「跟指令」建成**对 RM 的受限优化**——流水线长、组件多（SFT / RM / 策略 / 采样 / PPO），但职责清晰。

### 2.2 Constitutional AI / RLAIF：原则写进流程，有害性标签尽量交给模型

Anthropic 论文与介绍页一致：目标是在**没有任何「标出有害输出」的人类标签**的前提下，靠一份原则列表（constitution）做自改进，训练相对无害且**不过度回避**的助手；有害请求上倾向**解释为何拒绝**，而不是一味逃避。

整体两阶段（Figure 1）：

#### （A）监督阶段 SL-CAI：Critique → Revision → Finetune

1. 从 **helpful RLHF** 模型出发，对 red-team 提示采样回复（易引出有害内容）；
2. 按 constitution 中的原则，让模型**自我 critique**；
3. 再按原则 **revision**，去掉有害等内容；
4. 可多轮 critique–revision；原则共约 **16** 条相关 harmlessness 原则，每步随机采样；
5. 用修订后的回复（并混入 helpfulness 提示上的 helpful 模型采样）**微调预训练模型** → **SL-CAI**。

论文还对比了「跳过 critique、直接 revision」：小模型上带 critique 的修订 harmlessness PM 分更好；大模型上差距不明显，但主实验仍保留 critique，因其对推理过程更透明（§3.5）。

#### （B）RL 阶段 RLAIF：AI 偏好 → Preference Model → RL

- **Helpfulness** 比较仍可用人类反馈（与先前 HH RLHF 工作衔接）；
- **Harmlessness** 比较改由反馈模型（多为预训练 LM，CoT 变体则用 helpful RLHF）做选择题式评判，原则同样从 constitution 中随机抽；
- 用（人类 helpful + AI harmless）比较训练 **Preference Model (PM)**；
- 再以 PM 为奖励做 RL；策略初值与采样常用 **SL-CAI**。

这就是 **RL from AI Feedback (RLAIF)**：管道后半与 RLHF 同构，变的是**有害性标签来源**与**原则是否显式**。

动机四条（§1.1，压缩）：扩展监督、缓解 helpful vs harmless 张力（少逃避、多解释）、原则更透明、改目标时少重新采人标。

**跟读抓手：** CAI 不是「不用 RL」，而是「把人类监督上移到原则与少量示范，把大规模有害比较交给模型」；SL 阶段解决探索起点，RL 阶段拉高表现与可靠性（Figure 1 文案）。

### 2.3 DPO：同一 KL 约束目标，绕开显式奖励模型与 RL 环

DPO 的诊断：标准 RLHF 先拟合奖励模型，再用 RL（常 PPO）在「高奖励 + 不远离参考策略」下微调——流程复杂、常不稳定，训练环内还要对 LM 采样。

核心架构思想（§4）：

1. 仍从与 RLHF 相同的 **KL 约束奖励最大化**目标出发（下文公式 (3)）；
2. 写出该目标下最优策略的闭式（公式 (4)）；
3. **改写变量**：把奖励写成最优策略与参考策略的 log 比 + 配分函数（公式 (5)）；
4. 代入 Bradley-Terry 时，**配分函数在成对比较中消去**，偏好概率只依赖策略与 $\pi_{\mathrm{ref}}$（公式 (6)）；
5. 于是对策略直接做 **二元分类式最大似然**（公式 (7)）——**不再单独训 RM，也不跑 PPO**。

论文比喻：LM **暗含**一个奖励模型；策略网络同时扮演「语言模型」与「隐式奖励」。实现上仍需要偏好数据 $(x,y_w,y_l)$ 与参考策略 $\pi_{\mathrm{ref}}$（通常取 SFT；若无 SFT，可用偏好里的 $y_w$ 做 MLE 初始化参考）。

**脉络位置：** InstructGPT 把「示范 → 比较 → RM → PPO」立成主流工厂流水线；CAI 把「有害监督」原则化、AI 化；DPO 在数学上折叠「RM + RL」为一步偏好分类，换实现简单性（论文实验宣称在情感控制、摘要、单轮对话等设定上可匹敌或超过 PPO-RLHF——具体数字跟读原文 §6，此处不抄未核对表）。

---

## 三、数学原理辅线（直觉为主，关键公式注明出处）

### 3.1 偏好建模与 Bradley-Terry 直觉

假设存在潜在标量「好坏」$r^*(x,y)$，人类（或反馈模型）对两条回复的偏好服从 Bradley-Terry（BT）：

$$
p^*(y_1 \succ y_2 \mid x)
=
\frac{\exp(r^*(x,y_1))}
{\exp(r^*(x,y_1))+\exp(r^*(x,y_2))}
=
\sigma\bigl(r^*(x,y_1)-r^*(x,y_2)\bigr)
\quad\text{（DPO 文 Eq. 1）}
$$

直觉：只看**奖励差**；差越大，偏好越尖。成对比较不需要绝对分，适合「哪条更好」标注。

InstructGPT 的 RM 损失与此同构（成对 logistic / 交叉熵），写为（InstructGPT Eq. 1）：

$$
\mathrm{loss}(\theta)
=
-\frac{1}{\binom{K}{2}}
\,\mathbb{E}_{(x,y_w,y_l)\sim D}
\bigl[\log\sigma(r_\theta(x,y_w)-r_\theta(x,y_l))\bigr]
$$

其中 $y_w$ 为更被偏好的 completion。因损失对奖励整体平移不变，文中在 RL 前用 bias 把标注者示范的均分归一到 0。

DPO 对奖励模型的 MLE 损失同形（DPO Eq. 2）：

$$
L_R(r_\phi,D)
=
-\mathbb{E}_{(x,y_w,y_l)\sim D}
\bigl[\log\sigma(r_\phi(x,y_w)-r_\phi(x,y_l))\bigr].
$$

### 3.2 RLHF 中的「奖励 + KL」直觉

偏好学完后，策略优化常用（DPO 文对 Ziegler / Stiennon / InstructGPT 等管线的整理，Eq. 3）：

$$
\max_{\pi_\theta}
\;
\mathbb{E}_{x\sim D,\,y\sim\pi_\theta(\cdot|x)}
\bigl[r_\phi(x,y)\bigr]
\beta\,
D_{\mathrm{KL}}\bigl(\pi_\theta(\cdot|x)\,\|\,\pi_{\mathrm{ref}}(\cdot|x)\bigr).
$$

- **第一项**：跟着奖励（人类偏好的代理）走；
- **第二项**：别离参考策略（常为 SFT）太远——避免奖励过优化、多样性塌缩、跑出 RM 可靠区。

InstructGPT 实现里还写成「RM 标量奖励 − β·log(π_RL/π_SFT)」并可选加上预训练 log 项（InstructGPT Eq. 2）；PPO 在离散生成上优化该不可微目标。

闭式最优策略（在给定 $r$ 时）可写成（DPO Eq. 4）：

$$
\pi_r(y|x)
=
\frac{1}{Z(x)}
\,\pi_{\mathrm{ref}}(y|x)
\,\exp\Bigl(\frac{1}{\beta}r(x,y)\Bigr),
\quad
Z(x)=\sum_y \pi_{\mathrm{ref}}(y|x)\exp\bigl(r(x,y)/\beta\bigr).
$$

直觉：在参考分布上按 $\exp(r/\beta)$ 重加权；$Z(x)$ 是配分函数，直接算很贵——这正是「有最优形式却难用」的痛点。

### 3.3 DPO 损失为何是等价改写（直觉链）

1. 由 Eq. 4 反解奖励（DPO Eq. 5）：

$$
r(x,y)
=
\beta\log\frac{\pi_r(y|x)}{\pi_{\mathrm{ref}}(y|x)}
+
\beta\log Z(x).
$$

2. BT 只依赖 **$r(x,y_1)-r(x,y_2)$**，两项里的 $\beta\log Z(x)$ **相减抵消**。
3. 于是偏好概率可完全用最优策略与 $\pi_{\mathrm{ref}}$ 表达（DPO Eq. 6）。
4. 把 $\pi_r$ 换成可训的 $\pi_\theta$，得到直接偏好损失（DPO Eq. 7）：

$$
L_{\mathrm{DPO}}(\pi_\theta;\pi_{\mathrm{ref}})
=
-\mathbb{E}_{(x,y_w,y_l)\sim D}
\log\sigma
\Biggl(
\beta\log\frac{\pi_\theta(y_w|x)}{\pi_{\mathrm{ref}}(y_w|x)}
\beta\log\frac{\pi_\theta(y_l|x)}{\pi_{\mathrm{ref}}(y_l|x)}
\Biggr).
$$

这是对「隐式奖励」$ \hat r_\theta(x,y)=\beta\log\frac{\pi_\theta(y|x)}{\pi_{\mathrm{ref}}(y|x)} $ 的 BT 分类损失——与先训 $r_\phi$ 再 RL **同一偏好模型假设下的改参数化**，而不是另起一套无关目标。

**梯度直觉（论文 §4）：** 增大 $\log\pi(y_w)$、减小 $\log\pi(y_l)$；权重 $\sigma(\hat r_\theta(x,y_l)-\hat r_\theta(x,y_w))$ 在「隐式奖励排错」时更大。去掉该动态权重的朴素概率比目标，论文称易导致退化（见其 Appendix Table 3）。

**跟读口诀：** BT 吃「分差」→ KL 约束最优策略让「分」≈「β·log 策略比 + 常数」→ 分差里常数消掉 → 直接对策略做分类。

---

## 四、常见误区

1. **「对齐 = 再预训练一轮 / 只做 SFT」**
 SFT 解决的是示范模仿；相对偏好、安全边界、细风格往往仍要 RM+RL、DPO 或 CAI 一类阶段。InstructGPT 把 SFT 与 PPO 分步写清，不是同义词。

2. **「RLHF 的奖励模型 = 人类价值观的客观度量」**
 InstructGPT 自陈对齐的是标注者与研究者偏好；RM 是偏好代理，会过优化（CAI 文亦讨论 Goodharting / 套话化）。

3. **「有 KL 就能随便加大奖励权重」**
 KL 是软约束，系数 β 与 RM 尺度耦合；过小 KL 仍可模式崩塌或钻 RM 空子。DPO 把 β 写进分类损失，但仍需调。

4. **「Constitutional AI = 不用人类、也不用 RL」**
 CAI **仍用** SL + RL；人类监督上移到原则与 helpfulness 等；harmlessness 比较可 AI 化。介绍页与论文摘要写的是「无有害输出人类标签」，不是「零人类」。

5. **「DPO 证明不需要偏好模型假设」**
 DPO 仍嵌在 BT（或 Plackett-Luce）假设里；变的是**不显式拟合独立 RM + 不跑 RL 采样环**，不是取消偏好建模。

6. **「DPO 与 RLHF 目标无关，只是另一种对比学习」**
 论文论证路径是：从 **同一 KL 约束奖励目标** 出发做改参数化；朴素「只拉高 $y_w$、压低 $y_l$」而无 BT+β 权重，与 DPO 不是一回事。

7. **「InstructGPT 已公开完整 175B RM 结构与稳定配方」**
 正文明确主用 6B RM，并称 175B RM 不稳；更细结构 / 超参见附录——**未读附录则不要脑补层数或头宽**。

8. **「越无害越好，逃避也算对齐成功」**
 CAI 明确推动 **non-evasive**：在同样无害时，偏好解释性拒绝而非关机式回避；与「只会说抱歉」不是同一目标。

9. **把论文主结果数字当可复现承诺**
 各方评测协议、标注者指令、prompt 分布不同；笔记引用数量级时需回指向图表，复现前应重读实验节与附录。

---

## 五、引用

1. Long Ouyang et al. *Training language models to follow instructions with human feedback*. arXiv:2203.02155, 2022.
 PDF：`https://arxiv.org/abs/2203.02155`
 链接：https://arxiv.org/abs/2203.02155 ；https://arxiv.org/pdf/2203.02155

2. Yuntao Bai et al. *Constitutional AI: Harmlessness from AI Feedback*. arXiv:2212.08073, 2022.
 PDF：`https://arxiv.org/abs/2212.08073`
 链接：https://arxiv.org/abs/2212.08073 ；https://arxiv.org/pdf/2212.08073
 介绍页：https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback （2022-12-15）

3. Rafael Rafailov, Archit Sharma, Eric Mitchell et al. *Direct Preference Optimization: Your Language Model is Secretly a Reward Model*. NeurIPS 2023 / arXiv:2305.18290.
 PDF：`https://arxiv.org/abs/2305.18290`
 链接：https://arxiv.org/abs/2305.18290 ；https://arxiv.org/pdf/2305.18290

4. 脉络前置（文中引用、本议题不展开精读）：Christiano et al. 2017（RLHF 偏好）；Ziegler et al. 2019；Stiennon et al. 2020（摘要 RLHF）；Askell et al. 2021（HHH）；Bai et al. 2022（HH RLHF / red team，CAI 前置）；Schulman et al. 2017（PPO）；Bradley & Terry 1952（BT 模型）。

---

## 待核实 / 未读范围（跟读清单）

- InstructGPT **Appendix B/C**：标注者筛选与人口统计细节、175B RM 不稳的具体现象、PPO / PPO-ptx 超参表。
- InstructGPT 各公开基准精确分与 Figure 1 误差条：笔记只用了摘要级叙述，复述百分比前应对照正文表图。
- Constitutional AI **Appendix C** 完整 constitution 条文、Appendix D/E 流水线与 few-shot 样例；Crowdworker Elo 的精确读图。
- CAI 中 CoT 标签概率 **clamp 到 40–60%** 的消融是否在所有规模上成立——仅据 §4.1 定性描述。
- DPO 正文 §6 与附录：情感 / TL;DR / Anthropic-HH 的 win rate 数字、与 PPO 的 KL–reward frontier（Figure 2）——未逐表誊抄。
- DPO Theorem 1 / Proposition 1（奖励等价类与规范化）的完整假设：本笔记只用了推导直觉，证明细节待读 §5 与 Appendix A。
- 介绍页以外的 Anthropic「Policy Memo」正文未取用。
- 后续方法（IPO、KTO、ORPO、RLAIF 后续变体等）不在本 [[对齐脉络RLHF与偏好优化]] 精读范围。

## 相关笔记

- [[注意力与Transformer核心思想|Attention / Transformer]]
- [[DecoderOnly与GPT路线|Decoder-only / GPT]]
- [[规模定律与预训练范式|规模定律与预训练]]
- [[混合专家架构|MoE / 稀疏激活]]
- [[对齐脉络RLHF与偏好优化|对齐 RLHF / DPO]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿模型谱系]]

