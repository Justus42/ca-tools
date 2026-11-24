#!/usr/bin/env python3
"""three_stage.py - the greedy-metaheuristic 3-stage method of Izquierdo-Marquez, Torres-Jimenez, Acevedo-Juarez and
Avila-George (Inform. Sci. 2018), our own implementation with this project's programs.
  stage 1: CPHF(n; k, v, t) by annealing, allowed to stay incomplete (cphf_sa, BEST=1)
  stage 2: expand to n v^t rows (repeats removed) and add rows greedily for the missing tuples
  stage 3: repeat { delete the row whose loss is smallest (NCK wildcard hand-off, nck.c), and if tuples go missing,
           anneal the whole array at the new size (casa.c) } until the annealer fails in its time limit
usage: three_stage.py t v k target n WORK [stage1_secs] [anneal_secs] [total_secs] [seed]
Writes WORK/best_N.txt for every size reached and prints the best N."""
import sys, os, subprocess, itertools, random, time, glob
t, v, k, target, n, W = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), sys.argv[6]
s1 = int(sys.argv[7]) if len(sys.argv) > 7 else 60
sa = int(sys.argv[8]) if len(sys.argv) > 8 else 120
total = int(sys.argv[9]) if len(sys.argv) > 9 else 1800
seed = int(sys.argv[10]) if len(sys.argv) > 10 else 1
RESUME = sys.argv[11] if len(sys.argv) > 11 else None
H = os.path.dirname(os.path.abspath(__file__)); B = H + "/bin"
os.makedirs(W, exist_ok=True); t_end = time.time() + total
def run(cmd, **kw): return subprocess.run(cmd, capture_output=True, text=True, **kw)
def load(p): return [list(map(int, l.split())) for l in open(p) if l.strip()]
def save(p, X): open(p, 'w').write('\n'.join(' '.join(map(str, r)) for r in X) + '\n')
if RESUME:
    M1 = load(RESUME)
# stage 1
fam = f"{W}/cphf.txt"
if not RESUME:
  r = run([B + "/cphf_sa", str(n), str(k), str(v), str(t), str(seed), str(s1), "0.6", "0.9999", fam], env=dict(os.environ, BEST="1"))
  print("stage 1:", (r.stderr.strip().splitlines() or [""])[-1])
  run(["python3", H + "/expand.py", fam, str(v), str(t), f"{W}/m0.txt"])
  A = load(f"{W}/m0.txt")
if not RESUME:
    # stage 2: greedy rows for missing tuples (unassigned cells = -1, filled at random at the end)
    added = []
    rng = random.Random(seed)
    # the missing (t-set, tuple) list comes from one exact pass of ca_profile
    run([B + "/ca_profile", f"{W}/m0.txt", str(t), str(v), "-m", f"{W}/missing.txt"])
    items = [list(map(int, l.split())) for l in open(f"{W}/missing.txt") if l.strip()]
    rng.shuffle(items)
    for it in items:
        S, tup = it[:t], it[t:]
        if any(all(row[c] == x for c, x in zip(S, tup)) for row in added): continue
        for row in added:
            if all(row[c] in (-1, x) for c, x in zip(S, tup)):
                for c, x in zip(S, tup): row[c] = x
                break
        else:
            row = [-1] * k
            for c, x in zip(S, tup): row[c] = x
            added.append(row)
    M1 = A + [[x if x >= 0 else rng.randrange(v) for x in row] for row in added]
N = len(M1); cur = f"{W}/best_{N}.txt"; save(cur, M1)
if not RESUME: print(f"stage 2: {len(A)} rows from the CPHF + {len(added)} greedy rows = {N}")
# stage 3
CASA, NCK = B + "/casa", B + "/nck"
while time.time() < t_end and N > target:
    # NCK row elimination (wildcard hand-off) for a short burst
    pre = f"{W}/nck"
    for f in glob.glob(pre + "_*.txt"): os.remove(f)
    run([NCK, str(N), str(t), str(k), str(v), cur, pre, str(seed), str(min(60, sa))])
    got = sorted(glob.glob(pre + "_*.txt"), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
    if got and int(got[0].rsplit("_", 1)[1][:-4]) < N:
        if run([B + "/ca_profile", got[0], str(t), str(v)]).returncode: print("NCK output failed the exact check"); break
        N = int(got[0].rsplit("_", 1)[1][:-4]); cur = f"{W}/best_{N}.txt"; os.replace(got[0], cur); print("stage 3: NCK ->", N, flush=True); continue
    # delete the row with fewest uniquely covered tuples, anneal at N-1
    X = load(cur)
    run([B + "/ca_profile", cur, str(t), str(v), "-u", f"{W}/uniq.txt"])
    uniq = [int(l) for l in open(f"{W}/uniq.txt")]
    drop = min(range(N), key=lambda i: uniq[i]); Y = X[:drop] + X[drop + 1:]
    init = f"{W}/init_{N-1}.txt"; save(init, Y)
    out = f"{W}/casa_{N-1}.txt"
    if os.path.exists(out): os.remove(out)
    for tr in range(int(os.environ.get("RETRIES", "3"))):
        run([CASA, str(N - 1), str(t), str(k), str(v), str(seed + 1000 * tr), str(sa), "0.5", "0.99995", out, init])
        if os.path.exists(out) or time.time() > t_end: break
    if os.path.exists(out) and run([B + "/ca_profile", out, str(t), str(v)]).returncode == 0: N -= 1; cur = f"{W}/best_{N}.txt"; os.replace(out, cur); print("stage 3: anneal ->", N, flush=True)
    else: print("stage 3: annealer could not cover after deleting a row at", N - 1, "; stop"); break
print("BEST", N, cur)
