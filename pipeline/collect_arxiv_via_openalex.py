"""Collect arXiv-hosted papers through OpenAlex's index of arXiv (source
S4306400194, confirmed by singleton lookup -- see data/work/run2_pitfalls.log).

Runs the arxiv.phrases from pipeline/queries.yaml as OpenAlex full-text
searches filtered to that one source, so every hit is a paper OpenAlex has
indexed from arXiv (not a random OpenAlex work). Reuses the raw record shape
and helpers from pipeline.collect_openalex rather than reimplementing them.

Usage (from repo root):
    .venv/bin/python -m pipeline.collect_arxiv_via_openalex --out data/raw/arxiv_via_openalex.jsonl

Safe to run twice: a record is skipped if its record_key is already present
in ANY data/raw/*.jsonl file (not just this script's own output).
"""
import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from pyalex import Works, config

from pipeline.collect_openalex import (
    append_records,
    load_all_raw_keys,
    load_queries,
    redact,
    self_check,
    work_to_record,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
# Run 2: logging is redirected while another process finishes STATUS.md and
# the deliverables. Append here instead of deliverables/pitfalls.md.
RUN2_PITFALLS_PATH = REPO_ROOT / "data" / "work" / "run2_pitfalls.log"

ARXIV_SOURCE_ID = "S4306400194"  # arXiv (Cornell University), confirmed in step 2
SLEEP_SECONDS = 0.2


def log_pitfall(stage, message):
    RUN2_PITFALLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(RUN2_PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {stage} collector arxiv_via_openalex: {message}\n")


def fetch_query(query_str, year_from, limit, source_id):
    q = Works().search(query_str).filter(
        locations={"source": {"id": source_id}},
        from_publication_date=f"{year_from}-01-01",
    )
    per_page = min(limit, 100) if limit else 100
    records, cost = [], 0.0
    for page in q.paginate(per_page=per_page, n_max=limit):
        cost += (page.meta or {}).get("cost_usd") or 0
        for w in page:
            if len(records) >= limit:
                break
            records.append(work_to_record(w, "arxiv_via_openalex", query_str))
        time.sleep(SLEEP_SECONDS)
        if len(records) >= limit:
            break
    return records, cost


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=str(REPO_ROOT / "data" / "raw" / "arxiv_via_openalex.jsonl"))
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
    year_from = queries.get("year_from")
    per_query_cap = queries.get("per_query_cap", 50)
    phrases = queries["arxiv"]["phrases"]

    # Stage 1a rule (reused here): a new record is one not already in ANY
    # data/raw/*.jsonl file, not just this script's own output file. This
    # also makes overlap with the OpenAlex phrase pull / snowball / arXiv
    # pull itself a counted finding, per the task.
    existing_keys = load_all_raw_keys()

    total_cost = 0.0
    per_query_new = []
    per_query_skipped = []
    total_new = 0
    total_skipped = 0

    for phrase in phrases:
        try:
            fetched, cost = fetch_query(phrase, year_from, per_query_cap, ARXIV_SOURCE_ID)
        except Exception as exc:
            log_pitfall("stage 1a", f"query {phrase!r} failed: {redact(exc, api_key)}")
            per_query_new.append(f"{phrase!r}: 0 (failed)")
            continue
        total_cost += cost
        new = [r for r in fetched if r["record_key"] not in existing_keys]
        skipped = len(fetched) - len(new)
        for r in new:
            existing_keys.add(r["record_key"])
        append_records(out_path, new)
        total_new += len(new)
        total_skipped += skipped
        per_query_new.append(f"{phrase!r}: {len(new)}")
        per_query_skipped.append(f"{phrase!r}: {skipped}")
        if not fetched:
            log_pitfall("stage 1a", f"query {phrase!r} returned zero records from OpenAlex's arXiv index")

    problems = []
    if os.path.exists(out_path):
        problems = self_check(out_path)
        for p in problems:
            log_pitfall("stage 1a", f"self-check: {p}")
        with open(out_path, encoding="utf-8") as f:
            recs = [json.loads(line) for line in f if line.strip()]
        total_in_file = len(recs)
        new_with_arxiv_id = sum(1 for r in recs if r.get("arxiv_id"))
    else:
        total_in_file = 0
        new_with_arxiv_id = 0

    print(f"source: arxiv_via_openalex  out: {out_path}")
    print(f"total records in file: {total_in_file}  (records with arxiv_id: {new_with_arxiv_id})")
    print(f"new this run: {total_new}  skipped-as-already-present this run: {total_skipped}")
    print("per-query new: " + ("; ".join(per_query_new) if per_query_new else "none"))
    print("per-query skipped: " + ("; ".join(per_query_skipped) if per_query_skipped else "none"))
    print(f"cost_usd this run: {total_cost:.6f}")
    print("problems: " + ("; ".join(problems) if problems else "none"))


if __name__ == "__main__":
    main()
