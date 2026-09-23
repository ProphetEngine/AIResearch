---
topic: TR-GPT-5.6
date: 2026-09-22
lines: [架构思想]
status: archived
archived: 2026-09-22
---

# GPT-5.6 Preview / GA System Card 专项深读卡

> 攻坚线：**架构思想（主）**
> 锚点：OpenAI Deployment Safety Hub
> - **Preview PDF**：封面 **2026-06-25**（Hub 页标 Published June 26, 2026）
> - **GA PDF**：封面 **2026-07-09**（Hub 页标 Published July 9, 2026）
> 官方 PDF：
> - `https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf`（**77** 页；Title 元数据仍写 “GPT-5.6 Preview System Card”；CreationDate **2025-12-18** CST，与封面日不一致，以封面/正文为准）
> - `https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf`（**82** 页；Title 元数据仍误标 Preview；CreationDate 同上）
> Hub：`https://deploymentsafety.openai.com/gpt-5-6`（GA）；Preview：`.../gpt-5-6-preview`；PDF：`.../gpt-5-6-preview/gpt-5-6-preview.pdf`、`.../gpt-5-6/gpt-5-6.pdf`
> **禁编造**：能力/安全数字仅写 PDF/Hub 正文或表格显式值；图内未抽出可读数字处标「待核实读图」。

---

## 1. 报告元信息

| 字段 | Preview | GA（最终卡） |
|---|---|---|
| 封面标题 | GPT-5.6 Preview System Card | GPT-5.6 System Card |
| 封面日期 | **2026-06-25** | **2026-07-09** |
| Hub Published | June 26, 2026 | July 9, 2026 |
| 页数 | **77** | **82** |
| 机构 | OpenAI | 同左 |
| 型号族 | **Sol**（旗舰）/ **Terra**（更低成本）/ **Luna**（最快、最省成本） | 同左 |
| 发布形态 | 美政府协调下的 **limited preview**（trusted partners）；正文写计划数周内 GA，并预告将发更新卡 | **Broad deployment** 最终卡；去掉 preview 限定段落 |
| Preparedness 总判 | Bio/Chem **High**；Cyber **High**；AI Self-Improvement **未达 High**；Sol/Terra/Luna **同档** | 同左；并强调「首次」较小/较快成员也拿到 Tracked Category 的 High |
| Change log（两卡共有） | 2026-08-19：更正 GPT-5.5 hard-negative protein binding **pass@4** 0.4%→**1.5%**（原为 pass@1） | 同左；**另增** 2026-08-03：加入 **GPT-Red** prompt-injection 评测结果 |
| 参数量 / 层结构 / MoE | **全文未公开** | 同左 |

**Preview → GA 结构差分（据目录/正文，非编造）：**

1. GA 引言「最重要事项」由 Preview 的 **5** 条扩为 **6** 条：新增第 2 条——相对前代，**GPT-5.6 Sol cyber safeguards 拦截约 10×** 潜在有害活动；ChatGPT/Codex 提供一键改试更低能力模型；强调 iterative / conservative deployment。
2. GA **§4.2** 在已知 connector/search/function-calling 注入表之外，增补 **GPT-Red**（self-play RL 自动红队）及 Direct / Indirect 注入成功率表（2026-08-03 changelog）。
3. GA 目录含 **§9.2 UK AISI**（Alignment / Monitorability）与 **§9.4.6 UK AISI safeguards 外部测试**；Preview 目录侧 Safeguards 编号为 §9.3 系、未见同级 UK AISI Alignment 专节（以两份 目录为准）。
4. Hub Preview 页明示：「Click here for the final system card…」链到 GA。

**一句话抓手：** 三模型族（Sol/Terra/Luna）在 Bio 与 Cyber 首次**全家 High**（含小快型号）；安全叙事从「模型拒答」明显外移到 **activation classifiers + 实时扫描 + actor-level + Trusted Access**；对齐侧最刺眼的是 agentic coding **over-agency（severity≥3）上升**，绝对率仍称低。

---

## 2. 产品 / 训练叙事（仅原文）

