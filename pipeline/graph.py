"""Stage 4 graphs. See PLAN.md stage 4, .claude/agents/grapher.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.graph

Reads the extended set (papers.extended_set = 1) from data/db/papers.sqlite:
papers, paper_authors, authors, institutions, tags. Builds a co-authorship
graph over authors (edge = co-authored an extended-set paper, weighted by
how many) and an institution graph collapsed from it (each author's main
institution is its most-frequent affiliation across its extended-set
papers), computes degree and betweenness centrality and greedy-modularity
communities on the author graph, and writes:

    graphs/coauthor.graphml
    graphs/institution.graphml
    graphs/coauthor.html       (self-contained inline-SVG force-directed plot)
    graphs/top_pis.csv
    graphs/top_institutions.csv
    graphs/clusters.csv

Safe to run twice: every output is fully rewritten each run from the
database; nothing is appended to except deliverables/pitfalls_original_log.md.

Exact SQL used to count core/extended papers per author. This is what
build_author_records() computes in Python from the same three tables; the
auditor (or sanity_check() below, which runs on every invocation) can rerun
it directly for any author_id to check a top_pis.csv row:

    SELECT pa.author_id,
           COUNT(DISTINCT CASE WHEN p.core_set = 1 THEN pa.paper_id END) AS core_papers,
           COUNT(DISTINCT pa.paper_id) AS extended_papers
    FROM paper_authors pa
    JOIN papers p ON pa.paper_id = p.paper_id
    WHERE p.extended_set = 1 AND pa.author_id = ?
    GROUP BY pa.author_id

Sanity check (first, middle, last row of the sorted top_pis.csv,
reproduced by the query above against the actual database, rerun 2026-09-26
after step 2's anchor-papers curation pass, extended_set still 420 papers,
top_pis.csv still 1827 rows):

    author_id=A5100669891 'Ming C. Wu'            -> core=24 extended=27  (row: core=24 extended=27)
    author_id=A5084039159 'Antonio M. O. Ribeiro'  -> core=1  extended=1   (row: core=1  extended=1)
    author_id=A5110102724 'Jonathan Turner'        -> core=0  extended=1   (row: core=0  extended=1)

All three match. sanity_check() below repeats this on every run and raises
AssertionError on a mismatch.
"""
import csv
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

import networkx as nx

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
GRAPHS_DIR = REPO_ROOT / "graphs"
PITFALLS_PATH = REPO_ROOT / "deliverables" / "pitfalls_original_log.md"

PAPER_COUNT_SQL = """
    SELECT pa.author_id,
           COUNT(DISTINCT CASE WHEN p.core_set = 1 THEN pa.paper_id END) AS core_papers,
           COUNT(DISTINCT pa.paper_id) AS extended_papers
    FROM paper_authors pa
    JOIN papers p ON pa.paper_id = p.paper_id
    WHERE p.extended_set = 1 AND pa.author_id = ?
    GROUP BY pa.author_id
"""

# Colors are a plain, distinct-enough palette; not a design deliverable.
TECH_ROUTE_COLORS = {
    "mems_3d": "#1f77b4",
    "mems_2d": "#17becf",
    "mems_silicon_photonic": "#2ca02c",
    "lcos": "#9467bd",
    "piezo": "#8c564b",
    "thermo_optic": "#ff7f0e",
    "electro_optic": "#d62728",
    "soa": "#e377c2",
    "robotic_patch_panel": "#bcbd22",
    "architecture_only": "#7f7f7f",
    "other": "#aec7e8",
    "unclear": "#c7c7c7",
    "none": "#c7c7c7",
}


def log_pitfall(msg):
    PITFALLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(PITFALLS_PATH, "a", encoding="utf-8") as f:
        f.write(f"- [{ts}] stage 4 grapher: {msg}\n")


def log_pitfall_once(msg, marker):
    """Like log_pitfall, but skipped if `marker` is already in the file, so a
    rerun of graph.py does not re-log the same static, always-true finding
    on every invocation."""
    PITFALLS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if PITFALLS_PATH.exists() and marker in PITFALLS_PATH.read_text(encoding="utf-8"):
        return
    log_pitfall(msg)


# ---------- load ----------

