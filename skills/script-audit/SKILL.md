---
name: script-audit
description: >
  端到端审核一个 CoreClaw worker 脚本：静态规则（error/warn）、通过 API 或 MCP 实跑验证输入与输出、输出结果正确性、以及具体改进建议（含 concurrency.fields 并发调优以提升吞吐/控成本）。规则集源自 Core-Claw/coreclaw-cli 的审计 skill 并保持同步。适用于上传前或运行异常后审核任意 CoreClaw worker。触发词："审核 worker""审核脚本""check this worker""is this upload-safe""why did this run fail""improve concurrency""改进并发"。
---

# Script Audit（CoreClaw Worker 脚本审核）

对一个 CoreClaw worker 脚本做五层审核，按严重度排列发现，每条附来源指针。第 1 层静态规则集**已从 `Core-Claw/coreclaw-cli` 的 audit skill 100% 独立吸收**为本 skill 内置引擎（137 条规则 R001-R337，见 `references/contract-checklist.md`），不重新发明。第 2-4 层是本 skill 独有的扩展：输入输出实跑 API/MCP 验证、输出正确性、改进建议（并发、吞吐、成本）。

## 知识来源（均不依赖本地路径）

- **内置规则引擎**（第 1 层静态规则的来源，已 100% 吸收）：
  原源自 `Core-Claw/coreclaw-cli` 的 `skills/coreclaw-cli-audit/`，现完整并入本 skill：
  - `references/contract-checklist.md` — 137 条规则清单 R001-R337，每条带验证状态 + severity + 出处（input-schema / output-schema / project-structure / sdk-modules / platform-features / concurrency-rules / API v2 契约）
  - `references/known-gaps.md` — 已解决 + 待查缺口，含完整修复历史与平台实测探针结果（code 4000 推翻、unsupported editor 升 error、concurrency 非数组降 warn 等）
  - `references/concurrency-rules.md` — 平台任务拆分规则事实（决策顺序、活跃字段选择、元素类型矩阵、limits 预扣费算法）
  - `scripts/diff-contract.cjs` — 自动比对脚本（validation 调用统计 + checklist 覆盖率 + API operationId 覆盖率）
  这些是审核时的规则权威，引用规则码（如 R211 Camoufox playwright pin、R212 upsert key、R215 硬编码代理凭证）。
- **权威契约源**（规则集本身的依据，审核分歧时以这里为准）：
  GitHub 仓库 `Core-Claw/scraper-webui-docs` → `src/content/docs/developer-guide/`（英文）与 `src/content/docs/zh-cn/developer-guide/`（中文）。线上即 https://docs.coreclaw.com/developer-guide 与 https://docs.coreclaw.com/zh-cn/developer-guide 。规则集持续从此提炼，后续可基于此仓库 + 更多内容优化本 skill。
- **平台官方文档**：
  - 中文：https://docs.coreclaw.com/zh-cn/ · API https://docs.coreclaw.com/zh-cn/api/
  - 英文：https://docs.coreclaw.com/ · API https://docs.coreclaw.com/api/
  - MCP：https://docs.coreclaw.com/zh-cn/integrations/ai/mcp · EN https://docs.coreclaw.com/integrations/ai/mcp
  - 价格：https://www.coreclaw.com/pricing
- **上游 API 契约**：平台 API 文档（https://docs.coreclaw.com/api/）的 OpenAPI 契约，37 个 operation，全部 `/api/v2`，Bearer 鉴权。base URL `https://openapi.coreclaw.com`。
- 本 skill 其它参考文档：`references/verification-protocol.md`（第 2-3 层实跑协议）、`references/concurrency-suggestions.md`（第 4 层改进建议）、`references/sync-procedure.md`（与上游同步流程）

## 审核对象

一个 CoreClaw worker 项目，通常含：
- `input_schema.json` — 输入字段、editor、类型、并发配置
- `output_schema.json` — 输出列
- `main.py` / `index.js` — 采集逻辑
- `README.md` / `README_CN.md` — 输入文档（与实际字段交叉校验）

## 五层审核

### 第 1 层 — 静态规则（error / warn）

用内置规则集核对。两种方式：
- **手工核对**：逐条对照 `references/contract-checklist.md` 的 R001-R337 与 worker 的 schema/代码。
- **自动核对**（worker 已打包时）：clone `Core-Claw/coreclaw-cli` 到任意目录，跑其 validator 与本 skill 吸收的 diff-contract 脚本。

**不在本 skill 重定义规则**——引用规则码 R###。severity 政策见 `references/known-gaps.md` 末尾「Severity Guidelines」与 `contract-checklist.md` 每行的括注。

