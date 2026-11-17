#!/usr/bin/env python3
"""Deposit claims whose full check does not fit the table workflow's budget per array: planned by
check_upgrades.py (kind "deposit"), checked in shards, combined, and entered by external_array.py with
--exact-result. Without a result the submission waits (exit 4, nothing entered); a result whose outcome
does not match its shard outputs is refused; an array shown not to be covering fails (exit 1)."""
import csv, json, os, random, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); REPO = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import external_array as ea
import check_submission as cs
import builds_on as bo

TINY = "0.000001"


def oa9(rng):
    rows = [[a, b, (a + b) % 3, (a + 2 * b) % 3] for a in range(3) for b in range(3)]
    rng.shuffle(rows)
    return rows


def write_array(path, rows):
    with open(path, "w") as f:
        f.write("".join(" ".join(map(str, r)) + "\n" for r in rows))


def claim(root, name, rows):
    p = os.path.join(root, name)
    write_array(p, rows)
    _, _, sha, _ = ea.canonicalize_stream(p, 3, p + ".canon")
    return dict(t="2", v="3", k="4", N=str(len(rows)), location="local:" + name, sha256=sha,
                source_detail="test deposit", construction="test array",
                builds_on="oa-bush1952", credit="Test Person", notes="")


def make_sub(base, slug, claims):
    sub = os.path.join(base, "submissions", slug)
    os.makedirs(sub)
    with open(os.path.join(sub, "external.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=ea.EXT_CLAIMS_HEADER, lineterminator="\n")
        w.writeheader(); w.writerows(claims)
    return sub


def run(args):
    p = subprocess.run([sys.executable] + args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return p.returncode, p.stdout


def shards(sub, root, td, out, plan_path, nshards):
    up = os.path.join(TOOLS, "check_upgrades.py")
    rc, txt = run([up, sub, "--plan", plan_path, "--table-budget-minutes", TINY, "--local-root", root, "--table-dir", td])
    assert rc == 0, txt
    doc = json.load(open(plan_path))
    for e in doc["entries"]:
        e["shards"] = nshards
    doc["tasks"] = ["u%d-s%d" % (e["index"], j) for e in doc["entries"] for j in range(nshards)]
    json.dump(doc, open(plan_path, "w"))
    for task in doc["tasks"]:
        rc, txt = run([up, sub, "--run", plan_path, "--task", task, "--out", os.path.join(out, "tasks"),
                       "--threads", "1", "--local-root", root, "--table-dir", td])
        assert rc == 0, txt
    rc, txt = run([up, sub, "--results", plan_path, "--tasks", os.path.join(out, "tasks"), "--out", os.path.join(out, "res")])
    return rc, txt, doc


def enter(sub, root, td, exe, res=None):
    args = [os.path.join(TOOLS, "external_array.py"), sub, "--table-dir", td, "--ca-verify", exe, "--threads", "1",
            "--budget-minutes", TINY, "--local-root", root, "--apply"]
    if res:
        args += ["--exact-result", res]
    return run(args)


def rows_from(td, slug):
    return [r for r in csv.DictReader(open(os.path.join(td, "ca_table.csv"))) if "submissions/%s/external.csv" % slug in r["notes"]]


def main():
    fails = 0
    def check(name, ok, detail=""):
        nonlocal fails
        print("%s: %s" % (name, "PASS" if ok else "FAIL " + detail[-1500:]))
        fails += not ok
    rng = random.Random(11)
    with tempfile.TemporaryDirectory() as d:
        root = os.path.join(d, "deposit"); os.makedirs(root)
        td = os.path.join(d, "table"); os.makedirs(td)
        for fn, hdr, rows in (("ca_table.csv", cs.TABLE_HEADER, []), ("EXTERNAL.csv", ea.EXTERNAL_HEADER, []),
                              ("references.csv", bo.HEADER, [["oa-bush1952", r"\bbush\b", "K. A. Bush, Orthogonal arrays of "
                                                             "index unity, Ann. Math. Statist. 23 (1952) 426-434", ""]])):
            with open(os.path.join(td, fn), "w", newline="") as f:
                w = csv.writer(f, lineterminator="\n"); w.writerow(hdr); w.writerows(rows)
        exe = os.path.join(d, "ca_verify")
        subprocess.run(["cc", "-O3", "-pthread", "-o", exe, os.path.join(REPO, "ca_verify.c")], check=True)

        import re
        def env(fn, name):
            m = re.search(r'^  %s: "([^"]+)"' % name, open(os.path.join(REPO, ".github", "workflows", fn)).read(), re.M)
            return m and m.group(1)
        same = (env("table-page.yml", "THREADS") == env("certificate-check.yml", "TABLE_THREADS") == str(ea.TABLE_THREADS)
                and float(env("table-page.yml", "BUDGET_MINUTES")) == float(env("certificate-check.yml", "TABLE_BUDGET_MINUTES"))
                == ea.TABLE_BUDGET_MINUTES)
        check("table-page.yml, certificate-check.yml and external_array.py use the same budget per array", same)
        check("deferred under a tiny budget", ea.deferred(9, 2, 3, 4, 2, 1e-4))
        check("not deferred under the table budget", not ea.deferred(9, 2, 3, 4))

        good = [claim(root, "a.txt", oa9(rng)), claim(root, "b.txt", oa9(rng))]
        sub = make_sub(d, "test-deposit-good", good)
        rc, txt = enter(sub, root, td, exe)
        check("no result yet: waiting, exit 4", rc == 4 and "WAITING" in txt, txt)
        check("no result yet: nothing entered", not rows_from(td, "test-deposit-good"))

        out = os.path.join(d, "good")
        rc, txt, doc = shards(sub, root, td, out, os.path.join(d, "good.json"), 3)
        check("plan of kind deposit, every claim deferred, 3 shards each",
              doc["kind"] == "deposit" and len(doc["entries"]) == 2 and len(doc["tasks"]) == 6, json.dumps(doc)[:500])
        check("shards combined: both claims verified", rc == 0 and txt.count("(VERIFIED)") == 2, txt)

        bad_res = os.path.join(d, "tampered")
        shutil.copytree(os.path.join(out, "res"), bad_res)
        r = json.load(open(os.path.join(bad_res, "result.json")))
        r["entries"][0]["outcome"] = "incomplete"
        json.dump(r, open(os.path.join(bad_res, "result.json"), "w"))
        rc, txt = enter(sub, root, td, exe, bad_res)
        check("result that disagrees with its shard outputs: refused", rc not in (0, 4) and "the result says incomplete" in txt and not rows_from(td, "test-deposit-good"), txt)

        rc, txt = enter(sub, root, td, exe, os.path.join(out, "res"))
        got = rows_from(td, "test-deposit-good")
        check("entered with the result: exit 0, two VERIFIED rows", rc == 0 and len(got) == 2
              and all(x["tier"] == "VERIFIED" and "certificate-check.yml" in x["notes"] for x in got), txt)

        broken = oa9(rng); broken[0] = list(broken[1])
        sub2 = make_sub(d, "test-deposit-broken", [claim(root, "c.txt", broken)])
        out2 = os.path.join(d, "broken")
        rc, txt, _ = shards(sub2, root, td, out2, os.path.join(d, "broken.json"), 2)
        check("array with a gap: the shard check fails it", rc == 1 and "NOT A COVERING ARRAY" in txt, txt)
        rc, txt = enter(sub2, root, td, exe, os.path.join(out2, "res"))
        check("array with a gap: not entered, exit 1", rc == 1 and "NOT A COVERING ARRAY" in txt and not rows_from(td, "test-deposit-broken"), txt)
    print("deposit shards: %s" % ("all passed" if not fails else "%d failed" % fails))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
