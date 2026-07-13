"""Executable guards for the scaling-law derivations in Chapter 13.

The tests independently guard ``def-separable-scaling-law`` and
``def-training-compute-proxy``; the closed-form constrained optimum, marginal
balance, and Lagrange multiplier in ``thm-compute-optimal-allocation``; the
square-root specialization in ``cor-equal-exponent-allocation``; and the
compute exponent in ``prop-optimal-excess-loss-rate``. Boundary tests encode
the positivity and finiteness qualifications in the definitions and allocation
theorem. The qualitative remarks are intentionally not promoted into numeric
coverage: these executable guards concern training compute only.

All objective comparisons are evaluated in log space.  The suite is
stdlib-only, deterministic, and independent of MDX parsing.
"""

import math
import random
import unittest


def _require_finite(name: str, value: float) -> None:
    """Require a finite scalar, allowing either sign."""
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")


def _require_positive_finite(**values: float) -> None:
    """Require finite, strictly positive scaling-law parameters."""
    for name, value in values.items():
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"{name} must be finite and strictly positive")


def _logaddexp(left: float, right: float) -> float:
    """Return log(exp(left) + exp(right)) without overflow or underflow."""
    _require_finite("left log-term", left)
    _require_finite("right log-term", right)
    high = max(left, right)
    low = min(left, right)
    return high + math.log1p(math.exp(low - high))


def training_compute_proxy(N: float, D: float, kappa: float) -> float:
    """Evaluate the proxy C = kappa N D from def-training-compute-proxy."""
    _require_positive_finite(N=N, D=D, kappa=kappa)
    return kappa * N * D


def log_excess_loss_from_logs(
    log_N: float,
    log_D: float,
    *,
    A: float,
    B: float,
    alpha: float,
    beta: float,
) -> float:
    """Evaluate log(A N^-alpha + B D^-beta) from log N and log D."""
    _require_finite("log N", log_N)
    _require_finite("log D", log_D)
    _require_positive_finite(A=A, B=B, alpha=alpha, beta=beta)
    parameter_term = math.log(A) - alpha * log_N
    data_term = math.log(B) - beta * log_D
    return _logaddexp(parameter_term, data_term)


def log_excess_loss(
    N: float,
    D: float,
    *,
    A: float,
    B: float,
    alpha: float,
    beta: float,
) -> float:
    """Ordinary-coordinate wrapper for the stable log excess-loss evaluator."""
    _require_positive_finite(N=N, D=D)
    return log_excess_loss_from_logs(
        math.log(N), math.log(D), A=A, B=B, alpha=alpha, beta=beta
    )


def optimal_log_allocation(
    *,
    E: float,
    A: float,
    B: float,
    alpha: float,
    beta: float,
    kappa: float,
    C: float,
) -> tuple[float, float]:
    """Return (log N*, log D*) from thm-compute-optimal-allocation."""
    _require_finite("E", E)
    _require_positive_finite(
        A=A, B=B, alpha=alpha, beta=beta, kappa=kappa, C=C
    )
    log_compute_per_kappa = math.log(C) - math.log(kappa)
    log_marginal_ratio = (
        math.log(alpha)
        + math.log(A)
        - math.log(beta)
        - math.log(B)
    )
    log_N = (
        log_marginal_ratio + beta * log_compute_per_kappa
    ) / (alpha + beta)
    # This form enforces the compute constraint to roundoff even in extreme
    # regimes; it is algebraically identical to the symmetric formula for D*.
    log_D = log_compute_per_kappa - log_N
    return log_N, log_D


def optimal_log_multiplier(
    log_N: float,
    log_D: float,
    *,
    A: float,
    B: float,
    alpha: float,
    beta: float,
    C: float,
) -> tuple[float, float]:
    """Return log lambda from the N and D stationarity equations."""
    _require_finite("log N", log_N)
    _require_finite("log D", log_D)
    _require_positive_finite(A=A, B=B, alpha=alpha, beta=beta, C=C)
    from_N = math.log(alpha) + math.log(A) - alpha * log_N - math.log(C)
    from_D = math.log(beta) + math.log(B) - beta * log_D - math.log(C)
    return from_N, from_D


