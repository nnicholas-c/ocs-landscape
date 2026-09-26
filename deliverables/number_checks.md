# Number checks

Three numbers were questioned before the meeting. Each section gives the numbers with their sources, then the conclusion. J1 marks a key in data/work/nc1_route_provenance.json (pipeline/check_route_provenance.py). N2 marks a section of data/work/nc2_name_keys.md (pipeline/merge_name_keys.py). A1 and A2 mark the a_refetch block of data/work/audit_round1.json and data/work/audit_run2_round1.json (pipeline/audit.py).

## 1. Silicon photonic MEMS count

The write-up says silicon photonic MEMS (micro-electro-mechanical systems), route mems_silicon_photonic, is the largest device route with 43 core papers (J1, core_route_counts). The worry was that the snowball stage pulled in a UC Berkeley (University of California, Berkeley) cluster around the anchor paper W2260723393, "Large-scale broadband digital silicon photonic switches with vertical adiabatic couplers".

| Entry path of the 43 | Core papers |
|---|---|
| openalex query "silicon photonic MEMS switch" | 27 |
| openalex query "MEMS optical switch" | 6 |
| openalex query "silicon photonic switch data center" | 1 |
| openalex query "thermo-optic switch port count" | 1 |
| arxiv query "optical circuit switch" | 1 |
| anchor lookup (W2260723393) | 1 |
| snowball from seed W1982681165 | 6 |

(J1, q1_mems_silicon_photonic.summary.by_entry_path_nonexclusive)

17 of the 43 have a UC Berkeley affiliation and 24 share an author with the anchor, and all of them entered through a phrase query (J1, q1_mems_silicon_photonic.summary). Of 267 core papers (J1, core_papers), 47 have a snowball record and all 47 are snowball only (J1, q2_core_with_any_snowball_record).

| tech_route | Core | Snowball only | Core without snowball only |
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

(J1, core_route_counts, q2_snowball_only_core_by_route, q2_core_route_counts_without_snowball_only)

| Snowball seed | Seed route | Core papers brought in | Of them mems_silicon_photonic |
|---|---|---|---|
| W2119638333 | architecture_only | 1 | 0 |
| W4380874786 | architecture_only | 0 | 0 |
| W2141810662 | architecture_only | 2 | 0 |
| W2260723393 (the anchor) | mems_silicon_photonic | 9 | 0 |
| W2151668565 | architecture_only | 1 | 0 |
| W2486960733 | other | 3 | 0 |
| W2587610600 | electro_optic | 7 | 0 |
| W2807234289 | unclear | 11 | 0 |
| W1982681165 | mems_silicon_photonic | 11 | 6 |
| W2937088522 | unclear | 2 | 0 |

(J1, q3_seeds)

| OpenAlex query | Route named | Records | Exact phrase | Core papers |
|---|---|---|---|---|
| silicon photonic MEMS switch | mems_silicon_photonic | 34 | 24 | 29 |
| MEMS optical switch | MEMS family | 49 | 13 | 24 |
| 3D MEMS optical cross-connect | mems_3d | 46 | 0 | 0 |
| silicon photonic switch data center | silicon photonic platform | 45 | 0 | 4 |
| thermo-optic switch port count | thermo_optic | 41 | 0 | 23 |
| wavelength selective switch LCoS | lcos | 48 | 0 | 3 |
| piezoelectric optical switch | piezo | 45 | 0 | 0 |
| semiconductor optical amplifier switch data center | soa | 38 | 0 | 6 |
| robotic fiber patch panel | robotic_patch_panel | 49 | 0 | 1 |

(J1, q4_queries)

The five arXiv queries that name a route returned 0 records (J1, q4_queries), while arXiv was returning HTTP (Hypertext Transfer Protocol) 429 or 406 errors (deliverables/pitfalls_original_log.md, stage 1a checker, 2026-09-26 05:04). Of the 46 "3D MEMS optical cross-connect" records, 16 have "print" in the title (J1, q4_queries).

| Entity | Product | tech_route | Stage |
|---|---|---|---|
| Google | Apollo OCS (optical circuit switch) | mems_3d | shipping |
| Lumentum | R300 | mems_3d | unknown |
| Calient | S320 | mems_3d | shipping |
| UTStarcom | MOS64 and UOS64 | mems_3d | prototype |
| nEye | OCS-on-a-chip | mems_silicon_photonic | prototype |

(J1, q5_projects_csv, from data/projects.csv)

Conclusion. The snowball did not make the count. Without its 6 papers the route still has 37, ahead of thermo_optic at 16 and mems_3d at 11 (J1, q2_core_route_counts_without_snowball_only). The Berkeley cluster is real but came through phrase queries, and one query supplied 27 of the 43 (J1, q1_mems_silicon_photonic.summary). The gap to mems_3d reflects query yield, because the one 3D MEMS query found 0 core papers (J1, q4_queries). Paper counts measure research output in this sample, not shipping products.

