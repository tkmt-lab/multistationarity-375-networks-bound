"""Recheck the article's retained coordinate t=z/y and its three fixed intervals."""
from fractions import Fraction as Q
import sympy as S
import rational_polynomials as R
from common import load, json_file
from symbolic_input import K, X, equations
from seven_reaction_z import direct_intervals


def run():
    row = next(r for r in load() if r['candidate_index'] == 33449)
    cert = json_file('certificates/seven-reaction-t.json')
    x, y, z = X
    a, b, c, d, e, f = K
    h, t = S.symbols('h t', positive=True)
    F = S.Matrix(equations(row)) + S.Matrix([0, 0, -h*z])
    L = e*a*t + e*b - c*d
    D = t*L
    chart = {x: b*(b+a*t)/D, y: b*d/D, z: b*d/L}
    polynomial = (-e*a*(a+h)*t**3 + (a*c*d-h*(e*b-c*d))*t**2
                  + b*(e*b+f*a-2*c*d)*t + b*b*f)
    residuals = [S.cancel(v.subs(chart, simultaneous=True)) for v in F]
    assert residuals[0] == residuals[1] == 0
    assert S.cancel(residuals[2] - b*d*polynomial/D**2) == 0
    J = F.jacobian(X)
    det = S.cancel(J.det().subs(chart, simultaneous=True))
    assert S.cancel(D**3*det + b*d*D*(S.diff(polynomial, t)*D
                    - 2*polynomial*S.diff(D, t))) == 0
    # A strictly negative cubic leading term bounds distinct real roots by three.
    # At an equilibrium, det J = -y Q'(t); exponential stability requires Q'>0.
    assert S.expand(S.Poly(polynomial, t).LC() + e*a*(a+h)) == 0
    values = list(map(S.Rational, cert['parameters_abcdefh']))
    assert len(values) == 7 and all(v > 0 for v in values)
    params = dict(zip((*K, h), values))
    p = S.Poly(polynomial.subs(params), t)
    assert list(map(str, p.all_coeffs())) == cert['q_coefficients_descending']
    pp = list(map(Q, reversed(cert['q_coefficients_descending'])))
    seq = R.sturm(pp)
    assert len(seq[-1]) == 1  # no repeated roots
    threshold = max(Q(0), Q(str(((c*d-e*b)/(e*a)).subs(params))))
    assert str(threshold) == cert['positive_branch_threshold']
    assert R.variation_at(seq, threshold) - R.variation_infinity(seq) == 3
    assert p.count_roots(S.Rational(threshold.numerator, threshold.denominator), S.oo) == 3

    def interval(expr, box):
        num, den = S.cancel(expr).as_numer_denom()
        nc = list(map(lambda q: Q(str(q)), reversed(S.Poly(num, t).all_coeffs())))
        dc = list(map(lambda q: Q(str(q)), reversed(S.Poly(den, t).all_coeffs())))
        value = R.irational(nc, dc, box)
        assert value is not None
        return value

    numeric = {v: S.cancel(expr.subs(params)) for v, expr in chart.items()}
    coeffs = J.subs(params).charpoly().all_coeffs()[1:]
    b1, b2, b3 = coeffs
    hurwitz = [S.cancel(q.subs(numeric, simultaneous=True))
               for q in [b1, b2, b3, b1*b2-b3]]
    out = []
    previous = threshold
    for root in cert['roots']:
        box = tuple(Q(int(q['numerator']), int(q['denominator'])) for q in root['t_interval'])
        assert previous < box[0] < box[1]
        assert all(R.evaluate(pp, q) != 0 for q in box)
        assert R.count(seq, *box) == root['sturm_roots_in_interval'] == 1
        assert root['multiplicity'] == 1
        previous = box[1]
        xyz = [interval(numeric[v], box) for v in X]
        assert all(R.interval_sign(q) == 1 for q in xyz)
        signs = [R.interval_sign(interval(expr, box)) for expr in hurwitz]
        assert signs == root['hurwitz_signs'] and all(signs)
        direct = direct_intervals(row, list(map(Q, cert['parameters_abcdefh'][:6])),
                                  Q(cert['parameters_abcdefh'][6]), xyz)
        assert [R.interval_sign(direct[k]) for k in ['b1', 'b2', 'b3', 'H2']] == signs
        stable = all(s == 1 for s in signs)
        assert stable == root['exponentially_stable']
        out.append({'t_interval': list(map(str, box)), 'hurwitz_signs': signs,
                    'exponentially_stable': stable})
    assert len(out) == cert['positive_equilibria'] == 3
    assert sum(r['exponentially_stable'] for r in out) == cert['exponentially_stable_positive_equilibria'] == 1
    return {'status': 'PASS', 'positive_equilibria': 3, 'exponentially_stable_equilibria': 1,
            'symbolic_identities': True, 'roots': out}
