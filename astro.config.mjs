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
  deploy: 'workers',
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
    '\\sg': '\\operatorname{sg}',
  },
});

export default await defineBookConfig({
  styles: [researchPortfolioStyle, mathematicalGuidesFamilyStyle],
  base: '/transformers/',
  title: 'Transformer Mathematics',
  description:
    'From recurrent networks and state space models through attention and transformers to hybrid architectures and vision-language models — a rigorous Definition–Theorem–Proof treatment.',
  // SSM semantic macros in \mathbf typography (consumer wins over the
  // scaffold-injected ssmMacros; \stepsize (Δ) and \scanop (⊕) inherit —
  // typography-neutral). See scaffold issue #177 for the ssmMacros export.
  katexMacros: {
    '\\statevec': '\\mathbf{h}',
    '\\statemat': '\\mathbf{A}',
    '\\inputmat': '\\mathbf{B}',
    '\\outputmat': '\\mathbf{C}',
    '\\feedmat': '\\mathbf{D}',
    '\\discA': '\\bar{\\mathbf{A}}',
    '\\discB': '\\bar{\\mathbf{B}}',
  },
});
