---
title: "UI-Venus-2 Technical Report：跨端 GUI 基础智能体与可验证 RL 信号"
topic: UIVenus2GUI智能体
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2609.00028
arxiv: ["2609.00028"]
related: ["智能体工具与长程任务", "视觉语言动作谱系", "GRPO与DAPO算法族"]
appendix_index:
 - arxiv: "2609.12394"
 title: "BlueLM-GUI Technical Report"
archived: 2026-09-22
---

# UI-Venus-2（GUI 观测–动作闭环）

> **定位**：GUI 智能体技术报告主题轴——**Ant Group Venus Team** 的跨 **mobile / web / desktop** foundation GUI agent；主轴是 **截图观测 → 推理 → 结构化 GUI 动作 → 环境反馈** 的统一闭环，以及为离线 RL 供能的 **trace / sample 级可验证信号**。
> **攻坚线**：**架构思想（主）** + **评测字段（trace/sample 验证与多基准表，辅）**。
> **硬划界（禁止重写）**：**不写** ReAct / MCP / 通用工具环全文（→ **[[智能体工具与长程任务]]**）；**不写** 具身机器人 VLA / 连续动作 flow（→ **[[视觉语言动作谱系]]**）；GRPO/DAPO 算法族细节仅交叉引用（→ **[[GRPO与DAPO算法族]]**），本篇不展开配方。
> **同窗附录索引**：BlueLM-GUI（arXiv **2609.12394**）仅作对照入口，**不另开同题正文**。
> **禁止编造**：骨干规模、环境规模、验证四分类、基准数字一律取自官方 PDF（2026-09-22 CST）；正文未展开的投票协议 / 安全训练细节 / 离线 RL 具体损失 **标「文内未细写」**，不臆造。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Venus Team (Ant Group), *UI-Venus-2 Technical Report* | arXiv:**2609.00028v1** \[cs.AI\] **27 Aug 2026**；`https://arxiv.org/abs/2609.00028`（**37** 页） | 跨端 GUI foundation agent；环境–任务–验证三轴共扩 |
| **发布入口（文内）** | Code / Model / Project | https://github.com/inclusionAI/UI-Venus ；https://huggingface.co/collections/inclusionAI/ui-venus ；https://ui-venus.github.io/UI-Venus-2 | 权重与评测基建（本篇不跟 commit） |
| **家族前作（交叉）** | UI-Venus / UI-Venus-1.5 | Gu et al. (2025)；Team et al. (2026c)，文内称 mid-training 与 RL 配方沿用 1.5 | 本篇不重写 1.5 损失表 |
| **附录索引** | *BlueLM-GUI Technical Report* | arXiv:**2609.12394v3**（摘要核：真机 flywheel；35B-A3B；MobileGUI-VBench / AndroidWorld） | **仅索引**，见 §九 |

**一句话抓手：** 把「能点会逛」的 GUI agent 做成 **可部署 foundation** 的瓶颈不在单点 grounding，而在 **环境覆盖 × 功能可执行任务 × 防 reward hacking 的验证器** 三者同扩；UI-Venus-2 用统一 **reasoning–action** 闭环吃 mobile/web/OS，再用 **SGV（trace）+ a priori 逐步判定（sample）** 给离线 RL 喂多分辨率信号，最后用 **MOPD（动作结构感知蒸馏）** 把分域专家合回一个策略。

---

## 二、问题框定（相对工具环 / VLA）

摘要与 §1 把「基准模型 → 可信真实部署」的缺口压成三点：

1. **环境覆盖不够**：不能只活在少数应用；需覆盖多语言 mobile app 与 **原生桌面 OS**。
2. **任务构造脆弱**：开放指令必须 **功能可落地（function-grounded）**，否则轨迹不可执行、不可验。
3. **奖励验证不可靠**：粗粒度终态成功/失败会把「部分进展」当完成，或给出可被策略利用的虚高信号——**RL 只与 verifier 一样可靠**（§1）。

| 相邻路线 | 数据流 | 本篇是否主写 |
|---|---|---|
| **[[智能体工具与长程任务]]** 工具环 / MCP / 长程可靠性 | API·文件·沙箱工具调用 | **否**；GUI 动作是像素坐标级人机控件，不是 MCP 协议栈 |
| **[[视觉语言动作谱系]]** 机器人 VLA | 相机观测 → 关节/末端动作 | **否**；此处是 **数字界面截图 → Click/Type/Hotkey…** |
| **UI-Venus-2（本篇）** | 渲染界面图 → 结构化 GUI 动作 → 环境反馈再观测 | **是** |

