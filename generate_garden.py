import requests
import json
import os
from datetime import datetime, timedelta
import math

TOKEN = os.environ.get("GITHUB_TOKEN")
USERNAME = os.environ.get("GITHUB_USERNAME", "Raghav-joshi21")

def get_contributions():
    query = """
    query($username: String!) {
      user(login: $username) {
        contributionsCollection {
          contributionCalendar {
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    headers = {"Authorization": f"Bearer {TOKEN}"}
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": USERNAME}},
        headers=headers
    )
    data = response.json()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    
    result = []
    for week in weeks:
        total = sum(d["contributionCount"] for d in week["contributionDays"])
        date = week["contributionDays"][0]["date"]
        result.append({"commits": total, "date": date})
    return result

def get_petal_color(commits):
    if commits >= 9:
        return "#ff6600"
    elif commits >= 5:
        return "#f0a800"
    else:
        return "#f5d020"

def get_center_color(commits):
    if commits >= 9:
        return "#cc2200"
    elif commits >= 5:
        return "#e05500"
    else:
        return "#e8820a"

def get_petal_count(commits):
    if commits >= 8:
        return 8
    elif commits >= 4:
        return 6
    else:
        return 4

def generate_svg(weeks):
    W, H, groundY = 680, 320, 260
    plants = []

    total_weeks = len(weeks)
    for i, week in enumerate(weeks):
        commits = week["commits"]
        if commits == 0:
            continue
        x = 30 + i * (620 / max(total_weeks - 1, 1))
        max_h = min(20 + commits * 17, 200)
        phase = (i * 2.3) % (2 * math.pi)
        sway_amt = 4 if commits > 6 else 2
        plants.append({
            "x": x, "commits": commits, "maxH": max_h,
            "phase": phase, "swayAmt": sway_amt,
            "date": week["date"]
        })

    month_labels = []
    seen_months = set()
    for i, week in enumerate(weeks):
        month = week["date"][:7]
        if month not in seen_months:
            seen_months.add(month)
            x = 30 + i * (620 / max(len(weeks) - 1, 1))
            label = datetime.strptime(week["date"], "%Y-%m-%d").strftime("%b")
            month_labels.append((x, label))

    svg_parts = [f'''<svg width="680" height="320" viewBox="0 0 680 320" xmlns="http://www.w3.org/2000/svg">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%" stop-color="#1a6fbf"/>
    <stop offset="60%" stop-color="#4da6e8"/>
    <stop offset="100%" stop-color="#a8d8f0"/>
  </linearGradient>
  <radialGradient id="sun" cx="50%" cy="50%" r="50%">
    <stop offset="0%" stop-color="rgba(255,240,100,1)"/>
    <stop offset="50%" stop-color="rgba(255,210,50,0.8)"/>
    <stop offset="100%" stop-color="rgba(255,180,0,0)"/>
  </radialGradient>
  <style>
    .stem {{ stroke: #3b7022; stroke-linecap: round; fill: none; }}
    .leaf {{ fill: #4a8c28; }}
    .ground {{ fill: #2d5a1b; }}
    .ground-top {{ fill: #3b7022; }}
    .cloud {{ fill: rgba(255,255,255,0.82); }}
    .month {{ font-family: sans-serif; font-size: 11px; fill: #1a4a0a; text-anchor: middle; }}
    @keyframes sway {{
      0%,100% {{ transform: rotate(0deg); }}
      50% {{ transform: rotate(2deg); }}
    }}
    @keyframes grow {{
      from {{ transform: scaleY(0); transform-origin: bottom; }}
      to {{ transform: scaleY(1); transform-origin: bottom; }}
    }}
    .plant {{ animation: grow 1.5s ease-out forwards; transform-origin: bottom; }}
    .petal {{ animation: sway 3s ease-in-out infinite; transform-box: fill-box; transform-origin: center bottom; }}
  </style>
</defs>

<rect width="680" height="{groundY}" fill="url(#sky)"/>
<circle cx="600" cy="55" r="40" fill="url(#sun)"/>

<ellipse cx="80" cy="55" rx="45" ry="18" class="cloud"/>
<ellipse cx="52" cy="61" rx="26" ry="13" class="cloud"/>
<ellipse cx="110" cy="60" rx="30" ry="14" class="cloud"/>

<ellipse cx="300" cy="40" rx="60" ry="18" class="cloud"/>
<ellipse cx="270" cy="46" rx="35" ry="13" class="cloud"/>
<ellipse cx="340" cy="45" rx="38" ry="14" class="cloud"/>

<ellipse cx="490" cy="65" rx="40" ry="16" class="cloud"/>
<ellipse cx="465" cy="70" rx="25" ry="12" class="cloud"/>
<ellipse cx="518" cy="69" rx="28" ry="13" class="cloud"/>

<rect y="{groundY}" width="680" height="{H - groundY}" class="ground"/>
<rect y="{groundY}" width="680" height="10" class="ground-top"/>
''']

    for p in plants:
        x = p["x"]
        commits = p["commits"]
        max_h = p["maxH"]
        tip_x = x
        tip_y = groundY - max_h
        stem_w = 3 if commits > 6 else 2
        delay = (x / 680) * 1.2

        svg_parts.append(f'''
<g class="plant" style="animation-delay: {delay:.2f}s">
  <path class="stem" stroke-width="{stem_w}"
    d="M{x:.1f},{groundY} Q{x:.1f},{groundY - max_h*0.5:.1f} {tip_x:.1f},{tip_y:.1f}"/>
''')
        if commits >= 2:
            lx, ly = x - 8, groundY - max_h * 0.45
            svg_parts.append(f'  <ellipse class="leaf" cx="{lx:.1f}" cy="{ly:.1f}" rx="10" ry="4" transform="rotate(-30 {lx:.1f} {ly:.1f})"/>\n')
        if commits >= 5:
            lx2, ly2 = x + 8, groundY - max_h * 0.65
            svg_parts.append(f'  <ellipse class="leaf" cx="{lx2:.1f}" cy="{ly2:.1f}" rx="10" ry="4" transform="rotate(30 {lx2:.1f} {ly2:.1f})"/>\n')

        r = 9 if commits >= 9 else (7 if commits >= 5 else 5)
        petal_color = get_petal_color(commits)
        center_color = get_center_color(commits)
        petal_count = get_petal_count(commits)
        petal_delay = delay + 0.8

        for pi in range(petal_count):
            angle = (pi / petal_count) * 2 * math.pi
            px = tip_x + math.cos(angle) * (r + 4)
            py = tip_y + math.sin(angle) * (r + 4)
            rot = math.degrees(angle)
            sway_delay = petal_delay + pi * 0.1
            svg_parts.append(f'  <ellipse class="petal" cx="{px:.1f}" cy="{py:.1f}" rx="{r*0.8:.1f}" ry="{r*0.45:.1f}" fill="{petal_color}" transform="rotate({rot:.1f} {px:.1f} {py:.1f})" style="animation-delay:{sway_delay:.2f}s"/>\n')

        svg_parts.append(f'  <circle cx="{tip_x:.1f}" cy="{tip_y:.1f}" r="{r}" fill="{center_color}"/>\n')
        svg_parts.append('</g>\n')

    for mx, label in month_labels:
        svg_parts.append(f'<text x="{mx:.1f}" y="{H - 5}" class="month">{label}</text>\n')

    svg_parts.append(f'''
<rect x="12" y="10" width="220" height="22" rx="5" fill="rgba(0,0,0,0.25)"/>
<circle cx="26" cy="21" r="5" fill="#f5d020"/>
<text x="36" y="25" font-family="sans-serif" font-size="10" fill="#fff">1–4</text>
<circle cx="80" cy="21" r="5" fill="#f0a800"/>
<text x="90" y="25" font-family="sans-serif" font-size="10" fill="#fff">5–8</text>
<circle cx="134" cy="21" r="5" fill="#cc2200"/>
<text x="144" y="25" font-family="sans-serif" font-size="10" fill="#fff">9+ commits</text>
</svg>''')

    return "".join(svg_parts)

if __name__ == "__main__":
    print("Fetching contributions...")
    weeks = get_contributions()
    print(f"Got {len(weeks)} weeks of data")
    svg = generate_svg(weeks)
    os.makedirs("dist", exist_ok=True)
    with open("dist/garden.svg", "w") as f:
        f.write(svg)
    print("garden.svg generated successfully!")
