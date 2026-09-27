"""Number check 2, evidence step. Read-only on data/db/papers.sqlite.

Usage (from repo root):
    .venv/bin/python -m pipeline.check_name_keys
    .venv/bin/python -m pipeline.check_name_keys --seed 20260930 --out data/work/nc2_run2_evidence.json

Defaults (seed 20260927, data/work/nc2_evidence.json) reproduce run 1's file.

Where the 149 came from. deliverables/pitfalls_original_log.md 06:32 (stage 4
grapher) logged "149 name_key(s) map to more than one author_id in the
extended-set graph with at least one core paper". The count is made in
pipeline/graph.py log_split_person_candidates(), not in pipeline/curate.py.
curate.py only creates the split records (build_entities: a no-OpenAlex-ID
appearance joins an existing record only on a shared institution, otherwise
it gets name:<key>, name:<key>#2, ...). graph.py keeps only authors with an
extended-set paper, groups them by authors.name_key, and flags a key when it
has more than one author_id and at least one of them has a core paper. The
same count in SQL:

    WITH ext AS (
        SELECT pa.author_id,
               MAX(p.core_set) AS has_core
        FROM paper_authors pa
        JOIN papers p ON p.paper_id = pa.paper_id
        WHERE p.extended_set = 1
        GROUP BY pa.author_id
    )
    SELECT a.name_key
    FROM ext JOIN authors a ON a.author_id = ext.author_id
    GROUP BY a.name_key
    HAVING COUNT(*) > 1 AND MAX(ext.has_core) = 1
    ORDER BY a.name_key;

Writes data/work/nc2_evidence.json (fully rewritten each run, so safe to run
twice). Evidence only, no judgement about who is the same person.
"""
import argparse
import json
import random
import sqlite3
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
OUT_PATH = REPO_ROOT / "data" / "work" / "nc2_evidence.json"
SEED = 20260927
SAMPLE_SIZE = 15

FLAGGED_SQL = __doc__.split("same count in SQL:")[1].split(";")[0].strip()


