"""Numeric guards for prop-ln-jacobian and rem-rmsnorm.

Analytic Jacobians are checked against central differences. Deterministic
directions exercise the chapter bounds, including RMSNorm's sharp x=0 case.
"""

import math
import unittest


def layer_norm(
    values: list[float], gamma: list[float], epsilon: float
) -> list[float]:
    mean = sum(values) / len(values)
    centered = [value - mean for value in values]
    scale = math.sqrt(sum(value * value for value in centered) / len(values) + epsilon)
    return [weight * value / scale for weight, value in zip(gamma, centered)]


def rms_norm(
    values: list[float], gamma: list[float], epsilon: float
) -> list[float]:
    scale = math.sqrt(sum(value * value for value in values) / len(values) + epsilon)
    return [weight * value / scale for weight, value in zip(gamma, values)]


def layer_norm_jacobian(
    values: list[float], gamma: list[float], epsilon: float
) -> list[list[float]]:
    dimension = len(values)
    mean = sum(values) / dimension
    centered = [value - mean for value in values]
    scale = math.sqrt(
        sum(value * value for value in centered) / dimension + epsilon
    )
    return [
        [
            gamma[row]
            / scale
            * (
                int(row == column)
                - 1 / dimension
                - centered[row] * centered[column] / (dimension * scale * scale)
            )
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def rms_norm_jacobian(
    values: list[float], gamma: list[float], epsilon: float
) -> list[list[float]]:
    dimension = len(values)
    scale = math.sqrt(sum(value * value for value in values) / dimension + epsilon)
    return [
        [
            gamma[row]
            / scale
            * (
                int(row == column)
                - values[row] * values[column] / (dimension * scale * scale)
            )
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def finite_difference_jacobian(function, values: list[float]) -> list[list[float]]:
    epsilon = 1e-6
    base_output = function(values)
    jacobian = [[0.0 for _ in values] for _ in base_output]
    for column in range(len(values)):
        above = values.copy()
        below = values.copy()
        above[column] += epsilon
        below[column] -= epsilon
        upper = function(above)
        lower = function(below)
        for row in range(len(base_output)):
            jacobian[row][column] = (upper[row] - lower[row]) / (2 * epsilon)
    return jacobian


def matvec(matrix: list[list[float]], vector: list[float]) -> list[float]:
    return [sum(value * direction for value, direction in zip(row, vector)) for row in matrix]


def norm(vector: list[float]) -> float:
    return math.sqrt(sum(value * value for value in vector))


class NormalizationTests(unittest.TestCase):
    def assert_matrices_close(
        self, observed: list[list[float]], expected: list[list[float]]
    ) -> None:
        for observed_row, expected_row in zip(observed, expected):
            for observed_value, expected_value in zip(observed_row, expected_row):
                self.assertAlmostEqual(observed_value, expected_value, places=7)

    def test_layer_norm_jacobian_matches_finite_differences(self):
        """prop-ln-jacobian uses the derivative of centering and scaling."""
        values = [1.2, -0.7, 2.1, 0.3]
        gamma = [1.0, 0.5, 1.5, 0.8]
        epsilon = 0.07
        analytic = layer_norm_jacobian(values, gamma, epsilon)
        numeric = finite_difference_jacobian(
            lambda point: layer_norm(point, gamma, epsilon), values
        )
        self.assert_matrices_close(analytic, numeric)

    def test_rmsnorm_jacobian_matches_finite_differences(self):
        """rem-rmsnorm's rank-one Jacobian is the actual local derivative."""
        values = [1.2, -0.7, 2.1, 0.3]
        gamma = [1.0, 0.5, 1.5, 0.8]
        epsilon = 0.07
        analytic = rms_norm_jacobian(values, gamma, epsilon)
        numeric = finite_difference_jacobian(
            lambda point: rms_norm(point, gamma, epsilon), values
        )
        self.assert_matrices_close(analytic, numeric)

    def test_declared_bounds_hold_on_deterministic_directions(self):
        """Both chapter bounds dominate every sampled directional gain."""
        values = [1.2, -0.7, 2.1, 0.3]
        gamma = [1.0, 0.5, 1.5, 0.8]
        epsilon = 0.07
        layer_jacobian = layer_norm_jacobian(values, gamma, epsilon)
        rms_jacobian = rms_norm_jacobian(values, gamma, epsilon)
        layer_bound = max(abs(value) for value in gamma) / math.sqrt(epsilon)
        rms_bound = max(abs(value) for value in gamma) / math.sqrt(epsilon)
        directions = [
            [1.0, 0.0, 0.0, 0.0],
            [0.5, -1.0, 0.75, 0.25],
            [1.0, 1.0, 1.0, 1.0],
            [-2.0, 0.5, 1.0, -0.25],
        ]
        for direction in directions:
            self.assertLessEqual(norm(matvec(layer_jacobian, direction)), layer_bound * norm(direction))
            self.assertLessEqual(norm(matvec(rms_jacobian, direction)), rms_bound * norm(direction))

    def test_layer_norm_exact_eigenspaces_give_constant_one(self):
        """prop-ln-jacobian uses the commuting projection/rank-one spectrum."""
        values = [1.0, -1.0, 0.0]
        gamma = [1.0, 1.0, 1.0]
        epsilon = 0.25
        jacobian = layer_norm_jacobian(values, gamma, epsilon)
        scale = math.sqrt(2 / 3 + epsilon)
        uniform = [1.0, 1.0, 1.0]
        centered_input = values
        transverse = [1.0, 1.0, -2.0]
        self.assertAlmostEqual(norm(matvec(jacobian, uniform)), 0.0)
        self.assertAlmostEqual(
            norm(matvec(jacobian, centered_input)) / norm(centered_input),
            epsilon / (scale**3),
        )
        self.assertAlmostEqual(
            norm(matvec(jacobian, transverse)) / norm(transverse),
            1 / scale,
        )

        constant_jacobian = layer_norm_jacobian(
            [3.0, 3.0, 3.0], gamma, epsilon
        )
        self.assertAlmostEqual(
            norm(matvec(constant_jacobian, transverse)) / norm(transverse),
            1 / math.sqrt(epsilon),
        )

    def test_rmsnorm_bound_is_sharp_at_zero(self):
        """At x=0, rem-rmsnorm has J=diag(gamma)/sqrt(epsilon)."""
        gamma = [0.5, -2.0, 1.0]
        epsilon = 0.25
        jacobian = rms_norm_jacobian([0.0, 0.0, 0.0], gamma, epsilon)
        expected = [
            [1.0, 0.0, 0.0],
            [0.0, -4.0, 0.0],
            [0.0, 0.0, 2.0],
        ]
        self.assertEqual(jacobian, expected)
        self.assertEqual(max(abs(value) for value in gamma) / math.sqrt(epsilon), 4.0)

    def test_only_layer_norm_is_uniform_shift_invariant(self):
        """rem-rmsnorm correctly excludes LayerNorm's mean-shift invariance."""
        values = [1.0, -1.0, 0.5]
        shifted = [value + 3.0 for value in values]
        gamma = [1.0, 1.0, 1.0]
        epsilon = 0.1
        for original, moved in zip(
            layer_norm(values, gamma, epsilon),
            layer_norm(shifted, gamma, epsilon),
        ):
            self.assertAlmostEqual(original, moved)
        self.assertNotEqual(
            rms_norm(values, gamma, epsilon),
            rms_norm(shifted, gamma, epsilon),
        )


if __name__ == "__main__":
    unittest.main()
