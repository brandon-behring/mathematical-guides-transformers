# mathematical-guides-transformers

A **formal, Definition–Theorem–Proof** treatment of the transformer architecture (attention, softmax,
scaling) — a sibling of the [mathematical-guides](https://github.com/brandon-behring/mathematical-guides)
family. Deploys to `/transformers/` under the family hub.

Authoring follows the family's dossier-grounded
[formal style guide](https://github.com/brandon-behring/mathematical-guides/blob/main/docs/style-guide-formal-v0.1.md).

## Status: pre-release (alpha)

Live behind a pre-release banner at
[`mathematical.brandon-behring.dev/transformers/`](https://mathematical.brandon-behring.dev/transformers/)
— the family hub proxies `/transformers/*` to this Worker. Fourteen chapters are authored in the
formal D–T–P register and have passed an independent proof-and-content audit. The guide is migrating
to a planned nineteen-chapter **sequence-models arc** (recurrent networks and state space models →
attention and transformers → hybrid architectures and vision–language models), so the chapter
numbering below is intentionally sparse while that arc lands.

| # | Chapter |
|---|---|
| 00 | Notation and Prerequisites |
| 01 | Input Representations |
| 04 | The Attention Mechanism |
| 05 | Multi-Head Attention |
| 06 | The Transformer Block |
| 07 | Architecture Composition |
| 09 | Training a Transformer |
| 10 | Encoders for Detection |
| 11 | Practical Training Optimizations |
| 12 | Inference Optimizations |
| 15 | Connectors and Resamplers |
| 16 | Discrete Visual Tokenization |
| 17 | Unified Multimodal Models |
| 18 | Multimodal Evaluation |

## Build & deploy

```bash
npm install && npm run build
```

Deployed via GitHub Actions + the [`deploy-workflows`](https://github.com/brandon-behring/deploy-workflows)
reusable workflow (`@v2.0.2`) to a Cloudflare Worker (`brandon-behring-mathematical-transformers`),
served under the family hub at `/transformers/`. The site builds with `base=/transformers/`;
`public/_redirects` maps that base path onto the dist-root assets for standalone serving.

## Figures

Diagrams are authored in **TikZ** under `figures/*.tex`, compiled to PDF, and converted to SVG into
`public/figures/` by `book-scaffold build-figures` (PDF → SVG via pdftocairo). Regenerate with:

```bash
pdflatex -output-directory=figures figures/<name>.tex && npm run build:figures
```

Source (frozen): the LaTeX `transformer_mathematics` guide. This MDX guide is the canonical home for
the formal lens going forward.

## License
Content CC BY 4.0 (`LICENSE`); code MIT (`LICENSE-SCRIPTS`).
