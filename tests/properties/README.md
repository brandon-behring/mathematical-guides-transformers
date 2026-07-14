# Property tests — executable guards for the guide's formal claims

Pure-Python (stdlib-only) executable re-derivations and adversarial checks for
the guide's load-bearing formulas, domains, and boundary cases. Each test file
independently asserts the closed forms, limiting cases, or cross-chapter
consistencies the prose claims. A failing test means the prose and the math have
drifted apart.

**Current scope:** the 138-test suite covers BPE merge accounting and
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

The terminal proof audit adds 38 adversarial guards across three partitions:
support-safe KL and causal-mask boundaries, positional/RoPE domains, residual
identity, general-width attention typing and complexity, and $L^p$
equivariance; per-token KL scaling, floating-point ranges, LoRA denominators,
integer checkpointing, ZeRO wire traffic, quantization, FlashAttention traffic,
online-softmax exactness, and exact speculative sampling; and dense recurrent
cost, semiseparable rank, mLSTM readout scope, fixed-window hybrid state,
projected resampler hulls, conditional data processing, VQ gradient routing and
empty cells,
generated-image mask causality, retrieval ties, and per-token perplexity.

**Design.** Tests are self-contained executable assurance specifications, not a
parser for MDX mathematics. `tests/properties/coverage.json` maps each guarded
claim to its test and a normalized statement hash. The checker requires each ID
inside an executable test function, rather than accepting module prose or an
unused inventory tuple. CI therefore forces an explicit coverage review
whenever guarded prose changes; 92 theorem/definition IDs are currently mapped.
Reviewers still verify that each mathematical statement and executable
specification agree.

**Run:**

```bash
python3 -m unittest discover -s tests/properties -p 'test_*.py' -v
```

The suite is stdlib-only and runs in a separate Python 3.13 CI job.
