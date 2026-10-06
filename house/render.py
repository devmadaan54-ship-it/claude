#!/usr/bin/env python3
"""Render house models into HTML plans (one SVG per floor).

Usage:  python3 house/render.py                  -> model.yaml -> plan.html,
                                                    design_*.yaml -> design_*.html
        python3 house/render.py FILE.yaml ...    -> just those files
        python3 house/render.py ... --png DIR    -> also writes DIR/<stem>_<floor>.svg

A design file is a patch on another model:
    base: model.yaml          # model it starts from (may itself be a patch)
    remove: [ids]             # rooms, walls, openings, stairs, fixtures, zones...
    modify: {id: {field: value}}
    add_openings: {wall_id: [openings]}
    add: {floor: {rooms: [], walls: [], stairs: [], fixtures: []}}
    floor_notes: {floor: text}
    changes: [{what, why, structure}]  # change log shown on the page
Anything added is tagged status: new and drawn in teal.

All geometry is in feet; the SVG viewBox is in feet too, so 1 SVG unit = 1 ft.
"""
import copy
import html
import math
import pathlib
import sys

import yaml

HERE = pathlib.Path(__file__).resolve().parent
PATCH_KEYS = {"base", "remove", "modify", "add", "add_openings", "floor_notes"}
LISTS = ("rooms", "walls", "stairs", "fixtures", "annotations")

# Same view box for every floor so they line up when you flip between tabs.
VIEW = (-9.0, -4.0, 94.0, 54.0)  # x, y, w, h (feet)

FLOOR_ORDER = ["basement", "ground", "first", "terrace"]
GHOST_OF = {"basement": "ground", "ground": "basement", "first": "ground", "terrace": "first"}


def _items(model):
    """Yield (list, item) for every id-bearing element in the model."""
    for fl in model["floors"].values():
        for key in LISTS:
            for it in fl.get(key, []):
                yield fl[key], it
                for o in it.get("openings", []) if key == "walls" else []:
                    yield it["openings"], o
        site = fl.get("site") or {}
        for key in ("zones", "boundary_walls"):
            for it in site.get(key, []):
                yield site[key], it
                for o in it.get("openings", []):
                    yield it["openings"], o


def find(model, id_):
    for lst, it in _items(model):
        if it.get("id") == id_:
            return lst, it
    raise SystemExit(f"patch error: no element with id {id_!r}")


def load_model(path):
    data = yaml.safe_load(pathlib.Path(path).read_text())
    if "base" not in data:
        return data
    model = copy.deepcopy(load_model(pathlib.Path(path).parent / data["base"]))
    model["base_model"] = copy.deepcopy(model)
    for k, v in data.items():
        if k in PATCH_KEYS:
            continue
        if k == "meta":
            model.setdefault("meta", {}).update(v)
        else:
            model[k] = v
    for id_ in data.get("remove", []):
        lst, it = find(model, id_)
        lst.remove(it)
    for id_, fields in (data.get("modify") or {}).items():
        find(model, id_)[1].update(fields)
    for wall_id, ops in (data.get("add_openings") or {}).items():
        wall = find(model, wall_id)[1]
        for o in ops:
            o.setdefault("status", "new")
        wall.setdefault("openings", []).extend(ops)
    for floor, groups in (data.get("add") or {}).items():
        fl = model["floors"][floor]
        for key, items in groups.items():
            for it in items:
                it.setdefault("status", "new")
            fl.setdefault(key, []).extend(items)
    for floor, note in (data.get("floor_notes") or {}).items():
        model["floors"][floor]["note"] = note
    seen = set()
    for _, it in _items(model):
        if it.get("id") in seen:
            raise SystemExit(f"patch error: duplicate id {it['id']!r}")
        seen.add(it.get("id"))
    return model


def ftin(v):
    """16.5 -> 16'-6\""""
    total = round(abs(v) * 12)
    return f"{'-' if v < 0 else ''}{total // 12}'-{total % 12}\""


def esc(s):
    return html.escape(str(s), quote=True)


def rect(b, cls, extra=""):
    x1, y1, x2, y2 = b
    return (f'<rect class="{cls}" x="{x1:.2f}" y="{y1:.2f}" '
            f'width="{x2 - x1:.2f}" height="{y2 - y1:.2f}" {extra}/>')