def load_data(con):
    con.row_factory = sqlite3.Row
    paper_core = {
        r["paper_id"]: bool(r["core_set"])
        for r in con.execute("SELECT paper_id, core_set FROM papers WHERE extended_set = 1")
    }
    author_names = {r["author_id"]: (r["display_name"], r["name_key"]) for r in con.execute("SELECT author_id, display_name, name_key FROM authors")}
    inst_names = {r["inst_id"]: r["display_name"] for r in con.execute("SELECT inst_id, display_name FROM institutions")}
    tags = {
        r["paper_id"]: {"tech_route": r["tech_route"], "adjacent_field": r["adjacent_field"]}
        for r in con.execute("SELECT paper_id, tech_route, adjacent_field FROM tags")
    }

    author_papers = defaultdict(list)  # author_id -> [(paper_id, inst_id), ...]
    paper_authors = defaultdict(list)  # paper_id -> [author_id, ...]
    rows = con.execute(
        """SELECT pa.paper_id, pa.author_id, pa.inst_id
           FROM paper_authors pa JOIN papers p ON pa.paper_id = p.paper_id
           WHERE p.extended_set = 1
           ORDER BY pa.paper_id, pa.position"""
    ).fetchall()
    for r in rows:
        author_papers[r["author_id"]].append((r["paper_id"], r["inst_id"]))
        paper_authors[r["paper_id"]].append(r["author_id"])

    return paper_core, author_papers, paper_authors, author_names, inst_names, tags


# ---------- author records ----------

def build_author_records(paper_core, author_papers, author_names, inst_names, tags):
    records = {}
    for author_id, plist in author_papers.items():
        paper_ids = sorted({pid for pid, _ in plist})
        core_ids = sorted(pid for pid in paper_ids if paper_core.get(pid))
        inst_counter = Counter(inst for _, inst in plist if inst)
        main_inst_id = None
        if inst_counter:
            top_count = max(inst_counter.values())
            main_inst_id = sorted(i for i, c in inst_counter.items() if c == top_count)[0]
        tech_routes = sorted({tags[pid]["tech_route"] for pid in core_ids if tags.get(pid, {}).get("tech_route")})
        adjacent_fields = sorted({tags[pid]["adjacent_field"] for pid in paper_ids if tags.get(pid, {}).get("adjacent_field")})
        display_name, name_key = author_names.get(author_id, (author_id, author_id))
        records[author_id] = {
            "display_name": display_name,
            "name_key": name_key,
            "main_inst_name": inst_names.get(main_inst_id, "unknown") if main_inst_id else "unknown",
            "core_paper_ids": core_ids,
            "extended_paper_ids": paper_ids,
            "core_count": len(core_ids),
            "extended_count": len(paper_ids),
            "tech_routes": tech_routes,
            "adjacent_fields": adjacent_fields,
            "sample_paper_ids": (core_ids or paper_ids)[:5],
        }
    return records


def log_split_person_candidates(records):
    """One person split into two author rows shows up as one name_key with
    more than one author_id, at least one of which has core papers."""
    by_name_key = defaultdict(list)
    for author_id, rec in records.items():
        by_name_key[rec["name_key"]].append(author_id)
    flagged = []
    for name_key, author_ids in sorted(by_name_key.items()):
        if len(author_ids) > 1 and any(records[a]["core_count"] > 0 for a in author_ids):
            flagged.append((name_key, author_ids))
    if flagged:
        sample = "; ".join(
            f"{nk} -> {[(a, records[a]['core_count']) for a in aids]}" for nk, aids in flagged[:5]
        )
        log_pitfall_once(
            f"{len(flagged)} name_key(s) map to more than one author_id in the "
            f"extended-set graph with at least one core paper, likely one person "
            f"split into multiple nodes (inherited from stage 2 no-OpenAlex-ID "
            f"author merge policy, not fixed here). Sample: {sample}",
            marker="split into multiple nodes (inherited from stage 2",
        )


def log_near_duplicate_institutions(top_institutions):
    """Institutions with the same normalized name (case/whitespace only) but
    different inst_id would show up as separate top-institution rows."""
    seen = defaultdict(list)
    for row in top_institutions[:50]:
        key = row["institution"].strip().lower()
        seen[key].append(row["institution"])
    dupes = {k: v for k, v in seen.items() if len(set(v)) > 1}
    if dupes:
        log_pitfall_once(
            f"near-duplicate institution display names among top 50: {dupes}",
            marker="near-duplicate institution display names among top 50",
        )


# ---------- graphs ----------

def build_author_graph(records, paper_authors):
    G = nx.Graph()
    for author_id, rec in records.items():
        G.add_node(
            author_id,
            display_name=rec["display_name"],
            institution=rec["main_inst_name"],
            core_paper_count=rec["core_count"],
            extended_paper_count=rec["extended_count"],
            tech_routes=";".join(rec["tech_routes"]),
            adjacent_field=";".join(rec["adjacent_fields"]),
        )
    for paper_id, authors in paper_authors.items():
        uniq = sorted(set(authors))
        for a, b in combinations(uniq, 2):
            if G.has_edge(a, b):
                G[a][b]["weight"] += 1
            else:
                G.add_edge(a, b, weight=1)
    return G


