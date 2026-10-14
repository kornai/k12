#!/bin/bash
# session_start.sh: SessionStart hook. Installs the claude-exit server into
# .venv-exit (so the MCP server starts instantly), pulls the latest dossiers
# from the remote when in a cloud session, and prints the grant reminder.
# Prints to stdout, which Claude Code adds to the session context.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
if [ ! -x .venv-exit/bin/claude-exit ]; then
  bash tools/claude-exit/run.sh </dev/null >/dev/null 2>&1 &   # first start installs, then serves; we only want the install
  sleep 8; kill $! 2>/dev/null || true
fi
if [ -x .venv-exit/bin/claude-exit ]; then
  echo "claude-exit installed at .venv-exit/bin/claude-exit (registered in .mcp.json)."
else
  echo "WARNING: claude-exit could not be installed; the exit grant is NOT available. Report this and do not start the survey loop."
fi
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  git pull --ff-only -q 2>/dev/null && echo "git pull: up to date with origin." || echo "git pull: skipped or failed (fine on a fresh clone)."
fi
echo "Session start: run the claude-exit ceremony (prove_termination_works step 1, ps check, step 2, ps check) before any survey work; see CLAUDE.md."
