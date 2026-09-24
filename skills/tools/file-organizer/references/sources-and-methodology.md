# Methodology sources and design trade-offs

> When to read: when you want to change the dedup strategy, adjust conflict naming rules, or question "why not just delete duplicates."
> This file does not contain API details; it only covers design rationale.

## Idea sources (distilled from public methodology; no code copied)

| This script's approach | Idea distilled from |
|--------------|--------------|
| Read-only first / dry-run default | The Unix toolchain convention of "--dry-run first, then commit to disk"; `rsync -n`, `git clean -n`, Terraform `plan/apply` two-phase model |
| Prefix assertion after `resolve()` | The OWASP path-traversal protection canonicalize-then-check pattern |
| Size + header-hash dedup | The `fdupes` / `jdupes` size-then-partial-hash prefilter idea; full content comparison only among same-size candidates |
| Keep "oldest / shortest path" | Archiving toolchains (e.g. backup dedup) default to "keep the earliest original" to reduce broken links |
| Conflict appends `_1` sequence | An improved version of Windows Explorer / macOS Finder's "copy 2" naming convention (monotonically increasing sequence, easy for script idempotent reruns) |

## Key trade-offs

**Why dedup only reads the first 1KB?** Hashing a 4GB video in full takes tens of seconds, while the vast majority of duplicates
share the same size; reading 1KB is enough to distinguish. The cost is the theoretical existence of false negatives of
"same size + same first 1KB + different tail"—therefore `dedupe` is a **suggestion tool, not a cleanup tool**; the delete action always stays in human hands.

**Why doesn't apply support `--by size`?** Size is a file's physical attribute, not a semantic category.
After archiving by size, "invoice.pdf" ends up in `small(<1MB)/` and the user can never find it again.
`plan --by size` is retained to let the user observe the size distribution, not to encourage archiving that way.

**Why are symlinks always skipped?** Following symlinks during traversal would let "organize directory A" unexpectedly modify directory B,
and render boundary assertions meaningless. Skipping is the only choice that guarantees both safety and predictability.

**Why move rather than copy-then-delete?** `shutil.move` is a `rename` within the same filesystem,
atomic and instantaneous; across filesystems it auto-degrades to copy + delete. A copy-delete implementation leaves half a file if it fails midway.

## Official documentation

- Python `pathlib` (symlink semantics of `Path.resolve`): <https://docs.python.org/3/library/pathlib.html>
- Python `os.walk` (in-place trimming of `dirnames` to control descent): <https://docs.python.org/3/library/os.html#os.walk>
- Python `shutil.move`: <https://docs.python.org/3/library/shutil.html#shutil.move>
- Python `hashlib`: <https://docs.python.org/3/library/hashlib.html>
- `fdupes` (reference implementation of size + partial-hash dedup): <https://github.com/adrianlopezroche/fdupes>
