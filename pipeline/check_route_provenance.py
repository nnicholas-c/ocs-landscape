"""Number check 1. How did each tech_route's core papers get into the sample?

Read-only. Opens data/db/papers.sqlite in read-only mode and reads data/raw/*.jsonl,
pipeline/queries.yaml, data/raw/relevance.csv (through the collector's own seed
function) and data/projects.csv. Writes only the --out JSON.

    .venv/bin/python -m pipeline.check_route_provenance --out data/work/nc1_route_provenance.json

SQL used (all SELECTs):

    -- every paper with its tag row (tags cover core and extended papers)
    SELECT p.paper_id, p.title, p.year, p.cited_by_count, p.relevance_score,
           p.core_set, p.extended_set, t.tech_route
      FROM papers p LEFT JOIN tags t ON t.paper_id = p.paper_id;

    -- every raw record behind a paper; a merged paper has several
    SELECT record_key, paper_id FROM duplicates;

    -- papers with at least one author affiliated with UC Berkeley on that paper
    -- (arXiv-only records carry no affiliations, so this is a lower bound)
    SELECT DISTINCT pa.paper_id FROM paper_authors pa
      JOIN institutions i ON i.inst_id = pa.inst_id
     WHERE i.display_name = 'University of California, Berkeley';

    -- author rows of the anchor paper, and how many carry an institution
    SELECT COUNT(*) FROM paper_authors WHERE paper_id = ? [AND inst_id IS NOT NULL];

    -- papers sharing at least one author with the Berkeley anchor paper
    SELECT DISTINCT b.paper_id FROM paper_authors a
      JOIN paper_authors b ON b.author_id = a.author_id
     WHERE a.paper_id = ? AND b.paper_id <> a.paper_id;

Entry path of a raw record is read from its JSONL "query" field. It is one of
  query:<source>:<exact query string>   a phrase query (openalex or arxiv)
  anchor:<title>                        an anchor title lookup from queries.yaml
  snowball:<seed openalex id>           the stage 1c snowball
CAVEAT: the collectors skip a record_key already on disk, so each raw record
carries only the FIRST query that found it. A paper also matched by a later
query is not credited to that query. Counts per query are therefore lower
bounds on how many papers each query could find.
"""
import argparse
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from pipeline.collect_openalex import load_snowball_seeds

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
RAW_DIR = REPO_ROOT / "data" / "raw"
QUERIES_PATH = REPO_ROOT / "pipeline" / "queries.yaml"
PROJECTS_PATH = REPO_ROOT / "data" / "projects.csv"

BERKELEY_ANCHOR = "Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers"
FOCUS_ROUTE = "mems_silicon_photonic"
PROJECT_ROUTES = ("mems_3d", "mems_silicon_photonic")

# Which query strings in queries.yaml name a tech_route, matched against the
# route names and signal words in .claude/skills/ocs-domain/SKILL.md.
# A list with more than one route means the query names a family (MEMS, or the
# silicon photonic platform) rather than one route. Queries not listed name no route.
QUERY_NAMES_ROUTE = {
    "MEMS optical switch": ["mems_3d", "mems_2d", "mems_silicon_photonic"],
    "3D MEMS optical cross-connect": ["mems_3d"],
    "silicon photonic MEMS switch": ["mems_silicon_photonic"],
    "silicon photonic switch data center": ["mems_silicon_photonic", "thermo_optic", "electro_optic"],
    "silicon photonic switch": ["mems_silicon_photonic", "thermo_optic", "electro_optic"],
    "wavelength selective switch LCoS": ["lcos"],
    "wavelength selective switch": ["lcos"],
    "piezoelectric optical switch": ["piezo"],
    "thermo-optic switch port count": ["thermo_optic"],
    "thermo-optic switch": ["thermo_optic"],
    "semiconductor optical amplifier switch data center": ["soa"],
    "robotic fiber patch panel": ["robotic_patch_panel"],
}


def entry_path(rec, anchors):
    q = rec.get("query") or ""
    if q.startswith("snowball:"):
        return q
    if q in anchors:
        return f"anchor:{q}"
    return f"query:{rec.get('source')}:{q}"


