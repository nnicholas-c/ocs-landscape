# Run plan

The orchestrator works through these stages in order. Each stage names the subagent that runs it, what it reads, what it writes, and when it counts as done. Some stages have a gate, which is a check with a number attached. A gate that fails sends the run back to the named stage once. A second failure stops the run.

Parallelism. Stage 0 and stage 1a each launch two collectors at once, one per source. Stage 1b can launch up to three taggers at once on different batches. Stage 5 runs alongside stages 3 and 4. Everything else runs in order.

Before stage 0, the orchestrator confirms that .venv exists, that `.venv/bin/python -c "import pyalex, arxiv, pandas, rapidfuzz, networkx, plotly, yaml"` succeeds, and that .env has OPENALEX_API_KEY set to something other than the placeholder. If not, it stops and tells the user how to get the key (README step 3) rather than trying to run keyless. It then checks the key by calling https://api.openalex.org/rate-limit?api_key=<key> and logs daily_remaining_usd to STATUS.md.

---

## Stage 0. Smoke test

Runs. collector, twice in parallel, once with source=openalex and once with source=arxiv, in mode=smoke.

Reads. pipeline/queries.yaml (only the first query of the source), the openalex-arxiv-playbook skill.

Writes. pipeline/collect_openalex.py and pipeline/collect_arxiv.py (the collector writes these scripts), data/raw/smoke_openalex.jsonl and data/raw/smoke_arxiv.jsonl with 5 records each.

Done when. Both files exist, every record has every field in the playbook's record shape, the abstract field is readable prose (not an inverted index, not empty for all five), the OpenAlex collector reports the cost_usd of its calls from the response meta, and the collector's summary says so.

---

## Stage 1. Collection

### 1a. Full pull

Runs. collector, twice in parallel, mode=full.

Reads. All queries for its source in pipeline/queries.yaml, plus the anchors list.

Writes. data/raw/openalex.jsonl and data/raw/arxiv.jsonl. For each anchor title, the collector searches by title and appends the match if found. Misses go to pitfalls.

Done when. The two files together hold between 300 and 800 records (duplicates across sources are expected and fine at this stage) and each collector reports how many records each query returned and, for OpenAlex, the total cost_usd.

### 1b. Relevance scoring

Runs. tagger, in mode=relevance. The orchestrator first runs `.venv/bin/python -m pipeline.tag_export --mode relevance` which the tagger writes on its first invocation if it does not exist. It dumps title, year, venue, and the first 120 words of each abstract into data/work/relevance_batch_NNN.json, 25 records per batch. Launch one tagger per 4 batches (about 100 records), up to three taggers at once.

Writes. data/work/relevance_batch_NNN.out.json per batch, then `.venv/bin/python -m pipeline.tag_import --mode relevance` merges them into data/raw/relevance.csv with columns record_key, source, score, adjacent_field, reason.

Done when. Every record in the raw files has a row in relevance.csv.

### 1c. Snowball

Runs. collector, source=openalex, mode=snowball.

Reads. relevance.csv. Takes the 10 records with score 3 and the highest cited_by_count.

Writes. data/raw/openalex_snowball.jsonl with the referenced works and the citing works of those 10 papers, capped at 150 new records. Then 1b runs again on the new records only, appending to relevance.csv.

Gate A. Count the records with score 2 or 3 across all raw files, before dedup. Between 60 and 200 passes. Below 60, the orchestrator asks the collector to add the phrases listed under "if recall is low" in the ocs-domain skill, reruns 1a and 1b once, and logs it. Above 200, keep score 3 only as the core set, say so in STATUS.md, and pass.

---

## Stage 2. Curation

Runs. curator.

