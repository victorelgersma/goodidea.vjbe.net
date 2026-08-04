#!/usr/bin/env python3
"""
generate_dashboard.py

Parses a Qualtrics survey export CSV and generates dashboard JSON data.

Usage:
    generate_dashboard.py <input.csv> <output.json>

The generated JSON is consumed by the PHP dashboard frontend.
"""

import csv
import json
import sys
from collections import Counter
from datetime import datetime


# ---- Question labels ------------------------------------------------------

QUESTION_LABELS = {
    "Q1": "If the UU offered an optional physical student card, would you request it?",
    "Q2": "Why? (selected choice)",
    "Q2_8_TEXT": "Another reason:",
    "Q4": "If you could request a physical student card but would have to contribute towards the cost of printing it, would you?",
    "Q16": "How much would you be willing to pay?",
    "Q5": "Comments, suggestions, or questions regarding the digital-only student card policy (optional)",
    "Q9": "(optional) Name provided",
    "Q11": "(optional) E-mail provided",
}


Q16_ORDER = [
    "0 EUR",
    "Less than 5 EUR",
    "Between 5 and 10 EUR",
    "Between 10 and 15 EUR",
    "More than 15 EUR",
]


# Free text exclusions
SKIP_COMMENT_INDEXES = {
    "Q5": {1},
}


# ---------------------------------------------------------------------------


def load_rows(path):
    """
    Read Qualtrics export.
    Skips:
      - question text row
      - ImportId metadata row
    """

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        short_header = next(reader)
        next(reader)
        next(reader)

        return [
            dict(zip(short_header, row))
            for row in reader
        ]


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def filter_rows(rows):
    """
    Remove previews and incomplete responses.
    """

    non_preview = [
        r for r in rows
        if r.get("Status", "").strip() != "Survey Preview"
    ]

    kept = []
    incomplete = 0

    for r in non_preview:
        if to_float(r.get("Progress")) < 50:
            incomplete += 1
            continue

        kept.append(r)

    return kept, len(non_preview), incomplete


def tally_single(rows, field):
    result = Counter()

    for r in rows:
        value = (r.get(field) or "").strip()
        result[value if value else "(No answer)"] += 1

    return result


def tally_multiselect(rows, field):
    result = Counter()
    answered = 0

    for r in rows:
        value = (r.get(field) or "").strip()

        if not value:
            continue

        answered += 1

        for item in value.split(","):
            item = item.strip()
            if item:
                result[item] += 1

    return result, answered


def free_text_with_skip(rows, field):

    skip = SKIP_COMMENT_INDEXES.get(field, set())

    comments = []
    index = 1

    for r in rows:
        value = (r.get(field) or "").strip()

        if value:

            if index not in skip:
                comments.append(value)

            index += 1

    return comments


def ordered_items(counter, preferred_order=None):

    items = dict(counter)

    labels = []

    if preferred_order:
        for key in preferred_order:
            if key in items:
                labels.append(key)

    remaining = sorted(
        [
            key for key in items
            if key not in labels
        ],
        key=lambda k: items[k],
        reverse=True
    )

    labels.extend(remaining)

    counts = [
        items[label]
        for label in labels
    ]

    return labels, counts


def build_dashboard_data(rows):

    q1 = tally_single(rows, "Q1")
    q4 = tally_single(rows, "Q4")

    q2, q2_answered = tally_multiselect(rows, "Q2")

    q2_other = free_text_with_skip(
        rows,
        "Q2_8_TEXT"
    )

    q16 = tally_single(rows, "Q16")

    # Conditional question: ignore blanks
    q16.pop("(No answer)", None)

    q5_comments = free_text_with_skip(
        rows,
        "Q5"
    )

    name_count = sum(
        1
        for r in rows
        if (r.get("Q9") or "").strip()
    )

    email_count = sum(
        1
        for r in rows
        if (r.get("Q11") or "").strip()
    )


    q1_labels, q1_counts = ordered_items(
        q1,
        ["Yes", "Maybe", "No", "(No answer)"]
    )

    q4_labels, q4_counts = ordered_items(
        q4,
        ["Yes", "Maybe", "No", "(No answer)"]
    )

    q2_labels, q2_counts = ordered_items(q2)

    q16_labels, q16_counts = ordered_items(
        q16,
        Q16_ORDER
    )


    return {

        "questions": QUESTION_LABELS,

        "q1": {
            "labels": q1_labels,
            "counts": q1_counts,
        },

        "q2": {
            "labels": q2_labels,
            "counts": q2_counts,
            "answered": q2_answered,
        },

        "q2_other": q2_other,

        "q4": {
            "labels": q4_labels,
            "counts": q4_counts,
        },

        "q16": {
            "labels": q16_labels,
            "counts": q16_counts,
            "answered": sum(q16_counts),
        },

        "q5_comments": q5_comments,

        "contacts": {
            "names": name_count,
            "emails": email_count,
        },
    }


def main():

    if len(sys.argv) != 3:
        print(
            "Usage: generate_dashboard.py <input.csv> <output.json>",
            file=sys.stderr
        )
        sys.exit(1)


    input_csv = sys.argv[1]
    output_json = sys.argv[2]


    rows = load_rows(input_csv)

    kept, total_submissions, incomplete_excluded = filter_rows(rows)

    dashboard = build_dashboard_data(kept)


    dashboard["meta"] = {

        "generated_at":
            datetime.now().strftime("%Y-%m-%d %H:%M"),

        "total_submissions":
            total_submissions,

        "total_kept":
            len(kept),

        "incomplete_excluded":
            incomplete_excluded,
    }


    with open(
        output_json,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            dashboard,
            f,
            indent=2,
            ensure_ascii=False
        )


    print(
        f"Wrote dashboard JSON: {output_json}"
    )


if __name__ == "__main__":
    main()
