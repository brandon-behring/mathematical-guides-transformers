# Sequence-Models Arc Expansion (14 → 19 chapters) — approved design (execute in a fresh session)

## Context

The guide currently tells a pure attention-transformer + vision-language story. This plan expands it
to carry the full pedagogical arc **RNNs → state space models → attention → encoders/decoders across
architecture families → selective SSMs, modern recurrent models & hybrid attention–SSM architectures**,
reorganizing so reading order follows the arc. Exploration confirmed RNN/SSM/hybrid content is
greenfield here (only hooks: `rem-tf5-linear-attention` at `05-architecture-composition.mdx:197`,
kernel-regression view at `02-attention.mdx:40`); enc/dec and KV-cache math are already deep (ch05,
ch09) and must be built on, not duplicated. A complete sibling SSM book (`~/Claude/ssm-foundations`)
exists, but the user chose a **self-contained deep dive** — nothing here may depend on it.

Designed via 20 user decisions over 3 question rounds; **execution is deferred to a fresh session** —
the planning session only parks this document per the Large Task Protocol (proof-audit precedent).

## Locked decisions (20, all user-approved)

1. **Depth**: self-contained deep dive — prove what the guide uses.
2. **Ordering**: RNN + LTI SSMs before attention (ch 02–03); selective/duality + models/hybrids after inference optimizations (ch 13–14), before the VLM chapters.
3. **Scope**: **5 new chapters** — 02 recurrent-networks, 03 state-space-models, 08 encoder-decoder-families, 13 selective-state-spaces, 14 hybrid-architectures. (Grew from 4 when the user chose full theorem-level RWKV/xLSTM/DeltaNet coverage, which forced the ch13 split.)
4. **Audit sequencing**: expand first; the parked proof audit (`docs/plans/active/proof-audit_2026-07-03.md`) then runs over all 19 chapters (it re-enumerates at execution; scope prose gets a touch-up).
5. **ID policy**: rename everything — tf-ids, LO ids (`TF-{ch}.{n}`), exercise headings follow new chapter numbers.
6. **Parts**: 5 numeric parts; **training closes Part 3**.
7. **SSM notation**: semantic macros with consumer `\mathbf` overrides; state dim `d_s`; sequence length stays `n`; never `\seqlen/\statedim/\inputdim`; `\odot` for elementwise.
8. **PR shape**: **two PRs** — PR-1 mechanical, PR-2 content. Each: CI + 3-voice adversarial review + squash-merge (PR #4 precedent).
9. **Title**: "Transformer Mathematics"; description covers the arc.
10. **ch03 keeps 5 LOS**; **HiPPO fully inline** (Legendre lemma from generating function; LegS dynamics ~1–1.5 pp, labeled steps). No 99-appendix.
11. Author to **style guide v0.3** (`~/Claude/mathematical-guides/docs/style-guide-formal-v0.3.md`).
12. **Titles**: descriptive style — "Recurrent Networks and the Seq2Seq Lineage" · "Linear Recurrences and State Space Models" · "Encoders and Decoders Across Architecture Families" · "Selective State Spaces and State Space Duality" · "Modern Recurrent Models and Hybrid Architectures".
13. **ch01 stays intact** — the positional-encoding forward-dangle is handled by one cross-ref margin (weave #2), not restructuring.
14. **SSD depth**: both identities fully proved AND the chunked block algorithm derived as a proposition (`prop-tf13-chunked`, folded into LOS TF-13.4).
15. **RWKV/xLSTM/DeltaNet**: full section-with-theorems treatment (in ch14).
16. **ch13/14 split**: theory (selectivity + duality) | model families + hybrids + synthesis.
17. **Symbols approved**: `d_s`, `κ_j`, scan `•`, chapter-local `T`/`L` in ch13 (mask stays `M`).
18. **Post-authoring notation audit**: independent Codex agent (via `/lever:ask-codex`) sweeps all 19 chapters for notation consistency before PR-2 merges.
19. **Weaves**: all 11, including the optional DETR margin and the two audited-prose softenings in the attention chapter.
20. **Plan-park**: this document, committed to main before any branch work (this commit).

## Target structure

| Part | Ch | Slug (title) | Status |
|---|---|---|---|
| 1 Foundations | 00 | notation | weave |
| 1 | 01 | input-representations | weave |
| 2 Sequence models before attention | 02 | **recurrent-networks** | **NEW** |
| 2 | 03 | **state-space-models** | **NEW** |
| 3 The transformer | 04 | attention (was 02) | renumber+weave |
| 3 | 05 | multi-head-attention (was 03) | renumber+weave |
| 3 | 06 | transformer-block (was 04) | renumber+weave |
| 3 | 07 | architecture-composition (was 05) | renumber+weave |
| 3 | 08 | **encoder-decoder-families** | **NEW** |
| 3 | 09 | training (was 06) | renumber+weave |
| 4 Encoders in practice & efficiency | 10 | detection-encoders (was 07) | renumber+weave |
| 4 | 11 | training-optimizations (was 08) | renumber |
| 4 | 12 | inference-optimizations (was 09) | renumber+weave |
| 4 | 13 | **selective-state-spaces** | **NEW** |
| 4 | 14 | **hybrid-architectures** | **NEW** |
| 5 Vision-language | 15–18 | connectors-resamplers, discrete-visual-tokenization, unified-multimodal-models, multimodal-evaluation (were 10–13) | renumber |

Renumber map `MAP = {2:4, 3:5, 4:6, 5:7, 6:9, 7:10, 8:11, 9:12, 10:15, 11:16, 12:17, 13:18}`. Slugs are number-free → **URLs stable**. `prerequisites:` reference slugs → unaffected. Printed theorem numbers derive from `chapter:` via build-labels → auto-consistent.

Reference material: the gitignored Amidi Super-Study-Guide extraction (`reference-material/`, regen via `build.sh` + MinerU) may inform figures/structure as a **T3 explainer** — never citable as a primary source. The untracked ~38 MB PDF in the repo root must never be committed (stage by explicit path only).

---

## PR-1 — mechanical migration (branch `refactor/sequence-arc-renumber`)

**Commit 1** `refactor(content): rename chapter files for the 19-chapter arc (pure moves)` — 12 `git mv` per MAP (e.g. `02-attention.mdx → 04-attention.mdx`, `10-connectors-resamplers.mdx → 15-connectors-resamplers.mdx`). No content change → 100% similarity, blame survives; site byte-identical (order from `chapter:`, URLs from slugs).

**Commit 2** `refactor(content): renumber chapters and theorem/LO/exercise ids (tf2→tf4 … tf13→tf18)` — single-pass simultaneous rewrite over ALL 14 mdx files (cross-chapter token exists at `00-notation.mdx:62` → `def-tf2-causal-mask`). Sequential per-number sed CORRUPTS (overlapping domain/range); one dict pass:

```python
import re, glob
MAP = {2:4, 3:5, 4:6, 5:7, 6:9, 7:10, 8:11, 9:12, 10:15, 11:16, 12:17, 13:18}
sub = lambda m: str(MAP.get(int(m.group(1)), int(m.group(1))))
for f in glob.glob('src/content/transformers/*.mdx'):
    t = open(f).read()
    t = re.sub(r'-tf(\d+)-', lambda m: f"-tf{sub(m)}-", t)                    # ~475 theorem/XRef/frontmatter ids
    t = re.sub(r'\bTF-(\d+)\.', lambda m: f"TF-{sub(m)}.", t)                 # 55 LO ids
    t = re.sub(r'\bExercise (\d+)\.(?=\d)', lambda m: f"Exercise {sub(m)}.", t)  # 57 headings (all self-referential — verified)
    t = re.sub(r'^chapter: (\d+)$', lambda m: f"chapter: {sub(m)}", t, flags=re.M)
    open(f, 'w').write(t)
```

Verified facts: no bare "tfN" prose, no "Theorem N.M" prose, no `soln-` ids; `tf0`/`tf1` self-map; greedy `\d+` handles `-tf10-`; `01-input-representations.mdx` gets 0 token hits (dry-run census 475/55/57).

**Commit 3** `feat(content): adopt the 5-part structure` — add integer `part:` (1–5 per table) to all 14 files. Verified renderer behavior: numeric parts render "Part N" groups on `/chapters` + sidebar; part ≥ 6 = "Appendices" + letter garbage (never); string parts break sorting (never); monotone assignment → global order unchanged. (Today's build shows a lone "Part 0" group — parts fix that.)

**Commit 4** `feat(config): SSM KaTeX overrides in \mathbf typography; book title/description` — `astro.config.mjs` top-level opts (consumer wins over scaffold-injected `ssmMacros`, verified `dist/index.mjs:1352-1388`; `strict:'error'` fails loudly on undefined macros):

```js
title: 'Transformer Mathematics',
description: 'From recurrent networks and state space models through attention and transformers to hybrid architectures and vision-language models — a rigorous Definition–Theorem–Proof treatment.',
katexMacros: {
  '\\statevec': '\\mathbf{h}', '\\statemat': '\\mathbf{A}', '\\inputmat': '\\mathbf{B}',
  '\\outputmat': '\\mathbf{C}', '\\feedmat': '\\mathbf{D}',
  '\\discA': '\\bar{\\mathbf{A}}', '\\discB': '\\bar{\\mathbf{B}}',
  // \stepsize (Δ), \scanop (⊕) inherit — typography-neutral
},
```

**PR-1 gates**: `npm run validate` + `npm run build` green; `grep -rl 'katex-error' dist/` empty; `npm run build:labels 2>&1 | grep -c 'WARN duplicate'` → 0 (validate misses duplicates); **labels bijection** (save `labels-before.json`; renamed-old-key-set == new-set, count 176); vacancy `grep -rE '\-tf(2|3|8|13|14)-' src/content/transformers/` → empty; ordered-slug list under `part*1000+chapter` == today's order with holes at 2,3,8,13,14; dev-server spot check (Part 1–5 groups, prev/next nav). Main briefly shows non-contiguous chapter numbers after merge — harmless (URLs stable).

---

## PR-2 — content (branch `feat/sequence-models-arc`, off main after PR-1)

**Authoring order 02 → 03 → 08 → 13 → 14** (validate fails on forward XRefs: 08 cites ch02/03/12 ids; 13 cites `prop-tf8-causal-closure`; 14 cites ch13's theorems). One commit per chapter `feat(content): author chNN <title>`, each shipping its mdx + bibliography.bib entries + figure triples (`figures/*.tex` + `.pdf` + `public/figures/*.svg` — CI has no LaTeX; local `npm run build:figures`, pdflatex/pdftocairo verified on PATH).

Every chapter: style guide v0.3 register — `**Where we are.**` opener; concept-image before formal blocks; proofs inline with labeled autonomous steps; self-explanation margins before non-obvious proofs; margins ≤5/section (typed); full numeric trace for the genuinely-new construction; exercises verb-tagged with inline `<SolutionBox>`; frontmatter: title, slug, chapter, part, description, last_verified, rigor_level: rigorous, prerequisites (slugs), notation_introduced, theorems, los.

### ch02 — Recurrent Networks and the Seq2Seq Lineage (`recurrent-networks`, part 2)

Prereqs `[notation, input-representations]`. 4 LOS: define/trace the RNN; derive BPTT; prove the gradient bound + explain the LSTM/GRU remedy; construct seq2seq + additive attention. Cluster (ids referenced by chs 03/04/06/08/09/13/14):
- `def-tf2-rnn` — h_t = φ(W_h h_{t−1} + W_x x_t + b); unrolling as depth-n graph.
- `thm-tf2-bptt` — BPTT: ∂L/∂W as sum over time of chain-rule products (full derivation).
- `thm-tf2-gradient-bound` — ‖∂h_T/∂h_t‖ ≤ ∏_{s>t}‖W_h^⊤diag(φ′)‖ ≤ (σ_max(W_h)·sup|φ′|)^{T−t}; vanishing & exploding regimes, full proof.
- `def-tf2-lstm`, `def-tf2-gru`; `prop-tf2-cec` — constant error carousel: gate-controlled additive path carries gradient ≈ ∏f_s (no repeated W products), full proof for the cell-state path.
- `def-tf2-seq2seq` — RNN encoder-decoder; `prop-tf2-bottleneck` — fixed-vector bottleneck (pigeonhole; returns in ch14's recall bound).
- `def-tf2-additive-attention` — Bahdanau content addressing; remark cliffhanger: keep the addressing, drop the recurrence → ch04.
Worked example: 2-step scalar RNN gradient trace (vanishing visible numerically). Figures: `unrolled-rnn`, `seq2seq-bottleneck`. New bib: elman1990finding, werbos1990bptt, bengio1994learning, hochreiter1997lstm, cho2014gru, sutskever2014seq2seq, bahdanau2015attention, pascanu2013difficulty. 5–6 exercises. Vision margin: modality-blind sequences.

### ch03 — Linear Recurrences and State Space Models (`state-space-models`, part 2)

Prereqs `[notation, input-representations, recurrent-networks]`. **5 LOS** (approved): ZOH; recurrence⇄convolution⇄scan; gradients/eigenvalues; HiPPO; LTI limitation. Cluster:
- `def-tf3-ssm` — continuous LTI quintuple (A,B,C,D), state dim d_s (Kalman).
- `thm-tf3-zoh` — Ā = e^{ΔA}, B̄ = A^{−1}(e^{ΔA}−I)B; full proof (integrating factor, term-by-term integration).
- `thm-tf3-conv-recurrence` — y = κ ∗ u, κ_j = C Ā^j B̄ (+D); full proof by induction.
- `def-tf3-scan-op` + `prop-tf3-scan` — (a₂,b₂)•(a₁,b₁) = (a₂a₁, a₂b₁+b₂); associativity proof **written so it never uses time-invariance** (ch13 reuses verbatim); ⌈log₂n⌉ rounds.
- Gradient/eigenvalue proposition — ∂h_T/∂h_t = Ā^{T−t}; |μ| = e^{Δ·Reλ}; controlled timescales vs ch02's bound; non-normal transient warning margin.
- `lem-tf3-legendre` + `thm-tf3-hippo-legs` — **fully inline** HiPPO-LegS (online L²(ω) projection; coefficient dynamics, ~1–1.5 pp, four labeled steps); `prop-tf3-legs-nplr` (−A₊ + ½bb^⊤ = −½I + skew) → S4/S4D/S5 parameterization.
- `prop-tf3-lti-obstruction` — LTI ⇒ linear+time-invariant ⇒ no content-dependent selection (explicit selective-copy witness, additivity fails numerically); `rem-tf3-toward-selectivity` — two escapes: attention (ch04) or input-dependent (Δ,B,C) (ch13). **The book's central cliffhanger.**
Worked example `ex-tf3-impulse-trace`: d_s=2, A=diag(−1,−0.1), Δ=0.5 → Ā≈diag(.6065,.9512), B̄≈(.3935,.4877); impulse response y₀..y₂ ≈ (.8812,.7026,.5861) computed twice (recurrence & kernel). Figures: `ssm-three-faces`, `hippo-projection`. New bib: kalman1960filtering, gu2020hippo, gu2022s4, gu2022s4d, smith2023s5, blelloch1990prefix (+opt ladner1980parallel, cooley1965fft). 6 exercises (incl. 3×3 LegS compute).

### ch08 — Encoders and Decoders Across Architecture Families (`encoder-decoder-families`, part 3)

Prereqs `[notation, recurrent-networks, state-space-models, attention, architecture-composition]`. 4 LOS. Abstracts ch07's two switches over any **sequence mixer**:
- `def-tf8-mixer`, `def-tf8-causal` — causality as **prefix-consistency**: F_n(X)_{1:m} = F_m(X_{1:m}).
- `prop-tf8-causal-instances` (masked attention ✓, RNN/SSM ✓, unmasked ✗ with 2-token witness); `prop-tf8-causal-closure` (composition, position-wise, residual).
- `def-tf8-patterns` + `prop-tf8-instantiations` — encoder/decoder/enc-dec over the mixer; 3×3 instantiation table (transformer ch07, RNN seq2seq ch02, SSM decoder ch03).
- `thm-tf8-one-pass` — causal stack ⇒ all n next-token conditionals from one evaluation; fails bidirectionally. `prop-tf8-sequential-depth` — RNN Θ(n), SSM Θ(log n), attention Θ(1) matmuls (honest scope: standard evaluation circuits).
- `def-tf8-bidirectional-scan` (Schuster–Paliwal); attention bidirectional by not masking; forfeits prefix-consistency.
- `def-tf8-mlm` + `ex-tf8-incompatible-conditionals` + `rem-tf8-pseudolikelihood` — worked example: explicit 2-token conditional tables no joint realizes.
- `prop-tf8-prefix-reuse` (the KV-cache is correct *because of this*); `def-tf8-prefix-lm` (block mask); `rem-tf8-conditioning-routes`; `rem-tf8-decoder-only` — synthesis (4 proved ingredients, no new claims).
Figure: `architecture-lattice`. New bib: schuster1997bidirectional, lewis2020bart, dong2019unilm, besag1975pseudolikelihood, wang2022architecture. 6 exercises.

### ch13 — Selective State Spaces and State Space Duality (`selective-state-spaces`, part 4)

Prereqs `[notation, recurrent-networks, state-space-models, attention, architecture-composition, encoder-decoder-families, inference-optimizations]`. 4 LOS: selectivity+gating; selective scan; linattn⇄RNN duality; SSD + chunked cost. Cluster:
- `def-tf13-selective-ssm` — Mamba: Δ_t = softplus(x_t w_Δ+b), B_t = x_tW_B, C_t = x_tW_C; Ā_t = e^{Δ_tA}; **honesty note**: B̄_t ≈ Δ_tB_t is first-order ZOH (agreement when Δ_t‖A‖≪1 — warning margin).
- `prop-tf13-not-lti` — escapes `prop-tf3-lti-obstruction`; `ex-tf13-selective-copy` — full trace: d_s=1, a=−1, g_t = 1−e^{−Δ_t} ≈ (.9502,.00995,.00995) → write-once-hold vs LTI smearing.
- `prop-tf13-gate-equivalence` — scalar exact-ZOH: h_t = (1−g_t)h_{t−1} + g_tu_t — the GRU convex combination (ch02 returns).
- `prop-tf13-selective-scan` — ch03's associativity proof never used time-invariance ⇒ log-depth survives; the convolution face dies.
- `thm-tf13-linattn-rnn` — causal linear attention ≡ matrix-state recurrence S_t = S_{t−1} + φ(k_t)v_t^⊤ (+γ-decay variant covering RetNet-style retention), O(Dd_v) state, O(1)/token; upgrades `rem-tf7-linear-attention`; full proof.
- `def-tf13-transfer-matrix` + `thm-tf13-semiseparable` — T_{ij} = C_i(∏Ā_s)B̄_j; strictly-sub-diagonal submatrices have rank ≤ d_s (full proof, diagonal case, cumulative-decay col×row factorization).
- `thm-tf13-ssd` — scalar decay: T = L ⊙ (CB^⊤)diag(Δ), L 1-semiseparable — the selective SSM **is** masked linear attention; full proof.
- `prop-tf13-chunked` — **derived block algorithm** (decision 14): partition into n/c chunks; intra-chunk = masked matmul O(nc·d) via the SSD form; cross-chunk = scan over chunk-summary states O((n/c)·d_s·d); total cost + the balancing chunk size. Proof from the semiseparable factorization.
Notation note: T and L chapter-local (mask stays M). Figure: `semiseparable-mask`. New bib: gu2023mamba, dao2024ssd (katharopoulos2020transformers exists). 6 exercises (scan, gate, linattn, rank bound, T-vs-scan verify, chunked-cost compute).

### ch14 — Modern Recurrent Models and Hybrid Architectures (`hybrid-architectures`, part 4)

Prereqs `[notation, recurrent-networks, state-space-models, attention, architecture-composition, encoder-decoder-families, inference-optimizations, selective-state-spaces]`. 4 LOS: map RWKV/mLSTM onto the matrix-state machinery; prove delta rule = online SGD; derive the recall/state pigeonhole; derive decode-state accounting + compare production hybrids. Cluster:
- `def-tf14-rwkv` + `prop-tf14-rwkv-linattn` — RWKV's WKV recurrence (decayed numerator/denominator sums, per-channel decay, current-token bonus) ≡ decayed linear attention: the (S_t, z_t) pair of `thm-tf13-linattn-rnn` with elementwise decay; proof by unrolling both.
- `def-tf14-mlstm` + `prop-tf14-mlstm-gated-state` — xLSTM's mLSTM cell C_t = f_tC_{t−1} + i_tv_tk_t^⊤ (+ normalizer state) ≡ gated matrix-state recurrence; data-dependent scalar gates = selectivity in the sense of `prop-tf13-gate-equivalence`; exponential-gating stabilization stated.
- `def-tf14-delta` + `thm-tf14-delta-descent` — delta rule S_t = S_{t−1}(I − β_tk_tk_t^⊤) + β_tv_tk_t^⊤ is exact online gradient descent on ½‖Sk_t − v_t‖² at rate β_t; full proof; corollary: Gated DeltaNet = decay + delta step.
- `prop-tf14-state-recall` — pigeonhole: exact K-pair associative recall needs ≥ K log₂|V| bits of decode state; recurrent state O(d_s d) independent of n vs the KV-cache's lossless 2nd/layer — `prop-tf2-bottleneck` returns as the arc's closing symmetry.
- `def-tf14-swa` (first formal sliding-window definition in the book), `def-tf14-hybrid-stack` (interleaved, fraction f attention; ch08 causality theorems apply verbatim), `prop-tf14-decode-state` — M = N[f·2wd + (1−f)d_s d]b; worked numbers: N=32, d=4096, w=1024, d_s=16, b=2, n=65,536 → 34.4 GB full attention vs 0.30 GB at f=1/8 (~115×).
- `rem-tf14-design-space` — production table (Jamba, Griffin, Samba, Zamba, ~8%-attention finding), citing RWKV/xLSTM/DeltaNet formally; closing paragraph: the arc as one design space with two currencies — state size and content addressing.
Vision margin: Vision Mamba bidirectional/2-D scans (encoder pattern per `def-tf8-bidirectional-scan`). Figure: `hybrid-interleave`. New bib: peng2023rwkv, beck2024xlstm, schlag2021fastweight, yang2024deltanet, sun2023retnet (margin), lieber2024jamba, de2024griffin, ren2024samba, waleffe2024hybrid, zhu2024vim, jelassi2024copying (+opt arora2024based). 6 exercises.

### Weave commit — `feat(content): weave sequence-model cross-references into existing chapters`

All 11 approved (ids post-rename):
1. **00-notation**: dimension row `d_s`; operator rows (A,B,C,D,Δ), (Ā,B̄), scan `•` → "State Space Models"; conventions sentence (bold h_t state vs italic h heads); opener "specific to transformers" → "to sequence models".
2. **01-input-representations** (~56): cross-ref margin — recurrence carries order (no injected position, → ch02); attention processes sets, which is why PE exists (→ ch04).
3. **04-attention** opener (~28): soften "the transformer's one genuinely new operation" — attention was born inside the RNN encoder-decoder (XRef `def-tf2-additive-attention`).
4. **04-attention** (~40): `rem-tf4-addressing-lineage` — Bahdanau already had softmax content addressing; dot-product swaps the additive kernel and deletes the recurrent controller; kernel-regression covers both.
5. **05-multi-head-attention** (~133): margin — MQA/GQA shrink the cache by g/h but it still grows with n; removing n-dependence is the recurrent route (`prop-tf14-decode-state`).
6. **06-transformer-block** (~156): depth-direction product mirrors ch02's time-direction product; the identity term is the LSTM gate path's architectural cousin (`prop-tf2-cec`).
7. **07-architecture-composition** `rem-tf7-three-archs` (~126): neither switch mentions attention; ch08 abstracts both (`def-tf8-patterns`).
8. **07-architecture-composition** `rem-tf7-linear-attention` (~202): the running sums are a recurrent state; `thm-tf13-linattn-rnn` makes it exact, `thm-tf13-ssd` generalizes with decay.
9. **09-training** (autoregressive sidenote + teacher forcing ~137): factorization first served RNN seq2seq (`def-tf2-seq2seq`); one fast pass needs a parallel mixer (`thm-tf8-one-pass`, `prop-tf8-sequential-depth`).
10. **12-inference-optimizations** (~81, ~123): cache correctness = `prop-tf8-prefix-reuse`; 2Nndb is the price of lossless prefix memory vs O(d_s d) state and `prop-tf14-state-recall`'s cost.
11. **10-detection-encoders**: margin — DETR's encoder as the layer-agnostic encoder pattern (`def-tf8-patterns`).

### Docs commit — `docs: refresh README, CLAUDE.md, authors page + proof-audit scope`

- **CLAUDE.md**: style-guide pointer → `~/Claude/mathematical-guides/docs/style-guide-formal-v0.3.md` (fixes version + base path); scaffold "v4.2.0" → 4.26+; describe the 19-chapter/5-part arc; note the SSM macro overrides.
- **README.md**: full status rewrite (currently claims only ch00+02 exist, cites deleted appendix, links v0.1); arc-inclusive scope; drop stale manual-pdflatex instruction.
- `src/content/frontmatter/authors.mdx` (v0.1 link + scope phrase), `src/content.config.ts` header comment (→ v0.3), `package.json` description.
- `docs/plans/active/proof-audit_2026-07-03.md`: corpus note superseded by the 19-chapter arc (re-measure at execution); batches 14 → 19; one line recording the id renames.
- Move this plan to `docs/plans/implemented/` at completion. **Never** rewrite historical docs (`docs/audits/*`, `docs/plans/implemented/vlm-*`).

---

## Verification (per-commit gate + final)

```bash
npm run validate && npm run build            # XRef/Cite/Figure checks + full build
grep -rl 'katex-error' dist/ | wc -l         # 0
npm run build:labels 2>&1 | grep -c 'WARN duplicate'   # 0 (validate misses duplicates)
# prereq-DAG check (validate misses it): every prerequisites entry is an existing slug
```
Per new chapter: labels count strictly grew; all frontmatter `theorems:` ids in labels.json. **Notation audit (decision 18)**: after ch14 lands, delegate to an independent Codex agent via `/lever:ask-codex` — sweep all 19 chapters against 00-notation's standing tables (one referent per symbol, chapter-local declarations present, SSM notation vs existing conventions); fix findings before PR-2 merge. Final: dev-server — Part 1–5 groups, 19 cards, sidebar matches, new chapters render (numbering matches `chapter:`, figures theme in dark mode, solutions expand); pagefind finds a new-chapter term; `npm run pdf` smoke; `git log --follow` on one renamed file. PRs: CI green, 3-voice adversarial review, squash-merge.

## Key risks (mitigations built in)

- **Sequential-replace corruption** → single-pass dict script + labels bijection assert.
- **Duplicate/missed ids** → vacancy grep (tf2|tf3|tf8|tf13|tf14) + WARN-duplicate grep + validate's 367-XRef net.
- **Forward-XRef build breaks** → authoring order 02→03→08→13→14; notation-table XRefs land in the weave commit.
- **KaTeX macros** → consumer-wins overrides; `strict:'error'`; never `\seqlen/\statedim/\inputdim`.
- **Parts** → numeric 1–5 only (≥6 = "Appendices" + broken letters; strings break sort).
- **CI has no LaTeX** → commit .tex+.pdf+.svg per convention.
- **Untracked ~38 MB PDF** → stage explicitly by path, never `git add -A`.
- **Astro content-layer cache ghosts** (dev only) → `rm -rf .astro`.

## Follow-ups (out of scope)

- Family-hub README row for the transformers guide (separate repo commit).
- Proof audit over all 19 chapters in a fresh session (decision 4).
- Scaffold issue #177 (ssmMacros export) — override block is forward-compatible.
- Update auto-memory (arc-expansion status; proof-audit scope note).
