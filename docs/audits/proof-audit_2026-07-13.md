# Proof-correctness audit — frozen 24-chapter corpus (2026-07-13)

Terminal argument-level audit of every formal unit in the post-expansion
transformers guide. The staged pipeline found **49 substantive defects or
load-bearing rigor gaps**; every one survived two independent adversarial
refuters. The terminal diff review then found three further cross-chapter scope
or integration defects, each independently upheld, for **52 source corrections
in total**. Three Stage-D candidates were rejected. One additional result that
lacked an adjacent proof received a new proof. The six defect groups pre-seeded
by the earlier roadmap review all passed their non-regression check.

## Frozen scope

The audited source was commit `8f913733a509751c54c606a29b4123ce2d8f8103`
(`main` after the scaling-laws merge). A result together with its adjacent
proof is one audit unit, rather than two independently counted units.

| Unit class | Frozen count | Treatment |
|---|---:|---|
| Definitions | 107 | Domain, existence, uniqueness, typing, and side conditions |
| Theorem / proposition / lemma / corollary units | 104 | Statement, proof, and statement↔proof agreement; 103 had a written proof |
| Exercise solutions | 133 | Prompt↔solution agreement and derivation; 41 Prove, 28 Derive, 11 Construct, 53 other |
| **Total** | **344** | Complete Stage A/C coverage |

The three source partitions were chapters 00–07 (116 units; 30 proof blocks),
08–15 (117 units; 35 proof blocks), and 16–23 (111 units; 38 proof blocks).
This is 344/344 frozen units. The lone result without an adjacent proof was
`prop-params`; its statement was also sent through blind derivation, then a
proof was added during the fix phase.

## Method

1. **Formalize and falsify.** Each partition inventoried hypotheses,
   quantifiers, conclusions, domains, and types. Machine-calculable claims were
   recomputed with deterministic adversarial cases (ties, empty sets, zero
   densities, unequal head widths, dense state transitions, and restricted
   model families). Definitions and non-numeric units received the same
   well-definedness and statement↔proof comparison, but were not misrepresented
   as numeric tests.
2. **Blind derivation.** Proof specifications and permitted prior statements
   were passed inline to agents forbidden to read the repository or browse.
   The blind stage covered all 103 written proofs, all 41 Prove solutions, and
   the unproved `prop-params` statement: **145 derivations**. Blindness remained
   intact.
3. **Compare.** Source owners reconciled the blind derivations against the
   guide proofs and Stage-A results. Missing detail in a deliberately sanitized
   specification was distinguished from missing detail in the source.
4. **Adversarial verification.** Every substantive candidate went to two
   role-separated refuters who had not found that partition. A split vote went
   to an independent tiebreak. The deduplicated set was 52 candidates:
   **49 upheld, 3 rejected, 0 unresolved**.

All available in-session reviewers were Codex agents, so model identity was not
mistaken for vendor diversity. The role separation was nevertheless real:
source owners, blind derivations, and refuters used separate contexts, and the
blind agents had no filesystem or browser access. The planned Gemini external
leg was attempted on three sanitized inline bundles but failed before inference
because the installed client/account tier was no longer eligible. An Anthropic
CLI fallback also failed before inference because both API credit and the
interactive weekly allowance were exhausted. No external verdict was counted,
and this report makes no cross-vendor-consensus claim.

## Blind-derivation assurance

| Partition | Agreement | Could not prove from sanitized spec | Stage-C disposition |
|---|---:|---:|---|
| Chapters 00–07 | 45 | 1 | The UAT omission exposed a real scope/metric rigor gap |
| Chapters 08–15 | 45 | 0 | All source arguments agreed |
| Chapters 16–23 | 49 | 5 | Four were supplied by source-local definitions; resampler cost exposed a real missing term/assumption |
| **Total** | **139** | **6** | **145/145 completed** |

The four reconciled terminal-partition cases were static sparse counts, chunked
SSD cost, hybrid decode-state accounting under its stated state-size
abstraction, and the exact stopped-gradient VQ coefficients. Positive agreement
covered the guide's high-risk local algebra: BPE accounting, positional/RoPE
identities, BPTT and constant-error flow, ZOH/convolution/scan equivalence,
HiPPO/NPLR, attention variance, MHA ranks and cache counts, normalization
Jacobians, the gradient highway, ICL algebra, scaling laws, sparse patterns,
SSD chunking, VQ objectives, and evaluation identities after qualification.

