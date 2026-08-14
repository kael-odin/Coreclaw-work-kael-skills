---
name: apify-schema-mapper
description: >
  将 Apify actor 链接转换为 CoreClaw worker 的 schema 文件。给定一个或多个 Apify actor 链接（如 https://apify.com/compass/crawler-google-places），自动拉取对应的 .md 文档（https://apify.com/<owner>/<name>.md），提取脚本输入与输出字段，生成 CoreClaw 兼容的 input_schema.json 与 output_schema.json——字段名与 Apify 源 1:1 保留，类型映射到 CoreClaw 的 6 种，编辑器必须映射到 CoreClaw 支持的 12 种；并从 Apify API 下载 actor 图标落盘。触发词："Apify 转 CoreClaw""生成 input_schema""生成 output_schema""apify schema 转换""按 apify 链接生成 worker schema""下载 actor 图标"。
---

# Apify → CoreClaw Schema Mapper

把一个或多个 Apify actor 链接转成 CoreClaw worker 能直接用的 `input_schema.json` 与
`output_schema.json`，并把 actor 图标下载落盘。输出字段名与 Apify 源一致（不翻译不改名），
编辑器/类型严格限定在 CoreClaw 支持集合内，并在回复里附一份「映射说明」交代推断与限制
（交付物只有两个 schema 文件 + 图标文件（若有），`.md` 与说明均不落盘）。

## 知识来源

- **CoreClaw schema 权威格式**：官方文档 `developer-guide/worker-definition/input-schema.md`
  与 `output-schema.md`（12 种编辑器、6 种类型、properties/output 结构）——
  提炼在 `references/coreclaw-schema-format.md`。不依赖本地路径，别人 clone 即可用。
- **Apify `.md` 文档结构**：每个 actor 页对应 `https://apify.com/<owner>/<name>.md`。
  2026-08-13 以 onlyfans-downloader / north-carolina-sos-business-search / crawler-google-places
  实测确认结构与陷阱——见 `references/apify-md-structure.md`。
- **映射决策表**：`references/editor-mapping.md`（含实测映射样例）。

## 输入

- 一个或多个 Apify actor 链接，形如 `https://apify.com/<owner>/<name>`。
- 可选：输出目录（默认当前目录下 `apify-schema-output/<owner>-<name>/`）。

## 硬规则（不可妥协）

1. **字段名 1:1 保留**。Apify 的 camelCase 字段名原样进 CoreClaw schema，不翻译、不重命名、
   不增删（输出列同样）。
2. **编辑器只允许 12 种**：`input` `textarea` `number` `select` `radio` `checkbox` `switch`
   `datepicker` `requestList` `requestListSource` `stringList` `json`。
3. **类型只允许 6 种**：`string` `integer` `number` `boolean` `array` `object`。
4. **不编造选项**。`select`/`checkbox` 的 `options` 只能来自 `.md` 描述或示例值；
   描述给不出明确取值 → 回退 `input`（string）或 `stringList`（array），并把可选值线索写进 description。
5. **输出字段**：有文档化输出时，取 README 正文示例输出 JSON 的真字段，不是
   `# Actor output Schema` 段（那段往往是 `dataset`/`resultsMap` 存储包装）。正文无示例 →
   回退 output 段；仍无 → **按 actor 用途合理拟定输出列**（不必留空数组 `[]`），并在说明里
   注明「输出为拟定值，源 .md 无文档化输出」。
6. **required 是推断值**。`.md` 不声明 required：描述明确"must/required/必须"才 `true`，
   其余 `false`，交付说明里注明。
7. **每个链接都要给映射说明**（在回复里给出，不落盘为文件）。字段总数、select/checkbox 的
   options 来源、required 推断、输出来源（含"无文档化输出→拟定"标注）、concurrency 建议。
8. **图标取 API `pictureUrl`**。调用 `https://api.apify.com/v2/acts/<owner>~<name>`，取
   `data.pictureUrl`（S3 直链）下载为 `<输出目录>/icon.<扩展名>`（扩展名按 URL 或
   Content-Type 定，实测为 PNG 128×128）。**无 `pictureUrl`**（actor 未上传自定义图标）→
   不生成图标文件，在回复里注明「无自定义图标（Apify 页面用通用占位图
   `actor_picture.svg`）」；不下载通用占位图冒充该 actor 的图标。

## 工作流

### Phase 1 — 解析链接，拉取 `.md` 与 actor 元数据

- 从输入链接正则提取 `owner` 与 `name`：`https://apify.com/<owner>/<name>`。
- 抓取 `https://apify.com/<owner>/<name>.md`（`WebFetch` 或 `curl -sL`），解析完即弃、**不落盘**。
- 抓取 actor 元数据 `https://api.apify.com/v2/acts/<owner>~<name>`，记录 `data.pictureUrl`
  （图标直链；注意 `~` 路由可用，`/` 路由与 `/input-schema` 子路径 404）。此接口还提供
  `exampleRunInput`（可补 default）与 `readmeSummary`，但**无 inputSchema 字段**。
- 若 `.md` 抓取失败（404/超时），明确报告该链接不可用并跳过，不臆造字段。

### Phase 2 — 提取输入字段

- 定位 `# Actor input Schema` 段（到 `# API` 前为止）。
- 逐字段解析 `## \`字段名\` (type: \`类型\`):` 标题后的描述段（剥 HTML、反转义）。
- 解析 `## Actor input object example` JSON，取每个字段的**示例值**（用于判断 array/object
  元素形态、默认值、string 枚举）。
