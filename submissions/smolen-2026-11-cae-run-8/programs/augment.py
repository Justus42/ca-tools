#!/usr/bin/env python3
"""augment.py - covering arrays by the augmentation of Colbourn 2014 (Theorem 2.2, application A, tau = 2) from a Bush
orthogonal array of index one, with the direct quilting arrays of Lemmas 3.1 to 3.3.

  augment.py t k v BINARY OUT [N1QA]

t in 4..6, q = v - 1 a prime, k <= q + 1. BINARY is a CA(M; t, k, 2) (0/1 entries). N1QA is an N^(1)_{t,2}-quilting
array QA(R; t, k, 3) on symbols 0, 1, 2; without it the direct one of Lemma 3.1 (t = 4), 3.2 (t = 5) or 3.3 (t = 6) is
used. Rows written: rows of the OA with mu <= t-2 zeros, each zero set replaced by all 2^mu binary vectors; rows with
t-1 zeros, by the 2^(t-2) even binary vectors; for each new symbol s = 2..v-1 the quilting array with 2 renamed s; then
the binary array. N = sum_{mu<=t-2} rho_mu 2^mu + rho_{t-1} 2^(t-2) + (v-2) R + M.
"""
import itertools
import sys


def bush_oa(t, k, q):
    """all q^t rows of the Bush OA: polynomials of degree < t over GF(q), q prime, evaluated at 0..k-1 (and, when
    k = q + 1, the leading coefficient as the last column). The zero polynomial gives the all-zero row."""
    pts = list(range(min(k, q)))
    for coef in itertools.product(range(q), repeat=t):
        row = []
        for x in pts:
            s = 0
            for c in coef:
                s = (s * x + c) % q
            row.append(s)
        if k == q + 1:
            row.append(coef[0])
        yield row


def lemma_qa(t, k):
    """the direct N^(1)_{t,2}-QA on symbols 0, 1, 2 of Lemmas 3.1 (t=4), 3.2 (t=5), 3.3 (t=6)"""
    rows = []
    for g in range(k):
        others = [c for c in range(k) if c != g]
        if t == 4:
            rows.append([2 if c == g else 1 for c in range(k)])
            for h in others:
                rows.append([2 if c == g else (1 if c == h else 0) for c in range(k)])
        elif t == 5:
            for h in others:
                rows.append([2 if c == g else (1 if c == h else 0) for c in range(k)])
            for h in others:
                rows.append([2 if c == g else (0 if c == h else 1) for c in range(k)])
        elif t == 6:
            for a, b in itertools.combinations(others, 2):
                rows.append([2 if c == g else (0 if c in (a, b) else 1) for c in range(k)])
            for h in others:
                rows.append([2 if c == g else (1 if c == h else 0) for c in range(k)])
    if t == 6 and k == 7:
        for g in range(k):
            rows.append([2 if c == g else 1 for c in range(k)])
    return rows


def read(path):
    return [[int(x) for x in l.split()] for l in open(path) if l.strip()]


def build(t, k, v, binary, qa=None):
    q = v - 1
    if not all(q % d for d in range(2, q)) or k > q + 1:
        raise SystemExit("q = v - 1 must be a prime with k <= q + 1")
    qa = qa if qa is not None else lemma_qa(t, k)
    even = [list(b) for b in itertools.product((0, 1), repeat=t - 1) if sum(b) % 2 == 0]
    out, rho = [], [0] * (k + 1)
    for row in bush_oa(t, k, q):
        z = [i for i, x in enumerate(row) if x == 0]
        mu = len(z)
        rho[mu] += 1
        base = [x + 1 if x else 0 for x in row]
        if mu == k:
            continue
        if mu >= t:
            raise SystemExit("the OA has a row with %d zeros: not of index one" % mu)
        fills = even if mu == t - 1 else list(itertools.product((0, 1), repeat=mu))
        for f in fills:
            r = list(base)
            for i, b in zip(z, f):
                r[i] = b
            out.append(r)
    for s in range(2, v):
        for r in qa:
            out.append([s if x == 2 else x for x in r])
    out.extend(binary)
    return out, rho


def main():
    t, k, v = (int(x) for x in sys.argv[1:4])
    binary = read(sys.argv[4])
    qa = read(sys.argv[6]) if len(sys.argv) > 6 else None
    A, rho = build(t, k, v, binary, qa)
    with open(sys.argv[5], "w") as f:
        for r in A:
            f.write(" ".join(map(str, r)) + "\n")
    print("CA(%d; %d, %d, %d) written; rho = %s" % (len(A), t, k, v, rho[:t] + [rho[k]]))


if __name__ == "__main__":
    main()
