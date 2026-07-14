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

function matchingAsideEnd(html, openIndex) {
  const asideTag = /<\/?aside\b[^>]*>/gi;
  asideTag.lastIndex = openIndex;
  let depth = 0;
  let match;

  while ((match = asideTag.exec(html)) !== null) {
    depth += /^<\/aside\b/i.test(match[0]) ? -1 : 1;
    if (depth === 0) return asideTag.lastIndex;
  }

  return -1;
}

function exerciseGroupRanges(html) {
  const divTag = /<\/?div\b[^>]*>/gi;
  const groupClass = /\bclass\s*=\s*(['"])[^'"]*\bexercise-solution-pair\b[^'"]*\1/i;
  const stack = [];
  const ranges = [];
  let match;

  while ((match = divTag.exec(html)) !== null) {
    if (/^<\/div\b/i.test(match[0])) {
      const opening = stack.pop();
      if (opening?.group) ranges.push({ start: opening.index, end: divTag.lastIndex });
    } else if (!/\/\s*>$/.test(match[0])) {
      stack.push({ index: match.index, group: groupClass.test(match[0]) });
    }
  }

  return ranges;
}

/**
 * Keep each rendered exercise prompt with its collapsed SolutionBox in print.
 * A prompt can contain several sibling nodes (for example, display math), so
 * adjacent-sibling break rules alone cannot reliably describe the pair to
 * Paged.js. This print-only transform supplies the explicit atomic wrapper.
 */
export function groupPrintExerciseSolutions(raw) {
  if (typeof raw !== 'string') return raw;

  const exerciseStart = /<p\b[^>]*>\s*<strong\b[^>]*>\s*Exercise\b/gi;
  const solutionAside = /<aside\b[^>]*\bclass\s*=\s*(['"])[^'"]*\bsolution-box\b[^'"]*\1[^>]*>/gi;
  const starts = [...raw.matchAll(exerciseStart)].map((match) => match.index);
  const existingGroups = exerciseGroupRanges(raw);
  const insertions = [];
  let startCursor = 0;
  let pairEnd = 0;
  let solution;

  while ((solution = solutionAside.exec(raw)) !== null) {
    while (startCursor + 1 < starts.length && starts[startCursor + 1] < solution.index) {
      startCursor += 1;
    }

    const start = starts[startCursor];
    const end = matchingAsideEnd(raw, solution.index);
    if (start === undefined || start < pairEnd || end < 0) {
      throw new Error('Could not pair a print exercise prompt with its SolutionBox');
    }

    const alreadyGrouped = existingGroups.some(
      (group) => group.start < start && group.end >= end,
    );
    if (!alreadyGrouped) {
      insertions.push(
        { index: start, text: '<div class="exercise-solution-pair">' },
        { index: end, text: '</div>' },
      );
    }
    pairEnd = end;
  }

  let html = raw;
  for (const insertion of insertions.sort((a, b) => b.index - a.index)) {
    html = `${html.slice(0, insertion.index)}${insertion.text}${html.slice(insertion.index)}`;
  }
  return html;
}
