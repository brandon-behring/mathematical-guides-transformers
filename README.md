# Transformer Mathematics

A **formal, Definition–Theorem–Proof** treatment of sequence models — a sibling of the
[mathematical-guides](https://github.com/brandon-behring/mathematical-guides) family. Deploys to
`/transformers/` under the family hub.

The guide carries one arc from end to end: **recurrent networks and state space models → attention
and the transformer → encoders and decoders across architecture families → selective state spaces
and hybrid architectures → vision-language models**. Every construction the guide relies on is
proved; reading order follows the arc.

Authoring follows the family's dossier-grounded
[formal style guide](https://github.com/brandon-behring/mathematical-guides/blob/main/docs/style-guide-formal-v0.3.md).

## Structure: 19 chapters, 5 parts

- **Part 1 — Foundations.** Notation and prerequisites; input representations (the modality-agnostic
  embedding interface, positional encodings, RoPE).
- **Part 2 — Sequence models before attention.** Recurrent networks and the seq2seq lineage
  (BPTT, the vanishing-gradient bound, LSTM/GRU, the fixed-vector bottleneck, additive attention);
  linear recurrences and state space models (ZOH discretization, the recurrence/convolution/scan
  trinity, HiPPO, the LTI obstruction).
- **Part 3 — The transformer.** Scaled dot-product attention; multi-head attention; the transformer
  block; architecture composition; encoders and decoders across architecture families (causality as
  prefix-consistency, abstracted over any sequence mixer); training.
- **Part 4 — Encoders in practice & efficiency.** Detection encoders; training optimizations;
  inference optimizations (the KV-cache, quantization, speculative decoding); selective state spaces
  and state space duality (Mamba, linear-attention/SSM duality, the chunked algorithm); modern
  recurrent models and hybrid architectures (RWKV, xLSTM, DeltaNet, sliding-window hybrids).
- **Part 5 — Vision-language.** Connectors and resamplers; discrete visual tokenization; unified
  multimodal models; multimodal evaluation.

Chapter files live in `src/content/transformers/` (number-free slugs → stable URLs). Minimum
frontmatter is `title` + `last_verified`; the schema is
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