## Confirmed corrections

Every row below has a **2–0 UPHOLD** verification vote. “Defect” means a false,
ill-typed, or statement↔proof-inconsistent claim. “Gap” means an unstated
load-bearing assumption or undefined boundary case.

### Chapters 00–07 — 19

| ID / location | Class | Verified failure and correction |
|---|---|---|
| `prop-complexity` | Defect | Arbitrary value widths were simplified as though `h d_v=d`; full-block projections and linear activation memory were omitted. General widths and the standard-width/core-only crossover are now separated. |
| `def-cross-attention`, `def-decoder-block` | Defect | Cross-attention returned `m×d_v` and was added to an `m×d` residual. An output projection makes the map type-correct. |
| `prop-lti-obstruction` follow-up | Defect | Time invariance alone was said to block selection even with a nonlinear readout; a finite LTI shift register is a counterexample. The conclusion is restricted to the proved globally linear map. |
| `def-causal-mask` | Defect | A real matrix contained `-∞`. The definition now uses the extended-real/support convention. |
| `def-token-embedding`, `def-patch-embedding` | Defect | Transposes contradicted the standing row-vector convention. |
| `rem-rope-complex` | Defect | The real dot product was equated to a generally complex Hermitian sum; the real part is now explicit. |
| Exercise 4.2 | Defect | Marginal variance growth was treated as sufficient for one-hot attention; tied keys refute it. The conclusion now requires widening unique gaps. |
| `def-residual` prose | Defect | Identity was claimed “regardless of f”; it requires a branch that can be set to zero. |
| `prop-softmax-jacobian` prose | Defect | The simplex tangent plane was said to collapse at vertices; the softmax Jacobian collapses, not the affine tangent space. |
| `thm-universal-approx` cluster | Gap | The architecture class, `n≥2`, integrated `L^p` metric, domain symmetry, and learned separated additive positional table were underspecified; Exercise 7.5 incorrectly invoked uniform-limit closure. Statement, sketch, and exercise now carry the cited scope. |
| `thm-pe-rotation`, 2-D analogue | Gap | Integer shifts could leave the nonnegative position domain. |
| `def-kl` | Gap | Zero-mass and support-violation conventions were missing. |
| `def-bpe` / accounting result | Gap | Arbitrary merge rounds could continue after no positive-count pair remained. |
| `def-rope` | Gap | Pairing `d` coordinates required even `d`. |
| Exercise 6.4 | Gap | It used `epsilon=0` outside the LayerNorm definition's positive-epsilon domain. |
| `def-seq2seq` | Gap | “Any cell” was represented by one vector, omitting the LSTM `(c,h)` state pair. |
| Standing dimensions / MHA | Gap | Positive-integral dimensions and `h|d` were implicit where matrix widths use `d/h`. |
| `prop-scan` | Gap | `ceil(log2 n)` lacked `n≥1`. |
| Legendre/HiPPO generating-function proof | Gap | Termwise integration lacked the required uniform absolute convergence argument. |

### Chapters 08–15 — 15

| ID / location | Class | Verified failure and correction |
|---|---|---|
| Bidirectional encoder / Exercise 9.5 | Defect | A changed backward state need not change a merge that ignores it. Readout separation is now explicit. |
| `prop-ce-kl-training` | Defect | The gradient identity dropped the per-token `1/T` factor. |
| `def-ood-score` discussion | Defect | Nearest-inlier distance was called a monotone reparameterization of Gaussian NLL/Mahalanobis; it is now a separate analogue. |
| Mixed precision | Defect | `6e-5` was called the smallest fp16 positive value rather than the smallest normal, and FP32 Adam state was implicated in fp16 underflow. Normal/subnormal ranges and loss-scaling scope are corrected. |
| Exercise 14.4 | Defect | 13,107,200 adapter parameters are about `1/992` of 13B, not `1/320`; the latter denominator covers only selected dense matrices. |
| Quantization prose | Defect | Low-bit weight quantization was called reversible. Exact recovery now requires retaining the original checkpoint. |
| `prop-linear-attention-gd` construction | Gap | The claimed fixed layer lacked a typed token layout, projections, gating, query exclusion, residual channel, and normalization. The construction is now explicit. |
| Learning-rate schedule | Gap | `t` and warmup domains were missing. |
| Cosine similarity | Gap | Zero vectors made the definition undefined. |
| `def-ood-score` | Gap | `-log p` could be `+∞` despite a real codomain. |
| `prop-checkpoint-memory` | Gap | A continuous `sqrt(L)` optimizer was treated as an exact legal segment count. Integer/ceiling handling now preserves the asymptotic result. |
| `prop-zero-memory` | Gap | Resident precision was reused as wire precision and exact ring factors/schedule were omitted. The accounting now separates them. |
| `def-quantization` | Gap | Bit width, nondegenerate range, code domain, rounding ties, and constant blocks were undefined. |
| `prop-flash-io` | Gap | The traffic expression could fall below compulsory input/output traffic. The general bound includes `nd`, byte width, and the valid simplification regime. |
| Speculative decoding / `prop-spec-speedup` | Gap | Exact acceptance/residual sampling, the all-accepted bonus, `alpha=1`, and the cost regime were missing. |

