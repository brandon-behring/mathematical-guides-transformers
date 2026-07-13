"""Mixture-of-experts guards for def-moe, prop-moe-router-gradient,
def-moe-routing-objective, def-moe-capacity, prop-moe-capacity,
def-expert-choice, and prop-moe-flops.

Resident capacity, activated arithmetic, and ideal weight traffic are three
different quantities. Router gradients are checked against finite differences,
and load, capacity, and routing-direction identities are re-derived directly.
"""

from dataclasses import dataclass
import math
import unittest


@dataclass(frozen=True)
class MoEAccounting:
    resident_bytes: int
    activated_flops: int
    ideal_traffic_bytes: int
    active_experts: int


def active_expert_union(routes: list[set[int]]) -> set[int]:
    """Build the active-expert union A_B from per-token top-k selections."""
    return set().union(*routes)


def validate_routes(experts: int, k: int, routes: list[set[int]]) -> None:
    """Enforce the top-k set and expert-index premises of def-moe."""
    if not routes:
        raise ValueError("a served batch must contain at least one token")
    if not 1 <= k <= experts:
        raise ValueError("k must lie between one and the expert count")
    for selected in routes:
        if len(selected) != k:
            raise ValueError("every token must select exactly k distinct experts")
        if any(index < 0 or index >= experts for index in selected):
            raise ValueError("expert index outside the layer")


def account_moe(
    experts: int,
    k: int,
    routes: list[set[int]],
    expert_bytes: int,
    expert_call_flops: int,
) -> MoEAccounting:
    """Compute E*mu, T*k*Phi, and A_B*mu (prop-moe-flops)."""
    validate_routes(experts, k, routes)
    active = len(active_expert_union(routes))
    return MoEAccounting(
        resident_bytes=experts * expert_bytes,
        activated_flops=len(routes) * k * expert_call_flops,
        ideal_traffic_bytes=active * expert_bytes,
        active_experts=active,
    )


def intensity_ratio_to_dense(k: int, active_experts: int) -> float:
    """Return I_MoE / I_dense = k/A_B under the once-read idealization."""
    return k / active_experts


def softmax(scores: list[float]) -> list[float]:
    """Stable full softmax over all router logits (def-moe)."""
    offset = max(scores)
    weights = [math.exp(score - offset) for score in scores]
    normalizer = sum(weights)
    return [weight / normalizer for weight in weights]


def top_k_indices(scores: list[float], k: int) -> set[int]:
    """Select a deterministic top-k set, breaking equal scores by index."""
    if not 1 <= k <= len(scores):
        raise ValueError("k must lie between one and the score count")
    return set(sorted(range(len(scores)), key=lambda index: (-scores[index], index))[:k])


def full_softmax_masked_output(
    scores: list[float], expert_outputs: list[float], k: int
) -> float:
    """Scalar instance of def-moe's full-softmax-then-mask output."""
    if len(scores) != len(expert_outputs):
        raise ValueError("each score must have one expert output")
    selected = top_k_indices(scores, k)
    probabilities = softmax(scores)
    return sum(
        probabilities[index] * expert_outputs[index]
        for index in selected
    )


def full_softmax_masked_gradient(
    scores: list[float], expert_outputs: list[float], k: int
) -> list[float]:
    """Analytic score gradient from prop-moe-router-gradient."""
    selected = top_k_indices(scores, k)
    probabilities = softmax(scores)
    output = full_softmax_masked_output(scores, expert_outputs, k)
    return [
        probability
        * ((expert_outputs[index] if index in selected else 0.0) - output)
        for index, probability in enumerate(probabilities)
    ]


def selected_softmax_weights(scores: list[float], k: int) -> list[float]:
    """Selected-only renormalization from def-moe."""
    selected = top_k_indices(scores, k)
    offset = max(scores[index] for index in selected)
    unnormalized = [
        math.exp(score - offset) if index in selected else 0.0
        for index, score in enumerate(scores)
    ]
    normalizer = sum(unnormalized)
    return [weight / normalizer for weight in unnormalized]


def selected_softmax_output(
    scores: list[float], expert_outputs: list[float], k: int
) -> float:
    """Scalar selected-softmax variant whose unselected logits are local constants."""
    weights = selected_softmax_weights(scores, k)
    return sum(weight * output for weight, output in zip(weights, expert_outputs))