def id_mix(author_ids, oa_id):
    have = [oa_id[a] is not None for a in author_ids]
    return "all_openalex" if all(have) else "all_name_only" if not any(have) else "mixed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", type=Path, default=OUT_PATH, help="path relative to the repo root")
    args = ap.parse_args()
    seed, out_path = args.seed, REPO_ROOT / args.out

    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row

    flagged = [r[0] for r in con.execute(FLAGGED_SQL)]

    # Check: the SQL must agree with graph.py's own Python rule on the same database.
    from pipeline import graph
    paper_core, author_papers, _, author_names, inst_names, tags = graph.load_data(con)
    recs = graph.build_author_records(paper_core, author_papers, author_names, inst_names, tags)
    g = defaultdict(list)
    for a, r in recs.items():
        g[r["name_key"]].append(a)
    graph_flagged = sorted(k for k, ids in g.items() if len(ids) > 1 and any(recs[a]["core_count"] for a in ids))
    assert graph_flagged == sorted(flagged), (len(graph_flagged), len(flagged))

    authors = {r["author_id"]: dict(r) for r in con.execute("SELECT * FROM authors")}
    oa_id = {a: r["openalex_author_id"] for a, r in authors.items()}
    by_key = defaultdict(list)
    for a, r in sorted(authors.items()):
        by_key[r["name_key"]].append(a)

    ext_authors = {r[0] for r in con.execute(
        "SELECT DISTINCT pa.author_id FROM paper_authors pa JOIN papers p "
        "ON p.paper_id = pa.paper_id WHERE p.extended_set = 1")}
    # The records each flagged key counted (extended-set authors only), for the mix count.
    flagged_mix = Counter(id_mix([a for a in by_key[k] if a in ext_authors], oa_id) for k in flagged)
    multi_all = [k for k, ids in by_key.items() if len(ids) > 1]
    all_mix = Counter(id_mix(by_key[k], oa_id) for k in multi_all)

    papers = {r["paper_id"]: dict(r) for r in con.execute(
        "SELECT paper_id, title, year, venue, core_set, extended_set FROM papers")}
    tech = {r[0]: r[1] for r in con.execute("SELECT paper_id, tech_route FROM tags")}
    inst_name = {r[0]: r[1] for r in con.execute("SELECT inst_id, display_name FROM institutions")}
    pa_rows = con.execute("SELECT paper_id, author_id, inst_id FROM paper_authors").fetchall()
    con.close()

    paper_rows = defaultdict(list)   # paper_id -> [(author_id, inst_id)]
    author_rows = defaultdict(list)  # author_id -> [(paper_id, inst_id)]
    for r in pa_rows:
        paper_rows[r["paper_id"]].append((r["author_id"], r["inst_id"]))
        author_rows[r["author_id"]].append((r["paper_id"], r["inst_id"]))

    ranked = sorted(flagged)
    sample = sorted(random.Random(seed).sample(ranked, min(SAMPLE_SIZE, len(ranked))))

    def record(aid):
        plist, own_insts, paper_insts, coauthors = [], set(), set(), {}
        for pid, inst in sorted(author_rows[aid]):
            p = papers[pid]
            if inst:
                own_insts.add(inst)
            on_paper = sorted({i for _, i in paper_rows[pid] if i})
            paper_insts.update(on_paper)
            for co, _ in paper_rows[pid]:
                if co != aid:
                    coauthors[co] = authors[co]["name_key"]
            plist.append({
                "paper_id": pid, "title": p["title"], "year": p["year"], "venue": p["venue"],
                "set": "core" if p["core_set"] else "extended" if p["extended_set"] else "neither",
                "tech_route": tech.get(pid),
                "own_affiliation": {"inst_id": inst, "name": inst_name.get(inst)} if inst else None,
                "institutions_on_paper": [{"inst_id": i, "name": inst_name.get(i)} for i in on_paper],
            })
        years = [p["year"] for p in plist if p["year"] is not None]
        return {
            "author_id": aid,
            "display_name": authors[aid]["display_name"],
            "openalex_author_id": oa_id[aid],
            "in_extended_set_graph": aid in ext_authors,
            "year_range": [min(years), max(years)] if years else None,
            "papers": plist,
            "own_affiliations": sorted(own_insts),
            "institutions_on_papers": sorted(paper_insts),
            "coauthors": sorted(({"author_id": c, "display_name": authors[c]["display_name"],
                                  "name_key": k} for c, k in coauthors.items()),
                                 key=lambda d: (d["name_key"], d["author_id"])),
            "_co_keys": set(coauthors.values()),
            "_papers": {p["paper_id"] for p in plist},
            "_routes": {p["tech_route"] for p in plist if p["tech_route"]},
        }

    evidence = []
    for key in sample:
        recs = [record(a) for a in by_key[key]]
        pairs = []
        for x, y in combinations(recs, 2):
            pairs.append({
                "a": x["author_id"], "b": y["author_id"],
                # The key itself is left out, since those are the records being compared.
                "shared_coauthor_name_keys": sorted((x["_co_keys"] & y["_co_keys"]) - {key}),
                "shared_own_affiliations": sorted(set(x["own_affiliations"]) & set(y["own_affiliations"])),
                "shared_institutions_on_papers": sorted(set(x["institutions_on_papers"]) & set(y["institutions_on_papers"])),
                "shared_papers": sorted(x["_papers"] & y["_papers"]),
                "year_range_a": x["year_range"], "year_range_b": y["year_range"],
                "shared_tech_routes": sorted(x["_routes"] & y["_routes"]),
            })
        for r in recs:
            for k in ("_co_keys", "_papers", "_routes"):
                del r[k]
        evidence.append({"name_key": key, "id_mix": id_mix([r["author_id"] for r in recs], oa_id),
                         "records": recs, "pairwise": pairs})

    out = {
        "source": "data/db/papers.sqlite, read-only; script pipeline/check_name_keys.py",
        "flagged_rule_sql": FLAGGED_SQL,
        "flagged_keys_total": len(flagged),
        "flagged_id_mix": dict(sorted(flagged_mix.items())),
        "all_multi_record_keys_total": len(multi_all),
        "all_multi_record_keys_id_mix": dict(sorted(all_mix.items())),
        "seed": seed,
        "sampled_keys": sample,
        "sample_note": "records list every authors row with the key, including rows with no extended-set paper (in_extended_set_graph false), which the flag rule did not count",
        "evidence": evidence,
    }
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"flagged keys: {len(flagged)}  mix: {dict(flagged_mix)}")
    print(f"all multi-record keys: {len(multi_all)}  mix: {dict(all_mix)}")
    print(f"sampled: {sample}")
    print(f"wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