def text(x, y, s, cls, size=0.85, anchor="middle"):
    return (f'<text class="{cls}" x="{x:.2f}" y="{y:.2f}" font-size="{size}" '
            f'text-anchor="{anchor}">{esc(s)}</text>')


def fit(s, size, width):
    """Shrink font size so text of len(s) fits in width (rough serif metric)."""
    need = len(str(s)) * size * 0.58
    return size if need <= width * 0.92 else max(0.3, size * width * 0.92 / need)


def horizontal(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) >= (y2 - y1)


def opening_box(wall_box, span):
    x1, y1, x2, y2 = wall_box
    a, b = span
    if horizontal(wall_box):
        return [a, y1, b, y2]
    return [x1, a, x2, b]


def door_svg(wall_box, span, opens, double=False):
    """Leaf line + quarter arc. Hinge at span start (and end for double)."""
    x1, y1, x2, y2 = wall_box
    a, b = span
    out = []
    leaves = [(a, b)] if not double else [(a, (a + b) / 2), (b, (a + b) / 2)]
    for hinge, tip in leaves:
        L = abs(tip - hinge)
        if horizontal(wall_box):
            if opens == "up":
                fy, d = y1, -1
            else:
                fy, d = y2, 1
            hx, hy = hinge, fy
            lx, ly = hinge, fy + d * L
            ax, ay = tip, fy
        else:
            if opens == "left":
                fx, d = x1, -1
            else:
                fx, d = x2, 1
            hx, hy = fx, hinge
            lx, ly = fx + d * L, hinge
            ax, ay = fx, tip
        if not opens:
            out.append(f'<line class="door-leaf" x1="{hx:.2f}" y1="{hy:.2f}" '
                       f'x2="{ax:.2f}" y2="{ay:.2f}" stroke-dasharray="0.3 0.3"/>')
            continue
        # sweep flag: pick the arc that bulges away from the wall
        cross = (lx - hx) * (ay - hy) - (ly - hy) * (ax - hx)
        sweep = 1 if cross < 0 else 0
        out.append(f'<line class="door-leaf" x1="{hx:.2f}" y1="{hy:.2f}" x2="{lx:.2f}" y2="{ly:.2f}"/>')
        out.append(f'<path class="door-arc" d="M {lx:.2f} {ly:.2f} A {L:.2f} {L:.2f} 0 0 {sweep} '
                   f'{ax:.2f} {ay:.2f}"/>')
    return "".join(out)


def window_svg(ob, kind):
    x1, y1, x2, y2 = ob
    cls = {"window": "win", "ventilator": "vent", "glazed": "glaze", "gate": "gate"}.get(kind, "win")
    out = [rect(ob, "cut")]
    if kind == "opening":
        return out[0]
    if horizontal(ob):
        n = 3 if kind == "window" else 1
        for i in range(n):
            y = y1 + (y2 - y1) * (i + 1) / (n + 1)
            out.append(f'<line class="{cls}" x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}"/>')
    else:
        n = 3 if kind == "window" else 1
        for i in range(n):
            x = x1 + (x2 - x1) * (i + 1) / (n + 1)
            out.append(f'<line class="{cls}" x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}"/>')
    return "".join(out)


def stair_svg(s):
    if s.get("type") == "spiral":
        cx, cy = s["center"]
        r = s["radius"]
        out = [f'<circle class="stair" cx="{cx}" cy="{cy}" r="{r}"/>']
        for k in range(8):
            t = k * math.pi / 4
            out.append(f'<line class="tread" x1="{cx}" y1="{cy}" x2="{cx + r * math.cos(t):.2f}" '
                       f'y2="{cy + r * math.sin(t):.2f}"/>')
        out.append(text(cx, cy + r + 1.0, "spiral stair", "small"))
        return "".join(out)
    if isinstance(s.get("flights"), list):
        return flights_svg(s)
    x1, y1, x2, y2 = s["box"]
    out = [rect(s["box"], "stair")]
    x = x1
    while x < x2 - 0.01:
        out.append(f'<line class="tread" x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}"/>')
        x += 0.9
    mid = (y1 + y2) / 2
    out.append(rect([x1, mid - 1.4, x2, mid + 1.4], "landing"))
    for i, part in enumerate(str(s.get("label", "")).split(" / ")):
        out.append(text((x1 + x2) / 2, mid - 0.2 + i * 1.0, part, "small"))
    return "".join(out)


VEC = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


