"""Stage 7 audit, run 2. See PLAN.md stage 7, .claude/agents/auditor.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.audit          > data/work/audit_run2_prejudge.json
    # then the auditor reads data/work/audit_run2_judge_input.json and writes
    # data/work/audit_run2_judgments.json by hand
    .venv/bin/python -m pipeline.audit --merge  > data/work/audit_run2_round1.json

Read-only. Never writes to the database, the matrix, the tags table, or
projects.csv. Runs the four PLAN.md stage 7 checks with SEED below (run 2's
seed; run 1 used 20260926, see deliverables/validation_report.md "Run 1").

(a) 20 random core papers re-fetched from their source and compared on
    title, year, cited_by_count, and the first author's first institution.
(b) Measured-dimension cells (switching_time, insertion_loss, port_count,
    polarization_dependent_loss, crosstalk, wavelength_range, cost_per_port)
    are checked mechanically only: cited IDs exist, every " || "-joined
    quote is a verbatim substring of a cited abstract or project row quote,
    and every number in `value` (or a wavelength band name) is in one of
    the quotes. Category cells (integration, trl_band, ai_cluster_fit) and
    free-text cells (packaging_notes, scaling_limit, academic_groups,
    companies) get the same ID/quote mechanical check; academic_groups and
    companies are then verified by code (recomputed from
    pipeline.matrix_build against graphs/top_pis.csv and data/projects.csv);
    the rest are judged by the auditor via the judge_input/judgments files.
    Gate C samples 20 random cells with status=reported. Every reported
    category cell (27) is also judged as a census, separate from Gate C.
(c) 10 random projects.csv rows: fetch evidence_url with a plain HTTP GET
    and check the entity name and evidence_quote are both present in the
    page text after whitespace normalization. A network failure is
    recorded as unreachable, not a fail.
(d) Every tags row, evidence_span verbatim in the paper's abstract (or
    equal to the title when abstract is null) -- same check tag_import.py
    uses at load time.
"""
import argparse
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
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls_original_log.md"  # overrides CLAUDE.md rule 5 for this rework
WORK_DIR = REPO_ROOT / "data" / "work"
PREJUDGE_PATH = WORK_DIR / "audit_run2_prejudge.json"
JUDGE_INPUT_PATH = WORK_DIR / "audit_run2_judge_input.json"
JUDGMENTS_PATH = WORK_DIR / "audit_run2_judgments.json"
FINAL_PATH = WORK_DIR / "audit_run2_round1.json"

SEED = 20260927  # run 2 seed. Run 1 used SEED = 20260926 (see validation_report.md "Run 1").
SLEEP_SECONDS = 0.2  # playbook: stay well under OpenAlex's 100 req/s limit
HTTP_TIMEOUT = 15
USER_AGENT = "ocs-landscape-audit/1.0"
HTML_TAG_RE = re.compile(r"<[^>]+>")
SEP = " || "  # matches pipeline.matrix_build's join of multiple quotes in one cell

MEASURED_DIMS = {"switching_time", "insertion_loss", "port_count",
                  "polarization_dependent_loss", "crosstalk", "wavelength_range", "cost_per_port"}
CATEGORY_DIMS = {"integration", "trl_band", "ai_cluster_fit"}
CODE_CHECK_DIMS = {"academic_groups", "companies"}
JUDGE_TEXT_DIMS = {"packaging_notes", "scaling_limit"}

# Label definitions handed to the auditor for judgment, condensed from the
# ocs-domain and comparison-framework skills (loaded in full for this task).
LABEL_DEFS = {
    "integration": (
        "free_space_bulk: beams travel through air between mirrors or collimators in a "
        "sealed box, fiber collimator arrays at the ports. integrated_photonic: light stays "
        "in waveguides on a chip. mechanical_fiber: fibers are physically moved or "
        "reconnected. unclear: not stated. (ocs-domain, comparison-framework)"
    ),
    "trl_band": (
        "lab: a prototype, fabricated device, simulation, or testbed (signal words: we "
        "demonstrate, fabricated, prototype, proof of concept, simulation). pilot: a field "
        "trial, single-facility deployment, small production run. production: in service at "
        "scale or sold as a product (in production, deployed across, commercially "
        "available, shipping). unclear: not stated. (ocs-domain)"
    ),
    "ai_cluster_fit": (
        "Does the literature use or propose this route for accelerator clusters, "
        "reconfigurable topologies, or replacing a spine layer? yes/partial/no/not_reported. "
        "(comparison-framework; ocs-domain's ai_dc_fit analog: direct = targets accelerator "
        "clusters, ML training, TPU/GPU pods, collective communication, or spine "
        "replacement; indirect = data center networks generally, or an application that "
        "includes data centers; none = telecom/sensing/other only; unclear = not stated.)"
    ),
    "packaging_notes": (
        "Free text: fiber attach, hermetic sealing, thermal control, whatever the source "
        "states about physically packaging the switch. Supported means the quote actually "
        "states the packaging detail the value claims. (comparison-framework)"
    ),
    "scaling_limit": (
        "Free text: what stops the port count growing, as the source states it (mirror "
        "count, loss accumulation, control complexity, mechanical time). Supported means "
        "the quote actually states the limiting factor the value claims. (comparison-framework)"
    ),
}


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
    title = w.get("title")
    inst = None
    for auth in w.get("authorships") or []:
        insts = auth.get("institutions") or []
        inst = insts[0].get("display_name") if insts else None
        break
    return title, w.get("publication_year"), w.get("cited_by_count"), inst


