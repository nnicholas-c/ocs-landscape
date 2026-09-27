# Step 2, anchor papers

Method for all three: found the DOI by web search from a primary source (ACM
Digital Library or the publisher), then fetched the work from OpenAlex with a
free singleton call `Works()["https://doi.org/<doi>"]` (cost_usd 0.000 for
all three, confirmed from the run). Title check used rapidfuzz
`token_sort_ratio` on normalized titles (lowercased, punctuation stripped),
not `token_set_ratio`, per instructions, because `token_set_ratio` scores 100
whenever one title's words are a subset of the other's -- the exact bug that
let the stage 1a anchor search accept a 1999 "OPTICS" paper as a false match
for c-Through (see deliverables/pitfalls_original_log.md, stage 1 Gate A
checker, 2026-09-26 05:39).

## Finding: OpenAlex title truncation

For all three anchors, OpenAlex's `title` field (== `display_name`, no
fuller field exists on the record) holds only the words before the colon in
the real title, with the subtitle dropped entirely:

| Anchor title | OpenAlex title |
|---|---|
| Jupiter Evolving: Transforming Google's Datacenter Network via Optical Circuit Switches and Software-Defined Networking | Jupiter evolving |
| RotorNet: A Scalable, Low-complexity, Optical Datacenter Network | RotorNet |
| c-Through: Part-time Optics in Data Centers | c-Through |

Because of this, `token_sort_ratio` scores 24, 23, and 35 respectively --
all well under the 95 threshold -- even though each fetch is unambiguously
the right paper. The identity is not in question here the way it was for the
OPTICS false match: that record came from a full-text title *search* (wrong
paper, high score). These three records came from a *DOI* taken from a
verified primary source, so the fetch itself already pins the paper; the low
score only reflects OpenAlex's incomplete title metadata.

Confirmation used instead of the raw score: the OpenAlex title, normalized,
is an exact leading word-prefix of the anchor title, normalized (true for
all three -- this is the signature of a dropped subtitle, not a different
paper), cross-checked against publication year and author list for the two
that were appended:

- Jupiter Evolving (W4290990894): year 2022, authors led by Leon Poutievski,
  Omid Mashayekhi, Joon Suan Ong ... (23 authors) -- matches the known
  SIGCOMM '22 Google paper.
- RotorNet (W2743429249): year 2017, authors William Maxwell Mellette, Rob
  McGuinness, Arjun Roy, Alex Forencich, George C. Papen, Alex C. Snoeren ...
  (7 authors) -- matches the known SIGCOMM '17 UCSD paper.
- c-Through (W2097926925): DOI is byte-for-byte the same
  (10.1145/1851182.1851222) as the record already on disk from the stage 1c
  snowball, so identity needs no further cross-check.

This is a judgment call, logged for the checker/orchestrator to review, not
a silent override: the automated 95-threshold check as literally specified
fails for all three, and the reason (title truncation, not a wrong paper) is
recorded here rather than assumed.

## Per-anchor record

### Jupiter Evolving: Transforming Google's Datacenter Network via Optical Circuit Switches and Software-Defined Networking

- DOI: 10.1145/3544216.3544265
- Found at: https://dl.acm.org/doi/10.1145/3544216.3544265 (ACM SIGCOMM 2022 Conference proceedings page)
- OpenAlex W id: W4290990894
- Title check: token_sort_ratio 23.88 (fail at 95); truncated-title prefix match confirmed (see above); year and author list cross-checked against the known paper
- record_key `openalex:W4290990894`: not found in any existing data/raw/*.jsonl file
- Action: appended to data/raw/openalex.jsonl, source "openalex", query "anchor:Jupiter Evolving: Transforming Google's Datacenter Network via Optical Circuit Switches and Software-Defined Networking"

### RotorNet: A Scalable, Low-complexity, Optical Datacenter Network

- DOI: 10.1145/3098822.3098838
- Found at: https://dl.acm.org/doi/10.1145/3098822.3098838 (ACM SIGCOMM 2017 Conference proceedings page)
- OpenAlex W id: W2743429249
- Title check: token_sort_ratio 23.19 (fail at 95); truncated-title prefix match confirmed (see above); year and author list cross-checked against the known paper
- record_key `openalex:W2743429249`: not found in any existing data/raw/*.jsonl file
- Action: appended to data/raw/openalex.jsonl, source "openalex", query "anchor:RotorNet: A Scalable, Low-complexity, Optical Datacenter Network"

### c-Through: Part-time Optics in Data Centers

- DOI: 10.1145/1851182.1851222
- Found at: https://dl.acm.org/doi/10.1145/1851182.1851222 (ACM Digital Library page, "c-Through: part-time optics in data centers")
- OpenAlex W id: W2097926925
- Title check: token_sort_ratio 35.29 (fail at 95); truncated-title prefix match confirmed (see above); DOI is an exact match to the record already on disk
- record_key `openalex:W2097926925`: already present in data/raw/openalex_snowball.jsonl (source "openalex_snowball", query "snowball:W2141810662")
- Action: not appended, logged as already present

## Cost

Sum of meta.cost_usd across the three DOI singleton fetches: 0.000000 (as
expected -- singleton lookups by ID/DOI are free per the playbook).

## Idempotency check

Re-ran the fetch script a second time: all three anchors resolved to
"already_present" (the two just-appended plus c-Through), 0 new records
appended, data/raw/openalex.jsonl unchanged at 709 lines.

## Decision

Made by the orchestrator when step 2 resumed after BLOCKED.md.

- Jupiter Evolving and RotorNet are NOT confirmed and are NOT added. The title check (normalized token_sort_ratio of at least 95 between the anchor title in pipeline/queries.yaml and the paper's title) could not be met for either. OpenAlex stores only the words before the colon ("Jupiter evolving", "RotorNet"). The ACM Digital Library pages return HTTP 403 to automated fetches, and that must not be worked around. Web search result titles are also truncated ("Jupiter Evolving: Transforming Google's Datacenter Network ...", "RotorNet | Proceedings of ..."). Crossref is out of scope (CLAUDE.md rule 6). The queue's step 2 says to log any anchor that cannot be confirmed and move on, and its rules never allow loosening a check, so the prefix, year and author cross-check above is not accepted as a substitute.
- The two appended lines (openalex:W4290990894 and openalex:W2743429249) were removed. data/raw/openalex.jsonl was restored to exactly `git show origin/master:data/raw/openalex.jsonl`, after confirming those two lines were the only difference, and a byte comparison afterward matched.
- For a human decision, the identifiers are kept here. Jupiter Evolving has DOI 10.1145/3544216.3544265 and OpenAlex id W4290990894. RotorNet has DOI 10.1145/3098822.3098838 and OpenAlex id W2743429249. The open question is whether a DOI taken from the publisher's listing is enough to confirm identity when the title check cannot be run on a full title.
- c-Through is already present as openalex:W2097926925 (data/raw/openalex_snowball.jsonl, from the snowball), so it needs no addition.
- openalex:W2160642098 ("OPTICS", 1999) in data/raw/openalex.jsonl still carries the c-Through query from run 1's title search. Raw files are never edited, so that record stays as it is. The correct c-Through record is openalex:W2097926925.
