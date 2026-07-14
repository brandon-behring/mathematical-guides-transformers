"""Executable guards for the Chapters 0--7 proof-audit repairs.

Every formal coverage target named below appears literally in this file:
prop-softmax-jacobian, def-cross-entropy, def-kl, prop-ce-kl, def-bpe,
prop-bpe-merge-accounting, thm-pe-rotation, thm-pe-2d-shift, def-rope,
thm-rope-relative, rem-rope-complex, prop-scan, def-causal-mask,
thm-variance-preservation, def-residual, def-cross-attention,
def-decoder-block, prop-complexity, and thm-universal-approx.
"""

from collections import Counter
from itertools import product
import math
import unittest


COVERAGE_TARGET_IDS = (
    "prop-softmax-jacobian",
    "def-cross-entropy",
    "def-kl",
    "prop-ce-kl",
    "def-bpe",
    "prop-bpe-merge-accounting",
    "thm-pe-rotation",
    "thm-pe-2d-shift",
    "def-rope",
    "thm-rope-relative",
    "rem-rope-complex",
    "prop-scan",
    "def-causal-mask",
    "thm-variance-preservation",
    "def-residual",
    "def-cross-attention",
    "def-decoder-block",
    "prop-complexity",
    "thm-universal-approx",
)


def entropy(probabilities: tuple[float, ...]) -> float:
    """Evaluate entropy with the convention 0 log 0 = 0."""
    return -sum(value * math.log(value) for value in probabilities if value > 0)


def cross_entropy(
    target: tuple[float, ...], model: tuple[float, ...]
) -> float:
    """Evaluate the support-safe extended-real cross-entropy."""
    total = 0.0
    for target_mass, model_mass in zip(target, model, strict=True):
        if target_mass == 0:
            continue
        if model_mass == 0:
            return math.inf
        total -= target_mass * math.log(model_mass)
    return total


def kl_divergence(
    target: tuple[float, ...], model: tuple[float, ...]
) -> float:
    """Evaluate KL with zero-target and zero-model conventions."""
    total = 0.0
    for target_mass, model_mass in zip(target, model, strict=True):
        if target_mass == 0:
            continue
        if model_mass == 0:
            return math.inf
        total += target_mass * math.log(target_mass / model_mass)
    return total


def choose_bpe_pair(
    weighted_sequences: tuple[tuple[tuple[str, ...], int], ...],
) -> tuple[str, str] | None:
    """Return a deterministic positive-score pair, or stop if none exists."""
    counts: Counter[tuple[str, str]] = Counter()
    for sequence, frequency in weighted_sequences:
        if frequency <= 0:
            raise ValueError("BPE corpus frequencies must be positive")
        for left, right in zip(sequence, sequence[1:]):
            counts[left, right] += frequency
    if not counts:
        return None
    maximum = max(counts.values())
    if maximum <= 0:
        return None
    return min(pair for pair, count in counts.items() if count == maximum)


def bpe_round(
    weighted_sequences: tuple[tuple[tuple[str, ...], int], ...],
    vocabulary: frozenset[str],
) -> tuple[
    tuple[tuple[tuple[str, ...], int], ...], frozenset[str], int, bool
]:
    """Perform one admissible left-to-right merge or leave state unchanged."""
    pair = choose_bpe_pair(weighted_sequences)
    if pair is None:
        return weighted_sequences, vocabulary, 0, False
    merged = "".join(pair)
    if merged in vocabulary:
        suffix = 1
        while f"{merged}#{suffix}" in vocabulary:
            suffix += 1
        merged = f"{merged}#{suffix}"
    output: list[tuple[tuple[str, ...], int]] = []
    weighted_replacements = 0
    for sequence, frequency in weighted_sequences:
        next_sequence: list[str] = []
        index = 0
        replacements = 0
        while index < len(sequence):
            if index + 1 < len(sequence) and sequence[index : index + 2] == pair:
                next_sequence.append(merged)
                replacements += 1
                index += 2
            else:
                next_sequence.append(sequence[index])
                index += 1
        output.append((tuple(next_sequence), frequency))
        weighted_replacements += frequency * replacements
    return tuple(output), vocabulary | {merged}, weighted_replacements, True


