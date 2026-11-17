# smolen-2026-11-cae-run-8: 6 arrays from the engine (0 below the table, 6 at cited best known sizes that had no array)

Construction: one per array, named in claims.csv and below. Constructions are published theorems (references in
builds_on); searches are column extension at the record number of rows (the idea of the CA Extender of
Torres-Jimenez, Acevedo-Juarez and Avila-George 2021) with this project's own annealer casa.c.

Built from: real arrays only: arrays of this table (named by file), table certificates and constructions, Bose
orthogonal arrays and construction functions of the R package CAs 0.24.4 by Ulrike Groemping (constructions; where a
CAs function uses stored data of other authors, claims.csv names them), and arrays of this same submission.

Program: programs/ (build.py with laws.py and recipes.json for constructions; build.R with recipes.csv for PCA
products; casa.c and chain_ext.py with the start files for searches). Per array:
- CA(1653; 4, 6, 6): augmentation of Colbourn 2014 (Theorem 2.2, one new symbol per class, tau = 2): Bush orthogonal array OA(5^4; 4, 6, 5) with its all-zero row, rows with mu <= 2 zeros expanded by all binary vectors, rows with 3 zeros by the even binary vectors, 4 renamed copies of the quilting array of Lemma 3.1 (36 rows), and the table's weight-class CA(21; 4, 6, 2). Rebuild: `python3 programs/augment.py 4 6 6 ../../table/arrays/CA_21_4_6_2_2c6505cd.txt CA_1653_4_6_6.txt` (programs/, seeded).
- CA(43989; 4, 6, 14): augmentation of Colbourn 2014 (Theorem 2.2, one new symbol per class, tau = 2): Bush orthogonal array OA(13^4; 4, 6, 13) with its all-zero row, rows with mu <= 2 zeros expanded by all binary vectors, rows with 3 zeros by the even binary vectors, 12 renamed copies of the quilting array of Lemma 3.1 (36 rows), and the table's weight-class CA(21; 4, 6, 2). Rebuild: `python3 programs/augment.py 4 6 14 ../../table/arrays/CA_21_4_6_2_2c6505cd.txt CA_43989_4_6_14.txt` (programs/, seeded).
- CA(669; 4, 224, 3): CAs 0.24.4 construction CYCLOTOMY (CAs:::labelToCode("CYCLOTOMY", 4, 224, 3)). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(687; 4, 230, 3): CAs 0.24.4 construction CYCLOTOMY (CAs:::labelToCode("CYCLOTOMY", 4, 230, 3)). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(813; 4, 272, 3): CAs 0.24.4 construction CYCLOTOMY (CAs:::labelToCode("CYCLOTOMY", 4, 272, 3)). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(831; 4, 278, 3): CAs 0.24.4 construction CYCLOTOMY (CAs:::labelToCode("CYCLOTOMY", 4, 278, 3)). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.

Each array was checked exactly (ca_profile when built, ca_verify on all t-sets before submission).
