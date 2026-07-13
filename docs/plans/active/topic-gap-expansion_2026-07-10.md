# Topic-gap expansion (Track B) — four convergent gaps + evidence lock

**Status:** evidence reconciliation in progress. Track B content merges after Track A, while evidence validation and
drafting run in parallel. Repository inspection found that DPO/RLHF and scaling already have authoritative strict-live
dossiers; issues #5/#6 must resolve against those owners rather than by creating duplicates.

**Readiness review (Codex 2026-07-11):** the roadmap-readiness pass
(`docs/audits/roadmap-readiness_2026-07-11.md`) flagged two fixes, folded in below: the structure-design
pass becomes a hard **B0 exit gate** (not an at-execution afterthought), and evidence reconciliation **runs in parallel
with Track A** (only authoring waits on A3 + evidence acceptance) — so the critical path is evidence readiness, not
Track A completion.

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
- **Why:** ch09 "Training a Transformer" promises the training objective "from first principles" but delivers only
  pretraining MLE; every model it cites (GPT/Llama) is *defined* by a second objective it never mentions. Undercuts a
  title-level claim.
- **Shape (DTP-native):** derive the KL-regularized optimal policy $\pi\propto\pi_{\text{ref}}e^{r/\beta}$ → invert to
  express reward through policy → substitute into the Bradley-Terry likelihood → closed-form classification loss (same
  shape as the book's own $q-y$ logit-gradient / label-smoothing proofs). Reward modeling + PPO as the RL baseline DPO
  reduces.
- **Placement:** chapter in **P3 (Objectives), after Training**. Evidence owners: `research_rlhf` for reward modeling,
  InstructGPT, and PPO; `research_post_training_preference` for DPO and the IPO/KTO/ORPO frontier.

### 2. Scaling laws / Chinchilla — the unstated capstone
- **Why:** the capstone the ch11 training-memory + ch12 roofline accounting visibly builds toward ("why models are the
  size they are" is set up, never answered); the book already silently borrows the scaling-laws notation ($N$-params in
  ch11, $1/T$ in ch09).
- **Shape:** the empirical power-law fit $L(N,D)$ + a **general Lagrangian derivation** under $C\approx6ND$; claim
  square-root allocation only when the fitted exponents are equal or approximately equal.
- **Placement:** short chapter that **opens P4**. Evidence owner: `research_llm_pretraining_scaling`, extended only for
  genuinely missing inference-aware/over-training frontier evidence.

### 3. In-context learning / constructive attention capability — closes an asymmetry
- **Why:** the book proves the *limitations* of alternatives (ch03 LTI obstruction, ch14 fixed-state recall bound) but
  never proves attention's *capability* — ch07:116 ("in-context learning replaces explicit cross-attention") and
  ch14:206 (attention "solves associative recall") gesture without formalizing.
- **Scope (the Codex/Gemini-vs-Claude split):** the **theorem-shaped version** only — a constructive associative-lookup
  theorem with a softmax retrieval-error bound; copying/induction as a two-layer construction; one controlled ICL result
  (e.g. a transformer implementing linear-regression gradient descent). **Keep empirical "induction heads" and
  ICL-as-implicit-GD framing OUT** (unsettled/learning-theoretic) — cite them as a remark, don't formalize.
- **Placement:** section-to-chapter in **P3, after attention/composition**. **New dossier
  `research_incontext_associative_memory`** (associative memory / Hopfield-attention, induction-head constructions,
  ICL-as-algorithm results; clearly separate the empirical from the constructive).

### 4. Tokenization / BPE — textbook, no dossier
- **Why:** the sharpest **internal-consistency** crack in the dual-footing thesis — vision's tokenizer is *constructed*
  (ch16 VQ, straight-through, code rate) while text's is *assumed* (ch01 "a vocabulary is a finite set of indices").
- **Shape:** a **section/remark in ch01** (P1) mirroring ch16's rate/compression view; the BPE merge algorithm + why
  subword beats word/char. Author from primaries (BPE 1508.07909 / SentencePiece 1808.06226) — no strict-live dossier.

## Deferred / out of scope
- **DEFERRED (user):** diffusion/flow-matching for generative vision (transformer-as-denoiser, DiT). The AR/VQ route is
  a legitimate self-contained lens; acknowledge the alternative as a scoped ch17 sidenote now; revisit as a P6 addition
  (probability-flow ODE + conditional flow-matching) after this program.
- **OUT OF SCOPE (topic sweep; author may cite):** optimizer-convergence theory (Adam bounds, loss landscape);
  mechanistic-interpretability circuits/superposition; expressivity-as-complexity-classes ($\mathsf{TC}^0$/Dyck — *the
  most upgrade-worthy*, a candidate future remark); RAG; PEFT-beyond-LoRA; quantization-beyond-affine; broad
  generative-text eval. (Positional-encoding breadth, RMSNorm, init/signal-propagation are already covered or handled
  in Track A — not gaps.)

## Structure-design pass — a hard B0 EXIT GATE (per the Codex readiness review)
Track B grows the guide to ~24 chapters. Because IDs are semantic/chapter-free (Track A), adding chapters is cheap, but
**P3 gains ICL + RLHF/DPO**, while Scaling opens P4. Codex flagged "structure pass at execution" as too late; it is now a
**gate that must clear before any Track B authoring**, with explicit exit criteria:
- the authoritative DPO/scaling dossiers and the ICL evidence base are accepted (evidence ledgers usable);
- **chapter placement is fixed** — ICL after Composition, DPO after Training, Scaling opens P4;
- the **ICL theorem scope is frozen to the full constructive trio**: associative lookup + retrieval-error bound,
  explicit copying/induction construction, and one controlled transformer-as-gradient-descent result; empirical
  induction-head and implicit-GD interpretations remain remarks;
- the **DPO and scaling claims are pinned** to specific `evidence_ledger` ids in their dossiers.
Only then does authoring (B1–B4) begin.

## Delivery — phased
(B0-evidence) validate the existing DPO/RLHF and scaling owners, add only missing top-ups, and build/validate the ICL
evidence base without duplicating another dossier's ownership. **Run this in parallel with Track A.**
(B0-gate) the structure-design **exit gate** above clears.
(B1) BPE ch01 section (no dossier). (B2) ICL chapter. (B3) RLHF/DPO chapter. (B4) Scaling-laws chapter — each authored
only after the gate clears and A3 has landed. Drafts may run beside A4–A7, but content merges wait for A7 and proceed
serially. Each B PR updates apparatus/metadata after rebasing; B4 performs the final whole-corpus sweep.
Then the pre-seeded proof-audit runs over the full ~24-chapter corpus.

## Verification (at execution)
Each new chapter: cited claims resolve to its authoritative dossier evidence ledgers (BPE from primaries); Codex-5.6 + Sonnet +
Python numeric protocol; DPO/scaling derivations numerically checked; the structure-design pass keeps the parts
balanced and the dual-footing thesis intact (BPE closes the text-tokenizer asymmetry).
