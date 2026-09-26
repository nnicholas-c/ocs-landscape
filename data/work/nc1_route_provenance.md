# Number check 1. Where the 43 silicon photonic MEMS core papers came from

Question. The write-up says silicon photonic MEMS (micro-electro-mechanical systems), tech_route mems_silicon_photonic, is the largest device route with 43 core papers. A reader suspects the snowball stage pulled in a UC Berkeley cluster around the anchor "Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers". This note checks whether the count reflects the field or how the sample was built.

Every number below comes from pipeline/check_route_provenance.py (read-only), whose output is data/work/nc1_route_provenance.json. After each number, "(J: key)" names the JSON key that holds it. Run it with `.venv/bin/python -m pipeline.check_route_provenance --out data/work/nc1_route_provenance.json`. Two runs give byte-identical output.

How entry paths are read. Each raw JSONL record has a "query" field. A paper is traced to all its raw records through the duplicates table. The entry path is a phrase query (per source and exact query string), an anchor title, or the snowball (per seed paper_id). One caveat matters for every count here. The collectors skip a record that is already on disk, so each raw record carries only the first query that found it. A paper that a later query would also have found is not credited to that later query, so per-query counts are lower bounds. The raw files hold 904 unique record keys (J: unique_raw_record_keys), and all of them appear in the duplicates table (J: raw_keys_not_in_duplicates_table, empty). No mems_silicon_photonic core paper has more than one entry path (J: route_entry.mems_silicon_photonic, exclusive and non-exclusive counts both sum to 43).

UC Berkeley affiliation is read from paper_authors joined to institutions (display name "University of California, Berkeley"). It is a lower bound. The anchor paper itself has 5 author rows and 0 of them carry an institution (J: q3_berkeley_anchor.author_rows, author_rows_with_institution).

## (1) The 43 mems_silicon_photonic core papers by entry path

By kind, 36 came from a phrase query, 1 from an anchor lookup, and 6 only from the snowball (J: q1_mems_silicon_photonic.summary.by_entry_kind_exclusive).

| Entry path | Core papers |
|---|---|
| query, openalex, "silicon photonic MEMS switch" | 27 |
| query, openalex, "MEMS optical switch" | 6 |
| query, openalex, "silicon photonic switch data center" | 1 |
| query, openalex, "thermo-optic switch port count" | 1 |
| query, arxiv, "optical circuit switch" | 1 |
| anchor, "Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers" | 1 |
| snowball, seed W1982681165 | 6 |

(J: q1_mems_silicon_photonic.summary.by_entry_path_nonexclusive)

17 of the 43 have a UC Berkeley affiliation in the data, and all 17 entered through a phrase query (J: summary.ucb_affiliated, ucb_affiliated_by_entry_kind). 24 of the 43 share at least one author with the Berkeley anchor paper, and all 24 entered through a phrase query (J: summary.shares_author_with_berkeley_anchor, shares_author_with_anchor_by_entry_kind). None of the 6 snowball-only papers has a Berkeley affiliation or shares an author with the anchor (J: q1_mems_silicon_photonic.papers, ucb_affiliated and shares_author_with_berkeley_anchor are false for all 6). Those 6 are from 2002 to 2013 (J: q1_mems_silicon_photonic.papers, year).

## (2) Route counts among core papers with snowball-only papers removed

| tech_route | Core | Snowball only | Core without snowball-only |
|---|---|---|---|
| architecture_only | 101 | 5 | 96 |
| unclear | 44 | 9 | 35 |
| mems_silicon_photonic | 43 | 6 | 37 |
| thermo_optic | 23 | 7 | 16 |
| mems_3d | 15 | 4 | 11 |
| electro_optic | 12 | 8 | 4 |
| soa | 11 | 3 | 8 |
| other | 10 | 3 | 7 |
| mems_2d | 3 | 2 | 1 |
| lcos | 2 | 0 | 2 |
| piezo | 2 | 0 | 2 |
| robotic_patch_panel | 1 | 0 | 1 |

(J: core_route_counts, q2_snowball_only_core_by_route, q2_core_route_counts_without_snowball_only)

Out of 267 core papers (J: core_papers), 47 have a snowball record (J: q2_core_with_any_snowball_record), and all 47 are snowball only. Without them, mems_silicon_photonic is still the largest device route, at 37, ahead of thermo_optic at 16 and mems_3d at 11.

## (3) The snowball seeds

