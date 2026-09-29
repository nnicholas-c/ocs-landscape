"""Build status/index.html from status/template.html and the repo's data files.

Run from the repo root: .venv/bin/python status/build.py
"""
import csv
import json
import os
import sys
from urllib.parse import urlparse

SCOUT_DAY = "2026-09-26"  # undated project pages carry the day the scout fetched them

here = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "index.html")

matrix = [{"r": r["tech_route"], "d": r["dimension"], "s": r["status"], "v": r["value"], "u": r["unit"],
           "c": r["confidence"], "n": len([p for p in r["paper_ids"].split(";") if p.strip()]),
           "p": r["project_rows"].strip()}
          for r in csv.DictReader(open("deliverables/comparison_matrix.csv", encoding="utf-8"))]
pis = sorted(csv.DictReader(open("graphs/top_pis.csv", encoding="utf-8")), key=lambda r: -int(r["core_paper_count"]))[:10]
pis = [{"name": r["author"], "inst": r["institution"], "core": int(r["core_paper_count"])} for r in pis]
projects = [{"entity": r["entity"], "product": r["product_or_project"], "route": r["tech_route"], "stage": r["stage"],
             "url": r["evidence_url"], "host": urlparse(r["evidence_url"]).netloc.removeprefix("www."),
             "date": r["evidence_date"], "fetched": r["evidence_date"] == SCOUT_DAY}
            for r in csv.DictReader(open("data/projects.csv", encoding="utf-8"))]

assert len(matrix) == 126 and len(projects) == 12
assert sum(m["s"] == "reported" and not m["n"] and bool(m["p"]) for m in matrix) == 7  # company-page cells

page = open(os.path.join(here, "template.html"), encoding="utf-8").read()
for key, value in (("MATRIX", matrix), ("PIS", pis), ("PROJECTS", projects)):
    page = page.replace(f"/*{key}_JSON*/", json.dumps(value, ensure_ascii=False).replace("</", r"<\/"))
assert "_JSON*/" not in page
open(out, "w", encoding="utf-8", newline="\n").write(page)
print(f"wrote {out}, {len(page)} bytes")