def independently_minimize_log_excess(
    *,
    A: float,
    B: float,
    alpha: float,
    beta: float,
    kappa: float,
    C: float,
) -> tuple[float, float, float]:
    """Numerically minimize in log N under log N + log D = log(C/kappa).

    The bracketing and golden-section search do not use the theorem's closed
    form or its marginal-balance equation.
    """
    _require_positive_finite(
        A=A, B=B, alpha=alpha, beta=beta, kappa=kappa, C=C
    )
    log_compute_per_kappa = math.log(C) - math.log(kappa)

    def objective(log_N: float) -> float:
        return log_excess_loss_from_logs(
            log_N,
            log_compute_per_kappa - log_N,
            A=A,
            B=B,
            alpha=alpha,
            beta=beta,
        )

    center = log_compute_per_kappa / 2.0
    step = 1.0
    center_value = objective(center)
    left_value = objective(center - step)
    right_value = objective(center + step)

    if center_value <= left_value and center_value <= right_value:
        lower, upper = center - step, center + step
    else:
        direction = -1.0 if left_value < right_value else 1.0
        previous = center
        current = center + direction * step
        current_value = objective(current)
        for _ in range(64):
            step *= 2.0
            candidate = current + direction * step
            candidate_value = objective(candidate)
            if candidate_value >= current_value:
                lower, upper = sorted((previous, candidate))
                break
            previous = current
            current = candidate
            current_value = candidate_value
        else:
            raise RuntimeError("failed to bracket the log-space minimum")

    golden = (math.sqrt(5.0) - 1.0) / 2.0
    for _ in range(180):
        if upper - lower <= 1e-12 * (1.0 + abs((lower + upper) / 2.0)):
            break
        left_probe = upper - golden * (upper - lower)
        right_probe = lower + golden * (upper - lower)
        if objective(left_probe) <= objective(right_probe):
            upper = right_probe
        else:
            lower = left_probe

    log_N = (lower + upper) / 2.0
    log_D = log_compute_per_kappa - log_N
    return log_N, log_D, objective(log_N)


