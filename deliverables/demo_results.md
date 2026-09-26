# Small-sample demo results

Every number points to a file or to a query Q1 to Q12, listed at the end. Table text is folded to plain ASCII.

## Numbers

Records per raw file, before dedup (Q1, deliverables/curation_report.md).

| file | records |
|---|---|
| data/raw/openalex.jsonl | 707 |
| data/raw/arxiv.jsonl | 47 |
| data/raw/openalex_snowball.jsonl | 150 |
| data/raw/smoke_openalex.jsonl | 5 |
| data/raw/smoke_arxiv.jsonl | 5 |

The 10 smoke records repeat stage 1a records, leaving 904 unique records (deliverables/curation_report.md).

Records per query (Q1). Collectors skip records already on disk, so each record counts only for the first query that found it (deliverables/pitfalls.md, stage 8). The cap is 50 per query (pipeline/queries.yaml).

| source | query | records |
|---|---|---|
| openalex | optical circuit switch | 50 |
| openalex | MEMS optical switch | 49 |
| openalex | robotic fiber patch panel | 49 |
| openalex | wavelength selective switch LCoS | 48 |
| openalex | optical circuit switching machine learning cluster | 47 |
| openalex | 3D MEMS optical cross-connect | 46 |
| openalex | silicon photonic switch data center | 45 |
| openalex | piezoelectric optical switch | 45 |
| openalex | thermo-optic switch port count | 41 |
| openalex | optical beam steering switch fiber | 40 |
| openalex | reconfigurable data center network optical | 40 |
| openalex | semiconductor optical amplifier switch data center | 38 |
| openalex | optical interconnect reconfigurable topology distributed training | 37 |
| openalex | silicon photonic MEMS switch | 34 |
| openalex | optical switching data center survey | 33 |
| openalex | optical circuit switching data center | 30 |
| openalex | optical cross-connect data center | 28 |
| openalex | 7 anchor titles, one record each | 7 |
| openalex snowball | 10 seed papers, 15 records each | 150 |
| arxiv | optical circuit switch | 47 |
| arxiv | the other 9 phrases | 0 |

arXiv's other 9 phrases got HTTP 429 and 406 errors, so their zeros say nothing about arXiv's content (STATUS.md, stage 1a line). Anchors found were 10 of 13, and the c-Through hit is a false match to a 1999 paper titled "OPTICS" (STATUS.md, Gate A line).

OpenAlex reported 0.001 USD (US dollars) for stage 0 and 0.030 USD for stage 1a, and 0.033 USD used after stage 1a (STATUS.md). The snowball cost was not saved (deliverables/pitfalls.md, stage 8).

Relevance scores were 433 at 0, 116 at 1, 72 at 2, and 283 at 3, out of 904 (Q2). 355 scored 2 or 3, above Gate A's 200, so the core set is score 3 only (STATUS.md, Gate A line).

Dedup removed 3 records by DOI (digital object identifier), 4 by arXiv ID, and 12 by fuzzy title, leaving 885 papers (deliverables/curation_report.md), after the checker made the curator undo 3 wrong merges (STATUS.md, stage 2 RETRY line).

| set | papers | no abstract |
|---|---|---|
| all papers | 885 | 78 |
| core set | 267 | 13 |
| extended set (core plus adjacent) | 376 | 24 |

(Q3.) There are 5434 authors and 1342 institutions (deliverables/curation_report.md). 53 core papers have no venue (Q3).

## Technology map

Core papers by tag, out of 267 (Q4, Q5, Q6).

| tech_route | core papers |
|---|---|
| architecture_only | 101 |
| unclear | 44 |
| mems_silicon_photonic | 43 |
| thermo_optic | 23 |
| mems_3d | 15 |
| electro_optic | 12 |
| soa | 11 |
| other | 10 |
| mems_2d | 3 |
| piezo | 2 |
| lcos | 2 |
| robotic_patch_panel | 1 |

| trl_band | core papers |
|---|---|
| lab | 221 |
| unclear | 41 |
| production | 4 |
| pilot | 1 |

