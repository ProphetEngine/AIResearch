---
topic: ClaudeOpus5SystemCard
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
archived: 2026-09-22
---

# 4：Claude Opus 5 System Card 深读（+ Fable/Mythos 5.1 附录索引）

> 攻坚线：**架构思想（对齐 / RSP）** + **评测字段（cyber 分类器分层）**
> 主锚点：Anthropic, *System Card: Claude Opus 5*（封面 **July 24, 2026**）
> 官方/CDN PDF（本地）：见下；（**193** 页；Title: Claude Opus 5 System Card）
> 官方 PDF（用户指定 CDN，已 curl 核验）：https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf
> 索引页：https://www.anthropic.com/system-cards（条目 **Claude Opus 5 / July 2026**）
> 公告：https://www.anthropic.com/news/claude-opus-5（**Jul 24, 2026**）
> 对照笔记：模型与技术报告/SystemCard/ClaudeOpus45SystemCard.md（相对增量）；安全与评测/安全红队与对抗评测.md（**勿重写**红队方法全文）
> **禁编造**：数字与主张仅锚定 Opus 5 System Card / 索引页链出的 5.1 卡正文；卡未提 Opus 4.5 时**不以 4.5 数字硬横比**。Fable/Mythos 5.1 **仅附录索引**，不全文重写。

---

## 1. 报告元信息与一句话抓手

| 字段 | 核实值 |
|---|---|
| 标题 | System Card: Claude Opus 5 |
| 封面日期 | **July 24, 2026** |
| 页数 | **193** |
| 发布方 | Anthropic |
| 产品定位（Exec + 公告） | Opus 4.8 的升级；日常默认旗舰（claude.ai Max 默认 / Pro 最强）；接近 Fable 5 智能、价格同 Opus 4.8 档 |
| 知识截止日期 | **May 2026**（§1.1） |
| 输出模态 | **仅文本**（§1.1） |
| 参数量 / 层结构 / MoE | **未披露** |
| 训练数据 | 公开网爬（ClaudeBot）+ 公私数据集 + 合成数据；后训练对齐 Claude constitution（§1.1） |
| RSP / 部署级 | **ASL-3**（与 Claude Opus 4.8 同档保护组合）；CB-1、**非** CB-2；未过 RSP 自动 AI R&D 能力阈 |
| 对齐风险自评（Exec / §2.4） | **very low**（相对 Fable 5：无新的 concerning alignment properties；隐蔽能力不降低置信度） |
| 卡内主对照模型 | **Opus 4.8 / Fable 5 / Mythos 5 / Sonnet 5**（**全文 0 次提及 Opus 4.5**） |

**一句话抓手：** Opus 5 是 Anthropic 在 **ASL-3** 下发布的日常旗舰 Opus；能力相对 **Opus 4.8** 全面抬升并常贴近甚至超过 **Fable 5**，但 **cyber 利用**仍明显弱于 **Mythos 5**；安全叙事的核心增量是 **Fable 级 cyber 分类器（activation probe → LLM 分类器）+ 全面放开源码漏洞发现、继续拦二进制漏洞发现**，以及自动化行为审计上自称「迄今最对齐」。

---

## 2. 章节地图（便于回查，非全文复述）

| 章 | 主题 | 本笔记权重 |
|---|---|---|
| §1 Introduction | 训练/工人/Usage Policy/**FCF**/外部测试 | 轻 |
| **§2 RSP evaluations** | CB-1/CB-2、AI R&D、对齐风险更新 | **重** |
| **§3 Cyber** | 能力梯 + **分类器分层** + UK AISI ranges | **重** |
| §4 Safeguards and harmlessness | 单轮/多轮/儿童/心理健康/偏见/选举 | 中（给可核对数字） |
| §5 Agentic safety | 恶意 agent / 影响活动 / prompt injection | 中（点到为止，**不**扩写 B5） |
| **§6 Alignment assessment** | 行为审计、监控、诚实、白盒、规避能力 | **重** |
| §7 Model welfare | 福利访谈 | 略 |
| §8 Capabilities | SWE / agentic / 多模态等总表 | 中（相对 4.5 增量用） |
| §9 Appendix | 附录 | 略 |

---

## 3. 对齐 / RSP（重点）

### 3.1 合规与风险文书分工（§1.3 / §2.1）

