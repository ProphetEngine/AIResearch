---
title: "交互视频世界模型增量：Matrix-Game 3.0 + Cosmos WFM 平台（≠ V-JEPA）"
topic: MatrixGame与Cosmos
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
aux:
 - https://arxiv.org/abs/2604.08995
 - https://arxiv.org/pdf/2604.08995
 - https://arxiv.org/abs/2501.03575
 - https://arxiv.org/pdf/2501.03575
 - https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/
arxiv: ["2604.08995", "2501.03575"]
related:
 - "世界模型与VJEPA"
 - "视频生成正式报告"
 - "DiffusionForcing族"
 - "视觉语言动作谱系"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 交互视频世界模型增量：Matrix-Game 3.0 + Cosmos WFM 平台（≠ V-JEPA）

> **定位**：交互生成式世界模型增量——在 **[[世界模型与VJEPA]]** 已立「非生成式 JEPA 表征预测」之后，本卡只写 **交互 / 流式生成式世界模型** 增量切片：
> - **Matrix-Game 3.0**（Skywork AI）：**实时流式交互 WM** + **相机感知长程记忆** + 工业数据引擎 + few-step 蒸馏部署（720p / 至约 40 FPS）。
> - **Cosmos World Foundation Model Platform**（NVIDIA）：**Physical AI 世界基础模型平台**——视频策展 / 连续·离散 tokenizer / 扩散与自回归预训练 WFM / 后训练样例 / guardrail。
> **对照（不升主）**：**Genie 3** 仅有 DeepMind 博文（2025-08-05）、**无正式 PDF TR** → 本波不作主锚，仅作产品对照一句。
> **攻坚线**：**架构思想 / 平台接口（主）** + **文内交互一致性 / 吞吐字段（辅）**。
> **硬划界（开篇钉死，禁止滑向相邻卡）**：
> - **≠ [[世界模型与VJEPA]]**：禁止重写 JEPA **mask-denoising 表征预测**入门、V-JEPA 2 probe / VidQA / AC 后训练长文。本卡预测落在 **像素 / 潜视频生成**（动作条件交互或 Video2World），与表征空间 JEPA **正交**。
> - **≠ [[视频生成正式报告]]**：禁止写成 **文生视频旗舰正式报告缺口备忘**（Sora 等）。本卡对象是 **交互/流式 WM + Physical AI WFM 平台**，非「无可核长 TR」产品备忘。
> - **≠ [[DiffusionForcing族]]**：禁止重写 Diffusion Forcing → Self Forcing → Causal Forcing **训推对齐 forcing 族通史**。Matrix 文内引用 Self-Forcing / DMD / Causal Forcing 仅作 **蒸馏接口一句**，不展开族谱。
> - **≠ [[视觉语言动作谱系]]**：禁止写成 **Robotics VLA 控制部署通史**（RT-2 / OpenVLA / π0）。Cosmos 后训练含机器人 manipulation **样例**，本卡只录「预训练 WFM → 域内后训练」平台接口，不写闭环 VLA 策略谱系。
> **禁止编造**：主张与表数字一律锚定本地抽取（ + 博文 HTML 抽纯文本，2026-09-22 CST）。文内未给出的算力明细 / 未披露配方 → **不得外推**。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A** | Wang, Liu, Li, Huang, Xu et al.（Skywork AI）, *Matrix-Game 3.0: Real-Time and Streaming Interactive World Model with Long-Horizon Memory* | arXiv:**2604.08995**v2 \[cs.CV\] **13 Apr 2026**（abs：Submitted **10 Apr 2026**）；PDF **23,717,745** B ≈ **22.6MB**；**20** 页 letter | **实时流式交互 WM**：error-aware 基座 + 相机感知记忆 + multi-segment DMD 蒸馏 + INT8/VAE 剪枝 → **720p@~40FPS（5B）**；scale-up **MoE-28B / 2×14B** |
| **主文 B** | NVIDIA（Agarwal, Ali, Bala, … Liu et al.）, *Cosmos World Foundation Model Platform for Physical AI* | arXiv:**2501.03575**v3 \[cs.CV\] **9 Jul 2025**（abs：Submitted **7 Jan 2025**）；PDF **43,473,963** B ≈ **41.5MB**；**75** 页 A4 | **Physical AI WFM 平台**：策展→tokenizer→扩散/AR 预训练→后训练样例→guardrail；开源/开权重入口 **NVIDIA Cosmos-Predict1** |
| **对照（不升主）** | Parker-Holder & Fruchter（DeepMind）, *Genie 3: A new frontier for world models* | 博文 **2025-08-05**；https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/ → | **产品对照**：文生交互世界 **24 FPS / 720p / 数分钟一致性**；**无正式 PDF TR** → 不升主 |

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2604.08995` Matrix-Game 3.0 PDF | **22.6MB**（23,717,745 B） | 20 | **建议正式外链**（>20MB） |
| `2501.03575` Cosmos PDF | **41.5MB**（43,473,963 B） | 75 | **建议正式外链**（>20MB；页数亦偏长） |
| Genie 3 博文 | HTML→txt **~27K** | — | **链接+抽取**；**不升主**（无 PDF TR） |

**一句话抓手：**
- **Matrix-Game 3.0**：把「交互视频世界模型」做成 **可部署系统**——UE/AAA/真实四元组数据 + **自校正双向 DiT** + **相机感知记忆检索** + **多段 DMD 蒸馏**，在 5B 上冲 **720p 实时流式**。
- **Cosmos**：把「世界模型」做成 **可后训练的平台**——先大规模视频策展与 tokenizer，再预训练 **扩散 / 自回归** 两类 WFM，再用小数据后训练到相机控制 / 机器人 / 驾驶。
- **Genie 3（对照）**：闭源实时交互世界演示（博文宣称 24 FPS·720p·数分钟）；配方与栈未公开——本卡不跟。

---

## 二、议题边界：生成式交互 WM / WFM 平台 ≠ JEPA / 视频报告缺口 / Forcing 族 / VLA

### 2.1 四向对照（跟读）

| 轴 | 预测落在哪 | 交互 / 控制 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|---|
| **[[世界模型与VJEPA]] V-JEPA** | **表征空间** mask-denoising | AC 后训练接口 | [[世界模型与VJEPA]] | **否**（禁 JEPA 入门重写） |
| **[[视频生成正式报告]]** | 文生视频旗舰「正式报告」缺口 | 多为离线生成 | [[视频生成正式报告]] | **否** |
| **[[DiffusionForcing族]] Forcing 族** | 序列上 per-token 噪声 / 自 rollout | 训推对齐手法 | [[DiffusionForcing族]] | **否**（仅蒸馏引用） |
| **[[视觉语言动作谱系]] VLA** | 观测→动作策略 | 闭环机器人 | [[视觉语言动作谱系]] | **否**（Cosmos 机器人后训练仅样例） |
| **Matrix-Game 3.0** | **动作条件潜视频**流式生成 + 显式记忆 | 键鼠 / 相机；实时 | **本篇 A** | **是** |
| **Cosmos WFM** | Text2World / Video2World（扩散或 AR） | 后训练接相机位姿 / 指令 / 多视角 | **本篇 B** | **是** |
| **Genie 3** | 文生可导航交互世界 | 导航 + promptable events | **对照** | **索引 only** |

跟读直觉：[[世界模型与VJEPA]] 问「**世界如何在表征里可预测**」；Matrix 问「**人在键鼠下能否实时流式滚出分钟级一致世界**」；Cosmos 问「**如何先训通用 WFM 再便宜地后训练到 Physical AI 任务**」；Genie 3 是闭源产品演示位。四者可叠在「world model」外壳下，但**旋钮不同**——本卡禁止滑回 JEPA / Sora 备忘 / Forcing 通史 / VLA 谱系。

### 2.2 文内自划界（跟读）

- **Matrix §1 / Related**：点名 Genie 3「约 24 FPS·720p·分钟级」但 **未开源、细节不清**；Matrix-Game 2.0 / HY-Gamecraft-2 有实时流式但 **缺分钟级记忆**；Lingbot-World 靠扩上下文但难同时实时；本工作主打 **记忆一致性 × 高分辨率 × 真实时** 同框。Related 中 Diffusion Forcing / Self-Forcing / Causal Forcing / SVI 仅作 **长视频误差累积** 谱系，**不写 forcing 族通史**（→ [[DiffusionForcing族]]）。
- **Cosmos §1–2**：明确定义 $ \hat{x}_{t+1}=\mathcal{W}(x_{0:t},c_t) $ 的 **视觉 WFM**；用途列表含策略评估 / 初始化 / RL / MPC / 合成数据，但 **§2.1 明示本文不含将这些用途的实证结果**——本卡亦不外推。后训练机器人 / 驾驶 → **平台样例**，控制部署 → [[视觉语言动作谱系]]。
- **Genie 3 博文**：强调实时交互、数分钟一致性、promptable world events、与 SIMA 联调；**Limitation** 含有限动作空间、多 agent、真实地理精度、交互时长「数分钟而非数小时」——本卡只录对照，不升主。

`
 「world model」外壳（接口可取自 [[世界模型与VJEPA]] 定义句，正文不写 JEPA）
 │
 ┌────────────────────┼────────────────────┐
 ▼ ▼ ▼
 Matrix-Game 3.0 Cosmos WFM 平台 Genie 3（对照）
 实时流式交互+记忆 策展/Tokenizer/预训练/后训练 闭源博文演示
 本篇 A 本篇 B 索引 only
