---
name: authoring-figures
description: Author consistent, high-quality, collision-free TikZ figures for the transformer-mathematics guide. Use for "make a figure", "draw a diagram", "add a figure to chapter N", "this figure looks off / the text hits a line", or whenever creating or revising any figures/*.tex.
version: 0.2.0
effort: medium
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(pdflatex:*), Bash(pdftoppm:*), Bash(pdftocairo:*), Bash(python3:*), Bash(npm:*), Bash(codex:*)
---

# Authoring Figures

A repeatable discipline for figures that are **pedagogically clear, visually uniform, accessible, and
*provably* collision-free**. It encodes conventions learned the hard way (≈7 painful revisions of one
figure) plus a deterministic QA gate, so future figures start at that quality bar instead of rediscovering
it. Two hard rules underpin everything: **text never touches a line** (enforced by a machine gate, not the
eye), and **no raw coordinates** (relative positioning only).

Every figure loads the shared standard: `\documentclass[tikz,border=6pt]{standalone}` + `\usepackage{transformer-figures}`
(use `border=8pt` when a title/caption rides an edge lane; `10pt` for wide multi-panel figures)
(`figures/transformer-figures.sty` is the source of truth — colours, spacing tokens, styles, and the gate seam
all live there). Full rule-set + rationale: **`references/figure-standard.md`**.

## The standard — the UNIVERSAL layer (applies to *every* figure)

1. **Relative positioning, never raw `(x,y)`.** Place each element `right/above/below = <token> of <neighbour>`
   using the spacing tokens `\tfstagegap` (stage→stage), `\tflabelgap` (label→host), `\tfbranchgap` (branch drop).
   Hand-placed coordinates are what caused the collision whack-a-mole — don't.
2. **White-knockout operation labels welded to their arrow.** A label that names an operation rides its arrow
   as `\draw[tfflow] (a) -- (b) node[midway, tfoplabel]{$…$};`. The `tfoplabel` fill masks the line behind the
   glyphs, so a line **cannot** show through it, and `midway` keeps it off every other line. Never float a wide
   label in the gap between two lines.
3. **Reserved, line-free text lanes.** Titles above, captions/`= …` notes below, legend at the bottom — bands
   with **no connectors routed through them**. A line-free lane can't collide regardless of text width.
4. **Edge dimension labels on FREE edges.** Matrix sizes read off the box's own edges via `\tfdimtop/left/bottom/right`;
   put each on an edge no arrow uses (input arrow enters left → dims go top/right, etc.).
5. **Orthogonal routing.** Right-angle connectors (`tfflow` dataflow, `tfcollect` collector-without-head); minimal
   bends; **no text on any arrow path**. Curves are for decoration, not a formal pipeline.
6. **Grayscale-safe redundant encoding.** Every role = colour **+** border style **+** in-node label, so meaning
   survives greyscale and colour-vision deficiency. Render-check in grayscale. Also put a `%! no-theme` line at
   the top of the `.tex` so the figure renders as a light *card* in dark mode (the site's luminance-based dark
   remap otherwise washes out role symbols against the un-themed pastel fills) — see `references/figure-standard.md`.
7. **Type hierarchy by size *contrast*.** Large box symbols (the heroes) → smaller title → small light captions.
   Contrast carries the hierarchy — do not just make everything big.
8. **Framed heatmaps** for matrix instances: a rounded outer frame (so it reads as a box like the others),
   grayscale-by-magnitude cells, **white numerals on dark cells**, darkest capped ~40–70%.
9. **Notation earns its place.** Enough to follow the computation and track shapes — nothing decorative. The
   adjacent Definition–Theorem carries full rigor; the figure is intuition, not a restatement. Show matrix
   *sizes* (edge dims); do NOT spell out trivial multiplications like `(n×d)(d×n)→n×n`.
10. **No text touches any line.** Non-negotiable, and verified by the collision gate below — not by eyeballing.

## Per-topic vocabulary — EXTEND, don't reinvent

The `.sty` ships the attention vocabulary (Q=purple / K=blue / V=orange with border+label; matrix box; grayscale
heatmap; `×`/`⊕` merge nodes; edge-dim macros). For a **new topic**, add a *documented* role/device to the `.sty`
following the same `colour + border + label` convention (e.g. RNN gate/state roles, SSM state colours, VLM
modality roles) — never hard-code a colour in a figure. Each figure **selects the devices its content needs**;
it is not a clone of another. (Colours route through the `tfText`/`tfInk` seam so the gate can recolour them.)

## Process — run this for every figure

1. **Fidelity spec first** (before drawing): the source theorem/def id; the shapes/dims to show; any concrete
   numeric instance (and **Python-verify those numbers** — deterministic, never guessed); what the figure must
   NOT imply (e.g. "don't let this example read as a general property").
2. **Author** `figures/<name>.tex` from the spec, using the universal layer above (relative positioning,
   white-knockout ops, edge dims, reserved lanes).
3. **Build**: `pdflatex -halt-on-error -interaction=nonstopmode <name>.tex` (from `figures/`), or `npm run build:figures`.
4. **Collision GATE — hard, must be zero**:
   `python3 scripts/check_figure_collisions.py figures/<name>.tex`
   It flips text→magenta, connectors→cyan in one render and fails on any text-within-clearance-of-line pixel,
   saving a `tfgate-<name>.collision-N.png` crop of each offender. **Never proceed on a non-zero gate** — fix and re-run.
5. **Visual self-review** against `references/figure-standard.md`: reading order flows; dimension flow is legible;
   grayscale redundancy holds; hierarchy reads; no decorative notation; numbers match the source. **Look at the
   render** — the gate catches text↔line only, NOT text↔text / box↔box overlap (a label crowded onto a
   neighbour's text passes the gate). Optional codex **visual** audit for a flagship figure (`references/codex-audit.md`).
6. **Pedagogical review — a distinct gate, not the visual one** (`references/pedagogy-review.md`): read the
   figure's chapter section, then apply the rubric — name the ONE idea it must teach; is the visual metaphor apt
   (and does it distort the math?); **adversarially try to MISREAD it** (what wrong idea could a student form,
   and is it prevented?); does it *complement* the prose (intuition) rather than restate the definition (rigor)?
   For a load-bearing figure add the codex **pedagogy-lens** (render + the chapter prose in the prompt — a
   different prompt from the visual audit). Visual polish ≠ teaching: a gate-clean figure can still teach the
   wrong thing.
7. **Done** when: gate = **zero**, numbers Python-verified, visual review clean, **and** the pedagogical review
   passes (a named one-idea, misconception prevented, complements the prose).

## One-command QA

```
scripts/audit-figure.sh figures/<name>.tex            # build → gate → render PNG → report
scripts/audit-figure.sh figures/<name>.tex --codex    # + multimodal codex visual audit
```
Exit non-zero on a collision (or, with `--codex`, prints codex's critique for you to act on). The gate is the
hard gate; codex is advisory. **This wrapper checks VISUAL quality only** — the pedagogical review (step 6,
`references/pedagogy-review.md`) is a separate pass and is not automatable away.

## When to use

Creating a new figure, revising one, or diagnosing a figure that "looks off" / has a text-on-line collision.
For an author-time design *disagreement* you can't resolve, escalate with the codex audit (step 6).

## Example

> "Add a figure of the FFN expansion to ch06."
> 1. Spec: source `def-tf6-ffn`; show `d_model → d_ff → d_model` with `W₁,W₂` shapes; device = width-proportional
>    boxes; must show `d_ff > d_model` visually. 2. Author with edge dims + a white-knockout op-label on the arrow.
> 3. Build. 4. `check_figure_collisions.py` → zero. 5. Self-review. 6. Done.

---
**Related skills**: `/exploring-options`, `/consult`, `/adversarial-review`
