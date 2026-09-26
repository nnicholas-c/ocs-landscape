# Analysis and comparison framework

## Tagging rubric

The tagger labels each paper from its title and abstract only (ocs-domain skill). Every tag carries one evidence sentence copied exactly from the abstract (or the title if there is none), and the import rejects any sentence that is not verbatim. This run loaded 376 tags with 0 failures (STATUS.md, stage 3 line).

Relevance runs from 3 (builds, tests, or deploys an optical circuit switch, OCS, or designs a network around one) through 2 (an enabling component such as a telecom cross-connect) and 1 (an adjacent field with transferable skills) to 0 (unrelated).

Tech route is the main mechanism the paper demonstrates. MEMS is micro-electro-mechanical systems.
- mems_3d. Facing arrays of tilting micromirrors steer beams through free space.
- mems_2d. Flip-up mirrors at the crossings of a flat grid.
- mems_silicon_photonic. Actuators on a silicon chip move waveguide couplers.
- lcos. Liquid crystal on silicon (LCoS) phase arrays steer light.
- piezo. Piezoelectric actuators steer collimators or fibers.
- thermo_optic. Heat changes a waveguide's refractive index.
- electro_optic. Voltage changes the index, faster than heat.
- soa. Semiconductor optical amplifiers (SOA) act as on and off gates.
- robotic_patch_panel. A robot reconnects fibers.
- architecture_only. A network design that uses an OCS but builds none.
- other, or unclear when the abstract does not say.

Integration is free_space_bulk, integrated_photonic, mechanical_fiber, or unclear. TRL (technology readiness level) band is lab (prototype or simulation), pilot (field trial), production (in service or sold), or unclear. AI (artificial intelligence) data center fit is direct (accelerator clusters, training), indirect (data center networks generally), none, or unclear.

## Comparison matrix

Rows are the nine device routes, with a note for the other three (comparison-framework skill). The 14 dimensions are switching_time, insertion_loss, port_count, polarization_dependent_loss, crosstalk, wavelength_range, integration, packaging_notes, trl_band, academic_groups (up to five lead authors), companies (projects.csv rows), ai_cluster_fit (yes, partial, no), cost_per_port, and scaling_limit.

The matrix is one CSV (comma-separated values) row per route and dimension, 126 rows (deliverables/comparison_matrix.csv), and a script renders the Markdown. reported means a source sentence states the value, stored verbatim with its paper or project row. derived means a script computed it, true of all 9 academic_groups cells (same file). not_reported_in_abstract means papers exist but say nothing. no_source means no core paper, and this run also used it for 4 companies cells with no project row (STATUS.md, stage 6 line).

Differing numbers from two papers become a range citing both, and no number moves between routes. Vendor figures need their project row and the note "vendor claim". Confidence is high when two or more papers agree, medium for one, and low when ambiguous.

After audit round 1, categorical values carry their quote's words in parentheses, such as "partial (datacenter applications)". 18 of 27 reported categorical cells now look like this, outside the skill's fixed vocabulary (STATUS.md, stage 7 DONE line).

## Adjacent-field logic

To find people who could work on OCS, the extended set adds score 1 papers from six fields with transferable skills (ocs-domain skill). These are telecom cross-connects (same devices), micromirrors for LiDAR (laser ranging) and projection (same actuators), silicon photonics, LCoS displays, free-space packaging, and data center network systems.

The tagger judges the device, not keywords, so LCoS for cinema projectors counts and phone displays do not. Of 109 extended papers outside the core, 55 are silicon_photonics, 14 mems_micromirror, 7 lcos_display_phase, 5 telecom_oxc_roadm, 2 dc_network_systems, and 26 lost their field in tagging (query Q12 in deliverables/demo_results.md).

## What the framework cannot do from abstracts alone

- Fill cost and optical-quality cells. 31 of 126 cells are not reported. Cost per port is reported for 1 route of 9, polarization dependent loss for 2, and crosstalk for 4 (deliverables/comparison_matrix.csv).
- Settle judgment cells. Audit round 1 failed 5 maturity, integration, and fit cells that no single sentence stated (deliverables/validation_report.md).
- Link architecture papers to devices. Only 5 of 101 architecture_only core papers name a secondary route (tags table).
- Cover thin routes. piezo has 2 core papers and robotic_patch_panel 1 (query Q4 in deliverables/demo_results.md), and neither piezo abstract says piezo (deliverables/pitfalls.md, 07:06).

deliverables/reading_list.md names the 10 papers whose full text would fill the most gaps.
