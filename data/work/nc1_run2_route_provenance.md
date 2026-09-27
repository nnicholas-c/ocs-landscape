# Number check 1, run 2. How each route's core papers entered the sample

This reruns number check 1 on run 2's database, data/db/papers.sqlite, after the arXiv via OpenAlex pull and the step 2 anchor rebuild. It gives the core papers per tech route and, for the largest route, how its papers entered the sample. The largest route overall is architecture_only, and number check 1 was about the largest device route, silicon photonic MEMS (micro-electro-mechanical systems), so both are broken down.

Every number comes from pipeline/check_route_provenance.py (read-only). J2 is its run 2 output, data/work/nc1_run2_route_provenance.json, and J1 is run 1's committed output, data/work/nc1_route_provenance.json. "(J2, key)" names the JSON (JavaScript Object Notation) key that holds a number. Run it with `.venv/bin/python -m pipeline.check_route_provenance --out data/work/nc1_run2_route_provenance.json`. Two runs gave byte-identical output (cmp, 2026-09-26).

## SQL used

All SQL (Structured Query Language) statements are SELECTs on a read-only connection.

```sql
-- every paper with its tag row (tags cover core and extended papers)
SELECT p.paper_id, p.title, p.year, p.cited_by_count, p.relevance_score,
       p.core_set, p.extended_set, t.tech_route
  FROM papers p LEFT JOIN tags t ON t.paper_id = p.paper_id;

-- every raw record behind a paper; a merged paper has several
SELECT record_key, paper_id FROM duplicates;

-- papers with at least one author affiliated with UC Berkeley on that paper
-- (arXiv-only records carry no affiliations, so this is a lower bound)
SELECT DISTINCT pa.paper_id FROM paper_authors pa
  JOIN institutions i ON i.inst_id = pa.inst_id
 WHERE i.display_name = 'University of California, Berkeley';

-- author rows of the anchor paper, and how many carry an institution
SELECT COUNT(*) FROM paper_authors WHERE paper_id = ? [AND inst_id IS NOT NULL];

-- papers sharing at least one author with the Berkeley anchor paper
SELECT DISTINCT b.paper_id FROM paper_authors a
  JOIN paper_authors b ON b.author_id = a.author_id
 WHERE a.paper_id = ? AND b.paper_id <> a.paper_id;
```

## How entry paths are read

Each raw JSONL record has a "query" and a "source" field. A paper is traced to all its raw records through the duplicates table. The entry path is one of four kinds. A phrase query is credited per source and exact query string (openalex or arxiv). An arxiv_via_openalex record is credited to its phrase, run against OpenAlex's arXiv index. An anchor is credited to its title, whether the query field holds the plain title or "anchor:" plus the title. A snowball record is credited to its seed.

The collectors skip a record key that is already on disk, and arxiv_via_openalex skips keys in any raw file. So each raw record carries only the first query that found it, and per-query counts are lower bounds. The raw files hold 1245 unique record keys (J2, unique_raw_record_keys), and all of them appear in the duplicates table (J2, raw_keys_not_in_duplicates_table, empty). UC Berkeley (University of California, Berkeley) affiliation is a lower bound too.

## Core papers per tech route

| tech_route | Run 1 core | Run 2 core | Snowball only | Without snowball only | arxiv_via_openalex only |
|---|---|---|---|---|---|
| architecture_only | 101 | 105 | 5 | 100 | 3 |
| unclear | 44 | 44 | 9 | 35 | 0 |
| mems_silicon_photonic | 43 | 43 | 6 | 37 | 0 |
| thermo_optic | 23 | 30 | 7 | 23 | 7 |
| mems_3d | 15 | 16 | 4 | 12 | 1 |
| electro_optic | 12 | 14 | 8 | 6 | 2 |
| other | 10 | 13 | 3 | 10 | 3 |
| soa | 11 | 11 | 3 | 8 | 0 |
| mems_2d | 3 | 3 | 2 | 1 | 0 |
| lcos | 2 | 2 | 0 | 2 | 0 |
| piezo | 2 | 2 | 0 | 2 | 0 |
| robotic_patch_panel | 1 | 1 | 0 | 1 | 0 |

