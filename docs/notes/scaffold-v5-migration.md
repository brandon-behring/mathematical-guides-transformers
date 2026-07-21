# Scaffold v4 → v5 migration (2026-07-21)

Migrated `@brandon_m_behring/book-scaffold-astro` **^4.26.2 → ^5.2.0**. Single-book app; the
`transformers-systems` sibling is the v5.2.0 exemplar. Tracked on issue #26.

## Dependency compat matrix

| package | before | after | note |
|---|---|---|---|
| `@brandon_m_behring/book-scaffold-astro` | ^4.26.2 | **^5.2.0** | the only dependency that changed |
| `astro` | ^6.1.7 | ^6.1.7 | already the v5 peer — no Astro migration |
| `@astrojs/mdx` | ^5.0.3 | ^5.0.3 | already satisfies the v5 peer |
| `@astrojs/preact` | ^5.1.1 | ^5.1.1 | already satisfies the v5 peer |
| `preact` | ^10.29.1 | ^10.29.1 | already satisfies the v5 peer |

The guide already tracked Astro 6, so v5 was a single-line dependency bump plus the content/config
changes below. Node ≥ 22.12 (v5 engines) — satisfied (22.20).

## v5.0.0 breaking changes and how each was handled

1. **Mandatory preset (#212).** Already satisfied — `researchPortfolioStyle` in `styles:[…]` carries
   the `research-portfolio` preset. No change.
2. **`deploy` field removed (#211).** Deleted `deploy: 'pages'` from `mathematicalGuidesFamilyStyle`
   in `astro.config.mjs`. Deployment is configured by the platform + Astro `site`/`base` (base stays
   `/transformers/`).
3. **`apparatusRoutes` vocabulary restricted.** v5 accepts only
   `references | print | convergence | tips | exercises | glossary | practice-exam | flashcards |
   answers`. The guide's custom `quick-reference` key is rejected (build fails at `build-bib` config
   validation), and v5's `references` slot is the `<Cite>` **bibliography**, not a quick-reference.
   Changed `apparatusRoutes: ['glossary', 'quick-reference'] → ['glossary']`. The `/quick-reference/`
   page still builds (Astro file routing) and stays in the print edition; v5 has no config for a
   custom nav link and no nav slot, so restoring its sidebar link would require forking Base/NavContent
   — **decision: accept print-edition + direct-URL discoverability** (the pull-out's primary role is the
   printed card).

Schemas (`researchPortfolioChapterSchema`, `glossarySchema`, `frontmatterCollection`) and every deep
component import (`Theorem`/`Cite`/`XRef` ×24, `Base`, `ChapterHeader`, `virtual:book-scaffold/mdx-components`)
are unchanged in v5's exports — zero fan-out there.

**Deploy note (#188, net-new since 4.27).** The build now emits a default `dist/_headers` (security
headers + CSP; no `public/_headers` override). Benign here — this is a standalone Cloudflare Pages
project serving at root, so the `/*` pattern matches, and every family sibling ships the same default.
Caveat: the CSP is enforced only in production, not by `astro build` / static preview — a future CDN
script, external web font, or cross-origin `connect`/image source would break in prod while CI stays
green. The current build loads zero external scripts/styles/fonts, so nothing is affected today.

## Figures — the #190 base-escape check (the substantive work)

**Version correction:** issue #26 attributes the base-escape validator to scaffold 4.27; it actually
landed in **4.30.0** (#190). A true 4.26→4.27 bump would not have flagged figures — the block bites at
≥ 4.30.0, hence all of 5.x.

Under the non-root base `/transformers/`, v5 `validate` runs two checks that **conflict for any literal
`src`**:
- **#190 (check 10)** rejects a root-absolute authored `src` that escapes the base — so `/figures/x.svg`
  fails; it must be under `/transformers/`.
- **figure-existence (check 3)** resolves `public/<literal-src>` with **no base-strip** — so a literal
  `/transformers/figures/x.svg` points at `public/transformers/figures/x.svg`, which does not exist
  (figures live at `public/figures/`).

No literal string satisfies both. Both checks are regex-based over quoted string literals and
deliberately skip JSX expressions, so the sanctioned fix is the **base-aware expression** form:

```mdx
<Figure src={`${import.meta.env.BASE_URL}figures/<name>.svg`} ... />
```

All 31 authored srcs across 18 chapters were converted to this form. The local `Figure.astro` fork
(kept for per-figure SVG-ID namespacing on the single-document `/print/` route) gained a
`publicSvgPath(src, base)` helper — ported from the scaffold's `src/lib/figure.mjs` — that strips
`BASE_URL` before the `public/` read, so the resolved `/transformers/figures/x.svg` still inlines from
`public/figures/x.svg`. The ID-namespacing key is derived from the base-stripped path, so emitted IDs
are byte-identical to v4.

(Rejected alternative: duplicating the figure tree into `public/transformers/figures/` to keep literal
srcs — it fights `build:figures`, whose output is `public/figures/`.)

## Verification (worktree, vs a captured 4.26.2 baseline)

- `validate` exits **0** (24 chapters; was exit 31 under v5 pre-fix).
- `build` ✓ 32 pages; all nine `check:*`/`test:*` scripts pass (incl. `test:figure-svg`,
  `test:print-html`, `test:polish`).
- Runtime figures: 24 chapters inline SVG, **0** `<img>` fallbacks; print route inlines **31**
  namespaced figures (cross-figure-collision-safe).
- PDF: **298 pages** (identical to the 4.26.2 baseline; byte size within 10 B of metadata).

## Rollback

Discard the `chore/v5-migration` worktree/branch; `main` stays on 4.26.2. `build:figures` (pdflatex)
regenerates tracked figure PDFs with new timestamps — `git checkout -- figures/` before
`git worktree remove` (never `--force`).
