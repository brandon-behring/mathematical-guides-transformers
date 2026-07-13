import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import test from 'node:test';

import {
  CLASSIC_BPE_DICTIONARY,
  END_OF_WORD,
  applyMerges,
  learnBpe,
  mergePair,
  pairCounts,
} from '../src/lib/bpe.mjs';

function reconstruct(tokens) {
  const surface = tokens.join('');
  assert.ok(surface.endsWith(END_OF_WORD), 'encoded word retains its end marker');
  return surface.slice(0, -END_OF_WORD.length);
}

test('learns the deterministic classic weighted-dictionary trace', () => {
  const learned = learnBpe(CLASSIC_BPE_DICTIONARY, 8);

  assert.deepEqual(learned.merges, [
    ['e', 's'],
    ['es', 't'],
    ['est', END_OF_WORD],
    ['l', 'o'],
    ['lo', 'w'],
    ['e', 'w'],
    ['ew', `est${END_OF_WORD}`],
    ['n', `ewest${END_OF_WORD}`],
  ]);
  assert.deepEqual(
    learned.trace.map(({ tokenCount, vocabularySize, bitsPerToken, bitBudget }) => ({
      tokenCount,
      vocabularySize,
      bitsPerToken,
      bitBudget,
    })),
    [
      { tokenCount: 95, vocabularySize: 11, bitsPerToken: 4, bitBudget: 380 },
      { tokenCount: 86, vocabularySize: 12, bitsPerToken: 4, bitBudget: 344 },
      { tokenCount: 77, vocabularySize: 13, bitsPerToken: 4, bitBudget: 308 },
      { tokenCount: 68, vocabularySize: 14, bitsPerToken: 4, bitBudget: 272 },
      { tokenCount: 61, vocabularySize: 15, bitsPerToken: 4, bitBudget: 244 },
      { tokenCount: 54, vocabularySize: 16, bitsPerToken: 4, bitBudget: 216 },
      { tokenCount: 48, vocabularySize: 17, bitsPerToken: 5, bitBudget: 240 },
      { tokenCount: 42, vocabularySize: 18, bitsPerToken: 5, bitBudget: 210 },
      { tokenCount: 36, vocabularySize: 19, bitsPerToken: 5, bitBudget: 180 },
    ],
  );

  const initialCounts = pairCounts(learned.trace[0].vocabulary);
  assert.equal(initialCounts.find(({ pair }) => pair[0] === 'e' && pair[1] === 's').count, 9);
  assert.equal(initialCounts.find(({ pair }) => pair[0] === 's' && pair[1] === 't').count, 9);
  assert.equal(initialCounts.find(({ pair }) => pair[0] === 't' && pair[1] === END_OF_WORD).count, 9);
});

test('breaks equal-frequency pair ties lexicographically', () => {
  const learned = learnBpe([
    { word: 'ac', count: 1 },
    { word: 'ab', count: 1 },
  ], 1);

  assert.deepEqual(learned.trace[1].pair, ['a', 'b']);
  assert.equal(learned.trace[1].count, 1);
});

test('applies inference merges in the supplied order', () => {
  assert.deepEqual(
    applyMerges('abc', [['a', 'b'], ['b', 'c']]),
    ['ab', 'c', END_OF_WORD],
  );
  assert.deepEqual(
    applyMerges('abc', [['b', 'c'], ['a', 'bc']]),
    ['abc', END_OF_WORD],
  );
});

test('learned segmentations reconstruct every source word', () => {
  const { merges } = learnBpe(CLASSIC_BPE_DICTIONARY, 8);

  for (const { word } of CLASSIC_BPE_DICTIONARY) {
    assert.equal(reconstruct(applyMerges(word, merges)), word);
  }
});

test('counts overlapping pairs but merges them non-overlappingly left to right', () => {
  const original = ['a', 'a', 'a', 'a'];
  assert.deepEqual(mergePair(original, ['a', 'a']), ['aa', 'aa']);
  assert.deepEqual(original, ['a', 'a', 'a', 'a'], 'mergePair is pure');
  assert.deepEqual(mergePair(['a', 'a', 'a'], ['a', 'a']), ['aa', 'a']);

  const counts = pairCounts([{ word: 'aaaa', count: 2, tokens: original }]);
  assert.deepEqual(counts, [{ pair: ['a', 'a'], count: 6 }]);

  const learned = learnBpe([{ word: 'aaaa', count: 1 }], 1);
  assert.equal(learned.trace[1].count, 3, 'selection counts adjacent occurrences');
  assert.equal(learned.trace[1].appliedCount, 2, 'replacement uses non-overlapping occurrences');
  assert.deepEqual(learned.vocabulary[0].tokens, ['aa', 'aa', END_OF_WORD]);
});

test('keeps the reserved boundary marker disjoint and validates it consistently', () => {
  assert.throws(
    () => learnBpe([
      { word: '</x', count: 100 },
      { word: '</w>', count: 10 },
    ], 10),
    /contains the reserved end-of-word marker/,
  );
  assert.throws(
    () => applyMerges('abc', [], { endOfWord: '' }),
    /endOfWord must be a non-empty string/,
  );
  assert.throws(
    () => applyMerges('abc', [], { endOfWord: null }),
    /endOfWord must be a non-empty string/,
  );
  assert.throws(
    () => applyMerges('</w>', [['<', '/'], ['</', 'w'], ['</w', '>']]),
    /contains the reserved end-of-word marker/,
  );
});

test('explorer is static-first, print-complete, live, and free of hard-coded IDs', async () => {
  const source = await readFile(
    new URL('../src/components/BpeMergeExplorer.astro', import.meta.url),
    'utf8',
  );

  assert.match(source, /steps\.map\(\(step\) =>/);
  assert.match(source, /<button type="button" data-bpe-previous>/);
  assert.match(source, /<button type="button" data-bpe-next>/);
  assert.match(source, /aria-live="polite"/);
  assert.match(source, /data-bpe-controls hidden/);
  assert.match(source, /\.bpe-explorer__controls\[hidden\]\s*{\s*display: none;/);
  assert.match(source, /@media print/);
  assert.match(source, /display: list-item !important/);
  assert.doesNotMatch(source, /\bid\s*=/);
});
