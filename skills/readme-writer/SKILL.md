---
name: readme-writer
description: >
  为 CoreClaw worker 脚本撰写中英双语 README（README.md + README_CN.md），内容必须基于脚本真实的爬取逻辑、输入输出字段与能力范围，不得编造信息或链接，输入示例完整可跑、输出示例真实。会先生成有区分度的产品化标题与描述（中英各一份）以及用于 SEO 的 meta 标题和 meta 描述，再按既定结构撰写并做整体 SEO 优化。触发词："写脚本 README""生成 worker 文档""bilingual README""写中英文 README"。
---

# README Writer（CoreClaw Worker 脚本文档）

为 CoreClaw worker 脚本撰写双语 README，内容完全基于脚本本身的真实行为。每一条字段、示例、能力说明都可在脚本里找到出处，绝不编造。

## 知识来源（均不依赖本地路径）

- **结构模板**：已提炼进 `references/readme-structure.md`（源自已发布的 Google Maps Scraper 双语 README，含真实示例与 Example 1/2/3 写法）。本 skill 不依赖任何本地文件，他人 clone 即可用。
- **平台官方文档**（链接以下真实 URL，不得编造）：
  - 中文：https://docs.coreclaw.com/zh-cn/ · API https://docs.coreclaw.com/zh-cn/api/
  - 英文：https://docs.coreclaw.com/ · API https://docs.coreclaw.com/api/
  - MCP：https://docs.coreclaw.com/zh-cn/integrations/ai/mcp · EN https://docs.coreclaw.com/integrations/ai/mcp
  - 价格：https://www.coreclaw.com/pricing
  - GitHub 组织：https://github.com/Core-Claw
- **REST API 集成基线**（FAQ "能否当 API 用"必用）：base URL `https://openapi.coreclaw.com`，所有路径以 `/api/v2` 开头，鉴权 `Authorization: Bearer <API_KEY>`（legacy `api-key` header 与 `?token=` query 仍兼容）。典型流程：取 input schema → `POST /api/v2/workers/{workerId}/runs`（input 放在 `input.parameters.custom`，可设 `callback_url`）→ 存 `data.run_slug` → `GET /api/v2/worker-runs/{runId}` 查状态 → `GET /api/v2/worker-runs/{runId}/result` 取结果或 `/result/export` 导出。workerId 支持 slug 或 `owner~name` 路径，version 缺省为 latest。
- **导出格式**：平台支持 8 种——CSV、JSON、JSONL、XLSX、XLS、XML、HTML、RSS。
- **脚本本身**（撰写前必读，是内容唯一真实来源）：`input_schema.json`（字段名/类型/editor/required/default/enum）、`output_schema.json`（每个输出列）、`main.py`/`index.js`（爬取逻辑、硬性上限、增强开关、并发配置）。
- 参考文档：`references/readme-structure.md`、`references/grounding-rules.md`、`references/bilingual-style.md`、`references/seo-and-meta.md`。

## 硬规则（不可妥协）

1. **先读脚本再动笔**。读 `input_schema.json`、`output_schema.json`、`main.py`/`index.js`。每个字段名、类型、default、能力说明都从代码出。
2. **不编造信息**。脚本没有的功能不写；不确定的字段行为就明说或省略，绝不猜。
3. **不编造链接**。只允许：上述平台官方 URL、脚本真实封装的官方上游 API（链接须为稳定官方页）、仓库内资产（`assets/xxx.png`）、仓库内锚点。禁止编造任何 `https://`。
4. **输入示例完整可跑**。须是用户能直接粘贴运行并获得成功的完整 JSON 对象，包含所有必填字段与真实值；数组字段给 2-3 个元素。
5. **输出示例真实**。JSON 数组含一条完整记录，每个键都是 `output_schema.json` 的真实列；值用保留域名（`example.com`、`example-dental.test`）和占位号码（`+1 512-555-0101`），可空字段诚实留空（`email_2: ""`）。
6. **参数说明详细 + 格式举例**。每个输入参数：用途 → 使用建议（推荐/不推荐示例对照）→ 格式规范 → 非平凡格式给 `#### 示例：` 代码块。
7. **中文自然，去翻译腔**。`README_CN.md` 是给中文读者写的，不是机器翻译。
8. **两文件结构对称**。`README.md` 与 `README_CN.md` 章节顺序与层级一致；代码块/JSON/字段名（反引号内）两文件一致，只散文不同。

## 工作流

### Phase 0 — 生成产品化标题、描述、meta（中英各一份）

**在写正文之前，先产出这套元信息**，因为它决定整个 README 的定位与 SEO 基调。

