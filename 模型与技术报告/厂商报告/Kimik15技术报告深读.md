---
title: "技术报告专项：Kimi k1.5 Technical Report 深读切片（架构思想 / 数学原理）"
topic: TR-Kimi-k1.5
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
source_url: https://arxiv.org/abs/2501.12599
archived: 2026-09-22
---

# TR · Kimi k1.5 Technical Report 深读切片：架构思想 / 数学原理

> **定位**：报告级对照表 / 深读卡。数字与公式一律取自官方 PDF `https://arxiv.org/abs/2501.12599`（页眉 **arXiv:2501.12599v4**）。
> **刻意不写**：开闭源谱系通史（见 [[开源与闭源前沿模型谱系]]）、RLHF/DPO 通论（见 [[对齐脉络RLHF与偏好优化]]）、test-time scaling 通论（见 [[推理时扩展TestTimeScaling]]）、K2 MoE/MuonClip/Infra 专页（见 模型与技术报告/厂商报告/KimiK2技术报告深读.md）。本卡只补「可对表跟读」的 k1.5 RL 框架、镜像下降近似、length penalty、partial rollout 与相对 K2 的定位。
> **评测分**：摘要 / Table 2–3 / Figure 7 亮点可录；完整 Appendix C 细则与 Figure 5–10 曲线不逐格抄入（见第六节待核实）。

---

## 一、报告元信息

| 项 | 报告原文 / PDF 元数据 | 出处 |
|---|---|---|
| 标题 | Kimi k1.5: Scaling Reinforcement Learning with LLMs（封面另标 *Technical Report of Kimi k1.5*） | 封面 |
| 作者 | Kimi Team（XMP 另列大量具名贡献者） | 封面；XMP |
| arXiv 页眉 | **arXiv:2501.12599v4** \[cs.AI\] **3 Jun 2025** | PDF 第 1 页页眉 |
| XMP identifier | `https://arxiv.org/abs/2501.12599v4` | ` -meta` |
| XMP MetadataDate | 2025-06-12T11:54:31.349167+00:00（→ 用户时区 **2025-06-12 19:54 CST**） | XMP |
| PDF 页数 | **25**（letter） | |
| Creator / Producer | arXiv GenPDF (tex2pdf:)；pikepdf 8.15.1 | |
| 权利声明（XMP） | `http://creativecommons.org/licenses/by-nc-nd/4.0/` | XMP |
| 本地路径 | `https://arxiv.org/abs/2501.12599` | 仓库 |
| 官方镜像（检索到） | arXiv PDF：https://arxiv.org/pdf/2501.12599 ；GitHub：https://github.com/MoonshotAI/Kimi-k1.5 （含 `Kimi_k1.5.pdf`） | 检索 |
| 一句话主张（Abstract） | 多模态 LLM + RL；**long context scaling** + **improved policy optimization**；**不依赖** MCTS / value functions / process reward models；long-CoT 对标 o1；另给 **long2short** | Abstract |

**版本说明（本卡边界）**：本 PDF 页眉仅标 **v4 / 3 Jun 2025**。首发日、v1–v3 修订史若不在本 PDF 正文 → 见第六节待核实。Appendix B 写明当时 **未开源** proprietary 模型权重（「not open-sourcing our proprietary model at this time」）。

---

## 二、相对 K2 的定位（仅报告可核对交叉引用）

| 维度 | Kimi **k1.5**（本 PDF） | Kimi **K2**（对照 [[KimiK2技术报告深读]] / K2 PDF，作定位锚，非本卡深挖） |
|---|---|---|
| 报告主题 | **Scaling RL with LLMs**；多模态 long-CoT 推理 | **Open Agentic Intelligence**；MoE 规模 + MuonClip + agentic 后训练 |
| 开源态度（报告内） | Appendix B：**未开源** proprietary 权重；承诺披露数据管线 | 摘要脚注给 HF Instruct 权重 |
| 主干叙事 | context length 作为 RL 新缩放轴；隐式搜索 ≈ 拉长 CoT | 稀疏 MoE（Table 2：1.04T / 32.6B）+ 预训练 Infra + agentic RL |
| 从 k1.5 → K2 的明确继承（K2 正文引用 \[36\]） | — | 语料处理多沿用 k1.5；**policy optimization 算法沿用 k1.5**；**hybrid colocated** RL 架构类似；**partial rollout** 技术沿用 |
| 本卡该记什么 | RL 目标 / 镜像下降 surrogate / length penalty / prompt 策展 / long2short / Megatron+vLLM hybrid | 见 K2 卡：MuonClip、384 experts、checkpoint-engine &lt;30s 等 |

