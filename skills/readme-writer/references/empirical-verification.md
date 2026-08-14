# 实测验证 — 输入输出 claim 以实跑为准

README 的输入输出 claim（接受哪些输入形态、去重与否、失败是否产行、单次上限、真实输出结构）**必须以真实 run 的证据为准**，不以脚本自带 README、本地源码或 schema 推测为准。

## 为什么必须实跑（在案 3 例，Instagram 用户 ID 采集器）

| 自带 README / 源码声称 | 实测（API/MCP 真实 run） | 根因 |
|---|---|---|
| 输入接受对象数组 `[{"profile_id": ...}]` | `400 INVALID_INPUT`，只接受纯字符串数组 | 自带 README 描述的是"设计态"；线上 schema 是 `type: array` |
| "自动去重、接受逗号/分号/换行分隔文本" | 逗号文本整体被拒；重复 ID 重复出结果行 | 平台按元素拆子任务（fan-out），脚本里的批量 `parse_input` 是死代码——本地源码 ≠ 线上行为 |
| "查询失败也占一行，`profile_id` 保留、其余留空" | 失败 ID 无任何可见行 | 脚本内部确实推 `error_record`（带 ID 的空行），但平台把失败子任务的记录过滤出结果表/导出 |

教训：**可实测的行为，能跑一次真实 run 就不只读代码**。写 README 前先跑探针。

## 探针流程（MCP 优先，REST 兜底）

1. `get_worker_input_schema(worker_id)` — 记每个字段的 type/editor/required/default/enum。这是 API 层校验的依据（schema `type: array` 就是顶层字符串被拒的原因）。
2. `run_worker(worker_id, input_json, is_async=true)` — 探针输入见下节。保存 run_id。
3. `poll_run(run_id)` 到终态，或 `get_worker_run` 查 status。
4. `list_worker_run_results(run_id)` — 看返回行（count 与内容）。
5. `get_worker_run_log(run_id, grep="status_code|error_code|Total.*subtasks")` — 确认失败路径（400 / 404 / INVALID_INPUT / PROFILE_ID_UNRESOLVED）。
6. 需要完整嵌套时 `export_worker_run_results(run_id, format="json")`。

> 实跑消耗真实余额——探针输入保持最小（2-4 个元素）。待审核版本无法实跑（`run_worker` 返回 `50001 worker does not exist`），标 `[VERIFY] 受审核版本限制`，详见 script-audit 的 `verification-protocol.md`。

## 输入探针设计

一次 run 混入多种元素，逐条对照。构造原则：**真实可解析值打底，每个要验证的 claim 加一个针对性元素**。

| 要验证的 claim | 探针元素 | 判定 |
|---|---|---|
| 数组 vs 对象数组 | 一个元素用 `{"profile_id": "..."}` 对象 | 对象元素被拒 ⇒ 只写数组格式 |
| 纯字符串数组 | 全部元素为字符串 | 通过 ⇒ 输入示例用字符串数组 |
| 逗号分隔文本是否拆分 | 一个元素是 `"123,456"` | 被拒或当作单个无效 ⇒ 不写"支持逗号分隔" |
| 去重 | 同一真实 ID 出现两次 | 出 2 行 ⇒ 不写"自动去重"；出 1 行 ⇒ 可写 |
| 坏元素行为 | 一个非数字/不存在元素 + 一个真实元素 | run succeeded 且坏元素无行 ⇒ "坏元素被忽略"；整 run failed ⇒ "无效输入会导致运行失败" |
| 单次上限 | 逐步逼近上限数量 | 记录真实上限数字 |
| 必填字段 | 只缺某必填字段 | 校验错 ⇒ 标注该字段必填 |

## 输出探针清单

- **结果行列** = `output_schema.json` 的列？（在案：完全一致）
- **失败/查不到是否产行**：脚本可能推空行，但平台可能过滤失败子任务——**必须实测**。用 `list_worker_run_results` 的 count 判定，别信代码里的 `error_record` 调用。
- **真实 JSON 嵌套**：schema 只给顶层类型；嵌套子字段、空值形态（`""` / `null` / `[]`）只有真实输出才知道，不凭 schema 的 `items`/`fields` 编。
- **错误记录 vs 真实行**：用 `verify_run`（返回 `PASS`/`NO_DATA`/`FAILED`/`ERROR_RECORD`）区分，防 CAPTCHA/403 空行被当成成功数据。
- **全量 vs 预览**：分页 `offset` 是行偏移不是页码；要全量看用 export。

## 证据记录（进 grounding sheet）

每个可实测的 README claim 记一行：claim → run_id → 探针输入 → 观察结论。例：

```
claim: 输入只接受纯字符串数组（对象数组 400）；失败 ID 不产行
  run_id: 01KZYZKK66W9KFYERSZY14K1KE
  探针: ["25025320", "99999999999999999"]
  观察: run succeeded, result_count=1（仅真实 ID 一行），日志 404 PROFILE_ID_UNRESOLVED
```

README 里"输入接受什么""最多 N 条""失败会怎样"这类句子，都应能追到一张这样的行。无 run_id 或 schema 证据的可实测 claim，不得写入 README。
