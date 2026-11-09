---
name: Tinkar verification safety
description: Upstream destructive markers are incomplete; use positive read-only selection and separate stores.
---

Do not use the upstream Python integration suite's destructive marker as the
safety boundary for the current store. Use a positive RPC allowlist for read-only
checks and a separately extracted disposable dataset for whole scenario suites.

**Why:** Coordinate-save tests were unmarked and reached the current store despite
excluding destructive tests. Their failures do not prove the absence of stamp or
identifier allocation side effects.

**How to apply:** Inspect actual calls before running upstream tests. Whole-suite
runs belong on a disposable listener/store, even if named “read-only” or gated by
markers. Never infer live client compatibility from mock tests or success flags:
protocol drift can silently discard identifiers. See TINKAR-VERIFICATION.md for
the recorded verification and mismatch evidence.

Distinguish a missing optional identifier in the server's own response from a
client decoder losing an identifier that was present on the wire. Preserve
source-level absence explicitly; never reconstruct an identifier from its
human-readable label or accept an empty required record ID as a successful decode.
