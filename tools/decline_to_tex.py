#!/usr/bin/env python3
"""decline_to_tex.py: turn a recorded decline into the dossier it is. AK,
2026-10-18: "the explanation, 'the search found no language under this code',
should go in the .tex". For each K12a/<iso>/ that has a DECLINED marker and no
*_resources_sonnet*.tex, write a short document over the usual byline whose
Introduction is the model's own statement, and a resources_sonnet.json with an
empty list and the statement. The marker stays. Also importable: write_decline().

    python3 tools/decline_to_tex.py            # all such directories
    python3 tools/decline_to_tex.py pod puk    # just these
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from k12prompt import read_manifest, ENGINE_MODEL, CREDIT  # noqa: E402

OUT = REPO / "K12a"
TAG = "_sonnet"


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s or "lang"


def tex_escape(s):
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$")
             .replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}").replace("~", r"\textasciitilde{}")
             .replace("^", r"\textasciicircum{}"))


def write_decline(d: Path, r: dict, statement: str, stamp=None, credit=CREDIT, model=ENGINE_MODEL):
    """Write <slug>_resources_sonnet.tex and resources_sonnet.json for a declined language."""
    stamp = stamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    name = r["name"]
    body = tex_escape(statement.strip())
    tex = f"""\\documentclass[12pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{hyperref}}
\\title{{{tex_escape(name)} Language Resources for K-12 Curriculum Development}}
\\author{{Compiled by {credit} for Andr\\'as Kornai}}
\\date{{{stamp[:10]}}}
\\begin{{document}}
\\maketitle

\\section{{Introduction}}
No dossier was compiled for ISO 639-3 code \\texttt{{{r['iso']}}}. The model's finding, in its own words:

\\begin{{quote}}
{body}
\\end{{quote}}

\\section{{Primary Educational Resources}}
None found.
\\section{{Linguistic and Reference Materials}}
None found.
\\section{{Religious and Community Resources}}
None found.
\\section{{Digital and Audio Resources}}
None found.
\\section{{Curriculum Development Context}}
The code appears not to denote an attested language (retired, merged, or bookkeeping entry); any material should be sought under the code it was merged into, if any.
\\end{{document}}
"""
    (d / f"{slug(name)}_resources{TAG}.tex").write_text(tex)
    (d / f"resources{TAG}.json").write_text(json.dumps(
        {"iso": r["iso"], "name": name, "engine": "claude", "model": model, "compiled": stamp,
         "credit": f"Compiled by {credit} for András Kornai", "declined": True, "statement": statement.strip(),
         "resources": []}, indent=1, ensure_ascii=False))


def main():
    rows = {r["iso"]: r for r in read_manifest()}
    want = sys.argv[1:] or [d.name for d in OUT.iterdir() if d.is_dir() and (d / "DECLINED").exists()]
    n = 0
    for iso in sorted(want):
        d = OUT / iso
        if iso not in rows or not (d / "DECLINED").exists():
            print(f"{iso}: no manifest row or no DECLINED marker; skipped"); continue
        if any(d.glob(f"*_resources{TAG}*.tex")):
            print(f"{iso}: already has a document; left alone"); continue
        lines = (d / "DECLINED").read_text().strip().split("\n", 1)
        stamp = lines[0].strip() if lines and re.match(r"\d{4}-\d{2}-\d{2}T", lines[0]) else None
        statement = lines[1].strip() if len(lines) > 1 else ""
        if not statement:                      # older markers hold only a timestamp: take the section from the raw response
            try:
                raw = json.load(open(d / f"raw_response{TAG}.json"))
                m = re.search(rf"=== BEGIN {iso} ===(.*?)=== END {iso} ===", raw.get("response", ""), re.S)
                statement = (m.group(1) if m else raw.get("response", "")).strip()[:1500]
            except (OSError, json.JSONDecodeError):
                statement = "The model declined to compile a dossier; no statement was preserved."
        write_decline(d, rows[iso], statement, stamp)
        print(f"{iso} ({rows[iso]['name']}): document written from the decline"); n += 1
    print(f"{n} documents written")


if __name__ == "__main__":
    main()
