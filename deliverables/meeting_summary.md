# OCS landscape trial, week 1

## What was tried

We ran the optical circuit switching (OCS) pipeline on OpenAlex and arXiv on 2026-09-26, 04:32 to 07:42 (STATUS.md). A Workflow script ran eight role agents through nine stages and three numeric gates, and a checker agent verified each stage with code (PLAN.md, deliverables/architecture.md).

## What worked

- Every stage finished. Gate C passed on its second round after one matrix rework (deliverables/validation_report.md).
- Evidence held up. 376 of 376 tag sentences are verbatim, 16 of 16 re-fetched papers matched, and 10 of 10 project links still hold their quotes (deliverables/validation_report.md).
- The checker caught 3 wrong paper merges that no gate measures (STATUS.md, stage 2 RETRY line).
- OpenAlex usage stayed small, 0.033 USD (US dollars) after stage 1a (STATUS.md).

## What did not

- arXiv returned HTTP 429 and 406 errors on 9 of 10 phrases, leaving 47 records (STATUS.md, stage 1a line).
- The core set is 267 papers, not the planned 50 to 100 (deliverables/curation_report.md, CLAUDE.md).
- Audit round 1 failed the matrix check on 5 of 20 sampled cells, and "the pre-fix version of the test failed 21 of 82 cells before the rewrite" (deliverables/validation_report.md). The fix made the build use the audit's own test, so the checker called round 2 "circular" and read the 20 cells by hand (STATUS.md, stage 7 DONE line).
- Two audit problems stay open. 4 arXiv-only core papers "still have never been successfully re-checked against their source in either audit round" (deliverables/validation_report.md, round 2). On piezo:trl_band, the maturity cell of a route with 2 core papers, "The fix corrected what the cell asserts, not the thinness of its evidence base" (same file).
- 149 name keys map to several author records, splitting some people (deliverables/pitfalls.md, 06:32).

## What the small sample shows

- Silicon photonic MEMS (micro-electro-mechanical systems) is the largest device route with 43 core papers, and the top four authors all work on it (Q4 in deliverables/demo_results.md, graphs/top_pis.csv).
- 101 of 267 core papers design networks without building a switch, and their AI (artificial intelligence) cluster evidence reaches no matrix cell (deliverables/comparison_matrix.md).
- Abstracts cannot fill the matrix. 31 of 126 cells are not reported, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).

## Decisions needed next week

1. The scope of OCS (deliverables/open_questions.md).
2. Accept 267 core papers or add a cap.
3. How to get arXiv records.
4. Whether to add OFC, SIGCOMM, and NSDI (optics and networking conferences) and drop APEC, ECCE, and PCIM (power electronics).
5. Who reads the ten papers in deliverables/reading_list.md.
6. Whether the team map is for recruiting or partnering.