`

---

## 三、主文 A：Matrix-Game 3.0（2604.08995）

### 3.1 问题立轴：实时 × 高分辨率 × 长程记忆，三者同框仍稀缺

摘要 / §1：交互视频生成里，扩散模型越来越像世界模型，但既有路线难 **同时** 做到：

1. **记忆启用的长程时空一致**（分钟级、可回访场景）；
2. **高分辨率真实时**（文称 720p、至约 40 FPS）；
3. **可复现的数据 / 训推栈**（对标 Genie 3 等闭源系统）。

相对 Matrix-Game 2.0：3.0 在 **数据、模型、推理** 三侧系统升级。

### 3.2 四组件协同（§3 总览）

| 组件 | 作用（文内） |
|---|---|
| **Error-aware interactive base** | 双向 DiT + 动作条件；error buffer 收集/注入残差，学自校正（对齐后续蒸馏） |
| **Camera-aware long-horizon memory** | 按相机位姿 / FoV 重叠检索记忆帧；与 past / current 同注意力空间；相对 Plücker；共享误差注入 |
| **Multi-segment few-step distillation** | 双向学生多段自 rollout + **DMD**，对齐流式 few-step 推理 |
| **Real-time acceleration** | DiT **INT8**（注意力投影）、**MG-LightVAE** 剪枝、GPU 近似记忆检索；异步 **8 DiT + 1 VAE** |

骨干：交互基座基于 **Wan2.2-TI2V-5B**；动作模块进前 **15** 个 DiT block（沿用 2.0）。Scale-up：**MoE-28B**（摘要亦写 **2×14B**）；高低噪声分工——高噪声管动作精确、低噪声可吃互联网视频做细节；第一/第三人称高噪声分模型、共享低噪声。

### 3.3 Error-aware 基座（§3.1）

设计原则（文内两点）：

1. **师生同构双向架构**——避免异构 teacher–student 映射失配（引用 Causal Forcing 等理论动机，**不展开**）；
2. **对不完美上下文鲁棒**——训练时也应见自生成历史噪声，而非只见干净 GT。

流程要点：序列 latent 分 past（条件）与 current（加噪预测）；flow-matching 损失只加在 current。键盘离散动作 → **Cross-Attention**；鼠标连续信号 → **Self-Attention**。

误差机制（跟 SVI）：收集 $\delta=\hat{x}_i-x_i$ 入 buffer $E$；注入 $ \tilde{x}_i=x_i+\gamma\delta $。目标示意（式 3，抽取）：在扰动历史与动作条件 $c$ 下匹配速度场。

### 3.4 相机感知长程记忆（§3.2）

拒两条旁路后的选择：

- **拒** MoC 式稀疏长上下文（高噪声段相似度不稳 + 训时开销）；
- **拒** 单独 memory 分支 + 层层注入（收敛慢）。

**采纳**：检索到的 memory latent、近期 past、当前 noised current **同一 DiT self-attention**；可选保留序列首帧作 **sink latent**；相对几何用 **Plücker-style**；memory 与 history 共享误差注入（式 4–6）；时间 RoPE 注入真实帧索引 + **head-wise perturbed RoPE base**（式 7，$\sigma_\theta=0.8$）减轻周期对齐导致的「远距字面复制」。

训练设定（§5.1）：约 **5 memory + 4 past + 10 noisy** latent；记忆增强训集约 **4.8M** clips。

### 3.5 多段蒸馏与实时部署（§3.3–3.4）

- **多段 DMD**：双向学生按真实 few-step 多段 rollout；段 $i$ 的 past 取段 $i-1$ 尾；记忆自在线池按当前视角取；首段无记忆 → I2V。冷启动单段 600 step → 多段 $k\sim U\{1..6\}$ 共 2400 step（§5.1）。
- **加速**：INT8 @ attention projection（LightX2V 算子）；MG-LightVAE 50%/75% 剪枝（文称解码加速约 **×2.6 / ×5.2**）；GPU 采样近似视锥重叠替代 CPU 精确体积交；**8+1** 异步至约 **40 FPS**。

**Table 1**（75% VAE 剪枝设定下，去掉组件后的 FPS）：

| Configuration | FPS | ↓ Drop |
|---|---|---|
| Full | **~40** | – |
| − INT8 quantization | 27.38 | 12.62 |
| − MG-LightVAE | 25.79 | 14.21 |
| − GPU retrieval | 6.60 | 33.40 |

**Table 2**（720×1280、17-frame；PSNR/SSIM 与时间）：

| Model | PSNR↑ | SSIM↑ | Full(s)↓ | Dec.(s)↓ |
|---|---|---|---|---|
| Wan2.2 VAE | 33.79 | 0.99 | 0.99 | 0.76 |
| MG-LightVAE 50% | 31.84 | 0.99 | 0.52 | 0.30 |
| MG-LightVAE 75% | 31.14 | 0.99 | 0.35 | 0.13 |

### 3.6 数据引擎（§4）

三源互补，产出 **Video–Pose–Action–Prompt** 四元组：

1. **Unreal-Gen（UE5）**：>1000 场景；tick 同步 RGB / 位姿 / 动作；NavMesh–RL 探索；角色组合 $|C|>10^8$ 变体。
2. **AAA 四层解耦录制**：GTA V / RDR2 / Palworld / Cyberpunk 2077 / Hogwarts Legacy 等；OBS 分段；由位移推断 WSAD。
3. **真实世界**：DL3DV-10K、RealEstate10K、OmniWorld-CityWalk、SpatialVid-HD；统一用 **ViPE** 重标姿态。

标注：InternVL3.5-8B 四层 caption + 感知质量分；轨迹/速度过滤 + 质量过滤，文称去掉约 **20%** 原始数据。

### 3.7 实验读法（§5，辅）

- **场景回访协议**（Fig.9）：后半动作反转前半，迫使回到已见区域——成功重建不能只靠短时连续，需长程记忆。质化显示结构 / 外观细节可恢复。
- 蒸馏模型（Fig.11）继承记忆；28B 第三人称长视频质化（Fig.10）。
- **注意**：公开表以 **吞吐消融与 VAE 重建** 为主；分钟级一致性多以定性图支撑——跟读时勿把「~40 FPS」直接外推成统一榜上的一致分数。

---

## 四、主文 B：Cosmos World Foundation Model Platform（2501.03575）

### 4.1 平台立轴：先通用 WFM，再小数据后训练到 Physical AI

摘要 / §1：Physical AI 需要「自身的数字孪生（策略）」与「世界的数字孪生（世界模型）」。Cosmos 把 **World Foundation Model** 定位为 **可后训练的通用世界模型**，平台覆盖：

1. **视频策展管线**；
2. **预训练 WFM**（扩散族 + 自回归族）；
3. **后训练样例**（相机控制 / 机器人 manipulation / 自动驾驶）；
4. **视频 tokenizer**（连续 / 离散、因果）；
5. **Guardrail**（pre-Guard / post-Guard）。

开放：文称 **开源 + 开权重**（NVIDIA Open Model License），入口 **NVIDIA Cosmos-Predict1**。

WFM 接口（§2，Fig.3）：$ \hat{x}_{t+1}=\mathcal{W}(x_{0:t},c_t) $，$x$ 为 RGB 视频，$c$ 可为动作、随机扰动、文本描述等。

### 4.2 视频策展（§3）

- 原料约 **20M 小时** 原始视频（720p–4k）；管线抽出约 **100M** clips（**2–60 s**）；每 256 帧用 VLM 出一条 caption。
- 五步：**split**（镜头检测 + GPU H.264 转码）→ **filtering**（运动 / 画质 / 叠字 / 类型）→ **annotation** → **semantic dedup** → **sharding**（分辨率与宽高比）。
- 编排：Ray；目标是吞吐匹配不同理解模型速率。

本卡只立「策展接口」，不展开每个过滤器阈值。

### 4.3 Tokenizer（§4，接口）

- **连续**（向量）服务扩散 WFM；**离散**（整数）服务 AR WFM。
- **因果**：当前帧不依赖未来——便于图-视频联合训，并与 Physical AI 因果世界对齐。
- 文内家族名示例：`Cosmos-Tokenize1-CV8×8×8-720p`、`Cosmos-Tokenize1-DV8×16×16-720p`；离散侧 FSQ 词表大小文给 **64,000**（$8^3\times5^3$）。

### 4.4 预训练地图（§5 / Table 10）

文称全部 WFM 在约 **10,000×H100、约三个月** 集群上训练（§5 开篇）。

| Type | 扩散族 | 自回归族 |
|---|---|---|
| 基座 → 派生 | 7B / 14B **Text2World** → **Video2World** | 4B / 12B next-token → 5B / 13B **Video2World**（+T5 cross-attn） |
| Tokenizer | CV8×8×8-720p | DV8×16×16-720p |
| 增强器 | Prompt upsampler **12B**（基于 Mistral-NeMo-12B-Instruct） | Diffusion decoder **7B**（DV→CV） |

- **扩散**：EDM 式去噪分数匹配 + 不确定性加权；DiT 骨干；两阶段 Text2World → Video2World。
- **自回归**：Llama3-style GPT **从零**训视频 next-token；3D RoPE + YaRN（时间轴）+ 3D APE；QK-Norm。
- **评测字段（辅）**：§5.3 给 3D consistency 与 physics alignment；**Table 20** 示物理对齐在 1 vs 9 帧条件下 PSNR/SSIM/DreamSim/Avg.IoU——文内观察：更多条件帧通常更好；扩散在 9 帧条件像素级更好；**更大模型不一定更贴物理**（画质更好但物理仍挣扎）。本卡转述表意，不外推「已解决物理」。

### 4.5 后训练样例（§6）——平台接口，非 VLA 通史

| 样例 | 做法（压缩） | 本卡边界 |
|---|---|---|
| **相机控制** | 扩散 WFM 后训练接相机位姿 → 可导航虚拟世界 | 录接口；≠ Matrix 键鼠实时栈 |
| **机器人 manipulation** | video–action / 指令条件预测未来 | **≠ [[视觉语言动作谱系]]** 闭环 VLA 谱系 |
| **自动驾驶** | 多视角 Text/Video2World 样例 | 仅样例 |

§2.1 列出的策略评估 / MPC / RL 等 **本文无实证**——跟读时保持「平台能力声明 ≠ 已验证部署」。

### 4.6 Guardrail（§7，一句）

pre-Guard 拦有害输入、post-Guard 拦有害输出——本卡不展开分类器配方。

---

## 五、Genie 3 对照（不升主）

来源：DeepMind 博文 *Genie 3: A new frontier for world models*（**2025-08-05**，Parker-Holder & Fruchter）。

| 博文宣称（压缩） | 与本卡关系 |
|---|---|
| 文本提示 → 可导航动态世界；**24 FPS**、**720p**、一致性维持 **数分钟** | Matrix 文内对标「实时+分钟级」；本卡 **不** 当可核 TR |
| 相对 Genie 2：首次 **实时交互**，并提升一致性与真实感 | 谱系位 |
| Promptable world events；与 SIMA agent 联调 | 产品能力索引 |
| 限制：动作空间有限、多 agent、真实地点精度、时长「数分钟非数小时」等 | 跟读时勿夸大 |

**议程裁定（2026-09-22）**：无正式 PDF TR → **本波不升主**；仅对照一句。

---

## 六、跟读清单与禁止项

**优先跟：**

1. Matrix：**error buffer + 相机记忆同注意力 + 多段 DMD** 如何共同服务「流式分钟级」；Table 1/2 吞吐与 VAE 代价。
2. Cosmos：**策展 → 因果 tokenizer → 扩散/AR 双轨预训练 → 小数据后训练** 的平台分层；Table 10 模型地图。
3. 划界自检：文中是否误入 JEPA mask 损失、Sora 缺口叙事、Forcing 族公式堆叠、或 VLA 成功率表。

**禁止：**

- 把 Cosmos 写成「又一个文生视频模型评测」或把 Matrix 写成「又一个离线 DiT 视频」。
- 把 Genie 3 博文数字当作已 peer-review 的可复现配方。
- 建议把 **>20MB** 的两篇 PDF **入库二进制**（本卡明确 **正式外链**）。
- 编造未在抽取中出现的 FLOPs 明细、未公开的 Genie 训练预算、或「已验证 MPC/RL 收益」。

---

## 七、来源与核验

| 项 | 值 |
|---|---|
| Matrix PDF | https://arxiv.org/pdf/2604.08995 （v2；20p；**22.6MB**） |
| Cosmos PDF | https://arxiv.org/pdf/2501.03575 （v3；75p；**41.5MB**） |
| Genie 3 博文 | https://deepmind.google/blog/genie-3-a-new-frontier-for-world-models/ |
| 抽取 | |
| 核验时刻 | **2026-09-22 CST**（ / 博文 HTML→txt） |
| 二进制策略 | **两篇主 PDF >20MB → 建议正式外链**； |
