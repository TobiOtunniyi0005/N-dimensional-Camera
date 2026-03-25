import sys
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# 1. Read input filename from command line
# --------------------------------------------------
if len(sys.argv) < 2:
    raise RuntimeError(
        "Usage: python Grid.py <input_file.csv | input_file.xlsx>"
    )

input_filename = sys.argv[1]

# --------------------------------------------------
# 2. Resolve path relative to THIS script
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
input_path = BASE_DIR / input_filename

print(f"Looking for input file at: {input_path}")

if not input_path.exists():
    raise FileNotFoundError(f"Input file not found: {input_path}")

output_path = input_path.with_name(
    input_path.stem + "_grid" + input_path.suffix
)

# --------------------------------------------------
# 3. Load input file
# --------------------------------------------------
suffix = input_path.suffix.lower()

if suffix == ".csv":
    df = pd.read_csv(input_path)
elif suffix in [".xls", ".xlsx"]:
    df = pd.read_excel(input_path)
else:
    raise ValueError("Only CSV or Excel files are supported")

# --------------------------------------------------
# 4. Validate columns
# --------------------------------------------------
required_cols = {"Field", "Lower", "Upper"}
if not required_cols.issubset(df.columns):
    raise ValueError(
        f"Input must contain columns: {required_cols}"
    )

fields = df["Field"].tolist()

# --------------------------------------------------
# 5. Compute stretched bounds FIRST
# --------------------------------------------------
ranges = {}

for _, row in df.iterrows():
    field = row["Field"]

    L = int(2 * row["Lower"])
    H = int(2 * row["Upper"])

    M = (L + H) / 2

    new_L = int(L + 2 * (L - M))
    new_H = int(H + 2 * (H - M))

    ranges[field] = (new_L, new_H)

# --------------------------------------------------
# 6. Generate records
# --------------------------------------------------
records = []

for field, (low, high) in ranges.items():
    for value in range(low, high + 1):
        record = {f: 0 for f in fields}
        record[field] = value
        records.append(record)

result_df = pd.DataFrame(records)

# --------------------------------------------------
# 7. Save output
# --------------------------------------------------
if suffix == ".csv":
    result_df.to_csv(output_path, index=False)
else:
    result_df.to_excel(output_path, index=False)

print("✔ Done")
print(f"Output written to: {output_path.name}")
print(f"Rows generated: {len(result_df)}")
