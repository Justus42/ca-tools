import argparse
import csv
import os
from collections import defaultdict


def load(table_dir):
    rows = list(csv.DictReader(open(os.path.join(table_dir, "ca_table.csv"), newline="")))
    withdrawn = set()
    wf = os.path.join(table_dir, "withdrawn_files.csv")
    if os.path.exists(wf):
        for r in csv.DictReader(open(wf, newline="")):
            if r.get("sha256"):
                withdrawn.add(r["sha256"])
    floors = defaultdict(list)
    lf = os.path.join(table_dir, "lower_bounds.csv")
    if os.path.exists(lf):
        for r in csv.DictReader(open(lf, newline="")):
            floors[(int(r["t"]), int(r["v"]))].append((int(r["k_min"]), int(r["k_max"]), int(r["bound"])))
    return rows, withdrawn, floors


def floor_at(floors, t, v, k):
    for a, b, n in floors.get((t, v), []):
        if a <= k <= b:
            return n
    return None


def build(rows, withdrawn, floors):
    best = defaultdict(dict)
    arr = defaultdict(dict)
    for r in rows:
        try:
            t, v, k, n = int(r["t"]), int(r["v"]), int(r["k"]), int(r["N"])
        except ValueError:
            continue
        if r["tier"] in ("CITED", "VERIFIED"):
            d = best[(t, v)]
            d[k] = min(d.get(k, n), n)
        if r["tier"] == "VERIFIED" and r["array_sha256"] and r["array_sha256"] not in withdrawn:
            d = arr[(t, v)]
            d[k] = min(d.get(k, n), n)
    out = []
    for (t, v) in sorted(best):
        bk = sorted(best[(t, v)])
        ak = sorted(arr.get((t, v), {}))
        run_b = None
        run_a = None
        suffix_b = {}
        suffix_a = {}
        for k in reversed(bk):
            n = best[(t, v)][k]
            run_b = n if run_b is None else min(run_b, n)
            suffix_b[k] = run_b
        for k in reversed(ak):
            n = arr[(t, v)][k]
            run_a = n if run_a is None else min(run_a, n)
            suffix_a[k] = run_a
        ai = 0
        for k in bk:
            while ai < len(ak) and ak[ai] < k:
                ai += 1
            a = suffix_a[ak[ai]] if ai < len(ak) else None
            b = suffix_b[k]
            f = floor_at(floors, t, v, k)
            if a is None:
                status = "no_array"
            elif a > b:
                status = "array_above_best"
            elif f is not None and f >= b:
                continue
            else:
                status = "beat_best"
            out.append([t, v, k, b, "" if a is None else a, "" if f is None else f, status])
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--table-dir", default="table")
    p.add_argument("--out", default="table/wanted.csv")
    a = p.parse_args()
    rows, withdrawn, floors = load(a.table_dir)
    out = build(rows, withdrawn, floors)
    with open(a.out, "w", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["t", "v", "k", "best_N", "smallest_array_N", "proven_floor", "status"])
        w.writerows(out)
    counts = defaultdict(int)
    for r in out:
        counts[r[-1]] += 1
    print("wanted.csv: %d rows (%s)" % (len(out), ", ".join("%s %d" % kv for kv in sorted(counts.items()))))


if __name__ == "__main__":
    main()
