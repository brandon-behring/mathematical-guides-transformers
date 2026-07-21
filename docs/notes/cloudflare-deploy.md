# Cloudflare deploy runbook — Transformer Mathematics

> **Status (2026-07-21): first-time bring-up.** Neither `mathematical-guides` (the hub) nor this repo
> has the two Cloudflare deploy secrets set yet, so the family has not been deployed through CI. The
> **code wiring in this repo is done** (branch `feat/cf-deploy`); what remains are the manual,
> Cloudflare-account-side actions **only you can do**, below. After they're complete, every push to
> `main` auto-deploys.

## What you're deploying

`Transformer Mathematics` is **not** a standalone site — it is the **`transformers` child** of the
`mathematical-guides` family hub, served at **`https://mathematical.brandon-behring.dev/transformers/`**,
never on a domain of its own.

```
        mathematical.brandon-behring.dev        ← custom domain, attached to the HUB
                       │
   hub Worker: brandon-behring-mathematical      (repo: mathematical-guides)
     _worker.js routes by path:
       /transformers/*  ──service binding──►  CHILD Worker
       everything else  ──►  hub's own static assets (landing, /methodology, /about)
                       │
                       ▼
   child Worker: brandon-behring-mathematical-transformers   (repo: THIS one)
     _worker.js strips /transformers → serves dist/ via the ASSETS binding
```

Three consequences drive every step below:
- **Order matters:** the child must deploy **before** the hub, or the hub's service binding won't resolve.
- **The custom domain attaches to the hub** — never to the child, never to the apex `brandon-behring.dev`.
- **Both repos deploy identically:** GitHub Actions → the `deploy-workflows` reusable workflow →
  `wrangler deploy`. Each needs the same two secrets.

---

## ✅ Steps only you can do

### 1 · Create a Cloudflare API token
Dashboard → **My Profile → API Tokens → Create Token → "Edit Cloudflare Workers"** (use the template) →
set **Account Resources** to your account → Continue → **Create Token** → copy it (shown once).
The template grants exactly what `wrangler deploy` needs (Workers Scripts : Edit + Account : Read); no
Pages permission is required — this is the Workers + Static Assets flow.

### 2 · Copy your Account ID
Dashboard → **Workers & Pages** → **Account ID** in the right sidebar (also in any zone's Overview).

### 3 · Set the two secrets on BOTH repos
`secrets: inherit` passes each repo's *own* Actions secrets, and this is a personal account (no shared
org secrets), so **each repo needs its own copy**. Both are currently unset (verified 2026-07-21):

```bash
# this repo — the transformers child
gh secret set CLOUDFLARE_API_TOKEN  --repo brandon-behring/mathematical-guides-transformers
gh secret set CLOUDFLARE_ACCOUNT_ID --repo brandon-behring/mathematical-guides-transformers

# the hub — also unset; it deploys the same way
gh secret set CLOUDFLARE_API_TOKEN  --repo brandon-behring/mathematical-guides
gh secret set CLOUDFLARE_ACCOUNT_ID --repo brandon-behring/mathematical-guides
```

Paste the value at each prompt (prefix the command with `!` to run it in this Claude session, or use
your own terminal). Confirm with
`gh secret list --repo brandon-behring/mathematical-guides-transformers` (both names should appear).

> **Do this before merging the wiring PR.** The deploy workflow runs on push to `main` and fails
> loudly (red ✗ on `main`) if the secrets are missing.

### 4 · Deploy in order — child, then hub
1. **Child first.** Merge the `feat/cf-deploy` PR in this repo. Its `Deploy` workflow creates the
   `brandon-behring-mathematical-transformers` Worker. It isn't reachable on its own yet (no domain) —
   that's expected; the hub will front it.
2. **Hub second.** In `mathematical-guides`, trigger its `Deploy` (push a watched path, or re-run its
   latest workflow run). This creates `brandon-behring-mathematical` and resolves the
   `GUIDE_TRANSFORMERS` binding to the child. Deploying the hub *before* the child exists fails with
   `service … not found` — so keep this order.

