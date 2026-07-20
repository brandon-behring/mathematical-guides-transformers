import assert from 'node:assert/strict';
import { access, readdir, readFile } from 'node:fs/promises';
import test from 'node:test';
import { PDFDict, PDFDocument, PDFHexString, PDFName } from 'pdf-lib';
import { assertPrintRoute } from '../src/lib/print-route-preflight.mjs';
import { finalizeTaggedPdf } from '../src/lib/tagged-pdf.mjs';

const chapterDir = new URL('../src/content/transformers/', import.meta.url);
const glossaryDir = new URL('../src/content/glossary/', import.meta.url);
const allowedMarginVariants = new Set([
  'note',
  'warning',
  'tip',
  'formula',
  'pattern',
  'cross-ref',
  'analogy-limit',
  'computational-note',
]);
const marginWordLimits = {
  note: 30,
  warning: 30,
  tip: 32,
  formula: 40,
  pattern: 35,
  'cross-ref': 30,
  'analogy-limit': 30,
  'computational-note': 40,
};

async function chapters() {
  const names = (await readdir(chapterDir)).filter((name) => name.endsWith('.mdx')).sort();
  return Promise.all(names.map(async (name) => ({
    name,
    source: await readFile(new URL(name, chapterDir), 'utf8'),
  })));
}

async function editorialSources() {
  const entries = await chapters();
  const staticUrls = [
    new URL('../src/components/NotationIndex.mdx', import.meta.url),
    new URL('../src/components/QuickReference.mdx', import.meta.url),
    new URL('../src/content/frontmatter/authors.mdx', import.meta.url),
    new URL('../README.md', import.meta.url),
  ];
  for (const url of staticUrls) {
    entries.push({ name: url.pathname.split('/').at(-1), source: await readFile(url, 'utf8') });
  }
  for (const name of (await readdir(glossaryDir)).filter((value) => value.endsWith('.mdx')).sort()) {
    entries.push({ name: `glossary/${name}`, source: await readFile(new URL(name, glossaryDir), 'utf8') });
  }
  return entries;
}

