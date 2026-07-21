# README Structure — Annotated

The skeleton from SKILL.md, block by block, with the reason each block exists
and where the pattern was proven.

## Block 1 — Hero + badges (`<div align="center">`)

```
<div align="center">
  <img src="assets/readme/hero.svg" alt="<one-line value prop with primary keyword>" width="100%">
  [![CI](...badge...)](...workflow...)
  [![License: MIT](...)](LICENSE)
  [![dynamic-json badge showing live count]](raw-data-url)
  [![GitHub stars](...social...)](...stargazers)
  🌐 [Dashboard] · 🔗 [Subscription] · 📦 [Raw data] · 📊 [Stats]
</div>
```

**Why:** the first screen decides bounce. Hero proves identity; badges prove
the repo is alive (CI green), licensed, and has live data; the link row gives
the 4 most-likely next clicks without scrolling.

**Source:** `awesome-free-proxy-list/README.md` L1-12,
`how-to-bypass-amazon-captcha/README.md` L1-14.

**Visual layer belongs to `beautify-github-readme`** — this skill only owns the
`alt` text and the link-row copy ordering.

## Block 2 — "Why this exists" callout

```
> **Why this exists.** <3-sentence problem statement. Most repos in this space
> do X badly. This repo attaches Y. CI verifies Z, zero server cost.>
```

**Why:** search engines and GitHub search both weight early prose. Users
bounce in 3 seconds without a reason. This block is the elevator pitch AND the
SEO meta-description source (derive the docs-site `<meta description>` from
it). Three sentences max — the first names the problem, the second names the
differentiator, the third names the proof.

**Source:** both proxy-list and captcha repos open with this exact shape.

## Block 3 — First-runnable command

```
```bash
# first successful action — <what it does>
curl -s https://raw.githubusercontent.com/.../all.txt | head
```
```

**Why:** proves the repo works before the reader commits to reading. Lowest
friction win. The comment tells the reader what success looks like. Must be a
command that returns a real result on the first try — no setup, no API key,
no install. If the repo genuinely can't offer one (e.g. requires auth), link
to a live demo instead.

**Source:** `awesome-free-proxy-list/README.md` (curl the working list).

## Block 4 — Live stats / What you get

Dynamic block (see SKILL.md dynamic stat block) OR a "What you get" bullets
section enumerating the value per row, not per feature.

**Why:** "features" lists that read as capabilities ("supports X") underperform
"what you get" lists that read as benefits ("every proxy ships with country,
latency, anonymity"). Benefits convert; capabilities don't.

## Block 5 — Quick start

30-second path to first result. Numbered, copy-pasteable. The reader who
finishes this section has a working thing; everything after is depth.

## Block 6 — Domain sections

The actual content. Order by reader priority, not by implementation order.
Put the highest-value workflow first.

## Block 7 — Contributing / License

Boilerplate but required for trust + licensing clarity (SEO and legal).

## Anti-patterns to remove on sight

- Table of contents at the very top before the hero — pushes the value prop
  below the fold. Move ToC to after the first-runnable command, or omit (GitHub
 's sidebar handles navigation).
- "Status: WIP" without saying what works — readers can't tell if it's usable.
- Feature lists in implementation language ("uses Redis, Express, Vue") instead
  of benefit language.
- Screenshots without `alt` text.
- Internal anchor links that break because headings were translated to a
  different locale.
