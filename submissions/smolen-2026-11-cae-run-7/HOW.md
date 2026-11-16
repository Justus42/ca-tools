# smolen-2026-11-cae-run-7: 13 arrays from the engine (0 below the table, 13 at cited best known sizes that had no array)

Construction: one per array, named in claims.csv and below. Constructions are published theorems (references in
builds_on); searches are column extension at the record number of rows (the idea of the CA Extender of
Torres-Jimenez, Acevedo-Juarez and Avila-George 2021) with this project's own annealer casa.c.

Built from: real arrays only: arrays of this table (named by file), table certificates and constructions, Bose
orthogonal arrays and construction functions of the R package CAs 0.24.4 by Ulrike Groemping (constructions; where a
CAs function uses stored data of other authors, claims.csv names them), and arrays of this same submission.

Program: programs/ (build.py with laws.py and recipes.json for constructions; build.R with recipes.csv for PCA
products; casa.c and chain_ext.py with the start files for searches). Per array:
- CA(135; 4, 9, 3): derived array, CKRS 2010 (7) of [table array CA_405_5_10_3.txt (frozen-core extension of table array CA_405_5_9_3.txt (Dwyer CA_Database source code "DeMu)]. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(15625; 6, 7, 5): CAs 0.24.4 construction cphfCA (CAs:::labelToCode("cphfCA", 6, 7, 5)) with the stored CPHFs of Wagner, Colbourn and Simos 2022. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(1786; 4, 108, 4): CAs 0.24.4 construction cphfCA (CAs:::labelToCode("cphfCA", 4, 108, 4)) with the stored CPHFs of Wagner, Colbourn and Simos 2022. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(20476; 6, 21, 4): CAs 0.24.4 construction cphfCA (CAs:::labelToCode("cphfCA", 6, 21, 4)) with the stored CPHFs of Wagner, Colbourn and Simos 2022. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(208; 5, 104, 2): CAs 0.24.4 construction PALEY (CAs:::labelToCode("PALEY", 5, 104, 2)). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(373; 2, 251, 13): PCA/direct product PCA(hit CA_169_2_14_13.txt, hit CA_217_2_18_13.txt) (CAs productPCA/productCA). Rebuild: `Rscript programs/build.R programs/recipes.csv rebuilt ../../table/arrays`.
- CA(38; 2, 5763, 3): profile product of Colbourn and Torres-Jimenez 2013 (Thm 4.2 / Cor 4.5), 3 symbols of [table array CA_24_2_209_3.txt (Built in ca-tools 2026-11-10 in two steps, both run by programs/recipe_item123.sh, which w); table array CA_17_2_29_3_72088afb.txt (tools/own_arrays, array file CA_17_2_29_3_72088afb.txt: simulated annealing with Nurmela-s)] {'i': 20, 'j': 21, 'p': 7, 'q': 16}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(41; 2, 11898, 3): profile product of Colbourn and Torres-Jimenez 2013 (Thm 4.2 / Cor 4.5), 3 symbols of [table array CA_27_2_436_3.txt (Built in ca-tools 2026-11-10 (debate 16) in two steps. Step 1, profile product (method of ); table array CA_17_2_29_3_72088afb.txt (tools/own_arrays, array file CA_17_2_29_3_72088afb.txt: simulated annealing with Nurmela-s)] {'i': 4, 'j': 5, 'p': 7, 'q': 16}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(528; 2, 323, 16): product of Colbourn and Torres-Jimenez 2013 Cor 4.3 (rows differing in every column removed) of [table array CA_256_2_17_16.txt (CAs 0.24.4 construction fuseBushtCA (CAs:::labelToCode("fuseBushtCA", 2, 17, 16)). Built i); table array CA_288_2_19_16.txt (CAs 0.24.4 construction projBoseCA (CAs:::labelToCode("projBoseCA", 2, 19, 16)). Built in )] {'s': 1, 'r': 15}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(560; 2, 361, 16): product of Colbourn and Torres-Jimenez 2013 Cor 4.3 (rows differing in every column removed) of [table array CA_288_2_19_16.txt (CAs 0.24.4 construction projBoseCA (CAs:::labelToCode("projBoseCA", 2, 19, 16)). Built in ); table array CA_288_2_19_16.txt (CAs 0.24.4 construction projBoseCA (CAs:::labelToCode("projBoseCA", 2, 19, 16)). Built in )] {'s': 15, 'r': 1}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(702; 2, 441, 18): product of Colbourn and Torres-Jimenez 2013 Cor 4.3 (rows differing in every column removed) of [table array CA_360_2_21_18.txt (CAs 0.24.4 construction projBoseCA (CAs:::labelToCode("projBoseCA", 2, 21, 18)). Built in ); table array CA_360_2_21_18.txt (CAs 0.24.4 construction projBoseCA (CAs:::labelToCode("projBoseCA", 2, 21, 18)). Built in )] {'s': 17, 'r': 1}. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(8184; 4, 20, 8): CAs 0.24.4 construction scphfCA (CAs:::labelToCode("scphfCA", 4, 20, 8)) with stored SCPHFs (Sherwood et al. 2006, Walker and Colbourn 2009, Colbourn, Lanus and Sarkar 2018). Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.
- CA(9880; 3, 16, 20): ordered design plus binary patches, Cohen-Colbourn-Ling 2008 Construction 1 of [table array CA_17_3_16_2_0f12b71b.txt (tools/own_arrays, array file CA_17_3_16_2_0f12b71b.txt: SAT built here (tools/own_arrays/c)]. Rebuild: `python3 programs/build.py programs/recipes.json rebuilt ../..`.

Each array was checked exactly (ca_profile when built, ca_verify on all t-sets before submission).
