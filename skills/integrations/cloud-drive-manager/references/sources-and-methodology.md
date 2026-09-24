# Methodology sources and design trade-offs (cloud-drive-manager)

> When to read: when you're onboarding a fourth cloud drive, adjusting chunking thresholds, or questioning "why the script has no upload and delete
> commands". This file only covers design rationale.

## Idea sources (distilled from public methodology; not copied text)

| This skill's approach | Idea distilled from |
|---|---|
| Produce an upload plan before executing | The Terraform `plan`/`apply` and `rsync -n` two-phase convention: see what will happen first |
| Run a hash manifest before and after upload | The backup-domain verify-after-write principle (e.g. `rsync --checksum`, ZFS scrub idea): after writing, must read back and verify |
| Output in standard `sha256sum -c` format | The Unix toolchain tradition of "output consumable by existing tools": don't invent a private format |
| Skip symlinks | Consistent with file-organizer: following links lets the operation scope escape user intent |
| No delete command provided | Least-privilege/minimum-blast-radius principle: smaller capability = smaller misuse surface; keep irreversible operations in human hands |
| Sensitive info only from environment variables | Twelve-factor-app config principle; credentials don't go in code or command-line args |

## Key trade-offs

**Why does the script not touch the network at all?** Once upload logic is coupled with the "what to upload" logic, you land in an
awkward spot: to verify whether the manifest is correct, you must first have real credentials and actually upload. After the split,
`plan-upload` and `checksum-plan` can be fully tested offline, with no credentials,
and the user sees what will happen **before paying any transfer cost**. The cost is that the upload step needs to be
written by the AI or the user—SKILL.md step 3 lists the key constraints (chunk order, token lifetime, resumable upload)
clearly.

**Why no delete command?** Deletion is the only irreversible operation in the cloud-drive scenario, and one whose
**consequences scale with size**—`rm -rf` with one wrong path can delete the entire archive directory. The script providing delete brings two
risks: one, the AI might call it without sufficient confirmation; two, one typo in a command-line arg causes
irreversible loss. This skill's choice: only provide the capability to "see clearly what will be deleted" (`parse-list`),
leaving the execution to the user in their own drive client—where there's a recycle bin and a second confirmation dialog.

**Why is the instant-upload principle written into SKILL.md rather than the script?** Instant upload is a **protocol-layer constraint**,
not something a function can solve: it requires the client to use the right hash algorithm, compute the hash before upload,
and still verify after a hit. All three are process requirements, written into docs to guide real implementation;
what the script can do is only provide the `checksum-plan` hash-computing tool.

**Why are chunking thresholds a data table rather than hardcoded branches?** The three vendors' thresholds (4MB / 100MB / 250MB)
are platform policies that change with versions. Consolidated into a `CHUNK_POLICY` dict, fixing one point takes effect across the whole chain,
and the threshold sits next to the "rationale" (the `note` field), so there's no drift of "changed the number but forgot the doc."

**Why does `parse-list` normalize the three vendors' fields?** The three vendors' list-entry structures differ a lot
(Baidu's `isdir` integer, Aliyun's `type` string, OneDrive's child objects),
but they carry the same information. Normalized into `(name, size, is_dir, mtime, id)`,
judgments like "how many files in this directory, total size" need be written only once. Normalization is **read-side only**,
because it doesn't touch write semantics—the write-side differences (chunking, instant upload) can't be unified this way.

**Why do both size checksum and hash checksum?** Size catches "incomplete transfer" extremely fast;
hash catches "transferred but content wrong" (chunk order wrong, encoding conversion). Size-only misses content
corruption; hash-only is expensive on large directories. Two levels of checking, cheap first, expensive second.

## Official documentation

- Baidu Netdisk open platform (chunked upload, instant upload, file list): <https://pan.baidu.com/union/doc/>
- Baidu Netdisk upload flow and 4MB chunk convention: <https://pan.baidu.com/union/doc/nksg0sbfs>
- Aliyun Drive open platform (file list, upload, SHA1 dedup): <https://www.yuque.com/aliyundrive/zpfszx>
- OneDrive upload API (250MB single-request cap): <https://learn.microsoft.com/en-us/graph/api/driveitem-put-content>
- OneDrive create upload session (chunks must be multiples of 320 KiB): <https://learn.microsoft.com/en-us/graph/api/driveitem-createuploadsession>
- Microsoft Graph list children (`value[]` and `folder`/`file` child objects): <https://learn.microsoft.com/en-us/graph/api/driveitem-list-children>
- Python `hashlib` (algorithm names supported by `new()` and streaming digest): <https://docs.python.org/3/library/hashlib.html>
