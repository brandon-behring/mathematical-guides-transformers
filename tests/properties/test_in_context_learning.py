"""Executable guards for the constructive claims in In-Context Learning.

The first family independently checks the target-mass and value-error bounds
for thm-associative-lookup.  The second checks the hard target map in
def-vanilla-induction-map and its finite-softmax trace.  The third checks that
thm-induction-construction's finite matching mass and error formula are exact.
The fourth checks that
one gradient step on mean squared linear-regression loss is exactly the
unnormalized linear-kernel read in prop-linear-attention-gd.  Everything is
stdlib-only and deterministic.
"""

import math
import random
import unittest


def dot(left: list[float], right: list[float]) -> float:
    """Return the Euclidean inner product of two equally sized vectors."""
    if len(left) != len(right):
        raise ValueError("inner-product vectors must have equal dimension")
    return sum(x * y for x, y in zip(left, right))


def norm(vector: list[float]) -> float:
    """Return the Euclidean norm."""
    return math.sqrt(dot(vector, vector))


def softmax(scores: list[float]) -> list[float]:
    """Evaluate softmax stably over a nonempty score row."""
    if not scores:
        raise ValueError("softmax needs at least one score")
    offset = max(scores)
    exponentials = [math.exp(score - offset) for score in scores]
    normalizer = sum(exponentials)
    return [value / normalizer for value in exponentials]


def attention_read(scores: list[float], values: list[list[float]]) -> list[float]:
    """Return the convex value read induced by one softmax score row."""
    if len(scores) != len(values) or not values:
        raise ValueError("each nonempty value row needs exactly one score")
    dimension = len(values[0])
    if any(len(value) != dimension for value in values):
        raise ValueError("all values must have equal dimension")
    weights = softmax(scores)
    return [
        sum(weight * value[coordinate] for weight, value in zip(weights, values))
        for coordinate in range(dimension)
    ]


def associative_lookup_certificate(
    scores: list[float], values: list[list[float]], target: int
) -> tuple[float, float, float, float, float]:
    """Compute the quantities bounded by thm-associative-lookup.

    Returns ``(alpha_target, target_mass_lower_bound, error,
    error_upper_bound, margin)``.  The norm cap ``M`` is chosen as the largest
    observed value norm, which is the tightest valid cap for the supplied
    finite memory.
    """
    if len(scores) < 2 or len(scores) != len(values):
        raise ValueError("lookup needs at least two aligned key-value pairs")
    if target < 0 or target >= len(scores):
        raise ValueError("target index outside the memory")
    distractor_scores = [
        score for index, score in enumerate(scores) if index != target
    ]
    margin = scores[target] - max(distractor_scores)
    if margin <= 0:
        raise ValueError("the target must have a strictly positive score margin")

    weights = softmax(scores)
    alpha_target = weights[target]
    distractor_factor = (len(scores) - 1) * math.exp(-margin)
    target_mass_lower_bound = 1.0 / (1.0 + distractor_factor)

    output = attention_read(scores, values)
    target_value = values[target]
    error = norm([
        observed - expected for observed, expected in zip(output, target_value)
    ])
    value_cap = max(norm(value) for value in values)
    error_upper_bound = (
        2.0 * value_cap * distractor_factor / (1.0 + distractor_factor)
    )
    return (
        alpha_target,
        target_mass_lower_bound,
        error,
        error_upper_bound,
        margin,
    )


def token_basis(tokens: list[str]) -> dict[str, list[float]]:
    """Give each distinct token an orthonormal standard-basis vector."""
    vocabulary = sorted(set(tokens))
    return {
        token: [float(index == coordinate) for coordinate in range(len(vocabulary))]
        for index, token in enumerate(vocabulary)
    }


def ideal_induction_map(tokens: list[str]) -> list[float]:
    """Evaluate def-vanilla-induction-map at the final query position."""
    if len(tokens) < 3:
        raise ValueError("induction needs a predecessor, successor, and query")
    basis = token_basis(tokens)
    query = tokens[-1]
    successors = [
        tokens[index]
        for index in range(1, len(tokens) - 1)
        if tokens[index - 1] == query
    ]
    if not successors:
        raise ValueError("vanilla induction is undefined without a predecessor match")
    return [
        sum(basis[token][coordinate] for token in successors) / len(successors)
        for coordinate in range(len(basis))
    ]


