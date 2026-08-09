from pathlib import Path
import json,re,xml.etree.ElementTree as ET,hashlib

root=Path(__file__).resolve().parents[1]
pub=root/'public'
stale={
    '105 Tungsten Drive':'property-105-tungsten-drive-kalkallo',
    '6 Alisterus Road':'property-6-alisterus-road-kalkallo',
}

# Remove stale current-campaign cards from every public HTML surface.
for p in pub.glob('*.html'):
    s=p.read_text(encoding='utf-8'); old=s
    for address in stale:
        pos=0
        while True:
            i=s.find(address,pos)
            if i<0: break
            a=s.rfind('<article class="property-card',0,i)
            b=s.find('</article>',i)
            if a>=0 and b>=i:
                s=s[:a]+s[b+len('</article>'):]
                pos=max(0,a)
            else:
                pos=i+len(address)
    if p.name=='index.html':
        s=s.replace('Six homes.<br/><em>One northern postcode.</em>','Four current homes.<br/><em>Across Melbourne’s north.</em>')
        s=s.replace('Six different buyer stories, each presented with price, estate, scale and campaign detail visible before the first enquiry.','Four current campaigns, each presented with price, estate, scale and campaign detail visible before the first enquiry.')
    if s!=old:p.write_text(s,encoding='utf-8')

# Structured data: retain permanent records but make active/archival state explicit.
dp=pub/'data/properties.json'; data=json.loads(dp.read_text(encoding='utf-8'))
for prop in data:
    prop['status']='active';prop['mediaStatus']='awaiting-authoritative-vaultre-gallery'
    if prop['slug'] in stale.values():
        prop['status']='archived';prop['mediaStatus']='not-published-as-current-campaign';prop['featured']=False
        prop['price']='—';prop['note']='No current NorthEdge campaign';prop['gallery']=[];prop['highlights']=[]
        prop['description']=f"This permanent property record is retained for URL continuity. NorthEdge is not presenting {prop['address']}, {prop['suburb']} as a current NorthEdge campaign. Confirm current campaign status and representation from an authoritative listing source before acting."
dp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Remove archival property records from sitemap, keeping the physical permanent URLs available.
sm=pub/'sitemap.xml';tree=ET.parse(sm);rt=tree.getroot();ns={'s':'http://www.sitemaps.org/schemas/sitemap/0.9'}
for node in list(rt):
    loc=node.find('s:loc',ns)
    if loc is not None and any(loc.text.rstrip('/').endswith('/'+slug) for slug in stale.values()):rt.remove(node)
ET.register_namespace('', 'http://www.sitemaps.org/schemas/sitemap/0.9');tree.write(sm,encoding='utf-8',xml_declaration=True)

archive={
 'property-105-tungsten-drive-kalkallo':('105 Tungsten Drive','Kalkallo','Cloverton Estate','$660,000 – $690,000'),
 'property-6-alisterus-road-kalkallo':('6 Alisterus Road','Kalkallo','Cloverton Estate','$660,000 – $689,000'),
}
for slug,(address,suburb,estate,oldprice) in archive.items():
    p=pub/(slug+'.html');s=p.read_text(encoding='utf-8')
    if 'name="robots"' not in s:s=s.replace('<meta content="#F7F4EE" name="theme-color"/>','<meta content="#F7F4EE" name="theme-color"/><meta content="noindex,follow" name="robots"/>',1)
    s=re.sub(r'<meta content="[^"]*" name="description"/>',f'<meta content="Permanent property record for {address}, {suburb}. This address is not presented as a current NorthEdge campaign." name="description"/>',s,count=1)
    s=re.sub(r'<meta content="[^"]*" property="og:description"/>',f'<meta content="Permanent property record for {address}, {suburb}. Not a current NorthEdge campaign." property="og:description"/>',s,count=1)
    s=re.sub(r'<section class="property-gallery">.*?</section>','<section class="property-gallery property-gallery-archived"><div class="shell"><div class="property-archive-notice"><p class="eyebrow">Property record</p><h2>Campaign photography withheld.</h2><p>NorthEdge is not presenting this address as a current campaign. This permanent route remains available for URL continuity without implying current representation or media status.</p></div></div></section>',s,count=1,flags=re.S)
    s=s.replace(f'<p class="eyebrow">For sale · {estate}</p>',f'<p class="eyebrow">Property record · {estate}</p>',1)
    s=re.sub(r'<div class="property-head-price"><strong>.*?</strong><span>.*?</span></div>','<div class="property-head-price"><strong>Not a current NorthEdge campaign</strong><span>Permanent property URL retained</span></div>',s,count=1,flags=re.S)
    marker='<p class="eyebrow">The property</p><h2>';mi=s.find(marker)
    if mi>=0:
        ps=s.find('<p>',mi+len(marker));pe=s.find('</p>',ps)
        if ps>=0 and pe>=0:
            neutral=f'<p>This permanent property record is retained for continuity. NorthEdge is not presenting {address}, {suburb} as a current NorthEdge campaign. Confirm the current selling status, representative and campaign documents from an authoritative source before acting.</p>'
            s=s[:ps]+neutral+s[pe+4:]
    s=s.replace('<dt>Inspection</dt><dd>Contact agent</dd>','<dt>Inspection</dt><dd>Not presented as a current NorthEdge campaign</dd>',1)
    s=s.replace('<dt>Statement of Information</dt><dd>Confirm with agent before acting</dd>','<dt>Statement of Information</dt><dd>Not presented as a current NorthEdge campaign</dd>',1)
    s=s.replace('<dt>Agency</dt><dd>NorthEdge Real Estate</dd>','<dt>Record status</dt><dd>Permanent URL retained</dd>',1)
    s=s.replace('<h2>Ask about this property.</h2><p>Enquire without creating an account. The NorthEdge team will respond directly.</p>','<h2>Ask NorthEdge about this address.</h2><p>This page is not a current NorthEdge sale campaign. You may contact the team about its historical involvement or other property services.</p>',1)
    s=s.replace(oldprice,'—').replace('Current NorthEdge campaign','No current NorthEdge campaign').replace('NorthEdge current campaign','No current NorthEdge campaign').replace('Current NorthEdge price guide','No current NorthEdge campaign')
    p.write_text(s,encoding='utf-8')

