# mathematical-guides-transformers — AI authoring guide

Per-guide sibling of the `mathematical-guides` family (formal lens). Built on
`@brandon_m_behring/book-scaffold-astro` v4.26+; deploys to `/transformers/`. Titled
**"Transformer Mathematics"**: 19 chapters across 6 parts carrying the full arc — foundations →
recurrence and linear state → transformer architectures and objectives → efficient and conditional
computation → sub-quadratic and selective sequence models → multimodal models.

## Numbering contract
Final display numbering intentionally reserves 08 (in-context learning), 11 (RLHF/DPO), 13
(scaling laws), 16 (mixture of experts), and 17 (sparse attention). Until those planned chapters
land, the 19 current chapters occupy 00–07, 09–10, 12, 14–15, and 18–23. Keep each frontmatter
`slug` number-free: filenames and `chapter:` values may fill the reserved slots, but existing URLs
must remain stable.

## Authoring contract
Follow `~/Claude/mathematical-guides/docs/style-guide-formal-v0.3.md`: motivated Definition–Theorem–Proof;
intuition-first; **structured proofs read inline** (appendix only for the longest); `\defeq` +
typography conventions; disciplined notation; **faded/optional** worked examples; `<Theorem kind=...>`
+ slim margins; first-person "we"; cite primary sources.

## Schema
`src/content.config.ts` = `researchPortfolioChapterSchema.merge(formalChapterExtensions)`; chapters
glob `./src/content/transformers`. Minimum frontmatter: `title` + `last_verified`.

## Figures
TikZ source in `figures/*.tex` → PDF (pdflatex) → SVG in `public/figures/` via
`book-scaffold build-figures` (wired into `prebuild`). Reference with
`<Figure src="/figures/<name>.svg" ...>` (public-relative; the scaffold applies the base prefix at render).

## Do NOT
- Modify `~/course_learning/transformer_mathematics` — frozen LaTeX source.

## Family macros
KaTeX macros (`\R \Z \N \E \Var \norm \inner \defeq`) inline-duplicated in `astro.config.mjs` from the
hub's canonical `shared/styles/mathematical-guides-family.ts`. The SSM semantic macros
(`\statevec \statemat \inputmat \outputmat \feedmat \discA \discB`, rendering as bold `h A B C D` and
`Ā B̄`) are pinned to `\mathbf` typography as top-level consumer overrides in `astro.config.mjs` — they
win over the scaffold-injected `ssmMacros` (forward-compatible with scaffold #177). State dimension is
`d_s`, step size `\Delta`, scan operator `\bullet`, elementwise `\odot`; never `\seqlen/\statedim/\inputdim`.
