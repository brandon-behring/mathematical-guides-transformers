# Generated review manifests

- `corpus.json` records chapter order, parts, labels, learning-objective IDs,
  proof markers, and explicit printed-number occurrences. Regenerate it with
  `npm run update:corpus`; CI verifies it with `npm run check:corpus`.
- `semantic-id-migration.json` is created by Track A's one-time ID migration
  and records every mapped or deliberately retired anchor.

These files are tracked review surfaces. Generated `src/data/*.json` remains
ignored and is not a substitute for them.
