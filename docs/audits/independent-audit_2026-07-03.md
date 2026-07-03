# Independent Audit — Full-Guide Sweeps (2026-07-01 → 2026-07-03)

Adversarial multi-model audit of all 14 chapters (00–13) of the transformers
guide. Every confirmed finding below survived a 2-vote adversarial
verification; the mathematical subset additionally carries a unanimous
3-vendor (Anthropic / OpenAI / Google) consensus. **All confirmed findings
were fixed in the accompanying PR** — content bugs by correction, notation
collisions by correction or an explicit stated-departure note (the house
convention).

## Methodology

**Sweeps (3 lenses × 14 chapters = 42 finders).**
- *numerics* — every numeric claim recomputed with python; each exercise's
  solution checked against its stated prompt.
- *xref-cite* — every `<XRef>` checked for pointing at the *right* result
  (resolution is machine-checked; sense is not); every `<Cite>` checked
  against `bibliography.bib` for correct attribution.
- *style* — conformance to `00-notation.mdx` conventions, the pinned
  style-guide-formal-v0.1 contract, the dual-footing thesis, and
  figure↔prose agreement.

**Verification (adversarial, 2-vote).** Each candidate was attacked by two
independent refuter agents instructed to refute with quoted evidence
(numerics recomputed); split votes went to a tiebreaker. Kill rule: both
refute → dead; both uphold → CONFIRMED; split → tiebreaker decides.

**Model roster** (user-decided): finders Fable 5/max effort; verification
chapters 00–03 Fable 5/max, 04–11 Sonnet 5/max (quota fallback), remainder
Sonnet 5/high with Fable 5/max tiebreakers — cross-model verification of
same-model findings. External leg: the 44 numerics-lens confirmed findings
were independently re-audited by **codex (high reasoning): 44/44 AGREE** and
**Gemini: 44/44 AGREE** — unanimous 3-vendor consensus, no downgrades.

**Coverage.** 42/42 finders completed; 223 candidates; every candidate
adjudicated (0 unresolved). Raw verdicts: 174 confirmed, 49 refuted.
Cross-lens dedup (same file:line found under two lenses) → **135 unique
confirmed findings**. Verification consumed ~34M subagent tokens across six
workflow passes (three interrupted by quota limits and resumed from cache).

**Out of scope** (explicitly deselected): a proof-correctness sweep
re-deriving all 52 written proofs. The 13 genuinely-new proofs of chapters
10–13 carry a prior codex audit (see
`docs/plans/implemented/vlm-extension_2026-06-28.md`). Note: the numerics
lens nonetheless surfaced two proof-level defects (thm-variance-preservation's
hypothesis, the gradient-highway ordering) — a full proof sweep remains
worthwhile future work.

## Tally

| | count |
|---|---|
| Candidates found | 223 |
| Refuted by verification | 49 |
| Confirmed (unique, post-dedup) | **135** |
| — content severity (numerics + xref-cite) | 83 |
| — style severity | 52 |
| External 3-vendor consensus on math-critical | 44/44 AGREE ×2 |

## Headline findings (a selection)

1. **`00-notation.mdx:62` — the causal mask `M` was never defined anywhere.**
   The standing-operators table promised it in the Attention chapter; ch02
   contained only a figure caption; ch05/ch12 cited the unmasked attention
   definition for it. Fix: new `def-tf2-causal-mask` in ch02; retargeted refs.
2. **`02-attention.mdx:105` — variance-preservation theorem's hypotheses did
   not imply its conclusion** (q=(a,b), k=(b,a) Rademacher satisfies every
   stated hypothesis with Var⟨q,k⟩=4≠2). Fix: mutual independence across all
   2d_k components, and the proof step now names where it is used.
3. **`08-training-optimizations.mdx:107` — mixed-precision block stated as
   20N when its own terms sum to 16N**, propagating into the narrative, the
   ZeRO worked example (980 GB), and two exercises. Fixed throughout.
4. **`09-inference-optimizations.mdx:197` — FlashAttention HBM bound off by a
   factor of d** (Θ(n²d/M) vs the proof's own factors and Dao et al.'s
   Θ(n²d²/M)). Fixed in theorem, proof, and remark.
5. **`02-attention.mdx:52` — a second, duplicate numbered definition of
   softmax** violating the notation chapter's single-source contract. Fix:
   ch02 restructured to invoke ch00's canonical blocks.
6. **`01-input-representations.mdx:334` — ViT ablation direction inverted**
   (2D positional encodings reported "marginally better"; the cited paper
   reports no significant gain, marginally *worse*). Fixed.
7. **`13-multimodal-evaluation.mdx:80` — perplexity called a proper scoring
   rule minimized in expectation by the truth**; E[PPL] is minimized at
   q ∝ p^{T/(T+1)}. Restated for the log-loss with the exp/expectation order
   made explicit (prop, proof, and exercise).

