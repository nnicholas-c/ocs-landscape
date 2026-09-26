"""Import tagger batch outputs. See PLAN.md stages 1b and 3, .claude/agents/tagger.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.tag_import --mode relevance
    .venv/bin/python -m pipeline.tag_import --mode full

relevance mode merges every data/work/relevance_batch_*.out.json into
data/raw/relevance.csv (record_key, source, score, adjacent_field, reason),
one row per record_key. source is read off the record_key prefix
("openalex:..." / "arxiv:...") since the tagger's output does not repeat it.

full mode loads every data/work/tag_batch_*.out.json, in sorted filename
order (a later file wins for a repeated paper_id), into the tags table of
data/db/papers.sqlite. Each evidence_span is checked as a verbatim substring
of the paper's abstract (or equal to the title when the abstract is null);
every row is still loaded, and the failing ones are written to
data/work/tag_failures.json so the tagger can retag just those.

Idempotent: rerunning with the same batch files reproduces the same CSV rows
and the same tags-table rows (INSERT OR REPLACE keyed on paper_id / record_key).
"""
import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
WORK_DIR = REPO_ROOT / "data" / "work"
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
RELEVANCE_CSV = RAW_DIR / "relevance.csv"
FAILURES_PATH = WORK_DIR / "tag_failures.json"

RELEVANCE_FIELDS = ["record_key", "source", "score", "adjacent_field", "reason"]


def load_out_batches(prefix):
    """*.out.json for this prefix, in sorted filename order."""
    for path in sorted(WORK_DIR.glob(f"{prefix}_batch_*.out.json")):
        with open(path, encoding="utf-8") as f:
            for rec in json.load(f):
                yield rec


def import_relevance():
    rows = {}
    if RELEVANCE_CSV.exists():
        with open(RELEVANCE_CSV, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                rows[row["record_key"]] = row

    for rec in load_out_batches("relevance"):
        key = rec["record_key"]
        rows[key] = {
            "record_key": key,
            "source": key.split(":", 1)[0] if ":" in key else "",
            "score": rec.get("score"),
            "adjacent_field": rec.get("adjacent_field") or "",
            "reason": rec.get("reason", ""),
        }

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(RELEVANCE_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=RELEVANCE_FIELDS)
        writer.writeheader()
        for row in rows.values():
            writer.writerow(row)
    return len(rows)


def evidence_ok(evidence_span, abstract, title):
    if not evidence_span:
        return False
    if abstract:
        return evidence_span in abstract
    return evidence_span == title


TAGS_COLUMNS = [
    "paper_id",
    "tech_route",
    "tech_route_secondary",
    "integration",
    "trl_band",
    "ai_dc_fit",
    "adjacent_field",
    "evidence_span",
    "confidence",
]


def import_full():
    merged = {}
    for rec in load_out_batches("tag"):
        merged[rec["paper_id"]] = rec  # later file wins

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        papers = {}
        if merged:
            placeholders = ",".join("?" * len(merged))
            for row in con.execute(
                f"SELECT paper_id, title, abstract FROM papers WHERE paper_id IN ({placeholders})",
                list(merged),
            ):
                papers[row["paper_id"]] = dict(row)

        failures = []
        now = datetime.now(timezone.utc).isoformat()
        for paper_id, rec in merged.items():
            paper = papers.get(paper_id)
            if paper is None:
                failures.append({"paper_id": paper_id, "reason": "paper_id not found in papers table"})
                continue
            ok = evidence_ok(rec.get("evidence_span"), paper.get("abstract"), paper.get("title"))
            if not ok:
                failures.append(
                    {
                        "paper_id": paper_id,
                        "reason": "evidence_span not a verbatim substring of abstract/title",
                        "evidence_span": rec.get("evidence_span"),
                    }
                )
            values = [rec.get(c) for c in TAGS_COLUMNS] + [now]
            con.execute(
                f"INSERT OR REPLACE INTO tags ({', '.join(TAGS_COLUMNS)}, tagged_at) "
                f"VALUES ({', '.join('?' * len(TAGS_COLUMNS))}, ?)",
                values,
            )
        con.commit()
    finally:
        con.close()

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    with open(FAILURES_PATH, "w", encoding="utf-8") as f:
        json.dump(failures, f, indent=2, ensure_ascii=False)

    return len(merged), len(failures)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["relevance", "full"], required=True)
    args = ap.parse_args()

    if args.mode == "relevance":
        n = import_relevance()
        print(f"relevance.csv rows={n} path={RELEVANCE_CSV.relative_to(REPO_ROOT).as_posix()}")
    else:
        n, n_fail = import_full()
        print(f"tags loaded={n} failures={n_fail} failures_path={FAILURES_PATH.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
