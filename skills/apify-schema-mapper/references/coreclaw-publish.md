# CoreClaw 发布流程（实测 2026-08-20，scraper 账号）

把 apify-schema-mapper 的产物（schema/图标/描述/zip）发布为 CoreClaw worker 的完整链路。
全部接口与坑均以实测为准（trustmrr-startup-scraper 端到端跑通）。

## 0. 凭证（不落盘、不进 skill 文件）

| 凭证 | 用途 | 获取方式 |
|------|------|---------|
| `CORECLAW_API_KEY` | 公开 API（openapi.coreclaw.com/api/v2）Bearer | console 设置页生成，形如 `scraper_api_...` |
| `CORECLAW_CONSOLE_COOKIE` | console 会话（consoleapi.coreclaw.com/api）Cookie 头 | 登录 console 后 F12 → Network → 任意请求的 Cookie 头（关键是 `x-coreclaw-t` JWT） |

运行时优先读环境变量，否则向用户索取。**cookie 有有效期**（JWT 的 exp 字段，约 1 个月），过期需用户重新提供。

## 1. 构建 zip（根级平铺，重要）

zip 内所有文件**平铺在根级**（平台按根级解压，有子目录会找不到 main.py）：

```
main.py  sdk.py  sdk_pb2.py  sdk_pb2_grpc.py  requirements.txt  README.md  README_CN.md
input_schema.json  output_schema.json  description.txt  icon.<ext>  version.txt
```

- 模板文件取自本 skill 的 `references/worker-template/`（**不依赖本地路径**）。
- `version.txt`：每次发布前**必须改内容**（如 `v1.0.1-2`、时间戳），服务端校验「脚本包必须变化」，
  包不变报 `11000 Script package is unchanged`。
- `description.txt`/`icon` 为归档与展示用，平台不解析。
- 模板 `main.py` 是占位实现（快速失败测试桩，恒 exit 1）——结构与平台对接正确，
  **正式功能需替换为真实逻辑**（读 `CoreSDK.Parameter.get_input_json_dict()`，写
  `CoreSDK.Result.push_data` 等）。

## 2. 上传图标（仅当有 icon 文件）

```
POST https://consoleapi.coreclaw.com/api/common/upload     # Cookie: $CORECLAW_CONSOLE_COOKIE
multipart: file=@icon.<ext>
→ {"code":0,"data":{"file_path":"https://oss.coreclaw.com/scraper/<date>/<id>.png"}}
```

- 返回的 `file_path` 即 icon 的 OSS URL，后续所有 `icon` 字段用它。
- **icon 字段只认 `oss.coreclaw.com` 的 URL**：外部 URL（Apify S3 等）报
  `11000 Operation failed. Try again.`。

## 3. 创建 worker（若不存在）

```
POST https://consoleapi.coreclaw.com/api/actors/create     # Cookie: $CORECLAW_CONSOLE_COOKIE
multipart:
  title=脚本名（URL 末段去连字符，如 "trustmrr startup scraper"）
  description=商店短描述（data.description，**必须 ASCII**，见坑 1）
  categories=56（**单值**，见坑 2）
  icon=<OSS URL>（可选）
  scraper_file=@<name>.zip
→ {"code":0,"data":{"slug":"01M0..."}}
```

- 公开 API（openapi.coreclaw.com/api/v2）**没有创建接口**；`POST .../versions` 对不存在
  worker 返回 `11004 not found`，不隐式创建。
- worker 已存在（`GET /api/v2/workers/{owner}~{name}` 返回 200）→ 跳过本步直接走 4。
- 前端路由表里还有 `createVersion:/actors/version/create`、`versionPublish` 等，但
  create 一步到位（含 zip）即可，无需再走 createVersion。

## 4. 更新版本（公开 API）

```
GET  https://openapi.coreclaw.com/api/v2/workers/{owner}~{name}        # 读 data.version（如 v1.0.1）
PUT  https://openapi.coreclaw.com/api/v2/workers/{owner}~{name}/versions/{version}   # Bearer: $CORECLAW_API_KEY
multipart: title / description（ASCII）/ categories=56 / icon=<OSS URL> / scraper_file=@<name>.zip
→ {"code":0,"message":"success"}
```

- 刚创建的 worker **不能 POST 新建版本**：报 `50003 the worker version is not available`，
  只能 PUT 更新当前版本（v1.0.1）。
- PUT 是全量表单（title/description/categories/icon/scraper_file 都要带）。

## 5. 验证

```
GET https://openapi.coreclaw.com/api/v2/workers/{owner}~{name}/input-schema   # Public，输入表单字段
GET https://openapi.coreclaw.com/api/v2/workers/{owner}~{name}/internal       # Public，title/description/categories/version
```

- `input-schema` 返回 zip 里 input_schema.json 解析出的 properties（检查字段/编辑器/默认值齐全）。
- `internal` 的 `data.description` 是服务端权威值（页面展示可能滞后，见坑 5）。

## 坑清单（全部实测）

1. **description 含 em-dash（—，U+2014）→ `11000 Operation failed. Try again.`**
   发布前把 `—` 换成 ASCII `-`（其它 Unicode 字符未验证，保守全 ASCII）。
2. **categories 用单值** `56`；JSON 数组 `[56]` → 422/`102 invalid integer`。
3. **zip 内容必须变化**（version.txt 标记）；不变 → `11000 Script package is unchanged`。
4. **icon 只认 OSS URL**（先 common/upload 再引用）；外部 URL 报 Operation failed。
5. **页面展示信息与版本可能不同步**：`internal` 接口是服务端权威（实测 PUT 后 internal
   立即返回新值），console 页面顶部显示旧 description/无图标可能是前端缓存或平台的
   展示信息机制（i18n 有 "Worker display info won't update automatically" 文案）。
   确认数据以 `internal`/`input-schema` 为准；页面强制刷新（Ctrl+Shift+R）仍旧则
   在页面编辑保存一次触发同步。
6. **console API 部分接口上游故障**（`103 Network error, try again.`，如
   `version/list`、`version/detail`、`version/info_update`、`actors/save`、
   `version/create`）——这类接口当前不可用，不要依赖；用 create + PUT versions 组合即可。
7. **workerId 格式**：公开 API 用 `owner~name`（`/` 路由 404；纯 name 404）。
8. 公开 API 偶发全站 502（网关故障，15-25 分钟自愈）——重试即可。
9. **【重要】页面展示字段只在 create 时写入**：console 页面顶部读 `actors/detail`
   的 `icon`/`description`（console 侧数据），公开 API 的 PUT versions 更新的是
   **另一份**数据（`internal`/`input-schema` 接口可见），互不影响。所以：
   - **create 时必须一次传全展示字段**（完整 description + OSS icon），否则之后
     补改没有可用 API（info_update/save 等全部 103，2026-08-20 实测），只能页面
     手动编辑或等平台修复。
   - 验证页面展示用 `POST consoleapi.coreclaw.com/api/actors/detail`（body
     `{"slug":"..."}`，返回 `data.detail.icon/description/title`）；验证版本数据用
     公开 API 的 `internal`/`input-schema`。两个都过才算发布完成。

## 关键路径速查

- 公开 API base：`https://openapi.coreclaw.com/api/v2`（Bearer/QueryToken）
- console API base：`https://consoleapi.coreclaw.com/api`（Cookie 会话）
- 图标 OSS：`https://oss.coreclaw.com/...`（common/upload 返回）
