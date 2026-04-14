# AGENTS.md — Setup Instructions for AI Assistants

You are helping a user set up the Virtual Chief of Staff system on their machine.
Execute each step in order. Confirm each step succeeded before proceeding.

---

## Prerequisites Check

Run these commands and confirm each succeeds:

```bash
python3 --version   # need 3.11+
uv --version        # need uv installed
```

If `uv` is missing, install it:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Step 1: Install the Package

```bash
uv tool install git+https://github.com/yourusername/virtual-chief-of-staff
vcos --help   # confirm install succeeded
```

---

## Step 2: Create the Vault

Ask the user: *"Where would you like your vault to live? (e.g. ~/my-vault or ~/Documents/vault)"*

Then run:
```bash
vcos init --vault <path-they-chose>
```

This creates the folder structure and a `.env` template at `<vault>/.env`.

---

## Step 3: Configure Environment

Open `<vault>/.env` and fill in:

```
VCOS_VAULT_PATH=<vault-path>
ANTHROPIC_API_KEY=<ask the user for this>
OPENAI_API_KEY=<ask the user — optional>
FATHOM_API_KEY=<ask the user — optional, only needed for meeting minutes>
MEMPALACE_PALACE_PATH=~/.mempalace/palace
```

Ask the user for their API keys. They should have at least one of Anthropic or OpenAI.

---

## Step 4: Install and Initialize MemPalace

```bash
pip install mempalace
mempalace init ~/.mempalace/palace
```

Then mine the vault to build the initial index:
```bash
mempalace mine <vault-path> --wing personal
```

---

## Step 5: Verify

```bash
vcos retrieve "test"
```

Expected: no results — but no error. If you get an error, check that `VCOS_VAULT_PATH`
is set in the `.env` and that the vault path exists.

---

## Step 6: Add an Advisor (Optional)

The system ships with one example advisor: Marshall (executive presence coach).
His persona file is in `<vault>/work-style/advisors/marshall.md`.

Tell the user:
> "You can customise Marshall or add new advisors. Each advisor is a Markdown file
> in `work-style/advisors/`. Read marshall.md to see the format."

---

## Step 7: Connect a WhatsApp Bridge (Optional)

For voice note capture, the user needs a WhatsApp bridge:
- **NanoClaw**: https://github.com/nanoclaw (routes voice → vault)
- **OpenClaw**: see MemPalace integrations at https://github.com/MemPalace/mempalace/tree/develop/integrations/openclaw

This is optional — the system works without it. Voice notes can also be manually transcribed
and run through `vcos archive`.

---

## Done

The system is ready. Tell the user:

> "Your vault is set up at <vault-path>. Try your first capture:
> `vcos archive --content 'My first note' --path 'writing/articles/1-inbox/first-note.md'`
> Then retrieve it: `vcos retrieve 'first note'`"

---

## Troubleshooting

| Error | Fix |
|---|---|
| `VCOS_VAULT_PATH is not set` | Check `.env` is loaded — run `source <vault>/.env` |
| `mempalace: command not found` | Run `pip install mempalace` |
| `vcos: command not found` | Re-run `uv tool install ...` |
| `vault path does not exist` | Run `vcos init --vault <path>` first |
