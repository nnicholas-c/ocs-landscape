# Small-sample demo results

Every number points to a file or to a query Q1 to Q14, listed at the end. Table text is folded to plain ASCII. MEMS is micro-electro-mechanical systems.

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

Records per query (Q1), counted for the first query that found each record, since collectors skip records already on disk (deliverables/pitfalls.md, stage 8). The cap is 50 per query (pipeline/queries.yaml).

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

arXiv's other 9 phrases got HTTP (web protocol) errors 429 and 406, so their zeros say nothing about arXiv's content (STATUS.md, stage 1a line). Anchors found were 10 of 13, one a false match (STATUS.md, Gate A line).

OpenAlex use was 0.033 USD (US dollars) after stage 1a, and the snowball cost was not saved (STATUS.md; deliverables/pitfalls.md, stage 8).

Relevance scoring and dedup follow (DOI is digital object identifier). Because more than 200 records scored 2 or 3, Gate A kept score 3 only as the core set (PLAN.md).

| step | count | source |
|---|---|---|
| relevance score 0, 1, 2, 3 (of 904) | 433, 116, 72, 283 | Q2 |
| score 2 or 3 | 355 | STATUS.md, Gate A line |
| duplicates removed by DOI, arXiv ID, fuzzy title | 3, 4, 12 | deliverables/curation_report.md |
| wrong fuzzy merges undone after the checker's retry | 3 | STATUS.md, stage 2 RETRY line |
| papers after dedup | 885 | deliverables/curation_report.md |

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

architecture_only is the largest group, 101 of 267 (Q4). These papers use an optical circuit switch (OCS) in a network design rather than build one. Among devices, silicon photonic MEMS leads with 43, three routes have 2 or fewer, and 221 core papers are lab work (Q4, Q5).

The 43 reflects how the sample was built, not the field. One phrase, "silicon photonic MEMS switch", supplied 27 of the 43, while the only 3D MEMS phrase is credited with 0 core papers and 16 of its 46 records have "print" in the title (deliverables/number_checks.md, section 1). Without the snowball the route still has 37 against 11 for mems_3d (same section). Phrase queries also start in 2012, and 4 of 15 mems_3d core papers are older, against 3 of 43 (STATUS.md, 14:24 line; Q14). "Paper counts measure research output in this sample, not shipping products" (deliverables/number_checks.md, section 1).

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

The core groups are UC (University of California) Berkeley on silicon photonic MEMS (Ming C. Wu, 24 core papers), AIST (National Institute of Advanced Industrial Science and Technology) on thermo-optic switches (Keijiro Suzuki, 12), Eindhoven on optical amplifier switches and architecture (Nicola Calabretta, 11), and UC San Diego with Google on architecture and 3D MEMS (George C. Papen 10, Amin M. Vahdat 9), all from graphs/top_pis.csv.

The adjacent side is large. 553 of 1597 authors have no core paper (Q8). Communities 7 and 10 have no core route, and 33 of 39 and 31 of 31 of their members carry the silicon_photonics field (graphs/clusters.csv joined to graphs/top_pis.csv). This "transferable teams" pool has the weakest data, because 26 of 109 extended-only papers lost their adjacent field (STATUS.md, stage 4 DONE line) and 301 authors have no affiliation (Q8).

Split people affect the whole map. Of 149 flagged name keys (last name plus first initial), a random 15 got the same label from two classifiers, and 10 are one person split into several records, which scales to about 99 keys (62 to 126), so the number check calls it "mostly a real bug" (deliverables/number_checks.md, section 2). Keren Bergman has two records, with 10 and 1 core papers (graphs/top_pis.csv). Person rankings need a hand check. Groups are safer, but 14 of 16 split pairs fall in different communities (STATUS.md, 14:24 line).

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

Several evidence dates are fetch dates (data/projects.csv, note column). Polatis "shipping" rests on shop links, not a quoted sentence (deliverables/comparison_matrix.csv, piezo trl_band note).

## Comparison matrix

The full matrix with paper IDs and quotes is deliverables/comparison_matrix.md, written by pipeline/matrix_render.py from the rebuilt CSV. Its top-level table follows, with cells cut at 70 characters by the script (TABLE_CELL_MAX).