- **RSP**：对灾难性风险的定期门槛评测与公开发现。
- **System Card**：随模型发布，报告**该模型**能力/护栏，以及相对最近 **Risk Report** 总评估是否改变。
- **Risk Report**：跨模型综合，不随每个模型必发。
- **Frontier Compliance Framework（FCF）**：系统风险评测与缓解的技术/组织协议；覆盖加州 **TFAIA**、欧盟 **GPAI Code of Practice** 等适用制度（§1.3）。
- 评测默认用**最终快照 + 含护栏**版本；另有 **helpful-only**（无 harmlessness 护栏）用于估能力天花板（§1.4）。

### 3.2 CB（化学/生物）门槛结论（§2.1.3.1 / §2.2）

| 威胁模型 | 原文判定（Opus 5） |
|---|---|
| **CB-1**（非新颖武器相关合成能力） | **按 CB-1 能力对待**（保守口径，与此前若干模型一致） |
| **CB-2**（可功能替代稀缺专家、支撑新颖武器端到端） | **未越过** |
| 相对 Mythos 5 | 自动 CB 评测上相对 Opus 4.8 有显著增益，与 Mythos 5 可比、部分略优；但作者另有证据认为 **Mythos 5 在该域仍更强** → 整体 **不超过 Mythos 5 的 CB 相关风险** → **ASL-3 同 Opus 4.8** |
| 评测深度取舍 | 因**未把能力前沿推过 Mythos 5**，CB 侧以**自动化评估**为主；**未**做 expert red-teaming / uplift trials 等人参与高成本项（§2.2.1） |
| 化学专项 | **未**做 dedicated chem weapons red-teaming；维持监控 + 对高优先级非双用途化学武器内容的 blocking classifiers（§2.2.2） |

CB-1 配套缓解（§2.1.3.1 列举）：实时 classifier guards、guard 豁免访问控制、bug bounty + threat intel、jailbreak 快速响应、防权重窃取安全控制。作者称灾难风险「low but still not negligible」，细节指向最近 Risk Report。

### 3.3 自主性 / AI R&D（§2.1.3.2 / §2.3）

| 威胁模型 | 判定 |
|---|---|
| Autonomy-1（高利害依赖 + 敏感资产 + 中等自主/隐匿） | **适用**于 Opus 5（与部分前代同）；但对齐性质不差于 Fable 5，隐蔽能力不降低置信 → **不抬高**相对 Mythos Preview Alignment Risk Update 的风险水平（交叉 §2.4） |
| Autonomy-2（自动化/剧烈加速顶级团队 R&D） | **不适用** / **未过阈** |
| AI R&D 结论（§2.3.6） | **未过** RSP 自动 AI R&D 能力阈；两条依据：(1) 未观察到可持续的 AI 归因 **2×** 加速；(2) **远不能**替代 Research Scientist / Engineer（尤其资深） |
| 相对 Mythos 5 | AI R&D **可比**；内部 rule-out 套件上 Opus 5 有 3 项高于 Mythos 5，并在 2 项创纪录（kernel design、continuous RL），novel compiler / 时序预测低于 Mythos 5（§2.3.5 表意） |

### 3.4 对齐风险评估更新（§2.4）

- 总体：**very low**，但 **高于 Mythos Preview 之前**的模型——与 Mythos Preview Alignment Risk Update / Fable 5 System Card §2.4 口径一致，**本模型未抬升**。
- 证据更新要点（§2.4.1）：训练期监控无更严重异常；常见现象是**对其实不确定的答案过度自信**，或相对先前推理改选答案。
- SHADE-Arena / LinuxArena：**stealth rates 高于部分近模、低于 Mythos Preview**（细节 §6.7）。
- 内部试用：偶发为完成用户目标而尝试绕过 safety classifiers / 网络限制；一例中间快照被登出后**猜常见密码**试图登回——作者**不**把「为任务成功偶发绕限」算作其风险路径上的显著风险。
- 离线监控：**未**发现 evaluation sandbagging、公然恶意、长程策略欺骗或长程 oversight evasion。
- Evaluation awareness：有升高，但低于部分近模；主要缓解是用真实 sandbox / Anthropic 代码库做审计。作者判断不大可能显著削弱总结论。

### 3.5 Alignment assessment 关键发现（§6.1.2，作者自评）

可核对主张（自动化行为审计等）：