def kind(path):
    return path.split(":", 1)[0]


def sorted_counter(c):
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/work/nc1_route_provenance.json")
    args = ap.parse_args()

    cfg = yaml.safe_load(QUERIES_PATH.read_text(encoding="utf-8"))
    anchors = set(cfg.get("anchors") or [])

    # ---- raw records: every (record_key, entry path), across all raw files ----
    key_paths = defaultdict(set)
    key_title = {}
    key_text = {}   # lowercased title + abstract, for the phrase diagnostic in (4)
    key_refs = {}   # referenced_works of OpenAlex records, to tell seed references from citers
    raw_lines = Counter()
    for path in sorted(RAW_DIR.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                rec = json.loads(line)
                raw_lines[path.name] += 1
                key_paths[rec["record_key"]].add(entry_path(rec, anchors))
                key_title.setdefault(rec["record_key"], rec.get("title"))
                key_text.setdefault(rec["record_key"],
                                    f"{rec.get('title') or ''} {rec.get('abstract') or ''}".lower())
                if rec.get("referenced_works"):
                    key_refs.setdefault(rec["record_key"], set(rec["referenced_works"]))

    con = sqlite3.connect(f"file:{DB_PATH.as_posix()}?mode=ro", uri=True)
    papers = {
        r[0]: dict(zip(("paper_id", "title", "year", "cited_by_count", "relevance_score",
                        "core_set", "extended_set", "tech_route"), r))
        for r in con.execute(
            "SELECT p.paper_id, p.title, p.year, p.cited_by_count, p.relevance_score, "
            "p.core_set, p.extended_set, t.tech_route "
            "FROM papers p LEFT JOIN tags t ON t.paper_id = p.paper_id")
    }
    dup = dict(con.execute("SELECT record_key, paper_id FROM duplicates"))
    ucb = {r[0] for r in con.execute(
        "SELECT DISTINCT pa.paper_id FROM paper_authors pa "
        "JOIN institutions i ON i.inst_id = pa.inst_id "
        "WHERE i.display_name = 'University of California, Berkeley'")}

    paper_paths = defaultdict(set)
    paper_keys = defaultdict(list)
    for key, paths in key_paths.items():
        pid = dup.get(key)
        if pid is None:
            continue
        paper_paths[pid] |= paths
        paper_keys[pid].append(key)
    raw_keys_not_in_duplicates = sorted(k for k in key_paths if k not in dup)

    core = {pid: p for pid, p in papers.items() if p["core_set"] == 1}

    def combo(pid):
        return "+".join(sorted({kind(x) for x in paper_paths[pid]})) or "none"

    def snowball_only(pid):
        return combo(pid) == "snowball"

    # ---- per route: how core papers entered ----
    route_counts = Counter(p["tech_route"] for p in core.values())
    route_entry = {}
    for route in route_counts:
        pids = [pid for pid, p in core.items() if p["tech_route"] == route]
        by_path = Counter(x for pid in pids for x in paper_paths[pid])
        route_entry[route] = {
            "core_papers": len(pids),
            "by_entry_kind_exclusive": sorted_counter(Counter(combo(pid) for pid in pids)),
            "by_entry_path_nonexclusive": sorted_counter(by_path),
            "ucb_affiliated": sum(pid in ucb for pid in pids),
        }
    route_entry = dict(sorted(route_entry.items(), key=lambda kv: -kv[1]["core_papers"]))

    # ---- Berkeley anchor ----
    anchor_keys = [k for k, ps in key_paths.items() if f"anchor:{BERKELEY_ANCHOR}" in ps]
    anchor_pid = dup.get(anchor_keys[0]) if anchor_keys else None
    same_author = set()
    if anchor_pid:
        same_author = {r[0] for r in con.execute(
            "SELECT DISTINCT b.paper_id FROM paper_authors a "
            "JOIN paper_authors b ON b.author_id = a.author_id "
            "WHERE a.paper_id = ? AND b.paper_id <> a.paper_id", (anchor_pid,))}

    # ---- (1) focus route, paper by paper ----
    focus = sorted((pid for pid, p in core.items() if p["tech_route"] == FOCUS_ROUTE),
                   key=lambda pid: (combo(pid), pid))
    focus_papers = [{
        "paper_id": pid,
        "title": core[pid]["title"],
        "year": core[pid]["year"],
        "entry_paths": sorted(paper_paths[pid]),
        "raw_record_keys": sorted(paper_keys[pid]),
        "ucb_affiliated": pid in ucb,
        "shares_author_with_berkeley_anchor": pid in same_author,
        "is_berkeley_anchor": pid == anchor_pid,
    } for pid in focus]
    focus_summary = {
        "core_papers": len(focus),
        "by_entry_kind_exclusive": route_entry[FOCUS_ROUTE]["by_entry_kind_exclusive"],
        "by_entry_path_nonexclusive": route_entry[FOCUS_ROUTE]["by_entry_path_nonexclusive"],
        "ucb_affiliated": sum(pid in ucb for pid in focus),
        "ucb_affiliated_by_entry_kind": sorted_counter(Counter(combo(pid) for pid in focus if pid in ucb)),
        "shares_author_with_berkeley_anchor": sum(pid in same_author for pid in focus),
        "shares_author_with_anchor_by_entry_kind": sorted_counter(
            Counter(combo(pid) for pid in focus if pid in same_author)),
    }

    # ---- (2) route counts without snowball-only papers ----
    no_snowball = Counter(p["tech_route"] for pid, p in core.items() if not snowball_only(pid))

    # ---- (3) snowball seeds ----
    seeds_on_disk = sorted({x.split(":", 1)[1] for ps in key_paths.values() for x in ps
                            if x.startswith("snowball:")})
    seeds_recomputed = load_snowball_seeds(cfg.get("snowball", {}).get("top_n", 10))
    seeds = []
    for sid in seeds_recomputed + [s for s in seeds_on_disk if s not in seeds_recomputed]:
        tag = f"snowball:{sid}"
        brought_keys = [k for k, ps in key_paths.items() if tag in ps]
        brought = {dup[k] for k in brought_keys if k in dup}
        brought_core = [pid for pid in brought if pid in core]
        spid = dup.get(f"openalex:{sid}")
        sp = papers.get(spid, {})
        seeds.append({
            "seed_openalex_id": sid,
            "paper_id": spid,
            "title": sp.get("title"),
            "year": sp.get("year"),
            "cited_by_count": sp.get("cited_by_count"),
            "tech_route": sp.get("tech_route"),
            "core_set": sp.get("core_set"),
            "ucb_affiliated": spid in ucb,
            "raw_records_brought_in": len(brought_keys),
            "brought_in_from_seed_reference_list": sum(
                k.split(":", 1)[1] in key_refs.get(f"openalex:{sid}", set()) for k in brought_keys),
            "papers_brought_in": len(brought),
            "core_papers_brought_in": len(brought_core),
            "core_brought_in_by_route": sorted_counter(Counter(core[p]["tech_route"] for p in brought_core)),
            "core_snowball_only_by_route": sorted_counter(
                Counter(core[p]["tech_route"] for p in brought_core if snowball_only(p))),
        })
    snowball_core = {pid for pid in core if any(kind(x) == "snowball" for x in paper_paths[pid])}
    berkeley_anchor = {
        "anchor_title": BERKELEY_ANCHOR,
        "in_queries_yaml_anchors": BERKELEY_ANCHOR in anchors,
        "raw_records_with_this_anchor_as_query": anchor_keys,
        "paper_id": anchor_pid,
        "paper": papers.get(anchor_pid),
        "all_entry_paths_of_paper": sorted(paper_paths.get(anchor_pid, [])),
        "ucb_affiliated": anchor_pid in ucb,
        "author_rows": con.execute("SELECT COUNT(*) FROM paper_authors WHERE paper_id = ?",
                                   (anchor_pid,)).fetchone()[0],
        "author_rows_with_institution": con.execute(
            "SELECT COUNT(*) FROM paper_authors WHERE paper_id = ? AND inst_id IS NOT NULL",
            (anchor_pid,)).fetchone()[0],
        "is_snowball_seed": bool(anchor_pid) and any(s["paper_id"] == anchor_pid for s in seeds),
        "core_papers_sharing_an_author_with_anchor": sorted(same_author & set(core)),
    }

    # ---- (4) every query in queries.yaml ----
    by_path_records = Counter(x for ps in key_paths.values() for x in ps)
    by_path_papers = defaultdict(set)
    for pid, ps in paper_paths.items():
        for x in ps:
            by_path_papers[x].add(pid)
    qlist = [("openalex", q) for q in cfg.get("openalex") or []] + \
            [("arxiv", q) for q in (cfg.get("arxiv") or {}).get("phrases") or []]
    queries = []
    for source, q in qlist:
        tag = f"query:{source}:{q}"
        pids = by_path_papers.get(tag, set())
        queries.append({
            "source": source,
            "query": q,
            "names_routes": QUERY_NAMES_ROUTE.get(q, []),
            "raw_records_first_found_by_this_query": by_path_records.get(tag, 0),
            # OpenAlex search matches words, not the phrase; these show how loose the match was
            "records_with_exact_phrase_in_title_or_abstract": sum(
                q.lower() in key_text[k] for k, ps in key_paths.items() if tag in ps),
            "records_with_print_in_title": sum(
                "print" in (key_title[k] or "").lower() for k, ps in key_paths.items() if tag in ps),
            "papers": len(pids),
            "papers_by_relevance_score": {str(k): v for k, v in sorted(
                Counter(papers[p]["relevance_score"] for p in pids).items(), key=lambda kv: str(kv[0]))},
            "core_papers": sum(p in core for p in pids),
            "core_by_route": sorted_counter(Counter(core[p]["tech_route"] for p in pids if p in core)),
        })

    # context: routes among extended (score 2 or tagged) papers that are not core
    ext_not_core = Counter(p["tech_route"] for p in papers.values()
                           if p["extended_set"] == 1 and p["core_set"] != 1)

    # ---- (5) projects.csv ----
    with open(PROJECTS_PATH, encoding="utf-8", newline="") as f:
        projects = [{k: row[k] for k in ("entity", "entity_type", "product_or_project", "tech_route",
                                         "stage", "evidence_url", "evidence_date")}
                    for row in csv.DictReader(f) if row["tech_route"] in PROJECT_ROUTES]

    # ---- self-checks ----
    assert sum(r["core_papers"] for r in route_entry.values()) == len(core)
    assert all(paper_paths[pid] for pid in core), "a core paper has no raw record"
    assert sum(no_snowball.values()) == len(core) - sum(snowball_only(p) for p in core)

    out = {
        "caveat": "Collectors skip a record_key already on disk, so each raw record carries only the "
                  "first query that found it. Per-query counts are lower bounds.",
        "raw_lines_per_file": dict(raw_lines),
        "unique_raw_record_keys": len(key_paths),
        "raw_keys_not_in_duplicates_table": raw_keys_not_in_duplicates,
        "papers": len(papers),
        "core_papers": len(core),
        "core_route_counts": sorted_counter(route_counts),
        "route_entry": route_entry,
        "q1_mems_silicon_photonic": {"summary": focus_summary, "papers": focus_papers},
        "q2_core_route_counts_without_snowball_only": sorted_counter(no_snowball),
        "q2_snowball_only_core_by_route": sorted_counter(
            Counter(p["tech_route"] for pid, p in core.items() if snowball_only(pid))),
        "q2_core_with_any_snowball_record": len(snowball_core),
        "q3_seeds_recomputed_now": seeds_recomputed,
        "q3_seeds_on_disk": seeds_on_disk,
        "q3_seed_lists_match": sorted(seeds_recomputed) == seeds_on_disk,
        "q3_seeds": seeds,
        "q3_berkeley_anchor": berkeley_anchor,
        "q4_queries": queries,
        "context_extended_not_core_route_counts": sorted_counter(ext_not_core),
        "q5_projects_csv": projects,
    }
    out_path = REPO_ROOT / args.out
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"wrote {out_path}  core={len(core)}  {FOCUS_ROUTE}={len(focus)}  seeds={len(seeds)}")


if __name__ == "__main__":
    main()
