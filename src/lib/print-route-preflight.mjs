const expectedTitle = '<title>Transformer Mathematics — Print Edition</title>';
const namedEntities = new Map([
  ['amp', '&'],
  ['apos', "'"],
  ['gt', '>'],
  ['lt', '<'],
  ['nbsp', ' '],
  ['quot', '"'],
]);

function decodeEntities(text) {
  return text.replace(/&(#x[0-9a-f]+|#\d+|[a-z][a-z0-9]+);/gi, (entity, key) => {
    if (key.startsWith('#x')) return String.fromCodePoint(Number.parseInt(key.slice(2), 16));
    if (key.startsWith('#')) return String.fromCodePoint(Number.parseInt(key.slice(1), 10));
    return namedEntities.get(key.toLowerCase()) ?? entity;
  });
}

function headingText(fragment) {
  return decodeEntities(fragment.replace(/<[^>]+>/g, ' '))
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Refuse to render an error page or a different route as the book PDF.
 * The print route declares its chapter count, which must agree with the
 * rendered ChapterHeader instances in the fetched HTML.
 */
export async function assertPrintRoute(input, fetchImpl = globalThis.fetch) {
  let response;
  try {
    response = await fetchImpl(input, { redirect: 'follow' });
  } catch (cause) {
    throw new Error(`Could not fetch PDF input ${input}`, { cause });
  }

  if (!response.ok) {
    throw new Error(`PDF input ${input} returned HTTP ${response.status}`);
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (!/^text\/html\b/i.test(contentType)) {
    throw new Error(`PDF input ${input} returned ${contentType || 'no content type'}, not HTML`);
  }

  const html = await response.text();
  const declaredCount = Number.parseInt(
    html.match(/\bdata-print-chapter-count="(\d+)"/)?.[1] ?? '',
    10,
  );
  const renderedCount = (
    html.match(/class="[^"]*\bchapter-header\b[^"]*"/g) ?? []
  ).length;
  const hasPrintContainer = /class="[^"]*\bprint-edition\b[^"]*"/.test(html);
  const headings = [...html.matchAll(/<h([1-6])\b[^>]*>([\s\S]*?)<\/h\1>/gi)]
    .map((match) => headingText(match[2]))
    .filter(Boolean);

  if (
    !html.includes(expectedTitle)
    || !hasPrintContainer
    || !Number.isInteger(declaredCount)
    || declaredCount < 1
    || renderedCount !== declaredCount
    || headings.length < declaredCount
  ) {
    throw new Error(
      `PDF input ${input} is not the complete Transformer Mathematics print route `
      + `(declared chapters: ${Number.isInteger(declaredCount) ? declaredCount : 'missing'}; `
      + `rendered chapter headers: ${renderedCount})`,
    );
  }

  return { chapterCount: declaredCount, headings };
}
