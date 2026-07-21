# README 结构 — Worker 模板

提炼自已发布的 CoreClaw Google Maps Scraper 双语 README。这是 worker README 的标准章节顺序，`README.md`（英文）与 `README_CN.md`（中文）都按此顺序。

> 本文件是模板的唯一载体——本 skill 不依赖任何本地文件，他人 clone 即可用。

## 章节顺序与用途

### 1. `## 📍 什么是 X？` — 价值定位

一段话：把什么公开数据一键转化为结构化数据、核心用途、与手动方式对比。结尾点出相对官方 API 的差异点（如"突破 Google Places API 限制""绕过每区域 120 条上限"）。差异点须基于脚本真实能力，不编造。

### 2. `### 您可以用它做什么？` — 场景 bullet

4-6 条，每条是**用途**（收益）而非功能。范式：`**<动作>：** <能做什么>，<为什么重要>。` 例：生成潜在客户名单、分析竞争对手、洞察市场机会、发掘合作对象、自动化调研流程。

### 3. `## X 会提取哪些数据？` — 字段表 + 能力

**emoji 两列表**列出每个输出字段，严格映射 `output_schema.json`。随后一段"为最大化采集效果，X 提供以下能力"的 bullet：地点与联系数据、可直接导出的格式（8 种）、集成能力（webhook、MCP）、可选增强项。

这张表是数据卖点——每一列都必须存在于 `output_schema.json`。

### 4. `## ⬇️ 输入` — 逐参数文档

每个参数一个 `###` 子节。格式：
- **标题**：`### <标签>（必填/选填）-- <field_name>`
- **用途**：1-2 句该字段控制什么。
- **使用建议**：什么输入好、什么坏。tiktok_2 的"推荐示例 vs 不推荐示例"对照是黄金范式——用对比教学。
- **格式规范**：具体格式（如"城市 + 国家"，或 Circle/Polygon JSON 形状）。有 enum 则列出取值。
- **`#### 示例：`** 代码块，用于非平凡格式。

必填参数在前。每个标（必填）或（选填）。

#### 输入子节示例范式（对照写）

```
### 搜索词（必填）—— keyword

用于定义抓取的商家类型或服务类别，支持输入多个关键词以扩大覆盖范围。

建议使用含义不同、重叠度低的业务关键词组合，以提升数据覆盖效果并控制运行时间。

避免使用同义词重复或无筛选意义的词（如 near me、best），这些不会增加数据，只会增加重复查询。

推荐示例：

marketing agency, SEO agency, web design company, consulting firm, IT services, recruitment agency

不推荐示例：

marketing agency, marketing agencies, digital marketing agency, SEO agency near me, best SEO agency, web design company NYC
```

### 5. `## ⬆️ 输出` — 表格视图 + 真实 JSON + 分维度

- **表格视图**：描述 UI 表格（总览、按字段分组/筛选）。有截图则放仓库内资产（`![view.png](assets/view.png)`），不编造图片 URL。
- **`### 🧩 完整 JSON 记录`**：一个**真实** JSON 数组，含一条完整记录。每个键都是 `output_schema.json` 的列；值用保留域名（`example-dental.test`）和占位号（`+1 512-555-0101`），可空字段诚实留空（`email_2: ""`、`email_2_status: ""`）。这是 README 里被复制最多的块，必须字段精确、可跑。
- **分维度详解**（`### 📇 联系方式与拓展`、`### 📧 邮箱验证`、`### 📱 社交平台数据`、`### ⭐ 评分与评论`、`### 🧾 商家详情`）：**仅包含脚本真实产出的维度**。每个展开 JSON 记录中相关子集。

### 6. `## 📍📡 用地理参数实现更精准定位`（仅脚本支持时）

只有脚本支持进阶参数（地理参数、自定义区域等）时才写。每个给 `#### 示例 1：圆形区域`、`#### 示例 2：多边形区域`、`#### 示例 3：多个多边形区域` 编号的具体示例，含完整 JSON。脚本无此类参数则整节省略。

#### 自定义区域 Example 范式（GeoJSON，[经度, 纬度] 序）

```
#### 示例 1：圆形区域

用于在某个坐标周围固定半径内搜索。

​```jsonc
{
  "type": "Circle",
  "center": { "lng": 13.405, "lat": 52.520 },
  "radiusKm": 1
}
​```

#### 示例 2：多边形区域

用于街区、园区、商圈等不规则区域。首尾坐标必须相同以闭合边界。

​```jsonc
{
  "type": "Polygon",
  "coordinates": [[
    [13.388, 52.519],
    [13.410, 52.519],
    [13.410, 52.530],
    [13.388, 52.530],
    [13.388, 52.519]
  ]]
}
​```
```

注意：`custom_geojson` 坐标遵循 GeoJSON 标准 `[经度, 纬度]` 顺序；从 Google Maps URL `@纬度,经度` 复制要反序。

#### 搜索区域优先级（若脚本支持多方式）

```
custom_geojson > postal_code + country > base_location > country/state/city/county
```

### 7. `## ❓ 常见问题` — 基于真实限制的 Q&A

6-10 条，每条答案基于脚本真实行为，非营销话术。标准集（按脚本裁剪）：
- X 是如何工作的？（讲清运行时流程）
- 官方 API 有哪些缺点？（仅当脚本封装了某官方 API）
- 可以从多个位置采集吗？（多 run 或工作流）
- 如何提高采集速度？（引用真实 concurrency.fields 行为、max_results、增强开关关闭）
- 可以提取评论吗？（若有 fetch_reviews）
- 如何让每条评论单独占一行？（若支持）
- 可以与其他应用集成吗？（导出 8 格式 + webhook/MCP/n8n/REST API）
- 可以当作 API 使用吗？（见下方 API 集成答法范式）
- 采集 X 数据合法吗？（通用、非指示性）

#### "可以当作 API 使用吗"答法范式（真实链接与流程）

```
可以。使用 CoreClaw REST API 以编程方式运行 X。
base URL 为 https://openapi.coreclaw.com，所有路径以 /api/v2 开头，
鉴权用 Authorization: Bearer YOUR_API_KEY（legacy api-key header 与 ?token= query 仍兼容）。

典型流程：
1. GET /api/v2/workers/{workerId}/input-schema 取输入 schema（或 GET /api/v2/workers/{workerId} 取完整详情）。
   workerId 为 slug 或 owner~name 路径，version 缺省为 latest。
2. POST /api/v2/workers/{workerId}/runs 启动运行，传 is_async，
   scraper 输入放在 input.parameters.custom。可设 callback_url 接收回调免轮询。
3. 保存返回的 data.run_slug。
4. GET /api/v2/worker-runs/{runId} 查状态（用 run_slug 作 {runId}）。
5. GET /api/v2/worker-runs/{runId}/result 取结果，或 /result/export 导出文件。
```

> 这段基于 CoreClaw 官方 API 文档，链接真实。不要在别处编造 API 路径或 base URL。

### 8. `## 反馈` — 收尾

一两句邀请反馈。如有官方支持邮箱 `support@coreclaw.com` 可写（真实）。除非仓库真有 issue tracker 且你知道 URL，否则不编造 issue 链接。

## 反模式（看到就删）

- 用实现语言列功能（"用了 Playwright、asyncio"）——读者要用途不要技术栈。
- "状态：WIP"不说明哪些可用。
- 输入示例残缺（`{"keyword": "..."}` 缺其它必填）——不可跑。
- 输出 JSON 桩（`{"title": "...", "phone": "..."`）省略真实列——隐藏字段集。
- 编造图片 URL / demo 链接。
- 中文标题与英文结构不对应（破坏锚点对称）。
