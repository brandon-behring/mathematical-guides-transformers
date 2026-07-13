/**
 * Deterministic byte-pair encoding helpers.
 *
 * Training vocabulary entries have the shape
 * `{ word, count, tokens }`. Pair frequencies are weighted by `count`, ties
 * are resolved lexicographically by `(leftToken, rightToken)`, and every
 * replacement pass merges non-overlapping occurrences from left to right.
 */

export const END_OF_WORD = '</w>';

/** The weighted dictionary used in the classic BPE worked example. */
export const CLASSIC_BPE_DICTIONARY = Object.freeze([
  Object.freeze({ word: 'low', count: 5 }),
  Object.freeze({ word: 'lower', count: 2 }),
  Object.freeze({ word: 'newest', count: 6 }),
  Object.freeze({ word: 'widest', count: 3 }),
]);

function compareText(left, right) {
  if (left < right) return -1;
  if (left > right) return 1;
  return 0;
}

function comparePairs(left, right) {
  return compareText(left[0], right[0]) || compareText(left[1], right[1]);
}

function copyPair(pair) {
  if (!Array.isArray(pair) || pair.length !== 2) {
    throw new TypeError('a merge pair must be a two-token array');
  }
  return [String(pair[0]), String(pair[1])];
}

function normalizeCount(value, word) {
  const count = Number(value);
  if (!Number.isSafeInteger(count) || count <= 0) {
    throw new RangeError(`dictionary count for ${JSON.stringify(word)} must be a positive integer`);
  }
  return count;
}

function validateEndOfWord(endOfWord) {
  if (typeof endOfWord !== 'string' || endOfWord.length === 0) {
    throw new TypeError('endOfWord must be a non-empty string');
  }
  return endOfWord;
}

function normalizeDictionary(dictionary, endOfWord) {
  if (!Array.isArray(dictionary) || dictionary.length === 0) {
    throw new TypeError('dictionary must be a non-empty array');
  }

  const aggregated = new Map();
  for (const entry of dictionary) {
    const word = Array.isArray(entry) ? entry[0] : entry?.word;
    const rawCount = Array.isArray(entry) ? entry[1] : entry?.count;
    if (typeof word !== 'string' || word.length === 0) {
      throw new TypeError('every dictionary entry must have a non-empty word');
    }
    if (word.includes(endOfWord)) {
      throw new RangeError(
        'dictionary word ' + JSON.stringify(word) + ' contains the reserved end-of-word marker',
      );
    }
    const count = normalizeCount(rawCount, word);
    aggregated.set(word, (aggregated.get(word) ?? 0) + count);
  }

  return [...aggregated.entries()]
    .sort(([left], [right]) => compareText(left, right))
    .map(([word, count]) => ({
      word,
      count,
      tokens: [...word, endOfWord],
    }));
}

function copyVocabulary(vocabulary) {
  return vocabulary.map(({ word, count, tokens }) => ({
    word,
    count,
    tokens: [...tokens],
  }));
}

function accounting(vocabulary, vocabularySize) {
  const tokenCount = vocabulary.reduce(
    (total, entry) => total + entry.count * entry.tokens.length,
    0,
  );
  const bitsPerToken = Math.ceil(Math.log2(vocabularySize));
  return {
    tokenCount,
    vocabularySize,
    bitsPerToken,
    bitBudget: tokenCount * bitsPerToken,
  };
}

/**
 * Count adjacent pairs in a weighted segmented vocabulary.
 *
 * The returned array is sorted lexicographically, independent of input order.
 * An occurrence in an entry with count `c` contributes `c` to the pair count.
 */
export function pairCounts(vocabulary) {
  if (!Array.isArray(vocabulary)) {
    throw new TypeError('vocabulary must be an array');
  }

  const counts = new Map();
  for (const entry of vocabulary) {
    if (!Array.isArray(entry?.tokens)) {
      throw new TypeError('every vocabulary entry must have a tokens array');
    }
    const count = normalizeCount(entry.count, entry.word ?? entry.tokens.join(''));
    for (let index = 0; index + 1 < entry.tokens.length; index += 1) {
      const pair = [String(entry.tokens[index]), String(entry.tokens[index + 1])];
      const key = JSON.stringify(pair);
      const current = counts.get(key);
      if (current) {
        current.count += count;
      } else {
        counts.set(key, { pair, count });
      }
    }
  }

  return [...counts.values()]
    .map(({ pair, count }) => ({ pair: [...pair], count }))
    .sort((left, right) => comparePairs(left.pair, right.pair));
}

