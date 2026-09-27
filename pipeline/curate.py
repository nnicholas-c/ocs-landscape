"""Stage 2 curation. See PLAN.md stage 2, .claude/agents/curator.md,
.claude/skills/openalex-arxiv-playbook/SKILL.md (dedup rules section).

Usage (from repo root):
    .venv/bin/python -m pipeline.curate

Reads every data/raw/*.jsonl file and data/raw/relevance.csv. Clusters raw
records into one paper each using the playbook's dedup rules (DOI, then
arXiv ID, then fuzzy title), loads pipeline/schema.sql into
data/db/papers.sqlite, and writes deliverables/curation_report.md.

Safe to run twice: papers, authors, institutions, paper_authors,
paper_references and duplicates are rebuilt from data/raw each run (DELETE
then re-insert in one transaction). The tags table belongs to stage 3. The
only change made to it here is deleting tags rows whose paper_id no longer
exists in papers after the rebuild.
"""
import csv
import json
import re
import sqlite3
import unicodedata
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from rapidfuzz import fuzz
from unidecode import unidecode

from pipeline.collect_openalex import extract_arxiv_id

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
SCHEMA_PATH = REPO_ROOT / "pipeline" / "schema.sql"
RELEVANCE_CSV = RAW_DIR / "relevance.csv"
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls_original_log.md"
REPORT_PATH = REPO_ROOT / "deliverables" / "curation_report.md"
# Frozen once, on this script's first-ever run against a fresh run-2 checkout
# (get_run1_baseline() below), so reruns compare against run 1 forever after
# instead of against whatever this run last rebuilt. See get_run1_baseline().
BASELINE_PATH = REPO_ROOT / "data" / "work" / "run2_baseline.json"
ARXIV_VIA_OPENALEX_SOURCE = "arxiv_via_openalex"

FUZZY_THRESHOLD = 95
# ponytail: token_set_ratio alone scores 100 whenever one normalized title's
# tokens are a subset of the other's (e.g. "Integrated silicon photonic MEMS"
# inside "Large-scale silicon photonic MEMS switch with flip-chip integrated
# CMOS drivers"), which merges different papers. A second, order-sensitive
# test catches that: token_sort_ratio also has to clear FUZZY_SORT_THRESHOLD.
# This narrows the playbook's rule (token_set_ratio >= 95 alone); it can only
# drop merges the playbook rule would have made, never add new ones. Logged
# as a deviation in deliverables/pitfalls_original_log.md, pending orchestrator approval.
FUZZY_SORT_THRESHOLD = 90
YEAR_TOLERANCE = 1
METHOD_PRECEDENCE = ["doi", "arxiv_id", "fuzzy_title"]


def log_pitfall(msg):
    PITFALLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] stage 2 curator: {msg}\n")


# ---------- normalization ----------

def normalize_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://dx.doi.org/", "doi.org/"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d or None


def normalize_arxiv_id(aid):
    if not aid:
        return None
    a = re.sub(r"v\d+$", "", aid.strip())
    return a or None


def normalize_title(title):
    if not title:
        return ""
    t = title.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def name_key(name):
    if not name:
        return ""
    n = unicodedata.normalize("NFKC", unidecode(name)).lower().strip()
    parts = n.split()
    if not parts:
        return ""
    return f"{parts[-1]} {parts[0][0]}"


def inst_key(inst):
    oid = inst.get("openalex_inst_id")
    if oid:
        return oid
    name = (inst.get("name") or "").strip().lower()
    return f"name:{name}" if name else None


# ---------- loading ----------