def treads_svg(box, rise, tread, cls="tread"):
    x1, y1, x2, y2 = box
    out = []
    if rise in ("up", "down"):
        n = int(round((y2 - y1) / tread))
        for i in range(1, n):
            y = y1 + i * (y2 - y1) / n
            out.append(f'<line class="{cls}" x1="{x1:.2f}" y1="{y:.2f}" x2="{x2:.2f}" y2="{y:.2f}"/>')
    else:
        n = int(round((x2 - x1) / tread))
        for i in range(1, n):
            x = x1 + i * (x2 - x1) / n
            out.append(f'<line class="{cls}" x1="{x:.2f}" y1="{y1:.2f}" x2="{x:.2f}" y2="{y2:.2f}"/>')
    return "".join(out)


def arrow_svg(box, rise):
    x1, y1, x2, y2 = box
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = VEC[rise]
    hl = (abs(dx) * (x2 - x1) + abs(dy) * (y2 - y1)) / 2 - 0.3
    sx, sy, ex, ey = cx - dx * hl, cy - dy * hl, cx + dx * hl, cy + dy * hl
    px, py = -dy, dx
    head = (f"{ex:.2f},{ey:.2f} {ex - dx * .6 + px * .35:.2f},{ey - dy * .6 + py * .35:.2f} "
            f"{ex - dx * .6 - px * .35:.2f},{ey - dy * .6 - py * .35:.2f}")
    return (f'<line class="arrow" x1="{sx:.2f}" y1="{sy:.2f}" x2="{ex:.2f}" y2="{ey:.2f}"/>'
            f'<polygon class="arrowhead" points="{head}"/>')


def flights_svg(s):
    out = []
    for lb in s.get("landings", []):
        out.append(rect(lb, "landing"))
    for f in s["flights"]:
        out.append(rect(f["box"], "stair"))
        out.append(treads_svg(f["box"], f["rise"], f.get("tread", 0.833)))
        out.append(arrow_svg(f["box"], f["rise"]))
    if s.get("label"):
        lx, ly = s.get("label_pos") or [(s["box"][0] + s["box"][2]) / 2, s["box"][1] + 1.0]
        for i, part in enumerate(str(s["label"]).split(" / ")):
            out.append(text(lx, ly + i * 0.75, part, "small"))
    return "".join(out)


FIXTURE_LABEL = {"wc": "WC", "basin": "basin", "sink": "sink", "hob": "hob", "tub": "TUB",
                 "shower": "sh", "wardrobe": "wardrobe", "cupboard": "C.B.", "counter": "",
                 "fridge": "fridge", "washer": "WM"}


def fixture_svg(f):
    t = f["type"]
    if t == "round_column":
        cx, cy = f["center"]
        return f'<circle class="col" cx="{cx}" cy="{cy}" r="{f.get("radius", 0.5)}"/>'
    b = f["box"]
    x1, y1, x2, y2 = b
    if t == "column":
        return rect(b, "col")
    if t == "beam":
        return rect(b, "beam")
    if t == "lattice":
        return rect(b, "lattice")
    if t == "pergola":
        out = rect(b, "pergola")
        if f.get("label"):
            out += text((x1 + x2) / 2, (y1 + y2) / 2 + 0.4, f["label"], "pergola-label", 1.2)
        return out
    if t == "counter":
        return rect(b, "counter")
    if t == "lift":
        return (rect(b, "lift") + f'<line class="liftx" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>'
                f'<line class="liftx" x1="{x1}" y1="{y2}" x2="{x2}" y2="{y1}"/>'
                + text((x1 + x2) / 2, (y1 + y2) / 2 + 0.35, f.get("label", "LIFT"), "liftlabel",
                       fit(f.get("label", "LIFT"), 0.9, x2 - x1)))
    if t == "steps":
        return (rect(b, "steps") + treads_svg(b, f["rise"], f.get("tread", 1.0), "steptread")
                + arrow_svg(b, f["rise"]))
    out = rect(b, "fix", 'rx="0.25"')
    lab = f.get("label", FIXTURE_LABEL.get(t, t))
    if lab:
        w, h = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if h > 2 * w:
            sz = fit(lab, 0.6, h)
            out += (f'<text class="fixlabel" font-size="{sz:.2f}" text-anchor="middle" '
                    f'transform="translate({cx + sz * 0.35:.2f},{cy:.2f}) rotate(-90)">{esc(lab)}</text>')
        else:
            sz = fit(lab, 0.6, w)
            out += text(cx, cy + sz * 0.35, lab, "fixlabel", sz)
    return out


