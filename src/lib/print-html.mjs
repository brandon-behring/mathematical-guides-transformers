function safeId(value) {
  return String(value || 'chapter').replace(/[^a-zA-Z0-9_-]/g, '-');
}

/**
 * Scope Markdown-generated heading IDs inside the combined print document.
 * Semantic theorem/definition/figure IDs are deliberately left untouched so
 * the label registry remains stable; only h1–h6 IDs and their local references
 * are rewritten.
 */
export function namespacePrintHeadingIds(raw, prefix) {
  if (typeof raw !== 'string') return raw;

  const scopedPrefix = `${safeId(prefix)}--`;
  const headingIds = new Map();
  const headingRe = /<h([1-6])\b([^>]*?)\sid\s*=\s*(['"])([^'"]+)\3([^>]*)>/gi;

  let html = raw.replace(
    headingRe,
    (openTag, level, before, quote, id, after) => {
      const scoped = id.startsWith(scopedPrefix) ? id : `${scopedPrefix}${id}`;
      headingIds.set(id, scoped);
      return `<h${level}${before} id=${quote}${scoped}${quote}${after}>`;
    },
  );

  if (headingIds.size === 0) return html;

  html = html.replace(
    /(\shref\s*=\s*)(['"])#([^'"]+)\2/gi,
    (attribute, lead, quote, id) => {
      const scoped = headingIds.get(id);
      return scoped ? `${lead}${quote}#${scoped}${quote}` : attribute;
    },
  );

  html = html.replace(
    /(\saria-(?:labelledby|describedby)\s*=\s*)(['"])([^'"]*)\2/gi,
    (attribute, lead, quote, ids) => {
      const scoped = ids
        .split(/\s+/)
        .filter(Boolean)
        .map((id) => headingIds.get(id) ?? id)
        .join(' ');
      return `${lead}${quote}${scoped}${quote}`;
    },
  );

  return html;
}
