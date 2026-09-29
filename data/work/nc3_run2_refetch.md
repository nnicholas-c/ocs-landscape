# Number check 3, run 2. Re-fetch sample for check (a)

Input is data/work/audit_s20260929_round1.json, the run 2 audit after the anchor papers (seed 20260929, generated_at 2026-09-27T04:06:18Z in that file). Every number below is printed by the code at the end of this note, which reads only the a_refetch block of that file and changes nothing. "(J: key)" after a number names the a_refetch key it comes from. Run the code from the repo root with `.venv/bin/python -` and the block on standard input. Two runs give the same output.

How a field counts as compared. In pipeline/audit.py check_a, a subcheck is set to None when the stored value or the re-fetched value is missing, and None counts as neither pass nor fail. So a field was compared on a paper only when its subcheck is true or false. The code also checks that its recount of drawn, compared and dropped equals the counts the audit wrote.

## Sample

- Drawn 20, compared 20, dropped 0 (J: drawn, compared, dropped, recounted from items result). 20 passed and 0 failed (J: items result).
- 18 were re-fetched by OpenAlex ID (identifier) and 2 by the free OpenAlex DOI (digital object identifier) singleton lookup on the arXiv DOI (J: items method). 0 used the arxiv.org/abs page fallback (J: items method).

## Compared on title and year only

2 papers were compared on title and year only, with cited_by_count and first institution both unavailable (J: items subchecks). They are arxiv:2604.22146 and arxiv:2507.12265, the 2 arXiv-only papers in the sample (J: items method). For both, the stored cited_by_count is null while OpenAlex returned 0 (J: items stored, refetched). So the count was skipped because our database holds no value for these papers, not because the source lacked one. This differs from round 3 of run 1, where the arXiv page itself had no count (deliverables/number_checks.md, section 3). The first institution is null on both sides for both papers (J: items stored, refetched).

## Each field

| Field | Compared | Not compared | Mismatched | Papers not compared |
|---|---|---|---|---|
| title | 20 | 0 | 0 | none |
| year | 20 | 0 | 0 | none |
| cited_by_count | 18 | 2 | 0 | arxiv:2604.22146, arxiv:2507.12265 |
| first_institution | 16 | 4 | 0 | W2951487609, W2260723393, arxiv:2604.22146, arxiv:2507.12265 |

(J: items subchecks)

Title and year were compared on all 20 sampled paper_ids (J: sampled_ids). cited_by_count was compared on the 18 papers with an OpenAlex ID, listed in the output below. first_institution was compared on 16 of them, all except W2951487609 and W2260723393, whose first author has no institution on either side (J: items stored, refetched). In total 74 of 80 possible field comparisons were made, and 0 mismatched (output below).

## What this means for the write-up

The Gate C row "20 drawn, 20 compared, 0 dropped" in deliverables/validation_report.md (run 2 audit after the anchor papers) matches the file. The sentence below it says 0 mismatches on title, year, cited_by_count or first institution "across all 20 papers". That is true for mismatches, but it can be read as all four fields compared on all 20. cited_by_count was compared on 18 and first institution on 16. validation_report.md is append-only, so any clarification must be appended.

## Code

