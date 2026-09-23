---
title: "地球系统 FM 增量：ESFM 异构数据统一框架（≠ Aurora / ≠ ClimateAgent）"
topic: 地球系统基础模型ESFM
date: 2026-09-22
lines: [架构思想, 数据接口, 文内预报字段]
status: archived
sources:
 - https://arxiv.org/abs/2605.00850 # PDF ~11.43MiB / 48p → **仅 HTTPS 外链（不入库）**
aux:
 - https://arxiv.org/abs/2605.00850
 - https://arxiv.org/pdf/2605.00850
 - https://github.com/swiss-ai/ESFM
 - https://huggingface.co/ESFM
 - https://swiss-ai.github.io/ESFM/
 - https://github.com/swiss-ai/SwissClim_data_processing_scripts
 - https://github.com/swiss-ai/SwissClim_Evaluations/tree/v0.2.0
arxiv: ["2605.00850"]
related: ["天气气候基础模型", "气候科学Agent", "SkySense遥感基础模型", "表格与时序基础模型"]
code: "https://github.com/swiss-ai/ESFM"
retrieval_cutoff: 2026-09-22
timezone: Asia/Shanghai (CST)
---

# 地球系统 FM 增量：ESFM（≠ Aurora / ≠ ClimateAgent）

> **定位**：地球系统基础模型增量——在 **[[天气气候基础模型]] Aurora**（地球系统 foundation **预报骨干**）与 **[[气候科学Agent]] ClimateAgent**（气候数据科学 / 政策 **Agent 编排**）已立之后，本卡只写 **ESFM**（*Earth System Foundation Model*，arXiv:**2605.00850**v1）作为 **异构缺失数据整合、多分辨率 tokenizer、站点/卫星、AdaLN 概率集合** 的 **统一框架增量**。
> **攻坚线**：**架构思想 / 数据接口（主）** + **文内预报字段（辅）**。
> **硬划界（开篇钉死）**：
> - **≠ [[天气气候基础模型]]**：禁止重写 Aurora **1.3B** 骨干表、3D Perceiver + 3D Swin U-Net 层表、四域微调通史、Aurora 1.5 产品增量。本卡承认 ESFM **显式复用 Aurora 的 3D Swin UNet backbone**（文内引用 Bodnar et al. 2025），但只录 **ESFM 相对 Aurora 的接口增量**（逐变量 tokenization、NaN token、多分辨率 bin、axial attention、AdaLN-Zero 集合、掩码训练、KD 对齐），**禁止把本卡写成 Aurora 复读**。
> - **≠ [[气候科学Agent]]**：禁止写成 ClimateAgent / ClimateAgents / ClimAgent 多代理编排、报告流水线、政策仿真。ESFM 是 **格点/站点场预报 FM**，不是 LLM Agent。
> - **≠ [[SkySense遥感基础模型]]**：禁止写成 SkySense / SkySense++ / V2 遥感 **影像解译** EO FM。ESFM 吃的是大气/地表物理变量场与站点序列，不是高分光学+SAR 语义分割主轴。
> - **≠ [[表格与时序基础模型]]**：禁止写成 TabPFN / TimesFM / Chronos 表格·通用时序 foundation。站点实验只是 ESFM 统一骨干下的 **点数据接口**，不是独立 tabular/TS FM 谱系。
> **禁止编造**：参数量、MAE/CRPS、掩码概率、页数/体积一律锚定本地 （，2026-09-22 CST）与 `ls`；图柱未抽出标「待核实读图」。

---

## 一、材料元信息与 PDF 体积

