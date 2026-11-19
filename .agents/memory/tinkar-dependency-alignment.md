---
name: Tinkar dependency alignment
description: Avoid mixing current Tinkar source with incompatible published snapshot dependencies.
---

Treat Tinkar service, schema, and core dependencies as a coordinated revision set rather than independently selecting the latest source and public Nexus snapshots.

**Why:** Source and public snapshots have fallen out of alignment in both directions: service source initially expected unpublished APIs, while a later retry of the old checkout resolved a newer BOM with renamed modules. Locally installed source-built snapshots can also mask newer remote artifacts despite identical version strings.

**How to apply:** Recheck current source and snapshot metadata rather than assuming an earlier build blocker persists. Use an isolated Maven repository for source-build experiments so local SNAPSHOT overrides do not contaminate a clean public-dependency build. Prefer a known-good service revision with matching dependency versions or a complete coordinated upstream source build. Do not remove operations or fabricate protobuf definitions merely to make the server start. Local dependency overlays are experiments until the whole service is verified.

Keep HTTP exception handlers controller-local unless an OpenAPI dependency upgrade
is part of the work.

**Why:** The upstream parent can supply a newer Spring framework than the pinned
Springdoc library expects. Swagger may appear healthy until adding global
controller advice activates inspection that calls a removed
`ControllerAdviceBean(Object)` constructor. A local handler avoids turning a
domain-error fix into an unrelated dependency migration.

**How to apply:** After adding HTTP error handling, request the OpenAPI document
as well as the affected endpoint. Do not assume successful compilation or a
healthy application startup proves Swagger compatibility.
