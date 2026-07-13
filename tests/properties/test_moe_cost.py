"""Mixture-of-experts accounting guards def-moe and
prop-moe-flops.

Resident capacity, activated arithmetic, and ideal weight traffic are three
different quantities. These tests make their different dependencies explicit.
"""

from dataclasses import dataclass
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


class MoECostTests(unittest.TestCase):
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
