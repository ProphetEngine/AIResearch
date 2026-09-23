---
title: "权重·激活 PTQ 收口：SpinQuant（旋转）+ ARCQuant（NVFP4）（≠ KV量化 / ≠ ZeroQAT）"
topic: SpinQuant与ARCQuant量化
date: 2026-09-22
lines: [架构思想, 部署接口]
status: archived
sources:
 - https://arxiv.org/abs/2405.16406 # ≈10.21MB / 24p（主 A）
 - https://arxiv.org/abs/2601.07475 # ≈5.23MB / 15p（主 B）
arxiv: ["2405.16406", "2601.07475"]
related:
 - "KV缓存量化与压缩"
 - "ZeroQAT量化感知训练"
 - "端侧小模型"
 - "推理引擎生态"
note_bitnet: "BitNet v2（arXiv:2504.18415）属从零低比特训练，与本轴相邻但不升主；维护期补链"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 权重·激活 PTQ 收口：SpinQuant（旋转）+ ARCQuant（NVFP4）（≠ KV 量化 / ≠ ZeroQAT）

> **定位**：**P1** 收口——仓库量化三角此前已有 **[[KV缓存量化与压缩]]（KV cache）** 与 **[[ZeroQAT量化感知训练]]（训练期 ZO-QAT）**；本卡只补 **部署侧权重·激活 PTQ** 的横切缺口：
> - **SpinQuant**（*LLM Quantization with Learned Rotations*，ICLR 2025）：在 FP 网络输出不变的旋转参数化上，用 **Cayley SGD** 学 **Stiefel 流形**上的旋转，压激活/权重离群，再接 GPTQ；含可吸收的 $R_1,R_2$ 与在线 Hadamard $R_3,R_4$。
> - **ARCQuant**（*Boosting NVFP4 Quantization with Augmented Residual Channels*，arXiv **2601.07475v2**）：面向 **Blackwell NVFP4（g=16, E2M1+E4M3）**，用 **增广残差通道** 做双阶段补偿，保持 **统一 NVFP4 精度路径**，映射到标准 GEMM。
> **攻坚线**：**架构思想 / 部署接口（主）** + **文内 W4A4(KV) / NVFP4 精度—吞吐字段（辅）**。
> **硬划界（开篇钉死，禁止滑向相邻笔记）**：
> - **≠ [[KV缓存量化与压缩]]**：不写 KIVI / KVQuant 的 **K per-channel · V per-token**、残差窗、RoPE 前后误差轴；SpinQuant 表中的 **W-A-KV** 比特列只作「联合配置字段」，**禁止**把本卡写成 KV 量化通史。
> - **≠ [[ZeroQAT量化感知训练]]**：不写 ZeroQAT 的 **零阶前向梯度 / STE 绕开 / 端侧 QAT 内存**；本卡是 **冻结权重的 PTQ**（旋转学习或残差增广），不是训练期 QAT。
> - **≠ [[端侧小模型]]**：不写 MobileLLM / Phi-4 / 端侧 SLM 产品谱系；只取「部署侧低比特压力」接口一句。
> - **≠ B7**：不写 vLLM / SGLang / TRT-LLM 引擎选型、PagedAttention、投机解码族；ARCQuant 文内 vLLM 吞吐表仅作 **部署字段索引**。
> - **≠ BitNet v2**：原生低比特 **从零训练** → **本波不升主**（波 13 议程 §四；维护期补链）。
> **禁止编造**：公式编号、表数字、倍率一律锚定官方 PDF（2026-09-22 CST）。议程称 ARCQuant 为 ACL 2026；**官方 PDF 首页未印会议标识** → 本笔记以 **arXiv:2601.07475v2 \[cs.LG\] 4 Jul 2026** 为准，不虚构 proceedings 页码。
> **二进制**：两篇均 **≪20MB**（见 §一）→ **官方 HTTPS 外链**；SpinQuant ≈10.21MB，主管允许可入。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / 体积 / 页数 | 角色 |
|---|---|---|---|
| **主文 A** | Liu, Zhao, Fedorov, Soran, Choudhary, Krishnamoorthi, Chandra, Tian, Blankevoort（Meta），*SpinQuant: LLM Quantization with Learned Rotations* | arXiv:**2405.16406v4** \[cs.LG\] **20 Feb 2025**；ICLR 2025；`https://arxiv.org/abs/2405.16406`（**10,207,972** B ≈ **10.21MB**；**24** 页 letter；CreationDate **2025-02-21 CST**） | **可学习旋转 PTQ**：Stiefel + Cayley；`no_had` / `had` 两档 |
| **主文 B** | Meng, Luo, Zhao, Liu, Zhang*, Ma（天津大学），*ARCQuant: Boosting NVFP4 Quantization with Augmented Residual Channels for LLMs* | arXiv:**2601.07475v2** \[cs.LG\] **4 Jul 2026**；`https://arxiv.org/abs/2601.07475`（**5,234,557** B ≈ **5.23MB**；**15** 页 A4） | **NVFP4 增广残差通道**：统一精度 GEMM + 双阶段误差界 |

