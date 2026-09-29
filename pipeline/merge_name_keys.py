"""Number check 2, merge step.

Usage (from repo root):
    .venv/bin/python -m pipeline.merge_name_keys
    .venv/bin/python -m pipeline.merge_name_keys --evidence data/work/nc2_run2_evidence.json \
        --class-a data/work/nc2_run2_class_A.json --class-b data/work/nc2_run2_class_B.json \
        --out data/work/nc2_run2_name_keys.md

Defaults read data/work/nc2_evidence.json, nc2_class_A.json and nc2_class_B.json
(two independent classifiers) and write data/work/nc2_name_keys.md, run 1's
file. Re-runs the flag query read-only on data/db/papers.sqlite, so the
evidence file must come from the database now in place. The output is fully
rewritten each run, so safe to run twice. Final label per key is the label A
and B share, else cannot_tell. The run-specific prose (reasons, grapher log
line, conclusion) is looked up by the evidence file's seed in RUNS.
"""
import argparse
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist

from pipeline.check_name_keys import DB_PATH, FLAGGED_SQL, REPO_ROOT, id_mix

WORK = REPO_ROOT / "data" / "work"
LOG = REPO_ROOT / "deliverables" / "pitfalls_original_log.md"
LABELS = ("same_person", "different_people", "cannot_tell")
MIXES = ("all_openalex", "mixed", "all_name_only")

