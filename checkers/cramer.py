"""Exact certificate recheck using a separate sparse rational-polynomial engine.
No SymPy import, no solver, and no use of author stability flags.
"""
from fractions import Fraction as Q
import ast,itertools

ZERO=(0,)*7
def clean(p):return {m:c for m,c in p.items() if c}
def const(c):return {ZERO:c} if c else {}
def add(a,b):
    p=dict(a)
    for m,c in b.items():p[m]=p.get(m,0)+c
    return clean(p)
def scale(a,c):return clean({m:v*c for m,v in a.items()})
def sub(a,b):return add(a,scale(b,-1))
def mul(a,b):
    p={}
    for m,c in a.items():
        for n,d in b.items():
            k=tuple(x+y for x,y in zip(m,n));p[k]=p.get(k,0)+c*d
    return clean(p)
def power(a,n):
    assert isinstance(n,int) and 0<=n<=30
    p=const(1)
    for _ in range(n):p=mul(p,a)
    return p
def sign(p):
    if not p:return 0
    cs=list(p.values())
    if all(c>0 for c in cs):return 1
    if all(c<0 for c in cs):return -1
    return None
def divide(a,b):
    assert b;f=dict(a);q={};r={};lead=max(b);lc=b[lead];steps=0
    while f:
        steps+=1;assert steps<100000,'division iteration guard'
        m=max(f);c=f[m]
        if all(x>=y for x,y in zip(m,lead)):
            n=tuple(x-y for x,y in zip(m,lead));term={n:Q(c)/Q(lc)}
            q=add(q,term);f=sub(f,mul(term,b))
        else:r[m]=c;del f[m]
    return q,r
def parse(text,coordinate):
    names={f'k{i+1}':i for i in range(6)};names[coordinate]=6
    def walk(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,int):return const(node.value)
        if isinstance(node,ast.Name):
            m=[0]*7;m[names[node.id]]=1;return {tuple(m):1}
        if isinstance(node,ast.UnaryOp):
            assert isinstance(node.op,(ast.USub,ast.UAdd));return scale(walk(node.operand),-1 if isinstance(node.op,ast.USub) else 1)
        assert isinstance(node,ast.BinOp)
        a=walk(node.left)
        if isinstance(node.op,ast.Pow):
            assert isinstance(node.right,ast.Constant);return power(a,node.right.value)
        b=walk(node.right)
        if isinstance(node.op,ast.Add):return add(a,b)
        if isinstance(node.op,ast.Sub):return sub(a,b)
        if isinstance(node.op,ast.Mult):return mul(a,b)
        if isinstance(node.op,ast.Div):
            assert set(b)=={ZERO};return scale(a,1/Q(b[ZERO]))
        raise ValueError('unsupported polynomial syntax')
    return walk(ast.parse(text,mode='eval').body)
def det3(a):
    total={}
    for perm in itertools.permutations(range(3)):
        sg=(-1)**sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3));term=const(sg)
        for i,j in enumerate(perm):term=mul(term,a[i][j])
        total=add(total,term)
    return total
def coefficients(p):
    deg=max((m[-1] for m in p),default=0);out=[{} for _ in range(deg+1)]
    for m,c in p.items():n=m[:-1]+(0,);out[deg-m[-1]][n]=c
    return deg,out
def sign_patterns(signs):
    states={(0,0)}
    for sg in signs:
        new=set()
        for prev,v in states:
            for q in ([-1,0,1] if sg is None else [sg]):
                if q==0:new.add((prev,v))
                else:new.add((q,v+int(prev not in (0,q))))
        states=new
    return max(v for q,v in states)
