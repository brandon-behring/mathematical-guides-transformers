#!/usr/bin/env python3
"""Collision gate for transformer-figures TikZ figures.

Compiles a figure in "gate" mode (transformer-figures.sty flips prose text -> pure MAGENTA and
connector lines -> pure CYAN in a single render), rasterizes at high DPI, and fails if any text
pixel lies within a clearance margin of a connector pixel.  This catches "text through a line"
deterministically — the failure mode our eyeball QA kept missing.

Heatmap interiors are excluded by construction (their numerals are white/dark, not magenta).
White-knockout op-labels do not false-positive: their white fill erases the cyan beneath them.

Usage:  python3 scripts/check_figure_collisions.py figures/attention-shapes.tex [--clearance-mm 0.35] [--dpi 600]
Exit 0 = clean; exit 1 = collision(s), with crops written as tfgate-<name>.collision-N.png in the system temp dir.
Dimension double-arrows (tfInkDim) also ride the cyan seam; dimension labels sit just outside their bracket, so
edge-dimensioned figures still gate zero (verified across all figures using \tfdim* — no exclusion needed).
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageFilter


def compile_gate(tex_path, dpi):
    d = os.path.dirname(os.path.abspath(tex_path))
    name = os.path.splitext(os.path.basename(tex_path))[0]
    job = f"{name}-gate"
    cmd = ["pdflatex", "-halt-on-error", "-interaction=nonstopmode",
           f"-jobname={job}", rf"\def\tfgatemode{{gate}}\input{{{name}.tex}}"]
    r = subprocess.run(cmd, cwd=d, capture_output=True, text=True)
    pdf = os.path.join(d, f"{job}.pdf")
    if r.returncode != 0 or not os.path.exists(pdf):
        sys.stderr.write(r.stdout[-1500:] + "\n")
        raise SystemExit(f"gate compile failed for {tex_path}")
    png = os.path.join(d, f"{job}.png")
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-singlefile", pdf,
                    os.path.join(d, job)], check=True)
    for junk in (f"{job}.pdf", f"{job}.aux", f"{job}.log"):
        try: os.remove(os.path.join(d, junk))
        except OSError: pass
    return png, name, d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("tex")
    ap.add_argument("--clearance-mm", type=float, default=0.35)
    ap.add_argument("--dpi", type=int, default=600)
    a = ap.parse_args()

    png, name, d = compile_gate(a.tex, a.dpi)
    im = np.asarray(Image.open(png).convert("RGB")).astype(np.int16)
    R, G, B = im[..., 0], im[..., 1], im[..., 2]
    # pure-ish MAGENTA (text) vs CYAN (connectors); tolerant of anti-aliasing
    magenta = (R > 140) & (G < 120) & (B > 140)
    cyan    = (R < 120) & (G > 140) & (B > 140)

    k = max(1, round(a.clearance_mm * a.dpi / 25.4))          # clearance in px
    cyan_dil = np.asarray(
        Image.fromarray((cyan * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * k + 1))) > 0
    hit = magenta & cyan_dil

    n_text, n_line, n_hit = int(magenta.sum()), int(cyan.sum()), int(hit.sum())
    print(f"[{name}] dpi={a.dpi} clearance={a.clearance_mm}mm ({k}px)  "
          f"text_px={n_text} line_px={n_line} collision_px={n_hit}")
    if n_text == 0 or n_line == 0:
        raise SystemExit(f"[{name}] GATE ERROR: no {'text' if not n_text else 'line'} pixels — "
                         "figure not in gate mode? check tfText/tfInk seam.")
    if n_hit == 0:
        print(f"[{name}] ✓ no text↔line collisions")
        os.remove(png)
        return 0

    # cluster the offending pixels into regions, crop each
    ys, xs = np.where(hit)
    order = np.argsort(xs)
    xs, ys = xs[order], ys[order]
    regions = []
    # simple 1-D-ish clustering by x-gap
    cluster_xs, cluster_ys = [xs[0]], [ys[0]]
    for x, y in zip(xs[1:], ys[1:]):
        if x - cluster_xs[-1] > 4 * k:
            regions.append((cluster_xs, cluster_ys)); cluster_xs, cluster_ys = [], []
        cluster_xs.append(x); cluster_ys.append(y)
    regions.append((cluster_xs, cluster_ys))

    full = Image.open(png).convert("RGB")
    print(f"[{name}] ✗ {len(regions)} collision region(s):")
    pad = 6 * k
    for i, (rxs, rys) in enumerate(regions, 1):
        x0, x1 = max(0, min(rxs) - pad), min(full.width, max(rxs) + pad)
        y0, y1 = max(0, min(rys) - pad), min(full.height, max(rys) + pad)
        crop_path = os.path.join(tempfile.gettempdir(), f"tfgate-{name}.collision-{i}.png")
        full.crop((x0, y0, x1, y1)).resize(
            ((x1 - x0) * 3, (y1 - y0) * 3), Image.NEAREST).save(crop_path)
        print(f"    region {i}: bbox=({x0},{y0})-({x1},{y1})  {len(rxs)}px  → {crop_path}")
    os.remove(png)
    return 1


if __name__ == "__main__":
    sys.exit(main())