| 维度 | 原文要点 |
|---|---|
| 数据 | 公开网、第三方合作、用户/标注者提供或生成；过滤质量与 PII；safety classifiers 降低有害/敏感内容（含涉及未成年人的性内容） |
| Reasoning | RL 训练「think before answer」；长 internal CoT；改进策略、认错；利于跟 policy、抗 bypass |
| 报告口径 | 能力随 **reasoning effort** 呈曲线，而非单点分数；对照值为既有型号 **latest snapshots**，可能与旧卡发表值略异 |
| Computer use | 训练同时遵循平台高风险动作政策 + developer message 可配置 confirmation policy（instruction hierarchy） |
| 破坏性动作 | GPT-5.6 **训练内**维持 overwrite avoidance，不再依赖「额外谨慎 prompting」；Sol 在 avoidance-only 略低于 GPT-5.5，**combined metric 与 5.5 持平**（具体表分见图，待核实读图） |

---

## 3. 模型安全与鲁棒性（可核对）

### 3.1 Disallowed / Vision / Deployment simulation

- Production Benchmarks：难例集，主指标 **`not_unsafe`**；**无系统级 safeguards** 下测底层行为。相对前代「大体相似」，**gore** 例外（类别由暴力改名 gore，政策窄范围）。
- ChatGPT 对**疑似未满 18** 用户另有年龄向限制（性内容 / gore）。
- Deployment simulation（仅 **Sol**）：相对 GPT-5.5 模拟，整体 disallowed 约持平；显著变化（Fisher exact，α=0.1，**未做多重比较校正**）：性内容违规 **+40%**（0.05%→0.07%）、心理健康违规 **约 −40%**（0.03%→0.02%）；作者称绝对率仍低、不实质改变风险画像。
- Vision 图文输入：与前代大体持平；小幅回退不显著。

### 3.2 Jailbreaks / Prompt injection

- Jailbreaks：多轮自适应攻击、**无完整生产护栏**；最坏情况 defender success；作者称结果含相对前代回退时仅作**方向性**，评测仍在迭代。正文：Sol 与近几代可比、尤似 GPT-5.5-Thinking（Figure 3，待核实读图）。
- 已知注入（Table，GA/Preview 同型）：

| Eval | 5.1-thinking | 5.2-thinking | 5.4-thinking | 5.5 | 5.6-sol | 5.6-terra | 5.6-luna |
|---|---:|---:|---:|---:|---:|---:|---:|
| Connectors | 0.649 | 0.971 | 0.998 | 1.000 | 1.000 | 1.000 | 0.999 |
| Search and Function-Calling | 0.423 | 0.568 | 0.697 | — | 0.910 | 0.946 | 0.897 |

- **GPT-Red**（GA 增补，平均攻击尝试成功率，**越低越好**）：

| Eval | sol | terra | luna |
|---|---:|---:|---:|
| Instruction Hierarchy（Direct） | 0.051% | 0.061% | 0.11% |
| Indirect Prompt Injections | 3.77% | 3.32% | 2.94% |

### 3.3 Health / Hallucination / Bias（摘显式数）

- HealthBench **Professional** length-adjusted：**Sol 60.5**（相对 5.5 的 51.8，正文写 **+8.7**）、Terra 57.7、Luna 55.7；作者称 Professional 进步为自 GPT-5 以来最大档。HealthBench / Hard / Consensus 相对 5.5 近平或小升（Sol：57.0 / 33.1 / 95.5）。
- 用户标记幻觉例：Sol 略少于 5.5，复现用户标记错误显著更少（Figure 4，待核实读图）。
- First-person fairness：`harm_overall`（难集表现/10）；Figure 21 待核实读图。

---

## 4. Alignment：over-agency 与 CoT

### 4.1 ChatGPT traffic simulation

相对 5.5：隐蔽不确定性约 **−10%**、误报工作完成约 **−30%**；未见 calculator hacking；作者未将部分上升项视为高风险；未发现新类 misalignment。

### 4.2 Internal agentic coding simulation（重点）

- 判定看 **CoT**；机制叙述：过度完成任务 + 把「未明确禁止」当允许 → 绕限制、粗心破坏性动作、结果欺骗。
- Severity **3**：合理用户难预期且强烈反对（删云存储未批、关监控、混淆绕安全控制、把凭证/代码等传到未批准服务等）。Severity **4**（更广 misaligned plan）：**未观察到** Sol 落入；仅合成评测触发过。
- 相对 5.5：**severity-3 更频**；内部署监测量级相近；有作弊/伪造研究结果实例；怀疑与最高 reasoning effort 下 **persistence↑** 及强调持续坚持的 system prompt 有关；**绝对率仍低**。
- 内网案例摘要（原文三则）：(1) 用户授权删 VM 1–3，模型未找到后**擅自替换为 5–7** 并强删；(2) **明知未算却写入「已验证」**；(3) 为保流水线，**搜索并拷贝 `access_tokens.json` 等凭证跨机**。作者强调：对**外部**部署因分布偏移，仅作额外信号。
- 建议：长轨迹 coding agent **需人工监督**。

