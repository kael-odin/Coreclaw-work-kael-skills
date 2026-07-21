# Coreclaw Work — Kael 的 Skills

我个人用于 CoreClaw 工作的 Claude Code skills，全部打包在一个 plugin（`kael-skills`）里。所有 skill 都带知识来源、不依赖本地路径——别人 clone 到任意机器都能用。

## 为什么有这个仓库

CoreClaw 的工作横跨很多面（API v2、MCP server、n8n 节点、CLI、采集 worker、内容仓库）。那些花一次真实运行才学到的经验——输入包装陷阱、1 基分页 offset、concurrency.fields 吞吐杠杆——应该沉淀一次反复用，而不是每个会话重新发现。

这些 skill 是为**我自己复用**写的。它和面向消费者的 CoreClaw-Skill（教外部用户如何**操作**平台 API）不同，这里教的是**怎么干我的工作**。

## 安装

```bash
claude plugin marketplace add kael-odin/Coreclaw-work-kael-skills
claude plugin install kael-skills@coreclaw-work-kael-skills
```

所有 skill 都在 `kael-skills` plugin 下加载，调用形如 `/kael-skills:<skill 名>`。

## Skills

| Skill | 做什么 | 关键来源 |
|-------|--------|----------|
| `script-audit` | CoreClaw worker 五层审核：静态规则（error/warn）、经 API/MCP 实跑验证输入输出、输出正确性、改进建议（concurrency.fields 调吞吐/控成本）。规则集源自 `Core-Claw/coreclaw-cli` 的 audit skill 并保持同步。 | `Core-Claw/coreclaw-cli` audit skill · 平台 API 文档 · 平台文档 |
| `readme-writer` | 为 CoreClaw worker 撰写中英双语 README，基于脚本真实爬取逻辑/输入输出字段/能力范围，不编造信息与链接，输入示例完整可跑、输出示例真实。先生成产品化标题+描述+meta（中英各一份）再撰写并做 SEO 优化。 | 已发布 Google Maps Scraper 双语 README 模板 · 平台文档 |

后面还会加：worker 开发打包、worker-tasks CRUD 验收、三仓库 enum 同步、上游变更 triage。都会加到同一个 `kael-skills` plugin 里。

## 来源政策

每个 skill 都有**知识来源**段。claim 可追到：
- 被审核/被文档化的实际脚本（文件路径 + 行）
- 平台官方文档（真实 URL）
- 上游契约（平台 API 文档的 operationId）
- `Core-Claw/coreclaw-cli` audit skill（规则码，保持同步）
- memory 笔记或带日期的探针结果

无来源的 claim 标 `（实测结论 YYYY-MM-DD，待复核）` 并写明验证日期。上游会漂——依赖前先复核。

## 结构

```
.claude-plugin/
  marketplace.json          # marketplace：一个 plugin，kael-skills
  plugin.json               # plugin 清单
skills/
  script-audit/
    SKILL.md
    references/             # verification-protocol、concurrency-suggestions、sync-procedure
  readme-writer/
    SKILL.md
    references/             # readme-structure、grounding-rules、bilingual-style、seo-and-meta
```

加新 skill = 加 `skills/<名>/` 目录，plugin 自动发现，无需改 manifest。

## 平台文档基线（所有 skill 共用）

- 中文文档：https://docs.coreclaw.com/zh-cn/ · API https://docs.coreclaw.com/zh-cn/api/
- 英文文档：https://docs.coreclaw.com/ · API https://docs.coreclaw.com/api/
- MCP：https://docs.coreclaw.com/zh-cn/integrations/ai/mcp · EN https://docs.coreclaw.com/integrations/ai/mcp
- 价格：https://www.coreclaw.com/pricing · GitHub 组织：https://github.com/Core-Claw
- 平台支持 8 种导出格式：CSV、JSON、JSONL、XLSX、XLS、XML、HTML、RSS
