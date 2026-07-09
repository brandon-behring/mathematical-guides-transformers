# Design note — a "Sparse and Sub-Quadratic Attention" chapter

> **Status:** ideas + resources for the book rewrite. NOT chapter content, NOT a commitment to
> chapter numbering — placement is the rewrite session's call. Written 2026-07-09 while the
> evidence base (three research dossiers) is being built; treat every quantitative claim below
> as *to-be-anchored* against a primary at authoring time (the guide is strict about this).

## 1. Why this chapter

The guide already treats the **efficiency stack that surrounds sparse attention** with full
Definition–Theorem–Proof rigour, but has a hole exactly where "sparse attention" itself would sit:

| Already in the guide | Where | Depth |
|---|---|---|
| KV cache (memory + decode-cost props) | `03-multi-head-attention.mdx:113-146`, `09-inference-optimizations.mdx:77-124` | FULL |
| MQA / GQA | `03-multi-head-attention.mdx:113-146` | FULL |
| FlashAttention + online-softmax exactness theorem | `09-inference-optimizations.mdx:170-226` | FULL |
| MoE top-k routing + FLOPs proposition | `09-inference-optimizations.mdx:273-304` | FULL |
| Quadratic-complexity crossover (attn vs FFN) | `05-architecture-composition.mdx:166-193` | FULL |
| Linear / kernel attention | `05-architecture-composition.mdx:197-203` | PARTIAL (one remark) |
| PagedAttention | `09-inference-optimizations.mdx:124` | MENTION |

**Absent entirely:** sparse attention as a topic — static/learned attention *patterns*
(sliding-window, dilated, block-sparse), the classic long-document models (Sparse Transformer,
Longformer, BigBird, Reformer, Routing Transformer), the 2024–26 *natively-trainable* sparse
attention line (NSA, MoBA, DSA), inference-time KV *sparsity* (StreamingLLM/attention sinks,
H2O, SnapKV, Quest), and architectural KV compression (MLA). The guide currently has the pieces
that *reduce the constant* (KV cache, GQA) and the piece that *reduces memory but not FLOPs*
(FlashAttention) — but nothing on *reducing the asymptotic work by not attending everywhere*.

The natural framing that unifies the chapter: **the quadratic wall of §05, and the three escape
routes.** FlashAttention (already covered) is escape route zero — it keeps the O(n²) FLOPs but
makes them IO-optimal. The two remaining routes are *sparse* (compute a strategically chosen
subset of the n² scores) and *linear/kernel/SSM* (replace the softmax so no n² matrix ever
forms). Linear/SSM is a sibling territory (see `research_bridge_dynsys_ssm`, the
`post_transformers` project, and `ssm-foundations`); this chapter owns **sparse**.

## 2. Candidate structure

Proposed spine — five sections, mirroring the dossier sub-areas so the evidence base maps 1:1:

- **§1 The quadratic wall, restated as a sparsity opportunity.** Recap `prop-tf5-complexity`
  (O(n²d)); observe empirically-attested sparsity of learned attention maps (most mass on few
  keys) → the thesis that a chosen O(n·k) subset can approximate the full map. Set up the two
  design axes: *which* pairs to keep (the pattern) and *who decides* (static vs content-based vs
  trained).
- **§2 Static and factorized patterns.** Sliding-window / local, dilated, strided, block-sparse,
  global tokens. The Sparse Transformer factorization; Longformer (window + dilation + global);
  BigBird (window + random + global). Complexity drops from O(n²) to O(n·w) or O(n√n).
- **§3 Content-based and learned sparsity.** The model chooses the pattern: Reformer's LSH
  bucketing (O(n log n)); Routing Transformer's k-means routing; adaptively-sparse (entmax/
  sparsemax) attention distributions that produce *exact* zeros.
- **§4 Natively-trainable, hardware-aligned sparsity (the modern line).** NSA's three branches
  (compressed / selected / sliding-window), trained end-to-end and GQA-aligned; MoBA's
  MoE-style block routing; DSA (DeepSeek-V3.2) lightning-indexer token selection. The key modern
  shift: sparsity is *learned during pretraining*, not bolted on, and *co-designed with the
  kernel* so the FLOP savings become wall-clock savings.
- **§5 Inference-time KV sparsity.** Distinct axis: not "which scores to compute" but "which KV
  entries to keep." Attention sinks + StreamingLLM; H2O / SnapKV / Quest eviction & selection;
  MLA as low-rank KV factorization. Ties directly back to the ch09 KV-cache material.

Alternative packaging (per the AskUserQuestion answer the user gave — split by phase): fold §5
into ch09 where the KV cache already lives, and make §§1–4 the new chapter. Either works; the
rewrite decides. If split, keep a forward-reference from the new chapter's §1 to ch09 §KV.

## 3. Formalizability triage (what earns a Theorem vs a Remark)

The guide's discipline is Definition–Theorem–Proof with intuition first, faded/optional worked
examples, and *no unanchored numbers*. Not every result here is a theorem; calibrate:

