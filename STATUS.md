# Run status

The orchestrator ticks a box when a stage's "done when" condition in PLAN.md is met, and appends one log line per stage event. A resumed run starts at the first unticked stage.

## Stages

- [ ] Stage 0. Smoke test
- [ ] Stage 1. Collection (1a full pull, 1b relevance scoring, 1c snowball) and Gate A
- [ ] Stage 2. Curation
- [ ] Stage 3. Tagging and Gate B
- [ ] Stage 4. Graphs
- [ ] Stage 5. Scout
- [ ] Stage 6. Comparison matrix
- [ ] Stage 7. Audit and Gate C
- [ ] Stage 8. Write-up

## Log

Format. `- [YYYY-MM-DD HH:MM] stage N <name> DONE|FAILED|RETRY. <counts>. <problems, or "none">`

