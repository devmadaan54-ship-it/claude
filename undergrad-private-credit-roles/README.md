# Private Credit — Open Roles for Undergrads Graduating 2027

Live scan run **2026-08-14**. 26 reachable job boards, **908 open postings** pulled directly from
ATS APIs (Workday CXS, Greenhouse, Ashby, Lever, BambooHR, SmartRecruiters), then filtered on
graduation-eligibility and years-of-experience language taken from the **full job descriptions**,
not titles.

## Headline finding

**No firm on this list currently has an open, explicitly-labeled campus / analyst-program posting
for the class of 2027.**

The campus machinery running right now targets the **class of 2028**. Verified examples:

- Ares "2027 Summer Intern" — requires graduation **Dec 2027 – Aug 2028**; applications closed March 2026, posting no longer live.
- KKR "2027 Summer Analyst Program" — converts to **2028** full-time offers.
- Putnam / Franklin Templeton "Equity Associate Intern" — eligible grads **Fall 2027 – Spring 2029**.

A 2027 graduate did their junior-summer internship in Summer 2026, and most 2027 full-time analyst
seats are being filled by return offers from that class. So the live opportunities for them are
**direct-entry analyst roles and class-based programs**, not campus pipelines.

## Tier A — genuinely open to a 2027 grad (verified 0–2 yrs / no experience required)

| Firm | Role | Location | Eligibility evidence |
|---|---|---|---|
| **Franklin Templeton** | Internal Sales Associate — **June 2027 Class** | St. Petersburg, FL (+1) | Class-based training program starting June 2027; SIE/Series 7/63 obtained on the job. Best structural fit for a May 2027 grad. |
| **Franklin Templeton** | Internal Sales Associate — **January 2027 Class** | 3 locations | Same program, earlier cohort. |
| **Ares Management** | Analyst, Credit Technology | New York, NY | "**0-2 years** of software engineering experience"; BS Computer Science required. |
| **Ares Management** | Analyst, Real Estate Acquisitions (Self Storage) | Redondo Beach, CA | "**0-2 years** relevant experience"; Bachelor's in Real Estate/Finance/Accounting. |
| **ORIX USA** | Equity Underwriting, Analyst | Boston, MA | "**0-2 years** of related experience"; Bachelor's in business or finance preferred. |
| **Moelis & Company** | Analyst, IB — Private Capital Advisory (GP-Led Secondaries) | New York, NY | "Bachelor's degree required; prior internship or full-time experience ... **preferred**" — not required. |
| **Moelis & Company** | Analyst, IB — Private Capital Advisory (LP-Led Secondaries) | New York, NY | Same language. |

> Caution on Moelis: most of its other IB Analyst postings explicitly say "seeking an **experienced**
> Analyst." Only the two Private Capital Advisory roles leave the door open. All Moelis applications
> require a completed **Suited assessment**.

## Tier B — realistic stretch (1–3 yrs stated, often flexible for a strong grad)

| Firm | Role | Location |
|---|---|---|
| Blue Owl Capital | Analyst/Associate — Net Lease Real Assets (1–4 yrs) | Chicago, IL |
| Blue Owl Capital | Product Management & Investor Relations, Real Assets — Analyst (1–4 yrs) | New York, NY / Chicago, IL |
| Sixth Street | Asset Based Finance Analyst | New York, NY |
| Sixth Street | BDC Accounting Analyst | Boston, MA |
| Star Mountain Capital | Directs Investment Analyst | Tampa, FL |
| Star Mountain Capital | Portfolio Management Analyst | Tampa, FL |
| Star Mountain Capital | Portfolio Monitoring Analyst/Associate | Tampa, FL |
| Star Mountain Capital | Analyst/Associate, Financial Analytics | Tampa, FL |
| Redding Ridge Asset Management | Analyst/Associate, Corporate Credit (Credit Estimates) | New York, NY |
| Specialty Capital | Credit Analyst | Great Neck, NY |
| MonticelloAM | Business Analyst / CRE Financial Analyst | New York, NY / Richmond, VA |
| Prospect Administration | Investment Professional | New York, NY |
| Eagle Point Credit Management | Distressed Loan Analyst | Greenwich, CT |

