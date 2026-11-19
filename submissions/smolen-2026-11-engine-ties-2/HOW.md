# smolen-2026-11-engine-ties-2: 4 arrays from the engine (2 below the table, 2 at cited best known sizes that had no array)

Construction: one per array, named in claims.csv and below. Constructions are published theorems (references in
builds_on); searches are column extension at the record number of rows (the idea of the CA Extender of
Torres-Jimenez, Acevedo-Juarez and Avila-George 2021) with this project's own annealer casa.c.

Built from: real arrays only: arrays of this table (named by file), table certificates and constructions, Bose
orthogonal arrays and construction functions of the R package CAs 0.24.4 by Ulrike Groemping (constructions; where a
CAs function uses stored data of other authors, claims.csv names them), and arrays of this same submission.

Program: programs/ (build.py with laws.py and recipes.json for constructions; build.R with recipes.csv for PCA
products; casa.c and chain_ext.py with the start files for searches). Per array:
- CA(1647; 4, 6, 6): augmentation of an orthogonal array of index one with quilting arrays for classes of new symbols, Colbourn 2014 Theorem 2.2 (application B) of [table array CA_21_4_6_2_2c6505cd.txt (tools/own_arrays, array file CA_21_4_6_2_2c6505cd.txt: weight-class array built here: bina)] {'classes': [1, 1, 1, 1], 'sources': ['programs/inputs/QA_NP1_4_6_51.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt']}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(43983; 4, 6, 14): augmentation of an orthogonal array of index one with quilting arrays for classes of new symbols, Colbourn 2014 Theorem 2.2 (application B) of [table array CA_21_4_6_2_2c6505cd.txt (tools/own_arrays, array file CA_21_4_6_2_2c6505cd.txt: weight-class array built here: bina)] {'classes': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 'sources': ['programs/inputs/QA_NP1_4_6_51.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt', 'programs/inputs/QA_N1_4_6_36.txt']}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(73; 2, 301, 5): PCA/direct product PCA(hit CA_25_2_6_5.txt, hit CA_53_2_52_5.txt) (CAs productPCA/productCA). Rebuild: `Rscript programs/build.R programs/recipes.csv rebuilt ../../table/arrays`.
- CA(74; 2, 312, 5): PCA/direct product PCA(hit CA_25_2_6_5.txt, hit CA_54_2_54_5.txt) (CAs productPCA/productCA). Rebuild: `Rscript programs/build.R programs/recipes.csv rebuilt ../../table/arrays`.

Each array was checked exactly (ca_profile when built, ca_verify on all t-sets before submission).