def central_difference(
    function, point: list[float], coordinate: int, epsilon: float = 1e-6
) -> float:
    """Numerically differentiate one coordinate away from routing ties."""
    above = point.copy()
    below = point.copy()
    above[coordinate] += epsilon
    below[coordinate] -= epsilon
    return (function(above) - function(below)) / (2 * epsilon)


def switch_balance_loss(
    dispatches: list[int], probabilities: list[list[float]]
) -> float:
    """Compute E*sum_i f_i*P_i from def-moe-routing-objective."""
    if not dispatches or len(dispatches) != len(probabilities):
        raise ValueError("dispatches and probability rows must align")
    experts = len(probabilities[0])
    if any(len(row) != experts for row in probabilities):
        raise ValueError("probability rows must have equal width")
    tokens = len(dispatches)
    fractions = [dispatches.count(index) / tokens for index in range(experts)]
    mean_probabilities = [
        sum(row[index] for row in probabilities) / tokens
        for index in range(experts)
    ]
    return experts * sum(
        fraction * probability
        for fraction, probability in zip(fractions, mean_probabilities)
    )


def router_z_loss(score_rows: list[list[float]]) -> float:
    """Stable evaluation of the router z-loss in def-moe-routing-objective."""
    if not score_rows or any(not row for row in score_rows):
        raise ValueError("z-loss needs at least one nonempty score row")
    log_partitions = []
    for row in score_rows:
        offset = max(row)
        log_partitions.append(
            offset + math.log(sum(math.exp(score - offset) for score in row))
        )
    return sum(value * value for value in log_partitions) / len(log_partitions)


def capacity_accounting(
    loads: list[int], capacity_factor: float
) -> tuple[int, int, int]:
    """Return C, D, and executed assignments for def/prop-moe-capacity."""
    if not loads or capacity_factor <= 0 or any(load < 0 for load in loads):
        raise ValueError("loads and capacity factor must be positive-domain values")
    assignments = sum(loads)
    capacity = math.ceil(capacity_factor * assignments / len(loads))
    overflow = sum(max(load - capacity, 0) for load in loads)
    executed = sum(min(load, capacity) for load in loads)
    return capacity, overflow, executed


def token_choice_matrix(scores: list[list[float]], k: int) -> list[list[int]]:
    """Assignment matrix with exactly k selected experts per row."""
    return [
        [int(index in top_k_indices(row, k)) for index in range(len(row))]
        for row in scores
    ]


def expert_choice_matrix(scores: list[list[float]], bucket: int) -> list[list[int]]:
    """Assignment matrix with exactly bucket selected tokens per expert column."""
    if not scores or any(len(row) != len(scores[0]) for row in scores):
        raise ValueError("score matrix must be nonempty and rectangular")
    tokens, experts = len(scores), len(scores[0])
    if not 1 <= bucket <= tokens:
        raise ValueError("bucket must lie between one and the token count")
    matrix = [[0 for _ in range(experts)] for _ in range(tokens)]
    for expert in range(experts):
        selected = sorted(
            range(tokens), key=lambda token: (-scores[token][expert], token)
        )[:bucket]
        for token in selected:
            matrix[token][expert] = 1
    return matrix


