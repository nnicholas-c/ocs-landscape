# OCS landscape pipeline

## What this repo does

We are mapping optical circuit switching (OCS) for AI data centers. Three outputs are wanted. A map of the switching technologies and how they compare, a map of the research teams that work on OCS or on fields whose skills transfer into OCS, and a map of early-stage projects and companies. This week is a small-sample trial. Two free sources only (OpenAlex and arXiv), 50 to 100 core papers, the full pipeline run end to end, and an honest account of what broke. The point of the trial is to show that the multi-agent design works and that the data can be trusted. A polished report is not the goal this week.

PLAN.md is the script. STATUS.md is the checkpoint file. The four skills in .claude/skills hold the domain knowledge. The eight subagents in .claude/agents do the work.

## Who does what

The main session is the orchestrator. It reads PLAN.md, delegates each stage to the subagent named there, checks the stage's "done when" condition and its gate, appends a line to STATUS.md, ticks the box, and moves to the next stage. It does not read raw JSONL files, does not call the APIs, and does not write pipeline code itself. When a stage can run in parallel (PLAN.md says which), it launches those subagents together.

Subagents do exactly one stage each, write their outputs to the paths in PLAN.md, and return a summary of at most five lines with the file paths. They never paste data back into the main session.

## Hard rules for every agent

1. Numbers come from code or from a source sentence, never from memory. A count, a year, a citation number, a port count, a loss figure, or any other number appears in an output only if a script computed it or if it is copied from a source abstract with the exact source sentence attached. There is no third way. If you are about to type a number you believe is true, stop, and either compute it or mark it "not reported".

2. Every claim carries its provenance. A matrix cell carries the paper IDs it came from. A sentence about a team or an institution carries the paper IDs or the CSV row it came from. A project row carries the URL of the evidence and the date the evidence was written.

3. Empty means empty. When the sources do not say, the field says "not reported in abstract" or "unknown". Never fill a gap with a plausible guess. A visibly empty cell is a finding. A guessed cell is a defect.

4. Return paths, not data. When a subagent finishes, it reports where the output is and how many rows it has. It does not echo rows back.

5. Log pitfalls as they happen. Every API error, rate limit, missing field, suspicious match, and dead end goes into deliverables/pitfalls.md as an appended line with the stage and the time. This file is one of the deliverables, so a pitfall that is fixed still gets logged.

6. Scope is frozen for this run. OpenAlex and arXiv only. No IEEE Xplore, no Crossref, no PCIM, no patent databases, no paid data. The scout stage is capped in time and in entity count. Do not expand scope even if it seems easy.

7. The audit gate is mandatory. Nothing in stage 8 is written until stage 7 has passed. If the audit fails twice, the run stops and STATUS.md says why.

8. Resume, do not redo. If STATUS.md shows a stage as done, skip it unless a gate sent you back to it. Stage scripts must be safe to run twice. Running a collector twice must not duplicate records, and loading the database twice must not duplicate rows.

9. Writing style for everything in deliverables/. Plain words. Short paragraphs. No em dashes. Do not write a sentence that makes a claim, then a colon, then the evidence, rewrite it as two sentences or join them with "because" or "so". Only characters you can type on a plain keyboard, so no accented letters, curly quotes, or arrows. Define an abbreviation the first time it appears.

10. Stage scripts live in pipeline/, are plain Python, and are run from the repo root with `.venv/bin/python -m pipeline.<module>`. They read configuration from pipeline/queries.yaml and .env, and never hardcode an email or a path outside the repo.

## Environment

The virtual environment is .venv and the packages are in requirements.txt. If a package is missing, install it into .venv and add it to requirements.txt. OPENALEX_API_KEY in .env is a free OpenAlex key, required for every OpenAlex call (pass it through pyalex's config.api_key). The free tier is about 1 USD of usage per day. Full-text search calls cost 0.001 USD each, list and filter calls 0.0001 USD, single-record lookups nothing. The whole run should cost under 0.10 USD, so if a script is spending more than that something is looping. Prefer per_page=100, prefer singleton lookups for re-fetches, and never put a search call inside a per-record loop. arXiv needs no key.

## Data contract

pipeline/schema.sql is the single source of truth for table names and columns. Add a column there before you use it anywhere. The identity of a paper is paper_id, which is the OpenAlex work ID when one is known and otherwise the arXiv ID with the prefix "arxiv:". Raw pulls go to data/raw as JSONL, one JSON object per line, with the raw API response kept in a field called raw so nothing is lost. The curated database is data/db/papers.sqlite. Temporary batch files for tagging go in data/work and are not deliverables.

## STATUS.md format

One line per stage event, appended under "## Log". `- [YYYY-MM-DD HH:MM] stage N <name> DONE|FAILED|RETRY. <row counts>. <problems, or "none">`. Tick the stage's checkbox at the top when the "done when" condition and the gate are both met.
