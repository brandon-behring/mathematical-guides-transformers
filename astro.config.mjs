// @ts-check
/**
 * astro.config.mjs — mathematical-guides-transformers sibling.
 * Deploys to /transformers/ (subroute of the family hub).
 *
 * Inline-duplicates mathematicalGuidesFamilyStyle from
 * ~/mathematical-guides/shared/styles/mathematical-guides-family.ts (canonical).
 */
import {
  defineBookConfig,
  researchPortfolioStyle,
  defineStyle,
} from '@brandon_m_behring/book-scaffold-astro';

const mathematicalGuidesFamilyStyle = defineStyle({
  name: 'mathematical-guides-family',
  site: 'https://mathematical.brandon-behring.dev',
  routes: { frontmatter: { enabled: true, prefix: '' } },
  deploy: 'pages',
  katexMacros: {
    '\\R': '\\mathbb{R}',
    '\\Z': '\\mathbb{Z}',
    '\\N': '\\mathbb{N}',
    '\\E': '\\mathbb{E}',
    '\\Var': '\\operatorname{Var}',
    '\\norm': '\\left\\lVert #1 \\right\\rVert',
    '\\inner': '\\left\\langle #1, #2 \\right\\rangle',
    '\\defeq': '\\doteq',
    '\\softmax': '\\operatorname{softmax}',
    '\\Emb': '\\operatorname{Emb}',
  },
});

export default await defineBookConfig({
  styles: [researchPortfolioStyle, mathematicalGuidesFamilyStyle],
  base: '/transformers/',
});
