# Lab 2: ALU Transcript Generator

A Python application that calculates a student's final academic standing from a CSV file of grades, plus a Bash script that archives the grades file.

**Author:** shimwa-prosper

## Files

| File | Purpose |
| :--- | :--- |
| `grade-evaluator.py` | Validates grades and weights, calculates GPA, decides PASSED/FAILED, and lists resubmission options |
| `grades.csv` | Input data (columns: `assignment,group,score,weight`) |
| `organizer.sh` | Archives `grades.csv` with a timestamp, resets it, and logs the action |

## How to run the Python program

```
python3 grade-evaluator.py
```

When asked, type the file name, for example `grades.csv`. No external libraries are used (only `csv`, `sys` and `os`).

## How it works

1. **Grade validation:** every score must be between 0 and 100.
2. **Weight validation:** all weights add up to exactly 100, Formative = 60, Summative = 40.
3. **GPA:** `GPA = (Total Grade / 100) * 5.0`, where each assignment adds `score * weight / 100` to the total.
4. **Pass/Fail:** the student passes only with at least 50% in BOTH Formative and Summative (each measured as a percentage of its own category).
5. **Resubmission:** among failed formative assignments (score below 50), the ones with the highest weight are eligible. If several share that highest weight, all of them are shown.

## Example output (with the provided grades.csv)

```
Formative: 34.00 / 60  (56.7%)
Summative: 26.00 / 40  (65.0%)
Total Grade: 60.00 / 100
GPA: 3.00 / 5.0

Final Status: PASSED

Eligible for resubmission (failed formative with the highest weight):
  - Group Exercise (score: 40, weight: 20)
  - Functions and Debugging Lab (score: 45, weight: 20)
```

## Error handling

The program prints a clear message (and exits with code 1) for:

- no file name entered, file not found, path is not a file, or file is empty
- missing columns in the header, or a header with no rows
- empty rows (ignored, with a note)
- score or weight that is not a number (the line number is shown)
- group that is not `Formative` or `Summative`
- scores outside 0-100, negative weights, or weights that do not add up to 100 / 60 / 40

## Shell script: organizer.sh

```
bash organizer.sh
```

What it does:

1. Creates the `archive` directory if it does not exist.
2. Moves `grades.csv` into `archive/` renamed with a timestamp, for example `grades_20251105-170000.csv`.
3. Creates a new, empty `grades.csv` ready for the next batch.
4. Appends a line (timestamp, original name, archived name) to `organizer.log`. The log grows with every run.

If `grades.csv` does not exist, it prints an error and exits with code 1.

**Note:** running `organizer.sh` empties `grades.csv`, so copy your grades back before running the Python program again.
