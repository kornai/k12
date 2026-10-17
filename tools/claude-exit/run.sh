#!/bin/bash
# run.sh: start the claude-exit MCP server from a repository-local virtual
# environment, installing it on first use. Used by .mcp.json so the exit grant
# works in a fresh cloud VM without touching PATH. Needs Python 3.10+ and
# either uv or python3 -m venv; the cloud image has both.
#
# 2026-10-17: Claude Code launches MCP servers before the SessionStart hook
# runs, so this script and the hook can race to create the venv; the loser
# used to die and the MCP connection closed. Now the install is serialised
# with flock (Linux; macOS has no flock binary and skips it) and done into a
# temporary directory that is renamed into place only when complete.
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
ROOT=$(cd "$HERE/../.." && pwd)
V="$ROOT/.venv-exit"
LOCK="$ROOT/.venv-exit.lock"

install() {
  local T="$V.tmp.$$"
  rm -rf "$T"
  if command -v uv >/dev/null 2>&1; then
    uv venv -q "$T" && uv pip install -q --python "$T/bin/python" "$HERE"
  else
    python3 -m venv "$T" && "$T/bin/pip" install -q "$HERE"
  fi
  # uv venvs record their own path; recreate on the final path if a rename would break them
  if [ -x "$T/bin/claude-exit" ] && [ ! -x "$V/bin/claude-exit" ]; then
    if command -v uv >/dev/null 2>&1; then
      rm -rf "$T"; uv venv -q "$V" && uv pip install -q --python "$V/bin/python" "$HERE"
    else
      mv "$T" "$V"
    fi
  fi
  rm -rf "$T" 2>/dev/null || true
}

if [ ! -x "$V/bin/claude-exit" ]; then
  if command -v flock >/dev/null 2>&1; then
    exec 9>"$LOCK"
    flock -w 300 9                      # wait for a concurrent installer (the hook) rather than racing it
    [ -x "$V/bin/claude-exit" ] || install
    flock -u 9
  else
    install
  fi
fi >&2
exec "$V/bin/claude-exit"
