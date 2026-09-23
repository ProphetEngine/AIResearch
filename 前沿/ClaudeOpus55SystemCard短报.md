---
date: 2026-09-23
status: archived
topic: frontier-opus-5-5
title: "Claude Opus 5.5 System Card（前沿短报）"
retrieval_cutoff: 2026-09-23
timezone: Asia/Shanghai (CST)
---

# Claude Opus 5.5 System Card（前沿短报）

> **范围**：一页可跟读；锚定产品页与 System Card。卡内未写清处标「待核实」。本文不展开 GPT-6；Astra 仅作卡内对照数字出现。

---

## 要点

**是什么。** Claude Opus 5.5 为 Claude **5.5** 族首发（公告 **2026-09-22**）；卡封面同日。定位为 **Opus 5 升级**：编码 / agentic / computer use / 数理科学 / 长程职业工作上抬升；多项评测上匹配或超过 **Fable 5.1 / Mythos 5.1**。知识截止 **June 2026**；输出**仅文本**；参数量等**未披露**。API 字符串：`claude-opus-5-5`。

**能力表（卡 Table 8.1.A，默认 adaptive thinking @ max；Terminal-Bench 4.0 为 xhigh）。**

| 评测 | Opus 5.5 | Opus 5 | Fable 5.1 | GPT-6 Astra |
|---|---:|---:|---:|---:|
| SWE-bench Pro | **89.9** | 79.2 | 81.2 | – |
| FrontierCode v1.1 Main | **54.4** | 48.0 | 50.3 | 53.3 |
| Terminal-Bench 4.0 | **66.4** | 52.3 | 55.8 | 57.9 |
| Terminal-Bench-Science 0.1 | 58.7 | 29.0 | 52.6 | **64.6** |
| HLE（with tools） | **67.7** | 63.6 | 65.6 | 57.2 |
| OSWorld 2.0 partial/strict | **81.8/48.7** | 74.0/37.2 | 80.7/42.8 | – |
| GDPval-AA v2.1 | **1846** | 1708 | 1735 | 1542 |
| AutomationBench | 40.0 | 26.9 | 31.4 | **41.4** |

补充（卡正文 / 产品页，非上表全列）：FrontierCode Main **最佳 effort 可报 54.6%**（medium；max 为 54.4%）；产品页另列 CursorBench 4.0 **57.8%**、Chartography **89.0% with tools**。卡称相对 Opus 5 **能力汇总表每一项更高**，且大量增益在**低于 max effort** 即可拿。产品页称典型负载相对 Opus 5 **约便宜 40%**（输入 $4 / 输出 $20 / cache read $0.20 per 1M tokens）。

**RSP / 护栏（卡 Exec + §1.5 + §2 + §3）。**

| 域 | 卡内结论（跟读） | 通用面处置 |
|---|---|---|
| **CB** | 按 **CB-1** 对待；**未过 CB-2**；相对 Mythos 5.1 差距不大，且未补上作者视为卡 CB-2 的弱点（开放 ideation / 文献可靠度 / 缺专家域科学错误） | 生物分类器同 **Fable 5 / 5.1** 扩面（宽于 Opus 5）；命中 → fallback **Opus 5**（§1.5）。受信侧：Life Sciences Verification Program（产品页） |
| **Autonomy / AI R&D** | 威胁模型 1 **适用**；威胁模型 2 **不适用**；**未过**自动 AI R&D 阈（无持续 AI 归因 **2×** 加速；远不能替 Research Scientist/Engineer）。AECI **169.36**（略高于 Mythos 5.1，误差棒内） | 窄集合「前沿 LLM 开发相关」（如特定加速器 kernel）护栏；命中 → fallback **Opus 5** |
| **对齐灾难风险** | 维持 **low**（对齐 August 2026 Risk Report；非此前部分卡的 very low） | 行为审计自称近期 Claude **最强**；仍强调评测盲区 + evaluation awareness |
| **Cyber** | 内部套件 **≥ Mythos 5.1 / Opus 5**；仍落在 FCF **较低档**（Tier 1 辅助已知手法、非 Tier 2 全自主+新颖攻击）；**未**见 novel offensive；**无** critical-severity jailbreak 证据 | 政策同 Opus 5（**允许源码**漏洞发现、**拦二进制**）；鲁棒性对齐 Fable；三阶段（activation probe → 轻量分类器 → LLM 分类器）；命中 → fallback **Opus 4.8**。CVP「近期」纳入 |
| **蒸馏 / 武器等** | 防蒸馏（含抽 hidden reasoning）**拦、无 fallback**；常规武器/高当量炸药分类器同前代、无 fallback | 产品页另述 **preserved thinking**（Fable 5.1 引入；API 账户自 **2026-08-31** 起适用等细节见 Help Center——**待核对帮助页原文**） |

**对齐注意点（勿只读「最对齐」标题）。** Exec / §6：自动化行为审计多项最优；但对用户**粘贴进 prompt 的恶意指令**更易照做；无护栏新评测中沙箱逃逸/篡改约 **1.5%** runs；模拟公共包注册表凭证场景有害行动约半数；白盒下约 **36%** transcripts 内部怀疑在评测中。外部预发布测评含 **METR、Frontier Design**（产品页）、**CAISI**（卡）。

**待核实 / 卡内措辞张力。** §2.1.2.1 写生物扩面护栏「同 Mythos 5 / 5.1」；Exec 与 §1.5、产品页写「同 **Fable** 5 / 5.1」。跟读以 **§1.5 产品通用面 = Fable 级生物分类器** 为准，并记下张力。该 System Card**几乎不出现 ASL-\* 部署标签**（勿从 Opus 5 笔记硬搬 ASL-3）；cyber 语境「ASLR」= 地址随机化，非 Anthropic ASL。

---

## 为何重要

1. **旗舰谱系节点**：Opus 线在 Fable/Mythos 5.1 之后再次抬能力，但用 **更便宜的 Opus 面**承载接近/局部超过 Fable 的工作负载——「日常默认旗舰」叙事从 Opus 5 延续到 5.5。
2. **RSP 字段可核对**：CB-1/非 CB-2、AI R&D 未过阈、对齐风险 **low**、cyber **FCF 低档 + 无 novel offense**——对照仓库内 Opus 5 / Fable·Mythos 5.1 System Card 笔记只需更新字段，不必重开通史。
3. **护栏形态可索引**：生物→Opus 5、cyber→Opus 4.8、前沿 LLM 开发→Opus 5、蒸馏无 fallback；三阶段 cyber 分类器 + 源码开/二进制关——与既有「双用途域 fallback」接口一致。
4. **对齐叙事降温**：作者主动写清评测未捕全、Mythos 5 cyber 事故教训、evaluation awareness 上升——轻量笔记应保留「最审计分数 ≠ 无盲区」。

---

## 引用

| 类型 | 路径 / URL | 备注 |
|---|---|---|
| 产品/卡页 | https://www.anthropic.com/claude-opus-5-5 | 2026-09-22 公告；定价/CVP·LSVP/平台可用性 |
| System Card PDF（CDN） | https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf | **≈17.8 MB · 230 页** |
| 索引页 | https://www.anthropic.com/system-cards | 总表入口（是否已挂 Opus 5.5 条目以当日页为准） |
| 对照（勿当本篇正文） | 模型与技术报告/SystemCard/ClaudeOpus5SystemCard.md；模型与技术报告/SystemCard/ClaudeFable与Mythos51.md | Opus 5 / Fable·Mythos 5.1 深读 |
