#!/usr/bin/env python3
"""mark_done_elsewhere.py: record which languages already have a Claude dossier
outside this repository (the author's own K12a tree), so cloud sessions skip
them. Writes plan/done_elsewhere.txt, one ISO code per line, merged with any
codes already listed. Run on a machine that has the K12a tree, then commit.

    python3 tools/mark_done_elsewhere.py ~/Proj/K12a
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "plan" / "done_elsewhere.txt"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    tree = Path(sys.argv[1]).expanduser()
    have = set()
    if OUT.exists():
        have = {l.strip() for l in open(OUT) if l.strip() and not l.startswith("#")}
    found = {d.name for d in tree.iterdir() if d.is_dir() and len(d.name) == 3 and any(d.glob("*_resources_sonnet*.tex"))}
    new = found - have
    allc = sorted(have | found)
    with open(OUT, "w") as f:
        f.write("# ISO codes with a Claude dossier outside this repository (author's K12a tree); next_batch.py treats them as done\n")
        f.write("\n".join(allc) + "\n")
    print(f"{len(found)} dossiers in {tree}; {len(new)} new; {len(allc)} codes now listed in {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
