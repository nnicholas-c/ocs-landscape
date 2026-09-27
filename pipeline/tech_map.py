"""Step 3 tech map. Writes graphs/tech_map.html and decides the radar chart.

Usage (from repo root):
    .venv/bin/python -m pipeline.tech_map

(1) Core papers per tech route, stacked by trl_band, from the tags table
joined to papers (core_set = 1). Prints the SQL and every count it plots.
(2) Radar decision. For each of the 6 numeric matrix dimensions, counts the
routes in deliverables/comparison_matrix.csv whose cell has status
"reported". A dimension qualifies at 5 or more routes. The radar
(graphs/tech_radar.html) is drawn only if 4 or more dimensions qualify.

Output is plain inline SVG with no script and no external file, so the page
is self-contained and byte-identical on every run (no timestamps, no random
ids). Colors: TRL (technology readiness level) bands lab < pilot < production
are ordered, so they take one blue ramp from the dataviz reference palette
(validated with validate_palette.js --ordinal in both modes); "unclear" is
outside the order and takes the neutral muted gray.
"""

import csv
import html
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
MATRIX_CSV = REPO_ROOT / "deliverables" / "comparison_matrix.csv"
GRAPHS_DIR = REPO_ROOT / "graphs"

COUNT_SQL = """SELECT t.tech_route, t.trl_band, COUNT(*) AS n
FROM tags t JOIN papers p ON p.paper_id = t.paper_id
WHERE p.core_set = 1
GROUP BY t.tech_route, t.trl_band
ORDER BY t.tech_route, t.trl_band"""

UNTAGGED_SQL = """SELECT COUNT(*) FROM papers p LEFT JOIN tags t ON t.paper_id = p.paper_id
WHERE p.core_set = 1 AND t.paper_id IS NULL"""

BANDS = ["lab", "pilot", "production", "unclear"]
RADAR_DIMS = ["switching_time", "insertion_loss", "port_count",
              "polarization_dependent_loss", "crosstalk", "wavelength_range"]
RADAR_MIN_ROUTES = 5
RADAR_MIN_DIMS = 4

# Chart chrome from the dataviz reference palette, light then dark.
CHROME = {
    "surface": ("#fcfcfb", "#1a1a19"), "page": ("#f9f9f7", "#0d0d0d"),
    "ink": ("#0b0b0b", "#ffffff"), "ink2": ("#52514e", "#c3c2b7"),
    "muted": ("#898781", "#898781"), "grid": ("#e1e0d9", "#2c2c2a"),
    "axis": ("#c3c2b7", "#383835"),
    "border": ("rgba(11,11,11,0.10)", "rgba(255,255,255,0.10)"),
}
BAND_COLORS = {
    "lab": ("#86b6ef", "#184f95"),
    "pilot": ("#2a78d6", "#3987e5"),
    "production": ("#104281", "#9ec5f4"),
    "unclear": ("#898781", "#898781"),
}


# ---------- shared page shell (also used by pipeline.project_timeline) ----------

def esc(s):
    return html.escape(str(s), quote=True)


def theme_css(tokens):
    """tokens: {name: (light, dark)}. Dark applies on OS dark unless the page
    is stamped data-theme="light", and always when stamped data-theme="dark"."""
    light = ";".join(f"--{k}:{v[0]}" for k, v in tokens.items())
    dark = ";".join(f"--{k}:{v[1]}" for k, v in tokens.items())
    return (
        f":root{{color-scheme:light;{light}}}"
        f'@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{color-scheme:dark;{dark}}}}}'
        f':root[data-theme="dark"]{{color-scheme:dark;{dark}}}'
    )


def page(title, subtitle, body, tokens):
    css = theme_css({**CHROME, **tokens}) + (
        "body{margin:0;background:var(--page);color:var(--ink);"
        'font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}'
        "main{max-width:960px;margin:0 auto;padding:24px 16px}"
        "h1{font-size:20px;font-weight:600;margin:0 0 4px}"
        "h2{font-size:15px;font-weight:600;margin:20px 0 6px}"
        ".sub{color:var(--ink2);margin:0 0 16px}"
        ".card{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px}"
        ".legend{display:flex;flex-wrap:wrap;gap:4px 16px;color:var(--ink2);font-size:13px;margin:0 0 8px}"
        ".sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px;vertical-align:-1px}"
        ".dot{border-radius:50%}"
        ".chart{overflow-x:auto}"
        ".chart svg{display:block;width:100%;min-width:560px;height:auto}"
        "svg text{fill:var(--ink2);font-size:12px}"
        "svg .tick{fill:var(--muted);font-variant-numeric:tabular-nums}"
        "svg .mark:hover{opacity:.75}"
        ".note{color:var(--ink2);font-size:13px}"
        "details{margin-top:12px;overflow-x:auto}summary{cursor:pointer;color:var(--ink2)}"
        "table{border-collapse:collapse;margin-top:8px;font-size:13px}"
        "th,td{padding:4px 10px;border-bottom:1px solid var(--grid);text-align:left}"
        "td.n,th.n{text-align:right;font-variant-numeric:tabular-nums}"
        "ul{margin:4px 0;padding-left:20px}"
    )
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<meta name="color-scheme" content="light dark">'
        f"<title>{esc(title)}</title><style>{css}</style></head><body><main>"
        f'<h1>{esc(title)}</h1><p class="sub">{subtitle}</p>{body}</main></body></html>\n'
    )


