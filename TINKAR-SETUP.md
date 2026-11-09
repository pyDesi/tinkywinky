# Tinkar development setup

## Running service

The managed workflow **artifacts/api-server: Tinkar** runs the real upstream Java service.
Open `/tinkar/` in the project preview to reach Swagger.

- Swagger: `/tinkar/swagger-ui/index.html`
- OpenAPI: `/tinkar/api-docs`
- REST base path: `/tinkar/api`
- Internal REST port: 8099, supplied through the workflow's `PORT`
- Internal gRPC port: 9000
- Dataset: public `gudidsubset`, downloaded automatically without Nexus credentials

The existing Express API server is unchanged and still owns `/api`.
The gRPC listener was checked inside the workspace; external gRPC forwarding has not
been configured or verified.

## Active source and Java

This run uses `icaglobal/tinkar-service` revision `3f9e6a8` from November 9, 2026,
with current public Nexus snapshots and an official Eclipse Temurin Java 27
early-access toolchain.

Development locations:

- Active service source: `.local/upstream/tinkar-service-current`
- JDK: `.local/toolchains/jdk27`
- Isolated Maven repository: `.local/m2-tinkar-current`
- Downloaded dataset and writable store: `.local/tinkar-data`
- Startup script: `scripts/run-tinkar.sh`

The earlier checkout under `tinkar-service/` is not the active service.
Using a fresh checkout and isolated Maven repository avoids mixing the earlier
source-built SNAPSHOT overrides with newer published dependencies.

## Rebuild in this workspace

Run from the workspace root:

```bash
ROOT="$PWD"
export JAVA_HOME="$ROOT/.local/toolchains/jdk27"
export PATH="$JAVA_HOME/bin:$PATH"
cd "$ROOT/.local/upstream/tinkar-service-current"
./mvnw -ntp \
  -s "$ROOT/.local/conversation-workspace/files/attached_assets/settings_1791675610138.xml" \
  -Dmaven.repo.local="$ROOT/.local/m2-tinkar-current" \
  -Dmaven.test.skip=true \
  -Dmaven.javadoc.skip=true \
  package
```

Then restart **artifacts/api-server: Tinkar**. The startup script fails explicitly
if the JDK or service JAR is missing.

## Checks performed

- Swagger and OpenAPI returned HTTP 200 through the preview proxy.
- The OpenAPI document listed 44 paths.
- A read-only concept search for `device`, limited to three results, returned
  real records from the dataset.
- The internal gRPC health check returned `SERVING`.
- Swagger rendered correctly in the preview.

The upstream Java suite and Patrick's Python/DeX examples have now been run.
See [TINKAR-VERIFICATION.md](TINKAR-VERIFICATION.md) for the results, explicit
protocol mismatches, safety incident, and repeatable read-only/disposable checks.
The Java suite passes; the Python client is not fully compatible with this server.

## Development-only limitations

The JDK, source checkout, Maven cache, and dataset are under `.local`, excluded
from Git and published images. They remain available in this workspace, but a
fresh fork or clean environment needs a bootstrap step to restore them.

This is not a publishing configuration. No production hardening or authentication
configuration was added. Use the public test dataset and do not expose this
setup as a production service without addressing those items.
