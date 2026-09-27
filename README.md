# OCS landscape

English | [简体中文](README.zh-CN.md)

An agent-driven pipeline that maps optical circuit switching (OCS) for AI data centers from open bibliographic sources. Python scripts do the deterministic steps, role agents make the judgement calls, and every judgement is saved with its evidence (a quote, paper IDs, or a URL) so that it can be checked. The pipeline builds three maps.

1. **Technologies.** The switching routes and how they compare on switching time, loss, port count, maturity, and fit for AI (artificial intelligence) clusters. The routes are 3D MEMS (micro-electro-mechanical systems), 2D MEMS, silicon photonic MEMS, LCoS (liquid crystal on silicon), piezo, thermo-optic, electro-optic, SOA (semiconductor optical amplifier), and robotic patch panels.
2. **Teams.** The research groups that work on OCS, and the groups in adjacent fields whose skills transfer to it. Those fields are telecom cross-connects, micromirrors, silicon photonics, LCoS displays, free-space packaging, and data center networking.
3. **Projects.** Startups, established vendors, and hyperscaler projects, each backed by a public web address (URL) and a verbatim quote.

This repository holds a week-one, small-sample trial. Its purpose is to show that the pipeline works end to end and that its output can be checked. It is not yet a finished landscape report.

## Status

