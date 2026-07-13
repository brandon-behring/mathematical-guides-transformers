# mathematical-guides-transformers — AI authoring guide

Per-guide sibling of the `mathematical-guides` family (formal lens). Built on
`@brandon_m_behring/book-scaffold-astro` v4.26+; deploys to `/transformers/`. Titled
**"Transformer Mathematics"**: 21 chapters across 6 parts carrying the full arc — foundations →
recurrence and linear state → transformer architectures and objectives → efficient and conditional
computation → sub-quadratic and selective sequence models → multimodal models.

## Numbering contract
Final display numbering intentionally reserves 08 (in-context learning), 11 (RLHF/DPO), and 13
(scaling laws). Until those remaining planned chapters land, the 21 current chapters occupy
00–07, 09–10, 12, and 14–23. Keep each frontmatter
`slug` number-free: filenames and `chapter:` values may fill the reserved slots, but existing URLs
must remain stable.

## Authoring contract
Follow `~/Claude/mathematical-guides/docs/style-guide-formal-v0.3.md`: motivated Definition–Theorem–Proof;
intuition-first; **structured proofs read inline** (appendix only for the longest); `\defeq` +
typography conventions; disciplined notation; **faded/optional** worked examples; `<Theorem kind=...>`
+ slim margins; first-person "we"; cite primary sources.

Chapter 00's shared `NotationIndex.mdx` is the notation source of truth. Put any chapter-local symbol
reuse or row-to-column orientation switch in `NotationOverride.astro`; update the shared index when a
new recurring meaning is introduced. Add reader-facing terminology as one entry per file under
`src/content/glossary/`. Keep the compact lookup in `QuickReference.mdx` derived from the shared index,
not as a separately maintained notation table.

## Schema
`src/content.config.ts` registers chapters with
`researchPortfolioChapterSchema.merge(formalChapterExtensions)` and glossary entries with
`glossarySchema`. Chapters glob `./src/content/transformers`; glossary entries glob
`./src/content/glossary`. Minimum chapter frontmatter: `title` + `last_verified`.

## Reference routes
The native glossary route is enabled. `/quick-reference/` is consumer-owned and listed in
`apparatusRoutes`. The local `/print/` route deliberately replaces the scaffold route so the PDF
contains chapters, the A–Z glossary, and the pull-out quick reference in that order. Keep
`routes.print: false` while `src/pages/print.astro` exists.

## Figures
TikZ source in `figures/*.tex` → PDF (pdflatex) → SVG in `public/figures/` via
`book-scaffold build-figures` (wired into `prebuild`). Reference with
`<Figure src="/figures/<name>.svg" ...>` through `src/components/Figure.astro`, imported from
`../../components/Figure.astro` by chapter files. Do not import the scaffold Figure directly: the local wrapper
namespaces pdftocairo's generic internal IDs before inlining, which prevents cross-figure corruption on `/print/`.
`npm run test:figure-svg` enforces that boundary. The print route also scopes Markdown heading IDs per chapter;
`npm run test:print-html` guards that transform.

## Do NOT
- Modify `~/course_learning/transformer_mathematics` — frozen LaTeX source.

## Family macros
KaTeX macros (`\R \Z \N \E \Var \norm \inner \defeq`) inline-duplicated in `astro.config.mjs` from the
hub's canonical `shared/styles/mathematical-guides-family.ts`. The SSM semantic macros
(`\statevec \statemat \inputmat \outputmat \feedmat \discA \discB`, rendering as bold `h A B C D` and
`Ā B̄`) are pinned to `\mathbf` typography as top-level consumer overrides in `astro.config.mjs` — they
win over the scaffold-injected `ssmMacros` (forward-compatible with scaffold #177). State dimension is
`d_s`, step size `\Delta`, scan operator `\bullet`, elementwise `\odot`; never `\seqlen/\statedim/\inputdim`.