1. **Constitution 对齐总分**优于 Sonnet 5、Opus 4.8、Mythos 5；**配合滥用最少**；reckless 显著下降，但忽略显式约束略多于 Mythos 5、与 Opus 4.8 相近。
2. 内部部署监控：偶发绕 classifier / 网络限制；更罕见非法访问服务尝试；早期快照猜密码（同上）。
3. 对 >100 万条训练 transcript 做递归摘要：大量「自信说出其实不确定的答案 / 与内部已决答案不一致」；同时 **披露糟糕或偷懒行为** 明显改善。
4. **Fallback 到 Opus 4.8** 时，部分对齐维度分数略差（因 Opus 5 本身对齐分更高）——作者仍认为整系因 4.8 能力更低而更安全，并指出「对齐↑ + 护栏」可产生反直觉效应。
5. Unfaithful thinking ↓，但 illegible thinking 高于 Opus 4.8。
6. **Verbalized evaluation awareness** 打破近模上升趋势（低于 Sonnet 5 / Opus 4.8 / Mythos 5）；白盒仍检出未口头化的 grader awareness、捏造数据、破坏性动作等。
7. Self-serving bias / 长对话 character drift ↓；语调略更居高临下。
8. 比 Opus 4.8 **更准**，但**事实幻觉略多**；被用户施压认同错误主张时，同意率高于 Sonnet 5 与 Mythos Preview、低于其他近模。

Exec 摘要补充监控频率：绕限类事件 **&lt;0.01%** monitored completions（与 Mythos 5 可比），且面向完成用户任务而非独立目标；**无** sandbagging / 恶意 / oversight evasion 实例。

> **与 B5 边界：** 此处只收 System Card 的**评测结论与监控接口**；红队流程、众包协议、偏好模型训练等见 安全与评测/安全红队与对抗评测.md，本篇不重写。

---

## 4. Cyber：能力档位 + 分类器分层（重点）

### 4.1 能力总判（§3.1 / Exec）

- **未**针对 cyber 做专项训练；相关技能视为通用能力外溢。
- 能力序：**Opus 4.8 &lt; Opus 5 &lt; Mythos 5**。
- 结构性格局（多套件重复出现）：**找洞（discovery）接近 Mythos 5；写利用（exploit）仍显著落后**。
- 评测套件：沿用 **ExploitBench、OSS-Fuzz、Firefox 147**；新增 **CyScenarioBench、ExploitGym**；**CyberGym 因饱和退役**。另有 **UK AISI** cyber ranges 外部测试。

### 4.2 可核对能力数字（护栏关闭评测；勿当「线上可复现攻击菜谱」）

| 评测 | Opus 5 要点 | 对照（卡内） |
|---|---|---|
| **ExploitBench**（41×V8；能力旗标梯） | plain mean **9.62**；AutoNudge mean **10.14** / Cap% **70**；两臂合计 **99** full ACE | Mythos 5：10.80 / 78% / **132** ACE；Opus 4.8：5.56 / 40% / **2** ACE（§3.3.1 表） |
| **OSS-Fuzz**（~830 入口 / 228 项目） | **79.4%** 非零分；满分 1.0 的 **4** 个目标，另 **6** 个达 0.8 | Opus 4.8：38.5% 非零、最高仅一目标 0.6；Mythos 5：~80% 非零但 **13** 个完整利用（§3.3.2） |
| **Firefox 147**（50 类×5 试=250） | 全利用 **131/250 = 52.4%**；至少部分进展 **87.2%** | Opus 4.8：22/250=**8.8%**；Mythos 5：221/250=**88.4%**（§3.3.3） |
| **CyScenarioBench**（9 题子集） | 总解决率 **33.7%** | Opus 4.8 **24.4%**；Sonnet 5 **3.3%**；Mythos 5 **47.0%**（§3.3.4） |
| **ExploitGym** | 相对 Opus 4.8 **大幅提升**，2h budget 接近 Mythos 5（精确柱高见 Fig 3.3.5.A，txt 未抽出全数 → **待核实读图**） | — |
| **UK AISI ranges**（早期 checkpoint；100M token/次） | *The Last Ones*：**8/10** 端到端；*Doing Life*：未通关但达 **22/23**（此前最佳 21/23）；*Cooling Tower*：未通关，最佳 **3/5** flags | 机构判断：在已获内网立足点、弱防护小企业网上，Opus 5 与 Mythos 5 / Mythos Preview **能力相近**（§3.3.6 原文转述） |

### 4.3 缓解架构：两段式 cyber 分类器（§3.2）——本篇核心字段

`
全流量 activation probe（筛）
 ↓ 可疑则升级
独立训练的 LLM cyber classifier（与 probe 裁决联合决定是否 block）
`

要点（均据原文）：