| Milestone | State | Where |
|---|---|---|
| Run 1. A full pass of stages 0 to 8 with three gates | Done | tag `run1` |
| Audit fix. The matrix build is separated from its audit, stages 6 and 7 were rerun with a new seed, and three questioned numbers were checked in `deliverables/number_checks.md` | Done | tag `run1-fixed` |
| Step 1, run 2. arXiv papers collected through OpenAlex's arXiv index and carried through stages 1b to 8, reusing run 1's scout output for stage 5 | Done | [pull request #1](https://github.com/nnicholas-c/ocs-landscape/pull/1) |
| Step 2, anchor papers. The anchor papers the title search missed were looked up by DOI (digital object identifier), and stages 1b to 4 and 6 to 8 were rerun with audit seed 20260929 | Done | [pull request #4](https://github.com/nnicholas-c/ocs-landscape/pull/4) |
| Step 3, technology map and project timeline. Two web pages in `graphs/` and a taxonomy tree in `deliverables/framework.md` | Done | [pull request #6](https://github.com/nnicholas-c/ocs-landscape/pull/6) |
| Step 4, number checks. The three questioned numbers rechecked on run 2's data | Done | [pull request #7](https://github.com/nnicholas-c/ocs-landscape/pull/7) |

Steps 1 to 4 are the follow-up tasks after run 1, and each was merged as one pull request. They are not pipeline stages. A stage is one of the nine stages (0 to 8) that `PLAN.md` defines, and one step can rerun several stages.

All four pull requests are merged into `master`, which is the version to present. The one-page summary is `deliverables/meeting_summary.md`, and `deliverables/demo_results.md` compares run 1 with run 2.

## Scope of the trial

- **Sources.** OpenAlex and arXiv only (`CLAUDE.md`, rule 6). Since run 2, new arXiv content comes through OpenAlex's index of arXiv. The reason is that arXiv's own API (application programming interface) answered every request in a probe from the machine this trial ran on with HTTP (Hypertext Transfer Protocol) status 406 (`deliverables/pitfalls_original_log.md`, 15:54; `STATUS.md`, 16:50 line). That evidence covers only that machine. The 47 records run 1 pulled through that API are still in `data/raw/arxiv.jsonl` (`deliverables/curation_report.md`, Raw records). IEEE Xplore, PCIM (a power electronics conference), Crossref, patents, and paid company data are out of scope on purpose. `deliverables/architecture.md` records what adding IEEE Xplore, PCIM, patents, or company data would take.
- **Size.** The trial aimed for 50 to 100 core papers (`CLAUDE.md`). Above 200 relevant records, Gate A keeps only score 3 records (`PLAN.md`), which gave 284 core papers after deduplication in run 2, up from 267 in run 1 (`deliverables/curation_report.md`). Whether to accept that is one of the open decisions.
- **Cost.** OpenAlex requires a free API key and meters usage, with about 1 USD (US dollar) a day free (`CLAUDE.md`, Environment). Run 1 cost 0.04 USD (`STATUS.md`, 16:14 note). Run 2's ten new searches cost 0.01 USD, but its total was not captured (`deliverables/demo_results.md`, Run 1 versus run 2).

## How it works

The pipeline has nine stages. Each stage is run by the role agent or agents that `PLAN.md` names, and each stage writes its output to disk, so a run can stop and resume from `STATUS.md`. The work is split in two.

- **Deterministic work** is plain Python in `pipeline/`. This covers API collection, deduplication, loading the database, graph building, rendering, and audit sampling. The scripts are safe to run twice.
- **Judgement work** is done by role agents. This covers relevance scoring, tagging, matrix cell decisions, web scouting, and judging category cells. Each agent follows its role file in `.claude/agents/`, the shared rulebook `CLAUDE.md`, and the one or two domain skills its role file lists. Agents hand work back through files, as listed under "Running the judgement stages".

| Stage | Role | Main output |
|---|---|---|
| 0 Smoke test | collector | 5 records per source, record shape validated |
| 1 Collection, relevance scoring, snowball, Gate A | collector, tagger | `data/raw/*.jsonl`, `data/raw/relevance.csv` |
| 2 Curation and deduplication | curator | `data/db/papers.sqlite`, `deliverables/curation_report.md` |
| 3 Tagging, Gate B | tagger | `tags` table |
| 4 Co-author and institution graphs | grapher | `graphs/` |
| 5 Company and project scout | scout | `data/projects.csv` |
| 6 Comparison matrix | analyst | `deliverables/comparison_matrix.csv` and `.md`, `deliverables/reading_list.md` |
| 7 Audit, Gate C | auditor | `deliverables/validation_report.md` |
| 8 Write-up | writer | the six meeting deliverables |

**Gates.** A gate that fails sends the run back to the stage that produced the data once, and a second failure stops the run.

- **Gate A.** Between 60 and 200 records score 2 or 3 for relevance. Above 200, only score 3 papers form the core set.
- **Gate B.** Every core paper is tagged, and at least 90 percent of evidence sentences are verbatim substrings of their abstracts.
- **Gate C.** Re-fetch mismatches are at most 10 percent, unsupported matrix cells at most 10 percent, and project evidence failures at most 20 percent. Verbatim evidence passes at least 90 percent.

**Second judge.** In the runs so far, an orchestration layer drove the stages, and a separate second-judge agent re-ran each stage's checks with code before the stage counted as done, so no stage graded its own work. The orchestration layer and the second judge's instructions are not in this repository yet, so a run started from `CLAUDE.md` and `PLAN.md` alone has no second judge. Adding it is on the to-do list.

**Rules every agent follows.**

- A number comes from code or from a quoted source sentence, never from memory.
- Every claim carries its provenance, as a paper ID, a CSV row, or a URL with a date.
- A gap stays visibly empty ("not reported in abstract") instead of being filled with a guess.
- The data contract is `pipeline/schema.sql`.

## Domain skills

| Skill | Contents |
|---|---|
| `ocs-domain` | Tech route taxonomy, TRL (technology readiness) bands, AI-fit values, the relevance rubric, adjacent fields, and the scout's seed entities |
| `openalex-arxiv-playbook` | API usage, the raw record shape, dedup and merge rules, and known API failure modes |
| `comparison-framework` | Matrix dimensions, the long-format CSV, and the rules for filling a cell |
| `report-format` | Deliverable templates, length limits, and style rules |

## Setup

Requires Python 3.11 or newer (tested with 3.14).

1. Create the environment with `python -m venv .venv`.
2. Install the packages with `.venv/bin/pip install -r requirements.txt` (on Windows, `.venv\Scripts\pip`).
3. Get a free OpenAlex key at https://openalex.org/settings/api, run `cp .env.example .env`, and set `OPENALEX_API_KEY`. The key is required, and `collect_openalex`, `collect_arxiv_via_openalex`, and `audit` stop if it is unset, because they are the only scripts that call OpenAlex. `collect_arxiv`, which calls arXiv's own API, needs no key.

On Windows the interpreter is `.venv\Scripts\python.exe`, and the console's default code page crashes on non-ASCII titles. In Git Bash, create `.venv/bin/python` with the lines below and run `chmod +x .venv/bin/python`. In PowerShell, set `$env:PYTHONUTF8=1` and call `.venv\Scripts\python -m pipeline.<module>`.

```sh
#!/bin/sh
PYTHONUTF8=1 exec "$(dirname "$0")/../Scripts/python.exe" "$@"
```

## Running the deterministic steps

Run each module from the repo root as `.venv/bin/python -m pipeline.<module>`. Modules with flags print them with `--help`. The others take no flags and ignore `--help`, so adding it runs them.

| Module | Purpose |
|---|---|
| `collect_openalex` | Pull OpenAlex records into `data/raw/` (`--mode smoke`, `full`, or `snowball`, plus a required `--out <file>.jsonl`). Needs the OpenAlex key |
| `collect_arxiv` | Pull arXiv records through arXiv's API (`--mode smoke` or `full`, plus `--out`) |
| `collect_arxiv_via_openalex` | Pull arXiv-hosted papers through OpenAlex's arXiv index (`--out`, default `data/raw/arxiv_via_openalex.jsonl`). Needs the OpenAlex key. Run 2 uses this instead of `collect_arxiv` |
| `tag_export`, `tag_import` | Write batch files for the tagger and import its labels (`--mode relevance` or `full`). `tag_export --mode full --only <file>` retags the paper IDs listed one per line in that file |
| `curate` | Deduplicate by DOI, then arXiv ID, then fuzzy title, and load `papers.sqlite` |
| `graph` | Build the co-author and institution graphs, the rankings, and `coauthor.html` |
| `matrix_export`, `matrix_build`, `matrix_render` | Export route files, build the matrix CSV from the analyst's recorded cell decisions, and render the markdown |
| `tech_map`, `project_timeline` | Write `graphs/tech_map.html` and `graphs/project_timeline.html` |
| `audit` | Run Gate C checks (a) to (d) with a fixed seed. Needs the OpenAlex key and network access. `--merge` combines the pre-judgement results with the auditor's judgments |
| `check_route_provenance`, `check_name_keys`, `merge_name_keys` | The number checks behind `deliverables/number_checks.md` |
| `test_curate`, `test_tag_pipeline`, `test_matrix_build` | Regression checks |

To rebuild the outputs from committed data, run `curate`, `graph`, `matrix_export`, `matrix_build`, `matrix_render`, `tech_map`, and `project_timeline` in that order. The number checks and the three tests also run from committed files. The number checks need the flags below to reproduce run 2's files in `data/work/`. Without them, `check_route_provenance` and `check_name_keys` stop because `--out` is required (and `check_name_keys` would use run 1's seed if only `--out` were given), and `merge_name_keys` reads and writes run 1's files by default (each script's argparse options).

```sh
.venv/bin/python -m pipeline.check_route_provenance --out data/work/nc1_run2_route_provenance.json
.venv/bin/python -m pipeline.check_name_keys --seed 20260930 --out data/work/nc2_run2_evidence.json
.venv/bin/python -m pipeline.merge_name_keys --evidence data/work/nc2_run2_evidence.json --class-a data/work/nc2_run2_class_A.json --class-b data/work/nc2_run2_class_B.json --out data/work/nc2_run2_name_keys.md
```

Until [issue #5](https://github.com/nnicholas-c/ocs-landscape/issues/5) is fixed, `graph` can write the members of `graphs/clusters.csv` in a different order on each run.

`matrix_build.py` imports nothing from `audit.py`. In the audit fix, the analyst rebuilt the matrix before `audit.py` was rewritten, so it never saw the new test. No rule enforces this yet.

## Running the judgement stages

Scripts cannot run these stages. They need an agent host that reads `CLAUDE.md` as standing instructions, can launch the role files in `.claude/agents/` as subagents with the skills in `.claude/skills/`, and gives the scout web search and fetch. To run or resume, open a session in the repo root and ask it to follow `PLAN.md` from the first unticked stage in `STATUS.md`.

| Role | Hands back | Read by |
|---|---|---|
| tagger | `data/work/relevance_batch_NNN.out.json`, `data/work/tag_batch_NNN.out.json` | `tag_import --mode relevance`, `tag_import --mode full` |
| scout | `data/projects.csv` | `matrix_build`, `audit` |
| analyst | `data/work/matrix_cells.yaml` | `matrix_build` |
| auditor | `data/work/<prefix>judgments.json`, for example `data/work/audit_s20260929_judgments.json` | `audit --merge` |
| writer | the six files in `deliverables/` | readers |

## Results so far

The figures below are run 2's, as rerun in step 2, and are on `master`. Run 1's figures sit beside them in `deliverables/demo_results.md` (Run 1 versus run 2).

| Measure | Value | Source |
|---|---|---|
| Unique raw records to papers | 1245 to 1211 | `deliverables/curation_report.md` |
| Core set and extended set | 284 and 420 | `deliverables/curation_report.md` |
| Authors in the team map | 1827, in 159 communities | `graphs/top_pis.csv`, `graphs/clusters.csv` |
| Institutions in the institution graph | 260 | `graphs/top_institutions.csv` |
| Company and project rows | 12, each with a URL and a quote | `data/projects.csv` |
| Matrix cells | 126, of which 80 reported, 9 derived, 33 not reported, 4 with no source | `deliverables/comparison_matrix.csv` |
| Gate C, run 2 audit after the anchor papers (seed 20260929) | Passed on the first round. 0 percent mismatches (0 of 20), 0 percent unsupported (0 of 20), 0 percent project failures (0 of 10), 100 percent verbatim (420 of 420) | `deliverables/validation_report.md`, Run 2 audit after the anchor papers |
| Category cell census, not gated | 3 of 27 unsupported by the auditor, 0 of 27 by the blind second judge | `deliverables/validation_report.md`, same section; `STATUS.md`, 21:21 line |
| Largest device route | Silicon photonic MEMS, 43 core papers, 6 of them only through the snowball | `deliverables/number_checks.md`, Run 2, section 1 |
| Network designs that build no switch (architecture_only) | 105 of 284 core papers | `deliverables/number_checks.md`, Run 2, section 1 |
| Split authors, fresh sample of 15 flagged name keys | 6 were one person (40 percent, 95 percent interval 20 to 64), about 59 of 147 keys | `deliverables/number_checks.md`, Run 2, section 2 |
| Core papers with no OpenAlex ID and no citation count | 31 of 284 | `deliverables/number_checks.md`, Run 2, section 3 |

**Maps.** Clone the repository and open these pages in a browser. GitHub shows only their HTML source.

- [`graphs/tech_map.html`](graphs/tech_map.html) shows the 284 core papers by tech route, stacked by TRL band, and 236 of them are tagged lab (`data/work/step3_counts.txt`). No radar chart was drawn. A radar dimension counts when it is reported for 5 or more of the 9 device routes, a radar needs at least 4 of its 6 dimensions to count, and only 3 do (`data/work/step3_counts.txt`; `pipeline/tech_map.py`, lines 41 to 44).
- [`graphs/project_timeline.html`](graphs/project_timeline.html) plots the 4 of 12 projects with a known first public date, colored by stage. The other 8 are listed under the chart without a guessed date (`data/work/step3_counts.txt`).
- [`graphs/coauthor.html`](graphs/coauthor.html) is the co-author network behind the team map.
- The taxonomy tree of tech routes is a diagram in `deliverables/framework.md`.

**Naming.** Rounds 1 to 3 in `deliverables/validation_report.md` are run 1's audits. Run 2 has two audits. The "Run 2 audit" used seed 20260928 over two rounds and wrote `data/work/audit_r2data_*`, and the "Run 2 audit after the anchor papers" used seed 20260929 and wrote `data/work/audit_s20260929_*` (`deliverables/validation_report.md`, section headings; `pipeline/audit.py`, docstring). The older `data/work/audit_run2_*.json` files and the `STATUS.md` lines before 16:00 say "run 2" for run 1's round 3, which has nothing to do with the arXiv run 2.

**Findings to know before using the data.**

- **The sampled audit passed, but not every reported cell has been read.** The run 2 audit after the anchor papers found 0 of 20 sampled cells unsupported. In the census of all 27 category cells, the auditor judged 3 unsupported. They are the 2D MEMS integration cell, the piezo maturity cell, and the SOA AI-fit cell (`deliverables/validation_report.md`, Run 2 audit after the anchor papers). The blind second judge judged all 27 supported, so the two judges disagree on these 3 (`STATUS.md`, 21:21 line). Another 12 reported free-text cells passed the code check, which confirms that every cited paper exists and every quote is verbatim, but nobody judged whether the quotes support the value, because the audit judges only sampled and census cells (`deliverables/validation_report.md`, Corrections after code review ([pull request #4](https://github.com/nnicholas-c/ocs-landscape/pull/4)), item 2). The first run 2 audit, with seed 20260928, failed check (b) at 15 percent (`STATUS.md`, 17:37 line), and its second round re-checked the same 20 cells after they were fixed (`deliverables/validation_report.md`, Corrections after code review ([pull request #1](https://github.com/nnicholas-c/ocs-landscape/pull/1)), item 4).
- **The second judge, not the audit, caught the matrix build gaming the audit in run 1.** In round 2 the builder imported the audit's test and padded 18 of 27 category cells with words from the quotes so they would pass (`STATUS.md`, 07:42 line). Gate C passed that round at 0 percent unsupported, and only the second judge flagged it. The fix separated the build from the audit, and unsupported cells went from 25 percent in round 1, to 0 percent in round 2 (not trustworthy), to 5 percent in round 3 (`deliverables/validation_report.md`, Rate comparison across all three rounds).
- **Silicon photonic MEMS leads the device routes with 43 core papers because of how the sample was built.** In run 1 one search phrase supplied 27 of them, and the 3D MEMS phrase added no new core papers (`deliverables/number_checks.md`, section 1). That 0 is a lower bound, because each raw record is credited only to the first query that found it, and the 3D MEMS phrase ran fifth (`deliverables/pitfalls.md`, 14:17 and 14:24 entry). Phrase searches start in 2012, which likely drops older 3D MEMS work (`pipeline/queries.yaml`, year_from). In run 2 the count is unchanged and the snowball supplies only 6 of the 43 (`deliverables/number_checks.md`, Run 2, section 1). OpenAlex's arXiv index is the only path for 7 thermo-optic papers, which is the whole of that route's rise from 23 to 30 (same section).
- **Author records are split, and how often is uncertain.** A flagged name key is a surname plus first initial with several author records. In run 2's fresh sample, 6 of 15 flagged keys were one person split in two or more, which scales to about 59 of 147 keys, with a range of 29 to 94 (`deliverables/number_checks.md`, Run 2, section 2). Run 1's sample gave 10 of 15 (same file, section 2). Person-level rankings need a hand check before the team map is used to recruit individuals, and group-level use is safer (same file, Run 2, section 2).
- **arXiv content now comes through OpenAlex, but 31 core papers still lack OpenAlex data.** arXiv's API refused 9 of 10 phrase queries in run 1 with HTTP status 406 or 429, and a later probe, one request at a time, got 406 every time (`STATUS.md`, stage 1a line; `deliverables/pitfalls_original_log.md`, 15:54). Run 2 took 341 records from OpenAlex's arXiv index instead (`deliverables/curation_report.md`). Still, 31 of 284 core papers have no OpenAlex ID and no citation count, so audit check (a) cannot test their counts (`deliverables/number_checks.md`, Run 2, section 3). [Issue #2](https://github.com/nnicholas-c/ocs-landscape/issues/2) reports that these papers also lack institutions, and that a free DOI lookup found 29 of the 31 in review.
- **Two anchor papers are still missing.** Anchor papers are 13 known papers the collector looks up by title (`pipeline/queries.yaml`, anchors). Jupiter Evolving and RotorNet were fetched by DOI in step 2 but not added. OpenAlex stores only the title words before the colon, so the title check scored 23.88 and 23.19 against a threshold of 95 (`data/work/step2_anchors.md`). The real c-Through paper is in the core set through the snowball (same file).

## What is left to do

**This week**

- [ ] Apply the curator's subset-match guard to the anchor matcher (`fetch_anchor` in `pipeline/collect_openalex.py`). It still accepts a title when `token_set_ratio` alone is at least 95, which matched an unrelated 1999 paper for c-Through (`data/work/step2_anchors.md`).
- [ ] Commit the orchestration layer and a second-judge role, or write the second-judge step into `PLAN.md`, so it is part of the repo.
- [ ] Forbid the analyst from reading or importing `pipeline/audit.py`, in `.claude/agents/analyst.md` and `PLAN.md` stage 6.
- [ ] Log OpenAlex cost per stage. Run 1's snowball cost and run 2's total were not saved (`deliverables/demo_results.md`, Run 1 versus run 2).
- [ ] Backfill OpenAlex records for arXiv-only papers with free DOI lookups ([issue #2](https://github.com/nnicholas-c/ocs-landscape/issues/2)).
- [ ] Keep the arXiv IDs of merged records in `pipeline/curate.py` when the canonical record has none ([issue #3](https://github.com/nnicholas-c/ocs-landscape/issues/3)).
- [ ] Make the member order in `graphs/clusters.csv` independent of `PYTHONHASHSEED` ([issue #5](https://github.com/nnicholas-c/ocs-landscape/issues/5)).
- [ ] Update `README.zh-CN.md`. It translates this README as of commit `5a25410`, before run 2 and steps 2 to 4 were merged, so it still shows run 1's figures and run 2 as in progress.
- [ ] Judge the 12 reported free-text cells (packaging_notes and scaling_limit) that no audit has judged, or add them to the census (`deliverables/validation_report.md`, Corrections after code review ([pull request #4](https://github.com/nnicholas-c/ocs-landscape/pull/4)), item 2).

**Needs a decision (see `deliverables/open_questions.md`)**

- [ ] The scope of OCS, including whether optical packet switches and hyperscaler blog posts count.
- [ ] The standard for "supported" in judged category cells. This covers the 3 of 27 category cells the auditor judged unsupported and the blind second judge judged supported in run 2, the 2D MEMS integration, piezo maturity, and SOA AI-fit cells (`deliverables/validation_report.md`, Run 2 audit after the anchor papers; `STATUS.md`, 21:21 line).
- [ ] Accept 284 core papers or add a cap (`deliverables/curation_report.md`).
- [ ] Recruiting or partnering as the team map's goal. Recruiting needs author disambiguation first.
- [ ] Whether to target OFC (the Optical Fiber Communication Conference) and the networking conferences SIGCOMM and NSDI, with 9, 0, and 0 core papers in run 2, an undercount because 53 of 284 core papers lack a venue (`deliverables/open_questions.md`, item 2). Also whether the power electronics conferences APEC, ECCE, and PCIM belong in scope at all.
- [ ] Whether a DOI taken from the publisher's listing is enough to confirm an anchor paper when OpenAlex's title stops at the colon. This decides whether Jupiter Evolving (W4290990894) and RotorNet (W2743429249) are added (`data/work/step2_anchors.md`, Decision).

**For a full-scale run**

- [ ] Use arXiv's bulk metadata snapshot instead of its API.
- [ ] Add IEEE Xplore as a third collector with an IEEE section in the playbook (it has a key and a daily quota). Add PCIM by manual export or a scout-style agent if it belongs at all, since it has no API. Add patents as a new collector and skill, and company data by raising the scout's cap and fetching with a real browser (`deliverables/architecture.md`).
- [ ] Add a matrix view for the 105 architecture-only core papers (`deliverables/number_checks.md`, Run 2, section 1). What they say about AI clusters is not in any cell yet.
- [ ] Read the ten papers in `deliverables/reading_list.md` in full. Together they target all 33 cells that abstracts leave empty (`deliverables/reading_list.md`, checked against `deliverables/comparison_matrix.csv`).

## Repository layout

```
README.md               this file
PLAN.md                 the nine stages, their outputs, and the gates
STATUS.md               checkpoint log, one line per stage event
CLAUDE.md               the rulebook every agent follows
.claude/agents/         the eight role definitions
.claude/skills/         the four domain skill documents
pipeline/               stage scripts, schema.sql, queries.yaml
data/raw/               raw API pulls as JSONL, plus relevance.csv
data/db/papers.sqlite   the curated database
data/work/              batch files and audit inputs (mostly gitignored; files the deliverables or scripts need are committed)
data/projects.csv       the scout's company and project table
graphs/                 GraphML, rankings, clusters, coauthor.html, tech_map.html, project_timeline.html
deliverables/           meeting documents, the matrix, the audit, the pitfalls log
```

No secrets are committed, because `.env` is gitignored and the repo history has been scanned for the API key.
