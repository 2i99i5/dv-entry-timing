# Methodology and data dictionary

[Русский перевод](METHODOLOGY.ru.md)

## Design

Exploratory retrospective description of CEAC `submitDate` and issuance in DV-2017–2026. The late-date pattern was noticed before formalizing this analysis; the two-date window is a post-hoc summary, not a preregistered hypothesis test. No causal effect or optimal entry date is estimated.

## Cleaning and outcomes

One row represents a case, potentially including family members. `caseNumberFull` must be unique per file. The 2017 input uses semicolons; others use commas. Mixed date formats are parsed; nonempty unparseable dates raise an error. Missing dates remain missing. Empty/`None` status rows are excluded from observed counts, not classified as refusals. Missing status in protected records does not establish that the case does not exist.

An issued case has numeric `Issued > 0`: at least one visa recorded as issued within that case. This does not prove issuance to the principal, all family members, or entry into the US. `principal_issued` separately counts `status == 'Issued'`, as in the earlier notebook; interpreting that source status as the principal's status is not independently audited. `visas` sums numeric `Issued`.

`submitDate` falls in expected entry-season ranges and is used as an **entry-date proxy**. Its formal source definition is not independently confirmed; it is not established as a DS-260 submission date. `statusDate` is not treated as a verified issuance date. No time-to-issuance is estimated.

## Alignment and measures

Start(y) = minimum valid `submitDate` among observed cases in all regions in year y. Relative day = (`submitDate` − start(y)).days + 1. EU uses the same all-region start. Calendar lengths are retained, not scaled to 0–100%.

Let N(y,d) = observed dated cases and I(y,d) = those with `Issued > 0`.

- Count: I(y,d).
- Observed dated-case issuance share: I(y,d) / N(y,d).
- Last-two-date concentration: sum of I for the maximum relative day and preceding calendar day / sum of I for all dates in the year.

The last two dates are **observed calendar dates**, not independently verified official deadlines. Timestamps/timezones are unavailable. A deadline can close partway through the final day; unequal daily exposure may explain a penultimate-day peak. No exposure adjustment is made.

Earlier 2024/2025 figures contain 95% binomial Wilson intervals for daily shares. They do not account for selection bias, missing dates, snapshot uncertainty or regional composition. No significance test or evidence of no timing effect is claimed. Multi-year publication figures omit these bands for readability.

## Missingness and limits

In 2024–2025 all NVC cases lack dates. Coverage is 44.05% and 43.30% of observed cases. Missingness depends on processing status: complete cases are not representative of all selectees. No date imputation is performed. Dark/protected cases are not refusals.

DV-2026 is an August 22 snapshot, with 4,453 dated / 66,003 observed cases (6.75%) and 14,643 Dark cases. It is excluded from the headline range and LinkedIn bar chart. Local capture dates of 2017–2023 are unknown; those snapshots are not independently verified as final. Pandemic-era processing and regional/consular composition differ; visual overlays do not adjust for these factors.

There are no unsuccessful entrants, all-entry daily denominators, full dates for all selectees, verified individual issuance histories, or adjustment-of-status outcomes. Neither P(selection | entry date), P(visa | entry date), nor P(visa | entry date, selected) for all selectees is identifiable. Reported distributions and rates are conditional on the accessible dated sample. Cases differ from individual visa recipients; family size changes person-weighted counts.

## Provenance and reproducibility

Publisher: [DV Charts](https://dvcharts.xarthisius.xyz/), collecting from [CEAC](https://ceac.state.gov/CEACStatTracker/Status.aspx). Dated archives: [public mirror](https://github.com/dvcharts/dvcharts.github.io). Upstream source terms continue to apply; this repository does not relicense upstream data.

`input/download_manifest.json` records URLs, snapshot dates, retrieval times, sizes and SHA-256 for 2024–2026: October 1, 2024; October 1, 2025; August 22, 2026. Server Last-Modified is not observation date.

`outputs/ceac_analysis/input_inventory.json` records hashes, separators and provenance of all local inputs. Exact capture dates/archive identities of legacy 2017–2023 files are unknown. Hashes identify the files used but do not make them publicly retrievable. Fresh downloads may differ. Raw case-level CSVs are not committed.

Two explicit reproduction levels:

1. **Published results:** committed aggregates reproduce English figures and last-two-date results using `prepare_publication.py`, without network or raw files.
2. **Raw reconstruction:** `analyze_ceac.py` rebuilds aggregates from local inputs. Exact reproduction requires matching hashes. Downloads for 2024–2026 are documented; exact legacy reconstruction requires obtaining matching files.

## Validation

Python `csv.DictReader` independently reconciles raw files against pandas aggregates: unique IDs, dated-case totals, issued-case totals, source-status Issued totals, numeric visa totals and relative-date totals. All ten local files passed; see `validation_all_years.csv`. Unit tests cover mixed family outcomes, missing dates, alternate separators and malformed dates. Figures are inspected visually. These checks establish computational consistency, not source completeness or accuracy.

## Output dictionary

| File / field | Meaning |
|---|---|
| `coverage.csv` | Row, observed and dated counts; coverage; issuance totals; Dark counts; date bounds |
| `date_coverage_by_status.csv` | Dates available by status and year |
| `daily_all.csv` | Year/date aggregates |
| `daily_by_region.csv` | Year/region/date aggregates |
| `relative_daily_all.csv` | Aggregates aligned by relative day |
| `last_two_days.csv` | Two-date concentration, counts, peak day, 2026 partial flag |
| `cases` | Observed cases with valid dates |
| `issued_cases` | Cases with `Issued > 0` |
| `principal_issued` | Rows with status Issued |
| `visas` | Sum of numeric Issued |
| `share` | issued_cases / cases |
| `wilson_low`, `wilson_high` | Nominal 95% binomial Wilson bounds |
| `environment.json` | Versions used in recorded validation |

Supported: “late dates account for a substantial minority of observed issued cases.” Unsupported: “most recipients applied late,” “late entry improves odds,” or “entry date has no effect.” A larger numerator does not establish a higher rate without its denominator.
