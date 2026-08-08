from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]

# Candidate-only route corrections. Keep the two old URLs only as redirect sources.
route_refs={
    'property-rullinga-road-donnybrook.html':'property-7-rulingia-road-donnybrook.html',
    'property-rullinga-road-donnybrook':'property-7-rulingia-road-donnybrook',
    'property-mathoura-road-mickleham.html':'property-6-mathoura-road-mickleham.html',
    'property-mathoura-road-mickleham':'property-6-mathoura-road-mickleham',
}
for p in root.rglob('*'):
    if not p.is_file() or p.name=='RELEASE_MANIFEST.json' or '.git' in p.parts:
        continue
    try:s=p.read_text(encoding='utf-8')
    except UnicodeDecodeError:continue
    old=s
    for a,b in sorted(route_refs.items(),key=lambda x:len(x[0]),reverse=True):s=s.replace(a,b)
    if s!=old:p.write_text(s,encoding='utf-8')

old_r=root/'public/property-rullinga-road-donnybrook.html'
new_r=root/'public/property-7-rulingia-road-donnybrook.html'
old_m=root/'public/property-mathoura-road-mickleham.html'
new_m=root/'public/property-6-mathoura-road-mickleham.html'
if not old_r.exists() or new_r.exists():raise RuntimeError('Unexpected Rulingia route state')
if not old_m.exists() or new_m.exists():raise RuntimeError('Unexpected Mathoura route state')
old_r.rename(new_r);old_m.rename(new_m)

for p in [root/'public/buy.html',root/'public/index.html',root/'public/area-donnybrook.html',new_r]:
    s=p.read_text(encoding='utf-8').replace('Rullinga Road','7 Rulingia Road').replace('Rullinga+Road','7+Rulingia+Road')
    p.write_text(s,encoding='utf-8')
for p in [root/'public/buy.html',root/'public/index.html',root/'public/area-mickleham.html',new_m]:
    s=p.read_text(encoding='utf-8').replace('Mathoura Road','6 Mathoura Road').replace('Mathoura+Road','6+Mathoura+Road')
    p.write_text(s,encoding='utf-8')

# Structured property data.
dp=root/'public/data/properties.json'
data=json.loads(dp.read_text(encoding='utf-8'))
for prop in data:
    slug=prop['slug']
    if slug=='rullinga-road-donnybrook':
        prop['slug']='7-rulingia-road-donnybrook';prop['address']='7 Rulingia Road';prop['land']='392 m²'
    elif slug=='mathoura-road-mickleham':
        prop['slug']='6-mathoura-road-mickleham';prop['address']='6 Mathoura Road';prop['land']='448 m²'
    elif slug=='105-tungsten-drive-kalkallo':
        prop['price']='$660,000 – $690,000';prop['note']='NorthEdge current campaign'
        prop['description']=prop['description'].replace('Price guidance is available directly from the NorthEdge team so buyers can discuss the home and campaign context properly.','The current NorthEdge campaign is guided at $660,000 – $690,000. Buyers should confirm availability, inspections and campaign documents directly with the agency before acting.')
        prop['highlights']=[('Current NorthEdge price guide' if x=='Direct agent price guidance' else x) for x in prop['highlights']]
    elif slug=='6-alisterus-road-kalkallo':
        prop['price']='$660,000 – $689,000';prop['note']='NorthEdge current campaign'
dp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def replace_card_state(p,address,price,old_note):
    s=p.read_text(encoding='utf-8');marker=f'alt="{address}, Kalkallo"';i=s.find(marker)
    if i<0:raise RuntimeError(f'Card missing: {address} in {p}')
    a=s.rfind('<article class="property-card"',0,i);b=s.find('</article>',i)+len('</article>');card=s[a:b]
    card=card.replace('data-price="0"','data-price="660000"',1)
    card=card.replace('<p class="property-price">Contact agent</p>',f'<p class="property-price">{price}</p>',1)
    card=card.replace(f'<p class="property-note">{old_note}</p>','<p class="property-note">NorthEdge current campaign</p>',1)
    p.write_text(s[:a]+card+s[b:],encoding='utf-8')
replace_card_state(root/'public/index.html','105 Tungsten Drive','$660,000 – $690,000','Private price guidance')
replace_card_state(root/'public/area-kalkallo.html','105 Tungsten Drive','$660,000 – $690,000','Private price guidance')
replace_card_state(root/'public/area-kalkallo.html','6 Alisterus Road','$660,000 – $689,000','Inspection by arrangement')