### Chapters 16–23 — 15

| ID / location | Class | Verified failure and correction |
|---|---|---|
| `def-mixed-mask`, Exercise 22.5 | Defect | Bidirectional visibility leaked teacher-forced future image codes under a token-AR objective. Only fully observed image context is bidirectional; generated spans remain causal. |
| mLSTM specialization | Defect | State unrolling matched gated linear attention, but the readout equivalence dropped `max(|z^Tq|,1)`. The proposition and value coefficients retain it. |
| Resampler hull / Exercise 20.1 | Defect | A projector was compared with the raw-value hull while the resampler theorem concerns projected values. The comparison now uses one space and makes no false expressivity separation. |
| `prop-perplexity-kl` | Defect | The sequence entropy/KL equation dropped `1/T`. |
| `prop-recall-accuracy` | Defect | Strict pairwise probability omitted AUROC's half-credit for ties. |
| Connector bottleneck prose | Defect | `m<n` continuous tokens were said to force information loss; token count alone gives no continuous capacity bound. |
| Selective recurrence cost | Defect | Generic dense transitions were assigned diagonal/structured `O(n d_s)` cost. |
| `rem-body-unchanged` | Defect | An unmasked UAT was transferred to causal/mixed masks; a causal first row cannot approximate a future-dependent target. The remark now claims shared block ingredients, not an unchanged function class. |
| `prop-resampler-cost` | Gap | Query/output/FFN `m d^2` work was missing unless `m=O(n)`. |
| Connector DPI | Gap | Random text context supplied a second path from image to output. The result is now conditional on fixed context / a conditional Markov chain. |
| Exercise 20.2 | Gap | “Generic” weights did not exhibit the requested counterexample; explicit scalar parameters now do. |
| `prop-vq-gradient` | Gap | Arbitrary reconstruction loss/decoder did not justify differentiation. |
| Exercise 21.4 | Gap | The centroid and positive-definite Hessian claims omitted the empty-cell case. |
| Retrieval definitions | Gap | Nonempty query set, deterministic rank ties, and `B≥2` were missing. |
| Perplexity minimizer | Gap | Equality with the true conditional assumed realizability; restricted families yield a best-in-family KL projection. |

## Terminal diff-review additions — 3

Three read-only reviewers cross-checked partitions they had not authored. Each
item below received at least two independent uphold judgments before correction.
These additions are reported separately so the frozen Stage-D count above
remains reproducible rather than being silently rewritten after the fact.

| ID / location | Class | Verified failure and correction |
|---|---|---|
| `def-resampler`, `prop-resampler-convex` | Integration defect | Repairing the shared cross-attention definition exposed a dropped output projection in the connector chapter. The resampler now includes typed `W^O`, takes its hull after `W^V W^O`, and scopes convexity to the single attention layer rather than a deep residual/FFN stack. |
| `prop-decode-state` | Gap | The hybrid definition permits full causal attention, but the constant-state formula used `2wd` universally. The proposition now explicitly assumes all attention blocks use a fixed sliding window; the existing full-attention comparison remains linear in `n`. |
| `thm-online-softmax-exact` I/O clause | Gap | The proof tiles `Theta(M/d)` width-`d` query rows, which is not a realizable positive-size tile for `M=o(d)`. The traffic claim now states the load-bearing `M=Omega(d)` capacity hypothesis. |