The ten seeds found in the raw query field match the ten that the collector's own seed rule gives when rerun now (J: q3_seed_lists_match, true). Each seed brought in 15 raw records (J: q3_seeds[].raw_records_brought_in). Nine seeds took all 15 from their own reference list, and W2937088522 took 11 (J: q3_seeds[].brought_in_from_seed_reference_list). Every core paper a seed brought in is snowball only (J: q3_seeds[].core_brought_in_by_route equals core_snowball_only_by_route for every seed).

| Seed paper_id | Title | Seed route | Core papers brought in, by route |
|---|---|---|---|
| W2119638333 | Helios | architecture_only | 1 (architecture_only 1) |
| W4380874786 | TPU v4: An Optically Reconfigurable Supercomputer for Machine Learning with Hardware Support for Embeddings | architecture_only | 0 |
| W2141810662 | OSA: An Optical Switching Architecture for Data Center Networks With Unprecedented Flexibility | architecture_only | 2 (architecture_only 2) |
| W2260723393 | Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers | mems_silicon_photonic | 9 (unclear 4, electro_optic 2, thermo_optic 2, mems_3d 1) |
| W2151668565 | Integrating microsecond circuit switching into the data center | architecture_only | 1 (architecture_only 1) |
| W2486960733 | ProjecToR | other | 3 (other 2, mems_3d 1) |
| W2587610600 | 32 x 32 silicon electro-optic switch with built-in monitors and balanced-status units | electro_optic | 7 (unclear 3, thermo_optic 2, electro_optic 1, other 1) |
| W2807234289 | Photonic switching in high performance datacenters [Invited] | unclear | 11 (electro_optic 4, soa 3, mems_3d 2, mems_2d 1, unclear 1) |
| W1982681165 | Large-scale silicon photonic switches with movable directional couplers | mems_silicon_photonic | 11 (mems_silicon_photonic 6, thermo_optic 2, electro_optic 1, mems_2d 1, unclear 1) |
| W2937088522 | Wafer-scale silicon photonic switches beyond die size limit | unclear | 2 (architecture_only 1, thermo_optic 1) |

(J: q3_seeds[]. The multiplication sign in the W2587610600 title is written as x here.)

W1982681165 and W2937088522 have a UC Berkeley affiliation in the data (J: q3_seeds[].ucb_affiliated).

The Berkeley anchor is a seed. Its paper_id is W2260723393 and it has cited_by_count 313 in papers.sqlite (J: q3_berkeley_anchor.is_snowball_seed, paper). Its 15 snowball records gave 9 core papers and none of them is mems_silicon_photonic (J: q3_seeds, W2260723393). The anchor itself was found only by the anchor lookup. Its one raw record, openalex:W2260723393, carries the anchor title as its query, and the paper has no other entry path (J: q3_berkeley_anchor.raw_records_with_this_anchor_as_query, all_entry_paths_of_paper). In collect_openalex.py the phrase queries run before the anchor lookups and an anchor record is written only if its key is not already on disk, so no OpenAlex phrase query returned this paper within its cap.

All 6 snowball-only mems_silicon_photonic papers came from the other silicon photonic MEMS seed, W1982681165, not from the anchor (J: q1 table above, snowball W1982681165 = 6).

## (4) Queries in pipeline/queries.yaml that name a route

Which query names which route is a judgment made against the route names and signal words in the ocs-domain skill. It is written down in QUERY_NAMES_ROUTE in the script. "MEMS optical switch" names the MEMS family, and "silicon photonic switch" names a platform shared by three routes. "Exact phrase" counts records whose title or abstract contains the query string. OpenAlex search matches words, not phrases, so a low count means loose matches.

| Source | Query | Route named | Records | Exact phrase | Relevance scores 0/1/2/3 | Core papers by route |
|---|---|---|---|---|---|---|
| openalex | silicon photonic MEMS switch | mems_silicon_photonic | 34 | 24 | 1/1/2/29 | 29 (mems_silicon_photonic 27, thermo_optic 1, unclear 1) |
| openalex | MEMS optical switch | MEMS family | 49 | 13 | 10/9/6/24 | 24 (unclear 11, mems_silicon_photonic 6, mems_3d 5, mems_2d 1, thermo_optic 1) |
| openalex | 3D MEMS optical cross-connect | mems_3d | 46 | 0 | 37/5/4/0 | 0 |
| openalex | silicon photonic switch data center | silicon photonic platform | 45 | 0 | 16/25/0/4 | 4 (architecture_only 1, electro_optic 1, mems_silicon_photonic 1, other 1) |
| openalex | thermo-optic switch port count | thermo_optic | 41 | 0 | 8/6/3/23 | 23 (thermo_optic 12, unclear 7, electro_optic 1, mems_silicon_photonic 1, other 1, soa 1) |
| openalex | wavelength selective switch LCoS | lcos | 48 | 0 | 4/7/33/3 | 3 (lcos 1, mems_3d 1, unclear 1) |
| openalex | piezoelectric optical switch | piezo | 45 | 0 | 43/2/0/0 | 0 |
| openalex | semiconductor optical amplifier switch data center | soa | 38 | 0 | 27/5/0/6 | 6 (soa 3, architecture_only 2, electro_optic 1) |
| openalex | robotic fiber patch panel | robotic_patch_panel | 49 | 0 | 48/0/0/1 | 1 (robotic_patch_panel 1) |
| arxiv | MEMS optical switch | MEMS family | 0 | 0 | none | 0 |
| arxiv | silicon photonic switch | silicon photonic platform | 0 | 0 | none | 0 |
| arxiv | wavelength selective switch | lcos | 0 | 0 | none | 0 |
| arxiv | piezoelectric optical switch | piezo | 0 | 0 | none | 0 |
| arxiv | thermo-optic switch | thermo_optic | 0 | 0 | none | 0 |

