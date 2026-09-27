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

Round 1 used seed 20260926 and drew 20 papers (data/work/audit_round1.json, seed; A1, sample_size). 16 passed and 4 ended as errors (A1, pass, error). The 4 are arxiv:2603.28168, arxiv:2507.08119, arxiv:2608.03146 and arxiv:2306.09713, all arXiv-only (A1, items). Each got HTTP 406 from export.arxiv.org on an id_list lookup, and the same call failed outside the script (validation_report.md, round 1). Errors were left out of the rate, so the gate passed on 16. Round 2 reused the same 20 ids and hit the same 4 errors (data/work/audit_round2.json, a_refetch). No fallback existed, so those 4 were never checked.

Round 3 used seed 20260927 (data/work/audit_run2_round1.json, seed). It drew 20, compared 20 and dropped 0, with 20 pass and 0 fail (A2, drawn, compared, dropped, pass, fail). 16 went by method openalex and 4 by arxiv_html_fallback (A2, items method). Only 2 ids repeat from round 1, W2056973550 and W2529948110 (A1 and A2, sampled_ids). Round 3 has no second file, because Gate C passed on its first try (validation_report.md, round 3).

| arXiv-only paper | Method | Title | Year | cited_by_count | First institution |
|---|---|---|---|---|---|
| arxiv:2211.02466 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2405.20869 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2501.16907 | arxiv_html_fallback | match | match | not compared | not compared |
| arxiv:2603.07373 | arxiv_html_fallback | match | match | not compared | not compared |

(A2, items subchecks)

The script first tries the arxiv package with delay_seconds=10.0 and num_retries=3 (pipeline/audit.py, refetch_arxiv_api). All 4 still got HTTP 406 (deliverables/pitfalls_original_log.md, stage 7 auditor, 14:57). It then reads the citation_title and citation_date tags from the arxiv.org abstract page. That page has no citation count or institution, so only title and year were compared. The audit file keeps the method but not the first error, so the HTTP 406 reason rests on the log line. Two OpenAlex papers, W4402905306 and W2951487609, also had no first institution to compare (A2, items subchecks).

arXiv-only papers are 36 of the 267 core papers (query on data/db/papers.sqlite, core_set = 1 and openalex_id empty).

Conclusion. Rounds 1 and 2 compared 16 of 20 because the arXiv service refused every id lookup, not because of the sample design. Round 3 compared all 20, but its 4 arXiv-only papers were checked on title and year only.

## Run 2

The three checks were rerun on run 2's database (data/db/papers.sqlite, after the arXiv via OpenAlex pull and the step 2 anchor rebuild). J2 marks a key in data/work/nc1_run2_route_provenance.json (pipeline/check_route_provenance.py). N3 marks a section of data/work/nc2_run2_name_keys.md (pipeline/merge_name_keys.py). A3 marks the a_refetch block of data/work/audit_s20260929_round1.json (pipeline/audit.py), and R3 marks the code output in data/work/nc3_run2_refetch.md. pipeline/check_route_provenance.py, pipeline/check_name_keys.py and pipeline/merge_name_keys.py were rerun with the run 2 options for this section, and each matched its committed file, as did the R3 code (STATUS.md, step 4 second judge, 22:41). pipeline/audit.py was not rerun, so A3 is the file the step 2 audit wrote (git log of data/work/audit_s20260929_round1.json, commit 4bc8129).

### 1. Papers per tech route

arxiv_via_openalex is the run 2 path that runs a phrase against OpenAlex's index of arXiv papers.

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

(J1, core_route_counts. J2, core_route_counts, q2_snowball_only_core_by_route, q2_core_route_counts_without_snowball_only, route_entry[].by_entry_kind_exclusive.arxiv_via_openalex)

Run 2 has 284 core papers against 267 in run 1 (J2, core_papers. J1, core_papers). 47 core papers have a snowball record and all 47 are snowball only (J2, q2_core_with_any_snowball_record, q2_snowball_only_core_by_route).

The largest route is architecture_only with 105 core papers (J2, largest_route, core_route_counts). Of them 88 entered only through phrase queries, 7 through both an arxiv_via_openalex phrase and a phrase query, 5 only through the snowball, 3 only through an arxiv_via_openalex phrase and 2 only through an anchor lookup (J2, route_entry.architecture_only.by_entry_kind_exclusive).

