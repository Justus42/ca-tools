# expand.py GEN REPS N idx1 idx2 ... -> prints array (N rows) of the union of orbits, columns deduped up to relabel
import sys
gen,reps,N=sys.argv[1],sys.argv[2],int(sys.argv[3]); idx=list(map(int,sys.argv[4:]))
gens=[tuple(map(int,l.split()))[:N] for l in open(gen)]
idn=tuple(range(N)); G={idn}; fr=[idn]
while fr:
    nf=[]
    for g in fr:
        for h in gens:
            x=tuple(h[g[i]] for i in range(N))
            if x not in G: G.add(x); nf.append(x)
    fr=nf
R=[l.split() for l in open(reps)]
def norm(c):
    m={};o=[]
    for x in c:
        if x not in m: m[x]=len(m)
        o.append(m[x])
    return tuple(o)
cols=[]
for i in idx:
    m=[int(x) for x in R[i][:3]]
    c=[0 if m[0]>>r&1 else 1 if m[1]>>r&1 else 2 for r in range(N)]
    seen=set()
    for g in sorted(G):
        d=[0]*N
        for r in range(N): d[g[r]]=c[r]
        d=norm(d)
        if d not in seen: seen.add(d); cols.append(d)
for r in range(N): print(' '.join(str(c[r]) for c in cols))