def walls_svg(floor, cls="wall"):
    out = []
    for w in floor.get("walls", []):
        wcls = cls
        if cls == "wall":
            wcls += f' {w["kind"]}' if w.get("kind") else ""
            wcls += " new" if w.get("status") == "new" else ""
        out.append(rect(w["box"], wcls))
    return out


def render_floor(key, floor, model):
    g = []
    site = floor.get("site")
    if site:
        g.append(rect(site["plot"]["box"], "plot"))
        for z in site.get("zones", []):
            zc = "lawn" if "lawn" in z["id"] else "zone"
            g.append(rect(z["box"], zc))
            x1, y1, x2, y2 = z["box"]
            lab = z["name"] + (f'  FFL {z["ffl"]}' if z.get("ffl") else "")
            if "side_strip" in z["id"]:
                g.append(f'<text class="zonelabel" font-size="0.9" text-anchor="middle" '
                         f'transform="translate({(x1 + x2) / 2:.2f},{(y1 + y2) / 2:.2f}) rotate(-90)">{esc(lab)}</text>')
            else:
                g.append(text((x1 + x2) / 2, (y1 + y2) / 2, lab, "zonelabel", 1.0))
        for bw in site.get("boundary_walls", []):
            g.append(rect(bw["box"], "bwall"))
            for o in bw.get("openings", []):
                ob = opening_box(bw["box"], o["span"])
                g.append(rect(ob, "cut"))
                g.append(f'<line class="gate" x1="{ob[0]:.2f}" y1="{(ob[1] + ob[3]) / 2:.2f}" '
                         f'x2="{ob[2]:.2f}" y2="{(ob[1] + ob[3]) / 2:.2f}"/>')
                g.append(text((ob[0] + ob[2]) / 2, ob[1] - 0.4, "GATE", "small"))
    if floor.get("roof_outline"):
        g.append(rect(floor["roof_outline"]["box"], "roof"))

    # ghost of the reference floor (toggle)
    if model.get("base_model"):
        ref = model["base_model"]["floors"].get(key, {})
    else:
        ref = model["floors"].get(GHOST_OF.get(key), {})
    if ref:
        g.append('<g class="ghost">' + "".join(walls_svg(ref, "ghostwall")) + "</g>")

    for r in floor.get("rooms", []):
        kind = r.get("kind", "indoor")
        g.append(rect(r["box"], f"room {kind}"))
    for f in floor.get("fixtures", []):
        if f["type"] in ("beam", "lattice", "pergola"):
            g.append(fixture_svg(f))
    for s in floor.get("stairs", []):
        g.append(stair_svg(s))
    for f in floor.get("fixtures", []):
        if f["type"] not in ("beam", "lattice", "pergola", "cupboard"):
            g.append(fixture_svg(f))

    g.extend(walls_svg(floor))
    for f in floor.get("fixtures", []):
        if f["type"] == "cupboard":
            g.append(fixture_svg(f))
    ids = []
    for w in floor.get("walls", []):
        x1, y1, x2, y2 = w["box"]
        ids.append(text((x1 + x2) / 2, (y1 + y2) / 2 + 0.2, w["id"].split(".", 1)[1], "idlabel", 0.45))
        for o in w.get("openings", []):
            ob = opening_box(w["box"], o["span"])
            t = o["type"]
            if t in ("door", "double_door"):
                g.append(rect(ob, "cut"))
                g.append(door_svg(w["box"], o["span"], o.get("opens"), double=(t == "double_door")))
            elif t == "lift_door":
                g.append(rect(ob, "cut") + rect(ob, "liftdoor"))
            else:
                g.append(window_svg(ob, t))
            ids.append(text((ob[0] + ob[2]) / 2, (ob[1] + ob[3]) / 2 - 0.5, o["id"].split(".", 1)[1],
                            "idlabel oid", 0.45))

    # room labels on top
    for r in floor.get("rooms", []):
        x1, y1, x2, y2 = r["box"]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        if r["id"] == "gf.drawing":
            cy = y1 + (y2 - y1) * 0.42
        if r.get("label_pos"):
            cx, cy = r["label_pos"]
        lines = [(r["name"].upper(), "rname", 1.0)]
        if r.get("label"):
            lines.append((r["label"], "rdim", 0.75))
        if r.get("ceiling"):
            lines.append((f'ceiling {r["ceiling"]}', "rdim", 0.65))
        if r.get("ffl"):
            lines.append((f'FFL {r["ffl"]}', "rdim", 0.65))
        if r["name"] in ("Stair", "Stair Room"):
            lines = lines[1:]  # the stair symbol carries its own label
            cy = y2 - 1.0
        width = (x2 - x1) if not r.get("label_pos") else 2 * min(cx - x1, x2 - cx)
        sizes = [fit(s, sz, width) for s, _, sz in lines]
        k = min([sz / l[2] for sz, l in zip(sizes, lines)] or [1])
        top = cy - (len(lines) - 1) * 0.55 * k
        for i, (s, c, sz) in enumerate(lines):
            g.append(text(cx, top + i * 1.1 * k + 0.3 * k, s, c, sz * k))
        ids.append(text(cx, y2 - 0.4, r["id"].split(".", 1)[1], "idlabel", 0.45))

    for a in floor.get("annotations", []):
        if a["type"] == "freehand":
            pts = " ".join(f"{x},{y}" for x, y in a["points"])
            g.append(f'<polyline class="anno anno-{a["color"]}" points="{pts}"/>')
        elif a["type"] == "highlight":
            g.append(rect(a["box"], f'anno-hl anno-hl-{a["color"]}'))

    g.append('<g class="ids">' + "".join(ids) + "</g>")
    return "".join(g)