| 材料 | 标识 | 本地 / URL | 角色 |
|---|---|---|---|
| **主文** | Ozdemir, Cheng, Mohebi, Lehmann, Adamov, Zhang, Trentini, Grund, Fuhrer, Hoefler, Mishra, Schemm, Soja & Salzmann, *Earth System Foundation Model (ESFM): A unified framework for heterogeneous data integration and forecasting* | arXiv:**2605.00850v1** \[physics.ao-ph\]（兼 cs.AI / cs.LG / eess.IV）；页眉 **20 Apr 2026**；Submitted **20 Apr 2026**；XMP MetadataDate **2026-05-05T00:03:16Z**（→ **2026-05-05 08:03 CST**）；License **CC BY-NC-SA 4.0**；PDF 链接 https://arxiv.org/pdf/2605.00850（**未入库二进制**；见 `https://arxiv.org/abs/2605.00850`） | 主锚：异构数据统一框架 |
| **抽取** | 同上 | （**180,704 B ≈ 177 KiB**） | 全文检索 |
| **代码（辅）** | swiss-ai/ESFM | https://github.com/swiss-ai/ESFM（README 自称基于 Aurora stack 扩展；权重 HF `huggingface.co/ESFM`；Pages `swiss-ai.github.io/ESFM/`；预处理 `SwissClim_data_processing_scripts`；格点评测 `SwissClim_Evaluations` v0.2.0） | 开源训练/推理入口 |

| 文件 | 路径 | 体积 | 页数 | 备注 |
|---|---|---|---|---|
| ESFM PDF | https://arxiv.org/pdf/2605.00850（本盘仅 `/tmp` 校验，**未**写入 `*.pdf`） | **11,983,606 B ≈ 11.43 MiB** | **48** letter | **建议正式外链**（>10MB；议程亦标页数偏长→抽取优先） |
| ESFM 抽取 | | **177 KiB** | — | 瘦身主资产 |
| PDF 说明 | `https://arxiv.org/abs/2605.00850` | 短 stub | — | 记录体积决策 |

**一句话抓手：** Aurora 解决「稠密再分析上可缩放的 Earth-system FM 骨干」；ESFM 在同一 **3D Swin UNet** 上加 **逐变量 tokenization + 可学习 NaN + 六档多分辨率 tokenizer（含站点 1×1）+ 变量维 axial attention + AdaLN-Zero 集合**，把 foundation 从「通道齐全的格点张量」推到 **卫星稀疏 / 站点不规则 / 任意缺失维** 仍可预报——而不是再开一条 Agent 编排或遥感解译轴。

---

## 二、议题边界：异构数据接口增量 ≠ Aurora 骨干复读 ≠ Agent ≠ EO 解译 ≠ 表格时序 FM

### 2.1 四向对照（跟读）

| 邻卡 | 邻卡主锚 | 本卡只取 / 禁止 |
|---|---|---|
| **[[天气气候基础模型]]** | Aurora 1.3B；预训练→多域微调；Nature Earth-system FM | **只取**：ESFM 声明「builds on … Aurora」与 KD 对齐 small Aurora encoder；**禁止**重写 Aurora 骨干层表、参数缩放表、四域评测全文 |
| **[[气候科学Agent]]** | ClimateAgent 多代理气候数据科学 / ClimateAgents 社会—气候 | **禁止**任何 LLM 角色分层、工具调用编排、报告质量分 |
| **[[SkySense遥感基础模型]]** | SkySense 谱系：光学+多光谱+SAR 影像解译 | **禁止** RS 语义分割 / few-shot EO benchmark 主文 |
| **[[表格与时序基础模型]]** | TabPFN-3.5 + TimesFM / Chronos | **禁止**把 Weather-5K / 11k 站点写成独立 tabular/TS FM；站点是 ESFM **统一 backbone 的点数据 bin** |

### 2.2 文内自我定位（可核）

摘要与 §1.4：ESFM 是 **foundation model**（先学物理变量统计关系，再 finetune），**不是** task-specific weather forecasting model；相对既有 FM「假定通道齐全、时空格点完整」的假设，强调 **raw observations 天然稀疏、CMIP6 网格/缺失不一致**——理想 FM 应在 **统一 backbone** 内处理，而非插值填缺或每套变量重训 encoder/decoder。

---

## 三、架构思想 / 数据接口（主）

> 本节只写 **ESFM 相对「稠密多通道拼接」与相对 Aurora density-channel 做法** 的接口差；**不**复述 Aurora 3D Swin 内部块配置表（附录 A.3 仅录 ESFM s 与 Aurora s **对齐的少量默认超参**）。

### 3.1 统一框架（Fig. 1 / 贡献列表）

文内六条贡献（§1.4）：

