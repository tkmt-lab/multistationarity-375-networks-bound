"""Independent B3: exact elimination identities, Fraction Sturm and interval RH.

The second RH check differentiates raw N,Y monomials and evaluates interval
matrices directly; it does not reuse the symbolic characteristic coefficients.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,hashlib,json,sys,time
import sympy as S
import rational_polynomials as R
from symbolic_input import K,X,equations
from common import load,EXPECTED
x,y,z=X;a,b,c,d,e,f=K;h=S.Symbol('h',positive=True)

def coeff(expr):
    p=S.Poly(expr,z,domain=S.QQ)
    return R.trim([Q(str(p.nth(i))) for i in range(p.degree()+1)] if not p.is_zero else [0])

def rat(expr,P):
    n,dn=S.cancel(expr).as_numer_denom()
    return R.divide(coeff(n),P)[1],coeff(dn)

def ineg(v):return -v[1],-v[0]
def isub(v,w):return R.iadd(v,ineg(w))
def isum(vs):
    out=(Q(0),Q(0))
    for v in vs:out=R.iadd(out,v)
    return out
def iprod(vs):
    out=(Q(1),Q(1))
    for v in vs:out=R.imul(out,v)
    return out
def idet(M):
    return isum([iprod([M[0][0],M[1][1],M[2][2]]),iprod([M[0][1],M[1][2],M[2][0]]),iprod([M[0][2],M[1][0],M[2][1]]),
                 ineg(iprod([M[0][2],M[1][1],M[2][0]])),ineg(iprod([M[0][1],M[1][0],M[2][2]])),ineg(iprod([M[0][0],M[1][2],M[2][1]]))])

def direct_intervals(row,rates,hvalue,box):
    mat=[[(Q(0),Q(0)) for j in range(3)] for i in range(3)]
    for i in range(3):
        for j in range(3):
            terms=[]
            for r in range(6):
                coefficient=row['N'][i][r]*row['Y'][j][r]*rates[r]
                if not coefficient:continue
                factors=[(coefficient,coefficient)]
                for n in range(3):
                    exponent=row['Y'][n][r]-(n==j)
                    assert exponent>=0
                    factors.extend([box[n]]*exponent)
                terms.append(iprod(factors))
            mat[i][j]=isum(terms)
    mat[2][2]=R.iadd(mat[2][2],(-hvalue,-hvalue))
    b1=ineg(isum([mat[i][i] for i in range(3)]))
    b2=isum([isub(R.imul(mat[i][i],mat[j][j]),R.imul(mat[i][j],mat[j][i])) for i,j in [(0,1),(0,2),(1,2)]])
    b3=ineg(idet(mat));H=isub(R.imul(b1,b2),b3)
    return {'b1':b1,'b2':b2,'b3':b3,'H2':H}

def run(samples):
    start=time.monotonic();row=next(r for r in load() if r['candidate_index']==33449)
    F=S.Matrix(equations(row));F[2]-=h*z;J=F.jacobian(X)
    expected=S.Matrix([a*z+b*y-d*x,-b*y-c*y*z+e*x*z,-(a+h)*z+b*y-c*y*z+f*x*y])
    assert all(S.expand(q)==0 for q in F-expected)
    D=d*b+(d*c-b*e)*z
    P=S.expand((a+h)*D**2-a*e*z*(b-c*z)*D-a**2*e*f*z**2*(b+c*z))
    phi={x:a*z*(b+c*z)/D,y:a*e*z**2/D};Jphi=J.subs(phi)
    assert S.degree(P,z)<=3 and S.expand(P.subs(z,0)-(a+h)*d*d*b*b)==0
    assert S.expand(e*z*F[0]+d*F[1]-(a*e*z*z-D*y))==0
    assert S.cancel(F[0].subs(phi))==S.cancel(F[1].subs(phi))==0
    assert S.cancel(F[2].subs(phi)+z*P/D**2)==0
    assert S.cancel(D**2*Jphi.det()+z*D*S.diff(P,z)-P*(2*z*S.diff(D,z)-D))==0
    symbolic={'F':list(map(str,F)),'D':str(D),'phi':{str(k):str(v) for k,v in phi.items()},'P':str(P),
              'positive_constant_term':str(S.factor(P.subs(z,0))),
              'identities':['e*z*F1+d*F2 = a*e*z^2-D*y','F1(phi)=F2(phi)=0','F3(phi)=-z*P/D^2',
                            'D^2*detJ(phi)+z*D*Pprime-P*(2*z*Dprime-D)=0'],
              'global_stable_upper_bound':1,'proof_scope':'all seven strictly positive rates, including polynomial degree collapse and degenerate equilibria'}
    out={'source_sha256':EXPECTED,'symbolic':symbolic,'samples':[]}
    for sample in samples:
        rates=dict(zip(K,map(S.Rational,sample['kappa'])));rates[h]=S.Rational(sample['h'])
        pp=coeff(P.subs(rates));dd=coeff(D.subs(rates));sq=R.sturm(pp)
        assert len(sq[-1])==1
        seq,B,intervals=R.isolate_positive(pp)
        assert S.Poly(P.subs(rates),z).count_roots(0,S.oo)==len(intervals)
        numeric_phi={k:S.cancel(v.subs(rates)) for k,v in phi.items()};M=J.subs(rates).subs(numeric_phi)
        b1=S.cancel(-S.trace(M));b2=S.cancel(sum(M.extract(ids,ids).det() for ids in [(0,1),(0,2),(1,2)]));b3=S.cancel(-M.det());H2=S.cancel(b1*b2-b3)
        cp=M.charpoly().all_coeffs();assert cp[0]==1 and all(S.cancel(v-w)==0 for v,w in zip(cp[1:],[b1,b2,b3]))
        expressions={'x':numeric_phi[x],'y':numeric_phi[y],'b1':b1,'b2':b2,'b3':b3,'H2':H2}
        data={key:rat(value,pp) for key,value in expressions.items()}
        remainders=[]
        for eq in F.subs(rates).subs(numeric_phi):
            n,dn=S.cancel(eq).as_numer_denom();rem=R.divide(coeff(n),pp)[1];assert R.zero(rem);remainders.append(R.strings(rem))
        rec={'id':sample['id'],'kappa':sample['kappa'],'h':sample['h'],'P_coefficients_ascending':R.strings(pp),'D_coefficients_ascending':R.strings(dd),
             'sturm_chain':list(map(R.strings,seq)),'sturm_at_zero':R.variation_at(seq,Q(0)),'sturm_at_infinity':R.variation_infinity(seq),
             'cauchy_positive_bound':str(B),'distinct_positive_polynomial_roots':len(intervals),'sympy_positive_count':len(intervals),'square_free_gcd':'1',
             'ode_numerator_remainders':remainders,'expressions_mod_P':{k:{'numerator':R.strings(v[0]),'denominator':R.strings(v[1])} for k,v in data.items()},'roots':[]}
        for interval in intervals:
            for step in range(512):
                ds=R.interval_sign(R.ipoly(dd,interval))
                if ds<0:break
                evaluated={key:R.irational(*value,interval) for key,value in data.items()}
                signs={key:R.interval_sign(value) for key,value in evaluated.items()}
                ps=R.interval_sign(R.ipoly(R.derivative(pp),interval))
                if ds>0 and ps and all(signs.values()):
                    direct=direct_intervals(row,list(map(Q,sample['kappa'])),Q(sample['h']),[evaluated['x'],evaluated['y'],interval])
                    if all(R.interval_sign(v) for v in direct.values()):break
                interval=R.refine(pp,seq,interval)
            else:raise AssertionError('Interval verification did not finish')
            root={'z_interval':R.strings(interval),'sturm_variations':[R.variation_at(seq,t) for t in interval],'admissible':ds>0,'D_interval':R.strings(R.ipoly(dd,interval))}
            if ds>0:
                assert signs['x']==signs['y']==1 and signs['b3']==ps
                assert all(R.interval_sign(direct[key])==signs[key] for key in direct)
                first=[1,signs['b1'],signs['H2']*signs['b1'],signs['b3']]
                root.update({'value_intervals':{k:R.strings(v) for k,v in evaluated.items()},'signs':signs,'Pprime_sign':ps,'direct_matrix_intervals':{k:R.strings(v) for k,v in direct.items()},
                             'routh_first_column_signs':first,'right_half_plane_eigenvalues':R.variations(first),
                             'exponentially_stable':all(signs[k]>0 for k in ['b1','b2','b3','H2']),'nondegenerate':True})
            rec['roots'].append(root)
        rec['positive_equilibria']=sum(r['admissible'] for r in rec['roots'])
        rec['exponentially_stable_equilibria']=sum(r.get('exponentially_stable',False) for r in rec['roots'])
        out['samples'].append(rec)
    return out
