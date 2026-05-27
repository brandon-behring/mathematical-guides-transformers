/**
 * src/content.config.ts — transformers sibling content collections.
 * Formal-series schema (style-guide-formal-v0.1): researchPortfolioChapterSchema
 * merged with the formal fields; chapters glob ./src/content/transformers.
 */
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { researchPortfolioChapterSchema } from '@brandon_m_behring/book-scaffold-astro';
import { frontmatterCollection } from '@brandon_m_behring/book-scaffold-astro/schemas';

const formalChapterExtensions = z.object({
  prerequisites: z.array(z.string()).default([]),
  notation_introduced: z.array(z.string()).default([]),
  theorems: z.array(z.string()).default([]),
  rigor_level: z.enum(['informal', 'rigorous', 'fully-formal']).default('rigorous'),
  los: z
    .array(z.object({ id: z.string(), statement: z.string() }))
    .default([]),
});

const chapters = defineCollection({
  loader: glob({
    pattern: ['**/*.{md,mdx}', '!**/_*'],
    base: './src/content/transformers',
  }),
  schema: researchPortfolioChapterSchema.merge(formalChapterExtensions),
});

const frontmatter = frontmatterCollection(
  z.object({
    slug: z.string(),
    title: z.string(),
    order: z.number(),
    description: z.string().optional(),
  })
);

export const collections = { chapters, frontmatter };