def grid_svg():
    x, y, w, h = VIEW
    out = ['<g class="grid">']
    for gx in range(math.ceil(x), int(x + w) + 1):
        major = gx % 5 == 0
        out.append(f'<line class="{"gmaj" if major else "gmin"}" x1="{gx}" y1="{y}" x2="{gx}" y2="{y + h}"/>')
        if major:
            out.append(text(gx, y + 1.2, gx, "glabel", 0.8))
    for gy in range(math.ceil(y), int(y + h) + 1):
        major = gy % 5 == 0
        out.append(f'<line class="{"gmaj" if major else "gmin"}" x1="{x}" y1="{gy}" x2="{x + w}" y2="{gy}"/>')
        if major:
            out.append(text(x + 0.3, gy - 0.2, gy, "glabel", 0.8, "start"))
    out.append("</g>")
    return "".join(out)


def vastu_cell(v, x, y):
    gx1, gy1, gx2, gy2 = v["grid_box"]
    col = min(2, max(0, int((x - gx1) / ((gx2 - gx1) / 3))))
    row = min(2, max(0, int((y - gy1) / ((gy2 - gy1) / 3))))
    return v["cells"][row][col]


def vastu_svg(v):
    gx1, gy1, gx2, gy2 = v["grid_box"]
    cw, ch = (gx2 - gx1) / 3, (gy2 - gy1) / 3
    out = ['<g class="vastu">', rect([gx1 + cw, gy1 + ch, gx1 + 2 * cw, gy1 + 2 * ch], "vcentre")]
    for i in range(4):
        out.append(f'<line class="vline" x1="{gx1 + i * cw:.2f}" y1="{gy1}" x2="{gx1 + i * cw:.2f}" y2="{gy2}"/>')
        out.append(f'<line class="vline" x1="{gx1}" y1="{gy1 + i * ch:.2f}" x2="{gx2}" y2="{gy1 + i * ch:.2f}"/>')
    for r in range(3):
        for c in range(3):
            out.append(text(gx1 + c * cw + 0.5, gy1 + r * ch + 1.7, v["cells"][r][c], "vlabel", 1.5, "start"))
    out.append("</g>")
    return "".join(out)


def centre_of(b):
    return (b[0] + b[2]) / 2, (b[1] + b[3]) / 2


