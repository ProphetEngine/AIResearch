---
title: "Audio-native / Omni 增量：Qwen3-Omni → Qwen3.5-Omni"
topic: QwenOmni音视频原生
date: 2026-09-22
lines: [架构思想, 评测字段]
status: archived
sources:
 - https://arxiv.org/abs/2509.17765
 - https://arxiv.org/abs/2604.15804
arxiv: ["2509.17765", "2604.15804"]
related: ["SpeechLLM语音语言模型", "多模态架构脉络", "Qwen3技术报告深读", "StepAudio2语音旗舰", "SeamlessM4T语音翻译", "音视频联合Flamingo", "OnPolicy蒸馏OPD范式", "BAGEL统一多模态生成"]
archived: 2026-09-22
---

# Audio-native / Omni 增量：Qwen3-Omni → Qwen3.5-Omni

> **主要来源**：[Qwen3-Omni Technical Report](https://arxiv.org/abs/2509.17765)（Qwen Team，v1 2025-09-22）；[Qwen3.5-Omni Technical Report](https://arxiv.org/abs/2604.15804)（Qwen Team，v1 2026-04-17，v2 2026-04-21）（截至 2026-07-17）。
> **研究线**：架构思想（主：Thinker–Talker 双 MoE、自研音频编码器 AuT、多码本流式语音合成、ARIA 交织对齐）；评测字段（辅：音视频基准、VoiceBench、首包延迟、与同尺寸单模态模型的对照）
> **范围与相邻笔记**：
> - ≠ [[SpeechLLM语音语言模型]]：那篇以 Qwen2-Audio 为锚，写「音频编码器接 LLM、输出文本」；本篇写文本、图像、音频、视频都能输入，并流式输出语音的原生全模态模型。
> - ≠ [[Qwen3技术报告深读]]：本篇只取骨干初始化与后训练接口，不写 Qwen3 文本训练。
>
> **意义**：全模态模型过去有个默认代价：加入音频和视觉后，文本与视觉能力会比同尺寸的单模态模型差。Qwen3-Omni 在预训练早期就混入单模态与跨模态数据，报告首次在文本、图像、音频、视频上都不低于同尺寸的 Qwen 单模态模型，同时在 36 个音频与音视频基准中的 22 个上达到总体最好，并用多码本加轻量卷积解码把理论首包延迟压到 234 ms；Qwen3.5-Omni 再把上下文扩到 256k、可处理 10 小时以上音频，并用 ARIA 解决流式语音合成的不稳。两代合起来说明「一个模型看、听、说」已可以不以牺牲单项能力为代价。

---

## 一、问题背景

语音进入大模型有三种形态：识别—翻译—合成的级联；音频编码器接 LLM、只输出文本（如 Qwen2-Audio，见 [[SpeechLLM语音语言模型]]）；同一模型多模态输入、直接流式输出语音。第三种要同时解决三件事：音视频长输入的时间对齐、语音输出的低延迟、加入新模态后原有文本与视觉能力不退化。Qwen2.5-Omni 提出 Thinker–Talker 架构：Thinker 负责理解与生成文本，Talker 负责生成语音（Qwen3-Omni §1）。Qwen3-Omni 与 Qwen3.5-Omni 是在此基础上的两次升级。

## 二、脉络

| 时间 | 工作 | 关键一步 |
|---|---|---|
| 2022-12 | [Whisper](https://arxiv.org/abs/2212.04356) | 大规模弱监督语音识别，此后多数语音 LLM 用它作音频编码器 |
| 2023-11 | [Qwen-Audio](https://arxiv.org/abs/2311.07919) | 多任务音频语言模型，音频入、文本出 |
| 2024-07 | [Qwen2-Audio](https://arxiv.org/abs/2407.10759) | 支持语音聊天与音频分析两种交互模式，仍只输出文本 |
| 2025-03 | [Qwen2.5-Omni](https://arxiv.org/abs/2503.20215) | 提出 Thinker–Talker，端到端全模态输入并流式输出语音 |
| 2025-09 | Qwen3-Omni | 双方改为 MoE，自研 AuT 替换 Whisper，多码本流式合成，报告不降级 |
| 2026-04 | Qwen3.5-Omni | 混合注意力 MoE、256k 上下文、ARIA 单流交织 |

## 三、方法

### 3.1 Qwen3-Omni 相对 Qwen2.5-Omni 的五项改动（§1、§2）

1. **双 MoE**：Thinker 与 Talker 都改为 MoE，开源版 Thinker 为 30B-A3B。
2. **AuT 替换 Whisper**：从零训练的音频编码器，用 2000 万小时有监督音频训练，约 0.6B 参数，输出 12.5 Hz 的音频 token，并用分块窗口注意力支持实时预填充。
3. **多码本语音表示**：Talker 每步生成一帧编码，由多 token 预测模块补出其余码本层。
4. **轻量波形解码**：把分块扩散解码换成因果卷积网络，拿到第一帧编码就能开始输出波形。
5. **低码率**：输入与输出音频都降到 12.5 Hz。

另外两个设计：音视频按绝对时间对齐的 TM-RoPE，不再像 2.5-Omni 那样切固定 2 秒块；Talker 不再读取 Thinker 的高层文本表示，只依赖多模态特征，文本可经外部模块（检索、函数调用、安全过滤）改写后再交给 Talker（§1、§2.3）。预训练分三段：先锁住从 Qwen3 初始化的 LLM 训编码器与适配器，再在约 2T token 上从一开始就混合单模态与跨模态数据，最后把上下文从 8,192 扩到 32,768（§3）。Thinker 后训练沿用 Qwen3 的强到弱蒸馏，再做 GSPO（§4）。

### 3.2 Qwen3.5-Omni 的改动（§1–4）

- **骨干**：Thinker 与 Talker 都用 Qwen3.5 的混合注意力 MoE（含 Gated DeltaNet），利于长音视频推理；上下文 256k，可处理 10 小时以上音频或 400 秒 720P（1 FPS）视频（§2.1、§2.5）。
- **AuT 再训**：4000 万小时音频—文本数据，输出 6.25 Hz（每帧约 160 ms）（§2.2）。
- **ARIA**：流式合成不稳常因文本与语音分词器的编码效率不一致。ARIA 把双轨输入改成单通道交织，不依赖强制对齐或固定交织比，只约束任意前缀中语音与文本 token 的累积比例不超过该样本的全局比例（§2.4）。
- **时间戳**：保留 TM-RoPE，但在每个视频与音视频时间块前插入以秒为单位的文本时间戳，音频按随机间隔插入，缓解长序列上时间位置编码过大、过稀的问题（§2.3）。
- **Thinker 后训练三阶段**：各领域教师分别做 SFT 与 RL 后蒸馏进统一模型；在线策略蒸馏，把同一问题在文本输入下的更好回答作为音频输入时的蒸馏目标；面向多轮交互体验（语码切换、人设漂移、长程指令遵循）的强化学习（§4.1）。

## 四、结果

| 工作 | 评测 | 结果 |
|---|---|---|
| Qwen3-Omni | 36 个音频与音视频基准（摘要） | 32 个开源最好，22 个总体最好 |
| Qwen3-Omni | 理论首包延迟（Table 1） | 音频输入 234 ms，视频输入 547 ms |
| Qwen3-Omni | VoiceBench 总分（Table 7） | 30B-A3B-Thinking 88.8，Flash-Thinking 89.5，Gemini-2.5-Pro 89.6 |
| Qwen3.5-Omni | 音频与音视频理解、推理与交互（摘要） | Plus 在 215 个子任务与基准上达到最好，关键音频任务超过 Gemini-3.1 Pro，综合音视频理解与之相当 |
| Qwen3.5-Omni | VoiceBench（Table 5） | Plus 93.1，Gemini-3.1 Pro 88.9 |
| Qwen3.5-Omni | LibriSpeech clean / other 词错率（Table 5） | Plus 1.11 / 2.23，Gemini-3.1 Pro 3.36 / 4.41 |
| Qwen3.5-Omni | 理论首包延迟（Table 1） | Flash 音频 235 ms、视频 426 ms；Plus 435 ms、651 ms |

不降级的证据是同尺寸对照：Qwen3-Omni 对 Qwen3-30B-A3B 与 Qwen3-VL-30B-A3B（§6）；Qwen3.5-Omni-Plus 对 Qwen3.5-Plus-Instruct，文本能力持平、指令遵循略好，视觉持平、视频理解更强（§5.1.1、§5.1.3）。

## 五、意义

两代 Omni 把「全模态」从拼接系统推进到一个可开源部署的端到端模型：自研编码器解决音频表示，Thinker–Talker 解耦让文本可被外部模块改写后再说出口，多码本加因果卷积解决首包延迟，早期混合预训练解决能力退化。Qwen3.5-Omni 的在线策略蒸馏与交互对齐 RL 则把重心转向「用语音问和用文字问一样好」与多轮对话体验，这是语音助手从演示走向产品的关键。

## 六、局限与待核实

- **参数量不公开**：Qwen3.5-Omni 摘要只说「数千亿参数」，正文没有给出 Plus 与 Flash 的精确参数量或专家配置；两者只通过 API 提供，开源的是 Qwen3-Omni 的 30B-A3B Instruct、Thinking 与 Captioner（Apache 2.0）。
- **语音输出语种口径不一**：Qwen3.5-Omni 摘要写语音生成覆盖 10 种语言，正文与 Table 3 写语音输出 36 种（29 种语言加 7 种方言），本篇按表。
- **VoiceBench 列名**：Qwen3-Omni 正文说「Qwen3-Omni-Thinking 得 89.5」，但 Table 7 中 89.5 属于 Flash-Thinking 列，开源的 30B-A3B-Thinking 为 88.8。
- **延迟不可横比**：首包延迟是理论值；Qwen3.5-Omni 的 Flash 与 Plus 部署时的资源分配与并行策略不同，作者提示延迟不宜直接比较（§2.5）。
- **涌现能力无评测协议**：「音视频 Vibe Coding」（按音视频指令直接写代码）是 Qwen3.5-Omni 报告的涌现能力，论文没有给出对应基准。

## 七、与相邻笔记的分工

| 相邻笔记 | 本篇只取 | 本篇不写 |
|---|---|---|
| [[SpeechLLM语音语言模型]] | 上游：Qwen2-Audio 的「Whisper 编码器接 LLM、输出文本」在那篇，本篇是其后替换编码器并加上语音输出的一代 | Whisper 前端与三阶段训练 |
| [[多模态架构脉络]] | 定位：那篇「全模态入、语音出」一条以本篇为节点 | 视觉 LMM 通史 |
| [[Qwen3技术报告深读]] | 上游：本篇的 LLM 初始化与强到弱蒸馏来自那篇 | Qwen3 文本训练 |
| [[StepAudio2语音旗舰]] | 对照：Step-Audio 2 用单一解码器按固定比例交织音文 token，本篇用 Thinker–Talker 双模型，Qwen3.5-Omni 改为自适应交织 | Step-Audio 2 训练与评测 |
| [[SeamlessM4T语音翻译]] | 对照：那篇是专门的多语语音翻译模型与同传策略，本篇是通用全模态助手 | UnitY 与 EMMA |
| [[音视频联合Flamingo]] | 对照：那篇是非 Qwen 系的开源音视频联合理解模型，把 Qwen-Omni 列为对照，语音输出靠自带可选的流式 TTS 模块 | OmniVinci 系训练配方 |
| [[OnPolicy蒸馏OPD范式]] | 方法：Qwen3.5-Omni 后训练第二阶段用在线策略蒸馏，把文本输入下的回答质量迁到音频输入 | OPD 的一般形式与其他用法 |
| [[BAGEL统一多模态生成]] | 对照：同为多模态入、多模态出，BAGEL 输出图像，本篇输出流式语音 | 图像生成与编辑 |

## 八、延伸阅读

| 顺序 | 材料 | 看什么 |
|---|---|---|
| 1 | [Qwen3-Omni](https://arxiv.org/abs/2509.17765) §1–3、Table 1 | 五项改动、AuT、Talker 解耦、预训练三段与延迟账 |
| 2 | [Qwen3.5-Omni](https://arxiv.org/abs/2604.15804) §2.3–2.4、§4.1 | 时间戳、ARIA、后训练三阶段 |
| 3 | [Qwen3.5-Omni](https://arxiv.org/abs/2604.15804) §5、Table 4–6 | 与 Gemini-3.1 Pro 及同尺寸单模态模型的对照 |
| 4 | [[SpeechLLM语音语言模型]] | 前一代音频入、文本出的做法 |