| ai_dc_fit | core papers |
|---|---|
| indirect | 93 |
| unclear | 77 |
| direct | 69 |
| none | 28 |

architecture_only is the largest group, 101 of 267 (Q4). These papers use an optical circuit switch (OCS) in a network design rather than build one. Among devices, silicon photonic MEMS (micro-electro-mechanical systems) leads with 43, and three routes have 2 or fewer (Q4). 221 core papers are lab work and 4 are production (Q5).

This does not show which route is better or sells, because the queries have about one phrase per route (pipeline/queries.yaml). 4 of 12 company rows are mems_3d against 15 core papers, and the 2 piezo company rows sit on 2 core papers (Q10, Q4).

## Team map

Top 15 authors (graphs/top_pis.csv, first 15 rows, sorted by core paper count then degree). Degree is the number of distinct co-authors. Betweenness measures how often an author sits between two others.

| author | institution | core_paper_count | extended_paper_count | degree | betweenness | tech_routes | adjacent_field |
|---|---|---|---|---|---|---|---|
| Ming C. Wu | University of California, Berkeley | 24 | 27 | 58 | 0.035771 | mems_2d;mems_silicon_photonic;unclear | mems_micromirror;telecom_oxc_roadm |
| Tae Joon Seok | University of California, Berkeley | 19 | 19 | 26 | 0.000958 | mems_silicon_photonic;unclear |  |
| Niels Quack | Ecole Polytechnique Federale de Lausanne | 16 | 16 | 32 | 0.014096 | mems_silicon_photonic |  |
| Sangyoon Han | University of California, Berkeley | 16 | 16 | 20 | 0.000508 | mems_silicon_photonic;unclear |  |
| R.S. Muller | University of California, Berkeley | 13 | 13 | 23 | 0.000755 | mems_silicon_photonic;unclear |  |
| Keijiro Suzuki | National Institute of Advanced Industrial Science and Technology | 12 | 12 | 31 | 6.2e-05 | thermo_optic;unclear | silicon_photonics |
| Nicola Calabretta | Eindhoven University of Technology | 11 | 11 | 50 | 0.033323 | architecture_only;soa;unclear | silicon_photonics |
| Shu Namiki | National Institute of Advanced Industrial Science and Technology | 11 | 12 | 33 | 0.000121 | architecture_only;thermo_optic;unclear | silicon_photonics;telecom_oxc_roadm |
| Kazuhiro Ikeda | National Institute of Advanced Industrial Science and Technology | 11 | 11 | 23 | 2.7e-05 | thermo_optic;unclear | silicon_photonics |
| George C. Papen | University of California San Diego | 10 | 10 | 46 | 0.022373 | architecture_only;lcos;mems_3d;mems_silicon_photonic;unclear |  |
| Keren Bergman | Columbia University | 10 | 12 | 36 | 0.037728 | architecture_only;electro_optic;unclear |  |
| Hitoshi Kawashima | National Institute of Advanced Industrial Science and Technology | 10 | 10 | 34 | 0.000126 | thermo_optic;unclear | silicon_photonics |
| Ken-ichi Sato | Nagoya University | 10 | 10 | 17 | 0.00012 | architecture_only;other;thermo_optic;unclear |  |
| Georgios Zervas | University of Bristol | 9 | 10 | 49 | 0.014772 | architecture_only;piezo;soa |  |
| Amin M. Vahdat | Google (United States) | 9 | 9 | 43 | 0.01811 | architecture_only;lcos;mems_3d;unclear |  |

Top 10 institutions (graphs/top_institutions.csv, first 10 rows). Here degree counts linked institutions. Authors with no affiliation are left out of this ranking (STATUS.md, stage 4 DONE line).

