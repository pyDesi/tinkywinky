# REST and Python verification

Verified 2026-11-09 against the public GUDID subset, not production.
The original upstream baselines are retained below. The default checker now uses
a project-managed compatible client; it does not add missing server DeX features.

## Project-managed Python compatibility repair

The client is now committed under `vendor/ikm-python`, installed from the root
lockfile, and selected by the default smoke command. See
`vendor/ikm-python/PROVENANCE.md` for the coordinated schemas and local changes.

- Refreshed schemas/stubs match the active reflected server contracts.
- UUID bit pairs, multiple UUIDs and all search/entity/navigation STAMP IDs survive
  response conversion. Empty required, malformed and unresolved sequence IDs fail
  explicitly instead of looking like successful empty records.
- Coordinate override and saved-setting UUIDs use the current PublicId fields.
  Saved-coordinate response IDs, list entries and saved-coordinate references
  also use PublicId messages. The legacy singular `.id` keeps the first UUID;
  `.public_id` preserves every UUID. Serialization was tested with mocks only,
  not saves against the current store.
- `client.tinkar.*` routes to IkeGraphRAG or IkeKnowledgeGraph. Inspection and both
  raw chronology operations return real identifiers through the default live check.
- Grouped/semantic result IDs, matching semantic IDs, response timestamps and
  named semantic fields are preserved. Removed store-local nids are unavailable,
  not fabricated.
- The server omits pattern IDs from semantic responses; the client explicitly
  returns `pattern_public_id=None` in that case. Pattern names are not used to
  guess identifiers.
- Generated stubs require grpcio 1.81.0; the declared client minimum now matches.
- Obsolete unary admin import/export/reasoner wrappers fail before sending because
  the current server uses streaming jobs. Typed streaming support is separate work.

`bash scripts/check-tinkar.sh` now exits **0**, without an allow-mismatch flag.
The read-only smoke compares actual IDs, stamps and semantic fields with REST and
server reflection. It never downgrades a protocol failure to monitoring success.
All live checks for this repair were read-only; settings serialization and index/
admin routing were tested only with mocks, not writes against the current store.

## Results

| Check | Result |
| --- | --- |
| Upstream Java `./mvnw … test` | **322 passed**, 0 failures/errors/skips |
| Unmodified Python client mock tests | **60 passed**, 35 integration tests deselected |
| Smoke helper unit tests (initial baseline) | **11 passed** |
| Project smoke/client regression tests | **46 passed** |
| Current-store read-only REST vs live-schema gRPC | **Passed** |
| Unmodified Python client compatibility (historical baseline) | **Failed**; silent UUID loss and removed RPC service |
| Project-managed Python compatibility | **Passed**; strict default smoke exits 0 |
| Upstream DeX REST scenarios, disposable dataset | **151 pass, 14 fail, 7 skip** |
| Upstream gRPC scenarios, disposable dataset | **90 pass, 33 fail, 5 skip** |
| Python integration suite, disposable dataset | **6 pass, 21 fail, 3 skip, 5 deselected** |
| gRPC health, Swagger and proxied REST | `SERVING`, Swagger rendered, REST HTTP 200 |

The REST scenario script reports TOTAL=173 although pass+fail+skip=172: it
increments an extra counter in the missing-Albumin branch. These are the script's
unmodified results, not an adjusted success rate.

### Representative records

`bash scripts/check-tinkar.sh` compares the UUIDs and fully qualified names of
three results each for `device`, `albumin`, and `catheter`. It also compares:

- Entity lookup for a discovered device.
- 35 children and 35 descendants of public GUDID parent
  `f816dfb5-cc6d-5334-a0b4-c6e844689a30`, via both GraphRAG and KnowledgeGraph.
- Semantic UUIDs, pattern names, formatted field values and stamp timestamps.
  The current store's first device was `0fa170be-da88-5c75-a1c2-b9606a00ad27`,
  **Tyto Device Tyto Device**, with 10 semantics, including GS1 `07290016672183`.
  A fresh archive's search ordering selected **Vapocoolant Device**, with 6
  semantics. Selection is dynamic; parity is between transports on the same store,
  not between independent Lucene indexes.

