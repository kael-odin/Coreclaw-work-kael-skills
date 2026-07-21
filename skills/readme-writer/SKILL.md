---
name: readme-writer
description: >
  Write bilingual (EN + ZH) READMEs for CoreClaw worker scripts, matching the
  proven structure of shipped workers (e.g. tiktok_2 Google Maps Scraper).
  Content MUST be grounded in the script's actual scraping logic, input/output
  fields, and capability range — no fabricated info, no fabricated links, real
  input and output examples. Trigger on: "write the README", "写脚本 README",
  "generate worker docs", "bilingual README".
---

# README Writer (CoreClaw Worker)

Write a bilingual README (English `README.md` + Chinese `README_CN.md`) for a
CoreClaw worker script, following the proven structure of shipped workers.
The content is grounded in the script's **actual** behavior — every field,
example, and capability claim is traced to the real script, never invented.

## Sources

- **Structure template** (the canonical worker README shape):
  `D:/Coreclaw_Work/scripts/tiktok_2/README.md` and `README_CN.md`
  (Google Maps Scraper — shipped, bilingual, real examples)
- **Platform docs** (for cross-referencing field semantics, export formats,
  concurrency, pricing — link these, don't fabricate):
  - EN: https://docs.coreclaw.com/ · API https://docs.coreclaw.com/api/
  - ZH: https://docs.coreclaw.com/zh-cn/ · API https://docs.coreclaw.com/zh-cn/api/
  - MCP: https://docs.coreclaw.com/integrations/ai/mcp · ZH https://docs.coreclaw.com/zh-cn/integrations/ai/mcp
  - Pricing: https://www.coreclaw.com/pricing
  - GitHub org: https://github.com/Core-Claw
- **The script itself** (the primary source — read it before writing):
  - `input_schema.json` / `output_schema.json` — actual field names, types, editors, defaults
  - `main.py` / `index.js` — scraping logic, capability range, limits, enhancement toggles
  - any existing partial README — extract verifiable facts only
- Reference files in this skill: `references/readme-structure.md`,
  `references/grounding-rules.md`, `references/bilingual-style.md`

## Hard rules (non-negotiable)

These come straight from the user's requirements. Violating any of them makes
the README wrong, not just suboptimal.

1. **Ground everything in the actual script.** Read `input_schema.json`,
   `output_schema.json`, and the main script before writing a single line.
   Every field name, type, default, and capability claim must come from there.
2. **No fabricated information.** If the script doesn't expose a feature, don't
   document it. If you're unsure how a field behaves, say so or leave it out —
   do not guess.
3. **No fabricated links.** Only link to: the platform docs URLs above, the
   official Google/ upstream APIs (when the script wraps one and the link is
   canonical), or assets inside the repo. Never invent a `https://...` that
   you can't verify resolves.
4. **Real input examples, complete.** Input examples must be full JSON objects
   a user could paste and run — not fragments. Show the exact shape with real
   field names from the schema.
5. **Real output examples.** Output JSON must reflect actual `output_schema`
   columns with realistic values. Use reserved/example domains
   (`example.com`, `example-dental.test`) and placeholder phone numbers
   (`+1 512-555-0101`) — never real business data, but also never empty
   stubs. Mirror the real field set exactly.
6. **Detailed parameter descriptions with format examples.** Each input
   parameter gets: purpose → usage advice → recommended + not-recommended
   examples → format spec (e.g. "city + country" or a concrete Circle/Polygon
   JSON). See `references/readme-structure.md` §Input.
7. **Chinese must be natural, not translation-ese.** `README_CN.md` is written
   for a Chinese reader, not machine-translated from English. See
   `references/bilingual-style.md`.
8. **Two files, symmetric structure.** `README.md` and `README_CN.md` share
   the same section order and heading hierarchy. Section content is
   equivalent (not literal translation).

## Workflow

### Phase 1 — Read the script (grounding)

Before writing, extract these from the actual code:

- **Scraping logic**: what source does it hit, what query does it run, what's
  the per-request limit, what's the platform's hard cap (e.g. Google Maps'
  120-places-per-area limit). Source: `main.py`/`index.js`.
- **Input fields**: name, type, editor, required, default, enum values,
  description. Source: `input_schema.json`. Note which are arrays
  (concurrency candidates).
- **Output fields**: every column name + type. Source: `output_schema.json`.
- **Capability range**: what enhancement toggles exist, what each does,
  default on/off, cost implications (free add-ons vs runtime cost).
  Source: main script + schema.
- **Export formats**: CSV, JSON, JSONL, XLSX, XLS, XML, HTML, RSS (8, platform-wide).
- **Concurrency config** (if present): `concurrency.fields`, `remove_fields`,
  `limits`, legacy `b`. Affects how input arrays are split.

Record these as a grounding sheet (can be inline notes, not a deliverable).
**Do not proceed to Phase 2 with any gap — every README claim traces to a
line here.**

### Phase 2 — Map to the structure

Use the canonical structure from `references/readme-structure.md` (extracted
from tiktok_2). Summary of section order:

1. **What is X?** — one-paragraph value prop.
2. **What can you use it for?** — 4-6 benefit bullets (use cases, not features).
3. **What data does X extract?** — emoji two-column table of output fields +
   capability bullets.
4. **Input** — per-parameter subsections: purpose, advice, recommended +
   not-recommended examples, format spec. Required params marked.
5. **Output** — table view + complete JSON record (real, from Phase 1) +
   per-dimension detail sections (contact, email verification, social,
   ratings/reviews, merchant details — only those the script actually
   produces).
6. **Advanced usage** — geolocation/format params with Example 1/2/3 (only if
   the script supports them).
7. **FAQ** — 6-10 Q&A grounded in the script's real limits and integrations.
8. **Feedback** — close.

### Phase 3 — Write English first, then Chinese

Write `README.md` (English) fully from the grounding sheet. Then write
`README_CN.md` as a natural Chinese rewrite — same structure, same facts,
natural phrasing (see `references/bilingual-style.md`). **Do not
machine-translate.** Real examples (JSON, format specs) stay identical across
both files; only prose differs.

### Phase 4 — Verify against grounding

Re-check every claim against the grounding sheet:
- Every field name in the README exists in the schema?
- Every "up to N results" / "X limit" matches the script's real cap?
- Every link resolves (or is a platform-docs canonical URL)?
- Input examples are complete and runnable?
- Output JSON columns exactly match `output_schema.json`?
- Chinese reads naturally, no stilted translation?

Any mismatch → fix or remove. No exceptions.

## The 8 export formats (platform-wide)

CoreClaw supports exporting data in: **CSV, JSON, JSONL, XLSX, XLS, XML,
HTML, RSS**. State these in the Output section exactly as the platform offers
them. Source: platform docs + `exported-api-docs`.

## Bilingual pairing

Both files link to each other at the top, mirroring the shipped pattern:

```markdown
> 🌍 Language: English · [中文](README_CN.md)        # in README.md
> 🌍 语言：中文 · [English](README.md)                # in README_CN.md
```

Keep heading slugs consistent across both files where possible — GitHub
slugifies headings for anchor links, and mixed-locale headings break
cross-file anchors.

## When NOT to use this skill

- Visual README beautification (hero SVG, badges, motion) → `beautify-github-readme`.
- Content-repo landing pages with SEO goals (dashboards, subscriptions) →
  the broader `markdown-seo` pattern. This skill is specifically for
  **worker script** READMEs with input/output documentation.
- A worker with no input parameters and no output schema → there's nothing to
  document this way; write a short free-form README instead.

## Recency

Structure template reflects tiktok_2 as of 2026-07-21. Platform docs URLs and
the 8 export formats are platform-wide and stable, but field semantics in
docs can drift — always ground in the actual script's schema, not in docs
prose.
