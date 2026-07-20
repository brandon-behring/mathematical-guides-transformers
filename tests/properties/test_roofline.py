"""Roofline cost-per-token lower bound — guards ``def-cost-eq`` and
``prop-memory-bound`` (ch15, Inference Optimizations).

The device finishes a decode step no faster than the slower of its two clocks:
arithmetic (``Phi/F``) and memory (``beta/B``). Below the ridge point the FLOP
rate ``F`` cannot help — the entire lever of the chapter.
"""

import math
import unittest


def t_roof(phi: float, beta: float, F: float, B: float) -> float:
    """Ideal roofline time ``max(Phi/F, beta/B)`` (def-cost-eq)."""
    return max(phi / F, beta / B)


def intensity(phi: float, beta: float) -> float:
    """Arithmetic intensity ``I = Phi/beta`` (FLOPs per byte)."""
    return phi / beta


def ridge(F: float, B: float) -> float:
    """Device ridge point ``I* = F/B``."""
    return F / B


class RooflineTests(unittest.TestCase):
    def test_ridge_is_the_crossover(self):
        """def-cost-eq makes the two clocks equal at I = I*."""
        F, B = 3.12e14, 1.5e12
        I_star = ridge(F, B)
        beta = 1e6
        phi = I_star * beta
        self.assertTrue(math.isclose(phi / F, beta / B, rel_tol=1e-12))
        self.assertTrue(math.isclose(intensity(phi, beta), I_star, rel_tol=1e-12))

    def test_memory_bound_throughput_is_independent_of_F(self):
        """prop-memory-bound: below the ridge, more FLOPs do not help."""
        B = 1.5e12
        beta = 2e9
        phi = 2e6
        for F in (1e14, 5e14, 2e15):
            I = intensity(phi, beta)
            self.assertLess(I, ridge(F, B))
            roof = t_roof(phi, beta, F, B)
            self.assertTrue(math.isclose(roof, beta / B, rel_tol=1e-12))
            actual_time = 1.25 * roof
            self.assertGreaterEqual(actual_time, roof)
            self.assertLessEqual(phi / actual_time, B * I)
            self.assertTrue(math.isclose(phi / roof, B * I, rel_tol=1e-12))

    def test_compute_bound_saturates_at_F(self):
        """Above the ridge the step is compute-bound: T = Phi/F."""
        F, B = 3e14, 1.5e12
        phi = 3e12
        beta = 1e6
        self.assertGreater(intensity(phi, beta), ridge(F, B))
        self.assertTrue(math.isclose(t_roof(phi, beta, F, B), phi / F, rel_tol=1e-12))
        self.assertTrue(math.isclose(phi / t_roof(phi, beta, F, B), F, rel_tol=1e-12))

    def test_decode_intensity_collapses_to_order_one(self):
        """rem-prefill-decode: single-query matvec intensity is O(1)."""
        d = 8192
        phi = 2 * d * d
        beta = 2 * d * d
        self.assertTrue(math.isclose(intensity(phi, beta), 1.0, rel_tol=0.5))


if __name__ == "__main__":
    unittest.main()
