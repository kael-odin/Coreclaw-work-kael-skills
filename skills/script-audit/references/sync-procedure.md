# 同步流程 — 与上游保持规则集同步

本 skill 第 1 层静态规则集（`references/contract-checklist.md`、`references/known-gaps.md`、`references/concurrency-rules.md` + `scripts/diff-contract.cjs`）100% 吸收自 `Core-Claw/coreclaw-cli` 的 `skills/coreclaw-cli-audit/`。其依据是 `Core-Claw/scraper-webui-docs` 开发者契约。本 skill **不**重定义规则；只引用。正式审核前须同步。

> 本 skill 不依赖本地路径。clone 仓库到任意目录即可。

## 何时同步

- 审核一个近 2 周没审过的 worker 前。
- 发现引用了某规则码但不确定它是否仍在上游时。
- `coreclaw-cli` 或 `scraper-webui-docs` 有新 commit 后。

## 同步步骤

### 拉 coreclaw-cli 的 audit skill（规则集来源）

```bash
git clone https://github.com/Core-Claw/coreclaw-cli.git
cd coreclaw-cli
git fetch origin
git log --oneline origin/main -10              # 扫 audit/validation 相关 commit
git pull --ff-only
```

把上游 `skills/coreclaw-cli-audit/` 与本 skill 吸收的副本做 diff：

```bash
# 对比四个吸收文件，看上游是否有更新
diff skills/coreclaw-cli-audit/references/contract-checklist.md <本skill路径>/skills/script-audit/references/contract-checklist.md
diff skills/coreclaw-cli-audit/references/known-gaps.md          <本skill路径>/skills/script-audit/references/known-gaps.md
diff skills/coreclaw-cli-audit/references/concurrency-rules.md    <本skill路径>/skills/script-audit/references/concurrency-rules.md
diff skills/coreclaw-cli-audit/scripts/diff-contract.cjs          <本skill路径>/skills/script-audit/scripts/diff-contract.cjs
```

有变更 → 把上游新版复制覆盖本 skill 对应文件，保留本 skill SKILL.md 里吸收时加的中文说明段。

### 拉 scraper-webui-docs（规则集的契约依据）

```bash
git clone https://github.com/Core-Claw/scraper-webui-docs.git
cd scraper-webui-docs
git pull --ff-only
```

读开发者契约（英文 `src/content/docs/developer-guide/`，中文 `src/content/docs/zh-cn/developer-guide/`，线上 https://docs.coreclaw.com/developer-guide 与 zh-cn）：

- `worker-definition/input-schema.md`、`output-schema.md`、`project-structure.md`、`sdk-modules.md`
- `worker-definition/browser-automation/*.md`（Camoufox/Playwright/Puppeteer/Selenium/DrissionPage/Lightpanda 版本 pin 与代理契约）
- `worker-definition/platform-features/proxy-support.md`、`captcha-handling.md`、`browser-fingerprinting.md`
- `test-your-worker.md`、`builds-and-runs.md`、`deployment.md`、`publishing-and-monetization/*.md`

**遇到规则分歧以 scraper-webui-docs 开发者契约为准**——coreclaw-cli 的 audit skill 是其提炼，若上游 audit skill 与文档矛盾，信文档，并在本 skill 的 `known-gaps.md` 记录差异。

### 跑 diff-contract 验证覆盖率

```bash
# 须在 coreclaw-cli 仓库目录内运行（脚本扫 src/validation/ 与 src/cloud/client.js）
cd coreclaw-cli
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs
```
输出：validation 调用统计、checklist 覆盖率、severity 降级候选、API operationId 覆盖率。

## 同步后带入本 skill 的内容

- coreclaw-cli 新规则码 → `contract-checklist.md` 更新；本 skill 第 1 层发现可按码引用。
- coreclaw-cli 新探针结果（known-gaps.md）→ 更新 severity 假设（实测推翻则降级）。
- scraper-webui-docs 新文档或字段语义变更 → 若影响规则，向上游 coreclaw-cli 提 issue 或在本 skill known-gaps.md 记差异。
- 并发规则变更 → 更新本 skill `concurrency-rules.md`（事实）与 `concurrency-suggestions.md`（建议层）。
- 平台 API 文档新增 operation → 若影响第 2 层验证，更新本 skill SKILL.md 的 MCP 适配列表。

## 不要带入的

- CLI 自身校验代码（`src/validation/*.js`）——那是引擎实现，本 skill 引用规则码不移植引擎。
- CLI 的 `test/` fixture——它们测 CLI，不测你的 worker。

## 时效戳

同步后，更新 `skills/script-audit/SKILL.md` 末尾 `## 时效性` 行，写两个上游的 commit SHA 与日期。本 skill 唯一断言"截至某日"的地方——其它 claim 一律指向来源而非断言当下。
