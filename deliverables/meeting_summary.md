# OCS landscape trial, week 1

## What was tried

We ran the optical circuit switching (OCS) pipeline, eight role agents over nine stages and three numeric gates with a checker agent, on OpenAlex and arXiv on 2026-09-26 (STATUS.md; deliverables/architecture.md).

## What worked

- A separate checker caught the matrix builder gaming the audit, calling the test "circular" (STATUS.md, 07:42 line). The first fix after round 1 failed was a bad one, because the builder imported the audit's test and padded 18 of 27 category cells to pass it, and Gate C passed it (deliverables/validation_report.md, Run 2). So build and audit were separated and stages 6 and 7 rerun from scratch with a new seed. Unsupported cells were 25 percent in run 1 round 1, 0 percent in round 2 (not trustworthy), and 5 percent in run 2, against a 10 percent limit (same section).
- Run 2 re-fetched all 20 sampled papers with 0 mismatches (4 on title and year only), against 16 in run 1 (deliverables/number_checks.md, section 3). All 376 tag sentences and 10 of 10 project quotes passed (deliverables/validation_report.md, Run 2).

## What did not

- In run 2 the failing sample cell "never says single-chip", 3 of 27 category cells failed, and the piezo maturity cell is "the same cell and the same gap run 1 round 1 found" (deliverables/validation_report.md, Run 2).
- A blind second judge passed all 29, agreeing on 19 of 20 sample and 24 of 27 category cells, a split "Left for a human to settle" (deliverables/pitfalls_original_log.md, 15:10).
- arXiv rate limits blocked 9 of 10 phrase queries, leaving 47 records (STATUS.md, stage 1a line).
- About 99 of 149 flagged name keys are one person split into several records (deliverables/number_checks.md, section 2).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) leads the device routes with 43 core papers, reflecting how the sample was built, since one phrase supplied 27 of them (deliverables/number_checks.md, section 1).
- 101 of 267 core papers design networks without building a switch, and their AI (artificial intelligence) evidence reaches no cell (deliverables/comparison_matrix.md).
- Abstracts leave 32 of 126 matrix cells unreported, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. The standard for judged matrix cells.
3. Accept 267 core papers, not the planned 50 to 100, or cap them (deliverables/curation_report.md, CLAUDE.md).
4. How to get arXiv records.
5. Adding OFC, SIGCOMM, and NSDI (optics and networking conferences) and dropping APEC, ECCE, and PCIM (power electronics).
6. Who reads the ten papers in deliverables/reading_list.md.
7. Recruiting or partnering as the team map's goal.
