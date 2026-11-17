"""laws.py - construction laws of the engine, each with its size rule AND its builder (F26: code, not arrays).
Every builder takes ingredient arrays (lists of rows, symbols 0..v-1) and returns the rows of the result.
All are published constructions; references are ids of ca-tools table/references.csv.
PRIVATE engine code (F24); the builders are also copied into submissions as the program of a result."""
import itertools, math

# ----------------------------------------------------------------------------------------------- small fields
def is_prime(n): return n > 1 and all(n % p for p in range(2, int(n ** .5) + 1))
def pp(v):
    for p in range(2, v + 1):
        if is_prime(p):
            x, e = p, 1
            while x < v: x *= p; e += 1
            if x == v: return p, e
            if v % p == 0: return None
    return None
def gf(q):
    """addition and multiplication tables of GF(q), q a prime power <= 64 (polynomial basis)"""
    p, e = pp(q)
    if e == 1:
        return [[(a + b) % q for b in range(q)] for a in range(q)], [[a * b % q for b in range(q)] for a in range(q)]
    polys = {4: [1, 1, 1], 8: [1, 1, 0, 1], 9: [2, 2, 1], 16: [1, 1, 0, 0, 1], 25: [2, 4, 1], 27: [1, 2, 0, 1], 32: [1, 0, 1, 0, 0, 1], 49: [3, 6, 1], 64: [1, 1, 0, 0, 0, 0, 1]}
    mod = polys[q]   # monic irreducible, coefficients low degree first (x^e term last)
    def dig(a): return [(a // p ** i) % p for i in range(e)]
    def num(d): return sum(x * p ** i for i, x in enumerate(d))
    def mul(a, b):
        A, B = dig(a), dig(b); r = [0] * (2 * e - 1)
        for i, x in enumerate(A):
            for j, y in enumerate(B): r[i + j] = (r[i + j] + x * y) % p
        for d in range(2 * e - 2, e - 1, -1):
            c = r[d]
            if c:
                for i in range(e + 1): r[d - e + i] = (r[d - e + i] - c * mod[i]) % p
        return num(r[:e])
    add = [[num([(x + y) % p for x, y in zip(dig(a), dig(b))]) for b in range(q)] for a in range(q)]
    return add, [[mul(a, b) for b in range(q)] for a in range(q)]

# ----------------------------------------------------------------------------------------------- builders
def cut(A, k): return [r[:k] for r in A]

def fuse(A, v_from, v_to):
    """CKRS 2010 Lemma 3.1, applied v_from - v_to times: CA(N; t, k, v+1) -> CA(N - 2; t, k, v)"""
    X = [list(r) for r in A]; vv = v_from
    while vv > v_to:
        top = vv - 1; Z, R0 = X[0], X[1]
        tau = lambda x, j: top if x == Z[j] else (Z[j] if x == top else x)
        R = [tau(x, j) for j, x in enumerate(R0)]
        Y = []
        for row in X[2:]:
            out = []
            for j, x in enumerate(row):
                y = tau(x, j)
                if y == top: y = R[j] if R[j] != top else 0
                out.append(y)
            Y.append(out)
        X = Y; vv -= 1
    return X

def derive(A, v):
    """a CA(N; t+1, k+1, v) -> CA(<= N/v; t, k, v): the rows with the rarest symbol in its column, that column removed"""
    best = None
    for c in range(len(A[0])):
        for s in range(v):
            n = sum(1 for r in A if r[c] == s)
            if best is None or n < best[0]: best = (n, c, s)
    _, c, s = best
    return [r[:c] + r[c + 1:] for r in A if r[c] == s]

def constant_row(A, r):
    """symbols permuted per column so that row r reads 0 everywhere"""
    Z = A[r]
    return [[0 if x == Z[j] else (Z[j] if x == 0 else x) for j, x in enumerate(row)] for row in A]

def direct_product(A, B, cA=None, cB=None):
    """strength 2 direct product (CMMSSY 2006), with the generalized saving of Colbourn and Torres-Jimenez 2013
    Cor 4.3 for one constant row on each side (row cA of A and cB of B made all-0; the duplicate constant row
    dropped): CA(N1 + N2 - 1; 2, k1 k2, v), or N1 + N2 when no constant rows are given"""
    if cA is not None: A = constant_row(A, cA)
    if cB is not None: B = constant_row(B, cB)
    k1, k2 = len(A[0]), len(B[0])
    out = [[a[i] for i in range(k1) for _ in range(k2)] for a in A]
    cz = {row[0] for row in A if len(set(row)) == 1}
    for b in B:
        if len(set(b)) == 1 and b[0] in cz: continue
        out.append([b[j] for _ in range(k1) for j in range(k2)])
    return out

def add_column(A, C, v):
    """CKRS 2010 Thm 3.2 (8), one column: CA(N; t, k-1, v) and CA(M; t-2, k-2, v) give
    CA(N + v(v-1) M; t, k, v): the last column duplicated; for every ordered pair a != b, the strength t-2 array on
    the other k-2 columns with the two copies set to a and b. For t = 3, C is the strength-1 array: v constant rows."""
    k1 = len(A[0]); out = [r + [r[-1]] for r in A]
    for a in range(v):
        for b in range(v):
            if a == b: continue
            for c in C: out.append(list(c[:k1 - 1]) + [a, b])
    return out

def strength1(k, v): return [[s] * k for s in range(v)]

def composition(A, B, v2):
    """CKRS 2010 (3): CA(N1; t, k, v1) x CA(N2; t, k, v2) -> CA(N1 N2; t, k, v1 v2), symbol x1 v2 + x2"""
    return [[x * v2 + y for x, y in zip(a, b)] for a in A for b in B]

def ck_doubling(A, B, v):
    """Chateauneuf-Kreher doubling (CCL 2008 Thm 2): CA(N; 3, h, v), CA(M; 2, h, v) -> CA(N + (v-1)M; 3, 2h, v):
    [A | A] and, for d = 1..v-1, [B | B + d mod v]"""
    out = [list(r) + list(r) for r in A]
    for d in range(1, v):
        for r in B: out.append(list(r) + [(x + d) % v for x in r])
    return out

def cmtw34(A, B, q):
    """Colbourn, Martirosyan, Trung van, Walker 2006 Thm 3.4 (q a prime power): CA(N; 3, h, q), CA(M; 2, h, q) ->
    CA(N + (q-1)M + q^3 - q^2; 3, q h, q). Columns (i, g), i < h, g in GF(q). Rows: A copied into every block g;
    for lambda != 0, B + lambda g in column (i, g); for a != 0, b, c: a g^2 + b g + c in every column (i, g)."""
    add, mul = gf(q); h = len(A[0])
    out = [[r[i] for g in range(q) for i in range(h)] for r in A]
    for lam in range(1, q):
        for r in B: out.append([add[r[i]][mul[lam][g]] for g in range(q) for i in range(h)])
    for a in range(1, q):
        for b in range(q):
            for c in range(q):
                out.append([add[add[mul[a][mul[g][g]]][mul[b][g]]][c] for g in range(q) for i in range(h)])
    return out

# ----------------------------------------------------------------------------------------------- registry
# name: (references, short description)
# ------------------------------------------------------------------------------- profile product (W17), v = 3
def min_agreement(A):
    """two rows of A that agree in the fewest columns: (d, i, j)"""
    best = None
    for i in range(len(A)):
        for j in range(i + 1, len(A)):
            d = sum(1 for x, y in zip(A[i], A[j]) if x == y)
            if best is None or d < best[0]: best = (d, i, j)
    return best

def profile_product(A, i, j, B, p, q):
    """Colbourn and Torres-Jimenez 2013, Thm 4.2 / Cor 4.5, for 3 symbols (own code, as pprod.py of the submission
    smolen-2026-11-t2v3-26rows): A = CA(N;2,k,3) whose rows i, j agree in d1 columns (set K2), B = CA(M;2,l,3) whose
    rows p, q agree in d2 columns (set L2). Rename per column so that A[i] = 0 everywhere and A[j] = 2 off K2,
    B[p] = 1 everywhere and B[q] = 2 off L2. Drop rows A[i] and B[p], merge A[j] and B[q] into one row, drop the
    columns K2 x L2: CA(N + M - 3; 2, k l - d1 d2, 3)."""
    def ren(A, i, j, vi, vj):
        B = [r[:] for r in A]
        for c in range(len(A[0])):
            perm = {A[i][c]: vi}
            if A[j][c] != A[i][c]: perm[A[j][c]] = vj
            src = [s for s in range(3) if s not in perm]; dst = [s for s in range(3) if s not in perm.values()]
            for s_, d_ in zip(src, dst): perm[s_] = d_
            for r in range(len(A)): B[r][c] = perm[A[r][c]]
        return B
    A = ren(A, i, j, 0, 2); B = ren(B, p, q, 1, 2); k, l = len(A[0]), len(B[0])
    K2 = set(c for c in range(k) if A[j][c] == 0); L2 = set(c for c in range(l) if B[q][c] == 1)
    cols = [(a, b) for a in range(k) for b in range(l) if not (a in K2 and b in L2)]
    rows = [[A[r][a] for a, b in cols] for r in range(len(A)) if r not in (i, j)]
    rows += [[B[r][b] for a, b in cols] for r in range(len(B)) if r not in (p, q)]
    rows.append([A[j][a] if a in K2 else B[q][b] if b in L2 else 2 for a, b in cols])
    return rows

# ---------------------------------------------------- CMTW 2006, strength 4 (W21): Lemma 4.8 / Cor 4.9, Thm 4.11, Thm 4.13
def dca2(k, v):
    """a DCA(m (v - 1); 2, k, v) over the additive group of GF(v), m = ceil(log_v k): column = a vector x of GF(v)^m,
    rows (c, lam != 0) with entry lam * x_c. Two columns differ in some coordinate c, where lam (x_c - y_c) runs
    over every nonzero element."""
    add, mul = gf(v); m = 1
    while v ** m < k: m += 1
    X = [[(j // v ** c) % v for c in range(m)] for j in range(k)]
    return [[mul[lam][X[j][c]] for j in range(k)] for c in range(m) for lam in range(1, v)]

def cod_from_ca(A):
    """a COD(N - 1; 2, k, v) from a CA(N; 2, k, v): rename the symbols in each column so that row 0 is constant 0,
    and delete it (the remaining rows show every non-constant pair)."""
    out = []
    for r in A[1:]:
        out.append([0 if x == A[0][c] else (A[0][c] if x == 0 else x) for c, x in enumerate(r)])
    return out

def _bush_rows(v, deg, cond):
    """rows of the Bush OA(v^deg; deg, v, v) (polynomials of degree < deg evaluated at every field element) whose
    coefficient vector satisfies cond"""
    import itertools
    add, mul = gf(v); rows = []
    for beta in itertools.product(range(v), repeat=deg):          # beta[0] + beta[1] g + ...
        if not cond(beta): continue
        row = []
        for g in range(v):
            acc = 0; pw = 1
            for b in beta: acc = add[acc][mul[b][pw]]; pw = mul[pw][g]
            row.append(acc)
        rows.append(row)
    return rows

def cmtw48(C4, C3, Acod, v):
    """CMTW 2006 Lemma 4.8 with Corollary 4.9 (v a prime power, k >= 4): C4 = CA(4, k, v), C3 = CA(3, k, v),
    Acod = COD(2, k, v). Rows [C4 | C4]; [C3 | C3 + d] for d = 1..v-1; and the array for two twin pairs (the QCA
    of the paper, v^2 |Acod| rows), built as in Theorems 2.3 / 2.5 and Lemma 4.5: with B = the Bush OA(v^2; 2, v, v)
    without its v constant rows, the rows (r, n) carry the pair (a, B[n][a]), a = Acod[r][c], and for every l < v
    the rows (l, m) carry (l, Acod[m][c]); a pair (a, b) is written a on the first copy and a + b on the second.
    (With this way of writing the pair, the twin patterns not yet covered by the first two blocks are exactly
    those with different b, which these rows give; checked exactly in tests.)
    CA(N4 + (v - 1) N3 + v^2 |Acod|; 4, 2k, v)."""
    B = _bush_rows(v, 2, lambda b: b[1] != 0)
    out = [list(r) + list(r) for r in C4]
    for d in range(1, v):
        for r in C3: out.append(list(r) + [(x + d) % v for x in r])
    for r in Acod:
        for n in B: out.append(list(r) + [(a + n[a]) % v for a in r])
    for l in range(v):
        for m in Acod: out.append([l] * len(m) + [(l + x) % v for x in m])
    return out

def cmtw413(C4, C3, C2cod, v):
    """CMTW 2006 Theorem 4.13 (v >= 4 a prime power) and Theorem 4.11 (v = 3): C4 = CA(4, k, v), C3 = CA(3, k, v),
    C2cod = COD(2, k, v^2). Columns (f, h), f < k, h in GF(v). Blocks:
    G1 C4[f]; G2 C3[f] + s h (s != 0); G3 B3[h] + D[f] (B3 = Bush cubic-free rows with a nonzero quadratic term,
    D = dca2(k, v)); G4 every v^2 symbol of C2cod replaced by a row of the Bush OA(v^2; 2, v, v);
    G5 B[h], B = the Bush rows of degree < 4 with a nonzero quadratic or cubic term (v >= 4), or B3 again (v = 3).
    CA(N4 + (v-1) N3 + (v^3 - v^2) |D| + N2 + (v^4 - v^2 or 18); 4, v k, v)."""
    add, mul = gf(v); k = len(C4[0]); cols = [(f, h) for h in range(v) for f in range(k)]
    D = dca2(k, v); B3 = _bush_rows(v, 3, lambda b: b[2] != 0); A2 = _bush_rows(v, 2, lambda b: True)
    B5 = B3 if v == 3 else _bush_rows(v, 4, lambda b: (b[2], b[3]) != (0, 0))
    out = [[r[f] for f, h in cols] for r in C4]
    for s in range(1, v):
        for r in C3: out.append([add[r[f]][mul[s][h]] for f, h in cols])
    for d in D:
        for b in B3: out.append([add[b[h]][d[f]] for f, h in cols])
    for r in C2cod: out.append([A2[r[f]][h] for f, h in cols])
    for b in B5: out.append([b[h] for f, h in cols])
    return out

# ----------------------------------------------------------------------- projection (W29): Colbourn 2008, Theorem 2.3
def projection(q, t):
    """Colbourn 2008 (Strength two covering arrays: existence tables and projection), Theorem 2.3, generalising
    Stevens, Ling and Mendelsohn 2002: q a prime power, 1 <= t <= q - 2. From the OA(q^2; 2, q+1, q) with rows (i, j),
    entry i*l + j in column l of GF(q) and i in the last column, the t rows (0, j0) are projected: each is deleted,
    its symbol leaves every column, and a new column records, for the first s = q - t columns l, the rows that had
    j0 in column l (those rows take the other symbols in column l). A CA(q^2 - t; 2, q + 1 + t, q - t) with q - t
    constant rows (the rows (0, j) not projected, completed)."""
    add, mul = gf(q); s = q - t; STAR = -1
    T = list(range(q - t, q))                                  # projected rows (0, j0), j0 in T; symbols T leave columns l < q
    rows = [(i, j) for i in range(q) for j in range(q)]
    A = {r: [add[mul[r[0]][l]][r[1]] for l in range(q)] + [r[0]] for r in rows}
    new = {r: [STAR] * t for r in rows}
    keep = [x for x in range(q) if x not in T]                 # the q - t symbols kept in columns l < q
    for n, j0 in enumerate(T):
        for li in range(s):                                    # class C_li: rows (a, b), a != 0, with j0 in column li
            C = [r for r in rows if r[0] != 0 and add[mul[r[0]][li]][r[1]] == j0]
            for m, r in enumerate(C):
                new[r][n] = li
                A[r][li] = keep[m] if m < len(keep) else STAR
        for r in rows:                                         # j0 leaves the columns outside the first s
            for l in range(s, q):
                if A[r][l] == j0: A[r][l] = STAR
    keep_inf = list(range(1, s + 1))                           # last column: keep q - t of the nonzero symbols
    out = []
    for r in rows:
        if r[0] == 0 and r[1] in T: continue                   # the projected rows are deleted
        row = A[r] + new[r]
        if r[0] == 0: row = row[:q + 1] + [keep.index(r[1])] * t          # near-constant rows: constant on the new columns
        row[q] = keep_inf.index(row[q]) if row[q] in keep_inf else STAR
        for l in range(q): row[l] = keep.index(row[l]) if row[l] in keep else STAR
        out.append([x if x != STAR else 0 for x in row])
    return out

REFS = {
    "cut": ("", "first k columns of a wider array"),
    "fuse": ("fuse-ckrs2010", "fusing symbols, CKRS 2010 Lemma 3.1"),
    "derive": ("fuse-ckrs2010", "derived array, CKRS 2010 (7)"),
    "dp2": ("product-cmmssy2006;pca-ct2013", "direct product with constant rows, Colbourn-Torres-Jimenez 2013 Cor 4.3"),
    "add1": ("fuse-ckrs2010", "one column added, CKRS 2010 Thm 3.2"),
    "comp": ("fuse-ckrs2010", "composition of alphabets, CKRS 2010 (3)"),
    "ck": ("ck-ck2002", "Chateauneuf-Kreher doubling"),
    "cmtw34": ("roux-cmtw2006", "CMTW 2006 Thm 3.4"),
    "hartman4": ("roux-cmtw2006", "doubling at strength 4, Hartman (CMTW 2006 Theorem 4.7)"),
    "kroux": ("sa-ccl2008", "k-ary Roux, Cohen-Colbourn-Ling 2008 Theorem 3 (DCA from the field)"),
    "od": ("sa-ccl2008", "ordered design plus binary patches, Cohen-Colbourn-Ling 2008 Construction 1"),
    "phf": ("power-ct2010", "perfect hash family (Reed-Solomon) with a strength t array in every row"),
    "pdouble": ("ck-ck2002;binary-ks1973", "partial doubling with Kleitman-Spencer helper rows (twin law)"),
    "cmtw48": ("roux-cmtw2006", "Colbourn, Martirosyan, Tran van Trung and Walker 2006, Lemma 4.8 / Corollary 4.9 (strength 4 doubling)"),
    "cmtw413": ("roux-cmtw2006", "Colbourn, Martirosyan, Tran van Trung and Walker 2006, Theorem 4.13 (Theorem 4.11 for 3 symbols)"),
    "proj": ("proj-c2008", "projection of the orthogonal array OA(q^2; 2, q+1, q) (Colbourn 2008, Theorem 2.3)"),
    "pprod": ("pca-ct2013", "profile product of Colbourn and Torres-Jimenez 2013 (Thm 4.2 / Cor 4.5), 3 symbols"),
    "ctj": ("pca-ct2013;product-cmmssy2006", "product of Colbourn and Torres-Jimenez 2013 Cor 4.3 (rows differing in every column removed)"),
    "aug1": ("new https://doi.org/10.1142/S1793830914500347;oa-bush1952", "augmentation of an orthogonal array of index one, Colbourn 2014 Theorem 2.3 (2.1)"),
    "aug2": ("new https://doi.org/10.1142/S1793830914500347;oa-bush1952", "augmentation of an orthogonal array of index one, Colbourn 2014 Theorem 2.3 (2.2)"),
    "augq": ("new https://doi.org/10.1142/S1793830914500347;oa-bush1952", "augmentation of an orthogonal array of index one with quilting arrays, Colbourn 2014 Theorem 2.2"),
    "augB": ("new https://doi.org/10.1142/S1793830914500347;oa-bush1952", "augmentation of an orthogonal array of index one with quilting arrays for classes of new symbols, Colbourn 2014 Theorem 2.2 (application B)"),
}

# ----------------------------------------------------------------------------------------------- CTJ product
def disagreeing_rows(A, cap):
    """a largest-found set of rows that pairwise differ in every column (greedy over every start row)"""
    best = []
    for s in range(len(A)):
        S = [s]
        for r in range(len(A)):
            if r in S: continue
            if all(all(x != y for x, y in zip(A[r], A[q])) for q in S): S.append(r)
            if len(S) >= cap: break
        if len(S) > len(best): best = S
        if len(best) >= cap: break
    return best

def _relabel(M, S, base, v):
    k = len(M[0]); maps = []
    for j in range(k):
        perm = {}
        for r, s in enumerate(S): perm.setdefault(M[s][j], base + r)
        tgt = set(perm.values()); rs = [x for x in range(v) if x not in perm]; rt = [y for y in range(v) if y not in tgt]
        for x, y in zip(rs, rt): perm[x] = y
        maps.append(perm)
    return [[maps[j][x] for j, x in enumerate(row)] for row in M]

def ctj_product(A, B, v, S=None, T=None):
    """Colbourn and Torres-Jimenez 2013, Cor 4.3 (the product-ctj-1 construction of ca-tools): with s rows of A and
    r rows of B that pairwise differ in every column, s + r <= v, CA(N1 + N2 - (s + r); 2, k1 k2, v): the s rows of A
    become constant rows 0..s-1, the r rows of B constant rows s..s+r-1, all s + r rows are removed, and the rest
    is the direct product."""
    if S is None: S = disagreeing_rows(A, v - 1)
    if T is None: T = disagreeing_rows(B, v - len(S))
    A2 = _relabel(A, S, 0, v); B2 = _relabel(B, T, len(S), v); k1, k2 = len(A[0]), len(B[0])
    rows = [[a[i] for i in range(k1) for _ in range(k2)] for x, a in enumerate(A2) if x not in set(S)]
    rows += [b * k1 for y, b in enumerate(B2) if y not in set(T)]
    return rows

# ----------------------------------------------------------------------------------------------- direct constructions
def ksk_k(N):
    """columns of the Kleitman-Spencer / Katona binary strength-2 array on N rows"""
    import math
    return math.comb(N - 1, (N - 1) // 2 + 1) if N >= 4 else (1 if N == 4 else 0)

def ksk(N, k=None):
    """W1: binary CA(N; 2, C(N-1, floor((N-1)/2)+1), 2): columns = sets of size floor((N-1)/2)+1 of rows 1..N-1"""
    import itertools
    m = (N - 1) // 2 + 1; cols = []
    for S in itertools.combinations(range(1, N), m):
        cols.append(S)
        if k and len(cols) >= k: break
    return [[1 if r in S else 0 for S in cols] for r in range(N)]

def bush(q, t, k=None):
    """W2: Bush / Bose OA(q^t; t, q+1, q) for t <= q (columns: field points, then the top coefficient), q columns if t > q"""
    add, mul = gf(q); rows = []
    for co in itertools.product(range(q), repeat=t):
        r = []
        for x in range(q):
            s, xp = 0, 1
            for c in co: s = add[s][mul[c][xp]]; xp = mul[xp][x]
            r.append(s)
        if t <= q: r.append(co[-1])
        rows.append(r)
    return cut(rows, k) if k else rows

def weight_sets(k, t):
    """cheapest set of weights W (sum of C(k, w)) such that every interval [w, w + k - t], w = 0..t, meets W (exact DP)"""
    d = k - t; memo = {}
    def f(w):
        if w > t: return (0, [])
        if w in memo: return memo[w]
        best = None
        for x in range(w, w + d + 1):
            c, L = f(x + 1); c += math.comb(k, x)
            if best is None or c < best[0]: best = (c, [x] + L)
        memo[w] = best; return best
    return f(0)[1]

def weight_class(k, t):
    """W3: binary vectors whose weight lies in weight_sets(k, t): a CA(sum C(k, W); t, k, 2)"""
    W = set(weight_sets(k, t))
    return [[(m >> j) & 1 for j in range(k)] for m in range(2 ** k) if bin(m).count("1") in W]

def weight_class_N(k, t):
    import math
    return sum(math.comb(k, w) for w in weight_sets(k, t) if w <= k)

def pgl2(q):
    """the q^3 - q elements of PGL(2, q) acting on the projective line (points 0..q-1, infinity = q)"""
    add, mul = gf(q); inv = [0] + [next(b for b in range(1, q) if mul[a][b] == 1) for a in range(1, q)]
    neg = [next(b for b in range(q) if add[a][b] == 0) for a in range(q)]
    def sub(a, b): return add[a][neg[b]]
    seen = set(); rows = []
    for a, b, c, d in itertools.product(range(q), repeat=4):
        if sub(mul[a][d], mul[b][c]) == 0: continue
        img = []
        for x in range(q + 1):
            if x == q: num, den = a, c
            else: num, den = add[mul[a][x]][b], add[mul[c][x]][d]
            img.append(q if den == 0 else mul[num][inv[den]])
        tup = tuple(img)
        if tup not in seen: seen.add(tup); rows.append(list(tup))
    return rows

def ordered_design(q, B, k=None):
    """W13, Cohen-Colbourn-Ling 2008 Construction 1: v = q + 1, k <= q + 1: PGL(2,q) on the projective line (every
    triple of distinct symbols once on every 3 columns) plus, for every pair of symbols {x, y}, the binary
    CA(N2; 3, q+1, 2) B with its row 0 made all-0 and then removed, 0 -> x and 1 -> y, oriented so that every symbol
    is the '1' symbol of some pair: q^3 - q + C(q+1, 2)(N2 - 1) rows."""
    v = q + 1; k = k or v; B = constant_row(cut(B, k), 0)[1:]
    out = [r[:k] for r in pgl2(q)]
    for x in range(v):
        for y in range(x + 1, v):
            lo, hi = (y, x) if (x == 0 and y == v - 1) else (x, y)     # pair (0, q): 0 is the '1' symbol
            for b in B: out.append([hi if z else lo for z in b])
    return out

def turan(t, v):
    """edges of the Turan graph T(t, v): the most pairs of t positions with unequal values when t values come from v symbols"""
    a, r = divmod(t, v); sizes = [a + 1] * r + [a] * (v - r)
    return (t * t - sum(x * x for x in sizes)) // 2

def power_phf(q, e, t, C, v, k=None, M=None):
    """W23 (perfect hash family form): columns = polynomials of degree < e over GF(q) (q^e columns), rows = for each of
    M = C(t,2)(e-1)+1 evaluation points the rows of a CA(x; t, q, v) C (its row 0 made all-0; the all-0 row kept
    once): CA(M (x - 1) + 1; t, q^e, v). Two polynomials agree in at most e-1 points, so some point separates all t."""
    import math
    M = M or (turan(t, v) * (e - 1) + 1)   # only pairs with unequal targets need separating (DHF / Power CT form)
    if M > q: return None
    add, mul = gf(q); C0 = constant_row(C, 0); polys = list(itertools.product(range(q), repeat=e))
    if k: polys = polys[:k]
    out = [[0] * len(polys)]
    for x in range(M):
        vals = []
        for co in polys:
            s, xp = 0, 1
            for c in co: s = add[s][mul[c][xp]]; xp = mul[xp][x]
            vals.append(s)
        for row in C0[1:]: out.append([row[a] for a in vals])
    return out

def partial_doubling(A, r, s):
    """W19 (own, item120; Chateauneuf-Kreher / Roux family): binary CA(N0; 3, k0, 2) A, r helper rows: s columns get a
    twin; on the helper rows twinned column i carries vector F_i, its twin the complement, every other column the
    common vector p; F_1..F_s, p pairwise qualitatively independent on r rows (Kleitman-Spencer family).
    CA(N0 + r; 3, k0 + s, 2) when s + 1 <= C(r-1, floor((r-1)/2)+1)."""
    fam = [list(c) for c in zip(*ksk(r))]       # columns of the KSK array on r rows, each a vector of length r
    if s + 1 > len(fam): return None
    k0 = len(A[0]); p = fam[s]
    top = [row + [row[i] for i in range(s)] for row in A]
    bot = []
    for j in range(r):
        bot.append([fam[i][j] if i < s else p[j] for i in range(k0)] + [1 - fam[i][j] for i in range(s)])
    return top + bot

# ----------------------------------------------------------------------------------------------- cyclotomy, Paley
def primitive_root(p):
    fac = [f for f in range(2, p) if (p - 1) % f == 0 and is_prime(f)]
    for g in range(2, p):
        if all(pow(g, (p - 1) // f, p) != 1 for f in fac): return g
    return 1

def cyclotomic(p, v, k=None, diag=0):
    """W12 (Colbourn 2010): p prime, p = 1 mod v. Rows and columns are GF(p); entry = the cyclotomic class of c - r
    (discrete log mod v), diag on c = r. For v = 2 this is the Paley circulant (W11). Strength is checked, not assumed."""
    g = primitive_root(p); cls = [0] * p; x = 1
    for e in range(p - 1): cls[x] = e % v; x = x * g % p
    k = k or p
    return [[diag if c == r else cls[(c - r) % p] for c in range(k)] for r in range(p)]

def cyclo_primes(v, lo, hi):
    return [p for p in range(max(lo, 3), hi + 1) if is_prime(p) and (p - 1) % v == 0]

def cyclotomic_shifted(p, v, k=None, diag=0):
    """W12, Colbourn 2010 form with the point at infinity: for every shift s in Z_v the cyclotomic p x p array plus s,
    and an extra column equal to s: v p rows, p + 1 columns (reproduces the table's CA(212;3,54,4) at p = 53)."""
    X = cyclotomic(p, v, diag=diag); out = []
    for s in range(v):
        for r in X: out.append([(x + s) % v for x in r] + [s])
    return cut(out, k) if k else out

# ----------------------------------------------------------------------------------------------- RMS (W6)
def _ext_powers(q, deg):
    """powers alpha^j (j = 0 .. q^deg - 2) of a root of a primitive polynomial of degree deg over GF(q), as coordinate
    vectors (low degree first)"""
    add, mul = gf(q); n = q ** deg - 1
    neg = [next(b for b in range(q) if add[a][b] == 0) for a in range(q)]
    for co in itertools.product(range(q), repeat=deg):
        if co[0] == 0: continue                                   # constant term nonzero
        x = [0] * deg; x[0] = 1; seen = []
        ok = True
        for j in range(n):
            seen.append(tuple(x))
            # multiply by alpha: shift up, reduce alpha^deg = -(co[0] + co[1] a + ...)
            top = x[-1]; x = [0] + x[:-1]
            if top:
                for i in range(deg): x[i] = add[x[i]][mul[neg[top]][co[i]]]
            if tuple(x) == tuple([1] + [0] * (deg - 1)) and j < n - 1: ok = False; break
        if ok and len(set(seen)) == n: return seen
    return None

def rms(q, k=None):
    """W6, Raaphorst, Moura and Stevens 2014: CA(2q^3 - 1; 3, q^2+q+1, q). Column j: the points L(alpha^j) and
    L(alpha^-j) of PG(2,q) (alpha a root of a primitive cubic); two blocks of all F_q-combinations u . L, one zero row
    removed. Three points collinear in one plane are not in the other (orthogoval planes)."""
    add, mul = gf(q); P = _ext_powers(q, 3); n = q ** 3 - 1; K = q * q + q + 1; k = k or K
    out = []
    for blk in (1, -1):
        cols = [P[(blk * j) % n] for j in range(k)]
        for u in itertools.product(range(q), repeat=3):
            if blk == -1 and not any(u): continue
            row = []
            for L in cols:
                s = 0
                for a, b in zip(u, L): s = add[s][mul[a][b]]
                row.append(s)
            out.append(row)
    return out

# ----------------------------------------------------------------------------------------------- k-ary Roux (W21)
def kary_roux(A, B, C, v, h, l):
    """Cohen, Colbourn and Ling 2008 Theorem 3 (k-ary Roux) with the improvement that zero differences need no row:
    A = CA(3, h, v), B = CA(3, l, v), C = CA(2, l, v), D = the multiplication-table DCA over GF(v) without its zero row
    (v - 1 rows, h <= v, v a prime power). Columns (i, j), i < h, j < l. Rows: A[i] for every j; B[j] for every i;
    for every row c of C and nonzero lambda: c[j] + lambda * a_i. CA(N_A + N_B + (v - 1) N_C; 3, h l, v)."""
    add, mul = gf(v)
    out = [[a[i] for i in range(h) for j in range(l)] for a in A]
    out += [[b[j] for i in range(h) for j in range(l)] for b in B]
    for lam in range(1, v):
        for c in C: out.append([add[c[j]][mul[lam][i]] for i in range(h) for j in range(l)])
    return out

def hartman4(A, B, C, v):
    """Hartman's doubling at strength 4 (CMTW 2006 Theorem 4.7): A = CA(4, k, v), B = CA(3, k, v), C = CA(2, k, v^2).
    Columns (i, side). Rows [A | A]; for d = 1..v-1 [B | B + d]; and [C div v | C mod v] (each v^2 symbol is a pair
    (x, y), x on side 0, y on side 1), which covers every pattern on two twin pairs. CA(N_A + (v-1) N_B + N_C; 4, 2k, v)."""
    out = [list(r) + list(r) for r in A]
    for d in range(1, v):
        for r in B: out.append(list(r) + [(x + d) % v for x in r])
    for r in C: out.append([x // v for x in r] + [x % v for x in r])
    return out

def paley_doubled(p, k=None):
    """W11 doubled Paley: M the binary Paley circulant over GF(p); rows [0 | M] and [1 | 1 - M]: 2p rows, p + 1 columns
    (one strength higher than M when it holds; checked, not assumed)"""
    M = cyclotomic(p, 2)
    out = [[0] + r for r in M] + [[1] + [1 - x for x in r] for r in M]
    return cut(out, k) if k else out


# ------------------------------------------------------------------------------- augmentation (Colbourn 2014, W29)
_RHO = {}
def aug_rho(t, k, q):
    """rows of an OA(q^t; t, k, q) of index one with exactly mu zeros, mu = 0..t-1 (one all-zero row, none with t..k-1):
    sum_{j>=i} C(j,i) C(k-j,t-i) rho_j = C(k,i) C(k-i,t-i) (q-1)^(t-i), i = 0..t-1 (Colbourn 2014, Section 4)"""
    key = (t, k, q)
    if key not in _RHO:
        from fractions import Fraction
        M = [[Fraction(math.comb(j, i) * math.comb(k - j, t - i)) for j in range(t)] + [Fraction(math.comb(k, i) * math.comb(k - i, t - i) * (q - 1) ** (t - i))] for i in range(t)]
        for c in range(t):
            p = next(r for r in range(c, t) if M[r][c] != 0); M[c], M[p] = M[p], M[c]
            for r in range(t):
                if r != c and M[r][c] != 0:
                    f = M[r][c] / M[c][c]; M[r] = [x - f * y for x, y in zip(M[r], M[c])]
        _RHO[key] = [int(M[i][t] / M[i][i]) for i in range(t)]
    return _RHO[key]

def aug_base(t, k, q):
    r = aug_rho(t, k, q)
    return sum(r[m] * 2 ** m for m in range(t - 1)), r[t - 1]

def aug_size(form, t, k, v, M=None, R=None):
    """rows of the augmentation from OA(q^t; t, k, q), q = v - 1, tau = 2: form '1' (Thm 2.3 (2.1), M = CAN(t,k,2)),
    '2' (Thm 2.3 (2.2), R = CAN(t,k,3)), 'q' (Thm 2.2 A, R = N1-quilting array QA(t,k,3), M = CAN(t,k,2))"""
    base, r1 = aug_base(t, k, v - 1)
    if form == "1": return base + r1 * 2 ** (t - 1) + M
    if form == "2": return base + r1 * 2 ** (t - 2) + (v - 2) * R
    return base + r1 * 2 ** (t - 2) + (v - 2) * R + M

def lemma_quilt(t, k):
    """the direct N^(1)_{t,2}-quilting arrays on symbols 0, 1, 2 of Colbourn 2014 Lemmas 3.1 (t=4, k>=5), 3.2 (t=5, k>=6),
    3.3 (t=6, k>=7); None elsewhere"""
    rows = []
    if not ((t == 4 and k >= 5) or (t == 5 and k >= 6) or (t == 6 and k >= 7)): return None
    for g in range(k):
        others = [c for c in range(k) if c != g]
        if t == 4:
            rows.append([2 if c == g else 1 for c in range(k)])
            rows += [[2 if c == g else (1 if c == h else 0) for c in range(k)] for h in others]
        elif t == 5:
            rows += [[2 if c == g else (1 if c == h else 0) for c in range(k)] for h in others]
            rows += [[2 if c == g else (0 if c == h else 1) for c in range(k)] for h in others]
        else:
            rows += [[2 if c == g else (0 if c in (a, b) else 1) for c in range(k)] for a, b in itertools.combinations(others, 2)]
            rows += [[2 if c == g else (1 if c == h else 0) for c in range(k)] for h in others]
    if t == 6 and k == 7: rows += [[2 if c == g else 1 for c in range(k)] for g in range(k)]
    return rows

def lemma_quilt_N(t, k):
    if t == 4 and k >= 5: return k * k
    if t == 5 and k >= 6: return 2 * k * (k - 1)
    if t == 6 and k >= 8: return k * math.comb(k - 1, 2) + k * (k - 1)
    if t == 6 and k == 7: return 154
    return None

def augment(form, t, k, v, binary=None, third=None):
    """the augmentation array: Bush OA(q^t; t, k, q), q = v - 1, every nonzero symbol s written s + 1; rows with mu <= t-2
    zeros expanded by all 2^mu binary vectors; rows with t-1 zeros by all 2^(t-1) (form '1') or the 2^(t-2) even ones;
    form '1' then the binary CA in place of the all-zero row; forms '2' and 'q' then v-2 copies of `third` (a CA(t,k,3)
    or an N1-quilting array on 0, 1, 2) with symbol 2 written 2..v-1, and form 'q' also the binary CA"""
    q = v - 1
    allv = {m: [list(x) for x in itertools.product((0, 1), repeat=m)] for m in range(t)}
    even = [x for x in allv[t - 1] if sum(x) % 2 == 0]
    out = []
    for row in bush(q, t, k):
        z = [i for i, x in enumerate(row) if x == 0]
        if len(z) == k: continue
        if len(z) >= t: raise ValueError("not an orthogonal array of index one")
        base = [x + 1 if x else 0 for x in row]
        fills = allv[len(z)] if len(z) <= t - 2 or form == "1" else even
        for f in fills:
            r = list(base)
            for i, b_ in zip(z, f): r[i] = b_
            out.append(r)
    if form in ("2", "q"):
        for s_ in range(2, v):
            out += [[s_ if x == 2 else x for x in r] for r in third]
    if form in ("1", "q"):
        out += [list(r) for r in binary]
    return out


def aug_classes(v, cost_n, cost_np):
    """Colbourn 2014 Theorem 2.2 B: split the v-2 new symbols into classes of 1..4; the first class uses an (N^(a) u P)
    quilting array (cost_np[a]), the others N^(a) arrays (cost_n[a]); costs None where none is known.
    Returns (rows, [a_1, a_2, ...]) with the smallest number of quilting rows, or None."""
    m = v - 2
    INF = float("inf")
    best = [0] + [INF] * m; pick = [None] * (m + 1)
    for j in range(1, m + 1):
        for a in range(1, 5):
            if a <= j and cost_n.get(a) is not None and best[j - a] + cost_n[a] < best[j]:
                best[j] = best[j - a] + cost_n[a]; pick[j] = a
    out = None
    for a1 in range(1, 5):
        if a1 > m or cost_np.get(a1) is None or best[m - a1] == INF: continue
        tot = cost_np[a1] + best[m - a1]
        if out is None or tot < out[0]:
            cls, j = [a1], m - a1
            while j: cls.append(pick[j]); j -= pick[j]
            out = (tot, cls)
    return out

def augment_classes(t, k, v, classes):
    """the augmentation array of Theorem 2.2 B: the OA part of form 'q' and then, class by class, its quilting array
    (rows over 0, 1 and 2..1+a) with symbol 2 + j written as the class's j-th new symbol. classes: list of (a, rows);
    the first class's rows must also cover P (an N^(a) u P array, or an N^(a) array followed by a binary CA)."""
    out = augment("q", t, k, v, binary=[], third=[])
    nxt = 2
    for a, rows in classes:
        out += [[nxt + x - 2 if x >= 2 else x for x in r] for r in rows]
        nxt += a
    if nxt != v: raise ValueError("classes do not use the v - 2 new symbols")
    return out
