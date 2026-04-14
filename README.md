# Virtual Chief of Staff

## What This Is

A personal intelligence system built on Markdown — context capture, memory retrieval,
meeting minutes, proposals, and morning briefings. Everything stays on your machine
in plain text files you own.

Built on:
- **MemPalace** — semantic memory index (ChromaDB, local)
- **MarkItDown** — converts PDFs, Word docs, slides to Markdown
- **Any WhatsApp bridge** — NanoClaw, OpenClaw, or compatible (for voice/message capture)

Read the design story: [Article 1] · [Article 2] · [Article 3]

## Documentation

- [AGENTS.md](./AGENTS.md) — How to set this up using an AI assistant.
- [INTEGRATIONS.md](./docs/INTEGRATIONS.md) — Hooking up WhatsApp (NanoClaw) and AI Agents (MCP).
- [CLAUDE.md](./CLAUDE.md) — Quick reference for Claude Code users.

---

## What You Need

- Python 3.11+
- `uv` ([install](https://docs.astral.sh/uv/getting-started/installation/))
- An API key — Anthropic or OpenAI (or both)
- A WhatsApp bridge — [NanoClaw](https://github.com/nanoclaw) or [OpenClaw](https://github.com/MemPalace/mempalace/tree/develop/integrations/openclaw) (optional, for voice capture)
- Fathom API key (optional, for meeting minutes via Fathom)

---

## Install

```bash
uv tool install git+https://github.com/vshrinath/virtual-chief-of-staff
```

---

## Setup

**1. Create your vault**
```bash
vcos init --vault ~/my-vault
```

This scaffolds the directory structure and creates a `.env` file at `~/my-vault/.env`.

**2. Configure your `.env`**
```
VCOS_VAULT_PATH=~/my-vault
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here        # optional
FATHOM_API_KEY=your_key_here        # optional, for meeting minutes
MEMPALACE_PALACE_PATH=~/.mempalace/palace
```

**3. Initialize MemPalace**
```bash
mempalace init ~/.mempalace/palace
mempalace mine ~/my-vault --wing personal
```

**4. Verify**
```bash
vcos retrieve "test query"
# Should return: no results (empty vault — no error)
```

---

## The CLI

Every capability is a skill:

```bash
vcos archive --content "..." --path "projects/my-project/notes.md"
vcos retrieve "what did I decide about pricing?"
vcos compose --query "proposal for fintech client" --type proposal
vcos mom list
vcos mom 1 my-project
vcos standup
```

---

## Advisors

The system ships with one example advisor: **Marshall** (executive presence, Authority Audit).

Add your own in `~/my-vault/work-style/advisors/`. Marshall's persona file shows the format.
Any `.md` file you add there can be invoked by name via `vcos compose`.

---

## Adding Skills

A skill is a Python module registered in `src/vcos/cli.py`. Any coding tool (Claude, Cursor,
Gemini CLI) can read the codebase structure and help you add one.

---

## WhatsApp Bridge

The intelligence layer (retrieval, archiving, skills) runs independently of how capture works.
Compatible bridges:
- **NanoClaw** — routes voice notes and messages via WhatsApp → vault
- **OpenClaw** — OpenClaw integration (MemPalace has native support via `integrations/openclaw`)
- Any bridge that can drop a text file or POST to a local endpoint

---

## Not a Technical User?

Open this repo in Claude Code, Cursor, or Gemini CLI and say:

> "Read AGENTS.md and set up this system for me."

The AI will execute every step.
