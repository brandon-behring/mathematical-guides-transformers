#!/usr/bin/env node

/**
 * Render the print route with a protocol timeout large enough for the complete
 * book. pagedjs-cli exposes a page timeout, but its default Puppeteer launch
 * still caps a single CDP call at three minutes; the 21-chapter print route can
 * legitimately spend longer than that in Paged.js layout.
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import Printer from 'pagedjs-cli';
import puppeteer from 'puppeteer';

const [
  input = 'http://localhost:4321/transformers/print/',
  output = 'dist-pdf/book.pdf',
] = process.argv.slice(2);

const timeout = Number.parseInt(process.env.PDF_RENDER_TIMEOUT_MS ?? '900000', 10);
if (!Number.isFinite(timeout) || timeout <= 0) {
  throw new Error('PDF_RENDER_TIMEOUT_MS must be a positive integer');
}

const browser = await puppeteer.launch({
  headless: 'new',
  protocolTimeout: timeout,
  args: ['--disable-dev-shm-usage', '--export-tagged-pdf'],
});

const printer = new Printer({ timeout, closeAfter: false });
// Reuse the launch connection carrying protocolTimeout. Passing only a browser
// endpoint would make Printer reconnect with Puppeteer's shorter default.
printer.browser = browser;

printer.on('rendered', (message) => console.log(message));

try {
  const pdf = await printer.pdf(input, { outlineTags: ['h1', 'h2', 'h3'] });
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, pdf);
  console.log(`Saved ${output}`);
} finally {
  await browser.close();
}
