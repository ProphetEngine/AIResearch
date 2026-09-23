---
title: "Open robotics stacks 增量：LeRobot（相对 12）"
topic: LeRobot开源栈
date: 2026-09-22
lines: [架构思想]
status: archived
sources:
 - https://arxiv.org/abs/2602.22818
 - https://arxiv.org/abs/2310.08864
arxiv: ["2602.22818", "2310.08864"]
related: ["视觉语言动作谱系", "代码智能体Harness史线"]
archived: 2026-09-22
---

# Open robotics stacks 增量：LeRobot（相对 12）

> **定位**：开源机器人学习栈横切——在 **[[视觉语言动作谱系]]**（VLA 策略谱系：RT-2 → OpenVLA → π₀）之上，补一条 **开源端到端机器人学习栈 + 数据集标准** 增量轴；主锚为 Hugging Face **LeRobot**（arXiv **2602.22818**，ICLR 2026），对照锚为 **Open X-Embodiment（OXE）** 数据集仓（arXiv **2310.08864**）。
> **攻坚线**：**架构思想（主）**——垂直集成（middleware → 数据 → 算法 → 异步推理）；**数据集标准（辅）**——`LeRobotDataset` vs OXE 的 **RLDS**。
> **硬划界**：
> - **禁止重写** [[视觉语言动作谱系]] 中 **RT-2 / OpenVLA / π₀** 的策略全文（动作离散化、co-fine-tune、flow matching、成功率表等只允许 **一句交叉指针**）。
> - **OpenHands / 软件工程 coding agent** → **[[代码智能体Harness史线]]**；本项 **不混入**。
> - **禁止编造**：下载量、数据集数、参数量、延迟、成本等一律取自官方 PDF（2026-09-22 CST）。
> - 本卡写的是 **库与数据标准**，不是再写一篇「新 VLA 论文复述」。

---

## 一、材料元信息

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主锚** | Cadene et al., *LeRobot: An Open-Source Library for End-to-End Robot Learning* | arXiv:**2602.22818v1** \[cs.RO\] **26 Feb 2026**（ICLR 2026）；`https://arxiv.org/abs/2602.22818`（**20** 页） | 开源端到端栈：硬件 middleware、数据集、SOTA 算法参考实现、异步推理 |
| **对照锚** | Open X-Embodiment Collaboration, *Open X-Embodiment: Robotic Learning Datasets and RT-X Models* | arXiv:**2310.08864v9** \[cs.RO\] **14 May 2025**；`https://arxiv.org/abs/2310.08864`（**12** 页）；项目页 https://robotics-transformer-x.github.io/ | **数据集标准 / 跨具身仓**：22 embodiments、RLDS；RT-X 仅作「仓上模型」存在性，**不**展开策略 |

**一句话抓手：** [[视觉语言动作谱系]] 回答「**策略怎么把观测变成动作**」；本卡回答「**开源社区如何用一套库把硬件控制、数据格式、训练/部署串成可复现栈**」——LeRobot 是垂直集成，OXE 是更早的跨具身 **数据集聚合标准**。

---

## 二、议题边界：相对 [[视觉语言动作谱系]] 的增量轴

### 2.1 跟读对照表

| 轴 | **[[视觉语言动作谱系]] Robotics VLA** | **本卡 LeRobot / OXE** |
|---|---|---|
| 主对象 | VLA **策略架构**（离散 token vs flow） | **库栈 + 数据集 schema + 推理部署** |
| 典型问题 | $o, \text{lang} \to a$ 怎么表示与训练 | 电机接口、遥操作采集、流式大数据、action chunk 异步执行怎么工程化 |
| RT-2 / OpenVLA / π₀ | **正文** | 只作「库内已挂载的算法名」或「OXE 上曾训过 RT-X」的 **指针** |
| OpenHands 等 SE agent | 无关 | **禁止混入**（→ [[代码智能体Harness史线]]） |

### 2.2 刻意不写什么