class MoECostTests(unittest.TestCase):
    def test_full_softmax_router_gradient_matches_finite_differences(self):
        """prop-moe-router-gradient agrees with an independent local derivative."""
        scores = [2.0, 0.5, -1.0, -2.0]
        expert_outputs = [3.0, -2.0, 4.0, 1.0]
        k = 2
        analytic = full_softmax_masked_gradient(scores, expert_outputs, k)
        function = lambda point: full_softmax_masked_output(point, expert_outputs, k)
        numeric = [central_difference(function, scores, index) for index in range(4)]
        for expected, observed in zip(analytic, numeric):
            self.assertAlmostEqual(expected, observed, places=8)

    def test_full_softmax_keeps_an_unselected_logit_gradient(self):
        """Masking execution does not remove the full-softmax denominator path."""
        scores = [2.0, 0.5, -1.0]
        expert_outputs = [3.0, -2.0, 4.0]
        gradient = full_softmax_masked_gradient(scores, expert_outputs, k=2)
        probabilities = softmax(scores)
        output = full_softmax_masked_output(scores, expert_outputs, k=2)
        self.assertNotEqual(gradient[2], 0.0)
        self.assertAlmostEqual(gradient[2], -probabilities[2] * output)

    def test_router_matrix_gradient_is_input_outer_score_gradient(self):
        """Equation (5) has the d-by-E orientation required by the row score map."""
        inputs = [1.5, -0.4]
        weights = [[1.2, 0.1, -0.8], [0.3, 1.1, 0.2]]
        expert_outputs = [3.0, -2.0, 4.0]

        def score_matrix(matrix: list[list[float]]) -> list[float]:
            return [
                sum(inputs[row] * matrix[row][column] for row in range(2))
                for column in range(3)
            ]

        scores = score_matrix(weights)
        score_gradient = full_softmax_masked_gradient(scores, expert_outputs, k=2)
        for row in range(2):
            for column in range(3):
                above = [values.copy() for values in weights]
                below = [values.copy() for values in weights]
                above[row][column] += 1e-6
                below[row][column] -= 1e-6
                numeric = (
                    full_softmax_masked_output(
                        score_matrix(above), expert_outputs, k=2
                    )
                    - full_softmax_masked_output(
                        score_matrix(below), expert_outputs, k=2
                    )
                ) / (2e-6)
                self.assertAlmostEqual(
                    numeric, inputs[row] * score_gradient[column], places=8
                )

    def test_selected_softmax_normalizes_and_ignores_unselected_logits(self):
        """Equation (4) matches selected and unselected finite differences."""
        scores = [2.0, 0.5, -1.0]
        expert_outputs = [3.0, -2.0, 4.0]
        weights = selected_softmax_weights(scores, k=2)
        output = selected_softmax_output(scores, expert_outputs, k=2)
        self.assertAlmostEqual(sum(weights), 1.0)
        self.assertEqual(weights[2], 0.0)
        function = lambda point: selected_softmax_output(point, expert_outputs, k=2)
        for index in (0, 1):
            expected = weights[index] * (expert_outputs[index] - output)
            self.assertAlmostEqual(
                central_difference(function, scores, index), expected, places=8
            )
        self.assertAlmostEqual(central_difference(function, scores, 2), 0.0)

    def test_switch_balance_loss_endpoints_and_example(self):
        """def-moe-routing-objective gives 1 uniformly and E at confident collapse."""
        uniform = switch_balance_loss([0, 1], [[0.5, 0.5], [0.5, 0.5]])
        collapsed = switch_balance_loss([0, 0], [[1.0, 0.0], [1.0, 0.0]])
        example = switch_balance_loss(
            [0, 0, 0, 1],
            [[0.8, 0.2], [0.8, 0.2], [0.8, 0.2], [0.4, 0.6]],
        )
        self.assertEqual(uniform, 1.0)
        self.assertEqual(collapsed, 2.0)
        self.assertAlmostEqual(example, 1.2)

    def test_router_z_loss_gradient_and_translation_sensitivity(self):
        """Equations (7)-(8) expose the shift degree but do not isolate it."""
        scores = [2.0, 0.5, -1.0]
        offset = max(scores)
        log_partition = offset + math.log(
            sum(math.exp(score - offset) for score in scores)
        )
        probabilities = softmax(scores)
        function = lambda point: router_z_loss([point])
        analytic = [2 * log_partition * probability for probability in probabilities]
        numeric = [central_difference(function, scores, index) for index in range(3)]
        for expected, observed in zip(analytic, numeric):
            self.assertAlmostEqual(expected, observed, places=8)
        shifted = [score + 1.25 for score in scores]
        for before, after in zip(softmax(scores), softmax(shifted)):
            self.assertAlmostEqual(before, after)
        self.assertNotEqual(router_z_loss([scores]), router_z_loss([shifted]))
        self.assertNotAlmostEqual(analytic[0], analytic[1])

    def test_capacity_conserves_executed_plus_overflow(self):
        """prop-moe-capacity preserves all Tk assignments in the accounting."""
        capacity, overflow, executed = capacity_accounting([8, 4, 3, 1], 1.0)
        self.assertEqual(capacity, 4)
        self.assertEqual(overflow, 4)
        self.assertEqual(executed, 12)
        self.assertEqual(executed + overflow, 16)

    def test_balanced_loads_fit_but_aggregate_slots_do_not_prevent_overflow(self):
        """def-moe-capacity is per expert, even when total slots equal Tk."""
        self.assertEqual(capacity_accounting([4, 4, 4, 4], 1.0), (4, 0, 16))
        self.assertEqual(capacity_accounting([16, 0, 0, 0], 1.0), (4, 12, 4))

    def test_token_choice_fixes_rows_and_expert_choice_fixes_columns(self):
        """def-expert-choice swaps fixed token degree for fixed expert load."""
        scores = [[9.0, 10.0], [8.0, 7.0], [0.0, 6.0]]
        token_matrix = token_choice_matrix(scores, k=1)
        expert_matrix = expert_choice_matrix(scores, bucket=1)
        self.assertEqual([sum(row) for row in token_matrix], [1, 1, 1])
        self.assertEqual(
            [sum(row[column] for row in expert_matrix) for column in range(2)],
            [1, 1],
        )
        self.assertEqual([sum(row) for row in expert_matrix], [2, 0, 0])

    def test_active_union_obeys_the_top_k_bounds(self):
        """The explicit union satisfies k <= A_B <= min(E, T*k)."""
        experts, k = 10, 2
        route_families = [
            [{0, 1}, {0, 1}, {0, 1}, {0, 1}],
            [{0, 1}, {1, 2}, {2, 3}, {3, 4}],
            [{0, 1}, {2, 3}, {4, 5}, {6, 7}],
        ]
        for routes in route_families:
            with self.subTest(routes=routes):
                validate_routes(experts, k, routes)
                active = len(active_expert_union(routes))
                self.assertGreaterEqual(active, k)
                self.assertLessEqual(active, min(experts, len(routes) * k))

    def test_three_accounting_quantities_have_distinct_dependencies(self):
        """Residency uses E, compute uses T*k, and traffic uses A_B."""
        routes = [{0, 1}, {1, 2}, {2, 3}]
        result = account_moe(8, 2, routes, expert_bytes=100, expert_call_flops=30)
        self.assertEqual(result.resident_bytes, 800)
        self.assertEqual(result.activated_flops, 180)
        self.assertEqual(result.active_experts, 4)
        self.assertEqual(result.ideal_traffic_bytes, 400)

    def test_one_token_streams_only_its_k_active_experts(self):
        """For T=1, A_B=k and ideal intensity matches one dense expert."""
        result = account_moe(
            64,
            2,
            [{5, 17}],
            expert_bytes=1_024,
            expert_call_flops=2_048,
        )
        self.assertEqual(result.resident_bytes, 64 * 1_024)
        self.assertEqual(result.activated_flops, 2 * 2_048)
        self.assertEqual(result.ideal_traffic_bytes, 2 * 1_024)
        self.assertEqual(intensity_ratio_to_dense(2, result.active_experts), 1.0)

    def test_repeated_routing_reuses_the_same_weight_union(self):
        """The chapter exercise's repeated route keeps A_B=k, not T*k."""
        routes = [{3, 11} for _ in range(32)]
        result = account_moe(
            64,
            2,
            routes,
            expert_bytes=7,
            expert_call_flops=13,
        )
        self.assertEqual(result.resident_bytes, 64 * 7)
        self.assertEqual(result.activated_flops, 64 * 13)
        self.assertEqual(result.ideal_traffic_bytes, 2 * 7)
        self.assertEqual(intensity_ratio_to_dense(2, result.active_experts), 1.0)

    def test_full_coverage_recovers_the_k_over_e_limit(self):
        """When A_B=E, traffic is E*mu and the ratio becomes k/E."""
        routes = [{2 * t, 2 * t + 1} for t in range(32)]
        result = account_moe(
            64,
            2,
            routes,
            expert_bytes=7,
            expert_call_flops=13,
        )
        self.assertEqual(result.active_experts, 64)
        self.assertEqual(result.ideal_traffic_bytes, 64 * 7)
        self.assertEqual(intensity_ratio_to_dense(2, result.active_experts), 1 / 32)

    def test_expert_shards_sum_to_global_residency_and_traffic(self):
        """A disjoint expert partition redistributes, but does not erase, bytes."""
        shards = [set(range(0, 4)), set(range(4, 8))]
        active = {0, 2, 3, 7}
        expert_bytes = 128
        self.assertEqual(sum(len(shard) for shard in shards), 8)
        self.assertEqual(sum(len(shard & active) for shard in shards), len(active))
        local_resident = [len(shard) * expert_bytes for shard in shards]
        local_traffic = [len(shard & active) * expert_bytes for shard in shards]
        self.assertEqual(sum(local_resident), 8 * expert_bytes)
        self.assertEqual(sum(local_traffic), len(active) * expert_bytes)


if __name__ == "__main__":
    unittest.main()
