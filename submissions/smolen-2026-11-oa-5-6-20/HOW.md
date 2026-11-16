# smolen-2026-11-oa-5-6-20: CA(3200000; 5, 6, 20), kept in a Zenodo deposit

The array is CA_3200000_5_6_20.txt in arrays_t5.zip of Zenodo record 24271941, doi:10.5281/zenodo.24271941
("Covering arrays built for ca-tools (C. Smolen), batch 2026-11"). It was held back from
smolen-2026-11-engine-deposit-1 because ca_verify needs more memory for it than the checking machine had; since the
checker now counts exactly when ca_verify is stopped for memory, it is entered on its own.

It is built by the composition of alphabets of Colbourn, Keri, Rivas Soriano and Schlage-Puchta (2010), construction
(3): the even-weight binary orthogonal array CA(32; 5, 6, 2) composed with the table array CA(100000; 5, 6, 10). The
result has index one: every 5 columns hold each of the 20^5 tuples exactly once. Its size equals the cited best known
value, and it is the first array the table can give for it.