- RT-2 的 bin/token、OpenVLA 的 SigLIP∥DINOv2 + LoRA、π₀ 的 action expert / flow 损失与 Hz 叙事全文（见 [[视觉语言动作谱系]]）。
- OXE 文内 RT-1-X / RT-2-X 的完整实验表与「跨具身正向迁移」分项（本卡只保留数据集侧事实）。
- 具体 BOM 焊接/装配操作手册、电机固件刷写步骤。
- 软件工程 coding agent / OpenHands harness。

---

## 三、LeRobot 主张的问题：碎片化栈

据 §2.3，机器人学习生态的三大摩擦：

1. **Disaggregated Middleware**：中间件常按平台定制，团队被迫做一次性适配。
2. **Datasets and Formats**：TFDS、ROS bag、自定义 JSON 并存，缺少统一、多模态 schema → 难把分散数据拼成 mixture。
3. **Learning Frameworks**：实现细节 + 硬件差异放大不可复现性。

摘要与 §1 的对策：**垂直集成**——从低层电机 middleware，到大规模采集/存储/流式读取，再到 SOTA 算法的高效实现，以及 **广义异步推理栈**；强调可及硬件、可扩展具身、可复现管线。

跟读：**LeRobot 卖的不是「又一个 π₀ 架构论文」，而是把隐式学习（implicit / end-to-end policy）所需的周边系统钉成开源默认路径。**

---

## 四、垂直栈四块（Features）

`
低成本遥操作硬件 ──► 统一 Python middleware（读 leader / 写 follower）
 │
 ▼
 采集 → LeRobotDataset（+ Streaming）
 │
 ▼
 PyTorch 参考实现（RL / BC / 小 VLA）←→ HF 上公开权重
 │
 ▼
 异步推理：物理解耦（远端算力）+ 逻辑解耦（chunk 队列 + 聚合 f）
`

### 4.1 可及真实机器人（§3.1）

文称当前支持多款真机（静/动操作）：**SO-100 / SO-101**（单臂与双臂）、**Koch-v1.1**、**ALOHA-2**、**Hope-JR** 人形臂、**Stretch-3**、**LeKiwi** 移动操作、**Reachy-2** 等。共享 middleware：遥操作时读 leader 配置写到 follower；部署时用学到的策略直接控 follower。底层对接 FeeTech / Dynamixel 等低成本舵机 SDK；设计强调可扩展与可组合。

Table 1a 给出带公开 BOM 的成本量级（美元量级，文内写法）：例如 SO-100/101 操作臂约 **∼225**（双臂约 **550**）；Koch-v1.1 约 **∼670**（双臂约 **1346**）；ALOHA 约 **∼21k**；HopeJR-Arm 约 **∼500**；LeKiwi 约 **∼230**。叙事对比：相对闭源工业臂，低端开源平台可支撑 **去中心化** 大规模演示采集（§2.1 / Figure 4）。

### 4.2 数据集：`LeRobotDataset`（§3.2 + Appendix C）

| 项 | 论文事实 |
|---|---|
| 目标 | 统一多模态 schema：高频传感运动读数、多路相机、遥操作状态；自包含元数据（任务文本描述、具身、FPS、传感器类型等） |
| 规模快照 | 截至 **2025 年 9 月**：**16K+** 数据集、**2.2K+** 独立贡献者以该格式公开分享 |
| 覆盖 | 库内原生机器人（如 SO-10X）+ 社区移植的 Franka / xArm / R1Pro 等 |
| 存储形态（App. C.1） | 表格记录 **`.parquet`** + 压缩视频 **`.mp4`** + 轻量 metadata；流式时 metadata 全量下载，大体量视频/控制流 **按需** 拉取 |
| 流式 API | `StreamingLeRobotDataset`：远端按帧取数，不必整库落地；`IterableDataset` + **torchcodec** 在线解码 |
| 生态趋势（文内解读） | 下载量/体量上 Franka、xArm 等研究向集中采集仍领先；**数据集数量**上 SO-10X 等低成本平台在去中心化贡献中占比高（文称 **50%+** 数据集直接采自 SO-10X，Figure 5d） |