def check(n,record):
    assert len(n['Y'])==len(n['N'])==3 and all(len(row)==6 for row in n['Y']+n['N'])
    assert all(n['Y'][i][j] in (0,1) and n['Y'][i][j]+n['N'][i][j] in (0,1) for i in range(3) for j in range(6))
    assert all(sum(n['Y'][i][j] for i in range(3))<=2 for j in range(6))
    rank_witness=None
    for cols in itertools.combinations(range(6),3):
        minor=det3([[const(n['N'][i][j]) for j in cols] for i in range(3)])
        if minor:rank_witness={'columns_one_based':[j+1 for j in cols],'determinant':minor[ZERO]};break
    assert rank_witness,'full-rank assumption failed'
    assert n['candidate_index']==record['candidate_index']
    c=record['certificate'];assert c and c['complete'];order=c['coordinate_order'];assert set(order)=={'x','y','z'}
    t=c['coordinate'];assert order[2]==t
    indices=[['x','y','z'].index(a) for a in order];sg_coord=(-1)**sum(indices[i]>indices[j] for i in range(3) for j in range(i+1,3))
    assert sg_coord==c['coordinate_permutation_sign']
    T=[[int(q) for q in row] for row in c['row_transform']]
    detT=det3([[const(q) for q in row] for row in T]);assert set(detT)=={ZERO} and detT[ZERO]
    assert detT[ZERO]==int(c['row_transform_determinant'])
    F=[{} for _ in range(3)]
    for j in range(6):
        key=(n['Y'][indices[0]][j],n['Y'][indices[1]][j]);m=[0]*7;m[j]=1;m[6]=n['Y'][indices[2]][j]
        for i in range(3):F[i][key]=add(F[i].get(key,{}),{tuple(m):n['N'][i][j]})
    G=[]
    for row in T:
        out={}
        for i,w in enumerate(row):
            for key,p in F[i].items():out[key]=add(out.get(key,{}),scale(p,w))
        G.append(out)
    assert not G[0].get((1,1)) and not G[1].get((1,1))
    A=[[G[i].get(key,{}) for key in [(1,0),(0,1)]] for i in range(2)]
    b=[scale(G[i].get((0,0),{}),-1) for i in range(2)]
    D=sub(mul(A[0][0],A[1][1]),mul(A[0][1],A[1][0]))
    U=sub(mul(b[0],A[1][1]),mul(A[0][1],b[1]));V=sub(mul(A[0][0],b[1]),mul(b[0],A[1][0]))
    assert D and D==parse(c['D'],t),'D mismatch'
    assert U==parse(c['U'],t) and V==parse(c['V'],t),'Cramer numerator mismatch'
    cert=c['denominator_certificate'];sg=sign({'D':D,'U':U,'V':V,'U+V':add(U,V)}[cert['strict_polynomial']])
    assert sg in (-1,1) and sg==cert['sign']==c['D_sign_at_positive_equilibria'],'denominator sign certificate mismatch'
    P={}
    for (du,dv),coef in G[2].items():
        assert du+dv<=2;P=add(P,mul(coef,mul(power(U,du),mul(power(V,dv),power(D,2-du-dv)))))
    assert P
    poly=parse(c['Q'],t);L0=const(1)
    for item in c['removed_factors']:
        assert isinstance(item['power'],int) and item['power']>0
        f=parse(item['factor'],t);why=item['reason']
        factor_sign=sign(f)
        if why=='strict sign on positive parameters and coordinate':assert factor_sign in (-1,1) and factor_sign==item['sign']
        elif why.startswith('parameter-only'):
            raise AssertionError('uncertified parameter-only factor')
        elif why.startswith('factor of chart determinant'):
            quotient,remainder=divide(D,f);assert not remainder
        else:raise AssertionError('unknown discarded-factor reason')
        L0=mul(L0,power(f,item['power']))
    product=mul(poly,L0);assert product and max(product)==max(P)
    scalar=Q(P[max(P)])/Q(product[max(product)]);assert P==scale(product,scalar),'residual polynomial identity mismatch'
    degree,cs=coefficients(poly);signs=[sign(q) for q in cs];bound=sign_patterns(signs)
    assert degree==c['degree'] and signs==c['coefficient_signs_descending']
    assert bound==c['positive_root_bound'] and bound<=3
    nonzero=any(q not in (0,None) for q in signs);assert nonzero==c['nonzero_for_all_positive_parameters']
    assert nonzero
    assert degree in (3,4)
    if degree==4: assert signs[0]==-1 and signs[-1]==1
    return {'candidate_index':n['candidate_index'],'status':'PASS','degree':degree,
            'positive_equilibrium_bound':bound,'stoichiometric_rank_witness':rank_witness,
            'nonzero_all_positive_parameters':nonzero,'coefficient_signs':signs,
            'residual_scalar':str(scalar),'denominator_certificate':cert}
