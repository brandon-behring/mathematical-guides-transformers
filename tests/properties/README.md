# Property tests — numeric guards for the guide's quantitative claims

Pure-Python (stdlib-only) executable re-derivations of the guide's load-bearing
cost formulas. Each test file re-derives a proposition's arithmetic independently
and asserts the closed forms, limiting cases, and cross-chapter consistencies the
prose claims. A failing test means the prose and the math have drifted apart.

**Current scope:** eleven quantitative families: BPE merge accounting and
base-stream invariance; associative retrieval, finite-softmax induction, and
the controlled linear-attention/gradient-step identity; KL-regularized reward
optimization, Bradley–Terry/DPO substitution, gradients, and identification
boundaries; separable scaling laws, compute-optimal parameter/data allocation,
and the optimal excess-loss rate; the roofline
cost-per-token equation; KV-cache width
and memory (including unequal key/value widths, latent cached-state accounting,
and a dense-exactness counterexample for strict cache selection); MoE routing
gradients, balancing, per-expert capacity, routing direction, and the
three-quantity accounting of residency/activated compute/ideal traffic;
sparse-attention edge counts, receptive fields, normalization support, and
native branch budgets; SSD chunk-cost balance; decoding transformations
(temperature, top-$k$, and nucleus support and renormalization); and
LayerNorm/RMSNorm Jacobians and norm bounds.
The proof audit later extends this suite; it does not recreate it.

**Design.** Tests are self-contained executable assurance specifications, not a
parser for MDX mathematics. `tests/properties/coverage.json` maps each guarded
claim to its test and a normalized statement hash. CI therefore forces an
explicit coverage review whenever guarded prose changes; reviewers still verify
that the mathematical statement and executable specification agree.

**Run:**

```bash
python3 -m unittest discover -s tests/properties -p 'test_*.py' -v
```

The suite is stdlib-only and runs in a separate Python 3.13 CI job.
