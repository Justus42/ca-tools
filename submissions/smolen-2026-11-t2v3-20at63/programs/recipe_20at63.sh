#!/bin/bash
# recipe_20at63.sh  Builds CA(20;2,63,3) from nothing and logs with hashes.
#   Exhaustive orbit search, group Z3 x Z3 on 20 rows (two regular orbits of 9 rows and 2 fixed rows).
#   No input array and no random numbers.
# usage: bash recipe_20at63.sh TAG        (writes everything into the new folder run_TAG/ and RECIPE_TAG.log)
#        bash recipe_20at63.sh TAG full   (the whole search in two halves instead of the one representative)
# The short form searches only representative 2610 of 5184, where the full search finds its sets of seven orbits.
# Needs cc, python3, sha256sum or shasum.
set -e
cd "$(dirname "$0")"; TAG=${1:?give a tag}; MODE=${2:-short}; D=run_$TAG; [ -e "$D" ] && { echo "$D exists, nothing overwritten"; exit 1; }
mkdir "$D"; LOG=$PWD/RECIPE_$TAG.log; : > "$LOG"
sha(){ if command -v sha256sum >/dev/null 2>&1; then sha256sum "$1" | cut -c1-64; else shasum -a 256 "$1" | cut -c1-64; fi; }
say(){ echo "$*" | tee -a "$LOG"; }
say "recipe_20at63 tag $TAG mode $MODE on $(uname -sm); cc: $(cc --version | head -1); python: $(python3 --version 2>&1)"
for f in recipe_20at63.sh orbq7.c mkgrp.py chk.py; do say "sha256 $f $(sha $f)"; done
cc -O3 -o "$D/orbq7" orbq7.c
cd "$D"
C="python3 ../mkgrp.py z3z3 0,0 2 > z_20_00_f2.txt"; python3 ../mkgrp.py z3z3 0,0 2 > z_20_00_f2.txt
say "step1 | $C | out z_20_00_f2.txt $(sha z_20_00_f2.txt)"
if [ "$MODE" = full ]; then
  C="./orbq7 z_20_00_f2.txt 7 0 w20 2 0 and ./orbq7 z_20_00_f2.txt 7 0 w20b 2 1"
  ./orbq7 z_20_00_f2.txt 7 0 w20 2 0 > step2.out 2>&1 & P0=$!
  ./orbq7 z_20_00_f2.txt 7 0 w20b 2 1 > step2b.out 2>&1 & P1=$!
  while kill -0 $P0 2>/dev/null || kill -0 $P1 2>/dev/null; do sleep 600; echo "$(date +%H:%M) half 0: $(tail -n 1 step2.out | cut -c1-90) | half 1: $(tail -n 1 step2b.out | cut -c1-90)"; done
  wait $P0; wait $P1
  say "step2 | $C | no seed, both halves run to completion | half 0: $(grep COMPLETE step2.out) | half 1: $(grep COMPLETE step2b.out)"
else
  C="./orbq7 z_20_00_f2.txt 7 0 w20 5184 2610"; ./orbq7 z_20_00_f2.txt 7 0 w20 5184 2610 > step2.out 2>&1
  say "step2 | $C | no seed, representative 2610 only | $(grep 'clique #1' step2.out) | $(grep COMPLETE step2.out)"
fi
say "step2 out w20_dump_20_63.txt $(sha w20_dump_20_63.txt)"
cp w20_dump_20_63.txt CA_20_2_63_3.txt; say "check | $(python3 ../chk.py CA_20_2_63_3.txt 2 3)"
say "DONE CA_20_2_63_3.txt sha256 $(sha CA_20_2_63_3.txt)"
