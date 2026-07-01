# Extend the Transformers Guide to Vision-Language Models (Dual-Footing)

## Context

The guide `mathematical-guides-transformers` is a formal (Definition–Theorem–Proof)
treatment of transformers, currently 10 chapters (`00`–`09`) + a solutions appendix (`99`),
covering text LLMs end to end. The goal is to extend it to **Vision-Language Models** —
comprehensively (ViT, fusion/connectors, VL training, discrete tokenization, unified
generative models, evaluation) — but **without siloing VLMs as a separate subject**.

The governing decision (from the user): treat VLMs and text LLMs on a **dual footing**.
Demonstrate the genuinely-unique vision elements rigorously, but where the mathematics is
shared, present *one* concept with two modalities as instances — not a parallel "vision track."

### The dual-footing thesis (the organizing principle for everything below)

A transformer is a **modality-agnostic map on sequences in $\R^{n\times d}$**. Modality is
confined to exactly three interfaces:

1. **Embedding boundary** — raw input → $\hat{\mathbf X}\in\R^{n\times d}$. Text = token
   lookup $\mathbf e_x^\top\mathbf E$; image = patch projection
   $\operatorname{vec}(\mathbf u)^\top\mathbf W_{\text{patch}}$; discrete visual = codebook
   lookup $\mathbf e_z^\top\mathbf C$ (algebraically identical to text).
2. **Positional structure** — 1D index generalized to a 2D grid $(a,b)$, same equivariance.
3. **Read-out / cross-modal coupling** — autoregressive head, contrastive head,
   cross-attention. **All already general in the guide.**

Everything between (attention, MHA, FFN, LayerNorm, residual, stacking, training loss,
optimization) is modality-blind. So: a **ViT** *is* "an encoder (Ch 5) over patch embeddings
(Ch 1)"; a **captioner** *is* "autoregressive LM (Ch 6) conditioned via cross-attention (Ch 5)
on visual embeddings (Ch 1)"; **CLIP** *is already* "two encoders + contrastive head (Ch 7)."
The genuinely **new** math is narrow: patch/2D embedding, vector quantization, the
resampler/connector, and modality routing.

### Intended outcome

A reader finishes understanding modern VLMs as transformers with three swapped interfaces —
not as a new architecture. The guide gains 4 new chapters and dual-footing reframes in 5
existing ones, all in the established formal style, fully cross-linked and building.

---

## Structure of the change

Two parts: **(A) weave** vision into existing chapters as a co-equal modality; **(B) add** four
chapters for the genuinely-unique material. Final chapter map (numbering in **bold** = new):

```
00 notation                      edit: modality-agnostic notation (Emb map, unit/stream)
01 input-representations         edit: KEYSTONE — embedding interface, patch + codebook
                                       embedding, 2D positions  (forces theorem renumber)
02 attention                     unchanged  (load-bearing: proves the core is modality-blind)
03 multi-head-attention          unchanged
04 transformer-block             unchanged
05 architecture-composition      edit: ViT=encoder, fusion=cross-attn, unified-sequence remarks
06 training                      edit: captioning = conditional AR loss (example, no new theory)
07 detection-encoders            edit: CLIP = canonical cross-modal alignment (headline + remark)
08 training-optimizations        unchanged
09 inference-optimizations       unchanged
**10 connectors-resamplers**         NEW — projector, learned-query resampler, Flamingo gating
**11 discrete-visual-tokenization**  NEW — codebook, STE, VQ loss, image-gen = AR LM
**12 unified-multimodal-models**     NEW — interleaved sequences, modality routing, mixed mask
**13 multimodal-evaluation**         NEW — retrieval/perplexity/zero-shot reduced to Ch6/Ch7
99 appendix-solutions            edit: +17 solutions, +4 prerequisite slugs
```

**Placement decision.** New chapters **append at 10–13, no renumbering**. Rationale:
they depend on Ch 6 (AR-LM loss) and Ch 7 (CLIP), so must follow them; the alternative
(insert after Ch 7, shift `08`/`09` up) would rewrite every `tf8`/`tf9` theorem/LO/solution ID
and every `<XRef>` to them (Ch 9 is heavily cross-referenced) for zero pedagogical gain.
The "vision belongs next to architecture" intent is met by the **weave** in Ch 1/Ch 5, not by
chapter position. Optimization chapters `08`/`09` are prerequisites the new chapters lean on
(KV-cache, MoE), so keeping them before `10`–`13` is correct.