def vastu_rows(floor, v):
    """What sits in which zone: WCs, cooking, stairs, lift, entrances."""
    rows = []
    what = {"wc": "WC", "hob": "Cooking (hob)", "lift": "Lift"}
    for f in floor.get("fixtures", []):
        if f["type"] in what:
            cx, cy = centre_of(f["box"])
            rows.append((what[f["type"]], f["id"], vastu_cell(v, cx, cy)))
    for st in floor.get("stairs", []):
        if st.get("center"):
            cx, cy = st["center"]
        else:
            cx, cy = centre_of(st["box"])
        rows.append(("Stair", st["id"], vastu_cell(v, cx, cy)))
    for w in floor.get("walls", []):
        for o in w.get("openings", []):
            if o.get("entrance"):
                cx, cy = centre_of(opening_box(w["box"], o["span"]))
                rows.append(("Entrance door", o["id"], vastu_cell(v, cx, cy)))
    out = []
    for kind, id_, zone in rows:
        avoid = v.get("avoid", {}).get(kind, [])
        flag = ' class="bad"' if zone in avoid else ""
        out.append(f"<tr{flag}><td>{esc(kind)}</td><td><code>{esc(id_)}</code></td><td>{esc(zone)}</td>"
                   f"<td>{'avoid' if zone in avoid else 'ok'}</td></tr>")
    return "".join(out)


def compass_svg():
    # drawing up = East (approx), right = South, down = West, left = North
    cx, cy = 80.5, 36.0
    return (f'<g class="compass"><circle cx="{cx}" cy="{cy}" r="2.6"/>'
            + text(cx, cy - 3.0, "E", "cmp", 1.1) + text(cx + 3.6, cy + 0.4, "S", "cmp", 1.1)
            + text(cx, cy + 4.0, "W", "cmp", 1.1) + text(cx - 3.6, cy + 0.4, "N", "cmp", 1.1)
            + f'<line x1="{cx}" y1="{cy + 2.2}" x2="{cx}" y2="{cy - 2.2}"/>'
            + f'<line x1="{cx - 2.2}" y1="{cy}" x2="{cx + 2.2}" y2="{cy}"/></g>')


