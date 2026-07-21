/**
 * mathematical-guides-transformers — child Worker for the mathematical-guides family hub.
 *
 * Reached ONLY through the hub's GUIDE_TRANSFORMERS service binding:
 *   mathematical.brandon-behring.dev/transformers/*  →  (hub _worker.js)  →  here.
 *
 * The hub forwards the full, unmodified /transformers/... path. Astro builds this
 * guide with base '/transformers/' but emits its assets at the dist ROOT
 * (dist/index.html, dist/_astro/…, dist/chapters/…) — there is no dist/transformers/
 * directory — so we strip the /transformers prefix before serving from the ASSETS
 * binding. Without the strip every request would 404.
 *
 * The child has no custom domain of its own; it must be deployed BEFORE the hub so
 * the hub's service binding resolves. Full runbook: docs/notes/cloudflare-deploy.md.
 */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    // '/transformers/…' → '/…'; bare '/transformers' → '/'. The (?=\/|$) lookahead
    // avoids clipping an unrelated path that merely starts with "transformers".
    url.pathname = url.pathname.replace(/^\/transformers(?=\/|$)/, '') || '/';
    return env.ASSETS.fetch(new Request(url, request));
  },
};
