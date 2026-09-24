# Full PII Detection Rules (8 categories)

> This file is the methodology reference for `pii_scan.py`, for use when manually reviewing false positives. All regexes use Python `re` syntax.

## Strong-validation classes (enabled by default, low false-positive rate)

| Category | Regex | Validation |
|------|------|------|
| `id_card` | `(?<!\d)(\d{17}[\dXx])(?!\d)` | ID-card mod-11 check digit (`ID_WEIGHTS` + `ID_CHECK`) |
| `phone` | `(?<!\d)(\+?86[-\s]?)?(1[3-9]\d{9})(?!\d)` | Prefix `1[3-9]` |
| `bank_card` | `(?<!\d)(\d{13,19})(?!\d)` | Luhn mod-10 check |
| `credit_code` | `(?<![0-9A-Za-z])([0-9A-HJ-NP-RTUWXY]{2}\d{6}[0-9A-HJ-NP-RTUWXY]{10})(?![0-9A-Za-z])` | Unified social credit code length 18 (charset digits/letters, excludes I/O/S/V/Z) |
| `plate` | `(province_abbrev[A-Z])\d{4,5}[A-Z0-9 special_suffix]` | Chinese province-abbreviation set + special suffix chars (trailer/student/police/HK/military/consulate) |

## Heuristic classes (require explicit `--categories` to enable, high false-positive rate)

| Category | Regex | Notes |
|------|------|------|
| `email` | `([A-Za-z0-9._%+-]+)@([A-Za-z0-9.-]+\.[A-Za-z]{2,})` | Strong signal, but false positives depend on the data |
| `address` | `province_abbrev[city]?...road/street/alley/number` | Geographic prefix + street-number combo, noisy |
| `name` | `(name\|contact\|... )[:：=]\s*(CJK/letters 2-15)` | Relies on context keys (the `：` colon is the CJK full-width form) |

## Check-digit algorithms

- **ID-card mod-11**: multiply the first 17 digits by `ID_WEIGHTS=[7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2]`, sum, mod 11, and look up the last digit in `ID_CHECK="10X98765432"`.
- **Luhn mod-10**: from right to left, double every other digit (subtract 9 if >9), sum the whole column, mod 10 == 0.

## False-positive reference

| Input | Expected hit | Notes |
|------|---------|------|
| `13800138000` | phone | Valid prefix |
| `1001234` | none | Digit string not a phone number (fewer than 11 digits) |
| `110101199003078518` (correct check digit) | id_card | mod-11 passes |
| `11010119900307851X` (wrong check digit) | none | mod-11 fails → auto-rejected |
| `622202020011223344` (Luhn passes) | bank_card | Luhn passes |
| Any 16-digit non-card number | none | Luhn fails → rejected |

> Tightening advice: when the data has lots of numeric noise, first run only the 5 strong-validation classes with `--no-heuristics`; enable `email` once you've confirmed it's clean.

## Escaped / encoded text preprocessing

If the text is URL-encoded or JSON-escaped (`\u00XX`, `%XX`), the PII shape is broken and hit counts drop sharply.
Handling: decode first with `urllib.parse.unquote` / `json.loads` before feeding to the scanner; this script scans the raw text by default,
so when hits are 0 but PII is visible to the eye, first check whether it's wrapped by an encoding layer.
