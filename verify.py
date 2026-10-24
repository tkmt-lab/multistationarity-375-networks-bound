#!/usr/bin/env python3
"""Run the exact checks; a partial run never prints the full-package PASS."""
from pathlib import Path
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import json
import signal
import sys
import time

if not __debug__:
    raise SystemExit('Checks require Python assertions; do not use -O or -OO.')
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'checkers'))
from common import load, json_file, verify_manifest, EXPECTED, validate_bytes, INPUT


def rejected(label, function):
    try:
        function()
    except (AssertionError, ValueError, KeyError, ZeroDivisionError):
        return {'mutation': label, 'rejected': True}
    raise AssertionError('Negative control was accepted: ' + label)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--stdlib-only', action='store_true', help='B1 and Cramer B2 only; no B3 or Sylvester')
    ap.add_argument('--seconds', type=int, default=300, help='wall limit (Unix platforms)')
    args = ap.parse_args()
    assert 1 <= args.seconds <= 600
    if hasattr(signal, 'SIGALRM'):
        def timeout(_signal, _frame):
            raise TimeoutError('Verification wall limit reached; no PASS')
        signal.signal(signal.SIGALRM, timeout)
        signal.alarm(args.seconds)
    start = time.monotonic()
    report = {'started_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version,
              'upstream_sha256': EXPECTED, 'mode': 'stdlib-only' if args.stdlib_only else 'full',
              'manifest_file_count': verify_manifest()}
    source = {r['candidate_index']: r for r in load()}
    import cramer
    records = [json.loads(l) for l in (ROOT/'certificates/cramer.jsonl').read_text().splitlines()]
    assert len(records) == 375 and {r['candidate_index'] for r in records} == set(source)
    result = [cramer.check(source[r['candidate_index']], r) for r in records]
    degrees = dict(Counter(r['degree'] for r in result))
    assert degrees == {3: 272, 4: 103}
    witnesses = dict(Counter(r['denominator_certificate']['strict_polynomial'] for r in result))
    assert witnesses == {'D': 251, 'U': 100, 'V': 24}
    removed = Counter('strict-sign' if f['reason']=='strict sign on positive parameters and coordinate'
                      else 'divisor-of-D' for r in records for f in r['certificate']['removed_factors'])
    assert removed == {'strict-sign': 706, 'divisor-of-D': 21}
    cramer_degrees = {r['candidate_index']: r['degree'] for r in result}
    good = records[0]
    negatives = []
    for key, value in [('D', good['certificate']['D']+'+1'),
                       ('Q', good['certificate']['Q']+'+1'),
                       ('D_sign_at_positive_equilibria', -good['certificate']['D_sign_at_positive_equilibria'])]:
        bad = copy.deepcopy(good)
        bad['certificate'][key] = value
        negatives.append(rejected('Cramer '+key, lambda: cramer.check(source[bad['candidate_index']], bad)))
    negatives.append(rejected('upstream byte change', lambda: validate_bytes(INPUT.read_bytes()[:-1] + b'!')))
    report['cramer'] = {'network_count': len(result), 'degree_counts': degrees,
                        'denominator_witness_counts': witnesses,
                        'removed_factor_entries': dict(removed), 'networks': result}
    print('PASS Cramer: 375 networks (272 cubics, 103 quartics)', flush=True)
    import structure
    structural = structure.run()
    assert structural == json_file('certificates/structure.json')
    report['structure'] = structural
    print('PASS B1: finite table; selected 33449, 239089', flush=True)
    if not args.stdlib_only:
        import sympy
        import sylvester
        report['sympy'] = sympy.__version__
        proofs = json_file('certificates/resultants.json')
        assert len(proofs) == 375 and {p['candidate_index'] for p in proofs} == set(source)
        result = []
        for i, item in enumerate(proofs, 1):
            result.append(sylvester.check(source[item['candidate_index']], item['proof']))
            if i % 75 == 0: print(f'Sylvester: {i}/375 verified', flush=True)
        assert all(r['root_factor_degrees']==[cramer_degrees[r['candidate_index']]] and r['bound']==3
                   for r in result)
        special = [p['candidate_index'] for p in proofs if 'equation_basis' in p['proof']]
        assert special == [48328, 74814, 100108]
        cramer_axes = {r['candidate_index']: 'xyz'.index(r['certificate']['coordinate']) for r in records}
        differing_axes = sum(cramer_axes[p['candidate_index']] != p['proof']['order'][2] for p in proofs)
        assert differing_axes == 79
        bad = copy.deepcopy(proofs[0])
        bad['proof']['root_factors'][0]['factor'] += '+1'
        negatives.append(rejected('Sylvester root factor', lambda: sylvester.check(source[bad['candidate_index']], bad['proof'])))
        bad = copy.deepcopy(proofs[0])
        bad['proof']['nonvanishing_factors'][0]['sign'] *= -1
        negatives.append(rejected('Sylvester removed-factor sign', lambda: sylvester.check(source[bad['candidate_index']], bad['proof'])))
        report['sylvester'] = {'network_count': len(result), 'networks': result,
                              'equation_transform_ids': special, 'different_retained_coordinates': differing_axes}
        import seven_reaction_t
        import seven_reaction_z
        report['seven_reaction_t'] = seven_reaction_t.run()
        report['seven_reaction_z'] = seven_reaction_z.run(json_file('certificates/seven-reaction-sample.json'))
        assert report['seven_reaction_z'] == json_file('certificates/seven-reaction-z.json')
        z = report['seven_reaction_z']['samples'][0]
        assert z['positive_equilibria'] == 3 and z['exponentially_stable_equilibria'] == 1
        from fractions import Fraction as Q
        import rational_polynomials as R
        a,b,c,d,e,f = map(Q,z['kappa'])
        p = list(map(Q,reversed(json_file('certificates/seven-reaction-t.json')['q_coefficients_descending'])))
        seq = R.sturm(p)
        correspondence = []
        for zr,tr in zip(reversed(z['roots']), report['seven_reaction_t']['roots']):
            lo,hi = map(Q,zr['z_interval'])
            mapped = (d*b/(a*e*hi)+(d*c-b*e)/(a*e), d*b/(a*e*lo)+(d*c-b*e)/(a*e))
            tbox = tuple(map(Q,tr['t_interval']))
            assert max(mapped[0],tbox[0]) < min(mapped[1],tbox[1])
            union = min(mapped[0],tbox[0]), max(mapped[1],tbox[1])
            assert all(R.evaluate(p,q) != 0 for q in union) and R.count(seq,*union)==1
            assert [zr['signs'][k] for k in ['b1','b2','b3','H2']]==tr['hurwitz_signs']
            correspondence.append({'mapped_z_interval_in_t':list(map(str,mapped)),
                                   'union_sturm_roots':1,'hurwitz_signs_agree':True})
        assert len(correspondence)==3
        report['seven_reaction_correspondence'] = correspondence
        print('PASS B3: both coordinates; 3 positive equilibria, 1 exponentially stable', flush=True)
    report['negative_controls'] = negatives
    report['elapsed_seconds'] = time.monotonic()-start
    report['status'] = 'PASS_STDLIB_SUBSET' if args.stdlib_only else 'PASS'
    (ROOT/'work').mkdir(exist_ok=True)
    output = ROOT / ('work/stdlib-verification.json' if args.stdlib_only else 'work/verification.json')
    output.write_text(json.dumps(report, indent=2)+'\n')
    print(report['status'], f"({report['elapsed_seconds']:.3f}s);", output.relative_to(ROOT), flush=True)


if __name__ == '__main__':
    main()
