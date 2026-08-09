from pathlib import Path
import re

root=Path(__file__).resolve().parents[1]
public=root/'public'

# Make every lead form safe without JavaScript: POST to the same-origin API,
# carry its form identifier server-side, and include the static honeypot.
form_re=re.compile(r'<form([^>]*?)data-lead-form="([^"]+)"([^>]*)>')
for p in sorted(public.glob('*.html')):
    s=p.read_text(encoding='utf-8')
    def repl(m):
        before,form,after=m.group(1),m.group(2),m.group(3)
        attrs=(before+f'data-lead-form="{form}"'+after)
        if ' method=' not in attrs: attrs+=' method="post"'
        if ' action=' not in attrs: attrs+=' action="/api/leads"'
        opening='<form'+attrs+'>'
        hidden=(f'<input type="hidden" name="form" value="{form}"/>'
                '<input aria-hidden="true" autocomplete="off" class="hp-field" name="website" tabindex="-1" type="text"/>')
        return opening+hidden
    s=form_re.sub(repl,s)
    p.write_text(s,encoding='utf-8')

# Persist referral confirmation as evidence instead of a UI-only required box.
p=public/'referral.html';s=p.read_text(encoding='utf-8')
s=s.replace('<input required="" type="checkbox"/> I have read the referral terms and confirm the information is accurate.',
            '<input name="referral_consent" required="" type="checkbox" value="confirmed"/> I have read the referral terms and confirm the information is accurate.')
p.write_text(s,encoding='utf-8')

# Donnybrook lightbox: use an image that actually exists in the release.
p=public/'property-7-rulingia-road-donnybrook.html';s=p.read_text(encoding='utf-8')
s=s.replace('data-full="assets/images/donnybrook-living.jpg"','data-full="/assets/images/donnybrook-living-960.jpg"')
p.write_text(s,encoding='utf-8')

# Custom 404 must work at arbitrary path depth. Make every same-site resource and
# navigation target root-relative instead of resolving beneath the missing path.
p=public/'404.html';s=p.read_text(encoding='utf-8')
for prefix in ['assets/','site.webmanifest']:
    s=s.replace(f'href="{prefix}',f'href="/{prefix}').replace(f'src="{prefix}',f'src="/{prefix}')
route_map={
 'href="index"':'href="/"','href="buy"':'href="/buy"','href="rent"':'href="/rent"',
 'href="sell"':'href="/sell"','href="sold"':'href="/sold"','href="areas"':'href="/areas"',
 'href="about"':'href="/about"','href="contact"':'href="/contact"','href="referral"':'href="/referral"',
 'href="property-management"':'href="/property-management"','href="agent-gurinder-sandhu"':'href="/agent-gurinder-sandhu"',
 'href="privacy"':'href="/privacy"','href="terms"':'href="/terms"','href="accessibility"':'href="/accessibility"',
 'href="image-credits"':'href="/image-credits"','href="sell#appraisal"':'href="/sell#appraisal"',
 'src="assets/js/site.js"':'src="/assets/js/site.js"'
}
for a,b in route_map.items():s=s.replace(a,b)
p.write_text(s,encoding='utf-8')

# A no-JS successful form POST lands here. It is intentionally not in the sitemap.
thank=public/'thank-you.html'
if not thank.exists():
    thank.write_text('''<!DOCTYPE html>\n<html lang="en-AU"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><meta name="robots" content="noindex,nofollow"/><title>Enquiry received | NorthEdge Real Estate</title><link rel="icon" type="image/png" href="/assets/images/logo-320.png"/><link rel="stylesheet" href="/assets/css/site.css"/><link rel="stylesheet" href="/assets/css/v2.css"/><link rel="stylesheet" href="/assets/css/client-demo.css"/><link rel="stylesheet" href="/assets/css/final-demo.css"/></head><body><a class="skip-link" href="#main">Skip to content</a><main id="main"><section class="page-hero"><div class="shell page-hero-inner"><p class="eyebrow">Enquiry received</p><h1>Thank you.</h1><p>Your enquiry has been securely received by NorthEdge. For anything time-sensitive, call <a href="tel:0430595481">0430 595 481</a>.</p><div class="page-actions"><a class="button button-dark" href="/">Return home</a><a class="button button-line" href="/contact">Contact NorthEdge</a></div></div></section></main></body></html>\n''',encoding='utf-8')

# Sanity gates for the source issues this pass owns.
all_html='\n'.join(p.read_text(encoding='utf-8') for p in public.glob('*.html'))
if 'data-full="assets/images/donnybrook-living.jpg"' in all_html: raise RuntimeError('Missing Donnybrook image reference remains')
for m in form_re.finditer(all_html):
    tag=m.group(0)
    if 'method="post"' not in tag or 'action="/api/leads"' not in tag: raise RuntimeError('Unsafe non-JS form remains')
if 'name="referral_consent"' not in (public/'referral.html').read_text(encoding='utf-8'): raise RuntimeError('Referral consent is not persisted')
