"""Stage 6 export. See PLAN.md stage 6, .claude/agents/analyst.md.

Usage (from repo root):
    .venv/bin/python -m pipeline.matrix_export

Writes one file per tech route, data/work/route_<name>.json, with every core
paper (papers.core_set = 1) whose tags.tech_route is that route
(match = "primary"), plus core papers that carry it only as
tags.tech_route_secondary (match = "secondary"). Each entry has paper_id,
title, year, venue, abstract, match, and the paper's tags row.

Safe to run twice: every route file is fully rewritten from the database.
"""
import json
import sqlite3
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "data" / "db" / "papers.sqlite"
WORK_DIR = REPO_ROOT / "data" / "work"

TAG_FIELDS = ["tech_route", "tech_route_secondary", "integration", "trl_band",
              "ai_dc_fit", "adjacent_field", "evidence_span", "confidence"]

QUERY = f"""
SELECT p.paper_id, p.title, p.year, p.venue, p.abstract, p.cited_by_count,
       {", ".join("t." + f for f in TAG_FIELDS)}
FROM papers p JOIN tags t ON t.paper_id = p.paper_id
WHERE p.core_set = 1
ORDER BY p.year, p.paper_id
"""


def main():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = [dict(r) for r in con.execute(QUERY)]
    con.close()

    routes = defaultdict(list)
    for r in rows:
        entry = {k: r[k] for k in ("paper_id", "title", "year", "venue", "abstract", "cited_by_count")}
        entry["tags"] = {f: r[f] for f in TAG_FIELDS}
        if r["tech_route"]:
            routes[r["tech_route"]].append({**entry, "match": "primary"})
        sec = r["tech_route_secondary"]
        if sec and sec != r["tech_route"]:
            routes[sec].append({**entry, "match": "secondary"})

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    for route, papers in sorted(routes.items()):
        path = WORK_DIR / f"route_{route}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        n_prim = sum(p["match"] == "primary" for p in papers)
        print(f"{path.relative_to(REPO_ROOT).as_posix()} primary={n_prim} secondary={len(papers) - n_prim}")


if __name__ == "__main__":
    main()
