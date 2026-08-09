# NorthEdge Cutover R1 — QA Report

**Date:** 8 August 2026  
**Base release:** NorthEdge R3  
**Base SHA-256:** `7003c5932d9b96ed5113c93008578b990a50c490f8d5e985f587396372d3cb1c`

## Verified in this release

- 29 HTML routes scanned.
- 28 intended indexable routes represented in `sitemap.xml`.
- Zero broken local file references found by the static scanner.
- Zero broken internal anchors found by the static scanner.
- Zero duplicate HTML IDs found.
- Exactly one `h1` found on every HTML page.
- Titles and metadata/canonical architecture retained.
- 14 lead forms detected and mapped to the Cloudflare Pages `/api/leads` handler.
- Form controls are labelled or otherwise accessible to assistive technology under the static scan.
- `properties.json`, `site.webmanifest`, and `RELEASE_MANIFEST.json` parse as valid JSON.
- `assets/js/site.js`, `functions/api/leads.js`, and `functions/api/health.js` pass JavaScript syntax checks.
- No obvious committed API keys or production credentials found by the release secret-string scan.
- The demonstration-specific authored `brand-mark.svg`/`mark.svg` are not used in public HTML.
- Header, footer and browser-icon references use the supplied original NorthEdge logo assets.
- Old Netlify preview URLs are not referenced by public pages.

## Current campaign data correction pass

Before PR creation, the release candidate was cross-checked on 8 August 2026 against NorthEdge's current public sale feed and independent current listing evidence. The following consistency corrections were applied across listing cards, property data, property routes, canonicals, sitemap references and enquiry form identifiers:

- `105 Tungsten Drive, Kalkallo`: `$660,000 – $690,000`.
- `6 Alisterus Road, Kalkallo`: `$660,000 – $689,000`.
- Donnybrook campaign corrected from the incomplete/misspelled `Rullinga Road` label to `7 Rulingia Road, Donnybrook`; verified land size `392 m²`.
- Mickleham campaign corrected from `Mathoura Road` to `6 Mathoura Road, Mickleham`; verified land size `448 m²`.

These are point-in-time campaign facts. They must still be reverified against NorthEdge's authoritative listing source immediately before public-domain cutover. Statements of Information, inspection times and legal/compliance facts remain separate launch gates.

For that reason, property pages do not claim that a Statement of Information is currently available; they instruct users to confirm current document status with the agent before acting.

## Form behaviour

Public forms submit JSON to `/api/leads`. The browser does not clear a form or claim delivery unless the endpoint returns success. On failure, the entered data remains in the form and the user is directed to call NorthEdge.

The serverless handler includes:

- same-origin enforcement;
- payload-size checks;
- basic rate limiting;
- a honeypot field;
- allowed-form validation;
- input length limits and email validation;
- optional D1 database persistence;
- optional Resend email delivery;
- optional CRM/webhook delivery;
- no-store responses;
- failure-safe user messaging.

## Required Cloudflare-preview verification before domain cutover

The following cannot be honestly certified from a static local package alone and remain mandatory before changing the live domain:

1. Configure D1 and apply `schema/leads.sql`.
2. Bind D1 as `LEADS_DB` and set `REQUIRE_LEAD_DB=true` in production.
3. Configure and test at least one downstream delivery channel (Resend and/or approved CRM webhook).
4. Submit every public form on the Cloudflare preview and verify database persistence plus downstream delivery.
5. Run real-browser desktop/mobile/keyboard regression on the actual Cloudflare preview.
6. Reverify current property availability, prices, inspections and Statements of Information immediately before publication.
7. Obtain/record approval for final legal/privacy/referral wording and required licence/business disclosures.
8. Confirm rights/permissions for logo, campaign-system marks, photography and review material.
9. Capture the existing WordPress URL inventory and create the exact redirect map before cutover.
10. Back up the existing site/database and record rollback instructions.

**Cutover status:** Repository-ready; custom-domain cutover remains gated by the items above.

## Preview accessibility correction — 9 August 2026

Automated Chromium + axe testing on the Cloudflare branch preview identified insufficient contrast for the large italic brass title accents on the About page. The affected text used `#D9B97A` against `#F7F4EE` / `#EEE8DE`, producing 1.71:1 / 1.54:1 where WCAG requires 3:1 for large text. Light-surface About title accents now use the established darker NorthEdge brass `#815B25`. The complete route-level accessibility gate must pass again on the replacement preview before merge.