## All confirmed findings

Severity `content` = wrong mathematics, numbers, targets, or attributions;
`style` = confirmed contract violations (notation, typography, structure).
Every row was fixed in the accompanying PR.

| # | Location | Lens | Sev | Finding |
|---|---|---|---|---|
| 1 | `00-notation:51` | xref-cite | content | The single-source contract 'Each is defined once, in the chapter named' (and line 31's 'fixed here once, and later chapters invoke it by name') is false for softmax: chapter 02 … |
| 2 | `00-notation:62` | xref-cite | content | The standing-operator table row for the causal mask matrix M points to the Attention chapter, but no chapter in the guide ever defines a causal mask matrix M — chapter 02's only… |
| 3 | `00-notation:110` | style | style | The chapter declares a row-vector convention ('unless stated otherwise') but the softmax-Jacobian section, exercise solutions, and the row-stochastic definition silently use col… |
| 4 | `00-notation:136` | numerics | content | Temperature remark asserts the tau->0+ limit of softmax(z/tau) is 'the one-hot vector at argmax_i z_i' without a unique-maximizer hypothesis; the claim is false whenever the max… |
| 5 | `00-notation:208` | style | style | The closing prose writes attention as a one-argument operator on a vector, $\operatorname{Attn}(\mathbf x)$, bypassing the chapter's own operator table which fixes the signature… |
| 6 | `01-input-representations:115` | style | style | The dual-embedding figure labels the raw embedding output as X ('the core sees only this') and omits the positional-encoding stage, contradicting the chapter's own notation wher… |
| 7 | `01-input-representations:263` | style | style | def-tf1-rope reuses the standing dimension n (fixed guide-wide by ch00 as sequence length, and used as sequence length earlier in this chapter at lines 63 and 73) as the key's p… |
| 8 | `01-input-representations:265` | style | style | def-tf1-rope silently switches to a column-vector convention — Theta(m)q left-multiplication and f(q,m)^T f(k,n) are only well-formed for column vectors — against ch00's 'vector… |
| 9 | `01-input-representations:271` | style | style | The new operator Theta(t) — registered in frontmatter notation_introduced — is defined inside def-tf1-rope with a plain '=' instead of \defeq, breaking the \defeq discipline tha… |
| 10 | `01-input-representations:309` | xref-cite | content | The sidenote renders a chronological inversion: 'RoPE was introduced by Su et al. (2024); its use in a large open model is documented in Touvron et al. (2023)' — the introductio… |
| 11 | `01-input-representations:317` | xref-cite | content | Remark rem-tf1-modality-blind is cross-referenced by chapters 10 and 12 as the source of a numbered interface taxonomy ('Interfaces (1) and (3)'), but the remark contains no num… |
| 12 | `01-input-representations:322` | style | style | ALiBi is presented as a named scheme with its formula and an extrapolation claim but carries no <Cite> to a primary source, and the bibliography contains no ALiBi entry at all —… |
| 13 | `01-input-representations:324` | numerics | content | The prose announces a summary of 'the four schemes' but the table that immediately follows contains five data rows (Sinusoidal PE, RoPE, Learned PE, ALiBi, Learned 2D PE). *(also style)* |
| 14 | `01-input-representations:334` | numerics | content | The chapter claims the ViT paper found 2D-aware positional encodings 'only marginally better' than the learned 1D table, but the cited study reports no gain from 2D-aware encodi… *(also xref-cite)* |
| 15 | `02-attention:8` | style | style | Frontmatter declares 'prerequisites: []' — the only content chapter besides ch00 itself with no prerequisites, while every sibling (01, 03–13) lists at least [notation] — and 'n… |
| 16 | `02-attention:44` | style | style | The chapter carries its own '## Notation' section (lines 30–46) re-declaring ch00's standing dimension and operator tables — the only chapter in the guide to do so — and its sof… |
| 17 | `02-attention:52` | style | style | The chapter re-issues a second numbered Definition of softmax (id def-tf2-softmax) and a second Translation-invariance proposition (prop-softmax-translation, line 60), duplicati… |
| 18 | `02-attention:87` | style | style | The chapter's headline structural claim — each attention output is a convex combination of the value rows — is asserted citing only the local softmax definition, bypassing ch00'… |
| 19 | `02-attention:91` | xref-cite | content | Figure 2.1 (fig-causal-mask) depicts causal/masked self-attention as if defined here, but def-tf2-attention (the definition it sits under, and the target of three chapter-12 XRe… *(also style)* |
| 20 | `02-attention:105` | numerics | content | Theorem thm-variance-preservation's stated hypotheses (per-vector independent components plus only same-index q_m ⊥ k_m) do not imply the claimed Var(⟨q,k⟩)=d_k; the proof's cro… *(also style)* |
| 21 | `02-attention:135` | style | style | Exercise 2.1 applies the matrix-level term 'row-stochastic' to a single row ('Each row … is row-stochastic'), conflicting with ch00's def-row-stochastic, which defines the prope… |
| 22 | `02-attention:147` | numerics | content | Exercise 2.2's solution states the softmax Jacobian diag(p) − pp^⊤ 'has entries p_i(1−p_i)', but that formula describes only the diagonal; off-diagonal entries are −p_i p_j, whi… *(also style)* |
| 23 | `03-multi-head-attention:31` | numerics | content | Chapter recap says all three projections (W^Q, W^K, W^V) map R^d -> R^{d_k}, but W^V maps to R^{d_v} per this chapter's own Definition (line 38) and chapter 2's convention. *(also style)* |
| 24 | `03-multi-head-attention:42` | xref-cite | content | Hard-coded cross-chapter reference '(Attention chapter, Def. 2)' points at the wrong number under the book's own numbering scheme: scaled dot-product attention renders as 'Defin… *(also style)* |
| 25 | `03-multi-head-attention:49` | xref-cite | content | The chapter's central construction, multi-head attention (Definition 3.2), carries no citation to its primary source Vaswani et al. (2017), whose bib entry (vaswani2017attention… |
| 26 | `03-multi-head-attention:83` | style | style | The known-object translation calls W_i^Q (W_i^K)^T a 'Gram-style product' and asserts 'the correspondence is exact' without stating where the analogy breaks, violating style-gui… |
| 27 | `03-multi-head-attention:107` | numerics | content | Claim that a single head with d_k = d is 'full-rank' and 'could in principle realize any one logit matrix' is false whenever n > d, contradicting the chapter's own theorem bound… *(also style)* |
| 28 | `03-multi-head-attention:120` | style | style | The defining equation of MQA inside a kind="definition" environment uses plain '=' instead of \defeq, breaking the ch00 \defeq discipline that the chapter's other definitions fo… |
| 29 | `04-transformer-block:8` | xref-cite | content | Frontmatter prerequisites [notation, attention] omit chapter 3 (slug multi-head-attention) even though the chapter uses \operatorname{MHA} in three definitions and relies on the… |
| 30 | `04-transformer-block:51` | style | style | The named remark presenting the published 'FFN as key-value memory' reading (Geva et al. 2021, 'Transformer Feed-Forward Layers Are Key-Value Memories'; lineage in Sukhbaatar et… |
| 31 | `04-transformer-block:52` | numerics | content | The key-value memory remark transposes both weight matrices: given def-tf4-ffn's shapes (W1 in R^{d x d_ff}, W2 in R^{d_ff x d}), the keys are the COLUMNS of W1 and the values a… *(also style)* |
| 32 | `04-transformer-block:62` | style | style | The symbol sigma_sig in the Swish definition is never defined anywhere in the guide (grep: this is its only occurrence), in a chapter that already uses bare sigma for the generi… |
| 33 | `04-transformer-block:130` | numerics | content | The gradient-highway product is written with ascending index bounds, prod_{i=l}^{L-1}(I + df_i/dx_i), which under the standard left-to-right product convention multiplies the Ja… *(also style)* |
| 34 | `04-transformer-block:156` | xref-cite | content | The all-skip gradient-immunity claim cites he2016deep (the CVPR ResNet architecture paper), but the gradient decomposition it paraphrases is from the uncited He et al. 'Identity… |
| 35 | `04-transformer-block:165` | style | style | The post-norm and pre-norm block definitions (the chapter's central objects) are typed on bold-lowercase x, y, z — which ch00 typography fixes as single vectors in R^d — yet fee… |
| 36 | `04-transformer-block:230` | numerics | content | Exercise 4.5 asks the reader to 'Exhibit a sublayer f and an input', but the solution exhibits only f and never names an input, nor notes that its linear choice of f makes the J… |
| 37 | `05-architecture-composition:54` | xref-cite | content | The ViT remark cites <XRef id="def-tf1-pe-2d" /> (axial 2D sinusoidal PE) as an ingredient and asserts the result 'is the Vision Transformer' of dosovitskiy2021vit, but the cite… |
| 38 | `05-architecture-composition:76` | style | style | The bridge sentence before the decoder-block definition says the decoder block is 'the encoder block plus two sublayers', which contradicts the three-sublayer definition it intr… |
| 39 | `05-architecture-composition:83` | xref-cite | content | The remark instantiates cross-attention with H_img as 'patch features from a Vision Transformer' and an ungated CrossAttn equation, then calls this 'the mechanism of gated cross… |
| 40 | `05-architecture-composition:126` | style | style | The same object is typeset two different ways 70 lines apart: rem-tf5-vit writes the math-mode $\texttt{[CLS]}$ slot (line 54) while rem-tf5-three-archs writes a Markdown code-s… |
| 41 | `05-architecture-composition:130` | xref-cite | content | The concatenation fusion route is described as projecting 'the image patch embeddings' into token space with the encoder absent, cited to liu2023llava — but LLaVA projects froze… |
| 42 | `05-architecture-composition:138` | xref-cite | content | thm-tf5-universal-approx claims approximation 'uniformly on K' and the sidenote attributes both statements to yun2020transformers, but Yun et al. (ICLR 2020) prove approximation… |
| 43 | `05-architecture-composition:139` | xref-cite | content | The sidenote attributes both universal-approximation statements about 'transformers' — which this book defines as pre-norm blocks with layer normalization (def-tf5-encoder) — to… |
| 44 | `05-architecture-composition:149` | xref-cite | content | The proof sketch assigns the quantize step to self-attention ('the route step, which also serves to quantize'), but in the cited yun2020transformers construction quantization of… |
| 45 | `05-architecture-composition:174` | style | style | prop-tf5-complexity mixes per-head and all-heads granularity in one table: the QK^T row is counted across all h heads as O(n^2 d), while the AV row uses ch00's per-head d_v as O… |
| 46 | `05-architecture-composition:200` | style | style | The linear-attention display in rem-tf5-linear-attention is well-formed only under a column-vector convention (phi(k_j) v_j^T as a DxD_v outer product), silently overriding ch00… |
| 47 | `05-architecture-composition:202` | xref-cite | content | The linear-attention remark claims the method of katharopoulos2020transformers 'gives up the softmax's non-negativity', but Katharopoulos et al. require non-negative similaritie… |
| 48 | `05-architecture-composition:230` | numerics | content | The forward-FLOPs example counts both FFN matmuls but credits self-attention with only the QK^T product, dropping the AV weight-value product (listed as a same-order block compo… *(also style)* |
| 49 | `06-training:10` | numerics | content | Frontmatter 'theorems' inventory lists 10 ids but the chapter defines 11 <Theorem id=...> boxes: def-tf6-xavier-init is missing. *(also style)* |
| 50 | `06-training:33` | style | style | The chapter introduces T for sequence length, conflicting with ch00's standing-dimension table, which fixes n = 'sequence length (number of tokens)' and promises 'These symbols … |
| 51 | `06-training:71` | style | style | The displayed identity E[L(θ)] = H(p_data) + KL(p_data ∥ p_θ) silently drops the 1/T factor from the definition of L (Def. 6.2 defines L as a 1/T average), and the proof's key s… |
| 52 | `06-training:133` | style | style | Symbol collision on 𝐲 within one chapter: lines 117 and 154 use 𝐲 for a target probability distribution ('any target distribution 𝐲', '𝐲 = 𝐞_{x_t}'), while the immediately prece… |
| 53 | `06-training:137` | xref-cite | content | The sentence attributes to 'Def. 2' (Definition 6.2, cross-entropy loss) a requirement it does not state: neither Def. 6.1 nor Def. 6.2 says the conditionals are 'supposed to be… |
| 54 | `06-training:151` | xref-cite | content | Second occurrence of the dangling 'Prop. 2' ordinal: the result invoked (loss keeps falling as q -> 1 / gradient nonzero until q is one-hot) renders as Proposition 6.4, not 'Pro… |
| 55 | `06-training:194` | xref-cite | content | Hardcoded prose reference 'Prop. 2' is dangling under the rendered numbering: the intended logit-gradient proposition renders as Proposition 6.4, and no proposition renders as '… |
| 56 | `06-training:213` | style | style | 'Warmup rationale' is typed kind="proposition" (and listed in frontmatter theorems) but contains no provable statement and no proof — only qualitative empirics ('can swing sharp… |
| 57 | `06-training:224` | numerics | content | Prose hard-codes per-kind theorem ordinals ('Prop. 4', 'Prop. 2', 'Def. 2') that do not exist under the chapter's rendered single-counter numbering, and 'Prop. 4' collides with … *(also style)* |
| 58 | `06-training:244` | numerics | content | Depth-scaled residual initialization (variance scaled by 1/(2N)) is attributed to the original transformer (Vaswani et al. 2017), but it is the GPT-2 initialization recipe (Radf… *(also style)* |
| 59 | `06-training:247` | style | style | The chapter's roadmap and closing disagree on its own contents: the opening 'Where we are' promises 'the three adjustments' (teacher forcing, label smoothing, warmup) and never … |
| 60 | `06-training:289` | numerics | content | Exercise 6.4's solution prints per-class NLLs, the standard CE, and their mean computed from 3-decimal rounded probabilities instead of the exact softmax, so several published i… |
| 61 | `07-detection-encoders:64` | xref-cite | content | def-tf7-encoder-classifier attributes the identity H(e_y, ŷ) = -log ŷ_y to prop-ce-kl, but that identity is the one-hot reduction stated in def-cross-entropy, not in the cited d… |
| 62 | `07-detection-encoders:81` | xref-cite | content | The Temperature margin note attributes the tau->0 sharpening / tau->infinity flattening limits to def-softmax, but the softmax definition contains no temperature at all; those l… |
| 63 | `07-detection-encoders:108` | xref-cite | content | Proof of prop-tf7-contrastive-ce cites prop-ce-kl (the CE = entropy + KL decomposition) for the one-hot reduction of cross-entropy, a fact stated only in def-cross-entropy (00-n… *(also style)* |
| 64 | `07-detection-encoders:115` | numerics | content | Body text falsely claims that adding a constant to a whole row of M (a per-anchor similarity offset) leaves "the loss" unchanged; this is true only for L_row, not for the symmet… |
| 65 | `07-detection-encoders:132` | xref-cite | content | rem-tf7-crossmodal-canonical cites def-tf6-ce-loss for 'the autoregressive head', but that target defines the cross-entropy loss; the autoregressive head (softmax over h_t W_out… |
| 66 | `07-detection-encoders:163` | style | style | def-tf7-auroc bolds "area under the ROC curve" as the definiendum but the ROC curve is never defined (nor the acronym expanded) anywhere in the guide, and LO TF-7.4's promise to… |
| 67 | `07-detection-encoders:192` | numerics | content | Exercise 7.1 asks why the designated-position representation "escapes" the convex hull of the contextual states {h_i}, but by def-tf7-pooled-rep r_CLS = h_1 is itself one of the… |
| 68 | `07-detection-encoders:208` | numerics | content | Exercise 7.3 asks the reader to conclude a false statement — that "the contrastive loss" (defined as the symmetric L_con) depends on the similarities only through the row gaps M… |
| 69 | `07-detection-encoders:220` | style | style | Subscript typography drifts between body and solutions: the same symbols are set with \textsf in the main text ($s_{\textsf{M}}$, $\mathbf r_{\textsf{CLS}}$) but \text in the So… |
| 70 | `07-detection-encoders:228` | numerics | content | Exercise 7.5's prompt says to "shift one inlier's score", but the solution changes three of the four inlier scores ({1,2,3,4} -> {1,1,1,12}) while self-describing the move as "r… |
| 71 | `08-training-optimizations:10` | xref-cite | content | The frontmatter theorems registry omits two of the chapter's nine def/prop/thm blocks — def-tf8-mixed-precision and def-tf8-zero — the latter being a result the chapter itself c… |
| 72 | `08-training-optimizations:33` | style | style | The chapter redefines $N$ as the model's parameter count and introduces $L$ for depth, directly conflicting with ch00's standing-dimensions table ('$N$ \| number of transformer … |
| 73 | `08-training-optimizations:75` | style | style | The activation remark calls L·n·d·b_a a 'coarse upper bound' and then, in the same sentence, concedes the true activation footprint is several-fold larger ('before the per-block… |
| 74 | `08-training-optimizations:91` | numerics | content | The bf16-vs-fp16 remark asserts all three tabulated formats 'store the same total bits', but the table's own rows give FP32 = 1+8+23 = 32 bits versus fp16 = bf16 = 16 bits. |
| 75 | `08-training-optimizations:107` | numerics | content | Proposition prop-tf8-mixed-precision states (4+2)N + 2N + 8N = 20N, but the terms sum to 16N; the proof (line 121, '6N + 2N + 8N = 20N') and the narrative (line 124, 'moves the … *(also style)* |
| 76 | `08-training-optimizations:136` | style | style | The self-explanation margin prompt inverts the checkpointing variable: storing every K-th of L activations keeps about L/K checkpoints, not K, whereas the theorem it prepares (l… |
| 77 | `08-training-optimizations:139` | xref-cite | content | The impossibility claim 'No schedule using o(L) stored activations can avoid the extra forward pass' is cited to chen2016training, a constructive upper-bound paper that contains… |
| 78 | `08-training-optimizations:150` | numerics | content | The post-theorem narrative claims an L = 64 checkpointing example drops activation memory 'a factor of eight', but the theorem just proved peak memory Theta(K + L/K) = 8 + 8 = 1… *(also style)* |
| 79 | `08-training-optimizations:168` | numerics | content | The LoRA margin note applies the 2r/d = 1/128 reduction to a whole 70B model ('becomes ~0.5B trainable'), silently assuming every parameter matrix is adapted, while the chapter'… *(also style)* |
| 80 | `08-training-optimizations:232` | numerics | content | The ZeRO worked example (and Exercise 8.5's solution at line 286) computes the mixed-precision master-copy block as (4+2+8)N = 14N = 980 GB, contradicting the chapter's own mixe… *(also style)* |
| 81 | `08-training-optimizations:262` | numerics | content | Exercise 8.2's solution inherits the false 20N total, giving 140 GB and 1.75x an 80 GB accelerator where the proposition's own terms (6N + 2N + 8N = 16N) give 112 GB and 1.4x. |
| 82 | `08-training-optimizations:270` | numerics | content | Exercise 8.3's solution claims a 10x activation-memory reduction for L = 100, but the peak-memory model g(K) = K + L/K it just minimized gives peak 2*sqrt(100) = 20 versus 100 u… |
| 83 | `09-inference-optimizations:35` | style | style | The chapter bypasses two family/ch00 macros: it is the only chapter in the guide spelling \operatorname{softmax} (5 occurrences; ch00 and all other chapters use the \softmax mac… |
| 84 | `09-inference-optimizations:62` | numerics | content | The memory-bound proof names the wrong algebraic operation: 'divide both sides by β' applied to I < I* (i.e., Φ/β < F/𝓑) does not produce the displayed inequality Φ/(βF) < 1/𝓑 —… *(also style)* |
| 85 | `09-inference-optimizations:74` | numerics | content | The prefill arithmetic-intensity claim I ≈ n counts only the O(d²) weight bytes; with the unavoidable activation reads/writes (2nd elements) the intensity is 2nd²/(b(2nd+d²)), w… |
| 86 | `09-inference-optimizations:88` | style | style | prop-tf9-kv-memory writes the transformer layer count as L, bypassing chapter 00's standing-dimension table which fixes N as 'number of transformer layers (blocks)' — ch05 stack… |
| 87 | `09-inference-optimizations:110` | numerics | content | The uncached-step proof asserts the score cost Θ(t²d) dominates the K/V-regeneration cost Θ(td²) unconditionally, but for t < d the regeneration term dominates, so the propositi… *(also style)* |
| 88 | `09-inference-optimizations:145` | numerics | content | Margin note claims INT8's step size s is 'four times smaller' than INT4's over a fixed range; the true factor is (2^8−1)/(2^4−1) = 17 (≈16), consistent with the chapter's own ha… |
| 89 | `09-inference-optimizations:197` | numerics | content | FlashAttention HBM-traffic bound stated as Θ(n²d/M) is off by a factor of d: the proof's own factors multiply to Θ(n²d²/M), which is also the bound in Dao et al. (Theorem 2: Θ(N… *(also style)* |
| 90 | `09-inference-optimizations:220` | style | style | FlashAttention IO count is internally inconsistent: the proof's own factors — Θ(nd/M) query blocks times Θ(nd) bytes per block — multiply to Θ(n²d²/M), yet the stated total (and… |
| 91 | `10-connectors-resamplers:8` | xref-cite | content | The frontmatter prerequisites omit inference-optimizations (chapter 9) and training-optimizations (chapter 8) even though prop-tf10-resampler-cost's statement and proof are buil… *(also style)* |
| 92 | `10-connectors-resamplers:54` | xref-cite | content | The margin note asserts a numbered interface taxonomy 'again' — Interface (1) = embedding, Interface (3) = read-out/cross-modal — but no prior chapter establishes any numbered i… |
| 93 | `10-connectors-resamplers:67` | xref-cite | content | The LLaVA-1.5 two-layer MLP connector is cited to the original LLaVA paper (liu2023llava = 'Visual Instruction Tuning', arXiv 2304.08485), which used a single linear projection;… |
| 94 | `10-connectors-resamplers:79` | style | style | The chapter introduces the operator \operatorname{CA} (used 5 times, including in def-tf10-gated-xattn and both figure-adjacent proofs) while pointing the reader to def-tf5-cros… |
| 95 | `10-connectors-resamplers:83` | style | style | The chapter writes attention projections with subscripts (\mathbf W_Q, \mathbf W_K, \mathbf W_V; 15+ occurrences including exercises) whereas every other chapter that names thes… |
| 96 | `10-connectors-resamplers:115` | numerics | content | The resampler-cost proof claims the Θ(mnd) score+readout is 'the dominant cost' per layer, but the omitted key/value projections V·W_K, V·W_V cost Θ(n·d_vis·d_k) ≈ Θ(n d²) per l… |
| 97 | `10-connectors-resamplers:123` | xref-cite | content | def-tf10-mutual-information grounds H in def-entropy, but the target defines entropy only for a finite discrete distribution vector — it defines neither the entropy of a general… *(also style)* |
| 98 | `10-connectors-resamplers:207` | numerics | content | Exercise 10.2's solution exhibits a permutation (equal contents v1=v2, positions swapped between slots 1 and 2) that provably does NOT change any output row, so the solution fai… |
| 99 | `11-discrete-visual-tokenization:8` | xref-cite | content | Frontmatter prerequisites omit connectors-resamplers (chapter 10) even though the rate proposition and its proof both rest on <XRef id="prop-tf10-bottleneck" /> (lines 192, 196)… |
| 100 | `11-discrete-visual-tokenization:9` | style | style | The frontmatter notation_introduced omits two symbols this chapter actually introduces: the stop-gradient operator \sg (the chapter's headline new operator, a new KaTeX macro ad… |
| 101 | `11-discrete-visual-tokenization:41` | style | style | The chapter uses $\mathbf e_1,\dots,\mathbf e_K$ for learned codebook vectors, directly conflicting with ch00's standing convention that $\mathbf e_k$ is the k-th standard basis… |
| 102 | `11-discrete-visual-tokenization:43` | style | style | The chapter's three definitional displays — the quantizer $q(\mathbf z) = \mathbf e_{k^\star(\mathbf z)}$ (line 43), the STE $\mathbf z_q = \mathbf z_e + \sg[\cdot]$ (line 86), … |
| 103 | `11-discrete-visual-tokenization:47` | style | style | The term 'codebook' is formally defined twice in the guide as different objects — ch01 def-tf1-codebook-embedding: 'A **codebook** is a matrix $\mathbf C\in\R^{K\times d}$'; ch1… |
| 104 | `11-discrete-visual-tokenization:54` | style | style | The fig-grid-sequence caption narrates three pipeline stages ('From image to sequence. The encoder compresses an image to an L-cell latent grid; each cell is quantized...') but … |
| 105 | `11-discrete-visual-tokenization:170` | style | style | The headline theorem's displayed equation uses the logit vector $\mathbf o_t$, a symbol defined nowhere in this chapter, in ch00, or in the ch06 definition it cites (which write… |
| 106 | `11-discrete-visual-tokenization:172` | style | style | The chapter writes the KL divergence as $\mathrm{KL}(p_{\mathrm{data}}\Vert p_\theta)$ (three occurrences: lines 172, 176, 239), bypassing the operator symbol $D_{\mathrm{KL}}(\… |
| 107 | `11-discrete-visual-tokenization:176` | xref-cite | content | The proof of the headline dual-footing theorem states 'the identity that per-token cross-entropy equals the KL from the data to the model plus the data entropy' citing prop-tf6-… |
| 108 | `11-discrete-visual-tokenization:180` | xref-cite | content | The remark claims 'the same recipe' (the chapter's VQ codebook + STE + k-means codec) underlies DALL-E, but ramesh2021dalle's discrete VAE is trained with the Gumbel-softmax rel… |
| 109 | `11-discrete-visual-tokenization:192` | xref-cite | content | The equality condition 'with equality iff the codes are independent and uniformly distributed' cites def-entropy, which defines only single-variable entropy with max log K at th… |
| 110 | `11-discrete-visual-tokenization:196` | numerics | content | The rate proposition's proof claims the quantization residual's expected squared norm lower-bounds the achievable reconstruction error, which is false: the residual is a latent-… |
| 111 | `11-discrete-visual-tokenization:239` | numerics | content | Exercise 11.5(b)'s solution states the empirical per-token cross-entropy of a code sequence 'equals' the KL from data to model plus the data entropy, but the cited proposition (… *(also xref-cite)* |
| 112 | `12-unified-multimodal-models:34` | style | style | The chapter's organizing claim that modality survives 'only at the two ends' is contradicted by its own mixed block-causal mask section and capstone remark ('What differs is onl… |
| 113 | `12-unified-multimodal-models:45` | xref-cite | content | The sidenote lists Emu (sun2023emu) and Transfusion (zhou2024transfusion) among 'early-fusion unified models of this form', where 'this form' is def-tf12-interleaved's chain-rul… |
| 114 | `12-unified-multimodal-models:55` | style | style | The defining display of def-tf12-modality-embedding bypasses ch00/ch01 conventions three ways: the hat on x̂_t includes the position code, although ch00/ch01 reserve the hat for… |
| 115 | `12-unified-multimodal-models:61` | style | style | def-tf12-routed-heads routes by 'the *predicted next modality*' and conditions on c_{t+1}, but no modality-prediction factor p(c_{t+1} \| u_{\le t}) is ever defined, so the join… |
| 116 | `12-unified-multimodal-models:70` | style | style | The unified-decoder figure caption locates the embedding at the 'bottom' and the routed head at the 'top', but the rendered figure (figures/unified-decoder.tex and public/figure… |
| 117 | `12-unified-multimodal-models:75` | numerics | content | The margin note asserts embedding and head 'are Interfaces (1) and (3) of rem-tf1-modality-blind', but the cited remark contains no numbered interface enumeration, and no chapte… *(also xref-cite)* |
| 118 | `12-unified-multimodal-models:94` | numerics | content | The any-to-any proof claims image-to-text, text-to-image, and interleaved generation are 'the three choices of (prefix modality, suffix modality)', but two modalities give four … |
| 119 | `12-unified-multimodal-models:132` | numerics | content | The mixed block-causal mask definition equates 'every segment is a single text token' with 'the all-text case', but under its own segmentation (maximal same-modality spans, line… *(also xref-cite)* |
| 120 | `12-unified-multimodal-models:150` | xref-cite | content | rem-tf12-body-unchanged cites def-tf5-decoder-block (the three-sublayer encoder-decoder block WITH a cross-attention sublayer) as 'the same blocks' of the unified model's body a… |
| 121 | `12-unified-multimodal-models:157` | numerics | content | Exercise 12.1's prompt asks to 'identify which is the only modality-dependent component' (presupposing exactly one), but its own solution identifies two components — the image e… |
| 122 | `12-unified-multimodal-models:189` | numerics | content | Exercise 12.5 (and the definition at line 132) asks to prove reduction to 'the causal mask of def-tf2-attention', but def-tf2-attention defines unmasked scaled dot-product atten… |
| 123 | `13-multimodal-evaluation:8` | xref-cite | content | The frontmatter prerequisites are inconsistent with the chapter's actual cross-reference graph: the load-bearing XRef to rem-tf1-modality-blind targets 01-input-representations.… |
| 124 | `13-multimodal-evaluation:39` | style | style | Standing-dimension symbols from ch00's table — N ('number of transformer layers') and c ('channel count'), which ch00 says 'keep their meaning throughout the guide' — are silent… |
| 125 | `13-multimodal-evaluation:41` | style | style | Every definitional display in the chapter (recall@k/MRR line 41, PPL line 74, the zero-shot classifier lines 98–100) uses plain '=' instead of \defeq — chapter 13 is the only ch… |
| 126 | `13-multimodal-evaluation:58` | numerics | content | Clause 2 of prop-tf13-recall-accuracy equates the within-query pairwise hit probability Pr[M_ii > M_ij] with the pooled Mann–Whitney AUROC over positives {M_ii} and negatives {M… *(also xref-cite)* |
| 127 | `13-multimodal-evaluation:65` | xref-cite | content | The margin note asserts in-batch contrastive accuracy, recall@1, and 'the top of the ROC curve' are 'the same number read three ways', but by the chapter's own proposition the R… *(also style)* |
| 128 | `13-multimodal-evaluation:76` | style | style | The symbol H-hat silently renames ch06's loss — def-tf6-ce-loss defines '\mathcal L(\theta) \defeq ...', not \widehat H — and \widehat H is introduced here without being declare… |
| 129 | `13-multimodal-evaluation:80` | numerics | content | Proposition prop-tf13-perplexity-kl falsely claims perplexity is a proper scoring rule uniquely minimized in expectation by the true conditional distribution; expected perplexit… *(also xref-cite)* |
| 130 | `13-multimodal-evaluation:84` | style | style | The chapter bypasses ch00/family operator forms: it writes \mathrm{KL}(p \|\| p) where ch00's def-kl and the very proposition cited in the same sentence (prop-tf6-ce-kl-training… |
| 131 | `13-multimodal-evaluation:96` | style | style | def-tf13-zeroshot never states the L2-normalization hypothesis that its correctness proof and figure both rely on: t_c is built by def-tf7-pooled-rep (CLS/mean pooling, no norma… |
| 132 | `13-multimodal-evaluation:113` | xref-cite | content | Proposition prop-tf13-zeroshot-classifier cites prop-tf7-contrastive-alignment as proving that images align with class-name prompt embeddings, but the cited proposition only con… |
| 133 | `13-multimodal-evaluation:117` | numerics | content | The proof of prop-tf13-zeroshot-classifier claims softmax(o/tau) is 'exactly' the output of the encoder classifier def-tf7-encoder-classifier with head W_cls=[t_1,...,t_C], but … *(also xref-cite)* |
| 134 | `13-multimodal-evaluation:121` | xref-cite | content | The priority claim 'the retrieval-as-ranking view goes back to image-caption alignment' is pinned on karpathy2015deepvisual, but framing image-caption evaluation as a ranking ta… |
| 135 | `13-multimodal-evaluation:144` | numerics | content | Exercise 13.3 asks to prove a false statement (expected perplexity minimized exactly at the true conditional), and its solution does not prove the stated prompt — it derives the… |

## Refuted candidates

49 candidates were killed by adversarial verification (both refuters, or the
tiebreaker, refuted with quoted evidence). Representative refutations: the
post-tombstone stable-softmax remark in ch00 (a deliberate house pattern used
consistently across chapters), and several style candidates that misread the
pinned v0.1 style-guide principles. Full per-candidate vote transcripts are in
the workflow journal (session artifacts), not in the repo.

## Reviewer-of-record note

Fixes were authored sequentially in the main loop (Fable 5/max) to keep
cross-chapter clusters coherent (the mask-M cluster spans ch00/02/05/12; the
Interface taxonomy spans ch01/10/12). The fix diff itself received a 3-voice
adversarial review before merge; CI (`content-validate`, `astro-build`) gates
the PR. Local gate at fix time: `npm run validate` clean, `npm run build`
green, 0 `katex-error` occurrences in rendered HTML.
