# Section 10 — Saturation Tests

Each test is reported with its result, what it surfaced late, and what it would take to pass fully.

---

## Test 1 — Transaction saturation

*For the largest US data center transactions in each year from 2018 to present, confirm every named
investor, adviser and lender has been evaluated for inclusion.*

**Result: PASSED for 2024–2026. FAILED for 2018–2021. PARTIAL for 2022–2023.**

| Year | Largest transactions captured | Every named party evaluated? |
|---|---|---|
| 2026 | Ares/Vantage USD 2.4bn; KKR+Oak Hill/GTR; Igneo/Vault; DataBank Red Oak USD 2.0bn; Vistra/Meta PPAs; I Squared platform | Yes |
| 2025 | Aligned USD 40bn; Meta Hyperion USD 30bn; Vantage Frontier USD 22bn+; QTS CMBS USD 2.05bn; Switch ABS; Crusoe Series E; Applied Digital; Novva USD 2.0bn; Cologix ABS; DartPoints; PowerBridge; Homer City | Yes |
| 2024 | Vantage USD 9.2bn; CoreWeave USD 7.5bn; AirTrunk USD 16bn; Cologix USD 1.5bn; Intersect Power | Yes |
| 2023 | Compass USD 5.5bn; Cologix recap (2021); CoreWeave USD 2.3bn | Partial — Compass advisers never located |
| 2022 | Switch USD 11bn take-private; CyrusOne close; DataGryd | **No** — no adviser or lender named in any accessible source |
| 2021 | CyrusOne USD 15bn; DataSite/American Tower; Prime/Macquarie Capital; Cologix USD 3bn recap; DC BLOX | **No** — advisers not disclosed in accessible sources |
| 2018–2020 | DRFortress; Atlantic Metro/365; SDC Fund I | **No** — coverage is sparse; 2018–2020 releases are largely de-indexed |

**Found late in the process and added:** the eight sell-side advisers on Aligned (Guggenheim Securities
lead, plus Wells Fargo, TD Securities, Deutsche Bank, Goldman Sachs, J.P. Morgan, Citizens JMP and BofA)
— found in the final research batch, from Macquarie's own release rather than any of the deal coverage.
This single find added more Category 6 evidence than the previous ten searches combined, and is the
clearest illustration of why this test fails without league-table access.

**To pass fully:** Dealogic or Capital IQ transaction screens for 2018–2023. General web search no longer
reliably reaches press releases from that period.

---

## Test 2 — Platform saturation

*For each major US data center operator or platform, identify its financial sponsors, lenders and
advisers.*

**Result: PASSED for 21 of the 21 named platforms plus 12 additional platforms found.**

| Platform | Sponsors / lenders / advisers identified |
|---|---|
| QTS | Blackstone (owner); Goldman Sachs (CMBS lead) + BofA, BMO, Barclays, Citi, Morgan Stanley, RBC, Scotiabank, Wells Fargo |
| CyrusOne | KKR; Global Infrastructure Partners |
| Aligned | Macquarie AM (seller); AIP, MGX, GIP (buyers); Microsoft, NVIDIA, xAI, Temasek, KIA; prior: Mubadala, PATRIZIA, CenterSquare, BlueMountain; Guggenheim + 7 advisers |
| Vantage | DigitalBridge, Silver Lake, GIC, ADIA, CPP, PSP, AustralianSuper; Ares (USD 2.4bn); J.P. Morgan + MUFG; MUFG + SocGen; Barclays, Deutsche Bank, SocGen (euro ABS) |
| EdgeConneX | EQT |
| CoreSite | American Tower |
| Switch | DigitalBridge + IFM (take-private); Citi, Barclays, Goldman, RBC, Wells Fargo, Morgan Stanley, TD, Truist (ABS/CMBS) |
| DataBank | MUFG (lead); Citizens, PNC, TD Securities, Truist, CoBank, Deutsche Bank, SocGen |
| Stream | Stream Realty (former parent); Apollo (reported buyer) |
| TierPoint | Argo Infrastructure Partners |
| DartPoints | NOVA Infrastructure, Orion Infrastructure Capital, Astra Capital Management |
| STACK | Blue Owl (New Mexico campus); Apollo (European colo, reported); Guggenheim (adviser) |
| Compass | Brookfield Infrastructure, Ontario Teachers'; RedBird, Azrieli (sellers) |
| Prime | Macquarie Capital; Grain Management (preferred equity into Data Realty Holding) |
| Flexential | Identified as an ABS issuer; **sponsor not confirmed in this pass** |
| Cologix | Stonepeak; Madison International Realty |
| Novva | CIM Group; J.P. Morgan, Starwood Property Trust |
| Edged | **Not traced** |
| Crusoe | Valor Equity Partners, Mubadala Capital + ~28 named co-investors |
| CoreWeave | Blackstone, Magnetar, Coatue, Carlyle, CDPQ, DigitalBridge Credit, BlackRock, Eldridge, Great Elm; Goldman (adviser) |
| Applied Digital | Macquarie AM (up to USD 5bn); SMBC (USD 375m); Lake Street (adviser) |