| tech_route | switching_time | insertion_loss | port_count | polarization_dependent_loss | crosstalk | wavelength_range | integration | packaging_notes | trl_band | academic_groups | companies | ai_cluster_fit | cost_per_port | scaling_limit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| mems_3d | 20 us to a few ms | 1.2 to 4.0 dB | more than 1100 ports | [not reported] | [not reported] | 1500 to 1630 nm | free_space_bulk | cubic switch housing, packaging by tolerance expansion, shock absor... | production | Michal Stepanovsky (Czech Technical University in Prague) 3 papers;... | Google; Lumentum; Calient; UTStarcom | yes | 100 USD per port | switching speed falls as port count grows, set by micromirror dynamics |
| mems_2d | [not reported] | [not reported] | 16 x 16 ports | [not reported] | [not reported] | [not reported] | free_space_bulk | packaged single-chip component with reliable actuation | lab | Ming C. Wu (University of California, Berkeley) 2 papers; Steffen G... | [no source] | no | [not reported] | higher speed needs smaller mirrors, which reflect less efficiently |
| mems_silicon_photonic | 0.4 to 200 us | 3.7 to 22.7 dB | 128 x 128 ports | 0.5 to 8.5 dB | -80 to -30 dB | 1250 to 1700 nm | integrated_photonic | flip-chip bonding onto aluminum nitride or through-glass-via glass... | lab | Ming C. Wu (University of California, Berkeley) 19 papers; Tae Joon... | nEye | yes | [not reported] | electrical connection count, which grows with the square of port co... |
| lcos | 11.5 us | approximately 2 dB | 1 x 6 ports | [not reported] | [not reported] | [not reported] | free_space_bulk | multicore fiber collimator, spatial multiplexer and demultiplexer a... | lab | Nicola Calabretta (Eindhoven University of Technology) 2 papers; Xu... | Coherent | yes | [not reported] | [not reported] |
| piezo | millisecond scale | below 2.2 dB | 3 to 50 ports | [not reported] | -25 dB | 1550 nm | free_space_bulk | multicore fibers integrated directly into the switch; losses from m... | production | Georgios Zervas (University of Bristol) 3 papers; Nick Parsons (Pol... | Polatis; Drut Technologies | yes | [not reported] | port separation and maximum steering angle; more fiber cores add in... |
| thermo_optic | 3.52 to 100 us | 0.2 to 15.8 dB | 32 x 32 to 1,856 x 1,856 ports | around 2 dB | -50 to -20 dB | 1525 to 1565 nm, and C+L band | integrated_photonic | flip-chip bonding to a ceramic land grid array interposer; wire bon... | lab | Keijiro Suzuki (National Institute of Advanced Industrial Science a... | [no source] | yes | [not reported] | control units and wiring grow with port count; waveguide crossings... |
| electro_optic | 3 to 4 ns | 1 to 18.5 dB | 32 x 32 ports | [not reported] | -24.8 to -9 dB | O band; bandwidth 45 to 110 nm | integrated_photonic | CMOS logic and drivers integrated on the switch chip; wide bandwidt... | lab | Benjamin G. Lee (IBM (United States)) 4 papers; William M. J. Green... | [no source] | yes | [not reported] | crosstalk and signal degradation that grow with switch size |
| soa | 115 to 900 ps | [not reported] | 4 x 4 to 128 x 128 ports | [not reported] | [not reported] | [not reported] | integrated_photonic | quantum-dot SOAs operated uncooled; SOAs flip-chip or wafer bonded... | lab | A. Wonfor (University of Cambridge) 4 papers; Ian H. White (Univers... | [no source] | yes | [not reported] | signal impairments and degradation that grow with network size |
| robotic_patch_panel | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | [not reported] | mechanical_fiber | handles and connects angled physical contact connector plugs | production | Mitsuhiro Makihara (NTT (Japan)) 1 paper; Masato MIZUKAMI (NTT (Jap... | Telescent | no | [not reported] | [not reported] |

Of the 126 cells, 81 are reported, 32 are not reported in any abstract, 9 are derived, and 4 have no source (Q9), against 82, 31, 9, and 4 in run 1 (STATUS.md, 14:36 line).

## Audit results

A separate checker caught the matrix builder gaming the audit in run 1 round 2, a round Gate C had passed (STATUS.md, 07:42 line). So build and audit were separated, and stages 6 and 7 rerun from scratch with seed 20260927 in place of 20260926 (deliverables/validation_report.md, Run 2). Rates for all three rounds follow (same section).

| check | Gate C limit | run 1 round 1 | run 1 round 2 | run 2 |
|---|---|---|---|---|
| (a) re-fetch 20 core papers, mismatch rate | at most 10 percent | 0 percent, 16 compared, 4 dropped, PASS | 0 percent, same 16 compared, same 4 dropped, PASS | 0 percent, 20 compared, 0 dropped, PASS |
| (b) 20 reported matrix cells, unsupported rate | at most 10 percent | 25 percent (5 of 20), FAIL | 0 percent (0 of 20), PASS, not trustworthy | 5 percent (1 of 20), PASS |
| (c) 10 project rows, fail rate | at most 20 percent | 0 percent, PASS | 0 percent, PASS | 0 percent, PASS |
| (d) all 376 evidence spans, pass rate | at least 90 percent | 100 percent, PASS | 100 percent, PASS | 100 percent, PASS |

Gate C caught round 1's real unsupported cells, because check (b) failed and the auditor called this "a real property of how those cells were filled, not noise in the check" (validation_report.md, Run 1). Its words on each cell follow (CMOS is complementary metal-oxide-semiconductor).

| cell | cites | value | auditor's words (deliverables/validation_report.md, Run 1 round 1) |
|---|---|---|---|
| soa:ai_cluster_fit | W2056973550, W3093967660 | partial | The quote describes the switch fabric's use case in general terms and never uses a word close to partial, yes, or no. |
| electro_optic:integration | W2094700182, W1979338531 | integrated_photonic | The quote describes a Mach-Zehnder switch in silicon but does not use the words integrated or photonic. |
| mems_3d:integration | W3215039088, W2560361359 | free_space_bulk | The quote describes a microlens and MEMS mirror array, which is free-space bulk optics by the framework's own definition, but the quote does not use the words free, space, or bulk. |
| mems_silicon_photonic:trl_band | W3138799074, project row 8 | lab | The quote describes CMOS foundry fabrication and does not use the word lab or a synonym. |
| piezo:trl_band | project row 5, no paper_id | production (vendor) | The quote describes the switching mechanism only and does not use the word production. |

The first fix was a bad one. matrix_build.py imported the audit's value test, and 18 of 27 category cells were rewritten with quote words, such as "partial (computing systems and data networks)", "specifically so that shared-word test would pass" (validation_report.md, Run 2). Only the checker's 07:42 note caught this, calling the test "circular" (STATUS.md, 07:42 line). So the rework deleted the shared test, rebuilt the matrix from scratch, and rewrote audit.py (STATUS.md, 14:11 to 15:10 lines).

Run 2 checks each kind of cell its own way.

| cells | how checked | result | source |
|---|---|---|---|
| 33 measured cells | code, every number must stand in a quote | 33 pass | validation_report.md, Run 2 |
| 18 academic_groups and companies cells | recomputed with the build's own functions, which "shows reproducibility only" | 18 of 18 match | validation_report.md, Run 2; STATUS.md, 15:10 line |
| same 18, checker | recomputed independently | 42 of 42 names, 9 of 9 routes | STATUS.md, 15:10 line |
| 29 category and text cells, auditor | read against the label definitions | 1 of 20 Gate C sample cells fail, 3 of 27 census cells fail (11.1 percent, no gate) | validation_report.md, Run 2 |
| same 29, checker | read blind to the auditor's verdicts | 29 of 29 supported, agreement 19 of 20 (sample) and 24 of 27 (census) | data/work/audit_run2_checker_judgments.json; STATUS.md, 15:10 line |

The auditor's words on the 4 cells it failed follow (validation_report.md, Run 2).

| cell | value | auditor's words (deliverables/validation_report.md, Run 2) |
|---|---|---|
| mems_2d:packaging_notes (Gate C sample) | packaged single-chip component with reliable actuation | never says single-chip. That detail is not stated in this cell's quote. |
| mems_3d:integration (census) | free_space_bulk | free_space_bulk here rests on domain knowledge that a beam-steering MEMS crossconnect is a free-space device, not on words the quote itself states. |
| mems_2d:integration (census) | free_space_bulk | does not state free space, air, or bulk optics either. |
| piezo:trl_band (census) | production | This is the same cell and the same gap run 1 round 1 found. |

The auditor calls the kept piezo value "a known, deliberate choice, not a new defect" (validation_report.md, Run 2). The checker traces the disagreement to "quote-only reading (auditor) versus reading the cited abstract and the route definition (checker)", "Left for a human to settle the standard" (deliverables/pitfalls_original_log.md, 15:10).

Check (a) sample size. Run 1 drew 20, compared 16, and dropped 4 arXiv-only papers on HTTP 406 errors with no fallback, and round 2 dropped the same 4 (deliverables/number_checks.md, section 3). Run 2 drew 20, compared 20, and dropped 0, reading its 4 arXiv-only papers from arxiv.org/abs pages on title and year only (same section). So run 1's gap came from the arXiv service refusing every lookup, not from the sample design (same section).

The checker found the report's preamble "still says SEED = 20260926" (STATUS.md, 15:10 line).

## Queries used above

Run from the repo root. Q11 to Q13 back counts in open_questions.md and framework.md.

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
