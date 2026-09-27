# Small-sample demo results

Every number points to a file or to a query Q1 to Q17, listed at the end. Numbers describe run 2, the arXiv rebuild, unless marked run 1. Run 2 took arXiv content through OpenAlex's arXiv index and labels it arxiv_via_openalex (STATUS.md, 16:50 line). Rounds 1 to 3 are run 1's audits. The auditor runs the four checks, and the second judge re-checks each stage. MEMS is micro-electro-mechanical systems.

## Numbers

### Run 1 versus run 2

| measure | run 1 | run 2 | source |
|---|---|---|---|
| raw records, data/raw/openalex.jsonl | 707 | 707 | STATUS.md, 05:04 line; Q1 |
| raw records, data/raw/openalex_snowball.jsonl | 150 | 150 | STATUS.md, 05:38 line; Q1 |
| raw records, data/raw/arxiv.jsonl (arXiv's API, application programming interface) | 47 | 47 | STATUS.md, 05:04 line; Q1 |
| raw records, data/raw/arxiv_via_openalex.jsonl | 0 (no such file) | 341 | Q1 |
| raw records, the two smoke files | 10 | 10 | STATUS.md, 04:41 line; Q1 |
| unique raw records | 904 | 1245 | STATUS.md, 05:39 and 16:08 lines |
| papers after dedup | 885 | 1213 | STATUS.md, 05:57 line; Q3 |
| core set | 267 | 284 | STATUS.md, 05:57 line; Q3 |
| extended set | 376 | 420 | STATUS.md, 05:57 line; Q3 |
| arXiv-only papers, every source is arxiv or arxiv_via_openalex (of them core) | 40 (36) | 368 (53) | data/work/run2_arxiv_coverage.md; Q15 |
| papers with no OpenAlex ID (identifier), paper_id "arxiv:..." (of them core) | 40 (36) | 34 (31) | data/work/run2_arxiv_coverage.md; Q15 |
| authors in the database | 5434 | 7624 | STATUS.md, 05:57 line; deliverables/curation_report.md |
| authors in the team map | 1597 | 1827 | STATUS.md, 06:50 line; Q8 |
| institutions | 1342 | 1641 | STATUS.md, 05:57 line; deliverables/curation_report.md |
| audit (a), re-fetch mismatch rate | 0 percent, 20 of 20 compared (round 3) | 0 percent, 20 of 20 compared | deliverables/validation_report.md, round 3 and Run 2 audit |
| audit (b), unsupported sampled cells | 5 percent, 1 of 20 (round 3) | 15 percent, 3 of 20, FAIL on the first try, then 0 percent, 0 of 20 | same |
| audit (c), failed project links | 0 percent, 0 of 10 (round 3) | 0 percent, 0 of 10 | same |
| audit (d), verbatim evidence spans | 100 percent, 376 of 376 (round 3) | 100 percent, 420 of 420 | same |
| OpenAlex cost | 0.033 USD (US dollars) after stage 1a, 0.0404 USD at the finish, snowball cost not saved | 0.01 USD for the 10 new searches, 0.01 USD more for a rerun | STATUS.md, stage 1a, 16:14 and 15:58 lines; deliverables/pitfalls_original_log.md, 16:05 |

Run 1 had no arxiv_via_openalex file, so its 40 arXiv-only papers had only arxiv records, and Q15 still finds all 40.

### arXiv coverage gap before run 2

On the run 1 database, 133 of 885 papers were arXiv-hosted, meaning they had an arXiv ID, an arXiv DOI (digital object identifier), or an arxiv.org link. 40 of them had no OpenAlex ID, and in the core set 36 of 43 had none (data/work/run2_arxiv_coverage.md, query Q16). Run 2 closed little of that gap. Only 6 of the 40 gained an OpenAlex ID (deliverables/curation_report.md), and 31 of 60 arXiv-hosted core papers still have none (Q16).

### Records per source and query

Records per query (Q1) count the first query that found each record (deliverables/pitfalls.md, stage 8), capped at 50 (pipeline/queries.yaml).

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
| arxiv (run 1) | optical circuit switch | 47 |
| arxiv (run 1) | the other 9 phrases | 0 |
| arxiv_via_openalex (run 2) | wavelength selective switch | 45 |
| arxiv_via_openalex (run 2) | reconfigurable datacenter network | 44 |
| arxiv_via_openalex (run 2) | MEMS optical switch | 40 |
| arxiv_via_openalex (run 2) | piezoelectric optical switch | 39 |
| arxiv_via_openalex (run 2) | optical cross-connect | 39 |
| arxiv_via_openalex (run 2) | optical interconnect machine learning training | 37 |
| arxiv_via_openalex (run 2) | optical circuit switch | 33 |
| arxiv_via_openalex (run 2) | thermo-optic switch | 33 |
| arxiv_via_openalex (run 2) | silicon photonic switch | 31 |
| arxiv_via_openalex (run 2) | optical circuit switching | 0 new (STATUS.md, 15:58 line) |

In run 1, arXiv's other 9 phrases got HTTP (web protocol) errors 429 and 406, so their zeros say nothing about arXiv's content (STATUS.md, stage 1a line). Run 1 found 10 of 13 anchors, one a false match, and run 2 ran no anchor lookup, so Jupiter Evolving and RotorNet are still missing (STATUS.md, Gate A line; Q17).

### Relevance and dedup

Because more than 200 records scored 2 or 3, Gate A kept score 3 only as the core set (PLAN.md; STATUS.md, 16:08 line).

| step | count | source |
|---|---|---|
| relevance score 0, 1, 2, 3 (of 1245) | 694, 145, 98, 308 | Q2 |
| score 2 or 3, before dedup | 416 | STATUS.md, 16:08 line |
| duplicates removed by DOI, arXiv ID, fuzzy title | 4, 15, 13 | deliverables/curation_report.md |
| arxiv_via_openalex records that matched a run 1 paper by DOI, arXiv ID, fuzzy title | 0, 8, 2 | deliverables/curation_report.md |
| wrong fuzzy merges undone after the run 1 retry | 3 | STATUS.md, 05:51 line |
| papers after dedup | 1213 | deliverables/curation_report.md |

| set | papers | no abstract |
|---|---|---|
| all papers | 1213 | 112 |
| core set | 284 | 14 |
| extended set (core plus adjacent) | 420 | 26 |

(Q3.) 53 core papers have no venue (Q3).

## Technology map

Core papers by tag, run 2 from Q4, Q5, and Q6, run 1 from STATUS.md, 06:27 line.

| tech_route | run 1 core | run 2 core |
|---|---|---|
| architecture_only | 101 | 105 |
| unclear | 44 | 44 |
| mems_silicon_photonic | 43 | 43 |
| thermo_optic | 23 | 30 |
| mems_3d | 15 | 16 |
| electro_optic | 12 | 14 |
| other | 10 | 13 |
| soa | 11 | 11 |
| mems_2d | 3 | 3 |
| piezo | 2 | 2 |
| lcos | 2 | 2 |
| robotic_patch_panel | 1 | 1 |

| trl_band | run 1 core | run 2 core |
|---|---|---|
| lab | 221 | 236 |
| unclear | 41 | 43 |
| production | 4 | 4 |
| pilot | 1 | 1 |

| ai_dc_fit | run 1 core | run 2 core |
|---|---|---|
| indirect | 93 | 91 |
| unclear | 77 | 81 |
| direct | 69 | 74 |
| none | 28 | 38 |

architecture_only is the largest group, 105 of 284 (Q4). These papers use an optical circuit switch (OCS) in a network design rather than build one. Among devices, silicon photonic MEMS leads with 43, thermo_optic grew most, and 236 core papers are lab work (Q4, Q5).

The 43 reflects how the sample was built. In run 1 one phrase supplied 27 of the 43, and the only 3D MEMS phrase added 0 core papers (deliverables/number_checks.md, section 1). Phrase queries start in 2012, and 4 of 16 mems_3d core papers are older, against 3 of 43 (pipeline/queries.yaml; Q14).

## Team map

Top 15 authors (graphs/top_pis.csv, first 15 rows). Degree is the number of distinct co-authors. Betweenness measures how often an author sits between two others.

| author | institution | core_paper_count | extended_paper_count | degree | betweenness | tech_routes | adjacent_field |
|---|---|---|---|---|---|---|---|
| Ming C. Wu | University of California, Berkeley | 24 | 27 | 58 | 0.037677 | mems_2d;mems_silicon_photonic;unclear | mems_micromirror;telecom_oxc_roadm |
| Tae Joon Seok | University of California, Berkeley | 19 | 19 | 26 | 0.0009 | mems_silicon_photonic;unclear |  |
| Niels Quack | Ecole Polytechnique Federale de Lausanne | 16 | 16 | 32 | 0.014328 | mems_silicon_photonic |  |
| Sangyoon Han | University of California, Berkeley | 16 | 16 | 20 | 0.000483 | mems_silicon_photonic;unclear |  |
| R.S. Muller | University of California, Berkeley | 13 | 13 | 23 | 0.000712 | mems_silicon_photonic;unclear |  |
| Shu Namiki | National Institute of Advanced Industrial Science and Technology | 12 | 13 | 36 | 0.000138 | architecture_only;thermo_optic;unclear | silicon_photonics;telecom_oxc_roadm |
| Keijiro Suzuki | National Institute of Advanced Industrial Science and Technology | 12 | 12 | 31 | 4.7e-05 | thermo_optic;unclear | silicon_photonics |
| Nicola Calabretta | Eindhoven University of Technology | 11 | 11 | 50 | 0.031061 | architecture_only;soa;unclear | silicon_photonics |
| Kazuhiro Ikeda | National Institute of Advanced Industrial Science and Technology | 11 | 11 | 23 | 2.1e-05 | thermo_optic;unclear | silicon_photonics |
| Ken-ichi Sato | Nagoya University | 11 | 11 | 21 | 0.000117 | architecture_only;other;thermo_optic;unclear |  |
| George C. Papen | University of California San Diego | 10 | 10 | 46 | 0.022838 | architecture_only;lcos;mems_3d;mems_silicon_photonic;unclear |  |
| Keren Bergman | Columbia University | 10 | 12 | 36 | 0.038859 | architecture_only;electro_optic;unclear |  |
| Hitoshi Kawashima | National Institute of Advanced Industrial Science and Technology | 10 | 10 | 34 | 0.000101 | thermo_optic;unclear | silicon_photonics |
| Georgios Zervas | University of Bristol | 9 | 10 | 49 | 0.012832 | architecture_only;piezo;soa |  |
| Amin M. Vahdat | Google (United States) | 9 | 9 | 43 | 0.018839 | architecture_only;lcos;mems_3d;unclear |  |

Top 10 institutions (graphs/top_institutions.csv, first 10 rows). Degree counts linked institutions, and authors with no affiliation are left out (STATUS.md, 16:47 line).

| institution | author_count | core_paper_count | extended_paper_count | degree | betweenness | tech_routes |
|---|---|---|---|---|---|---|
| University of California, Berkeley | 22 | 27 | 31 | 15 | 0.05563 | mems_2d;mems_silicon_photonic;unclear |
| Eindhoven University of Technology | 34 | 18 | 20 | 19 | 0.078198 | architecture_only;mems_silicon_photonic;soa;thermo_optic;unclear |
| Ecole Polytechnique Federale de Lausanne | 17 | 18 | 19 | 13 | 0.025755 | mems_3d;mems_silicon_photonic;soa |
| National Institute of Advanced Industrial Science and Technology | 32 | 16 | 17 | 2 | 0.005926 | architecture_only;thermo_optic;unclear |
| University of California San Diego | 32 | 15 | 16 | 9 | 0.023831 | architecture_only;lcos;mems_3d;mems_silicon_photonic;thermo_optic;unclear |
| Columbia University | 20 | 13 | 15 | 15 | 0.07978 | architecture_only;electro_optic;other;unclear |
| IBM (United States) | 37 | 11 | 13 | 13 | 0.040193 | architecture_only;electro_optic;thermo_optic;unclear |
| Nagoya University | 7 | 11 | 11 | 2 | 0.011793 | architecture_only;other;thermo_optic;unclear |
| University of Bristol | 20 | 10 | 12 | 16 | 0.04783 | architecture_only;piezo;soa |
| NTT (Japan) | 22 | 10 | 11 | 11 | 0.044388 | architecture_only;mems_3d;other;robotic_patch_panel;unclear |

Community detection split 1827 authors into 159 communities. The largest has 164 members, 11 are single authors, and in 56 no member has a core paper, so their dominant route is "none" (Q7). The ten largest follow (graphs/clusters.csv, members in graphs/top_pis.csv order).

| community_id | size | dominant_tech_route | three highest-ranked members |
|---|---|---|---|
| 0 | 164 | architecture_only | Nicola Calabretta; Keren Bergman; Georgios Zervas |
| 1 | 138 | architecture_only | Ming C. Wu; Tae Joon Seok; Niels Quack |
| 2 | 102 | electro_optic | Benjamin G. Lee; William M. J. Green; Clint L. Schow |
| 3 | 98 | unclear | John Edward Bowers; Avantika Sohdi; Luke S. Theogarajan |
| 4 | 83 | unclear | Graham T. Reed; David J. Thomson; Yu Yu |
| 5 | 50 | architecture_only | Kai Chen; Kishore Ramachandran; Ankit Singla |
| 6 | 47 | thermo_optic | Shu Namiki; Keijiro Suzuki; Kazuhiro Ikeda |
| 7 | 46 | architecture_only | Eiji Oki; Pierre-Alexandre Blanche; Kazuya Anazawa |
| 8 | 42 | mems_silicon_photonic | Huan Li; Daoxin Dai; Yinpeng Hu |
| 9 | 39 | mems_silicon_photonic | H. Y. Fu; Richard E. Jones; John M. Heck |

The co-author plot is [graphs/coauthor.html](../graphs/coauthor.html), self-contained, with nodes colored by route and adjacent-only authors hollow (STATUS.md, 06:50 and 16:47 lines).

The core groups are UC (University of California) Berkeley on silicon photonic MEMS, AIST (National Institute of Advanced Industrial Science and Technology) on thermo-optic switches, Eindhoven on amplifier switches and architecture, and UC San Diego with Google on architecture and 3D MEMS (graphs/top_pis.csv).

The adjacent side is large, since 720 of 1827 authors have no core paper (Q8). In communities 11 and 12, which have no core member, 31 of 34 and 12 of 31 members carry the silicon_photonics field (graphs/clusters.csv joined to graphs/top_pis.csv). This "transferable teams" pool has the weakest data, because 33 of 136 extended-only papers have no adjacent field (Q12) and 338 authors have no affiliation (Q8).

Split people affect the whole map. In run 1, 10 of 15 sampled flagged name keys (last name plus first initial) were one person in several records, about 99 of 149 keys (62 to 126) (deliverables/number_checks.md, section 2). Run 2 flags 147 keys (STATUS.md, 16:47 line). Person rankings need a hand check.

## Early project map

Run 2 skipped the scout (STATUS.md, 16:50 line), so these are run 1's 12 rows (Q10), sorted by stage and then newest evidence date. "row" is the row number in data/projects.csv.

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

Several evidence dates are fetch dates (data/projects.csv, note column). Polatis "shipping" is the scout's stage, and its quote "describes the mechanism and not availability" (deliverables/comparison_matrix.csv, piezo trl_band note).

## Comparison matrix

The full matrix with paper IDs and quotes is deliverables/comparison_matrix.md, written by pipeline/matrix_render.py. Its top-level table follows, cut at 70 characters per cell by the script (TABLE_CELL_MAX).

| tech_route | switching_time | insertion_loss | port_count | polarization_dependent_loss | crosstalk | wavelength_range | integration | packaging_notes | trl_band | academic_groups | companies | ai_cluster_fit | cost_per_port | scaling_limit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mems_3d | 150 us to few ms | 1.2 to 4.0 dB | more than 1100 ports | -30 dB as printed | [not reported] | 1500 to 1630 nm | free_space_bulk | Stable cubic switch housing and tolerance-expanding assembly; compa... | production | Michal Stepanovsky (Czech Technical University in Prague) 3 papers;... | Google; Lumentum; Calient; UTStarcom | yes | 100 USD per port | Switching speed falls as port count grows; cross-axis coupling of m... |
| mems_2d | [not reported] | [not reported] | 16 x 16 ports | [not reported] | [not reported] | [not reported] | free_space_bulk | Reliable actuation reported to carry over to the packaged component... | lab | Ming C. Wu (University of California, Berkeley) 2 papers; Steffen G... | [no source] | no | [not reported] | [not reported] |
| mems_silicon_photonic | 0.4 to 200 us | 0.18 to 22.7 dB | 128 x 128 ports | 0.5 to 8.5 dB | -30 to -80 dB | 1250 to 1700 nm | integrated_photonic | Aluminum nitride interposer and 64-channel lidless fiber array; thr... | lab | Ming C. Wu (University of California, Berkeley) 19 papers; Tae Joon... | nEye | yes | [not reported] | Electrical interconnects grow as N squared with individual addressi... |
| lcos | 11.5 us | approximately 2 dB | 1 x 6 ports | [not reported] | [not reported] | [not reported] | free_space_bulk | Multicore-fiber collimator, spatial multiplexer array and LCoS spat... | lab | Nicola Calabretta (Eindhoven University of Technology) 2 papers; Xu... | Coherent | yes | [not reported] | Lengthy WSS configuration times and scheduling complexity when opti... |
| piezo | millisecond scale | below 2.2 dB | 3 to 50 ports | [not reported] | -25 dB | 1550 nm | free_space_bulk | Multicore fibers integrated directly at the switch ports; losses fr... | lab | Georgios Zervas (University of Bristol) 3 papers; Nick Parsons (Pol... | Polatis; Drut Technologies | yes | [not reported] | Port count set by port separation and maximum steering angle; more... |
| thermo_optic | 1 to under 100 us | below 1 to 15.8 dB | 32 x 32 ports on one chip; 1,856 x 1,856 as a system | around 2 dB | -20 to -50 dB | C band to C+L band, up to 110 nm wide; one device at 775 nm | integrated_photonic | Flip-chip bond to a ceramic interposer with a land grid array; wire... | lab | Keijiro Suzuki (National Institute of Advanced Industrial Science a... | [no source] | yes | [not reported] | Crossing loss grows with port count; control units and drive wiring... |
| electro_optic | 3 to 4 ns | about 1 to 18.5 dB | 32 x 32 ports | [not reported] | -9 to -40 dB | bandwidth 7 to 110 nm; O band in one device | integrated_photonic | CMOS logic and drivers integrated on the switch chip; bandwidth hol... | lab | Benjamin G. Lee (IBM (United States)) 4 papers; William M. J. Green... | [no source] | partial | [not reported] | Crosstalk limits fabric size; every switch unit needs calibration a... |
| soa | 115 to 900 ps | on-state gain above 14.3 dB, lossless | 4 x 4 to 128 x 128 ports | [not reported] | extinction ratio 33 to more than 70 dB | [not reported] | integrated_photonic | Quantum-dot SOAs can run uncooled; chip-on-carrier SOA mounting; ch... | lab | A. Wonfor (University of Cambridge) 4 papers; Ian H. White (Univers... | [no source] | yes | [not reported] | Signal degradation and power grow with fabric size; scaling to seve... |
| robotic_patch_panel | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | mechanical_fiber | Robot handles and mates angled physical contact (APC) connector plugs | production | Mitsuhiro Makihara (NTT (Japan)) 1 paper; Masato MIZUKAMI (NTT (Jap... | Telescent | no | [not reported] | [not reported] |

Of the 126 cells, 84 are reported, 29 are not reported in any abstract, 9 are derived, and 4 have no source (Q9), against 81, 32, 9, and 4 in run 1 after the rework (STATUS.md, 14:36 line).

## Audit results

### Run 2 audit

The run 2 audit used seed 20260928 and never calls export.arxiv.org. It recomputes academic_groups and companies itself, not with the build's functions, and 18 of 18 cells matched (deliverables/validation_report.md, Run 2 audit). Rates for every round follow (same file).

| check | Gate C limit | round 1 | round 2 (padded) | round 3 (after the fix) | run 2 audit, first try | run 2 audit, second round |
|---|---|---|---|---|---|---|
| (a) re-fetch 20 core papers, mismatch rate | at most 10 percent | 0 percent, 16 compared, 4 dropped, PASS | 0 percent, same 16 compared, same 4 dropped, PASS | 0 percent, 20 compared, 0 dropped, PASS | 0 percent, 20 compared, 0 dropped, PASS | 0 percent, same 20, PASS |
| (b) 20 reported matrix cells, unsupported rate | at most 10 percent | 25 percent (5 of 20), FAIL | 0 percent (0 of 20), PASS, not trustworthy | 5 percent (1 of 20), PASS | 15 percent (3 of 20), FAIL | 0 percent (0 of 20), PASS |
| (c) 10 project rows, fail rate | at most 20 percent | 0 percent, PASS | 0 percent, PASS | 0 percent, PASS | 0 percent, PASS | 0 percent, PASS |
| (d) all evidence spans, pass rate | at least 90 percent | 100 percent of 376, PASS | 100 percent of 376, PASS | 100 percent of 376, PASS | 100 percent of 420, PASS | 100 percent of 420, PASS |
| category census, unsupported cells | no gate | not run | not run | 3 of 27 | 4 of 27 | 2 of 27 |

Check (b) failed at first, so Gate C sent the run back to stage 6 once. For two of the three failures, "the specific sentence pipeline/matrix_build.py's extract() function picked out as this clause's quote is a different, nearby sentence that does not itself say it" (Run 2 audit). Stage 6 re-anchored 4 quotes and the second round passed (same file). CMOS is complementary metal-oxide-semiconductor.

| cell | where it failed | auditor's words (deliverables/validation_report.md, Run 2 audit) | second round |
|---|---|---|---|
| thermo_optic:packaging_notes | Gate C sample | The word feedback never appears in the cited quote. | passes |
| electro_optic:integration | Gate C sample and census | integrated_photonic here rests on domain knowledge that a CMOS-fabricated Mach-Zehnder silicon switch is a waveguide device, not on words the quote itself states | passes |
| mems_silicon_photonic:packaging_notes | Gate C sample | a different sentence in the same abstract that never mentions the interposer at all | passes |
| thermo_optic:integration | census | never uses waveguide, chip, integrated, or photonic. | passes |
| mems_2d:integration | census, both rounds | free_space_bulk still rests on domain knowledge the quote does not state. | still fails |
| soa:ai_cluster_fit | census, both rounds | this cell is still at most "partial", not "yes". | still fails |
| thermo_optic:wavelength_range | number check, not in the sample | the matrix should not claim "C band" on its own for this route without a quote that says so. | still fails |

Judging blind, the second judge called all 31 judged cells supported in both rounds, so it agreed with the auditor on 17 of 20 sample and 23 of 27 census cells at first, then 20 of 20 and 25 of 27 (data/work/audit_r2data_second_judge*.json; STATUS.md, 17:37 and 17:56 lines). It also found that two re-anchored cells changed value and two cite different papers, although the report says none did (STATUS.md, 17:56 line).

Check (a) needed no arxiv.org fallback, which "says more about which 20 papers this seed happened to draw" (Run 2 audit).

### Run 1 audits

Round 1 failed check (b), and the auditor called this "a real property of how those cells were filled, not noise in the check" (validation_report.md, round 1).

| cell | cites | value | auditor's words (deliverables/validation_report.md, round 1) |
|---|---|---|---|
| soa:ai_cluster_fit | W2056973550, W3093967660 | partial | The quote describes the switch fabric's use case in general terms and never uses a word close to partial, yes, or no. |
| electro_optic:integration | W2094700182, W1979338531 | integrated_photonic | The quote describes a Mach-Zehnder switch in silicon but does not use the words integrated or photonic. |
| mems_3d:integration | W3215039088, W2560361359 | free_space_bulk | The quote describes a microlens and MEMS mirror array, which is free-space bulk optics by the framework's own definition, but the quote does not use the words free, space, or bulk. |
| mems_silicon_photonic:trl_band | W3138799074, project row 8 | lab | The quote describes CMOS foundry fabrication and does not use the word lab or a synonym. |
| piezo:trl_band | project row 5, no paper_id | production (vendor) | The quote describes the switching mechanism only and does not use the word production. |

The first fix was a bad one. matrix_build.py imported the audit's value test, and 18 of 27 category cells got quote words "specifically so that shared-word test would pass" (validation_report.md, round 3). Gate C passed this round 2, and only the second judge caught it, calling the test "circular" (STATUS.md, 07:42 line). The rework rebuilt the matrix and rewrote audit.py for round 3, which checks each kind of cell its own way (STATUS.md, 14:11 to 15:10 lines).

| cells | how checked | result | source |
|---|---|---|---|
| 33 measured cells | code, every number must stand in a quote | 33 pass | validation_report.md, round 3 |
| 18 academic_groups and companies cells | recomputed with the build's own functions, which "shows reproducibility only" | 18 of 18 match | validation_report.md, round 3; STATUS.md, 15:10 line |
| same 18, second judge | recomputed independently | 42 of 42 names, 9 of 9 routes | STATUS.md, 15:10 line |
| 29 category and text cells, auditor | read against the label definitions | 1 of 20 Gate C sample cells fail, 3 of 27 census cells fail (11.1 percent, no gate) | validation_report.md, round 3 |
| same 29, second judge | read blind to the auditor's verdicts | 29 of 29 supported, agreement 19 of 20 (sample) and 24 of 27 (census) | data/work/audit_run2_checker_judgments.json; STATUS.md, 15:10 line |

| cell | value | auditor's words (deliverables/validation_report.md, round 3) |
|---|---|---|
| mems_2d:packaging_notes (Gate C sample) | packaged single-chip component with reliable actuation | never says single-chip. That detail is not stated in this cell's quote. |
| mems_3d:integration (census) | free_space_bulk | free_space_bulk here rests on domain knowledge that a beam-steering MEMS crossconnect is a free-space device, not on words the quote itself states. |
| mems_2d:integration (census) | free_space_bulk | does not state free space, air, or bulk optics either. |
| piezo:trl_band (census) | production | This is the same cell and the same gap run 1 round 1 [now round 1] found. |

The auditor called the kept piezo value "a known, deliberate choice, not a new defect" (validation_report.md, round 3), and run 2 sets it to lab (deliverables/comparison_matrix.csv). The second judge traced its disagreements to "quote-only reading (auditor) versus reading the cited abstract and the route definition (checker)" (deliverables/pitfalls_original_log.md, 15:10).

## Queries used above

Run from the repo root on the run 2 database.

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
| Q13 | `.venv/bin/python -c "import sqlite3; print(sqlite3.connect('data/db/papers.sqlite').execute('select count(*), sum(t.tech_route_secondary is not null) from tags t join papers p using(paper_id) where p.core_set=1 and t.tech_route=?', ('architecture_only',)).fetchone())"` |
| Q14 | `.venv/bin/python -c "import sqlite3; print(sqlite3.connect('data/db/papers.sqlite').execute('select t.tech_route, count(*), sum(p.year<2012) from tags t join papers p using(paper_id) where p.core_set=1 and t.tech_route in (?,?) group by 1', ('mems_3d','mems_silicon_photonic')).fetchall())"` |
| Q15 | `.venv/bin/python -c "import sqlite3; r=sqlite3.connect('data/db/papers.sqlite').execute('select sources, openalex_id is null, core_set from papers').fetchall(); s=[(set(a.split(',')),b,c) for a,b,c in r]; A={'arxiv','arxiv_via_openalex'}; print(sum(x<=A for x,_,_ in s), sum(c for x,_,c in s if x<=A), sum(b for _,b,_ in s), sum(b and c for _,b,c in s), sum('arxiv' in x and x<=A for x,_,_ in s))"` prints every-source-arXiv papers, of them core, no OpenAlex ID, of them core, and papers holding a run 1 arxiv record and no other OpenAlex pull |
| Q16 | `.venv/bin/python -c "import sqlite3; db=sqlite3.connect('data/db/papers.sqlite'); h=\"(arxiv_id is not null or lower(doi) like '10.48550/arxiv.%' or lower(url) like '%arxiv.org%')\"; print([db.execute(f'select count(*), sum(openalex_id is not null), sum(openalex_id is null) from papers where {w} {h}').fetchone() for w in ('', 'core_set=1 and')])"`, the arXiv-hosted test from data/work/run2_arxiv_coverage.md, which gave 133, 93, 40 and 43, 7, 36 on the run 1 database |
| Q17 | `.venv/bin/python -c "import sqlite3; print(sqlite3.connect('data/db/papers.sqlite').execute(\"select count(*) from papers where title like '%Jupiter Evolving%' or title like '%RotorNet%'\").fetchone())"` |
