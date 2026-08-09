# NorthEdge VaultRE Media Sync

## Purpose

NorthEdge property photography must come from an authorised NorthEdge-controlled source. Third-party portal copies are evidence only and are not a production media source.

The repository includes `tools/vaultre_media_sync.py`, a **read-only** VaultRE discovery/downloader. It uses VaultRE's current published residential-sale endpoint and the ordered `GET /properties/{id}/photos` endpoint. It never writes to VaultRE.

## Secret handling

Required environment variables:

```text
VAULTRE_API_KEY
VAULTRE_ACCESS_TOKEN
```

Optional:

```text
VAULTRE_BASE_URL=https://ap-southeast-2.api.vaultre.com.au/api/v1.3
VAULTRE_MEDIA_CACHE=.vaultre-cache
```

Do not put real values in Git, chat, screenshots, documentation or build logs. The API key belongs to an approved VaultRE integrator; the access token is granted by the VaultRE client with explicit scopes.

## Safety model

The utility:

- calls only HTTP GET endpoints;
- discovers currently published/listing-or-conditional residential sale properties;
- requires exactly one property match for each approved NorthEdge address;
- refuses ambiguous or missing matches rather than guessing;
- retrieves photos in VaultRE's current order;
- excludes photos explicitly marked unpublished;
- does not send VaultRE API credentials to media/CDN URLs;
- stores downloads in `.vaultre-cache/`, which is git-ignored;
- records source URL, photo ID, caption/type, order, hash and byte size in a local audit JSON;
- never republishes downloaded masters automatically.

## Step 1 — discovery only

From a trusted local/Work environment where the two secrets are already securely available:

```bash
python tools/vaultre_media_sync.py
```

Expected output must identify exactly these four active campaign addresses:

- 27 Design Way, Kalkallo
- 31 Roseneath Way, Mickleham
- 6 Mathoura Road, Mickleham
- 7 Rulingia Road, Donnybrook

Review `.vaultre-cache/vaultre-media-audit.json` before downloading anything. If a campaign no longer appears or a match is ambiguous, stop and revalidate the website campaign state before publication.

## Step 2 — download authorised originals

After discovery is reviewed:

```bash
python tools/vaultre_media_sync.py --download
```

Originals are written beneath:

```text
.vaultre-cache/<property-slug>/originals/
```

These files are a private processing cache, not the website's served gallery.

## Step 3 — production derivatives

For each approved photo set:

1. preserve the VaultRE order and captions as source evidence;
2. verify photo type (`Photograph`, floorplan or equivalent) and published state;
3. reject unrelated, duplicate, corrupt or tiny assets;
4. preserve orientation and aspect ratio;
5. do not upscale low-resolution masters;
6. generate appropriately compressed responsive derivatives for the website;
7. place served derivatives under a property-specific local path such as:
   `public/assets/images/properties/<permanent-slug>/`;
8. use the best verified campaign image as the property social-preview image;
9. include the first 3–5 strongest images in the visible editorial first fold;
10. include the remaining authorised images as `.gallery-extra` items so the full accessible lightbox can traverse them without creating a thumbnail wall;
11. use VaultRE captions where reliable; otherwise use neutral address + sequence alt text rather than inventing a room type;
12. update `docs/PROPERTY_MEDIA_AUDIT.md` and `RELEASE_MANIFEST.json`.

## Step 4 — mandatory regression

After the final gallery assets are committed to `cutover/legacy-routing-preview` and Cloudflare serves that exact commit, rerun:

- every indexable and archival route;
- every image/srcset/full-lightbox asset decode;
- previous/next, keyboard arrows, Escape, focus trap/return and touch/mobile controls;
- all-route WCAG 2.2 AA automated and manual keyboard smoke;
- every public lead form and no-JavaScript fallback;
- D1 persistence and QA-row cleanup;
- console/network error checks;
- representative Lighthouse with Performance >=95, Accessibility 100, SEO 100 and Best Practices >=95.

## Current status

The property-gallery interface is ready and has passed Cloudflare browser regression, but the complete authorised VaultRE master sets have not yet been ingested. The live-domain cutover remains blocked on that media ingest plus the other documented production gates.
