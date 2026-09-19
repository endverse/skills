---
name: magazine-briefing
description: Render structured JSON into a retro editorial magazine-style HTML page.
license: MIT
---

# Magazine Briefing

Turn a structured JSON document into a self-contained, retro editorial
magazine-style HTML page — paper texture, serif type, red accents, clickable
source links. Zero dependencies (Python stdlib only); the output is one
portable `.html` file that opens anywhere.

Use this for any recurring digest that should look like a print magazine rather
than a web dashboard: daily/weekly news briefings, research roundups, release
notes, curated link collections. The renderer is **content-agnostic** — brand
name, sections, and items all come from the input JSON, so it is not tied to
any single topic.

## When to Use

- You have (or can produce) a structured list of items grouped into sections
  and want a polished, shareable HTML page.
- You want a consistent "house style" across many issues.
- Not for: freeform prose documents, slide decks, or interactive apps.

## Quick Start

```bash
python3 scripts/render.py brief.json output.html
```

`brief.json` is the content; `output.html` is the rendered page. Open it in any
browser or host it (e.g. GitHub Pages) to share.

## Input Schema

See `templates/example-brief.json` for a runnable example. Fields:

| Field | Required | Meaning |
|---|---|---|
| `brand` | yes | Masthead title |
| `date_label` | yes | Date line under the title (any string) |
| `issue` | no | Issue number → renders "第 NNN 期" badge |
| `kicker` | no | Small uppercase tag in the masthead (e.g. "DAILY BRIEFING") |
| `lead` | no | One-paragraph intro, opens with a large red quote mark |
| `footer` | no | Footer line |
| `highlights[]` | no | Top items: `{title, url, summary, note}`; `note` is a red-bordered secondary block |
| `sections[]` | yes | Ordered boards: `{label?, categories[]}`. `label` shows a centered board divider (used when there are multiple boards) |
| `sections[].categories[]` | — | `{emoji, title, en?, items[]}` |
| `...items[]` | — | `{title, url, summary, tag?, source?, oss?}`; `oss:true` adds a green 🔧 开源 tag; `source` becomes a red ↗ link |
| `flash[]` | no | One-line link items: `{title, url}` |

## Design System (frozen)

The visual style is fixed and must not be edited per-issue — that consistency
is the point. Tokens: paper `#e9e2d6`, ink `#15130f`, red accent `#d7382f`,
`Noto Serif SC` serif type, `.paper` max-width 680px. To add a NEW visual
style later, add a second renderer/template rather than mutating this one.

## Pitfalls

- **Keep the style block untouched.** Per-issue edits break cross-issue consistency.
- **URLs must be real.** This renderer does not validate links; verify them upstream before rendering.
- **HTML escaping is automatic** — pass plain text in JSON, not pre-escaped entities.

## Verification

- `python3 scripts/render.py templates/example-brief.json /tmp/test.html` exits 0 and writes the file.
- Open the file: masthead, highlights, sections, and flash render with the magazine look.
