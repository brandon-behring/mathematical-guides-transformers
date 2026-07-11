# Figure standard — full rule-set + rationale

The authoritative design reference for `/authoring-figures`. Every rule here was learned from a real failure;
the *why* matters as much as the *what*, so you can apply the intent to a figure the rules don't literally cover.
The executable source of truth is `figures/transformer-figures.sty`; this document explains it.

---

## The two invariants (break these and you loop)

**I1 — Text never touches a line.** The single failure mode that cost ≈7 revisions. Its generator: a *shared
corridor* where wide labels live in the same narrow lane as arrows/collectors. Clearance pinned to one line lets
the label's box sweep across a second, orthogonal line — whack-a-mole. Kill it structurally (I3, I4) and verify
it mechanically (the gate), never by eyeballing a thumbnail (sub-pixel line-through-text is invisible there).

**I2 — No raw `(x,y)` coordinates.** Hand-placed coordinates with mis-estimated gaps produced three collisions in
a row. Use relative positioning (`right/above=<token> of <neighbour>`) so gaps are declared once and consistent.

---

## Layout rules

**Relative positioning + spacing tokens.** `\tfstagegap` (box→box along the pipeline), `\tflabelgap`
(label/title/caption→its host), `\tfbranchgap` (a branch's vertical drop, e.g. K below Q, V below ×). Tune gaps
in the `.sty`, once, for every figure. Position off node anchors and coordinates derived from them (`(a.east)`,
`($(a)!0.5!(b)$)`, `(a |- b)`), never bare numbers.

**White-knockout operation labels.** A label naming an op rides its arrow:
`\draw[tfflow] (a) -- (b) node[midway, tfoplabel]{$QK^\top/\sqrt{d_k}$\\ softmax};`. `tfoplabel` fills with the
page background, so the line is masked *behind* the glyphs — line-through-text is impossible by construction —
and `midway` auto-centres it so it cannot drift onto another line. Ensure the arrow segment is wider than the
label (widen `\tfstagegap` for the label-bearing stage) so the fill doesn't overrun a neighbouring box.

**Reserved text lanes.** Partition the canvas into bands: a middle *flow lane* (only boxes + arrows) and text
lanes above (title) and below (captions, `= …` notes, legend) that carry **no connectors**. Prose in a line-free
lane cannot collide, whatever its width. This also fixes "caption tail bumps the branch box." When a figure
carries title/caption in these edge lanes, give the `standalone` class a generous crop `border` (`border=6pt`,
not `3pt`; `8pt` when the caption is wide or two-plus lines) so edge glyphs don't crowd the crop boundary —
three figures' audits flagged a caption jammed against an edge. A caption should also be no wider than the
figure body: reflow a long formula line into the narrative (`widen d→d_ff …`) rather than letting it set the
bounding-box width and push its own ends toward the side crops.

**Orthogonal routing.** `tfflow` (dataflow, arrowhead) and `tfcollect` (a merge collector = flow minus head).
Right angles, minimal bends, connectors terminate at node borders. Curves read as decorative and invite
collisions; avoid them in a formal pipeline. Place merge junctions *close to their sources* so the collector's
vertical run sits far left, clear of any label.

**Split / merge junction idiom (never stack arrowheads).** For a 1→h fan-out or h→1 fan-in, draw a *bus* with
plain `tfcollect` lines, mark the branch point with a small `tfjoin` dot, and put **exactly one** `tfflow`
arrowhead — on the trunk of a fan-in (the single line entering the target) or at each leaf of a fan-out (the
lines entering the h boxes), never a pile of arrowheads meeting at the junction. Keep the fan geometrically
symmetric: equal branch spacing, mirrored top/bottom lengths, each branch on its box's exact vertical centre,
and the whole bank centred on the trunk axis. (Codex flagged stacked arrowheads + asymmetry as the #1 quality
tell on the MHA figure.) The `tfjoin` dot must be large enough to read in grayscale — `.sty` sets 2.8pt; a
hairline 1.7pt dot vanished at print scale (a second codex audit, on the KV-sharing fan-ins, caught it). A
residual skip rejoins the spine at a `tfadd` ⊕ node (bg-filled, so connectors terminate cleanly at its border).

**Comparison layout (align the shared endpoints).** When two rows/panels contrast variants of the same wiring
(pre- vs post-norm, MHA/GQA/MQA), give both the *identical gap pattern* so the elements they share — input,
tap, output — sit on the same vertical guides and both rows span the same width. The eye then reads the *one*
thing that moved (a box's position) as the difference, instead of being distracted by incidental layout drift.
Use one gap macro (`\newcommand{\gp}{8mm}`) and one box-footprint style (`blk`) across both rows, not per-row
hand-tuning — codex flagged drifting endpoints and size variation as the main tell on the pre/post-norm figure.
A **centred panel title** needs a *named* `\coordinate (p2mid) at ($(a)!0.5!(b)$)` for its x, placed
`at (p2mid |- t1)` to share the other titles' baseline — a raw calc-expr directly left of `|-` silently fails
to take the reference. And leave real room between compared sub-columns: a wire + white-knockout label between
two boxes needs ≈20mm, or the label lands on a neighbour's text.

**Switch-space (2×2) comparison + mask icons.** When a comparison is over *two binary switches* (e.g.
self-attention bidirectional/causal × cross-attention absent/present), the strongest layout is often the
switch space itself — a 2×2 grid whose axes *are* the switches, cells = settings (`tfpanel`), with the unused
setting greyed (`tfpaneloff`) and labelled with its reason. It teaches *why* only the standard settings are
used, not just what they are. Show a categorical attention pattern with `\tfmaskicon{full|causal}` — a small
grid, fully vs lower-triangularly shaded — so "bidirectional vs causal" is *seen* (the icon is shading, so it
survives grayscale natively). Beware the gate-blind text↔text overlap in dense cells, and resolve any axis
subtlety in the caption (e.g. an encoder-decoder in the "causal" row because its *generating* stack is causal).

---

## Shape & dimension rules

**Edge dimension labels (Amidi / tensor-diagram convention).** Read a matrix's size off its own edges via
`\tfdimtop/\tfdimleft/\tfdimbottom/\tfdimright`. Put each dim on a **free** edge — never the edge an arrow uses
(input enters left ⇒ dims on top/right; a box that outputs upward ⇒ dim on the bottom). This is why `\tfdim*`
take an explicit edge. Show *sizes* so the reader tracks shapes in their head; do **not** spell out trivial
multiplications (`(n×d_k)(d_k×n)→n×n`) — that's clutter, and the reader can multiply matrices. The bracket
double-arrow is deliberately the lightest stroke (`0.4pt`, below connectors) and its label sits just *outside*
the bracket (a hair of clearance), so a dimension reads as a measurement, not a connector.

**Dimension-by-size (proportional boxes).** When a figure's payload *is* one dimension growing (FFN's
`d → d_ff = 4d`, an expand/contract), encode it by drawing the box's extent along one axis proportional to the
value — and **hold the other axis constant across all boxes**, so it is *height* (not area/bulk) that carries
the reading. Two constraints follow. (i) A mid-pipeline box has flow on both edges of the encoding axis, so it
**cannot take an edge bracket** without a line crossing an arrow — carry its size with the proportional extent
plus a text label in the free lane above, and reserve the edge brackets for the terminal boxes' free outer
edges. (ii) Keep the proportion honest (a real 4× is worth more than a decorative one) and name the ratio.

**Framed heatmaps for matrix instances.** Draw a concrete example matrix as a rounded-frame grid (so it reads as
a box like Q/K/V/C), shaded by magnitude in **grayscale** (darker = larger; honest, no role-colour confusion),
**white numerals on dark cells**, darkest step capped so the block doesn't overpower the pale boxes. Numbers are
**Python-verified**; mark them approximate (`≈`, "2 dp") and never print an exact `0.00` for a strictly-positive
softmax entry. Keep the *abstract* object (`A`, `n×n`) distinct from the *example* so example-specific structure
(e.g. diagonal dominance) isn't read as a theorem.

---

## Accessibility & typography

**Grayscale-safe redundant encoding.** Role = colour **+** border style **+** in-node label. Q=purple/solid,
K=blue/dashed, V=orange/dotted, each labelled — so meaning survives grayscale and CVD. The label is mandatory
(grayscale is label-dominant); strengthen the weakest border (V's dotted) and darken hairlines for print. Always
render-check a grayscale companion. **Terminal boxes need a dark-enough border to survive grayscale** — a
high-luminance role colour (orange especially) maps to near-white and its border vanishes; the `.sty` gives
terminal/role boxes a darker, heavier border (`orange!78!black`, 0.8pt) and operation boxes a lighter one
(0.45pt), so terminals read as the pipeline's endpoints even without colour.

**Dark mode — render as a light "card".** Put a `%! no-theme` line at the top of every figure `.tex`. The site
otherwise remaps the figure's colours for dark mode by *luminance* — it maps **every** dark colour → light —
which washes out the dark role-box symbols against the (un-remapped) light pastel fills, i.e. light-on-light.
Opting out with `%! no-theme` keeps the figure exactly as designed, and the `.sty`'s `every picture` adds a
white `background rectangle`, so a figure renders as a fully-legible white card on the dark page (light mode
unchanged, white-on-white). Verified: a themed dark render leaves Q/K/V symbols faint; the light card is
crisp. (Alternatives — theme-stable dark symbols, or no-fill/border-only role boxes — either fail against the
luminance remap or change the approved filled-box look. The light card is the working, minimal fix.)

**Stroke-weight hierarchy (print-safe, settled).** The objects out-weight the wiring: role/terminal box borders
(0.8pt) > connectors (`tfflow`/`tfcollect`, 0.7pt) > dimension double-arrows (0.4pt); operation scaffolding
(`tfstruct`, 0.45pt) stays recessive. These values are the settled result of *three* codex audits: the first
two established the hierarchy (equal 0.6pt border/connector read as a flat map); the third (across ffn + block)
showed every stroke a touch thin for textbook reproduction, so the whole ladder was lifted one notch while
keeping the order. Do not keep chasing "lines look faint" past this — a multimodal reviewer scores a figure as
a full-page poster and will always want more ink than a shrunk-in-page figure needs.

**Type hierarchy by contrast.** Box symbols large (heroes), title a step down, captions small and lighter. The
*contrast* carries the hierarchy — don't inflate everything. Route all prose through `tfText` (so the gate can
recolour it, and so the palette is centralized).

**Notation earns its place.** The figure is intuition; the adjacent Definition–Theorem carries the rigor. Include
only what helps the reader follow the computation or track a shape. Cut formal-completeness decoration
(`A𝟙 = 𝟙` *and* "rows sum to 1" is redundant; pick one). Operation labels stay minimal.

---

## The stroke / colour seam (why colours are centralized)

All prose text routes through `\colorlet{tfText}` and all connectors through `\colorlet{tfInk}`/`\tfInkDim`. This
single seam lets the **collision gate** compile a two-colour render (text→magenta, connectors→cyan) with no
per-figure edits, so the gate can separate them. Never hard-code a text/connector colour in a figure — add or use
a `.sty` colorlet. Per-topic role colours (box fills/borders, heatmap) may stay local but should be documented in
the `.sty` (`%! palette-local:` where a legacy figure's colour means something specific).

---

## The collision gate (the mechanical QA)

`scripts/check_figure_collisions.py <fig.tex>` — compiles the figure in `\def\tfgatemode{gate}` (text→magenta,
connectors→cyan), rasterizes high-DPI, dilates the cyan mask by the clearance budget, and **fails on any magenta
pixel within that clearance of cyan**, saving a 3× crop of each offender. Heatmap interiors and box-internal
symbols are excluded by construction (numerals aren't magenta / are centred far from borders); white-knockout
fills erase cyan beneath op-labels (no false positive). It was validated by *catching* a known-bad version and
then *passing* the fixed one. **Zero is the release bar. Do not show a figure until the gate is zero.**
Scope caveat: the gate checks text↔**line** only (magenta text vs cyan connectors). Text↔text and box↔box
overlaps — a label crowded onto a neighbouring box's text, two under-spaced panels colliding — are the same
colour to the gate and pass it. Those are caught only by *looking* at the render, so the visual self-review
is not optional: gate first, then eyes. (Dimension double-arrows `tfInkDim` also ride the cyan seam, and
dimension labels sit just outside their bracket — so edge-dimensioned figures still gate zero in practice; no
`\tfdim*` exclusion is needed.)

---

## Escalation

For a hard/flagship figure, or a look dispute you can't resolve: run the **codex multimodal audit**
(`references/codex-audit.md`), and for the genuinely hard case add a second Claude design-lens critic and
reconcile — the points both raise are the ones to fix.
