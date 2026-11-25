# smolen-2026-11-formula-arrays-2: three more arrays from published constructions

CA(136; 5, 68, 2), CA(218; 5, 110, 2) and CA(53; 3, 704, 2). Each has the size of the best known value the table
cites for it, and the table had no array anyone could download at that size. The sizes stay with the cited rows.
This submission adds only the arrays.

Construction: published constructions only, one per array, named in claims.csv.
- The Paley construction from the quadratic residues of GF(q), q = 67 and q = 109 (2).
- The power construction of Colbourn and Torres-Jimenez, catalogue line Power CT11^3T3T3c (1).

Built from: the two Paley arrays are built from nothing but the formula. The power construction uses a distributing
hash family from the Bush orthogonal array on 11 symbols and two binary ingredients with 12 rows. The first is the
Paley array on 11 columns, built by formula. The second is miscCA(3, 8, 2), an array stored in the R package CAs
(GPL), which U. Groemping made from paleyCA(3, 23) with postopNCK. It is named in the credit of that claim.
No array of Torres-Jimenez is an ingredient or a start, and every array passed the fingerprint screen against
table/tj_fingerprints.csv and the withdrawn files.

Program: programs/build.R, the program of submission smolen-2026-11-formula-arrays, unchanged. It uses the R package
CAs 0.24.4 by Ulrike Groemping (CRAN). From this folder:

    Rscript programs/build.R claims.csv rebuilt

rebuilds all three files. The rebuild was run twice and compared with the stored files, and is identical, file for
file. As a control the same program rebuilt CA_67_4_67_2.txt and CA_43_3_242_2.txt of the earlier submission,
identical to the files in the table. Each array was checked exactly with ca_verify on all t-sets of columns.

AI tools used: yes