**Strong theorem/proposition candidates (clean, self-contained, provable inline):**
- **Complexity propositions, one per pattern.** For window width w: attention is O(n·w·d) time,
  O(n·w) memory — a direct counting argument, exactly parallel to the existing
  `prop-tf5-complexity`. Same for dilated (O(n·w) with receptive field w·dilation^depth), block
  (O(n·b·d) for block size b), strided/factorized Sparse Transformer (O(n√n)), LSH Reformer
  (O(n log n)). These are the backbone; they're short, rigorous, and mirror machinery the guide
  already has.
- **Receptive-field growth under depth.** For a sliding window of width w stacked L layers, the
  effective receptive field is Θ(L·w) (or geometric under dilation) — a clean inductive
  argument. Motivates *why* local attention still models long-range structure. This is a genuine
  lemma with a one-paragraph proof.
- **MLA as a low-rank KV factorization + a cache-size proposition.** MLA stores a compressed
  latent c_t = W_DKV · h_t of dimension d_c ≪ d_h·n_h, and reconstructs per-head K,V by up-
  projection. Cache size drops from 2·n_h·d_h·T elements (MHA) to ≈ (d_c + d_R)·T. This is a
  crisp linear-algebra statement with a memory-accounting proof — the strongest theorem
  candidate in §5, and it slots beside the existing `prop-tf3-kv-cache` (which already derives
  the g/h and 1/h cache fractions for GQA/MQA). Frame MLA as the third point on that curve:
  MHA → GQA (share KV heads) → MLA (low-rank KV).
- **NSA branch decomposition as a definition + a combined-complexity proposition.** Define the
  three branches and the gated combination o_t = Σ_b g_t^b · Attn(q_t, K̃^b, Ṽ^b); prove the
  per-query cost is O(n/block · d) for the selected branch + O(w·d) for the window, i.e. sub-
  quadratic. Definition is clean; the complexity claim is countable.
- **Exactness of adaptively-sparse (sparsemax/entmax) attention.** sparsemax = Euclidean
  projection onto the simplex; α-entmax generalizes softmax (α=1) and sparsemax (α=2). The
  *exact-zero* property (support can be a strict subset) is a provable consequence of the KKT
  conditions of the projection — a real theorem with a clean proof, and it connects sparsity to
  convex analysis, which suits the formal lens.

**Statable-but-cite (theorem exists in the literature; state it precisely, sketch or cite the
proof rather than reproduce it):**
- **BigBird universal approximation / Turing-completeness.** BigBird (window + random + global)
  is a universal approximator of sequence functions and Turing-complete, whereas *some* sparse
  patterns are provably weaker. This is the deepest theoretical result in the area and the payoff
  of §2, but its proof is long — state the theorem carefully, give the intuition (random edges
  give the sparse graph small-world connectivity; global tokens give a shortcut), and cite. The
  *contrast* result (there exist sparse-attention mechanisms requiring polynomially more layers to
  match full attention) is the honest counterweight — include it.
- **Yun et al. O(n)-connections universal approximability** — sparse Transformers with O(n) total
  connections per layer can still be universal approximators under stated conditions. Companion to
  the BigBird result; cite together.

**Empirics / remark only (no theorem — the guide should mark these as observed, not proved):**
- **Attention sinks.** The observation that models dump excess attention mass on the first few
  tokens, and that *keeping* those "sink" KV entries stabilizes streaming generation
  (StreamingLLM). This is an empirical phenomenon with a mechanistic hypothesis, not a theorem —
  present as a motivated Remark with a figure, explicitly flagged as empirical.
- **H2O / heavy-hitter eviction.** "A small set of tokens accumulates most attention mass, and
  evicting the rest preserves quality" — an empirical regularity + a greedy policy. Remark +
  algorithm box, not a theorem.
- **Wall-clock ≠ FLOPs for sparse methods.** The honest, important caveat (already foreshadowed by
  the FlashAttention treatment): many sparse methods reduce FLOPs without wall-clock speedup
  because gather/scatter is memory-bound and irregular. This is a *discussion* point — arguably
  the single most valuable paragraph in the chapter for a practitioner — and it's inherently
  empirical/architectural. Present as a MarginNote or a "why this is subtle" Remark, echoing the
  IO-awareness thesis of §09.

## 4. Hooks into existing chapters

- **ch03 (multi-head):** `prop-tf3-kv-cache` already derives cache fractions for MQA/GQA. §5's
  MLA proposition is the natural third entry — literally extend that curve. Add a forward pointer
  from ch03 to the new chapter's MLA result.
