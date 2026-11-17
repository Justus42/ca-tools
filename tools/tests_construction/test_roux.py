#!/usr/bin/env python3
"""roux-1 (Martirosyan and Colbourn 2005, Corollary 2.2): a certificate from three stored table rows is
valid and its array passes ca_verify; a wrong expected hash and an ingredient of too low strength are
rejected."""
import json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import construction_cert as cc

A4 = "0bb2494c9189f19258199c734965fb1a038ee396e56edac57d1da1df4d3e3be0"
C3 = "cd9d6a6893fac3a14dd8e2fd97decaf0ee09602d4522d2ddc79306713265f297"
E2 = "1843d5aabf8f245b4859f126042899e260e80666735a7845fbf3606a45b33a9d"


def cert(d, A, C, E, sha, N=111 + 2 * 33 + 81):
    p = os.path.join(d, "c.cert.json")
    json.dump({"format": cc.FORMAT, "construction": "roux-1", "t": 4, "v": 3, "h": 6, "A": {"rebuild": A},
               "C": {"rebuild": C}, "E": {"rebuild": E}, "expected": {"N": N, "k": 12, "array_sha256": sha}}, open(p, "w"))
    return p


def main():
    t0 = time.time(); fails = 0
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "CA.txt")
        res = cc.run(cert(d, A4, C3, E2, "0" * 64), out)
        sha = res["sha256"]
        res = cc.run(cert(d, A4, C3, E2, sha), out)
        ok = res["ok"] and res["N"] == 258 and res["k"] == 12
        exe = os.path.join(d, "ca_verify")
        subprocess.run(["cc", "-O3", "-pthread", "-o", exe, os.path.join(REPO, "ca_verify.c")], check=True)
        ver = subprocess.run([exe, out, "4", "3"], capture_output=True, text=True)
        ok = ok and "VERIFIED:" in ver.stdout
        print("valid certificate, array verified:", "PASS" if ok else "FAIL"); fails += not ok
        res = cc.run(cert(d, A4, C3, E2, "1" * 64), None)
        ok = not res["ok"] and any(f[0] == "sha256" for f in res["failures"])
        print("wrong expected hash rejected:", "PASS" if ok else "FAIL"); fails += not ok
        res = cc.run(cert(d, C3, C3, E2, sha), None)
        ok = not res["ok"] and any(f[0] == "roux_ingredients" for f in res["failures"])
        print("strength 3 array as A rejected:", "PASS" if ok else "FAIL"); fails += not ok
    print("total %d s" % (time.time() - t0))
    print("ALL TESTS PASSED" if not fails else "%d TEST(S) FAILED" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
