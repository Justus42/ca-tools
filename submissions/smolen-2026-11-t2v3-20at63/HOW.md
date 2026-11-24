# How this array was built

Construction: a 20-row array found by exhaustive search among arrays invariant under the group Z3 x Z3 acting on
the rows.

CA(20; 2, 63, 3).

The group Z3 x Z3 has 9 elements. It permutes rows 0 to 8 as it permutes its own elements, does the same on rows
9 to 17, and leaves rows 18 and 19 where they are. Applying a group element to a column gives another column. A
column whose 9 images are pairwise qualitatively independent (every pair of them shows all 9 symbol pairs) is kept,
one per orbit and up to renaming of symbols. There are 6,513,921 such orbits among 572,838,885 candidate columns.
Two orbits are joined when every column of one is qualitatively independent of every column of the other. Seven
mutually joined orbits are a covering array with 20 rows and 63 columns.

The program searches for every set of seven up to the normaliser of the group, which leaves 5,184 starting orbits
to try. The full search was run in two halves on an Apple M4 Max and both halves ran to completion, in 24,515 and
24,295 seconds. There are 5 sets of seven in the order used, all found at starting orbit 2610, and the other half
holds none. The array here is the first set. For that set the program also lists every further column that is
qualitatively independent of all 63 columns. There is none, so this array cannot take a 64th column.

The search is exhaustive and uses no random numbers. Programs programs/mkgrp.py (the group as row permutations)
and programs/orbq7.c (the search). These are the same two programs as in the submission
smolen-2026-11-t2v3-z3z3-18rows.

The array was checked exactly with ca_verify on all pairs of columns, and with the separate brute force check
programs/chk.py.

Replication. One script, programs/recipe_20at63.sh, builds the array from nothing and writes the recipe log
itself, with the sha256 of every program and output. Its short form searches starting orbit 2610 only and takes
about two minutes on one core. It was run twice in separate new folders on Linux x86_64. Both runs gave the file
of this submission, which is also byte for byte the file the full search wrote on the Apple machine. The logs are
programs/RECIPE_build.log and programs/RECIPE_replay.log. The full outputs of the two halves of the full search
are programs/orbq7_full_run_half0_log.txt and programs/orbq7_full_run_half1_log.txt.

Built from: nothing. The array has no input array. No array of Torres-Jimenez is an ingredient or start, and the
array does not have the fingerprint of one of his arrays.

Program: programs/ in this folder (recipe_20at63.sh, mkgrp.py, orbq7.c, chk.py). The search program orbq7.c was
written by an AI model for this project.

To rebuild:
    cd programs && bash recipe_20at63.sh mytag
which runs
    python3 mkgrp.py z3z3 0,0 2 > z_20_00_f2.txt
    cc -O3 -o orbq7 orbq7.c && ./orbq7 z_20_00_f2.txt 7 0 w20 5184 2610
To repeat the whole search (about seven hours on two cores):
    cd programs && bash recipe_20at63.sh mytag full
