from __future__ import annotations
import base64, hashlib, json, lzma, os, shutil, subprocess, tarfile, tempfile, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / '.bootstrap' / 'changed_text.b64'
PREVIEW = 'https://northedge-rebirth.netlify.app/'
MANIFEST = ROOT / 'RELEASE_MANIFEST.json'
REMOVE = [
    ROOT / '.bootstrap',
    ROOT / '.github' / 'workflows' / 'bootstrap-cutover.yml',
    ROOT / 'tools' / 'bootstrap-compact.py',
]

def sha256(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def run(*args: str):
    subprocess.run(args, cwd=ROOT, check=True)

# 1) Restore every changed/non-public text file exactly as prepared locally.
raw = lzma.decompress(base64.b64decode(PAYLOAD.read_text().strip()))
with tempfile.NamedTemporaryFile(suffix='.tar', delete=False) as tf:
    tf.write(raw); name=tf.name
try:
    with tarfile.open(name, 'r:') as t:
        for m in t.getmembers():
            dest=(ROOT / m.name).resolve()
            if ROOT.resolve() not in dest.parents and dest != ROOT.resolve():
                raise RuntimeError(f'Unsafe payload member: {m.name}')
        t.extractall(ROOT)
finally:
    os.unlink(name)

manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
entries=manifest['files']
print(f'Manifest entries: {len(entries)}')

# 2) Retrieve only package files not in the compact payload from the approved
# R3 preview. Never accept a byte unless it matches the Cutover R1 manifest.
for e in entries:
    rel=e['path']
    p=ROOT / rel
    if p.exists() and p.is_file() and p.stat().st_size == e['bytes'] and sha256(p) == e['sha256']:
        continue
    if not rel.startswith('public/'):
        raise RuntimeError(f'Non-public package file missing/mismatched after payload extraction: {rel}')
    url=PREVIEW + rel[len('public/'):]
    p.parent.mkdir(parents=True, exist_ok=True)
    err=None
    for attempt in range(3):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'ProddyG-NorthEdge-Cutover/1.0'})
            with urllib.request.urlopen(req, timeout=30) as r:
                data=r.read()
            got=hashlib.sha256(data).hexdigest()
            if len(data)!=e['bytes'] or got!=e['sha256']:
                raise RuntimeError(f'Integrity mismatch for {rel}: bytes {len(data)}/{e["bytes"]}, sha {got}/{e["sha256"]}')
            p.write_bytes(data)
            print('verified download', rel)
            err=None; break
        except Exception as ex:
            err=ex; time.sleep(2*(attempt+1))
    if err: raise err

# 3) Full package verification against the locally-authored manifest.
problems=[]
for e in entries:
    p=ROOT/e['path']
    if not p.is_file(): problems.append(f'missing {e["path"]}'); continue
    if p.stat().st_size!=e['bytes']: problems.append(f'size {e["path"]}')
    if sha256(p)!=e['sha256']: problems.append(f'sha256 {e["path"]}')
if problems:
    raise RuntimeError('Manifest verification failed: ' + '; '.join(problems[:20]))
print('All manifest entries verified.')

# Package manifest intentionally excludes itself; verify expected total tree.
package_files=[p for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and '.bootstrap' not in p.parts and not ('.github' in p.parts and 'workflows' in p.parts and p.name=='bootstrap-cutover.yml') and p.name!='bootstrap-compact.py']
if len(package_files) != manifest['fileCount']:
    raise RuntimeError(f'Package file count mismatch: {len(package_files)} != {manifest["fileCount"]}')

# 4) Remove one-time transport/bootstrap material so release HEAD contains only
# the verified Cutover R1 repository tree.
for p in REMOVE:
    if p.is_dir(): shutil.rmtree(p, ignore_errors=True)
    elif p.exists(): p.unlink()
for d in [ROOT/'.github'/'workflows', ROOT/'.github']:
    try: d.rmdir()
    except OSError: pass

run('git','config','user.name','github-actions[bot]')
run('git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com')
run('git','add','-A')
run('git','commit','-m','release: NorthEdge Cutover R1')
run('git','push','origin','HEAD:release/northedge-cutover-r1')
print('Cutover R1 committed and pushed after full integrity verification.')
