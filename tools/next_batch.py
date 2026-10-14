#!/usr/bin/env python3
"""next_batch.py: pick the next pending languages in a range and write the
batch prompt. A language counts as done when K12a/<iso>/ holds a
*_resources_sonnet*.tex (the same criterion as the survey driver), so the
repository itself is the state and several sessions on disjoint ranges never
collide. Standard library only.

    python3 tools/next_batch.py --range t-tz            # 4 codes, prompt in work/batch_prompt.txt
    python3 tools/next_batch.py --range u-wzz --n 4 --list   # just list what is pending

Range syntax: two codes joined by '-', inclusive on both ends, compared as
strings (so 't-tzz' is every code starting with t).
"""
import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
from k12prompt import read_manifest, build_batch_prompt  # noqa: E402

OUT = REPO / "K12a"
WORK = REPO / "work"


def done(iso):
    d = OUT / iso
    return d.is_dir() and any(d.glob("*_resources_sonnet*.tex"))


def declined(iso):
    return (OUT / iso / "DECLINED").exists()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", required=True, help="lo-hi, inclusive, e.g. t-tzz")
    ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--list", action="store_true", help="list pending codes in the range and exit")
    a = ap.parse_args()
    lo, hi = a.range.split("-")
    rows = [r for r in read_manifest() if lo <= r["iso"] <= hi]
    pending = [r for r in rows if not done(r["iso"]) and not declined(r["iso"])]
    if a.list:
        print(f"range {a.range}: {len(rows)} codes, {len(pending)} pending, {len(rows) - len(pending)} done or declined")
        print(" ".join(r["iso"] for r in pending))
        return
    batch = pending[: a.n]
    if not batch:
        print("NOTHING PENDING in range", a.range)
        return
    WORK.mkdir(exist_ok=True)
    (WORK / "batch_codes.txt").write_text(" ".join(r["iso"] for r in batch) + "\n")
    (WORK / "batch_prompt.txt").write_text(build_batch_prompt(batch))
    print(f"batch: {' '.join(r['iso'] + ' (' + r['name'] + ')' for r in batch)}")
    print(f"prompt written to work/batch_prompt.txt ({len(pending)} pending in range before this batch)")


if __name__ == "__main__":
    main()