css=pub/'assets/css/final-demo.css';cs=css.read_text(encoding='utf-8');marker='/* Property record: conservative non-current state */'
if marker not in cs:
    cs += '\n\n/* Property record: conservative non-current state */\n.property-gallery-archived{background:var(--paper,#F6F3ED);padding:clamp(90px,11vw,150px) 0 48px}\n.property-archive-notice{max-width:820px;border-top:1px solid rgba(129,91,37,.45);border-bottom:1px solid var(--hairline,#D8D0C4);padding:42px 0}\n.property-archive-notice h2{margin:10px 0 14px;font:300 clamp(40px,5vw,68px)/.95 var(--serif);color:var(--ink,#20272B)}\n.property-archive-notice p:last-child{max-width:680px;color:var(--slate,#485158);line-height:1.75}\n'
    css.write_text(cs,encoding='utf-8')

(root/'docs/PROPERTY_MEDIA_AUDIT.md').write_text("""# NorthEdge Property Media Audit

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
""",encoding='utf-8')

prov=root/'docs/SOURCE_PROVENANCE.md';pr=prov.read_text(encoding='utf-8')
note="""
## 10 August 2026 current-campaign and media revalidation

Cutover review separated current NorthEdge campaigns from stale legacy-feed records. `105 Tungsten Drive` is no longer presented as a current NorthEdge campaign because fresher public evidence identifies another current selling agency. `6 Alisterus Road` is no longer presented as current because current property data reports it off-market and no reliable current NorthEdge sale evidence was found. Their permanent routes are retained as `noindex` records without campaign galleries.

The four retained active campaigns require full NorthEdge/VaultRE-controlled gallery ingestion before live-domain cutover. Third-party portal images are evidence of campaign depth only and are not a production asset source.
"""
if '## 10 August 2026 current-campaign and media revalidation' not in pr:prov.write_text(pr.rstrip()+'\n'+note,encoding='utf-8')

# Verify truth invariants.
data=json.loads(dp.read_text(encoding='utf-8'));active=[p for p in data if p.get('status')=='active'];arch=[p for p in data if p.get('status')=='archived']
assert len(active)==4,[p['slug'] for p in active]
assert {p['slug'] for p in arch}==set(stale.values())
for html in pub.glob('*.html'):
    s=html.read_text(encoding='utf-8')
    for address in stale:
        for m in re.finditer(re.escape(address),s):
            a=s.rfind('<article class="property-card',0,m.start());b=s.find('</article>',m.start())
            assert not(a>=0 and b>=m.start()),f'stale card {address} in {html}'
for slug in stale.values():
    s=(pub/(slug+'.html')).read_text(encoding='utf-8')
    assert 'noindex,follow' in s and 'data-gallery-open' not in s
home=(pub/'index.html').read_text(encoding='utf-8');assert 'Four current homes.' in home;assert home.count('<article class="property-card')==4
rt=ET.parse(sm).getroot();locs=[n.text for n in rt.iter() if n.tag.endswith('loc')]
assert len(locs)==26,len(locs);assert not any('105-tungsten' in x or '6-alisterus' in x for x in locs)
print('Campaign truth gate PASS', [p['slug'] for p in active], 'sitemap',len(locs))

# Build the release manifest for the final tree, excluding the temporary transport files.
old=json.loads((root/'RELEASE_MANIFEST.json').read_text(encoding='utf-8'));exclude={'.github/workflows/property-truth-media-audit.yml','tools/reconcile-current-campaigns.py'};entries=[]
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root).as_posix()
    if not p.is_file() or '.git' in p.parts or p.name=='RELEASE_MANIFEST.json' or rel in exclude:continue
    b=p.read_bytes();entries.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out={k:old.get(k) for k in ['release','baseRelease','baseSha256'] if old.get(k) is not None};out['date']='2026-08-10';out['fileCount']=len(entries)+1;out['files']=entries
(root/'RELEASE_MANIFEST.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Final clean release files',out['fileCount'])
