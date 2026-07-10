# Dedicated proof-correctness sweep — approved design (execute in a fresh session)

## Context
Follow-up to the merged independent audit (PR #4 / `579a81c`), which excluded
proof re-derivation by design yet caught two proof-level defects incidentally.
The unit of verification is an ARGUMENT, not a claim, so the pipeline adds two
mechanisms the claim-sweeps lacked: machine-checked falsification and blind
re-derivation. Designed via 8 user decisions over 2 rounds; **execution is
deferred to a fresh session** (quota headroom) — this session only parks the
plan in-repo per the Large Task Protocol.

**Corpus (measured 2026-07-03, PRE sequence-models arc):** 52 theorem/proposition
statements, 51 written proofs (1 ch05 statement lacks an adjacent proof block —
automatic first candidate), 30 Prove-exercise solutions, 39 other solutions, 68
definitions, in `src/content/transformers/*.mdx`.

> **Superseded by the sequence-models arc expansion (2026-07-10).** The guide is
> now 19 chapters, not 14: the arc added chapters 02/03/08/13/14 (recurrent
> networks, state space models, encoder–decoder families, selective state spaces,
> hybrid architectures) and renumbered the rest (labels.json grew 176 → 244). This
> plan's corpus counts and per-chapter batching (14 batches → 19) must be
> **re-measured at execution**. The arc's own per-chapter integration already ran
> adversarial math + style verification and full numeric compute-verification, but
> that is a lighter pass than this plan's falsify → blind-derive → compare → verify
> pipeline, which still applies to all 19 chapters. Theorem/LO/exercise ids were
> renamed under `MAP = {2:4,3:5,4:6,5:7,6:9,7:10,8:11,9:12,10:15,11:16,12:17,13:18}`
> (tf0/tf1 self-map); any id this plan names is post-rename.

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

## Dossier ↔ chapter backing map (evidence base for the proof sweep, added 2026-07-09)

Strict-live anchored dossiers in `~/Claude/research-dossiers/` (+ `post_transformers`, `ssm-foundations`)
are the citation-grounded evidence base the sweep should draw on when checking primary-source claims. Map:

- **ch01 pos-enc (RoPE/ALiBi/sinusoidal), ch04 attention, ch05 MHA, ch06 LayerNorm/RMSNorm/block** →
  `research_transformer_architecture`.
- **ch04/07 sparse & efficient attention** → `research_{sparse_attention_patterns,trainable_sparse_attention,kv_cache_sparsity}` (built 2026-07-09).
- **ch03 SSM (S4/HiPPO), ch13 SSD/duality/RetNet, ch14 RWKV/xLSTM/DeltaNet/hybrids** →
  `post_transformers/references/dossier/` + `ssm-foundations` ch09–14 (already anchored — cross-link, do not re-derive).
- **ch09 scaling/objectives/tokenization** → `research_llm_pretraining_scaling`. **ch11 PEFT/LoRA** → `research_peft`.
- **ch12 MoE, ch17 routing** → `research_mixture_of_experts` (building 2026-07-09).
- **ch07 enc/dec taxonomy + cross-attn, ch08 masks/MLM/prefix-LM/UniLM** → `research_encoder_decoder_seq2seq` (building 2026-07-09).
- **ch02 RNN/LSTM/GRU/BPTT/seq2seq/Bahdanau** → `research_recurrent_seq2seq` (building 2026-07-09).

Runbooks: `~/Claude/research-dossiers/docs/plans/active/2026-07-09-{mixture-of-experts,encoder-decoder-seq2seq,recurrent-seq2seq}-dossier.md`.
When the sweep reaches ch02/07/08/12/17, pull anchored excerpts + evidence IDs from these rather than re-deriving citations.
