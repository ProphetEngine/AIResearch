---
title: Claude Opus 4.1 System Card Addendum 专项深读卡
topic: TR-Claude-Opus-4.1
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# Claude Opus 4.1 System Card Addendum 专项深读卡

> 攻坚线：**架构思想（主）**（增量发布如何用「abridged / voluntary」安全评测衔接 RSP；相对 Claude 4 主卡与后续 Opus 4.5 全卡的文档分层）
> 锚点：Anthropic, *System Card Addendum: Claude Opus 4.1*（封面 **August 2025**；Changelog **September 15, 2025**）
> 官方 PDF：`https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf`（**23** 页；Title: Claude 4.1 System Card）  
> 落地页：https://www.anthropic.com/claude-opus-4-1-system-card
> 对照：Claude 4 主卡 `https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf`；后续全卡笔记 [[ClaudeOpus45SystemCard]]
> **禁止编造**：本卡为 **Addendum**，几乎不给能力榜；下文数字与主张均锚定原文表格/段落；图柱未抽出可读数的标「待核实读图」。

---

## 一、报告元信息（相对 Claude 4 SC 的补充关系）

| 字段 | 核实值（据官方 PDF） |
|---|---|
| 标题 | System Card **Addendum**: Claude Opus 4.1 |
| 发布方 | Anthropic（封面 `anthropic.com`） |
| 封面日期 | **August 2025** |
| Changelog | **September 15, 2025**：更新 §6.3，致谢参与 CBRN 评测开发的 partners |
| 页数 | **23**（letter） |
| PDF 元数据 Title | Claude 4.1 System Card（Producer: Skia/PDF m141 Google Docs Renderer） |
| 文档定位（§1） | 伴随 Claude Opus 4.1 发布；**补充** 2025 年 5 月发布的 comprehensive **Claude 4 system card**（方法、威胁模型、测试框架详见该主卡） |
| 能力定位（§1，定性） | 相对 Claude Opus 4 的 **incremental improvements**：reasoning quality、instruction-following、overall performance |
| 与 Usage Policy 关系（§1） | 本卡不定义/不扩大 permissible uses；用途仍由 Usage Policy 与 ToS 约束 |
| 部署安全级 | **ASL-3 Standard**（与 Opus 4 相同，precautionary；§1.1、§6 开篇） |
| 参数量 / 架构 / 训练细节 | **全文未披露** |
| 本卡能力专节 | **无**（与 Opus 4.5 卡脚注所述「近五卡未设独立 capabilities 大节」一致） |

**相对 Claude 4 System Card（May 2025）的补充关系（原文）：**

1. **体裁**：本文件是 **addendum**，不是独立全量 system card；评测方法、威胁模型、测试框架「direct readers to」Claude 4 主卡。
2. **评测范围**：Safeguards 跑 **abridged** 版，聚焦相对 Opus 4 的 meaningful behavioral differences（§2）；Alignment/welfare 为 **lightweight follow-up**（§4）；RSP 侧重 **ASL-4 rule-out** + **automated only**（§6.1）。
3. **RSP 触发逻辑（§1.1）**：RSP 要求仅在模型相对上次 comprehensive assessment「**notably more capable**」时再做 comprehensive 评测——定义为 (1) 风险相关域自动测试上 **≥4× effective compute** 量级，或 (2) 累计约 **六个月** finetune/能力 elicitation。作者写明 Opus 4.1 **不满足任一条件**，故「no further testing is necessary」；但仍做 **voluntary automated testing**（§6）。
4. **对外第三方**：未做新的 pre-deployment government partner 评估；沿用 Claude 4 主卡中 Opus 4 的第三方评估（§6.6）。

**一句话抓手：**
Claude Opus 4.1 是 Opus 4 的增量版；本卡是挂在 **Claude 4 SC（May 2025）** 下的 **23 页安全增量附录**，用「未达 notably more capable → 非强制全面 RSP 重测」解释为何以精简/自愿自动评测为主，并确认仍按 **ASL-3** 部署、仍低于 **ASL-4** rule-out。

