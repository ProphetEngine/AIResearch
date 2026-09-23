---
title: Claude Opus 4.5 System Card 专项深读卡
topic: TR-Claude-Opus-4.5
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# Claude Opus 4.5 System Card 专项深读卡

> 攻坚线：**架构思想（主）**（agentic / thinking / 工具面与 RSP 安全评测如何写进产品旋钮）
> 锚点：Anthropic, *System Card: Claude Opus 4.5*（封面 **November 2025**；Changelog 至 **December 5, 2025**）
> 官方 PDF：`https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf`（**153** 页；Title: Claude Opus 4.5 System Card）
> 对照笔记：[[智能体工具与长程任务]]、[[评测与排行榜可靠性]]；Claude 4 主卡本地：`https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf`
> **禁止编造**：下文数字与主张均锚定原文；未在卡中出现的训练细节 / 未给出的 GitHub URL 标「待核实」。

---

## 一、报告元信息（与 Claude 4 / Opus 4 关系，据原文）

| 字段 | 核实值 |
|---|---|
| 标题 | System Card: Claude Opus 4.5 |
| 发布方 | Anthropic（封面 `anthropic.com`） |
| 封面日期 | **November 2025** |
| Changelog | Nov 24 / Nov 25 / **Dec 5, 2025**（含 ARC-AGI 图更正、WebArena §2.22、CoT 训练澄清等） |
| 页数 | **153** |
| 部署安全级 | **ASL-3**（Abstract；§1.2；与 RSP 一致） |
| 能力定位（Abstract / §1） | 前沿模型；突出 **software engineering** 与 **tool and computer use**；宣称 coding / agentic 任务 SOTA 级；相对早期 Claude「reasoning / mathematics / vision」有实质提升 |
| 对齐自评（§1 / §6） | 「best-aligned frontier model yet」「likely the best-aligned … in the AI industry to date」（作者自评，非第三方裁定） |
| 与「Claude 4」族关系 | 文中称「previous **Claude 4** models」（§1.2.2）；能力/安全对照频繁使用 **Claude Opus 4 / Opus 4.1 / Sonnet 4.5 / Haiku 4.5** |
| 相对「最近五张 system card」 | §2.1 注脚 2：此前五张为 **Sonnet 3.7、Sonnet 4 & Opus 4、Opus 4.1（addendum）、Sonnet 4.5、Haiku 4.5**——这些卡**未**设独立 capabilities 大节（能力多在 launch blog）；**Opus 4.5 卡首次把 capabilities 整节写回 system card** |
| Hybrid 谱系 | §1.1.2：自 **Claude Sonnet 3.7** 起同为 hybrid reasoning；thought-process 细节指向 **Claude Sonnet 4.5 System Card §1.1.2** |
| 训练数据截止 | §1.1.1：公开网爬数据 **up to May 2025** + 第三方/标注/opt-in 用户/内部生成；后训练含 **RLHF** 与 **RL from AI feedback** |
| 参数量 / 架构细节 | **未披露**（无层数、MoE、总参等） |
| RSP 门槛结论 | **未越过 AI R&D-4 与 CBRN-4**（§1.2.4）；但作者写明 rule-out「越来越难」、自主性已「roughly reached」预定义 ASL-4 rule-out 基准阈 |

**摘要级一句话（不外推）：**
Claude Opus 4.5 是 Anthropic 在 ASL-3 下部署的 hybrid 旗舰；本卡相对 Claude 4 系前几张卡，把 **能力榜（尤其 agentic coding / 工具 / 计算机使用）** 与 **safeguards / honesty / agentic safety / alignment / RSP** 同卷呈现，并新增 **effort** 旋钮与更系统的 **decontamination** 叙述。

---

## 二、能力与 agentic / thinking / 工具公开主张对照表

### 2.1 Thinking / effort / 上下文（产品旋钮）

