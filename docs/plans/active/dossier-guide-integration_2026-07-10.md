# Dossier→guide integration (Track A) — 6-part restructure, review-hardened

**Status:** approved design, **not yet executed**. Parked per the Large Task Protocol. Supersedes
`docs/notes/sparse-attention-chapter-ideas_2026-07-09.md`. Companion: `topic-gap-expansion_2026-07-10.md` (Track B).

## Context

The six merged research dossiers (`~/Claude/research-dossiers/`, research-dossiers PR #4) are the guide's backing
evidence base, but the guide cites none yet. This track (a) **extends** the guide with two new chapters (Mixture-of-
Experts; Sparse & Sub-Quadratic Attention) and (b) **improves** existing chapters with anchored primaries, inside a
**6-part restructure** validated by a 3-voice / 3-round review + a dossier-coverage audit. Design decisions and the
full review record: `~/.claude/plans/how-much-research-is-elegant-popcorn.md`.

**Cite-provenance principle:** the guide cites **primary papers** (`<Cite key=.../>` + `bibliography.bib` /
`src/data/references.json`), never dossier slugs. Per claim, pull the anchored excerpt + arXiv id from the dossier's
`evidence_ledger.yml` / `agent_index/`, add the primary, cite it — satisfying "cite primaries" + "no unanchored
numbers", with the dossier as the verbatim-anchored provenance layer.

## Target structure — 6 parts

Part titles live only as prose in `README.md` (frontmatter carries the numeric `part:`). **IDs become semantic /
chapter-free going forward** (precedent: ch00 `def-softmax`, all `fig-*` — they pass `validate`), so this and future
restructures do not renumber IDs.

- **P1 Foundations:** 00 Notation, 01 Input Representations (+ BPE section — see Track B)
- **P2 Recurrence & Linear State:** 02 Recurrent Networks, 03 Linear Recurrences & SSM
- **P3 Transformer Architectures & Objectives:** 04 Attention, 05 Multi-Head Attention, 06 Block, 07 Composition,
  08 Encoder-Decoder Families, 09 Training, **10 (retitled) Encoder Readouts, Contrastive Alignment, and Detection**
  (moved from old P4; coda). *(Track B inserts ICL and RLHF/DPO chapters into P3 — see the structure-design pass.)*
- **P4 Efficient & Conditional Computation:** 11 Training Optimizations, 12 Inference Optimizations, **NEW
  Mixture-of-Experts**
- **P5 Sub-Quadratic & Selective Sequence Models:** **NEW Sparse & Sub-Quadratic Attention**, Selective State Spaces
  (old ch13), Modern Recurrent & Hybrid (old ch14)
- **P6 Multimodal Models:** Connectors, Discrete Visual Tokenization (+ VQ-VAE on-ramp), Unified Multimodal,
  Multimodal Evaluation

The **split** (MoE ends P4 / sparse opens P5) is the review's key structural fix: MoE is FFN conditional-compute
(efficiency); sparse attention is a sub-quadratic sequence mixer (kin to linear-attention/SSMs), so escape-one (sparse)
flows into escape-two (selective-SSM) → hybrids as one contiguous P5 movement.

## Dossier-coverage audit — preconditions (run 2026-07-10)

Well-anchored: NSA core, BigBird/Yun universality (fully), MLA compression, KV-eviction family, MQA/GQA, expert-choice,
enc-dec taxonomy. **Gaps to resolve before/while authoring:**

1. **[BLOCKER] Corrected MoE traffic model ($A_B\mu$, not $E\mu$) is UNANCHORED.** `research_mixture_of_experts` anchors
   active-vs-total *params* (Mixtral 47B/13B, OLMoE 7B/1B) + FLOP cuts (GLaM), not memory *traffic*. **Resolution:
   DERIVE the three-quantity model from the ch12 roofline (`def-tf12-cost-eq`) + routing, citing the anchored param/FLOP
   facts as grounding** (a derivation needs no primary). Add a MoE-serving primary top-up only if citing empirical
   traffic/latency numbers. It must NOT ship as a bare cited fact.
2. **[HIGH] MLA decoupled-RoPE** unanchored → targeted DeepSeek-V2 (2405.04434) top-up, or drop the mechanism.
3. **[MED] Load-balancing aux-loss / capacity-factor** anchored only *negatively* → pull a positive excerpt from
   Switch (2101.03961) / ST-MoE (2202.08906).
4. **[LOW] Synthesis-only** (NSA sliding-window branch + GQA-alignment, entmax "still $O(n^2)$" caveat, $\Theta(Lw)$
   receptive field): frame as derivations/standard results, not footnoted claims.

## Extend — two new chapters

### NEW ch — Mixture-of-Experts (ends P4; `research_mixture_of_experts`)
- **Extract** the current ch12 MoE unit (`def-tf12-moe`, `prop-tf12-moe-flops`, `rem-tf12-expert-parallel`). ch12 keeps
  a one-line forward-ref; edit "five techniques"→"four" (12:36), move LO TF-12.7, strip MoE from the frontmatter theorem
  list (12:11), repoint the two ch17 `def-tf12-moe` refs (17:117,121).
- **Rebuild the cost model** as the derived three-quantity roofline: resident $E\mu$ · activated $Tk\Phi$ · traffic
  $A_B\mu$ (active-expert union). The $k/E$ intensity holds only when a batch activates all experts; single-token decode
  ≈ dense. Define the routing gradient **locally** (top-$k$ need not use STE — do not depend on the VQ-VAE STE).
- Load-balancing aux loss (positive excerpt), capacity factor + drop/overflow, expert-choice vs token-choice, landmarks
  (GShard/Switch/GLaM/ST-MoE/BASE/Mixtral/DeepSeekMoE/OLMoE) in remarks/table, expert-parallel systems remark (fix
  "sharding attacks bytes-read" → it changes residency + adds all-to-all). Backlinks: ch06 (FFN), ch09 (routing
  objective), ch11-12 (systems).

### NEW ch — Sparse & Sub-Quadratic Attention (opens P5; `research_sparse_attention_patterns` + `research_trainable_sparse_attention`)
- §1 quadratic wall as sparsity opportunity → §2 static/factorized (**sliding-window relocated from old-ch14
  `def-tf14-swa`**; dilated/strided/block/global; Sparse Transformer, Longformer, BigBird) → §3 content-based (Reformer
  LSH, Routing k-means; entmax/sparsemax with a **boxed caveat**: representational, still $O(n^2)$ scores, NOT
  sub-quadratic) → §4 NSA formalized (branch decomposition + complexity prop) + MoBA/DSA/V3.2 dated `last_verified`
  frontier remark.
- BigBird universality stated as a **parallel** result to `thm-tf7-universal-approx` (different hypotheses — NOT a
  "refinement"/corollary). Per-pattern complexity props mirror `prop-tf7-complexity`. No linear-attention re-derivation
  (forward-ref the adjacent Selective-SSM chapter).

## Improve — existing chapters
- **MLA → ch05:** `def-tf5-mla` + honest cache-size prop on a new symbol **$d_{\text{cache}} = h_kd_k + h_vd_v$**
  (defined in ch05, then used in ch12 — this fixes the ch05↔ch12 MHA-scoping gap where `prop-tf12-kv-memory` silently
  assumed $h_kd_k=d$). MLA compresses a distinct latent axis $d_c$ + decoupled RoPE (gated on precondition #2), not a
  point on the $g$-curve.
- **KV eviction → ch12:** StreamingLLM/H2O/SnapKV/Quest as `last_verified` remarks, quarantined **"approximate — breaks
  `prop-tf8-prefix-reuse`"** so they don't undercut ch12's exactness spine.
- **ch02 / ch08 citation enrichment** from `research_recurrent_seq2seq` / `research_encoder_decoder_seq2seq` (Bahdanau
  is cross-linked out to `research_transformer_architecture`; LSTM CEC is pre-arXiv name-only, per the dossiers).

## Math fixes — IN SCOPE now (blockers + touched chapters)
1. ch12 MoE three-quantity cost model (before extraction). 2. ch05↔ch12 `$d_{\text{cache}}$` unification (before MLA).
3. old-ch13→ new SSD chunk wording: $c\asymp\sqrt{d_s}$ minimizes the arithmetic surrogate; $c\asymp d_s$ is the
hardware-shape choice on the same $\Theta(nd_sd)$ plateau (asymptotics unchanged).

## Math fixes — DEFERRED → pre-seed the proof-audit (survivors of the 3-round review)
See `proof-audit_2026-07-03.md`'s pre-seeded list. In brief: ch10 contrastive over-reach + ch18:33 propagation; ch07
encoder⟺cross-attention in-chapter contradiction; ch17 any-to-any tag-factor omission; ch17 finite-alphabet wording
(prop + Exercise 17.3); ch18 prose N-4/N-5; ch08 definition-before-use. **Reviewed and REFUTED (do not seed):** ch13
dual-discretization (explicitly scoped), ch10 Mahalanobis (pooled reps in ambient $\R^d$; sphere is nonlinear).

## Migration, glossaries, completeness, repairs
- **IDs/prose:** semantic chapter-free IDs for new content; migrate moved-chapter IDs once; **prose-number grep sweep**
  (`Chapter \d` / `Ch \d` / `ch\. \d`) as an acceptance criterion — CI (`validate`) cannot catch prose numbers (ch18
  already ships two wrong ones today: N-4/N-5).
- **Glossaries:** notation = augment ch00's standing tables into a **disambiguation index** (one row per symbol×meaning;
  add $\gamma,\alpha,K,d_{\text{cache}}$; enumerate the column-vector switches) + `<NotationOverride>` chapter boxes +
  a back-matter quick-ref card. Terminology = back-matter A–Z (unit/token/code/patch, state, attention-output pre/post-
  $W^O$, exact-vs-lossless, resident/activated/traffic). A single one-referent table across the corpus is infeasible; a
  scoped index is. (Scaffold back-matter support = infra check at authoring.)
- **Completeness:** decoding/sampling section (greedy/temperature/top-k/top-p on the softmax row; ch09 or ch12);
  `rem-tf6-rmsnorm` (LN-Jacobian bound carries over); VQ-VAE autoencoder on-ramp in the visual-tokenization chapter.
- **Narrative repairs:** old-ch14 closing → close the **sub-quadratic-mixer arc** + bridge to multimodality (not "the
  book"); scope ch03:35/438's "remainder of the book is both escapes" to match + add the efficiency-interlude note to
  the ch03 roadmap; ch07→ch08 distinguishing sentence; dual-footing discipline in the new chapters (define over rows
  $\mathbf x_t\in\R^d$; text + patch examples together, no vision-sparse silo); `last_verified`-gated frontier.

## Verification protocol
New chapters + corrected propositions: **Codex 5.6** (adversarial math — substituting for out-of-credits Fable) +
Sonnet (style) + Python numeric compute-verification (seq-models-arc precedent).

## Delivery — phased shippable PRs
1. **Math-fix blockers + $d_{\text{cache}}$ unification** (small; de-risks MoE + MLA).
2. **Mechanical re-part + ID/prose migration + MoE-extract** (frontmatter `part:` + semantic-ID moves + prose sweep).
3. **MoE chapter** (derived cost model). 4. **Sparse chapter**. 5. **Glossaries + completeness + narrative repairs.**
Each independently reviewable/mergeable; isolates the risky renumber from content. Local gate per PR: `npm run validate`
+ `npm run build` + 0 KaTeX errors.

## Verification (of the whole track, at execution)
- All six dossiers' cited claims resolve to a primary + `evidence_ledger` id (or a "derive"/"top-up" tag per the
  coverage audit); the MoE traffic model is derived, not asserted.
- Prose-number sweep returns no wrong `Chapter N`; `validate` resolves all XRefs; build green.
- The two new chapters pass the Codex-5.6 + Sonnet + numeric protocol; the split reads as one arc (P5 = sparse →
  selective-SSM → hybrids).
