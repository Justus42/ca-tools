# Changes to the table's files

This file announces changes to the files that programs read (`table/ca_table.csv` and the files
named in `table/CONVENTIONS.md`, section 5): new columns and new values of a closed list, each at
least 30 days before its first use.

## 2026-11-24: new column ai_tools, first used no earlier than 2026-12-25

- `table/ca_table.csv` gains one column, `ai_tools`, added at the end of the file. The existing
  columns keep their names, order and meaning.
- Values: `yes`, or empty. `yes` means the person responsible for the submission says that AI
  tools were used to find or build the array. Empty means that nothing has been stated.
- Where it comes from: the line `AI tools used: yes` or `AI tools used: no` in the submission's
  `HOW.md` (`submissions/README.md`, "How it was built"). For a row entered before the column
  exists, it is filled only when the person responsible for that submission says so.
- The column says only whether AI tools were used. Which tools, and any run records, are not
  recorded in the table.
