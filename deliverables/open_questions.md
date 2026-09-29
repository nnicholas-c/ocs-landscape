# Open questions

Unmarked numbers are run 2's.

1. What counts as optical circuit switching (OCS)? A Google blog post outside both sources backs mems_3d production (data/projects.csv, row 1), and optical packet switches are only adjacent (ocs-domain skill), though soa and electro_optic switch in nanoseconds or less (deliverables/comparison_matrix.csv).

2. Should we target OFC (Optical Fiber Communication Conference), SIGCOMM, and NSDI (networking systems conferences), which the ocs-domain skill names for switches and data center designs? The data has 9, 0 and 0 core papers from them, an undercount, as 53 of 284 lack a venue (deliverables/demo_results.md, Q11 and Q3).

3. Do APEC, ECCE, and PCIM (power electronics conferences) belong? The data has none, and they fit only if switch power enters scope (Q11; ocs-domain skill).

4. What needs a person reading full texts? The 33 cells no abstract reports (deliverables/reading_list.md picks ten papers for them), piezo maturity on the Polatis page, and whether Coherent's switch is LCoS, liquid crystal on silicon (deliverables/comparison_matrix.csv, piezo trl_band note; deliverables/pitfalls.md, stage 6).

5. Is the "transferable teams" goal for recruiting or partnering? About 59 (29 to 94) of 147 flagged name keys hide one split person, from 6 of 15 sampled (deliverables/number_checks.md, Run 2, section 2). Recruiting needs splits merged by hand, so partnering is safer.

6. What must a judged cell meet? Reading quotes only, the auditor failed 4 of 29 cells in run 1's round 3 and 3 of 30 in run 2's anchor-papers audit, while the blind second judge failed none (deliverables/pitfalls_original_log.md, 15:10 and 21:21).

7. How do we handle IEEE Xplore's daily API (application programming interface) quota, which may spread a full pull over days (report-format skill), and PCIM, which lacks an API and needs manual export?

8. OpenAlex now requires a free API key and meters use, about 1 US dollar free daily, unforeseen by the assignment (CLAUDE.md). Run 1 cost 0.0404 dollars (STATUS.md, 16:14 note), but the snowball's share went unsaved (deliverables/pitfalls.md, stage 8), so a full run needs per-stage cost logs.

9. Is a 284-paper core set acceptable (deliverables/curation_report.md)? The trial aimed for 50 to 100 (CLAUDE.md), but above 200 Gate A keeps every score 3 paper (PLAN.md).

10. How should a full-scale run get arXiv records? In run 1, export.arxiv.org refused 9 of 10 phrase queries, and one-at-a-time probing was refused too (STATUS.md, stage 1a line; deliverables/pitfalls_original_log.md, 15:54). OpenAlex's arXiv index gave only 6 of 40 run 1 arXiv-only papers an OpenAlex identifier (deliverables/curation_report.md), which leaves arXiv's bulk metadata snapshot.

11. OpenAlex truncates the Jupiter Evolving and RotorNet titles at the colon, so they fail the title check (data/work/step2_anchors.md) and await the doi_publisher_confirmed method after the meeting (issue #13).

12. An append-only audit log accumulated inconsistencies over six rounds, so a full-scale run should write one report per round (deliverables/validation_report.md, Gate C summary headings).

13. Agents and the owner, not a person reading evidence, made three post-run checks. A person should confirm 4 split authors and 4 wrong merges before recruiting (deliverables/demo_results.md, Reviews after the run).
