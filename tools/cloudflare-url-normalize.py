from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
public=root/'public'

# Cloudflare Pages serves matching .html files at clean extensionless URLs.
# Keep physical filenames, normalize every public-facing NorthEdge URL.
for p in public.glob('*.html'):
    s=p.read_text(encoding='utf-8')
    s=re.sub(r'https://northedgerealestate\.com\.au/([A-Za-z0-9_-]+)\.html(?=([#?"<]|$))',r'https://northedgerealestate.com.au/\1',s)
    s=re.sub(r'href="([A-Za-z0-9_-]+)\.html((?:[#?][^"]*)?)"',r'href="\1\2"',s)
    p.write_text(s,encoding='utf-8')

# Client-side property-search navigation should target the canonical clean URL.
js=public/'assets/js/site.js'
s=js.read_text(encoding='utf-8').replace("location.href='buy.html?'+p.toString()","location.href='/buy?'+p.toString()")
js.write_text(s,encoding='utf-8')

# Sitemap canonicals follow the same clean URL policy.
sitemap=public/'sitemap.xml'
s=sitemap.read_text(encoding='utf-8')
s=re.sub(r'(https://northedgerealestate\.com\.au/[A-Za-z0-9_-]+)\.html(?=</loc>)',r'\1',s)
sitemap.write_text(s,encoding='utf-8')

# Static legacy redirects. Query-dependent listing routes are handled by Pages Functions.
redirects='''/index.html / 301
/home / 301
/about-us/ /about 301
/contacts/ /contact 301
/appraisal/ /sell#appraisal 301
/property-rullinga-road-donnybrook.html /property-7-rulingia-road-donnybrook 301
/property-mathoura-road-mickleham.html /property-6-mathoura-road-mickleham 301
'''
(public/'_redirects').write_text(redirects,encoding='utf-8')

# Do not claim a rental feed/live record until that production integration exists.
rent=public/'rent.html'
s=rent.read_text(encoding='utf-8')
s=s.replace('The production website connects directly to NorthEdge’s rental feed so available dates and prices stay accurate. Register your requirements now and the team can match you to new stock.','Current rental availability changes quickly. Register your requirements and the NorthEdge team can confirm current options, dates and pricing directly before you act.')
s=s.replace('Dates, price and property details are kept aligned with the live rental record.','NorthEdge can confirm current dates, price and property details directly before you apply or inspect.')
rent.write_text(s,encoding='utf-8')

# Function redirect destinations must also be canonical clean URLs.
for rel in ['functions/my-properties-main.js','functions/property-listing-details.js']:
    p=root/rel
    s=p.read_text(encoding='utf-8')
    s=re.sub(r"('/[A-Za-z0-9_-]+)\.html'",r"\1'",s)
    p.write_text(s,encoding='utf-8')
