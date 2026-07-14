"""Executable guards for the Chapters 8--15 proof-audit corrections.

The audited targets are named literally so claim-to-test tooling can locate
them without parsing generated names:

``prop-linear-attention-gd``, ``def-bidirectional-scan``,
``prop-ce-kl-training``, ``def-lr-schedule``, ``def-cosine-temp``,
``def-ood-score``, ``rem-bf16``, ``thm-checkpointing``,
``prop-lora-savings``, ``prop-zero-memory``, ``def-affine-quant``,
``prop-quant-error``, ``thm-online-softmax-exact``, ``def-spec-decode``, and
``prop-spec-speedup``.

The tests are deterministic and use only the Python standard library.
"""

import math
import unittest


AUDITED_CLAIM_IDS = (
    "prop-linear-attention-gd",
    "def-bidirectional-scan",
    "prop-ce-kl-training",
    "def-lr-schedule",
    "def-cosine-temp",
    "def-ood-score",
    "rem-bf16",
    "thm-checkpointing",
    "prop-lora-savings",
    "prop-zero-memory",
    "def-affine-quant",
    "prop-quant-error",
    "thm-online-softmax-exact",
    "def-spec-decode",
    "prop-spec-speedup",
)


def entropy(probabilities: list[float]) -> float:
    """Return entropy in nats for a strictly positive finite distribution."""
    return -sum(probability * math.log(probability) for probability in probabilities)


def kl_divergence(left: list[float], right: list[float]) -> float:
    """Return D_KL(left || right) for aligned positive distributions."""
    if len(left) != len(right) or not left:
        raise ValueError("distributions must be nonempty and aligned")
    return sum(p * math.log(p / q) for p, q in zip(left, right))


def expected_token_average_nll(
    data: list[float], model: list[float], sequence_length: int
) -> float:
    """Evaluate prop-ce-kl-training's per-token expected sequence NLL."""
    if sequence_length < 1:
        raise ValueError("sequence length must be a positive integer")
    return -sum(p * math.log(q) for p, q in zip(data, model)) / sequence_length


def legal_checkpoint_count(depth: int) -> int:
    """Choose the better legal integer neighboring sqrt(depth)."""
    if not isinstance(depth, int) or depth < 1:
        raise ValueError("depth must be a positive integer")
    root = math.sqrt(depth)
    candidates = {max(1, math.floor(root)), min(depth, math.ceil(root))}
    return min(candidates, key=lambda count: count + math.ceil(depth / count))


def checkpoint_peak(depth: int, count: int) -> int:
    """Return K + ceil(L/K) for rounded uniform checkpoint segments."""
    if not isinstance(count, int) or not 1 <= count <= depth:
        raise ValueError("checkpoint count must be an integer in [1, depth]")
    return count + math.ceil(depth / count)


def nearest_integer_ties_down(value: float) -> int:
    """Round to nearest, resolving exact half-integer ties downward."""
    lower = math.floor(value)
    upper = math.ceil(value)
    if value - lower <= upper - value:
        return lower
    return upper


def quantize_block(values: list[float], bits: int) -> tuple[list[int], list[float]]:
    """Apply def-affine-quant, including its exact constant-block branch."""
    if not isinstance(bits, int) or bits < 1:
        raise ValueError("bit width must be an integer at least one")
    if not values:
        raise ValueError("a quantized block must be nonempty")
    level_max = 2**bits - 1
    low = min(values)
    high = max(values)
    if low == high:
        return [0 for _ in values], [low for _ in values]

    scale = (high - low) / level_max
    zero_point = min(
        level_max, max(0, nearest_integer_ties_down(-low / scale))
    )
    levels = [
        min(
            level_max,
            max(0, nearest_integer_ties_down(value / scale + zero_point)),
        )
        for value in values
    ]
    reconstructions = [scale * (level - zero_point) for level in levels]
    return levels, reconstructions


def ring_payload_bytes(
    parameter_count: int, workers: int, wire_bytes: int, phases: int
) -> float:
    """Return exact per-worker ring payload for a fixed number of phases."""
    if parameter_count < 1 or workers < 2 or wire_bytes < 1 or phases < 1:
        raise ValueError("ring dimensions and widths must be positive")
    return phases * (workers - 1) * parameter_count * wire_bytes / workers


