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

## Structure: 23 chapters, 6 parts

Published chapter numbers deliberately reserve **13** (scaling laws).
The current 23-chapter corpus therefore occupies **00–12 and 14–23**. Source filenames carry
those final display numbers, while frontmatter `slug` values are number-free, so filling a reserved
slot does not change an existing chapter URL.

- **Part 1 — Foundations.** Notation and prerequisites; input representations (reversible text tokenization
  with BPE, the modality-agnostic embedding interface, positional encodings, RoPE).
- **Part 2 — Recurrence & Linear State.** Recurrent networks and the seq2seq lineage
  (BPTT, the vanishing-gradient bound, LSTM/GRU, the fixed-vector bottleneck, additive attention);
  linear recurrences and state space models (ZOH discretization, the recurrence/convolution/scan
  trinity, HiPPO, the LTI obstruction).
- **Part 3 — Transformer Architectures & Objectives.** Scaled dot-product attention; multi-head
  attention; the transformer block; architecture composition; in-context learning through
  associative lookup, copying and induction, and a controlled linear-attention gradient-descent
  construction; encoders and decoders across architecture families (causality as
  prefix-consistency, abstracted over any sequence mixer); token-level training; pairwise preference
  optimization through RLHF and DPO; encoder readouts, contrastive alignment, and detection.
- **Part 4 — Efficient & Conditional Computation.** Training optimizations; inference optimizations
  (greedy, temperature, top-$k$, and top-$p$ decoding; the KV-cache, quantization, FlashAttention,
  and speculative decoding); mixture-of-experts
  (routing gradients, load balance, expert capacity, cost accounting, and expert parallelism).
- **Part 5 — Sub-Quadratic & Selective Sequence Models.** Sparse and sub-quadratic attention
  (static and content-routed patterns, sparse expressiveness, NSA); selective state spaces and state
  space duality (Mamba, linear-attention/SSM duality, the chunked algorithm); modern recurrent
  models and hybrid architectures (RWKV, xLSTM, DeltaNet, sliding-window hybrids).
- **Part 6 — Multimodal Models.** Connectors and resamplers; discrete visual tokenization; unified
  multimodal models; multimodal evaluation.

Chapter files live in `src/content/transformers/`. Minimum frontmatter is `title` + `last_verified`;
the chapter schema is `researchPortfolioChapterSchema.merge(formalChapterExtensions)`. Glossary
entries live in `src/content/glossary/` and use the scaffold's `glossarySchema`
(`src/content.config.ts`).

## Reference apparatus

Chapter 00 contains the authoritative shared notation index. Chapter-local symbol or orientation
departures are called out with `NotationOverride`; do not silently reuse a standing symbol. The
site also exposes an alphabetical glossary at `/transformers/glossary/` and a pull-out notation and
equation card at `/transformers/quick-reference/`. The print edition appends both resources after
the chapters.

## Figures

Diagrams are authored in **TikZ** under `figures/*.tex`, compiled to PDF, and converted to SVG into
`public/figures/` by `book-scaffold build-figures` (PDF → SVG via pdftocairo), wired into `prebuild`.
Reference them with the project-local `<Figure src="/figures/<name>.svg" ...>` wrapper
(`src/components/Figure.astro`). It preserves inherited theming and namespaces converter-generated
SVG IDs so multiple inline diagrams remain independent in the combined print document. Regenerate
all figures with:

```bash
npm run build:figures
```

## Build

```bash
npm install && npm run build     # runs build:bib, build:labels, build:figures, validate, then astro build + pagefind
npm run validate                 # XRef / Cite / Figure checks without a full build
npm run test:properties          # numeric guards for quantitative claims
npm run test:bpe                 # deterministic BPE merge and accounting tests
npm run test:figure-svg          # inline-SVG ID/reference isolation
npm run test:print-html          # chapter-scoped heading IDs in the combined print route
npm run check:corpus             # verify tracked corpus structure, labels, and printed-number inventory
npm run dev                      # local dev server
```

## License
Content CC BY 4.0 (`LICENSE`); code MIT (`LICENSE-SCRIPTS`).
