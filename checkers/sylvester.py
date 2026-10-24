"""Second B2 checker: direct substitution + explicit Sylvester determinants.

No resultant(), factor_list(), or first-checker functions are called. Coefficient
sign variations are enumerated, independently of the first checker's DP.
SymPy polynomial arithmetic is shared; this is not a second CAS or formal proof.
"""
from pathlib import Path
from itertools import permutations,product
from collections import Counter
import hashlib,json,time
import sympy as S
ROOT=Path(__file__).resolve().parent
K=S.symbols('k1:7',positive=True);X=S.symbols('x1:4',positive=True);ALL=K+X
names={str(x):x for x in ALL}
def parse(s):return S.sympify(s,locals=names)
def sign(poly):
    terms=S.Poly(S.expand(poly),*ALL).as_dict()
    values=[v for v in terms.values() if v]
    if not values:return 0
    if min(values)>0:return 1
    if max(values)<0:return -1
    return None
def variations(signs):
    choices=[[-1,0,1] if s is None else [s] for s in signs]
    best=0
    for ss in product(*choices):
        nz=[v for v in ss if v]
        best=max(best,sum(nz[t]!=nz[t+1] for t in range(len(nz)-1)))
    return best
def determinant(rows):
    size=len(rows);ans=0
    for p in permutations(range(size)):
        parity=sum(p[i]>p[j] for i in range(size) for j in range(i+1,size))%2
        ans+=(-1)**parity*S.prod(rows[i][p[i]] for i in range(size))
    return S.expand(ans)
def sylvester(h,g,v):
    hc=S.Poly(h,v).all_coeffs();gc=S.Poly(g,v).all_coeffs();m=len(hc)-1;n=len(gc)-1
    assert 0<m+n<=4
    matrix=[]
    for i in range(n):matrix.append([0]*i+hc+[0]*(n-1-i))
    for i in range(m):matrix.append([0]*i+gc+[0]*(m-1-i))
    assert all(len(row)==m+n for row in matrix)
    return determinant(matrix),m+n
def removed_product(entries):
    factor=1
    for entry in entries:
        p=parse(entry['factor']);assert sign(p)==entry['sign'] in (-1,1)
        assert isinstance(entry['multiplicity'],int) and entry['multiplicity']>0
        factor*=p**entry['multiplicity']
    return factor

def check(row,proof):
    candidate=row['candidate_index']
    F=[S.expand(sum(row['N'][i][r]*K[r]*S.prod(X[j]**row['Y'][j][r] for j in range(3)) for r in range(6))) for i in range(3)]
    basis=proof.get('equation_basis',[[1,0,0],[0,1,0],[0,0,1]])
    assert determinant(basis) in (-1,1)
    F=[S.expand(sum(basis[i][j]*F[j] for j in range(3))) for i in range(3)]
    assert sorted(proof['order'])==[0,1,2]
    i,j,k=proof['order'];u,v,w=X[i],X[j],X[k]
    pu=S.Poly(F[i],u);assert pu.degree()==1
    A=-pu.nth(1);B=pu.nth(0);assert sign(A)==1 and S.expand(A-parse(proof['positive_pivot']))==0
    pv,pg=S.Poly(F[j],u),S.Poly(F[k],u);assert pv.degree()<=1 and pg.degree()<=1
    h0=S.expand(A*pv.nth(0)+B*pv.nth(1));g0=S.expand(A*pg.nth(0)+B*pg.nth(1))
    h=parse(proof['fiber_polynomial']);flip=proof.get('fiber_sign_flip',1);assert flip in (-1,1)
    assert S.expand(h*removed_product(proof.get('fiber_removed_factors',[]))-flip*h0)==0
    g=parse(proof['second_polynomial']) if 'second_polynomial' in proof else g0
    assert S.expand(g*removed_product(proof.get('second_removed_factors',[]))-g0)==0
    ph=S.Poly(h,v);assert ph.degree()<=2
    sa,sc=sign(ph.nth(2)),sign(ph.nth(0))
    assert sa in (-1,0) and sc in (0,1) and (sa,sc)!=(0,0)
    det,size=sylvester(h,g,v);assert det!=0
    scalar=parse(proof['resultant_coefficient']);assert scalar.is_Rational and scalar!=0
    fact=scalar*removed_product(proof['nonvanishing_factors']);bound=0
    degrees=[]
    for entry in proof['root_factors']:
        factor=parse(entry['factor']);p=S.Poly(factor,w);assert p.degree()>0
        assert factor.free_symbols <= set(K+(w,))
        assert entry['multiplicity']>0;fact*=factor**entry['multiplicity']
        signs=[sign(c) for c in p.all_coeffs()];assert signs==entry['coefficient_signs'] and any(s in (-1,1) for s in signs)
        value=variations(signs);assert value==entry['positive_root_bound'];bound+=value;degrees.append(int(p.degree()))
    assert S.expand(det-fact)==0 and bound==proof['positive_equilibrium_bound']<=3
    return {'candidate_index':candidate,'status':'PASS','sylvester_size':size,'root_factor_degrees':degrees,'bound':bound}
