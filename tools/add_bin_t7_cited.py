#!/usr/bin/env python3
"""add_bin_t7_cited.py - appends to table/ca_table.csv, as CITED S7 rows, the published sizes of
binary covering arrays at strengths 7 to 10 (the scope added in 6dbe83e), from three papers read
in full:

  CKRS  C. J. Colbourn, G. Keri, P. P. Rivas Soriano and J.-C. Schlage-Puchta, Covering and
        radius-covering arrays: constructions and classification, Discrete Appl. Math. 158 (2010)
        1158-1180: Lemma 2.1 and the binary part of Table 7.
  TOWER J. Torres-Jimenez, I. Izquierdo-Marquez, R. N. Kacker and D. R. Kuhn, Tower of covering
        arrays, Discrete Appl. Math. 190-191 (2015) 141-146: Tables 2, 3, 5 and 6.
  BB    J. Torres-Jimenez, I. Izquierdo-Marquez, A. Gonzalez-Gomez and H. Avila-George, A branch and
        bound algorithm to derive a direct construction for binary covering arrays, MICAI 2015,
        Part I, LNAI 9413, pp. 1-20, doi:10.1007/978-3-319-27060-9_13: Table 2.

Each value is the one the paper prints (one row per paper and size). Values a paper quotes from
another are not entered. Three printed Table 2 values of BB are not entered: (t, k) = (10, 12)
1356, (8, 14) 1356 and (10, 29) 142596 differ from the paper's own Eq. 1 (1365, 1365, 142506),
and 1356 at (10, 12) is below the exact value 1365.

Usage, from the repository root:
    python3 tools/add_bin_t7_cited.py YYYY-MM-DD           # dry run: print the rows
    python3 tools/add_bin_t7_cited.py YYYY-MM-DD --apply   # append them
"""
import csv, io, sys, datetime

DATE = sys.argv[1]
datetime.datetime.strptime(DATE, "%Y-%m-%d")
APPLY = "--apply" in sys.argv[2:]

