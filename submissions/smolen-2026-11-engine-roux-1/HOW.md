# smolen-2026-11-engine-roux-1: CA(139190; 5, 2604, 5) by Corollary 2.2 of Martirosyan and Colbourn 2005

The array is not stored. Its construction certificate is, and tools/construction_cert.py (kind roux-1) rebuilds it.

Theorem. S. S. Martirosyan and C. J. Colbourn, Recursive constructions of covering arrays, Bayreuth. Math. Schr. 74
(2005) 266-275, Corollary 2.2: CAN(t, 2l, v) <= CAN(t, l, v) + (v - 1) CAN(t - 1, l, v) + CAN(t - 2, l, v^2).

Ingredients, each a VERIFIED row of this table, rebuilt from its own recipe and matched by its array_sha256, first
1302 columns used:
- A = CA(49985; 5, 1562, 5), the cyclic covering perfect hash family CPHF(16; 1562, 5, 5) of this project
  (table/certificates/CPHF_16_1562_5_5.txt), expanded;
- C = CA(7445; 4, 1454, 5), the covering perfect hash family of Arhan Canli (Quantavane) 2026
  (table/certificates/CPHF_12_1454_5_4.txt, affine expansion);
- E = CA(59425; 3, 1302, 25), the 2-plication of Shokri and Moura 2025, by its construction certificate
  (table/constructions/smolen-2026-11-sm-xplication/CA_59425_3_1302_25.cert.json).

Rows: [A|A] (49985), then [C|C + d mod 5] for d = 1, 2, 3, 4 (4 x 7445), then [E div 5 | E mod 5] (59425):
139190 rows, 2604 columns. The best known values were 140566 (k = 2412) and 140590 (k = 2604), both cited as
Martirosyan-Colbourn with older ingredients.

Checks done before submitting: the certificate is valid (54 s); a second, independent assembly in numpy gives the same
sha256 (276ca6806d6b9b94...); ca_verify on 8 windows of 24 columns (5 made of 12 columns and their twins, 3 random)
covers every 5-tuple. An exact check of all C(2604, 5) column sets is out of reach, which is why the certificate is the
proof: each step of the corollary is checked and each ingredient is a verified row of the table.

The array was found by the closure of the private ca-tools engine; no array of Torres-Jimenez is an ingredient.
