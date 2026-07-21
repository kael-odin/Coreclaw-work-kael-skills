# SEO 与 Meta 规范

Phase 0 生成标题/描述/meta，Phase 5 整体 SEO 优化的依据。

## Phase 0 — 产品化标题、描述、meta

### 产品化标题

**目标**：简短、有区分度、用户友好、含核心关键词与数据对象。**不一定用脚本原名**——脚本文件名常是无意义的（`tiktok_2`），要重命名成产品化标题。

**范式**（参考已发布的 CoreClaw worker 命名）：
- `<平台> <对象> Scraper`：Google Maps Scraper
- `<对象> By <限定维度>`：Instagram Comment By Post URL
- `<平台> <对象> Scraper By <维度>`：TikTok Video Scraper By Hashtag

**规则**：
- 含主关键词（用户会搜的词，如 "Google Maps""TikTok""Instagram""Scraper"）。
- 有区分度——若与 store 里已有 worker 重名，加限定维度（By URL / By Hashtag / By Location / By Username）。
- 英文首字母大写（Title Case）；中文自然语序。
- ≤ 40 字符（英文）/ ≤ 16 字（中文）为佳。

**中英各一份**，例如：
- EN: `Instagram Comment By Post URL`
- ZH: `Instagram 按帖子 URL 采集评论`

### 简短描述

**目标**：一句话说清"输入什么 → 输出什么结构化数据 → 核心用途"。

- 英文 ≤ 160 字符（也用于 meta description 备选）。
- 中文 ≤ 30 字。
- 含主关键词，自然通顺不堆词。

例：
- EN: `Extract all comments from any Instagram post URL into structured data — author, text, likes, timestamp.`
- ZH: `输入 Instagram 帖子链接，一键提取全部评论的结构化数据——作者、正文、点赞、时间。`

### meta 标题（`<title>`）

用于 docs 站点 `<title>` 标签。搜索引擎结果页（SERP）标题。

- 英文 ≤ 60 字符（超出被截断）。
- 中文 ≤ 30 字。
- 格式：`<产品化标题> | CoreClaw` 或 `<产品化标题> - <次要关键词> | CoreClaw`。

例：
- EN: `Instagram Comment By Post URL | CoreClaw`
- ZH: `Instagram 按帖子 URL 采集评论 | CoreClaw`

### meta 描述（`<meta name="description">`）

SERP 摘要。决定点击率。

- 英文 ≤ 155 字符。
- 中文 ≤ 80 字。
- 含主关键词 + 价值点 + 行动暗示，自然通顺。
- 不要与简短描述完全相同——meta 描述可更侧重搜索意图与点击诱导。

例：
- EN: `Scrape Instagram comments by post URL. Export author, text, likes, and timestamp as CSV, JSON, or Excel. Start scraping in minutes on CoreClaw.`
- ZH: `按帖子链接采集 Instagram 评论，导出作者、正文、点赞数、时间，支持 CSV/JSON/Excel 等 8 种格式。在 CoreClaw 上几分钟即可开始。`

### 关键词清单

中英各一份，3-8 个。用于 meta keywords（弱权重但仍写）与正文布点参考。主词 + 长尾 + 平台词。

例（英文）：`Instagram comment scraper, scrape Instagram comments by URL, Instagram comment export, CoreClaw worker`

## meta 落地（若该 worker 有 docs 站点页）

在 README 顶部或 docs 页 frontmatter 写明 meta 标题与描述。GitHub README 本身无 meta 标签，但 docs 站（mkdocs/Hugo/Jekyll）要落到 `<head>`。若仅 GitHub README，则：
- README 首行 H1 = 产品化标题（即 meta 标题主体）。
- "什么是 X？"段的第一句 = meta 描述的来源。

## Phase 5 — 整体 SEO checklist

写完正文逐条过：

**页面内**
- [ ] 首行 H1 单一，与产品化标题一致，含主关键词。
- [ ] "什么是 X？"段在首屏（3 秒讲清价值）——搜索引擎与 GitHub 搜索都加权早期散文。
- [ ] 首条可运行命令在首 3 节内（若适用），证明价值、拉长停留时长（排名信号）。
- [ ] 描述性链接文本，禁"点击这里""here""this"。
- [ ] 图片 `alt` = 价值定位 + 关键词，禁"banner"。
- [ ] 代码块带语言标注（```bash、```json、```jsonc）——GitHub 与 docs 渲染器都按语言索引。
- [ ] 标题层级清晰，单一 H1，H2/H3 不跳级。
- [ ] 主关键词在 H1、首段、至少一个 H2、至少一个 alt 里自然出现（不堆砌）。

**站点/仓库级**
- [ ] `README.md` 与 `README_CN.md` 首屏双向链接（`> 🌍 语言：…`），双语翻倍可触达受众。
- [ ] 导出格式说明含全部 8 种（CSV/JSON/JSONL/XLSX/XLS/XML/HTML/RSS）——这些是长尾搜索词。
- [ ] FAQ 含"当 API 用"一条，带真实 REST API base URL 与流程——捕获"XXX API"类搜索意图。
- [ ] 不编造任何链接（见 grounding-rules 规则 3）——坏链损害信任与排名。

**新鲜度信号（若仓库有 CI/动态数据）**
- [ ] 动态 badge（shields.io dynamic/json）显实时数据/最后更新——证明仓库活跃。
- [ ] CI badge 置顶——绿色 CI 是信任信号。

## 关键词布点原则

- 主关键词在 H1 + 首段 + 一个 H2 + 一个 alt 里自然出现即可，不要塞满（堆砌被判罚）。
- 长尾词放在"输入""FAQ"小节的自然句里（如"scrape Instagram comments by URL"出现在输入参数说明里）。
- 平台词（CoreClaw）在标题后缀和 FAQ"当 API 用"段出现，建立品牌关联。

## 时效性

SEO 规范反映 2026-07 主流搜索引擎行为（Google SERP 截断约 60 字符标题 / 155 字符描述）。Google 抓取与 shields.io 渲染可能漂移，但标题/描述长度上限是稳定经验值。
