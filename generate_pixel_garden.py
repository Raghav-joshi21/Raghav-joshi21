import requests
import os
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
    # label only first occurrence of each month
    seen = set()
    for w in result:
        if w["month"] not in seen:
            seen.add(w["month"])
            w["label"] = w["month"]
        else:
            w["label"] = ""
    return result

def generate_svg(weeks):
    PX = 7
    COLS = 148
    ROWS = 78
    GY = 62
    W = COLS * PX
    H = ROWS * PX

    # pixel buffer
    buf = [[None]*COLS for _ in range(ROWS)]

    def px(x, y, c):
        if 0 <= x < COLS and 0 <= y < ROWS:
            buf[y][x] = c

    def row(x, y, w, c):
        for i in range(w): px(x+i, y, c)

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
        'yc1':'#6d4c41','yc2':'#4e342e','yc3':'#3e2723',
        'po1':'#ffcc02','po2':'#ffa000','po3':'#e65100','po4':'#bf360c',
        'oc1':'#4e342e','oc2':'#3e2723','oc3':'#1a0000',
        'pr1':'#ff8f00','pr2':'#e65100','pr3':'#bf360c','pr4':'#7f0000',
        'rc1':'#3e2723','rc2':'#1a0000','rc3':'#0d0000',
    }

    def draw_sky():
        skys = [C['sky1'],C['sky2'],C['sky3'],C['sky4'],C['sky5']]
        for r in range(GY):
            t = r / GY
            si = min(int(t * len(skys)), len(skys)-1)
            row(0, r, COLS, skys[si])

    def draw_sun(sx, sy):
        row(sx+1, sy-3, 5, C['sun'])
        row(sx+1, sy+7, 5, C['sun'])
        blk(sx-2, sy-1, 2, 7, C['sun'])
        blk(sx+7, sy-1, 2, 7, C['sun'])
        blk(sx, sy-2, 7, 9, C['sun'])
        blk(sx-1, sy-1, 9, 7, C['sun'])
        blk(sx+1, sy-1, 3, 3, C['sunhi'])

    def draw_cloud(cx, cy):
        blk(cx+3, cy, 6, 2, C['cloudsh'])
        blk(cx+1, cy+1, 10, 2, C['cloudsh'])
        blk(cx, cy+2, 13, 3, C['cloud'])
        blk(cx+2, cy+1, 9, 4, C['cloud'])
        blk(cx+4, cy, 6, 5, C['cloud'])

    def draw_ground():
        blk(0, GY, COLS, ROWS-GY, C['g1'])
        row(0, GY, COLS, C['g3'])
        row(0, GY+1, COLS, C['g2'])
        for x in range(0, COLS, 3): px(x, GY-1, C['g3'])
        for x in range(1, COLS, 5):
            px(x, GY-2, C['g4'])
            px(x+2, GY-3, C['g3'])

    def flower_yellow(bx, fy):
        row(bx-1, fy, 3, C['py1'])
        blk(bx-3, fy+1, 7, 1, C['py2'])
        blk(bx-3, fy+2, 7, 2, C['py3'])
        blk(bx-3, fy+4, 7, 1, C['py2'])
        row(bx-1, fy+5, 3, C['py1'])
        px(bx-3, fy+2, C['py4']); px(bx+3, fy+2, C['py4'])
        px(bx-2, fy+1, C['py2']); px(bx+2, fy+1, C['py2'])
        px(bx-2, fy+4, C['py2']); px(bx+2, fy+4, C['py2'])
        blk(bx-1, fy+1, 3, 3, C['yc1'])
        blk(bx-1, fy+2, 3, 1, C['yc2'])
        px(bx, fy+2, C['yc3'])
        px(bx-1, fy+1, C['yc2']); px(bx+1, fy+1, C['yc2'])

    def flower_orange(bx, fy):
        row(bx-1, fy-1, 3, C['po1'])
        blk(bx-4, fy, 9, 1, C['po2'])
        blk(bx-4, fy+1, 9, 5, C['po2'])
        blk(bx-4, fy+6, 9, 1, C['po2'])
        row(bx-1, fy+7, 3, C['po1'])
        blk(bx-4, fy+1, 2, 5, C['po3'])
        blk(bx+3, fy+1, 2, 5, C['po3'])
        blk(bx-2, fy+1, 5, 5, C['oc1'])
        blk(bx-1, fy+2, 3, 3, C['oc2'])
        px(bx, fy+3, C['oc3'])

    def flower_red(bx, fy):
        row(bx-2, fy-2, 5, C['pr1'])
        px(bx-4, fy-1, C['pr1']); px(bx+4, fy-1, C['pr1'])
        blk(bx-5, fy, 11, 1, C['pr2'])
        blk(bx-5, fy+1, 11, 6, C['pr2'])
        blk(bx-5, fy+7, 11, 1, C['pr2'])
        px(bx-4, fy+8, C['pr1']); px(bx+4, fy+8, C['pr1'])
        row(bx-2, fy+9, 5, C['pr1'])
        blk(bx-5, fy+1, 2, 6, C['pr3'])
        blk(bx+4, fy+1, 2, 6, C['pr3'])
        blk(bx-3, fy+1, 7, 6, C['rc1'])
        blk(bx-2, fy+2, 5, 4, C['rc2'])
        blk(bx-1, fy+3, 3, 2, C['rc3'])
        px(bx-2, fy+2, C['rc1']); px(bx+2, fy+2, C['rc1'])
        px(bx-2, fy+5, C['rc1']); px(bx+2, fy+5, C['rc1'])

    def draw_flower(bx, commits):
        if commits == 0: return
        max_stem = min(6 + int(commits * 2.8), 40)
        stem_top = GY - max_stem
        for s in range(max_stem):
            px(bx, stem_top+s, C['stem'])
            px(bx+1, stem_top+s, C['stem2'])
        if max_stem > 10 and commits >= 3:
            ly = GY - int(max_stem * 0.42)
            blk(bx-5, ly, 5, 1, C['leaf2'])
            blk(bx-6, ly+1, 5, 1, C['leaf'])
            blk(bx-4, ly+2, 3, 1, C['leaf3'])
        if max_stem > 16 and commits >= 5:
            ly2 = GY - int(max_stem * 0.65)
            blk(bx+2, ly2, 5, 1, C['leaf2'])
            blk(bx+3, ly2+1, 5, 1, C['leaf'])
            blk(bx+2, ly2+2, 3, 1, C['leaf3'])
        head_y = stem_top - 3
        if commits >= 9: flower_red(bx, head_y - 8)
        elif commits >= 5: flower_orange(bx, head_y - 6)
        else: flower_yellow(bx, head_y - 4)

    # Draw everything
    draw_sky()
    draw_sun(130, 6)
    draw_cloud(4, 8); draw_cloud(44, 5); draw_cloud(90, 9)
    draw_ground()

    for i, week in enumerate(weeks):
        x = round(4 + i * (COLS - 8) / len(weeks))
        draw_flower(x, week["commits"])

    # Build SVG rects
    rects = []
    for r in range(ROWS):
        for c in range(COLS):
            color = buf[r][c] or (C['sky5'] if r < GY else C['g1'])
            rx = c * PX + 1
            ry = r * PX + 1
            rects.append(f'<rect x="{rx}" y="{ry}" width="{PX-1}" height="{PX-1}" fill="{color}"/>')

    # Month labels
    month_texts = []
    for i, week in enumerate(weeks):
        if week["label"]:
            x = (4 + i * (COLS - 8) / len(weeks)) * PX
            month_texts.append(f'<text x="{x:.1f}" y="{H - PX*3}" font-family="monospace" font-size="{PX+1}" font-weight="bold" fill="#90caf9">{week["label"]}</text>')

    # Title
    title_text = f'<text x="{W//2}" y="{H - PX + 2}" font-family="monospace" font-size="{PX*2}" font-weight="bold" fill="#ffe066" text-anchor="middle">Raghav\'s Contribution Garden</text>'

    # Legend
    legend = f'''
<rect x="{PX}" y="{PX}" width="{PX*22}" height="{PX*3}" fill="rgba(0,0,0,0.7)"/>
<rect x="{PX+2}" y="{PX+4}" width="{PX-1}" height="{PX-1}" fill="#fdd835"/>
<text x="{PX*3+2}" y="{PX*2+3}" font-family="monospace" font-size="{PX}" font-weight="bold" fill="white">1-4 commits</text>
<rect x="{PX*2+76}" y="{PX+4}" width="{PX-1}" height="{PX-1}" fill="#ffa000"/>
<text x="{PX*2+78+PX}" y="{PX*2+3}" font-family="monospace" font-size="{PX}" font-weight="bold" fill="white">5-8</text>
<rect x="{PX*2+152}" y="{PX+4}" width="{PX-1}" height="{PX-1}" fill="#e65100"/>
<text x="{PX*2+154+PX}" y="{PX*2+3}" font-family="monospace" font-size="{PX}" font-weight="bold" fill="white">9+</text>
'''

    svg = f'''<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<rect width="{W}" height="{H}" fill="#111111"/>
{''.join(rects)}
<rect x="0" y="{H - PX*5}" width="{W}" height="{PX*5}" fill="rgba(0,0,0,0.72)"/>
{''.join(month_texts)}
{title_text}
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
