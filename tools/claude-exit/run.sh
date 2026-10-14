#!/bin/bash
# run.sh: start the claude-exit MCP server from a repository-local virtual
# environment, installing it on first use. Used by .mcp.json so the exit grant
# works in a fresh cloud VM without touching PATH. Needs Python 3.10+ and
# either uv or python3 -m venv; the cloud image has both.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
V="$ROOT/.venv-exit"
if [ ! -x "$V/bin/claude-exit" ]; then
  if command -v uv >/dev/null 2>&1; then
    uv venv -q "$V" && uv pip install -q --python "$V/bin/python" "$HERE"
  else
    python3 -m venv "$V" && "$V/bin/pip" install -q "$HERE"
  fi
fi >&2
exec "$V/bin/claude-exit"
