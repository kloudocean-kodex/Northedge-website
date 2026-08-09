from pathlib import Path
import json,hashlib
root=Path(__file__).resolve().parents[1]
public=root/'public'
old='© 2026 NorthEdge Real Estate'
new='© 2026 NorthEdge Real Estate · NORTHEDGE REAL ESTATE PTY LTD · ABN 35 690 949 412'
for p in sorted(public.glob('*.html')):
    s=p.read_text(encoding='utf-8')
    if old in s and new not in s:s=s.replace(old,new)
    p.write_text(s,encoding='utf-8')
for name in ['privacy.html','terms.html']:
    p=public/name;s=p.read_text(encoding='utf-8')
    marker='<p class="eyebrow">NorthEdge Real Estate</p>'
    identity='<p class="eyebrow">NORTHEDGE REAL ESTATE PTY LTD · ABN 35 690 949 412</p>'
    if marker in s:s=s.replace(marker,identity,1)
    p.write_text(s,encoding='utf-8')
