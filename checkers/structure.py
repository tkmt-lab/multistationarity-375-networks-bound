"""B1 from original Y,N: inflows and monomolecular net-production DAG."""
from common import load,validate_network
from itertools import combinations,permutations
from collections import Counter
import json,time

def det3(a):
    return sum((1 if sum(p[i]>p[j] for i in range(3) for j in range(i+1,3))%2==0 else -1)*
               a[0][p[0]]*a[1][p[1]]*a[2][p[2]] for p in permutations(range(3)))

def acyclic_kahn(edges):
    left=set(range(3))
    while left:
        sources=[v for v in left if not any(a in left and b==v for a,b in edges)]
        if not sources:return False
        left.difference_update(sources)
    return True

def acyclic_cycles(edges):
    return not any(all((p[i],p[(i+1)%len(p)]) in edges for i in range(len(p)))
                   for n in (1,2,3) for p in permutations(range(3),n))

def complex_name(v):
    return ' + '.join('X'+str(i+1) for i,c in enumerate(v) if c) or '0'

def run():
    start=time.monotonic(); records=[]
    for row in load():
        y,n=row['Y'],row['N']; validate_network(row) # shape, zero-one, quadratic; rank checked below
        assert any(det3([[n[i][j] for j in cols] for i in range(3)])!=0 for cols in combinations(range(6),3))
        reactions=[];inflows=[];edges=set()
        for j in range(6):
            reactant=[y[i][j] for i in range(3)]
            product=[y[i][j]+n[i][j] for i in range(3)]
            reactions.append(complex_name(reactant)+f' --k{j+1}--> '+complex_name(product))
            if sum(reactant)==0:inflows.append(j+1)
            if sum(reactant)==1:
                source=reactant.index(1)
                edges.update((source,i) for i in range(3) if n[i][j]>0)
        assert [r.replace(' ','') for r in reactions]==[r.replace(' ','') for r in row['reactions']]
        dag=acyclic_kahn(edges);assert dag==acyclic_cycles(edges)
        records.append({'candidate_index':row['candidate_index'],'matrix_rank':3,'inflow_count':len(inflows),
                        'monomolecular_net_production_DAG':dag,'selected':not inflows and dag})
    selected=sorted(r['candidate_index'] for r in records if r['selected'])
    counts=Counter((r['inflow_count']==0,r['monomolecular_net_production_DAG']) for r in records)
    result={'selected':selected,'matches_disclosed_claim':selected==[33449,239089],
            'definitions':{'inflow':'Y column sum is zero','edge':'Y column is e_i and N[j,column]>0: i -> j','DAG':'no directed cycle; retained catalyst does not produce a self-loop'},
            'all_author_reaction_strings_match_Y_and_N':True,'all_actual_matrix_ranks':3,
            'rank_field_used_as_matrix_rank':False,'stability_null_fields_used':False,
            'counts':[{'no_inflow':a,'DAG':b,'count':c} for (a,b),c in sorted(counts.items())],
            'rows':records,'elapsed_seconds':time.monotonic()-start}
    assert result['matches_disclosed_claim']
    result.pop('elapsed_seconds')
    return result
