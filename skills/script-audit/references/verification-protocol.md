# 验证协议 — 经 API/MCP 实跑输入输出

静态规则保证 schema 合规。不能保证平台接受真实输入值，或输出正确。这是 L2 + L3 实跑验证层的协议。

> 本 skill 不依赖本地路径。clone `Core-Claw/coreclaw-cli` 到任意位置即可用其审核脚本；MCP/API 调用走平台公网。

## L2 — 实跑验证输入

目标：确认平台接受真实输入，拒绝时抓真实 `code`/`message`。这是支撑任何 `error` severity claim 的探针（结构性原因除外）。

### 前置检查：待审核版本不可经 API/MCP 实跑

**关键约束（2026-07-21 实测）**：待审核版本（刚更新待上传审核，或新创建待上传审核）**无法经 API/MCP 运行**。实测 worker `01KPD6M5YVHWCNQCRK3FTA6PBC` v1.0.4（待审核）：

- `get_worker` / `get_worker_input_schema` → **能返回**待审核版本的完整信息、schema、parameters（读接口可见）
- `run_worker` → **返回 `50001 worker does not exist`**（写接口被拒，仿佛 worker 不存在）
- `list_store_workers` → store 列表里**搜不到**该 worker（未发布，store 不可见）

即：读接口看得到，写接口跑不了，store 不可见。三者组合 = 待审核版本。

**推论**：本层（L2 实跑验证）只对**已发布上架**的 worker 版本有效。对待审核版本，L2 跳过实跑，改走 UI 提交试运行（scraper-webui 的"测试运行"入口），或在 SKILL.md 报告里标 `[VERIFY] 受审核版本限制，须 UI 试跑`。不要把"API 报 50001"误记为 worker 本身的 `error`——这是版本状态而非脚本缺陷。

### 构造探针输入

1. `get_worker_input_schema` — 重读 live schema。绝不凭记忆或 worker README 造字段名，live schema 为准。
2. 构造最小 `input_json`，每次只测一个字段。最小 = 能产出非空结果的最小输入。Google Maps worker：一个关键词 + 一个小城市，不是 500 关键词跨 50 城。
3. 并发拆分 worker，测单元素数组（最小）和双元素数组（确认拆分产两个任务而非一个）。

### 经 MCP 运行（优先）

```
run_worker(worker_id, input_json, is_async=true)  → run_id
get_worker_run(run_id)                            → status, code, message
get_worker_run_log(run_id)                        → 失败时看真实错误
```

MCP 已含分页补偿与 `/last` 新鲜度修复；裸 REST 没有。

### REST 兜底

```
POST https://openapi.coreclaw.com/api/v2/workers/{worker_id}/runs
Authorization: Bearer <token>
Content-Type: application/json
{"input": {...}}        # 顶层 input，不包（v2 runWorker）
```
等后 `GET /api/v2/workers/{worker_id}/runs/{run_id}`。契约见平台 API 文档，operationId `runWorker`、`getWorkerRun`。

**鉴权陷阱**：v2 无 `api-key` header。只有 Bearer header 或 `?token=` query。v2 调用用 `api-key` 静默未鉴权 → `error`。

### 探针产物

记录探针结果，让 `error` claim 后续可审计：

```
examples/verify-<topic>/
  README.md      # 输入、预期、实际：平台接受/拒绝、真实 code+message、日期
  input.json     # 提交的精确输入
  result.json    # 抓取的响应（status, code, message, result_count）
```

状态标记：`⏳ 待验证` → `✅ Resolved`（接受）或 `⚠️ 实测推翻`（推翻假设）。已闭环探针留作回归 artifact。

### 探针后 severity 判定

- 平台硬拒（非 0 `code`、HTTP 4xx/5xx、不运行）→ `error`。
- 平台接受但表单/运行异常（如 checkbox 选项选不中）→ `warn`。
- 平台接受且干净运行 → 非发现，或仅 `info`。
- 无探针 → `[VERIFY]`，绝不 `[ERROR]`。

## L3 — 输出正确性

目标：运行成功，但输出对吗？schema 校验抓不到 `phone` 装了 URL、或 `rating` 是字符串。

### 抽样结果

```
list_worker_run_results(run_id, limit=20)   # 预览行
export_worker_run_results(run_id, format='json')  # 签名 download_url 做 full diff
```

8 种导出格式：**CSV、JSON、JSONL、XLSX、XLS、XML、HTML、RSS**。

### 检查矩阵

| 检查 | 验什么 | 失败例 |
|------|--------|--------|
| 字段存在 | output_schema 每列在行里 | schema 有 `email`，行里从不出现 |
| 字段正确 | 抽 3-5 行对照源页 | `phone` 装网站 URL；`rating` 是字符串非数字 |
| shape vs schema | schema `array<string>` vs 行值 | schema 说数组，行里逗号分隔字符串 |
| 跨拆分去重 | concurrency.fields 任务间无重复行 | 同一地点从两个拆分任务出现两次 |
| 无漏行 | 行数 vs 预期（注意 1 基 offset 陷阱） | offset 当行偏移用导致漏页 |
| CAPTCHA/403 行 | 错误行不被误判成功 | 403 HTML body 被当"结果"行收 |

最后一条优先用 `verify_run`——它返回结构化判定（`PASS`/`NO_DATA`/`FAILED`/`ERROR_RECORD`/`RUNNING`/`SUBMIT_FAIL`），防 CAPTCHA 或 403 行被误读成成功 PASS。

### 正确性发现是 `error`

与平台拒绝不同，正确性 bug 不需要上传探针——错误输出就是证据。但引用展示它的行：`[ERROR] L3: phone 字段第 3 行装了网站 URL。来源: verify_run 抽样 2026-07-21 [result.json:row3]`。

## 时效性

协议反映 2026-07-21 的 v2 API + MCP server 行为。MCP server 的分页补偿与 `/last` 新鲜度修复已就位；裸 REST 调用仍需手动把 `offset` 对齐到 `limit` 倍数。