## 2. Split authors (149 name keys)

A name key is a last name plus first initial, such as "sato k". A key is flagged when more than one author record with it has an extended-set paper and at least one has a core paper (pipeline/graph.py, log_split_person_candidates). The rule returns 149 keys today (data/work/nc2_evidence.json, flagged_keys_total), the same 149 the stage 4 grapher logged at 06:32 (deliverables/pitfalls_original_log.md). Status says whether a key's records in the team map carry an OpenAlex author ID (identifier).

| OpenAlex ID status | Flagged keys | Sampled | same_person | different_people | cannot_tell |
|---|---|---|---|---|---|
| all_openalex | 60 | 3 | 2 | 1 | 0 |
| mixed | 79 | 11 | 7 | 3 | 1 |
| all_name_only | 10 | 1 | 1 | 0 | 0 |

(N2 section 2)

| Key | Records in map of all | Final |
|---|---|---|
| ding e | 3 of 3 | same_person |
| fu x | 2 of 3 | cannot_tell |
| hu w | 2 of 3 | same_person |
| inoue t | 3 of 3 | same_person |
| li y | 3 of 12 | same_person |
| ma q | 2 of 3 | same_person |
| miles a | 2 of 2 | same_person |
| patterson d | 2 of 3 | same_person |
| sato k | 2 of 2 | same_person |
| schmid s | 6 of 6 | same_person |
| tang s | 2 of 3 | different_people |
| wang j | 4 of 11 | different_people |
| xu y | 2 of 2 | different_people |
| yang y | 3 of 10 | different_people |
| young c | 2 of 2 | same_person |

(N2 section 3, 15 keys drawn with seed 20260927)

Two independent classifiers agreed on 15 of 15 keys (N2 section 4). The same_person share is 10 of 15, or 67 percent, with a 95 percent Wilson interval of 42 to 85 percent. Scaled to 149 keys that is about 99, with a range of 62 to 126 (N2 section 5). Counting only pairs with both records in the map gives 9 of 15 (N2 section 5). An OpenAlex record not joined to an arXiv name-only record is the pattern in 7 of the 10 same_person keys (N2 section 5).

Conclusion. This is mostly a real bug. About two thirds of flagged keys hide one person split into several records, and a sample of 15 leaves the range wide. Person-level rankings need a hand check. Group-level use is safer, because the flag splits a person rather than merging strangers.

## 3. Re-fetch sample size (check a)

Check (a) draws core papers at random and compares title, year, cited_by_count and the first author's first institution with a fresh fetch (deliverables/validation_report.md).

Run 1 used seed 20260926 and drew 20 papers (data/work/audit_round1.json, seed; A1, sample_size). 16 passed and 4 ended as errors (A1, pass, error). The 4 are arxiv:2603.28168, arxiv:2507.08119, arxiv:2608.03146 and arxiv:2306.09713, all arXiv-only (A1, items). Each got HTTP 406 from export.arxiv.org on an id_list lookup, and the same call failed outside the script (validation_report.md, Run 1). Errors were left out of the rate, so the gate passed on 16. Round 2 of run 1 reused the same 20 ids and hit the same 4 errors (data/work/audit_round2.json, a_refetch). No fallback existed, so those 4 were never checked.

Run 2 used seed 20260927 (data/work/audit_run2_round1.json, seed). It drew 20, compared 20 and dropped 0, with 20 pass and 0 fail (A2, drawn, compared, dropped, pass, fail). 16 went by method openalex and 4 by arxiv_html_fallback (A2, items method). Only 2 ids repeat from run 1, W2056973550 and W2529948110 (A1 and A2, sampled_ids). There is no round 2 file, because Gate C passed on round 1 (validation_report.md, Run 2).

| arXiv-only paper | Method | Title | Year | cited_by_count | First institution |
|---|---|---|---|---|---|
| arxiv:2211.02466 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2405.20869 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2501.16907 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2603.07373 | arxiv_html_fallback | match | match | not compared | not compared |

(A2, items subchecks)

The script first tries the arxiv package with delay_seconds=10.0 and num_retries=3 (pipeline/audit.py, refetch_arxiv_api). All 4 still got HTTP 406 (deliverables/pitfalls_original_log.md, stage 7 auditor, 14:57). It then reads the citation_title and citation_date tags from the arxiv.org abstract page. That page has no citation count or institution, so only title and year were compared. The audit file keeps the method but not the first error, so the HTTP 406 reason rests on the log line. Two OpenAlex papers, W4402905306 and W2951487609, also had no first institution to compare (A2, items subchecks).

arXiv-only papers are 36 of the 267 core papers (query on data/db/papers.sqlite, core_set = 1 and openalex_id empty).

Conclusion. Run 1 compared 16 of 20 because the arXiv service refused every id lookup, not because of the sample design. Run 2 compared all 20, but its 4 arXiv-only papers were checked on title and year only.
