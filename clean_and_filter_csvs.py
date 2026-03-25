import csv
import os
from datetime import datetime

INPUT_DIR = "input_csvs"
OUTPUT_DIR = "clean_csvs"
BROKEN_FILE = "broken_records.csv"

MISSING_VALUES = {"", "NA", "NaN", "null", "NULL"}

os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_float(x):
    try:
        float(x)
        return True
    except:
        return False

def date_to_unix(date_str):
    try:
        dt = datetime.fromisoformat(date_str)
        return str(dt.timestamp())
    except:
        return None

broken_out = open(BROKEN_FILE, "w", newline="", encoding="utf-8")
broken_writer = csv.writer(broken_out)

broken_header_written = False

for file in os.listdir(INPUT_DIR):
    if not file.endswith(".csv"):
        continue

    input_path = os.path.join(INPUT_DIR, file)
    output_path = os.path.join(OUTPUT_DIR, file)

    print(f"Processing {file}")

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        first_row = next(reader)

        # Detect header (non-numeric fields)
        has_header = any(not is_float(x) for x in first_row)
        header = first_row if has_header else None

        rows = []
        broken_rows = []

        if not has_header:
            rows.append(first_row)

        for row in reader:
            if any(cell.strip() in MISSING_VALUES for cell in row):
                broken_rows.append(row)
            else:
                rows.append(row)

        if not rows:
            continue

        # Identify date column
        date_col = None
        if header:
            for i, name in enumerate(header):
                if name.lower() == "date":
                    date_col = i

        # Convert date to numeric
        cleaned_rows = []
        for row in rows:
            if date_col is not None:
                unix = date_to_unix(row[date_col])
                if unix is None:
                    broken_rows.append(row)
                    continue
                row[date_col] = unix
            cleaned_rows.append(row)

        # Remove non-numeric columns entirely
        numeric_cols = []
        for col in range(len(cleaned_rows[0])):
            if any(is_float(r[col]) for r in cleaned_rows):
                numeric_cols.append(col)

        final_rows = [[row[c] for c in numeric_cols] for row in cleaned_rows]

        # Write cleaned file (NO header)
        with open(output_path, "w", newline="", encoding="utf-8") as out:
            writer = csv.writer(out)
            writer.writerows(final_rows)

        # Write broken rows
        if broken_rows:
            if not broken_header_written:
                broken_writer.writerow(header if header else [f"col{i}" for i in range(len(first_row))])
                broken_header_written = True
            broken_writer.writerows(broken_rows)

broken_out.close()
print("✔ Done")
