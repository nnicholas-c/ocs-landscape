# OCS landscape trial, week 1

## What was tried

The optical circuit switching (OCS) pipeline has eight role agents, nine stages, and three gates. A second judge independently re-checks every stage (deliverables/architecture.md; data/work/audit_s20260929_second_judge.json).

Run 2 took arXiv records through OpenAlex's arXiv index, and step 2 (anchor papers) reran stages 1b to 8 except the scout (STATUS.md, 16:50 line; deliverables/demo_results.md, Numbers).

Unnamed audit rows are run 1's round 3 and run 2's anchor-papers audit.


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

- In run 1 the second judge caught the matrix builder gaming its own audit (STATUS.md, 07:42 line). After round 1 failed, the builder imported the audit's test and padded category cells such as maturity with quote words, passing round 2 (padded). Round 3 (after the fix) audited a matrix rebuilt without audit code (table; STATUS.md, 14:11 to 15:10 lines).
- Run 2's anchor-papers audit passed Gate C (the audit gate, at most 10 percent unsupported cells) first time (PLAN.md, stage 7; deliverables/demo_results.md, Audit results).

## What did not

- After the fix, the auditor judged 3 of 27 run 2 category cells unsupported, which the second judge, also reading the abstracts, called supported. None is sampled for Gate C, so a person must decide (deliverables/demo_results.md, Audit results).
- Jupiter Evolving and RotorNet, two anchor papers (known papers sought by title), are a known limit until after the meeting, because OpenAlex truncates their long titles at the colon, failing the title check (issue #13; data/work/step2_anchors.md; deliverables/demo_results.md, Numbers).
- About 59 (29 to 94) of run 2's 147 flagged name keys (surname plus first initial) hide one split person, from a sample of 15 (deliverables/number_checks.md, Run 2, section 2). Run 1's separate sample gave a higher range, so the true rate is uncertain, not falling (same file).
- The audit log keeps unresolved inconsistencies, mostly citations mixing old and new deliverables/pitfalls.md line numbers, because its corrections failed a third and final check (deliverables/validation_report.md, corrections after the step 7 style and source check; STATUS.md).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) leads the device routes with 43 core papers, but one phrase supplied 27 and the only 3D MEMS phrase 0, so the lead reflects the sample (data/work/nc1_run2_route_provenance.json; deliverables/demo_results.md, Technology and Early project maps).
- 105 of 284 core papers design networks without building a switch, and no matrix row holds their AI (artificial intelligence) cluster claims, a framework gap, not a finding (deliverables/demo_results.md, Q4).
- Abstracts leave 33 of 126 matrix cells unreported, and cost per port is known for 1 of 9 routes (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for "supported". An agent, not code, judges category cells, and the judges split on whether the quote alone must state the label.
3. Accept 284 core papers or cap them near the planned 50 to 100 (deliverables/curation_report.md; CLAUDE.md).
4. How to get arXiv records, with OpenAlex's arXiv index proposed now and arXiv's bulk metadata snapshot at full scale, since the index matched few arXiv-only papers (deliverables/pitfalls.md, arXiv access).
5. Adding OFC, SIGCOMM, and NSDI (optics and networking conferences), dropping APEC, ECCE, and PCIM (power electronics).
6. Who reads deliverables/reading_list.md in full.
7. Recruiting or partnering as the team map's goal.
8. How to budget OpenAlex's API, now needing a free key and metered (about 1 USD free a day), unforeseen by the assignment (CLAUDE.md, Environment).