function words(value) {
  return value.match(/\b[\p{L}\p{N}][\p{L}\p{N}'’.-]*\b/gu)?.length ?? 0;
}

function readerFacingSource(source) {
  const frontmatter = source.match(/^---\n([\s\S]*?)\n---\n/)?.[1] ?? '';
  const frontmatterText = [...frontmatter.matchAll(/^\s*(?:title|description|statement|term|aliases):\s*(.+?)\s*$/gm)]
    .map((match) => match[1].replace(/^(["'])(.*)\1$/, '$2'))
    .join('\n');
  const body = source
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/<NotationOverride\b[^>]*>[\s\S]*?<\/NotationOverride>/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`\n]+`/g, '')
    .replace(/^import .*;$/gm, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\b(?:id|src|key|href)="[^"]*"/g, '');
  return `${frontmatterText}\n${body}`;
}

function substantiveBody(source) {
  return source
    .replace(/^---\n[\s\S]*?\n---\n/, '')
    .replace(/<NotationOverride\b[^>]*>[\s\S]*?<\/NotationOverride>/g, '')
    .replace(/```[\s\S]*?```/g, '')
    .replace(/`[^`\n]+`/g, '')
    .replace(/^import .*;$/gm, '')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/\b(?:id|src|key|href)="[^"]*"/g, '');
}

function readerFacingProse(source) {
  return readerFacingSource(source)
    .replace(/\$\$[\s\S]*?\$\$/g, ' ')
    .replace(/\$[^$\n]*\$/g, ' ')
    .replace(/<[^>]+>/g, ' ');
}

test('chapter sources defer their sole H1 to ChapterHeader and keep TOC headings plain', async () => {
  const entries = await chapters();
  assert.equal(entries.length, 24);

  for (const { name, source } of entries) {
    assert.doesNotMatch(source, /^# /m, `${name} duplicates the frontmatter-backed chapter H1`);
    assert.doesNotMatch(
      source,
      /^#{2,3} .*\$.*$/m,
      `${name} puts TeX in a heading, which duplicates KaTeX accessibility text in navigation`,
    );

    const description = source.match(/^description:\s*"([^"]+)"$/m)?.[1] ?? '';
    assert.ok(description, `${name} has no description`);
    assert.ok(words(description) <= 40, `${name} description is ${words(description)} words`);
    assert.match(description, /\.$/, `${name} description is not a complete sentence`);
    assert.match(description, /^[A-Z][A-Za-z-]*s\b/, `${name} description does not begin with a third-person present-tense verb`);

    const opener = source.match(/\*\*Where we are\.\*\*([\s\S]*?)(?=\n\s*\n)/)?.[1] ?? '';
    assert.ok(opener, `${name} has no Where we are opener`);
    const openerWords = words(opener.replace(/<[^>]+>/g, ' ').replace(/\$[^$]*\$/g, ' math '));
    assert.ok(openerWords >= 80 && openerWords <= 120, `${name} opener is ${openerWords} words`);
  }
});

test('figures have authored accessibility text and reader-facing captions', async () => {
  let count = 0;
  for (const { name, source } of await chapters()) {
    for (const match of source.matchAll(/<Figure\b([\s\S]*?)\/>/g)) {
      count += 1;
      const props = match[1];
      assert.match(props, /\balt="[^"]+"/, `${name} Figure lacks alt`);
      assert.match(props, /\bdesc="[^"]+"/, `${name} Figure lacks desc`);
      const caption = props.match(/\bcaption="([^"]+)"/)?.[1] ?? '';
      assert.ok(caption, `${name} Figure lacks caption`);
      assert.ok(words(caption) <= 45, `${name} Figure caption is ${words(caption)} words`);
      assert.doesNotMatch(caption, /\b(?:def|thm|prop|lem|cor|rem|ex)-[a-z0-9-]+\b/i, `${name} caption exposes an internal ID`);
      assert.doesNotMatch(caption, /Rendered from TikZ|\$[^$]+\$/, `${name} caption exposes source or pipeline syntax`);
    }
  }
  assert.equal(count, 31);
});

test('margin-note variants are supported by the guide-local component', async () => {
  for (const { name, source } of await chapters()) {
    for (const match of source.matchAll(/<MarginNote\b[^>]*\bvariant="([^"]+)"/g)) {
      assert.ok(allowedMarginVariants.has(match[1]), `${name} uses unsupported MarginNote variant ${match[1]}`);
    }
    assert.equal(
      /book-scaffold-astro\/components\/MarginNote\.astro/.test(source),
      false,
      `${name} bypasses the guide-local semantic MarginNote component`,
    );
    assert.equal(
      /book-scaffold-astro\/components\/Sidenote\.astro/.test(source),
      false,
      `${name} bypasses the guide-local named Sidenote component`,
    );
    for (const match of source.matchAll(/<MarginNote\b([^>]*)>([\s\S]*?)<\/MarginNote>/g)) {
      const variant = match[1].match(/\bvariant="([^"]+)"/)?.[1] ?? 'note';
      const label = match[1].match(/\blabel="([^"]+)"/)?.[1] ?? variant;
      const prose = match[2].replace(/<[^>]+>/g, ' ').replace(/\$[^$]*\$/g, ' math ');
      const count = words(prose);
      assert.ok(
        count <= marginWordLimits[variant],
        `${name} MarginNote “${label}” is ${count} words; ${variant} limit is ${marginWordLimits[variant]}`,
      );
    }
  }
});

test('column-vector index labels mirror their notation-override scopes', async () => {
  const index = await readFile(new URL('../src/components/NotationIndex.mdx', import.meta.url), 'utf8');
  const columnScopes = [];

  for (const { source } of await chapters()) {
    for (const match of source.matchAll(/<NotationOverride\s+scope="([^"]+)">([\s\S]*?)<\/NotationOverride>/g)) {
      if (/\bcolumns?\b/i.test(match[2])) columnScopes.push(match[1]);
    }
  }

  const columnSection = index.match(/### Column-vector switches[\s\S]*?(?=<div className="notation-print-break")/)?.[0] ?? '';
  const indexScopes = [...columnSection.matchAll(/^\| ([^|]+?) \|/gm)]
    .map((match) => match[1].trim())
    .filter((scope) => scope !== 'Scope' && !/^-+$/.test(scope));
  assert.deepEqual(
    [...new Set(indexScopes)].sort(),
    [...new Set(columnScopes)].sort(),
    'NotationIndex column-vector rows and NotationOverride scopes diverge',
  );
  assert.match(
    index,
    /\| \$\\boldsymbol\\beta\$ \| learned featurewise normalization shift \| LayerNorm \(<XRef id="def-ln" \/>\) \|/,
    'NotationIndex must not assign LayerNorm\'s learned shift to RMSNorm',
  );
});

test('every solution disclosure identifies its exercise', async () => {
  let count = 0;
  for (const { name, source } of await chapters()) {
    const exerciseNumbers = [...source.matchAll(/\*\*Exercise\s+(\d+\.\d+)/g)].map((match) => match[1]);
    const solutionNumbers = [...source.matchAll(/<SolutionBox\s+exercise="(\d+\.\d+)"\s*>/g)].map((match) => match[1]);
    count += solutionNumbers.length;
    assert.deepEqual(solutionNumbers, exerciseNumbers, `${name} solution labels do not match exercise order`);
  }
  assert.equal(count, 133);
});

test('glossary accounting retains execution and capacity qualifiers', async () => {
  const activated = await readFile(new URL('../src/content/glossary/activated-arithmetic.mdx', import.meta.url), 'utf8');
  const traffic = await readFile(new URL('../src/content/glossary/active-expert-traffic.mdx', import.meta.url), 'utf8');
  assert.match(activated, /no dropped assignments/);
  assert.match(activated, /\(Tk-D\)\\Phi_\{\\mathrm\{FFN\}\}/);
  assert.match(traffic, /union of executed experts/);
});

test('book branding provides a subtitle and favicon', async () => {
  const config = await readFile(new URL('../astro.config.mjs', import.meta.url), 'utf8');
  const packageMetadata = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'));
  assert.match(config, /\btitle:\s*'Transformer Mathematics'/);
  assert.match(config, /\bsubtitle:\s*'[^']+'/);
  assert.doesNotMatch(config, /subtitle:\s*'A scaffold-astro book'/);
  const configDescription = config.match(/\bdescription:\s*'([^']+)'/s)?.[1] ?? '';
  assert.ok(configDescription, 'astro.config.mjs has no book description');
  assert.doesNotMatch(configDescription, /state space models|vision-language/i);
  assert.match(packageMetadata.description, /^Transformer Mathematics:/);
  assert.doesNotMatch(packageMetadata.description, /state space models|vision-language/i);
  await access(new URL('../public/favicon.svg', import.meta.url));
});

test('accessible names, deep links, and print containment stay wired', async () => {
  const [config, tablePlugin, figure, marginNote, sidenote, styles, printPage, renderer] = await Promise.all([
    readFile(new URL('../astro.config.mjs', import.meta.url), 'utf8'),
    readFile(new URL('../src/lib/rehype-table-captions.mjs', import.meta.url), 'utf8'),
    readFile(new URL('../src/components/Figure.astro', import.meta.url), 'utf8'),
    readFile(new URL('../src/components/MarginNote.astro', import.meta.url), 'utf8'),
    readFile(new URL('../src/components/Sidenote.astro', import.meta.url), 'utf8'),
    readFile(new URL('../src/styles/apparatus.css', import.meta.url), 'utf8'),
    readFile(new URL('../src/pages/print.astro', import.meta.url), 'utf8'),
    readFile(new URL('../scripts/render-pdf.mjs', import.meta.url), 'utf8'),
  ]);
  assert.match(config, /rehypePlugins:\s*\[rehypeTableCaptions\]/);
  assert.match(tablePlugin, /tagName:\s*'caption'/);
  assert.match(tablePlugin, /properties\.ariaLabel/);
  assert.match(figure, /aria-labelledby=\{captionId\}/);
  assert.match(marginNote, /aria-label=/);
  assert.match(sidenote, /role="note"\s+aria-label=/);
  assert.match(styles, /main \[id\][\s\S]*?scroll-margin-top:\s*5rem/);
  assert.match(styles, /\.print-edition \.sidenote[\s\S]*?float:\s*none/);
  assert.match(styles, /\.print-edition \.katex-display[\s\S]*?background-image:\s*none/);
  assert.match(printPage, /title="Transformer Mathematics — Print Edition"/);
  assert.match(printPage, /data-print-chapter-count=/);
  assert.match(renderer, /await assertPrintRoute\(input\)/);
  assert.match(renderer, /finalizeTaggedPdf\(chromePdf, headings\)/);
  assert.match(renderer, /generateTaggedPDF:\s*true/);
  assert.match(renderer, /generateDocumentOutline:\s*true/);
  assert.match(renderer, /PDF_CHROME_PATH/);
  assert.match(renderer, /StructTreeRoot/);
});

test('PDF preflight rejects HTTP errors and incomplete print routes', async () => {
  const htmlResponse = (body, status = 200) => new Response(body, {
    status,
    headers: { 'content-type': 'text/html; charset=utf-8' },
  });
  await assert.rejects(
    assertPrintRoute('http://example.test/404', async () => htmlResponse('Not Found', 404)),
    /HTTP 404/,
  );
  await assert.rejects(
    assertPrintRoute(
      'http://example.test/wrong',
      async () => htmlResponse('<title>Different route</title>'),
    ),
    /not the complete Transformer Mathematics print route/,
  );
  await assert.rejects(
    assertPrintRoute(
      'http://example.test/partial',
      async () => htmlResponse(
        '<title>Transformer Mathematics — Print Edition</title>'
        + '<div class="print-edition" data-print-chapter-count="2">'
        + '<header class="chapter-header"></header></div>',
      ),
    ),
    /declared chapters: 2; rendered chapter headers: 1/,
  );

  const result = await assertPrintRoute(
    'http://example.test/print',
    async () => htmlResponse(
      '<title>Transformer Mathematics — Print Edition</title>'
      + '<div class="prose print-edition" data-print-chapter-count="2">'
      + '<header class="chapter-header"><h1>First &amp; complete</h1></header>'
      + '<header class="chapter-header"><h1>Second chapter</h1></header></div>',
    ),
  );
  assert.deepEqual(result, {
    chapterCount: 2,
    headings: ['First & complete', 'Second chapter'],
  });
});

test('PDF finalization maps PDF 2.0 emphasis roles and repairs outline text', async () => {
  const source = await PDFDocument.create();
  source.addPage();
  const structureRoot = source.context.obj({ Type: PDFName.of('StructTreeRoot') });
  source.catalog.set(
    PDFName.of('StructTreeRoot'),
    source.context.register(structureRoot),
  );

  const outlineRoot = source.context.obj({ Type: PDFName.of('Outlines'), Count: 1 });
  const outlineRootRef = source.context.register(outlineRoot);
  const outlineItem = source.context.obj({
    Title: PDFHexString.fromText('Brokenheading'),
    Parent: outlineRootRef,
  });
  const outlineItemRef = source.context.register(outlineItem);
  outlineRoot.set(PDFName.of('First'), outlineItemRef);
  outlineRoot.set(PDFName.of('Last'), outlineItemRef);
  source.catalog.set(PDFName.of('Outlines'), outlineRootRef);

  const finalized = await finalizeTaggedPdf(
    await source.save({ useObjectStreams: false }),
    ['Repaired heading'],
  );
  assert.match(Buffer.from(finalized).subarray(0, 16).toString('latin1'), /^%PDF-1\.7/);

  const loaded = await PDFDocument.load(finalized, { updateMetadata: false });
  const loadedStructure = loaded.context.lookup(
    loaded.catalog.get(PDFName.of('StructTreeRoot')),
    PDFDict,
  );
  const roleMap = loaded.context.lookup(
    loadedStructure.get(PDFName.of('RoleMap')),
    PDFDict,
  );
  assert.equal(roleMap.get(PDFName.of('Strong')).toString(), '/Span');
  assert.equal(roleMap.get(PDFName.of('Em')).toString(), '/Span');

  const loadedOutline = loaded.context.lookup(
    loaded.catalog.get(PDFName.of('Outlines')),
    PDFDict,
  );
  const loadedItem = loaded.context.lookup(
    loadedOutline.get(PDFName.of('First')),
    PDFDict,
  );
  assert.equal(loadedItem.lookup(PDFName.of('Title')).decodeText(), 'Repaired heading');
});

test('reader-facing terminology follows the book-wide editorial ledger', async () => {
  const disallowed = [
    [/\bKV-cache\b/i, 'KV-cache → KV cache'],
    [/\b(?:key|keys|K)\/(?:value|values|V)\b/i, 'slash shorthand → key and value'],
    [/\b(?:query|queries)\/(?:key|keys)\b/i, 'slash shorthand → query and key'],
    [/\b(?:key|keys)\/(?:query|queries)\b/i, 'slash shorthand → query and key'],
    [/\bscore\/value\b/i, 'slash shorthand → score and value'],
    [/\bstate\/write\/read\b/i, 'slash shorthand → state, write, and read'],
    [/\bfeature\/value\b/i, 'slash shorthand → feature and value'],
    [/\binput\/output\b/i, 'slash shorthand → input and output'],
    [/\bLayerNorm\/RMSNorm\b/i, 'slash shorthand → LayerNorm and RMSNorm'],
    [/\bencoder-decoder\b/i, 'encoder-decoder → encoder–decoder'],
    [/\bimage-text\b/i, 'image-text → image–text'],
    [/\bvision-language\b/i, 'vision-language → vision–language'],
    [/\bquery-key\b/i, 'query-key → query–key'],
    [/\bkey-value\b/i, 'key-value → key–value'],
    [/\bwinner-loser\b/i, 'winner-loser → winner–loser'],
    [/\bpolicy-reference\b/i, 'policy-reference → policy–reference'],
    [/\browwise\b/i, 'rowwise → row-wise'],
    [/\btokenwise\b/i, 'tokenwise → token-wise'],
    [/\bnon-negative\b/i, 'non-negative → nonnegative'],
    [/\bnon-differentiable\b/i, 'non-differentiable → nondifferentiable'],
    [/\bcross attention\b/i, 'cross attention → cross-attention'],
    [/\bself attention\b/i, 'self attention → self-attention'],
    [/\bmulti head\b/i, 'multi head → multi-head'],
    [/\bfeed forward\b/i, 'feed forward → feed-forward'],
    [/\bzero shot\b/i, 'zero shot → zero-shot'],
    [/\bstate space (?:model|models|update|updates|formulation)\b/i, 'state-space compound needs a hyphen'],
    [/\b(?:colour|behaviour|modelling)\b/i, 'use American English spelling'],
    [/\bnotation chapter\b/, 'explicit chapter names use title case'],
    [/\btraining chapter\b/, 'explicit chapter names use title case'],
    [/\bdetection chapter\b/, 'explicit chapter names use title case'],
    [/\binference chapter\b/, 'explicit chapter names use title case'],
  ];

  for (const { name, source } of await editorialSources()) {
    const prose = readerFacingSource(source);
    for (const [pattern, message] of disallowed) {
      assert.equal(pattern.test(prose), false, `${name}: ${message}`);
    }
    assert.doesNotMatch(prose, /\S—|—\S/, `${name}: spaces must surround prose em dashes`);
    const proseWithoutAcronym = readerFacingProse(source).replace(/\bI\/O\b/g, '');
    const slashShorthand = proseWithoutAcronym.match(/\b[A-Za-z][A-Za-z-]*(?:\/[A-Za-z][A-Za-z-]*)+\b/);
    assert.equal(
      slashShorthand,
      null,
      `${name}: replace prose slash shorthand “${slashShorthand?.[0]}” with words or an en dash`,
    );
  }
});

test('abbreviations are expanded at their first substantive editorial use', async () => {
  const entries = new Map((await editorialSources()).map(({ name, source }) => [name, source]));
  const requiredExpansions = [
    ['05-multi-head-attention.mdx', 'MHA', /multi-head attention \(MHA\)/i],
    ['05-multi-head-attention.mdx', 'MQA', /Multi-Query Attention \(MQA\)/],
    ['05-multi-head-attention.mdx', 'GQA', /Grouped-Query Attention \(GQA\)/],
    ['05-multi-head-attention.mdx', 'MLA', /multi-head latent attention \(MLA\)/i],
    ['11-preference-optimization.mdx', 'DPO', /Direct Preference Optimization \(DPO\)/],
    ['11-preference-optimization.mdx', 'RLHF', /reinforcement learning from human feedback \(RLHF\)/i],
    ['11-preference-optimization.mdx', 'PPO', /Proximal Policy Optimization \(PPO\)/],
    ['12-detection-encoders.mdx', 'OOD', /out-of-distribution \(OOD\)/i],
    ['14-training-optimizations.mdx', 'LoRA', /low-rank adaptation \(LoRA\)/i],
    ['14-training-optimizations.mdx', 'FSDP', /Fully Sharded Data Parallel \(FSDP\)/],
    ['14-training-optimizations.mdx', 'DDP', /Distributed Data Parallel \(DDP\)/],
    ['15-inference-optimizations.mdx', 'KV', /key–value \(KV\) cache/i],
    ['16-mixture-of-experts.mdx', 'MoE', /mixture-of-experts \(MoE\)/i],
    ['17-sparse-attention.mdx', 'I/O', /input–output \(I\/O\)/i],
    ['17-sparse-attention.mdx', 'KKT', /Karush–Kuhn–Tucker \(KKT\)/],
    ['21-discrete-visual-tokenization.mdx', 'VQ-VAE', /vector-quantized variational autoencoder \(VQ-VAE\)/i],
    ['23-multimodal-evaluation.mdx', 'MRR', /mean reciprocal rank \(MRR\)/i],
    ['QuickReference.mdx', 'BPE', /byte-pair encoding \(BPE\)/i],
    ['QuickReference.mdx', 'KL', /Kullback–Leibler \(KL\)/],
    ['QuickReference.mdx', 'DPO', /Direct Preference Optimization \(DPO\)/],
    ['QuickReference.mdx', 'KV', /key–value \(KV\)/i],
    ['QuickReference.mdx', 'MoE', /mixture-of-experts \(MoE\)/i],
    ['NotationIndex.mdx', 'RNN', /recurrent neural network \(RNN\)/i],
    ['NotationIndex.mdx', 'WKV', /weighted key–value \(WKV\)/i],
    ['NotationIndex.mdx', 'LoRA', /low-rank adaptation \(LoRA\)/i],
    ['NotationIndex.mdx', 'MoE', /mixture-of-experts \(MoE\)/i],
    ['NotationIndex.mdx', 'KL', /Kullback–Leibler \(KL\)/],
    ['NotationIndex.mdx', 'RLHF', /reinforcement learning from human feedback \(RLHF\)/i],
    ['NotationIndex.mdx', 'DPO', /Direct Preference Optimization \(DPO\)/],
    ['NotationIndex.mdx', 'RoPE', /Rotary position embedding \(RoPE\)/i],
    ['glossary/activated-arithmetic.mdx', 'FLOPs', /floating-point operations \(FLOPs\)/i],
    ['glossary/resident-parameters.mdx', 'FLOPs', /floating-point operations \(FLOPs\)/i],
    ['glossary/lossless-prefix-memory.mdx', 'KV', /key–value \(KV\)/i],
    ['glossary/state.mdx', 'RNN', /recurrent neural network \(RNN\)/i],
    ['glossary/state.mdx', 'SSM', /state-space model \(SSM\)/i],
    ['glossary/state.mdx', 'KV', /key–value \(KV\)/i],
    ['glossary/subword.mdx', 'BPE', /byte-pair encoding \(BPE\)/i],
    ['glossary/direct-preference-optimization.mdx', 'KL', /Kullback–Leibler \(KL\)/],
    ['glossary/reference-policy.mdx', 'KL', /Kullback–Leibler \(KL\)/],
    ['glossary/reference-policy.mdx', 'DPO', /Direct Preference Optimization \(DPO\)/],
    ['glossary/reinforcement-learning-from-human-feedback.mdx', 'RLHF', /reinforcement learning from human feedback \(RLHF\)/i],
    ['glossary/reinforcement-learning-from-human-feedback.mdx', 'PPO', /Proximal Policy Optimization \(PPO\)/],
    ['README.md', 'BPE', /byte-pair encoding \(BPE\)/i],
    ['README.md', 'RoPE', /rotary position embedding \(RoPE\)/i],
    ['README.md', 'BPTT', /backpropagation through time \(BPTT\)/i],
    ['README.md', 'LSTM', /long short-term memory \(LSTM\)/i],
    ['README.md', 'GRU', /gated recurrent unit \(GRU\)/i],
    ['README.md', 'ZOH', /zero-order-hold \(ZOH\)/i],
    ['README.md', 'HiPPO', /high-order polynomial projection operators \(HiPPO\)/i],
    ['README.md', 'LTI', /linear\s+time-invariant \(LTI\)/i],
    ['README.md', 'RLHF', /reinforcement learning from human feedback \(RLHF\)/i],
    ['README.md', 'DPO', /Direct Preference\s+Optimization \(DPO\)/],
    ['README.md', 'KV', /key–value \(KV\)/i],
    ['README.md', 'NSA', /Native Sparse Attention \(NSA\)/],
    ['README.md', 'RWKV', /receptance-weighted key–value \(RWKV\)/i],
    ['README.md', 'xLSTM', /extended long short-term memory \(xLSTM\)/i],
  ];
  for (const [name, abbreviation, pattern] of requiredExpansions) {
    const source = entries.get(name);
    assert.ok(source, `${name} is missing from the editorial source set`);
    const body = substantiveBody(source);
    const expansion = body.match(pattern);
    assert.ok(expansion, `${name} does not expand ${pattern.source}`);
    const firstUse = body.search(new RegExp(`\\b${abbreviation}\\b`));
    assert.ok(
      firstUse >= expansion.index && firstUse < expansion.index + expansion[0].length,
      `${name} uses ${abbreviation} before expanding it`,
    );
  }
});

test('mathematics uses the shared macros for unambiguous standing notation', async () => {
  for (const { name, source } of await editorialSources()) {
    const body = readerFacingSource(source).replace(/\\langle\$[^$]+\$\\rangle/g, '');
    assert.equal(/\\mathbb\s*(?:\{\s*)?(?:R|Z|N|E)(?:\s*\})?/.test(body), false, `${name} bypasses a domain or expectation macro`);
    assert.equal(/\\operatorname\{Var\}/.test(body), false, `${name} bypasses \\Var`);
    assert.equal(/\\operatorname\{softmax\}/.test(body), false, `${name} bypasses \\softmax`);
    assert.equal(/\\operatorname\{Emb\}/.test(body), false, `${name} bypasses \\Emb`);
    assert.equal(/\\operatorname\{sg\}/.test(body), false, `${name} bypasses \\sg`);
    assert.equal(/\\lVert/.test(body), false, `${name} bypasses \\norm`);
    assert.equal(/\\langle/.test(body), false, `${name} bypasses \\inner`);
    assert.equal(/:=/.test(body), false, `${name} bypasses \\defeq`);
  }
});
