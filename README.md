# OCS landscape

English | [简体中文](README.zh-CN.md)

[中文项目汇报网站 · Chinese presentation](https://liu0029yuxuan.github.io/ocs-landscape-presentation/)

An agent-driven pipeline that maps optical circuit switching (OCS) for AI data centers from open bibliographic sources. Python scripts do the deterministic steps, role agents make the judgement calls, and every judgement is saved with its evidence (a quote, paper IDs, or a URL) so that it can be checked. The pipeline builds three maps.

1. **Technologies.** The switching routes (3D MEMS, 2D MEMS, silicon photonic MEMS, LCoS, piezo, thermo-optic, electro-optic, SOA, robotic patch panels) and how they compare on switching time, loss, port count, maturity, and fit for AI clusters.
2. **Teams.** The research groups that work on OCS, and the groups in adjacent fields whose skills transfer to it. Those fields are telecom cross-connects, micromirrors, silicon photonics, LCoS displays, free-space packaging, and data center networking.
3. **Projects.** Startups, established vendors, and hyperscaler projects, each backed by a public URL and a verbatim quote.

This repository holds a week-one, small-sample trial. Its purpose is to show that the pipeline works end to end and that its output can be checked. It is not yet a finished landscape report.

## Status

| Milestone | State | Where |
|---|---|---|
| Run 1, a full pass of stages 0 to 8 with three gates | Done | tag `run1` |
| Audit fix. The matrix build is separated from its audit, and stages 6 and 7 were rerun with a new seed | Done | tag `run1-fixed` |
| Three questioned numbers checked | Done | `deliverables/number_checks.md` |
| Meeting one-pager revised, and audit rounds renamed 1, 2 (padded), and 3 (after the fix) | Done | `master` |
| Run 2. arXiv papers collected through OpenAlex's arXiv index and carried through stages 1b to 8 | In progress | not yet pushed; will appear as branch `run2` |

Until run 2 lands, `master` is the version to present. The one-page summary is `deliverables/meeting_summary.md`.

## Scope of the trial

- **Sources.** OpenAlex and arXiv only (`CLAUDE.md`, rule 6). IEEE Xplore, PCIM, Crossref, patents, and paid company data are out of scope on purpose. `deliverables/architecture.md` records what adding IEEE Xplore, PCIM, patents, or company data would take.
- **Size.** The trial aimed for 50 to 100 core papers (`CLAUDE.md`). Above 200 relevant records, Gate A keeps every score 3 record, which gave 267 core papers after deduplication. Whether to accept that is one of the open decisions.
- **Cost.** OpenAlex requires a free API key and meters usage, with about 1 USD a day free. Run 1 cost 0.04 USD.

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
3. Get a free OpenAlex key at https://openalex.org/settings/api, run `cp .env.example .env`, and set `OPENALEX_API_KEY`. The key is required, and `collect_openalex` and `audit` stop if it is unset. arXiv needs no key.

On Windows the interpreter is `.venv\Scripts\python.exe`, and the console's default code page crashes on non-ASCII titles. In Git Bash, create `.venv/bin/python` with the lines below and run `chmod +x .venv/bin/python`. In PowerShell, set `$env:PYTHONUTF8=1` and call `.venv\Scripts\python -m pipeline.<module>`.

```sh
#!/bin/sh
PYTHONUTF8=1 exec "$(dirname "$0")/../Scripts/python.exe" "$@"
```

## Running the deterministic steps

Run each module from the repo root as `.venv/bin/python -m pipeline.<module>`. Modules with flags print them with `--help`. The others take no flags and ignore `--help`, so adding it runs them.

| Module | Purpose |
|---|---|
| `collect_openalex` | Pull OpenAlex records into `data/raw/` (`--mode smoke`, `full`, or `snowball`, plus a required `--out <file>.jsonl`) |
| `collect_arxiv` | Pull arXiv records (`--mode smoke` or `full`, plus `--out`) |
| `tag_export`, `tag_import` | Write batch files for the tagger and import its labels (`--mode relevance` or `full`). `tag_export --mode full --only <file>` retags the paper IDs listed one per line in that file |
| `curate` | Deduplicate by DOI, then arXiv ID, then fuzzy title, and load `papers.sqlite` |
| `graph` | Build the co-author and institution graphs, the rankings, and `coauthor.html` |
| `matrix_export`, `matrix_build`, `matrix_render` | Export route files, build the matrix CSV from the analyst's recorded cell decisions, and render the markdown |
| `audit` | Run Gate C checks (a) to (d) with a fixed seed. Needs the OpenAlex key and network access. `--merge` combines the pre-judgement results with the auditor's judgments |
| `check_route_provenance`, `check_name_keys`, `merge_name_keys` | The number checks behind `deliverables/number_checks.md` |
| `test_curate`, `test_tag_pipeline` | Regression checks |

To rebuild the outputs from committed data, run `curate`, `graph`, `matrix_export`, `matrix_build`, and `matrix_render` in that order. The number checks and the two tests also run from committed files.

`matrix_build.py` imports nothing from `audit.py`. In the audit fix, the analyst rebuilt the matrix before `audit.py` was rewritten, so it never saw the new test. No rule enforces this yet.

## Running the judgement stages

Scripts cannot run these stages. They need an agent host that reads `CLAUDE.md` as standing instructions, can launch the role files in `.claude/agents/` as subagents with the skills in `.claude/skills/`, and gives the scout web search and fetch. To run or resume, open a session in the repo root and ask it to follow `PLAN.md` from the first unticked stage in `STATUS.md`.

| Role | Hands back | Read by |
|---|---|---|
| tagger | `data/work/relevance_batch_NNN.out.json`, `data/work/tag_batch_NNN.out.json` | `tag_import --mode relevance`, `tag_import --mode full` |
| scout | `data/projects.csv` | `matrix_build`, `audit` |
| analyst | `data/work/matrix_cells.yaml` | `matrix_build` |
| auditor | `data/work/audit_run2_judgments.json` | `audit --merge` |
| writer | the six files in `deliverables/` | readers |

## Results so far

The figures below are from `master`.

| Measure | Value | Source |
|---|---|---|
| Raw records to papers | 904 to 885 | `deliverables/curation_report.md` |
| Core set and extended set | 267 and 376 | `deliverables/curation_report.md` |
| Authors in the team map | 1597, in 143 communities | `graphs/top_pis.csv`, `graphs/clusters.csv` |
| Company and project rows | 12, each with a URL and a quote | `data/projects.csv` |
| Matrix cells | 126, of which 81 reported, 9 derived, 32 not reported, 4 with no source | `deliverables/comparison_matrix.csv` |
| Gate C, round 3 | 0 percent mismatches, 5 percent unsupported, 0 percent project failures, 100 percent verbatim | `deliverables/validation_report.md` |

**Naming.** `data/work/audit_run2_*.json`, the docstring of `pipeline/audit.py`, and the `STATUS.md` lines before 16:00 say "run 2" for the audit this README calls round 3. That audit has nothing to do with the arXiv run 2.

**Findings to know before using the data.**

- **The second judge, not the audit, caught the matrix build gaming the audit.** In round 2 the builder imported the audit's test and padded 18 of 27 category cells with words from the quotes so they would pass. Gate C passed that round at 0 percent unsupported, and only the second judge flagged it. The fix separated the build from the audit, rebuilt the matrix with plain labels, and reran the audit with a new seed. Unsupported cells went from 25 percent in round 1, to 0 percent in round 2 (not trustworthy), to 5 percent in round 3.
- **Silicon photonic MEMS leads the device routes with 43 core papers because of how the sample was built.** One search phrase supplied 27 of them, the 3D MEMS phrase added no new core papers, and the 2012 start year for phrase searches likely drops older 3D MEMS work.
- **Author records are split.** Of the 149 flagged name keys (a surname plus first initial with several author records, at least one with a core paper), an estimated 62 to 126 are one person split in two or more, based on 10 of 15 sampled keys. Fix this before using the team map to recruit individuals.
- **arXiv's API refused 9 of 10 phrase queries** (HTTP 406, some 429), leaving 47 arXiv records. A later probe, one request at a time, got 406 on every request, so pacing was not the cause. Run 2 takes arXiv content through OpenAlex's arXiv index instead, labelled as such.

## What is left to do

**This week**

- [ ] Finish run 2 and push it as branch `run2`, with a run 1 versus run 2 table.
- [ ] Fetch the two missing anchor papers, Jupiter Evolving and RotorNet, by DOI. Singleton lookups are free. The real c-Through paper is already in the core set through the snowball.
- [ ] Apply the curator's subset-match guard to the anchor matcher in `collect_openalex`, which accepted an unrelated 1999 paper for c-Through.
- [ ] Commit the orchestration layer and a second-judge role, or write the second-judge step into `PLAN.md`, so it is part of the repo.
- [ ] Forbid the analyst from reading or importing `pipeline/audit.py`, in `.claude/agents/analyst.md` and `PLAN.md` stage 6.
- [ ] Recompute the matrix's academic-groups and companies cells in the audit independently. The audit currently reuses the builder's functions for them.
- [ ] Log OpenAlex cost per stage. The snowball's cost was not saved.

**Needs a decision (see `deliverables/open_questions.md`)**

- [ ] The scope of OCS, including whether optical packet switches and hyperscaler blog posts count.
- [ ] The standard for "supported" in judged category cells. This covers the 3 of 27 category cells the auditor judged unsupported when it checked all of them (the 3D MEMS and 2D MEMS integration cells and the piezo maturity cell).
- [ ] Accept 267 core papers or add a cap.
- [ ] Recruiting or partnering as the team map's goal. Recruiting needs author disambiguation first.
- [ ] Whether to target OFC, SIGCOMM, and NSDI (9, 0, and 0 core papers so far), and whether the power electronics venues APEC, ECCE, and PCIM belong in scope at all.

**For a full-scale run**

- [ ] Use arXiv's bulk metadata snapshot instead of its API.
- [ ] Add IEEE Xplore as a third collector with an IEEE section in the playbook (it has a key and a daily quota). Add PCIM by manual export or a scout-style agent if it belongs at all, since it has no API. Add patents as a new collector and skill, and company data by raising the scout's cap and fetching with a real browser (`deliverables/architecture.md`).
- [ ] Add a matrix view for the 101 architecture-only core papers. What they say about AI clusters is not in any cell yet.
- [ ] Read the ten papers in `deliverables/reading_list.md` in full. They target 23 of the 32 cells that abstracts leave empty.

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
graphs/                 GraphML, rankings, clusters, coauthor.html
deliverables/           meeting documents, the matrix, the audit, the pitfalls log
```

No secrets are committed, because `.env` is gitignored and the repo history has been scanned for the API key.
