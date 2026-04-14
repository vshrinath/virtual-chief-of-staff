# Connecting to Claude Code

You can give Claude Code direct access to your VCoS memory and capabilities using the Model Context Protocol (MCP).

## 1. Get the Config
Run this command in your terminal:
```bash
vcos config mcp
```
This will output a JSON block.

## 2. Update your Configuration
- Open your Claude Code config file (usually at `~/Library/Application Support/agentic/mcp_config.json` on Mac).
- Copy the JSON block from the step above into the `mcpServers` section.

## 3. Verify
In Claude Code, you can now ask:
> "Search my VCoS memory for the last meeting about SCEH."

Claude will now use `vcos` as a tool to find the answer.
