# Dedicated proof-correctness sweep — approved design (execute in a fresh session)

## Context
Follow-up to the merged independent audit (PR #4 / `579a81c`), which excluded
proof re-derivation by design yet caught two proof-level defects incidentally.
The unit of verification is an ARGUMENT, not a claim, so the pipeline adds two
mechanisms the claim-sweeps lacked: machine-checked falsification and blind
re-derivation. Designed via 8 user decisions over 2 rounds; **execution is
deferred to a fresh session** (quota headroom) — this session only parks the
plan in-repo per the Large Task Protocol.

**Corpus (measured 2026-07-03):** 52 theorem/proposition statements, 51
written proofs (1 ch05 statement lacks an adjacent proof block — automatic
first candidate), 30 Prove-exercise solutions, 39 other solutions, 68
definitions, in `src/content/transformers/*.mdx`.

## The 8 decisions
1. **Scope:** all 189 units (statements+proofs, both solution classes,
   definition well-definedness).
2. **Pipeline:** full A+B+C+D (falsify → blind-derive → compare → verify).
3. **Roster:** premium-where-it-counts — B and D-tiebreaks Fable 5/max;
   A, C, D-refuters Sonnet 5/high.
4. **Disposition:** report + fix → PR with CI + 3-voice adversarial review
   (PR #4 pattern), squash-merge.
5. **B blindness:** specs + citable prior statements passed INLINE (no file
   paths); post-run script greps B transcripts for chapter-file reads; any
   peek voids that unit's B signal and is disclosed in the report.
6. **Property tests are durable:** curated Stage-A tests land in
   `tests/properties/` (stdlib-only preferred; no new CI dependencies) with a
   test step added to `.github/workflows/content-validate.yml` (+ `tests/**`
   in its trigger paths) — the repo's first regression suite.
7. **Rigor bar:** fix defects (invalid steps, false statements,
   statement↔proof mismatches) AND rigor gaps (unstated load-bearing
   assumptions — "taken as given" is legal only when stated); improvements
   (redundant hypotheses, strengthenings) are report-only.
8. **Launch:** staged inside the fresh session — Stage A workflow to
   completion first (cheap, objective, ~150 calls, all-Sonnet; its FAILs are
   immediate counterexamples and its specs feed B), then the B+C+D workflow.

## Pipeline detail (for the executing session)
- **A — Formalize & falsify** *(sonnet/high)*: per unit, extract spec
  (hypotheses, quantifiers, conclusion); write AND run a pure-python property
  test (random + adversarial instances: tied maxima, Rademacher, degenerate
  dims). Verdict PASS / FAIL(+concrete instance) / not-instantiable.
  Definitions batched per chapter (14 batches): existence/uniqueness/side
  conditions (quantizer-tie-break class).
- **B — Blind re-derivation** *(fable/max; 52 proofs + 30 Prove-solutions)*:
  input = inline spec + inline statements of the unit's citable XRef targets.
  Output: derivation or "cannot prove without extra hypothesis X".
- **C — Comparison audit** *(sonnet/high)*: guide proof + B output + A
  verdict → candidates in the three classes of decision 7. Non-Prove
  solutions and definition batches get A+C only.
- **D — Verification**: dedup, 2 refuters *(sonnet/high)* with
  quoted-evidence refutation and recomputation, split → tiebreak
  *(fable/max)*. Confirmed → batched `/lever:ask-codex` (high reasoning) +
  `/lever:ask-gemini`; either external REFUTE → downgrade to PLAUSIBLE
  (report-only, not fixed).

## Execution mechanics (lessons carried from the last audit)
- Main-loop inventory script → `scratchpad/proof-units.json`; workflow args
  as `{path, count}` with the defensive `typeof args==='string' ?
  JSON.parse(args) : args` guard (args arrive stringified).
- Agents address units by index and read the inventory file themselves —
  EXCEPT Stage B, whose unit content is inlined (decision 5).
- On quota stall: do NOT re-launch; `Workflow({scriptPath, resumeFromRunId})`
  after reset/model switch — cached agents replay free. Report only
  journal-verified counts, never interim snapshots.
- Report: `docs/audits/proof-audit_<completion-date>.md` — methodology,
  ranked findings (evidence + votes + external verdicts), the improvement
  table, AND the assurance side: per-unit property-test PASSes and
  blind-derivation agreements (positive verification, not just defects).
- Fix phase: sequential main-loop edits (proof fixes touch hypotheses and
  downstream XRefs); exact-match python replacement scripts that fail loudly
  on non-unique matches; branch `fix/proof-audit-findings`; local gate
  `npm run validate` + `npm run build` + 0 katex-errors + new tests PASS.

## Verification (executing session)
- 189/189 units through their assigned stages (journal-verified; failed
  agents re-run before coverage is claimed).
- Every confirmed finding: quoted evidence + 2 uphold votes + external
  verdicts; every A-FAIL carries a concrete instance.
- Post-fix: fixed statements' property tests PASS; validate clean; build
  green; PR CI green (incl. the new test step); adversarial review of the
  diff; squash-merged to main; memory updated.
