"""Export batch files for the tagger. See PLAN.md stages 1b and 3, .claude/agents/tagger.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.tag_export --mode relevance
    .venv/bin/python -m pipeline.tag_export --mode full
    .venv/bin/python -m pipeline.tag_export --mode full --only data/work/retag_ids.txt

relevance mode reads every data/raw/*.jsonl, skips record_keys already scored in
data/raw/relevance.csv, and writes 25-record batches to
data/work/relevance_batch_NNN.json, numbered after the highest existing batch.

full mode reads extended_set papers from data/db/papers.sqlite and writes
20-record batches (full abstract) to data/work/tag_batch_NNN.json. --only
takes a file of paper_ids (one per line) and numbers those batches from 901
upward instead, so a partial retag never touches the normal range.

Safe to run twice: it only ever adds new batch files, never overwrites one.
"""
import argparse
import csv
import json
import re
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = REPO_ROOT / "data" / "raw"
WORK_DIR = REPO_ROOT / "data" / "work"
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
RELEVANCE_CSV = RAW_DIR / "relevance.csv"

RELEVANCE_BATCH_SIZE = 25
FULL_BATCH_SIZE = 20
ONLY_BATCH_START = 901


def first_words(text, n=120):
    if not text:
        return ""
    return " ".join(text.split()[:n])


def next_batch_num(prefix, low, high=999):
    """Highest NNN in data/work/<prefix>_batch_NNN.json within [low, high], plus one.
    Excludes *.out.json (the digits must sit right before ".json")."""
    pattern = re.compile(rf"^{re.escape(prefix)}_batch_(\d{{3}})\.json$")
    highest = low - 1
    for p in WORK_DIR.glob(f"{prefix}_batch_*.json"):
        m = pattern.match(p.name)
        if m:
            n = int(m.group(1))
            if low <= n <= high:
                highest = max(highest, n)
    return highest + 1


def write_batches(records, prefix, start_num, size):
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    written = []
    batch_num = start_num
    for i in range(0, len(records), size):
        chunk = records[i : i + size]
        path = WORK_DIR / f"{prefix}_batch_{batch_num:03d}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(chunk, f, indent=2, ensure_ascii=False)
        written.append(path)
        batch_num += 1
    return written


def existing_relevance_keys():
    if not RELEVANCE_CSV.exists():
        return set()
    with open(RELEVANCE_CSV, newline="", encoding="utf-8") as f:
        return {row["record_key"] for row in csv.DictReader(f)}


def export_relevance():
    done = existing_relevance_keys()
    seen = set()
    records = []
    for path in sorted(RAW_DIR.glob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                key = rec.get("record_key")
                if not key or key in seen or key in done:
                    continue
                seen.add(key)
                records.append(
                    {
                        "record_key": key,
                        "source": rec.get("source"),
                        "title": rec.get("title"),
                        "year": rec.get("year"),
                        "venue": rec.get("venue"),
                        "abstract": first_words(rec.get("abstract")),
                    }
                )
    start = next_batch_num("relevance", low=1, high=999)
    written = write_batches(records, "relevance", start, RELEVANCE_BATCH_SIZE)
    return written, len(records)


def extended_set_papers(only_ids=None):
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        if only_ids:
            placeholders = ",".join("?" * len(only_ids))
            rows = con.execute(
                f"SELECT paper_id, title, year, venue, abstract FROM papers "
                f"WHERE extended_set = 1 AND paper_id IN ({placeholders})",
                only_ids,
            ).fetchall()
        else:
            rows = con.execute(
                "SELECT paper_id, title, year, venue, abstract FROM papers WHERE extended_set = 1"
            ).fetchall()
        return [dict(r) for r in rows]
    finally:
        con.close()


def export_full(only_file=None):
    only_ids = None
    if only_file:
        only_ids = [
            line.strip()
            for line in Path(only_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    records = extended_set_papers(only_ids)
    if only_ids:
        start = next_batch_num("tag", low=ONLY_BATCH_START, high=999)
    else:
        start = next_batch_num("tag", low=1, high=ONLY_BATCH_START - 1)
    written = write_batches(records, "tag", start, FULL_BATCH_SIZE)
    return written, len(records)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["relevance", "full"], required=True)
    ap.add_argument("--only", help="full mode only: file of paper_ids, one per line")
    args = ap.parse_args()
    if args.only and args.mode != "full":
        raise SystemExit("--only is only valid with --mode full")

    if args.mode == "relevance":
        written, n = export_relevance()
    else:
        written, n = export_full(args.only)

    for p in written:
        print(p.relative_to(REPO_ROOT).as_posix())
    print(f"batches={len(written)} records={n}")


if __name__ == "__main__":
    main()
