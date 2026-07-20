"""Executable guards for the Chapters 18--23 proof-audit repairs.

Covered targets: prop-selective-scan, thm-semiseparable,
prop-mlstm-gated-state, def-resampler, prop-resampler-convex,
prop-resampler-cost, prop-connector-data-processing-bound,
thm-ste-identity, prop-vq-gradient, thm-codebook-kmeans, prop-merged-vocab,
def-mixed-mask, def-retrieval,
prop-recall-accuracy, and prop-perplexity-kl.
"""

from collections import Counter
import math
import unittest


def transition_multiplications(length: int, state_width: int) -> tuple[int, int]:
    """Return generic-dense and diagonal recurrence matvec counts."""
    if length <= 0 or state_width <= 0:
        raise ValueError("length and state width must be positive")
    return length * state_width**2, length * state_width


def mlstm_scalar_readouts(value: float, key: float, query: float) -> tuple[float, float]:
    """Compare the stabilized mLSTM readout with ordinary normalization."""
    cell = value * key
    normalizer = key
    score = normalizer * query
    if score == 0:
        raise ValueError("ordinary normalized linear attention is undefined")
    mlstm = cell * query / max(abs(score), 1.0)
    ordinary = cell * query / score
    return mlstm, ordinary


def resampler_output(
    raw_values: list[float], value_scale: float, output_scale: float, weights: list[float]
) -> float:
    """Form one def-resampler / prop-resampler-convex output after W^V W^O."""
    if len(raw_values) != len(weights) or not raw_values:
        raise ValueError("values and weights need the same nonzero length")
    if any(weight < 0 for weight in weights) or not math.isclose(sum(weights), 1.0):
        raise ValueError("attention weights must lie on the simplex")
    projected = [value * value_scale * output_scale for value in raw_values]
    return sum(weight * value for weight, value in zip(weights, projected))


def scalar_positional_resampler(
    contents: list[float], positions: list[float], query: float = 1.0
) -> float:
    """Evaluate the scalar q=W^K=W^V=W^O=1 positional witness."""
    if len(contents) != len(positions) or not contents:
        raise ValueError("contents and positions need the same nonzero length")
    augmented = [content + position for content, position in zip(contents, positions)]
    logits = [query * value for value in augmented]
    shift = max(logits)
    unnormalized = [math.exp(logit - shift) for logit in logits]
    denominator = sum(unnormalized)
    return sum(weight * value for weight, value in zip(unnormalized, augmented)) / denominator


def resampler_cost_proxy(layers: int, queries: int, patches: int, width: int) -> int:
    """Count L_r[m*n*d + (m+n)d^2] from prop-resampler-cost."""
    if min(layers, queries, patches, width) <= 0:
        raise ValueError("resampler dimensions must be positive")
    return layers * (queries * patches * width + (queries + patches) * width**2)


def hybrid_decode_state_bytes(
    layers: int,
    attention_layers: int,
    attention_span: int,
    width: int,
    state_width: int,
    bytes_per_element: int,
) -> int:
    """Count windowed/full attention plus recurrent per-request state."""
    if not 0 <= attention_layers <= layers or min(
        layers, attention_span, width, state_width, bytes_per_element
    ) <= 0:
        raise ValueError("hybrid dimensions lie outside their domains")
    recurrent_layers = layers - attention_layers
    return (
        attention_layers * 2 * attention_span * width
        + recurrent_layers * state_width * width
    ) * bytes_per_element


def entropy(values: list[object]) -> float:
    """Shannon entropy in nats for an empirical finite distribution."""
    if not values:
        raise ValueError("entropy needs a nonempty sample space")
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * math.log(count / total) for count in counts.values())


def joint(*columns: list[object]) -> list[tuple[object, ...]]:
    """Zip equally weighted random variables into a joint variable."""
    if not columns or len({len(column) for column in columns}) != 1:
        raise ValueError("joint variables need equal nonzero sample spaces")
    if not columns[0]:
        raise ValueError("joint variables need equal nonzero sample spaces")
    return list(zip(*columns))


def mutual_information(left: list[object], right: list[object]) -> float:
    """Compute empirical I(left; right) in nats."""
    return entropy(left) + entropy(right) - entropy(joint(left, right))