| institution | author_count | core_paper_count | extended_paper_count | degree | betweenness | tech_routes |
|---|---|---|---|---|---|---|
| University of California, Berkeley | 22 | 27 | 31 | 15 | 0.054689 | mems_2d;mems_silicon_photonic;unclear |
| Eindhoven University of Technology | 34 | 18 | 20 | 19 | 0.100428 | architecture_only;mems_silicon_photonic;soa;thermo_optic;unclear |
| Ecole Polytechnique Federale de Lausanne | 17 | 18 | 19 | 13 | 0.033654 | mems_3d;mems_silicon_photonic;soa |
| National Institute of Advanced Industrial Science and Technology | 32 | 15 | 16 | 2 | 0.006706 | architecture_only;thermo_optic;unclear |
| Columbia University | 20 | 13 | 15 | 15 | 0.084821 | architecture_only;electro_optic;other;unclear |
| University of California San Diego | 26 | 13 | 13 | 6 | 0.007245 | architecture_only;lcos;mems_3d;mems_silicon_photonic;unclear |
| IBM (United States) | 37 | 11 | 12 | 10 | 0.037183 | architecture_only;electro_optic;thermo_optic;unclear |
| University of Bristol | 20 | 10 | 12 | 16 | 0.058963 | architecture_only;piezo;soa |
| Google (United States) | 38 | 10 | 12 | 4 | 0.004677 | architecture_only;lcos;mems_3d;unclear |
| Nagoya University | 7 | 10 | 10 | 2 | 0.013333 | architecture_only;other;thermo_optic;unclear |

Community detection split 1597 authors into 143 communities. The largest has 130 members, 10 are single authors, and in 51 no member has a core paper, so their dominant route is "none" (Q7). The ten largest follow (graphs/clusters.csv, members ranked by graphs/top_pis.csv order).

| community_id | size | dominant_tech_route | three highest-ranked members |
|---|---|---|---|
| 0 | 130 | architecture_only | Keren Bergman; Qixiang Cheng; Madeleine Strom Glick |
| 1 | 107 | unclear | John Edward Bowers; Graham T. Reed; David J. Thomson |
| 2 | 105 | architecture_only | Nicola Calabretta; Georgios Zervas; Xuwei Xue |
| 3 | 94 | electro_optic | Benjamin G. Lee; William M. J. Green; Clint L. Schow |
| 4 | 87 | mems_silicon_photonic | Ming C. Wu; Tae Joon Seok; Niels Quack |
| 5 | 44 | thermo_optic | Keijiro Suzuki; Shu Namiki; Kazuhiro Ikeda |
| 6 | 42 | mems_silicon_photonic | Huan Li; Daoxin Dai; Yinpeng Hu |
| 7 | 39 | none | Marko Loncar; Lin Chang; Mengjie Yu |
| 8 | 38 | architecture_only | Cedric Fung Lam; Daniel N. Nelson; Erji Mao |
| 9 | 35 | mems_3d | David T. Neilson; F. Pardo; Paul R. Kolodner |

The co-author plot is [graphs/coauthor.html](../graphs/coauthor.html), one self-contained file with nodes colored by route and adjacent-only authors hollow (STATUS.md, stage 4 DONE line).

The core groups are clear. They are the University of California (UC) Berkeley silicon photonic MEMS group (Ming C. Wu, 24 core papers), the AIST (National Institute of Advanced Industrial Science and Technology) thermo-optic group (Keijiro Suzuki, 12), the Eindhoven semiconductor optical amplifier and architecture group (Nicola Calabretta, 11), and UC San Diego with Google on architecture and 3D MEMS (George C. Papen 10, Amin M. Vahdat 9), with all counts from graphs/top_pis.csv.

The adjacent side is large. 553 of 1597 authors have no core paper (Q8). Communities 7 and 10 have no core route, and 33 of 39 and 31 of 31 of their members carry the silicon_photonics field (graphs/clusters.csv joined to graphs/top_pis.csv). These groups are the "transferable teams" pool, and their data is weakest. 26 of 109 extended-only papers lost their adjacent field in tagging (STATUS.md, stage 4 DONE line), 301 authors have no affiliation (Q8), and 149 name keys map to more than one author record (deliverables/pitfalls.md, 06:32). Keren Bergman, for example, has one record with 10 core papers and another with 1 (graphs/top_pis.csv).

## Early project map

