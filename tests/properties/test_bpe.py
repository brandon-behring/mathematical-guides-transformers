"""Executable guards for prop-bpe-merge-accounting.

The implementation is deliberately tiny and independent of the chapter: a
left-to-right BPE step replaces a maximal set of non-overlapping occurrences of
one ordered token pair with one fresh token.
"""

from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class MergeResult:
    tokens: tuple[str, ...]
    replacements: int
    consumed_starts: tuple[int, ...]


def merge_pair(
    tokens: tuple[str, ...], pair: tuple[str, str], merged_token: str
) -> MergeResult:
    """Replace pair occurrences greedily from left to right without overlap."""
    output: list[str] = []
    consumed_starts: list[int] = []
    position = 0
    while position < len(tokens):
        if position + 1 < len(tokens) and tokens[position : position + 2] == pair:
            output.append(merged_token)
            consumed_starts.append(position)
            position += 2
        else:
            output.append(tokens[position])
            position += 1
    return MergeResult(
        tokens=tuple(output),
        replacements=len(consumed_starts),
        consumed_starts=tuple(consumed_starts),
    )


def extend_vocabulary(vocabulary: frozenset[str], merged_token: str) -> frozenset[str]:
    """Add the one fresh symbol allocated by a BPE merge rule."""
    if merged_token in vocabulary:
        raise ValueError("the merged token must be a fresh vocabulary entry")
    return vocabulary | {merged_token}


def reconstruct(
    tokens: tuple[str, ...], merged_token: str, pair: tuple[str, str]
) -> tuple[str, ...]:
    """Expand the newly merged symbol back to its two source symbols."""
    output: list[str] = []
    for token in tokens:
        output.extend(pair if token == merged_token else (token,))
    return tuple(output)


def fixed_width_id_bits(token_count: int, vocabulary_size: int) -> int:
    """Bits for token IDs when every ID uses ceil(log2(vocabulary_size)) bits."""
    if vocabulary_size < 2:
        raise ValueError("the fixed-width counterexample needs at least two IDs")
    return token_count * (vocabulary_size - 1).bit_length()


class BpeMergeAccountingTests(unittest.TestCase):
    def test_weighted_position_count_drops_by_weighted_replacements(self):
        """prop-bpe-merge-accounting: N_(t+1) = N_t - r_t."""
        corpus = [
            (("a", "b", "a", "b", "x"), 3),
            (("x", "a", "b", "y"), 2),
        ]
        weighted_before = sum(frequency * len(tokens) for tokens, frequency in corpus)
        weighted_after = 0
        weighted_replacements = 0
        for tokens, frequency in corpus:
            result = merge_pair(tokens, ("a", "b"), "ab")
            weighted_after += frequency * len(result.tokens)
            weighted_replacements += frequency * result.replacements

        self.assertEqual(weighted_before, 23)
        self.assertEqual(weighted_replacements, 8)
        self.assertEqual(weighted_after, weighted_before - weighted_replacements)

    def test_vocabulary_grows_by_exactly_one_fresh_entry(self):
        """prop-bpe-merge-accounting: V_(t+1) = V_t + 1."""
        before = frozenset({"a", "b", "x", "y"})
        after = extend_vocabulary(before, "ab")
        self.assertEqual(after, before | {"ab"})
        self.assertEqual(len(after), len(before) + 1)

    def test_reconstruction_is_invariant_under_one_merge(self):
        """Expanding the fresh symbol recovers the exact pre-merge sequence."""
        cases = [
            (("a", "b", "a", "b", "x"), ("a", "b"), "ab"),
            (("a", "a", "a"), ("a", "a"), "aa"),
            (("x", "y", "x", "y", "z"), ("x", "y"), "xy"),
        ]
        for tokens, pair, merged_token in cases:
            with self.subTest(tokens=tokens, pair=pair):
                result = merge_pair(tokens, pair, merged_token)
                self.assertEqual(reconstruct(result.tokens, merged_token, pair), tokens)

    def test_overlapping_candidates_never_consume_a_position_twice(self):
        """Greedy replacement chooses disjoint spans even for pair (a, a)."""
        tokens = ("a", "a", "a", "a", "a")
        result = merge_pair(tokens, ("a", "a"), "aa")

        self.assertEqual(result.consumed_starts, (0, 2))
        self.assertEqual(result.tokens, ("aa", "aa", "a"))
        for left, right in zip(
            result.consumed_starts, result.consumed_starts[1:]
        ):
            self.assertGreaterEqual(right, left + 2)

    def test_shorter_sequence_need_not_use_fewer_fixed_width_id_bits(self):
        """Token-count savings alone do not imply a smaller fixed-width ID budget."""
        tokens = ("a", "b", "x")
        vocabulary = frozenset({"a", "b", "x", "y"})
        result = merge_pair(tokens, ("a", "b"), "ab")
        expanded_vocabulary = extend_vocabulary(vocabulary, "ab")

        self.assertLess(len(result.tokens), len(tokens))
        self.assertEqual(result.replacements, 1)
        self.assertEqual(
            fixed_width_id_bits(len(tokens), len(vocabulary)),
            6,  # 3 IDs x ceil(log2(4)) = 3 x 2
        )
        self.assertEqual(
            fixed_width_id_bits(len(result.tokens), len(expanded_vocabulary)),
            6,  # 2 IDs x ceil(log2(5)) = 2 x 3
        )


if __name__ == "__main__":
    unittest.main()
