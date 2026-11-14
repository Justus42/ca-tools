#!/usr/bin/env python3
"""lexicon.py - the family of a construction text.

table/lexicon.csv is an ordered list of patterns (regular expressions) over the construction text of
table/ca_table.csv; the first pattern that matches gives the family. table/families.csv is the list of
families: the 31 labels of the R package CAs with their CAs spelling (column cas_label), then the
families CAs has no label for (cas_label empty). Trailing steps in a text (fuse, postop ...) do not
change the family. Conventions, section 8.

usage: lexicon.py "construction text"     print its family
       lexicon.py --count                 rows of ca_table.csv per family
       lexicon.py --check                 exit 1 if a construction text matches no pattern, a pattern
                                          names a family that is not in families.csv, or a CAs label
                                          appears twice
"""
import csv, os, re, sys, collections

T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "table")

def load():
    fams = list(csv.DictReader(open(os.path.join(T, "families.csv"), newline="")))
    pats = sorted(csv.DictReader(open(os.path.join(T, "lexicon.csv"), newline="")), key=lambda r: int(r["order"]))
    return fams, [(re.compile(r["pattern"]), r["family"]) for r in pats]

def family(text, pats):
    for p, f in pats:
        if p.search(text): return f
    return None

def main(argv):
    fams, pats = load()
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    if argv[0] not in ("--count", "--check"):
        print(family(argv[0], pats)); return 0
    names = [f["family"] for f in fams]; bad = []
    bad += [f"pattern names unknown family {f}" for _, f in pats if f not in names]
    labs = [f["cas_label"] for f in fams if f["cas_label"]]
    bad += [f"CAs label twice: {l}" for l in set(labs) if labs.count(l) > 1]
    bad += [f"family twice: {n}" for n in set(names) if names.count(n) > 1]
    cnt = collections.Counter(); miss = collections.Counter()
    for r in csv.DictReader(open(os.path.join(T, "ca_table.csv"), newline="")):
        f = family(r["construction"], pats)
        if f is None: miss[r["construction"]] += 1
        else: cnt[f] += 1
    bad += [f"no pattern for {n} row(s): {s[:100]}" for s, n in miss.items()]
    if argv[0] == "--count":
        for n in names: print(f"{cnt[n]:6d}  {n}")
    for b in bad: print("PROBLEM", b)
    print(f"lexicon: {len(pats)} patterns, {len(names)} families ({len(labs)} with a CAs label), {sum(cnt.values())} rows placed, {len(bad)} problem(s)")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