| 文件 | 体积 | 页数 | 备注 |
|---|---|---|---|
| `2405.16406-spinquant.pdf` | **10.21MB**（10,207,972 B） | 24 | **官方 HTTPS 外链**（≪20MB；主管允许可入） |
| `2601.07475-arcquant.pdf` | **5.23MB**（5,234,557 B） | 15 | **官方 HTTPS 外链**（≪20MB） |

**代码锚（PDF 声明）：**
- SpinQuant：`github.com/facebookresearch/SpinQuant`
- ARCQuant：`https://github.com/actypedef/ARCQuant`

**一句话抓手：**
- **SpinQuant**：随机旋转能去离群，但 **零样本均值可差到 13 点** → 在 **不改 FP 输出** 的前提下 **学旋转**；W4A8 常只需可吸收 $R_1,R_2$，极端 **W4A4KV4** 再加在线 Hadamard。
- **ARCQuant**：细粒度 **NVFP4** 下 **全局旋转会破坏 block 隔离**、混合精度又撞 Tensor Core 统一路径 → 把离群通道的 **残差以同精度通道拼进 reduction 维**，用标准 GEMM 换回近 W4A8 精度。

---

## 二、议题边界：W·A-PTQ ≠ KV / QAT / SLM / 引擎手册

### 2.1 五向对照（跟读）

| 轴 | 动什么 | 时机 | 仓库位置 | 本篇是否主写 |
|---|---|---|---|---|
| **[[KV缓存量化与压缩]] KV cache 量化** | 已生成的 K/V 张量按非对称轴压比特 | **解码缓存** | [[KV缓存量化与压缩]] | **否**（表字段可出现 KV 列，不展开公式） |
| **[[ZeroQAT量化感知训练]] ZeroQAT** | 前向 ZO 估梯度，联训量化参数 | **训练 / 微调** | [[ZeroQAT量化感知训练]] | **否** |
| **[[端侧小模型]] on-device SLM** | 深薄架构 / 合成数据 / 端侧产品 | 模型族 | [[端侧小模型]] | **否** |
| **B7 推理引擎** | vLLM / SGLang / TRT-LLM 选型 | 引擎生态 | B7 | **否**（名作吞吐对照） |
| **BitNet v2** | 原生低比特 **从零训练** | 预训练范式 | 维护期补链 | **不升主** |
| **SpinQuant** | **旋转参数化 + Cayley 学旋转** 后 PTQ | **部署前标定** | **本篇 A** | **是** |
| **ARCQuant** | **NVFP4 残差通道增广** + 融合量化核 | **部署前标定 + 在线残差** | **本篇 B** | **是** |

跟读直觉：[[KV缓存量化与压缩]] 问「**缓存里的 K/V 怎么压**」；[[ZeroQAT量化感知训练]] 问「**训练时怎么感知量化**」；SpinQuant 问「**在 FP 等价约束下怎么转一下再 PTQ**」；ARCQuant 问「**硬件细粒度 NVFP4 下怎么补残差还不破坏统一 GEMM**」。

### 2.2 与「权重量化史」的关系（防写成 AWQ/GPTQ 百科）

[[KV缓存量化与压缩]] 正文 **刻意不写** AWQ/GPTQ/SmoothQuant 通史。本卡 **只在两文实验协议出现处**点名：

| 出现处 | 用法（本卡允许） | 禁止 |
|---|---|---|
| SpinQuant §4.1 | 旋转学完后对旋转权重跑 **GPTQ**（128×2048 WikiText-2） | 复述 GPTQ Hessian 算法全文 |
| SpinQuant Table 1 | SmoothQuant / LLM-QAT / AWQ / OmniQuant / QuIP# 作 **对照行** | 升为 AWQ/OmniQuant 主轴 |
| ARCQuant §2 / Table 2 | SmoothQuant / QuaRot 适配到 NVFP4 作 **负例/对照**；Atom / FlatQuant / MicroMix 作 W4A4 基线 | 写成混合精度百科 |

