# Deliverable 5 — Self-Audit

## 1. Row count per category against the section 2 floors

| # | Category | Rows | Floor | Result |
|---|---|---|---|---|
| 1 | Digital infra specialist fund managers (pure-play) | 13 | 20 | **Below floor by 7** |
| 2 | Mega-cap PE / infrastructure arms | 22 | 25 | **Below floor by 3** |
| 3 | Middle-market and LMM infrastructure / TMT PE and growth | 36 | 30 | Met |
| 4 | Private credit, infra debt, asset-backed and structured finance | 18 | 30 | **Below floor by 12** |
| 5 | Commercial and investment banks (arrangers, bookrunners, PF lenders) | 25 | 25 | Met |
| 6 | Investment banks and boutiques with named digital infra practices | 22 | 50 | **Below floor by 28** |
| 7 | Pensions, SWFs, insurers, family offices | 15 | 25 | **Below floor by 10** |
| 8 | Power and energy investors moving into compute | 21 | 30 | **Below floor by 9** |
| 9 | Real estate capital markets data center teams | 8 | 8 | Met |
| | **Total** | **180** | **243** | **Below by 63** |

### Why the shortfalls exist

The binding constraint was **evidence, not effort or output length**. The rule I applied throughout was
the brief's own: no institution enters the table without a verifiable source, and no field gets filled by
inference. Roughly 75 web searches and page fetches were run. Where a firm is obviously active but I
could not produce a citation in this pass, I either excluded it or entered it at grade C with the
uncertainty stated in the Notes column, rather than manufacture a plausible row.

Category-specific causes:

- **Category 6 (28 short)** is the largest gap and the most structural. Adviser identity is disclosed in
  only a minority of data center transactions. The Aligned Data Centers release named eight advisers at
  once and was worth more than a dozen searches; almost no other release in this dataset names any. This
  category is only completable from a paid adviser league table (Infralogic, Mergermarket, Dealogic).
- **Category 4 (12 short)** has the same problem in a different form: ABS and CMBS structuring agents and
  anchor investors are disclosed in **rating agency presale reports**, not in press releases. Those
  reports are paywalled.
- **Category 1 (7 short)** is partly a definitional choice. I applied a strict reading of "pure-play" and
  moved Northleaf, Igneo and CVC DIF into Category 2 as diversified infrastructure managers with digital
  teams. A looser reading would put Category 1 at 16. The remaining gap needs the SEC Form D sweep.
- **Category 7 (10 short)** — I deliberately excluded pensions whose only evidence was an infrastructure
  allocation ranking. Section 8 of the brief forbids inferring sector participation from being a large
  infrastructure investor, and OMERS, AIMCo, BCI, IMCO and the large US public plans fell into exactly
  that bucket.
- **Category 8 (9 short)** — behind-the-meter and powered-land deals are frequently announced by the
  developer with the financial backer unnamed.

## 2. Rows with no source URL

**Zero.** Verified programmatically across all 180 rows. Every row also has at least one non-empty
Example transactions or firm-page citation supporting the category assignment.

## 3. Rows I am least confident in, and what specifically is uncertain

All 24 C-rated rows carry the reason in their Notes column. The ones that most need checking before use:

| Row | What is uncertain |
|---|---|
| Evercore, Jefferies, Rothschild & Co (Cat 6) | Included on a credible secondary source describing them as active infrastructure advisers. **No named data center mandate was found.** They are almost certainly active; the citation does not prove it. |
| Athene, Global Atlantic (Cat 4) | Exposure inferred from the Apollo and KKR origination relationships and aggregate Schedule D data — **not from any named data center transaction.** |
| Oaktree (Pure), Elliott (Ark) (Cat 4) | Single secondary source describing a **process**, not a completed transaction. |
| CenterSquare, BlueMountain, PATRIZIA (Cat 7) | Named as prior Aligned investors in one secondary aggregation only. BlueMountain has since been folded into Assured Investment Management, so the current counterparty differs from the name shown. |
| Sandbrook Capital (Cat 8) | The "powered, ready-to-build land" description came from a **search-engine summary of the firm's site**, not from a confirmed Sandbrook release. Verify before any outreach. |
| Mizuho, Natixis, ING, Standard Chartered (Cat 5) | Their verified transaction (AdaniConneX) is **Indian, not US**. US data center lending is likely but unconfirmed here. |
| Columbia Capital (Cat 3) | The 2,069-acre Arizona parcel is reported in a secondary aggregation, not a primary release. |
| Fermi America (Cat 8) | ~USD 15bn valuation from a single secondary source. |
| Media Venture Partners, Waller Capital (Cat 6) | Sector coverage described; **no data center transaction confirmed**, and Waller's most recent visible deal predates 2019. May be dormant. |
| Nomura Greentech, Flow Partners, Union Square Advisors, Colliers (Cat 6/9) | Named practice or coverage area confirmed; no specific mandate isolated. |

## 4. Figures, deals and firm names I could not confirm

- **"USD 165bn financing for a megascale AI data center campus in New Mexico led by Blue Owl with STACK,
  leased to Oracle."** Milbank states this in its own award release and I have cited it, but I could not
  corroborate the magnitude anywhere else, and it is far larger than any comparable financing in this
  dataset. **Treat the number as unverified.** It is flagged in the transaction row itself.
- **"SoftBank acquires DigitalBridge" (2025).** Asserted in one secondary M&A review. It sits awkwardly
  against DigitalBridge's own 2026 acquisition of ArcLight. **I excluded it from both tables** rather
  than record a corporate-control change I could not confirm.