1. **Missing data**：每变量独立 patch embedding + 掩码训练 → 初值局部无数据区域仍可 skillful 预报。
2. **Multimodality under one backbone**：多分辨率 tokenizer，把相近水平分辨率分 bin，共享变量 tokenizer 集合——覆盖 CMIP6 粗网格、**0.25° ERA5**、更细卫星、乃至站点点数据。
3. **Axial-attention**（Ho et al. 2019）：在 **变量维** 上做短上下文自注意力，刻画变量间依赖。
4. **Positional embeddings**：decoder 侧对 latent 加 **2D sine-cosine**，强化 detokenizer 位置信息。
5. **Probabilistic forecasting**：对确定性 ESFM 用 **AdaLN-Zero** 调制 latent，低成本扩成集合。
6. **Open community model**：训练脚本、权重、预处理全开源（脚注：`github.com/swiss-ai/ESFM`）。

### 3.2 Encoder：逐变量 tokenize → axial → Perceiver（Fig. 2）

流程（§2）：

1. **大气 / 地表变量分别**做 patch embedding（非 RGB 式通道拼接）。
2. **Axial attention** 跨变量 token（变量维自注意力；上下文极短）。
3. **Variable perceiver**（Jaegle et al. 2021）分别把大气变量、地表变量压到 latent 变量数；query 为可学习变量 embedding。
4. **Atmospheric level perceiver** 再沿气压层聚合——文内写明「as was originally proposed in Aurora」。
5. 与位置 / 面积 / 时间等 embedding concat 后进 backbone。

相对 ClimaX「用可学习向量做 cross-attn 聚合」：ESFM 选 **axial + perceiver**，并强调高分辨率下「每变量独立 tokenization」否则显存易爆。

### 3.3 缺失数据：可学习 NaN token（Fig. 3）— 对比 Aurora density channel

- **Aurora 做法（文内复述，不展开骨干）**：对可能部分缺失的变量加 **density channel**（波场例）；ESFM 批评其 (1) 不适合「观测/同化导致整变量缺失」时的推断；(2) **每多一变量 ≈ 输入输出通道翻倍**，扩展性差。
- **ESFM**：patch 内部分或全部缺失 → 换成 **可学习 NaN token**，并带上对应 **variable-type** 位置编码；可覆盖部分缺失、完全缺失，并自然扩展到缺失气压层（文称亦可扩到时间维）。

### 3.4 多分辨率 patch embedding + 站点 greedy 映射（§2.2 / Fig. 4）

**六档 resolution bin**（附录 A.3，与正文「six discrete bins」一致）：

| Bin | 分辨率区间（文内） |
|---|---|
| Very coarse | $(1.5^\circ, \infty)$ |
| Coarse | $(0.5^\circ, 1.5^\circ]$ |
| Medium | $(0.15^\circ, 0.5^\circ]$ |
| Fine | $(0.05^\circ, 0.15^\circ]$ |
| Very fine | $[10^{-5\circ}, 0.05^\circ]$ |
| Station | 分辨率记为 $0^\circ$；**1×1 pixel** patch |

站点：把 in-situ 列表 **贪心映射**到不规则经纬网格（软约束：列内纬度、行内经度单调），使窗口注意力邻居仍近似地理邻居；最小 patch area 位置嵌入从 $0.01^\circ$ 降到 $10^{-5\circ}$（赤道约 $1.2\,\mathrm{m}^2$ vs $1.2\,\mathrm{km}^2$）。**不修改 Aurora 的 3D Swin UNet backbone** 即可训站点。

### 3.5 确定性 → 集合：AdaLN-Zero（§2.3 / Fig. 5 / 式 1）

对 backbone 输出 latent $z$，用集合成员标识构造条件向量 $c_i^{\mathrm{ens}}$：

$$
z' = z + \gamma(c_i^{\mathrm{ens}})\,\mathrm{LN}(z) + \beta(c_i^{\mathrm{ens}})
$$

- $\gamma,\beta$ **零初始化** → 扩展非破坏（初始各成员=确定性输出）。
- 训练可只采样 $N$ 的子集 → 文称可扩到数千成员，**仅 AdaLN 参数近似线性增**；**backbone 不必多次前向**。
- 损失：`almost fair CRPS`（Lang et al. 2024b）+ 集合均值 **MAE**，等权；规则 lat-lon 网格加纬度加权。
- 主实验集合规模：**$N=8$**；文亦述 $N=1000$ 时每步随机选 $N_s=8$ 成员优化。