**可跟读闭环句（§2.1）：** 给定自然语言指令，模型 **观察渲染界面图像 → 解释视觉上下文 → 把高层意图译成可执行 GUI 动作 → 据环境反馈持续适配，直到任务完成**。

---

## 三、系统总览：三阶段管线 + 统一任务混合物

### 3.1 初始化与任务族

| 项 | 论文事实 |
|---|---|
| 基座 | **Qwen3.5-9B**、**Qwen3.6-27B**（§2.1） |
| 产物 | **UI-Venus-2-9B** / **UI-Venus-2-27B** |
| 任务混合物 | **Grounding + CAPTCHA + Mobile + Web + Computer**（互补：精细空间 / 可控可验交互 / 真实导航经验） |
| 动作空间 | 跨平台统一；桌面侧额外动作见附录 Table 7（§2.1 指向 appendix） |

### 3.2 三阶段（Figure 3 / §2.2–2.4）

`
BASE (Qwen3.5-9B / Qwen3.6-27B)
 │
 ├─ Stage I Mid-Training 大规模轨迹 SFT（Mobile/Web/OS 主导）
 │
 ├─ Stage II Offline RL 分域 step-level 离线 RL
 │ Grounding / CAPTCHA / Mobile / Web / Computer
 │
 └─ Stage III MOPD 多教师 On-policy Distillation → 统一 GUI agent
`

- **Stage I**：异构合成 + 交互轨迹 mid-training；查询由 curated seed 条件生成；轨迹经 **human–discriminator 协同** + 自动轨迹级评估过滤无效/歧义/低质样本（§2.2）。
- **Stage II**：在 mid-trained 模型上做 **离线 RL**。Mobile/OS/Web 用大规模 **step-level** 轨迹；CAPTCHA/Grounding 用程序化合成嵌入真实页面/App 背景，以获得 **稠密、难度可控、动作级正确性可验** 的监督（§2.3）。具体 RL 损失沿用 **UI-Venus-1.5** 配方——**本 TR 正文未重写算法式，勿填 GRPO/PPO 名**。
- **Stage III · MOPD**：多教师 on-policy distillation，把分域专家并入学生，同时尽量保留基座多模态推理（§2.4；引用 Xiao et al. 2026；Yan et al. 2026）。

### 3.3 MOPD：把蒸馏压在「会改环境的那一小段动作」上

GUI 回复通常是 **推理轨迹 + 结构化动作**，但 **只有动作进入环境、决定状态转移**；动作内部又有 **类型 → 参数 schema** 依赖（§2.4）。

相对「整段 response 均匀 token 蒸馏」的 vanilla OPD，文内做两类 GUI 适配：

**（1）Structured Action-Aware Distillation**——按学生动作正确性调节蒸馏强度：

| 学生动作状态 | 蒸馏策略（文内） |
|---|---|
| 完整动作正确 | **抑制** 动作段蒸馏（无需纠正） |
| 类型对、参数错 | **加强** 动作 span 监督 |
| 类型错 | **强调 type token**，并 **mask** 下游参数（参数语义依赖类型） |

例：Click 类型对但坐标错 → 仍可纠坐标；若误预测为 Scroll，其参数语义无关（§2.4）。

**（2）Teacher-Side Action-Type Conditioning**——给教师 prompt 追加正确动作类型 hint $h(z^*)$；**hint 从不进学生 prompt / 推理**；教师不另生成轨迹，只对学生采样打分。token 级蒸馏优势（文内式 (1)）：

$$
\hat{A}^{\mathrm{hint}}_t = \mathrm{sg}\big[\log \pi_{T_d}(y_t \mid P_T(x,z^*), y_{<t}) - \log \pi_\theta(y_t \mid P_S(x), y_{<t})\big]
$$

其中 $T_d$ 为域 $d$ 冻结教师，$\mathrm{sg}$ 停梯度。

---

## 四、数据生成闭环：目录 → 合同任务 → 截图–动作 rollout

### 4.1 通用三段（§3.1 / Figure 2）

