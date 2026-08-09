#!/usr/bin/env python3
"""Read-only VaultRE campaign media discovery/downloader for NorthEdge.

Secrets are read only from environment variables. This utility never writes to
VaultRE and never prints secret values. Downloads go to the git-ignored
.vaultre-cache/ directory for review/derivative generation before publication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = os.environ.get("VAULTRE_BASE_URL", "https://ap-southeast-2.api.vaultre.com.au/api/v1.3").rstrip("/")
CACHE = Path(os.environ.get("VAULTRE_MEDIA_CACHE", ".vaultre-cache"))
TARGETS = {
    "27-design-way-kalkallo": ("27 Design Way", "Kalkallo"),
    "31-roseneath-way-mickleham": ("31 Roseneath Way", "Mickleham"),
    "6-mathoura-road-mickleham": ("6 Mathoura Road", "Mickleham"),
    "7-rulingia-road-donnybrook": ("7 Rulingia Road", "Donnybrook"),
}


def die(message: str) -> "NoReturn":
    raise SystemExit(message)


def credentials() -> tuple[str, str]:
    api_key = os.environ.get("VAULTRE_API_KEY", "").strip()
    token = os.environ.get("VAULTRE_ACCESS_TOKEN", "").strip()
    if not api_key or not token:
        die("VAULTRE_API_KEY and VAULTRE_ACCESS_TOKEN must be supplied through an approved secret environment.")
    return api_key, token


def api_get(path: str) -> Any:
    api_key, token = credentials()
    request = urllib.request.Request(
        BASE + path,
        headers={
            "Accept": "application/json",
            "X-Api-Key": api_key,
            "Authorization": f"Bearer {token}",
            "User-Agent": "ProddyG-NorthEdge-VaultRE-Media-Sync/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            die(f"VaultRE GET {path} returned HTTP {response.status}.")
        return json.load(response)


def unwrap_list(payload: Any, label: str) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if isinstance(payload, dict):
        for key in ("items", "results", "data", "properties", "photos"):
            value = payload.get(key)
            if isinstance(value, list):
                return [x for x in value if isinstance(x, dict)]
    die(f"Unexpected VaultRE {label} response shape; refusing to guess.")


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def scalar_blob(value: Any) -> str:
    parts: list[str] = []
    def walk(node: Any) -> None:
        if isinstance(node, dict):
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)
        elif isinstance(node, (str, int, float)) and not isinstance(node, bool):
            parts.append(str(node))
    walk(value)
    return norm(" ".join(parts))


def find_property(items: list[dict[str, Any]], street: str, suburb: str) -> dict[str, Any]:
    street_n, suburb_n = norm(street), norm(suburb)
    matches = [item for item in items if street_n in scalar_blob(item) and suburb_n in scalar_blob(item)]
    if len(matches) != 1:
        ids = [m.get("id") for m in matches]
        die(f"Expected exactly one VaultRE match for {street}, {suburb}; found {len(matches)} ({ids}).")
    if not matches[0].get("id"):
        die(f"VaultRE property for {street}, {suburb} has no property id; refusing to continue.")
    return matches[0]


def extension(url: str, content_type: str | None = None) -> str:
    ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
        return ".jpg" if ext == ".jpeg" else ext
    guessed = mimetypes.guess_extension((content_type or "").split(";", 1)[0].strip())
    return ".jpg" if guessed in {".jpe", ".jpeg"} else (guessed or ".jpg")


def download_photo(url: str, destination_stem: Path) -> tuple[Path, str, int]:
    # Never forward VaultRE API credentials to a media/CDN URL.
    request = urllib.request.Request(url, headers={"User-Agent": "ProddyG-NorthEdge-Media-Mirror/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        if response.status != 200:
            die(f"Photo download returned HTTP {response.status}: {url}")
        content_type = response.headers.get("content-type", "")
        body = response.read()
    if not body:
        die(f"Downloaded zero bytes for {url}")
    path = destination_stem.with_suffix(extension(url, content_type))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)
    return path, hashlib.sha256(body).hexdigest(), len(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="Discover or download NorthEdge's authorised VaultRE property photo sets.")
    parser.add_argument("--download", action="store_true", help="Download published originals to .vaultre-cache after discovery.")
    parser.add_argument("--output", default=str(CACHE / "vaultre-media-audit.json"), help="Audit JSON output path.")
    args = parser.parse_args()

    # Official published/current residential-sale endpoint. This tool remains GET-only.
    payload = api_get("/properties/residential/sale?published=true&status=listingOrConditional")
    properties = unwrap_list(payload, "property-list")
    audit: dict[str, Any] = {
        "source": "VaultRE core API",
        "base": BASE,
        "mode": "download" if args.download else "discovery-only",
        "properties": {},
    }

    for slug, (street, suburb) in TARGETS.items():
        prop = find_property(properties, street, suburb)
        property_id = prop["id"]
        photo_payload = api_get(f"/properties/{urllib.parse.quote(str(property_id), safe='')}/photos")
        photos = unwrap_list(photo_payload, "photo-list")
        published = [p for p in photos if p.get("published") is not False and p.get("url")]
        if not published:
            die(f"No published VaultRE photos found for {street}, {suburb} (property id {property_id}).")

        rows: list[dict[str, Any]] = []
        for index, photo in enumerate(published, 1):
            row = {
                "order": index,
                "photoId": photo.get("id"),
                "url": photo.get("url"),
                "caption": photo.get("caption") or "",
                "type": photo.get("type") or "",
                "published": photo.get("published", True),
                "modified": photo.get("modified") or photo.get("modtime") or None,
            }
            if args.download:
                photo_id = str(photo.get("id") or index)
                stem = CACHE / slug / "originals" / f"{index:03d}-{photo_id}"
                path, sha, size = download_photo(str(photo["url"]), stem)
                row.update({"localPath": path.as_posix(), "sha256": sha, "bytes": size})
            rows.append(row)

        audit["properties"][slug] = {
            "propertyId": property_id,
            "address": f"{street}, {suburb}",
            "photoCount": len(rows),
            "photos": rows,
        }
        print(f"{street}, {suburb}: VaultRE property {property_id}; {len(rows)} published photos")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Audit written to {output}. Secrets were not written to output.")
    if not args.download:
        print("Discovery only. Re-run with --download after reviewing property matches and photo counts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
