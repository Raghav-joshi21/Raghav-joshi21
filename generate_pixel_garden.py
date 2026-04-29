import requests
import os
import math
from datetime import datetime

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
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": USERNAME}},
        headers=headers
    )
    data = r.json()
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    result = []
    for week in weeks:
        total = sum(d["contributionCount"] for d in week["contributionDays"])
        date = week["contributionDays"][0]["date"]
        month = datetime.strptime(date, "%Y-%m-%d").strftime("%b")
        result.append({"commits": total, "date": date, "month": month})
    seen = set()
    for w in result:
        if w["month"] not in seen:
            seen.add(w["month"])
            w["label"] = w["month"]
        else:
            w["label"] = ""
    return result

def generate_svg(weeks):
    PX = 6
    COLS = 170
    ROWS = 82
    GY = 64
    W = COLS * PX
    H = ROWS * PX

    buf = [[None]*COLS for _ in range(ROWS)]

    def p(x, y, c):
        if 0 <= x < COLS and 0 <= y < ROWS:
            buf[y][x] = c

    def row(x, y, w, c):
        for i in range(w): p(x+i, y, c)

    def blk(x, y, w, h, c):
        for r in range(h): row(x, y+r, w, c)

    C = {
        'sky1':'#0d47a1','sky2':'#1565c0','sky3':'#1e88e5','sky4':'#42a5f5','sky5':'#90caf9',
        'sun':'#ffe066','sunhi':'#fffde7',
        'cloud':'#ffffff','cloudsh':'#e3f2fd',
        'g1':'#1b5e20','g2':'#2e7d32','g3':'#43a047','g4':'#66bb6a',
        'stem':'#33691e','stem2':'#558b2f',
        'leaf':'#388e3c','leaf2':'#2e7d32','leaf3':'#1b5e20',
        'py1':'#fff176','py2':'#ffee58','py3':'#fdd835','py4':'#f9a825',
        'yc1':'#ff8f00','yc2':'#e65100','yc3':'#bf360c',
        'po1':'#ffcc02','po2':'#ffa000','po3':'#e65100',
        'oc1':'#bf360c','oc2':'#8d2c02','oc3':'#6d1f00',
        'pr1':'#ff8f00','pr2':'#e65100','pr3':'#bf360c',
        'rc1':'#bf360c','rc2':'#8d2c02','rc3':'#5d1f00',
    }

    def draw_sky():
        skys = [C['sky1'],C['sky2'],C['sky3'],C['sky4'],C['sky5']]
        for r in range(GY):
            si = min(int(r/GY*len(skys)), len(skys)-1)
            row(0, r, COLS, skys[si])

    def draw_sun():
        sx, sy = 154, 6
        row(sx+1, sy-3, 5, C['sun']); row(sx+1, sy+7, 5, C['sun'])
        blk(sx-2, sy-1, 2, 7, C['sun']); blk(sx+7, sy-1, 2, 7, C['sun'])
        blk(sx, sy-2, 7, 9, C['sun']); blk(sx-1, sy-1, 9, 7, C['sun'])
        blk(sx+1, sy-1, 3, 3, C['sunhi'])

    def draw_cloud_to_buf(cx, cy):
        x, y = int(cx), int(cy)
        blk(x+3, y, 6, 2, C['cloudsh']); blk(x+1, y+1, 10, 2, C['cloudsh'])
        blk(x, y+2, 13, 3, C['cloud']); blk(x+2, y+1, 9, 4, C['cloud'])
        blk(x+4, y, 6, 5, C['cloud'])

    def draw_ground():
        blk(0, GY, COLS, ROWS-GY, C['g1'])
        row(0, GY, COLS, C['g3']); row(0, GY+1, COLS, C['g2'])
        for x in range(0, COLS, 3): p(x, GY-1, C['g3'])
        for x in range(1, COLS, 5):
            p(x, GY-2, C['g4'])
            if x+2 < COLS: p(x+2, GY-3, C['g3'])

    def flower_yellow(bx, fy):
        row(bx-1, fy, 3, C['py1'])
        blk(bx-3, fy+1, 7, 1, C['py2']); blk(bx-3, fy+2, 7, 2, C['py3'])
        blk(bx-3, fy+4, 7, 1, C['py2']); row(bx-1, fy+5, 3, C['py1'])
        p(bx-3, fy+2, C['py4']); p(bx+3, fy+2, C['py4'])
        blk(bx-1, fy+1, 3, 3, C['yc1'])
        p(bx-1, fy+2, C['yc2']); p(bx+1, fy+2, C['yc2']); p(bx, fy+2, C['yc3'])
        p(bx-1, fy+1, '#ffca28')

    def flower_orange(bx, fy):
        row(bx-1, fy-1, 3, C['po1'])
        blk(bx-4, fy, 9, 1, C['po2']); blk(bx-4, fy+1, 9, 5, C['po2'])
        blk(bx-4, fy+6, 9, 1, C['po2']); row(bx-1, fy+7, 3, C['po1'])
        blk(bx-4, fy+1, 2, 5, C['po3']); blk(bx+3, fy+1, 2, 5, C['po3'])
        blk(bx-2, fy+1, 5, 5, C['oc1']); blk(bx-1, fy+2, 3, 3, C['oc2'])
        p(bx, fy+3, C['oc3']); p(bx-2, fy+1, '#ff8f00'); p(bx-1, fy+1, '#ffa000')

    def flower_red(bx, fy):
        row(bx-2, fy-2, 5, C['pr1'])
        p(bx-4, fy-1, C['pr1']); p(bx+4, fy-1, C['pr1'])
        blk(bx-5, fy, 11, 1, C['pr2']); blk(bx-5, fy+1, 11, 6, C['pr2'])
        blk(bx-5, fy+7, 11, 1, C['pr2'])
        p(bx-4, fy+8, C['pr1']); p(bx+4, fy+8, C['pr1']); row(bx-2, fy+9, 5, C['pr1'])
        blk(bx-5, fy+1, 2, 6, C['pr3']); blk(bx+4, fy+1, 2, 6, C['pr3'])
        blk(bx-3, fy+1, 7, 6, C['rc1']); blk(bx-2, fy+2, 5, 4, C['rc2'])
        blk(bx-1, fy+3, 3, 2, C['rc3'])
        p(bx-1, fy+2, '#ffa000'); p(bx, fy+2, '#ffb300'); p(bx+1, fy+2, '#ffa000')
        p(bx, fy+1, '#ff8f00')

    def draw_flower(bx, commits):
        if commits == 0: return
        max_stem = min(6 + int(commits * 2.5), 36)
        stem_top = GY - max_stem
        for s in range(max_stem):
            p(bx, stem_top+s, C['stem']); p(bx+1, stem_top+s, C['stem2'])
        if max_stem > 10 and commits >= 3:
            ly = GY - int(max_stem * 0.42)
            blk(bx-5, ly, 5, 1, C['leaf2']); blk(bx-6, ly+1, 5, 1, C['leaf'])
            blk(bx-4, ly+2, 3, 1, C['leaf3'])
        if max_stem > 14 and commits >= 5:
            ly2 = GY - int(max_stem * 0.65)
            blk(bx+2, ly2, 5, 1, C['leaf2']); blk(bx+3, ly2+1, 5, 1, C['leaf'])
            blk(bx+2, ly2+2, 3, 1, C['leaf3'])
        head_y = stem_top - 3
        if commits >= 9: flower_red(bx, head_y - 8)
        elif commits >= 5: flower_orange(bx, head_y - 6)
        else: flower_yellow(bx, head_y - 4)

    # --- Draw static background into buf ---
    draw_sky()
    draw_sun()
    draw_ground()

    spacing = math.floor((COLS - 8) / len(weeks))
    flower_positions = []
    for i, week in enumerate(weeks):
        bx = 4 + i * spacing
        flower_positions.append(bx)
        draw_flower(bx, week["commits"])

    # --- Render background rects (no clouds — those go as animated SVG groups) ---
    bg_rects = []
    for r in range(ROWS):
        for c in range(COLS):
            color = buf[r][c] or (C['sky5'] if r < GY else C['g1'])
            bg_rects.append(f'<rect x="{c*PX+1}" y="{r*PX+1}" width="{PX-1}" height="{PX-1}" fill="{color}"/>')

    # --- Build animated cloud groups ---
    def cloud_rects(ox, oy):
        rects = []
        shape = [
            (3,0,6,2,'#e3f2fd'),(1,1,10,2,'#e3f2fd'),
            (0,2,13,3,'#ffffff'),(2,1,9,4,'#ffffff'),(4,0,6,5,'#ffffff')
        ]
        for (cx,cy,cw,ch,cc) in shape:
            rects.append(f'<rect x="{(ox+cx)*PX+1}" y="{(oy+cy)*PX+1}" width="{cw*PX-1}" height="{ch*PX-1}" fill="{cc}"/>')
        return ''.join(rects)

    clouds_config = [
        {'start_x': 10, 'y': 7,  'speed': 28, 'w': 13},
        {'start_x': 60, 'y': 4,  'speed': 40, 'w': 16},
        {'start_x':120, 'y': 8,  'speed': 33, 'w': 13},
        {'start_x': 85, 'y': 12, 'speed': 50, 'w': 11},
    ]

    cloud_svg = []
    for i, cl in enumerate(clouds_config):
        travel = COLS + cl['w']
        start = cl['start_x']
        dur = cl['speed']
        delay = -(start / travel * dur)
        rects = cloud_rects(0, cl['y'])
        cloud_svg.append(f'''
<g id="cloud{i}">
  <animateTransform attributeName="transform" type="translate"
    from="{start*PX} 0" to="{(start + travel)*PX} 0"
    dur="{dur}s" begin="{delay:.1f}s" repeatCount="indefinite"/>
  {rects}
</g>''')

    # --- Flower sway animations ---
    sway_anims = []
    for i, week in enumerate(weeks):
        if week["commits"] == 0: continue
        bx = flower_positions[i]
        cx = bx * PX + PX
        max_stem = min(6 + int(week["commits"] * 2.5), 36)
        stem_top_y = (GY - max_stem) * PX
        dur = round(2.5 + (i % 7) * 0.3, 1)
        delay = round((i % 5) * 0.4, 1)
        sway_anims.append(f'''<animateTransform xlink:href="#flower{i}" attributeName="transform" type="rotate"
    values="0 {cx} {GY*PX};2 {cx} {GY*PX};0 {cx} {GY*PX};-2 {cx} {GY*PX};0 {cx} {GY*PX}"
    dur="{dur}s" begin="{delay}s" repeatCount="indefinite"/>''')

    # wrap flowers in groups for sway
    flower_groups = []
    for i, week in enumerate(weeks):
        if week["commits"] == 0: continue
        bx = flower_positions[i]
        cx = bx * PX + PX
        dur = round(2.5 + (i % 7) * 0.3, 1)
        delay = round((i % 5) * 0.4, 1)
        flower_groups.append(f'<g id="flower{i}" transform-origin="{cx}px {GY*PX}px"><animateTransform attributeName="transform" type="rotate" values="0 {cx} {GY*PX};2 {cx} {GY*PX};0 {cx} {GY*PX};-2 {cx} {GY*PX};0 {cx} {GY*PX}" dur="{dur}s" begin="{delay}s" repeatCount="indefinite" additive="sum"/></g>')

    # --- grow animation on flower rects ---
    grow_css = []
    for i, week in enumerate(weeks):
        if week["commits"] == 0: continue
        bx = flower_positions[i]
        max_stem = min(6 + int(week["commits"] * 2.5), 36)
        delay = round(i * 0.05, 2)
        grow_css.append(f'.f{i} {{ transform-origin: {bx*PX}px {GY*PX}px; animation: grow {1.2 + delay}s {delay}s ease-out both; }}')

    # --- month labels and title ---
    month_labels = []
    for i, week in enumerate(weeks):
        if week["label"]:
            x = flower_positions[i] * PX
            month_labels.append(f'<text x="{x}" y="{H - PX*4 + 2}" font-family="monospace" font-size="10" font-weight="bold" fill="#90caf9">{week["label"]}</text>')

    title = f'<text x="{W//2}" y="{H-6}" font-family="monospace" font-size="13" font-weight="bold" fill="#ffe066" text-anchor="middle">Raghav\'s Contribution Garden</text>'

    legend = f'''<rect x="6" y="6" width="232" height="28" fill="rgba(0,0,0,0.88)" rx="3"/>
<rect x="6" y="6" width="232" height="28" fill="none" stroke="#ffe066" stroke-width="1" rx="3"/>
<rect x="18" y="13" width="12" height="12" fill="#fdd835"/>
<text x="34" y="24" font-family="monospace" font-size="11" font-weight="bold" fill="white">1-4 commits</text>
<rect x="96" y="13" width="12" height="12" fill="#ffa000"/>
<text x="112" y="24" font-family="monospace" font-size="11" font-weight="bold" fill="white">5-8</text>
<rect x="148" y="13" width="12" height="12" fill="#e65100"/>
<text x="164" y="24" font-family="monospace" font-size="11" font-weight="bold" fill="white">9+</text>'''

    css = f'''
<style>
@keyframes grow {{
  from {{ transform: scaleY(0); }}
  to   {{ transform: scaleY(1); }}
}}
@keyframes cloudmove {{
  from {{ transform: translateX(0); }}
  to   {{ transform: translateX({COLS*PX}px); }}
}}
</style>'''

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
{css}
<!-- black grid background -->
<rect width="{W}" height="{H}" fill="#111111"/>
<!-- static scene -->
{''.join(bg_rects)}
<!-- animated clouds -->
{''.join(cloud_svg)}
<!-- bottom bar -->
<rect x="0" y="{H - PX*5}" width="{W}" height="{PX*5}" fill="rgba(0,0,0,0.82)"/>
<!-- month labels -->
{''.join(month_labels)}
<!-- title -->
{title}
<!-- legend -->
{legend}
</svg>'''

    return svg

if __name__ == "__main__":
    print("Fetching contributions...")
    weeks = get_contributions()
    print(f"Got {len(weeks)} weeks")
    svg = generate_svg(weeks)
    os.makedirs("dist", exist_ok=True)
    with open("dist/garden.svg", "w") as f:
        f.write(svg)
    print("Done! dist/garden.svg generated.")