1. **Capability Catalog Construction**：冷启动用 **Deep Research** 聚合官方文档、帮助页、用户讨论、常见工作流与历史任务 → 结构化能力目录（函数签名、前置条件、兼容函数、覆盖度）。rollout 后用观测页面状态、控件约束、实体校验、失败案例 **动态更新** 采样分布。
2. **Task Construction**：生成单能力 / 复合 / 查询式 / 批量 / 场景任务；每条任务是绑定 NL 指令、域、能力标签、初态、资源与期望结果的 **executable contract**；**validity gate** 拒绝不支持函数、歧义目标、缺依赖、**不可验结果**。
3. **Trajectory Collection**：**screenshot–action loop**；成功与失败都回写目录（观测函数、非法实体、未满足前置、失败原因），驱动下一轮覆盖薄弱能力。

摘要量化锚点（与贡献条目一致）：环境扩到 **170+** 多语言 mobile apps（贡献写 **100+ 中文 + 70+ 英文**）及 **原生桌面 OS**；任务侧用 deep-research **功能落地** 指令生成。

### 4.2 分域实例化（§3.2，只记可核数字与机制）

| 域 | 关键机制 / 数字（文内） |
|---|---|
| **Web** | 公开 browser-agent 基准 + **Tranco** → 可达性检查 + Kimi 2.6 打分 → **>4,000** 域、**19** 类；能力目录种入 InSTA-150k-v3 的 **45,000** 任务；真实 Chrome + **15-action Playwright**；规则清洗冗余 wait / 反向滚动 / 循环动作 |
| **Computer** | **TaskSpec**（桌面快照、setup、文件/服务、出处、outcome evaluator）；fixture fingerprint 去重与 hidden-answer 泄漏检测；长程任务 **层级切分子目标**，已验证 exit state 续种下一段 |
| **Synthetic Grounding** | 合成 HTML/CSS/JS → 截图+DOM+几何；九位点测（可见性、裁剪、滚动包含、遮挡、绘制像素等）；不可行指令作 hard negative；直接导出 SFT/RL，**绕过**通用任务构造 |
| **Synthetic CAPTCHA** | **70** 类规则引擎；潜状态决定答案/几何/合法动作/解轨迹；渲染进 mobile/webpage；渲染前验可解性 → 稠密可机验标签 |

CAPTCHA 在叙事上还有数据缩放作用：避免登录/注册等流程卡在验证门，阻塞下游状态收集（§1）。

---

## 五、可验证 RL 信号：Trace-level + Sample-level（本篇主轴）

动机（§3.3）：开放 GUI 任务上，粗 **二元终态** 标签不足以刻画部分进展、推理质量与任务可行性；需要 **语义上有意义且时间上可粒度化** 的验证。

### 5.1 Trace-level · Semantic Guided Verification（SGV）

相对规则可验的文件/配置终态，开放 GUI 成功常是 **语义** 而非句法。SGV 用 **VLM-as-Judge**（引用 Sun et al. 2026）看执行轨迹是否语义满足目标；**不依赖** agent 自报成功——失败/超时/用户介入轨迹同样可验（§3.3.1）。

五步管线（文内）：

1. 从任务目标抽 **可验证 completion keypoints**；
2. 轨迹切固定窗口，截图上对 CLK 叠 **红标**，增强视觉 grounding；
3. **并行** 判定各窗口满足哪些 keypoints，累积过程证据；
4. 证据 unambiguous → 硬规则；歧义 → 多模态终判（终止信号、行为统计、窗口解释、末帧）；
5. 结构化报告：结论、推理、逐 keypoint 状态、证据截图。

**轨迹四分类：**

| 标签 | 含义（文内） |
|---|---|
| **completed** | 全部关键目标达成 |
| **partial** | 部分目标达成或朝完成有实质进展 |
| **infeasible** | 外部约束下客观不可行，且被 agent 正确识别 |
| **failed** | 未形成有效进展 |

例：「在目标群发指定内容」→ keypoints：进对群、填标题正文、确认发布；前两步完成但步数耗尽 → **partial** 而非 failed。

**用途边界（重要）：** SGV 结论是 **数据策展的质量分层**，**不是**直接训练标签或基准分数。completed → 高质量候选；partial → 截断/续写修复队列；infeasible → 反哺可行性规则；failed → 拆分任务设计 / 环境稳定性 / agent 能力问题；新发现功能回灌子能力池（§3.3.1）。

**关于「multi-model voting」：** 摘要与贡献条目写「多异构模型投票」以降低单裁判偏差、减轻 reward hacking；§3.3.1 正文展开的是 **并行窗口判定 + 歧义多模态终判**。**投票的具体席位/票权协议正文未逐步展开** → 笔记只记主张，不补伪流程。

