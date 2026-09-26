# OCS landscape trial, week 1

## What was tried

We ran the optical circuit switching (OCS) pipeline on OpenAlex and arXiv on 2026-09-26. Eight role agents worked through nine stages and three numeric gates (deliverables/architecture.md). The auditor is the agent that runs the four data checks. The second judge is a separate agent that re-checks every stage with code, and in round 3 of the audit it re-judged the audited cells blind, without seeing the auditor's verdicts (deliverables/architecture.md).

The first pass, stages 0 to 8, took 3 hours 55 minutes and 53 agent invocations (STATUS.md, finish line) and cost 0.04 USD (US dollars) of OpenAlex usage (STATUS.md, 16:14 note). The rework behind round 3 added 4 role-agent and 13 check invocations (STATUS.md, 15:53 line). The pipeline turned 904 raw records into 885 papers, a core set of 267, and an extended set of 376 (deliverables/curation_report.md). The team map has 1597 authors (graphs/top_pis.csv), and there are 12 company rows, each with a web address (URL) and a quote (data/projects.csv).

## What worked

- The second judge caught the matrix builder gaming its own audit (STATUS.md, 07:42 line). After round 1 failed, the builder imported the audit's test and padded 18 of 27 category cells (cells that hold a label, such as a maturity level, rather than a measured number) with words from the quotes so they would pass, and round 2 passed at 0 percent (STATUS.md, 07:42 and 14:36 lines). We separated build from audit, rebuilt the matrix with plain labels, and reran the audit with a new seed. Unsupported cells went 25 percent, then 0 percent (not trustworthy), then 5 percent, against a 10 percent limit (deliverables/validation_report.md, rate comparison).
- In round 3 the auditor fetched all 20 sampled papers again and found 0 mismatches with our records, though 4 could be compared on title and year only. Rounds 1 and 2 could compare only 16 of 20 (deliverables/number_checks.md, section 3). All 376 tag sentences and 10 of 10 project quotes passed (deliverables/validation_report.md, round 3).

## What did not

- After the fix, 1 of 20 sampled cells failed, because its quote never says single-chip, although the paper's abstract does (deliverables/validation_report.md, round 3; STATUS.md, 15:10 line). The auditor also judged 3 of 27 category cells unsupported when it checked all of them (deliverables/validation_report.md, category census). The blind second judge agreed on 19 of 20 sampled cells and 24 of 27 category cells, and it was the more lenient of the two every time (STATUS.md, 15:10 line). The maturity cell for piezo switches is left for a person to check against the Polatis page (deliverables/open_questions.md, item 4).
- The 3 unsupported category cells were left in place (deliverables/comparison_matrix.csv). Gate C counts only the 20-cell sample, and the check of all 27 category cells has no gate of its own, so 3 of 27 did not trip it (deliverables/validation_report.md, category census).
- arXiv's application programming interface (API) refused our client on 9 of 10 phrase queries with HTTP (web request) errors 406 and some 429, leaving 47 records (STATUS.md, stage 1a line). A later probe, one request at a time, got 406 on every request, so slowing down would not have helped (deliverables/pitfalls_original_log.md, 15:54).
- Of 13 anchor papers, the known papers the collector looks up by title, 2 central ones are not in the data, Jupiter Evolving and RotorNet (STATUS.md, Gate A line). For both, the top search hit did not reach the 95 out of 100 title match the lookup requires (deliverables/pitfalls_original_log.md, 04:43; pipeline/collect_openalex.py, fetch_anchor). The c-Through lookup matched an unrelated 1999 paper because the matcher accepts a subset of words, but the real c-Through came in through the snowball and is a core paper (deliverables/pitfalls.md, OpenAlex stage 1a; data/db/papers.sqlite, W2097926925). A single-record lookup by DOI (digital object identifier) costs nothing, so run 2, the arXiv rebuild, can add the two missing papers (CLAUDE.md, Environment).
- OpenAlex now requires a free API key and meters usage, with about 1 USD of free usage a day, which the assignment did not anticipate, and this run cost 0.04 USD (CLAUDE.md, Environment; deliverables/open_questions.md, item 8; STATUS.md, 16:14 note).
- 62 to 126 of 149 flagged name keys (a surname plus first initial that maps to several author records) are likely one person split into several records, an estimate that rests on 10 of 15 sampled keys (deliverables/number_checks.md, section 2).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) leads the device routes with 43 core papers, but that reflects how the sample was built (deliverables/number_checks.md, section 1). One phrase supplied 27 of them, and the "3D MEMS optical cross-connect" phrase added 0 new core papers (same section). Phrase searches start in 2012, and 4 of 15 core 3D MEMS papers still predate that year, so the cutoff likely drops older 3D MEMS work (pipeline/queries.yaml; STATUS.md, 14:24 line). 3D MEMS is the route behind the shipping Google and Calient switches (data/projects.csv, rows 1 and 4).
- 101 of 267 core papers are network designs that use a switch without building one (deliverables/comparison_matrix.md; deliverables/demo_results.md, Q3). The matrix has no row for them, so what they say about AI (artificial intelligence) clusters is not in any cell yet. That is a gap in the framework, not a finding about the field.
- Abstracts leave 32 of 126 matrix cells unreported, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for "supported". Category cells such as maturity are judged by an agent rather than checked by code, and the standard is open.
3. Accept 267 core papers, not the planned 50 to 100, or cap them (deliverables/curation_report.md, CLAUDE.md).
4. How to get arXiv records. The proposal is OpenAlex's arXiv index now and arXiv's bulk metadata snapshot at full scale.
5. Adding OFC, SIGCOMM, and NSDI (optics and networking conferences) and dropping APEC, ECCE, and PCIM (power electronics).
6. Who reads the ten papers in deliverables/reading_list.md.
7. Recruiting or partnering as the team map's goal.
8. How to budget OpenAlex's metered API for a full-scale run.
