# NorthEdge Current State

**Date:** 10 August 2026  
**Stage:** Cloudflare cutover readiness — pre-merge, pre-domain cutover  
**Repository:** `kloudocean-kodex/Northedge-website`  
**Base branch:** `main`  
**Working branch:** `cutover/legacy-routing-preview`  
**Pull request:** #2 — draft, open, unmerged  
**Cloudflare branch preview:** `https://cutover-legacy-routing-previ.northedge-website.pages.dev`

## Immutable repository state before this checkpoint

- `main`: `e68b7070dd3117938f08d90f9d77bce76ac52302`
- reviewed `main` tree: `b5a8b9d4fab0b5812e0679f566511a1f20c44e02`
- candidate head before checkpoint docs: `ae9767a4b2a8d29a2a4fa366b1c739b6f2297f80`
- candidate tree before checkpoint docs: `98d2eb632350290908383a58901207c6715d4f0c`
- deployed/browser-tested `public/` subtree: `1732a4ffcc54f30764df35a595afe444d6562422`
- release manifest count before checkpoint docs: 183 files

The checkpoint-document commit may advance the overall branch SHA/tree and manifest count, but it must not change the `public/` subtree above.

## Verified complete on the branch preview

- Cloudflare Git-connected Pages branch preview.
- Pages Functions and legacy WordPress query-route handling.
- D1 `northedge-leads`, binding `LEADS_DB`, `REQUIRE_LEAD_DB=true`.
- D1 `leads` and `lead_rate_limits` schema.
- original 15 marked QA rows preserved; temporary later batches cleaned.
- clean Cloudflare extensionless URLs/canonicals/sitemap with no known redirect loop.
- deep 404 assets/navigation.
- mobile closed-menu keyboard focus protection.
- homepage Rent search routing.
- database-first lead endpoint and no-JavaScript POST fallback.
- referral consent persistence/validation.
- D1-backed abuse rate limiting.
- truthful stored-versus-delivered response semantics.
- API security headers, health schema/database checks and PII-safe operational logging.
- verified legal entity/ABN published; no invented estate-agent licence number.
- conservative Statement of Information wording pending authoritative documents.
- four current NorthEdge sale campaigns represented; two stale/non-current records removed from current-campaign surfaces and retained only as conservative `noindex` permanent records.
- 26 sitemap routes plus two archival routes passed the post-truth browser/accessibility regression.
- four active property-gallery routes passed production gallery interaction QA: thumbnail/full image decode, previous/next, ArrowLeft/ArrowRight, Escape, focus return, counter/caption and mobile controls.
- serious/critical automated axe failures: zero in the latest 28-route gallery regression.
- page errors: zero in that regression.

## Current property truth

Represented as active pending final cutover-day verification:

1. 27 Design Way, Kalkallo
2. 31 Roseneath Way, Mickleham
3. 6 Mathoura Road, Mickleham
4. 7 Rulingia Road, Donnybrook

Not represented as current NorthEdge campaigns:

- 105 Tungsten Drive, Kalkallo — permanent `noindex` record retained without active gallery.
- 6 Alisterus Road, Kalkallo — permanent `noindex` record retained without active gallery.

## Property-media state

The gallery **interface** is production-capable but the **media sets are not production-complete**.

The repository contains `docs/PROPERTY_MEDIA_AUDIT.md`, `docs/VAULTRE_MEDIA_SYNC.md` and `tools/vaultre_media_sync.py`. Full authorised originals for the four active campaigns must be obtained from NorthEdge-controlled VaultRE/agency sources. Third-party portal copies must not be scraped, hotlinked or used as the production source.

The VaultRE sync tool is GET-only, secret-environment-only, fails closed on ambiguous property matches, writes masters only to git-ignored `.vaultre-cache/`, and does not publish anything automatically.

## Remaining live-cutover blockers

1. Authorised complete VaultRE galleries for the four active campaigns, including approved floorplans/aerials as applicable, mirrored locally and fully QA'd.
2. Current campaign facts, inspection status and required Statements of Information reverified immediately before launch.
3. Real downstream lead delivery (approved email/CRM/webhook) configured and verified with auditable failure/retry handling. D1 persistence alone remains the safety record, not the complete operational workflow.
4. Estate-agent licence/display particulars verified from an authoritative source; do not invent.
5. Final owner/legal approval of Privacy, Terms and referral wording.
6. Image/review/partner/logo permissions confirmed.
7. Current WordPress/database backup, final legacy URL inventory and tested rollback plan.
8. Final post-media regression: all routes/assets/galleries, all 14 UI forms + no-JS fallback, D1 evidence/cleanup, WCAG 2.2 AA, console/network, desktop/tablet/mobile and Lighthouse targets.
9. PR #2 merge only after those gates; custom-domain/DNS cutover requires a separate explicit approval after `main` production verification.

## Explicitly prohibited at this state

- do not merge PR #2 without explicit approval after final gates;
- do not change `main` directly;
- do not attach or route `northedgerealestate.com.au`;
- do not change DNS, nameservers or MX/email DNS;
- do not remove or modify the current WordPress live site;
- do not commit or paste VaultRE, email, webhook or Cloudflare secret values.