**Additional platforms found and traced:** EdgeCore (Partners Group; MUFG), Global Technical Realty
(KKR, Oak Hill), Montera (Stonepeak), OpCore (InfraVia; Lazard, RBC, Perella Weinberg), Vault Digital
Infrastructure (CVC DIF, Northleaf → Igneo), atNorth (CPP, Partners Group), DC BLOX (Post Road),
DRFortress (GI Partners), Hudson InterXchange/DataGryd (Cordiant), Fleet Data Centers (Tract Capital),
BlackChamber Group (JLL-arranged financing), Texas Critical Data Centers (New Era Energy & Digital).

**Gaps:** Flexential's and Edged's sponsors were not confirmed.

---

## Test 3 — Adviser saturation

*Identify advisers appearing in 2+ transactions. None may be omitted.*

**Result: FAILED.**

Only **one** pure adviser reached 2+ verified data center transactions in this dataset —
**Guggenheim Securities** (Aligned sell-side lead; Apollo/STACK buy-side). Newmark reached 3 on the real
estate capital markets side. Every other adviser is at exactly one verified mandate, and most large
advisory firms have zero because **adviser identity is not disclosed in the majority of data center
transaction releases**.

This is not a search-effort failure — it is a disclosure failure in the source material. Of the 63
transactions in the table, only 11 name a financial adviser at all.

**To pass:** an Infralogic, Mergermarket or Dealogic **financial adviser league table** filtered to data
centers / digital infrastructure, 2018–present. This is the single highest-value missing input in the
entire project, and it is what holds Category 6 at 22 rows against a floor of 50.

---

## Test 4 — Investor saturation

*Identify sponsors appearing in 2+ transactions. None may be omitted.*

**Result: PASSED.**

**45 institutions** carry 2 or more verified transactions since Jan 2024 and all are in the table. The
recurring sponsors, in descending order:

- **4 transactions:** MUFG, CPP Investments, NextEra Energy Resources
- **3:** DigitalBridge, Blue Owl Digital Infrastructure, Grain Management, Blackstone, BlackRock,
  Macquarie Asset Management, Blue Owl Capital (credit), Goldman Sachs, Morgan Stanley, Wells Fargo,
  Barclays, RBC Capital Markets, TD Securities, Société Générale, PowerBridge, Newmark
- **2:** Post Road Group, Chirisa, PowerHouse Data Centers, Brookfield, Stonepeak, Silver Lake, Apollo
  (equity and credit), TPG, InfraVia, Five Point Infrastructure, SMBC, J.P. Morgan, Citigroup, Truist,
  Citizens, Deutsche Bank, Guggenheim Securities, PSP Investments, Kuwait Investment Authority, ArcLight,
  Energy Capital Partners, Constellation, Talen, NRG, LandBridge

Note the caveat from the self-audit: these counts are **verified-in-this-dataset floors**, not true
market counts.

---

## Test 5 — Financing saturation

*Identify recurring banks, credit funds, project finance lenders and infrastructure debt investors.*

**Result: PASSED for banks. PARTIAL for credit funds and infrastructure debt.**

**Recurring banks (all captured):** MUFG (4), SMBC, J.P. Morgan, Goldman Sachs, Morgan Stanley,
Wells Fargo, Citigroup, Barclays, RBC, TD Securities, Truist, Société Générale, Deutsche Bank, Citizens,
BofA, BMO, Scotiabank, PNC, CoBank, First Citizens, Macquarie Capital.

**Recurring credit funds (captured):** Blue Owl, PIMCO, Ares, Blackstone, Magnetar, Coatue, Apollo,
DigitalBridge Credit, Starwood Property Trust, Carlyle, CDPQ, BlackRock, Eldridge, Great Elm, Post Road.

**Partial — what is missing:** the ABS and CMBS structuring agents and anchor buyers on the ~42 rated
data center ABS issuances (USD 16.2bn through Q1 2025 per S&P) beyond the Switch, QTS, Cologix, DataBank
and Compass transactions captured here. Also missing: infrastructure debt fund managers whose data center
exposure sits inside diversified portfolios and is never announced deal-by-deal — MetLife IM is the only
one captured, and only because it publishes about it.

**To pass fully:** KBRA, Moody's and S&P **data center ABS/CMBS presale reports**, which name every
structuring agent, and Preqin or Infralogic infrastructure-debt fund screens.
