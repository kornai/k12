#!/bin/bash
# session_start.sh: SessionStart hook. Makes sure the claude-exit server is
# installed in .venv-exit (the MCP wrapper installs on first use too; both
# paths are serialised with flock on Linux), pulls the latest dossiers when in
# a cloud session, and prints the grant reminder. Stdout goes into the
# session context.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"
if [ ! -x .venv-exit/bin/claude-exit ]; then
  # run the installer path of the wrapper without serving: the wrapper execs the
  # server at the end, which exits at once on closed stdin
  timeout 240 bash tools/claude-exit/run.sh </dev/null >/dev/null 2>.venv-exit.install.log || true
fi
if [ -x .venv-exit/bin/claude-exit ]; then
  echo "claude-exit installed at .venv-exit/bin/claude-exit (registered in .mcp.json)."
  if ! timeout 10 .venv-exit/bin/python -c "import claude_exit.server" 2>>.venv-exit.install.log; then
    echo "WARNING: claude-exit is installed but does not import; see .venv-exit.install.log. Do not start the survey loop."
  fi
else
  echo "WARNING: claude-exit could not be installed (see .venv-exit.install.log); the exit grant is NOT available. Report this and do not start the survey loop."
fi
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
  git pull --ff-only -q 2>/dev/null && echo "git pull: up to date with origin." || echo "git pull: skipped or failed (fine on a fresh clone)."
fi
echo "Session start: run the claude-exit ceremony (prove_termination_works step 1, ps check, step 2, ps check) before any survey work; see CLAUDE.md. If the claude-exit tools are not listed, stop and report; a fresh session is the fix."