(J: q4_queries[]. Records are raw records whose query field is that query. Relevance scores and core counts are per paper, and a query's papers can be one fewer than its records after merging.)

The one query aimed only at free-space 3D MEMS returned 46 records. None of them scored 3, none contains the phrase, and 16 have "print" in the title (J: q4_queries, "3D MEMS optical cross-connect", records_with_print_in_title). The relevance.csv reasons for those records name 3D printing, bioprinting, sensors and other unrelated work. All five route-naming arXiv phrases returned 0 records, and the run 1 log says 9 of 10 arXiv phrase queries produced 0 records while arXiv returned HTTP 429 or 406 (deliverables/pitfalls_original_log.md, stage 1a checker, 2026-09-26 05:04). The only query that found both piezo core papers, "optical beam steering switch fiber", names no route (J: q4_queries, core_by_route piezo 2).

The 15 mems_3d core papers entered through 10 phrase-query papers, 4 snowball-only papers, and 1 anchor ("1100 x 1100 port MEMS-based optical crossconnect with 4-dB maximum loss") (J: route_entry.mems_3d.by_entry_kind_exclusive). "MEMS optical switch" gave 5 of them (J: route_entry.mems_3d.by_entry_path_nonexclusive). 11 core papers found by "MEMS optical switch" are tagged unclear, so their device route is not known (J: q4_queries, "MEMS optical switch").

## (5) mems_3d and mems_silicon_photonic rows in data/projects.csv

| Entity | Product or project | tech_route | stage | evidence_date |
|---|---|---|---|---|
| Google | Apollo OCS (Palomar MEMS switch) | mems_3d | shipping | 2022-08-23 |
| Lumentum | R300 Optical Circuit Switch (300x300 OCS) | mems_3d | unknown | 2026-09-26 |
| Calient | S320 Optical Circuit Switch | mems_3d | shipping | 2026-09-26 |
| UTStarcom | MOS64 (MEMS) and UOS64 (silicon photonics) OCS concept prototypes | mems_3d | prototype | 2026-09-21 |
| nEye | OCS-on-a-chip | mems_silicon_photonic | prototype | 2026-04-14 |

(J: q5_projects_csv, which also holds each row's evidence_url.) That is 4 mems_3d rows, 2 of them at stage shipping, and 1 mems_silicon_photonic row at stage prototype. The UTStarcom row names a silicon photonics product too but carries one tech_route, mems_3d.

## Conclusion

The snowball hypothesis does not hold, because removing the 6 snowball-only papers still leaves 37 silicon photonic MEMS core papers, the largest device route ahead of thermo_optic at 16 and mems_3d at 11, and the Berkeley anchor's own snowball added none (J: q2_core_route_counts_without_snowball_only, q3_seeds W2260723393). A Berkeley-linked cluster is real, since 24 of the 43 share an author with the anchor, but all 24 came in through phrase queries, and the single query "silicon photonic MEMS switch" supplied 27 of the 43 (J: q1_mems_silicon_photonic.summary). What explains the gap to mems_3d is query yield, because the one query aimed at free-space 3D MEMS, "3D MEMS optical cross-connect", returned 46 records with 0 core papers, 0 exact-phrase matches and 16 "print" titles, while the silicon photonic MEMS query returned 34 records with 29 core papers (J: q4_queries). Paper counts measure research output in this sample, not what ships, and data/projects.csv lists 2 mems_3d products at stage shipping against 1 mems_silicon_photonic product at prototype (J: q5_projects_csv). Whether the wider literature holds more silicon photonic MEMS papers than 3D MEMS papers, the sample cannot tell us.