def refetch_arxiv_api(arxiv_id):
    import arxiv
    client = arxiv.Client(page_size=1, delay_seconds=10.0, num_retries=3)
    results = list(client.results(arxiv.Search(id_list=[arxiv_id])))
    if not results:
        raise ValueError("arxiv id_list lookup returned no result")
    r = results[0]
    return r.title, (r.published.year if r.published else None)


def refetch_arxiv_html(arxiv_id):
    resp = requests.get(f"https://arxiv.org/abs/{arxiv_id}", timeout=HTTP_TIMEOUT,
                         headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    m_title = re.search(r'<meta name="citation_title" content="([^"]*)"', resp.text)
    m_date = re.search(r'<meta name="citation_date" content="([^"]*)"', resp.text)
    if not m_title or not m_date:
        raise ValueError("citation_title or citation_date meta tag not found on abs page")
    title = html.unescape(m_title.group(1))
    year = int(m_date.group(1).split("/")[0])
    return title, year


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
        method = None
        new_title = new_year = new_cited = new_inst = None
        errors = []
        if p["openalex_id"]:
            try:
                new_title, new_year, new_cited, new_inst = refetch_openalex(p["openalex_id"])
                method = "openalex"
                time.sleep(SLEEP_SECONDS)
            except Exception as exc:
                errors.append(f"openalex: {redact(exc, api_key)}")
        elif p["arxiv_id"]:
            try:
                new_title, new_year = refetch_arxiv_api(p["arxiv_id"])
                method = "arxiv_api"
            except Exception as exc1:
                errors.append(f"arxiv_api: {redact(exc1, api_key)}")
                try:
                    new_title, new_year = refetch_arxiv_html(p["arxiv_id"])
                    method = "arxiv_html_fallback"
                except Exception as exc2:
                    errors.append(f"arxiv_html_fallback: {redact(exc2, api_key)}")
        else:
            errors.append("no openalex_id or arxiv_id on this paper")

        if method is None:
            item["result"] = "dropped"
            item["method"] = None
            item["error"] = "; ".join(errors)
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
        item["method"] = method
        item["refetched"] = {"title": new_title, "year": new_year,
                              "cited_by_count": new_cited, "first_institution": new_inst}
        item["subchecks"] = subchecks
        item["result"] = "fail" if mismatched else "pass"
        item["mismatched_fields"] = mismatched
        items.append(item)

    n_pass = sum(1 for it in items if it["result"] == "pass")
    n_fail = sum(1 for it in items if it["result"] == "fail")
    n_dropped = sum(1 for it in items if it["result"] == "dropped")
    denom = n_pass + n_fail
    rate_fail = (n_fail / denom) if denom else None
    return {
        "sample_size": len(sample), "sampled_ids": [p["paper_id"] for p in sample],
        "drawn": len(sample), "compared": denom, "dropped": n_dropped,
        "items": items, "pass": n_pass, "fail": n_fail,
        "rate_fail": rate_fail, "gate_threshold": 0.10,
        "gate_pass": (rate_fail is not None and rate_fail <= 0.10),
    }


# ---------- (b) matrix cells: mechanical checks, code checks, and judged cells ----------

NUM_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
BAND_RE = re.compile(r"[A-Za-z](?:\+[A-Za-z])?\s*band", re.IGNORECASE)


def _strip_sep(s):
    return re.sub(r"[\s-]+", "", s or "").lower()


def _mechanical_check(con, projects, row):
    """ID and verbatim-quote checks shared by every dimension type. Returns
    (ok, reasons, quotes_list)."""
    paper_ids = [pid.strip() for pid in (row.get("paper_ids") or "").split(";") if pid.strip()]
    proj_rows = [int(n) for n in (row.get("project_rows") or "").split(";") if n.strip()]
    quote = row.get("evidence_quote") or ""
    quotes_list = quote.split(SEP) if quote else []

    reasons = []
    evidence_texts = []
    missing_ids = []
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

    if missing_ids:
        reasons.append(f"paper_id(s) not in database: {','.join(missing_ids)}")
    if missing_rows:
        reasons.append(f"project_row(s) not in projects.csv: {','.join(map(str, missing_rows))}")
    if not quotes_list:
        reasons.append("no evidence_quote")
    else:
        bad_quotes = [q for q in quotes_list if not any(q in t for t in evidence_texts)]
        if bad_quotes:
            reasons.append(f"{len(bad_quotes)} of {len(quotes_list)} quote(s) not a verbatim "
                            f"substring of any cited abstract or project row quote")
    return (not reasons, reasons, quotes_list)


def _measured_value_check(value, quotes_list, dimension):
    """Every number in `value` (and, for wavelength_range, every band name)
    must appear in at least one of the cell's quotes."""
    reasons = []
    for num in dict.fromkeys(NUM_RE.findall(value or "")):
        if not any(num in q for q in quotes_list):
            reasons.append(f"number {num!r} in value is in none of the quotes")
    if dimension == "wavelength_range":
        for band in dict.fromkeys(m.group(0) for m in BAND_RE.finditer(value or "")):
            band_norm = _strip_sep(band)
            if not any(band_norm in _strip_sep(q) for q in quotes_list):
                reasons.append(f"band {band!r} in value is in none of the quotes")
    return (not reasons, reasons)


def _academic_groups_companies_check(con, projects, pis, actual_rows):
    """Recompute academic_groups and companies with pipeline.matrix_build's
    own functions (the same code that built the CSV) and diff against the
    CSV. This is the code check the task asks for; no judgment needed."""
    from pipeline.matrix_build import ROUTES, academic_groups as mb_ag, companies as mb_co

    items = []
    for route in ROUTES:
        papers = {p["paper_id"]: p for p in json.loads(
            (WORK_DIR / f"route_{route}.json").read_text(encoding="utf-8"))}
        for dim, fn, args in (("academic_groups", mb_ag, (papers, con, pis)),
                              ("companies", mb_co, (projects,))):
            recomputed = fn(route, *args)
            actual = actual_rows[(route, dim)]
            mismatches = [f for f in ("value", "status", "paper_ids", "project_rows")
                          if recomputed.get(f, "") != actual.get(f, "")]
            items.append({
                "cell": f"{route}:{dim}", "result": "not_supported" if mismatches else "supported",
                "reason": (f"recomputed {mismatches} differs from comparison_matrix.csv"
                           if mismatches else "recomputed value, status and citations match comparison_matrix.csv"),
            })
    n_pass = sum(1 for it in items if it["result"] == "supported")
    return {"items": items, "pass": n_pass, "fail": len(items) - n_pass}


def check_b(con):
    with open(MATRIX_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        projects = {i: r for i, r in enumerate(csv.DictReader(f), start=1)}
    pis_path = REPO_ROOT / "graphs" / "top_pis.csv"
    with open(pis_path, newline="", encoding="utf-8") as f:
        pis = {r["author_id"]: r for r in csv.DictReader(f)}
    actual_rows = {(r["tech_route"], r["dimension"]): r for r in rows}

    ag_co_result = _academic_groups_companies_check(con, projects, pis, actual_rows)
    ag_co_by_cell = {it["cell"]: it for it in ag_co_result["items"]}

    resolved = {}     # cell_id -> {"result": pass/fail, "reasons": [...]}
    to_judge = {}      # cell_id -> row dict, for cells needing the auditor's read
    for row in rows:
        if row["status"] not in ("reported", "derived"):
            continue
        cell_id = f"{row['tech_route']}:{row['dimension']}"
        dim = row["dimension"]
        if dim in CODE_CHECK_DIMS:
            it = ag_co_by_cell[cell_id]
            resolved[cell_id] = {"result": "pass" if it["result"] == "supported" else "fail",
                                  "reasons": [] if it["result"] == "supported" else [it["reason"]]}
            continue
        ok, reasons, quotes_list = _mechanical_check(con, projects, row)
        if dim in MEASURED_DIMS:
            if ok:
                ok, val_reasons = _measured_value_check(row.get("value"), quotes_list, dim)
                reasons += val_reasons
            resolved[cell_id] = {"result": "pass" if ok else "fail", "reasons": reasons}
        else:  # CATEGORY_DIMS or JUDGE_TEXT_DIMS: mechanical pass required before judging
            if not ok:
                resolved[cell_id] = {"result": "fail", "reasons": reasons}
            else:
                to_judge[cell_id] = {"cell": cell_id, "dimension": dim, "value": row.get("value"),
                                      "quotes": quotes_list, "label_definition": LABEL_DEFS.get(dim, "")}

    reported = [r for r in rows if r["status"] == "reported"]
    gate_sample = random.Random(SEED).sample(reported, min(20, len(reported)))
    gate_sample_ids = [f"{r['tech_route']}:{r['dimension']}" for r in gate_sample]
    category_census_ids = [f"{r['tech_route']}:{r['dimension']}" for r in reported
                            if r["dimension"] in CATEGORY_DIMS]
    # Only cells actually needed for the Gate C sample or the category census
    # get judged -- a mechanical-pass category/free-text cell that lands in
    # neither just sits unresolved in `to_judge` and is never reported.
    needed_ids = [cid for cid in dict.fromkeys(gate_sample_ids + category_census_ids) if cid in to_judge]

    JUDGE_INPUT_PATH.write_text(
        json.dumps([to_judge[cid] for cid in needed_ids], indent=2, ensure_ascii=False),
        encoding="utf-8")

    return {
        "seed": SEED,
        "resolved": resolved,                       # cell_id -> result, for every reported/derived cell not needing judgment
        "pending_judgment_cell_ids": sorted(needed_ids),
        "gate_sample_ids": gate_sample_ids,
        "category_census_ids": category_census_ids,
        "academic_groups_companies_check": ag_co_result,
    }


def merge_b(b_stage1, judgments):
    """Fold the auditor's judgments.json into check_b's resolved cells and
    compute the Gate C sample rate and the category census, separately."""
    resolved = dict(b_stage1["resolved"])
    for cid, verdict in judgments.items():
        resolved[cid] = {"result": "pass" if verdict.get("supported") else "fail",
                          "reasons": [verdict.get("reason", "")]}

    missing = [cid for cid in b_stage1["pending_judgment_cell_ids"] if cid not in resolved]
    if missing:
        raise SystemExit(f"missing judgment for {len(missing)} cell(s): {missing}")

    def summarize(ids):
        items = [{"cell": cid, **resolved[cid]} for cid in ids]
        n_pass = sum(1 for it in items if it["result"] == "pass")
        n_fail = len(items) - n_pass
        rate_fail = (n_fail / len(items)) if items else None
        return items, n_pass, n_fail, rate_fail

    gate_items, gate_pass, gate_fail, gate_rate = summarize(b_stage1["gate_sample_ids"])
    census_items, census_pass, census_fail, census_rate = summarize(b_stage1["category_census_ids"])

    return {
        "sample_size": len(gate_items), "sampled_ids": b_stage1["gate_sample_ids"],
        "items": gate_items, "pass": gate_pass, "fail": gate_fail,
        "rate_fail": gate_rate, "gate_threshold": 0.10,
        "gate_pass": (gate_rate is not None and gate_rate <= 0.10),
        "category_census": {"sample_size": len(census_items), "items": census_items,
                             "pass": census_pass, "fail": census_fail, "rate_fail": census_rate,
                             "note": "Every reported category cell (integration, trl_band, "
                                     "ai_cluster_fit), judged as a census. Not part of Gate C."},
        "academic_groups_companies_check": b_stage1["academic_groups_companies_check"],
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

        resp.encoding = resp.apparent_encoding  # avoid the ISO-8859-1 mojibake trap (run 1 pitfall)
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


def run_stage1():
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
            "b_matrix_cells_stage1": check_b(con),
            "c_project_evidence": check_c(),
            "d_evidence_spans": check_d(con),
        }
    except Exception as exc:
        log_pitfall("stage 7", f"audit.py run failed: {redact(exc, api_key)}")
        raise
    finally:
        con.close()

    PREJUDGE_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n{len(result['b_matrix_cells_stage1']['pending_judgment_cell_ids'])} cells need "
          f"judgment: see {JUDGE_INPUT_PATH.relative_to(REPO_ROOT)}. Write "
          f"{JUDGMENTS_PATH.relative_to(REPO_ROOT)} then rerun with --merge.")


def run_merge():
    prejudge = json.loads(PREJUDGE_PATH.read_text(encoding="utf-8"))
    judgments = json.loads(JUDGMENTS_PATH.read_text(encoding="utf-8"))
    b_final = merge_b(prejudge["b_matrix_cells_stage1"], judgments)
    result = {k: v for k, v in prejudge.items() if k != "b_matrix_cells_stage1"}
    result["b_matrix_cells"] = b_final
    FINAL_PATH.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--merge", action="store_true",
                         help="fold data/work/audit_run2_judgments.json into the prejudge result")
    args = parser.parse_args()
    if args.merge:
        run_merge()
    else:
        run_stage1()


if __name__ == "__main__":
    main()