### 5.2 Sample-level · 执行前（a priori）逐步判定

与事后终态不同：仅用 **执行前** 信息——当前截图、声明动作类型与目标、agent 推理、任务目标——判定动作质量，便于实时干预，并避免把外部因素导致的页面跳变算进动作好坏（§3.3.2）。

两阶段：先查 **reasoning–action consistency**，再查任务对齐。

| 逐步标签 | 含义（文内） |
|---|---|
| **Correct** | 明确推进任务，且 agent 对正确性有把握 |
| **Exploratory** | 显式不确定但对合理候选路径做有根据探测（有 grounded 理由且引起状态变化） |
| **Ineffective** | 无实质贡献（点非交互区、短无用环等） |
| **Incorrect** | 偏离目标、完成后仍继续、或推理–动作不一致（幻觉 / thought–action mismatch） |

再聚合为轨迹三层：先判可行性（正确报 infeasible vs 未识别→failed）；可行则区分 **generic**（启动 App、切 tab、滚动）与 **task-specific**（填具体内容、选特定目标）——**至少一步有效 task-specific** 才可进 partial，仅 generic → failed。文内明确：这比粗二元成功/失败更可靠地服务 RL 奖励（§3.3.2）。

---

## 六、动作空间速览（附录 Table 7）

统一空间并把开源数据动作映射进来（Table 7 caption）。跟读分组：

- **共享**：Click / Drag / Swipe / DoubleClick / LongPress / Type / Wait / CallUser / Finished
- **Mobile**：PressBack/Home/Enter/Recent、LaunchApp、GetScreenshot、Answer
- **Desktop**：RightClick、Hotkey
- **Web**：Scroll、Launch(url)、GetUrl、TakeNote、Hover、Hotkey、SelectOption、PressBack/Home/Enter

推理侧（§4.1.1）：一般 agent 任务默认开 **think**，保留完整推理史进上下文；grounding **关推理、temperature=0**；CAPTCHA 支持 **multi-action** 解析。一般采样 temperature **1.0**，视觉分辨率用 Qwen3.5 默认配置。

---

## 七、评测字段（摘主表；对照声明保留）

**读表纪律（Figure 1 / 各表注）：** 偏 standalone 端到端、最近似任务子集与步数预算；源报告的 **action scaffold 可能不同**；`*` = 作者复现。本笔记只摘与「跨端闭环 + 验证叙事」相关的锚点分，不抄全表。

### 7.1 Mobile（Table 1）

| 基准 | UI-Venus-2-9B | UI-Venus-2-27B | 文内对照要点 |
|---|---:|---:|---|
| MobileGym | 52.7 | **60.5** | 超 Seed-2.0-Pro 52.0 |
| VenusBench-Mobile（149-task） | **46.5** | **48.7** | 复现 Opus-4.6 36.5* |
| AndroidWorld | 80.2 | **84.0** | 表内最强；文称该基准已较饱和 |
| MobileWorld GUI-only 117 tasks @50 steps（括号 @100） | 65.8 (75.2) | 76.1 (82.9) | @50 时 Qwen-UI-Agent-27B 报 82.1 |
| KnowUBench | 56.5 | 59.7 | — |
| MemGUI pass@1 | 62.6 | **70.3** | 超 Seed-2.0-Pro 65.6* |

### 7.2 Computer（Table 2）

| 基准 | 9B | 27B | 备注 |
|---|---:|---:|---|
| OSWorld-Verified | 70.8 | 80.5 | Claude-Opus-4.8 源报 83.4；文强调 scaffold 不可严格对齐 |
| DeskCraft（作者汇总 538-task Standard∪Interactive） | 48.0 | **55.5** | 超 Kimi-K2.6 41.4* |
| OSWorld 2.0 @150 steps（108 tasks）Binary / Partial | 0.0 / 7.5 | 2.8 / 13.2 | 长程仍弱；GPT-5.5 Binary 13.0 |

### 7.3 Web（Table 3）

| 基准 | 9B | 27B |
|---|---:|---:|
| WebVoyager（refreshed 595-task 协议） | 90.8 | **93.4** |
| Online-Mind2Web | 74.0 | **78.3** |
| REAL | 76.9 | **80.2** |
| Odysseys Avg / Perfect（200 tasks） | 77.3 / 62.0 | **80.4 / 66.3** |

