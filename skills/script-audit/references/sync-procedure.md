# 同步流程 — 与 scraper-webui-docs / coreclaw-cli 保持同步

第 1 层静态规则的权威依据是 `Core-Claw/scraper-webui-docs` 的开发者契约文档；CLI 的 audit skill 是辅助（尚不完善）。本 skill **不**重定义规则；只引用。正式审核前须同步。

> 本 skill 不依赖本地路径。clone 仓库到任意目录即可。

## 何时同步

- 审核一个近 2 周没审过的 worker 前。
- 发现引用了某规则但不确定它是否仍在文档里时。
- `scraper-webui-docs` 或 `coreclaw-cli` 有新 commit 后。

## 同步步骤

### 主：scraper-webui-docs（权威）

```bash
git clone https://github.com/Core-Claw/scraper-webui-docs.git
cd scraper-webui-docs
git fetch origin
git log --oneline origin/main -10              # 扫 developer-guide 相关 commit
git pull --ff-only
```

读开发者契约（英文在 `src/content/docs/developer-guide/`，中文在 `src/content/docs/zh-cn/developer-guide/`，线上 https://docs.coreclaw.com/developer-guide 与 https://docs.coreclaw.com/zh-cn/developer-guide ）：

- `worker-definition/input-schema.md` — 输入字段、editor、类型、并发配置契约
- `worker-definition/output-schema.md` — 输出列契约
- `worker-definition/project-structure.md` — 项目结构与必填文件
- `worker-definition/sdk-modules.md` — SDK 模块
- `worker-definition/browser-automation/*.md` — 各浏览器版本 pin 与代理契约（Camoufox/Playwright/Puppeteer/Selenium/DrissionPage/Lightpanda）
- `worker-definition/platform-features/proxy-support.md`、`captcha-handling.md`、`browser-fingerprinting.md`
- `test-your-worker.md`、`builds-and-runs.md`、`deployment.md`、`publishing-and-monetization/*.md`

**遇到规则分歧以本仓库文档为准。**

### 辅：coreclaw-cli 的 audit skill（非权威，参考用）

```bash
git clone https://github.com/Core-Claw/coreclaw-cli.git
cd coreclaw-cli
git pull --ff-only
cat skills/coreclaw-cli-audit/references/contract-checklist.md   # 规则码清单
cat skills/coreclaw-cli-audit/references/known-gaps.md           # 已解决/待查缺口
cat skills/coreclaw-cli-audit/references/concurrency-rules.md   # 并发摘要（本 skill 改进建议基础）
node skills/coreclaw-cli-audit/scripts/diff-contract.cjs         # 规则 + API operation 覆盖率
```

CLI 的 audit skill 目前**尚不完善**，是开发者契约的部分提炼而非全集。可引用规则码、跑 diff-contract 自动比对、参考其并发摘要，但**权威性低于 scraper-webui-docs**。后续方向是把开发者内容从 scraper-webui-docs 进一步炼化进 CLI skill 与本 skill。

## 同步后带入本 skill 的内容

- scraper-webui-docs 新文档或字段语义变更 → 更新第 1 层 severity 判断依据（指向文档路径）。
- CLI 新规则码 → 第 1 层发现里可按码引用（如 `hardcoded_api_key`），但指向 scraper-webui-docs 对应契约而非 CLI 源。
- CLI `known-gaps.md` 新探针结果 → 更新 severity 假设（实测推翻则降级）。
- CLI `concurrency-rules.md` 变更 → 更新本 skill `references/concurrency-suggestions.md`。
- 平台 API 文档新增 operation → 若某验证步骤需要，更新本 skill SKILL.md 的 MCP 适配列表。

## 不要带入的

- CLI 自身校验代码（`src/validation/*.js`）——那是引擎不是规则。本 skill 跑引擎，不移植它。
- CLI 的 `test/` fixture——它们测 CLI，不测你的 worker。

## 时效戳

同步后，更新 `skills/script-audit/SKILL.md` 末尾 `## 时效性` 行，写两个仓库的 commit SHA 与日期。本 skill 唯一断言"截至某日"的地方——其它 claim 一律指向来源而非断言当下。
