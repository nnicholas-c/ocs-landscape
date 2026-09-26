"""Number check 2, merge step.

Usage (from repo root):
    .venv/bin/python -m pipeline.merge_name_keys

Reads data/work/nc2_evidence.json, nc2_class_A.json and nc2_class_B.json (two
independent classifiers), re-runs the flag query read-only on
data/db/papers.sqlite, and writes data/work/nc2_name_keys.md (fully rewritten
each run, so safe to run twice). Final label per key is the label A and B
share, else cannot_tell.
"""
import json
import math
import sqlite3
from collections import Counter, defaultdict
from statistics import NormalDist

from pipeline.check_name_keys import DB_PATH, FLAGGED_SQL, REPO_ROOT, id_mix

WORK = REPO_ROOT / "data" / "work"
OUT = WORK / "nc2_name_keys.md"
LABELS = ("same_person", "different_people", "cannot_tell")
MIXES = ("all_openalex", "mixed", "all_name_only")

# One-line reasons, condensed by hand from the A and B reasons and checked
# against nc2_evidence.json. No counts in them, the table carries those.
REASONS = {
    "ding e": "All records are name-only 'Eric Ding' and every pair shares coauthor singh r (Rachee Singh) on photonic switching papers.",
    "fu x": "'Xing Fu' is someone else. The two 'Xin Fu' records share no coauthor, institution or route and their years do not overlap, so neither classifier could decide.",
    "hu w": "A5015039354 and name:hu w are both 'Weisheng Hu' and share coauthor sun w. A5000636579 is 'Weijin Hu', a different person.",
    "inoue t": "A5081996202 and name:inoue t are both 'Takeru Inoue' and share several coauthors (oki e, anazawa k, mano t). A5066816626 is 'Takashi Inoue'.",
    "li y": "The two 'Yang Li' records share coauthors and a Swinburne affiliation, but neither is in the team map. The records in the map (Yannanqi, Yupeng, Yinmei) are different people.",
    "ma q": "A5102968002 and name:ma q are both 'Qian Ma' with shared coauthors (dai d, hu y, lu y) and the same route. A5083422711 shares nothing and stays apart.",
    "miles a": "Both OpenAlex records share every coauthor and the University of Arizona affiliation on digital micromirror device (DMD) fiber switch papers, but the first names differ (Alexander, Arriel LaVena).",
    "patterson d": "A5077202069 (Google) and name:patterson d share coauthors jouppi n and young c on Google tensor processing unit (TPU) papers. A5101927146 (Berkeley, Roofline) is outside the map and shares nothing.",
    "sato k": "Both records are 'Ken-ichi Sato', share coauthor namiki s (Shu Namiki), and are on large optical circuit switch papers.",
    "schmid s": "All records are 'Stefan Schmid'. Four are tied by coauthors avin c and addanki v, and two (#2, #5) share only the name and route, so they were left undecided.",
    "tang s": "Three different first names (Shiwei, Shaojie, Sirui) with no shared coauthor, institution or route.",
    "wang j": "First names differ, except two 'Jian Wang' records at different institutions on different topics. The high-overlap pairs sit on the same paper, so they are two people.",
    "xu y": "'Yue Xu' and 'Yelong Xu' share no coauthor, institution or route.",
    "yang y": "Every record has a different first name, and the only overlaps are common coauthor keys such as zhang y.",
    "young c": "Both records are 'Cliff Young' and share coauthors jouppi n and patterson d on Google TPU papers.",
}


def wilson(k, n, conf=0.95):
    z = NormalDist().inv_cdf(0.5 + conf / 2)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def pct(x):
    return f"{100 * x:.0f} percent"


def load(name):
    return json.loads((WORK / name).read_text(encoding="utf-8"))


def pair_type(ids, oa):
    n = sum(oa[i] is not None for i in ids)
    return ("name-only + name-only", "OpenAlex + name-only", "OpenAlex + OpenAlex")[n]


