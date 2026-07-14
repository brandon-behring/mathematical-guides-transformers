# Whole-book independent polish — execution plan

**Status:** implemented
**Baseline:** `78a54ff6dee49938b31333a36860e21baab7ea29`
**Scope:** all 24 chapters plus the chapter index, navigation, figures, and print edition

## Editorial contract

This is a publication-polish pass over a mathematically audited baseline. It may
clarify, reorder, or add examples, but it must not silently weaken a hypothesis,
change a proved claim, or introduce an uncited factual assertion.

- Preserve all 24 chapter identities, semantic IDs, URLs, and printed numbers.
- Preserve the motivated Definition–Theorem–Proof register and mature-reader
  audience.
- Allow section-level reordering and small worked examples where they repair a
  demonstrated learning gap.
- Prefer deletion and compression over net prose growth, except for the reader
  contract, the missing attention trace, and targeted Part 6 scaffolding.
- Keep deployment out of scope until Cloudflare is configured.
- Publish as a draft PR for authorial review; do not merge automatically.

## Independent evidence

Three independently assigned read-only passes covered the complete book:

1. pedagogy and assessment;
2. prose, voice, and copy;
3. rendered web/print presentation and accessibility.

The baseline also passes corpus, semantic-ID, validation, property, figure,
print-HTML, BPE, and production-build gates. No mathematical blocker was found.

## Batch A — reader-facing defects and consistency

- Remove the redundant source-level chapter H1s; the scaffold already renders
  the frontmatter title, currently producing two visible H1s on every chapter.
- Replace math-bearing section headings whose KaTeX accessibility text is
  duplicated in the generated table of contents.
- Add non-placeholder book subtitle branding and the missing favicon.
- Shorten all card/header descriptions to reader-facing summaries without raw
  source notation.
- Remove build-pipeline boilerplate and internal semantic IDs from captions;
  keep captions concise and put detail in `alt`/`desc`.
- Supply explicit `alt` and `desc` for every figure.
- Route every semantic margin category through a guide-local component so its
  label and redundant visual treatment survive rendering.
- Give every solution disclosure a stable deep link and an accessible label
  naming its exercise.
- Fix confirmed grammar, terminology, citation spacing, hyphenation, and the
  speculative-decoding “accepted” versus “produced” mismatch.
- Clarify the designated-position pooling hull as the hull of ordinary content
  states, not the hull containing the designated state itself.
- Add a durable content-polish test and run it in CI.

### Notation, style, and terminology ledger

- Treat Chapter 0 and the repository style guide as the notation authority;
  preserve explicitly scoped `NotationOverride` exceptions.
- Inventory every recurring symbol, operator, abbreviation, capitalization,
  spelling, dash, and hyphenation choice across all 24 chapters before making
  replacements.
- Normalize reader-facing prose to one canonical form for terms such as
  encoder–decoder, row-wise, nonnegative, nondifferentiable, cross-attention,
  self-attention, multi-head, feed-forward, token-wise, zero-shot, image–text,
  and key–value/KV cache terminology. Preserve semantic IDs, URLs, source names,
  and grammatical noun/adjective distinctions.
- Normalize mathematical typography to the guide macros (`\\R`, `\\Z`, `\\N`,
  `\\E`, `\\Var`, `\\softmax`, `\\Emb`, `\\sg`, `\\defeq`, `\\norm`, and
  `\\inner`) wherever their meaning matches. Attach norm subscripts outside
  `\\norm`; write specialized dual or Jacobian actions explicitly rather than
  overloading raw angle delimiters. Preserve raw angle brackets only for
  syntactic placeholders.
- Record the canonical choices and intentional exceptions in a durable
  repository ledger (`docs/notation-style-terminology.md`), then add static
  regression checks for unambiguous drift.
- Perform a final cross-chapter consistency read after the range edits are
  reconciled; no chapter is accepted solely on its local consistency.

## Batch B — whole-book prose and navigation

- Rewrite every `Where we are` opener to one 80–120-word orienting paragraph:
  motivating problem, two or three moves, and destination.
- Remove theorem inventories, notation dumps, repetitive “same machinery”
  refrains, and excess metaphors from openers and transitions.
- Segment the five densest proof/exposition paragraphs with autonomous labels
  or genuine lists.
- Tighten overlong margins and calibrate absolute or overly casual claims.
- Normalize load-bearing prerequisite metadata without treating forward previews
  as prerequisites.
- Add a Chapter 0 “How to read this guide” section separating core prerequisites
  from advanced-proof prerequisites and identifying a core and full route.
- Mark the HiPPO and universal-approximation material as optional on a first pass.

## Batch C — targeted pedagogy

- Add a complete small-number Q/K/V attention trace immediately after the
  attention definition, including the causal-mask variant.
- Move Chapter 5’s dimension trace before cache-sharing variants and mark the
  MQA/GQA/MLA material as a forward-looking production section.
- Replace one redundant Chapter 4 exercise with an end-to-end trace.
- Add concise self-explanation prompts before the Part 6 data-processing, STE,
  any-to-any, and perplexity proofs; add a small inline trace only where the
  existing chapter has no concrete instance.
- Keep chapter splits, renumbering, and new cumulative capstones out of this
  pass; record them as optional future work rather than expanding the polish PR.

## Acceptance gates

- Exactly one rendered H1 on every chapter route.
- No math-source duplication in any generated section map.
- Every figure has explicit `alt` and `desc`; no caption contains an internal ID
  or build-pipeline note.
- No horizontal overflow, broken images, duplicate IDs, unnamed controls, or
  console errors across all chapter and apparatus routes at 375 px and 1440 px.
- Corpus, semantic-ID, property-coverage, validation, unit, and production-build
  gates pass.
- Zero rendered KaTeX errors.
- The notation/style/terminology ledger is satisfied across all reader-facing
  prose and mathematics, with intentional exceptions documented or scoped.
- Print PDF has no duplicated chapter title, stranded solution, accidental blank
  page, or split figure/caption.
- The final diff receives independent pedagogy, prose, and presentation review.
- Draft PR CI is green; merge and deployment require explicit user approval.

## Completion evidence

Implemented on `polish/whole-book-2026-07-14` and independently re-reviewed for
pedagogy, mathematical meaning, prose consistency, responsive presentation, and
print output. The final local acceptance run retains 24 chapters, 310 semantic
anchors, 109 learning objectives, 741 cross-references, 133 exercises, and 31
figures. All validation, corpus, semantic-ID, property-coverage, unit, and
production-build gates pass, including 95 guarded claims and 140 property tests.

A browser audit of 94 page instances at 320 px, 375 px, and 1440 px reports no
render, accessibility-name, fragment, overflow, HTTP, KaTeX, or runtime failures.
The final 298-page Letter PDF has 212 exact source-matching outline entries,
parser-clean tagged structure, embedded/subset Unicode fonts, no page-boundary
crossings, and no accidental blank pages.

Publication stops at a draft PR. Merge and deployment remain deferred until the
author has configured Cloudflare and explicitly approves those steps.
