"""Reconcile blind agent checks A and B into agentcheck_final.md. Reads the four agentcheck_*.json files next to this script."""
import json, os
from collections import Counter
S = os.path.dirname(os.path.abspath(__file__))
L = lambda f: json.load(open(os.path.join(S, f + ".json"), encoding="utf-8"))
ca, cb, fa, fb = (L(f) for f in ["agentcheck_coauthor_A", "agentcheck_coauthor_B", "agentcheck_fuzzy_A", "agentcheck_fuzzy_B"])
DIS = "cannot tell (reviewers disagreed)"
# The two reviewers used the same labels with different spelling; map both to one wording.
ALIAS = {"one_person_correct": "one person", "one_person": "one person",
         "split_across_records": "split across records", "cannot_tell": "cannot tell"}
norm = lambda v: ALIAS.get(v, v.replace("_", " ").strip())
final = lambda a, b: a if a == b else DIS
cell = lambda x: (" ".join(x) if isinstance(x, list) else str(x)).replace("\n", " ").replace("|", r"\|")

assert len(ca) == len(cb) == 20 and len(fa) == len(fb)
rows, subrows, frows = [], [], []
for a, b in zip(ca, cb):
    assert (a["rank"], a["author_id"]) == (b["rank"], b["author_id"])
    va, vb = norm(a["verdict"]), norm(b["verdict"])
    rows.append((a["rank"], a["author"], a["author_id"], va, vb, final(va, vb), cell(a["evidence"]), cell(b["evidence"])))
    oa = {o["author_id"]: o for o in a["other_records"]}; ob = {o["author_id"]: o for o in b["other_records"]}
    for k in sorted(set(oa) | set(ob)):
        sa = oa.get(k, {}).get("same_person", "not checked"); sb = ob.get(k, {}).get("same_person", "not checked")
        name = (oa.get(k) or ob.get(k))["display_name"]
        subrows.append((a["author"], k, name, sa, sb, final(sa, sb), cell(oa.get(k, {}).get("why", "")), cell(ob.get(k, {}).get("why", ""))))
for a, b in zip(fa, fb):
    assert (a["line"], a["kept_id"], a["merged_key"]) == (b["line"], b["kept_id"], b["merged_key"])
    va, vb = norm(a["verdict"]), norm(b["verdict"])
    frows.append((a["line"], a["kept_id"], a["merged_key"], va, vb, final(va, vb), cell(a["evidence"]), cell(b["evidence"])))

def agree(rs, i=3):
    n = len(rs); k = sum(r[i] == r[i + 1] for r in rs); return n, k, n - k
def dist(rs): return ", ".join(f"{v}: {c}" for v, c in sorted(Counter(r[5] for r in rs).items()))
def table(head, rs): return "\n".join(["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(str(c) for c in r) + " |" for r in rs])

na, ka, da = agree(rows); ns, ks, ds = agree(subrows); nf, kf, df = agree(frows)
diff = [r for r in frows if r[5] == "different papers"]
md = f"""# Agent checks, reconciled

Two reviewers (A and B) checked the same items blind to each other. For each item the final verdict is the verdict both gave. When they gave different verdicts, the final verdict is "{DIS}". Every count below was computed by `agentcheck_reconcile.py` from the four JSON files next to this one.

The two reviewers spelled the same labels differently, so the labels were mapped to one wording before comparing: `one_person` and `one_person_correct` both became "one person", `split_across_records` became "split across records", and `different_papers` / `same_paper` became "different papers" / "same paper". No verdict was changed beyond that spelling fix. The per-record calls ("yes", "no", "likely", "unclear") were compared as written, so "yes" against "likely" counts as a disagreement.

## Agreement counts

| Check | Items | Both agreed | Disagreed | Final verdicts |
|---|---|---|---|---|
| Top 20 authors (item verdict) | {na} | {ka} | {da} | {dist(rows)} |
| Other author records looked at for those 20 (same person?) | {ns} | {ks} | {ds} | {dist(subrows)} |
| Fuzzy merges | {nf} | {kf} | {df} | {dist(frows)} |

## Fuzzy merges whose final verdict is "different papers"

""" + ("\n".join(f"- line {r[0]}: kept `{r[1]}`, merged `{r[2]}`" for r in diff) or "- none") + f"""

## Table 1. Top 20 authors

{table(["Rank", "Author", "Author ID", "Verdict A", "Verdict B", "Final", "Evidence A", "Evidence B"], rows)}

### Other author records looked at for these 20

{table(["Top-20 author", "Record ID", "Name on record", "Same person? A", "Same person? B", "Final", "Why (A)", "Why (B)"], subrows)}

## Table 2. Fuzzy merges

{table(["Line", "Kept ID", "Merged key", "Verdict A", "Verdict B", "Final", "Evidence A", "Evidence B"], frows)}
"""
open(os.path.join(S, "agentcheck_final.md"), "w", encoding="utf-8").write(md)
# self-check: every table row has the header's column count once escaped pipes are ignored
for line in md.splitlines():
    if line.startswith("| "):
        assert line.replace(r"\|", "").count("|") - 1 in (5, 8), line[:80]
print(f"authors {na} agree {ka} disagree {da} | {dist(rows)}")
print(f"other records {ns} agree {ks} disagree {ds} | {dist(subrows)}")
for r in subrows:
    if r[3] != r[4]: print("  disagree:", r[0], r[1], r[3], r[4])
print(f"fuzzy {nf} agree {kf} disagree {df} | {dist(frows)}")
for r in diff: print("  different:", r[0], r[1], r[2])