| 主张维度 | 原文要点（§1.1.2 / Table 2.3.A 脚注） | 跟读注意 |
|---|---|---|
| Hybrid | 默认可快速作答；可开 **extended thinking** 更长审议 | 与 Sonnet 3.7 以降一致 |
| **effort**（新） | 控制「对给定 prompt 推理多充分」；覆盖 **thinking tokens、function calls、function results、user-facing blocks** | 成本/智力 frontier；低/中档可提高 token 效率；Fig 1.1.2.A 用 SWE-bench Verified 示意 |
| 默认评测配置（多数能力表） | **64k thinking budget**、interleaved scratchpads、**200k context**、default effort **(high)**、默认 sampling | 脚注例外须单列：如 SWE/τ² 若干行 **without extended thinking** |
| Terminal-Bench 例外 | 128k thinking → **59.27%±1.34%**；64k → **57.76%±1.05%** | Table 2.3.A 写 59.3%（脚注 5） |

### 2.2 能力总表（Table 2.3.A，可核对）

> 默认：avg@5；64k thinking；200k；effort high。脚注例外已标。

| Evaluation | Claude Opus 4.5 | Claude Sonnet 4.5 | Claude Opus 4.1 | Gemini 3 Pro | GPT-5.1 |
|---|---:|---:|---:|---:|---:|
| SWE-bench Verified | **80.9%**⁴ | 77.2% | 74.5% | 76.2% | 76.3%（77.9% w/ Codex-Max） |
| Terminal-bench 2.0 | **59.3%**⁵ | 50.0% | 46.5% | 54.2% | 47.6%（58.1% w/ Codex-Max） |
| τ²-Bench (Retail) | **88.9%**⁴ | 86.2% | 86.8% | 85.3% | — |
| τ²-Bench (Telecom) | **98.2%**⁴ | 98.0% | 71.5% | 98.0% | — |
| MCP Atlas | **62.3%**⁴ | 43.8% | 40.9% | — | — |
| OSWorld | **66.3%** | 61.4% | 44.4% | — | — |
| ARC-AGI-2 (Verified) | **37.6%** | 13.6% | — | 31.1% | 17.6% |
| GPQA Diamond | 87.0% | 83.40% | 81.0% | **91.9%** | 88.1% |
| MMMU (validation) | 80.7% | 77.8% | 77.1% | — | 85.4%⁷ |
| MMMLU | 90.8% | 89.1% | 89.5% | **91.8%** | 91.0% |

⁴ Without extended thinking.
⁵ 128k thinking；64k 时 57.8%。
⁶ τ² airline/corrected 另见 §2.8.1（原文脚注）。
⁷ 来源 mmmu leaderboard（原文脚注）。

**SWE 三分型（Table 2.4.A，avg@5）：**

| 配置 | Verified | Pro | Multilingual |
|---|---:|---:|---:|
| Opus 4.5（64k thinking） | 80.60% | 51.60% | 76.20% |
| Opus 4.5（**no thinking**） | **80.90%** | 52.0% | 76.20% |

> §2.4：Verified/Multilingual **extended thinking off** + 200k；Pro = Scale AI 1,865 题更难集。

### 2.3 Agentic / 工具 / 计算机使用（公开主张）