(J1, core_route_counts. J2, core_route_counts, q2_snowball_only_core_by_route, q2_core_route_counts_without_snowball_only, route_entry[].by_entry_kind_exclusive.arxiv_via_openalex. A 0 in the last column means the kind is absent from that route's exclusive counts.)

Run 2 has 284 core papers (J2, core_papers) against 267 in run 1 (J1, core_papers). 47 core papers have a snowball record and all 47 are snowball only (J2, q2_core_with_any_snowball_record, q2_snowball_only_core_by_route). The largest route is architecture_only (J2, largest_route).

## Largest route, architecture_only (105 core papers)

By kind, 88 entered only through phrase queries, 7 through both an arxiv_via_openalex phrase and a phrase query, 5 only through the snowball, 3 only through an arxiv_via_openalex phrase, and 2 only through an anchor (J2, route_entry.architecture_only.by_entry_kind_exclusive).

| Entry path | Core papers |
|---|---|
| query, arxiv, "optical circuit switch" | 37 |
| query, openalex, "optical circuit switch" | 24 |
| query, openalex, "optical circuit switching data center" | 14 |
| query, openalex, "reconfigurable data center network optical" | 11 |
| query, openalex, "optical interconnect reconfigurable topology distributed training" | 8 |
| query, openalex, "optical beam steering switch fiber" | 2 |
| query, openalex, "optical cross-connect data center" | 2 |
| query, openalex, "semiconductor optical amplifier switch data center" | 2 |
| query, openalex, "silicon photonic switch data center" | 1 |
| arxiv_via_openalex, "reconfigurable datacenter network" | 6 |
| arxiv_via_openalex, "optical circuit switch" | 4 |
| anchor, "Expanding across time to deliver bandwidth efficiency and low latency" | 1 |
| anchor, "Helios: A Hybrid Electrical/Optical Switch Architecture for Modular Data Centers" | 1 |
| snowball, seed W2141810662 | 2 |
| snowball, seed W2119638333 | 1 |
| snowball, seed W2151668565 | 1 |
| snowball, seed W2937088522 | 1 |

(J2, route_entry.architecture_only.by_entry_path_nonexclusive. A paper merged from several raw records is counted once per path, so this column sums to more than the route total.)

None of the 105 has a UC Berkeley affiliation in the data (J2, route_entry.architecture_only.ucb_affiliated).

## Largest device route, mems_silicon_photonic (43 core papers)

By kind, 35 entered only through phrase queries, 6 only through the snowball, 1 only through an anchor, and 1 through both an arxiv_via_openalex phrase and a phrase query (J2, q1_mems_silicon_photonic.summary.by_entry_kind_exclusive).

| Entry path | Core papers |
|---|---|
| query, openalex, "silicon photonic MEMS switch" | 27 |
| query, openalex, "MEMS optical switch" | 6 |
| query, openalex, "silicon photonic switch data center" | 1 |
| query, openalex, "thermo-optic switch port count" | 1 |
| query, arxiv, "optical circuit switch" | 1 |
| arxiv_via_openalex, "MEMS optical switch" | 1 |
| anchor, "Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers" | 1 |
| snowball, seed W1982681165 | 6 |

(J2, q1_mems_silicon_photonic.summary.by_entry_path_nonexclusive)

The one paper with an arxiv_via_openalex path is W7172527693, which also carries the arxiv query path. Its raw records include arxiv:2608.03146 (J2, q1_mems_silicon_photonic.papers). That arXiv ID is the one paper_id in run 1's list that is not in run 2's list, and W7172527693 is the one run 2 paper_id not in run 1's list (J1 and J2, q1_mems_silicon_photonic.papers[].paper_id).

17 of the 43 have a UC Berkeley affiliation in the data and all 17 entered through a phrase query. 24 share an author with the Berkeley anchor paper and all 24 entered through a phrase query (J2, q1_mems_silicon_photonic.summary). The anchor, W2260723393, entered only by the anchor lookup and is a snowball seed. It has 5 author rows, 0 of them with an institution (J2, q3_berkeley_anchor). Its snowball brought in 9 core papers, 0 of them mems_silicon_photonic, while seed W1982681165 brought in all 6 snowball-only mems_silicon_photonic papers (J2, q3_seeds). The seeds on disk match the collector's seed rule rerun now (J2, q3_seed_lists_match, true).

## arxiv_via_openalex phrases

| Phrase | Route named | Records | Exact phrase | Papers | Relevance 0/1/2/3 | Core papers by route |
|---|---|---|---|---|---|---|
| optical circuit switch | none | 33 | 3 | 33 | 24/0/5/4 | 4 (architecture_only 4) |
| optical circuit switching | none | 0 | 0 | 0 | none | 0 |
| MEMS optical switch | MEMS family | 40 | 3 | 39 | 36/0/1/2 | 2 (mems_3d 1, mems_silicon_photonic 1) |
| silicon photonic switch | silicon photonic platform | 31 | 2 | 30 | 18/7/2/3 | 3 (other 2, thermo_optic 1) |
| wavelength selective switch | lcos | 45 | 4 | 44 | 32/7/5/0 | 0 |
| piezoelectric optical switch | piezo | 39 | 0 | 39 | 38/1/0/0 | 0 |
| thermo-optic switch | thermo_optic | 33 | 3 | 33 | 7/11/6/9 | 9 (thermo_optic 6, electro_optic 2, other 1) |
| optical cross-connect | none | 39 | 0 | 39 | 38/1/0/0 | 0 |
| reconfigurable datacenter network | none | 44 | 9 | 43 | 30/2/5/6 | 6 (architecture_only 6) |
| optical interconnect machine learning training | none | 37 | 0 | 35 | 35/0/0/0 | 0 |

(J2, q4_queries[] where source is arxiv_via_openalex. Records are raw records first found by the phrase. Relevance and core counts are per paper. A score missing from papers_by_relevance_score is written 0. Route named comes from QUERY_NAMES_ROUTE in the script.)

## Conclusion

In run 2 the largest route is architecture_only with 105 of 284 core papers, 88 of which entered only through phrase queries, led by "optical circuit switch" on arXiv with 37 and on OpenAlex with 24 (J2, largest_route, core_papers, route_entry.architecture_only). The largest device route is still mems_silicon_photonic at 43 as in run 1, and it keeps 37 without its 6 snowball-only papers, all 6 from seed W1982681165 and none from the Berkeley anchor's snowball (J1 and J2, core_route_counts. J2, q2_core_route_counts_without_snowball_only, q3_seeds). Its 17 UC Berkeley-affiliated papers and its 24 papers sharing an author with the anchor all entered through phrase queries, and arxiv_via_openalex added a path to only 1 of its papers, one an arXiv query had already found (J2, q1_mems_silicon_photonic.summary, papers). arxiv_via_openalex is the only entry path of 7 thermo_optic core papers, equal to that route's rise from 23 in run 1 to 30, and of at most 3 papers in any other route (J1, core_route_counts. J2, route_entry[].by_entry_kind_exclusive).
