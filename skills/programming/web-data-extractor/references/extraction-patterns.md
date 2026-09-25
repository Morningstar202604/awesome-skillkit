# Extraction Patterns & Selector Recipes

Companion notes for `scripts/extract.py`. Keep these heuristics here so the
SKILL.md body stays short.

## Selector tips

- Prefer semantic, stable hooks: `.product`, `#results`, `table tbody tr`.
- Avoid long positional paths like `div:nth-child(3) > span:nth-child(2)`; they
  break on the smallest layout change.
- The script takes the FIRST match per field and uses stripped text. For repeated
  cards on a list page, run the extraction per detail URL or paginate the list.
- If a field lives in an attribute (e.g. a link href), collect the text you need
  and post-process, or extend the script.

## Pagination

- `--next` is the CSS selector of the anchor whose `href` points to the next page.
  Common values: `.next a`, `a[rel=next]`, `.pagination .next`.
- Relative URLs are resolved against the current page automatically.
- The script records visited URLs and stops if the next link repeats, so a
  "disabled next button" that re-points to the current page cannot loop forever.
- Always set `--max-pages`; the default (10) is a safety cap, not a target.

## When static extraction fails

- Empty records on a page that visibly has data in a browser => the content is
  rendered by JavaScript. Use headless browser automation, then extract from the
  rendered HTML.
- A page that needs a session/cookie can be warmed with `--cookie`, but never
  bypass a login wall or CAPTCHA.
