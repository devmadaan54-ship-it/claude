import json, re

res = json.load(open("raw.json"))

STRONG = re.compile(r"\b(campus|university|new\s?grad|graduate\s+(program|analyst|scheme)|"
                    r"summer\s+analyst|analyst\s+program|rotational|early\s+career|"
                    r"class\s+of\s+20\d\d|20(26|27|28)\s+analyst|analyst\s+20(26|27|28)|"
                    r"intern(ship)?\b|entry[- ]level|undergrad)", re.I)
SENIOR = re.compile(r"\b(senior|sr\.?|vp|vice\s+president|principal|director|head\s+of|managing|"
                    r"lead\b|manager|md\b|executive|chief|partner\b|counsel|controller)", re.I)
ANALYST = re.compile(r"\banalyst\b", re.I)

rows = []
for r in res:
    for j in r["jobs"]:
        t = j.get("title") or ""
        blob = t + " " + (j.get("desc") or "")
        s = bool(STRONG.search(t))
        sd = bool(STRONG.search(blob))
        if s or (ANALYST.search(t) and not SENIOR.search(t)) or sd:
            rows.append({"firm": r["firm"], "ats": r["ats"], "title": t,
                         "loc": j.get("loc") or "", "url": j.get("url") or "",
                         "updated": str(j.get("updated") or "")[:10],
                         "tier": "TITLE-HIT" if s else ("ANALYST" if ANALYST.search(t) else "desc-only"),
                         "why": ",".join(sorted({m.group(0).lower() for m in STRONG.finditer(blob)}))[:120]})

rows.sort(key=lambda x: (x["tier"] != "TITLE-HIT", x["firm"]))
json.dump(rows, open("candidates.json", "w"), indent=1)
print(f"{len(rows)} candidate rows\n")
for x in rows:
    print(f"[{x['tier']:<9}] {x['firm'][:34]:<34} | {x['title'][:60]:<60} | {x['loc'][:26]:<26} | {x['updated']}")
    if x["tier"] == "desc-only":
        print(f"{'':13}   ^ signals: {x['why']}")
