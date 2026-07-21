# Grounding Rules — No Fabrication

The README must be a faithful description of the actual script. These rules
make "no fabrication" operational.

## Rule 1 — Read before writing

Read all of these before writing any prose:
- `input_schema.json` — field names, types, editors, required, defaults, enums
- `output_schema.json` — every output column
- `main.py` / `index.js` — scraping logic, hard caps, enhancement toggles,
  concurrency config
- any existing partial README — extract verifiable facts, discard claims
  you can't confirm from the code

If any file is missing or unreadable, stop and say so. Do not write a README
from assumption.

## Rule 2 — Field name fidelity

Every field name in the README (input or output) must exist verbatim in the
schema JSON. Field names are case-sensitive. `place_categories` in the schema
must appear as `place_categories` in the README, never `placeCategories` or
`Place Categories`.

In running text, Markdown may render `place_categories` with backticks; in
JSON examples, use the exact key.

## Rule 3 — Capability claims must cite the code

Any claim like "up to 300 results per URL" or "bypasses the 120-place cap"
must trace to a line in the script or a platform doc. If the script enforces
no such cap, don't invent one. If the platform's hard cap is documented,
link the doc and quote the number.

When unsure, hedge honestly: "supports a large number of categories" rather
than fabricating "supports up to 100 categories" — unless the script or a doc
says 100.

## Rule 4 — Links: real or none

Allowed links:
- Platform docs (the canonical URLs in SKILL.md Sources)
- Official upstream APIs the script wraps, when the link is canonical and
  stable (e.g. Google Places API docs)
- Repo-internal assets (`![view](assets/view.png)`)
- Repo-internal anchors (relative `#section`)

Forbidden:
- Invented `https://example.org/some-page` that you haven't verified resolves
- Demo / playground URLs unless the repo actually deploys one
- Issue-tracker links unless the repo has issues enabled and you know the URL
- OSS image URLs unless they're from a real, existing CoreClaw asset path

If you need a placeholder, omit the link. A bare description is better than a
broken URL.

## Rule 5 — Input examples are complete and runnable

An input example is a full JSON object the user can paste into the run input
and get a successful run. It includes:
- every required field, with a real value
- optional fields shown when they illustrate a format
- the exact nesting (top-level vs under `input` vs `parameters.custom` —
  match the platform's actual run shape)

Never show a fragment like `{"keyword": "pizza"}` if the script also requires
`base_location`. Show both.

For array inputs, show a 2-3 element array so the format is unambiguous.

## Rule 6 — Output examples are real-shaped

The output JSON example must:
- be an array (the platform returns result rows as an array)
- contain every `output_schema.json` column as a key
- use realistic values: reserved domains (`example.com`,
  `example-dental.test`), placeholder phones (`+1 512-555-0101`), plausible
  numbers (`review_count: 842`, not `999999`)
- show nullable/empty fields honestly (`email_2: ""`, `email_2_status: ""`)
  — don't trim them, they teach the user what to expect

This is the most-copied block in any worker README. Getting it wrong means
every downstream user's parser breaks.

## Rule 7 — Enhancement toggles match the script

If the script has enhancement toggles (contact enrichment, email
verification, reviews, etc.), document each with its default (on/off), what
it costs (free add-on vs runtime), and what it returns. Don't invent
toggles the script doesn't have. Don't omit toggles it does have.

## Rule 8 — Honest capability range

State what the script does NOT do, when it matters. "Does not support
historic Popular Times" or "reviews are capped at N per place" — grounded in
the code. Honesty here prevents support tickets and bad reviews.

## Grounding sheet template

Before writing, fill this (inline notes, not a deliverable):

```
scraping_logic: <source hit, query shape, per-request limit, platform cap>
input_fields:
  - name: keyword, type: string, editor: text, required: yes, default: "", enum: []
  - name: base_location, type: string, ...
  - name: place_categories, type: array, ...
output_fields: <every output_schema column + type>
enhancement_toggles:
  - name: <toggle>, default: on, cost: free/runtime, returns: <fields>
concurrency: fields=[], remove_fields=[], limits=[], legacy_b=
hard_caps: <e.g. 120 places per area, 300 per URL> — source: <code line or doc>
```

Every README claim should be traceable to a line in this sheet.
