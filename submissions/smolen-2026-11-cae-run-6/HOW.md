# smolen-2026-11-cae-run-6: 9 arrays from one engine search run: 4 below the table, 5 at cited best known sizes that had no array

Construction: one per array, named in claims.csv and below. Constructions are published theorems (references in
builds_on); searches are column extension at the record number of rows (the idea of the CA Extender of
Torres-Jimenez, Acevedo-Juarez and Avila-George 2021) with this project's own annealer casa.c.

Built from: real arrays only: arrays of this table (named by file), table certificates and constructions, Bose
orthogonal arrays and construction functions of the R package CAs 0.24.4 by Ulrike Groemping (constructions; where a
CAs function uses stored data of other authors, claims.csv names them), and arrays of this same submission.

Program: programs/ (build.py with laws.py and recipes.json for constructions; build.R with recipes.csv for PCA
products; casa.c and chain_ext.py with the start files for searches). Per array:
- CA(113; 2, 100, 7): column extension at the record size from PCA/direct product PCA(CAs CKRS, CAs CS_CMMSSY) (CAs productPCA/productCA) (89 columns, 113 rows) padded at random (Python seed 3107) (casa 113 2 100 7 1 900 0.5 0.99995 CA_113_2_100_7.txt programs/start_CA_113_2_100_7.txt). Rebuild: `casa 113 2 100 7 1 900 0.5 0.99995 CA_113_2_100_7.txt programs/start_CA_113_2_100_7.txt` (seeded, deterministic).
- CA(120; 2, 111, 7): column extension at the record size from table array CA_119_2_109_7.txt (Column extension at fixed N by simulated annealing, starting from the PCA product of Bose ) (109 columns, 119 rows) padded at random (Python seed 3448) (casa 120 2 111 7 1 900 0.5 0.99995 CA_120_2_111_7.txt programs/start_CA_120_2_111_7.txt). Rebuild: `casa 120 2 111 7 1 900 0.5 0.99995 CA_120_2_111_7.txt programs/start_CA_120_2_111_7.txt` (seeded, deterministic).
- CA(1457; 6, 13, 3): cyclic CPHF search (own symcphf, the project's CPHF paper) and expansion (symcphf 6 3 13 1 -nmax 2 -time 900; cphf_tools expand). Rebuild: `symcphf 6 3 13 1 -nmax 2 -time 900; cphf_tools expand` (programs/, seeded).
- CA(2675; 6, 14, 3): 3-stage CPHF method (own code) (three_stage.py 6 3 14 2701 3 work/6_3_14/cphf3 120 600 1800 1). Rebuild: `three_stage.py 6 3 14 2701 3 work/6_3_14/cphf3 120 600 1800 1` (programs/, seeded).
- CA(3439; 6, 17, 3): 3-stage CPHF method (own code) (three_stage.py 6 3 17 3633 4 work/6_3_17/cphf3 120 600 1800 1). Rebuild: `three_stage.py 6 3 17 3633 4 work/6_3_17/cphf3 120 600 1800 1` (programs/, seeded).
- CA(48; 2, 38, 5): frozen-core extension at the record size from CAs 0.24.4 construction recBoseCA_CA (CAs:::labelToCode("recBoseCA_CA", 2, 36, 5)) (48 rows, 36 columns) (extv 2 5 programs/start_CA_48_2_38_5.txt 48 36 0 2 1 300 1.5 CA_48_2_38_5.txt). Rebuild: `extv 2 5 programs/start_CA_48_2_38_5.txt 48 36 0 2 1 300 1.5 CA_48_2_38_5.txt` (seeded, deterministic).
- CA(75; 3, 28, 3): column extension at the record size from table array CA_72_3_27_3.txt (column extension + tabu repair and row-deletion post-optimisation starting from CA(69;3,26) (27 columns, 72 rows) padded at random (Python seed 871) (casa 75 3 28 3 1 900 0.5 0.99995 CA_75_3_28_3.txt programs/start_CA_75_3_28_3.txt). Rebuild: `casa 75 3 28 3 1 900 0.5 0.99995 CA_75_3_28_3.txt programs/start_CA_75_3_28_3.txt` (seeded, deterministic).
- CA(805; 5, 14, 3): 3-stage CPHF method (own code) (three_stage.py 5 3 14 805 3 work/5_3_14/cphf3 120 600 1800 1). Rebuild: `three_stage.py 5 3 14 805 3 work/5_3_14/cphf3 120 600 1800 1` (programs/, seeded).
- CA(917; 5, 16, 3): 3-stage CPHF method (own code) (three_stage.py 5 3 16 920 3 work/5_3_16/cphf3 120 600 1800 1). Rebuild: `three_stage.py 5 3 16 920 3 work/5_3_16/cphf3 120 600 1800 1` (programs/, seeded).

Each array was checked exactly (ca_profile when built, ca_verify on all t-sets before submission).
