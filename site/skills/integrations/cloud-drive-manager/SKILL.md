---
name: cloud-drive-manager
description: "Plan and verify cloud-drive archives: enumerate a local directory into an upload manifest with per-file chunk strategy, generate sha256/md5 checksum lists for post-upload comparison, and render Baidu / Aliyun / OneDrive listing responses as readable tables. Use when the user asks to archive to a cloud drive / upload to Baidu Netdisk / back up to Aliyun Drive / sync to OneDrive / list cloud-drive files / verify upload completeness / archive to cloud drive / upload to Baidu Netdisk / backup to Aliyun Drive / sync to OneDrive. Do NOT use for Notion pages (use notion-workspace), chat notifications (use feishu-dingtalk-bridge), or local-only file organization (use file-organizer)."
license: Apache-2.0
compatibility: "Python 3.8+ stdlib only for the helper script (hashlib/json/pathlib). Live uploads need outbound HTTPS plus BAIDU_ACCESS_TOKEN / ALIYUN_REFRESH_TOKEN / ONEDRIVE_ACCESS_TOKEN in environment variables; the bundled script never contacts a network or deletes anything."
metadata:
  author: "awesome-skillkit"
  version: "1.0"
  category: integrations
  pattern: single-task
  tier: standard
  verified-date: "2026-09-17"
---

# Cloud Drive Manager (Cloud Archive)

Archiving an entire local directory to a cloud drive — the hard part is not "uploading," but three things:
**what to upload** (what to exclude), **how to upload** (simple upload or multipart), and **how to prove it uploaded correctly afterward** (checksums).

**Core judgment: produce a plan and a checksum checklist first, then talk about uploading.** The pre-upload checklist is "what will happen"; the post-upload checksum list is "did it actually happen." Missing either makes the archive untrustworthy.

**Red lines (enforced by this skill)**

1. **Never hardcode credentials**: access_token / refresh_token / client_secret are read only from environment variables
   (`BAIDU_ACCESS_TOKEN` / `ALIYUN_REFRESH_TOKEN` / `ONEDRIVE_ACCESS_TOKEN`).
   The script **never touches** these values — it only reads the local directory. Never write tokens into the script, config, or repo.
2. **Dry-run by default**: `plan-upload` outputs a plan and **uploads no files**.
   A real upload is a separate step the user runs after confirming the checklist.
3. **Double-confirm deletes**: this script **provides no delete command at all**. If the user wants to delete cloud files,
   you must first list them and then **confirm twice** — ① the target path is correct; ② the affected file count matches
   expectations. If either is in doubt, move/archive instead of deleting.
