# Open questions

Numbers are run 2's unless marked run 1.

1. What counts as optical circuit switching (OCS)? A Google blog post, outside OpenAlex and arXiv, backs the mems_3d production band (data/projects.csv, row 1). Optical packet switches count only as adjacent (ocs-domain skill), yet soa and electro_optic switch in nanoseconds or less (deliverables/comparison_matrix.csv).

2. Should OFC (Optical Fiber Communication Conference), SIGCOMM, and NSDI (networking systems conferences) be targeted? The ocs-domain skill names them for switch hardware and data center designs. The data has 9 core papers from OFC and 0 from SIGCOMM or NSDI (Q11 in deliverables/demo_results.md), an undercount, since 53 of 284 core papers lack a venue (Q3).

3. Do APEC, ECCE, and PCIM (power electronics conferences) belong at all? The data has none, as expected (Q11; ocs-domain skill). They fit only if switch power joins the scope.

4. Which parts need a person reading full texts? The ten papers in deliverables/reading_list.md target the 33 cells no abstract reports (deliverables/comparison_matrix.csv). A person should also check the Polatis page for piezo maturity, and whether Coherent's switch is LCoS, liquid crystal on silicon (same file, piezo trl_band note; deliverables/pitfalls.md, stage 6).

5. Is the "transferable teams" goal for recruiting or partnering? In run 1, about 99 of 149 flagged name keys were one person split across records (deliverables/number_checks.md, section 2), and run 2 flags 147 (STATUS.md, 16:47 line). Recruiting ranks individuals, so splits need merging by hand. Partnering uses groups, which is safer.

6. What must a judged matrix cell meet? In run 1's round 3 the auditor, reading quotes only, failed 4 of 29 judged cells, and the blind second judge failed none (deliverables/pitfalls_original_log.md, 15:10). In the run 2 audit after the anchor papers (seed 20260929) it was 3 of 30 against 0 (same file, 21:21).

7. How do we handle IEEE Xplore and PCIM? IEEE Xplore's API (application programming interface) has a daily quota (report-format skill), so a full pull may span days, and PCIM has no API, so it needs a manual export.

8. OpenAlex now requires a free API key and meters usage, with about 1 USD (US dollar) per day free (CLAUDE.md), which the assignment document did not anticipate. Run 1 cost 0.0404 USD (STATUS.md, 16:14 note), but the snowball's share of it was never saved (deliverables/pitfalls.md, stage 8), so a full run needs a per-stage cost log.

9. Is a core set of 284 acceptable (deliverables/curation_report.md)? The trial aimed for 50 to 100 (CLAUDE.md), but above 200 Gate A keeps every score 3 paper (PLAN.md).

10. How do we get arXiv records at full scale? In run 1, export.arxiv.org returned HTTP (web protocol) errors 406 or 429 on 9 of 10 phrase queries (STATUS.md, stage 1a line). A later one-at-a-time probe got 406 every time, so pacing was not the cause (deliverables/pitfalls_original_log.md, 15:54). Run 2 used OpenAlex's arXiv index, labelled arxiv_via_openalex, but only 6 of 40 run 1 arXiv-only papers gained an OpenAlex identifier (deliverables/curation_report.md). The full-scale option is arXiv's official bulk metadata snapshot.