def flash_io_terms(
    sequence_length: int, width: int, capacity_elements: int, bytes_per_element: int
) -> tuple[float, float]:
    """Return the stream floor and tiled term in the FlashAttention IO bound."""
    if min(sequence_length, width, bytes_per_element) <= 0:
        raise ValueError("sequence length, width, and byte width must be positive")
    if capacity_elements < width:
        raise ValueError("the row-tiling bound requires on-chip capacity Omega(width)")
    stream = bytes_per_element * sequence_length * width
    tiled = (
        bytes_per_element
        * sequence_length**2
        * width**2
        / capacity_elements
    )
    return stream, tiled


def online_softmax_output(scores: list[float], values: list[float]) -> float:
    """Evaluate the scalar online maximum/normalizer/output recurrence."""
    if not scores or len(scores) != len(values):
        raise ValueError("scores and values must be nonempty and aligned")
    maximum = -math.inf
    normalizer = 0.0
    accumulator = 0.0
    for score, value in zip(scores, values):
        next_maximum = max(maximum, score)
        rescale = 0.0 if maximum == -math.inf else math.exp(maximum - next_maximum)
        weight = math.exp(score - next_maximum)
        normalizer = normalizer * rescale + weight
        accumulator = accumulator * rescale + weight * value
        maximum = next_maximum
    return accumulator / normalizer


def learning_rate(step: int, warmup: int, width: int) -> float:
    """Evaluate the warmup/inverse-square-root schedule on its integer domain."""
    if not all(isinstance(value, int) and value >= 1 for value in (step, warmup, width)):
        raise ValueError("step, warmup, and width must be positive integers")
    return width**-0.5 * min(step**-0.5, step * warmup**-1.5)


