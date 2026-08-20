---
name: apify-schema-mapper
description: >
  将 Apify actor 链接转换为 CoreClaw worker 并发布上线。给定一个或多个 Apify actor 链接（如 https://apify.com/compass/crawler-google-places），自动拉取对应的 .md 文档（https://apify.com/<owner>/<name>.md），提取脚本输入与输出字段，生成 CoreClaw 兼容的 input_schema.json 与 output_schema.json——字段名与 Apify 源 1:1 保留，类型映射到 CoreClaw 的 6 种，编辑器必须映射到 CoreClaw 支持的 12 种；并从 Apify API 下载 actor 图标与商店短描述（营销语）落盘，description.txt 含脚本名（URL 末段去连字符）；然后组装 worker zip（内置模板，不依赖本地文件）并通过 CoreClaw API 创建 worker、上传图标、发布版本（需 CORECLAW_API_KEY 与 CORECLAW_CONSOLE_COOKIE）。触发词："Apify 转 CoreClaw""生成 input_schema""生成 output_schema""apify schema 转换""按 apify 链接生成 worker schema""下载 actor 图标""下载 actor 描述""发布到 coreclaw""创建 coreclaw worker""apify 链接上线"。
---

# Apify → CoreClaw Schema Mapper & Publisher

把一个或多个 Apify actor 链接转成 CoreClaw worker：生成 `input_schema.json` 与
`output_schema.json`，下载 actor 图标与短描述（商店营销语），组装 worker zip 并
**发布到 CoreClaw 平台**。输出字段名与 Apify 源一致（不翻译不改名），编辑器/类型严格限定在
CoreClaw 支持集合内，并在回复里附一份「映射说明」交代推断与限制（交付物：两个 schema 文件 +
图标文件（若有）+ 描述文件 + worker zip；`.md`、映射说明等中间物不落盘）。

## 知识来源

- **CoreClaw schema 权威格式**：官方文档 `developer-guide/worker-definition/input-schema.md`
  与 `output-schema.md`（12 种编辑器、6 种类型、properties/output 结构）——
  提炼在 `references/coreclaw-schema-format.md`。不依赖本地路径，别人 clone 即可用。
- **Apify `.md` 文档结构**：每个 actor 页对应 `https://apify.com/<owner>/<name>.md`。
  2026-08-13 以 onlyfans-downloader / north-carolina-sos-business-search / crawler-google-places
  实测确认结构与陷阱——见 `references/apify-md-structure.md`。
- **映射决策表**：`references/editor-mapping.md`（含实测映射样例）。
- **CoreClaw 发布流程**：接口、字段格式与全部坑见 `references/coreclaw-publish.md`
  （2026-08-20 实测跑通）。

## 输入

- 一个或多个 Apify actor 链接，形如 `https://apify.com/<owner>/<name>`。
- 可选：输出目录（默认当前目录下 `apify-schema-output/<owner>-<name>/`）。
- 发布凭证：环境变量 `CORECLAW_API_KEY` + `CORECLAW_CONSOLE_COOKIE`（见「凭证」节），
  缺失时向用户索取。

## 凭证（发布必需，不落盘、不硬编码）

- `CORECLAW_API_KEY`：公开 API（openapi.coreclaw.com/api/v2）Bearer 凭证，
  形如 `scraper_api_...`，console 设置页生成。
- `CORECLAW_CONSOLE_COOKIE`：console 会话 Cookie 头（consoleapi.coreclaw.com/api），
  关键是 `x-coreclaw-t` JWT；从登录后的 Chrome DevTools → Network → 请求 Cookie 头复制。
- **cookie 有有效期**（JWT exp，约 1 个月），过期后向用户重新索取。
- 不把凭证写进任何交付文件、日志或 skill 文件。

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
   options 来源、required 推断、输出来源（含"无文档化输出→拟定"标注）、concurrency 建议、
   发布结果（worker path / 版本 / 图标 URL / 验证结果）。
8. **图标取 API `pictureUrl`**。调用 `https://api.apify.com/v2/acts/<owner>~<name>`，取
   `data.pictureUrl`（S3 直链）下载为 `<输出目录>/icon.<扩展名>`（扩展名按 URL 或
   Content-Type 定，实测为 PNG 128×128）。**无 `pictureUrl`**（actor 未上传自定义图标）→
   **用脚本生成字母图标**：纯色背景 + 脚本名首字母（如 `T`）的简单 PNG（可用 Python PIL
   或纯 Python 写 PNG；若环境无 PIL 则生成 SVG 转 PNG 或直接生成最小合法 PNG），
   命名为 `icon.png`，并在回复里注明「无自定义图标，已生成字母图标」。
