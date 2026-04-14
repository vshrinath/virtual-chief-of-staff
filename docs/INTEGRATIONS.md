# Integrations Guide

This guide explains how to connect the Virtual Chief of Staff (VCoS) to input bridges (WhatsApp/Voice) and AI Agents (Claude Code, Antigravity, etc.).

---

## 1. Input Bridges (WhatsApp / Voice)

VCoS is "Bridge Agnostic." It expects transcripts to be piped into the vault via the CLI.

### NanoClaw / Custom Bridges
If you use [NanoClaw](https://github.com/vshrinath/nanoclaw) or a custom Go/Python bridge, you can hook up VCoS by calling the `archive` command after a message is transcribed.

**Command:**
```bash
vcos archive --content "$TRANSCRIPT" --path "writing/articles/1-inbox/$(date +%Y-%m-%d).md"
```

### Local Whisper Workflow (Highly Private)
If you install the `[whisper]` version of VCoS, you can handle transcription on your own machine without sending audio to an cloud provider.

**Workflow:**
1. **NanoClaw** captures the audio file (e.g., `recording.m4a`).
2. **NanoClaw** (or a local script) calls `vcos transcribe`:
   ```bash
   vcos transcribe recording.m4a --archive
   ```
3. **VCoS** transcribes the file and automatically saves it to your `writing/articles/1-inbox/` with the correct frontmatter.

*Note: This requires FFmpeg installed on your system.*

### OpenClaw
[OpenClaw](https://github.com/MemPalace/mempalace) is a bridge developed by the MemPalace team. Since VCoS uses MemPalace for memory, you can point OpenClaw directly at your palace index:

1. Set `MEMPALACE_PALACE_PATH` in your OpenClaw environment to match your VCoS settings.
2. OpenClaw will now have direct semantic access to your vault history.

---

## 2. AI Agents & MCP (Model Context Protocol)

You can give your AI assistants (Claude Code, Cursor, Antigravity, etc.) direct access to your Chief of Staff powers using **MCP**.

### The MemPalace MCP Server
Since VCoS stores everything in a MemPalace-compatible format, the easiest way to bridge to agents is using the `mempalace-mcp` server.

1. **Install the server:**
   ```bash
   uv tool install mempalace
   ```

2. **Configure your Agent:**
   Add this to your `mcp_config.json` (usually found in `~/Library/Application Support/Claude/` or similar):

```json
{
  "mcpServers": {
    "vcos-memory": {
      "command": "uvx",
      "args": ["mempalace-mcp"],
      "env": {
        "MEMPALACE_PALACE_PATH": "/path/to/your/vcos/palace"
      }
    }
  }
}
```

### Agent-Led Composition
When you are working in **Claude Code** or **Antigravity**, you can ask the agent to help you write using your VCoS style:

> *"Search my memory for SCEH project notes and then use the `vcos compose` command to draft a proposal in Marshall's style."*

Because you have `AGENTS.md` in your repo root, any agent you bring into this folder will automatically understand how to use these commands to assist you.

---

## 3. Desktop Workflows (Obsidian / Logseq)

Because your vault is just a folder of Markdown files, you can point **Obsidian** or **Logseq** at your `VCOS_VAULT_PATH`. 

- **Archiving**: Messages archived via WhatsApp appear instantly in your Obsidian inbox.
- **Bi-directional**: If you edit a file in Obsidian, running `vcos standup` will pick up those changes for your morning briefing.
