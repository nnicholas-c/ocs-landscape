"""Stage 6 render. See PLAN.md stage 6 and the comparison-framework skill.

Usage (from repo root, after pipeline.matrix_build):
    .venv/bin/python -m pipeline.matrix_render

Reads deliverables/comparison_matrix.csv and writes
deliverables/comparison_matrix.md (one overview table, one section per route
with every cell's sources and evidence quote, a footer with cell counts by
status). Also writes deliverables/reading_list.md from the reading_list in
data/work/matrix_cells.yaml, taking title and year from data/db/papers.sqlite
and the cells each paper would fill from the CSV.

Output is plain ASCII. Quotes are folded (micro sign to u, times sign to x,
curly quotes to straight), so the CSV stays the verbatim record.

Safe to run twice: both files are fully rewritten.
"""
import csv
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

import yaml
from unidecode import unidecode

from pipeline.matrix_build import DIMENSIONS, ROUTES

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "deliverables" / "comparison_matrix.csv"
MD_PATH = REPO_ROOT / "deliverables" / "comparison_matrix.md"
READING_PATH = REPO_ROOT / "deliverables" / "reading_list.md"
CELLS_PATH = REPO_ROOT / "data" / "work" / "matrix_cells.yaml"
PROJECTS_PATH = REPO_ROOT / "data" / "projects.csv"
WORK_DIR = REPO_ROOT / "data" / "work"
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"

OFF_MATRIX = ["architecture_only", "other", "unclear"]
# unidecode maps Greek mu to "m", which would turn microseconds into milliseconds.
PRE = {"μ": "u", "µ": "u", "π": "pi", "—": "-", "–": "-"}
TABLE_CELL_MAX = 70
ML_RE = re.compile(r"\b(TPU|GPU|accelerator|machine learning|deep learning|LLM)", re.I)


def fold(text):
    return unidecode("".join(PRE.get(c, c) for c in str(text)))


def cell_md(text):
    return fold(text).replace("|", "/").replace("\n", " ")


def short(row):
    if row["status"] == "not_reported_in_abstract":
        return "[not reported]"
    if row["status"] == "no_source":
        return "[no source]"
    # Append the unit unless the value already carries it.
    unit = row["unit"]
    text = row["value"] if not unit or unit in row["value"] else f"{row['value']} {unit}"
    return text if len(text) <= TABLE_CELL_MAX else text[:TABLE_CELL_MAX - 3].rstrip() + "..."


def sources(row):
    parts = [p for p in row["paper_ids"].split(";") if p]
    parts += [f"projects.csv row {r}" for r in row["project_rows"].split(";") if r]
    return "; ".join(parts)


