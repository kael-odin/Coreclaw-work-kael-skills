# Apify actor `.md` 文档结构

每个 Apify actor 页面对应一个 markdown 文档：`https://apify.com/<owner>/<name>.md`。
本文件描述其结构、解析方法、以及实测踩到的坑（2026-08-13 以
`onlyfans-downloader` / `north-carolina-sos-business-search` / `crawler-google-places` 验证）。

## 文档整体结构（自上而下）

1. 头部元信息：标题、作者、分类、统计（`## Pricing` / `## What's an Apify Actor?` / `## How to integrate an Actor?`）
2. `# README`：正文说明，通常含 **Example output / 示例 JSON**、字段说明、FAQ
3. `# Actor input Schema`：**输入字段的渲染段**（本 skill 的输入来源）
4. `## Actor input object example`：示例输入 JSON（含真实字段值/默认值）
5. `# Actor output Schema`：输出段（**多为存储级包装字段，非真实数据列**）
6. `# API`：JS/Python/CLI 调用示例 + OpenAPI 链接（与本 skill 无关）

## `# Actor input Schema` 段的格式

逐字段的标题统一为：

```
## `searchTerms` (type: `array`):

一段描述……
（可多段，直到下一个 `## ` 标题）
```

- 标题格式固定：`` ## `字段名` (type: `类型`): ``，`类型` 为 Apify JSON Schema 类型：
  `string` / `integer` / `number` / `boolean` / `array` / `object`。
- 描述可能含 HTML（`<br>`、`<b>`、`<a>`），解析时剥掉并 `&amp;`/`&quot;` 反转义。
- 描述末尾常跟 `## Actor input object example` JSON 代码块，给出**真实字段值**——
  这是判断 array/object 元素形态、默认值、以及 string 是否枚举的最可靠依据。

## `# Actor output Schema` 段的陷阱

**实测：`north-carolina-sos-business-search` 的 output 段只有 `datasetItems` / `datasetCsv`
两个存储字段；`crawler-google-places` 的 output 段只有 `dataset` / `resultsMap` /
`competitorAnalysis`。这些不是真实的每条数据列，转成 CoreClaw output_schema 没有意义。**

真实输出列在 **README 正文** 的示例输出 JSON 里：

- `north-carolina-sos-business-search`：`### Example output` 下的 JSON 块（25 个字段）。
- `crawler-google-places`：`#### JSON file` 下 "Example of 1 scraped restaurant in New York"
  的 JSON 块（60+ 字段）。
- `onlyfans-downloader`：正文**没有**任何输出字段（是浏览器扩展，非 API actor）→ 输出为空。

### 提取输出的规则

1. 优先找 README 正文里**单条记录形态**的 JSON 代码块（键是业务字段，如 `title`/`address`/
   `totalScore`）。特征：包含字段多、有嵌套对象/数组、不像调用代码。
2. 若正文无示例（如 onlyfans），回退用 `# Actor output Schema` 段的字段；仍无则 `output_schema.json`
   输出空数组 `[]` 并在交付说明里注明"该 actor 无文档化输出"。
3. 嵌套对象/数组字段：保留顶层 key 作为一列，type 用 `object`/`array`，description 里列出
   主要子字段名（如 `location` → `{lat,lng}`）。
4. 示例里 `null` 值不改变列的存在性（列照加），但 null 无法定类型 → 用相邻记录/常识定；
   无法确定时 `string` 并注明。
5. 示例里的 `"..."` 占位值（如 `"sos_id": "..."`）仍是真实字段，保留。

## 必填字段（required）不可用

`.md` **不渲染** Apify INPUT_SCHEMA 顶层的 `required: [...]`。判定规则：
- 描述里明确"must / required / 必须提供 / 不填无法运行" → `required: true`；
- 其余一律 `false`，并在交付说明中注明"required 为推断，源 .md 未声明"。

## 枚举值（enum）不可直接用

`.md` 不渲染 Apify 的 `enum`/`editor`。select 选项只能从描述或示例值推断：

- 描述给出明确取值（如 `searchMatching` "all / any"）→ 转成 `options`；
- 示例 JSON 值能枚举（如 `reviewsSort`）→ 从值推断；
- 描述只说"Define the order…"这类无取值信息 → **不要编造选项**，回退 `input` 编辑器，
  并把"可选值见原 actor 文档"写进 description。

