# Concurrency Suggestions — Improvement Layer

The richest improvement vein for CoreClaw workers. Source: `coreclaw-cli-audit/references/concurrency-rules.md`
(2026-07 platform HTML). This file turns those rules into audit suggestions.

## Decision order (platform runtime)

```
1. concurrency.fields non-empty  → split by fields (new rules)
2. else b non-empty              → split by b (legacy)
3. else                          → whole custom object = single task
4. both present                  → fields wins, b ignored
```

A worker with an array input but NO `concurrency.fields` and NO `b` runs as a
**single task** — the whole input serially. That is the #1 throughput miss.

## Suggestion matrix

### S-THROUGHPUT — array input without concurrency.fields

**Detect**: `input_schema.json` `properties` has a field of `type: "array"`
that represents a list of independent work units (keywords, place_ids,
google_maps_urls, search_terms), and `concurrency.fields` is absent or empty.

**Impact**: high. The platform cannot parallelize; one task does all the work
sequentially. Adding `concurrency.fields: ["keywords"]` lets the platform
split N keywords into N parallel tasks.

**Suggest**:
```json
"concurrency": {
  "fields": ["keywords"]
}
```
Each `keywords` entry becomes its own task. For primitive items the generated
task keeps `"keywords": ["pizza"]` (one-item array).

**Source**: concurrency-rules.md §Decision Order, §Split Result Shape.

### S-COST — precharge explosion without limits

**Detect**: a split field's items can each produce many billable results (e.g.
a `google_maps_urls` list where each URL may return hundreds of places), and
`concurrency.limits` is absent.

**Impact**: high cost. Precharge = sum of per-item billing counts, uncapped.
A 500-URL list × 200 results each = 100k precharge.

**Suggest**: a `limits` rule capping precharge per item. `limits` does NOT
change task count or task content — only the precharged (billing) count per
item.
```json
"concurrency": {
  "fields": ["google_maps_urls"],
  "limits": [
    { "field": "google_maps_urls", "max": 120 }
  ]
}
```
Per-item precharge capped at 120. `regex` optional (matches item values
recursively, not keys); omitted = matches every item. Multiple matching limits
→ smallest `max` wins.

**Source**: concurrency-rules.md §limits.

### S-LEGACY — still using `b` for splitting

**Detect**: `input_schema.json` has `b` (legacy) and no `concurrency.fields`.

**Impact**: medium. `b` is compatibility-only; `concurrency.fields` wins when
both exist. New workers should use `fields`.

**Suggest**: migrate `b` → `concurrency.fields`. The split semantics are
equivalent for a single field (the field key is kept as a one-item array for
primitives under `fields`, which is the new shape).

**Source**: concurrency-rules.md §Decision Order, §Split Result Shape.

### S-REMOVE — split field leaking into downstream custom

**Detect**: a split field's values are internal (IDs, internal tokens) and
should not appear in downstream task custom objects, but `concurrency.remove_fields`
is absent.

**Impact**: low-medium. Without `remove_fields`, disabled fields are retained
as `[""]` in generated task custom objects when the all-fields fallback is
active.

**Suggest**:
```json
"concurrency": {
  "fields": ["keywords", "place_ids"],
  "remove_fields": ["place_ids"]
}
```
When preferred fields (`fields - remove_fields`) are active and have meaningful
values, every `remove_fields` key is **deleted** from generated task custom
objects (not retained as `[""]`).

**Caveat**: `remove_fields` is only applied when preferred fields are active.
If the fallback all-fields path is active (preferred empty or all-empty),
`remove_fields` is NOT applied and those fields may participate in splitting.

**Source**: concurrency-rules.md §Active Field Selection.

### S-MIXED — mixed object/primitive items in a split field

**Detect**: a `concurrency.fields` entry whose array mixes objects and
primitives.

**Impact**: `error` (runtime). `field [X] must not mix object and primitive
items`.

**Suggest**: split into two fields, or normalize all items to one type.
Object items merge their keys into the task custom object; primitive items
wrap as one-item arrays — the two cannot coexist in one field.

**Source**: concurrency-rules.md §Element Type Matrix.

### S-NESTED — nested arrays as split items

**Detect**: a `concurrency.fields` array contains nested arrays.

**Impact**: `error` (runtime). `item at index N in [X] must be an object or
primitive value`.

**Suggest**: flatten, or wrap each inner array as an object.

**Source**: concurrency-rules.md §Element Type Matrix.

## Field selection rules (for schema validation findings)

These are `error`/`warn` findings, not suggestions, but listed here for
completeness:

- Each non-empty `concurrency.fields` item must match a `properties[*].name`.
- Each `concurrency.fields` property must have `type: "array"`.
- Each non-empty `concurrency.remove_fields` item must be a member of
  `concurrency.fields`.
- `limits.field` must be a member of `concurrency.fields` (it is a concurrency
  field, NOT a billing-quantity field like `max_results`).
- Object item must not contain a key equal to the concurrency field name →
  `item at index N in [X] must not override concurrency field`.

## Pagination trap (P2) — unrelated to concurrency but bites result correctness

Upstream list endpoints use 1-based page index (`page_index = offset/limit +
1`), not absolute row offset. A worker or caller doing `offset += limit` to
skip rows gets wrong pages — duplicate or missing rows, no error. The MCP
server has a compensation layer; raw REST callers must align `offset` to a
`limit` multiple. If a concurrency-split worker shows duplicate or missing
rows across tasks, check whether the per-task offset logic misuses `offset`.

Source: memory `[[coreclaw-pagination-bug-fix-2026-07-15]]`.
