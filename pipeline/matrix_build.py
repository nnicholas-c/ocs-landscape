"""Stage 6 build. See PLAN.md stage 6 and the comparison-framework skill.

Usage (from repo root, after pipeline.matrix_export):
    .venv/bin/python -m pipeline.matrix_build
then .venv/bin/python -m pipeline.matrix_render

Reads the analyst's cell decisions from data/work/matrix_cells.yaml and writes
deliverables/comparison_matrix.csv (long format, one row per route and dimension).
Every evidence quote is copied here, never typed, from the abstract in
data/work/route_<route>.json or from the evidence_quote of a data/projects.csv row,
located by the anchors in the YAML. Several quotes are joined by " || ".
academic_groups is counted from data/db/papers.sqlite and graphs/top_pis.csv, and
companies is read from data/projects.csv. projects.csv row N is its Nth data row.

Safe to run twice: the CSV is fully rewritten.
"""
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
CELLS_PATH = REPO_ROOT / "data" / "work" / "matrix_cells.yaml"
WORK_DIR = REPO_ROOT / "data" / "work"
PROJECTS_PATH = REPO_ROOT / "data" / "projects.csv"
PIS_PATH = REPO_ROOT / "graphs" / "top_pis.csv"
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
CSV_PATH = REPO_ROOT / "deliverables" / "comparison_matrix.csv"

ROUTES = ["mems_3d", "mems_2d", "mems_silicon_photonic", "lcos", "piezo",
          "thermo_optic", "electro_optic", "soa", "robotic_patch_panel"]
DIMENSIONS = ["switching_time", "insertion_loss", "port_count", "polarization_dependent_loss",
              "crosstalk", "wavelength_range", "integration", "packaging_notes", "trl_band",
              "academic_groups", "companies", "ai_cluster_fit", "cost_per_port", "scaling_limit"]
CATEGORIES = {
    "integration": {"free_space_bulk", "integrated_photonic", "mechanical_fiber", "unclear"},
    "trl_band": {"lab", "pilot", "production", "unclear"},
    "ai_cluster_fit": {"yes", "partial", "no", "not_reported"},
}
COLUMNS = ["tech_route", "dimension", "value", "unit", "value_min", "value_max", "status",
           "paper_ids", "project_rows", "evidence_quote", "confidence", "note"]
SEP = " || "
MAX_WORDS = 40  # a quote must stay under this many words
NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
# Identifiers that contain digits but are not numbers: paper IDs, route names, 2D/3D, row refs.
ID_RE = re.compile(r"W\d+|arxiv:[\d.]+|mems_[23]d|\b[23]D\b|\brows? \d+")
SENT_START = re.compile(r"[.!?]\s+(?=[A-Z(])")
SENT_END = re.compile(r"[.!?](?=\s+[A-Z(]|\s*$)")


def extract(text, anchors):
    """Copy a quote out of text. No anchor: all of it. One: its sentence. Two: start through end."""
    if not anchors:
        return text.strip()
    i = text.index(anchors[0])
    if len(anchors) == 2:
        return text[i:text.index(anchors[1], i) + len(anchors[1])]
    start = max([0] + [m.end() for m in SENT_START.finditer(text) if m.end() <= i])
    end = SENT_END.search(text, i)
    return text[start:end.end() if end else len(text)].strip()


def row(route, dim, **kw):
    return {c: "" for c in COLUMNS} | {"tech_route": route, "dimension": dim} | kw


def spec_cell(route, dim, c, papers, projects):
    quotes, pids, prows = [], [], []
    for src, *anchors in c.get("quotes", []):
        if src.startswith("row "):
            n = int(src.split()[1])
            assert projects[n]["tech_route"] == route, f"{route} {dim}: row {n} is another route"
            text = projects[n]["evidence_quote"]
            prows.append(str(n))
        else:
            text = papers[src]["abstract"]  # KeyError: the paper is not in this route's file
            pids.append(src)
        try:
            q = extract(text, anchors)
        except ValueError:
            raise SystemExit(f"{route} {dim}: anchor {anchors} not found in {src}")
        assert q in text and len(q.split()) < MAX_WORDS, f"{route} {dim}: bad quote from {src}: {q!r}"
        quotes.append(q)
    # One quote per contributing paper or project row, in the order of paper_ids then project_rows as given.
    assert len(quotes) == len(set(pids)) + len(set(prows)), f"{route} {dim}: a source has more than one quote"
    joined = SEP.join(quotes)
    value = str(c.get("value", ""))
    note = c.get("note", "")
    # CLAUDE.md rule 1: a number in value or note must stand, as a whole number, in one of this cell's quotes.
    quoted = set(NUM_RE.findall(joined))
    for num in NUM_RE.findall(value + " " + ID_RE.sub(" ", note)):
        assert num in quoted, f"{route} {dim}: number {num} is in no quote"
    if dim in CATEGORIES:
        assert value in CATEGORIES[dim], f"{route} {dim}: {value!r} is not a controlled label"
        if dim == "integration":
            k = sum(p["tags"]["integration"] == value for p in papers.values())
            note = (f"{note} In the tags table {k} of the {len(papers)} route papers "
                    f"in data/work/route_{route}.json carry integration {value}.").strip()
    assert not value or quotes, f"{route} {dim}: value without a quote"
    return row(route, dim, value=value, unit=c.get("unit", ""),
               value_min=c.get("value_min", ""), value_max=c.get("value_max", ""),
               status="reported" if value else "not_reported_in_abstract",
               paper_ids=";".join(dict.fromkeys(pids)), project_rows=";".join(prows),
               evidence_quote=joined, confidence=c.get("confidence", ""), note=note)


