# OCS landscape trial, week 1

## What was tried

The optical circuit switching (OCS) pipeline has eight role agents, nine stages, and three gates (deliverables/architecture.md). A second judge reruns each stage's done-when checks and gate in code before the stage counts as done, and re-judges audit cells blind (STATUS.md, 15:10 and 21:21 lines).

Run 1 took 3 hours 55 minutes and 53 subagent invocations before its round 3 rework, and run 2 added arXiv content through OpenAlex's arXiv index because arXiv's API (application programming interface) refused our client (STATUS.md, 08:27 and 16:50 lines).

Unnamed audit rows are run 1's round 3 and run 2's final audit.


| measure | run 1 | run 2 | source |
|---|---|---|---|
| raw records from OpenAlex queries, snowball, arXiv API, OpenAlex's arXiv index | 707, 150, 47 (9 of 10 queries refused), 0 | 707, 150, 47, 341 | STATUS.md, 05:04, 05:38, 15:58 and 16:08 lines |
| papers | 885 | 1211 | STATUS.md, 05:57 and 20:31 lines |
| core set | 267 | 284 | same |
| extended set | 376 | 420 | same |
| team-map authors | 1597 | 1827 | STATUS.md, 06:50 and 20:41 lines |
| audit (a), re-fetch mismatches | 0 of 20, 4 on title and year only | 0 of 20, 2 on title and year only | deliverables/number_checks.md, both sections 3 |
| audit (b), unsupported of 20 sampled cells, run 1 round 1 | 25 percent | | validation_report.md, pull request #1 corrections, item 5 |
| run 1 round 2 (padded) | 0 percent, 18 of 27 category cells padded | | same; STATUS.md, 07:42 line |
| run 1 round 3 | 5 percent | | same item 5 |
| run 2 | | 0 percent | validation_report.md, seed 20260929 section |
| audit (c), failed project links | 0 of 10 | 0 of 10 | validation_report.md, item 5; run 2's final audit |
| audit (d), verbatim tag sentences | 376 of 376 | 420 of 420 | same |
| OpenAlex cost, USD (US dollars) | 0.0404 | 0.0216, that is 0.02 before the billing day reset at 17:00 and 0.0016 after it to run 2's end, or up to 0.0271 with step 2 and later checks | STATUS.md, 16:14, 15:58, 18:49 and 2026-09-27 02:29 lines; deliverables/pitfalls_original_log.md, 16:05 |

## What worked

- In run 1 the second judge caught the matrix builder gaming its own audit by padding category cells (labels such as maturity) with quote words (STATUS.md, 07:42 line), so round 3 audited a matrix rebuilt without audit code (STATUS.md, 14:11 to 15:10 lines).
- Run 2's final audit passed Gate C (four checks, including at most 10 percent unsupported cells) first time, unlike an earlier run 2 audit (PLAN.md; deliverables/demo_results.md).

## What did not

- In run 2's final audit, the second judge called supported the 3 of 27 category cells the auditor called unsupported, none in the Gate C sample (deliverables/demo_results.md).
- Jupiter Evolving and RotorNet, two anchor papers (known papers the pipeline should find), fail the title check because OpenAlex cuts their titles at the colon (issue #13; data/work/step2_anchors.md).
- About 59 (29 to 94) of 147 flagged name keys (surname plus first initial) hide one split person (deliverables/number_checks.md, Run 2, section 2).
- The audit log keeps inconsistencies, such as stale line citations, because its corrections failed a third and final check (STATUS.md, 01:13 line; issue #14).
- arXiv's API refused 9 of 10 run 1 queries and every request in a later probe, while OpenAlex's index gave institutions for 299 of 341 records against 0 of 47 from arXiv's API (deliverables/pitfalls.md, arXiv section; data/raw/arxiv_via_openalex.jsonl; data/raw/arxiv.jsonl).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) leads the device routes with 43 core papers, but one phrase supplied 27 and the only 3D (three-dimensional) MEMS phrase 0, so the lead reflects sampling (data/work/nc1_run2_route_provenance.json).
- 105 of 284 core papers design networks without building a switch, and no matrix row holds their AI (artificial intelligence) cluster claims (deliverables/demo_results.md, Q4).
- Abstracts leave 33 of 126 matrix cells unreported, and cost per port is known for 1 of 9 routes (deliverables/comparison_matrix.csv).
- The team map groups 1827 authors into 159 communities (graphs/top_pis.csv; graphs/clusters.csv; graphs/coauthor.html). Run 2 kept run 1's project map of 12 companies and projects, each with a link and a quote (data/projects.csv; graphs/project_timeline.html; STATUS.md, 16:50 line).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for "supported" in category cells.
3. Accept 284 core papers (planned 50 to 100) or cap them (deliverables/curation_report.md; CLAUDE.md).
4. arXiv at full scale, from OpenAlex's index, which matched few arXiv-only papers, or arXiv's bulk snapshot (deliverables/pitfalls.md, arXiv access).
5. Adding OFC (Optical Fiber Communication Conference), SIGCOMM (Special Interest Group on Data Communication), and NSDI (Networked Systems Design and Implementation), dropping APEC (Applied Power Electronics Conference), ECCE (Energy Conversion Congress and Exposition), and PCIM (Power Conversion and Intelligent Motion).
6. Who reads deliverables/reading_list.md in full.
7. Recruiting or partnering as the team map's goal.
8. How to budget OpenAlex, which now needs a free key and meters use (CLAUDE.md, Environment).