#!/usr/bin/env python3
"""Tests of tools/priority.py and of its use in tools/build_frame.py (CONVENTIONS.md section 9).

Assertions: the submissions a row's notes name (anchored phrases only, existing folders only), the checks of
table/priority.csv, the priority date of a row (earliest of entry and submission, shared by rows holding the
same array), the order of tied rows by priority date instead of entry date, first_reached kept apart from the
named row when more constant rows win the headline, an empty first_reached on derived lines, and record()
writing pull_request and pushed lines from git history with GitHub answers replaced by a stand-in, and the
date of the paper a CITED row is cited from (basis paper, matched through references.csv).

Usage: test_priority.py   (prints PASS/FAIL lines and a summary; exit 1 on a failure)
"""
import csv
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tools"))
sys.path.insert(0, HERE)
import build_frame as bf  # noqa: E402
import priority  # noqa: E402
from test_build_frame import row, write_table  # noqa: E402

RESULTS = {"pass": 0, "fail": 0}


def check(cond, what):
    RESULTS["pass" if cond else "fail"] += 1
    print("%s  %s" % ("PASS" if cond else "FAIL", what), flush=True)
    return cond


def tree(root, slugs):
    table = os.path.join(root, "table")
    os.makedirs(table, exist_ok=True)
    for s in slugs:
        os.makedirs(os.path.join(root, "submissions", s), exist_ok=True)
    return table


def write_priority(table, lines):
    with open(os.path.join(table, "priority.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(priority.HEADER)
        w.writerows(lines)


def frame_in(root, rows, prio=(), slugs=(), **kw):
    table = tree(root, slugs)
    write_table(table, rows, **kw)
    if prio:
        write_priority(table, prio)
    lines, _, _ = bf.build(table)
    return [dict(zip(bf.FRAME_HEADER, l)) for l in lines]


def sub_row(t, v, k, n, entered, slug, sha):
    r = row(t, v, k, n, "VERIFIED", "S7", "", sha, entered)
    r["notes"] = "credit: someone; exceeds table: previous best 999; submission %s" % slug
    return r


def test_slugs_in():
    known = {"a-1", "b-2", "c-3", "d-4"}
    n = ("credit: x; submission a-1; pre-submission audit by y; checked before submission by two programs; "
         "beats 316 of submission b-2 by 1; from submissions/c-3/external.csv")
    check(priority.slugs_in(n, known) == ["a-1", "c-3"],
          "a row names its own submission and a deposit; mentions of other submissions in prose are not its own")
    check(priority.slugs_in("submission zz-9; x", known) == [],
          "a slug with no folder is not a submission")
    check(priority.slugs_in("x; construction certificate table/constructions/d-4/CA.cert.json", known) == ["d-4"],
          "a construction certificate names its submission")


def test_file_checks():
    good = [{"slug": "a-1", "date": "2026-11-13", "basis": "email", "evidence": "email to the maintainer"},
            {"slug": "a-1", "date": "2026-11-15T20:01:02Z", "basis": "pull_request", "evidence": "pr 81"}]
    check(priority.problems(good, priority.HEADER) == [], "a date and a UTC time are both accepted")
    bad = [{"slug": "a-1", "date": "13/11/2026", "basis": "rumour", "evidence": ""},
           {"slug": "b-2", "date": "2026-11-15", "basis": "pushed", "evidence": "c"},
           {"slug": "b-2", "date": "2026-11-16", "basis": "pull_request", "evidence": "d"}]
    p = priority.problems(bad, priority.HEADER)
    check(any("date" in x for x in p) and any("basis" in x for x in p) and any("evidence" in x for x in p)
          and any("more than one" in x for x in p), "bad date, basis, empty evidence and two automatic lines refused")
    check(priority.problems([], ["slug", "date"]) != [], "a wrong header is refused")


def test_row_dates_and_same_array():
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, ["s-1"])
        rows = [sub_row(3, 4, 20, 50, "2026-11-15", "s-1", "a" * 64),
                dict(row(3, 4, 20, 50, "VERIFIED", "S7", "", "a" * 64, "2026-11-20"), notes="exact check"),
                row(3, 4, 21, 60, "VERIFIED", "S7", "", "b" * 64, "2026-11-01")]
        write_table(table, rows)
        write_priority(table, [["s-1", "2026-11-13", "email", "email to the maintainer"],
                               ["s-1", "2026-11-15T20:00:00Z", "pull_request", "pr"]])
        d = priority.row_dates(rows, table)
    check(d[0] == "2026-11-13", "the email date before the pull request is the row's priority date")
    check(d[1] == "2026-11-13", "a later row with the same array keeps the earlier date")
    check(d[2] == "2026-11-01", "a row naming no submission keeps its entry date")


def test_tie_order_uses_priority():
    rows = [sub_row(3, 4, 20, 50, "2026-11-10", "early-entry", "a" * 64),
            sub_row(3, 4, 20, 50, "2026-11-12", "early-claim", "b" * 64)]
    with tempfile.TemporaryDirectory() as root:
        fr = frame_in(root, rows, slugs=["early-entry", "early-claim"])
    l = [x for x in fr if (x["t"], x["v"], x["k"]) == ("3", "4", "20")][0]
    check(l["id"] == "t3-v4-k20-1" and l["first_reached"] == "t3-v4-k20-1",
          "without priority lines the earlier entry is named and first")
    prio = [["early-entry", "2026-11-09T12:00:00Z", "pull_request", "pr 1"],
            ["early-claim", "2026-11-05", "deposit", "doi:10.5281/zenodo.1"]]
    with tempfile.TemporaryDirectory() as root:
        fr = frame_in(root, rows, prio, slugs=["early-entry", "early-claim"])
    l = [x for x in fr if (x["t"], x["v"], x["k"]) == ("3", "4", "20")][0]
    check(l["id"] == "t3-v4-k20-2" and l["first_reached"] == "t3-v4-k20-2",
          "an earlier deposit wins the tie over an earlier merge: named and first reached")


def test_first_reached_apart_from_headline():
    rows = [sub_row(3, 4, 20, 50, "2026-11-01", "first-one", "a" * 64),
            sub_row(3, 4, 20, 50, "2026-11-12", "more-constant", "b" * 64)]
    man = [["CA_50_3_20_4.txt", 3, 4, 20, 50, "exceeds_snapshot", "a" * 64, "S7", "", "", 1],
           ["CA_50_3_20_4_bbbbbbbb.txt", 3, 4, 20, 50, "equals_best", "b" * 64, "S7", "", "", 3]]
    with tempfile.TemporaryDirectory() as root:
        fr = frame_in(root, rows, slugs=["first-one", "more-constant"], manifest=man)
    l = [x for x in fr if (x["t"], x["v"], x["k"]) == ("3", "4", "20")][0]
    check(l["id"] == "t3-v4-k20-2" and l["first_reached"] == "t3-v4-k20-1",
          "more constant rows take the headline; first reached stays with the earlier row")


def test_derived_lines_empty():
    rows = [row(3, 5, 20, 100), row(3, 4, 40, 400)]
    with tempfile.TemporaryDirectory() as root:
        fr = frame_in(root, rows)
    der = [x for x in fr if x["basis"] == "derived"]
    rws = [x for x in fr if x["basis"] == "row"]
    check(der and all(x["first_reached"] == "" for x in der), "a derived line has an empty first_reached")
    check(rws and all(x["first_reached"] for x in rws), "every row line has a first_reached")


def git(root, *a, env=None):
    e = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
             GIT_COMMITTER_EMAIL="t@t", **(env or {}))
    return subprocess.run(["git", "-C", root] + list(a), check=True, capture_output=True, text=True, env=e).stdout


