# NorthEdge Real Estate website

Client-approved NorthEdge website prepared from the canonical R3 demonstration for production cutover.

## Release

- Release: **NorthEdge Cutover R1**
- Prepared: **8 August 2026**
- Canonical base: `NORTHEDGE_CLIENT_DEMO_ULTIMATE_R3_FINAL.zip`
- Verified base SHA-256: `7003c5932d9b96ed5113c93008578b990a50c490f8d5e985f587396372d3cb1c`
- Branding: the client's supplied original NorthEdge logo is used throughout the public site.

## Repository layout

- `public/` — deployable website
- `functions/api/` — Cloudflare Pages lead and health endpoints
- `schema/leads.sql` — optional/required production D1 lead-store schema depending on environment settings
- `docs/DEPLOYMENT.md` — production deployment and cutover gates
- `docs/SOURCE_PROVENANCE.md` — release/source provenance
- `tools/serve.py` — local static preview helper

## Cloudflare Pages

Use Git integration with:

- Framework preset: **None**
- Build command: **blank**
- Build output directory: **`public`**
- Pages Functions directory: repository **`functions/`** (auto-detected)

The production lead pipeline must be configured and tested before the custom domain is moved. See `docs/DEPLOYMENT.md`.

## Local preview

```bash
python tools/serve.py
```

Static local preview cannot execute Cloudflare Pages Functions, so form delivery must be tested on a Cloudflare preview deployment.

## Security

No credentials, API keys or production secrets belong in this repository. Use Cloudflare bindings and secrets.
