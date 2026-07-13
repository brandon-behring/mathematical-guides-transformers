# Topic-gap expansion (Track B) — four convergent gaps + evidence lock

**Status:** B0 evidence reconciliation and the atomic structure-design exit gate cleared on 2026-07-13. The accepted
`research-dossiers` snapshot, per-owner provenance commits, and exact evidence IDs are frozen in the B0 record below;
no Track B guide prose was authored before clearance. **B1 (BPE in ch01) is next**, followed serially by B2 ICL → B3
RLHF/DPO → B4 Scaling, with each PR based on its merged predecessor.

**Readiness review (Codex 2026-07-11):** the roadmap-readiness pass
(`docs/audits/roadmap-readiness_2026-07-11.md`) flagged two fixes, folded in below: the structure-design
pass becomes a hard **B0 exit gate** (not an at-execution afterthought). Track A's A3/A7 prerequisites and the B0
evidence/structure gate are complete; the critical path is now the locked B1→B4 merge sequence.

## Context

A 3-voice topic-coverage sweep (Codex + Gemini + Claude) asked what whole **topics** the guide is missing for its
stated ambition (not flow/notation — a separate 3-round review covered those). The book proved *more* complete than
expected — positional encodings are deep (RoPE proof, ALiBi, 2D), LoRA fully developed, init/signal-propagation
covered — so several candidates were already closed. Four gaps converged (≥2 voices) and are **folded in**; diffusion is
**deferred**; the rest are **out of scope** with rationale below.

Consistent with the hybrid-backing decision: **dossier-back the substantive research areas; author the textbook item
from primaries.** Any genuinely new dossier or top-up uses the same strict-live v3 pipeline as the accepted corpus
(`~/Claude/research_toolkit`).

## The four additions

### 1. RLHF / Preference Optimization (DPO) — load-bearing
- **Why:** ch10 "Training a Transformer" promises the training objective "from first principles" but delivers only
  pretraining MLE; it never explains the preference/reward objectives used to turn many base GPT/Llama-family models
  into instruct/chat variants. This undercuts a title-level claim.
