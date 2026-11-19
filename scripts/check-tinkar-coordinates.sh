#!/usr/bin/env bash
# Coordinates ONLY: never opens the current store and never restarts its workflow.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ "$#" == 0 || ( "$#" == 1 && "$1" == "--transport-only" ) ]] || {
  echo "Usage: $0 [--transport-only]"; exit 2;
}
SERVICE="$ROOT/.local/upstream/tinkar-coordinate-fix"
CLIENT="$ROOT/.local/upstream/ikm-python-coordinate-fix"
export JAVA_HOME="$ROOT/.local/toolchains/jdk27"
export PATH="$ROOT/.pythonlibs/bin:$JAVA_HOME/bin:$PATH"
export PYTHONPATH="$ROOT/scripts:$CLIENT/src"
ARCHIVE="$ROOT/.local/tinkar-verification/public-gudid.zip"
[[ -f "$SERVICE/target/tinkar-service-1.0.5-SNAPSHOT.jar" ]]
[[ -f "$CLIENT/tests/integration/test_knowledge_graph.py" ]]
echo "b40f3e5720874446281bfeb7fc2c8cb205459045a9b604cab91b2241a5c2b36c  $ARCHIVE" | sha256sum --check
python - <<'PY'
import socket
for port in (8100, 9001):
    with socket.socket() as s:
        s.bind(("127.0.0.1", port))
PY
mkdir -p "$ROOT/generated-artifacts/tinkar-coordinate-checks"
fresh_store() {
  local run
  run="$(mktemp -d "$ROOT/.local/tinkar-verification/run-XXXXXX")"
  mkdir "$run/data"
  unzip -q "$ARCHIVE" -d "$run/data"
  mv "$run/data/gudid" "$run/data/gudidsubset"
  printf 'fresh-public-gudid\n' > "$run/DISPOSABLE"
  printf '%s' "$run"
}
# This test first verifies zero-write capability refusals, then provisions
# explicitly TEST-ONLY registry patterns to exercise the supported code path.
JAVA_RUN="not run (transport-only)"
LOG="$(mktemp -d "$ROOT/generated-artifacts/tinkar-coordinate-checks/run-XXXXXX")"
echo "Coordinate evidence: $LOG"
if [[ "$#" == 0 ]]; then
  JAVA_RUN="$(fresh_store)"
  (
    cd "$SERVICE"
    ./mvnw -ntp \
      -s "$ROOT/.local/conversation-workspace/files/attached_assets/settings_1791675610138.xml" \
      -Dmaven.repo.local="$ROOT/.local/m2-tinkar-current" \
      -Dtest=PublicSubsetCoordinateTest -Dcoordinate.disposable.root="$JAVA_RUN" \
      -Dmaven.javadoc.skip=true test
  ) > "$LOG/public-store.log" 2>&1
fi
# A second NEW extraction, never the store the Java tests wrote to.
HTTP_RUN="$(fresh_store)"
PID=""
cleanup() {
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  echo "Disposable Java store: $JAVA_RUN"
  echo "Disposable transport store: $HTTP_RUN"
  echo "Evidence: $LOG"
}
trap cleanup EXIT
cd "$HTTP_RUN"
java --enable-preview --enable-native-access=ALL-UNNAMED -Xms256m -Xmx3g \
  -jar "$SERVICE/target/tinkar-service-1.0.5-SNAPSHOT.jar" \
  --server.address=127.0.0.1 --server.port=8100 --server.servlet.context-path=/tinkar \
  --grpc.server.address=127.0.0.1 --grpc.server.port=9001 \
  --dataset.name=gudidsubset --data.path.parent="$HTTP_RUN/data" > "$LOG/server.log" 2>&1 &
PID=$!
READY=false
for _ in $(seq 1 120); do
  kill -0 "$PID" 2>/dev/null || { tail -60 "$LOG/server.log"; exit 1; }
  if curl -fsS --max-time 2 http://127.0.0.1:8100/tinkar/api-docs >/dev/null 2>&1; then
    READY=true; break
  fi
  sleep 1
done
[[ "$READY" == true ]] || { echo "Disposable startup timed out"; exit 1; }
export TINKAR_COORDINATE_DISPOSABLE="$HTTP_RUN" TINKAR_COORDINATE_PID="$PID"
python "$ROOT/scripts/tinkar_coordinate_checks.py" > "$LOG/transports.log" 2>&1
# Collect/audit before deselection: every save in the upstream integration tree
# must carry its write marker, including examples passed through wrappers.
TINKAR_INTEGRATION=1 TINKAR_HOST=127.0.0.1 TINKAR_PORT=9001 \
  python -m pytest "$CLIENT/tests/integration" -p coordinate_safety \
    --collect-only -m 'not integration_destructive' -q > "$LOG/collection.log" 2>&1
# Only the coordinate examples; the known client UUID bug is a separate task.
# Supported ID-independent navigation tests run; writes skip with capability reasons.
TINKAR_INTEGRATION=1 TINKAR_INTEGRATION_DESTRUCTIVE=1 TINKAR_HOST=127.0.0.1 TINKAR_PORT=9001 \
  TINKAR_TEST_CONCEPT_ID="$(cat "$HTTP_RUN/concept-id")" \
  TINKAR_TEST_PARENT_ID=f816dfb5-cc6d-5334-a0b4-c6e844689a30 \
  python -m pytest "$CLIENT/tests/integration/test_knowledge_graph.py" \
    -p coordinate_safety -k 'not TestSemantics' -q -rs > "$LOG/python-examples.log" 2>&1
# With no dataset overrides, the old optional SNOMED fixtures must skip by name,
# not fail with an obscure entity error or trigger a restricted-data download.
env -u TINKAR_TEST_CONCEPT_ID -u TINKAR_TEST_PARENT_ID \
  TINKAR_INTEGRATION=1 TINKAR_INTEGRATION_DESTRUCTIVE=0 TINKAR_HOST=127.0.0.1 TINKAR_PORT=9001 \
  python -m pytest "$CLIENT/tests/integration/test_knowledge_graph.py" \
    -p coordinate_safety -k 'TestSemantics or TestKGChildren or TestKGDescendants' \
    -q -rs > "$LOG/optional-fixtures.log" 2>&1
cat "$LOG/transports.log" "$LOG/python-examples.log" "$LOG/optional-fixtures.log"
