---
name: markdown-seo
description: >
  Write and SEO-optimize Markdown for CoreClaw content repos — READMEs, docs,
  guides, tutorial sites. Applies the structural + SEO pattern proven across
  awesome-free-proxy-list, how-to-bypass-amazon-captcha, and
  awesome-academic-research-skills. Not visual beautification (use
  beautify-github-readme for that). Trigger on: "write the README", "SEO this
  doc", "optimize markdown", "写 README", "SEO 优化", "docs site structure".
---

# Markdown + SEO (CoreClaw Content Repos)

Write Markdown that ranks and converts, using the structural + SEO pattern
already proven in shipped CoreClaw content repos. This skill owns the **content
layer**: information order, copy hierarchy, the "why this exists" hook, the
first-runnable command, dual-language, dynamic stat blocks, and on-page SEO.
It does NOT own the visual layer — that's `beautify-github-readme` (hero SVG,
badges, motion). The two compose: this skill writes the content, that one
dresses it.

## Sources

- Proven shipped repos (the pattern source):
  - `D:/Coreclaw_Work/github/awesome-free-proxy-list/` — bilingual, dashboard, dynamic stats, CI
  - `D:/Coreclaw_Work/github/how-to-bypass-amazon-captcha-when-scraping/` — bilingual, docs site, playground, CI
  - `D:/Coreclaw_Work/github/awesome-academic-research-skills/` — dark mode, cards, sparkline, URL hash, SEO+RSS
- Reference files: `references/readme-structure.md`, `references/seo-checklist.md`

## Background: the pattern that works

Three CoreClaw content repos shipped to main with the same skeleton and all
three index well in GitHub + search. The skeleton is not aesthetic — it's a
conversion funnel: hero badge-row proves the repo is alive → "why this exists"
justifies the click in 3 seconds → first-runnable command proves it works
before the reader commits to reading → dynamic stats prove ongoing freshness.
SEO is not a section you add at the end; it's the information order itself.

## The skeleton (copy this order)

```
<div align="center">                          # hero + badges (visual layer pairs here)
  hero image (alt text = the one-line value prop, 1 keyword)
  CI badge · License · dynamic-json badge · stars badge
  link row: dashboard · subscriptions · raw data · stats
</div>
---
> **Why this exists.** <3-sentence problem statement + what this repo attaches that others don't.>
```bash
# first successful action — one command that works, lowest-friction win
<one curl/git clone that returns a real result>
```
## Live stats / What you get                   # dynamic block proves freshness
## Features                                     # bullet list, each a benefit not a feature
## Quick start                                  # 30-second path to first result
## ... domain sections ...
## Contributing / License
```

Full annotated structure with the reasoning for each block:
`references/readme-structure.md`.

## SEO checklist (run on every content file)

Every box must be ticked or explicitly waived with a reason. Full rationale +
examples in `references/seo-checklist.md`.

**On-page**
- [ ] Title line contains the primary keyword phrase naturally (not stuffed).
- [ ] First H1 is singular and matches the `<title>` of the docs site.
- [ ] "Why this exists" block in the first screen — search engines and GitHub
      search both weight early prose; users bounce in 3s without a reason.
- [ ] First-runnable command within the first 3 sections (proves value fast).
- [ ] Descriptive link text, never "click here" / "here" / "this".
- [ ] Image `alt` text carries the value prop + a keyword, not "banner".
- [ ] Code blocks have language hints (```bash, ```python) — GitHub and docs
      renderers both index fenced code by language.

**Site / repo level (for repos with a docs site)**
- [ ] `README.md` and `README.zh-CN.md` (or target locale) linked bidirectionally
      near the top — bilingual doubles addressable audience.
- [ ] GitHub Pages site with a clean URL structure; every page has a
      `<meta name="description">` derived from its first paragraph.
- [ ] `sitemap.xml` + `robots.txt` served by the docs site (mkdocs/Hugo/Jekyll
      all generate these; verify they exist).
- [ ] OpenGraph tags on the docs site landing page (`og:title`, `og:description`,
      `og:image`) — link previews on social/search.
- [ ] RSS feed for repos that update on a schedule (the academic-research-skills
      repo ships one; proxy-list could).

**Freshness signals (SEO + conversion)**
- [ ] Dynamic badge (shields.io `dynamic/json`) showing live count / last-updated
      — proves the repo is maintained, a ranking signal.
- [ ] `<!-- STATS:START/END -->` block auto-injected by a CI script — no manual
      maintenance, numbers never go stale.
- [ ] CI badge visible in hero — green CI is a trust signal.

## Dual-language (bilingual) pattern

Two repos ship bilingual and it doubled their reachable audience. The pattern:

- `README.md` (English, primary) and `README.zh-CN.md` (or target locale).
- Language switcher in the first block of BOTH files:
  `> 🌍 Language: English · [中文](README.zh-CN.md)` and the mirror.
- Translate content, don't just translate headers. Code blocks stay identical
  across locales; only prose differs.
- Anchor links use the English heading slugs in both files (GitHub slugifies
  headings; mixing locales breaks internal anchors). Keep headings identical
  across locales if possible, or accept that cross-locale anchor links break.

## Dynamic stat block (freshness without maintenance)

The pattern from awesome-free-proxy-list — a CI script rewrites a fenced
section each run, so the README always shows current numbers without a human
touching it:

```
<!-- STATS:START -->
Last update (UTC): **2026-07-20T04:03:03+00:00**
| Type | Working | Total |
|---|---:|---:|
| HTTP | 305 | 2000 |
<!-- STATS:END -->
```

The CI script reads `START`/`END` markers and replaces everything between.
Never hand-edit inside the markers — the next run overwrites it.

## When NOT to use this skill

- Pure visual README beautification → `beautify-github-readme`.
- Writing a docs site's CSS / theme → frontend-design.
- A one-file internal note with no SEO goal → just write it, skip the skeleton.

## Recency

Pattern validated 2026-07-10 through 2026-07-20 across the three source repos.
GitHub's renderer and shields.io behavior can shift — if a dynamic badge stops
rendering, check the shields.io schema before assuming the README broke.
