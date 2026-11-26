Construction: Paired-column ternary backbone followed by weighted local repair. Keep the first 26 entries of the 27 offset-zero and the 27 offset-one rows of the starting array. Use 19 further rows in which columns 14–26 equal columns 1–13 plus two modulo three. Search their 13 base entries and the two extension entries in all 73 rows (393 free entries).

Built from: Alexander LaVerdi’s 74-row array, ca-tools entry t3-v3-k28-3, built from Christopher Smolen’s starting array. The exact input is [table/arrays/CA_74_3_28_3.txt at c5f447da](https://github.com/chrispbsmolen/ca-tools/blob/c5f447da7f3efcc1b39cdea6340463ec7e90e006/table/arrays/CA_74_3_28_3.txt). The starting array is credited under the table’s CC BY 4.0 data terms. This submission modifies the bottom block and the extension assignments.

Program: Download and extract the [reproduction package](https://alexanderlehmann.dev/assets/covering-array-73-materials.zip). From the extracted root, run the following commands with GNU C++17 and Python 3. The last solver argument is a wall-time limit in seconds and can be increased on slower machines.

```sh
g++ -O3 -std=c++17 algebra/paired.cpp -o paired
./paired solver/ref/74.txt CA_73_3_28_3.txt 17521 300
python3 evidence/verify.py CA_73_3_28_3.txt --rows 73
sha256sum CA_73_3_28_3.txt
```

Expected SHA-256: `fd789cd09a08f645eaf3817311ba101ba9c619ccab47ad9ae926c636a49ae165`.

AI tools used: yes