9. **描述是第 4 个交付物**。每个 actor 生成 `<输出目录>/description.txt`，固定两段：
   **第 1 行是脚本名**——取链接 URL 路由最后一段 `<name>`，去掉全部 `-` 连字符
   （如 `mega-downloader-bypass-limit` → `mega downloader bypass limit`）；
   **空一行后是商店短描述**（营销语，英文原文，不翻译不改写）。**不落盘 `.md` 全文**。
   - 短描述来源优先级：① API 元数据的 `data.description`（商店页标题下方营销语的权威来源，
     实测为短句，如 "Download MEGA files and folders fast, …"）；
     ② 缺失/为空 → 取 `.md` 头部：H1 标题行下方、`- **URL**:` 列表之前的第一段
     （剥 HTML/反转义/去 markdown 标记）；
     ③ 两者皆无 → 写占位说明「No description available for this actor.」并在回复里注明「无可用描述」。
   - **不要用 `data.readmeSummary` 作描述**：那是长 README 摘要（常以 `## 标题` 开头），
     不是商店页的短营销语（2026-08-20 实测二者内容不同，用它会抓成长摘要）。
   - 描述文件用英文原文（与商店一致，不翻译、不改写）。
10. **发布时的 description 必须 ASCII**：multipart 上传给 CoreClaw 的 `description` 字段
    若含 em-dash（`—`，U+2014）会报 `11000 Operation failed. Try again.`（实测）——
    发布前把 `—` 换成 ASCII `-`（其它非 ASCII 字符保守处理）。本地 `description.txt`
    保留原文。
11. **zip 每次发布内容必须变化**：zip 内置 `version.txt` 标记文件（如 `v1.0.1-2`），
    每次发布前更新其内容；包不变报 `11000 Script package is unchanged`。

## 工作流

### Phase 1 — 解析链接，拉取 `.md` 与 actor 元数据

- 从输入链接正则提取 `owner` 与 `name`：`https://apify.com/<owner>/<name>`。
- 抓取 `https://apify.com/<owner>/<name>.md`（`WebFetch` 或 `curl -sL`），解析完即弃、**不落盘**。
- 抓取 actor 元数据 `https://api.apify.com/v2/acts/<owner>~<name>`，记录 `data.pictureUrl`
  （图标直链）与 `data.description`（**商店短描述**，供 description.txt 用；`data.readmeSummary`
  是长 README 摘要，**不要**用作描述来源。注意 `~` 路由可用，`/` 路由与 `/input-schema`
  子路径 404）。此接口还提供 `exampleRunInput`（可补 default），但**无 inputSchema 字段**。
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

### Phase 5 — 生成文件

- 每个 actor 建 `apify-schema-output/<owner>-<name>/`，写三个文件：
  - `input_schema.json`：`{description, properties:[…]}`。每个 property 含
    `title`（用 Apify 字段名的可读形式）、`name`（原字段名）、`type`、`editor`、
    `description`、`required`、**`default`（必须有）**；select/checkbox 补 `options`；
    datepicker 补 `format`/`valueFormat`；requestListSource 补 `param_list`。
  - `output_schema.json`：`[{name, type, description}, …]`，顺序按示例输出 JSON 的键序。
  - `description.txt`：**第 1 行脚本名**（URL 末段 `name` 去 `-` 转空格，如
    `mega-downloader-bypass-limit` → `mega downloader bypass limit`），空一行后接商店短描述
    （内容取 Phase 1 记录的 `data.description`；缺失时按规则 9 的回退链路取 `.md` 头部简介段，
    仍无则写占位说明并注明）。
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
- **下载/生成图标**：Phase 1 记录的 `pictureUrl` 有值 → `curl -sL <pictureUrl> -o <输出目录>/icon.<ext>`，
  扩展名按 URL 后缀或 `Content-Type` 定（`.png`/`.webp`/`.jpg`/`.svg` 均可）；下载后用文件头校验
  是图片（PNG 开头 `\x89PNG`）。无 `pictureUrl` → 按规则 8 生成字母图标 `icon.png`。
