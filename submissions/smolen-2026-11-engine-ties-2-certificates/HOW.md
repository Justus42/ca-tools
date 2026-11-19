# smolen-2026-11-engine-ties-2-certificates: 1 covering perfect hash families from the engine (0 below the table, 1 at cited best known sizes that had no array)

Construction: covering perfect hash families found by this project's own searches; each claim names its family file
and the expansion mode (affine, with restriction pairs where given: rows 2i and 2i+1 agree in their first d
coordinates, and the repeated runs are left out).

Built from: nothing but the search; no array or family of other authors.

Program: the searches are private engine code; every family is checked exactly by the table's certificate check.
Per family:
- CA(1377; 6, 9, 3) from families/family_CA_1377_6_9_3.txt, mode `affine pairs 4`: restricted Sherwood CPHF search (own rscphf), SCPHF(2; 9, 3, 6) with restriction pairs of dimension 4, expanded with repeated runs left out. Search: `rscphf 6 3 2 4 9 30 1 family.txt 0 60; rscphf expand family.txt 6 3 4 CA.txt`.
