# Dossier→guide integration (Track A) — 6-part restructure, review-hardened

**Status:** execution in progress; A0–A3 complete, A4 existing-chapter enrichment next. Supersedes
`docs/notes/sparse-attention-chapter-ideas_2026-07-09.md`. Companion: `topic-gap-expansion_2026-07-10.md` (Track B).

**Readiness review (Codex 2026-07-11):** the roadmap-readiness pass
(`docs/audits/roadmap-readiness_2026-07-11.md`) returned NO-GO for the backlog *as phased* (direction
A→B→C sound). Its blocking/important fixes are folded in below: the PR sequence is re-split (re-part / ID-migration /
MoE-author+extract are now separate — extracting MoE before its chapter exists would leave ch15 hollow), an explicit
**MoE derivation gate** precedes authoring, **ID-migration + bibliography invariants** are named, the **property-test
harness lands during this track** (not deferred to the proof-audit), and **infra-readiness spikes** run before
authoring.

## Context

The six merged research dossiers (`~/Claude/research-dossiers/`, research-dossiers PR #4) are the guide's backing
evidence base, but the guide cites none yet. This track (a) **extends** the guide with two new chapters (Mixture-of-
Experts; Sparse & Sub-Quadratic Attention) and (b) **improves** existing chapters with anchored primaries, inside a
**6-part restructure** validated by a 3-voice / 3-round review + a dossier-coverage audit. This active plan and its
tracked readiness review are now the authoritative record; the former home-directory design record is stale.

**Cite-provenance principle:** the guide cites **primary papers** (`<Cite key=.../>` + `bibliography.bib` /
`src/data/references.json`), never dossier slugs. Per claim, pull the anchored excerpt + arXiv id from the dossier's
`evidence_ledger.yml` / `agent_index/`, add the primary, cite it — satisfying "cite primaries" + "no unanchored
numbers", with the dossier as the verbatim-anchored provenance layer.

## Target structure — 6 parts

Part titles live only as prose in `README.md` (frontmatter carries the numeric `part:`). **IDs are semantic /
chapter-free** (precedent: ch00 `def-softmax`, all `fig-*` — they pass `validate`), so this and future restructures do
not renumber IDs. Final display numbers deliberately reserve 08/11/13 for Track B and 16/17 for Track A; current
chapters keep number-free slugs while those gaps are unfilled.

- **P1 Foundations:** 00 Notation, 01 Input Representations (+ BPE section — see Track B)
- **P2 Recurrence & Linear State:** 02 Recurrent Networks, 03 Linear Recurrences & SSM
- **P3 Transformer Architectures & Objectives:** 04 Attention, 05 Multi-Head Attention, 06 Block, 07 Composition,
  **08 reserved — In-Context Learning**, 09 Encoder-Decoder Families, 10 Training, **11 reserved — RLHF/DPO**,
  **12 Encoder Readouts, Contrastive Alignment, and Detection** (moved from old P4; coda).
- **P4 Efficient & Conditional Computation:** **13 reserved — Scaling Laws**, 14 Training Optimizations,
  15 Inference Optimizations, **16 reserved — Mixture-of-Experts**
- **P5 Sub-Quadratic & Selective Sequence Models:** **17 reserved — Sparse & Sub-Quadratic Attention**,
  18 Selective State Spaces (formerly ch13), 19 Modern Recurrent & Hybrid (formerly ch14)
- **P6 Multimodal Models:** 20 Connectors, 21 Discrete Visual Tokenization (+ VQ-VAE on-ramp),
  22 Unified Multimodal, 23 Multimodal Evaluation

The **split** (MoE ends P4 / sparse opens P5) is the review's key structural fix: MoE is FFN conditional-compute
(efficiency); sparse attention is a sub-quadratic sequence mixer (kin to linear-attention/SSMs), so escape-one (sparse)
flows into escape-two (selective-SSM) → hybrids as one contiguous P5 movement.

## Dossier-coverage audit — preconditions (run 2026-07-10)

Well-anchored: NSA core, BigBird/Yun universality (fully), MLA compression, KV-eviction family, MQA/GQA, expert-choice,
enc-dec taxonomy. **Gaps to resolve before/while authoring:**

1. **[BLOCKER] Corrected MoE traffic model ($A_B\mu$, not $E\mu$) is UNANCHORED.** `research_mixture_of_experts` anchors
   active-vs-total *params* (Mixtral 47B/13B, OLMoE 7B/1B) + FLOP cuts (GLaM), not memory *traffic*. **Resolution:
   DERIVE the three-quantity model from the ch15 roofline (`def-cost-eq`) + routing, citing the anchored param/FLOP
   facts as grounding** (a derivation needs no primary). Add a MoE-serving primary top-up only if citing empirical
   traffic/latency numbers. It must NOT ship as a bare cited fact.
2. **[HIGH] MLA decoupled-RoPE** unanchored → targeted DeepSeek-V2 (2405.04434) top-up, or drop the mechanism.
3. **[MED] Load-balancing aux-loss / capacity-factor** anchored only *negatively* → pull a positive excerpt from
   Switch (2101.03961) / ST-MoE (2202.08906).
4. **[LOW] Synthesis-only** (NSA sliding-window branch + GQA-alignment, entmax "still $O(n^2)$" caveat, $\Theta(Lw)$
   receptive field): frame as derivations/standard results, not footnoted claims.

## Extend — two new chapters

### NEW ch16 — Mixture-of-Experts (ends P4; `research_mixture_of_experts`)
- **Extract** the current ch15 MoE unit (`def-moe`, `prop-moe-flops`, `rem-expert-parallel`). ch15 keeps
  a one-line forward-ref; edit "five techniques"→"four" (15:36), move LO lo-moe-cost-accounting, strip MoE from the frontmatter theorem
  list (15:11), repoint the two ch22 `def-moe` refs (22:134,138).
- **Rebuild the cost model** as the derived three-quantity roofline: resident $E\mu$ · activated $Tk\Phi$ · traffic
  $A_B\mu$ (active-expert union). The $k/E$ intensity holds only when a batch activates all experts; single-token decode
  ≈ dense. Define the routing gradient **locally** (top-$k$ need not use STE — do not depend on the VQ-VAE STE).
- Load-balancing aux loss (positive excerpt), capacity factor + drop/overflow, expert-choice vs token-choice, landmarks
  (GShard/Switch/GLaM/ST-MoE/BASE/Mixtral/DeepSeekMoE/OLMoE) in remarks/table, expert-parallel systems remark (fix
  "sharding attacks bytes-read" → it changes residency + adds all-to-all). Backlinks: ch06 (FFN), ch10 (routing
  objective), ch14–15 (systems).

### NEW ch17 — Sparse & Sub-Quadratic Attention (opens P5; `research_sparse_attention_patterns` + `research_trainable_sparse_attention`)
- §1 quadratic wall as sparsity opportunity → §2 static/factorized (**sliding-window relocated from ch19
  (formerly ch14),
  `def-swa`**; dilated/strided/block/global; Sparse Transformer, Longformer, BigBird) → §3 content-based (Reformer
  LSH, Routing k-means; entmax/sparsemax with a **boxed caveat**: representational, still $O(n^2)$ scores, NOT
  sub-quadratic) → §4 NSA formalized (branch decomposition + complexity prop) + MoBA/DSA/V3.2 dated `last_verified`
  frontier remark.
- BigBird universality stated as a **parallel** result to `thm-universal-approx` (different hypotheses — NOT a
  "refinement"/corollary). Per-pattern complexity props mirror `prop-complexity`. No linear-attention re-derivation
  (forward-ref the adjacent Selective-SSM chapter).

## Improve — existing chapters
- **MLA → ch05:** `def-mla` + honest cache-size prop on a new symbol **$d_{\text{cache}} = h_kd_k + h_vd_v$**
  (defined in ch05, then used in ch15 — this fixes the ch05↔ch15 MHA-scoping gap where `prop-kv-memory` silently
  assumed $h_kd_k=d$). MLA compresses a distinct latent axis $d_c$ + decoupled RoPE (gated on precondition #2), not a
  point on the $g$-curve.
- **KV eviction → ch15:** StreamingLLM/H2O/SnapKV/Quest as `last_verified` remarks, quarantined **"approximate — breaks
  `prop-prefix-reuse`"** so they don't undercut ch15's exactness spine.
- **ch02 / ch09 citation enrichment** from `research_recurrent_seq2seq` / `research_encoder_decoder_seq2seq` (Bahdanau
  is cross-linked out to `research_transformer_architecture`; LSTM CEC is pre-arXiv name-only, per the dossiers).

## Math fixes — IN SCOPE now (blockers + touched chapters)
1. ch15 MoE three-quantity cost model (before extraction). 2. ch05↔ch15 `$d_{\text{cache}}$` unification (before MLA).
3. ch18 SSD chunk wording (formerly ch13): $c\asymp\sqrt{d_s}$ minimizes the arithmetic surrogate; $c\asymp d_s$ is the
hardware-shape choice on the same $\Theta(nd_sd)$ plateau (asymptotics unchanged).

## Math fixes — pre-seed the proof-audit (survivors of the 3-round review)
See `proof-audit_2026-07-03.md`'s pre-seeded list. In brief: ch12 contrastive over-reach + ch23:33 propagation; ch07
encoder⟺cross-attention in-chapter contradiction (**+ the `three-architectures` figure caption from #10 — fix figure
and prose together**, since the merged figure renders the same "unused 4th cell" framing); ch22 any-to-any tag-factor
omission; ch22 finite-alphabet wording (prop + Exercise 22.3); ch23 prose N-4/N-5; ch09 definition-before-use. **All six
confirmed groups are pulled forward into A1** — restructuring must not migrate known-invalid material; the terminal
audit verifies non-regression rather than rediscovering them. **Reviewed and REFUTED (do not seed):** ch18
dual-discretization (explicitly scoped), ch12
Mahalanobis (pooled reps in ambient $\R^d$; sphere is nonlinear).

## Migration, glossaries, completeness, repairs
- **IDs/prose:** semantic chapter-free IDs are now migrated; retain the old→new manifest and a **prose-number grep
  sweep** (`Chapter \d` / `Ch \d` / `ch\. \d`) as acceptance criteria — CI (`validate`) cannot catch prose numbers
  (the review caught two wrong ones in ch23 before A1).
- **Glossaries:** notation = augment ch00's standing tables into a **disambiguation index** (one row per symbol×meaning;
  add $\gamma,\alpha,K,d_{\text{cache}}$; enumerate the column-vector switches) + `<NotationOverride>` chapter boxes +
  a back-matter quick-ref card. Terminology = back-matter A–Z (unit/token/code/patch, state, attention-output pre/post-
  $W^O$, exact-vs-lossless, resident/activated/traffic). A single one-referent table across the corpus is infeasible; a
  scoped index is. The web routes and PDF print override both include the quick reference and glossary.
- **Completeness:** decoding/sampling section (greedy/temperature/top-k/top-p on the softmax row) in Inference
  Optimizations, with a forward reference from Training;
  `rem-rmsnorm` (LN-Jacobian bound carries over); VQ-VAE autoencoder on-ramp in the visual-tokenization chapter.
- **Narrative repairs:** ch19 closing (formerly ch14) → close the **sub-quadratic-mixer arc** + bridge to multimodality (not "the
  book"); scope ch03:35/438's "remainder of the book is both escapes" to match + add the efficiency-interlude note to
  the ch03 roadmap; ch07→ch09 distinguishing sentence; dual-footing discipline in the new chapters (define over rows
  $\mathbf x_t\in\R^d$; text + patch examples together, no vision-sparse silo); `last_verified`-gated frontier.

## Verification protocol
New chapters + corrected propositions: **Codex 5.6** (adversarial math — substituting for out-of-credits Fable) +
Sonnet (style) + Python numeric compute-verification (seq-models-arc precedent).

## Delivery — eight phased shippable PRs (execution lock 2026-07-13)
The old PR2 bundled re-part + ID-migration + MoE-extraction — too many failure modes, and extracting MoE before the MoE
chapter exists leaves ch15 hollow with dangling forward-refs. The execution review further separated verification,
known correctness, and existing-chapter enrichment:
1. **A0 verification foundation (complete):** stdlib property harness + Python CI; tracked corpus and property-coverage manifests;
   durable in-repo provenance; scaffold 4.26.2 dependency floor. The suite begins with the already-correct roofline.
2. **A1 all known correctness + quantitative spine (complete):** fix all six pre-seeded groups; retitle the detection chapter;
   correct $d_{\text{cache}}$, SSD wording, and the MoE derivation; complete all four property-test families. The
   **MoE derivation gate** separates resident $E\mu$, activated $Tk\Phi$, and traffic $A_B\mu$, with limiting-case checks
   for one-token decode, $A_B=E$, repeated routing, and expert sharding.
3. **A2 mechanical re-part ONLY (complete)** — frontmatter `part:` moves plus matching README/CLAUDE metadata, no ID/content edit.
4. **A3 semantic-ID + final-number migration (complete)** — allocate final 00–23 numbering once with planned gaps; generate the
   old→new/retired manifest; update every anchor class and printed number; pass the invariants below.
5. **A4 existing-chapter enrichment (next)** — MLA, approximate KV selection/eviction, and ch02/ch09 citations.
6. **A5 MoE chapter** — author AND extract from Inference Optimizations atomically.
7. **A6 Sparse & Sub-Quadratic Attention chapter** — relocate sliding-window material atomically.
8. **A7 apparatus + completeness + narrative repairs** — native glossary, local notation overrides, web+print quick
   reference/glossary, decoding, RMSNorm, VQ-VAE onramp, narrative sweep, and plan closeout.
Each independently reviewable/mergeable. **Per-PR gate:** `npm run validate` + `npm run build` + 0 KaTeX errors + 0
duplicate labels + (content PRs) the **bibliography gate** — every new `<Cite key>` resolves 1:1 through
`bibliography.bib` → `src/data/references.json`, keys unique.

**ID-migration invariants (PR3, re-checked after every later insertion):** corpus-wide duplicate-ID check; every old ID
either mapped or deliberately retired; no dangling `<XRef>`/label entries; no stray chapter-prefixed IDs; generated labels
match displayed chapter/theorem numbers; prose-number sweep after *each* insertion (semantic IDs stop key-drift, not
printed-number drift).

## Verification (of the whole track, at execution)
- All six dossiers' cited claims resolve to a primary + `evidence_ledger` id (or a "derive"/"top-up" tag per the
  coverage audit); the MoE traffic model is derived, not asserted.
- Prose-number sweep returns no wrong `Chapter N`; `validate` resolves all XRefs; build green.
- The two new chapters pass the Codex-5.6 + Sonnet + numeric protocol; the split reads as one arc (P5 = sparse →
  selective-SSM → hybrids).
