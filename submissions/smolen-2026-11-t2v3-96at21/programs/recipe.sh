#!/bin/sh
# Rebuild CA(21;2,96,3). Run from the repository root. Needs gcc and python 3. Deterministic (fixed seed 3 in clq).
set -e
P=$(pwd)/submissions/smolen-2026-11-t2v3-96at21/programs
D=$(mktemp -d); cd $D
gcc -O3 -DN=21 -o orb21 $P/orbN.c
gcc -O3 -o pool $P/pool.c
gcc -O3 -o clq $P/clq.c
./orb21 $P/G21_3.gen G21_3.reps
python3 $P/expand.py $P/G21_3.gen G21_3.reps 21 0 2 88 > a21_73.txt
./pool a21_73.txt > p73.txt
./clq p73.txt 3 500000 c73.txt
python3 $P/join.py a21_73.txt c73.txt > CA_21_2_96_3.txt
sha256sum a21_73.txt CA_21_2_96_3.txt
echo "output in $D"