**与训练配方的接口（跟读）：** 同一格式既服务「几十条轨迹的小规模 ACT」，也服务「百万 episode 级」的流式大库——这是栈层增量，不是策略层增量。

### 4.3 算法参考实现（§3.3）——只列「挂载名」，不重写策略

库内提供多范式 **纯 PyTorch** 参考实现，可从头训、也可加载公开预训练权重；文称可在 **<100 LOC** 训、**<40 LOC** 服务（Appendix D）。

| 范式 | 文内点名实现 |
|---|---|
| RL | **HIL-SERL**、**TD-MPC** |
| 单任务 BC | **ACT**、**Diffusion Policy**、**VQ-BET** |
| 多任务 / 语言条件 | **π₀**、**SmolVLA** |

社区上传趋势（Figure 7）：**ACT** 因体量小、推理快、约 **50** 条真实轨迹即可得到可用策略而占上传主导；作为单任务模型，条件一变需重训。**SmolVLA** 文内定位为较小规模、语言条件可控的真机 VLA，适用面更宽。

**相对 [[视觉语言动作谱系]] 的硬停：** π₀ / 离散 VLA 的架构与训练配方 **不在此复述**——此处只记录「LeRobot 把它们收成可跑的库组件」。Table 2/3 给出 fp32、扩散/flow **10** 步去噪设定下的峰值显存与平均推理延迟（CPU / MPS / RTX 4090 / A100）；例如 ACT **52M** 在 4090 上约 **5 ms** 量级延迟，π₀ **3.5B** 明显更重且在低端设备上可超时。跟读用途：**部署成本对照**，不是策略 SOTA 表。

### 4.4 异步推理（§3.4 / Figure 8）

现代 BC 策略多输出 **action chunk** $a_{t:t+H-1}$（文称库内 BC 均如此）。LeRobot 自定义推理栈做两层解耦：

1. **物理解耦**：推理可跑在网络对端的更强机器上；机器人侧低层控制器按目标控制频率逐步执行收到的动作。
2. **逻辑解耦**：生产者–消费者异步——推理以 lookahead $H$ 与控制环并行；重叠 chunk 用可定制聚合函数 $f$ 合并，尽量保证队列非空、减少机器人空闲。

跟读：**这是「策略输出 chunk」之后的系统层答案**；[[视觉语言动作谱系]] 写 chunk 从哪来，本卡写 chunk 怎么稳地喂给电机环。

### 4.5 仿真定位（§4）

核心焦点是 **真机**；仿真主要用于算法系统评测。接触丰富任务在仿真中仍难，故训练尽量吃真机数据。评测侧原生接入 **LIBERO**（含 Spatial / Object / Goal / 90 / Long 等套件叙事）与 **Meta-World**（MT / ML 套件），报告成功率等协议——**不**把本卡写成仿真基准通史。

---

## 五、对照：Open X-Embodiment 的数据集标准增量

### 5.1 OXE 仓在「标准」上提供了什么

据摘要与 §III.A：

| 项 | 事实 |
|---|---|
| 规模 | **1M+** 真实机器人轨迹；**22** 种具身；来自 **21** 机构协作；汇聚 **60** 个既有数据集（文亦写 34 个实验室来源） |
| 技能 / 任务 | **527** skills（**160266** tasks） |
| 具身跨度 | 单臂、双臂、四足等 |
| 存储标准 | **RLDS** 格式（序列化 **tfrecord**）；容纳不同动作空间与输入模态（多 RGB / 深度 / 点云等）；宣称主流深度学习框架可高效并行加载 |
| 仓目标 | 不只是「再发一个数据集」，而是标准化聚合 + 工具，推动 **X-embodiment** 研究；另提供 RT-X 检查点——**本卡不展开 RT-X 策略** |

Figure 2 侧写：Franka 场景多样性高；xArm 与 Google Robot 因若干大库贡献轨迹最多；技能长尾含 wipe / assemble 等。

### 5.2 LeRobotDataset vs OXE/RLDS（跟读对照）