- **Apollo's acquisition of Stream Data Centers from Stream Realty, and of STACK's European colocation
  assets.** Both appear only in a secondary M&A review; no primary Apollo or Stream release was located.
  Recorded at grade B/C with the caveat in Notes.
- **Vantage Data Centers' USD 22-23bn Frontier loan.** The Bloomberg and The Information reports are
  paywalled; I could read the headlines and standfirsts but not the full articles. Sizes and roles are
  as reported in those headlines.
- **Sentinel Data Centers fund sizes.** An early search summary described a "USD 400m debut fund growing
  to USD 2.1bn for its fourth vehicle in 2024." A follow-up search could not reproduce this and
  suggested the summary had conflated Sentinel Data Centers (an operator, acquired by CyrusOne) with
  Sentinel Global (an unrelated enterprise-technology VC). **The claim was dropped entirely.**
- **"Beignet Investor" as the Meta/Blue Owl SPV name.** Appeared in one secondary source and could not be
  reproduced against the Meta or Blue Owl releases. **Dropped from the transaction row.**
- **Careers page URLs (column 20).** These are recorded as `Unknown / Not verified` on effectively every
  row. Guessing `firm.com/careers` would have been fabrication under section 14, and verifying 180 of
  them individually was not achievable in this pass. **This column needs a dedicated crawl.**
- **Column 19 (titles that own these deals)** is populated only where a named team structure was
  evidenced — J.P. Morgan, JLL, BGL, MetLife IM. Elsewhere it is `Unknown / Not verified` rather than a
  plausible-sounding guess.
- **Column 12 (transactions since Jan 2024)** counts **only transactions verified inside this dataset**.
  The header says so explicitly. For large institutions these numbers are floors, not true counts —
  Bank of America almost certainly did more than the one QTS syndicate role recorded.

## 5. Exclusions — institutions considered and left out

- **Law firms** (Milbank, Latham & Watkins, Kirkland & Ellis, Simpson Thacher, Skadden, Mayer Brown,
  Proskauer, Baker McKenzie, Linklaters, Sterlington, Orrick, Quinn Emanuel). Heavily used as *sources*,
  exactly as section 5 suggests, but they are not financial institutions and the brief's universe is
  financial institutions. Their deal-list pages are the highest-yield free source for extending this work.
- **Equipment and supply-chain corporates** (GE Vernova, Bloom Energy, Vertiv, Eaton, Trane, Daikin,
  Legrand, Supermicro, DPR Construction, Kiewit). Not financial institutions. Goldman Sachs Asset
  Management is included for the Boyd Thermal sale because GSAM is the financial sponsor.
- **Hyperscalers as buyers of compute** (Microsoft, Google, Amazon, Meta, Oracle). Named throughout the
  transaction table as counterparties, but they are not the buyside institutions this brief targets.
  NVIDIA and xAI likewise appear in transactions but not as institution rows.
- **Pure operators** (Equinix, Digital Realty as an operator, QTS, Aligned, Vantage, DataBank, STACK,
  Cologix, EdgeCore, Switch, TierPoint, Prime, Novva). They are the assets. Digital Realty appears once,
  narrowly, as a *fund manager* for its US Hyperscale Data Center Fund.
- **Large infrastructure investors with no evidenced sector transaction** — OMERS, AIMCo, BCI, IMCO,
  CalPERS, CalSTRS and peers. Excluded under section 8's prohibition on inference. They belong in the
  universe and will appear once a commitment-disclosure sweep is run.
- **Firms named only in SEO listicles.** Several "top data center investor" pages were read as a
  cross-check per section 1 and produced no name that was not already sourced elsewhere.

## 6. Method notes and honest limitations

- **Transaction-first was followed.** The transaction table was written before the institution table, and
  the institution rows were extracted from it. Roughly 60% of institution rows trace to a transaction row;
  the remainder cite firm pages, SEC filings or trade press directly, as section 7 permits.
- **The Form D / ERA sweep did not happen.** EDGAR full-text search was not reachable through the
  available tooling; keyword searches surfaced 10-K/10-Q/497 filings from large listed managers instead.
  This is the main reason Category 1 and the Hidden Gems section are thinner than they should be.
- **Two high-value sources failed to load:** Data Center Dynamics' 2025 M&A review returned HTTP 403, and
  Houlihan Lokey's Q4 2025 Digital Infrastructure Industry Update PDF would not parse. A BeBeez summary
  of the DCD piece was used instead, which is a secondary source of a secondary source — rows sourced
  solely to it are graded B or C accordingly.
- **No paid database was available.** Infralogic, PitchBook, Capital IQ, Mergermarket, Dealogic,
  IJGlobal, Preqin and Green Street are all named in section 5 as the highest-value sources. None were
  accessible. Every remaining floor gap traces back to this.

## 7. Saturation tests — results

Reported in full in `saturation_tests.md`. Summary: **platform saturation** substantially passed (21 of
the 21 named platforms plus 12 more were traced to at least one sponsor, lender or adviser);
**investor and financing saturation** passed for 2024–2026 and partially for 2018–2023;
**adviser saturation failed** — adviser identity is simply not disclosed on most transactions without a
paid league table; **transaction saturation** passed for the largest deals of 2024–2026 and failed for
2018–2021, where press releases are no longer reliably indexed by general web search.
