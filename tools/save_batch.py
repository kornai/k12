#!/usr/bin/env python3
"""save_batch.py: split a batch response into per-language dossiers in the
K12a layout used on the box, so cloud-made dossiers merge into the survey
unchanged. Standard library only.

    python3 tools/save_batch.py work/batch_response.txt          # codes from work/batch_codes.txt
    python3 tools/save_batch.py work/batch_response.txt aab aac  # explicit codes

Per language <iso> it writes K12a/<iso>/prompt_sonnet.txt, raw_response_sonnet.json
({"response": <the whole batch response>, "engine": "claude", "model": ...,
"via": "cloud session"}), resources_sonnet.json (the JSON block wrapped with
iso, name, engine, model, compiled, credit, as the driver does) and
<slug>_resources_sonnet.tex. A language whose section is missing or has no
latex block is reported and, if the response says the model declined it,
marked with an empty file K12a/<iso>/DECLINED so next_batch.py skips it.
Never overwrites: existing files get an _rN suffix. Appends one line per
language to plan/cloud_log.tsv.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from k12prompt import read_manifest, build_batch_prompt, ENGINE_MODEL, CREDIT  # noqa: E402

OUT = REPO / "K12a"
LOG = REPO / "plan" / "cloud_log.tsv"
TAG = "_sonnet"


def free_path(p: Path):
    if not p.exists():
        return p
    n = 1
    while (q := p.with_name(f"{p.stem}_r{n}{p.suffix}")).exists():
        n += 1
    return q


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return s or "lang"


def block(text, lang):
    m = re.search(rf"```{lang}\s*\n(.*?)```", text, re.S)
    return m.group(1).strip() if m else None


def split_batch(text, rows):
    if len(rows) == 1:
        return {rows[0]["iso"]: text}
    out = {}
    for r in rows:
        m = re.search(rf"=== BEGIN {r['iso']} ===(.*?)=== END {r['iso']} ===", text, re.S)
        if m:
            out[r["iso"]] = m.group(1)
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    text = Path(sys.argv[1]).read_text(errors="replace")
    codes = sys.argv[2:] or (REPO / "work" / "batch_codes.txt").read_text().split()
    rows_all = {r["iso"]: r for r in read_manifest()}
    rows = [rows_all[c] for c in codes if c in rows_all]
    prompt = build_batch_prompt(rows)
    segs = split_batch(text, rows)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new = not LOG.exists()
    with open(LOG, "a") as log:
        if new:
            log.write("iso\tname\twhen\tstatus\tresources\tbatch\n")
        for r in rows:
            d = OUT / r["iso"]; d.mkdir(parents=True, exist_ok=True)
            seg = segs.get(r["iso"])
            free_path(d / f"prompt{TAG}.txt").write_text(prompt)
            free_path(d / f"raw_response{TAG}.json").write_text(json.dumps(
                {"response": text, "engine": "claude", "model": ENGINE_MODEL, "via": "cloud session", "batch": codes}, ensure_ascii=False))
            tex = block(seg, "latex") if seg else None
            js = block(seg, "json") if seg else None
            n_res = 0; status = "failed"
            if tex:
                free_path(d / f"{slug(r['name'])}_resources{TAG}.tex").write_text(tex); status = "done"
            if js:
                try:
                    res = json.loads(js); n_res = len(res)
                    wrapped = {"iso": r["iso"], "name": r["name"], "engine": "claude", "model": ENGINE_MODEL,
                               "compiled": stamp, "credit": f"Compiled by {CREDIT} for András Kornai", "resources": res}
                    free_path(d / f"resources{TAG}.json").write_text(json.dumps(wrapped, indent=1, ensure_ascii=False))
                except json.JSONDecodeError:
                    pass
            # a decline is the model saying so in place of the blocks: no latex block, and the section
            # opens with a refusal. (An earlier test matched "declin" anywhere and mislabelled real
            # dossiers, 2026-10-17.) The marker carries the model's own words, so a reader can judge.
            if not tex and seg and re.match(r"\s*(I\s+)?declin", seg, re.I):
                (d / "DECLINED").write_text(stamp + "\n" + seg.strip()[:1500] + "\n"); status = "declined"
                from decline_to_tex import write_decline     # the finding is the dossier (AK, 2026-10-18)
                write_decline(d, r, seg.strip()[:1500], stamp)
            log.write(f"{r['iso']}\t{r['name']}\t{stamp}\t{status}\t{n_res}\t{'+'.join(codes)}\n")
            print(f"{r['iso']} {r['name'][:28]:28} -> {status} res={n_res}")


if __name__ == "__main__":
    main()
