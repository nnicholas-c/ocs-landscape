# Open questions

1. What counts as optical circuit switching (OCS)? Hyperscaler blog posts are outside OpenAlex and arXiv, yet a Google blog post (data/projects.csv, row 1) backs the mems_3d production band. Optical packet switches count only as adjacent (ocs-domain skill), yet soa and electro_optic switch in nanoseconds or less (deliverables/comparison_matrix.csv).

2. Should OFC, SIGCOMM, and NSDI be targeted? The ocs-domain skill names OFC (Optical Fiber Communication Conference) for hardware and SIGCOMM and NSDI (networking systems conferences) for data center designs. This run found 9 core papers from OFC and 0 from SIGCOMM or NSDI (query Q11 in deliverables/demo_results.md), an undercount, since 53 of 267 core papers lack a venue (query Q3, same file).

3. Do APEC (Applied Power Electronics Conference), ECCE (Energy Conversion Congress and Expo), and PCIM (a power electronics conference) belong at all? This run found 0 papers from these power electronics venues, as expected (query Q11; ocs-domain skill). They fit only if switch power joins the scope.

4. Which parts need a person reading full texts? The ten papers in deliverables/reading_list.md target the 32 cells no abstract reports (deliverables/comparison_matrix.csv). A person should check the Polatis page behind the piezo production value and whether Coherent's switch is LCoS, liquid crystal on silicon (same file, piezo trl_band note; deliverables/pitfalls.md, stage 6).

5. Is the "transferable teams" goal for recruiting or partnering? About 99 of 149 flagged name keys (range 62 to 126) are one person split into several author records (deliverables/number_checks.md, section 2). Recruiting ranks individuals, so splits need merging by hand first. Partnering uses groups, which is safer, though split people add small false communities (STATUS.md, 14:24 line).

6. What must a judged matrix cell meet? The auditor, reading quotes only, failed 4 of 29 judged cells, and the blind checker, reading abstracts too, passed all 29 (deliverables/pitfalls_original_log.md, 15:10).

7. How do we handle IEEE Xplore and PCIM? IEEE Xplore's API (application programming interface) has a key and a daily quota (report-format skill), so a full pull may span days. PCIM has no API, so it needs a manual export or a scout-style web agent.

8. OpenAlex now requires a free API key and meters usage, with about 1 USD (US dollar) per day free (CLAUDE.md), which the assignment document did not anticipate. Stage 1a cost 0.030 USD (STATUS.md) and the snowball cost was never saved (deliverables/pitfalls.md, stage 8), so a full run needs a per-stage cost log.

9. Is a core set of 267 acceptable, and how many phrases per route? The trial aimed for 50 to 100 (CLAUDE.md), but above 200 Gate A keeps every score 3 paper (PLAN.md; deliverables/curation_report.md). Route counts follow the phrases too, as one phrase supplied 27 of 43 papers on the largest device route (deliverables/number_checks.md, section 1).

10. How do we get arXiv records? 9 of 10 arXiv phrase queries failed on rate-limit errors (STATUS.md, stage 1a line). Options are slower pacing, arxiv.org/abs pages, which served all 4 audit lookups (deliverables/validation_report.md, round 3), or OpenAlex.
