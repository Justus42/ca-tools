# smolen-2026-11-cphf3stage-g4: 6 arrays from one run of the 3-stage CPHF method: 4 below the table, 2 at cited best known sizes that had no array

Construction: the 3-stage method of Izquierdo-Marquez, Torres-Jimenez, Acevedo-Juarez and Avila-George (2018), own
implementation: a covering perfect hash family found by simulated annealing (cphf_sa.c) and expanded to a covering
array (expand.py), rows added greedily, then row deletion and re-annealing (nck.c, casa.c), with ca_profile.c for
coverage counts.

Built from: nothing but the programs below. No array of another author is used as a start or an ingredient.

Program: programs/ (three_stage.py, expand.py, cphf_sa.c, ca_profile.c, casa.c, nck.c; the same files as in
smolen-2026-11-cae-run-6). One run on 139 target sizes, one hour each, 8 workers. Per array:
- CA(1240; 4, 42, 4): `three_stage.py 4 4 42 1240 4 work/4_4_42/cphf3 120 600 3600 1`
- CA(803; 5, 14, 3): `three_stage.py 5 3 14 805 3 work/5_3_14/cphf3 120 600 3600 1`
- CA(4533; 5, 22, 4): `three_stage.py 5 4 22 4597 4 work/5_4_22/cphf3 120 600 3600 1`
- CA(4600; 5, 23, 4): `three_stage.py 5 4 23 4600 4 work/5_4_23/cphf3 120 600 3600 1`
- CA(4846; 5, 24, 4): `three_stage.py 5 4 24 4847 4 work/5_4_24/cphf3 120 600 3600 1`
- CA(2673; 6, 14, 3): `three_stage.py 6 3 14 2701 3 work/6_3_14/cphf3 120 600 3600 1`
The runs are seeded but stopped by wall-clock time, so a rerun reaches an array of about the same size, not
necessarily the same array. The submitted files are the certificates.

Each array was checked exactly (ca_verify on all t-sets when built, and again before submission).
