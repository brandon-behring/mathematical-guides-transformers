import {
  PDFDict,
  PDFDocument,
  PDFHexString,
  PDFName,
} from 'pdf-lib';

function requireDict(context, value, label) {
  if (!value) throw new Error(`Tagged PDF has no ${label}`);
  const resolved = context.lookup(value);
  if (!(resolved instanceof PDFDict)) {
    throw new Error(`Tagged PDF ${label} is not a dictionary`);
  }
  return resolved;
}

function outlineItems(context, outlineRoot) {
  const items = [];
  const visited = new Set();

  function visitSiblings(first) {
    let current = first;
    while (current) {
      const key = String(current);
      if (visited.has(key)) throw new Error('Tagged PDF outline contains a cycle');
      visited.add(key);

      const item = requireDict(context, current, 'outline item');
      items.push(item);
      const child = item.get(PDFName.of('First'));
      if (child) visitSiblings(child);
      current = item.get(PDFName.of('Next'));
    }
  }

  const first = outlineRoot.get(PDFName.of('First'));
  if (first) visitSiblings(first);
  return items;
}

/**
 * Make Chrome's tagged PDF consumable by PDF 1.7 structure parsers and replace
 * layout-derived bookmark strings with the exact source-heading text.
 */
export async function finalizeTaggedPdf(bytes, headings) {
  const document = await PDFDocument.load(bytes, { updateMetadata: false });
  const { context, catalog } = document;

  const structureRoot = requireDict(
    context,
    catalog.get(PDFName.of('StructTreeRoot')),
    'StructTreeRoot',
  );
  const roleMapEntry = structureRoot.get(PDFName.of('RoleMap'));
  const roleMap = roleMapEntry
    ? requireDict(context, roleMapEntry, 'RoleMap')
    : context.obj({});
  // Strong and Em are standard in PDF 2.0, but Chrome currently emits a PDF
  // 1.4 file. Map them to the PDF 1.7 Span role so conforming readers retain
  // their nested text instead of rejecting the structure elements.
  roleMap.set(PDFName.of('Strong'), PDFName.of('Span'));
  roleMap.set(PDFName.of('Em'), PDFName.of('Span'));
  structureRoot.set(PDFName.of('RoleMap'), roleMap);

  const outlineRoot = requireDict(
    context,
    catalog.get(PDFName.of('Outlines')),
    'document outline',
  );
  const items = outlineItems(context, outlineRoot);
  if (items.length !== headings.length) {
    throw new Error(
      `Tagged PDF outline has ${items.length} item(s), but the print route has `
      + `${headings.length} heading(s)`,
    );
  }
  items.forEach((item, index) => {
    item.set(PDFName.of('Title'), PDFHexString.fromText(headings[index]));
  });

  return document.save({ useObjectStreams: false });
}