---

## Part A — Woven integration into existing chapters

Edits are append-only remarks/examples **except Ch 1**, which inserts numbered Definitions/
Theorems and therefore renumbers. All `<XRef id=>` links are by id (stable); only printed
`n=` and prose "Definition N"/"Theorem N" change.

### A0. `00-notation.mdx` — modality-agnostic vocabulary
- New short subsection "Modality-agnostic conventions" after **Standing operators**.
- Standing-dimensions rows: $u_t$ (a **unit**: text token / image patch / code); $\mathcal U$
  (unit space); $p,c$ (patch side, channels); $s$ (modality/stream index, $\mathbf X^{(s)}$).
- Standing-operators row: $\Emb:\mathcal U\to\R^d$ (the embedding map, Interface 1). Edit the
  `\operatorname{PE}` row to note generalization to a grid index $(a,b)$.
- Frontmatter: `notation_introduced += \Emb, \mathcal U, u_t, (s), p, c`;
  `los += TF-0.4` (state the modality-agnostic embedding interface).

### A1. `01-input-representations.mdx` — THE KEYSTONE
Carries the most new math. Current numbered items end at Def 6 / Thm 3.

**Renumber map** (ids unchanged; only `n=`/prose bump):
Def vocabulary 1→1, token-embedding 2→2, **NEW** embedding-interface **3**, **NEW** patch-embedding
**4**, **NEW** codebook-embedding **5**, **NEW Thm** patch=conv **1**; sinusoidal-PE 3→6,
transformer-input 4→7, pe-rotation Thm 1→2, collision Thm 2→3, **NEW** axial-2D-PE def **8**,
**NEW Thm** 2D-shift **4**; rotation-2D 5→9, rope 6→10, rope-relative Thm 3→5. Prose refs to bump:
in `thm-tf1-pe-rotation` proof, `def-tf1-rope` body, the two RoPE remarks, exercises 2 & 5.
(Grep Ch 1 for literal "Definition 3/4/5/6" and "Theorem 1/2/3" to bound the edit.)

**New content, slotted after token-embedding close (line 49), before Sinusoidal PE (line 51):**
- **Def 3 Embedding interface** `def-tf1-embedding-interface`: a modality is $(\mathcal U,\Emb)$;
  $\hat{\mathbf X}=(\Emb(u_1);\dots;\Emb(u_n))$. Token embedding is the instance
  $\mathcal U=\mathcal V,\ \Emb(x)=\mathbf e_x^\top\mathbf E$.
- **Def 4 Patch embedding (ViT front-end)** `def-tf1-patch-embedding`: image
  $\R^{H\times W\times c}$ → $n=H_pW_p$ patches, $\Emb(\mathbf u_{ab})=\operatorname{vec}(\mathbf u_{ab})^\top\mathbf W_{\text{patch}}$,
  $\mathbf W_{\text{patch}}\in\R^{p^2c\times d}$. Cite `dosovitskiy2021vit`.
- **Def 5 Codebook embedding** `def-tf1-codebook-embedding`: $\Emb(z)=\mathbf C[z,:]$,
  **algebraically identical** to text lookup. Cite `vandenoord2017vqvae`.
- **Thm 1 Patch embedding is a strided convolution** `thm-tf1-patch-conv`: reshaping
  $\mathbf W_{\text{patch}}$ columns into a kernel $\mathbf K$, the ViT patch layer equals
  `Conv2d(c,d,kernel=p,stride=p)`. Proof: stride=kernel tiles into disjoint patches; output
  channel = Frobenius product = $\Emb(\mathbf u_{ab})_j$. *(Genuinely illuminating, fully
  rigorous; the "patchification is not new" payoff.)*
- Margin notes: "token lookup = patch projection on a one-hot input"; "patchification = the
  conv where stride = kernel." `<Figure src="/figures/dual-embedding.svg">`.

**New subsection "Two-dimensional positions", after collision discussion (line 146), before RoPE:**
- **Def 8 Axial (factorized) 2D sinusoidal PE** `def-tf1-pe-2d`:
  $\operatorname{PE}_{\text{2D}}(a,b)=(\operatorname{PE}(a),\operatorname{PE}(b))$, half-channels each.
