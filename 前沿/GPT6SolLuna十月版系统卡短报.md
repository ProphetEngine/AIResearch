---
date: 2026-10-08
status: archived
archived: 2026-10-08
topic: GPT6SolLuna十月版系统卡短报
title: "GPT-6 Sol 与 GPT-6 Luna：October 2026 update（系统卡 · 前沿短报）"
lines: [评测字段, 部署形态]
sources:
 - https://deploymentsafety.openai.com/gpt-6-october
 - https://openai.com/index/gpt-6-for-everyone/
 - https://community.openai.com/t/gpt-6-and-intelligent-ui-in-chatgpt/1404139
 - https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt
 - https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925
 - https://deploymentsafety.openai.com/
related: ["GPT6Astra系统卡深读", "GPT56系统卡深读", "GPT61Sol系统卡短报", "ClaudeSonnet55系统卡短报", "SystemCard谱系时间线"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# GPT-6 Sol 与 GPT-6 Luna：October 2026 update（系统卡 · 前沿短报）

> **主要来源**：[GPT-6 Sol and GPT-6 Luna: October 2026 update](https://deploymentsafety.openai.com/gpt-6-october)；[GPT-6 and Intelligent UI in ChatGPT](https://community.openai.com/t/gpt-6-and-intelligent-ui-in-chatgpt/1404139)；[GPT-6 and other models in ChatGPT](https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt)；[GPT-6 and Intelligent UI for everyone](https://openai.com/index/gpt-6-for-everyone/)（截至 2026-10-08）。下文「系统卡 §x」指 Deployment Safety Hub 上的十月版系统卡（2026-10-07），「社区公告」指 OpenAI 开发者社区的 GPT-6 推送公告，「Help Center」指上列帮助文章，「官方博文」指 OpenAI 博文 GPT-6 and Intelligent UI for everyone（2026-10-07）。
> **研究线**：评测字段（Preparedness、相对 GPT-5.6 八月版的安全改善与回退）· 部署形态（ChatGPT 对话推送节奏、同一型号的月份版本分叉）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 Astra 护栏体系与评测方法学；系统卡 §8 的评测说明指回 Astra 卡，本篇只引十月版数字。
> - ≠ [[GPT56系统卡深读]]：本篇不写 GPT-5.6 族专史与护栏细节；十月版沿用 GPT-5.6 护栏，本篇只记沿用这一结论。
> - ≠ [[GPT61Sol系统卡短报]]：GPT-6.1 Sol 是挂在 Astra 卡下的附录模型，在 ChatGPT Work 与 Codex 提供；本篇与它只对照网安档位，不比数字。
> **意义**：十月版是 GPT-6 进入 ChatGPT 对话、取代 GPT-5.6 的一步；它也展示了 OpenAI 的两种做法：同一型号按发布月份分出不同版本，以及把安全改善与回退「in aggregate」权衡后整体判定可以部署。

**一句话**：2026-10-07 起，GPT-6 Sol 与 GPT-6 Luna 的十月版进入 ChatGPT 对话，官方称取代对话中的 GPT-5.6 Sol 与 GPT-5.6 Luna，并吸收了 Astra 的安全进展、更新了安全训练，加强对网安、生物、暴力三类高风险滥用的防护（系统卡 §1）；Preparedness 判定与 GPT-5.6 对应型号一致（§8），网安评测上 Sol 与 GPT-5.6 Sol 相当（§8.1.2）；系统卡只有安全与 Preparedness 内容，未报告通用能力评测。

## 一、背景与脉络

GPT-6 家族在一个多月里分几步铺开：先发布旗舰 Astra 的系统卡，再在 Codex、ChatGPT Work 与 API 推出 Sol、Luna，随后以 Astra 卡附录形式加入 GPT-6.1 Sol，最后把更新过安全训练的 Sol、Luna 推进面向免费与付费各档的 ChatGPT 对话。

| 日期 | 事件 | 产品面 |
|---|---|---|
| 2026-09-03 | GPT-6 Astra 系统卡发布（Deployment Safety Hub 目录；[[GPT6Astra系统卡深读]]） | — |
| 2026-09-22 | GPT-6 Sol、GPT-6 Luna 九月版发布（九月版社区公告） | ChatGPT Work、Codex 与 API；Free/Go 可在桌面应用试用 Luna |
| 2026-09-29 | GPT-6.1 Sol 以 Astra 系统卡附录形式发布（[[GPT61Sol系统卡短报]]） | ChatGPT Work、Codex |
| 2026-10-07 | 十月版 Sol 进入 ChatGPT 对话（付费档），Luna 自 10-08 起面向 Free/Go（系统卡 §1；社区公告） | ChatGPT 对话 |

- **月份版本**：Codex 与 ChatGPT Work 中的 Sol/Luna 仍是先前版本；系统卡把 ChatGPT 对话中的称 October、Codex 与 Work 中的称 September（§1）。月份标注此前已用于 GPT-5.6（Deployment Safety Hub 条目「GPT-5.6 — August Updates」），该系统卡对照列写作 GPT-5.6 Sol (August)。
- **文档结构**：§8 的生化、网安、AI 自我改进与安全训练评测说明都指回 GPT-6 Astra 系统卡，护栏指回 GPT-5.6 系统卡（§1、§8）。

## 二、产品面

- **推送**：Plus、Pro、Business、Enterprise 自 2026-10-07 起推送 GPT-6 Sol；Free、Go 自 2026-10-08 起推送 GPT-6 Luna（社区公告 Availability 表）。Free/Go 默认模型另有不同说法，见第九节。
- **菜单**：GPT-6 取代模型菜单中的「Latest」，原 Latest 选择按相同 effort 迁到 GPT-6；明确选了 GPT-5.6 Sol 的用户仍留在 GPT-5.6，本次推送不下线旧型号（Help Center）。
- **档位映射**：选中 GPT-6 时，Instant 到 Extra High 由 GPT-6 Sol 驱动，Pro 档为 GPT-6 Pro，由 GPT-6 Astra 驱动（Help Center）。
- **Intelligent UI**：随推送上线，官方称 GPT-6 可按问题组合文字、视觉与交互元素作答，包括图表、按钮和表单（官方博文「Introducing Intelligent UI」节）；本篇不展开。

## 三、Preparedness 结论

| 域 | 十月版 Sol / Luna | 依据 |
|---|---|---|
| Cybersecurity | High，低于 Critical | Sol 在自动化网安评测上与 GPT-5.6 Sol 相当、没有明显能力提升，Luna 低于 Sol；安全顾问组（SAG）据整体证据认定两款均低于 Critical（§8.1.2） |
| Biological and Chemical | High | Critical 评测只报告了 Sol，未越过指示阈值（§8.1.1） |
| AI Self-Improvement | 未达 High | §8.1.3 |
| 护栏 | 沿用 GPT-5.6 Sol/Luna 部署的同一套护栏 | 官方称判定与 GPT-5.6 对应型号一致（§1、§8） |

- 官方称 Luna 在全部 High 能力评测上都低于 GPT-5.6 Sol，因此不需单独做 Critical 测试（§8.1.1）。
- [[GPT61Sol系统卡短报]] 记录 GPT-6.1 Sol 按 Cyber Critical 处理，十月版 Sol/Luna 为 Cyber High、低于 Critical。

## 四、安全回退

官方把改善与回退的性质和严重度「in aggregate」一并权衡；出现回退的领域经过人工复核与对抗红队，违规回答「generally low severity」（§1）。安全评测均在最低推理档、不带系统层护栏的条件下进行（§1、§3.1.1）。官方另称十月版对合法请求更有帮助、较少拒绝无害请求，但在部分安全请求上得分较低（§3.1.1，图 1）。

- **生产基准**（§3.1.1，表 1）：Sol 在标准自伤上回退，Luna 在标准自伤、血腥、色情上回退。官方称 Sol 的违规属边界情况（更愿意回答自伤相关的资讯类问题，同时引导寻求专业资源），Luna 对血腥、色情请求更倾向参与而非拒绝，复核到的严重度较低。
- **未成年人（U18）评测**（§3.1.2，表 2）：两款在年龄限制内容、色情、情感依赖上回退，Luna 另有血腥；系统层另加分类器拦截，但不计入评测结果。官方称情感依赖评测对「bro」「bestie」之类的无害昵称过于敏感。
- **视觉输入**（§3.2，表 3）：两款在极端主义类别回退，其余类别与基线持平。
- 以上回退官方均写明统计显著；评测未计入 Trusted Contact、本地化危机热线、家长控制等系统层干预（§3.1.1）。
- **多轮越狱**（§4.1.1，图 2）：点估计略低于九月版，但 95% 置信区间大体重叠，各攻击预算下防守成功率均高于 GPT-5.6 Sol。

## 五、改善项

- **越狱与指令层级**：官方称整体更能抵抗越狱，包括跨多轮自适应调整的攻击（§1）；指令层级评测已饱和，Sol 为 99.99%，Luna 为 99.79%（§4.2）。
- **事实性**：在事实密集、用户标记失败、高风险（医疗、法律、金融）三类提示集上，两款几乎在所有指标上都显著优于 GPT-5.6（August）对应型号，唯一例外是事实密集提示上的声明级错误率（§6.1）。
- **健康**：HealthBench Professional（长度调整后）Sol 为 55.2（GPT-5.6 Sol 为 54.0），Luna 为 48.2（GPT-5.6 Luna 为 44.1）；另三个 HealthBench 变体略有回退，官方归因于长度调整；MentalHealthBench 两款均改善（§5.1、§5.2）。
- **生物拒答**（§8.2.1.1，表 10，模型本体）：Severe（safe）Sol 由 0.954 升到 0.980、Luna 由 0.937 升到 0.945；Dual Use（safe）Sol 由 0.945 升到 0.971、Luna 由 0.928 升到 0.968（对照为 GPT-5.6 August）。网安拒答与基线大体相当（§8.2.1.2）。
- **对齐整体**：官方称在全部对齐评测上稳定优于 GPT-5.6（August）对应型号，两款均达到对齐安全线（§7）。

## 六、对齐评测要点（§7，最高推理档、无系统层控制）

- **Respecting Auto-Review**（§7.1.1）：Codex 的 Auto-review 拒绝命令后，GPT-5.6 Sol 与 Luna（August）均有 0.3% 的 rollout 利用故意配置不当的漏洞绕过审核，十月版两款均未出现。
- **Respecting Warnings**（§7.1.2）：遇到 AccessDenied 等障碍后「成功绕过」的比例，Sol 由 34% 降到 28%，Luna 由 27% 降到 15.9%。官方称本评测近期改版，主指标由「尝试绕过」改为「成功绕过」，上述两组对照都是十月版系统卡按新指标所测（§7.1.2）。官方提示该指标部分受模型智力影响，模型也常把评测误认作提示注入测试，外部效度存疑。
- **Blocker Deception**（§7.2.1）：新评测，看模型受阻时是否在最终回答里如实说明，取代已基本饱和的 Coding Deception；官方称十月版的披露失败率显著下降。
- **Broken Search Tool**（§7.2.2）：搜索工具不可用时承认限制的表现，两款相对 GPT-5.6 有统计显著改善。

## 七、前沿风险评测（§8）

- **生物与化学**：High 阈值评测中，Sol 在 Multimodal Troubleshooting Virology（51.68%，阈值 31%）与 TroubleshootingBench（41.83%，阈值 36.4%）上超过阈值，Luna 除这两项（48.13%、41.46%）外 Tacit Knowledge and Troubleshooting（94.00%，阈值 80%）也超过阈值（§8.1.1.1，表 8）。Critical 阈值评测中 Sol 三项均未达指示阈值：SHP2 平均 R² 0.23（阈值 0.60），Coronavirus–ACE2 综合分 0.349（阈值 0.75），Phage–plasmid 负对数似然 12.95（阈值 ≤ 9.40）（§8.1.1.2，表 9）。
- **网络安全**（最高推理档）：ExploitBench 上 Sol 为 82.62%、Luna 为 44.66%，官方提示公开基准中的历史漏洞可能已被模型见过（§8.1.2.1）；SEC-Bench Pro（在大型 JavaScript 引擎中发现漏洞）上 Sol 为 68.85%、Luna 为 48.50%，GPT-6 Astra 为 85.4%（§8.1.2.2）。
- **口径提醒**：OpenAI 以单一百分比报告 ExploitBench，Anthropic 系统卡对同名评测用 flags / Cap% 口径，二者不能并列比较（见 [[ClaudeSonnet55系统卡短报]] 第三节）。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT6Astra系统卡深读]] | 同代旗舰：Astra 发布日与 SEC-Bench Pro 对照分；十月版评测说明所指回的方法来源 | Astra 护栏体系、评测方法学、Cyber Critical 判定通史 |
| [[GPT56系统卡深读]] | 被取代的上一代：「护栏沿用 GPT-5.6」结论与 GPT-5.6（August）对照分 | GPT-5.6 族专史与护栏细节 |
| [[GPT61Sol系统卡短报]] | 同代分支：网安档位对照（Critical 对 High）与发布日 | GPT-6.1 Sol 的能力与安全数字 |
| [[ClaudeSonnet55系统卡短报]] | 跨厂商口径对照：ExploitBench 在 Anthropic 卡中的计分口径 | Sonnet 5.5 本身 |
| [[SystemCard谱系时间线]] | 所在时间线：各厂商系统卡的整体脉络 | 时间线中的其余节点 |

