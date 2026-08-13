# CoreClaw Schema 权威格式

来源：CoreClaw 官方文档 `developer-guide/worker-definition/input-schema.md` 与 `output-schema.md`
（https://docs.coreclaw.com/ 开发指南 · Worker 定义），以及官方 Python-Worker-Demo 的 `input_schema.json`。

## input_schema.json

顶层结构：

```json
{
  "description": "脚本用途说明（展示在表单顶部，可长）",
  "concurrency": { "fields": ["startUrls"] },        // 可选：任务拆分
  "properties": [
    { "title": "字段标签", "name": "startUrl", "type": "string",
      "editor": "input", "description": "帮助文案", "required": true,
      "default": "...", "options": [...] }
  ]
}
```

### properties 元素字段

| 字段 | 必填 | 说明 |
|------|------|------|
| `title` | 是 | 表单显示的字段标签 |
| `name` | 是 | 内部字段名，脚本用它读值，须唯一，匹配 `^[A-Za-z_][A-Za-z0-9_]*$` |
| `type` | 是 | 数据类型（下表） |
| `editor` | 是 | 表单控件（下表） |
| `description` | 是 | 字段下方帮助文案 |
| `required` | 是 | true=不填不能启动 |
| `default` | 否 | 初始值，须与 type 一致 |
| `options` | 否 | `checkbox`/`select`/`radio` 的选项数组 `[{label,value}]` |
| `param_list` | 否 | `requestListSource` 每条 URL 的附加参数定义 |
| `format`/`valueFormat` | 否 | `datepicker` 的日期格式（如 `DD/MM/YYYY`） |
| `sectionCaption`/`sectionDescription` | 否 | 分组标题/说明 |

### 支持的 type（6 种）

`string`、`integer`、`number`、`boolean`、`array`、`object`。

### 支持的 editor（12 种，唯一权威清单）

`input`、`textarea`、`number`、`select`、`radio`、`checkbox`、`switch`、
`datepicker`、`requestList`、`requestListSource`、`stringList`、`json`。

**推荐配对**（来自官方文档）：

| editor | type | 用途 |
|--------|------|------|
| `input` | string/integer/number | 单行文本、简单数字 |
| `textarea` | string | 多行文本 |
| `number` | integer/number | 数字输入 |
| `switch` | boolean | 开/关 |
| `checkbox` | array | 多选 |
| `select` | string/integer | 单选下拉 |
| `radio` | string/integer | 单选组 |
| `stringList` | array | 字符串列表 |
| `requestList` | array | URL/请求对象列表（default 可是 `[{"url":...}]` 或 `["str"]`） |
| `requestListSource` | array | 带附加参数的 URL 列表（需 `param_list`） |
| `json` | object | 结构化 JSON 编辑（default 用 `{}`） |
| `datepicker` | string | 日期选择 |

### concurrency（任务拆分，可选）

`concurrency.fields` 是候选拆分字段名列表，每个须对应 `properties[*].name` 且 type 为
`array`。可选 `remove_fields` 子集。**有多个互斥 array 输入（如 startUrls / searchTerms）
时建议配置**；否则整个输入作为单任务。若配置，注意：
- 数组项只能是「对象」或「原始值」的其中一种，不能混；
- 空数组字段会被过滤当作无值；
- 有值数组拆成任务时，每个任务该项只留一条，其它并发字段置 `[""]`，`remove_fields` 字段整个移除。

## output_schema.json

顶层为**数组**，每个元素一列：

```json
[
  { "name": "title", "type": "string", "description": "标题" }
]
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | 是 | 列标识，须与脚本 `push_data` 的 key 完全一致，唯一 |
| `type` | 是 | `string`/`number`/`integer`/`boolean`/`array`/`object` |
| `description` | 否 | 列头标签/说明 |

要点：
- `name` 必须匹配脚本 `push_data` 的 key；用 `upsert_data` 时唯一键列必须在 output_schema 里。
- 官方建议以 `output_schema.json` 为输出结构的主定义（运行时 `set_table_header` 只是程序化定义）。

## 平台侧字段命名约定

- 若 worker 接受"最大结果数"参数，用 `max_results` 作字段名（平台约定，下游集成识别）。
