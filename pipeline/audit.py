"""Stage 7 audit. See PLAN.md stage 7, .claude/agents/auditor.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.audit > data/work/audit_round1.json

Read-only. Never writes to the database, the matrix, the tags table, or
projects.csv. Runs the four PLAN.md stage 7 checks against a fixed random
seed (SEED below, also recorded in deliverables/validation_report.md so the
sample is reproducible) and prints one JSON object to stdout with, for each
check, the sample, the per-item result, and the pass/fail/rate against
Gate C:
    (a) 20 random core papers re-fetched from their source (OpenAlex or
        arXiv) and compared on title, year, cited_by_count, and the first
        author's first institution.
    (b) 20 random comparison_matrix.csv rows with status=reported: every
        cited paper_id must exist in the database, the evidence_quote must
        be a verbatim substring of a cited paper's abstract, and the value
        must appear in the quote.
    (c) 10 random projects.csv rows: fetch evidence_url with a plain HTTP
        GET and check the entity name and evidence_quote are both present
        in the page text after whitespace normalization. A network failure
        is recorded as unreachable, not a fail.
    (d) Every tags row, evidence_span verbatim in the paper's abstract (or
        equal to the title when abstract is null) -- same check tag_import.py
        uses at load time.
"""
import csv
import html
import json
import os
import random
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv
from pyalex import Works, config

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
MATRIX_PATH = REPO_ROOT / "deliverables" / "comparison_matrix.csv"
PROJECTS_PATH = REPO_ROOT / "data" / "projects.csv"
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls.md"

SEED = 20260926  # fixed seed for every random.Random() sample in this script
SLEEP_SECONDS = 0.2  # playbook: stay well under OpenAlex's 100 req/s limit
HTTP_TIMEOUT = 15
USER_AGENT = "ocs-landscape-audit/1.0"
HTML_TAG_RE = re.compile(r"<[^>]+>")


def redact(text, secret):
    """Never let the API key reach a log line or reply (see CLAUDE.md)."""
    text = str(text)
    return text.replace(secret, "<KEY>") if secret else text


def log_pitfall(stage, message):
    with open(PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{datetime.now().strftime('%Y-%m-%d %H:%M')}] {stage} auditor: {message}\n")


def normalize_title(s):
    s = (s or "").lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def normalize_ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


VALUE_STOPWORDS = {
    "the", "and", "with", "for", "from", "that", "this", "are", "was",
    "were", "has", "have", "not", "but", "its", "into", "over", "per",
    "via", "than", "when", "who", "does", "use", "used", "yes", "vendor",
}


def value_tokens(value):
    """Content words (>=3 chars, not a stopword) plus bare numbers, lowercased.
    Splits on underscores too, so an enum code like integrated_photonic
    yields ["integrated", "photonic"] instead of the literal enum string,
    which never appears verbatim in prose."""
    words = re.findall(r"[a-z]{3,}|\d+(?:\.\d+)?", (value or "").lower().replace("_", " "))
    return [w for w in words if w not in VALUE_STOPWORDS]


def value_in_quote(value, quote):
    """A cell's value is 'in' its quote if at least one content word or
    number from the value appears in the quote. Values are often composite
    (a range from two papers, a code word, a judgment call like trl_band or
    ai_cluster_fit) so requiring the whole value string verbatim would fail
    almost every cell regardless of whether it is actually grounded; this
    checks that the value isn't disconnected from the quote entirely."""
    quote = (quote or "").lower()
    toks = value_tokens(value)
    if not toks:
        return True  # nothing to check against
    return any(t in quote for t in toks)


def page_text(raw_html):
    return html.unescape(HTML_TAG_RE.sub(" ", raw_html))


def evidence_ok(evidence_span, abstract, title):
    """Same rule tag_import.py uses at load time (stage 1b/3)."""
    if not evidence_span:
        return False
    if abstract:
        return evidence_span in abstract
    return evidence_span == title


def open_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


# ---------- (a) re-fetch 20 random core papers ----------

def first_author_institution(con, paper_id):
    row = con.execute(
        """SELECT i.display_name FROM paper_authors pa
           JOIN institutions i ON i.inst_id = pa.inst_id
           WHERE pa.paper_id = ? AND pa.position = 0""",
        (paper_id,),
    ).fetchone()
    return row["display_name"] if row else None


def refetch_openalex(openalex_id):
    w = Works()[openalex_id]
    try:
        title = w["title"]  # pyalex only rebuilds title normally via __getitem__ too; keep consistent style
    except KeyError:
        title = None
    inst = None
    for a in w.get("authorships") or []:
        insts = a.get("institutions") or []
        inst = insts[0].get("display_name") if insts else None
        break
    return title, w.get("publication_year"), w.get("cited_by_count"), inst