| Entry path of architecture_only | Core papers |
|---|---|
| arxiv query "optical circuit switch" | 37 |
| openalex query "optical circuit switch" | 24 |
| openalex query "optical circuit switching data center" | 14 |
| openalex query "reconfigurable data center network optical" | 11 |
| openalex query "optical interconnect reconfigurable topology distributed training" | 8 |
| openalex query "optical beam steering switch fiber" | 2 |
| openalex query "optical cross-connect data center" | 2 |
| openalex query "semiconductor optical amplifier switch data center" | 2 |
| openalex query "silicon photonic switch data center" | 1 |
| arxiv_via_openalex "reconfigurable datacenter network" | 6 |
| arxiv_via_openalex "optical circuit switch" | 4 |
| anchor "Expanding across time to deliver bandwidth efficiency and low latency" | 1 |
| anchor "Helios: A Hybrid Electrical/Optical Switch Architecture for Modular Data Centers" | 1 |
| snowball from seed W2141810662 | 2 |
| snowball from seed W2119638333 | 1 |
| snowball from seed W2151668565 | 1 |
| snowball from seed W2937088522 | 1 |

(J2, route_entry.architecture_only.by_entry_path_nonexclusive)

A paper counts once per path, and each raw record keeps only the first query that found it, so the rows overlap and each is a lower bound (data/work/nc1_run2_route_provenance.md). None of the 105 has a UC Berkeley affiliation in the data (J2, route_entry.architecture_only.ucb_affiliated).

The largest device route is still mems_silicon_photonic at 43 (J2, core_route_counts). Its 6 snowball-only papers all came from seed W1982681165, none from the Berkeley anchor W2260723393 (J2, q3_seeds). Its 17 UC Berkeley-affiliated papers and 24 papers sharing an author with the anchor all entered through a phrase query (J2, q1_mems_silicon_photonic.summary).

Conclusion. Section 1's finding holds in run 2, because the snowball adds only 6 of the 43 mems_silicon_photonic papers (J2, q2_snowball_only_core_by_route). arxiv_via_openalex is the only path of 7 thermo_optic papers, equal to that route's rise from 23 to 30, and of at most 3 papers in any other route (J1 and J2, core_route_counts. J2, route_entry[].by_entry_kind_exclusive).

### 2. Split name keys, a fresh sample

The flag rule from section 2 returns 147 keys on run 2's database, the same 147 the stage 4 grapher logged at 16:44 (N3 section 1, deliverables/pitfalls_original_log.md).

| OpenAlex ID status | Flagged keys | Sampled | same_person | different_people | cannot_tell |
|---|---|---|---|---|---|
| all_openalex | 70 | 6 | 1 | 5 | 0 |
| mixed | 69 | 9 | 5 | 3 | 1 |
| all_name_only | 8 | 0 | 0 | 0 | 0 |

(N3 section 2)

15 keys were drawn at random with seed 20260930, not run 1's seed 20260927 (N3 section 3, section 2 above). Two classifiers, A and B, labeled each key without seeing each other's labels (data/work/nc2_run2_class_A.json, data/work/nc2_run2_class_B.json). One of A's summary views came from another agent's helper script, which read only data/work/nc2_run2_evidence.json, so it did not show A any of B's labels (deliverables/pitfalls_original_log.md, step 4 classifier A, 22:27).

| Key | Records in map of all | A | B | Final |
|---|---|---|---|---|
| chen b | 2 of 3 | different_people | different_people | different_people |
| chen g | 2 of 4 | different_people | different_people | different_people |
| chen s | 2 of 4 | same_person | same_person | same_person |
| chen y | 10 of 20 | same_person | same_person | same_person |
| liu z | 6 of 16 | same_person | same_person | same_person |
| patterson d | 2 of 3 | same_person | same_person | same_person |
| singh a | 4 of 4 | same_person | same_person | same_person |
| wei y | 2 of 2 | different_people | different_people | different_people |
| wu j | 4 of 7 | different_people | different_people | different_people |
| xu h | 2 of 3 | cannot_tell | cannot_tell | cannot_tell |
| yang y | 3 of 11 | different_people | different_people | different_people |
| yang z | 2 of 2 | different_people | different_people | different_people |
| zhang h | 3 of 12 | different_people | different_people | different_people |
| zhang j | 2 of 4 | different_people | different_people | different_people |
| zhu y | 3 of 7 | same_person | same_person | same_person |

