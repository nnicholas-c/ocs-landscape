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
playbook, pending orchestrator approval, in deliverables/pitfalls_original_log.md.

- Duplicates found by DOI: 4
- Duplicates found by arXiv ID: 17
- Duplicates found by fuzzy title: 13
- Total duplicates removed: 34
- Papers in the database: 1211

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
- Papers with no abstract: 111

## Authors and institutions

- Author appearances read from canonical records: 9303
- Distinct authors written: 7624
- Of those, with an OpenAlex author ID: 6601
- Author appearances merged into an existing author record: 109
  (89 merged into an ID bearing author by a shared
  institution, 20 merged into another no ID
  appearance by a shared institution)
- Institution appearances read: 11739
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

2236 author appearances listed more than one
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
Pitfalls from this run are appended to deliverables/pitfalls_original_log.md.

### How the new records were absorbed

Of the 341 arxiv_via_openalex records:

- Matched an existing (run 1) paper by DOI: 0
- Matched an existing (run 1) paper by arXiv ID: 8
- Matched an existing (run 1) paper by fuzzy title: 2
- Became new papers, no run 1 record in the cluster: 331
  records, forming 326 new paper(s)

### Core and extended set sizes, before and after

| set | run 1 | run 2 |
|---|---|---|
| Core (score 3) | 267 | 284 |
| Extended | 376 | 420 |

### arXiv coverage after run 2

- Papers with an arXiv ID: 460
- Papers that are arXiv-hosted only (every source is arxiv or
  arxiv_via_openalex, no openalex or openalex_snowball record):
  366

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

5 run 1 tags row(s) referenced a paper_id that this merge retired. Every new id shown below already has a tags row. This invocation deleted 0 tags row(s) whose paper_id is no longer in papers (every other tags row is untouched).

| old paper_id (no longer in papers) | became |
|---|---|
| arxiv:2501.16907 | W4406960606 |
| arxiv:2502.03885 | W4407244986 |
| arxiv:2401.09284 | W4391013534 |
| arxiv:2608.03146 | W7172527693 |
| arxiv:2405.20869 | W4399317831 |

## Step 2, anchor papers

Step 2 tried to add the 3 anchors the stage 1a anchor search missed (Jupiter Evolving, RotorNet and c-Through). The attempt is recorded in data/work/step2_anchors.md; this section states only what this run found on disk, by DOI, not what the attempt intended.

