# U.S. Data Center Finance Universe

A transaction-first map of U.S.-based financial institutions and investment teams with evidenced
activity in data center, digital infrastructure, AI infrastructure and power-for-compute transactions.

Built January 2018 – present, weighted to 2024–2026.

## Contents

| File | Deliverable | Rows |
|---|---|---|
| `institutions.csv` | **D1 — Master institution table** (23 columns, one row per institution) | 180 |
| `transactions.csv` | **D2 — Transaction table** (the provenance layer beneath D1) | 63 |
| `hidden_gems.md` | **D3 — Hidden gems** | 40 |
| `executive_summary.md` | **D4 — Executive summary** | — |
| `self_audit.md` | **D5 — Self-audit** | — |
| `saturation_tests.md` | Section 10 saturation tests, reported individually | 5 tests |

## Headline result

180 institutions against a floor of 243. **Zero rows without a source URL.** Evidence mix A 105 / B 51 /
C 24. Four of nine category floors met (3, 5, 9 met; 1, 2, 4, 6, 7, 8 short).

`self_audit.md` states exactly which floors were missed, by how much, and why. The short version: the
binding constraint was evidence, not effort. No paid transaction database (Infralogic, PitchBook,
Capital IQ, Mergermarket, Dealogic, IJGlobal, Preqin, Green Street) was reachable, and adviser identity
is undisclosed in most data center transaction releases. Category 6 is 28 rows short for that reason
alone. Nothing was invented to close a gap.

## How to read the tables

- **Unverified fields read `Unknown / Not verified`.** They are not blanks and they are not guesses.
- **Column 12** (`Number of relevant transactions since Jan 2024`) counts only transactions verified
  *inside this dataset*. For large institutions these are floors, not true market counts.
- **Column 20** (careers page URL) is `Unknown / Not verified` on effectively every row. Guessing
  `firm.com/careers` would have been fabrication; verifying 180 of them needs a dedicated crawl.
- **Column 21** is the evidence grade: **A** primary-source transaction evidence, **B** multiple credible
  secondary sources, **C** indirect or limited. All 24 C-rated rows state the specific uncertainty in
  their Notes column.
- **Column 23** (Notes) carries the deduplication and caveat information. Read it before outreach.
- Multiple source URLs in a cell are separated by ` | `.

## Deduplication

Where a house transacts through several separately branded teams, those teams are separate rows, because
they are separate counterparties. The main cases:

- **Citizens** — three rows: Citizens (bank lending), Citizens Digital Infrastructure / DH Capital
  (middle-market advisory, acquired 2021, brand retained), Citizens JMP Securities.
- **Blue Owl** — two rows: Blue Owl Digital Infrastructure (the former IPI Partners team, acquired Jan
  2025) and Blue Owl Capital's credit and financing activity.
- **Ares** — two rows: infrastructure equity, and credit / infrastructure debt.
- **Macquarie** — two rows: Macquarie Asset Management and Macquarie Capital.
- **BlackRock and GIP** — both listed; GIP retains its brand and remains the named counterparty on deals.
- **Starwood** — two rows: Starwood Capital Group (equity/development) and Starwood Property Trust
  (lending).
- **Mubadala** — three rows: Mubadala Investment Company, Mubadala Capital, and MGX (a separate Abu Dhabi
  vehicle).
- **Absorbed brands noted with current owner:** IPI Partners → Blue Owl; DH Capital → Citizens;
  Peppertree → TPG; CVC DIF (formerly DIF Capital Partners); Energy Capital Partners → Bridgepoint;
  ArcLight → DigitalBridge (announced); BlueMountain → Assured Investment Management.

## Scope decisions

**Included:** fund managers, banks, credit funds, advisers, LPs, and the power investors and powered-land
platforms that section 2 category 8 explicitly puts in scope — plus a small number of developer-side
platforms (Tract, PowerBridge, Chirisa, PowerHouse, LandBridge) that function as capital counterparties.
Each is flagged as such in Notes.

**Excluded, with reasons in `self_audit.md` §5:** law firms (used heavily as *sources*, but not financial
institutions); equipment and supply-chain corporates; hyperscalers as buyers of compute; pure operators
(they are the assets); and large infrastructure investors with no evidenced sector transaction — section 8
of the brief forbids inferring participation from size.

**Not compiled, per section 14:** individual people's names, contact details, educational history or
personal profiles. Column 19 carries role titles only, and only where a team structure was evidenced.

## Extending this

`executive_summary.md` ends with a gap-to-source table. The four highest-value next inputs, in order:

1. An **Infralogic / Mergermarket / Dealogic financial adviser league table** filtered to data centers,
   2018–present. This alone would close most of Category 6.
2. **KBRA / Moody's / S&P data center ABS and CMBS presale reports** — they name every structuring agent
   and anchor investor, which closes most of Category 4.
3. **SEC Form D full-text search and the IAPD Exempt Reporting Adviser database** on "digital
   infrastructure" and "data center" fund names — closes Category 1 and extends the hidden gems.
4. **Law firm deal-list pages** (Milbank, Latham, Kirkland, Simpson Thacher, Skadden, Mayer Brown,
   Gibson Dunn). Free, and they name counterparties that appear in no ranking — the Milbank pages alone
   produced four transactions in this pass.