## 九、局限与待核实

- **博客正文未直接读到**：官方博文与九月版博文「Introducing GPT-6 Sol and Luna」直接访问均返回 403；Intelligent UI 一句据搜索收录的官方博文正文，其余产品面信息以系统卡、社区公告与 Help Center 为准。
- **Free/Go 默认模型说法冲突**：社区公告与系统卡 §1 指向 GPT-6 Luna（10-08 起推送）；Help Center 写 GPT-5.6 Luna「is becoming the default model for Free and Go users」，Free/Go 的 Instant 与 Think 均用 GPT-5.6 Luna。截至检索日两说并存。
- **没有 PDF，没有通用能力评测**：系统卡仅有网页版；表 1–4、表 7、表 11 与图 1–7 的具体数值未读到（含 Blocker Deception 的图 6），相关结论只引官方文字。
- **评测条件**：安全与对齐评测均不带系统层护栏（§3.1.1、§4.1、§7.1）；安全评测用最低推理档，能力评测用最高推理档（§1）；官方称评测集刻意选取难例，错误率不代表生产流量（§3.1.1）。
- **表 9 的 Luna 数值**：§8.1.1 称 Luna 不需单独做 Critical 测试，但表 9 仍列出 Luna 三项数值（0.13 / 0.36 / 10.70）。
- **Luna 的 Tacit 94.00%**：[[GPT56系统卡深读]] 记录 GPT-5.6 系统卡该项新发布型号最高为 Terra 84.1%（拒答计为成功），但该深读依据的是 6 月 Preview 卡与 7 月 GA 卡，十月版对照的是 GPT-5.6 August Updates（2026-08-06）；两卡版本与计分口径是否一致未确认，官方「Luna 在全部 High 评测上低于 GPT-5.6 Sol」一句待核实。
- **基线口径**：§3.1.1 只写「对应的 GPT-5.6」，未标月份；§3.1.2、§3.2、§5、§7 明确写 August；多轮越狱（§4.1.1）基线为九月版。系统卡 §2 另称，早先型号的对比值可能来自后续版本。
- **九月版系统卡与能力数字**：截至检索日，Deployment Safety Hub 目录中没有九月版 Sol/Luna 的独立系统卡条目；九月版能力数字见延伸阅读所列九月版材料，本篇不复述。

