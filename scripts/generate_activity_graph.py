import json
from html import escape
from pathlib import Path

DATA = Path("/tmp/contrib.json")
OUT = Path("assets/activity-graph.svg")

payload = json.loads(DATA.read_text(encoding="utf-8"))
errors = payload.get("errors")
if errors:
    raise SystemExit(f"GitHub GraphQL error: {errors}")

days = []
for week in payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
    days.extend(week["contributionDays"])

# Keep the most recent 365 days and preserve chronological order.
days = sorted(days, key=lambda item: item["date"])[-365:]
counts = [int(item["contributionCount"]) for item in days]

W, H = 1100, 300
PAD_L, PAD_R, PAD_T, PAD_B = 55, 28, 48, 46
PLOT_W = W - PAD_L - PAD_R
PLOT_H = H - PAD_T - PAD_B
MAX = max(counts) if counts else 1

# Log-ish scaling keeps quiet periods readable without hiding busy days.
def y_for(value):
    import math
    scaled = math.log1p(value) / math.log1p(MAX) if MAX else 0
    return PAD_T + PLOT_H - scaled * PLOT_H

def x_for(index):
    if len(days) <= 1:
        return PAD_L
    return PAD_L + index * PLOT_W / (len(days) - 1)

points = [(x_for(i), y_for(c)) for i, c in enumerate(counts)]
line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
area = f"{PAD_L},{PAD_T + PLOT_H} {line} {PAD_L + PLOT_W},{PAD_T + PLOT_H}"

month_labels = []
seen = set()
for i, item in enumerate(days):
    month = item["date"][:7]
    if month not in seen:
        seen.add(month)
        x = x_for(i)
        label = item["date"][:7]
        month_labels.append(f'<text x="{x:.1f}" y="{H - 16}" class="label">{escape(label)}</text>')

# A compact, self-contained SVG means the README no longer depends on a third-party
# activity-graph image server being available.
total = sum(counts)
peak = max(counts) if counts else 0
last_date = days[-1]["date"] if days else ""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">Contribution Activity</title>
<desc id="desc">GitHub contribution activity for Raahin Suhail over the last year. {total} total contributions; peak of {peak} in one day.</desc>
<defs>
  <linearGradient id="area" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0%" stop-color="#00e5a8" stop-opacity="0.30"/>
    <stop offset="100%" stop-color="#00e5a8" stop-opacity="0.02"/>
  </linearGradient>
</defs>
<style>
  .bg {{ fill:#050505; }}
  .grid {{ stroke:#20262d; stroke-width:1; }}
  .line {{ fill:none; stroke:#00e5a8; stroke-width:2.5; stroke-linejoin:round; stroke-linecap:round; }}
  .area {{ fill:url(#area); }}
  .label {{ fill:#8b949e; font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
  .title {{ fill:#e6edf3; font:600 16px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
  .meta {{ fill:#8b949e; font:12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
</style>
<rect class="bg" x="0" y="0" width="{W}" height="{H}" rx="12"/>
<text x="{PAD_L}" y="24" class="title">Contribution Activity</text>
<text x="{W - PAD_R}" y="24" text-anchor="end" class="meta">{total} contributions · last year</text>
<line x1="{PAD_L}" y1="{PAD_T + PLOT_H * 0.25:.1f}" x2="{PAD_L + PLOT_W}" y2="{PAD_T + PLOT_H * 0.25:.1f}" class="grid"/>
<line x1="{PAD_L}" y1="{PAD_T + PLOT_H * 0.50:.1f}" x2="{PAD_L + PLOT_W}" y2="{PAD_T + PLOT_H * 0.50:.1f}" class="grid"/>
<line x1="{PAD_L}" y1="{PAD_T + PLOT_H * 0.75:.1f}" x2="{PAD_L + PLOT_W}" y2="{PAD_T + PLOT_H * 0.75:.1f}" class="grid"/>
<line x1="{PAD_L}" y1="{PAD_T + PLOT_H:.1f}" x2="{PAD_L + PLOT_W}" y2="{PAD_T + PLOT_H:.1f}" class="grid"/>
<polygon points="{area}" class="area"/>
<polyline points="{line}" class="line"/>
{''.join(month_labels)}
<text x="{W - PAD_R}" y="{H - 16}" text-anchor="end" class="meta">Updated {escape(last_date)}</text>
</svg>
'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"Generated {OUT} with {total} contributions through {last_date}.")