## Original upstream compatibility problems

These describe the unmodified reference client, not the project-managed default.

1. **Public IDs silently disappear in Python.** Current `Tinkar.proto` writes
   `PublicId.uuid_bits` (field 2), two unsigned 64-bit halves per UUID. The client
   only knows `repeated string uuids` (field 1). Its search calls return `success=True`
   and real names but `public_id=[]`; entity and semantic IDs and the
   search/entity stamp's status/author/module/path IDs are also lost.
   The server still accepts string `uuids` in requests. The smoke checker decodes
   reflected responses in its own descriptor pool solely to compare them with REST;
   **the upstream Python client/stubs are not patched or replaced**.
2. **Removed legacy service.** `client.tinkar.*` targets
   `dev.ikm.tinkar.service.TinkarSearchService`, no longer registered by this server.
   Calls return `UNIMPLEMENTED: Method not found`. Current search is on
   `IkeGraphRAG`; entity graph, entity-by-public-ID and inspection are on
   `IkeKnowledgeGraph`. A successful mock suite does not prove live compatibility.
3. **Coordinate override wire changes.** Current `position_path_id`, `module_ids`,
   `excluded_module_ids`, and `module_priority_ids` are PublicId messages on fields
   9–12, replacing the client's string fields 3–5 and 7. Old client override fields
   can be ignored as unknown wire fields. The upstream shell examples send
   strings, so grpcurl fails to parse these calls against the reflected schema
   (`expecting start of JSON object`). Counts alone cannot validate filtering.
4. **Generated dependency minimum is understated.** Client `pyproject.toml` allows
   grpcio 1.80.0, but committed gRPC stubs require **1.81.0** and reject 1.80.0
   at import. Verification pins grpcio/tools/reflection/health 1.81.0 and
   protobuf 6.33.5. With that generator, the upstream proto-staleness test passes.
   Java gRPC 1.78.0 vs Python gRPC 1.81.0 is not itself a transport failure.
5. The client also predates additive `named_fields`/`created_at` responses and
   the broader current service surface. Python semantic positional fields still
   decode, but new named fields are unavailable through its models.

### Dataset and scenario gaps

- The Java README says Java 25, but this checkout compiles for Java 27.
  The existing Temurin 27 toolchain was used.
- The Python integration tests hard-code chronic lung/disease-of-lung UUIDs
  `f6978e15-e169-58c2-a93d-eac1511974da` and
  `2716e9c0-b454-5973-8d2e-4c068897b244`; they are absent from this subset.
  The shell coordinate tests likewise expect absent diabetes-insipidus/albumin
  fixtures. These failures do not mean device search/navigation is broken.
- The REST DeX script found **11 of 12** scenario devices. Albumin Gen.2 was absent;
  four respiratory-device LIDR queries had no records and were skipped.
- Two REST failures are unconditional assertions in the upstream script:
  “multi-device comparison NOT IMPLEMENTED” and “tabular DeX export NOT IMPLEMENTED.”
  They are not independently exercised endpoint failures. The remaining 12
  REST failures come from coordinate-fixture assumptions.
- The gRPC script's device-ID extractor assumes `public_id.uuids`, so it silently
  bypasses some device details even when search returns results in `uuid_bits`.
  Its 33 failures combine absent coordinate fixtures, old override JSON and
  coordinate-save errors. Do not treat its passing count as complete coverage.
- Saving stamp/navigation/language coordinates fails with missing registry
  PatternEntity errors on this dataset (REST 500, gRPC UNKNOWN). This is distinct
  from the client protocol mismatch and reproduces on the disposable store.

## Safety incident and isolation

An initial integration invocation on port 9000 excluded the upstream
`integration_destructive` marker. **That marker is incomplete:** four coordinate
save tests are not marked destructive, so those write attempts reached the
current store. They failed because registry patterns were absent, before the
coordinate semantic was saved; transaction cancellation was invoked. There is no
pre-run store fingerprint, so stamp/identifier allocation side effects cannot be
ruled out. Do not interpret this verification as a guarantee that the current
store is byte-for-byte unchanged. No restoration or deletion of current data was
attempted.

