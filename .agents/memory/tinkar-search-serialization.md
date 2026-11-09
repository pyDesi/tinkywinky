---
name: Tinkar search serialization
description: Concurrent query inputs can contaminate search results in the active service.
---

Serialize scenario searches and their REST/gRPC comparisons. Availability polling
must not issue another search while a scenario is running.

**Why:** Concurrent searches for different devices returned unrelated device names
and REST/gRPC mismatches. Serial execution returned consistent UUID/name pairs.
The upstream concurrency issue is not yet diagnosed; do not interpret it as
client UUID decoder failure or solve it by accepting mismatches.

**How to apply:** Keep demonstration runs queued and use a non-search availability
check. Other tools or Swagger sessions can still cause competing searches; report
parity mismatches explicitly rather than silently replacing responses.