## 其它可用来源（补充，非必需）

- `https://api.apify.com/v2/acts/<owner>~<name>`：返回 actor 元数据（JSON），含
  `exampleRunInput`（示例输入值，可补 default）、`data.description`（商店短描述）、
  `readmeSummary`（长 README 摘要）、**`pictureUrl`（图标直链）**，但**无 inputSchema 字段**。
  `~` 路由可用，`/` 路由与 `/input-schema` 子路径 404。
- **描述来源（2026-08-20 修订）**：商店短描述（营销语）的权威来源是 **`data.description`**，
  实测为短句、与商店页标题下方文案逐字一致（如 mega-downloader-bypass-limit）。缺失时回退
  `.md` 头部 H1 标题行下方、`- **URL**:` 列表之前的第一段（与 `data.description` 同文）。
  **`readmeSummary` 不是描述来源**——它是长 README 摘要（常以 `## 标题` 开头），2026-08-20
  以 6 actor 实测与 `data.description` 内容不同，用它会抓成长摘要（旧规则 9 曾用它，已废止）。
- **图标来源**：`pictureUrl` 是 S3 直链，实测为 PNG 128×128；**仅部分 actor 有**
  （2026-08-14 实测：crawler-google-places 有，onlyfans-downloader / north-carolina-sos-business-search
  无）。无自定义图标的 actor 页面用通用占位图 `https://apify.com/img/store/actor_picture.svg`，
  **不要下载占位图冒充该 actor 的图标**——无 `pictureUrl` 时跳过并注明即可。
- 官方 OpenAPI 定义 URL 在 `.md` 末尾 `## OpenAPI specification` 给出（per-build，随版本变）。

## 2026-08-20 新形态补充（实测 6 actor：mega-downloader-bypass-limit / trustmrr-startup-scraper /
nysed-professional-license-search（已下架） / instagram-comment-bot / tiktok-comments-scraper /
e-commerce-scraping-tool）

- **README 正文可能有重复的字段说明段**：`mega` 有「Input ⌨️ / Fields」表、`e-commerce` 有带
  「Required: Yes」列的搜索参数表。可与 input Schema 段交叉验证，**但字段名可能对不上**
  （e-commerce 表里写 `SearchEngineSearchKeyword`，schema 字段实际叫 `searchEngineKeyword`），
  不能直接按表名匹配；required 推断仍以描述文字为准。
- **部分 actor 完全没有 `# Actor output Schema` 段**（trustmrr）——输出示例只在 README
  （`### Output`）。提取输出的主逻辑不变：先 README 正文，缺段不是异常。
- **README 里可能有多个 JSON 块，需区分「数据集行形状」与「视图/包装结构」**：e-commerce 同时有
  `{product, sellers}` 的 "Output schema" 视图块和 3 条真实行的 "JSON view" 块——后者才是输出列
  来源（标题含 "Example of" / "JSON view" 等字样更可信）。
- **README 的输入示例块可能不止一个且取值冲突**：tiktok 在 canonical `## Actor input object example`
  之前还有 README `### Input` 里的示例（`maxRepliesPerComment: 2` vs API 示例 `0` vs 输入示例缺失）。
  default 取舍优先级：`## Actor input object example` 优先；该字段缺席时按语义取关闭值并注明。
- **README 描述的功能可能超出实际 schema**（instagram：README 提 hashtag 搜索和密码登录，输入段
  只有 `cookies`/`comments`/`post_urls`）——以 `# Actor input Schema` 段为准，README 功能差异
  在交付说明里注明即可。
- **错误记录可能与正常记录混在同一数据集**（tiktok 的 `{url, input, error, errorCode}` 第二记录
  形态）——不并入主输出列，说明里注明。
- **actor 会下架**：nysed-professional-license-search 于 2026-08-20 实测 API 与 `.md` 双 404
  （`{"error":{"type":"record-not-found",...}}` / `{"error":"Missing actor"}`），但搜索引擎仍缓存其
  子页面。下架 actor 不要用缓存页臆造字段，按规则 1 报告不可用并跳过。
