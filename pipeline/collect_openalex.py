"""Collect OpenAlex paper metadata into JSONL.

Usage (from repo root):
    .venv/bin/python -m pipeline.collect_openalex --mode smoke --out data/raw/smoke_openalex.jsonl
    .venv/bin/python -m pipeline.collect_openalex --mode full --out data/raw/openalex.jsonl
    .venv/bin/python -m pipeline.collect_openalex --mode snowball --out data/raw/openalex_snowball.jsonl

Reads pipeline/queries.yaml and .env. Writes the raw record shape from the
openalex-arxiv-playbook skill, one JSON object per line. Safe to run twice:
existing record_keys in --out are loaded first and never duplicated.
"""
import argparse
import csv
import glob
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pyalex import Works, config
from rapidfuzz import fuzz

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_PATH = REPO_ROOT / "pipeline" / "queries.yaml"
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls.md"
RELEVANCE_PATH = REPO_ROOT / "data" / "raw" / "relevance.csv"
OPENALEX_RAW_PATH = REPO_ROOT / "data" / "raw" / "openalex.jsonl"

SLEEP_SECONDS = 0.2  # playbook: stay well under the 100 req/s limit
SNOWBALL_CAP = 150  # PLAN.md stage 1c: cap total new records


def redact(text, secret):
    """Never let the API key reach a log line or reply (see CLAUDE.md)."""
    text = str(text)
    return text.replace(secret, "<KEY>") if secret else text


