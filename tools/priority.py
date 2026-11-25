#!/usr/bin/env python3
"""Priority dates of the table rows (table/CONVENTIONS.md, section 9).

table/priority.csv has one line per piece of evidence that a submission's arrays existed by a date:
slug,date,basis,evidence. basis is one of BASIS_VALUES. date is YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ (UTC);
a date without a time stands for the start of that day. The priority date of a submission is the earliest
date among its lines.

The priority date of a row is the earliest of its entry date and the priority dates of the submission it
names in its notes, taken over every row that holds the same array (array_sha256) or the same family
(family_sha256), so an exact check entered later keeps the date of the array it checks.

Usage on main (table-page.yml): python3 tools/priority.py record [--table-dir table]
adds a pull_request or pushed line for every submission named by a row that has neither yet. It reads git
history and asks GitHub (gh api) for the pull request and its opening time.
"""
import csv
import io
import json
import os
import re
import subprocess
import sys

HEADER = ["slug", "date", "basis", "evidence"]
BASIS_VALUES = ("pull_request", "pushed", "email", "deposit", "paper")
AUTO_BASIS = ("pull_request", "pushed")
SLUG = r"[A-Za-z0-9._-]+"
SLUG_RE = re.compile(r"^%s$" % SLUG)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}Z)?$")
NOTE_PATTERNS = (
    re.compile(r"(?:^|; )submission (%s?)(?=[;,]|$)" % SLUG),
    re.compile(r"from submissions/(%s)/[a-z_]+\.csv" % SLUG),
    re.compile(r"(?:^|; )construction certificate table/constructions/(%s)/" % SLUG),
)
PR_MERGE_RE = re.compile(r"^Merge pull request #(\d+) ")
PR_SQUASH_RE = re.compile(r"\(#(\d+)\)$")


def path(table_dir):
    return os.path.join(table_dir, "priority.csv")


def read(table_dir):
    p = path(table_dir)
    if not os.path.exists(p):
        return []
    with open(p, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def problems(lines, header):
    out = []
    if header != HEADER:
        out.append("header is %s, expected %s" % (",".join(header), ",".join(HEADER)))
        return out
    seen = set()
    for n, d in enumerate(lines, 2):
        if not SLUG_RE.match(d["slug"] or ""):
            out.append("line %d: slug %r" % (n, d["slug"]))
        if not DATE_RE.match(d["date"] or ""):
            out.append("line %d: date %r is not YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ" % (n, d["date"]))
        if d["basis"] not in BASIS_VALUES:
            out.append("line %d: basis %r is not one of %s" % (n, d["basis"], ", ".join(BASIS_VALUES)))
        if not (d["evidence"] or "").strip():
            out.append("line %d: evidence is empty" % n)
        key = (d["slug"], d["basis"], d["date"])
        if key in seen:
            out.append("line %d: repeats slug, basis and date of an earlier line" % n)
        seen.add(key)
    autos = [d["slug"] for d in lines if d["basis"] in AUTO_BASIS]
    for s in sorted({s for s in autos if autos.count(s) > 1}):
        out.append("slug %s has more than one pull_request or pushed line" % s)
    return out


def check_file(table_dir):
    p = path(table_dir)
    if not os.path.exists(p):
        return ["%s is missing" % p]
    raw = open(p, "rb").read()
    if b"\r" in raw:
        return ["%s contains CR characters" % p]
    rd = csv.reader(io.StringIO(raw.decode("utf-8")))
    header = next(rd, [])
    return ["%s: %s" % (p, x) for x in problems(read(table_dir), header)]


def submission_dates(table_dir):
    """{slug: earliest date}"""
    out = {}
    for d in read(table_dir):
        if d["slug"] not in out or d["date"] < out[d["slug"]]:
            out[d["slug"]] = d["date"]
    return out


def slugs_in(notes, known):
    """the submissions a row's notes name as its own, kept only if that folder exists"""
    found = []
    for p in NOTE_PATTERNS:
        for s in p.findall(notes or ""):
            if s in known and s not in found:
                found.append(s)
    return found


def known_slugs(repo):
    out = set()
    for sub in ("submissions", os.path.join("table", "constructions")):
        d = os.path.join(repo, sub)
        if os.path.isdir(d):
            out.update(x for x in os.listdir(d) if os.path.isdir(os.path.join(d, x)))
    return out


def row_dates(rows, table_dir, known=None):
    """the priority date of every row, in file order; known: the submission folder names, when the folders
    themselves are not checked out"""
    repo = os.path.dirname(os.path.abspath(table_dir))
    known = known_slugs(repo) if known is None else known
    sub = submission_dates(table_dir)
    out = []
    for r in rows:
        ds = [r.get("entered") or ""] + [sub[s] for s in slugs_in(r.get("notes"), known) if s in sub]
        ds = [d for d in ds if d]
        out.append(min(ds) if ds else "")
    best = {}
    for r, d in zip(rows, out):
        for col in ("array_sha256", "family_sha256"):
            h = (r.get(col) or "").strip()
            if h and d and (h not in best or d < best[h]):
                best[h] = d
    for i, r in enumerate(rows):
        for col in ("array_sha256", "family_sha256"):
            h = (r.get(col) or "").strip()
            if h and h in best and (not out[i] or best[h] < out[i]):
                out[i] = best[h]
    return out


def git(repo, *args):
    return subprocess.run(["git", "-C", repo] + list(args), check=True, capture_output=True,
                          text=True).stdout.strip()


def gh_json(endpoint):
    r = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True)
    if r.returncode != 0:
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        return None