---

## 三、SpinQuant：可学习旋转的 W·A(·KV) PTQ

### 3.1 动机：离群 + 随机旋转方差

据 §1–§2：

1. **离群拉大量化动态范围**（式 1 的对称/非对称量化）；通道维硬件常不支持 → token/tensor 量化被少数大通道毁掉（Fig 2）。
2. **旋转**把大/小值统计上「搅匀」：Fig 3 显示旋转后激活 **kurtosis ≈ 3**（近高斯），激活与权重量化误差同时下降。
3. **但随机旋转方差巨大**：LLaMA-2 7B、W4A4、网络级参数化、100 次随机试验——最好与最差零样本均值差 **13 点**；随机 Hadamard 仍可差 **约 6 点**（Fig 4 / §2.2）。
4. → **SpinQuant**：固定预训练权重 $W$，在 Stiefel 流形上优化旋转，直接最小化 **量化网络任务损失**。

### 3.2 旋转参数化（§3.1，跟读）

| 符号 | 位置 | 吸收？ | 作用 |
|---|---|---|---|
| $R_1$ | 残差流旋转（embedding 后）；块内用 $R_1^{-1}$ 抵消 | **可 merge 进相邻权重** | 读残差的 Q/K/V/Up/Gate 输入去离群 |
| $R_2$ | Attention 内：$W_v$ 侧 ×$R_2$，out-proj 输入 ×$R_2^\top$（**按 head**，形状 $D_{\mathrm{head}}\times D_{\mathrm{head}}$） | **可 merge** | Value cache + out-proj 输入 |
| $R_3$ | RoPE 后、KV 路径上的 **在线 Hadamard** | **不可吸收** | 低比特 **KV** 时抑制 cache 离群 |
| $R_4$ | FFN 内、down-proj 前的 **在线 Hadamard** | **不可吸收** | 低比特 **激活** 时抑制 MLP 内离群 |

**两档部署：**

| 档 | 旋转集合 | 推理改动 | 适用（文内口径） |
|---|---|---|---|
| **SpinQuant$_{\mathrm{no\,had}}$** | 学得的 $R_1,R_2$ | **只换旋转后量化权重**；前向无新算子 | **W4A8 / W4A8KV8** 等「激活不极端」 |
| **SpinQuant$_{\mathrm{had}}$** | $R_1,R_2$ + 在线 $R_3,R_4$ | 需 **fast Hadamard**；文称相对无 Hadamard 约 **~8%** 网络时延开销（§4.5 / 主文复述） | **W4A4 / W4A4KV4** |

脚注（原文）：pre-norm（如 LLaMA）把 RMSNorm 的 scale $\alpha$ **吸收进后接权重**，即可构造旋转不变网络（Ashkboos et al. / SliceGPT 脉络）。

### 3.3 Cayley 优化（§3.2）

目标（式 2）：

$$
\arg\min_{R\in\mathcal{M}} \mathcal{L}_Q(R_1,R_2 \mid W,X)
$$

- $\mathcal{M}$：Stiefel（正交矩阵集）；$R_3,R_4$ **固定为 Hadamard**（在线便宜）。
- 更新（式 3–4）：对斜对称 $Y$ 做 Cayley 变换 $\Delta_R(Y)=(I-\frac{\alpha}{2}Y)^{-1}(I+\frac{\alpha}{2}Y)$，保证 $R'$ 仍正交；可用定点迭代避免显式求逆。
- **只训旋转**：$\{R_1,R_2\}$ 约占权重规模 **~0.26%**；FP 网络输出不变，只改「量化友好性」。
- **标定**：WikiText-2 **800** 样本、**100** iter；LR 1.5→0 线性衰减；$R$ 初值常用随机 Hadamard。文称 LLaMA-3 1B/3B/8B 约 **13/18/30 min**，LLaMA-2 7B/13B 约 **25/30 min**，70B 约 **3.5 h**，Mistral-7B 约 **16 min**（§4.1）。

**与 GPTQ 的配合（§4.3.2 / Table 3）：** 主实验在 **仅激活量化** 的网络上 Cayley，再对旋转权重跑 GPTQ——让旋转主扛激活误差、GPTQ 主扛权重量化。LLaMA-2 7B 上，相对「在 4-4-KV 上直接 Cayley」，该协议把 4-4-16 零样本均值从 **61.0±1.0** 提到 **64.1±0.4**（Wiki PPL 6.7→5.9）。

