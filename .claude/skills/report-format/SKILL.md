---
name: report-format
description: Templates, length limits, style rules, and traceability rules for the six meeting deliverables (architecture, framework, demo results, pitfalls, open questions, meeting summary). Load this before writing or editing anything in deliverables/ other than the matrix and the validation report, and whenever asked to summarize the run for a meeting.
---

# Report format

The audience is a manager and a few colleagues who will decide next week whether to continue this work and how to expand it. They want to know whether the method works and whether the data can be trusted. They do not want a polished literature review yet. Write for a reader who has ten minutes.

## Style rules (these matter, the reader flagged them)

- Plain words. If a term needs to be technical, define it the first time.
- Short paragraphs, three or four sentences.
- No em dashes anywhere. Use a comma, a period, or parentheses.
- Do not write a claim followed by a colon followed by the evidence. Write two sentences, or join them with "because", "so", or "which means".
- Only characters on a plain keyboard. No accented letters in names (write Gimenez, not the accented form), no curly quotes, no arrows, no bullet characters other than "-".
- Every number is followed by where it came from, in parentheses, like "(graphs/top_pis.csv)" or "(query in pipeline/graph.py, line 40)". A number without a source is a defect.
- Say what did not work as plainly as what did.

## deliverables/architecture.md (under 900 words plus the diagram)

```
# Multi-agent architecture

## What the pipeline does, in one paragraph

## Agent roster
A table with columns: agent, model, tools, reads, writes, one-line purpose. One row for the orchestrator (main session) and one per subagent, taken from .claude/agents/*.md.

## Data flow
A mermaid flowchart (```mermaid fence) from sources through raw JSONL, relevance, database, tags, graphs, scout, matrix, audit, write-up. Show the three gates as diamonds.

## Gates and what they catch
Gate A, B, C in three short paragraphs, with the thresholds.

## Why this shape
Three or four sentences on why pipeline plus validation rather than free-form agents, and why subagents rather than a framework this week.

## What changes to add IEEE Xplore, PCIM, patents, or company data
One paragraph per addition. Which agent changes, what new skill is needed, what the cost or quota problem is.
```

## deliverables/framework.md (under 700 words)

```
# Analysis and comparison framework

## Tagging rubric
The tech route values, TRL bands, AI fit values, adjacent fields, each with one line. Say that every tag carries a verbatim evidence sentence.

## Comparison matrix
The dimensions and the cell rules, and the status values, in plain words.

## Adjacent-field logic
Why the team map reaches into telecom, LiDAR, silicon photonics, and displays, and how the tagger decides.

## What the framework cannot do from abstracts alone
```

## deliverables/demo_results.md (under 1200 words plus tables)

```
# Small-sample demo results

## Numbers
Records pulled per source and per query. Duplicates removed by method. Core set size, extended set size. Papers with no abstract. Every number with its source file.

## Technology map
Papers per tech route, per TRL band, per AI fit value. A short paragraph on what the distribution suggests and what it does not.

## Team map
Top 15 rows of graphs/top_pis.csv as a table. Top 10 institutions. Cluster summary from graphs/clusters.csv. A link to graphs/coauthor.html. A paragraph naming which groups are core and which are adjacent, and why that matters for the "transferable teams" question.

## Early project map
The projects.csv table, sorted by stage then date.

## Comparison matrix
Include deliverables/comparison_matrix.md by reference and paste the top-level table. Count of cells by status.

## Audit results
The four checks, the rates, pass or fail, from validation_report.md.
```

## deliverables/pitfalls.md

Take the running log and group it by source (OpenAlex, arXiv, web) and then by stage. For each pitfall, one line for what happened and one for what was done. Keep the original timestamps. End with a short list of the pitfalls that will get worse at scale.

## deliverables/open_questions.md (under 500 words)

Number the questions. At minimum cover the scope of "OCS" (do hyperscaler white papers and blog posts count, do optical packet switches count), whether OFC, SIGCOMM and NSDI should be added and why they may matter more than APEC, ECCE and PCIM, which parts need a human to read full texts, whether the "transferable teams" goal is for recruiting or partnering (it changes the team map), what to do about IEEE Xplore's quota and PCIM's lack of an API, and the fact that OpenAlex now requires a free API key and meters usage (about 1 USD per day free), which the assignment document did not anticipate and which changes the cost picture for a full-scale run.

## deliverables/meeting_summary.md (one page, under 450 words)

```
# OCS landscape trial, week 1

## What was tried
## What worked
## What did not
## What the small sample shows (three bullets, each with a source)
## Decisions needed next week (numbered)
```
