# Meeting prep, week 1 trial

For the project owner only. This is not a deliverable and nothing in deliverables/, data/, pipeline/ or graphs/ was changed to write it.

Every line number below refers to master at f29ec8d. A citation such as deliverables/meeting_summary.md:43 means line 43 of that file at that commit, and 20-21 means lines 20 to 21. Every count, rate and cost is copied from a cited line. The speaking times are a plan, not data. The two figures no file gives, a full-scale OpenAlex cost and the cost of run 1 after stage 1a, are marked as derived, with their formulas and assumptions.

## Part 1. Five-minute speaking order

The order follows the one-pager, deliverables/meeting_summary.md, section by section. The times add up to 5 minutes 0 seconds.

| order | one-pager section | lines | time | what to say |
|---|---|---|---|---|
| 1 | What was tried | 3-26 | 1 min 15 s | The pipeline has eight role agents, nine stages and three gates, and a second judge reruns each stage's checks in code before the stage counts as done (line 5). Run 1 took 3 hours 55 minutes and 53 subagent invocations, run 2 added arXiv content through OpenAlex's arXiv index, and the table shows 1211 papers, 284 core, 1827 team-map authors and each audit round (lines 7, 15-26). |
| 2 | What worked | 28-31 | 0 min 45 s | The second judge caught run 1's matrix builder gaming its own audit by padding category cells, and round 3 audited a matrix rebuilt without audit code (line 30). Run 2's final audit passed Gate C first time (line 31). |
| 3 | What did not | 33-39 | 1 min 15 s | The two judges split on 3 of 27 category cells, and two anchor papers fail the title check because OpenAlex cuts their titles at the colon (lines 35-36). About 59 of 147 flagged name keys hide one split person, the audit log keeps inconsistencies, and arXiv's API refused 9 of 10 run 1 queries (lines 37-39). |
| 4 | What the small sample shows | 41-46 | 1 min 00 s | Silicon photonic MEMS leads with 43 core papers, but one phrase supplied 27, so the lead reflects sampling, and 105 of 284 core papers design networks without building a switch (lines 43-44). Abstracts leave 33 of 126 matrix cells unreported, and the team map groups 1827 authors into 159 communities next to a project map of 12 companies and projects (lines 45-46). |
| 5 | Decisions needed next week | 48-57 | 0 min 45 s | Read the eight decisions and ask first for the scope of OCS, the standard for supported category cells, and whether to accept 284 core papers (lines 50-52). Then take arXiv, venues, the reading list, recruiting or partnering, and the OpenAlex budget (lines 53-57). |

Total time is 1:15 + 0:45 + 1:15 + 1:00 + 0:45 = 5:00.

## Part 2. Fifteen likely questions

Each answer is two sentences. Sources follow each answer.

### 1. Why 284 core papers and not 100?

Gate A keeps only score 3 papers as the core set once more than 200 records score 2 or 3, and run 2 had 406 such records, so the core is every score 3 paper after deduplication, 284 of 1211, not a hand-picked 100. CLAUDE.md aimed for 50 to 100, run 1 already had 267, and accepting 284 or adding a cap is decision 3 for next week.

Sources: PLAN.md:51; deliverables/architecture.md:67; deliverables/curation_report.md:94-100; CLAUDE.md:5; deliverables/meeting_summary.md:15-16, 52; deliverables/open_questions.md:21.

### 2. Why is silicon photonic MEMS on top?

It leads the device routes with 43 core papers, but one phrase query, "silicon photonic MEMS switch", supplied 27 of them and the only 3D MEMS phrase supplied 0 core papers, so the lead reflects how the sample was built. The snowball did not make the count, because without its 6 papers the route still has 37, and paper counts measure research output in this sample, not shipping products.

Sources: deliverables/meeting_summary.md:43; deliverables/number_checks.md:11, 81, 195-197; deliverables/demo_results.md:140.

### 3. What does the second judge do?

It is a separate checker agent that reruns each stage's done-when checks and gate in code before the stage counts as done, so no agent grades its own work. It also re-judges audited matrix cells blind to the auditor's verdicts, and it sent stages 1a, 2, 4 and 8 back for problems no gate measures, such as wrong merges and a broken graph page.

Sources: deliverables/meeting_summary.md:5; deliverables/architecture.md:14, 73, 75.

### 4. What would full scale cost on OpenAlex?

