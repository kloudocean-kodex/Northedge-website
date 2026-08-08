from pathlib import Path
import json, hashlib
root=Path(__file__).resolve().parents[1]

for p in sorted((root/'public').glob('property-*.html')):
    s=p.read_text(encoding='utf-8')
    s=s.replace('<dt>Statement of Information</dt><dd>Available from agent</dd>','<dt>Statement of Information</dt><dd>Confirm with agent before acting</dd>')
    if p.name=='property-6-alisterus-road-kalkallo.html':
        s=s.replace('Contact NorthEdge for the complete photography set, Statement of Information and inspection arrangements.','Contact NorthEdge for the current photography, document status and inspection arrangements before acting.')
        s=s.replace('Statement of Information available','Current campaign documents to be confirmed')
    p.write_text(s,encoding='utf-8')

dp=root/'public/data/properties.json'
data=json.loads(dp.read_text(encoding='utf-8'))
for prop in data:
    if prop.get('slug')=='6-alisterus-road-kalkallo':
        prop['description']='A four-bedroom Kalkallo campaign positioned for buyers seeking a contemporary family home within the established Cloverton community. Contact NorthEdge for the current photography, document status and inspection arrangements before acting.'
        prop['highlights']=[('Current campaign documents to be confirmed' if x=='Statement of Information available' else x) for x in prop.get('highlights',[])]
dp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

qa=root/'docs/QA_REPORT.md'
s=qa.read_text(encoding='utf-8')
needle="These are point-in-time campaign facts. They must still be reverified against NorthEdge's authoritative listing source immediately before public-domain cutover. Statements of Information, inspection times and legal/compliance facts remain separate launch gates."
addition=needle+"\n\nFor that reason, property pages do not claim that a Statement of Information is currently available; they instruct users to confirm current document status with the agent before acting."
if addition not in s:s=s.replace(needle,addition)
qa.write_text(s,encoding='utf-8')

# Manifest excludes itself and one-time transport material and always stores repository-relative paths.
old=json.loads((root/'RELEASE_MANIFEST.json').read_text(encoding='utf-8'))
entries=[]
for p in sorted(root.rglob('*')):
    if not p.is_file() or '.git' in p.parts or p.name=='RELEASE_MANIFEST.json':
        continue
    rel=p.relative_to(root).as_posix()
    if rel in {'tools/conservative-soi-pass.py','.github/workflows/conservative-soi-pass.yml'}:
        continue
    b=p.read_bytes();entries.append({'path':rel,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
manifest={'release':old['release'],'date':old['date'],'baseRelease':old['baseRelease'],'baseSha256':old['baseSha256'],'fileCount':len(entries)+1,'files':entries}
(root/'RELEASE_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

alltxt='\n'.join(p.read_text(encoding='utf-8',errors='ignore') for p in (root/'public').glob('*.html'))
if 'Available from agent' in alltxt or 'Statement of Information available' in alltxt or 'Statement of Information available' in dp.read_text(encoding='utf-8'):
    raise RuntimeError('Unverified SOI availability wording remains')
if manifest['fileCount']!=176 or len(entries)!=175:raise RuntimeError(f'Unexpected manifest count: {manifest["fileCount"]}/{len(entries)}')
