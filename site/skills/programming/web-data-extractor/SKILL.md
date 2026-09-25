---
name: web-data-extractor
description: >-
  Extract structured data from websites with a polite, dry-run-first requests +
  BeautifulSoup scraper: CSS-selector field mapping, automatic pagination,
  CSV/JSON output, and built-in rate limiting. Use when the user asks to web
  scraping / data extraction / crawl a website / extract a table / scrape a
  listing / paginate results / pull prices off a page. Do NOT use for
  JavaScript-heavy SPAs (needs a real browser), bypassing login walls, CAPTCHA
  solving, or large-scale distributed crawling.
license: Apache-2.0
compatibility: "Python 3.8+; requires requests and beautifulsoup4 (pip install requests beautifulsoup4). CSV/JSON output uses stdlib. Needs network access to the target site; respects a configurable delay between pages."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: programming
  verified-date: "2026-09-25"
---

# Web Data Extractor (Polite HTML Scraper)

Turn a CSS-selector recipe into a CSV/JSON dataset: fetch one page -> map fields
-> follow the next-page link -> clean and save. The bundled script never touches
a file unless `--output` is given, and `--dry-run` previews the first page so you
can confirm selectors before crawling.

## Applicability Decision Table

| Situation | Use this skill? | Notes |
|---|:---:|---|
| Static HTML listing/details pages, table rows, prices | Yes | requests + BeautifulSoup is enough |
| Need CSV/JSON out of repeated pages | Yes | pagination via `--next` |
| JS-rendered SPA / infinite scroll that returns empty on static fetch | Partial | switch to browser automation (see JS Rendering) |
| Behind a login wall / paywall | No | Do not bypass auth; use the site's official API |
| Need to solve CAPTCHAs or evade bot detection | No | Out of scope; stop and report |
| One-off browser DevTools copy | No | Just copy the text; no script needed |

## Input Checklist

| Input | Required | Default | Notes |
|---|:---:|---|---|
| `--url` | yes | - | Start page; must be reachable |
| `--selectors` | yes | - | JSON map `{field: css}`, e.g. `'{"title":"h1","price":".price"}'` |
| `--output` | unless dry-run | - | `.csv` or `.json` |
| `--next` | no | - | Next-page link selector, e.g. `.next a` |
| `--max-pages` | no | 10 | Hard cap to avoid runaway loops |
| `--delay` | no | 2.0s | Seconds between requests; raise on sensitive sites |

When inputs are missing, ask once: target URL, the fields needed (with sample
selectors if known), output format, and whether pagination is involved.

## Pre-flight Checks

```bash
python3 -c "import requests, bs4; print('deps OK')"
python3 scripts/extract.py --url "$URL" --selectors '{"title":"title"}' --dry-run
curl -s "$(python3 -c 'import sys;from urllib.parse import urlparse;print(urlparse(sys.argv[1]).scheme+"://"+urlparse(sys.argv[1]).netloc)' "$URL")/robots.txt" | head
```

Before crawling: (1) read `robots.txt` for the target path; (2) confirm the ToS
allows automated collection; (3) start with `--dry-run` and a small `--max-pages`.

## Workflow

### Step 1: Identify the target
Confirm the exact start URL, the record (one row = one listing/detail), and the
fields needed. Note the site's volume: large catalogs may need batching.

### Step 2: Inspect structure
Open the page in a browser, right-click a field -> Inspect, and read the real DOM.
Write one CSS selector per field; prefer stable classes/IDs over generated paths.

### Step 3: Choose the method
Static HTML -> this script. Empty fields on a JS-heavy page -> see JS Rendering.

### Step 4: Extract
```bash
python3 scripts/extract.py --url "$URL" \
  --selectors '{"title":"h2.item","price":".price"}' --dry-run
```
Dry-run prints each field; adjust selectors until every row looks right.

### Step 5: Handle pagination
Add `--next ".next a"` to follow pages; set `--max-pages` and `--delay` (2s default).
The script stops on missing/duplicate next-link and warns on empty records.

### Step 6: Clean & output
```bash
python3 scripts/extract.py --url "$URL" \
  --selectors '{"title":"h2.item","price":".price"}' \
  --next ".next a" --max-pages 20 --output items.csv
```
Strip stray whitespace in post; pass the dataset downstream (see Chain Handoff).

## Extraction Patterns

| Pattern | How |
|---|---|
| List pages | One selector per repeated card field; paginate with `--next` |
| Detail pages | Pull list URLs first, then run the script per detail URL |
| HTML tables | Selectors target `th`/`td` cells; one row per record |
| Infinite scroll | Static fetch returns only the first batch; use browser automation |

## Anti-Scraping Handling

Set a browser-like `--user-agent` and send session `--cookie` for pages that need
a warmed session. Keep `--delay` >= 1s and respect `--max-pages`. If a page starts
returning 403/429 or challenge pages, stop: do not rotate proxies or solve
CAPTCHAs here (see Failure Remediation).

## JS Rendering

When `--dry-run` returns empty fields on a page that clearly has content in a
browser, the data is rendered client-side. Switch to a browser automation tool
(headless browser / Playwright-style) and render before extracting; this script
only does static requests.

## Compliance & Ethics

Honor `robots.txt` and the site ToS. Do not collect personal data (PII) beyond
what is needed, do not hammer the server (rate limit), and respect copyright on
the extracted content. Prefer an official API when one exists.

## Failure Remediation Table

| Symptom | Cause | Remedy |
|---|---|---|
| `could not connect` / timeout | Network down or site blocking | Check URL; retry once; raise `--timeout` |
| `HTTP 403` / `429` | Bot detected, rate-limited | Lower speed, raise `--delay`, set `--user-agent`; stop if it persists |
| Empty fields in dry-run | Wrong selector or JS-rendered page | Re-inspect DOM; if JS, use browser automation |
| `--selectors is not valid JSON` | Bad quoting | Wrap JSON in single quotes; escape inner double quotes |
| Pagination stops after page 1 | No `--next` selector given | Inspect the next-link element, set `--next` |
| Next URL repeats / loop | Site reuses the same link | The script detects revisits; raise `--max-pages` or fix `--next` |
| Output has `(empty)` rows | Selector mismatch on some pages | Compare against the live DOM; widen the selector |

## Quality Checklist

- [ ] `robots.txt` and ToS checked before crawling
- [ ] `--dry-run` shows correct fields before writing
- [ ] Selectors target stable classes/IDs, not generated paths
- [ ] `--max-pages` and `--delay` set sensibly
- [ ] No PII collected beyond the need; rate limit respected
- [ ] Output CSV/JSON has the expected row count and no all-empty records

## Chain Handoff

- To **data-ml-science**: hand the CSV/JSON for cleaning, ETL, and analysis.
- To **excel-assistant** (office domain): open the CSV for pivots and charts.

## References

- `scripts/extract.py` — the runnable scraper (flags listed in `--help`).
- `references/extraction-patterns.md` — selector recipes and pagination notes.
