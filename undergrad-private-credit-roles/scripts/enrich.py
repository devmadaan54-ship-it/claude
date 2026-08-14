import json, re, html, urllib.request, concurrent.futures as cf
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
res = json.load(open("raw.json"))

US = re.compile(r"\b(NY|New York|CA|Los Angeles|San Francisco|Chicago|IL|Boston|MA|Dallas|TX|Denver|CO|"
                r"Tampa|FL|Miami|Greenwich|CT|NJ|Norfolk|VA|Atlanta|GA|Redondo|Culver|Wilmington|DE|"
                r"Princeton|United States|USA|Remote|2 Locations|3 Locations)\b", re.I)
WANT = re.compile(r"\b(analyst|intern|associate|graduate|campus|rotational|new\s?grad|trainee)\b", re.I)
SENIOR = re.compile(r"\b(senior|sr\.?|vice president|vp\b|principal|director|head of|managing|chief|"
                    r"executive|counsel|controller|architect|manager)\b", re.I)

def strip(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(h or ""))).strip()

def wd_desc(url):
    m = re.match(r"https://([^.]+)\.(wd\d+)\.myworkdayjobs\.com/([^/]+)(/.*)", url)
    if not m: return ""
    t, wd, site, path = m.groups()
    api = f"https://{t}.{wd}.myworkdayjobs.com/wday/cxs/{t}/{site}{path}"
    try:
        d = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers=UA), timeout=25).read())
        info = d.get("jobPostingInfo", {})
        return strip(info.get("jobDescription", "")) + " || startDate=" + str(info.get("startDate", ""))
    except Exception as e:
        return f"ERR {type(e).__name__}"

targets = []
for r in res:
    for j in r["jobs"]:
        t = j.get("title") or ""
        if not WANT.search(t) or SENIOR.search(t): continue
        if not US.search((j.get("loc") or "") + " " + t): continue
        targets.append((r["firm"], t, j.get("loc") or "", j.get("url") or "", j.get("desc") or ""))

print(f"{len(targets)} US entry-level-ish postings to enrich")

def fill(x):
    firm, t, loc, url, desc = x
    if not desc and "myworkdayjobs.com" in url:
        desc = wd_desc(url)
    return {"firm": firm, "title": t, "loc": loc, "url": url, "desc": desc}

with cf.ThreadPoolExecutor(10) as ex:
    out = list(ex.map(fill, targets))
json.dump(out, open("enriched.json", "w"), indent=1)

GRAD = re.compile(r"(class of 20\d\d|graduat\w*[^.]{0,80}?20\d\d|20\d\d[^.]{0,40}?graduat\w*|"
                  r"(?:expected|anticipated)\s+graduation[^.]{0,60}|"
                  r"currently enrolled[^.]{0,80}|rising (?:senior|junior)|"
                  r"pursuing (?:a )?(?:bachelor|undergraduate)[^.]{0,60}|"
                  r"undergraduate (?:student|degree)[^.]{0,50}|"
                  r"\b0[-–\s]?(?:to)?[-–\s]?2 years|no prior (?:work )?experience|recent graduate)", re.I)

hits = []
for o in out:
    ms = {m.group(0).strip()[:120] for m in GRAD.finditer(o["desc"] or "")}
    if ms:
        hits.append({**o, "signals": sorted(ms)})
json.dump(hits, open("gradhits.json", "w"), indent=1)
print(f"\n{len(hits)} postings with undergrad/graduation-eligibility language:\n")
for h in hits:
    print(f"### {h['firm']} — {h['title']}  [{h['loc']}]")
    print(f"    {h['url'][:120]}")
    for s in h["signals"][:6]:
        print(f"      * {s}")
