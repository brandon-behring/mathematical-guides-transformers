"""Executable guards for Chapter 17 sparse-attention accounting.

The tests exercise def-sparse-attention, prop-sparse-edge-complexity,
def-swa, prop-swa-edge-cache, prop-swa-receptive-field,
prop-static-sparse-counts, def-sparsemax, prop-sparsemax-support,
def-nsa-branches, and prop-nsa-work.
"""

import math
import unittest


def validate_supports(supports: list[set[int]]) -> None:
    """Check that every query has a nonempty, in-range retained-key set."""
    if not supports:
        raise ValueError("attention needs at least one query")
    length = len(supports)
    for support in supports:
        if not support:
            raise ValueError("every sparse-attention row must retain one key")
        if any(key < 1 or key > length for key in support):
            raise ValueError("retained key lies outside the sequence")


def sparse_edge_count(supports: list[set[int]]) -> int:
    """Return m_E = sum_i r_i from def-sparse-attention."""
    validate_supports(supports)
    return sum(len(support) for support in supports)


def attention_core_coordinates(
    supports: list[set[int]], key_width: int, value_width: int
) -> tuple[int, int, int]:
    """Count prop-sparse-edge-complexity score/value coordinates and weights."""
    if key_width <= 0 or value_width <= 0:
        raise ValueError("head widths must be positive")
    edges = sparse_edge_count(supports)
    return edges * key_width, edges * value_width, edges


def causal_window_supports(length: int, window: int) -> list[set[int]]:
    """Enumerate the one-sided last-w convention in def-swa."""
    if length <= 0 or window <= 0:
        raise ValueError("length and window must be positive")
    return [
        set(range(max(1, query - window + 1), query + 1))
        for query in range(1, length + 1)
    ]


def sliding_window_closed_form(length: int, window: int) -> int:
    """Exact causal sliding-window edge count, including w >= n."""
    effective = min(length, window)
    return length * effective - effective * (effective - 1) // 2


def sliding_window_cache_elements(decoded: int, window: int, cache_width: int) -> int:
    """Return the prop-swa-edge-cache cap after decoded positions."""
    if decoded < 0 or window <= 0 or cache_width <= 0:
        raise ValueError("decoded count must be nonnegative; widths must be positive")
    return min(decoded, window) * cache_width


def structural_receptive_field(
    length: int, window: int, layers: int, position: int
) -> set[int]:
    """Compose causal-window graph neighborhoods backward through the stack."""
    if not 1 <= position <= length or layers < 0:
        raise ValueError("position and depth outside their domains")
    supports = causal_window_supports(length, window)
    reachable = {position}
    for _ in range(layers):
        reachable = set().union(*(supports[row - 1] for row in reachable))
    return reachable


def dilated_support(position: int, window: int, dilation: int) -> set[int]:
    """One causal dilated row from prop-static-sparse-counts."""
    if position <= 0 or window <= 0 or dilation <= 0:
        raise ValueError("dilated-support arguments must be positive")
    return {
        position - step * dilation
        for step in range(window)
        if position - step * dilation >= 1
    }


def factorized_edge_bound(length: int, block: int) -> int:
    """Return n*(b+ceil(n/b)) for the local-plus-strided pattern."""
    if length <= 0 or block <= 0:
        raise ValueError("length and block must be positive")
    return length * (block + math.ceil(length / block))


def block_sparse_edge_bound(length: int, block: int, key_blocks: int) -> int:
    """Return ceil(n/b)*rho*b^2 from prop-static-sparse-counts."""
    if length <= 0 or block <= 0 or key_blocks <= 0:
        raise ValueError("block-sparse arguments must be positive")
    return math.ceil(length / block) * key_blocks * block * block


def designate_global_rows(
    supports: list[set[int]], global_rows: set[int]
) -> list[set[int]]:
    """Add bidirectional edges for global rows chosen among existing rows."""
    validate_supports(supports)
    length = len(supports)
    if any(row < 1 or row > length for row in global_rows):
        raise ValueError("global row lies outside the sequence")
    augmented = [set(support) | global_rows for support in supports]
    for row in global_rows:
        augmented[row - 1] = set(range(1, length + 1))
    return augmented


def sparsemax(logits: list[float]) -> list[float]:
    """Evaluate def-sparsemax through the threshold in prop-sparsemax-support."""
    if not logits:
        raise ValueError("sparsemax needs at least one logit")
    ordered = sorted(logits, reverse=True)
    prefix = 0.0
    support_size = 0
    support_sum = 0.0
    for rank, value in enumerate(ordered, start=1):
        prefix += value
        if 1 + rank * value > prefix:
            support_size = rank
            support_sum = prefix
    threshold = (support_sum - 1) / support_size
    return [max(value - threshold, 0.0) for value in logits]


