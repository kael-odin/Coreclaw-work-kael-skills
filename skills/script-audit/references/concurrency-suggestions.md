# 并发建议 — 改进层

CoreClaw worker 最富矿的改进方向。来源：`coreclaw-cli-audit/references/concurrency-rules.md`（2026-07 平台 HTML）。本文件把规则转成审核建议。

> 规则集从 `Core-Claw/coreclaw-cli` 仓库同步，本 skill 不依赖本地路径。

## 决策顺序（平台运行时）

```
1. concurrency.fields 非空  → 按 fields 拆（新规则）
2. 否则 b 非空              → 按 b 拆（legacy）
3. 否则                      → 整个 custom 对象 = 单任务
4. 两者都在                  → fields 优先，b 被忽略
```

有数组输入但**无** `concurrency.fields` 且**无** `b` 的 worker 按**单任务**跑——整个输入串行。这是吞吐损失之首。

## 建议矩阵

### S-THROUGHPUT — 数组输入无 concurrency.fields

**检测**：`input_schema.json` 的 `properties` 有 `type: "array"` 字段，代表独立工作单元列表（keywords、place_ids、google_maps_urls、search_terms），且 `concurrency.fields` 缺省或空。

**影响**：高。平台无法并行；一个任务串行做所有事。加 `concurrency.fields: ["keywords"]` 让平台把 N 个关键词拆成 N 个并行任务。

**建议**：
```json
"concurrency": {
  "fields": ["keywords"]
}
```
每个 `keywords` 元素变独立任务。primitive 项生成的任务保留 `"keywords": ["pizza"]`（单元素数组）。

**来源**：concurrency-rules.md §决策顺序、§拆分结果形状。

### S-COST — 预扣费爆炸无 limits

**检测**：某拆分字段每项可能产大量可计费结果（如 `google_maps_urls` 列表每个 URL 可能返回数百地点），且 `concurrency.limits` 缺省。

**影响**：高成本。预扣费 = 各项计费数之和，无封顶。500 URL × 每个返回 200 = 10 万预扣。

**建议**：加 `limits` 规则封顶每项预扣。`limits` 不改任务数或任务内容——只封顶每项预扣（计费）数。
```json
"concurrency": {
  "fields": ["google_maps_urls"],
  "limits": [
    { "field": "google_maps_urls", "max": 120 }
  ]
}
```
每项预扣封顶 120。`regex` 选填（递归匹配 item 值，不匹配 key）；缺省 = 匹配该字段每一项无条件下。多个 limit 匹配同一项 → 最小 `max` 胜。

**来源**：concurrency-rules.md §limits。

### S-LEGACY — 仍用 `b` 拆分

**检测**：`input_schema.json` 有 `b`（legacy）且无 `concurrency.fields`。

**影响**：中。`b` 仅兼容；`concurrency.fields` 存在时优先。新 worker 应用 `fields`。

**建议**：`b` → `concurrency.fields` 迁移。单字段拆分语义等价（`fields` 下 primitive 项保留字段名为单元素数组，是新形状）。

**来源**：concurrency-rules.md §决策顺序、§拆分结果形状。

### S-REMOVE — 拆分字段泄漏到下游 custom

**检测**：某拆分字段值是内部（ID、内部 token），不应出现在下游任务 custom，但 `concurrency.remove_fields` 缺省。

**影响**：中低。无 `remove_fields` 时，全字段回退路径激活，被禁用字段保留为 `[""]` 在生成的任务 custom 里。

**建议**：
```json
"concurrency": {
  "fields": ["keywords", "place_ids"],
  "remove_fields": ["place_ids"]
}
```
当首选字段（`fields - remove_fields`）激活且有有效值时，每个 `remove_fields` 键从生成的任务 custom **删除**（非保留为 `[""]`）。

**注意**：`remove_fields` 仅在首选字段激活时应用。全字段回退路径激活（首选空或全空）时**不应用** `remove_fields`，那些字段可能参与拆分。

**来源**：concurrency-rules.md §活跃字段选择。

### S-MIXED — 拆分字段对象/primitive 混用

**检测**：某 `concurrency.fields` 条目的数组混了对象和 primitive。

**影响**：`error`（运行时）。`field [X] must not mix object and primitive items`。

**建议**：拆成两字段，或全部归一为一种类型。对象项把键并入任务 custom；primitive 项包成单元素数组——两者不能在同一字段共存。

**来源**：concurrency-rules.md §元素类型矩阵。

### S-NESTED — 拆分项是嵌套数组

**检测**：某 `concurrency.fields` 数组含嵌套数组。

**影响**：`error`（运行时）。`item at index N in [X] must be an object or primitive value`。

**建议**：扁平化，或把每个内层数组包成对象。

**来源**：concurrency-rules.md §元素类型矩阵。

## 字段选择规则（用于 schema 校验发现）

这些是 `error`/`warn` 发现，非建议，但列此以求完整：

- 每个非空 `concurrency.fields` 条目须匹配一个 `properties[*].name`。
- 每个 `concurrency.fields` 属性须 `type: "array"`。
- 每个非空 `concurrency.remove_fields` 条目须是 `concurrency.fields` 成员。
- `limits.field` 须是 `concurrency.fields` 成员（它是并发字段，非 `max_results` 那种计费字段）。
- 对象项不得含与并发字段名相等的键 → `item at index N in [X] must not override concurrency field`。

## 分页语义（P2）— 与并发无关但咬结果正确性

**2026-07-23 实测复核**（run `01KY6QQKPAAQS6DGQ6RD7JWDE8`，100 行结果）：

- `offset` 是**从 0 开始的行偏移**，不是页码。`offset=0,limit=5` 返回第 1-5 行；`offset=5,limit=5` 返回第 6-10 行；`offset=10,limit=5` 返回第 11-15 行。因此 `offset += limit` 是**正确的**翻页方式，不会跳行/漏行。
- `page_index` 只是响应里的**一基显示页号** = `floor(offset/limit) + 1`（如 `offset=3,limit=5` → page_index=1；`offset=5,limit=3` → page_index=2）。它不是请求参数，也不是行偏移。
- `offset` 不需要对齐到 `limit` 的倍数：`offset=3,limit=5` 合法，返回第 4-8 行。

**真正的陷阱**是把 `page_index`（一基页号）当成请求参数去翻页，或把 `offset` 当成页号（传 `offset=1` 想取第一页，实际取到第 2 行起）。翻页用 `offset += limit`，以响应的 `count` 和返回行数判断是否到尾。

MCP server 的分页补偿层与上述语义一致；裸 REST 直接按 `offset += limit` 翻页即可。若并发拆分 worker 跨任务出现重复或漏行，查每任务是否误把 `page_index` 当翻页参数，或是否对 `offset` 做了页号假设。

来源：memory `[[coreclaw-pagination-bug-fix-2026-07-15]]`，2026-07-23 实测复核修正了此前对 page_index 语义的误述。
