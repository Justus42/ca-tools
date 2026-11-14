# How this array was built

Construction: the automorphism group of the table's own CA(18;2,52,3), extended to a seventh triple of rows, then an
exact census of the invariant columns and an exact pool of further compatible columns.

CA(21; 2, 96, 3).

1. The group. The own CA(18;2,52,3) has an automorphism group G of order 108, transitive on its 18 rows. Its rows
   split into 6 triples, and on each triple a column is a polynomial from F3 to F3. The main orbit of 36 columns is
   quadratic on every triple, and each of its columns is fixed by an element of order 3 that rotates its symbols.

2. The extension. Such a column cannot continue onto a single new row, but it can continue onto a seventh triple
   that the element rotates. A homomorphism from G to Z3 extends G to 21 rows (7 triples).
   programs/G21_3.gen holds the three generators of the extended group.

3. The census. programs/orbN.c runs through all 3^21 columns and keeps the orbits whose columns are pairwise
   qualitatively independent. Three orbits, of sizes 36, 36 and 1, are mutually compatible and give a
   CA(21;2,73,3) (programs/expand.py).

4. The completion. programs/pool.c lists every column compatible with all 73 (71,194 columns up to relabelling).
   programs/clq.c, a local search with the fixed seed 3, finds 23 of them that are pairwise compatible.
   programs/join.py writes the 96 columns.

The array was checked exactly with ca_verify on all 4,560 pairs of columns, and again by an independent count.

Built from: the automorphism group of the table's own CA(18;2,52,3). No array of Torres-Jimenez is an ingredient or
start.

Program: programs/recipe.sh compiles and runs the programs above. It is deterministic. A complete run from scratch
reproduced the array exactly (programs/recipe_log.txt). Needs gcc and python 3.