```python
import json

PATH = "data/work/audit_s20260929_round1.json"
FIELDS = ("title", "year", "cited_by_count", "first_institution")
METHODS = ("openalex_id", "openalex_doi_singleton", "arxiv_html_fallback")

a = json.load(open(PATH, encoding="utf-8"))["a_refetch"]
items = a["items"]
assert [it["paper_id"] for it in items] == a["sampled_ids"]

dropped = [it["paper_id"] for it in items if it["result"] == "dropped"]
compared = [it for it in items if it["result"] in ("pass", "fail")]
assert len(items) == len(compared) + len(dropped)
assert (len(items), len(compared), len(dropped)) == (a["drawn"], a["compared"], a["dropped"])

# pipeline/audit.py check_a sets a subcheck to None when the stored or the
# re-fetched value is missing, so None means "not compared" (not a pass).
def ids(rows):
    return ", ".join(it["paper_id"] for it in rows) or "none"

print("drawn", len(items), "| compared", len(compared), "| dropped", len(dropped), "|", dropped or "none")
print("result", {r: sum(it["result"] == r for it in items) for r in ("pass", "fail", "dropped")})
for m in METHODS:
    rows = [it for it in compared if it["method"] == m]
    print("method", m, len(rows), "|", ids(rows))
ty_only = [it for it in compared
           if it["subchecks"]["cited_by_count"] is None and it["subchecks"]["first_institution"] is None]
print("title_and_year_only", len(ty_only), "|", ids(ty_only))
total = 0
for f in FIELDS:
    done = [it for it in compared if it["subchecks"][f] is not None]
    skip = [it for it in compared if it["subchecks"][f] is None]
    bad = [it for it in compared if it["subchecks"][f] is False]
    total += len(done)
    print(f"{f}: compared {len(done)} | not compared {len(skip)} | mismatched {len(bad)}")
    print("  compared ids:", ids(done))
    for it in skip:
        print("  not compared:", it["paper_id"], "stored", it["stored"][f], "refetched", it["refetched"][f])
print("field comparisons", total, "of", len(compared) * len(FIELDS))
```

## Output

```text
drawn 20 | compared 20 | dropped 0 | none
result {'pass': 20, 'fail': 0, 'dropped': 0}
method openalex_id 18 | W2889455810, W1997754090, W2951487609, W2116377381, W3089161534, W2490598172, W2047996703, W2797687360, W2049132385, W4380874786, W2121095819, W4281560993, W2063297543, W2583039042, W2260723393, W2735125579, W4205819848, W2316851065
method openalex_doi_singleton 2 | arxiv:2604.22146, arxiv:2507.12265
method arxiv_html_fallback 0 | none
title_and_year_only 2 | arxiv:2604.22146, arxiv:2507.12265
title: compared 20 | not compared 0 | mismatched 0
  compared ids: W2889455810, W1997754090, W2951487609, W2116377381, W3089161534, W2490598172, W2047996703, W2797687360, W2049132385, W4380874786, W2121095819, arxiv:2604.22146, W4281560993, W2063297543, W2583039042, W2260723393, W2735125579, W4205819848, W2316851065, arxiv:2507.12265
year: compared 20 | not compared 0 | mismatched 0
  compared ids: W2889455810, W1997754090, W2951487609, W2116377381, W3089161534, W2490598172, W2047996703, W2797687360, W2049132385, W4380874786, W2121095819, arxiv:2604.22146, W4281560993, W2063297543, W2583039042, W2260723393, W2735125579, W4205819848, W2316851065, arxiv:2507.12265
cited_by_count: compared 18 | not compared 2 | mismatched 0
  compared ids: W2889455810, W1997754090, W2951487609, W2116377381, W3089161534, W2490598172, W2047996703, W2797687360, W2049132385, W4380874786, W2121095819, W4281560993, W2063297543, W2583039042, W2260723393, W2735125579, W4205819848, W2316851065
  not compared: arxiv:2604.22146 stored None refetched 0
  not compared: arxiv:2507.12265 stored None refetched 0
first_institution: compared 16 | not compared 4 | mismatched 0
  compared ids: W2889455810, W1997754090, W2116377381, W3089161534, W2490598172, W2047996703, W2797687360, W2049132385, W4380874786, W2121095819, W4281560993, W2063297543, W2583039042, W2735125579, W4205819848, W2316851065
  not compared: W2951487609 stored None refetched None
  not compared: arxiv:2604.22146 stored None refetched None
  not compared: W2260723393 stored None refetched None
  not compared: arxiv:2507.12265 stored None refetched None
field comparisons 74 of 80
```