12 rows for 12 entities, 5 shipping, 2 prototype, and 5 unknown (Q10), sorted by stage and then newest evidence date. "row" is the row number in data/projects.csv.

| row | entity | entity_type | product_or_project | tech_route | stage | first_public_date | evidence_date | evidence_url | evidence_quote |
|---|---|---|---|---|---|---|---|---|---|
| 4 | Calient | established_vendor | S320 Optical Circuit Switch | mems_3d | shipping | unknown | 2026-09-26 | https://www.calient.net/ | With over 1 million port switches shipped, we're automating & accelerating change across industries. |
| 5 | Polatis | established_vendor | POLATIS 6000/7000 Series Optical Circuit Switch | piezo | shipping | unknown | 2026-09-26 | https://www.hubersuhner.com/en/optical-circuit-switching | makes connections using compact piezo-electric actuators to align collimated beams of light from opposing arrays of input and output fibers |
| 7 | iPronics | startup | ONE-32 Optical Networking Engine (silicon photonics OCS) | unclear | shipping | 2025-03-31 | 2025-03-31 | https://ipronics.com/ipronics-unveils-worlds-first-silicon-photonics-optical-circuit-switch-for-ai-driven-data-centers-optical-network-transformation/ | Available from May 2025, ONE-32 advances iPronics' vision of optical innovation to enable a future proof AI Data Center network. |
| 6 | Telescent | startup | G5 Robotic Patch Panel | robotic_patch_panel | shipping | 2024-03-21 | 2024-03-21 | https://www.telescent.com/latest-news/2024/3/21/telescent-introduces-new-g5-robotic-patch-panel-system | announces today the launch of its new G5 Robotic Patch Panel system |
| 1 | Google | hyperscaler_internal | Apollo OCS (Palomar MEMS switch) | mems_3d | shipping | unknown | 2022-08-23 | https://cloud.google.com/blog/topics/systems/the-evolution-of-googles-jupiter-data-center-network | Over multiple years, we designed and built Apollo OCS that now forms the basis for the vast majority of our data center networks. |
| 11 | UTStarcom | established_vendor | MOS64 (MEMS) and UOS64 (silicon photonics) OCS concept prototypes | mems_3d | prototype | 2026-09-21 | 2026-09-21 | https://www.financialcontent.com/article/gnwcq-2026-9-21-utstarcom-unveils-optical-circuit-switching-ocs-solution-for-ai-data-centers-at-cioe-2026 | unveiled concept prototypes of its next-generation Optical Circuit Switching (OCS) platform designed specifically for AI data center (AI DC) networking infrastructure |
| 8 | nEye | startup | OCS-on-a-chip | mems_silicon_photonic | prototype | unknown | 2026-04-14 | https://neye.ai | nEye's unique OCS-on-a-chip moves from the lab to the fab. |
| 2 | Lumentum | established_vendor | R300 Optical Circuit Switch (300x300 OCS) | mems_3d | unknown | unknown | 2026-09-26 | https://www.lumentum.com/en/products/300x300-optical-circuit-switch-ocs | Built on field-proven Lumentum micro-electro-mechanical systems (MEMS) technology with over a trillion mirror operating hours |
| 9 | Oriole Networks | startup | PRISM photonic networking platform | unclear | unknown | unknown | 2026-09-26 | https://oriolenetworks.com/ | Introducing PRISM, the Oriole solution that replaces energy hungry electrical switching with photonic switching. |
| 10 | Drut Technologies | startup | Photonic-native infrastructure built on POLATIS OCS | piezo | unknown | unknown | 2026-09-26 | https://www.polatis.com/press-releases/POLATIS_optical_circuit_switch_powers_SCinet_Network_at_SC25_and_showcased_in_Drut_Photonic_Infrastructure_for_AI.asp | another POLATIS OCS features as a key component of the dynamic photonic fabric in Drut Technologies' next-generation |
| 12 | Lightmatter | startup | Passage M1000 photonic interposer (built-in solid-state OCS) | unclear | unknown | unknown | 2026-09-26 | https://futurumgroup.com/insights/lightmatter-solving-how-to-interconnect-millions-of-chips/ | The M1000 employs solid-state optical circuit switching, while the L200 incorporates Alphawave Semi's chiplet technology |
| 3 | Coherent | established_vendor | Optical Circuit Switch (DLX-based, up to 512x512) | lcos | unknown | 2024-03-25 | 2024-03-25 | https://www.coherent.com/news/press-releases/optical-circuit-switch-for-data-centers-live-demo-at-ofc-2024-based-on-ultrareliable-dlx-technology | a new optical circuit switch (OCS) based on the company's field-proven and ultrareliable digital liquid-crystal technology |

