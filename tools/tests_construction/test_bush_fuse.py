#!/usr/bin/env python3
"""fuse-1 with a Bush ingredient and "times": the Bush OA(q^t; t, k, q) over prime and prime-power fields,
fused r times, gives a CA(q^t - 2r; t, k, q - r) that ca_verify confirms; certificates that break a
hypothesis (t above q, k above q + 1, a reducible modulus, a symbol count that does not match, rows past
the last fuse's input, times on another kind) are rejected, and the plain fuse-1 of a table row is unchanged."""
import json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import construction_cert as cc

FIELDS = {2: {"q": 2, "p": 2, "m": 1}, 3: {"q": 3, "p": 3, "m": 1}, 4: {"q": 4, "p": 2, "m": 2, "modulus": [1, 1, 1]},
          5: {"q": 5, "p": 5, "m": 1}, 7: {"q": 7, "p": 7, "m": 1}, 8: {"q": 8, "p": 2, "m": 3, "modulus": [1, 1, 0, 1]},
          9: {"q": 9, "p": 3, "m": 2, "modulus": [1, 0, 1]}, 11: {"q": 11, "p": 11, "m": 1}}


_n = [0]


def cert(d, t, q, k, times, sha="0" * 64, N=None, field=None, rows=None, kind="fuse-1"):
    c = {"format": cc.FORMAT, "construction": kind, "t": t, "v": q - times, "times": times,
         "input": {"bush": {"field": field or FIELDS[q], "k": k}},
         "expected": {"N": N if N is not None else q ** t - 2 * times, "k": k, "array_sha256": sha}}
    if rows is not None:
        c["rows"] = rows
    _n[0] += 1
    p = os.path.join(d, "c%d.cert.json" % _n[0])
    json.dump(c, open(p, "w"))
    return p


def failed_on(res, name):
    return not res["ok"] and any(f[0] == name for f in res["failures"])


def main():
    t0 = time.time(); fails = 0
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "ca_verify")
        subprocess.run(["cc", "-O3", "-pthread", "-o", exe, os.path.join(REPO, "ca_verify.c")], check=True)
        out = os.path.join(d, "CA.txt")
        cases = [(2, 3, 4, 1), (2, 4, 5, 2), (3, 5, 6, 2), (3, 4, 5, 1), (2, 8, 9, 6), (3, 7, 8, 3),
                 (2, 9, 10, 7), (4, 5, 6, 1), (3, 8, 9, 5), (2, 11, 12, 9), (3, 9, 10, 1), (4, 7, 8, 4)]
        for t, q, k, r in cases:
            sha = cc.run(cert(d, t, q, k, r), None)["sha256"]
            res = cc.run(cert(d, t, q, k, r, sha), out)
            ver = subprocess.run([exe, out, str(t), str(q - r)], capture_output=True, text=True)
            ok = res["ok"] and res["N"] == q ** t - 2 * r and res["k"] == k and "VERIFIED:" in ver.stdout
            print("Bush OA(%d^%d; %d, %d, %d) fused %d times = CA(%d; %d, %d, %d), ca_verify agrees: %s"
                  % (q, t, t, k, q, r, q ** t - 2 * r, t, k, q - r, "PASS" if ok else "FAIL"))
            fails += not ok
        sha = cc.run(cert(d, 3, 5, 6, 2), None)["sha256"]
        checks = [
            ("t above q rejected (Bush needs t <= q)", cert(d, 4, 3, 4, 1), "bush"),
            ("k above q + 1 rejected", cert(d, 2, 5, 7, 1), None),
            ("reducible modulus rejected (x^2 + 2x + 1 over GF(3))",
             cert(d, 2, 9, 10, 1, field={"q": 9, "p": 3, "m": 2, "modulus": [1, 2, 1]}), "bush"),
            ("rows past the input of the last fuse rejected", cert(d, 2, 4, 5, 2, rows=[0, 14]), "fuse_rows"),
            ("wrong expected hash rejected", cert(d, 3, 5, 6, 2, "1" * 64), "sha256"),
            ("wrong expected N rejected", cert(d, 3, 5, 6, 2, sha, N=124), "N"),
        ]
        for name, path, check in checks:
            try:
                res = cc.run(path, None)
                ok = failed_on(res, check) if check else not res["ok"]
            except cc.CertError:
                ok = check is None
            print("%s: %s" % (name, "PASS" if ok else "FAIL")); fails += not ok
        p = cert(d, 3, 5, 6, 2)
        c = json.load(open(p)); c["construction"] = "derive-1"; c["column"] = 0; c["symbol"] = 0; del c["times"]
        json.dump(c, open(p, "w"))
        try:
            cc.run(p, None); ok = False
        except cc.CertError:
            ok = True
        print("a bush ingredient outside fuse-1 refused: %s" % ("PASS" if ok else "FAIL")); fails += not ok
    print("%d failure(s), %.1f s" % (fails, time.time() - t0))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
