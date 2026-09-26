---
name: openalex-arxiv-playbook
description: How to pull paper metadata from OpenAlex (pyalex) and arXiv (the arxiv package), the exact raw record shape every collector must write, the rules for deduplicating and merging records across the two sources, and the known failure modes of both APIs. Load this before writing or running any collector, curator, or audit script, and whenever a script that talks to OpenAlex or arXiv misbehaves.
---

# OpenAlex and arXiv playbook

arXiv is free and needs no key. OpenAlex changed in early 2026 and now meters its API, so every call needs a free API key from openalex.org/settings/api, kept in .env as OPENALEX_API_KEY. The free key gives about 1 USD of usage per day. A full-text search call costs 0.001 USD, a list or filter call 0.0001 USD, and a single-record lookup by ID or DOI is free, so this week's run costs a few cents if written sensibly and a lot more if a search call ends up inside a loop. Both sources have quirks that will silently ruin the data if ignored. Read the whole file before writing a script. If a call fails with an unexpected parameter error, read the package's README or docstring rather than guessing parameter names, and log what you learned in pitfalls.md.

## Raw record shape

Every collector writes JSONL (one JSON object per line) with exactly these top-level fields. Missing values are null, never omitted and never an empty string.

```
record_key       "openalex:W2741809807" or "arxiv:2208.10041"
source           "openalex" | "arxiv" | "openalex_snowball"
query            the query string or anchor title that produced it, or "snowball:<seed paper_id>"
fetched_at       ISO 8601 UTC timestamp
title            string
abstract         plain prose, or null if the source has none
year             integer or null
doi              lowercase, without any https://doi.org/ prefix, or null
arxiv_id         "2208.10041" style, no version suffix, or null
openalex_id      "W2741809807" or null
authors          list of {name, openalex_author_id, institutions: [{name, openalex_inst_id, country}]}
venue            journal or conference display name, "arXiv" for preprints, or null
cited_by_count   integer for OpenAlex, null for arXiv
referenced_works list of OpenAlex work IDs (may be empty), null for arXiv
topics           list of topic display names (OpenAlex) or category codes (arXiv)
url              landing page
raw              the untouched API response object
```

Before appending to a file, load the record_keys already in it into a set and skip those. This is what makes a rerun safe.

## OpenAlex with pyalex

```python
from pyalex import Works, config
import os, time
config.api_key = os.environ["OPENALEX_API_KEY"]  # required since 2026
config.email = os.environ.get("OPENALEX_MAILTO")  # optional
config.max_retries = 3
config.retry_backoff_factor = 0.5

pager = (Works()
         .search("optical circuit switch")          # full text over title and abstract, 0.001 USD per page
         .filter(from_publication_date="2012-01-01")
         .paginate(per_page=100, n_max=100))        # per_page maximum is 100
for page in pager:
    for w in page:
        w["id"]                 # https://openalex.org/W... ; keep only the W part
        w["doi"]                # may be null, may have the https://doi.org/ prefix
        w["title"]
        w["publication_year"]
        w["abstract"]           # pyalex rebuilds this from abstract_inverted_index; may be None
        w["authorships"]        # list; each has author.id, author.display_name, institutions[]
        w["cited_by_count"]
        w["referenced_works"]   # list of W ids
        w["topics"]             # list; each has display_name
        w["primary_location"]   # may be None; source may be None; source.display_name is the venue
        w["locations"]          # look here for arxiv.org landing pages
    time.sleep(0.2)
```

Things that go wrong.

- The abstract is stored as an inverted index (word to positions). pyalex exposes `w["abstract"]` and rebuilds it. If you ever see a dict where prose should be, you read the wrong field. Roughly a third of records have no abstract at all. Keep them, mark abstract null, and count them in the collector summary.
- `primary_location` and its `source` can both be None. Guard every access.
- OpenAlex used to expose "concepts". That field is deprecated. Use `topics` (and `keywords` if present).
- Institutions come from OpenAlex's own disambiguation and are the best affiliation data you will get. arXiv has none. Keep OpenAlex institution IDs.
- Search is full text and forgiving, so a phrase like "optical switch" also returns papers about optical switching in unrelated contexts. That is fine. Relevance scoring in stage 1b is the filter, not the query.
- A 429 response means one of two things. Too many requests per second (the limit is 100 per second, so with a 0.2 second sleep you will never see this), or the daily budget is spent, in which case retrying is pointless until midnight UTC. Check https://api.openalex.org/rate-limit?api_key=<key> to tell them apart, and log which one it was. Every response also has a meta.cost_usd field. Sum it in the collector and report it.
- Budget arithmetic for this week. 17 phrase queries plus 13 anchor searches at one page each is about 30 search calls, or 0.03 USD. Snowballing 10 seeds is about 20 list calls. The audit re-fetches are singletons and cost nothing. If the collector reports more than 0.10 USD for the run, something is wrong.
- arXiv preprints appear in OpenAlex too, so expect heavy overlap with the arXiv pull. The DOI for an arXiv preprint in OpenAlex looks like `10.48550/arxiv.2208.10041`, which gives you the arXiv ID for free. Also check `locations[*].landing_page_url` for `arxiv.org/abs/`.
- Anchor titles. Use `Works().search(title)` and accept the top hit only if its normalized title matches the anchor at token_set_ratio 95 or more. Otherwise log a miss. Never fabricate an ID.

