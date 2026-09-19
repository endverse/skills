# endverse/skills

A personal marketplace of reusable **agent skills** — general-purpose,
cross-domain capabilities distilled from real work. Each skill is
self-contained (`SKILL.md` + `scripts/` + `templates/`) and follows the
standard agent-skill format, so it works across agents that support the
SKILL.md convention (Claude Code, Cursor, Codex CLI, OpenCode, Hermes, …).

## Skills

| Skill | Domain | What it does |
|---|---|---|
| [magazine-briefing](skills/content/magazine-briefing/) | content | Render structured JSON into a retro editorial magazine-style HTML page |
| [feishu-card-push](skills/messaging/feishu-card-push/) | messaging | Send a Feishu (Lark) Card 2.0 with cover, text blocks and a link button |
| [github-pages-publish](skills/devops/github-pages-publish/) | devops | Publish local files to an existing GitHub Pages repo and verify the live page |
| [daily-brief](skills/workflows/daily-brief/) | workflows | Generate & push a daily AI/infra briefing by composing the three skills above |

## Layout

```
skills/
├── content/
│   └── magazine-briefing/        # JSON → magazine-style HTML
├── messaging/
│   └── feishu-card-push/         # → Feishu Card 2.0
├── devops/
│   └── github-pages-publish/     # publish to GitHub Pages (+ SETUP.md, one-time)
└── workflows/
    └── daily-brief/              # composition skill: fetch/summarize + the 3 above
```

Skills are grouped by domain (`content/`, `messaging/`, …). The set is
intentionally broad — this is a personal toolbox, not a single-topic library.

## Install

For now, install manually: copy the skill directory into your agent's skills
folder (e.g. `~/.hermes/skills/`, `~/.claude/skills/`, or your agent's
equivalent). One-command installers (`npx skills add endverse/skills …`) will
be added once the set grows.

## Composing skills

Skills compose by **reference**, not by bundling: a higher-level workflow skill
tells the agent to invoke these skills at runtime (e.g. "render with
magazine-briefing, then push with feishu-card-push"), rather than vendoring
their code. This keeps each skill independently installable and lets shared
capabilities update in one place.

## License

MIT — see [LICENSE](LICENSE).
