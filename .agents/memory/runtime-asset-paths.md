---
name: Runtime asset paths
description: Publishing and managed development workflows launch the API from different directories.
---

Do not resolve workspace assets by assuming the API process starts in its artifact
directory. Resolve paths from the runtime module's location instead.

**Why:** Managed development workflows started in the artifact directory, but
publishing started the production bundle from the workspace root. Relative
working-directory traversal caused an import-time missing-file crash even though
the asset was included and compilation succeeded.

**How to apply:** Verify production startup from both locations when changing
file-backed configuration or subprocess entry points. Remember that bundled
modules resolve relative to the bundle, not the original source directory.
