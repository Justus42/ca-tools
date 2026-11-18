# smolen-2026-11-engine-below-1: four arrays from published recursions over this project's newest arrays

Construction: each array is a published recursion applied to arrays this project put into the table in the week of 2026-11-08 to
2026-11-12. The recursions had not been re-run on the new arrays. The ca-tools engine found them by recomputing
every recursion against the current table. `python3 submissions/smolen-2026-11-engine-below-1/programs/rebuild.py`
rebuilds all four from the table's own files and compares their sha256 with the files here.

| Array | Recursion | Ingredients (table files) | Best known before |
| --- | --- | --- | --- |
| CA(28; 3, 56, 2) | Chateauneuf-Kreher doubling | CA_20_3_28_2.txt, CA_8_2_35_2.txt | 29 |
| CA(29; 3, 64, 2) | Chateauneuf-Kreher doubling | CA_21_3_32_2.txt, CA_8_2_35_2.txt | 30 at 58 columns, 31 from 59 to 68 |
| CA(39; 2, 10283, 3) | profile product (Colbourn, Torres-Jimenez 2013) | CA_24_2_209_3.txt, CA_18_2_52_3.txt | 40 at 9207, 41 to 11898 |
| CA(42; 2, 21307, 3) | profile product (Colbourn, Torres-Jimenez 2013) | CA_27_2_436_3.txt, CA_18_2_52_3.txt | 43 at 20000; nothing listed past 20000 |

Built from: the table's own files only, named in the table above; the binary halves CA(20; 3, 28, 2) and
CA(21; 3, 32, 2) are this project's (submission smolen-2026-11-t3-orbit-free), CA(8; 2, 35, 2) is the Kleitman-Spencer
array of CAs, and CA(24; 2, 209, 3), CA(27; 2, 436, 3) and CA(18; 2, 52, 3) are this project's (submissions
smolen-2026-11-t2v3-z3z3-18rows and smolen-2026-11-d16-products).

Program: programs/rebuild.py, run from the root of ca-tools, rebuilds the four arrays and compares their sha256 with
the files here; with --write it writes them. The doubling is [A|A] over [B|1-B]; the product renames each column so
the two chosen rows of each factor become constant, drops them, merges the two remaining chosen rows into one, and
drops the columns where both factors' chosen rows agree, as in Colbourn and Torres-Jimenez 2013, Cor 4.5.

Every array passes ca_verify over all column sets. No Torres-Jimenez array is an ingredient or a start.
