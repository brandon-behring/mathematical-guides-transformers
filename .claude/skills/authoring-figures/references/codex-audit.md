# Codex visual audit (opt-in escalation)

A **multimodal** design/pedagogy critique of a *rendered* figure by codex (`gpt-5.6-sol`). Advisory, not a
gate — use it for a flagship/uncertain figure, or when you and the author disagree on a look. The collision
gate remains the hard gate; codex catches the *aesthetic* issues a pixel gate can't.

## Why the raw call (not a lever wrapper)

The lever wrappers (`ask_model.py`, `/consult`, `/adversarial-review`) are **text-only** — none pass `-i`,
so they can't see an image. A visual audit therefore needs the raw `codex exec`, mirroring the wrappers'
hardening: `-s read-only --ephemeral --skip-git-repo-check`, output to a file with `-o`, and **`</dev/null`**
(codex `exec` deadlocks on a non-TTY empty stdin — this is load-bearing). `codex -i` needs a **raster**, so
render a PNG from the figure PDF first (the pipeline emits SVG/PDF).

## Command

```bash
# 1. render a PNG from the compiled figure
pdftoppm -png -r 220 -singlefile figures/<name>.pdf /tmp/<name>
# (optional) grayscale companion for the accessibility check
pdftoppm -png -r 200 -gray -singlefile figures/<name>.pdf /tmp/<name>-gray

# 2. multimodal codex audit → markdown critique
codex exec -i /tmp/<name>.png -i /tmp/<name>-gray.png \
  -s read-only --skip-git-repo-check --ephemeral \
  -c model_reasoning_effort=high \
  -o /tmp/<name>-codex.md \
  -- "$(cat <PROMPT below>)" </dev/null
```

Then read `/tmp/<name>-codex.md`, resolve material issues, re-run the collision gate, and — for a genuinely
hard case — run a **second** critic (a Claude design-lens agent on the same PNGs) and reconcile the two; the
points *both* raise are the highest-signal (this two-voice cross-exam is what unstuck the flagship figure).

## Prompt template

> You are a senior information-design and STEM-pedagogy reviewer with a sharp eye for visual polish. The
> attached images (color, then grayscale) are ONE technical figure for a FORMAL transformer-mathematics
> textbook. The MATH and STRUCTURE are settled and must NOT change — critique PURELY visual quality and
> readability. Diagnose exactly what feels off and give CONCRETE, directly-implementable fixes. Scrutinize:
> (1) whitespace/negative-space balance; (2) alignment & rhythm (are stages on one optical centerline, gaps
> even?); (3) text hierarchy, sizes, placement — is any label too close to a line or box? (4) line/arrow
> weight consistency & clean junctions; (5) does any heavy element (e.g. a heatmap) overpower the rest;
> (6) does the grayscale panel prove colour-independence (role survives via border+label)? Output a one-line
> VERDICT, then a RANKED list of concrete changes (specific gap/size/weight/position adjustments). No
> praise-padding; do not restate the math.

Tailor the first sentence to the figure. Keep the prompt free of raw single quotes if you inline it (or pass
it via a quoted heredoc as here).
