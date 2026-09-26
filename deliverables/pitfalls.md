# Pitfalls log

This is the running log from the 2026-09-26 run, grouped by where the problem came from (the Windows host, OpenAlex, arXiv, the open web, or the pipeline's own logic) and then by stage. Each item gives the original timestamp, one line on what happened, and one line on what was done. Where several log lines describe the same problem, they are merged and every timestamp is listed. The original log, with its 119 entries unchanged line for line, is in deliverables/pitfalls_original_log.md (count of lines starting "- [" there), because it is not edited for style.

API means application programming interface. HTTP 429 means "too many requests" and HTTP 406 means "not acceptable". JSONL is JSON with one record per line. MEMS is micro-electro-mechanical systems.

## Windows host

### Preflight

- [2026-09-26 04:32] python -m venv puts the interpreter in .venv/Scripts, so every .venv/bin/python command in CLAUDE.md and PLAN.md would fail.
  Done. A shim at .venv/bin/python runs .venv/Scripts/python.exe with PYTHONUTF8=1, because the console's default code page breaks on non-ASCII titles.
- [2026-09-26 04:32] The first numpy import was blocked once by Windows Smart App Control ("DLL load failed").
  Done. Nothing, because the same import passed on retry.
- [2026-09-26 04:32] load_dotenv() with no path raised an AssertionError in find_dotenv when the script came from stdin.
  Done. Scripts call load_dotenv('.env') with the explicit path.
- [2026-09-26 04:32] There is no sqlite3 command-line tool on the machine.
  Done. Scripts and checks use Python's sqlite3 module.

## OpenAlex

### Stage 0 smoke test

- [2026-09-26 04:38, 04:41] The collector logged "returned zero new records" for 'optical circuit switch'. The stage 0 check found 5 records in the file and a rerun that added 0 new (STATUS.md, 04:41), so these lines record reruns skipping records already on disk.
  Done. Nothing. The message does not tell "no results" apart from "already on disk", which is worth fixing.

### Stage 1a full pull

- [2026-09-26 04:43, 05:04] 6 anchor titles were logged as unresolved. The checker found 4 of them (Mission Apollo, TPU v4, Lightwave Fabrics, TopoOpt) already in openalex.jsonl from phrase queries, because the script logs any anchor already on disk as a miss.
  Done. Not fixed. The data is right and only the log is wrong. True misses are Jupiter Evolving and RotorNet.
- [2026-09-26 05:39] The c-Through anchor matched a 1999 paper titled "OPTICS", because rapidfuzz token_set_ratio scores 100 when one title's words are a subset of the other's.
  Done. Not fixed, because the record scored 0 and does not affect Gate A. True anchor count is 10 of 13.

### Stage 1c snowball

- [2026-09-26 05:30] A rerun of the snowball doubled its output from 150 to 300 records, because each seed's counter restarted at 0, and an unstable sort changed which works were picked.
  Done. Counters now start from the records already on disk and the sort is explicit. Three reruns stayed at 150 records with 0 new and 0 USD (US dollars).

### Stage 8 write-up

- [2026-09-26 07:50] collect_openalex.py adds up the API's cost field for the snowball but no file stores it.
  Done. Not fixed. The run's OpenAlex cost is known only up to stage 1a, 0.033 USD (STATUS.md, stage 1a line).

## arXiv

### Stage 0 smoke test

- [2026-09-26 04:37, 04:39, 04:40] The smoke query 'optical circuit switch' got HTTP 406 on every retry, twice, and logged zero new records three times.
  Done. A rerun at 04:40 got 5 of 5 records. No code change, the existing retries are the only mitigation.

### Stage 1a full pull

- [2026-09-26 04:43 to 05:01] 9 of 10 phrase queries failed after 3 attempts with HTTP 406 or 429, in two passes, which is 18 failure lines plus 19 "zero new records" lines.
  Done. Not fixed. A rerun after a 45 second cooldown got 429 on every query (05:02). arxiv.jsonl holds 47 records, all from 'optical circuit switch', and the collector recommended a longer delay per request.
- [2026-09-26 05:04] collect_arxiv.py has no anchor title lookup, although PLAN.md stage 1a asks each collector to search the anchors.
  Done. Not fixed, passed to the orchestrator.

### Stage 7 audit

- [2026-09-26 07:22, 07:39] Check (a) could not re-fetch 4 arXiv-only core papers, because export.arxiv.org returned HTTP 406 on an id_list lookup, also outside the script.
  Done. Recorded as errors and left out of the rate in both rounds. The checker later matched title and year for all 4 from arxiv.org/abs pages (STATUS.md, stage 7 DONE line).

## Web (scout and audit fetches)

### Stage 5 scout

- [2026-09-26 06:10] microsoft.com research pages returned a "high demand" page on every fetch.
  Done. Microsoft Sirius was dropped and has no row.
- [2026-09-26 06:10] lightmatter.co is rendered by JavaScript, so a plain fetch returns an empty shell, and datacenterdynamics.com is behind Cloudflare.
  Done. The Lightmatter row uses a secondary analyst article (futurumgroup.com), noted in projects.csv.
- [2026-09-26 06:10] globenewswire.com timed out on the UTStarcom press release.
  Done. Used the financialcontent.com mirror of the same release.
- [2026-09-26 06:10] graphs/top_institutions.csv did not exist yet, because stage 4 was still running.
  Done. No leads were drawn from it.

### Stage 7 audit

- [2026-09-26 07:22] Check (c) read pages with no charset header as ISO-8859-1, which garbled curly apostrophes and made a real Drut Technologies quote look absent.
  Done. The script sets resp.encoding to resp.apparent_encoding, and 10 of 10 rows pass.

## Pipeline logic (no outside source)

### Stage 1b relevance scoring

- [2026-09-26 05:08, 05:12, 05:13, 05:18, 05:31, 05:36, 05:37] Tagger progress notes (scripts written, batches exported and scored, some records scored from title only).
  Done. No problem to fix.
- [2026-09-26 05:18, 05:20] Batch 017 was almost all piezoelectric materials papers (energy harvesting, biosensors), and batch 028 was soft robotics and composites, which is query noise on the words piezo, fiber, and actuator.
  Done. All scored 0. The queries were not changed.
- [2026-09-26 05:21] data/raw/*.jsonl has Unicode line-separator characters inside strings, so str.splitlines() splits records and json.loads fails. Also 7 score 1 records have no adjacent_field and will stay out of the extended set.
  Done. JSONL is read line by line on newline only. No data changed.

### Stage 2 curation

- [2026-09-26 05:47] Authors with no OpenAlex ID are merged only when they share an institution, and arXiv gives no institutions, so 63 same-name appearances stay split.
  Done. Kept on purpose, because merging two people is worse than splitting one.
- [2026-09-26 05:47] 1543 author appearances listed more than one institution on the same paper, and paper_authors stores only the first (1550 after the rerun, deliverables/curation_report.md).
  Done. Not fixed. The table holds one affiliation per paper and author.
- [2026-09-26 05:51, 05:55] 3 of 16 fuzzy-title merges joined different papers (the same subset flaw as c-Through), and one of them moved a score 2 paper into the core set.
  Done. Merges now also need token_sort_ratio of at least 90. 12 fuzzy merges remain, the 3 bad ones and one harmless pair are split, and core stays at 267. This narrows the playbook rule and is pending approval.
- [2026-09-26 05:57] 2 core pairs share a title but are 2 and 4 years apart, so the year rule keeps them split. The ICTCP pair is probably one paper, also left split.
  Done. Not fixed. They may double count in the graphs.

### Stage 3 tagging

- [2026-09-26 06:08, 06:14, 06:16, 06:22, 06:26] Many papers got tech_route unclear (20, 22, and 17 of 60 in three reports), because reviews and adjacent papers name no single mechanism. Null-abstract papers were tagged from the title at low confidence.
  Done. Nothing guessed. Evidence sentences were cut from the abstract by code, so none had to be retyped.
- [2026-09-26 06:26] One fragment did not match on W2124700175, because the abstract had a lowercase "this paper presents" mid-sentence.
  Done. Fixed and rerun, and all 60 spans in that set passed.

### Stage 4 graphs

- [2026-09-26 06:32, 06:33, 06:36 (three lines)] 149 name keys map to more than one author ID, which likely splits one person into several nodes. This comes from the stage 2 author rule. The same line was logged 5 times by an unguarded function.
  Done. Logging fixed to once at 06:37 and the extra lines kept. The split people are not fixed.
- [2026-09-26 06:36, 06:46] The plotly bundle made coauthor.html 5.96 MB, over the 5 MB cap, and the first fix loaded a separate plotly.min.js, which broke the page when copied alone.
  Done. The page is now plain inline SVG (scalable vector graphics) with no plotly, self-contained, at a few hundred KB.
- [2026-09-26 06:46] 301 authors with no affiliation were collapsed into one "unknown" institution that topped top_institutions.csv on fake bridges.
  Done. The institution graph now has no "unknown" node. author_id and member_author_ids columns were added for 76 repeated display names.

### Stage 6 matrix

- [2026-09-26 07:06] The stored abstract of W3041044413 gives a port count that disagrees with its title.
  Done. Its port count was not used.
- [2026-09-26 07:06] The stored abstract of W3215039088 has a garbled polarization dependent loss figure.
  Done. The cell is not_reported_in_abstract and the paper is on the reading list.
- [2026-09-26 07:06] Several abstracts carry markup debris such as /spl times/ and $\mu{\rm s}$.
  Done. The CSV keeps quotes verbatim and the Markdown folds them to ASCII.
- [2026-09-26 07:06] unidecode maps the Greek letter mu to "m", which would turn microseconds into milliseconds.
  Done. matrix_render.py maps mu to "u" first.
- [2026-09-26 07:06] Neither core piezo paper says piezo in its abstract, so the piezo row rests on tagger inference and a vendor page.
  Done. Noted in the cells.
- [2026-09-26 07:06] Mordia (W2002555923) is tagged lcos, but its abstract never names LCoS.
  Done. Confidence low, and the paper is on the reading list.
- [2026-09-26 07:06] 17 of 101 architecture_only core abstracts name accelerators or ML (machine learning), but none carries a secondary route, so this evidence reaches no ai_cluster_fit cell.
  Done. Not fixed, it is a stage 3 gap. Counted in comparison_matrix.md.
- [2026-09-26 07:06] SOA (semiconductor optical amplifier) abstracts give extinction ratio, not crosstalk.
  Done. Crosstalk left not reported, and a person should decide whether extinction ratio may stand in.
- [2026-09-26 07:06] 4 companies cells are no_source, because no project row has those routes, and 3 project rows with route unclear reach no cell.
  Done. Left as is.
- [2026-09-26 07:06 (two lines)] academic_groups has large ties at the top-5 cutoff on small routes, and split people can undercount a lead author. The second line corrects the piezo tie description.
  Done. Ties broken by top_pis.csv order and the tie count is in each cell note.
- [2026-09-26 07:36] The 5 cells that failed audit round 1 held bare codes (lab, partial) whose quote gave the signal only implicitly, and the same test failed 21 of 82 reported cells.
  Done. matrix_build.py now stops unless every value shares a word or number with its quote, using the audit's own test. Category values now carry their quote words.
- [2026-09-26 07:36] piezo trl_band said "production (vendor)", but no quote states a sale.
  Done. Downgraded to lab. A person should check the Polatis page before raising it.
- [2026-09-26 07:36] companies cells quoted the first project row even when the quote did not name the entity.
  Done. They now quote the first row that names its entity. The lcos and robotic_patch_panel cells are hand-written, and the build checks their row numbers.
- [2026-09-26 07:36] The Coherent quote says digital liquid-crystal and never says LCoS, so its lcos route is the scout's assignment.
  Done. Confidence lowered to low, with a note asking for a human check.

### Stage 7 audit

- [2026-09-26 07:22] The first draft of check (b) failed by construction on ranges and on category values, with a 70 percent fail rate.
  Done. Rewritten as a word or number overlap test that also accepts project row quotes, and the rate fell to 25 percent.
- [2026-09-26 07:39] Round 2 passed all four checks with the same samples.
  Done. Round 2 was appended to validation_report.md and round 1 left unchanged.
- [2026-09-26 07:28, 07:42, from STATUS.md, not the original log] The checker found that validation_report.md miscounts project-row cells (says 7, actual 3), overstates how many failures sit on thin routes (1 of 5, not 4), and says piezo:trl_band cites row 5 when the CSV cell cites no row. It also found that check (b) is now circular, because the build and the audit share one test.
  Done. Not fixed in the report. The checker read all 20 sampled cells by hand and found all 20 supported.

### Stage 8 write-up

- [2026-09-26 07:50] The query field in the raw files credits each record to the first query that found it.
  Done. demo_results.md labels records per query as first-found counts.
- [2026-09-26 07:50] 53 of 267 core papers have no venue.
  Done. Every venue count in the write-up says it is an undercount.
- [2026-09-26 08:07, from STATUS.md, not the original log] The checker sent stage 8 back once. framework.md, demo_results.md, and open_questions.md were over their word limits. meeting_summary.md left out the auditor's open piezo problem, neither it nor demo_results.md had the auditor's "21 of 82" count, and 46 lines of the unedited log in this file put a colon after the agent name (STATUS.md, stage 8 RETRY line).
  Done. The files were cut, inline queries moved to the query table in demo_results.md, the auditor's words were added, and the original log moved unchanged to deliverables/pitfalls_original_log.md.

## Pitfalls that will get worse at scale

- arXiv rate limits. 9 of 10 phrase queries already failed at this size, so more phrases need slower pacing or another route to arXiv records.
- OpenAlex metered cost. More queries and snowball rounds cost more, and the snowball cost was not even saved, so cost must be logged per stage.
- Fuzzy-title dedup. Pairs to compare grow with the square of the record count, and the subset flaw already caused 3 wrong merges in 885 papers.
- Split people. 149 name keys already map to more than one author, and the count grows with every source that lacks author IDs or affiliations.
- Blocked web pages. JavaScript rendering, Cloudflare, throttling, and a timeout already blocked 4 sites for a scout run of 12 entities.
- Hand checks. The only real test of matrix values is now a person or checker reading cells, which does not scale with the matrix.
- Log noise. Repeated lines (44 lines from the arXiv collector, 5 copies of the split-person line) already make the log hard to read.
