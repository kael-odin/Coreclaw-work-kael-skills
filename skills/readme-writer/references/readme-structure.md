# README Structure — Worker Template

Extracted from `D:/Coreclaw_Work/scripts/tiktok_2/README.md` (Google Maps
Scraper). This is the canonical section order for a CoreClaw worker README.
Both `README.md` and `README_CN.md` follow this order.

## Section order with purpose

### 1. `## 📍 What is X?` — value prop

One paragraph: what the scraper turns into structured data, the one-click /
automated framing, and the primary use cases in one sentence. End with the
key differentiator vs the official API (e.g. "extends beyond the official
Google Places API limits" / "bypasses the 120-places-per-area cap").

### 2. `### What can you use it for?` — benefit bullets

4-6 bullets, each a **use case** (benefit), not a feature. Pattern:
`**<action>:** <what it lets you do>, <why it matters>.` Examples: build lead
lists, analyze competitors, identify market opportunities, find partnership
targets, automate research workflows.

### 3. `## What data does X extract?` — field table + capabilities

**Emoji two-column table** listing every output field with an emoji + short
label. Mirrors `output_schema.json` exactly. Then a **capability bullets**
list under "to maximize results, X provides": place/contact data,
export-ready formats (the 8), integrations (webhooks, MCP), optional add-ons.

This is the table that sells the data — every column must exist in
`output_schema.json`.

### 4. `## ⬇️ Input` — per-parameter documentation

Each parameter is its own `###` subsection. For each:

- **Header**: `### <Label> (required/optional) -- <field_name>`
- **Purpose**: 1-2 sentences on what the field controls.
- **Usage advice**: what makes good input vs bad. The "recommended examples"
  vs "not recommended examples" pattern from tiktok_2 is the gold standard —
  it teaches by contrast.
- **Format spec**: concrete format (e.g. "city + country", or a Circle/Polygon
  JSON shape). If the parameter has enum values, list them.
- **`#### Examples:`** block where the format is non-trivial.

Required parameters come first. Mark each `(required)` or `(optional)`.

### 5. `## ⬆️ Output` — table view + real JSON + dimension detail

- **Table view**: describes the UI table (overview, group/filter by field).
  One screenshot if available (repo asset only — no fabricated image URLs).
- **`### 🧩 Complete JSON record`**: a **real** JSON array with one complete
  record. Every key is an `output_schema.json` column. Values use
  reserved/example domains and placeholder numbers — realistic but not real
  PII. This is the most-copied block in the README; it must be runnable and
  field-accurate.
- **Per-dimension detail** (`### 📇 Contact and enrichment`, `### 📧 Email
  verification`, `### 📱 Social platform data`, `### ⭐ Ratings and reviews`,
  `### 🧾 Merchant details`): only include sections for dimensions the script
  actually produces. Each expands the relevant subset of the JSON record.

### 6. Advanced usage (if applicable)

`## 📍📡 Using geolocation parameters for more accurate targeting` etc. —
only if the script supports advanced params. Each gets `#### Example 1:`,
`#### Example 2:` numbered concrete examples with full JSON. Skip entirely
if the script has no such params.

### 7. `## ❓ FAQ` — grounded Q&A

6-10 questions. Each answer grounded in the script's real behavior, not
marketing. Standard set (adapt to the script):
- How does X work?
- What are the drawbacks of the official API? (only if the script wraps one)
- Can I scrape from multiple locations?
- How can I improve scrape speed? → answer cites real concurrency.fields
  behavior if applicable
- Can X extract reviews?
- How can I output each review as a separate row? (if the script supports it)
- Can I integrate X with other applications? → webhooks, MCP, Make/Zapier
- Can I use X as an API? → point to platform API docs (real link)
- Is scraping X data legal? → generic, non-prescriptive

### 8. `## Feedback` — close

One-line invitation to report issues. No fabricated issue-tracker link unless
the repo actually has one.

## Anti-patterns (remove on sight)

- Feature lists in implementation language ("uses Playwright, asyncio") —
  readers want benefits, not stack.
- "Status: WIP" without saying what works.
- Fragment input examples (`{"keyword": "..."}` with no other required
  fields) — incomplete, not runnable.
- Output JSON stub (`{"title": "...", "phone": "..."}`) that omits real
  columns — hides the actual field set.
- Fabricated image URLs / demo links.
- Translated headings where the Chinese heading doesn't match the English
  structure (breaks anchor symmetry).
