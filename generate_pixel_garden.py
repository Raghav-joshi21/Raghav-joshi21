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

    # Keep only last 26 weeks (~6 months)
    result = result[-26:]

    seen = set()
    for w in result:
        if w["month"] not in seen:
            seen.add(w["month"])
            w["label"] = w["month"]
        else:
            w["label"] = ""
    return result

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def generate_gif(weeks):
    from PIL import Image, ImageDraw, ImageFont

    PX = 6
    COLS = 170
    ROWS = 82
    GY = 64
    W = COLS * PX
    H = ROWS * PX

    C = {
        'sky': ['#0d47a1','#1565c0','#1e88e5','#42a5f5','#90caf9'],
        'sun': '#ffe066', 'sunhi': '#fffde7',
        'cloud': '#ffffff', 'cloudsh': '#e3f2fd',
        'g1': '#1b5e20', 'g2': '#2e7d32', 'g3': '#43a047', 'g4': '#66bb6a',
        'stem': '#33691e', 'stem2': '#558b2f',
        'leaf': '#388e3c', 'leaf2': '#2e7d32', 'leaf3': '#1b5e20',
        'py1': '#fff176', 'py2': '#ffee58', 'py3': '#fdd835', 'py4': '#f9a825',
        'yc1': '#ff8f00', 'yc2': '#e65100', 'yc3': '#bf360c',
        'po1': '#ffcc02', 'po2': '#ffa000', 'po3': '#e65100',
        'oc1': '#bf360c', 'oc2': '#8d2c02', 'oc3': '#6d1f00',
        'pr1': '#ff8f00', 'pr2': '#e65100', 'pr3': '#bf360c',
        'rc1': '#bf360c', 'rc2': '#8d2c02', 'rc3': '#5d1f00',
    }

    # Wider spacing since we have fewer weeks
    n = len(weeks)
    spacing = math.floor((COLS - 8) / n)
    flower_positions = [4 + i * spacing + spacing // 2 for i in range(n)]

    cloud_configs = [
        {'x': 10.0, 'y': 7,  'speed': 0.4,  'w': 13},
        {'x': 60.0, 'y': 4,  'speed': 0.25, 'w': 16},
        {'x':120.0, 'y': 8,  'speed': 0.35, 'w': 13},
        {'x': 85.0, 'y': 12, 'speed': 0.2,  'w': 11},
    ]

    sway_phases = [i * 0.7 for i in range(n)]
    sway_speeds = [0.015 + (i % 7) * 0.003 for i in range(n)]

    GROW_FRAMES = 30
    LOOP_FRAMES = 70

    def make_frame(cloud_positions, grow_frac, sway_t):
        buf = [[None]*COLS for _ in range(ROWS)]

        def p(x, y, c):
            if 0 <= x < COLS and 0 <= y < ROWS:
                buf[y][x] = c

        def row(x, y, w, c):
            for i in range(w): p(x+i, y, c)

        def blk(x, y, w, h, c):
            for r in range(h): row(x, y+r, w, c)

        # sky
        for r in range(GY):
            si = min(int(r/GY*5), 4)
            row(0, r, COLS, C['sky'][si])

        # sun
        sx, sy = 154, 6
        row(sx+1,sy-3,5,C['sun']); row(sx+1,sy+7,5,C['sun'])
        blk(sx-2,sy-1,2,7,C['sun']); blk(sx+7,sy-1,2,7,C['sun'])
        blk(sx,sy-2,7,9,C['sun']); blk(sx-1,sy-1,9,7,C['sun'])
        blk(sx+1,sy-1,3,3,C['sunhi'])

        # clouds
        def draw_cloud(cx, cy):
            x, y = int(cx), int(cy)
            blk(x+3,y,6,2,C['cloudsh']); blk(x+1,y+1,10,2,C['cloudsh'])
            blk(x,y+2,13,3,C['cloud']); blk(x+2,y+1,9,4,C['cloud'])
            blk(x+4,y,6,5,C['cloud'])

        for cl in cloud_positions:
            draw_cloud(cl['x'], cl['y'])

        # ground
        blk(0,GY,COLS,ROWS-GY,C['g1'])
        row(0,GY,COLS,C['g3']); row(0,GY+1,COLS,C['g2'])
        for x in range(0,COLS,3): p(x,GY-1,C['g3'])
        for x in range(1,COLS,5):
            p(x,GY-2,C['g4'])
            if x+2<COLS: p(x+2,GY-3,C['g3'])

        def flower_yellow(bx, fy):
            row(bx-1,fy,3,C['py1'])
            blk(bx-3,fy+1,7,1,C['py2']); blk(bx-3,fy+2,7,2,C['py3'])
            blk(bx-3,fy+4,7,1,C['py2']); row(bx-1,fy+5,3,C['py1'])
            p(bx-3,fy+2,C['py4']); p(bx+3,fy+2,C['py4'])
            blk(bx-1,fy+1,3,3,C['yc1'])
            p(bx-1,fy+2,C['yc2']); p(bx+1,fy+2,C['yc2']); p(bx,fy+2,C['yc3'])
            p(bx-1,fy+1,'#ffca28')

        def flower_orange(bx, fy):
            row(bx-1,fy-1,3,C['po1'])
            blk(bx-4,fy,9,1,C['po2']); blk(bx-4,fy+1,9,5,C['po2'])
            blk(bx-4,fy+6,9,1,C['po2']); row(bx-1,fy+7,3,C['po1'])
            blk(bx-4,fy+1,2,5,C['po3']); blk(bx+3,fy+1,2,5,C['po3'])
            blk(bx-2,fy+1,5,5,C['oc1']); blk(bx-1,fy+2,3,3,C['oc2'])
            p(bx,fy+3,C['oc3']); p(bx-2,fy+1,'#ff8f00'); p(bx-1,fy+1,'#ffa000')

        def flower_red(bx, fy):
            row(bx-2,fy-2,5,C['pr1']); p(bx-4,fy-1,C['pr1']); p(bx+4,fy-1,C['pr1'])
            blk(bx-5,fy,11,1,C['pr2']); blk(bx-5,fy+1,11,6,C['pr2'])
            blk(bx-5,fy+7,11,1,C['pr2'])
            p(bx-4,fy+8,C['pr1']); p(bx+4,fy+8,C['pr1']); row(bx-2,fy+9,5,C['pr1'])
            blk(bx-5,fy+1,2,6,C['pr3']); blk(bx+4,fy+1,2,6,C['pr3'])
            blk(bx-3,fy+1,7,6,C['rc1']); blk(bx-2,fy+2,5,4,C['rc2'])
            blk(bx-1,fy+3,3,2,C['rc3'])
            p(bx-1,fy+2,'#ffa000'); p(bx,fy+2,'#ffb300'); p(bx+1,fy+2,'#ffa000')
            p(bx,fy+1,'#ff8f00')

        for i, week in enumerate(weeks):
            commits = week["commits"]
            if commits == 0: continue
            sway = round(math.sin(sway_t * sway_speeds[i] + sway_phases[i]) * 2)
            bx = flower_positions[i] + sway
            max_stem = min(6 + int(commits * 2.5), 36)
            stemH = round(max_stem * grow_frac)
            stem_top = GY - stemH
            for s in range(stemH):
                sw = round(sway * (s / max(stemH, 1)))
                p(bx+sw, stem_top+s, C['stem'])
                p(bx+sw+1, stem_top+s, C['stem2'])
            if stemH > 10 and commits >= 3:
                ly = GY - int(stemH*0.42)
                blk(bx-5,ly,5,1,C['leaf2']); blk(bx-6,ly+1,5,1,C['leaf'])
                blk(bx-4,ly+2,3,1,C['leaf3'])
            if stemH > 14 and commits >= 5:
                ly2 = GY - int(stemH*0.65)
                blk(bx+2,ly2,5,1,C['leaf2']); blk(bx+3,ly2+1,5,1,C['leaf'])
                blk(bx+2,ly2+2,3,1,C['leaf3'])
            if grow_frac < 0.65: continue
            head_y = stem_top - 3
            if commits >= 9: flower_red(bx, head_y-8)
            elif commits >= 5: flower_orange(bx, head_y-6)
            else: flower_yellow(bx, head_y-4)

        # bottom bar
        blk(0, ROWS-6, COLS, 6, '#000000')

        # render to PIL — extra 28px at bottom for title
        img = Image.new('RGB', (W, H+28), (17,17,17))
        draw = ImageDraw.Draw(img)

        for r in range(ROWS):
            for c in range(COLS):
                color = buf[r][c]
                if color is None:
                    color = C['sky'][-1] if r < GY else C['g1']
                draw.rectangle(
                    [c*PX+1, r*PX+1, c*PX+PX-1, r*PX+PX-1],
                    fill=hex_to_rgb(color)
                )

        try:
            font_sm  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 10)
            font_lg  = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 14)
            font_leg = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 11)
        except:
            font_sm  = ImageFont.load_default()
            font_lg  = font_sm
            font_leg = font_sm

        # month labels — centered under each week group
        for i, week in enumerate(weeks):
            if week["label"]:
                x = flower_positions[i] * PX
                draw.text((x, H-PX*4+2), week["label"], fill=(144,202,249), font=font_sm)

        # title centered below pixel area
        title = "Raghav's Contribution Garden"
        bbox = draw.textbbox((0,0), title, font=font_lg)
        tw = bbox[2] - bbox[0]
        draw.text((W//2 - tw//2, H+6), title, fill=(255,224,102), font=font_lg)

        # legend top left
        draw.rectangle([6,6,238,34], fill=(0,0,0))
        draw.rectangle([6,6,238,34], outline=(255,224,102), width=1)
        draw.rectangle([18,13,30,25], fill=hex_to_rgb('#fdd835'))
        draw.text((34,14), "1-4 commits", fill=(255,255,255), font=font_leg)
        draw.rectangle([118,13,130,25], fill=hex_to_rgb('#ffa000'))
        draw.text((134,14), "5-8", fill=(255,255,255), font=font_leg)
        draw.rectangle([168,13,180,25], fill=hex_to_rgb('#e65100'))
        draw.text((184,14), "9+", fill=(255,255,255), font=font_leg)

        return img

    print("Generating GIF frames...")
    frames = []
    durations = []

    cloud_positions = [{'x': float(cl['x']), 'y': cl['y'],
                        'speed': cl['speed'], 'w': cl['w']} for cl in cloud_configs]

    # Phase 1: grow (play once)
    for f in range(GROW_FRAMES):
        grow_frac = (f+1) / GROW_FRAMES
        for cl in cloud_positions:
            cl['x'] += cl['speed']
            if cl['x'] > COLS + cl['w']: cl['x'] = -cl['w']
        frames.append(make_frame(cloud_positions, grow_frac, 0))
        durations.append(40)
        if f % 10 == 0: print(f"  Grow {f}/{GROW_FRAMES}")

    # Phase 2: loop (clouds + sway, flowers fully grown)
    for f in range(LOOP_FRAMES):
        sway_t = f * 3
        for cl in cloud_positions:
            cl['x'] += cl['speed']
            if cl['x'] > COLS + cl['w']: cl['x'] = -cl['w']
        frames.append(make_frame(cloud_positions, 1.0, sway_t))
        durations.append(80)
        if f % 10 == 0: print(f"  Loop {f}/{LOOP_FRAMES}")

    os.makedirs("dist", exist_ok=True)
    frames[0].save(
        "dist/garden.gif",
        save_all=True,
        append_images=frames[1:],
        optimize=False,
        duration=durations,
        loop=0
    )
    print("Done! dist/garden.gif generated.")

if __name__ == "__main__":
    print("Fetching contributions...")
    weeks = get_contributions()
    print(f"Got {len(weeks)} weeks (last 6 months)")
    generate_gif(weeks)
