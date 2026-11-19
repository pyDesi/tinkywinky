---
name: Coordinate dataset capabilities
description: Missing coordinate registries are a dataset capability, not permission to invent schema.
---

Prefer explicit, non-allocating capability refusals when saved-coordinate registry
patterns are missing or have the wrong schema. Do not silently provision registry
patterns or concept stubs while serving a save or list request.

**Why:** A registry is also used as a semantic pattern; a concept stub cannot
satisfy that role. Automatically inventing field meanings in shared terminology
would be an undocumented dataset migration. Minimal test-only patterns are useful
for checking persistence but are not an authoritative ontology.

**How to apply:** Keep provisioning confined to explicitly disposable tests unless
a future request supplies an approved registry schema/migration. Report unsupported
datasets clearly on both transports and skip only that explicit capability error
in examples. Cancellation after stamp allocation is not a physical rollback;
measure side effects instead of claiming no changes from a failed save.