**一句话定位**：k1.5 是 Moonshot 公开的「长 CoT RL 配方与 Infra 原论文」；K2 在 agentic / MoE / 预训练优化器上开新篇，但 **RL 算法骨架与 partial rollout / colocated 部署明确回指 k1.5**。

---

## 三、架构思想（公开要点 · 禁止外推参数量）

### 3.1 训练阶段流水线（§2 开篇 + §2.5）

| 阶段 | 报告设定 |
|---|---|
| 顺序 | **pretraining → vanilla SFT → long-CoT SFT → RL**（本报告聚焦 RL；预训练细节在 Appendix B） |
| Long-CoT warmup（§2.2） | 在精炼 RL prompt 集上用 prompt engineering 构造「小而准」的 long-CoT 路径（类 rejection sampling，但强调长推理路径）；覆盖 planning / evaluation / reflection / exploration；**lightweight SFT** 作 RL 热身 |
| 模态 | text + vision **联合**训练与 RL（§1；Vision RL 数据三类见 §2.3.5） |

### 3.2 「隐式规划」主张（§2.3.1）——核心架构思想

| 主张 | 报告表述（压缩） |
|---|---|
| 显式搜索树 | 规划算法维护树 $T$，节点 $s=(x,z_{1:|s|})$，批评模型 $v$ 给反馈，再选扩展 |
| 扁平化视角 | 将搜索历史与反馈全部展平为语言 token 序列；规划算法视为 $A(\cdot|z_1,z_2,\ldots)$ |
| 可训练近似 | **不必显式建树 / 实现规划算法**；用长上下文自回归去近似隐式搜索；token 数 ≈ 传统规划算力预算 |
| 部署形态 | 推理仍 **纯自回归采样**，避开高级规划算法的复杂并行 |
| 刻意不做的事（Abstract / §1） | **Monte Carlo tree search、value functions、process reward models** |

> 报告强调：目标不仅是训练集准确率，而是学到 trial-and-error / 纠错 / 回溯等可泛化策略（§2.3.2 末段）。

### 3.3 Long context scaling + Partial Rollout（§1；§2.6.2；§3.3）

| 项 | 报告 |
|---|---|
| RL 上下文 | 缩放到 **128k**；硬推理基准上仍见持续提升（§3.3） |
| Partial rollout | 固定每轮 **output token budget**；超长轨迹截断写入 replay buffer，**下一 iter 续写**；历史段可复用，仅当前段需 on-policy 计算；可对部分段 **排除 loss** |
| 副产品 | 异步 worker 长短轨迹混跑；**repeat detection** 早停 + 可加惩罚 |
| 小模型缩放观察（Figure 5–6） | mid-sized / 更小 internal long-cot 上：response length 与 accuracy 同升；最终 k1.5 run 扩到 128k |

### 3.4 Long2short（§2.4；§3.4）——把长思维先验压回短 CoT

| 方法 | 做法（报告原文级） |
|---|---|
| Model merging | long-cot 与 short-cot **权重平均**，免训练 |
| Shortest rejection sampling | 同题采样 **$n=8$**，取**最短正确**答做 SFT |
| DPO | 最短正确为正；更长错误 + 正确但 ≥ **1.5×** 正样本长度的长答为负 |
| Long2short RL | 标准 RL 后另开一阶段：启用 §2.3.3 length penalty，并 **显著减小 max rollout length** |
| 亮点数字（Figure 7 文） | **k1.5-short w/ rl**：AIME2024 Pass@1 **60.8**（8 次平均），平均仅 **3,272** tokens |