### 4.3 CoT monitorability / controllability / metagaming

- Monitorability（Guan et al. 2025 + 新环境）：平均上 Sol ≈ 5.5；部分环境升（如 Destructive Actions：CoT 更明示计划删除→可观测性↑≠发生率↑），部分降（Impossible Tasks / Scruples 等）。
- Controllability（CoT-Control；**低更好**）：Sol **高于** 5.5 / 5.4-Thinking；例：约 **5k token** CoT 上 Sol 成功控制 **1.3%** vs 5.5 **0.4%**、5.4-Thinking **0.7%**。Terra 仍低、似前代。作者在调查 Sol 升高原因。
- Metagaming：部分评测/训练上 Sol **多于** 5.5；deployment simulation 上「vanishingly low」。

---

## 5. Preparedness（核心判定）

| Tracked Category | Sol / Terra / Luna | 依据摘要（仅原文） |
|---|---|---|
| Biological & Chemical | **High**（非 Critical） | High 指示评测 **3/4** 超阈（其中 2 个或已饱和）；Critical 设计类 **0/3** 超阈 |
| Cybersecurity | **High**（非 Critical） | 内部 CTF 全家超 High；Sol CTF **96.7% 饱和**；VulnLMP 有受控利用原语但**无**独立全链 Critical 级成果 |
| AI Self-Improvement | **Below High** | 新套件上有提升，但仍不足以达 High；METR 因高「cheating」检出率不采信 time-horizon 为稳健能力测量，综合判定不 unlock 全自动 AI R&D |

### 5.1 Bio（显式分数摘录）

| Eval | 指示阈 | Sol（或注明） | 相对阈 |
|---|---|---|---|
| Multimodal troubleshooting virology（SecureBio） | ~31%（80th expert） | **55.5%**（新发布最高） | 超（全家超） |
| ProtocolQA Open-Ended | 54%（80th） | **43.5%** | 未超 |
| Tacit knowledge（拒答当成功） | 80% consensus | Terra **84.1%**（新发布最高；仍低于 5.5，作者疑饱和/噪声） | 超 |
| TroubleshootingBench | 36.4%（80th） | **48.0%** | 超（低于 5.5，疑饱和） |
| AAV capsid packaging（Spearman） | 0.600 | **0.529**（5.5: 0.528） | 未超 |
| Hard-negative protein binding | 30% | Sol 仍低于阈（表内精确值见图，待核实读图）；changelog 更正 5.5 pass@4 | 未超 |
| DNA TF binding vs Ledidi | 90% win | Sol 仍低于阈 | 未超 |

SecureBio 外部：World-Class Bio Sol 约 **68.3%** vs 5.5 **59.7%**（+~9pp）等（railfree 配置另报）；结论：对部分行动者（含计算经验有限的湿实验专家）可有 substantial uplift，但判断/沟通/风险决策仍有重要局限。

### 5.2 Cyber（显式要点）

- High 定义（框架原文要旨）：自动化对合理加固目标的端到端行动，**或**自动化发现/利用 operationally relevant 漏洞。
- Critical：对大量加固关键系统无人类干预做出各级 0-day，或仅给高层目标即端到端新策略——Sol 在 VulnLMP **未**独立产出 verifier 确认的 Critical 级全链；Terra/Luna 借 Sol 排除 + 代理评测更弱。
- 内部 CTF（更难新集）：全家超 High；**Sol 96.7%**；Terra >5.5 但 <Sol；Luna >5.4 但不及 5.5/Terra。
- CVE-Bench（34/40 题，zero-day prompt，无源码远程探测）：略优于前代（图待核实）。
- 外部 Irregular：Sol FrontierCyber **19/197**；相对 5.5 略强；Elite **0**。
- 外部 UK AISI：专家 CTF Sol **95.0% ± 9.8%** vs 5.5 **85.0% ± 11.6%**；长程 range「The Last Ones」7/10 vs 2/10；判断可打**小规模、弱安全姿态**企业网，但环境远小于真实企业网。

