---
name: daily-brief
description: Generate and push a daily AI & infrastructure briefing by composing three skills.
license: MIT
---

# Daily Brief (每日 AI & 基础设施早报)

A **composition skill**: produce a daily "AI & 基础设施早报", publish it to
GitHub Pages, and push a Feishu card linking to it. It owns the domain logic
(sources, filtering, dedup, personalized summaries) and **composes three
general skills by reference** — it does NOT vendor their code:

- **magazine-briefing** — render the briefing JSON into magazine-style HTML.
- **github-pages-publish** — publish the HTML and verify the live page.
- **feishu-card-push** — send the cover-image card with a link button.

Install those three alongside this skill. Invoke each at its step below.

## When to Use

- Generate today's 早报 (AI + infrastructure morning briefing).
- Not for: one-time repo/Pages setup (see github-pages-publish `SETUP.md`), or
  reusing a single capability standalone (call that skill directly).

## Prerequisites

- The three composed skills installed.
- `lark-cli` bot auth (`lark-cli auth status`), `git` + `gh` auth.
- A GitHub Pages repo already created & enabled (one-time, via
  github-pages-publish `SETUP.md`).
- `scripts/` here provides the domain tools: `fetch_sources.py`,
  `process_items.py`, `dedup_history.py`, `verify_links.py`. Source list in
  `SOURCES.md`.

## Procedure

1. **Fetch + process** (this skill's scripts):
   ```bash
   python3 scripts/fetch_sources.py 72          # → raw_items.json
   python3 scripts/process_items.py             # → processed.json + report.txt
   ```
   Does AI-filter → same-batch dedup → cross-day dedup (dedup_history) →
   6+4 classify (K8s×AI first) → score 🔥highlights.
2. **Write summaries → briefing.json** (agent, model-written). Follow the
   Summary Standard below. **Emit the magazine-briefing schema**
   (`brand/date_label/issue/lead/highlights/sections/flash`); URLs copied
   verbatim from processed.json, never hand-typed.
3. **Verify links**: `python3 scripts/verify_links.py briefing.json` — blocks on
   dead links or non-fetched (hand-written) URLs; allows anti-bot 403/429.
4. **Render** (→ magazine-briefing): `python3 <magazine-briefing>/scripts/render.py briefing.json YYYY-MM-DD.html`.
5. **Publish** (→ github-pages-publish): `publish.py --repo-dir <repo> --pages-url <url> --files YYYY-MM-DD.html index.html --message "Publish YYYY-MM-DD"`.
6. **Commit dedup state**: `python3 scripts/dedup_history.py commit briefing.json` (updates seen.json).
7. **Push card** (→ feishu-card-push): **do NOT hand-write the card**. Copy
   `templates/card-template.json` and fill ONLY the placeholders — `{date}`,
   `{issue}`, `{highlight}`, `{glance}`, `{count_line}`, `{page_url}`,
   `{cover}` — leaving title / icon / template colour / block order untouched.
   Then `python3 <feishu-card-push>/scripts/send_card.py spec.json`. The locked
   template guarantees a consistent card every day (title 📰 AI & 基础设施早报,
   the myai_colorful circle icon, indigo header, footer 由 daily-brief 自动生成).

## Summary Standard (摘要铁律)

Reader profile: a **cloud-native engineer/architect in fintech quant** driving
an AI-native + K8s transition; uses AI agents/skills to install K8s/components;
shares AI practice with colleagues.

- Default 2-3 sentences, information-dense; every summary carries ≥1 concrete
  fact (number/name/result/mechanism). No vague "提出了一种方法".
- **Detailed (4-6 sentences: concrete steps / what was used / what problem it
  solves)** ONLY for **skill / agent 落地实践 / agent 最佳实践** items.
- State objectively what the tech DOES / what problem it solves. **Never** write
  "对做XX的人" / "对你意味着" — it's a briefing for everyone, not a reply to the reader.
- 🔥今日重点's second block is **新闻要点** (objective key facts), not "为什么重要".
- Categories: AI board (🧠模型与研究 · 🧩Agent&Skill · 🛠️AI工程落地 · 📊产品与商业一句话
  · 💡观点与好文 · 🛡️安全与治理) then infra board in priority order
  **K8s×AI → K8s核心 → 云原生周边 → 社区与项目 → 公有云**. 3-5 items/category, only
  categories with material news. OSS/GitHub items get a 🔧 tag.

## Pitfalls

- **URLs only from processed.json** — never hand-write; verify_links enforces this.
- **Cron: reasoning-only stalls.** In unattended runs the model can spend a turn
  planning without emitting a tool call, which the loop treats as a clean stop
  → the run ends mid-task. Drive it with explicit, action-first checkpoints:
  write briefing.json to disk and confirm it exists BEFORE moving on; do each
  numbered step as a real tool call, not internal planning.
- **Card 2.0 has no note tag** — feishu-card-push handles this (grey markdown).

## Verification

- `verify_links.py` exits 0; published page returns 200 and live==local;
  `send_card.py` prints 发送成功 with a message_id.
