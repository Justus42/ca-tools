#!/usr/bin/env python3
"""Tests of the exact count that tools/check_submission.py runs when ca_verify is stopped for memory
(run_ca_verify, killed_for_memory, read_columns, count_check).

Cases: an orthogonal array OA(9;2,4,3) is verified; the same array with a row removed has a gap, reported with
0-based columns and tuple as ca_verify reports them; a 1-based copy is verified; a file with a don't-care entry,
a ragged file and a file with too few columns end in error (the count does not judge them); a stand-in for ca_verify
that kills itself with SIGKILL hands over to the count, which verifies, and one that kills itself on a broken array
reports the gap; a stand-in that ends with an ordinary error (return code 2) is not counted; return codes and
messages that mean a stop for memory are recognised; the verify stamp says "exact count" when the count did
the check; the cell cap stops the count; the time limit gives a timeout.

Usage: test_count_check.py   (prints PASS/FAIL lines and a summary; exit 1 on a failure)
"""
import os
import stat
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, os.path.join(REPO, "table"))
import check_submission as cs  # noqa: E402

FAILS = []


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + ("" if cond else "  " + detail))
    if not cond:
        FAILS.append(name)


def oa9():
    rows = []
    for a in range(3):
        for b in range(3):
            rows.append([a, b, (a + b) % 3, (a + 2 * b) % 3])
    return rows


def write(d, name, rows, shift=0):
    p = os.path.join(d, name)
    with open(p, "w") as f:
        for r in rows:
            f.write(" ".join(str(x + shift) if isinstance(x, int) else x for x in r) + "\n")
    return p


def fake_verify(d, name, body):
    p = os.path.join(d, name)
    with open(p, "w") as f:
        f.write("#!/bin/sh\n" + body + "\n")
    os.chmod(p, os.stat(p).st_mode | stat.S_IXUSR)
    return p


def main():
    d = tempfile.mkdtemp(prefix="countcheck_")
    good = write(d, "good.txt", oa9())
    r = cs.count_check(good, 2, 3, 60)
    check("OA(9;2,4,3) verified", r["outcome"] == "verified", repr(r))

    rows = oa9()
    gone = rows.pop(4)
    broken = write(d, "broken.txt", rows)
    r = cs.count_check(broken, 2, 3, 60)
    check("row removed: gaps", r["outcome"] == "gaps", repr(r))
    cols, tup = r["missing"][0] if r["missing"] else ([], [])
    check("first gap is columns (0,1) tuple of the removed row",
          cols == [0, 1] and tup == gone[:2], repr(r["missing"][:1]))
    check("every reported gap is really missing",
          all(tuple(tp) not in {tuple(row[c] for c in cs_) for row in rows}
              for cs_, tp in r["missing"]), repr(r["missing"]))

    one = write(d, "one.txt", oa9(), shift=1)
    r = cs.count_check(one, 2, 3, 60)
    check("1-based copy verified", r["outcome"] == "verified", repr(r))

    rows = oa9()
    rows[0][1] = "-"
    wild = write(d, "wild.txt", rows)
    r = cs.count_check(wild, 2, 3, 60)
    check("don't-care entry: error, not judged", r["outcome"] == "error", repr(r))

    rag = os.path.join(d, "rag.txt")
    with open(rag, "w") as f:
        f.write("0 1 2\n0 1\n")
    r = cs.count_check(rag, 2, 3, 60)
    check("ragged file: error", r["outcome"] == "error", repr(r))

    r = cs.count_check(good, 5, 3, 60)
    check("k below t: error", r["outcome"] == "error", repr(r))

    kill = fake_verify(d, "kill.sh", "kill -9 $$")
    r = cs.run_ca_verify(kill, good, 2, 3, 1, 60)
    check("SIGKILL hands over to the count: verified", r["outcome"] == "verified", repr(r))
    check("the stop is reported", "ca_verify stopped" in r["stderr"], repr(r["stderr"]))
    r = cs.run_ca_verify(kill, broken, 2, 3, 1, 60)
    check("SIGKILL on a broken array: gaps", r["outcome"] == "gaps" and r["missing"], repr(r))

    plain = fake_verify(d, "plain.sh", "echo 'bad input' >&2; exit 2")
    r = cs.run_ca_verify(plain, good, 2, 3, 1, 60)
    check("ordinary error is not counted", r["outcome"] == "error" and "bad input" in r["stderr"], repr(r))

    check("memory stops recognised",
          cs.killed_for_memory(-9, "") and cs.killed_for_memory(137, "")
          and cs.killed_for_memory(1 + 1, "std::bad_alloc") and cs.killed_for_memory(2, "Out of memory"))
    check("other errors not taken for memory",
          not cs.killed_for_memory(2, "cannot open file") and not cs.killed_for_memory(None, ""))

    saved = cs.COUNT_MAX_CELLS
    cs.COUNT_MAX_CELLS = 10
    r = cs.count_check(good, 2, 3, 60)
    cs.COUNT_MAX_CELLS = saved
    check("cell cap stops the count", r["outcome"] == "error" and "C(4,2)" in r["stderr"], repr(r))

    r = cs.count_check(good, 2, 3, -1)
    check("time limit gives timeout", r["outcome"] == "timeout", repr(r))

    st = "ca_verify abc1234 2026-11-16 github-actions"
    check("stamp names the exact count when it did the check",
          cs.claim_stamp({"counted": True}, st) == "exact count abc1234 2026-11-16 github-actions"
          and cs.claim_stamp({"counted": False}, st) == st and cs.claim_stamp({}, st) == st)

    print("%d failed" % len(FAILS) if FAILS else "all passed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
