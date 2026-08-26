import re
from pathlib import Path

DATA = Path("/tmp/contrib.html")
OUT = Path("assets/github-streak.svg")

html = DATA.read_text(encoding="utf-8", errors="ignore")
patterns = [
    re.compile(r'<td[^>]*data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*data-level="(?P<level>\d+)"[^>]*>.*?</td>', re.S),
    re.compile(r'<td[^>]*data-level="(?P<level>\d+)"[^>]*data-date="(?P<date>\d{4}-\d{2}-\d{2})"[^>]*>.*?</td>', re.S),
]

matches = []
for pattern in patterns:
    matches = list(pattern.finditer(html))
    if matches:
        break
if not matches:
    raise SystemExit("Could not find GitHub contribution calendar.")

days = {}
for m in matches:
    cell = m.group(0)
    count_match = re.search(r'(\d+) contributions?', cell, re.I)
    days[m.group("date")] = int(count_match.group(1)) if count_match else int(m.group("level"))

ordered = sorted(days.items())[-366:]
counts = [c for _, c in ordered]
total = sum(counts)

current = 0
for c in reversed(counts):
    if c > 0:
        current += 1
    elif current:
        break

longest = run = 0
for c in counts:
    if c > 0:
        run += 1
        longest = max(longest, run)
    else:
        run = 0

W, H = 900, 210
BG, TEXT, MUTED, BORDER = "#0D1117", "#C9D1D9", "#8B949E", "#30363D"
ACCENT, RING, FIRE = "#58A6FF", "#8B949E", "#C9D1D9"

def arc(n, scale):
    return min(214, max(18, n * scale))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">
<title id="title">GitHub Contribution Streak</title>
<desc id="desc">{total} total contributions, {current} current streak, {longest} longest streak.</desc>
<rect x="1" y="1" width="898" height="208" rx="10" fill="{BG}" stroke="{BORDER}"/>
<style>.t{{fill:{TEXT};font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}.m{{fill:{MUTED};font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif}}</style>
<g transform="translate(190 92)"><circle r="50" fill="none" stroke="#21262D" stroke-width="7"/><circle r="50" fill="none" stroke="{ACCENT}" stroke-width="7" stroke-linecap="round" stroke-dasharray="{arc(total,1.8)} 314" transform="rotate(-90)"/><text y="7" text-anchor="middle" class="t" font-size="27" font-weight="700">{total}</text><text y="78" text-anchor="middle" class="m" font-size="13">TOTAL CONTRIBUTIONS</text></g>
<g transform="translate(450 92)"><circle r="50" fill="none" stroke="#21262D" stroke-width="7"/><circle r="50" fill="none" stroke="{RING}" stroke-width="7" stroke-linecap="round" stroke-dasharray="{arc(current,12)} 314" transform="rotate(-90)"/><text y="7" text-anchor="middle" class="t" font-size="27" font-weight="700">{current}</text><text y="78" text-anchor="middle" class="m" font-size="13">CURRENT STREAK</text></g>
<g transform="translate(710 92)"><circle r="50" fill="none" stroke="#21262D" stroke-width="7"/><circle r="50" fill="none" stroke="{FIRE}" stroke-width="7" stroke-linecap="round" stroke-dasharray="{arc(longest,7)} 314" transform="rotate(-90)"/><text y="7" text-anchor="middle" class="t" font-size="27" font-weight="700">{longest}</text><text y="78" text-anchor="middle" class="m" font-size="13">LONGEST STREAK</text></g>
</svg>'''

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg, encoding="utf-8")
print(f"Generated {OUT}: total={total}, current={current}, longest={longest}")
