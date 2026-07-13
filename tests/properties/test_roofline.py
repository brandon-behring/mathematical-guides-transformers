"""Roofline cost-per-token equation — guards ``def-tf12-cost-eq`` and
``prop-tf12-memory-bound`` (ch12, Inference Optimizations).

The device finishes a decode step no faster than the slower of its two clocks:
arithmetic (``Phi/F``) and memory (``beta/B``). Below the ridge point the FLOP
rate ``F`` cannot help — the entire lever of the chapter.
"""

import math
import unittest


def t_token(phi: float, beta: float, F: float, B: float) -> float:
    """Cost-per-token lower bound ``max(Phi/F, beta/B)`` (def-tf12-cost-eq)."""
    return max(phi / F, beta / B)


def intensity(phi: float, beta: float) -> float:
    """Arithmetic intensity ``I = Phi/beta`` (FLOPs per byte)."""
    return phi / beta


def ridge(F: float, B: float) -> float:
    """Device ridge point ``I* = F/B``."""
    return F / B


class RooflineTests(unittest.TestCase):
    def test_ridge_is_the_crossover(self):
        """At I = I* the two clocks are equal; the max has either argument."""
        F, B = 3.12e14, 1.5e12
        I_star = ridge(F, B)
        beta = 1e6
        phi = I_star * beta
        self.assertTrue(math.isclose(phi / F, beta / B, rel_tol=1e-12))
        self.assertTrue(math.isclose(intensity(phi, beta), I_star, rel_tol=1e-12))

    def test_memory_bound_throughput_is_independent_of_F(self):
        """prop-tf12-memory-bound: below the ridge, more FLOPs do not help."""
        B = 1.5e12
        beta = 2e9
        phi = 2e6
        for F in (1e14, 5e14, 2e15):
            I = intensity(phi, beta)
            self.assertLess(I, ridge(F, B))
            self.assertTrue(math.isclose(t_token(phi, beta, F, B), beta / B, rel_tol=1e-12))
            throughput = phi / t_token(phi, beta, F, B)
            self.assertTrue(math.isclose(throughput, B * I, rel_tol=1e-12))

    def test_compute_bound_saturates_at_F(self):
        """Above the ridge the step is compute-bound: T = Phi/F."""
        F, B = 3e14, 1.5e12
        phi = 3e12
        beta = 1e6
        self.assertGreater(intensity(phi, beta), ridge(F, B))
        self.assertTrue(math.isclose(t_token(phi, beta, F, B), phi / F, rel_tol=1e-12))
        self.assertTrue(math.isclose(phi / t_token(phi, beta, F, B), F, rel_tol=1e-12))

    def test_decode_intensity_collapses_to_order_one(self):
        """rem-tf12-prefill-decode: single-query matvec intensity is O(1)."""
        d = 8192
        phi = 2 * d * d
        beta = 2 * d * d
        self.assertTrue(math.isclose(intensity(phi, beta), 1.0, rel_tol=0.5))


if __name__ == "__main__":
    unittest.main()