def academic_groups(route, papers, con, pis):
    ids = list(papers)
    by_author = defaultdict(set)
    for author_id, pid in con.execute(
            f"SELECT author_id, paper_id FROM paper_authors WHERE paper_id IN ({','.join('?' * len(ids))})", ids):
        if author_id in pis:
            by_author[author_id].add(pid)
    ranked = sorted(by_author, key=lambda a: (-len(by_author[a]), -int(pis[a]["core_paper_count"]), pis[a]["author"]))
    top = ranked[:5]
    cut = len(by_author[top[-1]])
    tied_out = sum(1 for a in ranked[5:] if len(by_author[a]) == cut)
    value = "; ".join(
        f"{pis[a]['author']} ({pis[a]['institution'] or 'institution unknown'}) "
        f"{len(by_author[a])} paper{'s' if len(by_author[a]) != 1 else ''}" for a in top)
    note = (f"Derived by pipeline/matrix_build.py. Authors from graphs/top_pis.csv ranked by how many papers of "
            f"data/work/route_{route}.json ({len(ids)} in all, primary and secondary route matches) they coauthor, "
            f"ties broken by core_paper_count in graphs/top_pis.csv, institution as listed there."
            + (f" {tied_out} more authors tie with the last one listed." if tied_out else ""))
    return row(route, "academic_groups", value=value, status="derived", confidence="high",
               paper_ids=";".join(sorted(set().union(*(by_author[a] for a in top)))), note=note)


def companies(route, projects):
    hits = [(n, r) for n, r in projects.items() if r["tech_route"] == route]
    if not hits:
        unclear = ", ".join(r["entity"] for r in projects.values() if r["tech_route"] == "unclear")
        return row(route, "companies", status="no_source",
                   note=f"No row in data/projects.csv has tech_route {route}. "
                        f"Rows with tech_route unclear ({unclear}) are not counted in any route.")
    for n, r in hits:
        assert len(r["evidence_quote"].split()) < MAX_WORDS, f"row {n} quote too long"
    return row(route, "companies", value="; ".join(r["entity"] for _, r in hits), status="reported",
               project_rows=";".join(str(n) for n, _ in hits),
               evidence_quote=SEP.join(r["evidence_quote"].strip() for _, r in hits), confidence="medium",
               note=f"Vendor claims. Entities are the data/projects.csv rows whose tech_route is {route}, "
                    "a route the scout assigned (see each row's note there).")


def main():
    spec = yaml.safe_load(CELLS_PATH.read_text(encoding="utf-8"))["cells"]
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        projects = dict(enumerate(csv.DictReader(f), start=1))
    with open(PIS_PATH, newline="", encoding="utf-8") as f:
        pis = {r["author_id"]: r for r in csv.DictReader(f)}
    con = sqlite3.connect(DB_PATH)

    out = []
    for route in ROUTES:
        papers = {p["paper_id"]: p for p in json.loads((WORK_DIR / f"route_{route}.json").read_text(encoding="utf-8"))}
        cells = spec[route]
        assert set(cells) | {"academic_groups", "companies"} == set(DIMENSIONS), f"{route}: missing or extra dimensions"
        for dim in DIMENSIONS:
            if dim == "academic_groups":
                out.append(academic_groups(route, papers, con, pis))
            elif dim == "companies":
                out.append(companies(route, projects))
            else:
                out.append(spec_cell(route, dim, cells[dim], papers, projects))
    con.close()

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(out)
    print(f"{CSV_PATH.relative_to(REPO_ROOT).as_posix()} rows={len(out)} "
          + " ".join(f"{k}={v}" for k, v in sorted(Counter(r['status'] for r in out).items())))


if __name__ == "__main__":
    main()
