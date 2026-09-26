# Stage 7 validation report

This report is produced by pipeline/audit.py. It runs the four checks in
PLAN.md stage 7 against a fixed random seed, SEED = 20260926, recorded in
the script and here so the sample can be reproduced. The script is
read only. It does not edit the database, the matrix, the tags table, or
projects.csv.

Round 1 failed Gate C on check (b) and sent the run back to stage 6 once,
per PLAN.md. Round 2 below reruns all four checks with the same seed,
after stage 6 fixed the failing matrix cells, to confirm Gate C now passes.
Round 1's results are kept exactly as first written; nothing in it has been
edited, removed, or softened.

---

## Round 1

Run at 2026-09-26T14:14 UTC (second run, after two script fixes described
under check (b) below; see deliverables/pitfalls.md for details). Raw JSON
output is saved at data/work/audit_round1.json.

### Gate C summary

| Check | Sample | Pass | Fail | Rate | Threshold | Gate C |
|---|---|---|---|---|---|---|
| (a) core paper re-fetch | 20 (16 usable, 4 errors) | 16 | 0 | 0 percent | at most 10 percent mismatches | PASS |
| (b) matrix cell evidence | 20 | 15 | 5 | 25 percent | at most 10 percent unsupported | FAIL |
| (c) project evidence URL | 10 | 10 | 0 | 0 percent | at most 20 percent failures | PASS |
| (d) evidence span substring | 376 (all tags rows) | 376 | 0 | 100 percent pass | at least 90 percent | PASS |

Three of four checks pass. Check (b) fails, at more than twice its
threshold. Per PLAN.md Gate C, this sends the run back to stage 6 (the
analyst) once with the failing list below, then stage 7 runs again. A
second failure on check (b) stops the run.

### Check (a). Re-fetch 20 random core papers

Method. 20 of the 267 core_set=1 papers were drawn with random.Random(SEED).
OpenAlex-known papers (16 of 20) were re-fetched by ID with
`Works()[openalex_id]`. arXiv-only papers (4 of 20) were re-fetched with
`arxiv.Search(id_list=[arxiv_id])`. Title (normalized), year, cited_by_count
(match if within 10 percent), and the first author's first institution
(when the source states one) were compared against the stored row. Any one
of these four differing counts as a mismatch for that paper.

Result. 16 of 20 could be re-fetched and compared. 0 of 16 mismatched on
any field (16 pass, 0 fail). Mismatch rate over the usable sample is 0
percent, well under the 10 percent gate.

Errors (not counted as pass or fail, listed separately from Gate C).
4 arXiv-only papers could not be re-fetched. They are arxiv:2603.28168,
arxiv:2507.08119, arxiv:2608.03146, and arxiv:2306.09713. All four failed
the same way, HTTP 406 from export.arxiv.org/api/query on an id_list lookup.
This was reproduced outside the script too, so it is a source-side or
network condition, not a script bug. It matches the HTTP 406/429 arXiv
flakiness stage 1a already logged in pitfalls.md against the same host.
None of the 4 papers has a database mismatch on record, since none of them
were compared; the finding is that they could not be checked this round.

### Check (b). 20 random matrix cells with status=reported

Method. Of the 126 comparison_matrix.csv rows, 82 carry status=reported.
20 of those 82 were drawn with random.Random(SEED). A cell fails if any
cited paper_id is missing from the papers table, if any cited project_rows
number is missing from projects.csv, if evidence_quote is not a verbatim
substring of a cited paper's stored abstract or of a cited project row's
evidence_quote (per the comparison-framework skill's own definition, since
7 of the 20 sampled cells cite a project row instead of a paper), or if the
cell's value shares no content word or number with its evidence_quote.

The value check was rewritten once before this run. The first draft
required the whole value string, or every digit in it, to appear verbatim
in the quote. That fails by construction for a range built from two papers,
for a controlled vocabulary code such as integrated_photonic (the code
itself never appears in prose, only the underlying words do), and for a
judgment-call dimension such as trl_band or ai_cluster_fit, whose value is
the analyst's read of the evidence rather than a term the source text uses.
The rewritten check passes when the value shares at least one real word
(3 or more letters, not a stopword) or number with the quote. This dropped
the measured fail rate from 70 percent to 25 percent. See
deliverables/pitfalls.md for the two script fixes made before this run
(the value check above, and a response-encoding bug in check (c)).

Result. 15 of 20 pass, 5 of 20 fail. Fail rate is 25 percent, over the 10
percent gate.