def build_institution_graph(G_author, records):
    """'unknown' (no affiliation) is not a real institution, so it gets no
    node and no edges here: an author with no affiliation would otherwise
    collapse into one pseudo-institution that tops the ranking on fake
    inter-institution bridges. The author-level 'unknown' label stays in
    coauthor.graphml and top_pis.csv, which is a different, correct use of
    the label (an author really has no known affiliation)."""
    H = nx.Graph()
    inst_members = defaultdict(list)
    for author_id, rec in records.items():
        inst = rec["main_inst_name"]
        if inst == "unknown":
            continue
        inst_members[inst].append(author_id)
    for inst_name, members in inst_members.items():
        core_papers = set()
        ext_papers = set()
        tech_routes = set()
        for m in members:
            core_papers.update(records[m]["core_paper_ids"])
            ext_papers.update(records[m]["extended_paper_ids"])
            tech_routes.update(records[m]["tech_routes"])
        H.add_node(
            inst_name,
            author_count=len(members),
            core_paper_count=len(core_papers),
            extended_paper_count=len(ext_papers),
            tech_routes=";".join(sorted(tech_routes)),
        )
    for a, b, data in G_author.edges(data=True):
        inst_a = records[a]["main_inst_name"]
        inst_b = records[b]["main_inst_name"]
        if inst_a == inst_b or inst_a == "unknown" or inst_b == "unknown":
            continue
        w = data.get("weight", 1)
        if H.has_edge(inst_a, inst_b):
            H[inst_a][inst_b]["weight"] += w
        else:
            H.add_edge(inst_a, inst_b, weight=w)
    return H


def dominant_tech_route(author_ids, records):
    counter = Counter()
    for a in author_ids:
        for tr in records[a]["tech_routes"]:
            counter[tr] += 1
    if not counter:
        return "none"
    top_count = max(counter.values())
    return sorted(r for r, c in counter.items() if c == top_count)[0]


# ---------- CSV writers ----------

