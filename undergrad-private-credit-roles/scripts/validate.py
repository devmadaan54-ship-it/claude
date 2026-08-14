import json, urllib.request, concurrent.futures as cf
from collections import Counter
res = json.load(open("raw.json"))
UA = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

def name_of(r):
    """Ask the ATS who owns this board."""
    try:
        if r["ats"] == "greenhouse":
            u = f"https://boards-api.greenhouse.io/v1/boards/{r['slug']}"
            return json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=20).read()).get("name", "?")
        if r["ats"] == "ashby":
            u = f"https://api.ashbyhq.com/posting-api/job-board/{r['slug']}"
            d = json.loads(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=20).read())
            j = (d.get("jobs") or [{}])[0]
            return (j.get("jobUrl") or "").split("/jobs")[0] or "?"
    except Exception as e:
        return f"ERR {type(e).__name__}"
    return "-"

live = [r for r in res if r["n"] > 0]
with cf.ThreadPoolExecutor(10) as ex:
    names = list(ex.map(name_of, live))

for r, nm in zip(live, names):
    locs = Counter((j.get("loc") or "?").split(",")[0].strip() for j in r["jobs"])
    top = "; ".join(f"{k}({v})" for k, v in locs.most_common(4))
    print(f"{r['firm'][:36]:<36} [{r['ats']}:{r['slug'][:26]:<26}] board={nm[:38]:<38}")
    print(f"{'':38} n={r['n']:<4} locs: {top[:96]}")
    print(f"{'':38} ex: {(r['jobs'][0].get('title') or '')[:80]}")
