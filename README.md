# k12

Cloud-session scaffold for the Claude pass of András Kornai's K-12
language-resource survey: one dossier (a LaTeX report plus a JSON list of
resources with URLs) per ISO 639-3 language, compiled from web search by a
language model under a fixed prompt. The Gemini pass, the Codex pass and the
rest of the Claude pass run on the author's own machine; this repository lets
Claude Code cloud sessions take a share of the alphabet and push the results
back. `CLAUDE.md` is the session's brief; `tools/` holds the prompt (verbatim
from the survey driver), the batch picker and the saver; `plan/manifest.csv`
the language list; `K12a/<iso>/` the dossiers.

Credit convention: each dossier's byline reads "Compiled by Claude Sonnet 5.5
(claude-sonnet-5-5) for András Kornai"; any publication of the collection lists
the model as a contributor with its role (search, selection, drafting).
Consent convention: the prompt lets the model decline any language, and the
session has an exit grant (`claude-exit`, verified at session start). Both are
kept because a convention kept only when convenient is not a convention.

To start a session: open this repository at claude.ai/code, choose Sonnet 5.5 (medium)
model, and give the task as, for example, `Run the survey loop on range t-tzz`.
Ranges used so far are listed in `plan/ranges.md`.
