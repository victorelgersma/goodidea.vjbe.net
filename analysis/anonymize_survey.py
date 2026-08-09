#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


# Fields that should not appear in the public dataset.
REMOVE_FIELDS = {
    "StartDate",
    "EndDate",
    "RecordedDate",
    "IPAddress",
    "ResponseId",
    "RecipientLastName",
    "RecipientFirstName",
    "RecipientEmail",
    "ExternalReference",
    "LocationLatitude",
    "LocationLongitude",
    "DistributionChannel",
    "Status",
    "Progress",
    "Duration (in seconds)",
    "Q9",   # optional name
    "Q11",  # optional email address
}


def anonymize_csv(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    if len(rows) < 4:
        raise ValueError("CSV does not contain any survey responses.")

    headers = rows[0]

    try:
        distribution_index = headers.index("DistributionChannel")
    except ValueError:
        distribution_index = None

    try:
        progress_index = headers.index("Progress")
    except ValueError:
        raise ValueError("Could not find the 'Progress' column.")

    # Determine which columns to keep.
    keep_indices = []

    for i, header in enumerate(headers):
        if header in REMOVE_FIELDS:
            continue

        # Remove any date/time fields as a precaution.
        header_lower = header.lower()
        if "date" in header_lower or "time" in header_lower:
            continue

        keep_indices.append(i)

    # Qualtrics rows:
    #   0 = machine-readable column names
    #   1 = human-readable question labels
    #   2 = ImportId metadata
    #
    # Use the human-readable question labels as the public headers.
    question_headers = rows[1]

    output_headers = [
        question_headers[i] if i < len(question_headers) else ""
        for i in keep_indices
    ]

    output_rows = [output_headers]

    # Process survey responses.
    for row in rows[3:]:
        if len(row) <= progress_index:
            continue

        # Remove survey preview responses.
        if (
            distribution_index is not None
            and distribution_index < len(row)
            and row[distribution_index].strip().lower() == "preview"
        ):
            continue

        # Remove responses with Progress < 50.
        try:
            progress = float(row[progress_index].strip())
        except ValueError:
            continue

        if progress < 50:
            continue

        # Preserve the original survey answer strings.
        output_rows.append([
            row[i] if i < len(row) else ""
            for i in keep_indices
        ])

    # Write the anonymized CSV.
    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)
        writer.writerows(output_rows)

    print(f"Anonymized CSV written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Anonymize and filter a Qualtrics CSV export."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input Qualtrics CSV file",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV file (default: <input>_anonymized.csv)",
    )

    args = parser.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input file does not exist: {args.input}")

    output = args.output or args.input.with_name(
        f"{args.input.stem}_anonymized.csv"
    )

    anonymize_csv(args.input, output)


if __name__ == "__main__":
    main()
