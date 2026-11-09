#!/usr/bin/env bash
# Internal-only, read-only smoke check. Never runs upstream scenario suites.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$ROOT/.pythonlibs/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "Python verification dependencies missing. Run: UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --locked" >&2
  exit 1
fi
exec "$PYTHON" "$ROOT/scripts/tinkar_smoke.py" "$@"