def utc(stamp):
    """an ISO time with an offset, as git prints it, in UTC with Z"""
    import datetime
    t = datetime.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def first_commit(repo, slug):
    for sub in ("submissions", "table/constructions"):
        out = git(repo, "log", "--diff-filter=A", "--format=%H", "--reverse", "--", "%s/%s/" % (sub, slug))
        if out:
            return out.splitlines()[0]
    return ""


def pr_of(repo, sha, gh):
    """the pull request that brought commit sha to main: GitHub's link, else the first merge or squash
    commit on main after it whose subject names a pull request"""
    repo_name = os.environ.get("GITHUB_REPOSITORY", "")
    if repo_name:
        js = gh("repos/%s/commits/%s/pulls" % (repo_name, sha))
        if isinstance(js, list):
            for p in js:
                if p.get("merged_at") and p.get("base", {}).get("ref") == "main":
                    return int(p["number"])
    m = PR_SQUASH_RE.search(git(repo, "log", "-1", "--format=%s", sha))
    if m:
        return int(m.group(1))
    merges = git(repo, "log", "--merges", "--ancestry-path", "--reverse", "--format=%H %s", "%s..HEAD" % sha)
    for ln in merges.splitlines():
        h, _, s = ln.partition(" ")
        first_parent = subprocess.run(["git", "-C", repo, "merge-base", "--is-ancestor", sha, h + "^1"])
        if first_parent.returncode == 0:
            continue
        m = PR_MERGE_RE.match(s)
        return int(m.group(1)) if m else None
    return None


def evidence_for(repo, slug, gh=gh_json):
    """(date, basis, evidence) for a submission from git history and GitHub, or None"""
    sha = first_commit(repo, slug)
    if not sha:
        return None
    repo_name = os.environ.get("GITHUB_REPOSITORY", "")
    n = pr_of(repo, sha, gh)
    if n is not None and repo_name:
        js = gh("repos/%s/pulls/%d" % (repo_name, n))
        if isinstance(js, dict) and js.get("created_at"):
            return (utc(js["created_at"]), "pull_request", "https://github.com/%s/pull/%d" % (repo_name, n))
    return (utc(git(repo, "log", "-1", "--format=%cI", sha)), "pushed", "commit %s" % sha[:12])


def record(table_dir, gh=gh_json):
    """append a pull_request or pushed line for every submission named by a row that has none"""
    repo = os.path.dirname(os.path.abspath(table_dir))
    with open(os.path.join(table_dir, "ca_table.csv"), newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    lines = read(table_dir)
    have = {d["slug"] for d in lines if d["basis"] in AUTO_BASIS}
    known = known_slugs(repo)
    todo = []
    for r in rows:
        for s in slugs_in(r.get("notes"), known):
            if s not in have and s not in todo:
                todo.append(s)
    added = []
    for s in todo:
        e = evidence_for(repo, s, gh)
        if e is None:
            print("priority: no commit adds %s; left out" % s, file=sys.stderr)
            continue
        added.append({"slug": s, "date": e[0], "basis": e[1], "evidence": e[2]})
    if not added and os.path.exists(path(table_dir)):
        return 0
    lines.extend(added)
    lines.sort(key=lambda d: (d["slug"], d["date"], d["basis"]))
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=HEADER, lineterminator="\n")
    w.writeheader()
    w.writerows(lines)
    with open(path(table_dir), "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    for d in added:
        print("priority: %s %s %s (%s)" % (d["slug"], d["date"], d["basis"], d["evidence"]))
    return len(added)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    table_dir = argv[argv.index("--table-dir") + 1] if "--table-dir" in argv else \
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "table")
    if argv and argv[0] == "record":
        n = record(table_dir)
        print("priority: %d line%s added" % (n, "" if n == 1 else "s"))
        return 0
    if argv and argv[0] == "check":
        p = check_file(table_dir)
        for x in p:
            print(x)
        return 1 if p else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
