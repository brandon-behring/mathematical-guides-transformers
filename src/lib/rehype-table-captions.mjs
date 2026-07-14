/**
 * Give every Markdown table an accessible caption derived from its nearest
 * preceding heading and its column headers. The caption is visually hidden;
 * it remains available to screen readers and tagged-PDF export.
 */

function textContent(node) {
  if (!node) return '';
  if (node.type === 'text') return node.value ?? '';
  if (node.type === 'element' && String(node.properties?.ariaHidden) === 'true') return '';
  return (node.children ?? []).map(textContent).join(' ');
}

function normalizedText(node) {
  return textContent(node).replace(/\s+/g, ' ').trim();
}

function firstHeaderLabels(table) {
  const thead = table.children?.find((child) => child.type === 'element' && child.tagName === 'thead');
  const row = thead?.children?.find((child) => child.type === 'element' && child.tagName === 'tr');
  return (row?.children ?? [])
    .filter((child) => child.type === 'element' && child.tagName === 'th')
    .map(normalizedText)
    .filter(Boolean);
}

export default function rehypeTableCaptions() {
  return (tree) => {
    let currentHeading = 'Reference';
    const namesSeen = new Map();

    function visit(node) {
      if (node.type === 'element' && /^h[1-6]$/.test(node.tagName)) {
        currentHeading = normalizedText(node) || currentHeading;
      }

      if (node.type === 'element' && node.tagName === 'table') {
        const existingCaption = node.children?.find(
          (child) => child.type === 'element' && child.tagName === 'caption',
        );
        let name = normalizedText(existingCaption);
        if (!existingCaption) {
          const headers = firstHeaderLabels(node);
          const baseName = headers.length > 0
            ? `${currentHeading}: ${headers.join(', ')}`
            : `${currentHeading} table`;
          const occurrence = (namesSeen.get(baseName) ?? 0) + 1;
          namesSeen.set(baseName, occurrence);
          name = occurrence === 1 ? baseName : `${baseName} (${occurrence})`;
          node.children ??= [];
          node.children.unshift({
            type: 'element',
            tagName: 'caption',
            properties: {
              className: ['table-caption-sr'],
              style: 'position:absolute;inline-size:1px;block-size:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0',
            },
            children: [{ type: 'text', value: name }],
          });
        }
        node.properties ??= {};
        node.properties.ariaLabel ??= name;
      }

      for (const child of node.children ?? []) visit(child);
    }

    visit(tree);
  };
}
