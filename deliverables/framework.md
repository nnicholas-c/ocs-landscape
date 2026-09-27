# Analysis and comparison framework

Numbers are run 2's (the arXiv rebuild) unless marked run 1.

## Tagging rubric

The tagger labels each paper from its title and abstract only (ocs-domain skill). Every tag carries one evidence sentence copied exactly from the abstract (or title), and the import rejects any not verbatim. All 420 passed (STATUS.md, 16:43 line).

Relevance is 3 (builds, tests, or deploys an optical circuit switch, OCS, or designs a network around one), 2 (an enabling component), 1 (an adjacent field), or 0 (unrelated).

Tech route is the main mechanism. MEMS is micro-electro-mechanical systems.
- mems_3d. Tilting micromirror arrays steer beams through free space.
- mems_2d. Flip-up mirrors at the crossings of a flat grid.
- mems_silicon_photonic. Actuators on a silicon chip move waveguide couplers.
- lcos. Liquid crystal on silicon (LCoS) phase arrays steer light.
- piezo. Piezoelectric actuators steer collimators or fibers.
- thermo_optic. Heat changes a waveguide's refractive index.
- electro_optic. Voltage changes the index.
- soa. Semiconductor optical amplifiers (SOA) act as on and off gates.
- robotic_patch_panel. A robot reconnects fibers.
- architecture_only. A network design that uses an OCS but builds none.
- other, or unclear when the abstract does not say.

Integration is free_space_bulk, integrated_photonic, mechanical_fiber, or unclear. TRL (technology readiness level) band is lab (prototype or simulation), pilot (field trial), production (in service or sold), or unclear. AI (artificial intelligence) data center fit is direct (accelerator clusters), indirect (data center networks), none, or unclear.

## Comparison matrix

Rows are the nine device routes, with a note for the other three (comparison-framework skill). The 14 dimensions are switching_time, insertion_loss, port_count, polarization_dependent_loss, crosstalk, wavelength_range, integration, packaging_notes, trl_band, academic_groups (up to five lead authors), companies (projects.csv rows), ai_cluster_fit (yes, partial, no), cost_per_port, and scaling_limit.

The matrix is one CSV (comma-separated values) row per route and dimension, 126 rows, rendered to Markdown by a script (deliverables/comparison_matrix.csv). reported means a quoted source states the value, with its paper or project row. derived means a script computed it, as in all 9 academic_groups cells. not_reported_in_abstract means papers exist but say nothing. no_source marks 4 companies cells with no project row (STATUS.md, 17:11 line).

Differing numbers become a range citing both papers, and no number moves between routes. Vendor figures carry their project row and "vendor claim". Confidence is high when two or more papers agree, medium for one, low when ambiguous.

Category cells hold only the fixed label, with reasoning in the note. Run 1's first matrix padded 18 of 27 with quote words to pass the audit's test, and both rebuilds use plain labels (STATUS.md, 14:36 and 17:11 lines). ai_cluster_fit is yes for 6 of 9 routes under the skill's definition (clusters, reconfigurable topologies, or spine replacement), though only the thermo_optic and mems_silicon_photonic notes cite an abstract naming AI, ML (machine learning), or graphics processors (deliverables/comparison_matrix.csv).

## Adjacent-field logic

To find people who could work on OCS, the extended set adds score 1 papers from six transferable fields (ocs-domain skill), namely telecom cross-connects, micromirrors for LiDAR (laser ranging) and projection, silicon photonics, LCoS displays, free-space packaging, and data center network systems.

The tagger judges the device, not keywords, so LCoS for cinema projectors counts and phone displays do not. Of 136 extended papers outside the core, 70 are silicon_photonics, 14 mems_micromirror, 9 telecom_oxc_roadm, 7 lcos_display_phase, 3 dc_network_systems, and 33 lost their field in tagging (query Q12 in deliverables/demo_results.md).

## What the framework cannot do from abstracts alone

- Fill cost and optical-quality cells. 29 of 126 cells are not reported, and cost per port is known for 1 route of 9 (deliverables/comparison_matrix.csv).
- Settle judgment cells. In run 1's round 3 the auditor, reading quotes only, found 4 of 29 judged cells unsupported, and the second judge, reading abstracts too, none (deliverables/pitfalls_original_log.md, 15:10). The run 2 audit's second round gave 2 of 31 and 0 (STATUS.md, 17:56 line).
- Link architecture papers to devices. Only 5 of 105 architecture_only core papers carry a secondary route, none among the 17 naming accelerators or ML (query Q13 in deliverables/demo_results.md; deliverables/comparison_matrix.md).
- Cover thin routes. piezo has 2 core papers, neither saying piezo, and robotic_patch_panel 1 (query Q4 in deliverables/demo_results.md; deliverables/pitfalls.md, stage 6).
- Rank routes. Route counts follow the search phrases, not the field (deliverables/number_checks.md, section 1).

deliverables/reading_list.md lists 10 papers to read in full.