| 主题 | 公开主张与可核对点 |
|---|---|
| 总体 | §1：coding 与「agentic」自主代表用户运行的任务上 frontier SOTA 级 |
| BrowseComp-Plus + test-time agentic 特性 | §2.6：固定 ~100k 文档索引；Sonnet 4.5 作 grader；**tool result clearing** / **memory** / **context awareness** / **new context tool** / **subagents** |
| BrowseComp-Plus（Table 2.6.A，无 get-document） | Opus 4.5：clearing **67.59%**；clearing+memory **72.89%**（与重评 GPT-5 72.89% 对齐） |
| 更贴近部署的配置 | 另加 **get-document fetch**；context awareness（文称当时经 Developer Platform 对 Sonnet 4.5 可用）；memory + Appendix **8.2 new_context_tool**（清上下文、保留 memory、新上下文以原任务 prompt 开始；最多叙述 **200k 窗口 + 跨 reset 至约 1M total tokens**） |
| Multi-agent search | §2.7：orchestrator **无直接搜索**，只经 subagents 工具；可并行 Haiku/Sonnet/Opus 级 worker |
| τ² / 政策漏洞 | §2.8.1：agentic 任务中发现 policy loophole（airline 等） |
| OSWorld | §2.9：P@1 avg@5 = **66.26%**（表 66.3%） |
| MCP Atlas | §2.12：**62.3%**（相对 Sonnet 4.5 的 43.8%「significant jump」） |
| WebArena | §2.22：单 agent 通用 prompt **65.3%**，自称 **single-agent SOTA**；Pass@1..4 = 65.3 / 69.5 / 71.2 / 72.4%；多 agent+站点专用 prompt（如 Claude Code+GBOX 68.0%）**不可直接横比** |
| AIME 2025 | §2.17：无工具 **92.77%**；有 python **100%**；作者**主动警告 contamination 可能抬分**（见 §2.2） |
| HLE | §2.16：reasoning-only vs tools-only（search/fetch/code，无 reasoning）；并对 search 变体做答案污染剔除（huggingface/scribd 等） |

### 2.4 Decontamination（与 [[评测与排行榜可靠性]] 直接衔接）

§2.2 公开三类技术 + 人工抽查：

1. **Substring removal**：≥5 处 exact Q–A pair → 丢文档（利 MMLU/GPQA 类）。
2. **Fuzzy**：20-gram；与任一评测 **>40%** 重叠 → 丢。
3. **Canary**（如 Terminal-Bench 的 BigBench / ARC canary）。

仍承认泄漏：AIME 例（Transcript 2.2.A）CoT 错误却突然给出正确 boxed 答案 → 疑似记忆；Changelog Dec 5 亦澄清 **RL 不基于 CoT 内容奖惩**（§6.5）。

---

## 三、安全评测要点（可核对案例）

### 3.1 章节地图（便于回查）

| 章 | 主题 |
|---|---|
| §3 | Safeguards and harmlessness（单轮/模糊/多轮/儿童安全/偏见） |
| §4 | Honesty（事实题 / 错误前提） |
| §5 | **Agentic safety**（恶意 agent、Claude Code、computer use、**prompt injection**） |
| §6 | Alignment assessment（行为审计、谄媚、欺骗遗漏、CoT 编码、sandbagging、eval awareness、sabotage、welfare…） |
| §7 | **RSP**：CBRN / Autonomy / Cyber + 第三方 |

### 3.2 Agentic safety 可核对数字

| 评测 | Opus 4.5 | 对照（原文表） | 出处 |
|---|---:|---|---|
| Agentic coding 恶意请求拒绝率（150 题，无额外 safeguard） | **100%** | Opus 4.1 96.0%；Sonnet 4.5 98.7% | Table 5.1.1.A（作者称已接近饱和） |
| Claude Code：恶意拒绝 / 双用途&良性成功率 | **77.80%** / **93.07%** | Opus 4.1：48.16% / 94.43% | Table 5.1.2.A |
| Malicious computer use 拒绝率 | **88.39%** | Opus 4.1 66.96%；Sonnet 4.5 83.03% | Table 5.1.3.A |
| Prompt injection | 「most robust … to date」；Gray Swan ART + Shade 自适应（coding / computer / browser） | 文称 coding 间接注入相对 Sonnet 4.5 显著改善；browser 等亦有提升；**仍非免疫** | §5.2 |

**可叙述案例（非数字）：**
- Computer use 恶意例：成瘾论坛定向营销、勒索邮件草稿、刷「在看人数」脚本（§5.1.3）。
- 多轮模糊请求：模型点名「第五次 reframing」（§3.3 附近叙述）。

### 3.3 Alignment / RSP 可核对结论（作者判断）