severity 要点（基于开发者契约 + 已实测行为）：
- `error` = 平台上传/运行时硬拒、表单不渲染、或正确性/安全缺陷。缺 `output_schema.json`（R216）、硬编码代理凭证（R215）、Camoufox 未 pin `playwright==1.49.1`（R211）、upsert key 不在 output_schema（R212）、未知 editor 值表单不渲染（R015）、HTTP 脚本不读代理（R150）。
- `warn` = 平台接受但表单/运行可能异常，或文档 should/约定。editor/type 不匹配（R016，2026-07-13 实测平台接受）、axios+socks 未设 `proxy:false`（R214）、header 晚于 push（R213）、缺 README（R083）、缺文档标必填的 title/editor/description/required（R014a-d）。

**铁律（来自吸收的规则集）：任何 `error` 必须有真实探针（`examples/verify-*`）或开发者契约明文支撑，或结构性显而易见（缺必填文件、硬编码凭证字面量）。不得仅凭文档"must"定 `error`。** 2026-06-17 的"code 4000"事件——凭文档假设编造错误码，被 2026-07-13 探针推翻——是前车之鉴（详见 `references/known-gaps.md`）。

自动核对（须在 coreclaw-cli 仓库目录内运行，因 diff-contract 扫描其 `src/validation/`）：
```bash
git clone https://github.com/Core-Claw/coreclaw-cli.git
cd coreclaw-cli
# 把本 skill 吸收的 diff-contract.cjs 放到 skills/coreclaw-cli-audit/scripts/ 后运行，
# 或直接用 coreclaw-cli 仓库自带的同名脚本：
node src/cli.js validate <你的worker项目路径>
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs   # 规则 + API operation 覆盖率
```


### 第 2 层 — 实跑验证输入（API / MCP）

静态规则保证 schema 合规；不能保证平台接受真实输入值。用最小真实输入跑一次验证。

**前置约束（2026-07-21 实测）**：待审核版本（刚更新或新创建、未发布上架）无法经 API/MCP 运行——`get_worker`/`get_worker_input_schema` 能读到 schema，但 `run_worker` 返回 `50001 worker does not exist`，且 `list_store_workers` 搜不到该 worker。对待审核版本，L2 跳过实跑，标 `[VERIFY] 须 UI 试跑`，不要把 50001 误记为脚本缺陷。详见 `references/verification-protocol.md`。

优先 MCP（已含分页补偿 + 新鲜度修复）：
- `get_worker_input_schema` — 重读 live schema，绝不凭记忆造字段名。
- `run_worker` 用基于 live schema 构造的最小 `input_json`（异步）。
- `get_worker_run` + `get_worker_run_log` — 平台拒绝时抓真实 `code` + `message`。这本身就是支撑 `error` 的探针。

REST 兜底（MCP 不可用）：base URL `https://openapi.coreclaw.com`，`Authorization: Bearer <token>` 或 `?token=<token>`。契约见平台 API 文档，operationId `runWorker`。

完整验证协议与探针产物格式：`references/verification-protocol.md`。

### 第 3 层 — 输出正确性

运行成功的也可能产出错误输出。把结果行与真实情况对照，不只看"跑完了"：

- **字段存在**：`output_schema.json` 每个列都出现在真实结果行里（用 `list_worker_run_results` 抽样）。
- **字段正确**：抽 3-5 行与源页对照。`phone` 字段装了网站 URL、`rating` 是字符串而非数字、`reviews_count` 在有 200 条评论的地点上是 null——这些是 schema 校验抓不到的正确性 bug。
- **shape vs schema**：`output_schema` 写 `array<string>` 但行里是逗号分隔字符串 → 不匹配。
- **去重 / 分页**：用 `concurrency.fields` 拆分时，确认拆分任务间无重复行、无因 1 基 offset 陷阱漏行（见 `references/concurrency-suggestions.md` P2）。

导出小样本做 diff：
```
# 经 MCP: export_worker_run_results → 签名 download_url，格式 csv/json/jsonl/xlsx/xls/xml/html/rss
```
平台支持 8 种导出格式：**CSV、JSON、JSONL、XLSX、XLS、XML、HTML、RSS**（来源：平台文档）。

### 第 4 层 — 改进建议

这是 CLI 审计不提供的层。每条发现给具体可操作建议，按影响排序。最富矿的是并发调优——见 `references/concurrency-suggestions.md` 完整矩阵。摘要：

- **吞吐**：worker 有数组输入（如 `keywords`、`place_ids`、`google_maps_urls`）但没配 `concurrency.fields`，建议加上，让平台拆成并行任务而非串行单任务。
- **成本控制**：某字段会让预扣费爆炸（如 URL 列表每个 URL 可能返回数百结果），建议加 `concurrency.limits` 规则封顶每项预扣费。`limits` 不改任务数或任务内容——只封顶每项预扣（计费）数。
- **遗留迁移**：worker 还在用 legacy `b` 拆分，建议迁到 `concurrency.fields`（`fields` 存在时 `b` 被忽略；`b` 仅兼容）。
- **`remove_fields`**：某拆分字段值不应出现在下游任务 custom（如内部 ID），建议用 `concurrency.remove_fields` 删除而非保留为 `[""]`。
- **结果质量**：抽检发现空或畸形字段，建议修抽取器而非记录缺口。

