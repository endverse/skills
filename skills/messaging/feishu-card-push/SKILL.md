---
name: feishu-card-push
description: Send a Feishu (Lark) interactive Card 2.0 with cover, text and a link button.
license: MIT
---

# Feishu Card Push

Build and send a Feishu (Lark) **Card 2.0** interactive message from a simple
JSON spec: an optional cover image, ordered text blocks, and a primary button
that opens a URL. Handles image upload, `image_key` injection, a dry-run
validation pass, and the real send in one command.

Use this for any Feishu notification that should look richer than plain text:
daily/weekly briefings, release notes, alerts with a "view details" button.
The content is fully generic — nothing here is tied to a specific topic.

## Prerequisites

- `lark-cli` installed and authenticated with a ready **bot** identity
  (`lark-cli auth status` → `identities.bot.available: true`).
- The bot must already share a chat with the target user/group (a bot cannot
  cold-DM a user it has no conversation with).

## Quick Start

```bash
python3 scripts/send_card.py spec.json            # dry-run, then send
python3 scripts/send_card.py spec.json --dry-run  # validate only, no send
```

See `scripts/example-spec.json` for a runnable example.

## Input Schema

| Field | Required | Meaning |
|---|---|---|
| `chat_id` / `user_id` | one of | Target group (`oc_…`) or user (`ou_…`) |
| `header.title` | yes | Card title |
| `header.subtitle` | no | One-line context under the title |
| `header.template` | no | Header color (default `indigo`) |
| `header.icon` | no | A `standard_icon` token (e.g. `myai_colorful`) |
| `cover_image` | no | Absolute path to a local cover image; uploaded automatically |
| `blocks[]` | yes | Ordered body blocks: `{type:"markdown", content}`, `{type:"hr"}`, or `{type:"grey", content}` (grey text) |
| `button` | no | `{text, url}` → a full-width primary button that opens the URL |
| `footer` | no | Grey footer line |

## Pitfalls

- **Card 2.0 has no `note` tag** — the server rejects it. Use `{type:"grey"}`
  blocks for muted text (this script already does that).
- **Card content is passed through verbatim** by lark-cli; this script writes
  the card JSON to a temp file and feeds it via `--content`, avoiding shell
  quoting/heredoc corruption. Do not hand-assemble the send command inline.
- **`image_key` can expire** — the script re-uploads the cover on every run, so
  never hardcode an old `image_key`.
- **Always dry-run first** — the script does this automatically and aborts if
  the card is invalid, before the real send.

## Verification

- Dry-run prints `dry-run ✅`; a real send prints `发送成功 ✅ message_id=…`.
- The card renders in Feishu with the cover, text blocks, and a working button.