def finite_soft_induction(tokens: list[str], scale: float) -> list[float]:
    """Evaluate thm-induction-construction's finite-softmax copy stage."""
    if len(tokens) < 3:
        raise ValueError("induction needs a predecessor, successor, and query")
    basis = token_basis(tokens)
    query = tokens[-1]
    candidate_indices = range(1, len(tokens) - 1)
    scores = [
        scale if tokens[index - 1] == query else 0.0
        for index in candidate_indices
    ]
    values = [basis[tokens[index]] for index in candidate_indices]
    return attention_read(scores, values)


def mean_squared_gradient(
    features: list[list[float]], labels: list[float], weights: list[float]
) -> list[float]:
    """Gradient of (1/(2n)) sum_i (w^T x_i - y_i)^2."""
    if not features or len(features) != len(labels):
        raise ValueError("features and labels must be nonempty and aligned")
    dimension = len(weights)
    if any(len(feature) != dimension for feature in features):
        raise ValueError("features and weights must have equal dimension")
    residuals = [dot(weights, feature) - label for feature, label in zip(features, labels)]
    return [
        sum(residual * feature[coordinate] for residual, feature in zip(residuals, features))
        / len(features)
        for coordinate in range(dimension)
    ]


def gradient_step_prediction(
    features: list[list[float]],
    labels: list[float],
    initial_weights: list[float],
    query: list[float],
    step_size: float,
) -> float:
    """Take one explicit gradient step, then evaluate the query."""
    gradient = mean_squared_gradient(features, labels, initial_weights)
    updated_weights = [
        weight - step_size * derivative
        for weight, derivative in zip(initial_weights, gradient)
    ]
    return dot(query, updated_weights)


def linear_attention_prediction(
    features: list[list[float]],
    labels: list[float],
    initial_weights: list[float],
    query: list[float],
    step_size: float,
) -> float:
    """Evaluate prop-linear-attention-gd's kernel-weighted residual read."""
    if not features or len(features) != len(labels):
        raise ValueError("features and labels must be nonempty and aligned")
    if len(query) != len(initial_weights):
        raise ValueError("query and weights must have equal dimension")
    residual_read = sum(
        dot(query, feature) * (dot(initial_weights, feature) - label)
        for feature, label in zip(features, labels)
    )
    return dot(query, initial_weights) - step_size * residual_read / len(features)


class AssociativeLookupTests(unittest.TestCase):
    def test_equal_margin_distractors_make_the_mass_bound_exact(self):
        """thm-associative-lookup's target-mass lower bound is sharp."""
        scores = [1.25, -0.75, -0.75, -0.75]
        values = [[1.0], [-1.0], [0.5], [0.0]]
        alpha, lower, _error, _upper, margin = associative_lookup_certificate(
            scores, values, target=0
        )
        self.assertEqual(margin, 2.0)
        self.assertAlmostEqual(alpha, lower, places=15)
        self.assertAlmostEqual(1.0 - alpha, 3.0 * math.exp(-2.0) / (1.0 + 3.0 * math.exp(-2.0)))

    def test_vector_read_obeys_the_declared_error_bound(self):
        """thm-associative-lookup bounds ||y-v_t|| by bounded distractor mass."""
        scores = [-1.0, 2.0, 0.0, -0.5]
        values = [[-2.0, 0.0], [1.0, -1.0], [0.0, 2.0], [1.5, 0.5]]
        alpha, lower, error, upper, margin = associative_lookup_certificate(
            scores, values, target=1
        )
        self.assertEqual(margin, 2.0)
        self.assertGreaterEqual(alpha, lower - 1e-15)
        self.assertLessEqual(error, upper + 1e-15)

    def test_random_positive_margin_memories_obey_both_bounds(self):
        """Randomized guard for every clause of thm-associative-lookup."""
        generator = random.Random(20260713)
        for case in range(400):
            memory_size = generator.randint(2, 15)
            dimension = generator.randint(1, 7)
            target = generator.randrange(memory_size)
            target_score = generator.uniform(-4.0, 4.0)
            requested_margin = generator.uniform(0.02, 8.0)
            scores = []
            for index in range(memory_size):
                if index == target:
                    scores.append(target_score)
                else:
                    extra_gap = generator.uniform(0.0, 5.0)
                    scores.append(target_score - requested_margin - extra_gap)
            values = [
                [generator.uniform(-3.0, 3.0) for _ in range(dimension)]
                for _ in range(memory_size)
            ]

            with self.subTest(case=case, memory_size=memory_size, dimension=dimension):
                alpha, lower, error, upper, margin = associative_lookup_certificate(
                    scores, values, target
                )
                self.assertGreaterEqual(margin, requested_margin - 1e-12)
                self.assertGreaterEqual(alpha, lower - 2e-14)
                self.assertLessEqual(1.0 - alpha, 1.0 - lower + 2e-14)
                self.assertLessEqual(error, upper + 2e-12)

    def test_distractor_count_cannot_be_dropped_from_the_bound(self):
        """A fixed margin loses target mass as the memory grows."""
        margin = math.log(9.0)
        two_item_mass = softmax([margin, 0.0])[0]
        ten_item_mass = softmax([margin] + [0.0] * 9)[0]
        self.assertAlmostEqual(two_item_mass, 0.9)
        self.assertAlmostEqual(ten_item_mass, 0.5)


