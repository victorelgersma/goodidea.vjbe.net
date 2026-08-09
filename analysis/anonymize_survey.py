#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


# Qualtrics metadata/direct-identifying fields to remove.
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
}

# Direct-identifying survey fields in this particular survey.
REMOVE_SURVEY_FIELDS = {
    "Q9",  # optional name
    "Q11",  # optional email address
}


def anonymize_csv(input_path: Path, output_path: Path) -> None:
    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.reader(infile)
        rows = list(reader)

    if not rows:
        raise ValueError("CSV is empty.")

    headers = rows[0]

    # Find columns used for filtering responses.
    try:
        distribution_index = headers.index("DistributionChannel")
    except ValueError:
        distribution_index = None

    try:
        progress_index = headers.index("Progress")
    except ValueError:
        raise ValueError("Could not find the 'Progress' column.")

    # Determine which columns to retain.
    keep_indices = []

    for i, header in enumerate(headers):
        # Explicitly removed fields.
        if header in REMOVE_FIELDS:
            continue

        # Direct-identifying survey questions.
        if header in REMOVE_SURVEY_FIELDS:
            continue

        # Defensive removal of any date/time columns.
        header_lower = header.lower()
        if "date" in header_lower or "time" in header_lower:
            continue

        keep_indices.append(i)

    # Process rows.
    output_rows = []

    for row_number, row in enumerate(rows):

        # Qualtrics has three non-response/header rows:
        #   0 = column names
        #   1 = human-readable question labels
        #   2 = ImportId metadata
        if row_number < 3:
            output_rows.append(row)
            continue

        # Skip malformed/empty rows.
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
        progress_value = row[progress_index].strip()

        try:
            progress = float(progress_value)
        except ValueError:
            # If Progress isn't a valid number, don't include the response.
            continue

        if progress < 50:
            continue

        # Keep the response.
        output_rows.append(row)

    # Write anonymized CSV.
    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)

        for row in output_rows:
            writer.writerow([
                row[i] if i < len(row) else ""
                for i in keep_indices
            ])

    print(f"Anonymized CSV written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Anonymize and filter a Qualtrics CSV export."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input Qualtrics CSV file"
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output CSV file (default: <input>_anonymized.csv)"
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