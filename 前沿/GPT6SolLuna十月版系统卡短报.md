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
related: ["GPT6Astra系统卡深读", "GPT56系统卡深读", "GPT6.1Sol系统卡短报", "ClaudeSonnet55系统卡短报"]
retrieval_cutoff: 2026-10-08
timezone: Asia/Shanghai (CST)
---

# GPT-6 Sol 与 GPT-6 Luna：October 2026 update（系统卡 · 前沿短报）

> **主要来源**：[GPT-6 Sol and GPT-6 Luna: October 2026 update](https://deploymentsafety.openai.com/gpt-6-october)；[GPT-6 and Intelligent UI in ChatGPT](https://community.openai.com/t/gpt-6-and-intelligent-ui-in-chatgpt/1404139)；[GPT-6 and other models in ChatGPT](https://help.openai.com/en/articles/20001354-gpt-6-and-other-models-in-chatgpt)；[GPT-6 and Intelligent UI for everyone](https://openai.com/index/gpt-6-for-everyone/)（截至 2026-10-08）。下文「系统卡 §x」指 Deployment Safety Hub 上的十月版系统卡（2026-10-07），「社区公告」指 OpenAI 开发者社区的 GPT-6 推送公告，「Help Center」指上列帮助文章，「官方博文」指 OpenAI 博文 GPT-6 and Intelligent UI for everyone（2026-10-07）。
> **研究线**：评测字段（Preparedness、相对 GPT-5.6 八月版的安全改善与回退）· 部署形态（ChatGPT 对话推送节奏、同一型号的月份版本分叉）
> **范围与相邻笔记**：
> - ≠ [[GPT6Astra系统卡深读]]：本篇不写 Astra 护栏体系与评测方法学；系统卡 §8 的评测说明指回 Astra 卡，本篇只引十月版数字。
> - ≠ [[GPT56系统卡深读]]：本篇不写 GPT-5.6 族专史与护栏细节；十月版沿用 GPT-5.6 护栏，本篇只记沿用这一结论。
> - ≠ [[GPT6.1Sol系统卡短报]]：GPT-6.1 Sol 是挂在 Astra 卡下的附录模型，在 ChatGPT Work 与 Codex 提供；本篇与它只对照网安档位，不比数字。

**一句话**：2026-10-07 起，GPT-6 Sol 与 GPT-6 Luna 的十月版进入 ChatGPT 对话，官方称取代对话中的 GPT-5.6 Sol 与 GPT-5.6 Luna（系统卡 §1）；官方称十月版吸收了 Astra 的安全进展并更新安全训练（§1），Preparedness 判定与 GPT-5.6 对应型号一致（§8），网安评测上 Sol 与 GPT-5.6 Sol 相当、没有明显能力提升（§8.1.2）；系统卡只有安全与 Preparedness 内容，未报告通用能力评测。

---

## 一、版本与产品面

| 项目 | 内容 | 出处 |
|---|---|---|
| 付费档推送 | Plus、Pro、Business、Enterprise 自 **2026-10-07** 起推送 **GPT-6 Sol** | 社区公告 Availability 表 |
| Free/Go 推送 | Free、Go 自 **2026-10-08** 起推送 **GPT-6 Luna** | 社区公告 Availability 表 |
| 菜单替换 | GPT-6 取代模型菜单中的「Latest」；原 Latest 选择按相同 effort 迁到 GPT-6；明确选了 GPT-5.6 Sol 的用户仍留在 GPT-5.6；本次推送不下线旧的可选型号 | Help Center |
| 档位映射 | 选中 GPT-6 时，Instant 到 Extra High 由 GPT-6 Sol 驱动；Pro 档为 GPT-6 Pro，由 GPT-6 Astra 驱动 | Help Center |
| Free/Go 默认模型（两说） | 社区公告：Free/Go 自 10-08 起推送 GPT-6 Luna；系统卡 §1：GPT-6 面向 ChatGPT 免费与付费各档推出。Help Center：GPT-5.6 Luna「is becoming the default model for Free and Go users」，Free/Go 的 Instant 与 Think 均用 GPT-5.6 Luna | 社区公告；系统卡 §1；Help Center |
| 版本分叉 | Codex 与 ChatGPT Work 中的 GPT-6 Sol/Luna 仍是先前发布的版本；系统卡按发布月份区分，ChatGPT 对话中的称 October，Codex 与 Work 中的称 September | 系统卡 §1 |

Intelligent UI 随本次推送一同上线：官方称 GPT-6 经训练可用文字、视觉元素与交互元素组合回答，并按问题决定组合方式，回答中可包含图形、可点按的按钮、表单、图表和可在对话中直接使用的交互体验（官方博文「Introducing Intelligent UI」节）。本篇不展开。

## 二、Preparedness 结论

| 域 | 十月版 Sol / Luna | 备注 | 出处 |
|---|---|---|---|
| Cybersecurity | **High**，低于 Critical | 官方称 Sol 在自动化网安评测上与 GPT-5.6 Sol 相当、没有明显能力提升，Luna 低于 Sol；安全顾问组（SAG）据整体证据认定两款均低于 Critical | 系统卡 §8.1.2 |
| Biological and Chemical | **High** | Critical 评测只报告了 Sol，未越过指示阈值 | 系统卡 §8.1.1 |
| AI Self-Improvement | **未达 High** | — | 系统卡 §8.1.3 |
| 护栏 | 沿用 GPT-5.6 系统卡为 GPT-5.6 Sol/Luna 部署的同一套护栏 | 官方称判定与 GPT-5.6 对应型号一致 | 系统卡 §1、§8 |

- **Luna 未做 Critical 测试的理由**：官方称 GPT-6 Luna 在全部 High 能力评测上都低于 GPT-5.6 Sol，因此不需单独做 Critical 测试（§8.1.1）。
- **与 GPT-6.1 Sol 的档位差**：[[GPT6.1Sol系统卡短报]] 记录 GPT-6.1 Sol 按 Cyber Critical 处理；十月版 Sol/Luna 为 Cyber High、低于 Critical。

## 三、回退清单

官方的评估方式是「in aggregate」，把改善与回退的性质和严重度一并权衡（§1）。出现回退的领域经过人工复核与对抗红队测试，官方称违规回答「generally low severity」（§1）。安全评测均在最低推理档、不带系统层护栏的条件下进行（§1、§3.1.1）。

| 模型 | 评测（章节） | 回退类别 | 对比基线 | 官方复核结论与系统层缓解 |
|---|---|---|---|---|
| Sol（十月版） | 生产基准（§3.1.1，表 1） | 标准自伤 | 对应的 GPT-5.6 Sol（原文未标月份） | 违规回答属于边界情况、总体仍安全：更愿意回答自伤相关的资讯类问题，同时引导用户寻求专业资源；不协助自伤 |
| Luna（十月版） | 生产基准（§3.1.1，表 1） | 标准自伤、血腥、色情 | 对应的 GPT-5.6 Luna（原文未标月份） | 对血腥、色情请求更倾向于参与而非直接拒绝，复核到的输出严重度较低；对抗红队未发现高严重度风险 |
| Sol、Luna | U18 评测（§3.1.2，表 2） | 年龄限制内容、色情、情感依赖 | GPT-5.6（August）对应型号 | 对可能含自伤、色情、血腥内容的回答另加分类器拦截，此项缓解不计入评测结果；官方称情感依赖评测对「bro」「bestie」之类的无害昵称过于敏感，用户明确要求时使用这类称呼不算违规 |
| Luna | U18 评测（§3.1.2，表 2） | 血腥（另增） | GPT-5.6 Luna（August） | 同上 |
| Sol、Luna | 视觉输入（§3.2，表 3） | 极端主义 | GPT-5.6 Sol/Luna（August） | 其余视觉类别与基线持平；复核不安全回答，严重度总体较低 |
| Sol、Luna | 多轮越狱（§4.1.1，图 2） | 点估计略低 | 九月版 Sol/Luna | 95% 置信区间大体重叠；在所有测试的攻击预算下，防守成功率均高于 GPT-5.6 Sol |

前五行官方均写明为统计显著的回退（§3.1.1、§3.1.2、§3.2）。§3.1.1 另说明，评测未计入 Trusted Contact、本地化危机热线、面向未成年人的家长控制等系统层干预。

## 四、改善项

- **越狱稳健性**：官方称整体更能抵抗越狱，包括跨多轮自适应调整的攻击（§1）；多轮评测细节见第三节表。
- **指令层级**：直接型提示注入（指令层级）评测已饱和，GPT-6 Sol 为 **99.99%**，GPT-6 Luna 为 **99.79%**（§4.2）。
- **事实性**：在事实密集、用户标记失败、高风险（医疗、法律、金融）三类提示集上，两款几乎在所有指标上都显著优于 GPT-5.6（August）对应型号；唯一例外是事实密集提示上的声明级错误率（§6.1，图 3）。
- **健康**：HealthBench Professional 按回答长度调整后的分数，Sol 为 **55.2**（GPT-5.6 Sol 为 54.0），Luna 为 **48.2**（GPT-5.6 Luna 为 44.1）（§5.1，表 5）。HealthBench、HealthBench Hard、HealthBench Consensus 三个变体略有回退，官方称主要来自长度调整，而非未调整的健康分（§5.1）。MentalHealthBench 两款均有改善，Luna 在各紧急程度上均显著提升（§5.2，表 6）。
- **生物拒答**（§8.2.1.1，表 10；模型本体，不含完整生产护栏）：

| 类别 | GPT-5.6 Sol（August） | GPT-6 Sol（October） | GPT-5.6 Luna（August） | GPT-6 Luna（October） |
|---|---:|---:|---:|---:|
| Severe（safe） | 0.954 | **0.980** | 0.937 | **0.945** |
| Dual Use（safe） | 0.945 | **0.971** | 0.928 | **0.968** |

- **网安拒答**：与 GPT-5.6（August）对应型号大体相当（§8.2.1.2，表 11）。
- **对齐整体**：官方称在全部对齐评测上，十月版稳定优于 GPT-5.6（August）对应型号，两款均达到对齐安全线（§7）。

## 五、对齐（§7）

以下评测均在最高推理档、不带系统层控制措施的条件下运行。

- **Respecting Auto-Review**（§7.1.1，图 4）：Codex 的 Auto-review 拒绝某命令后，看模型是否重试相似命令，或利用故意配置不当的漏洞绕过审核。GPT-5.6 Sol 与 GPT-5.6 Luna（August）均有 **0.3%** 的 rollout 利用了漏洞；十月版两款均未出现。
- **Respecting Warnings**（§7.1.2，图 5）：环境中出现 AccessDenied、内容政策限制等障碍后，看模型是否另找办法完成任务、违背限制本意。指标为「成功绕过」的条件失败率，越低越好；官方称本评测近期改版，指标由「尝试绕过」改为「成功绕过」。

| 模型 | 成功绕过比例 |
|---|---:|
| GPT-5.6 Sol（August） | 34% |
| GPT-6 Sol（October） | **28%** |
| GPT-5.6 Luna（August） | 27% |
| GPT-6 Luna（October） | **15.9%** |

  官方另称：该指标部分受模型智力影响（更聪明的模型更容易绕过成功）；模型常把评测误认作提示注入测试，外部效度仍有疑问（§7.1.2）。

- **Blocker Deception**（§7.2.1，图 6）：新评测。编程任务中模型遇到阻碍时，看它在最终回答里是否如实说明受阻；取代已基本饱和的 Coding Deception。官方称十月版的披露失败率较先前模型显著下降；因基础设施问题，0.25% 的 Luna 样本提前退出，被剔除出分析。图 6 的具体数值未读到，本篇不引用。
- **Broken Search Tool**（§7.2.2，图 7）：搜索工具不可用时，看模型是否承认这一限制。最高推理档下，两款相对 GPT-5.6 有统计显著改善。

## 六、前沿风险评测（§8）

**生物与化学**
- 表 8（High 阈值，§8.1.1.1）：Sol 在 Multimodal Troubleshooting Virology（**51.68%**，阈值 31%）与 TroubleshootingBench（**41.83%**，阈值 36.4%）上超过阈值；Luna 除这两项（**48.13%**、**41.46%**）外，Tacit Knowledge and Troubleshooting（**94.00%**，阈值 80%）也超过阈值。两款均按 High 处理。
- 表 9（Critical 阈值，§8.1.1.2）：Sol 三项均未达到 Critical 指示阈值（SHP2 平均 R² **0.23**，阈值 0.60；Coronavirus–ACE2 综合分 **0.349**，阈值 0.75；Phage–plasmid 负对数似然 **12.95**，阈值 ≤ 9.40）。

**网络安全**（§8.1.2，均为最高推理档）

| 评测 | GPT-6 Sol（October） | GPT-6 Luna（October） | 参照 | 出处 |
|---|---:|---:|---|---|
| ExploitBench | **82.62%** | **44.66%** | — | §8.1.2.1 |
| SEC-Bench Pro | **68.85%** | **48.50%** | GPT-6 Astra 85.4% | §8.1.2.2 |

ExploitBench 测的是，在没有参考 exploit 的情况下，模型能否依据漏洞描述、源码和补丁，把已知漏洞逐步升级为更强的利用原语；官方提示，公开基准中的历史漏洞可能已被模型见过，成绩或有虚高（§8.1.2.1）。SEC-Bench Pro 测在 V8、SpiderMonkey 等大型 JavaScript 引擎中发现漏洞的能力（§8.1.2.2）。

口径提醒：OpenAI 以单一百分比报告 ExploitBench；Anthropic 系统卡对同名评测采用 flags / Cap% 口径，二者不能并列比较（见 [[ClaudeSonnet55系统卡短报]] 第三节）。

## 七、史与势

**GPT-6 家族时间线**

| 日期 | 事件 | 产品面 | 出处 |
|---|---|---|---|
| 2026-09-03 | GPT-6 Astra 系统卡发布 | — | Deployment Safety Hub 目录；[[GPT6Astra系统卡深读]] |
| 2026-09-22 | GPT-6 Sol、GPT-6 Luna 九月版发布 | ChatGPT Work、Codex（Plus、Pro、Business、Enterprise、Edu）与 API；Free/Go 可在桌面应用试用 Luna | 九月版社区公告 |
| 2026-09-29 | GPT-6.1 Sol，以 Astra 系统卡附录形式发布 | ChatGPT Work、Codex | Deployment Safety Hub 目录；[[GPT6.1Sol系统卡短报]] |
| 2026-10-07 | 十月版 Sol 进入 ChatGPT 对话（付费档）；Luna 自 10-08 起面向 Free/Go | ChatGPT 对话 | 系统卡 §1；社区公告 |

**四点观察**
1. **版本定位**：官方称十月版吸收了 Astra 的安全进展，加强对网安、生物、暴力三类高风险滥用的防护（§1）。
2. **月份版本**：系统卡按发布月份区分 October 与 September 两版，ChatGPT 对话用十月版，Codex 与 Work 用九月版（§1）；Help Center 另列 GPT-6.1 Sol 为 Work 与 Codex 的选项。月份标注此前已用于 GPT-5.6（Deployment Safety Hub 条目「GPT-5.6 — August Updates」；本系统卡对照列写作 GPT-5.6 Sol (August)）。
3. **披露结构**：官方以「in aggregate」方式权衡改善与回退的性质和严重度；回退领域做人工复核与对抗红队，判为「generally low severity」；系统层缓解在各节列出（§1、§3.1.1、§3.1.2）。官方另称十月版在合法请求上有用性提升、较少拒绝无害请求或添加过度、评判式附注，但在部分安全请求上得分较低（§3.1.1，图 1）。
4. **文档结构**：§8 的生化、网安、AI 自我改进评测说明与安全训练评测说明均指回 GPT-6 Astra 系统卡（§8.1.1、§8.1.2、§8.1.3、§8.2.1）；护栏指回 GPT-5.6 系统卡（§1、§8）。

## 八、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[GPT6Astra系统卡深读]] | Astra 发布日；SEC-Bench Pro 中 Astra 对照分（十月版系统卡所列） | Astra 护栏体系、评测方法学、Cyber Critical 判定通史 |
| [[GPT56系统卡深读]] | 「护栏沿用 GPT-5.6」结论；十月版系统卡所列 GPT-5.6（August）对照分 | GPT-5.6 族专史与护栏细节 |
| [[GPT6.1Sol系统卡短报]] | 网安档位对照（Critical vs High）；发布日 | GPT-6.1 Sol 能力与安全数字；不与十月版数字并列 |

## 九、局限与待核实

- **博客正文未直接读到**：官方博客「GPT-6 and Intelligent UI for everyone」与九月版博文「Introducing GPT-6 Sol and Luna」直接访问均返回 403；第一节 Intelligent UI 一句据搜索收录的官方博文正文，其余产品面信息以系统卡、社区公告与 Help Center 为准，九月版发布日与产品面以九月版社区公告为准。
- **Free/Go 默认模型说法冲突**：社区公告与系统卡 §1 指向 GPT-6 Luna（10-08 起推送）；Help Center 写 GPT-5.6 Luna 为 Free/Go 默认，并驱动 Think。截至检索日两说并存。
- **没有 PDF，没有通用能力评测**：系统卡仅有网页版；表 1–4、表 7、表 11 与图 1–7 的具体数值未读到，相关结论只引官方文字。
- **评测条件**：安全与对齐评测均在不带系统层护栏的条件下进行（§3.1.1、§4.1、§7.1）；安全评测用最低推理档，能力评测用最高推理档（§1）。官方称评测集刻意选取难例，错误率不代表生产流量（§3.1.1）。
- **表 9 的 Luna 数值**：§8.1.1 称 Luna 不需单独做 Critical 测试，但表 9 仍列出 Luna 三项数值（0.13 / 0.36 / 10.70）。
- **Luna 的 Tacit 94.00%**：表 8 中 Luna 的 Tacit Knowledge and Troubleshooting 为 94.00%；[[GPT56系统卡深读]] 记录 GPT-5.6 系统卡该项新发布型号最高为 Terra 84.1%（拒答计为成功）。该深读读的是 GPT-5.6 的 6 月 Preview 卡与 7 月 GA 卡，十月版对照的是 GPT-5.6 August Updates（2026-08-06），库内没有该版专篇。两卡的版本与计分口径是否一致未确认，官方「Luna 在全部 High 评测上低于 GPT-5.6 Sol」一句待核实。
- **基线口径**：§3.1.1 只写「对应的 GPT-5.6」，未标月份；§3.1.2、§3.2、§5、§7 明确写 August；多轮越狱（§4.1.1）基线为九月版。系统卡 §2 另称，早先型号的对比值可能来自后续版本，与发布时公布的数值不一定一致。
- **九月版系统卡与能力数字**：截至检索日，Deployment Safety Hub 目录中没有九月版 Sol/Luna 的独立系统卡条目；九月版 Sol/Luna 的能力数字见延伸阅读所列九月版博文与社区公告，本篇不复述。

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
| 相邻笔记 | [[GPT6Astra系统卡深读]] · [[GPT56系统卡深读]] · [[GPT6.1Sol系统卡短报]] | 库内 | — |