### 7.4 Grounding / CAPTCHA / Safety（Table 4–6）

- **VenusBench-GD**（英指令 micro-avg）：9B **77.1** / 27B **80.1**（超 1.5-30B-A3B 的 75.0）。
- **VenusBench-CAPTCHA**（219 例 micro Pass@1）：9B **78.1** / 27B **79.9**（Qwen3.6-27B 53.0）。
- **安全 ASR↓（Table 6）**：OSHarm — 9B **11.3** / 27B **15.3**（Qwen3.5-27B 18.0）；OSBlind — 9B **48.8** / 27B **47.9**（基座对照文称 79.4 / 89.3）。
 - OSHarm：故意滥用 / 第三方注入 / 模型误行为；OSBlind：指令良性但环境潜藏伤害（§4.1.2）。

**诚实缺口：** 引言称「后续章节含 ablations」，但 TOC/抽取正文 **未见独立消融章节或消融表**；「safety-aware mechanisms」在 §1 有主张，**方法论未见独立安全训练小节**——安全证据主要落在 §4.2.6 评测。笔记不补未写机制。

---

## 八、与仓库其他议题的接口（一句）

| 议题 | 接口 |
|---|---|
| **[[智能体工具与长程任务]]** | 同属「长程 agent 可靠性」；本篇对象是 **GUI 像素控件闭环**，不是工具 API / MCP |
| **[[视觉语言动作谱系]]** | 同属「观测→动作」；本篇动作空间是 **Click/Type/Hotkey…**，不是机器人连续控制 |
| **[[GRPO与DAPO算法族]]** | Stage II 是离线 RL，但损失式指向 UI-Venus-1.5；勿在此重写 GRPO/DAPO 清单 |
| **[[多模态架构脉络]]** | 基座是多模态理解模型；本篇增量在 **交互轨迹 + 可验奖励 + 动作结构蒸馏** |

---

## 九、附录索引：BlueLM-GUI（勿升正文）

| 项 | 核验（arXiv API，2026-09-22） |
|---|---|
| 标识 | arXiv:**2609.12394v3** \[cs.AI\]；标题 *BlueLM-GUI Technical Report: A Real-Device-Centric Flywheel for Self-Improving Mobile GUI Agents* |
| 摘要抓手 | **真机中心** flywheel；三原则 Every Sample / Every Rollout Is Real / Every Query Evolves；模型 **35B-A3B**；报 MobileGUI-VBench **87.4**、AndroidWorld **84.9**（开源侧叙述） |
| 与本篇关系 | 同窗 mobile GUI agent TR，侧重 **真机分布与自改进飞轮**；UI-Venus-2 侧重 **跨端统一闭环 + 验证器扩 RL 信号**。按 wave4 议程：**仅索引，不另开同题笔记** |

---

## 十、可跟读金句 / 误区

**金句**

- 「reinforcement learning is only as reliable as the data quality verifier that supplies its reward.」（§1）
- 「the action is the sole interface through which the agent interacts with and changes the environment.」（§2.4）
- SGV：「does not rely on the agent’s self-declared success」（§3.3.1）

**误区**

1. 把 UI-Venus-2 读成「又一个 grounding SOTA」——文内主线是 **环境×任务×验证** 共扩与 **MOPD 合专家**。
2. 把 SGV 四分类直接当 RL 标量奖励——文内定位是 **策展分层**；逐步四分类才直接服务 step-level 监督叙事。
3. 用 OSWorld-Verified 分数做严格头对头——作者已声明 **scaffold 不同**。
4. 把本篇写成 ReAct/MCP 或机器人 VLA——划界见文首。

---

## 十一、待核实 / 未在正文展开

- Offline RL 的具体目标函数、组大小、KL 等 → 指向 UI-Venus-1.5，本 PDF 未复述。
- 「multi-model voting」席位与聚合规则。
- Safety-aware **训练/门控** 实现细节（仅有评测 ASR）。
- 引言预告的 ablations 表。
- BlueLM-GUI 全文对照（若后续要做 mobile 真机专线再开，不在本笔记扩写）。

## 相关笔记

- [[Gemma4技术报告深读|Gemma 4]]
- [[AXK2技术报告深读|AX-K2]]
- [[UIVenus2GUI智能体|UI-Venus-2]]
- [[宪法分类器防御|Constitutional Classifiers]]
- [[过程奖励模型PRM谱系|Process Reward Models]]

