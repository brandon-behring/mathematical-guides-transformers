# Whole-book independent polish audit — 2026-07-14

## Scope and baseline

This publication-polish pass covers all 24 chapters, the glossary and quick
reference, the author page, site metadata, figures, navigation, and the print
edition. It began from commit
`78a54ff6dee49938b31333a36860e21baab7ea29`, after the terminal proof audit had
found no open mathematical blocker. Chapter numbers, slugs, semantic IDs,
citations, and URLs remained fixed.

Three independently assigned passes reviewed the full book from different angles:

1. pedagogy, prerequisites, exercises, and proof presentation;
2. mathematical prose, voice, notation, and terminology;
3. web/print presentation, accessibility, and systems-claim calibration.

The range authors then cross-reviewed one another's chapters. That second pass
caught several issues not expressible as lexical tests, including the scope of a
multi-head convex-hull claim, permutation equivariance versus loss of positional
identity, exposure-bias wording, AUROC pair dependence, selective-recomputation
logic, ZeRO sharding scope, per-head versus per-layer state accounting, the
latency meaning of arithmetic intensity, route prerequisites, and the residual
modality structure of a merged vocabulary.

## Changes accepted

### Reader contract and structure

- Removed the redundant source H1 from every chapter, leaving the scaffold's
  frontmatter-backed title as the sole rendered H1.
- Replaced three TeX-bearing section headings with plain-language headings so
  navigation does not duplicate KaTeX accessibility text.
- Added an honest prerequisite and reading-route section to Chapter 0, with a
  core transformer route and a full sequence-model route.
- Rewrote all chapter-card descriptions and all `Where we are` openers to a
  consistent reader-facing form.
- Marked the HiPPO and universal-approximation sections as optional on a first
  pass and segmented the densest explanations and proofs.

### Notation, style, and terminology

- Added `docs/notation-style-terminology.md` as the book-wide editorial ledger.
- Normalized shared mathematical macros, row/column announcements, chapter
  references, American spelling, dash spacing, common-noun capitalization, and
  first-use acronym expansions.
- Standardized paired terms such as *encoder–decoder*, *image–text*,
  *vision–language*, *query–key*, and *key–value*; standardized *state-space
  model* while retaining the cited coined name *State Space Duality*.
- Applied the same contract to the glossary, quick reference, author page,
  metadata, README, and authoring guide.
- Added a CI-enforced polish suite that separates reader-facing text from
  protected slugs, IDs, citation keys, and literal source titles.

### Pedagogy and claim precision

- Added a complete two-token attention trace and causal-mask variant, backed by
  a new property test; scoped straight-through-estimator gradients and exact
  merged-softmax factorization received guards as well, raising property
  coverage from 92 to 95 guarded claims.
- Moved the Chapter 5 dimension trace before production cache-sharing variants
  and made the MQA/GQA/MLA section an explicit forward preview.
- Added targeted self-explanation prompts in the multimodal chapters.
- Corrected or narrowed overbroad claims about resampler convexity, positional
  identity, induction retrieval, teacher-forcing distribution shift, label
  smoothing, contrastive invariances, AUROC, mixed precision, checkpointing,
  LoRA, ZeRO/FSDP, cache paging and quantization, FlashAttention, speculative
  decoding, State Space Duality, and connector information preservation.

### Accessibility and presentation

- Supplied authored `alt`, structural `desc`, and concise reader-facing captions
  for all 31 figures.
- Made SVG alternative text the accessible name and the longer description an
  independent `aria-describedby` description; namespaced SVG IDs remain intact.
- Added a guide-local semantic margin-note component with redundant labels and
  visual treatments for every supported note role, and gave ordinary sidenotes
  content-derived accessible names.
- Gave all 133 solution disclosures stable anchors and accessible names tied to
  their exercise numbers.
- Added generated semantic captions to every Markdown table and made notation
  index section labels real headings.
- Let dense figures use the full text-column width on narrow screens and added
  a guide favicon and non-placeholder subtitle.
- Kept sidenotes inside the print page, prevented equation-scroll affordances
  from printing, eliminated orphaned notation-index pages, and made the PDF
  renderer fail closed when the selected Chrome build cannot emit structure
  tags.

## Automated acceptance evidence

The final corpus retains 24 chapters, 310 semantic anchors, 109 learning
objectives, 741 cross-references, 133 exercises, and 31 figures. The following
checks pass:

- corpus and semantic-ID migration checks;
- 95 guarded-property coverage checks and 140 property tests;
- 13 content-polish tests, 4 SVG accessibility/ID tests, 3 print-HTML tests,
  and 7 BPE tests;
- scaffold validation and production build;
- 94 browser page instances covering all chapters and apparatus routes at
  320 px, 375 px, and 1440 px, plus the print route, with zero overflow, broken
  images, duplicate IDs, broken local fragments, unnamed
  controls/tables/notes, inaccessible figure SVGs, KaTeX errors, HTTP failures,
  or runtime failures;
- a 298-page Letter PDF with the exact expected title, 212 source-matching
  outline entries, and parser-clean structure tags; all 45 reported font rows
  are embedded, subset, and Unicode-mapped;
- tagged-PDF inspection reports zero structure-parser errors, all 62 exported
  Figure nodes have alternative text, and bounding-box inspection finds zero
  page-boundary crossings and zero sparse or accidental blank pages.

## Deliberately deferred

- Deployment remains blocked on the author's Cloudflare setup and requires
  explicit approval after the draft PR.
- A Chapter 1 split, new cumulative capstones, and additional bespoke figures
  for the efficiency chapters are structural enhancements rather than defects;
  they remain future editorial work.
- No chapter renumbering, semantic-ID cleanup, or URL migration was folded into
  this polish pass.
- Chrome's PDF exporter flattens HTML note roles, omits most generated hidden
  table captions, and does not retain the authored long SVG descriptions. The
  note content remains in reading order, every exported Figure is named, and
  the online guide retains the complete semantics; deeper PDF/UA normalization
  remains a future export-pipeline enhancement.