- **Shape (DTP-native):** derive the KL-regularized optimal policy $\pi\propto\pi_{\text{ref}}e^{r/\beta}$ → invert to
  express reward through policy → substitute into the Bradley-Terry likelihood → closed-form classification loss (same
  shape as the book's own $q-y$ logit-gradient / label-smoothing proofs). Reward modeling and PPO supply historical
  RLHF context; DPO follows from the KL-regularized reward objective plus Bradley–Terry, not from algebraically reducing
  PPO.
- **Placement:** chapter in **P3 (Objectives), after Training**. Evidence owners: `research_rlhf` for reward modeling,
  InstructGPT, and PPO; `research_post_training_preference` for DPO and the IPO/KTO/ORPO frontier.

### 2. Scaling laws / Chinchilla — the unstated capstone
- **Why:** the capstone the ch14 training-memory + ch15 roofline accounting visibly builds toward ("why models are the
  size they are" is set up, never answered); the book already silently borrows the scaling-laws notation ($N$-params in
  ch14, $1/T$ in ch10).
- **Shape:** the empirical power-law fit $L(N,D)$ + a **general Lagrangian derivation** under $C\approx6ND$; claim
  square-root allocation only when the fitted exponents are equal or approximately equal.
- **Placement:** short chapter that **opens P4**. Evidence owner: `research_llm_pretraining_scaling`, extended only for
  genuinely missing inference-aware/over-training frontier evidence.

### 3. In-context learning / constructive attention capability — closes an asymmetry
- **Why:** the book proves the *limitations* of alternatives (ch03 LTI obstruction, ch19 fixed-state recall bound) but
  never proves attention's *capability* — ch07:126 ("in-context learning replaces explicit cross-attention") and
  ch19:206 (attention "solves associative recall") gesture without formalizing.
- **Scope (the Codex/Gemini-vs-Claude split):** the **theorem-shaped version** only — a constructive associative-lookup
  theorem with a softmax retrieval-error bound; copying/induction as a two-layer construction; one controlled ICL result
  (e.g. a transformer implementing linear-regression gradient descent). **Keep empirical "induction heads" and
  ICL-as-implicit-GD framing OUT** (unsettled/learning-theoretic) — cite them as a remark, don't formalize.
- **Placement:** chapter in **P3, after attention/composition**. Accepted dossier
  `research_incontext_associative_memory` covers associative memory / Hopfield-attention, induction-head constructions,
  and ICL-as-algorithm results while separating the empirical from the constructive.

### 4. Tokenization / BPE — textbook, no dossier
- **Why:** the sharpest **internal-consistency** crack in the dual-footing thesis — vision's tokenizer is *constructed*
  (ch21 VQ, straight-through, code rate) while text's is *assumed* (ch01 "a vocabulary is a finite set of indices").
- **Shape:** a **section/remark in ch01** (P1) mirroring ch21's rate/compression view; the BPE merge algorithm plus the
  compression, vocabulary-size, sequence-length, and open-vocabulary tradeoffs among character, subword, and word
  units. Author from primaries (BPE 1508.07909 / SentencePiece 1808.06226) — no strict-live dossier.

## Deferred / out of scope
- **DEFERRED (user):** diffusion/flow-matching for generative vision (transformer-as-denoiser, DiT). The AR/VQ route is
  a legitimate self-contained lens; acknowledge the alternative as a scoped ch22 sidenote now; revisit as a P6 addition
  (probability-flow ODE + conditional flow-matching) after this program.
- **OUT OF SCOPE (topic sweep; author may cite):** optimizer-convergence theory (Adam bounds, loss landscape);
  mechanistic-interpretability circuits/superposition; expressivity-as-complexity-classes ($\mathsf{TC}^0$/Dyck — *the
  most upgrade-worthy*, a candidate future remark); RAG; PEFT-beyond-LoRA; quantization-beyond-affine; broad
  generative-text eval. (Positional-encoding breadth, RMSNorm, init/signal-propagation are already covered or handled
  in Track A — not gaps.)

## Structure-design pass — B0 EXIT GATE cleared 2026-07-13 (per the Codex readiness review)
Track B grows the guide to 24 chapters by filling reserved slots 08 (ICL), 11 (RLHF/DPO), and 13 (Scaling); Track A
fills 16 (MoE) and 17 (Sparse). Because IDs and slugs are semantic/chapter-free, adding chapters is cheap, but
**P3 gains ICL + RLHF/DPO**, while Scaling opens P4. Codex flagged "structure pass at execution" as too late; the gate
cleared before Track B authoring with these exit criteria:
- the authoritative RLHF, DPO, scaling, and constructive-ICL evidence owners were accepted with usable ledgers;
- **chapter placement is fixed** — ICL after Composition, DPO after Training, Scaling opens P4;
- the **ICL theorem scope is frozen to the full constructive trio**: associative lookup + retrieval-error bound,
  explicit copying/induction construction, and one controlled transformer-as-gradient-descent result; empirical
  induction-head and implicit-GD interpretations remain remarks;
- the **DPO and scaling claims are pinned** to specific `evidence_ledger` ids in their dossiers.
Authoring B1–B4 begins only from the accepted state recorded below.

### B0 acceptance record — cleared 2026-07-13

All SHAs refer to `brandon-behring/research-dossiers`. The reproducible accepted corpus snapshot is
`ffd4e3a184ea364b95764a541830a0bba9489c4b`, the `origin/main` commit containing the DPO equation top-up and every
earlier accepted owner. Per-owner evidence provenance is frozen as follows:

- **RLHF baseline — `research_rlhf`, accepted state `d13ceafd1200e19d106ff886ec6aace9cb5547a9`:**
  `ev_rlhf_0100` (pairwise human-preference signal), `ev_rlhf_0101` (PPO), `ev_rlhf_0102` (language-model reward
  learning), and `ev_rlhf_0105` (InstructGPT). These are abstract-level mechanism/context anchors; they support the
  baseline narrative, not a new proof of PPO's clipped surrogate.
- **DPO — `research_post_training_preference`, equation top-up
  `bc9e1f631aa4aa4bfb02900a04c3d98c13fda3d0` with qualification follow-up
  `7ae77214e4af8128c8d4307d4c473fca0fd3c3b4`:** `ev_post_training_preference_0001` and
  `ev_post_training_preference_0002` (core reparameterization/RL-free framing); `ev_post_training_preference_0003`,
  `ev_post_training_preference_0004`, `ev_post_training_preference_0005`, `ev_post_training_preference_0006`, and
  `ev_post_training_preference_0007` (exact KL objective → closed-form optimum → reward inversion → Bradley–Terry
  likelihood → DPO loss chain); and `ev_post_training_preference_0010`, `ev_post_training_preference_0011`,
  `ev_post_training_preference_0012`, and `ev_post_training_preference_0013` (ORPO/IPO/KTO frontier orientation). The
  frontier pins are method-framing atoms, not equation-complete bake-off evidence. The same-optimum reading is
  restricted to `β>0`, positive reference-policy support, the Bradley–Terry preference model, sufficient policy
  expressivity, and idealized global optimization; finite data, preference-model misspecification, restricted classes,
  or optimization error can break it.
- **Scaling — `research_llm_pretraining_scaling`, content commit
  `07e649de4397ebd205947f687634a21dca8e5c5f` (merged via `e66bf53813beab08497b34e0d8e1924dea2fb101`):**
  `ev_llm_pretraining_0001` (general empirical power law), `ev_llm_pretraining_0014` (separable Chinchilla loss),
  `ev_llm_pretraining_0015` (`C≈6ND`), `ev_llm_pretraining_0002` (near-equal empirical scaling),
  `ev_llm_pretraining_0016` (inference-aware allocation), and `ev_llm_pretraining_0017` (over-training). The general
  constrained optimum is a guide/dossier derivation from `0014` + `0015`; the square-root rule is scoped to equal or
  near-equal fitted exponents.
- **Constructive ICL — `research_incontext_associative_memory`, content commit
  `2edc981fec5322eae4e2370776c3f2201118b995` (merged via `303524b2bc30ae8869b25a10ff88d82cbb9d9cc6`):**
  `ev_incontext_associative_memory_0001` (attention formula grounding the dossier-derived margin/error bound);
  `ev_incontext_associative_memory_0006` and `ev_incontext_associative_memory_0007` (explicit two-layer induction/copy
  construction); and `ev_incontext_associative_memory_0010`, `ev_incontext_associative_memory_0011`, and
  `ev_incontext_associative_memory_0012` (controlled no-update linear-regression/GD constructions).
  `ev_incontext_associative_memory_0013` and `ev_incontext_associative_memory_0014` are accepted only for the dated
  empirical-induction remark; no broad implicit-GD interpretation enters the theorem spine.
- **BPE exception:** dossier-free by design. B1 remains author-from-primary work using Sennrich et al.
  (`arXiv:1508.07909`) and SentencePiece (`arXiv:1808.06226`); clearing B0 accepts that source boundary, not any
  unwritten guide claim.

This record clears the atomic authoring gate. Evidence pins freeze provenance, while the guide continues to cite the
primary papers rather than dossier slugs.

## Delivery — phased
This order—not the topic-heading order above—is authoritative:

1. **B0-evidence (complete 2026-07-13):** validate the existing DPO/RLHF and scaling owners, add only missing top-ups,
   and build/validate the ICL evidence base without duplicating another dossier's ownership.
2. **B0-gate (complete 2026-07-13):** record the accepted dossier commits and ledger IDs, then clear the
   structure-design exit gate above.
3. **B1 (next):** add the BPE section to ch01 (no dossier); the corpus remains 21 chapters.
4. **B2:** add ICL as ch08; the corpus becomes 22 chapters and 08 is no longer reserved.
5. **B3:** add RLHF/DPO as ch11; the corpus becomes 23 chapters and 11 is no longer reserved.
6. **B4:** add Scaling Laws as ch13; the corpus becomes 24 chapters and 13 is no longer reserved, then run the final
   whole-corpus sweep.
7. Run the pre-seeded terminal proof audit over the frozen 24-chapter corpus.

Each B PR proceeds only after its predecessor merges and updates the shared `NotationIndex`/`QuickReference`, glossary
entries where new terms warrant them, README/CLAUDE chapter metadata and occupied/reserved slots, corpus/property
manifests, and the prose-number sweep. Deployment remains a separate post-content task and is not part of this sequence.

## Verification (at execution)
Each new chapter: cited claims resolve to its authoritative dossier evidence ledgers (BPE from primaries); Codex-5.6 + Sonnet +
Python numeric protocol; DPO/scaling derivations numerically checked; the structure-design pass keeps the parts
balanced and the dual-footing thesis intact (BPE closes the text-tokenizer asymmetry).