### 3.5 预训练 / Vanilla SFT 公开骨架（§2.5；Appendix B）——有数字才录

| 项 | 报告 |
|---|---|
| 预训练三阶段 | (1) Vision-language pretraining（先纯语言 → 逐步多模态；视觉塔先单独训，再解冻 LM，最终 vision-text 占比 **30%**）→ (2) Cooldown（高质量 + 合成 QA）→ (3) Long-context activation |
| 长上下文激活 | 最大长度 **4,096 → 32,768 → 131,072**；**40% full attention + 60% partial attention**；RoPE frequency **1,000,000** |
| 架构披露边界（B.3） | 「variant of Transformer decoder」+ 多模态；**scaling 实验细节超出本报告范围**，留待后续 |
| Vanilla SFT 规模 | 文本约 **1M**（QA 500k / code 200k / math+science 200k / creative 5k / long-context 20k）+ 视觉文本 **1M** |
| Vanilla SFT 调度 | 先 **32k × 1 epoch**（LR $2\times10^{-5}\to2\times10^{-6}$），再 **128k × 1 epoch**（re-warmup 到 $1\times10^{-5}$ 再降到 $1\times10^{-6}$）；例级 packing |

**明确未给出（勿编造）**：总参数量、层数、hidden dim、注意力变体名称、视觉塔结构、预训练总 token 数。

---

## 四、数学原理（§2.3 · 可对公式跟读）

### 4.1 问题设定与目标（§2.3.1）

- 数据 $D=\{(x_i,y_i^*)\}_{i=1}^n$；策略 $\pi_\theta$；CoT $z=(z_1,\ldots,z_m)$，答案 $y$。
- 奖励 $r(x,y,y^*)\in\{0,1\}$：可验证题用规则（如测例）；自由形式用奖励模型判匹配。
- 优化目标：

$$
\max_\theta\; \mathbb{E}_{(x,y^*)\sim D,\,(y,z)\sim\pi_\theta}\bigl[r(x,y,y^*)\bigr] \tag{1}
$$

### 4.2 Online policy mirror descent 变体（§2.3.2）

第 $i$ 轮以当前 $\pi_{\theta_i}$ 为 reference，解相对熵正则问题：

$$
\max_\theta\; \mathbb{E}_{(x,y^*)\sim D}\,\mathbb{E}_{(y,z)\sim\pi_\theta}\bigl[r(x,y,y^*)\bigr] - \tau\,\mathrm{KL}\bigl(\pi_\theta(x)\,\|\,\pi_{\theta_i}(x)\bigr) \tag{2}
$$

- 闭式：$\pi^*(y,z|x)=\pi_{\theta_i}(y,z|x)\,\exp(r/\tau)/Z$。
- Surrogate（平方残差；可 off-policy，采样来自 $\pi_{\theta_i}$）：

$$
L(\theta)=\mathbb{E}_{(x,y^*)\sim D}\,\mathbb{E}_{(y,z)\sim\pi_{\theta_i}}\Biggl[\Biggl(r-\tau\log Z-\tau\log\frac{\pi_\theta(y,z|x)}{\pi_{\theta_i}(y,z|x)}\Biggr)^2\Biggr]
$$

- $\tau\log Z$ 用 $k$ 条样本近似：$\tau\log Z\approx\tau\log\bigl(\tfrac{1}{k}\sum_j\exp(r_j/\tau)\bigr)$；实践上也可用 **经验均值奖励** $\bar r=\mathrm{mean}(r_j)$ 作 baseline（$\tau\to\infty$ 时 $\tau\log Z\to\mathbb{E}[r]$）。
- 每题 $k$ 条响应后的梯度（报告式 (3)）：

$$
\frac{1}{k}\sum_{j=1}^k \nabla_\theta\log\pi_\theta(y_j,z_j|x)\,(r_j-\bar r)\;-\;\frac{\tau}{2}\,\nabla_\theta\Biggl(\log\frac{\pi_\theta}{\pi_{\theta_i}}\Biggr)^2
$$