# One-line reasons, condensed by hand from the A and B reasons and checked
# against the evidence file. No counts in them, the table carries those.
REASONS_RUN1 = {
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

REASONS_RUN2 = {
    "chen b": "Different first names (Benwen, Bao, Bin) at different institutions. The only shared coauthor key, guo h, is two different people (Hangbing Guo, Hangyu Guo).",
    "chen g": "Different first names (Genxiang, Guihai, Guanyu, Guo), and the only overlaps are common coauthor keys such as chen x.",
    "chen s": "A5068274938 and A5108580591 are both 'Sai Chen' at Alibaba Group and share coauthor Chongjin Xie. Only A5068274938 is in the team map. Shixi Chen and Shawn Shuoshuo Chen are other people.",
    "chen y": "The 'Yan Chen' records at Northwestern share coauthors such as Ankit Singla on the OSA (optical switching architecture) papers, and the 'Ying Chen' records at Minzu University of China share coauthors such as Genxiang Chen. The 'Young-kai Chen' records have Alcatel Lucent on both papers and the same topic but no shared coauthor, so that pair is weaker.",
    "liu z": "Zhuotao Liu is split into A5045206037 and name-only #2 and #5, which share coauthors Peirui Cao, Shizhen Zhao and Xinbing Wang. ZhuoRan Liu (name:liu z) and Zhuoran Liu (#4) share coauthors such as Weihao Jiang and Xinchi Han. ZhuoRan and Zhuotao sit on the same papers, so they are two people.",
    "patterson d": "A5077202069 (Google) and name:patterson d share coauthor Cliff Young on Google tensor processing unit (TPU) papers. A5101927146 (Berkeley, Roofline) is outside the map and shares nothing.",
    "singh a": "The 'Arjun Singh' records share many coauthors, such as Amin M. Vahdat, on the Apollo optical circuit switching (OCS) papers. The 'Atul Kumar Singh' records share Princeton and coauthors such as Ankit Singla on Proteus and OSA.",
    "wei y": "Different first names (Yuming, Yiran) with no shared coauthor, institution or paper.",
    "wu j": "Different first names (Jingbo, Jiamin, Jiayang, Jeffrey, Juejian, Junhui, Jian). The only overlaps are common coauthor keys and broad institutions on papers.",
    "xu h": "'Hongnan Xu' is someone else. 'Hong Li Xu' and 'Hong Xu' both work on data center networking, but they share no coauthor, neither has an affiliation, and their years are far apart, so neither classifier could decide.",
    "yang y": "Every record has a different first name, and the only overlaps are common coauthor keys such as wang h and broad institutions on papers.",
    "yang z": "Different first names (Zijiang, Zhiyong) with no shared coauthor, institution or paper.",
    "zhang h": "Mostly different first names. The 'Hao Zhang' records are at different institutions (Tianjin University, University of Science and Technology of China, Beijing Institute of Technology) on different topics with no shared coauthor.",
    "zhang j": "Jinsong and Jianfa differ by first name. The 'Jie Zhang' records are at Beijing University of Posts and Telecommunications (optical switching) and the China Meteorological Administration (climate model) with no shared coauthor.",
    "zhu y": "A5084336844 and name:zhu y are both 'Yibo Zhu' and share coauthors Yu Zhou and Yimin Jiang (listed once as 'Jiang, Yimin') on data center network papers. The Santa Barbara City College 'Yibo Zhu' shares nothing with them.",
}


def conclusion_run1(k_same, n, N, lo, hi, agree, types, **_):
    # Written for this outcome. If a rerun changes it, rewrite the text.
    assert k_same * 2 > n and agree == n, "conclusion text no longer matches the numbers"
    return (
        f"This is mostly a real bug, because {k_same} of {n} sampled keys hide at least one person split "
        f"into several records, which puts about {pct(k_same / n)} of the {N} keys in that state "
        f"(95 percent interval {pct(lo)} to {pct(hi)}, from a sample of {n}). "
        f"The most common cause is an OpenAlex record not joined to an arXiv name-only record "
        f"({types['OpenAlex + name-only']} keys), and the split people include authors of core OCS "
        "(optical circuit switching) papers such as Ken-ichi Sato, Stefan Schmid and David Patterson. "
        + FOR_USE)


def conclusion_run2(k_same, n, N, lo, hi, agree, types, final, log_time, **_):
    # Written for this outcome. If a rerun changes it, rewrite the text.
    assert agree == n and k_same * 2 < n and lo < 0.5 < hi, "conclusion text no longer matches the numbers"
    assert types["OpenAlex + OpenAlex"] and types["OpenAlex + name-only"]
    assert all(final[k] == "same_person" for k in ("singh a", "chen y", "liu z"))
    return (
        f"This is a real bug, though in this sample not for most keys, because {k_same} of {n} sampled "
        f"keys hide at least one person split into several records. That puts about {pct(k_same / n)} "
        f"of the {N} keys in that state (95 percent interval {pct(lo)} to {pct(hi)}, from a sample of "
        f"{n}), and the interval includes half, so the sample cannot say whether most flagged keys are "
        f"real splits. The {log_time} grapher line blames the stage 2 merge rule for name-only records, "
        f"but in {types['OpenAlex + OpenAlex']} of the {k_same} keys OpenAlex itself gave one person two "
        f"author IDs, which that rule cannot cause. In {types['OpenAlex + name-only']} keys an OpenAlex "
        "record was not joined to an arXiv name-only record. The split people include authors of core OCS "
        "papers such as Arjun Singh (Apollo), Yan Chen (OSA) and Zhuotao Liu. "
        + FOR_USE)


FOR_USE = ("For recruiting individuals, the map undercounts these people's papers and can show one "
           "person as several nodes, so every person-level ranking needs a hand check before use. "
           "For partnering with groups, the map is safer, because this flag marks one person shown as "
           "several nodes, not strangers merged into one, so a group is still found but its size and "
           "output are understated.")

# Keyed by the evidence file's seed. log is the stage 4 grapher line in LOG that
# first reported this flagged count.
RUNS = {
    20260927: {"reasons": REASONS_RUN1, "log": "2026-09-26 06:32", "conclusion": conclusion_run1},
    20260930: {"reasons": REASONS_RUN2, "log": "2026-09-26 16:44", "conclusion": conclusion_run2},
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


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def keys(x):
    return f"{x} key" if x == 1 else f"{x} keys"


def pair_type(ids, oa):
    n = sum(oa[i] is not None for i in ids)
    return ("name-only + name-only", "OpenAlex + name-only", "OpenAlex + OpenAlex")[n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", type=Path, default=WORK / "nc2_evidence.json", help="relative to the repo root")
    ap.add_argument("--class-a", type=Path, default=WORK / "nc2_class_A.json", help="relative to the repo root")
    ap.add_argument("--class-b", type=Path, default=WORK / "nc2_class_B.json", help="relative to the repo root")
    ap.add_argument("--out", type=Path, default=WORK / "nc2_name_keys.md", help="relative to the repo root")
    args = ap.parse_args()
    ev_path, a_path, b_path, out = (REPO_ROOT / p for p in (args.evidence, args.class_a, args.class_b, args.out))
    # The report names its inputs repo-relative, so refuse outside inputs before writing anything.
    bad = [n for n, p in (("--evidence", ev_path), ("--class-a", a_path), ("--class-b", b_path))
           if not p.is_relative_to(REPO_ROOT)]
    if bad:
        ap.error(f"{', '.join(bad)} must be inside the repo, because the report names its inputs repo-relative")
    rel = lambda p: p.relative_to(REPO_ROOT).as_posix()

    ev = load(ev_path)
    A = {r["name_key"]: r for r in load(a_path)}
    B = {r["name_key"]: r for r in load(b_path)}
    sample = ev["sampled_keys"]
    assert sorted(A) == sorted(B) == sorted(sample), "classifier files do not cover the sample"
    run = RUNS[ev["seed"]]
    assert sorted(run["reasons"]) == sorted(sample), "reasons do not cover the sample"

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
    log_time = run["log"][-5:]
    assert f"- [{run['log']}] stage 4 grapher: {N} name_key(s)" in LOG.read_text(encoding="utf-8")

    rows, final, agree, pair_agree = [], {}, 0, 0
    in_map_split, types, crosstab, outside = 0, Counter(), Counter(), {}
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
            if any(p <= in_map for p in shared):
                in_map_split += 1
            else:
                outside[k] = "partly" if set().union(*shared) & in_map else "entirely"
            for t in {pair_type(p, oa) for p in shared}:
                types[t] += 1
        rows.append(f"| {k} | {len(in_map)} of {len(recs)} | {a} | {b} | {final[k]} | {run['reasons'][k]} |")

    counts = Counter(final.values())
    k_same = counts["same_person"]
    lo, hi = wilson(k_same, n)
    lo2, hi2 = wilson(in_map_split, n)
    conclusion = run["conclusion"](k_same=k_same, n=n, N=N, lo=lo, hi=hi, agree=agree, types=types,
                                   final=final, log_time=log_time)
    c_tell = counts["cannot_tell"]
    if len(outside) == 1:
        (k, where), = outside.items()
        outside_text = f"One same_person key ({k}) has its split pair {where} outside the team map."
    elif outside:
        outside_text = (f"{len(outside)} same_person keys ({', '.join(outside)}) have no split pair "
                        "with both records in the team map.")
    else:
        outside_text = "Every same_person key has a split pair with both records in the team map."

    L = []
    w = L.append
    w("# Number check 2. Split name keys in the team map")
    w("")
    w(f"Inputs are {rel(ev_path)} (evidence, from pipeline/check_name_keys.py), "
      f"{rel(a_path)} and {rel(b_path)} (two independent classifiers). "
      "Every number below is computed by pipeline/merge_name_keys.py, which also re-runs the flag "
      "query read-only on data/db/papers.sqlite. A name key is a last name plus first initial, "
      "such as 'sato k'. The team map is the stage 4 author graph, which holds only authors with "
      "an extended-set paper.")
    w("")
    w("## 1. The count, reproduced")
    w("")
    w(f"The query returns {N} name keys today, the same as flagged_keys_total in the evidence file "
      f"and the {N} that the stage 4 grapher logged at {log_time} in deliverables/pitfalls_original_log.md. A key is flagged when more than one "
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
      "is wide. It uses no finite population correction, which would narrow it a little. "
      + ("The cannot_tell key is" if c_tell == 1 else f"The {c_tell} cannot_tell keys are")
      + " counted as not split.")
    w("")
    w(f"{outside_text} Counting only keys where a same-person pair has both records in the map gives {in_map_split} of {n} "
      f"({pct(in_map_split / n)}, Wilson interval {pct(lo2)} to {pct(hi2)}).")
    w("")
    w(f"Across the {k_same} same_person keys, an agreed same-person pair joins an OpenAlex record "
      f"to a name-only record in {keys(types['OpenAlex + name-only'])}, two name-only records in "
      f"{keys(types['name-only + name-only'])}, and two OpenAlex records in "
      f"{keys(types['OpenAlex + OpenAlex'])}. A key can have more than one kind.")
    w("")
    w("## 6. Conclusion")
    w("")
    w(conclusion)
    w("")
    out.write_text("\n".join(L), encoding="utf-8")
    text = out.read_text(encoding="utf-8")
    assert text.isascii() and "--" not in text.replace("|---", "")
    print(f"flagged {N}, mix {dict(mix)}; agreement {agree}/{n}; final {dict(counts)}; "
          f"same_person {k_same}/{n} Wilson {lo:.3f}-{hi:.3f} scaled {round(k_same / n * N)} "
          f"({round(lo * N)}-{round(hi * N)}); in-map split {in_map_split}/{n}; pair types {dict(types)}")
    print(f"wrote {out}")


if __name__ == "__main__":
    # Self-check: the interval contains k/n, is symmetric under k -> n-k, and reaches 0 at k = 0.
    for kk, nn in ((0, 15), (10, 15), (15, 15), (3, 7)):
        l1, h1 = wilson(kk, nn)
        l2, h2 = wilson(nn - kk, nn)
        assert abs(l1 - (1 - h2)) < 1e-9 and abs(h1 - (1 - l2)) < 1e-9
        assert l1 - 1e-9 <= kk / nn <= h1 + 1e-9
    assert wilson(0, 15)[0] == 0.0
    main()
