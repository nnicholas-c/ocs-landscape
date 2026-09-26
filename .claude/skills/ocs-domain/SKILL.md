---
name: ocs-domain
description: Domain knowledge for optical circuit switching (OCS) in AI data centers. Load this whenever you classify, score, search for, or write about OCS papers, switching technologies (MEMS, LCoS, piezo, thermo-optic, SOA, patch panels), transferable research teams, or OCS companies. Use it for relevance scoring, tagging, the scout's seed list, and any judgement about what counts as OCS or as an adjacent field.
---

# OCS domain guide

## What OCS means here

An optical circuit switch connects an input fiber to an output fiber and leaves that connection in place until it is told to change it. Light passes through without being converted to electricity, so the switch does not care about bit rate or protocol. In an AI data center this is used to rewire the network between groups of accelerators (GPUs or TPUs) so the topology fits the training job, and to replace part of the electrical spine layer. The switch is slow to reconfigure compared with a packet switch (milliseconds or longer versus nanoseconds) but it is cheap per bit, low power, and future-proof against faster links. Google's Apollo system, built on its Palomar MEMS switch, is the best-known deployment.

Two things are easy to confuse with OCS and must be tagged carefully. Optical packet switching and optical burst switching switch at nanosecond speed per packet, which is a different problem, and a paper about them is relevant only as an adjacent technology. Co-packaged optics and optical transceivers move bits but do not switch, so they are not OCS at all.

## Scope this week

OpenAlex and arXiv only. Core set is 50 to 100 papers. A company that ships a product but never published a paper is the scout's job, not the collector's.

## Switching technology routes (tech_route values)

Use exactly these values. Pick the primary route from what the paper actually demonstrates or studies, not from what it mentions in its introduction.

- `mems_3d`. Arrays of tilting micromirrors steer beams in free space between two facing mirror arrays. Any port to any port. Signal words are "3D MEMS", "two-axis micromirror", "analog micromirror array", "beam-steering crossconnect", "N x N optical crossconnect". This is the route behind most shipping data center OCS products.
- `mems_2d`. Micromirrors flip up or down at crossing points of a planar grid. Simpler control, but the mirror count grows with the square of the port count, so it stops scaling early. Signal words are "2D MEMS", "digital micromirror", "crossbar of pop-up mirrors".
- `mems_silicon_photonic`. Micromechanical actuators built on a silicon photonics chip move waveguide couplers. Integrated rather than free space. Signal words are "silicon photonic MEMS", "MEMS-actuated waveguide", "adiabatic coupler switch", "on-chip MEMS switch".
- `lcos`. Liquid crystal on silicon phase arrays steer light, usually inside wavelength selective switches used in telecom. Signal words are "LCoS", "liquid crystal on silicon", "wavelength selective switch", "WSS", "phase-only spatial light modulator switch".
- `piezo`. Piezoelectric actuators steer collimators or fibers. Signal words are "piezoelectric", "piezo-actuated collimator", "fiber beam steering", "DirectLight" (a product name).
- `thermo_optic`. Heat changes the refractive index in a waveguide interferometer to route light, usually on silicon or silica planar chips. Signal words are "thermo-optic", "TO switch", "Mach-Zehnder switch matrix", "silica PLC switch".
- `electro_optic`. Voltage, not heat, changes the index. Faster than thermo-optic, includes carrier-injection silicon, lithium niobate, and polymer switches. Signal words are "electro-optic switch", "carrier injection", "lithium niobate switch", "nanosecond switching".
- `soa`. Semiconductor optical amplifiers used as on/off gates in a broadcast-and-select fabric. Nanosecond switching, but noise and power scale badly. Signal words are "SOA gate", "broadcast and select", "SOA-based switch".
- `robotic_patch_panel`. A robot physically reconnects fibers. Reconfiguration takes minutes, but loss is near zero and there is no active optics in the path. Signal words are "robotic patch panel", "automated fiber cross-connect", "physical layer automation".
- `architecture_only`. The paper is about a data center or cluster network design that uses OCS as a building block but does not itself build a switch. Tag the switch it assumes in tech_route_secondary if it says.
- `other`. A real switching technology not listed (magneto-optic, acousto-optic, fluidic, DMD-based free space).
- `unclear`. The abstract does not say.

Rough orientation only, never copy into the matrix. Free-space MEMS and piezo switches reconfigure in milliseconds to tens of milliseconds and reach hundreds of ports with low loss. Thermo-optic and electro-optic integrated switches reconfigure in microseconds or faster but have fewer ports and more loss and crosstalk. SOA switches reconfigure in nanoseconds. Robotic patch panels take minutes. The matrix must carry the numbers the papers actually state, with the sentence they come from.

## Integration values

- `free_space_bulk`. Beams travel through air between mirrors or collimators inside a sealed box, with fiber collimator arrays at the ports.
- `integrated_photonic`. Light stays in waveguides on a chip.
- `mechanical_fiber`. Fibers are physically moved or reconnected.
- `unclear`.

