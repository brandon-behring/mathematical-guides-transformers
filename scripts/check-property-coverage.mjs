#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, writeFileSync } from 'node:fs';
import { join, relative } from 'node:path';

const root = process.cwd();
const coveragePath = join(root, 'tests/properties/coverage.json');
const chapterDir = join(root, 'src/content/transformers');
const write = process.argv.includes('--write');

const coverage = JSON.parse(readFileSync(coveragePath, 'utf8'));
const chapters = readdirSync(chapterDir)
  .filter((name) => name.endsWith('.mdx'))
  .map((name) => ({ path: join(chapterDir, name), source: readFileSync(join(chapterDir, name), 'utf8') }));

function escapeRegex(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function normalizedClaimBlock(id) {
  const needle = escapeRegex(id);
  const pattern = new RegExp(`<Theorem\\b(?=[^>]*\\bid=["']${needle}["'])[^>]*>[\\s\\S]*?<\\/Theorem>`);
  const matches = chapters.flatMap((chapter) => {
    const match = chapter.source.match(pattern);
    return match ? [{ chapter: relative(root, chapter.path), block: match[0] }] : [];
  });
  if (matches.length !== 1) {
    throw new Error(`${id}: expected one theorem block, found ${matches.length}`);
  }
  return matches[0].block.replace(/\s+/g, ' ').trim();
}

let changed = false;
const seen = new Set();
for (const claim of coverage.claims) {
  if (seen.has(claim.id)) throw new Error(`duplicate property coverage id: ${claim.id}`);
  seen.add(claim.id);
  const testPath = join(root, claim.test);
  if (!existsSync(testPath)) throw new Error(`${claim.id}: missing test file ${claim.test}`);
  if (!readFileSync(testPath, 'utf8').includes(claim.id)) {
    throw new Error(`${claim.id}: ${claim.test} does not name the guarded id`);
  }
  const hash = createHash('sha256').update(normalizedClaimBlock(claim.id)).digest('hex');
  if (write) {
    if (claim.statementSha256 !== hash) changed = true;
    claim.statementSha256 = hash;
  } else if (claim.statementSha256 !== hash) {
    throw new Error(`${claim.id}: statement changed; review the test and run npm run update:property-coverage`);
  }
}

if (write && changed) writeFileSync(coveragePath, `${JSON.stringify(coverage, null, 2)}\n`);
console.log(`property-coverage: ${coverage.claims.length} guarded claim(s) ${write ? 'recorded' : 'verified'}`);
