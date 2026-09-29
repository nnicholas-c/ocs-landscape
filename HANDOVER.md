# Handover to Yuxuan

For Yuxuan (GitHub liu0029yuxuan), who has write access (`gh api repos/nnicholas-c/ocs-landscape/collaborators`, role_name "write"). Every number is copied from the file or command named next to it. HANDOVER.zh-CN.md is a Chinese draft, and this file is authoritative.

## 1. What this is and where it stands

An agent-driven pipeline that maps optical circuit switching (OCS) for AI data centers from OpenAlex and arXiv, as maps of technologies, teams and projects. It is a week-one, small-sample trial, not a finished report (README.md). Runs 1 and 2 are done and all nine stages in STATUS.md are ticked. Run 2 has 1211 papers, 284 of them core (deliverables/curation_report.md, lines 48 and 100). When this was written, master was at b861015, the merge of #21 (`git log -1 --format=%h origin/master`). The tags are run1 (8172417), run1-fixed (874ee9c), run2-early-wip (6ad1c6f) and run2-final (commit 908917f) (`git ls-remote --tags origin`). To present, use deliverables/meeting_summary.md (the one-pager), MEETING_PREP.md (speaking order and likely questions) and SUMMARY-2026-09-27.md (what is on master and what needs a person).

## 2. Getting set up

1. `gh repo clone nnicholas-c/ocs-landscape`.
2. Python 3.11 or newer (README.md, Setup). `python -m venv .venv`, then `.venv/bin/pip install -r requirements.txt` (Windows: `.venv\Scripts\pip`).
3. Get your own free OpenAlex key at https://openalex.org/settings/api, `cp .env.example .env`, and set OPENALEX_API_KEY. The owner's key is never committed, because .env is gitignored (.gitignore, line 4).
4. On Windows, follow the shim note in README.md, Setup. It makes .venv/bin/python run .venv/Scripts/python.exe with PYTHONUTF8=1, so non-ASCII titles do not crash the console.
5. Deterministic steps are in README.md, "Running the deterministic steps", with the rebuild order from committed data. Judgement stages are in README.md, "Running the judgement stages". They need an agent host that loads CLAUDE.md, .claude/agents and .claude/skills, and gives the scout web search and fetch (README.md, line 124).
6. To resume, open an agent session at the repo root and ask it to follow PLAN.md from the first unticked stage in STATUS.md (README.md, same section). Every stage is ticked now, so the next run starts from a PLAN-run3.md, which is not written yet (section 4 says what goes in it).

## 3. How work is done here