(N3 section 3)

A and B gave the same label on 15 of 15 keys and listed the same same-person record pairs on 15 of 15 (N3 section 4). The same_person share is 6 of 15, or 40 percent, with a 95 percent Wilson interval of 20 to 64 percent (N3 section 5). Scaled to 147 keys that is about 59, with a range of 29 to 94 (N3 section 5). The cannot_tell key counts as not split. Counting only pairs with both records in the team map gives 5 of 15, or 33 percent (interval 15 to 58 percent) (N3 section 5).

Among the 6 same_person keys, a split joins an OpenAlex record to a name-only record in 3, two name-only records in 1 and two OpenAlex records in 3 (N3 section 5). These add to 7, not 6, because a key can have more than one kind, and liu z has both of the first two kinds (N3 section 5, liu z pairs_same in data/work/nc2_run2_class_A.json and data/work/nc2_run2_class_B.json). The stage 2 merge rule for name-only records cannot cause the last kind, because OpenAlex assigned both IDs itself (N3 section 2).

Conclusion. The bug is real, but run 2's sample does not show that most flagged keys are splits, because its interval of 20 to 64 percent includes half (N3 section 6). Run 1's sample gave 10 of 15 (interval 42 to 85 percent) (section 2 above), so section 2's "mostly a real bug" rests on one sample of 15.

Run 1 and run 2 drew different samples, with different seeds (20260927 in section 2 above, 20260930 in N3 section 3), from different databases (run 1's is data/db/papers.sqlite in commit 8172417, run 2's is the one in place now), and different classifier runs labeled them (data/work/nc2_class_A.json and nc2_class_B.json for run 1, the run 2 files named above). So the move from 10 to 6 of 15 does not show that splitting fell between the runs (section 2 above, N3 section 5). The two intervals overlap from 42 to 64 percent (section 2 above, N3 section 5), and patterson d and yang y, the only keys drawn in both samples, got the same final label both times (section 2 above, N3 section 3). Person-level rankings still need a hand check, and group-level use is still safer.

### 3. Re-fetch sample (check a)

This is the run 2 audit after the anchor papers, seed 20260929 (data/work/audit_s20260929_round1.json, seed). It drew 20, compared 20 and dropped 0, with 20 pass and 0 fail (A3, drawn, compared, dropped, pass, fail). 18 were re-fetched by OpenAlex ID and 2 by the free OpenAlex DOI (digital object identifier) singleton lookup on the arXiv DOI, and 0 used the arxiv.org abstract page (A3, items method). So no paper in this sample depended on the arXiv service.

| Field | Compared | Not compared | Mismatched | Papers not compared |
|---|---|---|---|---|
| title | 20 | 0 | 0 | none |
| year | 20 | 0 | 0 | none |
| cited_by_count | 18 | 2 | 0 | arxiv:2604.22146, arxiv:2507.12265 |
| first_institution | 16 | 4 | 0 | W2951487609, W2260723393, arxiv:2604.22146, arxiv:2507.12265 |

(R3, from A3 items subchecks)

2 papers, the arXiv-only arxiv:2604.22146 and arxiv:2507.12265, were compared on title and year only (R3, title_and_year_only). Their stored cited_by_count is null while OpenAlex returned 0, so our database lacked the value, not the source (A3, items stored, refetched). First institution is null on both sides for both (A3, items stored, refetched). In total 74 of 80 field comparisons were made and 0 mismatched (R3).

The run 2 audit's check (a) text says 0 mismatches "across all 20 papers" (deliverables/validation_report.md, Run 2 audit after the anchor papers, check a). That is true of mismatches but not of fields compared. validation_report.md's later section "Corrections after code review (pull request #4)" already states the 18 and 16 (validation_report.md, item 1 of that section).

Conclusion. All 20 were compared on title and year, but 2 had no stored citation count (R3). The gap goes beyond the sample, because 31 of the 284 core papers are arXiv-only and all 31 have a null cited_by_count (query on data/db/papers.sqlite, core_set = 1, openalex_id empty, cited_by_count null). Check (a) cannot test citation counts for arXiv-only papers until the database stores them.