- **Thm 4 Factorized 2D shift is a fixed block rotation** `thm-tf1-pe-2d-shift`: offset
  $(k,l)$ acts by block-diagonal orthogonal $\mathbf M_{k,l}=\operatorname{diag}(\mathbf M^{\text{row}}_k,\mathbf M^{\text{col}}_l)$;
  inner product depends only on $(k,l)$. Proof: apply 1D Thm 2 to each orthogonal half.
- **Remark Axial RoPE** `rem-tf1-rope-2d` (after rope-relative): row/column angle split; per-axis
  relative property; the scheme of modern multimodal transformers over patch grids.

**Capstone remark** `rem-tf1-modality-blind` (after RoPE remarks, before "Other positional
schemes"): once $\mathbf X=\hat{\mathbf X}+\mathbf P$ is formed it carries no record of modality;
every theorem in Ch 2–4, 8–9 is stated over $\R^{n\times d}$ and transfers verbatim. **States the
thesis where it first becomes true.**

**Other-schemes table:** append a "Learned 2D PE" row + one sentence (ViT used learned 1D).
**Exercises 6–8** (patch⊇token special case; $4\times4$ patch/kernel compute; derive Thm 4 from
Thm 2). Solutions → appendix `soln-tf1-ex6..8`.
**Frontmatter:** `notation_introduced += \Emb, \mathcal U, \mathbf W_{\text{patch}}, \mathbf C,
\operatorname{PE}_{\text{2D}}, (a,b)`; `theorems +=` the 8 new ids; `los += TF-1.5, TF-1.6`;
extend `description`.

### A2. `05-architecture-composition.mdx` — ViT and fusion as reuse (3 remarks, no new core)
- `rem-tf5-vit` (after encoder section, line 47): the ViT *is* `def-tf5-encoder` over
  `def-tf1-patch-embedding` + `def-tf1-pe-2d` + `[CLS]`; "not one line of the block, stack, or
  universal-approximation argument changes." Cite `dosovitskiy2021vit`.
- `rem-tf5-multimodal-crossattn` (after cross-attention convexity, line 68): VL fusion is
  `def-tf5-cross-attention` with the encoder stream taken to be vision; convexity
  (`prop-row-stochastic-convex`) ⇒ text "selects and averages" visual evidence, cannot fabricate.
  Cite `alayrac2022flamingo`.
- `rem-tf5-unified-sequence` (after `rem-tf5-three-archs`, line 111): the two fusion routes are
  the two settings of the cross-attention switch — cross-attend a separate image stream, **or**
  project patches into token space and concatenate into one decoder-only sequence
  (`def-tf5-decoder-only`). Cite `liu2023llava`.
- **Frontmatter:** `prerequisites += input-representations`; `theorems +=` 3 ids; `los += TF-5.5`.

### A3. `06-training.mdx` — captioning as conditional AR loss (1 example, no new theory)
- `ex-tf6-captioning` (after logit-gradient discussion, ~line 113): captioning factorizes
  $p_\theta(\mathbf y\mid\mathbf I)=\prod_t p_\theta(y_t\mid y_{<t},\mathbf c)$; the loss is the
  existing cross-entropy with the conditioning set enlarged from $y_{<t}$ to $(y_{<t},\mathbf c)$;
  KL identity, $\mathbf q-\mathbf y$ gradient, teacher forcing, label smoothing all transfer.
  Image enters via Interface 1 (prepended tokens) or Interface 3 (cross-attention). Cite
  `liu2023llava`, `alayrac2022flamingo`.
- **Frontmatter:** `theorems += ex-tf6-captioning`; `los += TF-6.5`.

### A4. `07-detection-encoders.mdx` — CLIP as canonical cross-modal alignment (reframe + 1 remark)
- Headline edit (contrastive-objective lead): promote "the same content in another modality
  (an image and its caption)" from parenthetical to the canonical positive-pair case.
- `rem-tf7-crossmodal-canonical` (after `rem-tf7-separation-geometry`): take the two contrastive
  views to be image vs caption embeddings; the symmetric InfoNCE is **exactly** CLIP; the shared
  embedding space is the dual-footing payoff powering zero-shot classification and the projection
  that injects visual tokens into the LM (forward-ref Ch 10/13). Cite `radford2021clip`.
- (Optional) SigLIP remark (sigmoid loss) if `zhai2023siglip` added.
- **Frontmatter:** `theorems += rem-tf7-crossmodal-canonical`; `los += TF-7.5`;
  optionally `prerequisites += input-representations`.

---

## Part B — New chapters 10–13

All follow house style: motivated D–T–P, intuition-first, first-person "we", inline structured
proofs, `<Cite>` to primary sources, `<MarginNote>`/`<Sidenote>`/`<Figure>`, exercises deferred to
`99`. Ids follow `def-tf<NN>-*` / `TF-<NN>.x` / `soln-tf<NN>-exM`. Each gets 2–4 figures.

### B1. `10-connectors-resamplers.mdx` — slug `connectors-resamplers`
*Prereqs:* notation, input-representations, attention, architecture-composition, detection-encoders.
The (often frozen) vision encoder → LLM bridge, treated as a distinct architectural pattern.
- **Def 10.1 Connector** $g_\phi:\R^{n\times d_{\text{vis}}}\to\R^{m\times d}$ producing soft visual
  tokens inserted into the LM sequence (Interface 1).
- **Def 10.2 Projector** (LLaVA): position-wise affine/MLP, $m=n$, no compression.
- **Def 10.3 Learned-query resampler** (Perceiver/Q-Former/Flamingo): cross-attention with
  **parameter** queries $\mathbf Q_{\text{lat}}\in\R^{m\times d}$ → fixed $m$ outputs.
- **Prop 10.1 Fixed length + convex hull**: $m$ rows ∀ $n$; each a convex combination of values
  (`prop-row-stochastic-convex`); permutation-invariant without positions. *(the $n\to m$ sense)*
- **Prop 10.2 Cost** $\Theta(L_r mn\,d)$ once; favorable vs projector when $N$ deep, $n\gg m$;
  shrinks KV-cache (`prop-tf9-kv-memory`).
- **Prop 10.3 Data-processing bound**: $X\!-\!\mathbf S\!-\!\hat Y$ Markov ⇒ $I(X;\hat Y)\le H(\mathbf S)$
  — the connector is an information bottleneck; with $m<n$ it must learn task-relevant compression.
- **Def 10.4 + Thm 10.1 Flamingo gated cross-attention**: $\tanh(\gamma)$ gates, $\gamma{=}0$ init ⇒
  inserted block is the **identity on the LM stream**, so $f_{\text{aug}}=f_{\text{LM}}$ at init;
  $\partial\mathcal L/\partial\theta=0$ but $\partial\mathcal L/\partial\gamma\ne0$ (gate unlocks
  the visual path). Analogy to LoRA zero-init (`def-tf8-lora`).
- *Sources:* liu2023llava(+15), alayrac2022flamingo, li2023blip2, jaegle2021perceiver,
  tishby1999information/2015deeplearning. *Figures:* resampler funnel; gated-xattn switch; (opt) context-cost.

### B2. `11-discrete-visual-tokenization.mdx` — slug `discrete-visual-tokenization`
*Prereqs:* notation, input-representations, architecture-composition, training.
Make an image a discrete sequence so Ch 6 applies **exactly**.
- **Def 11.1 Codebook + quantizer** $q(\mathbf z)=\arg\min_k\norm{\mathbf z-\mathbf e_k}$; image →
  index grid → length-$L$ sequence over $\{1,\dots,K\}$.
- **Prop 11.1 Voronoi projection**: $q$ = Euclidean projection onto $\mathcal C$; $\partial q/\partial\mathbf z=0$
  a.e. (the obstacle).
- **Def 11.2 + Thm 11.1 Straight-through estimator**: $\mathbf z_q=\mathbf z_e+\sg[q(\mathbf z_e)-\mathbf z_e]$;
  forward $=q(\mathbf z_e)$, backward Jacobian $=\mathbf I$ ⇒ reconstruction gradient copied to encoder.
- **Def 11.3 + Prop 11.2 VQ loss**: reconstruction + codebook + $\beta$·commitment (same squared
  distance, $\sg$ on opposite arguments); gradient split moves code vs encoder.
- **Thm 11.2 Codebook update = k-means step**: codebook-term minimizer is the Voronoi centroid;
  assign/centroid alternation is Lloyd's algorithm.
- **Thm 11.3 Dual-footing**: once VQ-tokenized, **image generation = autoregressive LM over a
  visual vocabulary** — Ch 6 factorization, softmax-over-$K$, CE=KL, teacher forcing all transfer
  with $|\mathcal V|=K$; modality enters only through the fixed codec $(\Phi,\Psi)$.
- **Prop 11.3 Rate/distortion**: $L\log_2 K$ bits; lossy codec sets a fidelity ceiling.
- *Sources:* vandenoord2017vqvae, razavi2019vqvae2, esser2021vqgan, ramesh2021dalle,
  bengio2013estimating. *Figures:* VQ pipeline w/ STE dashed-copy; Voronoi/k-means; (opt) grid→sequence.
- *New macro:* `\sg` = stop-gradient.

### B3. `12-unified-multimodal-models.mdx` — slug `unified-multimodal-models`
*Prereqs:* notation, input-representations, architecture-composition, training,
connectors-resamplers, discrete-visual-tokenization.
One decoder-only body (`def-tf5-decoder-only`) over interleaved image-text; modality only at the
embedding/unembedding interfaces.
- **Def 12.1 Interleaved sequence** $u_t=(c_t,x_t)$, tag $c_t\in\{\text{txt},\text{img}\}$.
- **Def 12.2 Modality-specific embedding** $\mathbf E_{c_t}[x_t,:]+\mathbf m_{c_t}$ (or soft token);
  per-position modality offset extends `def-tf1-token-embedding`.
- **Def 12.3 Modality-specific heads** routed by predicted modality.
- **Thm 12.1 Any-to-any factorization**: one body realizes every conditional (text→image,
  image→text, interleaved); Ch 6 chain rule is alphabet-agnostic.
- **Prop 12.1 Merged-vocabulary reduction**: with $\mathcal V=\mathcal V_{\text{txt}}\sqcup\mathcal V_{\text{img}}$
  the model is **exactly** the Ch 6 AR transformer — image and text are one language (Chameleon).
- **Prop 12.2 Why generation is discretized**: a categorical softmax head needs a finite alphabet
  (no closed normalizer over $\R^d$) ⇒ discretize *output* (Ch 11); conditioning only *reads*
  images, so *input* may stay continuous (Ch 10). Formal basis for the continuous-in/discrete-out
  design. Routing = hard analog of MoE (`def-tf9-moe`).
- **Def 12.4 Mixed block-causal mask**: causal across segments, bidirectional within an image
  segment; reduces to the Ch 2 causal mask when all-text.
- *Sources:* chameleonteam2024, lu2022unifiedio, zhou2024transfusion, sun2023emu, aghajanyan2022cm3.
  *Figures:* unified decoder w/ routed heads; design-space (merged/two-path/hybrid); mixed mask.

### B4. `13-multimodal-evaluation.mdx` — slug `multimodal-evaluation` (compact capstone)
*Prereqs:* notation, training, detection-encoders, unified-multimodal-models.
Math-first; every VL metric reduces to a ranking statistic (Ch 7) or a likelihood (Ch 6).
- **Def 13.1 + Prop 13.1 Retrieval**: rank, recall@k, MRR; **recall@1 = in-batch contrastive
  accuracy**, and the pairwise "positive outscores distractor" probability is the
  Mann–Whitney/AUROC statistic (`prop-tf7-auroc-rank`).
- **Def 13.2 + Prop 13.2 Perplexity** = $\exp$ of conditional cross-entropy (`def-tf6-ce-loss`) ⇒
  minimizing it minimizes conditional KL. Remark: BLEU/CIDEr/SPICE are surface overlap, not proper
  scoring rules.
- **Def 13.3 + Prop 13.3 Zero-shot** classification = softmax classifier whose weights are the
  class-name **text embeddings** (`def-tf7-encoder-classifier`), trained on **no** target labels;
  works because of contrastive geometry (`prop-tf7-contrastive-alignment`).
- *Sources:* radford2021clip, karpathy2015deepvisual, papineni2002bleu, vedantam2015cider,
  anderson2016spice. *Figures:* retrieval rank/top-k band; (opt) zero-shot nearest-text on sphere.

---

## Infrastructure (do first — unblocks authoring)

1. **KaTeX macros** in `astro.config.mjs` (`katexMacros`): add `\Emb`→`\operatorname{Emb}` and
   `\sg`→`\operatorname{sg}`. (`\norm`, `\inner` already exist and are reused.)
2. **Bibliography** `bibliography.bib` — add VLM primary sources (none exist yet). Core set:
   `dosovitskiy2021vit`, `alayrac2022flamingo`, `liu2023llava`, `liu2023llava15`, `li2023blip2`,
   `jaegle2021perceiver`, `tishby1999information`, `tishby2015deeplearning`, `vandenoord2017vqvae`,
   `razavi2019vqvae2`, `esser2021vqgan`, `ramesh2021dalle`, `bengio2013estimating`,
   `chameleonteam2024`, `lu2022unifiedio`, `zhou2024transfusion`, `sun2023emu`, `aghajanyan2022cm3`,
   `karpathy2015deepvisual`, `papineni2002bleu`, `vedantam2015cider`, `anderson2016spice`.
   (`radford2021clip`, `raffel2020t5`, `touvron2023llama`, `vaswani2017attention` already present.)
   **Standardize the ViT key to `dosovitskiy2021vit`** across all chapters.
3. **Figures**: author TikZ in `figures/*.tex` (standalone preamble matching
   `attention-pattern.tex`) → `public/figures/*.svg` via `book-scaffold build-figures` (already in
   `prebuild`). New keystone figure `dual-embedding.tex` (text-lookup ∥ patch-projection → same
   $\R^{n\times d}$). Plus the per-chapter figures listed in Part B (~8–10 total).
4. **Appendix** `99-appendix-solutions.mdx`: extend `prerequisites` with the 4 new slugs; append
   solution sections for `soln-tf1-ex6..8` and `soln-tf10..13-*` (~17 proofs/computations).

---

## Cross-reference & ID reconciliation

- Both designs cite existing ids by `<XRef>` (e.g. `prop-row-stochastic-convex`, `def-tf6-ce-loss`,
  `def-tf7-contrastive`, `prop-tf7-auroc-rank`, `def-tf9-kv-cache`, `def-tf9-moe`, `def-tf8-lora`).
  **Before authoring cross-refs, grep `id="` in Ch 06/07/09** to confirm exact slugs (some were
  inferred from summaries, not read). Fix any mismatch at author time.
- Forward-references (Ch 7 remark, Ch 5/6 remarks → Ch 10/13) are added in a **final link pass**
  once the new chapters' ids exist; until then existing-id links keep every file compiling.
- `labels.json` is auto-generated from `id=` on build, so new ids resolve without manual TOC edits.

---

## Implementation sequencing — two gated increments

Confirmed delivery: **Increment 1 (Part A weave) ships and is reviewed/built before Increment 2
(Part B new chapters) begins.** Each increment is independently buildable.

### Increment 1 — the dual-footing weave (Part A)
0. **Repo plan doc + memory** (first): copy this plan into `docs/plans/active/vlm-extension_<ts>.md`
   (project Large Task Protocol); save the **dual-footing principle** as a project memory + a line
   in the repo `CLAUDE.md` authoring contract (durable rule for future chapters).
1. **Infra**: add `\Emb` macro; add the Part-A bib keys (`dosovitskiy2021vit`, `alayrac2022flamingo`,
   `liu2023llava`, `vandenoord2017vqvae`); author `figures/dual-embedding.tex`; build figures.
2. **Ch 0**: notation rows + `TF-0.4`. Trivial.
3. **Ch 1** (highest churn — the only renumbering): grep Ch 1 for "Definition 3/4/5/6" &
   "Theorem 1/2/3" to bound edits, apply the renumber map, insert Defs 3–5 + Thm 1 + 2D-position
   Def 8/Thm 4 + capstone remark + figure + exercises 6–8; add `soln-tf1-ex6..8` to the appendix.
4. **Ch 5, 6, 7**: append the remarks/example + frontmatter deltas (append-only; new remarks carry
   their own counters → no renumbering).
5. **Gate**: `npm run build` clean, guide-health no regressions, all `<XRef>`/`<Cite>` resolve,
   visual spot-check of the Ch 1 keystone figure. **Review before proceeding.**

### Increment 2 — the four new chapters (Part B)
6. **Infra**: add `\sg` macro; add the remaining Part-B bib keys.
7. **Chapters 10 → 11 → 12 → 13** (this order = dependency order): author each with its figures and
   appendix solutions; run a build after each to catch KaTeX/MDX/`<XRef>` errors early. Connectors
   (Ch 10) authored at **full** depth (projector + resampler + info-bottleneck + Flamingo gating).
8. **Final cross-link pass**: wire the forward-references from Ch 5/6/7 into the new chapters' ids;
   full link-integrity check.
9. **Gate**: full `npm run build`, figures present/rendering, readiness check, adversarial math
   review of the new proofs (patch=conv, 2D shift, STE identity, VQ k-means, Thm 11.3 dual-footing,
   Flamingo identity-at-init, any-to-any, recall@1=accuracy), exercises↔solutions all resolve.

---

## Verification (end-to-end)

- **Build**: `npm run build` (runs `prebuild` → `build:figures` → `build:labels`) must pass with no
  KaTeX/MDX errors and all `<XRef>`/`<Cite>` resolved. `npm run dev` for visual spot-check of the
  keystone Ch 1 figure and the new chapters.
- **Figures**: confirm each `figures/*.tex` produced a `public/figures/*.svg` and renders.
- **Frontmatter/schema**: every new/edited chapter validates against
  `researchPortfolioChapterSchema.merge(formalChapterExtensions)` (title + last_verified minimum;
  los ids unique across the merged book).
- **Guide health**: run the project's `checking-guide-health` / `verifying-guide-readiness`
  workflows; confirm no regressions and no broken theorem references after the Ch 1 renumber.
- **Math review**: the genuinely-new proofs (patch=conv, 2D shift, STE identity, VQ k-means,
  dual-footing Thm 11.3, Flamingo identity-at-init, any-to-any, recall@1=accuracy) get an
  adversarial pass (`/adversarial-review` or a verification subagent) for rigor.
- **Exercises ↔ solutions**: every `<XRef id="soln-tf*">` resolves to a proof block in `99`.

---

## Open items / notes
- The two design passes agreed on substance; the only reconciliations are the ViT bib key name
  (standardize `dosovitskiy2021vit`) and confirming inferred ids in Ch 06/07/09 by grep.
- Scope is large (~2000+ lines MDX + ~10 figures + ~25 bib entries). Author in the phase order
  above; each phase is independently buildable.
- Chapters `02`, `03`, `04`, `08`, `09` are deliberately **untouched** — that they need no change
  is itself the proof of the dual-footing thesis and should be stated as such in Ch 1's capstone
  remark.

---

## Completion (2026-07-01)

**Shipped.** Increment 1 + 2 delivered as PR #1 → squash-merged `36cb6b1`
("feat: vision-language models (dual-footing extension, chapters 10–13)"),
review fixes in `c1ec95d`. The guide is 14 chapters (00–13), no appendix.

**Gate evidence.** `npm run build` green (14 chapters, 12 figures, 0 KaTeX
errors in rendered HTML); `validate` clean; codex adversarial proof audit of
all 13 genuinely-new proofs (6 rigor fixes applied, incl. KL-direction and
`prop-tf12-why-discrete` rescope); 3-voice adversarial review on PR #1 found
3 semantic bugs (KV-cache 21.5 GB, Ex9.5 1.65, RoPE-proof XRef), fixed.

**Decisions / deviations from this plan.**
- Solutions appendix (`99`) replaced by inline collapsible `SolutionBox`
  components per exercise (50 boxes across 10 chapters) — supersedes
  Infrastructure item 4 and the appendix rows in the chapter map.
- The 3-voice adversarial-review engine truncated to 4/78 files (covered the
  Increment-1 edits + config); the codex proof audit covered the full
  new-proof surface of chapters 10–13.
- Guide-health / readiness workflows inapplicable: this repo has no
  `guide_qa.yaml`.
- `ssmMacros` import deferred pending scaffold issue #177 (OPEN as of
  2026-07-01); KaTeX macros remain inline-duplicated in `astro.config.mjs`.

**Post-ship CI repair.** The standalone `content-validate` job failed on fresh
checkouts (gitignored `src/data/*.json` never generated); fixed via PR #3 →
`b8dc252` (`prevalidate` npm hook + `npm run validate` + widened trigger
paths). Both workflows green on `main`. Siblings + upstream tracked:
mathematical-guides#2, mathematical-guides-reinforcement-learning#1,
book-scaffold-astro#186.