def write_page(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path.stat().st_size


def nice_step(top):
    return next(s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000) if top / s <= 6)


def bar_end(x, y, w, h, r=4):
    """Rect path, square on the left, rounded right end (data end)."""
    r = min(r, w, h / 2)
    return (f"M{x:g},{y:g}h{w - r:g}a{r:g},{r:g} 0 0 1 {r:g},{r:g}v{h - 2 * r:g}"
            f"a{r:g},{r:g} 0 0 1 {-r:g},{r:g}h{r - w:g}z")


# ---------- data ----------

def load_counts(con):
    counts = {}
    for route, band, n in con.execute(COUNT_SQL):
        if band not in BANDS or not route:
            raise ValueError(f"unexpected tag value route={route!r} trl_band={band!r}; fix the tags, do not guess")
        counts.setdefault(route, dict.fromkeys(BANDS, 0))[band] = n
    untagged = con.execute(UNTAGGED_SQL).fetchone()[0]
    return counts, untagged


def radar_counts():
    rows = list(csv.DictReader(open(MATRIX_CSV, encoding="utf-8")))
    missing = set(RADAR_DIMS) - {r["dimension"] for r in rows}
    bad = {r["status"] for r in rows} - {"reported", "derived", "not_reported_in_abstract", "no_source"}
    if missing or bad:
        raise ValueError(f"comparison_matrix.csv: missing dimensions {sorted(missing)}, "
                         f"unexpected status {sorted(bad)}; fix the matrix, do not guess")
    routes = sorted({r["tech_route"] for r in rows})
    per_dim = {d: len({r["tech_route"] for r in rows if r["dimension"] == d and r["status"] == "reported"})
               for d in RADAR_DIMS}
    return routes, per_dim


# ---------- chart ----------