| 维度 | **OXE（对照锚）** | **LeRobotDataset（主锚）** |
|---|---|---|
| 时代角色 | 跨实验室 **集中策展式** 大库 + 统一 RLDS，服务 X-embodiment 预训练研究 | **库内原生 schema** + HF 生态上的 **去中心化** 贡献与流式消费 |
| 格式技术栈 | RLDS / tfrecord | parquet + mp4 + metadata；PyTorch 友好；`StreamingLeRobotDataset` |
| 与硬件栈关系 | 数据仓为主，不绑定某一 middleware | 与遥操作 middleware、采集、训练、异步推理 **同一库** 闭环 |
| 与 [[视觉语言动作谱系]] 关系 | OpenVLA 等曾用 OXE 策展子集（见 [[视觉语言动作谱系]]，不重复） | 把 π₀ / SmolVLA / ACT 等 **实现** 接进同一数据接口 |
| 本卡写法 | **标准对照**，不写 RT-1-X/RT-2-X 全文 | **主写栈** |

跟读金句压缩：**OXE 把「很多实验室的数据」收成可训的统一仓；LeRobot 把「从买得到的臂 → 采得到的数据 → 训得动的策略 → 跑得稳的 chunk 控制」收成可复现的开源默认路径。**

---

## 六、局限（作者自述，§5）

1. **机器人覆盖不全**：2025 年内从 3 套操作配置扩到文称 **8** 类常规/人形/移动操作平台，仍远非穷尽。
2. **算法覆盖非穷尽**：关键范式有强可复现实现，更多算法留给社区扩展。
3. **推理性能工程**：量化、图编译等低层优化「当前库未纳入」，实践强性能仍需额外优化。

---

## 七、跟读清单（可闭卷复述）

1. **相对 [[视觉语言动作谱系]]：** 那边是 VLA **策略谱系**；这边是开源 **端到端学习栈 + 数据标准**；禁止把 RT-2/OpenVLA/π₀ 正文搬过来；OpenHands 不进本卡。
2. **LeRobot 四块：** 统一 middleware ↔ `LeRobotDataset`（+ 流式）↔ PyTorch SOTA 参考实现 ↔ 异步 chunk 推理（物理+逻辑解耦）。
3. **数据快照：** 2025-09 口径 **16K+** 集 / **2.2K+** 贡献者；存储 = parquet + mp4。
4. **OXE 对照：** **1M+** 轨迹、**22** 具身、**RLDS/tfrecord** 的跨机构聚合仓；与 LeRobot 是「标准/仓」vs「垂直栈」互补，不是互相替代的同一篇策略论文。
5. **禁编造：** 延迟/显存/成本以文内 Table 为准；不把库内挂载名写成「本笔记新训出的 SOTA」。

---

## 八、引用

- Cadene, R., Aliberts, S., Capuano, F., et al. *LeRobot: An Open-Source Library for End-to-End Robot Learning*. arXiv:2602.22818, ICLR 2026.
 - abs: https://arxiv.org/abs/2602.22818
 - pdf: https://arxiv.org/pdf/2602.22818
 - 本地: `https://arxiv.org/abs/2602.22818`
- Open X-Embodiment Collaboration. *Open X-Embodiment: Robotic Learning Datasets and RT-X Models*. arXiv:2310.08864, 2023–2025.
 - abs: https://arxiv.org/abs/2310.08864
 - pdf: https://arxiv.org/pdf/2310.08864
 - 项目页: https://robotics-transformer-x.github.io/
 - 本地: `https://arxiv.org/abs/2310.08864`
- （指针，不展开）[[视觉语言动作谱系]]：多模态与具身/机器人与VLA/视觉语言动作谱系.md — RT-2 / OpenVLA / π₀ 策略正文。
- （划界）[[代码智能体Harness史线]]：Harness/智能体与工具/代码智能体Harness史线.md — OpenHands 等软件工程 agent，**本项不混入**。

## 相关笔记

- [[GaussianDreamer三维生成|GaussianDreamer]]
- [[LeRobot开源栈|LeRobot]]

