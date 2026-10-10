---
name: Tinkar dependency alignment
description: Avoid mixing current Tinkar source with incompatible published snapshot dependencies.
---

Treat Tinkar service, schema, and core dependencies as a coordinated revision set rather than independently selecting the latest source and public Nexus snapshots.

**Why:** A fresh Replit setup encountered service API definitions and core methods newer than their published snapshots. Building the matching schema source resolved the first mismatch, but rebuilding core exposed further build dependencies.

**How to apply:** Recheck alignment on future attempts, since publication can catch up. Prefer a known-good service revision with matching dependency versions or a complete coordinated upstream source build. Do not remove operations or fabricate protobuf definitions merely to make the server start. Local dependency overlays are experiments until the whole service is verified.