def nsa_branch_sizes(
    query: int,
    compression_block: int,
    compression_stride: int,
    selected_blocks: int,
    selected_width: int,
    window: int,
) -> tuple[int, int, int]:
    """Return c_t, s_t, u_t from def-nsa-branches at their maximum budgets."""
    if min(
        query,
        compression_block,
        compression_stride,
        selected_blocks,
        selected_width,
        window,
    ) <= 0:
        raise ValueError("NSA branch parameters must be positive")
    compressed = max(0, 1 + math.floor((query - compression_block) / compression_stride))
    selected = min(query, selected_blocks * selected_width)
    local = min(query, window)
    return compressed, selected, local


def nsa_support_count(
    length: int,
    compression_block: int,
    compression_stride: int,
    selected_blocks: int,
    selected_width: int,
    window: int,
) -> int:
    """Sum N_t with branch multiplicity, as in prop-nsa-work."""
    return sum(
        sum(
            nsa_branch_sizes(
                query,
                compression_block,
                compression_stride,
                selected_blocks,
                selected_width,
                window,
            )
        )
        for query in range(1, length + 1)
    )


def nsa_asymptotic_upper_terms(
    length: int,
    compression_stride: int,
    selected_blocks: int,
    selected_width: int,
    window: int,
) -> tuple[float, int]:
    """Exercise form n(n+1)/(2*delta) and n*(r*b+w), omitting +n."""
    compression = length * (length + 1) / (2 * compression_stride)
    selected_and_window = length * (selected_blocks * selected_width + window)
    return compression, selected_and_window