def log_pitfall(stage, message):
    with open(PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {stage} collector openalex: {message}\n")


def load_queries():
    with open(QUERIES_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_existing_keys(out_path):
    keys = set()
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    keys.add(json.loads(line)["record_key"])
    return keys


def load_all_raw_keys():
    """Stage 1c rule: a new record is one not already in ANY data/raw/*.jsonl file."""
    keys = set()
    for path in glob.glob(str(REPO_ROOT / "data" / "raw" / "*.jsonl")):
        keys |= load_existing_keys(path)
    return keys


def append_records(out_path, records):
    if not records:
        return
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "a", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def strip_id(openalex_url_or_id):
    """https://openalex.org/W123 -> W123. Bare IDs pass through unchanged."""
    if not openalex_url_or_id:
        return None
    return openalex_url_or_id.rsplit("/", 1)[-1]


def clean_doi(doi):
    if not doi:
        return None
    return doi.replace("https://doi.org/", "").replace("http://doi.org/", "").lower()


def extract_arxiv_id(work):
    doi = work.get("doi") or ""
    m = re.search(r"10\.48550/arxiv\.(\S+)", doi, re.IGNORECASE)
    if m:
        return re.sub(r"v\d+$", "", m.group(1))
    for loc in work.get("locations") or []:
        landing = (loc or {}).get("landing_page_url") or ""
        m = re.search(r"arxiv\.org/abs/([^v/?]+)", landing)
        if m:
            return m.group(1)
    return None


def normalize_title(s):
    s = (s or "").lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def work_to_record(work, source, query):
    # work["abstract"] (not .get) -- pyalex only rebuilds prose from
    # abstract_inverted_index behind __getitem__, dict.get bypasses it.
    try:
        abstract = work["abstract"]
    except KeyError:
        abstract = None

    authors = []
    for a in work.get("authorships") or []:
        author = a.get("author") or {}
        institutions = [
            {
                "name": inst.get("display_name"),
                "openalex_inst_id": strip_id(inst.get("id")),
                "country": inst.get("country_code"),
            }
            for inst in (a.get("institutions") or [])
        ]
        authors.append(
            {
                "name": author.get("display_name"),
                "openalex_author_id": strip_id(author.get("id")),
                "institutions": institutions,
            }
        )

    primary_location = work.get("primary_location") or {}
    src = primary_location.get("source") or {}
    openalex_id = strip_id(work.get("id"))

    return {
        "record_key": f"openalex:{openalex_id}",
        "source": source,
        "query": query,
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": work.get("title"),
        "abstract": abstract,
        "year": work.get("publication_year"),
        "doi": clean_doi(work.get("doi")),
        "arxiv_id": extract_arxiv_id(work),
        "openalex_id": openalex_id,
        "authors": authors,
        "venue": src.get("display_name"),
        "cited_by_count": work.get("cited_by_count"),
        "referenced_works": [strip_id(w) for w in (work.get("referenced_works") or [])],
        "topics": [t.get("display_name") for t in (work.get("topics") or [])],
        "url": primary_location.get("landing_page_url") or work.get("id"),
        "raw": work,
    }


def fetch_query(query_str, year_from, limit):
    q = Works().search(query_str)
    if year_from:
        q = q.filter(from_publication_date=f"{year_from}-01-01")
    per_page = min(limit, 100) if limit else 100
    records, cost = [], 0.0
    for page in q.paginate(per_page=per_page, n_max=limit):
        cost += (page.meta or {}).get("cost_usd") or 0
        for w in page:
            if len(records) >= limit:
                break
            records.append(work_to_record(w, "openalex", query_str))
        time.sleep(SLEEP_SECONDS)
        if len(records) >= limit:
            break
    return records, cost


def fetch_anchor(anchor_title):
    """Top hit only, accepted only at token_set_ratio >= 95. Never invent an ID."""
    page = Works().search(anchor_title).get(per_page=1)
    cost = (page.meta or {}).get("cost_usd") or 0
    if not page:
        return None, cost
    top = page[0]
    score = fuzz.token_set_ratio(normalize_title(anchor_title), normalize_title(top.get("title")))
    if score >= 95:
        return work_to_record(top, "openalex", anchor_title), cost
    return None, cost


def load_snowball_seeds(top_n=10):
    """Score-3 records from relevance.csv that carry an OpenAlex id, highest
    cited_by_count first. cited_by_count comes from the stage 1a raw pull."""
    cited_by = {}
    if OPENALEX_RAW_PATH.exists():
        with open(OPENALEX_RAW_PATH, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get("openalex_id"):
                    cited_by[rec["openalex_id"]] = rec.get("cited_by_count") or 0

    seeds = []
    with open(RELEVANCE_PATH, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("record_key", "").startswith("openalex:") and row.get("score") == "3":
                oid = row["record_key"].split(":", 1)[1]
                seeds.append((oid, cited_by.get(oid, 0)))
    seeds.sort(key=lambda x: x[1], reverse=True)
    return [oid for oid, _ in seeds[:top_n]]


def load_seed_counts(out_path, seeds):
    """How many snowball records each seed already has on disk, so a rerun
    tops seeds up to their quota instead of re-filling it from scratch."""
    counts = {sid: 0 for sid in seeds}
    if os.path.exists(out_path):
        with open(out_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                q = json.loads(line).get("query") or ""
                if q.startswith("snowball:"):
                    sid = q.split(":", 1)[1]
                    if sid in counts:
                        counts[sid] += 1
    return counts


def fetch_snowball(existing_keys, out_path, cap=SNOWBALL_CAP, top_n=10):
    if not RELEVANCE_PATH.exists():
        raise SystemExit(f"snowball mode needs {RELEVANCE_PATH}; run stage 1b first")

    seeds = load_snowball_seeds(top_n)
    if not seeds:
        return [], 0.0, {}

    # Share the cap evenly across seeds so one high-citation seed can't
    # starve the rest; remainder (cap % n) goes to the first seeds in
    # priority order (highest cited_by_count first).
    base, rem = divmod(cap, len(seeds))
    seed_cap = {sid: base + (1 if i < rem else 0) for i, sid in enumerate(seeds)}

    records, cost = [], 0.0
    # Start from what's already on disk for each seed (not 0), so a rerun that
    # finds a seed's quota already met does no new fetching for it -- the cap
    # is total-ever, not per-invocation.
    seed_count = load_seed_counts(out_path, seeds)

    def take(work, seed_id):
        if seed_count[seed_id] >= seed_cap[seed_id]:
            return
        rec = work_to_record(work, "openalex_snowball", f"snowball:{seed_id}")
        if rec["record_key"] not in existing_keys:
            existing_keys.add(rec["record_key"])
            records.append(rec)
            seed_count[seed_id] += 1

    for seed_id in seeds:
        remaining = seed_cap[seed_id] - seed_count[seed_id]
        if remaining <= 0:
            continue
        try:
            seed = Works()[seed_id]
        except Exception as exc:
            log_pitfall("stage 1c", f"snowball seed fetch failed for {seed_id}: {redact(exc, config.api_key)}")
            continue

        ref_ids = [strip_id(r) for r in (seed.get("referenced_works") or [])]
        for i in range(0, len(ref_ids), 100):
            if seed_count[seed_id] >= seed_cap[seed_id]:
                break
            batch = ref_ids[i : i + 100]
            try:
                page = Works().filter_or(openalex_id=batch).get(per_page=len(batch))
                cost += (page.meta or {}).get("cost_usd") or 0
                works = list(page)
            except Exception as exc:
                log_pitfall("stage 1c", f"referenced-works batch failed, falling back to singletons: {redact(exc, config.api_key)}")
                works = []
                for rid in batch:
                    try:
                        works.append(Works()[rid])
                    except Exception:
                        continue
                    time.sleep(0.15)
            # filter_or does not promise to return results in `batch` order, and an
            # unstable order plus the per-seed cap would pick a different subset on
            # every run. Reorder to the paper's own referenced_works order (fixed,
            # deterministic) before applying the cap, so reruns are idempotent.
            batch_rank = {rid: idx for idx, rid in enumerate(batch)}
            works.sort(key=lambda w: batch_rank.get(strip_id(w.get("id")), len(batch)))
            for w in works:
                take(w, seed_id)
            time.sleep(SLEEP_SECONDS)

        try:
            remaining = seed_cap[seed_id] - seed_count[seed_id]
            if remaining > 0:
                # Explicit sort: an unsorted filter-only query has no promised order,
                # so without this the top-`remaining` page (and thus which works get
                # taken under the cap) can differ between runs. Sorting makes reruns
                # idempotent and, as a side effect, prefers the more-cited citations.
                q = Works().filter(cites=seed_id).sort(cited_by_count="desc", publication_date="desc")
                for page in q.paginate(per_page=100, n_max=remaining):
                    cost += (page.meta or {}).get("cost_usd") or 0
                    for w in page:
                        take(w, seed_id)
                    time.sleep(SLEEP_SECONDS)
                    if seed_count[seed_id] >= seed_cap[seed_id]:
                        break
        except Exception as exc:
            log_pitfall("stage 1c", f"citing-works fetch failed for {seed_id}: {redact(exc, config.api_key)}")

    return records, cost, seed_cap


def self_check(out_path, n=3):
    """collector.md step 3: eyeball the first few records before reporting."""
    problems = []
    with open(out_path, encoding="utf-8") as f:
        recs = [json.loads(line) for line in f if line.strip()]
    for rec in recs[:n]:
        key = rec.get("record_key")
        abstract = rec.get("abstract")
        if abstract is not None and not isinstance(abstract, str):
            problems.append(f"{key}: abstract is not prose or null")
        doi = rec.get("doi")
        if doi and doi.startswith("http"):
            problems.append(f"{key}: doi keeps the https prefix")
        arxiv_id = rec.get("arxiv_id")
        if arxiv_id and re.search(r"v\d+$", arxiv_id):
            problems.append(f"{key}: arxiv_id keeps a version suffix")
        if "raw" not in rec:
            problems.append(f"{key}: raw field missing")
    return problems


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=["smoke", "full", "snowball"])
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    load_dotenv(str(REPO_ROOT / ".env"))
    api_key = os.environ.get("OPENALEX_API_KEY")
    if not api_key or api_key == "paste_your_key_here":
        raise SystemExit("OPENALEX_API_KEY missing or placeholder in .env")
    config.api_key = api_key
    config.email = os.environ.get("OPENALEX_MAILTO") or None
    config.max_retries = 3
    config.retry_backoff_factor = 0.5

    out_path = args.out if os.path.isabs(args.out) else str(REPO_ROOT / args.out)
    queries = load_queries()
    # Stage 1c: a new snowball record is one not already in ANY data/raw/*.jsonl
    # file, not just this run's own output file.
    existing_keys = load_all_raw_keys() if args.mode == "snowball" else load_existing_keys(out_path)

    total_cost = 0.0
    counts = []  # list of "label: n" for the summary
    problems = []

    if args.mode == "smoke":
        q = queries["openalex"][0]
        try:
            fetched, cost = fetch_query(q, queries.get("year_from"), limit=5)
        except Exception as exc:
            log_pitfall("stage 0", f"smoke query failed: {redact(exc, api_key)}")
            raise
        total_cost += cost
        new = [r for r in fetched if r["record_key"] not in existing_keys]
        append_records(out_path, new)
        counts.append(f"{q!r}: {len(new)}")
        if not new:
            log_pitfall("stage 0", f"query {q!r} returned zero new records")

    elif args.mode == "full":
        per_query_cap = queries.get("per_query_cap", 50)
        year_from = queries.get("year_from")
        for q in queries["openalex"]:
            try:
                fetched, cost = fetch_query(q, year_from, limit=per_query_cap)
            except Exception as exc:
                log_pitfall("stage 1a", f"query {q!r} failed: {redact(exc, api_key)}")
                counts.append(f"{q!r}: 0 (failed)")
                continue
            total_cost += cost
            new = [r for r in fetched if r["record_key"] not in existing_keys]
            for r in new:
                existing_keys.add(r["record_key"])
            append_records(out_path, new)
            counts.append(f"{q!r}: {len(new)}")
            if not new:
                log_pitfall("stage 1a", f"query {q!r} returned zero new records")

        for anchor in queries.get("anchors", []):
            try:
                rec, cost = fetch_anchor(anchor)
            except Exception as exc:
                log_pitfall("stage 1a", f"anchor {anchor!r} lookup failed: {redact(exc, api_key)}")
                continue
            total_cost += cost
            if rec and rec["record_key"] not in existing_keys:
                existing_keys.add(rec["record_key"])
                append_records(out_path, [rec])
                counts.append(f"anchor {anchor!r}: matched")
            else:
                counts.append(f"anchor {anchor!r}: no match")
                log_pitfall("stage 1a", f"anchor title did not resolve at >=95 match: {anchor!r}")

    elif args.mode == "snowball":
        sb_cfg = queries.get("snowball", {})
        cap = sb_cfg.get("max_new_records", SNOWBALL_CAP)
        top_n = sb_cfg.get("top_n", 10)
        fetched, cost, seed_cap = fetch_snowball(existing_keys, out_path, cap=cap, top_n=top_n)
        total_cost += cost
        append_records(out_path, fetched)
        per_seed = {}
        for r in fetched:
            seed_id = r["query"].split(":", 1)[1]
            per_seed[seed_id] = per_seed.get(seed_id, 0) + 1
        counts.append(f"cap {cap} split evenly across {len(seed_cap)} seeds (~{cap // len(seed_cap) if seed_cap else 0}/seed, remainder to highest-cited)")
        counts.append(f"new snowball records: {len(fetched)}")
        counts.append("per seed: " + ("; ".join(f"{sid}: {per_seed.get(sid, 0)}/{seed_cap[sid]}" for sid in seed_cap) if seed_cap else "none"))

    if os.path.exists(out_path):
        problems = self_check(out_path)
        for p in problems:
            log_pitfall(f"stage {'0' if args.mode == 'smoke' else '1'}", f"self-check: {p}")
        with open(out_path, encoding="utf-8") as f:
            total_in_file = sum(1 for line in f if line.strip())
    else:
        total_in_file = 0

    print(f"source: openalex  mode: {args.mode}  out: {out_path}")
    print(f"total records in file: {total_in_file}")
    print("per-query: " + ("; ".join(counts) if counts else "none"))
    print(f"cost_usd this run: {total_cost:.6f}")
    print("problems: " + ("; ".join(problems) if problems else "none"))


if __name__ == "__main__":
    main()
