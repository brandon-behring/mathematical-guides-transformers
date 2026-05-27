# mathematical-guides-transformers — AI authoring guide

Per-guide sibling of the `mathematical-guides` family (formal lens). Built on
`@brandon_m_behring/book-scaffold-astro` v4.2.0; deploys to `/transformers/`.

## Authoring contract
Follow `~/mathematical-guides/docs/style-guide-formal-v0.1.md`: motivated Definition–Theorem–Proof;
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
hub's canonical `shared/styles/mathematical-guides-family.ts`.