4. **Least privilege**: request only file read/write scopes from the cloud-drive open platform (e.g. Baidu's `netdisk`),
   **do not** request user-info, contacts, or other unrelated scopes; if authorization is limited to a single directory, do not request the whole drive.

## Input Checklist

| Input | Required | Notes |
|---|---|---|
| Source directory | Yes | The local directory to archive; symlinks are skipped |
| Remote root path | Yes | e.g. `/archive/2026-Q3`; confirm ownership and quota for this directory before uploading |
| Cloud-drive provider | Yes | `baidu` / `aliyun` / `onedrive`; determines the chunk threshold and hashing algorithm |
| Exclude rules | No | Comma-separated globs, e.g. `*.tmp,.DS_Store,node_modules/*` |
| Subpath prefix | No | `--prefix`; prepend a layer before relative paths, e.g. `backup` |
| access_token | Required for real uploads | Environment variable only; not needed during planning and verification |
| Listing response JSON | Required for parsing | The listing response body pulled from the cloud-drive API |

**When inputs are missing, ask for all at once:**

> Please provide in one go: ① the local source directory; ② the cloud-drive provider and remote target path; ③ file types to exclude
> (e.g. temp files, dependency directories); ④ whether the access_token is already in the environment
> (do not paste it to me — I only check for its existence). I will default to producing an upload plan and checksum checklist first, and will not upload.

## Pre-flight Self-check

```bash
python3 --version                                        # expect >= 3.8
test -f scripts/drive_ops.py && echo SCRIPT_OK            # expect to print SCRIPT_OK
# Credential check: only judge existence, never echo
for v in BAIDU_ACCESS_TOKEN ALIYUN_REFRESH_TOKEN ONEDRIVE_ACCESS_TOKEN; do
  printf '%s: ' "$v"; test -n "$(printenv $v)" && echo present || echo missing
done
test -d "$SRC_DIR" && echo DIR_OK                         # source directory exists
du -sh "$SRC_DIR" 2>/dev/null                             # first look at size vs quota
df -h "$SRC_DIR" | tail -1                                # also confirm local readability
```

| Result | Interpretation |
|---|---|
| A token is `missing` | Only affects the real upload; planning and verification proceed, produce the plan first |
| `DIR_OK` missing | The source directory does not exist; `plan-upload` will error out directly |
| Directory size > cloud-drive remaining quota | **Stop and ask the user** how to proceed; do not auto-batch |

## Cross-provider API Difference Table

| Dimension | Baidu Netdisk | Aliyun Drive | OneDrive |
|---|---|---|---|
| Auth | OAuth2 `access_token` (valid 30 days, needs refresh) | Exchange `refresh_token` for `access_token` (2 hours) | OAuth2 `access_token` (1 hour, refreshed via refresh) |
| Per-request upload cap | **4MB** (beyond forces multipart) | 100MB | **250MB** |
| Chunk size | Fixed **4MB** | Recommended 8MB | Must be an **integer multiple of 320KiB** |
| Instant-upload / dedup key | Whole-file **MD5** + per-chunk MD5 | **SHA1** + per-segment SHA1 | **quickXorHash** or sha256 |
| Listing entry fields | `list[]`, `isdir` 1/0, `fs_id`, `server_filename` | `items[]`, `type` `folder`/`file`, `file_id` | `value[]`, judge type via `folder`/`file` **sub-object** |
| Directory detection | `isdir == 1` (integer) | `type == "folder"` (string) | Presence of the `folder` key |
| Delete endpoint | To recycle bin (recoverable, retention period) | To recycle bin | To recycle bin / permanent delete (needs explicit `permanent` param) |
| Rate limits | Strict; chunked upload needs intervals | Moderate | Relaxed, with 429 backoff required |
| Special notes | The auth token must be refreshed every 30 days, or the whole batch breaks | Few directly exposed third-party SDKs; recommend direct REST | Chunk size must be a multiple of 320KiB, else 400 |

## How Instant Upload Works (why hashes are computed before uploading)

"Instant upload" is not a transfer optimization — it is **deduplication**: the client first computes the hash of the file
content and submits the hash to the server; the server checks its own storage for a record of an existing **whole file** with the same hash.
If found, it simply creates a reference pointing to the existing content — not a single byte is transferred.

Three corollaries directly drive the archive strategy:

1. **Computing the hash is a prerequisite cost of uploading, not optional.** A client that never hashes never benefits from instant upload.
2. **The server only accepts its own hash algorithm.** Baidu accepts MD5, Aliyun Drive accepts SHA1, OneDrive accepts
   quickXorHash — using the wrong algorithm means instant upload never hits, causing pointless re-uploads.
3. **Files hit by instant upload still need verification.** A hit only means "the server has content with the same hash,"
   not that you built the reference correctly this time. After uploading, still verify the references one by one.

Therefore this skill runs `checksum-plan` once **before** uploading (to get the baseline),
and after uploading pulls a listing from the drive and compares, forming a closed loop.

## Workflow

### Step 1: Plan the Upload (dry-run)

```bash
python3 scripts/drive_ops.py plan-upload \
  --dir "$SRC_DIR" --remote /archive/2026-Q3 \
  --provider baidu --prefix backup \
  --exclude "*.tmp,.DS_Store,node_modules/*" \
  --manifest upload_plan.json
```

Expected: prints the file list (relative path / size / upload strategy), the list of remote directories to create,
and the chunk basis for that platform. `--manifest` writes the same plan to JSON for later steps to consume.

**Layout meaning**: `simple` means a single request can carry it; `slice xN (4MB/chunk)` means it needs N multipart uploads.

On failure: `not a directory` → check the path; `no uploadable files in the directory` → **the script errors with exit code 2**
(an empty list is not success) — check whether `--dir` points wrong, or whether `--exclude` filtered everything out.

### Step 2: Generate the Checksum Baseline

```bash
python3 scripts/drive_ops.py checksum-plan --dir "$SRC_DIR" \
  --output sha256_before.txt --algo sha256 --exclude "*.tmp"
```

Expected: standard `<hash>  <relative path>` format, **verifiable directly with system tools**:

```bash
cd "$SRC_DIR" && sha256sum -c sha256_before.txt
```

On failure: `unsupported algorithm` → only `sha256` / `md5` / `sha1` are selectable;
`no computable files in the directory` → **the script errors with exit code 2** (a 0-line list is not a valid baseline; it would make
`sha256sum -c` pass vacuously and mask the problem) — first check `--dir` and `--exclude`;
large directories are slow → normal; `hashlib` computes streaming and does not use memory but is limited by disk read speed.

### Step 3: Upload (credentials injected by the proxy layer)

The upload itself is done by the AI/user via SDK or REST; the script does not participate. Key constraints:

- Follow the path per `mode`: `simple` uses the single-request endpoint; `slice` first `create` to get an uploadid,
  then `upload` each chunk, and finally `create` to close it out;
- Chunks must be submitted **in order** (Baidu/Aliyun both require order; out-of-order fails);
- Leave an interval between chunks to avoid triggering rate limits;
- Try the instant-upload endpoint first — hit files skip byte transfer.

Expected: each file returns a remote file_id, recorded in a ledger.
On failure: `access_token expired` → Baidu 30 days, Aliyun 2 hours, OneDrive 1 hour;
after refreshing, **resume from the checkpoint** rather than starting over (completed chunks need not be re-uploaded).

### Step 4: Pull the Listing and Verify

```bash
# first pull the drive listing and save as JSON, then parse
python3 scripts/drive_ops.py parse-list --json cloud_list.json --provider baidu
```

Expected: entry count and total file size match the plan from step 1; directory/file classification is correct.

**Per-file comparison**: compare remote hashes (if the API returns a hash field) against the step-2 baseline,
or at least compare **filename + size**; files whose size differs must be re-uploaded.

On failure: fewer entries → the upload was interrupted and not resumed; size 0 → the upload created a placeholder but wrote no content.

### Step 5: Delete (if truly necessary) — Double Confirm

This script **provides no delete command**, by design. If deletion is needed, you must:

1. **First confirmation**: show the user the `parse-list` output and have them confirm the **target path** is entirely correct;
2. **Second confirmation**: explicitly report the **affected file count and total size**, and have the user confirm it matches expectations;
3. Prefer **moving to an archive directory** over deleting — the recycle bin has a retention period, after which it is unrecoverable.

Expected: act only after the user confirms twice, preferring "move."
On failure: either confirmation is in doubt → stop, switch to a move, or let the user do it themselves on the web.

## Delivery Standards

- **Definition of success**: the cloud side's file count and total size match the upload plan, and sampled file hashes match
  the local baseline.
- **Artifacts**: `upload_plan.json` (plan), `sha256_before.txt` (local baseline),
  the cloud listing JSON + parsed output (remote view), and the upload ledger (file_id mapping).
- **Integrity verification**:
  - `sha256sum -c sha256_before.txt` is all OK (confirms the local baseline itself is reliable);
  - cloud entry count == planned file count, total size equal;
  - every local file in the ledger has a corresponding file_id, with no omissions;
  - no token plaintext may appear in any artifact: `grep -lE 'access_token|refresh_token' *.json` should have no hits.

## Failure Handling Table

| Symptom | Cause | Action |
|---|---|---|
| Baidu multipart upload reports `file size error` | Went simple-upload on a >4MB file, or chunk size is not 4MB | Use `plan-upload`'s `mode` field to decide the path; Baidu's chunk size is fixed at 4MB and cannot be chosen |
| OneDrive `400 invalidRequest` | Chunk size is not an integer multiple of 320KiB | Use e.g. 10MB (320KiB×32); `plan-upload`'s defaults already satisfy this |
| `access_token` expires mid-upload | Baidu 30-day / Aliyun 2-hour / OneDrive 1-hour short cycles | After refreshing the token, **resume from checkpoint**: continue completed chunks via the uploadid; do not start over |
| Instant upload never hits | Used a hash algorithm the platform does not accept (e.g. sending MD5 to Aliyun Drive) | Baidu uses MD5, Aliyun uses SHA1, OneDrive uses quickXorHash; the wrong algorithm never hits |
| The listing has fewer files than the plan | The upload was interrupted, or the directory was modified concurrently during upload | Use `plan-upload --manifest`'s snapshot to diff, and only re-upload the missing items |
| `plan is empty` / `no uploadable files in the directory` (exit code 2) | `--dir` points wrong, or `--exclude` globs are too broad and filtered everything | Check the absolute path `--dir` points to; narrow `--exclude` and rerun `plan-upload` to inspect the list. An empty list is not success; the script intentionally returns non-zero to block the pipeline |
| Listing size is 0 but files exist | A file record was created but content not written (multipart not closed) | Re-upload that file; multipart upload must call the close endpoint (Baidu `create`, Aliyun `complete`) |
| Upload hits rate limits | Requests too dense (Baidu especially strict) | Serial upload + inter-chunk intervals; on 429 use exponential backoff, do not retry concurrently |
| Files that should have uploaded were skipped | Misused `--exclude` globs (e.g. `*.log` filtered out logs to keep) | Run `plan-upload` first to inspect the list, confirm, then upload — that is the point of the dry-run |
| Symlinked content was not uploaded | The script intentionally skips symlinks | This is protection: following links would unexpectedly upload the external directory the link points to. Upload the real file if needed |
| Unrecoverable after deletion | The recycle-bin retention period expired, or a permanent-delete parameter was used | Double-confirm before deleting; prefer "move to archive directory" over deleting |

## References

- `scripts/drive_ops.py` — `plan-upload` (manifest + chunk strategy) /
  `checksum-plan` (directly consumable by `sha256sum -c`) / `parse-list` (normalizes the three providers' listings)
- `references/sources-and-methodology.md` — the principle of instant upload, the basis for chunk thresholds,
  and why the script provides no delete command