- Every change goes on a branch, then a pull request.
- A code review is posted on the pull request (#1 and #17 show the usual form).
- Fix the findings on the branch and say in a comment what was fixed.
- Merge with a merge commit (`git log --merges origin/master`).
- STATUS.md, deliverables/pitfalls_original_log.md and deliverables/validation_report.md are append-only. Correct an old line with a new line, never an edit (STATUS.md, line 3; deliverables/pitfalls_original_log.md, line 5; deliverables/validation_report.md, line 1981).
- No number from memory. A number comes from a script or a quoted source sentence, and a gap stays "not reported" (CLAUDE.md, hard rules 1 and 3).
- The second judge checks each stage. A separate agent reruns the stage's checks and gate in code before it counts, and re-judges audit cells blind (deliverables/meeting_summary.md, line 5). Its instructions are not in the repo yet (README.md, Second judge), so write them down before run 3.

Merged pull requests (`gh pr list --state merged --json number,title`): #1 run 2 via OpenAlex's arXiv index; #4 step 2, anchor papers; #6 step 3, technology map and timeline; #7 step 4, number checks; #8 step 5, one-pager from run 2; #9 step 6, README and CONTRIBUTIONS; #12 step 7, validation_report.md corrections; #15 step 7, one-pager cut; #17 step 7, owner option B edits; #18 step 8, SUMMARY-2026-09-27.md; #19 meeting prep sheet; #21 post-run agent checks. #1 to #17 each carry a posted review, #18 and #21 a verifier comment, #19 neither (`gh pr list --state merged --json number,comments,reviews`).

## 4. Open work, in order

1. **Issue #13 first.** Add Jupiter Evolving (DOI 10.1145/3544216.3544265) and RotorNet (DOI 10.1145/3098822.3098838) with the match method doi_publisher_confirmed. ACM Digital Library pages refuse scripts with HTTP 403, and that block must not be worked around (issue #13, comment of 2026-09-27T08:51:29Z). So a person confirms title, venue, year and first author in a browser (or through another in-scope source). That step is done. Both ACM pages were checked in a browser on 2026-09-28, and both papers match the OpenAlex records step 2 found (issue #13, comment of 2026-09-29T05:55:29Z). A script then fetches the OpenAlex record by DOI, a free lookup, and accepts it when OpenAlex's cut title is a prefix of the full title and year and first author match. This reruns stages 6 to 8 with a new seed and the blind second judge (issue #13).
2. **Issue #20 next.** 4 fuzzy-title merges joined different publications (deliverables/curation_report.md, lines 69, 70, 71 and 80). Decide the policy first. Either each publication is its own paper, or a conference and journal version count as one work. If separate, add a guard to pipeline/curate.py so records with different non-null DOIs never fuzzy-merge, then rerun stage 2 onward (issue #20). One rerun of stages 2 to 8 can then cover #13 too.
3. **The rest** (`gh issue list --state open`):
   - #14. Leftover inconsistencies in validation_report.md, kept by the owner's decision.
   - #10. "0 SIGCOMM core papers" mostly reflects missing venues, since 15 of 53 no-venue core papers carry an ACM DOI (issue #10).
   - #5. The member order in graphs/clusters.csv depends on PYTHONHASHSEED.
   - #3. curate drops arXiv IDs from merged records when the kept record has none.
   - #2. Backfill OpenAlex records for arXiv-only papers with free DOI lookups.

After the meeting, write the eight decisions into a PLAN-run3.md before any new run (deliverables/meeting_summary.md, lines 50 to 57). They are the scope of OCS, accepting 284 core papers or a cap, the standard for "supported" category cells, the arXiv route, the venues, who reads the reading list, recruiting or partnering, and the OpenAlex budget.

## 5. For Yuxuan specifically

- Review deliverables/meeting_summary.zh-CN.md and MEETING_PREP.zh-CN.md. Both are drafts and the English files are authoritative (the note at the top of each).
- README.zh-CN.md still translates README.md as of commit 5a25410 (its header note), which is before run 2 (CONTRIBUTIONS.md, line 5; README.md, line 182). It needs a full refresh. Its line 140 still says "ying he" (pander to). Per the review comment on pull request #15, the owner prefers "zuan ziji shenji de kongzi" (gaming its own audit), as in deliverables/meeting_summary.zh-CN.md, line 34.
- CONTRIBUTIONS.md is your file. The owner added one marked note at line 5, saying README.zh-CN.md is from 5a25410 and README.md is current. Update or remove it when you refresh README.zh-CN.md.
- The branch feat/chinese-project-pages (head f3c1a29) has no pull request (`gh pr list --head feat/chinese-project-pages --state all` is empty). Its run 2 data is pinned to commit 3859702, before stages 6 to 8 (site/README.md, line 29, on that branch). It shows 1213 papers (site/assets/data.js, line 32, on that branch), while master has 1211 (deliverables/curation_report.md, line 48). Rebuild its data from current master, then open a pull request.

## 6. Known limits

- deliverables/open_questions.md, the 13 open questions.
- Issue #14, the accepted leftovers in deliverables/validation_report.md.
- The two judges split on 3 of 27 category cells, and 12 free-text cells were never judged (README.md, Findings to know before using the data).
- About 59 (29 to 94) of 147 flagged name keys hide one split person, so use the team map at group level (deliverables/number_checks.md, Run 2, section 2).
- Two agents, not a person, checked the top 20 authors (16 one person, 4 split) and the 13 fuzzy-title merges (9 same paper, 4 different, issue #20), merged in #21 (deliverables/demo_results.md, Reviews after the run; data/work/agentcheck_final.md). A person should confirm the 4 splits and 4 wrong merges before the team map is used for recruiting (deliverables/open_questions.md, item 13).

## 7. What is not in the repo

- The owner's .env with the OpenAlex key.
- The local virtual environment, .venv.
- The orchestration scripts, the second judge's instructions and the scratch files used during the runs. README.md, Second judge, says the judge's instructions are not in the repo yet. Most of data/work/ is gitignored too (.gitignore, line 6).
