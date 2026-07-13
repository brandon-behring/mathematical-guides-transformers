# Dedicated proof-correctness sweep — approved terminal execution design

## Context
Follow-up to the merged independent audit (PR #4 / `579a81c`), which excluded
proof re-derivation by design yet caught two proof-level defects incidentally.
The unit of verification is an ARGUMENT, not a claim, so the pipeline adds two
mechanisms the claim-sweeps lacked: machine-checked falsification and blind
re-derivation. Designed via 8 user decisions over 2 rounds; execution remains
deliberately terminal, after Tracks A and B freeze the corpus.

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
> during that historical expansion (the already-semantic ch00/ch01 anchors mapped to themselves). A3 later replaced
> the chapter-prefixed identifiers with semantic IDs; any ID this plan names is post-migration.

> **Further superseded by the dossier-integration + topic-gap expansion (2026-07-10).** This audit now runs AFTER
> both `docs/plans/implemented/dossier-guide-integration_2026-07-10.md` (Track A: 6-part restructure, +MoE & Sparse chapters, MLA→ch05,
> glossaries) and `topic-gap-expansion_2026-07-10.md` (Track B: +RLHF/DPO, Scaling-laws, ICL, BPE). The corpus grows
> to **~24 chapters / 6 parts** — re-measure at execution. IDs become **semantic / chapter-free** going forward, so
> the `MAP`-style renumber no longer applies to new content. A 3-voice / 3-round review already ran over the current
> 19 chapters (2026-07-10); its **confirmed defects are pre-seeded below** (Stage-A/C work already done for them).

> **Readiness review (Codex 2026-07-11)** (`docs/audits/roadmap-readiness_2026-07-11.md`). Three changes:
> (1) all six confirmed pre-seeded defect groups are pulled forward to Track A A1; this terminal sweep verifies their
> non-regression. (2) This sweep is **not the only proof gate**: each new Track-A/B chapter gets a
> **lightweight per-chapter proof/numeric gate as it lands**; only the exhaustive falsify→derive→compare→verify sweep is
> terminal. (3) The **`tests/properties/` harness is landed by Track A (PR1), not created here** — this audit *extends*
> it, so migration and the new chapters already run under regression protection. The sweep inventories **semantic IDs**
> (post-migration), not chapter-prefixed IDs.

## Pre-seeded findings (from the 2026-07-10 three-round review — confirmed by ≥2 independent voices)

All items below are owned by Track A A1 and become explicit non-regression targets for Stage A/C/D; the audit does not
defer known-invalid material. The list is retained so the terminal report can record independent confirmation:
- **ch12 contrastive minimizer** (`prop-contrastive-alignment`): the "equivalently, on L2-normalized embeddings"
  step is false (fixed-τ margin ≤ 2/τ cannot diverge); split into unconstrained-logit lemma / constrained spherical-code
  optimum / directional tendency, and fix ch23:33's "correct precisely because" over-claim to match ch23:114's caveat.
- **ch07 encoder⟺cross-attention contradiction**: line 129's "an encoder exists exactly
  when cross-attention is present" contradicts the encoder-only row + ViT (55) + LLaVA (133) in-chapter; the real switch
  is whether the encoder feeds cross-attention vs. a concat-projector. (Expository.) **Fix the merged `three-architectures`
  figure caption (#10) in the same change** — it renders the same "unused 4th cell" framing (bidirectional self-attention
  + cross-attention is used in fusion / cross-encoders, so scope the claim to *generating* stacks).
- **ch22 any-to-any tag-factor**: the proof drops $p(c_t\mid u_{<t})$; add $p(u_t\mid u_{<t})=p(c_t\mid u_{<t})\,
  p(x_t\mid u_{<t},c_t)$ (theorem survives).
- **ch22 finite-alphabet wording** (`prop-why-discrete` + Exercise 22.3): "only over a finite alphabet / finite sum
  ⟺ finite alphabet" wrongly excludes countably-infinite categoricals; tighten in both spots (continuous half is already
  hedged "in general" — leave it).
- **ch23 prose numbers**: N-4 (ch23:77 "ch. 6" → ch. 10, `def-ce-loss`), N-5 (ch23:118 "ch. 7 classifier" → ch. 12,
  `def-encoder-classifier`).
- **ch09 definition-before-use**: uses `def-autoregressive-lm` before ch10 defines it; host the bare AR factorization
  in ch09 or add the `training` prereq.

