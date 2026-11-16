# smolen-2026-11-engine-deposit-1: 42 covering arrays from the ca-tools engine, kept in a Zenodo deposit

The arrays are in Zenodo record 24271941, doi:10.5281/zenodo.24271941 ("Covering arrays built for ca-tools
(C. Smolen), batch 2026-11"), one zip per strength (arrays_t2.zip to arrays_t6.zip), with MANIFEST.csv giving the
canonical SHA-256, recipe and references of every file. They are kept outside the repository because most of them are
larger than 1 MB. Two are below the table's best known values at entry: CA(186496; 6, 13, 6) and CA(862; 2, 5832, 17);
the others are at cited best known sizes that had no array.

This submission enters 42 of the 43 arrays of the record. The 43rd, CA(3200000; 5, 6, 20), is an orthogonal array of
index one (each 5-tuple exactly once in every set of 5 columns). It is entered separately, because ca_verify cannot
hold the 20^5 symbol sets of its 3.2 million rows in memory.

Construction: one per array, named in the construction column and recipe of external.csv: fusing symbols and
composition of alphabets (Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010), the products of Colbourn and
Torres-Jimenez 2013 (Cor 4.3, rows differing in every column removed, and the profile product), construction functions
of the R package CAs 0.24.4 by Ulrike Groemping, the Raaphorst-Moura-Stevens construction (2014) and Bush / Bose
orthogonal arrays. Where an array has more columns than needed, its first k columns are kept.

Built from: arrays of this table, named by file in each recipe, CAs 0.24.4 constructions, and Bush / Bose orthogonal
arrays built from finite fields.

Program: the engine's builder rebuilds each array from its recipe (programs/build.py with laws.py and recipes.json in
the earlier engine submissions, smolen-2026-11-cae-run-1 to run-7, use the same laws). Each array was checked exactly
with ca_verify on all column t-sets before the deposit; the table checks each again on download.