Decoder：气压层 perceiver 可query **与观测不同的目标层** → 再 AdaLN 出各成员 → 每变量 detokenizer。

### 3.6 ESFM s 规模锚定（禁止写成 Aurora 1.3B 表）

- 正文：比较实验统一用 **∼110 M** 的 **ESFM s**（「corresponds to small size Aurora」）。
- 附录 A.3：**115 M** parameters，「corresponding to Aurora small (Aurora s)」；默认沿用 Aurora 发布配置中的：embed dim **256**（backbone 输出因 skip 成 **512**）、backbone **3** 级 merge/split、drop path $p=0.2$；encoder perceiver 用后续 Aurora 仓库提出的 pre-LN on Q/K。
- KD 附录：teacher 曾用 Aurora **large (1.3 B)** 与 **small (117 M)**——本卡 **只录此数字作为 KD 设定**，**不**展开 Aurora large 骨干表。

---

## 四、训练协议（主接口续）

### 4.1 预训练三路径（§3.1 / Fig. 6）

| 标记 | 初始化 | 文内步骤 |
|---|---|---|
| **ESFM s,ri** | 随机 | 基线 |
| **ESFM s,ci** | 8 个 CMIP6（分辨率约 $0.7^\circ$–$1.9^\circ$）：CMCC, MIROC6, TaiESM1, NESM3, AWI, MPI-M, EC-Earth3, MRI-ESM2 | **92 k** steps 预训练后再 ERA5 |
| **ESFM s,kd** | KD：Aurora small encoder 作 teacher，对齐 ESFM encoder；随后用预训练 small Aurora **backbone+decoder** 权重 | KD **40 k** steps（附录：32 GPU；warmup 1k → lr **5e-4**，cosine → **4e-4**；L1 on logits；ERA5 1979–2020） |
| **ESFM s,kd\*** | 同 kd，但最终 ERA5 **100 k** 步 **关闭**掩码协议 | 与 SotA 稠密对比时用 |

文内结论：KD 初始化最优；后续默认以 **ESFM s,kd**（简称 ESFM s）为起点，并显式声明后续实验是否带掩码。

### 4.2 三种掩码 + 气压层随机子集（§3.2 / A.2）

默认掩码概率（CMIP6 与后续 ERA5 掩码训练共用）：

- 变量掩码 $p_v = 0.5$
- 气压层掩码 $p_l = 0.25$
- 连续空间掩码 $p_s = 0.25$（Baevski et al. 2023）

额外探索：从 WeatherBench2 ERA5 的 **37** 层中随机抽 $n_l=13$ 层，且观测与目标 **分别**抽样——相对固定 13 层掩码训练，6h MAE 恶化约 **85.4%–500%**（Table 11）；作者怀疑 **气压层 perceiver** 聚合局限，尝试加深/换 Perceiver 仍类似，标为未来工作。

### 4.3 默认 ERA5 设定（§4 开篇）

- 时段：**1979–2020**；lead：**6 h**
- 大气：**5** 变量 × **13** 气压层；地表 **4**；静态 2D **3**（与公开模型可比）
- 测试初始化：2023/2024 的 1/4/7/10 月 **2 日 00Z**，各四周（除非另说明）
- 自回归 rollout 至 **7 天**见附录 B

---

## 五、文内预报字段（辅）

> 只摘可核表数字；不外推未给的全集变量排名。

### 5.1 预训练消融（Fig. 6，6h MAE；带掩码的前三行）

| 模型 | T850 | Z500 | Q850 | T2m | U10m | V10m |
|---|---|---|---|---|---|---|
| ESFM s,ri | 0.300 | 26.676 | 2.88e-4 | 0.306 | 0.322 | 0.332 |
| ESFM s,ci | 0.281 | 26.218 | 2.67e-4 | 0.290 | 0.301 | 0.313 |
| ESFM s,kd | 0.248 | 15.910 | 2.48e-4 | 0.269 | 0.280 | 0.290 |
| ESFM s,kd\*（无掩码终训） | 0.224 | 12.535 | 2.24e-4 | 0.248 | 0.253 | 0.262 |

