"""Download published CEAC snapshots without querying individual applicants."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get("Last-Modified")


def download(year, as_of):
    index_url = f"https://db.ceac.xarthisius.xyz/{year}.json?shallow=true"
    data, _ = fetch(index_url)
    dates = sorted(d for d in json.loads(data) if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d) and d <= as_of)
    if not dates:
        raise ValueError(f"No snapshots through {as_of}")
    snapshot = dates[-1]
    url = f"https://dvcharts.github.io/data/raw/{year % 100}/FY{year}-ceac-{snapshot}.csv.gz"
    compressed, modified = fetch(url)
    raw = gzip.decompress(compressed)
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    if not {"caseNumberFull", "submitDate", "status", "Issued"}.issubset(reader.fieldnames or []):
        raise ValueError("Unexpected CSV schema")
    rows = sum(1 for _ in reader)
    if not rows:
        raise ValueError("Empty CSV")
    path = ROOT / "input" / f"FY{year}-ceac-current.csv"
    path.write_bytes(raw)
    return dict(year=year, snapshot_date=snapshot, url=url, index_url=index_url,
                downloaded_at_utc=datetime.now(timezone.utc).isoformat(),
                last_modified=modified, bytes=len(raw), rows=rows,
                sha256=hashlib.sha256(raw).hexdigest())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--years", nargs="+", type=int, default=[2024, 2025, 2026])
    parser.add_argument("--as-of", default=datetime.now(timezone.utc).date().isoformat())
    args = parser.parse_args()
    path = ROOT / "input" / "download_manifest.json"
    records = {r["year"]: r for r in json.loads(path.read_text())} if path.exists() else {}
    failed = False
    for year in args.years:
        try:
            record = download(year, args.as_of)
            records[year] = record
            print(json.dumps(record), flush=True)
        except Exception as exc:
            failed = True
            print(f"FY{year}: {exc}", flush=True)
            records.setdefault(year, {"year": year})["last_attempt_error"] = str(exc)
        path.write_text(json.dumps(list(records.values()), indent=2), encoding="utf-8")
    raise SystemExit(1 if failed else 0)