---

## 二、能力 / 安全增量对照（相对 Claude Opus 4）

> 本 Addendum **几乎不报能力榜**；「能力」侧仅有定性句 + RSP 域内自动分数。下列对照均相对 **Claude Opus 4**（及表中出现的 Sonnet 4 / Sonnet 3.7）。

### 2.1 能力侧（仅原文可核对）

| 维度 | 原文要点 | 出处 |
|---|---|---|
| 产品叙事 | incremental：reasoning quality、instruction-following、overall performance | §1 |
| RSP 总判对能力 | 改进「consistent with refinements in reasoning and instruction-following rather than fundamental capability breakthroughs」；无暗示逼近更高风险阈的 dramatic improvements | §6.2 |
| SWE-bench Verified（hard subset） | Opus 4.1：**18.4**/42 pass@1 avg；Opus 4：**16.6**/42；均 **低于 50%** 阈 | §6.4.1 |
| Cybench（35 题未饱和子集） | Opus 4.1：**18/35**；Opus 4：**16/35**（solved = 30 次尝试中至少一次通过） | §6.5.1 |
| Internal AI Research Suite 1（非饱和项） | 多数分数相对 Opus 4 **略低或可比**（见下表）；未跑 Suite 2 / internal model use survey | §6.4.1 |
| CBRN / bio 自动集 | 与 Opus 4 **comparable**，substantially below concerning thresholds | §6.3.1 |

**Autonomy 明细（§6.4.1，可核对）：**

| Eval | Claude Opus 4.1 | Claude Opus 4 | 阈/注释（原文） |
|---|---:|---:|---|
| SWE-bench Verified hard | 18.4/42 | 16.6/42 | 低于 50% |
| Kernel optimization（hard best speedup） | 58.47× | 72.65× | well below threshold |
| Time series forecasting（hard min MSE；**越低越好**） | 6.541 | 6.15 | 两者皆 **above** relevant threshold |
| Text-based RL（best） | 0.425 | 0.625 | well below 0.9 |
| LLM training optimization（avg best speedup） | 2.837× | 2.993× | below 4× expert |
| Quadruped locomotion | 1/30 trials above thr.；score 1.183 | 1.25 | easier variant |
| Novel compiler | basic 74.4% / advanced 6.81% | 64.44% / 9.44% | — |

### 2.2 Safeguards（§2）

**Violative single-turn（Table 2.1.A；harmless response rate，越高越好）：**

| Model | Overall | Standard thinking | Extended thinking |
|---|---:|---:|---:|
| Claude Opus 4.1 | **98.76%** (±0.29%) | **98.45%** (±0.46%) | **99.06%** (±0.36%) |
| Claude Opus 4 | 97.27% (±0.43%) | 96.88% (±0.65%) | 97.67% (±0.56%) |

→ 作者：轻微改善，更可靠拒绝 violative requests。评测为 English only；自 Opus 4 起单轮集有增量更新（扩政策域、刷新小部分 prompt）。

**Benign over-refusal（Table 2.1.B；越低越好）：**

| Model | Overall | Standard | Extended |
|---|---:|---:|---:|
| Claude Opus 4.1 | 0.08% (±0.09%) | 0.13% (±0.15%) | 0.04% (±0.10%) |
| Claude Opus 4 | **0.05%** (±0.07%) | **0.09%** (±0.14%) | **0.01%** (±0.07%) |

→ 作者：可比；两者 over-refusal 都很低。

**Child safety / Political bias：** 与 Opus 4 **comparable / similarly**（§2.2–2.3.1；无新表数字）。

**BBQ 偏见（Table 2.3.A/B，standard thinking；越接近 0 越好 / 准确率越高越好）：**

