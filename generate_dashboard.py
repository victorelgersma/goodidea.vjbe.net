#!/usr/bin/env python3
"""
generate_dashboard.py

Parses a Qualtrics survey export (CSV), filters out preview responses silently,
filters responses that are less than 50% complete, tallies the answers to every
question, and renders a self-contained HTML dashboard (Chart.js via CDN).

Supports compile-time index skipping for free-text comment questions.

Usage:
    generate_dashboard.py <input.csv> <output.html>
"""

import csv
import json
import sys
from collections import Counter
from datetime import datetime
from html import escape

# ---- Question labels (short code -> full question text) -------------------
QUESTION_LABELS = {
    "Q1": "If the UU offered an optional physical student card, would you request it?",
    "Q2": "Why? (selected choice)",
    "Q2_8_TEXT": "Another reason:",
    "Q4": "If you could request a physical student card but would have to contribute "
          "towards the cost of printing it, would you?",
    "Q16": "How much would you be willing to pay?",
    "Q5": "Comments, suggestions, or questions regarding the digital-only student "
          "card policy (optional)",
    "Q9": "(optional) Name provided",
    "Q11": "(optional) E-mail provided",
}

# Preferred display order for the willingness-to-pay categories.
Q16_ORDER = [
    "0 EUR",
    "Less than 5 EUR",
    "Between 5 and 10 EUR",
    "Between 10 and 15 EUR",
    "More than 15 EUR",
]

# ---------------------------------------------------------------------------
# COMPILE-TIME COMMENT EXCLUSION LISTS
# Specify 1-based indices of comments to skip/hide for each free-text question.
# Example: "Q5": {12, 18} skips comment #12 and #18 from Q5.
# ---------------------------------------------------------------------------
SKIP_COMMENT_INDEXES = {
    "Q5": {1},
}


