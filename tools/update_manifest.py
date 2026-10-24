"""Refresh hashes after a reviewed, intentional change; never run automatically."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.venv', 'work', '__pycache__'}
files = []
for path in sorted(ROOT.rglob('*')):
    rel = path.relative_to(ROOT)
    if not path.is_file() or any(p in IGNORED for p in rel.parts):
        continue
    if rel.as_posix() == 'manifest.json' or path.name == '.DS_Store' or path.suffix == '.pyc':
        continue
    assert not path.is_symlink(), f'symlink not supported: {rel}'
    raw = path.read_bytes()
    files.append({'path': rel.as_posix(), 'bytes': len(raw),
                  'sha256': hashlib.sha256(raw).hexdigest()})
assert sum(r['bytes'] for r in files) < 50_000_000
out = {'schema_version': 1, 'package_version': '1.0.0',
       'scope': 'All distributed files except this manifest; generated work and environments excluded.',
       'files': files}
(ROOT/'manifest.json').write_text(json.dumps(out, indent=2)+'\n')
print('Manifest:', len(files), 'files;', sum(r['bytes'] for r in files), 'bytes before manifest')