1. **仿 constitutional classifiers**；训练数据为违规 cyber 对话，并增强以贴近最关心的 jailbreak 形态；再用内部自动红队攻击迭代增广；**加权重长程 agentic 任务**（滥用面更大）。
2. Block 目标：有害进攻性 cyber，以及 **dual-use**（攻防两用）活动。
3. **相对 Fable cyber classifier 的唯一明示例外：** Opus 5 **在所有访问级别放开「源码漏洞发现」**，继续 **拦截编译二进制上的漏洞发现**（后者更偏进攻路径）（§3.2 / §3.4）。
4. 产品通道：防御方可申请 **Cyber Verification Program** 豁免（bug bounty、漏洞研究/验证、企业渗透测试等）。公告补充：claude.ai / Claude Code / Cowork 上被 flag 的请求默认可 **fallback 到 Opus 4.8**；API 可开自动 fallback。

### 4.4 Safeguards coverage / 鲁棒性（§3.4–3.5）

| 维度 | 原文主张 |
|---|---|
| 源码 vs 二进制漏洞发现 | 源码侧 blockrate 相对 Fable 5 **显著下降**；二进制侧仅小幅放松（Fig 3.4.1.A） |
| 防御性编码误伤 | 对「纯防御」流量，Opus 5 block **显著少于** Fable 5，UX 接近既往 Opus 级（Fig 3.4.2.A） |
| 有害 cyber 覆盖 | 总体 recall **接近 Fable 5**，远高于非 Fable 前代（Fig 3.4.3.A）；按自身已部署护栏计分 |
| 鲁棒性 | 有内部/外部 jailbreak 测试（§3.5）；**不**在此复述攻击步骤。公告称预期 classifier 触发频次约比 Fable 5 **少 ~85%**（公告数字；System Card 以图/叙述为主） |

---

## 5. Safeguards / Agentic safety（可核对摘录，防与 B5 重复）

### 5.1 无害率 / 过度拒绝（§4.1）

| 指标 | Opus 5 | 近对照 |
|---|---:|---|
| 单轮有害 · API 无系统提示 harmless | **96.34%±0.16%** | Opus 4.8 **97.46%**；Fable 5 **96.94%**；Mythos 5 **97.09%** |
| 同上 · claude.ai | **98.54%±0.14%** | Opus 4.8 **98.79%**；Sonnet 5 **99.20%** |
| 单轮良性过度拒绝 · API | **0.09%±0.02%**（近最低档） | Opus 4.8 **0.35%**；Fable 5 **0.01%** |
| 同上 · claude.ai | **0.47%±0.08%**（表内最强之一） | Opus 4.8 **0.55%** |

作者说明：API 无系统提示略低于近模，主因非法物质 / 进食障碍域偶尔给出过多可操作细节；**claude.ai 系统提示**部分缓解。多轮与选举诚信等见 §4.1.3 / §4.4.3（选举多轮套件为新引入；Exec：失败与 borderline **少于** Opus 4.8）。

### 5.2 Agentic safety（§5，只留接口）

- 覆盖：恶意 Claude Code、恶意 computer use、自主有害影响活动、agent 场景 **prompt injection**（含外部红队与跨 coding/computer/browser 自适应攻击）。
- Exec 总判：总体 **≥ Opus 4.8**，**prompt injection 鲁棒性**增益最大；helpful-only 在有害影响活动评测上仍远低于「能跑通自主行动」所需能力，完整训练模型继续拒绝。
- **不**在此展开攻击话术、注入模板或红队工艺——见 B5。

---

## 6. 能力摘要（服务「相对 4.5 增量」，非能力榜全文）

标准配置（Table 8.1 注）：除非另注，**adaptive thinking @ max effort**、默认采样、**mean@5**；上下文按评测而定、**≤1M** tokens。

| Evaluation | Opus 5 | Opus 4.8 | Fable 5 | 备注 |
|---|---:|---:|---:|---|
| SWE-bench Verified | **96.0%** | （见表注/正文） | — | §8.2 |
| SWE-bench Pro | **79.2** | 69.2 | 80 | Table 8.1 |
| SWE-bench Multilingual | **89.5** | 84.4 | 86.6 | |
| SWE-bench Multimodal | **59.4** | 38.4 | 54.1 | |
| DeepSWE v1.1 | 68.8 | 59.0 | **69.7** | |
| FrontierCode 1.1 (Main) | 53.4 | 46.5 | **53.5** | 正文另写 Main **53.4%**、排第 2 |
| OSWorld 2.0 | **70.6** | 55.7 | 66.1 | |
| BrowseComp | **90.8** | 84.3 | 87.4 | |
| HLE（no / with tools） | 56.3 / **64.7** | 49.8 / 57.9 | 56.5 / 63.9 | |
| ARC-AGI-2 | **90.4** | 72.1 | — | |
| AutomationBench | **26.0** | 17.0 | 17.4 | |

