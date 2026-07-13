# Property tests — numeric guards for the guide's quantitative claims

Pure-Python (stdlib-only) executable re-derivations of the guide's load-bearing
cost formulas. Each test file re-derives a proposition's arithmetic independently
and asserts the closed forms, limiting cases, and cross-chapter consistencies the
prose claims. A failing test means the prose and the math have drifted apart.

**Current scope (Track A foundation):** the roofline cost-per-token equation.
The following correctness PR adds the KV-cache/`d_cache`, three-quantity MoE,
and SSD chunk-balance specifications alongside the prose corrections they guard.
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
