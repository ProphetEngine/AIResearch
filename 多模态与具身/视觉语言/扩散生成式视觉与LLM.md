---
title: 扩散 / 生成式视觉与 LLM 交叉
topic: 扩散生成式视觉与LLM
date: 2026-09-22
lines: [架构思想, 数学原理]
status: archived
sources:
 - `https://arxiv.org/pdf/2112.10752`；
 - `https://arxiv.org/pdf/2212.09748`；
boundary: 与 [[多模态架构脉络]]（理解/对话多模态）划界——本卡补生成线（潜扩散 / DiT / 文本条件合成）；不重写 CLIP→Flamingo→LLaVA 理解史线
archived: 2026-09-22
---

# B-10：扩散 / 生成式视觉与 LLM 交叉

> 攻坚线：**架构思想（主）** + **数学原理（辅，扩散过程）**
> 入口：Rombach et al., *High-Resolution Image Synthesis with Latent Diffusion Models*（LDM，[arXiv:2112.10752](https://arxiv.org/abs/2112.10752)）；Peebles & Xie, *Scalable Diffusion Models with Transformers*（DiT，[arXiv:2212.09748](https://arxiv.org/abs/2212.09748)）。
> **与 [[多模态架构脉络]] 划界：** [[多模态架构脉络]] 走「对齐 → 条件语言生成 → 视觉指令 → 原生多模态主张」的**理解/对话**线；本卡走「像素/潜空间去噪 → 条件图像合成 → Transformer 骨干规模化 → 与 LLM 文本条件接口」的**生成**线。数字与断言只取已读 PDF / 议程标注，不编造。
> **视频旗舰正式报告：** 议程标明「若无稳定公开 PDF → **待核实**」——本笔记不引用二手概括代替 Sora 等正式技术报告。

**官方 PDF：**

- `https://arxiv.org/pdf/2112.10752`；
- `https://arxiv.org/pdf/2212.09748`；

---

## 一、动机：为何生成线必须另立

产品与研究里「多模态」常被一张图文截图糊成同一议题。跟读时至少拆成两条互不替代的能力：

| 能力轴 | 代表入口（已入库 / 本卡） | 默认输出 | 骨干直觉 |
|--------|---------------------------|----------|----------|
| **理解 / 对话** | [[多模态架构脉络]]：CLIP → Flamingo → LLaVA 等 | 文本（答案、caption、对话） | 视觉编码 →（对齐或桥接）→ **自回归 LM** |
| **生成 / 合成** | 本卡：LDM → DiT（及后续文生图产品） | 图像（像素或经解码器） | **去噪网络**（U-Net 或 Transformer）在噪声链上迭代 |

若不划界，会出现三类常见混淆：

1. **把 Stable Diffusion / DiT 并进 VLM 笔记**——二者条件接口都可吃文本，但训练目标、采样形态与评测（FID / IS vs VQA / 对话）完全不同。
2. **把「能根据文本出图」当成「能看图对话」**——前者是 $p(\text{image}\mid\text{text})$ 的生成模型；后者是 $p(\text{text}\mid\text{image}, \text{instruction})$。
3. **用参数量或「是否 Transformer」一刀切优劣**——DiT 正文明确：对图像生成模型，**参数量常是差代理**；应用 **Gflops** 与分辨率/token 数一起看（DiT §2 Architecture complexity）。

LDM 摘要给出的工程动机更直白：像素空间强扩散模型常需**数百 GPU 日**训练，推理因逐步评估昂贵（例：文中引 ADM 系约 150–1000 V100 日训练量级；50k 样本在单 A100 上约需约 5 天）。要在有限算力下保留质量与可条件控制，需把扩散挪到**感知上等价、维度更低**的潜空间，并用 **cross-attention** 接入文本等条件。

**本卡跟读主线：** 两阶段（感知压缩 AE + 潜空间扩散）→ U-Net LDM 的文本条件机制 → 用 ViT 式 Transformer 替换 U-Net（DiT）并证明 **Gflops ↔ FID** 规模化 → 与 LLM 的交叉落在「条件编码器 / 引导 / 混合流水线」，而非「同一条理解对话骨干」。

---

## 二、LDM：潜扩散——把算力从「不可见细节」挪开

### 2.1 架构思想：感知压缩 vs 语义压缩

LDM（§1，Fig. 2）把似然型模型在图像上的学习粗分为两阶段：

1. **感知压缩（perceptual compression）：** 去掉高频、对人眼几乎不可见的细节；此阶段几乎不学语义变化。
2. **语义压缩（semantic compression）：** 真正学习数据的概念与构图。

像素空间 DM 虽可用重加权目标（Ho et al.）弱化对「语义无意义」步的拟合，但**训练与推理仍要在全部像素上做反复函数求值**。LDM 的核心架构决策是：

> **显式拆开**「一次训好的通用自编码器」与「在潜空间上训的扩散先验」——AE 只做温和压缩（保留细节），DM 专攻语义生成。

相对此前依赖**极强空间压缩**以便自回归 Transformer 建模离散码本的路线（文中对比 VQGAN / DALL-E 式 $f=8,16$ 等），LDM 强调：DM 的 U-Net 对空间数据有好的归纳偏置，**不需要**那么激进的下采样；因此可以选更利于重建保真度的 $f$（Fig. 1：$f=4$ 重建相对 $f=8/16$ 的 PSNR / R-FID 更优）。

### 2.2 第一阶段：感知图像压缩（§3.1）

- 输入 $x \in \mathbb{R}^{H\times W\times 3}$，编码器 $\mathcal{E}$，潜变量 $z=\mathcal{E}(x)\in\mathbb{R}^{h\times w\times c}$，解码 $\tilde{x}=\mathcal{D}(z)$。
- 下采样因子 $f=H/h=W/w$，取 $f=2^m$。
- 训练：感知损失（LPIPS）+ patch 对抗目标，使重建落在图像流形、减轻纯 $L_1/L_2$ 模糊。
- 潜空间正则两种实验变体：
 - **KL-reg.：** 轻微 KL 拉向标准正态（类 VAE）；
 - **VQ-reg.：** 在解码器侧吸收向量量化层（可视为量化进 decoder 的 VQGAN 变体）。

要点：**DM 保留 $z$ 的二维结构**，故可用较温和 $f$，重建明显好于把 $z$ 压成 1D 再自回归的路线（§3.1，Tab. 8）。

### 2.3 数学辅线：像素 DM → 潜空间目标（§3.2，Appendix B）

扩散模型学习通过逐步去噪恢复数据分布，对应长度 $T$ 的固定前向马尔可夫链的逆过程。图像合成上最成功的设定多用**重加权变分下界**，等价于一串去噪自编码器 $\epsilon_\theta(x_t,t)$。简化目标（文中 Eq. 1）：

$$
L_{\mathrm{DM}}=\mathbb{E}_{x,\epsilon\sim\mathcal{N}(0,1),t}\Big[\|\epsilon-\epsilon_\theta(x_t,t)\|_2^2\Big],
$$

$t$ 在 $\{1,\ldots,T\}$ 上均匀采样。

换到潜空间后（Eq. 2）：

$$
L_{\mathrm{LDM}}:=\mathbb{E}_{\mathcal{E}(x),\epsilon\sim\mathcal{N}(0,1),t}\Big[\|\epsilon-\epsilon_\theta(z_t,t)\|_2^2\Big].
$$

骨干 $\epsilon_\theta$ 为**时间条件 U-Net**；训练时 $z_t$ 由冻结的 $\mathcal{E}$ 高效得到；采样得到 $z$ 后经 $\mathcal{D}$ **单次**解码回像素。

Appendix B 补充前向过程的 SNR 表述：$q(x_t|x_0)=\mathcal{N}(x_t\mid\alpha_t x_0,\sigma_t^2 I)$，并用 $\epsilon$-参数化把 ELBO 项写成去噪 MSE；重加权后得到上述简化目标。本卡不展开完整 ELBO 推导，只锚定「**噪声预测 MSE + 潜空间替换 $x\leftarrow z$**」。

### 2.4 条件机制：拼接 vs Cross-Attention（§3.3）——与 LLM 交叉的接口点

条件分布 $p(z\mid y)$ 用 $\epsilon_\theta(z_t,t,y)$ 实现。LDM 提供两类接入（Fig. 3）：

1. **拼接（concatenation）：** 适合空间对齐条件（语义图、低分辨率图、inpainting mask 等），可卷积式外推到 $\sim 1024^2$（§4.3.2）。
2. **Cross-attention（架构主贡献之一）：** 域编码器 $\tau_\theta$ 把 $y$（如文本）映为 $\tau_\theta(y)\in\mathbb{R}^{M\times d_\tau}$，再与 U-Net 中间特征 $\varphi_i(z_t)$ 做

$$
\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\Big(\frac{QK^\top}{\sqrt{d}}\Big)V,
$$

其中 $Q=W_Q^{(i)}\varphi_i(z_t)$，$K=W_K^{(i)}\tau_\theta(y)$，$V=W_V^{(i)}\tau_\theta(y)$。

条件 LDM 目标（Eq. 3）：

$$
L_{\mathrm{LDM}}:=\mathbb{E}_{\mathcal{E}(x),y,\epsilon\sim\mathcal{N}(0,1),t}\Big[\|\epsilon-\epsilon_\theta(z_t,t,\tau_\theta(y))\|_2^2\Big],
$$

$\tau_\theta$ 与 $\epsilon_\theta$ **联合**优化。文本时 $\tau_\theta$ 可为（未掩码）Transformer；布局等亦同构。

**跟读金句：** LDM 把「多模态」做成**生成器侧的条件接口**（token 条件 → cross-attn），不是 [[多模态架构脉络]] 里「冻结 LM + 视觉 token 续写文本」。

### 2.5 压缩倍率权衡与关键实证（§4.1–4.3）

- 固定单卡 A100、同参数与步数，扫 $f\in\{1,2,4,8,16,32\}$：$f$ 太小（接近像素）训练慢；$f$ 太大（如 32）过早平台且上限差；**LDM-\{4–8\}** 在效率与保真之间较优；ImageNet 上 2M 步后 LDM-8 相对 LDM-1 出现约 **38** 的 FID 差距（§4.1）。
- 无条件：CelebA-HQ 上报 FID **5.11**（Tab. 1，文称相对先前似然模型与部分 GAN 更优）。
- 文生图：LAION-400M 上训 **1.45B** 参数 KL-LDM；MS-COCO $256^2$ 上 LDM-KL-8 FID **23.31**，加 classifier-free guidance（$s=1.5$）的 LDM-KL-8-G FID **12.63**（Tab. 2）——与同期大参数 AR / 扩散方法同量级，参数更少。
- 类别条件 ImageNet：LDM-4-G（cfg $s=1.5$）FID **3.60**（Tab. 3）。
- 局限（§5）：逐步采样仍慢于 GAN；$f=4$ 重建损失对**需要像素级高精度**的任务可能成瓶颈（作者点名超分等）。

---

## 三、DiT：用 Transformer 换掉 U-Net，并证明「算力可扩展」

### 3.1 架构思想：U-Net 归纳偏置并非必需

DiT（摘要 / §1）指出：扩散图像模型长期默认 **卷积 U-Net**（自 Ho et al. DDPM 继承，Dhariwal & Nichol ADM 等主要做自适应归一化、通道等消融，**高层设计大体未动**）。DiT 的主张是：

> U-Net 归纳偏置**不是**扩散性能的关键；可换成标准 **Vision Transformer** 设计，从而继承 Transformer 在深度/宽度/token 数上的规模化性质，并与其他领域架构统一。

实现落点：在 **LDM 框架**内，用 Transformer 在 **VAE 潜空间的 patch 序列**上做去噪（可用现成卷积 VAE + Transformer DDPM 的混合管线；§3.1）。

### 3.2 设计空间（§3.2）

**Patchify：** 对潜变量空间表示（例：$256\times256\times3$ 图 → $f=8$ VAE → $z$ 为 $32\times32\times4$）按 patch 大小 $p$ 线性嵌入为长度 $T=(I/p)^2$、宽 $d$ 的 token 序列，加 ViT 式频率位置编码。$p\in\{2,4,8\}$：$p$ 减半 → $T$ 约 **4×** → Transformer Gflops 至少约 **4×**，但**参数量几乎不变**。

**条件块四种变体（Fig. 3，Fig. 5）：**

| 变体 | 做法 | 相对开销（文中） | 实证 |
|------|------|------------------|------|
| In-context | $t$、$c$ 嵌成两个额外 token，与图像 token 同等自注意力 | 几乎忽略 | 最弱 |
| Cross-attention | $t,c$ 成长度 2 序列，块内加 MH cross-attn（类 LDM） | 约 **+15%** Gflops | 中等 |
| adaLN | 用 $t+c$ 嵌入回归 LN 的 $\gamma,\beta$（FiLM / ADM 系） | 最低之一 | 较好 |
| **adaLN-Zero** | 再回归残差前的 $\alpha$，MLP 零初始化使块初始为恒等 | 同 adaLN 量级 | **全程最优** |

之后全文默认 **adaLN-Zero**。

**模型档位（Table 1）：** DiT-S/B/L/XL，对齐 ViT 的层数/隐宽/头数；设计空间 Gflops 覆盖约 **0.3–118.6**（随 $p$ 与分辨率变）。

**解码头：** 最终 LN（可自适应）+ 线性层，每 token 解出 $p\times p\times 2C$（噪声与对角协方差），再重排回空间布局。

### 3.3 数学辅线：与 LDM 共享的扩散骨架 + CFG（§3.1）

前向：$q(x_t|x_0)=\mathcal{N}(x_t;\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I)$，重参数 $x_t=\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon_t$。

逆过程：$p_\theta(x_{t-1}|x_t)=\mathcal{N}(\mu_\theta(x_t),\Sigma_\theta(x_t))$。将 $\mu_\theta$ 重参数为噪声网 $\epsilon_\theta$ 后，简单目标：

$$
\mathcal{L}_{\mathrm{simple}}(\theta)=\|\epsilon_\theta(x_t)-\epsilon_t\|_2^2.
$$

学协方差时跟 Nichol & Dhariwal：$\epsilon_\theta$ 用 $\mathcal{L}_{\mathrm{simple}}$，$\Sigma_\theta$ 用完整 KL 项。

**Classifier-free guidance（CFG）：** 训练时随机丢掉条件 $c$ 换成可学习空嵌入 $\emptyset$；采样时

$$
\hat\epsilon_\theta(x_t,c)=\epsilon_\theta(x_t,\emptyset)+s\cdot\big(\epsilon_\theta(x_t,c)-\epsilon_\theta(x_t,\emptyset)\big),\quad s>1.
$$

（文中由 Bayes / score 解释导出。）DiT 同样受益于 CFG。

**训练设定要点（§4）：** ImageNet 类别条件；离架 Stable Diffusion VAE（下采样 **8**）；AdamW，恒定 lr $10^{-4}$，batch 256，无 weight decay；EMA 0.9999；$T=1000$ linear schedule（ADM 超参）。**几乎未做** ViT 常见的 lr warmup / 强正则，文称各配置训练稳定、未见常见 loss spike。

### 3.4 规模化定律式结论（§5）——架构主结论

1. **更大 Gflops → 更低 FID：** 加深加宽或减小 $p$（加 token）在训练全程一致改进（Fig. 6–8）；相近 Gflops 的不同配置 FID 接近。
2. **参数量不足以定质量：** 固定模型档、减小 $p$ 时参数几乎不变，但 Gflops 升、FID 降。
3. **大模型更吃得动训练算力：** 小模型训更久也难追上大模型在更少步数下的效率曲线（Fig. 9）。
4. **加采样步数补不回模型算力缺口：** 小模型即使用更多采样步（更高采样 Gflops）仍难超过大模型较少步的结果（Fig. 10，§5.2）。
5. **SOTA 数字（Table 2/3，cfg）：**
 - ImageNet **$256^2$**：DiT-XL/2-G（cfg=1.50）FID **2.27**（此前 LDM-4-G cfg=1.50 为 **3.60**）。
 - ImageNet **$512^2$**：DiT-XL/2-G（cfg=1.50）FID **3.04**（文中对比 ADM-G, ADM-U 的 **3.85**）。
 - XL/2 在 $256^2$ 约 **118.6 Gflops**，相对像素 ADM（约 **1120 Gflops**）算力更省（Fig. 2 右）。

结论段（§6）明示后续可把 DiT 作 DALL·E 2 / Stable Diffusion 类**文生图**的 drop-in 骨干——这是与 LLM 文本塔交叉的产品接口，但 **DiT 正文实验本身是类别条件 ImageNet，不是完整文生图系统卡**。

---

## 四、与 LLM 条件 / 跨模态交叉（生成侧接口图）

本节只写两篇入口**已经说清或直接指向**的交叉，不脑补未读的「统一理解—生成」旗舰报告。

### 4.1 条件编码器 $\tau_\theta$：文本专家可以是 Transformer，乃至更强 LM

LDM §3.3 / §4.3.1：文本条件用 **BERT tokenizer + Transformer $\tau_\theta$**，经 cross-attn 注入 U-Net；$\tau_\theta$ 与去噪网联合训。布局条件同构（离散化框 + 类 id）。
**交叉含义：** 「LLM 相关模块」在生成线里首先扮演 **条件塔 / 提示编码器**，不是回答用户问题的对话 LM。是否换成冻结的大规模 LLM 文本编码器、是否用 CLIP 文本塔等，属于后续系统工作；**本卡入口未规定必须用对话级 LLM**。

### 4.2 Classifier-free guidance：采样期「听条件」的旋钮

LDM 与 DiT 均依赖 Ho & Salimans 的 CFG：训练丢条件、采样时外推条件与无条件分数差。文生图与类别条件表格中，加 G 的变体 FID / IS 显著变化（LDM Tab. 2–3；DiT Tab. 2–3）。
**交叉含义：** 产品侧「提示遵循强度」大量落在 **$s$**，与对话温度不是同一旋钮；过高 $s$ 常损多样性（两文 Precision/Recall 叙事均提示权衡）。

### 4.3 潜空间 AE：生成线与「视觉 token」叙事的分叉点

- LDM/DiT：**连续（或 VQ 正则）空间潜变量 + 迭代去噪**，解码器一次成像。
- 部分 generative VL / 离散码本 AR（LDM 相关工作对比的 VQGAN+Transformer、DALL-E 等）：**离散码上自回归**，压缩往往更猛。

[[多模态架构脉络]] 的视觉指令模型多走「视觉特征 → LM 词表侧」；生成线走「文本条件 → 图像似然模型」。**统一离散视觉 token 同时服务理解与生成**是另一支线，议程与 [[多模态架构脉络]]「待核实」已提示需另开笔记——**本卡不展开未核论文**。

### 4.4 DiT 之后的「LLM × 扩散」产品形态（仅标接口，不编造报告）

由入口可严格推出的接口层：

1. **Text → $\tau_\theta$ → cross-attn / adaLN 条件 → 潜空间扩散 → VAE decode**（LDM 已实现的文生图骨架；DiT 建议替换其中 U-Net）。
2. **混合流水线：** 例如用 Transformer 扩散产 CLIP 图像嵌入再解码（DiT 相关工作提及 DALL·E 2 用 Transformer 合成非空间 CLIP 嵌入）——属引用中的存在性说明，**细节以各系统论文为准，此处不复述未下载 PDF 的内部数**。
3. **视频旗舰（Sora 等）正式技术报告：待核实**（议程 [[扩散生成式视觉与LLM]]）。无稳定公开 PDF 前，不把二手博客结构图写入本卡「已核实」节。

### 4.5 与 [[多模态架构脉络]] 对照一句

| | [[多模态架构脉络]] | B-10 |
|--|------|------|
| 主概率 | $p(\text{text}\mid\text{vision},\ldots)$ | $p(\text{vision}\mid\text{text}/\text{class}/\text{map},\ldots)$ |
| 迭代轴 | 自回归 token | 扩散时间步 $t$ |
| 「Transformer」角色 | 多在语言骨干或桥接层 | 可在去噪骨干（DiT）或条件塔（LDM $\tau_\theta$） |
| 典型指标 | zero-shot / VQA / 对话 | FID、IS、Precision/Recall、采样吞吐 |

---

## 五、误区

1. **「LDM = 把 VAE 和扩散一块端到端猛训」**
 LDM 强调**先固定**感知压缩模型，再在其潜空间训 DM，避免重建与生成能力的脆弱加权（对比联合训的 LSGM 等，§1 贡献 (iii)、§4.2）。

2. **「压缩倍率越大越好（越省算力就必然越强）」**
 §4.1：过小 $f$ 把感知负担丢回 DM；过大 $f$ 信息损失封顶。甜蜜区在中等 $f$（常 4–8）。

3. **「Cross-attention 是 DiT 上条件注入的唯一/最佳选择」**
 DiT 在同类算力下 **adaLN-Zero ≫ cross-attn / in-context**（Fig. 5）。LDM 的 U-Net + cross-attn 与 DiT 的 ViT + adaLN-Zero 是**不同骨干上的不同最优条件通道**，不能混抄。

4. **「参数量越大生成一定越好」**
 DiT：看 **Gflops**（含分辨率与 patch/token）；减小 $p$ 几乎不加参却显著涨算力、降 FID。

5. **「采样步数加够，小模型可追上大模型」**
 DiT §5.2：采样算力补不满模型算力缺口。

6. **「文生图模型 = 多模态对话模型」**
 见 §一与 §四；条件塔吃文本 ≠ 视觉问答。

7. **「DiT 论文已经训好了开放域文生图并给出与 SD 对等的系统卡」**
 正文 SOTA 表是 **ImageNet 类别条件**；文生图是结论中的**前景接口**，不是该 PDF 的主实验交付。

8. **「视频生成旗舰结构已可从新闻稿当作论文事实引用」**
 议程：**待核实**。本卡不写二手架构断言。

---

## 六、引用

### 6.1 本卡强制入口（已下载）

- Rombach, Blattmann, Lorenz, Esser, Ommer. *High-Resolution Image Synthesis with Latent Diffusion Models*. arXiv:2112.10752. URL：`https://arxiv.org/pdf/2112.10752`；
- Peebles & Xie. *Scalable Diffusion Models with Transformers*. arXiv:2212.09748. URL：`https://arxiv.org/pdf/2212.09748`；

### 6.2 文中依赖、本卡未强制深读的经典（仅作指针）

- Ho, Jain, Abbeel. *Denoising Diffusion Probabilistic Models*（DDPM / 重加权目标）
- Ho & Salimans. *Classifier-Free Diffusion Guidance*
- Dhariwal & Nichol. *Diffusion Models Beat GANs on Image Synthesis*（ADM；U-Net 消融与 Gflops 讨论的前作）
- Ronneberger et al. U-Net；Dosovitskiy et al. ViT；Esser et al. VQGAN；Ramesh et al. DALL-E（LDM 对比的两阶段 AR 路线）

### 6.3 与已入库笔记的双链

- **[[多模态架构脉络]]** 多模态与具身/视觉语言/多模态架构脉络.md：理解/对话线；本卡不重写 CLIP/Flamingo/LLaVA。
- [[MOC_多模态与具身]]

### 6.4 待核实

- **视频生成旗舰**（如 Sora 等）**正式、稳定公开的技术报告 PDF** 与可复核架构图。
- 「统一理解—生成」单一骨干（离散视觉 token、自回归与扩散混合等）的代表性论文对照表——需另开笔记，入口核实后再写。
- 将 DiT 换入开放域文生图（SD 类）后的完整系统超参、文本塔选型与人评——超出 DiT 原文实验范围。
- LDM 仓库后续衍生（Stable Diffusion 各版）的训练数据与安全过滤细节：以各模型卡 / 报告为准，**不在本卡断言**。

---

## 附：跟读路径建议

1. LDM §1 + Fig. 2 → 建立「感知压缩 vs 语义压缩 / 为何进潜空间」。
2. LDM §3.1–3.3 → AE 正则、$L_{\mathrm{LDM}}$、cross-attn 条件（与 LLM 交叉的第一接口）。
3. LDM §4.1 → $f$ 权衡，建立「不是压得越狠越好」。
4. DiT §3.1–3.2 → patchify、四种条件块、为何锁定 adaLN-Zero。
5. DiT §5 + Fig. 8–10 → Gflops–FID 与「采样步补不回模型算力」。
6. 回到本卡 §四 → 只记生成侧条件接口；视频与统一模型标待核实。

## 相关笔记

- [[分词器与数据配比|B3 Tokenizer / 数据配比]]
- [[优化器与训练稳定性|B4 优化器]]
- [[安全红队与对抗评测|B5 红队]]
- [[检索增强与知识外挂|B6 RAG]]
- [[推理引擎生态|B7 推理引擎]]
- [[合成数据与教科书式数据|B8 合成 / 教材数据]]
- [[扩散生成式视觉与LLM|B10 扩散与视觉生成]]
- [[AI基础设施总览|AI Infra]]

