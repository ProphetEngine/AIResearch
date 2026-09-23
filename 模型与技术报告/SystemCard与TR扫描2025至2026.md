---
title: "TR/System Card 扫描：2025-06-01 → 2026-09-22"
topic: TR-scan
date: 2026-09-22
as_of: 2026-09-22
window: "2025-06-01 .. 2026-09-22"
scope: "前沿模型正式 technical report / system card（官方或 arXiv 可核对）"
status: archived
archived: 2026-09-22
---

# 可派发清单（2025-06 → 2026-09）

扫描口径：仅列能核对到 **官方 PDF** 或 **arXiv PDF** 的条目；找不到 PDF 则「官方 URL + 待核实」。禁止编造型号。

已覆盖（可略 / 本地已有）：DeepSeek-V3、DeepSeek-R1、Qwen3、o1 system card、Claude 4 system card、GPT-4 tech report。

## 主表

| 型号 | 发布日 | 官方/arXiv URL | PDF 是否可下 | 本地路径或「未下载」 | 备注 |
|------|--------|----------------|--------------|----------------------|------|
| **Gemini 2.5**（Pro/Flash 等 2.X 族） | arXiv 2025-07（v6 至 2025-12）；模型卡更新约 2025-06-27 | https://arxiv.org/abs/2507.06261 · PDF https://arxiv.org/pdf/2507.06261 · 官方镜像 https://storage.googleapis.com/deepmind-media/gemini/gemini_v2_5_report.pdf | 是 | `https://arxiv.org/abs/2507.06261` | **重点**正式 TR；Thinking / 长上下文 / 多模态 |
| **GPT-5** System Card | 2025-08-07（页卡）/ PDF 元数据约 2025-08-13 | https://openai.com/index/gpt-5-system-card/ · PDF https://cdn.openai.com/gpt-5-system-card.pdf · arXiv 镜像 https://arxiv.org/abs/2601.03267 | 是 | `https://cdn.openai.com/gpt-5-system-card.pdf` | **重点**；router + main/thinking |
| **GPT-5.1** Instant/Thinking Addendum | 约 2025-11-12 | https://deploymentsafety.openai.com/gpt-5-1 · PDF https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf | 是 | `https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf` | GPT-5 系列增补卡 |
| **GPT-5.2** System Card Update | 2025-12-11 | PDF https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf | 是 | `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` | Instant/Thinking；Preparedness 更新 |
| **GPT-5.6** Preview / GA System Card | Preview 2026-06-25；GA 页 2026-07-09 | https://deploymentsafety.openai.com/gpt-5-6 · Preview PDF https://deploymentsafety.openai.com/gpt-5-6-preview/gpt-5-6-preview.pdf | 是（Preview URL 可下；本轮未拉） | 未下载 | Sol/Terra/Luna；**待核实**与 GA 卡是否同一 PDF |
| **Claude Opus 4.5** System Card | 约 2025-11（Anthropic 发布） | https://www.anthropic.com/news/claude-opus-4-5 · PDF https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf | 是 | `https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf` | ASL-3；窗口内 Claude 新卡 |
| **Gemini 3 Pro** Model Card | 约 2025-11 发布；卡更新至 2026-05 | https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf · DeepMind 卡页（3.1）https://deepmind.google/models/model-cards/gemini-3-1-pro/ | 是 | `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` | 模型卡（非完整 TR）；Gemini 3.x 后续卡待扫 |
| **Kimi K2** | arXiv 2025-07-28 | https://arxiv.org/abs/2507.20534 · PDF https://arxiv.org/pdf/2507.20534 · GitHub tech_report.pdf | 是 | `https://arxiv.org/abs/2507.20534` | 开源 agentic MoE（~1T） |
| **GLM-4.5** | arXiv 2025-08-08 | https://arxiv.org/abs/2508.06471 · PDF https://arxiv.org/pdf/2508.06471 | 是 | `https://arxiv.org/abs/2508.06471` | Zhipu ARC；355B MoE |
| **MiniMax-M1** | arXiv 2025-06-16 | https://arxiv.org/abs/2506.13585 · PDF https://arxiv.org/pdf/2506.13585 | 是 | `https://arxiv.org/abs/2506.13585` | Lightning Attention；窗口起算内最早开源之一 |
| **DeepSeek-V3.2** | arXiv 2025-12-02 | https://arxiv.org/abs/2512.02556 · PDF https://arxiv.org/pdf/2512.02556 | 是 | `https://arxiv.org/abs/2512.02556` | DSA + agentic；含 Speciale 变体 |
| **Llama 4** Scout/Maverick | 2025-04-05（**早于窗口**） | Blog https://ai.meta.com/blog/Llama-4-multimodal-intelligence/ · Model Card MD https://github.com/meta-llama/llama-models/blob/main/models/llama4/MODEL_CARD.md · Docs https://dev.meta.ai/llama/docs/model-cards-and-prompt-formats/llama4 | **无** Meta 正式 PDF TR | 未下载 | **重点待核实**：仅有 MD/HF 模型卡与博客，无类似 Llama-3 式 PDF herd report；sekunde.github.io 非官方 |
| Claude Opus/Sonnet **4** System Card | 2025-05-22（略早于窗口） | https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf | 是 | `https://www-cdn.anthropic.com/4263b940cabb546aa0e3283f35b686f4f3b2ff47/Claude_4_System_Card.pdf` | **已有** |
| OpenAI **o3 / o4-mini** System Card | 2025-04-16（早于窗口） | https://cdn.openai.com/pdf/2221c875-02dc-4789-800b-e7758f3722c1/o3-and-o4-mini-system-card.pdf | 是 | 未下载（本清单窗口外） | 对照用；o3-pro 2025-06-10 未见独立完整新卡 |
| DeepSeek-V3 / R1 / Qwen3 / o1 / GPT-4 | （窗口前） | 见对应 TR 深读卡 / 官方 URL | 是 | 已有 | **已有**：`2412.19437-deepseek-v3.pdf`、`2501.12948-deepseek-r1.pdf`、`2505.09388-qwen3.pdf`、`2412.16720-o1-system-card.pdf`、`gpt-4-technical-report.pdf` |