- 解读（报告原文）：形似带均值 baseline 的 policy gradient；差异在于 **off-policy 采样自 $\pi_{\theta_i}$** + **$\ell_2$ 正则 log-ratio**；每轮 reference 变了则 **reset optimizer**。
- **无 value network**：效率动机 + 假设——逐步 advantage 会惩罚「先错后纠」路径，而长 CoT 恰恰需要探索错误再恢复。

### 4.3 Length penalty（§2.3.3）

对同题 $k$ 条响应，$\mathrm{min\_len},\mathrm{max\_len}$ 为最短/最长；若相等则 length reward=0；否则

$$
\lambda=0.5-\frac{\mathrm{len}(i)-\mathrm{min\_len}}{\mathrm{max\_len}-\mathrm{min\_len}},\qquad
\mathrm{len\_reward}(i)=\begin{cases}\lambda & r_i=1\\ \min(0,\lambda) & r_i=0\end{cases}
$$

- 语义：正确答中奖短罚长；错误答中显式罚长。
- 与原奖励加权相加；训练初期 **warmup：先无 length penalty，再恒定启用**（防早期拖慢）。
- **加权系数具体数值：正文未给出** → 待核实。

### 4.4 采样与奖励侧配方（§2.3.4–2.3.5）

| 机制 | 要点 |
|---|---|
| Curriculum | 先易后难；初始 RL 模型在极难题上正确样本过少 |
| Prioritized | 跟踪成功率 $s_i$，按 **$1-s_i$** 比例采样 |
| Prompt 难度 proxy | SFT 模型高温答 **10** 次，pass rate 越低越难 |
| Easy-to-hack 过滤 | 无 CoT 猜答案，**$N=8$** 次内猜中则剔除；排除选择题 / 判断 / 证明题等易假阳性类型 |
| Coding 测例生成 | CYaRon；每题先 50 测例 × 10 参考提交；≥7/10 一致算 valid；再要求 ≥9/10 全过才入集；1000 题样本 → 323 题入训 |
| Math RM | Classic value-head ≈ **84.4** acc；**CoT RM ≈ 98.5**（人工抽检）；RL 采用 CoT RM；各约 **800k** 数据 |
| Vision RL 数据 | Real-world / Synthetic visual reasoning / Text-rendered 三类 |

---

## 五、训练 / 推理 Infra 公开要点（§2.6）

| 项 | 报告 |
|---|---|
| 框架 | 迭代同步 RL：rollout → replay buffer → train；中央 master 调度 |
| Hybrid 部署 | **Kubernetes Sidecar**：Megatron（训）与 vLLM（推）同 pod 共享 GPU；checkpoint-engine 管 vLLM 生命周期 |
| 权重路径 | Megatron 结束后 offload → 转 HF 格式进 shared memory（消掉 PP/EP，留 TP）→ **Mooncake** 经 **RDMA** 传权重 → vLLM 加载；结束后杀/重启 vLLM 以释放 CUDA graph / NCCL 等残留 |
| 切换时延 | 训→推 **&lt; 1 minute**；推→训约 **ten seconds** |
| 动态扩推 | 可在训侧不变时增加 inference 节点 |
| Code sandbox | K8s 服务；crun 替 Docker（启动 0.12s→**0.04s**）；cgroup reuse；overlay+tmpfs；16 核机容器/秒 27→**120** |

推理侧算法主张（相对 Infra）：部署保持自回归；能力来自训练期拉长上下文学到的规划行为，而非测时 MCTS。

---

## 六、摘要级能力锚点（非评测深挖）

### 6.1 Long-CoT（Table 2 / Abstract）

| 基准 | k1.5 long-CoT（报告） | 对照（表内） |
|---|---|---|
| MATH-500 (EM) | **96.2** | o1 94.8 |
| AIME 2024 (Pass@1) | **77.5** | o1 74.4 |
| Codeforces (Percentile) | **94** | o1 94 |
| LiveCodeBench (Pass@1) | **62.5** | o1 67.2 |
| MathVista-Test | **74.9** | o1 71.0 |
| MMMU-Val | **70.0** | o1 77.3 |
| MathVision-Full | **38.6** | QVQ-72B 35.9 |

