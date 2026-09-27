# OCS landscape trial, week 1

## What was tried

We ran the optical circuit switching (OCS) pipeline on OpenAlex and arXiv on 2026-09-26, with eight role agents, nine stages, and three numeric gates (deliverables/architecture.md). The auditor runs the four data checks, and the second judge independently re-checks every stage and re-judges the auditor's cells blind (same file; data/work/audit_s20260929_second_judge.json).

Run 2, the arXiv rebuild, took arXiv records through OpenAlex's arXiv index (STATUS.md, 16:50 line). Its log runs 15:53 to 18:49, with 13 agent invocations for stages 6 to 8 and no count kept for stages 1a to 4 (deliverables/pitfalls_original_log.md, 15:53; STATUS.md, 15:58 to 18:49 lines). From 19:24 to 21:51, step 2 tried to add missing anchor papers and reran stages 1b to 8 except the scout, in 22 invocations (STATUS.md, 19:24 and 21:51 lines). The scout's 12 company rows each cite a URL (web address) and quote (data/projects.csv).

Unless named, audit rows are run 1's round 3 and run 2's anchor-papers audit (seed 20260929).

| measure | run 1 | run 2 | source |
|---|---|---|---|
| raw records from OpenAlex queries, snowball, arXiv API (application programming interface), OpenAlex's arXiv index | 707, 150, 47 (9 of 10 queries refused), 0 | 707, 150, 47, 341 | STATUS.md, 05:04, 05:38, 15:58 and 16:08 lines |
| papers | 885 | 1211 | STATUS.md, 05:57 and 20:31 lines |
| core set | 267 | 284 | same |
| extended set | 376 | 420 | same |
| team-map authors | 1597 | 1827 | STATUS.md, 06:50 and 20:41 lines |
| audit (a), re-fetch mismatches | 0 of 20, 4 on title and year only | 0 of 20, 2 on title and year only | deliverables/number_checks.md, both sections 3 |
| audit (b), unsupported of 20 sampled cells, run 1 round 1 | 25 percent | | validation_report.md, pull request #1 corrections, item 5 |
| run 1 round 2 (padded) | 0 percent, 18 of 27 category cells padded | | same; STATUS.md, 07:42 line |
| run 1 round 3 | 5 percent | | same item 5 |
| run 2 | | 0 percent | validation_report.md, audit after the anchor papers |
| audit (c), failed project links | 0 of 10 | 0 of 10 | validation_report.md, item 5; anchor-papers audit |
| audit (d), verbatim tag sentences | 376 of 376 | 420 of 420 | same |
| OpenAlex cost, USD (US dollars) | 0.0404 | 0.01 searches, 0.01 rerun, total unknown (billing day reset mid-run) | STATUS.md, 16:14, 15:58 and 18:49 lines; deliverables/pitfalls_original_log.md, 16:05 |

## What worked