def refetch_arxiv(arxiv_id):
    import arxiv
    client = arxiv.Client(page_size=1, delay_seconds=3.0, num_retries=3)
    results = list(client.results(arxiv.Search(id_list=[arxiv_id])))
    if not results:
        raise ValueError("arxiv id_list lookup returned no result")
    r = results[0]
    return r.title, (r.published.year if r.published else None), None, None


def check_a(con, api_key, sample_size=20):
    papers = [dict(r) for r in con.execute(
        "SELECT paper_id, openalex_id, arxiv_id, title, year, cited_by_count "
        "FROM papers WHERE core_set = 1"
    )]
    sample = random.Random(SEED).sample(papers, min(sample_size, len(papers)))

    items = []
    for p in sample:
        stored_inst = first_author_institution(con, p["paper_id"])
        item = {
            "paper_id": p["paper_id"],
            "stored": {"title": p["title"], "year": p["year"],
                       "cited_by_count": p["cited_by_count"], "first_institution": stored_inst},
        }
        try:
            if p["openalex_id"]:
                new_title, new_year, new_cited, new_inst = refetch_openalex(p["openalex_id"])
                time.sleep(SLEEP_SECONDS)
            elif p["arxiv_id"]:
                new_title, new_year, new_cited, new_inst = refetch_arxiv(p["arxiv_id"])
            else:
                item["result"] = "error"
                item["error"] = "no openalex_id or arxiv_id on this paper"
                items.append(item)
                continue
        except Exception as exc:
            item["result"] = "error"
            item["error"] = redact(str(exc), api_key)
            items.append(item)
            continue

        title_match = normalize_title(new_title) == normalize_title(p["title"])
        year_match = None if new_year is None or p["year"] is None else new_year == p["year"]
        if new_cited is None or p["cited_by_count"] is None:
            cited_match = None
        else:
            cited_match = abs(new_cited - p["cited_by_count"]) / max(p["cited_by_count"], 1) <= 0.10
        if new_inst is None or stored_inst is None:
            inst_match = None  # source has no institution for the first author, not counted
        else:
            inst_match = normalize_ws(new_inst).lower() == normalize_ws(stored_inst).lower()

        subchecks = {"title": title_match, "year": year_match,
                     "cited_by_count": cited_match, "first_institution": inst_match}
        mismatched = [k for k, v in subchecks.items() if v is False]
        item["refetched"] = {"title": new_title, "year": new_year,
                              "cited_by_count": new_cited, "first_institution": new_inst}
        item["subchecks"] = subchecks
        item["result"] = "fail" if mismatched else "pass"
        item["mismatched_fields"] = mismatched
        items.append(item)

    n_pass = sum(1 for it in items if it["result"] == "pass")
    n_fail = sum(1 for it in items if it["result"] == "fail")
    n_error = sum(1 for it in items if it["result"] == "error")
    denom = n_pass + n_fail
    rate_fail = (n_fail / denom) if denom else None
    return {
        "sample_size": len(sample), "sampled_ids": [p["paper_id"] for p in sample],
        "items": items, "pass": n_pass, "fail": n_fail, "error": n_error,
        "rate_fail": rate_fail, "gate_threshold": 0.10,
        "gate_pass": (rate_fail is not None and rate_fail <= 0.10),
    }


# ---------- (b) 20 random matrix cells with status=reported ----------