- **ch05 (architecture composition):** `prop-tf5-complexity` (the O(n²) wall) is the chapter's
  launch point; the linear-attention remark `rem-tf5-linear-attention` is the *sibling* escape
  route. Reframe both remarks as a two-line taxonomy ("exact-but-IO-optimal = FlashAttention;
  sparse = this chapter; kernel/linear/SSM = bridge dossier / ssm-foundations") and forward-
  reference the new chapter.
- **ch09 (inference optimizations):** FlashAttention's online-softmax exactness theorem
  (`thm-tf9-online-softmax-exact`) is the "escape route zero" baseline; block-sparse
  FlashAttention is the bridge from §09 to §2 of the new chapter (FlashAttention's own paper
  extends to block-sparse — cite that continuity). The KV-cache props (`prop-tf9-kv-memory`,
  `prop-tf9-decode-cost`) are what §5's eviction/compression methods attack. PagedAttention
  (currently a mention) belongs in §5's "memory management" discussion; consider promoting it
  there.
- **MoE (ch09 §MoE):** worth an explicit one-line analogy — MoBA routes *attention blocks* the
  way MoE routes *FFN experts* (top-k over blocks vs experts). The guide already has the MoE
  top-k machinery; reuse the vocabulary.

## 5. Figure ideas (TikZ, per the guide's figures pipeline)

Figures live as `figures/*.tex` → PDF → SVG in `public/figures/` via `book-scaffold
build-figures`, referenced with `<Figure src="/figures/<name>.svg" ...>`.

- **Attention-mask pattern gallery** (the signature figure): a row of n×n mask grids — dense /
  sliding-window / dilated / strided / global+window (Longformer) / window+random+global
  (BigBird) / block-sparse. One visual, the whole taxonomy. This is the highest-value figure.
- **The three escape routes from the quadratic wall**: a schematic — full O(n²) attention at
  center, three arrows to (i) FlashAttention [same FLOPs, IO-optimal], (ii) sparse [subset of
  scores], (iii) linear/SSM [no n² matrix]. Anchors §1 and ties the chapter into ch05/ch09.
- **KV-cache-size curve MHA → GQA → MLA**: bar/line chart of cache elements per token, extending
  the ch03 GQA picture to MLA's low-rank point.
- **NSA three-branch schematic**: query → {compressed KV, selected blocks, sliding window} →
  gated sum. Makes the modern line concrete.
- **Attention-sink heatmap**: a real attention map showing the first-token mass spike (empirical
  figure for the StreamingLLM remark) — must be generated from an actual model or reproduced from
  the source with attribution, per the no-unanchored-figures discipline.

## 6. Evidence base — dossiers (being built) + primary sources

The three dossiers under construction are the citation substrate; author the chapter *after* they
land so every claim is anchored:

- **`research_sparse_attention_patterns`** (§§2–3 + theory): Sparse Transformer (1904.10509),
  Longformer (2004.05150), BigBird (2007.14062), ETC (2004.08483), Reformer (2001.04451),
  Routing Transformer (2003.05997), adaptively-sparse/entmax (1909.00015), sparsemax (1602.02068),
  Yun et al. O(n)-connections (2006.04862), Long Range Arena (2011.04006), Tay "Efficient
  Transformers: A Survey" (2009.06732).
- **`research_trainable_sparse_attention`** (§4): NSA (2502.11089), MoBA (2502.13189), DSA /
  DeepSeek-V3.2-Exp report, SeerAttention (2410.13276), MInference (2407.02490), FlexPrefill
  (2502.20766), "The Sparse Frontier" (2504.17768), RULER (2404.06654), retrieval heads
  (2404.15574).
- **`research_kv_cache_sparsity`** (§5): StreamingLLM (2309.17453), H2O (2306.14048), SnapKV
  (2404.14469), Quest (2402.10774), DuoAttention (2410.10819), KIVI (2402.02750), MLA/DeepSeek-V2
  (2405.04434), YOCO (2405.05254), PagedAttention (2309.06180).

(arXiv IDs are hypotheses to verify at authoring time — the dossiers do the live verification;
pull anchored excerpts + evidence IDs from them rather than re-deriving.)

Sibling territory NOT owned by this chapter (cross-link, don't duplicate): linear/kernel attention
and SSMs (Performer, Linformer, Mamba, Hyena, RWKV) → `research_bridge_dynsys_ssm`,
`post_transformers`, `ssm-foundations`; FlashAttention kernel lineage →
`post_transformers/.../engineering_tricks/04`; KV-cache *economics/pricing* →
`research_agent_ops_cost`.

## 7. Open questions for the rewrite session

- **Placement:** standalone chapter, or §§1–4 standalone + §5 folded into ch09? (User leaned
  toward split-by-phase in planning; not decided.)
- **Depth on the modern line (§4):** NSA/MoBA/DSA move monthly. Decide how much to commit to
  print vs. keep as a "current frontier" remark with a `last_verified` gate — the volatile
  material risks staleness the way the rest of the guide doesn't.
- **Theory dose:** how much of the BigBird universality proof to reproduce vs cite. A formal-lens
  reader wants *a* proof; the full one is long. A proof-sketch + a boxed precise statement is
  probably the right altitude.
- **VLM tie-in (family principle):** the guide's dual-footing VLM/LLM principle suggests noting
  where sparse attention interacts with vision tokens (windowed attention in ViTs, Swin's shifted
  windows) — at least a MarginNote so the vision modality isn't siloed.
