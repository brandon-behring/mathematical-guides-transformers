# Pedagogical review — the second gate

The collision gate and the visual review answer *"is this figure clean?"*. They do **not** answer *"does this
figure teach the right thing, and can it be misread?"* — a gate-clean, beautifully-typeset figure can still
teach a falsehood, restate the definition without adding intuition, or invite a confident wrong inference. This
review is the pedagogical analog of the collision gate: run it on every figure, before it ships.

The guide's contract (style-guide): **the figure carries intuition; the adjacent Definition–Theorem carries
rigor.** A figure earns its place only by giving the reader something the prose cannot — a shape, a flow, a
scale, a comparison they can *see*. Judge every figure against that.

---

## The rubric (answer all six, in writing)

1. **One idea.** Name the *single* core intuition this figure must deliver, tied to its source theorem/def.
   If you can't state it in one sentence, the figure is unfocused. Everything in the frame serves that idea;
   anything that doesn't is decoration — cut it.
2. **Apt metaphor.** Is the visual structure the right analogy for the math — and does it distort anything?
   (A 2×2 grid for "two binary switches" is apt; a height-proportional box for `d_ff = 4d` is apt *iff* the
   other axis is held constant so *height*, not area, reads as the quantity.)
3. **Misconception adversarial pass (the core gate).** Actively try to **misread** the figure as an
   uncharitable or first-time student would. List every wrong takeaway it permits, then check each is
   prevented. This is where figures fail. Typical generators of misreading:
   - an *example* read as a *general property* (a diagonal-dominant attention instance → "attention is
     always diagonal"): tag it `example (n=3)`, keep the abstract object present alongside.
   - a *simplification* read as *the whole truth* (enc-dec placed in the "causal" row → "enc-dec has no
     bidirectional attention"): show the missing part (both masks), name it.
   - an *absence* read as *impossible* rather than *unused* (an empty grid cell → "this can't exist"): label
     it "non-standard" **with the reason**.
   - a *proxy* read as *the thing* (box height used for a count → "the layer is physically taller").
4. **Right altitude.** Intuition-first. The figure shows what prose can't (shape/flow/scale/comparison); it is
   **not** a re-typeset of the definition. Notation earns its place — enough to follow the idea, no more.
5. **Complement, not duplicate.** *Read the figure's chapter section.* Does the figure add intuition the prose
   lacks, agree with it exactly (no contradiction in notation, shapes, or claims), and avoid merely repeating
   a sentence as a picture? Note the anchor (`def-…`/`prop-…`/`rem-…`) it pairs with.
6. **Entry + build + hook.** Can a reader enter the figure (an obvious starting point), build understanding in
   a natural order, and leave with one memorable image? If the eye doesn't know where to start, say so.

A figure **passes** only with: a stated one-idea, every listed misconception prevented, and a concrete way it
complements (not restates) its prose.

---

## Mechanism — 2-voice, per figure

1. **Read the chapter section** the figure sits in (the def/theorem + surrounding prose). You cannot judge
   complementarity or fidelity-of-intuition without it.
2. **Claude pass:** answer the six rubric items in writing. The misconception pass is mandatory and adversarial
   — force at least two plausible misreadings and show they're blocked (or fix the figure so they are).
3. **Codex pedagogy-lens** (load-bearing figures, or any the Claude pass leaves uncertain): multimodal, because
   it must *see* the figure **and** read the prose. Raw `codex -i` is required (the lever text wrappers can't
   take an image). **Use a pedagogy prompt, distinct from the visual-audit prompt:**

   ```
   codex exec -i <fig>.png -s read-only --skip-git-repo-check --ephemeral \
     -c model_reasoning_effort=high -o <out>.md -- "You are a STEM educator AND a first-time student. \
     This figure accompanies the textbook passage below. As the EDUCATOR: what is the ONE idea it should \
     teach; does the visual metaphor distort the math; does it COMPLEMENT the passage or merely restate it? \
     As the STUDENT: what would confuse you; what WRONG conclusion might you confidently draw from it? \
     Do NOT critique colours/spacing/typography — a separate pass owns that. Passage: <<<paste the def + \
     surrounding prose>>>" </dev/null
   ```
4. **Reconcile.** Issues **both** voices raise, or any confirmed misreading, are the ones to fix — by
   reworking the figure (preferred) or, if truly unavoidable, a caption that names the boundary. Record the
   figure's one-idea + the misreadings you closed.

---

## Worked misconception checks (from this guide's figures)

- `attention-shapes`: the worked matrix is diagonal-dominant → could read as "attention is identity-like."
  *Blocked by* the `example (n=3)` tag + the abstract `A (n×n)` object kept beside it. Verify it still teaches
  *row-stochastic averaging* (rows sum to 1), not just "a heatmap."
- `kv-sharing`: shrinking the KV row could read as "fewer heads = worse," not the intended *cache ∝ #KV heads*.
  *Blocked by* the `#KV = h/g/1` counts + the cache formula; confirm the cache point lands, not merely "sharing."
- `ffn-expansion`: 4× height could read as distortion or "a taller layer." *Blocked by* equal box widths
  (height alone varies) + the `d_ff = 4d` label; the metaphor is honest only if the proportion is real.
- `block-anatomy`: could read as "LN just moves," missing *why*. Confirm the naked-skip vs LN-on-the-sum
  contrast teaches the gradient-path consequence, not only the position.
- `cross-attention-wiring`: Q/K,V asymmetry is shown — does it also imply the *convexity consequence* (decoder
  outputs are convex combinations of encoder values)? If the prose leans on it, the figure shouldn't fight it.
- `three-architectures` (2×2): enc-dec in the "causal" row → "no bidirectional part"; empty cell → "impossible."
  *Blocked by* both masks in the enc-dec cell + the "non-standard, because…" cell + the row-semantics caption.
