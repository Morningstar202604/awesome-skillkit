# Sources & Methodology

- Skill: `epub-builder` (originally written for awesome-skillkit, Apache-2.0).
- Position: a reinforcing skill for the `office` scenario pack. `office` originally had `docx-writer` (Word) and
  `pdf-pipeline` (PDF), missing a "reflowable e-book" outlet; this skill fills that slot.

## Methodology borrowed (ideas and normative facts only; no text or code copied)

| Source | License | Normative points borrowed |
|---|---|---|
| EPUB 3 spec (W3C / IDPF public docs) | W3C doc license | Package structure (mimetype / META-INF / OEBPS), `container.xml` rootfile pointer, OPF manifest vs. spine division of labor |
| EPUB 2 NCX TOC convention (DAISY public spec) | public spec | `toc.ncx` provides the TOC for older readers, must coexist with EPUB3's `nav.xhtml` |
| Markdown public syntax docs | see original | Basic semantics of headings/lists/quotes/code blocks/tables/inline emphasis |
| Generic ZIP file format public docs | public spec | `mimetype` must be the first entry and uncompressed (STORED), a hard OCF-layer requirement of EPUB |
| This repo's existing skill standards (SKILL-STANDARD-v2 under docs/) | Apache-2.0 | Skeleton sections, failure-handling table, subcommandization, and verifiable delivery standards |

All the above sources are used as **normative facts and structural skeleton**. The Markdown parser in `scripts/epub_build.py`,
the three XML templates for OPF/NCX/NAV, the `slugify` naming rule,
chapter-splitting logic, and the inspect read-back implementation are all written from scratch.
No upstream passage, example, or code was translated, rewritten, or excerpted.

## Key design decisions (why this way)

1. **Standard library only**: EPUB is "zip + XML"; `zipfile` and `xml.etree.ElementTree`
   suffice. Adding third-party libraries would break the skill in a bare environment, for near-zero benefit.
2. **`mimetype` write order treated as first-class**: at build time, use `ZipInfo` to explicitly specify
   `ZIP_STORED` and write it first, and reopen the file to self-check before `build` finishes—
   this is the most error-prone step and the one **hardest to notice on the surface** when wrong (the file generates, size looks normal,
   but readers reject it).
3. **Fixed ZIP timestamp**: `ZIP_TIMESTAMP = (1980,1,1,0,0,0)`,
   so the same input produces a **byte-for-byte reproducible** file, easy to diff and version-control.
4. **Chapter order read from spine, not manifest**: the manifest is just a resource list with no ordering guarantee;
   the spine defines reading order. inspect outputs by spine, matching reader behavior.
5. **Generate both toc.ncx and nav.xhtml**: old and new readers each recognize one; missing either means some devices get no TOC.
6. **UID derived from title+author+chapter count via `uuid5`**: rebuilding the same book yields the same
   `dc:identifier`, so readers don't treat each build as a new book and reset reading progress.
7. **No fancy styling**: EPUB's final typography is dominated by readers and user settings;
   over-specifying CSS breaks layouts across devices. Only minimal readable styles are provided.
8. **No image support, stated explicitly**: no pretending to support it. Images need a resource manifest, media types, and
   relative-path management—out of scope for another skill; vague promises are more harmful than saying "not supported."

## Limitations and boundaries

- **No images or cover**: text structure only. Illustrations require separate processing.
- **Chapter splitting recognizes H1 only**: does not recognize Chinese ordinal patterns like "Chapter 1"; users should organize the manuscript by H1.
- **Markdown subset**: supports headings/lists/quotes/code blocks/tables/inline emphasis/links/dividers;
  does not support footnotes, math, definition lists, embedded HTML.
- **Not epubcheck-level checking**: does not implement all epubcheck rules (e.g.
  the URI canonical form of `dc:identifier`, full media-type whitelist validation).
  For publication-level validation, run epubcheck separately.
- **No Chinese font embedding**: relies on reader font fallback; does not bundle font files.

## License

This skill and its reference files are distributed under Apache-2.0; the upstream documents listed carry their own license terms, which do not apply to this file.