### 6.2 Short-CoT（Table 3 / Abstract / Figure 7）

| 基准 | k1.5 short-CoT（报告） |
|---|---|
| AIME 2024 | **60.8** |
| MATH-500 | **94.6** |
| LiveCodeBench | **47.3** |
| MMLU / IF-Eval / CLUEWSC / C-Eval | 87.4 / 87.2 / 91.7 / 88.3 |

Appendix C 注明：Table 3 的 IF-Eval 来自 **intermediate** 模型，将更新——引用时需标注。

### 6.3 Ablation 定性结论（§3.5；不抄曲线点）

- 同数据不同规模：小模型可凭更长 CoT 追近大模型，但大模型通常更 token-efficient；追求上限仍宜对大模型扩上下文。
- 相对 ReST（无负梯度）：本方法 sample complexity 更好（Figure 10）。
- Curriculum（先混合 warmup，约 iter 24 后主攻难题）优于全程 uniform（Figure 9）。

---

## 七、待核实与引用

### 7.1 待核实（禁止当作已确认）

1. arXiv **首发 / v1–v3** 日期与 diff：本 PDF 仅见 **v4 · 3 Jun 2025**；写「首发日」需回查 https://arxiv.org/abs/2501.12599。
2. **模型参数量 / 层宽 / 视觉塔结构 / 预训练总 tokens**：正文与 Appendix B **明确未给**完整规模表；B.3 称架构 scaling「beyond the scope」。
3. 超参未公开数值：$\tau$、每题采样数 $k$、length penalty **加权系数**、RL 学习率 / batch、partial rollout 的具体 token budget。
4. LiveCodeBench 版本口径：摘要写 v 相关分数；Table 2/3 与 Figure 轴标签需逐表核对后再对外引用。
5. IF-Eval：Appendix C 承认 Table 3 数字来自 intermediate checkpoint。
6. 「up to +550%」相对 GPT-4o / Claude 3.5 的具体分母基准对：摘要口号级，精细对比应回到 Table 3 单格。
7. GitHub `MoonshotAI/Kimi-k1.5` 页面 README 与 PDF 是否始终同版：本卡以本地 arXiv v4 PDF 为准。
8. XMP 权利 **BY-NC-ND 4.0**；若后续另发权重，许可证以发布页为准（本 PDF 未写死 Apache 等）。

### 7.2 引用

- Kimi Team. *Kimi k1.5: Scaling Reinforcement Learning with LLMs* (Technical Report). arXiv:2501.12599v4 \[cs.AI\], 3 Jun 2025.
 PDF：https://arxiv.org/pdf/2501.12599
 本地：`https://arxiv.org/abs/2501.12599`
 （2026-09-22，Asia/Shanghai）

### 7.3 关联笔记

- [[KimiK2技术报告深读]]：模型与技术报告/厂商报告/KimiK2技术报告深读.md（下游继承：policy opt / partial rollout / colocated）
- [[对齐脉络RLHF与偏好优化]]：对齐与强化学习/对齐脉络RLHF与偏好优化.md（RLHF/DPO 通论）
- [[推理时扩展TestTimeScaling]]：架构/推理时扩展TestTimeScaling.md（测时缩放通论）
- [[DeepSeekR1推理训练深读]]：模型与技术报告/厂商报告/DeepSeekR1推理训练深读.md（同期推理 RL 对照）
- [[多模态架构脉络]]：多模态与具身/视觉语言/多模态架构脉络.md（多模态通论）

## 相关笔记

### 技术报告专项
- [[Grok4ModelCard|TR Grok 4 Model Cards]]
- [[Kimik15技术报告深读|TR Kimi k1.5]]
- [[KimiK2技术报告深读|TR Kimi K2]]
- [[Llama4待核实备忘|TR Llama 4 待核实备忘]]
- [[Mistral3公告短卡|TR Mistral / Ministral-3]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