## Tier C — open, but for the class of 2028+ (not this target)

- Ares — 2027 Summer Intern (grads Dec 2027–Aug 2028)
- KKR — 2027 Summer Analyst Program (→ 2028 full-time)
- Putnam / Franklin Templeton — Equity Associate Intern, Summer 2027 (grads Fall 2027–Spring 2029)
- Putnam / Franklin Templeton — Equity Externship, **Jan 5–7 2027**, 3 days, sophomores & juniors — historically a funnel into the summer internship
- VWH Capital — Quantitative Researcher Intern, Dallas, TX

## Explicitly NOT undergrad (despite year-labeled titles)

- **Oaktree** — "Associate, US Senior Loans, **2026**" (Los Angeles): requires "2-3 years as an analyst with a top investment bank." Year in the title is the class start, not a grad year.
- **BlackRock** — "**2027** GIP Infrastructure Private Equity Investment Associate": associate class, pre-requires banking experience.

---

# Data-quality problems in the source table

**14 of the ATS slugs point at a completely different company.** Anything downstream of these is
noise, not signal:

| Table entry | Slug resolves to |
|---|---|
| White Oak Global Advisors | `greenhouse:whiteoak` → **White Oak Veterinary Clinic** (vet externships) |
| Percent / Cadence Group | `workday:cadence.wd1` → **Cadence Design Systems** (semiconductors, 300 postings) |
| Community Investment Management | `greenhouse:community` → Rome Community Partners |
| Panagram Services | `greenhouse:psl` → "Pearson Spectre Litt" |
| Park Square Capital USA | `workday:park.wd1/ParkUniversityCareers` → **Park University** |
| Antares Capital LP | `ashby:antares` → LA thermal/fluids engineering firm |
| Silver Rock Capital Partners | `ashby:silver` → Silver.dev (Argentina dev recruiting) |
| Phoenix Merchant Partners | `ashby:phoenix` → Canadian pharmacy chain |
| Arena Investors | `ashby:arena` → Bay Area tech recruiting |
| Black Diamond Capital Mgmt | `recruitee:blackdiamond` → sales/recruiting internships, Andover MA |
| Metropolitan Partners Group | `pinpoint:mmgapts` → Metropolitan Companies (apartments, PA) |
| Runway Growth Capital | `ashby:runway` → Runway (AI/ML company) |
| FIG LLC / Fortress | `ashby:fig` → a single "Test job" in SF |
| Hercules Capital | `ashby:hercules` → unrelated SF/remote tech company |

**Corrections to boards the table had wrong or dark:**

- Ares → `aresmgmt.wd1.myworkdayjobs.com/External` (277 open) — table had no board.
- Golub Capital → `golubcapital.wd5.myworkdayjobs.com/golub_capital_careers` exists publicly, but the
  Workday CXS API returns HTTP 422 for every site-name variant tried. Needs manual resolution.
- KKR → `boards.greenhouse.io/kkr` is **404**; KKR has moved off Greenhouse. Student roles now live at
  `kkr.com/careers/student-careers`.
- HPS Investment Partners → now inside **BlackRock**; roles flow through `blackrock.wd1/BlackRock_Professional`.
- Angelo Gordon → now part of **TPG**.
- Oak Hill, Bayview, Marathon → iCIMS boards are JS-rendered; no titles extractable from static HTML.
  Need a headless browser (Chromium + Playwright are preinstalled in this environment).

## Reproducing

```bash
cd scripts
python3 fetch.py      # pull every verified board -> raw.json
python3 validate.py   # confirm each board belongs to the firm it claims
python3 filter.py     # title-level undergrad screen -> candidates.json
python3 enrich.py     # fetch full JDs, extract grad-year/experience -> gradhits.json
```

`firms.py` holds the verified board list and an `IMPOSTORS` map documenting every slug that
resolved to the wrong company.