Failing cells.

- soa:ai_cluster_fit (papers W2056973550, W3093967660). Value is "partial".
  The quote describes the switch fabric's use case in general terms and
  never uses a word close to partial, yes, or no.
- electro_optic:integration (papers W2094700182, W1979338531). Value is
  "integrated_photonic". The quote describes a Mach-Zehnder switch in
  silicon but does not use the words integrated or photonic.
- mems_3d:integration (papers W3215039088, W2560361359). Value is
  "free_space_bulk". The quote describes a microlens and MEMS mirror array,
  which is free-space bulk optics by the framework's own definition, but
  the quote does not use the words free, space, or bulk.
- mems_silicon_photonic:trl_band (paper W3138799074, project row 8). Value
  is "lab". The quote describes CMOS foundry fabrication and does not use
  the word lab or a synonym.
- piezo:trl_band (project row 5, no paper_id). Value is "production
  (vendor)". The quote describes the switching mechanism only and does not
  use the word production.

All 5 failures are the same pattern. The evidence_quote genuinely supports
the paper or project being on-topic for the cell, and none of the 5 has a
missing paper_id, a missing project row, or a quote that fails the
substring check against its source. What fails is that trl_band and
ai_cluster_fit are judgment calls the analyst made by reading the whole
abstract or page, not values a single quoted sentence is expected to state
in those words, and the two integration failures are the same kind of gap
one level down (the quote supports the physical setup but never names the
category). This is a real property of how those cells were filled, not
noise in the check. Whether it should count against Gate C is the
orchestrator's call; this report states the raw numbers un-softened per
the auditor's rules.

### Check (c). 10 random projects.csv rows

Method. 10 of the 12 rows were drawn with random.Random(SEED). Each
evidence_url was fetched with a plain HTTP GET (no browser). A row fails if
the entity name or the evidence_quote (both lowercased, whitespace
collapsed to single spaces) is absent from the fetched page text. A page
that could not be fetched at all counts as unreachable, not a fail.

Result. 10 of 10 fetched successfully. 10 of 10 pass, 0 fail, 0
unreachable. Fail rate is 0 percent, under the 20 percent gate.

One row, Drut Technologies, initially looked like a fail on the first pass
of the script. The page's apostrophe character came back mangled because
requests defaulted to the ISO-8859-1 fallback encoding when the server sent
no charset header, and the mangled text no longer matched the stored quote.
Setting resp.encoding to resp.apparent_encoding before reading the page
text fixed it (see deliverables/pitfalls.md). After the fix this row
passes.

### Check (d). Evidence span substring check, all tags rows

Method. This check applies the same rule tag_import.py uses at load time to
every one of the 376 tags rows, not a sample. A row passes when
evidence_span is a verbatim substring of the paper's stored abstract, or
equal to the title when the abstract is null.

Result. 376 of 376 pass. Pass rate is 100 percent, over the 90 percent
gate.

### Other observations, not covered by the four checks (round 1)

4 of the 5 check (b) failures sit on tech routes with very few core papers
(piezo core count 2, lcos-adjacent mems_silicon_photonic:trl_band resting
on a single paper W3138799074 plus one project row). A judgment-call cell
built from one paper's abstract has no second source to average against,
so the same paraphrase gap would likely recur if the run were repeated on
a larger sample of these routes. This is consistent with, not new
information beyond, the small-sample nature of this trial.

The piezo:trl_band cell rests entirely on a vendor project row with no
paper_id at all. This is allowed by the framework (rule 4, vendor claim)
and the cell's own note already says so, but it means the "trl_band" for
piezo switches in the matrix is not backed by any peer-reviewed evidence
in the core set, only by a product page.

---

## Round 2

Run at 2026-09-26T14:37:16Z UTC, same SEED = 20260926, so every sample
below is identical to round 1's sample (checked item by item; see the
"Round 2 vs round 1" note under each check). Raw JSON output is saved at
data/work/audit_round2.json. This round follows Gate C's round 1 failure
on check (b), which sent the run back to stage 6. Stage 6's fix is logged
in deliverables/pitfalls.md at 07:36 (matrix_build.py now shares
pipeline.audit.value_in_quote with the audit script itself, cell quotes in
data/work/matrix_cells.yaml were rewritten to name the signal words their
quote gives, and piezo:trl_band was downgraded from "production (vendor)"
to "lab" because no quote states a sale or deployment).

### Gate C summary

