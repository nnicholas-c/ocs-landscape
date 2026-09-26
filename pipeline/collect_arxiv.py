"""Collect paper metadata from arXiv into data/raw as JSONL.

Usage:
    .venv/bin/python -m pipeline.collect_arxiv --mode smoke --out data/raw/smoke_arxiv.jsonl
    .venv/bin/python -m pipeline.collect_arxiv --mode full  --out data/raw/arxiv.jsonl

Safe to run twice: record_keys already in --out are loaded first and skipped.
"""
import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import arxiv
import yaml
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
QUERIES_PATH = REPO_ROOT / "pipeline" / "queries.yaml"
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls.md"

VERSION_SUFFIX = re.compile(r"v\d+$")


def log_pitfall(stage: str, message: str) -> None:
    line = f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {stage} collector(arxiv): {message}\n"
    with open(PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(line)


def load_existing_keys(out_path: Path) -> set:
    keys = set()
    if out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    keys.add(json.loads(line)["record_key"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return keys


def normalize_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    for prefix in ("https://doi.org/", "http://dx.doi.org/", "doi.org/"):
        if d.startswith(prefix):
            d = d[len(prefix):]
    return d


def build_query(phrase: str, categories: list, year_from: int) -> str:
    cats = " OR ".join(f"cat:{c}" for c in categories)
    date_filter = f"submittedDate:[{year_from}01010000 TO 99991231235959]"
    return f'(abs:"{phrase}" OR ti:"{phrase}") AND ({cats}) AND {date_filter}'


def result_to_record(r, query_label: str) -> dict:
    arxiv_id = VERSION_SUFFIX.sub("", r.get_short_id())
    raw = {
        "entry_id": r.entry_id,
        "title": r.title,
        "summary": r.summary,
        "authors": [a.name for a in r.authors],
        "published": r.published.isoformat() if r.published else None,
        "updated": r.updated.isoformat() if r.updated else None,
        "doi": r.doi,
        "primary_category": r.primary_category,
        "categories": r.categories,
        "journal_ref": r.journal_ref,
        "comment": r.comment,
        "pdf_url": r.pdf_url,
    }
    return {
        "record_key": f"arxiv:{arxiv_id}",
        "source": "arxiv",
        "query": query_label,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "title": r.title,
        "abstract": r.summary or None,
        "year": r.published.year if r.published else None,
        "doi": normalize_doi(r.doi),
        "arxiv_id": arxiv_id,
        "openalex_id": None,
        "authors": [
            {"name": a.name, "openalex_author_id": None, "institutions": []}
            for a in r.authors
        ],
        "venue": "arXiv",
        "cited_by_count": None,
        "referenced_works": None,
        "topics": r.categories,
        "url": r.entry_id,
        "raw": raw,
    }


def run_query(client, query_str, max_results, seen_keys, out_f, query_label, stage):
    search = arxiv.Search(
        query=query_str, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )
    count = 0
    for attempt in range(3):
        try:
            for r in client.results(search):
                rec = result_to_record(r, query_label)
                if rec["record_key"] in seen_keys:
                    continue
                seen_keys.add(rec["record_key"])
                out_f.write(json.dumps(rec) + "\n")
                out_f.flush()
                count += 1
            break
        except Exception as e:
            if attempt == 2:
                log_pitfall(stage, f"query '{query_label}' failed after 3 attempts: {e}")
            else:
                time.sleep(2 ** attempt)
    if count == 0:
        log_pitfall(stage, f"query '{query_label}' returned zero new records")
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["smoke", "full"], required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    load_dotenv(REPO_ROOT / ".env")

    with open(QUERIES_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    year_from = cfg["year_from"]
    per_query_cap = cfg["per_query_cap"]
    categories = cfg["arxiv"]["categories"]
    phrases = cfg["arxiv"]["phrases"]

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    seen_keys = load_existing_keys(out_path)

    client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)

    stage = "stage0" if args.mode == "smoke" else "stage1a"
    per_query_counts = []

    with open(out_path, "a", encoding="utf-8") as out_f:
        if args.mode == "smoke":
            phrase = phrases[0]
            query_str = build_query(phrase, categories, year_from)
            n = run_query(client, query_str, 5, seen_keys, out_f, phrase, stage)
            per_query_counts.append((phrase, n))
        else:
            for phrase in phrases:
                query_str = build_query(phrase, categories, year_from)
                n = run_query(client, query_str, per_query_cap, seen_keys, out_f, phrase, stage)
                per_query_counts.append((phrase, n))

    total = len(seen_keys)
    print(f"source=arxiv out={out_path} total_records={total}")
    for phrase, n in per_query_counts:
        print(f"  {phrase!r}: {n}")


if __name__ == "__main__":
    main()
