"""SSD chunk-cost arithmetic guards prop-tf13-chunked.

The exact proxy used in the proof separates dense intra-chunk work, two
state-summary/broadcast passes, and the cross-chunk scan.
"""

import math
from typing import NamedTuple
import unittest


class ChunkCosts(NamedTuple):
    intra_chunk: int
    summaries_and_broadcasts: int
    scan: int

    @property
    def total(self) -> int:
        return self.intra_chunk + self.summaries_and_broadcasts + self.scan


def chunk_costs(n: int, d: int, d_s: int, c: int) -> ChunkCosts:
    """Count the three multiplication terms in prop-tf13-chunked."""
    if c < 1 or n % c:
        raise ValueError("chunk size must be a positive divisor of n")
    return ChunkCosts(
        intra_chunk=n * c * (d + d_s),
        summaries_and_broadcasts=2 * n * d_s * d,
        scan=(n // c) * d_s * d,
    )


def variable_proxy(c: float, d: int, d_s: int) -> float:
    """Return c(d+d_s) + d_s*d/c, the c-dependent part of P(c)/n."""
    return c * (d + d_s) + d_s * d / c


def legal_continuous_target(n: int, d: int, d_s: int) -> float:
    """Clamp the unconstrained positive optimum to the legal interval [1,n]."""
    unconstrained = math.sqrt(d_s * d / (d + d_s))
    return min(float(n), max(1.0, unconstrained))


class SSDChunkingTests(unittest.TestCase):
    def test_continuous_proxy_has_width_aware_minimizer(self):
        """AM-GM gives c*=sqrt(d_s*d/(d+d_s)), approaching sqrt(d_s)."""
        for d, d_s in ((8, 1), (64, 4), (1_024, 16), (65_536, 81)):
            with self.subTest(d=d, d_s=d_s):
                optimum = math.sqrt(d_s * d / (d + d_s))
                floor = 2 * math.sqrt(d_s * d * (d + d_s))
                self.assertTrue(
                    math.isclose(variable_proxy(optimum, d, d_s), floor)
                )
                for scale in (0.25, 0.5, 1.0, 2.0, 4.0):
                    self.assertGreaterEqual(
                        variable_proxy(scale * optimum, d, d_s),
                        floor,
                    )

    def test_discrete_optimum_for_state_width_16_is_chunk_4(self):
        """For the chapter dimensions, divisor 4 minimizes the exact proxy."""
        n, d, d_s = 8_192, 1_024, 16
        divisors = [c for c in range(1, n + 1) if n % c == 0]
        best = min(divisors, key=lambda c: variable_proxy(c, d, d_s))
        self.assertEqual(best, 4)
        self.assertLess(variable_proxy(best, d, d_s), variable_proxy(16, d, d_s))

    def test_discrete_choice_uses_multiplicative_not_additive_distance(self):
        """A nearer divisor additively can still have the larger a*c+b/c cost."""
        n, d, d_s = 330, 10**9, 61
        optimum = math.sqrt(d_s * d / (d + d_s))
        self.assertLess(abs(6 - optimum), abs(10 - optimum))
        self.assertLess(abs(math.log(10 / optimum)), abs(math.log(6 / optimum)))
        self.assertLess(variable_proxy(10, d, d_s), variable_proxy(6, d, d_s))

    def test_legal_continuous_target_clamps_both_endpoints(self):
        """Legal chunks clamp an out-of-range c* to 1 or n before discretizing."""
        self.assertEqual(legal_continuous_target(n=128, d=64, d_s=1), 1.0)
        self.assertEqual(legal_continuous_target(n=2, d=10**9, d_s=100), 2.0)

    def test_every_chunk_from_one_to_state_width_is_on_one_plateau(self):
        """For 1<=c<=d_s, the exact proxy stays within constants of n*d_s*d."""
        n = math.lcm(*range(1, 17))
        d, d_s = 64, 16
        baseline = n * d_s * d
        for c in range(1, d_s + 1):
            with self.subTest(c=c):
                total = chunk_costs(n, d, d_s, c).total
                self.assertGreaterEqual(total, 2 * baseline)
                self.assertLessEqual(total, 4 * baseline)

    def test_exercise_13_6_exact_totals_and_masked_matmul_comparison(self):
        """Reproduce the c=4,16,256 totals and the c=n comparison."""
        n, d, d_s = 8_192, 1_024, 16
        expected = {
            4: ChunkCosts(34_078_720, 268_435_456, 33_554_432),
            16: ChunkCosts(136_314_880, 268_435_456, 8_388_608),
            256: ChunkCosts(2_181_038_080, 268_435_456, 524_288),
        }
        for c, wanted in expected.items():
            with self.subTest(c=c):
                self.assertEqual(chunk_costs(n, d, d_s, c), wanted)

        self.assertEqual(expected[4].total, 336_068_608)
        self.assertEqual(expected[16].total, 413_138_944)
        self.assertEqual(expected[256].total, 2_449_997_824)
        masked_matmul = n * n * (d + d_s)
        self.assertEqual(masked_matmul, 69_793_218_560)
        self.assertTrue(
            math.isclose(
                masked_matmul / expected[4].total,
                207.6755070202808,
            )
        )
        self.assertTrue(
            math.isclose(masked_matmul / expected[16].total, 168.93401015228426)
        )


if __name__ == "__main__":
    unittest.main()
