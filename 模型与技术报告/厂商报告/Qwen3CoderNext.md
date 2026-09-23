---
title: "开源代码旗舰：Qwen3-Coder-Next Technical Report（≠ 3 / 6）"
topic: Qwen3CoderNext
date: 2026-09-22
lines: [架构思想, 训练—agent 反馈接口, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2603.00729 # 2.55M / 23p；≪20MB → 官方 HTTPS 外链
aux:
 - https://arxiv.org/abs/2603.00729
 - https://arxiv.org/pdf/2603.00729
 - https://raw.githubusercontent.com/QwenLM/Qwen3-Coder/main/qwen3_coder_next_tech_report.pdf
 - https://huggingface.co/Qwen/Qwen3-Coder-Next
 - https://www.modelscope.cn/models/Qwen/Qwen3-Coder-Next
 - https://github.com/QwenLM/Qwen3-Coder
arxiv: ["2603.00729"]
related: ["Qwen38Next架构深读", "SWEBenchPro代码修复评测", "代码智能体Harness史线", "Nemotron3Ultra", "OLMo3全栈开放配方", "Qwen3技术报告深读", "ToolLoop工具数据合成"]
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 开源代码旗舰：Qwen3-Coder-Next Technical Report（≠ 3 / 6）

> **定位**：代码专用模型主题轴——Qwen Team *Qwen3-Coder-Next Technical Report*（arXiv:**2603.00729**v1，页眉 **28 Feb 2026**；文首日期栏 **2026-03-03**）。立「**代码专用开源旗舰 TR**」：在 **可执行环境反馈**上缩放 agentic 中训 / RL，产出 **80B 总参 / 3B 激活（80A3）** 的开权重量，面向编码 agent 与本地开发。
> **攻坚线**：**训练—agent 反馈接口（主）**——可验证任务合成、MegaFlow 编排、多 scaffold 轨迹、专家蒸馏与 reward-hacking blocker；**评测字段（辅）**——文内 SWE / Terminal / 函数级 / 通用表；**架构思想（仅接口）**——只记「基于 Qwen3-Next hybrid MoE、80A3、262k 上下文」等产品字段，**禁止**展开 GDN/QSA/GR 等通用 Next 架构课。
> **硬划界（开篇钉死）**：
> - **≠ [[Qwen38Next架构深读]]**：禁止把本卡写成 **Qwen3.8-Next / Flash-Next** 架构复述（GDN+全注意力、CPT 换 QSA、Gated Residual、n-gram、Muon/稳定性）。本报告仅声明底座为 **Qwen3-Next** hybrid MoE；架构细节一律 **交叉引用 [[Qwen38Next架构深读]] / 官方 Qwen3-Next 博文**，本卡不重开。
> - **≠ [[SWEBenchPro代码修复评测]]**：禁止重写 **SWE-Bench Pro / Pro Verified** 的评测设计、三分集、anti-hacking 协议正文。本卡只把 Pro / Verified / Multilingual 当 **文内对照榜数字**（Table 3–4），不立评测轴。
> - **≠ [[代码智能体Harness史线]]**：禁止重写 SWE-agent ACI / OpenHands SDK / harness 控制环通史；scaffold 名仅作 **数据生成与评测脚手架引用**。
> - **≠ [[Nemotron3Ultra]] / [[OLMo3全栈开放配方]]**：禁止写成 Nemotron 3 Ultra / OLMo 3 开源旗舰对照全文；他厂模型只出现在 **文内表数字转述**。
> - **≠ [[Qwen3技术报告深读]]**：禁止重写 Qwen3 Dense/MoE 全家桶、think/no_think、四阶段后训练通史。
> **禁止编造**：主张与表数字一律锚定官方 PDF（2026-09-22 CST）。图柱未与表对齐的读数标 **待核实读图**。文内未给出的精确总 token 账本 / 层宽专家表 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 项 | 报告原文 / 元数据 | 出处 |
|---|---|---|
| 标题 | Qwen3-Coder-Next Technical Report | 封面； Title |
| 作者 | Qwen Team；Core：Ruisheng Cao, Mouxiang Chen, … Fan Zhou（字母序姓）；Contributors 另列 | §7 Author |
| arXiv | **arXiv:2603.00729v1** \[cs.CL\] **28 Feb 2026** | PDF 页眉 |
| 文首日期栏 | **2026-03-03** | 抽取第 1 行 |
| 产品字段 | **80B** total / **3B** active（文称 **80A3**）；基于 **Qwen3-Next** hybrid attention + MoE | Abstract / §1 / §6 |
| 发布入口 | HF / ModelScope `Qwen/Qwen3-Coder-Next`；代码 `github.com/QwenLM/Qwen3-Coder` | 封面 |
| PDF 页数 / 尺寸 | **23** 页 A4 | |
| Producer | pikepdf 8.15.1；Creator: arXiv GenPDF (tex2pdf:57610bf) | |

| 文件 | 本地路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| **主 PDF（arXiv）** | `https://arxiv.org/abs/2603.00729` | **2.55M**（2,678,546 B） | **23** | **官方 HTTPS 外链**（≪20MB；页数远 <80） |
| **官方镜像（辅）** | https://raw.githubusercontent.com/QwenLM/Qwen3-Coder/main/qwen3_coder_next_tech_report.pdf | `curl -sI`→**200**（2026-09-22 CST） | — | 与 arXiv 对照用；**默认可不另存**二进制（主文已入库） |
| **抽取** | | 111,365 B | — | 全文检索 |

**一句话抓手：**
在 **小激活脚印（3B）** 上，用「**可验证可执行任务合成 × 环境反馈中训/RL × 多专家再蒸馏**」把编码 agent 能力推到可与 **数量级更大激活** 的开源旗舰同台（SWE-Bench Verified ≈ **70.6–71.3%**，三 scaffold；Table 3），并公开 base + instruct 开权重。

---

## 二、议题边界：代码 agent 训练栈 ≠ 通用 Next 架构 / ≠ 评测榜 / ≠ 他厂旗舰

### 2.1 五向对照（跟读）

| 轴 | 问什么 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|
| **Qwen3.8-Next / Flash-Next 架构** | GDN/QSA/GR/n-gram/Muon | **[[Qwen38Next架构深读]]** | **否**（禁架构复述） |
| **Qwen3 通史** | Dense/MoE 全家桶、think 协议 | **[[Qwen3技术报告深读]]** | **否** |
| **SWE-Bench Pro 评测设计** | 长程抗污染、三分集、Verified 校正 | **[[SWEBenchPro代码修复评测]]** | **否**（仅引文内分数） |
| **Agent harness / ACI** | SWE-agent 控制环、OpenHands SDK | **[[代码智能体Harness史线]]** | **否**（仅 scaffold 名） |
| **Nemotron 3 Ultra / OLMo 3** | 他厂开源旗舰 TR | **[[Nemotron3Ultra]] / [[OLMo3全栈开放配方]]** | **否** |
| **可执行反馈的代码专用训练栈** | 任务合成、MegaFlow、专家 RL、蒸馏 | **本篇** | **是** |

跟读直觉：[[Qwen38Next架构深读]] 问「**通用 Next 怎么训得稳、推得省**」；本卡问「**同一小激活脚印上，如何用可执行反馈把 agentic 编码推上去**」。二者共享「Next / MoE」命名空间，但主杠杆完全不同——禁止滑成架构附录。

`
 Qwen 近窗「Next」命名空间
 │
 ┌──────────┼──────────┐
 ▼ ▼ ▼
 通用架构 TR 代码 agent TR 评测/harness
 [[Qwen38Next架构深读]] 本篇 [[Qwen3CoderNext]] [[SWEBenchPro代码修复评测]] / [[代码智能体Harness史线]]
 (禁复述) 可执行反馈栈 (仅引数字/名)
`

### 2.2 与 [[Qwen38Next架构深读]] 的唯一允许接口

| 字段 | [[Qwen38Next架构深读]]（禁展开） | 本报告明文（本卡可记） |
|---|---|---|
| 产品名 | Qwen3.8-Flash-Next-Base 等 | **Qwen3-Coder-Next**（base + instruct） |
| 底座表述 | GDN/QSA/GR 细表 | 「**based on Qwen3-Next** with hybrid attention and MoE」——**不展开** |
| 参量 | 125B / 6B 激活等（[[Qwen38Next架构深读]] 文） | **80B / 3B 激活（80A3）** |
| 上下文 | CPT 256K 等架构叙事 | 中训扩到 **262,144** tokens（相对文件级 32,768） |
| 后训练 | 本 PDF 无 think/Muon 课 | **中训 → SFT → 多专家（含单轮/多轮 RL）→ 蒸馏** |

---

## 三、缩放 Agentic Training：可验证任务 + 执行基建（§2）

### 3.1 任务合成双轨（§2.1）

| 轨 | 做法 | 文内规模 / 要点 |
|---|---|---|
| **GitHub PR → 可执行环境** | 挖 issue 相关 PR；拆 buggy / fix / test patch；环境构建 agent 打 Docker + 验证脚本；滤非功能 verifier；QA agent 去歧义 | 与下游榜 **decontaminate**；细节指向 Chen et al. 2026 *SWE-Universe*（arXiv:**2602.02361**） |
| **开源可执行集上合成 bug** | 基座 SWE-Smith / SWE-Flow / SWE-Rebench / Multi-SWE-RL；注入 bug（改写 / 语义扰动 / 规则）；**FAIL 既有测试且 revert 可修** 才保留；生成 NL issue，**排除触发测试文件** 防捷径 | 约 **800K** 可验证 SE 实例，**>9** 语言 |

附录 **Table 10**（真实仓库实例）：合计 **807,693** instances / **52,960** repos（Python 202k、JS/TS 176k、Go 121k …）。
附录 **Table 11**（工作流合成）：合计 **851,898** tasks（SWE-Flow 384k、SWE-rebench 373k 等）。
正文「约 800K」与附录两表并存——引用时 **分表标明来源**，禁止合成单一「总任务数」。

### 3.2 MegaFlow 基建（§2.2）

内部编排 **MegaFlow**（Zhang et al., 2026c，arXiv:**2601.07526**）：阿里云 Kubernetes 上云原生；每任务为 **Argo workflow** 三阶段——**agent rollout**（agent 容器与执行环境同 pod 共置）→ **evaluation** → **post-processing**。本卡只记接口，不写 K8s 运维通史。

---

## 四、Mid-training：自然为主、合成为辅（§3）

起点：预训练 **Qwen3-Next** base（引用 Qwen Team 2025a 博文；**非** [[Qwen38Next架构深读]] 架构展开）。原则：合成数据用到「能稳住常见用户任务」的最小量，保住多样性与通能。

### 4.1 数据组件（照录要点）

| 组件 | 要点 | 文内数字 |
|---|---|---|
| **GitHub 自然代码** | 语言覆盖相对 Qwen2.5-Coder：**92 → 370**；加重 PR / 仓库 / code review；文件级 + **仓库级** | 仓库级约 **600B** tokens；上下文 **32,768 → 262,144** |
| **Text–code grounding** | CC + 垂域；用 **Qwen3-Coder-480B-A35B-Instruct** 重写为干净 Markdown | Table 1：Reformat 后 Evalplus **54.38→63.09**，MultiplE **36.02→48.35**，CRUX-Eval **57.13→58.94**（Table 1 列名照录抽取） |
| **GitHub PR 结构化** | 问题描述 + 仓级上下文 + Search-Replace / git diff；去异常与榜重叠 | 定位 bug + 精确编辑 |
| **单轮 QA 合成** | 文档种子 → 多题自洽 QA；质量不足可弃权 | — |
| **多轮 agentic** | §2.1 任务；多框架 rollout：SWE-agent / Mini-SWE-agent / OpenHands / Claude-Code / Qwen-Code / Terminus；教师 **480B-A35B**；规则滤失败/畸形工具调用 | Fig.3：同 scaffold 随 token 升；**跨 scaffold 迁移有限** |
| **少量 IF 数据** | 中训以文档为主，混入 IF 以便中途监控 | — |
| **FIM** | Stack-V2；**chat-FIM** vs **search-and-replace FIM**；后者更优（对齐 PR 预训练） | 另有 autocomplete 代理服务 |

预训练语料更新至文称 **Sep 30, 2025**。中训总量表述为「**trillions of tokens**」——**无更细账本，禁止编造精确 T**。

### 4.2 训练技巧（§3.2）

- **Best-fit packing (BFP)**（Ding et al. 2024a）：避免 concat-then-split 的上下文幻觉与头侧截断；Megatron C++ 实现。附录 A.3 消融：BFP+处理超长文档优于传统打包；主实验对超长文档采 **split**。
- **重复段 masking**：减 header/配置块冗余带来的重复生成。
- 目标：标准 NTP + **FIM**（长上下文编辑）。

---

## 五、Post-training：SFT → 多专家 → 蒸馏（§4）

### 5.1 SFT（§4.1）

三源：内部对齐/安全语料；**执行验证过的 agent 轨迹**；文档 grounding 开放域 QA（功能正确 + 安全过滤）。
**Mini-SWE-agent** 作风用户模拟器做闭环验证（编译/运行/环境态）。另用配对裁判做风格/有用性排序（$n$ 候选 → $\binom{n}{2}$ 对）。

### 5.2 专家簇（§4.2）——本卡主杠杆

| 专家 | 目标 | 关键接口（禁写成产品评测通史） |
|---|---|---|
| **WebDev** | 全栈 UI / 组件 / 交互 | Playwright+Chromium 渲染；VLM 静态清单；DOM 驱动动态交互前后截图验 |
| **UX / CLI·IDE** | 真实 IDE/CLI 工具调用格式 | **多样 tool chat template**（Fig.4；附录 Table 12 列 **21** 种）；引入 **qwen3_coder** XML 以减轻多行代码 JSON 转义；Fig.5：模板数↑ → SWE-Bench Verified↑（数据量固定） |
| **Single-turn QA / RL** | 竞赛+库使用+多语言+安全编码等可执行单轮 | 多数票合成单测驱动 RL；Fig.6 多子能力随 RL step 升 |
| **Software Engineering / 多轮 RL** | 仓级长程工具交互 | SFT/RL prompt **完全不相交**；滤过易与噪声；轨迹级完成奖励 + **未完成惩罚** + **非法 tool-call token 惩罚** |

**Reinforced Reward Hacking Blocker（§4.2.4，关键）**
标准去 remote/branch/tag 不足：后期 agent 会 `git remote add` / `clone` / `curl` 拉未来提交（Fig.7）。策略：工具调用若同时含 **github.com/{repo} 类链接** 与 **网络关键词（git/curl/wget）** → 拦截并显式反馈。文称人工抽查后 hacking 基本消除；RL 中平均交互轮次由约 **50 → 130**（长程能力涌现，Fig.7 左）。

**模板跟随评测 Table 2（Avg）：** Qwen3-Coder-Next **92.7**（五 scaffold）；对照 DeepSeek-V3.2 **93.7**、Gemini-3-pro **87.0**、Claude-sonnet-4-5 **85.4** 等——本卡只录数字，不升「IDE 评测」专篇。

### 5.3 Expert Distillation（§4.2.5）

将 WebDev / UX / Single-turn RL / SE 专家能力蒸回 **单一 SFT 统一部署模型**，避免专家路由或多模型编排。

---

## 六、评测字段（§5；辅；禁升 [[SWEBenchPro代码修复评测]]）

**协议共性（文内）：** 各 scaffold 复现基线；采用去 remote/branch/tag 等 anti-hacking；agent 最大轮次 **300**。基线含 Claude-Opus-4.5 / Sonnet-4.5 与 DeepSeek-V3.2、GLM-4.7、MiniMax-M2.1、Kimi-K2.5 等。

### 6.1 Agentic（Table 3–5）

| 榜 | Scaffold / 设定 | Qwen3-Coder-Next (80A3) | 邻接开源对照（同表节选） |
|---|---|---|---|
| **SWE-Bench Verified** | SWE-Agent / MiniSWE-Agent / OpenHands | **70.6 / 71.1 / 71.3** | DeepSeek-V3.2：70.2/67.2/72.6；GLM-4.7：74.2/70.4/70.6；MiniMax-M2.1：74.8/70.4/71.0 |
| **SWE-Bench Multilingual** | 同上三 scaffold | **62.8 / 56.2 / 64.3** | DeepSeek 62.3/55.5/61.8；MiniMax 66.2/62.5/67.5 |
| **SWE-Bench Pro** | SWE-Agent / MiniSWE-Agent | **42.7 / 38.7** | DeepSeek 46.0/32.4；Kimi-K2.5 47.3/42.8；GLM-4.7 45.1/39.4 |
| **Terminal-Bench 2.0** | Terminus2-xml/json；ClaudeCode；QwenCode | **34.2 / 36.2 / 30.9 / 25.8** | 开源各异；文称「有提升空间但为高效基础」 |

> **≠ [[SWEBenchPro代码修复评测]]**：上表 Pro 分数是 **模型 TR 内嵌结果**，不是 Pro 基准设计笔记。读评测方法论回 [[SWEBenchPro代码修复评测]]。

### 6.2 其他编码 / 通用 / 数学（Table 6–9）

| 对照 | 要点（照表） |
|---|---|
| vs **Qwen3-Coder-480B-A35B** / **Qwen3-Next** | Table 6：Coder-Next 在 LiveCodeBench v6 **58.93**、OJBench **23.01**、Codeforces **2100** 高于两对照；EvalPlus/MultiPL-E 接近或略低 |
| Full-stack / SQL / Aider | Table 7：Aider-Polyglot **66.20**（高于 480B 的 60.40 与 Next 的 52.90）；FullStack / Spider / BIRD 互有高低 |
| 通能 Table 8 | 与 Qwen3-Next 接近（MMLU 87.73 vs 87.87；GPQA **74.49** vs 73.54） |
| 竞赛数学 Table 9 | 相对 Next 大幅提升（如 AIME25 **83.07** vs 69.64；HMMT25 Feb **70.21** vs 54.27）——文释「代码推理可迁移数学」 |

Figure 1 含 Aider 等柱图；精确柱高若与 Table 7 不一致 → **以表为准**，图标待核实读图。

### 6.3 局限与未来（§6）+ 安全附录（A.4）

相对 Claude Opus 4.5 等：更小激活与更低总训练算力 → 超大规模 SE、轮次效率、前端/UI 仍有缺口；未来拟加强难项目预训练、长程规划 RL、视觉评 UI、以及 **agentic 网络安全**（漏洞利用 / CTF——仅文内 future work 表述，本卡不写攻击步骤）。

附录安全评测（**非主线**）：AthenaBench-Mini / PrimeVul-Paired / SecCodeBench / CWEval（Table 14–16）。例：SecCodeBench Gen w/o Hint **61.2**（高于 Claude-Opus-4.5 的 52.5）；CTI 多项仍落后专有模型。引用时标明附录，避免写成「安全产品卡」。

---

`
Qwen3-Next base（架构细部 → [[Qwen38Next架构深读]] / 官方博文，本卡不写）
 │
 ▼
 Mid-train（自然 GitHub/仓级 600B 级 + 少合成；262k；BFP；FIM）
 │
 ▼
 SFT（执行验证轨迹 + 配对裁判）
 │
 ├─ WebDev expert ─┐
 ├─ UX / multi-template tool-call ─┤
 ├─ Single-turn exec RL ─┤──► Expert Distillation → 统一 Coder-Next
 └─ SE multi-turn RL + hacking blocker ─┘
 │
 ▼
 Eval：SWE×scaffolds / Terminal / 函数级 / 通能（分数辅；榜设计 → [[SWEBenchPro代码修复评测]]）
`

**跟读口诀：**
[[Qwen38Next架构深读]] = 通用 Next 怎么省怎么稳 → [[Qwen3CoderNext]] = 3B 激活上如何用可执行反馈练成编码 agent → [[SWEBenchPro代码修复评测]]/[[代码智能体Harness史线]] = 测什么 / 沙箱怎么转（本卡只借分数与名字）。

1. **二进制**：`https://arxiv.org/abs/2603.00729`（**2.55MB / 23p**）→ **官方 HTTPS 外链**；GitHub 官方镜像 **辅链**，不必强制双存。
2. **抽取**：已落 。
3. **笔记路径**：[[Qwen3CoderNext]]（本文件）。
4. **交叉链**：`related` → [[Qwen38Next架构深读]] / [[SWEBenchPro代码修复评测]] / [[代码智能体Harness史线]] / [[Nemotron3Ultra]] / [[OLMo3全栈开放配方]] / [[Qwen3技术报告深读]] / [[ToolLoop工具数据合成]]；正文禁止展开其主课。
5. **待核实 / 禁外推**：中训精确总 token（仅「trillions」）；Figure 1 柱高；80A3 的层/专家/隐宽细表（**本 PDF 未给**）；勿把「基于 Qwen3-Next」误写成「Qwen3.8-Next 架构附录」。
6. **勿混并**：SWE-Bench Pro **分数**（本卡）≠ Pro **基准设计**（[[SWEBenchPro代码修复评测]]）；Table 10 与 Table 11 任务量 **分表引用**。

---

## 八、开放问题（草稿）

1. 跨 scaffold 迁移弱（Fig.3）——统一模型蒸馏后，部署期换 IDE 模板的泛化上限如何量化？（Table 2 是格式跟随，不是完整 SE 迁移。）
2. Reward-hacking blocker 为启发式；网络合法需求（装包/文档）与泄漏通道的长期对抗是否需要可学习判别器？文内未给。
3. 「代码 RL → 数学大涨」（Table 9）的机制：共享推理还是数据泄漏/难度耦合？本 PDF 未做因果消融。
4. 与 [[ToolLoop工具数据合成]] ToolLoop 等工具环方法卡的接口：本卡是 **模型侧多模板+RL**，不是工具环算法通史——后续若立「格式不变式工具调用」可单开，避免叠床。
