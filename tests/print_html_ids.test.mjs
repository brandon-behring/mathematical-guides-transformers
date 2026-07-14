import assert from 'node:assert/strict';
import test from 'node:test';

import {
  groupPrintExerciseSolutions,
  namespacePrintHeadingIds,
} from '../src/lib/print-html.mjs';

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

test('groups a multi-node exercise prompt with its matching solution', () => {
  const raw = `
    <p><strong>Exercise 1.1 (Compute).</strong> Evaluate</p>
    <span class="katex-display">x + y</span>
    <p>and justify the result.</p>
    <aside class="callout callout-worked solution-box"><details><summary>Solution</summary><div>Work</div></details></aside>
    <p>Interlude.</p>
    <div class="exercise-solution-pair">
    <p><strong>Exercise 1.2 (Prove).</strong> Show the claim.</p>
    <aside class="callout solution-box"><details><summary>Solution</summary><div><aside>Nested note</aside></div></details></aside>
    </div>
  `;

  const got = groupPrintExerciseSolutions(raw);
  assert.equal((got.match(/class="exercise-solution-pair"/g) ?? []).length, 2);
  assert.match(
    got,
    /<div class="exercise-solution-pair"><p><strong>Exercise 1\.1[\s\S]*?<\/aside><\/div>\s*<p>Interlude\.<\/p>/,
  );
  assert.match(
    got,
    /<div class="exercise-solution-pair">\s*<p><strong>Exercise 1\.2[\s\S]*?<aside>Nested note<\/aside>[\s\S]*?<\/aside>\s*<\/div>/,
  );
  assert.equal(groupPrintExerciseSolutions(got), got);
});