def render(counts, routes_in_matrix, per_dim, qualifying):
    order = sorted(counts, key=lambda r: (-sum(counts[r].values()), r))
    totals = {r: sum(counts[r].values()) for r in order}
    top = max(totals.values())
    step = nice_step(top)
    xmax = -(-top // step) * step

    label_w, plot_w, right_pad, row_h, bar_h, top_pad, axis_h = 170, 500, 44, 32, 20, 8, 28
    width = label_w + plot_w + right_pad
    height = top_pad + row_h * len(order) + axis_h
    sx = plot_w / xmax
    base = top_pad + row_h * len(order)

    parts = []
    for v in range(0, xmax + 1, step):
        x = label_w + v * sx
        parts.append(f'<line x1="{x:g}" y1="{top_pad}" x2="{x:g}" y2="{base}" stroke="var(--grid)" stroke-width="1"/>')
        parts.append(f'<text class="tick" x="{x:g}" y="{base + 18}" text-anchor="middle">{v}</text>')
    for i, route in enumerate(order):
        y = top_pad + i * row_h + (row_h - bar_h) / 2
        parts.append(f'<text x="{label_w - 10}" y="{y + bar_h / 2 + 4:g}" text-anchor="end">{esc(route)}</text>')
        segs = [(b, counts[route][b]) for b in BANDS if counts[route][b]]
        x = label_w
        for j, (band, n) in enumerate(segs):
            w = n * sx
            last = j == len(segs) - 1
            draw_w = w if last else max(w - 2, 0.5)  # 2px surface gap between stacked segments
            shape = (f'<path d="{bar_end(round(x, 2), y, round(draw_w, 2), bar_h)}"' if last
                     else f'<rect x="{x:.2f}" y="{y:g}" width="{draw_w:.2f}" height="{bar_h}"')
            parts.append(f'{shape} class="mark" fill="var(--b-{band})">'
                         f"<title>{esc(route)}, {band}: {n} core papers</title></{'path' if last else 'rect'}>")
            x += w
        parts.append(f'<text x="{x + 6:.2f}" y="{y + bar_h / 2 + 4:g}">{totals[route]}</text>')
    parts.append(f'<line x1="{label_w}" y1="{top_pad}" x2="{label_w}" y2="{base}" stroke="var(--axis)" stroke-width="1"/>')
    svg = (f'<svg viewBox="0 0 {width} {height}" role="img" '
           f'aria-label="Core papers per tech route, stacked by TRL band">{"".join(parts)}</svg>')

    band_tot = {b: sum(counts[r][b] for r in order) for b in BANDS}
    legend = "".join(f'<span><span class="sw" style="background:var(--b-{b})"></span>{b} ({band_tot[b]})</span>'
                     for b in BANDS)
    head = "".join(f'<th class="n">{b}</th>' for b in BANDS)
    rows = "".join(
        f"<tr><td>{esc(r)}</td>" + "".join(f'<td class="n">{counts[r][b]}</td>' for b in BANDS)
        + f'<td class="n">{totals[r]}</td></tr>' for r in order)
    rows += ("<tr><th>total</th>" + "".join(f'<th class="n">{band_tot[b]}</th>' for b in BANDS)
             + f'<th class="n">{sum(totals.values())}</th></tr>')
    table = (f'<details><summary>Table view</summary><table><tr><th>tech route</th>{head}'
             f'<th class="n">total</th></tr>{rows}</table></details>')
    dims = ", ".join(f"{d} {n}" for d, n in per_dim.items())
    note = (f'<p class="note">No radar chart. {len(qualifying)} of {len(RADAR_DIMS)} numeric dimensions have status '
            f'"reported" for at least {RADAR_MIN_ROUTES} of the {len(routes_in_matrix)} matrix routes '
            f"(deliverables/comparison_matrix.csv), and a radar needs at least {RADAR_MIN_DIMS}. "
            f"Routes reported per dimension: {esc(dims)}.</p>")

    subtitle = (f"Core papers (core_set = 1, {sum(totals.values())} papers) per tech route, stacked by TRL "
                "(technology readiness level) band. Source: tags joined to papers in data/db/papers.sqlite, "
                "query in pipeline/tech_map.py.")
    body = (f'<div class="card"><div class="legend">{legend}</div><div class="chart">{svg}</div>'
            f'<div class="note" style="text-align:center">Core papers</div>{table}</div>{note}')
    return page("OCS tech map", esc(subtitle), body, {f"b-{b}": c for b, c in BAND_COLORS.items()})


# ---------- main ----------

def main():
    con = sqlite3.connect(DB_PATH)
    try:
        counts, untagged = load_counts(con)
    finally:
        con.close()
    routes_in_matrix, per_dim = radar_counts()
    qualifying = [d for d in RADAR_DIMS if per_dim[d] >= RADAR_MIN_ROUTES]
    draw_radar = len(qualifying) >= RADAR_MIN_DIMS

    print("== tech_map ==")
    print("SQL (counts plotted):")
    print(COUNT_SQL)
    print("SQL (core papers with no tags row, not plotted):")
    print(UNTAGGED_SQL)
    print("per route (sorted as plotted): " + " ".join(BANDS) + " total")
    order = sorted(counts, key=lambda r: (-sum(counts[r].values()), r))
    for r in order:
        print(f"  {r}: " + " ".join(str(counts[r][b]) for b in BANDS) + f" {sum(counts[r].values())}")
    for b in BANDS:
        print(f"per band {b}: {sum(c[b] for c in counts.values())}")
    print(f"routes plotted: {len(counts)}")
    print(f"total core papers plotted: {sum(sum(c.values()) for c in counts.values())}")
    print(f"core papers with no tags row (not plotted): {untagged}")

    print("== radar decision ==")
    print(f"source: deliverables/comparison_matrix.csv, {len(routes_in_matrix)} routes: {', '.join(routes_in_matrix)}")
    for d in RADAR_DIMS:
        ok = "qualifies" if per_dim[d] >= RADAR_MIN_ROUTES else "does not qualify"
        print(f"  {d}: reported for {per_dim[d]} of {len(routes_in_matrix)} routes, {ok}")
    print(f"qualifying dimensions: {len(qualifying)} of {len(RADAR_DIMS)} (need at least {RADAR_MIN_DIMS})")
    if draw_radar:
        # ponytail: no radar renderer, because the current matrix does not pass the gate (see the printed radar decision).
        # The matrix values are text ranges with mixed units, so a radar needs a scaling rule decided first.
        # Checked before the write so tech_map.html never gets the "No radar chart" note when the gate passes.
        raise SystemExit("decision: draw radar, but no radar renderer exists yet; stopping instead of skipping it")

    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    size = write_page(GRAPHS_DIR / "tech_map.html", render(counts, routes_in_matrix, per_dim, qualifying))
    (GRAPHS_DIR / "tech_radar.html").unlink(missing_ok=True)
    print("decision: no radar chart drawn (graphs/tech_radar.html not written)")
    print(f"wrote graphs/tech_map.html ({size} bytes)")


if __name__ == "__main__":
    main()
