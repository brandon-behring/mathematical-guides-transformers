# mathematical-guides-transformers — AI authoring guide

Per-guide sibling of the `mathematical-guides` family (formal lens). Built on
`@brandon_m_behring/book-scaffold-astro` v5.2+; deploys to `/transformers/`. Titled
**"Transformer Mathematics"**: 24 chapters across 6 parts carrying the full arc — foundations →
recurrence and linear state → transformer architectures and objectives → efficient and conditional
computation → sub-quadratic and selective sequence models → multimodal models.

## Numbering contract
The 24 chapters occupy every final display number from 0 through 23. Keep each frontmatter `slug`
number-free: zero-padded filenames and unpadded `chapter:` values carry source and display order,
while existing URLs remain stable.

## Authoring contract
Follow `~/Claude/mathematical-guides/docs/style-guide-formal-v0.3.md`: motivated Definition–Theorem–Proof;
intuition-first; **structured proofs read inline** (appendix only for the longest); `\defeq` +
typography conventions; disciplined notation; **faded/optional** worked examples; `<Theorem kind=...>`
+ slim margins; first-person "we"; cite primary sources.

Chapter 0's shared `NotationIndex.mdx` is the notation source of truth. Put any chapter-local symbol
reuse or row-to-column orientation switch in `NotationOverride.astro`; update the shared index when a
new recurring meaning is introduced. Add reader-facing terminology as one entry per file under
`src/content/glossary/`. Keep the compact lookup in `QuickReference.mdx` derived from the shared index,
not as a separately maintained notation table.

The reader-facing consistency contract is `docs/notation-style-terminology.md`. Apply it to chapters,
frontmatter, glossary entries, and quick-reference apparatus, then run `npm run test:polish`.

## Schema
`src/content.config.ts` registers chapters with
`researchPortfolioChapterSchema.merge(formalChapterExtensions)` and glossary entries with
`glossarySchema`. Chapters glob `./src/content/transformers`; glossary entries glob
`./src/content/glossary`. Minimum chapter frontmatter: `title` + `last_verified`.

## Reference routes
The native glossary route is enabled, so `apparatusRoutes: ['glossary']`. `/quick-reference/` is a
consumer-owned page (Astro file routing): v5 restricts `apparatusRoutes` to a fixed vocabulary with no
`quick-reference` key (its `references` slot is the `<Cite>` bibliography), so the pull-out is no longer
sidebar-linked — it stays reachable by URL and in the print edition. The local `/print/` route
deliberately replaces the scaffold route so the PDF contains chapters, the A–Z glossary, and the
pull-out quick reference in that order. Keep `routes.print: false` while `src/pages/print.astro` exists.

## Figures
TikZ source in `figures/*.tex` → PDF (pdflatex) → SVG in `public/figures/` via
`book-scaffold build-figures` (wired into `prebuild`). Under the non-root base, author the figure `src`
as a base-aware JSX expression built from `import.meta.env.BASE_URL` (a literal `/figures/…` is rejected
by the scaffold #190 base-escape check, and a literal base-prefixed path fails its figure-existence
check — the expression form satisfies both), through `src/components/Figure.astro`, imported from
`../../components/Figure.astro` by chapter files. Do not import the scaffold Figure directly: the local wrapper
`publicSvgPath`-strips the base before reading `public/figures/`, then namespaces pdftocairo's generic
internal IDs before inlining, which prevents cross-figure corruption on `/print/`.
`npm run test:figure-svg` enforces that boundary. The print route also scopes Markdown heading IDs per chapter;
`npm run test:print-html` guards that transform.

## Do NOT
- Modify `~/course_learning/transformer_mathematics` — frozen LaTeX source.

## Family macros
`\R \Z \N \E` come from the scaffold-injected `ssmMacros` base (identical definitions; scaffold #177
ships the set as a public export). The
family additions (`\Var \inner \defeq \softmax \Emb \sg`) and the auto-sizing `\norm` override remain
inline-duplicated in `astro.config.mjs` from the hub's canonical `shared/styles/mathematical-guides-family.ts`.
The state-space model (SSM) semantic macros
(`\statevec \statemat \inputmat \outputmat \feedmat \discA \discB`, rendering as bold `h A B C D` and
`Ā B̄`) are pinned to `\mathbf` typography as top-level consumer overrides in `astro.config.mjs` — they
win over the scaffold-injected `ssmMacros`. State dimension is
`d_s`, step size `\Delta`, scan operator `\bullet` (including `\scanop`), elementwise `\odot`; never `\seqlen/\statedim/\inputdim`.