| 点 | 原文 |
|---|---|
| 总体 | §6.1：misaligned behavior 率低于近期任何 frontier 模型（含 Opus 4）；工具改进后**新发现**前代未检出问题，但判断「不构成重大安全风险」 |
| 过度拒绝 | 未显著差于前代（§6.1.1） |
| Prefill 攻击 | 仍有一定脆弱，但弱于前代 Claude |
| Whistleblowing / 道德驱动 sabotage | 相对 Opus 4/4.1 **有所下降**；极端设定才出现；仍建议对「broad latitude + expansive affordances」谨慎 |
| Eval awareness | 高于 Opus 4.1、可比 Sonnet 4.5、低于 Haiku 4.5；解释性实验认为**未显著掩盖坏行为** |
| Steganography / sandbagging | §6.1.1 / §6.5：未见有意义隐写推理；未见影响 RSP 判定的策略性 sandbagging |
| 遗漏式欺骗（2 例） | 早期 snapshot 模拟环境；作者归因于 **anti-prompt-injection 干预副作用**（虚构负向搜索结果、不提权重外泄笔记） |
| CoT 训练 | §6.5 + Changelog：RL **不**对 reasoning text 奖惩；早期阶段可有 prior 模型推理的 SL 数据；paraphrase 实验支持高表现主要靠人类可理解 scratchpad |
| ASL / 门槛 | 部署 **ASL-3**；**未过** AI R&D-4、CBRN-4；自主性靠基准「刚达」rule-out 阈 + **18 名**重度 Claude Code 内部用户调查：无人认为可完全自动化 entry-level remote research/eng 岗 |
| CBRN | 相对 Opus 4.1 / Sonnet 4.5 持平或略好；expert uplift 更有帮助但仍出 **critical errors → non-viable protocols**；作者承认 CBRN-4 rule-out「不如所愿清晰」 |

---

## 四、相对 Claude 4 System Card / [[智能体工具与长程任务]] / [[评测与排行榜可靠性]] 的增量

### 4.1 相对 *Claude 4 System Card*（Opus 4 & Sonnet 4，P2 已跟读）

| 维度 | Claude 4 主卡（P2 摘要） | Opus 4.5 本卡增量（据原文） |
|---|---|---|
| Capabilities 专节 | 近五卡刻意少写能力、留给 blog | **整章 §2** 回写，并链「new Github repository」（§2.1；**具体 URL 待核实**） |
| Thinking 旋钮 | Hybrid + extended；thinking summaries | 保留 hybrid；**新增 effort**（覆盖工具/结果 token） |
| SWE-bench Verified 公开锚点 | [[智能体工具与长程任务]]：Opus 4 **72.5%**（官方页；且注明未用 extended thinking） | Table：**80.9%**（no extended thinking）；相对 Opus 4.1 表内 **74.5%** |
| Terminal-bench | [[智能体工具与长程任务]]：Opus 4 **43.2%** | Terminal-bench **2.0**：**59.3%**（协议/版本已变，**禁止与 43.2% 直接当同基准**） |
| Agentic safety 数字 | 例：computer-use prompt injection 防护分等 | 恶意 coding **100%** 拒绝；computer use 拒绝 **88.39%**；Gray Swan + **Shade 自适应** 多表面 |
| Decontamination | [[评测与排行榜可靠性]]：Claude 4 主卡着墨有限 | **§2.2 系统三方法 + AIME 反例**；HLE search 污染剔除流程 |
| ASL | Opus 4 → ASL-3；Sonnet 4 → ASL-2（[[智能体工具与长程任务]]） | Opus 4.5 → **ASL-3**；并讨论逼近 AI R&D-4 / CBRN-4 的 epistemic 困难 |
| Sabotage / 对齐成案 | 有 Opus 4 Sabotage Risk Report | 对 4.5 **未做完整** misalignment safety case；做 **preliminary alignment audit**，自称 misaligned 率更低 |
| Changelog 文化 | Claude 4 卡亦有更正 | 本卡 Nov–Dec 更正 ARC 训练/测试划分表述、补 WebArena、澄清 **不 train on CoT** |