Reads. Every file in data/raw/*.jsonl, data/raw/relevance.csv, pipeline/schema.sql, the openalex-arxiv-playbook skill (dedup rules section).

Writes. pipeline/curate.py, data/db/papers.sqlite with every table in schema.sql, and deliverables/curation_report.md. The report states how many duplicates were found by DOI, by arXiv ID, and by fuzzy title, how many author records were merged, how many institution records were merged, and lists ten fuzzy-title matches so a human can eyeball whether the threshold is right.

Done when. The papers table has core_set = 1 for records with score 2 or 3 (or score 3 only if Gate A said so), extended_set = 1 for core papers plus score 1 papers that carry an adjacent_field, every core paper has a title, a year, and at least one author, and a count query run by the orchestrator matches the numbers in curation_report.md.

---

## Stage 3. Tagging

Runs. tagger, mode=full. Export with `.venv/bin/python -m pipeline.tag_export --mode full`, which dumps every extended-set paper with its full abstract into data/work/tag_batch_NNN.json, 20 papers per batch. One tagger per 3 batches, up to two taggers at once.

Writes. data/work/tag_batch_NNN.out.json per batch, then `.venv/bin/python -m pipeline.tag_import --mode full` loads them into the tags table. The import script checks that every evidence_span is a verbatim substring of the paper's abstract and writes a list of failures to data/work/tag_failures.json.

Gate B. Every core paper has a tech_route and a trl, and at least 90 percent of evidence spans pass the substring check. Below 90 percent, retag only the failed papers once, then re-import. The failure count goes in STATUS.md either way.

---

## Stage 4. Graphs

Runs. grapher.

Reads. data/db/papers.sqlite (extended set, authors, institutions, tags).

Writes. pipeline/graph.py, graphs/coauthor.graphml, graphs/institution.graphml, graphs/coauthor.html (a force-directed plot with nodes colored by tech route and adjacent-field nodes drawn hollow), graphs/top_pis.csv (author, institution, core paper count, extended paper count, degree, betweenness, tech routes, adjacent field, sample paper IDs), graphs/top_institutions.csv, and graphs/clusters.csv (community id, member authors, dominant tech route, size).

Done when. All files exist, top_pis.csv has at least 20 rows, and every row's paper count can be reproduced by a query the grapher records at the top of graph.py.

---

## Stage 5. Scout (runs alongside 3 and 4)

Runs. scout.

Reads. The seed entity list and the search phrases in the ocs-domain skill, plus graphs/top_institutions.csv if it exists yet.

Writes. data/projects.csv with columns entity, entity_type (hyperscaler_internal, established_vendor, startup, university_spinout, other), product_or_project, tech_route, stage (concept, prototype, pilot, shipping, unknown), first_public_date, evidence_url, evidence_date, evidence_quote (under 25 words, copied exactly), note.

Cap. 15 entities and 60 minutes of wall-clock, whichever comes first. Then stop and write what you have.

Done when. The file exists with at least 8 rows and every row has an evidence_url and an evidence_quote.

---

## Stage 6. Comparison matrix

Runs. analyst.

Reads. data/db/papers.sqlite (core set with tags and abstracts), data/projects.csv, the comparison-framework skill. The analyst writes pipeline/matrix_export.py, which dumps one JSON file per tech route with that route's papers (title, year, abstract, paper_id, tags) into data/work/route_<name>.json.

Writes. deliverables/comparison_matrix.csv in the long format defined by the skill, deliverables/comparison_matrix.md rendered from the CSV by a script (pipeline/matrix_render.py), and deliverables/reading_list.md naming the ten papers a human should read in full to fill the cells that abstracts could not, with one line each on why.

Done when. Every tech route in the taxonomy has a row for every dimension, even when the value is "not reported in abstract", every cell with a value lists at least one paper_id or project row, and the markdown file was produced by the render script rather than by hand.

---

## Stage 7. Audit gate

Runs. auditor.

Reads. Everything produced so far. The auditor writes pipeline/audit.py and only that script plus the report. Run it as `.venv/bin/python -m pipeline.audit --seed <new seed>` (add `--round 2` for a second round and `--merge` after the judgments are written). Every audit uses a new seed, and the script refuses to overwrite an earlier audit's files.

Checks.
(a) Pick 20 random core papers, re-fetch each from its source API, and compare title, year, cited_by_count, and the first author's first institution against the database.
(b) Pick 20 random matrix cells that have a value. Confirm every cited paper_id exists in the database and that the paper's abstract actually supports the value.
(c) Pick 10 random rows of projects.csv. Fetch each evidence_url and confirm the page mentions the entity and contains the evidence_quote.
(d) Rerun the evidence-span substring check across every row of the tags table.

Writes. deliverables/validation_report.md with, for each check, the sample drawn, the raw pass and fail counts, the rate, and the failing items listed by ID.

Gate C. (a) at most 10 percent mismatches, counting a cited_by_count difference of more than 10 percent as a mismatch. (b) at most 10 percent unsupported cells. (c) at most 20 percent failures. (d) at least 90 percent. Any check failing sends the run back to the stage that produced the data (2 for a, 6 for b, 5 for c, 3 for d) with the auditor's failing list attached, once. Then stage 7 runs again. A second failure stops the run and STATUS.md records which check failed and the numbers.

---

## Stage 8. Write-up

Runs. writer.

Reads. deliverables/*.md, deliverables/comparison_matrix.csv, graphs/*.csv, data/projects.csv, STATUS.md, the report-format skill, and .claude/agents/*.md (to describe the architecture accurately).

Writes.
- deliverables/architecture.md (the agent roster, the data flow, the gates, a mermaid diagram, and what would change to add IEEE Xplore, patents, or company data)
- deliverables/framework.md (the tagging rubric, the matrix dimensions, the adjacent-field logic)
- deliverables/demo_results.md (counts, top PIs and institutions, cluster summary, the matrix, the project list, and links to the graphs)
- deliverables/pitfalls.md (the running log, cleaned up and grouped by source and by stage, with what was done about each)
- deliverables/open_questions.md (scope of OCS, whether to add OFC, SIGCOMM and NSDI, whether APEC, ECCE and PCIM belong at all, what needs a human reader)
- deliverables/meeting_summary.md (one page, what was tried, what worked, what did not, what to decide next week)

Done when. All six files exist, and every number in demo_results.md is followed by the file or query it came from.

---

## Finish

The orchestrator ticks the last box in STATUS.md, appends a final log line with the total wall-clock time and the number of subagent invocations if it can tell, and lists the six deliverable paths in its last message.