掩码终训相对无掩码：性能降幅文称约 **8.5%（T2m）–26.9%（Z500）**，中位 **10.7%（V850）**。

### 5.2 稠密 6h vs SotA（Table 1；ESFM s = 无掩码终训的 kd\*）

文内叙述：表面变量与 **AIFS / Aurora s** 相当，优于 GraphCast、SFNO、IFS Control；**Aurora l** 领先。上层类似：ESFM s ≈ Aurora s，AIFS 略优，Aurora l 最佳。作者称共享 backbone → ESFM **可缩放至 Aurora large 量级**同时保留灵活性（**主张级**，本卡不验证）。

摘录若干列（MAE）：

| 模型 | T850 | Z500 | T2m | U10m | V10m |
|---|---|---|---|---|---|
| **ESFM s** | 0.224 | 12.535 | 0.248 | 0.253 | 0.262 |
| Aurora s | 0.218 | 13.825 | 0.246 | 0.256 | 0.262 |
| Aurora l | 0.167 | 11.687 | 0.194 | 0.195 | 0.201 |
| AIFS | 0.182 | 14.679 | 0.219 | 0.232 | 0.238 |
| GraphCast | 0.208 | 13.608 | 0.304 | 0.269 | 0.272 |
| SFNO | 0.217 | 13.852 | 0.255 | 0.282 | 0.294 |
| IFS Control | 0.346 | 15.804 | 0.421 | 0.433 | 0.444 |

### 5.3 集合（Table 2；$N=8$；`L = MAE + afCRPS`，10k steps）

| 模型 | U10m CRPS/MAE | V10m | T2m | T850 | Z500 | Q850 |
|---|---|---|---|---|---|---|
| **ESFM s+** | 0.249 / 0.260 | 0.258 / 0.269 | 0.238 / 0.248 | 0.218 / 0.225 | 14.484 / 15.311 | 2.19e-4 / 2.28e-4 |
| AIFS-CRPS | 0.259 / 0.246 | 0.264 / 0.251 | 0.265 / 0.238 | 0.202 / 0.188 | 15.946 / 14.098 | 2.08e-4 / 1.96e-4 |
| FourCastNet 3 | 0.250 / 0.236 | 0.260 / 0.246 | 0.250 / 0.235 | 0.199 / 0.186 | 12.641 / 11.761 | 2.03e-4 / 1.90e-4 |

文内：表面 CRPS **优于** AIFS-CRPS 与 FourCastNet 3；大气层更参差，FourCastNet 3 常居前，但差距「very comparable」。

### 5.4 缺失/稀疏设定（§5；选锚）

- **区域掩码**（CH / EU / CONUS）：全局 6h 精度降幅小；掩码区内仍可预报（Table 3–4）；文强调学到 Q–T–P 等非线性关系。
- **整变量缺失 / 整层缺失**（Table 5–6）：整层缺失代价更大（须从其他层推断）。
- **MODIS PWV**（稀疏；2020 有效像素占用中位约 **0–5%** 量级文述）：finetune 后 6h 见 Table 7；两周 rollout PCC 约 **IR ~0.9 / NIR ~0.83**（§6）；与 MODIS 比与 ERA5 派生 PWV 更贴——作者警告 **可能学到 MODIS 检索偏差**。
- **ECMWF ~11,863 站**（映射 90×180；holdout 1k）：Table 8 三设置——同站时间泛化 / **野生新站 I/O** / **仅旧站观测外推新站坐标**。例：Regular 6h T MAE **1.07**（PCC 0.98）；Holdout I/O 6h T **1.87**；Extrapolating 6h T **2.32**。
- **Weather-5K**（Table 9）：默认只用 $(t-\Delta t,t)$ 而非榜上 48h 历史，24h Overall **10.8**，优于表内 Pyraformer 等 24h Overall（13.6–14.8）。
- **未见气候模式 CNRM-CM6-1-HR**（Table 10）：CMIP6 预训练（±ERA5）finetune 优于仅 ERA5 / 无预训练；含未见变量 SST / 海冰 / TWS。

