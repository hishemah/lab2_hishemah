# Lab 2: ALU Transcript Generator

A Python program that reads a student's course grades from a CSV file, checks that the data is valid, and prints the final grade, GPA, pass/fail decision and resubmission options. A Bash script archives the grades file and keeps a log of every archive.

## Files

| File | Purpose |
| --- | --- |
| `grade-evaluator.py` | Reads the CSV, validates it and prints the transcript |
| `grades.csv` | Sample grades used as input |
| `organizer.sh` | Archives `grades.csv` with a timestamp and logs the action |
| `Readme.md` | This file |

## Requirements

- Python 3.6 or newer (standard library only)
- Bash

## Running the grade evaluator

```bash
python3 grade-evaluator.py
```

When asked, type the CSV file name, for example `grades.csv`.

The CSV must have these columns: `assignment`, `group`, `score`, `weight`.

```
assignment,group,score,weight
Quiz,Formative,85,20
Midterm Project - Simple Calculator,Summative,70,20
```

The group can be written as `Formative` or `FA`, and `Summative` or `SA`, in any letter case.

## How the grade is calculated

- Each assignment adds `(score x weight) / 100` points (the "Final weight" column).
- Formatives (60) and Summatives (40) are the points earned in each category.
- Total grade is the sum of both categories, out of 100.
- GPA = (Total grade / 100) x 5.0
- The student **PASSED** only when the score is 50% or more in both categories (at least 30 of 60 Formative points and 20 of 40 Summative points). Otherwise the student **FAILED**.
- A formative assignment with a score below 50 has failed. Of the failed formative assignments, the one with the highest weight is available for resubmission. If several share that highest weight, all of them are listed. If none failed, it shows `None`.

The results were checked against all seven cases in the provided ALU transcript sheet (Transcript, v1 to v6). The category totals, GPA, status and resubmission match in every case.

## Validation

The program stops with a clear `Error:` message (exit code 1) when:

- no file name is entered, the file does not exist, or the name is a folder
- the file is empty, is not a text file, or has no assignment rows
- a required column is missing
- a row has a missing value, a score or weight that is not a number, or a group other than Formative or Summative (every bad row is listed with its line number)
- a score is outside 0 to 100
- a weight is 0 or negative
- the weights do not add up to 100, or Formative is not 60, or Summative is not 40

Rows where every value is empty are skipped and reported.

## Sample output with the provided grades.csv

```
--- Processing Grades ---
Scores : all 5 scores are between 0 and 100.
Weights: Formative 60 + Summative 40 = 100.

Assignment                           Category   Grade (%)  Weight  Final weight
Quiz                                 Formative         85      20            17
Group Exercise                       Formative         40      20             8
Functions and Debugging Lab          Formative         45      20             9
Midterm Project - Simple Calculator  Summative         70      20            14
Final Project - Text-Based Game      Summative         60      20            12

Formatives (60)           : 34 (56.67%)
Summatives (40)           : 26 (65%)
Total grade               : 60 / 100
GPA                       : 3 / 5

Status                    : PASSED
Failed formatives         : Group Exercise (40%, weight 20), Functions and Debugging Lab (45%, weight 20)
Available for resubmission: Group Exercise, Functions and Debugging Lab
```

## Running the organizer

```bash
bash organizer.sh
```

Run it from the folder that contains `grades.csv`. The script:

1. Creates an `archive` folder if it does not exist.
2. Moves `grades.csv` to `archive/grades_<timestamp>.csv`, for example `archive/grades_20251105-170000.csv`.
3. Creates a new empty `grades.csv`.
4. Appends a line to `organizer.log` with the timestamp, the original file name and the archived file name.

Example `organizer.log` entry:

```
20251105-170000 | original: grades.csv | archived: archive/grades_20251105-170000.csv
```

Every run adds a new line to `organizer.log`, so the log keeps the full history. The script stops with an error if `grades.csv` is missing or if `archive` exists as a file. An empty `grades.csv` is still archived, with a warning. If two runs happen in the same second, the script waits one second so no archive is overwritten.

Note: running the organizer empties `grades.csv`. To use the sample data again, copy it back from the `archive` folder.