### 3.4 主结果速览（Table 1，选读）

评测：8 项零样本常识推理均值 + WikiText-2 PPL；模型含 LLaMA-2 7/13/70B、LLaMA-3.2 1B/3B、LLaMA-3 8B、Mistral-7B。

**LLaMA-2 7B（摘自 Table 1；完整表见 PDF）：**

| (W-A-KV) | FloatingPoint | SmoothQuant | LLM-QAT | SpinQuant$_{\mathrm{no\,had}}$ | SpinQuant$_{\mathrm{had}}$ |
|---|---:|---:|---:|---:|---:|
| 16-16-16 | 66.9 / 5.5 | — | — | — | — |
| 4-8-8 | — | 58.8 / 7.5 | 64.6 / 11.4 | **65.8 / 5.8** | **65.8 / 5.7** |
| 4-4-4 | — | 39.0 / 7e2 | 44.9 / 14.9 | 56.0 / 9.2 | **64.0 / 5.9** |

文内主张（摘要 / §4.2，**记作者口径**）：
- LLaMA-2 7B、**W4A4KV4**：SpinQuant$_{\mathrm{had}}$ 零样本 **64.0**，距 FP **2.9** 点；相对同设定 LLM-QAT 差距缩小约 **19.1** 点，相对 SmoothQuant 约 **25.0** 点（摘要数字）。
- W4A8 档：SpinQuant$_{\mathrm{no\,had}}$ 已常够用；在线 Hadamard **边际收益小**。
- 相对并发 **QuaRot**（随机旋转）：LLaMA-3 难量化模型上，文称相对 QuaRot 把距 FP 的 gap **最多相对缩小 45.1%**（摘要）；Table 5 上 LLaMA-3 8B / 70B 的 GPTQ 与 RTN 对照显示 SpinQuant$_{\mathrm{had}}$ 稳定优于 QuaRot，且 **每块在线 Hadamard 更少**（2 vs QuaRot 的 4）。

**学旋转 vs 随机 Hadamard（Table 2 摘）：** Mistral-7B、SpinQuant$_{\mathrm{had}}$ 相对随机 Hadamard $R_{\{1,2,3,4\}}$，4-4-4 上 **↑16.2** 点（52.4→68.6）。

### 3.5 部署接口清单（SpinQuant）

`
标定：冻结 W → Cayley 学 R1,R2（可选目标：仅激活量化网络）
 → merge R1,R2 进权重 → （可选）GPTQ
推理：
 · no_had：换权重即可，无新 kernel
 · had：额外 fast Hadamard（R3/R4）；文称 ~8% 时延
勿与：KIVI 残差窗、ZeroQAT ZO 梯度、BitNet 从零训练 混叙事
`

---

## 四、ARCQuant：NVFP4 上的增广残差通道

### 4.1 问题：细粒度格式下「旋转 / 混精」双失灵

据 Abstract / §1 / §3.1：

| 硬件事实（文内） | 含义 |
|---|---|
| **NVFP4**：组大小 **g=16**，元素 **E2M1**，组 scale **E4M3**，另有 per-tensor 二级 scale | 细粒度 **block 隔离**：离群不该污染整张量 |
| **MXFP4**：g=32，E2M1 + E8M0 | 与 NVFP4 粒度不同 |
| Blackwell Tensor Core | 偏好 **统一精度 / 对齐 group** 的 MMA；异质 group（如 INT8/FP16 旁路）难吃满硬件 |

**为何不能直接搬旧 PTQ：**

1. **全局旋转 / Hadamard**：把离群幅值 **线性扩散到所有维** → 虽降全局峰值，但抬高原本低幅 block 的局部动态范围 → **破坏 NVFP4 隔离**（Fig 2–3；Table 2 上 Llama 3.1-8B：NVFP4+QuaRot 零样本均值 **70.18**，低于 NVFP4+RTN **70.45**）。
2. **混合精度（Atom 等）**：高精旁路通道与 NVFP4 g=16 vs MXFP8 g=32 **粒度冲突** → 难走统一 Tensor Core 路径。
3. → **ARCQuant**：不改数值分布、不混精度；对离群通道做 **同精度残差通道增广**，把补偿吃进 GEMM 的 **扩展 reduction 维**。

### 4.2 方法（§3.2–3.3）

**自适应离群识别（标定离线）：**

1. 按通道绝对最大值重排（Atom 式排序）。
2. 层内最大幅值 $M$；阈值 $\tau = 2^{-3} M$（对标 E5M2 与 E2M1 的 **3-bit 指数差**）。
3. 仅对超过阈值的 top-$S$ 通道做补偿；$S$ 按层定（Fig 7）。

