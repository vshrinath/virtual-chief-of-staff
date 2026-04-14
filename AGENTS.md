# AGENTS.md — Setup Instructions for AI Assistants

You are helping a user set up the Virtual Chief of Staff system on their machine.
Execute each step in order. Confirm each step succeeded before proceeding.

---

## Step 1: Platform-Specific Core Setup

Check the user's operating system and choose the correct setup path:

### 🪟 Windows Setup
Run this automated script to install `uv` and `ffmpeg` (via winget):
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup-windows.ps1
```
*Note: The user may need to restart their terminal after this step.*

### 🍎 Mac / 🐧 Linux Setup
Run these commands:
```bash
python3 --version   # need 3.11+
# Install uv if missing
curl -LsSf https://astral.sh/uv/install.sh | sh
# Install ffmpeg if missing (Mac)
brew install ffmpeg
```

---

## Step 2: Proactive Triage

Before you begin, introduce yourself to the user and ask these two questions to determine the setup path:

1. **Lean vs. Full?**: "Do you want to process voice notes locally? (Requires ~2GB disk space for Whisper/Torch). If yes, I'll install the 'Full' version. If no, the 'Lean' version."
2. **Bridge Integration?**: "Do you want to hook this up to WhatsApp or Slack right now? I can help you configure a bridge like NanoClaw."

---

## Step 3: Install the Package

Based on the user's choice:

### Lean Version
```bash
uv tool install git+https://github.com/vshrinath/virtual-chief-of-staff
```

### Full Version (Whisper)
```bash
uv tool install "vcos[whisper] @ git+https://github.com/vshrinath/virtual-chief-of-staff"
```

Then confirm:
```bash
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

Ask the user for their API keys. Or, tell them: 
> "I can help you get these keys. Run `vcos auth` and I'll open the provider dashboards for you."

### Connect to Claude / Antigravity
To hook this system up to other agents, run:
```bash
vcos config mcp
```
This generates the JSON block for `mcp_config.json`. Help the user copy-paste this into their agent settings.

---

## Step 4: Install and Initialize MemPalace

```bash
uv tool install mempalace
mempalace init ~/.mempalace/palace
```

Then mine the vault to build the initial index, including the system manual:
```bash
mempalace mine <vault-path>/projects --wing personal
mempalace mine <vault-path>/system/docs --project system --wing system
```

---

## Step 5: Verify & Diagnose

```bash
vcos status
vcos help "getting started"
```

This will confirm the system is healthy and the manual is searchable.

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
| `VCOS_VAULT_PATH is not set` | Check `.env` is loaded — run `source <vault>/.env` (Mac) or `$env:VCOS_VAULT_PATH="..."` (Windows) |
| `mempalace: command not found` | Run `pip install mempalace` |
| `vcos: command not found` | Re-run `uv tool install ...` |
| `vault path does not exist` | Run `vcos init --vault <path>` first |
| `powershell execution error` | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
