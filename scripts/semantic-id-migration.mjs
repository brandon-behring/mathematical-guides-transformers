#!/usr/bin/env node

/**
 * Durable verifier for Track A3's one-time chapter-number and semantic-ID
 * migration. The tracked migration manifest is the historical ledger; this
 * script proves that the ledger is complete, bijective, and still represented
 * by the live corpus while permitting later chapters and semantic IDs.
 *
 * Usage:
 *   node scripts/semantic-id-migration.mjs --check
 *   node scripts/semantic-id-migration.mjs --self-test
 */

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, sep } from 'node:path';

const root = process.cwd();
const chapterDir = join(root, 'src/content/transformers');
const manifestPath = join(root, 'docs/manifests/semantic-id-migration.json');
const corpusManifestPath = join(root, 'docs/manifests/corpus.json');

const EXPECTED_BASELINE_COMMIT = '9e10cc16ec61627a59d8445be7763d0fc1d9673c';
const EXPECTED_BASELINE_CORPUS_SHA256 = '16d9004b58c04d7c5b74bdd33fa66bb298c52499a3704b7f2d4aa5b09ad67a1d';
const EXPECTED_TARGET_CORPUS_SHA256 = '8a154e52f097675a005edea37dad5a962e1ca58802d93fe164496aee5733232b';

const EXPECTED_TOTALS = Object.freeze({
  chapters: 19,
  anchors: 252,
  learningObjectives: 86,
  xrefs: 654,
  frontmatterRegistryRefs: 172,
  exercises: 101,
  exerciseOccurrences: 105,
  figures: 27,
  labeledFigures: 26,
});

// Hashes use sorted UTF-8 records joined by "\n", including one final "\n".
// They pin the exact A2 source inventory and the approved A3 mapping without
// embedding hundreds of identifiers in this checker.
const EXPECTED_HASHES = Object.freeze({
  chapterRowsSha256: '01c005fc3cf2590f4517614b6ffe480b3f58824850a081e3b8f49e7eec79de4a',
  sourceAnchorsSha256: 'bb9f99f78f608f7a750c1442e76bea23b20ef9c622f1470f4e75ff660d038fd5',
  targetAnchorsSha256: 'f4c9860e0747df0dd4993d2a7e396ebe7dd726478c67fdffa86a9a9c5244f15a',
  anchorMappingsSha256: '31db83dc763e951fa7988879c29b2e3c22133f3a92a36de4b6e9fa802b45948c',
  sourceLearningObjectivesSha256: '8c0fa811b28a26c64afc76545f3ed524e2a72569e6a20a3f0238f1243dd6dbb8',
  targetLearningObjectivesSha256: 'e02b7e9af565880cd4c49befbfea7d1c3944f15cc3dd6c8ee3ea7148658572ef',
  learningObjectiveMappingsSha256: '0ee6e4a0224300a8b60eb135c418c0eb26413bf3317e8dcf896369e2e198dd9d',
  sourceExercisesSha256: '0336cd8da63e0909ec4125c0c71101ed993c4d8a4ee29a5d60e8794a7d32eb32',
  targetExercisesSha256: '0cf4b944f5402bae562f033f3da155d2331b518bb7435f404ed67c5f663b7985',
  exerciseRowsSha256: '54281a5359a8d81cea4dc8e4cb1cfbae4980661d8857fc29bc2e16b3c6298b9c',
});

const EXPECTED_FROZEN_REFERENCE_HASHES = Object.freeze({
  // Records are owner slug, owner path, zero-padded occurrence ordinal, and target ID.
  xrefsSha256: 'ece9223ffe85ca6ae76dfba963f3360bb3030ed8c2d68d091801daaa44182c57',
  registryRefsSha256: '007ac306c8dff9af43f806a5ccffa32b060d1be2ce5ea5d0fd0cf57a2694d744',
});

// These are the checksums recorded by the canonical migration ledger. The
// checker also derives independent sorted-record hashes below, so changing a
// mapping and merely preserving these metadata fields cannot hide drift.
const EXPECTED_MANIFEST_CHECKSUMS = Object.freeze({
  chapterMapSha256: '392ad5eac41b9948291f6865c5c850b191c855c37c44286c76e5faf1640da73c',
  anchorMapSha256: '35b336666e259f30173b96d7221680a7b9af69acb40ab2ac6a084fb36f0431df',
  learningObjectiveMapSha256: '4d9a6932817e759695a572dc2f392c0df43cdfd3461916b5af5837c7037f6436',
  exerciseMapSha256: 'eb6aaed6d68838de40a0e4409a871bea954ecf2a3c69bc961f1a0a19a5b983dd',
});

const EXPECTED_CHAPTERS = Object.freeze([
  [0, 0, 1, 'notation'],
  [1, 1, 1, 'input-representations'],
  [2, 2, 2, 'recurrent-networks'],
  [3, 3, 2, 'state-space-models'],
  [4, 4, 3, 'attention'],
  [5, 5, 3, 'multi-head-attention'],
  [6, 6, 3, 'transformer-block'],
  [7, 7, 3, 'architecture-composition'],
  [8, 9, 3, 'encoder-decoder-families'],
  [9, 10, 3, 'training'],
  [10, 12, 3, 'detection-encoders'],
  [11, 14, 4, 'training-optimizations'],
  [12, 15, 4, 'inference-optimizations'],
  [13, 18, 5, 'selective-state-spaces'],
  [14, 19, 5, 'hybrid-architectures'],
  [15, 20, 6, 'connectors-resamplers'],
  [16, 21, 6, 'discrete-visual-tokenization'],
  [17, 22, 6, 'unified-multimodal-models'],
  [18, 23, 6, 'multimodal-evaluation'],
].map(([oldChapter, newChapter, part, slug]) => ({ oldChapter, newChapter, part, slug })));

