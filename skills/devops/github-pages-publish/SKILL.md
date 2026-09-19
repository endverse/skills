---
name: github-pages-publish
description: Publish local files to an existing GitHub Pages repo and verify the live page.
license: MIT
---

# GitHub Pages Publish

Push local files to an **already-created** GitHub Pages repository and verify
the live page matches your local copy (byte-for-byte SHA-256). This is the
**recurring** action — commit, push, wait for the Pages build, confirm online
== local.

One-time setup (creating the repo and enabling Pages) is a separate, do-it-once
task — see [`SETUP.md`](SETUP.md). Keep it out of any daily/automated flow.

## When to Use

- You have a static site / generated HTML in a git repo whose Pages is already enabled, and you want to publish an update and confirm it went live.
- Not for: creating repos or enabling Pages (that's `SETUP.md`, done once).

## Prerequisites

- `git` and `gh` authenticated (`gh auth status`).
- The target repo already exists locally and on GitHub, with Pages enabled
  (see `SETUP.md`).

## Quick Start

```bash
python3 scripts/publish.py \
  --repo-dir /path/to/repo \
  --pages-url https://<owner>.github.io/<repo> \
  --files page.html index.html \
  --message "Publish 2026-09-19"
```

- `--files` — files to stage; omit to commit all pending changes.
- `--verify-file` — which file to hash-check online (defaults to the first `--files`).
- The script stages → commits (skips if nothing changed) → pushes → polls the
  live URL until its SHA-256 equals the local file, or warns if Pages is still
  building.

## Pitfalls

- **Pages must already be enabled.** A brand-new empty repo has no `main`
  branch and Pages creation fails — do `SETUP.md` first.
- **Build lag is normal.** Pages takes ~1-2 min; the script polls up to ~96s.
  A "still building" warning is not a failure — re-run the verify later.
- **`.nojekyll`** should exist in the repo root, or GitHub runs Jekyll and may
  drop files starting with `_`.

## Verification

- Script prints `✅ 线上 == 本地: <url>` when the live page matches.
- A non-zero exit means commit/push failed; fix and re-run.