def test_record():
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, [])
        git(root, "init", "-q", "-b", "main")
        rows = [row(3, 4, 30, 70)]
        write_table(table, rows)
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base", env={"GIT_COMMITTER_DATE": "2026-11-01T10:00:00+00:00"})
        git(root, "checkout", "-q", "-b", "contrib")
        os.makedirs(os.path.join(root, "submissions", "via-pr"))
        open(os.path.join(root, "submissions", "via-pr", "claims.csv"), "w").write("x\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "submit", env={"GIT_COMMITTER_DATE": "2026-11-02T10:00:00+00:00"})
        git(root, "checkout", "-q", "main")
        git(root, "merge", "-q", "--no-ff", "-m", "Merge pull request #7 from someone/via-pr", "contrib",
            env={"GIT_COMMITTER_DATE": "2026-11-04T10:00:00+00:00"})
        os.makedirs(os.path.join(root, "submissions", "pushed-one"))
        open(os.path.join(root, "submissions", "pushed-one", "claims.csv"), "w").write("x\n")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "own", env={"GIT_COMMITTER_DATE": "2026-11-05T08:30:00-06:00"})
        rows += [sub_row(3, 4, 20, 50, "2026-11-04", "via-pr", "a" * 64),
                 sub_row(3, 4, 21, 55, "2026-11-05", "pushed-one", "b" * 64)]
        write_table(table, rows)
        calls = []

        def fake_gh(endpoint):
            calls.append(endpoint)
            if endpoint.endswith("/pulls/7"):
                return {"number": 7, "created_at": "2026-11-02T11:00:00Z"}
            return []
        old = os.environ.get("GITHUB_REPOSITORY")
        os.environ["GITHUB_REPOSITORY"] = "o/r"
        try:
            n = priority.record(table, gh=fake_gh)
            again = priority.record(table, gh=fake_gh)
        finally:
            if old is None:
                del os.environ["GITHUB_REPOSITORY"]
            else:
                os.environ["GITHUB_REPOSITORY"] = old
        got = {d["slug"]: d for d in priority.read(table)}
    check(n == 2 and again == 0, "two submissions recorded once; a second run adds nothing")
    check(got.get("via-pr", {}).get("date") == "2026-11-02T11:00:00Z" and got["via-pr"]["basis"] == "pull_request"
          and got["via-pr"]["evidence"] == "https://github.com/o/r/pull/7",
          "a merged pull request gives its opening time, found through the merge commit")
    check(got.get("pushed-one", {}).get("date") == "2026-11-05T14:30:00Z" and got["pushed-one"]["basis"] == "pushed",
          "a submission pushed to main gives its commit time in UTC")
    check(priority.problems(list(got.values()), priority.HEADER) == [], "the written file passes its own checks")


