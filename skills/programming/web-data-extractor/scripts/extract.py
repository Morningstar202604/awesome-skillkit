#!/usr/bin/env python3
"""extract.py -- fetch a web page and pull fields out by CSS selectors.

A small, polite web-data-extraction tool built on requests + BeautifulSoup.
It turns a set of CSS selectors into structured records (CSV or JSON), with
optional pagination following a "next page" link, a configurable delay between
requests, and browser-like default headers. Dry-run mode fetches the first page
only and prints the extracted records without writing anything to disk.

Design principles
-----------------
1. **Polite by default**: a delay (default 2.0s) between every request, a
   browser-like User-Agent, and a hard page cap so a runaway selector never
   hammers a server.
2. **Read-only preview first**: `--dry-run` fetches one page and prints the
   records; no file is written unless `--output` is given and dry-run is off.
3. **Fail loud, not silent**: connection errors, HTTP errors, and unparseable
   selector JSON are reported with a clear message and a non-zero exit code.
   A selector that matches nothing on a page is recorded as an empty field and
   reported, not treated as fatal.

Examples
--------
  # Preview the first page of results, no file written
  python3 extract.py --url https://example.com \
      --selectors '{"title":"h1","lead":"p"}' --dry-run

  # Walk up to 10 pages following the ".next a" link, write CSV
  python3 extract.py --url https://example.com/items \
      --selectors '{"title":"h2.item","price":".price"}' \
      --next ".next a" --max-pages 10 --output items.csv

Stdlib for CSV/JSON/argparse; third-party: requests, beautifulsoup4.
Python >= 3.8.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from urllib.parse import urljoin

try:
    import requests
except ImportError:  # pragma: no cover - dependency is declared, but stay friendly
    print(
        "ERROR: the 'requests' package is required. Install it with: pip install requests",
        file=sys.stderr,
    )
    sys.exit(2)

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    print(
        "ERROR: the 'beautifulsoup4' package is required. Install it with: pip install beautifulsoup4",
        file=sys.stderr,
    )
    sys.exit(2)


# A realistic desktop browser header set. Sites that serve a stripped-down page
# to the default "python-requests/x.y" UA usually render the full layout to this.
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def build_session(user_agent: str | None, cookie: str | None) -> requests.Session:
    """Create a requests.Session with browser-like headers and optional overrides."""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    if user_agent:
        session.headers["User-Agent"] = user_agent
    if cookie:
        # Set as a raw Cookie header; the user supplies the whole cookie string.
        session.headers["Cookie"] = cookie
    return session


def parse_selectors(raw: str) -> dict:
    """Validate the --selectors JSON string into an ordered {field: css} map."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: --selectors is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict) or not data:
        print("ERROR: --selectors must be a non-empty JSON object, "
              "e.g. '{\"title\":\"h1\",\"price\":\".price\"}'", file=sys.stderr)
        sys.exit(2)
    for field, sel in data.items():
        if not isinstance(sel, str) or not sel.strip():
            print(f"ERROR: selector for field '{field}' must be a non-empty string",
                  file=sys.stderr)
            sys.exit(2)
    return data


def extract_record(soup: BeautifulSoup, selectors: dict) -> tuple[dict, list]:
    """Pull one record per field selector; return (record, missing_fields).

    For each field we take the FIRST matching element and its stripped text.
    Selectors that match nothing are recorded as "" and reported as missing so
    the operator can notice a broken selector rather than silently getting blanks.
    """
    record: dict = {}
    missing: list = []
    for field, css in selectors.items():
        node = soup.select_one(css)
        if node is None:
            record[field] = ""
            missing.append(field)
        else:
            record[field] = " ".join(node.get_text(" ", strip=True).split())
    return record, missing


def next_page_url(soup: BeautifulSoup, current_url: str, next_selector: str | None) -> str | None:
    """Resolve the absolute href of the next-page link, or None when absent/disabled."""
    if not next_selector:
        return None
    node = soup.select_one(next_selector)
    if node is None:
        return None
    href = node.get("href")
    if not href:
        return None
    return urljoin(current_url, href)


