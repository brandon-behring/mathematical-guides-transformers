import assert from 'node:assert/strict';
import { readdir, readFile } from 'node:fs/promises';
import test from 'node:test';

import { assembleSvg, namespaceSvgIds } from '../src/lib/figure.mjs';

test('namespaces SVG IDs and every supported fragment-reference form', () => {
  const raw = `<svg data-id="semantic-owner" aria-labelledby="title glyph-0">
    <defs><path id="glyph-0"/><clipPath id='clip-1'/></defs>
    <use xlink:href="#glyph-0"/><use href='#glyph-0'/>
    <g clip-path="url(#clip-1)"/>
  </svg>`;

  const got = namespaceSvgIds(raw, 'fig-demo');
  assert.match(got, /id="fig-demo--glyph-0"/);
  assert.match(got, /id='fig-demo--clip-1'/);
  assert.match(got, /xlink:href="#fig-demo--glyph-0"/);
  assert.match(got, /href='#fig-demo--glyph-0'/);
  assert.match(got, /url\(#fig-demo--clip-1\)/);
  assert.match(got, /aria-labelledby="title fig-demo--glyph-0"/);
  assert.match(got, /data-id="semantic-owner"/);
});

test('two inline assets with converter-generic IDs remain independent', () => {
  const raw = '<svg><defs><path id="glyph-0-0"/></defs><use href="#glyph-0-0"/></svg>';
  const combined = [
    assembleSvg(raw, { idBase: 'fig-first', alt: 'First' }),
    assembleSvg(raw, { idBase: 'fig-second', alt: 'Second' }),
  ].join('');

  const ids = [...combined.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]);
  assert.equal(new Set(ids).size, ids.length);
  assert.match(combined, /href="#fig-first--glyph-0-0"/);
  assert.match(combined, /href="#fig-second--glyph-0-0"/);
});

test('uses alt as the accessible name and desc as its separate description', () => {
  const got = assembleSvg('<svg><title>Converter title</title></svg>', {
    idBase: 'fig-accessible',
    caption: 'Visible caption with a different job.',
    alt: 'Concise diagram name',
    desc: 'Longer structural explanation of the diagram.',
  });

  assert.match(got, /<title id="fig-accessible-title">Concise diagram name<\/title>/);
  assert.match(got, /<desc id="fig-accessible-desc">Longer structural explanation/);
  assert.match(got, /aria-labelledby="fig-accessible-title"/);
  assert.match(got, /aria-describedby="fig-accessible-desc"/);
  assert.doesNotMatch(got, /Visible caption with a different job/);
  assert.doesNotMatch(got, /Converter title/);
});

test('all chapter figures use the namespacing wrapper', async () => {
  const chapterDir = new URL('../src/content/transformers/', import.meta.url);
  const chapterFiles = (await readdir(chapterDir)).filter((name) => name.endsWith('.mdx'));

  for (const file of chapterFiles) {
    const source = await readFile(new URL(file, chapterDir), 'utf8');
    assert.doesNotMatch(
      source,
      /book-scaffold-astro\/components\/Figure\.astro/,
      `${file} bypasses the document-safe Figure wrapper`,
    );
  }
});

test('every chapter figure src resolves to a file in public/figures/', async () => {
  // Under the non-root base, figure srcs are base-aware JSX expressions
  // (`${import.meta.env.BASE_URL}figures/<name>.svg`). The scaffold's own figure-existence
  // check matches only quoted string literals (RE_FIGURE), so it silently skips expression
  // srcs — a typo'd name would pass `validate` + `build` and then 404 as an <img> at runtime
  // and in the PDF. This guard restores that coverage: every `figures/<name>.svg` referenced
  // in a chapter must exist on disk.
  const chapterDir = new URL('../src/content/transformers/', import.meta.url);
  const publicFigDir = new URL('../public/figures/', import.meta.url);
  const chapterFiles = (await readdir(chapterDir)).filter((name) => name.endsWith('.mdx'));
  const available = new Set(
    (await readdir(publicFigDir)).filter((name) => name.endsWith('.svg')),
  );

  for (const file of chapterFiles) {
    const source = await readFile(new URL(file, chapterDir), 'utf8');
    for (const m of source.matchAll(/figures\/([A-Za-z0-9._-]+\.svg)/g)) {
      assert.ok(
        available.has(m[1]),
        `${file}: <Figure> references figures/${m[1]} but public/figures/${m[1]} does not exist`,
      );
    }
  }
});