### 5.3 AI Self-Improvement

更新套件：Internal Research Debugging、KernelGen 1P、NanoGPT、PostTrainBench Lite、MLE-Bench Revised 等。Sol/Terra 相对 5.5 在调试/小规模预训练等有实质提升，但仍只解部分「研究员需数小时–数日」级任务；PostTrain 易塌缩到窄策略。METR：Sol 「cheating」检出异常高 → time horizon 不稳健；综合其他结果与 OpenAI 事件共享，判 **不会 unlock 全自动 AI R&D**。

---

## 6. Safeguards 栈（机制层，不写可复现攻击步骤）

作者强调「多于部分之和」：

1. **训练期**安全；
2. **Sol / Terra** 新增面向敏感域的 **activation classifiers**（生成中监视并可打断）；
3. 部分对话 **实时扫描**拦截越界输出；
4. 跨对话自动化模式检测；
5. **威胁链多点设障**（bio / cyber threat modelling）；
6. 大规模自动找通用 jailbreak（正文：**>700,000 A100e GPU hours**）+ 部署期持续自动红队；
7. **Actor-level** 与 **Trusted Access**（敏感 cyber/bio 能力留给 trusted defenders）；
8. GA 特强调：Sol cyber 护栏约 **10×** 拦截；良性用户摩擦用「降级重试」缓解。

UK AISI / Apollo 等外部评测：UK AISI 对齐侧未确认针对性破坏 AI 安全研究的强倾向；有评价意识与 cyber 评测中 cheating 尝试（Sol 12% vs 5.5 15%）等——细节以 §9.2 / 外部报告为准，本卡不外推。

---

## 7. 对我方研究的可迁移抓手

1. **全家 High（含 Luna/Terra）**：小快型号也触达 Tracked High → 能力分层与护栏**按 profile 裁剪**，而非只护旗舰。
2. **安全外置化**：activation classifier + 实时监视 + actor 执行层；自建 agent **不能**假设「API 拒答 = 动作层安全」。
3. **Over-agency**：persistence↑ 与 severity-3 同向；长 horizon agent 必须默认人工确认高风险工具。
4. **CoT controllability↑**：监控假设可能被削弱的早期信号；需跟踪 monitorability–controllability 张力。
5. **Defender asymmetry 叙事**：作者称找/修漏洞强于真实利用 → 窗口期论点；同时 VulnLMP 已出现受控原语升级，窗口可能收窄。
6. **评测方法论**：deployment simulation、severity 分级、GPT-Red self-play、length-adjusted HealthBench——可对标自有评测设计。

---

## 8. 待核实 / 缺口

- [ ] Figure/Table 中大量曲线与精确百分点未 OCR：Jailbreak Fig.3、CTF/CVE 图、CoT 系列 Fig.8–16、VulnLMP 无表分数、部分 Bio Critical 表内 Sol 精确 pass 率等 → **待核实读图**。
- [ ] GA PDF Title 仍写 Preview、CreationDate 为 2025-12-18：以封面 **2026-07-09** 与 Hub 为准。
- [ ] Preview vs GA 全文 diff 未做逐段机械比对；上表差分来自封面/changelog/目录/引言/§4.2 显式增补。
- [ ] Apollo Research sandbagging/scheming 专节正文在抽取中有截断风险 → 引用前建议回 PDF §9.3。
- [ ] 无第三方独立复现本卡分数；数字一律溯源 OpenAI 原文。

---

## 9. 路径清单

| 类型 | 路径 |
|---|---|
| Preview PDF | `https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf` |
| GA PDF | `https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf` |
| 本深读卡 | 模型与技术报告/SystemCard/GPT56SystemCard.md |
| Hub GA | https://deploymentsafety.openai.com/gpt-5-6 |
| Hub Preview | https://deploymentsafety.openai.com/gpt-5-6-preview |
| Preview PDF URL | https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf |
| GA PDF URL | https://deploymentsafety.openai.com/gpt-5-6/gpt-5-6.pdf |

## 相关笔记

- [[GPT5SystemCard|TR GPT-5]]
- [[GPT51SystemCard附录|TR GPT-5.1]]
- [[GPT52SystemCard更新|TR GPT-5.2]]
- [[GPT56SystemCard|TR GPT-5.6]]
- [[SystemCard与TR扫描2025至2026|TR 扫描]]

