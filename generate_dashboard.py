#!/usr/bin/env python3
"""
generate_dashboard.py

Parses a Qualtrics survey export (CSV), filters out preview responses and
responses that are less than 50% complete, tallies the answers to every
question, and renders a self-contained HTML dashboard (Chart.js via CDN).

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
# Falls back to the short code itself if a column isn't in this map, so the
# script degrades gracefully if Qualtrics adds/removes questions later.
QUESTION_LABELS = {
    "Q1": "If the UU offered an optional physical student card, would you request it?",
    "Q2": "Why? (selected choice)",
    "Q2_8_TEXT": "Why? — \u201cAnother reason\u201d (free text)",
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
    """Drop Survey Preview rows and rows under 50% progress."""
    kept, preview_excluded, incomplete_excluded = [], 0, 0
    for r in rows:
        if r.get("Status", "").strip() == "Survey Preview":
            preview_excluded += 1
            continue
        if to_float(r.get("Progress")) < 50:
            incomplete_excluded += 1
            continue
        kept.append(r)
    return kept, preview_excluded, incomplete_excluded


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


def free_text(rows, field):
    return [(r.get(field) or "").strip() for r in rows if (r.get(field) or "").strip()]


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
    q2_other = free_text(rows, "Q2_8_TEXT")
    q16_raw = tally_single(rows, "Q16")
    q16_raw.pop("(No answer)", None)  # only asked conditionally; skip the blanks
    q5_comments = free_text(rows, "Q5")
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
        return "\n".join(
            f'<div class="comment-card">{escape(item)}</div>' for item in items
        )

    other_reasons_html = comment_list_html(
        data["q2_other"], "No free-text reasons were given."
    )
    comments_html = comment_list_html(
        data["q5_comments"], "No comments were left."
    )

    total_raw = meta["total_raw"]
    total_kept = meta["total_kept"]
    preview_excluded = meta["preview_excluded"]
    incomplete_excluded = meta["incomplete_excluded"]

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Digital Student Card Survey — Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  :root {{
    --bg: #f5f6f8;
    --card: #ffffff;
    --border: #e3e5e9;
    --text: #1a1d21;
    --text-muted: #6b7280;
    --accent: #4f46e5;
    --accent-soft: #eef2ff;
    --yes: #4f46e5;
    --maybe: #f59e0b;
    --no: #ef4444;
    --other: #94a3b8;
    --radius: 12px;
    --shadow: 0 1px 2px rgba(16,24,40,0.06), 0 1px 3px rgba(16,24,40,0.08);
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 2rem 1.5rem 4rem;
  }}
  .wrap {{ max-width: 1140px; margin: 0 auto; }}
  header.page-header {{ margin-bottom: 2rem; }}
  header.page-header h1 {{
    font-size: 1.6rem;
    margin: 0 0 0.35rem;
    font-weight: 700;
  }}
  header.page-header p {{
    margin: 0;
    color: var(--text-muted);
    font-size: 0.92rem;
  }}
  .stat-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 0.9rem;
    margin-bottom: 2rem;
  }}
  .stat-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
  }}
  .stat-card .num {{ font-size: 1.6rem; font-weight: 700; line-height: 1.1; }}
  .stat-card .label {{ font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem; }}
  .stat-card.excluded .num {{ color: var(--no); }}
  .stat-card.kept .num {{ color: var(--accent); }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
    gap: 1.25rem;
  }}
  .card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.5rem;
    box-shadow: var(--shadow);
  }}
  .card h2 {{
    font-size: 1rem;
    margin: 0 0 0.15rem;
    font-weight: 650;
  }}
  .card .sub {{
    font-size: 0.8rem;
    color: var(--text-muted);
    margin: 0 0 1rem;
  }}
  .card.full {{ grid-column: 1 / -1; }}
  .chart-box {{ position: relative; height: 280px; }}
  .chart-box.tall {{ height: 340px; }}
  .comment-list {{
    max-height: 340px;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    padding-right: 0.25rem;
  }}
  .comment-card {{
    background: var(--accent-soft);
    border-radius: 8px;
    padding: 0.7rem 0.9rem;
    font-size: 0.88rem;
    line-height: 1.45;
    color: #312e81;
    white-space: pre-wrap;
  }}
  .empty-msg {{ color: var(--text-muted); font-size: 0.88rem; font-style: italic; }}
  .contact-row {{
    display: flex;
    gap: 1.5rem;
    margin-top: 0.5rem;
  }}
  .contact-pill {{
    background: var(--accent-soft);
    color: var(--accent);
    border-radius: 999px;
    padding: 0.4rem 0.9rem;
    font-size: 0.85rem;
    font-weight: 600;
  }}
  footer {{
    text-align: center;
    color: var(--text-muted);
    font-size: 0.78rem;
    margin-top: 2.5rem;
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="page-header">
    <h1>Digital Student Card Survey — Results Dashboard</h1>
    <p>Generated {generated_at}</p>
  </header>

  <div class="stat-row">
    <div class="stat-card">
      <div class="num">{total_raw}</div>
      <div class="label">Total submissions received</div>
    </div>
    <div class="stat-card excluded">
      <div class="num">{preview_excluded}</div>
      <div class="label">Excluded — survey preview</div>
    </div>
    <div class="stat-card excluded">
      <div class="num">{incomplete_excluded}</div>
      <div class="label">Excluded — under 50% complete</div>
    </div>
    <div class="stat-card kept">
      <div class="num">{total_kept}</div>
      <div class="label">Included in this analysis</div>
    </div>
  </div>

  <div class="grid">

    <div class="card">
      <h2>{escape(QUESTION_LABELS["Q1"])}</h2>
      <p class="sub">n = {total_kept}</p>
      <div class="chart-box"><canvas id="chartQ1"></canvas></div>
    </div>

    <div class="card">
      <h2>{escape(QUESTION_LABELS["Q4"])}</h2>
      <p class="sub">n = {total_kept}</p>
      <div class="chart-box"><canvas id="chartQ4"></canvas></div>
    </div>

    <div class="card full">
      <h2>{escape(QUESTION_LABELS["Q2"])}</h2>
      <p class="sub">{data["q2"]["answered"]} respondents selected at least one reason &middot; multiple selections allowed</p>
      <div class="chart-box tall"><canvas id="chartQ2"></canvas></div>
    </div>

    <div class="card">
      <h2>{escape(QUESTION_LABELS["Q2_8_TEXT"])}</h2>
      <p class="sub">{len(data["q2_other"])} free-text responses</p>
      <div class="comment-list">
        {other_reasons_html}
      </div>
    </div>

    <div class="card">
      <h2>{escape(QUESTION_LABELS["Q16"])}</h2>
      <p class="sub">n = {data["q16"]["answered"]} (only asked of those willing to contribute)</p>
      <div class="chart-box"><canvas id="chartQ16"></canvas></div>
    </div>

    <div class="card full">
      <h2>{escape(QUESTION_LABELS["Q5"])}</h2>
      <p class="sub">{len(data["q5_comments"])} comments left</p>
      <div class="comment-list">
        {comments_html}
      </div>
    </div>

    <div class="card full">
      <h2>Optional contact info</h2>
      <p class="sub">Respondents could optionally leave their name/e-mail for follow-up. Shown as counts only.</p>
      <div class="contact-row">
        <span class="contact-pill">{data["name_count"]} left a name</span>
        <span class="contact-pill">{data["email_count"]} left an e-mail</span>
      </div>
    </div>

  </div>

  <footer>Preview responses and submissions under 50% progress were excluded from all figures above.</footer>
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

new Chart(document.getElementById('chartQ2'), {{
  type: 'bar',
  data: {{
    labels: DATA.q2.labels,
    datasets: [{{ data: DATA.q2.counts, backgroundColor: '#4f46e5', borderRadius: 4 }}]
  }},
  options: baseOptions({{
    indexAxis: 'y',
    scales: {{ x: {{ beginAtZero: true, ticks: {{ precision: 0 }} }} }}
  }})
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
    kept, preview_excluded, incomplete_excluded = filter_rows(rows)
    data = build_dashboard_data(kept)
    meta = {
        "total_raw": len(rows),
        "total_kept": len(kept),
        "preview_excluded": preview_excluded,
        "incomplete_excluded": incomplete_excluded,
    }

    html = render_html(data, meta, source_filename=input_path.split("/")[-1])

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Wrote dashboard: {output_path}")
    print(
        f"  {meta['total_raw']} total -> {preview_excluded} preview excluded, "
        f"{incomplete_excluded} incomplete excluded -> {meta['total_kept']} analyzed"
    )


if __name__ == "__main__":
    main()