**Reviewed and REFUTED (do NOT seed):** ch18 dual-discretization (the chapter explicitly names + numerically quantifies
each ZOH switch) and ch12 Mahalanobis "singular covariance" (pooled reps live in ambient $\R^d$; the unit sphere is a
*nonlinear* manifold, so the covariance is generically full-rank). Optional: a one-line note that `def-ood-score`
presumes the pre-normalization representation, to forestall the R3-4 confusion.

## The 8 decisions
1. **Scope:** every statement+proof, both solution classes, and every definition's well-definedness in the frozen
   post-Track-B corpus. Generate the exact denominator from the tracked corpus inventory at launch; do not reuse the
   historical 189-unit count.
2. **Pipeline:** full A+B+C+D (falsify → blind-derive → compare → verify).
3. **Roster:** premium-where-it-counts — B and D-tiebreaks Fable 5/max;
   A, C, D-refuters Sonnet 5/high. **(2026-07-10 substitution: Fable is out of
   credits — use Codex 5.6 in its place for Stage-B blind re-derivation and the
   D tiebreak; A/C/D-refuters unchanged.)**
4. **Disposition:** report + fix → PR with CI + 3-voice adversarial review
   (PR #4 pattern), squash-merge.
5. **B blindness:** specs + citable prior statements passed INLINE (no file
   paths); post-run script greps B transcripts for chapter-file reads; any
   peek voids that unit's B signal and is disclosed in the report.
6. **Property tests are durable:** curated Stage-A tests land in
   `tests/properties/` (stdlib-only preferred; no new CI dependencies) with a
   test step in `.github/workflows/content-validate.yml` (+ `tests/**` in its
   trigger paths). **(Amended 2026-07-11 per the readiness review: the harness
   + CI step are established by Track A, PR1 — this sweep *extends* the existing
   suite rather than creating it, so migration and the new chapters already run
   under regression protection.)**
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
  Definitions batched per chapter: existence/uniqueness/side
  conditions (quantizer-tie-break class).
- **B — Blind re-derivation** *(fable/max; every inventoried proof + Prove-solution)*:
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
- 100% of the frozen inventory through its assigned stages (journal-verified;
  failed agents re-run before coverage is claimed).
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
- **ch05 MLA + ch15 approximate KV selection/eviction** → `research_kv_cache_sparsity` (built 2026-07-09).
- **ch03 SSM (S4/HiPPO), ch18 SSD/duality/RetNet, ch19 RWKV/xLSTM/DeltaNet/hybrids** →
  `post_transformers/references/dossier/` + `ssm-foundations` ch09–14 (already anchored — cross-link, do not re-derive).
- **ch14 PEFT/LoRA** → `research_peft`.
- **new ch16 MoE chapter, ch22 routing** → `research_mixture_of_experts` (**MERGED** research-dossiers PR #4, 2026-07-10); the corrected MoE traffic model is a completed Track-A derivation from the roofline, not a cited empirical fact.
- **ch07 enc/dec taxonomy + cross-attn, ch09 masks/MLM/prefix-LM/UniLM** → `research_encoder_decoder_seq2seq` (**MERGED** PR #4).
- **ch02 RNN/LSTM/GRU/BPTT/seq2seq/Bahdanau** → `research_recurrent_seq2seq` (**MERGED** PR #4).
- **new ch17 Sparse chapter** → `research_sparse_attention_patterns` + `research_trainable_sparse_attention` (**MERGED** PR #4).

Track-B evidence owners (see `topic-gap-expansion_2026-07-10.md`):
- **new ch11 RLHF/DPO chapter** → accepted `research_rlhf` + `research_post_training_preference` owners.
- **new ch13 Scaling-laws chapter** → accepted `research_llm_pretraining_scaling` owner and targeted top-up.
- **new ch08 ICL chapter** → accepted `research_incontext_associative_memory` owner; the full constructive trio is
  locked, with empirical induction claims restricted to remarks.
- **ch01 BPE section** → author from primaries (BPE/SentencePiece), no dossier.

The exact accepted corpus SHA, per-owner provenance commits, and evidence IDs are frozen in the Track-B plan's
`B0 acceptance record — cleared 2026-07-13`; use that record rather than inferring support from dossier names alone.

When the sweep reaches a chapter, pull anchored excerpts + evidence IDs from its dossier's `evidence_ledger.yml`
rather than re-deriving citations. The corrected/frontier claims flagged by the 2026-07-10 dossier-coverage audit
(MoE traffic = derive; MLA decoupled-RoPE = top-up; MoE aux-loss = positive excerpt) are noted in
`docs/plans/implemented/dossier-guide-integration_2026-07-10.md`.