def check_b(con, sample_size=20):
    with open(MATRIX_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        projects = {i: r for i, r in enumerate(csv.DictReader(f), start=1)}  # project_rows is 1-indexed

    reported = [r for r in rows if r.get("status") == "reported"]
    sample = random.Random(SEED).sample(reported, min(sample_size, len(reported)))

    items = []
    for row in sample:
        cell_id = f"{row['tech_route']}:{row['dimension']}"
        paper_ids = [pid.strip() for pid in (row.get("paper_ids") or "").split(";") if pid.strip()]
        proj_rows = [int(n) for n in (row.get("project_rows") or "").split(";") if n.strip()]
        quote = row.get("evidence_quote") or ""

        missing_ids, evidence_texts = [], []
        for pid in paper_ids:
            r = con.execute("SELECT abstract FROM papers WHERE paper_id = ?", (pid,)).fetchone()
            if r is None:
                missing_ids.append(pid)
            else:
                evidence_texts.append(r["abstract"] or "")
        missing_rows = [n for n in proj_rows if n not in projects]
        for n in proj_rows:
            if n in projects:
                evidence_texts.append(projects[n].get("evidence_quote") or "")

        # skill: evidence_quote must be a verbatim substring of that paper's
        # abstract OR of the project row's evidence_quote.
        quote_supported = bool(quote) and any(quote in t for t in evidence_texts)

        reasons = []
        if missing_ids:
            reasons.append(f"paper_id(s) not in database: {','.join(missing_ids)}")
        if missing_rows:
            reasons.append(f"project_rows(s) not in projects.csv: {','.join(map(str, missing_rows))}")
        if not quote_supported:
            reasons.append("evidence_quote not a verbatim substring of any cited paper's abstract or project row's evidence_quote")
        if not value_in_quote(row.get("value"), quote):
            reasons.append("value shares no content word or number with evidence_quote")

        items.append({"cell": cell_id, "paper_ids": paper_ids, "project_rows": proj_rows,
                      "result": "fail" if reasons else "pass", "reasons": reasons})

    n_pass = sum(1 for it in items if it["result"] == "pass")
    n_fail = len(items) - n_pass
    rate_fail = (n_fail / len(items)) if items else None
    return {
        "sample_size": len(sample), "sampled_ids": [it["cell"] for it in items],
        "items": items, "pass": n_pass, "fail": n_fail,
        "rate_fail": rate_fail, "gate_threshold": 0.10,
        "gate_pass": (rate_fail is not None and rate_fail <= 0.10),
    }


# ---------- (c) 10 random projects.csv rows ----------

def check_c(sample_size=10):
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    sample = random.Random(SEED).sample(rows, min(sample_size, len(rows)))

    items = []
    for row in sample:
        entity = row.get("entity") or ""
        url = row.get("evidence_url") or ""
        quote = row.get("evidence_quote") or ""
        row_id = f"{entity} ({url})"
        try:
            resp = requests.get(url, timeout=HTTP_TIMEOUT, headers={"User-Agent": USER_AGENT})
            resp.raise_for_status()
        except requests.RequestException as exc:
            items.append({"row": row_id, "result": "unreachable", "detail": str(exc)[:200]})
            continue

        # requests falls back to ISO-8859-1 when a server sends no charset,
        # which mangles UTF-8 punctuation (curly apostrophes etc.) into
        # mojibake and breaks verbatim substring checks; sniff the real
        # encoding from the content instead.
        resp.encoding = resp.apparent_encoding
        text = normalize_ws(page_text(resp.text)).lower()
        reasons = []
        if normalize_ws(entity).lower() not in text:
            reasons.append("entity name absent from page text")
        if normalize_ws(quote).lower() not in text:
            reasons.append("evidence_quote absent from page text after whitespace normalization")
        items.append({"row": row_id, "result": "fail" if reasons else "pass", "reasons": reasons})

    n_pass = sum(1 for it in items if it["result"] == "pass")
    n_fail = sum(1 for it in items if it["result"] == "fail")
    n_unreachable = sum(1 for it in items if it["result"] == "unreachable")
    denom = n_pass + n_fail
    rate_fail = (n_fail / denom) if denom else None
    return {
        "sample_size": len(sample), "sampled_ids": [it["row"] for it in items],
        "items": items, "pass": n_pass, "fail": n_fail, "unreachable": n_unreachable,
        "rate_fail": rate_fail, "gate_threshold": 0.20,
        "gate_pass": (rate_fail is not None and rate_fail <= 0.20),
    }


# ---------- (d) every tags row ----------

def check_d(con):
    rows = con.execute(
        "SELECT t.paper_id, t.evidence_span, p.abstract, p.title "
        "FROM tags t JOIN papers p ON p.paper_id = t.paper_id"
    ).fetchall()
    fails = []
    n_pass = 0
    for r in rows:
        if evidence_ok(r["evidence_span"], r["abstract"], r["title"]):
            n_pass += 1
        else:
            fails.append({"paper_id": r["paper_id"], "evidence_span": r["evidence_span"]})
    n_fail = len(fails)
    rate_pass = (n_pass / len(rows)) if rows else None
    return {
        "sample_size": len(rows), "sampled_ids": "all tags rows (exhaustive, not sampled)",
        "items": fails, "pass": n_pass, "fail": n_fail,
        "rate_pass": rate_pass, "gate_threshold": 0.90,
        "gate_pass": (rate_pass is not None and rate_pass >= 0.90),
    }


def main():
    load_dotenv(str(REPO_ROOT / ".env"))
    api_key = os.environ.get("OPENALEX_API_KEY")
    if not api_key or api_key == "paste_your_key_here":
        raise SystemExit("OPENALEX_API_KEY missing or placeholder in .env")
    config.api_key = api_key
    config.max_retries = 3
    config.retry_backoff_factor = 0.5

    con = open_db()
    try:
        result = {
            "seed": SEED,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "a_refetch": check_a(con, api_key),
            "b_matrix_cells": check_b(con),
            "c_project_evidence": check_c(),
            "d_evidence_spans": check_d(con),
        }
    except Exception as exc:
        log_pitfall("stage 7", f"audit.py run failed: {redact(exc, api_key)}")
        raise
    finally:
        con.close()

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
