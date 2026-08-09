from pathlib import Path
import hashlib,json,re

root=Path(__file__).resolve().parents[1]
pub=root/'public'

pages={
 'property-27-design-way-kalkallo.html':{
   'address':'27 Design Way, Kalkallo VIC 3064','og':'assets/images/kalkallo-facade-1600.jpg'},
 'property-31-roseneath-way-mickleham.html':{
   'address':'31 Roseneath Way, Mickleham VIC 3064','og':'assets/images/roseneath-facade-1600.jpg'},
 'property-6-mathoura-road-mickleham.html':{
   'address':'6 Mathoura Road, Mickleham VIC 3064','og':'assets/images/drone-mathoura-1600.jpg'},
 'property-7-rulingia-road-donnybrook.html':{
   'address':'7 Rulingia Road, Donnybrook VIC 3064','og':'assets/images/donnybrook-drone-1600.jpg'},
}

for name,cfg in pages.items():
    p=pub/name;s=p.read_text(encoding='utf-8')
    # Use a property-specific local campaign image for the social preview rather than the generic corridor image.
    absolute='https://northedgerealestate.com.au/'+cfg['og']
    s=re.sub(r'<meta content="https://northedgerealestate\.com\.au/assets/images/hero-corridor-1600\.jpg" property="og:image"/>',f'<meta content="{absolute}" property="og:image"/><meta content="{cfg["address"]} — property campaign image" property="og:image:alt"/>',s,count=1)
    # Neutral, truthful sequence labels until authoritative VaultRE captions are available.
    gm=re.search(r'<section class="property-gallery">(.*?)</section>',s,re.S)
    if not gm: raise RuntimeError(f'Property gallery missing: {name}')
    section=gm.group(0)
    count=section.count('data-gallery-open')
    if count<1: raise RuntimeError(f'No gallery items: {name}')
    index=0
    def alt_repl(m):
        nonlocal_index[0]+=1
        return f'alt="{cfg["address"]} — property image {nonlocal_index[0]} of {count}"'
    nonlocal_index=[0]
    section=re.sub(r'alt="[^"]*property photography"',alt_repl,section)
    # Ensure script is loaded after site.js, which owns open/close/focus-return behaviour.
    s=s[:gm.start()]+section+s[gm.end():]
    marker='<script defer="" src="assets/js/property-gallery.js"></script>'
    if marker not in s:
        s=s.replace('<script defer="" src="assets/js/site.js"></script></body>',f'<script defer="" src="assets/js/site.js"></script>{marker}</body>',1)
    p.write_text(s,encoding='utf-8')

css=pub/'assets/css/final-demo.css';cs=css.read_text(encoding='utf-8')
marker='/* Production property gallery navigation */'
if marker not in cs:
    cs += r'''

/* Production property gallery navigation */
.gallery-grid .gallery-extra{display:none}
.lightbox{grid-template-rows:minmax(0,1fr) auto auto;grid-template-columns:minmax(0,1fr);align-content:center;justify-items:center}
.lightbox>img{grid-row:1;grid-column:1;width:auto;height:auto}
.lightbox-nav{grid-row:2;grid-column:1;display:flex;align-items:center;justify-content:center;gap:18px;margin-top:18px;color:#fff}
.lightbox-arrow{width:48px;height:48px;display:grid;place-items:center;border:1px solid rgba(255,255,255,.42);background:rgba(7,19,26,.64);color:#fff;transition:background .2s ease,border-color .2s ease,transform .2s ease}
.lightbox-arrow:hover:not(:disabled){background:rgba(255,255,255,.12);border-color:rgba(255,255,255,.75);transform:translateY(-1px)}
.lightbox-arrow:disabled{opacity:.32;cursor:default}
.lightbox-arrow:focus-visible,.lightbox-close:focus-visible{outline:2px solid #D8B37F;outline-offset:3px}
.lightbox-counter{min-width:72px;text-align:center;font:500 11px/1 var(--sans);letter-spacing:.14em;color:rgba(255,255,255,.88)}
.lightbox-caption{grid-row:3;grid-column:1;max-width:min(760px,88vw);margin:12px 0 0;text-align:center;color:rgba(255,255,255,.76);font-size:12px;line-height:1.55;letter-spacing:.02em}
@media(max-width:620px){
  .lightbox{padding:68px 14px 20px;grid-template-rows:minmax(0,1fr) auto auto}
  .lightbox>img{max-width:96vw;max-height:68vh}
  .lightbox-close{right:14px;top:14px;width:44px;height:44px}
  .lightbox-nav{width:100%;justify-content:space-between;gap:12px;margin-top:14px}
  .lightbox-arrow{width:52px;height:48px}
  .lightbox-caption{max-width:92vw;margin-top:9px;font-size:11px}
}
@media(prefers-reduced-motion:reduce){.lightbox-arrow{transition:none}}
'''
    css.write_text(cs,encoding='utf-8')

