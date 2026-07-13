/**
 * Render-side helpers for locally inlined figure SVGs.
 *
 * The book scaffold deliberately inlines SVGs so they inherit the site's
 * diagram theme.  A print route puts every figure in one document, however,
 * and converters such as pdftocairo reuse generic IDs (`glyph-0-0`, etc.) in
 * every asset.  SVG fragment references are document-scoped, so those IDs
 * must be namespaced per figure before the markup enters the page.
 */

const THEME_BLOCK_RE = /<style\b[^>]*\bdata-diagram-theme\b[^>]*>[\s\S]*?<\/style>/gi;

function safeId(value) {
  return String(value || 'figure').replace(/[^a-zA-Z0-9_-]/g, '-');
}

function escapeXml(value) {
  return String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function ensureSvgAttr(openTag, name, value) {
  const re = new RegExp(`\\s${name}=`, 'i');
  return re.test(openTag)
    ? openTag
    : openTag.replace(/<svg\b/i, `<svg ${name}="${value}"`);
}

function setSvgAttr(openTag, name, value) {
  const re = new RegExp(`\\s${name}=(['"])[\\s\\S]*?\\1`, 'i');
  return re.test(openTag)
    ? openTag.replace(re, ` ${name}="${value}"`)
    : openTag.replace(/<svg\b/i, `<svg ${name}="${value}"`);
}

function mergeSvgStyle(openTag, css) {
  const re = /\sstyle=(['"])([\s\S]*?)\1/i;
  const match = openTag.match(re);
  if (!match) return openTag.replace(/<svg\b/i, `<svg style="${css}"`);

  const existing = match[2].trim().replace(/;\s*$/, '');
  return openTag.replace(re, ` style="${existing ? `${existing};` : ''}${css}"`);
}

/** Return true when a local SVG can safely be read from public/. */
export function shouldInline(src) {
  return (
    typeof src === 'string' &&
    src.startsWith('/') &&
    !src.startsWith('//') &&
    /\.svg$/i.test(src)
  );
}

/**
 * Prefix every internal ID and every supported reference to it.
 *
 * References covered here are the forms emitted by the figure pipeline and
 * by standard SVG authoring tools: href/xlink:href fragments, url(#fragment)
 * paint/filter/clip references, and ARIA IDREF lists.
 */
export function namespaceSvgIds(raw, idBase = 'figure') {
  if (typeof raw !== 'string') return raw;

  const prefix = `${safeId(idBase)}--`;
  const idMap = new Map();

  let svg = raw.replace(/(^|[\s<])id\s*=\s*(['"])([^'"<>]+)\2/gi, (attribute, lead, quote, id) => {
    const namespaced = id.startsWith(prefix) ? id : `${prefix}${id}`;
    idMap.set(id, namespaced);
    return `${lead}id=${quote}${namespaced}${quote}`;
  });

  if (idMap.size === 0) return svg;

  svg = svg.replace(
    /(\s)(xlink:href|href)\s*=\s*(['"])#([^'"]+)\3/gi,
    (attribute, lead, name, quote, id) => {
      const namespaced = idMap.get(id);
      return namespaced ? `${lead}${name}=${quote}#${namespaced}${quote}` : attribute;
    },
  );

  svg = svg.replace(
    /url\(\s*(['"]?)#([^)'"\s]+)\1\s*\)/gi,
    (reference, quote, id) => {
      const namespaced = idMap.get(id);
      return namespaced ? `url(${quote}#${namespaced}${quote})` : reference;
    },
  );

  svg = svg.replace(
    /(\s)(aria-labelledby|aria-describedby)\s*=\s*(['"])([^'"]*)\3/gi,
    (attribute, lead, name, quote, ids) => {
      const namespaced = ids
        .split(/\s+/)
        .filter(Boolean)
        .map((id) => idMap.get(id) ?? id)
        .join(' ');
      return `${lead}${name}=${quote}${namespaced}${quote}`;
    },
  );

  return svg;
}

/** Prepare one trusted local SVG for responsive, accessible inline output. */
export function assembleSvg(raw, opts = {}) {
  const { caption, alt, desc, width = '100%', idBase = 'figure' } = opts;
  if (typeof raw !== 'string') return '';

  const withoutStandaloneTheme = raw.replace(THEME_BLOCK_RE, '');
  let svg = namespaceSvgIds(withoutStandaloneTheme, idBase);
  const openMatch = svg.match(/<svg\b[^>]*>/i);
  if (!openMatch) return svg;

  let openTag = openMatch[0];
  const body = svg
    .slice(openMatch.index + openTag.length)
    .replace(/<title\b[^>]*>[\s\S]*?<\/title>/gi, '')
    .replace(/<desc\b[^>]*>[\s\S]*?<\/desc>/gi, '');

  const titleText = caption ?? alt ?? '';
  const descText = desc ?? (alt && alt !== titleText ? alt : '');
  const id = safeId(idBase);
  const a11y = [];
  const labelledby = [];

  if (titleText) {
    a11y.push(`<title id="${id}-title">${escapeXml(titleText)}</title>`);
    labelledby.push(`${id}-title`);
  }
  if (descText) {
    a11y.push(`<desc id="${id}-desc">${escapeXml(descText)}</desc>`);
    labelledby.push(`${id}-desc`);
  }

  openTag = ensureSvgAttr(openTag, 'role', 'img');
  if (labelledby.length > 0) {
    openTag = setSvgAttr(openTag, 'aria-labelledby', labelledby.join(' '));
  }
  openTag = mergeSvgStyle(openTag, `width:${width};max-width:100%;height:auto`);

  return `${svg.slice(0, openMatch.index)}${openTag}${a11y.join('')}${body}`;
}
