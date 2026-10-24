"""Download the fixed upstream file to ignored work/input, then check its hash."""
from pathlib import Path
import sys
import urllib.request

if not __debug__:
    raise SystemExit('Checks require Python assertions; do not use -O or -OO.')
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'checkers'))
from common import INPUT, INPUT_BYTES, EXPECTED, URL, validate_bytes


def fetch():
    if INPUT.exists():
        validate_bytes(INPUT.read_bytes())
        print('PASS existing upstream input:', EXPECTED)
        return
    request = urllib.request.Request(URL, headers={'User-Agent': '375-networks-bound/1.0.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        raw = response.read(INPUT_BYTES + 1)
    validate_bytes(raw)
    INPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = INPUT.with_suffix('.json.part')
    temporary.write_bytes(raw)
    temporary.replace(INPUT)
    print('PASS downloaded upstream input:', len(raw), 'bytes;', EXPECTED)


if __name__ == '__main__':
    fetch()