CSS = """
:root{--bg:#f6f4ef;--paper:#ffffff;--ink:#1f2328;--muted:#6b6f76;--wall:#3b3f45;--accent:#2f6fde}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#16181c;--paper:#f3f1ec;--ink:#e8e6e1;--muted:#a3a7ae}}
:root[data-theme="dark"]{--bg:#16181c;--paper:#f3f1ec;--ink:#e8e6e1;--muted:#a3a7ae}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
header{padding:14px 16px 6px}
h1{font-size:18px;margin:0 0 2px}
.sub{color:var(--muted);font-size:12.5px}
.bar{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;padding:8px 16px}
.tabs button{border:1px solid #9994;background:transparent;color:var(--ink);padding:5px 11px;border-radius:7px;cursor:pointer;font:inherit}
.tabs button.on{background:var(--accent);border-color:var(--accent);color:#fff}
label{font-size:13px;color:var(--muted);user-select:none}
.sheet{padding:0 16px 10px}
.sheet h2{font-size:15px;margin:10px 0 2px}
.sheet p{margin:0 0 6px;color:var(--muted);font-size:12.5px;max-width:900px}
svg{width:100%;height:auto;background:var(--paper);border-radius:10px;display:block}
.hidden{display:none}
.plot{fill:none;stroke:#7a8;stroke-width:.12;stroke-dasharray:.6 .3}
.zone{fill:#ece9e2}.lawn{fill:#dcebd3}
.zonelabel{fill:#7b766c;font-family:Georgia,serif}
.bwall{fill:#9a948a}
.roof{fill:#efece6;stroke:#9a948a;stroke-width:.12}
.room.indoor{fill:#fbfaf7}.room.outdoor_covered{fill:#eef3f7}.room.outdoor{fill:#f2f6ee}
.room{stroke:none}
.wall{fill:var(--wall)}.wall.partition{fill:#8a7f55}.wall.parapet{fill:#7d828a}
.ghostwall{fill:#d9822b;opacity:.28}
.ghost{display:none}.show-ghost .ghost{display:inline}
.cut{fill:#fbfaf7}
.win{stroke:#2f6fde;stroke-width:.07}.vent{stroke:#2f6fde;stroke-width:.09;stroke-dasharray:.25 .2}
.glaze{stroke:#6aa0e8;stroke-width:.12}.gate{stroke:#a0522d;stroke-width:.18}
.door-leaf{stroke:#8b5a2b;stroke-width:.09}.door-arc{fill:none;stroke:#8b5a2b;stroke-width:.05;stroke-dasharray:.25 .15}
.stair{fill:#fde9ef;stroke:#d63a75;stroke-width:.06}.tread{stroke:#d63a75;stroke-width:.04}
.landing{fill:#fde9ef;stroke:#d63a75;stroke-width:.04}
.col{fill:#555a60}.beam{fill:none;stroke:#5cb85c;stroke-width:.07;stroke-dasharray:.4 .25}
.lattice{fill:#e3f3dc;stroke:#69b85a;stroke-width:.06;stroke-dasharray:.3 .2}
.pergola{fill:#e8f5e2;stroke:#69b85a;stroke-width:.08;stroke-dasharray:.5 .25}
.pergola-label{fill:#c03aa0;font-weight:600}
.counter{fill:none;stroke:#c9a46a;stroke-width:.05}
.fix{fill:#fff7e8;stroke:#c9a46a;stroke-width:.05}.fixlabel{fill:#9b7a43}
.rname{fill:#1f2328;font-family:Georgia,serif;font-weight:600;letter-spacing:.02em}
.rdim{fill:#4d5157;font-family:Georgia,serif}
.small{fill:#a3305e;font-size:.6px}
.idlabel{fill:#c0392b;font-family:ui-monospace,Menlo,monospace;display:none}
.show-ids .idlabel{display:inline}
.anno{fill:none;stroke-width:.35;stroke-linejoin:round}.anno-green{stroke:#2e7d32}
.anno-hl-yellow{fill:#ffd54a;opacity:.45}
.grid{display:none}.show-grid .grid{display:inline}
.gmin{stroke:#6aa0e8;stroke-width:.02;opacity:.35}.gmaj{stroke:#e5534b;stroke-width:.04;opacity:.45}
.glabel{fill:#e5534b}
.compass circle{fill:none;stroke:#c0392b;stroke-width:.12}.compass line{stroke:#c0392b;stroke-width:.06}
.cmp{fill:#c0392b;font-weight:700}
footer{padding:4px 16px 24px;color:var(--muted);font-size:12px}
.wall.new{fill:#16857a}.wall.railing{fill:#b9a77a}
.lift{fill:#eef1f6;stroke:#55606e;stroke-width:.08}.liftx{stroke:#55606e;stroke-width:.05}
.liftlabel{fill:#55606e;font-weight:700}.liftdoor{fill:#55606e;opacity:.35}
.steps{fill:#f4efe6;stroke:#a08a62;stroke-width:.06}.steptread{stroke:#a08a62;stroke-width:.04}
.arrow{stroke:#a3305e;stroke-width:.06}.arrowhead{fill:#a3305e}
.vastu{display:none}.show-vastu .vastu{display:inline}
.vline{stroke:#7b4fc9;stroke-width:.12;stroke-dasharray:.8 .4}
.vcentre{fill:#7b4fc9;opacity:.07}.vlabel{fill:#7b4fc9;opacity:.75;font-weight:700}
details.log{margin:4px 16px 8px;max-width:1000px;background:#fff8;border:1px solid #9993;border-radius:10px;padding:8px 12px}
details.log summary{cursor:pointer;font-weight:600}
.log ol{margin:6px 0 2px;padding-left:20px}.log li{margin:0 0 7px;font-size:13px}
.log .why,.log .str{display:block;color:var(--muted);font-size:12.5px}
.log .str::before{content:"Structure: ";font-weight:600}
.log .why::before{content:"Why: ";font-weight:600}
table.vt{border-collapse:collapse;margin:8px 0 4px;font-size:12.5px}
table.vt td,table.vt th{border-bottom:1px solid #9993;padding:3px 10px 3px 0;text-align:left}
table.vt tr.bad td{color:#c0392b;font-weight:600}
"""

JS = """
const tabs=document.querySelectorAll('.tabs button');
function show(k){tabs.forEach(b=>b.classList.toggle('on',b.dataset.k===k));
 document.querySelectorAll('.sheet').forEach(s=>s.classList.toggle('hidden',k!=='all'&&s.dataset.k!==k));
 try{localStorage.setItem('floor',k)}catch(e){}}
tabs.forEach(b=>b.onclick=()=>show(b.dataset.k));
for(const id of ['grid','ids','ghost','vastu']){const c=document.getElementById(id);if(!c)continue;
 const f=()=>document.body.classList.toggle('show-'+id,c.checked);c.onchange=f;f();}
let k='ground';try{k=localStorage.getItem('floor')||'ground'}catch(e){}show(k);
"""


