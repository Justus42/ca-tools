#!/usr/bin/env python3
"""ca_verify shards by pairs of first columns (SHARD/NSHARDS/p) and their merge, and the memory-aware
plan: per-shard set counts equal shard_sets_pairs and add up to C(k,t); a covering array verifies across
the pair shards; a planted gap is found with the same count as the unsharded run; a missing, repeated or
mixed shard set proves nothing; ca_verify refuses pair shards at t = 2; check_submission's memory model
gives what ca_verify allocates; and array_plan fits threads to the runner's memory and falls back to pair
shards when the shard of the smallest column is too long."""
import argparse, math, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
import ca_shard_merge as sm
import check_submission as cs
import check_upgrades as cu

fails = 0


def check(name, ok, detail=""):
    global fails
    print("%s: %s" % (name, "PASS" if ok else "FAIL " + str(detail)[-800:]))
    fails += not ok


def bush(q, t, k):
    rows = []
    for idx in range(q ** t):
        a = [(idx // q ** i) % q for i in range(t)]
        row = [sum(a[i] * pow(x, i, q) for i in range(t)) % q for x in range(min(k, q))]
        if k == q + 1:
            row.append(a[t - 1])
        rows.append(row[:k])
    return rows


def write(path, rows):
    with open(path, "w") as f:
        f.write("".join(" ".join(map(str, r)) + "\n" for r in rows))


def run(exe, args):
    r = subprocess.run([exe] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    return r.returncode, r.stdout


def main():
    with tempfile.TemporaryDirectory() as d:
        exe = os.path.join(d, "ca_verify")
        subprocess.run(["cc", "-O3", "-pthread", "-o", exe, os.path.join(REPO, "ca_verify.c")], check=True)
        for t in (3, 4, 5, 6):
            for k in (t, t + 1, t + 4, 13, 20):
                if k < t:
                    continue
                for m in (1, 2, 3, 7, 11):
                    n = [sm.shard_sets_pairs(t, k, i, m) for i in range(m)]
                    if sum(n) != math.comb(k, t):
                        check("pair counts t %d k %d m %d add up to C(k,t)" % (t, k, m), False, n)
        check("pair counts add up to C(k,t) for t 3..6, k up to 20, 1 to 11 shards", fails == 0)

        for q, t, k in ((7, 3, 8), (5, 4, 6), (11, 3, 12), (7, 4, 8)):
            A = bush(q, t, k)
            p = os.path.join(d, "A.txt"); write(p, A)
            for m in (2, 5, 9):
                outs = [run(exe, [p, str(t), str(q), "2", "%d/%d/p" % (i, m)])[1] for i in range(m)]
                counts = [int(re.search(r"all (\d+) column sets", o).group(1)) for o in outs]
                r = sm.merge(outs, t, k, len(A), q)
                check("OA(%d^%d; %d, %d, %d) in %d pair shards: counts match, merged VERIFIED" % (q, t, t, k, q, m),
                      r["verified"] and r["combos"] == math.comb(k, t)
                      and counts == [sm.shard_sets_pairs(t, k, i, m) for i in range(m)], (counts, r))
            B = [list(x) for x in A]; B[17][3] = (B[17][3] + 1) % q
            pb = os.path.join(d, "B.txt"); write(pb, B)
            full = run(exe, [pb, str(t), str(q), "1"])[1]
            gaps = int(re.search(r": (\d+) of", full).group(1))
            outs = [run(exe, [pb, str(t), str(q), "2", "%d/%d/p" % (i, 4)])[1] for i in range(4)]
            r = sm.merge(outs, t, k)
            check("one changed entry in OA(%d^%d; %d, %d, %d): pair shards find %d gapped sets, unsharded %d"
                  % (q, t, t, k, q, r["gaps"], gaps), not r["verified"] and r["gaps"] == gaps and gaps > 0)

        A = bush(7, 3, 8); p = os.path.join(d, "A.txt"); write(p, A)
        outs = [run(exe, [p, "3", "7", "2", "%d/4/p" % i])[1] for i in range(4)]
        col = [run(exe, [p, "3", "7", "2", "%d/4" % i])[1] for i in range(4)]
        for name, bad in (("a missing pair shard", outs[:3]), ("a repeated pair shard", outs[:3] + [outs[0]]),
                          ("pair and column shards mixed", outs[:2] + col[2:])):
            try:
                sm.merge(bad, 3, 8, len(A), 7); ok = False
            except sm.MergeError:
                ok = True
            check(name + " proves nothing (MergeError)", ok)
        rc, _ = run(exe, [p, "2", "7", "2", "0/3/p"])
        check("ca_verify refuses pair shards at t = 2", rc == 2, rc)
        rc, _ = run(exe, [p, "3", "7", "2", "0/3/x"])
        check("ca_verify refuses an unknown shard suffix", rc == 2, rc)

        a = argparse.Namespace(runner_threads=4, runner_gb=14.0, max_shards=20, shard_hours=5.0)
        pl = cu.array_plan(3382069, 6, 10, 18, False, a)
        check("plan for CA(3382069; 6, 18, 10): 3 threads within 14 GB, pair shards, every shard within 5 h",
              pl["exact"] and pl["threads"] == 3 and pl["split"] == "pairs" and pl["memory_gb"] <= 14 and pl["shard_hours"] <= 5, pl)
        pl = cu.array_plan(2650021, 6, 11, 13, False, a)
        check("plan for CA(2650021; 6, 13, 11): 2 threads within 14 GB", pl["exact"] and pl["threads"] == 2, pl)
        pl = cu.array_plan(100000, 4, 3, 40, False, a)
        check("small array keeps 4 threads and shards by smallest column", pl["threads"] == 4 and pl["split"] == "column", pl)
        a.runner_gb = 0.001
        pl = cu.array_plan(3382069, 6, 10, 18, False, a)
        check("an array that cannot fit one thread is not planned exactly", not pl["exact"] and pl["threads"] == 0, pl)

        P = os.path.join(d, "M.txt")
        for (q, t, k, rep) in ((11, 3, 12, 30), (5, 4, 6, 400), (7, 3, 8, 600), (5, 5, 6, 300)):
            write(P, bush(q, t, k) * rep)
            for th in (1, 2):
                pid = os.fork()
                if pid == 0:
                    os.dup2(os.open(os.devnull, os.O_WRONLY), 1); os.dup2(os.open(os.devnull, os.O_WRONLY), 2)
                    os.execv(exe, [exe, P, str(t), str(q), str(th)])
                _, st, ru = os.wait4(pid, 0)
                model = cs.verify_memory_bytes(rep * q ** t, t, q, k, th) / 2 ** 20
                meas = ru.ru_maxrss / 1024.0
                check("memory model, %d x %d over %d at t %d, %d thread%s: %.1f MB, ca_verify used %.1f MB"
                      % (rep * q ** t, k, q, t, th, "" if th == 1 else "s", model, meas), meas <= model)
    print("%d failure(s)" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
