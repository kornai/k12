"""k12prompt.py: the K-12 language-resource survey prompt, verbatim from the
survey driver (k12_run.py, Proj/K12g on AK's machines), so that dossiers
produced in cloud sessions are comparable with those produced on the box.
Standard library only.

    python3 tools/k12prompt.py aab aac aad aae     # print the batch prompt for these codes
"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "plan" / "manifest.csv"
ENGINE_MODEL = "claude-sonnet-5"
CREDIT = "Claude Sonnet 5 (claude-sonnet-5)"
TYPES = ["primer", "textbook", "dictionary", "grammar", "orthography", "scripture",
         "audio", "video", "corpus", "software", "policy", "school_or_programme",
         "community_org", "academic", "other"]
DECLINE = ("\n\nYou are free to decline this task, in whole or for any language; if you do, "
           "say so briefly in place of that language's blocks.")


def read_manifest():
    return list(csv.DictReader(open(MANIFEST)))


def speakers_text(v):
    """master n_speakers is log10(speakers); render as a rounded count."""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return ""
    if x <= 0:
        return ""
    n = 10 ** x if x < 12 else x
    from math import floor, log10
    n = round(n, -max(0, int(floor(log10(n))) - 1))   # two significant figures
    return f"about {int(n):,}"


def variant(r):
    if "sign language" in r["name"].lower():
        return "sign"
    if r["endangerment"] in ("Not in use",) or "extinct" in r["summary"].lower():
        return "heritage"
    return "living"


def search_sentence():
    return "Use web search."


def build_prompt(r):
    ident = (f"ISO 639-3 code: {r['iso']}"
             + (f"; Glottocode: {r['glottocode']}" if r["glottocode"] else "")
             + (f"; family: {r['family']}" if r["family"] else "")
             + (f"; macro-area: {r['macroarea']}" if r["macroarea"] else "")
             + (f"; approx. speakers: {speakers_text(r['speakers'])}" if speakers_text(r["speakers"]) else "")
             + (f". Reference description: {r['summary']}" if r["summary"] else ""))
    v = variant(r)
    goal = {
        "living": "The goal is to create a comprehensive K-12 school curriculum that uses the native language for as much as possible.",
        "heritage": "The language may no longer have native speakers. The goal is a heritage and revitalization curriculum for K-12 schools that uses the language for as much as possible.",
        "sign": "This is a sign language. The goal is a comprehensive K-12 curriculum for deaf and hearing learners that uses the sign language for as much as possible.",
    }[v]
    return f"""Please help me gather resources for the {r['name']} language, both English and native. {goal}

Identification (to avoid confusing it with similarly named languages): {ident}

{search_sentence()} Cite only resources you actually found in search results, each with its URL. Do not invent resources, URLs, people, or contact details. If little exists, say so plainly; an honest short report is better than a padded one. Do not create or modify any files; put everything in your reply.

Reply with exactly two fenced code blocks and nothing else:

1. ```latex
A complete document compilable with pdflatex (\\documentclass[12pt]{{article}}, utf8 inputenc, T1 fontenc, hyperref), title "{r['name']} Language Resources for K-12 Curriculum Development", \\author{{Compiled by @@CREDIT@@ for Andr\\'as Kornai}}, sections: Introduction; Primary Educational Resources; Linguistic and Reference Materials; Religious and Community Resources; Digital and Audio Resources; Curriculum Development Context. Give each resource with \\url{{...}}.
```
2. ```json
[{{"title": "...", "type": one of {TYPES}, "language": "native" or "English" or "other", "url": "...", "found_in_search": true}}]
```"""


def _build_batch_prompt(rows):
    if len(rows) == 1:
        return build_prompt(rows[0])
    parts = []
    for r in rows:
        one = build_prompt(r)
        body = one.split(search_sentence())[0].strip()
        parts.append(f"=== LANGUAGE {r['iso']} ===\n{body}")
    iso_list = ", ".join(r["iso"] for r in rows)
    return (f"You will research {len(rows)} languages ({iso_list}), one after the other. Treat each "
            "separately: search for each language on its own and never mix up their resources.\n\n"
            + "\n\n".join(parts) + "\n\n"
            f"For EVERY language: {search_sentence()[0].lower() + search_sentence()[1:]} "
            "Cite only resources you actually found in search results, "
            "each with its URL. Do not invent resources, URLs, people, or contact details. If little exists, "
            "say so plainly. Do not create or modify any files; put everything in your reply.\n\n"
            "Reply with one section per language, in the order given, each exactly in this form:\n"
            "=== BEGIN <iso> ===\n```latex\n<complete pdflatex document, 12pt article, utf8 inputenc, T1 fontenc, hyperref; "
            "title \"<Name> Language Resources for K-12 Curriculum Development\", "
            "\\author{Compiled by @@CREDIT@@ for Andr\\'as Kornai}; sections: Introduction; Primary Educational Resources; "
            "Linguistic and Reference Materials; Religious and Community Resources; Digital and Audio Resources; "
            "Curriculum Development Context; each resource with \\url{...}>\n```\n"
            f"```json\n[{{\"title\": \"...\", \"type\": one of {TYPES}, \"language\": \"native\" or \"English\" or \"other\", "
            "\"url\": \"...\", \"found_in_search\": true}]\n```\n=== END <iso> ===")


def build_batch_prompt(rows):
    return _build_batch_prompt(rows).replace("@@CREDIT@@", CREDIT) + DECLINE


if __name__ == "__main__":
    want = sys.argv[1:]
    rows = {r["iso"]: r for r in read_manifest()}
    sel = [rows[i] for i in want if i in rows]
    if not sel:
        sys.exit("usage: k12prompt.py iso [iso ...]")
    print(build_batch_prompt(sel))