def load_rows(path):
    """Read the Qualtrics export, skipping the two extra header rows."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        short_header = next(reader)   # Q1, Q2, ... short codes
        next(reader)                  # full question text (unused)
        next(reader)                  # ImportId JSON metadata (unused)
        return [dict(zip(short_header, row)) for row in reader]


def to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def filter_rows(rows):
    """Drop Survey Preview rows silently and filter rows under 50% progress."""
    non_preview = [r for r in rows if r.get("Status", "").strip() != "Survey Preview"]
    
    kept, incomplete_excluded = [], 0
    for r in non_preview:
        if to_float(r.get("Progress")) < 50:
            incomplete_excluded += 1
            continue
        kept.append(r)

    return kept, len(non_preview), incomplete_excluded


def tally_single(rows, field):
    c = Counter()
    for r in rows:
        v = (r.get(field) or "").strip()
        c[v if v else "(No answer)"] += 1
    return c


def tally_multiselect(rows, field):
    """Split a comma-packed multi-select cell into individual choice tallies."""
    c = Counter()
    answered = 0
    for r in rows:
        v = (r.get(field) or "").strip()
        if not v:
            continue
        answered += 1
        for part in v.split(","):
            part = part.strip()
            if part:
                c[part] += 1
    return c, answered


def free_text_with_skip(rows, field):
    """
    Extracts non-empty free-text answers as string comments.
    Skips any entry whose 1-based index is listed in SKIP_COMMENT_INDEXES[field].
    """
    skip_set = SKIP_COMMENT_INDEXES.get(field, set())
    comments = []
    index = 1

    for r in rows:
        val = (r.get(field) or "").strip()
        if val:
            if index not in skip_set:
                comments.append(val)
            index += 1

    return comments


def ordered_items(counter, preferred_order=None):
    """Return (labels, counts) — preferred order first, then the rest by count desc."""
    items = dict(counter)
    labels = []
    if preferred_order:
        for key in preferred_order:
            if key in items:
                labels.append(key)
    remaining = sorted(
        (k for k in items if k not in labels), key=lambda k: items[k], reverse=True
    )
    labels.extend(remaining)
    counts = [items[l] for l in labels]
    return labels, counts


def build_dashboard_data(rows):
    q1 = tally_single(rows, "Q1")
    q4 = tally_single(rows, "Q4")
    q2, q2_answered = tally_multiselect(rows, "Q2")
    q2_other = free_text_with_skip(rows, "Q2_8_TEXT")
    q16_raw = tally_single(rows, "Q16")
    q16_raw.pop("(No answer)", None)  # only asked conditionally; skip the blanks
    q5_comments = free_text_with_skip(rows, "Q5")
    name_count = sum(1 for r in rows if (r.get("Q9") or "").strip())
    email_count = sum(1 for r in rows if (r.get("Q11") or "").strip())

    q1_labels, q1_counts = ordered_items(q1, ["Yes", "Maybe", "No", "(No answer)"])
    q4_labels, q4_counts = ordered_items(q4, ["Yes", "Maybe", "No", "(No answer)"])
    q2_labels, q2_counts = ordered_items(q2)
    q16_labels, q16_counts = ordered_items(q16_raw, Q16_ORDER)

    return {
        "q1": {"labels": q1_labels, "counts": q1_counts},
        "q4": {"labels": q4_labels, "counts": q4_counts},
        "q2": {"labels": q2_labels, "counts": q2_counts, "answered": q2_answered},
        "q2_other": q2_other,
        "q16": {"labels": q16_labels, "counts": q16_counts, "answered": sum(q16_counts)},
        "q5_comments": q5_comments,
        "name_count": name_count,
        "email_count": email_count,
    }


def render_html(data, meta, source_filename):
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    data_json = json.dumps(data)

    def comment_list_html(items, empty_msg):
        if not items:
            return f'<p class="empty-msg">{empty_msg}</p>'
        cards = []
        for text in items:
            cards.append(
                f'<div class="comment-card">'
                f'{escape(text)}'
                f'</div>'
            )
        return "\n".join(cards)

    other_reasons_html = comment_list_html(
        data["q2_other"], "No free-text reasons were given."
    )
    comments_html = comment_list_html(
        data["q5_comments"], "No comments were left."
    )

    total_submissions = meta["total_submissions"]
    total_kept = meta["total_kept"]
    incomplete_excluded = meta["incomplete_excluded"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Digital Student Card Survey — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="stylesheet" href="style.css">
</head>
<body>
<iframe src="logo.html"
        style="width:100%; border:none; display:block;"
        title="Logo">
</iframe> 
<div id="site-nav"></div>
<script src="nav.js"></script>

<div class="wrap">

  <header class="page-header">
    <h1>Survey Results </h1>
    <h2>Introducing an Optional Physical Student Card</h2>
  </header>

  <div class="summary">
    <span class="count">{total_kept}</span>
    <span class="label">responses</span>
</div>

  <div class="grid">

    <div class="card" data-qnum="Q1">
      <h2>{escape(QUESTION_LABELS["Q1"])}</h2>
      <p class="sub">n = {total_kept}</p>
      <div class="chart-box"><canvas id="chartQ1"></canvas></div>
    </div>
    <div class="card full" data-qnum="Q2">
      <h2>{escape(QUESTION_LABELS["Q2"])}</h2>
      <p class="sub">{data["q2"]["answered"]} respondents selected at least one reason &middot; multiple selections allowed</p>
      <div class="reason-list tall" id="q2Reasons"></div>
    </div>
    <div class="card" data-qnum="Q2_8_TEXT">
      <h2>{escape(QUESTION_LABELS["Q2_8_TEXT"])}</h2>
      <p class="sub">{len(data["q2_other"])} free-text responses</p>
      <div class="comment-list">
        {other_reasons_html}
      </div>
    </div>


    <div class="card" data-qnum="Q4">
      <h2>{escape(QUESTION_LABELS["Q4"])}</h2>
      <p class="sub">n = {total_kept}</p>
      <div class="chart-box"><canvas id="chartQ4"></canvas></div>
    </div>

    <div class="card" data-qnum="Q16">
      <h2>{escape(QUESTION_LABELS["Q16"])}</h2>
      <p class="sub">n = {data["q16"]["answered"]} (only asked of those willing to contribute)</p>
      <div class="chart-box"><canvas id="chartQ16"></canvas></div>
    </div>

    <div class="card full" data-qnum="Q5">
      <h2>{escape(QUESTION_LABELS["Q5"])}</h2>
      <p class="sub">{len(data["q5_comments"])} comments left</p>
      <div class="comment-list">
        {comments_html}
      </div>
    </div>

    <div class="card full" data-qnum="Q9,Q11">
      <h2>Optional contact info</h2>
      <p class="sub">Respondents could optionally leave their name/e-mail for follow-up. Shown as counts only.</p>
      <div class="contact-row">
        <span class="contact-pill">{data["name_count"]} left a name</span>
        <span class="contact-pill">{data["email_count"]} left an e-mail</span>
      </div>
    </div>

  </div>
  <div class="methodology">
    <h3>Methodology</h3>
    <p>
        This report summarizes <strong>{total_kept}</strong> survey responses.
        Responses with less than 50% completion were also excluded from the analysis
        ({incomplete_excluded} response{"s" if incomplete_excluded != 1 else ""}).
    </p>
    <p>Results generated at {generated_at}</p>
</div>
</div>

<script>
const DATA = {data_json};

function baseOptions(extra) {{
  return Object.assign({{
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }} }},
  }}, extra || {{}});
}}

function colorFor(label) {{
  const map = {{ "Yes": "#4f46e5", "Maybe": "#f59e0b", "No": "#ef4444" }};
  return map[label] || "#94a3b8";
}}

new Chart(document.getElementById('chartQ1'), {{
  type: 'doughnut',
  data: {{
    labels: DATA.q1.labels,
    datasets: [{{ data: DATA.q1.counts, backgroundColor: DATA.q1.labels.map(colorFor) }}]
  }},
  options: baseOptions({{ plugins: {{ legend: {{ display: true, position: 'bottom' }} }} }})
}});

new Chart(document.getElementById('chartQ4'), {{
  type: 'doughnut',
  data: {{
    labels: DATA.q4.labels,
    datasets: [{{ data: DATA.q4.counts, backgroundColor: DATA.q4.labels.map(colorFor) }}]
  }},
  options: baseOptions({{ plugins: {{ legend: {{ display: true, position: 'bottom' }} }} }})
}});



const q2Container = document.getElementById("q2Reasons");

const maxQ2 = Math.max(...DATA.q2.counts);

DATA.q2.labels.forEach((label, i) => {{
  const row = document.createElement("div");
  row.className = "reason-row";

  const percent = (DATA.q2.counts[i] / maxQ2) * 100;

  row.innerHTML = `
    <div class="reason-label">${{label}}</div>
    <div class="reason-bar-wrap">
      <div class="reason-bar" style="width:${{percent}}%"></div>
    </div>
    <div class="reason-count">${{DATA.q2.counts[i]}}</div>
  `;

  q2Container.appendChild(row);
}});


new Chart(document.getElementById('chartQ16'), {{
  type: 'bar',
  data: {{
    labels: DATA.q16.labels,
    datasets: [{{ data: DATA.q16.counts, backgroundColor: '#4f46e5', borderRadius: 4 }}]
  }},
  options: baseOptions({{
    scales: {{ y: {{ beginAtZero: true, ticks: {{ precision: 0 }} }} }}
  }})
}});
</script>
</body>
</html>
"""
    return html


def main():
    if len(sys.argv) != 3:
        print("Usage: generate_dashboard.py <input.csv> <output.html>", file=sys.stderr)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    rows = load_rows(input_path)
    kept, total_submissions, incomplete_excluded = filter_rows(rows)
    data = build_dashboard_data(kept)
    meta = {
        "total_submissions": total_submissions,
        "total_kept": len(kept),
        "incomplete_excluded": incomplete_excluded,
    }

    html = render_html(data, meta, source_filename=input_path.split("/")[-1])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote dashboard: {output_path}")


if __name__ == "__main__":
    main()