/** Merge one pair non-overlappingly from left to right without mutating input. */
export function mergePair(tokens, pair) {
  if (!Array.isArray(tokens)) {
    throw new TypeError('tokens must be an array');
  }
  const [left, right] = copyPair(pair);
  const merged = [];

  for (let index = 0; index < tokens.length;) {
    if (
      index + 1 < tokens.length &&
      String(tokens[index]) === left &&
      String(tokens[index + 1]) === right
    ) {
      merged.push(`${left}${right}`);
      index += 2;
    } else {
      merged.push(String(tokens[index]));
      index += 1;
    }
  }

  return merged;
}

function bestPair(candidates) {
  return [...candidates].sort(
    (left, right) => right.count - left.count || comparePairs(left.pair, right.pair),
  )[0] ?? null;
}

/**
 * Learn up to `mergeLimit` BPE rules from a weighted word dictionary.
 *
 * Trace entry zero is the character-plus-boundary state. Each later entry is
 * the state after applying its recorded pair. `tokenCount` is N_t;
 * `vocabularySize` is |V_t|; and `bitBudget` uses the fixed-width code
 * N_t ceil(log2 |V_t|).
 */
export function learnBpe(
  dictionary = CLASSIC_BPE_DICTIONARY,
  mergeLimit = 8,
  { endOfWord = END_OF_WORD } = {},
) {
  if (!Number.isSafeInteger(mergeLimit) || mergeLimit < 0) {
    throw new RangeError('mergeLimit must be a non-negative integer');
  }
  validateEndOfWord(endOfWord);

  let vocabulary = normalizeDictionary(dictionary, endOfWord);
  const symbolInventory = new Set(vocabulary.flatMap((entry) => entry.tokens));
  let vocabularySize = symbolInventory.size;
  const merges = [];
  const trace = [{
    step: 0,
    pair: null,
    count: null,
    appliedCount: 0,
    vocabulary: copyVocabulary(vocabulary),
    ...accounting(vocabulary, vocabularySize),
  }];

  for (let step = 1; step <= mergeLimit; step += 1) {
    const selected = bestPair(pairCounts(vocabulary));
    if (!selected) break;

    const nextVocabulary = vocabulary.map((entry) => ({
      word: entry.word,
      count: entry.count,
      tokens: mergePair(entry.tokens, selected.pair),
    }));
    const appliedCount = vocabulary.reduce(
      (total, entry, index) => (
        total + entry.count * (entry.tokens.length - nextVocabulary[index].tokens.length)
      ),
      0,
    );
    const pair = [...selected.pair];
    const mergedSymbol = pair.join('');
    if (symbolInventory.has(mergedSymbol)) {
      throw new Error(
        'merge surface ' + JSON.stringify(mergedSymbol) + ' is not a fresh symbol',
      );
    }
    merges.push(pair);
    symbolInventory.add(mergedSymbol);
    vocabularySize = symbolInventory.size;
    vocabulary = nextVocabulary;

    trace.push({
      step,
      pair,
      count: selected.count,
      appliedCount,
      vocabulary: copyVocabulary(vocabulary),
      ...accounting(vocabulary, vocabularySize),
    });
  }

  return {
    endOfWord,
    merges: merges.map((pair) => [...pair]),
    vocabulary: copyVocabulary(vocabulary),
    trace,
  };
}

/**
 * Apply learned rules in their supplied order to a word or token array.
 *
 * String input is split into Unicode code points and receives the end marker;
 * token-array input is used as supplied. No rule is re-ranked at inference.
 */
export function applyMerges(
  wordOrTokens,
  merges,
  { endOfWord = END_OF_WORD } = {},
) {
  if (!Array.isArray(merges)) {
    throw new TypeError('merges must be an array');
  }
  validateEndOfWord(endOfWord);

  let tokens;
  if (typeof wordOrTokens === 'string') {
    if (wordOrTokens.includes(endOfWord)) {
      throw new RangeError(
        'input word ' + JSON.stringify(wordOrTokens) + ' contains the reserved end-of-word marker',
      );
    }
    tokens = [...wordOrTokens, endOfWord];
  } else if (Array.isArray(wordOrTokens)) {
    tokens = wordOrTokens.map(String);
  } else {
    throw new TypeError('wordOrTokens must be a string or token array');
  }

  for (const pair of merges) {
    tokens = mergePair(tokens, pair);
  }
  return tokens;
}
