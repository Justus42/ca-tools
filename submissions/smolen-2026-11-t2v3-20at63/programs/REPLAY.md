# Replay record for CA(20; 2, 63, 3)

sha256 of the array of this submission:
- CA_20_2_63_3.txt  14122f0eb24e772938a74b1fc14dea025c4e2555de7c7d3f4dddf49d312a38b1

The array was first written on 2026-11-21 by the full search on an Apple M4 Max (macOS, arm64), run in two halves
(orbq7 z_00.txt 7 0 z00_0 2 0 and the same with 2 1, where z_00.txt is the group file the recipe calls
z_20_00_f2.txt, byte for byte). Both halves ran to completion. Their full outputs are
orbq7_full_run_half0_log.txt and orbq7_full_run_half1_log.txt.

Two separate executions of recipe_20at63.sh in its short form on Linux x86_64 (gcc 13.3.0, Python 3.13) on
2026-11-23 gave this identical file. Each run was made in a new empty folder.

1. Tag build. Log RECIPE_build.log.
2. Tag replay. Log RECIPE_replay.log.

So the file is the same on two kinds of machine. The search uses integers only and no random numbers.

The short form searches starting orbit 2610 only (orbq7 z_20_00_f2.txt 7 0 w20 5184 2610). Its full output in run
1 is orbq7_short_run_log.txt. The full search has not been repeated a second time.

To replay, run `bash recipe_20at63.sh sometag` in this folder (it needs cc and python3) and compare the sha256 of
the file it writes into run_sometag/. It takes about two minutes on one core.