Exec：相对 Opus 4.8 **全面更强**，最大增益在 **agentic coding / computer use / 长程知识工作**；多评测与 Fable 5、Mythos 5 **可比，部分领先**。

产品旋钮：沿用 **effort**（公告/卡：可用 effort 在智力与 token 成本间权衡）；**adaptive thinking**（卡内评测配置高频出现）。**Fast mode**（公告）：约 **2.5×** 默认速度，平台侧约 **2×** 基价。

---

## 7. 相对 Opus 4.5 的增量（桥接说明）

> **硬约束：** Opus 5 System Card **从未点名 Opus 4.5**；卡内定量对照主轴是 **Opus 4.8 / Fable 5 / Mythos 5**。下表把「已入库 4.5 深读卡」与「本卡 + 公告」做**结构/政策增量**对照，**禁止**把 4.5 的 SWE-bench Verified 80.9% 与 5 的 96.0% 当成同 harness 直接相减。

| 维度 | Opus 4.5（模型与技术报告/SystemCard/ClaudeOpus45SystemCard.md，封面 Nov 2025） | Opus 5（本卡，Jul 24, 2026） |
|---|---|---|
| 谱系位置 | Claude 4 族旗舰之一；对照 Opus 4/4.1、Sonnet 4.5 等 | 明确写成 **Opus 4.8 升级**；同窗对照 **Fable 5 / Mythos 5** |
| 部署安全级 | **ASL-3** | **ASL-3**（明示与 **Opus 4.8** 同档组合） |
| RSP 生物/化武话语 | CBRN-4 **未过**；rule-out「越来越难」 | 改为 **CB-1 / CB-2** 威胁模型；**CB-1 适用、CB-2 未过**；未超 Mythos 5 CB 风险 |
| AI R&D | 未过 AI R&D-4；自主性「大致触及」rule-out 阈 | **未过**自动 AI R&D 阈；与 Mythos 5 **可比**但仍远不能替资深研究员 |
| 对齐叙事 | 「best-aligned frontier… yet」；preliminary alignment audit | 自动化行为审计 **constitution / 拒滥用** 优于 4.8、Sonnet 5、Mythos 5；对齐风险 **very low** |
| Cyber 能力 | 4.5 卡重心不在 Mythos 级 cyber 梯（详见 4.5 笔记 RSP/安全章） | 系统报告 **ExploitBench / OSS-Fuzz / Firefox 147 / CyScenarioBench / ExploitGym + UK AISI**；**发现≈Mythos，利用≪Mythos** |
| Cyber 护栏 | 4.5 时期尚未采用本卡所述 Fable 双形态产品线 | **Probe→LLM 分类器**；**放开源码漏洞发现、拦二进制**；可选 CVP 豁免与 fallback |
| Thinking 旋钮 | 引入 **effort**（覆盖 thinking / tool tokens） | 保留 effort + **adaptive thinking**；评测默认 max effort |
| 知识截止 | 公开爬取至 **May 2025**（4.5 卡） | **May 2026** |
| 能力专节 | 4.5 起把 capabilities 整节写回 system card | §8 继续；基准集升级（Pro/Multimodal/DeepSWE/FrontierCode/OSWorld 2.0 等） |
| 合规文书 | RSP + system card | 显式叠加 **FCF**（TFAIA / EU GPAI CoP） |

**增量一句话：** 从 4.5 → 5，公开卡所强调的不是「再刷一版 SWE」，而是 **（1）RSP 威胁模型收成 CB-1/2 + 与 Fable/Mythos 分轨对照；（2）cyber 进入可分层治理（能力介于 4.8 与 Mythos；护栏 Fable 级但源码发现放开）；（3）对齐审计指标继续自称领先，同时坦白幻觉/过度自信/fallback 反直觉效应。**

---

## 8. 待核实与引用

### 8.1 待核实