def test_paper_dates():
    rows = [row(7, 2, 8, 128, "CITED", "S7", "doi:10.1/LATER", entered="2026-11-24"),
            row(7, 2, 8, 128, "CITED", "S7", "arXiv:2001.00001v3", entered="2026-11-24")]
    refs = [["id", "keywords", "reference", "doi"], ["later-x2015", "", "A. Later, X (2015)", "10.1/later"],
            ["early-y2010", "", "B. Early, Y, arXiv:2001.00001 (2010)", "arXiv:2001.00001"]]
    prio = [["later-x2015", "2015-12-30", "paper", "doi:10.1/later"],
            ["early-y2010", "2010-06-30", "paper", "arXiv:2001.00001v3"]]
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, [])
        write_table(table, rows)
        with open(os.path.join(table, "references.csv"), "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(refs)
        d = priority.row_dates(rows, table, known=set())
        check(d == ["2026-11-24", "2026-11-24"], "without paper lines a cited row keeps its entry date")
        write_priority(table, prio)
        d = priority.row_dates(rows, table, known=set())
        check(d == ["2015-12-30", "2010-06-30"], "a cited row takes the date of the paper its snapshot_id names (case and arXiv version ignored)")
        lines, _, _ = bf.build(table)
    l = [dict(zip(bf.FRAME_HEADER, x)) for x in lines]
    l = [x for x in l if (x["t"], x["v"], x["k"]) == ("7", "2", "8")][0]
    check(l["id"] == "t7-v2-k8-2" and l["first_reached"] == "t7-v2-k8-2",
          "between two cited rows entered the same day, the earlier paper is named and first reached")
    vr = [row(7, 2, 8, 128, "VERIFIED", "S7", "doi:10.1/later", "c" * 64, "2026-11-24")]
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, [])
        write_table(table, vr)
        with open(os.path.join(table, "references.csv"), "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(refs)
        write_priority(table, prio)
        check(priority.row_dates(vr, table, known=set()) == ["2026-11-24"], "a VERIFIED row does not take a paper date")
    tr = [row(3, 7, 2448, 2275, "CITED", "S1", "colbourn-2024-11-ug", entered="2026-08-23"),
          row(3, 7, 2451, 2275, "CITED", "S7", "doi:10.1/later", entered="2026-11-09")]
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, [])
        write_table(table, tr)
        with open(os.path.join(table, "references.csv"), "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(refs)
        write_priority(table, prio + [["colbourn-2024-11-ug", "2024-11-30", "table", "test snapshot"]])
        check(priority.row_dates(tr, table, known=set()) == ["2024-11-30", "2015-12-30"],
              "a CITED row from a published table takes the snapshot's date (basis table)")
    lr = [row(3, 7, 183, 1309, "CITED", "S1", "colbourn-2024-11-ug", entered="2026-08-23"),
          row(3, 7, 183, 1309, "CITED", "S1", "colbourn-2024-11-ug", entered="2026-08-23")]
    lr[0]["builds_on"] = "early-y2010;later-x2015"
    lr[1]["builds_on"] = "early-y2010;unknown-z2020"
    with tempfile.TemporaryDirectory() as root:
        table = tree(root, [])
        write_table(table, lr)
        with open(os.path.join(table, "references.csv"), "w", newline="", encoding="utf-8") as f:
            csv.writer(f, lineterminator="\n").writerows(refs)
        write_priority(table, prio + [["colbourn-2024-11-ug", "2024-11-30", "table", "test snapshot"]])
        check(priority.row_dates(lr, table, known=set()) == ["2015-12-30", "2024-11-30"],
              "a table row takes the date of the newest paper its builds_on names, only when every paper there has a date")
        write_priority(table, prio + [["colbourn-2024-11-ug", "2024-11-30", "paper", "wrong basis"]])
        check(priority.row_dates(lr, table, known=set()) == ["2026-08-23", "2026-08-23"],
              "a snapshot dates its rows only through a line with basis table")


def main():
    for fn in (test_slugs_in, test_file_checks, test_row_dates_and_same_array, test_tie_order_uses_priority, test_paper_dates,
               test_first_reached_apart_from_headline, test_derived_lines_empty, test_record):
        fn()
    print("%d passed, %d failed" % (RESULTS["pass"], RESULTS["fail"]))
    return 1 if RESULTS["fail"] else 0


if __name__ == "__main__":
    sys.exit(main())
