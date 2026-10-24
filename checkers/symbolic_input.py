"""Mass-action equations from the pinned reactant and stoichiometric matrices."""
import sympy as S
K=S.symbols("k1:7",positive=True)
X=S.symbols("x1:4",positive=True)
def equations(row):
    y,n=S.Matrix(row['Y']),S.Matrix(row['N'])
    assert y.shape==n.shape==(3,6)
    assert all(q in (0,1) for q in y) and all(q in (0,1) for q in y+n)
    assert all(sum(y[:,j])<=2 for j in range(6))
    assert any(sum(y[:,j])==2 for j in range(6))
    assert all(any(n[i,j]<0 for j in range(6)) for i in range(3))
    assert n.rank()==3
    rates=S.Matrix([K[j]*S.prod(X[i]**y[i,j] for i in range(3)) for j in range(6)])
    return tuple(S.expand(e) for e in n*rates)