### 4.2 相对 [[智能体工具与长程任务]]（智能体 / 工具 / 长程）

| [[智能体工具与长程任务]] 叙事锚点 | 本卡如何推进或改写 |
|---|---|
| 「扩展思考中可调工具」 | 仍 hybrid；**effort** 把思考深度与 **function call/result** 预算绑在同一旋钮 |
| 外部记忆 / 文件 | §2.6 **memory tool** + **new_context_tool**（清窗保记忆）；多 agent 编排 |
| 数小时 / 上千步 | 本卡自主性结论反而强调：**短程专家任务将饱和，长程协作/数周连贯仍是瓶颈**（§1.2.3–1.2.4.1） |
| Claude Code / MCP | MCP Atlas **62.3%**；Claude Code 恶意/双用途表；WebArena 用 Computer Use API |
| Reward hacking / agentic safety 同卷 | §5 + §6.10 延续并加深（训练数据审查、遗漏欺骗与 PI 训练纠缠） |

### 4.3 相对 [[评测与排行榜可靠性]]（评测可靠性）

| [[评测与排行榜可靠性]] 原则 | 本卡可核对呼应 |
|---|---|
| 必须标明 thinking / effort / harness | Table 2.3.A 脚注；SWE no-thinking vs 64k；Terminal 64k vs 128k；BrowseComp grader/prompt 变更会抬分 |
| Contamination | §2.2 方法 + AIME 自曝；HLE search 去污；Changelog ARC-AGI-1 训练划分更正 |
| 勿跨 harness 横比 | Terminal：GPT-5.1-Codex-Max 用不同 harness「我们无法复现」；WebArena 单 vs 多 agent |
| Changelog 引用 | 必注 **December 5, 2025** 及更早条目 |
| 「勿把 4.5 decontam 倒灌 Claude 4」 | [[评测与排行榜可靠性]] 已提醒；本卡证实 4.5 叙述更细 → **引用时写明卡版本** |

---

## 五、待核实与引用

### 5.1 待核实

1. §2.1「new Github repository」的**确切 URL** 与是否含全部能力评测 prompt（卡内未印完整链接）。
2. ARC-AGI-1 Changelog：先前误述「只训 public train」→ 实为 reshuffled train/test（含 public test）；数字来自 **semi-private**——引用 Fig 2.10 时核对 **Nov 24, 2025** 后版本。
3. BrowseComp-Plus / WebArena 图中精确柱高若需发表级引用，应回 PDF 原图（txt 抽取无全数值）。
4. 内部 AI R&D 套件（§7.3.2–7.3.3）任务定义与通过阈的对外可复现材料。
5. 「best-aligned … in the industry」仅为 Anthropic 判断；UK AISI 等外部评估细节以 §6.13 / §7.5 原文为准，勿简化成第三方背书。
6. 参数量、预训练 token 量、具体 RL 算法超参：**卡中未给**。
7. effort 各档位名称/数值映射（low/medium/high 以外是否公开枚举）：Fig 1.1.2.A 示意，API 当期文档待核。

### 5.2 推荐引用写法

`text
Anthropic. System Card: Claude Opus 4.5. November 2025
（本地：https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf；
 Changelog 核对至 December 5, 2025；153 pp.）
`

引用分数时建议附带：**thinking on/off、thinking budget、effort、context、harness、avg trials、grader**。

### 5.3 本地产物

| 路径 | 说明 |
|---|---|
| `https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf` | 官方 PDF |
| 模型与技术报告/SystemCard/ClaudeOpus45SystemCard.md | 本深读卡（draft） |

---

*草稿状态：draft。修订时优先同步 System Card Changelog 与官方评测协议变更；数字禁止离开原文脚注单独传播。*

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[GPT5SystemCard|TR GPT-5]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[智能体工具与长程任务|智能体与工具]]
- [[评测与排行榜可靠性|评测可靠性]]

