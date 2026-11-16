import csv
import math
import os
import sys

REQUIRED_COLUMNS = ("assignment", "group", "score", "weight")
EXPECTED_WEIGHTS = {"Formative": 60, "Summative": 40}
GROUP_NAMES = {"formative": "Formative", "fa": "Formative",
               "summative": "Summative", "sa": "Summative"}
PASS_MARK = 50


def stop(message):
    """Print an error message and exit."""
    print(f"Error: {message}")
    sys.exit(1)


def show(number):
    """Format a number without trailing zeros."""
    return f"{round(number, 4):g}"


def line(label, value):
    """Print one labelled line of the summary."""
    print(f"{label:<26}: {value}")


def to_number(text, field):
    """Convert text to a float or raise a clear ValueError."""
    try:
        number = float(text)
    except ValueError:
        number = None
    if number is None or not math.isfinite(number):
        raise ValueError(f"{field} '{text}' is not a number")
    return number


def is_blank(row):
    """Check whether a CSV row has no values."""
    return all(not (row.get(key) or "").strip() for key in REQUIRED_COLUMNS)


def parse_row(row):
    """Turn one CSV row into an assignment record."""
    values = {key: (row.get(key) or "").strip() for key in REQUIRED_COLUMNS}
    missing = [key for key in REQUIRED_COLUMNS if not values[key]]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")

    group = GROUP_NAMES.get(values["group"].lower())
    if group is None:
        raise ValueError(
            f"group '{values['group']}' must be Formative or Summative")

    return {
        "assignment": values["assignment"],
        "group": group,
        "score": to_number(values["score"], "score"),
        "weight": to_number(values["weight"], "weight"),
    }


def ask_for_filename():
    """Ask the user which CSV file to open."""
    try:
        filename = input(
            "Enter the name of the CSV file to process (e.g., grades.csv): ")
    except (EOFError, KeyboardInterrupt):
        print()
        stop("No filename was entered.")

    filename = filename.strip()
    if not filename:
        stop("No filename was entered.")
    if not os.path.exists(filename):
        stop(f"The file '{filename}' was not found.")
    if not os.path.isfile(filename):
        stop(f"'{filename}' is a folder, not a CSV file.")
    return filename


def read_assignments(filename):
    """Read the CSV file and collect valid rows and row errors."""
    assignments = []
    problems = []
    blank_rows = 0

    with open(filename, mode="r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            stop(f"The file '{filename}' is empty.")

        reader.fieldnames = [name.strip().lower()
                             for name in reader.fieldnames]
        missing = [name for name in REQUIRED_COLUMNS
                   if name not in reader.fieldnames]
        if missing:
            stop(f"The file '{filename}' is missing the column(s): "
                 f"{', '.join(missing)}.")

        for row in reader:
            if is_blank(row):
                blank_rows += 1
                continue
            try:
                assignments.append(parse_row(row))
            except ValueError as error:
                problems.append(f"Line {reader.line_num}: {error}")

    return assignments, problems, blank_rows


def load_csv_data():
    """Load the grades CSV into a list of dictionaries."""
    filename = ask_for_filename()

    try:
        assignments, problems, blank_rows = read_assignments(filename)
    except UnicodeDecodeError:
        stop(f"'{filename}' is not a text CSV file.")
    except (OSError, csv.Error) as error:
        stop(f"Could not read '{filename}': {error}")

    if blank_rows:
        print(f"Note: skipped {blank_rows} row(s) with no values.")
    if problems:
        print(f"Error: {len(problems)} row(s) in '{filename}' are invalid:")
        for problem in problems:
            print(f"  {problem}")
        sys.exit(1)
    if not assignments:
        stop(f"The file '{filename}' has no assignment rows.")
    return assignments


def points(item):
    """Return the weighted points an assignment adds to the total."""
    return item["score"] * item["weight"] / 100


def group_totals(data):
    """Sum the weighted points and the weight of each group."""
    totals = {group: {"points": 0.0, "weight": 0.0}
              for group in EXPECTED_WEIGHTS}
    for item in data:
        totals[item["group"]]["points"] += points(item)
        totals[item["group"]]["weight"] += item["weight"]
    return totals


def check_scores(data):
    """List every score outside the 0-100 range."""
    return [f"{item['assignment']}: score {show(item['score'])} "
            f"is not between 0 and 100."
            for item in data if not 0 <= item["score"] <= 100]


def check_weights(data):
    """List every problem with the assignment and group weights."""
    errors = [f"{item['assignment']}: weight {show(item['weight'])} "
              f"must be greater than 0."
              for item in data if item["weight"] <= 0]

    totals = group_totals(data)
    for group, expected in EXPECTED_WEIGHTS.items():
        actual = round(totals[group]["weight"], 2)
        if actual != expected:
            errors.append(f"{group} weights add up to {show(actual)}, "
                          f"they must add up to {expected}.")

    total = round(sum(item["weight"] for item in data), 2)
    if total != 100:
        errors.append(f"All weights add up to {show(total)}, "
                      f"they must add up to 100.")
    return errors


def resubmission_options(data):
    """Return failed formatives and the highest-weight ones among them."""
    failed = [item for item in data
              if item["group"] == "Formative" and item["score"] < PASS_MARK]
    if not failed:
        return failed, []
    top_weight = max(item["weight"] for item in failed)
    return failed, [item for item in failed if item["weight"] == top_weight]


def print_table(data):
    """Print the assignments in the same layout as the ALU transcript."""
    width = max([len("Assignment")] + [len(item["assignment"])
                                       for item in data])
    print(f"\n{'Assignment':<{width}}  Category   Grade (%)  Weight"
          f"  Final weight")
    for item in data:
        print(f"{item['assignment']:<{width}}  {item['group']:<9}  "
              f"{show(item['score']):>9}  {show(item['weight']):>6}  "
              f"{show(points(item)):>12}")


def evaluate_grades(data):
    """Validate the grades and print the transcript and final decision."""
    print("\n--- Processing Grades ---")

    errors = check_scores(data) + check_weights(data)
    if errors:
        print("The grades cannot be evaluated until these are fixed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    print(f"Scores : all {len(data)} scores are between 0 and 100.")
    print("Weights: Formative 60 + Summative 40 = 100.")
    print_table(data)

    totals = group_totals(data)
    averages = {group: round(total["points"] / total["weight"] * 100, 2)
                for group, total in totals.items()}
    total_grade = sum(total["points"] for total in totals.values())
    gpa = total_grade / 100 * 5.0

    print()
    for group, total in totals.items():
        line(f"{group}s ({show(total['weight'])})",
             f"{show(total['points'])} ({show(averages[group])}%)")
    line("Total grade", f"{show(total_grade)} / 100")
    line("GPA", f"{show(gpa)} / 5")

    below = [group for group, average in averages.items()
             if average < PASS_MARK]
    print()
    if below:
        line("Status", f"FAILED ({' and '.join(below)} below {PASS_MARK}%)")
    else:
        line("Status", "PASSED")

    failed, eligible = resubmission_options(data)
    line("Failed formatives", ", ".join(
        f"{item['assignment']} ({show(item['score'])}%, "
        f"weight {show(item['weight'])})" for item in failed) or "None")
    line("Available for resubmission", ", ".join(
        item["assignment"] for item in eligible) or "None")


if __name__ == "__main__":
    course_data = load_csv_data()
    evaluate_grades(course_data)
