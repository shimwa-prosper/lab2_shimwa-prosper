import csv
import sys
import os
REQUIRED_COLUMNS = ['assignment', 'group', 'score', 'weight']
VALID_GROUPS = ['Formative', 'Summative']
PASS_MARK = 50.0  # percent, required in BOTH categories


def load_csv_data():
    """
    Prompts the user for a filename, checks that it can be read, validates
    its structure, and extracts all fields into a list of dictionaries.
    Every problem produces a clear message instead of a crash.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if filename == "":
        print("Error: No filename entered. Please type a name such as grades.csv.")
        sys.exit(1)

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is not a file.")
        sys.exit(1)

    if os.path.getsize(filename) == 0:
        print(f"Error: The file '{filename}' is empty. Add grades first "
              f"(header: {','.join(REQUIRED_COLUMNS)}).")
        sys.exit(1)

    assignments = []
    row_errors = []
    skipped_empty = 0

    try:
        with open(filename, mode='r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)

            # Clean up header names (spaces / different capitals)
            if reader.fieldnames is None:
                print(f"Error: '{filename}' has no header row.")
                sys.exit(1)
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames if name is not None]

            missing = [col for col in REQUIRED_COLUMNS if col not in reader.fieldnames]
            if missing:
                print(f"Error: Missing column(s) in '{filename}': {', '.join(missing)}.")
                print(f"Expected header: {','.join(REQUIRED_COLUMNS)}")
                sys.exit(1)

            for row in reader:
                line = reader.line_num  # real line number in the file

                # Skip rows where every cell is blank (e.g. ",,,")
                values = [str(v).strip() for v in row.values() if v is not None]
                if len(values) == 0 or all(v == "" for v in values):
                    skipped_empty += 1
                    continue

                name = (row.get('assignment') or '').strip()
                group = (row.get('group') or '').strip().capitalize()
                score_text = (row.get('score') or '').strip()
                weight_text = (row.get('weight') or '').strip()

                if name == "":
                    row_errors.append(f"Line {line}: assignment name is missing.")
                    continue
                if group not in VALID_GROUPS:
                    row_errors.append(f"Line {line} ({name}): group must be 'Formative' or "
                                      f"'Summative', got '{row.get('group')}'.")
                    continue

                # Convert numeric fields to floats for calculations
                try:
                    score = float(score_text)
                except ValueError:
                    row_errors.append(f"Line {line} ({name}): score '{score_text}' is not a number (e.g. 85).")
                    continue
                try:
                    weight = float(weight_text)
                except ValueError:
                    row_errors.append(f"Line {line} ({name}): weight '{weight_text}' is not a number (e.g. 20).")
                    continue

                assignments.append({
                    'assignment': name,
                    'group': group,
                    'score': score,
                    'weight': weight
                })
    except UnicodeDecodeError:
        print(f"Error: '{filename}' could not be read as text. Save it as a UTF-8 CSV file.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: No permission to read '{filename}'.")
        sys.exit(1)
    except csv.Error as e:
        print(f"Error: '{filename}' is not a valid CSV file: {e}")
        sys.exit(1)
    except OSError as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    if skipped_empty > 0:
        print(f"Note: {skipped_empty} empty row(s) were ignored.")

    if row_errors:
        print("Error: The file contains invalid rows:")
        for message in row_errors:
            print(f"  - {message}")
        sys.exit(1)

    if len(assignments) == 0:
        print(f"Error: '{filename}' has a header but no grade rows.")
        sys.exit(1)

    return assignments


def validate_scores(data):
    """a) Every score must be a percentage between 0 and 100."""
    errors = []
    for item in data:
        # 'not (0 <= x <= 100)' also rejects nan, which a plain 'x < 0 or x > 100' would miss
        if not (0 <= item['score'] <= 100):
            errors.append(f"'{item['assignment']}' has score {item['score']}, "
                          f"but scores must be between 0 and 100.")
    return errors


def validate_weights(data):
    """b) Total = 100, Formative = 60, Summative = 40."""
    errors = []
    total = 0.0
    formative = 0.0
    summative = 0.0

    for item in data:
        if not (item['weight'] >= 0):
            errors.append(f"'{item['assignment']}' has weight {item['weight']}, "
                          f"but weights cannot be negative.")
        total += item['weight']
        if item['group'] == 'Formative':
            formative += item['weight']
        else:
            summative += item['weight']

    # Small tolerance only to absorb floating-point noise (e.g. 33.3 + 33.3 + 33.4)
    if abs(total - 100) > 1e-9:
        errors.append(f"Total weight is {total:g}, but it must be exactly 100.")
    if abs(formative - 60) > 1e-9:
        errors.append(f"Formative weights add up to {formative:g}, but they must be exactly 60.")
    if abs(summative - 40) > 1e-9:
        errors.append(f"Summative weights add up to {summative:g}, but they must be exactly 40.")
    return errors


def evaluate_grades(data):
    """
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    # a) Score validation
    # b) Weight validation
    errors = validate_scores(data) + validate_weights(data)
    if errors:
        print("Validation failed. Please fix the following and run again:")
        for message in errors:
            print(f"  - {message}")
        sys.exit(1)

    # c) Final grade and GPA
    # Each assignment contributes score * weight / 100 points toward the 100-point total.
    formative_points = 0.0   # out of 60
    summative_points = 0.0   # out of 40
    for item in data:
        points = item['score'] * item['weight'] / 100
        if item['group'] == 'Formative':
            formative_points += points
        else:
            summative_points += points

    total_grade = formative_points + summative_points
    gpa = (total_grade / 100) * 5.0

    # Percentage inside each category (needed for the 50% rule)
    formative_pct = formative_points / 60 * 100
    summative_pct = summative_points / 40 * 100

    # d) Pass / Fail: at least 50% in BOTH categories
    passed = formative_pct >= PASS_MARK and summative_pct >= PASS_MARK
    status = "PASSED" if passed else "FAILED"

    # e) Failed formative assignments (< 50%) and the highest weight among them
    failed_formative = [item for item in data
                        if item['group'] == 'Formative' and item['score'] < PASS_MARK]
    resubmit = []
    if failed_formative:
        highest_weight = failed_formative[0]['weight']
        for item in failed_formative:
            if item['weight'] > highest_weight:
                highest_weight = item['weight']
        # keep ALL failed formatives that share the highest weight (ties)
        for item in failed_formative:
            if item['weight'] == highest_weight:
                resubmit.append(item)

    # f) Output
    print(f"\n{'Assignment':<40}{'Group':<12}{'Score':>7}{'Weight':>8}")
    print("-" * 67)
    for item in data:
        print(f"{item['assignment']:<40}{item['group']:<12}{item['score']:>7.1f}{item['weight']:>8.1f}")
    print("-" * 67)

    print(f"\nFormative: {formative_points:.2f} / 60  ({formative_pct:.1f}%)")
    print(f"Summative: {summative_points:.2f} / 40  ({summative_pct:.1f}%)")
    print(f"Total Grade: {total_grade:.2f} / 100")
    print(f"GPA: {gpa:.2f} / 5.0")
    print(f"\nFinal Status: {status}")

    if not passed:
        if formative_pct < PASS_MARK:
            print("  - Formative category is below 50%.")
        if summative_pct < PASS_MARK:
            print("  - Summative category is below 50%.")

    if resubmit:
        print("\nEligible for resubmission (failed formative with the highest weight):")
        for item in resubmit:
            print(f"  - {item['assignment']} (score: {item['score']:g}, weight: {item['weight']:g})")
    else:
        print("\nNo failed formative assignments: no resubmission needed.")


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