## TRL bands (trl_band values)

- `lab`. A prototype, a fabricated device, a simulation, a testbed. Signal words are "we demonstrate", "fabricated", "prototype", "proof of concept", "simulation".
- `pilot`. A field trial, a deployment in one facility, a small production run. Signal words are "field trial", "deployed in", "pilot".
- `production`. In service at scale or sold as a product. Signal words are "in production", "deployed across", "commercially available", "shipping".
- `unclear`.

Most papers are `lab`. Hyperscaler papers about live systems are `production`. Companies rarely publish, so `production` evidence usually comes from the scout, not from papers.

## AI data center fit (ai_dc_fit values)

- `direct`. The paper targets accelerator clusters, ML training, TPU or GPU pods, collective communication, or replacing the spine of a data center network.
- `indirect`. The paper is about data center networks generally, or about a switch whose stated application includes data centers.
- `none`. Telecom, sensing, or other applications only.
- `unclear`.

## Relevance score (stage 1b), 0 to 3

- 3. The paper builds, characterizes, or deploys an optical circuit switch, or designs a data center or cluster network around one.
- 2. The paper is about an enabling component or a close cousin. A wavelength selective switch, an optical cross-connect for telecom, a MEMS mirror array built for switching, a silicon photonic switch fabric, or a network architecture that assumes reconfigurable optical links.
- 1. The paper is in an adjacent field with transferable skills but no switching application (see the list below), or mentions optical switching only in passing. Set adjacent_field for these.
- 0. Unrelated, including other meanings of "OCS".

Score from the title and the abstract snippet only. When the snippet is cut off and you cannot tell between 1 and 2, give 2 and say so in the reason field.

## Adjacent transferable fields (adjacent_field values)

This map is being built to find people who could work on OCS, not only people who already do. So the team map must include groups whose hands-on skills match, even if their papers never say "data center". Tag these fields on score 1 and score 2 papers.

- `telecom_oxc_roadm`. Optical cross-connects, ROADMs, and wavelength selective switches for telecom networks. The most direct transfer. Same devices, same vendors, different scale and reconfiguration pattern.
- `mems_micromirror`. Micromirror arrays and scanners built for LiDAR, projection, beam steering, or adaptive optics. The actuator physics, fabrication, and control loops carry over.
- `silicon_photonics`. Integrated photonic switch fabrics, packaging, fiber attach, and thermal control. Feeds the integrated routes.
- `lcos_display_phase`. LCoS panels and phase-only spatial light modulators from displays, holography, and beam shaping. Feeds the LCoS route.
- `free_space_optics_packaging`. Alignment, collimator arrays, hermetic packaging, and reliability of free-space optical assemblies.
- `dc_network_systems`. Data center topology, scheduling, and control-plane work for reconfigurable networks, including systems papers from SIGCOMM and NSDI.

Do not match on keywords alone. A paper about LCoS for cinema projectors is `lcos_display_phase` because the device is the same. A paper about liquid crystal displays for phones is not.

## Search guidance

"OCS" collides with other meanings, including the outer continental shelf, obsessive compulsive symptoms, open clusters in astronomy, and several government offices. Never search the bare acronym. Search the phrases in pipeline/queries.yaml.

If recall is low (Gate A), add these phrases. "optical switch fabric", "free-space optical switch", "micromirror array switch", "photonic switch matrix", "reconfigurable optical interconnect", "circuit-switched optical network", "optical spine", "TPU interconnect optical", "GPU cluster optical circuit".

Conferences that matter for OCS itself are OFC (optical components and switches), SIGCOMM and NSDI (network systems), ISCA and HotChips (accelerator interconnects), and JLT and Optica as journals. APEC, ECCE, and PCIM are power electronics and packaging venues, so a low count from them is expected and is not a recall problem. Say this in open_questions.md.

## Seed entities for the scout

These are leads, not facts. Verify each one with a primary source (company page, press release, or a paper page) dated in the last three years before writing a row. If you cannot verify, leave the entity out and log it.

- Google (Apollo system, Palomar switch, hyperscaler internal)
- Lumentum (data center OCS products)
- Coherent (data center OCS products)
- Polatis, now part of Huber+Suhner (piezo beam steering switches)
- Calient (3D MEMS switches)
- Telescent (robotic patch panels)
- nEye Systems (silicon photonic MEMS switch startup)
- iPronics (programmable photonic circuits)
- Lightmatter (photonic interconnect, check whether any product is a circuit switch)
- Oriole Networks (optical networking for AI clusters)
- Drut Technologies (photonic fabric with optical circuit switching)
- Microsoft (research systems such as Sirius, check for anything newer)

Then search for entrants you do not know with phrases like "optical circuit switch startup", "OCS for AI clusters", "optical circuit switch product launch", restricted to the last two years.