def cosine_temperature_logit(
    left: tuple[float, ...], right: tuple[float, ...], temperature: float
) -> float:
    """Evaluate temperature-scaled cosine similarity on its stated domain."""
    if len(left) != len(right) or not left or temperature <= 0:
        raise ValueError("vectors must align and temperature must be positive")
    left_norm = math.sqrt(sum(value**2 for value in left))
    right_norm = math.sqrt(sum(value**2 for value in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("cosine similarity excludes zero vectors")
    return sum(a * b for a, b in zip(left, right)) / (
        left_norm * right_norm * temperature
    )


def negative_log_density(density: float) -> float:
    """Use the extended-real -log(0)=+infinity convention."""
    if density < 0:
        raise ValueError("a density cannot be negative")
    return math.inf if density == 0 else -math.log(density)


def speculative_output_distribution(
    target: list[float], draft: list[float]
) -> list[float]:
    """Compute accepted-proposal plus rejection-correction output mass."""
    if len(target) != len(draft) or not target:
        raise ValueError("target and draft distributions must be aligned")
    accepted = [min(p, q) for p, q in zip(target, draft)]
    rejection_probability = 1.0 - sum(accepted)
    positive_residual = [max(p - q, 0.0) for p, q in zip(target, draft)]
    denominator = sum(positive_residual)
    if math.isclose(rejection_probability, 0.0, abs_tol=1e-15):
        return accepted
    if denominator <= 0.0:
        raise AssertionError("a positive rejection branch needs correction mass")
    return [
        base + rejection_probability * residual / denominator
        for base, residual in zip(accepted, positive_residual)
    ]


def speculative_expected_tokens(acceptance: float, candidates: int) -> float:
    """Evaluate prop-spec-speedup's finite geometric expectation."""
    if not 0.0 <= acceptance <= 1.0 or candidates < 1:
        raise ValueError("acceptance and candidate count outside their domains")
    if acceptance == 1.0:
        return float(candidates + 1)
    return (1.0 - acceptance ** (candidates + 1)) / (1.0 - acceptance)


class ProofAuditOptimizationTests(unittest.TestCase):
    """Guard the representative numerical and domain corrections."""

    def test_cross_entropy_kl_identity_retains_one_over_t(self):
        """prop-ce-kl-training retains the per-token 1/T factor."""
        data = [0.2, 0.3, 0.5]
        model = [0.25, 0.25, 0.5]
        sequence_length = 7
        expected = expected_token_average_nll(data, model, sequence_length)
        decomposed = (
            entropy(data) + kl_divergence(data, model)
        ) / sequence_length
        self.assertAlmostEqual(expected, decomposed, places=15)
        self.assertNotAlmostEqual(expected, entropy(data) + kl_divergence(data, model))

    def test_fp16_normal_and_subnormal_floors_are_distinct(self):
        """rem-bf16 distinguishes FP16 normal and subnormal floors."""
        smallest_normal = 2.0**-14
        smallest_subnormal = 2.0**-24
        self.assertAlmostEqual(smallest_normal, 6.103515625e-5, places=20)
        self.assertAlmostEqual(smallest_subnormal, 5.960464477539063e-8, places=24)
        self.assertEqual(smallest_normal / smallest_subnormal, 1024.0)

    def test_lora_uses_two_different_denominators(self):
        """prop-lora-savings distinguishes selected matrices from the full model."""
        matrices, rank, width = 160, 8, 5120
        adapters = 2 * matrices * rank * width
        selected_dense = matrices * width**2
        full_model = 13_000_000_000
        self.assertEqual(adapters, 13_107_200)
        self.assertEqual(selected_dense // adapters, 320)
        self.assertAlmostEqual(adapters / selected_dense, 1.0 / 320.0)
        self.assertAlmostEqual(full_model / adapters, 991.8212890625)

    def test_checkpoint_choice_is_legal_for_non_square_and_prime_depths(self):
        """thm-checkpointing rounds the continuous optimum to legal segments."""
        for depth in (2, 17, 63, 101, 1009):
            with self.subTest(depth=depth):
                count = legal_checkpoint_count(depth)
                self.assertIsInstance(count, int)
                self.assertGreaterEqual(count, 1)
                self.assertLessEqual(count, depth)
                self.assertLessEqual(abs(count - math.sqrt(depth)), 1.0)
                self.assertLessEqual(
                    checkpoint_peak(depth, count), 2.0 * math.sqrt(depth) + 2.0
                )

    def test_quantizer_domains_ties_and_constant_block(self):
        """def-affine-quant and prop-quant-error cover domains, ties, and error."""
        self.assertEqual(nearest_integer_ties_down(2.5), 2)
        self.assertEqual(nearest_integer_ties_down(-0.5), -1)
        levels, reconstructed = quantize_block([-1.0, -0.1, 0.6, 2.0], bits=3)
        self.assertTrue(all(isinstance(level, int) for level in levels))
        self.assertTrue(all(0 <= level <= 7 for level in levels))
        constant_levels, constant_reconstructed = quantize_block([3.25] * 4, bits=1)
        self.assertEqual(constant_levels, [0, 0, 0, 0])
        self.assertEqual(constant_reconstructed, [3.25] * 4)
        self.assertEqual(len(reconstructed), len(levels))
        bound_values = [-3.0, -2.5, 0.5, 4.0]
        _, bounded_reconstruction = quantize_block(bound_values, bits=3)
        scale = (max(bound_values) - min(bound_values)) / (2**3 - 1)
        self.assertTrue(
            all(
                abs(value - restored) <= scale / 2 + 1e-15
                for value, restored in zip(bound_values, bounded_reconstruction)
            )
        )
        with self.assertRaises(ValueError):
            quantize_block([1.0], bits=0)

    def test_ring_payload_uses_wire_width_and_exact_worker_factor(self):
        """prop-zero-memory uses wire width and exact ring worker factors."""
        parameters, workers, wire_bytes = 70_000_000_000, 64, 2
        two_phase = ring_payload_bytes(parameters, workers, wire_bytes, phases=2)
        three_phase = ring_payload_bytes(parameters, workers, wire_bytes, phases=3)
        self.assertEqual(two_phase, 275_625_000_000.0)
        self.assertEqual(three_phase, 413_437_500_000.0)
        self.assertEqual(three_phase / two_phase, 1.5)

    def test_flash_io_includes_compulsory_stream_floor(self):
        """thm-online-softmax-exact scopes its row-tiling traffic to M=Omega(d)."""
        n, d, b = 4096, 128, 2
        for capacity in (d, 16 * d, n * d):
            with self.subTest(capacity=capacity):
                stream, tiled = flash_io_terms(n, d, capacity, b)
                total = stream + tiled
                self.assertGreaterEqual(total, stream)
                self.assertGreaterEqual(tiled, stream)
        stream, tiled = flash_io_terms(n, d, n * d, b)
        self.assertEqual(tiled, stream)
        materialized = b * (n**2 + n * d)
        self.assertGreater(materialized, stream)
        with self.assertRaises(ValueError):
            flash_io_terms(n, d, d - 1, b)

    def test_online_softmax_matches_materialized_attention(self):
        """thm-online-softmax-exact reproduces a stable materialized softmax read."""
        scores = [1_000.0, -1_000.0, 999.0, 997.5]
        values = [2.0, -3.0, 5.0, 11.0]
        shift = max(scores)
        weights = [math.exp(score - shift) for score in scores]
        materialized = sum(
            weight * value for weight, value in zip(weights, values)
        ) / sum(weights)
        self.assertAlmostEqual(
            online_softmax_output(scores, values), materialized, places=15
        )

    def test_bidirectional_dependence_requires_readout_separation(self):
        """def-bidirectional-scan needs Psi to separate changed backward states."""
        forward = 3.0
        backward_before = 2.0
        backward_after = 7.0
        ignore_backward = lambda left, _right: left
        use_both = lambda left, right: left + right
        self.assertNotEqual(backward_before, backward_after)
        self.assertEqual(
            ignore_backward(forward, backward_before),
            ignore_backward(forward, backward_after),
        )
        self.assertNotEqual(
            use_both(forward, backward_before), use_both(forward, backward_after)
        )

    def test_learning_rate_schedule_has_legal_domains_and_peak(self):
        """def-lr-schedule meets continuously at its positive-integer warmup peak."""
        width, warmup = 512, 4_000
        peak = width**-0.5 * warmup**-0.5
        self.assertAlmostEqual(learning_rate(warmup, warmup, width), peak)
        self.assertLess(learning_rate(1, warmup, width), peak)
        self.assertLess(learning_rate(4 * warmup, warmup, width), peak)
        with self.assertRaises(ValueError):
            learning_rate(0, warmup, width)

    def test_cosine_temperature_excludes_zero_vectors_and_nonpositive_scale(self):
        """def-cosine-temp requires nonzero embeddings and positive temperature."""
        self.assertAlmostEqual(
            cosine_temperature_logit((3.0, 4.0), (3.0, 4.0), 0.5), 2.0
        )
        with self.assertRaises(ValueError):
            cosine_temperature_logit((0.0, 0.0), (1.0, 0.0), 1.0)
        with self.assertRaises(ValueError):
            cosine_temperature_logit((1.0, 0.0), (1.0, 0.0), 0.0)

    def test_ood_negative_log_density_uses_extended_real_codomain(self):
        """def-ood-score sends zero fitted density to positive infinity."""
        self.assertEqual(negative_log_density(0.0), math.inf)
        self.assertEqual(negative_log_density(1.0), 0.0)
        with self.assertRaises(ValueError):
            negative_log_density(-0.1)

    def test_speculative_correction_recovers_target_and_alpha_one_branch(self):
        """def-spec-decode and prop-spec-speedup cover correction and alpha=1."""
        target = [0.05, 0.15, 0.30, 0.50]
        draft = [0.40, 0.10, 0.40, 0.10]
        output = speculative_output_distribution(target, draft)
        for observed, expected in zip(output, target):
            self.assertAlmostEqual(observed, expected, places=15)
        self.assertAlmostEqual(sum(output), 1.0, places=15)
        self.assertEqual(speculative_expected_tokens(1.0, candidates=4), 5.0)
        self.assertAlmostEqual(
            speculative_expected_tokens(0.8, candidates=4),
            sum(0.8**power for power in range(5)),
            places=15,
        )


if __name__ == "__main__":
    unittest.main()