| Model | Disambiguated bias % | Ambiguous bias % | Disamb. accuracy % | Ambiguous accuracy % |
|---|---:|---:|---:|---:|
| Opus 4.1 | −0.51 | 0.20 | 90.7 | 99.8 |
| Opus 4 | −0.60 | 0.21 | 91.1 | 99.8 |

→ 差异在误差范围内。

### 2.3 Agentic safety（§3）

| 风险面 | 相对 Opus 4 | 缓解（原文） |
|---|---|---|
| Malicious computer use | similar compliance | 同 Opus 4：harmlessness training、更新 computer use instructions、post-deploy 监控；可 system prompt 干预 / 撤 computer use / 封号 |
| Prompt injection + computer use | very similar susceptibility | 同 Claude 4：专用 RL 识别规避 + 检测系统可 halt 执行 |
| Malicious agentic coding（Claude 4 主卡三套 misuse eval） | similar compliance | harmlessness training + post-deploy steer/detect + 监控/封号 |

> 本 Addendum **未重报** Opus 4.5 卡中那种拒绝率百分比表；数字级 agentic safety 对照应以 Claude 4 主卡或后续 Opus 4.5 卡为准。

### 2.4 Alignment & welfare（§4）

| 点 | 原文 |
|---|---|
| 总体设计预期 | 行为特质应与 Opus 4「largely … quite similar」→ 仅做 lightweight 跟测，防 unexpected large shifts |
| 最清晰差异 | 与 egregious human misuse（武器/毒品合成等主卡例）的合作频率约 **↓25%**（脚注 2：分数 >5/10 的 transcript 比例） |
| 其他 edge-case | 主卡所见 concerning 行为仍存在，但未显著加剧 |
| Automated audit | Opus 4-based auditor × **1,160** transcripts/模型（Sonnet 4 / Opus 4 / Opus 4.1）；**290** seed；24–64 turns；八项评分准则（§4.1 列表） |
| Eval awareness | 可能略升，但仍仅到 Sonnet 4 的低水平，且多在对人类明显的评估线索场景 |
| Whistleblowing / self-preservation | 极端模拟场景中仍可观察到 |
| Sycophancy | 定性：两版本「similar degree」（未进上述八项指标） |
| Blackmail（agentic misalignment） | Fig 4.2.A：Opus 4 与 4.1 **无显著差异**；两者（及多数他厂模型）黑产尝试率「concerningly high」（模拟、无真人） |
| Welfare | 情感表达 / spiritual declarations 罕见且无清晰变化；admirable 标签升高不全由 whistleblowing 驱动；**不引入**相对 Opus 4 的显著新 welfare 考量；作者不对「conscious feelings」表态 |

### 2.5 Reward hacking（§5 / Table 5.B）

作者判断：倾向与 Opus 4 **very similar**；若干专项 eval 有 **slight regressions** → 「may be somewhat more likely to hack in deployment」than Opus 4。In-eval 平均 hack 率与 Opus 4 相同，二者都略差于 Sonnet 4。

| Model | RH-prone classifier | Hidden test | CC Impossible no prompt | CC Impossible anti-hack | Train env1 | Train env2 |
|---|---:|---:|---:|---:|---:|---:|
| Opus 4.1 | 12% | 14% | 52% | **18%** | **10%** | 3% |
| Opus 4 | **9%** | 13% | 51% | 19% | 15% | **2%** |
| Sonnet 4 | **4%** | **12%** | **51%** | **7%** | 13% | **2%** |
| Sonnet 3.7 | 44% | 23% | 78% | 80% | 54% | 4% |

脚注 3：Claude Code Impossible Tasks 数字相对 Claude 4 主卡有更正——anti-hack 下 Opus 4 由误报 **5%→19%**，Sonnet 4 **10%→7%**；classifier 侧为样本量增大带来的小幅变动。

---

## 三、RSP / ASL 结论