Several evidence dates are fetch dates (data/projects.csv, note column). Polatis "shipping" rests on shop links, not a quoted sentence (deliverables/comparison_matrix.csv, piezo trl_band note). Microsoft Sirius was dropped because its site throttled every fetch (deliverables/pitfalls.md, 06:10).

## Comparison matrix

The full matrix with paper IDs and quotes is deliverables/comparison_matrix.md, written by pipeline/matrix_render.py. Its top-level table follows, with cells cut at 70 characters by the script (TABLE_CELL_MAX).

| tech_route | switching_time | insertion_loss | port_count | polarization_dependent_loss | crosstalk | wavelength_range | integration | packaging_notes | trl_band | academic_groups | companies | ai_cluster_fit | cost_per_port | scaling_limit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mems_3d | 150 us to few ms | 1.33 to 4.0 dB | exceeding 1100 ports | [not reported] | [not reported] | 1500 to 1630 nm (S, C and L bands) | free_space_bulk (collimator array and MEMS mirror array) | cubic switch housing, tolerance-expansion packaging and shock absor... | production | Michal Stepanovsky (Czech Technical University in Prague) 3; Joseph... | Google (row 1, stage shipping); Lumentum (row 2, stage unknown); Ca... | partial (datacenter applications) | 100 USD per port | switching speed falls as port count grows (mirror optics and kinema... |
| mems_2d | less than 1 us to tens of ms (all MEMS cross-connect types) | [not reported] | 16 x 16 ports | [not reported] | [not reported] | [not reported] | free_space_bulk (reflective mirrors) | packaged single-chip component; mechanical cell design chosen for r... | lab (demonstrated, fabricated) | Ming C. Wu (University of California, Berkeley) 2; Steffen Gloeckne... | [no source] | no | [not reported] | [not reported] |
| mems_silicon_photonic | 0.4 to 200 us | 3.7 to 22.7 dB | 128 x 128 ports | 0.5 to 8.5 dB | -80 to -30 dB | 1250 to 1700 nm | integrated_photonic | grating-coupler fiber attach through flip-chip interposers and fibe... | lab (fabricated) | Ming C. Wu (University of California, Berkeley) 19; Tae Joon Seok (... | nEye (row 8, stage prototype) | yes | [not reported] | electrical connections grow as N squared with individual addressing... |
| lcos | 11.5 us | approximately 2 dB (projected net loss) | 1 x 6 core selective switch prototype; 23-host network prototype | [not reported] | [not reported] | [not reported] | free_space_bulk | multicore fiber collimator and spatial multiplexer array integrated... | lab (prototype) | George C. Papen (University of California San Diego) 1; Amin M. Vah... | Coherent (row 3, stage unknown), optical circuit switch on digital... | partial (future datacenters) | [not reported] | [not reported] |
| piezo | millisecond | below 2.2 dB | 3 ports demonstrated; 50 by design | [not reported] | -25 dB (design, intercore crosstalk after 1 km) | 1550 nm (design assumption) | free_space_bulk (collimated beams between opposing fiber arrays) | multicore fibers integrated directly into the switch ports | lab (development of the first multi-lane switch) | Nick Parsons (Polatis (United Kingdom)) 2; Georgios Zervas (Univers... | Polatis (row 5, stage shipping); Drut Technologies (row 10, stage u... | partial (data center network, DCN) | [not reported] | port count set by maximum steering angle and port separation; more... |
| thermo_optic | 3.52 to 100 us | 1.74 to 15.8 dB | 32 x 32 ports | around 2 dB | -50 to -20 dB | C+L band; 110 nm window | integrated_photonic | flip-chip bonding to a ceramic land grid array interposer; wire-bon... | lab (demonstration) | Keijiro Suzuki (National Institute of Advanced Industrial Science a... | [no source] | yes | [not reported] | control units and wiring grow quickly with port count; waveguide cr... |
| electro_optic | 3 to 4 ns | 1 to 18.5 dB | 32 x 32 ports | [not reported] | -24.8 to -9 dB | 7 to 110 nm of optical bandwidth | integrated_photonic (monolithically integrated matrix switches) | monolithic integration with CMOS logic and driver circuits on the s... | lab (fabricated) | William M. J. Green (IBM (United States)) 4; Benjamin G. Lee (IBM (... | [no source] | partial (data center interconnection networks) | [not reported] | crosstalk accumulates across stages and limits fabric size; fabrica... |
| soa | 115 to 900 ps | net gain of more than 14.3 dB for a gate switch; InP WDM switches d... | 4 x 4 monolithic cross-connect; 128 x 128 emulated in a recirculati... | [not reported] | [not reported] | [not reported] | integrated_photonic (monolithic cross-connect) | chip-on-carrier SOA; quantum-dot SOA switch elements can run uncooled | lab (we demonstrate) | Xuwei Xue (Eindhoven University of Technology) 3; Nicola Calabretta... | [no source] | partial (computing systems and data networks) | [not reported] | signal degradation and power grow with network size, which limits f... |
| robotic_patch_panel | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | mechanical_fiber | connection mechanisms handle angled physical contact connector plug... | production (vendor product launch) | Mitsuhiro Makihara (NTT (Japan)) 1; Masato MIZUKAMI (NTT (Japan)) 1 | Telescent (row 6, stage shipping), G5 Robotic Patch Panel | no | [not reported] | [not reported] |

Of the 126 cells, 82 are reported, 31 are not reported in any abstract, 9 are derived by a script, and 4 have no source (Q9).

## Audit results

From deliverables/validation_report.md, seed 20260926, same samples in both rounds.

| check | round 1 | round 2 | Gate C limit | result |
|---|---|---|---|---|
| (a) re-fetch 20 core papers | 16 pass, 0 fail, 4 errors, 0 percent mismatch | same | at most 10 percent | PASS both rounds |
| (b) 20 reported matrix cells | 15 pass, 5 fail, 25 percent unsupported | 20 pass, 0 fail, 0 percent | at most 10 percent | FAIL round 1, PASS round 2 |
| (c) 10 project rows | 10 pass, 0 fail, 0 unreachable | same | at most 20 percent | PASS both rounds |
| (d) all 376 evidence spans | 376 pass, 100 percent | same | at least 90 percent | PASS both rounds |

Round 1 failed check (b) and sent the run back to stage 6 once. The auditor's words on the 5 failing cells follow (deliverables/validation_report.md).

| cell | cites | value | auditor's words |
|---|---|---|---|
| soa:ai_cluster_fit | W2056973550, W3093967660 | partial | The quote describes the switch fabric's use case in general terms and never uses a word close to partial, yes, or no. |
| electro_optic:integration | W2094700182, W1979338531 | integrated_photonic | The quote describes a Mach-Zehnder switch in silicon but does not use the words integrated or photonic. |
| mems_3d:integration | W3215039088, W2560361359 | free_space_bulk | The quote describes a microlens and MEMS mirror array, which is free-space bulk optics by the framework's own definition, but the quote does not use the words free, space, or bulk. |
| mems_silicon_photonic:trl_band | W3138799074, project row 8 | lab | The quote describes CMOS foundry fabrication and does not use the word lab or a synonym. |
| piezo:trl_band | project row 5, no paper_id | production (vendor) | The quote describes the switching mechanism only and does not use the word production. |

The auditor called this "a real property of how those cells were filled, not noise in the check". The problem was not limited to the sample. In round 2 the auditor reported that "the pre-fix version of the test failed 21 of 82 cells before the rewrite" (deliverables/validation_report.md, round 2 check (b)). After round 2 it left two problems open. The 4 arXiv-only papers of check (a) "still have never been successfully re-checked against their source in either audit round", and on piezo:trl_band "The fix corrected what the cell asserts, not the thinness of its evidence base" (deliverables/validation_report.md).

The checker found problems in the audit itself. In its words, "the audit value test is now circular because matrix_build.py imports pipeline.audit.value_in_quote", so its own hand read of the 20 sampled values, which found all 20 supported, is the real evidence (STATUS.md, stage 7 DONE line). To pass that test, "18 of 27 reported categorical cells" now carry quote words outside the skill's fixed vocabulary (same line). The round 1 report "says 7 of 20 sampled cells cite a project row (actual 3)", and its claim that 4 of 5 failures sit on thin routes holds for 1 of 5 (STATUS.md, stage 7 RETRY line). Also "the report says piezo:trl_band is built from projects.csv row 5 but the CSV cell cites no project row" (STATUS.md, stage 7 DONE line). The checker did match the 4 arXiv papers on title and year from arxiv.org/abs pages (same line).

## Queries used above

Run from the repo root. Q11 and Q12 back counts in open_questions.md and framework.md.

| query | command |
|---|---|
| Q1 | `.venv/bin/python -c "import json,glob,collections as c; [print(f, c.Counter(json.loads(l)['query'] for l in open(f,encoding='utf-8') if l.strip())) for f in sorted(glob.glob('data/raw/*.jsonl'))]"` |
| Q2 | `.venv/bin/python -c "import pandas as pd; print(pd.read_csv('data/raw/relevance.csv').score.value_counts())"` |
| Q3 | `.venv/bin/python -c "import sqlite3; print(sqlite3.connect('data/db/papers.sqlite').execute('select count(*), sum(core_set), sum(extended_set), sum(abstract is null), sum(core_set=1 and abstract is null), sum(extended_set=1 and abstract is null), sum(core_set=1 and venue is null) from papers').fetchall())"` |
| Q4, Q5, Q6 | `.venv/bin/python -c "import sqlite3; db=sqlite3.connect('data/db/papers.sqlite'); [print(c, db.execute(f'select t.{c}, count(*) from tags t join papers p using(paper_id) where p.core_set=1 group by 1 order by 2 desc').fetchall()) for c in ('tech_route','trl_band','ai_dc_fit')]"` |
| Q7 | `.venv/bin/python -c "import pandas as pd; c=pd.read_csv('graphs/clusters.csv'); print(len(c), c['size'].sum(), c['size'].max(), (c['size']==1).sum(), (c.dominant_tech_route=='none').sum())"` |
| Q8 | `.venv/bin/python -c "import pandas as pd; t=pd.read_csv('graphs/top_pis.csv'); print(len(t), (t.core_paper_count==0).sum(), (t.institution=='unknown').sum())"` |
| Q9 | `.venv/bin/python -c "import pandas as pd; print(pd.read_csv('deliverables/comparison_matrix.csv').status.value_counts())"` |
| Q10 | `.venv/bin/python -c "import pandas as pd; p=pd.read_csv('data/projects.csv'); print(len(p), p.stage.value_counts().to_dict(), p.tech_route.value_counts().to_dict())"` |
| Q11 | `.venv/bin/python -c "import sqlite3; db=sqlite3.connect('data/db/papers.sqlite'); [print(p, db.execute('select count(*), sum(core_set) from papers where venue like ?', (p,)).fetchone()) for p in ('%Optical Fiber Communication%','%SIGCOMM%','%NSDI%','%Networked Systems%','%APEC%','%Applied Power Electronics%','%ECCE%','%Energy Conversion Congress%','%PCIM%','arXiv (Cornell University)')]"` |
| Q12 | `.venv/bin/python -c "import sqlite3; print(sqlite3.connect('data/db/papers.sqlite').execute('select adjacent_field, count(*) from tags join papers using(paper_id) where extended_set=1 and core_set=0 group by 1 order by 2 desc').fetchall())"` |
