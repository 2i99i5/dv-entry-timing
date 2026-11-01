"""Descriptive CEAC analysis. Never estimates odds among all lottery entrants."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "ceac_analysis"


def load(year):
    path = ROOT / "input" / f"FY{year}-ceac-current.csv"
    with path.open(encoding="utf-8-sig") as stream:
        delimiter = ";" if ";" in stream.readline() else ","
    d = pd.read_csv(path, sep=delimiter, keep_default_na=False)
    if d.caseNumberFull.duplicated().any():
        raise ValueError(f"Duplicate case IDs in {year}")
    d["year"] = year
    d["date"] = pd.to_datetime(d.submitDate, format="mixed", errors="coerce")
    invalid = ~d.submitDate.isin(["None", "", "0"]) & d.date.isna()
    if invalid.any():
        raise ValueError(f"Unparsed dates in {year}: {d.loc[invalid, 'submitDate'].unique()}")
    d["has_visa"] = pd.to_numeric(d.Issued, errors="raise") > 0
    d["principal_issued"] = d.status.eq("Issued")
    d["observed"] = ~d.status.isin(["None", ""])
    return d


def aggregate(d, keys):
    g = d.groupby(keys).agg(cases=("caseNumberFull", "size"),
                            issued_cases=("has_visa", "sum"),
                            principal_issued=("principal_issued", "sum"),
                            visas=("Issued", "sum")).reset_index()
    g["share"] = g.issued_cases / g.cases
    # Wilson intervals describe binomial sampling only, not selection bias.
    n, p, z = g.cases, g.share, 1.959963984540054
    center = (p + z*z/(2*n))/(1+z*z/n)
    half = z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    g["wilson_low"], g["wilson_high"] = center-half, center+half
    return g


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    frames, audit, missing = [], [], []
    for path in sorted((ROOT / "input").glob("FY*-ceac-current.csv")):
        year = int(path.name[2:6])
        d = load(year)
        real = d[d.observed]
        known = real[real.date.notna()]
        frames.append(known)
        audit.append(dict(year=year, rows=len(d), observed_cases=len(real),
                          no_status_rows=int((~d.observed).sum()), dated_cases=len(known),
                          date_coverage=len(known)/len(real),
                          issued_cases=int(real.has_visa.sum()),
                          dated_issued_cases=int(known.has_visa.sum()),
                          visas=int(real.Issued.sum()), dark_cases=int(real.status.eq("Dark").sum()),
                          first_date=str(known.date.min().date()), last_date=str(known.date.max().date())))
        for status, s in real.groupby("status"):
            missing.append(dict(year=year, status=status, cases=len(s), dated=int(s.date.notna().sum())))
    pd.DataFrame(audit).to_csv(OUT / "coverage.csv", index=False)
    pd.DataFrame(missing).to_csv(OUT / "date_coverage_by_status.csv", index=False)
    dated = pd.concat(frames, ignore_index=True)
    daily = aggregate(dated, ["year", "region", "date"])
    daily.to_csv(OUT / "daily_by_region.csv", index=False)
    aggregate(dated, ["year", "date"]).to_csv(OUT / "daily_all.csv", index=False)
    # An explicit case-level outcome: at least one Issued visa in the family case.
    # The principal's status alone misses mixed-status family cases.
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    starts = dated.groupby("year").date.transform("min")
    dated["relative_day"] = (dated.date - starts).dt.days + 1
    relative = aggregate(dated, ["year", "relative_day"])
    relative.to_csv(OUT / "relative_daily_all.csv", index=False)
    for region in ("ALL", "EU"):
        sub = dated if region == "ALL" else dated[dated.region.eq(region)]
        grouped = aggregate(sub, ["year", "relative_day"])
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        for color, (year, g) in zip(plt.get_cmap("tab10").colors, grouped.groupby("year")):
            label = str(year) + (" (неполный)" if year == 2026 else "")
            style = "--" if year == 2026 else "-"
            axes[0].plot(g.relative_day, g.issued_cases, style, color=color, label=label, alpha=.85)
            axes[1].plot(g.relative_day, g.share, style, color=color, alpha=.85)
        axes[0].set_ylabel("Кейсы с ≥1 выданной визой")
        axes[1].set_ylabel("Доля среди кейсов с известной датой")
        axes[1].yaxis.set_major_formatter(PercentFormatter(1))
        axes[1].set_ylim(0, 1)
        axes[1].set_xlabel("День относительно первой наблюдаемой submitDate в году (первый = 1)")
        axes[0].legend(ncol=5, loc="upper left", fontsize=10)
        for ax in axes:
            ax.grid(alpha=.2)
            ax.set_xticks(range(1, 38, 2))
        scope = "все регионы" if region == "ALL" else "регион EU"
        fig.suptitle(f"DV-2017–2026 · относительная дата заявки · {scope}", fontsize=18)
        fig.text(.07, .025, "Только кейсы с известной датой; пропуски NVC создают смещение выборки.\n"
                 "Начало отсчитывается по данным всего года, включая для EU. Источник: DV Charts / CEAC.", fontsize=10)
        fig.tight_layout(rect=(0, .07, 1, .96))
        for extension in ("png", "svg"):
            fig.savefig(OUT / f"relative_all_years_{region}.{extension}", dpi=160)
        plt.close(fig)
    for region in ("ALL", "EU"):
        fig, axes = plt.subplots(2, 2, figsize=(13, 8))
        for col, year in enumerate((2024, 2025)):
            sub = dated[dated.year.eq(year)]
            if region != "ALL":
                sub = sub[sub.region.eq(region)]
            g = aggregate(sub, ["date"])
            ax = axes[0, col]
            ax.bar(g.date, g.cases, color="#cbd5e1", label="Все кейсы с датой")
            ax.bar(g.date, g.issued_cases, color="#2563eb", label="Есть выданная виза")
            ax.set_title(f"DV-{year} · n = {len(sub):,}".replace(",", " "))
            ax.set_ylabel("Число кейсов")
            ax.legend(fontsize=9)
            ax = axes[1, col]
            ax.plot(g.date, g.share, color="#2563eb", linewidth=1.7)
            ax.fill_between(g.date, g.wilson_low, g.wilson_high, color="#2563eb", alpha=.15)
            ax.yaxis.set_major_formatter(PercentFormatter(1))
            ax.set_ylim(0, 1)
            ax.set_ylabel("Доля кейсов с ≥1 выданной визой")
            for row in range(2):
                a = axes[row, col]
                a.xaxis.set_major_locator(mdates.DayLocator(interval=7))
                a.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y"))
                a.tick_params(axis="x", rotation=20)
                a.grid(axis="y", alpha=.18)
            ax.set_xlabel("submitDate из CEAC")
        scope = "все регионы" if region == "ALL" else "регион EU"
        fig.suptitle(f"Дата submitDate и выдача визы · {scope}", fontsize=18, y=.98)
        fig.text(.06, .035, "Только наблюдаемые кейсы с известной датой. Это не вероятность для всех участников лотереи.\n"
                 "Затенение: 95% интервал Уилсона; он не учитывает смещение выборки. Источник: DV Charts / CEAC.", fontsize=10)
        fig.tight_layout(rect=(0, .09, 1, .95))
        fig.savefig(OUT / f"submission_vs_issued_{region}.png", dpi=160)
        fig.savefig(OUT / f"submission_vs_issued_{region}.svg")
        plt.close(fig)
    print(pd.DataFrame(audit).to_string(index=False))
    for year in (2024, 2025):
        for region in ("ALL", "EU"):
            s = dated[dated.year.eq(year)]
            if region != "ALL":
                s = s[s.region.eq(region)]
            print(year, region, len(s), int(s.has_visa.sum()), round(s.has_visa.mean()*100, 2))


if __name__ == "__main__":
    main()
