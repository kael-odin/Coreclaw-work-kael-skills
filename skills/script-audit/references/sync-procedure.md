# 同步流程 — 与 coreclaw-cli-audit 保持规则集同步

第 1 层静态规则集源自 `Core-Claw/coreclaw-cli` → `skills/coreclaw-cli-audit/`。本 skill **不**重定义这些规则；只引用。正式审核前须同步。

> 本 skill 不依赖本地路径。clone `Core-Claw/coreclaw-cli` 到任意目录即可。

## 何时同步

- 审核一个近 2 周没审过的 worker 前。
- 发现引用了某规则码但不确定它是否还存在时。
- `coreclaw-cli` 仓库在 `audit`/`validation` 相关路径有新 commit 后（盯触及 `skills/coreclaw-cli-audit/` 或 `src/validation/` 的 commit）。

## 同步步骤

```bash
# clone 或更新到任意本地目录
git clone https://github.com/Core-Claw/coreclaw-cli.git
cd coreclaw-cli
git fetch origin
git log --oneline origin/main -10              # 扫 audit/validation commit
git pull --ff-only
```

然后把规则源与本 skill 上次审核假设做 diff：

```bash
# 1. 规则清单（规则码 + severity 的权威来源）
cat skills/coreclaw-cli-audit/references/contract-checklist.md

# 2. 已知缺口 + 探针结果（已解决/待查）
cat skills/coreclaw-cli-audit/references/known-gaps.md

# 3. 并发规则（改进建议基础）
cat skills/coreclaw-cli-audit/references/concurrency-rules.md

# 4. 跑自动 diff（规则覆盖率 + API operationId 覆盖率）
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs
```

## 同步后带入本 skill 的内容

- 新规则码 → 第 1 层发现里按码引用（如 `R216`、`hardcoded_api_key`）。不要把规则文本抄进本 skill——指向源头。
- `known-gaps.md` 新探针结果 → 更新 severity 假设。标 `✅ Resolved` 为 `error` 的规则保持 `error`；标 `⚠️ 实测推翻` 的规则意味着原 `error` 现为 `warn`（或取消）。
- `concurrency-rules.md` 新并发行为 → 更新本 skill 的 `references/concurrency-suggestions.md`。
- 平台 API 文档新增 operation → 若某验证步骤需要，更新本 skill SKILL.md 的 MCP 适配列表。

## 不要带入的

- CLI 自身校验代码（`src/validation/*.js`）——那是引擎不是规则。本 skill 跑引擎，不移植它。
- CLI 的 `test/` fixture——它们测 CLI，不测你的 worker。

## 时效戳

同步后，更新 `skills/script-audit/SKILL.md` 末尾 `## 时效性` 行，写 `coreclaw-cli` commit SHA 与日期。这是本 skill 唯一断言"截至某日"的地方——其它 claim 一律指向来源而非断言当下。
