# Generated review manifests

- `corpus.json` records chapter order, parts, labels, learning-objective IDs,
  proof markers, and explicit printed-number occurrences. Regenerate it with
  `npm run update:corpus`; CI verifies it with `npm run check:corpus`.
- `semantic-id-migration.json` is created by Track A's one-time ID migration
  and records every mapped or deliberately retired anchor, learning objective,
  exercise number, chapter path, and chapter slot reserved by that historical
  migration. A later chapter may occupy one of those slots; occupancy does not
  rewrite the one-time migration record. Verify it with
  `npm run check:id-migration`; the checker also rejects duplicate/dangling or
  legacy live IDs. It recognizes the frozen A3 target by the tracked
  `corpus.json` hash and exact A3 cardinalities. After later planned work changes
  that target, it keeps enforcing the chapter allocation, anchor and
  learning-objective mappings, reference resolution, and baseline floors while
  allowing semantic content to move or grow.

  The manifest schema is version 1 and has this shape:

  ```json
  {
    "schemaVersion": 1,
    "generatedBy": "scripts/semantic-id-migration.mjs",
    "baseline": {
      "commit": "<40-hex A2 merge commit>",
      "corpusManifestSha256": "<64-hex SHA-256>",
      "totals": {
        "chapters": 19,
        "anchors": 252,
        "learningObjectives": 86,
        "xrefs": 654,
        "frontmatterRegistryRefs": 172,
        "exercises": 101,
        "exerciseOccurrences": 105,
        "figures": 27,
        "labeledFigures": 26
      }
    },
    "checksums": {
      "chapterMapSha256": "<64-hex SHA-256>",
      "anchorMapSha256": "<64-hex SHA-256>",
      "learningObjectiveMapSha256": "<64-hex SHA-256>",
      "exerciseMapSha256": "<64-hex SHA-256>"
    },
    "chapters": [
      {
        "slug": "encoder-decoder-families",
        "title": "Encoder–Decoder Families",
        "part": 3,
        "oldChapter": 8,
        "newChapter": 9,
        "oldPath": "src/content/transformers/08-encoder-decoder-families.mdx",
        "newPath": "src/content/transformers/09-encoder-decoder-families.mdx",
        "status": "renumbered"
      }
    ],
    "reservedSlots": [
      { "chapter": 8, "title": "In-context Learning", "plannedTrack": "B2" }
    ],
    "anchors": {
      "mapped": [
        {
          "oldId": "def-tf4-attention",
          "newId": "def-attention",
          "ownerSlug": "attention",
          "oldPath": "src/content/transformers/04-attention.mdx",
          "newPath": "src/content/transformers/04-attention.mdx",
          "identity": false
        }
      ],
      "retired": []
    },
    "learningObjectives": {
      "mapped": [
        {
          "oldId": "TF-4.1",
          "newId": "lo-scaled-dot-product-attention",
          "ownerSlug": "attention",
          "oldPath": "src/content/transformers/04-attention.mdx",
          "newPath": "src/content/transformers/04-attention.mdx"
        }
      ],
      "retired": []
    },
    "exercises": [
      {
        "ownerSlug": "encoder-decoder-families",
        "oldPath": "src/content/transformers/08-encoder-decoder-families.mdx",
        "newPath": "src/content/transformers/09-encoder-decoder-families.mdx",
        "ordinal": 1,
        "oldLabel": "Exercise 8.1",
        "newLabel": "Exercise 9.1",
        "occurrences": 1
      }
    ],
    "unanchoredComponents": [
      {
        "kind": "Figure",
        "ownerSlug": "hybrid-architectures",
        "oldPath": "src/content/transformers/14-hybrid-architectures.mdx",
        "newPath": "src/content/transformers/19-hybrid-architectures.mdx",
        "src": "/figures/hybrid-interleave.svg",
        "decision": "preserved-unlabeled",
        "reason": "<why it remains unlabeled>"
      }
    ]
  }
  ```

  The checksums are frozen review metadata from the atomic migration. The
  checker recomputes the anchor and learning-objective projections, pins all
  four values, and independently validates every chapter and exercise row. It
  also pins sorted-record source, target, and pair inventories, cardinalities,
  the two collision overrides, and the sole unlabeled-figure exception. Frozen
  mode additionally pins every XRef and frontmatter-registry occurrence by
  target, owner path, and ordinal, and requires every exercise row at its A3
  label and owner. Extension mode deliberately relaxes only that exercise
  location contract so A5/A6 and the reserved chapters may move or renumber
  exercises; headings must remain well-formed, unique, chapter-correct, and all
  printed exercise references must resolve, with the A3 count floors preserved.
  The preserved unlabeled Figure may later be labeled or relocated, but no new
  unlabeled exception may be introduced. Legacy-ID scans cover chapters, tests,
  figure sources, active plans, `.claude/skills`, and `.gitleaks.toml`.

These files are tracked review surfaces. Generated `src/data/*.json` remains
ignored and is not a substitute for them.