### 5 · Attach the custom domain to the HUB (one-time)
Dashboard → **Workers & Pages → `brandon-behring-mathematical` → Settings → Domains & Routes → Add →
Custom Domain** → `mathematical.brandon-behring.dev`. Cloudflare provisions DNS + the certificate.
Attach it to the **hub** only — never the child, never the apex.

### 6 · Verify
- `https://mathematical.brandon-behring.dev/transformers/` → the guide landing (a first hit may 404 for
  ~30 s while DNS propagates — refresh).
- Open a chapter (e.g. `…/transformers/chapters/00-…`): **inline SVG figures** and KaTeX math render.
- `…/transformers/print/` renders the print edition; `…/transformers/quick-reference/` loads by URL.
- CSP: `curl -sI https://mathematical.brandon-behring.dev/transformers/ | grep -i content-security-policy`
  returns the scaffold CSP; in DevTools, confirm the console shows no CSP blocks (all assets are
  same-origin, so it should be clean).

### 7 · Record it
Add an entry to the subdomain table in `~/Claude/brandon-behring.dev/README.md` (`#subdomain-convention`):
transformers is a **path under the hub** (`mathematical.brandon-behring.dev/transformers/`), not its own
subdomain.

---

## 🤖 What the wiring PR already did (no action needed)

Branch `feat/cf-deploy` in this repo:
- **`wrangler.toml`** — replaced the stale Pages stub with the Worker form: name
  `brandon-behring-mathematical-transformers` (must match the hub's service binding), `main = "_worker.js"`,
  `[assets] directory = "./dist"`, `binding = "ASSETS"`, `run_worker_first = true`.
- **`_worker.js`** — strips the `/transformers` prefix before serving from `ASSETS`. The hub forwards the
  full path and Astro emits assets at the `dist` root (there is no `dist/transformers/`), so the strip is
  what makes `/transformers/*` resolve.
- **`.github/workflows/deploy.yml`** — calls `brandon-behring/deploy-workflows/…/deploy-astro-worker.yml@v2.0.2`
  on push to `main`. No LaTeX is installed: the 31 figure SVGs are committed and `build:figures`
  graceful-skips missing tools; `validate` already runs via the build's `prebuild`.

The **hub repo is already wired** for transformers (`run_worker_first` + the `GUIDE_TRANSFORMERS`
binding) — it needs no code change, only its secrets (step 3) and its deploy (step 4.2).

---

## Troubleshooting

| Symptom | Cause → fix |
|---|---|
| Deploy fails: `CLOUDFLARE_API_TOKEN`/`ACCOUNT_ID` missing | Secret not set on that repo — step 3. |
| Hub deploy: `service "brandon-behring-mathematical-transformers" not found` | Child not deployed yet — deploy the child first (step 4.1). |
| `…/transformers/` 404s though the child Worker exists | Base-strip missing — confirm `wrangler.toml` has `main = "_worker.js"` + `run_worker_first = true` and `_worker.js` strips `/transformers`. |
| 404 on first load, fine after a refresh | DNS propagation (~30 s after the domain attach). |
| A resource is CSP-blocked in production | A new external script/font/origin was added; the CSP is prod-only, so CI won't catch it. Set `securityHeaders.contentSecurityPolicy` in `astro.config.mjs`, or ship a `public/_headers`. |
| Re-deploy the child | Re-run its latest **push** run in the Actions tab, or push a change to a watched path. The `workflow_dispatch` button no-ops — the reusable's deploy job gates on a `push` event. |

## References
- Hub routing: `mathematical-guides/wrangler.toml` + `_worker.js`.
- Reusable workflow: `brandon-behring/deploy-workflows` → `deploy-astro-worker.yml@v2.0.2` (+ its README).
- Scaffold recipe: `book-scaffold-astro/package/recipes/05-deploy-cloudflare.md` (Workers + Static
  Assets flow, the `dist/_headers` CSP, the LaTeX graceful-skip).
- Subdomain convention: `~/Claude/brandon-behring.dev/README.md#subdomain-convention`.
- Migration context: [`scaffold-v5-migration.md`](./scaffold-v5-migration.md) — the `#188` `_headers` note.
