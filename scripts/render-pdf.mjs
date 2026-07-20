#!/usr/bin/env node

/**
 * Render the print route with a protocol timeout large enough for the complete
 * book. pagedjs-cli exposes a page timeout, but its default Puppeteer launch
 * still caps a single CDP call at three minutes; the 24-chapter print route can
 * legitimately spend longer than that in Paged.js layout.
 */
import { existsSync } from 'node:fs';
import { mkdir, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import Printer from 'pagedjs-cli';
import puppeteer from 'puppeteer';
import { assertPrintRoute } from '../src/lib/print-route-preflight.mjs';
import { finalizeTaggedPdf } from '../src/lib/tagged-pdf.mjs';

const [
  input = 'http://localhost:4321/transformers/print/',
  output = 'dist-pdf/book.pdf',
] = process.argv.slice(2);

const timeout = Number.parseInt(process.env.PDF_RENDER_TIMEOUT_MS ?? '900000', 10);
if (!Number.isFinite(timeout) || timeout <= 0) {
  throw new Error('PDF_RENDER_TIMEOUT_MS must be a positive integer');
}

const executablePath = process.env.PDF_CHROME_PATH
  ?? (existsSync('/usr/bin/google-chrome') ? '/usr/bin/google-chrome' : puppeteer.executablePath());

const { headings } = await assertPrintRoute(input);

const browser = await puppeteer.launch({
  executablePath,
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
  const page = await printer.render(input);
  const client = await page.target().createCDPSession();
  const result = await client.send('Page.printToPDF', {
    printBackground: true,
    displayHeaderFooter: false,
    preferCSSPageSize: true,
    marginTop: 0,
    marginRight: 0,
    marginBottom: 0,
    marginLeft: 0,
    generateTaggedPDF: true,
    generateDocumentOutline: true,
  });
  await client.detach();
  const chromePdf = Buffer.from(result.data, 'base64');
  const pdf = Buffer.from(await finalizeTaggedPdf(chromePdf, headings));
  if (!pdf.includes(Buffer.from('/StructTreeRoot'))) {
    throw new Error(
      `Chromium at ${executablePath} did not emit a tagged PDF; set PDF_CHROME_PATH to a current Chrome build`,
    );
  }
  await mkdir(dirname(output), { recursive: true });
  await writeFile(output, pdf);
  console.log(`Saved ${output}`);
} finally {
  await browser.close();
}
