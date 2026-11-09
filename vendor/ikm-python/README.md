# tinkar-python

Python gRPC client for the [Tinkar](https://github.com/ikmdev) terminology service.

`tinkar-python` gives you a small, typed, synchronous client over the three
Tinkar gRPC services. Responses come back as [Pydantic](https://docs.pydantic.dev)
models, errors come back as a single `TinkarError`, and you never touch a
protobuf stub directly.

```python
from tinkar import TinkarClient

with TinkarClient(host="localhost", port=9095) as client:
    response = client.search.query("diabetes")
    for entity in response.results:
        print(entity.fully_qualified_name)
```

## Documentation

| Doc | What it covers |
|-----|----------------|
| [Getting Started](docs/guides/getting-started.md) | Install, connect, first query |
| [Tier 1 — Search & RAG](docs/guides/tier1-search-and-rag.md) | `search`, `entities`, `lidr` |
| [Tier 2 — Knowledge Graph](docs/guides/tier2-knowledge-graph.md) | `knowledge_graph`, coordinates, STAMP |
| [Tier 3 — Admin](docs/guides/tier3-admin.md) | `admin` import / export / reasoner |
| [Error Handling](docs/guides/error-handling.md) | `TinkarError`, error codes, timeouts |
| [API Reference](docs/api-reference.md) | Every method, model, and enum |
| [Contributing](docs/contributing.md) | Proto sync, stub regen, tests, release |

Start at [docs/](docs/index.md) for the full table of contents and a primer on
Tinkar concepts (tiers, STAMP, coordinates).

## Install

```bash
pip install tinkar-python
```

Or for development:

```bash
git clone <repo-url>
cd IKM-python
uv sync
```

Requires Python **3.13+**.

## The three tiers

The client exposes the Tinkar API as three tiers, each aimed at a different
kind of user. They all share one `TinkarClient` and one connection.

```python
with TinkarClient() as client:
    # Tier 1 — Graph RAG: simple, pre-resolved, no coordinate knowledge needed
    client.search.query("diabetes")
    client.entities.get("uuid")
    client.lidr.records("test-kit-uuid")

    # Tier 2 — Knowledge Graph: concept-aware, coordinate overrides
    client.knowledge_graph.semantics("concept-uuid")

    # Tier 3 — Admin: import, export, reasoner
    client.admin.run_reasoner()
```

| Tier | Namespaces | gRPC service | Audience |
|------|-----------|--------------|----------|
| 1 | `search`, `entities`, `lidr` | `IkeGraphRAG` | ML/RAG engineers, data scientists |
| 2 | `knowledge_graph` | `IkeKnowledgeGraph` | Analytics / knowledge-graph engineers |
| 3 | `admin` | `IkeAdmin` | Platform operators, CI/CD |
| — | `tinkar` | `TinkarSearchService` | Raw 1:1 RPC access, incl. entity-graph loading |

## Quick reference

```python
# --- Tier 1: search ---
client.search.query("diabetes")
client.search.concepts("diabetes", max_results=50)
client.search.concepts_by_component("diabetes")          # grouped
client.search.concepts_by_component_alpha("diabetes")
client.search.concepts_by_semantic("diabetes")           # flat, scored
client.search.concepts_by_semantic_alpha("diabetes")
client.search.rebuild_index()

# --- Tier 1: entities ---
client.entities.get("uuid")
client.entities.children("uuid")
client.entities.descendants("uuid")

# --- Tier 1: lidr (lab / diagnostics) ---
client.lidr.records("test-kit-uuid")
client.lidr.result_conformances("lidr-record-uuid")
client.lidr.allowed_results("conformance-uuid")

# --- Tier 2: knowledge graph ---
client.knowledge_graph.semantics("concept-uuid")
client.knowledge_graph.children("concept-uuid")
client.knowledge_graph.descendants("concept-uuid")
client.knowledge_graph.semantics_with_coordinate("concept-uuid", stamp_coordinate_id="...")
client.knowledge_graph.save_stamp_coordinate(allowed_states=AllowedStates.ACTIVE)
client.knowledge_graph.list_stamp_coordinates()
client.knowledge_graph.save_navigation_coordinate(premise_type=PremiseType.STATED)
client.knowledge_graph.list_navigation_coordinates()
client.knowledge_graph.save_language_coordinate(language_preset=LanguagePreset.SPANISH_PREFERRED_NAME)
client.knowledge_graph.list_language_coordinates()

# --- Tier 3: admin ---
client.admin.import_changeset(zip_bytes)
client.admin.export_entities()
client.admin.run_reasoner()

# --- tinkar: raw TinkarSearchService (1:1 RPC wrapper) ---
client.tinkar.inspect_concept("concept-uuid")            # semantics, no coordinates
client.tinkar.load_concept_entity_graph("concept-uuid")  # raw TinkarMsg chronologies
client.tinkar.get_entity_by_public_id("concept-uuid")    # single raw entity
# ...plus 1:1 equivalents of the search/entities/lidr operations
```

## Configuration

```python
client = TinkarClient(
    host="localhost",   # gRPC server host
    port=9095,          # gRPC server port
    timeout=30.0,       # default timeout in seconds (overridable per call)
)
```

Every method takes an optional `timeout` keyword that overrides the client
default:

```python
response = client.search.query("diabetes", timeout=60.0)
```

## Error handling

All failures raise `TinkarError` with a string `code`:

```python
from tinkar import TinkarClient, TinkarError

try:
    response = client.search.query("diabetes")
except TinkarError as e:
    match e.code:
        case "unavailable":
            print("Server is down")
        case "timeout":
            print("Request timed out")
        case _:
            print(f"Error [{e.code}]: {e.message}")
```

See [Error Handling](docs/guides/error-handling.md) for the full list of codes.

## Current limitations

- **Synchronous only.** No asyncio client yet.
- **Insecure channel only.** Connections use `grpc.insecure_channel` — no TLS
  or call credentials. Use on a trusted network or behind a secure proxy.
- **Python 3.13+** required.

## Development

```bash
uv sync                          # install dependencies
uv run pytest -v                 # run tests (against in-process mock servers)
./scripts/generate_proto.sh      # regenerate protobuf stubs from vendored protos
./scripts/sync_protos.sh         # pull latest protos from upstream GitHub (needs gh CLI)
```

See [Contributing](docs/contributing.md) for the proto workflow.

## Proto sources

- `Tinkar.proto` from [ikmdev/tinkar-schema](https://github.com/ikmdev/tinkar-schema) (`main`)
- Service protos from [ikmdev/tinkar-core](https://github.com/ikmdev/tinkar-core/tree/feature/grpcclient) (`feature/grpcclient`)