**在线激活量化：**

1. 重排 + 主量化 $Q_X=\mathrm{round}(X/s_X)$。
2. 离群残差 $R_o = X_o - s_{X_o}\cdot Q_{X_o}$，再量化为 $Q_{R_o}$。
3. 沿 K 维拼接：$Q_{X_{\mathrm{aug}}}=[Q_X \mid Q_{R_o}]$，scale 同步拼接。

**离线权重量化：** 权重同序重排；对离群权重 **复制** 已量化块 $Q_{W_o}$ 拼到右侧（不另算权重残差），使 GEMM 贡献 $R_o Q(W_o)^\top$。

**统一 GEMM（式 2）：**

$$
Y \approx Q(X)Q(W)^\top + Q(R_o)Q(W_o)^\top
= s_{X_{\mathrm{aug}}}\cdot Q_{X_{\mathrm{aug}}}\,(s_{W_{\mathrm{aug}}}\cdot Q_{W_{\mathrm{aug}}})^\top
$$

形状：$(N,K_{\mathrm{in}},M)\rightarrow(N,K_{\mathrm{in}}+S,M)$。融合核：Channel Reorder + RMSNorm + 主量化 + 残差量化 → 输出仍是 **严格 NVFP4**，后续可直接吃 **CUTLASS** 等标准 GEMM（Fig 4–5）。

### 4.3 误差界（§3.4，口径摘要）

文设 NVFP4 $\epsilon_4=2^{-2}$、MXFP8 $\epsilon_8=2^{-4}$，故 $\epsilon_4^2=\epsilon_8$。双阶段对离群通道量化后，最坏误差界 $B_{\mathrm{arc}}=(\alpha_1\alpha_2)M\epsilon_8$；因 E4M3 scale，$\sup\alpha_1\alpha_2\approx 1.266 < 2 \approx \sup\alpha_{\mathrm{mx}}$（MXFP8 E8M0）→ **宣称**与标准单阶段 MXFP8 最坏界可竞争。
**记法：** 此为作者理论论证，**非本仓库硬件实测裁决**。

### 4.4 主结果与效率（Table 1–4 / Fig 6–8）

**相对其他 W4A4（Table 1 摘，零样本均值 / Wiki PPL / MMLU-5shot）：**

| 模型 | FP16 | Atom | FlatQuant | ARCQuant |
|---|---:|---:|---:|---:|
| Llama 3.1-8B | 72.56 / 6.24 / 65.15 | 67.74 / 7.52 / 59.27 | 70.51 / 6.95 / 61.33 | **70.90 / 6.87 / 62.61** |
| Qwen2.5-7B | 70.97 / 6.85 / 74.16 | 67.57 / 8.96 / 68.17 | 69.17 / 7.88 / 71.95 | **70.28 / 7.28 / 72.84** |
| Qwen2.5-32B | 74.82 / 5.02 / 83.26 | 73.60 / 5.83 / 79.54 | 74.02 / 5.74 / 81.52 | **74.80 / 5.38 / 82.61** |

文称在 8B/7B 上 ARCQuant 可在 PPL·MMLU 上 **超过 W4A8+RTN 参考**；32B 上接近 FP16。

**同格式 NVFP4 策略（Table 2）：** ARCQuant 全面优于 NVFP4+RTN / Smooth / QuaRot；QuaRot 在 Llama 3.1-8B 上相对 RTN **回退**——支撑「旋转伤隔离」动机。

**代码生成（Table 3，Qwen2.5-Coder-7B-Instruct，pass@1）：** ARCQuant HumanEval **86.0**（FP16 84.1；Atom 80.5）。

**吞吐（摘要 + §4.3；Blackwell 消费/专业卡）：**
- 摘要：相对 FP16 **最高约 3×** 加速（prefill 叙事；Fig 6 细项：Qwen2.5-7B 在 PRO 6000 上 **2.0×–2.5×**，Llama 3.1-8B 在 RTX 5090 上达 **3.5×**；内存降 **1.5×–2.8×**）。
- 相对未补偿 NVFP4：时延仅增 **3%–9%**；Qwen2.5-7B prefill breakdown 总开销约 **4.9%**（Fig 8b）。
- **vLLM** 集成、Qwen2.5-7B、RTX 5090、bs=8、gen=128（Table 4）：seq 1024 时 total **21077** tok/s、decode **2342**（相对 FP16 decode **1.96×**）；seq 2048 时 decode **1249**（相对 FP16 **2.08×**）。→ **仅作文内部署字段**；引擎通史回 **B7**。

