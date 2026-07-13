"""Executable guards for the preference-optimization derivations in Chapter 11.

The first family checks def-kl-regularized-reward-objective, the Gibbs policy,
and exact objective-gap identity in
thm-kl-regularized-policy-optimum, including the support and temperature
assumptions.  The second independently follows reward-policy inversion through
the Bradley--Terry substitution that gives thm-dpo-objective, then checks the
scalar pair-loss derivatives in prop-dpo-pair-gradient.  The last family checks
the comparison-graph qualification in prop-dpo-population-optimum.  Everything
is stdlib-only, deterministic, and independent of MDX parsing.
"""

import math
import random
import unittest


def _require_positive_beta(beta: float) -> None:
    """Enforce the beta > 0 assumption used by every Gibbs/DPO result."""
    if not math.isfinite(beta) or beta <= 0.0:
        raise ValueError("beta must be finite and strictly positive")


def _validate_distribution(
    probabilities: list[float], *, require_positive: bool
) -> None:
    """Validate a finite probability row, optionally requiring full support."""
    if not probabilities or any(not math.isfinite(value) for value in probabilities):
        raise ValueError("probability rows must be nonempty and finite")
    if require_positive:
        if any(value <= 0.0 for value in probabilities):
            raise ValueError("this identity requires strictly positive support")
    elif any(value < 0.0 for value in probabilities):
        raise ValueError("probabilities cannot be negative")
    if not math.isclose(sum(probabilities), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("probability rows must sum to one")


def normalize_positive(weights: list[float]) -> list[float]:
    """Normalize a nonempty row of finite positive weights."""
    if not weights or any(not math.isfinite(value) or value <= 0.0 for value in weights):
        raise ValueError("normalization weights must be finite and positive")
    total = sum(weights)
    return [value / total for value in weights]


def sigmoid(value: float) -> float:
    """Evaluate the logistic sigmoid without overflowing at extreme logits."""
    if value >= 0.0:
        decay = math.exp(-value)
        return 1.0 / (1.0 + decay)
    growth = math.exp(value)
    return growth / (1.0 + growth)


def bernoulli_cross_entropy(target: float, prediction: float) -> float:
    """Return binary cross-entropy for probabilities strictly inside (0, 1)."""
    if not 0.0 < target < 1.0 or not 0.0 < prediction < 1.0:
        raise ValueError("Bernoulli probabilities must lie strictly inside (0, 1)")
    return -target * math.log(prediction) - (1.0 - target) * math.log1p(
        -prediction
    )


def bernoulli_kl(target: float, prediction: float) -> float:
    """Return KL(Ber(target) || Ber(prediction))."""
    if not 0.0 < target < 1.0 or not 0.0 < prediction < 1.0:
        raise ValueError("Bernoulli probabilities must lie strictly inside (0, 1)")
    return target * math.log(target / prediction) + (1.0 - target) * math.log(
        (1.0 - target) / (1.0 - prediction)
    )


def softplus(value: float) -> float:
    """Evaluate log(1 + exp(value)) stably."""
    if value > 0.0:
        return value + math.log1p(math.exp(-value))
    return math.log1p(math.exp(value))


def kl_divergence(left: list[float], right: list[float]) -> float:
    """Return D_KL(left || right), with the usual zero-mass convention."""
    if len(left) != len(right):
        raise ValueError("KL rows must have equal length")
    _validate_distribution(left, require_positive=False)
    _validate_distribution(right, require_positive=True)
    return sum(
        probability * math.log(probability / reference)
        for probability, reference in zip(left, right)
        if probability > 0.0
    )


def gibbs_policy(
    rewards: list[float], reference: list[float], beta: float
) -> tuple[list[float], float]:
    """Return pi_r and log Z from thm-kl-regularized-policy-optimum."""
    _require_positive_beta(beta)
    if len(rewards) != len(reference) or not rewards:
        raise ValueError("rewards and reference probabilities must align")
    if any(not math.isfinite(reward) for reward in rewards):
        raise ValueError("rewards must be finite")
    _validate_distribution(reference, require_positive=True)

    log_weights = [
        math.log(probability) + reward / beta
        for probability, reward in zip(reference, rewards)
    ]
    offset = max(log_weights)
    scaled_weights = [math.exp(value - offset) for value in log_weights]
    scaled_normalizer = sum(scaled_weights)
    policy = [weight / scaled_normalizer for weight in scaled_weights]
    log_normalizer = offset + math.log(scaled_normalizer)
    return policy, log_normalizer


def regularized_reward_objective(
    policy: list[float],
    rewards: list[float],
    reference: list[float],
    beta: float,
) -> float:
    """Evaluate J(pi) = E_pi[r] - beta D_KL(pi || pi_ref)."""
    _require_positive_beta(beta)
    if len(policy) != len(rewards) or len(policy) != len(reference):
        raise ValueError("objective rows must align")
    if any(not math.isfinite(reward) for reward in rewards):
        raise ValueError("rewards must be finite")
    return sum(
        probability * reward for probability, reward in zip(policy, rewards)
    ) - beta * kl_divergence(policy, reference)


def reverse_kl_reward_objective(
    policy: list[float],
    rewards: list[float],
    reference: list[float],
    beta: float,
) -> float:
    """A deliberately different objective using D_KL(pi_ref || pi)."""
    _require_positive_beta(beta)
    if len(policy) != len(rewards) or len(policy) != len(reference):
        raise ValueError("objective rows must align")
    _validate_distribution(policy, require_positive=True)
    return sum(
        probability * reward for probability, reward in zip(policy, rewards)
    ) - beta * kl_divergence(reference, policy)


def invert_gibbs_reward(
    policy: list[float], reference: list[float], beta: float, log_z: float
) -> list[float]:
    """Evaluate r = beta log(pi/pi_ref) + beta log Z."""
    _require_positive_beta(beta)
    if len(policy) != len(reference):
        raise ValueError("policy and reference rows must align")
    _validate_distribution(policy, require_positive=True)
    _validate_distribution(reference, require_positive=True)
    if not math.isfinite(log_z):
        raise ValueError("log Z must be finite")
    return [
        beta * math.log(probability / baseline) + beta * log_z
        for probability, baseline in zip(policy, reference)
    ]


def bradley_terry_probability(winner_reward: float, loser_reward: float) -> float:
    """Evaluate def-bradley-terry-preference for one ordered response pair."""
    if not math.isfinite(winner_reward) or not math.isfinite(loser_reward):
        raise ValueError("Bradley--Terry rewards must be finite")
    return sigmoid(winner_reward - loser_reward)


def dpo_logit(
    policy: list[float],
    reference: list[float],
    winner: int,
    loser: int,
    beta: float,
) -> float:
    """Return z = beta[(log pi-log ref)_w-(log pi-log ref)_l]."""
    _require_positive_beta(beta)
    if len(policy) != len(reference):
        raise ValueError("policy and reference rows must align")
    _validate_distribution(policy, require_positive=True)
    _validate_distribution(reference, require_positive=True)
    if not 0 <= winner < len(policy) or not 0 <= loser < len(policy):
        raise ValueError("response index outside the policy support")
    winner_ratio = math.log(policy[winner]) - math.log(reference[winner])
    loser_ratio = math.log(policy[loser]) - math.log(reference[loser])
    return beta * (winner_ratio - loser_ratio)


def dpo_pair_loss_from_margin(margin: float, beta: float) -> float:
    """Stable per-pair DPO loss softplus(-beta * margin)."""
    _require_positive_beta(beta)
    if not math.isfinite(margin):
        raise ValueError("the unscaled policy margin must be finite")
    return softplus(-beta * margin)


def dpo_pair_derivatives(margin: float, beta: float) -> tuple[float, float]:
    """Return first and second derivatives of the DPO loss in its margin."""
    _require_positive_beta(beta)
    if not math.isfinite(margin):
        raise ValueError("the unscaled policy margin must be finite")
    z = beta * margin
    negative_probability = sigmoid(-z)
    positive_probability = sigmoid(z)
    gradient = -beta * negative_probability
    hessian = beta * beta * positive_probability * negative_probability
    return gradient, hessian


def connected_components(
    node_count: int, edges: list[tuple[int, int]]
) -> list[set[int]]:
    """Return the undirected connected components of a comparison graph."""
    if node_count <= 0:
        raise ValueError("a comparison graph needs at least one response")
    adjacency = [set() for _ in range(node_count)]
    for left, right in edges:
        if not 0 <= left < node_count or not 0 <= right < node_count:
            raise ValueError("comparison endpoint outside the response set")
        adjacency[left].add(right)
        adjacency[right].add(left)

    remaining = set(range(node_count))
    components: list[set[int]] = []
    while remaining:
        seed = min(remaining)
        component = {seed}
        frontier = [seed]
        remaining.remove(seed)
        while frontier:
            node = frontier.pop()
            for neighbor in adjacency[node]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    frontier.append(neighbor)
        components.append(component)
    return components


def recover_scores_from_comparisons(
    node_count: int, comparisons: list[tuple[int, int, float]]
) -> tuple[list[float], list[set[int]]]:
    """Recover scores from exact directed differences, anchoring each component."""
    edges = [(left, right) for left, right, _ in comparisons]
    components = connected_components(node_count, edges)
    adjacency: list[list[tuple[int, float]]] = [[] for _ in range(node_count)]
    for left, right, difference in comparisons:
        # difference = score[left] - score[right].
        adjacency[left].append((right, -difference))
        adjacency[right].append((left, difference))

    recovered: list[float | None] = [None] * node_count
    for component in components:
        anchor = min(component)
        recovered[anchor] = 0.0
        frontier = [anchor]
        while frontier:
            node = frontier.pop()
            node_score = recovered[node]
            assert node_score is not None
            for neighbor, increment in adjacency[node]:
                proposed = node_score + increment
                if recovered[neighbor] is None:
                    recovered[neighbor] = proposed
                    frontier.append(neighbor)
                elif not math.isclose(
                    recovered[neighbor], proposed, rel_tol=1e-12, abs_tol=1e-12
                ):
                    raise ValueError("comparison differences are inconsistent")
    return [score if score is not None else 0.0 for score in recovered], components


class KLRegularizedPolicyTests(unittest.TestCase):
    def test_randomized_gibbs_gap_identity_and_normalization(self):
        """thm-kl-regularized-policy-optimum's exact gap holds at pi_r."""
        generator = random.Random(2026071301)
        for case in range(400):
            response_count = generator.randint(2, 12)
            beta = math.exp(generator.uniform(math.log(0.08), math.log(5.0)))
            reference = normalize_positive([
                math.exp(generator.uniform(-5.0, 5.0))
                for _ in range(response_count)
            ])
            rewards = [generator.uniform(-8.0, 8.0) for _ in range(response_count)]
            candidate = normalize_positive([
                math.exp(generator.uniform(-5.0, 5.0))
                for _ in range(response_count)
            ])

            optimum, log_z = gibbs_policy(rewards, reference, beta)
            optimum_value = regularized_reward_objective(
                optimum, rewards, reference, beta
            )
            candidate_value = regularized_reward_objective(
                candidate, rewards, reference, beta
            )
            expected_gap = beta * kl_divergence(candidate, optimum)

            with self.subTest(case=case, responses=response_count):
                self.assertAlmostEqual(sum(optimum), 1.0, places=14)
                self.assertTrue(all(probability > 0.0 for probability in optimum))
                self.assertAlmostEqual(optimum_value, beta * log_z, places=11)
                self.assertAlmostEqual(
                    optimum_value - candidate_value,
                    expected_gap,
                    delta=3e-11 * max(1.0, abs(expected_gap)),
                )
                self.assertGreaterEqual(expected_gap, -1e-12)

    def test_prompt_constant_reward_shift_leaves_the_policy_unchanged(self):
        """A reward shift changes beta log Z, not the Gibbs policy."""
        reference = [0.51, 0.29, 0.15, 0.05]
        rewards = [-1.2, 0.4, 2.0, -0.3]
        beta = 0.73
        shift = 37.25
        policy, log_z = gibbs_policy(rewards, reference, beta)
        shifted_policy, shifted_log_z = gibbs_policy(
            [reward + shift for reward in rewards], reference, beta
        )
        for observed, expected in zip(shifted_policy, policy):
            self.assertAlmostEqual(observed, expected, places=14)
        self.assertAlmostEqual(beta * (shifted_log_z - log_z), shift, places=12)

    def test_reward_inversion_keeps_log_z_and_pairwise_cancels_it(self):
        """cor-reward-policy-inversion requires +beta log Z, which cancels in pairs."""
        generator = random.Random(2026071302)
        for case in range(200):
            response_count = generator.randint(2, 10)
            beta = generator.uniform(0.1, 4.0)
            reference = normalize_positive([
                generator.uniform(0.01, 2.0) for _ in range(response_count)
            ])
            rewards = [generator.uniform(-6.0, 6.0) for _ in range(response_count)]
            policy, log_z = gibbs_policy(rewards, reference, beta)
            recovered = invert_gibbs_reward(policy, reference, beta, log_z)
            winner, loser = generator.sample(range(response_count), 2)
            pair_logit = dpo_logit(policy, reference, winner, loser, beta)

            with self.subTest(case=case):
                for observed, expected in zip(recovered, rewards):
                    self.assertAlmostEqual(observed, expected, places=11)
                self.assertAlmostEqual(
                    pair_logit, rewards[winner] - rewards[loser], places=11
                )

    def test_reverse_kl_does_not_have_the_forward_gibbs_optimum(self):
        """Changing D_KL(pi || ref) to D_KL(ref || pi) changes the optimum."""
        reference = [0.8, 0.2]
        rewards = [0.0, 2.0]
        beta = 0.7
        forward_policy, _ = gibbs_policy(rewards, reference, beta)
        forward_q = forward_policy[1]

        def reverse_derivative(q: float) -> float:
            return (
                rewards[1]
                - rewards[0]
                + beta * (reference[1] / q - reference[0] / (1.0 - q))
            )

        self.assertAlmostEqual(
            rewards[1]
            - rewards[0]
            - beta
            * math.log(
                (forward_q / reference[1])
                / ((1.0 - forward_q) / reference[0])
            ),
            0.0,
            places=12,
        )
        self.assertGreater(abs(reverse_derivative(forward_q)), 0.5)

        lower, upper = 1e-12, 1.0 - 1e-12
        for _ in range(100):
            midpoint = (lower + upper) / 2.0
            if reverse_derivative(midpoint) > 0.0:
                lower = midpoint
            else:
                upper = midpoint
        reverse_q = (lower + upper) / 2.0
        reverse_policy = [1.0 - reverse_q, reverse_q]
        self.assertGreater(abs(reverse_q - forward_q), 0.05)
        self.assertGreater(
            reverse_kl_reward_objective(reverse_policy, rewards, reference, beta),
            reverse_kl_reward_objective(forward_policy, rewards, reference, beta),
        )

    def test_gibbs_rejects_zero_reference_support_and_nonpositive_beta(self):
        """The closed form is scoped to beta > 0 and positive reference support."""
        with self.assertRaises(ValueError):
            gibbs_policy([0.0, 1.0], [1.0, 0.0], beta=1.0)
        with self.assertRaises(ValueError):
            gibbs_policy([0.0, 1.0], [0.5, 0.5], beta=0.0)
        with self.assertRaises(ValueError):
            gibbs_policy([0.0, 1.0], [0.5, 0.5], beta=-1.0)


class DPOObjectiveTests(unittest.TestCase):
    def test_randomized_bradley_terry_substitution_equals_dpo(self):
        """thm-dpo-objective follows by substituting the Gibbs inversion into BT."""
        generator = random.Random(2026071303)
        for case in range(300):
            response_count = generator.randint(2, 10)
            beta = generator.uniform(0.05, 5.0)
            reference = normalize_positive([
                generator.uniform(0.02, 3.0) for _ in range(response_count)
            ])
            rewards = [generator.uniform(-7.0, 7.0) for _ in range(response_count)]
            policy, _ = gibbs_policy(rewards, reference, beta)
            winner, loser = generator.sample(range(response_count), 2)
            dpo_probability = sigmoid(
                dpo_logit(policy, reference, winner, loser, beta)
            )
            bt_probability = bradley_terry_probability(
                rewards[winner], rewards[loser]
            )
            with self.subTest(case=case):
                self.assertAlmostEqual(dpo_probability, bt_probability, places=12)

    def test_pair_gradient_and_hessian_match_finite_differences(self):
        """prop-dpo-pair-gradient matches independent central differences."""
        generator = random.Random(2026071304)
        step = 1e-5
        for case in range(300):
            margin = generator.uniform(-8.0, 8.0)
            beta = generator.uniform(0.08, 3.0)
            gradient, hessian = dpo_pair_derivatives(margin, beta)
            finite_gradient = (
                dpo_pair_loss_from_margin(margin + step, beta)
                - dpo_pair_loss_from_margin(margin - step, beta)
            ) / (2.0 * step)
            upper_gradient, _ = dpo_pair_derivatives(margin + step, beta)
            lower_gradient, _ = dpo_pair_derivatives(margin - step, beta)
            finite_hessian = (upper_gradient - lower_gradient) / (2.0 * step)
            with self.subTest(case=case):
                self.assertAlmostEqual(gradient, finite_gradient, delta=2e-9)
                self.assertAlmostEqual(hessian, finite_hessian, delta=2e-9)
                self.assertLess(gradient, 0.0)
                self.assertGreaterEqual(hessian, 0.0)

    def test_softplus_loss_and_derivatives_stay_stable_at_extreme_margins(self):
        """The stable per-pair form has no exp overflow at z = +/-1000."""
        positive_loss = dpo_pair_loss_from_margin(1000.0, beta=1.0)
        negative_loss = dpo_pair_loss_from_margin(-1000.0, beta=1.0)
        positive_gradient, positive_hessian = dpo_pair_derivatives(1000.0, 1.0)
        negative_gradient, negative_hessian = dpo_pair_derivatives(-1000.0, 1.0)
        for value in (
            positive_loss,
            negative_loss,
            positive_gradient,
            positive_hessian,
            negative_gradient,
            negative_hessian,
        ):
            self.assertTrue(math.isfinite(value))
        self.assertEqual(positive_loss, 0.0)
        self.assertEqual(negative_loss, 1000.0)
        self.assertEqual(positive_gradient, 0.0)
        self.assertEqual(negative_gradient, -1.0)
        self.assertEqual(positive_hessian, 0.0)
        self.assertEqual(negative_hessian, 0.0)

    def test_reference_log_ratio_cannot_be_dropped(self):
        """A raw policy preference can have the opposite sign from the DPO margin."""
        policy = [0.6, 0.4]
        reference = [0.8, 0.2]
        raw_policy_log_odds = math.log(policy[0] / policy[1])
        correct_logit = dpo_logit(policy, reference, winner=0, loser=1, beta=1.0)
        self.assertGreater(raw_policy_log_odds, 0.0)
        self.assertLess(correct_logit, 0.0)
        self.assertGreater(sigmoid(raw_policy_log_odds), 0.5)
        self.assertLess(sigmoid(correct_logit), 0.5)

    def test_deterministic_preference_has_no_finite_logistic_optimum(self):
        """For a deterministic label, loss decreases toward an unattained zero."""
        finite_margins = [-100.0, -10.0, 0.0, 10.0, 100.0]
        losses = [dpo_pair_loss_from_margin(margin, 1.0) for margin in finite_margins]
        gradients = [dpo_pair_derivatives(margin, 1.0)[0] for margin in finite_margins]
        self.assertTrue(all(left > right for left, right in zip(losses, losses[1:])))
        self.assertTrue(all(loss > 0.0 for loss in losses))
        self.assertTrue(all(gradient < 0.0 for gradient in gradients))
        distant_finite_loss = dpo_pair_loss_from_margin(700.0, 1.0)
        self.assertGreater(distant_finite_loss, 0.0)
        self.assertLess(distant_finite_loss, 1e-300)

    def test_same_response_cancels_from_both_policy_and_reference_terms(self):
        """Comparing a response with itself fixes z=0 and loss=log 2."""
        reference = [0.15, 0.35, 0.50]
        policies = ([0.70, 0.20, 0.10], [0.05, 0.15, 0.80])
        for policy in policies:
            for response in range(len(policy)):
                with self.subTest(policy=policy, response=response):
                    logit = dpo_logit(
                        list(policy), reference, response, response, beta=2.7
                    )
                    self.assertEqual(logit, 0.0)
                    self.assertAlmostEqual(softplus(-logit), math.log(2.0))
                    self.assertEqual(sigmoid(logit), 0.5)

    def test_dpo_rejects_zero_policy_or_reference_support_and_bad_beta(self):
        """Log-ratio DPO needs both compared distributions positive and beta > 0."""
        with self.assertRaises(ValueError):
            dpo_logit([1.0, 0.0], [0.5, 0.5], 0, 1, beta=1.0)
        with self.assertRaises(ValueError):
            dpo_logit([0.5, 0.5], [1.0, 0.0], 0, 1, beta=1.0)
        with self.assertRaises(ValueError):
            dpo_logit([0.5, 0.5], [0.5, 0.5], 0, 1, beta=0.0)
        with self.assertRaises(ValueError):
            dpo_pair_loss_from_margin(1.0, beta=-0.5)


class PopulationIdentificationTests(unittest.TestCase):
    def test_population_risk_decomposition_and_normalization_recover_gibbs(self):
        """Every step of prop-dpo-population-optimum holds on connected graphs."""
        generator = random.Random(2026071305)
        for case in range(200):
            response_count = generator.randint(2, 9)
            beta = generator.uniform(0.15, 3.0)
            reference = normalize_positive([
                generator.uniform(0.05, 2.0) for _ in range(response_count)
            ])
            rewards = [
                generator.uniform(-4.0, 4.0) for _ in range(response_count)
            ]
            optimum, _ = gibbs_policy(rewards, reference, beta)
            candidate = normalize_positive([
                generator.uniform(0.05, 2.0) for _ in range(response_count)
            ])

            order = list(range(response_count))
            generator.shuffle(order)
            edges = list(zip(order, order[1:]))
            comparisons = [
                (left, right, (rewards[left] - rewards[right]) / beta)
                for left, right in edges
            ]
            recovered_scores, components = recover_scores_from_comparisons(
                response_count, comparisons
            )
            recovered_policy = normalize_positive([
                baseline * math.exp(score)
                for baseline, score in zip(reference, recovered_scores)
            ])

            optimal_risk = 0.0
            candidate_risk = 0.0
            entropy_floor = 0.0
            for left, right in edges:
                target = sigmoid(rewards[left] - rewards[right])
                optimal_prediction = sigmoid(
                    dpo_logit(optimum, reference, left, right, beta)
                )
                candidate_prediction = sigmoid(
                    dpo_logit(candidate, reference, left, right, beta)
                )
                edge_entropy = bernoulli_cross_entropy(target, target)
                candidate_edge_risk = bernoulli_cross_entropy(
                    target, candidate_prediction
                )
                with self.subTest(case=case, edge=(left, right)):
                    self.assertAlmostEqual(optimal_prediction, target, places=12)
                    self.assertAlmostEqual(
                        candidate_edge_risk,
                        edge_entropy + bernoulli_kl(target, candidate_prediction),
                        places=12,
                    )
                optimal_risk += bernoulli_cross_entropy(
                    target, optimal_prediction
                )
                candidate_risk += candidate_edge_risk
                entropy_floor += edge_entropy

            with self.subTest(case=case, normalization=True):
                self.assertEqual(components, [set(range(response_count))])
                for observed, expected in zip(recovered_policy, optimum):
                    self.assertAlmostEqual(observed, expected, places=12)
                self.assertAlmostEqual(optimal_risk, entropy_floor, places=12)
                self.assertGreaterEqual(candidate_risk + 1e-12, entropy_floor)

    def test_connected_comparisons_identify_scores_up_to_one_constant(self):
        """prop-dpo-population-optimum has one prompt constant on a connected graph."""
        scores = [-1.4, 0.2, 2.1, -0.8, 0.7]
        edges = [(0, 2), (2, 1), (1, 4), (4, 3)]
        comparisons = [
            (left, right, scores[left] - scores[right]) for left, right in edges
        ]
        recovered, components = recover_scores_from_comparisons(
            len(scores), comparisons
        )
        self.assertEqual(components, [set(range(5))])
        offsets = [observed - expected for observed, expected in zip(recovered, scores)]
        self.assertTrue(all(math.isclose(offset, offsets[0]) for offset in offsets))
        for left, right in edges:
            true_probability = sigmoid(scores[left] - scores[right])
            recovered_probability = sigmoid(recovered[left] - recovered[right])
            self.assertAlmostEqual(true_probability, recovered_probability)

    def test_disconnected_comparisons_allow_independent_component_shifts(self):
        """Disconnected comparisons do not identify cross-component score offsets."""
        scores = [-1.4, 0.2, 2.1, -0.8, 0.7]
        edges = [(0, 1), (1, 2), (3, 4)]
        components = connected_components(len(scores), edges)
        self.assertEqual(components, [{0, 1, 2}, {3, 4}])
        alternative = [
            scores[index] + (7.0 if index in components[0] else -4.0)
            for index in range(len(scores))
        ]
        for left, right in edges:
            self.assertAlmostEqual(
                alternative[left] - alternative[right], scores[left] - scores[right]
            )
        self.assertNotAlmostEqual(
            alternative[0] - alternative[3], scores[0] - scores[3]
        )
        self.assertNotEqual(
            sigmoid(alternative[0] - alternative[3]),
            sigmoid(scores[0] - scores[3]),
        )


if __name__ == "__main__":
    unittest.main()