def conditional_mutual_information(
    left: list[object], right: list[object], context: list[object]
) -> float:
    """Compute empirical I(left; right | context) in nats."""
    return (
        entropy(joint(left, context))
        + entropy(joint(right, context))
        - entropy(context)
        - entropy(joint(left, right, context))
    )


def cell_objective(points: list[float], code: float) -> float:
    """Return the fixed-assignment VQ codebook objective for one cell."""
    return sum((point - code) ** 2 for point in points)


def centroid_or_none(points: list[float]) -> float | None:
    """Return a nonempty-cell centroid; an empty cell is unconstrained."""
    return sum(points) / len(points) if points else None


def mixed_mask(
    segments: list[str], context_image_segments: set[str]
) -> list[list[bool]]:
    """Build def-mixed-mask with bidirectionality only in observed images."""
    if not segments:
        raise ValueError("a mask needs at least one position")
    return [
        [
            key <= query
            or (
                segments[query] == segments[key]
                and segments[query] in context_image_segments
            )
            for key in range(len(segments))
        ]
        for query in range(len(segments))
    ]


def deterministic_rank(scores: list[float], true_index: int) -> int:
    """Rank by decreasing score and then increasing candidate index."""
    if not scores or not 0 <= true_index < len(scores):
        raise ValueError("rank arguments lie outside their domains")
    ordering = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    return ordering.index(true_index) + 1


def retrieval_ranks(score_rows: list[list[float]], true_indices: list[int]) -> list[int]:
    """Evaluate def-retrieval on a finite nonempty query set."""
    if not score_rows or len(score_rows) != len(true_indices):
        raise ValueError("the retrieval query set must be finite and nonempty")
    return [
        deterministic_rank(scores, true_index)
        for scores, true_index in zip(score_rows, true_indices)
    ]


def tie_adjusted_auroc(similarities: list[list[float]]) -> float:
    """Pool a B>=2 matched diagonal against all off-diagonal negatives."""
    batch = len(similarities)
    if batch < 2 or any(len(row) != batch for row in similarities):
        raise ValueError("in-batch AUROC needs a square matrix with B >= 2")
    positives = [similarities[index][index] for index in range(batch)]
    negatives = [
        similarities[row][column]
        for row in range(batch)
        for column in range(batch)
        if row != column
    ]
    credit = sum(
        1.0 if positive > negative else 0.5 if positive == negative else 0.0
        for positive in positives
        for negative in negatives
    )
    return credit / (len(positives) * len(negatives))


def distribution_entropy(probabilities: tuple[float, ...]) -> float:
    """Entropy in nats, using 0 log 0 = 0."""
    return -sum(probability * math.log(probability) for probability in probabilities if probability)


def kl_divergence(
    data: tuple[float, ...], model: tuple[float, ...]
) -> float:
    """Return D_KL(data || model) on one finite support."""
    return sum(
        probability * math.log(probability / estimate)
        for probability, estimate in zip(data, model)
        if probability
    )


def per_token_cross_entropy(
    data: tuple[float, ...], model: tuple[float, ...], length: int
) -> float:
    """Expected complete-sequence log-loss divided by exact target length."""
    if length <= 0 or len(data) != len(model):
        raise ValueError("distribution supports and target length must be valid")
    if not math.isclose(sum(data), 1.0) or not math.isclose(sum(model), 1.0):
        raise ValueError("probabilities must sum to one")
    if any(probability < 0 for probability in data) or any(
        estimate <= 0 for estimate in model
    ):
        raise ValueError("this finite test uses nonnegative data and positive models")
    return -sum(probability * math.log(estimate) for probability, estimate in zip(data, model)) / length


