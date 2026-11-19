# Coordinate capability and example safety fixes

These are reviewable upstream patches, not edits to the running service. Do not
apply them to, restart, or experiment with the current store as part of validation.

## Source revisions

| Patch | Repository | Base revision |
| --- | --- | --- |
| `tinkar-service.patch` | https://github.com/icaglobal/tinkar-service | `3f9e6a865eb752464df63af5bb82de319aafd656` |
| `ikm-python.patch` | https://github.com/icaglobal/ikm-python | `c7e3170db2efe3f8928c4db0ce409d393eae787c` |

Apply each patch to its own clean checkout of the stated revision with
`git apply --check <absolute-patch-path>` followed by `git apply <absolute-patch-path>`.
Use separate checkouts named `.local/upstream/tinkar-coordinate-fix` and
`.local/upstream/ikm-python-coordinate-fix`. Do not overwrite the active checkout
or combine snapshot dependencies from older experiments.

## Behavior

- The registry ID must identify a real, non-canceled pattern with two string
  fields, not a concept stub or an allocated ID without an entity.
- Missing/wrong registry schema returns REST **412**, code
  `COORDINATE_REGISTRY_UNAVAILABLE`, and gRPC **FAILED_PRECONDITION** with the same
  code and a reason. This happens before coordinate construction or transactions.
- Save, list, and lookup all use non-allocating capability checks. Listing never
  initializes schema. Do not assume list calls in an unpatched service are safe.
- The service deliberately does **not** invent production registry field meanings
  or silently migrate an arbitrary dataset.
- All four live Python coordinate-save examples require
  `integration_destructive`. Only the explicit capability error is skippable:
  UNKNOWN, 500, transport, and serialization errors still fail.
- Python examples validate fixture presence. `TINKAR_TEST_CONCEPT_ID` and
  `TINKAR_TEST_PARENT_ID` can select verified fixtures instead of assuming
  SNOMED lung-disease concepts exist in every dataset.
- `scripts/coordinate_safety.py` audits pytest collection for unmarked coordinate
  writes, including save methods passed to wrappers. It is defense in depth,
  **not** a replacement for the positive RPC allowlist in `tinkar_smoke.py`.

## Repeatable validation

Use the toolchain, Maven settings, and isolated Maven cache in
[TINKAR-SETUP.md](../../TINKAR-SETUP.md). Build the **patched isolated** Java
checkout, not the active service:

```bash
ROOT="$PWD"
export JAVA_HOME="$ROOT/.local/toolchains/jdk27"
export PATH="$JAVA_HOME/bin:$PATH"
cd "$ROOT/.local/upstream/tinkar-coordinate-fix"
./mvnw -ntp \
  -s "$ROOT/.local/conversation-workspace/files/attached_assets/settings_1791675610138.xml" \
  -Dmaven.repo.local="$ROOT/.local/m2-tinkar-current" \
  -Dmaven.javadoc.skip=true package
cd "$ROOT"
.pythonlibs/bin/python -m pytest scripts/tests -q
bash scripts/check-tinkar-coordinates.sh
```

The coordinate runner requires the checksum-pinned public archive at
`.local/tinkar-verification/public-gudid.zip` (same public URL and checksum as
`scripts/check-tinkar-disposable.sh`). It does not fetch restricted data.
Every invocation extracts **two fresh stores**, refuses occupied disposable
ports 8100/9001, and stops its own server on exit. Ports 8099/9000 and the current
dataset are never used. Failed stores are retained, ignored, and never reused.

1. An opt-in Java test opens the first fresh public store. It verifies all nine
   unsupported save/list/lookup operations refuse before starting transactions;
   entity counts, write sequence and registry ID presence remain unchanged.
2. **Only in that disposable test**, two-string-field test registry patterns are
   explicitly provisioned. Save/list/lookup/idempotency are checked for stamp,
   navigation and language. These minimal test patterns are not an authoritative
   registry ontology and are not installed by the service or shipped public data.
3. A persistence error is injected after stamp allocation. Cancellation must
   leave no visible new coordinate; retained entity changes are reported. This
   demonstrates why cancellation must not be described as a physical rollback.
4. A second, unprovisioned fresh extraction verifies actual REST/gRPC capability
   errors, exact semantic-ID parity and state/time filtering for a discovered
   public device. Optional absent SNOMED fixtures are explicitly reported.
5. Patched Python examples run only on the second disposable listener. Supported
   hierarchy examples pass; saves skip with the capability reason. The separate
   known client UUID-decoding issue is not hidden or patched here.

Evidence is written under ignored `generated-artifacts/tinkar-coordinate-checks/`.
No browser workflow or currently running service needs to be restarted.
For a transport-handler-only change after the Java store checks have passed,
`bash scripts/check-tinkar-coordinates.sh --transport-only` verifies a new,
unprovisioned extraction without rerunning or reusing the earlier Java store.
