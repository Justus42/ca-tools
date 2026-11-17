# smolen-2026-11-engine-deposit-2: 30 covering arrays from the ca-tools engine, kept in a Zenodo deposit

The arrays are in Zenodo record 24295860, doi:10.5281/zenodo.24295860, one zip per array (LZMA), with MANIFEST.csv giving the
canonical SHA-256, recipe and references of every file. They are kept outside the repository because they are
larger than 1 MB. All are at cited best known sizes that had no array.

Construction: one per array, named in the construction column and recipe of external.csv: Augmentation of an orthogonal array with quilting arrays (Colbourn 2014, Theorem 2.2); Construction function of the R package CAs 0.24.4; Fusing symbols (Colbourn, Keri, Rivas Soriano and Schlage-Puchta 2010, Lemma 3.1); Product of Colbourn and Torres-Jimenez 2013 (Cor 4.3): rows differing in every column removed; Raaphorst-Moura-Stevens construction (2014).

Built from: arrays of this table, named by file in each recipe, and the constructions named above.

Program: the engine's builder rebuilds each array from its recipe with the laws used in the engine submissions
smolen-2026-11-cae-run-1 onward. Each array was checked exactly with ca_verify on all column t-sets before the
deposit; the table checks each again on download.
