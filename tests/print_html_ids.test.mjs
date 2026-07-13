import assert from 'node:assert/strict';
import test from 'node:test';

import { namespacePrintHeadingIds } from '../src/lib/print-html.mjs';

test('scopes generated headings and their local references only', () => {
  const raw = `
    <h2 id="notation">Notation</h2>
    <a href="#notation" aria-describedby="notation semantic-note">Return</a>
    <div id="def-softmax">Definition</div>
    <a href="#def-softmax">Definition link</a>
  `;

  const got = namespacePrintHeadingIds(raw, 'chapter-04');
  assert.match(got, /<h2 id="chapter-04--notation">/);
  assert.match(got, /href="#chapter-04--notation"/);
  assert.match(got, /aria-describedby="chapter-04--notation semantic-note"/);
  assert.match(got, /id="def-softmax"/);
  assert.match(got, /href="#def-softmax"/);
});

test('identical heading slugs become unique across print chapters', () => {
  const first = namespacePrintHeadingIds('<h2 id="exercises">Exercises</h2>', 'chapter-01');
  const second = namespacePrintHeadingIds('<h2 id="exercises">Exercises</h2>', 'chapter-02');
  const ids = [...`${first}${second}`.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);

  assert.deepEqual(ids, ['chapter-01--exercises', 'chapter-02--exercises']);
  assert.equal(new Set(ids).size, ids.length);
});
