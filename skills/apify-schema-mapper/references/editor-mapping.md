# Apify → CoreClaw 类型 & 编辑器映射决策表

Apify 的 `.md` 只给「字段名 + JSON 类型 + 描述 + 示例值」，不给 Apify editor/enum/required。
映射规则以「类型 + 描述 + 示例值形态」三要素决定 CoreClaw 的 type 与 editor。

## 1. 类型映射（1:1）

| Apify type | CoreClaw type |
|------------|---------------|
| `string` | `string` |
| `integer` | `integer` |
| `number` | `number` |
| `boolean` | `boolean` |
| `array` | `array` |
| `object` | `object` |

## 2. 编辑器映射（CoreClaw 只允许 12 种）

决策按类型分支，判断优先级从高到低：

### string
| 条件 | editor | 备注 |
|------|--------|------|
| 描述/示例含明确枚举取值（如 "all / any"、"newest/oldest"） | `select` | options 来自描述，不得编造；拿不准用 `input` |
| 语义是**严格日期**（"date / starting from / newer than"，示例值形如 `2024-05-03`，不接受相对日期） | `datepicker` | 补 `"format":"DD/MM/YYYY","valueFormat":"DD/MM/YYYY"` |
| 语义是日期但**接受相对/部分日期**（"8 days"、"3 months"、"newer than"） | `input` | datepicker 无法表达相对日期，回退 input，description 写明两种格式均可 |
| 内容是 JSON/凭据/长文本（`sessionJson`、cookies、`customGeolocation`） | `textarea` | 描述提示"JSON / paste / 长" |
| 其余 | `input` | 单行文本 |

### integer / number → `number`
例外：值为纯 on/off 的 integer（罕见）仍 `number`。

### boolean → `switch`

### array —— 看示例值元素形态（最可靠）：
| 元素形态 | editor | 备注 |
|----------|--------|------|
| 元素全是字符串且数量可变、无固定取值（关键词/搜索词/公司名） | `stringList` | 如 `searchTerms`、`categoryFilterWords` |
| 元素是 `{url}` 或含 url 的对象，URL 是主键 | `requestList` | 如 `startUrls` |
| 元素是 `{url,...}` 且带附加参数（method/headers/num_of_posts） | `requestListSource` | 需给 `param_list`（至少 url 参数） |
| 元素是固定少数可选值（如 `data_sections` 的 reviews/address/phone） | `checkbox` | options 来自描述/示例 |
| 无法判定元素形态 | `stringList` | 保守回退，注明 |

### object → `json`
`default: {}`。description 里说明期望结构（如 GeoJSON、`{facebooks,instagrams,...}` 布尔集）。
CoreClaw 没有嵌套字段编辑器，`json` 是最接近 Apify object 的形态。

## 3. required 判定（.md 不提供，推断）

- 描述明确 must/required/必须/不填无法 → `true`。
- 其余 `false`，交付说明注明是推断值。

## 4. 实测样例（2026-08-13）

| 字段（来源 actor） | Apify type | 示例值形态 | 映射 |
|---------------------|-----------|-----------|------|
| `searchTerms`（nc） | array | `["Red Hat Inc", "Lowe's..."]` | stringList |
| `sessionJson`（nc） | string | `""`（JSON 凭据） | textarea |
| `requestDelaySeconds`（nc） | number | `1.5` | number |
| `includeProfiles`（nc） | boolean | `true` | switch |
| `searchStringsArray`（gp） | array | `["restaurant"]` | stringList |
| `startUrls`（gp） | array | `[{"url":"...maps..."}]` | requestList |
| `scrapeSocialMediaProfiles`（gp） | object | `{"facebooks":false,...}` | json |
| `reviewsStartDate`（gp） | string | `2024-01-01`，也接受 "8 days" | input（接受相对日期，datepicker 无法表达） |
| `reviewsOrigin`（gp） | string | "all"/"google"（描述给出） | select |
| `searchMatching`（gp） | string | "all"/"any"（描述给出） | select |
| `listingNotice`（of） | string | 说明文字 | input（info 型字段） |

## 5. 交付说明（每个链接都要给）

生成文件后，附一段简短说明，包含：
- 字段总数、哪些用了 select/checkbox 及 options 来源；
- required 均为推断（.md 未声明）；
- 该 actor 输出是否为空、输出列取自正文示例还是 output Schema 段；
- 若原 actor 输入有互斥 array（如 startUrls/searchStringsArray），建议 concurrency 的配置。