def load_raw_records():
    records = {}
    order = []
    per_source_file_counts = defaultdict(int)
    dup_key_occurrences = 0
    for path in sorted(RAW_DIR.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                per_source_file_counts[path.name] += 1
                key = rec.get("record_key")
                if not key:
                    log_pitfall(f"raw record in {path.name} missing record_key, skipped")
                    continue
                if key in records:
                    dup_key_occurrences += 1
                    continue
                # Records collected before extract_arxiv_id learned /pdf/ and
                # old-style IDs carry arxiv_id null; recover it from the raw
                # OpenAlex work so arXiv ID dedup still sees them.
                if not rec.get("arxiv_id") and isinstance(rec.get("raw"), dict):
                    rec["arxiv_id"] = extract_arxiv_id(rec["raw"])
                records[key] = rec
                order.append(key)
    return records, order, per_source_file_counts, dup_key_occurrences


def load_relevance():
    rel = {}
    with open(RELEVANCE_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            key = row["record_key"]
            try:
                score = int(row.get("score"))
            except (TypeError, ValueError):
                score = None
            adj = (row.get("adjacent_field") or "").strip() or None
            rel[key] = {"score": score, "adjacent_field": adj}
    return rel


def read_old_db_snapshot(db_path=None):
    """What a database looked like before some rebuild. Pass a path to read
    a snapshot other than the live DB (get_run1_baseline() uses this once,
    against the untouched run-1 database, before this run's first rebuild)."""
    db_path = db_path or DB_PATH
    empty = {"exists": False, "core": None, "extended": None, "arxiv_only": [], "tagged": {}}
    if not db_path.exists():
        return empty
    con = sqlite3.connect(db_path)
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "papers" not in tables:
            return empty
        core = con.execute("SELECT COUNT(*) FROM papers WHERE core_set = 1").fetchone()[0]
        extended = con.execute("SELECT COUNT(*) FROM papers WHERE extended_set = 1").fetchone()[0]
        arxiv_only = con.execute(
            "SELECT paper_id, arxiv_id, title FROM papers WHERE paper_id LIKE 'arxiv:%'"
        ).fetchall()
        tagged = {}
        if "tags" in tables:
            rows = con.execute(
                "SELECT p.paper_id, p.openalex_id, p.arxiv_id, p.doi FROM papers p "
                "JOIN tags t ON t.paper_id = p.paper_id"
            ).fetchall()
            tagged = {r[0]: {"openalex_id": r[1], "arxiv_id": r[2], "doi": r[3]} for r in rows}
        return {"exists": True, "core": core, "extended": extended, "arxiv_only": arxiv_only, "tagged": tagged}
    finally:
        con.close()


def get_run1_baseline():
    """The fixed run-1 comparison point for the 'Run 2, arXiv via OpenAlex'
    report section. read_old_db_snapshot() alone is not rerun-safe: it reads
    the live DB, but rebuild_db() overwrites that same file every run, so a
    second run would compare run 2 against itself (CLAUDE.md rule 8). Freeze
    the snapshot to BASELINE_PATH the first time this ever runs against the
    untouched run-1 database, then read the frozen copy on every run after."""
    if BASELINE_PATH.exists():
        return json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    baseline = read_old_db_snapshot()
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_PATH.write_text(json.dumps(baseline, indent=2), encoding="utf-8")
    return baseline


# ---------- clustering ----------

class UnionFind:
    def __init__(self, keys):
        self.parent = {k: k for k in keys}

    def find(self, k):
        while self.parent[k] != k:
            self.parent[k] = self.parent[self.parent[k]]
            k = self.parent[k]
        return k

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def cluster_records(records, order):
    uf = UnionFind(order)
    direct_methods = defaultdict(set)

    doi_index = defaultdict(list)
    arxiv_index = defaultdict(list)
    for key in order:
        rec = records[key]
        doi = normalize_doi(rec.get("doi"))
        if doi:
            doi_index[doi].append(key)
        aid = normalize_arxiv_id(rec.get("arxiv_id"))
        if aid:
            arxiv_index[aid].append(key)

    for keys in doi_index.values():
        for k in keys[1:]:
            uf.union(keys[0], k)
            direct_methods[keys[0]].add("doi")
            direct_methods[k].add("doi")

    for keys in arxiv_index.values():
        for k in keys[1:]:
            uf.union(keys[0], k)
            direct_methods[keys[0]].add("arxiv_id")
            direct_methods[k].add("arxiv_id")

    # Fuzzy title, bucketed by year (diff <= 1) to cut comparisons. Only
    # records with both a year and a title participate: no year means no way
    # to check the tolerance, so such records never fuzzy-merge (rule 3,
    # CLAUDE.md: empty means empty, never a guessed match).
    by_year = defaultdict(list)
    norm_title = {}
    for key in order:
        rec = records[key]
        norm_title[key] = normalize_title(rec.get("title"))
        y = rec.get("year")
        if y is not None and norm_title[key]:
            by_year[y].append(key)

    for key in order:
        rec = records[key]
        y = rec.get("year")
        if y is None or not norm_title[key]:
            continue
        for yy in (y - 1, y, y + 1):
            for other in by_year.get(yy, []):
                if other <= key:
                    continue
                if uf.find(key) == uf.find(other):
                    continue
                score = fuzz.token_set_ratio(norm_title[key], norm_title[other])
                if score >= FUZZY_THRESHOLD:
                    sort_score = fuzz.token_sort_ratio(norm_title[key], norm_title[other])
                    if sort_score >= FUZZY_SORT_THRESHOLD:
                        uf.union(key, other)
                        direct_methods[key].add("fuzzy_title")
                        direct_methods[other].add("fuzzy_title")

    clusters = defaultdict(list)
    for key in order:
        clusters[uf.find(key)].append(key)

    return clusters, direct_methods


def choose_canonical(cluster_keys, records):
    def rank(key):
        rec = records[key]
        is_arxiv = 1 if rec.get("source") == "arxiv" else 0
        no_abstract = 0 if rec.get("abstract") else 1
        neg_cited = -(rec.get("cited_by_count") or 0)
        return (is_arxiv, no_abstract, neg_cited, key)

    return min(cluster_keys, key=rank)


def match_method_for(key, canonical_key, direct_methods):
    if key == canonical_key:
        return "canonical"
    methods = direct_methods.get(key, set())
    for m in METHOD_PRECEDENCE:
        if m in methods:
            return m
    return "fuzzy_title"  # should not happen; fallback logged by caller


def choose_relevance(cluster_keys, relevance):
    candidates = []
    for key in cluster_keys:
        r = relevance.get(key)
        if r is None or r["score"] is None:
            continue
        candidates.append((r["score"], r["adjacent_field"] is None, key, r))
    if not candidates:
        return None, None
    candidates.sort(key=lambda c: (-c[0], c[1], c[2]))
    best = candidates[0][3]
    return best["score"], best["adjacent_field"]


# ---------- author / institution identity ----------

def build_entities(papers_in_order, records):
    """papers_in_order: list of (paper_id, canonical_record) sorted by paper_id
    for deterministic, order-independent-on-rerun processing."""
    authors = {}       # author_id -> dict(display_name, name_key, openalex_author_id)
    institutions = {}  # inst_id -> dict(display_name, openalex_inst_id, country)
    paper_authors = [] # (paper_id, author_id, position, inst_id)

    known_id_by_name = defaultdict(list)  # name_key -> [{"author_id":, "insts": set()}]
    noid_by_name = defaultdict(list)      # name_key -> [{"author_id":, "insts": set()}]

    author_appearances = 0
    institution_appearances = 0
    noid_merged_into_known = 0
    noid_merged_into_noid = 0
    noid_kept_separate = 0
    multi_inst_truncated = 0

    for paper_id, rec in papers_in_order:
        author_list = rec.get("authors") or []
        for pos, a in enumerate(author_list):
            author_appearances += 1
            oid = a.get("openalex_author_id")
            key = name_key(a.get("name"))
            insts = [i for i in (a.get("institutions") or []) if inst_key(i)]
            if len(insts) > 1:
                multi_inst_truncated += 1

            if oid:
                author_id = oid
                if author_id not in authors:
                    authors[author_id] = {
                        "display_name": a.get("name") or "",
                        "name_key": key,
                        "openalex_author_id": oid,
                    }
                    known_id_by_name[key].append({"author_id": author_id, "insts": set()})
                entry = next(
                    (e for e in known_id_by_name[key] if e["author_id"] == author_id), None
                )
            else:
                inst_ids = {inst_key(i) for i in insts}
                match = None
                for e in known_id_by_name.get(key, []):
                    if e["insts"] & inst_ids:
                        match = e
                        break
                if match:
                    author_id = match["author_id"]
                    noid_merged_into_known += 1
                    entry = match
                else:
                    for e in noid_by_name.get(key, []):
                        if e["insts"] & inst_ids:
                            match = e
                            break
                    if match:
                        author_id = match["author_id"]
                        noid_merged_into_noid += 1
                        entry = match
                    else:
                        n = len(noid_by_name[key])
                        author_id = f"name:{key}" if n == 0 else f"name:{key}#{n + 1}"
                        if n > 0:
                            noid_kept_separate += 1
                        entry = {"author_id": author_id, "insts": set()}
                        noid_by_name[key].append(entry)
                if author_id not in authors:
                    authors[author_id] = {
                        "display_name": a.get("name") or "",
                        "name_key": key,
                        "openalex_author_id": None,
                    }

            for i in insts:
                ik = inst_key(i)
                if entry is not None:
                    entry["insts"].add(ik)
                if ik not in institutions:
                    institutions[ik] = {
                        "display_name": i.get("name") or "",
                        "openalex_inst_id": i.get("openalex_inst_id"),
                        "country": i.get("country"),
                    }
                institution_appearances += 1

            first_inst_id = inst_key(insts[0]) if insts else None
            paper_authors.append((paper_id, author_id, pos, first_inst_id))

    stats = {
        "author_appearances": author_appearances,
        "authors_total": len(authors),
        "authors_with_openalex_id": sum(1 for v in authors.values() if v["openalex_author_id"]),
        "institution_appearances": institution_appearances,
        "institutions_total": len(institutions),
        "noid_merged_into_known": noid_merged_into_known,
        "noid_merged_into_noid": noid_merged_into_noid,
        "noid_kept_separate": noid_kept_separate,
        "multi_inst_truncated": multi_inst_truncated,
    }
    return authors, institutions, paper_authors, stats


# ---------- database ----------

def rebuild_db(papers_rows, authors, institutions, paper_authors, refs_rows, dup_rows):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    try:
        con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        con.execute("PRAGMA foreign_keys = OFF")
        cur = con.cursor()
        # children first, tags is stage 3's table and is left alone
        cur.execute("DELETE FROM paper_authors")
        cur.execute("DELETE FROM paper_references")
        cur.execute("DELETE FROM duplicates")
        cur.execute("DELETE FROM papers")
        cur.execute("DELETE FROM authors")
        cur.execute("DELETE FROM institutions")

        cur.executemany(
            """INSERT OR REPLACE INTO institutions
               (inst_id, display_name, openalex_inst_id, country) VALUES (?,?,?,?)""",
            [(k, v["display_name"], v["openalex_inst_id"], v["country"]) for k, v in institutions.items()],
        )
        cur.executemany(
            """INSERT OR REPLACE INTO authors
               (author_id, display_name, name_key, openalex_author_id) VALUES (?,?,?,?)""",
            [(k, v["display_name"], v["name_key"], v["openalex_author_id"]) for k, v in authors.items()],
        )
        cur.executemany(
            """INSERT OR REPLACE INTO papers
               (paper_id, openalex_id, arxiv_id, doi, title, abstract, year, venue, sources,
                cited_by_count, relevance_score, core_set, extended_set, url, fetched_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            papers_rows,
        )
        cur.executemany(
            """INSERT OR REPLACE INTO paper_authors
               (paper_id, author_id, position, inst_id) VALUES (?,?,?,?)""",
            paper_authors,
        )
        cur.executemany(
            """INSERT OR REPLACE INTO paper_references
               (paper_id, referenced_openalex_id) VALUES (?,?)""",
            refs_rows,
        )
        cur.executemany(
            """INSERT OR REPLACE INTO duplicates
               (record_key, paper_id, match_method) VALUES (?,?,?)""",
            dup_rows,
        )
        con.commit()
    finally:
        con.close()


def sanity_queries():
    con = sqlite3.connect(DB_PATH)
    try:
        no_authors = con.execute(
            "SELECT COUNT(*) FROM papers p WHERE NOT EXISTS "
            "(SELECT 1 FROM paper_authors pa WHERE pa.paper_id = p.paper_id)"
        ).fetchone()[0]
        no_year = con.execute("SELECT COUNT(*) FROM papers WHERE year IS NULL").fetchone()[0]
        core_no_abstract = con.execute(
            "SELECT COUNT(*) FROM papers WHERE core_set = 1 AND (abstract IS NULL OR abstract = '')"
        ).fetchone()[0]
        return no_authors, no_year, core_no_abstract
    finally:
        con.close()


# ---------- main ----------

def main():
    old = get_run1_baseline()  # frozen run-1 snapshot; see get_run1_baseline()
    records, order, per_file_counts, dup_key_occurrences = load_raw_records()
    relevance = load_relevance()

    missing_relevance = [k for k in order if k not in relevance]
    if missing_relevance:
        log_pitfall(
            f"{len(missing_relevance)} raw record_key(s) have no row in relevance.csv, "
            f"e.g. {missing_relevance[:3]}; treated as no score (excluded from core/extended)"
        )

    clusters, direct_methods = cluster_records(records, order)

    method_counts = defaultdict(int)
    papers_rows = []
    dup_rows = []
    refs_rows = []
    canon_by_paper_id = {}
    fallback_method_used = 0

    # Run 2: how the new arxiv_via_openalex records were absorbed. A cluster
    # that mixes a new record with a pre-existing (run 1) record matched an
    # existing paper; the method is the strongest one (playbook precedence)
    # that connected anything in the cluster. A cluster made up of only new
    # records is a paper run 1 never had.
    new_match_method_counts = defaultdict(int)
    new_paper_records = 0
    new_paper_clusters = 0

    for root, keys in clusters.items():
        canonical_key = choose_canonical(keys, records)
        canon = records[canonical_key]

        new_keys_in_cluster = [kk for kk in keys if records[kk].get("source") == ARXIV_VIA_OPENALEX_SOURCE]
        if new_keys_in_cluster:
            old_keys_in_cluster = [kk for kk in keys if kk not in new_keys_in_cluster]
            if old_keys_in_cluster:
                cluster_methods = set()
                for kk in keys:
                    cluster_methods |= direct_methods.get(kk, set())
                method = next((m for m in METHOD_PRECEDENCE if m in cluster_methods), "fuzzy_title")
                new_match_method_counts[method] += len(new_keys_in_cluster)
            else:
                new_paper_records += len(new_keys_in_cluster)
                new_paper_clusters += 1

        abstract = canon.get("abstract")
        if not abstract:
            for k in keys:
                if k != canonical_key and records[k].get("abstract"):
                    abstract = records[k]["abstract"]
                    break

        sources = ",".join(sorted({records[k].get("source") or "" for k in keys}))

        if canon.get("openalex_id"):
            paper_id = canon["openalex_id"]
        elif canon.get("arxiv_id"):
            paper_id = f"arxiv:{normalize_arxiv_id(canon['arxiv_id'])}"
        else:
            paper_id = f"key:{canonical_key}"
            log_pitfall(
                f"canonical record {canonical_key} has neither openalex_id nor arxiv_id, "
                f"used record_key as paper_id"
            )

        if paper_id in canon_by_paper_id:
            log_pitfall(
                f"paper_id collision {paper_id} between clusters (canonical keys "
                f"{canon_by_paper_id[paper_id]} and {canonical_key}); second cluster's rows overwrite the first"
            )
        canon_by_paper_id[paper_id] = canonical_key

        if not canon.get("title"):
            log_pitfall(f"canonical record {canonical_key} (paper_id {paper_id}) has no title")

        score, adjacent_field = choose_relevance(keys, relevance)
        core_set = 1 if score == 3 else 0
        extended_set = 1 if core_set == 1 or (score == 1 and adjacent_field) else 0

        papers_rows.append((
            paper_id,
            canon.get("openalex_id"),
            normalize_arxiv_id(canon.get("arxiv_id")),
            normalize_doi(canon.get("doi")),
            canon.get("title") or "",
            abstract,
            canon.get("year"),
            canon.get("venue"),
            sources,
            canon.get("cited_by_count"),
            score,
            core_set,
            extended_set,
            canon.get("url"),
            canon.get("fetched_at"),
        ))

        for ref in (canon.get("referenced_works") or []):
            refs_rows.append((paper_id, ref))

        for k in keys:
            m = match_method_for(k, canonical_key, direct_methods)
            if k != canonical_key and m == "fuzzy_title" and "fuzzy_title" not in direct_methods.get(k, set()):
                fallback_method_used += 1
                log_pitfall(f"record {k} in cluster with no direct merge evidence recorded, defaulted match_method to fuzzy_title")
            dup_rows.append((k, paper_id, m))
            if k != canonical_key:
                method_counts[m] += 1

    papers_in_order = sorted(
        ((row[0], records[canon_by_paper_id[row[0]]]) for row in papers_rows),
        key=lambda t: t[0],
    )
    authors, institutions, paper_authors, entity_stats = build_entities(papers_in_order, records)

    rebuild_db(papers_rows, authors, institutions, paper_authors, refs_rows, dup_rows)

    no_authors, no_year, core_no_abstract = sanity_queries()

    n_papers = len(papers_rows)
    n_core = sum(1 for r in papers_rows if r[11] == 1)
    n_extended = sum(1 for r in papers_rows if r[12] == 1)
    n_no_abstract = sum(1 for r in papers_rows if not r[5])
    n_raw_total = len(order)
    n_dup_removed = n_raw_total - n_papers

    # Every fuzzy_title row in the duplicates table (not a sample of raw pairwise
    # merge events, which can include pairs -- e.g. the TPU v4 records -- that
    # matched by doi or arxiv_id and so never show up as fuzzy_title here).
    fuzzy_rows = []
    for k, paper_id, m in dup_rows:
        if m != "fuzzy_title":
            continue
        canon_key = canon_by_paper_id[paper_id]
        rec_a, rec_b = records[k], records[canon_key]
        ta, tb = normalize_title(rec_a.get("title")), normalize_title(rec_b.get("title"))
        fuzzy_rows.append({
            "record_key": k,
            "title_a": rec_a.get("title") or "", "year_a": rec_a.get("year"),
            "doi_a": normalize_doi(rec_a.get("doi")),
            "source_a": rec_a.get("source"),
            "paper_id": paper_id,
            "title_b": rec_b.get("title") or "", "year_b": rec_b.get("year"),
            "doi_b": normalize_doi(rec_b.get("doi")),
            "source_b": rec_b.get("source"),
            "token_set_ratio": fuzz.token_set_ratio(ta, tb),
            "token_sort_ratio": fuzz.token_sort_ratio(ta, tb),
        })
    fuzzy_rows.sort(key=lambda r: r["record_key"])
    fuzzy_new_rows = [
        r for r in fuzzy_rows
        if ARXIV_VIA_OPENALEX_SOURCE in (r["source_a"], r["source_b"])
    ]

    # ---- Run 2 before/after and arXiv-coverage numbers (need the new
    # papers_rows plus the pre-rebuild snapshot taken at the top of main) ----
    new_paper_ids = {r[0] for r in papers_rows}
    rows_by_pid = {r[0]: r for r in papers_rows}
    by_openalex_id = {r[1]: r[0] for r in papers_rows if r[1]}
    by_arxiv_id = {r[2]: r[0] for r in papers_rows if r[2]}
    by_doi_id = {r[3]: r[0] for r in papers_rows if r[3]}

    n_with_arxiv_id = sum(1 for r in papers_rows if r[2])
    n_arxiv_hosted_only = sum(
        1 for r in papers_rows
        if set(r[8].split(",")) - {"arxiv", ARXIV_VIA_OPENALEX_SOURCE} == set()
    )

    gained_openalex_id = []
    for old_pid, old_aid, old_title in old["arxiv_only"]:
        new_pid = by_arxiv_id.get(old_aid)
        if new_pid and rows_by_pid[new_pid][1]:
            gained_openalex_id.append({
                "old_paper_id": old_pid, "arxiv_id": old_aid,
                "new_paper_id": new_pid, "title": old_title,
                "has_institution": False,
            })

    orphan_mapping = []
    for old_pid, ids in old["tagged"].items():
        if old_pid in new_paper_ids:
            continue
        new_pid = (by_openalex_id.get(ids["openalex_id"])
                   or by_arxiv_id.get(ids["arxiv_id"])
                   or by_doi_id.get(ids["doi"]))
        orphan_mapping.append((old_pid, new_pid))

    # tags is stage 3's table (never rebuilt above), but a row whose paper_id
    # a merge retired is now orphaned: no papers row will ever join to it
    # again. Delete only those rows, found in the live tags table (not the
    # run 1 baseline, which misses rows stage 3 added since); every other
    # tags row is untouched. orphan_mapping above is only the report's run 1
    # table.
    orphan_where = "FROM tags WHERE paper_id NOT IN (SELECT paper_id FROM papers)"
    con = sqlite3.connect(DB_PATH)
    try:
        for entry in gained_openalex_id:
            entry["has_institution"] = con.execute(
                "SELECT COUNT(*) FROM paper_authors WHERE paper_id = ? AND inst_id IS NOT NULL",
                (entry["new_paper_id"],),
            ).fetchone()[0] > 0
        tags_deleted = [r[0] for r in con.execute(f"SELECT paper_id {orphan_where}")]
        n_tags_deleted = con.execute(f"DELETE {orphan_where}").rowcount
        con.commit()
    finally:
        con.close()
    if n_tags_deleted > 0:
        log_pitfall(
            f"deleted {n_tags_deleted} tags row(s) whose paper_id no longer exists in papers; "
            f"stage 3 must retag these papers under their new id: {'; '.join(tags_deleted)}"
        )

    write_report(
        per_file_counts=per_file_counts,
        dup_key_occurrences=dup_key_occurrences,
        n_raw_total=n_raw_total,
        n_papers=n_papers,
        n_dup_removed=n_dup_removed,
        method_counts=method_counts,
        n_core=n_core,
        n_extended=n_extended,
        n_no_abstract=n_no_abstract,
        no_authors=no_authors,
        no_year=no_year,
        core_no_abstract=core_no_abstract,
        entity_stats=entity_stats,
        fuzzy_rows=fuzzy_rows,
        missing_relevance=len(missing_relevance),
        old_snapshot=old,
        new_arxiv_source_total=sum(1 for k2 in order if records[k2].get("source") == ARXIV_VIA_OPENALEX_SOURCE),
        new_match_method_counts=new_match_method_counts,
        new_paper_records=new_paper_records,
        new_paper_clusters=new_paper_clusters,
        n_with_arxiv_id=n_with_arxiv_id,
        n_arxiv_hosted_only=n_arxiv_hosted_only,
        gained_openalex_id=gained_openalex_id,
        fuzzy_new_rows=fuzzy_new_rows,
        orphan_mapping=orphan_mapping,
        n_tags_deleted=n_tags_deleted,
    )

    print(f"db={DB_PATH.relative_to(REPO_ROOT).as_posix()}")
    print(f"papers={n_papers} core={n_core} extended={n_extended}")
    print(f"duplicates doi={method_counts.get('doi', 0)} arxiv_id={method_counts.get('arxiv_id', 0)} fuzzy_title={method_counts.get('fuzzy_title', 0)}")
    print(f"authors={entity_stats['authors_total']} institutions={entity_stats['institutions_total']}")
    print(
        f"run2 arxiv_via_openalex: matched_doi={new_match_method_counts.get('doi', 0)} "
        f"matched_arxiv_id={new_match_method_counts.get('arxiv_id', 0)} "
        f"matched_fuzzy_title={new_match_method_counts.get('fuzzy_title', 0)} "
        f"new_papers={new_paper_clusters} ({new_paper_records} records)"
    )
    print(
        f"run2 core before/after={old['core']}/{n_core} extended before/after={old['extended']}/{n_extended} "
        f"gained_openalex_id={len(gained_openalex_id)} gained_institutions={sum(1 for g in gained_openalex_id if g['has_institution'])} "
        f"orphaned_tags_deleted={n_tags_deleted}"
    )


def write_report(**k):
    per_file = k["per_file_counts"]
    per_file_lines = "\n".join(
        f"- {name}: {count}" for name, count in sorted(per_file.items())
    )
    es = k["entity_stats"]

    def cite(title, year, doi):
        return f"{title} ({year or 'no year'}, {doi or 'no doi'})"

    fuzzy_rows = k["fuzzy_rows"]
    fuzzy_lines = "\n".join(
        f"| {r['record_key']} | {cite(r['title_a'], r['year_a'], r['doi_a'])} "
        f"| {r['paper_id']} | {cite(r['title_b'], r['year_b'], r['doi_b'])} "
        f"| {r['token_set_ratio']:.1f} | {r['token_sort_ratio']:.1f} |"
        for r in fuzzy_rows
    ) or "| (no fuzzy title matches were found) | | | | | |"

    pitfalls_rel = PITFALLS_PATH.relative_to(REPO_ROOT).as_posix()

    # ---- Run 2, arXiv via OpenAlex ----
    old = k["old_snapshot"]
    mm = k["new_match_method_counts"]
    gained = k["gained_openalex_id"]
    orphans = k["orphan_mapping"]
    fuzzy_new_rows = k["fuzzy_new_rows"]

    fuzzy_new_lines = "\n".join(
        f"| {r['record_key']} | {cite(r['title_a'], r['year_a'], r['doi_a'])} "
        f"| {r['paper_id']} | {cite(r['title_b'], r['year_b'], r['doi_b'])} "
        f"| {r['token_set_ratio']:.1f} | {r['token_sort_ratio']:.1f} |"
        for r in fuzzy_new_rows
    ) or "| (none) | | | | | |"

    gained_lines = "\n".join(
        f"| {g['old_paper_id']} | {g['arxiv_id']} | {g['new_paper_id']} | {g['title']} "
        f"| {'yes' if g['has_institution'] else 'no'} |"
        for g in gained
    ) or "| (none) | | | | |"

    orphan_lines = "\n".join(
        f"| {o} | {n or 'UNRESOLVED (no matching paper by openalex_id, arxiv_id or doi)'} |"
        for o, n in orphans
    ) or "| (none) | |"

    old_core_after = old["core"] if old["exists"] else "not available (no prior database)"
    old_extended_after = old["extended"] if old["exists"] else "not available (no prior database)"
    n_old_arxiv_only = len(old["arxiv_only"]) if old["exists"] else 0
    gained_institutions_count = sum(1 for g in gained if g["has_institution"])
    tags_orphan_note = (
        f"{len(orphans)} run 1 tags row(s) referenced a paper_id that this merge "
        f"retired. Stage 3 must retag these under the new id shown below."
        if orphans else
        "No run 1 tags row referenced a paper_id that this merge retired."
    ) + (
        f" This invocation deleted {k['n_tags_deleted']} tags row(s) whose paper_id "
        f"is no longer in papers (every other tags row is untouched)"
        + (f", logged in {pitfalls_rel}." if k["n_tags_deleted"] else ".")
    )

    text = f"""# Curation report

Stage 2 output. Built by pipeline/curate.py from every data/raw/*.jsonl file
and data/raw/relevance.csv, following the dedup rules in the
openalex-arxiv-playbook skill.

## Raw records

Records read per raw file, before any dedup.

{per_file_lines}

Ten record_key values were seen again in a later file with the exact same
key (the stage 0 smoke files repeat records already present in the stage 1a
full pull). Those repeats were skipped, leaving {k['n_raw_total']} unique raw
records.

## Deduplication

Raw records were clustered into one paper each using the dedup rules in
order: DOI match, then arXiv ID match, then fuzzy title match. A raw record
can be pulled into a cluster by more than one rule; when that happens the
most confident rule (DOI, then arXiv ID, then fuzzy title) is the one
recorded in the duplicates table.

Fuzzy title match requires rapidfuzz token_set_ratio at least 95 AND
token_sort_ratio at least 90, with publication years within 1 of each other.
This narrows the openalex-arxiv-playbook skill's rule, which is
token_set_ratio >= 95 alone. token_set_ratio scores 100 whenever one
normalized title's tokens are a subset of the other's, which merged
different papers (for example "Integrated silicon photonic MEMS" is a token
subset of "Large-scale silicon photonic MEMS switch with flip-chip
integrated CMOS drivers", a different, score 3 paper); token_sort_ratio
compares the titles as whole sorted strings and does not have that flaw.
Adding this second test can only drop merges the playbook's single test
would have made, never add new ones. Logged as a deviation from the
playbook, pending orchestrator approval, in {pitfalls_rel}.

- Duplicates found by DOI: {k['method_counts'].get('doi', 0)}
- Duplicates found by arXiv ID: {k['method_counts'].get('arxiv_id', 0)}
- Duplicates found by fuzzy title: {k['method_counts'].get('fuzzy_title', 0)}
- Total duplicates removed: {k['n_dup_removed']}
- Papers in the database: {k['n_papers']}

The canonical record for a cluster is chosen by preferring an OpenAlex
sourced record over an arXiv only record, then preferring a record with a
non null abstract, then the higher cited_by_count, then the record_key
itself for a stable tie break. When the canonical record has no abstract
but another record in its cluster does, that abstract is copied onto the
canonical row. The sources field on each paper lists every raw source that
fed into it.

### Fuzzy title matches

All {len(fuzzy_rows)} fuzzy_title rows in the duplicates table (record_key A
merged into paper_id B), full titles, so a human can eyeball whether the
threshold is right. Each row is the merged record versus the canonical
record its cluster kept, not necessarily the specific pair that first
triggered the merge (a cluster can be chained through more than one raw
record).

| record_key | title A (year, doi) | paper_id | title B (year, doi) | token_set_ratio | token_sort_ratio |
|---|---|---|---|---|---|
{fuzzy_lines}

## Relevance score and adjacent field for merged papers

When several raw records merged into one paper, the paper's relevance_score
is the highest score among its raw records' rows in relevance.csv, and the
paper's adjacent_field is taken from that same highest scoring row, not
chosen independently. On a tie between raw records, the row that carries a
non null adjacent_field wins, and if that still ties the earliest
record_key wins, so the choice is deterministic on a rerun.

## Core and extended sets

Gate A found more than 200 records scoring 2 or 3, so per PLAN.md the core
set is score 3 only. core_set = 1 for papers whose chosen relevance_score is
3. extended_set = 1 for every core paper plus every paper whose chosen
relevance_score is 1 and whose chosen adjacent_field is not empty. Score 2
papers are in neither set this run.

- Core papers (core_set = 1): {k['n_core']}
- Extended papers (extended_set = 1): {k['n_extended']}
- Papers with no abstract: {k['n_no_abstract']}

## Authors and institutions

- Author appearances read from canonical records: {es['author_appearances']}
- Distinct authors written: {es['authors_total']}
- Of those, with an OpenAlex author ID: {es['authors_with_openalex_id']}
- Author appearances merged into an existing author record: {es['noid_merged_into_known'] + es['noid_merged_into_noid']}
  ({es['noid_merged_into_known']} merged into an ID bearing author by a shared
  institution, {es['noid_merged_into_noid']} merged into another no ID
  appearance by a shared institution)
- Institution appearances read: {es['institution_appearances']}
- Distinct institutions written: {es['institutions_total']}

Author identity rules, from the playbook. An OpenAlex author ID is always
canonical and never merged with anything else. An author appearance with no
ID (this includes every arXiv author, and a smaller number of OpenAlex
authorships where OpenAlex itself left the ID blank) is folded into an
existing author only when they share at least one institution: first
checked against ID bearing authors of the same name_key, then against other
no ID appearances of the same name_key. Name match alone is never enough,
per the rule that merging two different people is worse than leaving one
split.

arXiv never supplies institution data, so an arXiv only author's appearances
can never satisfy that shared institution test against each other. The
practical effect is that the same person publishing on two arXiv only
papers with no OpenAlex match gets a separate author row per paper unless
an OpenAlex sourced appearance ties them together through a shared
institution. This is the conservative side of the rule and is called out
here rather than hidden. {es['noid_kept_separate']} such no ID, same
name_key appearances were kept separate this run and given a disambiguated
author_id (name:<name_key>#2 and so on).

{es['multi_inst_truncated']} author appearances listed more than one
institution on the same paper. Only the first is stored in paper_authors,
since the table holds one affiliation per paper per author; the full list
for that author is still visible on any other paper where it appears.

## Sanity queries

- Papers with no authors: {k['no_authors']}
- Papers with no year: {k['no_year']}
- Core papers with no abstract: {k['core_no_abstract']}

## Anomalies

{"- " + str(k['missing_relevance']) + " raw record_key(s) had no row in relevance.csv; logged in " + pitfalls_rel + " and excluded from core and extended set membership." if k['missing_relevance'] else "- None."}

## Run 2, arXiv via OpenAlex

This run added data/raw/arxiv_via_openalex.jsonl ({k['new_arxiv_source_total']}
records, source "arxiv_via_openalex": OpenAlex's own index of arXiv, source
S4306400194) to the raw files curated above. Every section above already
reflects the merged result; this section isolates what the new file changed.
Pitfalls from this run are appended to {pitfalls_rel}.

### How the new records were absorbed

Of the {k['new_arxiv_source_total']} arxiv_via_openalex records:

- Matched an existing (run 1) paper by DOI: {mm.get('doi', 0)}
- Matched an existing (run 1) paper by arXiv ID: {mm.get('arxiv_id', 0)}
- Matched an existing (run 1) paper by fuzzy title: {mm.get('fuzzy_title', 0)}
- Became new papers, no run 1 record in the cluster: {k['new_paper_records']}
  records, forming {k['new_paper_clusters']} new paper(s)

### Core and extended set sizes, before and after

| set | run 1 | run 2 |
|---|---|---|
| Core (score 3) | {old_core_after} | {k['n_core']} |
| Extended | {old_extended_after} | {k['n_extended']} |

### arXiv coverage after run 2

- Papers with an arXiv ID: {k['n_with_arxiv_id']}
- Papers that are arXiv-hosted only (every source is arxiv or
  arxiv_via_openalex, no openalex or openalex_snowball record):
  {k['n_arxiv_hosted_only']}

### Run 1 arXiv-only papers that gained OpenAlex data

Run 1 had {n_old_arxiv_only} papers known only by arXiv ID (paper_id
"arxiv:...", no OpenAlex ID). Of those, this run:

- Gained an OpenAlex ID (merged with an arxiv_via_openalex record): {len(gained)}
- Of those, also gained at least one author institution: {gained_institutions_count}

| old paper_id | arxiv_id | new paper_id | title | gained an institution |
|---|---|---|---|---|
{gained_lines}

### Fuzzy title merges involving a new record

{len(fuzzy_new_rows)} of the {len(fuzzy_rows)} fuzzy_title merges listed
above involve at least one arxiv_via_openalex record.

| record_key | title A (year, doi) | paper_id | title B (year, doi) | token_set_ratio | token_sort_ratio |
|---|---|---|---|---|---|
{fuzzy_new_lines}

### Tags table cleanup

{tags_orphan_note}

| old paper_id (no longer in papers) | became |
|---|---|
{orphan_lines}
"""
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
