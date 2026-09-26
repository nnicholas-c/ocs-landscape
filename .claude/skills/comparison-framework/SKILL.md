---
name: comparison-framework
description: The comparison matrix for OCS switching technologies. Defines the rows (tech routes), the columns (performance, integration, maturity, who is behind it, AI cluster fit, cost), the long-format CSV every cell must be stored in, and the provenance rules for filling a cell. Load this whenever you fill, render, audit, or describe the technology comparison, or write the framework deliverable.
---

# Comparison framework

## Shape

Rows are the tech routes from the ocs-domain skill, excluding `architecture_only`, `other`, and `unclear` (those get a short note under the table instead). Columns are the dimensions below. The matrix is stored in long format so every cell can carry its own evidence, and the markdown table is rendered from the CSV by a script, never written by hand.

## Dimensions (one row per tech route per dimension)

Performance, from paper abstracts.
- `switching_time`. Time to establish a new connection. Unit as stated (ns, us, ms, s, min).
- `insertion_loss`. dB, typical or maximum as stated.
- `port_count`. Largest demonstrated N x N, or ports as stated.
- `polarization_dependent_loss`. dB.
- `crosstalk`. dB.
- `wavelength_range`. nm or band names (C band, O band).

Integration and packaging.
- `integration`. free_space_bulk, integrated_photonic, or mechanical_fiber, with a note on packaging if abstracts mention it.
- `packaging_notes`. Fiber attach, hermetic sealing, thermal control, whatever is stated.

Maturity.
- `trl_band`. The highest band supported by evidence (lab, pilot, production), with the paper or project row that shows it.

Who.
- `academic_groups`. Institutions and lead authors from graphs/top_pis.csv whose core papers carry this route. List up to five, each with a paper count.
- `companies`. From data/projects.csv, entities whose tech_route matches. List with the project row number.

Fit and cost.
- `ai_cluster_fit`. Does the literature use or propose this route for accelerator clusters, reconfigurable topologies, or replacing a spine layer? Values are yes, partial, no, or not_reported, with the paper IDs.
- `cost_per_port`. Only if a source states it. Almost always not_reported.
- `scaling_limit`. What stops the port count growing, as stated in sources (mirror count, loss accumulation, control complexity, mechanical time).

## CSV columns (deliverables/comparison_matrix.csv)

```
tech_route, dimension, value, unit, value_min, value_max, status, paper_ids, project_rows, evidence_quote, confidence, note
```

- `status` is one of `reported` (a source states it), `derived` (computed by a script from reported values, say how in note), `not_reported_in_abstract` (papers exist for the route but their abstracts do not say), `no_source` (no paper in the core set for this route at all).
- `paper_ids` is semicolon-separated paper_id values from the database. `project_rows` is semicolon-separated row numbers from projects.csv.
- `evidence_quote` is the sentence, copied exactly, that states the value. Under 40 words. One quote per cell is enough. It must be a verbatim substring of that paper's abstract or of the project row's evidence_quote.
- `value_min` and `value_max` hold the range when several papers report different numbers. `value` then holds the range as text, like "20 to 40".
- `confidence` is high when two or more papers agree, medium for one paper, low when the abstract is ambiguous.

## Rules for filling a cell

1. Read the route's papers from data/work/route_<name>.json. Fill only from those abstracts and from projects.csv. Nothing from memory. If you remember a figure that the abstracts do not state, the cell is not_reported_in_abstract, and you may add "a human should check the full text of <paper_id>" in note.
2. Two papers, two different numbers, both go in as a range with both IDs.
3. A number stated for a different route does not transfer. A 3D MEMS loss figure says nothing about piezo.
4. Product marketing numbers from the scout go in only with the project row and a note "vendor claim".
5. Every route gets every dimension, even when the answer is no_source. A visibly empty column tells the meeting what the abstracts cannot answer.

## Reading list (deliverables/reading_list.md)

Pick ten papers whose full text would fill the most not_reported cells, or would settle the most disagreements. One line each with paper_id, title, year, and the cells it would fill. Prefer surveys and hyperscaler system papers because one full read fills many cells.

## Rendering

pipeline/matrix_render.py reads the CSV and writes deliverables/comparison_matrix.md with one table (routes as rows, dimensions as columns, each cell showing value plus status in brackets when not reported), then a section per route listing the cells with their paper_ids and evidence quotes, then a footer with counts of cells by status. Plain ASCII, no em dashes.