- Jupiter Evolving (DOI 10.1145/3544216.3544265): not in any data/raw/*.jsonl file and not in the database (0 raw record(s) with this DOI).
- RotorNet (DOI 10.1145/3098822.3098838): not in any data/raw/*.jsonl file and not in the database (0 raw record(s) with this DOI).
- c-Through (DOI 10.1145/1851182.1851222): in the database as W2097926925, core (score 3), sources "openalex_snowball", matched by 1 raw record(s) carrying this DOI.

Jupiter Evolving and RotorNet were fetched from OpenAlex by DOI and then removed before this stage ran, so this run added neither. The anchor title check (rapidfuzz token_sort_ratio at least 95 against the full anchor title in pipeline/queries.yaml, a stricter test than the playbook's token_set_ratio rule, which the truncated titles would pass) does not confirm either one, because OpenAlex's title field holds only the words before the colon ("Jupiter evolving", "RotorNet"), so the check scores 23.88 for Jupiter Evolving and 23.19 for RotorNet, both well under the threshold. The two anchors were not confirmed by the title check, so they were not added. That is left as an open question for a human in data/work/step2_anchors.md. Neither DOI is in any data/raw/*.jsonl file now (0 record(s) on disk with these DOIs), so this run merged neither with an existing paper. c-Through was never missing from the database. It reached it as W2097926925 (sources "openalex_snowball"). That is a different raw record than the stage 1a anchor search's false match (openalex:W2160642098, "OPTICS", 1999, still on file under the c-Through query, since raw files are never edited).

### The 2 arXiv-ID merges from the extract_arxiv_id fallback

The pull request #1 code review fix that recovers arxiv_id from a raw OpenAlex
record's landing_page_url, for records whose own arxiv_id field is null,
let arXiv-ID matching catch 2 pair(s) this run that
duplicate detection missed before the fix (both sides of each pair already
existed in data/raw/*.jsonl; this is not new data from step 2's anchor
search). In both pairs the two records share the same arxiv_id, and
the full author lists also match (3 authors and 4 authors). openalex:W2960571025 is an SSRN (Social Science Research Network) working paper record.

| record_key (source) | title A | paper_id (source) | title B | shared arxiv_id |
|---|---|---|---|---|
| openalex:W2960571025 (arxiv_via_openalex) | Design and Evaluation of Product Aesthetics: A Human-Machine Hybrid Approach | W4285069006 (arxiv_via_openalex) | Product Aesthetic Design: A Machine Learning Augmentation | 1907.07786 |
| openalex:W3036896065 (arxiv_via_openalex) | A Competitive B-Matching Algorithm for Reconfigurable Datacenter Networks. | W3138831328 (arxiv_via_openalex) | Online Dynamic B-Matching With Applications to Reconfigurable Datacenter Networks | 2006.10692 |

## Agent review of the fuzzy-title merges (after the run)

This section was added after the run, outside the pipeline, so rerunning pipeline/curate.py regenerates this report without it. Two agents, not a person, reviewed each of the 13 merges in the Fuzzy title matches table above, each blind to the other, and a script (data/work/agentcheck_reconcile.py) reconciled their verdicts. They gave the same verdict on 13 of 13 merges, 9 same paper and 4 different papers (table below; data/work/agentcheck_final.md, Agreement counts and Table 2). The reasons below summarize the notes of the two agents, who read the database and the raw records.

| record_key (merged) | paper_id (kept) | agent A | agent B | final | reason |
|---|---|---|---|---|---|
| openalex:W1635046341 | W2271940456 | different papers | different papers | different papers | A 2015 conference paper and the 2016 journal letter that followed it, with different abstracts. The Wencong Zhang record A5037451400 is on the conference paper only and has no row in the authors table, so the merge dropped that record (agent A). A Wencong Zhang record with the same Berkeley co-authors (A5118983676) stays on the team map through 2 other 2015 papers, W1945545782 and W2186858051 (data/db/papers.sqlite) |
| openalex:W2186112211 | W2340261621 | different papers | different papers | different papers | A 2015 conference paper and a 2016 journal article with different abstracts and author lists. Keita Yamaguchi and Joji Yamaguchi are on the conference paper only and are not linked to the kept paper (agent A) |
| openalex:W2798334538 | W2792328579 | different papers | different papers | different papers | A 2017 conference paper and the 2018 journal article by the same single author, Ken-ichi Sato, with different abstracts. No author is lost, but two publications become one |
| openalex:W3000564174 | W2074285614 | same paper | same paper | same paper | One 2012 demo paper under two DOIs (digital object identifiers), the conference proceedings copy and the journal copy, with identical abstract, authors and pages |
| openalex:W3008629526 | W2948602808 | same paper | same paper | same paper | A repository copy with no DOI of the 2020 review article, with the same authors in the same order and a near-identical abstract. The kept record has no OpenAlex author IDs, so its authors are keyed by name and the merged record's author IDs were not carried over (agent A). The paper is off topic for OCS (optical circuit switching), a relevance issue and not a merge issue (agent B) |
| openalex:W3008830959 | W2151668565 | same paper | same paper | same paper | One 2013 paper under two DOIs, proceedings and journal copy, with the same authors, pages and DOI article number |
| openalex:W4238465620 | W2130531694 | same paper | same paper | same paper | One 2008 paper under two DOIs, proceedings and journal copy, with the same authors, pages and DOI article number |
| openalex:W4281707213 | W4200142051 | same paper | same paper | same paper | The 2-page 2022 conference abstract of the 2021 journal article, with the same authors and a near-identical abstract |
| openalex:W4284882945 | W4200142051 | same paper | same paper | same paper | A second copy of the same 2-page abstract as the row above, so these two rows are one item twice |
| openalex:W4310544708 | W2971102795 | same paper | same paper | same paper | The 2018 arXiv preprint of the 2019 journal article, with identical abstract and authors |
| openalex:W4391087787 | W4377082743 | same paper | same paper | same paper | One 2023 conference paper under two publishers' DOIs, with identical abstract and authors |
| openalex:W4392029208 | W4386365418 | different papers | different papers | different papers | A 2024 conference paper that cites the kept 2023 conference paper, with the same authors and a near-identical abstract. It is a separate publication of the same work, so the merge is wrong, and the harm is small because no author is lost |
| openalex:W4414838842 | W4410343081 | same paper | same paper | same paper | The 2025 arXiv preprint of the 2025 magazine article, with the same title and authors. The kept abstract is one sentence, so the texts could not be compared, and agent B rated its confidence moderate |
