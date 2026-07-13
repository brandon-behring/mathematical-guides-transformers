# Topic-gap expansion (Track B) — four convergent gaps + evidence lock

**Status:** B0 evidence reconciliation is next; Track A is complete. No Track B guide prose is authored until the
atomic B0 exit gate clears. Repository inspection found that DPO/RLHF and scaling already have authoritative
strict-live dossier owners, `research_rlhf` + `research_post_training_preference` and
`research_llm_pretraining_scaling`; any missing evidence must be reconciled against those owners rather than by
creating duplicates.

**Readiness review (Codex 2026-07-11):** the roadmap-readiness pass
(`docs/audits/roadmap-readiness_2026-07-11.md`) flagged two fixes, folded in below: the structure-design
pass becomes a hard **B0 exit gate** (not an at-execution afterthought). Track A's A3 and A7 prerequisites are now
complete; evidence acceptance and the locked merge sequence remain the authoring gates, so the critical path is B0
evidence readiness.

## Context

A 3-voice topic-coverage sweep (Codex + Gemini + Claude) asked what whole **topics** the guide is missing for its
stated ambition (not flow/notation — a separate 3-round review covered those). The book proved *more* complete than
expected — positional encodings are deep (RoPE proof, ALiBi, 2D), LoRA fully developed, init/signal-propagation
covered — so several candidates were already closed. Four gaps converged (≥2 voices) and are **folded in**; diffusion is
**deferred**; the rest are **out of scope** with rationale below.

Consistent with the hybrid-backing decision: **dossier-back the substantive research areas; author the textbook item
from primaries.** Any genuinely new dossier or top-up uses the same strict-live v3 pipeline as the six merged
(`~/Claude/research_toolkit`).

## The four additions

### 1. RLHF / Preference Optimization (DPO) — load-bearing
- **Why:** ch10 "Training a Transformer" promises the training objective "from first principles" but delivers only
  pretraining MLE; every model it cites (GPT/Llama) is *defined* by a second objective it never mentions. Undercuts a
  title-level claim.
- **Shape (DTP-native):** derive the KL-regularized optimal policy $\pi\propto\pi_{\text{ref}}e^{r/\beta}$ → invert to
  express reward through policy → substitute into the Bradley-Terry likelihood → closed-form classification loss (same
  shape as the book's own $q-y$ logit-gradient / label-smoothing proofs). Reward modeling + PPO as the RL baseline DPO
  reduces.
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
- **Placement:** section-to-chapter in **P3, after attention/composition**. **New dossier
  `research_incontext_associative_memory`** (associative memory / Hopfield-attention, induction-head constructions,
  ICL-as-algorithm results; clearly separate the empirical from the constructive).

### 4. Tokenization / BPE — textbook, no dossier
- **Why:** the sharpest **internal-consistency** crack in the dual-footing thesis — vision's tokenizer is *constructed*
  (ch21 VQ, straight-through, code rate) while text's is *assumed* (ch01 "a vocabulary is a finite set of indices").
- **Shape:** a **section/remark in ch01** (P1) mirroring ch21's rate/compression view; the BPE merge algorithm + why
  subword beats word/char. Author from primaries (BPE 1508.07909 / SentencePiece 1808.06226) — no strict-live dossier.

## Deferred / out of scope
- **DEFERRED (user):** diffusion/flow-matching for generative vision (transformer-as-denoiser, DiT). The AR/VQ route is
  a legitimate self-contained lens; acknowledge the alternative as a scoped ch22 sidenote now; revisit as a P6 addition
  (probability-flow ODE + conditional flow-matching) after this program.
- **OUT OF SCOPE (topic sweep; author may cite):** optimizer-convergence theory (Adam bounds, loss landscape);
  mechanistic-interpretability circuits/superposition; expressivity-as-complexity-classes ($\mathsf{TC}^0$/Dyck — *the
  most upgrade-worthy*, a candidate future remark); RAG; PEFT-beyond-LoRA; quantization-beyond-affine; broad
  generative-text eval. (Positional-encoding breadth, RMSNorm, init/signal-propagation are already covered or handled
  in Track A — not gaps.)

## Structure-design pass — a hard B0 EXIT GATE (per the Codex readiness review)
Track B grows the guide to 24 chapters by filling reserved slots 08 (ICL), 11 (RLHF/DPO), and 13 (Scaling); Track A
fills 16 (MoE) and 17 (Sparse). Because IDs and slugs are semantic/chapter-free, adding chapters is cheap, but
**P3 gains ICL + RLHF/DPO**, while Scaling opens P4. Codex flagged "structure pass at execution" as too late; it is now a
**gate that must clear before any Track B authoring**, with explicit exit criteria:
- the authoritative DPO/scaling dossiers and the ICL evidence base are accepted (evidence ledgers usable);
- **chapter placement is fixed** — ICL after Composition, DPO after Training, Scaling opens P4;
- the **ICL theorem scope is frozen to the full constructive trio**: associative lookup + retrieval-error bound,
  explicit copying/induction construction, and one controlled transformer-as-gradient-descent result; empirical
  induction-head and implicit-GD interpretations remain remarks;
- the **DPO and scaling claims are pinned** to specific `evidence_ledger` ids in their dossiers.
Only then does authoring (B1–B4) begin.

**B0 acceptance record.** Clearing the gate requires recording, in this plan, the accepted commit SHA and the exact
`evidence_ledger.yml` identifiers for the DPO, RLHF, scaling, and constructive-ICL claims. Before that record exists,
the only permitted Track B artifacts are evidence reconciliation/top-ups in the owning dossier repository and chapter
outlines used to test the structure; at-risk guide prose is not started. The gate is atomic, including dossier-free BPE,
so the four guide changes retain one unambiguous serial baseline.

## Delivery — phased
This order—not the topic-heading order above—is authoritative:

1. **B0-evidence:** validate the existing DPO/RLHF and scaling owners, add only missing top-ups, and build/validate the
   ICL evidence base without duplicating another dossier's ownership.
2. **B0-gate:** record the accepted dossier commits and ledger IDs, then clear the structure-design exit gate above.
3. **B1:** add the BPE section to ch01 (no dossier); the corpus remains 21 chapters.
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