SRC = {
    "CKRS2010": dict(
        doi="doi:10.1016/j.dam.2010.03.008", ref="fuse-ckrs2010",
        cite="Colbourn, Keri, Rivas Soriano and Schlage-Puchta, Discrete Appl. Math. 158 (2010) 1158-1180",
        credit="C. J. Colbourn, G. Keri, P. P. Rivas Soriano and J.-C. Schlage-Puchta 2010"),
    "Tower2015": dict(
        doi="doi:10.1016/j.dam.2015.03.010", ref="tower-tikk2015",
        cite="Torres-Jimenez, Izquierdo-Marquez, Kacker and Kuhn, Tower of covering arrays, Discrete Appl. Math. 190-191 (2015) 141-146",
        credit="J. Torres-Jimenez, I. Izquierdo-Marquez, R. N. Kacker and D. R. Kuhn 2015"),
    "BB2015": dict(
        doi="doi:10.1007/978-3-319-27060-9_13", ref="direct-tiga2015",
        cite="Torres-Jimenez, Izquierdo-Marquez, Gonzalez-Gomez and Avila-George, MICAI 2015, LNAI 9413, pp. 1-20",
        credit="J. Torres-Jimenez, I. Izquierdo-Marquez, A. Gonzalez-Gomez and H. Avila-George 2015"),
}
ROWS = [
    (7, 8, 128, 'BB2015', 'Table 2 p.14 (s=1)'),
    (7, 8, 128, 'CKRS2010', 'Table 7 p.1168 row (8;7) key a=OA'),
    (7, 9, 170, 'BB2015', 'Table 2 p.14 (s=2)'),
    (7, 9, 170, 'Tower2015', 'Table 5 p.6 TCA column'),
    (7, 10, 240, 'BB2015', 'Table 2 p.14 (s=3)'),
    (7, 10, 222, 'CKRS2010', 'Lemma 2.1 p.1159; Table 7 p.1169 row (10;7) range 192-222 key p=Lemma 2.1'),
    (7, 10, 224, 'Tower2015', 'Table 2 p.4 TCA column (base CA(7;2,5,2)); Table 3 p.4 New N; Table 5 p.6 TCA column'),
    (7, 11, 330, 'BB2015', 'Table 2 p.14 (s=4)'),
    (7, 11, 242, 'CKRS2010', 'Lemma 2.1 p.1159; Table 7 p.1169 row (11;7) range 224-242 key p=Lemma 2.1'),
    (7, 11, 240, 'Tower2015', 'Table 5 p.6 TCA column'),
    (7, 12, 440, 'BB2015', 'Table 2 p.14 (s=5)'),
    (7, 12, 264, 'CKRS2010', 'Lemma 2.1 p.1159; Table 7 p.1169 row (12;7) range 224-264 key p=Lemma 2.1'),
    (7, 12, 256, 'Tower2015', 'Table 3 p.4 New N; Table 5 p.6 TCA column'),
    (7, 13, 572, 'BB2015', 'Table 2 p.14 (s=6)'),
    (7, 13, 392, 'CKRS2010', 'Table 7 p.1169 row (13;7) range 224-392 key z=(8) or (9)'),
    (7, 13, 256, 'Tower2015', 'Table 3 p.4 New N'),
    (7, 14, 728, 'BB2015', 'Table 2 p.14 (s=7)'),
    (7, 14, 520, 'CKRS2010', 'Table 7 p.1169 row (14;7) range 224-520 key z=(8) or (9)'),
    (7, 14, 256, 'Tower2015', 'Table 3 p.4 New N'),
    (7, 15, 910, 'BB2015', 'Table 2 p.14 (s=8)'),
    (7, 15, 256, 'Tower2015', 'Table 3 p.4 New N'),
    (7, 16, 1120, 'BB2015', 'Table 2 p.14 (s=9)'),
    (7, 16, 256, 'Tower2015', 'Table 2 p.4 TCA column (base CA(8;2,11,2)); Table 3 p.4 New N'),
    (7, 17, 1360, 'BB2015', 'Table 2 p.14 (s=10)'),
    (7, 18, 1632, 'BB2015', 'Table 2 p.14 (s=11)'),
    (7, 19, 1938, 'BB2015', 'Table 2 p.14 (s=12)'),
    (7, 20, 2280, 'BB2015', 'Table 2 p.14 (s=13)'),
    (7, 21, 2660, 'BB2015', 'Table 2 p.14 (s=14)'),
    (7, 22, 3080, 'BB2015', 'Table 2 p.14 (s=15)'),
    (7, 23, 3542, 'BB2015', 'Table 2 p.14 (s=16)'),
    (7, 24, 4048, 'BB2015', 'Table 2 p.14 (s=17)'),
    (7, 25, 4600, 'BB2015', 'Table 2 p.14 (s=18)'),
    (7, 26, 5200, 'BB2015', 'Table 2 p.14 (s=19)'),
    (7, 27, 5850, 'BB2015', 'Table 2 p.14 (s=20)'),
    (7, 28, 6552, 'BB2015', 'Table 2 p.14 (s=21)'),
    (7, 29, 7308, 'BB2015', 'Table 2 p.14 (s=22)'),
    (7, 30, 8120, 'BB2015', 'Table 2 p.14 (s=23)'),
    (7, 31, 8990, 'BB2015', 'Table 2 p.14 (s=24)'),
    (7, 32, 9920, 'BB2015', 'Table 2 p.14 (s=25)'),
    (8, 9, 256, 'BB2015', 'Table 2 p.14 (s=1)'),
    (8, 9, 256, 'CKRS2010', 'Table 7 p.1168 row (9;8) key a=OA'),
    (8, 10, 341, 'BB2015', 'Table 2 p.14 (s=2)'),
    (8, 11, 496, 'BB2015', 'Table 2 p.14 (s=3) bold (improved); Table 4 p.15 New bound'),
    (8, 11, 563, 'CKRS2010', 'Table 7 p.1169 row (11;8) range 385-563 key z=(8) or (9)'),
    (8, 11, 448, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (8, 12, 715, 'BB2015', 'Table 2 p.14 (s=4) bold (improved); Table 4 p.15 New bound'),
    (8, 12, 795, 'CKRS2010', 'Table 7 p.1169 row (12;8) range 448-795 key z=(8) or (9)'),
    (8, 12, 480, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (8, 13, 1001, 'BB2015', 'Table 2 p.14 (s=5) bold (improved); Table 4 p.15 New bound'),
    (8, 13, 1051, 'CKRS2010', 'Table 7 p.1169 row (13;8) range 448-1051 key z'),
    (8, 13, 512, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (8, 14, 1307, 'CKRS2010', 'Table 7 p.1169 row (14;8) range 448-1307 key z'),
    (8, 15, 1820, 'BB2015', 'Table 2 p.14 (s=7)'),
    (8, 16, 2380, 'BB2015', 'Table 2 p.14 (s=8)'),
    (8, 17, 3060, 'BB2015', 'Table 2 p.14 (s=9)'),
    (8, 18, 3876, 'BB2015', 'Table 2 p.14 (s=10)'),
    (8, 19, 4845, 'BB2015', 'Table 2 p.14 (s=11)'),
    (8, 20, 5985, 'BB2015', 'Table 2 p.14 (s=12)'),
    (8, 21, 7315, 'BB2015', 'Table 2 p.14 (s=13)'),
    (8, 22, 8855, 'BB2015', 'Table 2 p.14 (s=14)'),
    (8, 23, 10626, 'BB2015', 'Table 2 p.14 (s=15)'),
    (8, 24, 12650, 'BB2015', 'Table 2 p.14 (s=16)'),
    (8, 25, 14950, 'BB2015', 'Table 2 p.14 (s=17)'),
    (8, 26, 17550, 'BB2015', 'Table 2 p.14 (s=18)'),
    (8, 27, 20475, 'BB2015', 'Table 2 p.14 (s=19)'),
    (8, 28, 23751, 'BB2015', 'Table 2 p.14 (s=20)'),
    (8, 29, 27405, 'BB2015', 'Table 2 p.14 (s=21)'),
    (8, 30, 31465, 'BB2015', 'Table 2 p.14 (s=22)'),
    (8, 31, 35960, 'BB2015', 'Table 2 p.14 (s=23)'),
    (8, 32, 40920, 'BB2015', 'Table 2 p.14 (s=24)'),
    (8, 33, 46376, 'BB2015', 'Table 2 p.14 (s=25)'),
    (9, 10, 512, 'BB2015', 'Table 2 p.14 (s=1)'),
    (9, 10, 512, 'CKRS2010', 'Table 7 p.1169 row (10;9) key a=OA'),
    (9, 11, 682, 'BB2015', 'Table 2 p.14 (s=2)'),
    (9, 12, 992, 'BB2015', 'Table 2 p.14 (s=3) bold (improved); Table 4 p.15 New bound'),
    (9, 12, 1230, 'CKRS2010', 'Table 7 p.1169 row (12;9) range 770-1230 key z'),
    (9, 12, 896, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (9, 13, 1430, 'BB2015', 'Table 2 p.14 (s=4) bold (improved); Table 4 p.15 New bound'),
    (9, 13, 2002, 'CKRS2010', 'Table 7 p.1169 row (13;9) range 896-2002 key z'),
    (9, 13, 960, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (9, 14, 2002, 'BB2015', 'Table 2 p.14 (s=5) bold (improved); Table 4 p.15 New bound'),
    (9, 14, 3014, 'CKRS2010', 'Table 7 p.1169 row (14;9) range 896-3014 key z'),
    (9, 14, 1024, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (9, 15, 2730, 'BB2015', 'Table 2 p.14 (s=6)'),
    (9, 16, 3640, 'BB2015', 'Table 2 p.14 (s=7)'),
    (9, 17, 4760, 'BB2015', 'Table 2 p.14 (s=8)'),
    (9, 18, 6120, 'BB2015', 'Table 2 p.14 (s=9)'),
    (9, 19, 7752, 'BB2015', 'Table 2 p.14 (s=10)'),
    (9, 20, 9690, 'BB2015', 'Table 2 p.14 (s=11)'),
    (9, 21, 11970, 'BB2015', 'Table 2 p.14 (s=12)'),
    (9, 22, 14630, 'BB2015', 'Table 2 p.14 (s=13)'),
    (9, 23, 17710, 'BB2015', 'Table 2 p.14 (s=14)'),
    (9, 24, 21252, 'BB2015', 'Table 2 p.14 (s=15)'),
    (9, 25, 25300, 'BB2015', 'Table 2 p.14 (s=16)'),
    (9, 26, 29900, 'BB2015', 'Table 2 p.14 (s=17)'),
    (9, 27, 35100, 'BB2015', 'Table 2 p.14 (s=18)'),
    (9, 28, 40950, 'BB2015', 'Table 2 p.14 (s=19)'),
    (9, 29, 47502, 'BB2015', 'Table 2 p.14 (s=20)'),
    (9, 30, 54810, 'BB2015', 'Table 2 p.14 (s=21)'),
    (9, 31, 62930, 'BB2015', 'Table 2 p.14 (s=22)'),
    (9, 32, 71920, 'BB2015', 'Table 2 p.14 (s=23)'),
    (9, 33, 81840, 'BB2015', 'Table 2 p.14 (s=24)'),
    (9, 34, 92752, 'BB2015', 'Table 2 p.14 (s=25)'),
    (10, 11, 1024, 'BB2015', 'Table 2 p.14 (s=1)'),
    (10, 11, 1024, 'CKRS2010', 'Table 7 p.1169 row (11;10) key a=OA'),
    (10, 13, 2016, 'BB2015', 'Table 2 p.14 (s=3) bold (improved); Table 4 p.15 New bound'),
    (10, 13, 2491, 'CKRS2010', 'Table 7 p.1169 row (13;10) range 1540-2491 key z'),
    (10, 13, 1792, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (10, 14, 3004, 'BB2015', 'Table 2 p.14 (s=4) bold (improved); Table 4 p.15 New bound'),
    (10, 14, 4081, 'CKRS2010', 'Table 7 p.1169 row (14;10) range 1792-4081 key z'),
    (10, 14, 1920, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (10, 15, 4368, 'BB2015', 'Table 2 p.14 (s=5)'),
    (10, 15, 2048, 'Tower2015', 'Table 5 p.6 TCA column; Table 6 p.6 New N'),
    (10, 16, 6188, 'BB2015', 'Table 2 p.14 (s=6)'),
    (10, 17, 8568, 'BB2015', 'Table 2 p.14 (s=7)'),
    (10, 18, 11628, 'BB2015', 'Table 2 p.14 (s=8)'),
    (10, 19, 15504, 'BB2015', 'Table 2 p.14 (s=9)'),
    (10, 20, 20349, 'BB2015', 'Table 2 p.14 (s=10)'),
    (10, 21, 26334, 'BB2015', 'Table 2 p.14 (s=11)'),
    (10, 22, 33649, 'BB2015', 'Table 2 p.14 (s=12)'),
    (10, 23, 42504, 'BB2015', 'Table 2 p.14 (s=13)'),
    (10, 24, 53130, 'BB2015', 'Table 2 p.14 (s=14)'),
    (10, 25, 65780, 'BB2015', 'Table 2 p.14 (s=15)'),
    (10, 26, 80730, 'BB2015', 'Table 2 p.14 (s=16)'),
    (10, 27, 98280, 'BB2015', 'Table 2 p.14 (s=17)'),
    (10, 28, 118755, 'BB2015', 'Table 2 p.14 (s=18)'),
    (10, 30, 169911, 'BB2015', 'Table 2 p.14 (s=20)'),
    (10, 31, 201376, 'BB2015', 'Table 2 p.14 (s=21)'),
    (10, 32, 237336, 'BB2015', 'Table 2 p.14 (s=22)'),
    (10, 33, 278256, 'BB2015', 'Table 2 p.14 (s=23)'),
    (10, 34, 324632, 'BB2015', 'Table 2 p.14 (s=24)'),
    (10, 35, 376992, 'BB2015', 'Table 2 p.14 (s=25)'),
]


def construction(src, where):
    if src == "CKRS2010":
        if "Lemma 2.1" in where:
            return "from the Steiner system S(5,6,12) (Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010, Lemma 2.1)"
        if "OA" in where:
            return "orthogonal array of index one, as listed in Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010, Table 7"
        return ("as listed in Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010, Table 7, key z "
                "(their constructions (8) or (9))")
    if src == "Tower2015":
        return ("tower of covering arrays from a base covering array (Torres-Jimenez, Izquierdo-Marquez, "
                "Kacker and Kuhn 2015)")
    return ("direct construction from binomial coefficients: a union of weight classes chosen by branch and "
            "bound (Torres-Jimenez, Izquierdo-Marquez, Gonzalez-Gomez and Avila-George 2015)")


raw = open("table/ca_table.csv", "rb").read().decode("utf-8")
lines = raw.split("\r\n"); assert lines[-1] == ""
rows = list(csv.reader(lines[:-1]))
hdr = rows[0]; assert hdr[:5] == ["t", "v", "k", "N", "tier"] and len(hdr) == 17
if any(r[4] == "CITED" and r[1] == "2" and int(r[0]) >= 7 for r in rows[1:]):
    sys.exit("the rows of add_bin_t7_cited.py are already in the table")
assert len(set((t, k, s) for t, k, N, s, w in ROWS)) == len(ROWS)
new = []
for t, k, N, src, where in ROWS:
    d = SRC[src]
    detail = "%s, %s: CA(%d; %d, %d, 2)" % (d["cite"], where, N, t, k)
    notes = ("credit: %s (the construction and the size, %s, %s); at entry: no earlier row at strengths 7 to 10; "
             "no array file checked here" % (d["credit"], d["doi"], where))
    new.append([t, 2, k, N, "CITED", "S7", detail, d["doi"], "", "", DATE, notes, "", "",
                construction(src, where), d["ref"], ""])
for r in new:
    print("CA(%d; %d, %d, 2)  %s" % (r[3], r[0], r[2], r[7]))
if APPLY:
    b = io.StringIO(); w = csv.writer(b, lineterminator="\r\n")
    for r in new:
        w.writerow(r)
    open("table/ca_table.csv", "wb").write((raw + b.getvalue()).encode("utf-8"))
    print("%d CITED S7 rows added; date %s" % (len(new), DATE))
else:
    print("dry run: %d rows; add --apply to append them" % len(new))