- **收尾自查**：① 编辑器全部落在 12 种内；② 类型全部落在 6 种内；③ 输入字段名与 `.md` 源
  逐一比对无遗漏无改名；输出列若有源示例则同样比对，无源示例（拟定输出）则复核列名合理、
  无重复、类型正确；④ 每个输入 property 都有 `default` 且其 JSON 类型与 `type` 一致
  （array 元素形态合理）；⑤ JSON 用 `python -m json.tool` 或等价方式校验可解析；
  ⑥ `<输出目录>/description.txt` 已生成：第 1 行为脚本名、正文非空（或为占位说明）。

### Phase 6 — 发布到 CoreClaw（可选，默认执行；无凭证则跳过并注明）

按 `references/coreclaw-publish.md` 的接口与坑执行，顺序：

1. **凭证**：读 `CORECLAW_API_KEY` / `CORECLAW_CONSOLE_COOKIE` 环境变量；缺失则向用户索取。
2. **组装 zip**（输出目录内 `<name>.zip`，**根级平铺**）：
   `references/worker-template/` 的全部文件 + `input_schema.json` + `output_schema.json` +
   `description.txt` + `icon.<ext>` + `version.txt`（内容 = 版本标记，每次发布前更新，
   如 `v1.0.1`、`v1.0.1-2`……）。
3. **上传图标**：`POST https://consoleapi.coreclaw.com/api/common/upload`（Cookie，
   multipart `file=@icon.<ext>`）→ `data.file_path`（OSS URL）。
4. **创建 worker**：先 `GET https://openapi.coreclaw.com/api/v2/workers/{owner}~{name}`
   （Bearer）判存在；不存在 → `POST https://consoleapi.coreclaw.com/api/actors/create`
   （Cookie，multipart：`title`=脚本名、`description`=短描述（**ASCII，规则 10**）、
   `categories=56`（单值，规则见文档）、`icon`=OSS URL、`scraper_file`=zip）→ `data.slug`。
5. **更新版本**：`GET .../workers/{owner}~{name}` 读 `data.version` →
   `PUT .../workers/{owner}~{name}/versions/{version}`（Bearer，multipart 同 create 字段，
   每次带**变化后**的 zip）。刚创建的 worker 不能 POST 新建版本（`50003`），用 PUT。
6. **验证**：`GET .../workers/{owner}~{name}/input-schema`（Public）确认表单字段；
   `GET .../workers/{owner}~{name}/internal`（Public）确认 title/description/categories/version。
7. 映射说明里汇报：worker path（`owner/name`）、slug、版本号、图标 OSS URL、验证结果。

## 已固化的样例（references/examples/）

- `onlyfans-downloader`：单 info 字段输入，无文档化输出 → 输出按用途拟定（5 个下载记录列）；
  无自定义图标（API 无 `pictureUrl`）；源 actor 已不在商店公开可查，`description.txt` 示例为
  占位说明（脚本名 + No description available）。
- `north-carolina-sos-business-search`：11 输入（stringList/switch/number/textarea），
  25 输出列（取 README `Example output`）；无自定义图标（API 无 `pictureUrl`）；源 actor
  已不在商店公开可查，仅保留 schema 样例（无 description.txt）。
- `crawler-google-places`：39 输入（stringList/requestList/switch/number/select/json/input，
  含 13 个布尔开关；`reviewsStartDate` 接受相对日期故用 input 而非 datepicker），
  68 输出列（取 README `JSON file` 示例）；有图标 → `icon.png`（128×128，下载自 `pictureUrl`）。
- `trustmrr-startup-scraper`（2026-08-20 端到端发布跑通）：8 输入 / 20 输出，发布为
  `scraper/trustmrr-startup-scraper`（categories 56、图标走 OSS、em-dash 转 ASCII）。

上表为 schema 格式参考；按规则 9，**每次正式 run 都会额外生成 `description.txt`**（已固化的
`crawler-google-places` / `onlyfans-downloader` 样例目录已含 `description.txt` 示意——第 1 行
脚本名（URL 末段去连字符）+ 商店短描述，后者源已下架故为占位说明；`north-carolina-sos-business-search`
源 actor 已不在商店公开可查，故仅保留 schema 样例）。

新增 actor 时若发现 `.md` 结构与上述样例不同，把新形态补进
`references/apify-md-structure.md`，保持本 skill 的解析规则可持续演化。