class VanillaInductionTests(unittest.TestCase):
    def test_random_matching_sets_obey_mass_and_error_formula(self):
        """Randomized guard for every clause of thm-induction-construction."""
        generator = random.Random(241011474)
        for case in range(300):
            candidates = generator.randint(2, 20)
            matches = generator.randint(1, candidates)
            dimension = generator.randint(1, 8)
            scale = generator.uniform(0.01, 9.0)
            scores = [scale] * matches + [0.0] * (candidates - matches)
            values = []
            for _ in range(candidates):
                value = [generator.uniform(-1.0, 1.0) for _ in range(dimension)]
                value_norm = norm(value)
                values.append(
                    [coordinate / max(1.0, value_norm) for coordinate in value]
                )

            weights = softmax(scores)
            matching_mass = sum(weights[:matches])
            expected_mass = matches / (
                matches + (candidates - matches) * math.exp(-scale)
            )
            target = [
                sum(value[coordinate] for value in values[:matches]) / matches
                for coordinate in range(dimension)
            ]
            output = attention_read(scores, values)
            error = norm([
                observed - expected
                for observed, expected in zip(output, target)
            ])

            with self.subTest(case=case, candidates=candidates, matches=matches):
                self.assertAlmostEqual(matching_mass, expected_mass, places=14)
                self.assertLessEqual(error, 2.0 * (1.0 - matching_mass) + 1e-14)

    def test_unique_match_trace_is_soft_at_finite_scale(self):
        """def-vanilla-induction-map and thm-induction-construction give the exact certificate."""
        tokens = ["A", "B", "C", "A"]
        basis = token_basis(tokens)
        output = finite_soft_induction(tokens, math.log(9.0))
        b_coordinate = basis["B"].index(1.0)
        c_coordinate = basis["C"].index(1.0)
        matching_mass = output[b_coordinate]
        error = norm([
            observed - target
            for observed, target in zip(output, basis["B"])
        ])
        self.assertAlmostEqual(matching_mass, 1.0 / (1.0 + math.exp(-math.log(9.0))))
        self.assertAlmostEqual(matching_mass, 0.9)
        self.assertAlmostEqual(output[c_coordinate], 0.1)
        self.assertLessEqual(error, 2.0 * (1.0 - matching_mass))
        self.assertEqual(ideal_induction_map(tokens), basis["B"])

    def test_repeated_matches_mix_successors_instead_of_taking_latest(self):
        """The hard map averages matches; finite softmax retains nonmatch leakage."""
        tokens = ["A", "B", "A", "C", "Z", "A"]
        basis = token_basis(tokens)
        a_coordinate = basis["A"].index(1.0)
        b_coordinate = basis["B"].index(1.0)
        c_coordinate = basis["C"].index(1.0)
        z_coordinate = basis["Z"].index(1.0)

        ideal = ideal_induction_map(tokens)
        self.assertAlmostEqual(ideal[b_coordinate], 0.5)
        self.assertAlmostEqual(ideal[c_coordinate], 0.5)

        finite = finite_soft_induction(tokens, math.log(9.0))
        self.assertAlmostEqual(finite[b_coordinate], 9.0 / 20.0)
        self.assertAlmostEqual(finite[c_coordinate], 9.0 / 20.0)
        self.assertAlmostEqual(finite[a_coordinate], 1.0 / 20.0)
        self.assertAlmostEqual(finite[z_coordinate], 1.0 / 20.0)
        self.assertLess(finite[c_coordinate], 0.5)

    def test_no_match_is_outside_the_ideal_map_domain(self):
        """The soft read needs a separate null gate to implement no-match abstention."""
        tokens = ["A", "B", "C", "D"]
        with self.assertRaisesRegex(ValueError, "undefined"):
            ideal_induction_map(tokens)
        self.assertEqual(
            finite_soft_induction(tokens, 0.0),
            finite_soft_induction(tokens, 40.0),
        )


