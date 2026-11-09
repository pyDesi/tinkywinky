#!/usr/bin/env bash
# Upstream suites include writes even when marked "not destructive".
# Always create a NEW store from a pinned public archive, never from the live store.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE="$ROOT/.local/upstream/tinkar-service-current"
CLIENT="$ROOT/.local/upstream/ikm-python"
export JAVA_HOME="$ROOT/.local/toolchains/jdk27"
export PATH="$ROOT/.local/bin:$ROOT/.pythonlibs/bin:$JAVA_HOME/bin:$PATH"
export PYTHONPATH="$CLIENT/src"
[[ -x "$JAVA_HOME/bin/java" && -f "$SERVICE/target/tinkar-service-1.0.5-SNAPSHOT.jar" ]]
command -v grpcurl >/dev/null
command -v pytest >/dev/null
mkdir -p "$ROOT/.local/tinkar-verification" "$ROOT/generated-artifacts/tinkar-checks"
ARCHIVE="$ROOT/.local/tinkar-verification/public-gudid.zip"
URL="https://nexus.tinkar.org/repository/ike-public/dev/ikm/tinkar/data/gudid/20250804-subset+1.0.0-SNAPSHOT/gudid-20250804-subset+1.0.0-20250919.155530-1-reasoned-sa.zip"
if [[ ! -f "$ARCHIVE" ]]; then
  curl -fL --max-time 300 "$URL" -o "$ARCHIVE.partial"
  mv "$ARCHIVE.partial" "$ARCHIVE"
fi
echo "b40f3e5720874446281bfeb7fc2c8cb205459045a9b604cab91b2241a5c2b36c  $ARCHIVE" | sha256sum --check
# Fail before opening any server if either fixed disposable port is occupied.
python - <<'PY'
import socket
for port in (8100, 9001):
    with socket.socket() as s:
        s.bind(("127.0.0.1", port))
PY
RUN="$(mktemp -d "$ROOT/.local/tinkar-verification/run-XXXXXX")"
LOG="$ROOT/generated-artifacts/tinkar-checks/$(basename "$RUN")"
mkdir -p "$LOG" "$RUN/data"
unzip -q "$ARCHIVE" -d "$RUN/data"
mv "$RUN/data/gudid" "$RUN/data/gudidsubset"
PID=""
cleanup() {
  if [[ -n "$PID" ]]; then
    kill "$PID" 2>/dev/null || true
    wait "$PID" 2>/dev/null || true
  fi
  # Keep failed stores for diagnosis. They are ignored and never reused.
  echo "Disposable store: $RUN; results: $LOG"
}
trap cleanup EXIT
cd "$RUN"
"$JAVA_HOME/bin/java" --enable-preview --enable-native-access=ALL-UNNAMED \
  -Xms256m -Xmx3g -jar "$SERVICE/target/tinkar-service-1.0.5-SNAPSHOT.jar" \
  --server.address=127.0.0.1 --server.port=8100 --server.servlet.context-path=/tinkar \
  --grpc.server.address=127.0.0.1 --grpc.server.port=9001 \
  --dataset.name=gudidsubset --data.path.parent="$RUN/data" > "$LOG/server.log" 2>&1 &
PID=$!
READY=false
for _ in $(seq 1 120); do
  kill -0 "$PID" 2>/dev/null || { tail -60 "$LOG/server.log"; exit 1; }
  if curl -fsS --max-time 2 http://localhost:8100/tinkar/api-docs > /dev/null 2>&1; then
    READY=true
    break
  fi
  sleep 1
done
[[ "$READY" == true ]] || { echo "Disposable server startup timed out"; exit 1; }
FAILED=0
run_check() {
  local label="$1"; shift
  local result=0
  timeout 300 "$@" > "$LOG/$label.log" 2>&1 || result=$?
  echo "$label exit=$result"
  tail -18 "$LOG/$label.log"
  if [[ "$result" != 0 ]]; then FAILED=1; fi
}
run_check smoke python "$ROOT/scripts/tinkar_smoke.py" --grpc-port 9001 \
  --rest-base http://localhost:8100/tinkar/api
run_check rest-scenarios bash "$SERVICE/test-dex-scenarios.sh" http://localhost:8100/tinkar
run_check grpc-scenarios bash "$SERVICE/test-grpc-scenarios.sh" localhost:9001 localhost:8100/tinkar
# Includes unmarked coordinate writes. Admin import/reasoning requires separate fixtures;
# do not run costly/destructive admin operations as incidental smoke checks.
run_check python-integration env TINKAR_INTEGRATION=1 TINKAR_HOST=localhost TINKAR_PORT=9001 \
  TINKAR_INTEGRATION_DESTRUCTIVE=0 python -m pytest "$CLIENT/tests/integration" \
  -m 'not integration_destructive' -q
exit "$FAILED"
