import json, re, sys, urllib.request, urllib.error, concurrent.futures as cf
from firms import FIRMS

UA = {"User-Agent": "Mozilla/5.0 (compatible; job-research/1.0)", "Accept": "application/json"}

def get(url, data=None, timeout=30):
    req = urllib.request.Request(url, headers=dict(UA))
    if data is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(data).encode()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def strip(h):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", h or "")).strip()

def greenhouse(slug):
    d = json.loads(get(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"))
    return [{"title": j.get("title"), "loc": (j.get("location") or {}).get("name"),
             "url": j.get("absolute_url"), "updated": j.get("updated_at"),
             "desc": strip(__import__("html").unescape(j.get("content", "")))[:4000]}
            for j in d.get("jobs", [])]

def ashby(slug):
    d = json.loads(get(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=false"))
    return [{"title": j.get("title"), "loc": j.get("location"), "url": j.get("jobUrl"),
             "updated": j.get("publishedAt"), "desc": strip(j.get("descriptionHtml", ""))[:4000]}
            for j in d.get("jobs", [])]

def lever(slug):
    d = json.loads(get(f"https://api.lever.co/v0/postings/{slug}?mode=json"))
    return [{"title": j.get("text"), "loc": (j.get("categories") or {}).get("location"),
             "url": j.get("hostedUrl"), "updated": j.get("createdAt"),
             "desc": strip(j.get("descriptionPlain", ""))[:4000]} for j in d]

def smartrecruiters(slug):
    d = json.loads(get(f"https://api.smartrecruiters.com/v1/companies/{slug}/postings?limit=100"))
    out = []
    for j in d.get("content", []):
        loc = j.get("location") or {}
        out.append({"title": j.get("name"), "loc": f"{loc.get('city','')}, {loc.get('region','')}",
                    "url": f"https://jobs.smartrecruiters.com/{slug}/{j.get('id')}",
                    "updated": j.get("releasedDate"), "desc": ""})
    return out

def bamboohr(slug):
    d = json.loads(get(f"https://{slug}.bamboohr.com/careers/list"))
    out = []
    for j in d.get("result", []):
        loc = j.get("location") or {}
        out.append({"title": j.get("jobOpeningName"),
                    "loc": f"{loc.get('city','')}, {loc.get('state','')}",
                    "url": f"https://{slug}.bamboohr.com/careers/{j.get('id')}",
                    "updated": j.get("originalOpenDate"), "desc": ""})
    return out

def recruitee(slug):
    d = json.loads(get(f"https://{slug}.recruitee.com/api/offers/"))
    return [{"title": j.get("title"), "loc": j.get("location"), "url": j.get("careers_url"),
             "updated": j.get("published_at"), "desc": strip(j.get("description", ""))[:4000]}
            for j in d.get("offers", [])]

def pinpoint(slug):
    d = json.loads(get(f"https://{slug}.pinpointhq.com/postings.json"))
    return [{"title": j.get("title"), "loc": (j.get("location") or {}).get("name"),
             "url": j.get("url"), "updated": j.get("published_at"), "desc": ""}
            for j in d.get("data", [])]

def workday(slug):
    tenant_wd, site = slug.split("/", 1)
    tenant, wd = tenant_wd.split(".", 1)
    url = f"https://{tenant}.{wd}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    out, offset = [], 0
    while offset < 300:
        d = json.loads(get(url, {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""}))
        posts = d.get("jobPostings", [])
        if not posts:
            break
        for j in posts:
            out.append({"title": j.get("title"), "loc": j.get("locationsText"),
                        "url": f"https://{tenant}.{wd}.myworkdayjobs.com/{site}{j.get('externalPath','')}",
                        "updated": j.get("postedOn"), "desc": ""})
        if len(posts) < 20:
            break
        offset += 20
    return out

def icims(slug):
    html = get(f"https://{slug}.icims.com/jobs/search?ss=1&searchRelation=keyword_all&in_iframe=1")
    titles = re.findall(r'class="title"[^>]*>\s*(?:<[^>]+>\s*)*([^<]{4,120})', html)
    return [{"title": t.strip(), "loc": "", "url": f"https://{slug}.icims.com/jobs/search",
             "updated": "", "desc": ""} for t in titles]

HANDLERS = dict(greenhouse=greenhouse, ashby=ashby, lever=lever, smartrecruiters=smartrecruiters,
                bamboohr=bamboohr, recruitee=recruitee, pinpoint=pinpoint, workday=workday, icims=icims)

def run(f):
    name, ats, slug = f
    try:
        jobs = HANDLERS[ats](slug)
        return {"firm": name, "ats": ats, "slug": slug, "ok": True, "n": len(jobs), "jobs": jobs}
    except Exception as e:
        return {"firm": name, "ats": ats, "slug": slug, "ok": False, "n": 0,
                "err": f"{type(e).__name__}: {e}", "jobs": []}

if __name__ == "__main__":
    with cf.ThreadPoolExecutor(12) as ex:
        res = list(ex.map(run, FIRMS))
    json.dump(res, open("raw.json", "w"), indent=1)
    for r in sorted(res, key=lambda x: -x["n"]):
        print(f"{r['n']:>4}  {'OK ' if r['ok'] else 'ERR'}  {r['firm'][:44]:<44} {r['ats']}"
              + ("" if r["ok"] else f"  <- {r.get('err','')[:70]}"))