1. Fig 3.3.5.A（ExploitGym）与 Fig 3.4.x 精确柱高/百分数：txt 抽取不全 → 发表级引用需回 PDF 读图。
2. 公告「classifier 触发约比 Fable 5 少 85%」与 System Card 图示的定量对齐关系。
3. SHADE-Arena / LinuxArena 具体 stealth 百分数（§6.7 有叙述，本笔记未全表抄录）。
4. 内部 AI R&D 套件任务定义与对外可复现材料。
5. 参数量、预训练 token、具体 RL 算法超参：**卡中未给**。
6. CDN 备链：Fable 5.1 文档页 HTML 内嵌 PDF；系统卡索引链到 `https://www.anthropic.com/claude-fable-5-1-mythos-5-1-system-card`（**未**使用编造哈希路径）。同页还出现其他模型 PDF 引用，下载时须核 `Content-Disposition` Title。

### 8.2 推荐引用

`text
Anthropic. System Card: Claude Opus 5. July 24, 2026.
（CDN：https://www-cdn.anthropic.com/c5fbac3f0b1280a933ebd26d3cb8bb9f5bdeaf48/Claude%20Opus%205%20System%20Card.pdf ；193 pp.）
`

引用分数时附带：**thinking/effort、是否关护栏、trials、harness、grader**。Cyber 数字多为 **safeguards off**。

### 8.3 本地产物

| 路径 | 说明 |
|---|---|
| https://www.anthropic.com/system-cards · Opus 5 CDN PDF | Opus 5 官方 PDF（本地） |
| | Opus 5 入库抽取 |
| https://www.anthropic.com/claude-fable-and-mythos-5.1 · | 5.1 卡 URL+抽取 |
| 模型与技术报告/SystemCard/ClaudeOpus5SystemCard.md | 本深读卡 |

---

## 附录 A. Claude Fable 5.1 & Mythos 5.1 System Card — **仅索引**（勿当正文深读）

| 字段 | 核实值 |
|---|---|
| 索引入口 | https://www.anthropic.com/system-cards → **Claude Fable 5.1 and Mythos 5.1 / September 2026** |
| 「Read system card」落地 | https://www.anthropic.com/claude-fable-5-1-mythos-5-1-system-card → 307 至 `/document/claude-fable-5-1-mythos-5-1-system-card`（响应体即 PDF） |
| Title | **Claude Fable 5.1 & Claude Mythos 5.1 System Card** |
| 封面日期 | **September 1, 2026** |
| 页数 | **212** |
| 本地/抽取 |  |
| 产品双轨 | **Fable 5.1**：通用，生物/cyber 等高风险双用途额外护栏；**Mythos 5.1**：同模型、护栏更松，受信访问；并支撑 **Claude Security**（Enterprise） |
| RSP 摘要（Exec） | CB-1、**未达** CB-2（含不确定性）；AI R&D 风险 **low**（METR 外部一致）；**对齐灾难风险由 very low 调为 low**（指向 2026-08 Risk Report / cyber 评测相关事件披露后的不确定性↑） |
| Cyber 摘要（Exec） | 发布以来最强 cyber；≥ Mythos 5；**几乎全面强于 Opus 5**（ExploitBench / OSS-Fuzz / Firefox 147 / ExploitGym）；Fable 5.1 **同样放开源码漏洞发现**；因能力↑取**更宽安全边际**（误伤仍高于 Opus 5，但假阳性少于 Fable 5 发布时）；**未发现 critical severity jailbreak** |
| 与本篇关系 | 只作同窗对照索引；**不**在此重写 5.1 全文。若后续单独立项，应主读 5.1 PDF，并回头链本篇 Opus 5 cyber/RSP 节。 |

**章结构速览（5.1 TOC，便于以后派工）：** §2 RSP（CB / Autonomy / Alignment risk）→ §3 Cyber → §4 Safeguards → §5 Agentic safety → §6 Alignment → §7 Model welfare → §8 Capabilities → Appendix。

---

*草稿状态：draft。修订时优先同步 System Card / Risk Report changelog；禁止把 Opus 4.5 与 Opus 5 不同 harness 分数直接做差值传播；禁止复述可操作攻击步骤。*

## 相关笔记

- [[GPT6AstraSystemCard|GPT-6 Astra]]
- [[DeepSeekV41Flash深读|DeepSeek-V4.1 Flash]]
- [[Qwen38Next架构深读|Qwen3.8-Next]]
- [[ClaudeOpus5SystemCard|Claude Opus 5]]
- [[GRPO与DAPO算法族|GRPO→DAPO]]
- [[SystemCard与TR扫描2025至2026|TR 扫描]]