| Check | Sample | Pass | Fail | Rate | Threshold | Gate C |
|---|---|---|---|---|---|---|
| (a) core paper re-fetch | 20 (16 usable, 4 errors) | 16 | 0 | 0 percent | at most 10 percent mismatches | PASS |
| (b) matrix cell evidence | 20 | 20 | 0 | 0 percent | at most 10 percent unsupported | PASS |
| (c) project evidence URL | 10 | 10 | 0 | 0 percent | at most 20 percent failures | PASS |
| (d) evidence span substring | 376 (all tags rows) | 376 | 0 | 100 percent pass | at least 90 percent | PASS |

All four checks pass. Gate C passes on round 2. No check needs a further
retry, and PLAN.md's "second failure stops the run" clause does not apply
because round 2 did not fail.

### Check (a). Re-fetch 20 random core papers

Method. Unchanged from round 1 (see above). Sample is identical to round 1
(same 20 paper_id values, verified programmatically against
data/work/audit_round1.json).

Result. 16 of 20 could be re-fetched and compared. 0 of 16 mismatched on
any field (16 pass, 0 fail). Mismatch rate is 0 percent, unchanged from
round 1.

Errors (not counted as pass or fail). The same 4 arXiv-only papers as round
1 (arxiv:2603.28168, arxiv:2507.08119, arxiv:2608.03146, arxiv:2306.09713)
failed the same way, HTTP 406 from export.arxiv.org/api/query on an
id_list lookup. This is unresolved and source-side, consistent with round
1's finding. Stage 6 does not touch stage 2's data, so this was not
expected to change, and it did not.

### Check (b). 20 random matrix cells with status=reported

Method. Unchanged from round 1 (see above). Sample is identical to round 1
(same 20 cells, verified programmatically).

Result. 20 of 20 pass, 0 of 20 fail. Fail rate is 0 percent, under the 10
percent gate.

All 5 cells that failed round 1 now pass: soa:ai_cluster_fit,
electro_optic:integration, mems_3d:integration,
mems_silicon_photonic:trl_band, and piezo:trl_band. Per
deliverables/pitfalls.md, the fix was at the source: quotes in
data/work/matrix_cells.yaml were rewritten to lead with the sentence that
names the signal word for the value (for example electro_optic:integration
now leads with the W1979338531 "monolithically integrated" quote), and
piezo:trl_band's value itself changed from "production (vendor)" to "lab"
because no quote in the core set or in projects.csv row 5 states a sale or
deployment. The same underlying test (matrix_build.py now imports
pipeline.audit.value_in_quote) was also run at build time against all 82
reported cells, not only the 20 sampled here; pitfalls.md records that the
pre-fix version of the test failed 21 of 82 cells before the rewrite, all
now fixed at the source rather than patched around this check.

### Check (c). 10 random projects.csv rows

Method. Unchanged from round 1 (see above). Sample is identical to round 1
(same 10 rows, verified programmatically).

Result. 10 of 10 fetched successfully. 10 of 10 pass, 0 fail, 0
unreachable. Fail rate is 0 percent, unchanged from round 1. The Drut
Technologies encoding fix from round 1 is already in the script this round
ran, so no new issue appeared.

### Check (d). Evidence span substring check, all tags rows

Method. Unchanged from round 1 (see above). Exhaustive, not sampled;
stage 6 does not touch the tags table so no change was expected here.

Result. 376 of 376 pass. Pass rate is 100 percent, unchanged from round 1.

### Other observations, not covered by the four checks (round 2)

Check (a)'s 4 arXiv HTTP 406 errors persist unchanged across both rounds
against the same 4 papers. They are not a Gate C fail (errors are excluded
from the rate, per PLAN.md and the auditor's rules), but they mean those 4
core papers still have never been successfully re-checked against their
source in either audit round. If a future run wants those 4 covered, the
fetch needs a different path than `arxiv.Search(id_list=...)` against
export.arxiv.org, since the same call fails outside the script too.

Round 1's observation about piezo:trl_band resting on a vendor page with no
peer-reviewed paper_id still applies in substance after the fix: the value
changed from "production (vendor)" to "lab", which is a lower and more
conservative claim, but the cell is still built from projects.csv row 5
(Polatis) plus one paper (W2591729902) whose abstract, per pitfalls.md,
does not use the word piezo. The fix corrected what the cell asserts, not
the thinness of its evidence base; that remains a property of the small
core-paper count on this route (2 core papers), same as round 1 noted for
the routes involved in all 5 failures.
