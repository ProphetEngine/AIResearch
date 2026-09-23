---
title: "Agentic workflow 生成基准：WorfBench + WorFEval"
topic: WorfBench工作流基准
date: 2026-09-22
lines: [评测字段, 架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2410.07869
 - https://arxiv.org/abs/2410.07869
arxiv: ["2410.07869"]
related: ["智能体工具与长程任务", "代码智能体Harness史线", "计算机使用智能体", "多智能体辩论", "VendingBench经营长程评测", "评测与排行榜可靠性"]
github: "https://github.com/zjunlp/WorfBench"
iclr_pdf: "https://proceedings.iclr.cc/paper_files/paper/2025/file/adbe936993aa7cf41e45054d8b72f183-Paper-Conference.pdf"
hf_collection: "https://huggingface.co/collections/zjunlp/worfbench-66fc28b8ac1c8e2672192ea1"
project: "https://zjunlp.github.io/project/WorFBench/"
archived: 2026-09-22
---

# Agentic workflow 生成基准：WorfBench + WorFEval

> **定位**：工作流评测主题轴——相对 **[[智能体工具与长程任务]]**（旗舰工具环 / 长程产品叙述）与 **[[代码智能体Harness史线]]**（编码 ACI / 沙箱 harness），补仓库缺失的 **「把复杂任务分解为可执行 DAG 工作流」生成质量** 评测轴。锚点是浙大 / 阿里 *Benchmarking Agentic Workflow Generation*（arXiv **2410.07869v3**，**ICLR 2025**）：基准 **WorfBench** + 协议 **WorFEval**（子序列 / 子图匹配）。
> **攻坚线**：**评测字段（主）**——$f1_{\mathrm{chain}}$ vs $f1_{\mathrm{graph}}$、四场景、held-out、端到端增益与并行耗时；**架构思想（辅）**——节点链 → DAG、工作流作先验 / CoT 增强 / 并行缩短路径。
> **硬划界**：
> - **≠ [[智能体工具与长程任务]]**：不写 MCP / ReAct / System Card 长程产品通史；本卡测的是 **规划图是否对**，不是工具环上能否跑完。
> - **≠ [[代码智能体Harness史线]]**：不写 SWE-agent ACI / OpenHands SDK / Docker 沙箱；本卡无「改仓库执行」闭环。
> - **≠ [[计算机使用智能体]]**：不是桌面 GUI / OSWorld / Operator；embodied 源（ALFWorld 等）只作 **工作流图构造数据源**。
> - **≠ [[多智能体辩论]]**：不是多代理辩论协议；文中 multi-agent 仅作「可能改进生成」的一句相关工作。
> - **≠ [[VendingBench经营长程评测]]**：不是经营净值 / meltdown 长程连贯。
> **禁止编造**：表数字、过滤率、超参一律锚定官方 PDF（2026-09-22 CST）。图内未列表格的点位不读点；§3.1「共 18 模型」与 Table 1 行数不一致处 **以表为准并标注**。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Qiao, Fang, Qiu, Wang, Zhang, Jiang, Xie, Huang, Chen（ZJU / Alibaba）, *Benchmarking Agentic Workflow Generation* | arXiv:**2410.07869v3** \[cs.CL\] **23 Feb 2025**；页眉 *Published as a conference paper at ICLR 2025*；`https://arxiv.org/abs/2410.07869`（**25** 页 letter；CreationDate **2025-02-25** CST；3,430,519 bytes） | 一手：任务形式、构造与质控、WorFEval、主表、下游作用 |
| **备·ICLR** | 同题会议 PDF | `https://arxiv.org/abs/2410.07869`（3,229,575 bytes）；https://proceedings.iclr.cc/paper_files/paper/2025/file/adbe936993aa7cf41e45054d8b72f183-Paper-Conference.pdf | 议程备链；本笔记数字以 arXiv 官方 PDF 为准 |
| **代码 / 数据** | zjunlp/**WorfBench** | https://github.com/zjunlp/WorfBench ；HF collection `zjunlp/worfbench-…`；项目页 https://zjunlp.github.io/project/WorFBench/ | `gen_workflow` / `eval_workflow`；训练参考 LLaMA-Factory |

**一句话抓手：** 现有 agent 评测多看 **端到端成败** 或 **线性分解**；WorfBench 把「子任务 + 依赖」建成 **DAG（含并行）**，WorFEval 用 **语义匹配 + LIS（链）+ MCIS（图）** 给出可复现的 $f1_{\mathrm{chain}}$ / $f1_{\mathrm{graph}}$——主发现是 **图规划系统性地难于线性规划**（闭源里 GPT-4 平均约 **67.32% → 52.47%**，差距约 **15%**）。

---

## 二、议题边界：测「规划图质量」，不是执行闭环

### 2.1 相对已入库只取接口

| 已入库 | 本卡只取 | 本卡不写 |
|---|---|---|
| **[[智能体工具与长程任务]]** 工具 / 长程 | 「多步任务需分解与依赖」的抽象动机；文中 ReAct 仅作构造管线格式 | MCP、旗舰 System Card、产品 SLA |
| **[[代码智能体Harness史线]]** harness | 「可执行粒度」与环境反馈存在 | ACI 命令面、沙箱 SDK、SWE-bench resolve |
| **[[计算机使用智能体]]** CUA | embodied 源名（ALFWorld / WebShop / OS） | 截图键鼠、OSWorld 2.0 长程桌面分 |
| **[[多智能体辩论]]** MAD | （无接口；仅划界） | 辩论轮次 / 去共识 |
| **[[VendingBench经营长程评测]]** Vending | （无接口；仅划界） | 净值、销售停滞、meltdown |

### 2.2 文内对立轴（跟读 §1）

既有评测三缺陷（文原文压缩）：

1. **场景窄**：多限 function calling 或纯推理。
2. **只看线性依赖**：现实常有 **并行** 的图结构（Fig.1）。
3. **评分解松**：过度依赖 GPT-3.5/4 判分，自身也有幻觉。

WorfBench 四特征（§1 bullet）：多场景；DAG 工作流；节点链中介 + 拓扑排序质控 + 人工核验；WorFEval 定量匹配。

---

## 三、架构思想（辅）：节点链 → DAG，再当下游先验

### 3.1 任务形式（§2.1）

给定任务描述 $q$、候选动作表 $A$（API / 工具 / embodied 动作或其混合）与模型 $M_\theta$：

$$
G(V,E) \leftarrow M_\theta(q,A)
$$
$G$ 为 **DAG**：节点 $V$ 是 **最小可执行粒度** 的子任务；边 $(v_i,v_j)$ 表示 $v_j$ 须在 $v_i$ 之后执行。另加 **START / END**。

直接生成图对 LM 不友好，故引入 **节点链** $C(V)$（图的一条拓扑序）：

$$
G(V,E) \leftarrow C(V) \leftarrow M_\theta(q,A)
$$
即先产节点序列，再为节点编号后产边。

### 3.2 构造管线（§2.2 · 跟读地图）

| 场景族 | held-in 源 | 节点链怎么来 | 备注 |
|---|---|---|---|
| **Function Call** | ToolBench、ToolAlpaca | 金标 function call → GPT-4 反推 thought → 执行得 observation → few-shot 产每步 node | held-out：**Seal-Tools** |
| **Embodied** | ALFWorld、WebShop、OS（轨迹自 ETO / AgentInstruct） | 按任务类人工设计 few-shot，GPT-4 据金标轨迹合成链（非「一动作一节点」） | held-out：**InterCodeSQL** |
| **Problem-Solving** | LUMOS-O（数学 / 常识 / 多模态推理） | 已有规划链 → 统一格式 | — |
| **Open-Grounded** | WikiHow | 已有过程链；无动作表则从公开动作库检索相似项作干扰 + 金标动作混合 | 提高选动作难度 |

边：对链中节点编号后由 GPT-4 生成边集。

### 3.3 质控（§2.3 · 可核数字）

| 阶段 | 做法 | 过滤比例（文） |
|---|---|---|
| **节点链**（主攻 function call） | 用节点检索函数列表；与金标不对齐则丢 | **15.36%** |
| **工作流图** | 对 GPT-4 图做拓扑排序（入度 0 时按节点号升序打破平局）；与节点链不一致则丢 | **29.77%** |
| 复杂度 | 丢仅 1 节点或 1 边的样本；过量场景随机下采样后划分 train/test；**测试集人工核验**（App. A.2：粒度 / 逻辑 / 任务质量） | — |

### 3.4 下游：工作流能干什么（§4 · 辅线）

1. **结构化先验**：把生成工作流塞进提示，引导规划（Table 3）。ALFWorld 上 GPT-4 seen **27.14→40.71**（↑13.57）、unseen **28.36→47.01**（↑18.65）；WebShop 增益较小（**55.62→56.49**）。工作流由 **微调后的 Qwen-2-7B** 生成，仍能抬更高参数模型——文称 **weak-guide-strong**。
2. **CoT 增强（function call）**：逐步按节点产 CoT，并用节点检索最相似 API，再决定如何调用；StableToolBench 上相对 ToolLlama / one-shot GPT-4 / Qwen-2-72B 有相对准确率优势（Fig.5，读图不臆造精确百分点）。
3. **并行减耗时**：无依赖节点可并行；以关键路径（Critical Path）估完成时间，相对逐步 ToolLlama，平均耗时约减 **1/5～1/3**（Fig.6 文述）。
4. **缩短规划步数**：先验减少盲目试错（Table 4：如 GPT-4 ALFWorld seen **17.19→15.64**）。

---

## 四、评测字段（主）：WorFEval

### 4.1 匹配前处理（§2.4）

- 节点语义：Sentence-BERT **`all-mpnet-base-v2`**，余弦相似度 $\sigma$。
- 阈值 $\beta=\mathbf{0.6}$（§3.1）：$\sigma<\beta$ 视为不匹配。
- 相似度矩阵上做 **最大权二分图匹配**，得到一一对应的匹配节点集 $V^{g\prime}$、$V^{p\prime}$。

### 4.2 节点链分：$f1_{\mathrm{chain}}$（最长递增子序列）

- 金标图取最多 **20** 条拓扑序（复杂度控制；理由见 App. A.9）。
- 将预测匹配节点映射回金标序号，对每条金标拓扑序算 **LIS** 长度，取最大 $l$。
- $p_{\mathrm{chain}}=l/|V^p|$，$r_{\mathrm{chain}}=l/|V^g|$，再合成 **F1**。

跟读口诀：**「顺序对不对」**——允许预测多插/漏节点，但匹配上的相对序要落在某条合法拓扑序里。

### 4.3 工作流图分：$f1_{\mathrm{graph}}$（最大公共诱导子图）

- 在匹配节点诱导出的预测子图与金标图上做 **MCIS**，得共同诱导子图节点数 $k$。
- $p_{\mathrm{graph}}=k/|V^p|$，$r_{\mathrm{graph}}=k/|V^g|$，再合成 **F1**。

跟读口诀：**「边依赖对不对」**——节点语义对上还不够，诱导结构要对。

### 4.4 基准规模（App. A.3）

| 集合 | 规模 | 备注 |
|---|---|---|
| Train | **18,679** | 四类大致均衡（Fig.7） |
| Test | **2,146** | 其中 **33.69%** 为 held-out |
| 步数 | 多数 **2–10**；少量 10–20；全库平均节点数 **4.17** | Fig.8 |

---

## 五、主结果跟读（Table 1 / Q1–Q4）

### 5.1 实验设定（§3.1）

- 提示：统一精心设计指令 + **two-shot**；解码默认超参，**temperature = 0.5**。
- 框架：LlamaFactory；≥70B 用 vLLM。
- Table 1 列：**闭源 4**（Claude-3.5 / GPT-3.5 / GPT-4 / O1-preview）+ **开源 15**（7B–72B 各系列）。文 §3.1 写「共 **18** 模型」，与 4+15=19 不一致——**跟读以 Table 1 为准**。

### 5.2 闭源平均与「约 15% 差距」（摘要 / Table 1）

| 模型 | $f1_{\mathrm{chain}}$ Avg | $f1_{\mathrm{graph}}$ Avg | 差（百分点） |
|---|---:|---:|---:|
| Claude-3.5 | 66.70 | **52.53** | 14.17 |
| GPT-3.5 | 63.86 | 48.02 | 15.84 |
| **GPT-4** | **67.32** | 52.47 | **14.85**（摘要「约 15%」） |
| O1-preview | 66.70 | 51.63 | 15.07 |

开源顶栏（同表）：Qwen-2-72B Avg **67.24 / 50.46**；Llama-3.1-70B **64.60 / 49.59**。
文 Q1：图分全面低于链分；平均差最大 **GLM-4-9B 20.05%**，最小 **Llama-3.1-70B 15.01%**。

**场景难度（跟读）：** Open-Grounded 最难——Claude-3.5 仍仅 **61.33 / 42.88**；Function Call 上 GPT-4 链分最高 **74.87**，图分 **62.11**。O1-preview 在 Problem-Solving 上图分领跑闭源 **59.25**，但 Function Call / Embodied / Open-Grounded 不占优（文：缺环境知识）。

### 5.3 Scaling 与「距专家还远」（Q2–Q3）

- 同系列放大：Qwen-2 **72B vs 7B** 图分 **+6.77%**；Llama-3.1 **70B vs 8B** 图分 **+11.51%**。
- 部分新 7B 超过多数旧 13B：文归因数据质量 / 世代，而非否定参数规模。
- 即便金标由图由 GPT-4 合成，**直接生成**时 GPT-4 平均仍只 **67.32 / 52.47**；节点边数增多时性能趋势下降（Fig.3，读图）。

**微调泛化（Table 2）：** 全参微调 Qwen-2-7B / InternLM-2.5-7B（App. A.5：cutoff 4096、3 epoch、lr $1\mathrm{e}{-5}$、3×A100-80G 等）。

| 模型 | Held-in Avg $f_{\mathrm{chain}}/f_{\mathrm{graph}}$ | Seal-Tools | InterCodeSQL |
|---|---|---|---|
| GPT-4 | 67.32 / 52.47 | 96.58 / 80.25 | 66.35 / 54.36 |
| Qwen-2-7B+FT | **79.35 / 70.38** | **96.49 / 82.82** | 62.37 / 48.72 |
| InternLM-2.5-7B+FT | 78.98 / 69.33 | 95.83 / **83.72** | 63.78 / 50.97 |

跟读：held-in 可大幅超过 GPT-4；Seal-Tools（平均约 2–3 节点，文述较简单）图分略超 GPT-4；**更复杂的 InterCodeSQL 上 FT 未稳定超越 GPT-4**——文结论：结构化工作流规划 **不能只靠拟合大量数据** 学到强泛化。

### 5.4 给金标链只预测边（Table 5 · 消融）

缓解粒度 / 显式性错误后，平均 $f1_{\mathrm{graph}}$ 仍大幅上升但未「解决」：如 GPT-4 **52.47→74.63**，Claude-3.5 **52.53→75.72**，Qwen-2-72B **50.46→69.21**。文判断：**依赖关系本身仍难**。

### 5.5 错误类型（Q4 / Fig.4）

人工归类 GPT-4 低分（$f1_{\mathrm{graph}}<0.5$）样本四类：**Granularity**（粒度不符最小可执行）、**Explicitness**（子任务过空泛）、**Graph**（节点对但边错）、**Format**（输出格式不合）。文归因多与 **环境知识不足** 相关，并指向 world knowledge / world model 集成（不在本卡展开）。

---

## 六、开源仓怎么用（跟读 README，非 walkthrough）

仓库任务名：`wikihow` / `toolbench` / `toolalpaca` / `lumos` / `alfworld` / `webshop` / `os`。

- **生成：** `python node_eval.py --task gen_workflow … --few_shot`
- **评测：** `--task eval_workflow --eval_type node`（另有 graph 模式）`--eval_model all-mpnet-base-v2`
- 训练模块改编自 LLaMA-Factory；端到端评测参考 IPR / StableToolBench。

数据入口：HF collection（README 链）；本卡不下载全量、不复跑分数。

---

## 七、可带走的结论（三句）

1. **评测字段**：agent「会不会规划」应拆成 **链序（LIS-F1）** 与 **图依赖（MCIS-F1）**；只报端到端成功率会掩盖 **系统性的图规划缺口（约 15+ 百分点）**。
2. **架构思想**：工作流 = **可并行 DAG 先验**——既能抬 embodied / tool 端到端，又能用关键路径砍推理墙钟时间，也能当逐步 CoT / 检索查询。
3. **上限意识**：合成金标 + 强提示下 GPT-4 图分仍约半成；微调抬 held-in 不等于抬复杂 held-out——下一步更像 **环境/世界知识**，而非更大 few-shot。

---

## 八、刻意不写 / 待核实

| 项 | 处理 |
|---|---|
| Fig.3 / 4 / 5 / 6 精确点位 | 未列表格化数字处 **不读点**；仅用文内已写百分数 / 区间 |
| §3.1「18 models」 | 与 Table 1 行数冲突 → 标注，以表为准 |
| 训练 loss 曲线、全量逐模型逐格复述 | 主表已给闭源全行列 + 开源 Avg；细格按需回 PDF |
| 与 PlanBench / ToolBench 端到端榜的横向对齐 | → 需要时交叉 **[[评测与排行榜可靠性]]**；本卡不重写榜可靠性通史 |
| World model 文献深读 | 文仅作改进方向指针 → 另卡 |

**本地核验命令备忘：**
` https://arxiv.org/abs/2410.07869` → （2026-09-22 CST）。

## 相关笔记

- [[DiffusionForcing族|Diffusion Forcing]]
- [[WorfBench工作流基准|WorfBench]]
- [[合成对齐数据Magpie|Magpie / ActiveUltraFeedback]]
- [[EntMTP熵引导投机解码|EntMTP]]
- [[DuoAttention与KVzip|DuoAttention / KVZip]]

