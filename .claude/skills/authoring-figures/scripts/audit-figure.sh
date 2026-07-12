#!/usr/bin/env bash
# audit-figure.sh <figures/name.tex> [--codex]
# One-command figure QA: build -> collision gate -> (optional) codex multimodal visual audit.
# Exit 0 = clean; 1 = collision (hard fail); 2 = compile error. Codex is advisory (never fails the run).
set -euo pipefail

fig="${1:?usage: audit-figure.sh <figures/name.tex> [--codex]}"
do_codex="${2:-}"

# repo root = 4 levels up from .claude/skills/authoring-figures/scripts/
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../../.." && pwd)"
cd "$root"

name="$(basename "$fig" .tex)"
dir="$(dirname "$fig")"

echo "▶ build $name"
( cd "$dir" && pdflatex -halt-on-error -interaction=nonstopmode "$name.tex" >/dev/null ) \
  || { echo "✗ compile failed"; exit 2; }

echo "▶ collision gate"
python3 scripts/check_figure_collisions.py "$fig" \
  || { echo "✗ collision gate FAILED — fix the crop(s) above, then re-run"; exit 1; }

if [ "$do_codex" = "--codex" ]; then
  echo "▶ codex visual audit (advisory)"
  stem="$(mktemp -u)"; out="${stem}.md"
  pdftoppm -png -r 220 -singlefile "$dir/$name.pdf"      "${stem}"
  pdftoppm -png -r 200 -gray -singlefile "$dir/$name.pdf" "${stem}-gray"
  codex exec -i "${stem}.png" -i "${stem}-gray.png" \
    -s read-only --skip-git-repo-check --ephemeral -c model_reasoning_effort=high -o "$out" \
    -- "You are a senior information-design and STEM-pedagogy reviewer. The two attached images (color, then grayscale) are ONE technical figure for a FORMAL transformer-mathematics textbook. The math and structure are settled; critique PURELY visual quality and readability. Give a one-line VERDICT, then a RANKED list of concrete directly-implementable fixes (specific gap, size, weight, position adjustments), and confirm the grayscale panel proves colour independence (role survives via border and label). No praise padding; do not restate the math." </dev/null \
    || echo "  (codex unavailable — credits/limit? — gate still passed)"
  [ -s "$out" ] && { echo "── codex critique ──"; cat "$out"; }
fi

echo "✓ $name: gate clean"