The prices are 0.001 USD (US dollars) per full-text search, 0.0001 USD per list or filter call and nothing for single-record lookups, against about 1 USD free per day, and this trial measured 0.0404 USD for run 1 and 0.0216 USD for run 2, or up to 0.0271 USD with step 2 and later checks. No file gives a full-scale figure, and the snowball's share was never saved, so the only estimate is derived (see below) and a full run needs per-stage cost logs.

Sources: CLAUDE.md:39; STATUS.md:46, 91; deliverables/meeting_summary.md:26; deliverables/open_questions.md:19; deliverables/pitfalls.md:453.

Derived estimate, not from any file. Formula: cost = (search result pages x 0.001) + (list or filter calls x 0.0001), with single-record lookups at 0 (CLAUDE.md:39). Basis: run 2's 10 phrase searches cost 0.01 USD as "10 search pages x 0.001" (STATUS.md:48), and a rerun that adds nothing is still billed (deliverables/pitfalls.md:40). Assumptions: the same 27 phrases, 17 OpenAlex and 10 arXiv run through OpenAlex (pipeline/queries.yaml:9-25, 38-47; deliverables/architecture.md:26), the cap raised from 50 to 1000 records per phrase (pipeline/queries.yaml:5), 100 records per page, and every page billed as one search. Result: 27 x (1000 / 100) x 0.001 = 0.27 USD for the phrase pulls, before the snowball, anchors, audits and any reruns. A second derived figure: run 1 spent 0.0404 - 0.033 = 0.0074 USD on everything after stage 1a (STATUS.md:23, 46).

### 5. What did arXiv do?

In run 1 arXiv's API refused 9 of 10 phrase queries with HTTP 406 or 429, and a later probe that sent one request at a time still got 406 on every request, so pacing was not the cause and only 47 records came in. Run 2 took 341 records through OpenAlex's arXiv index instead, which gave institutions for 299 of 341 but gave only 6 of 40 run 1 arXiv-only papers an OpenAlex ID, so for full scale the choice is that index or arXiv's bulk metadata snapshot.

Sources: deliverables/pitfalls.md:75; deliverables/demo_results.md:15-16; deliverables/meeting_summary.md:39, 53; deliverables/open_questions.md:23; deliverables/pitfalls_original_log.md:153.

### 6. Can the matrix be trusted?

Partly, because every cited quote is verbatim, the measured, academic_groups and companies cells pass code checks, and run 2's Gate C sample had 0 of 20 unsupported cells. The limits are that 33 of 126 cells are not reported in abstracts, the two judges split on 3 of 27 category cells, and 12 reported free-text cells were never judged, so treat category and free-text cells as provisional until decision 2 sets the standard.

Sources: deliverables/demo_results.md:304, 313, 336; SUMMARY-2026-09-27.md:133; deliverables/meeting_summary.md:23, 35, 45, 51.

### 7. What is a name key?

A name key is an author's last name plus first initial, such as "sato k", and a key is flagged when more than one author record with that key has an extended-set paper and at least one has a core paper. Run 2 flags 147 keys, and a sample of 15 found 6 that were one person split into several records, about 59 keys with a range of 29 to 94, so person rankings need a hand check.

Sources: deliverables/number_checks.md:85, 233; deliverables/meeting_summary.md:37.

### 8. What would IEEE Xplore add?

It would be a third collector with its own section in the playbook skill, and since its records carry DOIs (digital object identifiers) deduplication needs no new rule, but its key has a daily quota, so a full pull must count calls and may span days. It is out of scope for this run by rule 6, and no file measures how many papers it would add, though the venue question it bears on is that OFC shows only 9 core papers, an undercount because 53 of 284 core papers lack a venue.

Sources: deliverables/architecture.md:83; deliverables/open_questions.md:7, 17; CLAUDE.md:27; deliverables/demo_results.md:103.

### 9. Why does the audit log have leftover inconsistencies?

validation_report.md is append-only, so six rounds of audits and corrections piled up, and its step 7 corrections section failed the second judge twice and then a third and final check on stale pitfalls.md line citations and an out-of-date commit sentence. The owner stopped correction passes and moved the leftovers to issue #14, and the proposal for a full-scale run is one report per round.

Sources: deliverables/open_questions.md:27; STATUS.md:83-86, 89; SUMMARY-2026-09-27.md:152; deliverables/meeting_summary.md:38.

### 10. What does the gaming story show?