1. **产品化标题**（不一定用脚本原名）。要简短、有区分度、用户友好、含核心关键词与数据对象。参考范式："Instagram Comment By Post URL"、"Google Maps Scraper"、"TikTok Video Scraper By Hashtag"。中英各一份。
   - 英文：`<对象/平台> <动作> <限定维度>` 或 `<平台> <对象> Scraper`，首字母大写。
   - 中文：`<对象> <动作>` 或 `<平台><对象>采集器`，自然流畅。
   - 区分度检查：在 CoreClaw store 里搜这个标题，若与已有 worker 重名则加限定维度（By URL / By Hashtag / By Location）。
2. **简短描述**（一句话，中英各一份）。说清"输入什么 → 输出什么结构化数据 → 核心用途"。≤ 30 字（中文）/ ≤ 160 字符（英文，便于做 meta description）。
3. **meta 标题**（SEO，中英各一份）。用于 docs 站点 `<title>`，≤ 60 字符（英文）。格式：`<产品化标题> | CoreClaw` 或 `<产品化标题> - <次要关键词> | CoreClaw`。
4. **meta 描述**（SEO，中英各一份）。用于 `<meta name="description">`，≤ 155 字符（英文）/ ≤ 80 字（中文）。含主关键词 + 价值点 + 行动暗示，自然通顺不堆词。
5. **关键词清单**（中英各一份，3-8 个）。用于 meta keywords 与正文 SEO 布点。

完整规范与示例见 `references/seo-and-meta.md`。产出后先与用户确认标题方向再进 Phase 1（标题错了正文全错）。

### Phase 1 — 读脚本（grounding）

从实际代码提取：
- **爬取逻辑**：打哪个源、查询形态、单次请求上限、平台硬性上限（如 Google Maps 每区域 120 条上限）。来源 `main.py`/`index.js`。
- **输入字段**：name、type、editor、required、default、enum、description。来源 `input_schema.json`。标出哪些是数组（并发候选）。
- **输出字段**：每个列名 + 类型。来源 `output_schema.json`。
- **能力范围**：有哪些增强开关、各做什么、默认开/关、成本影响。来源主脚本 + schema。
- **导出格式**：CSV/JSON/JSONL/XLSX/XLS/XML/HTML/RSS（平台通用 8 种）。
- **并发配置**（若有）：`concurrency.fields`、`remove_fields`、`limits`、legacy `b`。

填一张 grounding sheet（内联笔记，非交付物）。**有缺口就不进 Phase 2**——每个 README claim 都要能追到此处某行。

### Phase 2 — 套结构

用 `references/readme-structure.md` 的章节顺序。摘要：
1. 标题（Phase 0 的产品化标题）+ 一句话价值定位
2. 能用它做什么（4-6 条场景 bullet，讲用途不讲功能）
3. 提取哪些数据（emoji 两列表，严格映射 output_schema + 能力 bullet）
4. 输入（每字段：用途 + 建议 + 推荐/不推荐示例 + 格式）
5. 输出（表格视图 + 完整 JSON 记录（真实，来自 Phase 1）+ 分维度详解，仅含脚本真实产出的维度）
6. 进阶用法（地理参数等带 Example 1/2/3，仅脚本支持时）
7. FAQ（6-10 条，基于脚本真实限制与集成能力）
8. 反馈

### Phase 3 — 先写英文，再中文自然重写

先完整写 `README.md`（英文）。再写 `README_CN.md` 为**自然中文重写**——同结构、同事实、自然表达（见 `references/bilingual-style.md`）。**不机翻**。真实示例（JSON、格式规范）两文件一致，只散文不同。

### Phase 4 — 对照 grounding 校验

逐条复查：
- README 里每个字段名都在 schema 里？
- 每个"最多 N 条""X 上限"与脚本真实上限一致？
- 每个链接可解析（或为平台官方 URL）？
- 输入示例完整可跑？
- 输出 JSON 列与 `output_schema.json` 完全一致？
- 中文自然无翻译腔？
- meta 标题/描述长度达标、含主关键词？

任何不符 → 改或删，无例外。

### Phase 5 — SEO 优化

整体过一遍 `references/seo-and-meta.md` 的 SEO checklist：标题层级、首屏价值定位、首条可运行命令（如有）、描述性链接文本、图片 alt、代码块语言标注、双语双向链接、导出格式说明等。

## 适用边界

无输入参数、无输出 schema 的 worker → 没有可文档化的内容，写个简短自由格式 README 即可。

## 时效性

结构模板提炼自 2026-07 已发布的 Google Maps Scraper README。平台文档 URL 与 8 种导出格式为平台级稳定信息，但字段语义可能漂移——始终以实际脚本的 schema 为准，不以文档散文为准。