- 每个字段记录：`name`、`apify_type`、`description`（清洗后）、`example_value`。

### Phase 3 — 提取输出字段

- 在 README 正文找「单条记录形态」的 JSON 代码块（标题常含 Example output / JSON file /
  Example of 1 scraped …）。
- 取该 JSON 的**顶层 key 集合**为输出列；按示例值定每列 type。
- 嵌套对象/数组：顶层 key 作一列，type `object`/`array`，description 列主要子字段。
- `null` 值不影响列存在；无法定类型的列给 `string` 并在说明里注明。
- 输出列的 description 用一句话说明该字段含义（可用原文描述精炼）。
- **README 正文与 output 段都无示例输出** → 按 actor 用途（README 介绍/行为描述）拟定一组合理
  输出列，类型给基本类型（多为 `string`），并在说明里标注「输出为拟定值，源 .md 无文档化输出」。

### Phase 4 — 类型 & 编辑器映射

按 `references/editor-mapping.md` 决策表：

- type 1:1 映射（string/integer/number/boolean/array/object）。
- editor 按「type + 描述 + 示例值形态」定：
  - string → `select`（有明确枚举）/ `datepicker`（日期）/ `textarea`（JSON·凭据·长文）/ `input`（默认）
  - integer、number → `number`；boolean → `switch`；object → `json`（default `{}`）
  - array → `stringList`（字符串列表）/ `requestList`（url 对象）/ `requestListSource`
    （url + 附加参数，给 `param_list`）/ `checkbox`（固定少数选项）
- 字段语义是"最大结果数"的，命名为 `max_results`（平台约定）。

### Phase 5 — 生成文件 + 映射说明

- 每个 actor 建 `apify-schema-output/<owner>-<name>/`，写两个文件：
  - `input_schema.json`：`{description, properties:[…]}`。每个 property 含
    `title`（用 Apify 字段名的可读形式）、`name`（原字段名）、`type`、`editor`、
    `description`、`required`、**`default`（必须有）**；select/checkbox 补 `options`；
    datepicker 补 `format`/`valueFormat`；requestListSource 补 `param_list`。
  - `output_schema.json`：`[{name, type, description}, …]`，顺序按示例输出 JSON 的键序。
- **schema 文件全英文**：`input_schema.json` 的顶层 `description`、每个 property 的
  `title`/`description`，以及 `output_schema.json` 的每列 `description` 一律用英文
  （schema 直接渲染在 CoreClaw 平台表单上，面向终端用户；字段 `name` 本就 1:1 保留英文）。
  映射说明（回复里给出）可用中文。
- **每个输入 property 都必须有 `default`**：初始值，JSON 类型与 `type` 一致（string→`"..."`、
  integer/number→数字、boolean→`true/false`、array→`[...]`、object→`{...}`），值符合字段语义。
  优先取自 `.md` 的 `Actor input object example`；「关闭/禁用」语义的字段用 `false`/`0`/`""`/`[]`/`{}`
  表示，不编造具体值（如 `sessionJson` 默认 `""`、`maxReviews` 默认 `0`）。
- 若存在互斥的 array 输入（如 startUrls / searchStringsArray），在 `input_schema.json`
  加 `concurrency.fields`（取主输入字段），并在说明里解释任务拆分语义。
- **交付物是 `input_schema.json` + `output_schema.json` + 图标文件（若有）**（`.md`、映射说明
  等均不落盘）。映射说明在回复里给出：字段数、select/checkbox 来源、required 推断声明、
  输出来源（含"拟定"标注）、图标下载结果（有/无 pictureUrl）、concurrency 说明、已知限制。
- **下载图标**：Phase 1 记录的 `pictureUrl` 有值 → `curl -sL <pictureUrl> -o <输出目录>/icon.<ext>`，
  扩展名按 URL 后缀或 `Content-Type` 定（`.png`/`.webp`/`.jpg`/`.svg` 均可）；下载后用文件头校验
  是图片（PNG 开头 `\x89PNG`）。无 `pictureUrl` → 不生成图标文件，回复里注明。
- **收尾自查**：① 编辑器全部落在 12 种内；② 类型全部落在 6 种内；③ 输入字段名与 `.md` 源
  逐一比对无遗漏无改名；输出列若有源示例则同样比对，无源示例（拟定输出）则复核列名合理、
  无重复、类型正确；④ 每个输入 property 都有 `default` 且其 JSON 类型与 `type` 一致
  （array 元素形态合理）；⑤ JSON 用 `python -m json.tool` 或等价方式校验可解析。

## 已固化的样例（references/examples/）

- `onlyfans-downloader`：单 info 字段输入，无文档化输出 → 输出按用途拟定（5 个下载记录列）；
  无自定义图标（API 无 `pictureUrl`）。
- `north-carolina-sos-business-search`：11 输入（stringList/switch/number/textarea），
  25 输出列（取 README `Example output`）；无自定义图标（API 无 `pictureUrl`）。
- `crawler-google-places`：39 输入（stringList/requestList/switch/number/select/json/input，
  含 13 个布尔开关；`reviewsStartDate` 接受相对日期故用 input 而非 datepicker），
  68 输出列（取 README `JSON file` 示例）；有图标 → `icon.png`（128×128，下载自 `pictureUrl`）。

新增 actor 时若发现 `.md` 结构与上述样例不同，把新形态补进
`references/apify-md-structure.md`，保持本 skill 的解析规则可持续演化。