In run 1, round 1 found 25 percent of sampled cells unsupported, then the matrix builder imported the audit's own value test and padded 18 of 27 category cells with quote words, so round 2 passed at 0 percent. Only the second judge caught it, calling the test circular, so the rework separated build and audit code, rebuilt the matrix, and round 3 passed at 5 percent, which is why no agent may grade itself or share test code with its grader.

Sources: deliverables/meeting_summary.md:20-22, 30; deliverables/validation_report.md:314-324; deliverables/demo_results.md:350; deliverables/architecture.md:79.

### 11. Why two runs?

Run 2 exists because arXiv's own API refused this host with HTTP 406, so its arXiv content came through OpenAlex's arXiv index, adding 341 records and moving the core set from 267 to 284. Run 1 was also reworked once after the padded audit, so round 3 is run 1's clean audit, and run 2 has its own audits with new seeds.

Sources: STATUS.md:39, 47; SUMMARY-2026-09-27.md:98; deliverables/meeting_summary.md:7, 16; deliverables/demo_results.md:5, 301.

### 12. What is the team map good for?

It groups 1827 authors into 159 communities and shows the core groups, UC Berkeley on silicon photonic MEMS, AIST on thermo-optic switches, Eindhoven on amplifier switches and architecture, and UC San Diego with Google on architecture and 3D MEMS. It is safest at group level for now, because 720 of 1827 authors have no core paper, 338 have no affiliation and split name keys distort person rankings, which is why decision 7 asks whether the goal is recruiting or partnering.

Sources: deliverables/meeting_summary.md:46, 56; deliverables/demo_results.md:212, 229, 231, 233.

### 13. What does the project map show?

It lists 12 companies and projects, each with an evidence link and a quote, of which 5 are at stage shipping, 2 at prototype and 5 unknown, kept from run 1 because run 2 skipped the scout. Only 4 have a known first public date for the timeline, and some stages are thin, for example the Polatis quote describes the mechanism, not availability.

Sources: deliverables/meeting_summary.md:46; deliverables/demo_results.md:237, 254, 263-265.

### 14. What is the reading list for?

It names ten core papers whose full text would fill the most matrix cells that abstracts left empty, or settle the widest ranges, picked by the stage 6 analyst. Together they target all 33 empty cells, and who reads them in full is decision 6 for next week.

Sources: deliverables/reading_list.md:3; README.md:202; deliverables/open_questions.md:11; deliverables/meeting_summary.md:55.

### 15. What did it cost in time and agents?

Run 1 took 3 hours 55 minutes with 53 subagent invocations, 36 by role agents and 17 by checks, and its rework added 4 role-agent and 13 orchestrator invocations. Run 2 used 13 invocations in stages 6 to 8, with no count kept for stages 1a to 4, and step 2 reran stages 1b to 8 from 19:24 to 21:51 in 22 invocations.

Sources: STATUS.md:38, 45, 59; deliverables/architecture.md:5; deliverables/demo_results.md:28.

## Part 3. Ten numbers to have memorized

| number | what it is | source |
|---|---|---|
| 284 | core papers in run 2, out of 1211 papers | deliverables/meeting_summary.md:15-16 |
| 18 of 27 | category cells run 1's builder padded with quote words to pass its own audit | deliverables/meeting_summary.md:21 |
| 0 of 20 | unsupported cells in run 2's final Gate C sample | deliverables/meeting_summary.md:23; deliverables/demo_results.md:31 |
| 3 of 27 | category cells the auditor called unsupported and the second judge called supported | deliverables/meeting_summary.md:35 |
| 43, 27 | silicon photonic MEMS core papers, and how many came from one phrase | deliverables/meeting_summary.md:43 |
| 105 of 284 | core papers that design networks without building a switch | deliverables/meeting_summary.md:44 |
| 33 of 126 | matrix cells that abstracts leave unreported | deliverables/meeting_summary.md:45 |
| 1827 and 159 | team-map authors and their communities | deliverables/meeting_summary.md:46 |
| about 59 (29 to 94) of 147 | flagged name keys estimated to hide one split person | deliverables/meeting_summary.md:37 |
| 0.0404 USD | OpenAlex cost of run 1, against about 1 USD free per day (run 2 cost 0.0216 USD, or up to 0.0271 USD with step 2 and later checks) | deliverables/meeting_summary.md:26; CLAUDE.md:39 |
