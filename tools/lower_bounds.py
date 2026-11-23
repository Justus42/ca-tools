import csv
import math
import os
import sys
from fractions import Fraction

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, "table", "ca_table.csv")
FRAME = os.path.join(ROOT, "table", "ca_frame.csv")
SEEDS = os.path.join(ROOT, "table", "lower_bound_seeds.csv")
OUT = os.path.join(ROOT, "table", "lower_bounds.csv")
HEADER = ["t", "v", "k_min", "k_max", "bound", "rule", "theorem", "reference", "derivation"]

THEOREMS = {
    "R0": ("CAN(t,k,v) >= v^t", "", ""),
    "R2": ("CAN(t,k,v) >= v CAN(t-1,k-1,v) (fixing a symbol)", "lb-lkklf2011", ""),
    "R3": ("CAN(2,k,2) = least N with C(N-1, ceil(N/2)) >= k", "binary-ks1973;binary-k1973", "Kleitman and Spencer 1973, Theorem 1"),
    "R5": ("published value", "", ""),
    "R6": ("binary strength 3, extra row at the end of a tread", "lb-cko2012", "Choi, Kim and Oh, Theorems 4.7 and 4.8"),
    "R7": ("binary strength t >= 3, Kleitman-Spencer bound (17)", "binary-ks1973", "Kleitman and Spencer 1973, (17) p. 261"),
    "R8": ("binary strength t >= 3, Kleitman-Spencer bound (8)", "binary-ks1973", "Kleitman and Spencer 1973, (8) p. 259"),
    "R9": ("CAN(2,k,v) >= v^2+2 for k >= v+2, v >= 3", "lb-smm1998", "Stevens, Moura and Mendelsohn 1998, Section 4.1, p. 291"),
    "R10": ("k <= (1/2) C(floor(2N/v), floor(N/v))", "lb-pt1989", "Poljak and Tuza 1989, Theorem 1, p. 113"),
    "R12": ("CAN(2,k,v) >= v^2+3 for k >= v+2, v >= 4", "lb-smm1998", "Stevens, Moura and Mendelsohn 1998, Theorem 6, pp. 292-293"),
    "R13": ("no orthogonal array of index unity with this many columns", "oa-bush1952", "Bush 1952, pp. 427 and 431"),
    "R14": ("no orthogonal array of index unity with this many columns", "lb-kp1975", "Kounias and Petros 1975, Theorem 2.2, Corollary 1, Theorem 3.3"),
    "R15": ("CAN(3,v+2,v) >= v^3 + c(v), v odd", "fuse-ckrs2010", "Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010, Theorem 8.1"),
    "R16": ("k <= (1/2) C(2 floor(N/v) + delta, floor(N/v))", "lb-smm1998", "Stevens, Moura and Mendelsohn 1998, Theorem 4, eq. (4)"),
    "R17": ("set packing bound", "lb-smm1998", "Stevens, Moura and Mendelsohn 1998, Corollary 3, eq. (7)"),
}

_seeds = None


def seeds():
    global _seeds
    if _seeds is None:
        _seeds = {}
        with open(SEEDS, newline="") as f:
            for r in csv.DictReader(f):
                _seeds.setdefault((int(r["t"]), int(r["v"])), []).append(
                    (int(r["k"]), int(r["bound"]), r["reference"], r["detail"]))
    return _seeds


def ks_exact(k):
    n = 2
    while math.comb(n - 1, math.ceil(n / 2)) < k:
        n += 1
    return n


