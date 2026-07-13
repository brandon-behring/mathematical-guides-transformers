"""KV-cache accounting guards prop-kv-cache and prop-kv-memory.

The tests deliberately keep key and value head counts and widths separate.
That general form must survive every specialization to MHA, GQA, and MQA,
while the MLA case keeps its distinct latent-width axis. A small attention
counterexample also guards rem-kv-selection-exactness.
"""

import math
import unittest


def cache_width(h_k: int, d_k: int, h_v: int, d_v: int) -> int:
    """Return d_cache = h_k*d_k + h_v*d_v (prop-kv-cache)."""
    return h_k * d_k + h_v * d_v


def cache_entries(n: int, h_k: int, d_k: int, h_v: int, d_v: int) -> int:
    """Count scalar entries stored by one layer for a length-n request."""
    return n * cache_width(h_k, d_k, h_v, d_v)


def latent_content_width(d_c: int) -> int:
    """Return the persisted content width for the latent-only MLA case."""
    return d_c


def latent_content_entries(n: int, d_c: int) -> int:
    """Count scalar entries in a length-n latent-only content cache."""
    return n * latent_content_width(d_c)


def selected_attention(
    scores: list[float], values: list[float], retained: list[int]
) -> float:
    """Renormalize softmax over exactly the retained cache entries."""
    weights = [math.exp(scores[index]) for index in retained]
    normalizer = sum(weights)
    return sum(
        weight * values[index] for weight, index in zip(weights, retained)
    ) / normalizer


def cache_bytes(
    layers: int,
    n: int,
    bytes_per_element: int,
    h_k: int,
    d_k: int,
    h_v: int,
    d_v: int,
) -> int:
    """Evaluate M_KV = N*n*b*d_cache (prop-kv-memory)."""
    return layers * bytes_per_element * cache_entries(n, h_k, d_k, h_v, d_v)


def heterogeneous_cache_bytes(
    n: int, bytes_per_element: int, layer_widths: list[int]
) -> int:
    """Evaluate M_KV = n*b*sum_l d_cache,l for heterogeneous layers."""
    return n * bytes_per_element * sum(layer_widths)


class KVCacheTests(unittest.TestCase):
    def test_latent_width_is_independent_of_materialized_head_multiplicity(self):
        """MLA's d_c is a separate axis, not a fractional GQA group count."""
        d_c = 512
        self.assertEqual(latent_content_width(d_c), 512)
        self.assertEqual(latent_content_entries(4_096, d_c), 4_096 * 512)
        head_counts = [32, 8, 1]
        materialized = [cache_width(g, 128, g, 128) for g in head_counts]
        latent = [latent_content_width(d_c) for _ in head_counts]
        self.assertEqual(materialized, [8_192, 2_048, 256])
        self.assertEqual(latent, [512, 512, 512])

    def test_strict_selection_need_not_preserve_dense_attention(self):
        """Reusing retained rows exactly does not make omitted rows irrelevant."""
        scores = [0.0, 0.0]
        values = [0.0, 2.0]
        dense = selected_attention(scores, values, [0, 1])
        strict_subset = selected_attention(scores, values, [0])
        self.assertEqual(dense, 1.0)
        self.assertEqual(strict_subset, 0.0)
        self.assertNotEqual(strict_subset, dense)
        self.assertEqual(selected_attention(scores, values, [0, 1]), dense)

    def test_heterogeneous_layers_sum_their_cache_widths(self):
        """The general model formula sums widths instead of multiplying by N."""
        widths = [1_024, 512, 256]
        self.assertEqual(
            heterogeneous_cache_bytes(2_048, 2, widths),
            2_048 * 2 * (1_024 + 512 + 256),
        )

    def test_general_unequal_key_and_value_widths(self):
        """The base formula does not assume equal K/V widths or head counts."""
        h_k, d_k = 3, 64
        h_v, d_v = 2, 96
        self.assertEqual(cache_width(h_k, d_k, h_v, d_v), 384)
        self.assertEqual(cache_entries(7, h_k, d_k, h_v, d_v), 2_688)
        self.assertEqual(cache_bytes(5, 7, 2, h_k, d_k, h_v, d_v), 26_880)

    def test_standard_mha_specializes_to_twice_model_width(self):
        """When h*d_k = h*d_v = d, d_cache=2d and M_KV=2Nndb."""
        layers, n, b = 24, 4_096, 2
        h, d_k, d_v = 32, 128, 128
        d = h * d_k
        self.assertEqual(h * d_v, d)
        self.assertEqual(cache_width(h, d_k, h, d_v), 2 * d)
        self.assertEqual(
            cache_bytes(layers, n, b, h, d_k, h, d_v),
            2 * layers * n * d * b,
        )

    def test_gqa_and_mqa_ratios_cancel_both_head_widths(self):
        """Equal K/V head counts give exact g/h and 1/h cache ratios."""
        h, g, n = 32, 8, 2_048
        d_k, d_v = 64, 80
        mha = cache_entries(n, h, d_k, h, d_v)
        gqa = cache_entries(n, g, d_k, g, d_v)
        mqa = cache_entries(n, 1, d_k, 1, d_v)
        self.assertEqual(gqa * h, mha * g)
        self.assertEqual(mqa * h, mha)

    def test_chapter_15_numeric_example(self):
        """The 80-layer, width-8192 FP16 example occupies exactly 20 GiB."""
        layers, n, b = 80, 8_192, 2
        h, d_k, d_v = 32, 256, 256
        total = cache_bytes(layers, n, b, h, d_k, h, d_v)
        self.assertEqual(cache_width(h, d_k, h, d_v), 16_384)
        self.assertEqual(total, 21_474_836_480)
        self.assertEqual(total, 20 * 2**30)
        self.assertEqual(
            cache_bytes(layers, 2 * n, b, h, d_k, h, d_v),
            2 * total,
        )


if __name__ == "__main__":
    unittest.main()