qa=root/'docs/QA_REPORT.md';q=qa.read_text(encoding='utf-8')
note='''
## Property gallery interaction readiness — 10 August 2026

The four verified active property routes now use property-specific local lead images for Open Graph previews and neutral address-based gallery labels pending authoritative VaultRE captions. The lightbox has production traversal controls: previous/next buttons, arrow-key navigation, touch swipe, live image count, caption, neighbour preloading, visible focus, and mobile-safe control placement. Existing `site.js` remains responsible for modal opening/closing, Escape handling, focus trapping and focus return. The first fold remains the restrained editorial gallery; future authorised VaultRE images can be added as hidden `.gallery-extra` triggers and remain fully traversable without creating a cluttered thumbnail wall.

This interaction work does not close the property-media completeness gate. Full authorised VaultRE masters for all four active campaigns are still required before live-domain cutover.
'''
if '## Property gallery interaction readiness — 10 August 2026' not in q:
    qa.write_text(q.rstrip()+'\n'+note,encoding='utf-8')

audit=root/'docs/PROPERTY_MEDIA_AUDIT.md';a=audit.read_text(encoding='utf-8')
note2='''
## Gallery interface readiness

The production property template is now prepared for complete ordered galleries without changing the restrained first-fold composition. Full galleries will remain locally hosted and can extend beyond the visible lead grid using hidden gallery items that are available to the accessible lightbox. Property-specific social-preview images and neutral per-image labels are in place for the current local assets. This is interface readiness only; the authorised VaultRE master-ingest requirement remains open.
'''
if '## Gallery interface readiness' not in a:audit.write_text(a.rstrip()+'\n'+note2,encoding='utf-8')

# Invariants before building the clean manifest.
for name,cfg in pages.items():
    s=(pub/name).read_text(encoding='utf-8')
    assert 'assets/js/property-gallery.js' in s,name
    assert 'hero-corridor-1600.jpg" property="og:image"' not in s,name
    assert cfg['og'] in s,name
    assert 'property photography' not in re.search(r'<section class="property-gallery">(.*?)</section>',s,re.S).group(0),name
    assert 'og:image:alt' in s,name
for name in ['property-105-tungsten-drive-kalkallo.html','property-6-alisterus-road-kalkallo.html']:
    s=(pub/name).read_text(encoding='utf-8')
    assert 'data-gallery-open' not in s,name
    assert 'assets/js/property-gallery.js' not in s,name
assert marker in css.read_text(encoding='utf-8')
assert (pub/'assets/js/property-gallery.js').is_file()

# Final release manifest excludes one-time transport files.
manifest=root/'RELEASE_MANIFEST.json';old=json.loads(manifest.read_text(encoding='utf-8'))
exclude={'.github/workflows/property-gallery-ux.yml','tools/apply-property-gallery-ux.py'};entries=[]
for p in sorted(root.rglob('*')):
    rel=p.relative_to(root).as_posix()
    if not p.is_file() or '.git' in p.parts or p.name=='RELEASE_MANIFEST.json' or rel in exclude:continue
    b=p.read_bytes();entries.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out={k:old.get(k) for k in ['release','baseRelease','baseSha256'] if old.get(k) is not None};out['date']='2026-08-10';out['fileCount']=len(entries)+1;out['files']=entries
manifest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Property gallery UX gate PASS; clean release files',out['fileCount'])
