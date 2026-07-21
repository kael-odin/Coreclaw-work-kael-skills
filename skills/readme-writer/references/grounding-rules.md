# Grounding 规则 — 不编造

README 必须忠实描述实际脚本。这些规则把"不编造"变成可操作条款。

## 规则 1 — 先读再写

动笔前必读：
- `input_schema.json` — 字段名、类型、editor、required、default、enum
- `output_schema.json` — 每个输出列
- `main.py` / `index.js` — 爬取逻辑、硬性上限、增强开关、并发配置
- 已有的部分 README（若有）——只取可验证事实，丢弃无法从代码确认的声明

任何文件缺失或不可读 → 停下并说明，不要凭假设写。

## 规则 2 — 字段名忠实

README 里每个字段名（输入或输出）必须与 schema JSON 逐字一致。大小写敏感。schema 里是 `place_categories`，README 里就必须是 `place_categories`，不能写成 `placeCategories` 或 `Place Categories`。

正文里可用反引号包裹 `place_categories`；JSON 示例里用精确键名。

## 规则 3 — 能力 claim 须引代码

任何"每个 URL 最多 300 条""突破 120 条上限"之类 claim，必须能追到脚本某行或平台文档。脚本没设上限就别编一个。平台硬性上限若有文档依据，引用文档并照抄数字。

不确定就诚实模糊："支持大量类别"，而不是编造"支持最多 100 个类别"——除非脚本或文档真说了 100。

## 规则 4 — 链接：真实或没有

**允许**的链接：
- 平台官方 URL（SKILL.md Sources 里列出的）
- 脚本真实封装的官方上游 API，且链接为稳定官方页（如 Google Places API 文档、Google 服务条款页）
- 仓库内资产（`![view](assets/view.png)`）
- 仓库内锚点（相对 `#section`）

**禁止**：
- 编造的 `https://example.org/some-page`（未验证可解析）
- demo/playground URL（除非仓库真部署了一个且你知道地址）
- issue tracker 链接（除非仓库开了 issue 且你知道 URL）
- OSS 图片 URL（除非是真实存在的 CoreClaw 资产路径）

要占位就别加链接。裸描述好过坏 URL。

## 规则 5 — 输入示例完整可跑

输入示例是用户能直接粘贴到运行输入并获得成功运行的完整 JSON 对象。须含：
- 所有必填字段，带真实值
- 选填字段在需要展示格式时给出
- 精确嵌套（顶层 vs 在 `input` 下 vs 在 `parameters.custom` 下——匹配平台真实运行形态）

平台 v2 运行接口：`POST /api/v2/workers/{workerId}/runs`，scraper 输入放在 `input.parameters.custom`。README 的"输入示例"展示给用户看的是 `input.parameters.custom` 的内容（或等价的 schema 视图），要标注清楚层级。

绝不显示残缺片段如 `{"keyword": "pizza"}`（若脚本还要求 `base_location`）。两者都要给。数组字段给 2-3 个元素，格式无歧义。

## 规则 6 — 输出示例真实

输出 JSON 示例必须：
- 是数组（平台返回结果行为数组）
- 含 `output_schema.json` 的每个列作为键
- 用真实值：保留域名（`example.com`、`example-dental.test`）、占位电话（`+1 512-555-0101`）、合理数字（`review_count: 842`，不要 `999999`）
- 诚实展示可空字段（`email_2: ""`、`email_2_status: ""`）——别裁掉，它们教会用户预期什么

这是 worker README 里被复制最多的块。写错意味着每个下游用户的解析器都会坏。

## 规则 7 — 增强开关与脚本一致

脚本有增强开关（联系信息增强、邮箱验证、评论等）时，逐个文档化：default（开/关）、成本（免费增强 vs 运行时成本）、返回什么。不编脚本没有的开关，也不漏脚本有的开关。

## 规则 8 — 诚实能力范围

该说脚本不能做什么时就说。基于代码说明"不支持历史热门时段""评论每地上限 N 条"。诚实能防 support 工单和差评。

## Grounding sheet 模板

动笔前填这张（内联笔记，非交付物）：

```
爬取逻辑: <打哪个源、查询形态、单次请求上限、平台硬性上限>
输入字段:
  - name: keyword, type: string, editor: text, required: 是, default: "", enum: []
  - name: base_location, type: string, ...
  - name: place_categories, type: array, ...
输出字段: <每个 output_schema 列 + 类型>
增强开关:
  - name: <开关>, default: on, cost: 免费/运行时, returns: <字段>
并发: fields=[], remove_fields=[], limits=[], legacy_b=
硬性上限: <如每区域 120 条、每 URL 300 条> — 来源: <代码行或文档>
```

README 每个 claim 都应能追到这张表某行。