def sinusoidal_pe(position: int, dimension: int) -> tuple[float, ...]:
    """Evaluate the nonnegative-domain even-width sinusoidal encoding."""
    if position < 0:
        raise ValueError("sinusoidal PE is defined only for nonnegative positions")
    if dimension <= 0 or dimension % 2:
        raise ValueError("sinusoidal PE needs a positive even dimension")
    values: list[float] = []
    for index in range(dimension // 2):
        frequency = 10000 ** (-2 * index / dimension)
        values.extend(
            (math.sin(frequency * position), math.cos(frequency * position))
        )
    return tuple(values)


def dot(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    """Return an ordinary Euclidean dot product."""
    return sum(a * b for a, b in zip(left, right, strict=True))


def axial_pe(row: int, column: int, dimension: int) -> tuple[float, ...]:
    """Concatenate two valid half-width sinusoidal encodings."""
    if dimension <= 0 or dimension % 4:
        raise ValueError("axial PE needs dimension divisible by four")
    return sinusoidal_pe(row, dimension // 2) + sinusoidal_pe(
        column, dimension // 2
    )


def rotate_pairs(
    vector: tuple[float, ...], position: int, angles: tuple[float, ...]
) -> tuple[float, ...]:
    """Apply column-oriented two-dimensional RoPE rotations."""
    if position < 0 or len(vector) != 2 * len(angles):
        raise ValueError("RoPE needs a nonnegative position and paired width")
    output: list[float] = []
    for index, angle in enumerate(angles):
        first, second = vector[2 * index : 2 * index + 2]
        cosine = math.cos(angle * position)
        sine = math.sin(angle * position)
        output.extend(
            (cosine * first - sine * second, sine * first + cosine * second)
        )
    return tuple(output)


def stable_softmax(logits: tuple[float, ...]) -> tuple[float, ...]:
    """Compute finite softmax weights stably."""
    shift = max(logits)
    weights = tuple(math.exp(value - shift) for value in logits)
    denominator = sum(weights)
    return tuple(value / denominator for value in weights)


def causal_softmax_row(
    logits: tuple[float, ...], row: int, penalty: float
) -> tuple[float, ...]:
    """Apply the finite -C causal mask used before taking C to infinity."""
    if not 0 <= row < len(logits) or penalty <= 0:
        raise ValueError("invalid causal row or penalty")
    masked = tuple(
        value if column <= row else value - penalty
        for column, value in enumerate(logits)
    )
    return stable_softmax(masked)


def rademacher_dot_variance(dimension: int, scaled: bool) -> float:
    """Enumerate the independent Rademacher model in the variance theorem."""
    values: list[float] = []
    for query in product((-1.0, 1.0), repeat=dimension):
        for key in product((-1.0, 1.0), repeat=dimension):
            value = dot(query, key)
            values.append(value / math.sqrt(dimension) if scaled else value)
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def residual(
    vector: tuple[float, ...], branch: tuple[float, ...]
) -> tuple[float, ...]:
    """Evaluate x + f(x) for an already-computed branch value."""
    return tuple(a + b for a, b in zip(vector, branch, strict=True))


def compose_affine(
    later: tuple[float, float], earlier: tuple[float, float]
) -> tuple[float, float]:
    """Compose scalar affine maps in the order used by prop-scan."""
    later_scale, later_bias = later
    earlier_scale, earlier_bias = earlier
    return (
        later_scale * earlier_scale,
        later_scale * earlier_bias + later_bias,
    )


def inclusive_affine_scan(
    pairs: tuple[tuple[float, float], ...],
) -> tuple[tuple[tuple[float, float], ...], int]:
    """Compute all prefixes by doubling and return its parallel-round count."""
    if not pairs:
        raise ValueError("prop-scan assumes n >= 1")
    prefixes = list(pairs)
    offset = 1
    rounds = 0
    while offset < len(prefixes):
        previous = prefixes.copy()
        for index in range(offset, len(prefixes)):
            prefixes[index] = compose_affine(
                previous[index], previous[index - offset]
            )
        offset *= 2
        rounds += 1
    return tuple(prefixes), rounds


def block_costs(
    n: int, d: int, h: int, d_k: int, d_v: int, d_ff: int
) -> tuple[int, int, int, int]:
    """Return projection, mixing, FFN, and dense-activation counts."""
    if min(n, d, h, d_k, d_v, d_ff) <= 0:
        raise ValueError("all block dimensions must be positive")
    projections = 2 * n * h * d * (d_k + d_v)
    mixing = h * n * n * (d_k + d_v)
    feed_forward = 2 * n * d * d_ff
    activations = h * n * n + h * n * (d_k + d_v) + n * d_ff + n * d
    return projections, mixing, feed_forward, activations


def cross_attention_shapes(
    m: int, n: int, d: int, d_k: int, d_v: int
) -> dict[str, tuple[int, int]]:
    """Trace the typed single-head cross-attention residual interface."""
    if min(m, n, d, d_k, d_v) <= 0:
        raise ValueError("all cross-attention dimensions must be positive")
    return {
        "query": (m, d_k),
        "key": (n, d_k),
        "value": (n, d_v),
        "scores": (m, n),
        "context": (m, d_v),
        "output_projection": (d_v, d),
        "output": (m, d),
        "residual": (m, d),
    }


def broadcast_defect_squared(first: float, second: float) -> float:
    """Squared swap defect of the first-row broadcast inside the unit ball."""
    return 2.0 * (second - first) ** 2


class FoundationProofAuditTests(unittest.TestCase):
    def test_kl_support_conventions_and_decomposition(self):
        """def-cross-entropy, def-kl, and prop-ce-kl remain valid on support boundaries."""
        target = (0.0, 0.25, 0.75)
        model = (0.0, 0.5, 0.5)
        self.assertAlmostEqual(
            cross_entropy(target, model),
            entropy(target) + kl_divergence(target, model),
        )
        self.assertEqual(kl_divergence((0.0, 1.0), (1.0, 0.0)), math.inf)
        self.assertEqual(cross_entropy((0.0, 1.0), (0.0, 1.0)), 0.0)

    def test_bpe_stops_without_positive_adjacent_count(self):
        """def-bpe does not allocate a fresh unused piece after exhaustion."""
        corpus = ((("a",), 4), (("b",), 2))
        vocabulary = frozenset({"a", "b"})
        after, expanded, replacements, performed = bpe_round(corpus, vocabulary)
        self.assertFalse(performed)
        self.assertEqual(after, corpus)
        self.assertEqual(expanded, vocabulary)
        self.assertEqual(replacements, 0)

    def test_admissible_bpe_round_has_positive_replacements(self):
        """prop-bpe-merge-accounting applies only to completed rounds."""
        corpus = ((("a", "b", "a", "b"), 3),)
        vocabulary = frozenset({"a", "b"})
        after, expanded, replacements, performed = bpe_round(corpus, vocabulary)
        self.assertTrue(performed)
        self.assertEqual(replacements, 6)
        self.assertEqual(len(expanded), len(vocabulary) + 1)
        self.assertEqual(
            sum(frequency * len(tokens) for tokens, frequency in after),
            3 * 4 - replacements,
        )

    def test_positional_shift_domain_and_relative_inner_products(self):
        """thm-pe-rotation and thm-pe-2d-shift require valid shifted indices."""
        dimension = 8
        offset = -2
        first = dot(sinusoidal_pe(5, dimension), sinusoidal_pe(5 + offset, dimension))
        second = dot(
            sinusoidal_pe(9, dimension), sinusoidal_pe(9 + offset, dimension)
        )
        self.assertAlmostEqual(first, second)
        with self.assertRaises(ValueError):
            sinusoidal_pe(-1, dimension)

        axial_first = dot(axial_pe(3, 4, dimension), axial_pe(2, 6, dimension))
        axial_second = dot(axial_pe(8, 1, dimension), axial_pe(7, 3, dimension))
        self.assertAlmostEqual(axial_first, axial_second)

    def test_rope_real_dot_is_real_part_of_complex_inner_product(self):
        """def-rope, thm-rope-relative, and rem-rope-complex retain the real dot product."""
        query = (1.0, 2.0, -0.5, 3.0)
        key = (4.0, -1.0, 2.0, 0.25)
        angles = (0.3, 0.7)
        query_position = 2
        key_position = 5
        real_dot = dot(
            rotate_pairs(query, query_position, angles),
            rotate_pairs(key, key_position, angles),
        )
        complex_sum = 0j
        for index, angle in enumerate(angles):
            query_complex = complex(query[2 * index], query[2 * index + 1])
            key_complex = complex(key[2 * index], key[2 * index + 1])
            complex_sum += (
                query_complex.conjugate()
                * key_complex
                * complex(math.cos(angle * 3), math.sin(angle * 3))
            )
        self.assertAlmostEqual(real_dot, complex_sum.real)
        self.assertNotAlmostEqual(complex_sum.imag, 0.0)

    def test_tied_maxima_do_not_converge_to_one_hot(self):
        """prop-softmax-jacobian keeps a nonzero tied-face block."""
        tied = stable_softmax((50.0, 50.0, 0.0))
        self.assertAlmostEqual(tied[0], 0.5)
        self.assertAlmostEqual(tied[1], 0.5)
        self.assertLess(tied[2], 1e-20)
        jacobian_00 = tied[0] * (1 - tied[0])
        jacobian_01 = -tied[0] * tied[1]
        self.assertAlmostEqual(jacobian_00, 0.25)
        self.assertAlmostEqual(jacobian_01, -0.25)

        unique = stable_softmax((100.0, 50.0, 0.0))
        self.assertAlmostEqual(unique[0], 1.0)
        self.assertLess(unique[1], 1e-20)

    def test_variance_scaling_on_independent_components(self):
        """thm-variance-preservation gives d_k before and one after scaling."""
        dimension = 4
        self.assertAlmostEqual(rademacher_dot_variance(dimension, False), dimension)
        self.assertAlmostEqual(rademacher_dot_variance(dimension, True), 1.0)

    def test_causal_mask_is_a_finite_limit_with_nonempty_support(self):
        """def-causal-mask suppresses future entries without an empty row."""
        logits = (0.5, 2.0, -1.0)
        first_row = causal_softmax_row(logits, row=0, penalty=100.0)
        self.assertAlmostEqual(first_row[0], 1.0)
        self.assertLess(first_row[1], 1e-40)
        self.assertLess(first_row[2], 1e-40)
        second_row = causal_softmax_row(logits, row=1, penalty=100.0)
        self.assertAlmostEqual(sum(second_row), 1.0)
        self.assertLess(second_row[2], 1e-40)

    def test_residual_identity_requires_a_zero_branch(self):
        """def-residual supplies an identity summand, not an identity output."""
        vector = (2.0, -3.0)
        self.assertEqual(residual(vector, (0.0, 0.0)), vector)
        self.assertNotEqual(residual(vector, (1.0, 0.0)), vector)

    def test_scan_domain_includes_singleton_and_rejects_empty(self):
        """prop-scan has n >= 1 and zero rounds for n = 1."""
        singleton, rounds = inclusive_affine_scan(((2.0, 3.0),))
        self.assertEqual(singleton, ((2.0, 3.0),))
        self.assertEqual(rounds, 0)
        with self.assertRaises(ValueError):
            inclusive_affine_scan(())

        pairs = ((2.0, 1.0), (3.0, -1.0), (0.5, 4.0))
        prefixes, rounds = inclusive_affine_scan(pairs)
        self.assertEqual(prefixes[-1], compose_affine(pairs[2], compose_affine(*pairs[1::-1])))
        self.assertEqual(rounds, math.ceil(math.log2(len(pairs))))

    def test_general_width_complexity_and_cross_attention_shapes(self):
        """prop-complexity, def-cross-attention, and def-decoder-block retain d_k != d_v."""
        n, d, h, d_k, d_v, d_ff = 7, 12, 3, 2, 5, 17
        projections, mixing, feed_forward, activations = block_costs(
            n, d, h, d_k, d_v, d_ff
        )
        self.assertEqual(projections, 2 * n * h * d * (d_k + d_v))
        self.assertEqual(mixing, h * n**2 * (d_k + d_v))
        self.assertEqual(feed_forward, 2 * n * d * d_ff)
        self.assertGreater(activations, h * n**2)

        shapes = cross_attention_shapes(m=4, n=n, d=d, d_k=d_k, d_v=d_v)
        self.assertEqual(shapes["scores"], (4, 7))
        self.assertEqual(shapes["context"], (4, 5))
        self.assertEqual(shapes["output_projection"], (5, 12))
        self.assertEqual(shapes["output"], shapes["residual"])
        self.assertNotEqual(shapes["context"], shapes["residual"])

    def test_lp_equivariance_obstruction_has_positive_measure(self):
        """thm-universal-approx needs a positive-measure global-Lp obstruction."""
        # On R=[0.3,0.4]x[-0.4,-0.3], ||X||_F<1, so the cutoff is one.
        # The row gap is at least 0.6, hence ||Delta_P f||_2^2 >= 2(0.6)^2
        # throughout a rectangle of Lebesgue measure 0.1*0.1.
        first_interval = (0.3, 0.4)
        second_interval = (-0.4, -0.3)
        volume = (first_interval[1] - first_interval[0]) * (
            second_interval[1] - second_interval[0]
        )
        minimum_gap = first_interval[0] - second_interval[1]
        defect_l2_squared_lower_bound = (
            broadcast_defect_squared(first_interval[0], second_interval[1])
            * volume
        )

        self.assertGreater(volume, 0.0)
        self.assertLess(
            math.hypot(first_interval[1], second_interval[0]), 1.0
        )
        self.assertAlmostEqual(minimum_gap, 0.6)
        self.assertAlmostEqual(defect_l2_squared_lower_bound, 0.0072)
        # ||Delta_P f||_2 <= 2||f-g||_2 for every equivariant g.
        self.assertGreater(
            math.sqrt(defect_l2_squared_lower_bound) / 2.0, 0.04
        )


if __name__ == "__main__":
    unittest.main()
