"""Executable guards for rem-softmax-temperature, def-token-decoding, and
prop-truncated-sampling.

The tests keep token ordering deterministic at ties, verify the temperature
limits, and re-derive truncation normalization, retained odds, nucleus
minimality, endpoint identities, and the chapter's worked example.
"""

from itertools import combinations
import math
import unittest


def softmax(logits: list[float], temperature: float = 1.0) -> list[float]:
    """Stable temperature softmax from def-token-decoding."""
    if not logits or temperature <= 0:
        raise ValueError("softmax needs logits and a positive temperature")
    scaled = [value / temperature for value in logits]
    offset = max(scaled)
    weights = [math.exp(value - offset) for value in scaled]
    normalizer = sum(weights)
    return [weight / normalizer for weight in weights]


def ranked_indices(probabilities: list[float]) -> list[int]:
    """Descending probability, breaking ties by the smaller index."""
    return sorted(
        range(len(probabilities)),
        key=lambda index: (-probabilities[index], index),
    )


def renormalize(probabilities: list[float], support: set[int]) -> list[float]:
    """Evaluate the truncate-and-renormalize operator R_S."""
    if not support:
        raise ValueError("support must be nonempty")
    normalizer = sum(probabilities[index] for index in support)
    return [
        probability / normalizer if index in support else 0.0
        for index, probability in enumerate(probabilities)
    ]


def top_k(probabilities: list[float], k: int) -> tuple[set[int], list[float]]:
    """Return S_k and its renormalized distribution."""
    if not 1 <= k <= len(probabilities):
        raise ValueError("k outside vocabulary")
    support = set(ranked_indices(probabilities)[:k])
    return support, renormalize(probabilities, support)


def top_p(
    probabilities: list[float], threshold: float
) -> tuple[set[int], list[float]]:
    """Return the deterministic minimum sorted prefix reaching threshold."""
    if not 0 < threshold <= 1:
        raise ValueError("threshold outside (0,1]")
    support: set[int] = set()
    mass = 0.0
    for index in ranked_indices(probabilities):
        support.add(index)
        mass += probabilities[index]
        if mass >= threshold:
            break
    return support, renormalize(probabilities, support)


class DecodingTests(unittest.TestCase):
    def test_temperature_limits_include_tied_maxima(self):
        """rem-softmax-temperature converges to tied-max and uniform laws."""
        logits = [2.0, 2.0, 0.0]
        cold = softmax(logits, temperature=1e-3)
        self.assertAlmostEqual(cold[0], 0.5)
        self.assertAlmostEqual(cold[1], 0.5)
        self.assertAlmostEqual(cold[2], 0.0)
        hot = softmax(logits, temperature=1e9)
        for probability in hot:
            self.assertAlmostEqual(probability, 1 / 3, places=8)

    def test_truncation_normalizes_and_preserves_retained_odds(self):
        """prop-truncated-sampling clauses (1)-(2) hold exactly."""
        probabilities = softmax([2.0, 1.0, 0.0, -1.0])
        support, truncated = top_k(probabilities, 2)
        self.assertEqual(support, {0, 1})
        self.assertAlmostEqual(sum(truncated), 1.0)
        self.assertEqual(truncated[2:], [0.0, 0.0])
        self.assertAlmostEqual(
            truncated[0] / truncated[1],
            probabilities[0] / probabilities[1],
        )

    def test_nucleus_support_has_minimum_cardinality(self):
        """prop-truncated-sampling clause (3) beats every smaller subset."""
        probabilities = [0.34, 0.26, 0.20, 0.12, 0.08]
        threshold = 0.75
        support, distribution = top_p(probabilities, threshold)
        self.assertEqual(support, {0, 1, 2})
        self.assertAlmostEqual(sum(distribution), 1.0)
        for size in range(len(support)):
            for candidate in combinations(range(len(probabilities)), size):
                self.assertLess(
                    sum(probabilities[index] for index in candidate),
                    threshold,
                )

    def test_endpoint_rules_and_tie_breaking(self):
        """def-token-decoding and prop-truncated-sampling share exact endpoints."""
        probabilities = softmax([1.0, 1.0, -2.0])
        one_support, one = top_k(probabilities, 1)
        self.assertEqual(one_support, {0})
        self.assertEqual(one, [1.0, 0.0, 0.0])
        all_support, all_k = top_k(probabilities, len(probabilities))
        nucleus_support, all_p = top_p(probabilities, 1.0)
        self.assertEqual(all_support, {0, 1, 2})
        self.assertEqual(nucleus_support, all_support)
        for expected, topk_value, topp_value in zip(probabilities, all_k, all_p):
            self.assertAlmostEqual(expected, topk_value)
            self.assertAlmostEqual(expected, topp_value)

    def test_nucleus_support_adapts_to_the_probability_row(self):
        """A fixed p0 can retain one sharp token or several diffuse tokens."""
        sharp_support, _ = top_p([0.91, 0.03, 0.03, 0.03], 0.9)
        diffuse_support, _ = top_p([0.26, 0.25, 0.25, 0.24], 0.9)
        self.assertEqual(len(sharp_support), 1)
        self.assertEqual(len(diffuse_support), 4)

    def test_chapter_exercise_trace(self):
        """Reproduce Exercise 15.6 from its log-probability logits."""
        base = [0.50, 0.25, 0.15, 0.10]
        logits = [math.log(probability) for probability in base]
        temperature_row = softmax(logits, temperature=2.0)
        expected = [0.3700903444, 0.2616933922, 0.2027068299, 0.1655094336]
        for observed, wanted in zip(temperature_row, expected):
            self.assertAlmostEqual(observed, wanted, places=9)
        support_k, distribution_k = top_k(temperature_row, 2)
        self.assertEqual(support_k, {0, 1})
        self.assertAlmostEqual(distribution_k[0], 0.5857864376, places=9)
        support_p, distribution_p = top_p(temperature_row, 0.8)
        self.assertEqual(support_p, {0, 1, 2})
        self.assertAlmostEqual(distribution_p[2], 0.2429108705, places=9)


if __name__ == "__main__":
    unittest.main()
