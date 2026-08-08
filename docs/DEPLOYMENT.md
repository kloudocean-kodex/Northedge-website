# NorthEdge production deployment

This repository is prepared for Cloudflare Pages with `public` as the build output and `functions/` as the Pages Functions directory.

## Required before custom-domain cutover

1. Create a Cloudflare D1 database, apply `schema/leads.sql`, and bind it as `LEADS_DB`.
2. Set `REQUIRE_LEAD_DB=true` in the production Pages environment.
3. Configure at least one delivery path:
   - Resend: `RESEND_API_KEY`, `LEAD_FROM_EMAIL`, and optionally `LEAD_TO_EMAIL`; and/or
   - CRM/webhook: `LEAD_WEBHOOK_URL` and optional `LEAD_WEBHOOK_TOKEN`.
4. Test every enquiry form on the Cloudflare preview and verify the corresponding D1 record and downstream delivery.
5. Check `/api/health` after bindings are configured. It reports configuration state only; it never exposes secrets.
6. Reverify all active property campaigns and prices against NorthEdge's authoritative listing source immediately before cutover.
7. Confirm all required Victorian Statements of Information are available for residential sale campaigns before publishing them live.
8. Confirm approved legal business name, ABN, estate-agent licence/OIEC display requirements, privacy terms, website terms and referral terms.
9. Confirm rights/permissions for the original NorthEdge logo, partner/platform marks, photography and reviews used on the site.
10. Build and approve an exact redirect map from the existing WordPress URLs. Do not guess legacy redirects.
11. Take a full backup of the current website/database and retain a rollback path before changing the custom domain.
12. Run Cloudflare-preview QA: navigation, phone, email, maps, social links, property pages, forms, keyboard navigation, responsive layouts, headers, 404s and redirects.
13. Submit the final sitemap and monitor Search Console after domain cutover.

## Cloudflare Pages settings

- Framework preset: None
- Build command: blank
- Build output directory: `public`
- Pages Functions: repository `functions/` directory

## Forms

Browser forms submit JSON to `/api/leads`. The endpoint validates the request, rate-limits obvious abuse, uses a honeypot, can store enquiries in D1, and can deliver through Resend and/or a CRM webhook. The UI does not display a success message unless the endpoint accepts the enquiry.

No real credentials belong in Git. Configure secrets and bindings in Cloudflare.
