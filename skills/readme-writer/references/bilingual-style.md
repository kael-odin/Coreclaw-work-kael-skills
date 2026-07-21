# Bilingual Style — Natural Chinese, Not Translation-ese

`README_CN.md` is written for a Chinese reader. It is not a machine
translation of `README.md`. Same facts, same structure, different phrasing.

## What translation-ese looks like (avoid)

Stilted markers that betray machine translation:

- "您可以用它来…" (over-formal, repetitive 您) — natural Chinese drops the
  pronoun when context is clear: "可以用来…"
- "这是一个强大的工具,它能够…" (English "is a powerful tool that can" calque)
  — Chinese prefers verb-first: "高效完成…"
- "请注意,如果您想要…" ("please note that if you want to") — just state
  the condition: "如需…"
- Noun-heavy stacks: "数据采集的自动化标准化与可重复利用的实现" — split
  into verbs: "让数据采集走向自动化、标准化、可重复利用"
- "被" passive overuse where Chinese uses active: "数据被提取" → "提取数据"
- English comma splices kept literally: ", which means…" → restructure as a
  new sentence in Chinese.

## Principles

### Verb-first, not noun-first

English technical prose leans noun-heavy ("data collection automation"). Lean
verb-heavy in Chinese ("自动化采集数据"). Action verbs carry the sentence;
the object is the data.

### Drop redundant pronouns

English requires a subject ("It extracts…"). Chinese drops it when context
is clear ("提取…"). Keep 您/它 only for politeness or disambiguation, not by
default.

### Short clauses, parallel structure

Chinese reads better with balanced short clauses than one long sentence.
The shipped READMEs use this: "告别手动搜索和逐条复制，让数据采集走向自
动化、标准化与可重复利用" — two parallel clauses, rhythm.

### Use the shipped terminology

CoreClaw platform terms have official Chinese forms in the zh-cn docs. Use
them, don't re-translate:
- Worker → Worker (keep English in tech context, or 平台任务) — match the
  zh-cn docs
- input → 输入
- output → 输出
- concurrency → 并发
- export → 导出
- webhook → webhook (keep)
- MCP → MCP (keep)

When unsure, check https://docs.coreclaw.com/zh-cn/ for the official term.

### Examples and JSON stay identical

Code blocks, JSON examples, field names in backticks, format specs — these
are identical across both files. Only the prose around them is Chinese. Do
not translate field names inside JSON. Do not translate `keyword` to `关键
词` inside a JSON example — the field name is `keyword`.

### Tone: helpful, not formal

The shipped READMEs address the reader directly with advice ("建议使用含
义不同、重叠度低的业务关键词组合"). Match that — direct, advisory, not
bureaucratic. Avoid 须知/告示 register.

## Re-check pass

After writing `README_CN.md`, read it aloud (mentally). Any clause that sounds
like it was translated — restructure it. The test: would a Chinese engineer
reading a native tool's docs write this sentence? If not, rewrite.

## Heading symmetry

Headings between the two files must be structurally symmetric (same section
order, same H2/H3 hierarchy). The Chinese heading text is natural Chinese,
not a word-by-word translation of the English. Example:

| English H2 | Chinese H2 (good) | Chinese H2 (translation-ese, avoid) |
|------------|-------------------|--------------------------------------|
| What data does X extract? | X 会提取哪些数据？ | X 提取什么数据？ |
| Search term (required) | 搜索词（必填） | 搜索术语（被要求） |
| Enhancement features | 增强功能 | 增强功能特性 |

Anchor slugs: GitHub slugifies from the heading text. If the English and
Chinese headings differ, cross-file anchor links (e.g. `[see Input](#input)`)
may not resolve across files. Keep headings structurally parallel; if you
need cross-file links, use file-level links (`README.md#input`) and accept
that the Chinese anchor may differ.