### 5.5 个例（辅；不展开工程规程）

- **Doksuri（2023-07）**：10 天 rollout；位置与 Aurora 在 96h 与 IBTrACS 较一致；强度上 **ESFM s 集合** 接近 ERA5 / Aurora large，**Aurora s** 偏弱；登陆后风速仍常低估；并提醒 ERA5 本身相对实况系统性偏弱（观测可达 ~60 m/s 量级文引）。
- **SSW 2023/24**：用垂直掩码策略 finetune 到 **16** 层（加 10/20/70 hPa）；Fig. 8 显示对 10 hPa、60°N 纬向风反转等有可预报性；文称对流层影响「encouraging」但 **>10 天**仍需更多确认。
- **长期稳定**：§4.6 / 摘要称保留既有 FM 的 long-term stability（细节见图版，未逐点抄）。

### 5.6 Summary 口径（§6）

- KD 相对随机初始化：变量相关 MAE 增益约 **12%–40%**，并省预训练算力。
- 灵活性换来相对「固定通道稠密模型」的 **边际 MAE/RMSE 代价**；可扩展 backbone 留作后续放大。
- 结构化掩码 ≈ 真实数据缺口代理；三维部分可观性（空间 / 变量 / 层）是主卖点。

---

## 六、代码辅源（README 快照，2026-09-22）

仓 https://github.com/swiss-ai/ESFM（未做完整 clone/复现；以下据 raw README）：

- 布局：`esfm/model/`、`utils/dataset.py`、`train.py`、`train_encoder_KD.py`、`inference.py` / `inference_rollout.py`、`evaluate_station_metrics.py`、`configs/`、`masking_config.yaml`、`loss_config.yaml`
- 环境：CSCS Alps Container Engine；modulus:24.04 / physicsnemo:25.03；多脚本默认 CSCS 路径，非 Alps 需改路径
- 权重：https://huggingface.co/ESFM
- 文档站：https://swiss-ai.github.io/ESFM/
- 预处理 / 格点评测：SwissClim 配套仓（见 YAML aux）

**不**把 README 未给的训练墙钟/集群配额写成事实。

---

## 七、跟读清单与反模式

**应跟读：** Fig. 2–5 数据流；§2.1 NaN vs density channel；§2.2 六 bin + 站点 greedy；§2.3 AdaLN 式 (1)；§3–4 预训练/掩码与 Table 1–2；§5 缺失/MODIS/站点；附录 A.2–A.3 概率与超参。

**反模式：**
1. 把本卡写成 **Aurora 1.3B / 四域微调** 复读（→ [[天气气候基础模型]]）。
2. 写成 **ClimateAgent** 编排或政策 Agent（→ [[气候科学Agent]]）。
3. 写成 **SkySense** 遥感解译（→ [[SkySense遥感基础模型]]）。
4. 写成 **TabPFN/TimesFM** 通史（→ [[表格与时序基础模型]]）。
5. 把「可扩到 Aurora large」当已完成缩放实验。
6. 把 MODIS 更贴合当成「更接近真值大气」。
7. 入库 **>10MB PDF 二进制**（本卡已按规矩拒绝）。

---

## 八、开放问题（文内已标 / 抽取未见则不填）

- 随机 37→13 气压层集合上的 **perceiver 瓶颈**（Table 11）如何改。
- ESFM **large** 是否兑现「保留灵活性同时追上 Aurora l」。
- 站点外推 / holdout 的误差结构（尤其气压 P 在 holdout 上 MAE 跳到 10³ 量级，Table 8）是否需专门位置编码或同化式接口。
- AdaLN 集合校准（spread–skill）全文表外细节。

---

## 九、来源与核验

- PDF：`curl` https://arxiv.org/pdf/2605.00850 → HTTP 200； **48** pages / **11,983,606** bytes；（2026-09-22 CST）。
- Abs/HTML 元数据交叉：Submitted **20 Apr 2026**；v1 only。
- GitHub README：`raw.githubusercontent.com/swiss-ai/ESFM/main/README.md`（API 限流时改 raw；2026-09-22）。
- **未**将 PDF 二进制写入 ；仅 README stub + 抽取。