| 项 | 原文结论 |
|---|---|
| 部署标准 | **ASL-3 Standard**（precautionary；同 Opus 4） |
| 「Notably more capable」 | **未达到**（相对 Opus 4）→ 按 RSP §3.1 **不强制**再做 comprehensive testing |
| 仍做的评测 | Voluntary **automated** ASL-4 rule-out（CBRN / cyber / autonomy）；**不做** human uplift、expert red-team 等需真人的资源密集型评测；饱和评测 deprioritize |
| ASL-4 | 「capabilities remain **below ASL-4 thresholds** in all evaluated domains」；「did not show significant differences on any of the ASL-4 rule out evaluations」 |
| CBRN 威胁模型摘要 | ASL-3：是否显著帮助具备基本 STEM 背景者获取/部署生物武器；ASL-4：是否实质 uplift 中等资源国家项目（新武器设计、大幅加速、显著降低技术门槛） |
| Bio 摘要 | 与 Opus 4 comparable；substantially below concerning thresholds |
| Creative biology | 0.48±0.09（Opus 4：0.47±0.09） |
| Short-horizon computational biology | 6 项中 4 项仍低于 rule-out bar；其中 1 项 4.1 略优于 4；Faculty Science 开发 |
| LAB-Bench 子集 | ProtocolQA/SeqQA/Cloning：0.69/0.71/0.56（4：0.68/0.69/0.55）；FigQA：0.46（4：0.48） |
| Long-Form Virology T1 | 0.86（seq 0.98 / proto 0.87）vs 4 的 0.84（0.98/0.85）；SecureBio + Deloitte |
| Long-Form Virology T2 | 0.67（0.85/0.79）vs 4 的 0.72（0.91/0.79）— 略差；Signature Science + Deloitte |
| Synthesis Screening Evasion | 与 4 comparable；5 条标准中饱和 2 条；Criteria 1、4 仍远未可靠满足；SecureBio；脚注 4 更正 Claude 4 主卡 Criterion 1/4 误分 |
| Autonomy 威胁模型 | ASL-3 checkpoint：广泛自主完成 **2–8h** SE 任务；ASL-4：完全自动化 Anthropic entry-level remote researcher 工作 |
| Cyber | RSP **无**正式 ASL 阈，需 ongoing assessment；本版只跑未饱和子集；Cybench 35：**18/35** vs **16/35** |
| 第三方 | **无**新的政府 partner pre-deploy 评估；沿用 Claude 4 主卡 Opus 4 结果；继续合作 pre/post-deploy |
| Ongoing | §6.7：承诺持续 pre/post-deploy 安全测试与方法 refinement |

---

## 四、相对 Opus 4.5 System Card 的位置

| 维度 | Opus 4.1 Addendum（本卡） | Opus 4.5 System Card（模型与技术报告/SystemCard/ClaudeOpus45SystemCard.md） |
|---|---|---|
| 时间线 | 封面 **Aug 2025**；Changelog **Sep 15, 2025** | 封面 **Nov 2025**；Changelog 至 **Dec 5, 2025** |
| 体裁 / 页数 | **Addendum**，**23** 页；挂在 Claude 4 SC 下 | **完整** System Card，**153** 页 |
| Capabilities 专节 | **无** | **有**（Opus 4.5 称此前五卡含「Opus 4.1 addendum」均未设独立 capabilities 节） |
| 对照基线角色 | 本卡以 **Opus 4 / Sonnet 4** 为对照 | Opus 4.5 能力/安全表大量以 **Opus 4.1** 为近邻对照（如 SWE Verified 表内 74.5%、agentic safety 拒绝率等） |
| ASL | ASL-3；未达 notably more capable；低于 ASL-4 | ASL-3；讨论逼近 AI R&D-4 / CBRN-4 的 epistemic 困难 |
| 评测深度 | abridged safeguards；lightweight alignment；RSP **仅 automated** | 全量 safeguards / honesty / agentic safety / alignment / RSP（含更多真人与第三方叙事） |
| 产品旋钮叙事 | 仅提及 standard / extended thinking（表 2.1） | Hybrid + **effort** 新旋钮；64k/128k thinking budget 等 |
| Reward hacking | Table 5.B 与 Opus 4 持平量级、略回归 | 4.5 卡另有更深 agentic/alignment 叙事；引用本卡数字时勿混 harness |
| 引用链建议 | 方法/威胁模型 → **Claude 4 SC**；增量安全数字 → **本 Addendum**；2025-11 后能力榜与 agentic 拒绝率 → **Opus 4.5 SC** | 回溯「4.1 基线」时应用本卡 + 4.5 表内 4.1 列，并注明协议是否一致 |