def write_top_pis(records, degree, betweenness):
    entries = []
    for author_id, rec in records.items():
        entries.append((author_id, {
            "author_id": author_id,
            "author": rec["display_name"],
            "institution": rec["main_inst_name"],
            "core_paper_count": rec["core_count"],
            "extended_paper_count": rec["extended_count"],
            "degree": degree.get(author_id, 0),
            "betweenness": round(betweenness.get(author_id, 0.0), 6),
            "tech_routes": ";".join(rec["tech_routes"]),
            "adjacent_field": ";".join(rec["adjacent_fields"]),
            "sample_paper_ids": ";".join(rec["sample_paper_ids"]),
        }))
    entries.sort(key=lambda e: (-e[1]["core_paper_count"], -e[1]["degree"], e[0]))

    path = GRAPHS_DIR / "top_pis.csv"
    fieldnames = ["author_id", "author", "institution", "core_paper_count", "extended_paper_count",
                  "degree", "betweenness", "tech_routes", "adjacent_field", "sample_paper_ids"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for _, row in entries:
            w.writerow(row)
    return entries


def write_top_institutions(H, records):
    betweenness = nx.betweenness_centrality(H, weight=None) if H.number_of_nodes() > 1 else {}
    entries = []
    for inst_name, data in H.nodes(data=True):
        entries.append({
            "institution": inst_name,
            "author_count": data["author_count"],
            "core_paper_count": data["core_paper_count"],
            "extended_paper_count": data["extended_paper_count"],
            "degree": H.degree(inst_name),
            "betweenness": round(betweenness.get(inst_name, 0.0), 6),
            "tech_routes": data["tech_routes"],
        })
    entries.sort(key=lambda r: (-r["core_paper_count"], -r["degree"], r["institution"]))
    path = GRAPHS_DIR / "top_institutions.csv"
    fieldnames = ["institution", "author_count", "core_paper_count", "extended_paper_count",
                  "degree", "betweenness", "tech_routes"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(entries)
    return entries


def write_clusters(communities, records):
    rows = []
    for idx, members in enumerate(communities):
        members = sorted(members, key=lambda a: records[a]["display_name"])
        rows.append({
            "community_id": idx,
            "member_authors": ";".join(records[a]["display_name"] for a in members),
            # same order as member_authors, so position i in one list is
            # position i in the other -- resolves duplicate display names
            # (e.g. two people both named "Guohui Wang") without a join.
            "member_author_ids": ";".join(members),
            "dominant_tech_route": dominant_tech_route(members, records),
            "size": len(members),
        })
    rows.sort(key=lambda r: (-r["size"], r["community_id"]))
    path = GRAPHS_DIR / "clusters.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["community_id", "member_authors", "member_author_ids", "dominant_tech_route", "size"])
        w.writeheader()
        w.writerows(rows)
    return rows


# ---------- html plot ----------

def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def write_html(G, records, path):
    """Plain inline SVG, no plotly runtime. plotly.min.js is ~4.8 MB by
    itself, which leaves no room under the 5 MB cap for ~1.1 MB of node/edge
    data once inlined, and a <script src="plotly.min.js"> sibling file
    breaks the page if it is copied or opened alone. A static force-directed
    plot only needs positions, colors, and hover text, all of which plain
    SVG does natively (<title> = native browser tooltip, no JS needed), so
    this drops the plotly dependency for this file entirely. Coordinates are
    rounded to 1 decimal (canvas is a normalized 0-2000 unit square, so 1
    decimal is already sub-pixel) to keep the file small."""
    raw_pos = nx.spring_layout(G, seed=42, weight="weight")
    xs0 = [p[0] for p in raw_pos.values()]
    ys0 = [p[1] for p in raw_pos.values()]
    span = max(max(xs0) - min(xs0), max(ys0) - min(ys0)) or 1.0
    CANVAS = 2000
    pos = {
        n: (round((x - min(xs0)) / span * CANVAS, 1), round((y - min(ys0)) / span * CANVAS, 1))
        for n, (x, y) in raw_pos.items()
    }
    pad = 30
    xs = [p[0] for p in pos.values()]
    ys = [p[1] for p in pos.values()]
    minx, miny = min(xs) - pad, min(ys) - pad
    width = max(xs) + pad - minx
    height = max(ys) + pad - miny

    def X(v):
        return round(v - minx, 1)

    def Y(v):
        return round(v - miny, 1)

    edge_parts = []
    for a, b in G.edges():
        x0, y0 = pos[a]
        x1, y1 = pos[b]
        edge_parts.append(f"M{X(x0)},{Y(y0)}L{X(x1)},{Y(y1)}")
    edge_path = "".join(edge_parts)

    present = set()  # (category, hollow) actually used, for the legend
    node_parts = []
    for author_id, rec in records.items():
        category = rec["tech_routes"][0] if rec["tech_routes"] else "none"
        hollow = rec["core_count"] == 0
        present.add((category, hollow))
        x, y = pos[author_id]
        r = max(3, min(20, 3 + rec["core_count"] * 2))
        cls = f"h-{category}" if hollow else f"n-{category}"
        title = (
            f"{rec['display_name']} | {rec['main_inst_name']} | "
            f"core {rec['core_count']} ext {rec['extended_count']} | "
            f"routes: {';'.join(rec['tech_routes']) or 'none'}"
            + (f" | adjacent: {';'.join(rec['adjacent_fields'])}" if rec["adjacent_fields"] else "")
        )
        node_parts.append(
            f'<circle cx="{X(x)}" cy="{Y(y)}" r="{r}" class="{cls}">'
            f"<title>{_esc(title)}</title></circle>"
        )

    style_rules = []
    for category, color in TECH_ROUTE_COLORS.items():
        style_rules.append(f".n-{category}{{fill:{color}}}")
        style_rules.append(f".h-{category}{{fill:none;stroke:{color};stroke-width:1.5}}")

    legend_rows = []
    for category, hollow in sorted(present):
        color = TECH_ROUTE_COLORS.get(category, "#c7c7c7")
        label = _esc(category + (" (adjacent only)" if hollow else ""))
        swatch = (
            f"border:1.5px solid {color};background:none"
            if hollow else f"background:{color};border:1.5px solid {color}"
        )
        legend_rows.append(
            '<div style="white-space:nowrap"><span style="display:inline-block;'
            f'width:10px;height:10px;border-radius:50%;{swatch};margin-right:5px"></span>{label}</div>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        'width="100%" height="100%" preserveAspectRatio="xMidYMid meet">'
        f"<style>{''.join(style_rules)} circle:hover{{stroke:#000;stroke-width:1.5}}</style>"
        f'<path d="{edge_path}" fill="none" stroke="#999999" stroke-width="0.5" opacity="0.6"/>'
        f"{''.join(node_parts)}"
        "</svg>"
    )

    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>OCS co-authorship network (extended set)</title>"
        "<style>html,body{height:100%;margin:0;font-family:sans-serif}"
        "#legend{position:fixed;top:8px;left:8px;background:#fff;padding:6px 10px;"
        "border:1px solid #ccc;font-size:12px;max-height:90vh;overflow:auto;z-index:1}"
        "</style></head><body>"
        f'<div id="legend"><div style="font-weight:bold;margin-bottom:4px">tech route</div>'
        f"{''.join(legend_rows)}</div>"
        f'<div style="height:100%;width:100%">{svg}</div>'
        "</body></html>"
    )
    path.write_text(html, encoding="utf-8")


# ---------- sanity check ----------

def sanity_check(con, entries):
    """Picks the first, middle, and last row of the sorted top_pis.csv rows
    and reproduces their core/extended paper counts with PAPER_COUNT_SQL,
    independent of build_author_records(). Raises AssertionError on any
    mismatch."""
    if not entries:
        return []
    picks = [entries[0], entries[len(entries) // 2], entries[-1]]
    results = []
    for author_id, row in picks:
        # every author here came from an extended-set paper_authors row, so
        # the GROUP BY always returns exactly one row.
        _, core, ext = con.execute(PAPER_COUNT_SQL, (author_id,)).fetchone()
        assert core == row["core_paper_count"], (author_id, "core", core, row["core_paper_count"])
        assert ext == row["extended_paper_count"], (author_id, "extended", ext, row["extended_paper_count"])
        results.append((author_id, row["author"], core, ext))
    return results


# ---------- main ----------

def main():
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    stale_plotly_js = GRAPHS_DIR / "plotly.min.js"
    if stale_plotly_js.exists():
        stale_plotly_js.unlink()
    log_pitfall_once(
        "retry fix: coauthor.html's earlier include_plotlyjs='directory' "
        "version loaded a sibling graphs/plotly.min.js (4.8 MB) via "
        "<script src>, so the page broke when copied without that file, "
        "and inlining the full plotly bundle plus the page's own ~1.1 MB "
        "of node/edge data would not fit under 5 MB either. Dropped the "
        "plotly runtime for this file: write_html() now emits plain inline "
        "SVG (native <title> tooltips instead of plotly hover, coordinates "
        "rounded to 1 decimal), self-contained and a few hundred KB. Also "
        "fixed build_institution_graph() to give 'unknown' (no affiliation) "
        "no node and no edges, since 301 such authors were collapsing into "
        "one pseudo-institution that topped top_institutions.csv on fake "
        "inter-institution bridges (betweenness 0.28 vs 0.098 for the real "
        "next institution). Author-level 'unknown' in coauthor.graphml and "
        "top_pis.csv is unchanged, that one is correct. Also added an "
        "author_id column to top_pis.csv and a member_author_ids column to "
        "clusters.csv (same order as member_authors) so the 76 duplicate "
        "display_names, e.g. two 'Guohui Wang' rows, resolve without a "
        "name+sample_paper_ids join.",
        marker="retry fix: coauthor.html's earlier include_plotlyjs='directory'",
    )
    con = sqlite3.connect(DB_PATH)
    try:
        paper_core, author_papers, paper_authors, author_names, inst_names, tags = load_data(con)
        records = build_author_records(paper_core, author_papers, author_names, inst_names, tags)
        log_split_person_candidates(records)

        G_author = build_author_graph(records, paper_authors)
        degree = dict(G_author.degree())
        betweenness = nx.betweenness_centrality(G_author, weight=None)
        communities = list(nx.algorithms.community.greedy_modularity_communities(G_author, weight="weight"))

        H_inst = build_institution_graph(G_author, records)

        nx.write_graphml(G_author, GRAPHS_DIR / "coauthor.graphml")
        nx.write_graphml(H_inst, GRAPHS_DIR / "institution.graphml")

        pi_entries = write_top_pis(records, degree, betweenness)
        inst_rows = write_top_institutions(H_inst, records)
        log_near_duplicate_institutions(inst_rows)
        cluster_rows = write_clusters(communities, records)

        write_html(G_author, records, GRAPHS_DIR / "coauthor.html")

        sanity_check(con, pi_entries)

        html_mb = (GRAPHS_DIR / "coauthor.html").stat().st_size / 1_000_000
        print(
            f"coauthor graph: {G_author.number_of_nodes()} nodes, {G_author.number_of_edges()} edges\n"
            f"institution graph: {H_inst.number_of_nodes()} nodes, {H_inst.number_of_edges()} edges\n"
            f"communities: {len(communities)}\n"
            f"top_pis.csv rows: {len(pi_entries)}\n"
            f"coauthor.html: {html_mb:.2f} MB"
        )
    finally:
        con.close()


if __name__ == "__main__":
    main()
