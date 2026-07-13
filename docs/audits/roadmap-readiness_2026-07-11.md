# Roadmap readiness review — 2026-07-11

This tracked copy replaces the former repository-external `.consult/` reference. The accepted execution decisions have since been refined in the active Track A, Track B, and proof-audit plans.

## Prioritized findings

### Blocking

1. Track A must never extract the inference MoE material before the destination chapter exists. Author and extract atomically.
2. Review the MoE derivation before authoring, separating resident capacity `E mu`, activated compute `T k Phi`, and batch traffic `A_B mu`, with limiting cases.
3. Repair confirmed proof defects before restructuring so later work does not migrate or cite known-invalid material.
4. Track B needs accepted dossiers, fixed placement, stable theorem scopes, and evidence-ledger ownership before authoring.

### Important

- Run the exhaustive proof audit last, but apply lightweight proof and numeric gates to every changed chapter.
- Establish the property-test harness before structural migrations.
- Keep re-parting and semantic-ID migration separate, with a generated old-to-new map and explicit invariants.
- Gate duplicate IDs, dangling XRefs, legacy chapter-coupled IDs, bibliography completeness, and printed-number drift.
- Prove infrastructure readiness for glossary/back matter, notation overrides, KaTeX, CI triggers, and figures before chapter authoring.
- Build Track B evidence in parallel with Track A.
- Keep deployment isolated from the content tracks and generate current corpus metadata rather than hard-coding counts.

## Accepted execution direction

1. Establish inventory, corpus-manifest, ID, and property-test checks.
2. Fix confirmed defects and the quantitative cost-model spine.
3. Re-part mechanically.
4. Migrate IDs and numbering through a checked manifest.
5. Enrich existing chapters.
6. Author/extract MoE atomically.
7. Author Sparse Attention.
8. Complete apparatus and narrative repairs.
9. In parallel, accept the Track B evidence base and lock its structure.
10. Land BPE, ICL, DPO, and Scaling Laws with local proof/numeric review.
11. Run the full staged proof audit over the frozen corpus.
12. Refresh deployment only from the stable semantic-ID baseline.