## 已下载（本轮）

相对路径均在 ：

| 文件 | 来源 |
|------|------|
| `https://cdn.openai.com/gpt-5-system-card.pdf` | cdn.openai.com |
| `https://cdn.openai.com/pdf/4173ec8d-1229-47db-96de-06d87147e07e/5_1_system_card.pdf` | cdn.openai.com |
| `https://cdn.openai.com/pdf/3a4153c8-c748-4b71-8e31-aecbde944f8d/oai_5_2_system-card.pdf` | cdn.openai.com |
| `https://arxiv.org/abs/2507.06261` | arXiv:2507.06261 |
| `https://storage.googleapis.com/deepmind-media/Model-Cards/Gemini-3-Pro-Model-Card.pdf` | storage.googleapis.com DeepMind Model-Cards |
| `https://www-cdn.anthropic.com/bf10f64990cfda0ba858290be7b8cc6317685f47/Claude%20Opus%204.5%20System%20Card.pdf` | www-cdn.anthropic.com |
| `https://arxiv.org/abs/2507.20534` | arXiv:2507.20534 |
| `https://arxiv.org/abs/2508.06471` | arXiv:2508.06471 |
| `https://arxiv.org/abs/2506.13585` | arXiv:2506.13585 |
| `https://arxiv.org/abs/2512.02556` | arXiv:2512.02556 |

共 **10** 份新 PDF（GPT-5 系 3 + Gemini 2 + Claude 1 + 开源 4）。

## 待核实清单

1. **Llama 4**：Meta 是否后续放出正式 PDF technical report / herd paper？当前仅 GitHub/HF `MODEL_CARD.md` + 博客（发布 2025-04-05，窗口外；仍列入因任务点名）。
2. **GPT-5.6**：Preview PDF vs 2026-07-09 GA 卡是否分文件；建议 curl `deploymentsafety.openai.com/gpt-5-6` 页面再落盘。
3. **Gemini 3 / 3.1 / 3.x**：除 3 Pro Model Card 外，是否有完整 technical report（类似 2.5 的 arXiv:2507.06261）？DeepMind 卡页 https://deepmind.google/models/model-cards/gemini-3-1-pro/ 待抓 PDF。
4. **Claude Sonnet 4.5 / Opus 4.1–4.x 中间版本**：是否各自独立 system card，还是并入 Opus 4.5？
5. **Kimi K2 Thinking / K3**：DeepSeek-V3.2 文中提及 Kimi-K2-Thinking；是否有独立 TR PDF。
6. **Seed-Thinking / Seed1.5**：arXiv:2504.13914 在窗口前；2025H2–2026 是否有新 Seed 报告。
7. **Grok-4 / xAI**：未见可核对官方 system card PDF（本轮搜索无稳定官方 PDF URL）。
8. **o3-pro（2025-06-10）**：多为博客/产品页；独立 system card PDF 待核实。
9. **Qwen3.5 / Qwen3-Omni 等后续**：有零散 arXiv 线索，需逐条核对发布日与 PDF 后再入库（禁编造）。

## 派发建议（优先级）

| 优先级 | 条目 | 理由 |
|--------|------|------|
| P0 | GPT-5 System Card + Gemini 2.5 TR | 窗口内闭源旗舰正式长文 |
| P0 | Claude Opus 4.5 System Card | 窗口内 Anthropic 最新完整卡 |
| P1 | DeepSeek-V3.2 / Kimi K2 / GLM-4.5 / MiniMax-M1 | 2025H2 开源报告集群 |
| P1 | GPT-5.1 / 5.2 增补卡 | 与 P0 串联读 Preparedness 演变 |
| P2 | Gemini 3 Pro Model Card + GPT-5.6 | 卡较短或需再核实 GA PDF |
| P2 | Llama 4 模型卡（MD） | 无 PDF TR；只作生态对照 |

## 检索备注

- 工具：WebSearch + WebFetch + `curl` 落盘； 校验非空 PDF。
- 非官方二次整理 PDF（如第三方 llama4.pdf）**不入主表可下载列**。
- 时区：Asia/Shanghai（CST）；文档 `as_of: 2026-09-22`。

## 相关笔记

### 技术报告专项
- [[DeepSeekV3训练与MoE基建|TR DeepSeek-V3]]
- [[Qwen3技术报告深读|TR Qwen3]]
- [[DeepSeekR1推理训练深读|TR DeepSeek-R1]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

### 相关深度笔记
- [[混合专家架构|MoE]]
- [[推理时扩展TestTimeScaling|Test-time scaling]]
- [[开源与闭源前沿模型谱系|前沿谱系]]
- [[AI基础设施总览|AI Infra]]

