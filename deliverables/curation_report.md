# Curation report

Stage 2 output. Built by pipeline/curate.py from every data/raw/*.jsonl file
and data/raw/relevance.csv, following the dedup rules in the
openalex-arxiv-playbook skill.

## Raw records

Records read per raw file, before any dedup.

- arxiv.jsonl: 47
- arxiv_via_openalex.jsonl: 341
- openalex.jsonl: 707
- openalex_snowball.jsonl: 150
- smoke_arxiv.jsonl: 5
- smoke_openalex.jsonl: 5

Ten record_key values were seen again in a later file with the exact same
key (the stage 0 smoke files repeat records already present in the stage 1a
full pull). Those repeats were skipped, leaving 1245 unique raw
records.

## Deduplication

Raw records were clustered into one paper each using the dedup rules in
order: DOI match, then arXiv ID match, then fuzzy title match. A raw record
can be pulled into a cluster by more than one rule; when that happens the
most confident rule (DOI, then arXiv ID, then fuzzy title) is the one
recorded in the duplicates table.

Fuzzy title match requires rapidfuzz token_set_ratio at least 95 AND
token_sort_ratio at least 90, with publication years within 1 of each other.
This narrows the openalex-arxiv-playbook skill's rule, which is
token_set_ratio >= 95 alone. token_set_ratio scores 100 whenever one
normalized title's tokens are a subset of the other's, which merged
different papers (for example "Integrated silicon photonic MEMS" is a token
subset of "Large-scale silicon photonic MEMS switch with flip-chip
integrated CMOS drivers", a different, score 3 paper); token_sort_ratio
compares the titles as whole sorted strings and does not have that flaw.
Adding this second test can only drop merges the playbook's single test
would have made, never add new ones. Logged as a deviation from the
playbook, pending orchestrator approval, in data/work/run2_pitfalls.log.

- Duplicates found by DOI: 4
- Duplicates found by arXiv ID: 15
- Duplicates found by fuzzy title: 13
- Total duplicates removed: 32
- Papers in the database: 1213

The canonical record for a cluster is chosen by preferring an OpenAlex
sourced record over an arXiv only record, then preferring a record with a
non null abstract, then the higher cited_by_count, then the record_key
itself for a stable tie break. When the canonical record has no abstract
but another record in its cluster does, that abstract is copied onto the
canonical row. The sources field on each paper lists every raw source that
fed into it.

### Fuzzy title matches

All 13 fuzzy_title rows in the duplicates table (record_key A
merged into paper_id B), full titles, so a human can eyeball whether the
threshold is right. Each row is the merged record versus the canonical
record its cluster kept, not necessarily the specific pair that first
triggered the merge (a cluster can be chained through more than one raw
record).

| record_key | title A (year, doi) | paper_id | title B (year, doi) | token_set_ratio | token_sort_ratio |
|---|---|---|---|---|---|
| openalex:W1635046341 | Row/column addressing of scalable silicon photonic MEMS switches (2015, 10.1109/omn.2015.7288891) | W2271940456 | Scalable Row/Column Addressing of Silicon Photonic MEMS Switches (2016, 10.1109/lpt.2016.2515106) | 100.0 | 100.0 |
| openalex:W2186112211 | MxN wavelength selective switches using beam splitting by space light modulators (2015, 10.1109/oecc.2015.7340301) | W2340261621 | M N Wavelength Selective Switches Using Beam Splitting By Space Light Modulators (2016, 10.1109/jphot.2016.2527705) | 98.8 | 97.5 |
| openalex:W2798334538 | Realization and Application of Large-scale Fast Optical Circuit Switch for Data Center Networking (2017, 10.1109/ecoc.2017.8346155) | W2792328579 | Realization and Application of Large-Scale Fast Optical Circuit Switch for Data Center Networking (2018, 10.1109/jlt.2018.2801308) | 100.0 | 100.0 |
| openalex:W3000564174 | A demonstration of ultra-low-latency data center optical circuit switching (2012, 10.1145/2377677.2377698) | W2074285614 | A demonstration of ultra-low-latency data center optical circuit switching (2012, 10.1145/2342356.2342377) | 100.0 | 100.0 |
| openalex:W3008629526 | Advances in Quantum Cryptography (2019, no doi) | W2948602808 | Advances in quantum cryptography (2020, 10.1364/aop.361502) | 100.0 | 100.0 |
| openalex:W3008830959 | Integrating microsecond circuit switching into the data center (2013, 10.1145/2534169.2486007) | W2151668565 | Integrating microsecond circuit switching into the data center (2013, 10.1145/2486001.2486007) | 100.0 | 100.0 |
| openalex:W4238465620 | A scalable, commodity data center network architecture (2008, 10.1145/1402958.1402967) | W2130531694 | A scalable, commodity data center network architecture (2008, 10.1145/1402946.1402967) | 100.0 | 100.0 |
| openalex:W4281707213 | Understanding the Performance Guarantee of Physical Topology Design for Optical Circuit Switched Data Centers (2022, 10.1145/3489048.3522639) | W4200142051 | Understanding the Performance Guarantee of Physical Topology Design for Optical Circuit Switched Data Centers (2021, 10.1145/3491054) | 100.0 | 100.0 |
| openalex:W4284882945 | Understanding the Performance Guarantee of Physical Topology Design for Optical Circuit Switched Data Centers (2022, 10.1145/3547353.3522639) | W4200142051 | Understanding the Performance Guarantee of Physical Topology Design for Optical Circuit Switched Data Centers (2021, 10.1145/3491054) | 100.0 | 100.0 |
| openalex:W4310544708 | A self-starting bi-chromatic LiNbO3 soliton microcomb (2018, 10.48550/arxiv.1812.09610) | W2971102795 | Self-starting bi-chromatic LiNbO 3 soliton microcomb (2019, 10.1364/optica.6.001138) | 97.1 | 97.1 |
| openalex:W4391087787 | Apollo: Large-Scale Deployment of Optical Circuit Switching for Datacenter Networking (2023, 10.23919/ofc49934.2023.10116374) | W4377082743 | Apollo: Large-Scale Deployment of Optical Circuit Switching for Datacenter Networking (2023, 10.1364/ofc.2023.m2g.1) | 100.0 | 100.0 |
| openalex:W4392029208 | Lightwave Fabrics: At-Scale Optical Circuit Switching for Datacenter and Machine Learning Systems (2024, 10.1109/mems58180.2024.10439411) | W4386365418 | Lightwave Fabrics: At-Scale Optical Circuit Switching for Datacenter and Machine Learning Systems (2023, 10.1145/3603269.3604836) | 100.0 | 100.0 |
| openalex:W4414838842 | Revolutionizing Datacenter Networks via Reconfigurable Topologies (2025, 10.48550/arxiv.2502.16228) | W4410343081 | Revolutionizing Datacenter Networks via Reconfigurable Topologies (2025, 10.1145/3708980) | 100.0 | 100.0 |

## Relevance score and adjacent field for merged papers

When several raw records merged into one paper, the paper's relevance_score
is the highest score among its raw records' rows in relevance.csv, and the
paper's adjacent_field is taken from that same highest scoring row, not
chosen independently. On a tie between raw records, the row that carries a
non null adjacent_field wins, and if that still ties the earliest
record_key wins, so the choice is deterministic on a rerun.

## Core and extended sets

Gate A found more than 200 records scoring 2 or 3, so per PLAN.md the core
set is score 3 only. core_set = 1 for papers whose chosen relevance_score is
3. extended_set = 1 for every core paper plus every paper whose chosen
relevance_score is 1 and whose chosen adjacent_field is not empty. Score 2
papers are in neither set this run.

- Core papers (core_set = 1): 284
- Extended papers (extended_set = 1): 420
- Papers with no abstract: 112

## Authors and institutions

- Author appearances read from canonical records: 9310
- Distinct authors written: 7624
- Of those, with an OpenAlex author ID: 6601
- Author appearances merged into an existing author record: 109
  (89 merged into an ID bearing author by a shared
  institution, 20 merged into another no ID
  appearance by a shared institution)
- Institution appearances read: 11743
- Distinct institutions written: 1641

Author identity rules, from the playbook. An OpenAlex author ID is always
canonical and never merged with anything else. An author appearance with no
ID (this includes every arXiv author, and a smaller number of OpenAlex
authorships where OpenAlex itself left the ID blank) is folded into an
existing author only when they share at least one institution: first
checked against ID bearing authors of the same name_key, then against other
no ID appearances of the same name_key. Name match alone is never enough,
per the rule that merging two different people is worse than leaving one
split.

arXiv never supplies institution data, so an arXiv only author's appearances
can never satisfy that shared institution test against each other. The
practical effect is that the same person publishing on two arXiv only
papers with no OpenAlex match gets a separate author row per paper unless
an OpenAlex sourced appearance ties them together through a shared
institution. This is the conservative side of the rule and is called out
here rather than hidden. 82 such no ID, same
name_key appearances were kept separate this run and given a disambiguated
author_id (name:<name_key>#2 and so on).

2237 author appearances listed more than one
institution on the same paper. Only the first is stored in paper_authors,
since the table holds one affiliation per paper per author; the full list
for that author is still visible on any other paper where it appears.

## Sanity queries

- Papers with no authors: 2
- Papers with no year: 0
- Core papers with no abstract: 14

## Anomalies

- None.

## Run 2, arXiv via OpenAlex

This run added data/raw/arxiv_via_openalex.jsonl (341
records, source "arxiv_via_openalex": OpenAlex's own index of arXiv, source
S4306400194) to the raw files curated above. Every section above already
reflects the merged result; this section isolates what the new file changed.
Pitfalls from this run are appended to data/work/run2_pitfalls.log, not this file's usual
pitfalls.md, per the phase's logging setup.

### How the new records were absorbed

Of the 341 arxiv_via_openalex records:

- Matched an existing (run 1) paper by DOI: 0
- Matched an existing (run 1) paper by arXiv ID: 8
- Matched an existing (run 1) paper by fuzzy title: 2
- Became new papers, no run 1 record in the cluster: 331
  records, forming 328 new paper(s)

### Core and extended set sizes, before and after

| set | run 1 | run 2 |
|---|---|---|
| Core (score 3) | 267 | 284 |
| Extended | 376 | 420 |

### arXiv coverage after run 2

- Papers with an arXiv ID: 458
- Papers that are arXiv-hosted only (every source is arxiv or
  arxiv_via_openalex, no openalex or openalex_snowball record):
  368

### Run 1 arXiv-only papers that gained OpenAlex data

Run 1 had 40 papers known only by arXiv ID (paper_id
"arxiv:...", no OpenAlex ID). Of those, this run:

- Gained an OpenAlex ID (merged with an arxiv_via_openalex record): 6
- Of those, also gained at least one author institution: 1

| old paper_id | arxiv_id | new paper_id | title | gained an institution |
|---|---|---|---|---|
| arxiv:2501.16907 | 2501.16907 | W4406960606 | Experimental Evaluation of an SDN Controller for Open Optical-circuit-switched Networks | no |
| arxiv:2502.03885 | 2502.03885 | W4407244986 | InfiniteHBD: Building Datacenter-Scale High-Bandwidth Domain for LLM with Optical Circuit Switching Transceivers | no |
| arxiv:2401.09284 | 2401.09284 | W4391013534 | A Fast Control Plane for a Large-Scale and High-Speed Optical Circuit Switch System | no |
| arxiv:1208.0581 | 1208.0581 | W2949939478 | Optimal Degree of Optical Circuit Switching in IP-over-WDM Networks | yes |
| arxiv:2608.03146 | 2608.03146 | W7172527693 | Zero-change foundry compatible silicon photonics MEMS optical switch | no |
| arxiv:2405.20869 | 2405.20869 | W4399317831 | Understanding the Throughput Bounds of Reconfigurable Datacenter Networks | no |

### Fuzzy title merges involving a new record

2 of the 13 fuzzy_title merges listed
above involve at least one arxiv_via_openalex record.

| record_key | title A (year, doi) | paper_id | title B (year, doi) | token_set_ratio | token_sort_ratio |
|---|---|---|---|---|---|
| openalex:W4310544708 | A self-starting bi-chromatic LiNbO3 soliton microcomb (2018, 10.48550/arxiv.1812.09610) | W2971102795 | Self-starting bi-chromatic LiNbO 3 soliton microcomb (2019, 10.1364/optica.6.001138) | 97.1 | 97.1 |
| openalex:W4414838842 | Revolutionizing Datacenter Networks via Reconfigurable Topologies (2025, 10.48550/arxiv.2502.16228) | W4410343081 | Revolutionizing Datacenter Networks via Reconfigurable Topologies (2025, 10.1145/3708980) | 100.0 | 100.0 |

### Tags table cleanup

5 tags row(s) referenced a paper_id no longer present in papers after this merge and were deleted (every other tags row is untouched); stage 3 must retag these under the new id shown below. Logged in data/work/run2_pitfalls.log.

| old paper_id (no longer in papers) | became |
|---|---|
| arxiv:2501.16907 | W4406960606 |
| arxiv:2502.03885 | W4407244986 |
| arxiv:2401.09284 | W4391013534 |
| arxiv:2608.03146 | W7172527693 |
| arxiv:2405.20869 | W4399317831 |