def render_matrix(rows):
    by_key = {(r["tech_route"], r["dimension"]): r for r in rows}
    out = ["# OCS comparison matrix", "",
           "Optical circuit switching (OCS) technology routes compared on the dimensions of the comparison-framework skill. "
           "Every cell comes from deliverables/comparison_matrix.csv, which pipeline.matrix_build fills from core-paper abstracts "
           "and data/projects.csv. This file is written by pipeline.matrix_render, not by hand.", "",
           "Abbreviations used below. MEMS is micro-electro-mechanical systems. LCoS is liquid crystal on silicon. "
           "SOA is semiconductor optical amplifier. TRL is technology readiness level. ML is machine learning. "
           "AI is artificial intelligence. GPU is graphics processing unit and TPU is tensor processing unit. "
           "CMOS is complementary metal-oxide-semiconductor. WSS is wavelength selective switch. "
           "Quoted abstracts use more abbreviations of their own, left as written.", "",
           "Status reported means a quoted source states the value. derived means a script computed it, as the note says. "
           "not_reported_in_abstract means the route has papers but their abstracts do not say, and the note names the paper "
           "whose full text should be read. no_source is used only for companies cells where no row of data/projects.csv "
           "carries the route. Every route has core papers.", "",
           "Category cells (integration, trl_band, ai_cluster_fit) hold only the controlled label. The reasoning is in the note. "
           "ai_cluster_fit follows the comparison-framework definition, so yes means an abstract uses or proposes the route for "
           "accelerator clusters, reconfigurable data center topologies, or replacing a spine layer. The note says whether "
           "any abstract names accelerators or machine learning directly.", "",
           "When a cell draws on several sources, the evidence holds one exact quote per source. The CSV separates them with || "
           "and this file shows the separator as // because a bar would break the table. "
           "projects.csv row N means the Nth data row of data/projects.csv, not counting the header.", "",
           "Quotes here are folded to plain ASCII, so the micro sign reads u and the times sign reads x. "
           "The CSV keeps every quote verbatim.", "",
           "## Overview", "",
           "| tech_route | " + " | ".join(DIMENSIONS) + " |",
           "|" + "---|" * (len(DIMENSIONS) + 1)]
    for route in ROUTES:
        out.append(f"| {route} | " + " | ".join(cell_md(short(by_key[(route, d)])) for d in DIMENSIONS) + " |")

    out += ["", "## Routes not in the table", ""]
    for route in OFF_MATRIX:
        path = WORK_DIR / f"route_{route}.json"
        papers = [p for p in json.loads(path.read_text(encoding="utf-8")) if p["match"] == "primary"] if path.exists() else []
        out.append(f"- {route}. {len(papers)} core papers carry this primary tech_route (data/work/route_{route}.json). "
                   "They are left out of the matrix by the comparison-framework skill.")
        if route == "architecture_only":
            ml = [p for p in papers if p["abstract"] and ML_RE.search(p["abstract"])]
            with_sec = sum(1 for p in ml if p["tags"]["tech_route_secondary"])
            out.append(f"  Of these, {len(ml)} abstracts name accelerators, GPUs, TPUs, or ML training "
                       f"(regex ML_RE in pipeline/matrix_render.py), and {with_sec} of them carry a tech_route_secondary, "
                       "so the others reach no route's ai_cluster_fit cell. Examples are "
                       + ", ".join(p["paper_id"] for p in ml[:5]) + ".")
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        off = [(i, r) for i, r in enumerate(csv.DictReader(f), start=1) if r["tech_route"] not in ROUTES]
    for i, r in off:
        out.append(f"- projects.csv row {i} ({cell_md(r['entity'])}, {cell_md(r['product_or_project'])}) has tech_route "
                   f"{r['tech_route']}, so it appears in no companies cell.")

    for route in ROUTES:
        out += ["", f"## {route}", "",
                "| dimension | value | unit | status | confidence | sources | evidence quote | note |",
                "|---|---|---|---|---|---|---|---|"]
        for d in DIMENSIONS:
            r = by_key[(route, d)]
            out.append("| " + " | ".join(cell_md(x) for x in (
                d, r["value"], r["unit"], r["status"], r["confidence"], sources(r),
                " || ".join(f'"{q}"' for q in r["evidence_quote"].split(" || ") if q), r["note"])) + " |")

    counts = Counter(r["status"] for r in rows)
    out += ["", "## Cell counts by status", "",
            f"Total cells {len(rows)}, which is {len(ROUTES)} routes times {len(DIMENSIONS)} dimensions.", "",
            "| tech_route | " + " | ".join(sorted(counts)) + " |",
            "|" + "---|" * (len(counts) + 1)]
    for route in ROUTES:
        c = Counter(r["status"] for r in rows if r["tech_route"] == route)
        out.append(f"| {route} | " + " | ".join(str(c[s]) for s in sorted(counts)) + " |")
    out.append("| all | " + " | ".join(str(counts[s]) for s in sorted(counts)) + " |")
    return "\n".join(out) + "\n"


def render_reading_list(rows):
    spec = yaml.safe_load(CELLS_PATH.read_text(encoding="utf-8"))
    con = sqlite3.connect(DB_PATH)
    out = ["# Reading list", "",
           "Ten core papers whose full text would fill the most matrix cells that abstracts left empty, "
           "or settle the widest ranges. Picked by the stage 6 analyst. Title and year come from data/db/papers.sqlite, "
           "and the cell lists come from deliverables/comparison_matrix.csv. Written by pipeline.matrix_render.", "",
           "MEMS is micro-electro-mechanical systems, LCoS is liquid crystal on silicon, and SOA is semiconductor "
           "optical amplifier.", ""]
    for n, (pid, why) in enumerate(spec["reading_list"], start=1):
        title, year = con.execute("SELECT title, year FROM papers WHERE paper_id = ?", (pid,)).fetchone()
        fills = [f"{r['tech_route']} {r['dimension']}" for r in rows
                 if r["status"] == "not_reported_in_abstract" and pid in r["note"]]
        checks = [f"{r['tech_route']} {r['dimension']}" for r in rows
                  if r["status"] == "reported" and (pid in r["paper_ids"].split(";") or pid in r["note"])
                  and (r["value_min"] or r["confidence"] == "low")]
        line = f"{n}. {pid}, \"{fold(title)}\" ({year}). {fold(why)}"
        line += f" Would fill {', '.join(fills)}." if fills else " Fills no empty cell by name."
        if checks:
            line += f" Would check {', '.join(checks)}."
        out.append(line)
    con.close()
    return "\n".join(out) + "\n"


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for path, text in ((MD_PATH, render_matrix(rows)), (READING_PATH, render_reading_list(rows))):
        assert text.isascii(), f"{path.name} has non-ASCII characters"
        path.write_text(text, encoding="utf-8")
        print(f"{path.relative_to(REPO_ROOT).as_posix()} lines={text.count(chr(10))}")


if __name__ == "__main__":
    main()