def write_output(records: list[dict], selectors: dict, output: Path) -> None:
    """Write records to CSV or JSON based on the file extension."""
    suffix = output.suffix.lower()
    fieldnames = list(selectors.keys())
    output.parent.mkdir(parents=True, exist_ok=True)

    if suffix == ".json":
        with output.open("w", encoding="utf-8") as fh:
            json.dump(records, fh, ensure_ascii=False, indent=2)
    elif suffix == ".csv":
        with output.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            for rec in records:
                writer.writerow({k: rec.get(k, "") for k in fieldnames})
    else:
        print(f"ERROR: --output must end in .csv or .json (got '{suffix}')",
              file=sys.stderr)
        sys.exit(2)
    print(f"Wrote {len(records)} record(s) to {output}")


def run(args) -> int:
    selectors = parse_selectors(args.selectors)

    if not args.dry_run and not args.output:
        print("ERROR: --output is required unless --dry-run is given.", file=sys.stderr)
        return 2
    if args.output:
        output = Path(args.output)
        if output.suffix.lower() not in (".csv", ".json"):
            print("ERROR: --output path must end in .csv or .json", file=sys.stderr)
            return 2
    else:
        output = None

    session = build_session(args.user_agent, args.cookie)

    records: list[dict] = []
    url = args.url
    seen: set[str] = set()
    page = 0
    max_pages = 1 if args.dry_run else args.max_pages

    while url and page < max_pages:
        if url in seen:
            print(f"Stopping: next-page URL already visited ({url}); pagination loop.",
                  file=sys.stderr)
            break
        seen.add(url)
        page += 1

        try:
            resp = session.get(url, timeout=args.timeout)
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            print(f"ERROR: could not connect to {url}: {exc}", file=sys.stderr)
            return 1
        except requests.exceptions.Timeout:
            print(f"ERROR: request timed out after {args.timeout}s for {url}",
                  file=sys.stderr)
            return 1
        except requests.exceptions.HTTPError as exc:
            print(f"ERROR: HTTP {resp.status_code} for {url}: {exc}", file=sys.stderr)
            return 1
        except requests.exceptions.RequestException as exc:
            print(f"ERROR: request failed for {url}: {exc}", file=sys.stderr)
            return 1

        soup = BeautifulSoup(resp.text, "html.parser")
        record, missing = extract_record(soup, selectors)
        records.append(record)

        tag = "DRY-RUN page" if args.dry_run else "page"
        print(f"[{tag} {page}] {url}")
        for field, value in record.items():
            preview = value if len(value) <= 80 else value[:77] + "..."
            mark = "  " if field not in missing else "!"
            print(f"   {mark}{field}: {preview if preview else '(empty)'}")
        if missing:
            print(f"   warning: no match for selector(s): {', '.join(missing)}")

        if args.dry_run:
            break

        url = next_page_url(soup, url, args.next)
        if url:
            time.sleep(args.delay)

    if not records:
        print("ERROR: no records extracted (nothing matched the selectors).",
              file=sys.stderr)
        return 1

    all_empty = all(not any(rec.values()) for rec in records)
    if all_empty:
        print("WARNING: every record field is empty; check your selectors against the "
              "actual page HTML.", file=sys.stderr)

    if output is not None:
        write_output(records, selectors, output)
    else:
        print(f"DRY-RUN: {len(records)} page(s) previewed; no file written.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="extract.py",
        description="Fetch web pages and extract fields by CSS selectors to CSV/JSON "
                    "(dry-run by default preview; polite delay between pages).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--url", required=True, help="target page URL (required)")
    p.add_argument("--selectors", required=True,
                   help="JSON object mapping field names to CSS selectors, "
                        "e.g. '{\"title\":\"h1\",\"price\":\".price\"}'")
    p.add_argument("--next", default=None,
                   help="CSS selector for the next-page link (e.g. '.next a'); without "
                        "this, only the start URL is fetched")
    p.add_argument("--max-pages", type=int, default=10,
                   help="maximum number of pages to follow (default: 10)")
    p.add_argument("--delay", type=float, default=2.0,
                   help="seconds to wait between page requests (default: 2.0)")
    p.add_argument("--output", default=None,
                   help="output file path, ending in .csv or .json")
    p.add_argument("--user-agent", default=None,
                   help="override the default browser User-Agent string")
    p.add_argument("--cookie", default=None,
                   help="raw Cookie header string to send with every request")
    p.add_argument("--dry-run", action="store_true",
                   help="fetch only the first page, print extracted fields, write no file")
    p.add_argument("--timeout", type=float, default=15.0,
                   help="per-request timeout in seconds (default: 15)")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