class TestScalingLawOptimalAllocation(unittest.TestCase):
    """Guard Chapter 13's separable training-compute derivation."""

    def test_stable_log_space_evaluation_handles_extreme_terms(self):
        """def-separable-scaling-law remains evaluable beyond exp range."""
        value = log_excess_loss_from_logs(
            1_000.0,
            -1_000.0,
            A=1.0,
            B=1.0,
            alpha=1.0,
            beta=2.0,
        )
        self.assertTrue(math.isfinite(value))
        self.assertAlmostEqual(value, 2_000.0, places=12)

        log_N, log_D = optimal_log_allocation(
            E=1.0,
            A=1e300,
            B=1e-300,
            alpha=0.5,
            beta=2.0,
            kappa=1e-300,
            C=1e300,
        )
        self.assertTrue(math.isfinite(log_N))
        self.assertTrue(math.isfinite(log_D))
        self.assertAlmostEqual(
            log_N + log_D,
            math.log(1e300) - math.log(1e-300),
            places=11,
        )

    def test_randomized_closed_form_satisfies_constraint_and_marginal_balance(self):
        """thm-compute-optimal-allocation obeys both defining equations."""
        rng = random.Random(13_001)
        for _ in range(400):
            A = math.exp(rng.uniform(-8.0, 8.0))
            B = math.exp(rng.uniform(-8.0, 8.0))
            alpha = rng.uniform(0.15, 3.0)
            beta = rng.uniform(0.15, 3.0)
            kappa = math.exp(rng.uniform(-5.0, 5.0))
            C = math.exp(rng.uniform(-8.0, 12.0))
            log_N, log_D = optimal_log_allocation(
                E=rng.uniform(0.0, 20.0),
                A=A,
                B=B,
                alpha=alpha,
                beta=beta,
                kappa=kappa,
                C=C,
            )

            self.assertAlmostEqual(
                math.log(kappa) + log_N + log_D, math.log(C), places=11
            )
            parameter_marginal = (
                math.log(alpha) + math.log(A) - alpha * log_N
            )
            data_marginal = math.log(beta) + math.log(B) - beta * log_D
            self.assertAlmostEqual(parameter_marginal, data_marginal, places=11)

    def test_closed_form_matches_independent_log_space_minimization(self):
        """An independent optimizer recovers thm-compute-optimal-allocation."""
        rng = random.Random(13_002)
        for _ in range(120):
            values = {
                "A": math.exp(rng.uniform(-6.0, 6.0)),
                "B": math.exp(rng.uniform(-6.0, 6.0)),
                "alpha": rng.uniform(0.2, 2.5),
                "beta": rng.uniform(0.2, 2.5),
                "kappa": math.exp(rng.uniform(-4.0, 4.0)),
                "C": math.exp(rng.uniform(-8.0, 12.0)),
            }
            expected_N, expected_D = optimal_log_allocation(E=0.0, **values)
            actual_N, actual_D, actual_loss = independently_minimize_log_excess(
                **values
            )
            expected_loss = log_excess_loss_from_logs(
                expected_N,
                expected_D,
                A=values["A"],
                B=values["B"],
                alpha=values["alpha"],
                beta=values["beta"],
            )
            self.assertAlmostEqual(actual_N, expected_N, delta=2e-7)
            self.assertAlmostEqual(actual_D, expected_D, delta=2e-7)
            self.assertAlmostEqual(actual_loss, expected_loss, places=11)

    def test_compute_preserving_global_perturbations_raise_loss(self):
        """thm-compute-optimal-allocation is the unique global minimum."""
        rng = random.Random(13_003)
        perturbations = (-12.0, -4.0, -1.0, -0.05, 0.05, 1.0, 4.0, 12.0)
        for _ in range(100):
            values = {
                "A": math.exp(rng.uniform(-5.0, 5.0)),
                "B": math.exp(rng.uniform(-5.0, 5.0)),
                "alpha": rng.uniform(0.2, 2.5),
                "beta": rng.uniform(0.2, 2.5),
                "kappa": math.exp(rng.uniform(-3.0, 3.0)),
                "C": math.exp(rng.uniform(-6.0, 10.0)),
            }
            log_N, log_D = optimal_log_allocation(E=0.0, **values)
            optimum = log_excess_loss_from_logs(
                log_N,
                log_D,
                A=values["A"],
                B=values["B"],
                alpha=values["alpha"],
                beta=values["beta"],
            )
            for shift in perturbations:
                perturbed = log_excess_loss_from_logs(
                    log_N + shift,
                    log_D - shift,
                    A=values["A"],
                    B=values["B"],
                    alpha=values["alpha"],
                    beta=values["beta"],
                )
                self.assertGreater(perturbed, optimum)

    def test_lagrange_multiplier_is_consistent_in_both_coordinates(self):
        """The multiplier in thm-compute-optimal-allocation is stationary."""
        rng = random.Random(13_004)
        for _ in range(250):
            values = {
                "A": math.exp(rng.uniform(-7.0, 7.0)),
                "B": math.exp(rng.uniform(-7.0, 7.0)),
                "alpha": rng.uniform(0.15, 3.0),
                "beta": rng.uniform(0.15, 3.0),
                "kappa": math.exp(rng.uniform(-4.0, 4.0)),
                "C": math.exp(rng.uniform(-7.0, 12.0)),
            }
            log_N, log_D = optimal_log_allocation(E=0.0, **values)
            from_N, from_D = optimal_log_multiplier(
                log_N,
                log_D,
                A=values["A"],
                B=values["B"],
                alpha=values["alpha"],
                beta=values["beta"],
                C=values["C"],
            )
            self.assertAlmostEqual(from_N, from_D, places=11)

            # |dL/dN| = lambda kappa D and |dL/dD| = lambda kappa N.
            N_loss_gradient = (
                math.log(values["alpha"])
                + math.log(values["A"])
                - (values["alpha"] + 1.0) * log_N
            )
            N_constraint_gradient = (
                from_N + math.log(values["kappa"]) + log_D
            )
            D_loss_gradient = (
                math.log(values["beta"])
                + math.log(values["B"])
                - (values["beta"] + 1.0) * log_D
            )
            D_constraint_gradient = (
                from_D + math.log(values["kappa"]) + log_N
            )
            self.assertAlmostEqual(N_loss_gradient, N_constraint_gradient, places=11)
            self.assertAlmostEqual(D_loss_gradient, D_constraint_gradient, places=11)

    def test_multiplier_is_negative_value_derivative(self):
        """lambda is the magnitude, not the sign, of marginal loss reduction."""

        def optimal_excess(C: float) -> float:
            log_N, log_D = optimal_log_allocation(
                E=7.0,
                A=1.0,
                B=1.0,
                alpha=1.0,
                beta=2.0,
                kappa=1.0,
                C=C,
            )
            return math.exp(
                log_excess_loss_from_logs(
                    log_N, log_D, A=1.0, B=1.0, alpha=1.0, beta=2.0
                )
            )

        C = 32.0
        step = 1e-3
        value_derivative = (
            optimal_excess(C + step) - optimal_excess(C - step)
        ) / (2.0 * step)
        log_N, log_D = optimal_log_allocation(
            E=7.0,
            A=1.0,
            B=1.0,
            alpha=1.0,
            beta=2.0,
            kappa=1.0,
            C=C,
        )
        from_N, from_D = optimal_log_multiplier(
            log_N,
            log_D,
            A=1.0,
            B=1.0,
            alpha=1.0,
            beta=2.0,
            C=C,
        )
        self.assertAlmostEqual(math.exp(from_N), 1.0 / 256.0, places=12)
        self.assertAlmostEqual(from_N, from_D, places=12)
        self.assertAlmostEqual(value_derivative, -math.exp(from_N), places=10)

    def test_allocation_is_invariant_to_additive_floor_E(self):
        """The E term in def-separable-scaling-law cannot move the optimum."""
        parameters = {
            "A": 3.5,
            "B": 0.7,
            "alpha": 0.43,
            "beta": 0.71,
            "kappa": 6.0,
            "C": 9.0e6,
        }
        baseline = optimal_log_allocation(E=0.0, **parameters)
        for E in (-100.0, -0.25, 1.0, 1e12):
            self.assertEqual(optimal_log_allocation(E=E, **parameters), baseline)

    def test_equal_exponents_give_square_roots_and_constant_ratio(self):
        """cor-equal-exponent-allocation has sqrt(C) growth and fixed N/D."""
        rng = random.Random(13_005)
        for _ in range(200):
            A = math.exp(rng.uniform(-7.0, 7.0))
            B = math.exp(rng.uniform(-7.0, 7.0))
            gamma = rng.uniform(0.1, 3.0)
            kappa = math.exp(rng.uniform(-4.0, 4.0))
            C = math.exp(rng.uniform(-7.0, 12.0))
            log_N, log_D = optimal_log_allocation(
                E=0.0,
                A=A,
                B=B,
                alpha=gamma,
                beta=gamma,
                kappa=kappa,
                C=C,
            )
            expected_N = 0.5 * (
                (math.log(A) - math.log(B)) / gamma
                + math.log(C)
                - math.log(kappa)
            )
            expected_D = 0.5 * (
                (math.log(B) - math.log(A)) / gamma
                + math.log(C)
                - math.log(kappa)
            )
            self.assertAlmostEqual(log_N, expected_N, places=11)
            self.assertAlmostEqual(log_D, expected_D, places=11)
            self.assertAlmostEqual(
                log_N - log_D, math.log(A / B) / gamma, places=11
            )

            scaled_N, scaled_D = optimal_log_allocation(
                E=0.0,
                A=A,
                B=B,
                alpha=gamma,
                beta=gamma,
                kappa=kappa,
                C=25.0 * C,
            )
            self.assertAlmostEqual(scaled_N - log_N, math.log(5.0), places=11)
            self.assertAlmostEqual(scaled_D - log_D, math.log(5.0), places=11)
            self.assertAlmostEqual(scaled_N - scaled_D, log_N - log_D, places=11)

    def test_unequal_exponents_change_ratio_and_only_weighted_terms_balance(self):
        """Unequal exponents vary D*/N* with C and need not equal raw terms."""
        alpha = 1.0
        beta = 2.0
        first_C = 32.0
        budget_ratio = 64.0
        first_N, first_D = optimal_log_allocation(
            E=0.0,
            A=1.0,
            B=1.0,
            alpha=alpha,
            beta=beta,
            kappa=1.0,
            C=first_C,
        )
        second_N, second_D = optimal_log_allocation(
            E=0.0,
            A=1.0,
            B=1.0,
            alpha=alpha,
            beta=beta,
            kappa=1.0,
            C=first_C * budget_ratio,
        )
        observed_log_ratio_change = (second_D - second_N) - (first_D - first_N)
        expected_log_ratio_change = (
            (alpha - beta) / (alpha + beta) * math.log(budget_ratio)
        )
        self.assertAlmostEqual(
            observed_log_ratio_change, expected_log_ratio_change, places=11
        )
        self.assertNotAlmostEqual(observed_log_ratio_change, 0.0, places=11)

        parameter_term = math.exp(-alpha * first_N)
        data_term = math.exp(-beta * first_D)
        self.assertNotAlmostEqual(parameter_term, data_term, places=12)
        self.assertAlmostEqual(
            alpha * parameter_term, beta * data_term, places=12
        )

    def test_unequal_exponent_numeric_trace(self):
        """The chapter trace A=B=kappa=1, alpha=1, beta=2, C=32 is exact."""
        log_N, log_D = optimal_log_allocation(
            E=7.0,
            A=1.0,
            B=1.0,
            alpha=1.0,
            beta=2.0,
            kappa=1.0,
            C=32.0,
        )
        self.assertAlmostEqual(math.exp(log_N), 8.0, places=12)
        self.assertAlmostEqual(math.exp(log_D), 4.0, places=12)
        self.assertAlmostEqual(training_compute_proxy(8.0, 4.0, 1.0), 32.0)
        self.assertAlmostEqual(1.0 / 8.0, 2.0 / (4.0**2))
        self.assertAlmostEqual(
            math.exp(
                log_excess_loss(
                    8.0, 4.0, A=1.0, B=1.0, alpha=1.0, beta=2.0
                )
            ),
            3.0 / 16.0,
        )
        optimum = 3.0 / 16.0
        model_heavy = 1.0 / 16.0 + 1.0 / (2.0**2)
        data_heavy = 1.0 / 4.0 + 1.0 / (8.0**2)
        equal_split = 1.0 / math.sqrt(32.0) + 1.0 / 32.0
        self.assertAlmostEqual(model_heavy, 5.0 / 16.0)
        self.assertAlmostEqual(data_heavy, 17.0 / 64.0)
        self.assertGreater(model_heavy, optimum)
        self.assertGreater(data_heavy, optimum)
        self.assertGreater(equal_split, optimum)
        from_N, from_D = optimal_log_multiplier(
            log_N,
            log_D,
            A=1.0,
            B=1.0,
            alpha=1.0,
            beta=2.0,
            C=32.0,
        )
        self.assertAlmostEqual(math.exp(from_N), 1.0 / 256.0)
        self.assertAlmostEqual(from_N, from_D, places=12)

    def test_optimal_excess_loss_has_the_claimed_compute_rate(self):
        """prop-optimal-excess-loss-rate is C^(-alpha beta/(alpha+beta))."""
        rng = random.Random(13_006)
        for _ in range(250):
            A = math.exp(rng.uniform(-6.0, 6.0))
            B = math.exp(rng.uniform(-6.0, 6.0))
            alpha = rng.uniform(0.15, 3.0)
            beta = rng.uniform(0.15, 3.0)
            kappa = math.exp(rng.uniform(-4.0, 4.0))
            first_C = math.exp(rng.uniform(-7.0, 8.0))
            ratio = math.exp(rng.uniform(0.1, 8.0))
            second_C = first_C * ratio

            first_N, first_D = optimal_log_allocation(
                E=0.0,
                A=A,
                B=B,
                alpha=alpha,
                beta=beta,
                kappa=kappa,
                C=first_C,
            )
            second_N, second_D = optimal_log_allocation(
                E=1e9,
                A=A,
                B=B,
                alpha=alpha,
                beta=beta,
                kappa=kappa,
                C=second_C,
            )
            first_loss = log_excess_loss_from_logs(
                first_N, first_D, A=A, B=B, alpha=alpha, beta=beta
            )
            second_loss = log_excess_loss_from_logs(
                second_N, second_D, A=A, B=B, alpha=alpha, beta=beta
            )
            expected_change = -(alpha * beta / (alpha + beta)) * math.log(ratio)
            self.assertAlmostEqual(second_loss - first_loss, expected_change, places=10)

    def test_optimum_rejects_nonpositive_or_nonfinite_parameters(self):
        """The fit, proxy, and optimizer require positive finite inputs."""
        valid = {
            "E": 1.0,
            "A": 2.0,
            "B": 3.0,
            "alpha": 0.5,
            "beta": 0.7,
            "kappa": 6.0,
            "C": 1e6,
        }
        for name in ("A", "B", "alpha", "beta", "kappa", "C"):
            for invalid in (0.0, -1.0, math.inf, -math.inf, math.nan):
                candidate = dict(valid)
                candidate[name] = invalid
                with self.subTest(name=name, invalid=invalid):
                    with self.assertRaises(ValueError):
                        optimal_log_allocation(**candidate)
        for invalid_E in (math.inf, -math.inf, math.nan):
            candidate = dict(valid)
            candidate["E"] = invalid_E
            with self.subTest(E=invalid_E):
                with self.assertRaises(ValueError):
                    optimal_log_allocation(**candidate)

    def test_evaluators_reject_invalid_coordinates_and_coefficients(self):
        """Definitions reject invalid domains instead of returning fake optima."""
        for invalid in (0.0, -1.0, math.inf, -math.inf, math.nan):
            with self.subTest(N=invalid):
                with self.assertRaises(ValueError):
                    training_compute_proxy(invalid, 2.0, 6.0)
            with self.subTest(compute_D=invalid):
                with self.assertRaises(ValueError):
                    training_compute_proxy(2.0, invalid, 6.0)
            with self.subTest(kappa=invalid):
                with self.assertRaises(ValueError):
                    training_compute_proxy(2.0, 3.0, invalid)
            with self.subTest(D=invalid):
                with self.assertRaises(ValueError):
                    log_excess_loss(
                        2.0,
                        invalid,
                        A=1.0,
                        B=1.0,
                        alpha=0.5,
                        beta=0.5,
                    )
        for name in ("A", "B", "alpha", "beta"):
            for invalid in (0.0, -1.0, math.inf, -math.inf, math.nan):
                parameters = {"A": 1.0, "B": 1.0, "alpha": 0.5, "beta": 0.5}
                parameters[name] = invalid
                with self.subTest(name=name, invalid=invalid):
                    with self.assertRaises(ValueError):
                        log_excess_loss(2.0, 3.0, **parameters)
        for invalid_log in (math.inf, -math.inf, math.nan):
            with self.subTest(log_N=invalid_log):
                with self.assertRaises(ValueError):
                    log_excess_loss_from_logs(
                        invalid_log,
                        0.0,
                        A=1.0,
                        B=1.0,
                        alpha=0.5,
                        beta=0.5,
                    )
            with self.subTest(log_D=invalid_log):
                with self.assertRaises(ValueError):
                    log_excess_loss_from_logs(
                        0.0,
                        invalid_log,
                        A=1.0,
                        B=1.0,
                        alpha=0.5,
                        beta=0.5,
                    )


if __name__ == "__main__":
    unittest.main()