其它建议类目：输入 schema UX（editor 选择、default、description）、输出完整性（缺有用列）、错误消息（含修复建议，绝不"code 4000"）、README 准确性（字段与实际 schema 一致——交给 `readme-writer` skill）。

### 第 5 层 — 分级报告

每条发现一行，`error` 在前，次 `warn`，次 `VERIFY`（需探针），次 `SUGGEST`（建议）。每条带来源指针。

```
[ERROR]  L1: <规则码> — <claim>。来源: coreclaw-cli-audit/contract-checklist.md R### [文件:行]
[VERIFY] L2: <claim> — 须造 examples/verify-<topic>，经 MCP run_worker 跑 [文件:行]
[WARN]   L1: <规则码> — <claim>。来源: <文档或规则> [文件:行]
[SUGGEST] L4: <改进>。来源: concurrency-rules.md §<节> [文件:行]
```

结尾 `net: <E> errors, <W> warns, <V> 待探针, <S> 建议。` 未要求则不改——本 skill 只报告，用户决定。

## MCP / API 适配

验证时用 MCP 面（它已修复裸 REST 调用会踩的分页 offset 与 `/last` 新鲜度 bug）：

- 发现：`list_store_workers`（公开）/ `list_workers`（自有）→ `get_worker` → `get_worker_input_schema`。
- 运行：`run_worker`（异步、ad-hoc 输入）或 `run_worker_task`（保存的预设）。多 worker 回归：`run_workers_batch` 带 `verify`、`concurrency=1` 避免限流掩盖问题。
- 状态：`get_worker_run`（显式 `run_id`，优先于可能 stale 的 `/last`）。返回字段（2026-07-23 实测）：`status`（唯一主要结果判断字段）、`results`（行数，`0` 不代表失败）、`err_msg`（可缺失，成功运行通常无）、`usage`/`traffic`（诊断，非成败判断）、`started_at`/`finished_at`/`duration`（Unix 秒）。状态取值 `ready`/`running`/`succeeded`/`failed`/`aborting`——`aborted` 不在公开契约，勿用。
- 结果：`list_worker_run_results`（预览）/ `export_worker_run_results`（下载，8 格式）。响应 `data.count` 为总行数，`data.headers[].{key,label}` 为列定义，`data.list[]` 为行；行可能含内部字段 `__coreclaw_data_id__`（忽略）。分页：`offset` 从 0 开始的行偏移（`offset += limit` 翻页正确），`page_index` 仅为响应内一基显示页号，非请求参数。
- 不看行即可判：`verify_run` → PASS / NO_DATA / FAILED / ERROR_RECORD / RUNNING / SUBMIT_FAIL（防 CAPTCHA/403 行被误判 PASS）。
- 失败看日志：`get_worker_run_log`（支持 grep/context_lines）。返回 `data.all_logs_url`（完整日志下载，可能临时）、`data.list[].{type,group,content,timestamp}`（timestamp 毫秒）、`data.result_count`。

鉴权：MCP 把 `Authorization: Bearer <token>` 转发上游。v2 支持三种等价鉴权——`Authorization: Bearer <token>`、`?token=<token>` query、legacy `api-key: <token>` header（已发布 `public/openapi.json` 把三者都列为全局 security；2026-07-23 复核）。推荐 Bearer；`api-key` header 合法，**不是** error。

## 保持规则集同步

本 skill 内置的规则集（contract-checklist / known-gaps / concurrency-rules）100% 吸收自 `Core-Claw/coreclaw-cli` 的 audit skill，其依据是 `Core-Claw/scraper-webui-docs` 开发者契约。两个上游都持续更新（CLI 近期加 `hardcoded_api_key`、`aiohttp_without_proxy`、`asyncio_run_with_sdk` 等规则）。正式审核前拉最新并 diff。流程见 `references/sync-procedure.md`。

## 时效性

内置规则集反映 `Core-Claw/coreclaw-cli` commit `cd48129`（2026-07-21 吸收），其依据 `Core-Claw/scraper-webui-docs` 同期状态。待审核版本不可经 API/MCP 实跑（见第 2 层）。上游会漂——依赖规则前先同步，依赖 `error` claim 前先重跑探针或确认开发者契约明文。

**2026-07-23 复核修正**：鉴权（v2 支持 `api-key` header，非 error）、分页（`offset` 为行偏移，`offset += limit` 正确；`page_index` 为响应内一基显示页号）、输入包装（`input.parameters.custom`）、运行/结果/日志响应字段，均已对齐已发布 `public/openapi.json` 与实测行为。
