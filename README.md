# Transformer Mathematics

A **formal, Definition–Theorem–Proof** treatment of sequence models — a sibling of the
[mathematical-guides](https://github.com/brandon-behring/mathematical-guides) family. Deploys to
`/transformers/` under the family hub.

The guide carries one arc from end to end: **foundations → recurrence and linear state → transformer
architectures and objectives → efficient and conditional computation → sub-quadratic and selective
sequence models → multimodal models**. Every construction the guide relies on is proved; reading
order follows the arc.

Authoring follows the family's dossier-grounded
[formal style guide](https://github.com/brandon-behring/mathematical-guides/blob/main/docs/style-guide-formal-v0.3.md).

## Structure: 21 chapters, 6 parts

Published chapter numbers deliberately reserve **08** (in-context learning), **11** (RLHF/DPO),
and **13** (scaling laws). The current 21-chapter corpus therefore occupies
**00–07, 09–10, 12, and 14–23**. Source filenames carry
those final display numbers, while frontmatter `slug` values are number-free, so filling a reserved
slot does not change an existing chapter URL.

- **Part 1 — Foundations.** Notation and prerequisites; input representations (the modality-agnostic
  embedding interface, positional encodings, RoPE).
- **Part 2 — Recurrence & Linear State.** Recurrent networks and the seq2seq lineage
  (BPTT, the vanishing-gradient bound, LSTM/GRU, the fixed-vector bottleneck, additive attention);
  linear recurrences and state space models (ZOH discretization, the recurrence/convolution/scan
  trinity, HiPPO, the LTI obstruction).
- **Part 3 — Transformer Architectures & Objectives.** Scaled dot-product attention; multi-head
  attention; the transformer block; architecture composition; encoders and decoders across
  architecture families (causality as prefix-consistency, abstracted over any sequence mixer);
  training; encoder readouts, contrastive alignment, and detection.
- **Part 4 — Efficient & Conditional Computation.** Training optimizations; inference optimizations
  (the KV-cache, quantization, FlashAttention, and speculative decoding); mixture-of-experts
  (routing gradients, load balance, expert capacity, cost accounting, and expert parallelism).
- **Part 5 — Sub-Quadratic & Selective Sequence Models.** Sparse and sub-quadratic attention
  (static and content-routed patterns, sparse expressiveness, NSA); selective state spaces and state
  space duality (Mamba, linear-attention/SSM duality, the chunked algorithm); modern recurrent
  models and hybrid architectures (RWKV, xLSTM, DeltaNet, sliding-window hybrids).
- **Part 6 — Multimodal Models.** Connectors and resamplers; discrete visual tokenization; unified
  multimodal models; multimodal evaluation.

Chapter files live in `src/content/transformers/`. Minimum frontmatter is `title` + `last_verified`;
the schema is
`researchPortfolioChapterSchema.merge(formalChapterExtensions)` (`src/content.config.ts`).

## Figures

Diagrams are authored in **TikZ** under `figures/*.tex`, compiled to PDF, and converted to SVG into
`public/figures/` by `book-scaffold build-figures` (PDF → SVG via pdftocairo), wired into `prebuild`.
Reference them with `<Figure src="/figures/<name>.svg" ...>` (public-relative; the scaffold applies
the base prefix at render). Regenerate all figures with:

```bash
npm run build:figures
```

## Build

```bash
npm install && npm run build     # runs build:bib, build:labels, build:figures, validate, then astro build + pagefind
npm run validate                 # XRef / Cite / Figure checks without a full build
npm run dev                      # local dev server
```

## License
Content CC BY 4.0 (`LICENSE`); code MIT (`LICENSE-SCRIPTS`).