const EXPECTED_RESERVED = Object.freeze([
  { chapter: 8, part: 3, title: 'In-context Learning', plannedTrack: 'B2' },
  { chapter: 11, part: 3, title: 'DPO / Preference Optimization', plannedTrack: 'B3' },
  { chapter: 13, part: 4, title: 'Scaling Laws', plannedTrack: 'B4' },
  { chapter: 16, part: 4, title: 'Mixture-of-Experts', plannedTrack: 'A5' },
  { chapter: 17, part: 5, title: 'Sparse & Sub-Quadratic Attention', plannedTrack: 'A6' },
]);

const EXPECTED_UNANCHORED_FIGURE = Object.freeze({
  kind: 'Figure',
  ownerSlug: 'hybrid-architectures',
  src: '/figures/hybrid-interleave.svg',
  decision: 'preserved-unlabeled',
});

const LEGACY_ID_PATTERN = /-tf\d+-|\bTF-\d+\.\d+\b/g;
const SEMANTIC_ID_PATTERN = /^[a-z][a-z0-9]*(?:-[a-z0-9]+)+$/;
const SEMANTIC_LO_PATTERN = /^lo-[a-z0-9]+(?:-[a-z0-9]+)*$/;

function posix(path) {
  return path.split(sep).join('/');
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

function hashRecords(records) {
  return sha256(`${[...records].sort().join('\n')}\n`);
}

function hashJson(value) {
  return sha256(JSON.stringify(value));
}

function scalar(source, key) {
  const match = source.match(new RegExp(`^${key}:\\s*(.+?)\\s*$`, 'm'));
  if (!match) throw new Error(`missing ${key}`);
  const raw = match[1].replace(/^['"]|['"]$/g, '');
  return /^-?\d+$/.test(raw) ? Number(raw) : raw;
}

function frontmatter(source) {
  return source.match(/^---\r?\n([\s\S]*?)\r?\n---/)?.[1] ?? '';
}

function attribute(attributes, key) {
  return attributes.match(new RegExp(`\\b${key}\\s*=\\s*["']([^"']+)["']`))?.[1];
}

function parseRegistry(front) {
  const line = front.match(/^theorems:\s*(.*)$/m);
  if (!line) return [];
  if (line[1].trim().startsWith('[')) {
    return [...line[1].matchAll(/['"]([^'"]+)['"]/g)].map((match) => match[1]);
  }
  const start = line.index + line[0].length;
  const tail = front.slice(start);
  const block = tail.match(/^\r?\n([\s\S]*?)(?=^[a-zA-Z_][\w-]*:\s*|$)/m)?.[1] ?? '';
  return [...block.matchAll(/^\s*-\s*['"]?([^'"\s]+)['"]?\s*$/gm)].map((match) => match[1]);
}

function parseChapter(path) {
  const source = readFileSync(path, 'utf8');
  const front = frontmatter(source);
  const anchors = [...source.matchAll(/<(?:Theorem|Figure|ExampleBox|ResultBox|NoteBox|CaseStudy)\b([^>]*)>/g)]
    .map((match) => attribute(match[1], 'id'))
    .filter(Boolean);
  const xrefs = [...source.matchAll(/<XRef\b[^>]*\bid\s*=\s*["']([^"']+)["']/g)].map(
    (match) => match[1],
  );
  const learningObjectives = [...front.matchAll(/^\s*- id:\s*([^\s]+)\s*$/gm)].map(
    (match) => match[1],
  );
  const figures = [...source.matchAll(/<Figure\b([^>]*)\/?\s*>/g)].map((match) => ({
    id: attribute(match[1], 'id'),
    src: attribute(match[1], 'src'),
  }));
  const exerciseOccurrences = [...source.matchAll(/\bExercise\s+(\d+)\.(\d+)\b/g)].map(
    (match) => `Exercise ${match[1]}.${match[2]}`,
  );
  const exerciseHeadingLines = [...source.matchAll(/^\*\*Exercise[^\n]*/gm)].map(
    (match) => match[0],
  );
  const parsedExerciseHeadings = exerciseHeadingLines.map((line) => ({
    line,
    match: /^\*\*Exercise\s+(\d+)\.(\d+)\s+\([^)]+\)\.\*\*/.exec(line),
  }));
  const exerciseHeadings = parsedExerciseHeadings
    .filter(({ match }) => match)
    .map(({ match }) => `Exercise ${match[1]}.${match[2]}`);
  const malformedExerciseHeadings = parsedExerciseHeadings
    .filter(({ match }) => !match)
    .map(({ line }) => line);
  return {
    path: posix(relative(root, path)),
    source,
    slug: scalar(front, 'slug'),
    chapter: scalar(front, 'chapter'),
    part: scalar(front, 'part'),
    anchors,
    xrefs,
    learningObjectives,
    registry: parseRegistry(front),
    figures,
    exerciseOccurrences,
    exerciseHeadings,
    malformedExerciseHeadings,
  };
}

function walkFiles(path, extensions) {
  if (!existsSync(path)) return [];
  if (statSync(path).isFile()) return extensions.some((ext) => path.endsWith(ext)) ? [path] : [];
  return readdirSync(path, { withFileTypes: true }).flatMap((entry) => {
    const child = join(path, entry.name);
    return entry.isDirectory() ? walkFiles(child, extensions) : walkFiles(child, extensions);
  });
}

function duplicateValues(values) {
  const counts = new Map();
  for (const value of values) counts.set(value, (counts.get(value) ?? 0) + 1);
  return [...counts.entries()].filter(([, count]) => count > 1).map(([value]) => value);
}

function ownedOccurrenceRecords(chapters, field) {
  return chapters.flatMap((chapter) =>
    chapter[field].map(
      (id, index) =>
        `${chapter.slug}\t${chapter.path}\t${String(index + 1).padStart(4, '0')}\t${id}`,
    ),
  );
}

function expectedAnchorTarget(old) {
  if (old === 'prop-tf2-bottleneck') return 'prop-seq2seq-fixed-vector-bottleneck';
  if (old === 'prop-tf15-bottleneck') return 'prop-connector-data-processing-bound';
  return old.replace(/-tf\d+(?=-)/, '');
}

function parseExercise(value) {
  const match = /^Exercise\s+(\d+)\.(\d+)$/.exec(value);
  return match ? { chapter: Number(match[1]), ordinal: Number(match[2]) } : null;
}

function readJson(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch (error) {
    throw new Error(`${posix(relative(root, path))}: ${error.message}`);
  }
}

function validateManifest(manifest, check) {
  check(manifest?.schemaVersion === 1, 'manifest schemaVersion must be 1');
  check(
    manifest?.generatedBy === 'scripts/semantic-id-migration.mjs',
    'manifest generatedBy must name scripts/semantic-id-migration.mjs',
  );
  check(manifest?.baseline?.commit === EXPECTED_BASELINE_COMMIT, 'manifest baseline commit is not A2');
  check(
    manifest?.baseline?.corpusManifestSha256 === EXPECTED_BASELINE_CORPUS_SHA256,
    'manifest baseline corpus hash is not the frozen A2 corpus',
  );

  for (const [key, expected] of Object.entries(EXPECTED_TOTALS)) {
    check(manifest?.baseline?.totals?.[key] === expected, `baseline.totals.${key} must be ${expected}`);
  }
  check(
    Object.keys(manifest?.baseline?.totals ?? {}).length === Object.keys(EXPECTED_TOTALS).length,
    'baseline.totals must contain only the nine frozen A2 counters',
  );

  for (const [key, expected] of Object.entries(EXPECTED_MANIFEST_CHECKSUMS)) {
    check(manifest?.checksums?.[key] === expected, `checksums.${key} must be ${expected}`);
  }
  check(
    Object.keys(manifest?.checksums ?? {}).length === Object.keys(EXPECTED_MANIFEST_CHECKSUMS).length,
    'manifest checksums must contain exactly the four canonical fields',
  );

  const chapters = Array.isArray(manifest?.chapters) ? manifest.chapters : [];
  check(chapters.length === EXPECTED_TOTALS.chapters, 'manifest must contain 19 chapter mappings');
  const chapterBySlug = new Map(chapters.map((entry) => [entry.slug, entry]));
  check(chapterBySlug.size === chapters.length, 'manifest chapter slugs must be unique');
  check(
    new Set(chapters.map((entry) => entry.oldChapter)).size === chapters.length,
    'manifest old chapter numbers must be unique',
  );
  check(
    new Set(chapters.map((entry) => entry.newChapter)).size === chapters.length,
    'manifest new chapter numbers must be unique',
  );
  check(
    new Set(chapters.map((entry) => entry.oldPath)).size === chapters.length,
    'manifest old chapter paths must be unique',
  );
  check(
    new Set(chapters.map((entry) => entry.newPath)).size === chapters.length,
    'manifest new chapter paths must be unique',
  );
  for (const expected of EXPECTED_CHAPTERS) {
    const entry = chapterBySlug.get(expected.slug);
    check(Boolean(entry), `manifest is missing chapter mapping for ${expected.slug}`);
    if (!entry) continue;
    for (const key of ['oldChapter', 'newChapter', 'part']) {
      check(entry[key] === expected[key], `${expected.slug}: ${key} must be ${expected[key]}`);
    }
    check(
      typeof entry.title === 'string' && entry.title.trim().length > 0,
      `${expected.slug}: title is required`,
    );
    check(
      entry.status === (expected.oldChapter === expected.newChapter ? 'unchanged-number' : 'renumbered'),
      `${expected.slug}: status does not match its number mapping`,
    );
    const oldPrefix = String(expected.oldChapter).padStart(2, '0');
    const newPrefix = String(expected.newChapter).padStart(2, '0');
    check(
      entry.oldPath === `src/content/transformers/${oldPrefix}-${expected.slug}.mdx`,
      `${expected.slug}: incorrect oldPath`,
    );
    check(
      entry.newPath === `src/content/transformers/${newPrefix}-${expected.slug}.mdx`,
      `${expected.slug}: incorrect newPath`,
    );
  }

  const reserved = Array.isArray(manifest?.reservedSlots) ? manifest.reservedSlots : [];
  check(reserved.length === EXPECTED_RESERVED.length, 'manifest must contain five reserved slots');
  const reservedByNumber = new Map(reserved.map((entry) => [entry.chapter, entry]));
  check(reservedByNumber.size === reserved.length, 'reserved chapter numbers must be unique');
  for (const expected of EXPECTED_RESERVED) {
    const entry = reservedByNumber.get(expected.chapter);
    check(Boolean(entry), `manifest is missing reserved chapter ${expected.chapter}`);
    if (!entry) continue;
    check(entry.title === expected.title, `reserved chapter ${expected.chapter} has the wrong title`);
    check(
      entry.plannedTrack === expected.plannedTrack,
      `reserved chapter ${expected.chapter} must belong to Track ${expected.plannedTrack}`,
    );
    check(
      !chapters.some((chapter) => chapter.newChapter === expected.chapter),
      `reserved chapter ${expected.chapter} collides with an A3 chapter mapping`,
    );
  }

  const anchorMapped = Array.isArray(manifest?.anchors?.mapped) ? manifest.anchors.mapped : [];
  const anchorRetired = Array.isArray(manifest?.anchors?.retired) ? manifest.anchors.retired : [];
  check(anchorMapped.length === EXPECTED_TOTALS.anchors, 'all 252 baseline anchors must be mapped');
  check(anchorRetired.length === 0, 'A3 retires no baseline anchors');
  const anchorOld = anchorMapped.map((entry) => entry.oldId);
  const anchorNew = anchorMapped.map((entry) => entry.newId);
  check(new Set(anchorOld).size === anchorOld.length, 'mapped anchor source IDs must be unique');
  check(new Set(anchorNew).size === anchorNew.length, 'mapped anchor target IDs must be unique');
  for (const entry of anchorMapped) {
    check(
      entry.newId === expectedAnchorTarget(entry.oldId),
      `${entry.oldId}: target must be ${expectedAnchorTarget(entry.oldId)}`,
    );
    check(SEMANTIC_ID_PATTERN.test(entry.newId), `${entry.newId}: invalid semantic anchor target`);
    check(typeof entry.ownerSlug === 'string', `${entry.oldId}: ownerSlug is required`);
    const chapter = chapterBySlug.get(entry.ownerSlug);
    check(Boolean(chapter), `${entry.oldId}: unknown ownerSlug ${entry.ownerSlug}`);
    if (chapter) {
      check(entry.oldPath === chapter.oldPath, `${entry.oldId}: oldPath disagrees with owner`);
      check(entry.newPath === chapter.newPath, `${entry.oldId}: newPath disagrees with owner`);
    }
    check(
      entry.identity === (entry.oldId === entry.newId),
      `${entry.oldId}: identity flag disagrees with the mapping`,
    );
  }
  check(
    anchorMapped.filter((entry) => entry.oldId === entry.newId).length === 37,
    'exactly 37 anchors must map identically',
  );
  check(
    anchorMapped.filter((entry) => entry.oldId !== entry.newId).length === 215,
    'exactly 215 anchors must change',
  );

  const loMapped = Array.isArray(manifest?.learningObjectives?.mapped)
    ? manifest.learningObjectives.mapped
    : [];
  const loRetired = Array.isArray(manifest?.learningObjectives?.retired)
    ? manifest.learningObjectives.retired
    : [];
  check(loMapped.length === EXPECTED_TOTALS.learningObjectives, 'all 86 baseline learning objectives must be mapped');
  check(loRetired.length === 0, 'A3 retires no learning objectives');
  const loOld = loMapped.map((entry) => entry.oldId);
  const loNew = loMapped.map((entry) => entry.newId);
  check(new Set(loOld).size === loOld.length, 'learning-objective source IDs must be unique');
  check(new Set(loNew).size === loNew.length, 'learning-objective target IDs must be unique');
  for (const entry of loMapped) {
    check(/^TF-\d+\.\d+$/.test(entry.oldId), `${entry.oldId}: invalid legacy learning-objective ID`);
    check(SEMANTIC_LO_PATTERN.test(entry.newId), `${entry.newId}: invalid semantic learning-objective ID`);
    check(typeof entry.ownerSlug === 'string', `${entry.oldId}: ownerSlug is required`);
    const chapter = chapterBySlug.get(entry.ownerSlug);
    check(Boolean(chapter), `${entry.oldId}: unknown ownerSlug ${entry.ownerSlug}`);
    if (chapter) {
      check(entry.oldPath === chapter.oldPath, `${entry.oldId}: oldPath disagrees with owner`);
      check(entry.newPath === chapter.newPath, `${entry.oldId}: newPath disagrees with owner`);
    }
  }

  const exercises = Array.isArray(manifest?.exercises) ? manifest.exercises : [];
  check(exercises.length === EXPECTED_TOTALS.exercises, 'manifest must contain 101 exercise mappings');
  check(
    new Set(exercises.map((entry) => entry.oldLabel)).size === exercises.length,
    'exercise source labels must be unique',
  );
  check(
    new Set(exercises.map((entry) => entry.newLabel)).size === exercises.length,
    'exercise target labels must be unique',
  );
  check(
    exercises.reduce((sum, entry) => sum + entry.occurrences, 0) === EXPECTED_TOTALS.exerciseOccurrences,
    'exercise occurrence counts must sum to 105',
  );
  const numberMap = new Map(EXPECTED_CHAPTERS.map((entry) => [entry.oldChapter, entry.newChapter]));
  for (const entry of exercises) {
    const oldExercise = parseExercise(entry.oldLabel);
    const newExercise = parseExercise(entry.newLabel);
    check(Boolean(oldExercise), `${entry.oldLabel}: invalid old exercise label`);
    check(Boolean(newExercise), `${entry.newLabel}: invalid new exercise label`);
    check(
      Number.isInteger(entry.occurrences) && entry.occurrences > 0,
      `${entry.oldLabel}: invalid occurrence count`,
    );
    check(typeof entry.ownerSlug === 'string', `${entry.oldLabel}: ownerSlug is required`);
    const chapter = chapterBySlug.get(entry.ownerSlug);
    check(Boolean(chapter), `${entry.oldLabel}: unknown ownerSlug ${entry.ownerSlug}`);
    if (!oldExercise || !newExercise || !chapter) continue;
    check(entry.oldPath === chapter.oldPath, `${entry.oldLabel}: oldPath disagrees with owner`);
    check(entry.newPath === chapter.newPath, `${entry.oldLabel}: newPath disagrees with owner`);
    check(oldExercise.chapter === chapter.oldChapter, `${entry.oldLabel}: old chapter disagrees with owner`);
    check(newExercise.chapter === chapter.newChapter, `${entry.newLabel}: new chapter disagrees with owner`);
    check(oldExercise.ordinal === newExercise.ordinal, `${entry.oldLabel}: exercise ordinal changed`);
    check(entry.ordinal === oldExercise.ordinal, `${entry.oldLabel}: ordinal field disagrees with its label`);
    check(
      numberMap.get(oldExercise.chapter) === newExercise.chapter,
      `${entry.oldLabel}: exercise chapter does not follow the final-number map`,
    );
  }

  const unanchored = Array.isArray(manifest?.unanchoredComponents) ? manifest.unanchoredComponents : [];
  check(unanchored.length === 1, 'manifest must record exactly one unanchored component');
  const exception = unanchored[0] ?? {};
  for (const [key, expected] of Object.entries(EXPECTED_UNANCHORED_FIGURE)) {
    check(exception[key] === expected, `unanchored figure ${key} must be ${expected}`);
  }
  const exceptionOwner = chapterBySlug.get(exception.ownerSlug);
  if (exceptionOwner) {
    check(exception.oldPath === exceptionOwner.oldPath, 'unanchored figure oldPath disagrees with owner');
    check(exception.newPath === exceptionOwner.newPath, 'unanchored figure newPath disagrees with owner');
  }
  check(
    typeof exception.reason === 'string' && exception.reason.trim().length > 0,
    'unanchored figure must record a reason',
  );

  const computedHashes = {
    chapterRowsSha256: hashRecords(
      chapters.map((entry) =>
        [
          entry.slug,
          entry.title,
          entry.part,
          entry.oldChapter,
          entry.newChapter,
          entry.oldPath,
          entry.newPath,
          entry.status,
        ].join('\t'),
      ),
    ),
    sourceAnchorsSha256: hashRecords(anchorOld),
    targetAnchorsSha256: hashRecords(anchorNew),
    anchorMappingsSha256: hashRecords(anchorMapped.map((entry) => `${entry.oldId}\t${entry.newId}`)),
    sourceLearningObjectivesSha256: hashRecords(loOld),
    targetLearningObjectivesSha256: hashRecords(loNew),
    learningObjectiveMappingsSha256: hashRecords(
      loMapped.map((entry) => `${entry.oldId}\t${entry.newId}`),
    ),
    sourceExercisesSha256: hashRecords(
      exercises.map((entry) => `${entry.oldLabel}\t${entry.occurrences}`),
    ),
    targetExercisesSha256: hashRecords(
      exercises.map((entry) => `${entry.newLabel}\t${entry.occurrences}`),
    ),
    exerciseRowsSha256: hashRecords(
      exercises.map((entry) =>
        [
          entry.ownerSlug,
          entry.oldPath,
          entry.newPath,
          entry.ordinal,
          entry.oldLabel,
          entry.newLabel,
          entry.occurrences,
        ].join('\t'),
      ),
    ),
  };
  for (const [key, expected] of Object.entries(EXPECTED_HASHES)) {
    check(computedHashes[key] === expected, `${key}: manifest mapping does not match the frozen migration design`);
  }
  check(
    hashJson(anchorMapped.map(({ oldId, newId, ownerSlug }) => ({ oldId, newId, ownerSlug }))) ===
      manifest?.checksums?.anchorMapSha256,
    'checksums.anchorMapSha256 does not match the canonical anchor projection',
  );
  check(
    hashJson(loMapped.map(({ oldId, newId, ownerSlug }) => ({ oldId, newId, ownerSlug }))) ===
      manifest?.checksums?.learningObjectiveMapSha256,
    'checksums.learningObjectiveMapSha256 does not match the canonical learning-objective projection',
  );

  return { chapterBySlug, reservedByNumber, anchorMapped, loMapped, exercises };
}

function isFrozenA3Target(corpusManifestSha256, totals) {
  return (
    corpusManifestSha256 === EXPECTED_TARGET_CORPUS_SHA256 &&
    Object.entries(EXPECTED_TOTALS).every(([key, expected]) => totals[key] === expected)
  );
}

function validateFrozenExerciseLedger(
  frozen,
  manifestExercises,
  currentBySlug,
  exerciseHeadings,
  exerciseOccurrenceCounts,
  check,
) {
  if (!frozen) return;
  for (const entry of manifestExercises) {
    const owner = currentBySlug.get(entry.ownerSlug);
    check(
      exerciseHeadings.some(
        ({ id, chapter }) => id === entry.newLabel && chapter.slug === entry.ownerSlug,
      ),
      `${entry.newLabel}: frozen A3 exercise must remain in ${entry.ownerSlug}`,
    );
    check(
      (exerciseOccurrenceCounts.get(entry.newLabel) ?? 0) >= entry.occurrences,
      `${entry.newLabel}: fewer than ${entry.occurrences} frozen A3 occurrence(s)`,
    );
    if (owner) {
      const ownerOccurrences = owner.exerciseOccurrences.filter(
        (id) => id === entry.newLabel,
      ).length;
      check(
        ownerOccurrences >= entry.occurrences,
        `${entry.newLabel}: fewer than ${entry.occurrences} occurrence(s) remain in ${entry.ownerSlug}`,
      );
    }
  }
}

function validateUnlabeledFigurePolicy(frozen, unlabeledFigures, check) {
  if (frozen) {
    check(unlabeledFigures.length === 1, 'frozen A3 target must have exactly one unlabeled Figure');
    const unlabeled = unlabeledFigures[0] ?? {};
    check(
      unlabeled.ownerSlug === EXPECTED_UNANCHORED_FIGURE.ownerSlug &&
        unlabeled.src === EXPECTED_UNANCHORED_FIGURE.src,
      'the frozen A3 unlabeled Figure must be hybrid-interleave in hybrid-architectures',
    );
    return;
  }
  check(unlabeledFigures.length <= 1, 'post-A3 chapters may not add unlabeled Figures');
  for (const figure of unlabeledFigures) {
    check(
      figure.src === EXPECTED_UNANCHORED_FIGURE.src,
      `post-A3 unlabeled Figure is not the preserved exception: ${figure.src}`,
    );
  }
}

function validateLiveCorpus(validated, check) {
  const chapters = readdirSync(chapterDir)
    .filter((name) => name.endsWith('.mdx'))
    .map((name) => parseChapter(join(chapterDir, name)))
    .sort((a, b) => a.part - b.part || a.chapter - b.chapter || a.slug.localeCompare(b.slug));

  const duplicateSlugs = duplicateValues(chapters.map((chapter) => chapter.slug));
  const duplicateNumbers = duplicateValues(chapters.map((chapter) => chapter.chapter));
  check(duplicateSlugs.length === 0, `duplicate chapter slugs: ${duplicateSlugs.join(', ')}`);
  check(duplicateNumbers.length === 0, `duplicate chapter numbers: ${duplicateNumbers.join(', ')}`);

  const currentBySlug = new Map(chapters.map((chapter) => [chapter.slug, chapter]));
  const allowedNumbers = new Set([
    ...EXPECTED_CHAPTERS.map((entry) => entry.newChapter),
    ...EXPECTED_RESERVED.map((entry) => entry.chapter),
  ]);
  for (const chapter of chapters) {
    check(allowedNumbers.has(chapter.chapter), `${chapter.path}: chapter ${chapter.chapter} is not allocated`);
    const expectedPath = `src/content/transformers/${String(chapter.chapter).padStart(2, '0')}-${chapter.slug}.mdx`;
    check(chapter.path === expectedPath, `${chapter.path}: expected path ${expectedPath}`);
  }
  for (const expected of EXPECTED_CHAPTERS) {
    const chapter = currentBySlug.get(expected.slug);
    check(Boolean(chapter), `live corpus is missing baseline chapter ${expected.slug}`);
    if (!chapter) continue;
    check(
      chapter.chapter === expected.newChapter,
      `${expected.slug}: live chapter must be ${expected.newChapter}`,
    );
    check(chapter.part === expected.part, `${expected.slug}: live part must be ${expected.part}`);
  }
  for (const expected of EXPECTED_RESERVED) {
    const chapter = chapters.find((candidate) => candidate.chapter === expected.chapter);
    if (!chapter) continue;
    check(chapter.part === expected.part, `${chapter.slug}: reserved chapter ${expected.chapter} has the wrong part`);
  }

  const anchorOwners = new Map();
  const allAnchors = [];
  for (const chapter of chapters) {
    for (const id of chapter.anchors) {
      allAnchors.push(id);
      const owners = anchorOwners.get(id) ?? [];
      owners.push(chapter.slug);
      anchorOwners.set(id, owners);
    }
  }
  const duplicateAnchors = [...anchorOwners.entries()].filter(([, owners]) => owners.length > 1);
  check(
    duplicateAnchors.length === 0,
    `duplicate anchors: ${duplicateAnchors.map(([id]) => id).join(', ')}`,
  );
  for (const id of allAnchors) {
    check(!LEGACY_ID_PATTERN.test(id), `${id}: legacy anchor remains`);
    LEGACY_ID_PATTERN.lastIndex = 0;
    check(SEMANTIC_ID_PATTERN.test(id), `${id}: anchor is not a semantic kebab-case ID`);
  }

  const allLearningObjectives = chapters.flatMap((chapter) => chapter.learningObjectives);
  const duplicateLearningObjectives = duplicateValues(allLearningObjectives);
  check(
    duplicateLearningObjectives.length === 0,
    `duplicate learning objectives: ${duplicateLearningObjectives.join(', ')}`,
  );
  for (const id of allLearningObjectives) {
    check(SEMANTIC_LO_PATTERN.test(id), `${id}: learning-objective ID is not semantic`);
  }

  const allXrefs = chapters.flatMap((chapter) => chapter.xrefs);
  const xrefRecords = ownedOccurrenceRecords(chapters, 'xrefs');
  for (const id of allXrefs) check(anchorOwners.has(id), `dangling XRef: ${id}`);
  const allRegistry = chapters.flatMap((chapter) => chapter.registry);
  const registryRecords = ownedOccurrenceRecords(chapters, 'registry');
  for (const id of allRegistry) check(anchorOwners.has(id), `dangling frontmatter theorem registry entry: ${id}`);

  for (const entry of validated.anchorMapped) {
    check(anchorOwners.has(entry.newId), `mapped anchor target is absent: ${entry.newId}`);
    if (entry.oldId !== entry.newId) {
      check(!anchorOwners.has(entry.oldId), `legacy anchor target still exists: ${entry.oldId}`);
    }
  }
  for (const entry of validated.loMapped) {
    check(
      allLearningObjectives.includes(entry.newId),
      `mapped learning objective is absent: ${entry.newId}`,
    );
    check(
      !allLearningObjectives.includes(entry.oldId),
      `legacy learning objective still exists: ${entry.oldId}`,
    );
  }

  const exerciseHeadings = chapters.flatMap((chapter) =>
    chapter.exerciseHeadings.map((id) => ({ id, chapter })),
  );
  for (const chapter of chapters) {
    for (const heading of chapter.malformedExerciseHeadings) {
      check(false, `${chapter.path}: malformed exercise heading (${heading})`);
    }
  }
  const duplicateExerciseHeadings = duplicateValues(exerciseHeadings.map(({ id }) => id));
  check(
    duplicateExerciseHeadings.length === 0,
    `duplicate exercise headings: ${duplicateExerciseHeadings.join(', ')}`,
  );
  for (const { id, chapter } of exerciseHeadings) {
    const parsed = parseExercise(id);
    check(parsed?.chapter === chapter.chapter, `${chapter.path}: ${id} disagrees with owning chapter`);
  }
  const exerciseHeadingIds = new Set(exerciseHeadings.map(({ id }) => id));
  const exerciseOccurrenceCounts = new Map();
  for (const id of chapters.flatMap((chapter) => chapter.exerciseOccurrences)) {
    exerciseOccurrenceCounts.set(id, (exerciseOccurrenceCounts.get(id) ?? 0) + 1);
  }
  for (const id of exerciseOccurrenceCounts.keys()) {
    check(
      exerciseHeadingIds.has(id),
      `exercise occurrence has no current heading: ${id}`,
    );
  }

  const allFigures = chapters.flatMap((chapter) =>
    chapter.figures.map((figure) => ({ ...figure, ownerSlug: chapter.slug })),
  );
  const unlabeledFigures = allFigures.filter((figure) => !figure.id);
  const exerciseOccurrenceTotal = [...exerciseOccurrenceCounts.values()].reduce(
    (sum, count) => sum + count,
    0,
  );
  const labeledFigureCount = allFigures.filter((figure) => figure.id).length;
  const liveTotals = {
    chapters: chapters.length,
    anchors: allAnchors.length,
    learningObjectives: allLearningObjectives.length,
    xrefs: allXrefs.length,
    frontmatterRegistryRefs: allRegistry.length,
    exercises: exerciseHeadings.length,
    exerciseOccurrences: exerciseOccurrenceTotal,
    figures: allFigures.length,
    labeledFigures: labeledFigureCount,
  };
  const corpusManifestSha256 = sha256(readFileSync(corpusManifestPath));
  const frozen = isFrozenA3Target(corpusManifestSha256, liveTotals);
  const mode = frozen ? 'frozen A3 target' : 'post-A3 extension';

  validateUnlabeledFigurePolicy(frozen, unlabeledFigures, check);

  if (frozen) {
    check(chapters.length === EXPECTED_TOTALS.chapters, 'frozen A3 target must have exactly 19 chapters');
    check(allAnchors.length === EXPECTED_TOTALS.anchors, 'frozen A3 target must have exactly 252 anchors');
    check(
      allLearningObjectives.length === EXPECTED_TOTALS.learningObjectives,
      'frozen A3 target must have exactly 86 learning objectives',
    );
    check(allXrefs.length === EXPECTED_TOTALS.xrefs, 'frozen A3 target must have exactly 654 XRefs');
    check(
      allRegistry.length === EXPECTED_TOTALS.frontmatterRegistryRefs,
      'frozen A3 target must have exactly 172 registry refs',
    );
    check(
      exerciseHeadings.length === EXPECTED_TOTALS.exercises,
      'frozen A3 target must have exactly 101 exercise headings',
    );
    check(
      exerciseOccurrenceTotal === EXPECTED_TOTALS.exerciseOccurrences,
      'frozen A3 target must have exactly 105 exercise occurrences',
    );
    check(allFigures.length === EXPECTED_TOTALS.figures, 'frozen A3 target must have exactly 27 Figures');
    check(
      labeledFigureCount === EXPECTED_TOTALS.labeledFigures,
      'frozen A3 target must have exactly 26 labeled Figures',
    );
    validateFrozenExerciseLedger(
      frozen,
      validated.exercises,
      currentBySlug,
      exerciseHeadings,
      exerciseOccurrenceCounts,
      check,
    );
    check(
      hashRecords(allAnchors) === EXPECTED_HASHES.targetAnchorsSha256,
      'frozen A3 anchor inventory does not match the approved target',
    );
    check(
      hashRecords(allLearningObjectives) === EXPECTED_HASHES.targetLearningObjectivesSha256,
      'frozen A3 learning-objective inventory does not match the approved target',
    );
    check(
      hashRecords(xrefRecords) === EXPECTED_FROZEN_REFERENCE_HASHES.xrefsSha256,
      'frozen A3 XRef targets/owners/occurrence order do not match the approved target',
    );
    check(
      hashRecords(registryRecords) === EXPECTED_FROZEN_REFERENCE_HASHES.registryRefsSha256,
      'frozen A3 registry targets/owners/occurrence order do not match the approved target',
    );
    for (const entry of validated.anchorMapped) {
      check(
        anchorOwners.get(entry.newId)?.includes(entry.ownerSlug),
        `${entry.newId}: frozen A3 owner must be ${entry.ownerSlug}`,
      );
    }
  } else {
    check(chapters.length >= EXPECTED_TOTALS.chapters, 'post-A3 corpus cannot lose baseline chapters');
    check(allAnchors.length >= EXPECTED_TOTALS.anchors, 'post-A3 corpus cannot lose baseline anchors');
    check(
      allLearningObjectives.length >= EXPECTED_TOTALS.learningObjectives,
      'post-A3 corpus cannot lose baseline learning objectives',
    );
    check(allXrefs.length >= EXPECTED_TOTALS.xrefs, 'post-A3 corpus cannot fall below the baseline XRef count');
    check(
      allRegistry.length >= EXPECTED_TOTALS.frontmatterRegistryRefs,
      'post-A3 corpus cannot fall below the baseline registry-ref count',
    );
    check(exerciseHeadings.length >= EXPECTED_TOTALS.exercises, 'post-A3 corpus cannot lose baseline exercises');
    check(
      exerciseOccurrenceTotal >= EXPECTED_TOTALS.exerciseOccurrences,
      'post-A3 corpus cannot lose baseline exercise occurrences',
    );
    check(allFigures.length >= EXPECTED_TOTALS.figures, 'post-A3 corpus cannot lose baseline Figures');
    check(
      labeledFigureCount >= EXPECTED_TOTALS.labeledFigures,
      'post-A3 corpus cannot lose baseline labeled Figures',
    );
  }

  return {
    mode,
    chapters: chapters.length,
    anchors: allAnchors.length,
    learningObjectives: allLearningObjectives.length,
    xrefs: allXrefs.length,
    registryRefs: allRegistry.length,
    exercises: exerciseHeadings.length,
    exerciseOccurrences: exerciseOccurrenceTotal,
    figures: allFigures.length,
  };
}

function validateLegacySurfaces(check) {
  const scopes = [
    { path: chapterDir, extensions: ['.md', '.mdx'] },
    { path: join(root, 'tests'), extensions: ['.py', '.json', '.md'] },
    { path: join(root, 'figures'), extensions: ['.tex', '.sty'] },
    { path: join(root, 'docs/plans/active'), extensions: ['.md'] },
    {
      path: join(root, '.claude/skills'),
      extensions: ['.md', '.json', '.toml', '.yaml', '.yml', '.js', '.mjs', '.ts', '.py', '.sh'],
    },
    { path: join(root, '.gitleaks.toml'), extensions: ['.toml'] },
  ];
  for (const scope of scopes) {
    for (const path of walkFiles(scope.path, scope.extensions)) {
      const source = readFileSync(path, 'utf8');
      const hits = [...source.matchAll(LEGACY_ID_PATTERN)].map((match) => match[0]);
      LEGACY_ID_PATTERN.lastIndex = 0;
      check(hits.length === 0, `${posix(relative(root, path))}: legacy IDs remain (${[...new Set(hits)].join(', ')})`);
    }
  }
}

function runCheck() {
  if (!existsSync(manifestPath)) {
    throw new Error(
      'docs/manifests/semantic-id-migration.json is missing; generate it during the atomic A3 migration',
    );
  }
  if (!existsSync(corpusManifestPath)) throw new Error('docs/manifests/corpus.json is missing');

  const errors = [];
  const check = (condition, message) => {
    if (!condition) errors.push(message);
  };
  const manifest = readJson(manifestPath);
  const validated = validateManifest(manifest, check);
  const live = validateLiveCorpus(validated, check);
  validateLegacySurfaces(check);
  if (errors.length) {
    throw new Error(`semantic-ID migration check failed (${errors.length}):\n- ${errors.join('\n- ')}`);
  }
  console.log(
    `semantic-id-migration: ${live.mode}; ${live.chapters} chapter(s), ${live.anchors} anchor(s), ` +
      `${live.learningObjectives} LO(s), ${live.xrefs} XRef(s), ${live.registryRefs} registry ref(s), ` +
      `${live.exercises} exercise(s)/${live.exerciseOccurrences} occurrence(s), ${live.figures} Figure(s) verified`,
  );
}

function runSelfTest() {
  const failures = [];
  const expect = (condition, message) => {
    if (!condition) failures.push(message);
  };
  expect(hashRecords(['b', 'a']) === '911169ddaaf146aff539f58c26c489af3b892dff0fe283c1c264c65ae5aa59a2', 'record hashing');
  expect(expectedAnchorTarget('def-tf12-cost-eq') === 'def-cost-eq', 'ordinary anchor mapping');
  expect(
    expectedAnchorTarget('prop-tf2-bottleneck') === 'prop-seq2seq-fixed-vector-bottleneck',
    'seq2seq collision override',
  );
  expect(
    expectedAnchorTarget('prop-tf15-bottleneck') === 'prop-connector-data-processing-bound',
    'connector collision override',
  );
  expect(expectedAnchorTarget('def-softmax') === 'def-softmax', 'identity anchor mapping');
  expect(attribute(' id="fig-example" src="/figures/example.svg"', 'src') === '/figures/example.svg', 'attribute parsing');
  expect(parseExercise('Exercise 12.6')?.ordinal === 6, 'exercise parsing');
  expect(
    ownedOccurrenceRecords(
      [{ slug: 'owner', path: 'chapter.mdx', xrefs: ['def-a', 'def-b'] }],
      'xrefs',
    )[1] === 'owner\tchapter.mdx\t0002\tdef-b',
    'owned reference occurrence projection',
  );
  expect(EXPECTED_CHAPTERS.length === EXPECTED_TOTALS.chapters, 'chapter-map cardinality');
  expect(
    new Set(EXPECTED_CHAPTERS.map((entry) => entry.newChapter)).size === 19,
    'chapter-map injectivity',
  );
  expect(new Set(EXPECTED_RESERVED.map((entry) => entry.chapter)).size === 5, 'reserved-slot cardinality');
  const allocatedNumbers = [
    ...new Set([
      ...EXPECTED_CHAPTERS.map((entry) => entry.newChapter),
      ...EXPECTED_RESERVED.map((entry) => entry.chapter),
    ]),
  ].sort((a, b) => a - b);
  expect(
    allocatedNumbers.join(',') === Array.from({ length: 24 }, (_, chapter) => chapter).join(','),
    'known plan must allocate exactly chapters 00-23',
  );
  expect(
    isFrozenA3Target(EXPECTED_TARGET_CORPUS_SHA256, { ...EXPECTED_TOTALS }),
    'frozen-target recognition',
  );
  expect(
    !isFrozenA3Target('0'.repeat(64), { ...EXPECTED_TOTALS }),
    'changed corpus enters extension mode',
  );
  expect(
    !isFrozenA3Target(EXPECTED_TARGET_CORPUS_SHA256, {
      ...EXPECTED_TOTALS,
      xrefs: EXPECTED_TOTALS.xrefs + 1,
    }),
    'cardinality growth enters extension mode',
  );

  const movedExercise = {
    ownerSlug: 'inference-optimizations',
    newLabel: 'Exercise 15.6',
    occurrences: 1,
  };
  const extensionExerciseErrors = [];
  validateFrozenExerciseLedger(
    false,
    [movedExercise],
    new Map(),
    [],
    new Map(),
    (condition, message) => {
      if (!condition) extensionExerciseErrors.push(message);
    },
  );
  expect(extensionExerciseErrors.length === 0, 'extension mode permits deliberate exercise moves');
  const frozenExerciseErrors = [];
  validateFrozenExerciseLedger(
    true,
    [movedExercise],
    new Map(),
    [],
    new Map(),
    (condition, message) => {
      if (!condition) frozenExerciseErrors.push(message);
    },
  );
  expect(frozenExerciseErrors.length > 0, 'frozen mode pins manifest exercise presence');

  const extensionFigureErrors = [];
  validateUnlabeledFigurePolicy(
    false,
    [{ ownerSlug: 'sparse-attention', src: EXPECTED_UNANCHORED_FIGURE.src }],
    (condition, message) => {
      if (!condition) extensionFigureErrors.push(message);
    },
  );
  expect(
    extensionFigureErrors.length === 0,
    'extension mode permits relocation of the preserved unlabeled Figure',
  );
  const newUnlabeledFigureErrors = [];
  validateUnlabeledFigurePolicy(
    false,
    [{ ownerSlug: 'sparse-attention', src: '/figures/new-unlabeled.svg' }],
    (condition, message) => {
      if (!condition) newUnlabeledFigureErrors.push(message);
    },
  );
  expect(newUnlabeledFigureErrors.length > 0, 'extension mode rejects new unlabeled Figures');
  if (failures.length) throw new Error(`semantic-ID checker self-test failed: ${failures.join(', ')}`);
  console.log('semantic-id-migration: self-test passed');
}

const checkMode = process.argv.includes('--check');
const selfTestMode = process.argv.includes('--self-test');
if (checkMode === selfTestMode) {
  console.error('usage: node scripts/semantic-id-migration.mjs (--check | --self-test)');
  process.exit(2);
}

try {
  if (selfTestMode) runSelfTest();
  else runCheck();
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