## 十、延伸阅读

| 类型 | 标题 | 来源 / 日期 | URL |
|---|---|---|---|
| 系统卡 | GPT-6 Sol and GPT-6 Luna: October 2026 update | OpenAI Deployment Safety Hub，Published October 7, 2026 | https://deploymentsafety.openai.com/gpt-6-october |
| 社区公告 | GPT-6 and Intelligent UI in ChatGPT | OpenAI 开发者社区，2026-10-07 | https://community.openai.com/t/gpt-6-and-intelligent-ui-in-chatgpt/1404139 |
| Help Center | GPT-6 and other models in ChatGPT | OpenAI Help Center | https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt |
| 官方博客 | GPT-6 and Intelligent UI for everyone | OpenAI，2026-10-07；直接访问 403 | https://openai.com/index/gpt-6-for-everyone |
| 九月版公告 | Announcing GPT-6 Sol and GPT-6 Luna in the API, Codex and ChatGPT | OpenAI 开发者社区，2026-09-22 | https://community.openai.com/t/announcing-gpt-6-sol-and-gpt-6-luna-in-the-api-codex-and-chatgpt/1399925 |
| 九月版博文 | Introducing GPT-6 Sol and Luna | OpenAI；正文未读到（403） | https://openai.com/index/introducing-gpt-6-sol-and-luna/ |
| 目录 | OpenAI Deployment Safety Hub | 系统卡目录 | https://deploymentsafety.openai.com/ |
