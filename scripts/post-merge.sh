#!/bin/bash
set -e
pnpm install --frozen-lockfile
UV_PROJECT_ENVIRONMENT=.pythonlibs uv sync --locked
pnpm --filter db push
