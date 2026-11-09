#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export JAVA_HOME="$ROOT/.local/toolchains/jdk27"
SERVICE="$ROOT/.local/upstream/tinkar-service-current"
JAR="$SERVICE/target/tinkar-service-1.0.5-SNAPSHOT.jar"

if [[ ! -x "$JAVA_HOME/bin/java" ]]; then
  echo "Java 27 is missing from $JAVA_HOME. Restore the development toolchain first." >&2
  exit 1
fi
if [[ ! -f "$JAR" ]]; then
  echo "The Tinkar service JAR is missing. Build the current checkout before starting it." >&2
  exit 1
fi

# Keep the downloaded dataset and writable store out of Git and published images.
cd "$SERVICE"
exec "$JAVA_HOME/bin/java" \
  --enable-preview \
  --enable-native-access=ALL-UNNAMED \
  -Xms256m -Xmx3g \
  -jar "$JAR" \
  --server.address=0.0.0.0 \
  --server.port="${PORT:-8099}" \
  --server.servlet.context-path=/tinkar \
  --server.forward-headers-strategy=framework \
  --springdoc.swagger-ui.path=/ \
  --grpc.server.port=9000 \
  --dataset.name=gudidsubset \
  --data.path.parent="$ROOT/.local/tinkar-data" \
  "$@"
