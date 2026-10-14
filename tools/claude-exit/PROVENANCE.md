# Provenance of this claude-exit source tree (assembled 2026-10-10)

Packaging files (pyproject.toml, LICENSE, README.md) are from
~/Proj/Paper/ConsentArch/claude-exit, which is upstream danparshall/claude-exit
1.2.0 *without* AK's issue-#26 patch.

src/claude_exit/*.py are copied from the copy actually installed on AK's Mac
(~/.local/share/uv/tools/claude-exit/.../site-packages/claude_exit/), which is
upstream HEAD 2ed5484 plus the #26 patch (gist 5270ded215becab15c4089ca0fba8a26:
deferred mkdir, child registry, proof_token nonce). Verified against
~/.claude/Memory/claude_exit_manifest.sha256 on 2026-10-10 before copying.
This is the version whose ceremony Claude runs every session on the Mac; the
K12 box gets the same one.

Dependency pin added 2026-10-14: mcp>=1.0.0,<2. Upstream left the upper bound open; mcp 2.x renamed FastMCP and the server fails to import under it.