land_icon='<span><svg aria-hidden="true" class="icon" viewbox="0 0 20 20"><path d="M2 15 7 5l4 6 2-3 5 7H2Z"></path></svg>{land}</span>'
def add_land_card(p,address,land,suburb):
    s=p.read_text(encoding='utf-8');i=s.find(f'alt="{address}, {suburb}"')
    if i<0:raise RuntimeError(f'Land card missing: {address} in {p}')
    a=s.rfind('<article class="property-card"',0,i);b=s.find('</article>',i)+len('</article>');card=s[a:b]
    if land not in card:
        ps=card.find('<div class="property-specs">');pe=card.find('</div>',ps)
        if ps<0 or pe<0:raise RuntimeError('Property specs missing')
        card=card[:pe]+land_icon.format(land=land)+card[pe:]
        p.write_text(s[:a]+card+s[b:],encoding='utf-8')
for p in [root/'public/index.html',root/'public/buy.html',root/'public/area-donnybrook.html']:
    add_land_card(p,'7 Rulingia Road','392 m²','Donnybrook')
for p in [root/'public/index.html',root/'public/buy.html',root/'public/area-mickleham.html']:
    add_land_card(p,'6 Mathoura Road','448 m²','Mickleham')

def property_land(p,land):
    s=p.read_text(encoding='utf-8');h=s.find('<section class="property-head">');d=s.find('<section class="property-detail">',h);seg=s[h:d]
    if land not in seg:
        ps=seg.find('<div class="property-specs">');pe=seg.find('</div>',ps);seg=seg[:pe]+land_icon.format(land=land)+seg[pe:];s=s[:h]+seg+s[d:]
    s=s.replace('<dt>Land</dt><dd>—</dd>',f'<dt>Land</dt><dd>{land}</dd>',1)
    p.write_text(s,encoding='utf-8')
property_land(new_r,'392 m²');property_land(new_m,'448 m²')

p=root/'public/property-105-tungsten-drive-kalkallo.html';s=p.read_text(encoding='utf-8')
s=s.replace('Price guidance is available directly from the NorthEdge team so buyers can discuss the home and campaign context properly.','The current NorthEdge campaign is guided at $660,000 – $690,000. Buyers should confirm availability, inspections and campaign documents directly with the agency before acting.')
s=s.replace('Direct agent price guidance','Current NorthEdge price guide');p.write_text(s,encoding='utf-8')

redir=root/'public/_redirects';r=redir.read_text(encoding='utf-8').rstrip()+'\n'
for line in ['/property-rullinga-road-donnybrook.html /property-7-rulingia-road-donnybrook.html 301','/property-mathoura-road-mickleham.html /property-6-mathoura-road-mickleham.html 301']:
    if line not in r:r+=line+'\n'
redir.write_text(r,encoding='utf-8')

qa=root/'docs/QA_REPORT.md';s=qa.read_text(encoding='utf-8')
insert='''\n## Current campaign data correction pass\n\nBefore PR creation, the release candidate was cross-checked on 8 August 2026 against NorthEdge's current public sale feed and independent current listing evidence. The following consistency corrections were applied across listing cards, property data, property routes, canonicals, sitemap references and enquiry form identifiers:\n\n- `105 Tungsten Drive, Kalkallo`: `$660,000 – $690,000`.\n- `6 Alisterus Road, Kalkallo`: `$660,000 – $689,000`.\n- Donnybrook campaign corrected from the incomplete/misspelled `Rullinga Road` label to `7 Rulingia Road, Donnybrook`; verified land size `392 m²`.\n- Mickleham campaign corrected from `Mathoura Road` to `6 Mathoura Road, Mickleham`; verified land size `448 m²`.\n\nThese are point-in-time campaign facts. They must still be reverified against NorthEdge's authoritative listing source immediately before public-domain cutover. Statements of Information, inspection times and legal/compliance facts remain separate launch gates.\n'''
if '## Current campaign data correction pass' not in s:s=s.replace('\n## Form behaviour\n',insert+'\n## Form behaviour\n')
qa.write_text(s,encoding='utf-8')
prov=root/'docs/SOURCE_PROVENANCE.md';s=prov.read_text(encoding='utf-8')
extra='''\n## 8 August 2026 campaign-data verification\n\nBefore PR creation, current public campaign evidence was used to correct two stale price displays and two incomplete property addresses inherited from the demonstration data. This does not replace the requirement to verify all live listing facts and compliance documents again immediately before domain cutover.\n'''
if '## 8 August 2026 campaign-data verification' not in s:s=s.rstrip()+'\n'+extra
prov.write_text(s,encoding='utf-8')

if old_r.exists() or old_m.exists():raise RuntimeError('Old physical routes remain')
if not new_r.exists() or not new_m.exists():raise RuntimeError('Corrected physical routes missing')