def svg_floor(key, fl, model, standalone=False):
    x, y, w, h = VIEW
    v = model.get("vastu")
    body = render_floor(key, fl, model) + (vastu_svg(v) if v else "")
    if standalone:
        return (f'<svg viewBox="{x} {y} {w} {h}" xmlns="http://www.w3.org/2000/svg" width="1740" '
                f'height="{int(1740 * h / w)}"><style>{CSS}</style><rect x="{x}" y="{y}" width="{w}" '
                f'height="{h}" fill="#fff"/><g class="show-vastu">' + body + "</g>" + compass_svg()
                + text(x + 1, y + h - 1.2, fl["title"].upper(), "rname", 1.6, "start") + "</svg>")
    return (f'<svg viewBox="{x} {y} {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="{esc(fl["title"])} plan">' + body + grid_svg() + compass_svg()
            + text(x + 1, y + h - 1.2, fl["title"].upper(), "rname", 1.6, "start") + "</svg>")


def changes_html(model):
    ch = model.get("changes")
    if not ch:
        return ""
    items = []
    for c in ch:
        items.append(f'<li>{esc(c["what"])}'
                     + (f'<span class="why">{esc(c["why"])}</span>' if c.get("why") else "")
                     + (f'<span class="str">{esc(c["structure"])}</span>' if c.get("structure") else "")
                     + "</li>")
    return f'<details class="log"><summary>Changes in this version ({len(ch)})</summary><ol>{"".join(items)}</ol></details>'


def render_file(src, png_dir=None):
    src = pathlib.Path(src)
    model = load_model(src)
    floors = model["floors"]
    out = HERE / ("plan.html" if src.stem == "model" else f"{src.stem}.html")
    v = model.get("vastu")
    sheets, buttons = [], []
    for key in FLOOR_ORDER:
        if key not in floors:
            continue
        fl = floors[key]
        buttons.append(f'<button data-k="{key}">{esc(fl["title"])}</button>')
        table = ""
        if v:
            rows = vastu_rows(fl, v)
            if rows:
                table = ('<table class="vt"><tr><th>Item</th><th>id</th><th>Vastu zone</th><th></th></tr>'
                         f"{rows}</table>")
        sheets.append(f'<section class="sheet" data-k="{key}"><h2>{esc(fl["title"])}</h2>'
                      f'<p>{esc(fl.get("note", ""))}</p>{svg_floor(key, fl, model)}{table}</section>')
    buttons.append('<button data-k="all">All floors</button>')
    meta = model["meta"]
    ghost_label = "existing walls (before)" if model.get("base_model") else "ghost of floor below/above"
    title = model.get("title", meta["name"])
    vastu_box = ('<label><input type="checkbox" id="vastu" checked> Vastu 3x3 grid</label>' if v else "")
    vnote = f'<div class="sub">{esc(v["note"])}</div>' if v and v.get("note") else ""
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><style>{CSS}</style></head><body>
<header><h1>{esc(title)}</h1>
<div class="sub">{esc(meta['name'])}, {esc(meta['location'])}. Generated from house/{esc(src.name)}.
Units in feet; origin = top-left outer corner of the ground floor walls. Drawing up = East, right = South.
New walls are teal.</div>{vnote}</header>
{changes_html(model)}
<div class="bar"><span class="tabs">{''.join(buttons)}</span>
{vastu_box}
<label><input type="checkbox" id="grid"> 1 ft grid</label>
<label><input type="checkbox" id="ids"> element ids</label>
<label><input type="checkbox" id="ghost"> {ghost_label}</label></div>
{''.join(sheets)}
<footer>Source: {esc(meta['source'])} ({esc(meta['drawn_by'])}, {esc(meta['drawing_date'])}).</footer>
<script>{JS}</script></body></html>"""
    out.write_text(page)
    print(f"wrote {out}")
    if png_dir:
        d = pathlib.Path(png_dir)
        d.mkdir(parents=True, exist_ok=True)
        for key in FLOOR_ORDER:
            if key in floors:
                (d / f"{src.stem}_{key}.svg").write_text(svg_floor(key, floors[key], model, standalone=True))


def main():
    args = sys.argv[1:]
    png = None
    if "--png" in args:
        i = args.index("--png")
        png = args[i + 1]
        del args[i:i + 2]
    files = args or [HERE / "model.yaml"] + sorted(HERE.glob("design_*.yaml"))
    for f in files:
        render_file(f, png)


if __name__ == "__main__":
    main()
