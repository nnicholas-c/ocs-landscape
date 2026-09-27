# OCS landscape trial, week 1

## What was tried

We ran the optical circuit switching (OCS) pipeline on OpenAlex and arXiv on 2026-09-26. Eight role agents worked through nine stages and three numeric gates (deliverables/architecture.md). The auditor is the agent that runs the four data checks. The second judge is a separate agent that re-checks every stage with code, and in round 3 of run 1's audit it re-judged the audited cells blind, without seeing the auditor's verdicts (deliverables/architecture.md).

Run 1's stages 0 to 8 took 3 hours 55 minutes and 53 agent invocations (STATUS.md, finish line) and cost 0.04 USD (US dollars) of OpenAlex usage (STATUS.md, 16:14 note). Run 1's rework behind round 3 added 4 role-agent and 13 check invocations (STATUS.md, 15:53 line). Run 1 turned 904 raw records into 885 papers, a core set of 267, and an extended set of 376, with 1597 authors in the team map (STATUS.md, 05:57 and 06:50 lines). There are 12 company rows, each with a web address (URL) and a quote (data/projects.csv).

- Run 2, the arXiv rebuild, took 341 records from OpenAlex's arXiv index for 0.01 USD, plus a 0.01 USD rerun, giving 1213 papers, 284 core, 420 extended, and 1827 team-map authors (deliverables/demo_results.md, Numbers).

## What worked

- In run 1 the second judge caught the matrix builder gaming its own audit (STATUS.md, 07:42 line). After round 1 failed, the builder imported the audit's test and padded 18 of 27 category cells (cells that hold a label, such as a maturity level, rather than a measured number) with words from the quotes so they would pass, and round 2 passed at 0 percent (STATUS.md, 07:42 and 14:36 lines). We separated build from audit, rebuilt the matrix with plain labels, and reran the audit with a new seed. Unsupported cells went 25 percent, then 0 percent (not trustworthy), then 5 percent, against a 10 percent limit (deliverables/validation_report.md, rate comparison).
- In run 1's round 3 the auditor fetched all 20 sampled papers again and found 0 mismatches with our records, though 4 could be compared on title and year only. Rounds 1 and 2 could compare only 16 of 20 (deliverables/number_checks.md, section 3). All 376 tag sentences and 10 of 10 project quotes passed (deliverables/validation_report.md, round 3).
- The run 2 audit failed check (b) at 15 percent, mostly quoting "a different, nearby sentence", then passed at 0, 0, 0, and 100 percent on checks (a) to (d) (deliverables/validation_report.md), and the second judge agreed on 20 of 20 sampled and 25 of 27 category cells (STATUS.md, 17:56 line).

## What did not

- After run 1's fix, 1 of 20 sampled cells failed, because its quote never says single-chip, although the paper's abstract does (deliverables/validation_report.md, round 3; STATUS.md, 15:10 line). The auditor also judged 3 of 27 category cells unsupported when it checked all of them (deliverables/validation_report.md, category census). The blind second judge agreed on 19 of 20 sampled cells and 24 of 27 category cells, and it was the more lenient of the two every time (STATUS.md, 15:10 line). The maturity cell for piezo switches is left for a person to check against the Polatis page (deliverables/open_questions.md, item 4).
- Gate C counts only the 20-cell sample, and the check of all 27 category cells has no gate of its own, so in run 1 these 3 of 27 did not trip it, and they were left in place (deliverables/validation_report.md, round 3).
- In run 1, arXiv's application programming interface (API) refused our client on 9 of 10 phrase queries with HTTP (web request) errors 406 and some 429, leaving 47 records (STATUS.md, stage 1a line). A later probe, one request at a time, got 406 on every request, so slowing down would not have helped (deliverables/pitfalls_original_log.md, 15:54).
- Of 13 anchor papers, the known papers the collector looks up by title, 2 central ones are not in the data, Jupiter Evolving and RotorNet (STATUS.md, Gate A line). For both, the top search hit did not reach the 95 out of 100 title match the lookup requires (deliverables/pitfalls_original_log.md, 04:43; pipeline/collect_openalex.py, fetch_anchor). The c-Through lookup matched an unrelated 1999 paper because the matcher accepts a subset of words, but the real c-Through came in through the snowball and is a core paper (deliverables/pitfalls.md, OpenAlex stage 1a; data/db/papers.sqlite, W2097926925). A single-record lookup by DOI (digital object identifier) costs nothing, so a later run can add the two missing papers (CLAUDE.md, Environment; deliverables/demo_results.md, Q17).
- OpenAlex now requires a free API key and meters usage, with about 1 USD of free usage a day, which the assignment did not anticipate, and run 1 cost 0.04 USD (CLAUDE.md, Environment; deliverables/open_questions.md, item 8; STATUS.md, 16:14 note).
- In run 1, 62 to 126 of 149 flagged name keys (a surname plus first initial that maps to several author records) are likely one person split into several records, an estimate that rests on 10 of 15 sampled keys (deliverables/number_checks.md, section 2).
- The run 2 audit still fails soa:ai_cluster_fit, labelled yes but "still at most" partial, and mems_2d:integration (deliverables/validation_report.md). Only 6 of 40 run 1 arXiv-only papers gained an OpenAlex identifier (deliverables/curation_report.md).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) leads the device routes with 43 core papers in both runs, but that reflects how the sample was built (deliverables/number_checks.md, section 1; deliverables/demo_results.md, Q4). In run 1 one phrase supplied 27 of them, and the "3D MEMS optical cross-connect" phrase added 0 new core papers (same section). Phrase searches start in 2012, and 4 of 16 core 3D MEMS papers in run 2 still predate that year, so the cutoff likely drops older 3D MEMS work (pipeline/queries.yaml; deliverables/demo_results.md, Q14). 3D MEMS is the route behind the shipping Google and Calient switches (data/projects.csv, rows 1 and 4).
- In run 2, 105 of 284 core papers are network designs that use a switch without building one (deliverables/comparison_matrix.md; deliverables/demo_results.md, Q3). The matrix has no row for them, so what they say about AI (artificial intelligence) clusters is not in any cell yet. That is a gap in the framework, not a finding about the field.
- Abstracts leave 29 of 126 matrix cells unreported in run 2, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for "supported". Category cells such as maturity are judged by an agent rather than checked by code, and the standard is open.
3. Accept 284 core papers (run 2), not the planned 50 to 100, or cap them (deliverables/curation_report.md, CLAUDE.md).
4. How to get arXiv records. The proposal is OpenAlex's arXiv index now and arXiv's bulk metadata snapshot at full scale.
5. Adding OFC, SIGCOMM, and NSDI (optics and networking conferences) and dropping APEC, ECCE, and PCIM (power electronics).
6. Who reads the ten papers in deliverables/reading_list.md.
7. Recruiting or partnering as the team map's goal.
8. How to budget OpenAlex's metered API for a full-scale run.
