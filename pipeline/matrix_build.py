"""Stage 6 build. See PLAN.md stage 6 and the comparison-framework skill.

Usage (from repo root, after pipeline.matrix_export):
    .venv/bin/python -m pipeline.matrix_build

Turns the analyst's cell decisions in data/work/matrix_cells.yaml into
deliverables/comparison_matrix.csv (long format, one row per route per
dimension). Evidence quotes are never typed: each quote spec
[source, start, end] names a paper_id (or "row:N" for data/projects.csv) and
the script slices the text from `start` through `end` out of that paper's
abstract or that row's evidence_quote. With no `end`, the quote runs to the
end of the sentence. Two dimensions are computed here, not read:

    academic_groups  core papers whose tags.tech_route is the route, counted
                     per author from paper_authors; top 5 by count, ties broken
                     by graphs/top_pis.csv order; name and institution from
                     graphs/top_pis.csv.
    companies        data/projects.csv rows whose tech_route is the route. The
                     evidence_quote is the first row quote that names its own
                     entity. When no row quote names its entity, the YAML
                     holds a hand-written companies cell instead, and it must
                     cite exactly the rows that carry the route.

Any (route, dimension) the YAML leaves out becomes not_reported_in_abstract
with a note naming the route's default full-text paper.

Checks (the script stops on any failure): every quote is a verbatim
substring of its source, under 40 words, and comes from a paper in that
route's data/work/route_<name>.json; every number typed in value, unit,
value_min, value_max, or note appears in one of the cell's quotes; every
cell with a value cites a paper_id or a project row; every reported value
shares a content word or number with its evidence_quote (the same test as
audit check (b), pipeline.audit.value_in_quote), so a bare category code
such as lab or integrated_photonic must name the signal words its quote
gives, for example "lab (fabricated)".

Safe to run twice: the CSV is fully rewritten.
"""
import csv
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

import yaml

from pipeline.audit import value_in_quote

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
WORK_DIR = REPO_ROOT / "data" / "work"
CELLS_PATH = WORK_DIR / "matrix_cells.yaml"
PROJECTS_PATH = REPO_ROOT / "data" / "projects.csv"
TOP_PIS_PATH = REPO_ROOT / "graphs" / "top_pis.csv"
OUT_PATH = REPO_ROOT / "deliverables" / "comparison_matrix.csv"

ROUTES = ["mems_3d", "mems_2d", "mems_silicon_photonic", "lcos", "piezo",
          "thermo_optic", "electro_optic", "soa", "robotic_patch_panel"]
DIMENSIONS = ["switching_time", "insertion_loss", "port_count", "polarization_dependent_loss",
              "crosstalk", "wavelength_range", "integration", "packaging_notes", "trl_band",
              "academic_groups", "companies", "ai_cluster_fit", "cost_per_port", "scaling_limit"]
COLUMNS = ["tech_route", "dimension", "value", "unit", "value_min", "value_max", "status",
           "paper_ids", "project_rows", "evidence_quote", "confidence", "note"]
STATUSES = {"reported", "derived", "not_reported_in_abstract", "no_source"}

# Query behind academic_groups (also reproducible by hand in the auditor).
GROUPS_SQL = """
SELECT pa.author_id, pa.paper_id
FROM paper_authors pa
JOIN papers p ON p.paper_id = pa.paper_id
JOIN tags t ON t.paper_id = pa.paper_id
WHERE p.core_set = 1 AND t.tech_route = ?
"""

NUM_RE = re.compile(r"\d+(?:[.,]\d+)*")
# Tokens that carry digits but are identifiers, not claims.
ID_RE = re.compile(r"\bW\d+\b|arxiv:\d+\.\d+|mems_[23]d|\brows? \d+(?:(?:, | and |; )\d+)*|\b[23]-?D\b")


def load_route_papers():
    papers = {}
    for route in ROUTES:
        path = WORK_DIR / f"route_{route}.json"
        papers[route] = {p["paper_id"]: p for p in json.loads(path.read_text(encoding="utf-8"))}
    return papers


