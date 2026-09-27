"""Step 3 project timeline. Writes graphs/project_timeline.html from data/projects.csv.

Usage (from repo root):
    .venv/bin/python -m pipeline.project_timeline

One row per entity with a known first_public_date (an ISO date), a dot at
that date colored by stage. Entities whose first_public_date is "unknown"
are listed under the chart, not plotted and not given a guessed date. Any
other first_public_date or stage value stops the script. Prints every count
it plots. Page shell, colors for chrome and theme handling are shared with
pipeline.tech_map. Stages concept < prototype < pilot < shipping are ordered,
so they take one blue ramp from the dataviz reference palette (validated with
validate_palette.js --ordinal in both modes); "unknown" takes the neutral gray.
"""

import csv
from datetime import date
from pathlib import Path

from pipeline.tech_map import GRAPHS_DIR, esc, page, write_page

REPO_ROOT = Path(__file__).resolve().parent.parent
PROJECTS_CSV = REPO_ROOT / "data" / "projects.csv"

STAGES = ["concept", "prototype", "pilot", "shipping", "unknown"]
STAGE_COLORS = {
    "concept": ("#86b6ef", "#184f95"),
    "prototype": ("#3987e5", "#2a78d6"),
    "pilot": ("#1c5cab", "#6da7ec"),
    "shipping": ("#0d366b", "#b7d3f6"),
    "unknown": ("#898781", "#898781"),
}


def load():
    rows = list(csv.DictReader(open(PROJECTS_CSV, encoding="utf-8")))
    entities = [r["entity"] for r in rows]
    if len(set(entities)) != len(entities):
        raise ValueError("projects.csv has an entity on more than one row; one row per entity is required")
    known, unknown = [], []
    for r in rows:
        if r["stage"] not in STAGES:
            raise ValueError(f"{r['entity']}: unexpected stage {r['stage']!r}")
        if r["first_public_date"] == "unknown":
            unknown.append(r)
        else:
            r["date"] = date.fromisoformat(r["first_public_date"])  # raises on anything else
            known.append(r)
    known.sort(key=lambda r: (r["date"], r["entity"]))
    unknown.sort(key=lambda r: (STAGES.index(r["stage"]), r["entity"]))
    return rows, known, unknown


def per_stage(rows):
    return {s: sum(r["stage"] == s for r in rows) for s in STAGES}


def render(rows, known, unknown):
    y0, y1 = known[0]["date"].year, known[-1]["date"].year + 1
    d0, d1 = date(y0, 1, 1).toordinal(), date(y1, 1, 1).toordinal()
    label_w, plot_w, right_pad, row_h, top_pad, axis_h = 150, 480, 90, 36, 8, 28
    width = label_w + plot_w + right_pad
    base = top_pad + row_h * len(known)
    height = base + axis_h

    def X(d):
        return label_w + (d.toordinal() - d0) / (d1 - d0) * plot_w

    parts = []
    for y in range(y0, y1 + 1):
        x = X(date(y, 1, 1))
        parts.append(f'<line x1="{x:.2f}" y1="{top_pad}" x2="{x:.2f}" y2="{base}" stroke="var(--grid)" stroke-width="1"/>')
        parts.append(f'<text class="tick" x="{x:.2f}" y="{base + 18}" text-anchor="middle">{y}</text>')
    parts.append(f'<line x1="{label_w}" y1="{base}" x2="{label_w + plot_w}" y2="{base}" stroke="var(--axis)" stroke-width="1"/>')
    for i, r in enumerate(known):
        cy = top_pad + i * row_h + row_h / 2
        cx = X(r["date"])
        tip = f"{r['entity']}, {r['product_or_project']}, stage {r['stage']}, first public {r['first_public_date']}"
        parts.append(f'<text x="{label_w - 10}" y="{cy + 4:g}" text-anchor="end">{esc(r["entity"])}</text>')
        # 24px transparent hit target around an r=5 dot with a 2px surface ring
        parts.append(f'<g class="mark"><title>{esc(tip)}</title>'
                     f'<circle cx="{cx:.2f}" cy="{cy:g}" r="12" fill="transparent"/>'
                     f'<circle cx="{cx:.2f}" cy="{cy:g}" r="5" fill="var(--st-{r["stage"]})" '
                     'stroke="var(--surface)" stroke-width="2"/></g>')
        parts.append(f'<text x="{cx + 10:.2f}" y="{cy + 4:g}">{r["first_public_date"]}</text>')
    svg = (f'<svg viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="First public date per entity, colored by stage">{"".join(parts)}</svg>')

    plotted = per_stage(known)
    legend = "".join(f'<span><span class="sw dot" style="background:var(--st-{s})"></span>{s} ({plotted[s]})</span>'
                     for s in STAGES if plotted[s])
    trs = "".join(
        f"<tr><td>{esc(r['entity'])}</td><td>{esc(r['product_or_project'])}</td><td>{r['stage']}</td>"
        f"<td>{r['first_public_date']}</td><td>{esc(r['evidence_url'])}</td></tr>" for r in known)
    table = ("<details><summary>Table view</summary><table><tr><th>entity</th><th>product or project</th>"
             f"<th>stage</th><th>first public date</th><th>evidence url</th></tr>{trs}</table></details>")
    items = "".join(f"<li>{esc(r['entity'])}, {esc(r['product_or_project'])} (stage {r['stage']})</li>"
                    for r in unknown)
    subtitle = (f"{len(known)} of {len(rows)} entities in data/projects.csv have a known first_public_date and are "
                f"plotted, colored by stage. The other {len(unknown)} are listed under the chart.")
    body = (f'<div class="card"><div class="legend">{legend}</div><div class="chart">{svg}</div>{table}</div>'
            f"<h2>First public date unknown ({len(unknown)} entities, not plotted)</h2><ul>{items}</ul>")
    return page("OCS project timeline", esc(subtitle), body, {f"st-{s}": c for s, c in STAGE_COLORS.items()})


def main():
    rows, known, unknown = load()
    if not known:
        raise SystemExit("no entity in data/projects.csv has a known first_public_date; nothing to plot")
    print("== project_timeline ==")
    print(f"source: data/projects.csv, {len(rows)} rows, {len({r['entity'] for r in rows})} entities")
    print(f"known first_public_date (plotted): {len(known)}")
    print(f"unknown first_public_date (listed under chart): {len(unknown)}")
    for label, subset in (("plotted", known), ("listed", unknown), ("all rows", rows)):
        print(f"per stage, {label}: " + ", ".join(f"{s} {n}" for s, n in per_stage(subset).items()))
    print("plotted rows (entity, stage, first_public_date):")
    for r in known:
        print(f"  {r['entity']}, {r['stage']}, {r['first_public_date']}")
    print("listed rows, date unknown (entity, stage):")
    for r in unknown:
        print(f"  {r['entity']}, {r['stage']}")
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    size = write_page(GRAPHS_DIR / "project_timeline.html", render(rows, known, unknown))
    print(f"wrote graphs/project_timeline.html ({size} bytes)")


if __name__ == "__main__":
    main()
