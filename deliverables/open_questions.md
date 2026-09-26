# Open questions

1. What counts as optical circuit switching (OCS)? Hyperscaler blog posts are not in OpenAlex or arXiv, yet the Google row in data/projects.csv (row 1) is a blog post and part of the evidence for the mems_3d production band. Optical packet switches count only as adjacent (ocs-domain skill), yet the soa and electro_optic rows report nanosecond switching (deliverables/comparison_matrix.csv). We need a rule for both.

2. Should OFC, SIGCOMM, and NSDI be targeted? The ocs-domain skill names OFC (Optical Fiber Communication Conference) for switch hardware and SIGCOMM and NSDI (networking systems conferences) for data center designs. This run searched by phrase and found 9 core papers from OFC and 0 from SIGCOMM or NSDI (query Q11 in deliverables/demo_results.md). These undercount, because 53 of 267 core papers have no venue (query Q3, same file).

3. Do APEC (Applied Power Electronics Conference), ECCE (Energy Conversion Congress and Expo), and PCIM (a power electronics conference) belong at all? They are power electronics venues, so a low count is expected and is not a recall problem (ocs-domain skill). This run found 0 papers from them (query Q11). They belong only if switch power or packaging joins the scope.

4. Which parts need a person reading full texts? The ten papers in deliverables/reading_list.md were picked to fill as many as possible of the 31 cells no abstract reports (deliverables/comparison_matrix.csv). A person should also check the Polatis shop page and whether the Coherent switch is really LCoS, liquid crystal on silicon (deliverables/pitfalls.md, 07:36).

5. Is the "transferable teams" goal for recruiting or partnering? Recruiting needs individuals, so the 149 split author records (deliverables/pitfalls.md, 06:32) and current affiliations must be fixed first. Partnering needs groups, so graphs/clusters.csv matters more.

6. How do we handle IEEE Xplore and PCIM? IEEE Xplore's API (application programming interface) needs a key and has a daily call quota (report-format skill), so a full pull must count calls and may span days. PCIM has no API, so it needs a manual export or a web agent under the scout's link-and-quote rule.

7. OpenAlex now requires a free API key and meters usage, with about 1 USD (US dollar) per day free (CLAUDE.md), which the assignment document did not anticipate. Stage 1a cost 0.030 USD (STATUS.md), but the snowball cost was never saved (deliverables/pitfalls.md, stage 8). A full-scale run needs a per-stage cost log.

8. Is a core set of 267 acceptable? The trial aimed for 50 to 100 (CLAUDE.md), but Gate A's rule above 200 keeps every score 3 paper (PLAN.md), giving 267 (deliverables/curation_report.md). We either accept that or add a cap.

9. How do we get arXiv records reliably? 9 of 10 arXiv phrase queries failed on HTTP 429 and 406 errors (STATUS.md, stage 1a line). Options are slower pacing, or taking arXiv papers through OpenAlex, which already supplies some (4 core papers have the venue 'arXiv (Cornell University)', query Q11).
