"""expand.py CPHF_FILE q t OUT: Sherwood-Martirosyan-Colbourn expansion CPHF(n;k,q,t) -> CA(n(q^t-1)+1; t, k, q),
duplicate rows removed. Field tables as in cphf_sa.c (q prime, 4, 8, 9)."""
import sys, itertools
f, q, t, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
def tables(q):
    if q in (4, 8):
        poly = 7 if q == 4 else 11
        def mul(a, b):
            r = 0
            while b:
                if b & 1: r ^= a
                b >>= 1; a <<= 1
                if a & q: a ^= poly
            return r
        return (lambda a, b: a ^ b), mul
    if q == 9:
        add = lambda a, b: (a % 3 + b % 3) % 3 + 3 * ((a // 3 + b // 3) % 3)
        mul = lambda a, b: ((a % 3) * (b % 3) - (a // 3) * (b // 3)) % 3 + 3 * (((a % 3) * (b // 3) + (a // 3) * (b % 3)) % 3)
        return add, mul
    return (lambda a, b: (a + b) % q), (lambda a, b: a * b % q)
add, mul = tables(q)
R = [[tuple(int(ch) for ch in w) for w in l.split()] for l in open(f) if l.strip() and not l.startswith('#')]
k = len(R[0]); rows = [tuple([0] * k)]
for row in R:
    for beta in itertools.product(range(q), repeat=t):
        if not any(beta): continue
        r = []
        for vec in row:
            s = 0
            for b, x in zip(beta, vec): s = add(s, mul(b, x))
            r.append(s)
        rows.append(tuple(r))
seen = set(); U = []
for r in rows:
    if r not in seen: seen.add(r); U.append(r)
open(out, 'w').write('\n'.join(' '.join(map(str, r)) for r in U) + '\n')
print(len(rows), 'rows,', len(U), 'after removing repeats')