def main():
    ev = load("nc2_evidence.json")
    A = {r["name_key"]: r for r in load("nc2_class_A.json")}
    B = {r["name_key"]: r for r in load("nc2_class_B.json")}
    sample = ev["sampled_keys"]
    assert sorted(A) == sorted(B) == sorted(sample), "classifier files do not cover the sample"

    # Reproduce the count and the ID-status breakdown from the database.
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    flagged = [r[0] for r in con.execute(FLAGGED_SQL)]
    ext = {r[0] for r in con.execute(
        "SELECT DISTINCT pa.author_id FROM paper_authors pa JOIN papers p "
        "ON p.paper_id = pa.paper_id WHERE p.extended_set = 1")}
    oa, by_key = {}, defaultdict(list)
    for aid, key, oid in con.execute("SELECT author_id, name_key, openalex_author_id FROM authors"):
        oa[aid] = oid
        by_key[key].append(aid)
    con.close()
    mix = Counter(id_mix([a for a in by_key[k] if a in ext], oa) for k in flagged)
    assert len(flagged) == ev["flagged_keys_total"], (len(flagged), ev["flagged_keys_total"])
    assert dict(mix) == ev["flagged_id_mix"], (dict(mix), ev["flagged_id_mix"])
    assert set(sample) <= set(flagged)
    N, n = len(flagged), len(sample)

    rows, final, agree, pair_agree = [], {}, 0, 0
    in_map_split, types, crosstab = 0, Counter(), Counter()
    for e in ev["evidence"]:
        k = e["name_key"]
        recs = e["records"]
        in_map = {r["author_id"] for r in recs if r["in_extended_set_graph"]}
        a, b = A[k]["label"], B[k]["label"]
        final[k] = a if a == b else "cannot_tell"
        agree += a == b
        pa = {frozenset(p) for p in A[k]["pairs_same"]}
        pb = {frozenset(p) for p in B[k]["pairs_same"]}
        pair_agree += pa == pb
        map_mix = id_mix(sorted(in_map), oa)
        crosstab[(map_mix, final[k])] += 1
        if final[k] == "same_person":
            shared = pa & pb
            in_map_split += any(p <= in_map for p in shared)
            for t in {pair_type(p, oa) for p in shared}:
                types[t] += 1
        rows.append(f"| {k} | {len(in_map)} of {len(recs)} | {a} | {b} | {final[k]} | {REASONS[k]} |")

    counts = Counter(final.values())
    k_same = counts["same_person"]
    lo, hi = wilson(k_same, n)
    lo2, hi2 = wilson(in_map_split, n)
    # The conclusion below is written for this outcome. If a rerun changes it, rewrite the text.
    assert k_same * 2 > n and agree == n, "conclusion text no longer matches the numbers"

    L = []
    w = L.append
    w("# Number check 2. Split name keys in the team map")
    w("")
    w("Inputs are data/work/nc2_evidence.json (evidence, from pipeline/check_name_keys.py), "
      "data/work/nc2_class_A.json and data/work/nc2_class_B.json (two independent classifiers). "
      "Every number below is computed by pipeline/merge_name_keys.py, which also re-runs the flag "
      "query read-only on data/db/papers.sqlite. A name key is a last name plus first initial, "
      "such as 'sato k'. The team map is the stage 4 author graph, which holds only authors with "
      "an extended-set paper.")
    w("")
    w("## 1. The count, reproduced")
    w("")
    w(f"The query returns {N} name keys today, the same as flagged_keys_total in the evidence file "
      "and the 149 that the stage 4 grapher logged at 06:32 in deliverables/pitfalls_original_log.md. A key is flagged when more than one "
      "author record with that key has an extended-set paper and at least one of those records "
      "has a core paper. The rule lives in pipeline/graph.py log_split_person_candidates().")
    w("")
    w("```sql")
    w(FLAGGED_SQL + ";")
    w("```")
    w("")
    w("## 2. Keys by OpenAlex ID status")
    w("")
    w("Status is read from the records of each key that are in the team map. all_openalex means "
      "every such record has an OpenAlex author ID (identifier). all_name_only means none does, "
      "which is the case for arXiv-only authors. mixed means some do and some do not.")
    w("")
    w(f"| status | flagged keys (of {N}) | share | sampled keys (of {n}) | final same_person | final different_people | final cannot_tell |")
    w("|---|---|---|---|---|---|---|")
    for m in MIXES:
        s = sum(crosstab[(m, lab)] for lab in LABELS)
        w(f"| {m} | {mix[m]} | {pct(mix[m] / N)} | {s} | " + " | ".join(str(crosstab[(m, lab)]) for lab in LABELS) + " |")
    w("")
    w("An all_openalex key cannot come from the stage 2 merge rule for name-only records, because "
      "OpenAlex itself gave its records different author IDs. So that rule can explain at most "
      f"the {mix['mixed'] + mix['all_name_only']} mixed or all_name_only keys.")
    w("")
    w(f"## 3. The {n} sampled keys")
    w("")
    w(f"The sample is {n} keys drawn at random from the {N} with seed {ev['seed']} "
      "(pipeline/check_name_keys.py). The records column counts records in the team map, then "
      "all author records with the key. A and B are the two classifier labels. Final is their "
      "shared label, else cannot_tell.")
    w("")
    w("| key | records (in map of all) | A | B | final | reason |")
    w("|---|---|---|---|---|---|")
    L.extend(rows)
    w("")
    w("## 4. Agreement between the two classifiers")
    w("")
    w(f"A and B gave the same label on {agree} of {n} keys ({pct(agree / n)}). They also listed "
      f"exactly the same same-person record pairs on {pair_agree} of {n} keys. Final labels are "
      + ", ".join(f"{lab} {counts[lab]}" for lab in LABELS) + ".")
    w("")
    w("## 5. Estimate")
    w("")
    w(f"The share of flagged keys that hide a real split (final label same_person) is {k_same} of "
      f"{n}, or {pct(k_same / n)}. The 95 percent Wilson interval is {pct(lo)} to {pct(hi)}. "
      f"Scaled to the {N} keys that is about {round(k_same / n * N)} keys, with a range of "
      f"{round(lo * N)} to {round(hi * N)}. This comes from a sample of {n} keys, so the interval "
      "is wide. It uses no finite population correction, which would narrow it a little. The "
      "cannot_tell key is counted as not split.")
    w("")
    w(f"One same_person key (li y) has its split pair entirely outside the team map. Counting only "
      f"keys where a same-person pair has both records in the map gives {in_map_split} of {n} "
      f"({pct(in_map_split / n)}, Wilson interval {pct(lo2)} to {pct(hi2)}).")
    w("")
    w(f"Across the {k_same} same_person keys, an agreed same-person pair joins an OpenAlex record "
      f"to a name-only record in {types['OpenAlex + name-only']} keys, two name-only records in "
      f"{types['name-only + name-only']} keys, and two OpenAlex records in "
      f"{types['OpenAlex + OpenAlex']} keys. A key can have more than one kind.")
    w("")
    w("## 6. Conclusion")
    w("")
    w(f"This is mostly a real bug, because {k_same} of {n} sampled keys hide at least one person split "
      f"into several records, which puts about {pct(k_same / n)} of the {N} keys in that state "
      f"(95 percent interval {pct(lo)} to {pct(hi)}, from a sample of {n}). "
      f"The most common cause is an OpenAlex record not joined to an arXiv name-only record "
      f"({types['OpenAlex + name-only']} keys), and the split people include authors of core OCS "
      "(optical circuit switching) papers such as Ken-ichi Sato, Stefan Schmid and David Patterson. "
      "For recruiting individuals, the map undercounts these people's papers and can show one "
      "person as several nodes, so every person-level ranking needs a hand check before use. "
      "For partnering with groups, the map is safer, because this flag marks one person shown as "
      "several nodes, not strangers merged into one, so a group is still found but its size and "
      "output are understated.")
    w("")
    OUT.write_text("\n".join(L), encoding="utf-8")
    text = OUT.read_text(encoding="utf-8")
    assert text.isascii() and "--" not in text.replace("|---", "")
    print(f"flagged {N}, mix {dict(mix)}; agreement {agree}/{n}; final {dict(counts)}; "
          f"same_person {k_same}/{n} Wilson {lo:.3f}-{hi:.3f}; in-map split {in_map_split}/{n}; "
          f"pair types {dict(types)}")
    print(f"wrote {OUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    # Self-check: the interval contains k/n, is symmetric under k -> n-k, and reaches 0 at k = 0.
    for kk, nn in ((0, 15), (10, 15), (15, 15), (3, 7)):
        l1, h1 = wilson(kk, nn)
        l2, h2 = wilson(nn - kk, nn)
        assert abs(l1 - (1 - h2)) < 1e-9 and abs(h1 - (1 - l2)) < 1e-9
        assert l1 - 1e-9 <= kk / nn <= h1 + 1e-9
    assert wilson(0, 15)[0] == 0.0
    main()
