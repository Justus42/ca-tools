import sys
A=[l.split() for l in open(sys.argv[1]) if l.strip()]
cols=[l.strip() for l in open(sys.argv[2]) if l.strip()]
for r in range(len(A)): print(' '.join(A[r]+[c[r] for c in cols]))