class SparseAttentionTests(unittest.TestCase):
    def test_general_edge_count_and_work_follow_retained_pairs(self):
        """def-sparse-attention and prop-sparse-edge-complexity use m_E."""
        supports = [{1}, {1, 2}, {1, 3}, {2, 4}]
        self.assertEqual(sparse_edge_count(supports), 7)
        self.assertEqual(attention_core_coordinates(supports, 8, 5), (56, 35, 7))

    def test_dense_causal_count_is_triangular(self):
        """The dense specialization of prop-sparse-edge-complexity is n(n+1)/2."""
        length = 17
        supports = [set(range(1, query + 1)) for query in range(1, length + 1)]
        self.assertEqual(sparse_edge_count(supports), length * (length + 1) // 2)

    def test_sliding_window_formula_and_endpoints(self):
        """prop-swa-edge-cache guards both edge and cache formulas."""
        for length in range(1, 20):
            for window in range(1, 25):
                with self.subTest(length=length, window=window):
                    observed = sparse_edge_count(causal_window_supports(length, window))
                    self.assertEqual(observed, sliding_window_closed_form(length, window))
        self.assertEqual(sliding_window_closed_form(8, 1), 8)
        self.assertEqual(sliding_window_closed_form(8, 8), 36)
        self.assertEqual(sliding_window_cache_elements(2, 5, 128), 256)
        self.assertEqual(sliding_window_cache_elements(20, 5, 128), 640)
        model_width = 64
        self.assertEqual(
            sliding_window_cache_elements(20, 5, 2 * model_width),
            2 * 5 * model_width,
        )

    def test_finite_depth_receptive_field_is_exact_and_capped(self):
        """prop-swa-receptive-field gives max(1,i-L(w-1)) through i."""
        cases = [(30, 5, 4, 20), (30, 5, 10, 20), (7, 1, 50, 7), (7, 9, 2, 4)]
        for length, window, layers, position in cases:
            with self.subTest(case=(length, window, layers, position)):
                observed = structural_receptive_field(length, window, layers, position)
                earliest = max(1, position - layers * (window - 1))
                self.assertEqual(observed, set(range(earliest, position + 1)))

    def test_dilation_changes_span_not_degree_or_contiguous_coverage(self):
        """prop-static-sparse-counts keeps at most w edges for fixed dilation."""
        support = dilated_support(position=10, window=4, dilation=3)
        self.assertEqual(support, {1, 4, 7, 10})
        self.assertEqual(len(support), 4)
        self.assertEqual(max(support) - min(support), (4 - 1) * 3)
        self.assertNotIn(9, support)

    def test_factorized_block_and_global_edge_bounds(self):
        """prop-static-sparse-counts reproduces each declared combinatorial bound."""
        self.assertEqual(factorized_edge_bound(4096, 64), 524_288)
        candidates = range(1, 257)
        minimizer = min(candidates, key=lambda block: factorized_edge_bound(4096, block))
        self.assertEqual(minimizer, 64)
        self.assertEqual(block_sparse_edge_bound(1024, 64, 3), 196_608)
        base = causal_window_supports(length=10, window=2)
        global_rows = {1, 10}
        augmented = designate_global_rows(base, global_rows)
        added = sparse_edge_count(augmented) - sparse_edge_count(base)
        self.assertLessEqual(added, 2 * len(global_rows) * len(base))
        self.assertEqual(augmented[0], set(range(1, 11)))
        self.assertTrue(all(global_rows <= support for support in augmented))

    def test_sparsemax_projection_support_and_translation_invariance(self):
        """def-sparsemax and prop-sparsemax-support satisfy projection conditions."""
        logits = [1.0, 0.5, -1.0]
        probabilities = sparsemax(logits)
        self.assertEqual(probabilities, [0.75, 0.25, 0.0])
        self.assertAlmostEqual(sum(probabilities), 1.0)
        self.assertTrue(all(value >= 0 for value in probabilities))
        shifted = sparsemax([value + 7 for value in logits])
        for before, after in zip(probabilities, shifted):
            self.assertAlmostEqual(before, after)

        # A Euclidean projection p onto the simplex satisfies
        # <z-p, y-p> <= 0 for every simplex point y. Check an independent grid.
        residual = [z - p for z, p in zip(logits, probabilities)]
        for first in range(11):
            for second in range(11 - first):
                candidate = [first / 10, second / 10, (10 - first - second) / 10]
                variational_inner = sum(
                    r * (y - p)
                    for r, y, p in zip(residual, candidate, probabilities)
                )
                self.assertLessEqual(variational_inner, 1e-12)

        self.assertEqual(sparsemax([3.0, 0.0, -1.0]), [1.0, 0.0, 0.0])
        self.assertEqual(sparsemax([1.0, 0.0, 0.0]), [1.0, 0.0, 0.0])
        full_support = sparsemax([0.2, 0.1, 0.0])
        self.assertTrue(all(value > 0 for value in full_support))
        self.assertAlmostEqual(sum(full_support), 1.0)

    def test_nsa_branch_count_keeps_duplicate_branch_entries(self):
        """def-nsa-branches adds compressed, selected, and window supports."""
        self.assertEqual(nsa_branch_sizes(1, 32, 16, 4, 64, 128)[0], 0)
        sizes = nsa_branch_sizes(512, 32, 16, 4, 64, 128)
        self.assertEqual(sizes, (31, 256, 128))
        self.assertEqual(sum(sizes), 415)

    def test_nsa_fixed_stride_remains_quadratic(self):
        """prop-nsa-work has a quadratic compression term at fixed delta."""
        parameters = dict(
            compression_block=32,
            compression_stride=16,
            selected_blocks=1,
            selected_width=1,
            window=1,
        )
        small = nsa_support_count(20_000, **parameters)
        large = nsa_support_count(40_000, **parameters)
        self.assertGreater(large / small, 3.9)
        self.assertLess(large / small, 4.1)

    def test_nsa_exact_counts_obey_bound_and_compression_boundaries(self):
        """def-nsa-branches counts stay below the prop-nsa-work upper bound."""
        self.assertEqual(nsa_branch_sizes(31, 32, 16, 2, 4, 3)[0], 0)
        self.assertEqual(nsa_branch_sizes(32, 32, 16, 2, 4, 3)[0], 1)
        self.assertEqual(nsa_branch_sizes(47, 32, 16, 2, 4, 3)[0], 1)
        self.assertEqual(nsa_branch_sizes(48, 32, 16, 2, 4, 3)[0], 2)

        for length in (1, 17, 64, 257):
            for compression_block in (1, 8, 32):
                for compression_stride in (1, 4, 16):
                    with self.subTest(
                        length=length,
                        compression_block=compression_block,
                        compression_stride=compression_stride,
                    ):
                        observed = nsa_support_count(
                            length,
                            compression_block,
                            compression_stride,
                            selected_blocks=2,
                            selected_width=4,
                            window=3,
                        )
                        upper = (
                            length * (1 + 2 * 4 + 3)
                            + length * (length + 1) / (2 * compression_stride)
                        )
                        self.assertLessEqual(observed, upper)

    def test_nsa_exercise_upper_terms_and_subquadratic_scaling(self):
        """prop-nsa-work matches the chapter trace and its conditional n^(3/2) case."""
        compression, other = nsa_asymptotic_upper_terms(65_536, 16, 16, 64, 512)
        self.assertEqual(compression, 134_219_776)
        self.assertEqual(other, 100_663_296)
        self.assertEqual(compression + other, 234_883_072)

        ratios = []
        for length in (10_000, 40_000):
            root = math.isqrt(length)
            scaled_compression, scaled_other = nsa_asymptotic_upper_terms(
                length,
                root,
                selected_blocks=1,
                selected_width=root // 2,
                window=root // 2,
            )
            ratios.append((scaled_compression + scaled_other) / (length ** 1.5))
        self.assertAlmostEqual(ratios[0], ratios[1], delta=0.02)


if __name__ == "__main__":
    unittest.main()
