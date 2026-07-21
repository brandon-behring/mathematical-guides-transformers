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
import rehypeTableCaptions from './src/lib/rehype-table-captions.mjs';

const guidePolishStyles = {
  name: 'guide-polish-styles',
  hooks: {
    'astro:config:setup': ({ injectScript }) => {
      injectScript('page-ssr', "import '/src/styles/apparatus.css';");
    },
  },
};

const mathematicalGuidesFamilyStyle = defineStyle({
  name: 'mathematical-guides-family',
  site: 'https://mathematical.brandon-behring.dev',
  routes: { frontmatter: { enabled: true, prefix: '' } },
  // \R \Z \N \E come from the scaffold-injected ssmMacros base (identical
  // definitions; exported publicly since book-scaffold-astro#177), so only
  // the family additions remain here. \norm deliberately overrides the
  // scaffold's non-sizing variant with \left/\right auto-sizing.
  katexMacros: {
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
  extraIntegrations: [guidePolishStyles],
  markdown: { rehypePlugins: [rehypeTableCaptions] },
  routes: { glossary: true, print: false },
  // v5 restricts apparatusRoutes to a fixed vocabulary (no custom 'quick-reference' key;
  // its 'references' slot is the bibliography that <Cite> links to). The consumer-owned
  // /quick-reference/ page still builds via Astro file routing and stays in the print
  // edition; only its auto sidebar link is dropped. Nav-discoverability handling: see issue #26.
  apparatusRoutes: ['glossary'],
  base: '/transformers/',
  title: 'Transformer Mathematics',
  subtitle: 'A formal guide to sequence models',
  description:
    'From recurrent networks and state-space models through attention and transformers to hybrid architectures and vision–language models — a rigorous Definition–Theorem–Proof treatment.',
  // SSM semantic macros in \mathbf typography (consumer wins over the
  // scaffold-injected ssmMacros). The consumer also pins \scanop to the guide's
  // documented bullet glyph; \stepsize (Δ) remains typography-neutral. See
  // scaffold issue #177 for the ssmMacros export.
  katexMacros: {
    '\\statevec': '\\mathbf{h}',
    '\\statemat': '\\mathbf{A}',
    '\\inputmat': '\\mathbf{B}',
    '\\outputmat': '\\mathbf{C}',
    '\\feedmat': '\\mathbf{D}',
    '\\discA': '\\bar{\\mathbf{A}}',
    '\\discB': '\\bar{\\mathbf{B}}',
    '\\scanop': '\\bullet',
  },
});