The same review found four assurance/presentation defects, also corrected: the
global-Lebesgue-`L^p` property guard used a measure-zero two-point witness; the
coverage checker accepted IDs present only in module prose or unused tuples;
one proof used bold emphasis but no autonomous logical label; and the print
transform nested a second wrapper around an already-grouped exercise. The new
positive-measure guard, seven additional executable tests, test-function
linkage check, proof label, and idempotent print transform close those holes.

## Rejected candidates

| Candidate | Votes | Disposition |
|---|---:|---|
| Exercise 1.4 must say every lookup table lacks a successor map | 1–1; tiebreak **REFUTE** | “In general” plus a collision counterexample correctly proves lack of a guarantee. A distinct finite table may admit an interpolating map; that does not refute the qualified source. |
| `prop-sequential-depth` omits reduction/softmax depth | 0–2 **REFUTE** | The theorem explicitly defines a matrix multiplication or position-wise map as one atomic stage and disclaims broader circuit lower bounds. |
| VQ Voronoi proof needs pairwise-distinct code vectors | 0–2 **REFUTE** | The mathematical codebook is already a set of `K` vectors, so its elements are distinct. An indexed implementation that permits duplicate rows is a different model. |

## Structural and formal-style corrections

- `prop-params`, the sole frozen result without an adjacent proof, now has one;
  the result count is unchanged and the post-fix proof-block count is 104.
- Thirty-one proof blocks that had no autonomous bold logical label now contain
  `**Proof.**` or a more specific bold step label; all 104 post-fix proof blocks
  contain at least one such label.
- Nine learning-objective lead verbs and two exercise tags were normalized to
  the formal-style controlled vocabulary.
- Stale `last_verified` dates in chapters 03, 04, and 20 were advanced to the
  audit date.
- The print transform now groups all 133 exercise prompts with their collapsed
  solution rows, and figures are atomic print units. The oversized hybrid-stack
  figure is scaled locally so its caption remains on the same page.

## Pre-seeded non-regression

All six groups from the active plan passed independently: normalized versus
unconstrained contrastive alignment; the encoder/cross-attention taxonomy and
figure caption; the modality-tag probability factor; countably infinite
categoricals; semantic (not hard-coded chapter-number) references in evaluation;
and the autoregressive factorization hosted before first use.

## Report-only improvements

The disposition contract leaves non-load-bearing strengthening opportunities
out of the fix diff. Recorded examples: strengthen the positional-encoding
collision discussion toward global injectivity; narrow “arbitrary summaries”
in the HiPPO intuition; say encoder rows “can depend” rather than implying they
always do; state when a scaling maximizer has unique positive magnitude;
clarify label smoothing's finite-logit endpoint; make AUROC sampling
independence explicit; distinguish ideal roofline bounds from achieved time;
state the hybrid-state normalizer/steady cap exactly; add a step-size condition
before calling every delta update descent; sharpen chunk asymptotic language;
and distinguish the mathematical VQ set from an implementation parameter table.

## Post-fix executable and print acceptance

No baseline result is reused as post-fix evidence.

- Property tests: **138/138 pass**, including 38 new audit guards across the
  foundations, optimization, and multimodal partitions.
- Property-coverage manifest: **92 guarded claims**, expanded from 46, with the
  generated manifest check clean.
- Corpus / semantic-ID checks: **24 chapters, 310 labels**, plus 109 learning
  objectives, 756 cross-references, 223 registry references, 133 exercises
  (137 occurrences), and 31 figures; the migration self-test also passes.
- Content validation and production build: **24 chapters valid; 32 pages
  built; 21,088 words indexed**.
- Rendered KaTeX errors: **0 files** containing error markup.
- Browser layout: **25 representative routes** have no horizontal overflow at
  a 375 px viewport.
- Full print PDF and pagination inspection: **323 pages, 5,160,856 bytes**.
  All 133 prompt/solution pairs are structurally grouped; no PDF page begins
  with a stranded Solution row; every sub-45-word page is an intentional part
  title; and the hybrid figure and caption occupy page 263 together.
- Pull-request CI: **PR #24 passed the required `build`, `validate`, and
  `properties` checks before squash merge.**