def load_projects():
    with open(PROJECTS_PATH, newline="", encoding="utf-8") as f:
        return {i: row for i, row in enumerate(csv.DictReader(f), start=1)}


def slice_quote(text, start, end=None):
    i = text.find(start)
    if i < 0:
        raise ValueError(f"start fragment not found: {start!r}")
    if end:
        j = text.find(end, i)
        if j < 0:
            raise ValueError(f"end fragment not found after start: {end!r}")
        return text[i:j + len(end)]
    j = text.find(". ", i)
    return text[i:] if j < 0 else text[i:j + 1]


def resolve_quote(spec, route, route_papers, projects):
    src, start, *rest = spec
    end = rest[0] if rest else None
    if src.startswith("row:"):
        return src, slice_quote(projects[int(src[4:])]["evidence_quote"], start, end)
    paper = route_papers[route].get(src)
    if paper is None:
        raise ValueError(f"{src} is not in data/work/route_{route}.json")
    if not paper["abstract"]:
        raise ValueError(f"{src} has no abstract")
    return src, slice_quote(paper["abstract"], start, end)


def check_numbers(where, fields, quotes):
    pool = " ".join(quotes)
    for text in fields:
        for num in NUM_RE.findall(ID_RE.sub(" ", text or "")):
            if num not in pool:
                raise ValueError(f"{where}: number {num!r} in {text!r} is in no quote of this cell")


def src_label(src):
    return f"projects.csv row {src[4:]}" if src.startswith("row:") else src


def build_spec_cell(c, route_papers, projects):
    route, dim = c["route"], c["dim"]
    where = f"{route}/{dim}"
    status = c["status"]
    if status not in STATUSES:
        raise ValueError(f"{where}: bad status {status}")
    resolved = [resolve_quote(q, route, route_papers, projects) for q in c.get("quotes", [])]
    for src, q in resolved:
        if len(q.split()) >= 40:
            raise ValueError(f"{where}: quote from {src} has {len(q.split())} words")
    quotes = [q for _, q in resolved]
    note = c.get("note", "")
    check_numbers(where, [str(c.get(k, "")) for k in ("value", "unit", "min", "max")] + [note], quotes)
    srcs = list(dict.fromkeys(s for s, _ in resolved))
    extra = [f'{src_label(s)} says "{q}"' for s, q in resolved[1:]]
    row = {
        "tech_route": route, "dimension": dim,
        "value": str(c.get("value", "not reported in abstract")),
        "unit": str(c.get("unit", "")),
        "value_min": str(c.get("min", "")), "value_max": str(c.get("max", "")),
        "status": status,
        "paper_ids": ";".join(s for s in srcs if not s.startswith("row:")),
        "project_rows": ";".join(s[4:] for s in srcs if s.startswith("row:")),
        "evidence_quote": quotes[0] if quotes else "",
        "confidence": c.get("conf", ""),
        "note": " ".join([note] + extra).strip(),
    }
    if status in ("reported", "derived") and not (row["paper_ids"] or row["project_rows"]):
        raise ValueError(f"{where}: a cell with a value cites no paper_id or project row")
    return row


