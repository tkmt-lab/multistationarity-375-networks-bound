"""Fixed upstream identity and standard-library input validation."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
REVISION = '323360df12c0787f9bbf7f223a6229b98233be39'
URL = ('https://raw.githubusercontent.com/zjdong-sudo/paper-multistability-results/'
       + REVISION + '/results/375_multistable_networks.json')
EXPECTED = '517d1f16f890159185f5384fa2ab089ec4d270e03efe31161ed29489121e252c'
INPUT_BYTES = 395599
INPUT = ROOT / 'work/input/375_multistable_networks.json'


def json_file(relative):
    return json.loads((ROOT / relative).read_text())


def validate_bytes(raw):
    assert len(raw) == INPUT_BYTES, 'upstream input size mismatch'
    assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'upstream SHA256 mismatch'


def validate_network(row):
    y, n = row['Y'], row['N']
    assert len(y) == len(n) == 3
    assert all(len(v) == 6 for v in y + n)
    assert all(type(q) is int for v in y + n for q in v)
    assert all(y[i][j] in (0, 1) and y[i][j] + n[i][j] in (0, 1)
               for i in range(3) for j in range(6))
    assert all(sum(y[i][j] for i in range(3)) <= 2 for j in range(6))
    assert any(sum(y[i][j] for i in range(3)) == 2 for j in range(6))


def load():
    if not INPUT.is_file():
        raise FileNotFoundError('Run python3 tools/fetch_input.py first.')
    raw = INPUT.read_bytes()
    validate_bytes(raw)
    rows = json.loads(raw)['networks']
    assert len(rows) == 375 and len({r['candidate_index'] for r in rows}) == 375
    for row in rows:
        validate_network(row)
    return rows


def verify_manifest():
    records = json_file('manifest.json')['files']
    assert records and len({r['path'] for r in records}) == len(records)
    for rec in records:
        p = Path(rec['path'])
        assert not p.is_absolute() and '..' not in p.parts
        raw = (ROOT / p).read_bytes()
        assert len(raw) == rec['bytes'], f"size mismatch: {p}"
        assert hashlib.sha256(raw).hexdigest() == rec['sha256'], f"hash mismatch: {p}"
    required = {p.relative_to(ROOT).as_posix() for d in ['checkers', 'certificates']
                for p in (ROOT / d).glob('*') if p.is_file()}
    assert required <= {r['path'] for r in records}
    return len(records)
