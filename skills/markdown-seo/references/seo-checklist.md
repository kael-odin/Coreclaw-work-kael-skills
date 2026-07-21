# SEO Checklist — Rationale

Each checkbox from SKILL.md, with the why and a concrete example.

## On-page

### Title contains primary keyword phrase

GitHub search and web search both weight the repo name + first H1. The primary
keyword phrase is what someone would type to find this repo. "awesome-free-
proxy-list" ranks for "free proxy list" because the phrase is in the name, the
H1, and the hero alt.

Bad: `my-tool` (no keyword).
Good: `awesome-free-proxy-list — daily-verified free proxies with metadata`.

### First H1 singular and matches docs-site `<title>`

One H1 per page. If the docs site has a different title than the README H1,
search engines see them as different pages competing for the same query.

### "Why this exists" in the first screen

3-second bounce test. Also the natural source for `<meta name="description">`.
Google truncates meta description at ~155 chars — keep the first sentence of
"Why this exists" under that.

### First-runnable command within first 3 sections

Dwell time is a ranking signal. A reader who runs a command and gets a result
stays longer, signals relevance. Repos that front-load installation
instructions lose readers who haven't decided the repo is worth installing.

### Descriptive link text

"click here" tells search engines nothing about the destination. Link text is
anchor text — it's a ranking signal for the target page.

Bad: `see [here](docs/quickstart.md)`.
Good: `see the [quick start guide](docs/quickstart.md)`.

### Image alt = value prop + keyword

Alt text is indexed. A hero with `alt="banner"` wastes the most prominent
image's SEO weight. `alt="awesome-free-proxy-list — daily-verified free
proxies with country, latency, and anonymity metadata"` puts the value prop
where crawlers read it.

### Code blocks have language hints

```bash and ```python render with syntax highlighting AND are indexed by
language. ```\`\`\`` (no hint) renders as plain text and loses both. mkdocs /
Hugo / Jekyll all need the hint to apply the right highlighter.

## Site / repo level

### Bilingual READMEs linked bidirectionally

Doubles addressable audience. The link must be in the FIRST block of both
files (above the fold), not buried in a footer. Pattern:
`> 🌍 Language: English · [中文](README.zh-CN.md)`.

Source: both captcha and proxy-list repos.

### Docs site meta description per page

Every page needs its own `<meta name="description">`, derived from that page's
first paragraph. A site-wide default description causes duplicate-meta issues
in search console.

### sitemap.xml + robots.txt

mkdocs-material: `plugins: [{search}, {sitemap}]`. Hugo: built-in. Jekyll:
`jekyll-sitemap` gem. Verify the file is served at `/sitemap.xml` after
deploy — a misconfigured base URL breaks this silently.

### OpenGraph tags

`og:title`, `og:description`, `og:image` on the landing page. These render the
link preview on Twitter/LinkedIn/Slack and in some search results. Missing
`og:image` → link preview is text-only, lower CTR.

### RSS feed (for schedule-updating repos)

The academic-research-skills repo ships RSS. For repos that update on a CI
schedule (proxy list, rankings), an RSS feed lets users subscribe to updates
and gives aggregators another discovery path.

## Freshness signals

### Dynamic badge

shields.io `dynamic/json` badge reads a JSON file (raw GitHub URL) and renders
a field. Proves the repo is maintained at a glance. Example from proxy-list:

```
[![Proxies](https://img.shields.io/badge/dynamic/json?url=...summary.json&query=$.counts.all.working&label=working&color=brightgreen)](...)
```

### STATS:START/END block

CI script (e.g. `scripts/update.py`) rewrites the block each run. The README
always shows current numbers. Stale numbers are a trust-killer; this removes
the maintenance burden.

### CI badge in hero

Green CI badge = maintained. Red CI badge = abandoned or broken. Either way
it's a signal readers (and savvy search engines via structured data) read.
