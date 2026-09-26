# OCS landscape pipeline

A scaffold for running the "optical circuit switching for AI data centers" analysis as one continuous Claude Code session. Claude Code's main session acts as the orchestrator, eight subagents in `.claude/agents` do the work, four skills in `.claude/skills` hold the domain knowledge, and `PLAN.md` is the script the run follows. Every stage writes its output to disk, so the run can be stopped and resumed.

This week's scope is deliberately small. OpenAlex and arXiv only, 50 to 100 core papers, the whole pipeline run end to end, and an honest record of what broke. The deliverables are a methodology write-up plus small-sample demo results for next week's meeting, not a finished report.

## What you need

- Python 3.11 or newer
- Claude Code installed and signed in
- Internet access. arXiv needs nothing. OpenAlex needs a free API key (see setup step 3). That is a change from what the assignment document assumes, and it is worth mentioning at the meeting.

## Setup, once

1. Put this folder somewhere and make it a git repo.

       git init && git add . && git commit -m "scaffold"

2. Create the Python environment and install packages.

       python -m venv .venv
       source .venv/bin/activate        (Windows: .venv\Scripts\activate)
       pip install -r requirements.txt

3. Get a free OpenAlex API key and put it in `.env`. Make an account at https://openalex.org, copy the key from https://openalex.org/settings/api, then copy `.env.example` to `.env` and paste the key into `OPENALEX_API_KEY`. Since early 2026 OpenAlex meters its API. A free key gives about 1 USD of usage a day, a full-text search costs a tenth of a cent, and single-record lookups are free, so this week's entire run costs a few cents. Without a key you get a tenth of that budget and the run will hit 429 errors partway through.

4. Open a terminal in this folder and start Claude Code.

       claude

## Starting the run

Paste this as your first message.

> Read CLAUDE.md and PLAN.md. Execute every stage in PLAN.md in order, delegating each stage to the subagent named there. Update STATUS.md after every stage. Never skip a gate. Stop only when every file listed under stage 8 in PLAN.md exists, or when a gate has failed twice.

Then leave it alone. Expect several hours of wall-clock time. The collectors wait between API calls on purpose.

## Resuming after an interruption

> Read STATUS.md and PLAN.md. Continue from the first stage that is not ticked. Do not redo ticked stages.

## If it keeps stopping to ask permission

`.claude/settings.json` pre-approves the tools the run needs. If prompts still appear, either click "always allow for this project" a few times, or start with

       claude --dangerously-skip-permissions

but only inside a container or a VM you would not mind losing. Never use that flag on a machine that holds anything you care about.

## What comes out

Everything for the meeting lands in `deliverables/`.

- `architecture.md`, the agent roster, data flow, gates, and a diagram
- `framework.md`, the tagging rubric and the comparison matrix design
- `demo_results.md`, the numbers, the team map, the project map, the matrix
- `comparison_matrix.md` and `.csv`, every cell with its source
- `reading_list.md`, ten papers a human should read in full
- `validation_report.md`, what the auditor checked and found
- `pitfalls.md`, what broke and what was done about it
- `open_questions.md`, what to decide next week
- `meeting_summary.md`, one page

Graphs land in `graphs/` (open `coauthor.html` in a browser). The curated database is `data/db/papers.sqlite`.

## Folder map

    CLAUDE.md                 rules every agent follows
    PLAN.md                   the stages, outputs, and gates the orchestrator executes
    STATUS.md                 checkpoint file, ticked as stages finish
    README.md                 this file
    requirements.txt          Python packages
    .env.example              copy to .env, add your email
    .claude/settings.json     tool permissions so the run does not pause
    .claude/agents/           eight subagents: collector, curator, tagger, grapher, scout, analyst, auditor, writer
    .claude/skills/           ocs-domain, openalex-arxiv-playbook, comparison-framework, report-format
    pipeline/schema.sql       the database contract
    pipeline/queries.yaml     search phrases, anchor papers, snowball settings (edit here, not in code)
    pipeline/*.py             written by the agents during the run
    data/raw/                 JSONL pulls from each source
    data/db/                  papers.sqlite
    data/work/                temporary batch files for tagging (not deliverables)
    graphs/                   graphml, csv rankings, coauthor.html
    deliverables/             everything for the meeting

## Editing before you start

Two files are worth a look before the first run. `pipeline/queries.yaml` holds the search phrases and the anchor papers, and `.claude/skills/ocs-domain/SKILL.md` holds the technology taxonomy and the seed company list. Both are opinions written to get the trial moving, not settled facts, and the run is told to verify anchors and seed companies rather than trust them.

## What is out of scope this week, on purpose

IEEE Xplore (needs a key and has a small free quota), PCIM (no API at all), patents, paid company data, and full-text reading. Crossref is also skipped this week because OpenAlex already carries DOIs and reference lists. The `open_questions.md` deliverable is where the run records what adding each of these would take.
