# Ranges for cloud sessions

State of 2026-10-17: 5,891 languages have a Claude dossier (box a–s plus the
first cloud session's t–wep, merged into main from branch
`claude/modest-galileo-8q1to7`); 2,235 are pending, scattered gaps in a–s
(box failures and the stretch its 2,000-language limit left) plus most of
u–z. `plan/done_elsewhere.txt` lists what the box did, so the picker skips
it. Ranges below are cut at actual pending codes, about 400 pending each;
start one session per range with "Run the survey loop on range <lo-hi>":

| range | pending | status |
|---|---|---|
| adq-plw | 400 | |
| ply-rug | 400 | |
| rui-sry | 400 | |
| srz-xiy | 400 | |
| xjb-ysn | 400 | |
| yso-zzj | 235 | |

A session that finishes reports "NOTHING PENDING" and can take another range.
Check with `python3 tools/next_batch.py --range <lo-hi> --list`.

History: 2026-10-14 split was box to `szz`, cloud t–z in four ranges; the
box run stopped at its limit in the n's and the first cloud session did
t–wep before its credit window closed.
