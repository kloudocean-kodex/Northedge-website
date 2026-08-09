# NorthEdge Property Media Audit

**Audit date:** 10 August 2026
**Release branch:** `cutover/legacy-routing-preview`
**Policy:** actual property media only. Production masters must come from NorthEdge-controlled VaultRE/agency sources and be mirrored locally. Portal-hosted copies are corroborating evidence only and must not be scraped or hotlinked.

| Property | Current representation evidence | Current campaign media evidence | Local distinct subjects | Production decision |
|---|---|---:|---:|---|
| 27 Design Way, Kalkallo | Current sale by Northedge Real Estate / Gurinder Sandhu | 20 current-listing images + 1 floorplan; broader property record contains 35 images | 3 | **Active. Full authorised VaultRE gallery required.** |
| 31 Roseneath Way, Mickleham | Current NorthEdge sale; Arsalan Basharat lead, Gurinder Sandhu supporting | 18 images + 1 floorplan in current agency listing evidence | 3 | **Active. Full authorised VaultRE gallery required.** |
| 6 Mathoura Road, Mickleham | Current NorthEdge sale / Gurinder Sandhu | 20 current-sale images + 1 floorplan; broader property record contains 34 images | 3; provenance of generic `mickleham-*` interiors must be confirmed | **Active. Full authorised VaultRE gallery required.** |
| 7 Rulingia Road, Donnybrook | Recent current-sale evidence identifies Northedge / Gurinder | 13 campaign photos + 1 floorplan | 2 | **Active pending cutover-day recheck. Full authorised VaultRE gallery required.** |
| 105 Tungsten Drive, Kalkallo | Fresher public evidence identifies another current selling agency | Not applicable to a current NorthEdge campaign | 3; generic Kalkallo interiors are unsafe to attribute | **Remove from current campaigns; retain `noindex` record without gallery.** |
| 6 Alisterus Road, Kalkallo | Current property data reports off-market; no reliable current NorthEdge sale evidence found | Not applicable | 1 | **Remove from current campaigns; retain `noindex` record without gallery.** |

## Authoritative production source

VaultRE's official API exposes `GET /properties/{id}/photos` for ordered property photography. VaultRE's technical guide requires API/feed integrators to download image files and host them locally rather than hotlinking. API access requires a client access token and API key; those credentials belong in an approved secret store and must never be committed to Git.

The existing NorthEdge WordPress listing pages could not be used as an unattended media source during this audit because the host returned a SiteGround CAPTCHA challenge to server-side requests. That is not permission to bypass the challenge or source media from third-party portals instead.

## Gallery acceptance standard

For each active campaign: ingest the ordered published VaultRE originals; preserve source ordering as evidence; art-direct a premium lead sequence; generate responsive local derivatives without upscaling; use the actual lead photo for social sharing; include authorised floorplan/aerial assets; use truthful scene-specific alt text; and verify every image, lightbox control, keyboard action and mobile crop on the Cloudflare preview.

**Current media readiness: NO-GO for live-domain cutover until authorised VaultRE masters for the four active campaigns are obtained and the complete galleries pass QA.**

## Gallery interface readiness

The production property template is now prepared for complete ordered galleries without changing the restrained first-fold composition. Full galleries will remain locally hosted and can extend beyond the visible lead grid using hidden gallery items that are available to the accessible lightbox. Property-specific social-preview images and neutral per-image labels are in place for the current local assets. This is interface readiness only; the authorised VaultRE master-ingest requirement remains open.
