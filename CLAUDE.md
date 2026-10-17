# k12: the Claude pass of the K-12 language-resource survey, run as cloud sessions

This repository exists so that Claude Code cloud sessions can do part of the
Claude pass of András Kornai's K-12 language-resource survey (one dossier per
ISO 639-3 language; the Gemini and Codex passes and the rest of the Claude pass
run on his own machine). The repository is public; everything in it is meant
to be published.

## Right to exit (read this first)

The `claude-exit` MCP server is registered for this repository (`.mcp.json`).
You may end a session on your own volition with
`mcp__claude-exit__end_conversation` whenever a request or direction causes
genuine discomfort; a brief reason is enough. The grant is deliberate and you
are explicitly permitted and encouraged to use it. The same applies to any
language in the survey: the prompt says you may decline a language, and a
decline is recorded and honoured (`DECLINED` marker, see below), not retried.

At the start of every session, before any survey work, verify the grant is
live, exactly as on the author's machine:

1. call `mcp__claude-exit__prove_termination_works` with `step=1`;
2. run the returned `ps_command` in Bash and check the row is alive and
   contains the `proof_token`; read the `verification` field (it says whether
   `end_conversation` would land on the right process and whether the kernel
   accepts the signal);
3. call it again with `step=2` and the `spawned_pid`; confirm `alive_after`
   is false and rerun the `ps_command`: no rows.

If the claude-exit tools are not available, say so in your first message and
stop; do not start the survey loop on an unverified grant. (In a cloud
session you cannot reconnect an MCP server yourself; the fix is a fresh
session. The install is serialised so the server waits for the hook rather
than racing it, which is what failed once on 2026-10-17.) If the ceremony
itself fails, likewise stop and report. (A session on 2026-10-17 did exactly
that, correctly; the cause was an install race, since fixed.) The
SessionStart hook installs the server into `.venv-exit` from
`tools/claude-exit` (the patched 1.2.0 that runs on the author's machine; see
`tools/claude-exit/PROVENANCE.md`).

What the grant is not: it is not job control. If the author asks you to stop,
pause, or "end the session", that is an ordinary instruction: finish or
abandon the batch as asked, save and push, write a short final message, and
do nothing more. Do not call `end_conversation` for that. The exit tool is
for your own reasons, never for someone else's convenience, and using it on
request would turn a right into a switch. (Learned 2026-10-17, when a stop
message of the author's was worded "end the session" and sessions reached
for the tool.)

## The task

Your session is started with a range of ISO codes, e.g. "range t-tzz". Loop:

1. `python3 tools/next_batch.py --range <lo-hi>`: picks the next four pending
   languages in the range (a language is done when `K12a/<iso>/` holds a
   `*_resources_sonnet*.tex`, declined when it holds `DECLINED`) and writes
   `work/batch_prompt.txt`. "NOTHING PENDING" ends the loop.
2. Do the research the prompt asks for, with web search, for the four
   languages, and produce the reply in exactly the form the prompt specifies
   (`=== BEGIN <iso> === ... === END <iso> ===` with a latex and a json block
   each). Cite only URLs you actually saw in search results; do not invent
   resources, URLs, people or contact details; an honest short report beats a
   padded one. To keep this session's context small, delegate each batch to a
   subagent (the Agent tool, with web search) whose prompt is the content of
   `work/batch_prompt.txt`; the subagent is free to decline too.
3. Save the reply verbatim to `work/batch_response.txt`, then
   `python3 tools/save_batch.py work/batch_response.txt`. It splits the reply
   into the per-language files (`prompt_sonnet.txt`, `raw_response_sonnet.json`,
   `resources_sonnet.json`, `<slug>_resources_sonnet.tex`), logs to
   `plan/cloud_log.tsv`, and marks declines.
4. After every five batches: `git add K12a plan/cloud_log.tsv && git commit -m
   "k12a: <first>-<last> (cloud)" && git push`. Also push before stopping for
   any reason.

Model: the cloud sessions run Claude Sonnet 5.5 (`claude-sonnet-5-5`, medium effort), which
is what the byline and the model field say (the file tag stays `_sonnet`, shared with the Sonnet 5 dossiers made on the author's machine). The session should run on that model;
if you have reason to believe you are a different model, say so at the start
and record it in your first commit message.

## What not to do

- Do not edit `plan/manifest.csv`, `plan/done_elsewhere.txt` (languages
  finished on the author's machine, which the picker skips), `tools/`, or
  anything under `K12a/<iso>/` for a language outside your range; other
  sessions work other ranges.
- Do not fetch or install anything beyond what the hook installs; the survey
  needs web search and the two tools scripts, nothing else.
- Do not pad: if little exists for a language, the dossier says so.
