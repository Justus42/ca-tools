#!/usr/bin/env python3
"""cyclo-1: for primes up to 110, v = 2, 3, 4, the plain and shifted forms and t = 3, 4, the certificate's
coverage verdict equals ca_verify on the whole array (both outcomes occur), and the rebuilt array hashes as an
independent build of the first k columns; a g that is not a primitive root, v not dividing p - 1, p not prime
and k above the number of columns are rejected by cyclo_params."""
import hashlib, json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import construction_cert as cc


def proot(p):
    m, fac, d = p - 1, set(), 2
    while d * d <= m:
        while m % d == 0:
            fac.add(d); m //= d
        d += 1
    if m > 1:
        fac.add(m)
    return next(g for g in range(2, p) if all(pow(g, (p - 1) // f, p) != 1 for f in fac))


def build(p, v, form, g):
    cls = [0] * p; x = 1
    for e in range(p - 1):
        cls[x] = e % v; x = x * g % p
    X = [[0 if c == r else cls[(c - r) % p] for c in range(p)] for r in range(p)]
    if form == "plain":
        return X
    return [[(x + s) % v for x in row] + [s] for s in range(v) for row in X]


def main():
    t0 = time.time(); fails = 0; seen = {True: 0, False: 0}; n = 0
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "ca_verify")
        subprocess.run(["cc", "-O3", "-pthread", "-o", exe, os.path.join(REPO, "ca_verify.c")], check=True)
        os.environ["CA_VERIFY"] = exe
        full = os.path.join(d, "full.txt"); cert = os.path.join(d, "c.json")
        for p in [q for q in range(11, 110) if cc.is_prime(q)]:
            for v in (2, 3, 4):
                if (p - 1) % v:
                    continue
                g = proot(p)
                for form in ("plain", "shifted"):
                    A = build(p, v, form, g); K = len(A[0])
                    with open(full, "w") as f:
                        f.write("".join(" ".join(map(str, r)) + "\n" for r in A))
                    for t in (3, 4):
                        k = K - 2
                        whole = subprocess.run([exe, full, str(t), str(v), "2"], capture_output=True,
                                               text=True).stdout.strip().splitlines()[-1].startswith("VERIFIED")
                        json.dump({"format": cc.FORMAT, "construction": "cyclo-1", "t": t, "v": v, "p": p, "g": g,
                                   "form": form, "expected": {"N": len(A), "k": k, "array_sha256": "0" * 64}},
                                  open(cert, "w"))
                        r = cc.run(cert, None)
                        cov = not any(f[0] == "cyclo_coverage" for f in r["failures"])
                        sha = hashlib.sha256("".join(" ".join(map(str, row[:k])) + "\n" for row in A).encode()).hexdigest()
                        ok = cov == whole and r["sha256"] == sha and r["N"] == len(A)
                        seen[whole] += 1; n += 1
                        if not ok:
                            fails += 1
                            print("FAIL p %d v %d %s t %d: whole array %s, certificate %s, hash %s"
                                  % (p, v, form, t, whole, cov, r["sha256"] == sha))
        print("%d arrays: the certificate agrees with ca_verify on the whole array (%d covering, %d not), "
              "and every rebuild hashes as an independent build: %s"
              % (n, seen[True], seen[False], "PASS" if fails == 0 else "FAIL"))
        ok = seen[True] > 20 and seen[False] > 20
        print("both outcomes occur often: %s" % ("PASS" if ok else "FAIL")); fails += not ok
        base = {"format": cc.FORMAT, "construction": "cyclo-1", "t": 3, "v": 3, "p": 31, "g": 3, "form": "plain",
                "expected": {"N": 31, "k": 29, "array_sha256": "0" * 64}}
        for name, mod in (("a g that is not a primitive root", {"g": 4}), ("v not dividing p - 1", {"v": 4}),
                          ("p not prime", {"p": 33, "g": 5}),
                          ("k above the number of columns", {"expected": {"N": 31, "k": 40, "array_sha256": "0" * 64}})):
            c = dict(base); c.update(mod); json.dump(c, open(cert, "w"))
            r = cc.run(cert, None)
            ok = not r["ok"] and any(f[0] == "cyclo_params" for f in r["failures"])
            print("%s rejected by cyclo_params: %s" % (name, "PASS" if ok else "FAIL")); fails += not ok
    print("%d failure(s), %.0f s" % (fails, time.time() - t0))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