### 4.5 局限（作者自述，§Limitations）

1. 权重侧当前主用 **RTN**；兼容 GPTQ/AWQ 属未来工作。
2. 吞吐收益绑定 **Blackwell 原生 NVFP4**；无该加速的旧架构上偏仿真。
3. 通道序与 $S$ **离线标定**，假设推理期离群结构相对稳定。

### 4.6 部署接口清单（ARCQuant）

`
标定：定通道重排 + 层wise S（阈值 τ=2^{-3}M）
权重：离线重排 + 量化 + 复制离群列 → QW_aug
推理：融合核（Reorder/RMSNorm/主量化/残差量化）→ 标准 NVFP4 GEMM(Kin+S)
勿与：SpinQuant 在线 Hadamard、KIVI 残差窗、ZeroQAT 混为一谈
对照口诀：SpinQuant「转分布」；ARCQuant「拼残差通道、保 block 隔离」
`

---

## 五、两文对照：同一 PTQ 缺口上的正交切片

| 维度 | SpinQuant | ARCQuant |
|---|---|---|
| **核心手段** | 学得正交旋转（+可选在线 Hadamard） | 同精度残差通道增广 |
| **对离群** | 搅匀分布 → kurtosis↓ | **隔离**离群并二次量化残差 |
| **与细粒度 NVFP4** | 文主战场是通用 INT/低比特 W·A·KV；**非** NVFP4 专用 | **专为** NVFP4 / Blackwell 统一路径 |
| **对旋转的态度** | 旋转是主药 | 旋转在 NVFP4 上常是 **负例**（Table 2） |
| **推理改动** | `no_had` 几乎零架构改；`had` ~8% | 融合量化核 + $K{+}S$ GEMM；相对纯 NVFP4 +3–9% |
| **权重 PTQ** | 常接 **GPTQ** | 主文 **RTN**（可扩展） |
| **代码** | facebookresearch/SpinQuant | actypedef/ARCQuant |

**收口结论（给维护期）：** 量化三角闭合为 **KV（[[KV缓存量化与压缩]]）· QAT（[[ZeroQAT量化感知训练]]）· W·A-PTQ（本卡）**。后续若补 **BitNet v2**，应单开「原生低比特训练」轴，**不要**并回本卡升主。

---

## 六、禁止清单与交叉回链

| 禁止 | 应回链 |
|---|---|
| 重写 KIVI / KVQuant 非对称公式与残差窗 | 推理与基础设施/KvQuant/KV缓存量化与压缩.md |
| 重写 ZeroQAT ZO 梯度 / 端侧 QAT 内存表 | 推理与基础设施/KvQuant/ZeroQAT量化感知训练.md |
| 重写 MobileLLM / Phi-4 / Gemma 小尺寸通史 | 推理与基础设施/端侧小模型.md / [[Gemma4技术报告深读]] |
| 写成 vLLM/SGLang/TRT-LLM 选型手册 | 推理与基础设施/InfraServing/推理引擎生态.md |
| 把 BitNet v2 升为本卡主文 | 波 13 议程 §四；维护期补链 |
| 无 PDF 依据合并跨文倍率或虚构 ACL 页码 | 只引本地抽取与 arXiv 版次 |

---

## 七、跟读检查清单

- [ ] 能口述 SpinQuant 的 $R_1$–$R_4$ 何者可吸收、何时必须 `had`
- [ ] 能解释「随机旋转 13 点方差 → Cayley on Stiefel」
- [ ] 能说明 ARCQuant 为何批评 Hadamard on NVFP4，以及 $Q_{X_{\mathrm{aug}}}=[Q_X|Q_{R_o}]$ 如何进 GEMM
- [ ] 能指出本卡与 [[KV缓存量化与压缩]] / [[ZeroQAT量化感知训练]] 的一句边界，且不展开对方公式
- [ ] 引用数字时能指回 Table / Fig 编号（禁止口算外推）

---

**成稿路径：** `/workspace/AIResearch-drafts/推理与基础设施/KvQuant/SpinQuant与ARCQuant量化.md
**PDF：** `https://arxiv.org/abs/2405.16406`（10.21MB / 24p，外链引用）· `https://arxiv.org/abs/2601.07475`（5.23MB / 15p，外链引用）
**状态：** archived · date 2026-09-22 · 检索截止 2026-09-22 CST