def cko_list():
    out = []
    for m in range(7, 60):
        c = math.comb(m - 1, m // 2 - 1)
        lo = c + m - 3 * (m // 2) if m % 2 else c - m // 2
        out.append((lo + 2, 2 * m + (1 if m % 2 else 2), m))
    return out


CKO = cko_list()
_memo = {}


def ks_strong(t, k):
    key = ("s", t, k)
    if key in _memo:
        return _memo[key]
    need = math.comb(k, t - 2)
    u = 2 ** (t - 1)
    n, last = u, 0
    while True:
        q = n // u + 1
        den = Fraction(2) ** (t - 3) * math.comb(n // 2 ** (t - 2), q)
        if den > 0 and Fraction(math.comb(n, q)) / den >= need:
            break
        last = n
        n += u
    _memo[key] = last + 1 if last else 0
    return _memo[key]


def ks_weak(t, k):
    key = ("w", t, k)
    if key in _memo:
        return _memo[key]
    need = math.comb(k, t - 1)
    u = 2 ** (t - 1)
    n = 2 ** t
    while sum(math.comb(n, j) for j in range(n // u + 1)) < need:
        n += 1
    _memo[key] = n
    return n


def poljak_tuza(k, v):
    n = v * v
    while math.comb((2 * n) // v, n // v) < 2 * k:
        n += 1
    return n


def smm_theorem4(k, v):
    n = v
    while True:
        q = n // v
        d = 1 if n % v == v - 1 else 0
        if math.comb(2 * q + d, q) >= 2 * k:
            return n
        n += 1


def smm_corollary3(k, v):
    def f(b):
        r = b // v
        return 0 if r - (v - 2) < 0 else math.comb(b, r - (v - 2)) // (v * math.comb(r, v - 2))
    t = v
    while not k <= f(t * v):
        t += 1
    return t + v * (v - 1)


def r15_add(v):
    return 6 if v == 3 else 10 if v == 5 else 11 if v in (7, 9) else 12


_lb = {}


def lower_bound(t, k, v):
    key = (t, k, v)
    if key in _lb:
        return _lb[key]
    best = (v ** t, "R0", "", "R0 v^t")
    def take(val, rule, ref, text):
        nonlocal best
        if val > best[0]:
            best = (val, rule, ref, text)
    if t == 2 and v == 2:
        best = (ks_exact(k), "R3", THEOREMS["R3"][1], "R3 Kleitman-Spencer, Katona (exact)")
    else:
        if t >= 3:
            b, rule, ref, text = lower_bound(t - 1, k - 1, v)
            take(v * b, "R2", ";".join(x for x in (THEOREMS["R2"][1], ref) if x),
                 "R2 %d x CAN(%d,%d,%d) >= %d [%s]" % (v, t - 1, k - 1, v, b, text))
        for kk, val, ref, detail in seeds().get((t, v), []):
            if k >= kk:
                take(val, "R5", ref, "R5 CAN(%d,%d,%d) >= %d: %s%s" % (t, kk, v, val, detail, "" if kk == k else "; R1"))
        if t == 3 and v == 2:
            for kk, val, m in CKO:
                if k >= kk:
                    take(val, "R6", THEOREMS["R6"][1], "R6 Choi-Kim-Oh Thm 4.%d at m=%d (k >= %d)%s"
                         % (7 if m % 2 else 8, m, kk, "" if kk == k else "; R1"))
    if t == 2 and v >= 3:
        if k >= v + 2:
            take(v * v + 2, "R9", THEOREMS["R9"][1], "R9 " + THEOREMS["R9"][2])
        take(poljak_tuza(k, v), "R10", THEOREMS["R10"][1], "R10 " + THEOREMS["R10"][2])
        if k >= v + 2 and v >= 4:
            take(v * v + 3, "R12", THEOREMS["R12"][1], "R12 " + THEOREMS["R12"][2])
        take(smm_theorem4(k, v), "R16", THEOREMS["R16"][1], "R16 " + THEOREMS["R16"][2])
        take(smm_corollary3(k, v), "R17", THEOREMS["R17"][1], "R17 " + THEOREMS["R17"][2])
    if t >= 3:
        if (v % 2 == 1 and t < v and k >= v + t - 1) or (v % 2 == 0 and t < v and k >= v + t) or (t >= v and k >= t + 2):
            take(v ** t + 1, "R13", THEOREMS["R13"][1], "R13 " + THEOREMS["R13"][2] + ": v^t+1")
        if t == 3 and v % 4 == 2 and v >= 6 and k >= v + 1:
            take(v ** 3 + 1, "R14", THEOREMS["R14"][1], "R14 Kounias and Petros 1975, Theorem 2.2: v^3+1")
        if v % 2 == 0 and v % 36 != 0 and 4 <= t < v and k >= v + t - 2:
            take(v ** t + 1, "R14", THEOREMS["R14"][1], "R14 Kounias and Petros 1975, Corollary 1: v^t+1")
        if (t, v) == (4, 5) and k >= 7:
            take(626, "R14", THEOREMS["R14"][1], "R14 Kounias and Petros 1975, Theorem 3.3: CAN(4,7,5) >= 626")
        if t == 3 and v % 2 == 1 and k >= v + 2:
            take(v ** 3 + r15_add(v), "R15", THEOREMS["R15"][1], "R15 " + THEOREMS["R15"][2] + ": v^3+%d" % r15_add(v))
    if v == 2 and t >= 3:
        x = ks_strong(t, k)
        take(x, "R7", THEOREMS["R7"][1], "R7 " + THEOREMS["R7"][2] + ": no array on %d rows" % (x - 1))
        take(ks_weak(t, k), "R8", THEOREMS["R8"][1], "R8 " + THEOREMS["R8"][2])
    _lb[key] = best
    return best


def table_keys():
    keys = {}
    with open(TABLE, newline="") as f:
        for r in csv.DictReader(f):
            key = (int(r["t"]), int(r["v"]), int(r["k"]))
            n = int(r["N"])
            keys[key] = min(n, keys.get(key, n))
    return keys


def ranges(keys):
    by_tv = {}
    for (t, v, k) in keys:
        by_tv.setdefault((t, v), []).append(k)
    out = []
    for (t, v) in sorted(by_tv):
        ks = sorted(by_tv[(t, v)])
        i = 0
        while i < len(ks):
            b, rule, ref, text = lower_bound(t, ks[i], v)
            j = i
            while j + 1 < len(ks) and lower_bound(t, ks[j + 1], v)[:2] == (b, rule):
                j += 1
            k_max = ks[j]
            out.append([t, v, ks[i], k_max, b, rule, theorem_text(rule, text), ref, text])
            i = j + 1
    return out


def theorem_text(rule, text):
    if rule == "R5":
        return "published value: " + text.split(": ", 1)[1].replace("; R1", "")
    stmt, _, where = THEOREMS[rule]
    return stmt + (" (" + where + ")" if where else "")


def bound_at(rows, t, v, k):
    for r in rows:
        if r[0] == t and r[1] == v and r[2] <= k <= r[3]:
            return r[4]
    return None


def load(path=OUT):
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        header = next(rd)
        rows = [[int(x) if i < 5 else x for i, x in enumerate(r)] for r in rd]
    return header, rows


def index(rows):
    by_tv = {}
    for r in rows:
        by_tv.setdefault((r[0], r[1]), []).append(r)
    return by_tv


def lookup(by_tv, t, v, k):
    for r in by_tv.get((t, v), ()):
        if r[2] <= k <= r[3]:
            return r[4]
    return None


def verified_sizes(table=TABLE):
    out = {}
    with open(table, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["tier"] == "VERIFIED":
                out.setdefault((int(r["t"]), int(r["v"])), []).append((int(r["k"]), int(r["N"])))
    return out


def closed_steps(rows, frame=FRAME, table=TABLE):
    by_tv = index(rows)
    ver = verified_sizes(table)
    out = []
    with open(frame, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            t, v, k, n = int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"])
            if lookup(by_tv, t, v, k) == n and any(kk >= k and nn == n for kk, nn in ver.get((t, v), ())):
                out.append((t, v, k, n))
    return out


def main():
    sys.setrecursionlimit(100000)
    keys = table_keys()
    above = [(key, n, lower_bound(key[0], key[2], key[1])[0]) for key, n in keys.items()
             if lower_bound(key[0], key[2], key[1])[0] > n]
    if above:
        for (t, v, k), n, b in above[:20]:
            print("bound above the table: t=%d v=%d k=%d N=%d bound=%d" % (t, v, k, n, b))
        sys.exit(1)
    rows = ranges(keys)
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(HEADER)
        w.writerows(rows)
    print("lower_bounds.csv: %d ranges over %d (t, v, k) keys" % (len(rows), len(keys)))


if __name__ == "__main__":
    main()