Snowballing.

```python
seed = Works()["W2741809807"]
refs = seed["referenced_works"]                      # list of W ids
citing = Works().filter(cites="W2741809807").paginate(per_page=100, n_max=100)
```

Fetch referenced works in batches with a pipe-separated OR filter on the openalex_id field, at most 100 IDs per request (one list call, 0.0001 USD, instead of dozens of singletons). If the batch call complains, fall back to one `Works()[id]` per ID with a 0.15 second sleep, which is free but slower. Cap total new records at the value in queries.yaml.

## arXiv with the arxiv package

```python
import arxiv
client = arxiv.Client(page_size=100, delay_seconds=3.0, num_retries=5)
query = '(abs:"optical circuit switch" OR ti:"optical circuit switch") AND (cat:physics.optics OR cat:cs.NI)'
search = arxiv.Search(query=query, max_results=100, sort_by=arxiv.SortCriterion.Relevance)
for r in client.results(search):
    r.get_short_id()        # "2208.10041v1" ; strip the v suffix for arxiv_id
    r.entry_id              # landing url
    r.title
    r.summary               # the abstract
    [a.name for a in r.authors]   # names only, no affiliations
    r.published.year
    r.primary_category, r.categories
    r.doi                   # journal DOI if the author supplied one, often None
    r.journal_ref
```

Things that go wrong.

- arXiv asks for about three seconds between requests. The client's delay_seconds handles it. Do not run two arXiv collectors at once.
- Phrase search needs the double quotes inside the query string. Without them every word is matched separately and recall explodes.
- Author affiliations are almost never present. Every arXiv-only paper will have authors with no institution. The team map gets affiliations only through the OpenAlex match, so the curator must try hard to match arXiv records to OpenAlex records.
- Version suffixes. `2208.10041v2` and `2208.10041v1` are the same paper. Always strip the version.
- Old-style IDs like `physics/0601001` exist. Keep them as strings.
- A query with more than a few thousand results will be slow and may time out. Keep per_query_cap in queries.yaml at 100 to 200 for this week.

## Dedup and merge rules (for the curator)

Apply in this order and record the method in the duplicates table.

1. DOI. Normalize both sides to lowercase, strip `https://doi.org/`, `http://dx.doi.org/`, and whitespace. Exact match merges.
2. arXiv ID. From the arXiv record directly, and from OpenAlex via the `10.48550/arxiv.` DOI or an arxiv.org landing page. Exact match after stripping versions merges.
3. Fuzzy title. Normalize by lowercasing, removing punctuation, collapsing whitespace. Merge when rapidfuzz `fuzz.token_set_ratio` is 95 or higher and the years differ by at most 1. Write every fuzzy merge into curation_report.md so a human can check the threshold.

Canonical record. Prefer OpenAlex over arXiv, and prefer the record with a non-null abstract. When the canonical record has no abstract and the duplicate does, copy the abstract over. Union the sources field.

Authors. The OpenAlex author ID is canonical. For arXiv-only authors, build name_key by lowercasing, stripping accents with unidecode, and reducing to "surname firstinitial". Two records with the same name_key are the same author only if they share a paper or an institution with a known-ID author of that name. Otherwise keep them separate and note the ambiguity. Merging two different people is worse than leaving one person split.

Institutions. OpenAlex institution IDs only. Do not invent affiliations for arXiv-only authors.

## Audit re-fetch

To re-check a paper, fetch it by ID with `Works()[openalex_id]` or by arXiv ID with `arxiv.Search(id_list=[arxiv_id])`, and compare title, year, and cited_by_count. Citation counts drift daily, so treat a difference under 10 percent as a match.