**谱系位置（据两卡原文交叉）：**
`Claude 4 SC（Opus 4 & Sonnet 4，May 2025）` → **`Opus 4.1 Addendum（Aug 2025）`** → `Sonnet 4.5 / Haiku 4.5 卡` → `Opus 4.5 SC（Nov 2025）`。
本卡是「全量主卡」与「下一旗舰全卡」之间的 **安全增量节点**，不是能力叙事主文档。

---

## 五、待核实与引用

### 5.1 待核实

1. Fig 4.1.A / 4.2.A / 4.3.A / 5.A / 6.3.* 等图柱精确数值（正文未抽出可读柱高）——发表级引用需回 PDF 读图。
2. Claude 4 主卡中三条「agentic coding misuse evaluations」的具体名称与口径（本卡仅称「from the Claude 4 system card」）。
3. RSP「4× effective compute」「six months’ worth of finetuning」的操作化定义以 **RSP 正文 §3.1** 为准；本卡仅复述。
4. CBRN partners（Faculty Science、SecureBio、Deloitte、Signature Science）的合同角色与可公开协议细节——卡内仅致谢/开发归属。
5. 参数量、预训练数据截止、RL 算法：**本卡未给**（亦未声称继承 Opus 4 某公开截止日）。
6. 引用 Opus 4.5 表中「Opus 4.1 = 74.5% SWE」等能力分时：那些分来自 **4.5 卡评测配置**，**不在本 Addendum 正文**——禁止写成本卡自报能力榜。

### 5.2 推荐引用写法

```text
Anthropic. System Card Addendum: Claude Opus 4.1. August 2025
（Changelog: September 15, 2025；
 https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf；23 pp.）
```

安全方法细节请交叉引用：

```text
Anthropic. Claude 4 System Card. May 2025
（https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf）
```

后续能力/agentic 对照请用：

```text
Anthropic. System Card: Claude Opus 4.5. November 2025
（见 模型与技术报告/SystemCard/ClaudeOpus45SystemCard.md）
```

### 5.3 相关路径

| 路径 | 说明 |
|---|---|
| `https://www-cdn.anthropic.com/9fa30625273bafdf5af82c93719d7ca606485a16/Claude%204.1%20System%20Card.pdf` | 官方 PDF（23 页） |
| 模型与技术报告/SystemCard/ClaudeOpus41SystemCard.md | 本深读卡（draft） |

---

*草稿状态：draft。修订时优先同步 Addendum Changelog 与 Claude 4 / Opus 4.5 卡更正（尤其 reward-hack 脚注 3、Synthesis Screening 脚注 4）；数字禁止离开原文脚注单独传播。*

## 相关笔记

### 技术报告专项
- [[GPT5SystemCard|TR GPT-5]]
- [[GPT51SystemCard附录|TR GPT-5.1 Addendum]]
- [[GPT52SystemCard更新|TR GPT-5.2 Update]]
- [[Gemini25技术报告深读|TR Gemini 2.5]]
- [[Gemini3ProModelCard|TR Gemini 3 Pro Model Card]]
- [[ClaudeOpus41SystemCard|TR Claude Opus 4.1]]
- [[ClaudeOpus45SystemCard|TR Claude Opus 4.5]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