All subsequent full scenario runs used a **fresh, separately extracted public
archive** on loopback REST 8100 and gRPC 9001, under
`.local/tinkar-verification/run-*`, never a copy of the running store. The
read-only smoke command uses an RPC allowlist and never imports upstream tests.
The Java tests use mocks or ephemeral memory-only stores loaded from the public
IKE starter set. No live import/create/edit/delete/reasoner/admin scenario was
run against the current store. Import/export/reasoner live tests were excluded
from the smoke run; no valid changeset fixture was invented.

The disposable process was stopped after the run. Disposable data is retained,
ignored, and never reused as the input to a later run. No production data,
restricted Nexus credentials, external gRPC forwarding or publishing was used.

## Repeat the checks

Prerequisites: the active service setup in [TINKAR-SETUP.md](TINKAR-SETUP.md)
and Python 3.13. The default check does **not** require an ignored Python checkout:

```bash
UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --locked
bash scripts/check-tinkar.sh
```

Smoke exits **0** only when fully compatible; failures return nonzero.
The old `--allow-known-client-mismatch` escape hatch has been removed.
This repair does not change the separate server-side missing-registry-pattern
problem in coordinate saves or the missing DeX fixture/device scenarios.

The smoke checker pins internal gRPC to 9000 (current) or 9001 (disposable).
REST defaults to `http://localhost:8099/tinkar/api`. It does not expose any ports.

Unit tests, without a running service:

```bash
.pythonlibs/bin/python -m pytest scripts/tests -q
```

The pinned ignored reference checkout remains useful for reproducing the historical
upstream baseline and scenario suites. It is not the default dependency. Its old
mock tests target an obsolete service, so they are not a compatibility gate for
the updated package. Project tests exercise current wire types, legacy routing,
malformed IDs, coordinate serialization and deterministic stub regeneration.

Full upstream examples must use the disposable runner, **not pytest's incomplete
destructive marker as a safety boundary**:

```bash
# grpcurl 1.9.4 was used; 1.9.3's dependency was blocked by the package firewall.
GOBIN="$PWD/.local/bin" go install github.com/fullstorydev/grpcurl/cmd/grpcurl@v1.9.4
bash scripts/check-tinkar-disposable.sh
```

It refuses occupied ports, validates the pinned public archive checksum, extracts
a new store for every run, binds loopback only, runs all three scenario suites and
smoke, stops its own server on exit, and returns nonzero for failed checks.
Expected current result: **exit 1**, with separate logs/exit codes for each suite.
Allow roughly 3 GiB Java heap per service plus overhead; the 1200 MiB trial was
insufficient. The first archive download is about 390 MiB (about 837 MiB extracted).
Generated evidence stays under ignored `generated-artifacts/tinkar-checks/`.

### Exact inputs and evidence

- Service: `icaglobal/tinkar-service` `3f9e6a865eb752464df63af5bb82de319aafd656`,
  version 1.0.5-SNAPSHOT, schema 1.43.5-SNAPSHOT, core 1.127.7-SNAPSHOT.
- Python: `icaglobal/ikm-python` `c7e3170db2efe3f8928c4db0ce409d393eae787c`,
  package `tinkar-python` 0.1.0.
- Public archive: `gudid-20250804-subset+1.0.0-20250919.155530-1-reasoned-sa.zip`;
  SHA-256 `b40f3e5720874446281bfeb7fc2c8cb205459045a9b604cab91b2241a5c2b36c`.
- Java results: `generated-artifacts/tinkar-checks/java-tests.log` and upstream
  `target/surefire-reports/`.
- Python mock results: `generated-artifacts/tinkar-checks/python-unit.log`.
- Current read-only parity: `generated-artifacts/tinkar-checks/smoke.log`.
- Disposable results: `generated-artifacts/tinkar-checks/run-n9kddB/`
  (`smoke.log`, `rest-scenarios.log`, `grpc-scenarios.log`,
  `python-integration.log`, `server.log`).

To rerun the Java suite, use the same Java, settings and isolated Maven repository
as the build command in TINKAR-SETUP.md, replacing `package` and the test-skip
flags with `test`. Do not mix older local source-built SNAPSHOT overrides.
