# Run 2 - arXiv coverage gap in the run 1 database

Computed on data/db/papers.sqlite as it stood before run 2 collection (run 1 output, untouched).

## Definition

A paper counts as "arXiv-hosted" if any of:
- `arxiv_id IS NOT NULL`
- `lower(doi) LIKE '10.48550/arxiv.%'`
- `lower(url) LIKE '%arxiv.org%'`

## SQL

```sql
-- shared condition, always parenthesized as a group before ANDing with anything else
-- (WHERE a OR b OR c AND d parses as a OR b OR (c AND d), not (a OR b OR c) AND d -- caught this the hard way, see pitfall log)

-- overall counts
SELECT COUNT(*) FROM papers
WHERE (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%');
-- => 133

SELECT COUNT(*) FROM papers
WHERE (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%')
  AND openalex_id IS NOT NULL;
-- => 93

SELECT COUNT(*) FROM papers
WHERE (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%')
  AND openalex_id IS NULL;
-- => 40

-- core set only (core_set = 1)
SELECT COUNT(*) FROM papers
WHERE core_set = 1
  AND (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%');
-- => 43

SELECT COUNT(*) FROM papers
WHERE core_set = 1
  AND (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%')
  AND openalex_id IS NOT NULL;
-- => 7

SELECT COUNT(*) FROM papers
WHERE core_set = 1
  AND (arxiv_id IS NOT NULL
       OR lower(doi) LIKE '10.48550/arxiv.%'
       OR lower(url) LIKE '%arxiv.org%')
  AND openalex_id IS NULL;
-- => 36

-- denominators for context
SELECT COUNT(*) FROM papers;            -- => 885
SELECT COUNT(*) FROM papers WHERE core_set = 1;  -- => 267
```

## Numbers

| scope | arXiv-hosted | with openalex_id | without openalex_id |
|---|---|---|---|
| overall (885 papers) | 133 | 93 | 40 |
| core set (267 papers) | 43 | 7 | 36 |

## Reading

Overall, 40 of 885 papers are arXiv-hosted with no OpenAlex ID (arXiv-only records that curation never matched to an OpenAlex work). In the core set specifically, 36 of 43 arXiv-hosted core papers (84 percent) have no OpenAlex ID. That is the gap this run's OpenAlex-indexed-arXiv pull is meant to close: OpenAlex's own index of arXiv (source S4306400194, see step 2) may carry OpenAlex metadata (cited_by_count, topics, institution-linked authorships) for records the arXiv-only pull could not provide.
