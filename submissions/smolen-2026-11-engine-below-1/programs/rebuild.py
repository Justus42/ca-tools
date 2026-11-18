#!/usr/bin/env python3
"""Rebuilds the four arrays of this submission from the table's own arrays and checks their sha256 against the files
here (--write writes them). Run from the root of ca-tools: python3 submissions/smolen-2026-11-engine-below-1/programs/rebuild.py"""
import hashlib, os, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SUB = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(SUB)); ARR = os.path.join(ROOT, "table", "arrays")


def load(name):
    with open(os.path.join(ARR, name)) as f:
        return [list(map(int, l.split())) for l in f if l.strip()]


def cut(A, k):
    return [r[:k] for r in A]


def ck_doubling(A, B, v):
    out = [r + r for r in A]
    for d in range(1, v):
        out += [r + [(x + d) % v for x in r] for r in B]
    return out


def profile_product(A, i, j, B, p, q):
    def ren(A, i, j, vi, vj):
        R = [r[:] for r in A]
        for c in range(len(A[0])):
            perm = {A[i][c]: vi}
            if A[j][c] != A[i][c]:
                perm[A[j][c]] = vj
            src = [s for s in range(3) if s not in perm]
            dst = [s for s in range(3) if s not in perm.values()]
            perm.update(zip(src, dst))
            for r in range(len(A)):
                R[r][c] = perm[A[r][c]]
        return R
    A = ren(A, i, j, 0, 2); B = ren(B, p, q, 1, 2); k, l = len(A[0]), len(B[0])
    K2 = {c for c in range(k) if A[j][c] == 0}; L2 = {c for c in range(l) if B[q][c] == 1}
    cols = [(a, b) for a in range(k) for b in range(l) if not (a in K2 and b in L2)]
    rows = [[A[r][a] for a, b in cols] for r in range(len(A)) if r not in (i, j)]
    rows += [[B[r][b] for a, b in cols] for r in range(len(B)) if r not in (p, q)]
    rows.append([A[j][a] if a in K2 else B[q][b] if b in L2 else 2 for a, b in cols])
    return rows, len(K2), len(L2)


def text(X):
    return "".join(" ".join(map(str, r)) + "\n" for r in X)


def main():
    out = {}
    out["CA_28_3_56_2.txt"] = ck_doubling(cut(load("CA_20_3_28_2.txt"), 28), cut(load("CA_8_2_35_2.txt"), 28), 2)
    out["CA_29_3_64_2.txt"] = ck_doubling(load("CA_21_3_32_2.txt"), cut(load("CA_8_2_35_2.txt"), 32), 2)
    X, d1, d2 = profile_product(load("CA_24_2_209_3.txt"), 20, 21, load("CA_18_2_52_3.txt"), 0, 1)
    print("profile product of CA(24; 2, 209, 3) and CA(18; 2, 52, 3): rows agree in %d and %d columns, %d columns" % (d1, d2, len(X[0])))
    out["CA_39_2_10283_3.txt"] = X
    X, d1, d2 = profile_product(load("CA_27_2_436_3.txt"), 4, 5, load("CA_18_2_52_3.txt"), 0, 1)
    print("profile product of CA(27; 2, 436, 3) and CA(18; 2, 52, 3): rows agree in %d and %d columns, %d columns" % (d1, d2, len(X[0])))
    out["CA_42_2_21307_3.txt"] = X
    bad = 0
    for name, X in out.items():
        got = hashlib.sha256(text(X).encode()).hexdigest()
        p = os.path.join(SUB, name)
        if "--write" in sys.argv:
            open(p, "w").write(text(X))
        want = hashlib.sha256(open(p, "rb").read()).hexdigest()
        print("%s: %d x %d, sha256 %s %s" % (name, len(X), len(X[0]), got[:16], "matches the file" if got == want else "DIFFERS"))
        bad += got != want
    print("all four rebuilt byte for byte" if not bad else "%d differ" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
