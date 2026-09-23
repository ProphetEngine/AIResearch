---
topic: TR-Mistral-3
date: 2026-09-22
status: archived
archived: 2026-09-22
---

# Mistral 3 / Large 3｜公告级短卡（P2）

## 一句话
Mistral AI 于 **2025-12-02** 发布 Mistral 3：包含面向边缘/本地的 Ministral 3（3B/8B/14B）与旗舰 **Mistral Large 3**；全系公告称采用 Apache 2.0。

## 发布要点（以官方公告为准）
- **Large 3**：稀疏 MoE，**41B active / 675B total**；从零训练于 3,000 张 NVIDIA H200；支持图像理解与多语言对话。公告发布 base 与 instruction-tuned 两版，并称 reasoning 版本将后续推出。
- **Ministral 3**：3B/8B/14B，各有 base、instruct、reasoning 版本，具图像理解能力；公告定位为 edge/local 高性价比系列。
- 公告还提到 Large 3 的 NVFP4 checkpoint，可用 vLLM 部署于单个 8×A100 或 8×H100 节点；此处不延伸为通用部署保证。

## Tech report / PDF 核验（检索范围：2025-06 至 2026-09-22）
- **有 PDF，但只对应 Ministral 3，不是 Large 3 的 standalone tech report**：官方公告末尾链接 `Ministral 3` 研究论文，arXiv v1 日期为 **2026-01-13**。
 - 摘要：3B/8B/14B × base/instruct/reasoning 共 9 个 dense 模型；提出 **Cascade Distillation**（迭代 prune → distill → repeat），从 Mistral Small 3.1 派生；支持视觉，最长 256k context（reasoning 版 128k），Apache 2.0。
 - 略读要点：报告称训练量约 1–3T tokens；14B Base 在部分基准接近 Mistral Small 3.1 Base，同时参数少逾 40%；架构为 decoder-only Transformer + GQA，视觉编码器为冻结的 410M ViT。以上均为论文自报结果。
- **Large 3 tech report：截至上述日期未在官方公告/模型文档中发现独立 PDF**；Large 3 的短卡内容因此只采用官方公告与官方模型文档，任何更深训练/评测细节标为**待核实**。

## 官方来源
1. Mistral AI 公告（2025-12-02）：<https://mistral.ai/news/mistral-3/>
2. Mistral Large 3 官方模型文档（2025-12-02）：<https://docs.mistral.ai/models/mistral-large-3-25-12>
3. 公告直链研究论文摘要：<https://arxiv.org/abs/2601.08584>
4. PDF：<https://arxiv.org/pdf/2601.08584>

## 本地材料
- PDF：`https://arxiv.org/abs/2601.08584`

## 相关笔记

### 技术报告专项
- [[Grok4ModelCard|TR Grok 4 Model Cards]]
- [[Kimik15技术报告深读|TR Kimi k1.5]]
- [[KimiK2技术报告深读|TR Kimi K2]]
- [[Llama4待核实备忘|TR Llama 4 待核实备忘]]
- [[Mistral3公告短卡|TR Mistral / Ministral-3]]
- [[SystemCard与TR扫描2025至2026|TR 扫描 2025-06→2026-09]]

