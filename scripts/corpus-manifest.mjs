#!/usr/bin/env node

import { readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = process.cwd();
const chapterDir = join(root, 'src/content/transformers');
const manifestPath = join(root, 'docs/manifests/corpus.json');
const write = process.argv.includes('--write');

function scalar(source, key) {
  const match = source.match(new RegExp(`^${key}:\\s*(.+?)\\s*$`, 'm'));
  if (!match) throw new Error(`missing ${key}`);
  const raw = match[1].replace(/^['"]|['"]$/g, '');
  return /^-?\d+$/.test(raw) ? Number(raw) : raw;
}

function lineOf(source, offset) {
  return source.slice(0, offset).split('\n').length;
}

const chapters = readdirSync(chapterDir)
  .filter((name) => name.endsWith('.mdx'))
  .map((name) => {
    const path = join(chapterDir, name);
    const source = readFileSync(path, 'utf8');
    const labelIds = [...source.matchAll(/<(?:Theorem|Figure|ExampleBox|ResultBox|NoteBox|CaseStudy)\b([^>]*)>/g)]
      .map((match) => match[1].match(/\bid\s*=\s*["']([^"']+)["']/)?.[1])
      .filter(Boolean);
    const objectiveIds = [...source.matchAll(/^\s*- id:\s*([^\s]+)\s*$/gm)].map((match) => match[1]);
    const xrefs = [...source.matchAll(/<XRef\b[^>]*\bid=["']([^"']+)["'][^>]*\/?\s*>/g)].map((match) => match[1]);
    const numberPattern = /\b(?:Chapter|Ch\.|ch\.)\s*\d+\b|\bExercise\s+\d+\.\d+\b|\bTF-\d+\.\d+\b/g;
    const printedNumberHits = [...source.matchAll(numberPattern)].map((match) => ({
      line: lineOf(source, match.index),
      text: match[0],
    }));
    const kindCounts = {};
    for (const match of source.matchAll(/<Theorem\b([^>]*)>/g)) {
      const kind = match[1].match(/\bkind=["']([^"']+)["']/)?.[1] ?? 'theorem';
      kindCounts[kind] = (kindCounts[kind] ?? 0) + 1;
    }
    return {
      path: relative(root, path),
      slug: scalar(source, 'slug'),
      title: scalar(source, 'title'),
      chapter: scalar(source, 'chapter'),
      part: scalar(source, 'part'),
      labelIds: [...new Set(labelIds)].sort(),
      objectiveIds: [...new Set(objectiveIds)].sort(),
      xrefs: [...new Set(xrefs)].sort(),
      kindCounts: Object.fromEntries(Object.entries(kindCounts).sort()),
      proofMarkers: (source.match(/\\blacksquare/g) ?? []).length,
      printedNumberHits,
    };
  })
  .sort((a, b) => a.part - b.part || a.chapter - b.chapter || a.slug.localeCompare(b.slug));

const allLabels = new Map();
for (const chapter of chapters) {
  for (const id of chapter.labelIds) {
    const owners = allLabels.get(id) ?? [];
    owners.push(chapter.path);
    allLabels.set(id, owners);
  }
}
const duplicates = [...allLabels.entries()].filter(([, owners]) => owners.length > 1);
if (duplicates.length) throw new Error(`duplicate ids: ${duplicates.map(([id]) => id).join(', ')}`);

const dangling = [];
for (const chapter of chapters) {
  for (const id of chapter.xrefs) if (!allLabels.has(id)) dangling.push(`${chapter.path}:${id}`);
}
if (dangling.length) throw new Error(`dangling XRefs: ${dangling.join(', ')}`);

const manifest = {
  schemaVersion: 1,
  generatedBy: 'scripts/corpus-manifest.mjs',
  totals: {
    chapters: chapters.length,
    labels: allLabels.size,
    learningObjectives: chapters.reduce((sum, chapter) => sum + chapter.objectiveIds.length, 0),
    proofMarkers: chapters.reduce((sum, chapter) => sum + chapter.proofMarkers, 0),
    printedNumberHits: chapters.reduce((sum, chapter) => sum + chapter.printedNumberHits.length, 0),
  },
  chapters,
};
const rendered = `${JSON.stringify(manifest, null, 2)}\n`;

if (write) {
  writeFileSync(manifestPath, rendered);
  console.log(`corpus-manifest: wrote ${chapters.length} chapter(s), ${allLabels.size} label(s)`);
} else {
  const existing = readFileSync(manifestPath, 'utf8');
  if (existing !== rendered) throw new Error('corpus manifest is stale; run npm run update:corpus');
  console.log(`corpus-manifest: ${chapters.length} chapter(s), ${allLabels.size} label(s) verified`);
}
