"""Build English publication figures and descriptive tables from saved aggregates."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import platform
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter, MaxNLocator

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "ceac_analysis"
FIG = ROOT / "figures"


def main(validate_inputs=False):
    FIG.mkdir(exist_ok=True)
    daily = pd.read_csv(OUT / "relative_daily_all.csv")
    rows = []
    for year, g in daily.groupby("year"):
        end = int(g.relative_day.max())
        tail = g[g.relative_day.ge(end - 1)]
        rows.append(dict(year=int(year), observed_days=end,
                         dated_cases=int(g.cases.sum()), issued_cases=int(g.issued_cases.sum()),
                         last_two_issued_cases=int(tail.issued_cases.sum()),
                         last_two_share=float(tail.issued_cases.sum()/g.issued_cases.sum()),
                         last_two_dated_cases=int(tail.cases.sum()),
                         peak_issued_day=int(g.loc[g.issued_cases.idxmax(), "relative_day"]),
                         incomplete=bool(year == 2026)))
    pd.DataFrame(rows).to_csv(OUT / "last_two_days.csv", index=False)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False})
    for region in ("ALL", "EU"):
        if region == "ALL":
            g = daily.copy()
        else:
            r = pd.read_csv(OUT / "daily_by_region.csv", parse_dates=["date"])
            starts = pd.read_csv(OUT / "coverage.csv").set_index("year").first_date
            r["relative_day"] = (r.date - pd.to_datetime(r.year.map(starts))).dt.days + 1
            g = r[r.region.eq(region)].copy()
        fig, axes = plt.subplots(2, 1, figsize=(13, 9), sharex=True)
        for color, (year, data) in zip(plt.get_cmap("tab10").colors, g.groupby("year")):
            label = str(year) + (" (partial)" if year == 2026 else "")
            for ax, column in zip(axes, ("issued_cases", "share")):
                ax.plot(data.relative_day, data[column], color=color,
                        linestyle="--" if year == 2026 else "-", linewidth=1.6,
                        label=label, alpha=.9)
        axes[0].legend(ncol=5, fontsize=10, loc="upper left")
        axes[0].set_ylabel("Cases with at least one issued visa")
        axes[1].set_ylabel("Issued-case share among dated cases")
        axes[1].yaxis.set_major_formatter(PercentFormatter(1))
        axes[1].set_ylim(0, 1)
        axes[1].set_xlabel("Days since the first observed submitDate in each DV year (first day = 1)")
        for ax in axes:
            ax.grid(alpha=.18)
            ax.set_xticks(range(1, 38, 2))
        scope = "all regions" if region == "ALL" else "EU region"
        fig.suptitle(f"DV entry timing and visa issuance | {scope}", fontsize=19)
        fig.text(.08, .025, "Observed cases with known dates only; missing dates create selection bias. DV-2026 is partial.\n"
                 "Source: DV Charts / CEAC. submitDate is treated as an entry-date proxy; see methodology.", fontsize=10)
        fig.tight_layout(rect=(0, .075, 1, .96))
        for ext in ("png", "svg"):
            fig.savefig(FIG / f"all_years_{region.lower()}_en.{ext}", dpi=170)
        plt.close(fig)
    result = pd.DataFrame(rows)
    complete = result[~result.incomplete]
    fig, ax = plt.subplots(figsize=(12, 6.75))
    ax.bar(complete.year.astype(str), complete.last_two_share, color="#2563eb", width=.65)
    for i, value in enumerate(complete.last_two_share):
        ax.text(i, value + .004, f"{value:.1%}", ha="center", fontsize=12)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylim(0, .205)
    ax.set_ylabel("Share of observed issued cases with known dates")
    ax.set_xlabel("DV program year")
    ax.grid(axis="y", alpha=.18)
    ax.set_axisbelow(True)
    ax.set_title("The last two observed entry dates account for\n11.5–16.9% of issued cases in these snapshots", fontsize=20, loc="left", pad=20)
    fig.text(.09, .025, "Cases, not individual visa recipients. Dates use CEAC submitDate as a proxy.\n"
             "This does not estimate the odds of selection or visa issuance. Source: DV Charts / CEAC.", fontsize=10)
    fig.tight_layout(rect=(0, .1, 1, 1))
    for ext in ("png", "svg"):
        fig.savefig(FIG / f"linkedin_last_two_days_en.{ext}", dpi=180)
    plt.close(fig)
    print(result.to_string(index=False))
    if not validate_inputs:
        return
    validation, inputs = [], []
    calendar = pd.read_csv(OUT / "daily_all.csv")
    manifest = {r["year"]: r for r in json.loads((ROOT / "input/download_manifest.json").read_text())}
    for path in sorted((ROOT / "input").glob("FY*-ceac-current.csv")):
        year = int(path.name[2:6])
        with path.open(encoding="utf-8-sig") as f:
            separator = ";" if ";" in f.readline() else ","
        with path.open(encoding="utf-8-sig") as f:
            records = list(csv.DictReader(f, delimiter=separator))
        known = [r for r in records if r["status"] not in ("None", "") and r["submitDate"] not in ("None", "", "0")]
        a = calendar[calendar.year.eq(year)]
        assert len({r["caseNumberFull"] for r in records}) == len(records)
        assert int(a.cases.sum()) == len(known)
        assert int(a.issued_cases.sum()) == sum(int(r["Issued"]) > 0 for r in known)
        assert int(a.principal_issued.sum()) == sum(r["status"] == "Issued" for r in known)
        assert int(a.visas.sum()) == sum(int(r["Issued"]) for r in known)
        assert not any(r["status"] in ("None", "") and int(r["Issued"]) > 0 for r in records)
        rel = daily[daily.year.eq(year)]
        assert int(rel.cases.sum()) == len(known)
        assert rel.relative_day.min() == 1
        validation.append(dict(year=year, dated_cases=len(known), checks="PASS"))
        inputs.append(dict(year=year, file=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           bytes=path.stat().st_size, delimiter=separator,
                           snapshot_date=manifest.get(year, {}).get("snapshot_date"),
                           provenance="dated public archive" if year in manifest else "author's legacy local snapshot; capture date unknown"))
    pd.DataFrame(validation).to_csv(OUT / "validation_all_years.csv", index=False)
    (OUT / "input_inventory.json").write_text(json.dumps(inputs, indent=2), encoding="utf-8")
    (OUT / "environment.json").write_text(json.dumps(dict(python=platform.python_version(), pandas=pd.__version__,
        numpy=np.__version__, matplotlib=matplotlib.__version__), indent=2), encoding="utf-8")
    print("Independent CSV reconciliation passed for all years.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate-inputs", action="store_true", help="Reconcile with local raw CSVs and record their hashes")
    main(parser.parse_args().validate_inputs)