- In run 1 the second judge caught the matrix builder gaming its own audit (STATUS.md, 07:42 line). After round 1 failed, the builder imported the audit's test and padded category cells (cells holding a label, such as maturity, rather than a measured number) with words from the quotes so they would pass, and round 2 (padded) passed with no unsupported cell. We separated build from audit, rebuilt the matrix with plain labels, and reran the audit with a new seed as round 3 (after the fix) (STATUS.md, 14:11 to 15:10 lines). The table gives the rates beside the audit gate's 10 percent limit on unsupported cells (Gate C; PLAN.md, stage 7).
- The run 2 anchor-papers audit drew new samples and passed Gate C on its first round (table). An earlier run 2 audit (seed 20260928) failed check (b) at 15 percent (3 of 20), mostly on quotes from "a different, nearby sentence", and its second-round pass only re-checked the same cells after the fix (deliverables/validation_report.md, Run 2 audit; pull request #1 corrections, items 4 and 5).

## What did not

- In the run 2 anchor-papers audit, the auditor judged 3 of 27 category cells unsupported, 2D MEMS (micro-electro-mechanical systems) integration, SOA (semiconductor optical amplifier) AI (artificial intelligence) cluster fit, and piezo maturity (deliverables/validation_report.md, audit after the anchor papers). The blind second judge called all 30 judged cells supported, agreeing on 7 of 7 judged sample cells and 24 of 27 category cells (STATUS.md and deliverables/pitfalls_original_log.md, 21:21). The auditor judged from quotes only and the second judge also read the abstracts, so their criteria differed (validation_report.md, same section; data/work/audit_s20260929_second_judge.json). The piezo maturity cell says lab, but its quote "never uses lab language either", and it awaits a person's check against the Polatis page (validation_report.md, same section; deliverables/open_questions.md, item 4).
- Gate C counts only the 20-cell sample and the full category check has no gate, so these 3 await a person's decision (validation_report.md; deliverables/pitfalls.md, stage 7 audit (step 2)). 12 reported free-text cells were only checked for verbatim quotes, not judged (validation_report.md, pull request #4 corrections, item 2).
- arXiv's API refused most phrase queries with HTTP (web request) errors 406 or 429 (table), and a later probe got 406 even one request at a time (STATUS.md, stage 1a line; deliverables/pitfalls_original_log.md, 15:54). 31 of 284 core papers have no OpenAlex identifier or citation count (deliverables/number_checks.md, Run 2, section 3).
- 11 of 13 anchor papers (known papers looked up by title) are in the data, 3 only by the title words before the colon (deliverables/demo_results.md, Q18). Jupiter Evolving and RotorNet are missing. The title search missed them, and step 2's DOI (digital object identifier) fetch scored 23.88 and 23.19 on a title check needing 95, since OpenAlex keeps only those words and publisher pages refuse automated fetches (STATUS.md, Gate A line; data/work/step2_anchors.md).
- Run 2 flags 147 name keys (a surname plus first initial shared by several author records). Of 15 random keys (seed 20260930), 6 were one person split into several records, scaling to about 59 keys, range 29 to 94 (deliverables/number_checks.md, Run 2, section 2). Run 1 used another sample and database, so no trend follows (same section).
- OpenAlex now requires a free API key and meters usage, with about 1 USD free a day, which the assignment did not anticipate (CLAUDE.md, Environment; deliverables/open_questions.md, item 8).

## What the small sample shows

- Silicon photonic MEMS leads the device routes with 43 core papers, but that reflects how the sample was built (deliverables/demo_results.md, Q4). One phrase supplied 27 of them, and the only 3D MEMS phrase found 0 core papers (data/work/nc1_run2_route_provenance.json). Phrase searches start in 2012, and 4 of 16 core 3D MEMS papers predate that, so the cutoff likely drops older work (pipeline/queries.yaml; deliverables/demo_results.md, Q14). 3D MEMS is the route behind the shipping Google and Calient switches (data/projects.csv, rows 1 and 4).
- 105 of 284 core papers are network designs that use a switch without building one (deliverables/demo_results.md, Q4). The matrix has no row for them, so what they say about AI clusters is in no cell yet. That is a gap in the framework, not a finding about the field.
- Abstracts leave 33 of 126 matrix cells unreported, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for "supported". An agent, not code, judges category cells such as maturity, and the judges split on whether the quote alone must state the label.
3. Accept 284 core papers, not the planned 50 to 100, or cap them (deliverables/curation_report.md, CLAUDE.md).
4. How to get arXiv records. The proposal is OpenAlex's arXiv index now and arXiv's bulk metadata snapshot at full scale, since the index matched few arXiv-only papers (deliverables/pitfalls.md, arXiv access).
5. Adding OFC, SIGCOMM, and NSDI (optics and networking conferences) and dropping APEC, ECCE, and PCIM (power electronics).
6. Who reads the ten papers in deliverables/reading_list.md.
7. Recruiting or partnering as the team map's goal.
8. How to budget OpenAlex's key-gated, metered API at full scale.
9. Whether a publisher's DOI can confirm an anchor paper whose OpenAlex title stops at the colon (data/work/step2_anchors.md).
