# mathematical-guides-transformers

A **formal, Definition–Theorem–Proof** treatment of the transformer architecture (attention, softmax,
scaling) — a sibling of the [mathematical-guides](https://github.com/brandon-behring/mathematical-guides)
family. Deploys to `/transformers/` under the family hub.

Authoring follows the family's dossier-grounded
[formal style guide](https://github.com/brandon-behring/mathematical-guides/blob/main/docs/style-guide-formal-v0.1.md).

## Status: skeleton

One proof-of-style chapter — `src/content/transformers/00-attention.mdx` (ported from the LaTeX
`transformer_mathematics` guide: softmax + translation-invariance + the variance-preservation theorem,
with inline structured proofs and the attention-as-convex-combination known-math anchor).

## Figures

Diagrams are authored in **TikZ** under `figures/*.tex`, compiled to PDF, and converted to SVG into
`public/figures/` by `book-scaffold build-figures` (PDF → SVG via pdftocairo). `figures/attention-pattern.tex`
is the worked example. Regenerate with:

```bash
pdflatex -output-directory=figures figures/attention-pattern.tex && npm run build:figures
```

Source (frozen): `~/course_learning/transformer_mathematics` (LaTeX). This MDX guide is the canonical
home for the formal lens going forward.

```bash
npm install && npm run build
```

## License
Content CC BY 4.0 (`LICENSE`); code MIT (`LICENSE-SCRIPTS`).