class LinearAttentionGradientDescentTests(unittest.TestCase):
    def test_chapter_trace_matches_an_explicit_gradient_step(self):
        """prop-linear-attention-gd agrees with direct parameter-space updating."""
        features = [[2.0, -1.0], [0.0, 3.0], [-1.0, 2.0]]
        labels = [1.0, -2.0, 0.5]
        initial_weights = [0.25, -0.5]
        query = [1.5, 2.0]
        step_size = 0.3

        direct = gradient_step_prediction(
            features, labels, initial_weights, query, step_size
        )
        attention = linear_attention_prediction(
            features, labels, initial_weights, query, step_size
        )
        self.assertAlmostEqual(direct, attention, places=15)

    def test_zero_initialization_reads_label_weighted_linear_kernels(self):
        """At w_0=0, the residual read reduces to +(eta/n) sum_i <q,x_i> y_i."""
        features = [[1.0, 0.0], [1.0, 2.0], [-2.0, 1.0]]
        labels = [2.0, -1.0, 3.0]
        query = [0.5, -1.0]
        step_size = 0.6
        expected = step_size * sum(
            dot(query, feature) * label
            for feature, label in zip(features, labels)
        ) / len(features)
        self.assertAlmostEqual(
            linear_attention_prediction(
                features, labels, [0.0, 0.0], query, step_size
            ),
            expected,
            places=15,
        )

    def test_random_prompts_match_direct_gradient_descent(self):
        """Randomized dimensional guard for prop-linear-attention-gd."""
        generator = random.Random(221115661)
        for case in range(500):
            dimension = generator.randint(1, 9)
            examples = generator.randint(1, 12)
            features = [
                [generator.uniform(-2.0, 2.0) for _ in range(dimension)]
                for _ in range(examples)
            ]
            labels = [generator.uniform(-3.0, 3.0) for _ in range(examples)]
            initial_weights = [generator.uniform(-1.0, 1.0) for _ in range(dimension)]
            query = [generator.uniform(-2.0, 2.0) for _ in range(dimension)]
            step_size = generator.uniform(0.0, 1.5)

            with self.subTest(case=case, dimension=dimension, examples=examples):
                direct = gradient_step_prediction(
                    features, labels, initial_weights, query, step_size
                )
                attention = linear_attention_prediction(
                    features, labels, initial_weights, query, step_size
                )
                self.assertAlmostEqual(direct, attention, places=11)

    def test_softmax_convex_read_is_not_the_signed_gd_operator(self):
        """prop-linear-attention-gd requires unnormalized signed weights."""
        features = [[1.0], [-1.0]]
        labels = [1.0, 1.0]
        query = [1.0]
        linear_gd = linear_attention_prediction(
            features, labels, [0.0], query, step_size=1.0
        )
        softmax_read = sum(
            weight * label
            for weight, label in zip(softmax([1.0, -1.0]), labels)
        )
        self.assertAlmostEqual(linear_gd, 0.0)
        self.assertAlmostEqual(softmax_read, 1.0)


if __name__ == "__main__":
    unittest.main()