def tag_counts(papers, field):
    c = Counter((p["tags"][field] or "null") for p in papers.values() if p["match"] == "primary")
    return ", ".join(f"{k} {v}" for k, v in sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def academic_groups(con, route, pis):
    by_author = defaultdict(set)
    for author_id, paper_id in con.execute(GROUPS_SQL, (route,)):
        by_author[author_id].add(paper_id)
    order = {a: i for i, a in enumerate(pis)}
    ranked = sorted(by_author, key=lambda a: (-len(by_author[a]), order.get(a, len(order))))
    top = ranked[:5]
    if not top:
        return {"value": "none", "status": "no_source", "note": "no core paper with this route has authors"}
    cutoff = len(by_author[top[-1]])
    tied = sum(1 for a in ranked if len(by_author[a]) == cutoff)
    value = "; ".join(f"{pis[a]['author']} ({pis[a]['institution']}) {len(by_author[a])}" for a in top)
    ids = sorted(set().union(*(by_author[a] for a in top)))
    note = (f"Computed by pipeline.matrix_build from paper_authors and tags (core set, primary tech_route). "
            f"Top {len(top)} of {len(ranked)} authors by paper count on this route, ties broken by "
            f"graphs/top_pis.csv order. Number of authors tied at the cutoff count of {cutoff} is {tied}.")
    return {"value": value, "status": "derived", "paper_ids": ";".join(ids), "confidence": "high", "note": note}


def companies(route, projects):
    rows = [(i, r) for i, r in projects.items() if r["tech_route"] == route]
    if not rows:
        return {"value": "none in projects.csv", "status": "no_source",
                "note": "No data/projects.csv row carries this tech_route. Rows with tech_route unclear are listed under the table."}
    value = "; ".join(f"{r['entity']} (row {i}, stage {r['stage']})" for i, r in rows)
    named = [r for _, r in rows if r["entity"].lower() in r["evidence_quote"].lower()]
    return {"value": value, "status": "reported", "project_rows": ";".join(str(i) for i, _ in rows),
            "evidence_quote": (named or [rows[0][1]])[0]["evidence_quote"], "confidence": "medium",
            "note": "Vendor claims from data/projects.csv. evidence_quote is the first listed row's quote that names its entity; each row carries its own URL and quote."}


def main():
    spec = yaml.safe_load(CELLS_PATH.read_text(encoding="utf-8"))
    route_papers = load_route_papers()
    projects = load_projects()
    with open(TOP_PIS_PATH, newline="", encoding="utf-8") as f:
        pis = {r["author_id"]: r for r in csv.DictReader(f)}

    cells = {}
    for c in spec["cells"]:
        key = (c["route"], c["dim"])
        if key in cells:
            raise ValueError(f"duplicate cell {key}")
        if c["route"] not in ROUTES or c["dim"] not in DIMENSIONS:
            raise ValueError(f"unknown route or dimension {key}")
        cells[key] = build_spec_cell(c, route_papers, projects)

    con = sqlite3.connect(DB_PATH)
    rows = []
    for route in ROUTES:
        n_primary = sum(p["match"] == "primary" for p in route_papers[route].values())
        for dim in DIMENSIONS:
            base = dict.fromkeys(COLUMNS, "")
            base.update(tech_route=route, dimension=dim)
            if dim == "academic_groups":
                base.update(academic_groups(con, route, pis))
            elif (route, dim) in cells:
                base.update(cells[(route, dim)])
                if dim == "companies":
                    want = set(companies(route, projects).get("project_rows", "").split(";"))
                    if set(base["project_rows"].split(";")) != want:
                        raise ValueError(f"{route}/companies: YAML cites rows {base['project_rows']}, "
                                         f"projects.csv has {';'.join(sorted(want))}")
            elif dim == "companies":
                base.update(companies(route, projects))
            elif n_primary == 0:
                base.update(value="no source", status="no_source", note="No core paper carries this route.")
            else:
                read = spec["default_read"][route]
                base.update(value="not reported in abstract", status="not_reported_in_abstract",
                            note=f"Not stated in any abstract of this route. A human should check the full text of {read}.")
            if dim in ("integration", "trl_band"):
                field = "integration" if dim == "integration" else "trl_band"
                base["note"] = (base["note"] + f" tags.{field} over this route's primary core papers: "
                                f"{tag_counts(route_papers[route], field)}.").strip()
            rows.append(base)
    con.close()

    unlinked = [f"{r['tech_route']}/{r['dimension']}" for r in rows
                if r["status"] == "reported" and not value_in_quote(r["value"], r["evidence_quote"])]
    if unlinked:
        raise ValueError(f"value shares no content word or number with evidence_quote: {', '.join(unlinked)}")

    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    by_status = Counter(r["status"] for r in rows)
    print(f"{OUT_PATH.relative_to(REPO_ROOT).as_posix()} rows={len(rows)} " +
          " ".join(f"{k}={v}" for k, v in sorted(by_status.items())))


if __name__ == "__main__":
    main()
