# Project-managed Tinkar Python client

Based on `https://github.com/icaglobal/ikm-python` revision
`c7e3170db2efe3f8928c4db0ce409d393eae787c` (package `tinkar-python` 0.1.0).
The original author metadata and README are retained. The upstream project's
license declaration is still pending; this vendored copy is for this project's
integration work, not a claim of a new license or publication approval.

Unlike the ignored reference checkout, **this directory is committed**. The
root `pyproject.toml`/`uv.lock` install it as the local `tinkar-python` dependency,
and the default smoke checker selects this source explicitly.

## Coordinated schemas

The five `proto/` files are copied from the build inputs of the active
`icaglobal/tinkar-service` revision
`3f9e6a865eb752464df63af5bb82de319aafd656`, with schema 1.43.5-SNAPSHOT.
The smoke command independently compares their wire contracts with server
reflection before sending application queries. Version labels alone do not
guarantee that mutable snapshots match.

SHA-256 of the vendored source inputs:

| File | SHA-256 |
| --- | --- |
| Tinkar.proto | `7d535bfbee44251fa9b6df6cf5cd3318ea51dda45d4f1a49eca521a00af1e046` |
| ike_types.proto | `920a41ffc5eee78c7aa01c85504afae6bb46bb61d6b1ba4a61fad1fc3fdd9054` |
| ike_graph_rag.proto | `793d4d9e41c3d641264f34afbf67eaf5446c74330255c889b1ba845ab3026da6` |
| ike_knowledge_graph.proto | `58f433e067551ee1612748eeacee48bee26a09618f5007148a0486dc874a18d8` |
| ike_admin.proto | `4bca58acd216ce13eca555d0f26e33defc84892974177abe6064b3885446911c` |

Regenerate stubs from the workspace root:

```bash
UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --locked
.pythonlibs/bin/python scripts/generate-tinkar-client.py
.pythonlibs/bin/python -m pytest scripts/tests -q
bash scripts/check-tinkar.sh
```

The generator uses the root lockfile's grpcio-tools 1.81.0 / protobuf 6.33.5.
The client's grpcio minimum is 1.81.0, matching its generated runtime checks.
The regression suite checks regeneration byte-for-byte.

## Compatibility changes

- Public IDs decode unsigned UUID words and legacy UUID strings, preserving
  multiple identifiers and rejecting odd, malformed, conflicting, empty required,
  or unresolved sequence-only IDs with `TinkarError(code="protocol_error")`.
- Every concept, semantic and STAMP converter uses the same decoder.
- Coordinate overrides and saved settings encode their UUIDs as current PublicId
  messages at the current field numbers; module-priority order is preserved.
  Saved-coordinate references and response IDs are also PublicId messages.
  Saved/list response models retain `.id` as the first UUID for compatibility and
  expose `.public_id` for the complete set; a missing required ID raises an error.
- `client.tinkar.*` is a facade: search/hierarchy/LIDR/index operations route to
  IkeGraphRAG; inspection and raw entity operations route to IkeKnowledgeGraph,
  with the correct request message. Nothing targets the removed search service.
- Grouped/semantic search models preserve their new PublicId messages and matching
  semantic IDs. Removed store-local nids are `None`, not fabricated zeros.
- Response timestamps and semantic named fields are available to callers.
- The active server omits pattern PublicIds in semantic inspection responses.
  `pattern_public_id=None` explicitly means unavailable from the server; it is
  not reconstructed from a name.
- Legacy unary import/export/reasoner wrappers now fail **before sending** with
  `unsupported_operation`: the server replaced them with streaming job/event
  APIs. Their current generated stubs are available, but a typed administrative
  streaming wrapper is separate work. A stream must not be mistaken for a
  completed successful job.

The old upstream mock suite and pinned reference checkout remain separate from
this vendored package. Project regression tests live in `scripts/tests`; they
use current wire types and recorded RPC paths, not the removed mock service.
All live checks in the default smoke command are read-only. Full upstream suites
still require a disposable store, regardless of their test markers.

Verification for this repair: 46 project regression tests passed; the strict
default smoke exited 0 against the running public subset. No live write tests
were performed.