def matrix_product(
    left: list[list[float]], right: list[list[float]]
) -> list[list[float]]:
    """Multiply two nonempty aligned dense matrices."""
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions must align")
    return [
        [
            sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transfer_matrix(
    transitions: list[list[list[float]]],
    writes: list[list[float]],
    reads: list[list[float]],
) -> list[list[float]]:
    """Materialize the scalar-input selective-SSM transfer matrix."""
    length = len(transitions)
    state_width = len(writes[0])
    if not (length == len(writes) == len(reads)):
        raise ValueError("time-indexed coefficients must align")
    identity = [
        [1.0 if row == column else 0.0 for column in range(state_width)]
        for row in range(state_width)
    ]
    result = [[0.0 for _ in range(length)] for _ in range(length)]
    for output_index in range(length):
        for input_index in range(output_index + 1):
            propagation = identity
            for step in range(input_index + 1, output_index + 1):
                propagation = matrix_product(transitions[step], propagation)
            propagated_write = [
                sum(propagation[row][column] * writes[input_index][column] for column in range(state_width))
                for row in range(state_width)
            ]
            result[output_index][input_index] = sum(
                reads[output_index][index] * propagated_write[index]
                for index in range(state_width)
            )
    return result


def numerical_rank(matrix: list[list[float]], tolerance: float = 1e-10) -> int:
    """Compute rank by Gaussian elimination for a small dense matrix."""
    reduced = [row[:] for row in matrix]
    rows = len(reduced)
    columns = len(reduced[0])
    pivot_row = 0
    for column in range(columns):
        pivot = max(range(pivot_row, rows), key=lambda row: abs(reduced[row][column]))
        if abs(reduced[pivot][column]) <= tolerance:
            continue
        reduced[pivot_row], reduced[pivot] = reduced[pivot], reduced[pivot_row]
        scale = reduced[pivot_row][column]
        reduced[pivot_row] = [value / scale for value in reduced[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = reduced[row][column]
            reduced[row] = [
                value - factor * pivot_value
                for value, pivot_value in zip(reduced[row], reduced[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def vq_routed_gradients(
    encoder_rows: list[float],
    assignments: list[int],
    codes: list[float],
    reconstruction_gradients: list[float],
    beta: float,
) -> tuple[list[float], list[float], list[float]]:
    """Return the three routed VQ gradient contributions."""
    if not len(encoder_rows) == len(assignments) == len(reconstruction_gradients) or beta <= 0:
        raise ValueError("assignments must align and beta must be positive")
    code_gradients = [0.0 for _ in codes]
    encoder_gradients = []
    for row, assignment in zip(encoder_rows, assignments):
        code_gradients[assignment] += 2.0 * (codes[assignment] - row)
        encoder_gradients.append(2.0 * beta * (row - codes[assignment]))
    return code_gradients, encoder_gradients, reconstruction_gradients[:]


def merged_softmax_factorization(
    block_logits: dict[str, list[float]],
) -> tuple[dict[str, float], dict[str, list[float]], list[float]]:
    """Factor a merged softmax into block mass and within-block softmax."""
    if not block_logits or any(not logits for logits in block_logits.values()):
        raise ValueError("each modality block needs at least one logit")
    shift = max(max(logits) for logits in block_logits.values())
    exponentials = {
        block: [math.exp(logit - shift) for logit in logits]
        for block, logits in block_logits.items()
    }
    block_sums = {block: sum(values) for block, values in exponentials.items()}
    total = sum(block_sums.values())
    route = {block: value / total for block, value in block_sums.items()}
    conditional = {
        block: [value / block_sums[block] for value in values]
        for block, values in exponentials.items()
    }
    merged = [
        value / total
        for values in exponentials.values()
        for value in values
    ]
    return route, conditional, merged


class MultimodalProofAuditTests(unittest.TestCase):
    def test_dense_and_diagonal_transition_costs_have_different_width_scaling(self):
        """prop-selective-scan does not turn generic dense transitions linear."""
        length, state_width = 257, 32
        dense, diagonal = transition_multiplications(length, state_width)
        self.assertEqual(dense, length * state_width**2)
        self.assertEqual(diagonal, length * state_width)
        self.assertEqual(dense // diagonal, state_width)

    def test_mlstm_state_match_does_not_imply_readout_match(self):
        """prop-mlstm-gated-state retains max(|z^Tq|,1) in the readout."""
        mlstm, ordinary = mlstm_scalar_readouts(value=2.0, key=0.5, query=1.0)
        self.assertEqual(mlstm, 1.0)
        self.assertEqual(ordinary, 2.0)
        self.assertNotEqual(mlstm, ordinary)

    def test_resampler_hull_is_the_projected_value_hull(self):
        """def-resampler and prop-resampler-convex use the W^V W^O output hull."""
        raw_values = [0.0, 1.0]
        output = resampler_output(
            raw_values, value_scale=3.0, output_scale=2.0, weights=[0.25, 0.75]
        )
        projected_values = [0.0, 6.0]
        self.assertLessEqual(min(projected_values), output)
        self.assertLessEqual(output, max(projected_values))
        self.assertGreater(output, max(raw_values))

    def test_lower_transfer_rectangle_has_state_width_rank(self):
        """thm-semiseparable factors every lower rectangle through d_s state."""
        transitions = [
            [[1.0, 0.0], [0.0, 1.0]],
            [[1.0, 1.0], [0.0, 1.0]],
            [[2.0, 0.0], [1.0, 1.0]],
            [[1.0, -1.0], [1.0, 2.0]],
            [[0.5, 1.0], [1.0, 0.0]],
            [[1.0, 0.5], [-1.0, 1.0]],
        ]
        writes = [[1.0 + index, (-1.0) ** index] for index in range(6)]
        reads = [[1.0, 0.5 + index] for index in range(6)]
        transfer = transfer_matrix(transitions, writes, reads)
        rectangle = [[transfer[row][column] for column in range(3)] for row in range(3, 6)]
        self.assertEqual(numerical_rank(rectangle), 2)
        self.assertLessEqual(numerical_rank(rectangle), len(writes[0]))

    def test_hybrid_decode_state_is_constant_only_for_fixed_windows(self):
        """prop-decode-state is n-independent for fixed windows, not full attention."""
        layers, attention_layers = 32, 4
        width, state_width, byte_width = 4_096, 16, 2
        windowed = hybrid_decode_state_bytes(
            layers, attention_layers, 1_024, width, state_width, byte_width
        )
        self.assertEqual(windowed, 70_778_880)
        full_short = hybrid_decode_state_bytes(
            layers, attention_layers, 65_536, width, state_width, byte_width
        )
        full_long = hybrid_decode_state_bytes(
            layers, attention_layers, 262_144, width, state_width, byte_width
        )
        self.assertGreater(full_short, windowed)
        self.assertAlmostEqual(
            (full_long - (layers - attention_layers) * state_width * width * byte_width)
            / (full_short - (layers - attention_layers) * state_width * width * byte_width),
            4.0,
        )

    def test_resampler_cost_includes_latent_and_visual_width_terms(self):
        """prop-resampler-cost includes (m+n)d^2 as well as mnd."""
        layers, queries, patches, width = 6, 64, 576, 1_024
        interaction = layers * queries * patches * width
        visual_width = layers * patches * width**2
        latent_width = layers * queries * width**2
        self.assertEqual(
            resampler_cost_proxy(layers, queries, patches, width),
            interaction + visual_width + latent_width,
        )
        self.assertGreater(latent_width, 0)

    def test_position_codes_break_patch_permutation_invariance_by_witness(self):
        """Exercise 20.2 gives outputs approximately 2.8577 and 1.7311."""
        original = scalar_positional_resampler([0.0, 1.0], [0.0, 2.0])
        swapped = scalar_positional_resampler([1.0, 0.0], [0.0, 2.0])
        self.assertTrue(math.isclose(original, 2.8577223804673))
        self.assertTrue(math.isclose(swapped, 1.7310585786300))
        self.assertNotEqual(original, swapped)

    def test_connector_dpi_must_condition_on_separately_supplied_context(self):
        """prop-connector-data-processing-bound can fail unconditionally."""
        context = [0, 0, 1, 1]
        connector = [0, 1, 0, 1]
        image = list(zip(context, connector))
        prediction = list(zip(context, connector))

        self.assertTrue(
            math.isclose(mutual_information(image, prediction), 2 * math.log(2))
        )
        self.assertTrue(
            math.isclose(mutual_information(image, connector), math.log(2))
        )
        self.assertGreater(
            mutual_information(image, prediction),
            mutual_information(image, connector),
        )
        self.assertTrue(
            math.isclose(
                conditional_mutual_information(image, prediction, context),
                conditional_mutual_information(image, connector, context),
            )
        )

    def test_empty_vq_cell_has_no_centroid_constraint(self):
        """thm-codebook-kmeans handles an empty cell without dividing by zero."""
        self.assertIsNone(centroid_or_none([]))
        self.assertEqual(cell_objective([], -10.0), 0.0)
        self.assertEqual(cell_objective([], 123.0), 0.0)
        self.assertEqual(centroid_or_none([1.0, 2.0, 3.0]), 2.0)

    def test_vq_stop_gradient_routes_codebook_and_commitment_terms(self):
        """thm-ste-identity copies downstream gradients; prop-vq-gradient adds direct terms."""
        encoder_rows = [1.0, 2.0, 8.0]
        assignments = [0, 0, 1]
        codes = [0.5, 10.0]
        reconstruction_gradient = [3.0, -2.0, 5.0]
        code_gradients, encoder_gradients, reconstruction_to_encoder = vq_routed_gradients(
            encoder_rows,
            assignments,
            codes,
            reconstruction_gradients=reconstruction_gradient,
            beta=0.25,
        )
        self.assertEqual(code_gradients, [-4.0, 4.0])
        self.assertEqual(encoder_gradients, [0.25, 0.75, -1.0])
        self.assertEqual(reconstruction_to_encoder, reconstruction_gradient)
        total_encoder_gradient = [
            direct + copied
            for direct, copied in zip(encoder_gradients, reconstruction_to_encoder)
        ]
        self.assertEqual(total_encoder_gradient, [3.25, -1.25, 4.0])
        self.assertNotEqual(total_encoder_gradient, reconstruction_gradient)

    def test_merged_softmax_factors_exactly_through_block_mass(self):
        """prop-merged-vocab uses the exact route probability Z_c / sum Z_c'."""
        logits = {"text": [1.5, -0.5], "image": [0.25, 2.0, -1.0]}
        route, conditional, merged = merged_softmax_factorization(logits)
        reconstructed = [
            route[block] * probability
            for block in logits
            for probability in conditional[block]
        ]
        self.assertTrue(math.isclose(sum(route.values()), 1.0))
        self.assertTrue(all(math.isclose(sum(row), 1.0) for row in conditional.values()))
        self.assertEqual(len(reconstructed), len(merged))
        self.assertTrue(
            all(math.isclose(left, right) for left, right in zip(reconstructed, merged))
        )

    def test_only_observed_image_context_is_bidirectional(self):
        """def-mixed-mask keeps tokenwise-generated image spans causal."""
        segments = ["text", "image-context", "image-context", "image-target", "image-target"]
        mask = mixed_mask(segments, {"image-context"})
        self.assertTrue(mask[1][2])
        self.assertFalse(mask[3][4])
        self.assertTrue(mask[4][3])
        self.assertFalse(mask[2][3])

        text_only = mixed_mask(["text", "text", "text"], set())
        self.assertEqual(
            text_only,
            [[True, False, False], [True, True, False], [True, True, True]],
        )

    def test_retrieval_domains_tie_rule_and_half_tie_auroc(self):
        """def-retrieval and prop-recall-accuracy make tie semantics explicit."""
        with self.assertRaises(ValueError):
            retrieval_ranks([], [])
        with self.assertRaises(ValueError):
            tie_adjusted_auroc([[0.5]])

        ranks = retrieval_ranks([[0.8, 0.5], [0.2, 0.5]], [0, 1])
        self.assertEqual(ranks, [1, 1])
        auroc = tie_adjusted_auroc([[0.8, 0.5], [0.2, 0.5]])
        self.assertEqual(auroc, 0.875)
        self.assertNotEqual(auroc, 0.75)

    def test_perplexity_keeps_one_over_t_and_kl_projection(self):
        """prop-perplexity-kl preserves the exact 1/T and family projection."""
        data = (0.4, 0.3, 0.2, 0.1)
        model = (0.35, 0.25, 0.25, 0.15)
        length = 2
        observed = per_token_cross_entropy(data, model, length)
        decomposition = (
            distribution_entropy(data) + kl_divergence(data, model)
        ) / length
        self.assertTrue(math.isclose(observed, decomposition))

        restricted = (
            (0.45, 0.25, 0.20, 0.10),
            (0.25, 0.25, 0.25, 0.25),
        )
        cross_entropies = [
            per_token_cross_entropy(data, candidate, length)
            for candidate in restricted
        ]
        divergences = [kl_divergence(data, candidate) for candidate in restricted]
        perplexities = [math.exp(loss) for loss in cross_entropies]
        self.assertEqual(cross_entropies.index(min(cross_entropies)), 0)
        self.assertEqual(divergences.index(min(divergences)), 0)
        self.assertEqual(perplexities.index(min(perplexities)), 0)


if __name__ == "__main__":
    unittest.main()
