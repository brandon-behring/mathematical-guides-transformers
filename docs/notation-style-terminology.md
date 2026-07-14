# Notation, style, and terminology ledger

**Status:** active editorial contract
**Scope:** reader-facing prose and mathematics in all chapters, frontmatter,
glossary entries, quick-reference material, print apparatus, and repository overview
**Authority:** Chapter 0 and the formal style guide v0.3

This ledger records recurring choices that are too local for the family style
guide but too important to decide independently in each chapter. It does not
authorize changes to semantic IDs, slugs, URLs, citation keys, filenames,
cited publication titles, or explicitly scoped `NotationOverride` passages.

## Mathematical notation

| Meaning | Canonical source | Do not introduce |
|---|---|---|
| real, integer, natural domains | `\R`, `\Z`, `\N` | raw `\mathbb{R}`, `\mathbb{Z}`, `\mathbb{N}` |
| expectation and variance | `\E`, `\Var` | locally restyled operator names |
| norm | `\norm{\mathbf x}` | raw delimiters when the shared macro has the same meaning |
| inner product | `\inner{\mathbf x}{\mathbf y}` | raw angle brackets when the shared macro has the same meaning |
| definitional equality | `\defeq` | `:=` or ordinary `=` for a stipulation |
| softmax | `\softmax` | raw `\operatorname{softmax}` |
| embedding and stop-gradient maps | `\Emb`, `\sg` | locally restyled operator names |

Attach a norm subscript outside the macro, as in `\norm{\mathbf A}_2`; matrix,
operator, and function norms use the same macro. Use `\inner` for every
mathematical inner product. Raw angle brackets are reserved for syntactic
placeholders; write specialized dual or Jacobian actions explicitly with a
transpose, adjoint, or named pairing.

Standing typography follows Chapter 0: italic scalars, bold lowercase row
vectors, bold uppercase matrices, and calligraphic sets. A displayed local
column-vector convention must be announced with `NotationOverride` and listed
in Chapter 0's column-vector table. Counts and dimensions are positive integers
unless a statement says otherwise. `\defeq` marks a definition; subsequent
derived identities use `=`.

## Recurring terminology

| Canonical form | Rule or distinction |
|---|---|
| **key–value cache**; **KV cache** | Spell out on first local use when helpful; use `KV cache` thereafter. Never `KV-cache`. Use “key and value rows or tensors” when naming two objects rather than the cache. |
| **encoder–decoder** | En dash joins equal architectural roles. Preserve ASCII hyphens in slugs, IDs, citation metadata, and literal source titles. |
| **image–text** | En dash joins paired modalities. |
| **vision–language** | En dash joins paired modalities. |
| **query–key**, **key–value**, **winner–loser**, **policy–reference** | En dash joins equal or contrasting roles. Use “query, key, and value” or “key and value” when listing distinct objects. More generally, use conjunctions rather than slash shorthand for reader-facing role lists; reserve `/` for ratios, code paths, URLs, and literal names. |
| **state-space model** | Hyphenate the compound modifier; write “state space” when it is a noun, as in “the state space has dimension …”. The cited coined name **State Space Duality** retains its source spelling and capitalization. |
| **cross-attention**, **self-attention** | Hyphenated compounds. |
| **multi-head**, **feed-forward** | Hyphenated modifiers and established component names. |
| **row-wise**, **token-wise** | Hyphenated adverbs or adjectives. Prefer “per row” or “per token” when it is clearer. |
| **zero-shot** | Hyphenated in reader-facing prose. Preserve `zeroshot` in semantic IDs and filenames. |
| **nonnegative**, **nondifferentiable** | Closed compounds. |
| **autoregressive**, **bidirectional**, **multimodal** | Closed compounds. |
| **query, key, and value** | Use words for the three roles; reserve `Q`, `K`, and `V` for mathematical symbols or an abbreviation introduced in context. |
| **softmax**, **transformer** | Lowercase common nouns except at the start of a sentence or in a title/proper name. |
| **LayerNorm**, **RMSNorm**, **LoRA**, **MoE**, **MLA**, **MQA**, **GQA** | Use these established abbreviations and capitalization after expansion at first substantive use. |

The same first-use rule applies to domain abbreviations such as RLHF, PPO,
FSDP, DDP, OOD, MRR, and KV cache. A title or frontmatter summary may preview an
abbreviation; the chapter body still expands it before relying on it.

## Prose and structural style

- Use first-person plural in exposition. Reserve second person for exercises and
  self-explanation prompts.
- Use one `Where we are` paragraph per chapter. It should orient the reader,
  name the chapter's main moves, and state the destination without becoming a
  theorem inventory.
- Write each chapter-card description as one complete, third-person,
  present-tense sentence stating what the chapter does.
- Use an em dash for an interruption, an en dash for paired terms or ranges, and
  a hyphen for ordinary compound modifiers. Spaces surround an em dash in prose.
- Use American English spellings (`color`, `behavior`, `modeling`) throughout.
- Capitalize an explicit full or shortened chapter name (“the Notation chapter,”
  “the Training chapter”); keep a generic reference (“the previous chapter”)
  lowercase.
- Use the serial comma in lists of three or more items.
- Keep a theorem's hypotheses attached to its claim; do not trade precision for
  a shorter sentence.
- Captions explain the figure's point. `alt` identifies its essential content;
  `desc` gives the structural detail needed to reconstruct it. Captions never
  expose build notes, source syntax, or semantic IDs.
- A term may intentionally differ in a literal quotation, a cited work's title,
  code, a filename, a URL, or a stable semantic identifier. Such strings are
  not evidence of reader-facing inconsistency.

## Review protocol

1. Search all chapter and apparatus sources, not only the chapter being edited.
2. Separate reader-facing prose and mathematics from protected identifiers and
   source titles before changing a match.
3. Check first-use expansions and Chapter 0 after every new abbreviation or
   symbol.
4. Run the content-polish test for unambiguous lexical and macro drift.
5. Finish with a human cross-chapter read; automated checks cannot decide every
   noun/adjective distinction or intentional notation override.
