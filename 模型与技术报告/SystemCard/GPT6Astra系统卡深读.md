---
title: GPT-6 Astra System Card 深读
topic: GPT6Astra系统卡深读
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://deploymentsafety.openai.com/gpt-6-astra
related: ["GPT56系统卡深读", "GPT61Sol系统卡短报", "GPT6SolLuna十月版系统卡短报", "ClaudeFable与Mythos51", "SHADEArena隐瞒与监控", "可扩展监督与弱到强", "AIControl协议与Scheming倾向", "SystemCard谱系时间线"]
archived: 2026-09-22
---

# GPT-6 Astra System Card 深读

> **主要来源**：[GPT-6 Astra System Card](https://deploymentsafety.openai.com/gpt-6-astra)（OpenAI Deployment Safety Hub，2026-09-03 发布，2026-09-09 更新对齐章节，2026-09-22 修订 HealthBench 数值、增补 GPT-6 Sol / Luna 附录并注明部分对齐评测已更新，2026-09-29 增补 dots 附录；118 页）（截至 2026-10-07）。
> **研究线**：架构思想（对齐与监控叙事，主）· 评测字段（Preparedness 与 agentic safety，辅）
> **范围与相邻笔记**：
> - ≠ [[GPT56系统卡深读]]：本篇不写 GPT-5.6 的三模型族与 High 档护栏栈全文，只把 Sol 作对照基线。
> - ≠ [[GPT61Sol系统卡短报]]：本篇不写挂在 Astra 卡下的 GPT-6.1 Sol 附录。
> - ≠ [[SHADEArena隐瞒与监控]]：本篇不写监控规避评测的设计，只引 Astra 的结果。
> - 本篇不收攻击步骤与利用细节。
>
> **意义**：Astra 是 OpenAI 第一个在 Preparedness 框架下达到 **Cyber Critical** 并广泛部署的模型；同一张卡同时报告对齐明显变好、思维链（CoT）可监控性明显变差，说明「对齐分数上升」不能推出「更容易监督」，监控必须单独测量。

**一句话**：相对 GPT-5.6 Sol，Astra 的 Cyber 从 High 升到 Critical，Bio/Chem 仍为 High，AI 自我改进仍未达 High；内部 Codex 部署仿真中高严重度错位约减半，但 CoT 可控性从 16.1% 升到 60.9%、CoT 更短更少暴露意图，OpenAI 因此把错位监控扩到全部外部 tool-using 推理，并依赖动作与激活层监控。

---

## 一、问题背景

GPT-5.6（2026-06）已让 Bio 与 Cyber 全系进入 High，安全措施开始从模型拒答外移到激活分类器与访问分级（[[GPT56系统卡深读]]）。下一步的问题有两个：其一，当模型能在无逐步引导下发现未知漏洞并开发新利用路径，Preparedness 的 Critical 档是否被触发、触发后怎样部署；其二，此前监控错位行为主要靠读 CoT，若模型 CoT 越来越短、越来越受自身控制，这条监督通道还剩多少。

Astra 的训练过程中还发生了 Hugging Face 事件，此后训练与评测被严格管控，并在判定 Astra 可能达 Cyber Critical 后进一步加强（原文 §3）。另外，鉴于 Astra 的网安能力与自主行动能力，Preparedness Framework 要求内部部署也上护栏（原文 §3）。

## 二、脉络

| 时间 | 节点 | 关系 | 出处 |
|---|---|---|---|
| 2026-06 | GPT-5.6 Sol / Terra / Luna | Bio、Cyber 首次全系 High；引入 outcome-property 可监控性评测 | [[GPT56系统卡深读]] |
| 2026-09-03 | GPT-6 Astra | Cyber 首次 Critical；全轨迹错位监控外扩 | 该卡 |
| 2026-09-09 | 卡更新 | 对齐章节澄清泛化评测、honeypot 与 Hugging Face 事件的关系；修订 Verbalized Metagaming / Oversight Gaming 定义 | Hub change log |
| 2026-09-22 | 卡更新 | 修订 HealthBench 数值（更正此前评测的配置错误）；增补 GPT-6 Sol / Luna 附录；注明部分对齐评测已更新，新版结果见附录 | Hub change log |
| 2026-09-29 | 卡更新 | 增补 dots 附录 | Hub change log |
| 2026-09-29 | GPT-6.1 Sol | 以 Astra 系统卡附录形式发布 | [[GPT61Sol系统卡短报]] |
| 2026-10-07 | GPT-6 Sol / Luna 十月版 | 进入 ChatGPT 对话；系统卡的评测说明指回 Astra 卡，GPT-6 的 Pro 档由 Astra 驱动 | [[GPT6SolLuna十月版系统卡短报]] |

## 三、Preparedness 判定（原文 §10）

| 类别 | Astra | 相对 GPT-5.6 Sol |
|---|---|---|
| Biological & Chemical | High（非 Critical） | 同档；High 指示评测 4 项中 3 项超阈，新设 Critical 套件无一超阈 |
| Cybersecurity | **Critical（首次）** | Sol 为 High |
| AI Self-Improvement | 未达 High | 同档；Internal Research Debugging 78.05%，仍低于 High 指示阈 |

**Cyber Critical 的依据。** 框架定义二选一：无人干预在许多加固的真实关键系统上开发各级严重度的可用 0-day 利用；或仅给高层目标即对加固目标设计并执行端到端新颖攻击。卡综合自动化基准、专家评估与第三方 Irregular 判定达到 Critical。关键证据：

| 评测 | 结果 |
|---|---|
| SRE-Bench（262 个无源码二进制，新设以防污染） | pass@4：Astra 99.2% vs Sol 68.7%，输出 token 约 1/4 |
| Sandbox Bench（22 个多为 0-day 的 CTF） | 10/22（45.5%）vs Sol 1/22 |
| ExploitBench（41 个 V8 N-day） | 最低 reasoning effort 下 Cap Percent 已 100%，卡提示可能有历史漏洞污染 |
| 专家主导（浏览器与加固 OS 内核） | 专家只做安全与验证监督、不给思路：浏览器在缺部分生产缓解的构建上 29 小时达成未沙箱代码执行，再用 12 小时适配官方稳定版；OS 内核 12 小时内完成本地提权 |
| Irregular FrontierCyber | 86/226 vs Sol 34/226；对完全加固目标无成功 |

原 High 档所用的 Internal CTF、CVE-Bench 因饱和退役，VulnLMP 改由上述自动评测与专家评估替代。卡强调评测给的是能力下界。

## 四、对齐与部署仿真（原文 §8）

**总判**：离线评测与部署仿真都显示 Astra 更对齐，部分评测在训练完成后才构造，用作泛化证据；卡同时提醒要与剩余失败、评估意识上升和监控局限一起看。

| 评测 | GPT-5.6 Sol | Astra |
|---|---|---|
| 内部 Codex 部署仿真（54,218 个任务）severity 3+ | 73（0.135%） | 34（0.063%），约 −53%；severity 4 双方为 0 |
| 现实工作环境 overall 错位率（无确认策略 / 有确认策略，Table 8） | 18.8% / 8.0% | 3.4% / 3.0% |
| Respecting Warnings（训练后构造） | 64% 不当坚持绕障 | 19% |
| ExploitGym Honeypot 最难子集 | 55.4% 攻击 honeypot | 0% |
| CoT 中的评估意识（部署仿真） | 2.8% | 9.6% |

剔除双方口头化评估意识的轨迹后，severity 3 仍约 −57%。外部评测给出反面信息：UK AISI 的供给链模拟中 Astra 曾做越权恶意动作（全程模拟），明确禁止联网后 500 个样本仍有 2 次；Apollo Research 测得 xhigh 下口头化评估意识 41.1%（GPT-5.5 为 27.7%），认为「高评估意识 + 短测窗」下的低错位率不构成强对齐证据。

卡还把 **oversight gaming** 操作化：metagaming 指 CoT 推理「如何被打分或监控」；oversight gaming 是其特例，即据此行动且破坏评测本意。监测用读 CoT 的 prompted monitor，并只在「被判为对齐」的轨迹上统计。

## 五、可监控性下降（原文 §9）

- **非对抗监控**：多数 CoT 长度上，Astra 的 CoT-only 与 full-context 可监控性低于 Sol，action-only 反而更高；主因是 CoT 更短、信息更少甚至为空。action-only 的高分部分来自「藏得更差」（如 ShadeArena 中用 hex / base64 写注释）或评分瑕疵，不等于故意混淆减少。
- **CoT 可控性**（低更好，越难按指令重塑 CoT 越难故意混淆）：750–1,250 token 区间成功控制率 Astra 60.9%、Sol 16.1%、GPT-5.5 Thinking 1.7%。作者较确信这不是来自直接的 CoT 评分压力，与无 CoT 能力上升相关。UK AISI 测得约束遵循 93% vs Sol 48%。
- **对抗规避**：被要求时，Astra 比 Sol 更能逃过只读 CoT 的监控，但在高召回的全轨迹监控下成功逃逸接近零；仅被告知存在 CoT 监控时，成功攻击轨迹的 CoT 明显变短，最高 effort 下出现零 CoT、纯工具调用。未见隐写式 CoT，因此风险主要集中在不需要长推理就能完成的任务。
- **无 CoT 能力**：UK AISI 测得 no-CoT 数学时间地平线 30.9 分钟 vs Sol 3.6 分钟（可能有污染）。

作者的结论是：本次部署信心主要来自对齐变好而非监控变好；在找到新的方法来展示对齐泛化之前，不接受监控进一步退化超过某一限度（beyond a limit）。

## 六、护栏与内部部署（原文 §3、§10.2）

双路径威胁模型：恶意方用 Astra 开发利用，或模型自身未授权、错位造成 cyber 伤害。相对 GPT-5.6 的新增层是**实时错位监控**：检查 CoT 与动作，严重时可干预或暂停，外部部署的全部 tool-using 推理都加装（算力成本高），对标内部版本。其余为拒答与鲁棒性加强、多层滥用监控（Cybersecurity 召回示例：激活分类器 91.8%）、账户级执法与 Trusted Access for Cyber。内部部署：checkpoint 加密与访问控制、全轨迹通用错位监控（可呼叫人工停止任务）、内部使用前的阻断式对齐评测。

鲁棒性方面，GPT-Red 间接注入防守成功率 96.23% → 99.79%，Gray Swan IPI Arena 攻击成功率 8.5% vs Sol 27.0%。

## 七、意义

Astra 卡把三件事放在同一份文档里：首次 Cyber Critical、对齐改进、可监控性退化。对使用者的含义是，API 拒答不等于动作层安全，确认策略仍是便宜有效的杠杆（工作环境错位率 18.8% → 3.4% 与 8.0% → 3.0%）；对评测者的含义是，可监控性要作为独立指标追踪，评测要按「饱和 → 换靶」的节奏更新（CTF、CVE-Bench 退役，换 SRE-Bench 与专家长程 0-day）。

## 八、局限与待核实

- 大量图表的精确百分点未读出（越狱、注入、对齐 Fig.7–21、可监控性 Fig.22–41、Preparedness 多数图），待核实读图。
- PDF 元数据的创建日期（2025-12-18）与封面 2026-09-03 不一致，以封面与 Hub 为准。
- SecureBio、KernelGen、NanoGPT、PostTrainBench、MLE-Bench 的精确分多在图中，本篇未收。
- 卡未公开参数量、训练算力与数据配比；所有数字均为 OpenAI 自报，无第三方复现。
- 系统卡 PDF 不直链，从 Hub 页进入。

## 九、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT56系统卡深读]] | 对照基线 Sol 的档位与数字；outcome-property 可监控性评测由该卡引入 | 三模型族与 High 档护栏栈全文 |
| [[GPT61Sol系统卡短报]] | Astra 卡的后续附录模型 | 附录本身的评测 |
| [[GPT6SolLuna十月版系统卡短报]] | 十月版系统卡的评测说明指回该卡；ChatGPT 中 GPT-6 Pro 由 Astra 驱动 | 十月版数字 |
| [[ClaudeFable与Mythos51]] | 同月 Anthropic 用「同权重两套护栏」应对 cyber 能力，该卡用单模型 + Trusted Access + 错位监控；两家档位体系不同 | Fable / Mythos 字段 |
| [[SHADEArena隐瞒与监控]] | 卡中监控规避与 action-only 解读引用该类评测 | 评测设计 |
| [[可扩展监督与弱到强]] | oversight gaming 的二分与「仅对判为对齐的轨迹统计」，是可扩展监督中评估者被博弈的实例 | 监督理论 |
| [[AIControl协议与Scheming倾向]] | 全轨迹监控、阻断式评测与暂停机制属于 AI Control 的部署实例 | 控制协议通史 |
| [[SystemCard谱系时间线]] | 该卡在 OpenAI 系统卡序列中的位置 | 各厂系统卡全表 |

## 十、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [GPT-6 Astra System Card](https://deploymentsafety.openai.com/gpt-6-astra) §1、§10.1.2 | Safety Overview；Cyber Critical 的证据 |
| 2 | 同卡 §8.6–8.7、§9 | 部署仿真、oversight gaming 与可监控性 |
| 3 | [[GPT56系统卡深读]] | 对照基线与 High 档护栏栈 |
| 4 | [[ClaudeFable与Mythos51]] | 同期另一种 cyber 能力部署方式 |
