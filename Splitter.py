import csv
import os
import sys

ROWS_PER_FILE = 10000

def split_csv(input_file):
    base, ext = os.path.splitext(input_file)

    with open(input_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

        file_index = 1
        row_count = 0
        out_file = None
        writer = None

        for row in reader:
            if row_count % ROWS_PER_FILE == 0:
                if out_file:
                    out_file.close()

                output_name = f"{base}_part{file_index}{ext}"
                out_file = open(output_name, "w", newline='', encoding='utf-8')
                writer = csv.writer(out_file)
                writer.writerow(header)

                print(f"Creating {output_name}")
                file_index += 1

            writer.writerow(row)
            row_count += 1

        if out_file:
            out_file.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python split_csv_chunks.py input.csv")
        sys.exit(1)

    split_csv(sys.argv[1])
